from ..from_type.to_string import type_to_string


def sqlalchemy_to_dict(sqlalch_obj, ctxt=None):
    columns = sqlalch_obj.__table__.columns.values()
    relationships = sqlalch_obj.__mapper__.relationships.values()
    if isinstance(sqlalch_obj, type):  # we have the base SQLAlchemy type, returns the description
        cols_dict = [{"name": c.name, "type": repr(type(c.type)), "fk": [f.target_fullname for f in c.foreign_keys]} if c.foreign_keys else \
                     {"name": c.name, "type": repr(type(c.type))} for c in columns]
        rels_dict = [{"name": r.key, "tablename": r.target.name} for r in relationships]
        res = {"columns": cols_dict, "relations": rels_dict, "tablename": sqlalch_obj.__tablename__}
        if not ctxt or (not "notype" in ctxt) or not ctxt["notype"]:
            res.update({"type": type_to_string(sqlalch_obj.__mapper__.class_)})
        return res
    else:                          # we have the instanced object, returns it serialized
        max_depth = 0              # nesting depth: 0 = no nested object, 1 = 1 nested object at most, ..., -1 = infinite nesting (no circular dependancy check atm)
        if ctxt is not None and "depth" in ctxt:
            max_depth = ctxt["depth"]
            next_dict = {k:v for k,v in ctxt.items()}
            next_dict["depth"] = max_depth - 1

        to_dict = {c.name: getattr(sqlalch_obj, c.name) for c in columns}
        if not ctxt or (not "notype" in ctxt) or not ctxt["notype"]:
            to_dict.update({"tablename": sqlalch_obj.__tablename__})
            to_dict.update({"type": type_to_string(sqlalch_obj.__mapper__.class_)})

        if not max_depth:
            return to_dict
        for r in relationships:
            attr = getattr(sqlalch_obj, r.key)
            if attr:
                to_dict[r.key] = sqlalchemy_to_dict(attr, next_dict)
        return to_dict


def answerstatement_to_dict(sqlalch_obj, ctxt=None):
    if isinstance(sqlalch_obj, type): # we have the base type, returns the description
        if hasattr(sqlalch_obj, "__baseattrs__"):
            out_dict = {"choices": [entry for entry in sqlalch_obj.__dict__ if entry not in sqlalch_obj.__baseattrs__ and entry[0] != '_']}
        else:
            out_dict = {"choices": [entry for entry in sqlalch_obj.__dict__ if entry[0] != '_']}
        if not ctxt or (not "notype" in ctxt) or not ctxt["notype"]:
            out_dict.update({"type": type_to_string(sqlalch_obj)})
        if ctxt and isinstance(ctxt, dict):
            if "exclusive" in ctxt:
                out_dict.update({"exclusive": True})
            if "max_choices" in ctxt:
                out_dict.update({"max_choices": ctxt["max_choices"]})
            if "min_choices" in ctxt:
                out_dict.update({"min_choices": ctxt["min_choices"]})
        return out_dict
    return sqlalch_obj.orm_obj.id      # else returns the enum value name
