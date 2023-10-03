import re
import unicodedata

import inspect
import logging
from typing import Union

import shortuuid

_logger = logging.getLogger(__name__)

def normalize_str(text: str):
    return re.sub('[^A-Za-z0-9_]+', '', unicodedata.normalize('NFKD', text.replace(' ', '_').lower()))


def generate_uuid(_type):
    return f"{_type}-{shortuuid.ShortUUID().random(length=10)}"

def logger(func):
    def wrapper(*args, **kwargs):
        from supersetapiclient.base.base import Object
        self_or_class = None
        if args:
            self_or_class = args[0]
        if kwargs:
            self_or_class = kwargs.get('self', kwargs.get('cls'))

        if self_or_class is None:
            class_name = ''
        else:
            if inspect.isclass(self_or_class):
                class_name = self_or_class.__name__
            elif isinstance(self_or_class, Object):
                class_name = self_or_class.__class__.__name__
            else:
                class_name = ''

        _logger.debug(f'>>> {class_name}.{func.__name__}')
        return func(*args, **kwargs)
    return wrapper


def remove_fields_optional(func):
    """
    Remove from data fields optional null or empty
    :param data:
    :return:
    """

    def wrapper(*args, **kwargs):
        data = func(*args, **kwargs)
        self = args[0]
        for f in self.fields():
            try:
                if f.type.__dict__.get('__origin__') and f.type.__origin__ is Union:
                    try:
                        data.pop(f.name)
                    except KeyError:
                        print('>>> erro ao remover: ', f.name)
            except AttributeError:
                pass
        return data

    return wrapper
