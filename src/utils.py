def is_bit_set(data: int, position: int) -> bool:
    return (data & (1 << position)) > 0


def set_bit(data: int, position: int) -> int:
    setter = 1 << position
    return data | setter


def reset_bit(data: int, position: int) -> int:
    setter = ~(1 << position)
    return data & setter


def get_bit_val(data: int, position: int) -> int:
    match data & (1 << position) > 0:
        case True: return 1
        case False: return 0
