import math

SCREEN_WIDTH = 160
SCREEN_HEIGHT = 144

# Cycles per frame is determined by the clock frequency of the CPU (4.194304 MHz)
# And the number of expected frames per second (~60) - to make this accurage it should be 59.73
MAX_CYCLES_PER_FRAME = math.floor(4194304 / 59.73)

PROGRAM_COUNTER_INIT = 0x100
STACK_POINTER_INIT = 0xFFFE

# Timers
DIVIDER_REGISTER_ADDR = 0xFF04
TIMER_ADDR = 0xFF05
TIMER_MODULATOR_ADDR = 0xFF06  # The value at this address is what the timer is set to upon overflow

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
