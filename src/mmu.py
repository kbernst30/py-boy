import logging


logger = logging.getLogger(__name__)


class Mmu:
    '''
    Memory Management Unit for the Gameboy. Memory has a 16 bit address bus and is broken down as follows:
        0000 - 3FFF	    16 KiB ROM bank 00	            From cartridge, usually a fixed bank
        4000 - 7FFF	    16 KiB ROM Bank 01~NN	        From cartridge, switchable bank via mapper (if any)
        8000 - 9FFF	    8 KiB Video RAM (VRAM)	        In CGB mode, switchable bank 0/1
        A000 - BFFF	    8 KiB External RAM	            From cartridge, switchable bank if any
        C000 - CFFF	    4 KiB Work RAM (WRAM)
        D000 - DFFF	    4 KiB Work RAM (WRAM)	        In CGB mode, switchable bank 1~7
        E000 - FDFF	    Mirror of C000~DDFF (ECHO RAM)	Nintendo says use of this area is prohibited.
        FE00 - FE9F	    Sprite attribute table (OAM)
        FEA0 - FEFF	    Not Usable	                    Nintendo says use of this area is prohibited
        FF00 - FF7F	    I/O Registers
        FF80 - FFFE	    High RAM (HRAM)
        FFFF - FFFF	    Interrupt Enable register (IE)
    '''

    MEMORY_SIZE = 0x10000

    def __init__(self):

        self.memory = [0 for _ in range(self.MEMORY_SIZE)]

        # Initial MMU state
        self.memory[0xFF05] = 0x00
        self.memory[0xFF06] = 0x00
        self.memory[0xFF07] = 0x00
        self.memory[0xFF10] = 0x80
        self.memory[0xFF11] = 0xBF
        self.memory[0xFF12] = 0xF3
        self.memory[0xFF14] = 0xBF
        self.memory[0xFF16] = 0x3F
        self.memory[0xFF17] = 0x00
        self.memory[0xFF19] = 0xBF
        self.memory[0xFF1A] = 0x7F
        self.memory[0xFF1B] = 0xFF
        self.memory[0xFF1E] = 0xBF
        self.memory[0xFF20] = 0xFF
        self.memory[0xFF21] = 0x00
        self.memory[0xFF22] = 0x00
        self.memory[0xFF23] = 0xBF
        self.memory[0xFF24] = 0x77
        self.memory[0xFF25] = 0xF3
        self.memory[0xFF26] = 0xF1
        self.memory[0xFF40] = 0x91
        self.memory[0xFF42] = 0x00
        self.memory[0xFF43] = 0x00
        self.memory[0xFF45] = 0x00
        self.memory[0xFF47] = 0xFC
        self.memory[0xFF48] = 0xFF
        self.memory[0xFF49] = 0xFF
        self.memory[0xFF4A] = 0x00
        self.memory[0xFF4B] = 0x00
        self.memory[0xFFFF] = 0x00

    def read_byte(self, addr: int) -> int:
        '''
        Read a byte from memory and return

        TODO deal with addresses on case basis
        '''

        return self.memory[addr]

    def write_byte(self, addr: int, data: int):
        '''
        Write a byte to memory

        TODO deal with addresses on case basis
        '''

        if addr < 0x8000:
            # Restricted ROM access here... do not write
            # TODO Handle banking
            pass

        elif addr >= 0xE000 and addr < 0xFE00:
            # If we are writing to ECHO (E000-FDFF) we must write to working RAM (C000-CFFF) as well
            pass

        elif addr >= 0xFEA0 and addr < 0xFF00:
            # Restricted area - do NOT allow writing
            logger.warn(f"Attempted write to restricted addr - 0x{format(addr, '0x')}")

        else:
            self.memory[addr] = data & 0xFF

    def load_rom(self, rom):
        end_addr = 0x8000
        for i in range(end_addr):
            self.memory[i] = rom.data[i]
