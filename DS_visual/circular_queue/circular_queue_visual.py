from tkinter import *
from tkinter import messagebox, filedialog
import json
import os
import random
import math
from datetime import datetime
from typing import Any, List, Optional, Tuple

from circular_queue.circular_queue_model import CircularQueueModel
from circular_queue.bfs_visual import open_bfs_visualizer
import storage
from DSL_utils import circular_queue_dsl

process_command = circular_queue_dsl._fallback_process_command

# ========== 多语言伪代码定义 ==========

# 语言选项
LANG_PSEUDOCODE = "伪代码"
LANG_C = "C语言"
LANG_JAVA = "Java"
LANG_PYTHON = "Python"
CODE_LANGUAGES = [LANG_PSEUDOCODE, LANG_C, LANG_JAVA, LANG_PYTHON]

# 入队 - 多语言
MULTILANG_ENQUEUE = {
    "伪代码": [
        ("// 入队操作 (Enqueue)", "comment"),
        ("ENQUEUE(queue, value):", "code"),
        ("  if queue.size ≥ capacity then", "code"),
        ("    return ERROR  // 队列已满", "comment"),
        ("  end if", "code"),
        ("  queue.buffer[rear] ← value", "code"),
        ("  rear ← (rear + 1) mod capacity", "code"),
        ("  queue.size ← size + 1", "code"),
        ("  return SUCCESS", "code"),
    ],
    "C语言": [
        ("// 入队操作 (Enqueue)", "comment"),
        ("int enqueue(Queue* q, int value) {", "code"),
        ("  if (q->size >= q->capacity) {", "code"),
        ("    return ERROR; // 队列已满", "comment"),
        ("  }", "code"),
        ("  q->buffer[q->rear] = value;", "code"),
        ("  q->rear = (q->rear + 1) % q->capacity;", "code"),
        ("  q->size++;", "code"),
        ("  return SUCCESS;", "code"),
        ("}", "code"),
    ],
    "Java": [
        ("// 入队操作 (Enqueue)", "comment"),
        ("boolean enqueue(int value) {", "code"),
        ("  if (size >= capacity) {", "code"),
        ("    return false; // 队列已满", "comment"),
        ("  }", "code"),
        ("  buffer[rear] = value;", "code"),
        ("  rear = (rear + 1) % capacity;", "code"),
        ("  size++;", "code"),
        ("  return true;", "code"),
        ("}", "code"),
    ],
    "Python": [
        ("# 入队操作 (Enqueue)", "comment"),
        ("def enqueue(self, value):", "code"),
        ("  if self.size >= self.capacity:", "code"),
        ("    return False  # 队列已满", "comment"),
        ("  # endif", "comment"),
        ("  self.buffer[self.rear] = value", "code"),
        ("  self.rear = (self.rear + 1) % self.capacity", "code"),
        ("  self.size += 1", "code"),
        ("  return True", "code"),
    ]
}

# 出队 - 多语言
MULTILANG_DEQUEUE = {
    "伪代码": [
        ("// 出队操作 (Dequeue)", "comment"),
        ("DEQUEUE(queue):", "code"),
        ("  if queue.size = 0 then", "code"),
        ("    return ERROR  // 队列为空", "comment"),
        ("  end if", "code"),
        ("  value ← queue.buffer[front]", "code"),
        ("  queue.buffer[front] ← NULL", "code"),
        ("  front ← (front + 1) mod capacity", "code"),
        ("  queue.size ← size - 1", "code"),
        ("  return value", "code"),
    ],
    "C语言": [
        ("// 出队操作 (Dequeue)", "comment"),
        ("int dequeue(Queue* q, int* value) {", "code"),
        ("  if (q->size == 0) {", "code"),
        ("    return ERROR; // 队列为空", "comment"),
        ("  }", "code"),
        ("  *value = q->buffer[q->front];", "code"),
        ("  q->buffer[q->front] = 0;", "code"),
        ("  q->front = (q->front + 1) % q->capacity;", "code"),
        ("  q->size--;", "code"),
        ("  return SUCCESS;", "code"),
        ("}", "code"),
    ],
    "Java": [
        ("// 出队操作 (Dequeue)", "comment"),
        ("Integer dequeue() {", "code"),
        ("  if (size == 0) {", "code"),
        ("    return null; // 队列为空", "comment"),
        ("  }", "code"),
        ("  int value = buffer[front];", "code"),
        ("  buffer[front] = 0;", "code"),
        ("  front = (front + 1) % capacity;", "code"),
        ("  size--;", "code"),
        ("  return value;", "code"),
        ("}", "code"),
    ],
    "Python": [
        ("# 出队操作 (Dequeue)", "comment"),
        ("def dequeue(self):", "code"),
        ("  if self.size == 0:", "code"),
        ("    return None  # 队列为空", "comment"),
        ("  # endif", "comment"),
        ("  value = self.buffer[self.front]", "code"),
        ("  self.buffer[self.front] = None", "code"),
        ("  self.front = (self.front + 1) % self.capacity", "code"),
        ("  self.size -= 1", "code"),
        ("  return value", "code"),
    ]
}

# 清空 - 多语言
MULTILANG_CLEAR = {
    "伪代码": [
        ("// 清空队列操作 (Clear)", "comment"),
        ("CLEAR(queue):", "code"),
        ("  for i ← 0 to capacity do", "code"),
        ("    queue.buffer[i] ← NULL", "code"),
        ("  end for", "code"),
        ("  front ← 0", "code"),
        ("  rear ← 0", "code"),
        ("  queue.size ← 0", "code"),
    ],
    "C语言": [
        ("// 清空队列操作 (Clear)", "comment"),
        ("void clear(Queue* q) {", "code"),
        ("  for (int i = 0; i < q->capacity; i++) {", "code"),
        ("    q->buffer[i] = 0;", "code"),
        ("  }", "code"),
        ("  q->front = 0;", "code"),
        ("  q->rear = 0;", "code"),
        ("  q->size = 0;", "code"),
        ("}", "code"),
    ],
    "Java": [
        ("// 清空队列操作 (Clear)", "comment"),
        ("void clear() {", "code"),
        ("  for (int i = 0; i < capacity; i++) {", "code"),
        ("    buffer[i] = 0;", "code"),
        ("  }", "code"),
        ("  front = 0;", "code"),
        ("  rear = 0;", "code"),
        ("  size = 0;", "code"),
        ("}", "code"),
    ],
    "Python": [
        ("# 清空队列操作 (Clear)", "comment"),
        ("def clear(self):", "code"),
        ("  for i in range(self.capacity):", "code"),
        ("    self.buffer[i] = None", "code"),
        ("  # endfor", "comment"),
        ("  self.front = 0", "code"),
        ("  self.rear = 0", "code"),
        ("  self.size = 0", "code"),
    ]
}

# 空闲状态 - 多语言
MULTILANG_IDLE = {
    "伪代码": [
        ("// 循环队列 (Circular Queue)", "comment"),
        ("", "code"),
        ("// 特点:", "comment"),
        ("// 1. 固定容量的环形缓冲区", "comment"),
        ("// 2. front指向队首元素(出队位置)", "comment"),
        ("// 3. rear指向下一个插入位置", "comment"),
        ("// 4. 使用取模实现循环", "comment"),
        ("", "code"),
        ("// 支持的操作:", "comment"),
        ("//   enqueue <val> - 入队", "comment"),
        ("//   dequeue - 出队", "comment"),
        ("//   clear - 清空", "comment"),
    ],
    "C语言": [
        ("// 循环队列 (Circular Queue)", "comment"),
        ("typedef struct {", "code"),
        ("  int* buffer;", "code"),
        ("  int capacity;", "code"),
        ("  int front;  // 队首指针", "comment"),
        ("  int rear;   // 队尾指针", "comment"),
        ("  int size;", "code"),
        ("} Queue;", "code"),
        ("", "code"),
        ("// 支持的操作:", "comment"),
        ("// enqueue(), dequeue(), clear()", "comment"),
    ],
    "Java": [
        ("// 循环队列 (Circular Queue)", "comment"),
        ("class CircularQueue {", "code"),
        ("  private int[] buffer;", "code"),
        ("  private int capacity;", "code"),
        ("  private int front; // 队首指针", "comment"),
        ("  private int rear;  // 队尾指针", "comment"),
        ("  private int size;", "code"),
        ("}", "code"),
        ("", "code"),
        ("// 支持的操作:", "comment"),
        ("// enqueue(), dequeue(), clear()", "comment"),
    ],
    "Python": [
        ("# 循环队列 (Circular Queue)", "comment"),
        ("class CircularQueue:", "code"),
        ("  def __init__(self, capacity):", "code"),
        ("    self.buffer = [None] * capacity", "code"),
        ("    self.capacity = capacity", "code"),
        ("    self.front = 0  # 队首指针", "comment"),
        ("    self.rear = 0   # 队尾指针", "comment"),
        ("    self.size = 0", "code"),
        ("", "code"),
        ("# 支持的操作:", "comment"),
        ("# enqueue(), dequeue(), clear()", "comment"),
    ]
}

# 保持向后兼容
PSEUDOCODE_ENQUEUE = MULTILANG_ENQUEUE["伪代码"]
PSEUDOCODE_DEQUEUE = MULTILANG_DEQUEUE["伪代码"]
PSEUDOCODE_CLEAR = MULTILANG_CLEAR["伪代码"]
PSEUDOCODE_IDLE = MULTILANG_IDLE["伪代码"]

class CircularQueueVisualizer:
    def __init__(self, root):
        self.window = root
        self.window.config(bg="#F5F7FA")
        self.window.title("循环队列可视化")
        
        # 使用现代化字体
        self.title_font = ("Microsoft YaHei", 24, "bold")
        self.subtitle_font = ("Microsoft YaHei", 11)
        self.button_font = ("Microsoft YaHei", 11)
        self.input_font = ("Microsoft YaHei", 11)
        self.canvas_font = ("Microsoft YaHei", 12)
        self.code_font = ("Consolas", 10)  # 伪代码字体
        
        # 代码语言设置（支持运行时切换）
        self.current_code_language = LANG_PSEUDOCODE  # 默认伪代码
        self.current_operation_type = None  # 当前操作类型
        
        # 伪代码相关颜色
        self.code_colors = {
            "bg": "#1E1E2E",
            "fg": "#D4D4D4",
            "highlight_bg": "#F9E2AF",
            "highlight_fg": "#1E1E2E",
            "comment": "#6A9955",
            "title": "#89B4FA",
            "separator": "#45475A",
        }
        
        # 创建主框架
        self.main_frame = Frame(self.window, bg="#F5F7FA")
        self.main_frame.pack(fill=BOTH, expand=True, padx=20, pady=10)
        
        # 标题区域
        self.create_heading()
        
        # 内容区域 - 左侧画布 + 右侧伪代码面板
        self.content_frame = Frame(self.main_frame, bg="#F5F7FA")
        self.content_frame.pack(fill=BOTH, expand=False, pady=(0, 10))
        
        # 画布区域 (左侧)
        self.canvas_frame = Frame(self.content_frame, bg="#F5F7FA")
        self.canvas_frame.pack(side=LEFT, fill=BOTH, expand=True)
        
        self.canvas = Canvas(self.canvas_frame, bg="white", width=1050, height=550, 
                           relief="flat", bd=0, highlightthickness=1, highlightbackground="#E1E8ED")
        self.canvas.pack()
        
        # 伪代码面板 (右侧)
        self._create_pseudocode_panel()
        
        self.capacity = 8
        self.model = CircularQueueModel(self.capacity)

        self.box_ids: List[int] = []
        self.text_ids: List[int] = []

        # 布局参数 - 线性队列
        self.center_x = 100
        self.center_y = 70
        self.cell_w = 90
        self.cell_h = 45
        self.gap = 10
        
        # 布局参数 - 环形队列
        self.ring_center_x = 525
        self.ring_center_y = 360
        self.ring_outer_radius = 130
        self.ring_inner_radius = 70
        self.ring_arc_gap = 3  # 扇形之间的间隙角度

        # 控件 & 状态
        self.value_var = StringVar()
        self.batch_var = StringVar()
        self.batch_var.set("1,2,3,4,5,6,7,8")
        self.random_count_var = StringVar()
        self.random_count_var.set("5")
        self.dsl_var = StringVar()
        self.input_frame = None

        self.enqueue_btn = None
        self.dequeue_btn = None
        self.clear_btn = None
        self.batch_btn = None
        self.random_btn = None
        self.back_btn = None
        self.bfs_btn = None

        self.batch_queue: List[str] = []
        self.batch_index = 0
        self.animating = False
        
        # 伪代码状态
        self.current_pseudocode: List[Tuple[str, str]] = []
        self.code_line_labels: List[Label] = []
        self.highlighted_line = -1

        self.create_control_panel()
        self.update_display()
        self._show_pseudocode_for_operation('idle')  # 显示初始伪代码

    def create_heading(self):
        heading_frame = Frame(self.main_frame, bg="#F5F7FA")
        heading_frame.pack(fill=X, pady=(0, 20))
        
        title_label = Label(heading_frame, text="循环队列可视化系统", 
                          font=self.title_font, bg="#F5F7FA", fg="#2C3E50")
        title_label.pack()
        
        subtitle_label = Label(heading_frame, 
                             text="环形缓冲数据结构：展示 head/tail 指针移动、入队/出队与满/空状态",
                             font=self.subtitle_font, bg="#F5F7FA", fg="#7F8C8D")
        subtitle_label.pack(pady=(5, 0))

    def _create_pseudocode_panel(self):
        """创建伪代码显示面板"""
        # 伪代码面板容器
        self.code_panel = Frame(
            self.content_frame, 
            bg=self.code_colors["bg"],
            width=300,
            bd=2,
            relief="groove"
        )
        self.code_panel.pack(side=RIGHT, fill=Y, padx=(10, 0))
        self.code_panel.pack_propagate(False)
        
        # 标题栏（包含标题和语言切换）
        title_frame = Frame(self.code_panel, bg=self.code_colors["bg"])
        title_frame.pack(fill=X, padx=10, pady=(10, 5))
        
        # 伪代码标题
        code_title = Label(
            title_frame,
            text="📝 算法代码",
            bg=self.code_colors["bg"],
            fg=self.code_colors["title"],
            font=("Microsoft YaHei", 11, "bold")
        )
        code_title.pack(side=LEFT)
        
        # 语言切换下拉框
        self.code_lang_var = StringVar(value=self.current_code_language)
        self.lang_menu = OptionMenu(
            title_frame, 
            self.code_lang_var, 
            *CODE_LANGUAGES,
            command=self._on_code_language_change
        )
        self.lang_menu.config(
            font=("微软雅黑", 8),
            bg="#313244",
            fg="#CDD6F4",
            activebackground="#45475A",
            activeforeground="#CDD6F4",
            highlightthickness=0,
            relief="flat",
            width=5
        )
        self.lang_menu["menu"].config(
            bg="#313244",
            fg="#CDD6F4",
            activebackground="#89B4FA",
            activeforeground="#1E1E2E",
            font=("微软雅黑", 8)
        )
        self.lang_menu.pack(side=RIGHT)
        
        # 语言切换快捷按钮组
        btn_frame = Frame(self.code_panel, bg=self.code_colors["bg"])
        btn_frame.pack(fill=X, padx=10, pady=(0, 5))
        
        self.lang_buttons = {}
        for lang in CODE_LANGUAGES:
            short_name = {"伪代码": "伪代码", "C语言": "C", "Java": "Java", "Python": "Py"}.get(lang, lang)
            btn = Label(
                btn_frame,
                text=short_name,
                font=("微软雅黑", 8),
                bg="#89B4FA" if lang == self.current_code_language else "#313244",
                fg="#1E1E2E" if lang == self.current_code_language else "#CDD6F4",
                padx=6,
                pady=2,
                cursor="hand2"
            )
            btn.pack(side=LEFT, padx=2)
            btn.bind("<Button-1>", lambda e, l=lang: self._switch_code_language(l))
            self.lang_buttons[lang] = btn
        
        # 分隔线
        separator = Frame(self.code_panel, height=2, bg=self.code_colors["separator"])
        separator.pack(fill=X, padx=10)
        
        # 代码显示区域的容器
        self.code_frame = Frame(self.code_panel, bg=self.code_colors["bg"])
        self.code_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # 状态标签
        self.code_status_label = Label(
            self.code_panel,
            text="等待操作...",
            font=("Microsoft YaHei", 9),
            bg="#313244",
            fg="#A6ADC8",
            anchor="w",
            padx=5,
            pady=3
        )
        self.code_status_label.pack(fill=X, side=BOTTOM)
    
    def _on_code_language_change(self, selected_lang):
        """语言切换回调（下拉框）"""
        self._switch_code_language(selected_lang)
    
    def _switch_code_language(self, new_lang):
        """切换代码语言并重新渲染"""
        if new_lang == self.current_code_language:
            return
        
        self.current_code_language = new_lang
        self.code_lang_var.set(new_lang)
        
        # 更新按钮样式
        for lang, btn in self.lang_buttons.items():
            if lang == new_lang:
                btn.config(bg="#89B4FA", fg="#1E1E2E")
            else:
                btn.config(bg="#313244", fg="#CDD6F4")
        
        # 保存当前高亮行
        saved_highlight = self.highlighted_line
        
        # 如果有当前操作类型，重新显示该语言的代码
        if self.current_operation_type:
            self._show_pseudocode_for_operation(self.current_operation_type)
            if saved_highlight >= 0:
                self._highlight_code_line(saved_highlight)
    
    def _show_pseudocode_for_operation(self, operation: str):
        """显示指定操作的伪代码（支持多语言）"""
        self.current_operation_type = operation
        
        multilang_map = {
            'enqueue': MULTILANG_ENQUEUE,
            'dequeue': MULTILANG_DEQUEUE,
            'clear': MULTILANG_CLEAR,
            'idle': MULTILANG_IDLE,
        }
        
        if operation in multilang_map:
            code_dict = multilang_map[operation]
            code = code_dict.get(self.current_code_language, code_dict.get("伪代码", []))
            self._set_pseudocode(code)

    def _set_pseudocode(self, pseudocode: List[Tuple[str, str]]):
        """设置要显示的伪代码"""
        self.current_pseudocode = pseudocode
        self._render_pseudocode()
        self.highlighted_line = -1

    def _render_pseudocode(self):
        """渲染伪代码到面板"""
        # 清除现有标签
        for label in self.code_line_labels:
            try:
                label.destroy()
            except:
                pass
        self.code_line_labels = []
        
        # 创建新标签
        for i, (text, code_type) in enumerate(self.current_pseudocode):
            # 设置颜色
            if code_type == "comment":
                fg_color = self.code_colors["comment"]
            else:
                fg_color = self.code_colors["fg"]
            
            label = Label(
                self.code_frame,
                text=f" {i+1:2d} │ {text}",
                font=self.code_font,
                bg=self.code_colors["bg"],
                fg=fg_color,
                anchor="w",
                padx=2,
                pady=1
            )
            label.pack(fill=X, anchor="w")
            self.code_line_labels.append(label)

    def _highlight_code_line(self, line_number: int, status_text: str = None):
        """高亮指定行"""
        # 取消之前的高亮
        if 0 <= self.highlighted_line < len(self.code_line_labels):
            old_label = self.code_line_labels[self.highlighted_line]
            code_type = self.current_pseudocode[self.highlighted_line][1] if self.highlighted_line < len(self.current_pseudocode) else "code"
            fg_color = self.code_colors["comment"] if code_type == "comment" else self.code_colors["fg"]
            try:
                old_label.config(bg=self.code_colors["bg"], fg=fg_color, font=self.code_font)
            except:
                pass
        
        # 设置新的高亮
        if 0 <= line_number < len(self.code_line_labels):
            new_label = self.code_line_labels[line_number]
            try:
                new_label.config(
                    bg=self.code_colors["highlight_bg"], 
                    fg=self.code_colors["highlight_fg"], 
                    font=(self.code_font[0], self.code_font[1], "bold")
                )
            except:
                pass
            self.highlighted_line = line_number
        
        # 更新状态
        if status_text:
            self._set_code_status(status_text)
        
        # 强制更新显示
        try:
            self.code_panel.update()
        except:
            pass

    def _reset_code_highlight(self):
        """重置所有高亮"""
        for i, label in enumerate(self.code_line_labels):
            code_type = self.current_pseudocode[i][1] if i < len(self.current_pseudocode) else "code"
            fg_color = self.code_colors["comment"] if code_type == "comment" else self.code_colors["fg"]
            try:
                label.config(bg=self.code_colors["bg"], fg=fg_color, font=self.code_font)
            except:
                pass
        self.highlighted_line = -1

    def _set_code_status(self, text: str):
        """设置状态文本"""
        try:
            self.code_status_label.config(text=text)
        except:
            pass

    def create_control_panel(self):
        # 主控制面板
        control_frame = Frame(self.main_frame, bg="#FFFFFF", relief="flat", bd=1, 
                            highlightbackground="#E1E8ED", highlightthickness=1)
        control_frame.pack(fill=X, pady=(0, 5))
        
        # 第一行：主要操作按钮 + 文件操作
        btn_row1 = Frame(control_frame, bg="#FFFFFF")
        btn_row1.pack(fill=X, padx=15, pady=(8, 4))
        
        self.enqueue_btn = self.create_modern_button(btn_row1, "入队", "#3498DB", 
                                                   self.prepare_enqueue, small=True)
        self.enqueue_btn.pack(side=LEFT, padx=4, pady=2)
        
        self.dequeue_btn = self.create_modern_button(btn_row1, "出队", "#E74C3C", 
                                                   self.animate_dequeue, small=True)
        self.dequeue_btn.pack(side=LEFT, padx=4, pady=2)
        
        self.clear_btn = self.create_modern_button(btn_row1, "清空", "#F39C12", 
                                                 self.clear_queue, small=True)
        self.clear_btn.pack(side=LEFT, padx=4, pady=2)
        
        self.back_btn = self.create_modern_button(btn_row1, "返回", "#95A5A6", 
                                                self.back_to_main, small=True)
        self.back_btn.pack(side=LEFT, padx=4, pady=2)
        
        # 分隔符
        sep1 = Label(btn_row1, text=" | ", font=("Microsoft YaHei", 9), bg="#FFFFFF", fg="#BDC3C7")
        sep1.pack(side=LEFT, padx=2)
        
        # 文件操作
        load_btn = self.create_modern_button(btn_row1, "加载", "#1ABC9C", 
                                           self.load_structure, small=True)
        load_btn.pack(side=LEFT, padx=4, pady=2)
        
        save_btn = self.create_modern_button(btn_row1, "保存", "#1ABC9C", 
                                           self.save_structure, small=True)
        save_btn.pack(side=LEFT, padx=4, pady=2)
        
        # 分隔符
        sep2 = Label(btn_row1, text=" | ", font=("Microsoft YaHei", 9), bg="#FFFFFF", fg="#BDC3C7")
        sep2.pack(side=LEFT, padx=2)
        
        # 随机插入（移到第一行）
        random_label = Label(btn_row1, text="随机:", 
                           font=("Microsoft YaHei", 10), bg="#FFFFFF", fg="#2C3E50")
        random_label.pack(side=LEFT, padx=(0, 3), pady=2)
        
        random_entry = Entry(btn_row1, textvariable=self.random_count_var, width=4, 
                           font=("Microsoft YaHei", 10), relief="solid", bd=1)
        random_entry.pack(side=LEFT, padx=2, pady=2)
        
        self.random_btn = self.create_modern_button(btn_row1, "入队", "#8E44AD", 
                                                  self.start_random_insert, small=True)
        self.random_btn.pack(side=LEFT, padx=4, pady=2)
        
        # 分隔符
        sep_bfs = Label(btn_row1, text=" | ", font=("Microsoft YaHei", 9), bg="#FFFFFF", fg="#BDC3C7")
        sep_bfs.pack(side=LEFT, padx=2)
        
        # BFS演示按钮
        self.bfs_btn = self.create_modern_button(btn_row1, "BFS演示", "#16A085", 
                                                self.open_bfs_demo, small=True)
        self.bfs_btn.pack(side=LEFT, padx=4, pady=2)
        
        # 第二行：批量构建 + DSL命令
        btn_row2 = Frame(control_frame, bg="#FFFFFF")
        btn_row2.pack(fill=X, padx=15, pady=(4, 8))
        
        # 批量构建
        batch_label = Label(btn_row2, text="批量:", 
                          font=("Microsoft YaHei", 10), bg="#FFFFFF", fg="#2C3E50")
        batch_label.pack(side=LEFT, padx=(0, 3), pady=2)
        
        batch_entry = Entry(btn_row2, textvariable=self.batch_var, width=20, 
                          font=("Microsoft YaHei", 10), relief="solid", bd=1)
        batch_entry.pack(side=LEFT, padx=2, pady=2)
        
        self.batch_btn = self.create_modern_button(btn_row2, "构建", "#27AE60", 
                                                 self.start_batch, small=True)
        self.batch_btn.pack(side=LEFT, padx=4, pady=2)
        
        # 分隔符
        sep3 = Label(btn_row2, text=" | ", font=("Microsoft YaHei", 9), bg="#FFFFFF", fg="#BDC3C7")
        sep3.pack(side=LEFT, padx=5)
        
        # DSL命令
        dsl_label = Label(btn_row2, text="DSL:", 
                        font=("Microsoft YaHei", 10), bg="#FFFFFF", fg="#2C3E50")
        dsl_label.pack(side=LEFT, padx=(0, 3), pady=2)
        
        dsl_entry = Entry(btn_row2, textvariable=self.dsl_var, width=35, 
                        font=("Microsoft YaHei", 10), relief="solid", bd=1)
        dsl_entry.pack(side=LEFT, padx=2, pady=2, fill=X, expand=True)
        dsl_entry.bind("<Return>", self.process_dsl)
        
        execute_btn = self.create_modern_button(btn_row2, "执行", "#9B59B6", 
                                              self.process_dsl, small=True)
        execute_btn.pack(side=LEFT, padx=4, pady=2)

    def create_modern_button(self, parent, text, color, command, small=False):
        btn_font = self.button_font if not small else ("Microsoft YaHei", 9)
        btn_width = 14 if not small else 6
        
        # 修复：确保命令正确传递
        btn = Button(parent, text=text, font=btn_font,
                    width=btn_width, height=1 if small else 2, 
                    bg=color, fg="white", 
                    activebackground=self.darken_color(color),
                    activeforeground="white",
                    relief="flat", bd=0,
                    command=command)  # 直接传递命令，不使用lambda
        
        # 添加悬停效果
        def on_enter(e):
            btn['bg'] = self.darken_color(color)
        def on_leave(e):
            btn['bg'] = color
            
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
        return btn

    def darken_color(self, color):
        # 简单的颜色变暗函数
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)
        
        r = max(0, r - 30)
        g = max(0, g - 30)
        b = max(0, b - 30)
        
        return f"#{r:02x}{g:02x}{b:02x}"

    def process_dsl(self, event=None):
        text = self.dsl_var.get().strip()
        if not text:
            return
        process_command(self, text)
        self.dsl_var.set("")

    def _ensure_folder(self):
        return storage.ensure_save_subdir("circular_queue")

    def save_structure(self):
        data = list(self.model.buffer)
        meta = {"capacity": self.capacity, "head": self.model.head, "tail": self.model.tail, "size": self.model.size}
        default_dir = self._ensure_folder()
        default_name = f"cqueue_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = filedialog.asksaveasfilename(initialdir=default_dir, initialfile=default_name, defaultextension=".json", filetypes=[("JSON files","*.json")])
        if filepath:
            payload = {"type":"circular_queue","buffer":data,"meta":meta}
            with open(filepath,"w",encoding="utf-8") as f:
                json.dump(payload,f,ensure_ascii=False,indent=2)
            messagebox.showinfo("成功", f"已保存到：\n{filepath}")

    def load_structure(self):
        default_dir = self._ensure_folder()
        filepath = filedialog.askopenfilename(initialdir=default_dir, filetypes=[("JSON files","*.json")])
        if filepath:
            with open(filepath,"r",encoding="utf-8") as f:
                loaded = json.load(f)
            buf = loaded.get("buffer", [])
            meta = loaded.get("meta", {})
            self.model.buffer = list(buf)[:self.capacity]
            self.model.capacity = self.capacity
            self.model.head = int(meta.get("head", 0))
            self.model.tail = int(meta.get("tail", 0))
            self.model.size = int(meta.get("size", sum(1 for x in buf if x is not None)))
            self.update_display()
            messagebox.showinfo("成功", "已加载循环队列")

    def prepare_enqueue(self):
        """准备入队操作 - 显示输入框"""
        if self.animating:
            messagebox.showwarning("提示", "动画进行中，请稍候")
            return
            
        if self.model.is_full():
            messagebox.showwarning("队列满", "队列已满，无法入队")
            return
            
        # 如果已有输入框，先销毁
        if self.input_frame:
            self.input_frame.destroy()
            self.input_frame = None
        
        self.value_var.set("")
        # 创建输入框
        self.input_frame = Frame(self.main_frame, bg="#F5F7FA", relief="flat", bd=1,
                               highlightbackground="#E1E8ED", highlightthickness=1)
        self.input_frame.pack(fill=X, pady=10)
        
        input_content = Frame(self.input_frame, bg="#F5F7FA")
        input_content.pack(padx=20, pady=15)
        
        Label(input_content, text="输入要入队的值:", 
              font=self.button_font, bg="#F5F7FA", fg="#2C3E50").pack(side=LEFT, padx=(0, 10))
        
        entry = Entry(input_content, textvariable=self.value_var, 
                     font=self.input_font, width=20, relief="solid", bd=1)
        entry.pack(side=LEFT, padx=10)
        entry.focus_set()  # 自动聚焦
        
        # 确认按钮
        confirm_btn = Button(input_content, text="确认入队", font=self.button_font,
                           width=12, height=1, 
                           bg="#3498DB", fg="white", 
                           activebackground=self.darken_color("#3498DB"),
                           activeforeground="white",
                           relief="flat", bd=0,
                           command=self._on_confirm_enqueue)
        confirm_btn.pack(side=LEFT, padx=5)
        
        # 取消按钮
        cancel_btn = Button(input_content, text="取消", font=self.button_font,
                          width=8, height=1,
                          bg="#95A5A6", fg="white",
                          activebackground=self.darken_color("#95A5A6"),
                          activeforeground="white",
                          relief="flat", bd=0,
                          command=self._cancel_input)
        cancel_btn.pack(side=LEFT, padx=5)
        
        # 添加悬停效果
        for btn in [confirm_btn, cancel_btn]:
            color = btn.cget("bg")
            def make_on_enter(button, btn_color):
                def on_enter(e):
                    button['bg'] = self.darken_color(btn_color)
                return on_enter
            def make_on_leave(button, btn_color):
                def on_leave(e):
                    button['bg'] = btn_color
                return on_leave
            
            btn.bind("<Enter>", make_on_enter(btn, color))
            btn.bind("<Leave>", make_on_leave(btn, color))
        
        # 绑定回车键到确认
        entry.bind("<Return>", lambda e: self._on_confirm_enqueue())

    def _cancel_input(self):
        """取消输入"""
        if self.input_frame:
            self.input_frame.destroy()
            self.input_frame = None

    def _on_confirm_enqueue(self):
        """确认入队操作"""
        value = self.value_var.get().strip()
        if not value:
            messagebox.showerror("错误", "请输入要入队的值")
            return
            
        # 销毁输入框
        if self.input_frame:
            self.input_frame.destroy()
            self.input_frame = None
            
        # 执行入队动画
        self.animate_enqueue(value)

    def animate_enqueue(self, value: Any, on_finish=None):
        """执行入队动画"""
        if self.animating:
            return
            
        if self.model.is_full():
            messagebox.showwarning("队列满", "队列已满，无法入队")
            return
            
        self.animating = True
        self._set_buttons_state("disabled")
        
        # 设置入队伪代码并高亮检查条件
        self._show_pseudocode_for_operation('enqueue')
        self._highlight_code_line(1, f"入队: {value}")

        # 创建移动的元素
        sx, sy = -120, self.center_y
        rect = self.canvas.create_rectangle(sx, sy, sx + self.cell_w, sy + self.cell_h, 
                                          fill="#D5F5E3", outline="#27AE60", width=2)
        txt = self.canvas.create_text(sx + self.cell_w/2, sy + self.cell_h/2, 
                                    text=str(value), font=("Microsoft YaHei", 14, "bold"), fill="#145A32")

        rear_idx = self.model.tail
        tx = self.center_x + rear_idx * (self.cell_w + self.gap)
        steps = 30
        dx = (tx - sx) / steps
        delay = 12

        def step(i=0):
            if i < steps:
                self.canvas.move(rect, dx, 0)
                self.canvas.move(txt, dx, 0)
                # 动画过程中高亮不同的代码行
                if i == 5:
                    self._highlight_code_line(2, "检查队列是否已满")
                elif i == 10:
                    self._highlight_code_line(4, f"buffer[{rear_idx}] = {value}")
                elif i == 20:
                    self._highlight_code_line(5, f"rear = ({rear_idx}+1) % {self.capacity}")
                self.window.after(delay, lambda: step(i+1))
            else:
                self.canvas.delete(rect)
                self.canvas.delete(txt)
                ok = self.model.enqueue(value)
                if not ok:
                    messagebox.showwarning("队列满", "入队失败：队列已满")
                self._highlight_code_line(6, f"size = {self.model.size}")
                self.update_display()
                
                # 延迟后显示完成状态
                def finish():
                    self._highlight_code_line(7, "入队完成!")
                    self.window.after(300, lambda: self._finish_enqueue(on_finish))
                self.window.after(200, finish)
        step()

    def _finish_enqueue(self, on_finish=None):
        """入队完成后的清理"""
        self.animating = False
        self._set_buttons_state("normal")
        self._show_pseudocode_for_operation('idle')
        self._set_code_status("等待操作...")
        if on_finish:
            on_finish()

    def animate_dequeue(self, on_finish=None):
        if self.animating or self.model.is_empty():
            if self.model.is_empty():
                messagebox.showwarning("队列空", "队列为空")
            return
        self.animating = True
        self._set_buttons_state("disabled")
        
        # 设置出队伪代码
        self._show_pseudocode_for_operation('dequeue')
        self._highlight_code_line(1, "开始出队操作")

        front_idx = self.model.head
        x = self.center_x + front_idx * (self.cell_w + self.gap)
        y = self.center_y
        highlight = self.canvas.create_rectangle(x, y, x + self.cell_w, y + self.cell_h, 
                                               fill="#FADBD8", outline="#E74C3C", width=2)
        val = self.model.buffer[front_idx]
        txt = self.canvas.create_text(x + self.cell_w/2, y + self.cell_h/2, 
                                    text=str(val) if val is not None else "", 
                                    font=("Microsoft YaHei", 14, "bold"), fill="#922B21")

        steps = 30
        dx = (1100 - x) / steps
        delay = 12

        def step(i=0):
            if i < steps:
                self.canvas.move(highlight, dx, 0)
                self.canvas.move(txt, dx, 0)
                # 动画过程中高亮不同的代码行
                if i == 3:
                    self._highlight_code_line(2, "检查队列是否为空")
                elif i == 8:
                    self._highlight_code_line(4, f"value = buffer[{front_idx}]")
                elif i == 15:
                    self._highlight_code_line(5, f"buffer[{front_idx}] = NULL")
                elif i == 22:
                    self._highlight_code_line(6, f"front = ({front_idx}+1) % {self.capacity}")
                self.window.after(delay, lambda: step(i+1))
            else:
                self.canvas.delete(highlight)
                self.canvas.delete(txt)
                dequeued_val = self.model.dequeue()
                self._highlight_code_line(7, f"size = {self.model.size}")
                self.update_display()
                
                # 延迟后显示完成状态
                def finish():
                    self._highlight_code_line(8, f"返回值: {dequeued_val}")
                    self.window.after(300, lambda: self._finish_dequeue(on_finish))
                self.window.after(200, finish)
        step()

    def _finish_dequeue(self, on_finish=None):
        """出队完成后的清理"""
        self.animating = False
        self._set_buttons_state("normal")
        self._show_pseudocode_for_operation('idle')
        self._set_code_status("等待操作...")
        if on_finish:
            on_finish()

    def clear_queue(self):
        if self.animating or self.model.is_empty():
            if self.model.is_empty():
                messagebox.showinfo("信息", "队列已空")
            return
        self._set_buttons_state("disabled")
        
        # 设置清空伪代码
        self._show_pseudocode_for_operation('clear')
        self._highlight_code_line(1, "开始清空队列")
        self.window.update()
        
        # 模拟逐步清空动画
        self.animating = True
        self._animate_clear_step(0)

    def _animate_clear_step(self, step_idx: int):
        """清空动画的步骤"""
        if step_idx == 0:
            self._highlight_code_line(2, "遍历缓冲区")
            self.window.after(200, lambda: self._animate_clear_step(1))
        elif step_idx == 1:
            self._highlight_code_line(3, "清空每个位置")
            self.window.after(200, lambda: self._animate_clear_step(2))
        elif step_idx == 2:
            self._highlight_code_line(4, "front = 0")
            self.window.after(200, lambda: self._animate_clear_step(3))
        elif step_idx == 3:
            self._highlight_code_line(5, "rear = 0")
            self.window.after(200, lambda: self._animate_clear_step(4))
        elif step_idx == 4:
            self._highlight_code_line(6, "size = 0")
            self.model.clear()
            self.update_display()
            self.window.after(300, lambda: self._finish_clear())

    def _finish_clear(self):
        """清空完成后的清理"""
        self.animating = False
        self._set_buttons_state("normal")
        self._show_pseudocode_for_operation('idle')
        self._set_code_status("队列已清空")

    def start_batch(self):
        if self.animating:
            return
        text = self.batch_var.get().strip()
        if not text:
            messagebox.showinfo("提示", "请输入要构建的值，例如：1,2,3")
            return
        items = [s.strip() for s in text.split(",") if s.strip() != ""]
        available = self.capacity - self.model.size
        if len(items) > available:
            if not messagebox.askyesno("容量不足", f"当前可用位置 {available}，要入队 {len(items)} 个。是否只入队前 {available} 个？"):
                return
            items = items[:available]
        self.batch_queue = items
        self.batch_index = 0
        self._set_buttons_state("disabled")
        self._batch_step()

    def start_random_insert(self):
        """开始随机插入指定数量的元素"""
        if self.animating:
            messagebox.showwarning("提示", "动画进行中，请稍候")
            return
        
        # 获取用户输入的数量
        try:
            count = int(self.random_count_var.get().strip())
            if count < 1:
                raise ValueError("数量必须大于0")
        except ValueError:
            messagebox.showerror("错误", "请输入有效的正整数 (1-100)")
            return
        
        # 限制最大数量
        if count > 100:
            count = 100
            messagebox.showinfo("提示", "已限制为最多100个")
        
        # 检查可用空间
        available = self.capacity - self.model.size
        if available == 0:
            messagebox.showwarning("队列满", "队列已满，无法入队")
            return
        
        if count > available:
            if not messagebox.askyesno("容量不足", 
                f"当前可用位置 {available}，要入队 {count} 个。是否只入队 {available} 个？"):
                return
            count = available
        
        # 生成随机数（范围 1-100）
        random_values = [str(random.randint(1, 100)) for _ in range(count)]
        
        self.batch_queue = random_values
        self.batch_index = 0
        self._set_buttons_state("disabled")
        self._set_code_status(f"随机入队 {len(random_values)} 个元素...")
        self._batch_step()

    def _batch_step(self):
        if self.batch_index >= len(self.batch_queue):
            total = len(self.batch_queue) if self.batch_queue else self.batch_index
            self.batch_queue = []
            self.batch_index = 0
            self._set_buttons_state("normal")
            self._show_pseudocode_for_operation('idle')
            self._set_code_status("批量入队完成")
            return
        total = len(self.batch_queue)
        v = self.batch_queue[self.batch_index]
        self.batch_index += 1
        self._set_code_status(f"入队第 {self.batch_index}/{total} 个: {v}")
        self.animate_enqueue(v, on_finish=self._batch_step)

    def update_display(self):
        self.canvas.delete("all")
        self.box_ids.clear()
        self.text_ids.clear()
        
        # 线性队列标题
        self.canvas.create_text(self.center_x + 350, 15, 
                              text="📋 线性视图 (Linear View)", 
                              font=("Microsoft YaHei", 11, "bold"), 
                              fill="#2C3E50")
        
        sz = self.model.size
        status = "满" if self.model.is_full() else ("空" if self.model.is_empty() else "非空")
        status_color = "#E74C3C" if self.model.is_full() else ("#7F8C8D" if self.model.is_empty() else "#27AE60")
        
        # 状态显示在标题旁边
        self.canvas.create_text(self.center_x + 600, 15, 
                              text=f"状态: {status}  |  大小: {sz}/{self.capacity}",
                              font=("Microsoft YaHei", 10), fill=status_color)

        # 绘制队列单元格
        for i in range(self.capacity):
            x = self.center_x + i * (self.cell_w + self.gap)
            y = self.center_y
            
            # 单元格样式
            fill_color = "#EBF5FB" if self.model.buffer[i] is not None else "#FDFEFE"
            outline_color = "#3498DB" if self.model.buffer[i] is not None else "#BDC3C7"
            
            rect = self.canvas.create_rectangle(x, y, x + self.cell_w, y + self.cell_h, 
                                              fill=fill_color, outline=outline_color, width=2)
            self.box_ids.append(rect)
            
            val = self.model.buffer[i]
            txt = self.canvas.create_text(x + self.cell_w/2, y + self.cell_h/2, 
                                        text=(str(val) if val is not None else "空"), 
                                        font=("Microsoft YaHei", 11, "bold"),
                                        fill="#2C3E50")
            self.text_ids.append(txt)
            
            # 索引标签
            self.canvas.create_text(x + self.cell_w/2, y + self.cell_h + 12, 
                                  text=f"{i}", font=("Microsoft YaHei", 9), fill="#7F8C8D")

        # front/rear 指针 (线性队列)
        front, rear = self.model.head, self.model.tail
        fx = self.center_x + front * (self.cell_w + self.gap) + self.cell_w/2
        fy = self.center_y - 20
        self.canvas.create_line(fx, fy, fx, self.center_y - 2, arrow=LAST, width=3, fill="#E67E22")
        self.canvas.create_text(fx, fy - 12, text=f"front({front})", 
                              font=("Microsoft YaHei", 9, "bold"), fill="#E67E22")

        rx = self.center_x + rear * (self.cell_w + self.gap) + self.cell_w/2
        ry = self.center_y + self.cell_h + 24
        self.canvas.create_line(rx, self.center_y + self.cell_h + 2, rx, ry, arrow=LAST, width=3, fill="#2E86C1")
        self.canvas.create_text(rx, ry + 12, text=f"rear({rear})", 
                              font=("Microsoft YaHei", 9, "bold"), fill="#2E86C1")
        
        # 分隔线
        self.canvas.create_line(20, 175, 1030, 175, fill="#E1E8ED", width=1, dash=(4, 2))
        
        # 绘制环形队列视图
        self._draw_ring_queue()

    def _draw_ring_queue(self):
        """绘制环形队列可视化"""
        cx, cy = self.ring_center_x, self.ring_center_y
        r_outer = self.ring_outer_radius
        r_inner = self.ring_inner_radius
        
        # 环形标题
        self.canvas.create_text(cx, 190, 
                              text="🔄 环形视图 (Circular View)", 
                              font=("Microsoft YaHei", 11, "bold"), 
                              fill="#2C3E50")
        
        # 每个扇形的角度范围
        angle_per_cell = 360 / self.capacity
        gap_angle = self.ring_arc_gap
        arc_angle = angle_per_cell - gap_angle
        
        front, rear = self.model.head, self.model.tail
        
        for i in range(self.capacity):
            # 从顶部 (90度) 开始，顺时针绘制
            # Tkinter的角度是逆时针的，所以我们需要调整
            start_angle = 90 - i * angle_per_cell - arc_angle
            
            # 确定单元格状态和颜色
            val = self.model.buffer[i]
            is_front = (i == front and self.model.size > 0)
            is_rear = (i == rear)
            
            # 填充颜色
            if val is not None:
                fill_color = "#D5F5E3"  # 有数据 - 浅绿色
                outline_color = "#27AE60"
            else:
                fill_color = "#F8F9F9"  # 空 - 浅灰色
                outline_color = "#BDC3C7"
            
            # front 位置特殊标记
            if is_front and self.model.size > 0:
                outline_color = "#E67E22"  # 橙色
            
            # 绘制扇形 (使用多边形模拟扇环)
            self._draw_arc_sector(cx, cy, r_inner, r_outer, start_angle, arc_angle, 
                                fill_color, outline_color)
            
            # 计算文本位置 (在扇形中间)
            mid_angle = math.radians(start_angle + arc_angle / 2)
            text_r = (r_inner + r_outer) / 2
            text_x = cx + text_r * math.cos(mid_angle)
            text_y = cy - text_r * math.sin(mid_angle)
            
            # 绘制值文本
            display_text = str(val) if val is not None else ""
            if display_text:
                self.canvas.create_text(text_x, text_y, 
                                      text=display_text, 
                                      font=("Microsoft YaHei", 10, "bold"),
                                      fill="#145A32")
            
            # 绘制索引标签 (在外圈)
            label_angle = math.radians(start_angle + arc_angle / 2)
            label_r = r_outer + 20
            label_x = cx + label_r * math.cos(label_angle)
            label_y = cy - label_r * math.sin(label_angle)
            self.canvas.create_text(label_x, label_y, 
                                  text=str(i), 
                                  font=("Microsoft YaHei", 9),
                                  fill="#7F8C8D")
        
        # 绘制 front 指针 (队首，出队位置)
        if self.model.size > 0:
            front_start = 90 - front * angle_per_cell - arc_angle / 2
            self._draw_ring_pointer(cx, cy, r_outer + 5, front_start, "#E67E22", "front", inward=True)
        
        # 绘制 rear 指针 (队尾，入队位置)
        rear_start = 90 - rear * angle_per_cell - arc_angle / 2
        self._draw_ring_pointer(cx, cy, r_inner - 5, rear_start, "#2E86C1", "rear", inward=False)
        
        # 中心显示队列信息
        self.canvas.create_oval(cx - 35, cy - 35, cx + 35, cy + 35, 
                              fill="#F0F3F4", outline="#D5DBDB", width=2)
        self.canvas.create_text(cx, cy - 10, 
                              text=f"{self.model.size}/{self.capacity}",
                              font=("Microsoft YaHei", 14, "bold"),
                              fill="#2C3E50")
        self.canvas.create_text(cx, cy + 12, 
                              text="size",
                              font=("Microsoft YaHei", 9),
                              fill="#7F8C8D")
        
        # 绘制知识说明区域
        self._draw_knowledge_panel()

    def _draw_arc_sector(self, cx, cy, r_inner, r_outer, start_angle, extent, fill_color, outline_color):
        """绘制扇环形状 (使用多边形模拟)"""
        points = []
        steps = 20  # 平滑度
        
        # 外弧 (从 start_angle 到 start_angle + extent)
        for i in range(steps + 1):
            angle = math.radians(start_angle + extent * i / steps)
            x = cx + r_outer * math.cos(angle)
            y = cy - r_outer * math.sin(angle)
            points.append((x, y))
        
        # 内弧 (从 start_angle + extent 到 start_angle，反向)
        for i in range(steps, -1, -1):
            angle = math.radians(start_angle + extent * i / steps)
            x = cx + r_inner * math.cos(angle)
            y = cy - r_inner * math.sin(angle)
            points.append((x, y))
        
        # 展平坐标列表
        flat_points = [coord for point in points for coord in point]
        
        self.canvas.create_polygon(flat_points, fill=fill_color, outline=outline_color, width=2)

    def _draw_ring_pointer(self, cx, cy, radius, angle_deg, color, label, inward=True):
        """绘制环形队列的指针"""
        angle_rad = math.radians(angle_deg)
        
        # 指针起点
        px = cx + radius * math.cos(angle_rad)
        py = cy - radius * math.sin(angle_rad)
        
        # 指针方向 (向内或向外)
        pointer_length = 25
        if inward:
            end_x = cx + (radius - pointer_length) * math.cos(angle_rad)
            end_y = cy - (radius - pointer_length) * math.sin(angle_rad)
        else:
            end_x = cx + (radius + pointer_length) * math.cos(angle_rad)
            end_y = cy - (radius + pointer_length) * math.sin(angle_rad)
        
        # 绘制箭头
        if inward:
            self.canvas.create_line(px, py, end_x, end_y, arrow=LAST, width=3, fill=color)
        else:
            self.canvas.create_line(end_x, end_y, px, py, arrow=LAST, width=3, fill=color)
        
        # 绘制标签 (增大偏移以适应较长标签)
        label_offset = 25
        if inward:
            label_x = cx + (radius + label_offset) * math.cos(angle_rad)
            label_y = cy - (radius + label_offset) * math.sin(angle_rad)
        else:
            label_x = cx + (radius - pointer_length - label_offset - 5) * math.cos(angle_rad)
            label_y = cy - (radius - pointer_length - label_offset - 5) * math.sin(angle_rad)
        
        self.canvas.create_text(label_x, label_y, 
                              text=label, 
                              font=("Microsoft YaHei", 9, "bold"),
                              fill=color)

    def _draw_knowledge_panel(self):
        """绘制数据结构与算法知识说明面板"""
        # 知识面板位置 (环形视图右侧)
        panel_x = 750
        panel_y = 210
        panel_w = 280
        panel_h = 330
        
        # 绘制面板背景
        self.canvas.create_rectangle(
            panel_x, panel_y, panel_x + panel_w, panel_y + panel_h,
            fill="#F8F9FA", outline="#DEE2E6", width=1
        )
        
        # 面板标题
        self.canvas.create_text(
            panel_x + panel_w / 2, panel_y + 15,
            text="📚 循环队列知识要点",
            font=("Microsoft YaHei", 10, "bold"),
            fill="#2C3E50"
        )
        
        # 分隔线
        self.canvas.create_line(
            panel_x + 10, panel_y + 32, panel_x + panel_w - 10, panel_y + 32,
            fill="#DEE2E6", width=1
        )
        
        # 知识要点内容
        knowledge_items = [
            ("📌 基本概念", "#3498DB", [
                "• 循环队列是一种环形缓冲区",
                "• 使用固定大小的数组实现",
                "• 通过取模运算实现首尾相连"
            ]),
            ("🎯 指针含义", "#E67E22", [
                f"• front = {self.model.head} (队首，出队位置)",
                f"• rear = {self.model.tail} (队尾，入队位置)",
            ]),
            ("⚙️ 核心操作", "#27AE60", [
                "• 入队: rear = (rear+1) % capacity",
                "• 出队: front = (front+1) % capacity",
            ]),
            ("📊 状态判断", "#9B59B6", [
                f"• 队空: size == 0 → {self.model.is_empty()}",
                f"• 队满: size == capacity → {self.model.is_full()}",
            ]),
            ("⏱️ 时间复杂度", "#E74C3C", [
                "• 入队/出队: O(1)",
                "• 查询队首: O(1)",
            ]),
        ]
        
        y_offset = panel_y + 45
        for title, title_color, items in knowledge_items:
            # 小标题
            self.canvas.create_text(
                panel_x + 15, y_offset,
                text=title,
                font=("Microsoft YaHei", 9, "bold"),
                fill=title_color,
                anchor="w"
            )
            y_offset += 18
            
            # 内容项
            for item in items:
                self.canvas.create_text(
                    panel_x + 20, y_offset,
                    text=item,
                    font=("Microsoft YaHei", 8),
                    fill="#495057",
                    anchor="w"
                )
                y_offset += 15
            
            y_offset += 5  # 组间距

    def _set_buttons_state(self, state):
        buttons = [self.enqueue_btn, self.dequeue_btn, self.clear_btn, self.back_btn, self.batch_btn, self.random_btn, self.bfs_btn]
        for btn in buttons:
            if btn:
                btn.config(state=state)
        
        if self.input_frame:
            for child in self.input_frame.winfo_children():
                if hasattr(child, 'config') and 'state' in child.config():
                    child.config(state=state)

    def open_bfs_demo(self):
        """打开BFS广度优先遍历演示窗口"""
        if self.animating:
            messagebox.showwarning("提示", "动画进行中，请稍候")
            return
        # 打开BFS可视化窗口，传入当前代码语言
        open_bfs_visualizer(self.window, self.model, self.current_code_language)

    def back_to_main(self):
        if self.animating:
            messagebox.showinfo("提示", "动画尚在进行，无法返回")
            return
        self.window.destroy()

if __name__ == '__main__':
    root = Tk()
    root.title("循环队列可视化系统")
    root.geometry("1450x900")  # 增大窗口以容纳伪代码面板和环形视图
    root.configure(bg="#F5F7FA")
    CircularQueueVisualizer(root)
    root.mainloop()