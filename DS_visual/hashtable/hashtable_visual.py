# -*- coding: utf-8 -*-
from tkinter import *
from tkinter import messagebox, filedialog, ttk
import json
import os
import sys
from datetime import datetime

# 支持直接运行和作为模块导入
try:
    from hashtable.hashtable_model import HashTableModel, TOMBSTONE, CollisionMethod, HASH_PRESETS, parse_hash_expression
except ModuleNotFoundError:
    from hashtable_model import HashTableModel, TOMBSTONE, CollisionMethod, HASH_PRESETS, parse_hash_expression

try:
    from llm import function_dispatcher
except ModuleNotFoundError:
    function_dispatcher = None


class HashtableVisualizer:
    def __init__(self, root, capacity: int = 11, method: CollisionMethod = CollisionMethod.OPEN_ADDRESSING):
        self.window = root
        self.window.config(bg="#0a0f1a")
        
        # 主容器
        self.main_frame = Frame(self.window, bg="#0a0f1a")
        self.main_frame.pack(fill=BOTH, expand=True)

        self.capacity = capacity
        self.method = method
        self.model = HashTableModel(self.capacity, self.method)

        # 布局参数
        self.left_width = 280
        self.right_width = 320
        self.start_x = 60
        self.start_y = 200
        self.cell_width = 80
        self.cell_height = 50
        self.spacing = 8

        # 可视元素引用
        self.cell_rects = []
        self.cell_texts = []
        self.index_texts = []
        self.chain_elements = []

        # 控件与状态
        self.value_entry = StringVar()
        self.dsl_var = StringVar()
        self.batch_entry_var = StringVar()
        self.input_frame = None
        self.animating = False
        self.batch_queue = []
        self.batch_index = 0

        self.capacity_var = StringVar(value=str(self.capacity))
        self.resize_frame = None

        # 散列函数相关
        self.hash_expr_var = StringVar(value="x % capacity")
        self.hash_preset_var = StringVar(value="mod")
        self.hash_frame = None

        # 动画临时数据
        self._anim_highlights = []
        self._anim_temp = []
        
        # 自动滚动相关
        self._auto_scroll_enabled = True
        
        # 状态和解释变量
        self.status_var = StringVar(value="就绪：请输入值并执行操作")
        self.explanation_var = StringVar(value="")
        
        # 伪代码标签字典
        self.code_labels = {}
        
        # LLM聊天窗口引用
        self.chat_window = None

        # 构建界面
        self._build_left_panel()
        self._build_center_panel()
        self._build_right_panel()
        
        self.update_display()
        
        # 注册到LLM函数调度器
        if function_dispatcher is not None:
            try:
                function_dispatcher.register_visualizer("hashtable", self)
                print("Hashtable visualizer registered.")
            except Exception as e:
                print("Hashtable registered failed:", e)

    def _build_left_panel(self):
        self.left_panel = Frame(self.main_frame, width=self.left_width, bg="#0a0f1a")
        self.left_panel.pack(side=LEFT, fill=Y, padx=(10, 0), pady=10)
        self.left_panel.pack_propagate(False)
        
        pad = 12
        
        # 标题
        title_frame = Frame(self.left_panel, bg="#0a0f1a")
        title_frame.pack(fill=X, pady=(10, 5))
        
        method_name = "开放寻址" if self.method == CollisionMethod.OPEN_ADDRESSING else "拉链法"
        Label(title_frame, text="📊 散列表可视化", fg="#4fd1c5",
              font=("Microsoft YaHei UI", 16, "bold"), bg="#0a0f1a").pack()
        Label(title_frame, text=f"冲突处理: {method_name}", bg="#0a0f1a",
              fg="#718096", font=("Microsoft YaHei UI", 9)).pack(pady=(2, 0))
        
        Frame(self.left_panel, height=2, bg="#1a2744").pack(fill=X, padx=pad, pady=(10, 10))
        
        # DSL命令输入区
        dsl_frame = Frame(self.left_panel, bg="#0a0f1a")
        dsl_frame.pack(padx=pad, pady=(0, 8), fill=X)
        
        dsl_title_frame = Frame(dsl_frame, bg="#0a0f1a")
        dsl_title_frame.pack(fill=X)
        
        Label(dsl_title_frame, text="⚡ DSL命令", 
              font=("Microsoft YaHei UI", 10, "bold"), 
              bg="#0a0f1a", fg="#9f7aea").pack(side=LEFT)
        
        # DSL帮助按钮
        def show_dsl_help():
            help_text = """
╔══════════════════════════════════════╗
║       📖 散列表 DSL 命令帮助           ║
╠══════════════════════════════════════╣
║                                      ║
║  📥 创建/插入操作:                    ║
║    create 23 17 35 8 42 29           ║
║    insert 50                         ║
║    add 60                            ║
║                                      ║
║  🔍 查找操作:                         ║
║    find 23                           ║
║    search 17                         ║
║                                      ║
║  🗑️ 删除/清空操作:                    ║
║    delete 23                         ║
║    remove 17                         ║
║    clear                             ║
║                                      ║
║  🔧 散列函数设置:                     ║
║    hash x%7                          ║
║    hash! (x*2+1)%capacity            ║
║    preset mod/multiply/square_mid    ║
║                                      ║
║  ⚙️ 其他操作:                         ║
║    resize 17                         ║
║    switch (切换冲突处理方法)          ║
║                                      ║
║  💡 提示:                             ║
║    直接输入数字列表会当作create处理   ║
║    例如: 23 17 35 8 42               ║
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
        self.dsl_var.set("create 23 17 35 8 42 29")
        dsl_entry = Entry(dsl_frame, textvariable=self.dsl_var, font=("Consolas", 11),
                     bg="#1a2744", fg="#e2e8f0", insertbackground="#9f7aea",
                     relief=FLAT, bd=6)
        dsl_entry.pack(fill=X, pady=(8, 0), ipady=4)
        dsl_entry.bind("<Return>", lambda e: self._execute_dsl())
        dsl_entry.bind("<KP_Enter>", lambda e: self._execute_dsl())
        
        # DSL执行按钮
        Button(dsl_frame, text="▶ 执行DSL", bg="#9f7aea", fg="white",
               bd=0, font=("Microsoft YaHei UI", 10, "bold"),
               activebackground="#805ad5", activeforeground="white",
               command=self._execute_dsl, cursor="hand2").pack(fill=X, pady=(8, 0), ipady=5)
        
        Frame(self.left_panel, height=2, bg="#1a2744").pack(fill=X, padx=pad, pady=(10, 8))
        
        btn_frame = Frame(self.left_panel, bg="#0a0f1a")
        btn_frame.pack(padx=pad, fill=X)
        
        btn_style = {'font': ("Microsoft YaHei UI", 9, "bold"), 'bd': 0, 'cursor': 'hand2'}
        
        row1 = Frame(btn_frame, bg="#0a0f1a")
        row1.pack(fill=X, pady=2)
        Button(row1, text="插入", bg="#3498DB", fg="white", width=7,
               command=self.prepare_insert, **btn_style).pack(side=LEFT, padx=2)
        Button(row1, text="查找", bg="#2ECC71", fg="white", width=7,
               command=self.prepare_find, **btn_style).pack(side=LEFT, padx=2)
        Button(row1, text="删除", bg="#E74C3C", fg="white", width=7,
               command=self.prepare_delete, **btn_style).pack(side=LEFT, padx=2)
        
        row2 = Frame(btn_frame, bg="#0a0f1a")
        row2.pack(fill=X, pady=2)
        Button(row2, text="清空", bg="#95A5A6", fg="white", width=7,
               command=self.clear_table, **btn_style).pack(side=LEFT, padx=2)
        Button(row2, text="切换模式", bg="#9B59B6", fg="white", width=7,
               command=self.switch_method, **btn_style).pack(side=LEFT, padx=2)
        Button(row2, text="散列函数", bg="#1ABC9C", fg="white", width=7,
               command=self.prepare_hash_func, **btn_style).pack(side=LEFT, padx=2)
        
        row3 = Frame(btn_frame, bg="#0a0f1a")
        row3.pack(fill=X, pady=2)
        Button(row3, text="调整容量", bg="#F39C12", fg="white", width=7,
               command=self.prepare_resize, **btn_style).pack(side=LEFT, padx=2)
        Button(row3, text="保存", bg="#3498DB", fg="white", width=7,
               command=self.save_structure, **btn_style).pack(side=LEFT, padx=2)
        Button(row3, text="加载", bg="#2ECC71", fg="white", width=7,
               command=self.load_structure, **btn_style).pack(side=LEFT, padx=2)
        
        Frame(self.left_panel, height=2, bg="#1a2744").pack(fill=X, padx=pad, pady=(10, 8))
        
        explain_frame = Frame(self.left_panel, bg="#1a2744", bd=0)
        explain_frame.pack(fill=X, padx=pad, pady=(0, 8))
        
        explain_header = Frame(explain_frame, bg="#2d3748")
        explain_header.pack(fill=X)
        Label(explain_header, text="💡 操作说明", bg="#2d3748", fg="#fbd38d",
              font=("Microsoft YaHei UI", 9, "bold")).pack(anchor="w", padx=8, pady=4)
        
        self.explanation_label = Label(explain_frame, textvariable=self.explanation_var,
              bg="#1a2744", wraplength=self.left_width - 35, justify=LEFT, fg="#e2e8f0",
              font=("Microsoft YaHei UI", 8))
        self.explanation_label.pack(padx=8, pady=6, anchor="w")
        
        Frame(self.left_panel, height=2, bg="#1a2744").pack(fill=X, padx=pad, pady=(0, 8))
        
        self.status_label = Label(self.left_panel, textvariable=self.status_var,
                                 bg="#0a0f1a", wraplength=self.left_width - 25,
                                 justify=LEFT, fg="#68d391", font=("Microsoft YaHei UI", 8))
        self.status_label.pack(padx=pad, pady=(0, 8), anchor="w")
        
        help_frame = Frame(self.left_panel, bg="#0d1526")
        help_frame.pack(fill=X, padx=pad, pady=(0, 5))
        help_text = "命令: create x y z | insert x\nfind x | delete x | clear\nhash expr | preset name"
        Label(help_frame, text=help_text, bg="#0d1526", fg="#718096",
              font=("Consolas", 7), justify=LEFT).pack(padx=6, pady=4, anchor="w")

    def _build_center_panel(self):
        self.center_panel = Frame(self.main_frame, bg="#0a0f1a")
        self.center_panel.pack(side=LEFT, fill=BOTH, expand=True, padx=8, pady=10)
        
        self.canvas = Canvas(self.center_panel, bg="#0d1526", bd=0, highlightthickness=0)
        self.canvas.pack(fill=BOTH, expand=True)
        
        h_scroll = Scrollbar(self.center_panel, orient=HORIZONTAL, command=self.canvas.xview)
        h_scroll.pack(fill=X, side=BOTTOM)
        self.canvas.configure(xscrollcommand=h_scroll.set)

    def _build_right_panel(self):
        self.right_panel = Frame(self.main_frame, width=self.right_width, bg="#0d1526")
        self.right_panel.pack(side=RIGHT, fill=Y, padx=(0, 10), pady=10)
        self.right_panel.pack_propagate(False)
        
        pad = 10
        
        header = Frame(self.right_panel, bg="#1a2744")
        header.pack(fill=X)
        Label(header, text="📜 算法伪代码", bg="#1a2744", fg="#63b3ed",
              font=("Microsoft YaHei UI", 11, "bold")).pack(pady=8)
        
        code_container = Frame(self.right_panel, bg="#0d1526")
        code_container.pack(fill=BOTH, expand=True, padx=pad, pady=(0, pad))
        
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
        
        self._init_pseudocode()
        
        Frame(self.right_panel, height=2, bg="#1a2744").pack(fill=X, padx=pad, pady=(5, 5))
        
        legend_frame = Frame(self.right_panel, bg="#0d1526")
        legend_frame.pack(fill=X, padx=pad, pady=(0, 5))
        
        Label(legend_frame, text="📊 颜色说明：", bg="#0d1526", fg="#a0aec0",
              font=("Microsoft YaHei UI", 8, "bold")).pack(anchor="w", pady=(0, 4))
        
        legends = [
            ("#fbd38d", "🟡 正在探测"),
            ("#68d391", "🟢 操作成功"),
            ("#fc8181", "🔴 冲突/删除"),
            ("#63b3ed", "🔵 目标位置"),
        ]
        
        for color, text in legends:
            row = Frame(legend_frame, bg="#0d1526")
            row.pack(fill=X, pady=1)
            Label(row, text=text, bg="#0d1526", fg=color, font=("Microsoft YaHei UI", 7)).pack(side=LEFT)

    def _init_pseudocode(self):
        self.pseudocode_lines = [
            ("", "【插入算法 - 开放寻址】", "title"),
            ("INS_START", "procedure INSERT(key):", "header"),
            ("INS_HASH", "  idx ← hash(key) % capacity", "code"),
            ("INS_LOOP", "  while table[idx] 非空:", "code"),
            ("INS_CHECK", "    if table[idx] == key:", "code"),
            ("INS_EXISTS", "      return 已存在", "code"),
            ("INS_PROBE", "    idx ← (idx + 1) % capacity", "code"),
            ("INS_FULL", "    if 回到起点: return 表满", "code"),
            ("INS_DO", "  table[idx] ← key", "code"),
            ("INS_END", "  return 插入成功", "header"),
            ("", "", "blank"),
            ("", "【查找算法】", "title"),
            ("FIND_START", "procedure FIND(key):", "header"),
            ("FIND_HASH", "  idx ← hash(key) % capacity", "code"),
            ("FIND_LOOP", "  while table[idx] 非空:", "code"),
            ("FIND_CHECK", "    if table[idx] == key:", "code"),
            ("FIND_FOUND", "      return (true, idx)", "code"),
            ("FIND_PROBE", "    idx ← (idx + 1) % capacity", "code"),
            ("FIND_END", "  return (false, -1)", "header"),
            ("", "", "blank"),
            ("", "【删除算法】", "title"),
            ("DEL_START", "procedure DELETE(key):", "header"),
            ("DEL_FIND", "  (found, idx) ← FIND(key)", "code"),
            ("DEL_CHECK", "  if not found:", "code"),
            ("DEL_NOTFOUND", "    return 未找到", "code"),
            ("DEL_TOMB", "  table[idx] ← TOMBSTONE", "code"),
            ("DEL_END", "  return 删除成功", "header"),
        ]
        
        self.code_labels = {}
        
        for step_id, text, style in self.pseudocode_lines:
            frame = Frame(self.code_frame, bg="#0d1526")
            frame.pack(fill=X, anchor="w")
            
            if style == "title":
                lbl = Label(frame, text=text, bg="#0d1526", fg="#fbd38d",
                           font=("Consolas", 9, "bold"))
            elif style == "header":
                lbl = Label(frame, text=text, bg="#0d1526", fg="#9f7aea",
                           font=("Consolas", 8, "bold"))
            elif style == "comment":
                lbl = Label(frame, text=text, bg="#0d1526", fg="#718096",
                           font=("Consolas", 7, "italic"))
            elif style == "blank":
                lbl = Label(frame, text=" ", bg="#0d1526", font=("Consolas", 4))
            else:
                lbl = Label(frame, text=text, bg="#0d1526", fg="#a0aec0",
                           font=("Consolas", 8))
            
            lbl.pack(anchor="w", padx=6, pady=0)
            
            if step_id:
                self.code_labels[step_id] = lbl

    def highlight_pseudocode(self, step_ids, clear_others=True):
        if clear_others:
            for sid, lbl in self.code_labels.items():
                lbl.config(bg="#0d1526")
                for line_id, text, style in self.pseudocode_lines:
                    if line_id == sid:
                        if style == "header":
                            lbl.config(fg="#9f7aea")
                        elif style == "comment":
                            lbl.config(fg="#718096")
                        else:
                            lbl.config(fg="#a0aec0")
                        break
        
        for step_id in step_ids:
            if step_id in self.code_labels:
                self.code_labels[step_id].config(bg="#2d4a3e", fg="#68d391")
                self.code_labels[step_id].update_idletasks()

    def update_status(self, text):
        self.status_var.set(text)
    
    def update_explanation(self, text):
        self.explanation_var.set(text)

    def switch_method(self):
        if self.animating:
            messagebox.showinfo("提示", "动画进行中，无法切换")
            return
        
        if self.method == CollisionMethod.OPEN_ADDRESSING:
            old_data = [v for v in self.model.table if v is not None and v is not self.model.tombstone]
            new_method = CollisionMethod.CHAINING
        else:
            old_data = [item for chain in self.model.table for item in chain]
            new_method = CollisionMethod.OPEN_ADDRESSING
        
        self.method = new_method
        self.model = HashTableModel(self.capacity, self.method)
        
        for item in old_data:
            self.model.insert(item)
        
        self.update_display()
        
        method_name = "拉链法" if new_method == CollisionMethod.CHAINING else "开放寻址法"
        self.update_status(f"✓ 已切换到{method_name}")
        messagebox.showinfo("切换成功", f"已切换到{method_name}")

    def prepare_resize(self):
        if self.animating:
            return
        self._open_resize_input()

    def _open_resize_input(self):
        if self.resize_frame:
            self.resize_frame.destroy()
        self.resize_frame = Toplevel(self.window)
        self.resize_frame.title("调整容量")
        self.resize_frame.geometry("300x100")
        self.resize_frame.config(bg="#1a2744")
        self.resize_frame.transient(self.window)
        self.resize_frame.grab_set()

        Label(self.resize_frame, text=f"新容量 (当前: {self.capacity}):", 
              font=("Microsoft YaHei UI", 10), bg="#1a2744", fg="#e2e8f0").pack(pady=(15, 5))
        
        entry = Entry(self.resize_frame, textvariable=self.capacity_var, width=10,
                      font=("Consolas", 11), bg="#0d1526", fg="#e2e8f0",
                      insertbackground="#e2e8f0", relief=FLAT)
        entry.pack(pady=5)
        
        btn_frame = Frame(self.resize_frame, bg="#1a2744")
        btn_frame.pack(pady=10)
        Button(btn_frame, text="确认", bg="#F39C12", fg="white", bd=0, width=8,
               font=("Microsoft YaHei UI", 9, "bold"),
               command=self._on_confirm_resize).pack(side=LEFT, padx=5)
        Button(btn_frame, text="取消", bg="#95A5A6", fg="white", bd=0, width=8,
               font=("Microsoft YaHei UI", 9, "bold"),
               command=self._close_resize_input).pack(side=LEFT, padx=5)
        
        entry.focus_set()
        entry.select_range(0, END)

    def _on_confirm_resize(self):
        try:
            new_cap = int(self.capacity_var.get())
            if new_cap <= 0:
                messagebox.showerror("错误", "容量必须是正整数")
                return
            if new_cap == self.capacity:
                self._close_resize_input()
                return
            if self.method == CollisionMethod.OPEN_ADDRESSING and new_cap < len(self.model):
                messagebox.showerror("错误", f"新容量({new_cap})不能小于当前元素数量({len(self.model)})")
                return
            self.model.resize(new_cap)
            self.capacity = new_cap
            self.update_display()
            self._close_resize_input()
            self.update_status(f"✓ 容量已调整为 {self.capacity}")
        except ValueError:
            messagebox.showerror("错误", "请输入有效的整数容量")
        except Exception as e:
            messagebox.showerror("错误", f"调整容量失败: {str(e)}")

    def _close_resize_input(self):
        if self.resize_frame:
            self.resize_frame.destroy()
            self.resize_frame = None

    def prepare_hash_func(self):
        if self.animating:
            return
        self._open_hash_input()

    def _open_hash_input(self):
        if self.hash_frame:
            self.hash_frame.destroy()
        self.hash_frame = Toplevel(self.window)
        self.hash_frame.title("散列函数设置")
        self.hash_frame.geometry("450x180")
        self.hash_frame.config(bg="#1a2744")
        self.hash_frame.transient(self.window)
        self.hash_frame.grab_set()

        row1 = Frame(self.hash_frame, bg="#1a2744")
        row1.pack(fill=X, padx=15, pady=(15, 5))
        Label(row1, text="预设:", font=("Microsoft YaHei UI", 10), bg="#1a2744", fg="#e2e8f0").pack(side=LEFT)
        preset_combo = ttk.Combobox(row1, textvariable=self.hash_preset_var, width=15, state="readonly",
                                     values=list(HASH_PRESETS.keys()))
        preset_combo.pack(side=LEFT, padx=10)
        preset_combo.bind("<<ComboboxSelected>>", self._on_preset_selected)
        
        self.preset_desc_label = Label(row1, text=HASH_PRESETS.get(self.hash_preset_var.get(), ("", ""))[1],
                                       font=("Microsoft YaHei UI", 8), bg="#1a2744", fg="#718096")
        self.preset_desc_label.pack(side=LEFT, padx=5)

        row2 = Frame(self.hash_frame, bg="#1a2744")
        row2.pack(fill=X, padx=15, pady=5)
        Label(row2, text="表达式:", font=("Microsoft YaHei UI", 10), bg="#1a2744", fg="#e2e8f0").pack(side=LEFT)
        
        self.hash_expr_var.set(self.model.hash_expr)
        hash_entry = Entry(row2, textvariable=self.hash_expr_var, width=30,
                          font=("Consolas", 10), bg="#0d1526", fg="#e2e8f0",
                          insertbackground="#e2e8f0", relief=FLAT)
        hash_entry.pack(side=LEFT, padx=10)

        Label(self.hash_frame, text="变量: x(值), capacity(容量)  例: x%7, (x*2+1)%capacity",
              font=("Microsoft YaHei UI", 8), bg="#1a2744", fg="#718096").pack(pady=5)

        btn_frame = Frame(self.hash_frame, bg="#1a2744")
        btn_frame.pack(pady=15)
        Button(btn_frame, text="应用", bg="#1ABC9C", fg="white", bd=0, width=8,
               font=("Microsoft YaHei UI", 9, "bold"),
               command=self._on_apply_hash).pack(side=LEFT, padx=5)
        Button(btn_frame, text="重建表", bg="#E67E22", fg="white", bd=0, width=8,
               font=("Microsoft YaHei UI", 9, "bold"),
               command=self._on_rebuild_with_hash).pack(side=LEFT, padx=5)
        Button(btn_frame, text="取消", bg="#95A5A6", fg="white", bd=0, width=8,
               font=("Microsoft YaHei UI", 9, "bold"),
               command=self._close_hash_input).pack(side=LEFT, padx=5)

    def _on_preset_selected(self, event=None):
        preset = self.hash_preset_var.get()
        if preset in HASH_PRESETS:
            expr, desc = HASH_PRESETS[preset]
            self.hash_expr_var.set(expr)
            if hasattr(self, 'preset_desc_label'):
                self.preset_desc_label.config(text=desc)

    def _on_apply_hash(self):
        expr = self.hash_expr_var.get().strip()
        if not expr:
            messagebox.showerror("错误", "请输入散列函数表达式")
            return
        try:
            test_func = parse_hash_expression(expr, self.capacity)
            test_func(42)
            self.model.set_hash_expression(expr)
            self.update_display()
            self._close_hash_input()
            self.update_status(f"✓ 散列函数已更新: h(x) = {expr}")
        except Exception as e:
            messagebox.showerror("错误", f"无效的散列函数表达式: {str(e)}")

    def _on_rebuild_with_hash(self):
        expr = self.hash_expr_var.get().strip()
        if not expr:
            messagebox.showerror("错误", "请输入散列函数表达式")
            return
        try:
            test_func = parse_hash_expression(expr, self.capacity)
            test_func(42)
            
            if self.method == CollisionMethod.OPEN_ADDRESSING:
                old_data = [v for v in self.model.table if v is not None and v is not self.model.tombstone]
            else:
                old_data = [item for chain in self.model.table for item in chain]
            
            self.model = HashTableModel(self.capacity, self.method, hash_expr=expr)
            for item in old_data:
                self.model.insert(item)
            
            self.update_display()
            self._close_hash_input()
            self.update_status(f"✓ 已使用新散列函数重建表: h(x) = {expr}")
        except Exception as e:
            messagebox.showerror("错误", f"重建失败: {str(e)}")

    def _close_hash_input(self):
        if self.hash_frame:
            self.hash_frame.destroy()
            self.hash_frame = None

    def set_hash_expression(self, expr, rebuild=True):
        if self.animating:
            return False
        try:
            test_func = parse_hash_expression(expr, self.capacity)
            test_func(42)
            
            if rebuild:
                if self.method == CollisionMethod.OPEN_ADDRESSING:
                    old_data = [v for v in self.model.table if v is not None and v is not self.model.tombstone]
                else:
                    old_data = [item for chain in self.model.table for item in chain]
                
                self.model = HashTableModel(self.capacity, self.method, hash_expr=expr)
                for item in old_data:
                    self.model.insert(item)
            else:
                self.model.set_hash_expression(expr)
            
            self.update_display()
            return True
        except Exception as e:
            messagebox.showerror("错误", f"设置散列函数失败: {str(e)}")
            return False
    
    def _execute_dsl(self, event=None):
        """执行DSL输入框中的命令（新的统一入口）"""
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
            # 如果DSL_utils不可用，回退到内置的process_dsl
            self.process_dsl()
        finally:
            try:
                self.dsl_var.set("")
            except:
                pass

    def process_dsl(self):
        text = self.dsl_var.get().strip()
        try:
            if text.startswith("create"):
                items = text.split()[1:]
                if not items:
                    messagebox.showerror("错误", "create 后请提供数值")
                    return
                try:
                    values = [int(x) for x in items]
                except ValueError:
                    messagebox.showerror("错误", "create 后请提供整数")
                    return
                self.batch_queue = values
                self.batch_index = 0
                self._set_buttons_state("disabled")
                self._batch_step()
            elif text.startswith("insert"):
                parts = text.split()
                if len(parts) != 2:
                    messagebox.showerror("错误", "格式: insert x")
                    return
                self.insert_value(int(parts[1]))
            elif text.startswith(("find", "search")):
                parts = text.split()
                if len(parts) != 2:
                    messagebox.showerror("错误", "格式: find x")
                    return
                self.find_value(int(parts[1]))
            elif text.startswith("delete"):
                parts = text.split()
                if len(parts) != 2:
                    messagebox.showerror("错误", "格式: delete x")
                    return
                self.delete_value(int(parts[1]))
            elif text == "clear":
                self.clear_table()
            elif text.startswith("hash"):
                expr_part = text[4:].strip()
                rebuild = False
                if text.startswith("hash!"):
                    rebuild = True
                    expr_part = text[5:].strip()
                
                if not expr_part:
                    messagebox.showerror("错误", "请提供散列函数表达式")
                    return
                
                if expr_part.lower() in HASH_PRESETS:
                    expr_part = HASH_PRESETS[expr_part.lower()][0]
                
                if self.set_hash_expression(expr_part, rebuild=rebuild):
                    mode = "（已重建表）" if rebuild else "（仅更新函数）"
                    self.update_status(f"✓ 散列函数: h(x) = {expr_part} {mode}")
            elif text.startswith("preset"):
                parts = text.split()
                if len(parts) != 2:
                    presets_list = ", ".join(HASH_PRESETS.keys())
                    messagebox.showinfo("预设", f"可用预设: {presets_list}\n用法: preset <名称>")
                    return
                preset_name = parts[1].lower()
                if preset_name not in HASH_PRESETS:
                    messagebox.showerror("错误", f"未知预设: {preset_name}")
                    return
                expr = HASH_PRESETS[preset_name][0]
                if self.set_hash_expression(expr, rebuild=True):
                    self.update_status(f"✓ 已应用预设 '{preset_name}'")
            else:
                messagebox.showerror("错误", "未知命令")
        finally:
            self.dsl_var.set("")

    def save_structure(self):
        payload = {
            "type": "hashtable",
            "capacity": self.capacity,
            "method": self.method.value,
            "hash_expr": self.model.hash_expr,
            "data": self.model.table
        }
        filepath = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if not filepath:
            return
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        self.update_status(f"✓ 已保存到 {os.path.basename(filepath)}")

    def load_structure(self):
        filepath = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if not filepath:
            return
        with open(filepath, "r", encoding="utf-8") as f:
            loaded = json.load(f)
        
        method_str = loaded.get("method", "open_addressing")
        new_method = CollisionMethod.CHAINING if method_str == "chaining" else CollisionMethod.OPEN_ADDRESSING
        
        if new_method != self.method:
            self.method = new_method
        
        self.capacity = loaded["capacity"]
        hash_expr = loaded.get("hash_expr", "x % capacity")
        self.model = HashTableModel(self.capacity, self.method, hash_expr=hash_expr)
        self.model.table = loaded["data"]
        
        if self.method == CollisionMethod.OPEN_ADDRESSING:
            self.model.size = sum(1 for v in self.model.table if v is not None and v is not TOMBSTONE)
        else:
            self.model.size = sum(len(chain) for chain in self.model.table)
        
        self.update_display()
        self.update_status(f"✓ 已加载散列表 (h(x) = {hash_expr})")

    def prepare_insert(self, default_value=""):
        if self.animating:
            return
        self._open_input("插入的值", default_value, "insert")

    def prepare_find(self, default_value=""):
        if self.animating:
            return
        self._open_input("查找的值", default_value, "find")

    def prepare_delete(self, default_value=""):
        if self.animating:
            return
        self._open_input("删除的值", default_value, "delete")

    def _open_input(self, label_text, default_value, action):
        if self.input_frame:
            self.input_frame.destroy()
        self.value_entry.set(default_value)

        self.input_frame = Toplevel(self.window)
        self.input_frame.title(label_text)
        self.input_frame.geometry("250x100")
        self.input_frame.config(bg="#1a2744")
        self.input_frame.transient(self.window)
        self.input_frame.grab_set()

        Label(self.input_frame, text=f"{label_text}:", font=("Microsoft YaHei UI", 10),
              bg="#1a2744", fg="#e2e8f0").pack(pady=(15, 5))
        
        entry = Entry(self.input_frame, textvariable=self.value_entry, width=15,
                      font=("Consolas", 11), bg="#0d1526", fg="#e2e8f0",
                      insertbackground="#e2e8f0", relief=FLAT)
        entry.pack(pady=5)
        entry.bind("<Return>", lambda e: self._on_confirm(action))
        
        Button(self.input_frame, text="确认", bg="#3498DB", fg="white", bd=0, width=10,
               font=("Microsoft YaHei UI", 9, "bold"),
               command=lambda: self._on_confirm(action)).pack(pady=10)
        
        entry.focus_set()

    def _on_confirm(self, action):
        val = self.value_entry.get().strip()
        if not val:
            messagebox.showerror("错误", "请输入一个值")
            return
        if self.input_frame:
            self.input_frame.destroy()
            self.input_frame = None
        try:
            int_val = int(val)
            {"insert": self.insert_value, "find": self.find_value, "delete": self.delete_value}[action](int_val)
        except ValueError:
            messagebox.showerror("错误", "请输入整数")

    def insert_value(self, value):
        if self.animating:
            return
        
        self.animating = True
        self._set_buttons_state("disabled")
        self._clear_temp_graphics()
        self.update_display()
        
        self.highlight_pseudocode(["INS_START"])
        self.update_status(f"▶ 开始插入: {value}")
        self.update_explanation(f"准备插入键值 {value}\n首先计算散列地址...")

        # 先显示哈希计算过程，然后进行插入动画
        def after_hash_calc():
            self._clear_temp_graphics()
            if self.method == CollisionMethod.OPEN_ADDRESSING:
                self._insert_open_animated_after_hash(value)
            else:
                self._insert_chain_animated_after_hash(value)
        
        self._show_hash_calculation_animation(value, after_hash_calc, operation="插入")

    def _insert_open_animated_after_hash(self, value):
        """开放寻址法插入动画（哈希计算后调用）"""
        before = list(self.model.table)
        target_idx, probe_path, is_full, _ = self.model.insert(value)
        after = list(self.model.table)
        
        self.model.table = before
        self.model.size = sum(1 for v in self.model.table if v is not None and v is not TOMBSTONE)

        if is_full:
            self.update_display()
            self.highlight_pseudocode(["INS_FULL"])
            self.update_status("✗ 散列表已满")
            self._finish_animation()
            return
        
        if target_idx is None:
            self.update_display()
            self.highlight_pseudocode(["INS_EXISTS"])
            self.update_status(f"✗ 值 {value} 已存在")
            self._finish_animation()
            return

        self.update_display()

        init_idx = self.model._hash(value)
        step_delay = 400
        current = {'i': 0}

        def highlight_step():
            i = current['i']
            self._clear_temp_graphics()
            
            if i >= len(probe_path):
                self._do_insert_animation(value, target_idx, after)
                return
            
            idx = probe_path[i]
            # 自动滚动到当前探测的单元格
            self._scroll_to_cell(idx)
            
            x = self.start_x + idx * (self.cell_width + self.spacing)
            h = self.canvas.create_rectangle(x, self.start_y, x + self.cell_width,
                                            self.start_y + self.cell_height,
                                            outline="#fbd38d", width=4)
            self._anim_temp.append(h)
            
            txt = self.canvas.create_text(x + self.cell_width / 2, self.start_y - 25,
                                         text=f"探测 {idx}", font=("Microsoft YaHei UI", 10, "bold"),
                                         fill="#fbd38d")
            self._anim_temp.append(txt)
            
            if i == 0:
                self.highlight_pseudocode(["INS_HASH"])
                self.update_explanation(f"散列地址 h({value}) = {init_idx}\n开始在位置 {idx} 探测...")
            else:
                self.highlight_pseudocode(["INS_LOOP", "INS_PROBE"])
                cell_val = self.model.table[idx]
                if cell_val is None:
                    self.update_explanation(f"位置 {idx} 为空，可以插入")
                elif cell_val is self.model.tombstone:
                    self.update_explanation(f"位置 {idx} 是墓碑标记，可以插入")
                else:
                    self.update_explanation(f"位置 {idx} 已有元素 {cell_val}\n发生冲突，继续探测下一位置...")
            
            self.update_status(f"探测位置 {idx}")
            current['i'] += 1
            self.window.after(step_delay, highlight_step)

        self.window.after(200, highlight_step)

    def _do_insert_animation(self, value, target_idx, final_table):
        self.highlight_pseudocode(["INS_DO"])
        
        # 自动滚动到目标单元格
        self._scroll_to_cell(target_idx)
        
        tgt_x = self.start_x + target_idx * (self.cell_width + self.spacing) + self.cell_width / 2
        start_y = self.start_y - 60
        tgt_y = self.start_y + self.cell_height / 2
        
        tx = self.canvas.create_text(tgt_x, start_y, text=str(value),
                                    font=("Arial", 14, "bold"), fill="#68d391")
        self._anim_temp.append(tx)
        
        steps = 15
        dy = (tgt_y - start_y) / steps
        step = {'i': 0}

        def move_step():
            if step['i'] >= steps:
                self._clear_temp_graphics()
                self.model.table = list(final_table)
                self.model.size = sum(1 for v in self.model.table if v is not None and v is not TOMBSTONE)
                self.update_display()
                
                x = self.start_x + target_idx * (self.cell_width + self.spacing)
                h = self.canvas.create_rectangle(x, self.start_y, x + self.cell_width,
                                                self.start_y + self.cell_height,
                                                outline="#68d391", width=4)
                self._anim_temp.append(h)
                
                self.highlight_pseudocode(["INS_END"])
                self.update_status(f"✓ 插入成功: {value} @ {target_idx}")
                
                self.window.after(600, self._finish_animation)
                return
            
            try:
                self.canvas.move(tx, 0, dy)
            except:
                pass
            step['i'] += 1
            self.window.after(30, move_step)

        move_step()

    def _insert_chain_animated_after_hash(self, value):
        """拉链法插入动画（哈希计算后调用）"""
        idx = self.model._hash(value)
        chain = self.model.table[idx]
        exists = value in chain
        
        self.update_display()
        
        # 自动滚动到目标桶
        self._scroll_to_cell(idx)
        
        x = self.start_x + idx * (self.cell_width + self.spacing)
        h = self.canvas.create_rectangle(x, self.start_y, x + self.cell_width,
                                        self.start_y + self.cell_height,
                                        outline="#fbd38d", width=4)
        self._anim_temp.append(h)
        
        self.highlight_pseudocode(["INS_HASH"])
        chain_info = f"链表长度: {len(chain)}" if chain else "链表为空"
        self.update_explanation(f"散列地址 h({value}) = {idx}\n定位到桶 {idx}，{chain_info}")
        self.update_status(f"定位到桶 {idx}")
        
        def check_chain():
            self._clear_temp_graphics()
            
            if exists:
                self.highlight_pseudocode(["INS_EXISTS"])
                self.update_explanation(f"遍历链表发现 {value} 已存在\n无需重复插入")
                self.update_status(f"✗ 值 {value} 已存在")
                self._finish_animation()
                return
            
            self.model.insert(value)
            self.update_display()
            
            self.highlight_pseudocode(["INS_END"])
            self.update_explanation(f"链表中未找到 {value}\n将新节点添加到链表末尾")
            self.update_status(f"✓ 插入成功: {value} @ 桶 {idx}")
            
            self.window.after(600, self._finish_animation)
        
        self.window.after(500, check_chain)

    def find_value(self, value):
        if self.animating:
            return

        self.animating = True
        self._set_buttons_state("disabled")
        self._clear_temp_graphics()
        self.update_display()
        
        self.highlight_pseudocode(["FIND_START"])
        self.update_status(f"▶ 开始查找: {value}")
        self.update_explanation(f"准备查找键值 {value}\n首先计算散列地址...")

        found, probe_path, chain_pos = self.model.find(value)

        # 先显示哈希计算过程，然后进行查找动画
        def after_hash_calc():
            self._clear_temp_graphics()
            if self.method == CollisionMethod.OPEN_ADDRESSING:
                self._find_open_animated_after_hash(value, found, probe_path)
            else:
                self._find_chain_animated_after_hash(value, found, probe_path, chain_pos)
        
        self._show_hash_calculation_animation(value, after_hash_calc, operation="查找")

    def _find_open_animated_after_hash(self, value, found, probe_path):
        """开放寻址法查找动画（哈希计算后调用）"""
        if not probe_path:
            self.update_status(f"✗ 未找到 {value}")
            self._finish_animation()
            return

        self.update_display()
        init_idx = self.model._hash(value)

        step_delay = 400
        current = {'i': 0}

        def highlight_step():
            i = current['i']
            self._clear_temp_graphics()

            if i >= len(probe_path):
                if found:
                    last_idx = probe_path[-1]
                    # 自动滚动到找到的位置
                    self._scroll_to_cell(last_idx)
                    x = self.start_x + last_idx * (self.cell_width + self.spacing)
                    
                    # 增强的成功视觉效果 - 多层高亮
                    glow = self.canvas.create_rectangle(
                        x - 6, self.start_y - 6, 
                        x + self.cell_width + 6, self.start_y + self.cell_height + 6,
                        outline="#2f855a", width=3)
                    self._anim_temp.append(glow)
                    
                    h = self.canvas.create_rectangle(x, self.start_y, x + self.cell_width,
                                                    self.start_y + self.cell_height,
                                                    outline="#68d391", fill="#c6f6d5", width=5)
                    self._anim_temp.append(h)
                    
                    # 重新绘制值文本（确保可见）
                    val_txt = self.canvas.create_text(
                        x + self.cell_width / 2, self.start_y + self.cell_height / 2,
                        text=str(value), font=("Consolas", 14, "bold"), fill="#22543d")
                    self._anim_temp.append(val_txt)
                    
                    # 成功标记
                    success_txt = self.canvas.create_text(
                        x + self.cell_width / 2, self.start_y - 35,
                        text="✓ 找到!", font=("Microsoft YaHei UI", 14, "bold"), fill="#38a169")
                    self._anim_temp.append(success_txt)
                    
                    # 结果框
                    result_bg = self.canvas.create_rectangle(
                        x - 30, self.start_y + self.cell_height + 15,
                        x + self.cell_width + 30, self.start_y + self.cell_height + 55,
                        fill="#276749", outline="#68d391", width=2)
                    self._anim_temp.append(result_bg)
                    
                    result_txt = self.canvas.create_text(
                        x + self.cell_width / 2, self.start_y + self.cell_height + 35,
                        text=f"查找成功: {value} 在位置 {last_idx}",
                        font=("Microsoft YaHei UI", 10, "bold"), fill="white")
                    self._anim_temp.append(result_txt)
                    
                    self.highlight_pseudocode(["FIND_FOUND"])
                    self.update_explanation(f"🎉 查找成功！\n\n在位置 {last_idx} 找到目标值 {value}")
                    self.update_status(f"✓ 查找成功: {value} 在位置 {last_idx}")
                else:
                    # 增强的失败视觉效果
                    last_idx = probe_path[-1] if probe_path else 0
                    self._scroll_to_cell(last_idx)
                    x = self.start_x + last_idx * (self.cell_width + self.spacing)
                    
                    # 红色高亮表示未找到
                    h = self.canvas.create_rectangle(x, self.start_y, x + self.cell_width,
                                                    self.start_y + self.cell_height,
                                                    outline="#fc8181", width=4)
                    self._anim_temp.append(h)
                    
                    # 失败标记
                    fail_txt = self.canvas.create_text(
                        x + self.cell_width / 2, self.start_y - 35,
                        text="✗ 未找到", font=("Microsoft YaHei UI", 14, "bold"), fill="#e53e3e")
                    self._anim_temp.append(fail_txt)
                    
                    # 结果框
                    result_bg = self.canvas.create_rectangle(
                        x - 30, self.start_y + self.cell_height + 15,
                        x + self.cell_width + 30, self.start_y + self.cell_height + 55,
                        fill="#742a2a", outline="#fc8181", width=2)
                    self._anim_temp.append(result_bg)
                    
                    result_txt = self.canvas.create_text(
                        x + self.cell_width / 2, self.start_y + self.cell_height + 35,
                        text=f"查找失败: {value} 不存在",
                        font=("Microsoft YaHei UI", 10, "bold"), fill="white")
                    self._anim_temp.append(result_txt)
                    
                    self.highlight_pseudocode(["FIND_END"])
                    self.update_explanation(f"❌ 查找失败！\n\n遇到空位置，停止查找\n表中不存在键值 {value}")
                    self.update_status(f"✗ 查找失败: {value} 不存在于散列表中")
                
                self.window.after(1500, self._finish_animation)
                return

            idx = probe_path[i]
            # 自动滚动到当前检查的单元格
            self._scroll_to_cell(idx)
            
            x = self.start_x + idx * (self.cell_width + self.spacing)
            
            h = self.canvas.create_rectangle(x, self.start_y, x + self.cell_width,
                                            self.start_y + self.cell_height,
                                            outline="#fbd38d", width=4)
            self._anim_temp.append(h)
            
            txt = self.canvas.create_text(x + self.cell_width / 2, self.start_y - 25,
                                         text=f"检查 {idx}", font=("Microsoft YaHei UI", 10, "bold"),
                                         fill="#fbd38d")
            self._anim_temp.append(txt)

            cell_val = self.model.table[idx]
            if i == 0:
                self.highlight_pseudocode(["FIND_HASH", "FIND_LOOP"])
                self.update_explanation(f"散列地址 h({value}) = {init_idx}\n开始在位置 {idx} 查找...")
            else:
                self.highlight_pseudocode(["FIND_LOOP", "FIND_PROBE"])
                
            # 显示当前位置的状态
            if cell_val is None:
                self.update_explanation(f"位置 {idx} 为空\n目标元素不存在")
            elif cell_val is self.model.tombstone:
                self.update_explanation(f"位置 {idx} 是墓碑标记\n跳过，继续查找...")
            elif cell_val == value:
                self.highlight_pseudocode(["FIND_CHECK"])
                self.update_explanation(f"位置 {idx} 的值 = {cell_val}\n与目标 {value} 匹配！")
            else:
                self.update_explanation(f"位置 {idx} 的值 = {cell_val}\n与目标 {value} 不匹配，继续探测...")
            
            self.update_status(f"检查位置 {idx}")

            current['i'] += 1
            self.window.after(step_delay, highlight_step)

        self.window.after(200, highlight_step)

    def _find_chain_animated_after_hash(self, value, found, probe_path, chain_pos):
        """拉链法查找动画（哈希计算后调用）"""
        if not probe_path:
            self.update_status(f"✗ 未找到 {value}")
            self._finish_animation()
            return

        idx = probe_path[0]
        chain = self.model.table[idx] if idx < len(self.model.table) else []

        self.update_display()

        # 自动滚动到目标桶
        self._scroll_to_cell(idx)

        x = self.start_x + idx * (self.cell_width + self.spacing)
        h = self.canvas.create_rectangle(x, self.start_y, x + self.cell_width,
                                        self.start_y + self.cell_height,
                                        outline="#fbd38d", width=4)
        self._anim_temp.append(h)

        self.highlight_pseudocode(["FIND_HASH"])
        chain_info = f"链表长度: {len(chain)}" if chain else "链表为空"
        self.update_explanation(f"散列地址 h({value}) = {idx}\n定位到桶 {idx}，{chain_info}")
        self.update_status(f"定位到桶 {idx}")

        # 如果链表为空，直接结束
        if not chain:
            def finish_empty():
                self._clear_temp_graphics()
                
                # 红色高亮表示未找到
                h = self.canvas.create_rectangle(x, self.start_y, x + self.cell_width,
                                                self.start_y + self.cell_height,
                                                outline="#fc8181", width=4)
                self._anim_temp.append(h)
                
                # 失败标记
                fail_txt = self.canvas.create_text(
                    x + self.cell_width / 2, self.start_y - 35,
                    text="✗ 未找到", font=("Microsoft YaHei UI", 14, "bold"), fill="#e53e3e")
                self._anim_temp.append(fail_txt)
                
                # 结果框
                result_bg = self.canvas.create_rectangle(
                    x - 30, self.start_y + self.cell_height + 15,
                    x + self.cell_width + 30, self.start_y + self.cell_height + 55,
                    fill="#742a2a", outline="#fc8181", width=2)
                self._anim_temp.append(result_bg)
                
                result_txt = self.canvas.create_text(
                    x + self.cell_width / 2, self.start_y + self.cell_height + 35,
                    text=f"查找失败: {value} 不存在",
                    font=("Microsoft YaHei UI", 10, "bold"), fill="white")
                self._anim_temp.append(result_txt)
                
                self.highlight_pseudocode(["FIND_END"])
                self.update_explanation(f"❌ 查找失败！\n\n桶 {idx} 的链表为空\n目标元素 {value} 不存在")
                self.update_status(f"✗ 查找失败: {value} 不存在于散列表中")
                self.window.after(1200, self._finish_animation)
            self.window.after(600, finish_empty)
            return

        # 遍历链表的动画
        current = {'pos': 0}
        step_delay = 400

        def traverse_chain():
            pos = current['pos']
            self._clear_temp_graphics()
            
            # 重新绘制桶的高亮
            h = self.canvas.create_rectangle(x, self.start_y, x + self.cell_width,
                                            self.start_y + self.cell_height,
                                            outline="#fbd38d", width=4)
            self._anim_temp.append(h)
            
            if pos >= len(chain):
                # 遍历完毕，未找到 - 增强视觉效果
                self._clear_temp_graphics()
                
                # 红色高亮桶
                h = self.canvas.create_rectangle(x, self.start_y, x + self.cell_width,
                                                self.start_y + self.cell_height,
                                                outline="#fc8181", width=4)
                self._anim_temp.append(h)
                
                # 失败标记
                fail_txt = self.canvas.create_text(
                    x + self.cell_width / 2, self.start_y - 35,
                    text="✗ 未找到", font=("Microsoft YaHei UI", 14, "bold"), fill="#e53e3e")
                self._anim_temp.append(fail_txt)
                
                # 结果框
                result_bg = self.canvas.create_rectangle(
                    x - 30, self.start_y + self.cell_height + len(chain) * 35 + 25,
                    x + self.cell_width + 30, self.start_y + self.cell_height + len(chain) * 35 + 65,
                    fill="#742a2a", outline="#fc8181", width=2)
                self._anim_temp.append(result_bg)
                
                result_txt = self.canvas.create_text(
                    x + self.cell_width / 2, self.start_y + self.cell_height + len(chain) * 35 + 45,
                    text=f"查找失败: {value} 不存在",
                    font=("Microsoft YaHei UI", 10, "bold"), fill="white")
                self._anim_temp.append(result_txt)
                
                self.highlight_pseudocode(["FIND_END"])
                self.update_explanation(f"❌ 查找失败！\n\n遍历完链表，未找到 {value}\n目标元素不存在于桶 {idx}")
                self.update_status(f"✗ 查找失败: {value} 不存在于散列表中")
                self.window.after(1200, self._finish_animation)
                return
            
            current_val = chain[pos]
            
            # 高亮当前链表节点
            node_x = x + self.cell_width / 2
            node_y = self.start_y + self.cell_height + 10 + pos * 35
            
            node_highlight = self.canvas.create_rectangle(
                node_x - 27, node_y - 2,
                node_x + 27, node_y + 30,
                outline="#63b3ed", width=3
            )
            self._anim_temp.append(node_highlight)
            
            check_txt = self.canvas.create_text(
                node_x + 45, node_y + 14,
                text=f"← 检查",
                font=("Microsoft YaHei UI", 9, "bold"),
                fill="#63b3ed"
            )
            self._anim_temp.append(check_txt)
            
            self.highlight_pseudocode(["FIND_LOOP", "FIND_CHECK"])
            
            if current_val == value:
                # 找到了 - 增强成功视觉效果
                self._clear_temp_graphics()
                
                # 绿色高亮桶
                glow = self.canvas.create_rectangle(
                    x - 6, self.start_y - 6, 
                    x + self.cell_width + 6, self.start_y + self.cell_height + 6,
                    outline="#2f855a", width=3)
                self._anim_temp.append(glow)
                
                h = self.canvas.create_rectangle(x, self.start_y, x + self.cell_width,
                                                self.start_y + self.cell_height,
                                                outline="#68d391", fill="#c6f6d5", width=5)
                self._anim_temp.append(h)
                
                # 高亮找到的链表节点
                node_highlight = self.canvas.create_rectangle(
                    node_x - 30, node_y - 5,
                    node_x + 30, node_y + 33,
                    outline="#68d391", fill="#c6f6d5", width=3)
                self._anim_temp.append(node_highlight)
                
                # 重绘节点值
                node_val_txt = self.canvas.create_text(
                    node_x, node_y + 14,
                    text=str(value), font=("Consolas", 12, "bold"), fill="#22543d")
                self._anim_temp.append(node_val_txt)
                
                # 成功标记
                success_txt = self.canvas.create_text(
                    x + self.cell_width / 2, self.start_y - 35,
                    text="✓ 找到!", font=("Microsoft YaHei UI", 14, "bold"), fill="#38a169")
                self._anim_temp.append(success_txt)
                
                # 结果框
                result_bg = self.canvas.create_rectangle(
                    x - 40, node_y + 45,
                    x + self.cell_width + 40, node_y + 85,
                    fill="#276749", outline="#68d391", width=2)
                self._anim_temp.append(result_bg)
                
                result_txt = self.canvas.create_text(
                    x + self.cell_width / 2, node_y + 65,
                    text=f"查找成功: {value} 在桶{idx}[{pos}]",
                    font=("Microsoft YaHei UI", 10, "bold"), fill="white")
                self._anim_temp.append(result_txt)
                
                self.highlight_pseudocode(["FIND_FOUND"])
                self.update_explanation(f"🎉 查找成功！\n\n链表位置 {pos}: 值 = {current_val}\n与目标 {value} 匹配！")
                self.update_status(f"✓ 查找成功: {value} 在桶{idx}的链表位置[{pos}]")
                
                self.window.after(1500, self._finish_animation)
                return
            else:
                # 继续查找
                self.update_explanation(f"链表位置 {pos}: 值 = {current_val}\n与目标 {value} 不匹配，继续...")
                self.update_status(f"检查链表节点 [{pos}] = {current_val}")
                current['pos'] += 1
                self.window.after(step_delay, traverse_chain)
        
        self.window.after(600, traverse_chain)

    def delete_value(self, value):
        if self.animating:
            return

        self.highlight_pseudocode(["DEL_START"])
        self.update_status(f"▶ 开始删除: {value}")

        if self.method == CollisionMethod.OPEN_ADDRESSING:
            self._delete_open_animated(value)
        else:
            self._delete_chain_animated(value)

    def _delete_open_animated(self, value):
        found, probe_path, _ = self.model.find(value)

        self.animating = True
        self._set_buttons_state("disabled")
        self._clear_temp_graphics()
        self.update_display()

        if not probe_path or not found:
            self.highlight_pseudocode(["DEL_NOTFOUND"])
            self.update_status(f"✗ 未找到 {value}")
            self.window.after(600, self._finish_animation)
            return

        target_idx = probe_path[-1]
        # 自动滚动到要删除的单元格
        self._scroll_to_cell(target_idx)
        
        x = self.start_x + target_idx * (self.cell_width + self.spacing)
        
        h = self.canvas.create_rectangle(x, self.start_y, x + self.cell_width,
                                        self.start_y + self.cell_height,
                                        outline="#fc8181", width=5)
        self._anim_temp.append(h)
        
        self.highlight_pseudocode(["DEL_TOMB"])
        self.update_status(f"删除位置 {target_idx}")
        
        def do_delete():
            self.model.delete(value)
            self._clear_temp_graphics()
            self.update_display()
            
            self.highlight_pseudocode(["DEL_END"])
            self.update_status(f"✓ 删除成功: {value}")
            
            self.window.after(600, self._finish_animation)
        
        self.window.after(500, do_delete)

    def _delete_chain_animated(self, value):
        found, probe_path, chain_pos = self.model.find(value)

        self.animating = True
        self._set_buttons_state("disabled")
        self._clear_temp_graphics()
        self.update_display()

        if not probe_path or not found:
            self.highlight_pseudocode(["DEL_NOTFOUND"])
            self.update_status(f"✗ 未找到 {value}")
            self.window.after(600, self._finish_animation)
            return

        idx = probe_path[0]
        # 自动滚动到要删除的桶
        self._scroll_to_cell(idx)
        
        x = self.start_x + idx * (self.cell_width + self.spacing)
        
        h = self.canvas.create_rectangle(x, self.start_y, x + self.cell_width,
                                        self.start_y + self.cell_height,
                                        outline="#fc8181", width=4)
        self._anim_temp.append(h)

        self.highlight_pseudocode(["DEL_FIND"])
        self.update_status(f"找到 {value} @ 桶 {idx}")

        def do_delete():
            self.model.delete(value)
            self._clear_temp_graphics()
            self.update_display()
            
            self.highlight_pseudocode(["DEL_END"])
            self.update_status(f"✓ 删除成功: {value}")
            
            self._finish_animation()
        
        self.window.after(500, do_delete)

    def _clear_temp_graphics(self):
        for item in self._anim_temp:
            try:
                self.canvas.delete(item)
            except:
                pass
        self._anim_temp = []

    def _scroll_to_cell(self, cell_index):
        """自动滚动画布，使指定索引的单元格居中显示"""
        if not self._auto_scroll_enabled:
            return
        
        # 计算单元格中心的x坐标
        cell_center_x = self.start_x + cell_index * (self.cell_width + self.spacing) + self.cell_width / 2
        
        # 获取画布可见区域的宽度
        canvas_width = self.canvas.winfo_width()
        if canvas_width <= 1:
            canvas_width = 800  # 默认值
        
        # 获取滚动区域的总宽度
        scroll_region = self.canvas.cget('scrollregion')
        if scroll_region:
            parts = scroll_region.split()
            if len(parts) >= 4:
                total_width = float(parts[2])
            else:
                total_width = self.start_x + self.capacity * (self.cell_width + self.spacing) + 50
        else:
            total_width = self.start_x + self.capacity * (self.cell_width + self.spacing) + 50
        
        # 计算目标滚动位置（使单元格居中）
        target_x = cell_center_x - canvas_width / 2
        
        # 限制在有效范围内
        target_x = max(0, min(target_x, total_width - canvas_width))
        
        # 转换为滚动比例 (0.0 - 1.0)
        if total_width > canvas_width:
            scroll_fraction = target_x / (total_width - canvas_width)
            scroll_fraction = max(0.0, min(1.0, scroll_fraction))
            self.canvas.xview_moveto(scroll_fraction)
        else:
            # 如果内容小于画布，不需要滚动
            self.canvas.xview_moveto(0)

    def _get_hash_calculation_display(self, value):
        """获取哈希计算的详细显示信息"""
        hash_expr = self.model.hash_expr
        hash_result = self.model._hash(value)
        
        # 替换表达式中的变量以显示实际计算过程
        display_expr = hash_expr.replace("capacity", str(self.capacity))
        display_expr = display_expr.replace("x", str(value))
        display_expr = display_expr.replace("X", str(value))
        
        return {
            'value': value,
            'expr': hash_expr,
            'display_expr': display_expr,
            'result': hash_result
        }

    def _show_hash_calculation_animation(self, value, callback, operation="计算"):
        """显示哈希计算过程的简洁动画 - 漂浮显示计算式然后淡出"""
        calc_info = self._get_hash_calculation_display(value)
        
        # 计算显示位置 - 在目标单元格上方
        target_idx = calc_info['result']
        cell_x = self.start_x + target_idx * (self.cell_width + self.spacing) + self.cell_width / 2
        start_y = self.start_y - 80
        
        # 滚动到目标位置
        self._scroll_to_cell(target_idx)
        
        # 构建计算式: h(23) = 23 % 11 = 1
        calc_text = f"h({value}) = {calc_info['display_expr']} = {calc_info['result']}"
        
        # 创建漂浮的计算式文本
        txt = self.canvas.create_text(
            cell_x, start_y,
            text=calc_text,
            font=("Consolas", 12, "bold"),
            fill="#fbd38d"
        )
        self._anim_temp.append(txt)
        
        # 更新解释区域
        self.update_explanation(f"计算散列地址: {calc_text}")
        self.highlight_pseudocode(["INS_HASH"] if operation == "插入" else ["FIND_HASH"])
        
        # 淡出动画
        fade_steps = 8
        current = {'step': 0, 'alpha': 255}
        
        # 颜色渐变序列 (从亮黄到暗)
        colors = ["#fbd38d", "#e9c17a", "#d7af67", "#c59d54", "#b38b41", "#a1792e", "#8f671b", "#7d5508"]
        
        def fade_step():
            if current['step'] >= fade_steps:
                # 动画完成，回调
                callback()
                return
            
            # 更新文本颜色实现淡出效果
            try:
                self.canvas.itemconfig(txt, fill=colors[current['step']])
            except:
                pass
            
            current['step'] += 1
            self.window.after(80, fade_step)
        
        # 显示一段时间后开始淡出
        self.window.after(600, fade_step)

    def _finish_animation(self):
        self._clear_temp_graphics()
        self.animating = False
        self._set_buttons_state("normal")
        
        if self.batch_queue and self.batch_index < len(self.batch_queue):
            self.window.after(300, self._batch_step)

    def clear_table(self):
        if self.animating:
            return
        self.model.clear()
        self.update_display()
        self.highlight_pseudocode([])
        self.update_status("✓ 散列表已清空")
    
    def set_chat_window(self, chat_window):
        """设置LLM聊天窗口引用"""
        self.chat_window = chat_window

    def _batch_step(self):
        if self.batch_index >= len(self.batch_queue):
            self.batch_queue = []
            self.batch_index = 0
            self._set_buttons_state("normal")
            self.update_status("✓ 批量插入完成")
            return
        
        val = self.batch_queue[self.batch_index]
        self.batch_index += 1
        self.insert_value(val)

    def update_display(self):
        self.canvas.delete("all")
        self.cell_rects.clear()
        self.cell_texts.clear()
        self.index_texts.clear()
        self.chain_elements.clear()

        self._draw_background()
        self._draw_info()

        if self.method == CollisionMethod.OPEN_ADDRESSING:
            self._draw_open_addressing()
        else:
            self._draw_chaining()
        
        # 更新画布滚动区域，确保可以滚动查看所有内容
        total_width = self.start_x + self.capacity * (self.cell_width + self.spacing) + 50
        total_height = self.canvas.winfo_height() or 500
        if self.method == CollisionMethod.CHAINING:
            # 拉链法需要更多垂直空间
            max_chain = self.model.get_max_chain_length()
            total_height = max(total_height, self.start_y + self.cell_height + max_chain * 40 + 50)
        self.canvas.configure(scrollregion=(0, 0, total_width, total_height))

    def _draw_background(self):
        w = self.canvas.winfo_width() or 900
        h = self.canvas.winfo_height() or 500
        
        colors = ["#0a0f1a", "#0d1526", "#101b30"]
        step_h = h // len(colors)
        for i, color in enumerate(colors):
            self.canvas.create_rectangle(0, i * step_h, w, (i + 1) * step_h + 10,
                                        fill=color, outline="")
        
        for gx in range(0, w, 50):
            self.canvas.create_line(gx, 0, gx, h, fill="#151f35")
        for gy in range(0, h, 50):
            self.canvas.create_line(0, gy, w, gy, fill="#151f35")

    def _draw_info(self):
        info_x, info_y = 20, 15
        
        method_name = "开放寻址法" if self.method == CollisionMethod.OPEN_ADDRESSING else "拉链法"
        self.canvas.create_text(info_x, info_y, text=f"📊 {method_name}",
                               anchor="w", font=("Microsoft YaHei UI", 12, "bold"),
                               fill="#4fd1c5")
        
        stats = f"容量: {self.capacity} | 元素: {len(self.model)}"
        self.canvas.create_text(info_x, info_y + 22, text=stats,
                               anchor="w", font=("Microsoft YaHei UI", 9),
                               fill="#a0aec0")
        
        hash_display = self.model.get_hash_display()
        self.canvas.create_text(info_x, info_y + 42, text=hash_display,
                               anchor="w", font=("Consolas", 9, "bold"),
                               fill="#68d391")

    def _draw_open_addressing(self):
        for i in range(self.capacity):
            x = self.start_x + i * (self.cell_width + self.spacing)
            
            val = self.model.table[i]
            if val is None:
                fill = "#1a2744"
                outline = "#2d3748"
            elif val is self.model.tombstone:
                fill = "#2d2d2d"
                outline = "#4a4a4a"
            else:
                fill = "#1e3a5f"
                outline = "#4fd1c5"
            
            rect = self.canvas.create_rectangle(x, self.start_y,
                                                x + self.cell_width,
                                                self.start_y + self.cell_height,
                                                fill=fill, outline=outline, width=2)
            self.cell_rects.append(rect)

            idx_txt = self.canvas.create_text(x + self.cell_width / 2,
                                              self.start_y - 15,
                                              text=str(i),
                                              font=("Consolas", 9, "bold"),
                                              fill="#718096")
            self.index_texts.append(idx_txt)

            if val is None:
                txt = ""
            elif val is self.model.tombstone:
                txt = "🪦"
            else:
                txt = str(val)
            
            cell_txt = self.canvas.create_text(x + self.cell_width / 2,
                                               self.start_y + self.cell_height / 2,
                                               text=txt, font=("Consolas", 12, "bold"),
                                               fill="#e2e8f0")
            self.cell_texts.append(cell_txt)

    def _draw_chaining(self):
        for i in range(self.capacity):
            x = self.start_x + i * (self.cell_width + self.spacing)
            
            chain = self.model.table[i]
            fill = "#1e3a5f" if chain else "#1a2744"
            outline = "#4fd1c5" if chain else "#2d3748"
            
            rect = self.canvas.create_rectangle(x, self.start_y,
                                                x + self.cell_width,
                                                self.start_y + self.cell_height,
                                                fill=fill, outline=outline, width=2)
            self.cell_rects.append(rect)

            idx_txt = self.canvas.create_text(x + self.cell_width / 2,
                                              self.start_y - 15,
                                              text=str(i),
                                              font=("Consolas", 9, "bold"),
                                              fill="#718096")
            self.index_texts.append(idx_txt)

            if not chain:
                cell_txt = self.canvas.create_text(x + self.cell_width / 2,
                                                   self.start_y + self.cell_height / 2,
                                                   text="∅", font=("Consolas", 12),
                                                   fill="#4a5568")
                self.cell_texts.append(cell_txt)
            else:
                self.canvas.create_text(x + self.cell_width / 2,
                                       self.start_y + self.cell_height / 2,
                                       text=f"[{len(chain)}]",
                                       font=("Consolas", 9),
                                       fill="#a0aec0")
                
                node_y = self.start_y + self.cell_height + 10
                for j, item in enumerate(chain):
                    node_x = x + self.cell_width / 2
                    node_rect = self.canvas.create_rectangle(
                        node_x - 25, node_y + j * 35,
                        node_x + 25, node_y + j * 35 + 28,
                        fill="#1a3a4a", outline="#38b2ac", width=2
                    )
                    node_txt = self.canvas.create_text(
                        node_x, node_y + j * 35 + 14,
                        text=str(item), font=("Consolas", 10, "bold"),
                        fill="#e2e8f0"
                    )
                    self.chain_elements.append((node_rect, node_txt))
                    
                    if j < len(chain) - 1:
                        self.canvas.create_line(
                            node_x, node_y + j * 35 + 28,
                            node_x, node_y + (j + 1) * 35,
                            arrow=LAST, fill="#38b2ac", width=2
                        )

    def _set_buttons_state(self, state):
        for w in self.left_panel.winfo_children():
            self._set_widget_state(w, state)

    def _set_widget_state(self, widget, state):
        try:
            widget.config(state=state)
        except:
            pass
        for child in widget.winfo_children():
            self._set_widget_state(child, state)

    def back_to_main(self):
        if self.animating:
            messagebox.showinfo("提示", "动画进行中，无法返回")
            return
        self.window.destroy()


if __name__ == "__main__":
    root = Tk()
    root.title("散列表可视化")
    root.geometry("1400x700")
    root.minsize(1200, 600)
    root.config(bg="#0a0f1a")
    
    HashtableVisualizer(root, capacity=11, method=CollisionMethod.OPEN_ADDRESSING)
    
    root.mainloop()
