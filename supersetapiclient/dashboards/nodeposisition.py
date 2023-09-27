from typing import List

from anytree import Node
from abc import ABC, abstractmethod
from typing_extensions import Self

from supersetapiclient.dashboards.itemposition import ItemPositionType, ItemPosition, _TabsItemPosition, \
    TabItemPosition, MarkdownItemPosition, _RowItemPosition, _GridItemPosition, DividerItemPosition
from supersetapiclient.exceptions import AcceptChildError, NodePositionValidationError



class NodePosition(Node):
    def __init__(self, item: ItemPosition, parent: Self=None):
        super().__init__(item.id, parent)
        self._item = item
        self._validate(item)
        if parent and not parent.item.ACCEPT_CHILD:
            raise AcceptChildError()
        self._add_child(parent)

    def _add_child(self,  parent: Self):
        if parent:
            parent.item.children.append(self.item.id)
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

    @abstractmethod
    def _validate(self, item: ItemPosition):
        return
        # TODO: disparar a exceção raise NotImplementedError(item)

    def get_new_node_position(self, item: ItemPosition, parent: Self):
        return NodePositionParse.get_instance(item, item.type_, parent)

    def insert(self, item: TabItemPosition) -> Self:
        return NodePositionParse.get_instance(item, item.type_, self)

    def _insert_parent(self, item: ItemPosition, parent: Self, NodePositionClass:Self):
        if parent.type_ != item.type_:
            return NodePositionClass(item, parent)
        return parent

    def _get_or_insert_parent(self, item: ItemPosition, parent: Self, NodePositionClass: Self):
        '''
        Checks if the parent node is of type item.type_, if yes, return it,
        If the parent is not of type item.type_, check if there is a child of type TABS, if so, return the first one.
        If the parent is not of type item.type_ and there are no children of type item.type_, add a new node to the tree and return it as the parent.
        :param item: GenericItemPosition
        :param parent: NodePosition
        :return: new NodePosition or parent
        '''
        if parent.type_ != item.type_:
            child_tabs_exists = False
            for child in parent.children:
                if child.type_ == item.type_:
                    parent = child
                    child_tabs_exists = True
            if not child_tabs_exists:
                return NodePositionClass(item, parent)
        return parent

    def __insert_sibling_order(self, children: List[Self], node_position:Self, parent= Self):
        # append children in order
        parent.item.children = []
        for child in children:
            parent.item.children.append(child.item.id)
        parent.children = children

        return node_position

    def insert_sibling_left(self, item: ItemPosition) -> Self:
        self._validate(item)
        node_position = None
        children = []

        # fill list children
        for child in self.parent.children:
            if child == self:
                node_position = self.get_new_node_position(item, self.parent)
                children.append(node_position)
            children.append(child)
        return self.__insert_sibling_order(children, node_position, self.parent)

    def insert_sibling_right(self, item: ItemPosition) -> Self:
        self._validate(item)
        node_position = None
        children = []

        # fill list children
        for child in self.parent.children:
            children.append(child)
            if child == self:
                node_position = self.get_new_node_position(item, self.parent)
                children.append(node_position)
        return self.__insert_sibling_order(children, node_position, self.parent)


    def insert_child(self, item: ItemPosition, position_index = int):
        self._validate(item)

        if position_index < 0:
            position_index = 0
        max_children = len(self.children)
        if position_index >= max_children:
            position_index = max_children

        node_position = None
        children = []

        # fill list children
        index = 0
        for child in self.children:
            if index == position_index:
                node_position = self.get_new_node_position(item, self)
                children.append(node_position)
            children.append(child)
            index += 1
        return self.__insert_sibling_order(children, node_position, self)


class RootNodePosition(NodePosition):
    def _validate(self, item: ItemPosition):
        if self.parent:
            raise NodePositionValidationError('Root cannot have a parent.')


class GridNodePosition(NodePosition):
    def _validate(self, item: ItemPosition):
        if self.parent.item.type_ != ItemPositionType.ROOT:
            raise NodePositionValidationError('The GRID parent must be ROOT.')


class TabsNodePosition(NodePosition):
    def _validate(self, item: ItemPosition):
        return


class RowNodePosition(NodePosition):
    def insert(self, item: TabItemPosition) -> Self:
        return MarkdownNodePosition(item, self)


    def _validate(self, item: ItemPosition):
        return

class TabNodePosition(NodePosition):
    def __init__(self, item: TabItemPosition, parent: Self):
        parent_tabs = self._get_or_insert_parent(_TabsItemPosition(), parent, TabsNodePosition)
        super().__init__(item, parent_tabs)

    def _validate(self, item: ItemPosition):
        if self.parent.item.type_ != ItemPositionType.TABS:
            raise NodePositionValidationError('The TAB parent must be TABS.')

    def insert(self, item: ItemPosition) -> Self:
        if not item.type_ in (ItemPositionType.TAB, ItemPositionType.DIVIDER, ItemPositionType.MARKDOWN):
            raise NodePositionValidationError('It is only allowed to insert Item Position of the TAB type')
        if item.type_ == ItemPositionType.TAB:
            parent = self._get_or_insert_parent(_TabsItemPosition(), self, TabsNodePosition)
            return self.get_new_node_position(item, parent)
        return NodePositionParse.get_instance(item, item.type_, self)

    # def get_new_node_position(self, item: ItemPosition, parent: Self):
    #     return TabNodePosition(item, parent)


class MarkdownNodePosition(NodePosition):
    def __init__(self, item: MarkdownItemPosition, parent: Self = None):
        self._validate(item)
        if parent and parent.type_ != ItemPositionType.ROW:
            parent = self._insert_parent(_RowItemPosition(), parent, RowNodePosition)
        super().__init__(item, parent)

    def _validate(self, item: ItemPosition):
        if not hasattr(item, 'width') or self.parent is None:
            return
        self.siblings
        total_width = 0
        for node_child in self.siblings:
            total_width += node_child.item.width
        total_width+=item.width
        if total_width > MarkdownItemPosition.MAX_WIDTH:
            raise NodePositionValidationError(
                f'There is not enough space for this component. Total {total_width} exceeds the maximum allowable width of {MarkdownItemPosition.MAX_WIDTH}')

    def insert(self, item: TabItemPosition) -> Self:
        raise NodePositionValidationError('Markdown component does not allow children')

    # def get_new_node_position(self, item: ItemPosition, parent: Self):
    #     return MarkdownNodePosition(item, self.parent)


class DivideNodePosistion(NodePosition):
    def _validate(self, item: ItemPosition):
        if item.children:
            raise NodePositionValidationError()


class NodePositionParse:
    PARSE = {
        'ROOT': RootNodePosition,
        'GRID': GridNodePosition,
        'ROW': RowNodePosition,
        'TABS': TabsNodePosition,
        'TAB': TabNodePosition,
        'MARKDOWN': MarkdownNodePosition,
        'DIVIDER': DivideNodePosistion
    }

    @classmethod
    def get_instance(cls, item: NodePosition, type_: ItemPositionType, parent: NodePosition):
        NodePositionClass = cls.get_class(str(type_))
        return NodePositionClass(item, parent)

    @classmethod
    def get_class(cls, type_: str):
        return cls.PARSE.get(type_, NodePosition)