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
        start = self._hash(x)
        i = start
        first_pass = True
        while True:
            val = self.table[i]
            if val is None:
                return -1  
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

    def delete(self, x: Any) -> Optional[int]: #
        idx = self.find(x)
        if idx == -1:
            return None
        self.table[idx] = self.tombstone
        return idx

    def clear(self):
        self.table = [None] * self.capacity

    def __len__(self):
        return sum(1 for v in self.table if v is not None and v is not self.tombstone)

    def load_list(self, items: List[Any]):
        self.clear()
        for x in items:
            self.insert(x)

    def __repr__(self):
        return f"HashTableModel(capacity={self.capacity}, table={self.table})"
