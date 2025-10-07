# bplustree_model.py
from typing import List, Optional, Dict, Tuple, Any
import math

class BPlusNode:
    def __init__(self, is_leaf: bool = False):
        self.is_leaf: bool = is_leaf
        self.keys: List[Any] = []
        self.children: List['BPlusNode'] = []  # for internal nodes: children pointers
        self.parent: Optional['BPlusNode'] = None
        self.next: Optional['BPlusNode'] = None  # for leaf node linked list

    def __repr__(self):
        t = "Leaf" if self.is_leaf else "Int"
        return f"<{t}Node keys={self.keys}>"

class BPlusTree:
    def __init__(self, order: int = 4):
        """
        order: 最大子节点数（internal node 最多有 order 个 children）
        因此每个节点最多有 order-1 个 keys。
        """
        if order < 3:
            raise ValueError("order should be >= 3 for meaningful splits")
        self.order = order
        self.root = BPlusNode(is_leaf=True)

    def clear(self):
        self.root = BPlusNode(is_leaf=True)

    # --------- helper: node -> level dict for visualization ----------
    def nodes_by_level(self) -> Dict[int, List[BPlusNode]]:
        levels: Dict[int, List[BPlusNode]] = {}
        q: List[Tuple[BPlusNode,int]] = [(self.root, 0)]
        visited = set()
        while q:
            node, d = q.pop(0)
            levels.setdefault(d, []).append(node)
            if not node.is_leaf:
                for c in node.children:
                    q.append((c, d+1))
        return levels

    def leaves(self) -> List[BPlusNode]:
        # return linked list of leaves left->right
        node = self.root
        while node and not node.is_leaf:
            node = node.children[0]
        out = []
        while node:
            out.append(node)
            node = node.next
        return out

    # ---------- insertion with events for animation ----------
    def insert_with_steps(self, key) -> List[Dict]:
        """
        Insert key and return a list of 'events' for visualization.
        Events are dicts:
          {'type':'visit', 'node': node}
          {'type':'insert', 'node': leaf_node}
          {'type':'split', 'node': old_node, 'new_node': new_node, 'promoted': promoted_key, 'is_leaf':bool}
        All node objects are the actual node instances (so visualizer can map to positions).
        """
        events = []
        # 1) find leaf (record visits)
        node = self.root
        while not node.is_leaf:
            events.append({'type':'visit', 'node': node})
            # choose child: first child with key > key, else rightmost
            i = 0
            while i < len(node.keys) and key >= node.keys[i]:
                i += 1
            node = node.children[i]
        # record visit to leaf
        events.append({'type':'visit', 'node': node})

        # 2) insert into leaf's keys (sorted)
        # avoid duplicates insertion for demo: still insert duplicates (keeps multiple)
        insert_pos = 0
        while insert_pos < len(node.keys) and node.keys[insert_pos] < key:
            insert_pos += 1
        node.keys.insert(insert_pos, key)
        events.append({'type':'insert', 'node': node})

        # 3) if overflow, split and propagate upward, recording splits
        max_keys = self.order - 1
        cur = node
        while len(cur.keys) > max_keys:
            # split node 'cur'
            if cur.is_leaf:
                # leaf split: split into left and right, promote first key of right to parent
                total = len(cur.keys)
                mid = math.ceil(total / 2)
                left_keys = cur.keys[:mid]
                right_keys = cur.keys[mid:]
                new_node = BPlusNode(is_leaf=True)
                new_node.keys = right_keys
                cur.keys = left_keys
                # link list
                new_node.next = cur.next
                cur.next = new_node
                new_node.parent = cur.parent

                promoted = new_node.keys[0]
                events.append({'type':'split', 'node': cur, 'new_node': new_node, 'promoted': promoted, 'is_leaf': True})

                # attach to parent
                parent = cur.parent
                if parent is None:
                    # create new root
                    new_root = BPlusNode(is_leaf=False)
                    new_root.keys = [promoted]
                    new_root.children = [cur, new_node]
                    cur.parent = new_root
                    new_node.parent = new_root
                    self.root = new_root
                    events.append({'type':'split', 'node': new_root, 'new_node': None, 'promoted': promoted, 'is_leaf': False})
                    break
                else:
                    # insert promoted into parent at proper position
                    insert_pos = 0
                    while insert_pos < len(parent.keys) and parent.keys[insert_pos] < promoted:
                        insert_pos += 1
                    parent.keys.insert(insert_pos, promoted)
                    parent.children.insert(insert_pos+1, new_node)
                    new_node.parent = parent
                    # now continue loop up from parent
                    cur = parent
                    continue
            else:
                # internal node split
                total = len(cur.keys)
                # for internal, we choose middle key to promote
                mid_index = total // 2
                promoted = cur.keys[mid_index]
                # left keeps keys[:mid_index], right keeps keys[mid_index+1:]
                left_keys = cur.keys[:mid_index]
                right_keys = cur.keys[mid_index+1:]
                # children split correspondingly
                left_children = cur.children[:mid_index+1]
                right_children = cur.children[mid_index+1:]
                new_node = BPlusNode(is_leaf=False)
                new_node.keys = right_keys
                new_node.children = right_children
                for c in right_children:
                    c.parent = new_node
                cur.keys = left_keys
                cur.children = left_children

                parent = cur.parent
                new_node.parent = parent
                events.append({'type':'split', 'node': cur, 'new_node': new_node, 'promoted': promoted, 'is_leaf': False})

                if parent is None:
                    # create new root
                    new_root = BPlusNode(is_leaf=False)
                    new_root.keys = [promoted]
                    new_root.children = [cur, new_node]
                    cur.parent = new_root
                    new_node.parent = new_root
                    self.root = new_root
                    events.append({'type':'split', 'node': new_root, 'new_node': None, 'promoted': promoted, 'is_leaf': False})
                    break
                else:
                    # insert promoted into parent
                    insert_pos = 0
                    while insert_pos < len(parent.keys) and parent.keys[insert_pos] < promoted:
                        insert_pos += 1
                    parent.keys.insert(insert_pos, promoted)
                    parent.children.insert(insert_pos+1, new_node)
                    new_node.parent = parent
                    cur = parent
                    continue

        return events
