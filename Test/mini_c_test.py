#!/usr/bin/env python3

import os
from platform import system
from Test.utils import run_process


class TestMiniCProject:
    def test_clean_build(self):
        project_dir = "resources/mini_c"
        build_dir = f"{project_dir}/build"
        if system() == "Windows":
            binary = f"{build_dir}/mini_c.exe"
        else:
            binary = f"{build_dir}/mini_c"

        exit_code = run_process(["cmake", "-S", project_dir, "-B", build_dir, "-G", "Ninja"])
        """CMake configure shall be successful."""
        assert exit_code == 0

        exit_code = run_process(["cmake", "--build", build_dir, "--target", "clean"])
        """CMake clean shall be successful."""
        assert exit_code == 0
        assert not os.path.isfile(binary)

        exit_code = run_process(["cmake", "--build", build_dir])
        """CMake build shall create expected mockups and binary."""
        assert exit_code == 0
        assert os.path.isfile(binary)

        exit_code = run_process([f"./{binary}"])
        """Built binary shall return with failure"""
        assert exit_code == 1
