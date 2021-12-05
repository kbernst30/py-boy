import sys

import logging

import sdl2

# import pygame
# import pygame.locals

from constants import MAX_CYCLES_PER_FRAME

from cpu import Cpu
from display import MainDisplay
from mmu import Mmu
from ppu import Ppu
from rom import Rom


logger = logging.getLogger(__name__)


class PyBoy:

    DISPLAY_SCALE = 5

    def __init__(self):
        self.mmu = Mmu()
        self.cpu = Cpu(self.mmu)
        self.ppu = Ppu(self.mmu)

        self.main_display = MainDisplay(self.ppu)

        self.rom = None

    def load_game(self, file):
        self.rom = Rom(file)
        self.mmu.load_rom(self.rom)

        self.cpu.reset()

    def run(self):
        # Main emu loop
        # pygame.time.set_timer(self.TIMER, 17)  # ~60 Hz

        if not self.rom:
            print("No ROM loaded")
            return

        self.rom.debug_header()

        # self.main_display.show()

        running = True
        while running:
            frame_cycles = 0

            try:
                # Execute a frame based on number of cycles we expect per frame
                while frame_cycles < MAX_CYCLES_PER_FRAME:
                    cycles = self.cpu.execute()
                    frame_cycles += cycles

                    self.ppu.update_graphics(cycles)
                    # self.ppu.debug_vram(self.main_display)

                # After execution of a frame, update the screen
                # self.main_display.render_screen()

            except Exception as e:
                logger.exception(e)
                sys.exit(1)

            for event in sdl2.ext.get_events():
                # if event.type == SDL_WINDOWEVENT and event.window.event == SDL_WINDOWEVENT_CLOSE:
                #     sys.exit()

                if event.type == sdl2.SDL_QUIT:
                    running = False
                    break

            # self.main_display.refresh()

        #     # Update screen
        #     # self._update_screen()

            # for event in pygame.event.get():
            #     if event.type == pygame.QUIT:
            #         sys.exit()
        #         elif event.type == self.TIMER:
        #             pass
        #             # self.mmu.update_delay_timer()
        #             # self.mmu.update_sound_timer()

    # def _init_canvas(self):
    #     width = 144 * self.DISPLAY_SCALE
    #     height = 160 * self.DISPLAY_SCALE

        # if self.debug:
        #     height += 500

        # size = width, height
        # window = pygame.display.set_mode(size, pygame.locals.DOUBLEBUF)
        # window.set_alpha(None)
        # pygame.display.flip()

        # self.canvas = pygame.display.get_surface()
        # self.canvas.fill((0, 0, 0))

        # return window
