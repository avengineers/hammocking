import unittest
from io import StringIO
from hammock import *


class TestSections(unittest.TestCase):
   def test_empty(self):
      """The empty mockup section"""
      sect = MOCK_SECTION("something", True)
      self.assertEqual("", str(sect), "An empty section has no content")

   def test_var(self):
      """Mock a variable"""
      sect = MOCK_SECTION("something", False)
      sect.add_var('int', 'x')
      self.assertEqual(
f"""#ifdef {sect.section_guard["code"]}
int x;
#endif
""", str(sect), "A section with variable")

   def test_var_config(self):
      """Mock a variable and config guard"""
      sect = MOCK_SECTION("something", True)
      sect.add_var('int', 'x')
      self.assertEqual(
f"""#ifdef HAM_something
#ifdef {sect.section_guard["code"]}
int x;
#endif
#endif // HAM_something
""", str(sect), "A section with variable")

   def test_void_function(self):
      """Mock a function with void return type and void parameters"""
      sect = MOCK_SECTION("something", True)
      sect.add_function('void', 'x', [])
      self.assertEqual(
f"""#ifdef HAM_something
#ifdef {sect.section_guard["code"]}
void x(void)
{{
}}
#endif
#endif // HAM_something
""", str(sect), "A section with a void function")

   def test_int_function(self):
      """Mock a function with int return type and void parameters"""
      sect = MOCK_SECTION("something", True)
      sect.add_function('int', 'x', [])
      self.assertEqual(
f"""#ifdef HAM_something
#ifdef {sect.section_guard["code"]}
int x(void)
{{
   return x__return;
}}
#endif
#endif // HAM_something
""", str(sect), "A section with a int function")

   def test_ext_var(self):
      """Mock a global variable"""
      sect = MOCK_SECTION("something", True)
      sect.add_global_var('int', 'x')
      self.assertEqual(
f"""#ifdef HAM_something
#ifdef {sect.section_guard["global_var"]}
extern int x;
#endif
#endif // HAM_something
""", str(sect), "A section with a global variable")


class TestAutomocker(unittest.TestCase):
   def test_something(self):
      out = StringIO()
      mock = AUTOMOCKER(['a'], out)
      self.assertFalse(mock.done, "Should not be done yet")
      self.assertListEqual(mock.symbols, ['a'])

      mock.read(StringIO("WTF"))
      self.assertTrue(mock.done, "Should be done now")
      self.assertListEqual(mock.symbols, [])


if __name__ == '__main__':
   unittest.main()
