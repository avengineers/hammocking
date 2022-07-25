/* Stolen from Gmock.
 * To be done: Praise the creator (BSD-3 license)
*/
#pragma once

#include <limits.h>
#include <ostream>  // NOLINT
#include <iostream>
#include <string>
#include <memory>

namespace testing {
// The implementation of a cardinality.
class CardinalityInterface {
public:
    virtual ~CardinalityInterface() {}

    // Conservative estimate on the lower/upper bound of the number of
    // calls allowed.
    virtual int ConservativeLowerBound() const { return 0; }
    virtual int ConservativeUpperBound() const { return INT_MAX; }

    // Returns true if and only if call_count calls will satisfy this
    // cardinality.
    virtual bool IsSatisfiedByCallCount(int call_count) const = 0;

    // Returns true if and only if call_count calls will saturate this
    // cardinality.
    virtual bool IsSaturatedByCallCount(int call_count) const = 0;

    virtual ::std::string Describe(void) const = 0;
    // Describes self to an ostream.
    virtual void DescribeTo(::std::ostream* os) const = 0;
};

// A Cardinality is a copyable and IMMUTABLE (except by assignment)
// object that specifies how many times a mock function is expected to
// be called.  The implementation of Cardinality is just a std::shared_ptr
// to const CardinalityInterface. Don't inherit from Cardinality!
class  Cardinality {
public:
    // Constructs a null cardinality.  Needed for storing Cardinality
    // objects in STL containers.
    Cardinality() {}

    // Constructs a Cardinality from its implementation.
    explicit Cardinality(const CardinalityInterface* impl) : impl_(impl) {}

    // Conservative estimate on the lower/upper bound of the number of
    // calls allowed.
    int ConservativeLowerBound() const { return impl_->ConservativeLowerBound(); }
    int ConservativeUpperBound() const { return impl_->ConservativeUpperBound(); }

    // Returns true if and only if call_count calls will satisfy this
    // cardinality.
    bool IsSatisfiedByCallCount(int call_count) const {
        return impl_->IsSatisfiedByCallCount(call_count);
    }

    // Returns true if and only if call_count calls will saturate this
    // cardinality.
    bool IsSaturatedByCallCount(int call_count) const {
        return impl_->IsSaturatedByCallCount(call_count);
    }

    // Returns true if and only if call_count calls will over-saturate this
    // cardinality, i.e. exceed the maximum number of allowed calls.
    bool IsOverSaturatedByCallCount(int call_count) const {
        return impl_->IsSaturatedByCallCount(call_count) &&
            !impl_->IsSatisfiedByCallCount(call_count);
    }

    // Describes self to an ostream
    void DescribeTo(::std::ostream* os) const { impl_->DescribeTo(os); }
    ::std::string Describe(void) const { return impl_->Describe(); }

    // Describes the given actual call count to an ostream.
    static void DescribeActualCallCountTo(int actual_call_count,
        ::std::ostream* os);

private:
    std::shared_ptr<const CardinalityInterface> impl_;
};

// Creates a cardinality that allows at least n calls.
Cardinality AtLeast(int n);

// Creates a cardinality that allows at most n calls.
Cardinality AtMost(int n);

// Creates a cardinality that allows any number of calls.
Cardinality AnyNumber();

// Creates a cardinality that allows between min and max calls.
Cardinality Between(int min, int max);

// Creates a cardinality that allows exactly n calls.
Cardinality Exactly(int n);

// Creates a cardinality from its implementation.
inline Cardinality MakeCardinality(const CardinalityInterface* c) {
    return Cardinality(c);
}

} /* namespace */
