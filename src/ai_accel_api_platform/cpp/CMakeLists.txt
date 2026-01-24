cmake_minimum_required(VERSION 3.18)
project(fast_ops LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

find_package(pybind11 CONFIG REQUIRED)
find_package(OpenMP)

pybind11_add_module(fast_ops bindings.cpp fast_ops.cpp)

if (OpenMP_CXX_FOUND)
  target_link_libraries(fast_ops PRIVATE OpenMP::OpenMP_CXX)
  target_compile_definitions(fast_ops PRIVATE USE_OPENMP)
endif()

set_target_properties(fast_ops PROPERTIES
  LIBRARY_OUTPUT_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}"
)
