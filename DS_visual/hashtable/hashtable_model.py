# hashtable/hashtable_model.py
from typing import Any, List, Optional, Tuple, Iterator

_TOMBSTONE = object()

class HashTable:
    """
    线性探测哈希表（带墓碑）。hash -> (hash(key) & 0x7fffffff) % capacity
    支持自动扩容（按 load_factor）。
    """
    def __init__(self, capacity: int = 11, load_factor: float = 0.6, auto_resize: bool = True):
        self.capacity = max(3, int(capacity))
        self.keys: List[Optional[Any]] = [None] * self.capacity
        self.values: List[Optional[Any]] = [None] * self.capacity
        self.size = 0
        self.tombstones = 0
        self.load_factor = float(load_factor)
        self.auto_resize = bool(auto_resize)

    def _hash(self, key: Any) -> int:
        return (hash(key) & 0x7fffffff) % self.capacity

    def _probe(self, start: int) -> Iterator[int]:
        i = start
        while True:
            yield i
            i += 1
            if i >= self.capacity:
                i = 0

    def _need_grow(self) -> bool:
        return self.auto_resize and (self.size + self.tombstones) / self.capacity > self.load_factor

    def _grow(self):
        items = list(self.items())
        newcap = max(3, self.capacity * 2)
        self.capacity = newcap
        self.keys = [None] * self.capacity
        self.values = [None] * self.capacity
        self.size = 0
        self.tombstones = 0
        for k, v in items:
            self.put(k, v, allow_grow=False)

    def _find_slot(self, key: Any) -> Tuple[Optional[int], Optional[int]]:
        """返回 (found_idx, insert_idx). found_idx 若存在; insert_idx 为可插入位置"""
        h = self._hash(key)
        first_tomb = None
        for idx in self._probe(h):
            k = self.keys[idx]
            if k is None:
                return (None, first_tomb if first_tomb is not None else idx)
            if k is _TOMBSTONE:
                if first_tomb is None:
                    first_tomb = idx
            elif k == key:
                return (idx, idx)
        return (None, None)

    def put(self, key: Any, value: Any, allow_grow: bool = True) -> bool:
        if allow_grow and self._need_grow():
            self._grow()
        found, insert = self._find_slot(key)
        if found is not None:
            self.values[found] = value
            return True
        if insert is None:
            return False
        if self.keys[insert] is _TOMBSTONE:
            self.tombstones -= 1
        self.keys[insert] = key
        self.values[insert] = value
        self.size += 1
        return True

    def get(self, key: Any) -> Optional[Any]:
        h = self._hash(key)
        for idx in self._probe(h):
            k = self.keys[idx]
            if k is None:
                return None
            if k is _TOMBSTONE:
                continue
            if k == key:
                return self.values[idx]
        return None

    def remove(self, key: Any) -> bool:
        h = self._hash(key)
        for idx in self._probe(h):
            k = self.keys[idx]
            if k is None:
                return False
            if k is _TOMBSTONE:
                continue
            if k == key:
                self.keys[idx] = _TOMBSTONE
                self.values[idx] = None
                self.size -= 1
                self.tombstones += 1
                return True
        return False

    def contains(self, key: Any) -> bool:
        return self.get(key) is not None

    def clear(self):
        self.keys = [None] * self.capacity
        self.values = [None] * self.capacity
        self.size = 0
        self.tombstones = 0

    def items(self):
        for k, v in zip(self.keys, self.values):
            if k is not None and k is not _TOMBSTONE:
                yield (k, v)

    def __len__(self) -> int:
        return self.size

    def is_empty(self) -> bool:
        return self.size == 0

    def is_full(self) -> bool:
        return self.size + self.tombstones >= self.capacity and not self.auto_resize

    def __repr__(self) -> str:
        pairs = ", ".join(f"{k}:{v}" for k, v in self.items())
        return f"<HashTable cap={self.capacity} size={self.size} [{pairs}]>"
