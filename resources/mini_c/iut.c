#include "iut.h"

int a(void) {
    return 1;
}

int func() {
    some_var = a() + b() + c() + d(1);
    return some_var;
}
