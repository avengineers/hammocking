Why HammocKing?
===============

Short story short:

**HammocKing** automates the generation of mockups of C-code in

* Google Test/Mock styles

or mockups, fakes, stubs of the framework of your choice.


    => Ready to unit test of legacy code in under a minute. <=


Short story long:

Unit testing
------------

    "The absence of **unit tests** may indicate a lack of **maturity in engineering** ..."

    "...unit tests should be **performed by developers** as soon as a function is coded..."

Source: https://medium.com/danilo-ferreira/the-absence-of-unit-tests-may-indicate-a-lack-of-maturity-in-engineering-c207bfcd3a2e


Prerequisites for a **successful** process implementation:

Unit test framework must be integral part of ...

* Mature
* Simple-to-use
* Well documented
* Developer's IDE/Editor
* Build system,
* Continuous Integration system.



Usecase
-------

**Problem: Big amount of legacy code base.**

This often leads to a very long getting started time before you can write your first unit test.

Why?

(Embedded) software consists of a set of software units.
They share data through interfaces.

"Legacy" code means that code base has grown WITHOUT unit tests.

(At least some of the) units have many interfaces.

.. image:: diagrams/motivation_1_embedded_software.svg

Let's isolate unit a to be item-under-test (iut) for unit testing. Such a unit usually consists of one c file. Occassionally it consists of more than one source files.

.. image:: diagrams/motivation_2_iut_isolated.svg


Without HammocKing
------------------

The typical mood of a developer who does that is ...

.. image:: https://www.nexmo.com/wp-content/uploads/2015/03/Manyellingatcomputer-1.jpg

In the language of a C/C++ developer the "required interfaces" are "external dependencies". So when isolated, these external dependencies which are

* global variables or
* global functions

do not exist. You need some "glue code" between your isolated production unit (unit under test) and your test file.


When building the test executable the linker complains about them unless you define them. This you do usually either in the source code of your test file(s) or in dedicated 
source files or you dedicate special mock source file(s) for that.

Especially when beginning unit testing of large legacy units never have seen test driven developers' hands it becomes very tedious to do the manual task of ...

* Filter the linker's error messages for undefined reference. Then ...
* For each reference ...
    * Search through source code to find the declaration of that reference (symbol)
    * Add include of header file where declaration is found to test code
    * Convert the declaration to a definition and ...
    * If the symbol is a function then write the body to establish the data flow between unit under test and test code (so write a mock, stub or fake).


Below example shows the linker's output for just 2 undefine references:

.. code-block:: console

    gcc -c -g -MMD -o a.c.obj a.c
    gcc -c -g -MMD -o a_test.c.obj a_test.c
    gcc   -g -o a_test.exe a.c.obj a_test.c.obj
    c:/users/manna/scoop/apps/mingw-winlibs-llvm-ucrt/current/bin/../lib/gcc/x86_64-w64-mingw32/12.2.0/../../../../x86_64-w64-mingw32/bin/ld.exe: a.c.obj: in function `a_some_func':
    C:\d\repos\hammock\doc\source\usage\examples\one_compile_unit/a.c:6: undefined reference to `b_getX'
    c:/users/manna/scoop/apps/mingw-winlibs-llvm-ucrt/current/bin/../lib/gcc/x86_64-w64-mingw32/12.2.0/../../../../x86_64-w64-mingw32/bin/ld.exe: C:\d\repos\hammock\doc\source\usage\examples\one_compile_unit/a.c:8: undefined reference to `c_setY'
    collect2.exe: error: ld returned 1 exit status
    make: *** [makefile:14: a_test.exe] Error 1
    PS C:\d\repos\hammock\doc\source\usage\examples\one_compile_unit> 


Back on the abstract level what the developer manually does is to create such adaptors (Mocks) between production code and test code:

.. image:: diagrams/motivation_4_iut_harness.svg

With HammocKing
---------------

.. image:: https://as2.ftcdn.net/v2/jpg/04/43/94/95/1000_F_443949516_guxeFkk1XEBx6kU2eJJ0NOuw5K3qQ4Y9.jpg

Or you let `hammocking` do this tedious job of creating these adaptors:

.. code-block:: console

    PS C:\d\repos\hammock\doc\source\usage\examples\one_compile_unit> make
    gcc -c -g -MMD -o a.c.obj a.c
    python -m hammocking --source a.c --plink a.c.obj --style plain_c --outdir . -g
    INFO: HammocKing: Will create mockup for function b_getX
    INFO: HammocKing: Will create mockup for function c_setY
    gcc -c -g -MMD -o a_test.c.obj a_test.c
    gcc -c -g -MMD -o mockup.c.obj mockup.c
    gcc   -g -o a_test.exe a.c.obj a_test.c.obj mockup.c.obj
    ./a_test.exe
    PS C:\d\repos\hammock\doc\source\usage\examples\one_compile_unit>

Remark: This means to can directly start with your (first) unit tests for that unit.



Google Test is only the default.
-------------------------------------

Why is the Google Test (including Google Mock) test framework the default?

See https://cuhkszlib-xiaoxing.readthedocs.io/en/latest/external/gtest/googletest/docs/FAQ.html

Mockups, stubs, fakes.

See https://stackoverflow.com/questions/346372/whats-the-difference-between-faking-mocking-and-stubbing

Test frameworks.

See https://en.wikipedia.org/wiki/List_of_unit_testing_frameworks#C

See Mockup styles.

.. image:: diagrams/motivation_5_style.svg

Appendix
--------

.. image:: diagrams/motivation_3_r_p_interfaces.svg




