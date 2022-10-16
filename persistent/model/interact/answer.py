from sqlalchemy import Column, ForeignKey, UniqueConstraint, Integer
from sqlalchemy.orm import relationship, declared_attr

from persistent.datastructure.metadated import MetadatedType
from persistent.base import BaseAndMetaChangeClassName
from persistent.type_system import register_type
from persistent.base_type import BasicEntity


__objectname__ = "ANSWER"


#@register_args({"QueryType": Query, "AnswerType": Answer}) # TODO: global type system registration for graph representation
@register_type(__objectname__, lambda QueryType, AnswerType: (QueryType.__tablename__, AnswerType.__tablename__))
def ANSWER(QueryType, AnswerType):

    answer_tablename = f'{__objectname__}<{QueryType.__tablename__},{AnswerType.__tablename__}>'

    ChangeClassNameBase, _ = BaseAndMetaChangeClassName(QueryType, AnswerType)

    class ANSWER_OBJECT(ChangeClassNameBase):
        __tablename__ = answer_tablename
        __questionobjecttype__ = QueryType.__questionobjecttype__
        __questiontype__ = QueryType.__questiontype__
        __answertype__ = AnswerType

        id = Column(Integer, primary_key=True)
        query_id = Column(Integer, ForeignKey(QueryType.id), nullable=False)
        answer_id = Column(Integer, ForeignKey(AnswerType.id), nullable=False)

        __table_args__ = (UniqueConstraint("query_id", "answer_id", name="unique_query"), )

        @declared_attr
        def query(cls):
            return relationship(QueryType, foreign_keys=[cls.query_id])

        @declared_attr
        def answer(cls):
            return relationship(AnswerType, foreign_keys=[cls.answer_id])

        @property
        def questioned_object(self):
            return self.query.questioned_object

        @property
        def question(self):
            return self.query.question

        @questioned_object.setter
        def questioned_object(self, data):
            self.query.questioned_object = data

        @question.setter
        def question(self, data):
            self.query.question = data

        def __repr__(self):
            return f'(A{self.id}) {self.query} -> {self.answer}'


    _ANSWER = BasicEntity(ANSWER_OBJECT.__tablename__, ["id", "query_id", "answer_id", "query", "answer"], ANSWER_OBJECT, __objectname__)

    return _ANSWER


def MetadatedAnswer(QueryType, AnswerType, *args):
    ANSWER_TYPE = ANSWER(QueryType, AnswerType)
    return MetadatedType(ANSWER_TYPE, *args)



if __name__ == "__main__":
    from persistent_to_disk import create_session
    from persistent.base_type import STRING_SIZE

    from sqlalchemy.exc import IntegrityError
    from sqlalchemy import String, Integer

    from .query import QUERY


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

    columns = {
        "id": Column(Integer, primary_key=True),
        "answer": Column(String(STRING_SIZE), unique=True),
    }

    Answer = BasicEntity("basicanswer", columns)


    session = create_session()

    v1 = Question.GET_CREATE(session, question="Is acyclic?")
    v2 = Question.GET_CREATE(session, question="Is tree?")
    v3 = Question.GET_CREATE(session, question="Is directed?")
    v4 = Question.GET_CREATE(session, question="Has root?")

    i1 = QuestionedObject.GET_CREATE(session, graphid=1)
    i2 = QuestionedObject.GET_CREATE(session, graphid=10)
    i3 = QuestionedObject.GET_CREATE(session, graphid=100)

    yes = Answer.GET_CREATE(session, answer="yes")
    no = Answer.GET_CREATE(session, answer="no")


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
