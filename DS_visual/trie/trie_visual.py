from tkinter import *
from tkinter import messagebox, ttk, Entry
from typing import Dict, Tuple, List, Optional
from trie.trie_model import TrieModel, TrieNode
from DSL_utils import process_command
import time

class TrieVisualizer:
    def __init__(self, root):
        self.window = root
        self.window.title("Trie（字典树）可视化")
        self.window.config(bg="#EEF2F6")
        self.window.geometry("1200x720")
        self.left_width = 340
        main = Frame(self.window, bg="#EEF2F6")
        main.pack(fill=BOTH, expand=True)
        self.status_text_var = StringVar(value="就绪：可插入 / 查找 / 清空。")
        self.left_panel = Frame(main, width=self.left_width, bg="#FFFFFF")
        self.left_panel.pack(side=LEFT, fill=Y, padx=(12, 0))
        self.left_panel.pack_propagate(False)
        self._build_left_panel()
        
        # 右侧画布区域（含滚动条）
        right = Frame(main, bg="#F3F6FB")
        right.pack(side=LEFT, fill=BOTH, expand=True, padx=(10,12), pady=10)
        
        # canvas + scrollbars
        self.canvas = Canvas(right, bg="white", bd=4, relief=RIDGE)
        self.h_scroll = Scrollbar(right, orient=HORIZONTAL, command=self.canvas.xview)
        self.v_scroll = Scrollbar(right, orient=VERTICAL, command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=self.h_scroll.set, yscrollcommand=self.v_scroll.set)
        
        # place
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.v_scroll.grid(row=0, column=1, sticky="ns")
        self.h_scroll.grid(row=1, column=0, sticky="ew")
        right.grid_rowconfigure(0, weight=1)
        right.grid_columnconfigure(0, weight=1)
        
        # enable panning by mouse drag
        self.canvas.bind("<ButtonPress-1>", lambda e: self.canvas.scan_mark(e.x, e.y))
        self.canvas.bind("<B1-Motion>", lambda e: self.canvas.scan_dragto(e.x, e.y, gain=1))
        
        # 鼠标滚轮支持
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Button-4>", self._on_mousewheel)  # Linux
        self.canvas.bind("<Button-5>", self._on_mousewheel)  # Linux
        
        # model
        self.model = TrieModel()
        
        # drawing bookkeeping
        self.node_items: Dict[TrieNode, int] = {}
        self.edge_items: List[int] = []
        
        # layout params (visual)
        self.node_w = 80
        self.node_h = 48
        self.level_gap = 120  # 增加层级间距
        self.margin_x = 80
        self.top_margin = 80
        self.min_canvas_width = 800
        self.min_canvas_height = 600
        
        # 初始化标志
        self._first_draw = True
        
        # animation state
        self.animating = False
        
        # 延迟初始绘制，确保窗口尺寸已确定
        self.window.after(100, self.redraw)

    def _on_mousewheel(self, event):
        """处理鼠标滚轮事件"""
        if event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")
        elif event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")

    def _build_left_panel(self):
        pad = 16
        # 标题区域使用渐变色背景
        title_frame = Frame(self.left_panel, bg="#4A90E2")
        title_frame.pack(fill=X, pady=(0, 16))
        title = Label(title_frame, text="Trie 可视化", font=("Helvetica", 16, "bold"), 
                      bg="#4A90E2", fg="white")
        title.pack(pady=(18,6))
        subtitle = Label(title_frame, text="逐字动画 · 创建/查找/清空", 
                         bg="#4A90E2", fg="#E8F1FF")
        subtitle.pack(pady=(0,14))
        
        # 输入框区域
        frm = Frame(self.left_panel, bg="white")
        frm.pack(padx=pad, pady=(6,8), fill=X)
        Label(frm, text="输入单词 (逗号/空格分隔):", 
              font=("Arial", 10), bg="white", fg="#666666").pack(anchor="w")
        
        # 美化输入框
        self.input_var = StringVar()
        entry = Entry(frm, textvariable=self.input_var, 
                      font=("Arial", 12),
                      relief=FLAT,
                      bg="#F5F8FA",
                      insertbackground="#666666")
        entry.pack(fill=X, pady=(6,0), ipady=6)
        entry.insert(0, "apple, apply, after, buffer, ball")
        
        # 回车默认触发 DSL
        entry.bind("<Return>", lambda e: self.process_dsl())
        entry.bind("<KP_Enter>", lambda e: self.process_dsl())
        
        # 按钮组
        btn_frame = Frame(self.left_panel, bg="white")
        btn_frame.pack(padx=pad, pady=(16,14), fill=X)

        style_btn = {
            "bd": 0,
            "relief": FLAT,
            "padx": 12,
            "pady": 8,
            "font": ("Arial", 11, "bold"),
            "cursor": "hand2"
        }
        
        # 渐变风格的按钮
        b_insert = Button(btn_frame, text="插入（动画）", 
                          bg="#3B82F6", fg="white",
                          activebackground="#2563EB",
                          activeforeground="white",
                          command=self.start_insert_animated, **style_btn)
        b_search = Button(btn_frame, text="查找（动画）", 
                          bg="#10B981", fg="white",
                          activebackground="#059669",
                          activeforeground="white",
                          command=self.start_search_animated, **style_btn)
        b_clear = Button(btn_frame, text="清空", 
                         bg="#EF4444", fg="white",
                         activebackground="#DC2626",
                         activeforeground="white",
                         command=self.clear_trie, **style_btn)
                         
        # 添加阴影效果的按钮容器
        for btn in (b_insert, b_search, b_clear):
            frame = Frame(btn_frame, bg="#E5E7EB", bd=1, relief=SOLID)
            frame.pack(fill=X, pady=(0,8))
            btn.pack(fill=X, pady=1)
        
        # 优雅的分割线
        sep_frame = Frame(self.left_panel, height=2, bg="#E5E7EB")
        sep_frame.pack(fill=X, padx=pad, pady=(14,16))
        
        # 当前词表区域
        list_frame = Frame(self.left_panel, bg="white")
        list_frame.pack(fill=X, padx=pad)
        Label(list_frame, 
              text="当前已插入单词：", 
              bg="white",
              font=("Arial", 10, "bold"),
              fg="#374151").pack(anchor="w")
              
        # 美化列表框
        self.word_listbox = Listbox(list_frame, 
                                    height=8,
                                    font=("Arial", 11),
                                    bg="#F8FAFC",
                                    fg="#374151",
                                    selectmode=BROWSE,
                                    activestyle="none",
                                    relief=FLAT,
                                    selectbackground="#3B82F6",
                                    selectforeground="white")
        self.word_listbox.pack(fill=X, pady=(6,0))
        
        # 状态栏
        sep_frame2 = Frame(self.left_panel, height=2, bg="#E5E7EB")
        sep_frame2.pack(fill=X, padx=pad, pady=(16,12))
        
        status_frame = Frame(self.left_panel, bg="#F0F9FF", bd=1, relief=SOLID)
        status_frame.pack(fill=X, padx=pad, pady=(4,12))
        status_lbl = Label(status_frame, 
                           textvariable=self.status_text_var,
                           wraplength=self.left_width-32,
                           bg="#F0F9FF",
                           justify=LEFT,
                           fg="#0369A1",
                           padx=8, pady=6)
        status_lbl.pack(anchor="w")
        
        # 帮助说明区域
        help_frame = Frame(self.left_panel, bg="#F3F4F6", bd=1, relief=SOLID)
        help_frame.pack(fill=X, padx=pad, pady=(12,16))
        
        Label(help_frame, 
              text="使用帮助", 
              font=("Arial", 10, "bold"),
              bg="#F3F4F6",
              fg="#4B5563",
              padx=10,
              pady=8).pack(anchor="w", pady=(8,4))
              
        help_text = ("• 请使用插入按钮查看逐字创建/遍历动画。\n"
                     "• 树会自动居中显示，支持滚轮和拖拽浏览。\n"
                     "• 查找会高亮遍历路径（黄色），命中末尾为绿色。")
                     
        Label(help_frame, 
              text=help_text,
              bg="#F3F4F6",
              fg="#6B7280",
              justify=LEFT,
              wraplength=self.left_width-32,
              padx=10,
              pady=6).pack(padx=pad, pady=(0,10))

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
        min_node_spacing = 60  # 节点之间的最小间距
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
                    # 单个节点居中
                    x = avail_width / 2
                else:
                    # 多个节点均匀分布
                    x = self.margin_x + i * (usable_width / (n - 1))
                
                y = self.top_margin + depth * self.level_gap
                pos[node] = (x, y)
        
        return pos, avail_width, required_height

    def redraw(self, highlight: Optional[Dict[TrieNode, str]] = None):
        """重新绘制整个 Trie 树"""
        self.canvas.delete("all")
        self.node_items.clear()
        self.edge_items.clear()

        # 计算节点位置和所需画布大小
        pos_result = self.compute_positions()
        if not pos_result or not pos_result[0]:
            # 空树
            self.canvas.update_idletasks()
            canvas_width = max(self.canvas.winfo_width(), self.min_canvas_width)
            canvas_height = max(self.canvas.winfo_height(), self.min_canvas_height)
            
            # 设置滚动区域
            self.canvas.config(scrollregion=(0, 0, canvas_width, canvas_height))
            
            # 显示提示
            self.canvas.create_text(canvas_width / 2, canvas_height / 2, 
                                   text="空的 Trie（请插入单词）", 
                                   font=("Arial", 18), 
                                   fill="#94a3b8",
                                   anchor="center")
            return
        
        pos, total_width, total_height = pos_result

        # 提示文本
        self.canvas.create_text(12, 10, anchor="nw",
                              text="Trie：插入 / 查找 / 清空。动画显示逐字符访问与创建。",
                              font=("Arial", 11), fill="#334155")

        # 绘制边（先绘制，使其在节点下方）
        for node, (cx, cy) in pos.items():
            parent = node.parent
            if parent and parent is not self.model.root and parent in pos:
                px, py = pos[parent]
                line = self.canvas.create_line(
                    px, py + self.node_h/2, 
                    cx, cy - self.node_h/2, 
                    width=2, arrow=LAST, fill="#475569"
                )
                self.edge_items.append(line)

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
                    root_x, root_y + 20, 
                    cx, cy - self.node_h/2, 
                    width=2, arrow=LAST, fill="#475569"
                )
                self.edge_items.append(line)

        # 绘制节点
        for node, (cx, cy) in pos.items():
            color = None
            if highlight and node in highlight:
                color = highlight[node]
            self._draw_node(node, cx, cy, fill_color=color)

        # 绘制 root 标记 - 使用更明显的样式
        self.canvas.create_oval(
            root_x-20, root_y-12, 
            root_x+20, root_y+12, 
            fill="#4A90E2", outline="#1e40af", width=2
        )
        self.canvas.create_text(
            root_x, root_y, 
            text="ROOT", 
            font=("Arial", 10, "bold"),
            fill="white"
        )
        bbox = self.canvas.bbox("all")
        
        if bbox:
            # 1. 获取内容实际边界和尺寸
            left, top, right, bottom = bbox
            content_width = right - left
            content_height = bottom - top

            # 2. 获取画布尺寸
            self.canvas.update_idletasks()
            canvas_width = max(self.canvas.winfo_width(), self.min_canvas_width)
            canvas_height = max(self.canvas.winfo_height(), self.min_canvas_height)

            # 3. 定义边距
            pad_x = 100
            pad_y = 80

            # 4. 计算最终的滚动区域尺寸
            #    确保滚动区域至少和画布一样大，这样小树也能居中
            scroll_width = max(content_width + 2 * pad_x, canvas_width)
            scroll_height = max(content_height + 2 * pad_y, canvas_height)

            # 5. 计算内容中心点
            content_center_x = left + content_width / 2
            content_center_y = top + content_height / 2

            # 6. 计算滚动区域的左上角坐标
            #    目标：滚动区域的中心 应该等于 内容的中心
            scroll_left = content_center_x - scroll_width / 2
            scroll_top = content_center_y - scroll_height / 2
            scroll_right = scroll_left + scroll_width
            scroll_bottom = scroll_top + scroll_height

            # 7. 设置滚动区域
            self.canvas.config(scrollregion=(
                scroll_left, 
                scroll_top, 
                scroll_right, 
                scroll_bottom
            ))

            # 8. 自动滚动视图，将内容中心移动到画布中心
            #    计算画布中心点 (canvas_width / 2, canvas_height / 2) 
            #    应该对应滚动区域中的哪个坐标
            desired_view_left = content_center_x - canvas_width / 2
            desired_view_top = content_center_y - canvas_height / 2

            # 9. 将这个坐标转换为 0.0-1.0 的比例
            if scroll_width > 0:
                x_fraction = (desired_view_left - scroll_left) / scroll_width
            else:
                x_fraction = 0.0
                
            if scroll_height > 0:
                y_fraction = (desired_view_top - scroll_top) / scroll_height
            else:
                y_fraction = 0.0

            # 10. 移动视图
            self.canvas.xview('moveto', x_fraction)
            self.canvas.yview('moveto', y_fraction)

    def _draw_node(self, node: TrieNode, cx: float, cy: float, fill_color: Optional[str] = None):
        """绘制单个节点 - 使用更生动的样式"""
        left = cx - self.node_w/2
        top = cy - self.node_h/2
        right = cx + self.node_w/2
        bottom = cy + self.node_h/2
        
        # 根据节点状态设置颜色
        if fill_color:
            fill = fill_color
        elif node.is_end:
            fill = "#E8F5E8"  # 结束节点使用浅绿色背景
        else:
            fill = "#F8FAFF"
        
        # 绘制节点主体 - 使用圆角矩形效果
        rect = self.canvas.create_rectangle(
            left, top, right, bottom, 
            fill=fill, outline="#1f2937", width=1.8
        )
        self.node_items[node] = rect
        
        # 显示字符 - 更醒目的样式
        self.canvas.create_text(
            cx, cy, 
            text=node.char, 
            font=("Arial", 14, "bold"), 
            fill="#0b1220"
        )
        
        # 如果是结束节点，显示更明显的标记
        if node.is_end:
            # 在节点右下角添加绿色结束标记
            end_marker = self.canvas.create_oval(
                right-18, top+8, right-4, top+22, 
                fill="#10B981", outline="#059669", width=1.5
            )
            # 添加白色对勾
            self.canvas.create_text(
                right-11, top+15,
                text="✓",
                font=("Arial", 8, "bold"),
                fill="white"
            )

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
        self.redraw()
        self.update_status("已清空 Trie")

    def start_insert_animated(self):
        """开始插入动画"""
        if self.animating:
            return
        words = self.parse_input_words()
        if not words:
            messagebox.showinfo("提示", "请输入单词（或逗号/空格分隔多个）")
            return
        
        # 更新列表框
        current_words = set(self.word_listbox.get(0, END))
        new_words_added = 0
        for w in words:
            if w not in current_words:
                self.word_listbox.insert(END, w)
                current_words.add(w)
                new_words_added += 1

        if new_words_added == 0 and len(words) > 0:
             self.update_status(f"单词 '{', '.join(words)}' 已存在")
             # 即使已存在，也执行一次搜索动画
             if len(words) == 1:
                 self.input_var.set(words[0])
                 self.start_search_animated()
             return

        self.animating = True
        word_idx = 0
        total_inserted = 0
        
        def process_next_word():
            nonlocal word_idx, total_inserted
            if word_idx >= len(words):
                self.animating = False
                self.update_status(f"插入完成：共处理 {total_inserted} 个单词（逐字动画）")
                return
            word = words[word_idx]
            word_idx += 1
            self.update_status(f"开始插入: '{word}'")
            self._animate_insert_word(word, lambda created_count: on_word_done(created_count))

        def on_word_done(created_count: int):
            nonlocal total_inserted
            total_inserted += 1
            self.window.after(400, process_next_word)  # 增加单词间延迟

        process_next_word()

    def _animate_insert_word(self, word: str, callback):
        """逐字符动画插入单词 - 更生动的动画效果"""
        cur = self.model.root
        pos_nodes: List[TrieNode] = []
        i = 0
        created_nodes: List[TrieNode] = []

        def step():
            nonlocal cur, i
            if i >= len(word):
                if cur is not self.model.root:
                    cur.is_end = True
                if pos_nodes:
                    last = pos_nodes[-1]
                    highlight = {n: "#FFD700" for n in pos_nodes[:-1]}  # 金色
                    highlight[last] = "#10B981"  # 绿色表示结束
                    self.redraw(highlight=highlight)
                    self.update_status(f"✓ 单词 '{word}' 插入完成")
                    # 结束节点闪烁效果
                    self._animate_node_pulse(last, "#10B981", 3, 600)
                    self.window.after(800, lambda: (self.redraw(), callback(len(created_nodes))))
                else:
                    self.redraw()
                    callback(len(created_nodes))
                return
            
            ch = word[i]
            if ch in cur.children:
                cur = cur.children[ch]
                pos_nodes.append(cur)
                highlight = {n: "#FFD700" for n in pos_nodes}
                self.redraw(highlight=highlight)
                self.update_status(f"→ 遍历到已有字母 '{ch}' (步骤 {i+1}/{len(word)})")
                # 当前节点闪烁效果
                self._animate_node_pulse(cur, "#FFD700", 1, 350)
                i += 1
                self.window.after(500, step)  # 增加延迟
            else:
                node = TrieNode(ch)
                node.parent = cur
                cur.children[ch] = node
                cur = node
                pos_nodes.append(cur)
                created_nodes.append(cur)
                
                hl = {n: "#FFD700" for n in pos_nodes[:-1]}
                hl[cur] = "#60A5FA"  # 蓝色表示新创建
                self.redraw(highlight=hl)
                self.update_status(f"✨ 创建新节点 '{ch}' (步骤 {i+1}/{len(word)})")
                # 新节点创建动画
                self._animate_node_creation(cur)
                i += 1
                self.window.after(650, step)  # 增加延迟

        step()

    def _animate_node_pulse(self, node: TrieNode, color: str, pulses: int, duration: int):
        """节点脉动动画效果"""
        if node not in self.node_items:
            return
            
        def pulse(remaining_pulses):
            if remaining_pulses <= 0:
                return
                
            item = self.node_items[node]
            original_fill = self.canvas.itemcget(item, "fill")
            
            # 闪烁到指定颜色
            self.canvas.itemconfig(item, fill=color)
            self.window.after(duration // (pulses * 2), 
                            lambda: self.canvas.itemconfig(item, fill=original_fill))
            
            # 下一次闪烁
            self.window.after(duration // pulses, lambda: pulse(remaining_pulses - 1))
        
        pulse(pulses)

    def _animate_node_creation(self, node: TrieNode):
        """新节点创建动画效果"""
        if node not in self.node_items:
            return
            
        item = self.node_items[node]
        
        # 缩放动画
        def scale_up(scale_factor):
            if scale_factor > 1.0:
                self.canvas.itemconfig(item, width=2.5)  # 临时加粗边框
                return
                
            # 获取原始位置
            coords = self.canvas.coords(item)
            if len(coords) >= 4:
                left, top, right, bottom = coords[:4]
                cx = (left + right) / 2
                cy = (top + bottom) / 2
                
                # 计算缩放后的尺寸
                new_w = self.node_w * scale_factor
                new_h = self.node_h * scale_factor
                new_left = cx - new_w/2
                new_top = cy - new_h/2
                new_right = cx + new_w/2
                new_bottom = cy + new_h/2
                
                self.canvas.coords(item, new_left, new_top, new_right, new_bottom)
                self.window.after(20, lambda: scale_up(scale_factor + 0.1))
        
        scale_up(0.3)

    def start_search_animated(self):
        """开始查找动画 - 更生动的效果"""
        if self.animating:
            return
        word = self.input_var.get().strip()
        if not word:
            messagebox.showinfo("提示", "请输入要查找的单词")
            return
        
        # 只取查找时的第一个词
        word = self.parse_input_words()[0]
        self.input_var.set(word) # 确保输入框只显示被查找的词
            
        found, path = self.model.search(word)
        if not path:
            self.redraw()
            self.update_status(f"❌ 查找：未找到 '{word}' (路径不存在)")
            # 闪烁输入框提示
            try:
                entry_widgets = self.left_panel.winfo_children()[0].winfo_children()
                for widget in entry_widgets:
                    if isinstance(widget, Entry):
                        original_bg = widget.cget("bg")
                        widget.config(bg="#FEE2E2")
                        self.window.after(800, lambda: widget.config(bg=original_bg))
                        break
            except:
                pass
            return
        
        self.animating = True
        i = 0
        
        def step():
            nonlocal i
            if i >= len(path):
                self.animating = False
                if found:
                    self.update_status(f"✅ 查找完成：找到 '{word}'")
                    node = path[-1]
                    highlight = {n: "#FFD700" for n in path[:-1]}
                    highlight[node] = "#10B981"  # 绿色
                    self.redraw(highlight=highlight)
                    # 成功闪烁效果
                    self._animate_node_pulse(node, "#10B981", 3, 800)
                    self.window.after(1000, lambda: self.redraw())
                else:
                    self.update_status(f"⚠️ 查找完成：未找到 '{word}'（前缀存在但不是完整单词）")
                    self.redraw(highlight={n: "#FFD700" for n in path})
                    # 警告闪烁效果
                    if path:
                        self._animate_node_pulse(path[-1], "#F59E0B", 3, 800)
                    self.window.after(1000, lambda: self.redraw())
                return
            
            node = path[i]
            self.redraw(highlight={n: "#FFD700" for n in path[:i+1]})
            self.update_status(f"🔍 查找: 比较到 '{node.char}' (步骤 {i+1}/{len(word)})")
            # 当前节点闪烁
            self._animate_node_pulse(node, "#FFD700", 1, 400)
            i += 1
            self.window.after(500, step)  # 增加延迟
        
        step()

    def process_dsl(self, event=None):
        """处理 DSL 命令"""
        if getattr(self, "animating", False):
            messagebox.showinfo("提示", "当前正在执行动画，无法执行DSL，请稍后再试。")
            return

        raw = (self.input_var.get() or "").strip()
        if not raw:
            return

        try:
            # 假设 process_command 存在
            process_command(self, raw)
        except Exception as e:
            # 如果是 NameError (process_command 未定义)，则退回到默认行为
            if isinstance(e, NameError):
                self.update_status("DSL 未加载。请使用按钮操作。")
                # 默认回车=插入
                self.start_insert_animated()
            else:
                messagebox.showerror("DSL 执行错误", f"执行 DSL 时出错: {e}")
                self.update_status("DSL 错误")

if __name__ == '__main__':
    root = Tk()
    app = TrieVisualizer(root)
    root.mainloop()
    
