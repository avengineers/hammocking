from collections.abc import Generator
from pathlib import Path

import pytest
from clang.cindex import Cursor, CursorKind, Index, TranslationUnit

from hammocking.hammocking import ConfigReader, Function, Hammock, HammockConfig, HammockIni, HammockRunner, MockupWriter, NmWrapper, Variable

# Apply default config
ConfigReader()


def clang_parse(snippet: str) -> Cursor:
    parseOpts = {
        "path": "~.c",
        "unsaved_files": [("~.c", snippet)],
        "options": TranslationUnit.PARSE_SKIP_FUNCTION_BODIES | TranslationUnit.PARSE_INCOMPLETE,
    }
    translation_unit = Index.create(excludeDecls=True).parse(**parseOpts)

    def is_var_or_func(c: Cursor) -> bool:
        return c.kind == CursorKind.VAR_DECL or c.kind == CursorKind.FUNCTION_DECL

    return next(filter(is_var_or_func, Hammock.iter_children(translation_unit.cursor)))


class TestVariable:
    def test_simple(self):
        "Basic type"
        v = Variable(clang_parse("char x"))
        assert v.name == "x"
        assert not v.is_constant()
        assert v.get_definition() == "char x"
        assert v.initializer() == "(char)0"

    def test_array(self):
        "Array type"
        w = Variable(clang_parse("int my_array[2]"))
        assert w.name == "my_array"
        assert not w.is_constant()
        assert w.get_definition() == "int my_array[2]"
        assert w.initializer() == "{0}"

    def test_unlimited_array(self):
        "Unlimited array type"
        w = Variable(clang_parse("int my_array[]"))
        assert w.name == "my_array"
        assert not w.is_constant()
        assert w.get_definition() == "int my_array[]"
        assert w.initializer() == "{0}"  # Cannot be initialized, but hey...

    def test_constant(self):
        "Basic constant"
        w = Variable(clang_parse("const int y;"))
        assert w.name == "y"
        assert w.is_constant()
        assert w.get_definition() == "const int y"
        assert w.initializer() == "(const int)0"

    def test_constant_array(self):
        "Basic constant array"
        w = Variable(clang_parse("const int y[3];"))
        assert w.name == "y"
        assert w.is_constant()
        assert w.get_definition() == "const int y[3]"
        assert w.initializer() == "{0}"

    def test_constant_struct(self):
        "Constant structure"
        w = Variable(
            clang_parse("""
            typedef struct { int a; int b; } y_t;
            extern const y_t y;""")
        )
        assert w.name == "y"
        assert w.is_constant()
        assert w.get_definition() == "const y_t y"
        assert w.initializer() == "(const y_t){0}"

    def test_ptr_int(self):
        "Pointer to integer"
        w = Variable(clang_parse("""int *ptr;"""))
        assert w.name == "ptr"
        assert not w.is_constant()
        assert w.get_definition() == "int * ptr"
        assert w.initializer() == "(int *)0"

    def test_ptr_func(self):
        "Pointer to function"
        w = Variable(clang_parse("""int (*func)(int,int)"""))
        assert w.name == "func"
        assert not w.is_constant()
        assert w.get_definition() == "int (*func)(int,int)"
        assert w.initializer() == "(int (*)(int, int))0"

    def test_constant_ptr(self):
        "Constant pointer"
        w = Variable(clang_parse("""const int *y;"""))
        assert w.name == "y"
        assert not w.is_constant()
        assert w.get_definition() == "const int * y"
        assert w.initializer() == "(const int *)0"

    def test_ptr_to_constant(self):
        "Pointer to constant"
        w = Variable(clang_parse("""int *const y;"""))
        assert w.name == "y"
        assert w.is_constant()
        assert w.get_definition() == "int *const y"
        assert w.initializer() == "(int *const)0"

    def test_repr(self) -> None:
        assert repr(Variable(clang_parse("char x"))) == "<char x>"


class TestFunction:
    def test_void_void(self):
        "returns void / void parameters"
        f = Function(clang_parse("void func(void);"))
        assert f.name == "func"
        assert f.get_signature() == "void func()"
        assert f.get_call() == "func()"
        assert f.get_param_types() == ""
        assert not f.has_return_value()
        assert f.default_return() == "void"  # "return void" is a valid way to exit a void function

    def test_void_int(self):
        "Integer parameter"
        f = Function(clang_parse("void set(int a);"))
        assert f.name == "set"
        assert f.get_signature() == "void set(int a)"
        assert f.get_call() == "set(a)"
        assert f.get_param_types() == "int"
        assert not f.has_return_value()

    def test_int_void(self):
        "Integer return type"
        f = Function(clang_parse("int get(void);"))
        assert f.name == "get"
        assert f.get_signature() == "int get()"
        assert f.get_call() == "get()"
        assert f.get_param_types() == ""
        assert f.has_return_value()
        assert f.default_return() == "(int)0"

    def test_typedef_int(self):
        "Integer/typedef return type"
        f = Function(clang_parse("typedef int some_type; some_type get(void);"))
        assert f.name == "get"
        assert f.get_signature() == "some_type get()"
        assert f.get_call() == "get()"
        assert f.get_param_types() == ""
        assert f.has_return_value()
        assert f.default_return() == "(some_type)0"

    def test_void_int_double(self):
        "Integer and double parameters"
        f = Function(clang_parse("void set(int a, double b);"))
        assert f.name == "set"
        assert f.get_signature() == "void set(int a, double b)"
        assert f.get_call() == "set(a, b)"
        assert f.get_param_types() == "int, double"
        assert not f.has_return_value()

    def test_function_with_unnamed_arguments(self):
        "Unnamed arguments"
        f = Function(clang_parse("float my_func(float, float);"))
        assert f.name == "my_func"
        assert f.get_signature() == "float my_func(float unnamed1, float unnamed2)"
        assert f.get_call() == "my_func(unnamed1, unnamed2)"
        assert f.get_param_types() == "float, float"
        assert f.default_return() == "(float)0"

    def test_variadic_function(self):
        "Variadic function"
        f = Function(clang_parse("int printf_func(const char* fmt, ...);"))
        assert f.name == "printf_func"
        assert f.get_signature() == "int printf_func(const char * fmt, ...)"
        assert f.get_call() == "printf_func(fmt)"  # TODO
        assert f.get_param_types() == "const char *"  # ?

    def test_array_param(self):
        "Takes an array parameter"
        f = Function(clang_parse("void x(int arg[]);"))
        assert f.name == "x"
        assert f.get_signature() == "void x(int arg[])"
        assert f.get_call() == "x(arg)"
        assert f.get_param_types() == "int[]"

    def test_funcptr_param(self):
        "Takes a function-pointer parameter"
        f = Function(clang_parse("void x(int (*cb)(void));"))
        assert f.name == "x"
        assert f.get_signature() == "void x(int (*cb)())"
        assert f.get_call() == "x(cb)"
        assert f.get_param_types() == "int (*)(void)"

    def test_blank_func(self):
        "Blank (nonproto) function"
        f = Function(clang_parse("void x();"))
        assert f.name == "x"
        assert f.get_signature() == "void x()"
        assert f.get_call() == "x()"
        assert f.get_param_types() == ""

    def test_const_ptr_return(self):
        "const-Pointer const-value return type"
        f = Function(clang_parse("const char* const x(void);"))
        assert f.name == "x"
        assert f.return_type == "const char *const"
        assert f.get_signature() == "const char *const x()"
        assert f.get_call() == "x()"
        assert f.get_param_types() == ""
        assert f.default_return() == "(const char *const)0"

    def test_struct_param_func(self):
        "Structure type parameter"
        f = Function(
            clang_parse("""
            typedef struct { int a; int b; } x_t;
            extern void f(x_t x);""")
        )
        assert f.name == "f"
        assert f.return_type == "void"
        assert f.get_signature() == "void f(x_t x)"
        assert f.get_call() == "f(x)"
        assert f.get_param_types() == "x_t"
        assert not f.has_return_value()

    def test_struct_type_return_func(self):
        "Structure/typedef return type"
        f = Function(
            clang_parse("""
            typedef struct { int a; int b; } x_t;
            extern x_t f();""")
        )
        assert f.name == "f"
        assert f.return_type == "x_t"
        assert f.get_signature() == "x_t f()"
        assert f.get_call() == "f()"
        assert f.get_param_types() == ""
        assert f.default_return() == "(x_t){0}"

    def test_named_struct_return_func(self):
        "Structure return type"
        f = Function(
            clang_parse("""
            struct x_s { int a; int b; };
            struct x_s f();
        """)
        )
        assert f.name == "f"
        assert f.return_type == "struct x_s"
        assert f.get_signature() == "struct x_s f()"
        assert f.get_call() == "f()"
        assert f.get_param_types() == ""
        assert f.default_return() == "(struct x_s){0}"

    def test_enum_param(self):
        "enum/typedef parameter"
        f = Function(
            clang_parse("""
            typedef enum { FIRST; SECOND } e_t;
            void f(e_t param);
        """)
        )
        assert f.name == "f"
        assert f.return_type == "void"
        assert f.get_signature() == "void f(e_t param)"
        assert f.get_call() == "f(param)"
        assert f.get_param_types() == "e_t"

    def test_named_enum_param(self):
        "named enum parameter"
        f = Function(
            clang_parse("""
            enum some_enum { FIRST; SECOND };
            void f(enum some_enum param);
        """)
        )
        assert f.name == "f"
        assert f.return_type == "void"
        assert f.get_signature() == "void f(enum some_enum param)"
        assert f.get_call() == "f(param)"
        assert f.get_param_types() == "enum some_enum"

    def test_named_enum_return(self):
        "named enum return"
        f = Function(
            clang_parse("""
            enum some_enum { FIRST; SECOND };
            enum some_enum get_enum(void);
        """)
        )
        assert f.name == "get_enum"
        assert f.return_type == "enum some_enum"
        assert f.get_signature() == "enum some_enum get_enum()"
        assert f.get_call() == "get_enum()"
        assert f.default_return() == "(enum some_enum)0"

    def test_repr(self) -> None:
        assert repr(Function(clang_parse("void foo();"))) == "<void foo ()>"


class TestMockupWriter:
    def test_empty_templates(self):
        writer = MockupWriter()
        assert writer.get_mockup("mockup.h") == open("tests/data/gmock_test/test_empty_templates/mockup.h").read()
        assert writer.get_mockup("mockup.cc") == open("tests/data/gmock_test/test_empty_templates/mockup.cc").read()

    @pytest.mark.parametrize(
        "filename,suffix,expected_name",
        [("my_file.c.j2", None, "my_file.c"), ("my_file.cpp.j2", "_new", "my_file_new.cpp")],
    )
    def test_create_out_filename(self, filename, suffix, expected_name):
        """@validates Req0001"""
        writer = MockupWriter(suffix=suffix)
        assert writer.create_out_filename(filename) == expected_name

    def test_add_header(self):
        writer = MockupWriter()
        writer.add_header("y.h")
        writer.add_header("a.h")
        writer.add_header("x.h")
        assert (
            writer.get_mockup("mockup.h")
            == """#ifndef mockup_h
#define mockup_h

#include "gmock/gmock.h"

extern "C" {
#include "a.h"
#include "x.h"
#include "y.h"
} /* extern "C" */

class class_mockup;
typedef class_mockup* mock_ptr_t;
extern mock_ptr_t mockup_global_ptr;

class class_mockup {

 public:
   class_mockup()  { mockup_global_ptr = this; }
   ~class_mockup() { mockup_global_ptr = nullptr; }
}; /* class_mockup */

/* Version A: Create a local object that is destroyed when out of scope */
#define CREATE_MOCK(name)   class_mockup name

/* Version B: Allocate an object that will be only explicitly deallocated */
#define CREATE_PERSISTENT_MOCK()     new class_mockup
#define DESTROY_PERSISTENT_MOCK()    {if(mockup_global_ptr) delete mockup_global_ptr;}

#endif /* mockup_h */
"""
        )

    def test_add_variable(self):
        writer = MockupWriter(suffix="_new")
        writer.add_variable(clang_parse("float y"))
        writer.add_variable(clang_parse("unsigned int a"))
        writer.add_variable(clang_parse("int x"))

        assert (
            writer.get_mockup("mockup.h")
            == """#ifndef mockup_new_h
#define mockup_new_h

#include "gmock/gmock.h"

extern "C" {
} /* extern "C" */

class class_mockup;
typedef class_mockup* mock_ptr_t;
extern mock_ptr_t mockup_global_ptr;

class class_mockup {

 public:
   class_mockup()  { mockup_global_ptr = this; }
   ~class_mockup() { mockup_global_ptr = nullptr; }
}; /* class_mockup */

/* Version A: Create a local object that is destroyed when out of scope */
#define CREATE_MOCK(name)   class_mockup name

/* Version B: Allocate an object that will be only explicitly deallocated */
#define CREATE_PERSISTENT_MOCK()     new class_mockup
#define DESTROY_PERSISTENT_MOCK()    {if(mockup_global_ptr) delete mockup_global_ptr;}

#endif /* mockup_new_h */
"""
        )

        assert (
            writer.get_mockup("mockup.cc")
            == """#include "mockup_new.h"

mock_ptr_t mockup_global_ptr = nullptr;

unsigned int a;
int x;
float y;

extern "C" {
}
"""
        )

    def test_add_function_get(self):
        writer = MockupWriter()
        writer.add_function(clang_parse("int a_get_y2();"))
        assert writer.get_mockup("mockup.h") == open("tests/data/gmock_test/test_add_function_get/mockup.h").read()
        assert writer.get_mockup("mockup.cc") == open("tests/data/gmock_test/test_add_function_get/mockup.cc").read()

    def test_add_function_set_one_arg(self):
        writer = MockupWriter()
        writer.add_function(clang_parse("void set_some_int(int some_value);"))
        assert writer.get_mockup("mockup.h") == open("tests/data/gmock_test/test_add_function_set_one_arg/mockup.h").read()
        assert writer.get_mockup("mockup.cc") == open("tests/data/gmock_test/test_add_function_set_one_arg/mockup.cc").read()

    def test_add_function_with_unnamed_arg(self):
        writer = MockupWriter()
        writer.add_function(clang_parse("float my_func(float);"))
        assert writer.get_mockup("mockup.h") == open("tests/data/gmock_test/test_add_function_with_unnamed_arg/mockup.h").read()
        assert writer.get_mockup("mockup.cc") == open("tests/data/gmock_test/test_add_function_with_unnamed_arg/mockup.cc").read()

    def test_mini_c_gmock(self):
        writer = MockupWriter()
        writer.add_header("a.h")
        writer.add_header("c.h")
        writer.add_variable(clang_parse("extern int a_y1"))
        writer.add_variable(clang_parse("extern int c_u1"))
        writer.add_variable(clang_parse("extern a_y4_t a_y4"))
        writer.add_variable(clang_parse("extern const int const_a;"))
        writer.add_variable(clang_parse("extern const int const_array[3];"))
        writer.add_function(clang_parse("int  a_get_y2();"))
        writer.add_function(clang_parse("int  a_get_y3_and_set_u5(int u5);"))
        writer.add_function(clang_parse("a_y5_t a_get_y5();"))
        writer.add_function(clang_parse("void a_get_y6(int* y6);"))
        writer.add_function(clang_parse("int  c_get_y3_and_set_u5(int u5);"))
        writer.add_function(clang_parse("void c_set_u2(int u2);"))
        writer.add_function(clang_parse("void c_set_u3_and_u4(int u3, int u4);"))
        writer.add_function(clang_parse("void c_set_u6(c_u6_t u6);"))
        assert writer.get_mockup("mockup.h") == open("tests/data/gmock_test/test_mini_c_gmock/mockup.h").read()
        assert writer.get_mockup("mockup.cc") == open("tests/data/gmock_test/test_mini_c_gmock/mockup.cc").read()

    def test_languagemode(self):
        writer = MockupWriter()
        assert writer.default_language_mode() == "c++"
        writer.set_mockup_style("plain_c")
        assert writer.default_language_mode() == "c"


class TestHammock:
    def test_variable(self):
        """Mock a variable"""
        hammock = Hammock({"a"})

        assert hammock.symbols == {"a"}
        assert not hammock.done, "Should not be done yet"

        hammock.parse("extern int a;")

        assert hammock.symbols == set()
        assert len(hammock.writer.variables) == 1, "Mockup shall have a variable"
        assert hammock.writer.variables[0].get_definition() == "int a", "Variable shall be created in the mockup"
        assert hammock.done, "Should be done now"

    def test_struct_variable(self):
        """Mock a struct variable"""
        hammock = Hammock({"x"})

        assert hammock.symbols == {"x"}
        assert not hammock.done, "Should not be done yet"

        hammock.parse("""typedef struct { int a; int b; } struct_t;
                   extern struct_t x;""")

        assert hammock.symbols == set()
        assert len(hammock.writer.variables) == 1, "Mockup shall have a variable"
        assert hammock.writer.variables[0].get_definition() == "struct_t x", "Variable shall be created in the mockup"
        assert hammock.done, "Should be done now"

    def test_const_struct_variable(self):
        """Mock a constant struct variable"""
        hammock = Hammock({"cx"})

        assert hammock.symbols == {"cx"}
        assert not hammock.done, "Should not be done yet"

        hammock.parse("""typedef struct { int a; int b; } struct_t;
                   extern const struct_t cx;""")

        assert hammock.symbols == set()
        assert len(hammock.writer.variables) == 1, "Mockup shall have a variable"
        assert hammock.writer.variables[0].get_definition() == "const struct_t cx", "Variable shall be created in the mockup"
        assert hammock.writer.variables[0].initializer() == "(const struct_t){0}", "Constant shall be initialized with struct initializer"
        assert hammock.done, "Should be done now"

    def test_void_func(self):
        """Mock a void(void) function"""
        hammock = Hammock({"x"})
        hammock.parse("extern void x(void);")

        assert len(hammock.writer.functions) == 1, "Mockup shall have a function"
        assert hammock.writer.functions[0].get_signature() == "void x()", "Function shall be created in the mockup"
        assert hammock.done, "Should be done now"

    def test_int_int_func(self):
        """Mock a int(int) function"""
        hammock = Hammock({"xxx"})
        hammock.parse("extern int xxx(int var1);")

        assert hammock.done, "Should be done now"
        assert len(hammock.writer.functions) == 1, "Mockup shall have a function"
        assert hammock.writer.functions[0].get_signature() == "int xxx(int var1)", "Function shall be created in the mockup"

    def test_variable_with_config_guard(self):
        """Mock a variable with config guard"""
        hammock = Hammock({"b"})
        hammock.parse(
            """#ifdef SOME_CONFIG
extern int b;
#endif
"""
        )

        assert not hammock.done, "Should not be done due to missing definition"

        hammock = Hammock({"b"}, ["-DSOME_CONFIG"])
        hammock.parse(
            """#ifdef SOME_CONFIG
extern int b;
#endif
"""
        )

        assert hammock.done, "Should be done now"
        assert len(hammock.writer.variables) == 1, "Mockup shall have a variable"
        assert hammock.writer.variables[0].get_definition() == "int b", "Variable shall be created in the mockup"

    def test_variable_and_function_with_config_guards(self):
        """Mock a variable and a function with different config guards"""
        hammock = Hammock({"b", "foo"}, ["-DSOME_CONFIG", "-DSOME_OTHER_CONFIG=2"])
        hammock.parse(
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

        assert hammock.done, "Should be done now"
        assert len(hammock.writer.variables) == 1, "Mockup shall have a variable"
        assert hammock.writer.variables[0].get_definition() == "int b", "Variable shall be created in the mockup"
        assert len(hammock.writer.functions) == 1, "Mockup shall have a function"
        assert hammock.writer.functions[0].get_signature() == "void foo()", "Function shall be created in the mockup"

    def test_extern_c_variable(self):
        """Mock a variable that is inside an "extern C" section"""
        hammock = Hammock({"foo"})
        hammock.parse("""
extern "C" {
extern void foo();
}
""")
        assert hammock.done, "Should be done now"
        assert len(hammock.writer.functions) == 1, "Mockup shall have a function"
        assert hammock.writer.functions[0].get_signature() == "void foo()", "Function shall be created in the mockup"

    def test_variable_array(self):
        """Mock an int array"""
        hammock = Hammock({"my_array"})
        hammock.parse("extern int my_array[2];")
        assert hammock.done, "Should be done now"
        assert len(hammock.writer.variables) == 1, "Mockup shall have a variable"
        assert hammock.writer.variables[0].get_definition() == "int my_array[2]", "Variable shall be created in the mockup"

    def test_langmode_auto(self):
        """Read as c++ compiler determined from output style"""
        hammock = Hammock({"bool_status"})
        hammock.parse(Path("tests/data/mini_c++_test/use_bool.c"))
        assert hammock.done, "Should be done now"
        assert len(hammock.writer.functions) == 1, "Mockup shall have a function"
        assert hammock.writer.functions[0].get_signature() == "bool bool_status()", "Function shall be created with bool type"

    def test_langmode_override(self):
        """Read as c compiler"""
        hammock = Hammock({"bool_status"}, ["-xc"])
        hammock.parse(Path("tests/data/mini_c++_test/use_bool.c"))
        assert hammock.done, "Should be done now"
        assert len(hammock.writer.functions) == 1, "Mockup shall have a function"
        assert hammock.writer.functions[0].get_signature() == "_Bool bool_status()", "Function shall be created with C99 bool type"

    def test_variadic_function(self):
        """Mock a variadic function"""
        hammock = Hammock({"printf"})
        hammock.parse("extern int printf(const char * format, ...);")
        assert hammock.done, "Should be done now"
        assert len(hammock.writer.functions) == 1, "Mockup shall have a function"
        assert hammock.writer.functions[0].get_signature() == "int printf(const char * format, ...)", "Function shall be created in the mockup"

    def test_ignore(self, tmp_path: Path) -> None:
        """Ignore symbols outside the project root directory"""
        c_file = tmp_path / "test.c"
        # copy mini_c_test/b.c to tmp path
        c_file.write_text(Path("tests/data/mini_c_test/b.c").read_text())
        # check without exclude method
        hammock = Hammock(symbols={"a_get_y2", "a_y1"}, cmd_args=["-Itests/data/mini_c_test/includes", "-x", "c"])
        hammock.parse(c_file)
        assert hammock.done
        assert len(hammock.writer.variables) == 1, "Mockup shall have a variable"
        assert len(hammock.writer.functions) == 1, "Mockup shall have a function"

        # check with exclude method
        hammock = Hammock(symbols={"a_get_y2", "a_y1"}, cmd_args=["-Itests/data/mini_c_test/includes", "-x", "c"], ignore_symbols_outside_project=True, project_root_dir=Path("some_dir"))
        hammock.parse(c_file)
        assert hammock.done
        assert len(hammock.writer.variables) == 0, "Mockup shall not have a variable"
        assert len(hammock.writer.functions) == 0, "Mockup shall not have a function"

    def test_read_stops_early_when_all_symbols_found(self, tmp_path: Path) -> None:
        """read() shall stop after all symbols are found — second source must not be parsed."""
        c_file = tmp_path / "test.c"
        c_file.write_text(Path("tests/data/mini_c_test/b.c").read_text())
        unreachable = tmp_path / "unreachable.c"
        unreachable.write_text("/* this file must not be parsed */")
        hammock = Hammock(symbols={"a_y1"}, cmd_args=["-Itests/data/mini_c_test/includes", "-x", "c"])
        hammock.read([c_file, unreachable])
        assert hammock.done
        assert len(hammock.writer.variables) == 1

    def test_parse_skips_symbol_in_excluded_path(self) -> None:
        """Symbols found in an excluded path must be silently skipped."""
        hammock = Hammock(symbols={"a_get_y2", "a_y1"}, cmd_args=["-Itests/data/mini_c_test/includes", "-x", "c"])
        hammock.add_excludes(["tests/data/mini_c_test/includes"])
        hammock.parse(Path("tests/data/mini_c_test/b.c"))
        assert hammock.done
        assert len(hammock.writer.variables) == 0
        assert len(hammock.writer.functions) == 0


class TestConfigReader:
    def test_parses_ignore_symbols_outside_project_true(self, tmp_path: Path) -> None:
        ini = tmp_path / "hammock.ini"
        ini.write_text("[hammocking]\nignore_symbols_outside_project=true\n")
        result = ConfigReader(ini).read()
        assert result.ignore_symbols_outside_project is True

    def test_parses_ignore_symbols_outside_project_false(self, tmp_path: Path) -> None:
        ini = tmp_path / "hammock.ini"
        ini.write_text("[hammocking]\nignore_symbols_outside_project=false\n")
        result = ConfigReader(ini).read()
        assert result.ignore_symbols_outside_project is False

    def test_merge_uses_ini_value_when_cli_not_set(self, tmp_path: Path) -> None:
        """When CLI did not set the flag (None), the INI value shall win after merge."""
        ini = tmp_path / "hammock.ini"
        ini.write_text("[hammocking]\nignore_symbols_outside_project=true\n")
        config = HammockConfig(sources=[], outdir=tmp_path, ignore_symbols_outside_project=None)
        hammock_ini = ConfigReader(ini).read()
        merged = config.merge(hammock_ini)
        assert merged.ignore_symbols_outside_project is True

    def test_default_ini_enables_ignore_symbols_outside_project(self) -> None:
        """The package default hammocking.ini shall set ignore_symbols_outside_project=true."""
        result = ConfigReader().read()
        assert result.ignore_symbols_outside_project is True

    def test_returns_empty_ini_when_config_file_does_not_exist(self, tmp_path: Path) -> None:
        """ConfigReader with a non-existent file shall return a default HammockIni without crashing."""
        reader = ConfigReader(tmp_path / "nonexistent.ini")
        assert not hasattr(reader, "hammock_ini")

    def test_parses_all_ini_keys(self, tmp_path: Path) -> None:
        """All supported INI keys are parsed correctly by _scan()."""
        ini = tmp_path / "hammock.ini"
        ini.write_text(
            "[hammocking]\n"
            "clang_lib_file=libclang.so\n"
            "clang_lib_path=/usr/lib/llvm\n"
            "nm=llvm-nm\n"
            "include_pattern=^my_prefix\n"
            "exclude_pattern=^_\n"
            "ignore_symbols_outside_project=true\n"
        )
        result = ConfigReader(ini).read()
        assert result.clang_lib_file == "libclang.so"
        assert result.clang_lib_path == "/usr/lib/llvm"
        assert result.nm_path == "llvm-nm"
        assert result.include_pattern == "^my_prefix"
        assert result.exclude_pattern == "^_"
        assert result.ignore_symbols_outside_project is True

    def test_merge_overlays_non_none_values(self) -> None:
        """HammockIni.merge() shall overlay non-None values from override, keeping defaults for None values."""
        default = HammockIni(exclude_pattern="^(_|llvm_)", exclude_paths=["/usr/include"])
        override = HammockIni(ignore_symbols_outside_project=True)
        merged = default.merge(override)
        assert merged.exclude_pattern == "^(_|llvm_)"
        assert merged.exclude_paths == ["/usr/include"]
        assert merged.ignore_symbols_outside_project is True

    def test_merge_override_replaces_default(self) -> None:
        """HammockIni.merge() shall replace default values with override values when both are set."""
        default = HammockIni(exclude_pattern="^default")
        override = HammockIni(exclude_pattern="^override")
        merged = default.merge(override)
        assert merged.exclude_pattern == "^override"


class TestHammockRunner:
    def test_init(self, tmp_path: Path) -> None:
        hammock_ini = tmp_path / "hammock.ini"
        hammock_ini.write_text("""
[hammocking]
# nm=nm
# include_pattern=....
exclude_pattern=^(_|llvm_|memcmp|memcpy|memset|bzero|exp|strlen)
[hammocking.darwin]
ignore_path=some_include_dir
[hammocking.linux]
ignore_path=some_include_dir
clang_lib_file=libclang.so
[hammocking.win32]
ignore_path=some_include_dir
""")
        hammock_config = HammockConfig(
            sources=[
                Path("tests/data/mini_c_test/b.c"),
            ],
            outdir=Path("tests/data/mini_c_test/build"),
            symbols={"a_y1", "a_get_y2"},
            cmd_args=["-IC:/D/Git/avengineers/hammocking/tests/data/mini_c_test/includes", "-x", "c"],
            exclude_pattern=r"^(_|llvm_|memcmp|memcpy|memset)",
            config=hammock_ini,
        )
        hammock = HammockRunner(hammock_config)
        assert hammock.hammock_config.exclude_paths == ["some_include_dir"]
        assert hammock.hammock_config.exclude_pattern == r"^(_|llvm_|memcmp|memcpy|memset)"
        assert hammock.hammock_config.ignore_symbols_outside_project is True

    def test_ignore_symbols_outside_project_defaults_to_true(self, tmp_path: Path) -> None:
        """When ignore_symbols_outside_project is not set, HammockRunner shall default to True."""
        config = HammockConfig(sources=[], outdir=tmp_path)
        runner = HammockRunner(config)
        assert runner.hammock_config.ignore_symbols_outside_project is True

    def test_explicit_false_overrides_ini_true(self, tmp_path: Path) -> None:
        """Explicitly setting False in HammockConfig must not be overridden by INI or HammockRunner default."""
        hammock_ini = tmp_path / "hammock.ini"
        hammock_ini.write_text("[hammocking]\nignore_symbols_outside_project=true\n")
        config = HammockConfig(sources=[], outdir=tmp_path, config=hammock_ini, ignore_symbols_outside_project=False)
        runner = HammockRunner(config)
        assert runner.hammock_config.ignore_symbols_outside_project is False

    def test_project_config_preserves_default_exclude_pattern(self, tmp_path: Path) -> None:
        """A project config that only sets one field must not lose the default exclude_pattern."""
        project_ini = tmp_path / "hammock.ini"
        project_ini.write_text("[hammocking]\nignore_symbols_outside_project=true\n")
        config = HammockConfig(sources=[], outdir=tmp_path, config=project_ini)
        runner = HammockRunner(config)
        assert runner.hammock_config.exclude_pattern is not None, "Default exclude_pattern lost when project config was provided"
        assert runner.hammock_config.exclude_pattern == "^(_|llvm_|memcpy|memmove|memset|memcmp|bzero|strlen)"
        assert runner.hammock_config.ignore_symbols_outside_project is True

    def test_run(self, tmp_path: Path) -> None:
        hammock_config = HammockConfig(
            sources=[
                Path("tests/data/mini_c_test/b.c"),
            ],
            outdir=tmp_path,
            symbols={"a_y1", "a_get_y2"},
            cmd_args=["-Itests/data/mini_c_test/includes", "-x", "c"],
        )
        hammock = HammockRunner(hammock_config)
        assert hammock.run() == 0

    def test_update_system_sets_nm_path(self, tmp_path: Path) -> None:
        """update_system() shall apply nm_path to NmWrapper."""
        original = NmWrapper.nmpath
        config = HammockConfig(sources=[], outdir=tmp_path, nm_path="custom-nm")
        HammockRunner(config)
        assert NmWrapper.nmpath == "custom-nm"
        NmWrapper.nmpath = original

    def test_update_system_sets_include_pattern(self, tmp_path: Path) -> None:
        """update_system() shall apply include_pattern to NmWrapper."""
        original = NmWrapper.includepattern
        config = HammockConfig(sources=[], outdir=tmp_path, include_pattern="^my_prefix")
        HammockRunner(config)
        assert NmWrapper.includepattern is not None
        NmWrapper.includepattern = original

    def test_run_excludes_symbols_in_exclude_list(self, tmp_path: Path) -> None:
        """Symbols in the exclude list shall be removed before mocking."""
        config = HammockConfig(
            sources=[Path("tests/data/mini_c_test/b.c")],
            outdir=tmp_path,
            symbols={"a_y1", "a_get_y2"},
            exclude=["a_y1"],
            cmd_args=["-Itests/data/mini_c_test/includes", "-x", "c"],
        )
        runner = HammockRunner(config)
        result = runner.run()
        assert result == 0
        assert runner.hammock is not None
        assert len(runner.hammock.writer.variables) == 0, "a_y1 (variable) was excluded, must not be mocked"
        assert len(runner.hammock.writer.functions) == 1, "a_get_y2 (function) was not excluded, must be mocked"

    def test_run_returns_1_when_symbol_cannot_be_mocked(self, tmp_path: Path) -> None:
        """run() shall return 1 when not all symbols could be found and mocked."""
        config = HammockConfig(
            sources=[Path("tests/data/mini_c_test/b.c")],
            outdir=tmp_path,
            symbols={"nonexistent_symbol_xyz"},
            cmd_args=["-Itests/data/mini_c_test/includes", "-x", "c"],
        )
        runner = HammockRunner(config)
        result = runner.run()
        assert result == 1
        assert "nonexistent_symbol_xyz" in runner.get_symbols()

    def test_get_symbols_returns_empty_before_run(self, tmp_path: Path) -> None:
        """get_symbols() shall return an empty list before run() is called."""
        config = HammockConfig(sources=[], outdir=tmp_path)
        runner = HammockRunner(config)
        assert runner.get_symbols() == []


class TestNmWrapperMockIt:
    """Tests for NmWrapper.mock_it() symbol filtering logic."""

    @pytest.fixture(autouse=True)
    def _save_and_restore_nm_state(self) -> Generator[None, None, None]:
        """Save and restore NmWrapper class-level state around each test."""
        original_exclude = NmWrapper.excludepattern
        original_include = NmWrapper.includepattern
        yield
        NmWrapper.excludepattern = original_exclude
        NmWrapper.includepattern = original_include

    def test_accepts_normal_undefined_symbol(self) -> None:
        """A regular undefined symbol shall be returned by mock_it()."""
        NmWrapper.set_exclude_pattern("^__gcov")
        assert NmWrapper.mock_it("         U my_function") == "my_function"

    def test_rejects_excluded_symbol(self) -> None:
        """A symbol matching exclude_pattern shall be filtered out."""
        NmWrapper.set_exclude_pattern("^__gcov")
        assert NmWrapper.mock_it("         U __gcov_merge_add") is None

    def test_rejects_non_undefined_symbol(self) -> None:
        """Lines that are not undefined symbols (no 'U') shall be ignored."""
        assert NmWrapper.mock_it("00000000 T my_function") is None

    def test_include_pattern_overrides_exclude(self) -> None:
        """include_pattern shall take precedence over exclude_pattern."""
        NmWrapper.set_exclude_pattern("^mem")
        NmWrapper.set_include_pattern("^memcpy$")
        assert NmWrapper.mock_it("         U memcpy") == "memcpy"
        assert NmWrapper.mock_it("         U memset") is None

    @pytest.mark.parametrize("symbol", ["memcpy", "memmove", "memset", "memcmp", "bzero", "strlen"])
    def test_default_exclude_pattern_filters_compiler_intrinsics(self, symbol: str) -> None:
        """The default exclude_pattern from hammocking.ini shall filter common compiler-generated symbols."""
        default_ini = ConfigReader().read()
        assert default_ini.exclude_pattern is not None
        NmWrapper.set_exclude_pattern(default_ini.exclude_pattern)
        assert NmWrapper.mock_it(f"         U {symbol}") is None, f"{symbol} should be excluded by default pattern"

    @pytest.mark.parametrize("symbol", ["my_app_function", "sensor_read", "can_transmit"])
    def test_default_exclude_pattern_allows_application_symbols(self, symbol: str) -> None:
        """The default exclude_pattern shall not filter regular application symbols."""
        default_ini = ConfigReader().read()
        assert default_ini.exclude_pattern is not None
        NmWrapper.set_exclude_pattern(default_ini.exclude_pattern)
        assert NmWrapper.mock_it(f"         U {symbol}") == symbol, f"{symbol} should not be excluded"
