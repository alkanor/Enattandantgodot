import itertools

from datastream.controller.query_controller.simple_query_controller import register_query_controller, SimpleQueryController
from datastream.converter.from_any.to_dict import any_to_dict
from datastream.converter.from_dict.to_any import dict_to_any
from flask import Flask, jsonify, request
from flask_cors import CORS

from datastream.semantics.communication_canal.http import HTTP
from datastream.semantics.types.json import JSON


class SimpleFlaskWebQueryServer:

    def __init__(self, questioned_object_type, question_type, answer_type, queries_per_next=1, db_session=None):
        self.controller = SimpleQueryController(questioned_object_type, question_type, answer_type, JSON, JSON, HTTP, db_session)
        self.answer_enum = any_to_dict(answer_type)
        self.answer_type = answer_type
        self.queries_per_next = max(1, queries_per_next)
        self.app = Flask(__name__)
        CORS(self.app)

        @self.app.route("/health")
        def health():
            return "OK"

        def __internal_get(latest_queries, session, existing_answers=None):
            res_dict = SimpleFlaskWebQueryServer.craft_final_dict(latest_queries)
            res_dict.update({"answer": self.answer_enum})
            if existing_answers:
                res_dict.update({"existing_answers": {i: {"id": j, "ans": any_to_dict(x)} for i,j,x in existing_answers}})
            res = jsonify(res_dict)
            session.close()
            return res


        @self.app.route("/next")
        @self.app.route("/next/<N>")
        def next_queries(N = -1):
            return __internal_get(*self.controller.get(int(N) if int(N) > 0 else self.queries_per_next))

        @self.app.route("/next_grouped")
        @self.app.route("/next_grouped/<N>")
        def next_queries_stacked(N = -1):
            return __internal_get(*self.controller.get_querylist(int(N) if int(N) > 0 else self.queries_per_next))

        @self.app.route("/next_forobjectgroup")
        @self.app.route("/next_forobjectgroup/<N>")
        def next_queries_grouped_for_objects(N = -1):
            return __internal_get(*self.controller.get_objectgroup(int(N) if int(N) > 0 else self.queries_per_next))

        @self.app.route("/processed", methods=["POST"])
        def process_query():
            jsoned = request.json
            answer, session = self.controller.answer(dict_to_any(jsoned, {"query": None, "answer": self.answer_type}))
            if isinstance(answer, list):
                res = jsonify([{"answer":{"id":a.id}, "processing":{"id":p.id}} for a,p in answer])
            else:
                res = jsonify({"answer":{"id":answer[0].id}, "processing":{"id":answer[1].id}})
            session.close()
            return res

    @staticmethod
    def recursive_dict_crafting(sorted_data, cur_depth, max_depth):
        if cur_depth >= max_depth:
            return [x[0].id for x in sorted_data]
        res_dict = {}
        for i, l in itertools.groupby(sorted_data, lambda x: x[cur_depth]):
            res_dict[i] = SimpleFlaskWebQueryServer.recursive_dict_crafting(l, cur_depth+1, max_depth)
        return res_dict

    @staticmethod
    def craft_final_dict(queries_with_metadata):
        objs = {q[0].questionedobject_id: q[0].questioned_object for q in queries_with_metadata}
        questions = {q[0].question_id: q[0].question for q in queries_with_metadata}
        queries = {q[0].id: (q[0].id, q[0].questionedobject_id, q[0].question_id) for q in queries_with_metadata}

        sorted_data = sorted(queries_with_metadata, key=lambda t: t[1:])
        ordered_queries = SimpleFlaskWebQueryServer.recursive_dict_crafting(sorted_data, 1, len(sorted_data[0]))
        return {
            "objs": any_to_dict(objs.values()),
            "questions": any_to_dict(questions.values()),
            "queries": any_to_dict(queries.values()),
            "ordered_queries": any_to_dict(ordered_queries),
        }

    def set_db_session(self, db_session):
        self.controller.set_db_session(db_session)

    def run(self):
        self.app.run()


register_query_controller(JSON, JSON, HTTP, SimpleFlaskWebQueryServer)



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



    v1 = Question.GET_CREATE(session, question="Is acyclic?")
    v2 = Question.GET_CREATE(session, question="Is tree?")
    v3 = Question.GET_CREATE(session, question="Is directed?")
    v4 = Question.GET_CREATE(session, question="Has root?")

    i1 = QuestionedObject.GET_CREATE(session, graphid=1)
    i2 = QuestionedObject.GET_CREATE(session, graphid=10)
    i3 = QuestionedObject.GET_CREATE(session, graphid=100)


    controller = SimpleFlaskWebQueryServer(QuestionedObject, Question, YesNoUnknown, 1, create_session)

    controller.run()
