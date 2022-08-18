Component 'a' does not use any external interfaces. So it can be unit-tested without any mocks.






Walked through https://google.github.io/googletest/quickstart-cmake.html

How we can combine the c-functions to gmock is described here:
https://stackoverflow.com/a/41640864/3749628


## Problem

Following problem exists:

Mockup objects need to created INSIDE test functions. The reason why is that a mock object need to be destroyed at the end of the test function 
in order to check its internal states against the expectations claimed by the test code of the test function.

This is necessary by design. If you let live a mock object over more than one test function then you create hidden dependencies between those test functions. That's really bad.
The expectations are then stated across those test functions.

It's interesting that, if you violate that pattern that, gmock+gtest behaves differently on Windows and Linux:

* On Windows the test executable crashes with a SEGFAULT.
* On Linux, it fails gracefully with following message:
```
ERROR: this mock object (used in test test_expectation_not_met__leaked.SomeTest) should be deleted but never is. Its address is @0x555c0ccfd2e0.
ERROR: 1 leaked mock object found at program exit. Expectations on a mock object are verified when the object is destructed. Leaking a mock means that its expectations aren't verified, which is usually a test bug. If you really intend to leak a mock, you can suppress this error using testing::Mock::AllowLeak(mock_object), or you may use a fake or stub instead of a mock.
``` 

I created bug report https://github.com/google/googletest/issues/3982 about the crash on windows.

So again: It's necessary to create the mock functions always INSIDE each test function.

This has consequences for the structure of our mockup and test files. The testcode, inside eacch test functions needs to create a new mock object. But currently the "glue code" between the stubs of the c-functions and the mock object functions rely on the fact that there is ONE global mock object.

This we need to change.

I solved the problem as follows:
I introduced a macro `CREATE_MOCK` which shall be used at the very beginning of a testcase. This creates a local mock object. It also sets a global pointer to that mock object. The c-stubs use this global pointer to access the mock's methods.

Inside each c-stub there is a check if the pointer is not zero. It handles the situation when someone does not used the macro `CREATE_MOCK` in a very simple way: It just prevents a crash. We need to check if there should be a more sophisticated handling on it.




