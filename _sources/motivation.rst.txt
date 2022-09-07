Why HammocKing?
===============

Unit testing

    "The absence of **unit tests** may indicate a lack of **maturity in engineering** ..."

    "...unit tests should be **performed by developers** as soon as a function is coded..."

Source: https://medium.com/danilo-ferreira/the-absence-of-unit-tests-may-indicate-a-lack-of-maturity-in-engineering-c207bfcd3a2e

Usecase
-------

(Embedded) software consists of a set of software units.
They share data through interfaces.

"Legacy" code means that code base has grown WITHOUT unit tests.

(At least some of the) units have many interfaces.

.. image:: diagrams/motivation_1_embedded_software.svg

Let's isolate unit a to be item-under-test (iut) for unit testing.

.. image:: diagrams/motivation_2_iut_isolated.svg


Without HammocKing
------------------

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

.. image:: https://www.nexmo.com/wp-content/uploads/2015/03/Manyellingatcomputer-1.jpg

.. image:: diagrams/motivation_4_iut_harness.svg


With HammocKing
---------------

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

.. image:: https://as2.ftcdn.net/v2/jpg/04/43/94/95/1000_F_443949516_guxeFkk1XEBx6kU2eJJ0NOuw5K3qQ4Y9.jpg



Google Mock is only the default.
--------------------------------

Mockups, stubs, fakes.

See https://stackoverflow.com/questions/346372/whats-the-difference-between-faking-mocking-and-stubbing

Test frameworks.

See https://en.wikipedia.org/wiki/List_of_unit_testing_frameworks#C

See Mockup styles.

.. image:: diagrams/motivation_5_style.svg

Appendix
--------

.. image:: diagrams/motivation_3_r_p_interfaces.svg




