#pragma once

#include "chunk/chunk.hpp"

enum class InterpretResult
{
    Ok,
    CompileError,
    RuntimeError,
};

class VM {
    Chunk m_current_chunk;
    std::size_t m_ip;

    public:
    InterpretResult interpret(const Chunk& chunk);
    InterpretResult run();
};
