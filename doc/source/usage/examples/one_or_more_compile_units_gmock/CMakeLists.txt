project(a_test)

cmake_minimum_required(VERSION 3.0)

add_executable(
    a_test
    a
    mockup.c
    a_test.c
)

add_library(
    a
    OBJECT
    a_1.c
    a_2.c
)

target_include_directories(
    a_test
    PRIVATE
    ${CMAKE_CURRENT_BINARY_DIR}
    ${CMAKE_CURRENT_LIST_DIR}
)

get_target_property(MOCK_SOURCES a SOURCES)

add_custom_command(
    OUTPUT mockup.c
    BYPRODUCTS mockup.h
    WORKING_DIRECTORY ${CMAKE_CURRENT_LIST_DIR}
    COMMAND python -m hammocking --sources ${MOCK_SOURCES} --plink $<TARGET_OBJECTS:a> --style plain_c --outdir ${CMAKE_CURRENT_BINARY_DIR}
    DEPENDS
    a
)

add_custom_command(
    TARGET a_test
    POST_BUILD
    COMMAND a_test
)
