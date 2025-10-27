from tkinter import *
from tkinter import messagebox
from tkinter import Toplevel, filedialog
from typing import Dict, Tuple, List, Optional
from binary_tree.bst.bst_model import BSTModel, TreeNode
import storage as storage
import json
from datetime import datetime
import os
from DSL_utils import process_command
from binary_tree.bst.bst_ui import draw_instructions, create_controls

class BSTVisualizer:
    def __init__(self, root):
        self.window = root
        self.window.title("🌳 二叉搜索树可视化系统")
        self.window.config(bg="#F0F2F5")
        
        # 颜色配置
        self.colors = {
            "bg_primary": "#F0F2F5",
            "bg_secondary": "#FFFFFF",
            "canvas_bg": "#FAFAFA",
            "node_default": "#E3F2FD",
            "node_highlight": "#FFEB3B",
            "node_success": "#C8E6C9",
            "node_warning": "#FFCDD2",
            "node_info": "#B3E5FC",
            "text_primary": "#212121",
            "text_secondary": "#666666",
            "btn_primary": "#2196F3",
            "btn_success": "#4CAF50",
            "btn_warning": "#FF9800",
            "btn_danger": "#F44336",
            "btn_info": "#9C27B0",
            "status_success": "#2E7D32",
            "status_error": "#C62828",
            "guide_bg": "#FFFDE7"
        }
        
        # 初始化核心属性
        self.canvas_width = 1250
        self.canvas_height = 560
        self.model = BSTModel()
        self.node_to_rect: Dict[TreeNode, int] = {}
        self.node_items: List[int] = []
        self.status_text_id: Optional[int] = None

        # 布局参数
        self.node_w = 120
        self.node_h = 44
        self.left_cell_w = 28
        self.center_cell_w = 64
        self.right_cell_w = self.node_w - self.left_cell_w - self.center_cell_w
        self.level_gap = 80  # 减小垂直间距
        self.margin_x = 40

        # 动画和引导模式状态
        self.animating = False
        self.guide_mode = BooleanVar(value=True)  # 提前初始化

        # 输入变量
        self.input_var = StringVar()
        self.dsl_var = StringVar()
        
        # 创建主框架
        self.main_frame = Frame(self.window, bg=self.colors["bg_primary"])
        self.main_frame.pack(fill=BOTH, expand=True, padx=12, pady=12)
        
        # 按正确顺序创建UI组件 - 控制面板在顶部
        self.create_header()
        self.create_control_panel()  # 先创建控制面板
        self.create_canvas_area()    # 再创建画布区域
        
        # 绘制初始界面
        self.redraw()
        
    def create_header(self):
        """创建标题区域"""
        header_frame = Frame(self.main_frame, bg=self.colors["bg_secondary"], 
                           relief=RAISED, bd=1)
        header_frame.pack(fill=X, pady=(0, 8))
        
        title_label = Label(header_frame, text="🌳 二叉搜索树可视化系统", 
                          font=("微软雅黑", 16, "bold"), 
                          bg=self.colors["bg_secondary"],
                          fg=self.colors["text_primary"],
                          pady=10)
        title_label.pack()
        
        subtitle_label = Label(header_frame, 
                             text="动态演示BST的插入、查找、删除操作，支持分步引导和动画展示",
                             font=("微软雅黑", 10), 
                             bg=self.colors["bg_secondary"],
                             fg=self.colors["text_secondary"])
        subtitle_label.pack(pady=(0, 8))

    def create_control_panel(self):
        """创建控制面板 - 放在顶部"""
        control_frame = Frame(self.main_frame, bg=self.colors["bg_secondary"],
                            relief=SOLID, bd=1)
        control_frame.pack(fill=X, pady=(0, 8))
        
        # 输入区域
        input_frame = Frame(control_frame, bg=self.colors["bg_secondary"])
        input_frame.pack(fill=X, padx=15, pady=8)
        
        Label(input_frame, text="节点值:", 
              font=("微软雅黑", 10), 
              bg=self.colors["bg_secondary"]).grid(row=0, column=0, sticky=W, pady=4)
        
        self.entry = Entry(input_frame, textvariable=self.input_var, 
                          width=25, font=("微软雅黑", 10),
                          relief=SOLID, bd=1)
        self.entry.grid(row=0, column=1, padx=8, pady=4, sticky=W)
        self.entry.insert(0, "15,6,23,4,7,71,5")
        
        # DSL输入区域
        Label(input_frame, text="DSL命令:", 
              font=("微软雅黑", 10), 
              bg=self.colors["bg_secondary"]).grid(row=0, column=2, sticky=W, pady=4, padx=(20,0))
        
        self.dsl_entry = Entry(input_frame, textvariable=self.dsl_var,
                              width=15, font=("微软雅黑", 10),
                              relief=SOLID, bd=1)
        self.dsl_entry.grid(row=0, column=3, padx=8, pady=4, sticky=W)
        self.dsl_entry.bind("<Return>", self.process_dsl)
        
        # 按钮区域 - 两行按钮
        btn_frame = Frame(control_frame, bg=self.colors["bg_secondary"])
        btn_frame.pack(fill=X, padx=15, pady=8)
        
        # 第一行按钮 - 主要操作
        btn_row1 = Frame(btn_frame, bg=self.colors["bg_secondary"])
        btn_row1.pack(fill=X, pady=4)
        
        self.create_button(btn_row1, "✨ 插入节点", 
                         self.insert_direct, self.colors["btn_success"]).pack(side=LEFT, padx=2)
        self.create_button(btn_row1, "🎬 动画插入", 
                         self.start_insert_animated, "#009688").pack(side=LEFT, padx=2)
        self.create_button(btn_row1, "🔍 查找节点", 
                         self.start_search_animated, self.colors["btn_primary"]).pack(side=LEFT, padx=2)
        self.create_button(btn_row1, "🗑️ 删除节点", 
                         self.start_delete_animated, self.colors["btn_danger"]).pack(side=LEFT, padx=2)
        
        # 第二行按钮 - 辅助操作
        btn_row2 = Frame(btn_frame, bg=self.colors["bg_secondary"])
        btn_row2.pack(fill=X, pady=4)
        
        self.create_button(btn_row2, "💾 保存结构", 
                         self.save_tree, "#9C27B0").pack(side=LEFT, padx=2)
        self.create_button(btn_row2, "📂 加载结构", 
                         self.load_tree, "#9C27B0").pack(side=LEFT, padx=2)
        self.create_button(btn_row2, "🧹 清空树", 
                         self.clear_canvas, self.colors["btn_warning"]).pack(side=LEFT, padx=2)
        self.create_button(btn_row2, "🚪 返回主界面", 
                         self.back_to_main, "#795548").pack(side=LEFT, padx=2)
        self.create_button(btn_row2, "⚡ 执行DSL", 
                         self.process_dsl, "#607D8B").pack(side=LEFT, padx=2)
        
        # 配置网格权重
        input_frame.columnconfigure(1, weight=1)

    def create_canvas_area(self):
        """创建画布区域 - 放在控制面板下方"""
        canvas_container = Frame(self.main_frame, bg=self.colors["bg_secondary"],
                               relief=SOLID, bd=1)
        canvas_container.pack(fill=BOTH, expand=True, pady=(0, 8))
        
        # 画布控制栏
        canvas_toolbar = Frame(canvas_container, bg=self.colors["bg_secondary"], height=28)
        canvas_toolbar.pack(fill=X, padx=10, pady=6)
        canvas_toolbar.pack_propagate(False)
        
        self.status_label = Label(canvas_toolbar, text="🟢 就绪", 
                                font=("微软雅黑", 10), 
                                bg=self.colors["bg_secondary"],
                                fg=self.colors["status_success"],
                                anchor=W)
        self.status_label.pack(side=LEFT, fill=X, expand=True)
        
        # 引导模式复选框
        self.guide_check = Checkbutton(canvas_toolbar, text="启用分步引导模式", 
                                      variable=self.guide_mode,
                                      bg=self.colors["bg_secondary"],
                                      font=("微软雅黑", 9),
                                      command=self._on_guide_mode_changed)
        self.guide_check.pack(side=RIGHT, padx=10)
        
        # 创建画布框架（带滚动条）
        canvas_frame = Frame(canvas_container)
        canvas_frame.pack(padx=10, pady=(0, 8), fill=BOTH, expand=True)
        
        # 添加垂直滚动条
        vscrollbar = Scrollbar(canvas_frame, orient=VERTICAL)
        vscrollbar.pack(side=RIGHT, fill=Y)
        
        # 添加水平滚动条
        hscrollbar = Scrollbar(canvas_frame, orient=HORIZONTAL)
        hscrollbar.pack(side=BOTTOM, fill=X)
        
        # 画布（支持滚动）
        self.canvas = Canvas(canvas_frame, bg=self.colors["canvas_bg"],
                           width=self.canvas_width, height=self.canvas_height,
                           relief=FLAT, highlightthickness=1,
                           highlightbackground="#E0E0E0",
                           yscrollcommand=vscrollbar.set,
                           xscrollcommand=hscrollbar.set)
        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)
        
        # 配置滚动条
        vscrollbar.config(command=self.canvas.yview)
        hscrollbar.config(command=self.canvas.xview)
        
        # 绑定鼠标滚轮事件
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Shift-MouseWheel>", self._on_shift_mousewheel)
        
        # 引导信息标签
        self.guide_label = Label(canvas_container, text="", font=("微软雅黑", 10, "bold"), 
                                fg="#D35400", bg=self.colors["guide_bg"], relief=SOLID, bd=1,
                                wraplength=1200, justify=CENTER, height=2)
        self.guide_label.pack(fill=X, padx=10, pady=(0, 8))

    def create_button(self, parent, text, command, color):
        """创建样式化按钮"""
        return Button(parent, text=text, command=command,
                     bg=color, fg="white", font=("微软雅黑", 9),
                     relief=FLAT, bd=0, padx=12, pady=6,
                     cursor="hand2", activebackground=self._darken_color(color))

    def _darken_color(self, color):
        """加深颜色用于按钮激活状态"""
        if color.startswith("#"):
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            r = max(0, r - 30)
            g = max(0, g - 30)
            b = max(0, b - 30)
            return f"#{r:02x}{g:02x}{b:02x}"
        return color

    def _on_guide_mode_changed(self):
        """引导模式改变时的回调"""
        if not self.guide_mode.get():
            self.guide_label.config(bg=self.colors["bg_secondary"])
        else:
            self.guide_label.config(bg=self.colors["guide_bg"])
        
    def update_guide(self, text: str):
        """更新引导文本"""
        if not self.guide_mode.get():
            return
            
        self.guide_label.config(text=text)
        
        # 同时在画布底部也显示
        if hasattr(self, 'guide_text_id') and self.guide_text_id:
            self.canvas.delete(self.guide_text_id)
        self.guide_text_id = self.canvas.create_text(
            self.canvas_width/2, self.canvas_height - 20, 
            text=text, font=("微软雅黑", 10, "bold"), 
            fill="#D35400", width=self.canvas_width-40
        )
    
    def clear_guide(self):
        """清除引导文本"""
        self.guide_label.config(text="")
        if hasattr(self, 'guide_text_id') and self.guide_text_id:
            self.canvas.delete(self.guide_text_id)
            self.guide_text_id = None
        
    def _on_mousewheel(self, event):
        """处理垂直滚动"""
        if event.state & 0x0004:  # Shift键被按下时，进行水平滚动
            self.canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")
        else:  # 否则进行垂直滚动
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    def _on_shift_mousewheel(self, event):
        """处理水平滚动（备用方法）"""
        self.canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")

    def process_dsl(self, event=None):
        text = (self.dsl_var.get() or "").strip()
        if not text:
            return
        if getattr(self, "animating", False):
            messagebox.showinfo("提示", "请等待当前动画完成")
            return
        process_command(self, text)
        self.dsl_var.set("")
    
    def update_status(self, text: str):
        """更新状态文本"""
        self.status_label.config(text=text)
        # 同时在画布上也显示状态
        if not self.status_text_id:
            self.status_text_id = self.canvas.create_text(
                self.canvas_width-10, 10, anchor="ne", 
                text=text, font=("微软雅黑", 10, "bold"), 
                fill=self.colors["status_success"]
            )
        else:
            self.canvas.itemconfig(self.status_text_id, text=text)

    # 其他方法保持不变...
    def _ensure_tree_folder(self) -> str:
        if hasattr(storage, "ensure_save_subdir"):
            return storage.ensure_save_subdir("bst")
        base_dir = os.path.dirname(os.path.abspath(storage.__file__))
        default_dir = os.path.join(base_dir, "save", "bst")
        os.makedirs(default_dir, exist_ok=True)
        return default_dir

    def save_tree(self):
        default_dir = self._ensure_tree_folder()
        default_name = f"bst_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = filedialog.asksaveasfilename(
            initialdir=default_dir,
            initialfile=default_name,
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="保存树到文件"
        )
        if not filepath:  # 用户取消保存
            return
            
        tree_dict = storage.tree_to_dict(self.model.root)
        
        metadata = {
            "saved_at": datetime.now().isoformat(),
            "node_count": len(tree_dict.get("nodes", [])) if isinstance(tree_dict, dict) else 0
        }
        payload = {"type": "tree", "tree": tree_dict, "metadata": metadata}
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)
            messagebox.showinfo("成功", f"✅ 二叉搜索树已保存到：\n{filepath}")
            self.update_status("💾 保存成功")
        except Exception as e:
            messagebox.showerror("错误", f"保存失败：{str(e)}")

    def load_tree(self):
        if self.animating:
            messagebox.showinfo("提示", "⏳ 请等待当前动画完成")
            return
            
        default_dir = self._ensure_tree_folder()
        filepath = filedialog.askopenfilename(
            initialdir=default_dir,
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="从文件加载二叉树"
        )
        if not filepath:  # 用户取消加载
            return
            
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                obj = json.load(f)
            tree_dict = obj.get("tree", {})
            if hasattr(storage, "tree_dict_to_nodes"):
                new_root = storage.tree_dict_to_nodes(tree_dict, TreeNode)
                self.model.root = new_root
                self.redraw()
                messagebox.showinfo("成功", "✅ 二叉树已成功加载并恢复")
                self.update_status("📂 加载成功")
        except Exception as e:
            messagebox.showerror("错误", f"加载失败：{str(e)}")

    def compute_positions(self) -> Dict[TreeNode, Tuple[float,float]]:
        pos: Dict[TreeNode, Tuple[float,float]] = {}
        nodes_inorder: List[TreeNode] = []
        depths: Dict[TreeNode, int] = {}

        def inorder(n: Optional[TreeNode], d: int):
            if n is None:
                return
            inorder(n.left, d+1)
            nodes_inorder.append(n)
            depths[n] = d
            inorder(n.right, d+1)

        inorder(self.model.root, 0)
        n = len(nodes_inorder)
        if n == 0:
            return pos
        width = self.canvas_width - 2*self.margin_x
        for i, node in enumerate(nodes_inorder):
            if n == 1:
                x = self.canvas_width / 2
            else:
                x = self.margin_x + i * (width / (n-1))
            y = 80 + depths[node] * self.level_gap
            pos[node] = (x, y)
        return pos

    def redraw(self):
        self.canvas.delete("all")
        self.node_items.clear()
        self.node_to_rect.clear()
        self.draw_instructions()
        if self.model.root is None:
            self.canvas.create_text(
                self.canvas_width/2, self.canvas_height/2, 
                text="🌳 空树 - 请插入节点开始可视化", 
                font=("微软雅黑", 14), fill="#9E9E9E"
            )
            return
        pos = self.compute_positions()
        # 先绘制边
        for node, (cx, cy) in pos.items():
            if node.left and node.left in pos:
                lx, ly = pos[node.left]
                self._draw_connection(cx, cy, lx, ly)
            if node.right and node.right in pos:
                rx, ry = pos[node.right]
                self._draw_connection(cx, cy, rx, ry)
        # 绘制节点
        for node, (cx, cy) in pos.items():
            self._draw_node(node, cx, cy)

    def _draw_connection(self, cx, cy, tx, ty):
        """绘制节点连接线"""
        top = cy + self.node_h/2
        bot = ty - self.node_h/2
        mid_y = (top + bot) / 2
        
        # 绘制带箭头的连接线
        line = self.canvas.create_line(cx, top, cx, mid_y, tx, bot, 
                                     width=2, fill="#78909C", arrow=LAST,
                                     smooth=True)
        self.node_items.append(line)

    def _draw_node(self, node: TreeNode, cx: float, cy: float):
        """绘制树节点"""
        left = cx - self.node_w/2
        top = cy - self.node_h/2
        right = cx + self.node_w/2
        bottom = cy + self.node_h/2
        
        # 绘制节点主体
        rect = self.canvas.create_rectangle(
            left, top, right, bottom, 
            fill=self.colors["node_default"], 
            outline="#1976D2", width=2
        )
        self.node_to_rect[node] = rect
        self.node_items.append(rect)
        
        # 节点内部区域分隔
        x1 = left + self.left_cell_w
        x2 = x1 + self.center_cell_w
        v1 = self.canvas.create_line(x1, top, x1, bottom, width=1, fill="#BBDEFB")
        v2 = self.canvas.create_line(x2, top, x2, bottom, width=1, fill="#BBDEFB")
        self.node_items += [v1, v2]
        
        # 节点值
        self.canvas.create_text(
            (x1+x2)/2, (top+bottom)/2, 
            text=str(node.val), 
            font=("微软雅黑", 11, "bold"),
            fill=self.colors["text_primary"]
        )

    def draw_instructions(self):
        """绘制操作说明"""
        # 绘制说明文字
        self.canvas.create_text(
            self.canvas_width/2, 30, 
            text="🌳 二叉搜索树可视化演示 - 支持插入、查找、删除操作的动态展示", 
            font=("微软雅黑", 11, "bold"), 
            fill="#333333", 
            tags="instructions"
        )
        
        # 绘制特性说明
        self.canvas.create_text(
            10, 55, anchor="nw",
            text="• 中序遍历用于横向布局 • 红色高亮显示搜索路径 • 绿色表示操作成功", 
            font=("微软雅黑", 9),
            fill="#666666",
            tags="instructions"
        )
        
        if self.status_text_id:
            self.canvas.delete(self.status_text_id)
        
        self.status_text_id = self.canvas.create_text(
            self.canvas_width-10, 55, anchor="ne", text="", 
            font=("微软雅黑", 10, "bold"), 
            fill="#2E7D32", 
            tags="instructions"
        )

    def parse_value(self, s: str):
        s = s.strip()
        try:
            return int(s)
        except Exception:
            try:
                return float(s)
            except Exception:
                return s

    def insert_direct(self):
        """直接插入节点"""
        if self.animating:
            messagebox.showinfo("提示", "⏳ 当前正在执行动画，请稍候...")
            return
            
        text = self.input_var.get().strip()
        if not text:
            messagebox.showinfo("提示", "📝 请输入要插入的值（多个值用逗号分隔）")
            return
            
        try:
            items = [self.parse_value(s) for s in text.split(",") if s.strip() != ""]
            for v in items:
                self.model.insert(v)
            self.redraw()
            self.update_status(f"✅ 已插入 {len(items)} 个节点")
            self.update_guide(f"✨ 成功插入 {len(items)} 个节点: {', '.join(map(str, items))}")
        except Exception as e:
            messagebox.showerror("错误", f"插入失败：{str(e)}")

    def start_insert_animated(self):
        """开始动画插入"""
        if self.animating:
            messagebox.showinfo("提示", "⏳ 当前正在执行动画，请稍候...")
            return
            
        text = self.input_var.get().strip()
        if not text:
            messagebox.showinfo("提示", "📝 请输入要插入的值（多个值用逗号分隔）")
            return  
            
        try:
            items = [self.parse_value(s) for s in text.split(",") if s.strip() != ""]
            if not items:
                return
            self.animating = True
            self.clear_guide()
            self.update_guide(f"🚀 开始插入操作：将依次插入 {len(items)} 个值")
            self.window.after(1000, lambda: self._insert_seq(items, 0))
        except Exception as e:
            messagebox.showerror("错误", f"插入失败：{str(e)}")

    def _insert_seq(self, items: List[str], idx: int):
        if idx >= len(items):
            self.animating = False
            self.update_status("✅ 插入完成")
            self.update_guide("🎉 所有插入操作已完成！")
            self.window.after(2000, self.clear_guide)
            return
            
        val = items[idx]
        remaining = len(items) - idx - 1
        self.update_guide(f"📥 准备插入第 {idx+1}/{len(items)} 个值: {val} ({remaining} 个待插入)")
        self.window.after(800, lambda: self._animate_search_path_for_insert(val, items, idx))

    def _animate_search_path_for_insert(self, val: str, items: List[str], idx: int):
        path_nodes = []
        explanations = []
        
        cur = self.model.root
        if cur is None:
            self.update_guide(f"🌱 树为空，将 {val} 作为根节点插入")
            self.redraw()
            self.window.after(800, lambda: self._finalize_insert_and_continue(val, items, idx))
            return

        # 构建路径和解释
        step_count = 0
        while cur:
            path_nodes.append(cur)
            step_count += 1
            cmp = self.model.compare_values(val, cur.val)
            
            if cmp == 0:
                explanation = f"🔍 步骤{step_count}: {val} = {cur.val}，向右子树移动（BST允许重复值）"
                cur = cur.right
            elif cmp < 0:
                explanation = f"🔍 步骤{step_count}: {val} < {cur.val}，向左子树移动（较小值在左）"
                cur = cur.left
            else:
                explanation = f"🔍 步骤{step_count}: {val} > {cur.val}，向右子树移动（较大值在右）"
                cur = cur.right
                
            explanations.append(explanation)

        self._play_highlight_sequence_with_explanations(path_nodes, explanations, val, items, idx)

    def _play_highlight_sequence_with_explanations(self, nodes: List[TreeNode], explanations: List[str], val: str, items: List[str], idx: int):
        if not nodes:
            self.update_guide(f"📍 找到插入位置，准备插入新节点 {val}")
            self.window.after(800, lambda: self._finalize_insert_and_continue(val, items, idx))
            return
            
        i = 0
        def step():
            nonlocal i
            if i >= len(nodes):
                self.update_guide(f"📍 搜索完成，准备在适当位置插入 {val}")
                self.window.after(800, lambda: self._finalize_insert_and_continue(val, items, idx))
                return
                
            node = nodes[i]
            explanation = explanations[i] if i < len(explanations) else f"访问节点 {node.val}"
            
            self.redraw()
            if node in self.node_to_rect:
                rid = self.node_to_rect[node]
                self.canvas.itemconfig(rid, fill=self.colors["node_highlight"])
                
            self.update_status(f"插入 {val}: 步骤 {i+1}/{len(nodes)}")
            self.update_guide(explanation)
            
            i += 1
            self.window.after(1000, step)
            
        step()

    def _finalize_insert_and_continue(self, val, items, idx):
        new_node = self.model.insert(val)
        pos_map = self.compute_positions()
        
        if new_node not in pos_map:
            self.redraw()
            self.update_guide(f"✅ 已插入 {val}，继续下一个值")
            self.window.after(800, lambda: self._insert_seq(items, idx+1))
            return
            
        # 显示新节点移动动画
        tx, ty = pos_map[new_node]
        sx, sy = self.canvas_width/2, 20
        
        self.update_guide(f"🎯 正在将新节点 {val} 放置到正确位置...")
        
        # 创建移动的新节点
        left = sx - self.node_w/2
        top = sy - self.node_h/2
        right = sx + self.node_w/2
        bottom = sy + self.node_h/2
        
        temp_rect = self.canvas.create_rectangle(left, top, right, bottom, 
                                               fill=self.colors["node_success"], 
                                               outline="#4CAF50", width=2)
        x1 = left + self.left_cell_w
        x2 = x1 + self.center_cell_w
        temp_text = self.canvas.create_text((x1+x2)/2, (top+bottom)/2, 
                                          text=str(val), font=("微软雅黑", 11, "bold"))

        steps = 30
        dx = (tx - sx)/steps
        dy = (ty - sy)/steps
        delay = 15

        def step(i=0):
            if i < steps:
                self.canvas.move(temp_rect, dx, dy)
                self.canvas.move(temp_text, dx, dy)
                self.window.after(delay, lambda: step(i+1))
            else:
                try:
                    self.canvas.delete(temp_rect)
                    self.canvas.delete(temp_text)
                except Exception:
                    pass
                    
                # 重绘完整树
                self.redraw()
                
                # 高亮显示新节点
                if new_node in self.node_to_rect:
                    rid = self.node_to_rect[new_node]
                    self.canvas.itemconfig(rid, fill=self.colors["node_success"])
                    self.update_guide(f"✅ 成功插入 {val}！新节点已放置在正确位置")
                    
                    def unhigh():
                        try:
                            self.canvas.itemconfig(rid, fill=self.colors["node_default"])
                        except Exception:
                            pass
                        # 继续插入下一个值
                        self.window.after(500, lambda: self._insert_seq(items, idx+1))
                    self.window.after(1000, unhigh)
                else:
                    self.window.after(500, lambda: self._insert_seq(items, idx+1))

        step()

    def start_search_animated(self):
        """开始动画查找"""
        if self.animating:
            messagebox.showinfo("提示", "⏳ 当前正在执行动画，请稍候...")
            return
            
        raw = self.input_var.get().strip()
        if not raw:
            messagebox.showinfo("提示", "🔍 请输入要查找的值")
            return
            
        try:
            val = self.parse_value(raw)
            self.animating = True
            self.clear_guide()
            
            self.update_guide(f"🔎 开始查找值 {val}：从根节点开始比较")
            
            path_nodes = []
            explanations = []
            cur = self.model.root
            
            if cur is None:
                self.update_guide("❌ 树为空，无法查找")
                self.animating = False
                return
            
            step_count = 0
            while cur:
                step_count += 1
                path_nodes.append(cur)
                cmp = self.model.compare_values(val, cur.val)
                
                if cmp == 0:
                    explanations.append(f"🎉 步骤{step_count}: 找到目标值 {val}！查找成功")
                    break
                elif cmp < 0:
                    explanations.append(f"🔍 步骤{step_count}: {val} < {cur.val}，向左子树继续查找")
                    cur = cur.left
                else:
                    explanations.append(f"🔍 步骤{step_count}: {val} > {cur.val}，向右子树继续查找")
                    cur = cur.right
                    
            found = (path_nodes and self.model.compare_values(val, path_nodes[-1].val) == 0)
            
            if not found and path_nodes:
                explanations.append(f"❌ 步骤{step_count}: 到达叶子节点，未找到值 {val}，查找失败")
                
            i = 0
            def step():
                nonlocal i
                if i >= len(path_nodes):
                    self.animating = False
                    if found:
                        node = path_nodes[-1]
                        self.redraw()
                        if node in self.node_to_rect:
                            rid = self.node_to_rect[node]
                            self.canvas.itemconfig(rid, fill=self.colors["node_success"])
                            self.update_guide(f"🎉 查找成功！在BST中找到值 {val}")
                        self.window.after(1500, lambda: self.canvas.itemconfig(rid, fill=self.colors["node_default"]) if 'rid' in locals() else None)
                    else:
                        self.update_guide(f"❌ 查找失败：BST中不存在值 {val}")
                    return
                    
                node = path_nodes[i]
                explanation = explanations[i] if i < len(explanations) else f"访问节点 {node.val}"
                
                self.redraw()
                if node in self.node_to_rect:
                    rid = self.node_to_rect[node]
                    self.canvas.itemconfig(rid, fill=self.colors["node_highlight"])
                    
                self.update_status(f"查找: 步骤 {i+1}/{len(path_nodes)}")
                self.update_guide(explanation)
                
                i += 1
                self.window.after(1000, step)
                
            step()
        except Exception as e:
            messagebox.showerror("错误", f"查找失败：{str(e)}")
            self.animating = False

    def start_delete_animated(self):
        """开始动画删除"""
        if self.animating:
            messagebox.showinfo("提示", "⏳ 当前正在执行动画，请稍候...")
            return
            
        raw = self.input_var.get().strip()
        if not raw:
            messagebox.showinfo("提示", "🗑️ 请输入要删除的值")
            return
            
        try:
            val = self.parse_value(raw)
            self.animating = True
            self.clear_guide()
            
            self.update_guide(f"🗑️ 开始删除值 {val}：首先定位目标节点")

            path_nodes = []
            explanations = []
            cur = self.model.root
            
            if cur is None:
                self.update_guide("❌ 树为空，无法删除")
                self.animating = False
                return
            
            step_count = 0
            while cur:
                step_count += 1
                path_nodes.append(cur)
                cmp = self.model.compare_values(val, cur.val)
                
                if cmp == 0:
                    explanations.append(f"🎯 步骤{step_count}: 找到要删除的节点 {val}，开始删除操作")
                    break
                elif cmp < 0:
                    explanations.append(f"🔍 步骤{step_count}: {val} < {cur.val}，向左子树继续查找")
                    cur = cur.left
                else:
                    explanations.append(f"🔍 步骤{step_count}: {val} > {cur.val}，向右子树继续查找")
                    cur = cur.right

            found = (path_nodes and self.model.compare_values(val, path_nodes[-1].val) == 0)
            
            if not found and path_nodes:
                explanations.append(f"❌ 步骤{step_count}: 未找到要删除的值 {val}，删除操作终止")
                
            i = 0
            def step():
                nonlocal i
                if i >= len(path_nodes):
                    if not found:
                        self.animating = False
                        self.update_guide(f"❌ 删除失败：BST中不存在值 {val}")
                        return
                    self._animate_deletion_process(val, path_nodes[-1])
                    return
                    
                node = path_nodes[i]
                explanation = explanations[i] if i < len(explanations) else f"访问节点 {node.val}"
                
                self.redraw()
                if node in self.node_to_rect:
                    self.canvas.itemconfig(self.node_to_rect[node], fill=self.colors["node_highlight"])
                    
                self.update_status(f"删除：步骤 {i+1}/{len(path_nodes)}")
                self.update_guide(explanation)
                
                i += 1
                self.window.after(1000, step)
                
            step()
        except Exception as e:
            messagebox.showerror("错误", f"删除失败：{str(e)}")
            self.animating = False

    def _animate_deletion_process(self, val, target_node):
        self.redraw()
        if target_node in self.node_to_rect:
            self.canvas.itemconfig(self.node_to_rect[target_node], fill=self.colors["node_warning"])
            self.update_guide(f"🎯 已定位到要删除的节点 {val}，分析节点类型...")
        
        def after_highlight():
            # 情况1：叶子节点
            if target_node.left is None and target_node.right is None:
                self.update_guide(f"🍃 节点 {val} 是叶子节点（无子节点），直接删除")
                def do_delete():
                    self.model.delete(val)
                    self.redraw()
                    self.update_guide(f"✅ 叶子节点 {val} 已成功删除")
                    self.animating = False
                self.window.after(1200, do_delete)
                
            # 情况2：只有一个子节点
            elif target_node.left is None or target_node.right is None:
                child = target_node.left if target_node.left else target_node.right
                child_type = "左" if target_node.left else "右"
                self.update_guide(f"📋 节点 {val} 有一个{child_type}子节点 {child.val}，用子节点替换当前节点")
                
                self.redraw()
                if child in self.node_to_rect:
                    self.canvas.itemconfig(self.node_to_rect[child], fill="#FFD93D")
                    
                def do_transplant():
                    self.model.delete(val)
                    self.redraw()
                    self.update_guide(f"✅ 已删除 {val}，其{child_type}子节点 {child.val} 提升到该位置")
                    self.animating = False
                self.window.after(1200, do_transplant)
                
            # 情况3：有两个子节点
            else:
                self.update_guide(f"🔄 节点 {val} 有两个子节点，寻找右子树中的最小值作为后继节点")
                succ = self.model.find_min(target_node.right)
                
                self.redraw()
                if succ in self.node_to_rect:
                    self.canvas.itemconfig(self.node_to_rect[succ], fill="#6BCF77")
                    self.update_guide(f"📌 找到后继节点 {succ.val}，用后继节点的值替换目标节点的值")
                    
                def swap_and_delete():
                    # 交换值
                    old_val = target_node.val
                    target_node.val = succ.val
                    succ.val = old_val
                    
                    self.redraw()
                    if target_node in self.node_to_rect:
                        self.canvas.itemconfig(self.node_to_rect[target_node], fill="#4ECDC4")
                        
                    self.update_guide(f"🔄 值已交换：节点现在包含 {target_node.val}，原值移到后继节点位置")
                    
                    def final_del():
                        self.update_guide(f"🗑️ 删除原后继节点（现在包含值 {old_val}）")
                        self.model.delete_node(succ)  
                        self.redraw()
                        self.update_guide(f"✅ 删除完成！BST结构已保持有序性")
                        self.animating = False
                    self.window.after(1200, final_del)
                    
                self.window.after(1200, swap_and_delete)
                
        self.window.after(800, after_highlight)

    def clear_canvas(self):
        """清空画布"""
        if self.animating:
            messagebox.showinfo("提示", "⏳ 当前正在执行动画，请稍候...")
            return
            
        self.model = BSTModel()
        self.redraw()
        self.update_status("🧹 已清空BST")
        self.clear_guide()

    def back_to_main(self):
        """返回主界面"""
        if self.animating:
            messagebox.showinfo("提示", "⏳ 正在执行动画，请等待完成")
            return
            
        if messagebox.askyesno("确认返回", "确定要返回主界面吗？"):
            self.window.destroy()
        
if __name__ == '__main__':
    w = Tk()
    w.title("🌳 二叉搜索树可视化系统")
    w.geometry("1350x800")
        
    BSTVisualizer(w)
    w.mainloop()