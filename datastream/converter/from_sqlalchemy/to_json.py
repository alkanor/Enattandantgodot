from .to_dict import sqlalchemy_to_dict
import json


def sqlalchemy_to_json(sqlalch_obj, ctxt=None):
    return json.dumps(sqlalchemy_to_dict(sqlalch_obj, ctxt))


def answerstatement_to_json(sqlalch_obj, ctxt=None):
    return json.dumps(sqlalchemy_to_dict(sqlalch_obj, ctxt))



if __name__ == "__main__":
    from persistent.datastructure.union import UNION

    from persistent_to_disk import create_session
    from persistent.base_type import BasicEntity, _Integer, _String, STRING_SIZE

    from sqlalchemy import String, Column, Integer

    columns = {
        "id": Column(Integer, primary_key=True),
        "lol": Column(String(STRING_SIZE), unique=True),
        "xD": Column(Integer, default=1337),
    }

    Test = BasicEntity("XXD", columns)

    session = create_session()

    UNION_TYPE = UNION(Test, _Integer, _String)

    print(sqlalchemy_to_json(UNION_TYPE))

    i3 = _Integer.GET_CREATE(session, id=999)
    u = UNION_TYPE.GET_CREATE(session, i3)

    session.commit()

    print(sqlalchemy_to_json(u))
