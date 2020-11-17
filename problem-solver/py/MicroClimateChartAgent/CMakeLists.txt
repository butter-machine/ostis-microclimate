file(GLOB_RECURSE SOURCES "*.cpp" "*.hpp")

add_library (MicroClimateChartModule SHARED ${SOURCES})

target_include_directories(MicroClimateChartModule PRIVATE ${SC_MEMORY_SRC})
target_link_libraries(MicroClimateChartModule sc-memory)

add_dependencies(MicroClimateChartModule sc-memory)

sc_codegen(MicroClimateChartModule ${CMAKE_CURRENT_LIST_DIR})
