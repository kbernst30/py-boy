from enum import Enum

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

    def execute(self):
        '''
        Get the next operation from memory, decode, and execute
        '''

        op = self.memory.read_byte(self.program_counter)
        self.program_counter += 1

        match op:
            case _: raise Exception(f"Unknown operation encountered 0x{format(op, '02x')}")

    def _write_register_pair(self, pair: RegisterPair, data: int):
        pass
