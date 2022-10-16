from persistent.datastructure.alias import ALIAS
from persistent.base_type.string import String


AnswerStatement = ALIAS(String, "AnswerEnum")


def craft_answer_for_session(answer_string):
    cached = {}
    def sub(session):
        if answer_string in cached:
            return cached[answer_string]
        target = String.GET_CREATE(session, answer_string)
        alias = AnswerStatement(session, target)
        existing = session.query(AnswerStatement).filter_by(alias_id=alias.alias_id).one_or_none()
        if not existing:
            session.add(alias)
            session.commit()
            existing = alias
        cached[answer_string] = existing
        return existing
    return sub


class Statement:
    __statement__ = True
