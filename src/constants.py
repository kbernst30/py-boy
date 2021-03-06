import math

SCREEN_WIDTH = 160
SCREEN_HEIGHT = 144
DISPLAY_FACTOR = 4

# Cycles per frame is determined by the clock frequency of the CPU (4.194304 MHz)
# And the number of expected frames per second (~60) - to make this accurage it should be 59.7275
CLOCK_SPEED = 4194304
MAX_CYCLES_PER_FRAME = math.floor(CLOCK_SPEED / 59.7275)

PROGRAM_COUNTER_INIT = 0x100
STACK_POINTER_INIT = 0xFFFE

# Timers
DIVIDER_REGISTER_ADDR = 0xFF04
TIMER_ADDR = 0xFF05
TIMER_MODULATOR_ADDR = 0xFF06  # The value at this address is what the timer is set to upon overflow
TIMER_CONTROL_ADDR = 0xFF07
CYCLES_PER_DIVIDER_INCREMENT = 256

# LCD and Graphics
LCD_CONTROL_ADDR = 0xFF40  # The address of the LCD control byte
LCD_STATUS_ADDR = 0xFF41  # The address of the LCD status byte

# LY - Current Scanline being processed is written to this address
# This can hold values 0 - 153, but 144-153 indicate VBlank period,
# as there are only 144 vertical scanlines
CURRENT_SCANLINE_ADDR = 0xFF44

# LYC - Current scanline compare value
CURRENT_SCANLINE_COMPARE_ADDR = 0xFF45

MAX_SCANLINE_VALUE = 153

CYCLES_PER_SCANLINE = 456  # It takes 456 clock cycles to draw one scanline

# SCX and SCY registers - Those specify the top-left coordinates
# of the visible 160×144 pixel area within the 256×256 pixels BG map.
# Values in the range 0–255 may be used.
BACKGROUND_SCROLL_Y = 0xFF42
BACKGROUND_SCROLL_X = 0xFF43

# WY and WX registers - these specify the top-left coordinates
# of the window, which can be displayed over the background
# WX is offset by +7 pixels, so a value of 7 places the window
# at x = 0
WINDOW_POS_Y = 0xFF4A
WINDOW_POS_X = 0xFF4B

COLOR_PALLETTE_ADDR = 0xFF47

# Banking
ROM_BANKING_MODE_ADDR = 0x147
RAM_BANK_COUNT_ADDR = 0x148
MAXIMUM_RAM_BANKS = 4
RAM_BANK_SIZE = 0x2000  # In bytes

GB_COLORS = {
    0: 0xFFFFFF,
    1: 0xCCCCCC,
    2: 0x777777,
    3: 0x000000
}

# Interrupts
# Known as IE (Interrupt Enable) register, which denotes which interrupts are currently enabled
# Bit 0 = VBlank Interrupt - INT $40
# Bit 1 = LCD Stat Interrupt - INT $48
# Bit 2 = Timer Interrupt - INT $50
# Bit 3 = Serial Interrupt - INT $58
# Bit 4 = Joypad Interrupt - INT $60
INTERRUPT_ENABLE_ADDR = 0xFFFF

# Known as IF (Interrupt Flag) register, which denotes which interrupts are currently requested
# Bit 0 = VBlank Interrupt - INT $40
# Bit 1 = LCD Stat Interrupt - INT $48
# Bit 2 = Timer Interrupt - INT $50
# Bit 3 = Serial Interrupt - INT $58
# Bit 4 = Joypad Interrupt - INT $60
INTERRUPT_FLAG_ADDR = 0xFF0F

# Joypad register - Bits are as follows:
# Bit 7 - Not used
# Bit 6 - Not used
# Bit 5 - P15 Select Action buttons    (0=Select)
# Bit 4 - P14 Select Direction buttons (0=Select)
# Bit 3 - P13 Input: Down  or Start    (0=Pressed) (Read Only)
# Bit 2 - P12 Input: Up    or Select   (0=Pressed) (Read Only)
# Bit 1 - P11 Input: Left  or B        (0=Pressed) (Read Only)
# Bit 0 - P10 Input: Right or A        (0=Pressed) (Read Only)
JOYPAD_REGISTER_ADDR = 0xFF00
