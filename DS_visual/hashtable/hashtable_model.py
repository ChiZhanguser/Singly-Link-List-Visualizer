from typing import List, Optional, Any, Tuple
from dataclasses import dataclass

TOMBSTONE = object()

@dataclass
class ProbeResult:
    """探测结果，包含探测路径和结果位置"""
    found: bool  # 是否找到
    target_index: Optional[int]  # 目标位置（插入位置或找到的位置）
    probe_path: List[int]  # 探测路径
    is_full: bool = False  # 表是否已满

class HashTableModel:
    def __init__(self, capacity: int = 11):
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self.capacity = capacity
        self.table: List[Optional[Any]] = [None] * capacity
        self.tombstone = TOMBSTONE
        self.size = 0  # 有效元素计数（不含墓碑）

    def _hash(self, x: Any) -> int:
        """计算元素的哈希值"""
        try:
            xi = int(x)
        except (ValueError, TypeError):
            xi = hash(str(x))
        return abs(xi) % self.capacity

    def _probe_find(self, x: Any) -> ProbeResult:
        """查找元素，返回探测结果"""
        start = self._hash(x)
        probe_path = []
        i = start

        while True:
            probe_path.append(i)
            val = self.table[i]
            
            if val is None:
                return ProbeResult(False, -1, probe_path)
            
            if val is not self.tombstone and val == x:
                return ProbeResult(True, i, probe_path)
            
            i = (i + 1) % self.capacity
            if i == start:
                break
        
        return ProbeResult(False, -1, probe_path)

    def _probe_insert(self, x: Any) -> ProbeResult:
        """探测插入位置，返回探测结果"""
        # 先尝试查找是否存在
        find_result = self._probe_find(x)
        if find_result.found:
            return find_result

        # 开始插入探测
        start = self._hash(x)
        probe_path = []
        i = start
        first_tombstone = -1

        while True:
            probe_path.append(i)
            val = self.table[i]
            
            if val is None:
                # 找到空位
                target = first_tombstone if first_tombstone != -1 else i
                return ProbeResult(False, target, probe_path)
            
            if val is self.tombstone and first_tombstone == -1:
                first_tombstone = i
            
            i = (i + 1) % self.capacity
            if i == start:
                break

        # 表满，但有墓碑可用
        if first_tombstone != -1:
            return ProbeResult(False, first_tombstone, probe_path)
            
        # 表完全满
        return ProbeResult(False, None, probe_path, is_full=True)

    def find(self, x: Any) -> Tuple[bool, List[int]]:
        """查找元素，返回 (是否找到, 探测路径)"""
        result = self._probe_find(x)
        return result.found, result.probe_path

    def insert(self, x: Any) -> Tuple[Optional[int], List[int], bool]:
        """插入元素，返回 (插入位置, 探测路径, 是否表满)"""
        result = self._probe_insert(x)
        if result.target_index is not None:
            if not result.found:  # 新插入而不是找到已存在
                self.table[result.target_index] = x
                self.size += 1
        return result.target_index, result.probe_path, result.is_full

    def delete(self, x: Any) -> Tuple[Optional[int], List[int]]:
        """删除元素，返回 (删除位置, 探测路径)"""
        result = self._probe_find(x)
        if result.found:
            self.table[result.target_index] = self.tombstone
            self.size -= 1
            return result.target_index, result.probe_path
        return None, result.probe_path

    def clear(self):
        """清空哈希表"""
        self.table = [None] * self.capacity
        self.size = 0

    def __len__(self):
        """返回有效元素数量（不含墓碑）"""
        return self.size

    def load_list(self, items: List[Any]):
        """批量加载元素列表"""
        self.clear()
        for x in items:
            self.insert(x)

    def get_load_factor(self) -> float:
        """返回负载因子（有效元素/容量）"""
        return self.size / self.capacity
    def resize(self, new_capacity: int):
        """调整散列表容量"""
        if new_capacity <= 0:
            raise ValueError("capacity must be positive")
        if new_capacity < self.size:
            raise ValueError(f"new capacity ({new_capacity}) cannot be less than current size ({self.size})")
        
        # 保存当前有效元素（排除None和墓碑）
        old_table = self.table
        old_capacity = self.capacity
        
        # 创建新表
        self.capacity = new_capacity
        self.table = [None] * new_capacity
        self.size = 0
        
        # 重新插入所有有效元素
        for item in old_table:
            if item is not None and item is not self.tombstone:
                self.insert(item)

    def __repr__(self):
        return f"HashTableModel(capacity={self.capacity}, size={self.size}, table={self.table})"
