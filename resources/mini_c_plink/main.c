#include "main.h"

int a(void) {
    return 1;
}

int main() {
    some_var = a() + b() + c() + d(1);
    return some_var;
}

#ifndef CFG_A
compile-error
#endif /* CFG_A */
