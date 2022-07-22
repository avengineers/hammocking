#include <stdio.h>
#include "mockup.h"
extern "C" {
#include "iut.h"
}

int d(int a) { return 4; }

int main() {
    HAM_FUNC(c).returns(3);
    printf("Result is: %i\n", func());
}
