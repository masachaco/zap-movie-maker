from textwrap import fill
from turtle import fillcolor
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import base64
import hashlib
from .util import *

def create_fuchidori_telop_image(text,font_path,font_size,fill_color="white",stroke_fill_color="black",background_color="white",stroke_width=5,back_ground_stroke_width=8):
    param = f"{text}-{font_path}-{font_size}-{fill_color}-{stroke_fill_color}-{background_color}-{stroke_width}-{back_ground_stroke_width}"
    hash = hashlib.md5(param.encode('utf-8')).hexdigest()
    output_path = get_path(f"./resource/telop/{hash}.png")
    if os.path.exists(output_path):
        return output_path

    im = Image.new('RGBA', (1200, 100))
    id = ImageDraw.Draw(im)
    font = ImageFont.truetype(font_path,int(font_size))
    id.multiline_text((7, 10), text,font=font, fill=background_color, stroke_width=back_ground_stroke_width)
    id.multiline_text((7, 10), text, font=font, fill=fill_color, stroke_width=stroke_width, stroke_fill=stroke_fill_color)

    im.save(output_path)
    return output_path