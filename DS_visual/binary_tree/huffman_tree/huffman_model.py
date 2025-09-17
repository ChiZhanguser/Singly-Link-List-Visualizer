# DS_visual/huffman/huffman_model.py
from typing import Any, List, Tuple, Optional
import heapq
import itertools

class HuffmanNode:
    def __init__(self, weight: float, left: 'HuffmanNode' = None, right: 'HuffmanNode' = None, label: str = ""):
        self.weight = weight
        self.left = left
        self.right = right
        self.label = label
        self.id = id(self)

    def __repr__(self):
        return f"HNode({self.weight})"

class HuffmanModel:
    def __init__(self):
        self.root: Optional[HuffmanNode] = None
        self.steps: List[Tuple[HuffmanNode, HuffmanNode, HuffmanNode]] = []

    def build_with_steps(self, weights: List[float]) -> Tuple[Optional[HuffmanNode], List[Tuple[HuffmanNode, HuffmanNode, HuffmanNode]], List[List[float]], List[List[float]]]:
        """
        构建 Huffman 树并记录每一步。
        返回 (root, steps, snapshots_before, snapshots_after)
        snapshots_before[i] 是第 i 步合并之前堆中的权值（已排序）
        snapshots_after[i] 是第 i 步合并之后堆中的权值（已排序）
        """
        self.steps = []
        snapshots_before: List[List[float]] = []
        snapshots_after: List[List[float]] = []

        if not weights:
            self.root = None
            return None, self.steps, snapshots_before, snapshots_after

        heap = []
        tie = itertools.count()
        for w in weights:
            n = HuffmanNode(weight=float(w), label=str(w))
            heapq.heappush(heap, (n.weight, next(tie), n))

        if len(heap) == 1:
            self.root = heap[0][2]
            return self.root, self.steps, snapshots_before, snapshots_after

        while len(heap) > 1:
            # 记录合并前快照（按权值排序）
            before = sorted([item[0] for item in heap])
            snapshots_before.append(before)

            w1, _, n1 = heapq.heappop(heap)
            w2, _, n2 = heapq.heappop(heap)
            parent = HuffmanNode(weight=w1 + w2, left=n1, right=n2, label=str(w1 + w2))
            self.steps.append((n1, n2, parent))
            heapq.heappush(heap, (parent.weight, next(tie), parent))

            # 记录合并后快照
            after = sorted([item[0] for item in heap])
            snapshots_after.append(after)

        self.root = heap[0][2]
        return self.root, self.steps, snapshots_before, snapshots_after
