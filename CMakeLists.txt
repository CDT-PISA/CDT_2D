cmake_minimum_required(VERSION 3.0)

macro(use_gnu_compiler)
    if(${CURRENT_COMPILER} STREQUAL "INTEL")
        # Save current gnu flags
        set(INTEL_CXX_FLAGS ${CMAKE_CXX_FLAGS} CACHE STRING "ICC flags." FORCE)
    endif()

    # Change compiler
    set(CMAKE_CXX_COMPILER ${GNU_CXX_COMPILER})
    set(CMAKE_CXX_FLAGS ${GNU_CXX_FLAGS})
    set(CURRENT_COMPILER "GNU" CACHE STRING "GCC compiler." FORCE)
endmacro()

#macro(use_intel_compiler)
#    if(${CURRENT_COMPILER} STREQUAL "GNU")
#        # Save current intel flags
#        set(GNU_CXX_FLAGS ${CMAKE_CXX_FLAGS} CACHE STRING "GCC flags." FORCE)
#    endif()
#
#    # Change compiler
#    set(CMAKE_CXX_COMPILER ${INTEL_CXX_COMPILER})
#    set(CMAKE_CXX_FLAGS ${INTEL_CXX_FLAGS})
#    set(CURRENT_COMPILER "INTEL" CACHE STRING "ICC compiler." FORCE)
#endmacro()

set(GNU_CXX_COMPILER g++)
set(GNU_CXX_FLAGS "-std=c++17 -O3")
#set(INTEL_CXX_COMPILER icpc)
#set(INTEL_CXX_FLAGS "-std=c++17 -O3")
set(CURRENT_COMPILER "GNU")

project(cdt_2d)

# Bring the headers into the project
include_directories(include)
file(GLOB SOURCES "src/*.cpp")
file(GLOB TRIANGULATION "src/triangulation/*.cpp")

use_gnu_compiler()

# The file(GLOB...) allows for wildcard additions:
message(${CMAKE_CXX_COMPILER})
add_library(cdt_2d_lib STATIC ${SOURCES})
add_custom_command(OUTPUT "src/triangulation.cpp" DEPENDS ${TRIANGULATION})
add_executable(cdt_2d main.cpp)
target_link_libraries(cdt_2d cdt_2d_lib)

install(TARGETS cdt_2d RUNTIME DESTINATION ${CMAKE_CURRENT_SOURCE_DIR}/bin)

# Intel

#use_intel_compiler()

#message(${CMAKE_CXX_COMPILER})
#add_library(intel_lib STATIC ${SOURCES})
#add_executable(intel main.cpp)
#set_target_properties(intel PROPERTIES OUTPUT_NAME "cdt_2d")
#target_link_libraries(intel intel_lib)

#add_custom_target(intel_install mv cdt_2d ../bin/cdt_2d)
# target_compile_options(ciao PUBLIC 
