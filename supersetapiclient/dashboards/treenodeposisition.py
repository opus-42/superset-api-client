from typing import List, Dict

from anytree import Node, RenderTree, search

from typing_extensions import Self

from supersetapiclient.dashboards.itemposition import ItemPositionType, GenericItemPosition, _RootItemPosition, \
    _GridItemPosition, _TABSItemPosition, TABItemPosition, MarkdownItemPosition, _ROWItemPosition
from supersetapiclient.utils import generate_uuid


class NodePosition(Node):
    def __init__(self, item: GenericItemPosition, parent: Self=None, children: Self=None):
        self._item = item
        super().__init__(item.id, parent, children)

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

class TreeNodePosition:
    def __init__(self):
        self._root = NodePosition(_RootItemPosition())
        NodePosition(_GridItemPosition(), self._root)

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

