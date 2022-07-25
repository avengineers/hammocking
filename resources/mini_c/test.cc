#include <stdio.h>
#include "mockup.h"
extern "C" {
#include "iut.h"
}

int c_gen(void) { return 5; }

int d_gen(int arg) { return arg + 3; }

int main() {
    HAM_FUNC(c).expect_calls(testing::AnyNumber());
    HAM_FUNC(c).expect_calls(testing::Exactly(2));

    HAM_FUNC(d).expect_calls(testing::AnyNumber());   // Any times with any arguments
    HAM_FUNC(d).expect_calls(testing::AtMost(3), 1);   // Up to 3 times with argument 1
    HAM_FUNC(d).set_generator(d_gen);
    printf("Result 😶 mocking is: %i\n", func());
    HAM_FUNC(c).returns(3);
    printf("Result 😃 mocking is: %i\n", func());
    HAM_FUNC(c).set_generator(c_gen);
    printf("Result 💣 mocking is: %i\n", func());
}
