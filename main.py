import os
import platform
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


try:
    disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST)
    is_noop = False
except FileNotFoundError:
    # The error is probably due to this script being run on a system that does
    # not have an OLED connected. In this case, we create fake objects to
    # render the result in the console.
    from image_noop import NoopDisplay, NoopImage, InMemoryImageDraw

    disp = NoopDisplay()
    is_noop = True

disp.begin()

width = disp.width
height = disp.height

# Reduce contrast
disp.command(Adafruit_SSD1306.SSD1306_SETPRECHARGE)
disp.command(5)
disp.set_contrast(5)
disp.command(Adafruit_SSD1306.SSD1306_SETVCOMDETECT)
disp.command(0)

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

sleep = 1  # seconds

hostname = platform.node()

try:
    elapsed_seconds = 0
    while True:
        draw.rectangle((0, 0, width, height), outline=0, fill=0)

        if elapsed_seconds == 10:
            elapsed_seconds = 0

        if elapsed_seconds >= 5:
            addr = psutil.net_if_addrs()[interface][0]
            draw.text(
                (0, 0),
                "Pi-hole %s" % addr.address.rjust(15),
                font=font,
                fill=255
            )

            uptime = datetime.now() - datetime.fromtimestamp(
                psutil.boot_time()
            )
            draw.text(
                (0, 12),
                "Up: %s" % humanize.naturaltime(uptime),
                font=font,
                fill=255
            )

            draw.text(
                (0, 22),
                "    %.1f %.1f %.1f" % os.getloadavg(),
                font=font,
                fill=255
            )

            cpu = int(psutil.cpu_percent(percpu=False))
            draw.text((0, 34), "CPU", font=font, fill=255)
            draw.rectangle(
                (26, 34, 126, 34 + 6),
                outline=255,
                fill=0
            )
            draw.rectangle(
                (26, 34, 26 + cpu, 34 + 6),
                outline=255,
                fill=255
            )

            mem = int(psutil.virtual_memory().percent)
            draw.text((0, 44), "RAM", font=font, fill=255)
            draw.rectangle(
                (26, 44, 126, 44 + 6),
                outline=255,
                fill=0
            )
            draw.rectangle(
                (26, 44, 26 + cpu, 44 + 6),
                outline=255,
                fill=255
            )

            disk = int(psutil.disk_usage(mount_point).percent)
            draw.text((0, 54), "Disk", font=font, fill=255)
            draw.rectangle(
                (26, 54, 126, 54 + 6),
                outline=255,
                fill=0
            )
            draw.rectangle(
                (26, 54, 26 + disk, 54 + 6),
                outline=255,
                fill=255
            )
        else:
            try:
                req = requests.get('http://pi.hole/admin/api.php')
                data = req.json()

                draw.text(
                    (0, 0),
                    "Pi-hole (%s)" % data["status"],
                    font=font,
                    fill=255
                )

                draw.line((0, 12, width, 12), fill=255)

                draw.text(
                    (0, 22),
                    "Blocked: %d (%d%%)" % (
                        data["ads_blocked_today"],
                        data["ads_percentage_today"]
                    ),
                    font=font,
                    fill=255
                )
                draw.text(
                    (0, 32),
                    "Queries: %d" % data["dns_queries_today"],
                    font=font,
                    fill=255
                )

                draw.line((0, 50, width, 50), fill=255)

                draw.text(
                    (0, 54),
                    "Blocklist: %d" % data["domains_being_blocked"],
                    font=font,
                    fill=255
                )
            except:  ## noqa
                draw.text(
                    (0, 0),
                    "ERROR!",
                    font=font,
                    fill=255
                )

        disp.image(image)
        disp.display()
        time.sleep(sleep)

        elapsed_seconds += 1
except (KeyboardInterrupt, SystemExit):
    print("Exiting...")
