

def sqlalchemy_to_dict(sqlalch_obj, ctxt=None):
    columns = sqlalch_obj.__table__.columns.values()
    relationships = sqlalch_obj.__mapper__.relationships.values()
    if isinstance(sqlalch_obj, type):  # we have the base SQLAlchemy type, returns the description
        cols_dict = [{"name": c.name, "type": repr(type(c.type)), "fk": [f.target_fullname for f in c.foreign_keys]} if c.foreign_keys else \
                     {"name": c.name, "type": repr(type(c.type))} for c in columns]
        rels_dict = [{"name": r.key, "tablename": r.target.name} for r in relationships]
        return {"columns": cols_dict, "relations": rels_dict, "type": sqlalch_obj.__tablename__}
    else:                          # we have the instanced object, returns it serialized
        max_depth = 0              # nesting depth: 0 = no nested object, 1 = 1 nested object at most, ..., -1 = infinite nesting (no circular dependancy check atm)
        if ctxt is not None and "depth" in ctxt:
            max_depth = ctxt["depth"]
            next_dict = {k:v for k,v in ctxt.items()}
            next_dict["depth"] = max_depth - 1

        to_dict = {c.name: getattr(sqlalch_obj, c.name) for c in columns}
        to_dict.update({"type": sqlalch_obj.__tablename__})
        if not max_depth:
            return to_dict
        for r in relationships:
            attr = getattr(sqlalch_obj, r.key)
            if attr:
                to_dict[r.key] = sqlalchemy_to_dict(attr, next_dict)
        return to_dict


def answerstatement_to_dict(sqlalch_obj, ctxt=None):
    from enum import Enum
    if isinstance(sqlalch_obj, Enum): # we have the base Enum type, returns the description
        out_dict = {"choices": [entry.name for entry in sqlalch_obj]}
        out_dict.update({"type": sqlalch_obj.__classname__})
        if ctxt and isinstance(ctxt, dict):
            if "exclusive" in ctxt:
                out_dict.update({"exclusive": True})
            if "max_choices" in ctxt:
                out_dict.update({"max_choices": ctxt["max_choices"]})
            if "min_choices" in ctxt:
                out_dict.update({"min_choices": ctxt["min_choices"]})
        return out_dict
    return sqlalch_obj.name           # else returns the enum value name
