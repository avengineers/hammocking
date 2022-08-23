# cmake project definition
cmake_minimum_required(VERSION 3.20.0)

set(CMAKE_C_COMPILER clang CACHE STRING "C Compiler")
project(mini_c)


## GTEST + GMOCK STUFF ####################################
# GoogleTest requires at least C++14
set(CMAKE_CXX_STANDARD 14)

include(FetchContent)
FetchContent_Declare(
  googletest
  GIT_REPOSITORY https://github.com/google/googletest.git
  GIT_TAG release-1.12.1
)

if (WIN32)
    # Prevent overriding the parent project's compiler/linker
    # settings on Windows
    set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
endif()

FetchContent_MakeAvailable(googletest)

include(GoogleTest)

find_package(Threads REQUIRED)

enable_testing()
## END OF GTEST + GMOCK STUFF #############################

add_compile_options(-fPIC)

set(PROD_SRC b.c)
set(MOCK_SRC mockup.cc)
set(TEST_SRC b_test.cc)

add_library(prodlib OBJECT ${PROD_SRC})

add_executable(
    ${PROJECT_NAME}
    ${MOCK_SRC}
    ${TEST_SRC}
)

target_link_libraries(
    ${PROJECT_NAME}
    prodlib
    GTest::gtest_main
    GTest::gmock_main
    Threads::Threads
)

gtest_discover_tests(${PROJECT_NAME})
