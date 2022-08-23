#!/usr/bin/env python3

import logging

import sys
from os.path import dirname

sys.path.append(dirname(__file__))

from subprocess import Popen, PIPE
import re
from argparse import ArgumentParser
from pathlib import Path
from typing import List, Union
from clang.cindex import Index
from clang.cindex import TranslationUnit
from clang.cindex import CursorKind
from mockup_writer import MockupWriter


class Hammock:
    def __init__(self, symbols: List[str], cmd_args: List[str] = []):
        self.symbols = symbols
        self.cmd_args = cmd_args
        self.writer = MockupWriter()

    def read(self, sources: List[Path]) -> None:
        for source in args.sources:
            if self.done:
                break
            self.parse(source)

    def parse(self, input: Union[Path, str]) -> None:
        parseOpts = {
            "args": self.cmd_args,
            "options": TranslationUnit.PARSE_SKIP_FUNCTION_BODIES | TranslationUnit.PARSE_INCOMPLETE,
        }

        if issubclass(type(input), Path):
            # Read a path
            parseOpts["path"] = input
        else:
            # Interpret a string as content of the file
            parseOpts["path"] = "~.c"
            parseOpts["unsaved_files"] = [("~.c", input)]

        for child in Index.create(excludeDecls=True).parse(**parseOpts).cursor.get_children():
            if child.spelling in self.symbols:
                self.writer.add_header(str(child.location.file))
                if child.kind == CursorKind.VAR_DECL:
                    self.writer.add_variable(child.type.spelling, child.spelling)
                elif child.kind == CursorKind.FUNCTION_DECL:
                    self.writer.add_function(
                        child.type.get_result().spelling,
                        child.spelling,
                        [(arg.type.spelling, arg.spelling) for arg in child.get_arguments()],
                    )
                else:
                    logging.warning(f"Unknown kind of symbol: {child.kind}")
                self.symbols.remove(child.spelling)

    def write(self, outdir: Path) -> None:
        self.writer.write(outdir)

    @property
    def done(self) -> bool:
        return len(self.symbols) == 0


class NmWrapper:
    def __init__(self, plink: Path):
        self.plink = plink
        self.undefined_symbols = []
        self.__process()

    def get_undefined_symbols(self) -> List[str]:
        return self.undefined_symbols

    def __process(self):
        with Popen(
            ["llvm-nm", "--undefined-only", "--format=just-symbols", self.plink],
            stdout=PIPE,
            stderr=PIPE,
            bufsize=1,
            universal_newlines=True,
        ) as p:
            for line in p.stdout:
                match = re.match(r"([^_]\S*)", line)
                if match:
                    self.undefined_symbols.append(match.group(1))
            assert p.returncode == None


if __name__ == "__main__":
    arg = ArgumentParser(fromfile_prefix_chars="@")

    group_symbols_xor_plink = arg.add_mutually_exclusive_group(required=True)
    group_symbols_xor_plink.add_argument("--symbols", "-s", help="Symbols to mock", nargs="+")
    group_symbols_xor_plink.add_argument("--plink", "-p", help="Path to partially linked object", type=Path)

    arg.add_argument("--outdir", "-o", help="Output directory", required=True, type=Path)
    arg.add_argument("--sources", help="List of source files to be parsed", type=Path, required=True, nargs="+")

    args, cmd_args = arg.parse_known_args()

    if not args.symbols:
        args.symbols = NmWrapper(args.plink).get_undefined_symbols()

    h = Hammock(symbols=args.symbols, cmd_args=cmd_args)
    h.read(args.sources)
    h.write(args.outdir)

    if not h.done:
        sys.stderr.write("Hammock failed. The following symbols could not be mocked:\n" + "\n".join(h.symbols) + "\n")
        exit(1)
    exit(0)
