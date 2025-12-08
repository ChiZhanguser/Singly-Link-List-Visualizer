from tkinter import *
from tkinter import messagebox, ttk, Entry
from typing import Dict, Tuple, List, Optional
from trie.trie_model import TrieModel, TrieNode
from DSL_utils import process_command
from llm import function_dispatcher
import time

# 深色主题颜色常量（与链表可视化保持一致）
THEME_COLORS = {
    "bg_dark": "#1a1a2e",
    "bg_card": "#16213e",
    "bg_input": "#0f0f23",
    "neon_cyan": "#00FFE5",
    "neon_pink": "#FF2E97",
    "neon_purple": "#A855F7",
    "neon_blue": "#4d96ff",
    "neon_green": "#6bcb77",
    "neon_orange": "#F97316",
    "neon_yellow": "#ffd93d",
    "neon_red": "#ff6b6b",
    "text_primary": "#e8e8e8",
    "text_secondary": "#a8a8a8",
}

class TrieVisualizer:
    def __init__(self, root):
        self.window = root
        self.window.title("Trie（字典树）可视化 - 带伪代码演示")
        self.window.config(bg="#1a1a2e")
        self.window.geometry("1400x800")
        
        # 伪代码相关变量（需要在创建面板前初始化）
        self.pseudo_code_lines = []
        self.current_highlight_line = -1
        self.animation_speed = 0.5  # 动画速度（秒）
        
        # DSL相关变量
        self.dsl_var = StringVar(value="")
        
        # LLM聊天窗口引用
        self.chat_window = None
        
        self.left_width = 300
        main = Frame(self.window, bg="#1a1a2e")
        main.pack(fill=BOTH, expand=True)
        self.status_text_var = StringVar(value="就绪：可插入 / 查找 / 清空。")
        
        # 左侧控制面板
        self.left_panel = Frame(main, width=self.left_width, bg="#16213e")
        self.left_panel.pack(side=LEFT, fill=Y, padx=(0, 0))
        self.left_panel.pack_propagate(False)
        self._build_left_panel()
        
        # 中间画布区域（含滚动条）
        center = Frame(main, bg="#0f0f23")
        center.pack(side=LEFT, fill=BOTH, expand=True, padx=(0,0), pady=0)
        
        # canvas + scrollbars
        self.canvas = Canvas(center, bg="#0f0f23", bd=0, highlightthickness=2, highlightbackground="#4a4e69")
        self.h_scroll = Scrollbar(center, orient=HORIZONTAL, command=self.canvas.xview)
        self.v_scroll = Scrollbar(center, orient=VERTICAL, command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=self.h_scroll.set, yscrollcommand=self.v_scroll.set)
        
        # place
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.v_scroll.grid(row=0, column=1, sticky="ns")
        self.h_scroll.grid(row=1, column=0, sticky="ew")
        center.grid_rowconfigure(0, weight=1)
        center.grid_columnconfigure(0, weight=1)
        
        # enable panning by mouse drag
        self.canvas.bind("<ButtonPress-1>", lambda e: self.canvas.scan_mark(e.x, e.y))
        self.canvas.bind("<B1-Motion>", lambda e: self.canvas.scan_dragto(e.x, e.y, gain=1))
        
        # 鼠标滚轮支持
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Button-4>", self._on_mousewheel)  # Linux
        self.canvas.bind("<Button-5>", self._on_mousewheel)  # Linux
        
        # 右侧伪代码面板
        self.create_pseudo_code_panel(main)
        
        # model
        self.model = TrieModel()
        
        # drawing bookkeeping
        self.node_items: Dict[TrieNode, int] = {}
        self.edge_items: List[int] = []
        self.text_items: Dict[TrieNode, int] = {}  # 节点文字
        
        # layout params (visual)
        self.node_w = 70
        self.node_h = 44
        self.level_gap = 100
        self.margin_x = 100
        self.top_margin = 100
        self.min_canvas_width = 800
        self.min_canvas_height = 600
        
        # 颜色配置
        self.colors = {
            "node_default": "#2d3a4f",
            "node_highlight": "#ffd93d",  # 当前访问
            "node_new": "#6bcb77",  # 新创建
            "node_end": "#4d96ff",  # 结束标记
            "node_found": "#6bcb77",  # 找到
            "node_not_found": "#ff6b6b",  # 未找到
            "text_default": "#e8e8e8",
            "text_highlight": "#1a1a2e",
            "edge_default": "#4a4e69",
            "edge_highlight": "#ffd93d",
        }
        
        # 初始化标志
        self._first_draw = True
        
        # animation state
        self.animating = False
        
        # 当前指针位置（用于动画）
        self.current_pointer_id = None
        
        # 延迟初始绘制，确保窗口尺寸已确定
        self.window.after(100, self.redraw)
        
        # 注册到LLM函数调度器
        try:
            function_dispatcher.register_visualizer("trie", self)
            print("Trie visualizer registered.")
        except Exception as e:
            print("Trie registered failed:", e)

    def create_pseudo_code_panel(self, parent):
        """创建伪代码显示面板（固定在右侧）"""
        pseudo_frame = Frame(parent, bg="#16213e", relief=FLAT, bd=0, width=320)
        pseudo_frame.pack(side=RIGHT, fill=Y, padx=(0, 0))
        pseudo_frame.pack_propagate(False)
        
        # 标题
        title_frame = Frame(pseudo_frame, bg="#e94560")
        title_frame.pack(fill=X)
        title_label = Label(title_frame, text="📋 伪代码执行过程", 
                           font=("微软雅黑", 12, "bold"), 
                           bg="#e94560", fg="white", pady=8)
        title_label.pack(fill=X)
        
        # 当前操作标签
        self.operation_label = Label(pseudo_frame, text="等待操作...", 
                                     font=("微软雅黑", 10, "bold"), 
                                     bg="#16213e", fg="#ffd93d", 
                                     wraplength=300, justify=LEFT,
                                     pady=8)
        self.operation_label.pack(fill=X, padx=10)
        
        # 分隔线
        separator = Frame(pseudo_frame, height=1, bg="#4a4e69")
        separator.pack(fill=X, padx=10, pady=(0, 8))
        
        # 伪代码显示区域
        code_container = Frame(pseudo_frame, bg="#0f0f23")
        code_container.pack(fill=BOTH, expand=True, padx=10, pady=(0, 8))
        
        self.pseudo_text = Text(code_container, 
                               font=("Consolas", 11), 
                               bg="#0f0f23", fg="#b2bec3",
                               relief=FLAT, 
                               wrap=NONE,
                               padx=12, pady=10,
                               cursor="arrow",
                               state=DISABLED,
                               height=18,
                               width=36)
        self.pseudo_text.pack(fill=BOTH, expand=True)
        
        # 配置高亮标签样式
        self.pseudo_text.tag_configure("highlight", 
                                       background="#ffd93d", 
                                       foreground="#1a1a2e",
                                       font=("Consolas", 11, "bold"))
        self.pseudo_text.tag_configure("executed", 
                                       foreground="#6bcb77")
        self.pseudo_text.tag_configure("pending", 
                                       foreground="#636e72")
        self.pseudo_text.tag_configure("comment",
                                       foreground="#4a4e69",
                                       font=("Consolas", 10, "italic"))
        
        # 进度指示器
        progress_frame = Frame(pseudo_frame, bg="#16213e")
        progress_frame.pack(fill=X, padx=10, pady=(0, 8))
        
        self.progress_label = Label(progress_frame, text="步骤: 0/0", 
                                    font=("Arial", 9), 
                                    bg="#16213e", fg="#b2bec3")
        self.progress_label.pack(side=LEFT)
        
        self.status_indicator = Label(progress_frame, text="⚫ 空闲", 
                                      font=("Arial", 9), 
                                      bg="#16213e", fg="#b2bec3")
        self.status_indicator.pack(side=RIGHT)
        
        # 分隔线
        control_separator = Frame(pseudo_frame, height=1, bg="#4a4e69")
        control_separator.pack(fill=X, padx=10, pady=5)
        
        # 速度控制
        speed_frame = Frame(pseudo_frame, bg="#16213e")
        speed_frame.pack(fill=X, padx=10, pady=(5, 10))
        
        speed_label = Label(speed_frame, text="⚡ 动画速度:", font=("Arial", 9), 
                           bg="#16213e", fg="#e8e8e8")
        speed_label.pack(side=LEFT)
        
        self.speed_var = DoubleVar(value=self.animation_speed)
        speed_scale = Scale(speed_frame, from_=0.1, to=1.5, resolution=0.1, 
                           orient=HORIZONTAL, variable=self.speed_var,
                           command=self._update_speed, length=160,
                           bg="#16213e", fg="#e8e8e8", highlightthickness=0,
                           troughcolor="#0f0f23", activebackground="#e94560",
                           font=("Arial", 8))
        speed_scale.pack(side=RIGHT, padx=5)
        
        # 当前状态说明框
        explain_frame = Frame(pseudo_frame, bg="#1a1a2e", relief=SOLID, bd=1)
        explain_frame.pack(fill=X, padx=10, pady=(5, 10))
        
        self.explain_label = Label(explain_frame, 
                                   text="💡 提示：点击插入或查找按钮开始演示",
                                   font=("微软雅黑", 9),
                                   bg="#1a1a2e", fg="#a8a8a8",
                                   wraplength=280, justify=LEFT,
                                   pady=8, padx=8)
        self.explain_label.pack(fill=X)

    def _update_speed(self, value):
        """更新动画速度"""
        self.animation_speed = float(value)

    def set_pseudo_code(self, title, lines):
        """设置要显示的伪代码"""
        self.pseudo_code_lines = lines
        self.current_highlight_line = -1
        
        self.operation_label.config(text=title, fg="#ffd93d")
        self.status_indicator.config(text="🟢 执行中", fg="#6bcb77")
        
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
            time.sleep(self.animation_speed * 0.5)

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
        self.status_indicator.config(text="✅ 完成", fg="#6bcb77")
        self.progress_label.config(text=f"步骤: {len(self.pseudo_code_lines)}/{len(self.pseudo_code_lines)}")
        self.window.update()

    def clear_pseudo_code(self):
        """清除伪代码显示"""
        self.pseudo_code_lines = []
        self.current_highlight_line = -1
        
        self.operation_label.config(text="等待操作...", fg="#ffd93d")
        self.status_indicator.config(text="⚫ 空闲", fg="#b2bec3")
        self.progress_label.config(text="步骤: 0/0")
        
        self.pseudo_text.config(state=NORMAL)
        self.pseudo_text.delete(1.0, END)
        self.pseudo_text.config(state=DISABLED)
        self.window.update()

    def update_explain(self, text: str):
        """更新说明文本"""
        self.explain_label.config(text=text)
        self.window.update()

    def _on_mousewheel(self, event):
        """处理鼠标滚轮事件"""
        if event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")
        elif event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")

    def _build_left_panel(self):
        pad = 12
        # 标题区域
        title_frame = Frame(self.left_panel, bg="#e94560")
        title_frame.pack(fill=X, pady=(0, 0))
        title = Label(title_frame, text="🌳 Trie 字典树", font=("微软雅黑", 14, "bold"), 
                      bg="#e94560", fg="white")
        title.pack(pady=(14,4))
        subtitle = Label(title_frame, text="前缀树 · 逐字符动画演示", 
                         bg="#e94560", fg="#ffccd5",
                         font=("微软雅黑", 9))
        subtitle.pack(pady=(0,12))
        
        # 输入框区域
        frm = Frame(self.left_panel, bg="#16213e")
        frm.pack(padx=pad, pady=(16,8), fill=X)
        Label(frm, text="📝 输入单词 (逗号/空格分隔):", 
              font=("微软雅黑", 9), bg="#16213e", fg="#a8a8a8").pack(anchor="w")
        
        # 输入框
        self.input_var = StringVar()
        entry_frame = Frame(frm, bg="#0f0f23", bd=1, relief=SOLID)
        entry_frame.pack(fill=X, pady=(6,0))
        entry = Entry(entry_frame, textvariable=self.input_var, 
                      font=("Consolas", 11),
                      relief=FLAT,
                      bg="#0f0f23",
                      fg="#e8e8e8",
                      insertbackground="#ffd93d",
                      bd=0)
        entry.pack(fill=X, ipady=8, padx=8)
        entry.insert(0, "apple, apply, app")
        
        # 回车默认触发 DSL
        entry.bind("<Return>", lambda e: self.process_dsl())
        entry.bind("<KP_Enter>", lambda e: self.process_dsl())
        
        # 按钮样式
        style_btn = {
            "bd": 0,
            "relief": FLAT,
            "padx": 16,
            "pady": 10,
            "font": ("微软雅黑", 10, "bold"),
            "cursor": "hand2"
        }
        
        # 按钮组
        btn_frame = Frame(self.left_panel, bg="#16213e")
        btn_frame.pack(padx=pad, pady=(16,8), fill=X)
        
        b_insert = Button(btn_frame, text="📥 插入（动画）", 
                          bg="#6bcb77", fg="white",
                          activebackground="#4a9d5a",
                          activeforeground="white",
                          command=self.start_insert_animated, **style_btn)
        b_insert.pack(fill=X, pady=(0,8))
        
        b_search = Button(btn_frame, text="🔍 查找（动画）", 
                          bg="#4d96ff", fg="white",
                          activebackground="#3a7bd5",
                          activeforeground="white",
                          command=self.start_search_animated, **style_btn)
        b_search.pack(fill=X, pady=(0,8))
        
        b_clear = Button(btn_frame, text="🗑️ 清空 Trie", 
                         bg="#ff6b6b", fg="white",
                         activebackground="#d63031",
                         activeforeground="white",
                         command=self.clear_trie, **style_btn)
        b_clear.pack(fill=X, pady=(0,0))
        
        # 分隔线
        sep_frame = Frame(self.left_panel, height=1, bg="#4a4e69")
        sep_frame.pack(fill=X, padx=pad, pady=(16,12))
        
        # DSL命令输入区域
        dsl_frame = Frame(self.left_panel, bg="#16213e")
        dsl_frame.pack(fill=X, padx=pad, pady=(0, 8))
        
        dsl_title_frame = Frame(dsl_frame, bg="#16213e")
        dsl_title_frame.pack(fill=X)
        
        Label(dsl_title_frame, text="⚡ DSL命令", 
              font=("微软雅黑", 9, "bold"), 
              bg="#16213e", fg=THEME_COLORS["neon_purple"]).pack(side=LEFT)
        
        # DSL帮助按钮
        def show_dsl_help():
            help_text = """
╔══════════════════════════════════════╗
║          📖 Trie DSL 命令帮助          ║
╠══════════════════════════════════════╣
║                                      ║
║  📥 插入操作:                         ║
║    insert word1, word2, word3        ║
║    add apple, app, application       ║
║                                      ║
║  🔍 查找操作:                         ║
║    search word                       ║
║    find apple                        ║
║                                      ║
║  🗑️ 清空操作:                         ║
║    clear                             ║
║    reset                             ║
║                                      ║
║  ℹ️ 帮助:                             ║
║    help                              ║
║                                      ║
║  💡 提示:                             ║
║    直接输入单词也会当作insert处理     ║
║    例如: apple, app, bat             ║
║                                      ║
╚══════════════════════════════════════╝
            """
            messagebox.showinfo("DSL 命令帮助", help_text)
        
        help_btn = Button(dsl_title_frame, text="?", 
                         font=("Arial", 8, "bold"),
                         bg="#4a4e69", fg="white",
                         activebackground="#5a5e79",
                         bd=0, padx=6, pady=1,
                         cursor="hand2",
                         command=show_dsl_help)
        help_btn.pack(side=RIGHT)
        
        # DSL输入框
        dsl_entry_frame = Frame(dsl_frame, bg="#0f0f23", bd=1, relief=SOLID)
        dsl_entry_frame.pack(fill=X, pady=(6,0))
        
        self.dsl_entry = Entry(dsl_entry_frame, 
                              textvariable=self.dsl_var,
                              font=("Consolas", 10),
                              bg="#0f0f23",
                              fg=THEME_COLORS["text_primary"],
                              insertbackground=THEME_COLORS["neon_purple"],
                              relief=FLAT,
                              bd=0)
        self.dsl_entry.pack(fill=X, ipady=6, padx=8)
        self.dsl_entry.bind("<Return>", lambda e: self._execute_dsl())
        self.dsl_entry.bind("<KP_Enter>", lambda e: self._execute_dsl())
        
        # DSL执行按钮
        dsl_btn_frame = Frame(dsl_frame, bg="#16213e")
        dsl_btn_frame.pack(fill=X, pady=(6,0))
        
        dsl_exec_btn = Button(dsl_btn_frame, text="▶ 执行DSL",
                             font=("微软雅黑", 9, "bold"),
                             bg=THEME_COLORS["neon_purple"], fg="white",
                             activebackground="#8B44CC",
                             activeforeground="white",
                             bd=0, padx=12, pady=6,
                             cursor="hand2",
                             command=self._execute_dsl)
        dsl_exec_btn.pack(fill=X)
        
        # 分隔线
        sep_frame2 = Frame(self.left_panel, height=1, bg="#4a4e69")
        sep_frame2.pack(fill=X, padx=pad, pady=(12,12))
        
        # 当前词表区域
        list_frame = Frame(self.left_panel, bg="#16213e")
        list_frame.pack(fill=X, padx=pad)
        Label(list_frame, 
              text="📚 已插入的单词：", 
              bg="#16213e",
              font=("微软雅黑", 9, "bold"),
              fg="#a8a8a8").pack(anchor="w")
              
        # 列表框
        list_container = Frame(list_frame, bg="#0f0f23", bd=1, relief=SOLID)
        list_container.pack(fill=X, pady=(6,0))
        self.word_listbox = Listbox(list_container, 
                                    height=6,
                                    font=("Consolas", 10),
                                    bg="#0f0f23",
                                    fg="#e8e8e8",
                                    selectmode=BROWSE,
                                    activestyle="none",
                                    relief=FLAT,
                                    selectbackground="#e94560",
                                    selectforeground="white",
                                    bd=0)
        self.word_listbox.pack(fill=X, padx=2, pady=2)
        
        # 状态栏
        sep_frame2 = Frame(self.left_panel, height=1, bg="#4a4e69")
        sep_frame2.pack(fill=X, padx=pad, pady=(16,10))
        
        status_frame = Frame(self.left_panel, bg="#1a1a2e", bd=1, relief=SOLID)
        status_frame.pack(fill=X, padx=pad, pady=(0,10))
        status_lbl = Label(status_frame, 
                           textvariable=self.status_text_var,
                           wraplength=self.left_width-32,
                           bg="#1a1a2e",
                           justify=LEFT,
                           fg="#ffd93d",
                           font=("微软雅黑", 9),
                           padx=10, pady=8)
        status_lbl.pack(anchor="w")
        
        # Trie 结构说明
        info_frame = Frame(self.left_panel, bg="#0f0f23", bd=1, relief=SOLID)
        info_frame.pack(fill=X, padx=pad, pady=(8,12))
        
        info_text = ("📖 Trie 树特点：\n"
                     "• 根节点为空，不存储字符\n"
                     "• 每个节点存储一个字符\n"
                     "• 从根到叶的路径组成单词\n"
                     "• ✓ 标记表示单词结束")
                     
        Label(info_frame, 
              text=info_text,
              bg="#0f0f23",
              fg="#6b7280",
              justify=LEFT,
              font=("微软雅黑", 8),
              wraplength=self.left_width-40,
              padx=10,
              pady=8).pack()

    def update_status(self, txt: str):
        self.status_text_var.set(txt)

    def compute_positions(self) -> Dict[TrieNode, Tuple[float,float]]:
        """计算所有节点的位置，返回 {node: (x, y)} 字典"""
        pos: Dict[TrieNode, Tuple[float,float]] = {}
        levels = self.model.nodes_by_level()
        if not levels:
            return pos
        max_depth = max(levels.keys())
        
        # 计算每层最大节点数
        max_nodes_per_level = max(len(nodes) for nodes in levels.values())
        
        # 计算所需的最小宽度
        min_node_spacing = 50
        min_required_width = max_nodes_per_level * (self.node_w + min_node_spacing) + 2 * self.margin_x
        
        # 获取可用宽度
        self.canvas.update_idletasks()
        canvas_width = max(self.canvas.winfo_width(), 600)
        avail_width = max(canvas_width, min_required_width)
        
        # 计算所需高度
        required_height = (max_depth + 1) * self.level_gap + self.top_margin * 2
        
        # 计算节点位置
        for depth in range(1, max_depth+1):
            nodes = levels.get(depth, [])
            n = len(nodes)
            if n == 0:
                continue
            
            # 计算这一层可用的宽度
            usable_width = avail_width - 2 * self.margin_x
            
            for i, node in enumerate(nodes):
                if n == 1:
                    x = avail_width / 2
                else:
                    x = self.margin_x + i * (usable_width / (n - 1))
                
                y = self.top_margin + depth * self.level_gap
                pos[node] = (x, y)
        
        return pos, avail_width, required_height

    def redraw(self, highlight: Optional[Dict[TrieNode, str]] = None):
        """重新绘制整个 Trie 树"""
        self.canvas.delete("all")
        self.node_items.clear()
        self.edge_items.clear()
        self.text_items.clear()

        # 计算节点位置和所需画布大小
        pos_result = self.compute_positions()
        if not pos_result or not pos_result[0]:
            # 空树
            self.canvas.update_idletasks()
            canvas_width = max(self.canvas.winfo_width(), self.min_canvas_width)
            canvas_height = max(self.canvas.winfo_height(), self.min_canvas_height)
            
            self.canvas.config(scrollregion=(0, 0, canvas_width, canvas_height))
            
            # 显示提示
            self.canvas.create_text(canvas_width / 2, canvas_height / 2 - 30, 
                                   text="🌳 空的 Trie 树", 
                                   font=("微软雅黑", 20, "bold"), 
                                   fill="#4a4e69",
                                   anchor="center")
            self.canvas.create_text(canvas_width / 2, canvas_height / 2 + 20, 
                                   text="请在左侧输入单词并点击插入", 
                                   font=("微软雅黑", 12), 
                                   fill="#636e72",
                                   anchor="center")
            return
        
        pos, total_width, total_height = pos_result

        # 绘制边（先绘制，使其在节点下方）
        for node, (cx, cy) in pos.items():
            parent = node.parent
            if parent and parent is not self.model.root and parent in pos:
                px, py = pos[parent]
                # 绘制边（带字符标签）
                line = self.canvas.create_line(
                    px, py + self.node_h/2 + 2, 
                    cx, cy - self.node_h/2 - 2, 
                    width=2, fill=self.colors["edge_default"],
                    smooth=True
                )
                self.edge_items.append(line)
                
                # 在边中间绘制字符标签
                mid_x = (px + cx) / 2
                mid_y = (py + self.node_h/2 + cy - self.node_h/2) / 2
                self.canvas.create_oval(mid_x-12, mid_y-10, mid_x+12, mid_y+10,
                                       fill="#1a1a2e", outline=self.colors["edge_default"])
                self.canvas.create_text(mid_x, mid_y, text=node.char,
                                       font=("Consolas", 9, "bold"),
                                       fill="#ffd93d")

        # 计算 root 位置（第一层节点的中心）
        first_level_nodes = self.model.nodes_by_level().get(1, [])
        if first_level_nodes:
            xs = [pos[n][0] for n in first_level_nodes if n in pos]
            root_x = sum(xs) / len(xs) if xs else (total_width / 2)
        else:
            root_x = total_width / 2
        root_y = self.top_margin / 2

        # 绘制从 root 到第一层的边
        for node in first_level_nodes:
            if node in pos:
                cx, cy = pos[node]
                line = self.canvas.create_line(
                    root_x, root_y + 22, 
                    cx, cy - self.node_h/2 - 2, 
                    width=2, fill=self.colors["edge_default"],
                    smooth=True
                )
                self.edge_items.append(line)
                
                # 边上的字符标签
                mid_x = (root_x + cx) / 2
                mid_y = (root_y + 22 + cy - self.node_h/2) / 2
                self.canvas.create_oval(mid_x-12, mid_y-10, mid_x+12, mid_y+10,
                                       fill="#1a1a2e", outline=self.colors["edge_default"])
                self.canvas.create_text(mid_x, mid_y, text=node.char,
                                       font=("Consolas", 9, "bold"),
                                       fill="#ffd93d")

        # 绘制节点
        for node, (cx, cy) in pos.items():
            color = None
            if highlight and node in highlight:
                color = highlight[node]
            self._draw_node(node, cx, cy, fill_color=color)

        # 绘制 root 标记
        self._draw_root_node(root_x, root_y)
        
        # 调整滚动区域
        self._adjust_scroll_region()

    def _draw_root_node(self, x, y):
        """绘制根节点"""
        # 外圈光晕
        self.canvas.create_oval(
            x-28, y-18, x+28, y+18,
            fill="#e94560", outline="", 
        )
        # 主体
        self.canvas.create_oval(
            x-24, y-14, x+24, y+14,
            fill="#e94560", outline="#ff8fab", width=2
        )
        self.canvas.create_text(
            x, y, 
            text="ROOT", 
            font=("Consolas", 10, "bold"),
            fill="white"
        )

    def _adjust_scroll_region(self):
        """调整画布滚动区域"""
        bbox = self.canvas.bbox("all")
        
        if bbox:
            left, top, right, bottom = bbox
            content_width = right - left
            content_height = bottom - top

            self.canvas.update_idletasks()
            canvas_width = max(self.canvas.winfo_width(), self.min_canvas_width)
            canvas_height = max(self.canvas.winfo_height(), self.min_canvas_height)

            pad_x = 100
            pad_y = 80

            scroll_width = max(content_width + 2 * pad_x, canvas_width)
            scroll_height = max(content_height + 2 * pad_y, canvas_height)

            content_center_x = left + content_width / 2
            content_center_y = top + content_height / 2

            scroll_left = content_center_x - scroll_width / 2
            scroll_top = content_center_y - scroll_height / 2
            scroll_right = scroll_left + scroll_width
            scroll_bottom = scroll_top + scroll_height

            self.canvas.config(scrollregion=(
                scroll_left, scroll_top, scroll_right, scroll_bottom
            ))

            desired_view_left = content_center_x - canvas_width / 2
            desired_view_top = content_center_y - canvas_height / 2

            if scroll_width > 0:
                x_fraction = (desired_view_left - scroll_left) / scroll_width
            else:
                x_fraction = 0.0
                
            if scroll_height > 0:
                y_fraction = (desired_view_top - scroll_top) / scroll_height
            else:
                y_fraction = 0.0

            self.canvas.xview('moveto', x_fraction)
            self.canvas.yview('moveto', y_fraction)

    def _draw_node(self, node: TrieNode, cx: float, cy: float, fill_color: Optional[str] = None):
        """绘制单个节点"""
        left = cx - self.node_w/2
        top = cy - self.node_h/2
        right = cx + self.node_w/2
        bottom = cy + self.node_h/2
        
        # 根据节点状态设置颜色
        if fill_color:
            fill = fill_color
            text_color = self.colors["text_highlight"] if fill_color == self.colors["node_highlight"] else self.colors["text_default"]
        elif node.is_end:
            fill = self.colors["node_end"]
            text_color = self.colors["text_default"]
        else:
            fill = self.colors["node_default"]
            text_color = self.colors["text_default"]
        
        # 节点阴影
        self.canvas.create_rectangle(
            left+3, top+3, right+3, bottom+3,
            fill="#0a0a14", outline=""
        )
        
        # 节点主体（圆角效果通过多边形实现）
        r = 8  # 圆角半径
        rect = self.canvas.create_polygon(
            left+r, top,
            right-r, top,
            right, top+r,
            right, bottom-r,
            right-r, bottom,
            left+r, bottom,
            left, bottom-r,
            left, top+r,
            fill=fill, outline="#e8e8e8", width=2, smooth=True
        )
        self.node_items[node] = rect
        
        # 显示字符
        text_id = self.canvas.create_text(
            cx, cy, 
            text=node.char, 
            font=("Consolas", 16, "bold"), 
            fill=text_color
        )
        self.text_items[node] = text_id
        
        # 如果是结束节点，显示标记
        if node.is_end:
            self.canvas.create_oval(
                right-16, top+4, right-2, top+18, 
                fill="#6bcb77", outline="#4a9d5a", width=1
            )
            self.canvas.create_text(
                right-9, top+11,
                text="✓",
                font=("Arial", 8, "bold"),
                fill="white"
            )

    def draw_pointer(self, x, y, text="cur"):
        """绘制当前指针"""
        self.clear_pointer()
        
        # 指针箭头
        arrow = self.canvas.create_polygon(
            x, y - 35,
            x - 8, y - 50,
            x + 8, y - 50,
            fill="#e94560", outline="#ff8fab", width=2
        )
        
        # 指针标签
        label_bg = self.canvas.create_rectangle(
            x - 20, y - 70, x + 20, y - 50,
            fill="#e94560", outline=""
        )
        label_text = self.canvas.create_text(
            x, y - 60, text=text,
            font=("Consolas", 10, "bold"),
            fill="white"
        )
        
        self.current_pointer_id = (arrow, label_bg, label_text)
        return self.current_pointer_id

    def clear_pointer(self):
        """清除当前指针"""
        if self.current_pointer_id:
            for item in self.current_pointer_id:
                self.canvas.delete(item)
            self.current_pointer_id = None

    def parse_input_words(self) -> List[str]:
        """解析输入框中的单词列表"""
        text = self.input_var.get().strip()
        if not text:
            return []
        parts = [p.strip() for p in text.replace(",", " ").split() if p.strip()]
        return parts

    def clear_trie(self):
        """清空 Trie 树"""
        if self.animating:
            return
        self.model.clear()
        self.word_listbox.delete(0, END)
        self.clear_pseudo_code()
        self.redraw()
        self.update_status("✅ 已清空 Trie 树")
        self.update_explain("💡 Trie 已清空，可以开始插入新单词")

    def start_insert_animated(self):
        """开始插入动画"""
        if self.animating:
            return
        words = self.parse_input_words()
        if not words:
            messagebox.showinfo("提示", "请输入单词（或逗号/空格分隔多个）")
            return
        
        self.animating = True
        word_idx = 0
        
        def process_next_word():
            nonlocal word_idx
            if word_idx >= len(words):
                self.animating = False
                self.complete_pseudo_code()
                self.update_status(f"✅ 插入完成：共插入 {len(words)} 个单词")
                self.update_explain("🎉 所有单词插入完成！Trie 树已更新。")
                return
            word = words[word_idx]
            word_idx += 1
            self._animate_insert_word_with_pseudo(word, process_next_word)

        process_next_word()

    def _animate_insert_word_with_pseudo(self, word: str, callback):
        """逐字符动画插入单词 - 带伪代码高亮"""
        # 设置伪代码
        pseudo_lines = [
            f"// 插入单词: \"{word}\"",
            "Insert(word):",
            "    cur = root",
            f"    for ch in \"{word}\":",
            "        if ch not in cur.children:",
            "            cur.children[ch] = new Node(ch)",
            "        cur = cur.children[ch]",
            "    cur.is_end = True  // 标记单词结束",
            "// 插入完成 ✓"
        ]
        self.set_pseudo_code(f"🔤 插入: {word}", pseudo_lines)
        
        self.update_explain(f"📝 开始插入单词 \"{word}\"，共 {len(word)} 个字符")
        self.update_status(f"正在插入: {word}")
        
        # 高亮前两行
        self.highlight_pseudo_line(0, delay=False)
        time.sleep(self.animation_speed * 0.3)
        self.highlight_pseudo_line(1, delay=False)
        time.sleep(self.animation_speed * 0.3)
        self.highlight_pseudo_line(2)  # cur = root
        
        cur = self.model.root
        pos_nodes: List[TrieNode] = []
        i = 0
        created_nodes: List[TrieNode] = []

        def step():
            nonlocal cur, i
            if i >= len(word):
                # 标记单词结束
                if cur is not self.model.root:
                    cur.is_end = True
                
                self.highlight_pseudo_line(7)  # cur.is_end = True
                self.update_explain(f"✅ 标记 \"{word}\" 的最后一个字符为单词结束")
                
                # 最终高亮
                if pos_nodes:
                    last = pos_nodes[-1]
                    highlight = {n: self.colors["node_highlight"] for n in pos_nodes[:-1]}
                    highlight[last] = self.colors["node_found"]
                    self.redraw(highlight=highlight)
                
                time.sleep(self.animation_speed)
                self.highlight_pseudo_line(8)  # 插入完成
                
                # 更新词表
                current_words = set(self.word_listbox.get(0, END))
                if word not in current_words:
                    self.word_listbox.insert(END, word)
                
                self.update_status(f"✅ 单词 \"{word}\" 插入完成")
                self.update_explain(f"🎯 成功插入 \"{word}\"！新增 {len(created_nodes)} 个节点")
                
                # 恢复正常显示
                self.window.after(int(self.animation_speed * 800), lambda: (
                    self.clear_pointer(),
                    self.redraw(),
                    callback()
                ))
                return
            
            ch = word[i]
            self.highlight_pseudo_line(3, delay=False)  # for ch in word
            self.update_explain(f"🔄 处理第 {i+1}/{len(word)} 个字符: '{ch}'")
            time.sleep(self.animation_speed * 0.3)
            
            if ch in cur.children:
                # 字符已存在
                self.highlight_pseudo_line(4, delay=False)  # if ch not in cur.children (false)
                self.update_explain(f"✓ 字符 '{ch}' 已存在于当前节点的子节点中")
                time.sleep(self.animation_speed * 0.3)
                
                self.highlight_pseudo_line(6)  # cur = cur.children[ch]
                self.update_explain(f"➡️ 移动到已有节点 '{ch}'")
                
                cur = cur.children[ch]
                pos_nodes.append(cur)
                
                # 更新显示
                highlight = {n: self.colors["node_highlight"] for n in pos_nodes}
                self.redraw(highlight=highlight)
                
                i += 1
                self.window.after(int(self.animation_speed * 600), step)
            else:
                # 需要创建新节点
                self.highlight_pseudo_line(4, delay=False)  # if ch not in cur.children (true)
                self.update_explain(f"❌ 字符 '{ch}' 不存在，需要创建新节点")
                time.sleep(self.animation_speed * 0.3)
                
                self.highlight_pseudo_line(5)  # cur.children[ch] = new Node(ch)
                self.update_explain(f"✨ 创建新节点: '{ch}'")
                
                node = TrieNode(ch)
                node.parent = cur
                cur.children[ch] = node
                
                time.sleep(self.animation_speed * 0.3)
                self.highlight_pseudo_line(6)  # cur = cur.children[ch]
                self.update_explain(f"➡️ 移动到新创建的节点 '{ch}'")
                
                cur = node
                pos_nodes.append(cur)
                created_nodes.append(cur)
                
                # 更新显示 - 新节点使用绿色高亮
                hl = {n: self.colors["node_highlight"] for n in pos_nodes[:-1]}
                hl[cur] = self.colors["node_new"]
                self.redraw(highlight=hl)
                
                i += 1
                self.window.after(int(self.animation_speed * 800), step)

        step()

    def start_search_animated(self):
        """开始查找动画"""
        if self.animating:
            return
        words = self.parse_input_words()
        if not words:
            messagebox.showinfo("提示", "请输入要查找的单词")
            return
        
        # 只取第一个词进行查找
        word = words[0]
        self.input_var.set(word)
        
        self.animating = True
        self._animate_search_word_with_pseudo(word)

    def _animate_search_word_with_pseudo(self, word: str):
        """逐字符动画查找单词 - 带伪代码高亮"""
        # 设置伪代码
        pseudo_lines = [
            f"// 查找单词: \"{word}\"",
            "Search(word):",
            "    cur = root",
            f"    for ch in \"{word}\":",
            "        if ch not in cur.children:",
            "            return False  // 路径不存在",
            "        cur = cur.children[ch]",
            "    return cur.is_end  // 是否为完整单词",
            "// 查找完成"
        ]
        self.set_pseudo_code(f"🔍 查找: {word}", pseudo_lines)
        
        self.update_explain(f"📝 开始查找单词 \"{word}\"，共 {len(word)} 个字符")
        self.update_status(f"正在查找: {word}")
        
        # 高亮前两行
        self.highlight_pseudo_line(0, delay=False)
        time.sleep(self.animation_speed * 0.3)
        self.highlight_pseudo_line(1, delay=False)
        time.sleep(self.animation_speed * 0.3)
        self.highlight_pseudo_line(2)  # cur = root
        
        cur = self.model.root
        path: List[TrieNode] = []
        i = 0

        def step():
            nonlocal cur, i
            if i >= len(word):
                # 检查是否为完整单词
                self.highlight_pseudo_line(7)  # return cur.is_end
                
                if cur.is_end:
                    self.update_explain(f"✅ 找到！\"{word}\" 是一个完整的单词")
                    self.update_status(f"✅ 查找成功: \"{word}\" 存在")
                    
                    # 高亮找到的路径
                    highlight = {n: self.colors["node_highlight"] for n in path[:-1]}
                    if path:
                        highlight[path[-1]] = self.colors["node_found"]
                    self.redraw(highlight=highlight)
                else:
                    self.update_explain(f"⚠️ \"{word}\" 只是前缀，不是完整单词")
                    self.update_status(f"⚠️ 查找结果: \"{word}\" 不是完整单词")
                    
                    # 高亮路径为警告色
                    highlight = {n: self.colors["node_highlight"] for n in path}
                    self.redraw(highlight=highlight)
                
                time.sleep(self.animation_speed)
                self.highlight_pseudo_line(8)  # 查找完成
                self.complete_pseudo_code()
                
                # 恢复正常显示
                self.window.after(int(self.animation_speed * 1200), lambda: (
                    self.clear_pointer(),
                    self.redraw(),
                    self._finish_search()
                ))
                return
            
            ch = word[i]
            self.highlight_pseudo_line(3, delay=False)  # for ch in word
            self.update_explain(f"🔄 查找第 {i+1}/{len(word)} 个字符: '{ch}'")
            time.sleep(self.animation_speed * 0.3)
            
            self.highlight_pseudo_line(4, delay=False)  # if ch not in cur.children
            
            if ch not in cur.children:
                # 字符不存在 - 查找失败
                self.highlight_pseudo_line(5)  # return False
                self.update_explain(f"❌ 字符 '{ch}' 不存在！查找失败")
                self.update_status(f"❌ 查找失败: \"{word}\" 不存在")
                
                # 高亮已搜索的路径为红色
                highlight = {n: self.colors["node_not_found"] for n in path}
                self.redraw(highlight=highlight)
                
                time.sleep(self.animation_speed)
                self.highlight_pseudo_line(8)
                self.complete_pseudo_code()
                
                self.window.after(int(self.animation_speed * 1200), lambda: (
                    self.clear_pointer(),
                    self.redraw(),
                    self._finish_search()
                ))
                return
            
            # 字符存在，继续
            self.update_explain(f"✓ 找到字符 '{ch}'")
            time.sleep(self.animation_speed * 0.3)
            
            self.highlight_pseudo_line(6)  # cur = cur.children[ch]
            self.update_explain(f"➡️ 移动到节点 '{ch}'")
            
            cur = cur.children[ch]
            path.append(cur)
            
            # 更新显示
            highlight = {n: self.colors["node_highlight"] for n in path}
            self.redraw(highlight=highlight)
            
            i += 1
            self.window.after(int(self.animation_speed * 600), step)

        step()

    def _finish_search(self):
        """查找完成后的清理"""
        self.animating = False

    def set_chat_window(self, chat_window):
        """设置LLM聊天窗口引用"""
        self.chat_window = chat_window
    
    def _execute_dsl(self, event=None):
        """执行DSL输入框中的命令"""
        if getattr(self, "animating", False):
            messagebox.showinfo("提示", "当前正在执行动画，请稍后再试。")
            return
        
        raw = (self.dsl_var.get() or "").strip()
        if not raw:
            return
        
        try:
            process_command(self, raw)
        except Exception as e:
            messagebox.showerror("DSL 执行错误", f"执行 DSL 时出错: {e}")
            self.update_status(f"DSL 错误: {e}")
        finally:
            try:
                self.dsl_var.set("")
            except:
                pass

    def process_dsl(self, event=None):
        """处理 DSL 命令（兼容旧的输入框方式）"""
        if getattr(self, "animating", False):
            messagebox.showinfo("提示", "当前正在执行动画，无法执行DSL，请稍后再试。")
            return

        raw = (self.input_var.get() or "").strip()
        if not raw:
            return

        try:
            process_command(self, raw)
        except Exception as e:
            if isinstance(e, NameError):
                self.update_status("DSL 未加载。请使用按钮操作。")
                self.start_insert_animated()
            else:
                messagebox.showerror("DSL 执行错误", f"执行 DSL 时出错: {e}")
                self.update_status("DSL 错误")

if __name__ == '__main__':
    root = Tk()
    app = TrieVisualizer(root)
    root.mainloop()
