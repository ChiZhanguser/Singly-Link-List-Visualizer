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

    def compare_values(self, a: Any, b: Any) -> int:
        """
        返回 -1 if a < b, 0 if a == b, 1 if a > b。
        尝试使用原生比较（数值或字符串等可比较类型）。若类型不兼容，则退回到字符串比较。
        """
        try:
            if a == b:
                return 0
            if a < b:
                return -1
            return 1
        except Exception:
            # 不可直接比较（比如 int 和 dict），使用字符串比较保证确定性
            sa, sb = str(a), str(b)
            if sa == sb:
                return 0
            return -1 if sa < sb else 1

    def insert(self, val: Any) -> TreeNode:
        if self.root is None:
            self.root = TreeNode(val)
            return self.root
        cur = self.root
        while True:
            cmp = self.compare_values(val, cur.val)
            if cmp < 0:
                if cur.left is None:
                    cur.left = TreeNode(val)
                    cur.left.parent = cur
                    return cur.left
                cur = cur.left
            else:
                # cmp >= 0（等于则放右子树，保留你原来的重复策略）
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
            cmp = self.compare_values(val, cur.val)
            if cmp == 0:
                return cur, path
            elif cmp < 0:
                cur = cur.left
            else:
                cur = cur.right
        return None, path

    def find_min(self, node: TreeNode) -> TreeNode:
        cur = node
        while cur.left:
            cur = cur.left
        return cur

    def transplant(self, u: TreeNode, v: Optional[TreeNode]):
        if u.parent is None:
            self.root = v
        else:
            if u is u.parent.left:
                u.parent.left = v
            else:
                u.parent.right = v
        if v:
            v.parent = u.parent

    def delete_node(self, node: Optional[TreeNode]) -> bool:
        if node is None:
            return False

        if node.left is None and node.right is None:
            if node.parent is None:
                self.root = None
            else:
                if node is node.parent.left:
                    node.parent.left = None
                else:
                    node.parent.right = None
        elif node.left is None:
            self.transplant(node, node.right)
        elif node.right is None:
            self.transplant(node, node.left)
        else:
            successor = self.find_min(node.right)
            if successor is not node.right:
                self.transplant(successor, successor.right)
                successor.right = node.right
                if successor.right:
                    successor.right.parent = successor
            self.transplant(node, successor)
            successor.left = node.left
            if successor.left:
                successor.left.parent = successor
        return True

    def delete(self, val: Any) -> Tuple[bool, List[TreeNode]]:
        node, path = self.search_with_path(val)
        if node is None:
            return False, path
        ok = self.delete_node(node)
        return ok, path
