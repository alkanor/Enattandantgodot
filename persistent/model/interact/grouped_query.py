from persistent.datastructure.list import LIST
from .query import QUERY


def GROUPED_QUERY(QuestionedObjectType, QuestionType):
    return LIST(QUERY(QuestionedObjectType, QuestionType))


if __name__ == "__main__":
    from persistent_to_disk import create_session
    from persistent.base_type import _Integer, STRING_SIZE, BasicEntity

    from sqlalchemy.exc import IntegrityError
    from sqlalchemy import String, Integer, Column

    columns = {
        "id": Column(Integer, primary_key=True),
        "question": Column(String(STRING_SIZE), unique=True),
    }

    Question = BasicEntity("basicquestion", columns)

    columns = {
        "id": Column(Integer, primary_key=True),
        "graphid": Column(Integer, unique=True),
    }

    QuestionedObject = BasicEntity("basicquestionedgraph", columns)

    session = create_session()

    v1 = Question.GET_CREATE(session, question="Is acyclic?")
    v2 = Question.GET_CREATE(session, question="Is tree?")
    v3 = Question.GET_CREATE(session, question="Is directed?")
    v4 = Question.GET_CREATE(session, question="Has root?")

    i1 = QuestionedObject.GET_CREATE(session, graphid=1)
    i2 = QuestionedObject.GET_CREATE(session, graphid=10)
    i3 = QuestionedObject.GET_CREATE(session, graphid=100)

    QUERY_TYPE = QUERY(QuestionedObject, Question)
    QUERY_TYPE2 = QUERY(QuestionedObject, Question)

    GROUPED_TYPE = GROUPED_QUERY(QuestionedObject, Question)
    GROUPED_TYPE2 = GROUPED_QUERY(QuestionedObject, Question)

    print(GROUPED_TYPE)
    print(GROUPED_TYPE2)
    GROUPED_TYPE2.addr = object().__repr__
    print(GROUPED_TYPE2.addr())
    print(GROUPED_TYPE.addr())

    mylist1 = GROUPED_TYPE(session, name="grouped1")
    mylist2 = GROUPED_TYPE(session, name="grouped2")

    mylist1.add(session, QUERY_TYPE.GET_CREATE(session, question=v1, questioned_object=i1))
    mylist1.add(session, QUERY_TYPE.GET_CREATE(session, question=v1, questioned_object=i1))
    mylist2.add(session, QUERY_TYPE.GET_CREATE(session, question=v2, questioned_object=i2))
    mylist2.add(session, QUERY_TYPE.GET_CREATE(session, question=v2, questioned_object=i3))
