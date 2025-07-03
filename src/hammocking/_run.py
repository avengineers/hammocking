"""
Used to run hammocking from the command line when run from this repository.

This is required because hammocking module is not visible when running from the repository.
"""

import runpy
import sys
from pathlib import Path

sys.path.insert(0, Path(__file__).parent.parent.absolute().as_posix())
runpy.run_module("hammocking.main", run_name="__main__")
