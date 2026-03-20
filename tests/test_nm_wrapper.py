from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from subprocess import CalledProcessError, CompletedProcess
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from py_app_dev.core.subprocess import SubprocessExecutor

from hammocking.hammocking import NmWrapper


def test_regex():
    assert not NmWrapper.mock_it("some_func")
    assert "some_func" == NmWrapper.mock_it("            U some_func")
    assert not NmWrapper.mock_it("__gcov_exit")
    assert not NmWrapper.mock_it("            U __gcov_exit")


def test_custom_regex():
    # TODO: Because the include/exclude patterns are class variables, updating these patterns will affect all other tests :O. Please avoid using class variables!
    NmWrapper.set_exclude_pattern("^_")
    NmWrapper.set_include_pattern("^_(xyz)")
    assert not NmWrapper.mock_it("   U _abc")  # Every underline function is now excluded
    assert "_xyz" == NmWrapper.mock_it("   U _xyz")  # ... except _xyz


@contextmanager
def mock_subprocess_executor(completed_process: CompletedProcess[Any]) -> Generator[MagicMock | AsyncMock, Any, None]:
    """Context manager to patch SubprocessExecutor.execute with a predefined CompletedProcess result."""
    with patch(SubprocessExecutor.__module__ + ".SubprocessExecutor.execute") as mock_execute:
        mock_execute.return_value = completed_process
        yield mock_execute


def test_nm_empty():
    with mock_subprocess_executor(CompletedProcess(args=["nm"], returncode=0, stdout="", stderr="")):
        nm_wrapper = NmWrapper(Path("some_object.o"))
        assert nm_wrapper.undefined_symbols == []


def test_nm_fails():
    with mock_subprocess_executor(CompletedProcess(args=["nm"], returncode=1, stdout="", stderr="")):
        with pytest.raises(CalledProcessError) as exception_info:
            NmWrapper(Path("some_object.o"))
        assert exception_info.value.returncode == 1
        assert exception_info.value.cmd == ["nm"]


def test_nm_returns_some_symbols():
    with mock_subprocess_executor(CompletedProcess(args=["nm"], returncode=0, stdout="some info\n   U my_symbol\n   U my_var\n", stderr="")):
        nm_wrapper = NmWrapper(Path("some_object.o"))
        nm_wrapper.set_include_pattern("^my_")
        assert set(nm_wrapper.undefined_symbols) == {"my_symbol", "my_var"}
