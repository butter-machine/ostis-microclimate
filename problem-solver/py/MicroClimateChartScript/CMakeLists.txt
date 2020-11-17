file(GLOB_RECURSE SOURCES "*.cpp" "*.hpp")

add_library (MicroClimateChartService SHARED ${SOURCES})

target_include_directories(MicroClimateChartService PRIVATE ${SC_MEMORY_SRC})
target_link_libraries(MicroClimateChartService sc-memory)

add_dependencies(MicroClimateChartService sc-memory)

sc_codegen(MicroClimateChartService ${CMAKE_CURRENT_LIST_DIR})
