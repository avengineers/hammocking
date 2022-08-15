#!/usr/bin/env python3

import io
import logging
import sys
from argparse import ArgumentParser
from pathlib import Path
from typing import List, Tuple, Union

from clang.cindex import Index
from clang.cindex import TranslationUnit
from clang.cindex import CursorKind


class MOCK_SECTION:
    section_guard = {
        "code": "MOCKUP_CODE",
        "global_var": "MOCKUP_ADDITIONAL_GLOBAL_VARIABLES",
    }

    def __init__(self, symbol: str, with_config_guard: bool = True):
        self.symbol = symbol
        self.global_vars = []
        self.vars = []
        self.functions = []
        self.config_guard = with_config_guard

    def add_global_var(self, type: str, name: str) -> None:
        """Add a global variable declaration + definition"""
        self.global_vars.append((type, name))

    def add_var(self, type: str, name: str) -> None:
        """Add a variable definition"""
        self.vars.append((type, name))  # TODO: Nice wrapper class

    def add_function(self, type: str, name: str, params: List[Tuple[str, str]]) -> None:
        self.functions.append((type, name, params))  # TODO: Nice wrapper class

    def _wrap_config(self, section: str):
        """
        Wrap a section in a config guard, if config is enabled
        """
        if self.config_guard and section != "":
            return "#ifdef HAM_" + self.symbol + "\n" + section + "#endif // HAM_" + self.symbol + "\n"
        else:
            return section

    def _get_includes(self) -> str:
        return ""

    def _get_global_vars(self) -> str:
        if self.global_vars:
            return (
                "#ifdef "
                + self.section_guard["global_var"]
                + "\n"
                + "".join(map(lambda v: self._var_impl(v, True), self.global_vars))
                + "#endif\n"
            )
        else:
            return ""

    def _var_impl(self, v: Tuple[str, str], is_extern: bool = False) -> str:
        """Implementation of a variable"""
        type, name = v
        section = "extern " if is_extern else ""
        return f"{section}{type} {name};\n"

    def _func_impl(self, f: Tuple[str, str, List[Tuple[str, str]]]) -> str:
        """Implementation of a function"""
        return_type, name, params = f
        func_decl = (
            f"{return_type} {name}("
            + ("void" if len(params) == 0 else ", ".join(f"{t} {n}" for t, n in params))
            + ")\n"
        )
        func_body = f"   return {name}__return;\n" if return_type != "void" else ""
        return func_decl + "{\n" + func_body + "}\n"

    def _get_code(self) -> str:
        if self.vars or self.functions:
            return (
                "#ifdef "
                + self.section_guard["code"]
                + "\n"
                + "".join(map(self._var_impl, self.vars))
                + "".join(map(self._func_impl, self.functions))
                + "#endif\n"
            )
        else:
            return ""

    def __str__(self):
        return self._wrap_config(self._get_includes() + self._get_global_vars() + self._get_code())


class AUTOMOCKER:
    def __init__(self, symbols: List[str], cmd_args: List[str] = []):
        self.symbols = symbols
        self.cmd_args = cmd_args
        self.config = None
        self.mockups = []

    def set_config(self, configfile) -> None:
        self.config = open(configfile, "w")

    def write_config_enabler(self) -> None:
        if self.config is not None:
            self.config.write("\n".join("#define HAM_%s" % symbol for symbol in self.symbols))

    def read(self, input: Union[Path, str]) -> None:
        if issubclass(type(input), Path):  # Read a path
            cursor = (
                Index.create(excludeDecls=True)
                .parse(
                    path=input,
                    args=self.cmd_args,
                    options=TranslationUnit.PARSE_SKIP_FUNCTION_BODIES | TranslationUnit.PARSE_INCOMPLETE,
                )
                .cursor
            )
        else:  # Interpret a string as content of the file
            cursor = (
                Index.create(excludeDecls=True)
                .parse(
                    path="~.c",
                    unsaved_files=[("~.c", input)],
                    args=self.cmd_args,
                    options=TranslationUnit.PARSE_SKIP_FUNCTION_BODIES | TranslationUnit.PARSE_INCOMPLETE,
                )
                .cursor
            )
        for child in cursor.get_children():
            if child.spelling in self.symbols:
                name = child.spelling
                mockup = MOCK_SECTION(name, self.config is not None)
                if child.kind == CursorKind.VAR_DECL:
                    mockup.add_var(child.type.spelling, name)
                elif child.kind == CursorKind.FUNCTION_DECL:
                    resulttype = child.type.get_result().spelling
                    if resulttype != "void":
                        mockup.add_global_var(resulttype, name + "__return")
                    mockup.add_function(
                        resulttype, name, [(arg.type.spelling, arg.spelling) for arg in child.get_arguments()]
                    )
                else:
                    logging.warning(f"Unknown kind of symbol: {child.kind}")
                self.mockups.append(mockup)
                self.symbols.remove(child.spelling)

    def write(self, output: io.IOBase) -> None:
        output.write("\n".join(str(sect) for sect in self.mockups))

    @property
    def done(self) -> bool:
        return len(self.symbols) == 0


if __name__ == "__main__":
    arg = ArgumentParser(fromfile_prefix_chars="@")
    arg.add_argument("--symbols", "-s", help="Symbols to mock", required=True, nargs="+")
    arg.add_argument("--output", "-o", help="Output")
    arg.add_argument("--config", "-c", help="Mockup config header")
    arg.add_argument("--sources", help="List of source files to be parsed", type=Path, required=True, nargs="+")
    args, cmd_args = arg.parse_known_args()

    mocker = AUTOMOCKER(symbols=args.symbols, 
                        cmd_args=cmd_args
                        )
    if args.config is not None:
        mocker.set_config(args.config)
        mocker.write_config_enabler()
    for input in args.sources:
        if mocker.done:
            break
        mocker.read(input)

    mocker.write(open(args.output, "w") if args.output is not None else sys.stdout)
    if not mocker.done:
        sys.stderr.write("Automocker failed. The following symbols could not be mocked:\n" + "\n".join(mocker.symbols) + "\n")
        exit(1)
    exit(0)
