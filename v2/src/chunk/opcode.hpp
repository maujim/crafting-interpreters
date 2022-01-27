#pragma once

#include <cstdint>
#include <string>

enum class OpCodeKind : uint8_t
{
    None,
    Return,
    Constant,
};

class OpCode {
    OpCodeKind m_kind;
    uint8_t m_value;
    std::string m_name;

    public:
    OpCode(OpCodeKind kind);
    OpCode(uint8_t code);

    OpCodeKind kind() const { return m_kind; }
    uint8_t value() const { return m_value; }
    std::string name() const { return m_name; }
};
