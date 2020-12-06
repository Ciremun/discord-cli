import json
import sys

keys = json.load(open('keys.json'))
config = json.load(open('config.json'))

for key, value in {**keys, **config}.items():
    setattr(sys.modules[__name__], key, value)
