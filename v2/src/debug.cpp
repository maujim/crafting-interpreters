#include "debug.hpp"

#include <iomanip>
#include <iostream>

void disassemble_chunk(const Chunk& chunk, std::string name) {
    std::cout << "== " << name << " ==\n";

    std::size_t offset = 0;
    while (offset < chunk.count()) {
        offset = disassemble_instruction(chunk, offset);
    }
}

std::size_t disassemble_instruction(const Chunk& chunk, std::size_t offset) {
    const auto prev_fill = std::cout.fill('0');
    std::cout << std::setw(4) << offset << ' ';
    std::cout.fill(prev_fill);

    const auto current_line = chunk.lines()[offset];
    const auto prev_line    = chunk.lines()[offset - 1];

    std::cout << std::setw(4);
    if (current_line == prev_line) {
        std::cout << '|';
    } else {
        std::cout << chunk.lines()[offset];
    }
    std::cout << ' ';

    const auto& opcode = chunk[offset];
    switch (opcode.kind()) {
        case OpCodeKind::None:
            std::cout << "Unknown opcode " << opcode.value() << '\n';
            return offset + 1;
        case OpCodeKind::Return:
            return simple_instruction(opcode, offset);
        case OpCodeKind::Constant:
            return constant_instruction(chunk, opcode, offset);
    }

    return offset + 1;
}

std::size_t simple_instruction(OpCode opcode, std::size_t offset) {
    std::cout << opcode.name() << '\n';
    return ++offset;
}

std::size_t constant_instruction(const Chunk& chunk, OpCode opcode,
                                 std::size_t offset) {

    const auto constant_idx = (chunk[offset + 1]).value();

    std::cout << std::left << std::setw(16) << opcode.name() << ' '
              << std::right << std::setw(4) << +constant_idx << " '"
              << chunk.m_constants[constant_idx] << "'\n";

    return offset + 2;
}
