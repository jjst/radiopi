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
from PIL import Image,ImageDraw,ImageFont
import traceback

logging.basicConfig(level=logging.DEBUG)

class Display():

    def __init__(self):
        from waveshare_epd import epd2in13_V2
        epd = epd2in13_V2.EPD()
        self._epd = epd
        logging.info(f"Display dimensions: {epd.width}x{epd.height}")
        epd.init(epd.FULL_UPDATE)
        epd.Clear(0xFF)
        font_path = os.path.join(resources_dir, 'Font.ttc')
        self._font = ImageFont.truetype(font_path, 24)
        self._stream_img = Image.new('1', (epd.height, epd.width), 255)
        self._stream_draw = ImageDraw.Draw(self._stream_img)
        epd.displayPartBaseImage(epd.getbuffer(self._stream_img))
        epd.init(epd.PART_UPDATE)

    def show_stream(self, stream_name):
        x, y = 0, 0
        self._stream_draw.rectangle((x, y, 240, 115), fill = 255)
        self._stream_draw.text((x, y), stream_name, font = self._font, fill = 0)
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
