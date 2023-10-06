"""Dashboard Nodes Objects."""

import json
from enum import Enum
from dataclasses import dataclass, field, asdict, make_dataclass
from typing import List
from supersetapiclient.base.enum_str import StringEnum
from supersetapiclient.base.parse import ParseMixin
from supersetapiclient.exceptions import ItemPositionValidationError, NodePositionValidationError
from supersetapiclient.utils import generate_uuid

def _asdict(data):
    return {
        field: value.value if isinstance(value, Enum) else value
        for field, value in data
    }

class ItemPositionType(StringEnum):
    ROOT = 'ROOT'
    GRID = 'GRID'
    TABS = 'TABS'
    TAB = 'TAB'
    ROW = 'ROW'
    CHART = 'CHART'
    COLUMN = 'COLUMN'
    MARKDOWN = 'MARKDOWN'
    DIVIDER = 'DIVIDER'


class PositionType(StringEnum):
    LEFT = 'LEFT'
    RIGHT = 'RIGHT'
    BOTTOM = 'BOTTOM'

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
class ItemPosition(ParseMixin):
    ACCEPT_CHILD = True
    MAX_WIDTH = 12

    id: str = field(init=False, repr=False)
    type_: ItemPositionType = field(init=False, repr=False)
    children: List[str] = field(default_factory=set)
    parents: List[str] = field(default_factory=set)

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

        if kwargs.get('meta'):
            if hasattr(self, 'meta'):
                self.meta.__dict__.update(kwargs['meta'])
            else:
                self.meta = kwargs['meta']

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


class Position:
    def __init__(self, item:ItemPosition, position:PositionType = PositionType.BOTTOM):
        self._item = item
        self._position = position

    @property
    def item(self):
        return self._item

    @property
    def position(self):
        return self._position


class RootItemPosition(ItemPosition):
    def __init__(self, **kwargs):
        super().__init__(type_=ItemPositionType.ROOT, id='ROOT_ID', **kwargs)


class GridItemPosition(ItemPosition):
    def __init__(self, **kwargs):
        super().__init__(type_=ItemPositionType.GRID, id='GRID_ID', **kwargs)


class TabsItemPosition(ItemPosition):
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

class RowItemPosition(ItemPosition):
    def __init__(self, background: str = 'BACKGROUND_TRANSPARENT', **kwargs):
        self.meta = MetaItemPosition({
            'background': background
        })
        super().__init__(type_=ItemPositionType.ROW, **kwargs)

    @property
    def background(self):
        return self.meta.background

class RelocateMixin:
    def __init__(self, relocate:bool, **kwargs):
        self.relocate = relocate

        width = self.meta.width
        height =self.meta.height

        if not relocate and width > ItemPosition.MAX_WIDTH:
            raise NodePositionValidationError(f'Maximum width allowed is  {ItemPosition.MAX_WIDTH}')

        if width <= 0:
            raise NodePositionValidationError('Width must be greater than zero')

        if height <= 0:
            raise NodePositionValidationError('Height must be greater than zero')

        super().__init__(**kwargs)


class MarkdownItemPosition(RelocateMixin, ItemPosition):
    ACCEPT_CHILD = False

    def __init__(self, code:str='', height: int = 50, width: int = 4, relocate:bool = True, **kwargs):
        _meta = {
            'code': code,
            'height': height,
            'width': width
        }
        self.meta = MetaItemPosition(_meta)

        super().__init__(relocate=relocate, type_=ItemPositionType.MARKDOWN, **kwargs)

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


class ChartItemPosition(RelocateMixin, ItemPosition):
    ACCEPT_CHILD = False
    def __init__(self, chartId: int, sliceName: str, sliceNameOverride: str = None, height: int = 50, width: int = 4, uuid: str = None, relocate:bool = True, **kwargs):
        if not chartId:
            raise NodePositionValidationError('chartId argument cannot be null or empty')
        if not sliceName:
            raise NodePositionValidationError('sliceName argument cannot be null or empty')

        _meta = {
            'chartId': chartId,
            'sliceName': sliceName,
            'sliceNameOverride': sliceNameOverride,
            'height': height,
            'width': width
        }
        if uuid:
            _meta.update({'uuid':uuid})

        self.meta = MetaItemPosition(_meta)
        super().__init__(relocate=relocate, type_=ItemPositionType.CHART, **kwargs)

    @property
    def chart_id(self):
        return self.meta.chartId

    @property
    def slice_name(self):
        return self.meta.sliceName

    @property
    def width(self):
        return self.meta.width

    @property
    def height(self):
        return self.meta.height

