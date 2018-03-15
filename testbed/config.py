from confetti import Config
import json
import os

_existing_config = os.environ.get('TESTBED_CONFIG_PATH')
if _existing_config is not None:
    with open(existing_config) as f:
        cfg = Config(json.load(f))
else:
    cfg = Config({
        'backslash_url': None,
    })

root = cfg.root

def serialize():
    return cfg.serialize_to_dict()
