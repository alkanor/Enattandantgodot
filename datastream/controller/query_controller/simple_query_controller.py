from sqlalchemy.orm import joinedload

from persistent.datastructure.contextualized import ContextualizedType
from persistent.model.interact.states.started_finished import StartedFinished_for_session
from persistent.model.interact.processing import PROCESSING
from persistent.model.interact.answer import ANSWER
from persistent.model.interact.query import QUERY
from persistent.base_type import _String

from sqlalchemy import update
from sqlalchemy import or_


controllers_per_canal = {}

def register_query_controller(repr_type, parse_type, communication_canal_type, query_controller):
    assert (repr_type, parse_type, communication_canal_type) not in controllers_per_canal, \
            f"Unable to register simple query controller for already enabled canal {(repr_type, parse_type, communication_canal_type)}"
    controllers_per_canal[(repr_type, parse_type, communication_canal_type)] = query_controller


class SimpleQueryController:

    def __init__(self, questioned_object_type, question_type, answer_type, repr_type, parse_type, communication_canal_type, db_session_creator=None):
        self.REPR_TYPE = repr_type
        self.PARSE_TYPE = parse_type
        self.CANAL_TYPE = communication_canal_type

        self.QUERY_TYPE = QUERY(questioned_object_type, question_type)
        self.ANSWER_TYPE = ANSWER(self.QUERY_TYPE, answer_type)
        self.CONTEXTUALIZED_ANSWER_TYPE = ContextualizedType(self.ANSWER_TYPE, _String)

        self.set_db_session_creator(db_session_creator)


    def set_db_session_creator(self, db_session_creator):
        if db_session_creator:
            self.db_session_creator = db_session_creator
            session = self.db_session_creator()
            self.STATUS_TYPE = StartedFinished_for_session(session)
            self.start = self.STATUS_TYPE.Started.value
            self.finished = self.STATUS_TYPE.Finished.value
            self.PROCESSING_TYPE = PROCESSING(self.QUERY_TYPE, self.STATUS_TYPE.__sqlalchemy_object__)
            self.CONTEXTUALIZED_PROCESSING_TYPE = ContextualizedType(self.PROCESSING_TYPE, _String)
            session.close()
        else:
            self.db_session = None
            self.STATUS_TYPE = None
            self.PROCESSING_TYPE = None
            self.METADATED_PROCESSING_TYPE = None
            self.target_name_processing = None
            self.target_name_answer = None


    def resolve(self, session):
        self.target_name_processing = _String.GET_CREATE(session, f"{self.__class__.__name__}-PROCESSING")
        self.target_name_answer = _String.GET_CREATE(session, f"{self.__class__.__name__}-ANSWER")


    def get(self, n=1):
        session = self.db_session_creator()
        self.resolve(session)
        remaining_to_get = 0
        result = []
        if n > 0:
            sub = session.query(self.QUERY_TYPE.id) \
                    .outerjoin(self.ANSWER_TYPE, self.PROCESSING_TYPE, self.CONTEXTUALIZED_ANSWER_TYPE, self.CONTEXTUALIZED_PROCESSING_TYPE) \
                        .filter(or_(self.CONTEXTUALIZED_PROCESSING_TYPE.context == self.target_name_processing, \
                                    self.CONTEXTUALIZED_ANSWER_TYPE.context == self.target_name_answer)) \
                        .group_by(self.QUERY_TYPE.id)

            all_unanswered_queries = session.query(self.QUERY_TYPE) \
                                            .join(self.QUERY_TYPE.questioned_object, self.QUERY_TYPE.question) \
                                            .options(joinedload(self.QUERY_TYPE.questioned_object)) \
                                            .options(joinedload(self.QUERY_TYPE.question)) \
                                            .filter(self.QUERY_TYPE.id.not_in(sub))
            limited_answers = all_unanswered_queries.limit(n).all()
            result.extend(limited_answers)

            processings = [self.PROCESSING_TYPE.GET_CREATE(session, query=q, status=self.start) for q in limited_answers]
            contextualized_processings = [self.CONTEXTUALIZED_PROCESSING_TYPE(context=self.target_name_processing, obj=p) for p in processings]
            [session.add(cp) for cp in contextualized_processings]
            session.commit()

            remaining_to_get = n - len(result)

        if n <= 0 or remaining_to_get > 0:
            sub_bis = session.query(self.QUERY_TYPE.id) \
                        .outerjoin(self.ANSWER_TYPE, self.ANSWER_TYPE.query_id == self.QUERY_TYPE.id) \
                        .outerjoin(self.CONTEXTUALIZED_ANSWER_TYPE, self.CONTEXTUALIZED_ANSWER_TYPE.object_id == self.ANSWER_TYPE.id) \
                            .filter(self.CONTEXTUALIZED_ANSWER_TYPE.context == self.target_name_answer) \
                            .group_by(self.QUERY_TYPE.id)

            final = session.query(self.QUERY_TYPE, self.CONTEXTUALIZED_PROCESSING_TYPE) \
                    .join(self.QUERY_TYPE.questioned_object, self.QUERY_TYPE.question) \
                    .options(joinedload(self.QUERY_TYPE.questioned_object)) \
                    .options(joinedload(self.QUERY_TYPE.question)) \
                    .outerjoin(self.PROCESSING_TYPE, self.PROCESSING_TYPE.query_id == self.QUERY_TYPE.id) \
                    .outerjoin(self.CONTEXTUALIZED_PROCESSING_TYPE, self.CONTEXTUALIZED_PROCESSING_TYPE.object_id == self.PROCESSING_TYPE.id) \
                        .filter(self.QUERY_TYPE.id.not_in(sub_bis)) \
                        .filter(self.CONTEXTUALIZED_PROCESSING_TYPE.context == self.target_name_processing) \
                            .order_by(self.CONTEXTUALIZED_PROCESSING_TYPE.modified_at,
                                      self.CONTEXTUALIZED_PROCESSING_TYPE.created_at) \
                            .group_by(self.QUERY_TYPE.id)

            if n <= 0:
                final_results = final.all()
            else:
                final_results = final.limit(remaining_to_get).all()

            result.extend([query for query, _ in final_results])
            for _, processing in final_results:
                session.execute(update(self.CONTEXTUALIZED_PROCESSING_TYPE).where(self.CONTEXTUALIZED_PROCESSING_TYPE.id == processing.id))
            session.commit()
        return result, session

    def answer(self, data, session=None):
        if not session:
            session = self.db_session_creator()
            self.resolve(session)

        if isinstance(data, list):
            return [self.answer(d, session)[0] for d in data], session

        related_query = session.query(self.QUERY_TYPE).filter_by(**data["query"]).one()
        related_answer = data["answer"](session)
        answer = self.ANSWER_TYPE.GET_CREATE(session, query=related_query, answer=related_answer)
        processing = self.PROCESSING_TYPE.GET_CREATE(session, query=related_query, status=self.finished)
        contextualized_answer = self.CONTEXTUALIZED_ANSWER_TYPE(session, context=self.target_name_answer, obj=answer)
        contextualized_processings = self.CONTEXTUALIZED_PROCESSING_TYPE(session, context=self.target_name_processing, obj=processing)

        return (contextualized_answer, contextualized_processings), session


if __name__ == "__main__":
    from persistent.model.interact.answers.yes_no_unknown import YesNoUnknown

    from persistent_to_disk import create_session
    from persistent.base_type import BasicEntity, STRING_SIZE, _String

    from sqlalchemy import String, Integer, Column, or_


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


    session = create_session()


    QUERY_TYPE = QUERY(QuestionedObject, Question)
    STATUS_TYPE = StartedFinished_for_session(session)
    PROCESSING_TYPE = PROCESSING(QUERY_TYPE, STATUS_TYPE.__sqlalchemy_object__)
    CONTEXTED_PROCESSING_TYPE = ContextualizedType(PROCESSING_TYPE, _String)
    ANSWER_TYPE = ANSWER(QUERY_TYPE, YesNoUnknown)
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
    sub = session.query(QUERY_TYPE.id) \
            .outerjoin(ANSWER_TYPE, PROCESSING_TYPE, CONTEXTED_ANSWER_TYPE, CONTEXTED_PROCESSING_TYPE) \
                .filter(or_(CONTEXTED_PROCESSING_TYPE.context == target_name_processing, \
                            CONTEXTED_ANSWER_TYPE.context == target_name_answer)) \
                .group_by(QUERY_TYPE.id)
    res = session.query(QUERY_TYPE).filter(QUERY_TYPE.id.not_in(sub)).all()
    print(res)
    print(len(res))

    N = 5
    to_deal_with = res[:N]
    M = 3

    # just pass all as processing
    new_processing = [PROCESSING_TYPE.GET_CREATE(session, query=v, status=start) for v in to_deal_with]
    metadated_processing = [CONTEXTED_PROCESSING_TYPE(session, target_name_processing, v) for v in new_processing]
    print(metadated_processing)


    if len(to_deal_with) == N:
        # take 3 out of them and mark them as finished (1 per second)
        import time
        for i in range(3):
            new_processing[i].status = finished
            session.commit()
            a = ANSWER_TYPE.GET_CREATE(session, query=to_deal_with[i], answer=yes)
            metadated_a = CONTEXTED_ANSWER_TYPE(session, target_name_answer, a)
            print(metadated_a)
            time.sleep(1)
            session.execute(update(CONTEXTED_PROCESSING_TYPE).where(CONTEXTED_PROCESSING_TYPE.id == metadated_processing[i].id))
        for i in range(2):
            session.execute(update(CONTEXTED_PROCESSING_TYPE).where(CONTEXTED_PROCESSING_TYPE.id == metadated_processing[i+3].id))
    else:
        print(dir(CONTEXTED_PROCESSING_TYPE))
        sub = session.query(QUERY_TYPE.id) \
                .outerjoin(ANSWER_TYPE, ANSWER_TYPE.query_id == QUERY_TYPE.id) \
                .outerjoin(CONTEXTED_ANSWER_TYPE, CONTEXTED_ANSWER_TYPE.object_id == ANSWER_TYPE.id) \
                    .filter(CONTEXTED_ANSWER_TYPE.context_id == target_name_answer.id) \
                    .group_by(QUERY_TYPE.id)
        res = session.query(QUERY_TYPE, _String, Question, QuestionedObject, PROCESSING_TYPE, CONTEXTED_PROCESSING_TYPE) \
                .outerjoin(PROCESSING_TYPE, PROCESSING_TYPE.query_id == QUERY_TYPE.id) \
                .outerjoin(CONTEXTED_PROCESSING_TYPE, CONTEXTED_PROCESSING_TYPE.object_id == PROCESSING_TYPE.id) \
                .outerjoin(Question) \
                .outerjoin(QuestionedObject) \
                .filter(QUERY_TYPE.id.not_in(sub)) \
                    .group_by(QUERY_TYPE.id) \
                    .order_by(CONTEXTED_PROCESSING_TYPE.modified_at, CONTEXTED_PROCESSING_TYPE.created_at) \
                    .all()
        print(res)
        print(len(res))
        print(type(CONTEXTED_ANSWER_TYPE.context))
