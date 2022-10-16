from persistent.datastructure.contextualized import ContextualizedType
from persistent.model.interact.states.started_finished import StartedFinished_for_session
from persistent.model.interact.processing import PROCESSING
from persistent.model.interact.answer import ANSWER
from persistent.model.interact.query import QUERY


controllers_per_canal = {}

def register_query_controller(repr_type, parse_type, communication_canal_type, query_controller):
    assert (repr_type, parse_type, communication_canal_type) not in controllers_per_canal, \
            f"Unable to register simple query controller for already enabled canal {(repr_type, parse_type, communication_canal_type)}"
    controllers_per_canal[(repr_type, parse_type, communication_canal_type)] = query_controller


class SimpleQueryController:

    def __init__(self, questioned_object_type, question_type, answer_type, repr_type, parse_type, communication_canal_type, db_session=None):
        self.REPR_TYPE = repr_type
        self.PARSE_TYPE = parse_type
        self.CANAL_TYPE = communication_canal_type

        self.QUERY_TYPE = QUERY(questioned_object_type, question_type)
        self.ANSWER_TYPE = ANSWER(self.QUERY_TYPE, answer_type)
        self.METADATED_ANSWER_TYPE = MetadatedType(self.ANSWER_TYPE, NAMED_DATE_METADATA(
                                                f"BasicAnswer_{self.CANAL_TYPE.__name__}_{self.REPR_TYPE.__name__}_{self.PARSE_TYPE.__name__}"))

        self.set_db_session(db_session)


    def set_db_session(self, db_session):
        if db_session:
            self.db_session = db_session
            self.STATUS_TYPE = StartedFinished_for_session(db_session)
            self.PROCESSING_TYPE = PROCESSING(self.QUERY_TYPE, self.STATUS_TYPE)
            self.METADATED_PROCESSING_TYPE = MetadatedType(self.PROCESSING_TYPE, NAMED_DATE_METADATA(
                                                f"BasicProcessing_{self.CANAL_TYPE.__name__}_{self.REPR_TYPE.__name__}_{self.PARSE_TYPE.__name__}"))
        else:
            self.db_session = None
            self.STATUS_TYPE = None
            self.PROCESSING_TYPE = None
            self.METADATED_PROCESSING_TYPE = None


    def get(self, n=-1):
        all_unanswered_queries = self.db_session.query(self.QUERY_TYPE).join(self.ANSWER_TYPE).filter()
        pass


    def answer(ref, data):
        pass


if __name__ == "__main__":
    from persistent.model.interact.answers.yes_no_unknown import YesNoUnknown
    from persistent.model.interact.answers.answer_statement import AnswerStatement

    from persistent_to_disk import create_session
    from persistent.base_type import BasicEntity, STRING_SIZE, _String

    from sqlalchemy import String, Integer, Column, or_, update


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
        "answer": Column(String(STRING_SIZE), unique=True),
    }

    Answer = BasicEntity("basicanswer", columns)


    session = create_session()


    QUERY_TYPE = QUERY(QuestionedObject, Question)
    STATUS_TYPE = StartedFinished_for_session(session)
    PROCESSING_TYPE = PROCESSING(QUERY_TYPE, STATUS_TYPE.__sqlalchemy_object__)
    CONTEXTED_PROCESSING_TYPE = ContextualizedType(PROCESSING_TYPE, _String)
    ANSWER_TYPE = ANSWER(QUERY_TYPE, AnswerStatement)
    CONTEXTED_ANSWER_TYPE = ContextualizedType(ANSWER_TYPE, _String)


    v1 = Question.GET_CREATE(session, question="Is acyclic?")
    v2 = Question.GET_CREATE(session, question="Is tree?")
    v3 = Question.GET_CREATE(session, question="Is directed?")
    v4 = Question.GET_CREATE(session, question="Has root?")

    i1 = QuestionedObject.GET_CREATE(session, graphid=1)
    i2 = QuestionedObject.GET_CREATE(session, graphid=10)
    i3 = QuestionedObject.GET_CREATE(session, graphid=100)

    yes = YesNoUnknown.YES(session)
    no = YesNoUnknown.NO(session)
    unknown = YesNoUnknown.UNKNOWN(session)

    start = STATUS_TYPE.Started.value
    finished = STATUS_TYPE.Finished.value


    from itertools import product

    questioned_objects_questions = list(product([i1, i2, i3], [v1, v2, v3, v4]))

    queries = [QUERY_TYPE.GET_CREATE(session, questioned_object=qo, question=q) for qo, q in questioned_objects_questions]

    p = PROCESSING_TYPE.GET_CREATE(session, query=queries[0], status=start)

    print(start)
    print(p)

    process_test_ctxt = _String.GET_CREATE(session, "processing test")
    ctxted_processing = CONTEXTED_PROCESSING_TYPE(session, p, process_test_ctxt)
    print(ctxted_processing)


    res = session.query(QUERY_TYPE).all()
    print(len(res), res)

    a = ANSWER_TYPE.GET_CREATE(session, query=queries[1], answer=yes)
    print(a)
    answer_test_ctxt = _String.GET_CREATE(session, "answer query 1")
    ctxted_answer = CONTEXTED_ANSWER_TYPE(session, answer_test_ctxt, a)
    print(ctxted_answer)

    # Ensemble des queries sans answers hors processing recherchées
    target_name_processing = _String.GET_CREATE(session, "MAIN_CONTROLLER_TEST-PROCESSING")
    target_name_answer = _String.GET_CREATE(session, "MAIN_CONTROLLER_TEST-ANSWER")
    res = session.query(QUERY_TYPE) \
            .outerjoin(ANSWER_TYPE) \
            .outerjoin(PROCESSING_TYPE) \
            .outerjoin(CONTEXTED_ANSWER_TYPE) \
            .outerjoin(CONTEXTED_PROCESSING_TYPE) \
                .filter(or_(PROCESSING_TYPE.query == None, CONTEXTED_PROCESSING_TYPE.context != target_name_processing)) \
                .filter(or_(ANSWER_TYPE.query == None, CONTEXTED_ANSWER_TYPE.context != target_name_answer)).all()
    print(res)
    print(len(res))

    N = 5
    to_deal_with = res[:N]
    M = 3

    if len(to_deal_with) == N:
        # just pass the 5 as processing
        new_processing = [PROCESSING_TYPE.GET_CREATE(session, query=v, status=start) for v in to_deal_with]
        metadated_processing = [CONTEXTED_PROCESSING_TYPE(session, target_name_processing, v) for v in new_processing]
        print(metadated_processing)

        # take 3 out of them and mark them as finished (1 per second)
        mc = PROCESSING_METADATA_ENTRY.__metadataclass__
        target_answer = METADATED_ANSWER_TYPE.__metadataclass__.GET_CREATE(session, name=target_name_answer)

        import time
        for i in range(3):
            new_processing[i].status = finished
            session.commit()
            a = ANSWER_TYPE.GET_CREATE(session, query=to_deal_with[i], answer=yes)
            metadated_a = METADATED_ANSWER_TYPE(session, target_answer, a)
            print(metadated_a)
            time.sleep(1)
            session.execute(update(mc).where(mc.id == metadated_processing[i].metadata.id))
    else:
        res = session.query(QUERY_TYPE) \
            .outerjoin(ANSWER_TYPE) \
            .outerjoin(PROCESSING_TYPE) \
            .outerjoin(ANSWER_METADATA_ENTRY) \
            .outerjoin(ANSWER_METADATA_ENTRY.__metadataclass__) \
            .filter(or_(ANSWER_TYPE.query == None, ANSWER_METADATA_ENTRY.__metadataclass__.name != target_name)).all()
        print(len(res), res)

 #   res = session.query(QUERY_TYPE).outerjoin(ANSWER_TYPE).filter(ANSWER_TYPE.query_id == None).all()
 #   print(len(res), res)
