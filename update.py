import json
import os
import re
import sys
import subprocess


def parse_bool(s):
    return s == '1'


CLOTHING_POSITIONS = {
    'b': 'bottom',
    't': 'top',
    's': 'shoe',
    'h': 'hat'
}


def parse_clothing(s):
    return CLOTHING_POSITIONS.get(s)


KNOWN_OBJECT_PROPS = {
    'clothing': parse_clothing,
    'floor': parse_bool,
    'foodValue': int,
    'heatValue': int,
    'numUses': int,
    'numSlots': int,
    'permanent': parse_bool,
    'rValue': float,
    'spriteID': int
}


def update(out):
    base_path = 'OneLifeData7'
    objects_path = os.path.join(base_path, 'objects')
    sprites_path = os.path.join(base_path, 'sprites')
    categories_path = os.path.join(base_path, 'categories')
    transitions_path = os.path.join(base_path, 'categories')

    sys.stderr.write('Parsing object files...')

    # Objects
    objects = {}
    for fn in os.listdir(objects_path):
        if fn != 'nextObjectNumber.txt':
            oid, obj = parse_object_file(os.path.join(objects_path, fn))
            objects[oid] = obj

    sprites = {}
    for obj in objects.itervalues():
        # Sprite
        sid = obj['spriteID']
        if sid not in sprites:
            png_fn = os.path.join('sprites', '{}.png'.format(sid))
            tga_fn = os.path.join(sprites_path, '{}.tga'.format(sid))
            subprocess.check_call(['convert', tga_fn, png_fn])
            sprites[sid] = png_fn

        obj['sprite'] = sprites[sid]

        # Category
        if obj['name'].startswith('@ '):
            fn = os.path.join(categories_path, '{}.txt'.format(obj['id']))
            obj['name'] = obj['name'][2:]
            obj['category'] = True
            obj['category_members'] = parse_category_file(fn)

    interactions = {}

    print json.dumps({'objects': objects})


def parse_object_file(fn):
    with open(fn) as f:
        raw = f.read()

    # props = re.split(r"[\s#]", raw)
    lines = raw.splitlines()
    oid = int(lines.pop(0).split('=')[1])
    name = lines.pop(0)

    obj = {'id': oid, 'name': name}
    for line in lines:
        name, value = line.split('=', 1)
        converter = KNOWN_OBJECT_PROPS.get(name)
        if converter and name not in obj:
            cleaned_value = re.split(r"[#,]", value, 2)[0]
            obj[name] = converter(cleaned_value)

    return oid, obj


def parse_category_file(fn):
    with open(fn) as f:
        return map(int, f.read().splitlines()[2:])


if __name__ == '__main__':
    with open('ohol_new.json', 'w') as out:
        update(out)

    os.rename('ohol_new.json', 'ohol.json')
