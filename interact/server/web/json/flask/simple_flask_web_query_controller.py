from datastream.controller.query_controller.simple_query_controller import register_query_controller, SimpleQueryController
from datastream.converter.from_any.to_dict import any_to_dict
from datastream.converter.from_json.to_any import json_to_any
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
            latest_queries = self.controller.get(self.queries_per_next)
            return jsonify([{"question": any_to_dict(question), "object": any_to_dict(obj.questioned_object), "choices": self.answer_enum}
                              for obj, question in latest_queries])

        @self.app.route("/processed/", methods=["POST"])
        def process_query():
            jsoned = request.json
            return jsonify(self.controller.answer(json_to_any(jsoned)))

    def set_db_session(self, db_session):
        self.controller.set_db_session(db_session)

    def run(self):
        self.app.run()


register_query_controller(JSON, JSON, HTTP, SimpleFlaskWebQueryServer)
