from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, declared_attr

from persistent.datastructure.metadated import MetadatedType
from persistent.base import BaseAndMetaChangeClassName
from persistent.type_system import register_type
from persistent.base_type import BasicEntity


__objectname__ = "QUERY"


@register_type(__objectname__, lambda QuestionedObjectType, QuestionType: (QuestionedObjectType.__tablename__, QuestionType.__tablename__))
def QUERY(QuestionedObjectType, QuestionType):

    query_tablename = f'{__objectname__}<{QuestionedObjectType.__tablename__},{QuestionType.__tablename__}>'

    ChangeClassNameBase, _ = BaseAndMetaChangeClassName(QuestionedObjectType, QuestionType)

    class QUERY_OBJECT(ChangeClassNameBase):
        __tablename__ = query_tablename
        __questionobjecttype__ = QuestionedObjectType
        __questiontype__ = QuestionType

        id = Column(Integer, primary_key=True)
        questionedobject_id = Column(Integer, ForeignKey(QuestionedObjectType.id), nullable=False)
        question_id = Column(Integer, ForeignKey(QuestionType.id), nullable=False)

        __table_args__ = (UniqueConstraint("questionedobject_id", "question_id", name="unique_query"), )

        @declared_attr
        def questioned_object(cls):
            return relationship(QuestionedObjectType, foreign_keys=[cls.questionedobject_id])

        @declared_attr
        def question(cls):
            return relationship(QuestionType, foreign_keys=[cls.question_id])

        def __repr__(self):
            return f'(Q{self.id}) {self.question} applied to {self.questioned_object}'


    _QUERY = BasicEntity(QUERY_OBJECT.__tablename__, ["id", "questionedobject_id", "question_id", "questioned_object", "question"], QUERY_OBJECT, __objectname__)

    return _QUERY


def MetadatedQuery(QuestionedObjectType, QuestionType, *args):
    QUERY_TYPE = QUERY(QuestionedObjectType, QuestionType)
    return MetadatedType(QUERY_TYPE, *args)



if __name__ == "__main__":
    from persistent_to_disk import create_session
    from persistent.base_type import _Integer, STRING_SIZE

    from sqlalchemy.exc import IntegrityError
    from sqlalchemy import String, Integer


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

    q1 = QUERY_TYPE.GET_CREATE(session, question=v1, questioned_object=i1)
    q2 = QUERY_TYPE.GET_CREATE(session, question=v2, questioned_object=i1)
    q3 = QUERY_TYPE.GET_CREATE(session, question=v3, questioned_object=i3)
    q4 = QUERY_TYPE.GET_CREATE(session, question=v1, questioned_object=i2)
    q5 = QUERY_TYPE.GET_CREATE(session, question=v1, questioned_object=i3)

    print(q1)
    print(q2)
    print(q3)
    print(q4)
    print(q5)

    try:
        q1.questioned_object = i2
        print(q1)
        session.commit()
    except IntegrityError:
        print("Integrity error normal if db already created before")
        session.rollback()

    print(q1.questioned_object)
    print(q1.question)

    QUERY_TYPE2 = QUERY(_Integer, Question)
    QUERY_TYPE3 = QUERY(QuestionedObject, Question)

    print(QUERY_TYPE2 == QUERY_TYPE3)
    print(QUERY_TYPE3 == QUERY_TYPE)
