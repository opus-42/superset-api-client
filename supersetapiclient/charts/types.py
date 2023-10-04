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

class NumberFormatType(StringEnum):
    ORIGINAL_VALUE = '~g'
    SMART_NUMBER = 'SMART_NUMBER' #Adaptive formatting
    SMART_NUMBER_SIGNED = 'SMART_NUMBER_SIGNED'
    OVER_MAX_HIDDEN = 'OVER_MAX_HIDDEN'

    DOLLAR = '$,.2f'
    DOLLAR_SIGNED = '+$,.2f'
    DOLLAR_ROUND = '$,d'
    DOLLAR_ROUND_SIGNED = '+$,d'

    FLOAT_1_POINT = ',.1f'
    FLOAT_2_POINT = ',.2f'
    FLOAT_3_POINT = ',.3f'
    FLOAT = FLOAT_2_POINT;

    FLOAT_SIGNED_1_POINT = '+,.1f'
    FLOAT_SIGNED_2_POINT = '+,.2f'
    FLOAT_SIGNED_3_POINT = '+,.3f'
    FLOAT_SIGNED = FLOAT_SIGNED_2_POINT;

    INTEGER = ',d'
    INTEGER_SIGNED = '+,d'

    PERCENT_1_POINT = ',.1%'
    PERCENT_2_POINT = ',.2%'
    PERCENT_3_POINT = ',.3%'

    PERCENT_SIGNED_1_POINT = '+,.1%'
    PERCENT_SIGNED_2_POINT = '+,.2%'
    PERCENT_SIGNED_3_POINT = '+,.3%'
    PERCENT_SIGNED = PERCENT_SIGNED_2_POINT;

    SI_1_DIGIT = '.1s'
    SI_2_DIGIT = '.2s'
    SI_3_DIGIT = '.3s'
    SI = SI_3_DIGIT;

    DURATION = 'DURATION' #Duration in ms (66000 => 1m 6s)
    DURATION_SUB = 'DURATION_SUB' #Duration in ms (100.40008 => 100ms 400µs 80ns)


class DateFormatType(StringEnum):
    SMART_DATE = 'smart_date'
    DATABASE_DATETIME = '%Y-%m-%d %H:%M:%S'
    DATABASE_DATETIME_REVERSE = '%d-%m-%Y %H:%M:%S'
    US_DATE = '%m/%d/%Y'
    INTERNATIONAL_DATE = '%d/%m/%Y'
    DATABASE_DATE = '%Y-%m-%d'
    TIME = '%H:%M:%S'


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


class CurrencyCodeType(StringEnum):
    AED = 'AED'
    AFN = 'AFN'
    ALL = 'ALL'
    AMD = 'AMD'
    ANG = 'ANG'
    AOA = 'AOA'
    ARS = 'ARS'
    AUD = 'AUD'
    AWG = 'AWG'
    AZN = 'AZN'
    BAM = 'BAM'
    BBD = 'BBD'
    BDT = 'BDT'
    BGN = 'BGN'
    BHD = 'BHD'
    BIF = 'BIF'
    BMD = 'BMD'
    BND = 'BND'
    BOB = 'BOB'
    BRL = 'BRL'
    BSD = 'BSD'
    BTN = 'BTN'
    BWP = 'BWP'
    BYN = 'BYN'
    BZD = 'BZD'
    CAD = 'CAD'
    CDF = 'CDF'
    CHF = 'CHF'
    CLP = 'CLP'
    CNY = 'CNY'
    COP = 'COP'
    CRC = 'CRC'
    CUC = 'CUC'
    CUP = 'CUP'
    CVE = 'CVE'
    CZK = 'CZK'
    DJF = 'DJF'
    DKK = 'DKK'
    DOP = 'DOP'
    DZD = 'DZD'
    EGP = 'EGP'
    ERN = 'ERN'
    ETB = 'ETB'
    EUR = 'EUR'
    FJD = 'FJD'
    FKP = 'FKP'
    GBP = 'GBP'
    GEL = 'GEL'
    GHS = 'GHS'
    GIP = 'GIP'
    GMD = 'GMD'
    GNF = 'GNF'
    GTQ = 'GTQ'
    GYD = 'GYD'
    HKD = 'HKD'
    HNL = 'HNL'
    HRK = 'HRK'
    HTG = 'HTG'
    HUF = 'HUF'
    IDR = 'IDR'
    ILS = 'ILS'
    INR = 'INR'
    IQD = 'IQD'
    IRR = 'IRR'
    ISK = 'ISK'
    JMD = 'JMD'
    JOD = 'JOD'
    JPY = 'JPY'
    KES = 'KES'
    KGS = 'KGS'
    KHR = 'KHR'
    KMF = 'KMF'
    KPW = 'KPW'
    KRW = 'KRW'
    KWD = 'KWD'
    KYD = 'KYD'
    KZT = 'KZT'
    LAK = 'LAK'
    LBP = 'LBP'
    LKR = 'LKR'
    LRD = 'LRD'
    LSL = 'LSL'
    LYD = 'LYD'
    MAD = 'MAD'
    MDL = 'MDL'
    MGA = 'MGA'
    MKD = 'MKD'
    MMK = 'MMK'
    MNT = 'MNT'
    MOP = 'MOP'
    MRU = 'MRU'
    MUR = 'MUR'
    MVR = 'MVR'
    MWK = 'MWK'
    MXN = 'MXN'
    MYR = 'MYR'
    MZN = 'MZN'
    NAD = 'NAD'
    NGN = 'NGN'
    NIO = 'NIO'
    NOK = 'NOK'
    NPR = 'NPR'
    NZD = 'NZD'
    OMR = 'OMR'
    PAB = 'PAB'
    PEN = 'PEN'
    PGK = 'PGK'
    PHP = 'PHP'
    PKR = 'PKR'
    PLN = 'PLN'
    PYG = 'PYG'
    QAR = 'QAR'
    RON = 'RON'
    RSD = 'RSD'
    RUB = 'RUB'
    RWF = 'RWF'
    SAR = 'SAR'
    SBD = 'SBD'
    SCR = 'SCR'
    SDG = 'SDG'
    SEK = 'SEK'
    SGD = 'SGD'
    SHP = 'SHP'
    SLL = 'SLL'
    SOS = 'SOS'
    SRD = 'SRD'
    SSP = 'SSP'
    STN = 'STN'
    SVC = 'SVC'
    SYP = 'SYP'
    SZL = 'SZL'
    THB = 'THB'
    TJS = 'TJS'
    TMT = 'TMT'
    TND = 'TND'
    TOP = 'TOP'
    TRY = 'TRY'
    TTD = 'TTD'
    TWD = 'TWD'
    TZS = 'TZS'
    UAH = 'UAH'
    UGX = 'UGX'
    USD = 'USD'
    UYU = 'UYU'
    UZS = 'UZS'
    VES = 'VES'
    VND = 'VND'
    VUV = 'VUV'
    WST = 'WST'
    XAF = 'XAF'
    XCD = 'XCD'
    XOF = 'XOF'
    XPF = 'XPF'
    YER = 'YER'
    ZAR = 'ZAR'
    ZMW = 'ZMW'
    ZWL = 'ZWL'


class CurrentPositionType(StringEnum):
    PREFIX = 'prefix'
    SUFFIX = 'suffix'