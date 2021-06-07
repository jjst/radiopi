#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib')
resources_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'resources')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
import time
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import requests

logging.basicConfig(level=logging.INFO)

class Display():

    def __init__(self):
        from waveshare_epd import epd2in13_V2
        epd = epd2in13_V2.EPD()
        self._epd = epd
        logging.info(f"Display dimensions: {epd.width}x{epd.height}")
        epd.init(epd.FULL_UPDATE)
        epd.Clear(0xFF)
        font_path = os.path.join(resources_dir, 'Font.ttc')
        self._font = ImageFont.truetype(font_path, 28)
        self._stream_img = Image.new('1', (epd.height, epd.width), 255)
        self._stream_draw = ImageDraw.Draw(self._stream_img)
        epd.displayPartBaseImage(epd.getbuffer(self._stream_img))
        epd.init(epd.PART_UPDATE)

    def show_stream(self, stream):
        epd = self._epd
        draw = self._stream_draw
        logging.info(f"Updating display to show stream: {stream.name}")

        # Show station favicon
        r = requests.get(stream.favicon, allow_redirects=True)
        image1 = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame
        favicon_image = Image.open(BytesIO(r.content))
        resized_favicon = favicon_image.resize((32, 32))
        image1.paste(resized_favicon, (2, 2))
        epd.display(epd.getbuffer(image1))

        # Show text with station name
        x, y = 0, 0
        W, H = (epd.height, 30)
        w, h = draw.textsize(stream.name, font=self._font)
        draw.rectangle((x, y, W, H), fill=255)
        draw.text(((W-w)/2, (H-h)/2), stream.name, font=self._font, fill=0)
        epd.display(epd.getbuffer(self._stream_img))

    def turn_off(self):
        x, y = 0, 0
        epd = self._epd
        self._stream_draw.rectangle((x, y, 240, 115), fill=255)
        epd.displayPartial(epd.getbuffer(self._stream_img))



if __name__ == "__main__":
    try:

        epd = epd2in13_V2.EPD()
        time_image = Image.new('1', (epd.height, epd.width), 255)
        time_draw = ImageDraw.Draw(time_image)

        epd.displayPartBaseImage(epd.getbuffer(time_image))

        epd.init(epd.PART_UPDATE)
        num = 0
        while (True):
            x, y = 180, 95
            time_draw.rectangle((x, y, 240, 115), fill = 255)
            time_draw.text((x, y), time.strftime('%H:%M'), font = font24, fill = 0)
            epd.displayPartial(epd.getbuffer(time_image))
            num = num + 1
            if(num == 10):
                break
        # epd.Clear(0xFF)
        logging.info("Clear...")
        epd.init(epd.FULL_UPDATE)
        epd.Clear(0xFF)

        logging.info("Goto Sleep...")
        epd.sleep()

    except IOError as e:
        logging.info(e)

    except KeyboardInterrupt:
        logging.info("ctrl + c:")
        epd2in13_V2.epdconfig.module_exit()
        exit()
