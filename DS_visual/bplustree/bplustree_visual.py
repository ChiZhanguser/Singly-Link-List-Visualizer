# bplustree_visual.py
from tkinter import *
from tkinter import messagebox
from typing import Dict, Tuple, List, Optional, Any
from bplustree.bplustree_model import BPlusTree, BPlusNode
import math

class BPlusVisualizer:
    """
    改进版：自动放大/拉伸布局 + 左侧控制折叠（占满画布空间）
    """
    def __init__(self, root):
        self.window = root
        self.window.title("B+ 树 可视化 - 插入与分裂演示 (自适应布局)")
        self.window.geometry("1280x760")
        self.window.config(bg="#071129")

        # UI 布局参数
        self.left_width = 360
        self.left_collapsed = False

        main = Frame(self.window, bg="#071129")
        main.pack(fill=BOTH, expand=True)

        # 左侧控制面板
        self.left_panel = Frame(main, width=self.left_width, bg="#071129")
        self.left_panel.pack(side=LEFT, fill=Y)
        self.left_panel.pack_propagate(False)

        # status var
        self.status_var = StringVar(value="就绪：请输入键并插入（支持整数或字符串）")

        self._build_left_panel()

        # 右侧画布容器
        self.right = Frame(main, bg="#071129")
        self.right.pack(side=LEFT, fill=BOTH, expand=True, padx=(12,16), pady=12)

        # canvas
        self.canvas = Canvas(self.right, bg="#071129", bd=0, highlightthickness=0)
        self.canvas.pack(fill=BOTH, expand=True, side=LEFT)

        # scrollbars
        self.h_scroll = Scrollbar(self.right, orient=HORIZONTAL, command=self.canvas.xview)
        self.v_scroll = Scrollbar(self.right, orient=VERTICAL, command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=self.h_scroll.set, yscrollcommand=self.v_scroll.set)
        self.h_scroll.pack(fill=X, side=BOTTOM)
        self.v_scroll.pack(fill=Y, side=RIGHT)

        # panning
        self.canvas.bind("<ButtonPress-1>", lambda e: self.canvas.scan_mark(e.x, e.y))
        self.canvas.bind("<B1-Motion>", lambda e: self.canvas.scan_dragto(e.x, e.y, gain=1))

        # 模型与视觉参数
        self.tree = BPlusTree(order=4)

        # base visual params (调整后会按画布大小自适应)
        self.base_node_w = 160
        self.base_node_h = 56
        self.node_w = self.base_node_w
        self.node_h = self.base_node_h
        self.base_level_gap = 140
        self.level_gap = self.base_level_gap
        self.margin_x = 36
        self.top_margin = 56

        # spacing & zoom
        self.min_spacing = self.node_w + 40
        self.zoom_scale = 1.0
        self.fit_mode = True

        # mapping
        self.node_items: Dict[BPlusNode, int] = {}

        # animation state
        self.animating = False

        # initial draw
        self.redraw()

    # ---------------- left panel ----------------
    def _build_left_panel(self):
        pad = 12
        Label(self.left_panel, text="B+ 树 可视化", fg="#A3E1FF",
              font=("Segoe UI", 16, "bold"), bg="#071129").pack(pady=(18,6))
        Label(self.left_panel, text="插入与分裂演示（order = 4）", bg="#071129", fg="#9fb8d6").pack()

        frm = Frame(self.left_panel, bg="#071129")
        frm.pack(padx=pad, pady=(12,8), fill=X)
        Label(frm, text="输入键（逗号/空格分隔）：", bg="#071129", fg="#9fb8d6").pack(anchor="w")
        self.input_var = StringVar()
        entry = Entry(frm, textvariable=self.input_var, font=("Arial",12), bg="#0f2740", fg="#E6F7FF", insertbackground="#E6F7FF")
        entry.pack(fill=X, pady=(8,0))
        self.input_var.set("10, 20, 5, 6, 12, 30, 7, 17")

        btn_frame = Frame(self.left_panel, bg="#071129")
        btn_frame.pack(padx=pad, pady=(12,8), fill=X)
        Button(btn_frame, text="插入（动画）", bg="#0EA5A3", fg="white", bd=0, command=self.start_insert_animated).pack(fill=X, pady=(0,8))
        Button(btn_frame, text="清空", bg="#EF4444", fg="white", bd=0, command=self.clear_tree).pack(fill=X)

        Frame(self.left_panel, height=1, bg="#0b2236").pack(fill=X, padx=pad, pady=(12,10))
        fit_frame = Frame(self.left_panel, bg="#071129")
        fit_frame.pack(padx=pad, fill=X)
        Button(fit_frame, text="Fit", command=self.toggle_fit_mode, width=6, bg="#1E293B", fg="#A3E1FF", bd=0).pack(side=LEFT)
        Button(fit_frame, text="Zoom +", command=self.zoom_in, width=8, bg="#1E293B", fg="#A3E1FF", bd=0).pack(side=LEFT, padx=(8,0))
        Button(fit_frame, text="Zoom -", command=self.zoom_out, width=8, bg="#1E293B", fg="#A3E1FF", bd=0).pack(side=LEFT, padx=(8,0))
        Button(fit_frame, text="Collapse controls", command=self.toggle_left_panel, width=14, bg="#0b2b3b", fg="#A3E1FF", bd=0).pack(side=LEFT, padx=(8,0))

        Frame(self.left_panel, height=1, bg="#0b2236").pack(fill=X, padx=pad, pady=(12,12))
        Label(self.left_panel, text="当前叶子序列（从左到右）：", bg="#071129", fg="#9fb8d6").pack(anchor="w", padx=pad)
        self.leaf_listbox = Listbox(self.left_panel, height=6, bg="#0f2740", fg="#E6F7FF", bd=0, highlightthickness=0)
        self.leaf_listbox.pack(fill=X, padx=pad, pady=(8,0))

        Frame(self.left_panel, height=1, bg="#0b2236").pack(fill=X, padx=pad, pady=(12,8))
        Label(self.left_panel, textvariable=self.status_var, bg="#071129", wraplength=self.left_width-24, justify=LEFT, fg="#9fe9c9").pack(padx=pad, pady=(6,10))
        help_text = ("提示：\n• Collapse controls 隐藏左侧面板以扩大画布。\n• Fit 会尝试横向压缩/拉伸节点以填满可见宽度。\n• Zoom 改变显示尺度，必要时拖动画布查看完整树。")
        Label(self.left_panel, text=help_text, bg="#071129", fg="#7ea9bf", justify=LEFT, wraplength=self.left_width-24).pack(padx=pad, pady=(6,10))

    # ---------------- collapse left panel ----------------
    def toggle_left_panel(self):
        if self.left_collapsed:
            # expand
            self.left_panel.pack(side=LEFT, fill=Y)
            self.left_collapsed = False
            self.update_status("已展开控制面板")
        else:
            # collapse
            self.left_panel.forget()
            self.left_collapsed = True
            self.update_status("已折叠控制面板（使用全部画布空间）")
        # redraw after layout change
        self.window.after(80, self.redraw)

    # ---------------- status / parse ----------------
    def update_status(self, txt: str):
        self.status_var.set(txt)

    def parse_input_keys(self) -> List[Any]:
        text = self.input_var.get().strip()
        if not text:
            return []
        parts = [p.strip() for p in text.replace(",", " ").split() if p.strip()]
        out: List[Any] = []
        for p in parts:
            try:
                out.append(int(p))
            except:
                out.append(p)
        return out

    # ---------------- zoom / fit ----------------
    def toggle_fit_mode(self):
        self.fit_mode = not self.fit_mode
        self.update_status(f"Fit 模式: {'开' if self.fit_mode else '关'}")
        self.redraw()

    def zoom_in(self):
        self.zoom_scale *= 1.12
        self._apply_zoom()
        self.update_status(f"缩放: {self.zoom_scale:.2f}")
        self.redraw()

    def zoom_out(self):
        self.zoom_scale /= 1.12
        self._apply_zoom()
        self.update_status(f"缩放: {self.zoom_scale:.2f}")
        self.redraw()

    def _apply_zoom(self):
        self.node_w = max(60, int(self.base_node_w * self.zoom_scale))
        self.node_h = max(28, int(self.base_node_h * self.zoom_scale))
        self.level_gap = max(60, int(self.base_level_gap * self.zoom_scale))
        self.min_spacing = self.node_w + 40

    # ---------------- compute positions: 放大利用画布 ----------------
    def compute_positions(self) -> Dict[BPlusNode, Tuple[float,float]]:
        pos: Dict[BPlusNode, Tuple[float,float]] = {}
        levels = self.tree.nodes_by_level()
        if not levels:
            return pos
        max_depth = max(levels.keys())
        level_counts = {d: len(nodes) for d, nodes in levels.items()}
        max_nodes = max(level_counts.values())

        # canvas available size
        self.canvas.update_idletasks()
        avail_w = max(self.canvas.winfo_width(), 600)
        avail_h = max(self.canvas.winfo_height(), 400)

        inner_w = avail_w - 2*self.margin_x
        inner_h = avail_h - 2*self.top_margin

        # dynamic vertical spacing: 将层级均匀分配在 inner_h 中（至少保留 base gap）
        if max_depth > 0:
            vgap = max(inner_h / (max_depth+1), 60)
        else:
            vgap = min(inner_h, self.level_gap)
        # limit vgap to reasonable bounds
        vgap = max(60, min(vgap, self.level_gap * 1.6))
        # update level_gap used for positioning
        self.level_gap = int(vgap)

        # dynamic node width when nodes are few: 尝试扩大节点宽度以填满空间
        # compute average nodes per level; if small, allow node_w to grow up to a cap
        avg_nodes = sum(level_counts.values()) / len(level_counts)
        if avg_nodes <= 3:
            # expand node width as fraction of available width
            desired_w = int(inner_w / max(3, int(avg_nodes)+1) * 0.6)
            self.node_w = max(60, min(desired_w, int(self.base_node_w * 2.2)))
        else:
            self.node_w = self.base_node_w

        # recompute min spacing
        spacing_base = max(self.node_w + 24, 100)

        # compute horizontal spacing per level:
        for depth in range(0, max_depth+1):
            nodes = levels.get(depth, [])
            n = len(nodes)
            if n == 0:
                continue
            # choose spacing:
            if self.fit_mode and n > 1:
                total_span = inner_w
                spacing = min(spacing_base, total_span / (n+1))
            else:
                spacing = spacing_base
            # ensure spacing not too small
            spacing = max(28, spacing)
            # total span occupied
            total_span = spacing * (n - 1) if n>1 else 0
            start_x = self.margin_x + (inner_w - total_span) / 2.0
            for i, node in enumerate(nodes):
                if n == 1:
                    x = self.margin_x + inner_w / 2.0
                else:
                    x = start_x + i * spacing
                # vertical pos: center levels across inner_h
                y = self.top_margin + depth * vgap
                pos[node] = (x, y)
        return pos

    # ---------------- drawing ----------------
    def _draw_gradient_background(self):
        w = max(self.canvas.winfo_width(), 1200)
        h = max(self.canvas.winfo_height(), 700)
        stops = ["#071129", "#0b1f3a", "#0f2946", "#132b4f", "#0b1f3a"]
        steps = 100
        def interp(c1, c2, t):
            r1,g1,b1 = int(c1[1:3],16), int(c1[3:5],16), int(c1[5:7],16)
            r2,g2,b2 = int(c2[1:3],16), int(c2[3:5],16), int(c2[5:7],16)
            r = int(r1 + (r2-r1)*t); g = int(g1 + (g2-g1)*t); b = int(b1 + (b2-b1)*t)
            return f"#{r:02x}{g:02x}{b:02x}"
        for i in range(steps):
            t = i / max(1, steps-1)
            idx = int(t * (len(stops)-1))
            t2 = (t*(len(stops)-1)) - idx
            c = interp(stops[idx], stops[min(idx+1,len(stops)-1)], t2)
            y0 = int(i * (h/steps))
            y1 = int((i+1) * (h/steps))
            self.canvas.create_rectangle(0, y0, w, y1, outline="", fill=c)
        # faint grid
        grid = "#0e2a3a"
        for gx in range(0, w, 80):
            self.canvas.create_line(gx, 0, gx, h, fill=grid)
        for gy in range(0, h, 80):
            self.canvas.create_line(0, gy, w, gy, fill=grid)

    def _rounded_rect(self, left, top, right, bottom, r=10, **kwargs):
        ids = []
        ids.append(self.canvas.create_rectangle(left+r, top, right-r, bottom, **kwargs))
        ids.append(self.canvas.create_rectangle(left, top+r, right, bottom-r, **kwargs))
        ids.append(self.canvas.create_oval(left, top, left+2*r, top+2*r, **kwargs))
        ids.append(self.canvas.create_oval(right-2*r, top, right, top+2*r, **kwargs))
        ids.append(self.canvas.create_oval(left, bottom-2*r, left+2*r, bottom, **kwargs))
        ids.append(self.canvas.create_oval(right-2*r, bottom-2*r, right, bottom, **kwargs))
        return ids

    def redraw(self, highlight: Optional[Dict[BPlusNode, str]] = None):
        self.canvas.delete("all")
        self.node_items.clear()

        # background
        self._draw_gradient_background()

        # header
        self.canvas.create_text(32, 30, anchor="w", text=f"B+ 树（order={self.tree.order}）", font=("Segoe UI",14,"bold"), fill="#A7F3D0")
        self.canvas.create_text(32, 50, anchor="w", text="插入与节点分裂（自适应布局）", font=("Segoe UI",10), fill="#9fb8d6")

        pos = self.compute_positions()
        if not pos:
            self.canvas.create_text(640, 300, text="空树（请插入键）", font=("Arial",20), fill="#94a3b8")
            self.canvas.config(scrollregion=(0,0,1400,900))
            self._refresh_leaf_list()
            return

        # draw edges (glow)
        for node, (cx, cy) in pos.items():
            if not node.is_leaf:
                for child in node.children:
                    if child in pos:
                        px, py = pos[child]
                        self.canvas.create_line(cx, cy + self.node_h/2, px, py - self.node_h/2, width=4, fill="#072c37", smooth=True)
                        self.canvas.create_line(cx, cy + self.node_h/2, px, py - self.node_h/2, width=2, fill="#5eead4", smooth=True)

        # draw nodes (rounded cards)
        for node, (cx, cy) in pos.items():
            color = None
            if highlight and node in highlight:
                color = highlight[node]
            self._draw_node(node, cx, cy, fill_color=color)

        # draw leaf pointers
        for leaf in self.tree.leaves():
            pos_map = pos
            if leaf in pos_map and leaf.next in pos_map:
                lx, ly = pos_map[leaf]
                nx, ny = pos_map[leaf.next]
                left = lx + self.node_w/2
                right = nx - self.node_w/2
                self.canvas.create_line(left, ly, right, ny, arrow=LAST, dash=(6,4), fill="#7dd3fc")

        # update scrollregion and center if fit
        bbox = self.canvas.bbox("all")
        if bbox:
            l,t,r,b = bbox
            pad = 120
            self.canvas.config(scrollregion=(l-pad, t-pad, r+pad, b+pad))
            if self.fit_mode:
                canvas_w = max(self.canvas.winfo_width(), 1)
                content_w = (r - l) + pad*2
                if content_w > 0:
                    left_view = max(0, (l + (r - l)/2.0) - canvas_w/2.0 + pad)
                    full_width = (r + pad) - (l - pad)
                    if full_width > 0:
                        frac = left_view / full_width
                        frac = max(0.0, min(1.0, frac))
                        try:
                            self.canvas.xview_moveto(frac)
                        except Exception:
                            pass

        self._refresh_leaf_list()

    def _draw_node(self, node: BPlusNode, cx: float, cy: float, fill_color: Optional[str] = None):
        left = cx - self.node_w/2
        top = cy - self.node_h/2
        right = cx + self.node_w/2
        bottom = cy + self.node_h/2

        base_fill = fill_color or ("#052635" if node.is_leaf else "#073146")
        # outer glow rect
        glow_l, glow_t, glow_r, glow_b = left-6, top-6, right+6, bottom+6
        self._rounded_rect(glow_l, glow_t, glow_r, glow_b, r=12, fill="#06343b", outline="")
        # main card
        self._rounded_rect(left, top, right, bottom, r=10, fill=base_fill, outline="#0fe6c4")
        # inner border
        self.canvas.create_rectangle(left+6, top+6, right-6, bottom-6, outline="#073b40", width=1)
        # text
        text = " | ".join(str(k) for k in node.keys)
        marker = " L" if node.is_leaf else ""
        self.canvas.create_text(cx, cy, text=text + marker, font=("Segoe UI",11,"bold"), fill="#E6F7FF")

    def _refresh_leaf_list(self):
        self.leaf_listbox.delete(0, END)
        leaves = self.tree.leaves()
        for leaf in leaves:
            self.leaf_listbox.insert(END, ", ".join(str(k) for k in leaf.keys))

    # ---------------- user actions ----------------
    def clear_tree(self):
        if self.animating:
            return
        self.tree.clear()
        self.redraw()
        self.update_status("已清空 B+ 树")

    def start_insert_animated(self):
        if self.animating:
            return
        keys = self.parse_input_keys()
        if not keys:
            messagebox.showinfo("提示", "请输入要插入的键（逗号/空格分隔）")
            return
        self.animating = True
        key_idx = 0
        def process_next():
            nonlocal key_idx
            if key_idx >= len(keys):
                self.animating = False
                self.update_status("批量插入完成")
                return
            k = keys[key_idx]
            key_idx += 1
            self.update_status(f"开始插入：{k}")
            events = self.tree.insert_with_steps(k)
            self._animate_events(events, lambda: self.window.after(300, process_next))
        process_next()

    def _animate_events(self, events: List[Dict], callback):
        i = 0
        def step():
            nonlocal i
            if i >= len(events):
                self.redraw()
                callback()
                return
            ev = events[i]
            evtype = ev.get('type')
            if evtype == 'visit':
                node = ev['node']
                self.redraw(highlight={node: "#FCD34D"})
                self.update_status(f"访问节点 {node.keys}")
                i += 1
                self.window.after(380, step)
            elif evtype == 'insert':
                node = ev['node']
                self.redraw(highlight={node: "#10B981"})
                self.update_status(f"在叶节点插入：{node.keys}")
                i += 1
                self.window.after(520, step)
            elif evtype == 'split':
                node = ev['node']
                new_node = ev.get('new_node')
                promoted = ev.get('promoted')
                is_leaf = ev.get('is_leaf', False)
                hl = {node: "#F87171"}
                if new_node is not None:
                    hl[new_node] = "#86efac"
                self.redraw(highlight=hl)
                self.update_status(f"节点分裂（is_leaf={is_leaf}），升键：{promoted}")
                i += 1
                self.window.after(700, step)
            else:
                i += 1
                self.window.after(200, step)
        step()

if __name__ == '__main__':
    root = Tk()
    app = BPlusVisualizer(root)
    root.mainloop()
