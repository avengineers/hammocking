#!/usr/bin/env python3

from subprocess import Popen, PIPE


"""
Utility functions needed by all test scripts.
"""


def run_process(args, cwd=None):
    with Popen(args, stdout=PIPE, stderr=PIPE, bufsize=1, universal_newlines=True, cwd=cwd) as p:
        for line in p.stdout:
            print(line, end="")
        for line in p.stderr:
            print(line, end="")

    return p.returncode
