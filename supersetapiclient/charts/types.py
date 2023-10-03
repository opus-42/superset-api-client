from supersetapiclient.base.enum_str import StringEnum


class ChartType(StringEnum):
    PIE = 'pie'


#https://github.com/apache/superset/blob/8553b06155249c3583cf0dcd22221ec06cbb833d/superset-frontend/plugins/plugin-chart-echarts/src/types.ts
class LegendType(StringEnum):
    PLAIN ='plain'
    SCROLL = 'scroll'


class LegendOrientationType(StringEnum):
    BOTTOM = 'bottom'
    TOP = 'top'
    LEFT = 'lef'
    RIGHT = 'right'


D3_FORMAT_OPTIONS = [
  ['SMART_NUMBER', 'Adaptive formatting'],
  ['~g', 'Original value'],
  [',d', ',d (12345.432 => 12,345)'],
  ['.1s', '.1s (12345.432 => 10k)'],
  ['.3s', '.3s (12345.432 => 12.3k)'],
  [',.1%', ',.1% (12345.432 => 1,234,543.2%)'],
  ['.3%', '.3% (12345.432 => 1234543.200%)'],
  ['.4r', '.4r (12345.432 => 12350)'],
  [',.3f', ',.3f (12345.432 => 12,345.432)'],
  ['+,', '+, (12345.432 => +12,345.432)'],
  ['$,.2f', '$,.2f (12345.432 => $12,345.43)'],
  ['DURATION', 'Duration in ms (66000 => 1m 6s)'],
  ['DURATION_SUB', 'Duration in ms (100.40008 => 100ms 400µs 80ns)'],
]

D3_TIME_FORMAT_OPTIONS = [
  ['smart_date', 'Adaptive formatting'],
  ['%d/%m/%Y', '%d/%m/%Y | 14/01/2019'],
  ['%m/%d/%Y', '%m/%d/%Y | 01/14/2019'],
  ['%Y-%m-%d', '%Y-%m-%d | 2019-01-14'],
  ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M:%S | 2019-01-14 01:32:10'],
  ['%d-%m-%Y %H:%M:%S', '%Y-%m-%d %H:%M:%S | 14-01-2019 01:32:10'],
  ['%H:%M:%S', '%H:%M:%S | 01:32:10'],
]

class LabelType(StringEnum):
    CATEGORY_NAME ='key'
    VALUE = 'value'
    PERCENTAGE = 'percent'
    CATEGORY_AND_VALUE = 'key_value'
    CATEGORY_AND_PERCENTAGE = 'key_percent'
    CATEGORI_VALUE_AND_PERCENTAG = 'key_value_percent'


class FilterOperationType(StringEnum):
    EQUAL = '=='
    NOT_EQUAL = '!='
    LESS_THAN = '<'
    LESS_THAN_OR_EQUAL = '<='
    GREATER_THAN = '>'
    GREATER_THAN_OR_EQUAL = '>='
    IN = 'IN'
    NOT_IN = 'NOT IN'
    LIKE = 'LIKE'
    ILIKE = 'ILIKE'
    IS_NOT_NULL = 'IS NOT NULL'
    IS_NULL = 'IS NULL'
    LATEST_PARTITION = 'LATEST PARTITION'
    IS_TRUE = '=='
    IS_FALSE = '==',
    TEMPORAL_RANGE = 'TEMPORAL_RANGE'

class FilterExpressionType(StringEnum):
    SIMPLE = 'SIMPLE'
    CUSTOM_CQL = 'SQL'

class FilterClausesType(StringEnum):
  HAVING = 'HAVING'
  WHERE = 'WHERE'


class DatasourceType(StringEnum):
    SLTABLE = "sl_table"
    TABLE = "table"
    DATASET = "dataset"
    QUERY = "query"
    SAVEDQUERY = "saved_query"
    VIEW = "view"