from enum import Enum
from constants import (
    BACKGROUND_SCROLL_X,
    BACKGROUND_SCROLL_Y,
    CURRENT_SCANLINE_ADDR,
    CYCLES_PER_SCANLINE,
    GB_COLORS,
    LCD_CONTROL_ADDR,
    LCD_STATUS_ADDR,
    MAX_SCANLINE_VALUE
)
from mmu import Mmu
from utils import get_bit_val, is_bit_set, set_bit


class LcdControl:
    '''
    LCDC - the main LCD control register, located in memory. The different
    bits control what and how we display on screen:
      7 - LCD/PPU enabled, 0 = disabled, 1 = enabled
      6 - Window tile map area, 0 = 0x9800-0x9BFF, 1 = 0x9C00-0x9FFF
      5 - Window enabled, 0 = disabled, 1 = enabled
      4 - BG and Window tile data area, 0 = 0x8800-0x97FF, 1 = 0x8000-0x8FFFF
      3 - BG tile map area, 0 = 0x9800-0x9BFF, 1 = 0x9C00-0x9FFF
      2 - Object size, 0 = 8x8, 1 = 8x16
      1 - Object enabled, 0 = disabled, 1 = enabled
      0 - Background enabled, 0 = disabled, 1 = enabled
    '''

    def __init__(self, memory: Mmu):
        self.memory = memory

    def is_lcd_enabled(self) -> bool:
        '''
        Return True if LCD is enabled, False otherwise
        '''

        return is_bit_set(self.memory.read_byte(LCD_CONTROL_ADDR), 7)

    def get_background_tile_data_area(self) -> int:
        '''
        Get the start address for the background/window tiles
        '''

        return 0x8000 if is_bit_set(self.memory.read_byte(LCD_CONTROL_ADDR), 4) else 0x9000

    def is_background_tile_data_addressing_signed(self) -> bool:
        '''
        Depending on addressing mode for backgroudn tiles, determine if the identification number
        for tiles is signed or unsigned. If we are addressing in mode 1 (starting at 0x9000) it should
        be signed, which will allow us to look back to address 0x8800
        '''

        return not is_bit_set(self.memory.read_byte(LCD_CONTROL_ADDR), 4)

    def is_background_enabled(self) -> bool:
        '''
        Return True if the Background is currently enabled and able to be drawn
        '''

        return is_bit_set(self.memory.read_byte(LCD_CONTROL_ADDR), 0)

    def get_background_tile_map_area(self) -> int:
        '''
        Gets the starting address of the current background tile map
        '''

        return 0x9C00 if is_bit_set(self.memory.read_byte(LCD_CONTROL_ADDR), 3) else 0x9800


class LcdMode(Enum):
    H_BLANK = 0
    V_BLANK = 1
    SPRITE_SEARCH = 2
    LCD_TRANSFER = 3


class LcdStatus:
    '''
    STAT - the main LCD status register, located in memory. The different bits
    indicate the status of the LCD
      6 - LYC = LY Interrupt - if enabled and LYC = LY, request LCD interrupt
      5 - Mode 2 (Searching Sprites) interrupt enabled
      4 - Mode 1 (VBlank) interrupt enabled
      3 - Mode 0 (Hblank) interrupt enabled
      2 - LYC = LY - Set if current scanline (LY) is equal to value we are comparing to (LYC)
      1, 0 - LCD mode
        00: H-Blank Mode
        01: V-Blank mode
        10: Searching Sprites Atts
        11: Transferring Data to LCD driver
    '''

    def __init__(self, memory: Mmu):
        self.memory = memory

    def get_status(self):
        self.memory.read_byte(LCD_STATUS_ADDR)

    def set_status(self):
        self.memory.write_byte(LCD_STATUS_ADDR)

    def get_mode(self) -> LcdMode:
        '''
        Returns the current LCD mode from the Status register
        '''

        msb = get_bit_val(self.memory.read_byte(LCD_STATUS_ADDR), 1)
        lsb = get_bit_val(self.memory.read_byte(LCD_STATUS_ADDR), 0)
        lcd_mode = msb << 1 | lsb

        match lcd_mode:
            case 0: return LcdMode.H_BLANK,
            case 1: return LcdMode.V_BLANK,
            case 2: return LcdMode.SPRITE_SEARCH,
            case 3: return LcdMode.LCD_TRANSFER

    def set_mode(self, mode: LcdMode):
        '''
        Set the current LCD mode into the Status register
        '''

        val = mode.value
        current_status = self.get_status()
        current_status |= val
        self.set_status(current_status)


class Ppu:

    def __init__(self, memory: Mmu):
        self.memory = memory
        self.lcd_control = LcdControl(self.memory)
        self.lcd_status = LcdStatus(self.memory)

        # It takes 456 clock cycles to draw one scanline
        self.scanline_counter = CYCLES_PER_SCANLINE

        self.debug = True

    def update_graphics(self, cycles: int):
        '''
        Attempt to update the graphics. If we have taken more than the number
        of cycles needed to update a scanline, it is time to draw it

        In reality, CPU and PPU are running in parallel but we need to do this
        a bit more synchornously
        '''

        self.update_lcd_status()

        # Only update the counter if the LCD is enabled
        if self.lcd_control.is_lcd_enabled():
            self.scanline_counter -= cycles

        # We have run the number of necessary cycles to draw a scanline
        if self.scanline_counter < 0:
            # print(self.scanline_counter)
            self.scanline_counter += CYCLES_PER_SCANLINE

            # TODO Draw the next scanline
            self.memory.update_scanline()
            scanline = self.memory.read_byte(CURRENT_SCANLINE_ADDR)

            if scanline == 144:
                # Entering VBlank, request interrupt
                pass

            elif scanline > MAX_SCANLINE_VALUE:
                self.memory.reset_scanline()

            else:
                # TODO Draw the next scanline
                pass

    def update_lcd_status(self):
        '''
        Update LCD status to ensure we are correctly drawing graphics depending on the
        state of the hardware
        '''

        if not self.lcd_control.is_lcd_enabled():
            # LCD is disabled, this means we are in VBlank, so reset scanline
            # self.scanline_counter = CYCLES_PER_SCANLINE
            # self.memory.reset_scanline()
            pass

    def get_tiles(self):
        '''
        Get all the tiles in VRAM - This is used for debugging purposes
        '''

        # Let's just start with BG tiles for now
        # Get the address that background/window tiles are in from LCD control
        is_tile_identifier_signed = self.lcd_control.is_background_tile_data_addressing_signed()
        addr_space_len = 0xFFF

        if not is_tile_identifier_signed:
            start_addr = self.lcd_control.get_background_tile_data_area()
        else:
            start_addr = self.lcd_control.get_background_tile_data_area() - int(addr_space_len / 2)

        tiles = []
        counter = 0

        current_tile = []
        for addr in range(start_addr, start_addr + addr_space_len, 2):
            # each tile occupies 16 bytes, and each line in the sprite is 2 bytes long
            # so that makes each tile 8x8 pixels
            # We have 2 bytes per line to help determine the "color" of the pixel
            # Each bit in the first byte of a line is the least significant bit of the color ID
            # and the bit in the second byte is the most significant bit. Use the color ID against
            # the pallette to get the appropriate color
            byte_1 = self.memory.read_byte(addr)
            byte_2 = self.memory.read_byte(addr + 1)

            counter += 2

            line = []

            # Loop through pixels left to right as that's the order in the tile (bit 7 - 0)
            for i in range(7, -1, -1):
                least_significant_bit = get_bit_val(byte_1, i)
                most_significant_bit = get_bit_val(byte_2, i)
                color_id = (most_significant_bit << 1) | least_significant_bit
                color = self._get_color(color_id)
                line.append(color)

            current_tile.append(line)
            if counter == 16:
                counter = 0
                tiles.append(current_tile.copy())
                current_tile = []

        return tiles

    def is_background_enabled(self) -> bool:
        return self.lcd_control.is_background_enabled()

    def get_background_tile_map(self) -> list[int]:
        '''
        Get the current background tile map to be able to determine
        which tiles to draw to the screen. Tile map can be at one of two addresses
        depending on LCD Control Bit 3, so get the appropriate address. The map is 32x32
        which is 1024 bytes (0x400)
        '''

        tile_map_len = 0x400
        tile_map_addr = self.lcd_control.get_background_tile_map_area()
        tile_map = []
        for i in range(tile_map_addr, tile_map_len):
            tile_map.append(self.memory.read_byte(i))

        return tile_map

    def get_background_scroll_x(self) -> int:
        '''
        Get the X Scroll position of the background
        '''

        return self.memory.read_byte(BACKGROUND_SCROLL_X)

    def get_background_scroll_y(self) -> int:
        '''
        Get the X Scroll position of the background
        '''

        return self.memory.read_byte(BACKGROUND_SCROLL_Y)

    def _get_color(self, color_id: int):
        '''
        Get the color based on ID and current color pallette
        '''

        pallette = self.memory.read_byte(0xFF47)  # this register is where the color pallette is

        # The pallette bits define colors as such (using color ID from 0 - 1)
        # Bit 7-6 - Color for index 3
        # Bit 5-4 - Color for index 2
        # Bit 3-2 - Color for index 1
        # Bit 1-0 - Color for index 0
        match color_id:
            case 3: color = get_bit_val(pallette, 7) << 1 | get_bit_val(pallette, 6)
            case 2: color = get_bit_val(pallette, 5) << 1 | get_bit_val(pallette, 4)
            case 1: color = get_bit_val(pallette, 3) << 1 | get_bit_val(pallette, 2)
            case 0: color = get_bit_val(pallette, 1) << 1 | get_bit_val(pallette, 0)
            case _: raise Exception(f"Invalid color_id - {color_id}")

        return GB_COLORS[color]
