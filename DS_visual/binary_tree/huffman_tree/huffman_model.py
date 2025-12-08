from typing import Any, List, Tuple, Optional, Dict
import heapq
import itertools

class HuffmanNode:
    def __init__(self, weight: float, left: 'HuffmanNode' = None, right: 'HuffmanNode' = None, label: str = ""):
        self.weight = weight
        self.left = left
        self.right = right
        self.label = label
        self.id = id(self)

    def __repr__(self):
        return f"HNode({self.weight})"


class HeapOperation:
    """记录堆操作的类"""
    def __init__(self, op_type: str, index: int, value: float, 
                 swap_with: int = -1, heap_state: List[float] = None,
                 description: str = ""):
        self.op_type = op_type  # 'insert', 'extract', 'sift_up', 'sift_down', 'swap', 'compare'
        self.index = index       # 操作涉及的索引
        self.value = value       # 操作涉及的值
        self.swap_with = swap_with  # 交换的目标索引 (-1 表示无交换)
        self.heap_state = heap_state.copy() if heap_state else []  # 当前堆状态快照
        self.description = description  # 操作描述
    
    def __repr__(self):
        return f"HeapOp({self.op_type}, idx={self.index}, val={self.value})"


class MinHeapWithSteps:
    """
    带有步骤记录的最小堆实现
    用于可视化展示堆的上浮(sift-up)和下沉(sift-down)过程
    """
    def __init__(self):
        self.heap: List[Tuple[float, int, Any]] = []  # (weight, tie_breaker, node)
        self.tie_counter = itertools.count()
        self.operations: List[HeapOperation] = []  # 记录所有操作
    
    def _get_weights(self) -> List[float]:
        """获取当前堆中所有权值"""
        return [item[0] for item in self.heap]
    
    def _record(self, op_type: str, index: int, value: float, 
                swap_with: int = -1, description: str = ""):
        """记录一次操作"""
        self.operations.append(HeapOperation(
            op_type=op_type,
            index=index,
            value=value,
            swap_with=swap_with,
            heap_state=self._get_weights(),
            description=description
        ))
    
    def push(self, weight: float, node: Any) -> List[HeapOperation]:
        """
        插入元素并返回此次插入的所有操作步骤
        包括: 插入到末尾 + 上浮过程
        """
        start_idx = len(self.operations)
        tie = next(self.tie_counter)
        
        # 1. 将新元素添加到堆末尾
        self.heap.append((weight, tie, node))
        insert_idx = len(self.heap) - 1
        self._record('insert', insert_idx, weight, 
                    description=f"将 {weight:.0f} 插入到堆的位置 {insert_idx}")
        
        # 2. 执行上浮 (sift-up)
        self._sift_up(insert_idx)
        
        return self.operations[start_idx:]
    
    def _sift_up(self, idx: int):
        """上浮操作: 将指定索引的元素向上调整到正确位置"""
        while idx > 0:
            parent_idx = (idx - 1) // 2
            
            # 记录比较操作
            self._record('compare', idx, self.heap[idx][0], parent_idx,
                        description=f"比较: 节点[{idx}]={self.heap[idx][0]:.0f} 与 父节点[{parent_idx}]={self.heap[parent_idx][0]:.0f}")
            
            if self.heap[idx][0] < self.heap[parent_idx][0]:
                # 需要交换
                self._record('sift_up', idx, self.heap[idx][0], parent_idx,
                            description=f"上浮: {self.heap[idx][0]:.0f} < {self.heap[parent_idx][0]:.0f}, 交换位置")
                
                self.heap[idx], self.heap[parent_idx] = self.heap[parent_idx], self.heap[idx]
                
                self._record('swap', parent_idx, self.heap[parent_idx][0], idx,
                            description=f"交换完成: 位置 {idx} ↔ 位置 {parent_idx}")
                
                idx = parent_idx
            else:
                # 不需要交换,上浮结束
                self._record('sift_up_done', idx, self.heap[idx][0],
                            description=f"上浮完成: {self.heap[idx][0]:.0f} ≥ 父节点, 停止")
                break
        else:
            if idx == 0:
                self._record('sift_up_done', 0, self.heap[0][0],
                            description=f"上浮完成: 已到达堆顶")
    
    def pop(self) -> Tuple[float, Any, List[HeapOperation]]:
        """
        弹出最小元素并返回此次操作的所有步骤
        包括: 取出堆顶 + 最后元素移到堆顶 + 下沉过程
        """
        start_idx = len(self.operations)
        
        if not self.heap:
            return None, None, []
        
        # 1. 记录取出堆顶
        min_item = self.heap[0]
        self._record('extract', 0, min_item[0],
                    description=f"取出堆顶最小元素: {min_item[0]:.0f}")
        
        if len(self.heap) == 1:
            self.heap.pop()
            return min_item[0], min_item[2], self.operations[start_idx:]
        
        # 2. 将最后一个元素移到堆顶
        last_item = self.heap.pop()
        self.heap[0] = last_item
        self._record('move_to_top', 0, last_item[0],
                    description=f"将末尾元素 {last_item[0]:.0f} 移动到堆顶")
        
        # 3. 执行下沉 (sift-down)
        self._sift_down(0)
        
        return min_item[0], min_item[2], self.operations[start_idx:]
    
    def _sift_down(self, idx: int):
        """下沉操作: 将指定索引的元素向下调整到正确位置"""
        n = len(self.heap)
        
        while True:
            smallest = idx
            left = 2 * idx + 1
            right = 2 * idx + 2
            
            # 检查左子节点
            if left < n:
                self._record('compare', idx, self.heap[idx][0], left,
                            description=f"比较: 当前[{idx}]={self.heap[idx][0]:.0f} 与 左子[{left}]={self.heap[left][0]:.0f}")
                if self.heap[left][0] < self.heap[smallest][0]:
                    smallest = left
            
            # 检查右子节点
            if right < n:
                self._record('compare', smallest, self.heap[smallest][0], right,
                            description=f"比较: 较小者[{smallest}]={self.heap[smallest][0]:.0f} 与 右子[{right}]={self.heap[right][0]:.0f}")
                if self.heap[right][0] < self.heap[smallest][0]:
                    smallest = right
            
            if smallest != idx:
                # 需要交换
                self._record('sift_down', idx, self.heap[idx][0], smallest,
                            description=f"下沉: {self.heap[idx][0]:.0f} > 子节点 {self.heap[smallest][0]:.0f}, 交换位置")
                
                self.heap[idx], self.heap[smallest] = self.heap[smallest], self.heap[idx]
                
                self._record('swap', smallest, self.heap[smallest][0], idx,
                            description=f"交换完成: 位置 {idx} ↔ 位置 {smallest}")
                
                idx = smallest
            else:
                # 不需要交换,下沉结束
                self._record('sift_down_done', idx, self.heap[idx][0],
                            description=f"下沉完成: 当前节点 ≤ 所有子节点")
                break
    
    def __len__(self):
        return len(self.heap)
    
    def get_current_state(self) -> List[float]:
        """获取当前堆状态"""
        return self._get_weights()
    
    def clear_operations(self):
        """清除操作记录"""
        self.operations.clear()


class HuffmanModel:
    def __init__(self):
        self.root: Optional[HuffmanNode] = None
        self.steps: List[Tuple[HuffmanNode, HuffmanNode, HuffmanNode]] = []
        self.heap_operations_log: List[List[HeapOperation]] = []  # 每个阶段的堆操作
    
    def build_with_steps(self, weights: List[float]) -> Tuple[
        Optional[HuffmanNode], 
        List[Tuple[HuffmanNode, HuffmanNode, HuffmanNode]], 
        List[List[float]], 
        List[List[float]]
    ]:
        """原有的构建方法,保持向后兼容"""
        self.steps = []
        snapshots_before: List[List[float]] = []
        snapshots_after: List[List[float]] = []

        if not weights:
            self.root = None
            return None, self.steps, snapshots_before, snapshots_after

        heap = []
        tie = itertools.count()
        for w in weights:
            n = HuffmanNode(weight=float(w), label=str(w))
            heapq.heappush(heap, (n.weight, next(tie), n))

        if len(heap) == 1:
            self.root = heap[0][2]
            return self.root, self.steps, snapshots_before, snapshots_after

        while len(heap) > 1:
            # 记录合并前快照（按权值排序）
            before = sorted([item[0] for item in heap])
            snapshots_before.append(before)

            w1, _, n1 = heapq.heappop(heap)
            w2, _, n2 = heapq.heappop(heap)
            parent = HuffmanNode(weight=w1 + w2, left=n1, right=n2, label=str(w1 + w2))
            self.steps.append((n1, n2, parent))
            heapq.heappush(heap, (parent.weight, next(tie), parent))

            # 记录合并后快照
            after = sorted([item[0] for item in heap])
            snapshots_after.append(after)

        self.root = heap[0][2]
        return self.root, self.steps, snapshots_before, snapshots_after
    
    def build_with_heap_steps(self, weights: List[float]) -> Tuple[
        Optional[HuffmanNode],
        List[Tuple[HuffmanNode, HuffmanNode, HuffmanNode]],
        List[List[float]],
        List[List[float]],
        List[Dict]  # 堆操作日志
    ]:
        """
        增强版构建方法: 返回详细的堆操作步骤
        用于可视化展示每一步的堆操作
        """
        self.steps = []
        self.heap_operations_log = []
        snapshots_before: List[List[float]] = []
        snapshots_after: List[List[float]] = []

        if not weights:
            self.root = None
            return None, self.steps, snapshots_before, snapshots_after, []

        # 使用自定义的堆实现
        heap = MinHeapWithSteps()
        
        # 记录初始化阶段的所有插入操作
        init_operations = []
        for w in weights:
            n = HuffmanNode(weight=float(w), label=str(w))
            ops = heap.push(float(w), n)
            init_operations.append({
                'phase': 'init',
                'action': 'insert',
                'weight': float(w),
                'node': n,
                'operations': ops.copy()
            })
        
        heap.clear_operations()  # 清除,为后续操作准备
        
        self.heap_operations_log.append({
            'phase': 'initialization',
            'description': f'初始化: 将 {len(weights)} 个节点依次插入堆中',
            'operations': init_operations,
            'heap_state': heap.get_current_state()
        })

        if len(heap) == 1:
            self.root = heap.heap[0][2]
            return self.root, self.steps, snapshots_before, snapshots_after, self.heap_operations_log

        merge_idx = 0
        while len(heap) > 1:
            merge_log = {
                'phase': 'merge',
                'merge_index': merge_idx,
                'description': f'第 {merge_idx + 1} 次合并',
                'operations': []
            }
            
            # 记录合并前快照
            before = heap.get_current_state()
            snapshots_before.append(sorted(before))
            merge_log['before_state'] = before.copy()
            
            # 取出第一个最小元素
            heap.clear_operations()
            w1, n1, ops1 = heap.pop()
            merge_log['operations'].append({
                'action': 'extract_first',
                'weight': w1,
                'node': n1,
                'operations': [vars(op) for op in ops1],
                'heap_state_after': heap.get_current_state()
            })
            
            # 取出第二个最小元素
            heap.clear_operations()
            w2, n2, ops2 = heap.pop()
            merge_log['operations'].append({
                'action': 'extract_second',
                'weight': w2,
                'node': n2,
                'operations': [vars(op) for op in ops2],
                'heap_state_after': heap.get_current_state()
            })
            
            # 创建父节点并插入堆
            parent = HuffmanNode(weight=w1 + w2, left=n1, right=n2, label=str(w1 + w2))
            self.steps.append((n1, n2, parent))
            
            heap.clear_operations()
            ops3 = heap.push(parent.weight, parent)
            merge_log['operations'].append({
                'action': 'insert_merged',
                'weight': parent.weight,
                'node': parent,
                'operations': [vars(op) for op in ops3],
                'heap_state_after': heap.get_current_state()
            })
            
            # 记录合并后快照
            after = heap.get_current_state()
            snapshots_after.append(sorted(after))
            merge_log['after_state'] = after.copy()
            
            self.heap_operations_log.append(merge_log)
            merge_idx += 1

        self.root = heap.heap[0][2]
        return self.root, self.steps, snapshots_before, snapshots_after, self.heap_operations_log
