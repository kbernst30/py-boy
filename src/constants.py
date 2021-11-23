import math

# Cycles per frame is determined by the clock frequency of the CPU (4.194304 MHz)
# And the number of expected frames per second (~60) - to make this accurage it should be 59.73
MAX_CYCLES_PER_FRAME = math.floor(4194304 / 59.73)

PROGRAM_COUNTER_INIT = 0x100
STACK_POINTER_INIT = 0xFFFE
