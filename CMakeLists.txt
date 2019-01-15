cmake_minimum_required(VERSION 3.0)

project(cdt_2d)

add_executable(cdt_2d main.cpp)

install(TARGETS cdt_2d RUNTIME DESTINATION bin)
