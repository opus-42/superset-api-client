import json
from dataclasses import dataclass

from supersetapiclient.base import Object, default_string
from supersetapiclient.dashboards.treenodeposisition import TreeNodePosition, NodeValueType, NodePosition


@dataclass
class Metadataposition(Object):
    DASHBOARD_VERSION_KEY: str = default_string("v2")

    def __post_init__(self):
        super().__post_init__()

        self._tree = TreeNodePosition('ROOT_ID', NodeValueType.ROOT)
        NodePosition('GRID_ID', NodeValueType.GRID, self._tree.root)

    @property
    def tree(self):
        return self._tree

    def to_json(self, columns=None):
        if columns is None:
            columns = self.field_names()
        data = self.tree.to_json()
        data.update(super().to_json(columns))
        return json.dumps(data)

    def add_tab(self, title: str, parent_: str):
        parent = self.tree.find_by_id(parent_)
        return parent.insert(title, NodeValueType.TAB)
