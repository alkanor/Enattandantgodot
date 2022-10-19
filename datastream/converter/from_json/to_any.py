from ..from_dict.to_any import dict_to_any
import json


def json_to_any(json_object, type_helper=None, ctxt=None):
    dict_from_json = json.loads(json_object)
    return dict_to_any(dict_from_json)
