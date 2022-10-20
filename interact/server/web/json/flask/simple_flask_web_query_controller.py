from datastream.controller.query_controller.simple_query_controller import register_query_controller, SimpleQueryController
from datastream.converter.from_any.to_dict import any_to_dict
from datastream.converter.from_dict.to_any import dict_to_any
from flask import Flask, jsonify, request

from datastream.semantics.communication_canal.http import HTTP
from datastream.semantics.types.json import JSON


class SimpleFlaskWebQueryServer:

    def __init__(self, questioned_object_type, question_type, answer_type, queries_per_next=1, db_session=None):
        self.controller = SimpleQueryController(questioned_object_type, question_type, answer_type, JSON, JSON, HTTP, db_session)
        self.answer_enum = any_to_dict(answer_type)
        self.answer_type = answer_type
        self.queries_per_next = max(1, queries_per_next)
        self.app = Flask(__name__)

        @self.app.route("/health")
        def health():
            return "OK"

        @self.app.route("/next")
        def next_queries():
            latest_queries, session = self.controller.get(self.queries_per_next)
            res = jsonify([{"question": any_to_dict(q.question), "object": any_to_dict(q.questioned_object), "query": q.id, "answer": self.answer_enum}
                              for q in latest_queries])
            session.close()
            return res

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
