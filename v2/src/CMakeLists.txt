add_executable(
    clox
    main.cpp
    debug.cpp
    vm.cpp
    chunk/chunk.cpp
    chunk/opcode.cpp
)

target_compile_options(clox PRIVATE -Werror=switch -Wall -Wextra)
