# -*- coding: utf-8 -*-

import json
import itertools
import os
import re
import sys
import subprocess

from composite import create_composite_sprite

spinner = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])


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


OBJECT_PROPS = {
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

SPRITE_PROPS = {
    'ageRange': parse_coords,
    'hFlip': parse_bool,
    'parent': int,
    'pos': parse_coords,
    'rot': float
}

TRANSITION_PROPS = [
    ('newActor', int),
    ('newTarget', int),
    ('autoDecaySecs', int),
    ('actorMinUseFraction', float),
    ('targetMinUseFraction', float),
    ('reverseUseActor', int),
    ('reverseUseTargetFlag', int),
    ('move', int),
    ('desiredMoveDist', int)
]


def update(out):
    sys.stderr.write("Parsing object files ⠏")

    # Objects
    objects = {}
    objects_path = data_path('objects')
    for fn in os.listdir(objects_path):
        sys.stderr.write('\b' + spinner.next())

        if fn != 'nextObjectNumber.txt':
            oid, obj = load_object(os.path.join(objects_path, fn))
            objects[oid] = obj

    sys.stderr.write("\b\b\nLoading transitions ⠏")

    # Transitions
    transitions = []
    transitions_path = data_path('transitions')
    for fn in os.listdir(transitions_path):
        sys.stderr.write('\b' + spinner.next())
        if re.match("-?[\d]*_-?[\d]*[_A-Z]*.txt", fn):
            transitions.append(load_transition(
                os.path.join(transitions_path, fn)))

    sys.stderr.write("\b\b\nGenerating sprites ⠏")

    # Sprites
    for obj in objects.itervalues():
        sys.stderr.write('\b' + spinner.next())

        # Create a composite sprite.
        if not obj['person']:
            out_fn = os.path.join('sprites', '{}.png'.format(obj['id']))
            create_composite_sprite(obj['sprites'], out_fn, obj['pixHeight'])
            obj['sprite'] = out_fn
            del obj['sprites']

    json.dump({'objects': objects, 'transitions': transitions}, out)
    sys.stderr.write("\b\b\nDone!\n")


def load_object(fn):
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

        sprite_converter = SPRITE_PROPS.get(name)
        if sprite_converter:
            current_sprite[name] = sprite_converter(value)
            next

        converter = OBJECT_PROPS.get(name)
        if converter:
            cleaned_value = re.split(r"[#,]", value, maxsplit=2)[0]
            obj[name] = converter(cleaned_value)

    obj['sprites'].append(current_sprite)
    for i, sp in enumerate(obj['sprites']):
        # Load the offset from the info file.
        name, offset_x, offset_y = load_sprite_info(
            data_path('sprites', sp['id']))
        sp['name'] = name
        sp['offset'] = (offset_x, offset_y)

    # If the object is a category, add its members.
    if obj['name'].startswith('@ '):
        obj['name'] = obj['name'][2:]
        obj['category'] = True
        obj['category_members'] = load_category(
            data_path('categories', oid))

    return oid, obj


def load_category(fn):
    with open(fn) as f:
        return map(int, f.read().splitlines()[2:])


def load_sprite_info(fn):
    with open(fn) as f:
        raw = f.read().split()
        return raw[0], float(raw[2]), float(raw[3])


def load_transition(fn):
    with open(fn) as f:
        line = f.read().splitlines()[0]

    transition = {name: converter(val)
                  for (name, converter), val
                  in zip(TRANSITION_PROPS, line.split(" "))}

    fn_data = os.path.basename(fn)[:-4].split("_")
    transition['actor'] = int(fn_data[0])
    transition['target'] = int(fn_data[1])

    return transition


if __name__ == '__main__':
    with open('ohol_new.json', 'w') as out:
        update(out)

    os.rename('ohol_new.json', 'ohol.json')
