#!/usr/bin/env python3

import os
from Test.utils import run_process


class TestMiniCProject:
    def test_clean_build(self):
        project_dir = "resources/mini_c"
        build_dir = f"{project_dir}/build"

        exit_code = run_process(["cmake", "-S", project_dir, "-B", build_dir, "-G", "Ninja"])
        """CMake configure shall be successful."""
        assert exit_code == 0

        exit_code = run_process(["cmake", "--build", build_dir, "--target", "clean"])
        """CMake clean shall be successful."""
        assert exit_code == 0
        assert not os.path.isfile(f"{build_dir}/mockups.mockup")
        assert not os.path.isfile(f"{build_dir}/mini_c.exe")

        exit_code = run_process(["cmake", "--build", build_dir])
        """CMake build shall create expected mockups and binary."""
        assert exit_code == 0
        assert os.path.isfile(f"{build_dir}/mockups.mockup")
        assert os.path.isfile(f"{build_dir}/mini_c.exe")

        exit_code = run_process([f"{build_dir}/mini_c.exe"])
        """Built binary shall be executable"""
        assert exit_code == 0
