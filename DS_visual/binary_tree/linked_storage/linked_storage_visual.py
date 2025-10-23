from tkinter import *
from tkinter import messagebox, filedialog
from binary_tree.linked_storage.linked_storage_model import BinaryTreeModel, TreeNode
from typing import Dict, Tuple, List, Optional
import math
import storage as storage
import os
import json
from datetime import datetime
import re

class BinaryTreeVisualizer:
    def __init__(self, root):
        self.window = root
        self.window.config(bg="#F3F6FA")
        self.window.title("二叉树可视化工具")
        self.canvas_width = 1250
        self.canvas_height = 520
        self.canvas = Canvas(self.window, bg="#F3F6FA", width=self.canvas_width, height=self.canvas_height,
                             relief=FLAT, bd=0, highlightthickness=0)
        self.canvas.pack(pady=(10, 0), padx=15, fill=BOTH, expand=True)
        self.root_node: Optional[TreeNode] = None
        self.node_items: List[int] = []
        self.node_to_rect: Dict[TreeNode, int] = {}
        self.node_w = 120
        self.node_h = 44
        self.left_cell_w = 28
        self.center_cell_w = 64
        self.right_cell_w = self.node_w - self.left_cell_w - self.center_cell_w
        self.level_gap = 100
        self.input_var = StringVar()
        self.dsl_var = StringVar()  # 新增：DSL输入框变量
        self.batch_queue: List[str] = []
        self.animating = False
        self.status_text_id: Optional[int] = None
        self.dsl_history: List[str] = []
        self.history_index = -1
        self.create_controls()
        self.draw_decorations()
        self.draw_instructions()

    def draw_rounded_rect(self, x1, y1, x2, y2, r=12, **kwargs):
        if r <= 0:
            return [self.canvas.create_rectangle(x1, y1, x2, y2, **kwargs)]
        ids = []
        ids.append(self.canvas.create_arc(x1, y1, x1+2*r, y1+2*r, start=90, extent=90, style=PIESLICE, **kwargs))
        ids.append(self.canvas.create_arc(x2-2*r, y1, x2, y1+2*r, start=0, extent=90, style=PIESLICE, **kwargs))
        ids.append(self.canvas.create_arc(x1, y2-2*r, x1+2*r, y2, start=180, extent=90, style=PIESLICE, **kwargs))
        ids.append(self.canvas.create_arc(x2-2*r, y2-2*r, x2, y2, start=270, extent=90, style=PIESLICE, **kwargs))
        ids.append(self.canvas.create_rectangle(x1+r, y1, x2-r, y2, **kwargs))
        ids.append(self.canvas.create_rectangle(x1, y1+r, x2, y2-r, **kwargs))
        return ids

    def draw_decorations(self):
        self.canvas.delete("decor")
        cx1, cy1 = 12, 12
        cx2, cy2 = self.canvas_width - 12, self.canvas_height - 12
        shadow_ids = []
        for i, off in enumerate((6,4,2)):
            alpha_fill = "#E6EDF6" if i == 0 else "#EEF6F9"
            sid = self.canvas.create_rectangle(cx1+off, cy1+off, cx2+off, cy2+off, fill=alpha_fill, outline="", tags=("decor",))
            shadow_ids.append(sid)
        card_ids = self.draw_rounded_rect(cx1, cy1, cx2, cy2, r=14, fill="#FFFFFF", outline="", tags=None)
        for _id in card_ids:
            self.canvas.addtag_withtag("decor", _id)
        dot1 = self.canvas.create_oval(cx1+18, cy1+18, cx1+58, cy1+58, fill="#E6F2FF", outline="", tags=("decor",))
        arc = self.canvas.create_oval(cx2-120, cy1-40, cx2+40, cy1+120, fill="#F0FAF4", outline="", tags=("decor",))
        for i in range(3):
            r = 40 + i*18
            opacity = 0.06 + i*0.02
            col = "#F3F8F6" if i % 2 == 0 else "#EEF8FF"
            c = self.canvas.create_oval(cx2 - r - 20, cy2 - r - 20, cx2 + r - 20, cy2 + r - 20, fill=col, outline="", tags=("decor",))
        step = 80
        for x in range(int(cx1)+step, int(cx2), step):
            gid = self.canvas.create_line(x, cy1+20, x, cy2-20, fill="#F4F7FA", dash=(2,6), tags=("decor",))
        for y in range(int(cy1)+step, int(cy2), step):
            gid = self.canvas.create_line(cx1+20, y, cx2-20, y, fill="#F8FAFC", dash=(2,6), tags=("decor",))
        self.canvas.tag_lower("decor")

    def create_controls(self):
        # 创建主控制框架
        main_control_frame = Frame(self.window, bg="#F3F6FB")
        main_control_frame.pack(fill=X, padx=15, pady=10)
        
        # 标题
        title_label = Label(main_control_frame, text="二叉树可视化工具", font=("Segoe UI", 16, "bold"),
                          bg="#F3F6FB", fg="#2D3748")
        title_label.pack(pady=(0, 10))
        
        # 输入框行
        input_frame = Frame(main_control_frame, bg="#F3F6FB")
        input_frame.pack(fill=X, pady=5)
        
        # 层序序列输入
        level_order_label = Label(input_frame, text="层序序列:", font=("Segoe UI", 11),
                                 bg="#F3F6FB", fg="#4A5568")
        level_order_label.grid(row=0, column=0, sticky=W, padx=(0, 10))
        
        level_order_entry = Entry(input_frame, textvariable=self.input_var, width=50, font=("Segoe UI", 11),
                                 relief=SOLID, bd=1, highlightthickness=1, highlightcolor="#4299E1",
                                 highlightbackground="#CBD5E0")
        level_order_entry.grid(row=0, column=1, sticky=EW, padx=(0, 20))
        level_order_entry.insert(0, "1,2,3,#,4,#,5")
        level_order_entry.bind("<Return>", lambda e: self.build_tree_from_input())
        
        # DSL输入
        dsl_label = Label(input_frame, text="DSL命令:", font=("Segoe UI", 11),
                         bg="#F3F6FB", fg="#4A5568")
        dsl_label.grid(row=0, column=2, sticky=W, padx=(0, 10))
        
        dsl_entry = Entry(input_frame, textvariable=self.dsl_var, width=25, font=("Segoe UI", 11),
                         relief=SOLID, bd=1, highlightthickness=1, highlightcolor="#9F7AEA",
                         highlightbackground="#CBD5E0")
        dsl_entry.grid(row=0, column=3, sticky=EW)
        dsl_entry.insert(0, "help")
        dsl_entry.bind("<Return>", self.process_dsl)
        dsl_entry.bind("<Up>", self.show_prev_history)
        dsl_entry.bind("<Down>", self.show_next_history)
        
        # 配置列权重
        input_frame.columnconfigure(1, weight=1)
        input_frame.columnconfigure(3, weight=1)
        
        # 按钮行 - 使用两行布局确保所有按钮可见
        button_frame1 = Frame(main_control_frame, bg="#F3F6FB")
        button_frame1.pack(fill=X, pady=5)
        
        button_frame2 = Frame(main_control_frame, bg="#F3F6FB")
        button_frame2.pack(fill=X, pady=5)

        button_style = {"font": ("Segoe UI", 10), "width": 12, "height": 1,
                       "relief": FLAT, "bd": 0, "cursor": "hand2"}

        # 第一行按钮
        build_btn = Button(button_frame1, text="一步构建", **button_style,
                          bg="#48BB78", fg="white", activebackground="#38A169",
                          command=self.build_tree_from_input)
        build_btn.pack(side=LEFT, padx=5)

        animate_btn = Button(button_frame1, text="逐步构建", **button_style,
                            bg="#4299E1", fg="white", activebackground="#3182CE",
                            command=self.start_animated_build)
        animate_btn.pack(side=LEFT, padx=5)

        clear_btn = Button(button_frame1, text="清空画布", **button_style,
                          bg="#ED8936", fg="white", activebackground="#DD6B20",
                          command=self.clear_canvas)
        clear_btn.pack(side=LEFT, padx=5)

        back_btn = Button(button_frame1, text="返回主界面", **button_style,
                         bg="#718096", fg="white", activebackground="#4A5568",
                         command=self.back_to_main)
        back_btn.pack(side=LEFT, padx=5)

        # 第二行按钮
        save_btn = Button(button_frame2, text="保存树", **button_style,
                          bg="#6C9EFF", fg="white", activebackground="#4C6EF5",
                          command=self.save_tree)
        save_btn.pack(side=LEFT, padx=5)

        load_btn = Button(button_frame2, text="打开树", **button_style,
                          bg="#6C9EFF", fg="white", activebackground="#4C6EF5",
                          command=self.load_tree)
        load_btn.pack(side=LEFT, padx=5)
        
        dsl_help_btn = Button(button_frame2, text="DSL帮助", **button_style,
                         bg="#9F7AEA", fg="white", activebackground="#805AD5",
                         command=self.show_dsl_help)
        dsl_help_btn.pack(side=LEFT, padx=5)

        # 提示信息
        hint_label = Label(main_control_frame, 
                          text="提示: 使用逗号或空格分隔节点，#表示空节点。按 Enter 可执行 DSL（如：create 1 # 2 3 # 3 4 5 / clear / animate ...）",
                          font=("Segoe UI", 9), bg="#F3F6FB", fg="#718096", wraplength=900, justify=LEFT)
        hint_label.pack(pady=(5, 0))

    def _ensure_tree_folder(self) -> str:
        if hasattr(storage, "ensure_save_subdir"):
            return storage.ensure_save_subdir("tree")
        base_dir = os.path.dirname(os.path.abspath(storage.__file__))
        default_dir = os.path.join(base_dir, "save", "tree")
        os.makedirs(default_dir, exist_ok=True)
        return default_dir

    def save_tree(self):
        default_dir = self._ensure_tree_folder()
        default_name = f"tree_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = filedialog.asksaveasfilename(
            initialdir=default_dir,
            initialfile=default_name,
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="保存树到文件"
        )
        if not filepath:  # 用户取消了保存
            return
            
        tree_dict = storage.tree_to_dict(self.root_node) if hasattr(storage, "tree_to_dict") else {}
        metadata = {
            "saved_at": datetime.now().isoformat(),
            "node_count": len(tree_dict.get("nodes", [])) if isinstance(tree_dict, dict) else 0
        }
        payload = {"type": "tree", "tree": tree_dict, "metadata": metadata}
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        messagebox.showinfo("成功", f"二叉树已保存到：\n{filepath}")
        self.update_status("保存成功", "#48BB78")

    def load_tree(self):
        default_dir = self._ensure_tree_folder()
        filepath = filedialog.askopenfilename(
            initialdir=default_dir,
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="从文件加载二叉树"
        )
        if not filepath:  # 用户取消了加载
            return
            
        with open(filepath, "r", encoding="utf-8") as f:
            obj = json.load(f)
        tree_dict = obj.get("tree", {})
        new_root = storage.tree_dict_to_nodes(tree_dict, TreeNode)
        self.root_node = new_root
        self.redraw_tree()
        messagebox.showinfo("成功", "二叉树已成功加载并恢复")
        self.update_status("加载成功", "#48BB78")

    def draw_instructions(self):
        self.canvas.delete("instr")
        self.canvas.create_line(30, 42, self.canvas_width-30, 42, fill="#EEF2F7", width=1, tags=("instr",))
        self.canvas.create_text(30, 20,
                               text="显示规则：每个节点分为3格 [left | value | right]，左右指针连接到子节点或指向NULL",
                               anchor="w", font=("Segoe UI", 10), fill="#4A5568", tags=("instr",))
        if self.status_text_id:
            self.canvas.delete(self.status_text_id)
        self.status_text_id = self.canvas.create_text(
            self.canvas_width - 30, 20, text="就绪", anchor="ne",
            font=("Segoe UI", 11, "bold"), fill="#4299E1", tags=("instr",)
        )

    def update_status(self, text: str, color: str = "#4299E1"):
        if not self.status_text_id:
            self.status_text_id = self.canvas.create_text(
                self.canvas_width - 15, 15, text=text, anchor="ne",
                font=("Segoe UI", 11, "bold"), fill=color, tags=("instr",)
            )
        else:
            self.canvas.itemconfig(self.status_text_id, text=text, fill=color)

    def build_tree_from_input(self):
        text = self.input_var.get().strip()
        if not text:
            messagebox.showinfo("提示", "请输入层序序列，例如：1,2,3,#,4,#,5")
            return
        # 支持逗号或空格分隔
        parts = [p.strip() for p in re.split(r'[\s,]+', text) if p.strip() != ""]
        root, _ = BinaryTreeModel.build_from_level_order(parts)
        self.root_node = root
        self.redraw_tree()
        self.update_status("构建完成", "#48BB78")

    def clear_canvas(self):
        if self.animating:
            self.update_status("正在动画中，请稍后...", "#E53E3E")
            return
        self.canvas.delete("all")
        self.node_items.clear()
        self.node_to_rect.clear()
        self.root_node = None
        self.draw_decorations()
        self.draw_instructions()
        self.update_status("已清空画布", "#4299E1")

    def redraw_tree(self):
        self.canvas.delete("all")
        self.node_items.clear()
        self.node_to_rect.clear()
        self.draw_decorations()
        self.draw_instructions()
        if not self.root_node:
            self.canvas.create_text(self.canvas_width/2, self.canvas_height/2,
                                   text="空树", font=("Segoe UI", 16), fill="#A0AEC0")
            return
        initial_offset = self.canvas_width / 4
        start_y = 80
        self._draw_node(self.root_node, self.canvas_width/2, start_y, initial_offset)

    # 坐标计算
    def compute_positions(self, root: Optional[TreeNode]) -> Dict[TreeNode, Tuple[float,float]]:
        pos: Dict[TreeNode, Tuple[float,float]] = {}
        if not root:
            return pos
        initial_offset = self.canvas_width / 4
        start_y = 80

        def _rec(node: TreeNode, cx: float, cy: float, offset: float):
            pos[node] = (cx, cy)
            child_y = cy + self.level_gap
            child_offset = max(offset/2, 20)
            if node.left:
                _rec(node.left, cx - offset, child_y, child_offset)
            if node.right:
                _rec(node.right, cx + offset, child_y, child_offset)
        _rec(root, self.canvas_width/2, start_y, initial_offset)
        return pos

    def start_animated_build(self):
        if self.animating:
            self.update_status("已有动画在进行中", "#E53E3E")
            return
        text = self.input_var.get().strip()
        if not text:
            messagebox.showinfo("提示", "请输入层序序列，例如：1,2,3,#,4,#,5")
            return
        parts = [p.strip() for p in re.split(r'[\s,]+', text) if p.strip() != ""]
        if not parts:
            return
        max_nodes = 255
        if len(parts) > max_nodes:
            if not messagebox.askyesno("警告", f"输入节点过多（{len(parts)}），可能导致绘制重叠或卡顿，是否继续？"):
                return
        self.batch_queue = parts
        self.animating = True
        self.update_status("开始动画构建...", "#4299E1")
        self._animated_step(0)

    def _animated_step(self, idx: int):
        if idx >= len(self.batch_queue):
            self.animating = False
            self.update_status("构建完成", "#48BB78")
            return
        parts_sofar = self.batch_queue[:idx+1]
        prev_parts = self.batch_queue[:idx]
        prev_root, prev_node_list = BinaryTreeModel.build_from_level_order(prev_parts)
        parent_node = None
        if idx > 0:
            parent_idx = (idx - 1) // 2
            if parent_idx < len(prev_node_list):
                parent_node = prev_node_list[parent_idx]
        self.root_node = prev_root
        self.redraw_tree()
        self.update_status(f"插入中: {self.batch_queue[idx]} (位置: {idx})", "#4299E1")

        if parent_node and parent_node in self.node_to_rect:
            rect_id = self.node_to_rect[parent_node]
            try:
                self.canvas.itemconfig(rect_id, fill="#FEFCBF", outline="#D69E2E", width=2)
            except Exception:
                pass
        if parts_sofar[-1] == "#" or parts_sofar[-1] == "" :
            temp_root, _ = BinaryTreeModel.build_from_level_order(parts_sofar)
            def after_delay():
                self.root_node = temp_root
                self.redraw_tree()
                self.window.after(350, lambda: self._animated_step(idx+1))
            self.window.after(500, after_delay)
            return

        temp_root, node_list = BinaryTreeModel.build_from_level_order(parts_sofar)
        target_item = node_list[-1] if node_list else None
        # 计算目标坐标
        pos_map = self.compute_positions(temp_root)
        if target_item not in pos_map:
            self.root_node = temp_root
            self.redraw_tree()
            self.window.after(300, lambda: self._animated_step(idx+1))
            return
        target_cx, target_cy = pos_map[target_item]
        start_cx = self.canvas_width / 2
        start_cy = 30
        left = start_cx - self.node_w/2
        top = start_cy - self.node_h/2
        right = start_cx + self.node_w/2
        bottom = start_cy + self.node_h/2

        # 添加阴影效果
        shadow_offset = 2
        shadow_rect = self.canvas.create_rectangle(
            left+shadow_offset, top+shadow_offset,
            right+shadow_offset, bottom+shadow_offset,
            fill="#E2E8F0", outline=""
        )
        temp_rect = self.canvas.create_rectangle(
            left, top, right, bottom,
            fill="#C6F6D5", outline="#38A169", width=2
        )
        x1 = left + self.left_cell_w
        x2 = x1 + self.center_cell_w
        temp_text = self.canvas.create_text(
            (x1 + x2)/2, (top + bottom)/2,
            text=str(target_item.val),
            font=("Segoe UI", 12, "bold"),
            fill="#22543D"
        )

        # 动画移动到目标位置
        steps = 30
        dx = (target_cx - start_cx) / steps
        dy = (target_cy - start_cy) / steps
        delay = 12

        def step(i=0):
            if i < steps:
                self.canvas.move(shadow_rect, dx, dy)
                self.canvas.move(temp_rect, dx, dy)
                self.canvas.move(temp_text, dx, dy)
                self.window.after(delay, lambda: step(i+1))
            else:
                try:
                    self.canvas.delete(shadow_rect)
                    self.canvas.delete(temp_rect)
                    self.canvas.delete(temp_text)
                except Exception:
                    pass
                self.root_node = temp_root
                self.redraw_tree()
                # 高亮父节点在新的绘制中继续显示一段时间（若存在）
                if idx > 0:
                    parent_idx = (idx - 1) // 2
                    # 通过 node_list 找父节点实例（注意：新的树用的是 temp_root 的节点）
                    if parent_idx < len(node_list):
                        new_parent = node_list[parent_idx]
                        if new_parent and new_parent in self.node_to_rect:
                            try:
                                self.canvas.itemconfig(
                                    self.node_to_rect[new_parent],
                                    fill="#FEFCBF", outline="#D69E2E", width=2
                                )
                            except Exception:
                                pass
                # 等短时间后继续下一步
                self.window.after(400, lambda: self._animated_step(idx+1))

        step()

    # 绘制单节点
    def _draw_node(self, node: TreeNode, cx: float, cy: float, offset: float):
        left = cx - self.node_w/2
        top = cy - self.node_h/2
        right = cx + self.node_w/2
        bottom = cy + self.node_h/2

        # 添加阴影效果（单个节点）
        shadow_offset = 3
        shadow_rect = self.canvas.create_rectangle(
            left+shadow_offset, top+shadow_offset,
            right+shadow_offset, bottom+shadow_offset,
            fill="#E9F3FF", outline=""
        )

        rect = self.canvas.create_rectangle(
            left, top, right, bottom,
            fill="#FFF", outline="#C6E4FF", width=2
        )
        # 记录映射（TreeNode -> rect id）
        self.node_to_rect[node] = rect
        self.node_items.append(rect)
        self.node_items.append(shadow_rect)

        # 分割竖线
        x1 = left + self.left_cell_w
        x2 = x1 + self.center_cell_w
        v1 = self.canvas.create_line(x1, top, x1, bottom, width=1, fill="#EDF2F7")
        v2 = self.canvas.create_line(x2, top, x2, bottom, width=1, fill="#EDF2F7")
        self.node_items += [v1, v2]

        # 中间值
        self.canvas.create_text(
            (x1 + x2)/2, (top + bottom)/2,
            text=str(node.val),
            font=("Segoe UI", 12, "bold"),
            fill="#1F2937"
        )

        left_center_x = left + self.left_cell_w/2
        right_center_x = x2 + self.right_cell_w/2

        child_y = cy + self.level_gap
        child_offset = max(offset/2, 20)

        # 左子节点或 NULL
        if node.left:
            child_x = cx - offset
            self._draw_line_from_cell_to_child(left_center_x, bottom, child_x, child_y - self.node_h/2)
            self._draw_node(node.left, child_x, child_y, child_offset)
        else:
            null_x = cx - offset
            null_y = child_y
            rect_null = self.canvas.create_rectangle(
                null_x - 28, null_y - 14, null_x + 28, null_y + 14,
                fill="#FFF5F5", outline="#FED7D7", width=1
            )
            text_null = self.canvas.create_text(
                null_x, null_y, text="NULL",
                font=("Segoe UI", 9, "bold"), fill="#C53030"
            )
            self.node_items += [rect_null, text_null]
            self._draw_line_from_cell_to_child(left_center_x, bottom, null_x, null_y - 14)

        # 右子节点或 NULL
        if node.right:
            child_x = cx + offset
            self._draw_line_from_cell_to_child(right_center_x, bottom, child_x, child_y - self.node_h/2)
            self._draw_node(node.right, child_x, child_y, child_offset)
        else:
            null_x = cx + offset
            null_y = child_y
            rect_null = self.canvas.create_rectangle(
                null_x - 28, null_y - 14, null_x + 28, null_y + 14,
                fill="#FFF5F5", outline="#FED7D7", width=1
            )
            text_null = self.canvas.create_text(
                null_x, null_y, text="NULL",
                font=("Segoe UI", 9, "bold"), fill="#C53030"
            )
            self.node_items += [rect_null, text_null]
            self._draw_line_from_cell_to_child(right_center_x, bottom, null_x, null_y - 14)

    def _draw_line_from_cell_to_child(self, sx, sy, ex, ey):
        mid_y = sy + 10
        line1 = self.canvas.create_line(sx, sy, sx, mid_y, width=2, fill="#667085")
        line2 = self.canvas.create_line(sx, mid_y, ex, ey, arrow=LAST, width=2, fill="#667085")
        self.node_items += [line1, line2]

    def back_to_main(self):
        if self.animating:
            messagebox.showinfo("提示", "正在动画构建，无法返回")
            return
        self.window.destroy()

    # ----------------------------
    # DSL 历史记录功能
    # ----------------------------
    def add_to_history(self, command: str):
        """添加命令到历史记录"""
        if command and (not self.dsl_history or self.dsl_history[-1] != command):
            self.dsl_history.append(command)
            self.history_index = len(self.dsl_history)

    def show_prev_history(self, event=None):
        """显示上一条历史命令"""
        if not self.dsl_history:
            return
        if self.history_index > 0:
            self.history_index -= 1
            self.dsl_var.set(self.dsl_history[self.history_index])

    def show_next_history(self, event=None):
        """显示下一条历史命令"""
        if not self.dsl_history:
            return
        if self.history_index < len(self.dsl_history) - 1:
            self.history_index += 1
            self.dsl_var.set(self.dsl_history[self.history_index])
        else:
            self.history_index = len(self.dsl_history)
            self.dsl_var.set("")

    # ----------------------------
    # 简化的 DSL 支持
    # ----------------------------
    def show_dsl_help(self):
        """显示DSL帮助信息"""
        help_text = """
DSL (Domain Specific Language) 命令帮助：

基础命令：
  create <序列>    - 逐步动画按层序构建树
  build <序列>     - 一步构建树
  animate <序列>   - 逐步动画构建树

遍历命令：
  preorder         - 显示前序遍历结果
  inorder          - 显示中序遍历结果  
  postorder        - 显示后序遍历结果
  levelorder       - 显示层序遍历结果

实用命令：
  clear / reset    - 清空画布
  height           - 计算并显示树的高度
  count            - 计算并显示节点数量

说明：
  - 序列支持用逗号或空格分隔节点，使用 '#' 表示空节点
  - 按上下箭头键可浏览命令历史记录
        """
        messagebox.showinfo("DSL 命令帮助", help_text)

    def process_dsl(self, event=None):
        raw = (self.dsl_var.get() or "").strip()  # 改为使用dsl_var
        if not raw:
            return
        
        # 添加到历史记录
        self.add_to_history(raw)
        
        # 将命令拆分：允许用空格或逗号分隔节点，命令与其参数也可用空格分隔
        parts = [p for p in re.split(r'[\s,]+', raw) if p != ""]
        if not parts:
            return
        cmd = parts[0].lower()
        args = parts[1:]

        try:
            # 🌳 树构建命令
            if cmd in ("create", "animate"):
                if not args:
                    messagebox.showinfo("用法", "示例: create 1 # 2 3 # 3 4 5 （用空格或逗号分隔，# 表示空）")
                    return
                seq_text = " ".join(args)
                self.input_var.set(seq_text)  # 设置到层序序列输入框
                self.start_animated_build()
                
            elif cmd == "build":
                if not args:
                    messagebox.showinfo("用法", "示例: build 1 # 2 3 # 3 4 5")
                    return
                seq_text = " ".join(args)
                self.input_var.set(seq_text)  # 设置到层序序列输入框
                self.build_tree_from_input()

            # 📊 遍历命令
            elif cmd == "preorder":
                self.show_traversal("preorder")
            elif cmd == "inorder":
                self.show_traversal("inorder")
            elif cmd == "postorder":
                self.show_traversal("postorder")
            elif cmd == "levelorder":
                self.show_traversal("levelorder")

            # 🎨 显示控制命令
            elif cmd in ("clear", "reset"):
                self.clear_canvas()
                self.update_status("DSL: clear 执行完成", "#4299E1")
                
            elif cmd == "height":
                self.show_tree_height()
                
            elif cmd == "count":
                self.show_node_count()

            # ❓ 帮助命令
            elif cmd in ("help", "?"):
                self.show_dsl_help()
                
            elif cmd == "history":
                self.show_command_history()

            else:
                messagebox.showinfo("未识别命令", f"未知命令: {cmd}\n输入 'help' 查看可用命令")

        except Exception as e:
            messagebox.showerror("DSL 执行错误", f"命令执行失败: {e}")
            self.update_status("DSL 错误", "#E53E3E")

    # ----------------------------
    # DSL 命令的具体实现
    # ----------------------------
    
    def show_tree_height(self):
        """显示树的高度"""
        height = self._get_tree_height(self.root_node)
        messagebox.showinfo("树高度", f"树的高度为: {height}")
        self.update_status(f"树高度: {height}", "#4299E1")

    def _get_tree_height(self, node: TreeNode) -> int:
        """计算树高度"""
        if not node:
            return 0
        return 1 + max(self._get_tree_height(node.left), 
                      self._get_tree_height(node.right))

    def show_node_count(self):
        """显示节点数量"""
        count = self._count_nodes(self.root_node)
        messagebox.showinfo("节点计数", f"节点总数为: {count}")
        self.update_status(f"节点数: {count}", "#4299E1")

    def _count_nodes(self, node: TreeNode) -> int:
        """计算节点数量"""
        if not node:
            return 0
        return 1 + self._count_nodes(node.left) + self._count_nodes(node.right)

    def show_traversal(self, traversal_type: str):
        """显示遍历结果"""
        if not self.root_node:
            messagebox.showinfo("遍历", "树为空")
            return
            
        result = []
        if traversal_type == "preorder":
            self._preorder_traversal(self.root_node, result)
        elif traversal_type == "inorder":
            self._inorder_traversal(self.root_node, result)
        elif traversal_type == "postorder":
            self._postorder_traversal(self.root_node, result)
        elif traversal_type == "levelorder":
            result = self._levelorder_traversal(self.root_node)
            
        result_str = " ".join(map(str, result))
        messagebox.showinfo(f"{traversal_type}遍历", f"遍历结果:\n{result_str}")
        self.update_status(f"{traversal_type}遍历完成", "#4299E1")

    def _preorder_traversal(self, node: TreeNode, result: List):
        if node:
            result.append(node.val)
            self._preorder_traversal(node.left, result)
            self._preorder_traversal(node.right, result)

    def _inorder_traversal(self, node: TreeNode, result: List):
        if node:
            self._inorder_traversal(node.left, result)
            result.append(node.val)
            self._inorder_traversal(node.right, result)

    def _postorder_traversal(self, node: TreeNode, result: List):
        if node:
            self._postorder_traversal(node.left, result)
            self._postorder_traversal(node.right, result)
            result.append(node.val)

    def _levelorder_traversal(self, node: TreeNode) -> List:
        if not node:
            return []
        result = []
        queue = [node]
        while queue:
            current = queue.pop(0)
            result.append(current.val)
            if current.left:
                queue.append(current.left)
            if current.right:
                queue.append(current.right)
        return result

    def show_command_history(self):
        """显示命令历史记录"""
        if not self.dsl_history:
            messagebox.showinfo("命令历史", "历史记录为空")
            return
            
        history_text = "\n".join([f"{i+1}. {cmd}" for i, cmd in enumerate(self.dsl_history[-10:])])
        messagebox.showinfo("命令历史 (最近10条)", history_text)


if __name__ == '__main__':
    window = Tk()
    window.title("二叉树可视化工具")
    window.geometry("1350x800")  # 增加窗口高度
    window.configure(bg="#F3F6FA")
    BinaryTreeVisualizer(window)
    window.mainloop()