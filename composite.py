import sys

from wand.image import Image
from wand.drawing import Drawing
from wand.color import Color


def _coord_add(*args):
    return tuple(map(sum, zip(*args)))


def _draw_sprite(draw, fn, x, y, r):
    with Image(filename=fn) as layer:
        layer.rotate(r)
        draw.composite('over', x, y, layer.width, layer.height, layer)


def create_composite_sprite(sprites, out_fn, pix_height):
    with Drawing() as draw:
        draw.gravity = 'center'

        width = height = 128
        basis_y = 0
        if pix_height > 256:
            width = height = 512
            basis_y = 128 + 64
        elif pix_height > 128:
            width = height = 256
            basis_y = 64

        last_parent = None
        for i, sp in enumerate(sprites):
            ageStart, ageEnd = sp['ageRange']
            if not ageStart < 20 and (ageEnd > 20 or ageEnd == -1):
                next

            x, y = sp['pos']
            offset_x, offset_y = sp['offset']
            x -= offset_x
            y = -y - offset_y + basis_y
            r = (sp['rot'] * 360) % 360
            _draw_sprite(draw, sp['sprite'], x, y, r)

        with Image(width=width, height=height, background=Color('transparent')) as img:
            draw.draw(img)
            img.save(filename=out_fn)
