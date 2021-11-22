import sys

from pyboy import PyBoy


def main(rom):
    pyboy = PyBoy()
    pyboy.load_game(rom)
    pyboy.run()


if __name__ == '__main__':
    rom = sys.argv[1]
    main(rom)
