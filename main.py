import json
import os
import platform
import subprocess
import time

import Adafruit_SSD1306
import humanize
import psutil
import requests

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from datetime import datetime

# 128x64 display with hardware I2C
RST = None

class NoopImage:

    draw = None

    def print(self):
        self.draw.print()

class InMemoryImageDraw:

    content = []

    def __init__(self, image):
        image.draw = self

    def text(self, xy, text, font=None, fill=None):
        self.content.append(text)

    def rectangle(self, *args, **kwargs):
        os.system("clear")

    def print(self):
        print("\n".join(self.content))
        self.content = []

class NoopDisplay:

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

try:
    disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST)
    is_noop = False
except FileNotFoundError:
    disp = NoopDisplay()
    is_noop = True

disp.begin()

width = disp.width
height = disp.height

disp.clear()
disp.display()

if is_noop:
    image = NoopImage()
    draw = InMemoryImageDraw(image)
    font = None
else:
    image = Image.new('1', (width, height))
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype('./SF_Pixelate.ttf', 10)

top = 0
x = 0

hostname = platform.node()

try:
    while True:
        draw.rectangle((0, 0, width, height), outline=0, fill=0)

        with requests.get('http://pi.hole/admin/api.php') as request:
            data = request.json()

            draw.text(
                (x, top),
                "Pi-hole (%s)" % data["status"],
                font=font,
                fill=255
            )
            draw.text(
                (x, top + 14),
                "Blocked: %d (%d%%)" % (data["ads_blocked_today"], data["ads_percentage_today"]),
                font=font,
                fill=255
            )
            draw.text(
                (x, top + 24),
                "Queries: %d" % data["dns_queries_today"],
                font=font,
                fill=255
            )

            av1, av2, av3 = os.getloadavg()
            draw.text(
                (x, top + 44),
                "Load: %.1f %.1f %.1f" % os.getloadavg(),
                font=font,
                fill=255
            )
            uptime = datetime.now() - datetime.fromtimestamp(psutil.boot_time())
            draw.text(
                (x, top + 54),
                "Up: %s" % humanize.naturaltime(uptime),
                font=font,
                fill=255
            )

        disp.image(image)
        disp.display()
        time.sleep(1)
except KeyboardInterrupt:
    print("Exiting...")
