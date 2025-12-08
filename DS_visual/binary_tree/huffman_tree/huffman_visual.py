from tkinter import *
from tkinter import messagebox, ttk, filedialog
from binary_tree.huffman_tree.huffman_model import HuffmanModel, HuffmanNode
from typing import Dict, Tuple, List, Optional
from collections import Counter
import math
import json
import os
import time
from datetime import datetime
# 假设您已有一个名为 storage.py 的文件，用于处理路径和文件操作
import storage as storage 

# ---- 现代配色方案 (Material / Pastel) ----
COLORS = {
    "bg": "#F4F7F6", "canvas_bg": "#FFFFFF", "grid": "#F0F2F5", "pool_bg": "#E8ECEF",
    "node_fill": "#FFFFFF", "node_border": "#455A64", "node_text": "#263238", "shadow": "#CFD8DC",
    "highlight_fill": "#FFF3E0", "highlight_border": "#FF9800",
    "line": "#B0BEC5", "line_active": "#546E7A",
    "math_text": "#1E88E5", "ripple": "#90CAF9",
    "bit_0": "#E53935", "bit_1": "#43A047", "photon": "#FFD600",
    # 新增教学动画颜色
    "compare_scan": "#9C27B0",  # 扫描比较时的颜色
    "min_found": "#4CAF50",     # 找到最小值时的颜色
    "merge_glow": "#FF5722",    # 合并时发光颜色
    "arrow": "#3F51B5",         # 箭头颜色
    "explanation_bg": "#1a1a2e", # 解释面板背景
    "step_bg": "#16213e",       # 步骤面板背景
    # 堆可视化颜色
    "heap_bg": "#1a1a2e",       # 堆面板背景
    "heap_node": "#2d3436",     # 堆节点填充
    "heap_border": "#00cec9",   # 堆节点边框
    "heap_text": "#dfe6e9",     # 堆节点文本
    "heap_line": "#636e72",     # 堆连线
    "heap_compare": "#fdcb6e",  # 比较时高亮
    "heap_swap": "#e17055",     # 交换时高亮
    "heap_sift_up": "#00b894",  # 上浮高亮
    "heap_sift_down": "#d63031", # 下沉高亮
    "heap_insert": "#6c5ce7",   # 插入高亮
    "heap_extract": "#e84393",  # 提取高亮
}

class HuffmanVisualizer:
    def __init__(self, root):
        self.window = root
        self.window.config(bg=COLORS["bg"])
        self.canvas_w = 900   
        self.canvas_h = 550
        
        # 绘图参数
        self.node_r = 22; self.node_d = 44
        self.pool_y = 80; self.tree_root_y = 160; self.level_h = 85       
        
        # 状态
        self.node_vis: Dict = {}  
        self.final_positions: Dict = {} 
        self.animating = False
        self.status_id = None
        
        # 伪代码相关变量
        self.pseudo_code_lines = []
        self.current_highlight_line = -1
        self.animation_speed = 1.0  # 动画速度倍率
        
        self.model = HuffmanModel()
        self.steps = []; self.snap_before = []; self.snap_after = []
        
        # 输入模式状态
        self.input_mode = StringVar(value="numeric")
        self.char_data = [] 
        
        # ========== 新增: 步进控制相关 ==========
        self.paused = False
        self.step_mode = False  # 单步模式
        self.next_step_event = None  # 用于单步触发
        self.current_step_idx = 0
        self.total_steps = 0
        
        # 教学解释文本
        self.explanation_items = []  # canvas上的解释文本项
        
        # ========== 新增: 堆可视化相关 ==========
        self.heap_vis: Dict = {}  # 堆节点可视化数据
        self.heap_state: List[float] = []  # 当前堆状态
        self.heap_operations_log = []  # 堆操作日志
        self.show_heap = True  # 是否显示堆可视化
        self.heap_node_r = 18  # 堆节点半径
        self.heap_canvas = None  # 堆画布

        # ---- 界面布局 ----
        # 首先创建底部输入面板（确保它总是可见）
        self._init_bottom_panel()
        
        # 主容器
        container = Frame(self.window, bg=COLORS["bg"])
        container.pack(fill=BOTH, expand=True, padx=15, pady=(10, 5))
        
        # 左侧：主画布 (恢复完整高度)
        left_frame = Frame(container, bg=COLORS["bg"])
        left_frame.pack(side=LEFT, fill=BOTH, expand=True)
        
        # 主画布 (Huffman树) - 完整尺寸
        self.canvas = Canvas(left_frame, bg=COLORS["canvas_bg"], width=self.canvas_w, height=self.canvas_h, bd=0, highlightthickness=0)
        self.canvas.pack(fill=BOTH, expand=True, padx=(0,10))
        
        # 右侧容器（伪代码面板 + 堆可视化 + 控制面板）
        right_container = Frame(container, bg=COLORS["bg"])
        right_container.pack(side=RIGHT, fill=Y)
        
        # 伪代码面板（上方）
        self._init_pseudo_code_panel(right_container)
        
        # 堆可视化面板（放在右侧，紧凑型）
        self._init_heap_panel(right_container)
        
        # 教学解释面板
        self._init_explanation_panel(right_container)
        
        # 控制面板（下方）
        right_frame = Frame(right_container, width=300, bg=COLORS["bg"])
        right_frame.pack(fill=X, pady=(5, 0))
        
        self._init_right_panel(right_frame)
        self._draw_background_elements()

    def _init_pseudo_code_panel(self, parent):
        """创建伪代码显示面板"""
        pseudo_frame = Frame(parent, bg="#2d3436", relief=RAISED, bd=2, width=300, height=220)
        pseudo_frame.pack(fill=X)
        pseudo_frame.pack_propagate(False)
        
        # 标题
        title_label = Label(pseudo_frame, text="📋 伪代码执行过程", 
                           font=("微软雅黑", 11, "bold"), 
                           bg="#2d3436", fg="#00cec9", pady=5)
        title_label.pack(fill=X)
        
        # 分隔线
        separator = Frame(pseudo_frame, height=2, bg="#00cec9")
        separator.pack(fill=X, padx=10, pady=(0, 3))
        
        # 当前操作标签
        self.operation_label = Label(pseudo_frame, text="等待操作...", 
                                     font=("微软雅黑", 9), 
                                     bg="#2d3436", fg="#dfe6e9", 
                                     wraplength=280, justify=LEFT)
        self.operation_label.pack(fill=X, padx=10, pady=3)
        
        # 伪代码显示区域
        code_container = Frame(pseudo_frame, bg="#1e272e")
        code_container.pack(fill=BOTH, expand=True, padx=8, pady=5)
        
        self.pseudo_text = Text(code_container, 
                               font=("Consolas", 9), 
                               bg="#1e272e", fg="#b2bec3",
                               relief=FLAT, 
                               wrap=WORD,
                               padx=6, pady=4,
                               cursor="arrow",
                               state=DISABLED,
                               height=6,
                               width=34)
        self.pseudo_text.pack(fill=BOTH, expand=True)
        
        # 配置高亮标签样式
        self.pseudo_text.tag_configure("highlight", 
                                       background="#00b894", 
                                       foreground="#ffffff",
                                       font=("Consolas", 9, "bold"))
        self.pseudo_text.tag_configure("executed", 
                                       foreground="#55efc4")
        self.pseudo_text.tag_configure("pending", 
                                       foreground="#636e72")
        
        # 进度指示器
        progress_frame = Frame(pseudo_frame, bg="#2d3436")
        progress_frame.pack(fill=X, padx=10, pady=(0, 5))
        
        self.progress_label = Label(progress_frame, text="步骤: 0/0", 
                                    font=("Arial", 8), 
                                    bg="#2d3436", fg="#b2bec3")
        self.progress_label.pack(side=LEFT)
        
        self.status_indicator = Label(progress_frame, text="⚫ 空闲", 
                                      font=("Arial", 8), 
                                      bg="#2d3436", fg="#b2bec3")
        self.status_indicator.pack(side=RIGHT)

    def _init_explanation_panel(self, parent):
        """创建教学解释面板 - 为初学者提供详细解释"""
        explain_frame = Frame(parent, bg=COLORS["explanation_bg"], relief=RAISED, bd=2, width=300, height=140)
        explain_frame.pack(fill=X, pady=(5, 0))
        explain_frame.pack_propagate(False)
        
        # 标题
        Label(explain_frame, text="💡 当前操作详解", 
              font=("微软雅黑", 10, "bold"), 
              bg=COLORS["explanation_bg"], fg="#ffd700", pady=3).pack(fill=X)
        
        # 分隔线
        Frame(explain_frame, height=2, bg="#ffd700").pack(fill=X, padx=10, pady=(0, 5))
        
        # 解释文本区域
        self.explain_text = Text(explain_frame,
                                font=("微软雅黑", 9),
                                bg="#0f0f23", fg="#cccccc",
                                relief=FLAT,
                                wrap=WORD,
                                padx=6, pady=4,
                                cursor="arrow",
                                state=DISABLED,
                                height=4,
                                width=34)
        self.explain_text.pack(fill=BOTH, expand=True, padx=8, pady=(0, 8))
        
        # 配置样式标签
        self.explain_text.tag_configure("keyword", foreground="#ff79c6", font=("微软雅黑", 9, "bold"))
        self.explain_text.tag_configure("value", foreground="#50fa7b")
        self.explain_text.tag_configure("important", foreground="#ffb86c", font=("微软雅黑", 9, "bold"))
    
    def _init_heap_panel(self, parent):
        """初始化堆可视化面板 - 紧凑型，放在右侧"""
        heap_frame = Frame(parent, bg=COLORS["heap_bg"], relief=RAISED, bd=2, width=300, height=180)
        heap_frame.pack(fill=X, pady=(5, 0))
        heap_frame.pack_propagate(False)
        
        # 顶部标题栏
        title_bar = Frame(heap_frame, bg=COLORS["heap_bg"])
        title_bar.pack(fill=X, padx=8, pady=3)
        
        Label(title_bar, text="📊 最小堆", 
              font=("微软雅黑", 9, "bold"), 
              bg=COLORS["heap_bg"], fg="#00cec9").pack(side=LEFT)
        
        # 堆操作说明
        self.heap_op_label = Label(title_bar, text="等待...", 
                                   font=("微软雅黑", 8), 
                                   bg=COLORS["heap_bg"], fg="#ffeaa7",
                                   wraplength=150)
        self.heap_op_label.pack(side=RIGHT)
        
        # 分隔线
        Frame(heap_frame, height=1, bg="#00cec9").pack(fill=X, padx=8)
        
        # 堆画布 - 紧凑尺寸
        self.heap_canvas = Canvas(heap_frame, bg="#0f0f23", 
                                  width=280, height=110,
                                  bd=0, highlightthickness=0)
        self.heap_canvas.pack(padx=8, pady=5)
        
        # 堆数组显示
        array_frame = Frame(heap_frame, bg=COLORS["heap_bg"])
        array_frame.pack(fill=X, padx=8, pady=(0, 5))
        
        Label(array_frame, text="数组:", font=("Consolas", 8), 
              bg=COLORS["heap_bg"], fg="#b2bec3").pack(side=LEFT)
        
        self.heap_array_label = Label(array_frame, text="[ ]", 
                                      font=("Consolas", 8, "bold"),
                                      bg=COLORS["heap_bg"], fg="#74b9ff",
                                      wraplength=230)
        self.heap_array_label.pack(side=LEFT, padx=3)
        
        # 索引提示（隐藏，太占空间）
        self.heap_index_label = Label(array_frame, text="", 
                                      font=("Consolas", 7),
                                      bg=COLORS["heap_bg"], fg="#636e72")
        # 不pack，节省空间
    
    def set_explanation(self, text, keywords=None, values=None, important=None):
        """设置教学解释内容"""
        self.explain_text.config(state=NORMAL)
        self.explain_text.delete(1.0, END)
        self.explain_text.insert(END, text)
        
        # 高亮关键词
        if keywords:
            for kw in keywords:
                self._highlight_text_in_widget(self.explain_text, kw, "keyword")
        if values:
            for v in values:
                self._highlight_text_in_widget(self.explain_text, str(v), "value")
        if important:
            for imp in important:
                self._highlight_text_in_widget(self.explain_text, imp, "important")
        
        self.explain_text.config(state=DISABLED)
        self.window.update()
    
    def _highlight_text_in_widget(self, widget, text, tag):
        """在Text widget中高亮指定文本"""
        start = "1.0"
        while True:
            pos = widget.search(text, start, END)
            if not pos:
                break
            end = f"{pos}+{len(text)}c"
            widget.tag_add(tag, pos, end)
            start = end
    
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

    def _init_right_panel(self, parent):
        """ 初始化右侧控制面板和堆状态列表 """
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("HeapTree.Treeview", background="white", foreground="#37474F", rowheight=26, font=("Segoe UI", 9), borderwidth=0)
        style.configure("HeapTree.Treeview.Heading", font=("Segoe UI", 9, "bold"), background="#ECEFF1", foreground="#455A64")
        
        Label(parent, text="优先队列状态 (最小堆)", bg=COLORS["bg"], fg="#455A64", font=("Segoe UI", 10, "bold")).pack(anchor="nw", pady=(0,3))
        self.heap_tree = ttk.Treeview(parent, columns=("pool"), show="headings", style="HeapTree.Treeview", height=4)
        
        self.heap_tree.heading("pool", text="候选节点池 (按权值排序)")
        
        self.heap_tree.column("pool", width=280, anchor="center")
        self.heap_tree.pack(fill=X, pady=3)
        
        # ========== 新增: 步进控制面板 ==========
        step_frame = Frame(parent, bg=COLORS["step_bg"], relief=GROOVE, bd=2)
        step_frame.pack(fill=X, pady=5)
        
        Label(step_frame, text="🎮 动画控制", font=("微软雅黑", 9, "bold"),
              bg=COLORS["step_bg"], fg="#00cec9").pack(pady=3)
        
        # 控制按钮行
        ctrl_btn_frame = Frame(step_frame, bg=COLORS["step_bg"])
        ctrl_btn_frame.pack(fill=X, padx=5, pady=3)
        
        self.pause_btn = Button(ctrl_btn_frame, text="⏸ 暂停", command=self.toggle_pause,
                                bg="#ff7675", fg="white", font=("Segoe UI", 9, "bold"),
                                bd=0, padx=8, pady=3, cursor="hand2")
        self.pause_btn.pack(side=LEFT, padx=2)
        
        self.step_btn = Button(ctrl_btn_frame, text="⏭ 下一步", command=self.do_next_step,
                               bg="#74b9ff", fg="white", font=("Segoe UI", 9, "bold"),
                               bd=0, padx=8, pady=3, cursor="hand2")
        self.step_btn.pack(side=LEFT, padx=2)
        
        self.auto_btn = Button(ctrl_btn_frame, text="▶ 自动", command=self.set_auto_mode,
                               bg="#55efc4", fg="#2d3436", font=("Segoe UI", 9, "bold"),
                               bd=0, padx=8, pady=3, cursor="hand2")
        self.auto_btn.pack(side=LEFT, padx=2)
        
        # 速度控制
        speed_frame = Frame(step_frame, bg=COLORS["step_bg"])
        speed_frame.pack(fill=X, padx=5, pady=3)
        
        Label(speed_frame, text="速度:", font=("Segoe UI", 8),
              bg=COLORS["step_bg"], fg="#b2bec3").pack(side=LEFT)
        
        self.speed_var = DoubleVar(value=1.0)
        self.speed_scale = Scale(speed_frame, from_=0.25, to=3.0, resolution=0.25,
                                 orient=HORIZONTAL, variable=self.speed_var,
                                 length=150, bg=COLORS["step_bg"], fg="#b2bec3",
                                 highlightthickness=0, troughcolor="#2d3436",
                                 command=self._on_speed_change)
        self.speed_scale.pack(side=LEFT, padx=5)
        
        self.speed_label = Label(speed_frame, text="1.0x", font=("Consolas", 9),
                                 bg=COLORS["step_bg"], fg="#ffeaa7")
        self.speed_label.pack(side=LEFT)
        
        # 步骤进度
        self.step_progress_label = Label(step_frame, text="合并步骤: 0/0",
                                         font=("Segoe UI", 9),
                                         bg=COLORS["step_bg"], fg="#dfe6e9")
        self.step_progress_label.pack(pady=3)
        
        btn_frame = Frame(parent, bg=COLORS["bg"])
        btn_frame.pack(fill=X, pady=5)
        self._make_btn(btn_frame, "清空重置", self.clear_canvas, "#FFCC80", "#E65100").pack(fill=X, pady=2)
        
        io_frame = Frame(btn_frame, bg=COLORS["bg"])
        io_frame.pack(fill=X, pady=2)
        self._make_btn(io_frame, "保存树", self.save_tree, "#90CAF9", "#1565C0").pack(side=LEFT, fill=X, expand=True, padx=(0,2))
        self._make_btn(io_frame, "加载树", self.load_tree, "#90CAF9", "#1565C0").pack(side=RIGHT, fill=X, expand=True, padx=(2,0))
        self._make_btn(btn_frame, "退出程序", self.back_to_main, "#CFD8DC", "#455A64").pack(fill=X, pady=2)

    def _on_speed_change(self, val):
        """速度滑块变化回调"""
        self.animation_speed = float(val)
        self.speed_label.config(text=f"{float(val):.2f}x")
    
    def toggle_pause(self):
        """切换暂停状态"""
        self.paused = not self.paused
        if self.paused:
            self.pause_btn.config(text="▶ 继续", bg="#55efc4", fg="#2d3436")
            self.step_mode = True
            self.status_indicator.config(text="⏸ 已暂停", fg="#ffeaa7")
        else:
            self.pause_btn.config(text="⏸ 暂停", bg="#ff7675", fg="white")
            self.step_mode = False
            self.status_indicator.config(text="🟢 执行中", fg="#00b894")
            # 继续动画
            if self.next_step_event:
                self.next_step_event()
    
    def do_next_step(self):
        """执行下一步 (单步模式)"""
        if not self.animating:
            return
        self.paused = True
        self.step_mode = True
        self.pause_btn.config(text="▶ 继续", bg="#55efc4", fg="#2d3436")
        if self.next_step_event:
            self.next_step_event()
    
    def set_auto_mode(self):
        """设置自动模式"""
        self.paused = False
        self.step_mode = False
        self.pause_btn.config(text="⏸ 暂停", bg="#ff7675", fg="white")
        self.status_indicator.config(text="🟢 执行中", fg="#00b894")
        if self.next_step_event:
            self.next_step_event()
    
    def _schedule_next(self, callback, delay_ms):
        """调度下一个动画步骤，考虑暂停和速度"""
        adjusted_delay = int(delay_ms / self.animation_speed)
        
        def wrapper():
            if not self.animating:
                return
            if self.paused and self.step_mode:
                # 暂停模式：保存回调等待手动触发
                self.next_step_event = callback
                return
            callback()
        
        self.window.after(adjusted_delay, wrapper)

    def _init_bottom_panel(self):
        """ 初始化底部输入面板 (包括模式切换和 DSL) - 首先pack到底部确保可见 """
        ctrl_frame = Frame(self.window, bg="white", pady=8)
        ctrl_frame.pack(side=BOTTOM, fill=X)  # 使用 side=BOTTOM 确保始终在底部

        # 输入模式切换
        mode_frame = Frame(ctrl_frame, bg="white")
        mode_frame.pack(side=LEFT, padx=10)
        Label(mode_frame, text="数据源:", font=("Segoe UI", 9, "bold"), bg="white", fg="#455A64").pack(anchor=W)
        Radiobutton(mode_frame, text="权值列表", variable=self.input_mode, value="numeric", bg="white", font=("Segoe UI", 9)).pack(anchor=W)
        Radiobutton(mode_frame, text="文本字符串", variable=self.input_mode, value="text", bg="white", font=("Segoe UI", 9)).pack(anchor=W)

        Label(ctrl_frame, text="输入内容:", font=("Segoe UI", 10, "bold"), bg="white", fg="#455A64").pack(side=LEFT)
        self.input_var = StringVar(value="5, 9, 12, 13, 16, 45")
        Entry(ctrl_frame, textvariable=self.input_var, width=25, font=("Consolas", 11), bd=1, relief=SOLID).pack(side=LEFT, padx=5)
        
        self._make_btn(ctrl_frame, "▶ 开始构建", self.start_animated_build, "#66BB6A", "white").pack(side=LEFT, padx=8)

        # 分隔线
        Frame(ctrl_frame, width=2, bg="#E0E0E0").pack(side=LEFT, fill=Y, padx=8, pady=5)
        
        Label(ctrl_frame, text="DSL:", font=("Segoe UI", 9, "bold"), bg="white", fg="#455A64").pack(side=LEFT)
        self.dsl_var = StringVar()
        e = Entry(ctrl_frame, textvariable=self.dsl_var, width=12, font=("Consolas", 10), bd=1, relief=SOLID)
        e.pack(side=LEFT, padx=5)
        e.bind("<Return>", lambda e: self._on_dsl_submit())
        Button(ctrl_frame, text="执行", command=self._on_dsl_submit, bg="#78909C", fg="white", bd=0, padx=8).pack(side=LEFT, padx=2)

    def _make_btn(self, parent, text, cmd, bg, fg):
        """ 创建标准按钮样式 """
        return Button(parent, text=text, command=cmd, bg=bg, fg=fg, font=("Segoe UI", 10, "bold"), bd=0, padx=10, pady=5, cursor="hand2")

    def _draw_background_elements(self):
        """ 绘制网格和候选池背景 """
        self.canvas.delete("all")
        for x in range(0, self.canvas_w, 40): self.canvas.create_line(x, 0, x, self.canvas_h, fill=COLORS["grid"], width=1)
        for y in range(0, self.canvas_h, 40): self.canvas.create_line(0, y, 0, self.canvas_h, fill=COLORS["grid"], width=1)
        for y in range(0, self.canvas_h, 40): self.canvas.create_line(0, y, self.canvas_w, y, fill=COLORS["grid"], width=1)
        pad = 20
        self.canvas.create_rectangle(pad, pad, self.canvas_w - pad, pad + 110, fill=COLORS["pool_bg"], outline="", tags="bg")
        self.canvas.create_text(pad + 15, pad + 15, text="CANDIDATE POOL (候选节点池) - 优先队列", anchor="nw", font=("Segoe UI", 9, "bold"), fill="#90A4AE", tags="bg")
        self.status_id = self.canvas.create_text(self.canvas_w - 30, 30, text="Ready", anchor="ne", font=("Segoe UI", 14, "bold"), fill="#455A64")

    # -------------------------------------------------------------------------
    #  核心逻辑 & 输入处理
    # -------------------------------------------------------------------------

    def update_status(self, txt): self.canvas.itemconfig(self.status_id, text=txt)

    def parse_input(self) -> Optional[List[float]]:
        """ 解析输入内容，支持数字列表和文本字符串 """
        raw = self.input_var.get().strip()
        if not raw: return None
        
        if self.input_mode.get() == "text":
            counts = Counter(raw)
            sorted_items = sorted(counts.items(), key=lambda x: (x[1], x[0]))
            self.char_data = sorted_items
            return [x[1] for x in sorted_items]
        else:
            try:
                raw = raw.replace("，", ",")
                nums = [float(x) for x in raw.split(",") if x.strip()]
                self.char_data = []
                return nums
            except:
                return None

    def start_animated_build(self):
        if self.animating: return
        nums = self.parse_input()
        if not nums: 
            messagebox.showwarning("提示", "请输入有效内容")
            return

        self.animating = True
        self.paused = False
        self.step_mode = False
        self.node_vis.clear(); self.final_positions.clear()
        self._tree_clear(); self._draw_background_elements()
        self._clear_explanation_canvas()
        self._clear_heap_display()  # 清除堆显示
        
        self.model = HuffmanModel()
        # 使用增强版构建方法，获取详细的堆操作日志
        root, self.steps, self.snap_before, self.snap_after, self.heap_operations_log = \
            self.model.build_with_heap_steps(nums)
        
        self.total_steps = len(self.steps)
        self.current_step_idx = 0
        self.step_progress_label.config(text=f"合并步骤: 0/{self.total_steps}")
        
        # 设置伪代码
        n = len(nums)
        pseudo_lines = [
            f"// Huffman树构建 (共{n}个节点)",
            "1. 初始化: 依次将节点插入最小堆",
            "2. while (堆中节点数 > 1):",
            "3.     从堆中提取最小节点 (下沉调整)",
            "4.     再提取一个最小节点 (下沉调整)",
            "5.     创建新节点(权值=两者之和)",
            "6.     将新节点插入堆 (上浮调整)",
            "7. 堆中唯一节点即为根节点",
            "8. 生成Huffman编码"
        ]
        self.set_pseudo_code(f"Huffman树构建: {n}个节点", pseudo_lines)
        self.highlight_pseudo_line(0)
        
        # 初始化教学解释
        self.set_explanation(
            f"🎯 目标：构建Huffman树\n\n"
            f"输入了 {n} 个节点，权值为: {', '.join([self._fmt(x) for x in nums])}\n\n"
            f"📌 核心数据结构：最小堆 (Min-Heap)\n"
            f"• 堆顶永远是最小值\n"
            f"• 插入时执行「上浮」操作\n"
            f"• 提取时执行「下沉」操作\n\n"
            f"下方将同步展示堆的变化过程！",
            keywords=["Huffman树", "最小堆", "上浮", "下沉"],
            values=[str(n)],
            important=["堆顶永远是最小值"]
        )
        
        self.highlight_pseudo_line(1)
        
        if root: self._calculate_layout(root)
        
        self._update_tree_list(self.snap_before[0] if self.snap_before else nums, initial=True)
        
        # 先展示堆的初始化过程（带上浮动画）
        self._animate_heap_initialization(nums)

    def _animate_heap_initialization(self, weights):
        """动画展示堆的初始化过程 - 极简版，快速展示最终状态"""
        n = len(weights)
        
        # 从堆操作日志中获取初始化阶段的最终状态
        init_log = None
        for log in self.heap_operations_log:
            if log.get('phase') == 'initialization':
                init_log = log
                break
        
        final_heap = init_log.get('heap_state', sorted(weights)) if init_log else sorted(weights)
        
        self.set_explanation(
            f"📥 构建最小堆\n\n"
            f"将 {n} 个节点插入堆中。\n"
            f"堆顶: {self._fmt(final_heap[0])} (最小值)\n\n"
            f"接下来开始合并过程...",
            keywords=["最小堆", "堆顶"],
            values=[str(n), self._fmt(final_heap[0])],
            important=["最小值"]
        )
        
        # 直接显示最终堆状态
        self._draw_heap(final_heap)
        self.heap_op_label.config(text=f"初始化完成 ({n}个节点)")
        self.update_status(f"堆初始化完成")
        
        # 快速进入候选池动画
        self._schedule_next(lambda: self._animate_initial_pool_simple(weights), 400)
    
    
    def _animate_initial_pool_simple(self, weights):
        """简化版：直接显示节点进入候选池"""
        n = len(weights); gap = 15
        total_w = n * self.node_d + (n-1) * gap
        start_x = (self.canvas_w - total_w) / 2 + self.node_r
        
        self.update_status("开始构建Huffman树")
        
        # 直接创建所有节点
        for i, w in enumerate(weights):
            cx = start_x + i * (self.node_d + gap)
            cy = self.pool_y + 50
            char_label = self.char_data[i][0] if i < len(self.char_data) else None
            uid = f"pool_{i}"
            self._create_node_visual(uid, w, cx, cy, is_pool=True, char_label=char_label)
        
        # 快速开始合并
        self._schedule_next(lambda: self._animate_sequence(0), 300)
    
    def _animate_initial_pool(self, weights):
        """动画展示初始节点进入候选池"""
        n = len(weights); gap = 15
        total_w = n * self.node_d + (n-1) * gap
        start_x = (self.canvas_w - total_w) / 2 + self.node_r
        
        self.update_status("初始化: 节点正在进入候选池...")
        
        def add_node(i):
            if i >= n:
                # 所有节点添加完成
                self.set_explanation(
                    f"✅ 初始化完成！\n\n"
                    f"所有 {n} 个节点已加入优先队列。\n\n"
                    f"📊 当前队列状态:\n"
                    f"[{', '.join([self._fmt(w) for w in sorted(weights)])}]\n\n"
                    f"⏳ 接下来开始合并过程...\n"
                    f"每次找出最小的两个节点进行合并！",
                    keywords=["优先队列", "合并"],
                    values=[str(n)],
                    important=["最小的两个节点"]
                )
                self._schedule_next(lambda: self._animate_sequence(0), 1000)
                return
            
            w = weights[i]
            cx = start_x + i * (self.node_d + gap)
            cy_start = -30  # 从顶部开始
            cy_end = self.pool_y + 50
            char_label = self.char_data[i][0] if i < len(self.char_data) else None
            
            # 创建节点在起始位置
            uid = f"pool_{i}"
            self._create_node_visual(uid, w, cx, cy_start, is_pool=True, char_label=char_label)
            
            # 动画移动到目标位置
            self._animate_node_drop(uid, cy_start, cy_end, lambda: add_node(i + 1))
        
        add_node(0)
    
    def _animate_node_drop(self, uid, cy_start, cy_end, callback):
        """动画：节点从上方掉落到候选池"""
        if uid not in self.node_vis:
            callback()
            return
        
        duration = 15
        d = self.node_vis[uid]
        cx = d['cx']
        
        def step(i):
            if i > duration:
                # 掉落完成后的弹跳效果
                self._animate_bounce(uid, callback)
                return
            
            t = i / duration
            # 使用缓动函数实现加速效果
            ease = t * t
            cy = cy_start + (cy_end - cy_start) * ease
            self._move_node_absolute(uid, cx, cy)
            self.window.after(int(20 / self.animation_speed), lambda: step(i + 1))
        
        step(0)
    
    def _animate_bounce(self, uid, callback):
        """节点着陆弹跳动画"""
        if uid not in self.node_vis:
            callback()
            return
        
        d = self.node_vis[uid]
        original_cy = d['cy']
        
        def bounce(i):
            if i > 6:
                self._move_node_absolute(uid, d['cx'], original_cy)
                callback()
                return
            
            # 弹跳高度逐渐减小
            offset = (6 - i) * 2 * (-1 if i % 2 == 0 else 1)
            self._move_node_absolute(uid, d['cx'], original_cy + offset)
            self.window.after(int(30 / self.animation_speed), lambda: bounce(i + 1))
        
        bounce(0)

    def _calculate_layout(self, root):
        nodes = []
        def walk(n, d):
            if not n: return
            walk(n.left, d+1); n.depth = d; nodes.append(n)
            walk(n.right, d+1)
        walk(root, 0)
        padding = 60
        avail_w = self.canvas_w - 2 * padding
        for i, node in enumerate(nodes):
            x = padding + (i / (len(nodes)-1 or 1)) * avail_w
            y = self.tree_root_y + node.depth * self.level_h
            self.final_positions[node.id] = (x, y)

    def _draw_initial_pool(self, weights):
        n = len(weights); gap = 15
        total_w = n * self.node_d + (n-1) * gap
        start_x = (self.canvas_w - total_w) / 2 + self.node_r
        
        for i, w in enumerate(weights):
            cx = start_x + i * (self.node_d + gap); cy = self.pool_y + 50
            char_label = self.char_data[i][0] if i < len(self.char_data) else None
            self._create_node_visual(f"pool_{i}", w, cx, cy, is_pool=True, char_label=char_label) 

    # -------------------------------------------------------------------------
    #  动画序列 - 增强版
    # -------------------------------------------------------------------------

    def _animate_sequence(self, idx):
        if not self.animating: return
        
        self.current_step_idx = idx
        self.step_progress_label.config(text=f"合并步骤: {idx}/{self.total_steps}")
        
        if idx >= len(self.steps):
            # 高亮完成步骤
            self.highlight_pseudo_line(7, delay=False)  # 根节点
            self.highlight_pseudo_line(8, delay=False)  # 生成编码
            self.complete_pseudo_code()
            self.update_status("🎉 构建完成！开始生成编码...")
            self.animating = False
            
            # 清空堆显示（堆已经只剩根节点）
            self._draw_heap([self.steps[-1][2].weight] if self.steps else [])
            self.heap_op_label.config(text="✅ 构建完成 - 堆中仅剩根节点")
            
            self.set_explanation(
                f"🎉 Huffman树构建完成！\n\n"
                f"共执行了 {self.total_steps} 次合并操作。\n\n"
                f"📌 关键特性:\n"
                f"• 每个叶子节点代表一个原始数据\n"
                f"• 权值小的节点深度更大\n"
                f"• 从根到叶的路径决定编码\n\n"
                f"接下来将生成Huffman编码...",
                keywords=["Huffman树", "叶子节点", "编码"],
                values=[str(self.total_steps)],
                important=["权值小的节点深度更大"]
            )
            
            if self.steps:
                root_node = self.steps[-1][2]
                self._pulse_node(root_node.id, color="#FFD700")
                self._draw_binary_labels(root_node)
                # 直接使用 window.after，因为 animating 已设为 False
                self.window.after(1500, lambda: self._start_encoding_demo(root_node))
            return

        node_a, node_b, node_p = self.steps[idx]
        
        # 获取此次合并的堆操作日志
        merge_log = self._get_merge_log(idx)
        
        # 更新教学解释（简化版）
        remaining = len(self.snap_before[idx])
        self.set_explanation(
            f"📍 第 {idx + 1}/{self.total_steps} 次合并\n\n"
            f"提取最小两个节点:\n"
            f"  {self._fmt(node_a.weight)} + {self._fmt(node_b.weight)} = {self._fmt(node_p.weight)}\n\n"
            f"剩余 {remaining - 2 + 1} 个节点待处理",
            keywords=["合并", "提取"],
            values=[self._fmt(node_a.weight), self._fmt(node_b.weight), self._fmt(node_p.weight)]
        )
        
        # 简化：直接显示堆状态
        if merge_log:
            before_state = merge_log.get('before_state', self.snap_before[idx])
            self._draw_heap(before_state, [0, 1], COLORS["heap_extract"])  # 高亮前两个最小节点
        
        self.highlight_pseudo_line(2, delay=False)
        self.update_status(f"第 {idx+1}/{self.total_steps} 次合并")

        # 快速进入树的动画
        self._animate_heap_extract_sequence(idx, node_a, node_b, node_p, merge_log)
    
    def _get_merge_log(self, idx):
        """获取第idx次合并的堆操作日志"""
        merge_count = 0
        for log in self.heap_operations_log:
            if log.get('phase') == 'merge':
                if merge_count == idx:
                    return log
                merge_count += 1
        return None
    
    def _animate_heap_extract_sequence(self, idx, node_a, node_b, node_p, merge_log):
        """极简版：快速展示堆提取结果，不展示详细过程"""
        if not merge_log:
            self._continue_tree_animation(idx, node_a, node_b, node_p)
            return
        
        operations = merge_log.get('operations', [])
        
        # 获取插入合并节点的操作
        insert_merged = None
        for op in operations:
            if op.get('action', '') == 'insert_merged':
                insert_merged = op
        
        self._current_merge_ops = {'insert_merged': insert_merged}
        
        # 显示提取后的堆状态
        after_extract_state = merge_log.get('after_state', [])
        # 找到提取两个节点后、插入新节点前的状态
        for op in operations:
            if op.get('action', '') == 'extract_second':
                after_extract_state = op.get('heap_state_after', after_extract_state)
                break
        
        self.highlight_pseudo_line(3, delay=False)
        self.heap_op_label.config(text=f"提取: {self._fmt(node_a.weight)}, {self._fmt(node_b.weight)}")
        if after_extract_state:
            self._draw_heap(after_extract_state)
        
        # 快速进入树动画
        self._schedule_next(lambda: self._continue_tree_animation(idx, node_a, node_b, node_p), 200)
    
    def _animate_heap_operation_list(self, operations: List[dict], callback):
        """极简版：只显示堆操作的最终结果，不展示中间过程"""
        if not operations:
            callback()
            return
        
        # 只获取最终状态
        last_heap_state = None
        for op in operations:
            state = op.get('heap_state', None)
            if state:
                last_heap_state = state
        
        # 直接显示最终状态
        if last_heap_state:
            self._draw_heap(last_heap_state)
        
        # 快速回调
        self._schedule_next(callback, 150)
    
    def _continue_tree_animation(self, idx, node_a, node_b, node_p):
        """继续Huffman树的合并动画"""
        vis_a = self._find_pool_visual(node_a)
        vis_b = self._find_pool_visual(node_b)

        def after_selection():
            self.highlight_pseudo_line(5, delay=False)
            
            id1 = self._bind_visual(node_a)
            id2 = self._bind_visual(node_b)
            target_a = self.final_positions[node_a.id]
            target_b = self.final_positions[node_b.id]

            def start_move_out_of_pool(node_id, target_pos, callback):
                vis_data = self.node_vis.get(node_id, {})
                if vis_data.get('is_pool', False) or abs(vis_data.get('cy', 0) - (self.pool_y + 50)) < 5:
                    if node_id in self.node_vis: self.node_vis[node_id]['is_pool'] = False
                    self._tween_move(node_id, target_pos, None, None, duration=30, callback=callback)
                else:
                    callback()

            def step_3_highlight_and_merge():
                self.highlight_pseudo_line(5, delay=False)
                self.update_status(f"Step {idx+1}: 合并 {self._fmt(node_a.weight)} + {self._fmt(node_b.weight)} = {self._fmt(node_p.weight)}")
                self._update_tree_list(self.snap_before[idx])

                self._move_node_absolute(id1, target_a[0], target_a[1])
                self._move_node_absolute(id2, target_b[0], target_b[1])

                self._animate_highlight(id1, id2, lambda:
                    self._animate_move_merge(idx, id1, id2, node_a, node_b, node_p)
                )

            def step_1_move_a():
                self.update_status(f"Step {idx+1}: 节点 {self._fmt(node_a.weight)} 移动到树的位置")
                start_move_out_of_pool(id1, target_a, step_2_move_b)

            def step_2_move_b():
                self.update_status(f"Step {idx+1}: 节点 {self._fmt(node_b.weight)} 移动到树的位置")
                start_move_out_of_pool(id2, target_b, step_3_highlight_and_merge)

            step_1_move_a()

        self._animate_selection(vis_a, vis_b, after_selection)
    
    # -------------------------------------------------------------------------
    #  动画合并 - 增强版
    # -------------------------------------------------------------------------

    def _animate_move_merge(self, idx, id1, id2, na, nb, np):
        target_p = self.final_positions[np.id]
        
        self.highlight_pseudo_line(5, delay=False)
        
        # 设置子节点样式为普通
        self._set_node_style(id1, "normal"); self._set_node_style(id2, "normal")
        
        # 创建合并动画效果
        self._animate_merge_effect(id1, id2, target_p, lambda: self._create_parent_node(idx, na, nb, np, target_p))
    
    def _animate_merge_effect(self, id1, id2, target_p, callback):
        """合并时的视觉效果"""
        # 创建连接线动画
        if id1 in self.node_vis and id2 in self.node_vis:
            v1, v2 = self.node_vis[id1], self.node_vis[id2]
            
            # 绘制临时连接线
            line = self.canvas.create_line(
                v1['cx'], v1['cy'], target_p[0], target_p[1],
                fill=COLORS["merge_glow"], width=3, dash=(5, 3), tags="merge_line")
            line2 = self.canvas.create_line(
                v2['cx'], v2['cy'], target_p[0], target_p[1],
                fill=COLORS["merge_glow"], width=3, dash=(5, 3), tags="merge_line")
            
            # 发光效果
            glow = self.canvas.create_oval(
                target_p[0]-30, target_p[1]-30, target_p[0]+30, target_p[1]+30,
                outline=COLORS["merge_glow"], width=2, tags="merge_glow")
            
            def pulse(i):
                if i > 10:
                    self.canvas.delete("merge_line")
                    self.canvas.delete("merge_glow")
                    callback()
                    return
                
                scale = 1 + 0.1 * math.sin(i * math.pi / 5)
                r = 30 * scale
                self.canvas.coords(glow, 
                    target_p[0]-r, target_p[1]-r, target_p[0]+r, target_p[1]+r)
                self._schedule_next(lambda: pulse(i + 1), 50)
            
            pulse(0)
        else:
            callback()
    
    def _create_parent_node(self, idx, na, nb, np, target_p):
        """创建父节点"""
        # 创建父节点
        self._create_node_visual(np.id, np.weight, target_p[0], target_p[1], is_pool=False)
        self._animate_ripple(target_p[0], target_p[1])
        
        # 绘制连线
        self._draw_bezier_grow(np.id, na.id)
        self._draw_bezier_grow(np.id, nb.id)
        
        # 显示数学公式
        self._show_math_float(target_p[0], target_p[1]-35, na.weight, nb.weight)

        is_final_root = (idx == len(self.steps) - 1)
        
        if is_final_root:
            def on_final_root_created():
                self.update_status("🎉 构建完成！根节点已生成。")
                self._update_tree_list(self.snap_after[idx])
                self._draw_heap([np.weight])  # 最终堆中只有根节点
                self.heap_op_label.config(text="✅ 堆中仅剩根节点")
                self._schedule_next(lambda: self._animate_sequence(idx + 1), 1000)
            self._schedule_next(on_final_root_created, 1000)
        else:
            self.highlight_pseudo_line(6, delay=False)
            
            # 更新解释
            self.set_explanation(
                f"✅ 新节点创建成功！\n\n"
                f"权值: {self._fmt(np.weight)} = {self._fmt(na.weight)} + {self._fmt(nb.weight)}\n\n"
                f"📌 将新节点插入最小堆...\n"
                f"（可能需要上浮调整）\n\n"
                f"剩余 {len(self.snap_after[idx])} 个节点待处理。",
                keywords=["最小堆", "新节点", "上浮"],
                values=[self._fmt(np.weight), str(len(self.snap_after[idx]))],
                important=["插入最小堆"]
            )
            
            pool_uid = f"pool_{np.id}"
            cx_pool = self.canvas_w / 2; cy_pool = self.pool_y + 50
            
            if pool_uid in self.node_vis:
                old = self.node_vis.pop(pool_uid)
                for it in ('shadow', 'shape', 'text'):
                    try: self.canvas.delete(old[it])
                    except: pass

            self._create_node_visual(pool_uid, np.weight, cx_pool, cy_pool, is_pool=True)

            # 简化：直接更新堆显示，不播放详细动画
            def on_heap_update_complete():
                self._draw_heap(self.snap_after[idx])
                self.heap_op_label.config(text=f"✅ 插入 {self._fmt(np.weight)}")
                self._update_tree_list(self.snap_after[idx])
                if pool_uid in self.node_vis:
                    self.node_vis[pool_uid]['is_pool'] = True
                    self.node_vis[pool_uid]['claimed'] = False
                self._relayout_pool_positions(include_id=pool_uid, duration=25, 
                    callback=lambda: self._schedule_next(lambda: self._animate_sequence(idx + 1), 300))

            self._schedule_next(on_heap_update_complete, 200)

    # -------------------------------------------------------------------------
    #  教学功能：编码生成
    # -------------------------------------------------------------------------

    def _draw_binary_labels(self, node):
        if not node: return
        if node.left:
            self._draw_edge_label(node.id, node.left.id, "0")
            self._draw_binary_labels(node.left)
        if node.right:
            self._draw_edge_label(node.id, node.right.id, "1")
            self._draw_binary_labels(node.right)

    def _draw_edge_label(self, pid, cid, text):
        if pid not in self.node_vis or cid not in self.node_vis: return
        p, c = self.node_vis[pid], self.node_vis[cid]
        mx = p['cx'] * 0.4 + c['cx'] * 0.6
        my = p['cy'] * 0.4 + c['cy'] * 0.6
        
        color = COLORS["bit_0"] if text == "0" else COLORS["bit_1"]
        self.canvas.create_oval(mx-8, my-8, mx+8, my+8, fill="white", outline=color, tags="bit_label")
        self.canvas.create_text(mx, my, text=text, font=("Arial", 9, "bold"), fill=color, tags="bit_label")

    def _start_encoding_demo(self, root):
        """ 启动光子编码动画 """
        pseudo_lines = [
            "// Huffman编码生成",
            "GenerateCode(node, code):",
            "    if (node是叶子节点):",
            "        输出 node.char → code",
            "    else:",
            "        GenerateCode(左子节点, code+'0')",
            "        GenerateCode(右子节点, code+'1')",
            "// 从根节点开始，code=空串"
        ]
        self.set_pseudo_code("Huffman编码生成", pseudo_lines)
        self.highlight_pseudo_line(0)
        self.highlight_pseudo_line(1)
        self.highlight_pseudo_line(7)
        
        self.set_explanation(
            f"🔤 开始生成Huffman编码\n\n"
            f"编码规则:\n"
            f"• 向左走 → 添加 '0'\n"
            f"• 向右走 → 添加 '1'\n\n"
            f"从根节点开始遍历到每个叶子节点，\n"
            f"路径上的0/1序列就是该节点的编码。\n\n"
            f"💡 权值越小的节点，编码越长！",
            keywords=["Huffman编码", "叶子节点", "根节点"],
            values=["0", "1"],
            important=["权值越小的节点，编码越长"]
        )
        
        # 收集所有叶子节点的路径数据
        leaves = []
        def dfs(node, path, nodes_path):
            if not node: return
            if not node.left and not node.right:
                leaves.append({"node": node, "bits": path, "route": nodes_path + [node]}); return
            dfs(node.left, path+"0", nodes_path + [node])
            dfs(node.right, path+"1", nodes_path + [node])
        
        dfs(root, "", [])
        leaves.sort(key=lambda x: self.final_positions[x['node'].id][0])

        # ============ 创建现代风格结果弹窗 ============
        top = Toplevel(self.window)
        top.title("Huffman Encoding Report")
        top.geometry("580x720")
        top.config(bg="#0f0f1a")
        top.attributes("-topmost", True)
        
        # 主题色
        bg_dark = "#0f0f1a"
        bg_card = "#1a1a2e"
        accent_cyan = "#00d4aa"
        accent_purple = "#a855f7"
        accent_pink = "#ec4899"
        text_primary = "#ffffff"
        text_secondary = "#94a3b8"
        
        # ---- 顶部标题区域 ----
        header_frame = Frame(top, bg=bg_dark, pady=20, padx=25)
        header_frame.pack(fill=X)
        
        # 标题行
        title_row = Frame(header_frame, bg=bg_dark)
        title_row.pack(fill=X)
        
        Label(title_row, text="⚡", font=("Segoe UI", 28), bg=bg_dark, fg=accent_cyan).pack(side=LEFT)
        
        title_text = Frame(title_row, bg=bg_dark)
        title_text.pack(side=LEFT, padx=12)
        Label(title_text, text="Huffman 编码报告", font=("微软雅黑", 18, "bold"), 
              bg=bg_dark, fg=text_primary).pack(anchor=W)
        Label(title_text, text="Encoding Table & Compression Analysis", 
              font=("Consolas", 10), bg=bg_dark, fg=text_secondary).pack(anchor=W)
        
        # 渐变分隔线
        sep_canvas = Canvas(top, height=3, bg=bg_dark, highlightthickness=0)
        sep_canvas.pack(fill=X, padx=25)
        sep_canvas.create_rectangle(0, 0, 600, 3, fill=accent_cyan, outline="")
        
        # ---- 统计卡片区域 ----
        stats_frame = Frame(top, bg=bg_dark, pady=15, padx=25)
        stats_frame.pack(fill=X)
        
        # 三个统计卡片
        total_bits_var = IntVar(value=0)
        total_chars_var = IntVar(value=len(leaves))
        avg_len_var = StringVar(value="0.00")
        
        def create_stat_card(parent, icon, title, var, color, is_string=False):
            card = Frame(parent, bg=bg_card, padx=15, pady=12)
            card.pack(side=LEFT, fill=X, expand=True, padx=5)
            
            # 圆角效果模拟（通过边框）
            top_line = Frame(card, height=3, bg=color)
            top_line.pack(fill=X, side=TOP)
            
            Label(card, text=icon, font=("Segoe UI", 20), bg=bg_card, fg=color).pack(anchor=W)
            Label(card, text=title, font=("微软雅黑", 9), bg=bg_card, fg=text_secondary).pack(anchor=W)
            if is_string:
                Label(card, textvariable=var, font=("Consolas", 18, "bold"), bg=bg_card, fg=text_primary).pack(anchor=W)
            else:
                Label(card, textvariable=var, font=("Consolas", 18, "bold"), bg=bg_card, fg=text_primary).pack(anchor=W)
        
        create_stat_card(stats_frame, "📊", "字符数", total_chars_var, accent_cyan)
        create_stat_card(stats_frame, "📈", "WPL", total_bits_var, accent_purple)
        create_stat_card(stats_frame, "📏", "平均码长", avg_len_var, accent_pink, is_string=True)
        
        # ---- 表格区域 ----
        table_container = Frame(top, bg=bg_dark, padx=25, pady=10)
        table_container.pack(fill=BOTH, expand=True)
        
        # 表格标题
        table_header = Frame(table_container, bg=bg_card, pady=10, padx=15)
        table_header.pack(fill=X)
        Label(table_header, text="📋 编码详情表", font=("微软雅黑", 11, "bold"), 
              bg=bg_card, fg=text_primary).pack(side=LEFT)
        
        # 配置现代表格样式
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Modern.Treeview", 
                       background=bg_card, 
                       foreground=text_primary,
                       fieldbackground=bg_card,
                       rowheight=38,
                       font=("Consolas", 10),
                       borderwidth=0)
        style.configure("Modern.Treeview.Heading", 
                       font=("微软雅黑", 10, "bold"),
                       background="#252542",
                       foreground=accent_cyan,
                       borderwidth=0,
                       relief="flat")
        style.map("Modern.Treeview",
                 background=[("selected", "#2d2d5a")],
                 foreground=[("selected", accent_cyan)])
        style.map("Modern.Treeview.Heading",
                 background=[("active", "#303060")])
        
        tree_frame = Frame(table_container, bg=bg_card)
        tree_frame.pack(fill=BOTH, expand=True, pady=(0, 10))
        
        cols = ("idx", "char", "weight", "code", "len", "bits")
        tree = ttk.Treeview(tree_frame, columns=cols, show="headings", style="Modern.Treeview", height=10)
        
        tree.heading("idx", text="#")
        tree.heading("char", text="字符")
        tree.heading("weight", text="频率")
        tree.heading("code", text="二进制编码")
        tree.heading("len", text="码长")
        tree.heading("bits", text="W×L")
        
        tree.column("idx", width=40, anchor="center")
        tree.column("char", width=70, anchor="center")
        tree.column("weight", width=70, anchor="center")
        tree.column("code", width=200, anchor="w")
        tree.column("len", width=60, anchor="center")
        tree.column("bits", width=80, anchor="center")
        
        # 滚动条
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        tree.pack(side=LEFT, fill=BOTH, expand=True)
        vsb.pack(side=RIGHT, fill=Y)
        
        # 行标签样式
        tree.tag_configure('even', background="#1e1e3a")
        tree.tag_configure('odd', background=bg_card)
        tree.tag_configure('new_row', background="#1a3a2a")
        
        # ---- 底部信息栏 ----
        footer_frame = Frame(top, bg=bg_card, pady=15, padx=25)
        footer_frame.pack(fill=X, side=BOTTOM)
        
        # WPL 公式展示
        formula_frame = Frame(footer_frame, bg=bg_card)
        formula_frame.pack(fill=X)
        
        Label(formula_frame, text="💡 加权路径长度公式：", font=("微软雅黑", 10), 
              bg=bg_card, fg=text_secondary).pack(side=LEFT)
        Label(formula_frame, text="WPL = Σ(频率 × 码长)", font=("Consolas", 11, "bold"), 
              bg=bg_card, fg=accent_purple).pack(side=LEFT, padx=10)
        
        # 提示信息
        tip_frame = Frame(footer_frame, bg=bg_card, pady=8)
        tip_frame.pack(fill=X)
        Label(tip_frame, text="✨ Huffman编码保证在所有前缀编码中具有最小的加权路径长度", 
              font=("微软雅黑", 9), bg=bg_card, fg=text_secondary).pack(anchor=W)

        self.update_status("正在生成编码表...")
        row_counter = [0]  # 用于计数行号
        
        def run_next_leaf(idx):
            if idx >= len(leaves):
                self.complete_pseudo_code()
                self.update_status(f"✅ 编码完成! 共生成 {len(leaves)} 个编码")
                
                # 计算平均码长
                if len(leaves) > 0 and total_bits_var.get() > 0:
                    total_weight = sum(item['node'].weight for item in leaves)
                    avg = total_bits_var.get() / total_weight if total_weight > 0 else 0
                    avg_len_var.set(f"{avg:.2f}")
                
                self.set_explanation(
                    f"🎊 编码生成完成！\n\n"
                    f"共生成 {len(leaves)} 个字符编码。\n\n"
                    f"加权路径长度 (WPL): {total_bits_var.get()}\n\n"
                    f"💡 WPL 是衡量编码效率的指标，\n"
                    f"Huffman编码保证 WPL 最小！",
                    keywords=["WPL", "Huffman编码"],
                    values=[str(len(leaves)), str(total_bits_var.get())],
                    important=["WPL 最小"]
                )
                return

            item = leaves[idx]; target_node = item['node']; code_bits = item['bits']; route_nodes = item['route']
            vis_data = self.node_vis.get(target_node.id, {})
            char_txt = vis_data.get('char_label', '')
            if char_txt is None or char_txt == '': char_txt = f"W{int(target_node.weight)}"
            else: char_txt = f"'{char_txt}'"
            
            if code_bits and code_bits[-1] == '0':
                self.highlight_pseudo_line(5, delay=False)
            elif code_bits and code_bits[-1] == '1':
                self.highlight_pseudo_line(6, delay=False)
            
            self._animate_photon(route_nodes, lambda: insert_row(char_txt, target_node.weight, code_bits, idx))
            
            def insert_row(c, w, code, i):
                if not top.winfo_exists():
                    return
                
                self.highlight_pseudo_line(2, delay=False)
                self.highlight_pseudo_line(3, delay=False)
                
                row_counter[0] += 1
                bit_len = len(code)
                total_for_char = int(w) * bit_len
                
                # 格式化编码显示（添加空格分隔）
                code_display = ' '.join([code[j:j+4] for j in range(0, len(code), 4)]) if code else "—"
                
                # 交替行颜色
                row_tag = 'even' if row_counter[0] % 2 == 0 else 'odd'
                row_id = tree.insert("", "end", 
                                    values=(row_counter[0], c, int(w), code_display, bit_len, total_for_char), 
                                    tags=(row_tag, 'new_row'))
                tree.see(row_id)
                
                # 更新统计
                current_total = total_bits_var.get()
                total_bits_var.set(current_total + total_for_char)
                
                # 实时更新平均码长
                total_weight = sum(leaves[j]['node'].weight for j in range(i + 1))
                if total_weight > 0:
                    avg = (current_total + total_for_char) / total_weight
                    avg_len_var.set(f"{avg:.2f}")
                
                # 移除之前行的新行高亮
                for child in tree.get_children():
                    if child != row_id:
                        old_tags = tree.item(child, 'tags')
                        new_tags = tuple(t for t in old_tags if t != 'new_row')
                        tree.item(child, tags=new_tags)
                
                # 直接使用 window.after，因为 animating 已为 False
                delay = int(300 / self.animation_speed)
                self.window.after(delay, lambda: run_next_leaf(i + 1))

        run_next_leaf(0)

    def _animate_photon(self, path_nodes, on_done):
        if not path_nodes: on_done(); return
        start_pos = self.final_positions[path_nodes[0].id]
        
        # 创建更醒目的光子效果
        photon = self.canvas.create_oval(start_pos[0]-8, start_pos[1]-8, start_pos[0]+8, start_pos[1]+8, 
                                         fill=COLORS["photon"], outline="white", width=2)
        glow = self.canvas.create_oval(start_pos[0]-12, start_pos[1]-12, start_pos[0]+12, start_pos[1]+12,
                                       outline=COLORS["photon"], width=2)
        
        full_coords = [self.final_positions[n.id] for n in path_nodes]
        total_segments = len(full_coords) - 1
        steps_per_seg = 12
        
        def fly(seg_idx, step_idx):
            if seg_idx >= total_segments:
                self.canvas.delete(photon)
                self.canvas.delete(glow)
                on_done()
                return
            p1 = full_coords[seg_idx]; p2 = full_coords[seg_idx+1]
            t = step_idx / steps_per_seg
            cx = p1[0] + (p2[0] - p1[0]) * t
            cy = p1[1] + (p2[1] - p1[1]) * t
            self.canvas.coords(photon, cx-8, cy-8, cx+8, cy+8)
            self.canvas.coords(glow, cx-12, cy-12, cx+12, cy+12)
            
            if step_idx < steps_per_seg:
                self.window.after(int(12 / self.animation_speed), lambda: fly(seg_idx, step_idx+1))
            else:
                self.window.after(int(12 / self.animation_speed), lambda: fly(seg_idx+1, 0))
        fly(0, 0)

    # -------------------------------------------------------------------------
    #  工具函数
    # -------------------------------------------------------------------------
    
    def _clear_explanation_canvas(self):
        """清除画布上的解释性元素"""
        for tag in ["scan_label", "min_label", "merge_line", "merge_glow"]:
            self.canvas.delete(tag)
    
    # =========================================================================
    #  堆可视化方法
    # =========================================================================
    
    def _draw_heap(self, heap_state: List[float], highlight_indices: List[int] = None,
                   highlight_color: str = None, operation: str = ""):
        """绘制堆的二叉树可视化 - 紧凑版"""
        if not self.heap_canvas:
            return
        
        self.heap_canvas.delete("all")
        self.heap_vis.clear()
        
        n = len(heap_state)
        if n == 0:
            self.heap_canvas.create_text(
                140, 55, text="堆为空",
                font=("微软雅黑", 10), fill="#636e72")
            self.heap_array_label.config(text="[ ]")
            return
        
        # 更新数组显示
        array_str = "[ " + ", ".join([self._fmt(x) for x in heap_state]) + " ]"
        self.heap_array_label.config(text=array_str)
        
        # 紧凑型尺寸
        canvas_w = 270
        canvas_h = 100
        r = 14  # 更小的节点半径
        
        # 计算堆的层数
        levels = math.ceil(math.log2(n + 1)) if n > 0 else 1
        
        # 为每个节点计算位置
        positions = {}
        
        for i in range(n):
            level = math.floor(math.log2(i + 1))
            pos_in_level = i - (2 ** level - 1)
            
            # 水平位置
            level_width = canvas_w / (2 ** level)
            x = 5 + level_width * (pos_in_level + 0.5)
            
            # 垂直位置
            if levels > 1:
                y = 18 + level * (canvas_h - 25) / (levels - 1)
            else:
                y = canvas_h // 2
            
            positions[i] = (x, y)
        
        # 先绘制连线
        for i in range(n):
            left_child = 2 * i + 1
            right_child = 2 * i + 2
            px, py = positions[i]
            
            if left_child < n:
                cx, cy = positions[left_child]
                self.heap_canvas.create_line(
                    px, py + r, cx, cy - r,
                    fill=COLORS["heap_line"], width=1, tags="heap_line")
            
            if right_child < n:
                cx, cy = positions[right_child]
                self.heap_canvas.create_line(
                    px, py + r, cx, cy - r,
                    fill=COLORS["heap_line"], width=1, tags="heap_line")
        
        # 绘制节点
        highlight_indices = highlight_indices or []
        for i in range(n):
            x, y = positions[i]
            weight = heap_state[i]
            
            # 确定节点颜色
            if i in highlight_indices and highlight_color:
                fill_color = highlight_color
                border_color = "#ffffff"
                text_color = "#ffffff"
            else:
                fill_color = COLORS["heap_node"]
                border_color = COLORS["heap_border"]
                text_color = COLORS["heap_text"]
            
            # 绘制节点（无阴影，更紧凑）
            shape = self.heap_canvas.create_oval(
                x - r, y - r, x + r, y + r,
                fill=fill_color, outline=border_color, width=2, tags=f"heap_{i}")
            text = self.heap_canvas.create_text(
                x, y, text=self._fmt(weight),
                font=("Consolas", 8, "bold"), fill=text_color, tags=f"heap_{i}")
            
            self.heap_vis[i] = {
                'x': x, 'y': y, 'shape': shape, 
                'text': text, 'weight': weight
            }
    
    def _highlight_heap_nodes(self, indices: List[int], color: str = None, reset_others: bool = True):
        """高亮指定节点，不重绘整个堆（避免闪烁）"""
        if not self.heap_canvas or not self.heap_vis:
            return
        
        for i, vis in self.heap_vis.items():
            if i in indices and color:
                # 高亮选中的节点
                self.heap_canvas.itemconfig(vis['shape'], fill=color, outline="#ffffff")
                self.heap_canvas.itemconfig(vis['text'], fill="#ffffff")
            elif reset_others:
                # 恢复其他节点默认样式
                self.heap_canvas.itemconfig(vis['shape'], fill=COLORS["heap_node"], outline=COLORS["heap_border"])
                self.heap_canvas.itemconfig(vis['text'], fill=COLORS["heap_text"])
    
    def _animate_heap_insert(self, heap_states: List[List[float]], 
                             operations: List[dict], callback):
        """动画展示堆插入操作（简化版，减少闪烁）"""
        # 此方法已废弃，使用 _animate_heap_insert_steps 代替
        callback()
    
    def _animate_heap_extract(self, operations: List[dict], callback):
        """动画展示堆提取最小值操作（简化版，减少闪烁）"""
        # 此方法已废弃，使用 _animate_heap_operation_list 代替
        callback()
    
    def _update_heap_display(self, heap_state: List[float], operation: str = ""):
        """更新堆的静态显示"""
        self.heap_state = heap_state.copy()
        self._draw_heap(heap_state)
        if operation:
            self.heap_op_label.config(text=operation)
    
    def _clear_heap_display(self):
        """清除堆显示"""
        if self.heap_canvas:
            self.heap_canvas.delete("all")
        self.heap_vis.clear()
        self.heap_state = []
        if hasattr(self, 'heap_op_label') and self.heap_op_label:
            self.heap_op_label.config(text="等待...")
        if hasattr(self, 'heap_array_label') and self.heap_array_label:
            self.heap_array_label.config(text="[ ]")
    
    def _update_tree_list(self, items, initial=False):
        for i in self.heap_tree.get_children(): self.heap_tree.delete(i)
        
        if initial and self.input_mode.get() == "text" and self.char_data:
            display_str = ", ".join([f"'{c}':{w}" for c, w in self.char_data])
        else:
            sorted_items = sorted(items)
            display_str = ",  ".join([self._fmt(x) for x in sorted_items])
            
        self.heap_tree.insert("", "end", values=(display_str,))

    def _tree_clear(self):
        for i in self.heap_tree.get_children(): self.heap_tree.delete(i)
    
    def _fmt(self, v): return str(int(v)) if abs(v - int(v)) < 1e-9 else f"{v:.1f}"

    def _create_node_visual(self, uid, weight, cx, cy, is_pool=False, char_label=None):
        r = self.node_r
        disp_text = self._fmt(weight)
        if char_label: disp_text = f"'{char_label}'\n{disp_text}"
            
        shadow = self.canvas.create_oval(cx-r+3, cy-r+3, cx+r+3, cy+r+3, fill=COLORS["shadow"], outline="", tags=f"node_{uid}")
        shape = self.canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill=COLORS["node_fill"], outline=COLORS["node_border"], width=2, tags=f"node_{uid}")
        text = self.canvas.create_text(cx, cy, text=disp_text, font=("Segoe UI", 9, "bold"), fill=COLORS["node_text"], justify=CENTER, tags=f"node_{uid}")
        
        self.node_vis[uid] = {
            'cx': cx, 'cy': cy, 'shadow': shadow, 'shape': shape, 'text': text,
            'weight': weight, 'is_pool': is_pool, 'claimed': False, 'char_label': char_label
        }

    def _bind_visual(self, node):
        pool_key = f"pool_{node.id}"
        if pool_key in self.node_vis and self.node_vis[pool_key].get('is_pool', False) and not self.node_vis[pool_key].get('claimed', False):
            self.node_vis[pool_key]['claimed'] = True
            self.node_vis[pool_key]['is_pool'] = False
            data = self.node_vis.pop(pool_key)
            self.node_vis[node.id] = data
            return node.id

        if node.id in self.node_vis:
            self.node_vis[node.id]['claimed'] = True
            return node.id
        
        best_id = None
        for vid, v in self.node_vis.items():
            if v['is_pool'] and not v['claimed']:
                if abs(v['weight'] - node.weight) < 0.001: best_id = vid; break
        
        if best_id:
            self.node_vis[best_id]['claimed'] = True
            self.node_vis[best_id]['is_pool'] = False
            data = self.node_vis.pop(best_id); self.node_vis[node.id] = data
            return node.id
        else:
            pos = self.final_positions.get(node.id, (0,0))
            self._create_node_visual(node.id, node.weight, pos[0], pos[1])
            return node.id

    def _tween_move(self, id1, pos1, id2, pos2, duration, callback):
        d1 = self.node_vis.get(id1); d2 = self.node_vis.get(id2)
        if not d1: callback(); return
            
        s1, s2 = (d1['cx'], d1['cy']), (None, None)
        if d2: s2 = (d2['cx'], d2['cy'])
        
        def step(i):
            if i > duration: callback(); return
            t = i / duration; e = t * t * (3 - 2 * t)
            
            nx1 = s1[0] + (pos1[0]-s1[0])*e; ny1 = s1[1] + (pos1[1]-s1[1])*e
            self._move_node_absolute(id1, nx1, ny1)
            
            if d2 and pos2:
                nx2 = s2[0] + (pos2[0]-s2[0])*e; ny2 = s2[1] + (pos2[1]-s2[1])*e
                self._move_node_absolute(id2, nx2, ny2)
                
            self.window.after(int(15 / self.animation_speed), lambda: step(i+1))
            
        step(0)

    def _find_pool_visual(self, node) -> Optional[str]:
        pool_key = f"pool_{node.id}"
        if pool_key in self.node_vis and self.node_vis[pool_key].get('is_pool', False):
            return pool_key

        for vid, v in self.node_vis.items():
            if v.get('is_pool', False) and not v.get('claimed', False) and abs(v.get('weight', 0) - node.weight) < 0.001:
                return vid

        if node.id in self.node_vis:
            return node.id

        return None

    def _animate_selection(self, vid_a: Optional[str], vid_b: Optional[str], callback):
        items = [v for v in (vid_a, vid_b) if v]
        if not items:
            callback(); return

        orig = {}
        def mark(vid):
            if vid not in self.node_vis: return
            shape = self.node_vis[vid]['shape']
            outline_val = self.canvas.itemcget(shape, 'outline')
            width_str = self.canvas.itemcget(shape, 'width') or '2'
            try:
                width_val = int(float(width_str))
            except Exception:
                width_val = 2
            orig[vid] = {'outline': outline_val, 'width': width_val}
            self.canvas.itemconfig(shape, outline=COLORS['highlight_border'], width=4)

        def unmark_all():
            for vid, vals in orig.items():
                try:
                    self.canvas.itemconfig(self.node_vis[vid]['shape'], outline=vals['outline'], width=vals['width'])
                except Exception:
                    pass

        for vid in items: mark(vid)
        self._schedule_next(lambda: (unmark_all(), callback()), 600)

    def _relayout_pool_positions(self, include_id=None, duration=30, callback=None):
        pool_items = [(vid, v) for vid, v in self.node_vis.items() if v.get('is_pool', False)]
        if include_id and include_id in self.node_vis and all(vid != include_id for vid, _ in pool_items):
            pool_items.append((include_id, self.node_vis[include_id]))

        n = len(pool_items)
        if n == 0:
            if callback: callback()
            return

        gap = 15
        total_w = n * self.node_d + (n - 1) * gap
        start_x = (self.canvas_w - total_w) / 2 + self.node_r
        targets = {}

        pool_items.sort(key=lambda x: x[1].get('cx', 0))
        for i, (vid, _) in enumerate(pool_items):
            tx = start_x + i * (self.node_d + gap)
            ty = self.pool_y + 50
            targets[vid] = (tx, ty)

        remaining = len(targets)
        def one_done():
            nonlocal remaining
            remaining -= 1
            if remaining <= 0 and callback:
                callback()

        for vid, pos in targets.items():
            if vid in self.node_vis:
                self.node_vis[vid]['is_pool'] = True
                self.node_vis[vid]['claimed'] = False
            self._tween_move(vid, pos, None, None, duration, one_done)

    def _move_node_absolute(self, uid, cx, cy):
        if uid not in self.node_vis: return
        d = self.node_vis[uid]; dx, dy = cx - d['cx'], cy - d['cy']
        for item in [d['shadow'], d['shape'], d['text']]: self.canvas.move(item, dx, dy)
        d['cx'], d['cy'] = cx, cy

    def _draw_bezier_grow(self, pid, cid):
        if pid not in self.node_vis or cid not in self.node_vis: return
        p, c = self.node_vis[pid], self.node_vis[cid]
        x1, y1 = p['cx'], p['cy'] + self.node_r
        x2, y2 = c['cx'], c['cy'] - self.node_r
        line = self.canvas.create_line(x1, y1, x1, y1, width=2, fill=COLORS["line_active"], smooth=True, capstyle=ROUND)
        self.canvas.tag_lower(line)
        def grow(i):
            if i > 20: self.canvas.itemconfig(line, fill=COLORS["line"]); return
            t = i/20; tx = x1+(x2-x1)*t; ty = y1+(y2-y1)*t; my = (y1+ty)/2
            self.canvas.coords(line, x1, y1, x1, my, tx, my, tx, ty)
            self.window.after(int(15 / self.animation_speed), lambda: grow(i+1))
        grow(1)

    def _animate_ripple(self, cx, cy):
        r = self.node_r; oval = self.canvas.create_oval(cx-r, cy-r, cx+r, cy+r, outline=COLORS["ripple"], width=2)
        def expand(s):
            if s>10: self.canvas.delete(oval); return
            sc=1+s*0.15; self.canvas.coords(oval, cx-r*sc, cy-r*sc, cx+r*sc, cy+r*sc)
            self.window.after(int(30 / self.animation_speed), lambda: expand(s+1))
        expand(0)

    def _show_math_float(self, cx, cy, w1, w2):
        tid = self.canvas.create_text(cx, cy, text=f"{self._fmt(w1)}+{self._fmt(w2)}={self._fmt(w1+w2)}", 
                                      font=("Arial", 12, "bold"), fill=COLORS["math_text"])
        def fly(i): 
            if i>25: self.canvas.delete(tid); return
            self.canvas.move(tid, 0, -1.2)
            alpha = max(0, 1 - i/25)
            self.window.after(int(35 / self.animation_speed), lambda: fly(i+1))
        fly(0)
    
    def _animate_highlight(self, id1, id2, cb):
        self._set_node_style(id1, "highlight"); self._set_node_style(id2, "highlight")
        self._schedule_next(cb, 500)

    def _set_node_style(self, uid, style):
        if uid not in self.node_vis: return
        v = self.node_vis[uid]
        c_fill = COLORS["highlight_fill"] if style=="highlight" else COLORS["node_fill"]
        c_out = COLORS["highlight_border"] if style=="highlight" else COLORS["node_border"]
        self.canvas.itemconfig(v['shape'], fill=c_fill, outline=c_out)

    def _pulse_node(self, uid, color):
        if uid not in self.node_vis: return
        s = self.node_vis[uid]['shape']; o = self.canvas.itemcget(s, "outline")
        self.canvas.itemconfig(s, outline=color, width=4)
        self.window.after(600, lambda: self.canvas.itemconfig(s, outline=o, width=2))

    def clear_canvas(self):
        self.animating = False
        self.paused = False
        self.step_mode = False
        self.node_vis.clear()
        self._tree_clear()
        self._draw_background_elements()
        self._clear_explanation_canvas()
        self._clear_heap_display()  # 清除堆显示
        self.update_status("Ready")
        self.clear_pseudo_code()
        self.step_progress_label.config(text="合并步骤: 0/0")
        self.set_explanation("等待输入数据...\n\n输入权值列表或文本字符串，\n点击「开始构建」按钮开始演示。")

    def back_to_main(self): self.window.destroy()

    def _on_dsl_submit(self):
        cmd = self.dsl_var.get().strip()
        if not cmd: return
        try:
            from DSL_utils import process_command
            process_command(self, cmd)
            self.update_status(f"DSL执行成功: {cmd}")
        except Exception as e: messagebox.showerror("DSL 错误", str(e))
        self.dsl_var.set("")

    def _ensure_huffman_folder(self) -> str:
        try:
            return storage.ensure_save_subdir("huffman")
        except:
            d = "data/huffman"
            if not os.path.exists(d): os.makedirs(d)
            return d

    def save_tree(self):
        nums = self.parse_input()
        if not nums: return
        payload = {
            "weights": nums, "mode": self.input_mode.get(), "char_data": self.char_data,
            "saved_at": datetime.now().isoformat()
        }
        default_dir = self._ensure_huffman_folder()
        default_name = f"huffman_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = filedialog.asksaveasfilename(
            initialdir=default_dir, initialfile=default_name, defaultextension=".json", filetypes=[("JSON files", "*.json")]
        )
        if filepath:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)
            messagebox.showinfo("成功", f"文件已保存至:\n{filepath}")

    def load_tree(self):
        default_dir = self._ensure_huffman_folder()
        filepath = filedialog.askopenfilename(initialdir=default_dir, filetypes=[("JSON files", "*.json")])
        if filepath:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    obj = json.load(f)
                weights = obj.get("weights", []); mode = obj.get("mode", "numeric")
                if weights:
                    self.input_var.set(",".join(map(str, weights))); self.input_mode.set(mode)
                    self.char_data = obj.get("char_data", []) 
                    self.start_animated_build()
                    messagebox.showinfo("加载成功", f"已加载 {len(weights)} 个权值并开始重构 (模式: {mode})")
                else:
                    messagebox.showwarning("警告", "文件中未找到有效权值数据")
            except Exception as e:
                messagebox.showerror("加载失败", str(e))

if __name__ == '__main__':
    w = Tk()
    w.title("Huffman树可视化 - 教学增强版")
    w.geometry("1500x900")
    try: from ctypes import windll; windll.shcore.SetProcessDpiAwareness(1)
    except: pass
    HuffmanVisualizer(w)
    w.mainloop()
