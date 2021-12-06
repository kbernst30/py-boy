def get_memory_sequence(mem: "list[int]") -> str:
    return ' '.join([format(i, '#06x') for i in mem])
