from tkinter import *
from tkinter import messagebox, ttk, filedialog
from binary_tree.huffman_tree.huffman_model import HuffmanModel, HuffmanNode
from typing import Dict, Tuple, List, Optional
import storage as storage
import json
from datetime import datetime
import os

class HuffmanVisualizer:
    def __init__(self, root):
        self.window = root
        self.window.config(bg="#F0F4F8")
        self.canvas_w = 920   
        self.canvas_h = 520
        container = Frame(self.window, bg="#F0F4F8")
        container.pack(fill=BOTH, expand=True, padx=10, pady=8)
        left_frame = Frame(container, bg="#F0F4F8")
        left_frame.pack(side=LEFT, fill=BOTH, expand=True)
        self.canvas = Canvas(left_frame, bg="#FBFDFF", width=self.canvas_w, height=self.canvas_h, bd=0, highlightthickness=0)
        self.canvas.pack(fill=BOTH, expand=False, padx=(0,8))
        self._draw_subtle_grid()
        right_frame = Frame(container, width=320, bg="#F0F4F8")
        right_frame.pack(side=RIGHT, fill=Y)
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("HeapTree.Treeview", 
                        background="#FFFFFF", 
                        foreground="#0B2545", 
                        rowheight=22, 
                        fieldbackground="#FFFFFF",
                        font=("Arial", 10))
        style.configure("HeapTree.Treeview.Heading", font=("Arial", 10, "bold"), background="#E6EEF8")
        style.map("HeapTree.Treeview", background=[('selected', '#FFD59E')])
        label = Label(right_frame, text="当前堆的快照（按权值排序）", bg="#F0F4F8", fg="#0B2545", font=("Arial", 11, "bold"))
        label.pack(padx=8, pady=(6,2), anchor="nw")
        columns = ("before", "after")
        self.heap_tree = ttk.Treeview(right_frame, columns=columns, show="headings", style="HeapTree.Treeview", height=20)
        self.heap_tree.heading("before", text="Before")
        self.heap_tree.heading("after", text="After")
        self.heap_tree.column("before", width=140, anchor="w")
        self.heap_tree.column("after", width=140, anchor="w")
        self.heap_tree.pack(padx=8, pady=4, fill=Y)
        bottom_right = Frame(right_frame, bg="#F0F4F8")
        bottom_right.pack(side=BOTTOM, fill=X, pady=8)
        Button(bottom_right, text="清空", command=self.clear_canvas, bg="#FFB74D").pack(side=LEFT, padx=6)
        Button(bottom_right, text="返回主界面", command=self.back_to_main, bg="#6EA8FE", fg="white").pack(side=RIGHT, padx=6)
        self.model = HuffmanModel()
        self.steps: List[Tuple[HuffmanNode, HuffmanNode, HuffmanNode]] = []
        self.snap_before: List[List[float]] = []
        self.snap_after: List[List[float]] = []

        self.node_vis: Dict = {}  
        self.animating = False

        self.node_w = 80
        self.node_h = 40
        self.base_y = self.canvas_h - 80
        self.gap_x = 30
        self.level_gap = 80

        ctrl_frame = Frame(self.window, bg="#F0F4F8")
        ctrl_frame.pack(fill=X, padx=12, pady=(0,6))

        Label(ctrl_frame, text="输入权值（逗号分隔）:", font=("Arial",11), bg="#F0F4F8").pack(side=LEFT, padx=6)
        self.input_var = StringVar()
        self.entry = Entry(ctrl_frame, textvariable=self.input_var, width=36, font=("Arial",11))
        self.entry.pack(side=LEFT, padx=6)
        self.entry.insert(0, "1,2,3,4")
        Button(ctrl_frame, text="逐步动画构建", command=self.start_animated_build, bg="#2E8B57", fg="white").pack(side=LEFT, padx=6)

        Button(ctrl_frame, text="保存 Huffman", command=self.save_tree, bg="#6C9EFF", fg="white").pack(side=LEFT, padx=6)
        Button(ctrl_frame, text="打开 Huffman", command=self.load_tree, bg="#6C9EFF", fg="white").pack(side=LEFT, padx=6)

        self.status_id = None
        self._draw_instructions()

    def _draw_instructions(self):
        for item in self.canvas.find_all():
            if "grid" not in self.canvas.gettags(item):
                self.canvas.delete(item)
        self.canvas.create_text(12, 12, anchor="nw", text="Huffman 构建：逐步合并最小两个节点并生成父节点。右侧显示每步堆快照 (Before / After)。", font=("Arial",11), fill="#0B2545")
        if self.status_id:
            try:
                self.canvas.delete(self.status_id)
            except Exception:
                pass
        self.status_id = self.canvas.create_text(self.canvas_w - 12, 12, anchor="ne", text="", font=("Arial",11,"bold"), fill="#0B2545")

    def _draw_subtle_grid(self):
        self.canvas.delete("all")
        step = 20
        w, h = self.canvas_w, self.canvas_h
        for x in range(0, w, step):
            self.canvas.create_line(x, 0, x, h, fill="#F1F5F9", tags=("grid",))
        for y in range(0, h, step):
            self.canvas.create_line(0, y, w, y, fill="#F1F5F9", tags=("grid",))

    def update_status(self, txt: str):
        if self.status_id:
            self.canvas.itemconfig(self.status_id, text=txt)
        else:
            self.status_id = self.canvas.create_text(self.canvas_w - 12, 12, anchor="ne", text=txt, font=("Arial",11,"bold"), fill="#0B2545")

    def _tree_clear(self):
        for iid in self.heap_tree.get_children():
            self.heap_tree.delete(iid)

    def _tree_insert_steps(self, snaps_before: List[List[float]]):
        self._tree_clear()
        for i, before in enumerate(snaps_before):
            before_str = ", ".join([self._fmt_num(x) for x in before])
            self.heap_tree.insert("", "end", iid=str(i), values=(before_str, ""))
        if not snaps_before:
            self.heap_tree.insert("", "end", iid="init", values=("", ""))

    def _tree_set_after(self, idx: int, after_list: List[float]):
        after_str = ", ".join([self._fmt_num(x) for x in after_list])
        iid = str(idx)
        if iid in self.heap_tree.get_children():
            self.heap_tree.set(iid, column="after", value=after_str)
        else:
            self.heap_tree.insert("", "end", iid=iid, values=("", after_str))

    def _tree_highlight(self, idx: int):
        iid = str(idx)
        try:
            self.heap_tree.selection_remove(self.heap_tree.selection())
        except Exception:
            pass
        if iid in self.heap_tree.get_children():
            self.heap_tree.selection_set(iid)
            self.heap_tree.see(iid)

    def _fmt_num(self, v: float) -> str:
        if abs(v - int(v)) < 1e-9:
            return str(int(v))
        return f"{v:.2f}"

    def parse_input(self) -> Optional[List[float]]:
        s = self.input_var.get().strip()
        if not s:
            messagebox.showinfo("提示", "请输入权值，例如：1,2,3,4")
            return None
        parts = [p.strip() for p in s.split(",") if p.strip() != ""]
        try:
            nums = [float(x) for x in parts]
        except Exception:
            messagebox.showerror("错误", "请输入数字（用逗号分隔）")
            return None
        return nums
        
    def _ensure_huffman_folder(self) -> str:
        return storage.ensure_save_subdir("huffman")
    def save_tree(self):
        weights = self.parse_input()
        positions = {"leaves": [], "parents": []}
        leaf_positions = []
        for k, v in list(self.node_vis.items()):
            if isinstance(k, tuple) and k[0] == "leaf":
                leaf_positions.append((k[1], float(v.get("cx", 0)), float(v.get("cy", 0))))
        if leaf_positions:
            leaf_positions.sort(key=lambda x: x[0])
            positions["leaves"] = [[cx, cy] for idx, cx, cy in leaf_positions]
        parent_positions = []
        for (a, b, p) in getattr(self, "steps", []):
            pv = self.node_vis.get(p.id)
            if pv:
                parent_positions.append([float(pv.get("cx", 0)), float(pv.get("cy", 0))])
            else:
                parent_positions.append(None)
        if parent_positions:
            positions["parents"] = parent_positions
        tree_dict = storage.tree_to_dict(getattr(self.model, "root", None))
        payload = {
            "type": "huffman",
            "weights": weights,
            "tree": tree_dict,
            "positions": positions,
            "metadata": {
                "saved_at": datetime.now().isoformat(),
                "node_count": len(tree_dict.get("nodes", [])) if isinstance(tree_dict, dict) else 0
            }
        }
        default_dir = self._ensure_huffman_folder()
        default_name = f"huffman_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = filedialog.asksaveasfilename(
            initialdir=default_dir,
            initialfile=default_name,
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="保存 Huffman 到文件"
        )
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        messagebox.showinfo("成功", f"Huffman 已保存到：\n{filepath}")
        self.update_status("保存成功")

    def load_tree(self):
        default_dir = self._ensure_huffman_folder()
        filepath = filedialog.askopenfilename(
            initialdir=default_dir,
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="从文件加载 Huffman"
        )
        with open(filepath, "r", encoding="utf-8") as f:
            obj = json.load(f)
        weights = [float(x) for x in obj.get("weights", [])]

        positions = {}
        positions = obj["positions"]
        leaf_pos_list = positions.get("leaves", []) if isinstance(positions, dict) else []
        parent_pos_list = positions.get("parents", []) if isinstance(positions, dict) else []

        self.model = HuffmanModel()
        root, steps, snaps_before, snaps_after = self.model.build_with_steps(weights)
        self.steps = steps
        self.snap_before = snaps_before
        self.snap_after = snaps_after

        self.node_vis.clear()
        self._draw_subtle_grid()
        self._draw_instructions()
        self._tree_clear()

        n = len(weights)
        total_w = n * self.node_w + max(0, (n - 1) * self.gap_x)
        start_x = max(self.node_w / 2 + 20, (self.canvas_w - total_w) / 2 + self.node_w / 2)
        for i, w in enumerate(weights):
            if i < len(leaf_pos_list) and leaf_pos_list[i] is not None:
                lp = leaf_pos_list[i]
                if isinstance(lp, dict):
                    cx = float(lp.get("cx", start_x + i * (self.node_w + self.gap_x)))
                    cy = float(lp.get("cy", self.base_y))
                elif isinstance(lp, (list, tuple)) and len(lp) >= 2:
                    cx = float(lp[0]); cy = float(lp[1])
                else:
                    cx = start_x + i * (self.node_w + self.gap_x); cy = self.base_y
            else:
                cx = start_x + i * (self.node_w + self.gap_x)
                cy = self.base_y
            rect = self.canvas.create_rectangle(cx - self.node_w/2, cy - self.node_h/2,
                                                cx + self.node_w/2, cy + self.node_h/2,
                                                fill="#E8F8F0", outline="#88C7A3", width=2)
            txt = self.canvas.create_text(cx, cy, text=self._fmt_num(w), font=("Arial",12,"bold"), fill="#0B2545")
            # 存放 leaf mapping（注意：later we may map child node.id -> this visual）
            self.node_vis[("leaf", i)] = {'cx': cx, 'cy': cy, 'rect': rect, 'text': txt, 'merged': False, 'weight': float(w)}

        # 绘制父节点（按 steps 顺序），优先使用 parent_pos_list 中的坐标
        for i, (a, b, p) in enumerate(steps):
            if i < len(parent_pos_list) and parent_pos_list[i] is not None:
                pp = parent_pos_list[i]
                if isinstance(pp, (list, tuple)) and len(pp) >= 2:
                    tx = float(pp[0]); ty = float(pp[1])
                else:
                    va = self.node_vis.get(a.id); vb = self.node_vis.get(b.id)
                    if va and vb:
                        tx = (va['cx'] + vb['cx'])/2
                        ty = min(va['cy'], vb['cy']) - self.level_gap
                    else:
                        tx = self.canvas_w/2
                        ty = self.base_y - (i+1) * self.level_gap
            else:
                va = self.node_vis.get(a.id)
                vb = self.node_vis.get(b.id)
                if va and vb:
                    tx = (va['cx'] + vb['cx'])/2
                    ty = min(va['cy'], vb['cy']) - self.level_gap
                else:
                    tx = self.canvas_w/2
                    ty = self.base_y - (i+1) * self.level_gap
            self._create_node_visual(p, tx, ty)
            self._link_parent_child(p, a)
            self._link_parent_child(p, b)
            self._mark_merged(a)
            self._mark_merged(b)
            if i < len(snaps_after):
                self._tree_set_after(i, snaps_after[i])
        self.update_status("已通过权值恢复 Huffman（如有保存的视觉坐标则使用之）")
        messagebox.showinfo("成功", f"已通过权值恢复 Huffman（共 {len(weights)} 个初始权值）")
        
    def start_animated_build(self):
        if self.animating:
            return
        nums = self.parse_input()
        if nums is None:
            return
        self.model = HuffmanModel()
        self.node_vis.clear()
        self.canvas.delete("all")
        self._draw_subtle_grid()
        self._draw_instructions()
        self.draw_initial_leaves(nums)
        root, self.steps, self.snap_before, self.snap_after = self.model.build_with_steps(nums)
        # 在 Treeview 里预填 before 列
        self._tree_insert_steps(self.snap_before)
        # 显示初始 heap（如果没有 steps 则显示整个初始数组）
        if self.snap_before:
            self.update_status("准备开始动画 (显示 第1步 前 的堆)")
            self._tree_highlight(0)
        else:
            self.update_status("无需合并（单个或空）")
            return
        if not self.steps:
            self.animating = False
            return
        self.animating = True
        self._animate_step(0)

    def _animate_step(self, idx: int):
        if idx >= len(self.steps):
            self.animating = False
            self.update_status("Huffman 构建完成")
            if self.snap_after:
                self._tree_set_after(len(self.steps)-1, self.snap_after[-1])
                self._tree_highlight(len(self.steps)-1)
            return

        a, b, p = self.steps[idx]
        self.update_status(f"步骤 {idx+1}/{len(self.steps)} ： 合并 {self._fmt_num(a.weight)} 与 {self._fmt_num(b.weight)} -> {self._fmt_num(p.weight)}")
        self._tree_highlight(idx)

        self._highlight_node(a, "yellow")  
        self._highlight_node(b, "yellow")

        va = self.node_vis.get(a.id)
        vb = self.node_vis.get(b.id)
        if va and vb:
            tx = (va['cx'] + vb['cx'])/2
            ty = min(va['cy'], vb['cy']) - self.level_gap
        else:
            tx = self.canvas_w/2
            ty = self.base_y - (idx+1)*self.level_gap

        # temp parent fly-in
        temp_cx = self.canvas_w/2
        temp_cy = 20
        temp_rect = self.canvas.create_rectangle(temp_cx - self.node_w/2, temp_cy - self.node_h/2,
                                                 temp_cx + self.node_w/2, temp_cy + self.node_h/2,
                                                 fill="#C6F6D5", outline="black", width=2)
        temp_text = self.canvas.create_text(temp_cx, temp_cy, text=self._fmt_num(p.weight), font=("Arial",12,"bold"))

        steps_move = 28
        dx = (tx - temp_cx)/steps_move
        dy = (ty - temp_cy)/steps_move
        delay = 14

        def move_step(i=0):
            if i < steps_move:
                try:
                    self.canvas.move(temp_rect, dx, dy)
                    self.canvas.move(temp_text, dx, dy)
                except Exception:
                    pass
                self.window.after(delay, lambda: move_step(i+1))
            else:
                try:
                    self.canvas.delete(temp_rect)
                    self.canvas.delete(temp_text)
                except Exception:
                    pass
                self._create_node_visual(p, tx, ty)
                self._link_parent_child(p, a)
                self._link_parent_child(p, b)
                self._mark_merged(a)
                self._mark_merged(b)
                # 更新 Treeview 的 After 列
                if idx < len(self.snap_after):
                    self._tree_set_after(idx, self.snap_after[idx])
                self._tree_highlight(idx)
                # 下一步
                self.window.after(520, lambda: self._animate_step(idx+1))

        move_step()

    def draw_initial_leaves(self, weights: List[float]):
        self.canvas.delete("all")
        self._draw_subtle_grid()
        self._draw_instructions()
        self.node_vis.clear()

        n = len(weights)
        total_w = n * self.node_w + max(0, (n-1) * self.gap_x)
        start_x = max(self.node_w/2 + 20, (self.canvas_w - total_w)/2 + self.node_w/2)
        for i, w in enumerate(weights):
            cx = start_x + i * (self.node_w + self.gap_x)
            cy = self.base_y
            rect = self.canvas.create_rectangle(cx - self.node_w/2, cy - self.node_h/2, cx + self.node_w/2, cy + self.node_h/2,
                                                fill="#E8F8F0", outline="#88C7A3", width=2)
            txt = self.canvas.create_text(cx, cy, text=self._fmt_num(w), font=("Arial",12,"bold"), fill="#0B2545")
            self.node_vis[("leaf", i)] = {'cx':cx, 'cy':cy, 'rect':rect, 'text':txt, 'merged':False, 'weight': float(w)}

    def _create_node_visual(self, node: HuffmanNode, cx: float, cy: float):
        rect = self.canvas.create_rectangle(cx - self.node_w/2, cy - self.node_h/2, cx + self.node_w/2, cy + self.node_h/2,
                                           fill="#FFFFFF", outline="#7DA7E0", width=2)
        txt = self.canvas.create_text(cx, cy, text=self._fmt_num(node.weight), font=("Arial",12,"bold"), fill="#0B2545")
        self.node_vis[node.id] = {'cx':cx, 'cy':cy, 'rect':rect, 'text':txt, 'merged':False, 'weight': node.weight, 'node_obj': node}
        
    def _link_parent_child(self, parent: HuffmanNode, child: HuffmanNode):
        pvis = self.node_vis.get(parent.id)
        cvis = self.node_vis.get(child.id)
        if not cvis:
            for k,v in list(self.node_vis.items()):
                if isinstance(k, tuple) and k[0] == "leaf":
                    if abs(v['weight'] - child.weight) < 1e-9 and not v['merged']:
                        cvis = v
                        self.node_vis[child.id] = cvis
                        del self.node_vis[k]
                        break
        if not pvis or not cvis:
            return
        sx = pvis['cx']; sy = pvis['cy'] + self.node_h/2
        ex = cvis['cx']; ey = cvis['cy'] - self.node_h/2
        midy = (sy + ey) / 2
        l1 = self.canvas.create_line(sx, sy, sx, midy, fill="#9FB9D9", width=2)
        l2 = self.canvas.create_line(sx, midy, ex, ey, arrow=LAST, fill="#9FB9D9", width=2)

    def _highlight_node(self, node: HuffmanNode, color: str):
        v = self.node_vis.get(node.id)
        if not v:
            for k,vv in self.node_vis.items():
                if isinstance(k, tuple) and k[0] == "leaf":
                    if abs(vv['weight'] - node.weight) < 1e-9 and not vv['merged']:
                        v = vv
                        self.node_vis[node.id] = v
                        del self.node_vis[k]
                        break
        if v:
            try:
                self.canvas.itemconfig(v['rect'], fill=color)
            except Exception:
                pass

    def _mark_merged(self, node: HuffmanNode):
        v = self.node_vis.get(node.id)
        if v:
            v['merged'] = True
            try:
                self.canvas.itemconfig(v['rect'], fill="#DDDDDD", outline="#BDBDBD")
            except Exception:
                pass

    def clear_canvas(self):
        if self.animating:
            return
        self.node_vis.clear()
        self.model = HuffmanModel()
        self.steps = []
        self.snap_before = []
        self.snap_after = []
        self._draw_subtle_grid()
        self._draw_instructions()
        self._tree_clear()
        self.update_status("已清空")

    def back_to_main(self):
        if self.animating:
            messagebox.showinfo("提示", "动画进行中，无法返回")
            return
        self.window.destroy()
        
if __name__ == '__main__':
    w = Tk()
    w.title("Huffman 构建可视化")
    w.geometry("1350x730")
    HuffmanVisualizer(w)
    w.mainloop()
