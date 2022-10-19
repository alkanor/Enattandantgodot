from persistent.datastructure.alias import ALIAS
from persistent.base_type.string import String


AnswerEnumAlias = ALIAS(String, "AnswerEnum")


def craft_answer_for_session(method):
    cached = {}
    answer_string = method.__name__
    def when_called(CLS, session):
        if answer_string in cached:
            return cached[answer_string]
        target = String.GET_CREATE(session, answer_string)
        alias = CLS(session, target)
        existing = session.query(CLS).filter_by(alias_id=alias.alias_id).one_or_none()
        if not existing:
            session.add(alias)
            session.commit()
            existing = alias
        cached[answer_string] = existing
        return existing
    return when_called


class AnswerStatement(AnswerEnumAlias):
    __statement__ = True
    __baseattrs__ = AnswerEnumAlias.__dict__

    @classmethod
    def from_raw(cls, data):
        assert isinstance(data, str), "Simple answer statement expects a string to be unserialized"
        assert data in cls.__dict__, f"Simple answer statement expects a string in the {cls.__name__} keys, not {data}"
        return getattr(cls, data)
