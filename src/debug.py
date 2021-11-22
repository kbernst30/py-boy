def get_memory_sequence(mem: list[int]):
    return ' '.join([format(i, '#06x') for i in mem])
