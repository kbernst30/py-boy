import logging

from constants import CURRENT_SCANLINE_ADDR, DIVIDER_REGISTER_ADDR, MAXIMUM_RAM_BANKS, RAM_BANK_SIZE


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

        # RAM banks to be used for external RAM
        self.ram_banks = [0 for _ in range(MAXIMUM_RAM_BANKS * RAM_BANK_SIZE)]

        # RAM access is disabled by default, and must explicitly be enabled
        self.enable_ram = False

        # Restrict some areas of memory if LCD is in certain modes
        self.oam_access = True
        self.color_pallette_access = True  # TODO CGB only
        self.vram_access = True

        self.reset()

    def reset(self):
        '''
        Reset state of MMU
        '''

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

        TODO deal with addresses on case basis - basically need to deal with MBC modes
        '''

        is_reading_restricted_oam = addr >= 0xFE00 and addr <= 0xFE9F and not self.oam_access
        is_reading_restricted_vram = addr >= 0x8000 and addr <= 0x9FFF and not self.vram_access

        if is_reading_restricted_oam or is_reading_restricted_vram:
            # Reading something currently restricted, return garbage (0xFF)
            return 0xFF
        else:
            return self.memory[addr]

    def write_byte(self, addr: int, data: int):
        '''
        Write a byte to memory

        TODO deal with addresses on case basis
        '''

        is_writing_restricted_oam = addr >= 0xFE00 and addr <= 0xFE9F and not self.oam_access
        is_writing_restricted_vram = addr >= 0x8000 and addr <= 0x9FFF and not self.vram_access

        if is_writing_restricted_oam or is_writing_restricted_vram:
            # IF attempting to write to currently restricted memory, just do nothing
            pass

        elif addr < 0x8000:
            # Restricted ROM access here... do not write
            # TODO Handle banking
            self._handle_banking(addr, data)

        elif addr >= 0xE000 and addr < 0xFE00:
            # If we are writing to ECHO (E000-FDFF) we must write to working RAM (C000-CFFF) as well
            pass

        elif addr >= 0xFEA0 and addr < 0xFF00:
            # Restricted area - do NOT allow writing
            pass
            # logger.warn(f"Attempted write to restricted addr - 0x{format(addr, '0x')}")

        elif addr == DIVIDER_REGISTER_ADDR or addr == CURRENT_SCANLINE_ADDR:
            # We cannot write here directly - reset to 0
            self.memory[addr] = 0

        else:
            self.memory[addr] = data & 0xFF

    def load_rom(self, rom):
        end_addr = 0x8000
        for i in range(end_addr):
            self.memory[i] = rom.data[i]

    def update_scanline(self):
        '''
        Scanline cannot be writen to directly, so update it using this utility
        '''

        self.memory[CURRENT_SCANLINE_ADDR] += 1

    def reset_scanline(self):
        '''
        We need to be able to reset the current scanline to zero
        '''

        self.memory[CURRENT_SCANLINE_ADDR] = 0

    def restrict_oam_access(self):
        '''
        Restrict access to OAM - needed for certain LCD modes
        '''

        self.oam_access = False

    def open_oam_access(self):
        '''
        Open access to OAM - needed for certain LCD modes
        '''

        self.oam_access = True

    def restrict_color_pallette_access(self):
        '''
        Restrict access to CGB Color Pallette - needed for certain LCD modes
        '''

        self.color_pallette_access = False

    def open_color_pallette_access(self):
        '''
        Open access to CGB Color Pallette - needed for certain LCD modes
        '''

        self.color_pallette_access = True

    def restrict_vram_access(self):
        '''
        Restrict access to VRAM - needed for certain LCD modes
        '''

        self.vram_access = False

    def open_vram_access(self):
        '''
        Open access to VRAM - needed for certain LCD modes
        '''

        self.vram_access = True

    def _handle_banking(self, addr: int, data: int):
        '''
        Writing to address 0x0000 - 0x7FFF does stuff to the internal MMU's state in terms
        of dealing with ROM and RAM banking. Handle these cases here
        '''

        # If writing to address less than 0x2000, we are enabling or disabling RAM access
        if addr < 0x2000:
            if (data & 0xF) == 0xA:
                # If the lower nibble of data being written is 0xA (for some reason) then we enable
                # RAM, otherwise disable
                self.enable_ram = True
            else:
                self.enable_ram = False
