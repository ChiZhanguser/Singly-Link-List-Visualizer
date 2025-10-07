# DS_visual/binary_tree/rbt_model.py
from typing import Any, Optional, List, Dict, Tuple


class RBNode:
    def __init__(self, val: Any, color: str = "R"):
        self.val = val
        self.left: Optional['RBNode'] = None
        self.right: Optional['RBNode'] = None
        self.parent: Optional['RBNode'] = None
        self.color: str = color  # "R" or "B"
        self.id = id(self)       # stable identifier for this runtime node
        # 当节点被 clone_tree 克隆时，克隆节点会设置 .orig_id = 原节点.id
        self.orig_id: Optional[int] = None

    def __repr__(self):
        return f"RBNode({self.val},{self.color})"


def clone_tree(node: Optional[RBNode]) -> Optional[RBNode]:
    """
    深拷贝一棵红黑树（复制 val, color, 结构；并在克隆节点上记录 orig_id=原节点.id）
    克隆节点的 parent 指向克隆结构内的父节点（保持内部一致性）
    """
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

    # ---------- rotations (maintain parent pointers carefully) ----------
    def _rotate_left(self, x: RBNode) -> RBNode:
        """Left rotate at node x, return new subtree root (y)."""
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

        # 如果 x 原来是根（parent 为 None），调用者需要检查并设置 self.root = y
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

    # ---------- insertion with rich step recording ----------
    def insert_with_steps(self, val: Any) -> Tuple[RBNode, List[RBNode], List[Dict], List[Optional[RBNode]]]:
        """
        Insert val and return:
          - inserted_node (model node)
          - path_nodes: list of nodes visited during BST insert (for visualizing search path)
          - events: list of events (recolor/rotation) in order; each event is a dict describing it but
                    referencing node identities via integer ids (e.g. parent_id, uncle_id, x_id, ...)
          - snapshots: list of cloned roots capturing tree states:
              snapshots[0] = before insertion (clone)
              snapshots[1] = after raw BST insertion (new node inserted, colored RED)
              snapshots[2..] = after each recolor/rotation step (clones)
        """
        events: List[Dict] = []
        path_nodes: List[RBNode] = []
        snapshots: List[Optional[RBNode]] = []

        # snapshot before any change
        snapshots.append(clone_tree(self.root))

        # BST insert
        if self.root is None:
            new_node = RBNode(val, color="B")  # root must be black
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

        # snapshot after raw insert
        snapshots.append(clone_tree(self.root))

        # fixup
        node = new_node
        while node is not self.root and node.parent and node.parent.color == "R":
            p = node.parent
            g = p.parent
            if g is None:
                break
            # determine uncle
            if g.left is p:
                uncle = g.right
                # case 1: uncle red -> recolor parent+uncle black, grand red, move up
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
                    # case 2/3: uncle black
                    # if node is right child -> left-rotate parent (convert to left-left)
                    if p.right is node:
                        # rotate left at p
                        new_subroot = self._rotate_left(p)
                        # fix parent pointers around new_subroot
                        # if p had parent (g), we already adjusted parent children in _rotate_left
                        if new_subroot.parent is None:
                            # new_subroot may become overall root
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
                        # after rotation, node.parent was updated; update p reference for next steps
                        p = node.parent
                    # recolor and right-rotate grand
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
