import json
import os
import re
import sys
import subprocess

from composite import create_composite_sprite


def data_path(data_type, oid=None, ext='txt'):
    if oid:
        return os.path.join('OneLifeData7', data_type, '{}.{}'.format(str(oid), ext))
    else:
        return os.path.join('OneLifeData7', data_type)


def parse_bool(s):
    return s == '1'


def parse_coords(s):
    return map(float, s.split(',', 2))


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
    'person': parse_bool,
    'pixHeight': int,
    'rValue': float,
    'spriteID': int
}

KNOWN_SPRITE_PROPS = {
    'ageRange': parse_coords,
    'hFlip': parse_bool,
    'parent': int,
    'pos': parse_coords,
    'rot': float
}


def update(out):
    sys.stderr.write("Parsing object files...\n")

    # Objects
    objects = {}
    objects_path = data_path('objects')
    for fn in os.listdir(data_path('objects')):
        if fn != 'nextObjectNumber.txt':
            oid, obj = parse_object_file(os.path.join(objects_path, fn))
            objects[oid] = obj

    sys.stderr.write("Generating sprites...\n")

    for obj in objects.itervalues():
        # Category
        if obj['name'].startswith('@ '):
            obj['name'] = obj['name'][2:]
            obj['category'] = True
            obj['category_members'] = parse_category_file(
                data_path('categories', obj['id']))

            # No need for a sprite
            next

        if obj['person']:
            next

        # Create a composite Sprite
        out_fn = os.path.join('sprites', '{}.png'.format(obj['id']))
        create_composite_sprite(obj['sprites'], out_fn, obj['pixHeight'])
        obj['sprite'] = out_fn
        del obj['sprites']

    interactions = {}

    print(json.dumps({'objects': objects}))


def parse_object_file(fn):
    with open(fn) as f:
        raw = f.read()

    lines = raw.splitlines()
    oid = int(lines.pop(0).split('=')[1])
    name = lines.pop(0)

    obj = {'id': oid, 'name': name, 'sprites': []}
    current_sprite = None
    for line in lines:
        name, value = line.split('=', 1)

        if name == 'spriteID':
            if current_sprite is not None:
                obj['sprites'].append(current_sprite)

            sid = int(value)
            current_sprite = {
                'id': sid,
                'sprite': data_path('sprites', sid, 'tga')
            }
            next

        sprite_converter = KNOWN_SPRITE_PROPS.get(name)
        if sprite_converter:
            current_sprite[name] = sprite_converter(value)
            next

        converter = KNOWN_OBJECT_PROPS.get(name)
        if converter:
            cleaned_value = re.split(r"[#,]", value, maxsplit=2)[0]
            obj[name] = converter(cleaned_value)

    obj['sprites'].append(current_sprite)
    for i, sp in enumerate(obj['sprites']):
        # Load the offset from the info file.
        name, offset_x, offset_y = parse_sprite_info_file(
            data_path('sprites', sp['id']))
        sp['name'] = name
        sp['offset'] = (offset_x, offset_y)

        # This makes following the tree later easier.
        sp['index'] = i

    return oid, obj


def parse_category_file(fn):
    with open(fn) as f:
        return map(int, f.read().splitlines()[2:])


def parse_sprite_info_file(fn):
    with open(fn) as f:
        raw = f.read().split()
        return raw[0], float(raw[2]), float(raw[3])


if __name__ == '__main__':
    with open('ohol_new.json', 'w') as out:
        update(out)

    os.rename('ohol_new.json', 'ohol.json')
