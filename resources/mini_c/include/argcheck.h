#pragma once
#include <string>

namespace testing {

template <typename T>
class Expected_arg {
public:
    Expected_arg() {
        this->any = true;
    }
    Expected_arg(T value) {
        this->any = false;
        this->value = value;
    }
    bool operator==(T other) {
        return (any || this->value == other);
    }
    bool operator!=(T other) {
        return (!any && this->value != other);
    }
    ::std::string Describe(void) {
        if (any) return "*";
        else return std::to_string(value);
    }
private:
    bool any;
    T value;
};
}
