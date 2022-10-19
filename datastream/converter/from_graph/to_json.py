from .to_dict import graph_to_dict
import json


def graph_to_json(graph, ctxt=None):
    return json.loads(graph_to_dict(graph, ctxt))
