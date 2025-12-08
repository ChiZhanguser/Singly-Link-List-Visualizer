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

    # ============================================
    # 查找操作
    # ============================================
    @staticmethod
    def search(root: Optional['TreeNode'], value: Any) -> Tuple[Optional['TreeNode'], List['TreeNode']]:
        """
        在二叉树中查找指定值的节点 (BFS层序查找)
        
        返回:
            - 找到的节点 (或 None)
            - 查找路径 (访问过的节点列表)
        """
        if not root:
            return None, []
        
        path = []
        queue = deque([root])
        
        while queue:
            node = queue.popleft()
            path.append(node)
            
            # 比较值（支持字符串和数字比较）
            if str(node.val) == str(value):
                return node, path
            
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        
        return None, path

    @staticmethod
    def search_with_parent(root: Optional['TreeNode'], value: Any) -> Tuple[Optional['TreeNode'], Optional['TreeNode'], str]:
        """
        查找节点并返回其父节点
        
        返回:
            - 找到的节点 (或 None)
            - 父节点 (或 None，如果是根节点)
            - 子节点方向 ('left', 'right', 或 '' 表示根节点)
        """
        if not root:
            return None, None, ''
        
        if str(root.val) == str(value):
            return root, None, ''
        
        queue = deque([(root, None, '')])  # (节点, 父节点, 方向)
        
        while queue:
            node, parent, direction = queue.popleft()
            
            if str(node.val) == str(value):
                return node, parent, direction
            
            if node.left:
                queue.append((node.left, node, 'left'))
            if node.right:
                queue.append((node.right, node, 'right'))
        
        return None, None, ''

    # ============================================
    # 插入操作
    # ============================================
    @staticmethod
    def insert(root: Optional['TreeNode'], value: Any, parent_value: Any = None, 
               direction: str = 'auto') -> Tuple[Optional['TreeNode'], Optional['TreeNode'], bool, str]:
        """
        在二叉树中插入新节点
        
        参数:
            root: 树的根节点
            value: 要插入的值
            parent_value: 父节点的值 (如果为 None，则自动找第一个空位)
            direction: 'left', 'right', 或 'auto' (自动选择空位)
        
        返回:
            - 新的根节点
            - 新插入的节点
            - 是否成功
            - 消息说明
        """
        new_node = TreeNode(value)
        
        # 如果树为空，新节点成为根节点
        if not root:
            return new_node, new_node, True, f"创建根节点 {value}"
        
        # 如果指定了父节点
        if parent_value is not None:
            # 找到父节点
            parent, _ = BinaryTreeModel.search(root, parent_value)
            if not parent:
                return root, None, False, f"未找到父节点 {parent_value}"
            
            if direction == 'left' or direction == 'l':
                if parent.left:
                    return root, None, False, f"节点 {parent_value} 的左子节点已存在"
                parent.left = new_node
                return root, new_node, True, f"在节点 {parent_value} 的左侧插入 {value}"
            elif direction == 'right' or direction == 'r':
                if parent.right:
                    return root, None, False, f"节点 {parent_value} 的右子节点已存在"
                parent.right = new_node
                return root, new_node, True, f"在节点 {parent_value} 的右侧插入 {value}"
            else:  # auto
                if not parent.left:
                    parent.left = new_node
                    return root, new_node, True, f"在节点 {parent_value} 的左侧插入 {value}"
                elif not parent.right:
                    parent.right = new_node
                    return root, new_node, True, f"在节点 {parent_value} 的右侧插入 {value}"
                else:
                    return root, None, False, f"节点 {parent_value} 已有两个子节点"
        
        # 自动模式：BFS 找第一个空位
        queue = deque([root])
        while queue:
            node = queue.popleft()
            if not node.left:
                node.left = new_node
                return root, new_node, True, f"在节点 {node.val} 的左侧插入 {value}"
            else:
                queue.append(node.left)
            
            if not node.right:
                node.right = new_node
                return root, new_node, True, f"在节点 {node.val} 的右侧插入 {value}"
            else:
                queue.append(node.right)
        
        return root, None, False, "插入失败"

    # ============================================
    # 删除操作
    # ============================================
    @staticmethod
    def delete(root: Optional['TreeNode'], value: Any) -> Tuple[Optional['TreeNode'], bool, str, List['TreeNode']]:
        """
        从二叉树中删除指定值的节点
        
        删除策略:
        1. 叶子节点：直接删除
        2. 只有一个子节点：用子节点替换
        3. 有两个子节点：用右子树的最小节点(中序后继)替换
        
        返回:
            - 新的根节点
            - 是否成功删除
            - 消息说明
            - 受影响的节点路径
        """
        if not root:
            return None, False, "树为空", []
        
        # 找到要删除的节点及其父节点
        target, parent, direction = BinaryTreeModel.search_with_parent(root, value)
        
        if not target:
            return root, False, f"未找到值为 {value} 的节点", []
        
        affected_path = [target]
        
        # 情况1：叶子节点
        if not target.left and not target.right:
            if not parent:  # 是根节点
                return None, True, f"删除根节点 {value}，树变为空", affected_path
            
            if direction == 'left':
                parent.left = None
            else:
                parent.right = None
            affected_path.insert(0, parent)
            return root, True, f"删除叶子节点 {value}", affected_path
        
        # 情况2：只有一个子节点
        elif not target.left or not target.right:
            child = target.left if target.left else target.right
            affected_path.append(child)
            
            if not parent:  # 是根节点
                return child, True, f"删除根节点 {value}，子节点 {child.val} 成为新根", affected_path
            
            if direction == 'left':
                parent.left = child
            else:
                parent.right = child
            affected_path.insert(0, parent)
            return root, True, f"删除节点 {value}，由子节点 {child.val} 替代", affected_path
        
        # 情况3：有两个子节点 - 用中序后继替换
        else:
            # 找中序后继（右子树的最左节点）
            successor_parent = target
            successor = target.right
            affected_path.append(successor)
            
            while successor.left:
                successor_parent = successor
                successor = successor.left
                affected_path.append(successor)
            
            # 保存后继节点的值
            successor_val = successor.val
            
            # 删除后继节点（后继节点最多只有右子节点）
            if successor_parent == target:
                successor_parent.right = successor.right
            else:
                successor_parent.left = successor.right
            
            # 用后继节点的值替换目标节点的值
            target.val = successor_val
            
            return root, True, f"删除节点 {value}，由中序后继 {successor_val} 替代", affected_path

    # ============================================
    # 辅助方法
    # ============================================
    @staticmethod
    def get_all_nodes(root: Optional['TreeNode']) -> List['TreeNode']:
        """获取所有节点（层序遍历）"""
        if not root:
            return []
        
        nodes = []
        queue = deque([root])
        while queue:
            node = queue.popleft()
            nodes.append(node)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        return nodes

    @staticmethod
    def find_node_path(root: Optional['TreeNode'], value: Any) -> List['TreeNode']:
        """
        找到从根节点到目标节点的路径
        """
        if not root:
            return []
        
        def dfs(node: TreeNode, path: List[TreeNode]) -> Optional[List[TreeNode]]:
            if not node:
                return None
            
            path.append(node)
            
            if str(node.val) == str(value):
                return path.copy()
            
            left_result = dfs(node.left, path)
            if left_result:
                return left_result
            
            right_result = dfs(node.right, path)
            if right_result:
                return right_result
            
            path.pop()
            return None
        
        result = dfs(root, [])
        return result if result else []