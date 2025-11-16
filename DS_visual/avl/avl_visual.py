from tkinter import *
from tkinter import messagebox
from typing import Dict, Tuple, List, Optional
from avl.avl_model import AVLModel, AVLNode, clone_tree
import storage as storage
from tkinter import filedialog
from datetime import datetime

class AVLVisualizer:
    def __init__(self, root):
        self.window = root
        self.is_embedded = hasattr(root, 'title') and callable(root.title)  # 检测是否为独立窗口
        
        if self.is_embedded:
            # 独立运行模式
            self.window.title("🌳 AVL 树可视化系统")
            self.window.config(bg="#1E1E2E")
            # 恢复到合理的紧凑高度，现在并排布局可以容纳所有控件
            self.window.geometry("1350x780") 
        else:
            # 嵌入模式，使用更紧凑的布局
            self.window.config(bg="#1E1E2E")
        
        # 设置现代字体
        self.title_font = ("Segoe UI", 16, "bold")
        self.label_font = ("Segoe UI", 11)
        self.button_font = ("Segoe UI", 10, "bold")
        self.status_font = ("Segoe UI", 10, "italic")
        
        # 色彩方案
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
            "edge_color": "#616161"
        }
        
        # 根据运行模式调整画布大小
        if self.is_embedded:
            self.canvas_w = 1200
            self.canvas_h = 560
        else:
            # 嵌入模式使用更小的画布
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
            # 嵌入模式使用grid布局，更紧凑
            self.canvas.grid(row=0, column=0, columnspan=4, padx=10, pady=5, sticky="nsew")

        self.model = AVLModel()
        self.node_vis: Dict[str, Dict] = {}
        self.animating = False

        # layout params
        self.node_w = 120
        self.node_h = 44
        self.level_gap = 100
        self.margin_x = 40

        # controls
        self.input_var = StringVar()
        self.create_controls()
        self.draw_instructions()

    def create_controls(self):
        if self.is_embedded:
            self._create_standalone_controls()
        else:
            self._create_embedded_controls()

    def _create_standalone_controls(self):
        """独立运行时的控件布局"""
        # 主控制框架
        main_frame = Frame(self.window, bg=self.colors["bg_primary"])
        main_frame.pack(pady=(0, 8), fill=X, padx=15)
        
        # 标题
        title_label = Label(
            main_frame, 
            text="🎯 AVL 树操作面板", 
            bg=self.colors["bg_primary"], 
            fg=self.colors["text_light"],
            font=self.title_font
        )
        title_label.pack(pady=(0, 15))

        # --- 新增容器，用于实现并排布局 ---
        top_controls_container = Frame(main_frame, bg=self.colors["bg_primary"])
        top_controls_container.pack(fill=X, pady=(0, 12)) 
        
        # 1. DSL命令框架 (放在左边)
        dsl_frame = LabelFrame(
            top_controls_container, # <--- 放置在容器内
            text="⚡ DSL 命令",
            bg=self.colors["bg_secondary"],
            fg=self.colors["text_light"],
            font=self.label_font,
            padx=12,
            pady=12
        )
        # 使用 side=LEFT 实现并排
        dsl_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 6)) 

        # DSL第一行：标签和输入框
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
            width=35, # 调整宽度以适应并排布局
            font=self.label_font,
            bd=2,
            relief=GROOVE
        )
        dsl_entry.pack(side=LEFT, padx=6, fill=X, expand=True)
        dsl_entry.bind('<Return>', self.execute_dsl_command)
        
        # DSL第二行：按钮
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

        # 2. 插入操作框架 (放在右边)
        insert_frame = LabelFrame(
            top_controls_container, # <--- 放置在容器内
            text="📥 插入节点",
            bg=self.colors["bg_secondary"],
            fg=self.colors["text_light"],
            font=self.label_font,
            padx=12,
            pady=12
        )
        # 使用 side=LEFT 实现并排
        insert_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=(6, 0)) 

        # 插入操作的第一行：标签和输入框
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
            width=25, # 调整宽度以适应并排布局
            font=self.label_font,
            bd=2,
            relief=GROOVE
        )
        entry.pack(side=LEFT, padx=6, fill=X, expand=True)
        entry.insert(0, "30, 20, 10, 25, 28, 27, 50, 40, 45")
        
        # 插入操作的第二行：按钮
        input_row2 = Frame(insert_frame, bg=self.colors["bg_secondary"])
        input_row2.pack(fill=X, pady=(8, 0))
        
        self.create_button(
            input_row2, 
            "✨ Insert (动画)", 
            self.colors["accent_green"],
            self.start_insert_animated
        ).pack(side=LEFT, padx=4, pady=4)
        
        self.create_button(
            input_row2, 
            "🗑️ 清空", 
            self.colors["accent_orange"],
            self.clear_canvas
        ).pack(side=LEFT, padx=4, pady=4)

        # 文件操作框架 (保持在底部)
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

        # 文件操作按钮容器
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

        # 状态栏
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

    # --- 保持其他方法不变 ---

    def _create_embedded_controls(self):
        """嵌入到主程序时的紧凑控件布局"""
        # 使用grid布局，更紧凑
        control_frame = Frame(self.window, bg=self.colors["bg_primary"])
        control_frame.grid(row=1, column=0, columnspan=4, sticky="ew", padx=10, pady=5)
        
        # 配置列权重
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_columnconfigure(1, weight=1)
        self.window.grid_columnconfigure(2, weight=1)
        self.window.grid_columnconfigure(3, weight=1)
        
        # 第一行：插入操作
        insert_label = Label(
            control_frame, 
            text="插入:", 
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
        entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        entry.insert(0, "30, 20, 40, 10, 25, 35, 50, 5, 15")
        
        self.create_button(
            control_frame, 
            "✨ Insert", 
            self.colors["accent_green"],
            self.start_insert_animated
        ).grid(row=0, column=2, padx=5, pady=2)
        
        self.create_button(
            control_frame, 
            "🗑️ 清空", 
            self.colors["accent_orange"],
            self.clear_canvas
        ).grid(row=0, column=3, padx=5, pady=2)
        
        # 第二行：文件操作
        self.create_button(
            control_frame, 
            "💾 保存", 
            self.colors["accent_blue"],
            self.save_structure
        ).grid(row=1, column=0, padx=5, pady=2)
        
        self.create_button(
            control_frame, 
            "📂 打开", 
            self.colors["accent_blue"],
            self.load_structure
        ).grid(row=1, column=1, padx=5, pady=2)
        
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
        dsl_entry.grid(row=2, column=1, padx=5, pady=2, sticky="ew")
        dsl_entry.bind('<Return>', self.execute_dsl_command)
        
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
        
        # 状态标签
        self.status_label = Label(
            control_frame,
            text="就绪",
            bg=self.colors["bg_primary"],
            fg=self.colors["text_light"],
            font=self.status_font
        )
        self.status_label.grid(row=3, column=0, columnspan=4, padx=5, pady=2, sticky="w")

    def create_button(self, parent, text, color, command):
        """创建样式统一的按钮"""
        if self.is_embedded:
            # 嵌入模式使用更小的按钮
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
            # 独立模式使用正常大小的按钮
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
        """执行DSL命令 (已更新为使用主DSL路由器)"""
        dsl_text = self.dsl_var.get().strip()
        if not dsl_text:
            return
            
        try:
            # 导入顶层的 DSL 处理器 (即 __init__.py 中的 process_command)
            from DSL_utils import process_command 
            
            # 让主处理器自动识别 visualizer 类型并执行命令
            success = process_command(self, dsl_text) 
            
            if success:
                self.dsl_var.set("")
                self.update_status("✅ DSL命令执行成功")
        except Exception as e:
            messagebox.showerror("❌ DSL错误", f"执行DSL命令时出错: {str(e)}")

    def show_dsl_help(self):
        """显示DSL帮助 (已修复导入路径)"""
        try:
            # 修复了不一致的导入路径
            from DSL_utils import avl_dsl
            avl_dsl._show_help()
        except ImportError:
             messagebox.showerror("❌ 导入错误", "无法加载 AVL DSL 帮助。\n请确保 'DSL_utils' 包已正确安装。")
        
    def draw_instructions(self):
        self.canvas.delete("all")
        self.node_vis.clear()
        
        # 绘制标题和说明
        title_text = "🌳 AVL 树可视化系统 - 插入演示：展示插入路径并精确动画显示旋转"
        self.canvas.create_text(
            self.canvas_w/2, 20, 
            text=title_text, 
            font=("Segoe UI", 12, "bold"), 
            fill=self.colors["text_dark"]
        )
        
        # 状态显示区域
        self.status_id = self.canvas.create_text(
            self.canvas_w - 15, 20, 
            anchor="ne", 
            text="", 
            font=self.status_font, 
            fill=self.colors["accent_green"]
        )

    def update_status(self, txt: str):
        """更新状态栏和画布状态"""
        if hasattr(self, 'status_label'):
            self.status_label.config(text=txt)
        
        if self.status_id:
            self.canvas.itemconfig(self.status_id, text=txt)
        else:
            self.status_id = self.canvas.create_text(
                self.canvas_w - 15, 20, 
                anchor="ne", 
                text=txt, 
                font=self.status_font, 
                fill=self.colors["accent_green"]
            )

    def _draw_connection(self, cx, cy, tx, ty):
        """绘制两段式箭头连接线"""
        top = cy + self.node_h/2
        bot = ty - self.node_h/2
        midy = (top + bot) / 2
        
        # 绘制连接线，带有渐变效果
        l1 = self.canvas.create_line(cx, top, cx, midy, width=2.5, fill=self.colors["edge_color"])
        l2 = self.canvas.create_line(cx, midy, tx, bot, arrow=LAST, width=2.5, fill=self.colors["edge_color"])
        return (l1, l2)

    def compute_positions_for_root(self, root: Optional[AVLNode]) -> Dict[str, Tuple[float, float]]:
        """计算节点位置"""
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
        """绘制树结构"""
        self.canvas.delete("all")
        self.draw_instructions()
        
        if root is None:
            # 绘制空树提示
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

        # 绘制节点
        self.node_vis.clear()
        for node, key in node_to_key.items():
            cx, cy = pos[key]
            left, top, right, bottom = cx - self.node_w/2, cy - self.node_h/2, cx + self.node_w/2, cy + self.node_h/2
            
            # 绘制带圆角的节点
            rect = self.canvas.create_rectangle(
                left, top, right, bottom, 
                fill=self.colors["node_normal"], 
                outline=self.colors["accent_blue"], 
                width=2,
                stipple="gray50"  # 添加纹理效果
            )
            
            # 节点内部装饰线
            x1, x2 = left + 28, left + 92
            self.canvas.create_line(x1, top, x1, bottom, width=1, fill="#BBDEFB")
            self.canvas.create_line(x2, top, x2, bottom, width=1, fill="#BBDEFB")
            
            # 节点文本
            txt = self.canvas.create_text(
                (x1+x2)/2, cy, 
                text=str(node.val), 
                font=("Segoe UI", 12, "bold"),
                fill=self.colors["text_dark"]
            )
            
            self.node_vis[key] = {
                'rect': rect, 
                'text': txt, 
                'cx': cx, 
                'cy': cy, 
                'val': str(node.val),
                'edges': {}
            }

        # 绘制边
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

    # ---------- 插入动画流程 ----------
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
                
            self.update_status(f"🔍 搜索路径: 访问 {v} (步骤 {i+1}/{len(path_nodes)})")
            self.window.after(420, lambda: highlight_path(i+1))

        highlight_path(0)

    def animate_flyin_new(self, val_str: str, snap_after_insert: Optional[AVLNode], on_complete):
        """新节点飞入动画"""
        if not snap_after_insert:
            on_complete(); return
            
        pos_after = self.compute_positions_for_root(snap_after_insert)
        candidate_keys = [k for k in pos_after.keys() if k.split('#')[0] == str(val_str)]
        if not candidate_keys:
            on_complete(); return
            
        target_key = candidate_keys[-1]
        tx, ty = pos_after[target_key]

        # 创建临时飞入节点
        sx, sy = self.canvas_w/2, 20
        left, top, right, bottom = sx - self.node_w/2, sy - self.node_h/2, sx + self.node_w/2, sy + self.node_h/2
        
        temp_rect = self.canvas.create_rectangle(
            left, top, right, bottom, 
            fill=self.colors["node_new"], 
            outline=self.colors["accent_green"], 
            width=2
        )
        temp_text = self.canvas.create_text(sx, sy, text=str(val_str), font=("Segoe UI", 12, "bold"))

        steps = 30
        dx = (tx - sx)/steps
        dy = (ty - sy)/steps
        delay = 12
        
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
                    
                self.window.after(300, on_complete)
        step()

    def _redraw_all_edges_during_animation(self):
        """动画期间重绘所有边"""
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
        """单次旋转动画"""
        pos_before = self.compute_positions_for_root(before_root)
        pos_after = self.compute_positions_for_root(after_root)

        self.draw_tree_from_root(before_root)

        keys_common = set(pos_before.keys()) & set(pos_after.keys())
        moves = []
        for k in keys_common:
            item = self.node_vis.get(k)
            if not item:
                continue
            sx, sy = pos_before[k]
            tx, ty = pos_after[k]
            moves.append((k, item['rect'], item['text'], sx, sy, tx, ty))

        # 绘制旋转指示
        rtype = rotation_info.get('type', '')
        label_text = f"🔄 旋转: {rtype}"
        z = rotation_info.get('z'); y = rotation_info.get('y')
        zkey = None; ykey = None
        
        if z:
            zkey = next((k for k in pos_before.keys() if k.split('#')[0]==str(z.val)), None)
        if y:
            ykey = next((k for k in pos_before.keys() if k.split('#')[0]==str(y.val)), None)

        arc_id = None; label_id = None
        if zkey and ykey:
            zx, zy = pos_before[zkey]; yx, yy = pos_before[ykey]
            midx = (zx + yx)/2
            topy = min(zy, yy) - 30
            try:
                arc_id = self.canvas.create_arc(
                    midx-30, topy-20, midx+30, topy+20, 
                    start=0, extent=180, style=ARC, width=3, 
                    outline=self.colors["accent_red"]
                )
                label_id = self.canvas.create_text(
                    midx, topy-28, 
                    text=label_text, 
                    font=("Segoe UI", 11, "bold"), 
                    fill=self.colors["accent_red"]
                )
            except Exception:
                arc_id = None; label_id = None

        frames = 30
        delay = 20

        def rect_center_coords(rect_id):
            coords = self.canvas.coords(rect_id)
            if not coords or len(coords) < 4:
                return (0,0)
            x1,y1,x2,y2 = coords
            return ((x1+x2)/2, (y1+y2)/2)

        def frame_step(f=0):
            if f >= frames:
                self.draw_tree_from_root(after_root)
                if arc_id:
                    try: self.canvas.delete(arc_id)
                    except: pass
                if label_id:
                    try: self.canvas.delete(label_id)
                    except: pass
                self.window.after(300, on_done)
                return
            
            t = (f+1)/frames
            for (k, rect_id, text_id, sx, sy, tx, ty) in moves:
                cur_cx = sx + (tx - sx) * t
                cur_cy = sy + (ty - sy) * t
                try:
                    ccx, ccy = rect_center_coords(rect_id)
                    if (ccx, ccy) == (0,0): continue
                    dx = cur_cx - ccx
                    dy = cur_cy - ccy
                    self.canvas.move(rect_id, dx, dy)
                    self.canvas.move(text_id, dx, dy)
                except Exception:
                    pass

            self._redraw_all_edges_during_animation()
            self.window.after(delay, lambda: frame_step(f+1))
        frame_step(0)

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

    def _after_insert_rotations(self, rotations, snapshots, insertion_idx):
        if not rotations:
            self.draw_tree_from_root(clone_tree(self.model.root))
            self.window.after(300, lambda: self._insert_seq(insertion_idx+1))
            return

        def done_all():
            self.draw_tree_from_root(clone_tree(self.model.root))
            self.window.after(300, lambda: self._insert_seq(insertion_idx+1))
        self._animate_rotations_sequence(rotations, snapshots, insertion_idx, done_all)

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
            # 嵌入模式下不关闭窗口，只是隐藏
            self.window.pack_forget()  # 或者 grid_forget，取决于布局
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