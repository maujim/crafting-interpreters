#include "chunk.hpp"

void Chunk::add_code(OpCode code, std::size_t line) {
    m_codes.push_back(code);
    m_lines.push_back(line);
}

std::size_t Chunk::add_constant(LoxValue constant) {
    m_constants.push_back(constant);
    return m_constants.size() - 1;
}

std::size_t Chunk::count() const {
    return m_codes.size();
}

const std::vector<LoxValue>& Chunk::constants() const {
    return m_constants;
}

const std::vector<std::size_t>& Chunk::lines() const {
    return m_lines;
}

OpCode& Chunk::operator[](std::size_t pos) {
    return m_codes[pos];
}

const OpCode& Chunk::operator[](std::size_t pos) const {
    return m_codes[pos];
}
