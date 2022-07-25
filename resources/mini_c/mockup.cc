#include "hammock.hh"

Func0Mockup<int> c_mockup;
Func1Mockup<int, int> d_mockup;

extern "C" int c(void) {
    return c_mockup.run();
}

extern "C" int d(int arg) {
    return d_mockup.run(arg);
}

extern "C" { int some_var; }
