

# TODO: handle maximum size -> generator with size estimate
def any_to_dict(any_object, ctxt=None):
    if isinstance(any_object, int) or isinstance(any_object, str):
        return any_object

    from datastructure.base.graph import Graph
    if isinstance(any_object, Graph):
        from datastream.converter.from_graph.to_dict import graph_to_dict
        return graph_to_dict(any_object)

    if hasattr(any_object, "__statement__"):
        from persistent.model.interact.answers.answer_statement import AnswerEnumAlias
        if isinstance(any_object, AnswerEnumAlias) or isinstance(any_object, type):
            from datastream.converter.from_sqlalchemy.to_dict import answerstatement_to_dict
            return answerstatement_to_dict(any_object, ctxt)

    if hasattr(any_object, "__tablename__"): # we may strongly have a SQLAlchemy object to deal with
        from persistent.model.interact.answers.answer_statement import AnswerEnumAlias
        if isinstance(any_object, AnswerEnumAlias):
            from datastream.converter.from_sqlalchemy.to_dict import answerstatement_to_dict
            return answerstatement_to_dict(any_object, ctxt)

        from datastream.converter.from_sqlalchemy.to_dict import sqlalchemy_to_dict
        return sqlalchemy_to_dict(any_object, ctxt)

    if type(any_object) == dict:
        return {k: any_to_dict(v, ctxt) for k,v in any_object.items()}
    if hasattr(any_object, "__iter__"):
        return [any_to_dict(obj, ctxt) for obj in any_object]

    return {k: v for k,v in any_object.__dict__.items()}
