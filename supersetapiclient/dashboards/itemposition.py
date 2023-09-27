"""Dashboard Nodes Objects."""

import json
import inspect
from enum import Enum
from dataclasses import dataclass, field, asdict, InitVar, Field, make_dataclass
from typing import List, ClassVar, Dict
from supersetapiclient.base import Object, default_string
from supersetapiclient.exceptions import ItemPositionValidationError, NodePositionValidationError
from supersetapiclient.utils import generate_uuid

def _asdict(data):
    return {
        field: value.value if isinstance(value, Enum) else value
        for field, value in data
    }

class ItemPositionType(Enum):
    NONE = None
    ROOT = 'ROOT'
    GRID = 'GRID'
    TABS = 'TABS'
    TAB = 'TAB'
    ROW = 'ROW'
    CHART = 'CHART'
    COLUMN = 'COLUMN'
    MARKDOWN = 'MARKDOWN'
    DIVIDER = 'DIVIDER'

    def __str__(self):
        return str(self.value)

    def __eq__(self, other):
        if str(self.__class__) == str(other.__class__):
            return self.value == other.value
        return False


@dataclass
class MetaItemPosition:
    def __init__(self, data: dict):
        self.__class__ = make_dataclass(self.__class__.__name__, data.keys(), bases=(self.__class__,))
        for k, v in data.items():
            setattr(self, k, v)

    def to_dict(self):
        return asdict(self)

    def to_json(self):
        return self.to_dict()

    def __str__(self):
        return json.dumps(self.to_json())


@dataclass
class ItemPosition:
    ACCEPT_CHILD = True

    id: str = field(init=False, repr=False)
    type_: ItemPositionType = field(init=False, repr=False)
    children: List[str] = field(default_factory=list)
    parents: List[str] = field(default_factory=list)

    def __init__(self, **kwargs):
        type_ = kwargs.get('type_') or kwargs.get('type')
        if not type_:
            strerr = f'type_ argument cannot be empty. Check child class {self.__class__.__name__}.'
            raise ItemPositionValidationError(strerr)
        self.type_ = kwargs.get('type_')
        self.id = kwargs.get('id', self.get_new_uuid())
        if not hasattr(self, 'children'):
            self.children = kwargs.get('children', [])
        if not hasattr(self, 'parents'):
            self.parents = kwargs.get('parents', [])

    def to_dict(self):
        data = asdict(self, dict_factory=_asdict)
        if hasattr(self, 'meta'):
            data['meta'] = self.meta.to_json()
        data['type'] = data['type_']
        data.pop('type_')
        return data

    def to_json(self, columns=None):
        return self.to_dict()

    def __str__(self):
        return json.dumps(self.to_json())

    def get_new_uuid(self):
        return generate_uuid(f'{self.type_}-')

class _RootItemPosition(ItemPosition):
    def __init__(self, **kwargs):
        super().__init__(type_=ItemPositionType.ROOT, id='ROOT_ID', **kwargs)


class _GridItemPosition(ItemPosition):
    def __init__(self, **kwargs):
        super().__init__(type_=ItemPositionType.GRID, id='GRID_ID', **kwargs)


class _TabsItemPosition(ItemPosition):
    def __init__(self, **kwargs):
        self.meta = MetaItemPosition({})
        super().__init__(type_=ItemPositionType.TABS, **kwargs)


class TabItemPosition(ItemPosition):
    def __init__(self, text:str, **kwargs):
        self.meta = MetaItemPosition({
            'text': text,
            'defaultText': 'Tab title',
            'placeholder': 'Tab title'
        })
        super().__init__(type_=ItemPositionType.TAB, **kwargs)

    @property
    def text(self):
        return self.meta.text

    @property
    def defaultText(self):
        return self.meta.defaultText

    @property
    def placeholder(self):
        return self.meta.placeholder

class _RowItemPosition(ItemPosition):
    def __init__(self, background: str = 'BACKGROUND_TRANSPARENT', **kwargs):
        self.meta = MetaItemPosition({
            'background': background
        })
        super().__init__(type_=ItemPositionType.ROW, **kwargs)

    @property
    def background(self):
        return self.meta.background

class MarkdownItemPosition(ItemPosition):
    ACCEPT_CHILD = False
    MAX_WIDTH = 12

    def __init__(self, code:str='', height: int = 50, width: int = 4, **kwargs):
        if width > MarkdownItemPosition.MAX_WIDTH:
            raise NodePositionValidationError(f'Maximum width allowed is  {self.MAX_WIDTH}')

        if width <= 0:
            raise NodePositionValidationError('Width must be greater than zero')

        if height <= 0:
            raise NodePositionValidationError('Height must be greater than zero')

        self.meta = MetaItemPosition({
            'code': code,
            'height': height,
            'width': width
        })
        super().__init__(type_=ItemPositionType.MARKDOWN, **kwargs)

    @property
    def code(self):
        return self.meta.code

    @property
    def width(self):
        return self.meta.width

    @property
    def height(self):
        return self.meta.height


class DividerItemPosition(ItemPosition):
    def __init__(self, **kwargs):
        self.meta = MetaItemPosition({})
        super().__init__(type_=ItemPositionType.DIVIDER, **kwargs)


class ItemPositionParse:
    PARSE = {
        'ROOT': _RootItemPosition,
        'GRID': _GridItemPosition,
        'TABS': _TabsItemPosition,
        'TAB': TabItemPosition,
        'ROW': _RowItemPosition,
        'MARKDOWN': MarkdownItemPosition,
        'DIVIDER': DividerItemPosition
    }

    @classmethod
    def get_instance(cls, **kwargs):
        type_ = kwargs.get('type') or kwargs.get('type_')
        if not type_:
            raise ItemPositionValidationError(f'type_ argument cannot be empty.')
        ItemPositionClass = cls.get_class(type_)
        return ItemPositionClass(**kwargs)

    @classmethod
    def get_class(cls, type_: str):
        return cls.PARSE.get(type_, ItemPosition)