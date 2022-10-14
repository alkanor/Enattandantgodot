import json


# TODO: handle maximum json type -> generator with size estimate
def any_to_json(any_object, ctxt=None):
    if type(any_object) == dict:
        return json.dumps({k: any_to_json(v, ctxt) for k,v in any_object.items()})
    if hasattr(any_object, "__iter__"):
        return json.dumps([any_to_json(obj, ctxt) for obj in any_object])

    if hasattr(any_object, "__tablename__"): # we may strongly have a SQLAlchemy object to deal with
        from persistent.model.interact.answers.answer_statement import AnswerStatement
        if isinstance(any_object, AnswerStatement):
            from datastream.converter.from_sqlalchemy.to_json import answerstatement_to_json
            return answerstatement_to_json(any_object, ctxt)

        from datastream.converter.from_sqlalchemy.to_json import sqlalchemy_to_json
        return sqlalchemy_to_json(any_object, ctxt)

    return json.dumps(any_object)
