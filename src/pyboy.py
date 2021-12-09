import sys

import logging

from constants import MAX_CYCLES_PER_FRAME

from cpu import Cpu
from interrupts import InterruptControl
from mmu import Mmu
from ppu import Ppu
from rom import Rom
from timers import TimerControl


logger = logging.getLogger(__name__)


class PyBoy:

    def __init__(self):
        self.mmu = Mmu()
        self.interrupts = InterruptControl(self.mmu)
        self.timers = TimerControl(self.mmu, self.interrupts)
        self.ppu = Ppu(self.mmu, self.interrupts)
        self.cpu = Cpu(self.mmu, self.timers, self.ppu)

        self.rom = None

    def load_game(self, file):
        self.rom = Rom(file)
        self.mmu.load_rom(self.rom)

        self.cpu.reset()

        self.rom.debug_header()

    def run(self):
        if not self.rom:
            print("No ROM loaded")
            return

        frame_cycles = 0

        try:
            # Execute a frame based on number of cycles we expect per frame
            while frame_cycles < MAX_CYCLES_PER_FRAME:
                cycles = self.cpu.execute()
                frame_cycles += cycles

                interrupt = self.interrupts.get_servicable_interrupt()
                if interrupt is not None:
                    self.cpu.service_interrupt(interrupt)

        except Exception as e:
            logger.exception(e)
            self.exit(1)

    def get_screen(self):
        return self.ppu.get_screen()

    def get_tiles(self):
        return self.ppu.get_tiles()

    def exit(self, exit_code=0):
        sys.exit(exit_code)
