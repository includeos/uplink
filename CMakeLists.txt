cmake_minimum_required(VERSION 3.0)
#TODO bump to a newer version that works with the below as minimum


set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

#get arch the proper cmake way
if (NOT DEFINED ARCH)
  set(ARCH ${CMAKE_HOST_SYSTEM_PROCESSOR})
endif()

add_definitions(-DARCH_${ARCH})
add_definitions(-DARCH="${ARCH}")


option(LIVEUPDATE "Enable liveupdate" ON)
option(TLS "Enable secure connections" ON)

if (EXISTS ${CMAKE_CURRENT_BINARY_DIR}/conanbuildinfo.cmake)
  include(${CMAKE_CURRENT_BINARY_DIR}/conanbuildinfo.cmake)
  conan_basic_setup()
else()
  if (NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release)
  endif()
  if (CONAN_PROFILE)
    set(CONANPROFILE PROFILE ${CONAN_PROFILE})
  endif()
  if(NOT EXISTS "${CMAKE_BINARY_DIR}/conan.cmake")
     message(STATUS "Downloading conan.cmake from https://github.com/conan-io/cmake-conan")
     file(DOWNLOAD "https://github.com/conan-io/cmake-conan/raw/v0.13/conan.cmake"
                   "${CMAKE_BINARY_DIR}/conan.cmake")
  endif()
  include(${CMAKE_BINARY_DIR}/conan.cmake)
  conan_cmake_run(
    CONANFILE conanfile.py
    BASIC_SETUP
    ${CONANPROFILE}
  )
endif()

set(LIBRARY_NAME "uplink")

set(SOURCES
  transport.cpp
  ws_uplink.cpp
  register_plugin.cpp
  config.cpp
  uplink.cpp
  )

# Install headers
install(DIRECTORY . DESTINATION ${INCLUDE_PREFIX}include/uplink
  FILES_MATCHING PATTERN "*.hpp"
  PATTERN "starbase" EXCLUDE
  PATTERN "build" EXCLUDE)

# Uplink library
add_library(${LIBRARY_NAME} STATIC ${SOURCES})
if (LIVEUPDATE)
  set_target_properties(${LIBRARY_NAME} PROPERTIES COMPILE_DEFINITIONS "LIVEUPDATE")
endif()
install(TARGETS ${LIBRARY_NAME} DESTINATION ${LIB_PREFIX}plugins)

# Uplink log driver
add_library(uplink_log STATIC uplink_log.cpp)
install(TARGETS uplink_log DESTINATION ${LIB_PREFIX}drivers)
