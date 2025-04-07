project(a_test)

cmake_minimum_required(VERSION 3.0)

add_executable(
    a_test
    mockup.c
    a_test.c
)

add_library(
    a
    OBJECT
    a_1.c
    a_2.c
)

target_link_libraries(
    a_test
    a
)

target_include_directories(
    a_test
    PRIVATE
    ${CMAKE_CURRENT_BINARY_DIR}
    ${CMAKE_CURRENT_LIST_DIR}
)

get_target_property(HAMMOCKING_SOURCES a SOURCES)

set(HAMMOCKING_LIBRARY_AS_ONE_OBJECT a.obj)

add_custom_command(
    OUTPUT mockup.c
    BYPRODUCTS mockup.h
    WORKING_DIRECTORY ${CMAKE_CURRENT_LIST_DIR}
    COMMAND python -m hammocking --sources ${HAMMOCKING_SOURCES} --plink ${CMAKE_CURRENT_BINARY_DIR}/${HAMMOCKING_LIBRARY_AS_ONE_OBJECT} --style=plain_c --outdir ${CMAKE_CURRENT_BINARY_DIR}
    DEPENDS
    ${HAMMOCKING_LIBRARY_AS_ONE_OBJECT}
)

add_custom_command(
    OUTPUT ${HAMMOCKING_LIBRARY_AS_ONE_OBJECT}
    COMMAND ${CMAKE_C_COMPILER} -r -nostdlib -o ${HAMMOCKING_LIBRARY_AS_ONE_OBJECT} $<TARGET_OBJECTS:a>
    COMMAND_EXPAND_LISTS
    VERBATIM
    DEPENDS $<TARGET_OBJECTS:a>
)

add_custom_command(
    TARGET a_test
    POST_BUILD
    COMMAND a_test
)
