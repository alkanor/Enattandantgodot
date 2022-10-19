

def type_to_string(type_or_instance, ctxt=None):
    if isinstance(type_or_instance, type):
        return type_or_instance.__module__ + "::" + type_or_instance.__name__
    else:
        return type_or_instance.__class__.__module__ + "::" + type_or_instance.__class__.__name__
