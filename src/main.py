import sys
import sdl2.ext

from pyboy import PyBoy


def main(rom):
    sdl2.ext.init()

    pyboy = PyBoy()
    pyboy.load_game(rom)
    pyboy.run()

    return 0


if __name__ == '__main__':
    rom = sys.argv[1]

    sys.exit(main(rom))
