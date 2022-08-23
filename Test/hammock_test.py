#!/usr/bin/env python3

import unittest
from src.hammock import *
from Test.utils import *


class TestHammock(unittest.TestCase):
    def test_variable(self):
        """Mock a variable"""
        mock = Hammock(["a"])
        self.assertFalse(mock.done, "Should not be done yet")
        self.assertListEqual(mock.symbols, ["a"])

        mock.parse("extern int a;")
        self.assertTrue(mock.done, "Should be done now")
        self.assertListEqual(mock.symbols, [])
        self.assertEqual(len(mock.writer.variables), 1, "Mockup shall have a variable")
        self.assertEqual(mock.writer.variables[0].get_definition(), "int a", "Variable shall be created in the mockup")

    def test_void_func(self):
        """Mock a void(void) function"""
        mock = Hammock(["x"])
        mock.parse("extern void x(void);")
        self.assertTrue(mock.done, "Should be done now")
        self.assertEqual(len(mock.writer.functions), 1, "Mockup shall have a function")
        self.assertEqual(
            mock.writer.functions[0].get_signature(), "void x()", "Function shall be created in the mockup"
        )

    def test_int_int_func(self):
        """Mock a int(int) function"""
        mock = Hammock(["xxx"])
        mock.parse("extern int xxx(int var1);")
        self.assertTrue(mock.done, "Should be done now")
        self.assertEqual(len(mock.writer.functions), 1, "Mockup shall have a function")
        self.assertEqual(
            mock.writer.functions[0].get_signature(), "int xxx(int var1)", "Function shall be created in the mockup"
        )

    def test_variable_with_config_guard(self):
        """Mock a variable with config guard"""
        mock = Hammock(["b"])
        mock.parse(
            """#ifdef SOME_CONFIG
extern int b;
#endif
"""
        )
        assert False == mock.done, "Should not be done due to missing definition"

        mock = Hammock(["b"], ["-DSOME_CONFIG"])
        mock.parse(
            """#ifdef SOME_CONFIG
extern int b;
#endif
"""
        )
        assert mock.done, "Should be done now"

        assert len(mock.writer.variables) == 1, "Mockup shall have a variable"
        assert mock.writer.variables[0].get_definition() == "int b", "Variable shall be created in the mockup"

    def test_variable_and_function_with_config_guards(self):
        """Mock a variable and a function with different config guards"""
        mock = Hammock(["b", "foo"], ["-DSOME_CONFIG", "-DSOME_OTHER_CONFIG=2"])
        mock.parse(
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
        assert len(mock.writer.variables) == 1, "Mockup shall have a variable"
        assert mock.writer.variables[0].get_definition() == "int b", "Variable shall be created in the mockup"
        assert len(mock.writer.functions) == 1, "Mockup shall have a function"
        assert mock.writer.functions[0].get_signature() == "void foo()", "Function shall be created in the mockup"


if __name__ == "__main__":
    unittest.main()
