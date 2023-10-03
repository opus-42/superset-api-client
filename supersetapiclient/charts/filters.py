import json
from dataclasses import dataclass, field
from enum import Enum

from supersetapiclient.base.base import Object, default_string
from supersetapiclient.charts.types import FilterOperationType, FilterExpressionType

#https://github.com/apache/superset/blob/8553b06155249c3583cf0dcd22221ec06cbb833d/superset/utils/core.py#L137


@dataclass
class AdhocFilterClause(Object):
    comparator: str
    subject: str
    clause: str = default_string(default='WHERE')
    operator: FilterOperationType = field(default_factory=FilterOperationType.EQUAL)

    expressionType: FilterExpressionType = field(default_factory=FilterExpressionType.SIMPLE)

    isExtra: bool = field(default=False)
    isNew: bool = field(default=False)
