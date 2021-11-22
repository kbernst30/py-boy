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

        self.memory[addr] = data & 0xFF

    def load_rom(self, rom):
        end_addr = 0x8000
        for i in range(end_addr):
            self.memory[i] = rom.data[i]
