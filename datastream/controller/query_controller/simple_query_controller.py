from sqlalchemy.orm import joinedload

from persistent.datastructure.contextualized import ContextualizedType
from persistent.datastructure.list import LIST
from persistent.model.interact.states.started_finished import StartedFinished_for_session
from persistent.model.interact.processing import PROCESSING
from persistent.model.interact.answer import ANSWER
from persistent.model.interact.query import QUERY
from persistent.base_type import _String

from sqlalchemy import update, or_, func

import itertools


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

        self.GROUP_QUERY_TYPE = LIST(self.QUERY_TYPE)
        self.GROUP_OBJECT_TYPE = LIST(questioned_object_type)

        self.set_db_session_creator(db_session_creator)
        self.__construct_queries()


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


    def __construct_queries(self):
        self.processing_or_answered_queries = lambda session:\
            session.query(self.QUERY_TYPE.id) \
            .outerjoin(self.ANSWER_TYPE, self.PROCESSING_TYPE, self.CONTEXTUALIZED_ANSWER_TYPE,
                       self.CONTEXTUALIZED_PROCESSING_TYPE) \
            .filter(or_(self.CONTEXTUALIZED_PROCESSING_TYPE.context == self.target_name_processing, \
                        self.CONTEXTUALIZED_ANSWER_TYPE.context == self.target_name_answer)) \
            .group_by(self.QUERY_TYPE.id)

        self.answered_queries = lambda session:\
            session.query(self.QUERY_TYPE.id) \
            .outerjoin(self.ANSWER_TYPE, self.ANSWER_TYPE.query_id == self.QUERY_TYPE.id) \
            .outerjoin(self.CONTEXTUALIZED_ANSWER_TYPE,
                       self.CONTEXTUALIZED_ANSWER_TYPE.object_id == self.ANSWER_TYPE.id) \
            .filter(self.CONTEXTUALIZED_ANSWER_TYPE.context == self.target_name_answer) \
            .group_by(self.QUERY_TYPE.id)

        self.all_unanswered_queries = lambda session:\
            session.query(self.QUERY_TYPE) \
                .join(self.QUERY_TYPE.questioned_object, self.QUERY_TYPE.question) \
                .options(joinedload(self.QUERY_TYPE.questioned_object)) \
                .options(joinedload(self.QUERY_TYPE.question)) \
                .filter(self.QUERY_TYPE.id.not_in(self.processing_or_answered_queries(session)))

        self.unanswered_but_processed_queries = lambda session, excluded_queries:\
                session.query(self.QUERY_TYPE.id,
                          self.CONTEXTUALIZED_PROCESSING_TYPE.id.label("cp_id"),
                          self.CONTEXTUALIZED_PROCESSING_TYPE.modified_at,
                          self.CONTEXTUALIZED_PROCESSING_TYPE.created_at) \
                .outerjoin(self.PROCESSING_TYPE, self.PROCESSING_TYPE.query_id == self.QUERY_TYPE.id) \
                .outerjoin(self.CONTEXTUALIZED_PROCESSING_TYPE,
                           self.CONTEXTUALIZED_PROCESSING_TYPE.object_id == self.PROCESSING_TYPE.id) \
                .filter(self.QUERY_TYPE.id.not_in(excluded_queries)) \
                .filter(self.CONTEXTUALIZED_PROCESSING_TYPE.context == self.target_name_processing) \
                .subquery()

        def sorted_unanswered_queries_per_processing_date_func(session, excluded_queries):
            unanswered_but_processed_queries = self.unanswered_but_processed_queries(session, excluded_queries)
            sorted_unanswered_queries_per_processing_date = \
                    session.query(unanswered_but_processed_queries.c.id,
                                  unanswered_but_processed_queries.c.cp_id,
                                  unanswered_but_processed_queries.c.modified_at,
                                  unanswered_but_processed_queries.c.created_at,
                                  func.rank().over(
                                    order_by=(unanswered_but_processed_queries.c.modified_at.desc(),
                                              unanswered_but_processed_queries.c.created_at.desc()),
                                    partition_by=unanswered_but_processed_queries.c.id
                                ).label('rnk')
                    ) \
                    .subquery()

            return (session.query(sorted_unanswered_queries_per_processing_date.c.id,
                                 sorted_unanswered_queries_per_processing_date.c.cp_id,
                                 sorted_unanswered_queries_per_processing_date.c.modified_at,
                                 sorted_unanswered_queries_per_processing_date.c.created_at) \
                          .filter(sorted_unanswered_queries_per_processing_date.c.rnk == 1),
                    sorted_unanswered_queries_per_processing_date.c)

        self.sorted_unanswered_queries_per_processing_date = sorted_unanswered_queries_per_processing_date_func


    def resolve(self, session):
        self.target_name_processing = _String.GET_CREATE(session, f"{self.__class__.__name__}-PROCESSING")
        self.target_name_answer = _String.GET_CREATE(session, f"{self.__class__.__name__}-ANSWER")



    def get_group(self, n=1):
        self.GROUP_OBJECT_TYPE = LIST(questioned_object_type)

    # first_query must return an SQLAlchemy query that is made of any SQLAlchemy objects of type X
    # first_parsing is a conversion function (first_query -> [X]) -> QUERY_TYPE
    # second_query must return an SQLAlchemy query that is made of any SQLAlchemy objects of type Y
    # second_parsing is a conversion function (second_query -> [Y]) -> [Z]
    # third_parsing is a conversion function (second_query -> [Y]) -> CTXT_PROCESSING[id] (for updating appropriate processings)
    def __get_internal(self, first_query, first_parsing, second_query, second_parsing, third_parsing, n=1, length_func=len):
        if n == 0:
            return [], None

        session = self.db_session_creator()
        self.resolve(session)
        remaining_to_get = 0
        result = []

        if n > 0:
            first_batch_query_full, first_batch_query_toupdate = first_query(session, n)
            first_batch = first_batch_query_full.all()
            result.extend(second_parsing(session, first_batch, first_batch))

            queries_to_update = first_parsing(session, first_batch_query_toupdate, first_batch_query_toupdate.all())
            queries_per_id = {q.id: q for q in queries_to_update}
            processings = [
                self.PROCESSING_TYPE.GET_CREATE(session, query=q, status=self.start) for q in queries_per_id.values()
            ]
            contextualized_processings = [
                self.CONTEXTUALIZED_PROCESSING_TYPE(context=self.target_name_processing, obj=p) for p in processings
            ]
            [session.add(cp) for cp in contextualized_processings]
            session.commit()

            remaining_to_get = n - length_func(result)

        if n < 0 or remaining_to_get > 0:
            second_batch_query = second_query(session, n, remaining_to_get)
            second_batch = second_batch_query.all()
            result.extend(second_parsing(session, second_batch_query, second_batch))

            ctprocessingindex = third_parsing(session, second_batch_query, second_batch)
            for processing_id in ctprocessingindex:
                session.execute(update(self.CONTEXTUALIZED_PROCESSING_TYPE).where(self.CONTEXTUALIZED_PROCESSING_TYPE.id == processing_id))
            session.commit()

        return result, session


    def get(self, n=1):
        def query1(session, N):
            result = self.all_unanswered_queries(session).limit(N)
            return result, result
        def parsing1(session, results, results_all):
            return results_all
        def query2(session, N, remaining):
            sorted_unanswered_queries, cols = self.sorted_unanswered_queries_per_processing_date(session, self.answered_queries(session))
            final_end = sorted_unanswered_queries.order_by(cols.modified_at,
                                                           cols.created_at)

            if N < 0:
                kept_objects = final_end.subquery()
            else:
                kept_objects = final_end.limit(remaining).subquery()

            return session.query(self.QUERY_TYPE, kept_objects.c.cp_id) \
                .join(kept_objects, kept_objects.c.id == self.QUERY_TYPE.id) \
                .options(joinedload(self.QUERY_TYPE.questioned_object)) \
                .options(joinedload(self.QUERY_TYPE.question))
        def parsing2(session, results, results_all):
            return [(x[0],) for x in results_all]
        def parsing3(session, results, results_all):
            return [x[1] for x in results_all]

        return self.__get_internal(query1, parsing1, query2, parsing2, parsing3, n)


    def __queries_that_are_not_in_group(self, N, session, group_query_type, join_obj=False, list_metadata_condition=None):
        associated_queries = self.processing_or_answered_queries(session)

        allowed_entries = session.query(group_query_type.__entrytype__.metadata_id)
        if join_obj:
            allowed_entries = allowed_entries.join(self.QUERY_TYPE.__questionobjecttype__)
        allowed_entries = allowed_entries.join(self.QUERY_TYPE) \
                                         .filter(self.QUERY_TYPE.id.not_in(associated_queries))

        if list_metadata_condition:
            allowed_entries = allowed_entries.filter(list_metadata_condition)
        allowed_entries = allowed_entries.group_by(group_query_type.__entrytype__.metadata_id)

        if N > 0:
            allowed_entries = allowed_entries.limit(N)

        res = session.query(self.QUERY_TYPE, group_query_type.__entrytype__.metadata_id)
        if join_obj:
            res = res.options(joinedload(self.QUERY_TYPE.questioned_object)) \
                     .join(group_query_type.__entrytype__, group_query_type.__entrytype__.entry_id == self.QUERY_TYPE.questionedobject_id)
        else:
            res = res.join(group_query_type.__entrytype__)
        res = res.options(joinedload(self.QUERY_TYPE.question)) \
                    .filter(group_query_type.__entrytype__.metadata_id.in_(allowed_entries))
        print(res.all())
        return res, res.filter(self.QUERY_TYPE.id.not_in(associated_queries))


    def get_querylist(self, n=1, list_metadata_condition=None):
        def query1(session, N):
            return self.__queries_that_are_not_in_group(N, session, self.GROUP_QUERY_TYPE, False, list_metadata_condition)
        def parsing1(session, results, results_all):
            return [x[0] for x in results_all]
        def query2(session, N, remaining):
            sorted_unanswered_queries, cols = self.sorted_unanswered_queries_per_processing_date(session,
                                                                                                 self.answered_queries(session))
            print("\n".join(map(repr, sorted_unanswered_queries.all())))

            sorted_unanswered_subquery = sorted_unanswered_queries.subquery()

            sorted_entries = session.query(self.GROUP_QUERY_TYPE.__entrytype__.metadata_id, sorted_unanswered_subquery.c.modified_at,
                                       sorted_unanswered_subquery.c.created_at, sorted_unanswered_subquery.c.cp_id,
                                       func.rank().over(
                                           order_by=(sorted_unanswered_subquery.c.modified_at,
                                                     sorted_unanswered_subquery.c.created_at,
                                                     self.GROUP_QUERY_TYPE.__entrytype__.id),
                                           partition_by=self.GROUP_QUERY_TYPE.__entrytype__.metadata_id
                                       ).label('rnk')
                                   ) \
                            .join(sorted_unanswered_subquery).subquery()

            latest_sorted_entries = session.query(sorted_entries) \
                .filter(sorted_entries.c.rnk == 1) \
                .order_by(sorted_entries.c.modified_at, sorted_entries.c.created_at) \
                .group_by(sorted_entries.c.metadata_id)

            if N < 0:
                latest_sorted_entries_subquery = latest_sorted_entries.subquery()
            else:
                latest_sorted_entries_subquery = latest_sorted_entries.limit(remaining).subquery()

            return session.query(self.QUERY_TYPE, self.GROUP_QUERY_TYPE.__entrytype__.metadata_id) \
                            .join(self.GROUP_QUERY_TYPE.__entrytype__) \
                            .join(latest_sorted_entries_subquery, latest_sorted_entries_subquery.c.metadata_id == self.GROUP_QUERY_TYPE.__entrytype__.metadata_id) \
                            .options(joinedload(self.QUERY_TYPE.questioned_object)) \
                            .options(joinedload(self.QUERY_TYPE.question)) \
                            .order_by(latest_sorted_entries_subquery.c.modified_at, latest_sorted_entries_subquery.c.created_at)
        def parsing2(session, results, results_all):
            return [(x._BasicEntity, x.metadata_id, x._BasicEntity.questionedobject_id) for x in results_all]
        def parsing3(session, results, results_all):
            result_subquery = results.subquery()
            latest_processings = session.query(self.CONTEXTUALIZED_PROCESSING_TYPE.id) \
                                        .join(self.PROCESSING_TYPE) \
                                        .join(self.QUERY_TYPE) \
                                        .join(result_subquery, result_subquery.c.id == self.PROCESSING_TYPE.query_id) \
                                        .filter(self.CONTEXTUALIZED_PROCESSING_TYPE.context == self.target_name_processing) \
                                        .group_by(self.CONTEXTUALIZED_PROCESSING_TYPE.id)
                                        # todo : sort and take only the most recent
                                        # .order_by(self.CONTEXTUALIZED_PROCESSING_TYPE.modified_at, self.CONTEXTUALIZED_PROCESSING_TYPE.created_at) \
            return [x[0] for x in latest_processings.all()]
        def count_different_metadata(results):
            return len(set([x[-1] for x in results]))
        return self.__get_internal(query1, parsing1, query2, parsing2, parsing3, n, count_different_metadata)


    def get_objectgroup(self, n=1):
        def query1(session, N):
            return self.__queries_that_are_not_in_group(N, session, self.GROUP_OBJECT_TYPE, True)
        def parsing1(session, results, results_all):
            return [x[0] for x in results_all]
        def query2(session, N, remaining):
            print(f"REMAINING: {remaining}")
            sorted_unanswered_queries, cols = self.sorted_unanswered_queries_per_processing_date(session,
                                                                                                 self.answered_queries(session))
            print("\n".join(map(repr, sorted_unanswered_queries.all())))

            sorted_unanswered_subquery = sorted_unanswered_queries.subquery()

            sorted_entries = session.query(self.GROUP_OBJECT_TYPE.__entrytype__.metadata_id, sorted_unanswered_subquery.c.modified_at,
                                       sorted_unanswered_subquery.c.created_at, sorted_unanswered_subquery.c.cp_id,
                                       func.rank().over(
                                           order_by=(sorted_unanswered_subquery.c.modified_at,
                                                     sorted_unanswered_subquery.c.created_at,
                                                     self.GROUP_OBJECT_TYPE.__entrytype__.id),
                                           partition_by=self.GROUP_OBJECT_TYPE.__entrytype__.metadata_id
                                       ).label('rnk')
                                   ) \
                            .join(self.QUERY_TYPE.__questionobjecttype__,
                                  self.QUERY_TYPE.__questionobjecttype__.id == self.GROUP_OBJECT_TYPE.__entrytype__.entry_id) \
                            .join(self.QUERY_TYPE,
                                  self.QUERY_TYPE.questionedobject_id == self.GROUP_OBJECT_TYPE.__entrytype__.entry_id) \
                            .join(sorted_unanswered_subquery, sorted_unanswered_subquery.c.id == self.QUERY_TYPE.id) \
                            .subquery()

            latest_sorted_entries = session.query(sorted_entries) \
                .filter(sorted_entries.c.rnk == 1) \
                .order_by(sorted_entries.c.modified_at, sorted_entries.c.created_at) \
                .group_by(sorted_entries.c.metadata_id)

            if N < 0:
                latest_sorted_entries_subquery = latest_sorted_entries.subquery()
            else:
                latest_sorted_entries_subquery = latest_sorted_entries.limit(remaining).subquery()

            print("\n".join(map(repr, latest_sorted_entries.all())))

            return session.query(self.QUERY_TYPE, self.GROUP_OBJECT_TYPE.__entrytype__.metadata_id) \
                            .options(joinedload(self.QUERY_TYPE.questioned_object)) \
                            .join(self.GROUP_OBJECT_TYPE.__entrytype__, self.GROUP_OBJECT_TYPE.__entrytype__.entry_id == self.QUERY_TYPE.questionedobject_id) \
                            .join(latest_sorted_entries_subquery, latest_sorted_entries_subquery.c.metadata_id == self.GROUP_OBJECT_TYPE.__entrytype__.metadata_id) \
                            .options(joinedload(self.QUERY_TYPE.question)) \
                            .order_by(latest_sorted_entries_subquery.c.modified_at, latest_sorted_entries_subquery.c.created_at)
        def parsing2(session, results, results_all):
            return [(x._BasicEntity, x.metadata_id, x._BasicEntity.questionedobject_id) for x in results_all]
        def parsing3(session, results, results_all):
            result_subquery = results.subquery()
            latest_processings = session.query(self.CONTEXTUALIZED_PROCESSING_TYPE.id) \
                                        .join(self.PROCESSING_TYPE) \
                                        .join(self.QUERY_TYPE) \
                                        .join(result_subquery, result_subquery.c.id == self.PROCESSING_TYPE.query_id) \
                                        .filter(self.CONTEXTUALIZED_PROCESSING_TYPE.context == self.target_name_processing) \
                                        .group_by(self.CONTEXTUALIZED_PROCESSING_TYPE.id)
                                        # todo : sort and take only the most recent
                                        # .order_by(self.CONTEXTUALIZED_PROCESSING_TYPE.modified_at, self.CONTEXTUALIZED_PROCESSING_TYPE.created_at) \
            return [x[0] for x in latest_processings.all()]
        def count_different_metadata(results):
            print("OKOK COUNT")
            print(results)
            print(len(set([x[-1] for x in results])))
            print("========================")
            return len(set([x[-1] for x in results]))

        return self.__get_internal(query1, parsing1, query2, parsing2, parsing3, n, count_different_metadata)


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
    from persistent.base_type import BasicEntity, STRING_SIZE

    from sqlalchemy import String, Integer, Column


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

    GroupedObject = LIST(QuestionedObject)
    GroupedQueries = LIST(QUERY_TYPE)
    g = GroupedObject(session, name="test grouped")

    if len(g.entries) < 2:
        g.add(session, i1)
        g.add(session, i2)
        g2 = GroupedObject(session, name="test grouped 2")
        g2.add(session, i1)
        g2.add(session, i3)
        g3 = GroupedObject(session, name="test grouped 3")
        g3.add(session, i2)
        g3.add(session, i3)

        g = GroupedQueries(session, name="test gqueries")
        g.add(session, queries[0])
        g.add(session, queries[1])
        g.add(session, queries[2])
        g.add(session, queries[3])
        g2 = GroupedQueries(session, name="test gqueries 2")
        g2.add(session, queries[0])
        g2.add(session, queries[6])
        g2.add(session, queries[7])
        g2.add(session, queries[8])
        g3 = GroupedQueries(session, name="test gqueries 3")
        g3.add(session, queries[0])
        g3.add(session, queries[10])
        g3.add(session, queries[11])
        g4 = GroupedQueries(session, name="test gqueries 4")
        g4.add(session, queries[4])
        g4.add(session, queries[9])

    s = SimpleQueryController(QuestionedObject, Question, ANSWER_TYPE, None, None, None, create_session)
    s.resolve(session)

    tmp, session2 = s.get_querylist(1)
    for i in tmp:
        print(i)
    session2.close()

    import time
    time.sleep(1)

    tmp, session3 = s.get_objectgroup(1)
    print(tmp)
    exit()

    sorted_queries, cols = s.sorted_unanswered_queries_per_processing_date(session,
                                                                           s.answered_queries(session))
    print("\n".join(map(repr, sorted_queries.all())))

    final_end = sorted_queries.subquery()

    final2 = session.query(GroupedQueries.__entrytype__.metadata_id, final_end.c.modified_at, final_end.c.created_at,
                               func.rank().over(
                                   order_by=(final_end.c.modified_at,
                                             final_end.c.created_at),
                                   partition_by=GroupedQueries.__entrytype__.metadata_id
                               ).label('rnk')
                           ) \
                    .join(final_end).subquery()

    final2 = session.query(final2) \
                    .filter(final2.c.rnk == 1) \
                    .order_by(final2.c.modified_at, final2.c.created_at) \
                    .limit(3)

    print("\n".join(map(repr, final2.all())))

    final2 = final2.subquery()

    full_res = session.query(QUERY_TYPE, final2.c.metadata_id) \
                    .join(GroupedQueries.__entrytype__) \
                    .join(final2, final2.c.metadata_id == GroupedQueries.__entrytype__.metadata_id) \
                    .order_by(final2.c.modified_at, final2.c.created_at)

    print("\n".join(map(repr, full_res.all())))

    exit()

    sub2 = session.query(QUERY_TYPE) \
        .join(QUERY_TYPE.questioned_object) \
        .options(joinedload(QUERY_TYPE.questioned_object)) \
        .outerjoin(ANSWER_TYPE, PROCESSING_TYPE, CONTEXTED_ANSWER_TYPE, CONTEXTED_PROCESSING_TYPE) \
        .group_by(QUERY_TYPE.questioned_object)
    #print(sub2.all())

    sub2 = session.query(GroupedObject.__entrytype__, QUERY_TYPE) \
        .join(QUERY_TYPE.questioned_object) \
        .options(joinedload(QUERY_TYPE.questioned_object)) \
        .join(GroupedObject.__entrytype__.metadataobj) \
        .options(joinedload(GroupedObject.__entrytype__.metadataobj)) \
        .outerjoin(ANSWER_TYPE, PROCESSING_TYPE, CONTEXTED_ANSWER_TYPE, CONTEXTED_PROCESSING_TYPE) \
        .group_by(GroupedObject.__entrytype__.metadata_id)
    res2 = sub2.all()
    print(res2[0][1])
    print(res2[0][0].metadataobj)
    print(res2[0][0].entry)
    print([x[0].metadataobj for x in res2])


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
