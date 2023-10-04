import json
from dataclasses import dataclass

from supersetapiclient.base.base import Object
from supersetapiclient.charts.charts import Chart
from supersetapiclient.dashboards.itemposition import TabItemPosition, MarkdownItemPosition, ItemPosition, \
    ChartItemPosition
from supersetapiclient.dashboards.nodeposisition import MarkdownNodePosition, TabNodePosition, NodePosition, \
    ChartNodePosition
from supersetapiclient.dashboards.treenodeposisition import TreeNodePosition


@dataclass
class Metadataposition(Object):
    DASHBOARD_VERSION_KEY: str = 'v2'

    def __init__(self, tree:TreeNodePosition = None, **kwargs):
        self._tree = tree or TreeNodePosition()

    @property
    def tree(self):
        return self._tree

    def to_dict(self, columns=None):
        # data = super().to_dict(self.field_names())
        data = super().to_dict()
        data.update(self.tree.to_dict())
        return data

    # def to_json(self, columns=None):
    #     return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, data: dict):
        maindata = {}
        for k, v in data.items():
            if not isinstance(v, dict):
                maindata[k] = v
        obj = super().from_json(maindata)
        obj._tree = TreeNodePosition.from_dict(data)
        return obj

    def add_tab(self, title: str, parent: ItemPosition = None) -> TabNodePosition:
        if not parent:
            parent = self.tree.grid
        return self.tree.insert(TabItemPosition(text=title), parent)

    def add_markdown(self, markdown: str, parent: ItemPosition = None, height: int = 50, width: int = 4, relocate:bool = True) -> MarkdownNodePosition:
        if not parent:
            parent = self.tree.grid
        return self.tree.insert(MarkdownItemPosition(code=markdown, height=height, width=width, relocate=relocate), parent)

    def add(self, item: ItemPosition, parent: ItemPosition) -> NodePosition:
        return self.tree.insert(item, parent)

    def add_chart(self, chart:Chart, parent: ItemPosition = None, height: int = 50, width: int = 4, relocate:bool = True) -> ChartNodePosition:
        if not parent:
            parent = self.tree.grid
        return self.tree.insert(ChartItemPosition(chartId=chart.id,
                                                  sliceName=chart.slice_name,
                                                  sliceNameOverride=chart.slice_name_override,
                                                  height=height,
                                                  width=width,
                                                  relocate=relocate), parent)