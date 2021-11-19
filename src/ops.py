from enum import Enum


class Operation(Enum):
    LD = 0
    LD_16_BIT = 1
    ADD = 2
    ADC = 3
    SUB = 4
    SBC = 5
    AND = 6
    XOR = 7
    OR = 8
    CP = 9
    INC = 10
    DEC = 11
    DAA = 12
    CPL = 12
    ADD_16_BIT = 13
    INC_16_BIT = 14
    DEC_16_BIT = 15
    RLCA = 16
    RLA = 17
    RRCA = 18
    RRA = 19
    RLC = 20
    RL = 21
    RRC = 22
    RR = 23
    SLA = 24
    SWAP = 25
    SRA = 26
    SRL = 27
    BIT = 28
    SET = 29
    RES = 30
    CCF = 31
    SCF = 32
    NOP = 33
    HALT = 34
    STOP = 35
    DI = 36
    EI = 37
    JP = 38
    JR = 39
    CALL = 40
    RET = 41
    RETI = 42
    RST = 43


class OpCode:

    def __init__(self, code: int, operation: Operation, len: int, cycles: int, alt_cycles: int = None):
        self.code = code
        self.operation = operation
        self.len = len
        self.cycles = cycles
        self.alt_cycles = cycles if alt_cycles is None else alt_cycles


opcodes = [
    OpCode(0x00, Operation.NOP, 1, 4),
    OpCode(0x01, Operation.LD_16_BIT, 3, 12),
    OpCode(0x02, Operation.LD, 1, 8),
    OpCode(0x03, Operation.INC_16_BIT, 1, 8),
    OpCode(0x04, Operation.INC, 1, 4),
    OpCode(0x05, Operation.DEC, 1, 4),
    OpCode(0x06, Operation.LD, 2, 8),
    OpCode(0x07, Operation.RLCA, 1, 4),
    OpCode(0x08, Operation.LD_16_BIT, 3, 20),
    OpCode(0x09, Operation.ADD_16_BIT, 1, 8),
    OpCode(0x0A, Operation.LD, 1, 8),
    OpCode(0x0B, Operation.DEC_16_BIT, 1, 8),
    OpCode(0x0C, Operation.INC, 1, 4),
    OpCode(0x0D, Operation.DEC, 1, 4),
    OpCode(0x0E, Operation.LD, 2, 8),
    OpCode(0x0F, Operation.RRCA, 1, 4),

    OpCode(0x10, Operation.STOP, 2, 4),
    OpCode(0x11, Operation.LD_16_BIT, 3, 12),
    OpCode(0x12, Operation.LD, 1, 8),
    OpCode(0x13, Operation.INC_16_BIT, 1, 8),
    OpCode(0x14, Operation.INC, 1, 4),
    OpCode(0x15, Operation.DEC, 1, 4),
    OpCode(0x16, Operation.LD, 2, 8),
    OpCode(0x17, Operation.RLA, 1, 4),
    OpCode(0x18, Operation.JR, 2, 12),
    OpCode(0x19, Operation.ADD_16_BIT, 1, 8),
    OpCode(0x1A, Operation.LD, 1, 8),
    OpCode(0x1B, Operation.DEC_16_BIT, 1, 8),
    OpCode(0x1C, Operation.INC, 1, 4),
    OpCode(0x1D, Operation.DEC, 1, 4),
    OpCode(0x1E, Operation.LD, 2, 8),
    OpCode(0x1F, Operation.RRA, 1, 4),

    OpCode(0x20, Operation.JR, 2, 12, 8),
    OpCode(0x21, Operation.LD_16_BIT, 3, 12),
    OpCode(0x22, Operation.LD, 1, 8),
    OpCode(0x23, Operation.INC_16_BIT, 1, 8),
    OpCode(0x24, Operation.INC, 1, 4),
    OpCode(0x25, Operation.DEC, 1, 4),
    OpCode(0x26, Operation.LD, 2, 8),
    OpCode(0x27, Operation.DAA, 1, 4),
    OpCode(0x28, Operation.JR, 2, 12, 8),
    OpCode(0x29, Operation.ADD_16_BIT, 1, 8),
    OpCode(0x2A, Operation.LD, 1, 8),
    OpCode(0x2B, Operation.DEC_16_BIT, 1, 8),
    OpCode(0x2C, Operation.INC, 1, 4),
    OpCode(0x2D, Operation.DEC, 1, 4),
    OpCode(0x2E, Operation.LD, 2, 8),
    OpCode(0x2F, Operation.CPL, 1, 4),

    OpCode(0x30, Operation.JR, 2, 12, 8),
    OpCode(0x31, Operation.LD_16_BIT, 3, 12),
    OpCode(0x32, Operation.LD, 1, 8),
    OpCode(0x33, Operation.INC_16_BIT, 1, 8),
    OpCode(0x34, Operation.INC, 1, 4),
    OpCode(0x35, Operation.DEC, 1, 4),
    OpCode(0x36, Operation.LD, 2, 8),
    OpCode(0x37, Operation.SCF, 1, 4),
    OpCode(0x38, Operation.JR, 2, 12, 8),
    OpCode(0x39, Operation.ADD_16_BIT, 1, 8),
    OpCode(0x3A, Operation.LD, 1, 8),
    OpCode(0x3B, Operation.DEC_16_BIT, 1, 8),
    OpCode(0x3C, Operation.INC, 1, 4),
    OpCode(0x3D, Operation.DEC, 1, 4),
    OpCode(0x3E, Operation.LD, 2, 8),
    OpCode(0x3F, Operation.CCF, 1, 4),
]
