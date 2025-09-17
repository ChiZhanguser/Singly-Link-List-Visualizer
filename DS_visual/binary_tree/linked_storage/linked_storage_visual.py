# DS_visual/binary_tree/binary_tree_visual.py
from tkinter import *
from tkinter import messagebox
from binary_tree.linked_storage.linked_strorage_model import BinaryTreeModel, TreeNode
from typing import Dict, Tuple, List, Optional

class BinaryTreeVisualizer:
    def __init__(self, root):
        self.window = root
        self.window.config(bg="#F7F9FB")
        self.canvas_width = 1250
        self.canvas_height = 520
        self.canvas = Canvas(self.window, bg="white", width=self.canvas_width, height=self.canvas_height, relief=RAISED, bd=8)
        self.canvas.pack(pady=(10,0))

        # 当前树根
        self.root_node: Optional[TreeNode] = None

        # canvas 元素记录
        self.node_items: List[int] = []
        # 节点->矩形 id 映射（用于高亮父节点）
        self.node_to_rect: Dict[TreeNode, int] = {}

        # 布局参数
        self.node_w = 120
        self.node_h = 44
        self.left_cell_w = 28
        self.center_cell_w = 64
        self.right_cell_w = self.node_w - self.left_cell_w - self.center_cell_w
        self.level_gap = 100

        # 批量构建/动画状态
        self.input_var = StringVar()
        self.batch_queue: List[str] = []
        self.animating = False

        # 右上状态文本 id
        self.status_text_id: Optional[int] = None

        self.create_controls()
        self.draw_instructions()

    def create_controls(self):
        frame = Frame(self.window, bg="#F7F9FB")
        frame.pack(pady=8, fill=X)

        label = Label(frame, text="按层序输入节点（逗号分隔，# 表示空）:", font=("Arial", 12), bg="#F7F9FB")
        label.pack(side=LEFT, padx=6)

        entry = Entry(frame, textvariable=self.input_var, width=60, font=("Arial", 12))
        entry.pack(side=LEFT, padx=6)
        entry.insert(0, "1,2,3,#,4,#,5")

        build_btn = Button(frame, text="一步构建(直接显示)", font=("Arial", 12), bg="green", fg="white", command=self.build_tree_from_input)
        build_btn.pack(side=LEFT, padx=6)

        animate_btn = Button(frame, text="逐步动画构建", font=("Arial", 12), bg="#2E8B57", fg="white", command=self.start_animated_build)
        animate_btn.pack(side=LEFT, padx=6)

        clear_btn = Button(frame, text="清空", font=("Arial", 12), bg="orange", fg="white", command=self.clear_canvas)
        clear_btn.pack(side=LEFT, padx=6)

        back_btn = Button(frame, text="返回主界面", font=("Arial", 12), bg="blue", fg="white", command=self.back_to_main)
        back_btn.pack(side=LEFT, padx=6)

    def draw_instructions(self):
        self.canvas.create_text(10, 10, text="显示规则：每个节点分为 3 格 => [left | value | right]。左右指针连到子节点或指向 NULL。示例: 1,2,3,#,4,#,5", anchor="nw", font=("Arial", 11))
        # 初始化右上状态文本
        if self.status_text_id:
            try:
                self.canvas.delete(self.status_text_id)
            except Exception:
                pass
        self.status_text_id = self.canvas.create_text(self.canvas_width - 10, 10, text="", anchor="ne", font=("Arial", 12, "bold"), fill="darkgreen")

    def update_status(self, text: str):
        if not self.status_text_id:
            self.status_text_id = self.canvas.create_text(self.canvas_width - 10, 10, text=text, anchor="ne", font=("Arial", 12, "bold"), fill="darkgreen")
        else:
            self.canvas.itemconfig(self.status_text_id, text=text)

    def build_tree_from_input(self):
        text = self.input_var.get().strip()
        if not text:
            messagebox.showinfo("提示", "请输入层序序列，例如：1,2,3,#,4,#,5")
            return
        parts = [p.strip() for p in text.split(",")]
        root, _ = BinaryTreeModel.build_from_level_order(parts)
        self.root_node = root
        self.redraw_tree()

    def clear_canvas(self):
        if self.animating:
            return
        self.canvas.delete("all")
        self.node_items.clear()
        self.node_to_rect.clear()
        self.root_node = None
        self.draw_instructions()
        self.update_status("")

    def redraw_tree(self):
        """
        清空并按 self.root_node 绘制整棵树；同时构建 node->rect 的映射（用于高亮）
        """
        self.canvas.delete("all")
        self.node_items.clear()
        self.node_to_rect.clear()
        self.draw_instructions()
        if not self.root_node:
            self.canvas.create_text(self.canvas_width/2, self.canvas_height/2, text="空树", font=("Arial", 18), fill="gray")
            return
        initial_offset = self.canvas_width / 4
        start_y = 60
        self._draw_node(self.root_node, self.canvas_width/2, start_y, initial_offset)

    # ------------- 布局（仅计算坐标） -------------
    def compute_positions(self, root: Optional[TreeNode]) -> Dict[TreeNode, Tuple[float,float]]:
        pos: Dict[TreeNode, Tuple[float,float]] = {}
        if not root:
            return pos
        initial_offset = self.canvas_width / 4
        start_y = 60

        def _rec(node: TreeNode, cx: float, cy: float, offset: float):
            pos[node] = (cx, cy)    
            child_y = cy + self.level_gap
            child_offset = max(offset/2, 20)
            if node.left:
                _rec(node.left, cx - offset, child_y, child_offset)
            if node.right:
                _rec(node.right, cx + offset, child_y, child_offset)
        _rec(root, self.canvas_width/2, start_y, initial_offset)
        return pos

    # ------------- 动画插入（含父节点高亮与状态显示） -------------
    def start_animated_build(self):
        if self.animating:
            return
        text = self.input_var.get().strip()
        if not text:
            messagebox.showinfo("提示", "请输入层序序列，例如：1,2,3,#,4,#,5")
            return
        parts = [p.strip() for p in text.split(",")]
        if not parts:
            return
        max_nodes = 255
        if len(parts) > max_nodes:
            if not messagebox.askyesno("警告", f"输入节点过多（{len(parts)}），可能导致绘制重叠或卡顿，是否继续？"):
                return
        self.batch_queue = parts
        self.animating = True
        self._animated_step(0)

    def _animated_step(self, idx: int):
        # 结束条件
        if idx >= len(self.batch_queue):
            self.animating = False
            self.update_status("构建完成")
            return

        # parts 包含当前要插入的项
        parts_sofar = self.batch_queue[:idx+1]
        # prev_parts 是插入前已有的项（用于在插入前显示当前树并高亮父节点）
        prev_parts = self.batch_queue[:idx]

        # 构建 prev tree（用于高亮父节点）
        prev_root, prev_node_list = BinaryTreeModel.build_from_level_order(prev_parts)
        # parent index 按层序数组规则
        parent_node = None
        if idx > 0:
            parent_idx = (idx - 1) // 2
            if parent_idx < len(prev_node_list):
                parent_node = prev_node_list[parent_idx]

        # 显示当前树（未插入当前项），并高亮父节点（如果存在）
        self.root_node = prev_root
        self.redraw_tree()
        self.update_status(f"准备插入： val = {self.batch_queue[idx]}    插入到 index = {idx}")

        # 高亮父节点（如果存在并在当前绘制映射中）
        if parent_node and parent_node in self.node_to_rect:
            rect_id = self.node_to_rect[parent_node]
            try:
                self.canvas.itemconfig(rect_id, fill="yellow")
            except Exception:
                pass

        # 如果当前项为 '#'（空），则直接应用并重绘（不飞入）
        if parts_sofar[-1] == "#" or parts_sofar[-1] == "" :
            # 直接把带当前占位的树作为当前树并重绘（会显示 NULL）
            temp_root, _ = BinaryTreeModel.build_from_level_order(parts_sofar)
            # 保持短暂停留以便用户看见高亮父节点和状态
            def after_delay():
                self.root_node = temp_root
                self.redraw_tree()
                # 继续下一步
                self.window.after(350, lambda: self._animated_step(idx+1))
            self.window.after(500, after_delay)
            return

        # 构建含当前节点的临时树以获得目标位置
        temp_root, node_list = BinaryTreeModel.build_from_level_order(parts_sofar)
        target_item = node_list[-1] if node_list else None
        # 计算目标坐标
        pos_map = self.compute_positions(temp_root)
        if target_item not in pos_map:
            # 若找不到位置，则直接应用并继续
            self.root_node = temp_root
            self.redraw_tree()
            self.window.after(300, lambda: self._animated_step(idx+1))
            return
        target_cx, target_cy = pos_map[target_item]

        # 在画布顶部创建临时节点（视觉与真实节点一致）
        start_cx = self.canvas_width / 2
        start_cy = 20
        left = start_cx - self.node_w/2
        top = start_cy - self.node_h/2
        right = start_cx + self.node_w/2
        bottom = start_cy + self.node_h/2

        temp_rect = self.canvas.create_rectangle(left, top, right, bottom, fill="#C6F6D5", outline="black", width=2)
        x1 = left + self.left_cell_w
        x2 = x1 + self.center_cell_w
        temp_text = self.canvas.create_text((x1 + x2)/2, (top + bottom)/2, text=str(target_item.val), font=("Arial", 12, "bold"))

        # 动画移动到目标位置
        steps = 30
        dx = (target_cx - start_cx) / steps
        dy = (target_cy - start_cy) / steps
        delay = 12

        def step(i=0):
            if i < steps:
                self.canvas.move(temp_rect, dx, dy)
                self.canvas.move(temp_text, dx, dy)
                self.window.after(delay, lambda: step(i+1))
            else:
                # 删除临时图元，设置并重绘完整树（含新节点）
                try:
                    self.canvas.delete(temp_rect)
                    self.canvas.delete(temp_text)
                except Exception:
                    pass
                self.root_node = temp_root
                self.redraw_tree()
                # 高亮父节点在新的绘制中继续显示一段时间（若存在）
                if idx > 0:
                    parent_idx = (idx - 1) // 2
                    # 通过 node_list 找父节点实例（注意：新的树用的是 temp_root 的节点）
                    if parent_idx < len(node_list):
                        new_parent = node_list[parent_idx]
                        if new_parent and new_parent in self.node_to_rect:
                            try:
                                self.canvas.itemconfig(self.node_to_rect[new_parent], fill="yellow")
                            except Exception:
                                pass
                # 等短时间后继续下一步
                self.window.after(400, lambda: self._animated_step(idx+1))

        step()

    # ------------- 绘制单节点（同时记录 node->rect） -------------
    def _draw_node(self, node: TreeNode, cx: float, cy: float, offset: float):
        left = cx - self.node_w/2
        top = cy - self.node_h/2
        right = cx + self.node_w/2
        bottom = cy + self.node_h/2

        rect = self.canvas.create_rectangle(left, top, right, bottom, fill="#F0F8FF", outline="black", width=2)
        # 记录映射（TreeNode -> rect id）
        self.node_to_rect[node] = rect
        self.node_items.append(rect)

        # 分割竖线
        x1 = left + self.left_cell_w
        x2 = x1 + self.center_cell_w
        v1 = self.canvas.create_line(x1, top, x1, bottom, width=1)
        v2 = self.canvas.create_line(x2, top, x2, bottom, width=1)
        self.node_items += [v1, v2]

        # 中间值
        self.canvas.create_text((x1 + x2)/2, (top + bottom)/2, text=str(node.val), font=("Arial", 12, "bold"))

        left_center_x = left + self.left_cell_w/2
        right_center_x = x2 + self.right_cell_w/2

        child_y = cy + self.level_gap
        child_offset = max(offset/2, 20)

        # 左子节点或 NULL
        if node.left:
            child_x = cx - offset
            self._draw_line_from_cell_to_child(left_center_x, bottom, child_x, child_y - self.node_h/2)
            self._draw_node(node.left, child_x, child_y, child_offset)
        else:
            null_x = cx - offset
            null_y = child_y
            rect_null = self.canvas.create_rectangle(null_x - 28, null_y - 14, null_x + 28, null_y + 14, fill="#FFF0F0", outline="red")
            text_null = self.canvas.create_text(null_x, null_y, text="NULL", font=("Arial", 9, "bold"), fill="red")
            self.node_items += [rect_null, text_null]
            self._draw_line_from_cell_to_child(left_center_x, bottom, null_x, null_y - 14)

        # 右子节点或 NULL
        if node.right:
            child_x = cx + offset
            self._draw_line_from_cell_to_child(right_center_x, bottom, child_x, child_y - self.node_h/2)
            self._draw_node(node.right, child_x, child_y, child_offset)
        else:
            null_x = cx + offset
            null_y = child_y
            rect_null = self.canvas.create_rectangle(null_x - 28, null_y - 14, null_x + 28, null_y + 14, fill="#FFF0F0", outline="red")
            text_null = self.canvas.create_text(null_x, null_y, text="NULL", font=("Arial", 9, "bold"), fill="red")
            self.node_items += [rect_null, text_null]
            self._draw_line_from_cell_to_child(right_center_x, bottom, null_x, null_y - 14)

    def _draw_line_from_cell_to_child(self, sx, sy, ex, ey):
        mid_y = sy + 10
        line1 = self.canvas.create_line(sx, sy, sx, mid_y, width=2)
        line2 = self.canvas.create_line(sx, mid_y, ex, ey, arrow=LAST, width=2)
        self.node_items += [line1, line2]

    def back_to_main(self):
        if self.animating:
            messagebox.showinfo("提示", "正在动画构建，无法返回")
            return
        self.window.destroy()
        from main_interface import MainInterface
        main_window = Tk()
        app = MainInterface(main_window)
        main_window.mainloop()

if __name__ == '__main__':
    window = Tk()
    window.title("二叉树可视化")
    window.geometry("1350x730")
    window.maxsize(1350, 730)
    window.minsize(1350, 730)
    BinaryTreeVisualizer(window)
    window.mainloop()