from typing import List, Dict

from anytree import Node, RenderTree, search

from typing_extensions import Self

from supersetapiclient.dashboards.itemposition import ItemPositionType, GenericItemPosition, _RootItemPosition, \
    _GridItemPosition, _TABSItemPosition, TABItemPosition, MarkdownItemPosition, _ROWItemPosition
from supersetapiclient.exceptions import AcceptChildError
from supersetapiclient.utils import generate_uuid

NODEPOSITION_PARSE = {
    'GRID': _GridItemPosition,
    'TABS': _TABSItemPosition,
    'TAB': TABItemPosition,
    'ROW': _ROWItemPosition,
    'MARKDOWN': MarkdownItemPosition
}

class NodePosition(Node):
    def __init__(self, item: GenericItemPosition, parent: Self=None):
        if parent and not parent.item.ACCEPT_CHILD:
            raise AcceptChildError()

        self._item = item
        super().__init__(item.id, parent)

        if parent:
            parent.item.children.append(item.id)
            self.item.parents.append(parent.item.id)

    @property
    def item(self):
        return self._item

    @property
    def id(self):
        return self._item.id

    @property
    def type_(self):
        return ItemPositionType(self.item.type_)


    def insert(self, item: GenericItemPosition) -> Self:
        func = {
            'TAB': self.insert_tab,
            'MARKDOWN': self.insert_markdown,
        }

        if not func.get(str(item.type_)):
            raise KeyError(f'{item.type_} not found!')

        return func[str(item.type_)](item)

    def insert_tab(self, item: TABItemPosition):
        parent = self.__ger_or_insert_parent(_TABSItemPosition(), self)
        return NodePosition(item, parent)

    def insert_markdown(self, item: MarkdownItemPosition):
        parent = self.__ger_or_insert_parent(_ROWItemPosition(), self)
        return NodePosition(item, parent)

    def __ger_or_insert_parent(self, item: GenericItemPosition, parent: Self):
        # Verifica se o nó pai é do tipo TABS, se não,
        # Busca se exist um filho do tipo TABS.
        # Caso não encontre, crie um filho do tipo TABS
        if parent.type_ != item.type_:
            child_tabs_exists = False
            for child in parent.children:
                if child.type_ == item.type_:
                    parent = child
                    child_tabs_exists = True
            if not child_tabs_exists:
                return NodePosition(item, parent)
        return parent


class NodePositionMarkdown(NodePosition):
    #Não há espaço suficiente para esse componente. Tente diminuir sua largura ou aumentar a largura do destino.
    def insert_left(self):
        pass
    def insert_right(self):
        pass

class TreeNodePosition:
    def __init__(self):
        self._root = NodePosition(_RootItemPosition())
        NodePosition(_GridItemPosition(), self._root)

    @property
    def root(self) -> NodePosition:
        return self._root

    def insert(self, item: GenericItemPosition, parent: Self=None) -> NodePosition:
        return NodePosition(item, parent)

    def find_by_id(self, id: str):
        return search.find(self._root, lambda node: node.name == id)

    def print(self):
        # print(RenderTree(self.root, style=AsciiStyle()).by_attr())
        for pre, fill, node in RenderTree(self.root):
            print(f"{pre}{node.item}")

    def __to_dict(self, node: NodePosition, values: Dict):
        for child_id in node.item.children:
            node_child = self.find_by_id(child_id)
            values[child_id] = node_child.item.to_dict()
            self.__to_dict(node_child, values)

    def to_dict(self):
        values = {}
        values[self.root.id] = self.root.item.to_dict()
        self.__to_dict(self.root, values)
        return values

    @classmethod
    def __generate_tree(cls, position_id:str, data:dict, tree: Self):
        parent_node = tree.find_by_id(position_id)
        if position_id in data:
            parent_node_value = data[position_id]
            for child_position_id in parent_node_value.get("children", []):
                position_node = tree.find_by_id(child_position_id)
                if not position_node:
                    ItemPositionClass = NODEPOSITION_PARSE[data[child_position_id]['type']]
                    kwargs = data[child_position_id].copy()
                    kwargs.pop('children')
                    kwargs.pop('parents')
                    metadata = data[child_position_id].get('meta', {})
                    if metadata:
                        kwargs.update(metadata)
                    item_position = ItemPositionClass(**kwargs)
                    tree.insert(item_position, parent_node)
                cls.__generate_tree(child_position_id, data, tree)

    @classmethod
    def from_dict(cls, data:dict):
        tree = cls()
        tree.root.item.parents = data['ROOT_ID']['parents']
        tree.root.item.children = data['ROOT_ID']['children']

        grid_node = tree.find_by_id('GRID_ID')
        grid_node.item.parents = data['GRID_ID']['parents']

        cls.__generate_tree('ROOT_ID', data, tree)
        return tree