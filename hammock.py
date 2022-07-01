from argparse import ArgumentParser

if __name__ == "__main__":
   arg = ArgumentParser()
   arg.add_argument('--symbols', '-s', help="Symbols to mock", required=True, nargs='+')
   arg.add_argument('--output', '-o', help="Output")
   arg.add_argument('files', nargs='+')
   args = arg.parse_args()

   # Fake
   with open(args.output, 'w') as f:
      f.write("""
      #ifdef MOCKUP_ADDITIONAL_GLOBAL_VARIABLES
      extern int c__return;
      #endif
      #ifdef MOCKUP_CODE
      int c(void) { 
      return c__return; 
      }
      #endif
      """)
