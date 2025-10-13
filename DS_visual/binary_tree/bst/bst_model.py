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

    # 保留你已有的 transplant 实现（如果已经存在则无需重复）
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

        # 三种情形：无子、仅一子、两子
        if node.left is None and node.right is None:
            # 叶子节点
            if node.parent is None:
                self.root = None
            else:
                if node is node.parent.left:
                    node.parent.left = None
                else:
                    node.parent.right = None
        elif node.left is None:
            # 只有右子
            self.transplant(node, node.right)
        elif node.right is None:
            # 只有左子
            self.transplant(node, node.left)
        else:
            # 两个子节点：用右子树的最小节点（后继）替换
            successor = self.find_min(node.right)
            if successor is not node.right:
                # 将 successor 用其右子替换（从原位置摘下）
                self.transplant(successor, successor.right)
                successor.right = node.right
                if successor.right:
                    successor.right.parent = successor
            # 将 node 替换为 successor
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

