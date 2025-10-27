from tkinter import *
from tkinter import ttk
from tkinter import messagebox, filedialog
from typing import Dict, Tuple, List, Optional
from rbt.rbt_model import RBModel, RBNode, clone_tree
import storage as storage


class RBTVisualizer:
    def __init__(self, root):
        self.window = root
        self.window.title("红黑树可视化演示")
        self.window.config(bg="#F0F2F5")
        
        # 设置窗口图标和样式
        self.window.geometry("1350x750")
        self.window.minsize(1200, 700)
        
        # 颜色配置
        self.colors = {
            "bg_primary": "#F0F2F5",
            "bg_secondary": "#FFFFFF",
            "red_node": "#FF5252",
            "black_node": "#37474F",
            "highlight": "#FF9800",
            "path_highlight": "#4CAF50",
            "text_light": "#FFFFFF",
            "text_dark": "#212121",
            "btn_primary": "#2196F3",
            "btn_success": "#4CAF50",
            "btn_warning": "#FF9800",
            "btn_danger": "#F44336",
            "canvas_bg": "#FAFAFA"
        }
        
        # 创建主框架
        self.main_frame = Frame(self.window, bg=self.colors["bg_primary"])
        self.main_frame.pack(fill=BOTH, expand=True, padx=12, pady=12)
        
        # 创建标题
        self.create_header()
        
        # 创建画布区域
        self.create_canvas_area()
        
        # 创建控制面板
        self.create_control_panel()
        
        # 初始化模型和状态
        self.model = RBModel()
        self.node_vis: Dict[str, Dict] = {}
        self.animating = False
        self.node_w = 120
        self.node_h = 44
        self.level_gap = 100
        self.margin_x = 40
        
        # 绘制初始说明
        self.draw_instructions()

    def create_header(self):
        """创建标题区域"""
        header_frame = Frame(self.main_frame, bg=self.colors["bg_secondary"], 
                           relief=RAISED, bd=1)
        header_frame.pack(fill=X, pady=(0, 12))
        
        title_label = Label(header_frame, text="红黑树可视化演示系统", 
                          font=("微软雅黑", 16, "bold"), 
                          bg=self.colors["bg_secondary"],
                          fg=self.colors["text_dark"],
                          pady=12)
        title_label.pack()
        
        subtitle_label = Label(header_frame, 
                             text="演示红黑树的插入过程：搜索路径、红节点插入、颜色调整与旋转修复",
                             font=("微软雅黑", 10), 
                             bg=self.colors["bg_secondary"],
                             fg="#666666")
        subtitle_label.pack(pady=(0, 10))

    def create_canvas_area(self):
        """创建画布区域"""
        canvas_container = Frame(self.main_frame, bg=self.colors["bg_secondary"],
                               relief=SOLID, bd=1)
        canvas_container.pack(fill=BOTH, expand=True, pady=(0, 12))
        
        # 画布控制栏
        canvas_toolbar = Frame(canvas_container, bg=self.colors["bg_secondary"], height=30)
        canvas_toolbar.pack(fill=X, padx=10, pady=8)
        canvas_toolbar.pack_propagate(False)
        
        self.status_label = Label(canvas_toolbar, text="就绪", 
                                font=("微软雅黑", 10), 
                                bg=self.colors["bg_secondary"],
                                fg=self.colors["btn_primary"],
                                anchor=W)
        self.status_label.pack(side=LEFT, fill=X, expand=True)
        
        # 画布
        self.canvas_w = 1200
        self.canvas_h = 560
        self.canvas = Canvas(canvas_container, bg=self.colors["canvas_bg"], 
                           width=self.canvas_w, height=self.canvas_h,
                           relief=FLAT, highlightthickness=1,
                           highlightbackground="#E0E0E0")
        self.canvas.pack(padx=10, pady=(0, 10), fill=BOTH, expand=True)

    def create_control_panel(self):
        """创建控制面板"""
        control_frame = Frame(self.main_frame, bg=self.colors["bg_secondary"],
                            relief=SOLID, bd=1)
        control_frame.pack(fill=X)
        
        # 输入区域
        input_frame = Frame(control_frame, bg=self.colors["bg_secondary"])
        input_frame.pack(fill=X, padx=15, pady=12)
        
        Label(input_frame, text="输入节点值:", 
              font=("微软雅黑", 10), 
              bg=self.colors["bg_secondary"]).grid(row=0, column=0, sticky=W, pady=5)
        
        self.input_var = StringVar()
        self.entry = Entry(input_frame, textvariable=self.input_var, 
                          width=40, font=("微软雅黑", 10),
                          relief=SOLID, bd=1)
        self.entry.grid(row=0, column=1, padx=8, pady=5, sticky=EW)
        self.entry.insert(0, "1,2,3,4,5,0,6")
        
        # 按钮区域
        btn_frame = Frame(control_frame, bg=self.colors["bg_secondary"])
        btn_frame.pack(fill=X, padx=15, pady=10)
        
        # 第一行按钮
        btn_row1 = Frame(btn_frame, bg=self.colors["bg_secondary"])
        btn_row1.pack(fill=X, pady=5)
        
        self.create_button(btn_row1, "插入节点 (动画演示)", 
                         self.start_insert_animated, self.colors["btn_success"]).pack(side=LEFT, padx=4)
        self.create_button(btn_row1, "插入节点 (直接)", 
                         self.insert_direct, self.colors["btn_primary"]).pack(side=LEFT, padx=4)
        self.create_button(btn_row1, "清空树", 
                         self.clear_canvas, self.colors["btn_warning"]).pack(side=LEFT, padx=4)
        
        # 第二行按钮
        btn_row2 = Frame(btn_frame, bg=self.colors["bg_secondary"])
        btn_row2.pack(fill=X, pady=5)
        
        self.create_button(btn_row2, "保存结构", 
                         self.save_structure, "#9C27B0").pack(side=LEFT, padx=4)
        self.create_button(btn_row2, "加载结构", 
                         self.load_structure, "#9C27B0").pack(side=LEFT, padx=4)
        self.create_button(btn_row2, "返回主界面", 
                         self.back_to_main, self.colors["btn_danger"]).pack(side=LEFT, padx=4)
        
        # 配置网格权重
        input_frame.columnconfigure(1, weight=1)

    def create_button(self, parent, text, command, color):
        """创建样式化按钮"""
        return Button(parent, text=text, command=command,
                     bg=color, fg="white", font=("微软雅黑", 9),
                     relief=FLAT, bd=0, padx=12, pady=6,
                     cursor="hand2")

    def draw_instructions(self):
        """绘制初始说明"""
        self.canvas.delete("all")
        self.node_vis.clear()    
        # 绘制图例
        legend_y = self.canvas_h - 30
        self.draw_legend(legend_y)

    def draw_legend(self, y_pos):
        """绘制图例"""
        legend_items = [
            ("红节点", self.colors["red_node"]),
            ("黑节点", self.colors["black_node"]),
            ("搜索路径", self.colors["path_highlight"]),
            ("当前操作", self.colors["highlight"])
        ]
        
        x_pos = 20
        for text, color in legend_items:
            # 颜色方块
            self.canvas.create_rectangle(x_pos, y_pos-8, x_pos+16, y_pos+8,
                                       fill=color, outline="#CCCCCC")
            # 文本
            self.canvas.create_text(x_pos+25, y_pos, text=text, 
                                  font=("微软雅黑", 9), anchor=W, fill="#666666")
            x_pos += 90

    def update_status(self, text: str):
        """更新状态栏"""
        self.status_label.config(text=text)

    def _draw_connection(self, cx, cy, tx, ty):
        """绘制节点连接线"""
        top = cy + self.node_h/2
        bot = ty - self.node_h/2
        midy = (top + bot) / 2
        
        # 绘制带箭头的连接线
        line = self.canvas.create_line(cx, top, cx, midy, tx, bot, 
                                     width=2, fill="#78909C", arrow=LAST,
                                     smooth=True)
        return line

    def compute_positions_for_root(self, root: Optional[RBNode]) -> Dict[str, Tuple[float, float]]:
        """计算节点位置"""
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
            y = 80 + depths[node] * self.level_gap
            res[key] = (x, y)
            
        return res

    def _build_key_maps_from_root(self, root: Optional[RBNode]) -> Tuple[Dict[int,str], Dict[str, RBNode]]:
        """构建键映射"""
        orig_id_to_key: Dict[int,str] = {}
        key_to_node: Dict[str, RBNode] = {}
        if not root:
            return orig_id_to_key, key_to_node

        inorder_nodes: List[RBNode] = []
        def inorder_collect(n: Optional[RBNode]):
            if not n:
                return
            inorder_collect(n.left)
            inorder_nodes.append(n)
            inorder_collect(n.right)
        inorder_collect(root)

        counts: Dict[str,int] = {}
        for node in inorder_nodes:
            base = str(node.val)
            cnt = counts.get(base, 0)
            counts[base] = cnt + 1
            key = f"{base}#{cnt}" if cnt > 0 else base
            key_to_node[key] = node
            if getattr(node, 'orig_id', None) is not None:
                orig_id_to_key[node.orig_id] = key
        return orig_id_to_key, key_to_node

    def draw_tree_from_root(self, root: Optional[RBNode]):
        """绘制树"""
        self.canvas.delete("all")
        self.draw_instructions()
        
        if root is None:
            self.canvas.create_text(self.canvas_w/2, self.canvas_h/2, 
                                  text="空树", font=("微软雅黑", 16), fill="#9E9E9E")
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

        # 先绘制边
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

        # 绘制节点
        self.node_vis.clear()
        for node, key in node_to_key.items():
            cx, cy = pos[key]
            self.draw_tree_node(cx, cy, node, key)

    def draw_tree_node(self, cx: float, cy: float, node: RBNode, key: str):
        """绘制单个树节点"""
        left = cx - self.node_w/2
        top = cy - self.node_h/2
        right = cx + self.node_w/2
        bottom = cy + self.node_h/2
        
        # 节点颜色
        is_red = node.color == "R"
        fill_color = self.colors["red_node"] if is_red else self.colors["black_node"]
        text_color = self.colors["text_light"] if not is_red else self.colors["text_dark"]
        
        # 绘制节点主体（圆角矩形效果）
        rect = self.canvas.create_rectangle(left, top, right, bottom,
                                          fill=fill_color, outline="#E0E0E0",
                                          width=2, stipple="gray50")
        
        # 节点内部区域分隔
        x1 = left + 28
        x2 = x1 + 64
        self.canvas.create_line(x1, top, x1, bottom, width=1, fill="#FFFFFF" if is_red else "#546E7A")
        self.canvas.create_line(x2, top, x2, bottom, width=1, fill="#FFFFFF" if is_red else "#546E7A")
        
        # 节点值
        txt = self.canvas.create_text(cx, cy, text=str(node.val),
                                    font=("微软雅黑", 11, "bold"), fill=text_color)
        
        # 颜色标识
        color_label = self.canvas.create_text(left+14, cy, text=node.color,
                                            font=("微软雅黑", 9, "bold"),
                                            fill="#FFD54F" if is_red else "#B0BEC5")
        
        self.node_vis[key] = {
            'rect': rect, 
            'text': txt, 
            'cx': cx, 
            'cy': cy, 
            'val': str(node.val),
            'color_label': color_label
        }

    def start_insert_animated(self):
        """开始动画插入"""
        if self.animating:
            messagebox.showinfo("提示", "当前正在执行动画，请稍候...")
            return
            
        if not self.validate_input():
            return
            
        self.animating = True
        self.batch = [p.strip() for p in self.input_var.get().split(",") if p.strip()]
        self._insert_seq(0)

    def insert_direct(self):
        """直接插入（无动画）"""
        if not self.validate_input():
            return
            
        values = [p.strip() for p in self.input_var.get().split(",") if p.strip()]
        for val in values:
            self.model.insert(val)
            
        self.draw_tree_from_root(clone_tree(self.model.root))
        self.update_status(f"已直接插入节点: {', '.join(values)}")

    def validate_input(self):
        """验证输入"""
        s = self.input_var.get().strip()
        if not s:
            messagebox.showinfo("提示", "请输入数字，用逗号分隔\n例如：10, 5, 20, 15, 30")
            return False
            
        try:
            values = [p.strip() for p in s.split(",") if p.strip()]
            for val in values:
                int(val)  # 验证是否为数字
        except ValueError:
            messagebox.showerror("错误", "输入包含非数字内容，请确保只输入数字")
            return False
            
        return True

    def _insert_seq(self, idx: int):
        """插入序列"""
        if idx >= len(self.batch):
            self.animating = False
            self.update_status("所有插入操作已完成")
            return

        val = self.batch[idx]
        inserted_node, path_nodes, events, snapshots = self.model.insert_with_steps(val)

        snap_pre = snapshots[0]
        snap_after_insert = snapshots[1] if len(snapshots) > 1 else None

        pos_pre = self.compute_positions_for_root(snap_pre)
        origid_to_key_pre, _ = self._build_key_maps_from_root(snap_pre)

        def highlight_path(i=0):
            if i >= len(path_nodes):
                self.update_status(f"插入 {val}: 定位插入位置")
                self.animate_flyin_new(val, snap_after_insert, 
                                     lambda: self._after_insert_events(events, snapshots, idx))
                return
                
            node = path_nodes[i]
            node_id = getattr(node, 'id', None)
            key = origid_to_key_pre.get(node_id)
            self.draw_tree_from_root(snap_pre)
            
            if key:
                try:
                    self.canvas.itemconfig(self.node_vis[key]['rect'], 
                                         outline=self.colors["path_highlight"], 
                                         width=3)
                except Exception:
                    pass
                    
            self.update_status(f"搜索路径: 访问节点 {node.val} (步骤 {i+1})")
            self.window.after(450, lambda: highlight_path(i+1))

        highlight_path(0)

    def animate_flyin_new(self, val_str: str, snap_after_insert: Optional[RBNode], on_complete):
        """动画：新节点飞入"""
        if not snap_after_insert:
            on_complete()
            return
            
        pos_after = self.compute_positions_for_root(snap_after_insert)
        origid_to_key_after, _ = self._build_key_maps_from_root(snap_after_insert)
        
        # 找到新插入的节点
        candidate_keys = [k for id_, k in origid_to_key_after.items() 
                         if k and k.split('#')[0] == str(val_str)]
        if not candidate_keys:
            candidate_keys = [k for k in pos_after.keys() 
                            if k.split('#')[0] == str(val_str)]
        if not candidate_keys:
            on_complete()
            return
            
        target_key = candidate_keys[-1]
        tx, ty = pos_after[target_key]

        # 起始位置（画布顶部中央）
        sx, sy = self.canvas_w/2, 20
        
        # 创建临时节点
        left = sx - self.node_w/2
        top = sy - self.node_h/2
        right = sx + self.node_w/2
        bottom = sy + self.node_h/2
        
        temp_rect = self.canvas.create_rectangle(left, top, right, bottom,
                                               fill="#FFE0B2", outline="#FF9800",
                                               width=2)
        temp_text = self.canvas.create_text(sx, sy, text=str(val_str),
                                          font=("微软雅黑", 11, "bold"))

        # 动画参数
        steps = 30
        dx = (tx - sx)/steps
        dy = (ty - sy)/steps
        delay = 15
        
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
                    # 高亮新插入的节点
                    self.canvas.itemconfig(self.node_vis[target_key]['rect'], 
                                         outline=self.colors["highlight"], 
                                         width=3)
                except Exception:
                    pass
                    
                self.window.after(400, on_complete)
        step()

    def _animate_single_event(self, before_root: Optional[RBNode], after_root: Optional[RBNode], event: Dict, on_done):
        """动画：单步操作"""
        pos_before = self.compute_positions_for_root(before_root)
        pos_after = self.compute_positions_for_root(after_root)

        self.draw_tree_from_root(before_root)
        origid_to_key_before, key_to_node_before = self._build_key_maps_from_root(before_root)
        origid_to_key_after, key_to_node_after = self._build_key_maps_from_root(after_root)

        # 收集需要移动的节点
        keys_common = set(pos_before.keys()) & set(pos_after.keys())
        moves = []
        for k in keys_common:
            item = self.node_vis.get(k)
            if not item:
                continue
            sx, sy = pos_before[k]
            tx, ty = pos_after[k]
            moves.append((k, item['rect'], item['text'], sx, sy, tx, ty))

        # 添加操作说明
        label_id = None
        op_type = event.get('type', '')
        
        if op_type == 'recolor':
            label_text = "颜色调整: 父节点和叔节点变黑，祖父节点变红"
            label_color = "#D32F2F"
        elif op_type in ['rotate_left', 'rotate_right']:
            direction = "左旋" if op_type == 'rotate_left' else "右旋"
            label_text = f"执行{direction}操作"
            label_color = "#1976D2"
        else:
            label_text = "执行平衡操作"
            label_color = "#388E3C"

        # 在相关节点上方显示说明
        z_id = event.get('z_id') or event.get('z')
        if z_id:
            zk = origid_to_key_before.get(z_id) or origid_to_key_after.get(z_id)
            if zk and zk in pos_before:
                zx, zy = pos_before[zk]
                label_id = self.canvas.create_text(zx, zy-50, text=label_text,
                                                 font=("微软雅黑", 10, "bold"),
                                                 fill=label_color)
        else:
            label_id = self.canvas.create_text(self.canvas_w/2, 30, text=label_text,
                                             font=("微软雅黑", 10, "bold"),
                                             fill=label_color)

        # 执行动画
        frames = 24
        delay = 25

        def frame_step(f=0):
            if f >= frames:
                self.draw_tree_from_root(after_root)
                if label_id:
                    try: 
                        self.canvas.delete(label_id)
                    except: 
                        pass
                self.window.after(350, on_done)
                return
                
            t = (f+1)/frames
            for (k, rect_id, text_id, sx, sy, tx, ty) in moves:
                cur_cx = sx + (tx - sx) * t
                cur_cy = sy + (ty - sy) * t
                
                try:
                    # 计算当前位置
                    coords = self.canvas.coords(rect_id)
                    if not coords or len(coords) < 4:
                        continue
                    x1, y1, x2, y2 = coords
                    current_cx = (x1 + x2) / 2
                    current_cy = (y1 + y2) / 2
                    
                    # 移动节点
                    dx = cur_cx - current_cx
                    dy = cur_cy - current_cy
                    self.canvas.move(rect_id, dx, dy)
                    self.canvas.move(text_id, dx, dy)
                except Exception:
                    pass
                    
            self.window.after(delay, lambda: frame_step(f+1))
            
        frame_step(0)

    def _animate_events_sequence(self, events: List[Dict], snapshots: List[Optional[RBNode]], insertion_index: int, on_all_done):
        """动画：事件序列"""
        if not events:
            on_all_done()
            return

        def step(i=0):
            if i >= len(events):
                on_all_done()
                return
                
            before_root = snapshots[1 + i]
            after_root = snapshots[2 + i]
            ev = events[i]
            
            self.update_status(f"平衡操作 {i+1}/{len(events)}: {ev.get('type', 'unknown')}")
            self._animate_single_event(before_root, after_root, ev, 
                                     lambda: step(i+1))
        step(0)

    def _after_insert_events(self, events, snapshots, insertion_idx):
        """插入后的事件处理"""
        if not events:
            self.draw_tree_from_root(clone_tree(self.model.root))
            self.window.after(400, lambda: self._insert_seq(insertion_idx+1))
            return

        def done_all():
            self.draw_tree_from_root(clone_tree(self.model.root))
            self.update_status(f"完成插入: {self.batch[insertion_idx]}")
            self.window.after(500, lambda: self._insert_seq(insertion_idx+1))
            
        self._animate_events_sequence(events, snapshots, insertion_idx, done_all)

    def clear_canvas(self):
        """清空画布"""
        if self.animating:
            messagebox.showinfo("提示", "请等待当前动画完成")
            return
            
        self.model = RBModel()
        self.node_vis.clear()
        self.canvas.delete("all")
        self.draw_instructions()
        self.update_status("已清空红黑树")

    def back_to_main(self):
        """返回主界面"""
        if messagebox.askyesno("确认", "确定要返回主界面吗？"):
            self.window.destroy()

    def save_structure(self):
        """保存结构"""
        root = self.model.root
        ok = storage.save_tree_to_file(root)
        if ok:
            self.update_status("树结构保存成功")
            messagebox.showinfo("成功", "红黑树结构已保存到文件")

    def load_structure(self):
        """加载结构"""
        if self.animating:
            messagebox.showinfo("提示", "请等待当前动画完成")
            return
            
        tree_dict = storage.load_tree_from_file()
        if not tree_dict:
            messagebox.showinfo("提示", "没有找到保存的树结构文件")
            return
            
        from rbt.rbt_model import RBNode as RBNodeClass
        newroot = storage.tree_dict_to_nodes(tree_dict, RBNodeClass)
        self.model.root = newroot
        self.draw_tree_from_root(clone_tree(self.model.root))
        self.update_status("已从文件加载红黑树结构")


if __name__ == '__main__':
    w = Tk()
    w.title("红黑树可视化演示系统")
    w.geometry("1350x750")
    
    # 设置窗口图标（如果有的话）
    try:
        w.iconbitmap("rbt_icon.ico")  # 如果有图标文件的话
    except:
        pass
        
    RBTVisualizer(w)
    w.mainloop()