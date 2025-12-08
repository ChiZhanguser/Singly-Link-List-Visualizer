"""
有向图模型 - 用于DFS演示
Directed Graph Model for DFS Demonstration
"""
from typing import Any, List, Dict, Set, Optional, Tuple
import random
import math


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
    center_x, center_y = 200, 180
    radius = 120
    
    for i, v in enumerate(vertices):
        angle = 2 * math.pi * i / num_vertices - math.pi / 2  # 从顶部开始
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        graph.set_position(v, x, y)
    
    return graph


def generate_dfs_friendly_graph(
    num_vertices: int = 7,
    branching_factor: int = 2,
    max_depth: int = 4
) -> DirectedGraph:
    """
    生成适合DFS演示的有向图 - 树状结构，有明显的深度路径
    
    特点:
    1. 从起点开始，有一条明显的深度路径
    2. 在某些节点有分支，展示DFS的回溯
    3. 适合演示DFS的"先深入再回溯"特性
    
    Args:
        num_vertices: 顶点数量 (5-12)
        branching_factor: 分支因子（每个节点最多多少个子节点）
        max_depth: 最大深度
    
    Returns:
        DirectedGraph: 适合DFS演示的有向图
    """
    num_vertices = max(5, min(12, num_vertices))
    branching_factor = max(1, min(3, branching_factor))
    
    graph = DirectedGraph()
    
    # 创建顶点
    vertices = [chr(ord('A') + i) for i in range(num_vertices)]
    for v in vertices:
        graph.add_vertex(v)
    
    # 构建树状结构 - 有明显的深度路径
    root = vertices[0]
    assigned = {root}
    unassigned = set(vertices[1:])
    
    # 使用队列构建树，但确保有一条主深度路径
    parent_queue = [(root, 0)]  # (节点, 深度)
    depth_map = {root: 0}
    
    # 首先创建一条主路径（深度优先）
    current = root
    depth = 0
    main_path = [root]
    
    while unassigned and depth < max_depth - 1:
        # 选择一个未分配的节点作为主路径的下一个节点
        if unassigned:
            next_node = min(unassigned)  # 选择字母序最小的
            graph.add_edge(current, next_node)
            assigned.add(next_node)
            unassigned.discard(next_node)
            depth += 1
            depth_map[next_node] = depth
            main_path.append(next_node)
            current = next_node
    
    # 然后为主路径上的节点添加分支
    for node in main_path[:-1]:  # 除了最后一个节点
        node_depth = depth_map[node]
        if node_depth < max_depth - 1:
            # 添加1-2个分支
            num_branches = min(branching_factor - 1, len(unassigned))
            branches = random.sample(list(unassigned), num_branches) if num_branches > 0 else []
            
            for branch in branches:
                graph.add_edge(node, branch)
                assigned.add(branch)
                unassigned.discard(branch)
                depth_map[branch] = node_depth + 1
    
    # 处理剩余未分配的节点
    while unassigned:
        # 找一个已分配的非叶子节点
        available_parents = [v for v in assigned if depth_map.get(v, 0) < max_depth - 1]
        if not available_parents:
            available_parents = list(assigned)
        
        parent = random.choice(available_parents)
        child = min(unassigned)
        graph.add_edge(parent, child)
        assigned.add(child)
        unassigned.discard(child)
        depth_map[child] = depth_map.get(parent, 0) + 1
    
    # 计算顶点位置 - 树形布局
    _layout_tree(graph, root, depth_map)
    
    return graph


def _layout_tree(graph: DirectedGraph, root: Any, depth_map: Dict[Any, int]):
    """为树形图计算布局位置"""
    # 按深度分组
    depth_groups = {}
    for v, d in depth_map.items():
        if d not in depth_groups:
            depth_groups[d] = []
        depth_groups[d].append(v)
    
    max_depth = max(depth_groups.keys()) if depth_groups else 0
    
    # 计算每层的位置
    center_x = 240
    start_y = 50
    layer_height = 70
    
    for depth in range(max_depth + 1):
        vertices_at_depth = depth_groups.get(depth, [])
        if not vertices_at_depth:
            continue
        
        width = len(vertices_at_depth)
        spacing = min(90, 400 / max(width, 1))
        start_x = center_x - (width - 1) * spacing / 2
        
        for i, v in enumerate(sorted(vertices_at_depth)):
            x = start_x + i * spacing
            y = start_y + depth * layer_height
            graph.set_position(v, x, y)


def dfs_traversal(graph: DirectedGraph, start: Any) -> List[Tuple[str, Any, Any]]:
    """
    DFS遍历生成器，返回每一步的操作
    
    Args:
        graph: 有向图
        start: 起始顶点
    
    Returns:
        List of (action, data1, data2) tuples:
        - ("push", vertex, depth): 入栈
        - ("pop", vertex, depth): 出栈
        - ("visit", vertex, depth): 访问顶点
        - ("check_neighbor", current, neighbor): 检查邻居
        - ("skip", neighbor, None): 跳过已访问的邻居
        - ("backtrack", from_vertex, to_vertex): 回溯
        - ("done", None, None): 完成
    """
    if not graph.has_vertex(start):
        return [("error", "起始顶点不存在", None)]
    
    steps = []
    visited: Set[Any] = set()
    stack: List[Tuple[Any, int]] = []  # (顶点, 深度)
    
    # 起始顶点入栈
    steps.append(("push", start, 0))
    stack.append((start, 0))
    
    while stack:
        # 出栈
        current, depth = stack.pop()
        steps.append(("pop", current, depth))
        
        if current in visited:
            steps.append(("skip", current, None))
            continue
        
        visited.add(current)
        steps.append(("visit", current, depth))
        
        # 遍历邻居（逆序入栈，保证字母序遍历）
        neighbors = graph.get_neighbors(current)
        neighbors_to_push = []
        
        for neighbor in neighbors:
            steps.append(("check_neighbor", current, neighbor))
            if neighbor not in visited:
                neighbors_to_push.append(neighbor)
                steps.append(("will_push", neighbor, depth + 1))
            else:
                steps.append(("skip", neighbor, None))
        
        # 逆序入栈
        for neighbor in reversed(neighbors_to_push):
            steps.append(("push", neighbor, depth + 1))
            stack.append((neighbor, depth + 1))
        
        # 如果没有新邻居入栈且栈不为空，说明要回溯
        if not neighbors_to_push and stack:
            next_vertex = stack[-1][0] if stack else None
            if next_vertex:
                steps.append(("backtrack", current, next_vertex))
    
    steps.append(("done", None, None))
    return steps


# 测试代码
if __name__ == "__main__":
    # 测试DFS友好图生成
    g = generate_dfs_friendly_graph(7, 2, 4)
    print(f"Generated graph: {g}")
    print(f"Vertices: {g.get_vertices()}")
    print(f"Edges: {g.get_edges()}")
    
    # 测试DFS
    if g.get_vertices():
        start = g.get_vertices()[0]
        steps = dfs_traversal(g, start)
        print(f"\nDFS from {start}:")
        for step in steps:
            print(f"  {step}")

