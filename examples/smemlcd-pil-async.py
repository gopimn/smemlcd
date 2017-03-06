#
# smemlcd - Sharp Memory LCDs library
#
# Copyright (C) 2014 by Artur Wroblewski <wrobell@pld-linux.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import argparse
import asyncio
import time

from smemlcd import SMemLCD
import PIL.Image, PIL.ImageDraw, PIL.ImageFont

parser = argparse.ArgumentParser(description='smemlcd library asyncio example')
parser.add_argument(
    '-p', dest='policy', choices=('default', 'uv'), nargs=1,
    help='TrueType font filename'
)
parser.add_argument('-f', dest='font', nargs=1, help='TrueType font filename')
parser.add_argument('device', help='SPI device filename, i.e. /dev/spi')
args = parser.parse_args()

WIDTH, HEIGHT = 400, 240

def center(draw, y, txt, font):
    w, h = draw.textsize(txt, font=font)
    x = int((WIDTH - w) / 2)
    draw.text((x, y), txt, fill='white', font=font)

if args.policy == 'uv':
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

img = PIL.Image.new('1', (WIDTH, HEIGHT))
draw = PIL.ImageDraw.Draw(img)
if args.font:
    font = PIL.ImageFont.truetype(args.font[0], size=30)
else:
    font = PIL.ImageFont.load_default()

async def run(lcd):
    for i in range(60, -1, -1):
        img.paste(0)

        center(draw, 60, 'smemlcd library demo', font)

        s = 'closing in {:02d}...'.format(i)
        center(draw, 100, s, font)

        draw.arc(((180, 180), (220, 220)), 0, 360, fill='white')
        draw.pieslice(((180, 180), (220, 220)), -90, (60 - i) * 6 - 90, outline='white')

        t1 = time.time()
        await lcd.write_async(img.tobytes())
        print('lcd writing time', round(time.time() - t1, 4))

        await asyncio.sleep(1)


loop = asyncio.get_event_loop()

lcd = SMemLCD(args.device, loop=loop)
try:
    loop.run_until_complete(run(lcd))
finally:
    loop.close()
    lcd.close()

# vim: sw=4:et:ai