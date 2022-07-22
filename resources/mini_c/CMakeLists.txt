# cmake project definition
cmake_minimum_required(VERSION 3.20.0)

project(mini_c LANGUAGES C CXX)

set(HAMMOCK_DIR ${CMAKE_CURRENT_LIST_DIR}/../../src)

set(PROD_SRC iut.c)
set(MOCK_SRC b.c mockup.cc)
set(TEST_SRC test.cc)

add_executable(
    ${PROJECT_NAME}
    ${PROD_SRC}
    ${MOCK_SRC}
    ${TEST_SRC}
)
