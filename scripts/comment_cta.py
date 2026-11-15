"""Draw an animated three-step comment CTA onto a Pillow RGBA frame."""
from functools import lru_cache
import math

from PIL import ImageDraw, ImageFont


@lru_cache
def _font(path, size):
    return ImageFont.truetype(path, size)


def draw_cta(frame, elapsed, font_path, keyword, *, origin=(806, 140), type_at=1.20):
    """Draw the prompt, typed keyword, and three cycling steps at 1280×720."""
    x, y = origin
    progress = max(0, min(1, elapsed / .28))
    x += round(32 * (1-progress)**3)
    y += round(18 * (1-progress)**3)
    d = ImageDraw.Draw(frame)
    ink = '#11645f'
    white = '#fcffff'
    mint = '#bdf7ed'
    violet = '#eee1fb'

    def box(x1, y1, x2, y2, fill, radius=13, outline=None, width=1):
        d.rounded_rectangle((x1, y1, x2, y2), radius, fill, outline, width)

    def text(tx, ty, value, size, fill=ink, anchor='lm'):
        d.text((tx, ty), value, fill=fill, font=_font(font_path, size), anchor=anchor)

    box(x, y-40, x+400, y-5, '#dffbf5', 12)
    text(x+200, y-23, '想要这个方法？用关键词领取', 19, anchor='mm')
    box(x+4, y+6, x+404, y+319, (28,100,94,48), 22)
    box(x, y, x+400, y+313, white, 22, '#a7ebe0', 2)
    text(x+23, y+29, f'评论区留 {keyword}', 24)
    d.line((x+23, y+49, x+377, y+49), fill='#d4f2ee', width=2)

    start = max(0, elapsed)
    phase = int(start/.48) % 3
    hop = round(6*math.sin(math.pi*(start/.48 % 1)))
    for i, caption in enumerate(('打开评论区', f'输入 {keyword}', '领取方法')):
        yy = y+63+i*41-(hop if phase==i else 0)
        box(x+22, yy, x+378, yy+33, mint if phase==i else '#edf8f6', 10)
        text(x+36, yy+16, f'0{i+1}', 14)
        text(x+82, yy+16, caption, 18)
        if phase==i:
            d.polygon([(x+354,yy+11),(x+361,yy+16),(x+354,yy+21)],fill=ink)

    box(x+22, y+190, x+378, y+239, violet, 12, '#d8c0eb')
    count = 0 if elapsed < type_at else min(len(keyword), 1+int((elapsed-type_at)/.16))
    shown = keyword[:count]
    text(x+39, y+214, shown, 34)
    cursor = x+40+d.textlength(shown,font=_font(font_path,34))
    if int(elapsed*5)%2==0 or 0<count<len(keyword):
        d.line((cursor,y+201,cursor,y+227),fill=ink,width=2)
    button = min(58, 242//max(1,len(keyword)))
    for i, key in enumerate(keyword):
        kx=x+23+i*button
        hit=0<=elapsed-type_at-i*.16<.17
        dy=4 if hit else 0
        box(kx,y+252+dy,kx+button-7,y+289+dy,mint if hit else violet,8)
        text(kx+(button-7)//2,y+270+dy,key,17,anchor='mm')
    ready=elapsed>=type_at+len(keyword)*.16
    box(x+267,y+252,x+377,y+289,mint if ready else '#edf8f6',9)
    text(x+322,y+270,'执行',17,anchor='mm')
