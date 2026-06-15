cmake_minimum_required(VERSION 3.15...3.31)
project(robosim LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)
if(NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
  set(CMAKE_BUILD_TYPE Release CACHE STRING "" FORCE)
endif()

include(FetchContent)

# --- Eigen (header-only linear algebra) -----------------------------------
FetchContent_Declare(
  Eigen3
  GIT_REPOSITORY https://gitlab.com/libeigen/eigen.git
  GIT_TAG 3.4.0
  GIT_SHALLOW TRUE
)
set(EIGEN_BUILD_DOC OFF CACHE BOOL "" FORCE)
set(EIGEN_BUILD_TESTING OFF CACHE BOOL "" FORCE)
set(BUILD_TESTING OFF CACHE BOOL "" FORCE)  # silence Eigen's own test tree
FetchContent_MakeAvailable(Eigen3)

# --- robosim core (pure C++, no Python) -----------------------------------
add_library(robosim_core src/physics.cpp)
target_include_directories(robosim_core PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include)
target_link_libraries(robosim_core PUBLIC Eigen3::Eigen)
target_compile_features(robosim_core PUBLIC cxx_std_17)

# --- Python bindings (only under scikit-build/pip, or when requested) ------
if(DEFINED SKBUILD OR ROBOSIM_BUILD_PYTHON)
  find_package(pybind11 CONFIG REQUIRED)
  pybind11_add_module(_core bindings/bindings.cpp)
  target_link_libraries(_core PRIVATE robosim_core)
  install(TARGETS _core LIBRARY DESTINATION robosim)
endif()

# --- C++ tests (standalone dev builds only; excluded from wheels) ----------
option(ROBOSIM_BUILD_TESTS "Build C++ Catch2 tests" ON)
if(ROBOSIM_BUILD_TESTS AND NOT DEFINED SKBUILD)
  FetchContent_Declare(
    Catch2
    GIT_REPOSITORY https://github.com/catchorg/Catch2.git
    GIT_TAG v3.7.1
    GIT_SHALLOW TRUE
  )
  FetchContent_MakeAvailable(Catch2)
  enable_testing()
  add_executable(test_physics tests/cpp/test_physics.cpp)
  target_link_libraries(test_physics PRIVATE robosim_core Catch2::Catch2WithMain)
  list(APPEND CMAKE_MODULE_PATH ${catch2_SOURCE_DIR}/extras)
  include(Catch)
  catch_discover_tests(test_physics)
endif()
