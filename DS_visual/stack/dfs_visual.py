"""
DFS可视化模块 - 使用栈演示深度优先遍历
DFS Visualization Module - Demonstrating Depth-First Search with Stack

核心特点:
1. 清晰展示DFS的"深度优先"特性 - 先深入再回溯
2. 使用栈可视化展示push/pop操作
3. 深度视图面板直观展示递归深度
4. 回溯动画效果展示DFS的探索过程
5. 丰富的动画效果：深度潜入、路径追踪、回溯闪光等
"""
from tkinter import *
from tkinter import messagebox
import math
import time
from typing import List, Tuple, Optional, Any, Dict, Set

from stack.graph_model import DirectedGraph, generate_random_graph, generate_dfs_friendly_graph, dfs_traversal
from stack.stack_model import StackModel


# ========== 动画配置 ==========
ANIMATION_CONFIG = {
    "dive_duration": 600,       # 深度潜入动画持续时间(ms)
    "backtrack_duration": 500,  # 回溯动画持续时间
    "pulse_duration": 400,      # 脉冲动画持续时间
    "glow_duration": 600,       # 光晕持续时间
    "edge_trace_steps": 12,     # 边追踪步数
    "particle_count": 10,       # 粒子数量
    "sparkle_duration": 400,    # 闪光持续时间
}


# ========== 深度颜色 - 用不同颜色区分不同深度 ==========
DEPTH_COLORS = [
    "#E74C3C",  # Depth 0 - 红色 (起点)
    "#E67E22",  # Depth 1 - 橙色
    "#F1C40F",  # Depth 2 - 黄色
    "#27AE60",  # Depth 3 - 绿色
    "#3498DB",  # Depth 4 - 蓝色
    "#9B59B6",  # Depth 5 - 紫色
    "#1ABC9C",  # Depth 6 - 青色
    "#E91E63",  # Depth 7 - 粉色
]

def get_depth_color(depth: int) -> str:
    """获取深度对应的颜色"""
    return DEPTH_COLORS[depth % len(DEPTH_COLORS)]


# ========== DFS 多语言伪代码 ==========
LANG_PSEUDOCODE = "伪代码"
LANG_C = "C语言"
LANG_JAVA = "Java"
LANG_PYTHON = "Python"

MULTILANG_DFS = {
    "伪代码": [
        ("// 深度优先搜索 - 栈实现", "comment"),
        ("DFS(graph, start):", "code"),
        ("  stack ← 创建空栈", "code"),
        ("  visited ← 空集合", "code"),
        ("  push(start)  // 起点入栈", "code"),
        ("  while stack 非空 do", "code"),
        ("    current ← pop()  // 出栈", "code"),
        ("    if current ∈ visited then", "code"),
        ("      continue  // 跳过已访问", "code"),
        ("    end if", "code"),
        ("    visited.add(current)", "code"),
        ("    访问 current  // 处理当前节点", "code"),
        ("    // 将邻居逆序入栈", "comment"),
        ("    for neighbor ∈ reverse(adj[current]) do", "code"),
        ("      if neighbor ∉ visited then", "code"),
        ("        push(neighbor)  // 入栈", "code"),
        ("      end if", "code"),
        ("    end for", "code"),
        ("  end while", "code"),
    ],
    "C语言": [
        ("// DFS - 栈实现", "comment"),
        ("void dfs(Graph* g, int start) {", "code"),
        ("  Stack* s = createStack();", "code"),
        ("  int visited[MAX] = {0};", "code"),
        ("  push(s, start);  // 起点入栈", "code"),
        ("  while (!isEmpty(s)) {", "code"),
        ("    int cur = pop(s);  // 出栈", "code"),
        ("    if (visited[cur]) {", "code"),
        ("      continue;  // 跳过已访问", "code"),
        ("    }", "code"),
        ("    visited[cur] = 1;", "code"),
        ("    visit(cur);  // 处理当前节点", "code"),
        ("    // 将邻居逆序入栈", "comment"),
        ("    for (int i = adjSize[cur]-1; i >= 0; i--) {", "code"),
        ("      int nb = adj[cur][i];", "code"),
        ("      if (!visited[nb]) {", "code"),
        ("        push(s, nb);  // 入栈", "code"),
        ("      }", "code"),
        ("    }", "code"),
        ("  }", "code"),
        ("}", "code"),
    ],
    "Java": [
        ("// DFS - 栈实现", "comment"),
        ("void dfs(int start) {", "code"),
        ("  Stack<Integer> s = new Stack<>();", "code"),
        ("  Set<Integer> visited = new HashSet<>();", "code"),
        ("  s.push(start);  // 起点入栈", "code"),
        ("  while (!s.isEmpty()) {", "code"),
        ("    int cur = s.pop();  // 出栈", "code"),
        ("    if (visited.contains(cur)) {", "code"),
        ("      continue;  // 跳过已访问", "code"),
        ("    }", "code"),
        ("    visited.add(cur);", "code"),
        ("    visit(cur);  // 处理当前节点", "code"),
        ("    // 将邻居逆序入栈", "comment"),
        ("    List<Integer> neighbors = adj.get(cur);", "code"),
        ("    for (int i = neighbors.size()-1; i >= 0; i--) {", "code"),
        ("      int nb = neighbors.get(i);", "code"),
        ("      if (!visited.contains(nb)) {", "code"),
        ("        s.push(nb);  // 入栈", "code"),
        ("      }", "code"),
        ("    }", "code"),
        ("  }", "code"),
        ("}", "code"),
    ],
    "Python": [
        ("# DFS - 栈实现", "comment"),
        ("def dfs(graph, start):", "code"),
        ("  stack = []  # 创建空栈", "code"),
        ("  visited = set()", "code"),
        ("  stack.append(start)  # 起点入栈", "code"),
        ("  while stack:  # 栈非空", "code"),
        ("    cur = stack.pop()  # 出栈", "code"),
        ("    if cur in visited:", "code"),
        ("      continue  # 跳过已访问", "code"),
        ("    # endif", "code"),
        ("    visited.add(cur)", "code"),
        ("    visit(cur)  # 处理当前节点", "code"),
        ("    # 将邻居逆序入栈", "comment"),
        ("    for nb in reversed(graph.neighbors(cur)):", "code"),
        ("      if nb not in visited:", "code"),
        ("        stack.append(nb)  # 入栈", "code"),
        ("    # endfor", "code"),
    ]
}


class DFSVisualizer:
    """DFS可视化窗口 - 强调深度优先特性"""
    
    def __init__(self, parent_window, stack_model: StackModel, code_language: str = "伪代码"):
        self.parent = parent_window
        self.stack_model = stack_model
        self.code_language = code_language
        
        # 创建新窗口
        self.window = Toplevel(parent_window)
        self.window.title("🔍 DFS 深度优先遍历 - 栈实现演示")
        self.window.geometry("1500x900")
        self.window.configure(bg="#F5F7FA")
        self.window.transient(parent_window)
        
        # DFS状态
        self.graph: Optional[DirectedGraph] = None
        self.dfs_steps: List[Tuple] = []
        self.current_step = 0
        self.visited_vertices: Set[Any] = set()
        self.stacked_vertices: Set[Any] = set()
        self.current_vertex: Optional[Any] = None
        self.traversal_order: List[Any] = []
        
        # 深度信息 - 核心数据结构
        self.vertex_depth: Dict[Any, int] = {}  # 顶点 -> 深度
        self.current_depth = 0  # 当前深度
        self.max_depth = 0  # 最大深度
        self.dfs_path: List[Any] = []  # 当前DFS路径（用于回溯显示）
        
        # 栈（用于可视化）
        self.visual_stack: List[Tuple[Any, int]] = []  # (顶点, 深度)
        
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
            "edge_backtrack": "#9B59B6",
            "text_default": "#2C3E50",
            "bg": "#F5F7FA",
            "stack_empty": "#F8F9F9",
            "stack_top": "#E74C3C",
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
        
        self._create_ui()
        self._generate_graph()
    
    def _create_ui(self):
        """创建UI布局"""
        # === 标题区域 ===
        title_frame = Frame(self.window, bg="#2C3E50")
        title_frame.pack(fill=X)
        
        Label(title_frame, text="🌲 DFS 深度优先搜索 - 栈实现可视化", 
              font=("Microsoft YaHei", 18, "bold"),
              bg="#2C3E50", fg="white").pack(side=LEFT, padx=20, pady=10)
        
        Label(title_frame, text="观察DFS如何像探险家一样深入探索，遇到死胡同再回溯",
              font=("Microsoft YaHei", 11),
              bg="#2C3E50", fg="#BDC3C7").pack(side=LEFT, padx=20)
        
        # === 深度进度条 ===
        self._create_depth_progress_bar()
        
        # === 主内容区域 ===
        content_frame = Frame(self.window, bg=self.colors["bg"])
        content_frame.pack(fill=BOTH, expand=True, padx=10, pady=5)
        
        # 左侧：图 + 栈
        left_frame = Frame(content_frame, bg=self.colors["bg"])
        left_frame.pack(side=LEFT, fill=BOTH, expand=True)
        
        # 图画布
        graph_header = Frame(left_frame, bg=self.colors["bg"])
        graph_header.pack(fill=X, padx=5)
        Label(graph_header, text="📊 有向图 (不同颜色 = 不同深度)", 
              font=("Microsoft YaHei", 11, "bold"),
              bg=self.colors["bg"], fg="#2C3E50").pack(side=LEFT)
        self._create_legend(graph_header)
        
        self.graph_canvas = Canvas(left_frame, bg="white", width=480, height=380,
                                   highlightthickness=2, highlightbackground="#9B59B6")
        self.graph_canvas.pack(pady=5, padx=5)
        
        # 栈可视化
        stack_header = Frame(left_frame, bg=self.colors["bg"])
        stack_header.pack(fill=X, padx=5, pady=(10, 0))
        Label(stack_header, text="📚 栈 (颜色标记深度级别)", 
              font=("Microsoft YaHei", 11, "bold"),
              bg=self.colors["bg"], fg="#2C3E50").pack(side=LEFT)
        
        self.stack_canvas = Canvas(left_frame, bg="white", width=480, height=140,
                                   highlightthickness=2, highlightbackground="#9B59B6")
        self.stack_canvas.pack(pady=5, padx=5)
        
        # 栈信息
        self.stack_info_label = Label(left_frame, 
                                      text="栈大小: 0 | 当前深度: 0",
                                      font=("Consolas", 10),
                                      bg="#F3E5F5", fg="#6A1B9A")
        self.stack_info_label.pack(fill=X, padx=5)
        
        # === 中间：深度视图面板 (核心！) ===
        self._create_depth_view_panel(content_frame)
        
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
        
        # 当前路径显示
        path_frame = Frame(right_frame, bg=self.code_colors["bg"])
        path_frame.pack(fill=X, padx=10, pady=5)
        Label(path_frame, text="🛤️ 当前DFS路径:", font=("Microsoft YaHei", 9, "bold"),
              bg=self.code_colors["bg"], fg="#F9E2AF").pack(anchor=W)
        self.path_label = Label(path_frame, text="(未开始)",
                                font=("Consolas", 10), bg="#313244", fg="#FAB387",
                                wraplength=320, anchor="w", padx=5, pady=3)
        self.path_label.pack(fill=X)
        
        self.status_label = Label(right_frame, text="等待开始...",
                                 font=("Microsoft YaHei", 9),
                                 bg="#313244", fg="#A6ADC8", anchor="w", padx=5, pady=3)
        self.status_label.pack(fill=X, side=BOTTOM)
        
        # === 控制面板 ===
        self._create_control_panel()
    
    def _create_depth_progress_bar(self):
        """创建深度进度条"""
        self.progress_frame = Frame(self.window, bg="#4A235A", height=60)
        self.progress_frame.pack(fill=X)
        self.progress_frame.pack_propagate(False)
        
        Label(self.progress_frame, text="📊 DFS深度进度:", 
              font=("Microsoft YaHei", 10, "bold"),
              bg="#4A235A", fg="white").pack(side=LEFT, padx=10)
        
        # 深度指示器容器
        self.depth_indicator_frame = Frame(self.progress_frame, bg="#4A235A")
        self.depth_indicator_frame.pack(side=LEFT, fill=X, expand=True, padx=10)
        
        # 当前深度标签
        self.current_depth_label = Label(self.progress_frame,
                                        text="当前深度: 0",
                                        font=("Microsoft YaHei", 12, "bold"),
                                        bg="#4A235A", fg="#F1C40F")
        self.current_depth_label.pack(side=RIGHT, padx=20)
    
    def _update_depth_progress(self):
        """更新深度进度条"""
        # 清除旧的指示器
        for widget in self.depth_indicator_frame.winfo_children():
            widget.destroy()
        
        if self.max_depth == 0:
            return
        
        for depth in range(self.max_depth + 1):
            depth_frame = Frame(self.depth_indicator_frame, bg="#4A235A")
            depth_frame.pack(side=LEFT, padx=5)
            
            # 深度颜色块
            color = get_depth_color(depth)
            is_current = (depth == self.current_depth)
            
            # 深度标签
            vertices_at_depth = [v for v, d in self.vertex_depth.items() if d == depth]
            vertex_str = ",".join(str(v) for v in vertices_at_depth[:3])
            if len(vertices_at_depth) > 3:
                vertex_str += "..."
            
            # 外框 - 当前深度有动画效果
            if is_current:
                bg_color = color
                fg_color = "white"
                relief = "raised"
                border_width = 3
            else:
                bg_color = "#5D6D7E"
                fg_color = "#AEB6BF"
                relief = "flat"
                border_width = 1
            
            indicator = Label(depth_frame,
                             text=f"D{depth}\n{vertex_str}",
                             font=("Microsoft YaHei", 9, "bold" if is_current else "normal"),
                             bg=bg_color, fg=fg_color,
                             relief=relief, bd=border_width,
                             padx=10, pady=5)
            indicator.pack()
            
            # 连接线（除了最后一层）
            if depth < self.max_depth:
                Label(depth_frame, text="↓", font=("Arial", 14, "bold"),
                      bg="#4A235A", fg="#7F8C8D").pack(side=RIGHT, padx=2)
        
        # 更新当前深度标签
        self.current_depth_label.config(
            text=f"🌲 当前深度: {self.current_depth}",
            fg=get_depth_color(self.current_depth))
    
    def _create_depth_view_panel(self, parent):
        """创建深度视图面板 - 直观展示DFS路径"""
        panel_frame = Frame(parent, bg="#FDFEFE", width=280, relief="groove", bd=2)
        panel_frame.pack(side=LEFT, fill=Y, padx=10)
        panel_frame.pack_propagate(False)
        
        # 标题
        Label(panel_frame, text="🌲 深度视图 (Depth View)",
              font=("Microsoft YaHei", 12, "bold"),
              bg="#FDFEFE", fg="#2C3E50").pack(pady=10)
        
        # 说明
        Label(panel_frame, 
              text="DFS沿着一条路径深入探索\n遇到死胡同后回溯\n尝试其他未探索的分支",
              font=("Microsoft YaHei", 9),
              bg="#FDFEFE", fg="#7F8C8D",
              justify=CENTER).pack(pady=5)
        
        # 分隔线
        Frame(panel_frame, height=2, bg="#BDC3C7").pack(fill=X, padx=10, pady=5)
        
        # 深度容器（可滚动）
        depth_container = Frame(panel_frame, bg="#FDFEFE")
        depth_container.pack(fill=BOTH, expand=True, padx=10, pady=5)
        
        self.depth_panel = depth_container
        
        # DFS路径说明
        path_frame = Frame(panel_frame, bg="#F3E5F5")
        path_frame.pack(fill=X, padx=5, pady=5)
        
        Label(path_frame, text="🛤️ DFS像探险家一样探索",
              font=("Microsoft YaHei", 10, "bold"),
              bg="#F3E5F5", fg="#6A1B9A").pack()
        
        self.path_desc_label = Label(path_frame,
                               text="深入 → 深入 → 回溯 → 深入...",
                               font=("Microsoft YaHei", 9),
                               bg="#F3E5F5", fg="#8E24AA")
        self.path_desc_label.pack()
    
    def _update_depth_view(self):
        """更新深度视图面板"""
        # 清除旧内容
        for widget in self.depth_panel.winfo_children():
            widget.destroy()
        
        if not self.dfs_path:
            Label(self.depth_panel, text="(等待DFS开始)",
                  font=("Microsoft YaHei", 10),
                  bg="#FDFEFE", fg="#BDC3C7").pack(pady=20)
            return
        
        # 显示当前DFS路径
        Label(self.depth_panel, text="📍 当前探索路径:",
              font=("Microsoft YaHei", 10, "bold"),
              bg="#FDFEFE", fg="#2C3E50").pack(anchor=W, pady=(5, 2))
        
        path_frame = Frame(self.depth_panel, bg="#FDFEFE")
        path_frame.pack(fill=X, pady=5)
        
        for i, v in enumerate(self.dfs_path):
            depth = self.vertex_depth.get(v, 0)
            color = get_depth_color(depth)
            is_current = (v == self.current_vertex)
            
            node_label = Label(path_frame, text=str(v),
                              font=("Microsoft YaHei", 11, "bold"),
                              bg=color if is_current else "#ECF0F1",
                              fg="white" if is_current else "#2C3E50",
                              padx=12, pady=5,
                              relief="raised" if is_current else "flat")
            node_label.pack(side=LEFT, padx=2)
            
            if i < len(self.dfs_path) - 1:
                Label(path_frame, text="→", font=("Arial", 12, "bold"),
                      bg="#FDFEFE", fg="#7F8C8D").pack(side=LEFT)
        
        # 显示栈内容
        Label(self.depth_panel, text="\n📚 栈内容 (待探索):",
              font=("Microsoft YaHei", 10, "bold"),
              bg="#FDFEFE", fg="#2C3E50").pack(anchor=W, pady=(10, 2))
        
        stack_frame = Frame(self.depth_panel, bg="#FDFEFE")
        stack_frame.pack(fill=X, pady=5)
        
        if self.visual_stack:
            for v, d in reversed(self.visual_stack[-6:]):  # 只显示最近6个
                color = get_depth_color(d)
                Label(stack_frame, text=f"{v}(D{d})",
                      font=("Microsoft YaHei", 9),
                      bg=color, fg="white",
                      padx=8, pady=3).pack(side=LEFT, padx=2)
            
            if len(self.visual_stack) > 6:
                Label(stack_frame, text=f"...+{len(self.visual_stack)-6}",
                      font=("Microsoft YaHei", 9),
                      bg="#FDFEFE", fg="#7F8C8D").pack(side=LEFT)
        else:
            Label(stack_frame, text="[空栈]",
                  font=("Microsoft YaHei", 9),
                  bg="#FDFEFE", fg="#BDC3C7").pack()
        
        # 更新路径描述
        if self.current_depth > 0:
            self.path_desc_label.config(
                text=f"当前深度: {self.current_depth} | 最大深度: {self.max_depth}")
    
    def _create_legend(self, parent):
        """创建图例"""
        legend_frame = Frame(parent, bg=self.colors["bg"])
        legend_frame.pack(side=RIGHT)
        
        Label(legend_frame, text="图例:", font=("Microsoft YaHei", 8),
              bg=self.colors["bg"], fg="#7F8C8D").pack(side=LEFT, padx=5)
        
        for i, name in enumerate(["D0(起点)", "D1", "D2", "D3+"]):
            color = get_depth_color(i)
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
        self.vertex_count_var = StringVar(value="7")
        Entry(row1, textvariable=self.vertex_count_var, width=3,
              font=("Microsoft YaHei", 10), relief="solid", bd=1).pack(side=LEFT)
        
        Label(row1, text="分支:", font=("Microsoft YaHei", 10),
              bg="#FFFFFF", fg="#2C3E50").pack(side=LEFT, padx=(10, 3))
        self.branch_var = StringVar(value="2")
        Entry(row1, textvariable=self.branch_var, width=3,
              font=("Microsoft YaHei", 10), relief="solid", bd=1).pack(side=LEFT)
        
        Label(row1, text=" | ", bg="#FFFFFF", fg="#BDC3C7").pack(side=LEFT, padx=8)
        
        Label(row1, text="起点:", font=("Microsoft YaHei", 10),
              bg="#FFFFFF", fg="#2C3E50").pack(side=LEFT, padx=(0, 3))
        self.start_vertex_var = StringVar(value="A")
        Entry(row1, textvariable=self.start_vertex_var, width=3,
              font=("Microsoft YaHei", 10), relief="solid", bd=1).pack(side=LEFT)
        
        Label(row1, text=" | ", bg="#FFFFFF", fg="#BDC3C7").pack(side=LEFT, padx=8)
        
        self.dfs_btn = self._create_button(row1, "▶ 开始DFS", "#27AE60", self._start_dfs)
        self.dfs_btn.pack(side=LEFT, padx=3)
        
        self.step_btn = self._create_button(row1, "⏭ 单步", "#3498DB", self._step_dfs)
        self.step_btn.pack(side=LEFT, padx=3)
        
        self.pause_btn = self._create_button(row1, "⏸ 暂停", "#F39C12", self._toggle_pause)
        self.pause_btn.pack(side=LEFT, padx=3)
        
        self.reset_btn = self._create_button(row1, "🔄 重置", "#E74C3C", self._reset_dfs)
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
        
        code = MULTILANG_DFS.get(self.code_language, MULTILANG_DFS[LANG_PSEUDOCODE])
        for i, (text, typ) in enumerate(code):
            fg = self.code_colors["comment"] if typ == "comment" else self.code_colors["fg"]
            lbl = Label(self.code_frame, text=f" {i+1:2d} │ {text}",
                       font=("Consolas", 9), bg=self.code_colors["bg"], fg=fg,
                       anchor="w", padx=2, pady=1)
            lbl.pack(fill=X, anchor="w")
            self.code_labels.append(lbl)
    
    def _highlight_line(self, line: int, status: str = None):
        code = MULTILANG_DFS.get(self.code_language, MULTILANG_DFS[LANG_PSEUDOCODE])
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
    
    # ==================== 绘图 ====================
    
    def _generate_graph(self):
        if self.animating:
            messagebox.showwarning("提示", "请先停止动画")
            return
        
        try:
            n = max(5, min(10, int(self.vertex_count_var.get())))
            b = max(1, min(3, int(self.branch_var.get())))
        except:
            messagebox.showerror("错误", "请输入有效数值")
            return
        
        # 使用DFS友好的图生成器
        self.graph = generate_dfs_friendly_graph(n, b, 5)
        
        if self.graph.get_vertices():
            self.start_vertex_var.set(self.graph.get_vertices()[0])
        
        self._reset_dfs()
        self._draw_graph()
        self._draw_stack()
        
        # 显示图的结构信息
        edge_info = []
        for v in self.graph.get_vertices():
            neighbors = self.graph.get_neighbors(v)
            if neighbors:
                edge_info.append(f"{v}→{','.join(neighbors)}")
        
        self.action_label.config(
            text=f"✅ 已生成DFS演示图\n"
                 f"顶点数: {self.graph.vertex_count()}\n"
                 f"边数: {self.graph.edge_count()}\n\n"
                 f"结构 (父→子):\n" + "\n".join(edge_info[:5]) + 
                 ("\n..." if len(edge_info) > 5 else "") +
                 f"\n\n💡 点击\"开始DFS\"观察深度优先遍历")
    
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
                # 根据深度选择颜色
                if v in self.vertex_depth:
                    color = get_depth_color(self.vertex_depth[v])
                else:
                    color = self.colors["vertex_default"]
                self._draw_vertex(v, pos[0], pos[1], color)
    
    def _draw_vertex(self, label, x, y, color, is_current=False):
        r = 26
        outline = "#9B59B6" if is_current else "#2C3E50"
        width = 4 if is_current else 2
        
        self.graph_canvas.create_oval(x-r, y-r, x+r, y+r, fill=color,
                                      outline=outline, width=width, tags=f"v_{label}")
        
        # 文字颜色
        text_color = "white" if color != self.colors["vertex_default"] else "#2C3E50"
        self.graph_canvas.create_text(x, y, text=str(label),
                                      font=("Microsoft YaHei", 13, "bold"),
                                      fill=text_color, tags=f"t_{label}")
        
        # 显示深度
        if label in self.vertex_depth:
            depth = self.vertex_depth[label]
            self.graph_canvas.create_text(x, y + r + 12, text=f"D{depth}",
                                          font=("Microsoft YaHei", 9, "bold"),
                                          fill=get_depth_color(depth), tags=f"d_{label}")
    
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
        self.graph_canvas.delete(f"d_{v}")
        self._draw_vertex(v, pos[0], pos[1], color, is_current)
    
    def _draw_stack(self):
        """绘制栈可视化（垂直方向）"""
        self.stack_canvas.delete("all")
        
        cell_w, cell_h = 50, 35
        start_x, start_y = 20, 120  # 从底部开始向上绘制
        
        # 标题
        self.stack_canvas.create_text(240, 15, text="栈 (深度颜色标记)",
                                     font=("Microsoft YaHei", 10, "bold"), fill="#2C3E50")
        
        # 绘制栈底部边框
        self.stack_canvas.create_line(start_x, start_y + 5, start_x + 460, start_y + 5,
                                     fill="#2C3E50", width=3)
        self.stack_canvas.create_text(start_x + 230, start_y + 18, text="栈底",
                                     font=("Microsoft YaHei", 9), fill="#7F8C8D")
        
        # 绘制栈元素（从底部向上）
        max_show = 8  # 最多显示8个元素
        stack_to_show = self.visual_stack[-max_show:] if len(self.visual_stack) > max_show else self.visual_stack
        
        for i, (val, depth) in enumerate(stack_to_show):
            x = start_x + i * (cell_w + 4)
            y = start_y - cell_h
            
            # 根据深度确定颜色
            fill = get_depth_color(depth)
            text_color = "white"
            
            # 栈顶特殊标记
            is_top = (i == len(stack_to_show) - 1)
            outline = "#9B59B6" if is_top else "#2C3E50"
            outline_width = 3 if is_top else 2
            
            self.stack_canvas.create_rectangle(x, y, x + cell_w, y + cell_h,
                                              fill=fill, outline=outline, width=outline_width)
            
            # 值
            self.stack_canvas.create_text(x + cell_w / 2, y + cell_h / 2, text=str(val),
                                         font=("Microsoft YaHei", 11, "bold"), fill=text_color)
            
            # 深度标记
            self.stack_canvas.create_text(x + cell_w / 2, y - 10, text=f"D{depth}",
                                         font=("Microsoft YaHei", 8), fill=get_depth_color(depth))
        
        # 栈顶指针
        if stack_to_show:
            top_x = start_x + (len(stack_to_show) - 1) * (cell_w + 4) + cell_w / 2
            self.stack_canvas.create_line(top_x, start_y - cell_h - 25, top_x, start_y - cell_h - 15,
                                         fill="#9B59B6", width=3, arrow=LAST)
            self.stack_canvas.create_text(top_x, start_y - cell_h - 35, text="top",
                                         font=("Microsoft YaHei", 9, "bold"), fill="#9B59B6")
        
        # 如果栈中元素超出显示范围，显示省略号
        if len(self.visual_stack) > max_show:
            self.stack_canvas.create_text(start_x + max_show * (cell_w + 4) + 20, start_y - cell_h / 2,
                                         text=f"...+{len(self.visual_stack) - max_show}",
                                         font=("Microsoft YaHei", 9), fill="#7F8C8D")
        
        # 更新信息标签
        self.stack_info_label.config(
            text=f"栈大小: {len(self.visual_stack)} | 当前深度: {self.current_depth}")
    
    # ==================== DFS控制 ====================
    
    def _update_speed(self, val):
        self.animation_speed = 2900 - int(val)
    
    def _start_dfs(self):
        if not self.graph:
            messagebox.showwarning("提示", "请先生成图")
            return
        
        start = self.start_vertex_var.get().strip().upper()
        if not self.graph.has_vertex(start):
            messagebox.showerror("错误", f"顶点'{start}'不存在")
            return
        
        if self.animating:
            return
        
        self._reset_dfs()
        self._generate_dfs_steps(start)
        self.animating = True
        self._set_buttons_state()
        self._animate_step()
    
    def _generate_dfs_steps(self, start):
        """生成DFS步骤"""
        self.dfs_steps = []
        
        # 初始化
        self.dfs_steps.append(("init", None, None))
        
        # 使用栈进行DFS
        visited = set()
        stack = [(start, 0, None)]  # (顶点, 深度, 父节点)
        
        self.dfs_steps.append(("push", start, 0))
        
        while stack:
            current, depth, parent = stack.pop()
            
            self.dfs_steps.append(("pop", current, depth))
            
            if current in visited:
                self.dfs_steps.append(("skip_visited", current, depth))
                continue
            
            visited.add(current)
            self.dfs_steps.append(("visit", current, depth))
            
            # 检查邻居
            neighbors = self.graph.get_neighbors(current)
            unvisited_neighbors = []
            
            if neighbors:
                self.dfs_steps.append(("explore_start", current, neighbors))
                
                for nb in neighbors:
                    self.dfs_steps.append(("check_edge", current, nb))
                    if nb not in visited:
                        unvisited_neighbors.append(nb)
                        self.dfs_steps.append(("will_push", nb, depth + 1))
                    else:
                        self.dfs_steps.append(("skip", nb, None))
                
                # 逆序入栈（保证按顺序访问）
                for nb in reversed(unvisited_neighbors):
                    self.dfs_steps.append(("push", nb, depth + 1))
                    stack.append((nb, depth + 1, current))
                
                self.dfs_steps.append(("explore_end", current, None))
            
            # 如果没有未访问的邻居且栈非空，可能需要回溯
            if not unvisited_neighbors and stack:
                next_vertex = stack[-1][0]
                next_depth = stack[-1][1]
                if next_depth < depth:
                    self.dfs_steps.append(("backtrack", current, (next_vertex, next_depth)))
        
        self.dfs_steps.append(("done", None, None))
    
    def _step_dfs(self):
        if not self.graph:
            messagebox.showwarning("提示", "请先生成图")
            return
        
        start = self.start_vertex_var.get().strip().upper()
        
        if not self.dfs_steps:
            if not self.graph.has_vertex(start):
                messagebox.showerror("错误", f"顶点'{start}'不存在")
                return
            self._reset_dfs()
            self._generate_dfs_steps(start)
        
        if self.current_step >= len(self.dfs_steps):
            return
        
        self._execute_step(self.dfs_steps[self.current_step])
        self.current_step += 1
    
    def _toggle_pause(self):
        if self.animating:
            self.animating = False
            self.paused = True
            self.pause_btn.config(text="▶ 继续")
        else:
            if self.dfs_steps and self.current_step < len(self.dfs_steps):
                self.animating = True
                self.paused = False
                self.pause_btn.config(text="⏸ 暂停")
                self._animate_step()
    
    def _reset_dfs(self):
        self.animating = False
        self.paused = False
        self.dfs_steps = []
        self.current_step = 0
        self.visited_vertices = set()
        self.stacked_vertices = set()
        self.current_vertex = None
        self.traversal_order = []
        self.vertex_depth = {}
        self.current_depth = 0
        self.max_depth = 0
        self.dfs_path = []
        self.visual_stack = []
        self.highlighted_line = -1
        
        self._render_pseudocode()
        self._draw_graph()
        self._draw_stack()
        self._update_depth_progress()
        self._update_depth_view()
        
        self.result_label.config(text="(未开始)")
        self.path_label.config(text="(未开始)")
        self.action_label.config(text="等待开始...")
        self.status_label.config(text="已重置")
        self.pause_btn.config(text="⏸ 暂停")
        self._set_buttons_state()
    
    def _set_buttons_state(self):
        state = DISABLED if self.animating else NORMAL
        self.gen_btn.config(state=state)
        self.dfs_btn.config(state=state)
        self.step_btn.config(state=state)
    
    def _animate_step(self):
        if not self.animating:
            return
        
        if self.current_step >= len(self.dfs_steps):
            self.animating = False
            self._set_buttons_state()
            return
        
        self._execute_step(self.dfs_steps[self.current_step])
        self.current_step += 1
        
        if self.animating:
            self.window.after(self.animation_speed, self._animate_step)
    
    def _execute_step(self, step):
        action, d1, d2 = step
        
        if action == "init":
            self._highlight_line(2, "初始化")
            self.action_label.config(text="📋 初始化DFS:\n• 创建空栈\n• 创建visited集合\n• 准备深度优先遍历")
            
            # 初始化动画 - 在图中心显示波纹
            cx, cy = 240, 190
            self._create_dive_effect(cx, cy, "#9B59B6")
        
        elif action == "push":
            v, depth = d1, d2
            
            self.visual_stack.append((v, depth))
            self.stacked_vertices.add(v)
            self.vertex_depth[v] = depth
            self.max_depth = max(self.max_depth, depth)
            
            color = get_depth_color(depth)
            self._update_vertex(v, color)
            self._draw_stack()
            self._update_depth_progress()
            self._update_depth_view()
            
            # 入栈动画
            self._animate_stack_push(v, depth, color)
            
            self._highlight_line(4 if depth == 0 else 15, f"入栈: {v}")
            self.action_label.config(
                text=f"📥 入栈: {v} (深度{depth})\n\n"
                     f"• stack.push({v})\n"
                     f"• 栈大小: {len(self.visual_stack)}\n"
                     f"• 该节点深度为 {depth}")
        
        elif action == "pop":
            v, depth = d1, d2
            self.current_vertex = v
            self.current_depth = depth
            
            # 从栈中移除
            if self.visual_stack and self.visual_stack[-1][0] == v:
                self.visual_stack.pop()
            
            color = get_depth_color(depth)
            self._update_vertex(v, color, is_current=True)
            self._draw_stack()
            self._update_depth_progress()
            
            # 出栈动画
            self._animate_stack_pop(v, depth, color)
            
            self._highlight_line(6, f"出栈: {v}")
            self.action_label.config(
                text=f"📤 出栈: {v} (深度{depth})\n\n"
                     f"• current = stack.pop()\n"
                     f"• 栈大小: {len(self.visual_stack)}\n"
                     f"• 当前深度: {depth}")
        
        elif action == "skip_visited":
            v, depth = d1, d2
            self._highlight_line(8, f"跳过已访问: {v}")
            self.action_label.config(
                text=f"⏭️ 跳过节点 {v}\n\n"
                     f"• {v} ∈ visited\n"
                     f"• 该节点已被访问过\n"
                     f"• continue 继续循环")
        
        elif action == "visit":
            v, depth = d1, d2
            self.visited_vertices.add(v)
            self.stacked_vertices.discard(v)
            self.traversal_order.append(v)
            
            # 更新DFS路径
            # 回溯到正确的深度
            while self.dfs_path and self.vertex_depth.get(self.dfs_path[-1], 0) >= depth:
                self.dfs_path.pop()
            self.dfs_path.append(v)
            
            color = get_depth_color(depth)
            self._update_vertex(v, color)
            self._draw_stack()
            self._update_depth_view()
            
            order = " → ".join(str(x) for x in self.traversal_order)
            path = " → ".join(str(x) for x in self.dfs_path)
            self.result_label.config(text=order)
            self.path_label.config(text=path)
            
            # 访问节点的动画效果
            pos = self.graph.get_position(v)
            if pos:
                self._animate_discovery_sparkles(pos[0], pos[1], color)
                self._animate_vertex_glow(v, color, 1.2)
            
            self._highlight_line(11, f"访问: {v}")
            self.action_label.config(
                text=f"✅ 访问节点 {v}\n\n"
                     f"• 深度: {depth}\n"
                     f"• visited.add({v})\n"
                     f"• 已访问序列:\n  {order}\n"
                     f"• 当前路径:\n  {path}")
        
        elif action == "explore_start":
            v, neighbors = d1, d2
            nb_str = ", ".join(str(n) for n in neighbors)
            
            # 探索动画
            pos = self.graph.get_position(v)
            if pos:
                self._animate_scanning_effect(v)
            
            self._highlight_line(13, f"探索{v}的邻居")
            self.action_label.config(
                text=f"🔍 探索 {v} 的所有邻居\n\n"
                     f"📋 邻居列表: [{nb_str}]\n"
                     f"将逆序入栈以保证顺序访问")
        
        elif action == "check_edge":
            u, v = d1, d2
            self._draw_edge(u, v, self.colors["edge_highlight"], 4)
            
            # 边脉冲动画
            is_new = v not in self.visited_vertices
            pulse_color = "#27AE60" if is_new else "#E74C3C"
            self._animate_edge_pulse(u, v, pulse_color)
            
            self._highlight_line(14, f"检查边 {u}→{v}")
            
            status = "✨ 新节点!" if is_new else "⚠️ 已访问"
            self.action_label.config(
                text=f"🔗 检查边: {u} → {v}\n\n"
                     f"• 目标节点: {v}\n"
                     f"• 状态: {status}")
        
        elif action == "will_push":
            v, depth = d1, d2
            self._highlight_line(15, f"准备入栈: {v}")
            
            # 预览光晕
            self._animate_vertex_glow(v, get_depth_color(depth), 0.8)
        
        elif action == "skip":
            v = d1
            if self.current_vertex:
                self._draw_edge(self.current_vertex, v, self.colors["edge_traversed"], 2)
            
            self._highlight_line(14, f"跳过{v}(已访问)")
            self.action_label.config(
                text=f"⏭️ 跳过节点 {v}\n\n"
                     f"• {v} ∈ visited\n"
                     f"• 该节点已被访问过")
        
        elif action == "explore_end":
            v = d1
            for nb in self.graph.get_neighbors(v):
                self._draw_edge(v, nb, self.colors["edge_traversed"], 2)
            self._highlight_line(17, f"{v}的邻居探索完毕")
        
        elif action == "backtrack":
            from_v, to_info = d1, d2
            to_v, to_depth = to_info
            
            # 回溯动画
            self._animate_backtrack(from_v, to_v)
            
            self._highlight_line(5, "回溯")
            self.action_label.config(
                text=f"🔙 回溯!\n\n"
                     f"• 从 {from_v} 回溯\n"
                     f"• 下一个: {to_v} (深度{to_depth})\n"
                     f"• 遇到死胡同，尝试其他分支")
        
        elif action == "done":
            self.animating = False
            self._update_depth_progress()
            self._update_depth_view()
            self._set_buttons_state()
            
            order = " → ".join(str(x) for x in self.traversal_order)
            
            # 完成庆祝动画
            self._celebrate_completion()
            
            self._highlight_line(18, "✅ DFS完成!")
            self.action_label.config(
                text=f"🎉 DFS深度优先遍历完成!\n\n"
                     f"📊 遍历统计:\n"
                     f"• 最大深度: {self.max_depth}\n"
                     f"• 访问顺序: {order}\n\n"
                     f"💡 DFS特点:\n"
                     f"• 沿一条路径深入探索\n"
                     f"• 遇到死胡同再回溯\n"
                     f"• 使用栈保存待访问节点")
    
    # ==================== 动画效果 ====================
    
    def _create_dive_effect(self, x: float, y: float, color: str):
        """创建深度潜入效果"""
        steps = 15
        step_delay = 40
        
        items = []
        
        def animate_dive(step):
            for item in items:
                self.graph_canvas.delete(item)
            items.clear()
            
            if step >= steps:
                return
            
            progress = step / steps
            
            # 向下扩展的箭头/线条效果
            for i in range(3):
                offset = i * 0.2
                if progress > offset:
                    line_progress = min(1, (progress - offset) / 0.6)
                    line_length = 50 * line_progress
                    
                    alpha = 1 - line_progress * 0.5
                    r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
                    fade = int(100 * (1 - alpha))
                    r2 = min(255, r + fade)
                    g2 = min(255, g + fade)
                    b2 = min(255, b + fade)
                    line_color = f"#{r2:02x}{g2:02x}{b2:02x}"
                    
                    item = self.graph_canvas.create_line(
                        x + (i - 1) * 20, y,
                        x + (i - 1) * 20, y + line_length,
                        fill=line_color, width=3, arrow=LAST
                    )
                    items.append(item)
            
            self.window.after(step_delay, lambda: animate_dive(step + 1))
        
        animate_dive(0)
    
    def _animate_stack_push(self, v, depth, color):
        """栈入栈动画"""
        # 简化动画，主要更新栈显示
        self._draw_stack()
    
    def _animate_stack_pop(self, v, depth, color):
        """栈出栈动画"""
        # 简化动画，主要更新栈显示
        self._draw_stack()
    
    def _animate_edge_pulse(self, u, v, color: str):
        """边脉冲动画"""
        pu, pv = self.graph.get_position(u), self.graph.get_position(v)
        if not pu or not pv:
            return
        
        r = 26
        dx, dy = pv[0] - pu[0], pv[1] - pu[1]
        length = math.sqrt(dx * dx + dy * dy)
        if length < 1:
            return
        
        ux, uy = dx / length, dy / length
        sx, sy = pu[0] + r * ux, pu[1] + r * uy
        ex, ey = pv[0] - r * ux, pv[1] - r * uy
        
        steps = ANIMATION_CONFIG["edge_trace_steps"]
        duration = ANIMATION_CONFIG["pulse_duration"]
        step_delay = duration // steps
        
        pulse_items = []
        
        def animate_pulse(step):
            for item in pulse_items:
                self.graph_canvas.delete(item)
            pulse_items.clear()
            
            if step >= steps:
                return
            
            progress = step / steps
            
            pulse_x = sx + (ex - sx) * progress
            pulse_y = sy + (ey - sy) * progress
            
            pulse_size = 8 + 4 * math.sin(progress * math.pi)
            
            item = self.graph_canvas.create_oval(
                pulse_x - pulse_size, pulse_y - pulse_size,
                pulse_x + pulse_size, pulse_y + pulse_size,
                fill=color, outline="white", width=2
            )
            pulse_items.append(item)
            
            self.window.after(step_delay, lambda: animate_pulse(step + 1))
        
        animate_pulse(0)
    
    def _animate_vertex_glow(self, v, color: str, intensity: float = 1.0):
        """顶点光晕动画"""
        pos = self.graph.get_position(v)
        if not pos:
            return
        
        x, y = pos
        duration = ANIMATION_CONFIG["glow_duration"]
        steps = 12
        step_delay = duration // steps
        
        glow_items = []
        
        def animate_glow(step):
            for item in glow_items:
                self.graph_canvas.delete(item)
            glow_items.clear()
            
            if step >= steps:
                return
            
            progress = step / steps
            pulse = 0.5 + 0.5 * math.sin(progress * math.pi * 2)
            
            for layer in range(3, 0, -1):
                glow_radius = 26 + layer * 8 * intensity * pulse
                
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
        """发现节点闪光效果"""
        particle_count = ANIMATION_CONFIG["particle_count"]
        duration = ANIMATION_CONFIG["sparkle_duration"]
        steps = 10
        step_delay = duration // steps
        
        particles = []
        for i in range(particle_count):
            angle = 2 * math.pi * i / particle_count
            speed = 35 + (i % 3) * 12
            particles.append({
                "angle": angle,
                "speed": speed,
                "size": 3 + (i % 2) * 2
            })
        
        particle_items = []
        
        def animate_sparkles(step):
            for item in particle_items:
                self.graph_canvas.delete(item)
            particle_items.clear()
            
            if step >= steps:
                return
            
            progress = step / steps
            
            for p in particles:
                distance = p["speed"] * progress
                px = x + distance * math.cos(p["angle"])
                py = y + distance * math.sin(p["angle"])
                
                size = p["size"] * (1 - progress * 0.7)
                
                r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
                fade = int(200 * progress)
                r2 = min(255, r + fade)
                g2 = min(255, g + fade)
                b2 = min(255, b + fade)
                p_color = f"#{r2:02x}{g2:02x}{b2:02x}"
                
                item = self.graph_canvas.create_oval(
                    px - size, py - size,
                    px + size, py + size,
                    fill=p_color, outline="white", width=1
                )
                particle_items.append(item)
            
            self.window.after(step_delay, lambda: animate_sparkles(step + 1))
        
        animate_sparkles(0)
    
    def _animate_scanning_effect(self, v):
        """雷达扫描效果"""
        pos = self.graph.get_position(v)
        if not pos:
            return
        
        x, y = pos
        steps = 16
        step_delay = 40
        
        items = []
        
        def animate_scan(step):
            for item in items:
                self.graph_canvas.delete(item)
            items.clear()
            
            if step >= steps:
                return
            
            progress = step / steps
            angle = progress * 2 * math.pi
            
            scan_length = 50
            end_x = x + scan_length * math.cos(angle)
            end_y = y + scan_length * math.sin(angle)
            
            depth = self.vertex_depth.get(v, 0)
            color = get_depth_color(depth)
            
            item1 = self.graph_canvas.create_line(
                x, y, end_x, end_y,
                fill=color, width=3, dash=(5, 3)
            )
            items.append(item1)
            
            item2 = self.graph_canvas.create_oval(
                end_x - 5, end_y - 5,
                end_x + 5, end_y + 5,
                fill=color, outline="white", width=2
            )
            items.append(item2)
            
            self.window.after(step_delay, lambda: animate_scan(step + 1))
        
        animate_scan(0)
    
    def _animate_backtrack(self, from_v, to_v):
        """回溯动画"""
        from_pos = self.graph.get_position(from_v)
        to_pos = self.graph.get_position(to_v)
        
        if not from_pos or not to_pos:
            return
        
        steps = 12
        step_delay = 40
        
        items = []
        
        def animate_backtrack_step(step):
            for item in items:
                self.graph_canvas.delete(item)
            items.clear()
            
            if step >= steps:
                return
            
            progress = step / steps
            
            # 绘制回溯路径（虚线）
            current_x = from_pos[0] + (to_pos[0] - from_pos[0]) * progress
            current_y = from_pos[1] + (to_pos[1] - from_pos[1]) * progress
            
            item1 = self.graph_canvas.create_line(
                from_pos[0], from_pos[1],
                current_x, current_y,
                fill="#9B59B6", width=4, dash=(8, 4)
            )
            items.append(item1)
            
            # 回溯指示点
            point_size = 8 + 4 * math.sin(progress * math.pi)
            item2 = self.graph_canvas.create_oval(
                current_x - point_size, current_y - point_size,
                current_x + point_size, current_y + point_size,
                fill="#9B59B6", outline="white", width=2
            )
            items.append(item2)
            
            # 回溯标签
            item3 = self.graph_canvas.create_text(
                (from_pos[0] + current_x) / 2,
                (from_pos[1] + current_y) / 2 - 15,
                text="⟲ 回溯",
                font=("Microsoft YaHei", 9, "bold"),
                fill="#9B59B6"
            )
            items.append(item3)
            
            self.window.after(step_delay, lambda: animate_backtrack_step(step + 1))
        
        animate_backtrack_step(0)
    
    def _celebrate_completion(self):
        """完成庆祝动画"""
        vertices = list(self.traversal_order)
        
        for i, v in enumerate(vertices):
            pos = self.graph.get_position(v)
            if pos:
                depth = self.vertex_depth.get(v, 0)
                color = get_depth_color(depth)
                
                self.window.after(
                    i * 120,
                    lambda x=pos[0], y=pos[1], c=color:
                        self._animate_firework(x, y, c)
                )
    
    def _animate_firework(self, x: float, y: float, color: str):
        """烟花效果"""
        particle_count = 14
        duration = 500
        steps = 12
        step_delay = duration // steps
        
        particles = []
        for i in range(particle_count):
            angle = 2 * math.pi * i / particle_count
            speed = 25 + (i % 3) * 8
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
                t = progress
                distance = p["speed"] * t
                
                px = x + distance * math.cos(p["angle"])
                py = y + distance * math.sin(p["angle"]) + 15 * t * t
                
                size = p["size"] * (1 - progress * 0.5)
                
                r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
                fade = int(150 * progress)
                r2 = max(50, r - fade)
                g2 = max(50, g - fade)
                b2 = max(50, b - fade)
                p_color = f"#{r2:02x}{g2:02x}{b2:02x}"
                
                item = self.graph_canvas.create_oval(
                    px - size, py - size,
                    px + size, py + size,
                    fill=p_color, outline=""
                )
                items.append(item)
            
            self.window.after(step_delay, lambda: animate_firework_step(step + 1))
        
        animate_firework_step(0)


def open_dfs_visualizer(parent_window, stack_model: StackModel, code_language: str = "伪代码"):
    return DFSVisualizer(parent_window, stack_model, code_language)


if __name__ == "__main__":
    root = Tk()
    root.title("测试")
    root.geometry("200x100")
    
    stack = StackModel(10)
    Button(root, text="打开DFS演示", command=lambda: open_dfs_visualizer(root, stack)).pack(pady=30)
    root.mainloop()

