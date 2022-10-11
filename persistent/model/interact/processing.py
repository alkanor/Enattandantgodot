from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, declared_attr

from persistent.datastructure.metadated import MetadatedType
from persistent.base import BaseAndMetaChangeClassName
from persistent.type_system import register_type


__objectname__ = "PROCESSING"


#@register_args({"QueryType": Query, "StatusType": Status, "StateType": State}) # TODO: global type system registration for graph representation
@register_type(__objectname__, lambda QueryType, StatusType, StateType: (QueryType.__tablename__, StatusType.__tablename__, StateType.__tablename__))
def PROCESSING(QueryType, StatusType, StateType = None):

    if StateType:
        processing_tablename = f'{__objectname__}<{QueryType.__tablename__},{StatusType.__tablename__},{StateType.__tablename__}>'
    else:
        processing_tablename = f'{__objectname__}<{QueryType.__tablename__},{StatusType.__tablename__}>'

    ChangeClassNameBase, _ = BaseAndMetaChangeClassName(QueryType, StatusType, StateType)

    class PROCESSING_OBJECT(ChangeClassNameBase):
        __tablename__ = processing_tablename
        __questionobjecttype__ = QueryType.__questionobjecttype__
        __questiontype__ = QueryType.__questiontype__
        __statustype__ = StatusType

        id = Column(Integer, primary_key=True)
        query_id = Column(Integer, ForeignKey(QueryType.id), nullable=False)
        status_id = Column(Integer, ForeignKey(StatusType.id), nullable=False)

        if StateType:
            __statetype__ = StateType
            state_id = Column(Integer, ForeignKey(StateType.id))
            __table_args__ = (UniqueConstraint("query_id", "status_id", "state_id", name="unique_processing"), )
        else:
            __table_args__ = (UniqueConstraint("query_id", "status_id", name="unique_processing"),)

        @declared_attr
        def query(cls):
            return relationship(QueryType, foreign_keys=[cls.query_id])

        @declared_attr
        def status(cls):
            return relationship(StatusType, foreign_keys=[cls.status_id])

        if StateType:
            @declared_attr
            def state(cls):
                return relationship(StateType, foreign_keys=[cls.state])

        @property
        def questioned_object(self):
            return self.query.questioned_object

        @property
        def question(self):
            return self.query.question

        def __repr__(self):
            return f'(P{self.id}) {self.query} [{self.status}]{" "+repr(self.state) if StateType else ""}'


    _PROCESSING = BasicEntity(PROCESSING_OBJECT.__tablename__, ["id", "query_id", "status_id", "query", "status"]+(["state_id", "state"] if StateType else []),
                              PROCESSING_OBJECT, __objectname__)

    return _PROCESSING


def MetadatedProcessing(QueryType, StatusType, StateType, *args):
    PROCESSING_TYPE = PROCESSING(QueryType, StatusType, StateType)
    return MetadatedType(PROCESSING_TYPE, *args)



if __name__ == "__main__":
    from persistent_to_disk import create_session
    from persistent.base_type import BasicEntity, STRING_SIZE

    from sqlalchemy.exc import IntegrityError
    from sqlalchemy import String, Integer

    from .query import QUERY


    columns = {
        "id": Column(Integer, primary_key=True),
        "question": Column(String(STRING_SIZE), unique=True),
    }

    Question = BasicEntity("basicQ", columns)

    columns = {
        "id": Column(Integer, primary_key=True),
        "graphid": Column(Integer, unique=True),
    }

    QuestionedObject = BasicEntity("basicG", columns)

    columns = {
        "id": Column(Integer, primary_key=True),
        "status": Column(String(STRING_SIZE), unique=True),
    }

    Status = BasicEntity("status", columns)

    columns = {
        "id": Column(Integer, primary_key=True),
        "state": Column(String(STRING_SIZE), unique=True),
    }

    State = BasicEntity("state", columns)


    session = create_session()

    v1 = Question.GET_CREATE(session, question="Is acyclic?")
    v2 = Question.GET_CREATE(session, question="Is tree?")
    v3 = Question.GET_CREATE(session, question="Is directed?")
    v4 = Question.GET_CREATE(session, question="Has root?")

    i1 = QuestionedObject.GET_CREATE(session, graphid=1)
    i2 = QuestionedObject.GET_CREATE(session, graphid=10)
    i3 = QuestionedObject.GET_CREATE(session, graphid=100)

    start = Status.GET_CREATE(session, status="starting")
    progress = Status.GET_CREATE(session, status="in progress")
    ended = Status.GET_CREATE(session, status="finished")


    QUERY_TYPE = QUERY(QuestionedObject, Question)

    q1 = QUERY_TYPE.GET_CREATE(session, question=v1, questioned_object=i1)
    q2 = QUERY_TYPE.GET_CREATE(session, question=v2, questioned_object=i1)
    q3 = QUERY_TYPE.GET_CREATE(session, question=v1, questioned_object=i3)

    print(q1.id)
    print(yes.id)

    ANSWER_TYPE = ANSWER(QUERY_TYPE, Answer)

    a1 = ANSWER_TYPE.GET_CREATE(session, query=q1, answer=yes)
    a2 = ANSWER_TYPE.GET_CREATE(session, query=q2, answer=yes)
    a3 = ANSWER_TYPE.GET_CREATE(session, query=q3, answer=no)

    print(a1)
    print(a2)
    print(a3)

    print(a1.query)
    print(a1.answer)
    print(a1.question)
    print(a1.questioned_object)

    a1.question = v4
    try:
        session.commit()
    except IntegrityError:
        print("Normal integrity error when resetting the question (question + questioned object already in a query)")
