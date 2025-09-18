# DS_visual/binary_tree/avl_model.py
from typing import Any, Optional, List, Tuple, Dict
import copy


class AVLNode:
    def __init__(self, val: Any):
        self.val = val
        self.left: Optional['AVLNode'] = None
        self.right: Optional['AVLNode'] = None
        self.parent: Optional['AVLNode'] = None
        self.height: int = 1
        self.id = id(self)

    def __repr__(self):
        return f"AVLNode({self.val})"

def clone_tree(node: Optional[AVLNode]) -> Optional[AVLNode]:
    """深拷贝一棵树（复制 val, 结构、height；parent 指针在重建时会被正确设置）"""
    if node is None:
        return None
    # 使用递归复制节点（不保留原 id）
    new_node = AVLNode(node.val)
    new_node.height = node.height
    new_node.left = clone_tree(node.left)
    new_node.right = clone_tree(node.right)
    if new_node.left:
        new_node.left.parent = new_node
    if new_node.right:
        new_node.right.parent = new_node
    return new_node

class AVLModel:
    def __init__(self):
        self.root: Optional[AVLNode] = None

    def _height(self, node: Optional[AVLNode]) -> int:
        return node.height if node else 0

    def _update_height(self, node: AVLNode):
        node.height = 1 + max(self._height(node.left), self._height(node.right))

    def _balance_factor(self, node: AVLNode) -> int:
        return self._height(node.left) - self._height(node.right)

    # rotations (same as before)
    def _rotate_right(self, z: AVLNode) -> AVLNode:
        y = z.left
        if y is None:
            return z
        T3 = y.right
        y.right = z
        z.left = T3
        parent = z.parent
        y.parent = parent
        z.parent = y
        if T3:
            T3.parent = z
        if parent:
            if parent.left is z:
                parent.left = y
            else:
                parent.right = y
        self._update_height(z)
        self._update_height(y)
        return y

    def _rotate_left(self, z: AVLNode) -> AVLNode:
        y = z.right
        if y is None:
            return z
        T2 = y.left
        y.left = z
        z.right = T2
        parent = z.parent
        y.parent = parent
        z.parent = y
        if T2:
            T2.parent = z
        if parent:
            if parent.left is z:
                parent.left = y
            else:
                parent.right = y
        self._update_height(z)
        self._update_height(y)
        return y

    def insert_with_steps(self, val: Any) -> Tuple[AVLNode, List[AVLNode], List[Dict], List[Optional[AVLNode]]]:
        """
        插入并返回丰富信息：
          - inserted_node: 新插入的节点引用 (在 current model 中)
          - path_nodes: 插入时访问的节点（按顺序，便于可视化搜索路径）
          - rotations: list of rotation dicts: { type:'LL'|'RR'|'LR'|'RL', 'z':z_node, 'y':y_node, 'x':x_node, 'new_root':new_subroot }
          - snapshots: list of tree-roots 的 clone：
                snapshots[0] = tree 在插入前的 clone (可为 None)
                snapshots[1] = tree 在插入后但尚未旋转（clone）
                snapshots[2..] = tree 每次旋转后对应的 clone（按 rotations 顺序）
        注意：快照中的节点为 clone（id 不同），仅用于可视化（位置计算）；path_nodes/rotations 中的节点是 model 中的真实节点。
        """
        rotations: List[Dict] = []
        path_nodes: List[AVLNode] = []
        snapshots: List[Optional[AVLNode]] = []

        # snapshot before any modification
        snapshots.append(clone_tree(self.root))

        # normal BST insert (record path)
        if self.root is None:
            self.root = AVLNode(val)
            path_nodes.append(self.root)
            # snapshot after insertion (no rotations)
            snapshots.append(clone_tree(self.root))
            return self.root, path_nodes, rotations, snapshots

        cur = self.root
        parent = None
        while cur:
            parent = cur
            path_nodes.append(cur)
            if str(val) < str(cur.val):
                cur = cur.left
            else:
                cur = cur.right

        # attach new node
        new_node = AVLNode(val)
        new_node.parent = parent
        if str(val) < str(parent.val):
            parent.left = new_node
        else:
            parent.right = new_node
        path_nodes.append(new_node)

        # snapshot immediately after insertion (before rotations)
        snapshots.append(clone_tree(self.root))

        # rebalance upwards, record rotations and snapshot after each rotation
        node = new_node.parent
        while node:
            self._update_height(node)
            bf = self._balance_factor(node)

            # LL
            if bf > 1 and self._balance_factor(node.left) >= 0:
                z = node
                y = node.left
                x = y.left if y else None
                new_subroot = self._rotate_right(z)
                if new_subroot.parent is None:
                    self.root = new_subroot
                rotations.append({'type':'LL', 'z':z, 'y':y, 'x':x, 'new_root':new_subroot})
                snapshots.append(clone_tree(self.root))
                node = new_subroot.parent
                continue

            # LR
            if bf > 1 and self._balance_factor(node.left) < 0:
                z = node
                y = node.left
                x = y.right if y else None
                self._rotate_left(y)
                new_subroot = self._rotate_right(z)
                if new_subroot.parent is None:
                    self.root = new_subroot
                rotations.append({'type':'LR', 'z':z, 'y':y, 'x':x, 'new_root':new_subroot})
                snapshots.append(clone_tree(self.root))
                node = new_subroot.parent
                continue

            # RR
            if bf < -1 and self._balance_factor(node.right) <= 0:
                z = node
                y = node.right
                x = y.right if y else None
                new_subroot = self._rotate_left(z)
                if new_subroot.parent is None:
                    self.root = new_subroot
                rotations.append({'type':'RR', 'z':z, 'y':y, 'x':x, 'new_root':new_subroot})
                snapshots.append(clone_tree(self.root))
                node = new_subroot.parent
                continue

            # RL
            if bf < -1 and self._balance_factor(node.right) > 0:
                z = node
                y = node.right
                x = y.left if y else None
                self._rotate_right(y)
                new_subroot = self._rotate_left(z)
                if new_subroot.parent is None:
                    self.root = new_subroot
                rotations.append({'type':'RL', 'z':z, 'y':y, 'x':x, 'new_root':new_subroot})
                snapshots.append(clone_tree(self.root))
                node = new_subroot.parent
                continue

            node = node.parent

        return new_node, path_nodes, rotations, snapshots
