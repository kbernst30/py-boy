from enum import Enum


class Operation(Enum):
    LD = 0
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

    def __init__(self, code: int, mnemonic: str, operation: Operation, len: int, cycles: int, alt_cycles: int = None):
        self.code = code
        self.mnemonic = mnemonic
        self.operation = operation
        self.len = len
        self.cycles = cycles
        self.alt_cycles = cycles if alt_cycles is None else alt_cycles


opcodes = [
    OpCode(0x00, "NOP", Operation.NOP, 1, 4),
    OpCode(0x01, "LD BC, d16", Operation.LD, 3, 12),
    OpCode(0x02, "LD (BC), A", Operation.LD, 1, 8),
    OpCode(0x03, "INC BC", Operation.INC_16_BIT, 1, 8),
    OpCode(0x04, "INC B", Operation.INC, 1, 4),
    OpCode(0x05, "DEC B", Operation.DEC, 1, 4),
    OpCode(0x06, "LD B, d8", Operation.LD, 2, 8),
    OpCode(0x07, "RLCA", Operation.RLCA, 1, 4),
    OpCode(0x08, "LD (a16), SP", Operation.LD, 3, 20),
    OpCode(0x09, "ADD HL, BC", Operation.ADD_16_BIT, 1, 8),
    OpCode(0x0A, "LD A, (BC)", Operation.LD, 1, 8),
    OpCode(0x0B, "DEC, BC", Operation.DEC_16_BIT, 1, 8),
    OpCode(0x0C, "INC C", Operation.INC, 1, 4),
    OpCode(0x0D, "DEC C", Operation.DEC, 1, 4),
    OpCode(0x0E, "LD C, d8", Operation.LD, 2, 8),
    OpCode(0x0F, "RRCA", Operation.RRCA, 1, 4),

    OpCode(0x10, "STOP", Operation.STOP, 2, 4),
    OpCode(0x11, "LD DE, d16", Operation.LD, 3, 12),
    OpCode(0x12, "LD (DE), A", Operation.LD, 1, 8),
    OpCode(0x13, "INC DE", Operation.INC_16_BIT, 1, 8),
    OpCode(0x14, "INC D", Operation.INC, 1, 4),
    OpCode(0x15, "DEC D", Operation.DEC, 1, 4),
    OpCode(0x16, "LD D, d8", Operation.LD, 2, 8),
    OpCode(0x17, "RLA", Operation.RLA, 1, 4),
    OpCode(0x18, "JR r8", Operation.JR, 2, 12),
    OpCode(0x19, "ADD HL, DE", Operation.ADD_16_BIT, 1, 8),
    OpCode(0x1A, "LD A, (DE)", Operation.LD, 1, 8),
    OpCode(0x1B, "DEC DE", Operation.DEC_16_BIT, 1, 8),
    OpCode(0x1C, "INC E", Operation.INC, 1, 4),
    OpCode(0x1D, "DEC E", Operation.DEC, 1, 4),
    OpCode(0x1E, "LD E, d8", Operation.LD, 2, 8),
    OpCode(0x1F, "RRA", Operation.RRA, 1, 4),

    OpCode(0x20, "JR NZ, r8", Operation.JR, 2, 12, 8),
    OpCode(0x21, "LD HL, d16", Operation.LD, 3, 12),
    OpCode(0x22, "LD (HL+), A", Operation.LD, 1, 8),
    OpCode(0x23, "INC HL", Operation.INC_16_BIT, 1, 8),
    OpCode(0x24, "INC H", Operation.INC, 1, 4),
    OpCode(0x25, "DEC H", Operation.DEC, 1, 4),
    OpCode(0x26, "LD H, d8", Operation.LD, 2, 8),
    OpCode(0x27, "DAA", Operation.DAA, 1, 4),
    OpCode(0x28, "JR Z, r8", Operation.JR, 2, 12, 8),
    OpCode(0x29, "ADD HL, HL", Operation.ADD_16_BIT, 1, 8),
    OpCode(0x2A, "LD A, (HL+)", Operation.LD, 1, 8),
    OpCode(0x2B, "DEC HL", Operation.DEC_16_BIT, 1, 8),
    OpCode(0x2C, "INC L", Operation.INC, 1, 4),
    OpCode(0x2D, "DEC L", Operation.DEC, 1, 4),
    OpCode(0x2E, "LD L, d8", Operation.LD, 2, 8),
    OpCode(0x2F, "CPL", Operation.CPL, 1, 4),

    OpCode(0x30, "JR NC, r8", Operation.JR, 2, 12, 8),
    OpCode(0x31, "LD SP, d16", Operation.LD, 3, 12),
    OpCode(0x32, "LD (HL-), A", Operation.LD, 1, 8),
    OpCode(0x33, "INC SP", Operation.INC_16_BIT, 1, 8),
    OpCode(0x34, "INC (HL)", Operation.INC, 1, 4),
    OpCode(0x35, "DEC (HL)", Operation.DEC, 1, 4),
    OpCode(0x36, "LD (HL), d8", Operation.LD, 2, 8),
    OpCode(0x37, "SCF", Operation.SCF, 1, 4),
    OpCode(0x38, "JR C, r8", Operation.JR, 2, 12, 8),
    OpCode(0x39, "ADD HL, SP", Operation.ADD_16_BIT, 1, 8),
    OpCode(0x3A, "LD A, (HL-)", Operation.LD, 1, 8),
    OpCode(0x3B, "DEC SP", Operation.DEC_16_BIT, 1, 8),
    OpCode(0x3C, "INC A", Operation.INC, 1, 4),
    OpCode(0x3D, "DEC A", Operation.DEC, 1, 4),
    OpCode(0x3E, "LD A, d8", Operation.LD, 2, 8),
    OpCode(0x3F, "CCF", Operation.CCF, 1, 4),

    OpCode(0x40, "LD B, B", Operation.LD, 1, 4),
    OpCode(0x41, "LD B, C", Operation.LD, 1, 4),
    OpCode(0x42, "LD B, D", Operation.LD, 1, 4),
    OpCode(0x43, "LD B, E", Operation.LD, 1, 4),
    OpCode(0x44, "LD B, H", Operation.LD, 1, 4),
    OpCode(0x45, "LD B, L", Operation.LD, 1, 4),
    OpCode(0x46, "LD B, (HL)", Operation.LD, 1, 8),
    OpCode(0x47, "LD B, A", Operation.LD, 1, 4),
    OpCode(0x48, "LD C, B", Operation.LD, 1, 4),
    OpCode(0x49, "LD C, C", Operation.LD, 1, 4),
    OpCode(0x4A, "LD C, D", Operation.LD, 1, 4),
    OpCode(0x4B, "LD C, E", Operation.LD, 1, 4),
    OpCode(0x4C, "LD C, H", Operation.LD, 1, 4),
    OpCode(0x4D, "LD C, L", Operation.LD, 1, 4),
    OpCode(0x4E, "LD C, (HL)", Operation.LD, 1, 8),
    OpCode(0x4F, "LD C, A", Operation.LD, 1, 4),

    OpCode(0x50, "LD D, B", Operation.LD, 1, 4),
    OpCode(0x51, "LD D, C", Operation.LD, 1, 4),
    OpCode(0x52, "LD D, D", Operation.LD, 1, 4),
    OpCode(0x53, "LD D, E", Operation.LD, 1, 4),
    OpCode(0x54, "LD D, H", Operation.LD, 1, 4),
    OpCode(0x55, "LD D, L", Operation.LD, 1, 4),
    OpCode(0x56, "LD D, (HL)", Operation.LD, 1, 8),
    OpCode(0x57, "LD D, A", Operation.LD, 1, 4),
    OpCode(0x58, "LD E, B", Operation.LD, 1, 4),
    OpCode(0x59, "LD E, C", Operation.LD, 1, 4),
    OpCode(0x5A, "LD E, D", Operation.LD, 1, 4),
    OpCode(0x5B, "LD E, E", Operation.LD, 1, 4),
    OpCode(0x5C, "LD E, H", Operation.LD, 1, 4),
    OpCode(0x5D, "LD E, L", Operation.LD, 1, 4),
    OpCode(0x5E, "LD E, (HL)", Operation.LD, 1, 8),
    OpCode(0x5F, "LD E, A", Operation.LD, 1, 4),

    OpCode(0x60, "LD H, B", Operation.LD, 1, 4),
    OpCode(0x61, "LD H, C", Operation.LD, 1, 4),
    OpCode(0x62, "LD H, D", Operation.LD, 1, 4),
    OpCode(0x63, "LD H, E", Operation.LD, 1, 4),
    OpCode(0x64, "LD H, H", Operation.LD, 1, 4),
    OpCode(0x65, "LD H, L", Operation.LD, 1, 4),
    OpCode(0x66, "LD H, (HL)", Operation.LD, 1, 8),
    OpCode(0x67, "LD H, A", Operation.LD, 1, 4),
    OpCode(0x68, "LD L, B", Operation.LD, 1, 4),
    OpCode(0x69, "LD L, C", Operation.LD, 1, 4),
    OpCode(0x6A, "LD L, D", Operation.LD, 1, 4),
    OpCode(0x6B, "LD L, E", Operation.LD, 1, 4),
    OpCode(0x6C, "LD L, H", Operation.LD, 1, 4),
    OpCode(0x6D, "LD L, L", Operation.LD, 1, 4),
    OpCode(0x6E, "LD L, (HL)", Operation.LD, 1, 8),
    OpCode(0x6F, "LD L, A", Operation.LD, 1, 4),

    OpCode(0x70, "LD (HL), B", Operation.LD, 1, 8),
    OpCode(0x71, "LD (HL), C", Operation.LD, 1, 8),
    OpCode(0x72, "LD (HL), D", Operation.LD, 1, 8),
    OpCode(0x73, "LD (HL), E", Operation.LD, 1, 8),
    OpCode(0x74, "LD (HL), H", Operation.LD, 1, 8),
    OpCode(0x75, "LD (HL), L", Operation.LD, 1, 8),
    OpCode(0x76, "HALT", Operation.HALT, 1, 4),
    OpCode(0x77, "LD (HL), A", Operation.LD, 1, 8),
    OpCode(0x78, "LD A, B", Operation.LD, 1, 4),
    OpCode(0x79, "LD A, C", Operation.LD, 1, 4),
    OpCode(0x7A, "LD A, D", Operation.LD, 1, 4),
    OpCode(0x7B, "LD A, E", Operation.LD, 1, 4),
    OpCode(0x7C, "LD A, H", Operation.LD, 1, 4),
    OpCode(0x7D, "LD A, L", Operation.LD, 1, 4),
    OpCode(0x7E, "LD A, (HL)", Operation.LD, 1, 8),
    OpCode(0x7F, "LD A, A", Operation.LD, 1, 4),

    OpCode(0x80, "ADD A, B", Operation.ADD, 1, 4),
    OpCode(0x81, "ADD A, C", Operation.ADD, 1, 4),
    OpCode(0x82, "ADD A, D", Operation.ADD, 1, 4),
    OpCode(0x83, "ADD A, E", Operation.ADD, 1, 4),
    OpCode(0x84, "ADD A, H", Operation.ADD, 1, 4),
    OpCode(0x85, "ADD A, L", Operation.ADD, 1, 4),
    OpCode(0x86, "ADD A, (HL)", Operation.ADD, 1, 8),
    OpCode(0x87, "ADD A, A", Operation.ADD, 1, 4),
    OpCode(0x88, "ADC A, B", Operation.ADC, 1, 4),
    OpCode(0x89, "ADC A, C", Operation.ADC, 1, 4),
    OpCode(0x8A, "ADC A, D", Operation.ADC, 1, 4),
    OpCode(0x8B, "ADC A, E", Operation.ADC, 1, 4),
    OpCode(0x8C, "ADC A, H", Operation.ADC, 1, 4),
    OpCode(0x8D, "ADC A, L", Operation.ADC, 1, 4),
    OpCode(0x8E, "ADC A, (HL)", Operation.ADC, 1, 8),
    OpCode(0x8F, "ADC A, A", Operation.ADC, 1, 4),

    OpCode(0x90, "SUB B", Operation.SUB, 1, 4),
    OpCode(0x91, "SUB C", Operation.SUB, 1, 4),
    OpCode(0x92, "SUB D", Operation.SUB, 1, 4),
    OpCode(0x93, "SUB E", Operation.SUB, 1, 4),
    OpCode(0x94, "SUB H", Operation.SUB, 1, 4),
    OpCode(0x95, "SUB L", Operation.SUB, 1, 4),
    OpCode(0x96, "SUB (HL)", Operation.SUB, 1, 8),
    OpCode(0x97, "SUB A", Operation.SUB, 1, 4),
    OpCode(0x98, "SBC A, B", Operation.SBC, 1, 4),
    OpCode(0x99, "SBC A, C", Operation.SBC, 1, 4),
    OpCode(0x9A, "SBC A, D", Operation.SBC, 1, 4),
    OpCode(0x9B, "SBC A, E", Operation.SBC, 1, 4),
    OpCode(0x9C, "SBC A, H", Operation.SBC, 1, 4),
    OpCode(0x9D, "SBC A, L", Operation.SBC, 1, 4),
    OpCode(0x9E, "SBC A, (HL)", Operation.SBC, 1, 8),
    OpCode(0x9F, "SBC A, A", Operation.SBC, 1, 4),

    OpCode(0xA0, "AND B", Operation.AND, 1, 4),
    OpCode(0xA1, "AND C", Operation.AND, 1, 4),
    OpCode(0xA2, "AND D", Operation.AND, 1, 4),
    OpCode(0xA3, "AND E", Operation.AND, 1, 4),
    OpCode(0xA4, "AND H", Operation.AND, 1, 4),
    OpCode(0xA5, "AND L", Operation.AND, 1, 4),
    OpCode(0xA6, "AND (HL)", Operation.AND, 1, 8),
    OpCode(0xA7, "AND A", Operation.AND, 1, 4),
    OpCode(0xA8, "XOR B", Operation.XOR, 1, 4),
    OpCode(0xA9, "XOR C", Operation.XOR, 1, 4),
    OpCode(0xAA, "XOR D", Operation.XOR, 1, 4),
    OpCode(0xAB, "XOR E", Operation.XOR, 1, 4),
    OpCode(0xAC, "XOR H", Operation.XOR, 1, 4),
    OpCode(0xAD, "XOR L", Operation.XOR, 1, 4),
    OpCode(0xAE, "XOR (HL)", Operation.XOR, 1, 8),
    OpCode(0xAF, "XOR A", Operation.XOR, 1, 4),

    OpCode(0xB0, "OR B", Operation.OR, 1, 4),
    OpCode(0xB1, "OR C", Operation.OR, 1, 4),
    OpCode(0xB2, "OR D", Operation.OR, 1, 4),
    OpCode(0xB3, "OR E", Operation.OR, 1, 4),
    OpCode(0xB4, "OR H", Operation.OR, 1, 4),
    OpCode(0xB5, "OR L", Operation.OR, 1, 4),
    OpCode(0xB6, "OR (HL)", Operation.OR, 1, 8),
    OpCode(0xB7, "OR A", Operation.OR, 1, 4),
    OpCode(0xB8, "CP B", Operation.CP, 1, 4),
    OpCode(0xB9, "CP C", Operation.CP, 1, 4),
    OpCode(0xBA, "CP D", Operation.CP, 1, 4),
    OpCode(0xBB, "CP E", Operation.CP, 1, 4),
    OpCode(0xBC, "CP H", Operation.CP, 1, 4),
    OpCode(0xBD, "CP L", Operation.CP, 1, 4),
    OpCode(0xBE, "CP (HL)", Operation.CP, 1, 8),
    OpCode(0xBF, "CP A", Operation.CP, 1, 4),

    OpCode(0xC0, "RET NZ", Operation.RET, 1, 20, 8),
    OpCode(0xC1, "POP BC", Operation.POP, 1, 12),
    OpCode(0xC2, "JP NZ, a16", Operation.JP, 3, 16, 12),
    OpCode(0xC3, "JP a16", Operation.JP, 3, 16),
    OpCode(0xC4, "CALL NZ, a16", Operation.CALL, 3, 24, 12),
    OpCode(0xC5, "PUSH BC", Operation.PUSH, 1, 16),
    OpCode(0xC6, "ADD A, d8", Operation.ADD, 2, 8),
    OpCode(0xC7, "RST 00H", Operation.RST, 1, 16),
    OpCode(0xC8, "RET Z", Operation.RET, 1, 20, 8),
    OpCode(0xC9, "RET", Operation.RET, 1, 16),
    OpCode(0xCA, "JP Z a16", Operation.JP, 3, 16, 12),
    OpCode(0xCB, "PREFIX", Operation.PREFIX, 1, 4),
    OpCode(0xCC, "CALL Z, a16", Operation.CALL, 3, 24, 12),
    OpCode(0xCD, "CALL a16", Operation.CALL, 3, 24),
    OpCode(0xCE, "ADC A, d8", Operation.ADC, 2, 8),
    OpCode(0xCF, "RST 08H", Operation.RST, 1, 16),

    OpCode(0xD0, "RET NZ", Operation.RET, 1, 20, 8),
    OpCode(0xD1, "POP DE", Operation.POP, 1, 12),
    OpCode(0xD2, "JP NC, a16", Operation.JP, 3, 16, 12),
    # OpCode(0xD3, Operation.JP, 3, 16),
    OpCode(0xD4, "CALL NC, a16", Operation.CALL, 3, 24, 12),
    OpCode(0xD5, "PUSH DE", Operation.PUSH, 1, 16),
    OpCode(0xD6, "SUB d8", Operation.SUB, 2, 8),
    OpCode(0xD7, "RST 10H", Operation.RST, 1, 16),
    OpCode(0xD8, "RET C", Operation.RET, 1, 20, 8),
    OpCode(0xD9, "RETI", Operation.RETI, 1, 16),
    OpCode(0xDA, "JP C, a16", Operation.JP, 3, 16, 12),
    # OpCode(0xDB, Operation.PREFIX, 1, 4),
    OpCode(0xDC, "CALL C, a16", Operation.CALL, 3, 24, 12),
    # OpCode(0xDD, Operation.CALL, 3, 24),
    OpCode(0xDE, "SBC A, d8", Operation.SBC, 2, 8),
    OpCode(0xDF, "RST 18H", Operation.RST, 1, 16),

    OpCode(0xE0, "LDH (a8), A", Operation.LDH, 2, 12),
    OpCode(0xE1, "POP HL", Operation.POP, 1, 12),
    OpCode(0xE2, "LD (C), A", Operation.LD, 1, 8),
    # OpCode(0xE3, Operation.JP, 3, 16),
    # OpCode(0xE4, Operation.CALL, 3, 24, 12),
    OpCode(0xE5, "PUSH HL", Operation.PUSH, 1, 16),
    OpCode(0xE6, "AND d8", Operation.AND, 2, 8),
    OpCode(0xE7, "RST 20H", Operation.RST, 1, 16),
    OpCode(0xE8, "ADD SP, r8", Operation.ADD, 1, 2, 16),
    OpCode(0xE9, "JP HL", Operation.JP, 1, 4),
    OpCode(0xEA, "LD (a16), A", Operation.LD, 3, 16),
    # OpCode(0xEB, Operation.PREFIX, 1, 4),
    # OpCode(0xEC, Operation.CALL, 3, 24, 12),
    # OpCode(0xED, Operation.CALL, 3, 24),
    OpCode(0xEE, "XOR d8", Operation.XOR, 2, 8),
    OpCode(0xEF, "RST 28H", Operation.RST, 1, 16),

    OpCode(0xF0, "LDH A, (d8)", Operation.LDH, 2, 12),
    OpCode(0xF1, "POP AF", Operation.POP, 1, 12),
    OpCode(0xF2, "LD A, (C)", Operation.LD, 1, 8),
    OpCode(0xF3, "DI", Operation.DI, 1, 4),
    # OpCode(0xF4, Operation.CALL, 3, 24, 12),
    OpCode(0xF5, "PUSH AF", Operation.PUSH, 1, 16),
    OpCode(0xF6, "OR d8", Operation.OR, 2, 8),
    OpCode(0xF7, "RST 30H", Operation.RST, 1, 16),
    OpCode(0xF8, "LD HL, SP + r8", Operation.LD, 1, 2, 12),
    OpCode(0xF9, "LD SP, HL", Operation.LD, 1, 8),
    OpCode(0xFA, "LD A, (a16)", Operation.LD, 3, 16),
    OpCode(0xFB, "EI", Operation.EI, 1, 4),
    # OpCode(0xFC, Operation.CALL, 3, 24, 12),
    # OpCode(0xFD, Operation.CALL, 3, 24),
    OpCode(0xFE, "CP d8", Operation.CP, 2, 8),
    OpCode(0xFF, "RST 38H", Operation.RST, 1, 16),
]

opcodes_map = {opcode.code: opcode for opcode in opcodes}
