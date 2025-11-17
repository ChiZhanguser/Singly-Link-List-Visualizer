from typing import List, Any, Tuple

class SequenceListModel:
    def __init__(self, capacity: int = 11):
        """
        capacity: 初始容量（固定容量），当需要更多空间时按规则扩容：
                  capacity = capacity * 2 - 1
        """
        self.data: List[Any] = []
        self.capacity: int = max(1, int(capacity))

    def to_list(self) -> List[Any]:
        return list(self.data)

    def clear(self) -> None:
        self.data.clear()

    def append(self, value: Any) -> None:
        # 确保容量再追加
        self.ensure_capacity_for(len(self.data) + 1)
        self.data.append(value)

    def pop(self, idx: int = -1) -> Any:
        return self.data.pop(idx)

    def insert(self, idx: int, value: Any) -> None:
        # idx 是 0-based
        self.ensure_capacity_for(len(self.data) + 1)
        self.data.insert(idx, value)

    def __len__(self) -> int:
        return len(self.data)

    def __repr__(self) -> str:
        return repr(self.data)

    def insert_first(self, value: Any) -> None:
        self.ensure_capacity_for(len(self.data) + 1)
        self.data.insert(0, value)

    def insert_last(self, value: Any) -> None:
        self.ensure_capacity_for(len(self.data) + 1)
        self.data.append(value)

    def insert_after(self, position: int, value: Any) -> None:
        # position 1-based: insert after position -> insert at index position
        if position < 1 or position > len(self.data):
            raise IndexError("position out of range")
        self.ensure_capacity_for(len(self.data) + 1)
        self.data.insert(position, value)

    def delete_first(self) -> None:
        if not self.data:
            raise IndexError("delete from empty list")
        self.data.pop(0)

    def delete_last(self) -> None:
        if not self.data:
            raise IndexError("delete from empty list")
        self.data.pop()

    def expand_once(self) -> Tuple[int, int]:
        """
        执行一次扩容操作（按规则 capacity = capacity*2 - 1）
        返回 (old_capacity, new_capacity)
        """
        old = self.capacity
        self.capacity = self.capacity * 2 - 1
        return (old, self.capacity)

    def ensure_capacity_for(self, needed: int) -> List[Tuple[int,int]]:
        """
        确保容量至少能容纳 needed 个元素。
        若不足则按规则逐次扩容，返回一个 (old,new) 列表表示每次扩容的记录（按发生顺序）。
        如果不需要扩容，返回空列表。
        """
        expansions = []
        while needed > self.capacity:
            expansions.append(self.expand_once())
        return expansions
