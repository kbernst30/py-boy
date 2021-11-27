import sdl2


class MainDisplay:

    def __init__(self):
        self.window = sdl2.ext.Window("Hello World!", size=(640, 480))

    def show(self):
        self.window.show()

        processor = sdl2.ext.TestEventProcessor()
        processor.run(self.window)
