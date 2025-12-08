"""
BFS可视化模块 - 使用循环队列演示广度优先遍历
BFS Visualization Module - Demonstrating Breadth-First Search with Circular Queue

核心特点:
1. 清晰展示BFS的"层序遍历"特性 - 一层一层向外扩展
2. 使用环形循环队列可视化front/rear指针
3. 层级视图面板直观展示每层节点
4. 波浪动画效果展示BFS的扩散过程
5. 丰富的动画效果：波纹扩散、边脉冲、节点光晕等
"""
from tkinter import *
from tkinter import messagebox
import math
import time
from typing import List, Tuple, Optional, Any, Dict, Set

from circular_queue.graph_model import DirectedGraph, generate_random_graph, generate_bfs_friendly_graph, bfs_traversal
from circular_queue.circular_queue_model import CircularQueueModel


# ========== 动画配置 ==========
ANIMATION_CONFIG = {
    "wave_duration": 800,      # 波纹动画持续时间(ms)
    "wave_rings": 3,           # 波纹环数
    "pulse_duration": 400,     # 脉冲动画持续时间
    "glow_duration": 600,      # 光晕持续时间
    "edge_pulse_steps": 8,     # 边脉冲步数
    "particle_count": 12,      # 粒子数量
    "sparkle_duration": 500,   # 闪光持续时间
}


# ========== 层级颜色 - 用不同颜色区分不同层 ==========
LAYER_COLORS = [
    "#E74C3C",  # Layer 0 - 红色 (起点)
    "#F39C12",  # Layer 1 - 橙色
    "#F1C40F",  # Layer 2 - 黄色
    "#2ECC71",  # Layer 3 - 绿色
    "#3498DB",  # Layer 4 - 蓝色
    "#9B59B6",  # Layer 5 - 紫色
    "#1ABC9C",  # Layer 6 - 青色
    "#E91E63",  # Layer 7 - 粉色
]

def get_layer_color(layer: int) -> str:
    """获取层级对应的颜色"""
    return LAYER_COLORS[layer % len(LAYER_COLORS)]


# ========== BFS 多语言伪代码 ==========
LANG_PSEUDOCODE = "伪代码"
LANG_C = "C语言"
LANG_JAVA = "Java"
LANG_PYTHON = "Python"

MULTILANG_BFS = {
    "伪代码": [
        ("// 广度优先搜索 - 层序遍历", "comment"),
        ("BFS(graph, start):", "code"),
        ("  queue ← 创建循环队列", "code"),
        ("  visited ← 空集合", "code"),
        ("  enqueue(start)  // 第0层入队", "code"),
        ("  visited.add(start)", "code"),
        ("  layer ← 0  // 当前层级", "code"),
        ("  while queue 非空 do", "code"),
        ("    // --- 处理当前层 ---", "comment"),
        ("    current ← dequeue()", "code"),
        ("    访问 current (第layer层)", "code"),
        ("    // --- 发现下一层 ---", "comment"),
        ("    for neighbor ∈ adj[current] do", "code"),
        ("      if neighbor ∉ visited then", "code"),
        ("        enqueue(neighbor)  // 下一层", "code"),
        ("        visited.add(neighbor)", "code"),
        ("    layer++  // 进入下一层", "code"),
        ("  end while", "code"),
    ],
    "C语言": [
        ("// BFS - 层序遍历", "comment"),
        ("void bfs(Graph* g, int start) {", "code"),
        ("  CircularQueue* q = createQueue();", "code"),
        ("  int visited[MAX] = {0};", "code"),
        ("  enqueue(q, start);  // Layer 0", "code"),
        ("  visited[start] = 1;", "code"),
        ("  int layer = 0;", "code"),
        ("  while (!isEmpty(q)) {", "code"),
        ("    // 处理当前层", "comment"),
        ("    int cur = dequeue(q);", "code"),
        ("    visit(cur, layer);", "code"),
        ("    // 发现下一层节点", "comment"),
        ("    for (int i = 0; i < adjSize[cur]; i++) {", "code"),
        ("      int nb = adj[cur][i];", "code"),
        ("      if (!visited[nb]) {", "code"),
        ("        enqueue(q, nb);", "code"),
        ("        visited[nb] = 1;", "code"),
        ("      }", "code"),
        ("    }", "code"),
        ("  }", "code"),
        ("}", "code"),
    ],
    "Java": [
        ("// BFS - 层序遍历", "comment"),
        ("void bfs(int start) {", "code"),
        ("  Queue<Integer> q = new CircularQueue<>();", "code"),
        ("  Set<Integer> visited = new HashSet<>();", "code"),
        ("  q.enqueue(start);  // Layer 0", "code"),
        ("  visited.add(start);", "code"),
        ("  int layer = 0;", "code"),
        ("  while (!q.isEmpty()) {", "code"),
        ("    // 处理当前层", "comment"),
        ("    int cur = q.dequeue();", "code"),
        ("    visit(cur, layer);", "code"),
        ("    // 发现下一层节点", "comment"),
        ("    for (int nb : adj.get(cur)) {", "code"),
        ("      if (!visited.contains(nb)) {", "code"),
        ("        q.enqueue(nb);", "code"),
        ("        visited.add(nb);", "code"),
        ("      }", "code"),
        ("    }", "code"),
        ("  }", "code"),
        ("}", "code"),
    ],
    "Python": [
        ("# BFS - 层序遍历", "comment"),
        ("def bfs(graph, start):", "code"),
        ("  queue = CircularQueue()", "code"),
        ("  visited = set()", "code"),
        ("  queue.enqueue(start)  # Layer 0", "code"),
        ("  visited.add(start)", "code"),
        ("  layer = 0", "code"),
        ("  while not queue.is_empty():", "code"),
        ("    # 处理当前层", "comment"),
        ("    cur = queue.dequeue()", "code"),
        ("    visit(cur, layer)", "code"),
        ("    # 发现下一层节点", "comment"),
        ("    for nb in graph.neighbors(cur):", "code"),
        ("      if nb not in visited:", "code"),
        ("        queue.enqueue(nb)", "code"),
        ("        visited.add(nb)", "code"),
        ("    layer += 1", "code"),
    ]
}


class BFSVisualizer:
    """BFS可视化窗口 - 强调层序遍历特性"""
    
    def __init__(self, parent_window, queue_model: CircularQueueModel, code_language: str = "伪代码"):
        self.parent = parent_window
        self.queue_model = queue_model
        self.code_language = code_language
        
        # 创建新窗口
        self.window = Toplevel(parent_window)
        self.window.title("🔍 BFS 广度优先遍历 - 层序遍历演示")
        self.window.geometry("1500x900")
        self.window.configure(bg="#F5F7FA")
        self.window.transient(parent_window)
        
        # BFS状态
        self.graph: Optional[DirectedGraph] = None
        self.bfs_steps: List[Tuple] = []
        self.current_step = 0
        self.visited_vertices: Set[Any] = set()
        self.queued_vertices: Set[Any] = set()
        self.current_vertex: Optional[Any] = None
        self.traversal_order: List[Any] = []
        
        # 层级信息 - 核心数据结构
        self.vertex_layer: Dict[Any, int] = {}  # 顶点 -> 层级
        self.layer_vertices: Dict[int, List[Any]] = {}  # 层级 -> 顶点列表
        self.current_layer = 0  # 当前正在处理的层
        self.max_layer = 0  # 最大层级
        self.processing_layer = -1  # 正在处理的层级
        
        # 循环队列
        self.queue_capacity = 12
        self.queue_buffer: List[Optional[Any]] = [None] * self.queue_capacity
        self.queue_front = 0
        self.queue_rear = 0
        self.queue_size = 0
        
        # 动画状态
        self.animating = False
        self.paused = False
        self.animation_speed = 1200
        
        # 颜色
        self.colors = {
            "vertex_default": "#ECF0F1",
            "vertex_current": "#FFFFFF",
            "edge_default": "#BDC3C7",
            "edge_highlight": "#E74C3C",
            "edge_traversed": "#27AE60",
            "text_default": "#2C3E50",
            "bg": "#F5F7FA",
            "queue_empty": "#F8F9F9",
            "queue_front": "#E67E22",
            "queue_rear": "#2E86C1",
        }
        
        self.code_colors = {
            "bg": "#1E1E2E",
            "fg": "#D4D4D4",
            "highlight_bg": "#F9E2AF",
            "highlight_fg": "#1E1E2E",
            "comment": "#6A9955",
            "title": "#89B4FA",
        }
        
        # UI组件
        self.code_labels: List[Label] = []
        self.highlighted_line = -1
        self.edge_items: Dict[Tuple[Any, Any], int] = {}
        self.layer_frames: List[Frame] = []
        
        self._create_ui()
        self._generate_graph()
    
    def _create_ui(self):
        """创建UI布局"""
        # === 标题区域 ===
        title_frame = Frame(self.window, bg="#2C3E50")
        title_frame.pack(fill=X)
        
        Label(title_frame, text="🌊 BFS 广度优先搜索 - 层序遍历可视化", 
              font=("Microsoft YaHei", 18, "bold"),
              bg="#2C3E50", fg="white").pack(side=LEFT, padx=20, pady=10)
        
        Label(title_frame, text="观察BFS如何像波浪一样一层一层向外扩展",
              font=("Microsoft YaHei", 11),
              bg="#2C3E50", fg="#BDC3C7").pack(side=LEFT, padx=20)
        
        # === 层级进度条 ===
        self._create_layer_progress_bar()
        
        # === 主内容区域 ===
        content_frame = Frame(self.window, bg=self.colors["bg"])
        content_frame.pack(fill=BOTH, expand=True, padx=10, pady=5)
        
        # 左侧：图 + 队列
        left_frame = Frame(content_frame, bg=self.colors["bg"])
        left_frame.pack(side=LEFT, fill=BOTH, expand=True)
        
        # 图画布
        graph_header = Frame(left_frame, bg=self.colors["bg"])
        graph_header.pack(fill=X, padx=5)
        Label(graph_header, text="📊 有向图 (不同颜色 = 不同层级)", 
              font=("Microsoft YaHei", 11, "bold"),
              bg=self.colors["bg"], fg="#2C3E50").pack(side=LEFT)
        self._create_legend(graph_header)
        
        self.graph_canvas = Canvas(left_frame, bg="white", width=480, height=380,
                                   highlightthickness=2, highlightbackground="#3498DB")
        self.graph_canvas.pack(pady=5, padx=5)
        
        # 循环队列
        queue_header = Frame(left_frame, bg=self.colors["bg"])
        queue_header.pack(fill=X, padx=5, pady=(10, 0))
        Label(queue_header, text="🔄 循环队列 (颜色标记所属层级)", 
              font=("Microsoft YaHei", 11, "bold"),
              bg=self.colors["bg"], fg="#2C3E50").pack(side=LEFT)
        
        self.queue_canvas = Canvas(left_frame, bg="white", width=480, height=140,
                                   highlightthickness=2, highlightbackground="#16A085")
        self.queue_canvas.pack(pady=5, padx=5)
        
        # 队列信息
        self.queue_info_label = Label(left_frame, 
                                      text="front: 0 | rear: 0 | size: 0/12",
                                      font=("Consolas", 10),
                                      bg="#E8F6F3", fg="#1E8449")
        self.queue_info_label.pack(fill=X, padx=5)
        
        # === 中间：层级视图面板 (核心！) ===
        self._create_layer_view_panel(content_frame)
        
        # === 右侧：伪代码 + 状态 ===
        right_frame = Frame(content_frame, bg=self.code_colors["bg"], width=350)
        right_frame.pack(side=RIGHT, fill=Y, padx=5)
        right_frame.pack_propagate(False)
        
        # 伪代码
        code_header = Frame(right_frame, bg=self.code_colors["bg"])
        code_header.pack(fill=X, padx=10, pady=10)
        Label(code_header, text="📝 算法代码",
              font=("Microsoft YaHei", 11, "bold"),
              bg=self.code_colors["bg"], fg=self.code_colors["title"]).pack(side=LEFT)
        
        # 语言切换
        lang_frame = Frame(code_header, bg=self.code_colors["bg"])
        lang_frame.pack(side=RIGHT)
        self.lang_buttons = {}
        for lang in [LANG_PSEUDOCODE, LANG_C, LANG_JAVA, LANG_PYTHON]:
            short = {"伪代码": "伪代码", "C语言": "C", "Java": "Java", "Python": "Py"}[lang]
            btn = Label(lang_frame, text=short, font=("Microsoft YaHei", 8),
                       bg="#89B4FA" if lang == self.code_language else "#313244",
                       fg="#1E1E2E" if lang == self.code_language else "#CDD6F4",
                       padx=5, pady=2, cursor="hand2")
            btn.pack(side=LEFT, padx=1)
            btn.bind("<Button-1>", lambda e, l=lang: self._switch_language(l))
            self.lang_buttons[lang] = btn
        
        self.code_frame = Frame(right_frame, bg=self.code_colors["bg"])
        self.code_frame.pack(fill=BOTH, expand=True, padx=10, pady=5)
        self._render_pseudocode()
        
        # 当前操作说明
        action_frame = Frame(right_frame, bg="#2D3436", relief="groove", bd=2)
        action_frame.pack(fill=X, padx=10, pady=5)
        Label(action_frame, text="📍 当前操作", font=("Microsoft YaHei", 9, "bold"),
              bg="#2D3436", fg="#DFE6E9").pack(anchor=W, padx=5, pady=2)
        self.action_label = Label(action_frame, text="等待开始...",
                                  font=("Microsoft YaHei", 10),
                                  bg="#2D3436", fg="#74B9FF",
                                  wraplength=320, justify=LEFT)
        self.action_label.pack(fill=X, padx=5, pady=5)
        
        # 遍历结果
        result_frame = Frame(right_frame, bg=self.code_colors["bg"])
        result_frame.pack(fill=X, padx=10, pady=5)
        Label(result_frame, text="🎯 遍历顺序:", font=("Microsoft YaHei", 9, "bold"),
              bg=self.code_colors["bg"], fg="#89B4FA").pack(anchor=W)
        self.result_label = Label(result_frame, text="(未开始)",
                                  font=("Consolas", 10), bg="#313244", fg="#A6E3A1",
                                  wraplength=320, anchor="w", padx=5, pady=3)
        self.result_label.pack(fill=X)
        
        self.status_label = Label(right_frame, text="等待开始...",
                                 font=("Microsoft YaHei", 9),
                                 bg="#313244", fg="#A6ADC8", anchor="w", padx=5, pady=3)
        self.status_label.pack(fill=X, side=BOTTOM)
        
        # === 控制面板 ===
        self._create_control_panel()
    
    def _create_layer_progress_bar(self):
        """创建层级进度条"""
        self.progress_frame = Frame(self.window, bg="#34495E", height=60)
        self.progress_frame.pack(fill=X)
        self.progress_frame.pack_propagate(False)
        
        Label(self.progress_frame, text="📊 BFS层级进度:", 
              font=("Microsoft YaHei", 10, "bold"),
              bg="#34495E", fg="white").pack(side=LEFT, padx=10)
        
        # 层级指示器容器
        self.layer_indicator_frame = Frame(self.progress_frame, bg="#34495E")
        self.layer_indicator_frame.pack(side=LEFT, fill=X, expand=True, padx=10)
        
        # 当前层级标签
        self.current_layer_label = Label(self.progress_frame,
                                        text="当前层: -",
                                        font=("Microsoft YaHei", 12, "bold"),
                                        bg="#34495E", fg="#F1C40F")
        self.current_layer_label.pack(side=RIGHT, padx=20)
    
    def _update_layer_progress(self):
        """更新层级进度条"""
        # 清除旧的指示器
        for widget in self.layer_indicator_frame.winfo_children():
            widget.destroy()
        
        if not self.layer_vertices:
            return
        
        for layer in range(self.max_layer + 1):
            layer_frame = Frame(self.layer_indicator_frame, bg="#34495E")
            layer_frame.pack(side=LEFT, padx=5)
            
            # 层级颜色块
            color = get_layer_color(layer)
            is_current = (layer == self.processing_layer)
            is_completed = (layer < self.processing_layer)
            
            # 层级标签
            vertices = self.layer_vertices.get(layer, [])
            vertex_str = ",".join(str(v) for v in vertices)
            
            # 外框 - 当前层有动画效果
            if is_current:
                bg_color = color
                fg_color = "white"
                relief = "raised"
                border_width = 3
            elif is_completed:
                bg_color = color
                fg_color = "white"
                relief = "flat"
                border_width = 1
            else:
                bg_color = "#5D6D7E"
                fg_color = "#AEB6BF"
                relief = "flat"
                border_width = 1
            
            indicator = Label(layer_frame,
                             text=f"L{layer}\n{vertex_str}",
                             font=("Microsoft YaHei", 9, "bold" if is_current else "normal"),
                             bg=bg_color, fg=fg_color,
                             relief=relief, bd=border_width,
                             padx=10, pady=5)
            indicator.pack()
            
            # 当前层的脉冲动画
            if is_current:
                self._start_layer_pulse_animation(indicator, color)
            
            # 箭头（除了最后一层）- 使用动画箭头
            if layer < self.max_layer:
                arrow_color = "#2ECC71" if is_completed else "#7F8C8D"
                arrow_label = Label(layer_frame, text="→", font=("Arial", 14, "bold"),
                      bg="#34495E", fg=arrow_color)
                arrow_label.pack(side=RIGHT, padx=2)
                
                # 如果是当前层，箭头闪烁
                if is_current:
                    self._animate_arrow(arrow_label)
        
        # 更新当前层标签
        if self.processing_layer >= 0:
            self.current_layer_label.config(
                text=f"🌊 正在处理: 第 {self.processing_layer} 层",
                fg=get_layer_color(self.processing_layer))
        else:
            self.current_layer_label.config(text="当前层: -", fg="#F1C40F")
    
    def _start_layer_pulse_animation(self, label: Label, color: str):
        """为当前层指示器添加脉冲动画"""
        pulse_count = [0]  # 使用列表来保持引用
        
        def pulse():
            if pulse_count[0] >= 10 or not label.winfo_exists():
                return
            
            # 交替颜色
            if pulse_count[0] % 2 == 0:
                # 亮起
                r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
                bright_r = min(255, r + 40)
                bright_g = min(255, g + 40)
                bright_b = min(255, b + 40)
                bright_color = f"#{bright_r:02x}{bright_g:02x}{bright_b:02x}"
                label.config(bg=bright_color)
            else:
                label.config(bg=color)
            
            pulse_count[0] += 1
            self.window.after(200, pulse)
        
        pulse()
    
    def _animate_arrow(self, arrow_label: Label):
        """箭头闪烁动画"""
        colors = ["#2ECC71", "#F1C40F", "#E74C3C", "#3498DB"]
        color_index = [0]
        
        def flash():
            if not arrow_label.winfo_exists():
                return
            
            arrow_label.config(fg=colors[color_index[0] % len(colors)])
            color_index[0] += 1
            
            if color_index[0] < 12:  # 闪烁几次后停止
                self.window.after(150, flash)
        
        flash()
    
    def _create_layer_view_panel(self, parent):
        """创建层级视图面板 - 直观展示每层节点"""
        panel_frame = Frame(parent, bg="#FDFEFE", width=280, relief="groove", bd=2)
        panel_frame.pack(side=LEFT, fill=Y, padx=10)
        panel_frame.pack_propagate(False)
        
        # 标题
        Label(panel_frame, text="🌊 层级视图 (Layer View)",
              font=("Microsoft YaHei", 12, "bold"),
              bg="#FDFEFE", fg="#2C3E50").pack(pady=10)
        
        # 说明
        Label(panel_frame, 
              text="BFS按层级顺序访问节点\n同一层的节点会连续处理\n下一层节点在当前层完成后处理",
              font=("Microsoft YaHei", 9),
              bg="#FDFEFE", fg="#7F8C8D",
              justify=CENTER).pack(pady=5)
        
        # 分隔线
        Frame(panel_frame, height=2, bg="#BDC3C7").pack(fill=X, padx=10, pady=5)
        
        # 层级容器（可滚动）
        layer_container = Frame(panel_frame, bg="#FDFEFE")
        layer_container.pack(fill=BOTH, expand=True, padx=10, pady=5)
        
        self.layer_panel = layer_container
        
        # 波浪动画说明
        wave_frame = Frame(panel_frame, bg="#E8F8F5")
        wave_frame.pack(fill=X, padx=5, pady=5)
        
        Label(wave_frame, text="🌊 BFS像波浪一样扩散",
              font=("Microsoft YaHei", 10, "bold"),
              bg="#E8F8F5", fg="#16A085").pack()
        
        self.wave_label = Label(wave_frame,
                               text="从起点开始，逐层向外扩展",
                               font=("Microsoft YaHei", 9),
                               bg="#E8F8F5", fg="#1ABC9C")
        self.wave_label.pack()
    
    def _update_layer_view(self):
        """更新层级视图面板"""
        # 清除旧内容
        for widget in self.layer_panel.winfo_children():
            widget.destroy()
        
        if not self.layer_vertices:
            Label(self.layer_panel, text="(等待BFS开始)",
                  font=("Microsoft YaHei", 10),
                  bg="#FDFEFE", fg="#BDC3C7").pack(pady=20)
            return
        
        for layer in range(self.max_layer + 1):
            vertices = self.layer_vertices.get(layer, [])
            if not vertices:
                continue
            
            color = get_layer_color(layer)
            is_current = (layer == self.processing_layer)
            is_completed = all(v in self.visited_vertices for v in vertices)
            
            # 层级框架
            layer_frame = Frame(self.layer_panel, bg=color if is_current else "#FDFEFE",
                              relief="raised" if is_current else "groove", bd=2)
            layer_frame.pack(fill=X, pady=3)
            
            # 层级标题
            header_bg = color if is_current else "#F8F9F9"
            header_fg = "white" if is_current else color
            
            status = "✅" if is_completed else ("🔄" if is_current else "⏳")
            Label(layer_frame, text=f"{status} 第 {layer} 层 (Layer {layer})",
                  font=("Microsoft YaHei", 10, "bold"),
                  bg=header_bg, fg=header_fg).pack(fill=X, padx=5, pady=2)
            
            # 节点列表
            node_frame = Frame(layer_frame, bg="white")
            node_frame.pack(fill=X, padx=5, pady=5)
            
            for v in vertices:
                is_visited = v in self.visited_vertices
                is_processing = (v == self.current_vertex)
                
                node_bg = color if is_visited else ("#F1C40F" if is_processing else "#ECF0F1")
                node_fg = "white" if is_visited else "#2C3E50"
                
                node_label = Label(node_frame, text=str(v),
                                  font=("Microsoft YaHei", 11, "bold"),
                                  bg=node_bg, fg=node_fg,
                                  padx=12, pady=5,
                                  relief="raised" if is_processing else "flat")
                node_label.pack(side=LEFT, padx=3)
        
        # 更新波浪说明
        if self.processing_layer >= 0:
            wave_text = f"🌊 波浪已扩展到第 {self.processing_layer} 层"
            if self.processing_layer < self.max_layer:
                wave_text += f"\n下一层: 第 {self.processing_layer + 1} 层"
            self.wave_label.config(text=wave_text)
    
    def _create_legend(self, parent):
        """创建图例"""
        legend_frame = Frame(parent, bg=self.colors["bg"])
        legend_frame.pack(side=RIGHT)
        
        Label(legend_frame, text="图例:", font=("Microsoft YaHei", 8),
              bg=self.colors["bg"], fg="#7F8C8D").pack(side=LEFT, padx=5)
        
        for i, name in enumerate(["L0(起点)", "L1", "L2", "L3+"]):
            color = get_layer_color(i)
            f = Frame(legend_frame, bg=self.colors["bg"])
            f.pack(side=LEFT, padx=3)
            Canvas(f, width=14, height=14, bg=color, highlightthickness=1,
                   highlightbackground="#2C3E50").pack(side=LEFT)
            Label(f, text=name, font=("Microsoft YaHei", 8),
                  bg=self.colors["bg"], fg="#7F8C8D").pack(side=LEFT)
    
    def _create_control_panel(self):
        """创建控制面板"""
        control = Frame(self.window, bg="#FFFFFF", relief="flat", bd=1,
                       highlightbackground="#E1E8ED", highlightthickness=1)
        control.pack(fill=X, padx=10, pady=5)
        
        row1 = Frame(control, bg="#FFFFFF")
        row1.pack(fill=X, padx=15, pady=8)
        
        self.gen_btn = self._create_button(row1, "🎲 随机生成图", "#9B59B6", self._generate_graph)
        self.gen_btn.pack(side=LEFT, padx=3)
        
        Label(row1, text="顶点:", font=("Microsoft YaHei", 10),
              bg="#FFFFFF", fg="#2C3E50").pack(side=LEFT, padx=(10, 3))
        self.vertex_count_var = StringVar(value="6")
        Entry(row1, textvariable=self.vertex_count_var, width=3,
              font=("Microsoft YaHei", 10), relief="solid", bd=1).pack(side=LEFT)
        
        Label(row1, text="密度:", font=("Microsoft YaHei", 10),
              bg="#FFFFFF", fg="#2C3E50").pack(side=LEFT, padx=(10, 3))
        self.edge_density_var = StringVar(value="0.35")
        Entry(row1, textvariable=self.edge_density_var, width=4,
              font=("Microsoft YaHei", 10), relief="solid", bd=1).pack(side=LEFT)
        
        Label(row1, text=" | ", bg="#FFFFFF", fg="#BDC3C7").pack(side=LEFT, padx=8)
        
        Label(row1, text="起点:", font=("Microsoft YaHei", 10),
              bg="#FFFFFF", fg="#2C3E50").pack(side=LEFT, padx=(0, 3))
        self.start_vertex_var = StringVar(value="A")
        Entry(row1, textvariable=self.start_vertex_var, width=3,
              font=("Microsoft YaHei", 10), relief="solid", bd=1).pack(side=LEFT)
        
        Label(row1, text=" | ", bg="#FFFFFF", fg="#BDC3C7").pack(side=LEFT, padx=8)
        
        self.bfs_btn = self._create_button(row1, "▶ 开始BFS", "#27AE60", self._start_bfs)
        self.bfs_btn.pack(side=LEFT, padx=3)
        
        self.step_btn = self._create_button(row1, "⏭ 单步", "#3498DB", self._step_bfs)
        self.step_btn.pack(side=LEFT, padx=3)
        
        self.pause_btn = self._create_button(row1, "⏸ 暂停", "#F39C12", self._toggle_pause)
        self.pause_btn.pack(side=LEFT, padx=3)
        
        self.reset_btn = self._create_button(row1, "🔄 重置", "#E74C3C", self._reset_bfs)
        self.reset_btn.pack(side=LEFT, padx=3)
        
        Label(row1, text=" | 速度:", font=("Microsoft YaHei", 10),
              bg="#FFFFFF", fg="#2C3E50").pack(side=LEFT, padx=(8, 3))
        
        self.speed_scale = Scale(row1, from_=400, to=2500, orient=HORIZONTAL,
                                length=120, bg="#FFFFFF", troughcolor="#E1E8ED",
                                highlightthickness=0, command=self._update_speed)
        self.speed_scale.set(1200)
        self.speed_scale.pack(side=LEFT)
        
        self._create_button(row1, "关闭", "#95A5A6", self.window.destroy).pack(side=RIGHT, padx=3)
    
    def _create_button(self, parent, text, color, command):
        btn = Button(parent, text=text, font=("Microsoft YaHei", 9),
                    width=10, bg=color, fg="white",
                    activebackground=self._darken(color), activeforeground="white",
                    relief="flat", bd=0, command=command)
        btn.bind("<Enter>", lambda e: btn.config(bg=self._darken(color)))
        btn.bind("<Leave>", lambda e: btn.config(bg=color))
        return btn
    
    def _darken(self, color):
        r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
        return f"#{max(0,r-25):02x}{max(0,g-25):02x}{max(0,b-25):02x}"
    
    def _switch_language(self, lang):
        self.code_language = lang
        for l, btn in self.lang_buttons.items():
            btn.config(bg="#89B4FA" if l == lang else "#313244",
                      fg="#1E1E2E" if l == lang else "#CDD6F4")
        self._render_pseudocode()
        if self.highlighted_line >= 0:
            self._highlight_line(self.highlighted_line)
    
    def _render_pseudocode(self):
        for label in self.code_labels:
            label.destroy()
        self.code_labels = []
        
        code = MULTILANG_BFS.get(self.code_language, MULTILANG_BFS[LANG_PSEUDOCODE])
        for i, (text, typ) in enumerate(code):
            fg = self.code_colors["comment"] if typ == "comment" else self.code_colors["fg"]
            lbl = Label(self.code_frame, text=f" {i+1:2d} │ {text}",
                       font=("Consolas", 9), bg=self.code_colors["bg"], fg=fg,
                       anchor="w", padx=2, pady=1)
            lbl.pack(fill=X, anchor="w")
            self.code_labels.append(lbl)
    
    def _highlight_line(self, line: int, status: str = None):
        code = MULTILANG_BFS.get(self.code_language, MULTILANG_BFS[LANG_PSEUDOCODE])
        if 0 <= self.highlighted_line < len(self.code_labels):
            typ = code[self.highlighted_line][1] if self.highlighted_line < len(code) else "code"
            fg = self.code_colors["comment"] if typ == "comment" else self.code_colors["fg"]
            self.code_labels[self.highlighted_line].config(
                bg=self.code_colors["bg"], fg=fg, font=("Consolas", 9))
        
        if 0 <= line < len(self.code_labels):
            self.code_labels[line].config(
                bg=self.code_colors["highlight_bg"], fg=self.code_colors["highlight_fg"],
                font=("Consolas", 9, "bold"))
            self.highlighted_line = line
        
        if status:
            self.status_label.config(text=status)
    
    # ==================== 循环队列 ====================
    
    def _queue_enqueue(self, value):
        if self.queue_size >= self.queue_capacity:
            return False
        self.queue_buffer[self.queue_rear] = value
        self.queue_rear = (self.queue_rear + 1) % self.queue_capacity
        self.queue_size += 1
        return True
    
    def _queue_dequeue(self):
        if self.queue_size == 0:
            return None
        val = self.queue_buffer[self.queue_front]
        self.queue_buffer[self.queue_front] = None
        self.queue_front = (self.queue_front + 1) % self.queue_capacity
        self.queue_size -= 1
        return val
    
    def _queue_clear(self):
        self.queue_buffer = [None] * self.queue_capacity
        self.queue_front = self.queue_rear = self.queue_size = 0
    
    def _queue_to_list(self):
        result = []
        idx = self.queue_front
        for _ in range(self.queue_size):
            result.append(self.queue_buffer[idx])
            idx = (idx + 1) % self.queue_capacity
        return result
    
    # ==================== 绘图 ====================
    
    def _generate_graph(self):
        if self.animating:
            messagebox.showwarning("提示", "请先停止动画")
            return
        
        try:
            n = max(5, min(10, int(self.vertex_count_var.get())))
        except:
            messagebox.showerror("错误", "请输入有效数值")
            return
        
        # 使用BFS友好的图生成器 - 保证每个节点有多个出边
        # 这样能清楚地展示BFS的层序特性（一个父节点发现多个子节点）
        self.graph = generate_bfs_friendly_graph(n, min_children=2, max_children=3)
        
        if self.graph.get_vertices():
            self.start_vertex_var.set(self.graph.get_vertices()[0])
        
        self._reset_bfs()
        self._draw_graph()
        self._draw_queue()
        
        # 显示图的结构信息
        edge_info = []
        for v in self.graph.get_vertices():
            neighbors = self.graph.get_neighbors(v)
            if neighbors:
                edge_info.append(f"{v}→{','.join(neighbors)}")
        
        self.action_label.config(
            text=f"✅ 已生成BFS演示图\n"
                 f"顶点数: {self.graph.vertex_count()}\n"
                 f"边数: {self.graph.edge_count()}\n\n"
                 f"结构 (父→子):\n" + "\n".join(edge_info[:5]) + 
                 ("\n..." if len(edge_info) > 5 else "") +
                 f"\n\n💡 每个节点有多个出边\n点击\"开始BFS\"观察层序遍历")
    
    def _draw_graph(self):
        self.graph_canvas.delete("all")
        self.edge_items.clear()
        
        if not self.graph:
            return
        
        cx, cy, r = 240, 190, 140
        vertices = self.graph.get_vertices()
        
        for i, v in enumerate(vertices):
            angle = 2 * math.pi * i / len(vertices) - math.pi / 2
            self.graph.set_position(v, cx + r * math.cos(angle), cy + r * math.sin(angle))
        
        # 绘制边
        for u, v in self.graph.get_edges():
            self._draw_edge(u, v, self.colors["edge_default"])
        
        # 绘制顶点
        for v in vertices:
            pos = self.graph.get_position(v)
            if pos:
                # 根据层级选择颜色
                if v in self.vertex_layer:
                    color = get_layer_color(self.vertex_layer[v])
                else:
                    color = self.colors["vertex_default"]
                self._draw_vertex(v, pos[0], pos[1], color)
    
    def _draw_vertex(self, label, x, y, color, is_current=False):
        r = 26
        outline = "#E74C3C" if is_current else "#2C3E50"
        width = 4 if is_current else 2
        
        self.graph_canvas.create_oval(x-r, y-r, x+r, y+r, fill=color,
                                      outline=outline, width=width, tags=f"v_{label}")
        
        # 文字颜色
        text_color = "white" if color != self.colors["vertex_default"] else "#2C3E50"
        self.graph_canvas.create_text(x, y, text=str(label),
                                      font=("Microsoft YaHei", 13, "bold"),
                                      fill=text_color, tags=f"t_{label}")
        
        # 显示层级
        if label in self.vertex_layer:
            layer = self.vertex_layer[label]
            self.graph_canvas.create_text(x, y + r + 12, text=f"L{layer}",
                                          font=("Microsoft YaHei", 9, "bold"),
                                          fill=get_layer_color(layer), tags=f"l_{label}")
    
    def _draw_edge(self, u, v, color, width=2):
        pu, pv = self.graph.get_position(u), self.graph.get_position(v)
        if not pu or not pv:
            return
        
        r = 26
        dx, dy = pv[0] - pu[0], pv[1] - pu[1]
        length = math.sqrt(dx*dx + dy*dy)
        if length < 1:
            return
        
        ux, uy = dx/length, dy/length
        sx, sy = pu[0] + r*ux, pu[1] + r*uy
        ex, ey = pv[0] - r*ux, pv[1] - r*uy
        
        if (u, v) in self.edge_items:
            self.graph_canvas.delete(self.edge_items[(u, v)])
        
        item = self.graph_canvas.create_line(sx, sy, ex, ey, fill=color, width=width,
                                             arrow=LAST, arrowshape=(10, 12, 5))
        self.edge_items[(u, v)] = item
        self.graph_canvas.tag_lower(item)
    
    def _update_vertex(self, v, color, is_current=False):
        pos = self.graph.get_position(v)
        if not pos:
            return
        self.graph_canvas.delete(f"v_{v}")
        self.graph_canvas.delete(f"t_{v}")
        self.graph_canvas.delete(f"l_{v}")
        self._draw_vertex(v, pos[0], pos[1], color, is_current)
    
    def _draw_queue(self):
        """绘制带层级颜色的线性队列"""
        self.queue_canvas.delete("all")
        
        cell_w, cell_h = 50, 45
        start_x, start_y = 15, 45
        
        # 标题
        self.queue_canvas.create_text(240, 15, text="循环队列 (带层级颜色)",
                                     font=("Microsoft YaHei", 10, "bold"), fill="#2C3E50")
        
        # 绘制队列格子
        for i in range(self.queue_capacity):
            x = start_x + i * (cell_w + 4)
            y = start_y
            
            val = self.queue_buffer[i]
            
            # 根据值确定颜色
            if val is not None and val in self.vertex_layer:
                fill = get_layer_color(self.vertex_layer[val])
                text_color = "white"
            elif val is not None:
                fill = "#AED6F1"
                text_color = "#1A5276"
            else:
                fill = self.colors["queue_empty"]
                text_color = "#BDC3C7"
            
            outline = "#2C3E50" if val else "#BDC3C7"
            self.queue_canvas.create_rectangle(x, y, x+cell_w, y+cell_h,
                                              fill=fill, outline=outline, width=2)
            
            # 值
            if val is not None:
                self.queue_canvas.create_text(x+cell_w/2, y+cell_h/2, text=str(val),
                                             font=("Microsoft YaHei", 12, "bold"), fill=text_color)
            
            # 索引
            self.queue_canvas.create_text(x+cell_w/2, y+cell_h+12, text=str(i),
                                         font=("Microsoft YaHei", 8), fill="#7F8C8D")
        
        # front指针
        if self.queue_size > 0:
            fx = start_x + self.queue_front * (cell_w + 4) + cell_w/2
            self.queue_canvas.create_line(fx, start_y-5, fx, start_y-18, 
                                         fill=self.colors["queue_front"], width=3, arrow=FIRST)
            self.queue_canvas.create_text(fx, start_y-28, text=f"front={self.queue_front}",
                                         font=("Microsoft YaHei", 8, "bold"),
                                         fill=self.colors["queue_front"])
        
        # rear指针
        rx = start_x + self.queue_rear * (cell_w + 4) + cell_w/2
        self.queue_canvas.create_line(rx, start_y+cell_h+5, rx, start_y+cell_h+18,
                                     fill=self.colors["queue_rear"], width=3, arrow=LAST)
        self.queue_canvas.create_text(rx, start_y+cell_h+30, text=f"rear={self.queue_rear}",
                                     font=("Microsoft YaHei", 8, "bold"),
                                     fill=self.colors["queue_rear"])
        
        # 更新信息标签
        self.queue_info_label.config(
            text=f"front: {self.queue_front} | rear: {self.queue_rear} | "
                 f"size: {self.queue_size}/{self.queue_capacity}")
    
    # ==================== BFS控制 ====================
    
    def _update_speed(self, val):
        self.animation_speed = 2900 - int(val)
    
    def _start_bfs(self):
        if not self.graph:
            messagebox.showwarning("提示", "请先生成图")
            return
        
        start = self.start_vertex_var.get().strip().upper()
        if not self.graph.has_vertex(start):
            messagebox.showerror("错误", f"顶点'{start}'不存在")
            return
        
        if self.animating:
            return
        
        self._reset_bfs()
        self._generate_bfs_steps(start)
        self.animating = True
        self._set_buttons_state()
        self._animate_step()
    
    def _generate_bfs_steps(self, start):
        """生成强调层级的BFS步骤 - 特别强调多个邻居依次入队"""
        self.bfs_steps = []
        
        # 计算所有层级信息
        self._compute_layers(start)
        
        # 初始化
        self.bfs_steps.append(("init", None, None))
        self.bfs_steps.append(("new_layer", 0, [start]))  # 开始第0层
        self.bfs_steps.append(("enqueue", start, 0))
        self.bfs_steps.append(("mark", start, 0))
        
        visited = {start}
        queue = [(start, 0)]
        current_layer = 0
        
        while queue:
            v, layer = queue.pop(0)
            
            # 检查是否进入新层
            if layer > current_layer:
                next_layer_vertices = [x for x, l in self.vertex_layer.items() if l == layer]
                self.bfs_steps.append(("new_layer", layer, next_layer_vertices))
                current_layer = layer
            
            self.bfs_steps.append(("dequeue", v, layer))
            self.bfs_steps.append(("visit", v, layer))
            
            neighbors = self.graph.get_neighbors(v)
            
            if neighbors:
                # 先收集未访问的邻居
                unvisited_neighbors = [nb for nb in neighbors if nb not in visited]
                
                # 显示探索开始 - 强调发现了多少个新节点
                self.bfs_steps.append(("explore_start", v, (neighbors, unvisited_neighbors)))
                
                # 如果有多个未访问邻居，添加"准备依次入队"的提示
                if len(unvisited_neighbors) >= 2:
                    self.bfs_steps.append(("batch_enqueue_start", v, unvisited_neighbors))
                
                # 依次处理每个邻居
                enqueue_index = 0
                for nb in neighbors:
                    self.bfs_steps.append(("check_edge", v, nb))
                    if nb not in visited:
                        enqueue_index += 1
                        # 入队时带上序号信息 (第几个入队 / 总共几个)
                        self.bfs_steps.append(("enqueue_animated", nb, 
                                              (layer + 1, enqueue_index, len(unvisited_neighbors), v)))
                        visited.add(nb)
                        queue.append((nb, layer + 1))
                    else:
                        self.bfs_steps.append(("skip", nb, None))
                
                # 如果有多个未访问邻居，添加"入队完成"的提示
                if len(unvisited_neighbors) >= 2:
                    self.bfs_steps.append(("batch_enqueue_end", v, unvisited_neighbors))
                
                self.bfs_steps.append(("explore_end", v, None))
        
        self.bfs_steps.append(("done", None, None))
    
    def _compute_layers(self, start):
        """预计算所有顶点的层级"""
        self.vertex_layer = {start: 0}
        self.layer_vertices = {0: [start]}
        self.max_layer = 0
        
        visited = {start}
        queue = [(start, 0)]
        
        while queue:
            v, layer = queue.pop(0)
            for nb in self.graph.get_neighbors(v):
                if nb not in visited:
                    visited.add(nb)
                    nb_layer = layer + 1
                    self.vertex_layer[nb] = nb_layer
                    if nb_layer not in self.layer_vertices:
                        self.layer_vertices[nb_layer] = []
                    self.layer_vertices[nb_layer].append(nb)
                    self.max_layer = max(self.max_layer, nb_layer)
                    queue.append((nb, nb_layer))
        
        self._update_layer_progress()
        self._update_layer_view()
    
    def _step_bfs(self):
        if not self.graph:
            messagebox.showwarning("提示", "请先生成图")
            return
        
        start = self.start_vertex_var.get().strip().upper()
        
        if not self.bfs_steps:
            if not self.graph.has_vertex(start):
                messagebox.showerror("错误", f"顶点'{start}'不存在")
                return
            self._reset_bfs()
            self._generate_bfs_steps(start)
        
        if self.current_step >= len(self.bfs_steps):
            return
        
        self._execute_step(self.bfs_steps[self.current_step])
        self.current_step += 1
    
    def _toggle_pause(self):
        if self.animating:
            self.animating = False
            self.paused = True
            self.pause_btn.config(text="▶ 继续")
        else:
            if self.bfs_steps and self.current_step < len(self.bfs_steps):
                self.animating = True
                self.paused = False
                self.pause_btn.config(text="⏸ 暂停")
                self._animate_step()
    
    def _reset_bfs(self):
        self.animating = False
        self.paused = False
        self.bfs_steps = []
        self.current_step = 0
        self.visited_vertices = set()
        self.queued_vertices = set()
        self.current_vertex = None
        self.traversal_order = []
        self.vertex_layer = {}
        self.layer_vertices = {}
        self.max_layer = 0
        self.processing_layer = -1
        self.highlighted_line = -1
        
        self._queue_clear()
        self._render_pseudocode()
        self._draw_graph()
        self._draw_queue()
        self._update_layer_progress()
        self._update_layer_view()
        
        self.result_label.config(text="(未开始)")
        self.action_label.config(text="等待开始...")
        self.status_label.config(text="已重置")
        self.pause_btn.config(text="⏸ 暂停")
        self._set_buttons_state()
    
    def _set_buttons_state(self):
        state = DISABLED if self.animating else NORMAL
        self.gen_btn.config(state=state)
        self.bfs_btn.config(state=state)
        self.step_btn.config(state=state)
    
    def _animate_step(self):
        if not self.animating:
            return
        
        if self.current_step >= len(self.bfs_steps):
            self.animating = False
            self._set_buttons_state()
            return
        
        self._execute_step(self.bfs_steps[self.current_step])
        self.current_step += 1
        
        if self.animating:
            self.window.after(self.animation_speed, self._animate_step)
    
    def _execute_step(self, step):
        action, d1, d2 = step
        
        if action == "init":
            self._highlight_line(2, "初始化")
            self.action_label.config(text="📋 初始化BFS:\n• 创建循环队列\n• 创建visited集合\n• 准备层序遍历")
            
            # 初始化动画 - 在图中心显示波纹
            cx, cy = 240, 190
            self._create_ripple_wave(cx, cy, 150, "#3498DB", 0)
        
        elif action == "new_layer":
            layer = d1
            vertices = d2
            old_layer = self.processing_layer
            self.processing_layer = layer
            self._update_layer_progress()
            self._update_layer_view()
            
            color = get_layer_color(layer)
            v_str = ", ".join(str(v) for v in vertices)
            
            self._highlight_line(8, f"进入第{layer}层")
            self.action_label.config(
                text=f"🌊🌊🌊 进入第 {layer} 层 🌊🌊🌊\n\n"
                     f"本层节点: [{v_str}]\n"
                     f"共 {len(vertices)} 个节点\n\n"
                     f"BFS会先处理完本层所有节点\n"
                     f"再进入下一层")
            
            # 增强的层级过渡动画
            self._animate_layer_transition(old_layer, layer)
            
            # 波浪效果：闪烁本层所有节点
            self._flash_layer(layer)
        
        elif action == "enqueue":
            v, layer = d1, d2
            old_rear = self.queue_rear
            target_index = old_rear
            
            self._queue_enqueue(v)
            self.queued_vertices.add(v)
            
            color = get_layer_color(layer)
            self._update_vertex(v, color)
            
            # 入队动画
            self._animate_queue_enqueue(v, target_index, color)
            
            # 节点发现动画
            pos = self.graph.get_position(v)
            if pos:
                self._animate_vertex_glow(v, color, 1.0)
                self._animate_discovery_sparkles(pos[0], pos[1], color)
            
            self._highlight_line(4 if layer == 0 else 14, f"入队: {v}")
            self.action_label.config(
                text=f"📥 入队: {v} (第{layer}层)\n\n"
                     f"• buffer[{old_rear}] = {v}\n"
                     f"• rear = ({old_rear}+1) % {self.queue_capacity} = {self.queue_rear}\n"
                     f"• 该节点属于第{layer}层\n"
                     f"• 颜色标记为该层颜色")
        
        elif action == "mark":
            self._highlight_line(5 if d2 == 0 else 15, f"标记{d1}已访问")
            # 标记动画 - 给节点添加一个快速的勾选效果
            pos = self.graph.get_position(d1)
            if pos:
                self._animate_vertex_glow(d1, get_layer_color(d2), 0.5)
        
        elif action == "dequeue":
            v, layer = d1, d2
            old_front = self.queue_front
            source_index = old_front
            
            color = get_layer_color(layer)
            
            # 出队动画
            self._animate_queue_dequeue(v, source_index, color, 
                                       callback=lambda: self._draw_queue())
            
            self._queue_dequeue()
            self.current_vertex = v
            
            self._update_vertex(v, color, is_current=True)
            self._update_layer_view()
            
            # 当前节点光晕效果
            pos = self.graph.get_position(v)
            if pos:
                self._animate_vertex_glow(v, color, 1.5)
                # 从中心发射波纹表示准备探索
                self._create_ripple_wave(pos[0], pos[1], 100, color, layer)
            
            self._highlight_line(9, f"出队: {v}")
            self.action_label.config(
                text=f"📤 出队: {v} (第{layer}层)\n\n"
                     f"• current = buffer[{old_front}] = {v}\n"
                     f"• front = ({old_front}+1) % {self.queue_capacity} = {self.queue_front}\n"
                     f"• 当前正在处理第{layer}层")
        
        elif action == "visit":
            v, layer = d1, d2
            self.visited_vertices.add(v)
            self.queued_vertices.discard(v)
            self.traversal_order.append(v)
            
            color = get_layer_color(layer)
            self._update_vertex(v, color)
            self._draw_queue()
            self._update_layer_view()
            
            order = " → ".join(str(x) for x in self.traversal_order)
            self.result_label.config(text=order)
            
            # 访问节点的庆祝动画
            pos = self.graph.get_position(v)
            if pos:
                self._animate_discovery_sparkles(pos[0], pos[1], color)
            
            self._highlight_line(10, f"访问: {v}")
            self.action_label.config(
                text=f"✅ 访问节点 {v}\n\n"
                     f"• 层级: 第 {layer} 层\n"
                     f"• 已访问序列:\n  {order}\n\n"
                     f"接下来探索{v}的邻居")
        
        elif action == "explore_start":
            v, data = d1, d2
            all_neighbors, unvisited = data
            all_str = ", ".join(str(n) for n in all_neighbors)
            new_str = ", ".join(str(n) for n in unvisited)
            
            # 探索开始时发射探测波纹
            pos = self.graph.get_position(v)
            if pos:
                layer = self.vertex_layer.get(v, 0)
                color = get_layer_color(layer)
                self._create_ripple_wave(pos[0], pos[1], 120, color, layer)
                # 添加扫描效果 - 雷达式搜索邻居
                self._animate_scanning_effect(v)
            
            self._highlight_line(12, f"探索{v}的邻居")
            self.action_label.config(
                text=f"🔍 探索 {v} 的所有邻居\n\n"
                     f"📋 邻居列表: [{all_str}]\n"
                     f"✨ 新发现节点: [{new_str}]\n"
                     f"共 {len(unvisited)} 个新节点将入队\n\n"
                     f"👉 这{len(unvisited)}个节点将依次入队，\n"
                     f"   成为下一层的节点")
        
        elif action == "batch_enqueue_start":
            parent = d1
            children = d2
            children_str = ", ".join(str(c) for c in children)
            self._highlight_line(14, f"准备依次入队{len(children)}个节点")
            self.action_label.config(
                text=f"📦 准备批量入队!\n\n"
                     f"父节点 {parent} 发现 {len(children)} 个新子节点:\n"
                     f"[{children_str}]\n\n"
                     f"🌊 这些节点将依次入队:\n"
                     f"   1️⃣ → 2️⃣ → ... → {len(children)}️⃣\n\n"
                     f"观察队列如何逐个增长！")
            
            # 高亮所有待入队节点并添加闪烁预告
            for i, c in enumerate(children):
                self._update_vertex(c, "#FFFFFF", is_current=False)
                pos = self.graph.get_position(c)
                if pos:
                    # 为每个待发现节点添加预告光晕
                    self.window.after(i * 100, lambda x=pos[0], y=pos[1]: 
                        self._animate_discovery_sparkles(x, y, "#F1C40F"))
        
        elif action == "enqueue_animated":
            v = d1
            layer, idx, total, parent = d2
            
            old_rear = self.queue_rear
            target_index = old_rear
            
            self._queue_enqueue(v)
            self.queued_vertices.add(v)
            
            color = get_layer_color(layer)
            self._update_vertex(v, color)
            self._update_layer_view()
            
            # 入队动画
            self._animate_queue_enqueue(v, target_index, color)
            
            # 绘制从图节点到队列的连接动画
            self._draw_animated_connection(v, target_index, color)
            
            # 显示入队进度
            progress_bar = "●" * idx + "○" * (total - idx)
            
            self._highlight_line(14, f"入队: {v} ({idx}/{total})")
            self.action_label.config(
                text=f"📥 入队第 {idx}/{total} 个: {v}\n\n"
                     f"进度: [{progress_bar}]\n\n"
                     f"• 父节点: {parent}\n"
                     f"• buffer[{old_rear}] = {v}\n"
                     f"• rear: {old_rear} → {self.queue_rear}\n"
                     f"• 该节点属于第 {layer} 层\n\n"
                     f"{'✅ 全部入队完成!' if idx == total else f'⏳ 还有 {total-idx} 个节点待入队'}")
            
            # 增强的闪烁效果
            self._flash_vertex(v, color)
        
        elif action == "batch_enqueue_end":
            parent = d1
            children = d2
            children_str = " → ".join(str(c) for c in children)
            next_layer = self.vertex_layer.get(children[0], 0) if children else 0
            
            self._highlight_line(15, "入队完成")
            self.action_label.config(
                text=f"✅ 批量入队完成!\n\n"
                     f"父节点 {parent} 的 {len(children)} 个子节点\n"
                     f"已全部加入队列:\n\n"
                     f"入队顺序: {children_str}\n\n"
                     f"🎯 这些节点都属于第 {next_layer} 层\n"
                     f"📋 它们将在第{next_layer}层被依次出队访问")
        
        elif action == "check_edge":
            u, v = d1, d2
            self._draw_edge(u, v, self.colors["edge_highlight"], 4)
            
            # 边上的脉冲动画 - 显示数据流动
            is_new = v not in self.visited_vertices and v not in self.queued_vertices
            pulse_color = "#2ECC71" if is_new else "#E74C3C"
            self._animate_edge_pulse(u, v, pulse_color)
            
            # 目标节点预览光晕
            if is_new:
                next_layer = self.vertex_layer.get(v, 0)
                self._animate_vertex_glow(v, get_layer_color(next_layer), 0.8)
            
            self._highlight_line(13, f"检查边 {u}→{v}")
            
            status = "✨ 新节点!" if is_new else "⚠️ 已访问"
            
            self.action_label.config(
                text=f"🔗 检查边: {u} → {v}\n\n"
                     f"• 目标节点: {v}\n"
                     f"• 状态: {status}\n"
                     f"• {v} {'∉' if is_new else '∈'} visited")
        
        elif action == "skip":
            v = d1
            if self.current_vertex:
                self._draw_edge(self.current_vertex, v, self.colors["edge_traversed"], 2)
            
            # 跳过节点的淡化效果
            pos = self.graph.get_position(v)
            if pos:
                # 显示一个"已访问"的标记动画
                self._show_skip_indicator(pos[0], pos[1])
            
            self._highlight_line(13, f"跳过{v}(已访问)")
            self.action_label.config(
                text=f"⏭ 跳过节点 {v}\n\n"
                     f"• {v} ∈ visited\n"
                     f"• 该节点已被发现过\n"
                     f"• 无需重复入队")
        
        elif action == "explore_end":
            v = d1
            for nb in self.graph.get_neighbors(v):
                self._draw_edge(v, nb, self.colors["edge_traversed"], 2)
            self._highlight_line(16, f"{v}的邻居探索完毕")
        
        elif action == "done":
            self.animating = False
            self.processing_layer = self.max_layer + 1
            self._update_layer_progress()
            self._update_layer_view()
            self._set_buttons_state()
            
            order = " → ".join(str(x) for x in self.traversal_order)
            
            # 构建层级统计
            layer_stats = []
            for l in range(self.max_layer + 1):
                verts = self.layer_vertices.get(l, [])
                layer_stats.append(f"L{l}: {','.join(str(v) for v in verts)}")
            
            # 完成时的庆祝动画
            self._celebrate_completion()
            
            self._highlight_line(17, "✅ BFS完成!")
            self.action_label.config(
                text=f"🎉 BFS层序遍历完成!\n\n"
                     f"📊 遍历统计:\n"
                     f"• 总层数: {self.max_layer + 1} 层\n"
                     f"• 访问顺序: {order}\n\n"
                     f"📋 各层节点:\n" + "\n".join(layer_stats) +
                     f"\n\n💡 BFS特点:\n"
                     f"• 先访问完一层，再访问下一层\n"
                     f"• 同层节点按入队顺序访问\n"
                     f"• 像波浪一样逐层扩散")
    
    # ==================== 增强动画效果 ====================
    
    def _create_ripple_wave(self, center_x: float, center_y: float, max_radius: float, 
                           color: str, layer: int):
        """
        创建从中心扩散的波纹动画 - 展示BFS的波浪式扩散
        
        Args:
            center_x, center_y: 波纹中心坐标
            max_radius: 最大扩散半径
            color: 波纹颜色
            layer: 当前层级（用于多环效果）
        """
        rings = ANIMATION_CONFIG["wave_rings"]
        duration = ANIMATION_CONFIG["wave_duration"]
        steps = 20
        step_delay = duration // steps
        
        ring_items = []
        
        def animate_wave(step):
            # 清除之前的波纹
            for item in ring_items:
                self.graph_canvas.delete(item)
            ring_items.clear()
            
            if step >= steps:
                return
            
            progress = step / steps
            
            for ring in range(rings):
                # 每个环有不同的延迟和大小
                ring_delay = ring * 0.2
                ring_progress = max(0, min(1, (progress - ring_delay) / (1 - ring_delay * rings / (rings + 1))))
                
                if ring_progress <= 0:
                    continue
                
                # 计算当前环的半径和透明度
                current_radius = ring_progress * max_radius
                # 透明度随扩散衰减（通过改变线宽和虚线模式模拟）
                alpha = 1 - ring_progress
                line_width = max(1, int(4 * alpha))
                
                # 创建波纹环 - 使用渐变色效果
                r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
                # 混合白色来模拟透明效果
                fade = int(255 * (1 - alpha))
                r2 = min(255, r + fade)
                g2 = min(255, g + fade)
                b2 = min(255, b + fade)
                ring_color = f"#{r2:02x}{g2:02x}{b2:02x}"
                
                # 绘制波纹圆环
                item = self.graph_canvas.create_oval(
                    center_x - current_radius, center_y - current_radius,
                    center_x + current_radius, center_y + current_radius,
                    outline=ring_color, width=line_width, 
                    dash=(8, 4) if ring > 0 else ()
                )
                ring_items.append(item)
                self.graph_canvas.tag_lower(item)
            
            self.window.after(step_delay, lambda: animate_wave(step + 1))
        
        animate_wave(0)
    
    def _animate_edge_pulse(self, u, v, color: str, callback=None):
        """
        创建边上的脉冲动画 - 显示数据沿边流动
        
        Args:
            u, v: 边的起点和终点
            color: 脉冲颜色
            callback: 动画完成后的回调函数
        """
        pu, pv = self.graph.get_position(u), self.graph.get_position(v)
        if not pu or not pv:
            if callback:
                callback()
            return
        
        r = 26  # 顶点半径
        dx, dy = pv[0] - pu[0], pv[1] - pu[1]
        length = math.sqrt(dx * dx + dy * dy)
        if length < 1:
            if callback:
                callback()
            return
        
        ux, uy = dx / length, dy / length
        sx, sy = pu[0] + r * ux, pu[1] + r * uy
        ex, ey = pv[0] - r * ux, pv[1] - r * uy
        
        steps = ANIMATION_CONFIG["edge_pulse_steps"]
        duration = ANIMATION_CONFIG["pulse_duration"]
        step_delay = duration // steps
        
        pulse_items = []
        
        def animate_pulse(step):
            # 清除之前的脉冲
            for item in pulse_items:
                self.graph_canvas.delete(item)
            pulse_items.clear()
            
            if step >= steps:
                if callback:
                    callback()
                return
            
            progress = step / steps
            
            # 计算脉冲位置（沿边移动的点）
            pulse_x = sx + (ex - sx) * progress
            pulse_y = sy + (ey - sy) * progress
            
            # 绘制移动的脉冲点（大小逐渐变化）
            pulse_size = 8 + 4 * math.sin(progress * math.pi)
            
            # 主脉冲点
            item1 = self.graph_canvas.create_oval(
                pulse_x - pulse_size, pulse_y - pulse_size,
                pulse_x + pulse_size, pulse_y + pulse_size,
                fill=color, outline="white", width=2
            )
            pulse_items.append(item1)
            
            # 拖尾效果（多个渐小的点）
            for trail in range(1, 4):
                trail_progress = max(0, progress - trail * 0.08)
                if trail_progress <= 0:
                    continue
                trail_x = sx + (ex - sx) * trail_progress
                trail_y = sy + (ey - sy) * trail_progress
                trail_size = pulse_size * (1 - trail * 0.25)
                
                # 拖尾颜色渐淡
                r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
                fade = int(80 * trail)
                r2 = min(255, r + fade)
                g2 = min(255, g + fade)
                b2 = min(255, b + fade)
                trail_color = f"#{r2:02x}{g2:02x}{b2:02x}"
                
                item = self.graph_canvas.create_oval(
                    trail_x - trail_size, trail_y - trail_size,
                    trail_x + trail_size, trail_y + trail_size,
                    fill=trail_color, outline=""
                )
                pulse_items.append(item)
            
            self.window.after(step_delay, lambda: animate_pulse(step + 1))
        
        animate_pulse(0)
    
    def _animate_vertex_glow(self, v, color: str, intensity: float = 1.0):
        """
        创建顶点光晕动画 - 强调当前节点
        
        Args:
            v: 顶点标签
            color: 光晕颜色
            intensity: 光晕强度 (0-1)
        """
        pos = self.graph.get_position(v)
        if not pos:
            return
        
        x, y = pos
        duration = ANIMATION_CONFIG["glow_duration"]
        steps = 15
        step_delay = duration // steps
        
        glow_items = []
        
        def animate_glow(step):
            # 清除之前的光晕
            for item in glow_items:
                self.graph_canvas.delete(item)
            glow_items.clear()
            
            if step >= steps:
                return
            
            # 使用正弦波创建呼吸效果
            progress = step / steps
            pulse = 0.5 + 0.5 * math.sin(progress * math.pi * 2)
            
            # 绘制多层光晕
            for layer in range(3, 0, -1):
                glow_radius = 26 + layer * 8 * intensity * pulse
                
                # 光晕颜色渐变
                r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
                alpha = (4 - layer) / 4 * pulse
                r2 = min(255, int(r + (255 - r) * (1 - alpha)))
                g2 = min(255, int(g + (255 - g) * (1 - alpha)))
                b2 = min(255, int(b + (255 - b) * (1 - alpha)))
                glow_color = f"#{r2:02x}{g2:02x}{b2:02x}"
                
                item = self.graph_canvas.create_oval(
                    x - glow_radius, y - glow_radius,
                    x + glow_radius, y + glow_radius,
                    fill="", outline=glow_color, width=3
                )
                glow_items.append(item)
                self.graph_canvas.tag_lower(item)
            
            self.window.after(step_delay, lambda: animate_glow(step + 1))
        
        animate_glow(0)
    
    def _animate_discovery_sparkles(self, x: float, y: float, color: str):
        """
        创建发现节点时的闪光粒子效果
        
        Args:
            x, y: 粒子爆发中心
            color: 粒子颜色
        """
        particle_count = ANIMATION_CONFIG["particle_count"]
        duration = ANIMATION_CONFIG["sparkle_duration"]
        steps = 12
        step_delay = duration // steps
        
        # 生成粒子的初始角度和速度
        particles = []
        for i in range(particle_count):
            angle = 2 * math.pi * i / particle_count + (i % 2) * 0.3
            speed = 40 + (i % 3) * 15
            particles.append({
                "angle": angle,
                "speed": speed,
                "size": 4 + (i % 3) * 2
            })
        
        particle_items = []
        
        def animate_sparkles(step):
            # 清除之前的粒子
            for item in particle_items:
                self.graph_canvas.delete(item)
            particle_items.clear()
            
            if step >= steps:
                return
            
            progress = step / steps
            
            for p in particles:
                # 计算粒子当前位置
                distance = p["speed"] * progress
                px = x + distance * math.cos(p["angle"])
                py = y + distance * math.sin(p["angle"])
                
                # 粒子大小和透明度随时间减小
                size = p["size"] * (1 - progress * 0.7)
                
                # 颜色渐变
                r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
                fade = int(200 * progress)
                r2 = min(255, r + fade)
                g2 = min(255, g + fade)
                b2 = min(255, b + fade)
                p_color = f"#{r2:02x}{g2:02x}{b2:02x}"
                
                # 绘制星形粒子
                item = self.graph_canvas.create_oval(
                    px - size, py - size,
                    px + size, py + size,
                    fill=p_color, outline="white", width=1
                )
                particle_items.append(item)
            
            self.window.after(step_delay, lambda: animate_sparkles(step + 1))
        
        animate_sparkles(0)
    
    def _animate_queue_enqueue(self, value, target_index: int, color: str):
        """
        创建入队动画 - 元素滑入队列
        
        Args:
            value: 入队的值
            target_index: 目标位置索引
            color: 元素颜色
        """
        cell_w, cell_h = 50, 45
        start_x, start_y = 15, 45
        
        # 计算目标位置
        target_x = start_x + target_index * (cell_w + 4) + cell_w / 2
        target_y = start_y + cell_h / 2
        
        # 起始位置（从上方落下）
        start_anim_y = -30
        
        steps = 10
        step_delay = 30
        
        item_ids = []
        
        def animate_enqueue(step):
            for item in item_ids:
                self.queue_canvas.delete(item)
            item_ids.clear()
            
            if step >= steps:
                self._draw_queue()
                return
            
            progress = step / steps
            # 使用弹性缓动效果
            eased = 1 - math.pow(1 - progress, 3)
            
            current_y = start_anim_y + (target_y - start_anim_y) * eased
            
            # 绘制移动的元素
            item1 = self.queue_canvas.create_rectangle(
                target_x - cell_w / 2, current_y - cell_h / 2,
                target_x + cell_w / 2, current_y + cell_h / 2,
                fill=color, outline="#2C3E50", width=3
            )
            item_ids.append(item1)
            
            item2 = self.queue_canvas.create_text(
                target_x, current_y,
                text=str(value),
                font=("Microsoft YaHei", 12, "bold"),
                fill="white"
            )
            item_ids.append(item2)
            
            # 添加下落阴影
            shadow_offset = 5 * (1 - eased)
            item3 = self.queue_canvas.create_oval(
                target_x - 15 - shadow_offset,
                target_y + cell_h / 2 + 5,
                target_x + 15 + shadow_offset,
                target_y + cell_h / 2 + 10,
                fill="#DDD", outline=""
            )
            item_ids.append(item3)
            self.queue_canvas.tag_lower(item3)
            
            self.window.after(step_delay, lambda: animate_enqueue(step + 1))
        
        animate_enqueue(0)
    
    def _animate_queue_dequeue(self, value, source_index: int, color: str, callback=None):
        """
        创建出队动画 - 元素弹出队列
        
        Args:
            value: 出队的值
            source_index: 源位置索引
            color: 元素颜色
            callback: 动画完成后的回调
        """
        cell_w, cell_h = 50, 45
        start_x, start_y = 15, 45
        
        # 计算源位置
        source_x = start_x + source_index * (cell_w + 4) + cell_w / 2
        source_y = start_y + cell_h / 2
        
        # 目标位置（向上弹出并淡出）
        target_anim_y = -50
        
        steps = 12
        step_delay = 25
        
        item_ids = []
        
        def animate_dequeue(step):
            for item in item_ids:
                self.queue_canvas.delete(item)
            item_ids.clear()
            
            if step >= steps:
                if callback:
                    callback()
                return
            
            progress = step / steps
            # 弹出效果
            eased = 1 - math.pow(1 - progress, 2)
            
            current_y = source_y + (target_anim_y - source_y) * eased
            # 缩放效果
            scale = 1 + 0.3 * math.sin(progress * math.pi)
            
            # 透明度效果（通过颜色模拟）
            r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
            fade = int(100 * progress)
            r2 = min(255, r + fade)
            g2 = min(255, g + fade)
            b2 = min(255, b + fade)
            current_color = f"#{r2:02x}{g2:02x}{b2:02x}"
            
            # 绘制弹出的元素
            half_w = cell_w / 2 * scale
            half_h = cell_h / 2 * scale
            
            item1 = self.queue_canvas.create_rectangle(
                source_x - half_w, current_y - half_h,
                source_x + half_w, current_y + half_h,
                fill=current_color, outline="#2C3E50", width=2
            )
            item_ids.append(item1)
            
            item2 = self.queue_canvas.create_text(
                source_x, current_y,
                text=str(value),
                font=("Microsoft YaHei", int(12 * scale), "bold"),
                fill="white" if progress < 0.7 else "#AAA"
            )
            item_ids.append(item2)
            
            self.window.after(step_delay, lambda: animate_dequeue(step + 1))
        
        animate_dequeue(0)
    
    def _animate_layer_transition(self, from_layer: int, to_layer: int):
        """
        创建层级过渡动画 - 显示进入新层级
        
        Args:
            from_layer: 源层级
            to_layer: 目标层级
        """
        # 在进度条上创建滑动效果
        if not self.layer_vertices:
            return
        
        to_color = get_layer_color(to_layer)
        to_vertices = self.layer_vertices.get(to_layer, [])
        
        if not to_vertices:
            return
        
        # 为目标层的每个顶点创建波纹
        for i, v in enumerate(to_vertices):
            pos = self.graph.get_position(v)
            if pos:
                # 延迟创建波纹，产生级联效果
                self.window.after(
                    i * 100,
                    lambda x=pos[0], y=pos[1], c=to_color: 
                        self._create_ripple_wave(x, y, 60, c, to_layer)
                )
                # 同时添加闪光效果
                self.window.after(
                    i * 100 + 50,
                    lambda x=pos[0], y=pos[1], c=to_color:
                        self._animate_discovery_sparkles(x, y, c)
                )
    
    def _flash_layer(self, layer):
        """闪烁指定层的所有节点 - 增强版"""
        vertices = self.layer_vertices.get(layer, [])
        color = get_layer_color(layer)
        
        # 添加波纹效果
        for i, v in enumerate(vertices):
            pos = self.graph.get_position(v)
            if pos:
                self.window.after(
                    i * 80,
                    lambda x=pos[0], y=pos[1], c=color:
                        self._create_ripple_wave(x, y, 80, c, layer)
                )
        
        def flash(count):
            if count <= 0:
                for v in vertices:
                    self._update_vertex(v, color)
                return
            
            for v in vertices:
                if count % 2 == 0:
                    self._update_vertex(v, color)
                else:
                    self._update_vertex(v, "#FFFFFF")
            
            self.window.after(120, lambda: flash(count - 1))
        
        flash(6)
    
    def _flash_vertex(self, v, final_color):
        """闪烁单个顶点 - 增强版，带光晕效果"""
        pos = self.graph.get_position(v)
        
        # 添加光晕效果
        if pos:
            self._animate_vertex_glow(v, final_color, 1.2)
            self._animate_discovery_sparkles(pos[0], pos[1], final_color)
        
        def flash(count):
            if count <= 0:
                self._update_vertex(v, final_color)
                return
            
            if count % 2 == 0:
                self._update_vertex(v, final_color)
            else:
                self._update_vertex(v, "#FFFFFF")
            
            self.window.after(80, lambda: flash(count - 1))
        
        flash(6)
    
    def _show_skip_indicator(self, x: float, y: float):
        """
        显示跳过节点的指示器动画 - 表示节点已被访问
        
        Args:
            x, y: 节点位置
        """
        steps = 10
        step_delay = 40
        
        items = []
        
        def animate_skip(step):
            for item in items:
                self.graph_canvas.delete(item)
            items.clear()
            
            if step >= steps:
                return
            
            progress = step / steps
            
            # 创建一个"X"标记动画
            size = 15 + 10 * math.sin(progress * math.pi)
            alpha = 1 - progress
            
            # 红色叉号颜色渐变
            fade = int(255 * (1 - alpha))
            color = f"#{255:02x}{fade:02x}{fade:02x}"
            
            # 绘制叉号
            item1 = self.graph_canvas.create_line(
                x - size, y - size, x + size, y + size,
                fill=color, width=3
            )
            item2 = self.graph_canvas.create_line(
                x + size, y - size, x - size, y + size,
                fill=color, width=3
            )
            items.extend([item1, item2])
            
            self.window.after(step_delay, lambda: animate_skip(step + 1))
        
        animate_skip(0)
    
    def _celebrate_completion(self):
        """
        BFS完成时的庆祝动画 - 所有节点依次闪烁
        """
        vertices = list(self.traversal_order)
        
        # 依次为每个访问的节点创建烟花效果
        for i, v in enumerate(vertices):
            pos = self.graph.get_position(v)
            if pos:
                layer = self.vertex_layer.get(v, 0)
                color = get_layer_color(layer)
                
                # 延迟创建效果，形成级联
                self.window.after(
                    i * 150,
                    lambda x=pos[0], y=pos[1], c=color:
                        self._animate_firework(x, y, c)
                )
        
        # 最后在中心创建一个大波纹
        self.window.after(
            len(vertices) * 150 + 200,
            lambda: self._create_ripple_wave(240, 190, 200, "#F1C40F", 0)
        )
    
    def _animate_firework(self, x: float, y: float, color: str):
        """
        烟花爆炸效果
        
        Args:
            x, y: 爆炸中心
            color: 烟花颜色
        """
        particle_count = 16
        duration = 600
        steps = 15
        step_delay = duration // steps
        
        # 生成粒子
        particles = []
        for i in range(particle_count):
            angle = 2 * math.pi * i / particle_count
            speed = 30 + (i % 3) * 10
            particles.append({
                "angle": angle,
                "speed": speed,
                "size": 3 + (i % 2) * 2
            })
        
        items = []
        
        def animate_firework_step(step):
            for item in items:
                self.graph_canvas.delete(item)
            items.clear()
            
            if step >= steps:
                return
            
            progress = step / steps
            
            for p in particles:
                # 粒子运动轨迹 - 带重力效果
                t = progress
                distance = p["speed"] * t
                
                px = x + distance * math.cos(p["angle"])
                # 添加重力效果
                py = y + distance * math.sin(p["angle"]) + 20 * t * t
                
                # 粒子大小和亮度随时间变化
                size = p["size"] * (1 - progress * 0.5)
                
                # 颜色渐暗
                r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
                fade = int(180 * progress)
                r2 = max(0, r - fade)
                g2 = max(0, g - fade)
                b2 = max(0, b - fade)
                p_color = f"#{max(50,r2):02x}{max(50,g2):02x}{max(50,b2):02x}"
                
                # 绘制粒子（带拖尾）
                item = self.graph_canvas.create_oval(
                    px - size, py - size,
                    px + size, py + size,
                    fill=p_color, outline=""
                )
                items.append(item)
            
            self.window.after(step_delay, lambda: animate_firework_step(step + 1))
        
        animate_firework_step(0)
    
    def _animate_scanning_effect(self, v):
        """
        为当前节点创建扫描效果 - 表示正在探索邻居
        
        Args:
            v: 当前节点
        """
        pos = self.graph.get_position(v)
        if not pos:
            return
        
        x, y = pos
        steps = 20
        step_delay = 50
        
        items = []
        
        def animate_scan(step):
            for item in items:
                self.graph_canvas.delete(item)
            items.clear()
            
            if step >= steps:
                return
            
            progress = step / steps
            angle = progress * 2 * math.pi  # 完整转一圈
            
            # 扫描线
            scan_length = 60
            end_x = x + scan_length * math.cos(angle)
            end_y = y + scan_length * math.sin(angle)
            
            layer = self.vertex_layer.get(v, 0)
            color = get_layer_color(layer)
            
            # 绘制扫描线
            item1 = self.graph_canvas.create_line(
                x, y, end_x, end_y,
                fill=color, width=3, dash=(5, 3)
            )
            items.append(item1)
            
            # 扫描点
            item2 = self.graph_canvas.create_oval(
                end_x - 5, end_y - 5,
                end_x + 5, end_y + 5,
                fill=color, outline="white", width=2
            )
            items.append(item2)
            
            self.window.after(step_delay, lambda: animate_scan(step + 1))
        
        animate_scan(0)
    
    def _draw_animated_connection(self, v, queue_index: int, color: str):
        """
        绘制从图节点到队列的动画连接线 - 可视化入队过程
        
        Args:
            v: 图中的节点
            queue_index: 队列中的目标位置
            color: 连接线颜色
        """
        pos = self.graph.get_position(v)
        if not pos:
            return
        
        # 图节点位置（相对于画布）
        graph_x, graph_y = pos
        
        # 在图画布底部创建指示箭头
        steps = 12
        step_delay = 40
        
        items = []
        
        def animate_connection(step):
            for item in items:
                self.graph_canvas.delete(item)
            items.clear()
            
            if step >= steps:
                return
            
            progress = step / steps
            
            # 创建从节点向下的动画箭头
            arrow_y = graph_y + 26 + 30 * progress
            
            # 透明度效果
            alpha = 1 - progress * 0.5
            r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
            fade = int(100 * (1 - alpha))
            r2 = min(255, r + fade)
            g2 = min(255, g + fade)
            b2 = min(255, b + fade)
            line_color = f"#{r2:02x}{g2:02x}{b2:02x}"
            
            # 绘制箭头
            item = self.graph_canvas.create_line(
                graph_x, graph_y + 26,
                graph_x, arrow_y,
                fill=line_color, width=3, arrow=LAST,
                arrowshape=(8, 10, 4)
            )
            items.append(item)
            
            # 添加"入队"文字
            if progress > 0.3:
                text_item = self.graph_canvas.create_text(
                    graph_x + 30, graph_y + 40,
                    text="→队列",
                    font=("Microsoft YaHei", 8, "bold"),
                    fill=color
                )
                items.append(text_item)
            
            self.window.after(step_delay, lambda: animate_connection(step + 1))
        
        animate_connection(0)


def open_bfs_visualizer(parent_window, queue_model: CircularQueueModel, code_language: str = "伪代码"):
    return BFSVisualizer(parent_window, queue_model, code_language)


if __name__ == "__main__":
    root = Tk()
    root.title("测试")
    root.geometry("200x100")
    
    queue = CircularQueueModel(8)
    Button(root, text="打开BFS演示", command=lambda: open_bfs_visualizer(root, queue)).pack(pady=30)
    root.mainloop()
