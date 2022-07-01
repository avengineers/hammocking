import unittest
from io import StringIO
from hammock import AUTOMOCKER


class MyTestCase(unittest.TestCase):
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
