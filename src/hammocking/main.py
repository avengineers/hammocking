import logging
import sys
from pathlib import Path
from typing import Annotated, List, Optional

import typer
from py_app_dev.core.exceptions import UserNotificationException
from py_app_dev.core.logging import logger, setup_logger, time_it

from hammocking import __version__
from hammocking.hammocking import ConfigReader, Hammock, NmWrapper

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
    outdir: Annotated[Path, typer.Option(..., "--outdir", help="The output directory.")],
    sources: Annotated[List[Path], typer.Option(..., "--sources", help="List of source files to be parsed.")],
    symbols: Annotated[Optional[List[str]], typer.Option(..., "--symbols", "-s", help="The symbols to mock.")] = None,
    plink: Annotated[Optional[Path], typer.Option(..., "--plink", help="The path to the partially linked object.")] = None,
    debug: Annotated[Optional[bool], typer.Option(..., "--debug", help="Debugging.")] = False,
    style: Annotated[Optional[str], typer.Option(..., "--style", "-t", help="Mockup style to output.")] = "gmock",
    suffix: Annotated[Optional[str], typer.Option(..., "--suffix", help="Suffix to be added to the generated files.")] = "",
    exclude_paths: Annotated[Optional[List[str]], typer.Option(..., "--except", help="Path prefixes that should not be mocked.")] = None,
    exclude: Annotated[Optional[List[str]], typer.Option(..., "--exclude", help="Symbols that should not be mocked.")] = None,
    config: Annotated[Optional[str], typer.Option(..., "--config", help="Configuration file.")] = "",
    cmd_args: List[str] = typer.Argument(..., help="Unnamed positional arguments"),  # noqa: B008
) -> None:
    logging.basicConfig(level=logging.DEBUG if debug else logging.INFO)
    config = ConfigReader(Path(config))
    if exclude_paths is None:
        exclude_paths = ["/usr/include"]
    if exclude is None:
        exclude = []
    exclude_paths += config.exclude_paths
    if not symbols:
        symbols = NmWrapper(plink).get_undefined_symbols()

    symbols -= set(exclude)

    logger.debug(f"Extra arguments: {cmd_args}")

    h = Hammock(symbols=symbols, cmd_args=cmd_args, mockup_style=style, suffix=suffix)
    h.add_excludes(exclude_paths)
    h.read(sources)
    h.write(outdir)

    if not h.done:
        sys.stderr.write("Hammocking failed. The following symbols could not be mocked:\n" + "\n".join(h.symbols) + "\n")
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
