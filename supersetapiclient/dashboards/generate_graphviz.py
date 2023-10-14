import os
import graphviz

from supersetapiclient.dashboards.itemposition import ItemPositionType
from supersetapiclient.dashboards.nodeposisition import NodePosition
from supersetapiclient.dashboards.treenodeposisition import TreeNodePosition

class GenerateGraphMixin:
    def _add_nodes_edges(self, graph, node: NodePosition, treenode: TreeNodePosition):
        for child_key in node.item.children:
            node_nane = child_key
            node_child = treenode.find_by_id(child_key)
            if node_child.item.type_:
                extra_info = ''
                node_nane += f'\n{node_child.item.type_}'
                if node_child.item.type_ == ItemPositionType.MARKDOWN:
                    extra_info = f'height:{node_child.item.meta.height}, width:{node_child.item.meta.width}'
            if hasattr(node_child.item, 'meta') and node_child.item.meta:
                meta = node_child.item.meta.to_dict()
                meta_name = meta.get('text') or meta.get('sliceName') or meta.get('code')
                if meta.get('chartId'):
                    meta_name = f"{meta['chartId']} - {meta['sliceName']}"
                if meta_name:
                    node_nane += f'\n{meta_name}'
                if extra_info:
                    node_nane += f'\n{extra_info}'
            graph.node(child_key, label=node_nane)
            graph.edge(node.name, child_key)
            self._add_nodes_edges(graph, node_child, treenode)

    @property
    def treenode(self):
        if hasattr(self, '_treenode'):
            return self._treenode
        raise ValueError('Variable self._treenode:TreeNodePosition not found')

    def generate_graph(self, dir_path:str):
        dot = graphviz.Digraph(comment="Árvore de Dependências")

        root_id = self.treenode.root.name
        dot.node(root_id, label=root_id)

        self._add_nodes_edges(dot, self.treenode.root, self.treenode)

        filename = os.path.join(dir_path, 'treenode')
        dot.render(filename, format='png')
        filename = os.path.join(dir_path, 'treenode.svg')
        dot.render(outfile=filename).replace('\\', '/')


    def print_position_tree(self):
       self.treenode.print()