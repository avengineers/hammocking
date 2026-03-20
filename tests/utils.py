#!/usr/bin/env python3

"""
Utility functions needed by all test scripts.
"""

from subprocess import PIPE, Popen


def run_process(args: list[str], cwd: str | None = None) -> int:
    with Popen(args, stdout=PIPE, stderr=PIPE, bufsize=1, universal_newlines=True, cwd=cwd) as p:
        if p.stdout:
            for line in p.stdout:
                print(line, end="")
        if p.stderr:
            for line in p.stderr:
                print(line, end="")

    return p.returncode


def cmake_configure(project_dir: str, build_dir: str) -> int:
    return run_process(["cmake", "-S", project_dir, "-B", build_dir, "-G", "Ninja"])


def cmake_build_target(build_dir: str, target: str) -> int:
    return run_process(["cmake", "--build", build_dir, "--target", target])
