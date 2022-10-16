

# TODO: handle maximum size -> generator with size estimate
def any_to_dict(any_object, ctxt=None):
    if hasattr(any_object, "__tablename__"): # we may strongly have a SQLAlchemy object to deal with
        from persistent.model.interact.answers.answer_statement import AnswerStatement
        if isinstance(any_object, AnswerStatement):
            from datastream.converter.from_sqlalchemy.to_dict import answerstatement_to_dict
            return answerstatement_to_dict(any_object, ctxt)

        from datastream.converter.from_sqlalchemy.to_dict import sqlalchemy_to_dict
        return sqlalchemy_to_dict(any_object, ctxt)

    if hasattr(any_object, "__statement__"):
        from enum import EnumMeta
        from persistent.model.interact.answers.answer_statement import Statement
        if isinstance(any_object, Statement) or isinstance(any_object, EnumMeta):
            from datastream.converter.from_sqlalchemy.to_dict import answerstatement_to_dict
            return answerstatement_to_dict(any_object, ctxt)

    if type(any_object) == dict:
        return {k: any_to_dict(v, ctxt) for k,v in any_object.items()}
    if hasattr(any_object, "__iter__"):
        return [any_to_dict(obj, ctxt) for obj in any_object]

    return {k: v for k,v in any_object.__dict__.items()}
