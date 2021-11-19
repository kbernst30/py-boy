import sys

import pygame
import pygame.locals

from cpu import Cpu
from mmu import Mmu


class PyBoy:

    DISPLAY_SCALE = 5
    TIMER = pygame.USEREVENT + 1

    def __init__(self):

        # Setup pygame
        pygame.init()

        self.font = pygame.font.SysFont("monospace", 20)
        self.window = self._init_canvas()

        self.mmu = Mmu()
        self.cpu = Cpu(self.mmu)

    def run(self):
        # Main emu loop
        pygame.time.set_timer(self.TIMER, 17)  # ~60 Hz

        while True:
            self.cpu.execute()

            # Update screen
            # self._update_screen()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                elif event.type == self.TIMER:
                    pass
                    # self.mmu.update_delay_timer()
                    # self.mmu.update_sound_timer()

    def _init_canvas(self):
        width = 144 * self.DISPLAY_SCALE
        height = 160 * self.DISPLAY_SCALE

        # if self.debug:
        #     height += 500

        size = width, height
        window = pygame.display.set_mode(size, pygame.locals.DOUBLEBUF)
        window.set_alpha(None)
        pygame.display.flip()

        self.canvas = pygame.display.get_surface()
        self.canvas.fill((0, 0, 0))

        return window
