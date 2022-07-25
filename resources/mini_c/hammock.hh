#pragma once

#include <stdio.h>
#include <stdlib.h>


template <class R>
class FuncMockup{
public:
    FuncMockup() {
        this->generator = NULL;
        this->default_return = (R)0;
    }
    R run(void) {
        this->calls++;
        if (this->generator)
            return this->generator();
        else
            return this->default_return;
    }
    void returns(R value) {
        this->default_return = value;
    }
    void set_generator(R(*gen)(void)) {
        this->generator = gen;
    }
    void expect_calls(int n) {
        this->expected = n;
    }
    ~FuncMockup() {
        if ((this->expected != -1) &&
            (this->calls != this->expected)) {
            printf("Expectation did not match! Expected: %u calls; actual: %u calls\n",
                this->expected, this->calls);
            exit(1);
        }
    }
private:
    R default_return;
    R(*generator)(void);
    int expected = -1;
    int calls = 0;
};

#define HAM_FUNC(f) f##_mockup
