import os


class NoopImage:
    """NoopImage is a fake image for printing contnet on `stdout`."""

    draw = None

    def print(self):
        self.draw.print()


class InMemoryImageDraw:
    """InMemoryImageDraw is a fake implementation of an instance returned by
    ImageDraw.Draw() (Pillow). It is used for printing content on `stdout`."""

    content = []

    def __init__(self, image):
        image.draw = self

    def text(self, xy, text, font=None, fill=None):
        self.content.append(text)

    def rectangle(self, *args, **kwargs):
        self.content = []

    def line(self, *args, **kwargs):
        self.content.append('-' * 20)

    def print(self):
        os.system("clear")
        print("\n".join(self.content))
        self.content = []


class NoopDisplay:
    """NoopDisplay is a fake display for printing contnet on `stdout`."""

    width = 0
    height = 0

    def begin(self):
        pass

    def clear(self):
        pass

    def image(self, image):
        image.print()

    def display(self):
        pass

    def set_contrast(self, contrast):
        pass

    def command(self, command):
        pass
