from typing import List, Any, Optional

class LinkedListModel:
    def __init__(self):
        self.node_value_store: List[Any] = []

    def to_list(self) -> List[Any]:
        return list(self.node_value_store)

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
        # position 1-based: insert after position -> insert at index position
        if position < 1 or position > len(self.node_value_store):
            raise IndexError("position out of range")
        self.node_value_store.insert(position, value)

    def delete_first(self) -> None:
        if not self.node_value_store:
            raise IndexError("delete from empty list")
        self.node_value_store.pop(0)

    def delete_last(self) -> None:
        if not self.node_value_store:
            raise IndexError("delete from empty list")
        self.node_value_store.pop()
