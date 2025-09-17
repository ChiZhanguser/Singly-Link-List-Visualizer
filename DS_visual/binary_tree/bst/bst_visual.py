# DS_visual/binary_tree/bst_visual.py
from tkinter import *
from tkinter import messagebox
from typing import Dict, Tuple, List, Optional
from binary_tree.bst.bst_model import BSTModel, TreeNode

class BSTVisualizer:
    def __init__(self, root):
        self.window = root
        self.window.config(bg="#F7F9FB")
        self.canvas_width = 1250
        self.canvas_height = 560
        self.canvas = Canvas(self.window, bg="white", width=self.canvas_width, height=self.canvas_height, relief=RAISED, bd=8)
        self.canvas.pack(pady=(10,0))

        # 模型
        self.model = BSTModel()

        # drawing bookkeeping
        self.node_to_rect: Dict[TreeNode, int] = {}
        self.node_items: List[int] = []
        self.status_text_id: Optional[int] = None

        # layout params
        self.node_w = 120
        self.node_h = 44
        self.left_cell_w = 28
        self.center_cell_w = 64
        self.right_cell_w = self.node_w - self.left_cell_w - self.center_cell_w
        self.level_gap = 100
        self.margin_x = 40

        # animation state
        self.animating = False

        # input var
        self.input_var = StringVar()
        self.create_controls()
        self.draw_instructions()

    def create_controls(self):
        frame = Frame(self.window, bg="#F7F9FB")
        frame.pack(pady=8, fill=X)

        Label(frame, text="值输入（单值或逗号批量）:", font=("Arial",12), bg="#F7F9FB").pack(side=LEFT, padx=6)
        entry = Entry(frame, textvariable=self.input_var, width=46, font=("Arial",12))
        entry.pack(side=LEFT, padx=6)
        entry.insert(0, "15,6,23,4,7,71,5")

        Button(frame, text="Insert (直接)", command=self.insert_direct, bg="green", fg="white").pack(side=LEFT, padx=6)
        Button(frame, text="Insert (动画)", command=self.start_insert_animated, bg="#2E8B57", fg="white").pack(side=LEFT, padx=6)
        Button(frame, text="Search (动画)", command=self.start_search_animated, bg="#FFA500").pack(side=LEFT, padx=6)
        Button(frame, text="Delete (动画)", command=self.start_delete_animated, bg="red", fg="white").pack(side=LEFT, padx=6)
        Button(frame, text="清空", command=self.clear_canvas, bg="orange").pack(side=LEFT, padx=6)
        Button(frame, text="返回主界面", command=self.back_to_main, bg="blue", fg="white").pack(side=LEFT, padx=6)

    def draw_instructions(self):
        self.canvas.delete("all")
        self.node_items.clear()
        self.node_to_rect.clear()
        self.canvas.create_text(10, 10, anchor="nw", text="BST：插入 / 查找 / 删除 动态演示。中序位置用于横向布局。", font=("Arial",11))
        if self.status_text_id:
            try:
                self.canvas.delete(self.status_text_id)
            except Exception:
                pass
        self.status_text_id = self.canvas.create_text(self.canvas_width-10, 10, anchor="ne", text="", font=("Arial",12,"bold"), fill="darkgreen")

    def update_status(self, text: str):
        if not self.status_text_id:
            self.status_text_id = self.canvas.create_text(self.canvas_width-10, 10, anchor="ne", text=text, font=("Arial",12,"bold"), fill="darkgreen")
        else:
            self.canvas.itemconfig(self.status_text_id, text=text)

    # ---------- layout: compute inorder positions ----------
    def compute_positions(self) -> Dict[TreeNode, Tuple[float,float]]:
        pos: Dict[TreeNode, Tuple[float,float]] = {}
        nodes_inorder: List[TreeNode] = []
        depths: Dict[TreeNode, int] = {}

        def inorder(n: Optional[TreeNode], d: int):
            if n is None:
                return
            inorder(n.left, d+1)
            nodes_inorder.append(n)
            depths[n] = d
            inorder(n.right, d+1)

        inorder(self.model.root, 0)
        n = len(nodes_inorder)
        if n == 0:
            return pos
        width = self.canvas_width - 2*self.margin_x
        # avoid division by zero
        for i, node in enumerate(nodes_inorder):
            if n == 1:
                x = self.canvas_width / 2
            else:
                x = self.margin_x + i * (width / (n-1))
            y = 60 + depths[node] * self.level_gap
            pos[node] = (x, y)
        return pos

    # ---------- drawing ----------
    def redraw(self):
        self.canvas.delete("all")
        self.node_items.clear()
        self.node_to_rect.clear()
        self.draw_instructions()
        if self.model.root is None:
            self.canvas.create_text(self.canvas_width/2, self.canvas_height/2, text="空树", font=("Arial",18), fill="gray")
            return
        pos = self.compute_positions()
        # draw edges first for nicer visuals
        for node, (cx, cy) in pos.items():
            if node.left and node.left in pos:
                lx, ly = pos[node.left]
                self._draw_connection(cx, cy, lx, ly)
            if node.right and node.right in pos:
                rx, ry = pos[node.right]
                self._draw_connection(cx, cy, rx, ry)
        # draw nodes
        for node, (cx, cy) in pos.items():
            self._draw_node(node, cx, cy)

    def _draw_connection(self, cx, cy, tx, ty):
        # draw two-stage line
        top = cy + self.node_h/2
        bot = ty - self.node_h/2
        mid_y = (top + bot) / 2
        l1 = self.canvas.create_line(cx, top, cx, mid_y, width=2)
        l2 = self.canvas.create_line(cx, mid_y, tx, bot, arrow=LAST, width=2)
        self.node_items += [l1, l2]

    def _draw_node(self, node: TreeNode, cx: float, cy: float):
        left = cx - self.node_w/2
        top = cy - self.node_h/2
        right = cx + self.node_w/2
        bottom = cy + self.node_h/2
        rect = self.canvas.create_rectangle(left, top, right, bottom, fill="#F0F8FF", outline="black", width=2)
        self.node_to_rect[node] = rect
        self.node_items.append(rect)
        # vertical splits
        x1 = left + self.left_cell_w
        x2 = x1 + self.center_cell_w
        v1 = self.canvas.create_line(x1, top, x1, bottom, width=1)
        v2 = self.canvas.create_line(x2, top, x2, bottom, width=1)
        self.node_items += [v1, v2]
        self.canvas.create_text((x1+x2)/2, (top+bottom)/2, text=str(node.val), font=("Arial",12,"bold"))

    # ---------- user actions ----------
    def insert_direct(self):
        text = self.input_var.get().strip()
        if not text:
            messagebox.showinfo("提示", "请输入值或逗号分隔的值")
            return
        items = [s.strip() for s in text.split(",") if s.strip()!=""]
        for v in items:
            self.model.insert(v)
        self.redraw()
        self.update_status(f"已插入 {len(items)} 个节点")

    # ---------- animated insert seq ----------
    def start_insert_animated(self):
        if self.animating:
            return
        text = self.input_var.get().strip()
        if not text:
            messagebox.showinfo("提示", "请输入值或逗号分隔的值")
            return
        items = [s.strip() for s in text.split(",") if s.strip()!=""]
        if not items:
            return
        self.animating = True
        self._insert_seq(items, 0)

    def _insert_seq(self, items: List[str], idx: int):
        if idx >= len(items):
            self.animating = False
            self.update_status("插入完成")
            return
        val = items[idx]
        # stepwise highlight path for this insert
        self._animate_search_path_for_insert(val, lambda: self._finalize_insert_and_continue(val, items, idx))

    def _finalize_insert_and_continue(self, val, items, idx):
        # create the node in model (so compute_positions will include it)
        new_node = self.model.insert(val)
        # animate fly-in to computed position
        pos_map = self.compute_positions()
        if new_node not in pos_map:
            # fallback - redraw and continue
            self.redraw()
            self.window.after(300, lambda: self._insert_seq(items, idx+1))
            return
        tx, ty = pos_map[new_node]
        # create temp visual at top
        sx, sy = self.canvas_width/2, 20
        left = sx - self.node_w/2; top = sy - self.node_h/2; right = sx + self.node_w/2; bottom = sy + self.node_h/2
        temp_rect = self.canvas.create_rectangle(left, top, right, bottom, fill="#C6F6D5", outline="black", width=2)
        x1 = left + self.left_cell_w; x2 = x1 + self.center_cell_w
        temp_text = self.canvas.create_text((x1+x2)/2, (top+bottom)/2, text=str(val), font=("Arial",12,"bold"))

        steps = 30
        dx = (tx - sx)/steps
        dy = (ty - sy)/steps
        delay = 12

        def step(i=0):
            if i < steps:
                self.canvas.move(temp_rect, dx, dy)
                self.canvas.move(temp_text, dx, dy)
                self.window.after(delay, lambda: step(i+1))
            else:
                try:
                    self.canvas.delete(temp_rect)
                    self.canvas.delete(temp_text)
                except Exception:
                    pass
                # redraw full tree where new node exists
                self.redraw()
                # briefly highlight new node
                if new_node in self.node_to_rect:
                    rid = self.node_to_rect[new_node]
                    self.canvas.itemconfig(rid, fill="lightgreen")
                    def unhigh():
                        try:
                            self.canvas.itemconfig(rid, fill="#F0F8FF")
                        except Exception:
                            pass
                        # continue
                        self.window.after(150, lambda: self._insert_seq(items, idx+1))
                    self.window.after(300, unhigh)
                else:
                    self.window.after(300, lambda: self._insert_seq(items, idx+1))

        step()

    # ---------- animated search (used for insert path highlight and user search) ----------
    def _animate_search_path_for_insert(self, val: str, on_complete):
        """
        模拟插入时的比较路径：每个访问节点高亮（黄色），根据比较走 left/right。
        on_complete 在访问到插入点（节点为 None 的位置）时调用（此时模型尚未插入节点）
        """
        # simulate walk without modifying model: traverse until we reach None where insert would happen
        path_nodes = []
        cur = self.model.root
        if cur is None:
            # inserting as root
            self.redraw()
            self.update_status(f"准备插入 val={val} 到 root (index=0)")
            # short delay then complete
            self.window.after(400, on_complete)
            return

        steps = []
        while cur:
            steps.append(cur)
            if str(val) == str(cur.val):
                # treat as go-right (or consider duplicates as right)
                cur = cur.right
            elif str(val) < str(cur.val):
                cur = cur.left
            else:
                cur = cur.right
        # now steps is list of visited nodes
        self._play_highlight_sequence(steps, f"插入 val={val}", on_complete)

    def _play_highlight_sequence(self, nodes: List[TreeNode], label_prefix: str, on_complete):
        if not nodes:
            self.window.after(200, on_complete)
            return
        i = 0
        def step():
            nonlocal i
            if i >= len(nodes):
                # done
                on_complete()
                return
            node = nodes[i]
            # redraw tree and highlight this node
            self.redraw()
            if node in self.node_to_rect:
                rid = self.node_to_rect[node]
                self.canvas.itemconfig(rid, fill="yellow")
            self.update_status(f"{label_prefix} 访问: {node.val} (step {i})")
            i += 1
            self.window.after(520, step)
        step()

    # ---------- animated search by user ----------
    def start_search_animated(self):
        if self.animating:
            return
        val = self.input_var.get().strip()
        if not val:
            messagebox.showinfo("提示", "请输入要查找的值")
            return
        self.animating = True
        # use search path
        path_nodes = []
        cur = self.model.root
        while cur:
            path_nodes.append(cur)
            if str(val) == str(cur.val):
                break
            elif str(val) < str(cur.val):
                cur = cur.left
            else:
                cur = cur.right
        # play
        found = (path_nodes and str(path_nodes[-1].val) == str(val))
        i = 0
        def step():
            nonlocal i
            if i >= len(path_nodes):
                self.animating = False
                if found:
                    self.update_status(f"查找完成: 找到 {val}")
                    # highlight found node red briefly
                    node = path_nodes[-1]
                    self.redraw()
                    if node in self.node_to_rect:
                        rid = self.node_to_rect[node]
                        self.canvas.itemconfig(rid, fill="red")
                        self.window.after(600, lambda: self.canvas.itemconfig(rid, fill="#F0F8FF"))
                else:
                    self.update_status(f"查找完成: 未找到 {val}")
                return
            node = path_nodes[i]
            self.redraw()
            if node in self.node_to_rect:
                rid = self.node_to_rect[node]
                self.canvas.itemconfig(rid, fill="yellow")
            self.update_status(f"Search: 比较到 {node.val} (step {i})")
            i += 1
            self.window.after(520, step)
        step()

    # ---------- animated delete ----------
    def start_delete_animated(self):
        if self.animating:
            return
        val = self.input_var.get().strip()
        if not val:
            messagebox.showinfo("提示", "请输入要删除的值")
            return
        # find path first (visualize)
        self.animating = True
        path_nodes = []
        cur = self.model.root
        while cur:
            path_nodes.append(cur)
            if str(val) == str(cur.val):
                break
            elif str(val) < str(cur.val):
                cur = cur.left
            else:
                cur = cur.right

        found = (path_nodes and str(path_nodes[-1].val) == str(val))
        i = 0
        def step():
            nonlocal i
            if i >= len(path_nodes):
                # finished scanning path
                if not found:
                    self.animating = False
                    self.update_status(f"删除：未找到 {val}")
                    return
                # now animate deletion process (visual guidance)
                self._animate_deletion_process(val)
                return
            node = path_nodes[i]
            self.redraw()
            if node in self.node_to_rect:
                self.canvas.itemconfig(self.node_to_rect[node], fill="yellow")
            self.update_status(f"删除：比较到 {node.val} (step {i})")
            i_plus = i+1
            i_next = lambda: self.window.after(420, step)
            i += 1
            self.window.after(420, step)
        step()

    def _animate_deletion_process(self, val):
        # perform deletion but visualize key steps:
        # 1) find node (already highlighted), 2) if two children -> find successor & highlight, animate swap, then remove successor; otherwise show transplant
        node, path = self.model.search_with_path(val)
        if node is None:
            self.animating = False
            self.update_status(f"删除失败：未找到 {val}")
            return
        # highlight to show deleting node
        self.redraw()
        if node in self.node_to_rect:
            self.canvas.itemconfig(self.node_to_rect[node], fill="red")
        self.update_status(f"准备删除 {val}")
        # Delay then handle cases
        def after_highlight():
            # case analysis
            if node.left is None and node.right is None:
                # leaf
                self.model.delete(val)
                self.redraw()
                self.update_status(f"删除叶子节点 {val}")
                self.animating = False
            elif node.left is None or node.right is None:
                # one child
                # show transplant visually: highlight child then transplant
                child = node.left if node.left else node.right
                self.redraw()
                if child in self.node_to_rect:
                    self.canvas.itemconfig(self.node_to_rect[child], fill="yellow")
                self.update_status(f"删除：节点有一个子节点，进行替换")
                def do_transplant():
                    self.model.delete(val)
                    self.redraw()
                    self.update_status(f"已删除 {val} (单子节点替换)")
                    self.animating = False
                self.window.after(600, do_transplant)
            else:
                # two children: find successor
                succ = self.model.find_min(node.right)
                # highlight successor path
                self.redraw()
                if succ in self.node_to_rect:
                    self.canvas.itemconfig(self.node_to_rect[succ], fill="orange")
                self.update_status(f"删除：找到后继 {succ.val}，将其值替换到目标节点")
                def swap_and_delete():
                    # swap values in model (visual will reflect after redraw)
                    node.val, succ.val = succ.val, node.val
                    self.redraw()
                    # highlight swapped node (the node now contains successor value)
                    if node in self.node_to_rect:
                        self.canvas.itemconfig(self.node_to_rect[node], fill="lightgreen")
                    self.update_status(f"已交换值，接下来删除后继节点 {val}（其已移至 succ 位置）")
                    # then delete the successor (which has at most one child)
                    def final_del():
                        # successor's value equals original node's value? careful: we swapped
                        # delete by value of original target (which is now in succ) — simpler: delete succ.val (the old node.val)
                        self.model.delete(val)
                        self.redraw()
                        self.update_status(f"删除完成（两子节点情况）")
                        self.animating = False
                    self.window.after(500, final_del)
                self.window.after(700, swap_and_delete)
        self.window.after(500, after_highlight)

    # ---------- clear & back ----------
    def clear_canvas(self):
        if self.animating:
            return
        self.model = BSTModel()
        self.redraw()
        self.update_status("已清空")

    def back_to_main(self):
        if self.animating:
            messagebox.showinfo("提示", "正在动画，不能返回")
            return
        self.window.destroy()
        from main_interface import MainInterface
        main_window = Tk()
        app = MainInterface(main_window)
        main_window.mainloop()

if __name__ == '__main__':
    w = Tk()
    w.title("BST 可视化")
    w.geometry("1350x730")
    BSTVisualizer(w)
    w.mainloop()
