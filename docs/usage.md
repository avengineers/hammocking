# Usage

## Command line

Before integrating hammocking into your build system, try it on the command line to understand what it does and what it needs.

```shell
python -m hammocking --sources <source files> --plink <object file> --outdir <output dir>
```

### Required arguments

| Argument | Description |
|----------|-------------|
| `--sources` | Source files of the unit under test. Hammocking parses these to find symbol declarations. |
| `--outdir`, `-o` | Directory where generated mock files are written. Must exist. |

Plus **one** of these (mutually exclusive):

| Argument | Description |
|----------|-------------|
| `--symbols`, `-s` | Space-separated list of symbol names to mock. |
| `--plink`, `-p` | Path to a partially linked object file. Hammocking extracts undefined symbols from it using `nm`. |

### Optional arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `--style`, `-t` | `gmock` | Output style for generated mocks. See [Mock output styles](#mock-output-styles). |
| `--suffix` | *(empty)* | Suffix added to generated filenames (e.g. `_mock` produces `mockup_mock.cc`). |
| `--config` | *(none)* | Path to a project-level `hammocking.ini`. See [Configuration](#configuration). |
| `--except` | `/usr/include` | Path prefixes to exclude from symbol search. Symbols found in headers under these paths are not mocked. |
| `--exclude` | *(none)* | Specific symbol names to skip, even if they appear as undefined. |
| `--exclude-pattern` | *(from config)* | Regex pattern — matching symbols from `nm` output are skipped. |
| `--include-pattern` | *(none)* | Regex pattern — only matching symbols are considered. Takes precedence over `--exclude-pattern`. |
| `--clang-lib-file` | *(auto)* | Filename of the libclang shared library (e.g. `libclang.so`). |
| `--clang-lib-path` | *(auto)* | Directory containing the libclang shared library. |
| `--nm-path` | `nm` | Path to the `nm` tool. |
| `--ignore-symbols-outside-project` | `true` | Skip symbols whose declarations are outside `--project-root-dir`. |
| `--project-root-dir` | *(none)* | Project root directory. Required for `--ignore-symbols-outside-project`. |
| `--debug`, `-d` | `false` | Enable debug logging. |

Any additional arguments not listed here are passed through to libclang (e.g. `-I<path>` for include directories, `-x c` to force C language mode).

(mock-output-styles)=
## Mock output styles

Hammocking supports two output styles, selected via `--style`:

| Style | Files generated | Use case |
|-------|-----------------|----------|
| `gmock` (default) | `mockup.cc`, `mockup.h` | C++ test frameworks with Google Mock. Functions are wrapped as `MOCK_METHOD`, variables as extern definitions. |
| `plain_c` | `mockup.c`, `mockup.h` | Pure C test environments. Functions are generated as simple stubs, variables as plain definitions. |

## One compilation unit

This scenario is shown for explanation purposes. The next chapter covers both single and multiple compilation units.

![Usage One Compile Unit Only](diagrams/usage_one_compile_unit_only.uxf.svg)

### Make

```makefile
CC := gcc -c
LD := gcc
CC_OPTS := -g

a_test.exe: a.c.obj a_test.c.obj mockup.c.obj
	$(LD) $(CC_OPTS) -o $@ $^

%.c.obj: %.c
	$(CC) $(CC_OPTS) -MMD -o $@ $<

mockup.c: a.c.obj
	python -m hammocking --sources a.c --plink a.c.obj --style plain_c --outdir . $(CC_OPTS)
```

### CMake

For a single compilation unit, the CMake setup is the same as for multiple units below — just with a single source file in the `OBJECT` library.

## One or more compilation units

![Usage One or More Compile Units](diagrams/usage_one_or_more_compile_units.uxf.svg)

### Make

```makefile
CC := gcc -c
LD := gcc
CC_OPTS := -g

a_test.exe: a_1.c.obj a_2.c.obj a_test.c.obj mockup.c.obj
	$(LD) $(CC_OPTS) -o $@ $^

%.c.obj: %.c
	$(CC) $(CC_OPTS) -MMD -o $@ $<

# Partially link all production objects into one file
a.obj: a_1.c.obj a_2.c.obj
	$(LD) -r -nostdlib -o $@ $^

# Generate mocks from the partially linked object
mockup.c: a.obj
	python -m hammocking --sources a_1.c a_2.c --plink a.obj --style plain_c --outdir . $(CC_OPTS)
```

### CMake

```cmake
project(a_test)
cmake_minimum_required(VERSION 3.0)

add_library(a OBJECT a_1.c a_2.c)
get_target_property(HAMMOCKING_SOURCES a SOURCES)

# Partially link production objects
set(PROD_PARTIAL_LINK a.obj)
add_custom_command(
    OUTPUT ${PROD_PARTIAL_LINK}
    COMMAND ${CMAKE_C_COMPILER} -r -nostdlib -o ${PROD_PARTIAL_LINK} $<TARGET_OBJECTS:a>
    COMMAND_EXPAND_LISTS
    VERBATIM
    DEPENDS $<TARGET_OBJECTS:a>
)

# Generate mocks
add_custom_command(
    OUTPUT mockup.c
    BYPRODUCTS mockup.h
    WORKING_DIRECTORY ${CMAKE_CURRENT_LIST_DIR}
    COMMAND python -m hammocking
        --sources ${HAMMOCKING_SOURCES}
        --plink ${CMAKE_CURRENT_BINARY_DIR}/${PROD_PARTIAL_LINK}
        --style plain_c
        --outdir ${CMAKE_CURRENT_BINARY_DIR}
    DEPENDS ${PROD_PARTIAL_LINK}
)

add_executable(a_test mockup.c a_test.c)
target_link_libraries(a_test a)
target_include_directories(a_test PRIVATE
    ${CMAKE_CURRENT_BINARY_DIR}
    ${CMAKE_CURRENT_LIST_DIR}
)
```

## Usage with Google Test and Google Mock

When using [Google Test](https://google.github.io/googletest/) with [Google Mock](https://google.github.io/googletest/reference/mocking.html), use `--style gmock` (the default). This generates `mockup.cc` with `MOCK_METHOD` wrappers and a `mockup.h` header.

```cmake
# Fetch Google Test
include(FetchContent)
FetchContent_Declare(googletest
    GIT_REPOSITORY https://github.com/google/googletest.git
    GIT_TAG release-1.12.1
)
FetchContent_MakeAvailable(googletest)

include(GoogleTest)
enable_testing()

# Production code as OBJECT library
add_library(prodlib OBJECT b.c)

# Partially link
set(PROD_PARTIAL_LINK prod.obj)
add_custom_command(
    OUTPUT ${PROD_PARTIAL_LINK}
    COMMAND ${CMAKE_CXX_COMPILER} -r -nostdlib -o ${PROD_PARTIAL_LINK} $<TARGET_OBJECTS:prodlib>
    COMMAND_EXPAND_LISTS
    VERBATIM
    DEPENDS $<TARGET_OBJECTS:prodlib>
)

# Generate gmock-style mocks
add_custom_command(
    OUTPUT mockup.cc
    BYPRODUCTS mockup.h
    WORKING_DIRECTORY ${CMAKE_CURRENT_LIST_DIR}
    COMMAND python -m hammocking
        --sources b.c
        --plink ${CMAKE_CURRENT_BINARY_DIR}/${PROD_PARTIAL_LINK}
        --outdir ${CMAKE_CURRENT_BINARY_DIR}
        "-I$<JOIN:$<TARGET_PROPERTY:prodlib,INCLUDE_DIRECTORIES>,;-I>"
    DEPENDS ${PROD_PARTIAL_LINK}
)

# Test executable
add_executable(my_test mockup.cc b_test.cc)
target_link_libraries(my_test prodlib GTest::gtest_main GTest::gmock_main)
gtest_discover_tests(my_test)
```

## Exclude symbols outside the project root

Hammocking ignores symbols whose declarations are found outside your project root directory by default. This filters out symbols provided by standard libraries or system headers.

To use this feature, specify the project root with `--project-root-dir`:

```shell
python -m hammocking --sources src/my_module.c --plink build/my_module.obj \
    --outdir build/ --project-root-dir /path/to/my/project
```

To opt out, set `ignore_symbols_outside_project=false` in your `hammocking.ini` configuration file.

(configuration)=
## Configuration

Hammocking ships with a built-in default `hammocking.ini` that provides sensible defaults for all platforms. You can override individual settings by providing a project-level configuration file.

### How configuration merging works

Hammocking always loads its **built-in defaults first**, then overlays your project configuration on top. This means your project config only needs to contain the settings you want to change — everything else falls back to the defaults.

The priority order (highest wins):

1. **Command line options** — always win
2. **Project `hammocking.ini`** — provided via `--config`
3. **Built-in defaults** — shipped with the package

For example, if the built-in default sets `exclude_pattern=^(_|llvm_|memcpy|...)` and your project config only sets `ignore_symbols_outside_project=true`, the default `exclude_pattern` remains active.

### Project configuration file

Create a file named `hammocking.ini` with the settings you want to override:

```ini
[hammocking]
parameter = value
[hammocking.<system>]
parameter = value
```

The `<system>` section depends on the platform you are running on, e.g. `hammocking.linux` for Linux, `hammocking.win32` for Windows, or `hammocking.darwin` for macOS. Platform-specific settings override the generic `[hammocking]` section.

Pass it to hammocking with the `--config` option:

```shell
python -m hammocking --config path/to/hammocking.ini ...
```

### Available parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `clang_lib_file` | *(none)* | Filename of the libclang shared library |
| `clang_lib_path` | *(platform-specific)* | Directory containing the libclang shared library |
| `ignore_path` | *(platform-specific)* | Comma-separated list of paths to exclude from symbol search (called `exclude_paths` on the command line) |
| `exclude_pattern` | `^(_\|llvm_\|memcpy\|memmove\|memset\|memcmp\|bzero\|strlen)` | Regex pattern — matching symbols from `nm` output are skipped. Filters out compiler-generated runtime symbols that should not be mocked. |
| `include_pattern` | *(none)* | Regex pattern — only matching symbols are considered. Takes precedence over `exclude_pattern`. |
| `nm` | `nm` | Path to the `nm` tool for extracting undefined symbols |
| `ignore_symbols_outside_project` | `true` | When `true`, symbols found outside the project root directory are ignored |

Each of these parameters can also be set via command line option. Command line options always take precedence over configuration file values.

### Default exclude_pattern

The built-in `exclude_pattern` filters out symbols that compilers (especially GCC) generate implicitly, such as calls to `memcpy` for struct copies or `memset` for zero-initialization. These are runtime library functions, not real dependencies of your code.

If you need to mock one of these filtered symbols, you have two options:

* Use `include_pattern` in your project config — it takes precedence over `exclude_pattern`
* Override `exclude_pattern` in your project config with a narrower pattern
