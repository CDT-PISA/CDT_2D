cmake_minimum_required(VERSION 3.0)

project(cdt_2d)

# Bring the headers into the project
include_directories(include)

# The file(GLOB...) allows for wildcard additions:
file(GLOB SOURCES "src/*.cpp")
#list(REMOVE_ITEM SOURCES "src/debug.cpp")
#set(SOURCES src/main.cpp src/triangulation.cpp)

add_library(cdt_2d_lib STATIC ${SOURCES})

# # Bring the headers into the project
# target_include_directories(cdt_2d_lib PRIVATE include)

add_executable(cdt_2d main.cpp)
target_link_libraries(cdt_2d cdt_2d_lib)

set_property(TARGET cdt_2d PROPERTY CXX_STANDARD 17)
set_property(TARGET cdt_2d_lib PROPERTY CXX_STANDARD 17)

install(TARGETS cdt_2d RUNTIME DESTINATION ~/projects/CDT_2D/bin)
# install(TARGETS cdt_2d RUNTIME DESTINATION ~/projects/CDT_2D/bin CONFIGURATIONS Release)
