from typing import Dict, List, Tuple, Optional

class TrieNode:
    def __init__(self, char: str = ""):
        self.char: str = char
        self.children: Dict[str, 'TrieNode'] = {}
        self.is_end: bool = False
        self.parent: Optional['TrieNode'] = None  

    def __repr__(self):
        return f"TrieNode('{self.char}', end={self.is_end})"


class TrieModel:
    """
      - insert(word) -> 返回插入时访问/创建的节点路径（从 root 开始，不包含虚拟 root 的 char）
      - search(word) -> (found: bool, path: List[TrieNode])  path 为访问到的节点列表（不包括 root）
      - clear() -> 重置 trie
    """
    def __init__(self):
        self.root = TrieNode("")  # root 不显示字符

    def insert(self, word: str) -> List[TrieNode]:
        """
        插入单词（小写/大小写不做强制转换，按传入处理）
        返回路径（节点列表），从首字母对应节点开始（不返回 root）
        """
        cur = self.root
        path: List[TrieNode] = []
        for ch in word:
            if ch not in cur.children:
                node = TrieNode(ch)
                node.parent = cur
                cur.children[ch] = node
            cur = cur.children[ch]
            path.append(cur)
        cur.is_end = True
        return path

    def search(self, word: str) -> Tuple[bool, List[TrieNode]]:
        """
        查找单词（完全匹配），返回 (是否存在, 访问路径)
        path 中不包含 root（从第一个字符对应节点开始）
        """
        cur = self.root
        path: List[TrieNode] = []
        for ch in word:
            if ch not in cur.children:
                return False, path
            cur = cur.children[ch]
            path.append(cur)
        return cur.is_end, path

    def clear(self) -> None:
        """清空 trie"""
        self.root = TrieNode("")

    def collect_all_nodes(self) -> List[TrieNode]:
        """
        返回 trie 中所有节点（不包含 root）——用于绘图布局。
        顺序为按层 BFS 遍历。
        """
        out: List[TrieNode] = []
        q: List[TrieNode] = []
        for cnode in self.root.children.values():
            q.append(cnode)
        while q:
            node = q.pop(0)
            out.append(node)
            for ch, child in node.children.items():
                q.append(child)
        return out

    def nodes_by_level(self) -> Dict[int, List[TrieNode]]:
        """
        按深度返回节点字典（深度从 1 开始，root 为 0）。
        方便在可视化中按层均匀分布。
        """
        levels: Dict[int, List[TrieNode]] = {}
        q: List[Tuple[TrieNode,int]] = []
        for c in self.root.children.values():
            q.append((c, 1))
        while q:
            node, d = q.pop(0)
            levels.setdefault(d, []).append(node)
            for child in node.children.values():
                q.append((child, d+1))
        return levels
