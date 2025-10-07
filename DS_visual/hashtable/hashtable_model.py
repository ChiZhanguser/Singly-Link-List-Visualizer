from typing import List, Optional, Any
TOMBSTONE = object()

class HashTableModel:
    def __init__(self, capacity: int = 11):
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self.capacity = capacity
        self.table: List[Optional[Any]] = [None] * capacity
        self.tombstone = TOMBSTONE

    def _hash(self, x: Any) -> int:
        try:
            xi = int(x)
        except Exception:
            xi = hash(x)
        return int(xi) % self.capacity

    def find(self, x: Any) -> int:
        """查找值 x，若找到返回索引，否则返回 -1。探测到空位（None）则可终止。"""
        start = self._hash(x)
        i = start
        first_pass = True
        while True:
            val = self.table[i]
            if val is None:
                return -1  # 直接遇到空位 => 不存在
            if val is not self.tombstone and val == x:
                return i
            i = (i + 1) % self.capacity
            if i == start:
                break
        return -1

    def insert(self, x: Any) -> Optional[int]:
        if self.find(x) != -1:
            return self.find(x)

        start = self._hash(x)
        i = start
        first_tombstone = -1
        while True:
            val = self.table[i]
            if val is None:
                # 如果之前遇到 tombstone，优先放在那里
                target = first_tombstone if first_tombstone != -1 else i
                self.table[target] = x
                return target
            if val is self.tombstone:
                if first_tombstone == -1:
                    first_tombstone = i
            # 否则被占用，继续线性探测
            i = (i + 1) % self.capacity
            if i == start:
                break
        # 全表探测一圈仍未找到空位
        if first_tombstone != -1:
            self.table[first_tombstone] = x
            return first_tombstone
        return None

    def delete(self, x: Any) -> Optional[int]:
        """删除 x（用 tombstone 标记）。若不存在返回 None；否则返回被删除的索引。"""
        idx = self.find(x)
        if idx == -1:
            return None
        self.table[idx] = self.tombstone
        return idx

    def clear(self):
        """完全清空表（把 tombstone 都清除为 None）"""
        self.table = [None] * self.capacity

    def __len__(self):
        # 统计实际存储的元素（不计 tombstone）
        return sum(1 for v in self.table if v is not None and v is not self.tombstone)

    def load_list(self, items: List[Any]):
        """按顺序批量清空并插入 items（用于批量构建）"""
        self.clear()
        for x in items:
            self.insert(x)

    def __repr__(self):
        return f"HashTableModel(capacity={self.capacity}, table={self.table})"
