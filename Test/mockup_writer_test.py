#!/usr/bin/env python3

from src.mockup_writer import *


class TestVariable:
    def test_creation(self):
        v = Variable("char", "x")
        assert v.name == "x"
        assert v.type == "char"
        assert v.get_definition() == "char x"

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
        #assert f.has_return_value() == False

class TestMockupWriter:
    def test_empty_templates(self):
        writer = MockupWriter()
        assert writer.get_mockup_h() == open("Test/data/gmock_test/test_empty_templates/mockup.h").read()
        assert writer.get_mockup_cc() == open("Test/data/gmock_test/test_empty_templates/mockup.cc").read()

    def test_add_header(self):
        writer = MockupWriter()
        writer.add_header("y.h")
        writer.add_header("a.h")
        writer.add_header("x.h")
        assert (
            writer.get_mockup_h()
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
        writer = MockupWriter()
        writer.add_variable("float", "y")
        writer.add_variable("unsigned int", "a")
        writer.add_variable("int", "x")

        assert (
            writer.get_mockup_h()
            == """#ifndef mockup_h
#define mockup_h

#include "gmock/gmock.h" 

extern "C" {
} /* extern "C" */

class class_mockup {

   public:
}; /* class_mockup */

extern class_mockup *mockup_global_ptr;

#define CREATE_MOCK(name)   class_mockup name; mockup_global_ptr = &name;

#endif /* mockup_h */
"""
        )

        assert (
            writer.get_mockup_cc()
            == """#include "mockup.h"

class_mockup *mockup_global_ptr = 0;

unsigned int a;
int x;
float y;

"""
        )

    def test_add_function_get(self):
        writer = MockupWriter()
        writer.add_function("int", "a_get_y2", [])
        assert writer.get_mockup_h() == open("Test/data/gmock_test/test_add_function_get/mockup.h").read()
        assert writer.get_mockup_cc() == open("Test/data/gmock_test/test_add_function_get/mockup.cc").read()

    def test_add_function_set_one_arg(self):
        writer = MockupWriter()
        writer.add_function("void", "set_some_int", [("int", "some_value")])
        assert writer.get_mockup_h() == open("Test/data/gmock_test/test_add_function_set_one_arg/mockup.h").read()
        assert writer.get_mockup_cc() == open("Test/data/gmock_test/test_add_function_set_one_arg/mockup.cc").read()

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
        assert writer.get_mockup_h() == open("Test/data/gmock_test/test_mini_c_gmock/mockup.h").read()
        assert writer.get_mockup_cc() == open("Test/data/gmock_test/test_mini_c_gmock/mockup.cc").read()