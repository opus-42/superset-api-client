import re
import unicodedata

import inspect
from typing import Union, get_origin

import shortuuid

def normalize_str(text: str):
    return re.sub('[^A-Za-z0-9_]+', '', unicodedata.normalize('NFKD', text.replace(' ', '_').lower()))

def generate_uuid(_type):
    return f"{_type}-{shortuuid.ShortUUID().random(length=10)}"

