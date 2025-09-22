# DS_visual/binary_tree/binary_tree_visual.py
from tkinter import *
from tkinter import messagebox
from binary_tree.linked_storage.linked_storage_model import BinaryTreeModel, TreeNode
from typing import Dict, Tuple, List, Optional
import math

class BinaryTreeVisualizer:
    def __init__(self, root):
        self.window = root
        # 更柔和的整体窗体背景（偏暖灰 + 微蓝）
        self.window.config(bg="#F3F6FA")
        self.window.title("二叉树可视化工具")
        
        try:
            self.window.iconbitmap("binary_tree_icon.ico")
        except:
            pass
        
        self.canvas_width = 1250
        self.canvas_height = 520
        # 画布放在中间卡片上，用白色卡片和阴影突出
        self.canvas = Canvas(self.window, bg="#F3F6FA", width=self.canvas_width, height=self.canvas_height, 
                             relief=FLAT, bd=0, highlightthickness=0)
        self.canvas.pack(pady=(15, 0), padx=15, fill=BOTH, expand=True)

        self.root_node: Optional[TreeNode] = None

        self.node_items: List[int] = []

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
        # 初次绘制装饰（会在 redraw 时重绘）
        self.draw_decorations()
        self.draw_instructions()

    # ---------- 辅助绘制函数 ----------
    def draw_rounded_rect(self, x1, y1, x2, y2, r=12, **kwargs):
        """在 canvas 上绘制圆角矩形，返回创建的 id 列表（弧 + 矩形组合）"""
        if r <= 0:
            return [self.canvas.create_rectangle(x1, y1, x2, y2, **kwargs)]
        # 四个角的弧
        ids = []
        ids.append(self.canvas.create_arc(x1, y1, x1+2*r, y1+2*r, start=90, extent=90, style=PIESLICE, **kwargs))
        ids.append(self.canvas.create_arc(x2-2*r, y1, x2, y1+2*r, start=0, extent=90, style=PIESLICE, **kwargs))
        ids.append(self.canvas.create_arc(x1, y2-2*r, x1+2*r, y2, start=180, extent=90, style=PIESLICE, **kwargs))
        ids.append(self.canvas.create_arc(x2-2*r, y2-2*r, x2, y2, start=270, extent=90, style=PIESLICE, **kwargs))
        # 中间矩形与边矩形
        ids.append(self.canvas.create_rectangle(x1+r, y1, x2-r, y2, **kwargs))
        ids.append(self.canvas.create_rectangle(x1, y1+r, x2, y2-r, **kwargs))
        return ids

    def draw_decorations(self):
        """在画布上绘制背景卡片、阴影和角落装饰。每次 redraw_tree 前调用以保持背景一致。"""
        self.canvas.delete("decor")  # 先清理老装饰（使用 tag）
        # 背景底色（使用画布本身背景）
        # 卡片阴影
        cx1, cy1 = 12, 12
        cx2, cy2 = self.canvas_width - 12, self.canvas_height - 12
        shadow_ids = []
        # 画几层半透明阴影（模拟柔和阴影）
        for i, off in enumerate((6,4,2)):
            alpha_fill = "#E6EDF6" if i == 0 else "#EEF6F9"
            sid = self.canvas.create_rectangle(cx1+off, cy1+off, cx2+off, cy2+off, fill=alpha_fill, outline="", tags=("decor",))
            shadow_ids.append(sid)
        # 卡片主体（白卡片，圆角）
        card_ids = self.draw_rounded_rect(cx1, cy1, cx2, cy2, r=14, fill="#FFFFFF", outline="", tags=None)
        for _id in card_ids:
            # 为了方便整体清理，重新加 tag
            self.canvas.addtag_withtag("decor", _id)

        # 角落装饰 —— 圆点与半透明带
        # 左上小圆
        dot1 = self.canvas.create_oval(cx1+18, cy1+18, cx1+58, cy1+58, fill="#E6F2FF", outline="", tags=("decor",))
        # 右上装饰带（弧形）
        arc = self.canvas.create_oval(cx2-120, cy1-40, cx2+40, cy1+120, fill="#F0FAF4", outline="", tags=("decor",))
        # 右下渐变状叠层（用多个同心圆模拟）
        for i in range(3):
            r = 40 + i*18
            opacity = 0.06 + i*0.02
            # 近似透明色使用浅色阶
            col = "#F3F8F6" if i % 2 == 0 else "#EEF8FF"
            c = self.canvas.create_oval(cx2 - r - 20, cy2 - r - 20, cx2 + r - 20, cy2 + r - 20, fill=col, outline="", tags=("decor",))
        # 微弱网格线（作为装饰，不影响主体）
        step = 80
        for x in range(int(cx1)+step, int(cx2), step):
            gid = self.canvas.create_line(x, cy1+20, x, cy2-20, fill="#F4F7FA", dash=(2,6), tags=("decor",))
        for y in range(int(cy1)+step, int(cy2), step):
            gid = self.canvas.create_line(cx1+20, y, cx2-20, y, fill="#F8FAFC", dash=(2,6), tags=("decor",))

        # 把装饰放到底层（确保节点和线在线上方）
        self.canvas.tag_lower("decor")

    # ---------- 控件 ----------
    def create_controls(self):
        # 主控制框架作为“卡片”置于窗口上方
        control_frame = Frame(self.window, bg="#F3F6FB", pady=10)
        control_frame.pack(fill=X, padx=30, pady=(18, 6))
        
        # 标题
        title_label = Label(control_frame, text="二叉树可视化工具", font=("Segoe UI", 16, "bold"), 
                          bg="#F3F6FB", fg="#2D3748")
        title_label.pack(pady=(0, 8))

        # 输入区域框架
        input_frame = Frame(control_frame, bg="#F3F6FB")
        input_frame.pack(fill=X, pady=5)
        
        label = Label(input_frame, text="输入层序序列:", font=("Segoe UI", 11), 
                     bg="#F3F6FB", fg="#4A5568")
        label.pack(side=LEFT, padx=(0, 10))

        entry = Entry(input_frame, textvariable=self.input_var, width=50, font=("Segoe UI", 11),
                     relief=SOLID, bd=1, highlightthickness=1, highlightcolor="#4299E1", 
                     highlightbackground="#CBD5E0")
        entry.pack(side=LEFT, padx=(0, 10), fill=X, expand=True)
        entry.insert(0, "1,2,3,#,4,#,5")

        # 按钮框架
        button_frame = Frame(control_frame, bg="#F3F6FB")
        button_frame.pack(fill=X, pady=10)
        
        # 按钮样式
        button_style = {"font": ("Segoe UI", 10), "width": 12, "height": 1, 
                       "relief": FLAT, "bd": 0, "cursor": "hand2"}
        
        build_btn = Button(button_frame, text="一步构建", **button_style,
                          bg="#48BB78", fg="white", activebackground="#38A169",
                          command=self.build_tree_from_input)
        build_btn.pack(side=LEFT, padx=5)

        animate_btn = Button(button_frame, text="逐步构建", **button_style,
                            bg="#4299E1", fg="white", activebackground="#3182CE",
                            command=self.start_animated_build)
        animate_btn.pack(side=LEFT, padx=5)

        clear_btn = Button(button_frame, text="清空画布", **button_style,
                          bg="#ED8936", fg="white", activebackground="#DD6B20",
                          command=self.clear_canvas)
        clear_btn.pack(side=LEFT, padx=5)

        back_btn = Button(button_frame, text="返回主界面", **button_style,
                         bg="#718096", fg="white", activebackground="#4A5568",
                         command=self.back_to_main)
        back_btn.pack(side=LEFT, padx=5)
        
        # 添加提示标签
        hint_label = Label(control_frame, text="提示: 使用逗号分隔节点，#表示空节点", 
                          font=("Segoe UI", 9), bg="#F3F6FB", fg="#718096")
        hint_label.pack(pady=(5, 0))

    # ---------- 状态 ----------
    def draw_instructions(self):
        # instructions 也画在画布上，带 tag 以便在 redraw 时清理保留装饰
        self.canvas.delete("instr")
        # 在卡片顶部画一条细线装饰
        self.canvas.create_line(30, 42, self.canvas_width-30, 42, fill="#EEF2F7", width=1, tags=("instr",))
        self.canvas.create_text(30, 20, 
                               text="显示规则：每个节点分为3格 [left | value | right]，左右指针连接到子节点或指向NULL", 
                               anchor="w", font=("Segoe UI", 10), fill="#4A5568", tags=("instr",))
        # 初始化右上状态文本 id
        if self.status_text_id:
            try:
                self.canvas.delete(self.status_text_id)
            except Exception:
                pass
        self.status_text_id = self.canvas.create_text(
            self.canvas_width - 30, 20, text="就绪", anchor="ne", 
            font=("Segoe UI", 11, "bold"), fill="#4299E1", tags=("instr",)
        )

    def update_status(self, text: str, color: str = "#4299E1"):
        if not self.status_text_id:
            self.status_text_id = self.canvas.create_text(
                self.canvas_width - 15, 15, text=text, anchor="ne", 
                font=("Segoe UI", 11, "bold"), fill=color, tags=("instr",)
            )
        else:
            self.canvas.itemconfig(self.status_text_id, text=text, fill=color)

    # ---------- 核心交互 ----------
    def build_tree_from_input(self):
        text = self.input_var.get().strip()
        if not text:
            messagebox.showinfo("提示", "请输入层序序列，例如：1,2,3,#,4,#,5")
            return
        parts = [p.strip() for p in text.split(",")]
        root, _ = BinaryTreeModel.build_from_level_order(parts)
        self.root_node = root
        self.redraw_tree()
        self.update_status("构建完成", "#48BB78")

    def clear_canvas(self):
        if self.animating:
            self.update_status("正在动画中，请稍后...", "#E53E3E")
            return
        # 清空非装饰/非控制标记的元素（保持 decor tag 可以被替换）
        self.canvas.delete("all")
        self.node_items.clear()
        self.node_to_rect.clear()
        self.root_node = None
        # 重新绘制装饰与提示
        self.draw_decorations()
        self.draw_instructions()
        self.update_status("已清空画布", "#4299E1")

    def redraw_tree(self):
        """
        清空并按 self.root_node 绘制整棵树；同时构建 node->rect 的映射（用于高亮）
        """
        # 清除图元但保留装饰（decor）——先删除除 decor 以外的元素
        # 最简单：完全清空再重绘装饰
        self.canvas.delete("all")
        self.node_items.clear()
        self.node_to_rect.clear()
        # 重新绘制装饰和说明
        self.draw_decorations()
        self.draw_instructions()
        if not self.root_node:
            self.canvas.create_text(self.canvas_width/2, self.canvas_height/2, 
                                   text="空树", font=("Segoe UI", 16), fill="#A0AEC0")
            return
        initial_offset = self.canvas_width / 4
        start_y = 80
        self._draw_node(self.root_node, self.canvas_width/2, start_y, initial_offset)

    # ------------- 布局（仅计算坐标） -------------
    def compute_positions(self, root: Optional[TreeNode]) -> Dict[TreeNode, Tuple[float,float]]:
        pos: Dict[TreeNode, Tuple[float,float]] = {}
        if not root:
            return pos
        initial_offset = self.canvas_width / 4
        start_y = 80

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
            self.update_status("已有动画在进行中", "#E53E3E")
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
        self.update_status("开始动画构建...", "#4299E1")
        self._animated_step(0)

    def _animated_step(self, idx: int):
        # 结束条件
        if idx >= len(self.batch_queue):
            self.animating = False
            self.update_status("构建完成", "#48BB78")
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
        self.update_status(f"插入中: {self.batch_queue[idx]} (位置: {idx})", "#4299E1")

        # 高亮父节点（如果存在并在当前绘制映射中）
        if parent_node and parent_node in self.node_to_rect:
            rect_id = self.node_to_rect[parent_node]
            try:
                self.canvas.itemconfig(rect_id, fill="#FEFCBF", outline="#D69E2E", width=2)
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
        start_cy = 30
        left = start_cx - self.node_w/2
        top = start_cy - self.node_h/2
        right = start_cx + self.node_w/2
        bottom = start_cy + self.node_h/2

        # 添加阴影效果
        shadow_offset = 2
        shadow_rect = self.canvas.create_rectangle(
            left+shadow_offset, top+shadow_offset, 
            right+shadow_offset, bottom+shadow_offset,
            fill="#E2E8F0", outline=""
        )
        temp_rect = self.canvas.create_rectangle(
            left, top, right, bottom, 
            fill="#C6F6D5", outline="#38A169", width=2
        )
        x1 = left + self.left_cell_w
        x2 = x1 + self.center_cell_w
        temp_text = self.canvas.create_text(
            (x1 + x2)/2, (top + bottom)/2, 
            text=str(target_item.val), 
            font=("Segoe UI", 12, "bold"),
            fill="#22543D"
        )

        # 动画移动到目标位置
        steps = 30
        dx = (target_cx - start_cx) / steps
        dy = (target_cy - start_cy) / steps
        delay = 12

        def step(i=0):
            if i < steps:
                self.canvas.move(shadow_rect, dx, dy)
                self.canvas.move(temp_rect, dx, dy)
                self.canvas.move(temp_text, dx, dy)
                self.window.after(delay, lambda: step(i+1))
            else:
                # 删除临时图元，设置并重绘完整树（含新节点）
                try:
                    self.canvas.delete(shadow_rect)
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
                                self.canvas.itemconfig(
                                    self.node_to_rect[new_parent], 
                                    fill="#FEFCBF", outline="#D69E2E", width=2
                                )
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

        # 添加阴影效果（单个节点）
        shadow_offset = 3
        shadow_rect = self.canvas.create_rectangle(
            left+shadow_offset, top+shadow_offset, 
            right+shadow_offset, bottom+shadow_offset,
            fill="#E9F3FF", outline=""
        )
        
        rect = self.canvas.create_rectangle(
            left, top, right, bottom, 
            fill="#FFF", outline="#C6E4FF", width=2
        )
        # 记录映射（TreeNode -> rect id）
        self.node_to_rect[node] = rect
        self.node_items.append(rect)
        self.node_items.append(shadow_rect)

        # 分割竖线
        x1 = left + self.left_cell_w
        x2 = x1 + self.center_cell_w
        v1 = self.canvas.create_line(x1, top, x1, bottom, width=1, fill="#EDF2F7")
        v2 = self.canvas.create_line(x2, top, x2, bottom, width=1, fill="#EDF2F7")
        self.node_items += [v1, v2]

        # 中间值
        self.canvas.create_text(
            (x1 + x2)/2, (top + bottom)/2, 
            text=str(node.val), 
            font=("Segoe UI", 12, "bold"),
            fill="#1F2937"
        )

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
            rect_null = self.canvas.create_rectangle(
                null_x - 28, null_y - 14, null_x + 28, null_y + 14, 
                fill="#FFF5F5", outline="#FED7D7", width=1
            )
            text_null = self.canvas.create_text(
                null_x, null_y, text="NULL", 
                font=("Segoe UI", 9, "bold"), fill="#C53030"
            )
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
            rect_null = self.canvas.create_rectangle(
                null_x - 28, null_y - 14, null_x + 28, null_y + 14, 
                fill="#FFF5F5", outline="#FED7D7", width=1
            )
            text_null = self.canvas.create_text(
                null_x, null_y, text="NULL", 
                font=("Segoe UI", 9, "bold"), fill="#C53030"
            )
            self.node_items += [rect_null, text_null]
            self._draw_line_from_cell_to_child(right_center_x, bottom, null_x, null_y - 14)

    def _draw_line_from_cell_to_child(self, sx, sy, ex, ey):
        mid_y = sy + 10
        line1 = self.canvas.create_line(sx, sy, sx, mid_y, width=2, fill="#667085")
        line2 = self.canvas.create_line(sx, mid_y, ex, ey, arrow=LAST, width=2, fill="#667085")
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
    window.title("二叉树可视化工具")
    window.geometry("1350x780")
    window.configure(bg="#F3F6FA")
    # 设置窗口图标（如果有的话）
    try:
        window.iconbitmap("binary_tree_icon.ico")
    except:
        pass
    BinaryTreeVisualizer(window)
    window.mainloop()
