from datastream.controller.query_controller.simple_query_controller import register_query_controller, SimpleQueryController
from datastream.converter.from_any.to_json import any_to_json
from datastream.converter.from_json.to_any import json_to_any
from flask import Flask, jsonify, request
import json


class SimpleFlaskWebQueryServer:

    def __init__(self, question, answer_type, queries_per_next=1):
        self.controller = SimpleQueryController(question, answer_type, JSON, JSON, HTTP)
        self.jsoned_question = to_json(question)
        self.jsoned_answer_enum = to_json(answer_type)
        self.answer_type = answer_type
        self.queries_per_next = max(1, queries_per_next)
        self.app = Flask(__name__)

        @self.app.route("/health")
        def health():
            return "OK"

        @self.app.route("/next")
        def next_queries():
            latest_queries = self.controller.get(self.queries_per_next)
            return jsonify([{"question": self.jsoned_question, "object": to_json(obj.questioned_object), "choices": self.jsoned_answer_enum}
                                    for obj in latest_queries])

        @self.app.route("/processed/<query_id>", methods=["POST"])
        def process_query(query_id):
            jsoned = request.json
            self.controller.answer(query_id, jsoned)

    def run(self):
        self.app.run()


register_query_controller(JSON, JSON, HTTP, SimpleFlaskWebQueryServer)
