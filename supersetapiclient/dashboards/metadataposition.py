import json
from dataclasses import dataclass
from typing import ClassVar

from supersetapiclient.base import Object, default_string
from supersetapiclient.dashboards.itemposition import TabItemPosition, MarkdownItemPosition, ItemPosition, \
    ItemPositionType, ItemPositionParse
from supersetapiclient.dashboards.nodeposisition import MarkdownNodePosition, TabNodePosition, NodePosition
from supersetapiclient.dashboards.treenodeposisition import TreeNodePosition


@dataclass
class Metadataposition(Object):
    DASHBOARD_VERSION_KEY: str = 'v2'

    def __init__(self, tree:TreeNodePosition = None, **kwargs):
        self._tree = tree or TreeNodePosition()

    @property
    def tree(self):
        return self._tree

    def to_dict(self):
        data = super().to_dict(self.field_names())
        data.update(self.tree.to_dict())
        return data

    def to_json(self, columns=None):
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, data: dict):
        maindata = {}
        for k, v in data.items():
            if not isinstance(v, dict):
                maindata[k] = v
        obj = super().from_json(maindata)
        obj._tree = TreeNodePosition.from_dict(data)
        return obj

    def add_tab(self, title: str, parent_id: str) -> TabNodePosition:
        parent = self.tree.find_by_id(parent_id)
        return self.tree.insert(TabItemPosition(text=title), parent)

    def add_markdown(self, markdown: str, parent_id: str, height: int = 50, width: int = 4) -> MarkdownNodePosition:
        parent = self.tree.find_by_id(parent_id)
        return self.tree.insert(MarkdownItemPosition(code=markdown, height=height, width=width), parent)

    def add(self, item: ItemPosition, parent: ItemPosition) -> NodePosition:
        return self.tree.insert(item, parent)