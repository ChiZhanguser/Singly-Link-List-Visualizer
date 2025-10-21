from tkinter import *
from tkinter import messagebox
from typing import Dict, Tuple, List, Optional
from avl.avl_model import AVLModel, AVLNode, clone_tree
import storage as storage
from tkinter import filedialog
from datetime import datetime

class AVLVisualizer:
    def __init__(self, root):
        self.window = root
        self.window.title("AVL 可视化")
        self.window.config(bg="#F7F9FB")
        self.canvas_w = 1200
        self.canvas_h = 560
        self.canvas = Canvas(self.window, bg="white", width=self.canvas_w, height=self.canvas_h, bd=6, relief=RAISED)
        self.canvas.pack(padx=10, pady=8)

        self.model = AVLModel()
        # node_vis: key -> dict (key is like "val" or "val#k" in a snapshot)
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
        entry.insert(0, "1,2,3")
        Button(frame, text="Insert (动画)", bg="#2E8B57", fg="white", command=self.start_insert_animated).pack(side=LEFT, padx=6)
        Button(frame, text="清空", bg="#FFB74D", command=self.clear_canvas).pack(side=LEFT, padx=6)
        Button(frame, text="返回主界面", bg="#6EA8FE", fg="white", command=self.back_to_main).pack(side=LEFT, padx=6)
        Button(frame, text="保存", bg="#6C9EFF", command=self.save_structure).pack(side=LEFT, padx=6)
        Button(frame, text="打开", bg="#6C9EFF", command=self.load_structure).pack(side=LEFT, padx=6)
        self.status_id = None
        
    def draw_instructions(self):
        self.canvas.delete("all")
        self.node_vis.clear()
        self.canvas.create_text(12, 12, anchor="nw", text="AVL 插入演示：展示插入路径并精确动画显示旋转（节点从旧坐标平滑移动到新坐标）", font=("Arial",11))
        self.status_id = self.canvas.create_text(self.canvas_w - 12, 12, anchor="ne", text="", font=("Arial",11,"bold"), fill="darkgreen")

    def update_status(self, txt: str):
        if self.status_id:
            self.canvas.itemconfig(self.status_id, text=txt)
        else:
            self.status_id = self.canvas.create_text(self.canvas_w - 12, 12, anchor="ne", text=txt, font=("Arial",11,"bold"), fill="darkgreen")

    def _draw_connection(self, cx, cy, tx, ty):
        """Draw two-segment arrow from parent center (cx,cy) to child center (tx,ty)."""
        top = cy + self.node_h/2
        bot = ty - self.node_h/2
        midy = (top + bot) / 2
        l1 = self.canvas.create_line(cx, top, cx, midy, width=2)
        l2 = self.canvas.create_line(cx, midy, tx, bot, arrow=LAST, width=2)
        return (l1, l2)

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
        """Draw the given snapshot root onto canvas. Build node_vis mapping keyed by 'val' or 'val#k'."""
        self.canvas.delete("all")
        self.draw_instructions()
        if root is None:
            self.canvas.create_text(self.canvas_w/2, self.canvas_h/2, text="空树", font=("Arial",18), fill="gray")
            return

        pos = self.compute_positions_for_root(root)

        # build inorder_nodes to generate stable duplicate keys and node->key mapping
        inorder_nodes: List[AVLNode] = []
        def inorder_collect(n: Optional[AVLNode]):
            if not n:
                return
            inorder_collect(n.left)
            inorder_nodes.append(n)
            inorder_collect(n.right)
        inorder_collect(root)

        # map node -> key
        node_to_key: Dict[AVLNode, str] = {}
        counts: Dict[str,int] = {}
        for node in inorder_nodes:
            base = str(node.val)
            cnt = counts.get(base, 0)
            counts[base] = cnt + 1
            key = f"{base}#{cnt}" if cnt > 0 else base
            node_to_key[node] = key

        # [FIXED] Step 1: Draw nodes first and initialize node_vis with edge placeholders
        self.node_vis.clear()
        for node, key in node_to_key.items():
            cx, cy = pos[key]
            left, top, right, bottom = cx - self.node_w/2, cy - self.node_h/2, cx + self.node_w/2, cy + self.node_h/2
            rect = self.canvas.create_rectangle(left, top, right, bottom, fill="#F0F8FF", outline="black", width=2)
            x1, x2 = left + 28, left + 92
            self.canvas.create_line(x1, top, x1, bottom, width=1)
            self.canvas.create_line(x2, top, x2, bottom, width=1)
            txt = self.canvas.create_text((x1+x2)/2, cy, text=str(node.val), font=("Arial",12,"bold"))
            self.node_vis[key] = {
                'rect': rect, 
                'text': txt, 
                'cx': cx, 
                'cy': cy, 
                'val': str(node.val),
                'edges': {}  # Placeholder for outgoing edge items
            }

        # [FIXED] Step 2: Draw edges and store their canvas IDs in the parent's node_vis entry
        def setup_edges(n: Optional[AVLNode]):
            if not n:
                return
            parent_key = node_to_key[n]
            parent_cx, parent_cy = pos[parent_key]

            if n.left:
                child_key = node_to_key[n.left]
                child_cx, child_cy = pos[child_key]
                line_ids = self._draw_connection(parent_cx, parent_cy, child_cx, child_cy)
                self.node_vis[parent_key]['edges'][child_key] = line_ids
                setup_edges(n.left)
            
            if n.right:
                child_key = node_to_key[n.right]
                child_cx, child_cy = pos[child_key]
                line_ids = self._draw_connection(parent_cx, parent_cy, child_cx, child_cy)
                self.node_vis[parent_key]['edges'][child_key] = line_ids
                setup_edges(n.right)
                
        setup_edges(root)

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
        left, top, right, bottom = sx - self.node_w/2, sy - self.node_h/2, sx + self.node_w/2, sy + self.node_h/2
        temp_rect = self.canvas.create_rectangle(left, top, right, bottom, fill="#C6F6D5", outline="black", width=2)
        x1 = left + 28
        temp_text = self.canvas.create_text(sx, sy, text=str(val_str), font=("Arial",12,"bold"))

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

    # [NEW] Helper method to redraw edges during animation
    def _redraw_all_edges_during_animation(self):
        """
        Redraws all edges based on the current positions of the nodes on the canvas.
        This is called every frame during an animation.
        """
        for parent_key, parent_vis in self.node_vis.items():
            try:
                # Get parent's current center coordinates from its rectangle
                parent_coords = self.canvas.coords(parent_vis['rect'])
                if not parent_coords or len(parent_coords) < 4: continue
                parent_cx = (parent_coords[0] + parent_coords[2]) / 2
                parent_cy = (parent_coords[1] + parent_coords[3]) / 2

                # Iterate over its outgoing edges
                for child_key, line_ids in parent_vis.get('edges', {}).items():
                    child_vis = self.node_vis.get(child_key)
                    if not child_vis: continue
                    
                    # Get child's current center coordinates
                    child_coords = self.canvas.coords(child_vis['rect'])
                    if not child_coords or len(child_coords) < 4: continue
                    child_cx = (child_coords[0] + child_coords[2]) / 2
                    child_cy = (child_coords[1] + child_coords[3]) / 2
                    
                    # Update the line coordinates using the same logic as _draw_connection
                    l1_id, l2_id = line_ids
                    top = parent_cy + self.node_h / 2
                    bot = child_cy - self.node_h / 2
                    midy = (top + bot) / 2
                    
                    self.canvas.coords(l1_id, parent_cx, top, parent_cx, midy)
                    self.canvas.coords(l2_id, parent_cx, midy, child_cx, bot)
            except TclError:
                # This can happen if a canvas item was unexpectedly deleted. Safe to ignore.
                continue

    def _animate_single_rotation(self, before_root: Optional[AVLNode], after_root: Optional[AVLNode], rotation_info: Dict, on_done):
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

        frames = 30 # Increased for smoother animation
        delay = 20  # Decreased for faster frame rate

        def rect_center_coords(rect_id):
            coords = self.canvas.coords(rect_id)
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
                # compute desired current center (interpolation)
                cur_cx = sx + (tx - sx) * t
                cur_cy = sy + (ty - sy) * t
                try:
                    # get current center to compute delta for move command
                    ccx, ccy = rect_center_coords(rect_id)
                    if (ccx, ccy) == (0,0): continue
                    dx = cur_cx - ccx
                    dy = cur_cy - ccy
                    self.canvas.move(rect_id, dx, dy)
                    self.canvas.move(text_id, dx, dy)
                except Exception:
                    pass

            # [FIXED] Redraw all edges to keep them connected during animation
            self._redraw_all_edges_during_animation()
            
            self.window.after(delay, lambda: frame_step(f+1))
        frame_step(0)

    def _animate_rotations_sequence(self, rotations: List[Dict], snapshots: List[Optional[AVLNode]], insertion_index: int, on_all_done):
        if not rotations:
            on_all_done(); return

        def step(i=0):
            if i >= len(rotations):
                on_all_done()
                return
            before_root = snapshots[1 + i]
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

    def clear_canvas(self):
        if self.animating:
            return
        self.model = AVLModel()
        self.node_vis.clear()
        self.canvas.delete("all")
        self.draw_instructions()
        self.update_status("已清空")

    def back_to_main(self):
        self.window.destroy()

    def _ensure_avl_folder(self) -> str:
        return storage.ensure_save_subdir("avl")

    def save_structure(self):
        root = self.model.root
        default_dir = self._ensure_avl_folder()
        default_name = f"avl_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = filedialog.asksaveasfilename(
            initialdir=default_dir,
            initialfile=default_name,
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="保存 AVL 到文件"
        )
        if not filepath: return
        ok = storage.save_tree_to_file(root, filepath)
        if ok:
            messagebox.showinfo("成功", f"AVL 已保存到：\n{filepath}")
            self.update_status("保存成功")

    def load_structure(self):
        default_dir = self._ensure_avl_folder()
        filepath = filedialog.askopenfilename(
            initialdir=default_dir,
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="从文件加载 AVL"
        )
        if not filepath: return
        tree_dict = storage.load_tree_from_file(filepath)
        from avl.avl_model import AVLNode as AVLNodeClass
        newroot = storage.tree_dict_to_nodes(tree_dict, AVLNodeClass)
        self.model.root = newroot
        self.draw_tree_from_root(clone_tree(self.model.root))
        messagebox.showinfo("成功", f"AVL 已从文件加载并恢复结构：\n{filepath}")
        self.update_status("已经从文件加载并恢复结构")

if __name__ == '__main__':
    w = Tk()
    w.title("AVL 可视化（增强旋转动画）")
    w.geometry("1350x730")
    AVLVisualizer(w)
    w.mainloop()