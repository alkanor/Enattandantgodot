from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, declared_attr

from persistent.datastructure.metadated import MetadatedType
from persistent.base import BaseAndMetaChangeClassName
from persistent.type_system import register_type


__objectname__ = "PROCESSING"


#@register_args({"QueryType": Query, "StatusType": Status, "StateType": State}) # TODO: global type system registration for graph representation
@register_type(__objectname__, lambda QueryType, StatusType, StateType = None:
                                      (QueryType.__tablename__, StatusType.__tablename__, StateType.__tablename__ if StateType else None))
def PROCESSING(QueryType, StatusType, StateType = None):

    if StateType:
        processing_tablename = f'{__objectname__}<{QueryType.__tablename__},{StatusType.__tablename__},{StateType.__tablename__}>'
        ChangeClassNameBase, _ = BaseAndMetaChangeClassName(QueryType, StatusType, StateType)
    else:
        processing_tablename = f'{__objectname__}<{QueryType.__tablename__},{StatusType.__tablename__}>'
        ChangeClassNameBase, _ = BaseAndMetaChangeClassName(QueryType, StatusType)

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
                return relationship(StateType, foreign_keys=[cls.state_id])

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

    STATUS = BasicEntity("status", columns)

    columns = {
        "id": Column(Integer, primary_key=True),
        "state": Column(String(STRING_SIZE), unique=True),
    }

    STATE = BasicEntity("state", columns)


    session = create_session()

    v1 = Question.GET_CREATE(session, question="Is acyclic?")
    v2 = Question.GET_CREATE(session, question="Is tree?")
    v3 = Question.GET_CREATE(session, question="Is directed?")
    v4 = Question.GET_CREATE(session, question="Has root?")

    i1 = QuestionedObject.GET_CREATE(session, graphid=1)
    i2 = QuestionedObject.GET_CREATE(session, graphid=10)
    i3 = QuestionedObject.GET_CREATE(session, graphid=100)

    start = STATUS.GET_CREATE(session, status="starting")
    progress = STATUS.GET_CREATE(session, status="in progress")
    ended = STATUS.GET_CREATE(session, status="finished")

    s1 = STATE.GET_CREATE(session, state="state1")
    s2 = STATE.GET_CREATE(session, state="state2")
    s3 = STATE.GET_CREATE(session, state="state3")

    QUERY_TYPE = QUERY(QuestionedObject, Question)

    q1 = QUERY_TYPE.GET_CREATE(session, question=v1, questioned_object=i1)
    q2 = QUERY_TYPE.GET_CREATE(session, question=v2, questioned_object=i1)
    q3 = QUERY_TYPE.GET_CREATE(session, question=v1, questioned_object=i3)

    PROCESSING_TYPE1 = PROCESSING(QUERY_TYPE, STATUS, STATE)
    PROCESSING_TYPE2 = PROCESSING(QUERY_TYPE, STATUS)

    a1 = PROCESSING_TYPE1.GET_CREATE(session, query=q1, status=start, state=s1)
    a2 = PROCESSING_TYPE1.GET_CREATE(session, query=q2, status=ended)
    a3 = PROCESSING_TYPE2.GET_CREATE(session, query=q3, status=progress)

    print(a1)
    print(a2)
    print(a3)

    print(a1.query)
    print(a1.status)
    print(a1.state)
    print(a1.question)
    print(a1.questioned_object)

    print(a3.query)
    print(a3.status)
    try:
        print(a3.state)
    except AttributeError:
        print("Normal lack of state attribute due to type construction for PROCESSING_TYPE2")