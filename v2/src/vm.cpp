#include "vm.hpp"

#include <iostream>

InterpretResult VM::interpret(const Chunk& chunk) {
    m_current_chunk = chunk;
    m_ip            = 0;
    return this->run();
}

InterpretResult VM::run() {
    while (true) {
        const auto& opcode = m_current_chunk[m_ip];
        switch (opcode.kind()) {
            case OpCodeKind::None:
                std::cout << "Unknown opcode " << opcode.value() << '\n';
                return offset + 1;
            case OpCodeKind::Return:
                return InterpretResult::Ok;
            case OpCodeKind::Constant:
                return constant_instruction(chunk, opcode, offset);
        }
    };
}
