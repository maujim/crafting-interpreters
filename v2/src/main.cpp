#include <cstdint>
#include <iostream>

#include "chunk/chunk.hpp"
#include "debug.hpp"
#include "vm.hpp"

int main(int argc, const char* argv[]) {
    VM vm;
    Chunk chunk;

    const auto constant_idx = chunk.add_constant(1.2);
    chunk.add_code(OpCodeKind::Constant, 123);
    chunk.add_code(constant_idx, 123);
    chunk.add_code(OpCodeKind::Return, 123);

    disassemble_chunk(chunk, "test chunk");

    vm.interpret(chunk);

    return 0;
}
