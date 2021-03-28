
def has_method(obj, name):
    return hasattr(obj.__class__, name) and callable(getattr(obj.__class__, name))
