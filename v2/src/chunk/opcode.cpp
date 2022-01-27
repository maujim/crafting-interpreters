#include "opcode.hpp"

OpCode::OpCode(OpCodeKind kind) :
    m_kind(kind), m_value(static_cast<uint8_t>(kind)) {
    switch (kind) {
        case OpCodeKind::None:
            m_name = "NONE";
            break;
        case OpCodeKind::Return:
            m_name = "RETURN";
            break;
        case OpCodeKind::Constant:
            m_name = "CONSTANT";
            break;
    }
}

OpCode::OpCode(uint8_t code) : OpCode::OpCode(OpCodeKind::None) {
    m_value = code;
}
