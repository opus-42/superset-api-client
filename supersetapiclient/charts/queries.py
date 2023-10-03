from dataclasses import dataclass, field
from typing import List

from supersetapiclient.base.base import Object, default_string
from supersetapiclient.charts.types import FilterOperationType


@dataclass
class QuerieExtra(Object):
    having: str = ''
    where: str = ''

    def to_dict(self):
        return super().to_dict(columns=None)


@dataclass
class QueryFilterClause(Object):
    col: str
    val: str
    op: FilterOperationType = field(default_factory=FilterOperationType.EQUAL)

@dataclass
class Querie(Object):
    filters: List[QueryFilterClause] = field(default_factory=list)
    extras: QuerieExtra = field(default_factory=QuerieExtra)
    columns: List[str] = field(default_factory=list)
    metrics: List[str] = field(default_factory=list)
    row_limit: int = field(default=100)
    series_limit: int = field(default=0)
    order_desc: bool = field(default=True)

    def to_dict(self, columns=None):
        data = super().to_dict(columns)

        data['extras'] = self.extras.to_dict()

        filters = []
        for query_filter in self.filters:
            filters.append(QueryFilterClause.to_dict(query_filter))
        data['filters'] = filters

        return data

    def to_json(self, columns=None):
        return super().to_json(columns)

    @classmethod
    def from_json(cls, data: dict):
        obj = super().from_json(data)

        obj.extras = QuerieExtra.from_json(data['extras'])

        filters = []
        for query_filter in data['filters']:
            filters.append(QueryFilterClause.from_json(query_filter))
        obj.filters = filters

        return obj