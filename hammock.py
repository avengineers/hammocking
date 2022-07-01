from argparse import ArgumentParser
from pathlib import Path

if __name__ == "__main__":
   arg = ArgumentParser(fromfile_prefix_chars='@')
   arg.add_argument('--symbols', '-s', help="Symbols to mock", required=True, nargs='+')
   arg.add_argument('--output', '-o', help="Output")
   arg.add_argument('--config', '-c', help="Mockup config header")
   arg.add_argument('files', nargs='+')
   args = arg.parse_args()

   # Fake
   Path(args.output).write_text("""
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
   Path(args.config).write_text('\n'.join("#define HAM_%s" % symbol for symbol in args.symbols))
