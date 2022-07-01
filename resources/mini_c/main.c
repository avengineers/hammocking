#include <stdio.h>
#include "main.h"

int a(void) {
    return 1;
}

int main() {
    some_var = a() + b() + c();
    printf("Result is: %i\n", some_var);
}
