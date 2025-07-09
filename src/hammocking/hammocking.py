#!/usr/bin/env python3

import sys
from dataclasses import dataclass, field
from os import listdir
from os.path import dirname

from mashumaro import DataClassDictMixin

sys.path.append(dirname(__file__))

import configparser
import logging
import re
from argparse import ArgumentParser, Namespace
from pathlib import Path
from subprocess import CalledProcessError
from typing import Any, Dict, Iterable, Iterator, List, Optional, Set, Tuple, Union

from clang.cindex import Config, Cursor, CursorKind, Index, TranslationUnit, TypeKind
from jinja2 import Environment, FileSystemLoader, select_autoescape
from py_app_dev.core.subprocess import SubprocessExecutor


@dataclass
class HammockIni(DataClassDictMixin):
    """Configuration for Hammock Ini File"""

    clang_lib_file: Optional[str] = None
    clang_lib_path: Optional[str] = None
    exclude_paths: Optional[List[str]] = None
    exclude_pattern: Optional[str] = None
    include_pattern: Optional[str] = None
    nm_path: Optional[str] = None


@dataclass
class HammockConfig(DataClassDictMixin):
    """Configuration for Hammocking"""

    outdir: Path
    sources: List[Path]
    symbols: Optional[Set[str]] = None
    plink: Optional[Path] = None
    style: Optional[str] = "gmock"
    suffix: Optional[str] = ""
    exclude_paths: Optional[List[str]] = None
    exclude: Optional[List[str]] = field(default_factory=lambda: [])
    config: Optional[Path] = None
    exclude_pattern: Optional[str] = None
    clang_lib_file: Optional[str] = None
    clang_lib_path: Optional[str] = None
    include_pattern: Optional[str] = None
    nm_path: Optional[str] = None
    ignore_symbols_outside_project: bool = False
    project_root_dir: Optional[Path] = None
    cmd_args: Optional[List[str]] = None

    @classmethod
    def from_namespace(cls, namespace: Namespace) -> "HammockConfig":
        """
        Create an instance of this class from a namespace.

        Args:
            namespace (Namespace): Namespace for the Config.

        Returns:
            HammockConfig: The instance of this class.

        """
        return cls.from_dict(vars(namespace))

    def merge(self, hammock_ini: HammockIni) -> "HammockConfig":
        """
        Merge the HammockIni configuration into the current HammockConfig instance.

        Args:
            hammock_ini (HammockIni): The HammockIni instance to merge.

        Returns:
            None
        """
        result: Dict[Any, Any] = {}
        result = self.to_dict()
        hammock_ini_dict = hammock_ini.to_dict()
        for key, value in result.items():
            if value is None and key in hammock_ini_dict:
                result[key] = hammock_ini_dict[key]
        return HammockConfig.from_dict(result)


class RenderableType:
    def __init__(self, t: TypeKind) -> None:
        self.t: TypeKind = t

    def render(self, name: str) -> str:
        if self.t.kind == TypeKind.CONSTANTARRAY:
            res = f"{name}[{self.t.get_array_size()}]"
            element_type = RenderableType(self.t.get_array_element_type())
            return element_type.render(res)
        elif self.t.kind == TypeKind.INCOMPLETEARRAY:
            res = f"{name}[]"
            element_type = RenderableType(self.t.get_array_element_type())
            return element_type.render(res)
        elif self.t.kind == TypeKind.POINTER and self.t.get_pointee().kind == TypeKind.FUNCTIONPROTO:
            # param is of type function pointer
            pt = self.t.get_pointee()
            return f"{pt.get_result().spelling} (*{name})({','.join(arg.spelling for arg in pt.argument_types())})"
        else:
            return self.t.spelling + " " + name

    @property
    def is_constant(self) -> bool:
        if self.is_array:
            return self.t.element_type.is_const_qualified()
        else:
            return self.t.is_const_qualified()

    @property
    def is_array(self) -> bool:
        # many array kinds will make problems, but they are array types.
        return self.t.kind == TypeKind.CONSTANTARRAY or self.t.kind == TypeKind.INCOMPLETEARRAY or self.t.kind == TypeKind.VARIABLEARRAY or self.t.kind == TypeKind.DEPENDENTSIZEDARRAY

    @property
    def is_struct(self) -> bool:
        fields = list(self.t.get_canonical().get_fields())
        return len(fields) > 0

    def initializer(self) -> str:
        if self.is_struct:
            return f"({self.spelling}){{0}}"
        elif self.is_array:
            return "{0}"
        elif self.t.kind == TypeKind.VOID:
            return "void"
        else:
            return f"({self.spelling})0"

    @property
    def spelling(self) -> str:
        return self.t.spelling


class ConfigReader:
    section = "hammocking"
    configfile = Path(__file__).parent / (section + ".ini")

    def __init__(self, configfile: Optional[Path] = None):
        if configfile is None or configfile == Path(""):
            self.configfile = ConfigReader.configfile
        else:
            self.configfile = configfile
        self.exclude_paths: List[str] = []
        if not self.configfile.exists():
            return
        self.hammock_ini = HammockIni()

    def read(self) -> HammockIni:
        """
        Read the configuration from the given file.

        Args:
            configfile (Optional[Path]): The path to the configuration file. If None, the default config file is used.

        Returns:
            HammockIni: The configuration read from the file.
        """
        config = configparser.ConfigParser()
        config.read_string(self.configfile.read_text())
        # Read generic settings
        self._scan(config.items(section=self.section))
        # Read OS-specific settings
        os_section = f"{self.section}.{sys.platform}"
        if config.has_section(os_section):
            logging.debug(f"Reading OS-specific configuration from section: {os_section}")
        self._scan(config.items(section=os_section))
        return self.hammock_ini

    def _scan(self, items: List[Tuple[str, str]]) -> None:
        for item, value in items:
            if item == "clang_lib_file":
                self.hammock_ini.clang_lib_file = value
            if item == "clang_lib_path":
                self.hammock_ini.clang_lib_path = value
            if item == "nm":
                self.hammock_ini.nm_path = value
            if item == "ignore_path":
                self.hammock_ini.exclude_paths = value.split(",")
            if item == "include_pattern":
                self.hammock_ini.include_pattern = value
            if item == "exclude_pattern":
                self.hammock_ini.exclude_pattern = value


class Variable:
    def __init__(self, c: Cursor) -> None:
        self._type = RenderableType(c.type)
        self.name = c.spelling

    @property
    def type(self) -> str:
        """The variable type as string"""
        return self._type.spelling

    def get_definition(self, with_type: bool = True) -> str:
        if with_type:
            return self._type.render(self.name)
        else:
            return self.name

    def is_constant(self) -> bool:
        """Is constant qualified"""
        return self._type.is_constant

    def initializer(self) -> str:
        """C expression to represent the value "0" according to the variable type"""
        return self._type.initializer()

    def __repr__(self) -> str:
        return f"<{self.get_definition()}>"


class Function:
    def __init__(self, c: Cursor) -> None:
        self.type = RenderableType(c.result_type)
        self.name = c.spelling
        self.params = [Variable(arg) for arg in c.get_arguments()]
        self.is_variadic = c.type.is_function_variadic() if c.type.kind == TypeKind.FUNCTIONPROTO else False

    def get_signature(self) -> str:
        """
        Return the function declaration form
        """
        return f"{self.type.render(self.name)}({self._collect_arguments(True)}{', ...' if self.is_variadic else ''})"

    def _collect_arguments(self, with_types: bool) -> str:
        unnamed_index = 1
        arguments = []
        for param in self.params:
            if not param.name:
                param.name = "unnamed" + str(unnamed_index)
                unnamed_index = unnamed_index + 1
            arguments.append(param.get_definition(with_types))

        return ", ".join(arguments)

    def has_return_value(self) -> bool:
        """Does the function have a return value?"""
        return self.type.t.kind != TypeKind.VOID

    @property
    def return_type(self) -> str:
        """The function return type as string"""
        return self.type.spelling  # rendering includes the name, which is not what the user wants here.

    def default_return(self) -> str:
        """C expression to represent the value "0" according to the function return type"""
        return self.type.initializer()

    def get_call(self) -> str:
        """
        Return a piece of C code to call the function
        """
        # TODO: support variadic functions
        # if self.is_variadic:
        #
        # else:
        return f"{self.name}({self._collect_arguments(False)})"

    def get_param_types(self) -> str:
        """Return the function type parameters as a list of types"""
        param_types = ", ".join(f"{param.type}" for param in self.params)
        return f"{param_types}"

    def __repr__(self) -> str:
        return f"<{self.type} {self.name} ({self.get_param_types()})>"


class MockupWriter:
    def __init__(self, mockup_style: str = "gmock", suffix: str = "") -> None:
        self.headers: List[str] = []
        self.variables: List[Variable] = []
        self.functions: List[Function] = []
        self.template_dir: str = f"{dirname(__file__)}/templates"
        self.mockup_style: str = mockup_style
        self.suffix: str = suffix
        self.logger = logging.getLogger("Hammocking")
        self.environment = Environment(loader=FileSystemLoader(f"{self.template_dir}/{self.mockup_style}"), keep_trailing_newline=True, trim_blocks=True, autoescape=select_autoescape())

    def set_mockup_style(self, mockup_style: str) -> None:
        self.mockup_style = mockup_style

    def add_header(self, name: str) -> None:
        """Add a header to be included in mockup"""
        if name not in self.headers:
            self.headers.append(name)

    def add_variable(self, c: Cursor) -> None:
        """Add a variable definition"""
        self.logger.info(f"Create mockup for variable {c.spelling}")
        self.variables.append(Variable(c))

    def add_function(self, c: Cursor) -> None:
        """Add a variable definition"""
        self.logger.info(f"Create mockup for function {c.spelling}")
        self.functions.append(Function(c))

    def get_mockup(self, file: str) -> str:
        return self.render(Path(file + ".j2"))

    def render(self, file: Path) -> str:
        return self.environment.get_template(f"{file}").render(
            headers=sorted(self.headers), variables=sorted(self.variables, key=lambda x: x.name), functions=sorted(self.functions, key=lambda x: x.name), suffix=self.suffix
        )

    def write(self, outdir: Path) -> None:
        for file in listdir(f"{self.template_dir}/{self.mockup_style}"):
            if file.endswith(".j2"):
                Path(outdir, self.create_out_filename(file)).write_text(self.render(Path(file)))

    def create_out_filename(self, template_filename: str) -> str:
        template = Path(Path(template_filename).stem)
        return template.stem + (self.suffix if self.suffix else "") + template.suffix

    def default_language_mode(self) -> str:
        return "c++" if self.mockup_style in ["gmock"] else "c"


class Hammock:
    def __init__(
        self, symbols: Set[str], cmd_args: Optional[List[str]] = None, mockup_style: str = "gmock", suffix: str = "", project_root_dir: Optional[Path] = None, ignore_symbols_outside_project: bool = False
    ) -> None:
        self.logger = logging.getLogger("Hammocking")
        self.symbols: Set[str] = symbols
        self.cmd_args = cmd_args or []
        self.writer = MockupWriter(mockup_style, suffix)
        self.exclude_paths: List[str] = []
        self.project_root_dir = project_root_dir
        self.ignore_symbols_outside_project = ignore_symbols_outside_project

    def add_excludes(self, paths: Iterable[str]) -> None:
        self.exclude_paths.extend(paths)

    def read(self, sources: List[Path]) -> None:
        for source in sources:
            if self.done:
                break
            self.logger.debug(f"Parsing {source}")
            self.parse(source)

    @staticmethod
    def iter_children(cursor: Cursor) -> Iterator[Cursor]:
        """
        Iterate the direct children of the cursor (usually called with a translation unit), but dive into namespaces like extern "C" {
        """
        for child in cursor.get_children():
            if child.spelling:
                yield child
            elif child.kind == CursorKind.UNEXPOSED_DECL:  # if cursor is 'extern "C" {', loop inside
                yield from Hammock.iter_children(child)

    def parse(self, input: Union[Path, str]) -> None:
        parseOpts = {
            "args": self.cmd_args,
            "options": TranslationUnit.PARSE_SKIP_FUNCTION_BODIES | TranslationUnit.PARSE_INCOMPLETE,
        }
        # Determine language mode, if not explicitly given
        if not any(arg.startswith("-x") for arg in parseOpts["args"]):
            parseOpts["args"].append("-x" + self.writer.default_language_mode())

        if issubclass(type(input), Path):
            # Read a path
            parseOpts["path"] = input
            basepath = Path(input).parent.absolute()
        else:
            # Interpret a string as content of the file
            parseOpts["path"] = "~.c"
            parseOpts["unsaved_files"] = [("~.c", input)]
            basepath = Path.cwd()

        self.logger.debug(f"Symbols to be mocked: {self.symbols}")
        translation_unit = Index.create(excludeDecls=True).parse(**parseOpts)
        self.logger.debug(f"Parse diagnostics: {list(iter(translation_unit.diagnostics))}")
        self.logger.debug(f"Command arguments: {parseOpts['args']}")
        for child in self.iter_children(translation_unit.cursor):
            if child.spelling in self.symbols:
                if any(child.location.file.name.startswith(prefix) for prefix in self.exclude_paths):
                    self.logger.info(f"Skipping symbol {child.spelling} due to exclude path: {child.location.file}")
                elif self.ignore_symbols_outside_project and self.project_root_dir and self.project_root_dir.resolve() not in Path(child.location.file.name).resolve().parents:
                    self.logger.info(f"Skipping symbol {child.spelling} because it is not in the project: {child.location.file}")
                else:
                    in_header = child.location.file.name != translation_unit.spelling
                    if in_header:
                        headerpath = child.location.file.name
                        if headerpath.startswith("./"):
                            headerpath = (basepath / headerpath[2:]).as_posix()
                        self.writer.add_header(headerpath)
                        self.logger.info(f"Symbol {child.spelling} found in header file: {headerpath}")
                    else:
                        self.logger.info(f"Symbol {child.spelling} found in source file: {child.location.file}")
                    if child.kind == CursorKind.VAR_DECL:
                        self.writer.add_variable(child)
                    elif child.kind == CursorKind.FUNCTION_DECL:
                        self.writer.add_function(child)
                    else:
                        self.logger.warning(f"Unknown kind of symbol: {child.kind}")
                self.symbols.remove(child.spelling)

    def write(self, outdir: Path) -> None:
        self.writer.write(outdir)

    @property
    def done(self) -> bool:
        return len(self.symbols) == 0


class NmWrapper:
    nmpath = "nm"
    includepattern = None
    excludepattern: re.Pattern[str] = re.compile("^__gcov")
    if sys.platform == "darwin":  # Mac objects have an additional _
        pattern = r"\s*U\s+_(\S*)"
    else:
        pattern = r"\s*U\s+(\S*)"

    def __init__(self, plink: Path):
        self.plink = plink
        self.undefined_symbols: List[str] = []
        self.logger = logging.getLogger(self.__class__.__name__)
        self.__process()

    @classmethod
    def set_nm_path(cls, path: str) -> None:
        cls.nmpath = path

    @classmethod
    def set_include_pattern(cls, pattern: str) -> None:
        cls.includepattern = re.compile(pattern)

    @classmethod
    def set_exclude_pattern(cls, pattern: str) -> None:
        cls.excludepattern = re.compile(pattern)

    def get_undefined_symbols(self) -> Set[str]:
        return set(self.undefined_symbols)

    def __process(self) -> None:
        self.logger.debug(f"Processing nm command for: {self.plink}")
        executor = SubprocessExecutor(command=[NmWrapper.nmpath, self.plink], capture_output=True, print_output=False)
        completed_process = executor.execute(handle_errors=False)
        if completed_process:
            if completed_process.returncode != 0:
                raise CalledProcessError(completed_process.returncode, completed_process.args, stderr=completed_process.stderr)

            # Process the output
            for line in completed_process.stdout.splitlines():
                symbol = self.mock_it(line)
                if symbol:
                    self.undefined_symbols.append(symbol)

            if not self.undefined_symbols:
                self.logger.info("No symbols to be mocked found by nm.")
            else:
                self.logger.debug(f"Symbols found by nm: {self.undefined_symbols}")
            self.logger.debug(f"Finished processing nm command for: {self.plink}")
        else:
            raise UnboundLocalError("nm command failed")

    @classmethod
    def mock_it(cls, symbol: str) -> Optional[str]:
        if match := re.match(cls.pattern, symbol):
            symbol = match.group(1)
            if cls.includepattern and re.match(cls.includepattern, symbol):
                logging.debug(symbol + " to be mocked (via include pattern)")
                return symbol
            elif cls.excludepattern is None or re.match(cls.excludepattern, symbol) is None:
                logging.debug(symbol + " to be mocked")
                return symbol
            else:
                logging.debug(symbol + " is excluded")
        return None


class HammockRunner:
    def __init__(self, hammock_config: HammockConfig):
        self.hammock_config = hammock_config
        if self.hammock_config.config and self.hammock_config.config.exists():
            ini_config = ConfigReader(self.hammock_config.config)
        else:
            ini_config = ConfigReader()
        if ini_config:
            hammock_ini = ini_config.read()
            self.hammock_config = self.hammock_config.merge(hammock_ini)
        self.update_system()

    def update_system(self) -> None:
        if self.hammock_config.clang_lib_file:
            if not Config.loaded:
                Config.set_library_file(self.hammock_config.clang_lib_file)
        if self.hammock_config.clang_lib_path:
            if not Config.loaded:
                Config.set_library_path(self.hammock_config.clang_lib_path)
        if self.hammock_config.nm_path:
            NmWrapper.set_nm_path(self.hammock_config.nm_path)
        if self.hammock_config.include_pattern:
            NmWrapper.set_include_pattern(self.hammock_config.include_pattern)
        if self.hammock_config.exclude_pattern:
            NmWrapper.set_exclude_pattern(self.hammock_config.exclude_pattern)

    def run(self) -> int:
        if self.hammock_config.plink and not self.hammock_config.symbols:
            self.hammock_config.symbols = NmWrapper(self.hammock_config.plink).get_undefined_symbols()

        if self.hammock_config.symbols and self.hammock_config.exclude:
            self.hammock_config.symbols -= set(self.hammock_config.exclude)

        self.hammock = Hammock(
            symbols=self.hammock_config.symbols if self.hammock_config.symbols else set(),
            cmd_args=self.hammock_config.cmd_args if self.hammock_config.cmd_args else [],
            mockup_style=self.hammock_config.style if self.hammock_config.style else "gmock",
            suffix=self.hammock_config.suffix if self.hammock_config.suffix else "",
            ignore_symbols_outside_project=self.hammock_config.ignore_symbols_outside_project if self.hammock_config.ignore_symbols_outside_project else False,
            project_root_dir=self.hammock_config.project_root_dir if self.hammock_config.project_root_dir else None,
        )
        self.hammock.add_excludes(self.hammock_config.exclude_paths if self.hammock_config.exclude_paths else [])
        self.hammock.read(self.hammock_config.sources)
        self.hammock.write(self.hammock_config.outdir)

        if self.hammock.done:
            logging.info("Hammocking finished successfully.")
            return 0
        else:
            logging.error("Hammocking failed. The following symbols could not be mocked:\n" + "\n".join(self.hammock.symbols))
            return 1

    def get_symbols(self) -> List[str]:
        """Get the symbols that could not be mocked."""
        return list(self.hammock.symbols) if self.hammock else []


def main(pargv: List[str]) -> None:
    arg = ArgumentParser(fromfile_prefix_chars="@", prog="hammocking")

    group_symbols_xor_plink = arg.add_mutually_exclusive_group(required=True)
    group_symbols_xor_plink.add_argument("--symbols", "-s", help="Symbols to mock", nargs="+")
    group_symbols_xor_plink.add_argument("--plink", "-p", help="Path to partially linked object", type=Path)

    arg.add_argument("--debug", "-d", help="Debugging", required=False, default=False, action="store_true")
    arg.add_argument("--outdir", "-o", help="Output directory", required=True, type=Path)
    arg.add_argument("--sources", help="List of source files to be parsed", type=Path, required=True, nargs="+")

    arg.add_argument("--style", "-t", help="Mockup style to output", required=False, default="gmock")
    arg.add_argument("--suffix", help="Suffix to be added to the generated files", required=False, default="")
    arg.add_argument("--except", help="Path prefixes that should not be mocked", nargs="*", dest="exclude_pathes", default=["/usr/include"])
    arg.add_argument("--exclude", help="Symbols that should not be mocked", nargs="*", default=[])
    arg.add_argument("--config", help="Configuration file", required=False, default="")
    arg.add_argument("--exclude-pattern", help="Exclude symbols matching this pattern", required=False)
    arg.add_argument("--clang-lib-file", help="Path to the Clang library file", required=False)
    arg.add_argument("--clang-lib-path", help="Path to the Clang library directory", required=False)
    arg.add_argument("--nm-path", help="Path to the nm command", required=False)
    arg.add_argument("--include-pattern", help="Include symbols matching this pattern", required=False)
    arg.add_argument("--ignore-symbols-outside-project", help="Used to exclude symbols not found in the project-root-directory.", default=False, action="store_true", required=False)
    arg.add_argument("--project-root-dir", help="Path to the project root directory", type=Path, required=False)
    args, cmd_args = arg.parse_known_args(args=pargv)

    args.cmd_args = cmd_args

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)
    logging.debug(f"Extra arguments: {args.cmd_args}")
    hammock_config = HammockConfig.from_namespace(args)
    hammock_runner = HammockRunner(hammock_config)
    result = hammock_runner.run()
    if result != 0:
        sys.stderr.write("Hammocking failed. The following symbols could not be mocked:\n" + "\n".join(hammock_runner.get_symbols()) + "\n")
        exit(1)
    exit(0)


if __name__ == "__main__":
    main(sys.argv)
