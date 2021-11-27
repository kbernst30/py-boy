import logging

from enum import Enum

from constants import PROGRAM_COUNTER_INIT, STACK_POINTER_INIT

from ops import OpCode, Operation, opcodes_map
from mmu import Mmu
from utils import get_bit_val, reset_bit, set_bit


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
            self.value = 255

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
        #     self._debug()
        #     self.debug_ctr += 1
        #     self.debug_set.add(f"{format(op, '02X')} - {opcode.mnemonic} - {opcode.cycles} - {opcode.alt_cycles}")

        #     if self.debug_ctr == 16510:
        #         for item in self.debug_set:
        #             print(item)

        self.program_counter += 1

        # print(opcode.mnemonic)

        match opcode.operation:
            case Operation.ADC: return self._do_add_8_bit(opcode, with_carry=True)
            case Operation.ADD: return self._do_add_8_bit(opcode)
            case Operation.AND: return self._do_and(opcode)
            case Operation.CALL: return self._do_call(opcode)
            case Operation.CCF: return self._do_complement_carry(opcode)
            case Operation.CP: return self._do_compare(opcode)
            case Operation.DEC: return self._do_decrement_8_bit(opcode)
            case Operation.DEC_16_BIT: return self._do_decrement_16_bit(opcode)
            case Operation.DI: return self._do_disable_interrupts(opcode)
            case Operation.INC: return self._do_increment_8_bit(opcode)
            case Operation.INC_16_BIT: return self._do_increment_16_bit(opcode)
            case Operation.JP: return self._do_jump(opcode)
            case Operation.JR: return self._do_jump_relative(opcode)
            case Operation.LD: return self._do_load(opcode)
            case Operation.LDH: return self._do_load_h(opcode)
            case Operation.NOP: return opcode.cycles
            case Operation.OR: return self._do_or(opcode)
            case Operation.POP: return self._do_pop(opcode)
            case Operation.PUSH: return self._do_push(opcode)
            case Operation.RET: return self._do_return(opcode)
            case Operation.RST: return self._do_restart(opcode)
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
        # if addr == 0xFF01:
        #     print(str(self.debug_ctr) + " - " + format(addr, '0x'), format(data, '0x'))
        #     self.debug_ctr += 1

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

            return res

        match opcode.code:
            case 0x80: self.af.hi = do_add(self.af.hi, self.bc.hi)
            case 0x83: self.af.hi = do_add(self.af.hi, self.de.lo)
            case 0x88: self.af.hi = do_add(self.af.hi, self.bc.hi)
            case 0x89: self.af.hi = do_add(self.af.hi, self.bc.lo)
            case 0xC6: self.af.hi = do_add(self.af.hi, self._get_next_byte())
            case _: raise Exception(f"Unknown operation encountered 0x{format(opcode.code, '02x')} - {opcode.mnemonic}")

        return opcode.cycles

    def _do_and(self, opcode: OpCode) -> int:
        '''
        Performs the AND operation and sets appropriate status flags

        :return the number of cycles needed to execute this operation
        '''

        match opcode.code:
            case 0xE6:
                self.af.hi &= self._get_next_byte()
                val = self.af.hi
            case _: raise Exception(f"Unknown operation encountered 0x{format(opcode.code, '02x')} - {opcode.mnemonic}")

        self._update_zero_flag(val == 0)
        self._update_half_carry_flag(True)
        self._update_sub_flag(False)
        self._update_carry_flag(False)

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
            res = val_1 - val_2

            self._update_zero_flag(res & 0xFF == 0)
            self._update_sub_flag(True)
            self._update_carry_flag(val_1 < val_2)
            self._update_half_carry_flag((val_1 & 0xF) - (val_2 & 0xF) < 0)

        match opcode.code:
            case 0xBF: do_cp(self.af.hi, self.af.hi)
            case 0xFE: do_cp(self.af.hi, self._get_next_byte())
            case _: raise Exception(f"Unknown operation encountered 0x{format(opcode.code, '02x')} - {opcode.mnemonic}")

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
            case _: raise Exception(f"Unknown operation encountered 0x{format(opcode.code, '02x')} - {opcode.mnemonic}")

        return opcode.cycles

    def _do_disable_interrupts(self, opcode: OpCode) -> int:
        '''
        Disable interrupts

        :return the number of cycles needed to execute this operation
        '''

        self.interrupts_enabled = False
        return opcode.cycles

    def _do_increment_8_bit(self, opcode: OpCode) -> int:
        '''
        Do 8-bit increment instruction and update flags as necessary

        :return the number of cycles need to execute this operation
        '''

        match opcode.code:
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
            case _: raise Exception(f"Unknown operation encountered 0x{format(opcode.code, '02x')} - {opcode.mnemonic}")

        return opcode.cycles

    def _do_jump(self, opcode: OpCode) -> int:
        '''
        Do jump to instruction. Update program counter to new position

        :return the number of cycles needed to execute this operation
        '''

        cycles = opcode.cycles

        match opcode.code:
            case 0xC3: self.program_counter = self._get_next_word()
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
            case _: raise Exception(f"Unknown operation encountered 0x{format(opcode.code, '02x')} - {opcode.mnemonic}")

        return cycles

    def _do_load(self, opcode: OpCode) -> int:
        '''
        Do a load instruction.

        :return the number of cycles needed to execute this operation
        '''

        match opcode.code:
            case 0x01: self.bc.value = self._get_next_word()
            case 0x06: self.bc.hi = self._get_next_byte()
            case 0x08: self._write_memory(self._get_next_word(), self.stack_pointer)
            case 0x0E: self.bc.lo = self._get_next_byte()
            case 0x11: self.de.value = self._get_next_word()
            case 0x12: self._write_memory(self.de.value, self.af.hi)
            case 0x1A: self.af.hi = self._read_memory(self.de.value)
            case 0x21: self.hl.value = self._get_next_word()
            case 0x22:
                self._write_memory(self.hl.value, self.af.hi)
                self.hl.increment()
            case 0x2A:
                self.af.hi = self._read_memory(self.hl.value)
                self.hl.increment()
            case 0x31: self.stack_pointer = self._get_next_word()
            case 0x32:
                self._write_memory(self.hl.value, self.af.hi)
                self.hl.decrement()
            case 0x44: self.bc.hi = self.hl.hi
            case 0x47: self.bc.hi = self.af.hi
            case 0x57: self.de.hi = self.af.hi
            case 0x60: self.hl.hi = self.bc.hi
            case 0x67: self.hl.hi = self.af.hi
            case 0x6F: self.hl.lo = self.af.hi
            case 0x73: self._write_memory(self.hl.value, self.de.lo)
            case 0x77: self._write_memory(self.hl.value, self.af.hi)
            case 0x78: self.af.hi = self.bc.hi
            case 0x7A: self.af.hi = self.de.hi
            case 0x7C: self.af.hi = self.hl.hi
            case 0x7D: self.af.hi = self.hl.lo
            case 0x7F: self.af.hi = self.af.hi
            case 0x3E: self.af.hi = self._get_next_byte()
            case 0xEA: self._write_memory(self._get_next_word(), self.af.hi)
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
            case 0xb1:
                self.af.hi |= self.bc.lo
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
            case 0xF1: self.af.value = self._pop_word_from_stack()
            case _: raise Exception(f"Unknown operation encountered 0x{format(opcode.code, '02x')} - {opcode.mnemonic}")

        return opcode.cycles

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
            case _: raise Exception(f"Unknown operation encountered 0x{format(opcode.code, '02x')} - {opcode.mnemonic}")

        return cycles

    def _do_restart(self, opcode: OpCode) -> int:
        '''
        Push current program counter to stack and then restart from predefined address (0x0000 + n)

        :return the number of cycles needed to execute this operation
        '''

        self._push_word_to_stack(self.program_counter)

        match opcode.code:
            case 0xFF: self.program_counter = 0x38

        return opcode.cycles

    def _do_xor(self, opcode: OpCode) -> int:
        '''
        Performs the OR operation and sets appropriate status flags

        :return the number of cycles needed to execute this operation
        '''

        match opcode.code:
            case 0xA9:
                self.af.hi ^= self.bc.lo
                val = self.af.hi
            case _: raise Exception(f"Unknown operation encountered 0x{format(opcode.code, '02x')} - {opcode.mnemonic}")

        self._update_zero_flag(val == 0)
        self._update_half_carry_flag(False)
        self._update_sub_flag(False)
        self._update_carry_flag(False)

        return opcode.cycles

    # flake8: noqa: E741 E501
    def _debug(self):
        a = format(self.af.hi, '02X')
        f = format(self.af.lo, '02X')
        b = format(self.bc.hi, '02X')
        c = format(self.bc.lo, '02X')
        d = format(self.de.hi, '02X')
        e = format(self.de.lo, '02X')
        h = format(self.hl.hi, '02X')
        l = format(self.hl.lo, '02X')
        sp = format(self.stack_pointer, '04X')
        pc = format(self.program_counter, '04X')

        pc_1 = format(self._read_memory(self.program_counter), '02X')
        pc_2 = format(self._read_memory(self.program_counter + 1), '02X')
        pc_3 = format(self._read_memory(self.program_counter + 2), '02X')
        pc_4 = format(self._read_memory(self.program_counter + 3), '02X')

        with open("debug.txt", "a") as debug_file:
            debug_file.write(f'A: {a} F: {f} B: {b} C: {c} D: {d} E: {e} H: {h} L: {l} SP: {sp} PC: 00:{pc} ({pc_1} {pc_2} {pc_3} {pc_4})\n')
