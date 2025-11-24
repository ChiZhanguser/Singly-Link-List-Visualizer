from tkinter import *
from tkinter import messagebox
from typing import Dict, Tuple, List, Optional
from avl.avl_model import AVLModel, AVLNode, clone_tree
import storage as storage
from tkinter import filedialog
from datetime import datetime
# 确保 TclError 被导入，以便在动画中捕获异常
from tkinter import TclError 

class AVLVisualizer:
    def __init__(self, root):
        self.window = root
        self.is_embedded = hasattr(root, 'title') and callable(root.title)
        
        if self.is_embedded:
            self.window.title("🌳 AVL 树可视化系统")
            self.window.config(bg="#1E1E2E")
            self.window.geometry("1350x780") 
        else:
            self.window.config(bg="#1E1E2E")
        
        self.title_font = ("Segoe UI", 16, "bold")
        self.label_font = ("Segoe UI", 11)
        self.button_font = ("Segoe UI", 10, "bold")
        self.status_font = ("Segoe UI", 10, "italic")
        
        self.colors = {
            "bg_primary": "#1E1E2E",
            "bg_secondary": "#2D2D44",
            "bg_canvas": "#FFFFFF",
            "accent_green": "#4CAF50",
            "accent_blue": "#2196F3",
            "accent_orange": "#FF9800",
            "accent_purple": "#9C27B0",
            "accent_red": "#F44336",
            "text_light": "#FFFFFF",
            "text_dark": "#2D2D44",
            "node_normal": "#E3F2FD",
            "node_highlight": "#FFF9C4",
            "node_new": "#C8E6C9",
            "edge_color": "#616161",
            # 新增颜色定义
            "node_comparing": "#FFE0B2",
            "node_balance_ok": "#E8F5E8",
            "node_balance_warning": "#FFF3E0",
            "node_balance_critical": "#FFEBEE",
            "balance_text": "#2E7D32",
            "height_text": "#1565C0",
            "path_highlight": "#FFD54F",
            "rotation_highlight": "#E91E63",
        }
        
        if self.is_embedded:
            self.canvas_w = 1200
            self.canvas_h = 560
        else:
            self.canvas_w = 1100
            self.canvas_h = 500
            
        self.canvas = Canvas(
            self.window, 
            bg=self.colors["bg_canvas"], 
            width=self.canvas_w, 
            height=self.canvas_h,
            bd=4, 
            relief=GROOVE,
            highlightthickness=2,
            highlightbackground=self.colors["accent_blue"]
        )
        
        if self.is_embedded:
            self.canvas.pack(padx=15, pady=10)
        else:
            self.canvas.grid(row=0, column=0, columnspan=4, padx=10, pady=5, sticky="nsew")

        self.model = AVLModel()
        self.node_vis: Dict[str, Dict] = {}
        self.animating = False
        self.batch: List[str] = [] # 确保 batch 被初始化

        self.node_w = 120
        self.node_h = 44
        self.level_gap = 100
        self.margin_x = 40

        # 新增动画参数
        self.animation_speed = 1.0
        self.show_balance_factors = True
        self.show_height = True
        self.highlight_comparisons = True

        self.input_var = StringVar()
        self.create_controls()
        self.draw_instructions()

    def create_controls(self):
        if self.is_embedded:
            self._create_standalone_controls()
        else:
            self._create_embedded_controls()

    def _create_standalone_controls(self):
        """独立运行时的控件布局 (添加删除按钮)"""
        main_frame = Frame(self.window, bg=self.colors["bg_primary"])
        main_frame.pack(pady=(0, 8), fill=X, padx=15)
        
        title_label = Label(
            main_frame, 
            text="🎯 AVL 树操作面板", 
            bg=self.colors["bg_primary"], 
            fg=self.colors["text_light"],
            font=self.title_font
        )
        title_label.pack(pady=(0, 15))

        top_controls_container = Frame(main_frame, bg=self.colors["bg_primary"])
        top_controls_container.pack(fill=X, pady=(0, 12)) 
        
        dsl_frame = LabelFrame(
            top_controls_container,
            text="⚡ DSL 命令",
            bg=self.colors["bg_secondary"],
            fg=self.colors["text_light"],
            font=self.label_font,
            padx=12,
            pady=12
        )
        dsl_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 6)) 

        dsl_row1 = Frame(dsl_frame, bg=self.colors["bg_secondary"])
        dsl_row1.pack(fill=X, pady=(0, 8))

        Label(
            dsl_row1, 
            text="DSL命令:", 
            bg=self.colors["bg_secondary"], 
            fg=self.colors["text_light"],
            font=self.label_font
        ).pack(side=LEFT, padx=6)
        
        self.dsl_var = StringVar()
        dsl_entry = Entry(
            dsl_row1, 
            textvariable=self.dsl_var, 
            width=35,
            font=self.label_font,
            bd=2,
            relief=GROOVE
        )
        dsl_entry.pack(side=LEFT, padx=6, fill=X, expand=True)
        dsl_entry.bind('<Return>', self.execute_dsl_command)
        
        dsl_row2 = Frame(dsl_frame, bg=self.colors["bg_secondary"])
        dsl_row2.pack(fill=X, pady=(8, 0))
        
        self.create_button(
            dsl_row2, 
            "🚀 执行DSL", 
            self.colors["accent_purple"],
            self.execute_dsl_command
        ).pack(side=LEFT, padx=6, pady=4)
        
        self.create_button(
            dsl_row2, 
            "❓ DSL帮助", 
            "#673AB7",
            self.show_dsl_help
        ).pack(side=LEFT, padx=6, pady=4)

        # 2. 插入/删除操作框架 (原插入框架)
        insert_frame = LabelFrame(
            top_controls_container,
            text="📥 插入 / 删除 节点",
            bg=self.colors["bg_secondary"],
            fg=self.colors["text_light"],
            font=self.label_font,
            padx=12,
            pady=12
        )
        insert_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=(6, 0)) 

        input_row1 = Frame(insert_frame, bg=self.colors["bg_secondary"])
        input_row1.pack(fill=X, pady=(0, 8))

        Label(
            input_row1, 
            text="输入数字（逗号分隔）:", 
            bg=self.colors["bg_secondary"], 
            fg=self.colors["text_light"],
            font=self.label_font
        ).pack(side=LEFT, padx=6)
        
        entry = Entry(
            input_row1, 
            textvariable=self.input_var, 
            width=25,
            font=self.label_font,
            bd=2,
            relief=GROOVE
        )
        entry.pack(side=LEFT, padx=6, fill=X, expand=True)
        entry.insert(0, "30, 20, 10, 25, 28, 27, 50, 40, 45")
        
        input_row2 = Frame(insert_frame, bg=self.colors["bg_secondary"])
        input_row2.pack(fill=X, pady=(8, 0))
        
        self.create_button(
            input_row2, 
            "✨ Insert (动画)", 
            self.colors["accent_green"],
            self.start_insert_animated
        ).pack(side=LEFT, padx=4, pady=4)
        
        # 新增删除按钮
        self.create_button(
            input_row2, 
            "❌ Delete (动画)", 
            self.colors["accent_red"],
            self.start_delete_animated
        ).pack(side=LEFT, padx=4, pady=4)
        
        self.create_button(
            input_row2, 
            "🗑️ 清空", 
            self.colors["accent_orange"],
            self.clear_canvas
        ).pack(side=LEFT, padx=4, pady=4)

        # 动画控制面板
        self._create_animation_controls_standalone(main_frame)

        file_frame = LabelFrame(
            main_frame,
            text="💾 文件操作",
            bg=self.colors["bg_secondary"],
            fg=self.colors["text_light"],
            font=self.label_font,
            padx=12,
            pady=12
        )
        file_frame.pack(fill=X, pady=(0, 12))

        file_buttons = Frame(file_frame, bg=self.colors["bg_secondary"])
        file_buttons.pack(fill=X)
        
        self.create_button(
            file_buttons, 
            "💾 保存", 
            self.colors["accent_blue"],
            self.save_structure
        ).pack(side=LEFT, padx=6, pady=6)
        
        self.create_button(
            file_buttons, 
            "📂 打开", 
            self.colors["accent_blue"],
            self.load_structure
        ).pack(side=LEFT, padx=6, pady=6)
        
        self.create_button(
            file_buttons, 
            "🏠 返回主界面", 
            "#6A5ACD",
            self.back_to_main
        ).pack(side=LEFT, padx=6, pady=6)

        self.status_frame = Frame(self.window, bg=self.colors["bg_secondary"], height=30)
        self.status_frame.pack(fill=X, side=BOTTOM, pady=(5, 0))
        self.status_frame.pack_propagate(False)
        
        self.status_label = Label(
            self.status_frame,
            text="就绪",
            bg=self.colors["bg_secondary"],
            fg=self.colors["text_light"],
            font=self.status_font
        )
        self.status_label.pack(side=LEFT, padx=12, pady=6)

    def _create_animation_controls_standalone(self, parent):
        """独立运行时的动画控制面板"""
        anim_frame = LabelFrame(
            parent,
            text="🎬 动画控制",
            bg=self.colors["bg_secondary"],
            fg=self.colors["text_light"],
            font=self.label_font,
            padx=12,
            pady=8
        )
        anim_frame.pack(fill=X, pady=(0, 10))
        
        anim_row1 = Frame(anim_frame, bg=self.colors["bg_secondary"])
        anim_row1.pack(fill=X, pady=4)
        
        # 速度控制
        Label(anim_row1, text="速度:", bg=self.colors["bg_secondary"], 
              fg=self.colors["text_light"], font=self.label_font).pack(side=LEFT, padx=6)
        
        self.speed_var = DoubleVar(value=1.0)
        speed_scale = Scale(anim_row1, from_=0.3, to=3.0, resolution=0.1, 
                           variable=self.speed_var, orient=HORIZONTAL,
                           length=120, showvalue=True, bg=self.colors["bg_secondary"],
                           fg=self.colors["text_light"], highlightbackground=self.colors["bg_secondary"],
                           command=self.update_animation_speed)
        speed_scale.pack(side=LEFT, padx=6)
        
        # 显示选项
        self.bf_var = BooleanVar(value=True)
        bf_check = Checkbutton(anim_row1, text="显示平衡因子", variable=self.bf_var,
                              command=self.toggle_balance_factors, bg=self.colors["bg_secondary"],
                              fg=self.colors["text_light"], selectcolor=self.colors["bg_primary"],
                              activebackground=self.colors["bg_secondary"])
        bf_check.pack(side=LEFT, padx=10)
        
        self.height_var = BooleanVar(value=True)
        height_check = Checkbutton(anim_row1, text="显示高度", variable=self.height_var,
                                  command=self.toggle_height_display, bg=self.colors["bg_secondary"],
                                  fg=self.colors["text_light"], selectcolor=self.colors["bg_primary"],
                                  activebackground=self.colors["bg_secondary"])
        height_check.pack(side=LEFT, padx=10)

    def _create_embedded_controls(self):
        """嵌入到主程序时的紧凑控件布局 (添加删除按钮)"""
        control_frame = Frame(self.window, bg=self.colors["bg_primary"])
        control_frame.grid(row=1, column=0, columnspan=4, sticky="ew", padx=10, pady=5)
        
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_columnconfigure(1, weight=1)
        self.window.grid_columnconfigure(2, weight=1)
        self.window.grid_columnconfigure(3, weight=1)
        
        # 第一行：插入操作
        insert_label = Label(
            control_frame, 
            text="插入/删除:",
            bg=self.colors["bg_primary"], 
            fg=self.colors["text_light"],
            font=self.label_font
        )
        insert_label.grid(row=0, column=0, padx=(0, 5), pady=2, sticky="w")
        
        entry = Entry(
            control_frame, 
            textvariable=self.input_var, 
            width=20, 
            font=self.label_font,
            bd=2,
            relief=GROOVE
        )
        entry.grid(row=0, column=1, columnspan=2, padx=5, pady=2, sticky="ew") 
        entry.insert(0, "30, 20, 40, 10, 25, 35, 50")
        
        self.create_button(
            control_frame, 
            "✨ Insert", 
            self.colors["accent_green"],
            self.start_insert_animated
        ).grid(row=0, column=3, padx=5, pady=2)
        
        # 第二行：操作按钮
        self.create_button(
            control_frame, 
            "❌ Delete",
            self.colors["accent_red"],
            self.start_delete_animated
        ).grid(row=1, column=0, padx=5, pady=2)
        
        self.create_button(
            control_frame, 
            "🗑️ 清空", 
            self.colors["accent_orange"],
            self.clear_canvas
        ).grid(row=1, column=1, padx=5, pady=2)
        
        self.create_button(
            control_frame, 
            "💾 保存", 
            self.colors["accent_blue"],
            self.save_structure
        ).grid(row=1, column=2, padx=5, pady=2)
        
        self.create_button(
            control_frame, 
            "📂 打开", 
            self.colors["accent_blue"],
            self.load_structure
        ).grid(row=1, column=3, padx=5, pady=2)
        
        # 第三行：DSL命令
        dsl_label = Label(
            control_frame, 
            text="DSL:", 
            bg=self.colors["bg_primary"], 
            fg=self.colors["text_light"],
            font=self.label_font
        )
        dsl_label.grid(row=2, column=0, padx=(0, 5), pady=2, sticky="w")
        
        self.dsl_var = StringVar()
        dsl_entry = Entry(
            control_frame, 
            textvariable=self.dsl_var, 
            width=25, 
            font=self.label_font,
            bd=2,
            relief=GROOVE
        )
        dsl_entry.grid(row=2, column=1, columnspan=1, padx=5, pady=2, sticky="ew")
        
        self.create_button(
            control_frame, 
            "🚀 执行", 
            self.colors["accent_purple"],
            self.execute_dsl_command
        ).grid(row=2, column=2, padx=5, pady=2)
        
        self.create_button(
            control_frame, 
            "❓ 帮助", 
            "#673AB7",
            self.show_dsl_help
        ).grid(row=2, column=3, padx=5, pady=2)
        
        # 动画控制
        self._create_animation_controls_embedded(control_frame)
        
        # 状态标签
        self.status_label = Label(
            control_frame,
            text="就绪",
            bg=self.colors["bg_primary"],
            fg=self.colors["text_light"],
            font=self.status_font
        )
        self.status_label.grid(row=4, column=0, columnspan=4, padx=5, pady=2, sticky="w")

    def _create_animation_controls_embedded(self, parent):
        """嵌入模式下的动画控制"""
        anim_frame = Frame(parent, bg=self.colors["bg_primary"])
        anim_frame.grid(row=3, column=0, columnspan=4, sticky="ew", padx=10, pady=5)
        
        # 速度控制
        Label(anim_frame, text="速度:", bg=self.colors["bg_primary"], 
              fg=self.colors["text_light"], font=("Segoe UI", 9)).grid(row=0, column=0, padx=(0,5))
        
        self.speed_var = DoubleVar(value=1.0)
        speed_scale = Scale(anim_frame, from_=0.3, to=3.0, resolution=0.1, 
                           variable=self.speed_var, orient=HORIZONTAL,
                           length=80, showvalue=True, bg=self.colors["bg_primary"],
                           fg=self.colors["text_light"], highlightbackground=self.colors["bg_primary"])
        speed_scale.grid(row=0, column=1, padx=5)
        speed_scale.bind("<Motion>", lambda e: self.update_animation_speed(self.speed_var.get()))
        
        # 显示选项
        self.bf_var = BooleanVar(value=True)
        bf_check = Checkbutton(anim_frame, text="平衡因子", variable=self.bf_var,
                              command=self.toggle_balance_factors, bg=self.colors["bg_primary"],
                              fg=self.colors["text_light"], selectcolor=self.colors["bg_secondary"],
                              activebackground=self.colors["bg_primary"], font=("Segoe UI", 9))
        bf_check.grid(row=0, column=2, padx=10)
        
        self.height_var = BooleanVar(value=True)
        height_check = Checkbutton(anim_frame, text="高度", variable=self.height_var,
                                  command=self.toggle_height_display, bg=self.colors["bg_primary"],
                                  fg=self.colors["text_light"], selectcolor=self.colors["bg_secondary"],
                                  activebackground=self.colors["bg_primary"], font=("Segoe UI", 9))
        height_check.grid(row=0, column=3, padx=10)

    def create_button(self, parent, text, color, command):
        if self.is_embedded:
            return Button(
                parent,
                text=text,
                bg=color,
                fg=self.colors["text_light"],
                font=("Segoe UI", 9, "bold"),
                command=command,
                bd=0,
                relief=RAISED,
                padx=12,
                pady=4,
                cursor="hand2"
            )
        else:
            return Button(
                parent,
                text=text,
                bg=color,
                fg=self.colors["text_light"],
                font=self.button_font,
                command=command,
                bd=0,
                relief=RAISED,
                padx=15,
                pady=8,
                cursor="hand2"
            )

    def execute_dsl_command(self, event=None):
        dsl_text = self.dsl_var.get().strip()
        if not dsl_text:
            return
        try:
            from DSL_utils import process_command 
            success = process_command(self, dsl_text) 
            if success:
                self.dsl_var.set("")
                self.update_status("✅ DSL命令执行成功")
        except Exception as e:
            messagebox.showerror("❌ DSL错误", f"执行DSL命令时出错: {str(e)}")

    def show_dsl_help(self):
        try:
            from DSL_utils import avl_dsl
            avl_dsl._show_help()
        except ImportError:
             messagebox.showerror("❌ 导入错误", "无法加载 AVL DSL 帮助。\n请确保 'DSL_utils' 包已正确安装。")

    def draw_instructions(self):
        self.canvas.delete("all")
        self.node_vis.clear()
        
        title_text = "🌳 AVL 树可视化系统 - 插入/删除演示：展示搜索路径并精确动画显示旋转"
        self.canvas.create_text(
            self.canvas_w/2, 20, 
            text=title_text, 
            font=("Segoe UI", 12, "bold"), 
            fill=self.colors["text_dark"]
        )
        
        self.status_id = self.canvas.create_text(
            self.canvas_w - 15, 20, 
            anchor="ne", 
            text="", 
            font=self.status_font, 
            fill=self.colors["accent_green"]
        )

    def update_status(self, txt: str):
        if hasattr(self, 'status_label'):
            self.status_label.config(text=txt)
        
        if self.status_id:
            try:
                self.canvas.itemconfig(self.status_id, text=txt)
            except TclError:
                self.status_id = None
        
        if not self.status_id:
             try:
                self.status_id = self.canvas.create_text(
                    self.canvas_w - 15, 20, 
                    anchor="ne", 
                    text=txt, 
                    font=self.status_font, 
                    fill=self.colors["accent_green"]
                )
             except TclError:
                 pass

    def _draw_connection(self, cx, cy, tx, ty):
        top = cy + self.node_h/2
        bot = ty - self.node_h/2
        midy = (top + bot) / 2
        l1 = self.canvas.create_line(cx, top, cx, midy, width=2.5, fill=self.colors["edge_color"])
        l2 = self.canvas.create_line(cx, midy, tx, bot, arrow=LAST, width=2.5, fill=self.colors["edge_color"])
        return (l1, l2)

    def compute_positions_for_root(self, root: Optional[AVLNode]) -> Dict[str, Tuple[float, float]]:
        res: Dict[str, Tuple[float,float]] = {}
        if not root:
            return res
        inorder_nodes: List[AVLNode] = []
        depths: Dict[AVLNode, int] = {}
        def inorder(n: Optional[AVLNode], d: int):
            if not n:
                return
            inorder(n.left, d+1)
            inorder_nodes.append(n)
            depths[n] = d
            inorder(n.right, d+1)
        inorder(root, 0)
        n = len(inorder_nodes)
        if n == 0:
            return res
        width = max(200, self.canvas_w - 2*self.margin_x)
        counts: Dict[str,int] = {}
        for i, node in enumerate(inorder_nodes):
            base = str(node.val)
            cnt = counts.get(base, 0)
            counts[base] = cnt + 1
            key = f"{base}#{cnt}" if cnt > 0 else base
            if n == 1:
                x = self.canvas_w/2
            else:
                x = self.margin_x + i * (width / (n-1))
            y = 60 + depths[node] * self.level_gap
            res[key] = (x, y)
        return res

    def draw_tree_from_root(self, root: Optional[AVLNode]):
        self.canvas.delete("all")
        self.draw_instructions()
        if root is None:
            self.canvas.create_text(
                self.canvas_w/2, self.canvas_h/2, 
                text="🌲 空树", 
                font=("Segoe UI", 20), 
                fill="#888888"
            )
            return
        pos = self.compute_positions_for_root(root)
        inorder_nodes: List[AVLNode] = []
        def inorder_collect(n: Optional[AVLNode]):
            if not n:
                return
            inorder_collect(n.left)
            inorder_nodes.append(n)
            inorder_collect(n.right)
        inorder_collect(root)
        node_to_key: Dict[AVLNode, str] = {}
        counts: Dict[str,int] = {}
        for node in inorder_nodes:
            base = str(node.val)
            cnt = counts.get(base, 0)
            counts[base] = cnt + 1
            key = f"{base}#{cnt}" if cnt > 0 else base
            node_to_key[node] = key
        self.node_vis.clear()
        for node, key in node_to_key.items():
            cx, cy = pos[key]
            self._draw_single_node(node, cx, cy, key)
        def setup_edges(n: Optional[AVLNode]):
            if not n:
                return
            parent_key = node_to_key[n]
            parent_cx, parent_cy = pos[parent_key]
            if n.left:
                child_key = node_to_key[n.left]
                child_cx, child_cy = pos[child_key]
                line_ids = self._draw_connection(parent_cx, parent_cy, child_cx, child_cy)
                self.node_vis[parent_key]['edges'][child_key] = line_ids
                setup_edges(n.left)
            if n.right:
                child_key = node_to_key[n.right]
                child_cx, child_cy = pos[child_key]
                line_ids = self._draw_connection(parent_cx, parent_cy, child_cx, child_cy)
                self.node_vis[parent_key]['edges'][child_key] = line_ids
                setup_edges(n.right)
        setup_edges(root)

    def _draw_single_node(self, node: AVLNode, cx: float, cy: float, key: str):
        """绘制单个节点，包含平衡因子和高度信息"""
        # 计算平衡因子
        left_height = node.left.height if node.left else 0
        right_height = node.right.height if node.right else 0
        balance_factor = left_height - right_height
        
        # 根据平衡因子选择颜色
        if abs(balance_factor) <= 1:
            node_color = self.colors["node_balance_ok"]
        elif abs(balance_factor) == 2:
            node_color = self.colors["node_balance_warning"]
        else:
            node_color = self.colors["node_balance_critical"]
            
        # 绘制节点主体
        left, top, right, bottom = cx - self.node_w/2, cy - self.node_h/2, cx + self.node_w/2, cy + self.node_h/2
        rect = self.canvas.create_rectangle(
            left, top, right, bottom, 
            fill=node_color, 
            outline=self.colors["accent_blue"], 
            width=2,
            stipple="gray50"
        )
        
        # 绘制分隔线
        x1, x2 = left + 28, left + 92
        self.canvas.create_line(x1, top, x1, bottom, width=1, fill="#BBDEFB")
        self.canvas.create_line(x2, top, x2, bottom, width=1, fill="#BBDEFB")
        
        # 主值文本
        txt = self.canvas.create_text(
            (x1+x2)/2, cy - 8, 
            text=str(node.val), 
            font=("Segoe UI", 12, "bold"),
            fill=self.colors["text_dark"]
        )
        
        # 高度文本
        height_text = self.canvas.create_text(
            x1 + 14, cy + 8,
            text=f"h:{node.height}",
            font=("Segoe UI", 8),
            fill=self.colors["height_text"]
        )
        
        # 平衡因子文本
        bf_text = self.canvas.create_text(
            x2 - 14, cy + 8,
            text=f"bf:{balance_factor}",
            font=("Segoe UI", 8, "bold"),
            fill=self.colors["balance_text"]
        )
        
        # 存储节点信息
        self.node_vis[key] = {
            'rect': rect, 
            'text': txt,
            'height_text': height_text,
            'bf_text': bf_text,
            'cx': cx, 
            'cy': cy, 
            'val': str(node.val),
            'edges': {},
            'balance_factor': balance_factor
        }
        
        # 根据显示设置控制文本可见性
        if not self.show_height:
            self.canvas.itemconfig(height_text, state='hidden')
        if not self.show_balance_factors:
            self.canvas.itemconfig(bf_text, state='hidden')

    # 动画控制方法
    def update_animation_speed(self, value):
        """更新动画速度"""
        try:
            self.animation_speed = float(value)
        except:
            self.animation_speed = 1.0

    def toggle_balance_factors(self):
        """切换平衡因子显示"""
        self.show_balance_factors = self.bf_var.get()
        self.redraw_current_tree()

    def toggle_height_display(self):
        """切换高度显示"""
        self.show_height = self.height_var.get()
        self.redraw_current_tree()

    def redraw_current_tree(self):
        """重绘当前树"""
        self.draw_tree_from_root(clone_tree(self.model.root))

    # 插入动画流程
    def start_insert_animated(self):
        if self.animating:
            self.update_status("⚠️ 正在执行动画，请稍候...")
            return
        s = self.input_var.get().strip()
        if not s:
            messagebox.showinfo("💡 提示", "请输入数字，例如：1,2,3")
            return
        batch = [p.strip() for p in s.split(",") if p.strip()!=""]
        if not batch:
            return
        self.batch = batch
        self.animating = True
        self.update_status("🎬 开始插入动画...")
        self._insert_seq(0)

    def _insert_seq(self, idx: int):
        if idx >= len(self.batch):
            self.animating = False
            self.update_status("✅ 所有插入完成")
            self._show_final_balance_report()
            return
        val = self.batch[idx]
        inserted_node, path_nodes, rotations, snapshots = self.model.insert_with_steps(val)
        snap_pre = snapshots[0]
        snap_after_insert = snapshots[1] if len(snapshots) > 1 else None
        pos_pre = self.compute_positions_for_root(snap_pre)
        val_to_keys_pre: Dict[str, List[str]] = {}
        for k in pos_pre.keys():
            base = k.split('#')[0]
            val_to_keys_pre.setdefault(base, []).append(k)

        def highlight_path(i=0):
            if i >= len(path_nodes):
                self.update_status(f"📥 插入 {val}: 开始落位")
                self.animate_flyin_new(val, snap_after_insert, lambda: self._after_insert_rotations(rotations, snapshots, idx))
                return
            node = path_nodes[i]
            v = str(node.val)
            keylist = val_to_keys_pre.get(v, [])
            if keylist:
                key = keylist.pop(0)
                self.draw_tree_from_root(snap_pre)
                try:
                    self.canvas.itemconfig(self.node_vis[key]['rect'], fill=self.colors["node_highlight"])
                except Exception:
                    pass
            else:
                self.draw_tree_from_root(snap_pre)
            
            # 显示比较信息
            if i < len(path_nodes) - 1:
                next_node = path_nodes[i + 1]
                comparison = self._get_comparison_text(val, node.val, next_node == node.left)
                status_text = f"🔍 比较 {val} 和 {v}: {comparison}"
            else:
                status_text = f"🎯 找到插入位置: {val}"
                
            self.update_status(status_text)
            
            # 自适应延迟
            delay = int(600 / self.animation_speed)
            self.window.after(delay, lambda: highlight_path(i+1))

        highlight_path(0)
    
    def _get_comparison_text(self, val1, val2, go_left: bool) -> str:
        """生成比较文本"""
        cmp_result = self.model._compare(val1, val2)
        if cmp_result < 0:
            return f"{val1} < {val2}，转向左子树" if go_left else f"{val1} < {val2}"
        elif cmp_result > 0:
            return f"{val1} > {val2}，转向右子树" if not go_left else f"{val1} > {val2}"
        else:
            return f"{val1} = {val2}，转向右子树"

    def animate_flyin_new(self, val_str: str, snap_after_insert: Optional[AVLNode], on_complete):
        if not snap_after_insert:
            on_complete(); return
        pos_after = self.compute_positions_for_root(snap_after_insert)
        candidate_keys = [k for k in pos_after.keys() if k.split('#')[0] == str(val_str)]
        if not candidate_keys:
            on_complete(); return
        target_key = candidate_keys[-1]
        tx, ty = pos_after[target_key]
        sx, sy = self.canvas_w/2, 20
        left, top, right, bottom = sx - self.node_w/2, sy - self.node_h/2, sx + self.node_w/2, sy + self.node_h/2
        temp_rect = self.canvas.create_rectangle(
            left, top, right, bottom, 
            fill=self.colors["node_new"], 
            outline=self.colors["accent_green"], 
            width=2
        )
        temp_text = self.canvas.create_text(sx, sy, text=str(val_str), font=("Segoe UI", 12, "bold"))
        steps = int(30 * self.animation_speed)
        dx = (tx - sx)/steps
        dy = (ty - sy)/steps
        delay = max(8, int(12 / self.animation_speed))
        def step(i=0):
            if i < steps:
                try:
                    self.canvas.move(temp_rect, dx, dy)
                    self.canvas.move(temp_text, dx, dy)
                except Exception:
                    pass
                self.window.after(delay, lambda: step(i+1))
            else:
                try:
                    self.canvas.delete(temp_rect)
                    self.canvas.delete(temp_text)
                except Exception:
                    pass
                self.draw_tree_from_root(snap_after_insert)
                try:
                    self.canvas.itemconfig(self.node_vis[target_key]['rect'], fill=self.colors["node_new"])
                except Exception:
                    pass
                self.window.after(int(300 / self.animation_speed), on_complete)
        step()

    def _after_insert_rotations(self, rotations, snapshots, insertion_idx):
        if not rotations:
            self.draw_tree_from_root(clone_tree(self.model.root))
            self.window.after(int(300 / self.animation_speed), lambda: self._insert_seq(insertion_idx+1))
            return
        def done_all():
            self.draw_tree_from_root(clone_tree(self.model.root))
            self.window.after(int(300 / self.animation_speed), lambda: self._insert_seq(insertion_idx+1))
        self._animate_rotations_sequence(rotations, snapshots, insertion_idx, done_all)

    # 删除动画流程
    def start_delete_animated(self):
        if self.animating:
            self.update_status("⚠️ 正在执行动画，请稍候...")
            return
            
        s = self.input_var.get().strip()
        if not s:
            messagebox.showinfo("💡 提示", "请输入要删除的数字，例如：1,2,3")
            return
            
        batch = [p.strip() for p in s.split(",") if p.strip()!=""]
        if not batch:
            return
            
        self.batch = batch
        self.animating = True
        self.update_status("🎬 开始删除动画...")
        self._delete_seq(0)

    def _delete_seq(self, idx: int):
        if idx >= len(self.batch):
            self.animating = False
            self.update_status("✅ 所有删除完成")
            self._show_final_balance_report()
            return

        val = self.batch[idx]
        deleted_node, path_nodes, rotations, snapshots = self.model.delete_with_steps(val)

        snap_pre = snapshots[0]
        snap_after_delete = snapshots[1] if len(snapshots) > 1 else None

        pos_pre = self.compute_positions_for_root(snap_pre)
        val_to_keys_pre: Dict[str, List[str]] = {}
        for k in pos_pre.keys():
            base = k.split('#')[0]
            val_to_keys_pre.setdefault(base, []).append(k)

        def highlight_path_for_delete(i=0):
            if i >= len(path_nodes):
                if deleted_node is None:
                    self.update_status(f"❌ 未找到 {val}")
                    self.draw_tree_from_root(snap_pre)
                    self.window.after(int(600 / self.animation_speed), lambda: self._delete_seq(idx + 1))
                else:
                    self.update_status(f"❌ 找到 {val}: 正在移除...")
                    self.animate_show_deletion(
                        val, 
                        snap_after_delete, 
                        lambda: self._after_delete_rotations(rotations, snapshots, idx)
                    )
                return
                
            node = path_nodes[i]
            v = str(node.val)
            keylist = val_to_keys_pre.get(v, [])
            if keylist:
                key = keylist.pop(0)
                self.draw_tree_from_root(snap_pre)
                try:
                    self.canvas.itemconfig(self.node_vis[key]['rect'], fill=self.colors["node_highlight"])
                except Exception:
                    pass
            else:
                self.draw_tree_from_root(snap_pre)
                
            # 显示比较信息
            if i < len(path_nodes) - 1:
                next_node = path_nodes[i + 1]
                comparison = self._get_comparison_text(val, node.val, next_node == node.left)
                status_text = f"🔍 搜索 {val}: 比较 {val} 和 {v}: {comparison}"
            else:
                status_text = f"🎯 找到目标节点: {val}"
                
            self.update_status(status_text)
            
            delay = int(600 / self.animation_speed)
            self.window.after(delay, lambda: highlight_path_for_delete(i+1))

        highlight_path_for_delete(0)

    def animate_show_deletion(self, val_str: str, snap_after_delete: Optional[AVLNode], on_complete):
        self.draw_tree_from_root(snap_after_delete)
        self.update_status(f"✅ {val_str} 已移除 (或值已交换). 准备旋转...")
        self.window.after(int(800 / self.animation_speed), on_complete)

    def _after_delete_rotations(self, rotations, snapshots, deletion_idx):
        if not rotations:
            self.draw_tree_from_root(clone_tree(self.model.root))
            self.window.after(int(300 / self.animation_speed), lambda: self._delete_seq(deletion_idx+1))
            return

        def done_all():
            self.draw_tree_from_root(clone_tree(self.model.root))
            self.window.after(int(300 / self.animation_speed), lambda: self._delete_seq(deletion_idx+1))
            
        self._animate_rotations_sequence(rotations, snapshots, deletion_idx, done_all)

    # 通用动画方法
    def _redraw_all_edges_during_animation(self):
        for parent_key, parent_vis in self.node_vis.items():
            try:
                parent_coords = self.canvas.coords(parent_vis['rect'])
                if not parent_coords or len(parent_coords) < 4: continue
                parent_cx = (parent_coords[0] + parent_coords[2]) / 2
                parent_cy = (parent_coords[1] + parent_coords[3]) / 2
                for child_key, line_ids in parent_vis.get('edges', {}).items():
                    child_vis = self.node_vis.get(child_key)
                    if not child_vis: continue
                    child_coords = self.canvas.coords(child_vis['rect'])
                    if not child_coords or len(child_coords) < 4: continue
                    child_cx = (child_coords[0] + child_coords[2]) / 2
                    child_cy = (child_coords[1] + child_coords[3]) / 2
                    l1_id, l2_id = line_ids
                    top = parent_cy + self.node_h / 2
                    bot = child_cy - self.node_h / 2
                    midy = (top + bot) / 2
                    self.canvas.coords(l1_id, parent_cx, top, parent_cx, midy)
                    self.canvas.coords(l2_id, parent_cx, midy, child_cx, bot)
            except TclError:
                continue

    def _animate_single_rotation(self, before_root: Optional[AVLNode], after_root: Optional[AVLNode], rotation_info: Dict, on_done):
        pos_before = self.compute_positions_for_root(before_root)
        pos_after = self.compute_positions_for_root(after_root)
        
        # 绘制旋转前的树，并高亮参与旋转的节点
        self.draw_tree_from_root(before_root)
        self._highlight_rotation_nodes(rotation_info, pos_before)
        
        # 旋转类型说明
        rtype = rotation_info.get('type', '')
        rotation_explanation = self._get_rotation_explanation(rtype)
        self.update_status(f"🔄 执行 {rtype} 旋转: {rotation_explanation}")
        
        keys_common = set(pos_before.keys()) & set(pos_after.keys())
        moves = []
        for k in keys_common:
            item = self.node_vis.get(k)
            if not item:
                continue
            sx, sy = pos_before[k]
            tx, ty = pos_after[k]
            moves.append((k, item['rect'], item['text'], sx, sy, tx, ty))
            
        # 绘制旋转弧线和标签
        arc_id, label_id = self._draw_rotation_arc(rotation_info, pos_before)
        
        frames = int(30 * self.animation_speed)
        delay = max(10, int(20 / self.animation_speed))
        
        def frame_step(f=0):
            if f >= frames:
                self.draw_tree_from_root(after_root)
                if arc_id:
                    try: self.canvas.delete(arc_id)
                    except: pass
                if label_id:
                    try: self.canvas.delete(label_id)
                    except: pass
                self.window.after(int(300 / self.animation_speed), on_done)
                return
                
            t = (f+1)/frames
            for (k, rect_id, text_id, sx, sy, tx, ty) in moves:
                cur_cx = sx + (tx - sx) * t
                cur_cy = sy + (ty - sy) * t
                try:
                    ccx, ccy = self._get_rect_center(rect_id)
                    if (ccx, ccy) == (0,0): continue
                    dx = cur_cx - ccx
                    dy = cur_cy - ccy
                    self.canvas.move(rect_id, dx, dy)
                    self.canvas.move(text_id, dx, dy)
                    # 移动平衡因子和高度文本
                    if k in self.node_vis:
                        bf_text = self.node_vis[k].get('bf_text')
                        height_text = self.node_vis[k].get('height_text')
                        if bf_text:
                            self.canvas.move(bf_text, dx, dy)
                        if height_text:
                            self.canvas.move(height_text, dx, dy)
                except Exception:
                    pass
                    
            self._redraw_all_edges_during_animation()
            self.window.after(delay, lambda: frame_step(f+1))
            
        frame_step(0)

    def _highlight_rotation_nodes(self, rotation_info: Dict, positions: Dict):
        """高亮参与旋转的节点"""
        z_node = rotation_info.get('z')
        y_node = rotation_info.get('y') 
        x_node = rotation_info.get('x')
        
        # 高亮z节点（红色）
        if z_node:
            z_key = next((k for k in positions.keys() if k.split('#')[0] == str(z_node.val)), None)
            if z_key and z_key in self.node_vis:
                self.canvas.itemconfig(self.node_vis[z_key]['rect'], 
                                     fill=self.colors["accent_red"])
        
        # 高亮y节点（橙色）
        if y_node:
            y_key = next((k for k in positions.keys() if k.split('#')[0] == str(y_node.val)), None)
            if y_key and y_key in self.node_vis:
                self.canvas.itemconfig(self.node_vis[y_key]['rect'],
                                     fill=self.colors["accent_orange"])
        
        # 高亮x节点（绿色）
        if x_node:
            x_key = next((k for k in positions.keys() if k.split('#')[0] == str(x_node.val)), None)
            if x_key and x_key in self.node_vis:
                self.canvas.itemconfig(self.node_vis[x_key]['rect'],
                                     fill=self.colors["accent_green"])

    def _get_rotation_explanation(self, rtype: str) -> str:
        """获取旋转类型的解释"""
        explanations = {
            'LL': '左子树的左子树导致不平衡 - 右旋',
            'RR': '右子树的右子树导致不平衡 - 左旋', 
            'LR': '左子树的右子树导致不平衡 - 先左旋后右旋',
            'RL': '右子树的左子树导致不平衡 - 先右旋后左旋'
        }
        return explanations.get(rtype, '调整树结构以保持平衡')

    def _draw_rotation_arc(self, rotation_info: Dict, positions: Dict):
        """绘制旋转弧线"""
        z = rotation_info.get('z')
        y = rotation_info.get('y')
        if not z or not y:
            return None, None
            
        zkey = next((k for k in positions.keys() if k.split('#')[0] == str(z.val)), None)
        ykey = next((k for k in positions.keys() if k.split('#')[0] == str(y.val)), None)
        
        if not zkey or not ykey:
            return None, None
            
        zx, zy = positions[zkey]
        yx, yy = positions[ykey]
        midx = (zx + yx)/2
        topy = min(zy, yy) - 40
        
        try:
            arc_id = self.canvas.create_arc(
                midx-40, topy-25, midx+40, topy+25, 
                start=0, extent=180, style=ARC, width=3, 
                outline=self.colors["rotation_highlight"],
                dash=(5, 3)
            )
            label_id = self.canvas.create_text(
                midx, topy-35, 
                text=f"🔄 {rotation_info.get('type', '')}", 
                font=("Segoe UI", 11, "bold"), 
                fill=self.colors["rotation_highlight"]
            )
            return arc_id, label_id
        except Exception:
            return None, None

    def _get_rect_center(self, rect_id):
        """获取矩形中心坐标"""
        try:
            coords = self.canvas.coords(rect_id)
            if not coords or len(coords) < 4:
                return (0,0)
            x1,y1,x2,y2 = coords
            return ((x1+x2)/2, (y1+y2)/2)
        except TclError:
            return (0,0)

    def _animate_rotations_sequence(self, rotations: List[Dict], snapshots: List[Optional[AVLNode]], insertion_index: int, on_all_done):
        if not rotations:
            on_all_done(); return
        def step(i=0):
            if i >= len(rotations):
                on_all_done()
                return
            before_root = snapshots[1 + i] 
            after_root = snapshots[2 + i]
            rot_info = rotations[i]
            self.update_status(f"🔄 执行旋转 {i+1}/{len(rotations)}: {rot_info.get('type')}")
            self._animate_single_rotation(before_root, after_root, rot_info, lambda: step(i+1))
        step(0)

    def _show_final_balance_report(self):
        """显示最终的平衡报告"""
        if not self.model.root:
            return
            
        def check_balance(node):
            if not node:
                return True, 0
            left_balanced, left_height = check_balance(node.left)
            right_balanced, right_height = check_balance(node.right)
            balanced = (left_balanced and right_balanced and 
                       abs(left_height - right_height) <= 1)
            return balanced, 1 + max(left_height, right_height)
        
        is_balanced, _ = check_balance(self.model.root)
        status = "✅ 树是平衡的" if is_balanced else "⚠️ 树不平衡"
        self.update_status(f"{status} | 高度: {self.model.root.height}")
        
        # 短暂高亮显示结果
        self.canvas.create_text(
            self.canvas_w/2, self.canvas_h - 20,
            text=status,
            font=("Segoe UI", 12, "bold"),
            fill=self.colors["accent_green"] if is_balanced else self.colors["accent_orange"]
        )

    # 清空和文件操作
    def clear_canvas(self):
        if self.animating:
            self.update_status("⚠️ 正在执行动画，无法清空")
            return
        self.model = AVLModel()
        self.node_vis.clear()
        self.canvas.delete("all")
        self.draw_instructions()
        self.update_status("🗑️ 已清空")

    def back_to_main(self):
        if self.is_embedded:
            self.window.pack_forget()
        else:
            self.window.destroy()

    def _ensure_avl_folder(self) -> str:
        return storage.ensure_save_subdir("avl")

    def save_structure(self):
        root = self.model.root
        default_dir = self._ensure_avl_folder()
        default_name = f"avl_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = filedialog.asksaveasfilename(
            initialdir=default_dir,
            initialfile=default_name,
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="保存 AVL 到文件"
        )
        if not filepath: return
        ok = storage.save_tree_to_file(root, filepath)
        if ok:
            messagebox.showinfo("✅ 成功", f"AVL 已保存到：\n{filepath}")
            self.update_status("💾 保存成功")

    def load_structure(self):
        default_dir = self._ensure_avl_folder()
        filepath = filedialog.askopenfilename(
            initialdir=default_dir,
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="从文件加载 AVL"
        )
        if not filepath: return
        tree_dict = storage.load_tree_from_file(filepath)
        from avl.avl_model import AVLNode as AVLNodeClass
        newroot = storage.tree_dict_to_nodes(tree_dict, AVLNodeClass)
        self.model.root = newroot
        self.draw_tree_from_root(clone_tree(self.model.root))
        messagebox.showinfo("✅ 成功", f"AVL 已从文件加载并恢复结构：\n{filepath}")
        self.update_status("📂 已从文件加载结构")

if __name__ == '__main__':
    w = Tk()
    app = AVLVisualizer(w)
    w.mainloop()