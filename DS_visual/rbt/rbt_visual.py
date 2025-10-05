# DS_visual/binary_tree/rbt_visual.py
from tkinter import *
from tkinter import messagebox
from typing import Dict, Tuple, List, Optional
from rbt.rbt_model import RBModel, RBNode, clone_tree
import storage as storage
from tkinter import filedialog

class RBTVisualizer:
    def __init__(self, root):
        self.window = root
        self.window.title("Red-Black Tree 可视化")
        self.window.config(bg="#F7F9FB")
        self.canvas_w = 1200
        self.canvas_h = 560
        self.canvas = Canvas(self.window, bg="white", width=self.canvas_w, height=self.canvas_h, bd=6, relief=RAISED)
        self.canvas.pack(padx=10, pady=8)

        self.model = RBModel()
        self.node_vis: Dict[str, Dict] = {}
        self.animating = False

        # layout params
        self.node_w = 120
        self.node_h = 44
        self.level_gap = 100
        self.margin_x = 40

        # controls
        self.input_var = StringVar()
        self.create_controls()
        self.draw_instructions()

    def create_controls(self):
        frame = Frame(self.window, bg="#F7F4F8")
        frame.pack(pady=(0,6), fill=X)

        Label(frame, text="输入（按插入顺序，逗号分隔）:", bg="#F7F4F8", font=("Arial",11)).pack(side=LEFT, padx=6)
        entry = Entry(frame, textvariable=self.input_var, width=44, font=("Arial",11))
        entry.pack(side=LEFT, padx=6)
        entry.insert(0, "10,5,20")

        Button(frame, text="Insert (动画)", bg="#C62828", fg="white", command=self.start_insert_animated).pack(side=LEFT, padx=6)
        Button(frame, text="清空", bg="#FFB74D", command=self.clear_canvas).pack(side=LEFT, padx=6)
        Button(frame, text="返回主界面", bg="#6EA8FE", fg="white", command=self.back_to_main).pack(side=LEFT, padx=6)
        Button(frame, text="保存", bg="#6C9EFF", command=self.save_structure).pack(side=LEFT, padx=6)
        Button(frame, text="打开", bg="#6C9EFF", command=self.load_structure).pack(side=LEFT, padx=6)

        self.status_id = None

    def draw_instructions(self):
        self.canvas.delete("all")
        self.node_vis.clear()
        self.canvas.create_text(12, 12, anchor="nw", text="红黑树插入演示：展示搜索路径、插入为红节点、重染色与旋转修复（逐步快照）", font=("Arial",11))
        self.status_id = self.canvas.create_text(self.canvas_w - 12, 12, anchor="ne", text="", font=("Arial",11,"bold"), fill="darkred")

    def update_status(self, txt: str):
        if self.status_id:
            self.canvas.itemconfig(self.status_id, text=txt)
        else:
            self.status_id = self.canvas.create_text(self.canvas_w - 12, 12, anchor="ne", text=txt, font=("Arial",11,"bold"), fill="darkred")

    # ---------- small helper to draw edge ----------
    def _draw_connection(self, cx, cy, tx, ty):
        top = cy + self.node_h/2
        bot = ty - self.node_h/2
        midy = (top + bot) / 2
        l1 = self.canvas.create_line(cx, top, cx, midy, width=2)
        l2 = self.canvas.create_line(cx, midy, tx, bot, arrow=LAST, width=2)
        return (l1, l2)

    # ---------- layout computation (same style as AVL visualizer) ----------
    def compute_positions_for_root(self, root: Optional[RBNode]) -> Dict[str, Tuple[float, float]]:
        res: Dict[str, Tuple[float,float]] = {}
        if not root:
            return res

        inorder_nodes: List[RBNode] = []
        depths: Dict[RBNode, int] = {}
        def inorder(n: Optional[RBNode], d: int):
            if not n:
                return
            inorder(n.left, d+1)
            inorder_nodes.append(n)
            depths[n] = d
            inorder(n.right, d+1)
        inorder(root, 0)
        n = len(inorder_nodes)
        if n == 0:
            return res
        width = max(200, self.canvas_w - 2*self.margin_x)
        counts: Dict[str,int] = {}
        for i, node in enumerate(inorder_nodes):
            base = str(node.val)
            cnt = counts.get(base, 0)
            counts[base] = cnt + 1
            key = f"{base}#{cnt}" if cnt > 0 else base
            if n == 1:
                x = self.canvas_w/2
            else:
                x = self.margin_x + i * (width / (n-1))
            y = 60 + depths[node] * self.level_gap
            res[key] = (x, y)
        return res

    def draw_tree_from_root(self, root: Optional[RBNode]):
        self.canvas.delete("all")
        self.draw_instructions()
        if root is None:
            self.canvas.create_text(self.canvas_w/2, self.canvas_h/2, text="空树", font=("Arial",18), fill="gray")
            return

        pos = self.compute_positions_for_root(root)

        inorder_nodes: List[RBNode] = []
        def inorder_collect(n: Optional[RBNode]):
            if not n:
                return
            inorder_collect(n.left)
            inorder_nodes.append(n)
            inorder_collect(n.right)
        inorder_collect(root)

        node_to_key: Dict[RBNode, str] = {}
        counts: Dict[str,int] = {}
        for node in inorder_nodes:
            base = str(node.val)
            cnt = counts.get(base, 0)
            counts[base] = cnt + 1
            key = f"{base}#{cnt}" if cnt > 0 else base
            node_to_key[node] = key

        def draw_edges(n: Optional[RBNode]):
            if not n:
                return
            k = node_to_key[n]
            cx, cy = pos[k]
            if n.left:
                lk = node_to_key[n.left]
                lx, ly = pos[lk]
                self._draw_connection(cx, cy, lx, ly)
            if n.right:
                rk = node_to_key[n.right]
                rx, ry = pos[rk]
                self._draw_connection(cx, cy, rx, ry)
            draw_edges(n.left); draw_edges(n.right)
        draw_edges(root)

        self.node_vis.clear()
        for node, key in node_to_key.items():
            cx, cy = pos[key]
            left = cx - self.node_w/2; top = cy - self.node_h/2; right = cx + self.node_w/2; bottom = cy + self.node_h/2
            fillcol = "#FFCDD2" if node.color == "R" else "#333333"
            rect = self.canvas.create_rectangle(left, top, right, bottom, fill=fillcol, outline="black", width=2)
            x1 = left + 28; x2 = x1 + 64
            self.canvas.create_line(x1, top, x1, bottom, width=1)
            self.canvas.create_line(x2, top, x2, bottom, width=1)
            txt_fill = "black" if node.color == "R" else "white"
            txt = self.canvas.create_text((x1+x2)/2, (top+bottom)/2, text=str(node.val), font=("Arial",12,"bold"), fill=txt_fill)
            # also show color letter
            color_label = self.canvas.create_text(left+10, (top+bottom)/2, text=node.color, font=("Arial",9,"bold"))
            self.node_vis[key] = {'rect':rect, 'text':txt, 'cx':cx, 'cy':cy, 'val':str(node.val), 'color_label': color_label}

    # ---------- insertion flow (search path highlight -> fly-in -> events playback) ----------
    def start_insert_animated(self):
        if self.animating:
            return
        s = self.input_var.get().strip()
        if not s:
            messagebox.showinfo("提示", "请输入数字，例如：10,5,20")
            return
        batch = [p.strip() for p in s.split(",") if p.strip()!=""]
        if not batch:
            return
        self.batch = batch
        self.animating = True
        self._insert_seq(0)

    def _insert_seq(self, idx: int):
        if idx >= len(self.batch):
            self.animating = False
            self.update_status("所有插入完成")
            return

        val = self.batch[idx]
        inserted_node, path_nodes, events, snapshots = self.model.insert_with_steps(val)

        snap_pre = snapshots[0]
        snap_after_insert = snapshots[1] if len(snapshots) > 1 else None

        pos_pre = self.compute_positions_for_root(snap_pre)
        val_to_keys_pre: Dict[str, List[str]] = {}
        for k in pos_pre.keys():
            base = k.split('#')[0]
            val_to_keys_pre.setdefault(base, []).append(k)

        def highlight_path(i=0):
            if i >= len(path_nodes):
                self.update_status(f"插入 {val}: 开始落位")
                self.animate_flyin_new(val, snap_after_insert, lambda: self._after_insert_events(events, snapshots, idx))
                return
            node = path_nodes[i]
            v = str(node.val)
            keylist = val_to_keys_pre.get(v, [])
            if keylist:
                key = keylist.pop(0)
                self.draw_tree_from_root(snap_pre)
                try:
                    self.canvas.itemconfig(self.node_vis[key]['rect'], outline="orange", width=4)
                except Exception:
                    pass
            else:
                self.draw_tree_from_root(snap_pre)
            self.update_status(f"搜索路径: 访问 {v} (step {i})")
            self.window.after(420, lambda: highlight_path(i+1))

        highlight_path(0)

    def animate_flyin_new(self, val_str: str, snap_after_insert: Optional[RBNode], on_complete):
        if not snap_after_insert:
            on_complete(); return
        pos_after = self.compute_positions_for_root(snap_after_insert)
        candidate_keys = [k for k in pos_after.keys() if k.split('#')[0] == str(val_str)]
        if not candidate_keys:
            on_complete(); return
        target_key = candidate_keys[-1]
        tx, ty = pos_after[target_key]

        sx, sy = self.canvas_w/2, 20
        left = sx - self.node_w/2; top = sy - self.node_h/2; right = sx + self.node_w/2; bottom = sy + self.node_h/2
        temp_rect = self.canvas.create_rectangle(left, top, right, bottom, fill="#FFE0B2", outline="black", width=2)
        x1 = left + 28; x2 = x1 + 64
        temp_text = self.canvas.create_text((x1+x2)/2, (top+bottom)/2, text=str(val_str), font=("Arial",12,"bold"))

        steps = 30
        dx = (tx - sx)/steps
        dy = (ty - sy)/steps
        delay = 12
        def step(i=0):
            if i < steps:
                try:
                    self.canvas.move(temp_rect, dx, dy)
                    self.canvas.move(temp_text, dx, dy)
                except Exception:
                    pass
                self.window.after(delay, lambda: step(i+1))
            else:
                try:
                    self.canvas.delete(temp_rect)
                    self.canvas.delete(temp_text)
                except Exception:
                    pass
                self.draw_tree_from_root(snap_after_insert)
                try:
                    self.canvas.itemconfig(self.node_vis[target_key]['rect'], fill="#FFCDD2")
                except Exception:
                    pass
                self.window.after(300, on_complete)
        step()

    # ---------- animate a single event (recolor or rotation) ----------
    def _animate_single_event(self, before_root: Optional[RBNode], after_root: Optional[RBNode], event: Dict, on_done):
        pos_before = self.compute_positions_for_root(before_root)
        pos_after = self.compute_positions_for_root(after_root)

        self.draw_tree_from_root(before_root)

        keys_common = set(pos_before.keys()) & set(pos_after.keys())
        moves = []
        for k in keys_common:
            item = self.node_vis.get(k)
            if not item:
                continue
            sx, sy = pos_before[k]
            tx, ty = pos_after[k]
            moves.append((k, item['rect'], item['text'], sx, sy, tx, ty))

        label_id = None
        if event.get('type') == 'recolor':
            label_text = "重染色 (parent/uncle -> B, grand -> R)"
            # try to find parent/uncle keys for label
            parent = event.get('parent'); uncle = event.get('uncle'); grand = event.get('grand')
            pk = next((k for k in pos_before.keys() if k.split('#')[0] == str(parent.val)), None) if parent else None
            gk = next((k for k in pos_before.keys() if k.split('#')[0] == str(grand.val)), None) if grand else None
            if pk and gk:
                px, py = pos_before[pk]; gx, gy = pos_before[gk]
                mx = (px + gx)/2
                try:
                    label_id = self.canvas.create_text(mx, min(py, gy)-36, text=label_text, font=("Arial",10,"bold"), fill="brown")
                except:
                    label_id = None
        else:
            label_text = event.get('type', 'rotate')
            # place label near root of affected before snapshot if possible
            z = event.get('x') or event.get('z')
            if z:
                zk = next((k for k in pos_before.keys() if k.split('#')[0] == str(z.val)), None)
                if zk:
                    zx, zy = pos_before[zk]
                    try:
                        label_id = self.canvas.create_text(zx, zy-36, text=label_text, font=("Arial",10,"bold"), fill="red")
                    except:
                        label_id = None

        frames = 24
        delay = 30

        def rect_center_coords(rect_id):
            coords = self.canvas.coords(rect_id)
            if not coords or len(coords) < 4:
                return (0,0)
            x1,y1,x2,y2 = coords
            return ((x1+x2)/2, (y1+y2)/2)

        def frame_step(f=0):
            if f >= frames:
                self.draw_tree_from_root(after_root)
                if label_id:
                    try: self.canvas.delete(label_id)
                    except: pass
                self.window.after(300, on_done)
                return
            t = (f+1)/frames
            for (k, rect_id, text_id, sx, sy, tx, ty) in moves:
                cur_cx = sx + (tx - sx) * t
                cur_cy = sy + (ty - sy) * t
                try:
                    ccx, ccy = rect_center_coords(rect_id)
                    if ccx == 0 and ccy == 0:
                        continue
                    dx = cur_cx - ccx
                    dy = cur_cy - ccy
                    self.canvas.move(rect_id, dx, dy)
                    self.canvas.move(text_id, dx, dy)
                    # move color label if exists
                    # find color_label by scanning items (not ideal but ok)
                except Exception:
                    pass
            self.window.after(delay, lambda: frame_step(f+1))
        frame_step(0)

    def _animate_events_sequence(self, events: List[Dict], snapshots: List[Optional[RBNode]], insertion_index: int, on_all_done):
        if not events:
            on_all_done(); return

        def step(i=0):
            if i >= len(events):
                on_all_done()
                return
            before_root = snapshots[1 + i]
            after_root = snapshots[2 + i]
            ev = events[i]
            self.update_status(f"执行步骤 {i+1}/{len(events)}: {ev.get('type')}")
            self._animate_single_event(before_root, after_root, ev, lambda: step(i+1))
        step(0)

    def _after_insert_events(self, events, snapshots, insertion_idx):
        if not events:
            self.draw_tree_from_root(clone_tree(self.model.root))
            self.window.after(300, lambda: self._insert_seq(insertion_idx+1))
            return

        def done_all():
            self.draw_tree_from_root(clone_tree(self.model.root))
            self.window.after(300, lambda: self._insert_seq(insertion_idx+1))
        self._animate_events_sequence(events, snapshots, insertion_idx, done_all)

    # ---------- clear & back ----------
    def clear_canvas(self):
        if self.animating:
            return
        self.model = RBModel()
        self.node_vis.clear()
        self.canvas.delete("all")
        self.draw_instructions()
        self.update_status("已清空")

    def back_to_main(self):
        self.window.destroy()

    def save_structure(self):
        root = self.model.root
        ok = storage.save_tree_to_file(root)
        if ok:
            self.update_status("保存成功")

    def load_structure(self):
        tree_dict = storage.load_tree_from_file()
        if not tree_dict:
            return
        from rbt.rbt_model import RBNode as RBNodeClass
        newroot = storage.tree_dict_to_nodes(tree_dict, RBNodeClass)
        self.model.root = newroot
        self.draw_tree_from_root(clone_tree(self.model.root))
        self.update_status("已经从文件加载并恢复结构")


if __name__ == '__main__':
    w = Tk()
    w.title("Red-Black Tree 可视化")
    w.geometry("1350x730")
    RBVisualizer(w)
    w.mainloop()
