#!/usr/bin/env python3

import unittest

import pytest

from hammocking.hammocking import *


class TestVariable:
    def test_creation(self):
        v = Variable("char", "x")
        assert v.name == "x"
        assert v.type == "char"
        assert v.get_definition() == "char x"
        
        w = Variable("int", "my_array", 2)
        assert w.name == "my_array"
        assert w.type == "int"
        assert w.get_definition() == "int my_array[2]"


class TestFunction:
    def test_void_void(self):
        f = Function(type="void", name="func", params=[])
        assert f.name == "func"
        assert f.get_signature() == "void func()"
        assert f.get_call() == "func()"
        assert f.get_param_types() == ""
        assert f.has_return_value() == False

    def test_void_int(self):
        f = Function(type="void", name="set", params=[Variable('int', 'a')])
        assert f.name == "set"
        assert f.get_signature() == "void set(int a)"
        assert f.get_call() == "set(a)"
        assert f.get_param_types() == "int"
        assert f.has_return_value() == False

    def test_int_void(self):
        f = Function(type="int", name="get", params=[])
        assert f.name == "get"
        assert f.get_signature() == "int get()"
        assert f.get_call() == "get()"
        assert f.get_param_types() == ""
        assert f.has_return_value() == True

    def test_void_int_double(self):
        f = Function(type="void", name="set", params=[Variable('int', 'a'), Variable('double', 'b')])
        assert f.name == "set"
        assert f.get_signature() == "void set(int a, double b)"
        assert f.get_call() == "set(a, b)"
        assert f.get_param_types() == "int, double"
        # assert f.has_return_value() == False

    def test_function_with_unnamed_arguments(self):
        f = Function(type="float", name="my_func", params=[Variable('float', ''), Variable('float', '')])
        assert f.name == "my_func"
        assert f.get_signature() == "float my_func(float unnamed1, float unnamed2)"
        assert f.get_call() == "my_func(unnamed1, unnamed2)"
        assert f.get_param_types() == "float, float"


class TestMockupWriter:
    def test_empty_templates(self):
        writer = MockupWriter()
        assert writer.get_mockup('mockup.h') == open("tests/data/gmock_test/test_empty_templates/mockup.h").read()
        assert writer.get_mockup('mockup.cc') == open("tests/data/gmock_test/test_empty_templates/mockup.cc").read()

    @pytest.mark.parametrize(
        "filename,suffix,expected_name",
        [
            ("my_file.c.j2", None, "my_file.c"),
            ("my_file.cpp.j2", "_new", "my_file_new.cpp")
        ],
    )
    def test_create_out_filename(self, filename, suffix, expected_name):
        """ @validates Req0001 """
        writer = MockupWriter(suffix=suffix)
        assert writer.create_out_filename(filename) == expected_name

    def test_add_header(self):
        writer = MockupWriter()
        writer.add_header("y.h")
        writer.add_header("a.h")
        writer.add_header("x.h")
        assert (
                writer.get_mockup('mockup.h')
                == """#ifndef mockup_h
#define mockup_h

#include "gmock/gmock.h" 

extern "C" {
#include "a.h"
#include "x.h"
#include "y.h"
} /* extern "C" */

class class_mockup {

   public:
}; /* class_mockup */

extern class_mockup *mockup_global_ptr;

#define CREATE_MOCK(name)   class_mockup name; mockup_global_ptr = &name;

#endif /* mockup_h */
"""
        )

    def test_add_variable(self):
        writer = MockupWriter(suffix="_new")
        writer.add_variable("float", "y")
        writer.add_variable("unsigned int", "a")
        writer.add_variable("int", "x")

        assert (
                writer.get_mockup('mockup.h')
                == """#ifndef mockup_new_h
#define mockup_new_h

#include "gmock/gmock.h" 

extern "C" {
} /* extern "C" */

class class_mockup {

   public:
}; /* class_mockup */

extern class_mockup *mockup_global_ptr;

#define CREATE_MOCK(name)   class_mockup name; mockup_global_ptr = &name;

#endif /* mockup_new_h */
"""
        )

        assert (
                writer.get_mockup('mockup.cc')
                == """#include "mockup_new.h"

class_mockup *mockup_global_ptr = 0;

unsigned int a;
int x;
float y;

"""
        )

    def test_add_function_get(self):
        writer = MockupWriter()
        writer.add_function("int", "a_get_y2", [])
        assert writer.get_mockup('mockup.h') == open("tests/data/gmock_test/test_add_function_get/mockup.h").read()
        assert writer.get_mockup('mockup.cc') == open("tests/data/gmock_test/test_add_function_get/mockup.cc").read()

    def test_add_function_set_one_arg(self):
        writer = MockupWriter()
        writer.add_function("void", "set_some_int", [("int", "some_value")])
        assert writer.get_mockup('mockup.h') == open(
            "tests/data/gmock_test/test_add_function_set_one_arg/mockup.h").read()
        assert writer.get_mockup('mockup.cc') == open(
            "tests/data/gmock_test/test_add_function_set_one_arg/mockup.cc").read()

    def test_add_function_with_unnamed_arg(self):
        writer = MockupWriter()
        writer.add_function("float", "my_func", [("float", "")])
        assert writer.get_mockup('mockup.h') == open(
            "tests/data/gmock_test/test_add_function_with_unnamed_arg/mockup.h").read()
        assert writer.get_mockup('mockup.cc') == open(
            "tests/data/gmock_test/test_add_function_with_unnamed_arg/mockup.cc").read()

    def test_mini_c_gmock(self):
        writer = MockupWriter()
        writer.add_header("a.h")
        writer.add_header("c.h")
        writer.add_variable("int", "a_y1")
        writer.add_variable("int", "c_u1")
        writer.add_variable("a_y4_t", "a_y4")
        writer.add_function("int", "a_get_y2", [])
        writer.add_function("int", "a_get_y3_and_set_u5", [("int", "u5")])
        writer.add_function("a_y5_t", "a_get_y5", [])
        writer.add_function("void", "a_get_y6", [("int*", "y6")])
        writer.add_function("int", "c_get_y3_and_set_u5", [("int", "u5")])
        writer.add_function("void", "c_set_u2", [("int", "u2")])
        writer.add_function("void", "c_set_u3_and_u4", [("int", "u3"), ("int", "u4")])
        writer.add_function("void", "c_set_u6", [("c_u6_t", "u6")])
        assert writer.get_mockup('mockup.h') == open("tests/data/gmock_test/test_mini_c_gmock/mockup.h").read()
        assert writer.get_mockup('mockup.cc') == open("tests/data/gmock_test/test_mini_c_gmock/mockup.cc").read()

    def test_languagemode(self):
        writer = MockupWriter()
        assert writer.default_language_mode() == 'c++'
        writer.set_mockup_style('plain_c')
        assert writer.default_language_mode() == 'c'


class TestNmWrapper(unittest.TestCase):
    regex = NmWrapper.regex

    def test_regex(self):
        line = 'some_func'
        match = re.match(self.regex, line)
        assert not match

        line = '         U some_func'
        match = re.match(self.regex, line)
        assert 'some_func' == match.group(1)

        line = '__gcov_exit'
        match = re.match(self.regex, line)
        assert not match

        line = '         U __gcov_exit'
        match = re.match(self.regex, line)
        assert not match


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

    def test_variable_array(self):
        """Mock an int array"""
        mock = Hammock(["my_array"])
        mock.parse("extern int my_array[2];")
        assert mock.done, "Should be done now"
        assert len(mock.writer.variables) == 1, "Mockup shall have a variable"
        assert mock.writer.variables[0].get_definition() == "int my_array[2]", "Variable shall be created in the mockup" 

    def test_langmode_auto(self):
        """Read as c++ compiler determined from output style"""
        mock = Hammock(["bool_status"])
        mock.parse(Path("tests/data/mini_c++_test/use_bool.c"))
        assert mock.done, "Should be done now"
        assert len(mock.writer.functions) == 1, "Mockup shall have a function"
        assert mock.writer.functions[0].get_signature() == "bool bool_status()", "Function shall be created with bool type"

    def test_langmode_override(self):
        """Read as c compiler"""
        mock = Hammock(["bool_status"], ["-xc"])
        mock.parse(Path("tests/data/mini_c++_test/use_bool.c"))
        assert mock.done, "Should be done now"
        assert len(mock.writer.functions) == 1, "Mockup shall have a function"
        assert mock.writer.functions[0].get_signature() == "_Bool bool_status()", "Function shall be created with C99 bool type"


if __name__ == "__main__":
    unittest.main()
