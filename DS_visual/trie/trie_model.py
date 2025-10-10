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
    def __init__(self):
        self.root = TrieNode("")  # root 不显示字符

    def insert(self, word: str) -> List[TrieNode]:
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
