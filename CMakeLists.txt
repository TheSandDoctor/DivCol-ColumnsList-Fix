cmake_minimum_required(VERSION 2.8.12)
project(divcolfixer)

add_subdirectory(pybind11)
pybind11_add_module(divcolfixer src/main.cpp)
