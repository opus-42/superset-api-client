from dataclasses import dataclass, field
from typing import List, Optional

from supersetapiclient.base.base import Object, default_string
from supersetapiclient.charts.types import FilterOperatorType
from supersetapiclient.typing import FilterValues


@dataclass
class QuerieExtra(Object):
    having: str = ''
    where: str = ''


@dataclass
class QueryFilterClause(Object):
    col: str
    val: Optional[FilterValues]
    op: FilterOperatorType = FilterOperatorType.EQUAL


@dataclass
class Querie(Object):
    filters: List[QueryFilterClause] = field(default_factory=list)
    extras: QuerieExtra = field(default_factory=QuerieExtra)
    columns: List[str] = field(default_factory=list)
    metrics: List[str] = field(default_factory=list)
    row_limit: int = 100
    series_limit: int = 0
    order_desc: bool = True

    def __post_init__(self):
        if not self.metrics:
            self.metrics = ['count']
