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

    def draw(self, color, area):
        sdl2.ext.fill(self.surface, color, area)


class Pixel(sdl2.ext.Entity):

    def __init__(self, world, sprite, posx=0, posy=0):
        self.sprite = sprite
        self.sprite.position = posx, posy


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
        # self.draw(10, 10, 0x000000)

    def render_screen(self):
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
                    # print([1 if x > 0 else 0 for x in line])
                    for j in range(len(line)):
                        color = line[j]
                        self.draw(x + j, y + i, color)

                # print("\n")
                x += 8

    def refresh(self):
        self.window.refresh()

    def draw(self, x: int, y: int, color: int):
        red = color >> 16
        blue = (color >> 8) & 0xFF
        green = color & 0xFF

        color = sdl2.ext.Color(red, blue, green)

        x1 = x * self.DISPLAY_FACTOR
        x2 = x1 + self.DISPLAY_FACTOR
        y1 = self.DISPLAY_FACTOR
        y2 = self.DISPLAY_FACTOR

        self.renderer.draw(color, (x1, x2, y1, y2))
