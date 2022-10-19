

def deal_with(obj, type_helper, ctxt):
    if hasattr(type_helper, "from_raw"): # we may strongly have a SQLAlchemy object to deal with
        return type_helper.from_raw(obj)

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


def dict_to_any(dict_object, type_helper=None, ctxt=None):
    if isinstance(dict_object, list):
        return [dict_to_any(obj, type_helper, ctxt) for obj in dict_object]
    if isinstance(type_helper, dict) and isinstance(dict_object, dict):
        return {k: dict_to_any(dict_object[k], type_helper.get(k, None), ctxt) for k in dict_object}

    return deal_with(dict_object, type_helper, ctxt)
