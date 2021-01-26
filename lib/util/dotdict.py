class ShadowError(BaseException):
    pass

class DotDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __init__(self, dct: dict = None, shadow: bool = False):
        super().__init__()
        if dct is not None:
            built_in = ['clear', 'copy', 'fromkeys', 'get',
                        'items', 'keys', 'pop', 'popitem',
                        'setdefault', 'update', 'values']
            for key, value in dct.items():
                if shadow and (key.startswith('__') or key in built_in):
                    raise ShadowError(f'"{key}" is a built-in method of dict')
                if hasattr(value, 'keys'):
                    value = DotDict(value)
                self[key] = value
            self.__raw__ = dct
