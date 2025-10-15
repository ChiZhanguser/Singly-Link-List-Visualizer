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
        self.window.config(bg="#F3F6FB")
        self.window.geometry("1200x720")
        self.left_width = 320
        main = Frame(self.window, bg="#F3F6FB")
        main.pack(fill=BOTH, expand=True)
        self.status_text_var = StringVar(value="就绪：可插入 / 查找 / 清空。")
        self.left_panel = Frame(main, width=self.left_width, bg="#F8FAFF")
        self.left_panel.pack(side=LEFT, fill=Y)
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
        # model
        self.model = TrieModel()
        # drawing bookkeeping
        self.node_items: Dict[TrieNode, int] = {}
        self.edge_items: List[int] = []
        # layout params (visual)
        self.node_w = 72
        self.node_h = 44
        self.level_gap = 120
        self.margin_x = 40
        self.top_margin = 36
        # animation state
        self.animating = False
        self.redraw()

    def _build_left_panel(self):
        pad = 12
        title = Label(self.left_panel, text="Trie 可视化", font=("Helvetica", 14, "bold"), bg="#F8FAFF")
        title.pack(pady=(18,6))
        subtitle = Label(self.left_panel, text="逐字动画 · 创建/查找/清空", bg="#F8FAFF", fg="#555")
        subtitle.pack(pady=(0,10))
        # 输入框
        frm = Frame(self.left_panel, bg="#F8FAFF")
        frm.pack(padx=pad, pady=(6,8), fill=X)
        Label(frm, text="输入单词 (逗号/空格分隔):", bg="#F8FAFF").pack(anchor="w")
        self.input_var = StringVar()
        entry = Entry(frm, textvariable=self.input_var, font=("Arial", 12))
        entry.pack(fill=X, pady=(6,0))
        entry.insert(0, "apple, app, bat")
        # 回车默认触发 DSL（主键盘 Enter 与小键盘 Enter）
        entry.bind("<Return>", lambda e: self.process_dsl())
        entry.bind("<KP_Enter>", lambda e: self.process_dsl())
        # 按钮
        btn_frame = Frame(self.left_panel, bg="#F8FAFF")
        btn_frame.pack(padx=pad, pady=(12,10), fill=X)

        style_btn = {"bd":0, "relief":FLAT, "padx":8, "pady":6, "font":("Arial",11,"bold")}
        b_insert = Button(btn_frame, text="插入（动画）", bg="#2E8B57", fg="white",
                          command=self.start_insert_animated, **style_btn)
        b_search = Button(btn_frame, text="查找（动画）", bg="#FF9F1C", fg="white",
                          command=self.start_search_animated, **style_btn)
        b_clear = Button(btn_frame, text="清空", bg="#E04E3F", fg="white",
                         command=self.clear_trie, **style_btn)
        b_insert.pack(fill=X, pady=(0,6))
        b_search.pack(fill=X, pady=(0,6))
        b_clear.pack(fill=X)
        # 分割线
        Frame(self.left_panel, height=1, bg="#E6E9F2").pack(fill=X, padx=pad, pady=(14,12))
        # 当前词表（右侧自动刷新）
        Label(self.left_panel, text="当前已插入单词：", bg="#F8FAFF").pack(anchor="w", padx=pad)
        self.word_listbox = Listbox(self.left_panel, height=8)
        self.word_listbox.pack(fill=X, padx=pad, pady=(6,0))
        # 状态栏（使用在 __init__ 先定义好的 status_text_var）
        Frame(self.left_panel, height=1, bg="#E6E9F2").pack(fill=X, padx=pad, pady=(12,8))
        status_lbl = Label(self.left_panel, textvariable=self.status_text_var, wraplength=self.left_width-24,
                           bg="#F8FAFF", justify=LEFT, fg="#2D6A4F")
        status_lbl.pack(padx=pad, pady=(4,12), anchor="w")
        # 帮助与说明
        help_text = ("提示：\n"
                     "• 请使用插入按钮查看逐字创建/遍历动画。\n"
                     "• 当节点很多时，使用滚动条或按住鼠标左键拖动画布查看。\n"
                     "• 查找会高亮遍历路径（黄色），命中末尾为绿色。")
        Label(self.left_panel, text=help_text, bg="#F8FAFF", fg="#555", justify=LEFT, wraplength=self.left_width-24).pack(padx=pad, pady=(6,10))

    def update_status(self, txt: str):
        self.status_text_var.set(txt)

    def compute_positions(self) -> Dict[TrieNode, Tuple[float,float]]:
        pos: Dict[TrieNode, Tuple[float,float]] = {}
        levels = self.model.nodes_by_level()
        if not levels:
            return pos
        max_depth = max(levels.keys())

        # get canvas width available (use actual widget width if larger)
        self.canvas.update_idletasks()
        avail_width = max(self.canvas.winfo_width(), 800)
        # reserve some extra width per level depending on max node count across levels
        for depth in range(1, max_depth+1):
            nodes = levels.get(depth, [])
            n = len(nodes)
            if n == 0:
                continue
            width = max(avail_width - 2*self.margin_x, 300)
            for i, node in enumerate(nodes):
                if n == 1:
                    x = self.margin_x + width / 2
                else:
                    x = self.margin_x + i * (width / (n-1))
                y = self.top_margin + (depth-1) * self.level_gap
                pos[node] = (x, y)
        return pos

    # ---------------- drawing ----------------
    def redraw(self, highlight: Optional[Dict[TrieNode, str]] = None):
        self.canvas.delete("all")
        self.node_items.clear()
        self.edge_items.clear()

        # instruction at top-left of canvas
        self.canvas.create_text(12, 10, anchor="nw",
                                text="Trie：插入 / 查找 / 清空。动画显示逐字符访问与创建。",
                                font=("Arial",11), fill="#334155")

        pos = self.compute_positions()
        if not pos:
            # empty trie 显示提示
            self.canvas.create_text(600, 200, text="空的 Trie（请插入单词）", font=("Arial",18), fill="#94a3b8")
            # update scrollregion to reasonably small area
            self.canvas.config(scrollregion=(0,0,1200,600))
            return

        # draw edges first
        for node, (cx, cy) in pos.items():
            parent = node.parent
            if parent and parent is not self.model.root and parent in pos:
                px, py = pos[parent]
                line = self.canvas.create_line(px, py + self.node_h/2, cx, cy - self.node_h/2, width=2, arrow=LAST, fill="#475569")
                self.edge_items.append(line)

        # root position: center at top relative to positions
        first_level_nodes = self.model.nodes_by_level().get(1, [])
        if first_level_nodes:
            xs = [pos[n][0] for n in first_level_nodes if n in pos]
            root_x = sum(xs) / len(xs) if xs else (self.canvas.winfo_width()//2)
        else:
            root_x = self.canvas.winfo_width()//2
        root_y = 16

        for node in first_level_nodes:
            if node in pos:
                cx, cy = pos[node]
                l = self.canvas.create_line(root_x, root_y + 20, cx, cy - self.node_h/2, width=2, arrow=LAST, fill="#475569")
                self.edge_items.append(l)

        # draw nodes
        for node, (cx, cy) in pos.items():
            color = None
            if highlight and node in highlight:
                color = highlight[node]
            self._draw_node(node, cx, cy, fill_color=color)

        # draw small root marker
        self.canvas.create_oval(root_x-16, root_y-10, root_x+16, root_y+10, fill="#EAF2FF", outline="#0f172a")
        self.canvas.create_text(root_x, root_y, text="root", font=("Arial",10, "bold"))

        # update scrollregion to bounding box of all items + margin
        bbox = self.canvas.bbox("all")
        if bbox:
            left, top, right, bottom = bbox
            pad = 60
            self.canvas.config(scrollregion=(left-pad, top-pad, right+pad, bottom+pad))

    def _draw_node(self, node: TrieNode, cx: float, cy: float, fill_color: Optional[str] = None):
        left = cx - self.node_w/2
        top = cy - self.node_h/2
        right = cx + self.node_w/2
        bottom = cy + self.node_h/2
        fill = fill_color if fill_color else "#F8FAFF"
        # 去掉不合法的 radius 参数
        rect = self.canvas.create_rectangle(left, top, right, bottom, fill=fill, outline="#1f2937", width=1.8)
        self.node_items[node] = rect
        # display char and end marker
        self.canvas.create_text(cx - 12, cy, text=node.char, font=("Arial",12,"bold"), fill="#0b1220")
        if node.is_end:
            self.canvas.create_oval(right-16, top+8, right-6, top+18, fill="#ef4444", outline="")

    def parse_input_words(self) -> List[str]:
        text = self.input_var.get().strip()
        if not text:
            return []
        parts = [p.strip() for p in text.replace(",", " ").split() if p.strip()]
        return parts

    def clear_trie(self):
        if self.animating:
            return
        self.model.clear()
        self.word_listbox.delete(0, END)
        self.redraw()
        self.update_status("已清空 Trie")

    def start_insert_animated(self):
        if self.animating:
            return
        words = self.parse_input_words()
        if not words:
            messagebox.showinfo("提示", "请输入单词（或逗号/空格分隔多个）")
            return
        for w in words:
            self.word_listbox.insert(END, w)

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
            self.window.after(300, process_next_word)

        process_next_word()

    def _animate_insert_word(self, word: str, callback):
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
                    highlight = {n: "gold" for n in pos_nodes[:-1]}
                    highlight[last] = "#9AE6B4"
                    self.redraw(highlight=highlight)
                    self.update_status(f"单词 '{word}' 插入完成")
                    self.window.after(480, lambda: (self.redraw(), callback(len(created_nodes))))
                else:
                    self.redraw()
                    callback(len(created_nodes))
                return
            ch = word[i]
            if ch in cur.children:
                cur = cur.children[ch]
                pos_nodes.append(cur)
                self.redraw(highlight={n: "gold" for n in pos_nodes})
                self.update_status(f"遍历到已有字母 '{ch}' (step {i+1}/{len(word)})")
                i += 1
                self.window.after(380, step)
            else:
                node = TrieNode(ch)
                node.parent = cur
                cur.children[ch] = node
                cur = node
                pos_nodes.append(cur)
                created_nodes.append(cur)
                # 合并字典的写法兼容性考虑，直接生成新 dict
                hl = {n: "gold" for n in pos_nodes[:-1]}
                hl[cur] = "#BEE3DB"
                self.redraw(highlight=hl)
                self.update_status(f"创建新节点 '{ch}' (step {i+1}/{len(word)})")
                i += 1
                self.window.after(520, step)

        step()

    def start_search_animated(self):
        if self.animating:
            return
        word = self.input_var.get().strip()
        if not word:
            messagebox.showinfo("提示", "请输入要查找的单词")
            return
        found, path = self.model.search(word)
        if not path:
            self.redraw()
            self.update_status(f"查找：未找到 '{word}'")
            return
        self.animating = True
        i = 0
        def step():
            nonlocal i
            if i >= len(path):
                self.animating = False
                if found:
                    self.update_status(f"查找完成：找到 '{word}'")
                    node = path[-1]
                    self.redraw(highlight={n: "gold" for n in path[:-1]} | {node: "#9AE6B4"})
                    self.window.after(700, lambda: self.redraw())
                else:
                    self.update_status(f"查找完成：未找到 '{word}'（前缀存在但不是完整单词）")
                    self.redraw(highlight={n: "gold" for n in path})
                    self.window.after(700, lambda: self.redraw())
                return
            node = path[i]
            self.redraw(highlight={n: "gold" for n in path[:i+1]})
            self.update_status(f"查找: 比较到 '{node.char}' (step {i+1}/{len(path)})")
            i += 1
            self.window.after(380, step)
        step()

    # --------------------
    # DSL entry: 回车默认触发 DSL（在 _build_left_panel 已绑定）
    # 将命令传给 DSL_utils.process_command，DSL 会根据 visualizer 类型分发执行
    # --------------------
    def process_dsl(self, event=None):
        """
        当用户在 Entry 中按回车时调用；也可以从代码中直接调用。
        event 参数会被忽略（用于绑定兼容）。
        """
        # 若当前有动画在执行，拒绝执行新的 DSL 命令（避免状态冲突）
        if getattr(self, "animating", False):
            messagebox.showinfo("提示", "当前正在执行动画，无法执行 DSL，请稍后再试。")
            return

        raw = (self.input_var.get() or "").strip()
        if not raw:
            return

        try:
            # 将 visualizer（self）与命令传到 DSL 分发器
            process_command(self, raw)
            # （可选）执行成功后清空输入框：如果不希望清空可以注释下一行
            # self.input_var.set("")
        except Exception as e:
            messagebox.showerror("DSL 执行错误", f"执行 DSL 时出错: {e}")
            self.update_status("DSL 错误")

if __name__ == '__main__':
    root = Tk()
    app = TrieVisualizer(root)
    root.mainloop()
