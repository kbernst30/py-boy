import sys

import logging

import pygame

from constants import MAX_CYCLES_PER_FRAME

from cpu import Cpu
from display import MainDisplay
from interrupts import InterruptControl
from mmu import Mmu
from ppu import Ppu
from rom import Rom


logger = logging.getLogger(__name__)


class PyBoy:

    DISPLAY_SCALE = 5
    TIMER = pygame.USEREVENT + 1

    def __init__(self):
        self.mmu = Mmu()
        self.cpu = Cpu(self.mmu)
        self.ppu = Ppu(self.mmu)
        self.interrupts = InterruptControl(self.mmu, self.cpu)

        self.main_display = MainDisplay(self.ppu)

        self.rom = None

        pygame.init()

    def load_game(self, file):
        self.rom = Rom(file)
        self.mmu.load_rom(self.rom)

        self.cpu.reset()

    def run(self):
        # Main emu loop
        pygame.time.set_timer(self.TIMER, 17)  # ~60 Hz

        if not self.rom:
            print("No ROM loaded")
            return

        self.rom.debug_header()

        running = True
        while running:
            frame_cycles = 0

            try:
                # Execute a frame based on number of cycles we expect per frame
                while frame_cycles < MAX_CYCLES_PER_FRAME:
                    cycles = self.cpu.execute()
                    frame_cycles += cycles

                    self.ppu.update_graphics(cycles)
                    self.interrupts.service_interrupts()

                # After execution of a frame, update the screen
                self.main_display.render_screen()

            except Exception as e:
                logger.exception(e)
                self.exit(1)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit()

    def exit(self, exit_code=0):
        pygame.display.quit()
        pygame.quit()
        sys.exit(exit_code)
