from dataclasses import dataclass, field
from typing import List

from supersetapiclient.base.base import Object, default_string
from supersetapiclient.charts.types import FilterOperationType


@dataclass
class QuerieExtra(Object):
    having: str = ''
    where: str = ''


@dataclass
class QueryFilterClause(Object):
    col: str
    val: str
    op: FilterOperationType = FilterOperationType.EQUAL


@dataclass
class Querie(Object):
    filters: List[QueryFilterClause] = field(default_factory=list)
    extras: QuerieExtra = field(default_factory=QuerieExtra)
    columns: List[str] = field(default_factory=list)
    metrics: List[str] = field(default_factory=list)
    row_limit: int = field(default=100)
    series_limit: int = field(default=0)
    order_desc: bool = field(default=True)
