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

class BSTVisualizer:
    def __init__(self, root):
        # --- 仅改动：统一深色背景色调变量 ---
        self.WIN_BG = "#0B1220"         # 窗口背景
        self.PANEL_BG = "#0F2330"       # 控件区域背景
        self.CANVAS_BG = "#071A2B"      # 画布背景
        self.TEXT_COLOR = "#E6F7FF"     # 默认文字颜色
        self.HINT_COLOR = "#9FB8C6"     # 次要文字颜色
        self.STATUS_COLOR = "lightgreen"

        self.window = root
        # 将主窗体背景改为深色
        self.window.config(bg=self.WIN_BG)
        self.canvas_width = 1250
        self.canvas_height = 560
        # 画布背景改为深色
        self.canvas = Canvas(self.window, bg=self.CANVAS_BG, width=self.canvas_width, height=self.canvas_height, relief=RAISED, bd=8, highlightthickness=0)
        self.canvas.pack(pady=(10,0))

        # 模型
        self.model = BSTModel()
        
        self.dsl_var = StringVar()

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
        # 父框（占据一整行），背景改为深色
        top_frame = Frame(self.window, bg=self.PANEL_BG)
        top_frame.pack(pady=6, fill=X)

        # 上排：主输入 + 操作按钮（占满宽度，超多按钮会自动换行到下一行）
        op_frame = Frame(top_frame, bg=self.PANEL_BG)
        op_frame.pack(fill=X, padx=6)

        Label(op_frame, text="值输入（单值或逗号/空格批量）:", font=("Arial",12), bg=self.PANEL_BG, fg=self.TEXT_COLOR).pack(side=LEFT, padx=(0,6))
        entry = Entry(op_frame, textvariable=self.input_var, width=36, font=("Arial",12), bg="#16313a", fg=self.TEXT_COLOR, insertbackground=self.TEXT_COLOR)
        entry.pack(side=LEFT, padx=(0,8))
        entry.insert(0, "15,6,23,4,7,71,5")

        Button(op_frame, text="Insert (直接)", command=self.insert_direct, bg="#1f8f4a", fg="white").pack(side=LEFT, padx=4)
        Button(op_frame, text="Insert (动画)", command=self.start_insert_animated, bg="#2E8B57", fg="white").pack(side=LEFT, padx=4)
        Button(op_frame, text="Search (动画)", command=self.start_search_animated, bg="#FFA500").pack(side=LEFT, padx=4)
        Button(op_frame, text="Delete (动画)", command=self.start_delete_animated, bg="#c04a4a", fg="white").pack(side=LEFT, padx=4)
        Button(op_frame, text="清空", command=self.clear_canvas, bg="#d67a2a").pack(side=LEFT, padx=4)
        Button(op_frame, text="返回主界面", command=self.back_to_main, bg="#2B6CB0", fg="white").pack(side=LEFT, padx=4)

        # 下排：保存/打开 + DSL（保证可见）
        bottom_frame = Frame(self.window, bg=self.PANEL_BG)
        bottom_frame.pack(pady=(4,8), fill=X, padx=6)

        # 左侧：保存/打开
        left_ops = Frame(bottom_frame, bg=self.PANEL_BG)
        left_ops.pack(side=LEFT, anchor="w")
        Button(left_ops, text="保存树", command=self.save_tree, bg="#426EF6", fg="white").pack(side=LEFT, padx=6)
        Button(left_ops, text="打开树", command=self.load_tree, bg="#426EF6", fg="white").pack(side=LEFT, padx=6)

        # 右侧：DSL 输入（放在右边更显眼），但也能放在中间
        dsl_ops = Frame(bottom_frame, bg=self.PANEL_BG)
        dsl_ops.pack(side=RIGHT, anchor="e")
        Label(dsl_ops, text="DSL 命令:", font=("Arial",11), bg=self.PANEL_BG, fg=self.TEXT_COLOR).pack(side=LEFT, padx=(0,6))
        # 绑定到 self.dsl_var，保存为实例属性便于调试/访问
        self.dsl_entry = Entry(dsl_ops, width=36, font=("Arial",11), textvariable=self.dsl_var, bg="#16313a", fg=self.TEXT_COLOR, insertbackground=self.TEXT_COLOR)
        self.dsl_entry.pack(side=LEFT, padx=(0,6))
        # 回车执行
        self.dsl_entry.bind("<Return>", lambda e: self.process_dsl())
        # 按钮执行
        Button(dsl_ops, text="执行DSL", command=self.process_dsl, bg="#2B6CB0", fg="white").pack(side=LEFT)

        # 给 DSL entry 初始焦点提示（可选）
        # self.dsl_entry.insert(0, "例如: insert 10 20 30 / search 7 / delete 9 / create 5 6 7")

    def process_dsl(self, event=None):
        text = (self.dsl_var.get() or "").strip()
        if not text:
            return
        if getattr(self, "animating", False):
            messagebox.showinfo("提示", "当前正在动画，请稍后执行 DSL 命令")
            return
        try:
            # process_command 在文件顶部已导入（from DSL_utils import process_command）
            # 但我们仍做存在性判断以避免 import 问题
            try:
                from DSL_utils import process_command as _pc
            except Exception:
                _pc = None
            if _pc:
                _pc(self, text)
            else:
                # 回退实现（尽量提供最基本的行为）
                cmd = text.split()
                if not cmd:
                    return
                c = cmd[0].lower()
                args = cmd[1:]
                if c == "insert" or c == "create":
                    # 空格优先： insert 5 6 7 或 create 1 2 3
                    items = [a for a in args if a != ""]
                    # 兼容逗号写法
                    if len(items) == 1 and "," in items[0]:
                        items = [x.strip() for x in items[0].split(",") if x.strip()!=""]
                    # 清空并创建（create）或插入（insert）
                    if c == "create":
                        # 清空 model 并插入
                        try:
                            if hasattr(self.model, "clear"):
                                self.model.clear()
                            else:
                                self.model.root = None
                        except Exception:
                            pass
                        for v in items:
                            try:
                                self.model.insert(v)
                            except Exception:
                                pass
                        if hasattr(self, "redraw"):
                            self.redraw()
                    else:  # insert
                        for v in items:
                            try:
                                self.model.insert(v)
                            except Exception:
                                pass
                        if hasattr(self, "redraw"):
                            self.redraw()
                elif c == "search":
                    if not args:
                        messagebox.showerror("错误", "search 需要一个参数，例如：search 7")
                    else:
                        v = args[0]
                        # 尝试直接调用动画入口，否则简单 redraw + status
                        if hasattr(self, "input_var") and hasattr(self, "start_search_animated"):
                            self.input_var.set(v); self.start_search_animated()
                        else:
                            # 简易查找
                            node = None
                            if hasattr(self.model, "search_with_path"):
                                node, _ = self.model.search_with_path(v)
                            elif hasattr(self.model, "search"):
                                node = self.model.search(v)
                            if node is not None:
                                if hasattr(self, "update_status"):
                                    self.update_status(f"查找：找到 {v}")
                                if hasattr(self, "redraw"):
                                    self.redraw()
                            else:
                                if hasattr(self, "update_status"):
                                    self.update_status(f"查找：未找到 {v}")
                elif c == "delete":
                    if not args:
                        messagebox.showerror("错误", "delete 需要一个参数，例如：delete 7")
                    else:
                        v = args[0]
                        if hasattr(self, "input_var") and hasattr(self, "start_delete_animated"):
                            self.input_var.set(v); self.start_delete_animated()
                        else:
                            try:
                                if hasattr(self.model, "delete"):
                                    self.model.delete(v)
                                elif hasattr(self.model, "remove"):
                                    self.model.remove(v)
                                elif hasattr(self.model, "delete_by_value"):
                                    self.model.delete_by_value(v)
                            except Exception:
                                pass
                            if hasattr(self, "redraw"):
                                self.redraw()
                elif c == "clear":
                    if hasattr(self, "clear_canvas"):
                        self.clear_canvas()
                    else:
                        try:
                            self.model = BSTModel()
                        except Exception:
                            try:
                                self.model.root = None
                            except Exception:
                                pass
                        if hasattr(self, "redraw"):
                            self.redraw()
                else:
                    messagebox.showinfo("未识别命令", "支持：insert/search/delete/clear/create（参数以空格分隔，例如：insert 5 6 7）")
        finally:
            # 清空 DSL 输入框（改善 UX）
            try:
                self.dsl_var.set("")
            except Exception:
                pass

    
    def draw_instructions(self):
        self.canvas.delete("all")
        self.node_items.clear()
        self.node_to_rect.clear()
        # 指示文本颜色改为浅色，便于在深色背景上可读
        self.canvas.create_text(10, 10, anchor="nw", text="BST：插入 / 查找 / 删除 动态演示。中序位置用于横向布局。", font=("Arial",11), fill=self.TEXT_COLOR)
        if self.status_text_id:
            try:
                self.canvas.delete(self.status_text_id)
            except Exception:
                pass
        self.status_text_id = self.canvas.create_text(self.canvas_width-10, 10, anchor="ne", text="", font=("Arial",12,"bold"), fill=self.STATUS_COLOR)

    def update_status(self, text: str):
        if not self.status_text_id:
            self.status_text_id = self.canvas.create_text(self.canvas_width-10, 10, anchor="ne", text=text, font=("Arial",12,"bold"), fill=self.STATUS_COLOR)
        else:
            self.canvas.itemconfig(self.status_text_id, text=text)

    # ---------- storage helpers ----------
    def _ensure_tree_folder(self) -> str:
        """
        确保 save/tree 文件夹存在，优先使用 storage.ensure_save_subdir("tree")。
        返回该目录的绝对路径。
        """
        try:
            if hasattr(storage, "ensure_save_subdir"):
                return storage.ensure_save_subdir("bst")
            base_dir = os.path.dirname(os.path.abspath(storage.__file__))
            default_dir = os.path.join(base_dir, "save", "bst")
            os.makedirs(default_dir, exist_ok=True)
            return default_dir
        except Exception:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            default_dir = os.path.join(base_dir, "..", "save", "bst")
            default_dir = os.path.normpath(default_dir)
            os.makedirs(default_dir, exist_ok=True)
            return default_dir

    def save_tree(self):
        """
        将当前 self.model.root 保存为 JSON 文件（链式节点描述）。
        """
        try:
            if not self.model or getattr(self.model, "root", None) is None:
                if not messagebox.askyesno("确认", "当前树为空，是否仍然保存一个空树文件？"):
                    return

            default_dir = self._ensure_tree_folder()
            default_name = f"bst_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = filedialog.asksaveasfilename(
                initialdir=default_dir,
                initialfile=default_name,
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="保存树到文件"
            )
            if not filepath:
                return

            # 使用 storage.tree_to_dict（若可用）
            if hasattr(storage, "tree_to_dict"):
                try:
                    tree_dict = storage.tree_to_dict(self.model.root)
                except Exception as e:
                    print("storage.tree_to_dict error:", e)
                    tree_dict = {}
            else:
                tree_dict = {}

            metadata = {
                "saved_at": datetime.now().isoformat(),
                "node_count": len(tree_dict.get("nodes", [])) if isinstance(tree_dict, dict) else 0
            }
            payload = {"type": "tree", "tree": tree_dict, "metadata": metadata}
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)

            messagebox.showinfo("成功", f"二叉搜索树已保存到：\n{filepath}")
            self.update_status("保存成功")
        except Exception as e:
            print("save_tree error:", e)
            messagebox.showerror("错误", f"保存失败：{e}")
            self.update_status("保存失败")

    def load_tree(self):
        """
        从文件加载树结构并恢复为链式节点图，优先尝试 storage.tree_dict_to_nodes，
        否则如果文件是 list 或包含 data 字段，尝试用 BSTModel 逐项 insert 恢复（兜底兼容旧格式）。
        """
        try:
            default_dir = self._ensure_tree_folder()
            filepath = filedialog.askopenfilename(
                initialdir=default_dir,
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="从文件加载二叉树"
            )
            if not filepath:
                return

            with open(filepath, "r", encoding="utf-8") as f:
                obj = json.load(f)
            if not obj:
                messagebox.showerror("错误", "文件内容为空或无法解析")
                return

            # 优先识别标准 tree payload
            if isinstance(obj, dict) and obj.get("type") == "tree" and "tree" in obj:
                tree_dict = obj.get("tree", {})
            elif isinstance(obj, dict) and "nodes" in obj and "root" in obj:
                # 兼容旧式直接 tree_dict
                tree_dict = obj
            elif isinstance(obj, list):
                # 直接是一个层序或顺序数组的情况，使用 BSTModel 逐项插入作为兜底
                values = obj
                new_model = BSTModel()
                for v in values:
                    try:
                        new_model.insert(v)
                    except Exception:
                        # 尝试字符串化后插入
                        new_model.insert(str(v))
                self.model = new_model
                self.redraw()
                messagebox.showinfo("成功", f"已通过列表格式恢复为 BST（共 {len(values)} 项）")
                self.update_status("加载成功（通过列表恢复）")
                return
            elif isinstance(obj, dict) and "data" in obj and isinstance(obj.get("data"), list):
                values = obj.get("data", [])
                new_model = BSTModel()
                for v in values:
                    try:
                        new_model.insert(v)
                    except Exception:
                        new_model.insert(str(v))
                self.model = new_model
                self.redraw()
                messagebox.showinfo("成功", f"已通过 data 字段恢复为 BST（共 {len(values)} 项）")
                self.update_status("加载成功（通过 data 恢复）")
                return
            else:
                messagebox.showerror("错误", "文件格式不被识别（需为 tree 类型或包含 nodes/root，或为 list）")
                return

            # 若获得 tree_dict，尝试使用 storage.tree_dict_to_nodes 重建节点图
            if hasattr(storage, "tree_dict_to_nodes"):
                try:
                    new_root = storage.tree_dict_to_nodes(tree_dict, TreeNode)
                    if new_root is None:
                        raise RuntimeError("tree_dict_to_nodes 返回 None")
                    # 将新根赋给模型（注意：BSTModel 可能还需其他内部状态，若有需要请在 model 中提供恢复接口）
                    try:
                        self.model.root = new_root
                    except Exception:
                        # 若不能直接赋值（不太可能），则替换为新 BSTModel 并设置 root 属性
                        try:
                            nm = BSTModel()
                            nm.root = new_root
                            self.model = nm
                        except Exception:
                            # 最后兜底：仍然尝试把 new_root 直接用于绘图（不改变 model）
                            self.model.root = new_root
                    self.redraw()
                    messagebox.showinfo("成功", "二叉树已成功加载并恢复")
                    self.update_status("加载成功")
                    return
                except Exception as e:
                    print("tree_dict_to_nodes error:", e)
                    # 回退到其他方式
            # 如果到这里说明 tree_dict 重建失败或不存在 重试用层序数组字段（若存在）
            # 最后兜底：尝试从 obj.get("level_order") 或 obj.get("nodes") 中读取可用值
            if isinstance(obj, dict) and "level_order" in obj and isinstance(obj["level_order"], list):
                vals = obj["level_order"]
                new_model = BSTModel()
                for v in vals:
                    try:
                        new_model.insert(v)
                    except Exception:
                        new_model.insert(str(v))
                self.model = new_model
                self.redraw()
                messagebox.showinfo("成功", f"已通过 level_order 恢复（{len(vals)} 项）")
                self.update_status("加载成功（通过 level_order 恢复）")
                return

            messagebox.showwarning("警告", "已读取文件但无法自动重建为节点图（storage.tree_dict_to_nodes 失败），请检查文件格式或手动恢复。")
            self.update_status("加载但未能重建节点")
        except Exception as e:
            print("load_tree error:", e)
            messagebox.showerror("错误", f"加载失败：{e}")
            self.update_status("加载失败")

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
    def redraw(self):
        self.canvas.delete("all")
        # draw a subtle gradient-ish background on canvas (approximate by rectangles)
        w = max(self.canvas_width, self.canvas.winfo_width() if self.canvas.winfo_width() else self.canvas_width)
        h = max(self.canvas_height, self.canvas.winfo_height() if self.canvas.winfo_height() else self.canvas_height)
        stops = ["#071A2B", "#0A2433", "#0E2F3A"]
        steps = 30
        def interp(c1, c2, t):
            r1,g1,b1 = int(c1[1:3],16), int(c1[3:5],16), int(c1[5:7],16)
            r2,g2,b2 = int(c2[1:3],16), int(c2[3:5],16), int(c2[5:7],16)
            r = int(r1 + (r2-r1)*t); g = int(g1 + (g2-g1)*t); b = int(b1 + (b2-b1)*t)
            return f"#{r:02x}{g:02x}{b:02x}"
        for i in range(steps):
            t = i/(steps-1)
            idx = int(t*(len(stops)-1))
            t2 = (t*(len(stops)-1)) - idx
            c = interp(stops[idx], stops[min(idx+1, len(stops)-1)], t2)
            y0 = int(i*(h/steps))
            y1 = int((i+1)*(h/steps))
            self.canvas.create_rectangle(0, y0, w, y1, outline="", fill=c)
        # faint grid lines to give structure
        grid_col = "#0b3a46"
        for gx in range(0, w, 80):
            self.canvas.create_line(gx, 0, gx, h, fill=grid_col)
        for gy in range(0, h, 80):
            self.canvas.create_line(0, gy, w, gy, fill=grid_col)

        self.node_items.clear()
        self.node_to_rect.clear()
        self.draw_instructions()
        if self.model.root is None:
            self.canvas.create_text(self.canvas_width/2, self.canvas_height/2, text="空树", font=("Arial",18), fill="#9fb8c6")
            return
        pos = self.compute_positions()
        # draw edges first for nicer visuals (use a lighter color)
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
        l1 = self.canvas.create_line(cx, top, cx, mid_y, width=2, fill="#6ee7b7")
        l2 = self.canvas.create_line(cx, mid_y, tx, bot, arrow=LAST, width=2, fill="#86f0da")
        self.node_items += [l1, l2]

    def _draw_node(self, node: TreeNode, cx: float, cy: float):
        left = cx - self.node_w/2
        top = cy - self.node_h/2
        right = cx + self.node_w/2
        bottom = cy + self.node_h/2
        # 为了与深色背景形成对比，保留节点为浅色卡片
        rect = self.canvas.create_rectangle(left, top, right, bottom, fill="#F0F8FF", outline="black", width=2)
        self.node_to_rect[node] = rect
        self.node_items.append(rect)
        # vertical splits
        x1 = left + self.left_cell_w
        x2 = x1 + self.center_cell_w
        v1 = self.canvas.create_line(x1, top, x1, bottom, width=1)
        v2 = self.canvas.create_line(x2, top, x2, bottom, width=1)
        self.node_items += [v1, v2]
        self.canvas.create_text((x1+x2)/2, (top+bottom)/2, text=str(node.val), font=("Arial",12,"bold"), fill="#0b2236")

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
                # now animate deletion process (visualize)
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
        
if __name__ == '__main__':
    w = Tk()
    w.title("BST 可视化")
    w.geometry("1350x730")
    BSTVisualizer(w)
    w.mainloop()
