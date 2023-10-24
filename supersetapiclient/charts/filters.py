import json
from dataclasses import dataclass, field

from supersetapiclient.base.base import Object, default_string
from supersetapiclient.charts.types import FilterOperatorType, FilterExpressionType
from supersetapiclient.typing import Optional


#https://github.com/apache/superset/blob/8553b06155249c3583cf0dcd22221ec06cbb833d/superset/utils/core.py#L137


@dataclass
class AdhocFilterClause(Object):
    subject: str
    comparator: Optional[str] = None
    clause: str = default_string(default='WHERE')
    operator: FilterOperatorType = FilterOperatorType.EQUALS
    operatorId: str = field(default=FilterOperatorType.EQUALS.name)
    expressionType: FilterExpressionType = FilterExpressionType.SIMPLE

    isExtra: bool = False
    isNew: bool = False

    def __post_init__(self):
        super().__post_init__()
        self.operatorId = str(self.operator.name)
