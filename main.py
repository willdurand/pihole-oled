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

# Config

# Network interface to retrieve the IP address
interface = os.getenv('PIHOLE_OLED_INTERFACE', 'eth0')
# Mount point for disk usage info
mount_point = os.getenv('PIHOLE_OLED_MOUNT_POINT', '/')
# There is no reset pin on the SSD1306 0.96"
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
sleep = 1 # seconds

hostname = platform.node()

try:
    seconds = 0
    while True:
        draw.rectangle((0, 0, width, height), outline=0, fill=0)

        if seconds == 10:
            seconds = 0

        if seconds >= 5:
            addr = psutil.net_if_addrs()[interface][0]
            draw.text(
                (x, top),
                "Pi-hole %s" % addr.address.rjust(15),
                font=font,
                fill=255
            )

            uptime = datetime.now() - datetime.fromtimestamp(psutil.boot_time())
            draw.text(
                (x, top + 12),
                "Up: %s" % humanize.naturaltime(uptime),
                font=font,
                fill=255
            )

            draw.text(
                (x, top + 22),
                "    %.1f %.1f %.1f" % os.getloadavg(),
                font=font,
                fill=255
            )

            cpu = int(psutil.cpu_percent(percpu=False))
            draw.text((x, top + 34), "CPU", font=font, fill=255)
            draw.rectangle((x + 26, top + 34 , 126, top + 34 + 6), outline=255, fill=0)
            draw.rectangle((x + 26, top + 34, 26 + cpu, top + 34 + 6), outline=255, fill=255)

            mem = int(psutil.virtual_memory().percent)
            draw.text((x, top + 44), "RAM", font=font, fill=255)
            draw.rectangle((x + 26, top + 44 , 126, top + 44 + 6), outline=255, fill=0)
            draw.rectangle((x + 26, top + 44, 26 + cpu, top + 44 + 6), outline=255, fill=255)

            disk = int(psutil.disk_usage(mount_point).percent)
            draw.text((x, top + 54), "Disk", font=font, fill=255)
            draw.rectangle((x + 26, top + 54 , 126, top + 54 + 6), outline=255, fill=0)
            draw.rectangle((x + 26, top + 54, 26 + disk, top + 54 + 6), outline=255, fill=255)
        else:
            try:
                req = requests.get('http://pi.hole/admin/api.php')
                data = req.json()

                draw.text(
                    (x, top),
                    "Pi-hole (%s)" % data["status"],
                    font=font,
                    fill=255
                )

                draw.line((x, top + 12, width, top + 12), fill=255)

                draw.text(
                    (x, top + 22),
                    "Blocked: %d (%d%%)" % (data["ads_blocked_today"], data["ads_percentage_today"]),
                    font=font,
                    fill=255
                )
                draw.text(
                    (x, top + 32),
                    "Queries: %d" % data["dns_queries_today"],
                    font=font,
                    fill=255
                )

                draw.line((x, top + 50, width, top + 50), fill=255)

                draw.text(
                    (x, top + 54),
                    "Blocklist: %d" % data["domains_being_blocked"],
                    font=font,
                    fill=255
                )
            except:
                draw.text(
                    (x, top),
                    "ERROR!",
                    font=font,
                    fill=255
                )

        disp.image(image)
        disp.display()
        time.sleep(sleep)

        seconds += 1
except KeyboardInterrupt:
    print("Exiting...")
