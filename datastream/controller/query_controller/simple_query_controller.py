

controllers_per_canal = {}

def register_query_controller(communication_canal_type, query_controller):
    assert communication_canal_type not in controllers_per_canal, f"Unable to register simple query controller for already enabled canal {communication_canal_type}"
    controllers_per_canal[communication_canal_type] = query_controller


class SimpleQueryController:

    def __init__(self, questioned_object, question, answer_type, repr_type, parse_type, communication_canal_type):
def get(n=-1):
    pass


def deal_with(ref, data):
    pass
