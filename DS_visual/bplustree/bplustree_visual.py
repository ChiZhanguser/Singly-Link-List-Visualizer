from tkinter import *
from tkinter import ttk, messagebox
from typing import Dict, Tuple, List, Optional, Any
from bplustree.bplustree_model import BPlusTree, BPlusNode
from llm import function_dispatcher
import math

# 深色主题颜色常量
THEME_COLORS = {
    "bg_dark": "#0a0f1a",
    "bg_card": "#0d1526",
    "bg_input": "#1a2744",
    "neon_cyan": "#4fd1c5",
    "neon_pink": "#FF2E97",
    "neon_purple": "#9f7aea",
    "neon_blue": "#63b3ed",
    "neon_green": "#68d391",
    "neon_orange": "#f6ad55",
    "neon_yellow": "#fbd38d",
    "neon_red": "#fc8181",
    "text_primary": "#e2e8f0",
    "text_secondary": "#a0aec0",
}

class BPlusVisualizer:
    def __init__(self, root):
        self.window = root
        self.window.title("B+ 树可视化 - 插入与分裂演示")
        self.window.geometry("1500x850")
        self.window.config(bg="#0a0f1a")

        # UI布局参数
        self.left_width = 320
        self.right_width = 340
        self.left_collapsed = False

        main = Frame(self.window, bg="#0a0f1a")
        main.pack(fill=BOTH, expand=True)

        # 左侧控制面板
        self.left_panel = Frame(main, width=self.left_width, bg="#0a0f1a")
        self.left_panel.pack(side=LEFT, fill=Y)
        self.left_panel.pack_propagate(False)

        # status var
        self.status_var = StringVar(value="就绪：请输入键并插入")
        # explanation var - 用于显示当前操作的详细解释
        self.explanation_var = StringVar(value="")
        
        # DSL相关变量
        self.dsl_var = StringVar(value="")
        
        # LLM聊天窗口引用
        self.chat_window = None

        self._build_left_panel()

        # 中间画布容器
        self.center = Frame(main, bg="#0a0f1a")
        self.center.pack(side=LEFT, fill=BOTH, expand=True, padx=8, pady=12)

        # canvas
        self.canvas = Canvas(self.center, bg="#0a0f1a", bd=0, highlightthickness=0)
        self.canvas.pack(fill=BOTH, expand=True, side=LEFT)

        # scrollbars
        self.h_scroll = Scrollbar(self.center, orient=HORIZONTAL, command=self.canvas.xview)
        self.v_scroll = Scrollbar(self.center, orient=VERTICAL, command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=self.h_scroll.set, yscrollcommand=self.v_scroll.set)
        self.h_scroll.pack(fill=X, side=BOTTOM)
        self.v_scroll.pack(fill=Y, side=RIGHT)

        # panning
        self.canvas.bind("<ButtonPress-1>", lambda e: self.canvas.scan_mark(e.x, e.y))
        self.canvas.bind("<B1-Motion>", lambda e: self.canvas.scan_dragto(e.x, e.y, gain=1))

        # 右侧伪代码面板
        self.right_panel = Frame(main, width=self.right_width, bg="#0d1526")
        self.right_panel.pack(side=RIGHT, fill=Y, padx=(0, 12), pady=12)
        self.right_panel.pack_propagate(False)
        
        self._build_pseudocode_panel()

        # 模型与视觉参数 - 阶数改为3以演示更多分裂
        self.tree = BPlusTree(order=3)

        # base visual params
        self.base_node_w = 160
        self.base_node_h = 60
        self.node_w = self.base_node_w
        self.node_h = self.base_node_h
        self.base_level_gap = 140
        self.level_gap = self.base_level_gap
        self.margin_x = 60
        self.top_margin = 120

        # spacing & zoom
        self.min_spacing = self.node_w + 40
        self.zoom_scale = 1.0
        self.fit_mode = True

        # mapping
        self.node_items: Dict[BPlusNode, int] = {}

        # animation state
        self.animating = False
        self.current_insert_key = None
        
        # content bounds for background drawing
        self._content_bounds = None

        # initial draw
        self.redraw()
        
        # 注册到LLM函数调度器
        try:
            function_dispatcher.register_visualizer("bplustree", self)
            print("B+ tree visualizer registered.")
        except Exception as e:
            print("B+ tree registered failed:", e)

    def _build_left_panel(self):
        pad = 14
        
        # 标题区域
        title_frame = Frame(self.left_panel, bg="#0a0f1a")
        title_frame.pack(fill=X, pady=(16, 8))
        Label(title_frame, text="🌳 B+ 树可视化", fg="#4fd1c5",
              font=("Segoe UI", 18, "bold"), bg="#0a0f1a").pack()
        Label(title_frame, text="插入与分裂演示 (order = 3)", bg="#0a0f1a", 
              fg="#718096", font=("Segoe UI", 10)).pack(pady=(4, 0))

        # 分隔线
        Frame(self.left_panel, height=2, bg="#1a2744").pack(fill=X, padx=pad, pady=(12, 16))

        # 输入区域
        input_frame = Frame(self.left_panel, bg="#0a0f1a")
        input_frame.pack(padx=pad, pady=(0, 12), fill=X)
        Label(input_frame, text="📝 输入键值（逗号/空格分隔）：", bg="#0a0f1a", 
              fg="#a0aec0", font=("Segoe UI", 10)).pack(anchor="w")
        self.input_var = StringVar()
        entry = Entry(input_frame, textvariable=self.input_var, font=("Consolas", 12), 
                     bg="#1a2744", fg="#e2e8f0", insertbackground="#e2e8f0",
                     relief=FLAT, bd=8)
        entry.pack(fill=X, pady=(8, 0), ipady=6)
        self.input_var.set("10, 20, 5, 6, 12, 30, 7, 17")

        # 按钮区域
        btn_frame = Frame(self.left_panel, bg="#0a0f1a")
        btn_frame.pack(padx=pad, pady=(8, 12), fill=X)
        
        insert_btn = Button(btn_frame, text="▶ 插入（动画演示）", bg="#38b2ac", fg="white", 
                           bd=0, font=("Segoe UI", 11, "bold"),
                           activebackground="#319795", activeforeground="white",
                           command=self.start_insert_animated, cursor="hand2")
        insert_btn.pack(fill=X, pady=(0, 10), ipady=8)
        
        clear_btn = Button(btn_frame, text="🗑 清空树", bg="#e53e3e", fg="white", 
                          bd=0, font=("Segoe UI", 10),
                          activebackground="#c53030", activeforeground="white",
                          command=self.clear_tree, cursor="hand2")
        clear_btn.pack(fill=X, ipady=6)

        # 分隔线
        Frame(self.left_panel, height=2, bg="#1a2744").pack(fill=X, padx=pad, pady=(12, 12))
        
        # DSL命令输入区域
        dsl_frame = Frame(self.left_panel, bg="#0a0f1a")
        dsl_frame.pack(padx=pad, pady=(0, 12), fill=X)
        
        dsl_title_frame = Frame(dsl_frame, bg="#0a0f1a")
        dsl_title_frame.pack(fill=X)
        
        Label(dsl_title_frame, text="⚡ DSL命令", 
              font=("Segoe UI", 10, "bold"), 
              bg="#0a0f1a", fg=THEME_COLORS["neon_purple"]).pack(side=LEFT)
        
        # DSL帮助按钮
        def show_dsl_help():
            help_text = """
╔══════════════════════════════════════╗
║       📖 B+ 树 DSL 命令帮助           ║
╠══════════════════════════════════════╣
║                                      ║
║  📥 插入操作:                         ║
║    insert 10, 20, 30                 ║
║    add 5, 15, 25                     ║
║                                      ║
║  🔍 查找操作:                         ║
║    search 10                         ║
║    find 20                           ║
║                                      ║
║  🗑️ 清空操作:                         ║
║    clear                             ║
║    reset                             ║
║                                      ║
║  ℹ️ 帮助:                             ║
║    help                              ║
║                                      ║
║  💡 提示:                             ║
║    直接输入数字也会当作insert处理     ║
║    例如: 10, 20, 30, 40              ║
║                                      ║
╚══════════════════════════════════════╝
            """
            messagebox.showinfo("DSL 命令帮助", help_text)
        
        help_btn = Button(dsl_title_frame, text="?", 
                         font=("Segoe UI", 8, "bold"),
                         bg="#2d3748", fg="white",
                         activebackground="#4a5568",
                         bd=0, padx=6, pady=1,
                         cursor="hand2",
                         command=show_dsl_help)
        help_btn.pack(side=RIGHT)
        
        # DSL输入框
        dsl_entry = Entry(dsl_frame, textvariable=self.dsl_var, 
                         font=("Consolas", 11), 
                         bg="#1a2744", fg=THEME_COLORS["text_primary"], 
                         insertbackground=THEME_COLORS["neon_purple"],
                         relief=FLAT, bd=8)
        dsl_entry.pack(fill=X, pady=(8, 0), ipady=4)
        dsl_entry.bind("<Return>", lambda e: self._execute_dsl())
        dsl_entry.bind("<KP_Enter>", lambda e: self._execute_dsl())
        
        # DSL执行按钮
        dsl_exec_btn = Button(dsl_frame, text="▶ 执行DSL",
                             font=("Segoe UI", 10, "bold"),
                             bg=THEME_COLORS["neon_purple"], fg="white",
                             activebackground="#805ad5",
                             activeforeground="white",
                             bd=0,
                             cursor="hand2",
                             command=self._execute_dsl)
        dsl_exec_btn.pack(fill=X, pady=(8, 0), ipady=6)

        # 分隔线
        Frame(self.left_panel, height=2, bg="#1a2744").pack(fill=X, padx=pad, pady=(12, 12))

        # 缩放控制
        zoom_frame = Frame(self.left_panel, bg="#0a0f1a")
        zoom_frame.pack(padx=pad, fill=X)
        Label(zoom_frame, text="🔍 视图控制：", bg="#0a0f1a", fg="#a0aec0",
              font=("Segoe UI", 10)).pack(anchor="w", pady=(0, 6))
        
        btn_row = Frame(zoom_frame, bg="#0a0f1a")
        btn_row.pack(fill=X)
        Button(btn_row, text="居中", command=self.center_view, width=6, 
               bg="#4299e1", fg="white", bd=0, font=("Segoe UI", 9, "bold")).pack(side=LEFT)
        Button(btn_row, text="适应", command=self.toggle_fit_mode, width=6, 
               bg="#2d3748", fg="#e2e8f0", bd=0, font=("Segoe UI", 9)).pack(side=LEFT, padx=(6, 0))
        Button(btn_row, text="+", command=self.zoom_in, width=3, 
               bg="#2d3748", fg="#e2e8f0", bd=0, font=("Segoe UI", 9)).pack(side=LEFT, padx=(6, 0))
        Button(btn_row, text="-", command=self.zoom_out, width=3, 
               bg="#2d3748", fg="#e2e8f0", bd=0, font=("Segoe UI", 9)).pack(side=LEFT, padx=(4, 0))

        # 分隔线
        Frame(self.left_panel, height=2, bg="#1a2744").pack(fill=X, padx=pad, pady=(16, 12))

        # 当前操作说明框
        explain_frame = Frame(self.left_panel, bg="#1a2744", bd=0)
        explain_frame.pack(fill=X, padx=pad, pady=(0, 12))
        
        explain_header = Frame(explain_frame, bg="#2d3748")
        explain_header.pack(fill=X)
        Label(explain_header, text="💡 当前操作说明", bg="#2d3748", fg="#fbd38d", 
              font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=10, pady=6)
        
        self.explanation_label = Label(explain_frame, textvariable=self.explanation_var, 
              bg="#1a2744", wraplength=self.left_width - 40, justify=LEFT, fg="#e2e8f0",
              font=("Segoe UI", 9))
        self.explanation_label.pack(padx=10, pady=10, anchor="w")

        # 分隔线
        Frame(self.left_panel, height=2, bg="#1a2744").pack(fill=X, padx=pad, pady=(0, 12))

        # 叶节点列表
        Label(self.left_panel, text="🍃 叶节点链表（从左到右）：", bg="#0a0f1a", 
              fg="#a0aec0", font=("Segoe UI", 10)).pack(anchor="w", padx=pad)
        self.leaf_listbox = Listbox(self.left_panel, height=5, bg="#1a2744", fg="#e2e8f0", 
                                   bd=0, highlightthickness=0, font=("Consolas", 10),
                                   selectbackground="#38b2ac")
        self.leaf_listbox.pack(fill=X, padx=pad, pady=(8, 12))

        # 状态栏
        Frame(self.left_panel, height=2, bg="#1a2744").pack(fill=X, padx=pad, pady=(0, 8))
        self.status_label = Label(self.left_panel, textvariable=self.status_var, 
                                 bg="#0a0f1a", wraplength=self.left_width - 30, 
                                 justify=LEFT, fg="#68d391", font=("Segoe UI", 9))
        self.status_label.pack(padx=pad, pady=(0, 12))

    def _build_pseudocode_panel(self):
        """构建右侧伪代码面板"""
        pad = 12
        
        # 标题
        header = Frame(self.right_panel, bg="#1a2744")
        header.pack(fill=X)
        Label(header, text="📜 插入算法伪代码", bg="#1a2744", fg="#63b3ed",
              font=("Segoe UI", 12, "bold")).pack(pady=10)

        # 伪代码容器
        code_container = Frame(self.right_panel, bg="#0d1526")
        code_container.pack(fill=BOTH, expand=True, padx=pad, pady=(0, pad))

        # 创建 Canvas 用于滚动
        self.code_canvas = Canvas(code_container, bg="#0d1526", highlightthickness=0)
        code_scrollbar = Scrollbar(code_container, orient=VERTICAL, command=self.code_canvas.yview)
        
        self.code_frame = Frame(self.code_canvas, bg="#0d1526")
        
        self.code_canvas.configure(yscrollcommand=code_scrollbar.set)
        code_scrollbar.pack(side=RIGHT, fill=Y)
        self.code_canvas.pack(side=LEFT, fill=BOTH, expand=True)
        
        self.code_window = self.code_canvas.create_window((0, 0), window=self.code_frame, anchor="nw")
        
        self.code_frame.bind("<Configure>", lambda e: self.code_canvas.configure(
            scrollregion=self.code_canvas.bbox("all")))
        self.code_canvas.bind("<Configure>", lambda e: self.code_canvas.itemconfig(
            self.code_window, width=e.width))

        # 伪代码行
        self.pseudocode_lines = [
            ("", "B+ 树插入算法", "title"),
            ("", "", "blank"),
            ("START", "procedure INSERT(key):", "header"),
            ("", "", "blank"),
            ("FIND_START", "  // 第一步：查找插入位置", "comment"),
            ("FIND_ROOT", "  node ← root", "code"),
            ("FIND_LOOP", "  while node 不是叶节点:", "code"),
            ("FIND_KEY", "    找到第一个 key[i] > key 的位置 i", "code"),
            ("FIND_CHILD", "    node ← children[i]", "code"),
            ("FIND_END", "  // 现在 node 是目标叶节点", "comment"),
            ("", "", "blank"),
            ("INSERT_START", "  // 第二步：插入键值", "comment"),
            ("INSERT_KEY", "  在 node.keys 中有序插入 key", "code"),
            ("INSERT_CHECK", "  // 检查是否需要分裂", "comment"),
            ("", "", "blank"),
            ("SPLIT_START", "  // 第三步：处理溢出", "comment"),
            ("SPLIT_LOOP", "  while node.keys 数量 > order-1:", "code"),
            ("SPLIT_DO", "    // 节点溢出，需要分裂", "comment"),
            ("SPLIT_MID", "    mid ← ⌈len(keys)/2⌉", "code"),
            ("SPLIT_LEFT", "    左节点 ← keys[0:mid]", "code"),
            ("SPLIT_RIGHT", "    右节点 ← keys[mid:]", "code"),
            ("SPLIT_PROMOTE", "    提升键 ← 右节点第一个键(叶)/中间键(内)", "code"),
            ("SPLIT_PARENT", "    将提升键插入父节点", "code"),
            ("SPLIT_NEWROOT", "    if 无父节点: 创建新根节点", "code"),
            ("SPLIT_UP", "    node ← 父节点 (继续向上检查)", "code"),
            ("", "", "blank"),
            ("END", "  return 插入成功", "header"),
        ]

        self.code_labels: Dict[str, Label] = {}
        
        for step_id, text, style in self.pseudocode_lines:
            frame = Frame(self.code_frame, bg="#0d1526")
            frame.pack(fill=X, anchor="w")
            
            if style == "title":
                lbl = Label(frame, text=text, bg="#0d1526", fg="#fbd38d",
                           font=("Consolas", 11, "bold"))
            elif style == "header":
                lbl = Label(frame, text=text, bg="#0d1526", fg="#9f7aea",
                           font=("Consolas", 10, "bold"))
            elif style == "comment":
                lbl = Label(frame, text=text, bg="#0d1526", fg="#718096",
                           font=("Consolas", 9, "italic"))
            elif style == "blank":
                lbl = Label(frame, text=" ", bg="#0d1526", font=("Consolas", 6))
            else:  # code
                lbl = Label(frame, text=text, bg="#0d1526", fg="#a0aec0",
                           font=("Consolas", 9))
            
            lbl.pack(anchor="w", padx=8, pady=1)
            
            if step_id:
                self.code_labels[step_id] = lbl

        # 图例
        Frame(self.right_panel, height=2, bg="#1a2744").pack(fill=X, padx=pad, pady=(8, 8))
        
        legend_frame = Frame(self.right_panel, bg="#0d1526")
        legend_frame.pack(fill=X, padx=pad, pady=(0, 8))
        
        Label(legend_frame, text="📊 颜色说明：", bg="#0d1526", fg="#a0aec0",
              font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 6))
        
        legends = [
            ("#fbd38d", "🟡 正在访问的节点"),
            ("#68d391", "🟢 插入成功"),
            ("#fc8181", "🔴 节点分裂"),
            ("#63b3ed", "🔵 新创建的节点"),
        ]
        
        for color, text in legends:
            row = Frame(legend_frame, bg="#0d1526")
            row.pack(fill=X, pady=2)
            Canvas(row, width=14, height=14, bg="#0d1526", highlightthickness=0).pack(side=LEFT, padx=(0, 8))
            Label(row, text=text, bg="#0d1526", fg=color, font=("Segoe UI", 8)).pack(side=LEFT)

    def highlight_pseudocode(self, step_ids: List[str], clear_others: bool = True):
        """高亮指定的伪代码行"""
        if clear_others:
            # 重置所有行
            for sid, lbl in self.code_labels.items():
                lbl.config(bg="#0d1526")
                # 根据类型恢复颜色
                for line_id, text, style in self.pseudocode_lines:
                    if line_id == sid:
                        if style == "header":
                            lbl.config(fg="#9f7aea")
                        elif style == "comment":
                            lbl.config(fg="#718096")
                        else:
                            lbl.config(fg="#a0aec0")
                        break
        
        # 高亮指定行
        for step_id in step_ids:
            if step_id in self.code_labels:
                self.code_labels[step_id].config(bg="#2d4a3e", fg="#68d391")
                # 滚动到可见
                self.code_labels[step_id].update_idletasks()

    def toggle_fit_mode(self):
        self.fit_mode = not self.fit_mode
        self.update_status(f"适应模式: {'开' if self.fit_mode else '关'}")
        self.redraw()

    def zoom_in(self):
        self.zoom_scale *= 1.15
        self._apply_zoom()
        self.update_status(f"缩放: {self.zoom_scale:.2f}")
        self.redraw()

    def zoom_out(self):
        self.zoom_scale /= 1.15
        self._apply_zoom()
        self.update_status(f"缩放: {self.zoom_scale:.2f}")
        self.redraw()

    def _apply_zoom(self):
        self.node_w = max(60, int(self.base_node_w * self.zoom_scale))
        self.node_h = max(28, int(self.base_node_h * self.zoom_scale))
        self.level_gap = max(60, int(self.base_level_gap * self.zoom_scale))
        self.min_spacing = self.node_w + 40

    def update_status(self, txt: str):
        self.status_var.set(txt)
        
    def update_explanation(self, txt: str):
        """更新操作解释"""
        self.explanation_var.set(txt)

    def parse_input_keys(self) -> List[Any]:
        text = self.input_var.get().strip()
        if not text:
            return []
        parts = [p.strip() for p in text.replace(",", " ").split() if p.strip()]
        out: List[Any] = []
        for p in parts:
            try:
                out.append(int(p))
            except:
                out.append(p)
        return out

    def compute_positions(self) -> Dict[BPlusNode, Tuple[float, float]]:
        """
        使用自底向上的布局算法，确保：
        1. 叶节点按顺序均匀排列
        2. 每个父节点位于其子节点的中心
        3. 节点之间不会重叠
        """
        pos: Dict[BPlusNode, Tuple[float, float]] = {}
        levels = self.tree.nodes_by_level()
        if not levels:
            return pos
        
        max_depth = max(levels.keys())

        self.canvas.update_idletasks()
        canvas_w = max(self.canvas.winfo_width(), 800)
        canvas_h = max(self.canvas.winfo_height(), 500)
        
        # 计算垂直间距
        vgap = max(120, self.level_gap)
        
        # 计算叶节点数量，确定水平间距
        leaves = self.tree.leaves()
        num_leaves = max(len(leaves), 1)
        
        # 节点水平间距（确保节点之间有足够空间）
        min_h_spacing = self.node_w + 40  # 节点宽度 + 间隙
        
        # 计算所需的总宽度
        total_width_needed = num_leaves * min_h_spacing
        
        # 计算内容区域的边界（确保有足够的边距）
        content_padding = 150  # 内容区域两侧的padding
        
        # 始终从固定的起点开始，确保内容居中
        # 计算实际需要的画布宽度
        actual_content_width = total_width_needed + 2 * content_padding
        
        # 如果内容比画布小，居中显示；否则从左边开始
        if actual_content_width <= canvas_w:
            start_x = (canvas_w - total_width_needed) / 2 + min_h_spacing / 2
        else:
            start_x = content_padding + min_h_spacing / 2
        
        h_spacing = min_h_spacing
        
        # 第一步：为叶节点分配位置（从左到右）
        leaf_y = self.top_margin + max_depth * vgap
        for i, leaf in enumerate(leaves):
            x = start_x + i * h_spacing
            pos[leaf] = (x, leaf_y)
        
        # 第二步：自底向上，为每个内部节点分配位置（位于子节点中心）
        for depth in range(max_depth - 1, -1, -1):
            nodes = levels.get(depth, [])
            y = self.top_margin + depth * vgap
            
            for node in nodes:
                if node.is_leaf:
                    continue  # 叶节点已处理
                
                # 计算子节点的位置范围
                child_positions = [pos[child][0] for child in node.children if child in pos]
                
                if child_positions:
                    # 父节点位于子节点的中心
                    x = (min(child_positions) + max(child_positions)) / 2
                else:
                    x = canvas_w / 2
                
                pos[node] = (x, y)
        
        # 保存内容边界信息供背景绘制使用
        if pos:
            all_x = [p[0] for p in pos.values()]
            all_y = [p[1] for p in pos.values()]
            self._content_bounds = (
                min(all_x) - self.node_w / 2 - content_padding,
                min(all_y) - self.node_h / 2 - 50,
                max(all_x) + self.node_w / 2 + content_padding,
                max(all_y) + self.node_h / 2 + 50
            )
        else:
            self._content_bounds = (0, 0, canvas_w, canvas_h)
        
        return pos

    def _draw_gradient_background(self, bounds=None):
        """绘制渐变背景，覆盖指定的边界区域"""
        canvas_w = max(self.canvas.winfo_width(), 800)
        canvas_h = max(self.canvas.winfo_height(), 600)
        
        # 使用内容边界或画布大小
        if bounds:
            l, t, r, b = bounds
            # 确保背景至少覆盖画布可见区域
            x_start = min(l, 0) - 100
            y_start = min(t, 0) - 100
            x_end = max(r, canvas_w) + 100
            y_end = max(b, canvas_h) + 100
        else:
            x_start, y_start = -100, -100
            x_end, y_end = canvas_w + 100, canvas_h + 100
        
        w = x_end - x_start
        h = y_end - y_start
        
        # 深色渐变背景
        stops = ["#0a0f1a", "#0d1526", "#101b30", "#0d1526", "#0a0f1a"]
        steps = 60
        
        def interp(c1, c2, t):
            r1, g1, b1 = int(c1[1:3], 16), int(c1[3:5], 16), int(c1[5:7], 16)
            r2, g2, b2 = int(c2[1:3], 16), int(c2[3:5], 16), int(c2[5:7], 16)
            r = int(r1 + (r2 - r1) * t)
            g = int(g1 + (g2 - g1) * t)
            b = int(b1 + (b2 - b1) * t)
            return f"#{r:02x}{g:02x}{b:02x}"
        
        for i in range(steps):
            t = i / max(1, steps - 1)
            idx = int(t * (len(stops) - 1))
            t2 = (t * (len(stops) - 1)) - idx
            c = interp(stops[idx], stops[min(idx + 1, len(stops) - 1)], t2)
            y0 = y_start + int(i * (h / steps))
            y1 = y_start + int((i + 1) * (h / steps))
            self.canvas.create_rectangle(x_start, y0, x_end, y1, outline="", fill=c)
        
        # 网格
        grid = "#151f35"
        grid_start_x = int(x_start // 60) * 60
        grid_start_y = int(y_start // 60) * 60
        for gx in range(grid_start_x, int(x_end) + 60, 60):
            self.canvas.create_line(gx, y_start, gx, y_end, fill=grid)
        for gy in range(grid_start_y, int(y_end) + 60, 60):
            self.canvas.create_line(x_start, gy, x_end, gy, fill=grid)

    def _rounded_rect(self, left, top, right, bottom, r=10, **kwargs):
        ids = []
        ids.append(self.canvas.create_rectangle(left + r, top, right - r, bottom, **kwargs))
        ids.append(self.canvas.create_rectangle(left, top + r, right, bottom - r, **kwargs))
        ids.append(self.canvas.create_oval(left, top, left + 2 * r, top + 2 * r, **kwargs))
        ids.append(self.canvas.create_oval(right - 2 * r, top, right, top + 2 * r, **kwargs))
        ids.append(self.canvas.create_oval(left, bottom - 2 * r, left + 2 * r, bottom, **kwargs))
        ids.append(self.canvas.create_oval(right - 2 * r, bottom - 2 * r, right, bottom, **kwargs))
        return ids

    def center_view(self):
        """将视图居中到树的中心位置"""
        bbox = self.canvas.bbox("all")
        if not bbox:
            return
        l, t, r, b = bbox
        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()
        
        # 计算内容中心
        content_cx = (l + r) / 2
        content_cy = (t + b) / 2
        content_w = r - l
        content_h = b - t
        
        # 计算滚动位置使内容居中
        scroll_l, scroll_t, scroll_r, scroll_b = self.canvas.cget("scrollregion").split()
        scroll_l, scroll_t, scroll_r, scroll_b = float(scroll_l), float(scroll_t), float(scroll_r), float(scroll_b)
        scroll_w = scroll_r - scroll_l
        scroll_h = scroll_b - scroll_t
        
        if scroll_w > 0 and scroll_h > 0:
            # 计算使内容居中的滚动位置
            target_x = (content_cx - canvas_w / 2 - scroll_l) / scroll_w
            target_y = (content_cy - canvas_h / 2 - scroll_t) / scroll_h
            
            target_x = max(0, min(1, target_x))
            target_y = max(0, min(1, target_y))
            
            self.canvas.xview_moveto(target_x)
            self.canvas.yview_moveto(target_y)

    def redraw(self, highlight: Optional[Dict[BPlusNode, str]] = None, 
               highlight_edges: Optional[List[Tuple[BPlusNode, BPlusNode]]] = None,
               inserting_key: Any = None):
        self.window.update_idletasks()
        
        self.canvas.delete("all")
        self.node_items.clear()

        # 先计算位置以获取内容边界
        pos = self.compute_positions()
        
        # 获取内容边界用于背景绘制
        content_bounds = getattr(self, '_content_bounds', None)
        self._draw_gradient_background(content_bounds)

        # 显示当前插入的键（固定在视口位置）
        if inserting_key is not None:
            self.canvas.create_text(80, 30, 
                                   text=f"正在插入: {inserting_key}",
                                   font=("Segoe UI", 14, "bold"), fill="#fbd38d", anchor="w",
                                   tags="fixed_ui")

        # 图例（固定位置）
        legend_y = 60
        legend_x = 20
        self.canvas.create_text(legend_x, legend_y, text="图例：",
                               font=("Segoe UI", 10, "bold"), fill="#a0aec0", anchor="w",
                               tags="fixed_ui")
        
        items = [
            (60, "#fbd38d", "访问中"),
            (140, "#68d391", "已插入"),
            (220, "#fc8181", "分裂"),
            (300, "#63b3ed", "新节点"),
        ]
        for offset, color, text in items:
            self.canvas.create_oval(legend_x + offset, legend_y - 6, 
                                   legend_x + offset + 12, legend_y + 6,
                                   fill=color, outline="", tags="fixed_ui")
            self.canvas.create_text(legend_x + offset + 18, legend_y, 
                                   text=text, font=("Segoe UI", 9), 
                                   fill="#e2e8f0", anchor="w", tags="fixed_ui")

        # pos已在前面计算过
        if not pos:
            self.canvas.create_text(400, 300, text="空树（请输入键并插入）",
                                   font=("Segoe UI", 18), fill="#718096")
            self.canvas.create_text(400, 340, 
                                   text="order = 3，每个节点最多 2 个键",
                                   font=("Segoe UI", 12), fill="#4a5568")
            self.canvas.config(scrollregion=(0, 0, 1000, 700))
            self._refresh_leaf_list()
            return

        # 绘制边（高亮特定路径）
        for node, (cx, cy) in pos.items():
            if not node.is_leaf:
                for child in node.children:
                    if child in pos:
                        px, py = pos[child]
                        # 检查是否需要高亮这条边
                        is_highlighted = False
                        if highlight_edges:
                            for parent, child_node in highlight_edges:
                                if parent == node and child_node == child:
                                    is_highlighted = True
                                    break
                        
                        if is_highlighted:
                            # 高亮路径 - 动态效果
                            self.canvas.create_line(cx, cy + self.node_h / 2, 
                                                   px, py - self.node_h / 2,
                                                   width=8, fill="#fbd38d", smooth=True)
                            self.canvas.create_line(cx, cy + self.node_h / 2, 
                                                   px, py - self.node_h / 2,
                                                   width=4, fill="#f6e05e", smooth=True)
                        else:
                            # 普通边
                            self.canvas.create_line(cx, cy + self.node_h / 2, 
                                                   px, py - self.node_h / 2,
                                                   width=3, fill="#1a2744", smooth=True)
                            self.canvas.create_line(cx, cy + self.node_h / 2, 
                                                   px, py - self.node_h / 2,
                                                   width=2, fill="#4fd1c5", smooth=True)

        # 绘制节点
        for node, (cx, cy) in pos.items():
            color = None
            if highlight and node in highlight:
                color = highlight[node]
            self._draw_node(node, cx, cy, fill_color=color)

        # 绘制叶节点链表指针
        for leaf in self.tree.leaves():
            pos_map = pos
            if leaf in pos_map and leaf.next in pos_map:
                lx, ly = pos_map[leaf]
                nx, ny = pos_map[leaf.next]
                left = lx + self.node_w / 2
                right = nx - self.node_w / 2
                # 链表箭头
                self.canvas.create_line(left + 5, ly + 8, right - 5, ny + 8, 
                                       arrow=LAST, dash=(4, 3), 
                                       fill="#63b3ed", width=2)

        bbox = self.canvas.bbox("all")
        if bbox:
            l, t, r, b = bbox
            pad = 150
            # 设置滚动区域，确保有足够的边距
            scroll_l = min(l - pad, -pad)
            scroll_t = min(t - pad, -pad)
            scroll_r = max(r + pad, self.canvas.winfo_width() + pad)
            scroll_b = max(b + pad, self.canvas.winfo_height() + pad)
            
            self.canvas.config(scrollregion=(scroll_l, scroll_t, scroll_r, scroll_b))
            
            # 自动居中显示
            if self.fit_mode:
                self.window.after(10, self.center_view)

        self._refresh_leaf_list()

    def _draw_node(self, node: BPlusNode, cx: float, cy: float, fill_color: Optional[str] = None):
        left = cx - self.node_w / 2
        top = cy - self.node_h / 2
        right = cx + self.node_w / 2
        bottom = cy + self.node_h / 2

        # 根据状态选择颜色和边框
        if fill_color:
            base_fill = fill_color
            if fill_color == "#fbd38d":  # 访问中 - 黄色
                border_color = "#f6ad55"
                border_width = 3
                glow_color = "#744210"
            elif fill_color == "#68d391":  # 插入成功 - 绿色
                border_color = "#48bb78"
                border_width = 3
                glow_color = "#22543d"
            elif fill_color == "#fc8181":  # 分裂 - 红色
                border_color = "#f56565"
                border_width = 3
                glow_color = "#742a2a"
            elif fill_color == "#63b3ed":  # 新节点 - 蓝色
                border_color = "#4299e1"
                border_width = 3
                glow_color = "#2a4365"
            else:
                border_color = "#4fd1c5"
                border_width = 2
                glow_color = "#1a4544"
        else:
            if node.is_leaf:
                base_fill = "#1a2744"
                border_color = "#4fd1c5"
            else:
                base_fill = "#1e3a5f"
                border_color = "#9f7aea"
            border_width = 2
            glow_color = "#0d1526"

        # 外层光晕
        glow_l, glow_t, glow_r, glow_b = left - 4, top - 4, right + 4, bottom + 4
        self._rounded_rect(glow_l, glow_t, glow_r, glow_b, r=12, fill=glow_color, outline="")
        
        # 主卡片
        self._rounded_rect(left, top, right, bottom, r=8, fill=base_fill,
                          outline=border_color, width=border_width)
        
        # 节点类型标签
        node_type = "LEAF" if node.is_leaf else "INTERNAL"
        type_color = "#4fd1c5" if node.is_leaf else "#9f7aea"
        self.canvas.create_text(cx, top - 12, text=node_type,
                               font=("Consolas", 8, "bold"), fill=type_color)

        # 键值 - 使用分隔符显示
        if node.keys:
            # 绘制键值分隔
            key_width = (right - left - 20) / max(len(node.keys), 1)
            for i, key in enumerate(node.keys):
                kx = left + 10 + key_width * i + key_width / 2
                self.canvas.create_text(kx, cy, text=str(key),
                                       font=("Consolas", 13, "bold"), fill="#e2e8f0")
                if i < len(node.keys) - 1:
                    sep_x = left + 10 + key_width * (i + 1)
                    self.canvas.create_line(sep_x, top + 8, sep_x, bottom - 8,
                                           fill="#4a5568", width=1)
        else:
            self.canvas.create_text(cx, cy, text="∅",
                                   font=("Consolas", 12), fill="#718096")

        # 显示键的数量和容量
        max_keys = self.tree.order - 1
        key_info = f"{len(node.keys)}/{max_keys}"
        info_color = "#fc8181" if len(node.keys) >= max_keys else "#718096"
        self.canvas.create_text(cx, bottom + 12, text=key_info,
                               font=("Consolas", 8), fill=info_color)

    def _refresh_leaf_list(self):
        self.leaf_listbox.delete(0, END)
        leaves = self.tree.leaves()
        for i, leaf in enumerate(leaves):
            arrow = " → " if i < len(leaves) - 1 else ""
            self.leaf_listbox.insert(END, f"[{', '.join(str(k) for k in leaf.keys)}]{arrow}")

    def clear_tree(self):
        if self.animating:
            return
        self.tree.clear()
        self.redraw()
        self.update_status("已清空 B+ 树")
        self.update_explanation("")
        self.highlight_pseudocode([])
    
    def set_chat_window(self, chat_window):
        """设置LLM聊天窗口引用"""
        self.chat_window = chat_window
    
    def _execute_dsl(self, event=None):
        """执行DSL输入框中的命令"""
        if self.animating:
            messagebox.showinfo("提示", "当前正在执行动画，请稍后再试。")
            return
        
        raw = (self.dsl_var.get() or "").strip()
        if not raw:
            return
        
        try:
            from DSL_utils import process_command
            process_command(self, raw)
        except Exception as e:
            messagebox.showerror("DSL 执行错误", f"执行 DSL 时出错: {e}")
            self.update_status(f"DSL 错误: {e}")
        finally:
            try:
                self.dsl_var.set("")
            except:
                pass

    def start_insert_animated(self):
        if self.animating:
            return
        keys = self.parse_input_keys()
        if not keys:
            messagebox.showinfo("提示", "请输入要插入的键（逗号/空格分隔）")
            return
        self.animating = True
        key_idx = 0

        def process_next():
            nonlocal key_idx
            if key_idx >= len(keys):
                self.animating = False
                self.update_status("✓ 批量插入完成")
                self.update_explanation("所有键已成功插入到 B+ 树中\n可以查看左侧叶节点链表验证结果")
                self.highlight_pseudocode(["END"])
                return
            k = keys[key_idx]
            key_idx += 1
            self.current_insert_key = k
            self.update_status(f"▶ 开始插入：{k} (进度 {key_idx}/{len(keys)})")
            events = self.tree.insert_with_steps(k)
            self._animate_events(events, k, lambda: self.window.after(300, process_next))

        self.highlight_pseudocode(["START"])
        self.window.after(500, process_next)

    def _animate_events(self, events: List[Dict], inserting_key: Any, callback):
        i = 0
        visit_count = 0
        
        def step():
            nonlocal i, visit_count
            if i >= len(events):
                self.redraw(inserting_key=inserting_key)
                callback()
                return
            ev = events[i]
            evtype = ev.get('type')
            
            if evtype == 'visit':
                node = ev['node']
                visit_count += 1
                
                # 计算访问路径（从根到当前节点的边）
                edges = []
                current = node
                while current.parent:
                    edges.append((current.parent, current))
                    current = current.parent
                
                self.redraw(highlight={node: "#fbd38d"}, highlight_edges=edges,
                           inserting_key=inserting_key)
                
                # 高亮对应的伪代码
                if node.is_leaf:
                    self.highlight_pseudocode(["FIND_END"])
                    node_type = "叶节点"
                    explain = f"✓ 到达目标叶节点\n\n"
                    explain += f"节点内容: [{', '.join(str(k) for k in node.keys)}]\n"
                    explain += f"将在此节点插入键 {inserting_key}"
                else:
                    if visit_count == 1:
                        self.highlight_pseudocode(["FIND_ROOT", "FIND_LOOP"])
                    else:
                        self.highlight_pseudocode(["FIND_KEY", "FIND_CHILD"])
                    node_type = "内部节点"
                    explain = f"访问{node_type}（第 {visit_count} 步）\n\n"
                    explain += f"节点键: [{', '.join(str(k) for k in node.keys)}]\n"
                    explain += f"比较 {inserting_key} 与节点中的键\n"
                    explain += f"选择合适的子节点继续向下查找"

                self.update_status(f"🔍 访问{node_type}: [{', '.join(str(k) for k in node.keys)}]")
                self.update_explanation(explain)
                
                i += 1
                self.window.after(600, step)
                
            elif evtype == 'insert':
                node = ev['node']
                self.redraw(highlight={node: "#68d391"}, inserting_key=inserting_key)
                
                self.highlight_pseudocode(["INSERT_KEY", "INSERT_CHECK"])
                
                self.update_status(f"✓ 插入成功: {inserting_key} → [{', '.join(str(k) for k in node.keys)}]")

                max_keys = self.tree.order - 1
                explain = f"键 {inserting_key} 已插入到叶节点\n\n"
                explain += f"当前节点: [{', '.join(str(k) for k in node.keys)}]\n"
                explain += f"节点容量: {len(node.keys)}/{max_keys}\n\n"
                if len(node.keys) > max_keys:
                    explain += f"⚠️ 节点溢出！需要分裂"
                elif len(node.keys) == max_keys:
                    explain += f"节点已满，再插入将触发分裂"
                else:
                    explain += f"节点未满，无需分裂"
                self.update_explanation(explain)
                
                i += 1
                self.window.after(800, step)
                
            elif evtype == 'split':
                node = ev['node']
                new_node = ev.get('new_node')
                promoted = ev.get('promoted')
                is_leaf = ev.get('is_leaf', False)
                
                hl = {node: "#fc8181"}
                if new_node is not None:
                    hl[new_node] = "#63b3ed"

                self.redraw(highlight=hl, inserting_key=inserting_key)
                    
                # 高亮分裂相关的伪代码
                self.highlight_pseudocode(["SPLIT_LOOP", "SPLIT_DO", "SPLIT_MID", 
                                          "SPLIT_LEFT", "SPLIT_RIGHT", "SPLIT_PROMOTE"])
                
                node_type = "叶节点" if is_leaf else "内部节点"
                self.update_status(f"⚡ {node_type}分裂: 提升键 {promoted} 到父节点")
                
                # 详细解释分裂过程
                if new_node:
                    explain = f"⚡ 节点分裂！\n\n"
                    explain += f"🔴 原节点: [{', '.join(str(k) for k in node.keys)}]\n"
                    explain += f"🔵 新节点: [{', '.join(str(k) for k in new_node.keys)}]\n\n"
                    explain += f"📤 提升键: {promoted}\n"
                    explain += f"   → 插入到父节点中\n\n"
                    if is_leaf:
                        explain += f"叶节点分裂特点：\n"
                        explain += f"提升键保留在右侧叶节点中"
                    else:
                        explain += f"内部节点分裂特点：\n"
                        explain += f"提升键不保留在子节点中"
                else:
                    self.highlight_pseudocode(["SPLIT_NEWROOT"])
                    explain = f"🌟 创建新的根节点！\n\n"
                    explain += f"树的高度增加了一层\n"
                    explain += f"新根节点的键: [{promoted}]"
                    
                self.update_explanation(explain)
                
                i += 1
                self.window.after(1000, step)
            else:
                i += 1
                self.window.after(200, step)

        step()


if __name__ == '__main__':
    root = Tk()
    app = BPlusVisualizer(root)
    root.mainloop()
