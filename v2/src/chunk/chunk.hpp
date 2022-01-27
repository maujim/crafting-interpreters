#pragma once

#include <vector>

#include "opcode.hpp"

using LoxValue = double;

class Chunk {
    std::vector<OpCode> m_codes;
    std::vector<LoxValue> m_constants;
    std::vector<std::size_t> m_lines;

    public:
    void add_code(OpCode code, std::size_t line);
    std::size_t add_constant(LoxValue constant);

    std::size_t count() const;

    const std::vector<LoxValue>& constants() const;
    const std::vector<std::size_t>& lines() const;

    OpCode& operator[](std::size_t pos);
    const OpCode& operator[](std::size_t pos) const;
};
