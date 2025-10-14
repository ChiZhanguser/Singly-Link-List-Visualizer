from tkinter import *
from tkinter import messagebox
from tkinter import Toplevel, filedialog
from typing import Dict, Tuple, List, Optional
from binary_tree.bst.bst_model import BSTModel, TreeNode
import storage as storage
import json
from datetime import datetime
import os
from DSL_utils import process_command
from binary_tree.bst.bst_ui import draw_instructions, create_controls

class BSTVisualizer:
    def __init__(self, root):
        self.window = root
        self.window.config(bg="#F7F9FB")
        self.canvas_width = 1250
        self.canvas_height = 560
        self.canvas = Canvas(self.window, bg="white", width=self.canvas_width, height=self.canvas_height, relief=RAISED, bd=8)
        self.canvas.pack(pady=(10,0))
        self.dsl_var = StringVar()
        self.model = BSTModel()
        self.node_to_rect: Dict[TreeNode, int] = {}
        self.node_items: List[int] = []
        self.status_text_id: Optional[int] = None

        # 布局参数
        self.node_w = 120
        self.node_h = 44
        self.left_cell_w = 28
        self.center_cell_w = 64
        self.right_cell_w = self.node_w - self.left_cell_w - self.center_cell_w
        self.level_gap = 100
        self.margin_x = 40

        # 是否正在执行动画
        self.animating = False

        # 输入框
        self.input_var = StringVar()
        create_controls(self)
        draw_instructions(self)
    def process_dsl(self, event=None):
        text = (self.dsl_var.get() or "").strip()
        if not text:
            return
        if getattr(self, "animating", False):
            messagebox.showinfo("提示", "当前正在动画，请稍后执行 DSL 命令")
            return
        process_command(self,text)
        self.dsl_var.set("")
    
    def update_status(self, text: str):
        if not self.status_text_id:
            self.status_text_id = self.canvas.create_text(self.canvas_width-10, 10, anchor="ne", text=text, font=("Arial",12,"bold"), fill="darkgreen")
        else:
            self.canvas.itemconfig(self.status_text_id, text=text)
    def _ensure_tree_folder(self) -> str:
        if hasattr(storage, "ensure_save_subdir"):
            return storage.ensure_save_subdir("bst")
        base_dir = os.path.dirname(os.path.abspath(storage.__file__))
        default_dir = os.path.join(base_dir, "save", "bst")
        os.makedirs(default_dir, exist_ok=True)
        return default_dir

    def save_tree(self):
        default_dir = self._ensure_tree_folder()
        default_name = f"bst_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = filedialog.asksaveasfilename(
            initialdir=default_dir,
            initialfile=default_name,
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="保存树到文件"
        )
        tree_dict = storage.tree_to_dict(self.model.root)
        
        metadata = {
            "saved_at": datetime.now().isoformat(),
            "node_count": len(tree_dict.get("nodes", [])) if isinstance(tree_dict, dict) else 0
        }
        payload = {"type": "tree", "tree": tree_dict, "metadata": metadata}
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        messagebox.showinfo("成功", f"二叉搜索树已保存到：\n{filepath}")
        self.update_status("保存成功")

    def load_tree(self):
        default_dir = self._ensure_tree_folder()
        filepath = filedialog.askopenfilename(
            initialdir=default_dir,
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="从文件加载二叉树"
        )
        with open(filepath, "r", encoding="utf-8") as f:
            obj = json.load(f)
        tree_dict = obj.get("tree", {})
        if hasattr(storage, "tree_dict_to_nodes"):
            new_root = storage.tree_dict_to_nodes(tree_dict, TreeNode)
            self.model.root = new_root
            self.redraw()
            messagebox.showinfo("成功", "二叉树已成功加载并恢复")
            self.update_status("加载成功")
            return

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
        for i, node in enumerate(nodes_inorder):
            if n == 1:
                x = self.canvas_width / 2
            else:
                x = self.margin_x + i * (width / (n-1))
            y = 60 + depths[node] * self.level_gap
            pos[node] = (x, y)
        return pos

    def redraw(self):
        self.canvas.delete("all")
        self.node_items.clear()
        self.node_to_rect.clear()
        draw_instructions(self)
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
    def parse_value(self, s: str):
        s = s.strip()
        try:
            return int(s)
        except Exception:
            try:
                return float(s)
            except Exception:
                return s

    def insert_direct(self):
        text = self.input_var.get().strip()
        if not text:
            messagebox.showinfo("提示", "请输入值或逗号分隔的值")
            return
        # 先用 s.strip() 过滤空白，再 parse_value，不要在 parse_value 返回值上调用 .strip()
        items = [self.parse_value(s) for s in text.split(",") if s.strip() != ""]
        for v in items:
            self.model.insert(v)
        self.redraw()
        self.update_status(f"已插入 {len(items)} 个节点")


    def start_insert_animated(self):
        if self.animating:
            return
        text = self.input_var.get().strip()
        if not text:
            messagebox.showinfo("提示", "请输入值或逗号分隔的值")
            return  
        items = [self.parse_value(s) for s in text.split(",") if s.strip() != ""]
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
        self._animate_search_path_for_insert(val, lambda: self._finalize_insert_and_continue(val, items, idx))

    def _finalize_insert_and_continue(self, val, items, idx):
        new_node = self.model.insert(val)
        pos_map = self.compute_positions()
        if new_node not in pos_map:
            self.redraw()
            self.window.after(300, lambda: self._insert_seq(items, idx+1))
            return
        tx, ty = pos_map[new_node]
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

    def _animate_search_path_for_insert(self, val: str, on_complete):
        path_nodes = []
        cur = self.model.root
        if cur is None:
            self.redraw()
            self.update_status(f"准备插入 val={val} 到 root (index=0)")
            self.window.after(400, on_complete)
            return

        steps = []
        while cur:
            steps.append(cur)
            cmp = self.model.compare_values(val, cur.val)
            if cmp == 0:
                cur = cur.right   
            elif cmp < 0:
                cur = cur.left
            else:
                cur = cur.right
            # if str(val) == str(cur.val):
            #     cur = cur.right
            # elif str(val) < str(cur.val):
            #     cur = cur.left
            # else:
            #     cur = cur.right
        self._play_highlight_sequence(steps, f"插入 val={val}", on_complete)

    def _play_highlight_sequence(self, nodes: List[TreeNode], label_prefix: str, on_complete):
        if not nodes:
            self.window.after(200, on_complete)
            return
        i = 0
        def step():
            nonlocal i
            if i >= len(nodes):
                on_complete()
                return
            node = nodes[i]
            self.redraw()
            if node in self.node_to_rect:
                rid = self.node_to_rect[node]
                self.canvas.itemconfig(rid, fill="yellow")
            self.update_status(f"{label_prefix} 访问: {node.val} (step {i})")
            i += 1
            self.window.after(520, step)
        step()

 
    def start_search_animated(self):
        if self.animating:
            return
        raw = self.input_var.get().strip()
        if not raw:
            messagebox.showinfo("提示", "请输入要查找的值")
            return
        val = self.parse_value(raw)
        self.animating = True
        path_nodes = []
        cur = self.model.root
        while cur:
            path_nodes.append(cur)
            cmp = self.model.compare_values(val, cur.val)
            if cmp == 0:
                break
            elif cmp < 0:
                cur = cur.left
            else:
                cur = cur.right
        found = (path_nodes and self.model.compare_values(val, path_nodes[-1].val) == 0)
        i = 0
        def step():
            nonlocal i
            if i >= len(path_nodes):
                self.animating = False
                if found:
                    self.update_status(f"查找完成: 找到 {val}")
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


    def start_delete_animated(self):
        if self.animating:
            return
        raw = self.input_var.get().strip()
        if not raw:
            messagebox.showinfo("提示", "请输入要删除的值")
            return
        val = self.parse_value(raw)
        self.animating = True
        path_nodes = []
        cur = self.model.root
        while cur:
            path_nodes.append(cur)
            cmp = self.model.compare_values(val, cur.val)
            if cmp == 0:
                break
            elif cmp < 0:
                cur = cur.left
            else:
                cur = cur.right

        found = (path_nodes and self.model.compare_values(val, path_nodes[-1].val) == 0)
        i = 0
        def step():
            nonlocal i
            if i >= len(path_nodes):
                if not found:
                    self.animating = False
                    self.update_status(f"删除：未找到 {val}")
                    return
                self._animate_deletion_process(val)
                return
            node = path_nodes[i]
            self.redraw()
            if node in self.node_to_rect:
                self.canvas.itemconfig(self.node_to_rect[node], fill="yellow")
            self.update_status(f"删除：比较到 {node.val} (step {i})")
            i += 1
            self.window.after(420, step)
        step()


    def _animate_deletion_process(self, val):
        node, path = self.model.search_with_path(val)
        if node is None:
            self.animating = False
            self.update_status(f"删除失败：未找到 {val}")
            return
        self.redraw()
        if node in self.node_to_rect:
            self.canvas.itemconfig(self.node_to_rect[node], fill="red")
        self.update_status(f"准备删除 {val}")
        def after_highlight():
            if node.left is None and node.right is None:
                self.model.delete(val)
                self.redraw()
                self.update_status(f"删除叶子节点 {val}")
                self.animating = False
            elif node.left is None or node.right is None:
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
                succ = self.model.find_min(node.right)
                self.redraw()
                if succ in self.node_to_rect:
                    self.canvas.itemconfig(self.node_to_rect[succ], fill="orange")
                self.update_status(f"删除：找到后继 {succ.val}，将其值替换到目标节点")
                def swap_and_delete():
                    node.val, succ.val = succ.val, node.val
                    self.redraw()
                    if node in self.node_to_rect:
                        self.canvas.itemconfig(self.node_to_rect[node], fill="lightgreen")
                    self.update_status(f"已交换值，接下来删除后继节点 {val}（其已移至 succ 位置）")
                    def final_del():
                        self.model.delete_node(succ)  
                        self.redraw()
                        self.update_status(f"删除完成（两子节点情况）")
                        self.animating = False
                    self.window.after(500, final_del)
                self.window.after(700, swap_and_delete)
        self.window.after(500, after_highlight) 

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
        
if __name__ == '__main__':
    w = Tk()
    w.title("BST 可视化")
    w.geometry("1350x730")
    BSTVisualizer(w)
    w.mainloop()
