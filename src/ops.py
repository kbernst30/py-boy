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
    DAA = 1
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
    OpCode(0x34, "INC (HL)", Operation.INC, 1, 12),
    OpCode(0x35, "DEC (HL)", Operation.DEC, 1, 12),
    OpCode(0x36, "LD (HL), d8", Operation.LD, 2, 12),
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
    OpCode(0x76, "HALT", Operation.HALT, 1, 0),
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
    OpCode(0xCB, "PREFIX", Operation.PREFIX, 1, 0),
    OpCode(0xCC, "CALL Z, a16", Operation.CALL, 3, 24, 12),
    OpCode(0xCD, "CALL a16", Operation.CALL, 3, 24),
    OpCode(0xCE, "ADC A, d8", Operation.ADC, 2, 8),
    OpCode(0xCF, "RST 08H", Operation.RST, 1, 16),

    OpCode(0xD0, "RET NC", Operation.RET, 1, 20, 8),
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
    OpCode(0xE8, "ADD SP, r8", Operation.ADD_16_BIT, 2, 16),
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
    OpCode(0xF8, "LD HL, SP + r8", Operation.LD, 2, 12),
    OpCode(0xF9, "LD SP, HL", Operation.LD, 1, 8),
    OpCode(0xFA, "LD A, (a16)", Operation.LD, 3, 16),
    OpCode(0xFB, "EI", Operation.EI, 1, 4),
    # OpCode(0xFC, Operation.CALL, 3, 24, 12),
    # OpCode(0xFD, Operation.CALL, 3, 24),
    OpCode(0xFE, "CP d8", Operation.CP, 2, 8),
    OpCode(0xFF, "RST 38H", Operation.RST, 1, 16),
]

prefix_opcodes = [
    OpCode(0x00, "RLC B", Operation.RLC, 2, 8),
    OpCode(0x01, "RLC C", Operation.RLC, 2, 8),
    OpCode(0x02, "RLC D", Operation.RLC, 2, 8),
    OpCode(0x03, "RLC E", Operation.RLC, 2, 8),
    OpCode(0x04, "RLC H", Operation.RLC, 2, 8),
    OpCode(0x05, "RLC L", Operation.RLC, 2, 8),
    OpCode(0x06, "RLC (HL)", Operation.RLC, 2, 16),
    OpCode(0x07, "RLC A", Operation.RLC, 2, 8),
    OpCode(0x08, "RRC B", Operation.RRC, 2, 8),
    OpCode(0x09, "RRC C", Operation.RRC, 2, 8),
    OpCode(0x0A, "RRC D", Operation.RRC, 2, 8),
    OpCode(0x0B, "RRC E", Operation.RRC, 2, 8),
    OpCode(0x0C, "RRC H", Operation.RRC, 2, 8),
    OpCode(0x0D, "RRC L", Operation.RRC, 2, 8),
    OpCode(0x0E, "RRC (HL)", Operation.RRC, 2, 16),
    OpCode(0x0F, "RRC A", Operation.RRC, 2, 8),

    OpCode(0x10, "RL B", Operation.RL, 2, 8),
    OpCode(0x11, "RL C", Operation.RL, 2, 8),
    OpCode(0x12, "RL D", Operation.RL, 2, 8),
    OpCode(0x13, "RL E", Operation.RL, 2, 8),
    OpCode(0x14, "RL H", Operation.RL, 2, 8),
    OpCode(0x15, "RL L", Operation.RL, 2, 8),
    OpCode(0x16, "RL (HL)", Operation.RL, 2, 16),
    OpCode(0x17, "RL A", Operation.RL, 2, 8),
    OpCode(0x18, "RR B", Operation.RR, 2, 8),
    OpCode(0x19, "RR C", Operation.RR, 2, 8),
    OpCode(0x1A, "RR D", Operation.RR, 2, 8),
    OpCode(0x1B, "RR E", Operation.RR, 2, 8),
    OpCode(0x1C, "RR H", Operation.RR, 2, 8),
    OpCode(0x1D, "RR L", Operation.RR, 2, 8),
    OpCode(0x1E, "RR (HL)", Operation.RR, 2, 16),
    OpCode(0x1F, "RR A", Operation.RR, 2, 8),

    OpCode(0x20, "SLA B", Operation.SLA, 2, 8),
    OpCode(0x21, "SLA C", Operation.SLA, 2, 8),
    OpCode(0x22, "SLA D", Operation.SLA, 2, 8),
    OpCode(0x23, "SLA E", Operation.SLA, 2, 8),
    OpCode(0x24, "SLA H", Operation.SLA, 2, 8),
    OpCode(0x25, "SLA L", Operation.SLA, 2, 8),
    OpCode(0x26, "SLA (HL)", Operation.SLA, 2, 16),
    OpCode(0x27, "SLA A", Operation.SLA, 2, 8),
    OpCode(0x28, "SRA B", Operation.SRA, 2, 8),
    OpCode(0x29, "SRA C", Operation.SRA, 2, 8),
    OpCode(0x2A, "SRA D", Operation.SRA, 2, 8),
    OpCode(0x2B, "SRA E", Operation.SRA, 2, 8),
    OpCode(0x2C, "SRA H", Operation.SRA, 2, 8),
    OpCode(0x2D, "SRA L", Operation.SRA, 2, 8),
    OpCode(0x2E, "SRA (HL)", Operation.SRA, 2, 16),
    OpCode(0x2F, "SRA A", Operation.SRA, 2, 8),

    OpCode(0x30, "SWAP B", Operation.SWAP, 2, 8),
    OpCode(0x31, "SWAP C", Operation.SWAP, 2, 8),
    OpCode(0x32, "SWAP D", Operation.SWAP, 2, 8),
    OpCode(0x33, "SWAP E", Operation.SWAP, 2, 8),
    OpCode(0x34, "SWAP H", Operation.SWAP, 2, 8),
    OpCode(0x35, "SWAP L", Operation.SWAP, 2, 8),
    OpCode(0x36, "SWAP (HL)", Operation.SWAP, 2, 16),
    OpCode(0x37, "SWAP A", Operation.SWAP, 2, 8),
    OpCode(0x38, "SRL B", Operation.SRL, 2, 8),
    OpCode(0x39, "SRL C", Operation.SRL, 2, 8),
    OpCode(0x3A, "SRL D", Operation.SRL, 2, 8),
    OpCode(0x3B, "SRL E", Operation.SRL, 2, 8),
    OpCode(0x3C, "SRL H", Operation.SRL, 2, 8),
    OpCode(0x3D, "SRL L", Operation.SRL, 2, 8),
    OpCode(0x3E, "SRL (HL)", Operation.SRL, 2, 16),
    OpCode(0x3F, "SRL A", Operation.SRL, 2, 8),

    OpCode(0x40, "BIT 0, B", Operation.BIT, 2, 8),
    OpCode(0x41, "BIT 0, C", Operation.BIT, 2, 8),
    OpCode(0x42, "BIT 0, D", Operation.BIT, 2, 8),
    OpCode(0x43, "BIT 0, E", Operation.BIT, 2, 8),
    OpCode(0x44, "BIT 0, H", Operation.BIT, 2, 8),
    OpCode(0x45, "BIT 0, L", Operation.BIT, 2, 8),
    OpCode(0x46, "BIT 0, (HL)", Operation.BIT, 2, 12),
    OpCode(0x47, "BIT 0, A", Operation.BIT, 2, 8),
    OpCode(0x48, "BIT 1, B", Operation.BIT, 2, 8),
    OpCode(0x49, "BIT 1, C", Operation.BIT, 2, 8),
    OpCode(0x4A, "BIT 1, D", Operation.BIT, 2, 8),
    OpCode(0x4B, "BIT 1, E", Operation.BIT, 2, 8),
    OpCode(0x4C, "BIT 1, H", Operation.BIT, 2, 8),
    OpCode(0x4D, "BIT 1, L", Operation.BIT, 2, 8),
    OpCode(0x4E, "BIT 1, (HL)", Operation.BIT, 2, 12),
    OpCode(0x4F, "BIT 1, A", Operation.BIT, 2, 8),

    OpCode(0x50, "BIT 2, B", Operation.BIT, 2, 8),
    OpCode(0x51, "BIT 2, C", Operation.BIT, 2, 8),
    OpCode(0x52, "BIT 2, D", Operation.BIT, 2, 8),
    OpCode(0x53, "BIT 2, E", Operation.BIT, 2, 8),
    OpCode(0x54, "BIT 2, H", Operation.BIT, 2, 8),
    OpCode(0x55, "BIT 2, L", Operation.BIT, 2, 8),
    OpCode(0x56, "BIT 2, (HL)", Operation.BIT, 2, 12),
    OpCode(0x57, "BIT 2, A", Operation.BIT, 2, 8),
    OpCode(0x58, "BIT 3, B", Operation.BIT, 2, 8),
    OpCode(0x59, "BIT 3, C", Operation.BIT, 2, 8),
    OpCode(0x5A, "BIT 3, D", Operation.BIT, 2, 8),
    OpCode(0x5B, "BIT 3, E", Operation.BIT, 2, 8),
    OpCode(0x5C, "BIT 3, H", Operation.BIT, 2, 8),
    OpCode(0x5D, "BIT 3, L", Operation.BIT, 2, 8),
    OpCode(0x5E, "BIT 3, (HL)", Operation.BIT, 2, 12),
    OpCode(0x5F, "BIT 3, A", Operation.BIT, 2, 8),

    OpCode(0x60, "BIT 4, B", Operation.BIT, 2, 8),
    OpCode(0x61, "BIT 4, C", Operation.BIT, 2, 8),
    OpCode(0x62, "BIT 4, D", Operation.BIT, 2, 8),
    OpCode(0x63, "BIT 4, E", Operation.BIT, 2, 8),
    OpCode(0x64, "BIT 4, H", Operation.BIT, 2, 8),
    OpCode(0x65, "BIT 4, L", Operation.BIT, 2, 8),
    OpCode(0x66, "BIT 4, (HL)", Operation.BIT, 2, 12),
    OpCode(0x67, "BIT 4, A", Operation.BIT, 2, 8),
    OpCode(0x68, "BIT 5, B", Operation.BIT, 2, 8),
    OpCode(0x69, "BIT 5, C", Operation.BIT, 2, 8),
    OpCode(0x6A, "BIT 5, D", Operation.BIT, 2, 8),
    OpCode(0x6B, "BIT 5, E", Operation.BIT, 2, 8),
    OpCode(0x6C, "BIT 5, H", Operation.BIT, 2, 8),
    OpCode(0x6D, "BIT 5, L", Operation.BIT, 2, 8),
    OpCode(0x6E, "BIT 5, (HL)", Operation.BIT, 2, 12),
    OpCode(0x6F, "BIT 5, A", Operation.BIT, 2, 8),

    OpCode(0x70, "BIT 6, B", Operation.BIT, 2, 8),
    OpCode(0x71, "BIT 6, C", Operation.BIT, 2, 8),
    OpCode(0x72, "BIT 6, D", Operation.BIT, 2, 8),
    OpCode(0x73, "BIT 6, E", Operation.BIT, 2, 8),
    OpCode(0x74, "BIT 6, H", Operation.BIT, 2, 8),
    OpCode(0x75, "BIT 6, L", Operation.BIT, 2, 8),
    OpCode(0x76, "BIT 6, (HL)", Operation.BIT, 2, 12),
    OpCode(0x77, "BIT 6, A", Operation.BIT, 2, 8),
    OpCode(0x78, "BIT 7, B", Operation.BIT, 2, 8),
    OpCode(0x79, "BIT 7, C", Operation.BIT, 2, 8),
    OpCode(0x7A, "BIT 7, D", Operation.BIT, 2, 8),
    OpCode(0x7B, "BIT 7, E", Operation.BIT, 2, 8),
    OpCode(0x7C, "BIT 7, H", Operation.BIT, 2, 8),
    OpCode(0x7D, "BIT 7, L", Operation.BIT, 2, 8),
    OpCode(0x7E, "BIT 7, (HL)", Operation.BIT, 2, 12),
    OpCode(0x7F, "BIT 7, A", Operation.BIT, 2, 8),

    OpCode(0x80, "RES 0, B", Operation.RES, 2, 8),
    OpCode(0x81, "RES 0, C", Operation.RES, 2, 8),
    OpCode(0x82, "RES 0, D", Operation.RES, 2, 8),
    OpCode(0x83, "RES 0, E", Operation.RES, 2, 8),
    OpCode(0x84, "RES 0, H", Operation.RES, 2, 8),
    OpCode(0x85, "RES 0, L", Operation.RES, 2, 8),
    OpCode(0x86, "RES 0, (HL)", Operation.RES, 2, 16),
    OpCode(0x87, "RES 0, A", Operation.RES, 2, 8),
    OpCode(0x88, "RES 1, B", Operation.RES, 2, 8),
    OpCode(0x89, "RES 1, C", Operation.RES, 2, 8),
    OpCode(0x8A, "RES 1, D", Operation.RES, 2, 8),
    OpCode(0x8B, "RES 1, E", Operation.RES, 2, 8),
    OpCode(0x8C, "RES 1, H", Operation.RES, 2, 8),
    OpCode(0x8D, "RES 1, L", Operation.RES, 2, 8),
    OpCode(0x8E, "RES 1, (HL)", Operation.RES, 2, 16),
    OpCode(0x8F, "RES 1, A", Operation.RES, 2, 8),

    OpCode(0x90, "RES 2, B", Operation.RES, 2, 8),
    OpCode(0x91, "RES 2, C", Operation.RES, 2, 8),
    OpCode(0x92, "RES 2, D", Operation.RES, 2, 8),
    OpCode(0x93, "RES 2, E", Operation.RES, 2, 8),
    OpCode(0x94, "RES 2, H", Operation.RES, 2, 8),
    OpCode(0x95, "RES 2, L", Operation.RES, 2, 8),
    OpCode(0x96, "RES 2, (HL)", Operation.RES, 2, 16),
    OpCode(0x97, "RES 2, A", Operation.RES, 2, 8),
    OpCode(0x98, "RES 3, B", Operation.RES, 2, 8),
    OpCode(0x99, "RES 3, C", Operation.RES, 2, 8),
    OpCode(0x9A, "RES 3, D", Operation.RES, 2, 8),
    OpCode(0x9B, "RES 3, E", Operation.RES, 2, 8),
    OpCode(0x9C, "RES 3, H", Operation.RES, 2, 8),
    OpCode(0x9D, "RES 3, L", Operation.RES, 2, 8),
    OpCode(0x9E, "RES 3, (HL)", Operation.RES, 2, 16),
    OpCode(0x9F, "RES 3, A", Operation.RES, 2, 8),

    OpCode(0xA0, "RES 4, B", Operation.RES, 2, 8),
    OpCode(0xA1, "RES 4, C", Operation.RES, 2, 8),
    OpCode(0xA2, "RES 4, D", Operation.RES, 2, 8),
    OpCode(0xA3, "RES 4, E", Operation.RES, 2, 8),
    OpCode(0xA4, "RES 4, H", Operation.RES, 2, 8),
    OpCode(0xA5, "RES 4, L", Operation.RES, 2, 8),
    OpCode(0xA6, "RES 4, (HL)", Operation.RES, 2, 16),
    OpCode(0xA7, "RES 4, A", Operation.RES, 2, 8),
    OpCode(0xA8, "RES 5, B", Operation.RES, 2, 8),
    OpCode(0xA9, "RES 5, C", Operation.RES, 2, 8),
    OpCode(0xAA, "RES 5, D", Operation.RES, 2, 8),
    OpCode(0xAB, "RES 5, E", Operation.RES, 2, 8),
    OpCode(0xAC, "RES 5, H", Operation.RES, 2, 8),
    OpCode(0xAD, "RES 5, L", Operation.RES, 2, 8),
    OpCode(0xAE, "RES 5, (HL)", Operation.RES, 2, 16),
    OpCode(0xAF, "RES 5, A", Operation.RES, 2, 8),

    OpCode(0xB0, "RES 6, B", Operation.RES, 2, 8),
    OpCode(0xB1, "RES 6, C", Operation.RES, 2, 8),
    OpCode(0xB2, "RES 6, D", Operation.RES, 2, 8),
    OpCode(0xB3, "RES 6, E", Operation.RES, 2, 8),
    OpCode(0xB4, "RES 6, H", Operation.RES, 2, 8),
    OpCode(0xB5, "RES 6, L", Operation.RES, 2, 8),
    OpCode(0xB6, "RES 6, (HL)", Operation.RES, 2, 16),
    OpCode(0xB7, "RES 6, A", Operation.RES, 2, 8),
    OpCode(0xB8, "RES 7, B", Operation.RES, 2, 8),
    OpCode(0xB9, "RES 7, C", Operation.RES, 2, 8),
    OpCode(0xBA, "RES 7, D", Operation.RES, 2, 8),
    OpCode(0xBB, "RES 7, E", Operation.RES, 2, 8),
    OpCode(0xBC, "RES 7, H", Operation.RES, 2, 8),
    OpCode(0xBD, "RES 7, L", Operation.RES, 2, 8),
    OpCode(0xBE, "RES 7, (HL)", Operation.RES, 2, 16),
    OpCode(0xBF, "RES 7, A", Operation.RES, 2, 8),

    OpCode(0xC0, "SET 0, B", Operation.SET, 2, 8),
    OpCode(0xC1, "SET 0, C", Operation.SET, 2, 8),
    OpCode(0xC2, "SET 0, D", Operation.SET, 2, 8),
    OpCode(0xC3, "SET 0, E", Operation.SET, 2, 8),
    OpCode(0xC4, "SET 0, H", Operation.SET, 2, 8),
    OpCode(0xC5, "SET 0, L", Operation.SET, 2, 8),
    OpCode(0xC6, "SET 0, (HL)", Operation.SET, 2, 16),
    OpCode(0xC7, "SET 0, A", Operation.SET, 2, 8),
    OpCode(0xC8, "SET 1, B", Operation.SET, 2, 8),
    OpCode(0xC9, "SET 1, C", Operation.SET, 2, 8),
    OpCode(0xCA, "SET 1, D", Operation.SET, 2, 8),
    OpCode(0xCB, "SET 1, E", Operation.SET, 2, 8),
    OpCode(0xCC, "SET 1, H", Operation.SET, 2, 8),
    OpCode(0xCD, "SET 1, L", Operation.SET, 2, 8),
    OpCode(0xCE, "SET 1, (HL)", Operation.SET, 2, 16),
    OpCode(0xCF, "SET 1, A", Operation.SET, 2, 8),

    OpCode(0xD0, "SET 2, B", Operation.SET, 2, 8),
    OpCode(0xD1, "SET 2, C", Operation.SET, 2, 8),
    OpCode(0xD2, "SET 2, D", Operation.SET, 2, 8),
    OpCode(0xD3, "SET 2, E", Operation.SET, 2, 8),
    OpCode(0xD4, "SET 2, H", Operation.SET, 2, 8),
    OpCode(0xD5, "SET 2, L", Operation.SET, 2, 8),
    OpCode(0xD6, "SET 2, (HL)", Operation.SET, 2, 16),
    OpCode(0xD7, "SET 2, A", Operation.SET, 2, 8),
    OpCode(0xD8, "SET 3, B", Operation.SET, 2, 8),
    OpCode(0xD9, "SET 3, C", Operation.SET, 2, 8),
    OpCode(0xDA, "SET 3, D", Operation.SET, 2, 8),
    OpCode(0xDB, "SET 3, E", Operation.SET, 2, 8),
    OpCode(0xDC, "SET 3, H", Operation.SET, 2, 8),
    OpCode(0xDD, "SET 3, L", Operation.SET, 2, 8),
    OpCode(0xDE, "SET 3, (HL)", Operation.SET, 2, 16),
    OpCode(0xDF, "SET 3, A", Operation.SET, 2, 8),

    OpCode(0xE0, "SET 4, B", Operation.SET, 2, 8),
    OpCode(0xE1, "SET 4, C", Operation.SET, 2, 8),
    OpCode(0xE2, "SET 4, D", Operation.SET, 2, 8),
    OpCode(0xE3, "SET 4, E", Operation.SET, 2, 8),
    OpCode(0xE4, "SET 4, H", Operation.SET, 2, 8),
    OpCode(0xE5, "SET 4, L", Operation.SET, 2, 8),
    OpCode(0xE6, "SET 4, (HL)", Operation.SET, 2, 16),
    OpCode(0xE7, "SET 4, A", Operation.SET, 2, 8),
    OpCode(0xE8, "SET 5, B", Operation.SET, 2, 8),
    OpCode(0xE9, "SET 5, C", Operation.SET, 2, 8),
    OpCode(0xEA, "SET 5, D", Operation.SET, 2, 8),
    OpCode(0xEB, "SET 5, E", Operation.SET, 2, 8),
    OpCode(0xEC, "SET 5, H", Operation.SET, 2, 8),
    OpCode(0xED, "SET 5, L", Operation.SET, 2, 8),
    OpCode(0xEE, "SET 5, (HL)", Operation.SET, 2, 16),
    OpCode(0xEF, "SET 5, A", Operation.SET, 2, 8),

    OpCode(0xF0, "SET 6, B", Operation.SET, 2, 8),
    OpCode(0xF1, "SET 6, C", Operation.SET, 2, 8),
    OpCode(0xF2, "SET 6, D", Operation.SET, 2, 8),
    OpCode(0xF3, "SET 6, E", Operation.SET, 2, 8),
    OpCode(0xF4, "SET 6, H", Operation.SET, 2, 8),
    OpCode(0xF5, "SET 6, L", Operation.SET, 2, 8),
    OpCode(0xF6, "SET 6, (HL)", Operation.SET, 2, 16),
    OpCode(0xF7, "SET 6, A", Operation.SET, 2, 8),
    OpCode(0xF8, "SET 7, B", Operation.SET, 2, 8),
    OpCode(0xF9, "SET 7, C", Operation.SET, 2, 8),
    OpCode(0xFA, "SET 7, D", Operation.SET, 2, 8),
    OpCode(0xFB, "SET 7, E", Operation.SET, 2, 8),
    OpCode(0xFC, "SET 7, H", Operation.SET, 2, 8),
    OpCode(0xFD, "SET 7, L", Operation.SET, 2, 8),
    OpCode(0xFE, "SET 7, (HL)", Operation.SET, 2, 16),
    OpCode(0xFF, "SET 7, A", Operation.SET, 2, 8),
]

opcodes_map = {opcode.code: opcode for opcode in opcodes}
prefix_opcodes_map = {opcode.code: opcode for opcode in prefix_opcodes}


def debug_ops():
    for i in range(0x10):
        for j in range(0x10):
            code = i << 4 | j
            if code in opcodes_map:
                print(f'{int(opcodes_map[code].alt_cycles/4)}', end=",")
            else:
                print(0, end=",")

        print("")

    print("")

    for i in range(0x10):
        for j in range(0x10):
            code = i << 4 | j
            if code in prefix_opcodes_map:
                print(f'{int(prefix_opcodes_map[code].alt_cycles/4)}', end=",")
            else:
                print(0, end=",")

        print("")
