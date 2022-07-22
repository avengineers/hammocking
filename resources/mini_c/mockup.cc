#include "hammock.hh"

FuncMockup<int> c_mockup;

extern "C" int c(void) {
    return c_mockup.run();
}

extern "C" { int some_var; }
