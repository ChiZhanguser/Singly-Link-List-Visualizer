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
        """普通插入（返回插入的节点实例）——维护 parent 指针"""
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
        """
        查找并返回 (node, path)
        path 是按访问顺序的节点列表（不包含 None）
        """
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

    def transplant(self, u: TreeNode, v: Optional[TreeNode]):
        """
        用 v 替换子树 u（u.parent 指针被考虑），用于删除实现
        """
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
        """
        删除值 val（首次匹配），返回 (成功, path_of_search)
        删除按照标准 BST 算法进行，维护 parent 指针。
        """
        node, path = self.search_with_path(val)
        if node is None:
            return False, path

        # 三种情况
        if node.left is None and node.right is None:
            # 叶子
            if node.parent is None:
                self.root = None
            else:
                if node is node.parent.left:
                    node.parent.left = None
                else:
                    node.parent.right = None
        elif node.left is None:
            # 仅右子
            self.transplant(node, node.right)
        elif node.right is None:
            # 仅左子
            self.transplant(node, node.left)
        else:
            # 两个子节点：找到后继 (min of right subtree)
            successor = self.find_min(node.right)
            # successor 可能是 node.right 本身或其左支
            if successor.parent is not node:
                # 将 successor 的右子替代 successor
                self.transplant(successor, successor.right)
                successor.right = node.right
                if successor.right:
                    successor.right.parent = successor
            # 替换 node 为 successor
            self.transplant(node, successor)
            successor.left = node.left
            if successor.left:
                successor.left.parent = successor
        return True, path
