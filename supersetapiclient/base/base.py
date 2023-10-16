"""Base classes."""
import dataclasses
import logging
from abc import abstractmethod
from enum import Enum
from typing_extensions import Self
from supersetapiclient.base.parse import ParseMixin
from supersetapiclient.client import QueryStringFilter
from supersetapiclient.typing import NotToJson

logger = logging.getLogger(__name__)

try:
    from functools import cached_property
except ImportError:  # pragma: no cover
    # Python<3.8
    from cached_property import cached_property

import json
import os.path
from pathlib import Path
from typing import List, Union, Dict, get_args, get_origin, Any, Literal

import yaml
from requests import HTTPError

from supersetapiclient.exceptions import BadRequestError, ComplexBadRequestError, MultipleFound, NotFound, \
    LoadJsonError, ValidationError

class ObjectDecoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Enum):
            return str(obj.value)  # Converte o Enum para seu valor (string)
        return super(self).default(obj)


def json_field(**kwargs):
    if not kwargs.get('default'):
        kwargs['default']=None

    return dataclasses.field(repr=False, **kwargs)

def default_string(**kwargs):
    if not kwargs.get('default'):
        kwargs['default']=''

    return dataclasses.field(repr=False, **kwargs)

def default_bool(**kwargs):
    if not kwargs.get('default'):
        kwargs['default']=False
    return dataclasses.field(repr=False)

def raise_for_status(response):
    try:
        response.raise_for_status()
    except HTTPError as e:
        # Attempt to propagate the server error message
        try:
            error_msg = response.json()["message"]
        except Exception:
            try:
                errors = response.json()["errors"]
            except Exception:
                raise e
            raise ComplexBadRequestError(*e.args, request=e.request, response=e.response, errors=errors) from None
        raise BadRequestError(*e.args, request=e.request, response=e.response, message=error_msg) from None


class Object(ParseMixin):
    _factory = None
    JSON_FIELDS = []

    _extra_fields: Dict = {}

    def __post_init__(self):
        for f in self.JSON_FIELDS:
            value = getattr(self, f) or "{}"
            if isinstance(value, str):
                setattr(self, f, json.loads(value))

    @abstractmethod
    def validate(self, data: dict):
        pass


    @property
    def extra_fields(self):
        return self._extra_fields

    @classmethod
    def fields(cls) -> set:
        """Get field names."""
        _fields = set()

        for n, f in cls.__dataclass_fields__.items():
            if isinstance(f, dataclasses.Field):
                _fields.add(f)

        _fields.update(dataclasses.fields(cls))

        return _fields

    @classmethod
    def get_field(cls, name):
        for f in cls.fields():
            if f.name == name:
                return f

    @classmethod
    def field_names(cls) -> list:
        """Get field names."""
        fields = []
        for f in cls.fields():
            if not isinstance(f.default, Object):
                fields.append(f.name)
        return fields

    @classmethod
    def required_fields(cls, data) -> dict:
        rdata = {}
        for f in cls.fields():
            if f.default is dataclasses.MISSING and not isinstance(f.default, Object):
                rdata[f.name] = data.get(f.name)
        return rdata

    @classmethod
    def __get_extra_fields(cls, data) -> dict:
        if not data:
            return {}

        field_names = set(cls.field_names())

        data_keys = set(data.keys())
        extra_fields_keys = data_keys - field_names
        extra_fields = {}
        for field_name in extra_fields_keys:
            extra_fields[field_name] = data.pop(field_name)

        return extra_fields

    @classmethod
    def _issubclass_object(cls, type_):
        try:
            if issubclass(type_, Object):
                return True
        except:
            pass
        return False

    @classmethod
    def _subclass_object(cls, field_name:str):
        field = cls.get_field(field_name)
        ObjectClass = field.type
        logger.debug(f'field_name: {field_name}; field.type: {field.type}')
        type_ = None
        while get_origin(ObjectClass):
            if get_args(ObjectClass):
                if len(get_args(ObjectClass)) == 2:
                    type_, ObjectClass = get_args(ObjectClass)
                    if 'NoneType' in str(ObjectClass):
                        if get_args(type_) and len(get_args(type_)) > 1:
                            type_, ObjectClass = get_args(type_)
                            logger.debug(f'while get_origin(ObjectClass) > if get_args(ObjectClass) > if len(get_args(ObjectClass)) == 2 > if "NoneType" in str(ObjectClass)')
                            logger.debug(f'type_: {type_}, ObjectClass: {ObjectClass}')
                        else:
                            ObjectClass = get_args(type_) or None
                            logger.debug(f'while get_origin(ObjectClass) > if get_args(ObjectClass) > if len(get_args(ObjectClass)) == 2 > else if "NoneType" in str(ObjectClass)')
                            logger.debug(f'ObjectClass: {ObjectClass}')
                else:
                    if get_origin(ObjectClass) is Literal:
                        ObjectClass = None
                        logger.debug(f'while get_origin(ObjectClass) > if get_args(ObjectClass) > else if len(get_args(ObjectClass)) == 2 > if get_origin(ObjectClass) is Literal')
                    else:
                        logger.debug(f'while get_origin(ObjectClass) > if get_args(ObjectClass) > else if len(get_args(ObjectClass)) == 2 > else if get_origin(ObjectClass) is Literal')
                        ObjectClass = get_args(ObjectClass)[-1]
                    logger.debug(f'ObjectClass: {ObjectClass}')
            else:
                break

        if 'NoneType' in str(ObjectClass):
            ObjectClass = None
        if 'NoneType' in str(type_):
            type_ = None
        if cls._issubclass_object(ObjectClass):
            return type_, ObjectClass
        elif cls._issubclass_object(type_):
            return ObjectClass, type_
        return type_, None

    @classmethod
    def from_json(cls, data: dict) -> Self:
        extra_fields = cls.__get_extra_fields(data)
        field_name = None
        data_value = None
        try:
            obj = cls(**data)

            for field_name in cls.JSON_FIELDS:
                data_value = data.get(field_name)
                if isinstance(data_value, str):
                    field = cls.get_field(field_name)
                    if get_origin(field.type) is Union:
                        ObjectClass = get_args(field.type)[0]
                    else:
                        ObjectClass = field.type

                    if ObjectClass is Dict:
                        value = json.loads(data_value)
                    else:
                        value = ObjectClass.from_json(json.loads(data[field_name]))
                    setattr(obj, field_name, value)

            for field_name, data_value in data.items():
                logger.debug(f'field_name: {field_name}; data_value: {data_value}')
                if field_name in cls.JSON_FIELDS:
                    continue
                if isinstance(data_value, dict):
                    type_, ObjectClass = cls._subclass_object(field_name)
                    value = None
                    if type_ and ObjectClass:
                        value = {}
                        for k, field_value in data_value.items():
                            value[k] = ObjectClass.from_json(field_value)
                    elif ObjectClass:
                        value = ObjectClass.from_json(data_value)
                    else:
                        value = data_value
                    setattr(obj, field_name, value)
                elif isinstance(data_value, list):
                    type_, ObjectClass = cls._subclass_object(field_name)
                    if ObjectClass is None:
                        value = data_value
                    else:
                        value = []
                        for field_data_value in data_value:
                            value.append(ObjectClass.from_json(field_data_value))
                    setattr(obj, field_name, value)
                else:
                    setattr(obj, field_name, data_value)

            obj._extra_fields = extra_fields
        except Exception as err:
            msg = f"""{err}
                cls={cls}
                field_name={field_name}
                data_value={data_value}
                data={data}
                extra_fields={extra_fields}
            """
            logger.exception(msg)
            raise LoadJsonError(err)
        return obj

    def __remove_fields_Optional_or_NotToJson(self, data:dict):
        def remove(data:dict, field: dataclasses.Field):
            try:
                data.pop(field.name)
            except KeyError:
                pass

        for field in self.fields():
            try:
                if get_origin(field.type) is Union and 'typing.Optional' in str(field.type):
                    if field.default is dataclasses.MISSING:
                        remove(data, field)
                    elif field.default == data[field.name]:
                        remove(data, field)
                    else:
                        logger.warning('untreated else condition')
                if get_origin(field.type) is NotToJson:
                    remove(data, field)
            except AttributeError:
                pass
        return data

    def __remove_field_starting_shyphen(self, data):
        fields = list(data.keys())
        for field in fields:
            if fields[0] == "_":
                data.pop(field)

    def to_dict(self, columns=[]) -> dict:
        columns_names = set(columns or [])
        columns_names.update(self.field_names())
        data = {}
        for c in columns_names:
            if not hasattr(self, c):
                # Column that is not implemented yet
                continue
            value = getattr(self, c)
            if isinstance(value, Enum):
                value = str(value)
            if value and isinstance(value, Object):
                value = value.to_dict(columns)
            elif value and isinstance(value, list):
                values_data = []
                for field_value in value:
                    if isinstance(field_value, Object):
                        values_data.append(field_value.to_dict(columns))
                    else:
                        values_data.append(field_value)
                    value = values_data
            if value and isinstance(value, dict):
                ProbableObjectClass1, ProbableObjectClass2 = self._subclass_object(c)
                if ProbableObjectClass1 and ProbableObjectClass2:
                    _value = {}
                    if self._issubclass_object(ProbableObjectClass1):
                        for ojb, value_ in value.items():
                            _value[obj.to_dict()] = value_
                    elif self._issubclass_object(ProbableObjectClass2):
                        for k, obj in value.items():
                            _value[k] =  obj.to_dict()
                    else:
                        msg = f"""self={self}
                            field_name={c}
                            data_value={value}
                            data={data}
                            ProbableObjectClass1={ProbableObjectClass1}
                            ProbableObjectClass2={ProbableObjectClass2}
                        """
                        logger.error(msg)
                        raise ValidationError('Unable to determine ObjectClass')
                    value = _value
            data[c] = value
            logger.info(f'return data {data}')
        return data

    def to_json(self, columns=[]) -> dict:
        data = self.to_dict(columns)
        self.validate(data)

        for field in self.JSON_FIELDS:
            obj = getattr(self, field)
            if isinstance(obj, Object):
                data[field] = json.dumps(obj.to_json(), cls=ObjectDecoder)
            elif isinstance(obj, dict):
                data[field] = json.dumps(data[field], cls=ObjectDecoder)

        self.__remove_field_starting_shyphen(data)

        self.__remove_fields_Optional_or_NotToJson(data)

        if data.get('extra_fields'):
            data.pop('extra_fields')
        logger.info(f'return data {data}')
        return data

    @property
    def base_url(self) -> str:
        return self._factory.client.join_urls(self._factory.base_url, self.id)

    def export(self, path: Union[Path, str]) -> None:
        """Export object to path"""
        self._factory.export(ids=[self.id], path=path)

    def fetch(self) -> None:
        """Fetch additional object information."""
        field_names = self.field_names()

        client = self._factory.client
        response = client.get(self.base_url)
        o = response.json().get("result")
        for k, v in o.items():
            if k in field_names:
                if k in self.JSON_FIELDS:
                    setattr(self, k, json.loads(v or "{}"))
                else:
                    setattr(self, k, v)

    def save(self) -> None:
        """Save object information."""
        o = self.to_json(columns=self._factory.edit_columns)
        logger.info(f'payload: {o}')

        response = self._factory.client.put(self.base_url, json=o)
        raise_for_status(response)
        logger.info(f'response: {response.json()}')

    def delete(self) -> bool:
        return self._factory.delete(id=self.id)

    def get_request_response(self):
        jdict = self._request_response.json()
        for field_name in self.JSON_FIELDS:
            jdict['result'][field_name] = json.loads(jdict['result'][field_name])
        return jdict

class ObjectFactories:
    endpoint = ""
    base_object: Object = None

    _INFO_QUERY = {"keys": ["add_columns", "edit_columns"]}


    def __init__(self, client):
        """Create a new Dashboards endpoint.

        Args:
            client (client): superset client
        """
        self.client = client

    @abstractmethod
    def get_base_object(self, data):
        logger.error(f'Abstract Method "get_base_object" not implemented, self: {self}')
        raise NotImplemented()

    @cached_property
    def _infos(self):
        # Get infos
        response = self.client.get(self.info_url, params={"q": json.dumps(self._INFO_QUERY)})
        raise_for_status(response)
        return response.json()

    @property
    def add_columns(self):
        return [e.get("name") for e in self._infos.get("add_columns", [])]

    @property
    def edit_columns(self):
        return [e.get("name") for e in self._infos.get("edit_columns", [])]

    @property
    def base_url(self):
        """Base url for these objects."""
        url = self.client.join_urls(self.client.base_url, self.endpoint)
        logger.info(f'url: {url}')
        return url

    @property
    def info_url(self):
        return self.client.join_urls(self.base_url, "_info")

    @property
    def import_url(self):
        return self.client.join_urls(self.base_url, "import/")

    @property
    def export_url(self):
        return self.client.join_urls(self.base_url, "export/")

    def get(self, id: str):
        """Get an object by id."""
        url = self.client.join_urls(self.base_url, id)
        logger.info(f'url: {url}')

        response = self.client.get(url)
        raise_for_status(response)

        result = response.json()
        logger.info(f'response: {result}')

        data_result = result['result']
        result["id"] = id
        BaseClass = self.get_base_object(data_result)

        object = BaseClass.from_json(data_result)
        object._request_response = response
        object._factory = self

        return object

    def find(self, filter:QueryStringFilter, columns:List[str]=[], page_size: int = 100, page: int = 0):
        """Find and get objects from api."""

        response = self.client.find(self.base_url, filter, columns, page_size, page)

        objects = []
        for data in response.get("result"):
            o = self.get_base_object(data).from_json(data)
            o._factory = self
            objects.append(o)

        return objects

    def count(self):
        """Count objects."""
        response = self.client.get(self.base_url)
        raise_for_status(response)
        return response.json()["count"]

    def find_one(self, filter:QueryStringFilter, columns:List[str]=[]):
        """Find only object or raise an Exception."""
        objects = self.find(filter, columns)
        if len(objects) == 0:
            raise NotFound(f"No {self.get_base_object().__name__} found")
        if len(objects) > 1:
            raise MultipleFound(f"Multiple {self.get_base_object().__name__} found")
        return objects[0]

    def add(self, obj) -> int:
        """Create an object on remote."""

        o = obj.to_json(columns=self.add_columns)
        logger.info(f'payload: {o}')

        response = self.client.post(self.base_url, json=o)
        raise_for_status(response)
        result = response.json()
        logger.info(f'response: {result}')

        obj.id = result.get("id")
        obj._factory = self
        return obj.id

    def export(self, ids: List[int], path: Union[Path, str]) -> None:
        """Export object into an importable file"""
        ids_array = ",".join([str(i) for i in ids])
        response = self.client.get(self.export_url, params={"q": f"[{ids_array}]"})

        raise_for_status(response)

        content_type = response.headers["content-type"].strip()
        if content_type.startswith("application/text"):  # pragma: no cover
            # Superset 1.x
            data = yaml.load(response.text, Loader=yaml.FullLoader)
            with open(path, "w", encoding="utf-8") as f:
                yaml.dump(data, f, default_flow_style=False)
            return
        if content_type.startswith("application/json"):  # pragma: no cover
            # Superset 1.x
            data = response.json()
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            return
        if content_type.startswith("application/zip"):
            data = response.content
            with open(path, "wb") as f:
                f.write(data)
            return
        raise ValueError(f"Unknown content type {content_type}")

    def delete(self, id: int) -> bool:
        """Delete a object on remote."""
        url = self.client.join_urls(self.base_url, id)
        logger.info(f'url: {url}')
        response = self.client.delete(url)
        raise_for_status(response)
        logger.info(f'response: {response.json()}')
        return response.json().get("message") == "OK"

    def import_file(self, file_path, overwrite=False, passwords=None) -> dict:
        """Import a file on remote.

        :param file_path: Path to a JSON or ZIP file containing the import data
        :param overwrite: If True, overwrite existing remote entities
        :param passwords: JSON map of passwords for each featured database in
        the file. If the ZIP includes a database config in the path
        databases/MyDatabase.yaml, the password should be provided in the
        following format: {"MyDatabase": "my_password"}
        """
        data = {"overwrite": json.dumps(overwrite)}
        passwords = {f"databases/{db}.yaml": pwd for db, pwd in (passwords or {}).items()}
        file_name = os.path.split(file_path)[-1]
        file_ext = os.path.splitext(file_name)[-1].lstrip(".").lower()
        with open(file_path, "rb") as f:
            files = {
                "formData": (file_name, f, f"application/{file_ext}"),
                "passwords": (None, json.dumps(passwords), None),
            }
            response = self.client.post(
                self.import_url,
                files=files,
                data=data,
                headers={"Accept": "application/json"},
            )
        raise_for_status(response)

        # If import is successful, the following is returned: {'message': 'OK'}
        return response.json().get("message") == "OK"
