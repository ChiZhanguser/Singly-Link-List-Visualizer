from typing import List, Any, Optional, Tuple

class StackModel:
    def __init__(self, capacity: int = 10, auto_expand: bool = True, expand_factor: float = 2.0):
        """
        初始化栈模型
        
        Args:
            capacity: 初始容量
            auto_expand: 是否支持自动扩容
            expand_factor: 扩容因子（每次扩容后容量变为原来的多少倍）
        """
        self.data: List[Any] = []
        self.capacity = capacity
        self.top = -1  # 栈顶指针，初始为-1表示空栈
        self.auto_expand = auto_expand
        self.expand_factor = expand_factor
        self._expansion_history: List[Tuple[int, int]] = []  # 记录扩容历史 (旧容量, 新容量)

    def is_empty(self) -> bool:
        return self.top == -1

    def is_full(self) -> bool:
        return self.top == self.capacity - 1

    def _expand(self) -> Tuple[int, int]:
        """
        扩容操作
        Returns:
            (旧容量, 新容量) 元组
        """
        old_capacity = self.capacity
        new_capacity = int(self.capacity * self.expand_factor)
        if new_capacity <= old_capacity:
            new_capacity = old_capacity + 1
        self.capacity = new_capacity
        self._expansion_history.append((old_capacity, new_capacity))
        return (old_capacity, new_capacity)
    

    
    def set_capacity(self, new_capacity: int) -> bool:
        """
        手动设置容量
        
        Args:
            new_capacity: 新容量（必须大于等于当前元素数量）
        Returns:
            是否设置成功
        """
        if new_capacity < len(self.data):
            return False
        old_capacity = self.capacity
        self.capacity = new_capacity
        if new_capacity != old_capacity:
            self._expansion_history.append((old_capacity, new_capacity))
        return True

    def push(self, value: Any, force_expand: bool = False) -> Tuple[bool, Optional[Tuple[int, int]]]:
        """
        入栈操作
        
        Args:
            value: 要入栈的值
            force_expand: 是否强制扩容（即使auto_expand为False）
        Returns:
            (是否成功, 扩容信息或None) 元组
        """
        expansion_info = None
        if self.is_full():
            if self.auto_expand or force_expand:
                expansion_info = self._expand()
            else:
                return (False, None)
        self.data.append(value)
        self.top += 1
        return (True, expansion_info)

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

    def get_expansion_history(self) -> List[Tuple[int, int]]:
        """获取扩容历史"""
        return self._expansion_history.copy()
    
    def clear_expansion_history(self) -> None:
        """清空扩容历史"""
        self._expansion_history.clear()

    def __len__(self) -> int:
        return len(self.data)

    def __repr__(self) -> str:
        return f"Stack(top={self.top}, capacity={self.capacity}, auto_expand={self.auto_expand}, data={self.data})"