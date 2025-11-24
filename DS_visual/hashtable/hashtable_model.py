from typing import List, Optional, Any, Tuple, Union, Callable
from dataclasses import dataclass
from enum import Enum

TOMBSTONE = object()

class CollisionMethod(Enum):
    """冲突处理方法"""
    OPEN_ADDRESSING = "open_addressing"  # 开放寻址法
    CHAINING = "chaining"  # 拉链法

@dataclass
class ProbeResult:
    """探测结果，包含探测路径和结果位置"""
    found: bool  # 是否找到
    target_index: Optional[int]  # 目标位置（插入位置或找到的位置）
    probe_path: List[int]  # 探测路径
    is_full: bool = False  # 表是否已满
    chain_position: Optional[int] = None  # 在链表中的位置（仅拉链法）

class HashTableModel:
    def __init__(self, capacity: int = 11, method: CollisionMethod = CollisionMethod.OPEN_ADDRESSING, 
                 hash_func: Optional[Callable[[Any], int]] = None):
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self.capacity = capacity
        self.method = method
        self.tombstone = TOMBSTONE
        self.size = 0  # 有效元素计数
        
        # 设置哈希函数
        if hash_func is None:
            self.hash_func = self._default_hash
        else:
            self.hash_func = hash_func
        
        if method == CollisionMethod.OPEN_ADDRESSING:
            self.table: List[Optional[Any]] = [None] * capacity
        else:  # CHAINING
            self.table: List[List[Any]] = [[] for _ in range(capacity)]

    def _default_hash(self, x: Any) -> int:
        """默认哈希函数"""
        try:
            xi = int(x)
        except (ValueError, TypeError):
            xi = hash(str(x))
        return abs(xi) % self.capacity

    def _hash(self, x: Any) -> int:
        """计算元素的哈希值"""
        return self.hash_func(x)

    # ==================== 开放寻址法 ====================
    def _probe_find_open(self, x: Any) -> ProbeResult:
        """开放寻址法：查找元素"""
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

    def _probe_insert_open(self, x: Any) -> ProbeResult:
        """开放寻址法：探测插入位置"""
        find_result = self._probe_find_open(x)
        if find_result.found:
            return find_result

        start = self._hash(x)
        probe_path = []
        i = start
        first_tombstone = -1

        while True:
            probe_path.append(i)
            val = self.table[i]
            
            if val is None:
                target = first_tombstone if first_tombstone != -1 else i
                return ProbeResult(False, target, probe_path)
            
            if val is self.tombstone and first_tombstone == -1:
                first_tombstone = i
            
            i = (i + 1) % self.capacity
            if i == start:
                break

        if first_tombstone != -1:
            return ProbeResult(False, first_tombstone, probe_path)
            
        return ProbeResult(False, None, probe_path, is_full=True)

    # ==================== 拉链法 ====================
    def _probe_find_chain(self, x: Any) -> ProbeResult:
        """拉链法：查找元素"""
        idx = self._hash(x)
        probe_path = [idx]
        chain = self.table[idx]
        
        for pos, val in enumerate(chain):
            if val == x:
                return ProbeResult(True, idx, probe_path, chain_position=pos)
        
        return ProbeResult(False, idx, probe_path)

    def _probe_insert_chain(self, x: Any) -> ProbeResult:
        """拉链法：探测插入位置"""
        idx = self._hash(x)
        probe_path = [idx]
        chain = self.table[idx]
        
        # 检查是否已存在
        for pos, val in enumerate(chain):
            if val == x:
                return ProbeResult(True, idx, probe_path, chain_position=pos)
        
        # 不存在，返回插入位置
        return ProbeResult(False, idx, probe_path, chain_position=len(chain))

    # ==================== 统一接口 ====================
    def find(self, x: Any) -> Tuple[bool, List[int], Optional[int]]:
        """查找元素，返回 (是否找到, 探测路径, 链表位置)"""
        if self.method == CollisionMethod.OPEN_ADDRESSING:
            result = self._probe_find_open(x)
            return result.found, result.probe_path, None
        else:
            result = self._probe_find_chain(x)
            return result.found, result.probe_path, result.chain_position

    def insert(self, x: Any) -> Tuple[Optional[int], List[int], bool, Optional[int]]:
        """插入元素，返回 (插入位置, 探测路径, 是否表满, 链表位置)"""
        if self.method == CollisionMethod.OPEN_ADDRESSING:
            result = self._probe_insert_open(x)
            if result.target_index is not None and not result.found:
                self.table[result.target_index] = x
                self.size += 1
            return result.target_index, result.probe_path, result.is_full, None
        else:
            result = self._probe_insert_chain(x)
            if not result.found:
                self.table[result.target_index].append(x)
                self.size += 1
            return result.target_index, result.probe_path, False, result.chain_position

    def delete(self, x: Any) -> Tuple[Optional[int], List[int], Optional[int]]:
        """删除元素，返回 (删除位置, 探测路径, 链表位置)"""
        if self.method == CollisionMethod.OPEN_ADDRESSING:
            result = self._probe_find_open(x)
            if result.found:
                self.table[result.target_index] = self.tombstone
                self.size -= 1
                return result.target_index, result.probe_path, None
            return None, result.probe_path, None
        else:
            result = self._probe_find_chain(x)
            if result.found:
                self.table[result.target_index].pop(result.chain_position)
                self.size -= 1
                return result.target_index, result.probe_path, result.chain_position
            return None, result.probe_path, None

    def clear(self):
        """清空哈希表"""
        if self.method == CollisionMethod.OPEN_ADDRESSING:
            self.table = [None] * self.capacity
        else:
            self.table = [[] for _ in range(self.capacity)]
        self.size = 0

    def __len__(self):
        """返回有效元素数量"""
        return self.size

    def load_list(self, items: List[Any]):
        """批量加载元素列表"""
        self.clear()
        for x in items:
            self.insert(x)

    def get_load_factor(self) -> float:
        """返回负载因子"""
        return self.size / self.capacity

    def resize(self, new_capacity: int):
        """调整散列表容量"""
        if new_capacity <= 0:
            raise ValueError("capacity must be positive")
        if self.method == CollisionMethod.OPEN_ADDRESSING and new_capacity < self.size:
            raise ValueError(f"new capacity ({new_capacity}) cannot be less than current size ({self.size})")
        
        # 保存当前有效元素
        old_table = self.table
        old_capacity = self.capacity
        
        # 创建新表
        self.capacity = new_capacity
        if self.method == CollisionMethod.OPEN_ADDRESSING:
            self.table = [None] * new_capacity
        else:
            self.table = [[] for _ in range(new_capacity)]
        self.size = 0
        
        # 重新插入所有有效元素
        if self.method == CollisionMethod.OPEN_ADDRESSING:
            for item in old_table:
                if item is not None and item is not self.tombstone:
                    self.insert(item)
        else:
            for chain in old_table:
                for item in chain:
                    self.insert(item)

    def get_chain_length(self, index: int) -> int:
        """获取指定索引处的链长度（仅拉链法）"""
        if self.method == CollisionMethod.CHAINING:
            return len(self.table[index])
        return 0

    def get_max_chain_length(self) -> int:
        """获取最大链长度（仅拉链法）"""
        if self.method == CollisionMethod.CHAINING:
            return max(len(chain) for chain in self.table) if self.table else 0
        return 0

    def __repr__(self):
        return f"HashTableModel(capacity={self.capacity}, size={self.size}, method={self.method.value}, table={self.table})"