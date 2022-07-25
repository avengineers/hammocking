#pragma once

#include <stdio.h>
#include <stdlib.h>
#include <iostream>
#include <sstream>
#include "include/cardinality.h"
#include "include/argcheck.h"

template <typename R>
class Func0Mockup {
public:
    Func0Mockup() {
        this->generator = nullptr;
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
    void expect_calls(::testing::Cardinality c) {
        this->expected = c;
    }
    ~Func0Mockup() {
        if (!this->expected.IsSatisfiedByCallCount(this->calls))
        {
            std::stringstream ss;
            ss << "Expectation did not match! Expected: ";
            this->expected.DescribeTo(&ss);
            std::cerr << ss.str() << " actual: " << this->calls << " calls\n";
            exit(1);
        }
    }
private:
    R default_return;
    R(*generator)(void);
    ::testing::Cardinality expected = ::testing::AnyNumber();
    int calls = 0;
};

template <typename R, typename T>
class Func1Mockup {
public:
    Func1Mockup() {
        this->generator = nullptr;
        this->default_return = (R)0;
        this->expected = ::testing::AnyNumber();
        this->expected_arg = ::testing::Expected_arg<T>();
    }
    R run(T arg1) {
        this->calls++;
        if (this->expected_arg != arg1) {
            std::cerr << "Argument #1 mismatch! Expected: " << this->expected_arg.Describe()
                << " actual: " << arg1 << "\n";
            exit(1);
        }
        if (this->generator)
            return this->generator(arg1);
        else
            return this->default_return;
    }
    void returns(R value) {
        this->default_return = value;
    }
    void set_generator(R(*gen)(T arg1)) {
        this->generator = gen;
    }
    void expect_calls(::testing::Cardinality c) {
        this->expected = c;
    }
    void expect_calls(::testing::Cardinality c, T arg) {
        this->expected = c;
        this->expected_arg = testing::Expected_arg<T>(arg);
    }
    ~Func1Mockup() {
        if (!this->expected.IsSatisfiedByCallCount(this->calls))
        {
            std::cerr << "Expectation did not match! Expected: " << this->expected.Describe()
                 << " actual: " << this->calls << " calls\n";
            exit(1);
        }
    }
private:
    R default_return;
    R(*generator)(T arg);
    ::testing::Cardinality expected;
    ::testing::Expected_arg<T> expected_arg;
    int calls = 0;
};
#define HAM_FUNC(f) f##_mockup
