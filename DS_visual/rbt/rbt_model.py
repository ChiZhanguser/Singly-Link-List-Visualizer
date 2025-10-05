# DS_visual/binary_tree/rbt_model.py
from typing import Any, Optional, List, Dict


class RBNode:
    def __init__(self, val: Any, color: str = "R"):
        self.val = val
        self.left: Optional['RBNode'] = None
        self.right: Optional['RBNode'] = None
        self.parent: Optional['RBNode'] = None
        self.color: str = color  # "R" or "B"
        self.id = id(self)

    def __repr__(self):
        return f"RBNode({self.val},{self.color})"


def clone_tree(node: Optional[RBNode]) -> Optional[RBNode]:
    """深拷贝一棵红黑树（复制 val, color, 结构；parent 在重建时正确设置）"""
    if node is None:
        return None
    new_node = RBNode(node.val, color=node.color)
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

        # if x was root, now y should become root (caller must set if needed)
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
    def insert_with_steps(self, val: Any) -> (RBNode, List[RBNode], List[Dict], List[Optional[RBNode]]):
        """
        Insert val and return:
          - inserted_node (model node)
          - path_nodes: list of nodes visited during BST insert (for visualizing search path)
          - events: list of events (recolor/rotation) in order; each event is a dict describing it
          - snapshots: list of cloned roots capturing tree states:
              snapshots[0] = before insertion (clone)
              snapshots[1] = after raw BST insertion (new node inserted, colored RED)
              snapshots[2..] = after each recolor/rotation step (clones)
        Notes:
          - events reference model nodes (not clones).
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
            # keep same comparison strategy as AVL code
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
                    events.append({'type': 'recolor', 'parent': p, 'uncle': uncle, 'grand': g})
                    snapshots.append(clone_tree(self.root))
                    node = g
                    continue
                else:
                    # case 2/3: uncle black
                    # if node is right child -> left-rotate parent (convert to left-left)
                    if p.right is node:
                        # rotate left at p
                        new_subroot = self._rotate_left(p)
                        # if new_subroot has no parent => it might be new root
                        if new_subroot.parent is None:
                            # fix top-level pointer
                            if g.parent is None:
                                self.root = new_subroot
                        events.append({'type': 'rotate_left', 'x': p, 'y': node, 'z': g, 'new_root': new_subroot})
                        snapshots.append(clone_tree(self.root))
                        # after rotation, node becomes left child of g's left-subtree; update p reference
                        p = node.parent  # updated
                    # now node is left child of parent p; recolor and right-rotate grand
                    p.color = "B"
                    g.color = "R"
                    new_subroot = self._rotate_right(g)
                    if new_subroot.parent is None:
                        self.root = new_subroot
                    events.append({'type': 'rotate_right', 'x': g, 'y': p, 'z': node, 'new_root': new_subroot})
                    snapshots.append(clone_tree(self.root))
                    break
            else:
                # symmetric: parent is right child of grand
                uncle = g.left
                if uncle and uncle.color == "R":
                    p.color = "B"
                    uncle.color = "B"
                    g.color = "R"
                    events.append({'type': 'recolor', 'parent': p, 'uncle': uncle, 'grand': g})
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
                        events.append({'type': 'rotate_right', 'x': p, 'y': node, 'z': g, 'new_root': new_subroot})
                        snapshots.append(clone_tree(self.root))
                        p = node.parent
                    # recolor and rotate left at grand
                    p.color = "B"
                    g.color = "R"
                    new_subroot = self._rotate_left(g)
                    if new_subroot.parent is None:
                        self.root = new_subroot
                    events.append({'type': 'rotate_left', 'x': g, 'y': p, 'z': node, 'new_root': new_subroot})
                    snapshots.append(clone_tree(self.root))
                    break

        # ensure root black
        if self.root and self.root.color != "B":
            self.root.color = "B"
            events.append({'type': 'root_recolor', 'node': self.root})
            snapshots.append(clone_tree(self.root))

        return new_node, path_nodes, events, snapshots
