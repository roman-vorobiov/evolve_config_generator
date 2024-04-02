import json


def load_config(path):
    with open(path, 'r') as f:
        return json.load(f)


def save_config(config, path, pretty=False):
    with open(path, 'w') as f:
        if pretty:
            json.dump(config, f, indent='  ')
        else:
            json.dump(config, f)


def dump_config(config, pretty=False):
    if pretty:
        return json.dumps(config, indent='  ')
    else:
        return json.dumps(config)
