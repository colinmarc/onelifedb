import json
import os
import re
import sys
import subprocess

from composite import create_composite_sprite


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
    'rValue': float,
    'spriteID': int
}

KNOWN_SPRITE_PROPS = {
    'pos': parse_coords,
    'rot': float,
    'hFlip': parse_bool
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
    base_path = 'OneLifeData7'
    objects_path = os.path.join(base_path, 'objects')
    sprites_path = os.path.join(base_path, 'sprites')
    categories_path = os.path.join(base_path, 'categories')
    transitions_path = os.path.join(base_path, 'transitions')

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
        for sp in obj['sprites']:
            sp['fn'] = tga_fn = os.path.join(
                sprites_path, '{}.tga'.format(sp['id']))

        out_fn = os.path.join('sprites', '{}.png'.format(obj['id']))
        create_composite_sprite(obj['sprites'], out_fn)
        obj['sprite'] = out_fn
        # del obj['sprites']

        # Category
        if obj['name'].startswith('@ '):
            fn = os.path.join(categories_path, '{}.txt'.format(obj['id']))
            obj['name'] = obj['name'][2:]
            obj['category'] = True
            obj['category_members'] = parse_category_file(fn)

    interactions = {}
    
    trans_files = os.listdir(transitions_path)
    transitions = [parse_transition_file(os.path.join(transitions_path,fn))
                   for fn in trans_files
                   if re.match("-?[\d]*_-?[\d]*[_A-Z]*.txt", fn)]

    print(json.dumps({
        'objects': objects,
        'transitions': transitions
    }))


def parse_object_file(fn):
    with open(fn) as f:
        raw = f.read()

    # props = re.split(r"[\s#]", raw)
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

            current_sprite = {'id': int(value)}

        sprite_converter = KNOWN_SPRITE_PROPS.get(name)
        if sprite_converter:
            current_sprite[name] = sprite_converter(value)
            next

        converter = KNOWN_OBJECT_PROPS.get(name)
        if converter:
            cleaned_value = re.split(r"[#,]", value, maxsplit=2)[0]
            obj[name] = converter(cleaned_value)

    obj['sprites'].append(current_sprite)
    return oid, obj


def parse_category_file(fn):
    with open(fn) as f:
        return map(int, f.read().splitlines()[2:])

def parse_transition_file(fn):
    with  open(fn) as f:
        line = f.read().splitlines()[0]
        
    fn_data = os.path.basename(fn)[:-4].split("_")
    transition = {
        "actor": int(fn_data[0]),
        "target": int(fn_data[1])
    }

    props_raw = line.split(" ")
    for idx, val in enumerate(props_raw):
        name, converter = TRANSITION_PROPS[idx]
        transition[name] = converter(val)
    return transition

if __name__ == '__main__':
    with open('ohol_new.json', 'w') as out:
        update(out)

    os.rename('ohol_new.json', 'ohol.json')
