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
    POP = 44
    PUSH = 45
    PREFIX = 46
    LDH = 47


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

    OpCode(0x40, Operation.LD, 1, 4),
    OpCode(0x41, Operation.LD, 1, 4),
    OpCode(0x42, Operation.LD, 1, 4),
    OpCode(0x43, Operation.LD, 1, 4),
    OpCode(0x44, Operation.LD, 1, 4),
    OpCode(0x45, Operation.LD, 1, 4),
    OpCode(0x46, Operation.LD, 1, 8),
    OpCode(0x47, Operation.LD, 1, 4),
    OpCode(0x48, Operation.LD, 1, 4),
    OpCode(0x49, Operation.LD, 1, 4),
    OpCode(0x4A, Operation.LD, 1, 4),
    OpCode(0x4B, Operation.LD, 1, 4),
    OpCode(0x4C, Operation.LD, 1, 4),
    OpCode(0x4D, Operation.LD, 1, 4),
    OpCode(0x4E, Operation.LD, 1, 8),
    OpCode(0x4F, Operation.LD, 1, 4),

    OpCode(0x50, Operation.LD, 1, 4),
    OpCode(0x51, Operation.LD, 1, 4),
    OpCode(0x52, Operation.LD, 1, 4),
    OpCode(0x53, Operation.LD, 1, 4),
    OpCode(0x54, Operation.LD, 1, 4),
    OpCode(0x55, Operation.LD, 1, 4),
    OpCode(0x56, Operation.LD, 1, 8),
    OpCode(0x57, Operation.LD, 1, 4),
    OpCode(0x58, Operation.LD, 1, 4),
    OpCode(0x59, Operation.LD, 1, 4),
    OpCode(0x5A, Operation.LD, 1, 4),
    OpCode(0x5B, Operation.LD, 1, 4),
    OpCode(0x5C, Operation.LD, 1, 4),
    OpCode(0x5D, Operation.LD, 1, 4),
    OpCode(0x5E, Operation.LD, 1, 8),
    OpCode(0x5F, Operation.LD, 1, 4),

    OpCode(0x60, Operation.LD, 1, 4),
    OpCode(0x61, Operation.LD, 1, 4),
    OpCode(0x62, Operation.LD, 1, 4),
    OpCode(0x63, Operation.LD, 1, 4),
    OpCode(0x64, Operation.LD, 1, 4),
    OpCode(0x65, Operation.LD, 1, 4),
    OpCode(0x66, Operation.LD, 1, 8),
    OpCode(0x67, Operation.LD, 1, 4),
    OpCode(0x68, Operation.LD, 1, 4),
    OpCode(0x69, Operation.LD, 1, 4),
    OpCode(0x6A, Operation.LD, 1, 4),
    OpCode(0x6B, Operation.LD, 1, 4),
    OpCode(0x6C, Operation.LD, 1, 4),
    OpCode(0x6D, Operation.LD, 1, 4),
    OpCode(0x6E, Operation.LD, 1, 8),
    OpCode(0x6F, Operation.LD, 1, 4),

    OpCode(0x70, Operation.LD, 1, 8),
    OpCode(0x71, Operation.LD, 1, 8),
    OpCode(0x72, Operation.LD, 1, 8),
    OpCode(0x73, Operation.LD, 1, 8),
    OpCode(0x74, Operation.LD, 1, 8),
    OpCode(0x75, Operation.LD, 1, 8),
    OpCode(0x76, Operation.HALT, 1, 4),
    OpCode(0x77, Operation.LD, 1, 8),
    OpCode(0x78, Operation.LD, 1, 4),
    OpCode(0x79, Operation.LD, 1, 4),
    OpCode(0x7A, Operation.LD, 1, 4),
    OpCode(0x7B, Operation.LD, 1, 4),
    OpCode(0x7C, Operation.LD, 1, 4),
    OpCode(0x7D, Operation.LD, 1, 4),
    OpCode(0x7E, Operation.LD, 1, 8),
    OpCode(0x7F, Operation.LD, 1, 4),

    OpCode(0x80, Operation.ADD, 1, 4),
    OpCode(0x81, Operation.ADD, 1, 4),
    OpCode(0x82, Operation.ADD, 1, 4),
    OpCode(0x83, Operation.ADD, 1, 4),
    OpCode(0x84, Operation.ADD, 1, 4),
    OpCode(0x85, Operation.ADD, 1, 4),
    OpCode(0x86, Operation.ADD, 1, 8),
    OpCode(0x87, Operation.ADD, 1, 4),
    OpCode(0x88, Operation.ADC, 1, 4),
    OpCode(0x89, Operation.ADC, 1, 4),
    OpCode(0x8A, Operation.ADC, 1, 4),
    OpCode(0x8B, Operation.ADC, 1, 4),
    OpCode(0x8C, Operation.ADC, 1, 4),
    OpCode(0x8D, Operation.ADC, 1, 4),
    OpCode(0x8E, Operation.ADC, 1, 8),
    OpCode(0x8F, Operation.ADC, 1, 4),

    OpCode(0x90, Operation.SUB, 1, 4),
    OpCode(0x91, Operation.SUB, 1, 4),
    OpCode(0x92, Operation.SUB, 1, 4),
    OpCode(0x93, Operation.SUB, 1, 4),
    OpCode(0x94, Operation.SUB, 1, 4),
    OpCode(0x95, Operation.SUB, 1, 4),
    OpCode(0x96, Operation.SUB, 1, 8),
    OpCode(0x97, Operation.SUB, 1, 4),
    OpCode(0x98, Operation.SBC, 1, 4),
    OpCode(0x99, Operation.SBC, 1, 4),
    OpCode(0x9A, Operation.SBC, 1, 4),
    OpCode(0x9B, Operation.SBC, 1, 4),
    OpCode(0x9C, Operation.SBC, 1, 4),
    OpCode(0x9D, Operation.SBC, 1, 4),
    OpCode(0x9E, Operation.SBC, 1, 8),
    OpCode(0x9F, Operation.SBC, 1, 4),

    OpCode(0xA0, Operation.AND, 1, 4),
    OpCode(0xA1, Operation.AND, 1, 4),
    OpCode(0xA2, Operation.AND, 1, 4),
    OpCode(0xA3, Operation.AND, 1, 4),
    OpCode(0xA4, Operation.AND, 1, 4),
    OpCode(0xA5, Operation.AND, 1, 4),
    OpCode(0xA6, Operation.AND, 1, 8),
    OpCode(0xA7, Operation.AND, 1, 4),
    OpCode(0xA8, Operation.XOR, 1, 4),
    OpCode(0xA9, Operation.XOR, 1, 4),
    OpCode(0xAA, Operation.XOR, 1, 4),
    OpCode(0xAB, Operation.XOR, 1, 4),
    OpCode(0xAC, Operation.XOR, 1, 4),
    OpCode(0xAD, Operation.XOR, 1, 4),
    OpCode(0xAE, Operation.XOR, 1, 8),
    OpCode(0xAF, Operation.XOR, 1, 4),

    OpCode(0xB0, Operation.OR, 1, 4),
    OpCode(0xB1, Operation.OR, 1, 4),
    OpCode(0xB2, Operation.OR, 1, 4),
    OpCode(0xB3, Operation.OR, 1, 4),
    OpCode(0xB4, Operation.OR, 1, 4),
    OpCode(0xB5, Operation.OR, 1, 4),
    OpCode(0xB6, Operation.OR, 1, 8),
    OpCode(0xB7, Operation.OR, 1, 4),
    OpCode(0xB8, Operation.CP, 1, 4),
    OpCode(0xB9, Operation.CP, 1, 4),
    OpCode(0xBA, Operation.CP, 1, 4),
    OpCode(0xBB, Operation.CP, 1, 4),
    OpCode(0xBC, Operation.CP, 1, 4),
    OpCode(0xBD, Operation.CP, 1, 4),
    OpCode(0xBE, Operation.CP, 1, 8),
    OpCode(0xBF, Operation.CP, 1, 4),

    OpCode(0xC0, Operation.RET, 1, 20, 8),
    OpCode(0xC1, Operation.POP, 1, 12),
    OpCode(0xC2, Operation.JP, 3, 16, 12),
    OpCode(0xC3, Operation.JP, 3, 16),
    OpCode(0xC4, Operation.CALL, 3, 24, 12),
    OpCode(0xC5, Operation.PUSH, 1, 16),
    OpCode(0xC6, Operation.ADD, 2, 8),
    OpCode(0xC7, Operation.RST, 1, 16),
    OpCode(0xC8, Operation.RET, 1, 20, 8),
    OpCode(0xC9, Operation.RET, 1, 16),
    OpCode(0xCA, Operation.JP, 3, 16, 12),
    OpCode(0xCB, Operation.PREFIX, 1, 4),
    OpCode(0xCC, Operation.CALL, 3, 24, 12),
    OpCode(0xCD, Operation.CALL, 3, 24),
    OpCode(0xCE, Operation.ADC, 2, 8),
    OpCode(0xCF, Operation.RST, 1, 16),

    OpCode(0xD0, Operation.RET, 1, 20, 8),
    OpCode(0xD1, Operation.POP, 1, 12),
    OpCode(0xD2, Operation.JP, 3, 16, 12),
    # OpCode(0xD3, Operation.JP, 3, 16),
    OpCode(0xD4, Operation.CALL, 3, 24, 12),
    OpCode(0xD5, Operation.PUSH, 1, 16),
    OpCode(0xD6, Operation.SUB, 2, 8),
    OpCode(0xD7, Operation.RST, 1, 16),
    OpCode(0xD8, Operation.RET, 1, 20, 8),
    OpCode(0xD9, Operation.RETI, 1, 16),
    OpCode(0xDA, Operation.JP, 3, 16, 12),
    # OpCode(0xDB, Operation.PREFIX, 1, 4),
    OpCode(0xDC, Operation.CALL, 3, 24, 12),
    # OpCode(0xDD, Operation.CALL, 3, 24),
    OpCode(0xDE, Operation.SBC, 2, 8),
    OpCode(0xDF, Operation.RST, 1, 16),

    OpCode(0xE0, Operation.LDH, 2, 12),
    OpCode(0xE1, Operation.POP, 1, 12),
    OpCode(0xE2, Operation.LD, 1, 8),
    # OpCode(0xE3, Operation.JP, 3, 16),
    # OpCode(0xE4, Operation.CALL, 3, 24, 12),
    OpCode(0xE5, Operation.PUSH, 1, 16),
    OpCode(0xE6, Operation.AND, 2, 8),
    OpCode(0xE7, Operation.RST, 1, 16),
    OpCode(0xE8, Operation.ADD, 1, 2, 16),
    OpCode(0xE9, Operation.JP, 1, 4),
    OpCode(0xEA, Operation.LD, 3, 16),
    # OpCode(0xEB, Operation.PREFIX, 1, 4),
    # OpCode(0xEC, Operation.CALL, 3, 24, 12),
    # OpCode(0xED, Operation.CALL, 3, 24),
    OpCode(0xEE, Operation.XOR, 2, 8),
    OpCode(0xEF, Operation.RST, 1, 16),

    OpCode(0xF0, Operation.LDH, 2, 12),
    OpCode(0xF1, Operation.POP, 1, 12),
    OpCode(0xF2, Operation.LD, 1, 8),
    OpCode(0xF3, Operation.DI, 1, 4),
    # OpCode(0xF4, Operation.CALL, 3, 24, 12),
    OpCode(0xF5, Operation.PUSH, 1, 16),
    OpCode(0xF6, Operation.OR, 2, 8),
    OpCode(0xF7, Operation.RST, 1, 16),
    OpCode(0xF8, Operation.LD, 1, 2, 12),
    OpCode(0xF9, Operation.LD, 1, 8),
    OpCode(0xFA, Operation.LD, 3, 16),
    OpCode(0xFB, Operation.EI, 1, 4),
    # OpCode(0xFC, Operation.CALL, 3, 24, 12),
    # OpCode(0xFD, Operation.CALL, 3, 24),
    OpCode(0xFE, Operation.CP, 2, 8),
    OpCode(0xFF, Operation.RST, 1, 16),
]
