import io
import sys
from argparse import ArgumentParser
from pathlib import Path
from typing import List


class AUTOMOCKER:
   def __init__(self, symbols: List[str], output: io.IOBase):
      self.symbols = symbols
      self.out = output
      self.config = None

   def set_config(self, configfile) -> None:
      self.config = open(configfile, 'w')

   def read(self, input: io.IOBase) -> None:
      # Fake
      self.out.write("""
   #ifdef HAM_some_var
   #ifdef MOCKUP_CODE
   int some_var;
   #endif 
   #endif // HAM_some_var

   #ifdef HAM_c
   #ifdef MOCKUP_ADDITIONAL_GLOBAL_VARIABLES
   extern int c__return;
   #endif
   #ifdef MOCKUP_CODE
   int c(void) { 
   return c__return; 
   }
   #endif
   #endif // HAM_c
   """)
      if self.config is not None:
         self.config.write('\n'.join("#define HAM_%s" % symbol for symbol in self.symbols))
      self.symbols = []

   @property
   def done(self) -> bool:
      return len(self.symbols) == 0



if __name__ == "__main__":
   arg = ArgumentParser(fromfile_prefix_chars='@')
   arg.add_argument('--symbols', '-s', help="Symbols to mock", required=True, nargs='+')
   arg.add_argument('--output', '-o', help="Output")
   arg.add_argument('--config', '-c', help="Mockup config header")
   arg.add_argument('files', nargs='+')
   args = arg.parse_args()

   mocker = AUTOMOCKER(args.symbols, open(args.output, 'w') if args.output is not None else sys.stdout)
   if args.config is not None:
      mocker.set_config(args.config)
   for input in args.files:
      if mocker.done:
         break
      mocker.read_file(input)

   if not mocker.done:
      sys.stderr.write("Automocker failed. The following symbols could not be mocked:\n" + "\n".join(mocker.symbols))
      exit(1)
   exit(0)
