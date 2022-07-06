#!/usr/bin/python3

import io
import sys
from argparse import ArgumentParser
from typing import List, Tuple
from clang.cindex import Index
from clang.cindex import TranslationUnit
from clang.cindex import Cursor
from clang.cindex import CursorKind
from clang.cindex import Config


class MOCK_SECTION:
    section_guard = {
        "code": "MOCKUP_CODE",
        "global_var": "MOCKUP_ADDITIONAL_GLOBAL_VARIABLES"
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

    # TODO: proper parameter list
    def add_function(self, type: str, name: str, params: List[str]) -> None:
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
            return "#ifdef " + self.section_guard["global_var"] + "\n" \
                   + "".join(map(lambda v: self._var_impl(v, True), self.global_vars)) \
                   + "#endif\n"
        else:
            return ""

    def _var_impl(self, v: Tuple[str, str], is_extern: bool = False) -> str:
        """Implementation of a variable"""
        type, name = v
        section = "extern " if is_extern else ""
        return f"{section}{type} {name};\n"

    def _func_impl(self, f: Tuple[str, str, List[str]]) -> str:
        """Implementation of a function"""
        return_type, name, params = f
        func_decl = f"{return_type} {name}(" + (
            "void" if len(params) == 0 else ", ".join(params)) + ")\n"
        func_body = f"   return {name}__return;\n" if return_type != "void" else ""
        return func_decl + "{\n" + func_body + "}\n"

    def _get_code(self) -> str:
        if self.vars or self.functions:
            return "#ifdef " + self.section_guard["code"] + "\n" \
                   + "".join(map(self._var_impl, self.vars)) \
                   + "".join(map(self._func_impl, self.functions)) \
                   + "#endif\n"
        else:
            return ""

    def __str__(self):
        return self._wrap_config(
            self._get_includes() +
            self._get_global_vars() +
            self._get_code()
        )


class AUTOMOCKER:
    def __init__(self, symbols: List[str], output: io.IOBase):
        self.symbols = symbols
        self.out = output
        self.config = None

    def set_config(self, configfile) -> None:
        self.config = open(configfile, 'w')

    def read(self, input: io.IOBase) -> None:
        # Fake
        sec1 = MOCK_SECTION('some_var', self.config is not None)
        sec1.add_var('int', 'some_var')
        sec2 = MOCK_SECTION('c', self.config is not None)
        sec2.add_function('int', 'c', [])
        sec2.add_global_var('int', 'c__return')

        self.out.write("\n".join(str(sect) for sect in [sec1, sec2]))
        if self.config is not None:
            self.config.write('\n'.join("#define HAM_%s" %
                              symbol for symbol in self.symbols))
        self.symbols = []

    @property
    def done(self) -> bool:
        return len(self.symbols) == 0


if __name__ == "__main__":
    arg = ArgumentParser(fromfile_prefix_chars='@')
    arg.add_argument('--symbols', '-s', help="Symbols to mock",
                     required=True, nargs='+')
    arg.add_argument('--output', '-o', help="Output")
    arg.add_argument('--config', '-c', help="Mockup config header")
    arg.add_argument('files', nargs='+')
    args = arg.parse_args()

    mocker = AUTOMOCKER(args.symbols, open(args.output, 'w')
                        if args.output is not None else sys.stdout)
    if args.config is not None:
        mocker.set_config(args.config)
    for input in args.files:
        if mocker.done:
            break
        mocker.read(open(input))

    if not mocker.done:
        sys.stderr.write(
            "Automocker failed. The following symbols could not be mocked:\n" + "\n".join(mocker.symbols))
        exit(1)
    exit(0)
