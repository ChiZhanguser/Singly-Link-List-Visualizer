from typing import List, Any

class SequenceListModel:
    def __init__(self):
        self.data: List[Any] = []

    def to_list(self) -> List[Any]:
        return list(self.data)

    def clear(self) -> None:
        self.data.clear()

    def append(self, value: Any) -> None:
        self.data.append(value)

    def pop(self, idx: int = -1) -> Any:
        return self.data.pop(idx)

    def insert(self, idx: int, value: Any) -> None:
        self.data.insert(idx, value)

    def __len__(self) -> int:
        return len(self.data)

    def __repr__(self) -> str:
        return repr(self.data)

    def insert_first(self, value: Any) -> None:
        self.data.insert(0, value)

    def insert_last(self, value: Any) -> None:
        self.data.append(value)

    def insert_after(self, position: int, value: Any) -> None:
        # position 1-based: insert after position -> insert at index position
        if position < 1 or position > len(self.data):
            raise IndexError("position out of range")
        self.data.insert(position, value)

    def delete_first(self) -> None:
        if not self.data:
            raise IndexError("delete from empty list")
        self.data.pop(0)

    def delete_last(self) -> None:
        if not self.data:
            raise IndexError("delete from empty list")
        self.data.pop()
