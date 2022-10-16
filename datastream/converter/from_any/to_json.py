from .to_dict import any_to_dict

import json


def any_to_json(any_object, ctxt=None):
    return json.dumps(any_to_dict(any_object, ctxt))
