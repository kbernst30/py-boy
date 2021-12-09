import sys
import pyglet

from pyglet import shapes

from constants import DISPLAY_FACTOR, SCREEN_HEIGHT, SCREEN_WIDTH

from pyboy import PyBoy


pyboy = PyBoy()
main_window = pyglet.window.Window(SCREEN_WIDTH * DISPLAY_FACTOR, SCREEN_HEIGHT * DISPLAY_FACTOR, "PyBoy")
# vram_viewer = pyglet.window.Window(512, 512, "VRAM")

main_window.set_location(100, 100)
# vram_viewer.set_location(main_window.get_location()[0] + main_window.width + 10, main_window.get_location()[1] + 20)

pyglet.gl.glClearColor(255, 255, 255, 0)

fps_display = pyglet.window.FPSDisplay(window=main_window)

pixels = []
# tile_pixels = {}

batch = pyglet.graphics.Batch()
# tile_batch = pyglet.graphics.Batch()

# Setup Screen - TODO move to function
for i in range(SCREEN_WIDTH):
    line = []
    for j in range(SCREEN_HEIGHT - 1, -1, -1):
        line.append(
            shapes.Rectangle(
                x=i * DISPLAY_FACTOR,
                y=j * DISPLAY_FACTOR,
                width=DISPLAY_FACTOR,
                height=DISPLAY_FACTOR,
                color=(i, i, i),
                batch=batch
            )
        )

    pixels.append(line)


# Setup VRAM Viewer - TODO move to function
# x = 0
# y = 0

# for tile in pyboy.get_tiles():

#     if x >= 512:
#         x = 0
#         y += 8 * 2

#     for i in range(len(tile)):
#         line = tile[i]
#         for j in range(len(line)):
#             tile_pixels[(x + i), (y + j)] = shapes.Rectangle(
#                 x=x + (j * 2),
#                 y=512 - y - (i * 2),
#                 width=2,
#                 height=2,
#                 color=(255, 0, 0),
#                 batch=tile_batch
#             )

#     x += 8 * 2


def run_frame(dt):
    pyboy.run()

    screen = pyboy.get_screen()

    for row in range(len(screen)):
        for col in range(len(screen[row])):
            color = screen[row][col]
            red = color >> 16
            green = (color >> 8) & 0xFF
            blue = color & 0xFF

            current_color = pixels[row][col].color

            if current_color[0] != red or current_color[1] != green or current_color[2] != blue:
                pixels[row][col].color = (red, green, blue)

    # x = 0
    # y = 0
    # for tile in pyboy.get_tiles():

    #     if x >= 512:
    #         x = 0
    #         y += 16

    #     for i in range(len(tile)):
    #         line = tile[i]
    #         for j in range(len(line)):
    #             color = line[j]
    #             red = color >> 16
    #             green = (color >> 8) & 0xFF
    #             blue = color & 0xFF

    #             current_color = tile_pixels[(x + i), (y + j)].color

    #             if current_color[0] != red or current_color[1] != green or current_color[2] != blue:
    #                 tile_pixels[(x + i), (y + j)].color = (red, green, blue)

    #     x += 16


@main_window.event("on_draw")
def on_main_draw():
    main_window.clear()
    batch.draw()
    fps_display.draw()


# @vram_viewer.event("on_draw")
# def on_vram_draw():
#     vram_viewer.clear()
#     tile_batch.draw()


pyglet.clock.schedule_interval(run_frame, 1 / 59.7275)


def main(rom):
    pyboy.load_game(rom)

    pyglet.app.run()

    return 0


if __name__ == '__main__':
    rom = sys.argv[1]

    sys.exit(main(rom))
