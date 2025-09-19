# DS_visual/binary_tree/avl_visual.py
from tkinter import *
from tkinter import messagebox
from typing import Dict, Tuple, List, Optional
from avl.avl_model import AVLModel, AVLNode, clone_tree
import storage as storage
from tkinter import filedialog

class AVLVisualizer:
    def __init__(self, root):
        self.window = root
        self.window.title("AVL 可视化（增强旋转动画）")
        self.window.config(bg="#EAF5FF")
        self.canvas_w = 1200
        self.canvas_h = 560

        # 顶部渐变
        self.header = Canvas(self.window, height=90, bd=0, highlightthickness=0)
        self.header.pack(fill=X)
        self._draw_header_gradient(self.header, 90, "#3a8dde", "#70b7ff")
        self.header.create_text(40, 32, anchor='w', text="AVL树动态演示", font=("Helvetica", 26, "bold"), fill="#062A4A")
        self.header.create_text(40, 62, anchor='w', text="平衡二叉树 • 动画旋转 • 路径高亮 • 交互体验", font=("Helvetica", 12), fill="#EAF6FF")

        # 主卡片区（带阴影）
        shadow = Frame(self.window, bg="#d7e9ff")
        shadow.place(relx=0.5, y=90, anchor='n', relwidth=0.92, height=610)
        card = Frame(self.window, bg="white", bd=0, highlightthickness=0)
        card.place(relx=0.5, y=88, anchor='n', relwidth=0.92, height=606)

        # 画布区
        self.canvas = Canvas(card, bg="#F8FBFF", width=self.canvas_w, height=self.canvas_h, bd=0, highlightthickness=0)
        self.canvas.pack(padx=10, pady=(18,8))

        self.model = AVLModel()
        self.node_vis: Dict[str, Dict] = {}
        self.animating = False

        # layout params
        self.node_w = 120
        self.node_h = 44
        self.level_gap = 100
        self.margin_x = 40

        # controls
        self.input_var = StringVar()
        self.create_controls(card)
        self.draw_instructions()

    def _draw_header_gradient(self, canvas, h, c1, c2):
        canvas.delete("grad")
        width = canvas.winfo_width() or 1200
        steps = 40
        for i in range(steps):
            t = i / (steps - 1)
            r1, g1, b1 = int(c1[1:3],16), int(c1[3:5],16), int(c1[5:7],16)
            r2, g2, b2 = int(c2[1:3],16), int(c2[3:5],16), int(c2[5:7],16)
            r = int(r1 + (r2 - r1) * t)
            g = int(g1 + (g2 - g1) * t)
            b = int(b1 + (b2 - b1) * t)
            color = f'#{r:02x}{g:02x}{b:02x}'
            y0 = int(i * (h / steps))
            y1 = int((i+1) * (h / steps))
            canvas.create_rectangle(0, y0, width, y1, outline=color, fill=color, tags="grad")


    def create_controls(self, parent):
        frame = Frame(parent, bg="#F7F4F8")
        frame.pack(pady=(0,6), fill=X)

        Label(frame, text="输入（逗号分隔）:", bg="#F7F4F8", font=("微软雅黑",12)).pack(side=LEFT, padx=8)
        entry = Entry(frame, textvariable=self.input_var, width=32, font=("微软雅黑",12), bd=2, relief=GROOVE)
        entry.pack(side=LEFT, padx=8)
        entry.insert(0, "1,2,3")

        def style_btn(btn, color):
            btn.config(font=("微软雅黑",12,"bold"), bd=0, relief="flat", bg=color, fg="white", activebackground="#eaf6ff", cursor="hand2")

        btn_insert = Button(frame, text="插入动画", command=self.start_insert_animated)
        style_btn(btn_insert, "#2E8B57")
        btn_insert.pack(side=LEFT, padx=8)

        btn_clear = Button(frame, text="清空", command=self.clear_canvas)
        style_btn(btn_clear, "#FFB74D")
        btn_clear.pack(side=LEFT, padx=8)

        btn_back = Button(frame, text="返回主界面", command=self.back_to_main)
        style_btn(btn_back, "#6EA8FE")
        btn_back.pack(side=LEFT, padx=8)

        btn_save = Button(frame, text="保存", command=self.save_structure)
        style_btn(btn_save, "#6C9EFF")
        btn_save.pack(side=LEFT, padx=8)

        btn_load = Button(frame, text="打开", command=self.load_structure)
        style_btn(btn_load, "#6C9EFF")
        btn_load.pack(side=LEFT, padx=8)

        self.status_id = None

  

    def draw_instructions(self):
        self.canvas.delete("all")
        self.node_vis.clear()
        self.canvas.create_text(18, 18, anchor="nw", text="🌟 AVL插入演示：路径高亮 + 动画旋转 + 节点平滑移动", font=("微软雅黑",13,"bold"), fill="#3a8dde")
        self.status_id = self.canvas.create_text(self.canvas_w - 18, 18, anchor="ne", text="", font=("微软雅黑",12,"bold"), fill="#2ecc71")

    def update_status(self, txt: str):
        if self.status_id:
            self.canvas.itemconfig(self.status_id, text=txt)
        else:
            self.status_id = self.canvas.create_text(self.canvas_w - 18, 18, anchor="ne", text=txt, font=("微软雅黑",12,"bold"), fill="#2ecc71")

    # ---------- small helper to draw edge ----------
    def _draw_connection(self, cx, cy, tx, ty):
        """Draw two-segment arrow from parent center (cx,cy) to child center (tx,ty)."""
        top = cy + self.node_h/2
        bot = ty - self.node_h/2
        midy = (top + bot) / 2
        l1 = self.canvas.create_line(cx, top, cx, midy, width=2)
        l2 = self.canvas.create_line(cx, midy, tx, bot, arrow=LAST, width=2)
        return (l1, l2)

    # ---------- helper: layout computation for ANY given root (snapshot) ----------
    def compute_positions_for_root(self, root: Optional[AVLNode]) -> Dict[str, Tuple[float, float]]:
        """
        Returns mapping key -> (cx,cy) for a given snapshot root.
        Keys are "val" or "val#k" to disambiguate duplicates (k is occurrence index).
        """
        res: Dict[str, Tuple[float,float]] = {}
        if not root:
            return res

        # inorder traversal to determine horizontal ordering and depth
        inorder_nodes: List[AVLNode] = []
        depths: Dict[AVLNode, int] = {}
        def inorder(n: Optional[AVLNode], d: int):
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
        # assign keys while handling duplicates by count
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

    def draw_tree_from_root(self, root: Optional[AVLNode]):
        self.canvas.delete("all")
        self.draw_instructions()
        if root is None:
            self.canvas.create_text(self.canvas_w/2, self.canvas_h/2, text="空树", font=("微软雅黑",20,"bold"), fill="#b2bec3")
            return

        pos = self.compute_positions_for_root(root)
        inorder_nodes: List[AVLNode] = []
        def inorder_collect(n: Optional[AVLNode]):
            if not n:
                return
            inorder_collect(n.left)
            inorder_nodes.append(n)
            inorder_collect(n.right)
        inorder_collect(root)
        node_to_key: Dict[AVLNode, str] = {}
        counts: Dict[str,int] = {}
        for node in inorder_nodes:
            base = str(node.val)
            cnt = counts.get(base, 0)
            counts[base] = cnt + 1
            key = f"{base}#{cnt}" if cnt > 0 else base
            node_to_key[node] = key

        # draw edges recursively
        def draw_edges(n: Optional[AVLNode]):
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

        # draw nodes and populate node_vis
        self.node_vis.clear()
        for node, key in node_to_key.items():
            cx, cy = pos[key]
            left = cx - self.node_w/2; top = cy - self.node_h/2; right = cx + self.node_w/2; bottom = cy + self.node_h/2
            # 圆角矩形节点
            rect = self.canvas.create_oval(left, top, right, bottom, fill="#EAF6FF", outline="#3a8dde", width=3)
            txt = self.canvas.create_text(cx, cy, text=str(node.val), font=("微软雅黑",14,"bold"), fill="#2d3436")
            # 节点阴影
            shadow = self.canvas.create_oval(left+4, top+4, right+4, bottom+4, fill="#d7e9ff", outline="", width=0)
            self.canvas.tag_lower(shadow, rect)
            self.node_vis[key] = {'rect':rect, 'text':txt, 'cx':cx, 'cy':cy, 'val':str(node.val)}

    # ---------- main insertion animation flow ----------
    def start_insert_animated(self):
        if self.animating:
            return
        s = self.input_var.get().strip()
        if not s:
            messagebox.showinfo("提示", "请输入数字，例如：1,2,3")
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

        # call model: it returns new node, path, rotations, snapshots (snapshots[0]=pre, [1]=after-insert, [2..]=after rotations)
        inserted_node, path_nodes, rotations, snapshots = self.model.insert_with_steps(val)

        snap_pre = snapshots[0]
        snap_after_insert = snapshots[1] if len(snapshots) > 1 else None

        # prepare mapping of pre-snapshot keys per value to highlight path
        pos_pre = self.compute_positions_for_root(snap_pre)
        val_to_keys_pre: Dict[str, List[str]] = {}
        for k in pos_pre.keys():
            base = k.split('#')[0]
            val_to_keys_pre.setdefault(base, []).append(k)

        # sequentially highlight path over pre-snapshot
        def highlight_path(i=0):
            if i >= len(path_nodes):
                # proceed to fly-in
                self.update_status(f"插入 {val}: 开始落位")
                self.animate_flyin_new(val, snap_after_insert, lambda: self._after_insert_rotations(rotations, snapshots, idx))
                return
            node = path_nodes[i]
            v = str(node.val)
            keylist = val_to_keys_pre.get(v, [])
            if keylist:
                key = keylist.pop(0)
                self.draw_tree_from_root(snap_pre)
                try:
                    self.canvas.itemconfig(self.node_vis[key]['rect'], fill="yellow")
                except Exception:
                    pass
            else:
                self.draw_tree_from_root(snap_pre)
            self.update_status(f"搜索路径: 访问 {v} (step {i})")
            self.window.after(420, lambda: highlight_path(i+1))

        highlight_path(0)

    def animate_flyin_new(self, val_str: str, snap_after_insert: Optional[AVLNode], on_complete):
        """Fly new node into position using snap_after_insert to determine target key."""
        if not snap_after_insert:
            on_complete(); return
        pos_after = self.compute_positions_for_root(snap_after_insert)
        candidate_keys = [k for k in pos_after.keys() if k.split('#')[0] == str(val_str)]
        if not candidate_keys:
            on_complete(); return
        # choose last candidate (heuristic: newly inserted tends to be right-most among equals)
        target_key = candidate_keys[-1]
        tx, ty = pos_after[target_key]

        # create temporary visual at top and animate
        sx, sy = self.canvas_w/2, 20
        left = sx - self.node_w/2; top = sy - self.node_h/2; right = sx + self.node_w/2; bottom = sy + self.node_h/2
        temp_rect = self.canvas.create_rectangle(left, top, right, bottom, fill="#C6F6D5", outline="black", width=2)
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
                # draw after-insert snapshot so new node appears
                self.draw_tree_from_root(snap_after_insert)
                # highlight new node
                try:
                    self.canvas.itemconfig(self.node_vis[target_key]['rect'], fill="lightgreen")
                except Exception:
                    pass
                self.window.after(300, on_complete)
        step()

    # ---------- rotation animation (precise interpolation) ----------
    def _animate_single_rotation(self, before_root: Optional[AVLNode], after_root: Optional[AVLNode], rotation_info: Dict, on_done):
        """
        animate nodes from before_root positions to after_root positions (interpolation).
        rotation_info used to render label/arc.
        """
        pos_before = self.compute_positions_for_root(before_root)
        pos_after = self.compute_positions_for_root(after_root)

        # draw before_root to get canvas items mapping
        self.draw_tree_from_root(before_root)

        keys_common = set(pos_before.keys()) & set(pos_after.keys())
        moves = []
        for k in keys_common:
            item = self.node_vis.get(k)
            if not item:
                continue
            sx, sy = pos_before[k]
            tx, ty = pos_after[k]
            # rect coords top-left used by canvas.coords
            moves.append((k, item['rect'], item['text'], sx, sy, tx, ty))

        # draw arc/label to indicate rotation direction (best-effort)
        rtype = rotation_info.get('type', '')
        label_text = f"旋转: {rtype}"
        z = rotation_info.get('z'); y = rotation_info.get('y')
        zkey = None; ykey = None
        if z:
            zkey = next((k for k in pos_before.keys() if k.split('#')[0]==str(z.val)), None)
        if y:
            ykey = next((k for k in pos_before.keys() if k.split('#')[0]==str(y.val)), None)

        arc_id = None; label_id = None
        if zkey and ykey:
            zx, zy = pos_before[zkey]; yx, yy = pos_before[ykey]
            midx = (zx + yx)/2
            topy = min(zy, yy) - 30
            try:
                arc_id = self.canvas.create_arc(midx-30, topy-20, midx+30, topy+20, start=0, extent=180, style=ARC, width=2, outline="red")
                label_id = self.canvas.create_text(midx, topy-28, text=label_text, font=("Arial",10,"bold"), fill="red")
            except Exception:
                arc_id = None; label_id = None

        frames = 24
        delay = 30

        # Helper to get current center of rect
        def rect_center_coords(rect_id):
            coords = self.canvas.coords(rect_id)  # [x1,y1,x2,y2]
            if not coords or len(coords) < 4:
                return (0,0)
            x1,y1,x2,y2 = coords
            return ((x1+x2)/2, (y1+y2)/2)

        def frame_step(f=0):
            if f >= frames:
                # final: draw after_root snapshot to ensure exact positions
                self.draw_tree_from_root(after_root)
                if arc_id:
                    try: self.canvas.delete(arc_id)
                    except: pass
                if label_id:
                    try: self.canvas.delete(label_id)
                    except: pass
                self.window.after(300, on_done)
                return
            t = (f+1)/frames
            for (k, rect_id, text_id, sx, sy, tx, ty) in moves:
                # compute desired current center
                cur_cx = sx + (tx - sx) * t
                cur_cy = sy + (ty - sy) * t
                # get current center to compute delta
                try:
                    cur_coords = rect_center_coords(rect_id)
                    if cur_coords == (0,0):
                        continue
                    ccx, ccy = cur_coords
                    dx = cur_cx - ccx
                    dy = cur_cy - ccy
                    self.canvas.move(rect_id, dx, dy)
                    self.canvas.move(text_id, dx, dy)
                except Exception:
                    pass
            self.window.after(delay, lambda: frame_step(f+1))
        frame_step(0)

    def _animate_rotations_sequence(self, rotations: List[Dict], snapshots: List[Optional[AVLNode]], insertion_index: int, on_all_done):
        """
        rotations[i] corresponds to snapshots[i+2] (snapshots[0]=pre, [1]=after-insert)
        """
        if not rotations:
            on_all_done(); return

        def step(i=0):
            if i >= len(rotations):
                on_all_done()
                return
            before_root = snapshots[1 + i]   # after previous step (i==0 -> after-insert)
            after_root = snapshots[2 + i]
            rot_info = rotations[i]
            self.update_status(f"执行旋转 {i+1}/{len(rotations)}: {rot_info.get('type')}")
            self._animate_single_rotation(before_root, after_root, rot_info, lambda: step(i+1))
        step(0)

    def _after_insert_rotations(self, rotations, snapshots, insertion_idx):
        if not rotations:
            self.draw_tree_from_root(clone_tree(self.model.root))
            self.window.after(300, lambda: self._insert_seq(insertion_idx+1))
            return

        def done_all():
            self.draw_tree_from_root(clone_tree(self.model.root))
            self.window.after(300, lambda: self._insert_seq(insertion_idx+1))
        self._animate_rotations_sequence(rotations, snapshots, insertion_idx, done_all)

    # ---------- clear & back ----------
    def clear_canvas(self):
        if self.animating:
            return
        self.model = AVLModel()
        self.node_vis.clear()
        self.canvas.delete("all")
        self.draw_instructions()
        self.update_status("已清空")

    def back_to_main(self):
        if self.animating:
            messagebox.showinfo("提示", "动画进行中，无法返回")
            return
        self.window.destroy()
        from main_interface import MainInterface
        main_window = Tk()
        app = MainInterface(main_window)
        main_window.mainloop()
    def save_structure(self):
        root = self.model.root
        ok = storage.save_tree_to_file(root)
        if ok:
            self.update_status("保存成功")
    
    def load_structure(self):
        tree_dict = storage.load_tree_from_file()
        if not tree_dict:
            return
        from avl.avl_model import AVLNode as AVLNodeClass 
        newroot = storage.tree_dict_to_nodes(tree_dict, AVLNodeClass)
        self.model.root = newroot
        self.draw_tree_from_root(clone_tree(self.model.root))
        self.update_status("已经从文件加载并恢复结构")

if __name__ == '__main__':
    w = Tk()
    w.title("AVL 可视化（增强旋转动画）")
    w.geometry("1350x730")
    AVLVisualizer(w)
    w.mainloop()
