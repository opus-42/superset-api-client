import sys


class ParseMixin:
    @classmethod
    def get_instance(cls, **kwargs):
        type_ = kwargs.get('type') or kwargs.get('type_')
        if not type_:
            raise Exception(f'type_ argument cannot be empty.')
        ParseClass = cls.get_class(type_)
        return ParseClass(**kwargs)

    @classmethod
    def get_class(cls, type_: str):
        suffix = cls.__name__
        class_name = f'{type_.capitalize()}{suffix}'
        return getattr(sys.modules[cls.__module__], class_name, None)