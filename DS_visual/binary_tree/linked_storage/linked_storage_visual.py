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
import time

class BinaryTreeVisualizer:
    def __init__(self, root):
        self.window = root
        self.window.config(bg="#F3F6FA")
        self.window.title("二叉树可视化工具")
        
        # 伪代码相关变量（需要在创建面板前初始化）
        self.pseudo_code_lines = []
        self.current_highlight_line = -1
        self.animation_speed = 0.03
        
        # 创建主内容区域（画布 + 伪代码面板）
        main_content = Frame(self.window, bg="#F3F6FA")
        main_content.pack(fill=BOTH, expand=True, padx=10, pady=5)
        
        # 左侧画布容器 - 支持滚动
        canvas_container = Frame(main_content, bg="#F3F6FA")
        canvas_container.pack(side=LEFT, fill=BOTH, expand=True)
        
        self.canvas_width = 980
        self.canvas_height = 450
        self.canvas_scroll_width = 2000  # 滚动区域宽度
        self.canvas_scroll_height = 1200  # 滚动区域高度
        
        # 创建带滚动条的画布
        self.canvas_frame = Frame(canvas_container, bg="#F3F6FA")
        self.canvas_frame.pack(fill=BOTH, expand=True, pady=(5, 0))
        
        # 垂直滚动条
        self.v_scrollbar = Scrollbar(self.canvas_frame, orient=VERTICAL)
        self.v_scrollbar.pack(side=RIGHT, fill=Y)
        
        # 水平滚动条
        self.h_scrollbar = Scrollbar(self.canvas_frame, orient=HORIZONTAL)
        self.h_scrollbar.pack(side=BOTTOM, fill=X)
        
        self.canvas = Canvas(self.canvas_frame, bg="#F3F6FA", width=self.canvas_width, height=self.canvas_height,
                             relief=FLAT, bd=0, highlightthickness=0,
                             xscrollcommand=self.h_scrollbar.set,
                             yscrollcommand=self.v_scrollbar.set)
        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)
        
        # 配置滚动条
        self.v_scrollbar.config(command=self.canvas.yview)
        self.h_scrollbar.config(command=self.canvas.xview)
        
        # 绑定鼠标滚轮事件
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Shift-MouseWheel>", self._on_shift_mousewheel)
        
        # 设置初始滚动区域
        self.canvas.config(scrollregion=(0, 0, self.canvas_scroll_width, self.canvas_scroll_height))
        
        # 右侧伪代码面板
        self.create_pseudo_code_panel(main_content)
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
        self.dsl_var = StringVar()
        self.batch_queue: List[str] = []
        self.animating = False
        self.status_text_id: Optional[int] = None
        self.dsl_history: List[str] = []
        self.history_index = -1
        
        # 遍历动画相关
        self.traversal_animating = False
        self.traversal_highlights: List[int] = []
        
        self.create_controls()
        self.draw_decorations()
        self.draw_instructions()
    
    def create_pseudo_code_panel(self, parent):
        """创建伪代码显示面板（固定在右侧）"""
        pseudo_frame = Frame(parent, bg="#2d3436", relief=RAISED, bd=2, width=300)
        pseudo_frame.pack(side=RIGHT, fill=Y, padx=(8, 0))
        pseudo_frame.pack_propagate(False)
        
        # 标题
        title_label = Label(pseudo_frame, text="📋 伪代码执行过程", 
                           font=("微软雅黑", 12, "bold"), 
                           bg="#2d3436", fg="#00cec9", pady=5)
        title_label.pack(fill=X)
        
        # 分隔线
        separator = Frame(pseudo_frame, height=2, bg="#00cec9")
        separator.pack(fill=X, padx=10, pady=(0, 3))
        
        # 当前操作标签
        self.operation_label = Label(pseudo_frame, text="等待操作...", 
                                     font=("微软雅黑", 10), 
                                     bg="#2d3436", fg="#dfe6e9", 
                                     wraplength=280, justify=LEFT)
        self.operation_label.pack(fill=X, padx=10, pady=3)
        
        # 伪代码显示区域
        code_container = Frame(pseudo_frame, bg="#1e272e")
        code_container.pack(fill=BOTH, expand=True, padx=8, pady=5)
        
        self.pseudo_text = Text(code_container, 
                               font=("Consolas", 10), 
                               bg="#1e272e", fg="#b2bec3",
                               relief=FLAT, 
                               wrap=WORD,
                               padx=8, pady=8,
                               cursor="arrow",
                               state=DISABLED,
                               height=16,
                               width=32)
        self.pseudo_text.pack(fill=BOTH, expand=True)
        
        # 配置高亮标签样式
        self.pseudo_text.tag_configure("highlight", 
                                       background="#00b894", 
                                       foreground="#ffffff",
                                       font=("Consolas", 10, "bold"))
        self.pseudo_text.tag_configure("executed", 
                                       foreground="#55efc4")
        self.pseudo_text.tag_configure("pending", 
                                       foreground="#636e72")
        
        # 进度指示器
        progress_frame = Frame(pseudo_frame, bg="#2d3436")
        progress_frame.pack(fill=X, padx=10, pady=(0, 5))
        
        self.progress_label = Label(progress_frame, text="步骤: 0/0", 
                                    font=("Arial", 9), 
                                    bg="#2d3436", fg="#b2bec3")
        self.progress_label.pack(side=LEFT)
        
        self.status_indicator = Label(progress_frame, text="⚫ 空闲", 
                                      font=("Arial", 9), 
                                      bg="#2d3436", fg="#b2bec3")
        self.status_indicator.pack(side=RIGHT)
        
        # 速度控制
        control_separator = Frame(pseudo_frame, height=1, bg="#636e72")
        control_separator.pack(fill=X, padx=10, pady=5)
        
        speed_frame = Frame(pseudo_frame, bg="#2d3436")
        speed_frame.pack(fill=X, padx=10, pady=2)
        
        speed_label = Label(speed_frame, text="动画速度:", font=("Arial", 9), 
                           bg="#2d3436", fg="#dfe6e9")
        speed_label.pack(side=LEFT)
        
        self.speed_var = DoubleVar(value=self.animation_speed)
        speed_scale = Scale(speed_frame, from_=0.01, to=0.1, resolution=0.01, 
                           orient=HORIZONTAL, variable=self.speed_var,
                           command=self._update_speed, length=140,
                           bg="#2d3436", fg="#dfe6e9", highlightthickness=0,
                           troughcolor="#1e272e", activebackground="#00b894")
        speed_scale.pack(side=RIGHT, padx=5)
    
    def _update_speed(self, value):
        """更新动画速度"""
        self.animation_speed = float(value)
    
    def set_pseudo_code(self, title, lines):
        """设置要显示的伪代码"""
        self.pseudo_code_lines = lines
        self.current_highlight_line = -1
        
        self.operation_label.config(text=title, fg="#74b9ff")
        self.status_indicator.config(text="🟢 执行中", fg="#00b894")
        
        self.pseudo_text.config(state=NORMAL)
        self.pseudo_text.delete(1.0, END)
        
        for i, line in enumerate(lines):
            line_text = str(line) if not isinstance(line, dict) else line.get("text", "")
            line_num = f"{i+1:2}. "
            self.pseudo_text.insert(END, line_num, "pending")
            self.pseudo_text.insert(END, line_text + "\n", "pending")
        
        self.pseudo_text.config(state=DISABLED)
        self.progress_label.config(text=f"步骤: 0/{len(lines)}")
        self.window.update()
    
    def highlight_pseudo_line(self, line_index, delay=True):
        """高亮指定行的伪代码"""
        if not self.pseudo_code_lines or line_index < 0 or line_index >= len(self.pseudo_code_lines):
            return
        
        self.pseudo_text.config(state=NORMAL)
        
        for i in range(len(self.pseudo_code_lines)):
            start_pos = f"{i+1}.0"
            end_pos = f"{i+1}.end"
            self.pseudo_text.tag_remove("highlight", start_pos, end_pos)
            self.pseudo_text.tag_remove("pending", start_pos, end_pos)
            self.pseudo_text.tag_remove("executed", start_pos, end_pos)
            
            if i < line_index:
                self.pseudo_text.tag_add("executed", start_pos, end_pos)
            elif i == line_index:
                self.pseudo_text.tag_add("highlight", start_pos, end_pos)
            else:
                self.pseudo_text.tag_add("pending", start_pos, end_pos)
        
        self.pseudo_text.config(state=DISABLED)
        self.pseudo_text.see(f"{line_index+1}.0")
        
        self.current_highlight_line = line_index
        self.progress_label.config(text=f"步骤: {line_index+1}/{len(self.pseudo_code_lines)}")
        self.window.update()
        
        if delay:
            time.sleep(self.animation_speed * 3)
    
    def complete_pseudo_code(self):
        """标记伪代码执行完成"""
        self.pseudo_text.config(state=NORMAL)
        
        for i in range(len(self.pseudo_code_lines)):
            start_pos = f"{i+1}.0"
            end_pos = f"{i+1}.end"
            self.pseudo_text.tag_remove("highlight", start_pos, end_pos)
            self.pseudo_text.tag_remove("pending", start_pos, end_pos)
            self.pseudo_text.tag_add("executed", start_pos, end_pos)
        
        self.pseudo_text.config(state=DISABLED)
        self.status_indicator.config(text="✅ 完成", fg="#55efc4")
        self.progress_label.config(text=f"步骤: {len(self.pseudo_code_lines)}/{len(self.pseudo_code_lines)}")
        self.window.update()
    
    def clear_pseudo_code(self):
        """清除伪代码显示"""
        self.pseudo_code_lines = []
        self.current_highlight_line = -1
        
        self.operation_label.config(text="等待操作...", fg="#dfe6e9")
        self.status_indicator.config(text="⚫ 空闲", fg="#b2bec3")
        self.progress_label.config(text="步骤: 0/0")
        
        self.pseudo_text.config(state=NORMAL)
        self.pseudo_text.delete(1.0, END)
        self.pseudo_text.config(state=DISABLED)
        self.window.update()

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
        
        # 获取当前滚动区域尺寸
        scroll_region = self.canvas.cget('scrollregion')
        if scroll_region:
            parts = scroll_region.split()
            if len(parts) == 4:
                scroll_width = float(parts[2])
                scroll_height = float(parts[3])
            else:
                scroll_width = self.canvas_scroll_width
                scroll_height = self.canvas_scroll_height
        else:
            scroll_width = self.canvas_scroll_width
            scroll_height = self.canvas_scroll_height
        
        cx1, cy1 = 12, 12
        cx2, cy2 = scroll_width - 12, scroll_height - 12
        
        # 绘制背景卡片
        shadow_ids = []
        for i, off in enumerate((6,4,2)):
            alpha_fill = "#E6EDF6" if i == 0 else "#EEF6F9"
            sid = self.canvas.create_rectangle(cx1+off, cy1+off, cx2+off, cy2+off, fill=alpha_fill, outline="", tags=("decor",))
            shadow_ids.append(sid)
        card_ids = self.draw_rounded_rect(cx1, cy1, cx2, cy2, r=14, fill="#FFFFFF", outline="", tags=None)
        for _id in card_ids:
            self.canvas.addtag_withtag("decor", _id)
        
        # 左上角装饰
        dot1 = self.canvas.create_oval(cx1+18, cy1+18, cx1+58, cy1+58, fill="#E6F2FF", outline="", tags=("decor",))
        
        # 右上角装饰
        arc = self.canvas.create_oval(cx2-120, cy1-40, cx2+40, cy1+120, fill="#F0FAF4", outline="", tags=("decor",))
        
        # 右下角装饰
        for i in range(3):
            r = 40 + i*18
            col = "#F3F8F6" if i % 2 == 0 else "#EEF8FF"
            c = self.canvas.create_oval(cx2 - r - 20, cy2 - r - 20, cx2 + r - 20, cy2 + r - 20, fill=col, outline="", tags=("decor",))
        
        # 网格线（限制绘制数量避免性能问题）
        step = 80
        max_lines = 30
        line_count = 0
        for x in range(int(cx1)+step, int(cx2), step):
            if line_count >= max_lines:
                break
            self.canvas.create_line(x, cy1+20, x, min(cy2-20, cy1 + 800), fill="#F4F7FA", dash=(2,6), tags=("decor",))
            line_count += 1
        
        line_count = 0
        for y in range(int(cy1)+step, int(cy2), step):
            if line_count >= max_lines:
                break
            self.canvas.create_line(cx1+20, y, min(cx2-20, cx1 + 1200), y, fill="#F8FAFC", dash=(2,6), tags=("decor",))
            line_count += 1
        
        self.canvas.tag_lower("decor")

    def create_controls(self):
        main_control_frame = Frame(self.window, bg="#F3F6FB")
        main_control_frame.pack(fill=X, padx=15, pady=10)
        
        title_label = Label(main_control_frame, text="二叉树可视化工具", font=("Segoe UI", 16, "bold"),
                          bg="#F3F6FB", fg="#2D3748")
        title_label.pack(pady=(0, 10))
        
        input_frame = Frame(main_control_frame, bg="#F3F6FB")
        input_frame.pack(fill=X, pady=5)
        
        level_order_label = Label(input_frame, text="层序序列:", font=("Segoe UI", 11),
                                 bg="#F3F6FB", fg="#4A5568")
        level_order_label.grid(row=0, column=0, sticky=W, padx=(0, 10))
        
        level_order_entry = Entry(input_frame, textvariable=self.input_var, width=50, font=("Segoe UI", 11),
                                 relief=SOLID, bd=1, highlightthickness=1, highlightcolor="#4299E1",
                                 highlightbackground="#CBD5E0")
        level_order_entry.grid(row=0, column=1, sticky=EW, padx=(0, 20))
        level_order_entry.insert(0, "1,2,3,#,4,#,5")
        level_order_entry.bind("<Return>", lambda e: self.build_tree_from_input())
        
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
        
        input_frame.columnconfigure(1, weight=1)
        input_frame.columnconfigure(3, weight=1)
        
        button_frame1 = Frame(main_control_frame, bg="#F3F6FB")
        button_frame1.pack(fill=X, pady=5)
        
        button_frame2 = Frame(main_control_frame, bg="#F3F6FB")
        button_frame2.pack(fill=X, pady=5)

        button_style = {"font": ("Segoe UI", 10), "width": 12, "height": 1,
                       "relief": FLAT, "bd": 0, "cursor": "hand2"}

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

        save_btn = Button(button_frame2, text="保存树", **button_style,
                          bg="#6C9EFF", fg="white", activebackground="#4C6EF5",
                          command=self.save_tree)
        save_btn.pack(side=LEFT, padx=5)

        load_btn = Button(button_frame2, text="打开树", **button_style,
                          bg="#6C9EFF", fg="white", activebackground="#4C6EF5",
                          command=self.load_tree)
        load_btn.pack(side=LEFT, padx=5)
        
        # 操作按钮行
        button_frame3 = Frame(main_control_frame, bg="#F3F6FB")
        button_frame3.pack(fill=X, pady=5)

        # 查找、插入、删除按钮
        search_btn = Button(button_frame2, text="查找节点", **button_style,
                           bg="#3182CE", fg="white", activebackground="#2C5282",
                           command=self.start_search_animation)
        search_btn.pack(side=LEFT, padx=5)

        insert_btn = Button(button_frame2, text="插入节点", **button_style,
                           bg="#38A169", fg="white", activebackground="#276749",
                           command=self.start_insert_animation)
        insert_btn.pack(side=LEFT, padx=5)

        delete_btn = Button(button_frame2, text="删除节点", **button_style,
                           bg="#E53E3E", fg="white", activebackground="#C53030",
                           command=self.start_delete_animation)
        delete_btn.pack(side=LEFT, padx=5)

        # 遍历动画按钮
        preorder_btn = Button(button_frame3, text="前序遍历(动)", **button_style,
                              bg="#9F7AEA", fg="white", activebackground="#805AD5",
                              command=self.start_preorder_animation)
        preorder_btn.pack(side=LEFT, padx=5)

        inorder_btn = Button(button_frame3, text="中序遍历(动)", **button_style,
                             bg="#9F7AEA", fg="white", activebackground="#805AD5",
                             command=self.start_inorder_animation)
        inorder_btn.pack(side=LEFT, padx=5)

        postorder_btn = Button(button_frame3, text="后序遍历(动)", **button_style,
                               bg="#9F7AEA", fg="white", activebackground="#805AD5",
                               command=self.start_postorder_animation)
        postorder_btn.pack(side=LEFT, padx=5)
        
        dsl_help_btn = Button(button_frame3, text="DSL帮助", **button_style,
                         bg="#718096", fg="white", activebackground="#4A5568",
                         command=self.show_dsl_help)
        dsl_help_btn.pack(side=LEFT, padx=5)

        hint_label = Label(main_control_frame, 
                          text="提示: DSL命令示例 → create 1,2,3 | search 2 | insert 5 left 3 | delete 2 | preorder-anim。按 Enter 执行。",
                          font=("Segoe UI", 9), bg="#F3F6FB", fg="#718096", wraplength=1100, justify=LEFT)
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
        if not filepath:
            return
            
        tree_dict = storage.tree_to_dict(self.root_node) if hasattr(storage, "tree_to_dict") else {}
        metadata = {
            "saved_at": datetime.now().isoformat(),
            "node_count": len(tree_dict.get("nodes", [])) if isinstance(tree_dict, dict) else 0
        }
        payload = {"type": "tree", "tree": tree_dict, "metadata": metadata}
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        messagebox.showinfo("成功", f"二叉树已保存到:\n{filepath}")
        self.update_status("保存成功", "#48BB78")

    def load_tree(self):
        default_dir = self._ensure_tree_folder()
        filepath = filedialog.askopenfilename(
            initialdir=default_dir,
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="从文件加载二叉树"
        )
        if not filepath:
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
                               text="显示规则:每个节点分为3格 [left | value | right],左右指针连接到子节点或指向NULL",
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

    def _on_mousewheel(self, event):
        """垂直滚动（鼠标滚轮）"""
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_shift_mousewheel(self, event):
        """水平滚动（Shift + 鼠标滚轮）"""
        self.canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")

    def _get_tree_depth(self, node) -> int:
        """计算树的深度"""
        if not node:
            return 0
        return 1 + max(self._get_tree_depth(node.left), self._get_tree_depth(node.right))

    def _update_scroll_region(self):
        """根据树的深度动态更新滚动区域"""
        if not self.root_node:
            self.canvas.config(scrollregion=(0, 0, self.canvas_width, self.canvas_height))
            return
        
        depth = self._get_tree_depth(self.root_node)
        
        # 计算需要的高度: start_y + (depth-1) * level_gap + node_h + 额外空间(NULL节点)
        required_height = 80 + depth * self.level_gap + self.node_h + 100
        
        # 计算需要的宽度: 最底层可能有 2^(depth-1) 个节点
        # 每个节点宽度 node_w，加上间距
        max_nodes_bottom = 2 ** (depth - 1) if depth > 0 else 1
        required_width = max(self.canvas_width, max_nodes_bottom * (self.node_w + 40))
        
        # 更新滚动区域
        scroll_width = max(self.canvas_scroll_width, required_width)
        scroll_height = max(self.canvas_scroll_height, required_height)
        
        self.canvas.config(scrollregion=(0, 0, scroll_width, scroll_height))

    def _scroll_to_node(self, cx: float, cy: float):
        """自动滚动画布以显示指定位置的节点"""
        scroll_region = self.canvas.cget('scrollregion')
        if not scroll_region:
            return
        
        parts = scroll_region.split()
        if len(parts) != 4:
            return
        
        scroll_width = float(parts[2])
        scroll_height = float(parts[3])
        
        # 计算节点在滚动区域中的相对位置
        if scroll_width > 0 and scroll_height > 0:
            # 计算目标位置，使节点居中显示
            target_x = max(0, min(1, (cx - self.canvas_width / 2) / scroll_width))
            target_y = max(0, min(1, (cy - self.canvas_height / 2) / scroll_height))
            
            self.canvas.xview_moveto(target_x)
            self.canvas.yview_moveto(target_y)

    def _center_view_on_tree(self, tree_center_x: float, tree_top_y: float):
        """将视图居中到树的中心位置"""
        scroll_region = self.canvas.cget('scrollregion')
        if not scroll_region:
            return
        
        parts = scroll_region.split()
        if len(parts) != 4:
            return
        
        scroll_width = float(parts[2])
        scroll_height = float(parts[3])
        
        if scroll_width <= self.canvas_width:
            # 如果滚动区域宽度小于可见区域，不需要水平滚动
            target_x = 0
        else:
            # 计算使树居中的滚动位置
            # xview_moveto(x) 将滚动区域的 x*scroll_width 位置放在可见区域的左边缘
            # 目标：使 tree_center_x 位于可见区域的中心
            # 即：可见区域左边缘 = tree_center_x - canvas_width/2
            left_edge = tree_center_x - self.canvas_width / 2
            target_x = max(0, min(1, left_edge / scroll_width))
        
        # 垂直方向：保持顶部显示
        target_y = 0
        
        self.canvas.xview_moveto(target_x)
        self.canvas.yview_moveto(target_y)

    def build_tree_from_input(self):
        text = self.input_var.get().strip()
        if not text:
            messagebox.showinfo("提示", "请输入层序序列,例如:1,2,3,#,4,#,5")
            return
        parts = [p.strip() for p in re.split(r'[\s,]+', text) if p.strip() != ""]
        root, _ = BinaryTreeModel.build_from_level_order(parts)
        self.root_node = root
        self.redraw_tree()
        self.update_status("构建完成", "#48BB78")

    def clear_canvas(self):
        if self.animating or self.traversal_animating:
            self.update_status("正在动画中,请稍后...", "#E53E3E")
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
        
        # 先更新滚动区域
        self._update_scroll_region()
        
        self.draw_decorations()
        self.draw_instructions()
        if not self.root_node:
            self.canvas.create_text(self.canvas_width/2, self.canvas_height/2,
                                   text="空树", font=("Segoe UI", 16), fill="#A0AEC0")
            return
        
        # 根据树的深度动态计算参数
        depth = self._get_tree_depth(self.root_node)
        
        # 计算中心位置和初始偏移
        # 获取当前滚动区域
        scroll_region = self.canvas.cget('scrollregion')
        if scroll_region:
            parts = scroll_region.split()
            if len(parts) == 4:
                scroll_width = float(parts[2])
            else:
                scroll_width = self.canvas_scroll_width
        else:
            scroll_width = self.canvas_scroll_width
        
        center_x = scroll_width / 2
        
        # 根据深度调整初始偏移，确保节点不会重叠
        # 对于深层树，需要更大的初始偏移
        if depth <= 4:
            initial_offset = self.canvas_width / 4
        else:
            # 为深层树增加偏移量
            initial_offset = max(self.canvas_width / 4, (2 ** (depth - 2)) * (self.node_w / 2 + 10))
        
        start_y = 80
        self._draw_node(self.root_node, center_x, start_y, initial_offset)
        
        # 自动滚动使树居中显示
        self._center_view_on_tree(center_x, start_y)

    def compute_positions(self, root: Optional[TreeNode]) -> Dict[TreeNode, Tuple[float,float]]:
        pos: Dict[TreeNode, Tuple[float,float]] = {}
        if not root:
            return pos
        
        # 根据树的深度动态计算参数
        depth = self._get_tree_depth(root)
        
        # 获取当前滚动区域
        scroll_region = self.canvas.cget('scrollregion')
        if scroll_region:
            parts = scroll_region.split()
            if len(parts) == 4:
                scroll_width = float(parts[2])
            else:
                scroll_width = self.canvas_scroll_width
        else:
            scroll_width = self.canvas_scroll_width
        
        center_x = scroll_width / 2
        
        # 根据深度调整初始偏移
        if depth <= 4:
            initial_offset = self.canvas_width / 4
        else:
            initial_offset = max(self.canvas_width / 4, (2 ** (depth - 2)) * (self.node_w / 2 + 10))
        
        start_y = 80

        def _rec(node: TreeNode, cx: float, cy: float, offset: float):
            pos[node] = (cx, cy)
            child_y = cy + self.level_gap
            child_offset = max(offset/2, 20)
            if node.left:
                _rec(node.left, cx - offset, child_y, child_offset)
            if node.right:
                _rec(node.right, cx + offset, child_y, child_offset)
        _rec(root, center_x, start_y, initial_offset)
        return pos

    def start_animated_build(self):
        if self.animating:
            self.update_status("已有动画在进行中", "#E53E3E")
            return
        text = self.input_var.get().strip()
        if not text:
            messagebox.showinfo("提示", "请输入层序序列,例如:1,2,3,#,4,#,5")
            return
        parts = [p.strip() for p in re.split(r'[\s,]+', text) if p.strip() != ""]
        if not parts:
            return
        max_nodes = 255
        if len(parts) > max_nodes:
            if not messagebox.askyesno("警告", f"输入节点过多({len(parts)}),可能导致绘制重叠或卡顿,是否继续?"):
                return
        self.batch_queue = parts
        self.animating = True
        
        # 设置伪代码
        pseudo_lines = [
            f"// 层序构建二叉树 (共{len(parts)}个节点)",
            "queue = new Queue()",
            "root = new TreeNode(items[0])",
            "queue.enqueue(root)",
            "for i = 1 to n-1:",
            "    parent = queue.dequeue()",
            "    if items[i] != '#':",
            "        node = new TreeNode(items[i])",
            "        parent.left/right = node",
            "        queue.enqueue(node)",
            "return root"
        ]
        self.set_pseudo_code(f"层序构建二叉树", pseudo_lines)
        self.highlight_pseudo_line(0)
        self.highlight_pseudo_line(1)
        self.highlight_pseudo_line(2)
        self.highlight_pseudo_line(3)
        
        self.update_status("开始动画构建...", "#4299E1")
        self._animated_step(0)

    def _animated_step(self, idx: int):
        if idx >= len(self.batch_queue):
            self.animating = False
            self.highlight_pseudo_line(10)  # return root
            self.complete_pseudo_code()
            self.update_status("构建完成", "#48BB78")
            return
        
        # 高亮循环步骤
        self.highlight_pseudo_line(4, delay=False)  # for循环
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
        
        # 高亮dequeue操作
        self.highlight_pseudo_line(5, delay=False)
        
        if parts_sofar[-1] == "#" or parts_sofar[-1] == "" :
            temp_root, _ = BinaryTreeModel.build_from_level_order(parts_sofar)
            def after_delay():
                self.root_node = temp_root
                self.redraw_tree()
                self.window.after(350, lambda: self._animated_step(idx+1))
            self.window.after(500, after_delay)
            return
        
        # 高亮创建新节点
        self.highlight_pseudo_line(6, delay=False)
        self.highlight_pseudo_line(7, delay=False)

        temp_root, node_list = BinaryTreeModel.build_from_level_order(parts_sofar)
        target_item = node_list[-1] if node_list else None
        pos_map = self.compute_positions(temp_root)
        if target_item not in pos_map:
            self.root_node = temp_root
            self.redraw_tree()
            self.window.after(300, lambda: self._animated_step(idx+1))
            return
        target_cx, target_cy = pos_map[target_item]
        
        # 获取滚动区域中心作为起始位置
        scroll_region = self.canvas.cget('scrollregion')
        if scroll_region:
            parts_sr = scroll_region.split()
            if len(parts_sr) == 4:
                scroll_width = float(parts_sr[2])
                start_cx = scroll_width / 2
            else:
                start_cx = self.canvas_width / 2
        else:
            start_cx = self.canvas_width / 2
        start_cy = 30
        left = start_cx - self.node_w/2
        top = start_cy - self.node_h/2
        right = start_cx + self.node_w/2
        bottom = start_cy + self.node_h/2

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

        steps = 30
        dx = (target_cx - start_cx) / steps
        dy = (target_cy - start_cy) / steps
        delay = 12
        
        # 如果目标位置超出可见区域，自动滚动
        if target_cy > self.canvas_height - 50:
            self._scroll_to_node(target_cx, target_cy)

        def step(i=0):
            if i < steps:
                self.canvas.move(shadow_rect, dx, dy)
                self.canvas.move(temp_rect, dx, dy)
                self.canvas.move(temp_text, dx, dy)
                self.window.after(delay, lambda: step(i+1))
            else:
                # 高亮连接父节点和入队操作
                self.highlight_pseudo_line(8, delay=False)
                self.highlight_pseudo_line(9, delay=False)
                
                try:
                    self.canvas.delete(shadow_rect)
                    self.canvas.delete(temp_rect)
                    self.canvas.delete(temp_text)
                except Exception:
                    pass
                self.root_node = temp_root
                self.redraw_tree()
                if idx > 0:
                    parent_idx = (idx - 1) // 2
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
                self.window.after(400, lambda: self._animated_step(idx+1))

        step()

    def _draw_node(self, node: TreeNode, cx: float, cy: float, offset: float):
        left = cx - self.node_w/2
        top = cy - self.node_h/2
        right = cx + self.node_w/2
        bottom = cy + self.node_h/2

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
        self.node_to_rect[node] = rect
        self.node_items.append(rect)
        self.node_items.append(shadow_rect)

        x1 = left + self.left_cell_w
        x2 = x1 + self.center_cell_w
        v1 = self.canvas.create_line(x1, top, x1, bottom, width=1, fill="#EDF2F7")
        v2 = self.canvas.create_line(x2, top, x2, bottom, width=1, fill="#EDF2F7")
        self.node_items += [v1, v2]

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
        if self.animating or self.traversal_animating:
            messagebox.showinfo("提示", "正在动画构建,无法返回")
            return
        self.window.destroy()

    # ===========================================
    # 遍历动画功能
    # ===========================================
    
    def start_preorder_animation(self):
        """启动前序遍历动画"""
        if not self.root_node:
            messagebox.showinfo("提示", "树为空,无法遍历")
            return
        if self.traversal_animating or self.animating:
            self.update_status("已有动画在进行中", "#E53E3E")
            return
        
        self.traversal_animating = True
        self.traversal_highlights = []
        result = []
        self._collect_preorder(self.root_node, result)
        
        # 设置伪代码
        pseudo_lines = [
            "// 前序遍历 (根-左-右)",
            "void preorder(node):",
            "    if (node == null):",
            "        return",
            "    visit(node)  // 访问根节点",
            "    preorder(node.left)  // 左子树",
            "    preorder(node.right) // 右子树"
        ]
        self.set_pseudo_code("前序遍历 (根-左-右)", pseudo_lines)
        self.highlight_pseudo_line(0)
        self.highlight_pseudo_line(1)
        
        self.update_status("开始前序遍历动画...", "#9F7AEA")
        self._animate_traversal(result, 0, "前序")
    
    def start_inorder_animation(self):
        """启动中序遍历动画"""
        if not self.root_node:
            messagebox.showinfo("提示", "树为空,无法遍历")
            return
        if self.traversal_animating or self.animating:
            self.update_status("已有动画在进行中", "#E53E3E")
            return
        
        self.traversal_animating = True
        self.traversal_highlights = []
        result = []
        self._collect_inorder(self.root_node, result)
        
        # 设置伪代码
        pseudo_lines = [
            "// 中序遍历 (左-根-右)",
            "void inorder(node):",
            "    if (node == null):",
            "        return",
            "    inorder(node.left)  // 左子树",
            "    visit(node)  // 访问根节点",
            "    inorder(node.right) // 右子树"
        ]
        self.set_pseudo_code("中序遍历 (左-根-右)", pseudo_lines)
        self.highlight_pseudo_line(0)
        self.highlight_pseudo_line(1)
        
        self.update_status("开始中序遍历动画...", "#9F7AEA")
        self._animate_traversal(result, 0, "中序")
    
    def start_postorder_animation(self):
        """启动后序遍历动画"""
        if not self.root_node:
            messagebox.showinfo("提示", "树为空,无法遍历")
            return
        if self.traversal_animating or self.animating:
            self.update_status("已有动画在进行中", "#E53E3E")
            return
        
        self.traversal_animating = True
        self.traversal_highlights = []
        result = []
        self._collect_postorder(self.root_node, result)
        
        # 设置伪代码
        pseudo_lines = [
            "// 后序遍历 (左-右-根)",
            "void postorder(node):",
            "    if (node == null):",
            "        return",
            "    postorder(node.left)  // 左子树",
            "    postorder(node.right) // 右子树",
            "    visit(node)  // 访问根节点"
        ]
        self.set_pseudo_code("后序遍历 (左-右-根)", pseudo_lines)
        self.highlight_pseudo_line(0)
        self.highlight_pseudo_line(1)
        
        self.update_status("开始后序遍历动画...", "#9F7AEA")
        self._animate_traversal(result, 0, "后序")
    
    def _collect_preorder(self, node: TreeNode, result: List[TreeNode]):
        """收集前序遍历节点顺序"""
        if node:
            result.append(node)
            self._collect_preorder(node.left, result)
            self._collect_preorder(node.right, result)
    
    def _collect_inorder(self, node: TreeNode, result: List[TreeNode]):
        """收集中序遍历节点顺序"""
        if node:
            self._collect_inorder(node.left, result)
            result.append(node)
            self._collect_inorder(node.right, result)
    
    def _collect_postorder(self, node: TreeNode, result: List[TreeNode]):
        """收集后序遍历节点顺序"""
        if node:
            self._collect_postorder(node.left, result)
            self._collect_postorder(node.right, result)
            result.append(node)
    
    def _animate_traversal(self, nodes: List[TreeNode], idx: int, traversal_name: str):
        """执行遍历动画的单步"""
        if idx >= len(nodes):
            # 动画结束
            self.traversal_animating = False
            # 清除所有高亮
            for rect_id in self.traversal_highlights:
                try:
                    # 恢复到普通节点的颜色 (假设是白色背景, 蓝色边框)
                    self.canvas.itemconfig(rect_id, fill="#FFF", outline="#C6E4FF", width=2)
                except:
                    pass
            self.traversal_highlights.clear()
            
            # 完成伪代码
            self.complete_pseudo_code()
            
            # 显示完整结果
            result_str = " -> ".join([str(n.val) for n in nodes])
            self.update_status(f"{traversal_name}遍历完成", "#48BB78")
            messagebox.showinfo(f"{traversal_name}遍历结果", f"遍历序列:\n{result_str}")
            return
        
        current_node = nodes[idx]
        
        # 根据遍历类型高亮不同的visit行
        if traversal_name == "前序":
            self.highlight_pseudo_line(4, delay=False)  # visit在前
        elif traversal_name == "中序":
            self.highlight_pseudo_line(5, delay=False)  # visit在中
        elif traversal_name == "后序":
            self.highlight_pseudo_line(6, delay=False)  # visit在后
        
        # 取消上一个节点的高亮
        if idx > 0 and self.traversal_highlights:
            # 只取消上一个节点的高亮（即倒数第二个，因为最后一个是当前节点的高亮）
            prev_rect = self.node_to_rect.get(nodes[idx-1])
            if prev_rect:
                try:
                    # 将上一个高亮过的节点改为'已访问'颜色 (例如浅蓝色)
                    self.canvas.itemconfig(prev_rect, fill="#E6F7FF", outline="#91D5FF", width=2)
                except:
                    pass
        
        # 高亮当前节点
        if current_node in self.node_to_rect:
            rect_id = self.node_to_rect[current_node]
            # 记录下当前高亮的 rect_id，但为了防止重复高亮/清除，这里仅用 rect_id 查找
            # 每次动画步骤不追加到 self.traversal_highlights，而是在结束后统一清除。
            # 为了实现'已访问'和'当前访问'的区别，我们直接修改颜色。
            try:
                # 设置当前访问节点为'当前访问'颜色 (例如黄色)
                self.canvas.itemconfig(rect_id, fill="#FFF59D", outline="#F57C00", width=3)
                # 将当前节点的 rect_id 记录下来，用于结束时恢复颜色
                if rect_id not in self.traversal_highlights:
                     self.traversal_highlights.append(rect_id)
            except:
                pass
            
            # 更新状态文本
            visited = " -> ".join([str(nodes[i].val) for i in range(idx + 1)])
            self.update_status(f"{traversal_name}遍历: {visited}", "#9F7AEA")
        
        # 继续下一步
        self.window.after(800, lambda: self._animate_traversal(nodes, idx + 1, traversal_name))

    # ===========================================
    # 查找操作及动画
    # ===========================================
    
    def start_search_animation(self, value=None):
        """启动查找动画"""
        if not self.root_node:
            messagebox.showinfo("提示", "树为空，无法查找")
            return
        if self.animating or self.traversal_animating:
            self.update_status("已有动画在进行中", "#E53E3E")
            return
        
        # 如果没有传入值，尝试从 DSL 输入获取
        if value is None:
            from tkinter import simpledialog
            value = simpledialog.askstring("查找节点", "请输入要查找的值:")
            if value is None or value.strip() == "":
                return
            value = value.strip()
        
        self.traversal_animating = True
        self.traversal_highlights = []
        
        # 使用模型的查找方法获取路径
        from binary_tree.linked_storage.linked_storage_model import BinaryTreeModel
        found_node, search_path = BinaryTreeModel.search(self.root_node, value)
        
        # 设置伪代码
        pseudo_lines = [
            f"// 层序查找节点 {value}",
            "queue = new Queue()",
            "queue.enqueue(root)",
            "while (!queue.isEmpty()):",
            "    node = queue.dequeue()",
            f"    if (node.val == {value}):",
            "        return node  // 找到目标",
            "    queue.enqueue(node.left)",
            "    queue.enqueue(node.right)",
            "return null  // 未找到"
        ]
        self.set_pseudo_code(f"查找节点 {value}", pseudo_lines)
        self.highlight_pseudo_line(0)
        self.highlight_pseudo_line(1)
        self.highlight_pseudo_line(2)
        
        self.update_status(f"开始查找 {value}...", "#4299E1")
        self._animate_search(search_path, 0, value, found_node is not None)
    
    def _animate_search(self, path: list, idx: int, target_value, found: bool):
        """执行查找动画的单步"""
        if idx >= len(path):
            self.traversal_animating = False
            # 清除高亮
            for rect_id in self.traversal_highlights:
                try:
                    self.canvas.itemconfig(rect_id, fill="#FFF", outline="#C6E4FF", width=2)
                except:
                    pass
            self.traversal_highlights.clear()
            
            self.complete_pseudo_code()
            
            if found:
                self.update_status(f"找到节点 {target_value}", "#48BB78")
                messagebox.showinfo("查找成功", f"找到值为 {target_value} 的节点！")
            else:
                self.update_status(f"未找到节点 {target_value}", "#E53E3E")
                messagebox.showinfo("查找失败", f"未找到值为 {target_value} 的节点")
            return
        
        current_node = path[idx]
        
        # 高亮伪代码
        self.highlight_pseudo_line(3, delay=False)  # while
        self.highlight_pseudo_line(4, delay=False)  # dequeue
        
        # 恢复上一个节点的颜色
        if idx > 0:
            prev_node = path[idx - 1]
            prev_rect = self.node_to_rect.get(prev_node)
            if prev_rect:
                try:
                    # 已访问但未找到的节点用浅灰色
                    self.canvas.itemconfig(prev_rect, fill="#E2E8F0", outline="#A0AEC0", width=2)
                except:
                    pass
        
        # 高亮当前节点
        if current_node in self.node_to_rect:
            rect_id = self.node_to_rect[current_node]
            is_target = str(current_node.val) == str(target_value)
            
            if is_target:
                # 找到目标，用绿色高亮
                self.highlight_pseudo_line(5, delay=False)
                self.highlight_pseudo_line(6, delay=False)
                self.canvas.itemconfig(rect_id, fill="#C6F6D5", outline="#38A169", width=3)
            else:
                # 正在访问的节点用黄色
                self.canvas.itemconfig(rect_id, fill="#FFF59D", outline="#F57C00", width=3)
            
            if rect_id not in self.traversal_highlights:
                self.traversal_highlights.append(rect_id)
            
            visited = " → ".join([str(path[i].val) for i in range(idx + 1)])
            self.update_status(f"查找 {target_value}: 已访问 {visited}", "#4299E1")
        
        # 继续下一步
        delay = 600 if (idx == len(path) - 1 and found) else 500
        self.window.after(delay, lambda: self._animate_search(path, idx + 1, target_value, found))

    # ===========================================
    # 插入操作及动画
    # ===========================================
    
    def start_insert_animation(self, value=None, parent_value=None, direction='auto'):
        """启动插入动画"""
        if self.animating or self.traversal_animating:
            self.update_status("已有动画在进行中", "#E53E3E")
            return
        
        # 如果没有传入值，弹出对话框获取
        if value is None:
            from tkinter import simpledialog
            value = simpledialog.askstring("插入节点", "请输入要插入的值:")
            if value is None or value.strip() == "":
                return
            value = value.strip()
        
        self.animating = True
        
        from binary_tree.linked_storage.linked_storage_model import BinaryTreeModel
        
        # 执行插入
        new_root, new_node, success, message = BinaryTreeModel.insert(
            self.root_node, value, parent_value, direction
        )
        
        if not success:
            self.animating = False
            messagebox.showerror("插入失败", message)
            self.update_status(f"插入失败: {message}", "#E53E3E")
            return
        
        # 设置伪代码
        if parent_value:
            pseudo_lines = [
                f"// 在节点 {parent_value} 的{direction}侧插入 {value}",
                f"parent = search({parent_value})",
                "if (parent == null):",
                "    return false  // 父节点不存在",
                f"newNode = new TreeNode({value})",
                f"parent.{direction} = newNode",
                "return true  // 插入成功"
            ]
        else:
            pseudo_lines = [
                f"// 自动插入节点 {value}",
                "if (root == null):",
                f"    root = new TreeNode({value})",
                "    return",
                "queue = new Queue()",
                "queue.enqueue(root)",
                "while (!queue.isEmpty()):",
                "    node = queue.dequeue()",
                "    if (node.left == null):",
                f"        node.left = new TreeNode({value})",
                "        return",
                "    if (node.right == null):",
                f"        node.right = new TreeNode({value})",
                "        return"
            ]
        
        self.set_pseudo_code(f"插入节点 {value}", pseudo_lines)
        
        # 更新树结构
        old_root = self.root_node
        self.root_node = new_root
        
        # 先重绘树（不包含新节点的高亮）
        self.redraw_tree()
        
        # 如果有新节点，执行动画高亮
        if new_node and new_node in self.node_to_rect:
            self._animate_insert_highlight(new_node, message)
        else:
            self.animating = False
            self.complete_pseudo_code()
            self.update_status(message, "#48BB78")
            messagebox.showinfo("插入成功", message)
    
    def _animate_insert_highlight(self, new_node, message):
        """高亮新插入的节点"""
        rect_id = self.node_to_rect.get(new_node)
        if not rect_id:
            self.animating = False
            self.complete_pseudo_code()
            return
        
        # 闪烁动画
        flash_count = [0]
        original_fill = "#FFF"
        highlight_fill = "#C6F6D5"
        highlight_outline = "#38A169"
        
        def flash():
            if flash_count[0] >= 6:
                # 动画结束，恢复正常颜色
                try:
                    self.canvas.itemconfig(rect_id, fill=original_fill, outline="#C6E4FF", width=2)
                except:
                    pass
                self.animating = False
                self.complete_pseudo_code()
                self.update_status(message, "#48BB78")
                messagebox.showinfo("插入成功", message)
                return
            
            try:
                if flash_count[0] % 2 == 0:
                    self.canvas.itemconfig(rect_id, fill=highlight_fill, outline=highlight_outline, width=3)
                else:
                    self.canvas.itemconfig(rect_id, fill=original_fill, outline="#C6E4FF", width=2)
            except:
                pass
            
            flash_count[0] += 1
            self.window.after(200, flash)
        
        # 依次高亮伪代码行
        for i in range(len(self.pseudo_code_lines)):
            self.highlight_pseudo_line(i, delay=False)
        
        flash()

    # ===========================================
    # 删除操作及动画
    # ===========================================
    
    def start_delete_animation(self, value=None):
        """启动删除动画"""
        if not self.root_node:
            messagebox.showinfo("提示", "树为空，无法删除")
            return
        if self.animating or self.traversal_animating:
            self.update_status("已有动画在进行中", "#E53E3E")
            return
        
        # 如果没有传入值，弹出对话框获取
        if value is None:
            from tkinter import simpledialog
            value = simpledialog.askstring("删除节点", "请输入要删除的值:")
            if value is None or value.strip() == "":
                return
            value = value.strip()
        
        # 先找到要删除的节点以确认存在
        from binary_tree.linked_storage.linked_storage_model import BinaryTreeModel
        target, _, _ = BinaryTreeModel.search_with_parent(self.root_node, value)
        
        if not target:
            messagebox.showinfo("删除失败", f"未找到值为 {value} 的节点")
            self.update_status(f"未找到节点 {value}", "#E53E3E")
            return
        
        self.animating = True
        
        # 判断删除类型
        if not target.left and not target.right:
            delete_type = "叶子节点"
        elif not target.left or not target.right:
            delete_type = "单子节点"
        else:
            delete_type = "双子节点"
        
        # 设置伪代码
        pseudo_lines = [
            f"// 删除节点 {value} ({delete_type})",
            f"node = search({value})",
            "if (node == null):",
            "    return false",
            "// 检查子节点情况",
            "if (node.left == null && node.right == null):",
            "    // 叶子节点：直接删除",
            "    parent.child = null",
            "else if (node.left == null || node.right == null):",
            "    // 单子节点：用子节点替换",
            "    parent.child = node.child",
            "else:",
            "    // 双子节点：用中序后继替换",
            "    successor = findMin(node.right)",
            "    node.val = successor.val",
            "    delete(successor)"
        ]
        self.set_pseudo_code(f"删除节点 {value}", pseudo_lines)
        
        # 高亮要删除的节点
        self._animate_delete_phase1(target, value)
    
    def _animate_delete_phase1(self, target, value):
        """删除动画第一阶段：高亮要删除的节点"""
        rect_id = self.node_to_rect.get(target)
        if rect_id:
            # 用红色高亮要删除的节点
            self.canvas.itemconfig(rect_id, fill="#FED7D7", outline="#E53E3E", width=3)
        
        self.highlight_pseudo_line(0, delay=False)
        self.highlight_pseudo_line(1, delay=False)
        self.update_status(f"准备删除节点 {value}...", "#E53E3E")
        
        # 等待一段时间后执行删除
        self.window.after(800, lambda: self._animate_delete_phase2(value))
    
    def _animate_delete_phase2(self, value):
        """删除动画第二阶段：执行删除并重绘"""
        from binary_tree.linked_storage.linked_storage_model import BinaryTreeModel
        
        new_root, success, message, affected_path = BinaryTreeModel.delete(self.root_node, value)
        
        if success:
            self.root_node = new_root
            self.redraw_tree()
            
            # 高亮剩余伪代码行
            for i in range(4, len(self.pseudo_code_lines)):
                self.highlight_pseudo_line(i, delay=False)
            
            self.complete_pseudo_code()
            self.update_status(message, "#48BB78")
            messagebox.showinfo("删除成功", message)
        else:
            self.update_status(f"删除失败: {message}", "#E53E3E")
            messagebox.showerror("删除失败", message)
        
        self.animating = False

    # ===========================================
    # DSL 历史记录功能
    # ===========================================
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

    # ===========================================
    # DSL 命令处理
    # ===========================================
    def show_dsl_help(self):
        """显示DSL帮助信息"""
        help_text = """
═══════════════════════════════════════
    二叉树 DSL 命令帮助
═══════════════════════════════════════

【树构建命令】
  create <序列>       - 逐步动画按层序构建树
  build <序列>        - 一步构建树
  animate <序列>      - 逐步动画构建树

【节点操作命令】
  search <值>         - 查找节点 (动画演示)
  insert <值>         - 自动插入到第一个空位
  insert <值> left <父节点值>   - 插入为左子节点
  insert <值> right <父节点值>  - 插入为右子节点
  delete <值>         - 删除指定节点 (动画演示)

【遍历命令 - 显示结果】
  preorder            - 显示前序遍历结果
  inorder             - 显示中序遍历结果  
  postorder           - 显示后序遍历结果
  levelorder          - 显示层序遍历结果

【遍历命令 - 动画演示】
  preorder-anim       - 前序遍历动画
  inorder-anim        - 中序遍历动画
  postorder-anim      - 后序遍历动画

【实用命令】
  clear / reset       - 清空画布
  height              - 计算并显示树的高度
  count               - 计算并显示节点数量
  help / ?            - 显示此帮助信息

【使用说明】
  • 序列支持用逗号或空格分隔节点
  • 使用 '#' 表示空节点
  • 按↑↓箭头键可浏览命令历史记录
  • 所有操作都有动画演示效果

【示例】
  create 1,2,3,#,4,#,5
  search 4
  insert 6 left 3
  delete 2
═══════════════════════════════════════
        """
        messagebox.showinfo("DSL 命令帮助", help_text)

    def process_dsl(self, event=None):
        raw = (self.dsl_var.get() or "").strip()
        if not raw:
            return
        
        # 添加到历史记录
        self.add_to_history(raw)
        
        # 将命令拆分:允许用空格或逗号分隔节点,命令与其参数也可用空格分隔
        parts = [p for p in re.split(r'[\s,]+', raw) if p != ""]
        if not parts:
            return
        cmd = parts[0].lower()
        args = parts[1:]

        try:
            # 🌳 树构建命令
            if cmd in ("create", "animate"):
                if not args:
                    messagebox.showinfo("用法", "示例: create 1 # 2 3 # 3 4 5 (用空格或逗号分隔,# 表示空)")
                    return
                seq_text = " ".join(args)
                self.input_var.set(seq_text)
                self.start_animated_build()
                
            elif cmd == "build":
                if not args:
                    messagebox.showinfo("用法", "示例: build 1 # 2 3 # 3 4 5")
                    return
                seq_text = " ".join(args)
                self.input_var.set(seq_text)
                self.build_tree_from_input()

            # 🔍 查找命令
            elif cmd in ("search", "find"):
                if not args:
                    # 没有参数时弹出对话框
                    self.start_search_animation()
                else:
                    self.start_search_animation(args[0])

            # ➕ 插入命令
            elif cmd == "insert":
                if not args:
                    # 没有参数时弹出对话框
                    self.start_insert_animation()
                else:
                    value = args[0]
                    parent_value = None
                    direction = 'auto'
                    
                    # 解析插入参数: insert <value> [left|right] [parent_value]
                    # 或: insert <value> left <parent_value>
                    # 或: insert <value> right <parent_value>
                    if len(args) >= 3:
                        if args[1].lower() in ('left', 'l'):
                            direction = 'left'
                            parent_value = args[2]
                        elif args[1].lower() in ('right', 'r'):
                            direction = 'right'
                            parent_value = args[2]
                        elif args[2].lower() in ('left', 'l'):
                            parent_value = args[1]
                            direction = 'left'
                        elif args[2].lower() in ('right', 'r'):
                            parent_value = args[1]
                            direction = 'right'
                    elif len(args) >= 2:
                        # insert <value> <parent_value> (自动选择方向)
                        if args[1].lower() in ('left', 'l', 'right', 'r'):
                            direction = 'left' if args[1].lower() in ('left', 'l') else 'right'
                        else:
                            parent_value = args[1]
                    
                    self.start_insert_animation(value, parent_value, direction)

            # ➖ 删除命令
            elif cmd == "delete":
                if not args:
                    # 没有参数时弹出对话框
                    self.start_delete_animation()
                else:
                    self.start_delete_animation(args[0])

            # 📊 遍历命令(静态显示)
            elif cmd == "preorder":
                self.show_traversal("preorder")
            elif cmd == "inorder":
                self.show_traversal("inorder")
            elif cmd == "postorder":
                self.show_traversal("postorder")
            elif cmd == "levelorder":
                self.show_traversal("levelorder")
            
            # 🎬 遍历动画命令
            elif cmd in ("preorder-anim", "preorder-animate"):
                self.start_preorder_animation()
            elif cmd in ("inorder-anim", "inorder-animate"):
                self.start_inorder_animation()
            elif cmd in ("postorder-anim", "postorder-animate"):
                self.start_postorder_animation()

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

    # ===========================================
    # DSL 命令的具体实现
    # ===========================================
    
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
    window.geometry("1350x800")
    window.configure(bg="#F3F6FA")
    BinaryTreeVisualizer(window)
    window.mainloop()