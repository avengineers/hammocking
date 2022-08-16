#!/usr/bin/env python3

import unittest
from src.hammock import *
from Test.utils import *


class TestSections(unittest.TestCase):
    def test_empty(self):
        """The empty mockup section"""
        sect = MOCK_SECTION("something", True)
        self.assertEqual("", str(sect), "An empty section has no content")

    def test_var(self):
        """Mock a variable"""
        sect = MOCK_SECTION("something", False)
        sect.add_var("int", "x")
        self.assertEqual(
            f"""#ifdef {sect.section_guard["code"]}
int x;
#endif
""",
            str(sect),
            "A section with variable",
        )

    def test_var_config(self):
        """Mock a variable with a config guard"""
        sect = MOCK_SECTION("something", True)
        sect.add_var("int", "x")
        self.assertEqual(
            f"""#ifdef HAM_something
#ifdef {sect.section_guard["code"]}
int x;
#endif
#endif // HAM_something
""",
            str(sect),
            "A section with variable",
        )

    def test_void_function(self):
        """Mock a function with void return type and void parameters"""
        sect = MOCK_SECTION("something", True)
        sect.add_function("void", "x", [])
        self.assertEqual(
            f"""#ifdef HAM_something
#ifdef {sect.section_guard["code"]}
void x(void)
{{
}}
#endif
#endif // HAM_something
""",
            str(sect),
            "A section with a void function",
        )

    def test_int_function(self):
        """Mock a function with int return type and void parameters"""
        sect = MOCK_SECTION("something", True)
        sect.add_function("int", "x", [])
        self.assertEqual(
            f"""#ifdef HAM_something
#ifdef {sect.section_guard["code"]}
int x(void)
{{
   return x__return;
}}
#endif
#endif // HAM_something
""",
            str(sect),
            "A section with a int function",
        )

    def test_ext_var(self):
        """Mock a global variable"""
        sect = MOCK_SECTION("something", True)
        sect.add_global_var("int", "x")
        self.assertEqual(
            f"""#ifdef HAM_something
#ifdef {sect.section_guard["global_var"]}
extern int x;
#endif
#endif // HAM_something
""",
            str(sect),
            "A section with a global variable",
        )


class TestAutomocker(unittest.TestCase):
    def test_variable(self):
        """Mock a variable"""
        mock = AUTOMOCKER(["a"])
        self.assertFalse(mock.done, "Should not be done yet")
        self.assertListEqual(mock.symbols, ["a"])

        mock.read("extern int a;")
        self.assertTrue(mock.done, "Should be done now")
        self.assertListEqual(mock.symbols, [])
        self.assertEqual(len(mock.mockups), 1, "Shall have created a mockup")
        self.assertEqual(len(mock.mockups[0].vars), 1, "Mockup shall have a variable")
        self.assertEqual(mock.mockups[0].vars[0], ("int", "a"), "Variable shall be created in the mockup")

    def test_void_func(self):
        """Mock a void(void) function"""
        mock = AUTOMOCKER(["x"])
        mock.read("extern void x(void);")
        self.assertTrue(mock.done, "Should be done now")
        self.assertEqual(len(mock.mockups), 1, "Shall have created a mockup")
        self.assertEqual(len(mock.mockups[0].functions), 1, "Mockup shall have a function")
        self.assertEqual(len(mock.mockups[0].global_vars), 0, "Mockup shall have no global variable")
        self.assertEqual(mock.mockups[0].functions[0], ("void", "x", []), "Function shall be created in the mockup")

    def test_int_int_func(self):
        """Mock a int(int) function"""
        mock = AUTOMOCKER(["xxx"])
        mock.read("extern int xxx(int var1);")
        self.assertTrue(mock.done, "Should be done now")
        self.assertEqual(len(mock.mockups), 1, "Shall have created a mockup")
        self.assertEqual(len(mock.mockups[0].functions), 1, "Mockup shall have a function")
        self.assertEqual(len(mock.mockups[0].global_vars), 1, "Mockup shall have a global variable")
        self.assertEqual(
            mock.mockups[0].functions[0], ("int", "xxx", [("int", "var1")]), "Function shall be created in the mockup"
        )
        self.assertEqual(
            mock.mockups[0].global_vars[0], ("int", "xxx__return"), "return value shall be a global variable"
        )

    def test_variable_with_config_guard(self):
        """Mock a variable with config guard"""
        mock = AUTOMOCKER(["b"])
        mock.read(
            """#ifdef SOME_CONFIG
extern int b;
#endif
"""
        )
        assert False == mock.done, "Should not be done due to missing definition"

        mock = AUTOMOCKER(["b"], ["-DSOME_CONFIG"])
        mock.read(
            """#ifdef SOME_CONFIG
extern int b;
#endif
"""
        )
        assert mock.done, "Should be done now"

        assert len(mock.mockups) == 1, "Shall have created a mockup"
        assert len(mock.mockups[0].vars) == 1, "Mockup shall have a variable"
        assert mock.mockups[0].vars[0] == ("int", "b"), "Variable shall be created in the mockup"

    def test_variable_and_function_with_config_guards(self):
        """Mock a variable and a function with different config guards"""
        mock = AUTOMOCKER(["b", "foo"], ["-DSOME_CONFIG", "-DSOME_OTHER_CONFIG=2"])
        mock.read(
            """#ifdef SOME_CONFIG
extern int b;
#endif

#ifdef SOME_OTHER_CONFIG
extern void foo();
#endif

#ifdef SOME_FUNC_TO_BE_IGNORED
extern void ignore_me();
#endif
"""
        )
        assert mock.done, "Should be done now"
        assert len(mock.mockups) == 2, "Shall have created two mockup"
        assert len(mock.mockups[0].vars) == 1, "Mockup shall have a variable"
        assert mock.mockups[0].vars[0] == ("int", "b"), "Variable shall be created in the mockup"
        assert len(mock.mockups[1].functions) == 1, "Mockup shall have a function"
        assert mock.mockups[1].functions[0] == ("void", "foo", []), "Function shall be created in the mockup"


class TestSymbols(unittest.TestCase):
    def test_getSymbols(self):
        project_dir = "resources/mini_c_plink"
        build_dir = f"{project_dir}/build"
        exit_code = cmake_configure(project_dir, build_dir)
        assert exit_code == 0
        exit_code = cmake_build_target(build_dir, "clean")
        assert exit_code == 0
        exit_code = exit_code = cmake_build_target(build_dir, "all")
        assert exit_code == 0
        symbols = Symbols(f"{build_dir}/prod.obj")
        assert ["c", "d", "some_var"] == symbols.getSymbols(), ""
        pass


if __name__ == "__main__":
    unittest.main()
