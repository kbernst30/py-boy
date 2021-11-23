from enum import Enum

from constants import PROGRAM_COUNTER_INIT, STACK_POINTER_INIT

from ops import OpCode, Operation, opcodes_map
from mmu import Mmu


class RegisterPair(Enum):
    AF = "REGISTER_AF"
    BC = "REGISTER_BC"
    DE = "REGISTER_DE"
    HL = "REGISTER_HL"


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
        self.af = 0
        self.bc = 0
        self.de = 0
        self.hl = 0

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
            case Operation.DI: return self._do_disable_interrupts(opcode)
            case Operation.JP: return self._do_jump(opcode)
            case Operation.LD: return self._do_load(opcode)
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

    def _get_next_word(self) -> int:
        '''
        Gets the next 2 bytes at the location of the program counter. CPU is little endian

        :return an int representing the next two bytes in memory, properly made for little endian
        '''

        first_byte = self._get_next_byte()
        second_byte = self._get_next_byte()
        return ((second_byte << 8) | first_byte) & 0xFFFF

    def _do_disable_interrupts(self, opcode: OpCode) -> int:
        '''
        Disable interrupts

        :return the number of cycles needed to execute this operation
        '''

        self.interrupts_enabled = False
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

    def _do_load(self, opcode: OpCode) -> int:
        '''
        Do a load instruction.

        :return the number of cycles needed to execute this operation
        '''

        match opcode.code:
            case 0x31: self.stack_pointer = self._get_next_word()
            case _: raise Exception(f"Unknown operation encountered 0x{format(opcode.code, '02x')} - {opcode.mnemonic}")

        return opcode.cycles

    def _write_register_pair(self, pair: RegisterPair, data: int):
        pass
