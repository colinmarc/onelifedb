import sys

from wand.image import Image
from wand.drawing import Drawing
from wand.color import Color


def create_composite_sprite(sprites, out_fn):
    with Drawing() as draw:
        draw.gravity = 'center'
        basis_x, basis_y = 0, 0

        for sp in sprites:
            # I'm really confused about the coordinate system, but this seems to work.
            x, y = sp['pos']
            if basis_x == 0 and basis_y == 0:
                basis_x = x
                basis_y = y
            else:
                basis_x += x / 2
                basis_y += y / 2

            with Image(filename=sp['fn']) as layer:
                draw.composite('over', basis_x, basis_y,
                               layer.width, layer.height, layer)

        with Image(width=128,
                   height=128,
                   background=Color('transparent')) as img:
            draw.draw(img)
            img.save(filename=out_fn)
