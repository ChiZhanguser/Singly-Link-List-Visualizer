from typing import Any, Optional, List, Dict, Tuple


class RBNode:
    def __init__(self, val: Any, color: str = "R"):
        self.val = val
        self.left: Optional['RBNode'] = None
        self.right: Optional['RBNode'] = None
        self.parent: Optional['RBNode'] = None
        self.color: str = color  # 是红节点还是黑节点
        self.id = id(self)    
        self.orig_id: Optional[int] = None

    def __repr__(self):
        return f"RBNode({self.val},{self.color})"


def clone_tree(node: Optional[RBNode]) -> Optional[RBNode]:
    if node is None:
        return None
    new_node = RBNode(node.val, color=node.color)
    new_node.orig_id = node.id
    new_node.left = clone_tree(node.left)
    new_node.right = clone_tree(node.right)
    if new_node.left:
        new_node.left.parent = new_node
    if new_node.right:
        new_node.right.parent = new_node
    return new_node


class RBModel:
    def __init__(self):
        self.root: Optional[RBNode] = None

    def _rotate_left(self, x: RBNode) -> RBNode:
        y = x.right
        if y is None:
            return x
        beta = y.left
        y.left = x
        x.right = beta

        parent = x.parent
        y.parent = parent
        x.parent = y
        if beta:
            beta.parent = x

        if parent:
            if parent.left is x:
                parent.left = y
            else:
                parent.right = y
        return y

    def _rotate_right(self, x: RBNode) -> RBNode:
        """Right rotate at node x, return new subtree root (y)."""
        y = x.left
        if y is None:
            return x
        beta = y.right
        y.right = x
        x.left = beta

        parent = x.parent
        y.parent = parent
        x.parent = y
        if beta:
            beta.parent = x

        if parent:
            if parent.left is x:
                parent.left = y
            else:
                parent.right = y

        return y
    
    def insert_with_steps(self, val: Any) -> Tuple[RBNode, List[RBNode], List[Dict], List[Optional[RBNode]]]:
        events: List[Dict] = []
        path_nodes: List[RBNode] = []
        snapshots: List[Optional[RBNode]] = []

        snapshots.append(clone_tree(self.root))

        if self.root is None:
            new_node = RBNode(val, color="B")  # 根节点必须是黑的
            self.root = new_node
            path_nodes.append(new_node)
            snapshots.append(clone_tree(self.root))
            return new_node, path_nodes, events, snapshots

        cur = self.root
        parent = None
        while cur:
            parent = cur
            path_nodes.append(cur)
            if str(val) < str(cur.val):
                cur = cur.left
            else:
                cur = cur.right

        new_node = RBNode(val, color="R")
        new_node.parent = parent
        if str(val) < str(parent.val):
            parent.left = new_node
        else:
            parent.right = new_node
        path_nodes.append(new_node)

        snapshots.append(clone_tree(self.root))

        node = new_node
        while node is not self.root and node.parent and node.parent.color == "R":
            p = node.parent
            g = p.parent
            if g is None:
                break
            if g.left is p:
                uncle = g.right
                if uncle and uncle.color == "R":
                    p.color = "B"
                    uncle.color = "B"
                    g.color = "R"
                    events.append({
                        'type': 'recolor',
                        'parent_id': p.id,
                        'uncle_id': uncle.id,
                        'grand_id': g.id
                    })
                    snapshots.append(clone_tree(self.root))
                    node = g
                    continue
                else:
                    if p.right is node:
                        new_subroot = self._rotate_left(p)
                        if new_subroot.parent is None:
                            if g.parent is None:
                                self.root = new_subroot
                        events.append({
                            'type': 'rotate_left',
                            'x_id': p.id,
                            'y_id': node.id,
                            'z_id': g.id,
                            'new_root_id': new_subroot.id
                        })
                        snapshots.append(clone_tree(self.root))
                        p = node.parent
                    p.color = "B"
                    g.color = "R"
                    new_subroot = self._rotate_right(g)
                    if new_subroot.parent is None:
                        self.root = new_subroot
                    events.append({
                        'type': 'rotate_right',
                        'x_id': g.id,
                        'y_id': p.id,
                        'z_id': node.id,
                        'new_root_id': new_subroot.id
                    })
                    snapshots.append(clone_tree(self.root))
                    break
            else:
                # symmetric: parent is right child of grand
                uncle = g.left
                if uncle and uncle.color == "R":
                    p.color = "B"
                    uncle.color = "B"
                    g.color = "R"
                    events.append({
                        'type': 'recolor',
                        'parent_id': p.id,
                        'uncle_id': uncle.id,
                        'grand_id': g.id
                    })
                    snapshots.append(clone_tree(self.root))
                    node = g
                    continue
                else:
                    # if node is left child -> rotate right at p
                    if p.left is node:
                        new_subroot = self._rotate_right(p)
                        if new_subroot.parent is None:
                            if g.parent is None:
                                self.root = new_subroot
                        events.append({
                            'type': 'rotate_right',
                            'x_id': p.id,
                            'y_id': node.id,
                            'z_id': g.id,
                            'new_root_id': new_subroot.id
                        })
                        snapshots.append(clone_tree(self.root))
                        p = node.parent
                    # recolor and rotate left at grand
                    p.color = "B"
                    g.color = "R"
                    new_subroot = self._rotate_left(g)
                    if new_subroot.parent is None:
                        self.root = new_subroot
                    events.append({
                        'type': 'rotate_left',
                        'x_id': g.id,
                        'y_id': p.id,
                        'z_id': node.id,
                        'new_root_id': new_subroot.id
                    })
                    snapshots.append(clone_tree(self.root))
                    break

        # ensure root black
        if self.root and self.root.color != "B":
            self.root.color = "B"
            events.append({'type': 'root_recolor', 'node_id': self.root.id})
            snapshots.append(clone_tree(self.root))

        return new_node, path_nodes, events, snapshots
