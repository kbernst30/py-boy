import pygame
import pygame.locals

from constants import SCREEN_HEIGHT, SCREEN_WIDTH
from ppu import Ppu


class MainDisplay:

    DISPLAY_FACTOR = 4

    def __init__(self, ppu: Ppu):
        self.ppu = ppu

        size = SCREEN_WIDTH * self.DISPLAY_FACTOR, SCREEN_HEIGHT * self.DISPLAY_FACTOR

        self.window = pygame.display.set_mode(size, pygame.locals.DOUBLEBUF)
        self.window.set_alpha(None)
        pygame.display.flip()

        self.canvas = pygame.display.get_surface()
        self.canvas.fill((255, 255, 255))

        self.debug = False

    def render_screen(self):
        self.canvas.fill((255, 255, 255))

        if self.debug:
            tiles = self.ppu.get_tiles()

            x = 0
            y = 0

            for tile in tiles:

                if x > SCREEN_WIDTH:
                    x = 0
                    y += 8

                for i in range(len(tile)):
                    line = tile[i]
                    for j in range(len(line)):
                        color = line[j]
                        self.draw_rect(x + j, y + i, color)

                x += 8

        else:
            screen = self.ppu.get_screen()
            for row in range(len(screen)):
                for col in range(len(screen[row])):
                    color = screen[row][col]
                    if color != 0xFFFFFF:
                        self.draw_rect(row, col, color)

        pygame.display.flip()

    def refresh(self):
        self.window.refresh()

    def draw_rect(self, x: int, y: int, color: int):
        red = color >> 16
        blue = (color >> 8) & 0xFF
        green = color & 0xFF

        pygame.draw.rect(self.canvas, (red, blue, green), (
            x * self.DISPLAY_FACTOR,
            y * self.DISPLAY_FACTOR,
            self.DISPLAY_FACTOR,
            self.DISPLAY_FACTOR,
        ))
