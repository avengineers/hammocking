#pragma once

#include <stdio.h>

template <class R>
class StaticReturnGenerator {
public:
    R ret_val;
    StaticReturnGenerator() {
        ret_val = (R)0;
    }
    R generate(void) {
        return ret_val;
    }    
};

template <class R>
class FuncMockup{
public:
    FuncMockup() {
        this->generator = StaticReturnGenerator<R>();
    }
    R run(void) {
        this->calls++;
        return this->generator.generate();
    }
    void returns(R value) {
        this->generator.ret_val = value;
    }
    void expect_calls(int n) {
        this->expected = n;
    }
    ~FuncMockup() {
        if ((this->expected != -1) &&
            (this->calls != this->expected)) {
            printf("Expectation did not match! Expected: %u calls; actual: %u calls\n",
                this->expected, this->calls);
        }
    }
private:
    StaticReturnGenerator<R> generator;
    int expected = -1;
    int calls = 0;
};

#define HAM_FUNC(f) f##_mockup
