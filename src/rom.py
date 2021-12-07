from debug import get_memory_sequence


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
        print(f'Number of Banks:\n {self.get_number_of_banks()}')
        print("\n---------------------------------\n")

    def get_cartridge_type(self) -> int:
        return self.data[0x0147]

    def get_number_of_banks(self) -> int:
        '''
        Get the number of banks in the ROM, denoted at addr 0x0148
        These mappings were taken from PanDocs
        '''

        ref = self.data[0x0148]
        if ref == 0x00:
            return 2
        elif ref == 0x01:
            return 4
        elif ref == 0x02:
            return 8
        elif ref == 0x03:
            return 16
        elif ref == 0x04:
            return 32
        elif ref == 0x05:
            return 64
        elif ref == 0x06:
            return 128
        elif ref == 0x07:
            return 256
        elif ref == 0x08:
            return 512
        elif ref == 0x52:
            return 72
        elif ref == 0x53:
            return 80
        elif ref == 0x54:
            return 96

        # We shouldn't get here but if we do, just assume no extra banks
        return 2

    def _load_data(self, file: str):
        with open("%s" % file, "rb") as f:
            data = []
            for byte in iter(lambda: f.read(1), b''):
                data.append(byte)

            return [int.from_bytes(d, "big") for d in data]
