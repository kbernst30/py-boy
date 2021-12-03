from ppu import Ppu
import sdl2

from constants import SCREEN_HEIGHT, SCREEN_WIDTH


class SoftwareRenderer(sdl2.ext.SoftwareSpriteRenderSystem):
    def __init__(self, window):
        super(SoftwareRenderer, self).__init__(window)
        sdl2.ext.fill(self.surface, sdl2.ext.Color(255, 255, 255))

    # def render(self, components):
    #     sdl2.ext.fill(self.surface, sdl2.ext.Color(255, 255, 255))
    #     super(SoftwareRenderer, self).render(components)

    def refresh(self):
        '''
        Clear screen back to white
        '''

        sdl2.ext.fill(self.surface, sdl2.ext.Color(255, 255, 255))

    def draw(self, color, area):
        sdl2.ext.fill(self.surface, color, area)


class Pixel(sdl2.ext.Entity):

    def __init__(self, world, sprite, posx=0, posy=0):
        self.sprite = sprite
        self.sprite.position = posx, posy


# class PixelFetcher:

#     def __init__(self, ppu: Ppu):
#         self.ppu = ppu


class MainDisplay:

    DISPLAY_FACTOR = 4

    def __init__(self, ppu: Ppu):
        self.ppu = ppu

        self.window = sdl2.ext.Window(
            "Py Boy",
            size=(
                SCREEN_WIDTH * self.DISPLAY_FACTOR,
                SCREEN_HEIGHT * self.DISPLAY_FACTOR
            )
        )

        self.renderer = SoftwareRenderer(self.window)
        self.world = sdl2.ext.World()

        self.world.add_system(self.renderer)

        self.factory = sdl2.ext.SpriteFactory(sdl2.ext.SOFTWARE)

        self.debug = True

    def show(self):
        self.window.show()

        # processor = sdl2.ext.TestEventProcessor()
        # processor.run(self.window)
        # for x in range(SCREEN_WIDTH):
        #     self.draw(x, 10, 0x000000)

    def render_screen(self):
        self.renderer.refresh()
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
                    # print([0 if x == 0xFFFFFF else 1 for x in line])
                    for j in range(len(line)):
                        color = line[j]
                        self.draw(x + j, y + i, color)

                # print("\n")
                x += 8

        else:
            screen = self.ppu.get_screen()
            for row in range(len(screen)):
                for col in range(len(screen[row])):
                    # color = screen[row][col] if type(screen[row][col]) is int else next(screen[row][col])
                    color = screen[row][col]
                    self.draw(row, col, color)

    def refresh(self):
        self.window.refresh()

    def draw(self, x: int, y: int, color: int):
        red = color >> 16
        blue = (color >> 8) & 0xFF
        green = color & 0xFF

        color = sdl2.ext.Color(red, blue, green)

        x1 = x * self.DISPLAY_FACTOR
        x2 = self.DISPLAY_FACTOR
        y1 = y * self.DISPLAY_FACTOR
        y2 = self.DISPLAY_FACTOR

        self.renderer.draw(color, (x1, y1, x2, y2))
