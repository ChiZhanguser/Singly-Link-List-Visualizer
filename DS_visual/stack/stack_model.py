from typing import List, Any, Optional

class StackModel:
    def __init__(self, capacity: int = 10):
        self.data: List[Any] = []
        self.capacity = capacity
        self.top = -1  # 栈顶指针，初始为-1表示空栈

    def is_empty(self) -> bool:
        return self.top == -1

    def is_full(self) -> bool:
        return self.top == self.capacity - 1

    def push(self, value: Any) -> bool:
        if self.is_full():
            return False
        self.data.append(value)
        self.top += 1
        return True

    def pop(self) -> Optional[Any]:
        if self.is_empty():
            return None
        value = self.data.pop()
        self.top -= 1
        return value

    def peek(self) -> Optional[Any]:
        if self.is_empty():
            return None
        return self.data[self.top]

    def clear(self) -> None:
        self.data.clear()
        self.top = -1

    def __len__(self) -> int:
        return len(self.data)

    def __repr__(self) -> str:
        return f"Stack(top={self.top}, data={self.data})"