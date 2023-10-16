import logging
from typing import List

from anytree import Node, RenderTree
from abc import ABC, abstractmethod

from typing_extensions import Self

from supersetapiclient.base.parse import ParseMixin
from supersetapiclient.dashboards.itemposition import ItemPositionType, ItemPosition, TabsItemPosition, \
    TabItemPosition, MarkdownItemPosition, RowItemPosition, GridItemPosition, DividerItemPosition, ColumnItemPosition
from supersetapiclient.exceptions import AcceptChildError, NodePositionValidationError

logger = logging.getLogger(__name__)

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
            self.item.parents = [p.item.id for p in self.path][:-1]

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
    def __init__(self, item: ItemPosition, parent: Self = None):
        if not hasattr(self, 'parent'):
            self.parent = parent

        self._validate(item)

        parent = self._get_next_row_free(item, parent)
        super().__init__(item, parent)


    def _get_next_row_free(self, item:ItemPosition, thisnode:NodePosition) ->NodePosition:
        """
            If thisnode does not exist, throw an exception.

            If thisnode is not Row or Tab, return a new row.

            # Handling when item.relocate = False
            checks if thisnode is a row, if yes, checks if there is space,
            otherwise, throw the exception.

            If thisnode is a TAB, create a new row.

            # Handling when item.relocate = True
            Check if thisnode is a row, if yes, check if there is space
            to include the item.

            If the row has full space, check if there are free sibling rows,
            if yes, include the item, otherwise, create a new row.

            If thisnode is a TAB, search all children of type ROW if there is space
            to include the item. If you don't find it, create a new row.

        :param item:
        :param thisnode:
        :return:
        """
        logger.debug(f'This node {thisnode.item.id}({thisnode.type_})')
        if thisnode:
            if thisnode.type_ == ItemPositionType.ROW:
                free_space, total_width = self.have_free_space(thisnode, item)
                if free_space:
                    logger.debug(f'This node {thisnode.item.id}({thisnode.type_}) has space, return it.')
                    return thisnode

                if not item.relocate:
                    raise NodePositionValidationError(
                        f'There is not enough space for this component. Total {total_width} exceeds the maximum allowable width of {ItemPosition.MAX_WIDTH}.')

                # The line is full.
                # Find out if there is a sibling with space
                if thisnode.siblings:
                    for node_brother in thisnode.siblings:
                        free_space, total_width = self.have_free_space(node_brother, item)
                        if free_space:
                            logger.debug(f'This node {thisnode.item.id}({thisnode.type_}) has no space. It has been verified that there is a sibling {node_brother.item.id}({node_brother.type_}) of it with free space, so return it.')
                            return node_brother

                # No rows with space were found, so create a new row node.
                logger.debug(f'There are no rows nodes with space. Creating a new row node and returning it.')
                return self.get_new_node_position(RowItemPosition(), thisnode.parent)
            elif thisnode.type_ == ItemPositionType.TAB:
                if thisnode.children:
                    for child in thisnode.children:
                        free_space, total_width = self.have_free_space(child, item)
                        if free_space:
                            logger.debug(f'A child node {child.item.id}({child.type_}) of thisnode with space was found. Return it.')
                            return child

                    if not item.relocate:
                        raise NodePositionValidationError(
                            f'There is not enough space for this component. Total {total_width} exceeds the maximum allowable width of {ItemPosition.MAX_WIDTH}.')

                # TAB does not have rows available, returning a new row node.
                logger.debug(f'This node {thisnode.item.id}({thisnode.type_}) does not have rows available, returning a new row node.')
                return self.get_new_node_position(RowItemPosition(), thisnode)
            elif thisnode.type_ == ItemPositionType.COLUMN:
                return thisnode
            #     free_space, total_width = self.have_free_space(thisnode, item)
            #     if free_space:
            #         logger.debug(f'This node {thisnode.item.id}({thisnode.type_}) has space, return it.')
            #         return thisnode
            #
            #     if not item.relocate:
            #         raise NodePositionValidationError(
            #             'Node of type COLUMN can only have one child. Add the item to a new node of type COLUMN or pass the argument as relocate=True to create a new column dynamically.')
            #     # thisnode already has a child.
            #     # If thisnode has a child, it checks if there is space on the parent node.
            #     # If yes, create a new column node sibling to thisnode and return this new node.
            #     free_space, total_width = self.have_free_space(thisnode.parent, item)
            #     if free_space:
            #         logger.debug(f'This node {thisnode.item.id}({thisnode.type_}) already has a child. Verified that the parent node {thisnode.parent.item.id}({thisnode.parent.type_}) has space. Returning a new COLUMN node.')
            #         return self.get_new_node_position(ColumnItemPosition(), thisnode.parent)
            #     else:
            #         # Parent of this node has no space.
            #         # Return the next free ROW type node. If you can't find it, create a new one and return.
            #         new_node_row = self._get_next_row_free(item, thisnode.parent)
            #         new_node_column = self.get_new_node_position(ColumnItemPosition(), new_node_row)
            #         logger.debug(f'This node {thisnode.item.id}({thisnode.type_}) has a child and its parent has no free space. A free ROW node {new_node_row.item.id}({new_node_row.type_}) was found and then a new node child {new_node_column.item.id}({new_node_column.type_} node was created. Returning this new child node.')
            #         return new_node_column
            else:
                logger.debug(f'Returning a new ROW node, child of this node {thisnode.item.id}({thisnode.type_}).')
                return self.get_new_node_position(RowItemPosition(), thisnode)

    @classmethod
    def have_free_space(cls, row_node, item):
        total_width = item.width
        try:
            for child in row_node.children:
                if hasattr(child.item, 'width'):
                    total_width += child.item.width
            if total_width <= ItemPosition.MAX_WIDTH:
                return True, total_width
            return False, total_width
        except Exception as err:
            msg = f"""Unexpected error. Unhandled exception.
                err={err}
                row_node={row_node}
                item={item}
            """
            logger.warning(msg)
            return True, total_width

    #Get the next brother free
    def _validate(self, item: ItemPosition):
        try:
            self.parent
        except:
            logger.warning(f'self not parent {self}?!'
                           f'{self.__dict__}')
            return

        if not hasattr(item, 'width') or self.parent is None:
            return

        total_width = item.width
        try:
            for node_sibling in self.siblings:
                total_width += node_sibling.item.width
            if total_width > ItemPosition.MAX_WIDTH and not item.relocate:
                raise NodePositionValidationError(
                    f'There is not enough space for this component. Total {total_width} exceeds the maximum allowable width of {MarkdownItemPosition.MAX_WIDTH}')
        except Exception as err:
            msg = f"""Unexpected error. Unhandled exception.
                    err={err}
                    item={item}
                """
            logger.warning(msg)


class MarkdownNodePosition(CheckFreeSpaceMixin, NodePosition):
    def __init__(self, item: MarkdownItemPosition, parent: Self = None):
        super().__init__(item, parent)


class ChartNodePosition(CheckFreeSpaceMixin, NodePosition):
    def __init__(self, item: MarkdownItemPosition, parent: Self = None):
        super().__init__(item, parent)


class ColumnNodePosition(NodePosition):
    def __init__(self, item: ColumnItemPosition, parent: Self = None):
        super().__init__(item, parent)

class NodePositionParse:
    PARSE = {
        'ROOT': RootNodePosition,
        'GRID': GridNodePosition,
        'ROW': RowNodePosition,
        'COLUMN': ColumnNodePosition,
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