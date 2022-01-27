#pragma once

#include <string>

#include "chunk/chunk.hpp"

void disassemble_chunk(const Chunk& chunk, std::string name);
std::size_t disassemble_instruction(const Chunk& chunk, std::size_t offset);

std::size_t simple_instruction(OpCode opcode, std::size_t offset);
std::size_t constant_instruction(const Chunk& chunk, OpCode opcode, std::size_t offset);
