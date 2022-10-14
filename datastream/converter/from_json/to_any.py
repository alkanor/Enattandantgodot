import json


def deal_with(obj, type_helper, ctxt):
    if hasattr(type_helper, "from_json"): # we may strongly have a SQLAlchemy object to deal with
        return type_helper.from_json(obj)

    if hasattr(type_helper, "__tablename__"): # we may strongly have a SQLAlchemy object to deal with
        return type_helper(**obj)

    if "type" in obj:
        # TODO: complete type system
        # if obj["type"] in known_types:
        #   return known_types["types"]
        if obj["type"].lower() == "Graph":
            from datastream.converter.from_dict.to_graph import dict_to_graph
            return dict_to_graph(obj)
    # TODO: complete
    return obj


def json_to_any(json_object, type_helper=None, ctxt=None):
    dict_from_json = json.loads(json_object)

    if isinstance(dict_from_json, list):
        return [deal_with(obj, type_helper, ctxt) for obj in dict_from_json]

    return deal_with(dict_from_json, type_helper, ctxt)
