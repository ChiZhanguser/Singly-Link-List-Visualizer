"""
有向图模型 - 用于BFS演示
Directed Graph Model for BFS Demonstration
"""
from typing import Any, List, Dict, Set, Optional, Tuple
import random


class DirectedGraph:
    """
    有向图数据结构
    使用邻接表存储
    """
    
    def __init__(self):
        self.vertices: Dict[Any, List[Any]] = {}  # 邻接表: 顶点 -> 邻居列表
        self.vertex_positions: Dict[Any, Tuple[float, float]] = {}  # 顶点位置 (用于可视化)
    
    def add_vertex(self, v: Any) -> bool:
        """添加顶点"""
        if v in self.vertices:
            return False
        self.vertices[v] = []
        return True
    
    def add_edge(self, u: Any, v: Any) -> bool:
        """添加有向边 u -> v"""
        if u not in self.vertices:
            self.add_vertex(u)
        if v not in self.vertices:
            self.add_vertex(v)
        if v not in self.vertices[u]:
            self.vertices[u].append(v)
            return True
        return False
    
    def remove_vertex(self, v: Any) -> bool:
        """删除顶点及其相关的边"""
        if v not in self.vertices:
            return False
        del self.vertices[v]
        # 删除所有指向v的边
        for u in self.vertices:
            if v in self.vertices[u]:
                self.vertices[u].remove(v)
        if v in self.vertex_positions:
            del self.vertex_positions[v]
        return True
    
    def remove_edge(self, u: Any, v: Any) -> bool:
        """删除有向边 u -> v"""
        if u not in self.vertices or v not in self.vertices[u]:
            return False
        self.vertices[u].remove(v)
        return True
    
    def get_neighbors(self, v: Any) -> List[Any]:
        """获取顶点v的所有邻居（出边指向的顶点）"""
        return self.vertices.get(v, [])
    
    def get_vertices(self) -> List[Any]:
        """获取所有顶点"""
        return list(self.vertices.keys())
    
    def get_edges(self) -> List[Tuple[Any, Any]]:
        """获取所有边"""
        edges = []
        for u in self.vertices:
            for v in self.vertices[u]:
                edges.append((u, v))
        return edges
    
    def vertex_count(self) -> int:
        """顶点数量"""
        return len(self.vertices)
    
    def edge_count(self) -> int:
        """边的数量"""
        return sum(len(neighbors) for neighbors in self.vertices.values())
    
    def has_vertex(self, v: Any) -> bool:
        """检查顶点是否存在"""
        return v in self.vertices
    
    def has_edge(self, u: Any, v: Any) -> bool:
        """检查边是否存在"""
        return u in self.vertices and v in self.vertices[u]
    
    def clear(self):
        """清空图"""
        self.vertices.clear()
        self.vertex_positions.clear()
    
    def set_position(self, v: Any, x: float, y: float):
        """设置顶点位置"""
        self.vertex_positions[v] = (x, y)
    
    def get_position(self, v: Any) -> Optional[Tuple[float, float]]:
        """获取顶点位置"""
        return self.vertex_positions.get(v)
    
    def in_degree(self, v: Any) -> int:
        """计算入度"""
        count = 0
        for u in self.vertices:
            if v in self.vertices[u]:
                count += 1
        return count
    
    def out_degree(self, v: Any) -> int:
        """计算出度"""
        return len(self.vertices.get(v, []))
    
    def to_dict(self) -> Dict:
        """序列化为字典"""
        return {
            "vertices": {str(k): [str(x) for x in v] for k, v in self.vertices.items()},
            "positions": {str(k): list(v) for k, v in self.vertex_positions.items()}
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "DirectedGraph":
        """从字典反序列化"""
        graph = cls()
        vertices = data.get("vertices", {})
        positions = data.get("positions", {})
        
        for v, neighbors in vertices.items():
            graph.vertices[v] = list(neighbors)
        
        for v, pos in positions.items():
            if len(pos) >= 2:
                graph.vertex_positions[v] = (pos[0], pos[1])
        
        return graph
    
    def __repr__(self) -> str:
        return f"DirectedGraph(V={self.vertex_count()}, E={self.edge_count()})"


def generate_random_graph(
    num_vertices: int = 6,
    edge_probability: float = 0.3,
    ensure_connected: bool = True,
    vertex_prefix: str = ""
) -> DirectedGraph:
    """
    生成随机有向图
    
    Args:
        num_vertices: 顶点数量 (3-12)
        edge_probability: 边的生成概率 (0.0-1.0)
        ensure_connected: 是否确保图是弱连通的
        vertex_prefix: 顶点名称前缀
    
    Returns:
        DirectedGraph: 随机生成的有向图
    """
    num_vertices = max(3, min(12, num_vertices))
    edge_probability = max(0.1, min(0.8, edge_probability))
    
    graph = DirectedGraph()
    
    # 创建顶点 (使用字母或数字命名)
    vertices = []
    for i in range(num_vertices):
        if vertex_prefix:
            v = f"{vertex_prefix}{i}"
        else:
            # 使用字母A, B, C...
            v = chr(ord('A') + i)
        vertices.append(v)
        graph.add_vertex(v)
    
    # 如果需要确保连通，先创建一条路径
    if ensure_connected and len(vertices) > 1:
        # 随机打乱顶点顺序
        shuffled = vertices.copy()
        random.shuffle(shuffled)
        # 创建一条路径确保弱连通
        for i in range(len(shuffled) - 1):
            graph.add_edge(shuffled[i], shuffled[i + 1])
    
    # 随机添加额外的边
    for u in vertices:
        for v in vertices:
            if u != v and not graph.has_edge(u, v):
                if random.random() < edge_probability:
                    graph.add_edge(u, v)
    
    # 计算顶点位置 (环形布局)
    import math
    center_x, center_y = 200, 180
    radius = 120
    
    for i, v in enumerate(vertices):
        angle = 2 * math.pi * i / num_vertices - math.pi / 2  # 从顶部开始
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        graph.set_position(v, x, y)
    
    return graph


def generate_bfs_friendly_graph(
    num_vertices: int = 7,
    min_children: int = 2,
    max_children: int = 3
) -> DirectedGraph:
    """
    生成适合BFS演示的有向图 - 树状结构，每个节点有多个子节点
    
    特点:
    1. 从起点开始，每层节点都有多个出边
    2. 形成明显的层级结构，便于观察BFS的层序遍历
    3. 可能有一些交叉边增加复杂性
    
    Args:
        num_vertices: 顶点数量 (5-12)
        min_children: 每个节点最少子节点数
        max_children: 每个节点最多子节点数
    
    Returns:
        DirectedGraph: 适合BFS演示的有向图
    """
    import math
    
    num_vertices = max(5, min(12, num_vertices))
    min_children = max(1, min(4, min_children))
    max_children = max(min_children, min(5, max_children))
    
    graph = DirectedGraph()
    
    # 创建顶点
    vertices = [chr(ord('A') + i) for i in range(num_vertices)]
    for v in vertices:
        graph.add_vertex(v)
    
    # 构建层级结构
    # 第一个顶点是根节点（Layer 0）
    root = vertices[0]
    assigned = {root}
    unassigned = set(vertices[1:])
    
    # 按层构建 - 当前层的节点会连接到下一层
    current_layer = [root]
    layer_assignment = {root: 0}  # 记录每个顶点的层级
    layer_num = 0
    
    while unassigned and current_layer:
        next_layer = []
        layer_num += 1
        
        for parent in current_layer:
            if not unassigned:
                break
            
            # 为每个父节点分配子节点
            num_children = random.randint(min_children, min(max_children, len(unassigned)))
            children = random.sample(list(unassigned), min(num_children, len(unassigned)))
            
            for child in children:
                graph.add_edge(parent, child)
                assigned.add(child)
                unassigned.discard(child)
                next_layer.append(child)
                layer_assignment[child] = layer_num
        
        current_layer = next_layer
    
    # 添加一些同层之间的边（可选，增加复杂性）
    layers = {}
    for v, l in layer_assignment.items():
        if l not in layers:
            layers[l] = []
        layers[l].append(v)
    
    # 随机添加少量交叉边（从低层到高层）
    for layer in range(len(layers) - 1):
        if layer + 2 < len(layers):  # 可以跳过一层连接
            for v in layers[layer]:
                if random.random() < 0.2:  # 20%概率
                    targets = layers.get(layer + 2, [])
                    if targets:
                        target = random.choice(targets)
                        if not graph.has_edge(v, target):
                            graph.add_edge(v, target)
    
    # 计算顶点位置 - 按层级布局
    max_layer = max(layer_assignment.values()) if layer_assignment else 0
    
    # 计算每层的宽度
    layer_widths = {}
    for l in range(max_layer + 1):
        layer_widths[l] = len(layers.get(l, []))
    
    # 设置位置 - 层级布局
    center_x = 240
    start_y = 50
    layer_height = 80
    
    for layer in range(max_layer + 1):
        layer_vertices = layers.get(layer, [])
        if not layer_vertices:
            continue
        
        width = len(layer_vertices)
        spacing = min(100, 400 / max(width, 1))
        start_x = center_x - (width - 1) * spacing / 2
        
        for i, v in enumerate(layer_vertices):
            x = start_x + i * spacing
            y = start_y + layer * layer_height
            graph.set_position(v, x, y)
    
    return graph


def bfs_traversal(graph: DirectedGraph, start: Any) -> List[Tuple[str, Any, Any]]:
    """
    BFS遍历生成器，返回每一步的操作
    
    Args:
        graph: 有向图
        start: 起始顶点
    
    Returns:
        List of (action, data1, data2) tuples:
        - ("visit", vertex, None): 访问顶点
        - ("enqueue", vertex, None): 入队
        - ("dequeue", vertex, None): 出队
        - ("check_neighbor", current, neighbor): 检查邻居
        - ("skip", neighbor, None): 跳过已访问的邻居
        - ("done", None, None): 完成
    """
    if not graph.has_vertex(start):
        return [("error", "起始顶点不存在", None)]
    
    steps = []
    visited: Set[Any] = set()
    queue: List[Any] = []
    
    # 起始顶点入队
    steps.append(("enqueue", start, None))
    queue.append(start)
    visited.add(start)
    
    while queue:
        # 出队
        current = queue.pop(0)
        steps.append(("dequeue", current, None))
        steps.append(("visit", current, None))
        
        # 遍历邻居
        neighbors = graph.get_neighbors(current)
        for neighbor in neighbors:
            steps.append(("check_neighbor", current, neighbor))
            if neighbor not in visited:
                steps.append(("enqueue", neighbor, None))
                queue.append(neighbor)
                visited.add(neighbor)
            else:
                steps.append(("skip", neighbor, None))
    
    steps.append(("done", None, None))
    return steps


# 测试代码
if __name__ == "__main__":
    # 测试随机图生成
    g = generate_random_graph(6, 0.3)
    print(f"Generated graph: {g}")
    print(f"Vertices: {g.get_vertices()}")
    print(f"Edges: {g.get_edges()}")
    
    # 测试BFS
    if g.get_vertices():
        start = g.get_vertices()[0]
        steps = bfs_traversal(g, start)
        print(f"\nBFS from {start}:")
        for step in steps:
            print(f"  {step}")

