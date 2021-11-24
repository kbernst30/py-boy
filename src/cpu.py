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
        return ((self.lo << 8) | self.hi) & 0xFFFF

    @value.setter
    def value(self, value):
        self.lo = value >> 8
        self.hi = value & 0xF

    def increment(self):
        self.value = self.value + 1
        if self.value > 255:
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

    def reset(self):
        '''
        Reset the CPU and all registers to appropriate values
        '''

        self.program_counter = PROGRAM_COUNTER_INIT
        self.stack_pointer = STACK_POINTER_INIT

    def execute(self) -> int:
        '''
        Get the next operation from memory, decode, and execute

        :return the number of cycles the operation took
        '''

        op = self.memory.read_byte(self.program_counter)
        opcode = opcodes_map[op]
        self.program_counter += 1

        match opcode.operation:
            case Operation.CALL: return self._do_call(opcode)
            case Operation.DI: return self._do_disable_interrupts(opcode)
            case Operation.INC: return self._do_increment_8_bit(opcode)
            case Operation.JP: return self._do_jump(opcode)
            case Operation.JR: return self._do_jump_relative(opcode)
            case Operation.LD: return self._do_load(opcode)
            case Operation.LDH: return self._do_load_h(opcode)
            case Operation.NOP: return opcode.cycles
            case _: raise Exception(f"Unknown operation encountered 0x{format(op, '02x')} - {opcode.mnemonic}")

    def _get_next_byte(self) -> int:
        '''
        Gets the next byte at the location of the program counter, and increments the program counter

        :return an int representing the next byte in memory
        '''

        byte = self.memory.read_byte(self.program_counter)
        self.program_counter += 1
        return byte & 0xFF

    def _get_next_byte_signed(self) -> int:
        '''
        Gets the next byte at the location of the program counter, as an 8-bit signed,
        and increments the program counter

        :return an int representing the next signed byte in memory
        '''

        byte = self._get_next_byte()
        return byte - 256

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

    def _update_zero_flag(self, val: int):
        '''
        Set zero flag if val is zero, otherwise reset it
        '''

        if val == 0:
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

    def _push_byte_to_stack(self, byte: int):
        '''
        Push a byte value onto the stack and decrement the stack pointer
        '''

        self.memory.write_byte(self.stack_pointer, byte)
        self.stack_pointer -= 1

    def _pop_byte_from_stack(self) -> int:
        '''
        Pop a byte from the stack and increment the stack pointer

        :return the popped value
        '''

        val = self.memory.read_byte(self.stack_pointer)
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

    def _do_call(self, opcode: OpCode) -> int:
        '''
        Pushes the current PC onto the stack and sets the program counter to the appropriate address,
        if conditionally approved

        :return the number of cycles needed to execute this operation
        '''

        cycles = opcode.cycles

        match opcode.code:
            case 0xCD:
                addr = self._get_next_word()
                self._push_word_to_stack(self.program_counter)
                self.program_counter = addr

            case _: raise Exception(f"Unknown operation encountered 0x{format(opcode.code, '02x')} - {opcode.mnemonic}")

        return cycles

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
            case 0x14:
                self.de.increment_hi()
                val = self.de.hi
            case 0x1C:
                self.de.increment_lo()
                val = self.de.lo

            case _: raise Exception(f"Unknown operation encountered 0x{format(opcode.code, '02x')} - {opcode.mnemonic}")

        self._update_zero_flag(val)
        self._update_sub_flag(False)
        self._update_half_carry_flag(val & 0xF == 0)

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
            case _: raise Exception(f"Unknown operation encountered 0x{format(opcode.code, '02x')} - {opcode.mnemonic}")

        return cycles

    def _do_load(self, opcode: OpCode) -> int:
        '''
        Do a load instruction.

        :return the number of cycles needed to execute this operation
        '''

        match opcode.code:
            case 0x0E: self.bc.lo = self._get_next_byte()
            case 0x11: self.de.value = self._get_next_word()
            case 0x12: self.memory.write_byte(self.de.value, self.af.hi)
            case 0x21: self.hl.value = self._get_next_word()
            case 0x2A:
                self.af.hi = self.memory.read_byte(self.hl.value)
                self.hl.increment()
            case 0x31: self.stack_pointer = self._get_next_word()
            case 0x47: self.bc.hi = self.af.hi
            case 0x7C: self.af.hi = self.hl.hi
            case 0x7D: self.af.hi = self.hl.lo
            case 0x3E: self.af.hi = self._get_next_byte()
            case 0xEA: self.memory.write_byte(self._get_next_word(), self.af.hi)
            case _: raise Exception(f"Unknown operation encountered 0x{format(opcode.code, '02x')} - {opcode.mnemonic}")

        return opcode.cycles

    def _do_load_h(self, opcode: OpCode) -> int:
        '''
        Do a load instruction where address in instruction is least significant byte of address
        and most significant byte is 0xFF

        :return the number of cycles needed to execute this operation
        '''

        match opcode.code:
            case 0xE0: self.memory.write_byte(0xFF00 | self._get_next_byte(), self.af.hi)
            case _: raise Exception(f"Unknown operation encountered 0x{format(opcode.code, '02x')} - {opcode.mnemonic}")

        return opcode.cycles

    def _write_register_pair(self, pair: RegisterPair, data: int):
        pass
