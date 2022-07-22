#pragma once

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
        return this->generator.generate();
    }
    void returns(R value) {
        this->generator.ret_val = value;
    }
private:
    StaticReturnGenerator<R> generator;
};

#define HAM_FUNC(f) f##_mockup
