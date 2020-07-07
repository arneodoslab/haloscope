# Install script for directory: /Users/panos/Documents/NYU/6.Extracurricular/11.Haloscope/0.Simulations/V1

# Set the install prefix
if(NOT DEFINED CMAKE_INSTALL_PREFIX)
  set(CMAKE_INSTALL_PREFIX "/usr/local")
endif()
string(REGEX REPLACE "/$" "" CMAKE_INSTALL_PREFIX "${CMAKE_INSTALL_PREFIX}")

# Set the install configuration name.
if(NOT DEFINED CMAKE_INSTALL_CONFIG_NAME)
  if(BUILD_TYPE)
    string(REGEX REPLACE "^[^A-Za-z0-9_]+" ""
           CMAKE_INSTALL_CONFIG_NAME "${BUILD_TYPE}")
  else()
    set(CMAKE_INSTALL_CONFIG_NAME "Release")
  endif()
  message(STATUS "Install configuration: \"${CMAKE_INSTALL_CONFIG_NAME}\"")
endif()

# Set the component getting installed.
if(NOT CMAKE_INSTALL_COMPONENT)
  if(COMPONENT)
    message(STATUS "Install component: \"${COMPONENT}\"")
    set(CMAKE_INSTALL_COMPONENT "${COMPONENT}")
  else()
    set(CMAKE_INSTALL_COMPONENT)
  endif()
endif()

# Is this installation the result of a crosscompile?
if(NOT DEFINED CMAKE_CROSSCOMPILING)
  set(CMAKE_CROSSCOMPILING "FALSE")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/bin" TYPE EXECUTABLE FILES "/Users/panos/Documents/NYU/6.Extracurricular/11.Haloscope/0.Simulations/V1/SLACtut")
  if(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/SLACtut" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/SLACtut")
    execute_process(COMMAND /usr/bin/install_name_tool
      -delete_rpath "/Users/panos/geant4.10.06-install/lib"
      "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/SLACtut")
    if(CMAKE_INSTALL_DO_STRIP)
      execute_process(COMMAND "/Library/Developer/CommandLineTools/usr/bin/strip" -u -r "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/SLACtut")
    endif()
  endif()
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/SLACtut" TYPE FILE FILES
    "/Users/panos/Documents/NYU/6.Extracurricular/11.Haloscope/0.Simulations/V1/icons.mac"
    "/Users/panos/Documents/NYU/6.Extracurricular/11.Haloscope/0.Simulations/V1/gui.mac"
    "/Users/panos/Documents/NYU/6.Extracurricular/11.Haloscope/0.Simulations/V1/run.png"
    "/Users/panos/Documents/NYU/6.Extracurricular/11.Haloscope/0.Simulations/V1/init.mac"
    "/Users/panos/Documents/NYU/6.Extracurricular/11.Haloscope/0.Simulations/V1/init_vis.mac"
    "/Users/panos/Documents/NYU/6.Extracurricular/11.Haloscope/0.Simulations/V1/run1.mac"
    "/Users/panos/Documents/NYU/6.Extracurricular/11.Haloscope/0.Simulations/V1/run2.mac"
    "/Users/panos/Documents/NYU/6.Extracurricular/11.Haloscope/0.Simulations/V1/vis.mac"
    "/Users/panos/Documents/NYU/6.Extracurricular/11.Haloscope/0.Simulations/V1/scoring.mac"
    "/Users/panos/Documents/NYU/6.Extracurricular/11.Haloscope/0.Simulations/V1/draw.mac"
    "/Users/panos/Documents/NYU/6.Extracurricular/11.Haloscope/0.Simulations/V1/drawSlice.mac"
    )
endif()

if(CMAKE_INSTALL_COMPONENT)
  set(CMAKE_INSTALL_MANIFEST "install_manifest_${CMAKE_INSTALL_COMPONENT}.txt")
else()
  set(CMAKE_INSTALL_MANIFEST "install_manifest.txt")
endif()

string(REPLACE ";" "\n" CMAKE_INSTALL_MANIFEST_CONTENT
       "${CMAKE_INSTALL_MANIFEST_FILES}")
file(WRITE "/Users/panos/Documents/NYU/6.Extracurricular/11.Haloscope/0.Simulations/V1/${CMAKE_INSTALL_MANIFEST}"
     "${CMAKE_INSTALL_MANIFEST_CONTENT}")
