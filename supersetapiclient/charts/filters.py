import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from supersetapiclient.base.base import Object, default_string
from supersetapiclient.charts.types import FilterOperatorType, FilterExpressionType

#https://github.com/apache/superset/blob/8553b06155249c3583cf0dcd22221ec06cbb833d/superset/utils/core.py#L137


@dataclass
class AdhocFilterClause(Object):
    subject: str
    comparator: Optional[str] = None
    clause: str = default_string(default='WHERE')
    operator: FilterOperatorType = FilterOperatorType.EQUAL
    operatorId: str = field(default=FilterOperatorType.EQUAL.name)
    expressionType: FilterExpressionType = FilterExpressionType.SIMPLE

    isExtra: bool = field(default=False)
    isNew: bool = field(default=False)

    def __post_init__(self):
        self.operatorId = str(self.operator)
