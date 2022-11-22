#!/usr/bin/env python3

import sys
from os import listdir, environ
from os.path import dirname

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
import logging


class Variable:
    def __init__(self, type: str, name: str, size: int = 0) -> None:
        self.type = type
        self.name = name
        self.size = size

    def get_definition(self) -> str:
        return f"{self.type} {self.name}" + (f"[{self.size}]" if self.size > 0 else "")


class Function:
    def __init__(self, type: str, name: str, params: List[Variable]) -> None:
        self.type = type
        self.name = name
        self.params = params

    def get_signature(self) -> str:
        return f"{self.type} {self.name}({self._collect_arguments(True)})"

    def _collect_arguments(self, with_types: bool) -> str:
        unnamed_index = 1
        arguments = []
        for param in self.params:
            arg_name = param.name if param.name else 'unnamed' + str(unnamed_index)
            unnamed_index = unnamed_index + 1
            arg_type = param.type + ' ' if with_types else ''
            arguments.append(f"{arg_type}{arg_name}")
        return ", ".join(arguments)

    def has_return_value(self) -> bool:
        return self.type != "void"

    def get_call(self) -> str:
        return f"{self.name}({self._collect_arguments(False)})"

    def get_param_types(self) -> str:
        param_types = ", ".join(f"{param.type}" for param in self.params)
        return f"{param_types}"


class MockupWriter:

    def __init__(self, mockup_style="gmock", suffix=None) -> None:
        self.headers = []
        self.variables = []
        self.functions = []
        self.template_dir = f"{dirname(__file__)}/templates"
        self.mockup_style = mockup_style
        self.suffix = suffix or ""
        self.environment = Environment(
            loader=FileSystemLoader(f"{self.template_dir}/{self.mockup_style}"),
            keep_trailing_newline=True,
            trim_blocks=True
        )

    def set_mockup_style(self, mockup_style: str) -> None:
        self.mockup_style = mockup_style

    def add_header(self, name: str) -> None:
        """Add a header to be included in mockup"""
        if name not in self.headers:
            self.headers.append(name)

    def add_variable(self, type: str, name: str, size: int = 0) -> None:
        """Add a variable definition"""
        print(f"INFO: HammocKing: Create mockup for variable {name}")
        self.variables.append(Variable(type, name, size))

    def add_function(self, type: str, name: str, params: List[Tuple[str, str]] = []) -> None:
        """Add a variable definition"""
        print(f"INFO: HammocKing: Create mockup for function {name}")
        self.functions.append(Function(type, name, [Variable(param[0], param[1]) for param in params]))

    def get_mockup(self, file: str) -> str:
        return self.render(Path(file + '.j2'))

    def render(self, file: Path) -> str:
        return self.environment.get_template(f"{file}").render(
            headers=sorted(self.headers),
            variables=sorted(self.variables, key=lambda x: x.name),
            functions=sorted(self.functions, key=lambda x: x.name),
            suffix=self.suffix
        )

    def write(self, outdir: Path) -> None:
        for file in listdir(f"{self.template_dir}/{self.mockup_style}"):
            if file.endswith(".j2"):
                Path(outdir, self.create_out_filename(file)).write_text(self.render(Path(file)))

    def create_out_filename(self, template_filename: str):
        template = Path(Path(template_filename).stem)
        return template.stem + (self.suffix if self.suffix else "") + template.suffix

    def default_language_mode(self) -> str:
        return 'c++' if self.mockup_style in ["gmock"] else 'c'


class Hammock:
    def __init__(self, symbols: List[str], cmd_args: List[str] = [], mockup_style="gmock", suffix=None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.symbols = symbols
        self.cmd_args = cmd_args
        self.writer = MockupWriter(mockup_style, suffix)

    def read(self, sources: List[Path]) -> None:
        for source in sources:
            if self.done:
                break
            self.logger.debug(f"Parsing {source}")
            self.parse(source)

    def parse(self, input: Union[Path, str]) -> None:
        parseOpts = {
            "args": self.cmd_args,
            "options": TranslationUnit.PARSE_SKIP_FUNCTION_BODIES | TranslationUnit.PARSE_INCOMPLETE,
        }
        # Determine language mode, if not explicitly given
        if not any(arg.startswith('-x') for arg in parseOpts["args"]):
            parseOpts["args"].append('-x' + self.writer.default_language_mode())

        if issubclass(type(input), Path):
            # Read a path
            parseOpts["path"] = input
        else:
            # Interpret a string as content of the file
            parseOpts["path"] = "~.c"
            parseOpts["unsaved_files"] = [("~.c", input)]

        self.logger.debug(f"Symbols to be mocked: {self.symbols}")
        translation_unit = Index.create(excludeDecls=True).parse(**parseOpts)
        self.logger.debug(f"Parse diagnostics: {list(translation_unit.diagnostics)}")
        self.logger.debug(f"Command arguments: {parseOpts['args']}")
        for child in translation_unit.cursor.get_children():
            if child.spelling in self.symbols:
                in_header = child.location.file.name != translation_unit.spelling
                if in_header:  # We found it in the Source itself. Better not include the whole source!
                    self.writer.add_header(str(child.location.file))
                if child.kind == CursorKind.VAR_DECL:
                    child_type_array_size = child.type.get_array_size()
                    if child_type_array_size > 0:
                        self.writer.add_variable(child.type.element_type.spelling, child.spelling, child_type_array_size)
                    else:
                        self.writer.add_variable(child.type.spelling, child.spelling)
                elif child.kind == CursorKind.FUNCTION_DECL:
                    self.writer.add_function(
                        child.type.get_result().spelling,
                        child.spelling,
                        [(arg.type.spelling, arg.spelling) for arg in child.get_arguments()],
                    )
                else:
                    self.logger.warning(f"Unknown kind of symbol: {child.kind}")
                self.symbols.remove(child.spelling)

    def write(self, outdir: Path) -> None:
        self.writer.write(outdir)

    @property
    def done(self) -> bool:
        return len(self.symbols) == 0


class NmWrapper:
    regex = r"\s*U\s+((?!_|llvm_)\S*)"

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
            assert p.returncode is None


def main(pargv):
    arg = ArgumentParser(fromfile_prefix_chars="@", prog='hammocking')

    group_symbols_xor_plink = arg.add_mutually_exclusive_group(required=True)
    group_symbols_xor_plink.add_argument("--symbols", "-s", help="Symbols to mock", nargs="+")
    group_symbols_xor_plink.add_argument("--plink", "-p", help="Path to partially linked object", type=Path)

    arg.add_argument("--debug", "-d", help="Debugging", required=False, default=False, action="store_true")
    arg.add_argument("--outdir", "-o", help="Output directory", required=True, type=Path)
    arg.add_argument("--sources", help="List of source files to be parsed", type=Path, required=True, nargs="+")

    arg.add_argument("--style", "-t", help="Mockup style to output", required=False, default="gmock")
    arg.add_argument("--suffix", help="Suffix to be added to the generated files", required=False)
    args, cmd_args = arg.parse_known_args(args=pargv)

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    if not args.symbols:
        args.symbols = NmWrapper(args.plink).get_undefined_symbols()

    h = Hammock(symbols=args.symbols, cmd_args=cmd_args, mockup_style=args.style, suffix=args.suffix)
    h.read(args.sources)
    h.write(args.outdir)

    if not h.done:
        sys.stderr.write(
            "HammocKing failed. The following symbols could not be mocked:\n" + "\n".join(h.symbols) + "\n")
        exit(1)
    exit(0)


if __name__ == "__main__":
    main(sys.argv)
