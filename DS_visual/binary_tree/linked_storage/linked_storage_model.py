from typing import Any, List, Optional, Tuple
from collections import deque

class TreeNode:
    def __init__(self, val: Any):
        self.val = val
        self.left: Optional['TreeNode'] = None
        self.right: Optional['TreeNode'] = None

    def __repr__(self):
        return f"TreeNode({self.val})"

class BinaryTreeModel:
    def __init__(self):
        self.root: Optional[TreeNode] = None

    @staticmethod
    def build_from_level_order(items: List[str]) -> Tuple[Optional[TreeNode], List[Optional[TreeNode]]]:
        if not items:
            return None, []

        it = iter(items)
        first = next(it, None)
        if first is None or first == "#":
            return None, [None] * len(items)

        root = TreeNode(first)
        node_list: List[Optional[TreeNode]] = [root]  # index 0 对应 items[0]
        q = deque([root])
        idx = 1  # 已处理 items 的下一个索引（node_list 的长度就是已填项数量）

        while q and idx < len(items):
            node = q.popleft()
            # left
            if idx < len(items):
                left_val = items[idx]
                if left_val != "#" and left_val is not None:
                    node.left = TreeNode(left_val)
                    q.append(node.left)
                    node_list.append(node.left)
                else:
                    node_list.append(None)
                idx += 1
            # right
            if idx < len(items):
                right_val = items[idx]
                if right_val != "#" and right_val is not None:
                    node.right = TreeNode(right_val)
                    q.append(node.right)
                    node_list.append(node.right)
                else:
                    node_list.append(None)
                idx += 1

        # 如果 items 比实际展开更多（例如以 # 结尾），补齐 node_list 长度
        while len(node_list) < len(items):
            node_list.append(None)

        return root, node_list
