# cmake project definition
cmake_minimum_required(VERSION 3.20.0)

set(CMAKE_C_COMPILER clang CACHE STRING "C Compiler")
project(mini_c C)

set(HAMMOCK_DIR ${CMAKE_CURRENT_LIST_DIR}/../../src)

set(PROD_SRC main.c b.c)
set(MOCK_SRC mockup.c)
set(PROD_SRC_OBJECT prod.obj)

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

add_library(
    prod
    ${PROD_SRC}
)

add_custom_command(
    OUTPUT ${PROD_SRC_OBJECT}
    WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
    COMMAND clang -r -nostdlib -o ${PROD_SRC_OBJECT} libprod.a
    COMMAND llvm-nm --undefined-only ${PROD_SRC_OBJECT}
    DEPENDS prod
)

add_executable(
    ${PROJECT_NAME}
    ${MOCK_SRC}
)

target_link_libraries(${PROJECT_NAME} prod)

target_compile_options(${PROJECT_NAME} PRIVATE --include ${CMAKE_CURRENT_BINARY_DIR}/mockup_config.h)

# Get all properties that cmake supports
if(NOT CMAKE_PROPERTY_LIST)
    execute_process(COMMAND cmake --help-property-list OUTPUT_VARIABLE CMAKE_PROPERTY_LIST)
    
    # Convert command output into a CMake list
    string(REGEX REPLACE ";" "\\\\;" CMAKE_PROPERTY_LIST "${CMAKE_PROPERTY_LIST}")
    string(REGEX REPLACE "\n" ";" CMAKE_PROPERTY_LIST "${CMAKE_PROPERTY_LIST}")
endif()
    
function(print_properties)
    message("CMAKE_PROPERTY_LIST = ${CMAKE_PROPERTY_LIST}")
endfunction()
    
function(print_target_properties target)
    if(NOT TARGET ${target})
      message(STATUS "There is no target named '${target}'")
      return()
    endif()

    foreach(property ${CMAKE_PROPERTY_LIST})
        string(REPLACE "<CONFIG>" "${CMAKE_BUILD_TYPE}" property ${property})

        # Fix https://stackoverflow.com/questions/32197663/how-can-i-remove-the-the-location-property-may-not-be-read-from-target-error-i
        if(property STREQUAL "LOCATION" OR property MATCHES "^LOCATION_" OR property MATCHES "_LOCATION$")
            continue()
        endif()

        get_property(was_set TARGET ${target} PROPERTY ${property} SET)
        if(was_set)
            get_target_property(value ${target} ${property})
            message("${target} ${property} = ${value}")
        endif()
    endforeach()
endfunction()

message("##########")
print_target_properties(${PROJECT_NAME})
