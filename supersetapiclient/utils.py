import re
import unicodedata

import inspect
import logging
from typing import Union, get_origin

import shortuuid

_logger = logging.getLogger(__name__)

def normalize_str(text: str):
    return re.sub('[^A-Za-z0-9_]+', '', unicodedata.normalize('NFKD', text.replace(' ', '_').lower()))

def generate_uuid(_type):
    return f"{_type}-{shortuuid.ShortUUID().random(length=10)}"

