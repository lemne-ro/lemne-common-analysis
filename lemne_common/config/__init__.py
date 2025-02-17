import os
import json
from dotenv import dotenv_values


class DotDict(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


def get():
    config = {
        **dotenv_values('.env'),
        **os.environ,
    }

    config = DotDict(config)

    for key in config:
        try:
            config[key] = json.loads(config[key])
        except json.decoder.JSONDecodeError:
            pass

    return config

