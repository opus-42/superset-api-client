import json
from dataclasses import dataclass
from typing import ClassVar

from supersetapiclient.base import Object, default_string
from supersetapiclient.dashboards.itemposition import TABItemPosition, MarkdownItemPosition
from supersetapiclient.dashboards.treenodeposisition import TreeNodePosition, ItemPositionType, NodePosition


@dataclass
class Metadataposition(Object):
    DASHBOARD_VERSION_KEY: ClassVar[str] = 'v2'

    def __post_init__(self):
        super().__post_init__()
        self._tree = TreeNodePosition()

    @property
    def tree(self):
        return self._tree

    def to_dict(self):
        return self.tree.to_dict()

    def to_json(self, columns=None):
        return json.dumps(self.to_dict())

    def add_tab(self, title: str, parent_id: str):
        parent = self.tree.find_by_id(parent_id)
        return parent.insert(TABItemPosition(text=title))

    def add_markdown(self, markdown: str, parent_id: str, height: int = 50, width: int = 4):
        parent = self.tree.find_by_id(parent_id)
        return parent.insert(MarkdownItemPosition(markdown, height, width))