from debug import get_memory_sequence


# CARTRIDGE_TYPES = {
#     0x00: 'ROM ONLY',
#     0x01: 'MBC1',
#     0x02: 'MBC1+RAM',
#     0x03: 'MBC1+RAM+BATTERY'
# }


class Rom:

    def __init__(self, file):
        self._data = self._load_data(file)

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        self._data = data

    def debug_header(self):
        '''
        Print out and debug the ROM header

        ROM header is located at addr 0x0100 - 0x014F
        '''

        print("\n---------------------------------\n")

        title = ' '.join([chr(c) for c in self.data[0x134:0x143]])

        print(f'Entry Point:\n {get_memory_sequence(self.data[0x100:0x104])}')
        print(f'Nintendo Logo:\n {get_memory_sequence(self.data[0x104:0x134])}')
        print(f'Title:\n {title}')
        print(f'Cartridge Type:\n {format(self.data[0x147], "02X")}')
        print("\n---------------------------------\n")

    def get_cartridge_type(self) -> int:
        return self.data[0x0147]

    def _load_data(self, file: str):
        with open("%s" % file, "rb") as f:
            data = []
            for byte in iter(lambda: f.read(1), b''):
                data.append(byte)

            return [int.from_bytes(d, "big") for d in data]
