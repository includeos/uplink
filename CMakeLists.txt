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

include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)

option(LIVEUPDATE "Enable liveupdate" ON)
option(TLS "Enable secure connections" ON)
option(UPLINK_LOG "Enable logging over uplink" ON)

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
  src/transport.cpp
  src/ws_uplink.cpp
  src/register_plugin.cpp
  src/config.cpp
  src/uplink.cpp
  )

set(HDRS
  include/uplink/common.hpp
  include/uplink/config.hpp
  include/uplink/log.hpp
  include/uplink/transport.hpp
  include/uplink/uplink.hpp # including this pulls in the rest
  include/uplink/ws_uplink.hpp
  )

# Uplink library
add_library(${LIBRARY_NAME} STATIC ${SOURCES})
if (LIVEUPDATE)
  set_target_properties(${LIBRARY_NAME} PROPERTIES COMPILE_DEFINITIONS "LIVEUPDATE")
endif()


# Install headers (?)
set_target_properties(${LIBRARY_NAME} PROPERTIES PUBLIC_HEADER "${HDRS}")

install(TARGETS ${LIBRARY_NAME}
        ARCHIVE DESTINATION plugins
        PUBLIC_HEADER DESTINATION include/uplink
  )

# Uplink log driver
if(UPLINK_LOG)
  add_library(uplink_log STATIC src/uplink_log.cpp)
  install(TARGETS uplink_log ARCHIVE DESTINATION drivers)
endif()

