Usage
=====

Command line
------------

Before we integrate it into the build chain of your choice it is a good idea to call it on the command line
in order to gather more understanding what it does and what it needs.

Let's call hammock without any arguments:

..  code-block:: shell

    $ python -m hammock
    usage: hammock [-h] (--symbols SYMBOLS [SYMBOLS ...] | --plink PLINK) --outdir OUTDIR --sources SOURCES [SOURCES ...]
    hammock: error: the following arguments are required: --outdir/-o, --sources

Hammock needs ...

* *--sources*: The list of paths to source files which represent your item-under test. (In classic unittest it is just one)
* Either ...
   * --symbols*: comma seperated list of symbol names which are to mock or
   * *--plink*: path to the object file which contains the unresolved symbols to mock
* *--outdir*: An existing directory where to write code files containing mockup code.

One compilation unit
--------------------

In a simple scenario your

.. image:: diagrams/usage_one_compile_unit_only.uxf.svg


Make
****

.. include:: usage/examples/one_compile_unit/Makefile
   :code: makefile
   :literal:
   :number-lines:


CMake
*****


More or more compilation units
------------------------------



.. image:: diagrams/usage_one_or_more_compile_units.uxf.svg

Make
****

.. include:: usage/examples/one_or_more_compile_units/Makefile
   :code: makefile
   :literal:
   :number-lines:

CMake
*****


Usage with GoogleTest and GoogleMocks
-------------------------------------

.. include:: ../../tests/data/mini_c_test/CMakeLists.txt
   :code: makefile
   :literal:
   :number-lines:

