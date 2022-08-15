# cmake project definition
cmake_minimum_required(VERSION 3.20.0)

set(CMAKE_C_COMPILER clang CACHE STRING "C Compiler")
project(mini_c C)

set(HAMMOCK_DIR ${CMAKE_CURRENT_LIST_DIR}/../../src)

set(PROD_SRC main.c b.c)
set(MOCK_SRC mockup.c)


set(THE_FLAGS -Wall -Wextra -DCFG_A -DCFG_D)
add_compile_options(
    "$<$<COMPILE_LANGUAGE:C>:${THE_FLAGS}>"
)

# One command to mock them all!
add_custom_command(
    OUTPUT ${MOCK_SRC}
    BYPRODUCTS mockup.h mockup_config.h mockups.mockup
    WORKING_DIRECTORY ${CMAKE_CURRENT_LIST_DIR}
    COMMAND ${CMAKE_COMMAND} -E copy ${HAMMOCK_DIR}/mockup.c ${CMAKE_CURRENT_BINARY_DIR}/
    COMMAND ${CMAKE_COMMAND} -E copy ${HAMMOCK_DIR}/mockup.h ${CMAKE_CURRENT_BINARY_DIR}/
    COMMAND python ${HAMMOCK_DIR}/hammock.py --sources ${PROD_SRC} --symbols c d some_var --output ${CMAKE_CURRENT_BINARY_DIR}/mockups.mockup --config ${CMAKE_CURRENT_BINARY_DIR}/mockup_config.h ${THE_FLAGS}
    DEPENDS ${PROD_SRC} ${HAMMOCK_DIR}/mockup.c ${HAMMOCK_DIR}/hammock.py
)

add_executable(
    ${PROJECT_NAME}
    ${PROD_SRC}
    ${MOCK_SRC}
)

target_compile_options(${PROJECT_NAME} PRIVATE --include ${CMAKE_CURRENT_BINARY_DIR}/mockup_config.h)
