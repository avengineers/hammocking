from argparse import Namespace
import logging
import sys
from pathlib import Path
from typing import Annotated, List, Optional

import typer
from py_app_dev.core.exceptions import UserNotificationException
from py_app_dev.core.logging import logger, setup_logger, time_it

from hammocking import __version__
from hammocking.hammocking import ConfigReader, Hammock, HammockConfig, HammockRunner, NmWrapper

package_name = "hammocking"

app = typer.Typer(name=package_name, help="an extension for hammocking in spl-core")


@app.callback(invoke_without_command=True)
def version(
    version: bool = typer.Option(None, "--version", "-v", is_eager=True, help="Show version and exit."),
) -> None:
    if version:
        typer.echo(f"{package_name} {__version__}")
        raise typer.Exit()


@app.command()
@time_it("init")
def init(project_dir: Path = typer.Option(Path.cwd().absolute(), help="The project directory"), enable: bool = False) -> None:  # noqa: B008
    logger.info(f"Initializing project in {project_dir} with enable={enable}")


@app.command()
@time_it("run")
def run(
    ctx: typer.Context,
    outdir: Annotated[Path, typer.Option(..., "--outdir", help="The output directory.")],
    sources: Annotated[List[Path], typer.Option(..., "--sources", help="List of source files to be parsed.")],
    symbols: Annotated[Optional[List[str]], typer.Option(..., "--symbols", "-s", help="The symbols to mock.")] = None,
    plink: Annotated[Optional[Path], typer.Option(..., "--plink", help="The path to the partially linked object.")] = None,
    debug: Annotated[Optional[bool], typer.Option(..., "--debug", help="Debugging.")] = False,
    style: Annotated[Optional[str], typer.Option(..., "--style", "-t", help="Mockup style to output.")] = "gmock",
    suffix: Annotated[Optional[str], typer.Option(..., "--suffix", help="Suffix to be added to the generated files.")] = "",
    exclude_paths: Annotated[Optional[List[str]], typer.Option(..., "--except", help="Path prefixes that should not be mocked.")] = None,
    exclude_symbols: Annotated[Optional[List[str]], typer.Option(..., "--exclude", help="Symbols that should not be mocked.")] = None,
    config: Annotated[Optional[str], typer.Option(..., "--config", help="Configuration file.")] = "",
    clang_lib_file: Annotated[Optional[str], typer.Option(..., "--clang-lib-file", help="The path to the clang library file.")] = None,
    clang_lib_path: Annotated[Optional[str], typer.Option(..., "--clang-lib-path", help="The path to the clang library path.")] = None,
    ignore_path: Annotated[Optional[List[str]], typer.Option(..., "--ignore-path", help="List of paths to ignore.")] = None,
    nm_path: Annotated[Optional[str], typer.Option(..., "--nm", help="The path to the nm executable.")] = None,
    include_pattern: Annotated[Optional[str], typer.Option(..., "--include-pattern", help="Pattern to include files for parsing.")] = None,
    exclude_pattern: Annotated[Optional[str], typer.Option(..., "--exclude-pattern", help="Pattern to exclude files from parsing.")] = None,
    cmd_args: List[str] = typer.Argument(..., help="Unnamed positional arguments"),  # noqa: B008
) -> None:

    namespace = Namespace(**ctx.params)
    hammock_config = HammockConfig.from_namespace(namespace)
    hammock_runner = HammockRunner(hammock_config)
    result = hammock_runner.run()
    if result != 0:
        sys.stderr.write("Hammocking failed. The following symbols could not be mocked:\n" + "\n".join(hammock_runner.get_symbols()) + "\n")
        exit(1)
    exit(0)


def main() -> int:
    try:
        setup_logger()
        app()
        return 0
    except UserNotificationException as e:
        logger.error(f"{e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
