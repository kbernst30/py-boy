import logging

from enum import Enum

from constants import PROGRAM_COUNTER_INIT, STACK_POINTER_INIT

from ops import OpCode, Operation, opcodes_map, prefix_opcodes_map
from mmu import Mmu
from utils import bit_negate, get_bit_val, is_bit_set, reset_bit, set_bit


logger = logging.getLogger(__name__)


class RegisterPair:
    '''
    Denotes a register pair such as BC or DE
    Remember, Gameboy is Little Endian so treat all data as lo byte (i.e. C) first
    and hi byte (i.e. B) second
    '''

    def __init__(self, name):
        self.name = name
        self.lo = 0
        self.hi = 0

    @property
    def value(self):
        return ((self.hi << 8) | self.lo) & 0xFFFF

    @value.setter
    def value(self, value):
        self.hi = value >> 8
        self.lo = value & 0xFF

    def increment(self):
        self.value = self.value + 1
        if self.value > 0xFFFF:
            self.value = 0

    def decrement(self):
        self.value = self.value - 1
        if self.value < 0:
            self.value = 0xFFFF

    def increment_lo(self):
        self.lo += 1
        if self.lo > 255:
            self.lo = 0

    def increment_hi(self):
        self.hi += 1
        if self.hi > 255:
            self.hi = 0

    def decrement_lo(self):
        self.lo -= 1
        if self.lo < 0:
            self.lo = 255

    def decrement_hi(self):
        self.hi -= 1
        if self.hi < 0:
            self.hi = 255


class Flags(Enum):
    '''
    The F register contains flags for the CPU. The following bits
    represent the following flags:

    7	z	Zero flag
    6	n	Subtraction flag (BCD)
    5	h	Half Carry flag (BCD)
    4	c	Carry flag
    '''

    ZERO = 7
    SUBTRACTION = 6
    HALF_CARRY = 5
    CARRY = 4


class Cpu:
    '''
    CPU for the Gameboy

    There are 8 general purpose registers but are often used in pairs. The registers are as follows:
        AF	-   A	F	Accumulator & Flags
        BC	-   B	C	BC
        DE	-   D	E	DE
        HL	-   H	L	HL

    There is a 2-Byte register for the Program counter and a 2-Byte register for the Stack Pointer
    '''

    def __init__(self, memory: Mmu):
        # Register pairs
        self.af = RegisterPair("AF")
        self.bc = RegisterPair("BC")
        self.de = RegisterPair("DE")
        self.hl = RegisterPair("HL")

        self.program_counter = 0
        self.stack_pointer = 0

        # Memory Management Unit
        self.memory = memory

        # Interrupts
        self.interrupts_enabled = True

        self.debug_ctr = 0
        self.debug_set = set()

    def reset(self):
        '''
        Reset the CPU and all registers to appropriate values
        '''

        self.program_counter = PROGRAM_COUNTER_INIT
        self.stack_pointer = STACK_POINTER_INIT

        self.af.value = 0x01B0
        self.bc.value = 0x0013
        self.de.value = 0x00D8
        self.hl.value = 0x014D

    def execute(self) -> int:
        '''
        Get the next operation from memory, decode, and execute

        :return the number of cycles the operation took
        '''

        op = self._read_memory(self.program_counter)
        opcode = opcodes_map[op]

        # if self.debug_ctr < 1258895:
        # if self.debug_ctr < 16510:
            # self._debug()
            # self.debug_ctr += 1
        #     self.debug_set.add(f"{format(op, '02X')} - {opcode.mnemonic} - {opcode.cycles} - {opcode.alt_cycles}")

        #     if self.debug_ctr == 16510:
        #         for item in self.debug_set:
        #             print(item)

        # self._debug(opcode)
        self.program_counter += 1

        # print(opcode.mnemonic)

        match opcode.operation:
            case Operation.ADC: return self._do_add_8_bit(opcode, with_carry=True)
            case Operation.ADD: return self._do_add_8_bit(opcode)
            case Operation.ADD_16_BIT: return self._do_add_16_bit(opcode)
            case Operation.AND: return self._do_and(opcode)
            case Operation.CALL: return self._do_call(opcode)
            case Operation.CCF: return self._do_complement_carry(opcode)
            case Operation.CP: return self._do_compare(opcode)
            case Operation.CPL: return self._do_complement(opcode)
            case Operation.DEC: return self._do_decrement_8_bit(opcode)
            case Operation.DEC_16_BIT: return self._do_decrement_16_bit(opcode)
            case Operation.DI: return self._do_disable_interrupts(opcode)
            case Operation.EI: return self._do_enable_interrupts(opcode)
            case Operation.INC: return self._do_increment_8_bit(opcode)
            case Operation.INC_16_BIT: return self._do_increment_16_bit(opcode)
            case Operation.JP: return self._do_jump(opcode)
            case Operation.JR: return self._do_jump_relative(opcode)
            case Operation.LD: return self._do_load(opcode)
            case Operation.LDH: return self._do_load_h(opcode)
            case Operation.NOP: return opcode.cycles
            case Operation.OR: return self._do_or(opcode)
            case Operation.POP: return self._do_pop(opcode)
            case Operation.PREFIX: return opcode.cycles + self._do_prefix()
            case Operation.PUSH: return self._do_push(opcode)
            case Operation.RET: return self._do_return(opcode)
            case Operation.RLA: return self._do_rla(opcode)
            case Operation.RLCA: return self._do_rlca(opcode)
            case Operation.RRA: return self._do_rra(opcode)
            case Operation.RRCA: return self._do_rrca(opcode)
            case Operation.RST: return self._do_restart(opcode)
            case Operation.SBC: return self._do_sub_8_bit(opcode, with_carry=True)
            case Operation.SCF: return self._do_set_carry_flag(opcode)
            case Operation.SUB: return self._do_sub_8_bit(opcode)
            case Operation.XOR: return self._do_xor(opcode)
            case _: raise Exception(f"Unknown operation encountered 0x{format(op, '02x')} - {opcode.mnemonic}")

    def _read_memory(self, addr: int) -> int:
        '''
        Read a byte from memory and return

        :return the data from memory
        '''

        return self.memory.read_byte(addr)

    def _write_memory(self, addr: int, data: int):
        '''
        Write a byte to memory
        '''

        # Testing for Blargg output
        if addr == 0xFF01:
            # print(str(self.debug_ctr) + " - " + format(addr, '0x'), format(data, '0x'))
            print(chr(data), end="")
            self.debug_ctr += 1

        self.memory.write_byte(addr, data)

    def _get_next_byte(self) -> int:
        '''
        Gets the next byte at the location of the program counter, and increments the program counter

        :return an int representing the next byte in memory
        '''

        byte = self._read_memory(self.program_counter)
        self.program_counter += 1
        return byte & 0xFF

    def _get_next_byte_signed(self) -> int:
        '''
        Gets the next byte at the location of the program counter, as an 8-bit signed,
        and increments the program counter

        :return an int representing the next signed byte in memory
        '''

        byte = self._get_next_byte()
        return byte - 256 if byte > 127 else byte

    def _get_next_word(self) -> int:
        '''
        Gets the next 2 bytes at the location of the program counter. CPU is little endian

        :return an int representing the next two bytes in memory, properly made for little endian
        '''

        first_byte = self._get_next_byte()
        second_byte = self._get_next_byte()
        return ((second_byte << 8) | first_byte) & 0xFFFF

    def _is_zero_flag_set(self) -> bool:
        '''
        Checks if zero flag in F register is set

        :return True if zero flag is set, False otherwise
        '''

        return get_bit_val(self.af.lo, Flags.ZERO.value)

    def _is_carry_flag_set(self) -> bool:
        '''
        Checks if carry flag in F register is set

        :return True if carry flag is set, False otherwise
        '''

        return get_bit_val(self.af.lo, Flags.CARRY.value)

    def _is_half_carry_flag_set(self) -> bool:
        '''
        Checks if half carry flag in F register is set

        :return True if half carry flag is set, False otherwise
        '''

        return get_bit_val(self.af.lo, Flags.HALF_CARRY.value)

    def _is_sub_flag_set(self) -> bool:
        '''
        Checks if subtract flag in F register is set

        :return True if subtract flag is set, False otherwise
        '''

        return get_bit_val(self.af.lo, Flags.SUBTRACTION.value)

    def _update_zero_flag(self, val: bool):
        '''
        Set zero flag if val is True, otherwise reset it
        '''

        if val:
            self.af.lo = set_bit(self.af.lo, Flags.ZERO.value)
        else:
            self.af.lo = reset_bit(self.af.lo, Flags.ZERO.value)

    def _update_sub_flag(self, val: bool):
        '''
        Set sub flag if val is True, otherwise reset it
        '''

        if val:
            self.af.lo = set_bit(self.af.lo, Flags.SUBTRACTION.value)
        else:
            self.af.lo = reset_bit(self.af.lo, Flags.SUBTRACTION.value)

    def _update_half_carry_flag(self, val: bool):
        '''
        Set half carry flag if val is True, otherwise reset it
        '''

        if val:
            self.af.lo = set_bit(self.af.lo, Flags.HALF_CARRY.value)
        else:
            self.af.lo = reset_bit(self.af.lo, Flags.HALF_CARRY.value)

    def _update_carry_flag(self, val: bool):
        '''
        Set carry flag if val is True, otherwise reset it
        '''

        if val:
            self.af.lo = set_bit(self.af.lo, Flags.CARRY.value)
        else:
            self.af.lo = reset_bit(self.af.lo, Flags.CARRY.value)

    def _push_byte_to_stack(self, byte: int):
        '''
        Push a byte value onto the stack and decrement the stack pointer
        '''

        self.stack_pointer -= 1
        self._write_memory(self.stack_pointer, byte)

    def _pop_byte_from_stack(self) -> int:
        '''
        Pop a byte from the stack and increment the stack pointer

        :return the popped value
        '''

        val = self._read_memory(self.stack_pointer)
        self.stack_pointer += 1
        return val

    def _push_word_to_stack(self, word: int):
        '''
        Push a word value onto the stack and decrement the stack pointer twice
        Push in order of endianess so lo is popped first (hi pushed first, lo second)
        '''

        lo = word & 0xFF
        hi = word >> 8
        self._push_byte_to_stack(hi)
        self._push_byte_to_stack(lo)

    def _pop_word_from_stack(self) -> int:
        '''
        Pop a word from the stack and increment the stack pointer twice

        :return the popped value
        '''

        lo = self._pop_byte_from_stack()
        hi = self._pop_byte_from_stack()
        return ((hi << 8) | lo) & 0xFFFF

    def _do_add_8_bit(self, opcode: OpCode, with_carry=False) -> int:
        '''
        Performs an 8-bit add operation and stores result in A, setting appropriate flags

        :return the number of cycles needed to execute this operation
        '''

        def do_add(val_1: int, val_2: int) -> int:
            carry = 1 if with_carry and self._is_carry_flag_set() else 0
            res = val_1 + val_2 + carry

            self._update_zero_flag(res & 0xFF == 0)
            self._update_sub_flag(False)
            self._update_carry_flag(res > 0xFF)
            self._update_half_carry_flag((val_1 & 0xF) + (val_2 & 0xF) + carry > 0xF)

            return res & 0xFF

        match opcode.code:
            case 0x80: self.af.hi = do_add(self.af.hi, self.bc.hi)
            case 0x81: self.af.hi = do_add(self.af.hi, self.bc.lo)
            case 0x82: self.af.hi = do_add(self.af.hi, self.de.hi)
            case 0x83: self.af.hi = do_add(self.af.hi, self.de.lo)
            case 0x84: self.af.hi = do_add(self.af.hi, self.hl.hi)
            case 0x85: self.af.hi = do_add(self.af.hi, self.hl.lo)
            case 0x86: self.af.hi = do_add(self.af.hi, self._read_memory(self.hl.value))
            case 0x87: self.af.hi = do_add(self.af.hi, self.af.hi)
            case 0x88: self.af.hi = do_add(self.af.hi, self.bc.hi)
            case 0x89: self.af.hi = do_add(self.af.hi, self.bc.lo)
            case 0x8A: self.af.hi = do_add(self.af.hi, self.de.hi)
            case 0x8B: self.af.hi = do_add(self.af.hi, self.de.lo)
            case 0x8C: self.af.hi = do_add(self.af.hi, self.hl.hi)
            case 0x8D: self.af.hi = do_add(self.af.hi, self.hl.lo)
            case 0x8E: self.af.hi = do_add(self.af.hi, self._read_memory(self.hl.value))
            case 0x8F: self.af.hi = do_add(self.af.hi, self.af.hi)
            case 0xC6: self.af.hi = do_add(self.af.hi, self._get_next_byte())
            case 0xCE: self.af.hi = do_add(self.af.hi, self._get_next_byte())
            case _: raise Exception(f"Unknown operation encountered 0x{format(opcode.code, '02x')} - {opcode.mnemonic}")

        return opcode.cycles

    def _do_add_16_bit(self, opcode: OpCode) -> int:
        '''
        Performs an 16-bit add operation

        :return the number of cycles needed to execute this operation
        '''

        def do_add(val_1: int, val_2: int) -> int:
            res = val_1 + val_2

            self._update_sub_flag(False)
            self._update_carry_flag(res > 0xFFFF)
            self._update_half_carry_flag((val_1 & 0xFF) + (val_2 & 0xFF) > 0xFF)

            return res & 0xFFFF

        match opcode.code:
            case 0x09: self.hl.value = do_add(self.hl.value, self.bc.value)
            case 0x19: self.hl.value = do_add(self.hl.value, self.de.value)
            case 0x29: self.hl.value = do_add(self.hl.value, self.hl.value)
            case _: raise Exception(f"Unknown operation encountered 0x{format(opcode.code, '02x')} - {opcode.mnemonic}")

        return opcode.cycles

    def _do_and(self, opcode: OpCode) -> int:
        '''
        Performs the AND operation and sets appropriate status flags

        :return the number of cycles needed to execute this operation
        '''

        match opcode.code:
            case 0xA0:
                self.af.hi &= self.bc.hi
                val = self.af.hi
            case 0xA1:
                self.af.hi &= self.bc.lo
                val = self.af.hi
            case 0xA2:
                self.af.hi &= self.de.hi
                val = self.af.hi
            case 0xA3:
                self.af.hi &= self.de.lo
                val = self.af.hi
            case 0xA4:
                self.af.hi &= self.hl.hi
                val = self.af.hi
            case 0xA5:
                self.af.hi &= self.hl.lo
                val = self.af.hi
            case 0xA6:
                self.af.hi &= self._read_memory(self.hl.value)
                val = self.af.hi
            case 0xA7:
                self.af.hi &= self.af.hi
                val = self.af.hi
            case 0xE6:
                self.af.hi &= self._get_next_byte()
                val = self.af.hi
            case _: raise Exception(f"Unknown operation encountered 0x{format(opcode.code, '02x')} - {opcode.mnemonic}")

        self._update_zero_flag(val == 0)
        self._update_half_carry_flag(True)
        self._update_sub_flag(False)
        self._update_carry_flag(False)

        return opcode.cycles

    def _do_bit(self, opcode: OpCode) -> int:
        '''
        Test bit in given register

        :return the number of cycles needed to execute this operation
        '''

        match opcode.code:
            case 0x40: self._update_zero_flag(not is_bit_set(self.bc.hi, 0))
            case 0x41: self._update_zero_flag(not is_bit_set(self.bc.lo, 0))
            case 0x42: self._update_zero_flag(not is_bit_set(self.de.hi, 0))
            case 0x43: self._update_zero_flag(not is_bit_set(self.de.lo, 0))
            case 0x44: self._update_zero_flag(not is_bit_set(self.hl.hi, 0))
            case 0x45: self._update_zero_flag(not is_bit_set(self.hl.lo, 0))
            case 0x46: self._update_zero_flag(not is_bit_set(self._read_memory(self.hl.value), 0))
            case 0x47: self._update_zero_flag(not is_bit_set(self.af.hi, 0))
            case 0x48: self._update_zero_flag(not is_bit_set(self.bc.hi, 1))
            case 0x49: self._update_zero_flag(not is_bit_set(self.bc.lo, 1))
            case 0x4A: self._update_zero_flag(not is_bit_set(self.de.hi, 1))
            case 0x4B: self._update_zero_flag(not is_bit_set(self.de.lo, 1))
            case 0x4C: self._update_zero_flag(not is_bit_set(self.hl.hi, 1))
            case 0x4D: self._update_zero_flag(not is_bit_set(self.hl.lo, 1))
            case 0x4E: self._update_zero_flag(not is_bit_set(self._read_memory(self.hl.value), 1))
            case 0x4F: self._update_zero_flag(not is_bit_set(self.af.hi, 1))
            case 0x50: self._update_zero_flag(not is_bit_set(self.bc.hi, 2))
            case 0x51: self._update_zero_flag(not is_bit_set(self.bc.lo, 2))
            case 0x52: self._update_zero_flag(not is_bit_set(self.de.hi, 2))
            case 0x53: self._update_zero_flag(not is_bit_set(self.de.lo, 2))
            case 0x54: self._update_zero_flag(not is_bit_set(self.hl.hi, 2))
            case 0x55: self._update_zero_flag(not is_bit_set(self.hl.lo, 2))
            case 0x56: self._update_zero_flag(not is_bit_set(self._read_memory(self.hl.value), 2))
            case 0x57: self._update_zero_flag(not is_bit_set(self.af.hi, 2))
            case 0x58: self._update_zero_flag(not is_bit_set(self.bc.hi, 3))
            case 0x59: self._update_zero_flag(not is_bit_set(self.bc.lo, 3))
            case 0x5A: self._update_zero_flag(not is_bit_set(self.de.hi, 3))
            case 0x5B: self._update_zero_flag(not is_bit_set(self.de.lo, 3))
            case 0x5C: self._update_zero_flag(not is_bit_set(self.hl.hi, 3))
            case 0x5D: self._update_zero_flag(not is_bit_set(self.hl.lo, 3))
            case 0x5E: self._update_zero_flag(not is_bit_set(self._read_memory(self.hl.value), 3))
            case 0x5F: self._update_zero_flag(not is_bit_set(self.af.hi, 3))
            case 0x60: self._update_zero_flag(not is_bit_set(self.bc.hi, 4))
            case 0x61: self._update_zero_flag(not is_bit_set(self.bc.lo, 4))
            case 0x62: self._update_zero_flag(not is_bit_set(self.de.hi, 4))
            case 0x63: self._update_zero_flag(not is_bit_set(self.de.lo, 4))
            case 0x64: self._update_zero_flag(not is_bit_set(self.hl.hi, 4))
            case 0x65: self._update_zero_flag(not is_bit_set(self.hl.lo, 4))
            case 0x66: self._update_zero_flag(not is_bit_set(self._read_memory(self.hl.value), 4))
            case 0x67: self._update_zero_flag(not is_bit_set(self.af.hi, 4))
            case 0x68: self._update_zero_flag(not is_bit_set(self.bc.hi, 5))
            case 0x69: self._update_zero_flag(not is_bit_set(self.bc.lo, 5))
            case 0x6A: self._update_zero_flag(not is_bit_set(self.de.hi, 5))
            case 0x6B: self._update_zero_flag(not is_bit_set(self.de.lo, 5))
            case 0x6C: self._update_zero_flag(not is_bit_set(self.hl.hi, 5))
            case 0x6D: self._update_zero_flag(not is_bit_set(self.hl.lo, 5))
            case 0x6E: self._update_zero_flag(not is_bit_set(self._read_memory(self.hl.value), 5))
            case 0x6F: self._update_zero_flag(not is_bit_set(self.af.hi, 5))
            case 0x70: self._update_zero_flag(not is_bit_set(self.bc.hi, 6))
            case 0x71: self._update_zero_flag(not is_bit_set(self.bc.lo, 6))
            case 0x72: self._update_zero_flag(not is_bit_set(self.de.hi, 6))
            case 0x73: self._update_zero_flag(not is_bit_set(self.de.lo, 6))
            case 0x74: self._update_zero_flag(not is_bit_set(self.hl.hi, 6))
            case 0x75: self._update_zero_flag(not is_bit_set(self.hl.lo, 6))
            case 0x76: self._update_zero_flag(not is_bit_set(self._read_memory(self.hl.value), 6))
            case 0x77: self._update_zero_flag(not is_bit_set(self.af.hi, 6))
            case 0x78: self._update_zero_flag(not is_bit_set(self.bc.hi, 7))
            case 0x79: self._update_zero_flag(not is_bit_set(self.bc.lo, 7))
            case 0x7A: self._update_zero_flag(not is_bit_set(self.de.hi, 7))
            case 0x7B: self._update_zero_flag(not is_bit_set(self.de.lo, 7))
            case 0x7C: self._update_zero_flag(not is_bit_set(self.hl.hi, 7))
            case 0x7D: self._update_zero_flag(not is_bit_set(self.hl.lo, 7))
            case 0x7E: self._update_zero_flag(not is_bit_set(self._read_memory(self.hl.value), 7))
            case 0x7F: self._update_zero_flag(not is_bit_set(self.af.hi, 7))
            case _: raise Exception(f"Unknown prefix operation encountered 0x{format(opcode.code, '02x')} - {opcode.mnemonic}")

        self._update_half_carry_flag(True)
        self._update_sub_flag(False)

        return opcode.cycles

    def _do_call(self, opcode: OpCode) -> int:
        '''
        Pushes the current PC onto the stack and sets the program counter to the appropriate address,
        if conditionally approved

        :return the number of cycles needed to execute this operation
        '''

        cycles = opcode.cycles

        match opcode.code:
            case 0xC4:
                if not self._is_zero_flag_set():
                    addr = self._get_next_word()
                    self._push_word_to_stack(self.program_counter)
                    self.program_counter = addr
                else:
                    self.program_counter += 2
                    cycles = opcode.alt_cycles
            case 0xCC:
                if self._is_zero_flag_set():
                    addr = self._get_next_word()
                    self._push_word_to_stack(self.program_counter)
                    self.program_counter = addr
                else:
                    self.program_counter += 2
                    cycles = opcode.alt_cycles
            case 0xCD:
                addr = self._get_next_word()
                self._push_word_to_stack(self.program_counter)
                self.program_counter = addr

            case _: raise Exception(f"Unknown operation encountered 0x{format(opcode.code, '02x')} - {opcode.mnemonic}")

        return cycles

    def _do_compare(self, opcode: OpCode) -> int:
        '''
        Does a compare operation, and updates flags as appropriate

        :return the number of cycles needed to execute this operation
        '''

        def do_cp(val_1: int, val_2: int):
            self._update_zero_flag(val_1 == val_2)
            self._update_sub_flag(True)
            self._update_carry_flag(val_1 < val_2)
            self._update_half_carry_flag((val_1 & 0xF) - (val_2 & 0xF) < 0)

        match opcode.code:
            case 0xB8: do_cp(self.af.hi, self.bc.hi)
            case 0xB9: do_cp(self.af.hi, self.bc.lo)
            case 0xBA: do_cp(self.af.hi, self.de.hi)
            case 0xBB: do_cp(self.af.hi, self.de.lo)
            case 0xBC: do_cp(self.af.hi, self.hl.hi)
            case 0xBD: do_cp(self.af.hi, self.hl.lo)
            case 0xBE: do_cp(self.af.hi, self._read_memory(self.hl.value))
            case 0xBF: do_cp(self.af.hi, self.af.hi)
            case 0xFE: do_cp(self.af.hi, self._get_next_byte())
            case _: raise Exception(f"Unknown operation encountered 0x{format(opcode.code, '02x')} - {opcode.mnemonic}")

        return opcode.cycles

    def _do_complement(self, opcode: OpCode) -> int:
        '''
        Complement all bits of the A register

        :return the number of cycles needed to execute this operation
        '''

        self.af.hi = bit_negate(self.af.hi)

        self._update_half_carry_flag(False)
        self._update_sub_flag(False)

        return opcode.cycles

    def _do_complement_carry(self, opcode: OpCode) -> int:
        '''
        Complements the carry flag

        :return the number of cycles needed to execute this operation
        '''

        self._update_carry_flag(not self._is_carry_flag_set())
        self._update_half_carry_flag(False)
        self._update_sub_flag(False)

        return opcode.cycles

    def _do_decrement_8_bit(self, opcode: OpCode) -> int:
        '''
        Do 8-bit decrement instruction and update flags as necessary

        :return the number of cycles need to execute this operation
        '''

        match opcode.code:
            case 0x05:
                self.bc.decrement_hi()
                val = self.bc.hi
            case 0x0D:
                self.bc.decrement_lo()
                val = self.bc.lo
            case 0x15:
                self.de.decrement_hi()
                val = self.de.hi
            case 0x1D:
                self.de.decrement_lo()
                val = self.de.lo
            case 0x25:
                self.hl.decrement_hi()
                val = self.hl.hi
            case 0x2D:
                self.hl.decrement_lo()
                val = self.hl.lo
            case 0x35:
                val = self._read_memory(self.hl.value)
                val -= 1
                if val < 0:
                    val = 255
                self._write_memory(self.hl.value, val)
            case 0x3D:
                self.af.decrement_hi()
                val = self.af.hi

            case _: raise Exception(f"Unknown operation encountered 0x{format(opcode.code, '02x')} - {opcode.mnemonic}")

        self._update_zero_flag(val == 0)
        self._update_sub_flag(True)
        self._update_half_carry_flag(val & 0xF == 0xF)

        return opcode.cycles

    def _do_decrement_16_bit(self, opcode: OpCode) -> int:
        '''
        Do 16-bit decrement instruction

        :return the number of cycles need to execute this operation
        '''

        match opcode.code:
            case 0x0B: self.bc.decrement()
            case 0x1B: self.de.decrement()
            case 0x2B: self.hl.decrement()
            case 0x3B:
                self.stack_pointer -= 1
                if self.stack_pointer < 0:
                    self.stack_pointer = 0xFFFF
            case _: raise Exception(f"Unknown operation encountered 0x{format(opcode.code, '02x')} - {opcode.mnemonic}")

        return opcode.cycles

    def _do_disable_interrupts(self, opcode: OpCode) -> int:
        '''
        Disable interrupts

        :return the number of cycles needed to execute this operation
        '''

        self.interrupts_enabled = False
        return opcode.cycles

    def _do_enable_interrupts(self, opcode: OpCode) -> int:
        '''
        Enable interrupts

        :return the number of cycles needed to execute this operation
        '''

        self.interrupts_enabled = True
        return opcode.cycles

    def _do_increment_8_bit(self, opcode: OpCode) -> int:
        '''
        Do 8-bit increment instruction and update flags as necessary

        :return the number of cycles need to execute this operation
        '''

        match opcode.code:
            case 0x04:
                self.bc.increment_hi()
                val = self.bc.hi
            case 0x0C:
                self.bc.increment_lo()
                val = self.bc.lo
            case 0x14:
                self.de.increment_hi()
                val = self.de.hi
            case 0x1C:
                self.de.increment_lo()
                val = self.de.lo
            case 0x24:
                self.hl.increment_hi()
                val = self.hl.hi
            case 0x2C:
                self.hl.increment_lo()
                val = self.hl.lo
            case 0x34:
                val = self._read_memory(self.hl.value)
                val += 1
                if val > 255:
                    val = 0
                self._write_memory(self.hl.value, val)
            case 0x3C:
                self.af.increment_hi()
                val = self.af.hi

            case _: raise Exception(f"Unknown operation encountered 0x{format(opcode.code, '02x')} - {opcode.mnemonic}")

        self._update_zero_flag(val == 0)
        self._update_sub_flag(False)
        self._update_half_carry_flag(val & 0xF == 0)

        return opcode.cycles

    def _do_increment_16_bit(self, opcode: OpCode) -> int:
        '''
        Do 16-bit increment instruction

        :return the number of cycles need to execute this operation
        '''

        match opcode.code:
            case 0x03: self.bc.increment()
            case 0x13: self.de.increment()
            case 0x23: self.hl.increment()
            case 0x33:
                self.stack_pointer += 1
                if self.stack_pointer > 0xFFFF:
                    self.stack_pointer = 0
            case _: raise Exception(f"Unknown operation encountered 0x{format(opcode.code, '02x')} - {opcode.mnemonic}")

        return opcode.cycles

    def _do_jump(self, opcode: OpCode) -> int:
        '''
        Do jump to instruction. Update program counter to new position

        :return the number of cycles needed to execute this operation
        '''

        cycles = opcode.cycles

        match opcode.code:
            case 0xC2:
                self.program_counter = self._get_next_byte() if not self._is_zero_flag_set() else self.program_counter + 1
                cycles = opcode.alt_cycles if self._is_zero_flag_set() else cycles
            case 0xC3: self.program_counter = self._get_next_word()
            case 0xE9: self.program_counter = self.hl.value
            case _: raise Exception(f"Unknown operation encountered 0x{format(opcode.code, '02x')} - {opcode.mnemonic}")

        return cycles

    def _do_jump_relative(self, opcode: OpCode) -> int:
        '''
        Do jump to instruction, using relative address (PC + next byte).
        Update program counter to new position

        :return the number of cycles needed to execute this operation
        '''

        cycles = opcode.cycles

        match opcode.code:
            case 0x18: self.program_counter = self._get_next_byte_signed() + self.program_counter
            case 0x20:
                self.program_counter = self._get_next_byte_signed() + self.program_counter \
                    if not self._is_zero_flag_set() else self.program_counter + 1
                cycles = opcode.alt_cycles if self._is_zero_flag_set() else cycles
            case 0x28:
                self.program_counter = self._get_next_byte_signed() + self.program_counter \
                    if self._is_zero_flag_set() else self.program_counter + 1
                cycles = opcode.alt_cycles if not self._is_zero_flag_set() else cycles
            case 0x30:
                self.program_counter = self._get_next_byte_signed() + self.program_counter \
                    if not self._is_carry_flag_set() else self.program_counter + 1
                cycles = opcode.alt_cycles if self._is_carry_flag_set() else cycles
            case 0x38:
                self.program_counter = self._get_next_byte_signed() + self.program_counter \
                    if self._is_carry_flag_set() else self.program_counter + 1
                cycles = opcode.alt_cycles if not self._is_carry_flag_set() else cycles
            case _: raise Exception(f"Unknown operation encountered 0x{format(opcode.code, '02x')} - {opcode.mnemonic}")

        return cycles

    def _do_load(self, opcode: OpCode) -> int:
        '''
        Do a load instruction.

        :return the number of cycles needed to execute this operation
        '''

        match opcode.code:
            case 0x01: self.bc.value = self._get_next_word()
            case 0x02: self._write_memory(self.bc.value, self.af.hi)
            case 0x06: self.bc.hi = self._get_next_byte()
            case 0x08: self._write_memory(self._get_next_word(), self.stack_pointer)
            case 0x0A: self.af.hi = self._read_memory(self.bc.value)
            case 0x0E: self.bc.lo = self._get_next_byte()
            case 0x11: self.de.value = self._get_next_word()
            case 0x12: self._write_memory(self.de.value, self.af.hi)
            case 0x16: self.de.hi = self._get_next_byte()
            case 0x1A: self.af.hi = self._read_memory(self.de.value)
            case 0x1E: self.de.lo = self._get_next_byte()
            case 0x21: self.hl.value = self._get_next_word()
            case 0x22:
                self._write_memory(self.hl.value, self.af.hi)
                self.hl.increment()
            case 0x26: self.hl.hi = self._get_next_byte()
            case 0x2A:
                self.af.hi = self._read_memory(self.hl.value)
                self.hl.increment()
            case 0x2E: self.hl.lo = self._get_next_byte()
            case 0x31: self.stack_pointer = self._get_next_word()
            case 0x32:
                self._write_memory(self.hl.value, self.af.hi)
                self.hl.decrement()
            case 0x36: self._write_memory(self.hl.value, self._get_next_byte())
            case 0x3A:
                self.af.hi = self._read_memory(self.hl.value)
                self.hl.decrement()
            case 0x40: self.bc.hi = self.bc.hi
            case 0x41: self.bc.hi = self.bc.lo
            case 0x42: self.bc.hi = self.de.hi
            case 0x43: self.bc.hi = self.de.lo
            case 0x44: self.bc.hi = self.hl.hi
            case 0x45: self.bc.hi = self.hl.lo
            case 0x46: self.bc.hi = self._read_memory(self.hl.value)
            case 0x47: self.bc.hi = self.af.hi
            case 0x48: self.bc.lo = self.bc.hi
            case 0x49: self.bc.lo = self.bc.lo
            case 0x4A: self.bc.lo = self.de.hi
            case 0x4B: self.bc.lo = self.de.lo
            case 0x4C: self.bc.lo = self.hl.hi
            case 0x4D: self.bc.lo = self.hl.lo
            case 0x4E: self.bc.lo = self._read_memory(self.hl.value)
            case 0x4F: self.bc.lo = self.af.hi
            case 0x50: self.de.hi = self.bc.hi
            case 0x51: self.de.hi = self.bc.lo
            case 0x52: self.de.hi = self.de.hi
            case 0x53: self.de.hi = self.de.lo
            case 0x54: self.de.hi = self.hl.hi
            case 0x55: self.de.hi = self.hl.lo
            case 0x56: self.de.hi = self._read_memory(self.hl.value)
            case 0x57: self.de.hi = self.af.hi
            case 0x58: self.de.lo = self.bc.hi
            case 0x59: self.de.lo = self.bc.lo
            case 0x5A: self.de.lo = self.de.hi
            case 0x5B: self.de.lo = self.de.lo
            case 0x5C: self.de.lo = self.hl.hi
            case 0x5D: self.de.lo = self.hl.lo
            case 0x5E: self.de.lo = self._read_memory(self.hl.value)
            case 0x5F: self.de.lo = self.af.hi
            case 0x60: self.hl.hi = self.bc.hi
            case 0x61: self.hl.hi = self.bc.lo
            case 0x62: self.hl.hi = self.de.hi
            case 0x63: self.hl.hi = self.de.lo
            case 0x64: self.hl.hi = self.hl.hi
            case 0x65: self.hl.hi = self.hl.lo
            case 0x66: self.hl.hi = self._read_memory(self.hl.value)
            case 0x67: self.hl.hi = self.af.hi
            case 0x68: self.hl.lo = self.bc.hi
            case 0x69: self.hl.lo = self.bc.lo
            case 0x6A: self.hl.lo = self.de.hi
            case 0x6B: self.hl.lo = self.de.lo
            case 0x6C: self.hl.lo = self.hl.hi
            case 0x6D: self.hl.lo = self.hl.lo
            case 0x6E: self.hl.lo = self._read_memory(self.hl.value)
            case 0x6F: self.hl.lo = self.af.hi
            case 0x70: self._write_memory(self.hl.value, self.bc.hi)
            case 0x71: self._write_memory(self.hl.value, self.bc.lo)
            case 0x72: self._write_memory(self.hl.value, self.de.hi)
            case 0x73: self._write_memory(self.hl.value, self.de.lo)
            case 0x74: self._write_memory(self.hl.value, self.hl.hi)
            case 0x75: self._write_memory(self.hl.value, self.hl.lo)
            case 0x77: self._write_memory(self.hl.value, self.af.hi)
            case 0x78: self.af.hi = self.bc.hi
            case 0x79: self.af.hi = self.bc.lo
            case 0x7A: self.af.hi = self.de.hi
            case 0x7B: self.af.hi = self.de.lo
            case 0x7C: self.af.hi = self.hl.hi
            case 0x7D: self.af.hi = self.hl.lo
            case 0x7E: self.af.hi = self._read_memory(self.hl.value)
            case 0x7F: self.af.hi = self.af.hi
            case 0x3E: self.af.hi = self._get_next_byte()
            case 0xEA: self._write_memory(self._get_next_word(), self.af.hi)
            case 0xF8:
                offset = self._get_next_byte_signed()
                self.hl.value = self.stack_pointer + offset
                self._update_zero_flag(False)
                self._update_sub_flag(False)
                self._update_carry_flag((self.stack_pointer & 0xFF) + (offset & 0xFF) > 0xFF)
                self._update_half_carry_flag((self.stack_pointer & 0xF) + (offset & 0xF) > 0xF)
            case 0xF9: self.stack_pointer = self.hl.value
            case 0xFA: self.af.hi = self._read_memory(self._get_next_word())
            case _: raise Exception(f"Unknown operation encountered 0x{format(opcode.code, '02x')} - {opcode.mnemonic}")

        return opcode.cycles

    def _do_load_h(self, opcode: OpCode) -> int:
        '''
        Do a load instruction where address in instruction is least significant byte of address
        and most significant byte is 0xFF

        :return the number of cycles needed to execute this operation
        '''

        match opcode.code:
            case 0xE0: self._write_memory(0xFF00 | self._get_next_byte(), self.af.hi)
            case 0xF0: self.af.hi = self._read_memory(0xFF00 | self._get_next_byte())
            case _: raise Exception(f"Unknown operation encountered 0x{format(opcode.code, '02x')} - {opcode.mnemonic}")

        return opcode.cycles

    def _do_or(self, opcode: OpCode) -> int:
        '''
        Performs the OR operation and sets appropriate status flags

        :return the number of cycles needed to execute this operation
        '''

        match opcode.code:
            case 0xB0:
                self.af.hi |= self.bc.hi
                val = self.af.hi
            case 0xB1:
                self.af.hi |= self.bc.lo
                val = self.af.hi
            case 0xB2:
                self.af.hi |= self.de.hi
                val = self.af.hi
            case 0xB3:
                self.af.hi |= self.de.lo
                val = self.af.hi
            case 0xB4:
                self.af.hi |= self.hl.hi
                val = self.af.hi
            case 0xB5:
                self.af.hi |= self.hl.lo
                val = self.af.hi
            case 0xB6:
                self.af.hi |= self._read_memory(self.hl.value)
                val = self.af.hi
            case 0xB7:
                self.af.hi |= self.af.lo
                val = self.af.hi
            case 0xF6:
                self.af.hi |= self._get_next_byte()
                val = self.af.hi
            case _: raise Exception(f"Unknown operation encountered 0x{format(opcode.code, '02x')} - {opcode.mnemonic}")

        self._update_zero_flag(val == 0)
        self._update_half_carry_flag(False)
        self._update_sub_flag(False)
        self._update_carry_flag(False)

        return opcode.cycles

    def _do_pop(self, opcode: OpCode) -> int:
        '''
        Pop word of the stack and load it into register pair

        :return the number of cycles needed to execute this operation
        '''

        match opcode.code:
            case 0xC1: self.bc.value = self._pop_word_from_stack()
            case 0xD1: self.de.value = self._pop_word_from_stack()
            case 0xE1: self.hl.value = self._pop_word_from_stack()
            case 0xF1:
                self.af.value = self._pop_word_from_stack()
                self.af.lo &= 0xF0  # The lower bits of the Flags register are never set
            case _: raise Exception(f"Unknown operation encountered 0x{format(opcode.code, '02x')} - {opcode.mnemonic}")

        return opcode.cycles

    def _do_prefix(self) -> int:
        '''
        Do a prefix operation, from the CB opcode

        :return the number of cycles from the prefix operation
        '''

        op = self._read_memory(self.program_counter)
        opcode = prefix_opcodes_map[op]

        self.program_counter += 1

        match opcode.operation:
            case Operation.BIT: return self._do_bit(opcode)
            case Operation.RES: return self._do_res(opcode)
            case Operation.RL: return self._do_rl(opcode, through_carry=True)
            case Operation.RLC: return self._do_rl(opcode, through_carry=False)
            case Operation.RR: return self._do_rr(opcode, through_carry=True)
            case Operation.RRC: return self._do_rr(opcode, through_carry=False)
            case Operation.SET: return self._do_set(opcode)
            case Operation.SLA: return self._do_shift_left(opcode)
            case Operation.SRA: return self._do_shift_right(opcode, maintain_msb=True)
            case Operation.SRL: return self._do_shift_right(opcode)
            case Operation.SWAP: return self._do_swap(opcode)
            case _: raise Exception(f"Unknown prefix operation encountered 0x{format(op, '02x')} - {opcode.mnemonic}")

    def _do_push(self, opcode: OpCode) -> int:
        '''
        Push word onto stack

        :return the number of cycles needed to execute this operation
        '''

        match opcode.code:
            case 0xC5: self._push_word_to_stack(self.bc.value)
            case 0xD5: self._push_word_to_stack(self.de.value)
            case 0xE5: self._push_word_to_stack(self.hl.value)
            case 0xF5: self._push_word_to_stack(self.af.value)
            case _: raise Exception(f"Unknown operation encountered 0x{format(opcode.code, '02x')} - {opcode.mnemonic}")

        return opcode.cycles

    def _do_return(self, opcode: OpCode) -> int:
        '''
        Do a return from subprocedure, popping PC off of the stack

        :return the number of cycles needed to execute this operation
        '''

        cycles = opcode.cycles

        match opcode.code:
            case 0xC8:
                self.program_counter = self._pop_word_from_stack() \
                    if self._is_zero_flag_set() else self.program_counter + 1
                cycles = opcode.alt_cycles if not self._is_zero_flag_set() else cycles
            case 0xC9: self.program_counter = self._pop_word_from_stack()
            case 0xD0:
                self.program_counter = self._pop_word_from_stack() \
                    if not self._is_carry_flag_set() else self.program_counter + 1
                cycles = opcode.alt_cycles if self._is_carry_flag_set() else cycles
            case 0xD8:
                self.program_counter = self._pop_word_from_stack() \
                    if self._is_carry_flag_set() else self.program_counter + 1
                cycles = opcode.alt_cycles if not self._is_carry_flag_set() else cycles
            case _: raise Exception(f"Unknown operation encountered 0x{format(opcode.code, '02x')} - {opcode.mnemonic}")

        return cycles

    def _do_res(self, opcode: OpCode) -> int:
        '''
        Reset bit n in given register

        :return the number of cycles needed to execute this operation
        '''

        match opcode.code:
            case 0x80: self.bc.hi = reset_bit(self.bc.hi, 0)
            case 0x81: self.bc.lo = reset_bit(self.bc.lo, 0)
            case 0x82: self.de.hi = reset_bit(self.de.hi, 0)
            case 0x83: self.de.hi = reset_bit(self.de.lo, 0)
            case 0x84: self.hl.hi = reset_bit(self.hl.hi, 0)
            case 0x85: self.hl.hi = reset_bit(self.hl.lo, 0)
            case 0x86: self._write_memory(self.hl.value, reset_bit(self._read_memory(self.hl.value), 0))
            case 0x87: self.af.hi = reset_bit(self.af.hi, 0)
            case 0x88: self.bc.hi = reset_bit(self.bc.hi, 1)
            case 0x89: self.bc.hi = reset_bit(self.bc.lo, 1)
            case 0x8A: self.de.hi = reset_bit(self.de.hi, 1)
            case 0x8B: self.de.hi = reset_bit(self.de.lo, 1)
            case 0x8C: self.hl.hi = reset_bit(self.hl.hi, 1)
            case 0x8D: self.hl.hi = reset_bit(self.hl.lo, 1)
            case 0x8E: self._write_memory(self.hl.value, reset_bit(self._read_memory(self.hl.value), 1))
            case 0x8F: self.af.hi = reset_bit(self.af.hi, 1)
            case 0x90: self.bc.hi = reset_bit(self.bc.hi, 2)
            case 0x91: self.bc.hi = reset_bit(self.bc.lo, 2)
            case 0x92: self.de.hi = reset_bit(self.de.hi, 2)
            case 0x93: self.de.hi = reset_bit(self.de.lo, 2)
            case 0x94: self.hl.hi = reset_bit(self.hl.hi, 2)
            case 0x95: self.hl.hi = reset_bit(self.hl.lo, 2)
            case 0x96: self._write_memory(self.hl.value, reset_bit(self._read_memory(self.hl.value), 2))
            case 0x97: self.af.hi = reset_bit(self.af.hi, 2)
            case 0x98: self.bc.hi = reset_bit(self.bc.hi, 3)
            case 0x99: self.bc.hi = reset_bit(self.bc.lo, 3)
            case 0x9A: self.de.hi = reset_bit(self.de.hi, 3)
            case 0x9B: self.de.hi = reset_bit(self.de.lo, 3)
            case 0x9C: self.hl.hi = reset_bit(self.hl.hi, 3)
            case 0x9D: self.hl.hi = reset_bit(self.hl.lo, 3)
            case 0x9E: self._write_memory(self.hl.value, reset_bit(self._read_memory(self.hl.value), 3))
            case 0x9F: self.af.hi = reset_bit(self.af.hi, 3)
            case 0xA0: self.bc.hi = reset_bit(self.bc.hi, 4)
            case 0xA1: self.bc.hi = reset_bit(self.bc.lo, 4)
            case 0xA2: self.de.hi = reset_bit(self.de.hi, 4)
            case 0xA3: self.de.hi = reset_bit(self.de.lo, 4)
            case 0xA4: self.hl.hi = reset_bit(self.hl.hi, 4)
            case 0xA5: self.hl.hi = reset_bit(self.hl.lo, 4)
            case 0xA6: self._write_memory(self.hl.value, reset_bit(self._read_memory(self.hl.value), 4))
            case 0xA7: self.af.hi = reset_bit(self.af.hi, 4)
            case 0xA8: self.bc.hi = reset_bit(self.bc.hi, 5)
            case 0xA9: self.bc.hi = reset_bit(self.bc.lo, 5)
            case 0xAA: self.de.hi = reset_bit(self.de.hi, 5)
            case 0xAB: self.de.hi = reset_bit(self.de.lo, 5)
            case 0xAC: self.hl.hi = reset_bit(self.hl.hi, 5)
            case 0xAD: self.hl.hi = reset_bit(self.hl.lo, 5)
            case 0xAE: self._write_memory(self.hl.value, reset_bit(self._read_memory(self.hl.value), 5))
            case 0xAF: self.af.hi = reset_bit(self.af.hi, 5)
            case 0xB0: self.bc.hi = reset_bit(self.bc.hi, 6)
            case 0xB1: self.bc.hi = reset_bit(self.bc.lo, 6)
            case 0xB2: self.de.hi = reset_bit(self.de.hi, 6)
            case 0xB3: self.de.hi = reset_bit(self.de.lo, 6)
            case 0xB4: self.hl.hi = reset_bit(self.hl.hi, 6)
            case 0xB5: self.hl.hi = reset_bit(self.hl.lo, 6)
            case 0xB6: self._write_memory(self.hl.value, reset_bit(self._read_memory(self.hl.value), 6))
            case 0xB7: self.af.hi = reset_bit(self.af.hi, 6)
            case 0xB8: self.bc.hi = reset_bit(self.bc.hi, 7)
            case 0xB9: self.bc.hi = reset_bit(self.bc.lo, 7)
            case 0xBA: self.de.hi = reset_bit(self.de.hi, 7)
            case 0xBB: self.de.hi = reset_bit(self.de.lo, 7)
            case 0xBC: self.hl.hi = reset_bit(self.hl.hi, 7)
            case 0xBD: self.hl.hi = reset_bit(self.hl.lo, 7)
            case 0xBE: self._write_memory(self.hl.value, reset_bit(self._read_memory(self.hl.value), 7))
            case 0xBF: self.af.hi = reset_bit(self.af.hi, 7)
            case _: raise Exception(f"Unknown prefix operation encountered 0x{format(opcode.code, '02x')} - {opcode.mnemonic}")

        return opcode.cycles


    def _do_restart(self, opcode: OpCode) -> int:
        '''
        Push current program counter to stack and then restart from predefined address (0x0000 + n)

        :return the number of cycles needed to execute this operation
        '''

        self._push_word_to_stack(self.program_counter)

        match opcode.code:
            case 0xFF: self.program_counter = 0x38

        return opcode.cycles

    def _do_rl(self, opcode: OpCode, through_carry=False) -> int:
        '''
        Rotate value right

        :return the number of cycles needed to execute this operation
        '''

        def do_rl(val):
            most_significant_bit = get_bit_val(val, 7)
            carry_bit = 1 if self._is_carry_flag_set() else 0
            res = (val << 1) | (carry_bit  if through_carry else most_significant_bit)

            self._update_zero_flag(res == 0)
            self._update_carry_flag(most_significant_bit == 1)
            self._update_half_carry_flag(False)
            self._update_sub_flag(False)

            return res

        match opcode.code:
            case 0x00: self.bc.hi = do_rl(self.bc.hi)
            case 0x01: self.bc.lo = do_rl(self.bc.lo)
            case 0x02: self.de.hi = do_rl(self.de.hi)
            case 0x03: self.de.lo = do_rl(self.de.lo)
            case 0x04: self.hl.hi = do_rl(self.hl.hi)
            case 0x05: self.hl.lo = do_rl(self.hl.lo)
            case 0x06: self._write_memory(self.hl.value, do_rl(self._read_memory(self.hl.value)))
            case 0x07: self.af.hi = do_rl(self.af.hi)
            case 0x10: self.bc.hi = do_rl(self.bc.hi)
            case 0x11: self.bc.lo = do_rl(self.bc.lo)
            case 0x12: self.de.hi = do_rl(self.de.hi)
            case 0x13: self.de.lo = do_rl(self.de.lo)
            case 0x14: self.hl.hi = do_rl(self.hl.hi)
            case 0x15: self.hl.lo = do_rl(self.hl.lo)
            case 0x16: self._write_memory(self.hl.value, do_rl(self._read_memory(self.hl.value)))
            case 0x17: self.af.hi = do_rl(self.af.hi)
            case _: raise Exception(f"Unknown prefix operation encountered 0x{format(opcode.code, '02x')} - {opcode.mnemonic}")

        return opcode.cycles

    def _do_rlca(self, opcode: OpCode) -> int:
        '''
        Rotate A register left setting carry to bit 7, ensuring zero flag is set to 0
        '''

        most_significant_bit = get_bit_val(self.af.hi, 7)
        res =  (self.af.hi << 1) | most_significant_bit

        self._update_zero_flag(False)
        self._update_carry_flag(most_significant_bit == 1)
        self._update_half_carry_flag(False)
        self._update_sub_flag(False)

        self.af.hi = res
        return opcode.cycles

    def _do_rla(self, opcode: OpCode) -> int:
        '''
        Rotate A register left through the carry flag, ensuring zero flag is set to 0
        '''

        most_significant_bit = get_bit_val(self.af.hi, 7)
        carry_bit = 1 if self._is_carry_flag_set() else 0
        res =  (self.af.hi << 1) | carry_bit

        self._update_zero_flag(False)
        self._update_carry_flag(most_significant_bit == 1)
        self._update_half_carry_flag(False)
        self._update_sub_flag(False)

        self.af.hi = res
        return opcode.cycles

    def _do_rra(self, opcode: OpCode) -> int:
        '''
        Rotate A register right through the carry flag, ensuring zero flag is set to 0
        '''

        least_significant_bit = get_bit_val(self.af.hi, 0)
        carry_bit = 1 if self._is_carry_flag_set() else 0
        res = (carry_bit << 7) | (self.af.hi >> 1)

        self._update_zero_flag(False)
        self._update_carry_flag(least_significant_bit == 1)
        self._update_half_carry_flag(False)
        self._update_sub_flag(False)

        self.af.hi = res
        return opcode.cycles

    def _do_rrca(self, opcode: OpCode) -> int:
        '''
        Rotate A register rigjt setting carry to bit 0, ensuring zero flag is set to 0
        '''

        least_significant_bit = get_bit_val(self.af.hi, 0)
        res =  (least_significant_bit << 7) | (self.af.hi >> 1)

        self._update_zero_flag(False)
        self._update_carry_flag(least_significant_bit == 1)
        self._update_half_carry_flag(False)
        self._update_sub_flag(False)

        self.af.hi = res
        return opcode.cycles

    def _do_rr(self, opcode: OpCode, through_carry=False) -> int:
        '''
        Rotate value right

        :return the number of cycles needed to execute this operation
        '''

        def do_rr(val):
            least_significant_bit = get_bit_val(val, 0)
            carry_bit = 1 if self._is_carry_flag_set() else 0
            res = (carry_bit << 7 if through_carry else least_significant_bit) | (val >> 1)

            self._update_zero_flag(res == 0)
            self._update_carry_flag(least_significant_bit == 1)
            self._update_half_carry_flag(False)
            self._update_sub_flag(False)

            return res

        match opcode.code:
            case 0x08: self.bc.hi = do_rr(self.bc.hi)
            case 0x09: self.bc.lo = do_rr(self.bc.lo)
            case 0x0A: self.de.hi = do_rr(self.de.hi)
            case 0x0B: self.de.lo = do_rr(self.de.lo)
            case 0x0C: self.hl.hi = do_rr(self.hl.hi)
            case 0x0D: self.hl.lo = do_rr(self.hl.lo)
            case 0x0E: self._write_memory(self.hl.value, do_rr(self._read_memory(self.hl.value)))
            case 0x0F: self.af.hi = do_rr(self.af.hi)
            case 0x18: self.bc.hi = do_rr(self.bc.hi)
            case 0x19: self.bc.lo = do_rr(self.bc.lo)
            case 0x1A: self.de.hi = do_rr(self.de.hi)
            case 0x1B: self.de.lo = do_rr(self.de.lo)
            case 0x1C: self.hl.hi = do_rr(self.hl.hi)
            case 0x1D: self.hl.lo = do_rr(self.hl.lo)
            case 0x1E: self._write_memory(self.hl.value, do_rr(self._read_memory(self.hl.value)))
            case 0x1F: self.af.hi = do_rr(self.af.hi)
            case _: raise Exception(f"Unknown prefix operation encountered 0x{format(opcode.code, '02x')} - {opcode.mnemonic}")

        return opcode.cycles

    def _do_set(self, opcode: OpCode) -> int:
        '''
        Set bit n in given register

        :return the number of cycles needed to execute this operation
        '''

        match opcode.code:
            case 0xC0: self.bc.hi = set_bit(self.bc.hi, 0)
            case 0xC1: self.bc.lo = set_bit(self.bc.lo, 0)
            case 0xC2: self.de.hi = set_bit(self.de.hi, 0)
            case 0xC3: self.de.hi = set_bit(self.de.lo, 0)
            case 0xC4: self.hl.hi = set_bit(self.hl.hi, 0)
            case 0xC5: self.hl.hi = set_bit(self.hl.lo, 0)
            case 0xC6: self._write_memory(self.hl.value, set_bit(self._read_memory(self.hl.value), 0))
            case 0xC7: self.af.hi = set_bit(self.af.hi, 0)
            case 0xC8: self.bc.hi = set_bit(self.bc.hi, 1)
            case 0xC9: self.bc.hi = set_bit(self.bc.lo, 1)
            case 0xCA: self.de.hi = set_bit(self.de.hi, 1)
            case 0xCB: self.de.hi = set_bit(self.de.lo, 1)
            case 0xCC: self.hl.hi = set_bit(self.hl.hi, 1)
            case 0xCD: self.hl.hi = set_bit(self.hl.lo, 1)
            case 0xCE: self._write_memory(self.hl.value, set_bit(self._read_memory(self.hl.value), 1))
            case 0xCF: self.af.hi = set_bit(self.af.hi, 1)
            case 0xD0: self.bc.hi = set_bit(self.bc.hi, 2)
            case 0xD1: self.bc.hi = set_bit(self.bc.lo, 2)
            case 0xD2: self.de.hi = set_bit(self.de.hi, 2)
            case 0xD3: self.de.hi = set_bit(self.de.lo, 2)
            case 0xD4: self.hl.hi = set_bit(self.hl.hi, 2)
            case 0xD5: self.hl.hi = set_bit(self.hl.lo, 2)
            case 0xD6: self._write_memory(self.hl.value, set_bit(self._read_memory(self.hl.value), 2))
            case 0xD7: self.af.hi = set_bit(self.af.hi, 2)
            case 0xD8: self.bc.hi = set_bit(self.bc.hi, 3)
            case 0xD9: self.bc.hi = set_bit(self.bc.lo, 3)
            case 0xDA: self.de.hi = set_bit(self.de.hi, 3)
            case 0xDB: self.de.hi = set_bit(self.de.lo, 3)
            case 0xDC: self.hl.hi = set_bit(self.hl.hi, 3)
            case 0xDD: self.hl.hi = set_bit(self.hl.lo, 3)
            case 0xDE: self._write_memory(self.hl.value, set_bit(self._read_memory(self.hl.value), 3))
            case 0xDF: self.af.hi = set_bit(self.af.hi, 3)
            case 0xE0: self.bc.hi = set_bit(self.bc.hi, 4)
            case 0xE1: self.bc.hi = set_bit(self.bc.lo, 4)
            case 0xE2: self.de.hi = set_bit(self.de.hi, 4)
            case 0xE3: self.de.hi = set_bit(self.de.lo, 4)
            case 0xE4: self.hl.hi = set_bit(self.hl.hi, 4)
            case 0xE5: self.hl.hi = set_bit(self.hl.lo, 4)
            case 0xE6: self._write_memory(self.hl.value, set_bit(self._read_memory(self.hl.value), 4))
            case 0xE7: self.af.hi = set_bit(self.af.hi, 4)
            case 0xE8: self.bc.hi = set_bit(self.bc.hi, 5)
            case 0xE9: self.bc.hi = set_bit(self.bc.lo, 5)
            case 0xEA: self.de.hi = set_bit(self.de.hi, 5)
            case 0xEB: self.de.hi = set_bit(self.de.lo, 5)
            case 0xEC: self.hl.hi = set_bit(self.hl.hi, 5)
            case 0xED: self.hl.hi = set_bit(self.hl.lo, 5)
            case 0xEE: self._write_memory(self.hl.value, set_bit(self._read_memory(self.hl.value), 5))
            case 0xEF: self.af.hi = set_bit(self.af.hi, 5)
            case 0xF0: self.bc.hi = set_bit(self.bc.hi, 6)
            case 0xF1: self.bc.hi = set_bit(self.bc.lo, 6)
            case 0xF2: self.de.hi = set_bit(self.de.hi, 6)
            case 0xF3: self.de.hi = set_bit(self.de.lo, 6)
            case 0xF4: self.hl.hi = set_bit(self.hl.hi, 6)
            case 0xF5: self.hl.hi = set_bit(self.hl.lo, 6)
            case 0xF6: self._write_memory(self.hl.value, set_bit(self._read_memory(self.hl.value), 6))
            case 0xF7: self.af.hi = set_bit(self.af.hi, 6)
            case 0xF8: self.bc.hi = set_bit(self.bc.hi, 7)
            case 0xF9: self.bc.hi = set_bit(self.bc.lo, 7)
            case 0xFA: self.de.hi = set_bit(self.de.hi, 7)
            case 0xFB: self.de.hi = set_bit(self.de.lo, 7)
            case 0xFC: self.hl.hi = set_bit(self.hl.hi, 7)
            case 0xFD: self.hl.hi = set_bit(self.hl.lo, 7)
            case 0xFE: self._write_memory(self.hl.value, set_bit(self._read_memory(self.hl.value), 7))
            case 0xFF: self.af.hi = set_bit(self.af.hi, 7)
            case _: raise Exception(f"Unknown prefix operation encountered 0x{format(opcode.code, '02x')} - {opcode.mnemonic}")

        return opcode.cycles

    def _do_set_carry_flag(self, opcode: OpCode) -> int:
        '''
        Set the carry flag

        :return the number of cycles needed to execute this operation
        '''

        self._update_half_carry_flag(False)
        self._update_sub_flag(False)
        self._update_carry_flag(True)

        return opcode.cycles

    def _do_shift_left(self, opcode: OpCode) -> int:
        '''
        Shift register bits left into carry flag, least significant bit should be 0

        :Return the number of cycles needed to execute this operation
        '''

        def do_shift_left(val):
            most_significant_bit = get_bit_val(val, 7)
            res = val << 1

            self._update_zero_flag(res == 0)
            self._update_carry_flag(most_significant_bit == 1)
            self._update_half_carry_flag(False)
            self._update_sub_flag(False)

            return res

        match opcode.code:
            case 0x20: self.bc.hi = do_shift_left(self.bc.hi)
            case 0x21: self.bc.lo = do_shift_left(self.bc.lo)
            case 0x22: self.de.hi = do_shift_left(self.de.hi)
            case 0x23: self.de.lo = do_shift_left(self.de.lo)
            case 0x24: self.hl.hi = do_shift_left(self.hl.hi)
            case 0x25: self.hl.lo = do_shift_left(self.hl.lo)
            case 0x26: self._write_memory(self.hl.value, do_shift_left(self._read_memory(self.hl.value)))
            case 0x27: self.af.hi = do_shift_left(self.af.hi)
            case _: raise Exception(f"Unknown prefix operation encountered 0x{format(opcode.code, '02x')} - {opcode.mnemonic}")

        return opcode.cycles

    def _do_shift_right(self, opcode: OpCode, maintain_msb=False) -> int:
        '''
        Shift register bits right into carry flag, Most significant bit should be 0

        :return the number of cycles needed to execute this operation
        '''

        def do_shift_right(val):
            most_significant_bit = get_bit_val(val, 7)
            least_significant_bit = get_bit_val(val, 0)
            res = val >> 1
            if maintain_msb:
                res |= (most_significant_bit << 7)

            self._update_zero_flag(res == 0)
            self._update_carry_flag(least_significant_bit == 1)
            self._update_half_carry_flag(False)
            self._update_sub_flag(False)

            return res

        match opcode.code:
            case 0x28: self.bc.hi = do_shift_right(self.bc.hi)
            case 0x29: self.bc.lo = do_shift_right(self.bc.lo)
            case 0x2A: self.de.hi = do_shift_right(self.de.hi)
            case 0x2B: self.de.lo = do_shift_right(self.de.lo)
            case 0x2C: self.hl.hi = do_shift_right(self.hl.hi)
            case 0x2D: self.hl.lo = do_shift_right(self.hl.lo)
            case 0x2E: self._write_memory(self.hl.value, do_shift_right(self._read_memory(self.hl.value)))
            case 0x2F: self.af.hi = do_shift_right(self.af.hi)
            case 0x38: self.bc.hi = do_shift_right(self.bc.hi)
            case 0x39: self.bc.lo = do_shift_right(self.bc.lo)
            case 0x3A: self.de.hi = do_shift_right(self.de.hi)
            case 0x3B: self.de.lo = do_shift_right(self.de.lo)
            case 0x3C: self.hl.hi = do_shift_right(self.hl.hi)
            case 0x3D: self.hl.lo = do_shift_right(self.hl.lo)
            case 0x3E: self._write_memory(self.hl.value, do_shift_right(self._read_memory(self.hl.value)))
            case 0x3F: self.af.hi = do_shift_right(self.af.hi)
            case _: raise Exception(f"Unknown prefix operation encountered 0x{format(opcode.code, '02x')} - {opcode.mnemonic}")

        return opcode.cycles

    def _do_sub_8_bit(self, opcode: OpCode, with_carry=False) -> int:
        '''
        Performs an 8-bit sub operation and stores result in A, setting appropriate flags

        :return the number of cycles needed to execute this operation
        '''

        def do_sub(val_1: int, val_2: int) -> int:
            carry = 1 if with_carry and self._is_carry_flag_set() else 0
            res = val_1 - val_2 - carry
            res = res if res >= 0 else 256 + res

            self._update_zero_flag(res & 0xFF == 0)
            self._update_sub_flag(True)
            self._update_carry_flag(val_1 < val_2 + carry)
            self._update_half_carry_flag((val_1 & 0xF) < (val_2 & 0xF) + carry)

            return res

        match opcode.code:
            case 0x90: self.af.hi = do_sub(self.af.hi, self.bc.hi)
            case 0x91: self.af.hi = do_sub(self.af.hi, self.bc.lo)
            case 0x92: self.af.hi = do_sub(self.af.hi, self.de.hi)
            case 0x93: self.af.hi = do_sub(self.af.hi, self.de.lo)
            case 0x94: self.af.hi = do_sub(self.af.hi, self.hl.hi)
            case 0x95: self.af.hi = do_sub(self.af.hi, self.hl.lo)
            case 0x96: self.af.hi = do_sub(self.af.hi, self._read_memory(self.hl.value))
            case 0x97: self.af.hi = do_sub(self.af.hi, self.af.hi)
            case 0x98: self.af.hi = do_sub(self.af.hi, self.bc.hi)
            case 0x99: self.af.hi = do_sub(self.af.hi, self.bc.lo)
            case 0x9A: self.af.hi = do_sub(self.af.hi, self.de.hi)
            case 0x9B: self.af.hi = do_sub(self.af.hi, self.de.lo)
            case 0x9C: self.af.hi = do_sub(self.af.hi, self.hl.hi)
            case 0x9D: self.af.hi = do_sub(self.af.hi, self.hl.lo)
            case 0x9E: self.af.hi = do_sub(self.af.hi, self._read_memory(self.hl.value))
            case 0x9F: self.af.hi = do_sub(self.af.hi, self.af.hi)
            case 0xD6: self.af.hi = do_sub(self.af.hi, self._get_next_byte())
            case 0xDE: self.af.hi = do_sub(self.af.hi, self._get_next_byte())
            case _: raise Exception(f"Unknown operation encountered 0x{format(opcode.code, '02x')} - {opcode.mnemonic}")

        return opcode.cycles

    def _do_swap(self, opcode: OpCode) -> int:
        '''
        Do swap operation, swapping upper and lower nibbles of value
        '''

        def do_swap(val):
            res = (val & 0xF) | (val >> 4)
            self._update_zero_flag(res == 0)
            self._update_sub_flag(False)
            self._update_carry_flag(False)
            self._update_half_carry_flag(False)
            return res

        match opcode.code:
            case 0x30: self.bc.hi = do_swap(self.bc.hi)
            case 0x31: self.bc.lo = do_swap(self.bc.lo)
            case 0x32: self.de.hi = do_swap(self.de.hi)
            case 0x33: self.de.lo = do_swap(self.de.lo)
            case 0x34: self.hl.hi = do_swap(self.hl.hi)
            case 0x35: self.hl.lo = do_swap(self.hl.lo)
            case 0x36: self._write_memory(self.hl.value, do_swap(self._read_memory(self.hl.value)))
            case 0x37: self.af.hi = do_swap(self.af.hi)
            case _: raise Exception(f"Unknown prefix operation encountered 0x{format(opcode.code, '02x')} - {opcode.mnemonic}")

        return opcode.cycles

    def _do_xor(self, opcode: OpCode) -> int:
        '''
        Performs the OR operation and sets appropriate status flags

        :return the number of cycles needed to execute this operation
        '''

        match opcode.code:
            case 0xA8:
                self.af.hi ^= self.bc.hi
                val = self.af.hi
            case 0xA9:
                self.af.hi ^= self.bc.lo
                val = self.af.hi
            case 0xAA:
                self.af.hi ^= self.de.hi
                val = self.af.hi
            case 0xAB:
                self.af.hi ^= self.de.lo
                val = self.af.hi
            case 0xAC:
                self.af.hi ^= self.hl.hi
                val = self.af.hi
            case 0xAD:
                self.af.hi ^= self.hl.lo
                val = self.af.hi
            case 0xAE:
                self.af.hi ^= self._read_memory(self.hl.value)
                val = self.af.hi
            case 0xAF:
                self.af.hi ^= self.af.hi
                val = self.af.hi
            case 0xEE:
                self.af.hi ^= self._get_next_byte()
                val = self.af.hi
            case _: raise Exception(f"Unknown operation encountered 0x{format(opcode.code, '02x')} - {opcode.mnemonic}")

        self._update_zero_flag(val == 0)
        self._update_half_carry_flag(False)
        self._update_sub_flag(False)
        self._update_carry_flag(False)

        return opcode.cycles

    # flake8: noqa: E741 E501
    def _debug(self):
        # a = format(self.af.hi, '02X')
        # f = format(self.af.lo, '02X')
        # b = format(self.bc.hi, '02X')
        # c = format(self.bc.lo, '02X')
        # d = format(self.de.hi, '02X')
        # e = format(self.de.lo, '02X')
        # h = format(self.hl.hi, '02X')
        # l = format(self.hl.lo, '02X')
        af = format(self.af.value, '04X')
        bc = format(self.bc.value, '04X')
        de = format(self.de.value, '04X')
        hl = format(self.hl.value, '04X')
        sp = format(self.stack_pointer, '04X')
        pc = format(self.program_counter, '04X')

        pc_1 = format(self._read_memory(self.program_counter), '02X')
        pc_2 = format(self._read_memory(self.program_counter + 1), '02X')
        pc_3 = format(self._read_memory(self.program_counter + 2), '02X')
        pc_4 = format(self._read_memory(self.program_counter + 3), '02X')

        # with open("debug.txt", "a") as debug_file:
        #     debug_file.write(f'A: {a} F: {f} B: {b} C: {c} D: {d} E: {e} H: {h} L: {l} SP: {sp} PC: 00:{pc} ({pc_1} {pc_2} {pc_3} {pc_4})\n')

        # with open("debug.txt", "a") as debug_file:
        #     debug_file.write(f"AF: {af} BC: {bc} DE: {de} HL: {hl} {format(self.program_counter, '04X')} - {opcode.mnemonic}\n")

        with open("debug.txt", "a") as debug_file:
            debug_file.write(f'SP: {sp} PC: 00:{pc} ({pc_1} {pc_2} {pc_3} {pc_4})\n')