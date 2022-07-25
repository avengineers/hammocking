#include <stdio.h>
#include "mockup.h"
extern "C" {
#include "iut.h"
}

int d(int a) { return 4; }

int c_gen(void) { return 5; }

int main() {
    HAM_FUNC(c).expect_calls(2);
    printf("Result 😶 mocking is: %i\n", func());
    HAM_FUNC(c).returns(3);
    printf("Result 😃 mocking is: %i\n", func());
    HAM_FUNC(c).set_generator(c_gen);
    printf("Result 💣 mocking is: %i\n", func());
}
