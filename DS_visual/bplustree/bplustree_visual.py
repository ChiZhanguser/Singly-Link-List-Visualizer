from tkinter import *
from tkinter import messagebox
from typing import Dict, Tuple, List, Optional, Any
from bplustree.bplustree_model import BPlusTree, BPlusNode
import math

class BPlusVisualizer:
    def __init__(self, root):
        self.window = root
        self.window.title("B+树可视化")
        self.window.geometry("1280x760")
        self.window.config(bg="#071129")

        # UI布局参数
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
        # explanation var - 用于显示当前操作的详细解释
        self.explanation_var = StringVar(value="")

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

        # base visual params
        self.base_node_w = 180
        self.base_node_h = 70
        self.node_w = self.base_node_w
        self.node_h = self.base_node_h
        self.base_level_gap = 160
        self.level_gap = self.base_level_gap
        self.margin_x = 50
        self.top_margin = 100

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

    def _build_left_panel(self):
        pad = 12
        Label(self.left_panel, text="B+ 树可视化", fg="#A3E1FF",
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

        Frame(self.left_panel, height=1, bg="#0b2236").pack(fill=X, padx=pad, pady=(12,12))
        
        # 当前操作说明框 - 高亮显示
        explain_frame = Frame(self.left_panel, bg="#0a2540", bd=2, relief=SOLID)
        explain_frame.pack(fill=X, padx=pad, pady=(0,12))
        Label(explain_frame, text="🔍 当前操作：", bg="#0a2540", fg="#FCD34D", 
              font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=8, pady=(8,4))
        Label(explain_frame, textvariable=self.explanation_var, bg="#0a2540", 
              wraplength=self.left_width-32, justify=LEFT, fg="#E6F7FF",
              font=("Segoe UI", 9)).pack(padx=8, pady=(0,8), anchor="w")

        Frame(self.left_panel, height=1, bg="#0b2236").pack(fill=X, padx=pad, pady=(0,12))
        
        Label(self.left_panel, text="当前叶节点序列（从左到右）：", bg="#071129", fg="#9fb8d6").pack(anchor="w", padx=pad)
        self.leaf_listbox = Listbox(self.left_panel, height=6, bg="#0f2740", fg="#E6F7FF", bd=0, highlightthickness=0)
        self.leaf_listbox.pack(fill=X, padx=pad, pady=(8,0))

        Frame(self.left_panel, height=1, bg="#0b2236").pack(fill=X, padx=pad, pady=(12,8))
        Label(self.left_panel, textvariable=self.status_var, bg="#071129", wraplength=self.left_width-24, justify=LEFT, fg="#9fe9c9").pack(padx=pad, pady=(6,10))

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

    def update_status(self, txt: str):
        self.status_var.set(txt)
        
    def update_explanation(self, txt: str):
        """更新操作解释"""
        self.explanation_var.set(txt)

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

    def compute_positions(self) -> Dict[BPlusNode, Tuple[float,float]]:
        pos: Dict[BPlusNode, Tuple[float,float]] = {}
        levels = self.tree.nodes_by_level()
        if not levels:
            return pos
        max_depth = max(levels.keys())
        level_counts = {d: len(nodes) for d, nodes in levels.items()}

        self.canvas.update_idletasks()
        avail_w = max(self.canvas.winfo_width(), 600)
        avail_h = max(self.canvas.winfo_height(), 400)

        inner_w = avail_w - 2*self.margin_x
        inner_h = avail_h - 2*self.top_margin

        if max_depth > 0:
            vgap = max(inner_h / (max_depth+1), 60)
        else:
            vgap = min(inner_h, self.level_gap)
        vgap = max(60, min(vgap, self.level_gap * 1.6))
        self.level_gap = int(vgap)

        avg_nodes = sum(level_counts.values()) / len(level_counts)
        if avg_nodes <= 3:
            desired_w = int(inner_w / max(3, int(avg_nodes)+1) * 0.6)
            self.node_w = max(60, min(desired_w, int(self.base_node_w * 2.2)))
        else:
            self.node_w = self.base_node_w

        spacing_base = max(self.node_w + 24, 100)

        for depth in range(0, max_depth+1):
            nodes = levels.get(depth, [])
            n = len(nodes)
            if n == 0:
                continue
            if self.fit_mode and n > 1:
                total_span = inner_w
                spacing = min(spacing_base, total_span / (n+1))
            else:
                spacing = spacing_base
            spacing = max(28, spacing)
            total_span = spacing * (n - 1) if n>1 else 0
            start_x = self.margin_x + (inner_w - total_span) / 2.0
            for i, node in enumerate(nodes):
                if n == 1:
                    x = self.margin_x + inner_w / 2.0
                else:
                    x = start_x + i * spacing
                y = self.top_margin + depth * vgap
                pos[node] = (x, y)
        return pos

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

    def redraw(self, highlight: Optional[Dict[BPlusNode, str]] = None, 
               highlight_edges: Optional[List[Tuple[BPlusNode, BPlusNode]]] = None):
        self.window.update_idletasks()
        
        self.canvas.delete("all")
        self.node_items.clear()

        self._draw_gradient_background()
        
        # 添加图例说明
        legend_y = 20
        self.canvas.create_text(20, legend_y, text="图例：", 
                               font=("Arial", 11, "bold"), fill="#A3E1FF", anchor="w")
        
        # 黄色 - 访问
        self.canvas.create_rectangle(80, legend_y-8, 100, legend_y+8, fill="#FCD34D", outline="#F59E0B", width=2)
        self.canvas.create_text(110, legend_y, text="", font=("Arial", 9), fill="#E6F7FF", anchor="w")
        
        # 绿色 - 插入
        self.canvas.create_rectangle(200, legend_y-8, 220, legend_y+8, fill="#10B981", outline="#059669", width=2)
        self.canvas.create_text(230, legend_y, text="插入成功", font=("Arial", 9), fill="#E6F7FF", anchor="w")
        
        # 红色 - 分裂
        self.canvas.create_rectangle(320, legend_y-8, 340, legend_y+8, fill="#EF4444", outline="#DC2626", width=2)
        self.canvas.create_text(350, legend_y, text="节点分裂", font=("Arial", 9), fill="#E6F7FF", anchor="w")
        
        # 蓝色 - 新节点
        self.canvas.create_rectangle(440, legend_y-8, 460, legend_y+8, fill="#3B82F6", outline="#2563EB", width=2)
        self.canvas.create_text(470, legend_y, text="新建节点", font=("Arial", 9), fill="#E6F7FF", anchor="w")
        
        pos = self.compute_positions()
        if not pos:
            self.canvas.create_text(640, 300, text="空树（请输入键并插入）", 
                                   font=("Arial",20), fill="#94a3b8")
            self.canvas.config(scrollregion=(0,0,1400,900))
            self._refresh_leaf_list()
            return

        # 绘制边（高亮特定路径）
        for node, (cx, cy) in pos.items():
            if not node.is_leaf:
                for child in node.children:
                    if child in pos:
                        px, py = pos[child]
                        # 检查是否需要高亮这条边
                        is_highlighted = False
                        if highlight_edges:
                            for parent, child_node in highlight_edges:
                                if parent == node and child_node == child:
                                    is_highlighted = True
                                    break
                        
                        if is_highlighted:
                            # 高亮路径 - 更粗更亮
                            self.canvas.create_line(cx, cy + self.node_h/2, px, py - self.node_h/2, 
                                                   width=8, fill="#FCD34D", smooth=True)
                            self.canvas.create_line(cx, cy + self.node_h/2, px, py - self.node_h/2, 
                                                   width=4, fill="#FBBF24", smooth=True)
                        else:
                            # 普通边
                            self.canvas.create_line(cx, cy + self.node_h/2, px, py - self.node_h/2, 
                                                   width=4, fill="#072c37", smooth=True)
                            self.canvas.create_line(cx, cy + self.node_h/2, px, py - self.node_h/2, 
                                                   width=2, fill="#5eead4", smooth=True)

        # 绘制节点
        for node, (cx, cy) in pos.items():
            color = None
            if highlight and node in highlight:
                color = highlight[node]
            self._draw_node(node, cx, cy, fill_color=color)

        # 绘制叶节点链表指针
        for leaf in self.tree.leaves():
            pos_map = pos
            if leaf in pos_map and leaf.next in pos_map:
                lx, ly = pos_map[leaf]
                nx, ny = pos_map[leaf.next]
                left = lx + self.node_w/2
                right = nx - self.node_w/2
                self.canvas.create_line(left, ly, right, ny, arrow=LAST, 
                                       dash=(6,4), fill="#7dd3fc", width=2)

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

        # 根据状态选择颜色和边框
        if fill_color:
            base_fill = fill_color
            if fill_color == "#FCD34D":  # 访问中
                border_color = "#F59E0B"
                border_width = 3
            elif fill_color == "#10B981":  # 插入成功
                border_color = "#059669"
                border_width = 3
            elif fill_color == "#EF4444":  # 分裂
                border_color = "#DC2626"
                border_width = 3
            elif fill_color == "#3B82F6":  # 新节点
                border_color = "#2563EB"
                border_width = 3
            else:
                border_color = "#0fe6c4"
                border_width = 2
        else:
            base_fill = "#052635" if node.is_leaf else "#073146"
            border_color = "#0fe6c4"
            border_width = 2

        # 外层光晕
        glow_l, glow_t, glow_r, glow_b = left-6, top-6, right+6, bottom+6
        self._rounded_rect(glow_l, glow_t, glow_r, glow_b, r=12, fill="#06343b", outline="")
        
        # 主卡片
        self._rounded_rect(left, top, right, bottom, r=10, fill=base_fill, 
                          outline=border_color, width=border_width)
        
        # 节点类型标签
        node_type = "LEAF" if node.is_leaf else "INTERNAL"
        type_color = "#10B981" if node.is_leaf else "#3B82F6"
        self.canvas.create_text(cx, top - 18, text=node_type, 
                               font=("Arial", 8, "bold"), fill=type_color)
        
        # 键值
        text = " | ".join(str(k) for k in node.keys)
        if not text:
            text = "empty"
        self.canvas.create_text(cx, cy, text=text, 
                               font=("Consolas", 12, "bold"), fill="#E6F7FF")
        
        # 显示键的数量
        key_count = f"keys: {len(node.keys)}"
        self.canvas.create_text(cx, bottom + 18, text=key_count,
                               font=("Arial", 8), fill="#64748b")

    def _refresh_leaf_list(self):
        self.leaf_listbox.delete(0, END)
        leaves = self.tree.leaves()
        for leaf in leaves:
            self.leaf_listbox.insert(END, ", ".join(str(k) for k in leaf.keys))

    def clear_tree(self):
        if self.animating:
            return
        self.tree.clear()
        self.redraw()
        self.update_status("已清空 B+ 树")
        self.update_explanation("")

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
                self.update_explanation("所有键已成功插入到 B+ 树中")
                return
            k = keys[key_idx]
            key_idx += 1
            self.update_status(f"开始插入：{k} (剩余 {len(keys)-key_idx} 个)")
            events = self.tree.insert_with_steps(k)
            self._animate_events(events, lambda: self.window.after(200, process_next))
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
                # 计算访问路径（从根到当前节点的边）
                edges = []
                current = node
                while current.parent:
                    edges.append((current.parent, current))
                    current = current.parent
                
                self.redraw(highlight={node: "#FCD34D"}, highlight_edges=edges)
                
                node_type = "叶节点" if node.is_leaf else "内部节点"
                self.update_status(f"访问{node_type}: {node.keys}")
                
                # 详细解释
                if node.is_leaf:
                    explain = f"到达叶节点 {node.keys}\n准备在此节点插入数据"
                else:
                    explain = f"在内部节点 {node.keys} 中查找\n根据键值选择子节点继续向下"
                self.update_explanation(explain)
                
                i += 1
                self.window.after(500, step)
                
            elif evtype == 'insert':
                node = ev['node']
                self.redraw(highlight={node: "#10B981"})
                self.update_status(f"插入成功: {node.keys}")
                
                explain = f"键已插入到叶节点\n当前节点包含 {len(node.keys)} 个键"
                if len(node.keys) >= self.tree.order - 1:
                    explain += f"\n⚠️ 节点已满 (最多 {self.tree.order-1} 个键)"
                self.update_explanation(explain)
                
                i += 1
                self.window.after(700, step)
                
            elif evtype == 'split':
                node = ev['node']
                new_node = ev.get('new_node')
                promoted = ev.get('promoted')
                is_leaf = ev.get('is_leaf', False)
                
                hl = {node: "#EF4444"}
                if new_node is not None:
                    hl[new_node] = "#3B82F6"
                    
                self.redraw(highlight=hl)
                
                node_type = "叶节点" if is_leaf else "内部节点"
                self.update_status(f"{node_type}分裂: 提升键 {promoted}")
                
                # 详细解释分裂过程
                if new_node:
                    explain = f"节点分裂！\n"
                    explain += f"原节点（红色）: {node.keys}\n"
                    explain += f"新节点（蓝色）: {new_node.keys}\n"
                    explain += f"提升键 {promoted} 到父节点"
                    if is_leaf:
                        explain += f"\n\n叶节点分裂：保留提升键在右侧叶节点中"
                    else:
                        explain += f"\n\n内部节点分裂：提升键不保留在子节点中"
                else:
                    explain = f"创建新的根节点\n提升键: {promoted}"
                    
                self.update_explanation(explain)
                
                i += 1
                self.window.after(900, step)
            else:
                i += 1
                self.window.after(200, step)
        step()


if __name__ == '__main__':
    root = Tk()
    app = BPlusVisualizer(root)
    root.mainloop()