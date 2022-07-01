#include <stdio.h>
#include "main.h"

int a(void) {
    return 1;
}

int main() {
    int result = a() + b() + c();
    printf("Result is: %i\n", result);
}