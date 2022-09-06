#!/usr/bin/env python3

import logging

import sys
from os.path import dirname, splitext
from os import listdir
sys.path.append(dirname(__file__))

from subprocess import Popen, PIPE
import re
from argparse import ArgumentParser
from pathlib import Path
from typing import List, Union, Tuple
from clang.cindex import Index
from clang.cindex import TranslationUnit
from clang.cindex import CursorKind
from jinja2 import Environment, FileSystemLoader


class Variable:
    def __init__(self, type: str, name: str) -> None:
        self.type = type
        self.name = name

    def get_definition(self) -> str:
        return f"{self.type} {self.name}"


class Function:
    def __init__(self, type: str, name: str, params: List[Variable]) -> None:
        self.type = type
        self.name = name
        self.params = params

    def get_signature(self) -> str:
        arguments = ", ".join(f"{param.type} {param.name}" for param in self.params)
        return f"{self.type} {self.name}({arguments})"

    def has_return_value(self) -> bool:
        return self.type != "void"

    def get_call(self) -> str:
        arguments = ", ".join(f"{param.name}" for param in self.params)
        return f"{self.name}({arguments})"

    def get_param_types(self) -> str:
        param_types = ", ".join(f"{param.type}" for param in self.params)
        return f"{param_types}"


class MockupWriter:
    
    def __init__(self, mockup_style="gmock") -> None:
        self.headers = []
        self.variables = []
        self.functions = []
        self.template_dir = f"{dirname(__file__)}/templates"
        self.mockup_style = mockup_style
        self.environment = Environment(
            loader=FileSystemLoader(f"{self.template_dir}/{self.mockup_style}"),
            keep_trailing_newline=True,
            trim_blocks=True,
        )

    def set_mockup_style(self, mockup_style: str) -> None:
        self.mockup_style = mockup_style

    def add_header(self, name: str) -> None:
        """Add a header to be included in mockup"""
        if name not in self.headers:
            self.headers.append(name)

    def add_variable(self, type: str, name: str) -> None:
        """Add a variable definition"""
        self.variables.append(Variable(type, name))

    def add_function(self, type: str, name: str, params: List[Tuple[str, str]] = []) -> None:
        """Add a variable definition"""
        self.functions.append(Function(type, name, [Variable(param[0], param[1]) for param in params]))
    
    def get_mockup(self, file: Path) -> str:
        return self.render(file + '.j2')
        
    def render(self, file: Path) -> str:
        return self.environment.get_template(f"{file}").render(
                    headers=sorted(self.headers),
                    variables=sorted(self.variables, key=lambda x: x.name),
                    functions=sorted(self.functions, key=lambda x: x.name)
                )
        
    def write(self, outdir: Path) -> None:
        for file in listdir(f"{self.template_dir}/{self.mockup_style}"):
            if file.endswith(".j2"):
                Path(outdir, f"{splitext(file)[0]}").write_text(self.render(file))


class Hammock:
    def __init__(self, symbols: List[str], cmd_args: List[str] = [], mockup_style="gmock"):
        self.symbols = symbols
        self.cmd_args = cmd_args
        self.writer = MockupWriter(mockup_style)

    def read(self, sources: List[Path]) -> None:
        for source in sources:
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
    regex = r"\s*U\s+([^_]\S*)"
    
    def __init__(self, plink: Path):
        self.plink = plink
        self.undefined_symbols = []
        self.__process()

    def get_undefined_symbols(self) -> List[str]:
        return self.undefined_symbols

    def __process(self):
        with Popen(
            ["llvm-nm", "--undefined-only", self.plink],
            stdout=PIPE,
            stderr=PIPE,
            bufsize=1,
            universal_newlines=True,
        ) as p:
            for line in p.stdout:
                match = re.match(self.regex, line)
                if match:
                    self.undefined_symbols.append(match.group(1))
            assert p.returncode == None


def main(pargv):
    
    arg = ArgumentParser(fromfile_prefix_chars="@", prog='hammocking')

    group_symbols_xor_plink = arg.add_mutually_exclusive_group(required=True)
    group_symbols_xor_plink.add_argument("--symbols", "-s", help="Symbols to mock", nargs="+")
    group_symbols_xor_plink.add_argument("--plink", "-p", help="Path to partially linked object", type=Path)

    arg.add_argument("--outdir", "-o", help="Output directory", required=True, type=Path)
    arg.add_argument("--sources", help="List of source files to be parsed", type=Path, required=True, nargs="+")
    
    arg.add_argument("--style", "-t", help="Mockup style to output", required=False, default="gmock")

    args, cmd_args = arg.parse_known_args(args=pargv)

    if not args.symbols:
        args.symbols = NmWrapper(args.plink).get_undefined_symbols()

    print(f"DEBUG: {args.style}")
    h = Hammock(symbols=args.symbols, cmd_args=cmd_args, mockup_style=args.style)
    h.read(args.sources)
    h.write(args.outdir)

    if not h.done:
        sys.stderr.write("HammocKing failed. The following symbols could not be mocked:\n" + "\n".join(h.symbols) + "\n")
        exit(1)
    exit(0)


if __name__ == "__main__":
    main(sys.argv)
