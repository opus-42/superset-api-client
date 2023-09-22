from typing import List, Dict

from anytree import Node, RenderTree, search
import shortuuid
from typing_extensions import Self
from enum import Enum

class NodeValueType(Enum):
    ROOT = 'ROOT'
    GRID = 'GRID'
    TABS = 'TABS'
    TAB = 'TAB'
    ROW = 'ROW'
    CHART = 'CHART'
    COLUMN = 'COLUMN'
    MARKDOWN = 'MARKDOWN'

    def __str__(self):
        return str(self.value)

    def __eq__(self, other):
        if str(self.__class__) == str(other.__class__):
            return self.value == other.value
        return False


class NodePosition(Node):
    def __init__(self, id: str, _type: NodeValueType, parent: Self=None, children: Self=None):
        value = {
            "id": id,
            "type": str(_type),
            "children": [],
            "parents": []
        }

        self._value = value
        super().__init__(id, parent, children)

        if parent:
            parent.value['children'].append(id)
            self.value['parents'].append(parent.value['id'])

    @property
    def value(self):
        return self._value

    @property
    def id(self):
        return self.name

    @property
    def type_(self):
        return NodeValueType(self.value['type'])

    @classmethod
    def generate_uuid(cls, _type):
        return f"{_type}-{shortuuid.ShortUUID().random(length=10)}"
    #print(generate_uuid('TAB'))

    def insert(self, title: str, _type: NodeValueType, uuid: str = None) -> Self:
        func = {
            'GRID': None,
            'TAB': self.__insert_tab,
            'CHART': self.__insert_charts
        }

        if not func.get(str(_type)):
            raise KeyError(f'{_type} not found!')

        if uuid is None:
            uuid = self.generate_uuid(_type)

        return func[str(_type)](uuid, title, _type)

    def __insert_tab(self, uuid: str, title: str, _type: NodeValueType):
        parent = self

        # Verifica se o nó pai é do tipo TABS, se não,
        # Busca se exist um filho do tipo TABS.
        # Caso não encontre, crie um filho do tipo TABS
        if parent.type_ != NodeValueType.TABS:
            child_tabs_exists = False
            for child in parent.children:
                if child.type_ == NodeValueType.TABS:
                    parent = child
                    child_tabs_exists = True
            if not child_tabs_exists:
                parent = self.__insert_tabs(parent)

        node = NodePosition(uuid, _type, parent)
        value = { 
                "meta": {
                  "defaultText": "Tab title",
                  "placeholder": "Tab title",
                  "text": title
                }
              }
        node.value.update(value)
        return node
    
    def __insert_tabs(self, parent: Self):
        uuid = self.generate_uuid('TABS-')
        node = NodePosition(uuid, NodeValueType.TABS, parent)
        node.value.update({ "meta": {} })
        return node

    def __insert_charts(self):
        pass


class TreeNodePosition:
    def __init__(self, name: str, type_ : NodeValueType):
        self._root = NodePosition(name, type_)

    @property
    def root(self) -> NodePosition:
        return self._root

    # def insert(self, value: dict, parent_id: Optional[str] = None) -> NodePosition:
    #     if parent_id is None:
    #         node = self.root
    #     else:
    #         node = search.find(self._root, lambda node: node.name == parent_id)
    #     return NodePosition(value, parent=node)

    def find_by_id(self, id: str):
        return search.find(self._root, lambda node: node.name == id)

    def print(self):
        # print(RenderTree(self.root, style=AsciiStyle()).by_attr())
        for pre, fill, node in RenderTree(self.root ):
            print(f"{pre}{node.value}")

    def __to_json(self, node: NodePosition, values: Dict):
        for child_key in node.value.get("children", []):
            node_child = self.find_by_id(child_key)
            values[child_key] = node_child.value
            self.__to_json(node_child, values)

    def to_json(self):
        values = {}
        values[self.root.id] = self.root.value
        self.__to_json(self.root, values)
        return values

