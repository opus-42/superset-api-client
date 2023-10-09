from typing import List

from anytree import Node, RenderTree
from abc import ABC, abstractmethod

from typing_extensions import Self

from supersetapiclient.base.parse import ParseMixin
from supersetapiclient.dashboards.itemposition import ItemPositionType, ItemPosition, TabsItemPosition, \
    TabItemPosition, MarkdownItemPosition, RowItemPosition, GridItemPosition, DividerItemPosition
from supersetapiclient.exceptions import AcceptChildError, NodePositionValidationError

class NodePosition(Node, ParseMixin):
    def __init__(self, item: ItemPosition, parent: Self=None):
        super().__init__(item.id, parent)
        self._is_sibling_left = False
        self._is_sibling_right = False

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

    def get_new_node_position(self, item: ItemPosition, parent: Self):
        return NodePositionParse.get_instance(item, item.type_, parent)

    def insert(self, item: ItemPosition) -> Self:
        if not item.ACCEPT_CHILD:
            raise NodePositionValidationError(f'{self.get_class(item.type_).__name__} component does not allow children')
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


    def __insert_sibling_order(self, orphan_children: List[Self], node_position:Self, parent= Self):
        parent.item.children = []

        # I already have a father. Remove me from the list of orphaned children.
        if node_position.parent != parent:
            orphan_children.remove(node_position)

        for child in orphan_children:
            parent.item.children.append(child.item.id)
        parent.children = orphan_children

        return node_position


    def insert_sibling_left(self, item: ItemPosition) -> Self:
        self._is_sibling_left = True

        self._validate(item)
        node_position = None
        orphan_children = []

        # fill list children
        for child in self.parent.children:
            if child == self:
                node_position = self.get_new_node_position(item, self.parent)
                orphan_children.append(node_position)
            orphan_children.append(child)
        return self.__insert_sibling_order(orphan_children, node_position, self.parent)

    def insert_sibling_right(self, item: ItemPosition) -> Self:
        self._is_sibling_right = True

        self._validate(item)
        node_position = None
        orphan_children = []

        # fill list children
        for child in self.parent.children:
            orphan_children.append(child)
            if child == self:
                node_position = self.get_new_node_position(item, self.parent)
                orphan_children.append(node_position)

        return self.__insert_sibling_order(orphan_children, node_position, self.parent)


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
    def _validate(self, item: ItemPosition):
        return


class TabNodePosition(NodePosition):
    def __init__(self, item: TabItemPosition, parent: Self):
        parent_tabs = self._get_or_insert_parent(TabsItemPosition(), parent, TabsNodePosition)
        super().__init__(item, parent_tabs)

    def _validate(self, item: ItemPosition):
        if self.parent.item.type_ != ItemPositionType.TABS:
            raise NodePositionValidationError('The TAB parent must be TABS.')

    def insert(self, item: ItemPosition) -> Self:
        if not item.type_ in (ItemPositionType.TAB, ItemPositionType.DIVIDER, ItemPositionType.MARKDOWN):
            raise NodePositionValidationError(f'It is only allowed to insert Item Position of the {item.type_} type')
        if item.type_ == ItemPositionType.TAB:
            parent = self._get_or_insert_parent(TabsItemPosition(), self, TabsNodePosition)
            return self.get_new_node_position(item, parent)
        return NodePositionParse.get_instance(item, item.type_, self)


class DividerNodePosistion(NodePosition):
    def _validate(self, item: ItemPosition):
        if item.children:
            raise NodePositionValidationError()


class CheckFreeSpaceMixin:
    def __init__(self, item: MarkdownItemPosition, parent: Self = None):
        self._validate(item)

        parent = self._get_next_row_free(item, parent)

        # if parent and parent.type_ != ItemPositionType.ROW:
        #     parent = self._insert_parent(RowItemPosition(), parent, RowNodePosition)

        super().__init__(item, parent)


    def _get_next_row_free(self, item, parent):
        """
            Se parent não existir dispare uma exceção.

            Se parent não for Row ou Tab, retorne com uma nova row.

            # Tratamento quando item.relocate = False
            checa se parent é uma row, se sim, verifica se há espaço,
            caso contrário, dispare a exceção.

            Se parente for um TAB, crie uma nova row.

            # Tratamento quando item.relocate = True
            Checa se parent é uma row, se sim, verifica se há espaço
            para incluir o item.

            Se a row estiver com espaço lotado, verifica se há rows irmãos livre,
            se sim, inclui o item, caso contrário, cria uma nova row.

            Se parent for um TAB, busca em todos os filhos do tipo ROW se há espaço
            para incluir o item. Se não encontrar, crua uma nova row.

        :param item:
        :param parent:
        :return:
        """

        if parent:
            if parent.type_ == ItemPositionType.ROW:
                free_space, total_width = self.have_free_space(parent, item)
                if free_space:
                    return parent

                if not item.relocate:
                    raise NodePositionValidationError(
                        f'There is not enough space for this component. Total {total_width} exceeds the maximum allowable width of {ItemPosition.MAX_WIDTH}.')

                # Row está cheio.
                # Busca se existe algum irmão com espaço
                if parent.sibling:
                    for node_irmao in parent.sibling:
                        free_space, total_width = self.have_free_space(node_irmao, item)
                        if free_space:
                            return node_irmao

                # Não foi encontrado rows com espaço, então cria uma nova.
                return self.get_new_node_position(RowItemPosition(), parent.parent)
            elif parent.type_ == ItemPositionType.TAB:
                if parent.children:
                    for child in parent.children:
                        free_space, total_width = self.have_free_space(child, item)
                        if free_space:
                            return child

                    if not item.relocate:
                        raise NodePositionValidationError(
                            f'There is not enough space for this component. Total {total_width} exceeds the maximum allowable width of {ItemPosition.MAX_WIDTH}.')

                # Aba não possui rows disponíveis, retornando uma nova
                return self.get_new_node_position(RowItemPosition(), parent)
            else:
                return self.get_new_node_position(RowItemPosition(), parent)

    @classmethod
    def have_free_space(cls, row_node, item):
        total_width = item.width
        for child in row_node.children:
            total_width += child.item.width
        if total_width <= ItemPosition.MAX_WIDTH:
            return True, total_width
        return False, total_width

    #Get the next brother free
    def _validate(self, item: ItemPosition):
        if not hasattr(item, 'width') or self.parent is None:
            return
        total_width = item.width
        for node_sibling in self.siblings:
            total_width += node_sibling.item.width
        if total_width > ItemPosition.MAX_WIDTH and not item.relocate:
            raise NodePositionValidationError(
                f'There is not enough space for this component. Total {total_width} exceeds the maximum allowable width of {MarkdownItemPosition.MAX_WIDTH}')


class MarkdownNodePosition(CheckFreeSpaceMixin, NodePosition):
    def __init__(self, item: MarkdownItemPosition, parent: Self = None):
        super().__init__(item, parent)


class ChartNodePosition(CheckFreeSpaceMixin, NodePosition):
    def __init__(self, item: MarkdownItemPosition, parent: Self = None):
        super().__init__(item, parent)


class NodePositionParse:
    PARSE = {
        'ROOT': RootNodePosition,
        'GRID': GridNodePosition,
        'ROW': RowNodePosition,
        'TABS': TabsNodePosition,
        'TAB': TabNodePosition,
        'MARKDOWN': MarkdownNodePosition,
        'DIVIDER': DividerNodePosistion,
        'CHART': ChartNodePosition

    }

    @classmethod
    def get_instance(cls, item: NodePosition, type_: ItemPositionType, parent: NodePosition):
        NodePositionClass = cls.get_class(str(type_))
        return NodePositionClass(item, parent)

    @classmethod
    def get_class(cls, type_: str):
        return cls.PARSE.get(type_, NodePosition)