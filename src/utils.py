from enum import Enum, IntEnum


class LcdMode(Enum):
    H_BLANK = 0
    V_BLANK = 1
    SPRITE_SEARCH = 2
    LCD_TRANSFER = 3


class Interrupt(IntEnum):
    V_BLANK = 0
    LCD_STAT = 1
    TIMER = 2
    SERIAL = 3
    JOYPAD = 4


def is_bit_set(data: int, position: int) -> bool:
    return (data & (1 << position)) > 0


def set_bit(data: int, position: int) -> int:
    setter = 1 << position
    return data | setter


def reset_bit(data: int, position: int) -> int:
    setter = bit_negate(1 << position)
    return data & setter


def get_bit_val(data: int, position: int) -> int:
    # match data & (1 << position) > 0:
    if data & (1 << position) > 0:
        return 1
    else:
        return 0


def bit_negate(data: int, bits=8) -> int:
    '''
    Perform a bitwise negation for unsigned values
    '''

    return (1 << bits) - 1 - data
