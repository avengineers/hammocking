#include "include/cardinality.h"
#include <sstream>

namespace testing {
// Implements the Between(m, n) cardinality.
class BetweenCardinalityImpl : public CardinalityInterface {
public:
    BetweenCardinalityImpl(int min, int max)
        : min_(min >= 0 ? min : 0), max_(max >= min_ ? max : min_) {
        if (min < 0) {
            std::cerr << "The invocation lower bound must be >= 0, "
                << "but is actually " << min << ".";
        }
        else if (max < 0) {
            std::cerr << "The invocation upper bound must be >= 0, "
                << "but is actually " << max << ".";
        }
        else if (min > max) {
            std::cerr << "The invocation upper bound (" << max
                << ") must be >= the invocation lower bound (" << min << ").";
        }
    }

    // Conservative estimate on the lower/upper bound of the number of
    // calls allowed.
    int ConservativeLowerBound() const override { return min_; }
    int ConservativeUpperBound() const override { return max_; }

    bool IsSatisfiedByCallCount(int call_count) const override {
        return min_ <= call_count && call_count <= max_;
    }

    bool IsSaturatedByCallCount(int call_count) const override {
        return call_count >= max_;
    }

    void DescribeTo(::std::ostream* os) const override;
    std::string Describe(void) const override;

private:
    const int min_;
    const int max_;

    BetweenCardinalityImpl(const BetweenCardinalityImpl&) = delete;
    BetweenCardinalityImpl& operator=(const BetweenCardinalityImpl&) = delete;
};

// Formats "n times" in a human-friendly way.
inline std::string FormatTimes(int n) {
    if (n == 1) {
        return "once";
    }
    else if (n == 2) {
        return "twice";
    }
    else {
        std::stringstream ss;
        ss << n << " times";
        return ss.str();
    }
}

// Describes the Between(m, n) cardinality in human-friendly text.
std::string BetweenCardinalityImpl::Describe(void) const {
    std::stringstream ss;
    if (min_ == 0) {
        if (max_ == 0) {
            ss << "never called";
        }
        else if (max_ == INT_MAX) {
            ss << "called any number of times";
        }
        else {
            ss << "called at most " << FormatTimes(max_);
        }
    }
    else if (min_ == max_) {
        ss << "called " << FormatTimes(min_);
    }
    else if (max_ == INT_MAX) {
        ss << "called at least " << FormatTimes(min_);
    }
    else {
        // 0 < min_ < max_ < INT_MAX
        ss << "called between " << min_ << " and " << max_ << " times";
    }
    return ss.str();
}

void BetweenCardinalityImpl::DescribeTo(::std::ostream* os) const {
    *os << Describe();
}

// Creates a cardinality that allows at least n calls.
Cardinality AtLeast(int n) { return Between(n, INT_MAX); }

// Creates a cardinality that allows at most n calls.
Cardinality AtMost(int n) { return Between(0, n); }

// Creates a cardinality that allows any number of calls.
Cardinality AnyNumber() { return AtLeast(0); }

// Creates a cardinality that allows between min and max calls.
Cardinality Between(int min, int max) {
    return Cardinality(new BetweenCardinalityImpl(min, max));
}

// Creates a cardinality that allows exactly n calls.
Cardinality Exactly(int n) { return Between(n, n); }

}

