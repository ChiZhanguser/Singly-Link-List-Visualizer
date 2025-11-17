from typing import Any, Iterable, Iterator, Optional

class _Node:
    __slots__ = ("value", "next")
    def __init__(self, value: Any):
        self.value: Any = value
        self.next: Optional["_Node"] = None

class _NodeList:
    def __init__(self, iterable: Optional[Iterable[Any]] = None):
        self.head: Optional[_Node] = None
        self._size: int = 0
        if iterable:
            for v in iterable:
                self.append(v)

    def __len__(self) -> int:
        return self._size

    def __iter__(self) -> Iterator[Any]:
        cur = self.head
        while cur:
            yield cur.value
            cur = cur.next

    def to_list(self) -> list:
        out = []
        cur = self.head
        while cur:
            out.append(cur.value)
            cur = cur.next
        return out

    def __repr__(self) -> str:
        return repr(self.to_list())

    def clear(self) -> None:
        self.head = None
        self._size = 0

    def append(self, value: Any) -> None:
        new = _Node(value)
        if not self.head:
            self.head = new
        else:
            cur = self.head
            while cur.next:
                cur = cur.next
            cur.next = new
        self._size += 1

    def _node_at(self, idx: int) -> _Node:
        n = self._size
        if idx < 0:
            idx += n
        if idx < 0 or idx >= n:
            raise IndexError("index out of range")
        cur = self.head
        for _ in range(idx):
            cur = cur.next  
        return cur  

    def __getitem__(self, idx: int) -> Any:
        node = self._node_at(idx)
        return node.value

    def __setitem__(self, idx: int, value: Any) -> None:
        node = self._node_at(idx)
        node.value = value

    def pop(self, idx: int = -1) -> Any:
        if self._size == 0:
            raise IndexError("pop from empty list")
        n = self._size
        if idx < 0:
            idx += n
        if idx < 0 or idx >= n:
            raise IndexError("pop index out of range")
        if idx == 0:
            node = self.head
            assert node is not None
            self.head = node.next
            node.next = None
            self._size -= 1
            return node.value
        prev = self._node_at(idx - 1)
        assert prev.next is not None
        node = prev.next
        prev.next = node.next
        node.next = None
        self._size -= 1
        return node.value

    def insert(self, idx: int, value: Any) -> None:
        if idx <= 0:
            new = _Node(value)
            new.next = self.head
            self.head = new
            self._size += 1
            return
        if idx >= self._size:
            self.append(value)
            return
        prev = self._node_at(idx - 1)
        new = _Node(value)
        new.next = prev.next
        prev.next = new
        self._size += 1

class LinkedListModel:
    def __init__(self):
        self.node_value_store: _NodeList = _NodeList()

    def to_list(self):
        return self.node_value_store.to_list()

    def clear(self) -> None:
        self.node_value_store.clear()

    def append(self, value: Any) -> None:
        self.node_value_store.append(value)

    def pop(self, idx: int = -1) -> Any:
        return self.node_value_store.pop(idx)

    def insert(self, idx: int, value: Any) -> None:
        self.node_value_store.insert(idx, value)

    def __len__(self) -> int:
        return len(self.node_value_store)

    def __repr__(self) -> str:
        return repr(self.node_value_store)

    def insert_first(self, value: Any) -> None:
        self.node_value_store.insert(0, value)

    def insert_last(self, value: Any) -> None:
        self.node_value_store.append(value)

    def insert_after(self, position: int, value: Any) -> None:
        # position 为 1-based：在 position 后插入 -> 在 index position 处插入
        if position < 1 or position > len(self.node_value_store):
            raise IndexError("position out of range")
        self.node_value_store.insert(position, value)

    def delete_first(self) -> None:
        if len(self.node_value_store) == 0:
            raise IndexError("delete from empty list")
        self.node_value_store.pop(0)

    def delete_last(self) -> None:
        if len(self.node_value_store) == 0:
            raise IndexError("delete from empty list")
        self.node_value_store.pop()

    def delete_at_position(self, pos):
        """删除指定位置的节点"""
        if pos < 1 or pos > len(self.node_value_store):
            raise IndexError("position out of range")
        self.node_value_store.pop(pos-1)