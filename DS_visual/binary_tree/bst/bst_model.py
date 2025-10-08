from typing import Any, Optional, List, Tuple

class TreeNode:
    def __init__(self, val: Any):
        self.val = val
        self.left: Optional['TreeNode'] = None
        self.right: Optional['TreeNode'] = None
        self.parent: Optional['TreeNode'] = None

    def __repr__(self):
        return f"TreeNode({self.val})"

class BSTModel:
    def __init__(self):
        self.root: Optional[TreeNode] = None

    def insert(self, val: Any) -> TreeNode:
        if self.root is None:
            self.root = TreeNode(val)
            return self.root
        cur = self.root
        while True:
            if str(val) < str(cur.val):
                if cur.left is None:
                    cur.left = TreeNode(val)
                    cur.left.parent = cur
                    return cur.left
                cur = cur.left
            else:
                if cur.right is None:
                    cur.right = TreeNode(val)
                    cur.right.parent = cur
                    return cur.right
                cur = cur.right

    def search_with_path(self, val: Any) -> Tuple[Optional[TreeNode], List[TreeNode]]:
        path: List[TreeNode] = []
        cur = self.root
        while cur:
            path.append(cur)
            if str(val) == str(cur.val):
                return cur, path
            elif str(val) < str(cur.val):
                cur = cur.left
            else:
                cur = cur.right
        return None, path

    def find_min(self, node: TreeNode) -> TreeNode:
        cur = node
        while cur.left:
            cur = cur.left
        return cur

    def transplant(self, u: TreeNode, v: Optional[TreeNode]):  # 用子树 v 替换子树 u
        if u.parent is None:
            self.root = v
        else:
            if u is u.parent.left:
                u.parent.left = v
            else:
                u.parent.right = v
        if v:
            v.parent = u.parent

    def delete(self, val: Any) -> Tuple[bool, List[TreeNode]]:
        node, path = self.search_with_path(val)
        if node is None:
            return False, path
        if node.left is None and node.right is None:  # 叶子结点
            if node.parent is None:
                self.root = None
            else:
                if node is node.parent.left:
                    node.parent.left = None
                else:
                    node.parent.right = None
        elif node.left is None:                # 右边有孩子
            self.transplant(node, node.right)
        elif node.right is None:                     # 左边有孩子
            self.transplant(node, node.left)
        else:                                   # 两个子节点
            successor = self.find_min(node.right)
            if successor.parent is not node:
                self.transplant(successor, successor.right)
                successor.right = node.right
                if successor.right:
                    successor.right.parent = successor
            self.transplant(node, successor)
            successor.left = node.left
            if successor.left:
                successor.left.parent = successor
        return True, path
