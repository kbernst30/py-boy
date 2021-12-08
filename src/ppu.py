from constants import (
    BACKGROUND_SCROLL_X,
    BACKGROUND_SCROLL_Y,
    COLOR_PALLETTE_ADDR,
    CURRENT_SCANLINE_ADDR,
    CURRENT_SCANLINE_COMPARE_ADDR,
    CYCLES_PER_SCANLINE,
    GB_COLORS,
    LCD_CONTROL_ADDR,
    LCD_STATUS_ADDR,
    MAX_CYCLES_PER_FRAME,
    MAX_SCANLINE_VALUE,
    SCREEN_HEIGHT,
    SCREEN_WIDTH
)
from interrupts import InterruptControl
from mmu import Mmu
from utils import Interrupt, get_bit_val, is_bit_set, LcdMode, reset_bit, set_bit


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

    def is_window_enabled(self) -> bool:
        '''
        Return True if the Window is currently enabled and should be drawn
        '''

        return is_bit_set(self.memory.read_byte(LCD_CONTROL_ADDR), 5)


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
        return self.memory.read_byte(LCD_STATUS_ADDR)

    def set_status(self, status: int):
        self.memory.write_byte(LCD_STATUS_ADDR, status)

    def get_mode(self) -> LcdMode:
        '''
        Returns the current LCD mode from the Status register
        '''

        msb = get_bit_val(self.memory.read_byte(LCD_STATUS_ADDR), 1)
        lsb = get_bit_val(self.memory.read_byte(LCD_STATUS_ADDR), 0)
        lcd_mode = msb << 1 | lsb

        # match lcd_mode:
        if lcd_mode == 0:
            return LcdMode.H_BLANK,
        elif lcd_mode == 1:
            return LcdMode.V_BLANK,
        elif lcd_mode == 2:
            return LcdMode.SPRITE_SEARCH,
        elif lcd_mode == 3:
            return LcdMode.LCD_TRANSFER

    def set_mode(self, mode: LcdMode):
        '''
        Set the current LCD mode into the Status register
        '''

        val = mode.value
        current_status = self.get_status()
        current_status |= val
        self.set_status(current_status)

    def is_hblank_stat_interrupt_enabled(self):
        '''
        Return whether or not a STAT interrupt should occur during HBlank
        '''

        return is_bit_set(self.memory.read_byte(LCD_STATUS_ADDR), 3)

    def is_vblank_stat_interrupt_enabled(self):
        '''
        Return whether or not a STAT interrupt should occur during VBlank
        '''

        return is_bit_set(self.memory.read_byte(LCD_STATUS_ADDR), 4)

    def is_oam_stat_interrupt_enabled(self):
        '''
        Return whether or not a STAT interrupt should occur during OAM search
        '''

        return is_bit_set(self.memory.read_byte(LCD_STATUS_ADDR), 5)

    def update_coincidence_flag(self, val: bool):
        '''
        Update the coincidence flag (Bit 2) based on value
        '''

        status = self.get_status()
        if val:
            status = set_bit(status, 2)
        else:
            status = reset_bit(status, 2)

        self.set_status(status)


class Ppu:

    def __init__(self, memory: Mmu, interrupts: InterruptControl):
        self.memory = memory
        self.interrupts = interrupts

        self.lcd_control = LcdControl(self.memory)
        self.lcd_status = LcdStatus(self.memory)

        # It takes 456 clock cycles to draw one scanline
        self.scanline_counter = CYCLES_PER_SCANLINE

        # Create an array to hold the state of the LCD
        self.screen = [[0 for _ in range(SCREEN_HEIGHT)] for _ in range(SCREEN_WIDTH)]

        self.debug = True

    def get_screen(self) -> "list[list[int]]":
        return self.screen

    def get_current_scanline(self) -> int:
        '''
        Return the current scanline that the PPU is working on
        '''

        return self.memory.read_byte(CURRENT_SCANLINE_ADDR)

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
        if self.scanline_counter <= 0:
            self.scanline_counter = CYCLES_PER_SCANLINE

            scanline = self.memory.read_byte(CURRENT_SCANLINE_ADDR)
            self.memory.update_scanline()

            if scanline == 144:
                self.interrupts.request_interrupt(Interrupt.V_BLANK)

            elif scanline > MAX_SCANLINE_VALUE:
                self.memory.reset_scanline()

            else:
                self.draw_scanline()

    def update_lcd_status(self):
        '''
        Update LCD status to ensure we are correctly drawing graphics depending on the
        state of the hardware
        '''

        scanline = self.memory.read_byte(CURRENT_SCANLINE_ADDR)
        scanline_compare = self.memory.read_byte(CURRENT_SCANLINE_COMPARE_ADDR)

        # TODO do i need this??
        if not self.lcd_control.is_lcd_enabled():
            # LCD is disabled, this means we are in VBlank, so reset scanline
            self.scanline_counter = CYCLES_PER_SCANLINE
            self.memory.reset_scanline()

            # Set VBlank mode to LCD Status
            self.lcd_status.set_mode(LcdMode.V_BLANK)

            self.memory.open_oam_access()
            self.memory.open_vram_access()

            return

        should_request_stat_interrupt = False
        current_mode = self.lcd_status.get_mode()

        # If LCD is enabled, we should cycle through different LCD modes depending on what
        # "dot" we are drawing in the current scanline. We have 456 cycles per scanline
        # for scanlines 0-143. This is broken down as follows:
        #   Length 80 Dots - Mode 2 - Sprite (OAM) Scan
        #   Length 168 - 291 dots (depending on sprite count) - Mode 3 - LCD Transfer (use 172 for now)
        #   Length 85 - 208 Dots (depending on previous length) - Mode 0 - HBlank (use 204 for now)
        # If we are operating on a scanline greater than the visible screen (i.e. scanline >= 144)
        # We are in VBlank and should set LCD status to that mode
        if scanline >= 144:
            self.lcd_status.set_mode(LcdMode.V_BLANK)

            self.memory.open_oam_access()
            self.memory.open_vram_access()

            should_request_stat_interrupt = self.lcd_status.is_vblank_stat_interrupt_enabled()

        else:
            if self.scanline_counter >= MAX_CYCLES_PER_FRAME - 80:
                # This is mode 2
                self.lcd_status.set_mode(LcdMode.SPRITE_SEARCH)

                # Restrict OAM access for Mode 2
                self.memory.restrict_oam_access()
                self.memory.open_vram_access()

                should_request_stat_interrupt = self.lcd_status.is_oam_stat_interrupt_enabled()

            elif self.scanline_counter >= MAX_CYCLES_PER_FRAME - 80 - 172:
                # This is mode 3
                self.lcd_status.set_mode(LcdMode.LCD_TRANSFER)

                # Restrict OAM and VRAM access for Mode 3
                self.memory.restrict_oam_access()
                self.memory.restrict_vram_access()

            else:
                # This is mode 0
                self.lcd_status.set_mode(LcdMode.H_BLANK)

                self.memory.open_oam_access()
                self.memory.open_vram_access()

                should_request_stat_interrupt = self.lcd_status.is_hblank_stat_interrupt_enabled()

        # TODO some other interrupts we might need to request here - If mode changed
        # or if Compare scanline is same as current scanline

        # IF we changed mode and should interrupt, do it
        if current_mode != self.lcd_status.get_mode() and should_request_stat_interrupt:
            self.interrupts.request_interrupt(Interrupt.LCD_STAT)

        # If current scanline (LY) is equal to value to compare to (LYC)
        # Then set the coincidence flag (bit 2) of LCD status and request
        # An STAT interrupt
        if scanline == scanline_compare:
            self.lcd_status.update_coincidence_flag(True)
            self.interrupts.request_interrupt(Interrupt.LCD_STAT)
        else:
            self.lcd_status.update_coincidence_flag(False)

    def draw_scanline(self):
        '''
        Draw a specific scanline to the display
        '''

        if self.is_background_enabled():
            self._render_background()

        # TODO sprites

    def get_tiles(self):
        '''
        Get all the tiles in VRAM - This is used for debugging purposes
        '''

        tiles = []
        counter = 0

        start_addr = 0x8000
        addr_space_len = 8192

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
                color = self._get_color_from_id(color_id)
                line.append(color)

            current_tile.append(line)
            if counter == 16:
                counter = 0
                tiles.append(current_tile.copy())
                current_tile = []

        return tiles

    def get_background_tile_pixels(self, y: int) -> "list[int]":
        '''
        Generate a line of pixels in a tile for a line at y position on screen
        '''

        for i in range(0, SCREEN_WIDTH):
            x = self.get_background_scroll_x() + i

            tile_map_addr = self.lcd_control.get_background_tile_map_area()
            x_offset = int(x / 8)
            y_offset = int(y / 8) * 32

            tile_identifier = self.memory.read_byte(tile_map_addr + x_offset + y_offset)
            is_tile_identifier_signed = self.lcd_control.is_background_tile_data_addressing_signed()
            if is_tile_identifier_signed:
                tile_identifier -= 256

            # Recall each tile occupies 16 bytes of memory so ensure we account fo 16 total
            # bytes when finding the right y position.
            yield self._get_tile_line_pixel(tile_identifier, (y % 8) * 2, (7 - x) % 8)

    def is_background_enabled(self) -> bool:
        return self.lcd_control.is_background_enabled()

    def get_background_tile_map(self) -> "list[int]":
        '''
        Get the current background tile map to be able to determine
        which tiles to draw to the screen. Tile map can be at one of two addresses
        depending on LCD Control Bit 3, so get the appropriate address. The map is 32x32
        which is 1024 bytes (0x400)
        '''

        tile_map_len = 0x400
        tile_map_addr = self.lcd_control.get_background_tile_map_area()
        tile_map = []
        for i in range(tile_map_addr, tile_map_addr + tile_map_len):
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

    def _get_tile_line_pixel(self, tile_identifier: int, offset: int, x: int) -> int:
        '''
        Get the pixel of a line in a tile (8 pixels) given the existing tile identifier.
        Offset is used to get the correct pixel based on which bytes we are looking at
        '''

        tile_data_addr = self.lcd_control.get_background_tile_data_area()
        addr = tile_data_addr + (tile_identifier * 16)
        tile_data_low = self.memory.read_byte(addr + offset)
        tile_data_high = self.memory.read_byte(addr + offset + 1)

        # Loop through pixels left to right as that's the order in the tile (bit 7 - 0)
        return self._get_color(tile_data_low, tile_data_high, x)

    def _get_color(self, tile_data_low: int, tile_data_high: int, bit: int) -> int:
        '''
        Get the color ID based on the 2 bytes of the tile being looked at
        The ID will later be mapped onto the palette to get the right color
        '''

        least_significant_bit = get_bit_val(tile_data_low, bit)
        most_significant_bit = get_bit_val(tile_data_high, bit)
        return self._get_color_from_id((most_significant_bit << 1) | least_significant_bit)

    def _get_color_from_id(self, color_id: int):
        '''
        Get the color based on ID and current color pallette
        '''

        pallette = self.memory.read_byte(COLOR_PALLETTE_ADDR)  # this register is where the color pallette is

        # The pallette bits define colors as such (using color ID from 0 - 1)
        # Bit 7-6 - Color for index 3
        # Bit 5-4 - Color for index 2
        # Bit 3-2 - Color for index 1
        # Bit 1-0 - Color for index 0
        # match color_id:
        if color_id == 3:
            color = get_bit_val(pallette, 7) << 1 | get_bit_val(pallette, 6)
        elif color_id == 2:
            color = get_bit_val(pallette, 5) << 1 | get_bit_val(pallette, 4)
        elif color_id == 1:
            color = get_bit_val(pallette, 3) << 1 | get_bit_val(pallette, 2)
        elif color_id == 0:
            color = get_bit_val(pallette, 1) << 1 | get_bit_val(pallette, 0)
        else:
            raise Exception(f"Invalid color_id - {color_id}")

        return GB_COLORS[color]

    def _render_background(self):
        # TODO deal with the Window

        current_scanline = self.get_current_scanline()

        def get_pixels():
            y_pos = (self.get_background_scroll_y() + current_scanline) & 0xFF
            return self.get_background_tile_pixels(y_pos)

        # Get all the pixels needed for a given scanline
        pixels = get_pixels()
        i = 0
        for pixel in pixels:
            if current_scanline < SCREEN_HEIGHT and current_scanline > 0:
                self.screen[i][current_scanline] = pixel
                i += 1
