
def has_method(obj, name):
    # TODO is this a bug? is hasattr always false or what?
    return hasattr(obj.__class__, name) and callable(getattr(obj.__class__, name))

def has_member(obj, name):
    return hasattr(obj, name)
