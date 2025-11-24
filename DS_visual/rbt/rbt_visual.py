from tkinter import *
from tkinter import ttk
from tkinter import messagebox, filedialog
from typing import Dict, Tuple, List, Optional
from rbt.rbt_model import RBModel, RBNode, clone_tree
import storage as storage
from DSL_utils import process_command 
import time

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
            "delete_mark": "#2196F3",
            "text_light": "#FFFFFF",
            "text_dark": "#212121",
            "btn_primary": "#2196F3",
            "btn_success": "#4CAF50",
            "btn_warning": "#FF9800",
            "btn_danger": "#F44336",
            "canvas_bg": "#FAFAFA",
            "search_halo": "#FFC107",
            "rotation_guide": "#9C27B0",
            "case1_color": "#E91E63",
            "case2_color": "#9C27B0",
            "case3_color": "#3F51B5",
            "info_panel": "#FFF9C4",
            "knowledge_panel": "#E3F2FD"
        }
        
        # 动画控制变量
        self.animation_speed = 500  # 默认速度（毫秒）
        self.paused = False
        self.current_step = 0
        self.total_steps = 0
        
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
        
        # 临时动画对象存储
        self.temp_objects = []
        
        # 知识展示状态
        self.showing_welcome = True
        
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
                             text="演示红黑树的插入/删除过程:搜索路径、节点操作、颜色调整与旋转修复",
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
        
        # 动画速度控制
        speed_frame = Frame(canvas_toolbar, bg=self.colors["bg_secondary"])
        speed_frame.pack(side=RIGHT, padx=10)
        
        Label(speed_frame, text="速度:", font=("微软雅黑", 9), 
              bg=self.colors["bg_secondary"]).pack(side=LEFT, padx=(0, 5))
        
        self.speed_scale = Scale(speed_frame, from_=100, to=2000, orient=HORIZONTAL,
                                length=120, showvalue=False, command=self.update_speed,
                                bg=self.colors["bg_secondary"], highlightthickness=0)
        self.speed_scale.set(500)
        self.speed_scale.pack(side=LEFT)
        
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

        # 输入节点值
        Label(input_frame, text="输入节点值:",
            font=("微软雅黑", 10),
            bg=self.colors["bg_secondary"]).grid(row=0, column=0, sticky=W, padx=(0,6), pady=5)

        self.input_var = StringVar()
        self.input_entry = Entry(input_frame, textvariable=self.input_var,
                                font=("微软雅黑", 10), relief=SOLID, bd=1)
        self.input_entry.grid(row=0, column=1, padx=(0,12), pady=5, sticky=EW)
        self.input_entry.insert(0, "1,2,3,4,5,0,6")
        self.input_entry.bind("<Return>", lambda e: self.start_insert_animated())

        # DSL输入
        Label(input_frame, text="DSL命令:",
            font=("微软雅黑", 10),
            bg=self.colors["bg_secondary"]).grid(row=0, column=2, sticky=W, padx=(6,6), pady=5)

        self.dsl_var = StringVar()
        self.dsl_entry = Entry(input_frame, textvariable=self.dsl_var,
                            font=("微软雅黑", 10), relief=SOLID, bd=1)
        self.dsl_entry.grid(row=0, column=3, padx=(0,6), pady=5, sticky=EW)
        self.dsl_entry.insert(0, "create 1 2 3 4 5 0 6")
        self.dsl_entry.bind("<Return>", lambda e: self.execute_dsl())

        # DSL执行按钮
        self.execute_dsl_btn = Button(input_frame, text="执行DSL", command=self.execute_dsl,
                                    bg=self.colors["btn_primary"], fg="white",
                                    font=("微软雅黑", 9), relief=FLAT, bd=0, padx=10, pady=4,
                                    cursor="hand2")
        self.execute_dsl_btn.grid(row=0, column=4, padx=(6,0), pady=5, sticky=W)

        input_frame.columnconfigure(1, weight=1)
        input_frame.columnconfigure(3, weight=1)
        self.entry = self.input_entry

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
        self.create_button(btn_row1, "单节点插入 (动画)",
                        self.insert_single_node_animated, "#00ACC1").pack(side=LEFT, padx=4)
        self.create_button(btn_row1, "删除节点 (动画)",
                        self.start_delete_animated, self.colors["btn_danger"]).pack(side=LEFT, padx=4)
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
        
        # 第三行按钮 - 动画控制
        btn_row3 = Frame(btn_frame, bg=self.colors["bg_secondary"])
        btn_row3.pack(fill=X, pady=5)
        
        self.create_button(btn_row3, "暂停动画",
                        self.pause_animation, "#FF5722").pack(side=LEFT, padx=4)
        self.create_button(btn_row3, "继续动画",
                        self.resume_animation, "#4CAF50").pack(side=LEFT, padx=4)
        self.create_button(btn_row3, "下一步",
                        self.next_step, "#2196F3").pack(side=LEFT, padx=4)

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
        
        # 只在未开始动画时显示欢迎信息
        if self.showing_welcome:
            # 绘制欢迎信息
            welcome_text = "欢迎使用红黑树可视化演示系统\n\n" \
                          "功能说明:\n" \
                          "• 插入节点: 展示搜索路径和平衡过程\n" \
                          "• 删除节点: 展示删除过程和修复操作\n" \
                          "• 动画控制: 可暂停、继续和调整速度\n" \
                          "• 支持DSL命令批量操作\n\n" \
                          "请在左侧输入节点值开始演示"
            
            self.canvas.create_text(self.canvas_w/2, self.canvas_h/2 - 50, 
                                  text=welcome_text, font=("微软雅黑", 12), 
                                  fill="#666666", justify=CENTER)

    def draw_legend(self, y_pos):
        """绘制图例"""
        legend_items = [
            ("红节点", self.colors["red_node"]),
            ("黑节点", self.colors["black_node"]),
            ("搜索路径", self.colors["path_highlight"]),
            ("当前操作", self.colors["highlight"]),
            ("删除标记", self.colors["delete_mark"]),
            ("旋转指示", self.colors["rotation_guide"])
        ]
        
        x_pos = 20
        for text, color in legend_items:
            self.canvas.create_rectangle(x_pos, y_pos-8, x_pos+16, y_pos+8,
                                       fill=color, outline="#CCCCCC")
            self.canvas.create_text(x_pos+25, y_pos, text=text, 
                                  font=("微软雅黑", 9), anchor=W, fill="#666666")
            x_pos += 90

    def update_status(self, text: str):
        """更新状态栏"""
        self.status_label.config(text=text)
    
    def update_speed(self, value):
        """更新动画速度"""
        self.animation_speed = int(value)
    
    def pause_animation(self):
        """暂停动画"""
        self.paused = True
        self.update_status("动画已暂停")
    
    def resume_animation(self):
        """继续动画"""
        self.paused = False
        self.update_status("动画继续")
    
    def next_step(self):
        """执行下一步"""
        # 这里需要与具体的动画步骤配合使用
        pass
    
    def wait_if_paused(self):
        """如果暂停则等待"""
        while self.paused:
            self.window.update()
            time.sleep(0.1)
    
    def execute_dsl(self):
        """执行DSL命令"""
        cmd = self.dsl_var.get().strip()
        if not cmd:
            messagebox.showinfo("提示", "请输入DSL命令,例如:\n  create 1,2,3\n  delete 5\n  clear")
            return

        if process_command is None:
            messagebox.showerror("模块缺失", "未找到 DSL_utils 模块,无法执行 DSL 命令。")
            self.update_status("DSL 执行失败:缺少 DSL_utils")
            return

        try:
            result = process_command(self, cmd)
            if result is False:
                self.update_status(f"DSL 命令执行失败: {cmd}")
            else:
                self.update_status(f"DSL 命令已执行: {cmd}")
        except Exception as e:
            import traceback
            traceback.print_exc()
            messagebox.showerror("DSL 执行异常", f"执行 DSL 时发生异常:\n{e}")
            self.update_status("DSL 执行异常")

    def start_delete_animated(self):
        """开始删除节点动画"""
        if self.animating:
            messagebox.showinfo("提示", "当前正在执行动画,请稍候...")
            return
        
        if self.model.root is None:
            messagebox.showinfo("提示", "树为空,无法删除节点")
            return
        
        val_str = self.input_var.get().strip()
        if not val_str:
            messagebox.showinfo("提示", "请输入要删除的节点值")
            return
        
        # 只取第一个值
        values = [v.strip() for v in val_str.split(",") if v.strip()]
        if not values:
            messagebox.showinfo("提示", "请输入有效的节点值")
            return
        
        val = values[0]
        
        try:
            int(val)
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")
            return
        
        # 开始动画，移除欢迎文字
        self.showing_welcome = False
        self.animating = True
        self.update_status(f"开始删除节点: {val}")
        
        # 显示操作说明
        self.show_operation_explanation("delete", f"开始删除节点 {val}")
        
        # 调用删除方法
        deleted_node, path_nodes, events, snapshots = self.model.delete_with_steps(val)
        
        if deleted_node is None:
            self.animating = False
            messagebox.showinfo("提示", f"节点 {val} 不存在")
            self.update_status(f"删除失败: 节点 {val} 不存在")
            return
        
        snap_pre = snapshots[0]
        snap_after_delete = snapshots[1] if len(snapshots) > 1 else None
        
        # 显示红黑树删除知识
        self.show_rb_delete_knowledge()
        
        # 高亮搜索路径
        def highlight_path(i=0):
            if i >= len(path_nodes):
                self.update_status(f"找到节点 {val}, 准备删除")
                self.show_operation_explanation("delete", f"已定位到节点 {val}, 开始删除操作")
                self.animate_delete_node(val, deleted_node, snap_after_delete,
                                       lambda: self._after_delete_events(events, snapshots, val))
                return
            
            self.wait_if_paused()
            
            node = path_nodes[i]
            self.draw_tree_from_root(snap_pre)
            
            # 高亮当前访问的节点
            origid_to_key, _ = self._build_key_maps_from_root(snap_pre)
            node_id = getattr(node, 'id', None)
            key = origid_to_key.get(node_id)
            
            if key and key in self.node_vis:
                try:
                    # 如果是目标节点,用删除标记颜色
                    if str(node.val) == str(val):
                        self.canvas.itemconfig(self.node_vis[key]['rect'],
                                             outline=self.colors["delete_mark"],
                                             width=4)
                        # 添加闪烁效果
                        self.flash_node(key, self.colors["delete_mark"])
                    else:
                        self.canvas.itemconfig(self.node_vis[key]['rect'],
                                             outline=self.colors["path_highlight"],
                                             width=3)
                        # 添加搜索光晕
                        self.create_search_halo(key)
                except Exception:
                    pass
            
            self.update_status(f"搜索路径: 访问节点 {node.val} (步骤 {i+1})")
            self.window.after(max(100, self.animation_speed), lambda: highlight_path(i+1))
        
        highlight_path(0)

    def animate_delete_node(self, val_str: str, deleted_node, snap_after_delete, on_complete):
        """删除节点的淡出动画"""
        if not snap_after_delete:
            # 如果删除后树为空
            self.canvas.delete("all")
            self.draw_instructions()
            self.update_status(f"已删除节点 {val_str}, 树已为空")
            self.window.after(400, on_complete)
            return
        
        # 找到被删除节点的可视化键
        snap_before = clone_tree(self.model.root) if self.model.root else None
        if not snap_before:
            on_complete()
            return
        
        origid_to_key, _ = self._build_key_maps_from_root(snap_before)
        deleted_id = getattr(deleted_node, 'id', None)
        deleted_key = origid_to_key.get(deleted_id)
        
        if not deleted_key or deleted_key not in self.node_vis:
            # 无法找到节点,直接完成
            self.draw_tree_from_root(snap_after_delete)
            on_complete()
            return
        
        # 显示删除动画说明
        self.show_operation_explanation("delete", f"正在删除节点 {val_str}")
        
        # 淡出动画
        node_item = self.node_vis[deleted_key]
        rect_id = node_item['rect']
        text_id = node_item['text']
        color_label = node_item['color_label']
        
        steps = 20
        delay = max(10, self.animation_speed // 30)
        
        def fade_step(i=0):
            if i >= steps:
                # 删除完成,重绘树
                self.draw_tree_from_root(snap_after_delete)
                self.update_status(f"节点 {val_str} 已删除")
                self.window.after(max(100, self.animation_speed), on_complete)
                return
            
            self.wait_if_paused()
            
            # 计算透明度 (通过颜色变淡模拟)
            alpha = 1 - (i / steps)
            
            try:
                # 获取当前颜色并调整亮度
                if hasattr(deleted_node, 'color') and deleted_node.color == "R":
                    base_color = self.colors["red_node"]
                else:
                    base_color = self.colors["black_node"]
                
                # 简单的淡出效果:逐渐变成背景色
                bg_color = self.colors["canvas_bg"]
                
                # 逐渐缩小
                scale = alpha
                cx = node_item['cx']
                cy = node_item['cy']
                new_w = self.node_w * scale
                new_h = self.node_h * scale
                
                left = cx - new_w/2
                right = cx + new_w/2
                top = cy - new_h/2
                bottom = cy + new_h/2
                
                self.canvas.coords(rect_id, left, top, right, bottom)
                
                # 逐渐变透明
                if i > steps/2:
                    self.canvas.itemconfig(text_id, state=HIDDEN)
                    self.canvas.itemconfig(color_label, state=HIDDEN)
                
            except Exception:
                pass
            
            self.window.after(delay, lambda: fade_step(i+1))
        
        fade_step(0)

    def _after_delete_events(self, events, snapshots, val):
        """删除后的修复事件处理"""
        if not events or len(snapshots) <= 2:
            # 没有修复事件,直接完成
            self.draw_tree_from_root(clone_tree(self.model.root))
            self.animating = False
            self.update_status(f"完成删除: {val}")
            self.show_operation_explanation("delete", f"节点 {val} 删除完成")
            return
        
        def done_all():
            self.draw_tree_from_root(clone_tree(self.model.root))
            self.animating = False
            self.update_status(f"完成删除并修复平衡: {val}")
            self.show_operation_explanation("delete", f"节点 {val} 删除完成, 树已重新平衡")
        
        # 从索引2开始(0是删除前,1是删除后删除修复前)
        self._animate_delete_events_sequence(events, snapshots, 2, done_all)

    def _animate_delete_events_sequence(self, events, snapshots, start_idx, on_done):
        """删除修复事件序列动画"""
        if not events:
            on_done()
            return
        
        def step(event_idx=0, snap_idx=start_idx):
            if event_idx >= len(events):
                on_done()
                return
            
            self.wait_if_paused()
            
            # 确保有足够的快照
            if snap_idx >= len(snapshots) or snap_idx + 1 >= len(snapshots):
                on_done()
                return
            
            before_root = snapshots[snap_idx]
            after_root = snapshots[snap_idx + 1]
            ev = events[event_idx]
            
            # 显示修复操作说明
            op_type = ev.get('type', 'unknown')
            explanation = self.get_operation_explanation(op_type)
            self.show_operation_explanation("fixup", explanation)
            
            # 显示具体的红黑树删除修复知识
            if event_idx == 0:
                self.show_rb_delete_fixup_knowledge()
            
            self.update_status(f"删除修复 {event_idx+1}/{len(events)}: {op_type}")
            self._animate_single_event(before_root, after_root, ev,
                                     lambda: step(event_idx+1, snap_idx+1))
        
        step(0, start_idx)

    def insert_single_node_animated(self):
        """单节点插入(带动画)"""
        if self.animating:
            messagebox.showinfo("提示", "当前正在执行动画,请稍候...")
            return
        
        val_str = self.input_var.get().strip()
        if not val_str:
            messagebox.showinfo("提示", "请输入要插入的单个节点值")
            return
        
        values = [v.strip() for v in val_str.split(",") if v.strip()]
        if len(values) != 1:
            messagebox.showwarning("提示", "单节点插入模式只能输入一个节点值\n如需插入多个节点,请使用批量插入功能")
            return
        
        val = values[0]
        
        try:
            int(val)
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")
            return
        
        # 开始动画，移除欢迎文字
        self.showing_welcome = False
        self.animating = True
        self.show_operation_explanation("insert", f"开始插入节点 {val}")
        
        # 显示红黑树插入知识
        self.show_rb_insert_knowledge()
        
        inserted_node, path_nodes, events, snapshots = self.model.insert_with_steps(val)
        
        snap_pre = snapshots[0]
        snap_after_insert = snapshots[1] if len(snapshots) > 1 else None
        
        pos_pre = self.compute_positions_for_root(snap_pre)
        origid_to_key_pre, _ = self._build_key_maps_from_root(snap_pre)
        
        def highlight_path(i=0):
            if i >= len(path_nodes):
                self.update_status(f"插入 {val}: 定位插入位置")
                self.show_operation_explanation("insert", f"已找到插入位置, 准备插入节点 {val}")
                self.animate_flyin_new(val, snap_after_insert, 
                                     lambda: self._after_insert_events_single(events, snapshots, val))
                return
            
            self.wait_if_paused()
            
            node = path_nodes[i]
            node_id = getattr(node, 'id', None)
            key = origid_to_key_pre.get(node_id)
            self.draw_tree_from_root(snap_pre)
            
            if key:
                try:
                    self.canvas.itemconfig(self.node_vis[key]['rect'], 
                                         outline=self.colors["path_highlight"], 
                                         width=3)
                    # 添加搜索光晕
                    self.create_search_halo(key)
                except Exception:
                    pass
            
            self.update_status(f"搜索路径: 访问节点 {node.val} (步骤 {i+1})")
            self.window.after(max(100, self.animation_speed), lambda: highlight_path(i+1))
        
        highlight_path(0)

    def _after_insert_events_single(self, events, snapshots, val):
        """单节点插入后的事件处理"""
        if not events:
            self.draw_tree_from_root(clone_tree(self.model.root))
            self.animating = False
            self.update_status(f"完成单节点插入: {val}")
            self.show_operation_explanation("insert", f"节点 {val} 插入完成")
            return
        
        def done_all():
            self.draw_tree_from_root(clone_tree(self.model.root))
            self.animating = False
            self.update_status(f"完成单节点插入: {val}")
            self.show_operation_explanation("insert", f"节点 {val} 插入完成, 树已重新平衡")
        
        self._animate_events_sequence(events, snapshots, 0, done_all)

    def _draw_connection(self, cx, cy, tx, ty):
        """绘制节点连接线"""
        top = cy + self.node_h/2
        bot = ty - self.node_h/2
        midy = (top + bot) / 2
        
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
        # 不再绘制欢迎文字
        self.showing_welcome = False
        
        # 绘制图例
        legend_y = self.canvas_h - 30
        self.draw_legend(legend_y)
        
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
        
        is_red = node.color == "R"
        fill_color = self.colors["red_node"] if is_red else self.colors["black_node"]
        text_color = self.colors["text_light"] if not is_red else self.colors["text_dark"]
        
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
            messagebox.showinfo("提示", "当前正在执行动画,请稍候...")
            return
            
        if not self.validate_input():
            return
            
        # 开始动画，移除欢迎文字
        self.showing_welcome = False
        self.animating = True
        self.batch = [p.strip() for p in self.input_var.get().split(",") if p.strip()]
        self.show_operation_explanation("insert", f"开始批量插入 {len(self.batch)} 个节点")
        
        # 显示红黑树插入知识
        self.show_rb_insert_knowledge()
        
        self._insert_seq(0)

    def insert_direct(self):
        """直接插入(无动画)"""
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
            messagebox.showinfo("提示", "请输入数字,用逗号分隔\n例如:10, 5, 20, 15, 30")
            return False
            
        try:
            values = [p.strip() for p in s.split(",") if p.strip()]
            for val in values:
                int(val)
        except ValueError:
            messagebox.showerror("错误", "输入包含非数字内容,请确保只输入数字")
            return False
            
        return True
    
    def _compare_values(self, val1, val2):
        """比较两个值的大小(按整数比较)"""
        try:
            return int(val1) < int(val2)
        except (ValueError, TypeError):
            return str(val1) < str(val2)

    def _insert_seq(self, idx: int):
        """插入序列"""
        if idx >= len(self.batch):
            self.animating = False
            self.update_status("所有插入操作已完成")
            self.show_operation_explanation("insert", "所有节点插入完成")
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
                self.show_operation_explanation("insert", f"准备插入节点 {val}")
                self.animate_flyin_new(val, snap_after_insert, 
                                     lambda: self._after_insert_events(events, snapshots, idx))
                return
                
            self.wait_if_paused()
            
            node = path_nodes[i]
            node_id = getattr(node, 'id', None)
            key = origid_to_key_pre.get(node_id)
            self.draw_tree_from_root(snap_pre)
            
            if key:
                try:
                    self.canvas.itemconfig(self.node_vis[key]['rect'], 
                                         outline=self.colors["path_highlight"], 
                                         width=3)
                    # 添加搜索光晕
                    self.create_search_halo(key)
                except Exception:
                    pass
                    
            self.update_status(f"搜索路径: 访问节点 {node.val} (步骤 {i+1})")
            self.window.after(max(100, self.animation_speed), lambda: highlight_path(i+1))

        highlight_path(0)

    def animate_flyin_new(self, val_str: str, snap_after_insert: Optional[RBNode], on_complete):
        """动画:新节点飞入"""
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

        # 起始位置
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
        
        # 添加到临时对象列表
        self.temp_objects.extend([temp_rect, temp_text])

        # 动画参数
        steps = 30
        dx = (tx - sx)/steps
        dy = (ty - sy)/steps
        delay = max(10, self.animation_speed // 30)
        
        def step(i=0):
            if i < steps:
                self.wait_if_paused()
                
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
                    # 从临时对象列表中移除
                    self.temp_objects = [obj for obj in self.temp_objects 
                                       if obj not in [temp_rect, temp_text]]
                except Exception:
                    pass
                    
                self.draw_tree_from_root(snap_after_insert)
                try:
                    self.canvas.itemconfig(self.node_vis[target_key]['rect'], 
                                         outline=self.colors["highlight"], 
                                         width=3)
                    # 添加插入完成闪烁
                    self.flash_node(target_key, self.colors["highlight"])
                except Exception:
                    pass
                    
                self.window.after(max(100, self.animation_speed), on_complete)
        step()

    def _animate_single_event(self, before_root: Optional[RBNode], after_root: Optional[RBNode], event: Dict, on_done):
        """动画:单步操作"""
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
            label_text = "颜色调整: 重新着色"
            label_color = "#D32F2F"
            # 显示颜色变化动画
            self.animate_color_change(event, before_root, after_root)
            # 显示红黑树颜色知识
            self.show_rb_color_knowledge()
        elif op_type in ['rotate_left', 'rotate_right']:
            direction = "左旋" if op_type == 'rotate_left' else "右旋"
            label_text = f"执行{direction}操作"
            label_color = "#1976D2"
            # 显示旋转指示
            self.show_rotation_guide(event, before_root)
            # 显示红黑树旋转知识
            self.show_rb_rotation_knowledge(direction)
        else:
            label_text = "执行平衡操作"
            label_color = "#388E3C"

        # 在画布顶部显示说明
        label_id = self.canvas.create_text(self.canvas_w/2, 30, text=label_text,
                                         font=("微软雅黑", 10, "bold"),
                                         fill=label_color)
        self.temp_objects.append(label_id)

        # 执行动画
        frames = 24
        delay = max(10, self.animation_speed // 20)

        def frame_step(f=0):
            if f >= frames:
                self.draw_tree_from_root(after_root)
                # 清理临时对象
                for obj in self.temp_objects:
                    try: 
                        self.canvas.delete(obj)
                    except: 
                        pass
                self.temp_objects.clear()
                self.window.after(max(100, self.animation_speed), on_done)
                return
                
            self.wait_if_paused()
            
            t = (f+1)/frames
            for (k, rect_id, text_id, sx, sy, tx, ty) in moves:
                cur_cx = sx + (tx - sx) * t
                cur_cy = sy + (ty - sy) * t
                
                try:
                    coords = self.canvas.coords(rect_id)
                    if not coords or len(coords) < 4:
                        continue
                    x1, y1, x2, y2 = coords
                    current_cx = (x1 + x2) / 2
                    current_cy = (y1 + y2) / 2
                    
                    dx = cur_cx - current_cx
                    dy = cur_cy - current_cy
                    self.canvas.move(rect_id, dx, dy)
                    self.canvas.move(text_id, dx, dy)
                except Exception:
                    pass
                    
            self.window.after(delay, lambda: frame_step(f+1))
            
        frame_step(0)

    def _animate_events_sequence(self, events: List[Dict], snapshots: List[Optional[RBNode]], insertion_index: int, on_all_done):
        """动画:事件序列"""
        if not events:
            on_all_done()
            return

        def step(i=0):
            if i >= len(events):
                on_all_done()
                return
                
            self.wait_if_paused()
            
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
            self.window.after(max(100, self.animation_speed), lambda: self._insert_seq(insertion_idx+1))
            return

        def done_all():
            self.draw_tree_from_root(clone_tree(self.model.root))
            self.update_status(f"完成插入: {self.batch[insertion_idx]}")
            self.window.after(max(100, self.animation_speed), lambda: self._insert_seq(insertion_idx+1))
            
        self._animate_events_sequence(events, snapshots, insertion_idx, done_all)

    def clear_canvas(self):
        """清空画布"""
        if self.animating:
            messagebox.showinfo("提示", "请等待当前动画完成")
            return
            
        self.model = RBModel()
        self.node_vis.clear()
        self.canvas.delete("all")
        self.showing_welcome = True  # 重置欢迎文字显示状态
        self.draw_instructions()
        self.update_status("已清空红黑树")

    def back_to_main(self):
        """返回主界面"""
        if messagebox.askyesno("确认", "确定要返回主界面吗?"):
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
        self.showing_welcome = False  # 加载结构后不显示欢迎文字
        self.draw_tree_from_root(clone_tree(self.model.root))
        self.update_status("已从文件加载红黑树结构")

    # ===== 新增的动画效果方法 =====
    
    def create_search_halo(self, node_key):
        """创建搜索光晕效果"""
        if node_key not in self.node_vis:
            return
            
        node = self.node_vis[node_key]
        cx, cy = node['cx'], node['cy']
        
        # 创建光晕圆圈
        halo = self.canvas.create_oval(cx-25, cy-25, cx+25, cy+25,
                                     outline=self.colors["search_halo"],
                                     width=2, dash=(5, 2))
        self.temp_objects.append(halo)
        
        # 光晕动画
        def animate_halo(step=0):
            if step < 3:  # 闪烁3次
                if step % 2 == 0:
                    self.canvas.itemconfig(halo, state=HIDDEN)
                else:
                    self.canvas.itemconfig(halo, state=NORMAL)
                self.window.after(200, lambda: animate_halo(step+1))
            else:
                try:
                    self.canvas.delete(halo)
                    self.temp_objects.remove(halo)
                except:
                    pass
                    
        animate_halo()

    def flash_node(self, node_key, color):
        """节点闪烁效果"""
        if node_key not in self.node_vis:
            return
            
        node = self.node_vis[node_key]
        rect = node['rect']
        original_width = 2
        
        def flash(step=0):
            if step < 6:  # 闪烁3次
                if step % 2 == 0:
                    self.canvas.itemconfig(rect, outline=color, width=4)
                else:
                    self.canvas.itemconfig(rect, outline="#E0E0E0", width=original_width)
                self.window.after(150, lambda: flash(step+1))
            else:
                self.canvas.itemconfig(rect, outline="#E0E0E0", width=original_width)
                
        flash()

    def show_operation_explanation(self, operation_type, text):
        """显示操作说明"""
        # 清除之前的说明
        for obj in self.temp_objects:
            if "explanation" in str(obj):
                try:
                    self.canvas.delete(obj)
                except:
                    pass
        
        # 创建说明面板
        panel = self.canvas.create_rectangle(20, 20, 400, 80,
                                           fill=self.colors["info_panel"],
                                           outline="#FFC107", width=2)
        text_id = self.canvas.create_text(30, 30, text=text, 
                                        font=("微软雅黑", 10), anchor=NW, width=360,
                                        fill="#333333")
        
        # 标记为说明对象
        self.canvas.addtag_withtag("explanation", panel)
        self.canvas.addtag_withtag("explanation", text_id)
        
        self.temp_objects.extend([panel, text_id])

    def get_operation_explanation(self, operation_type):
        """获取操作说明文本"""
        explanations = {
            'recolor': '颜色调整: 重新着色节点以保持红黑树性质',
            'rotate_left': '左旋操作: 调整树结构保持平衡',
            'rotate_right': '右旋操作: 调整树结构保持平衡',
            'root_recolor': '根节点重着色: 确保根节点为黑色'
        }
        return explanations.get(operation_type, '执行平衡操作')

    def show_rotation_guide(self, event, before_root):
        """显示旋转指示"""
        pivot_id = event.get('x_id')
        if not pivot_id:
            return
            
        origid_to_key, _ = self._build_key_maps_from_root(before_root)
        pivot_key = origid_to_key.get(pivot_id)
        
        if pivot_key and pivot_key in self.node_vis:
            node = self.node_vis[pivot_key]
            cx, cy = node['cx'], node['cy']
            
            # 根据旋转类型显示方向指示
            if event.get('type') == 'rotate_left':
                # 左旋指示 - 逆时针箭头
                arrow = self.canvas.create_line(cx, cy-30, cx-20, cy-10, cx-10, cy-10,
                                              arrow=LAST, fill=self.colors["rotation_guide"],
                                              width=3)
                text = self.canvas.create_text(cx-30, cy-15, text="左旋", 
                                             font=("微软雅黑", 9, "bold"),
                                             fill=self.colors["rotation_guide"])
            else:
                # 右旋指示 - 顺时针箭头  
                arrow = self.canvas.create_line(cx, cy-30, cx+20, cy-10, cx+10, cy-10,
                                              arrow=LAST, fill=self.colors["rotation_guide"],
                                              width=3)
                text = self.canvas.create_text(cx+30, cy-15, text="右旋", 
                                             font=("微软雅黑", 9, "bold"),
                                             fill=self.colors["rotation_guide"])
            
            self.temp_objects.extend([arrow, text])

    def animate_color_change(self, event, before_root, after_root):
        """颜色变化动画"""
        node_id = event.get('node_id')
        if not node_id:
            return
            
        origid_to_key, _ = self._build_key_maps_from_root(before_root)
        node_key = origid_to_key.get(node_id)
        
        if node_key and node_key in self.node_vis:
            node = self.node_vis[node_key]
            rect = node['rect']
            
            # 获取新旧颜色
            old_color = self.canvas.itemcget(rect, "fill")
            new_color = self.colors["red_node"] if event.get('new_color') == 'R' else self.colors["black_node"]
            
            # 颜色过渡动画
            steps = 10
            delay = max(10, self.animation_speed // 30)
            
            def color_transition(step=0):
                if step <= steps:
                    # 计算过渡颜色
                    ratio = step / steps
                    if old_color == self.colors["red_node"] and new_color == self.colors["black_node"]:
                        # 红变黑
                        r = int(255 * (1 - ratio))
                        g = int(82 * (1 - ratio))
                        b = int(82 * (1 - ratio))
                    else:
                        # 黑变红
                        r = int(55 + 200 * ratio)
                        g = int(71 + 184 * ratio)
                        b = int(79 + 173 * ratio)
                    
                    transition_color = f"#{r:02x}{g:02x}{b:02x}"
                    self.canvas.itemconfig(rect, fill=transition_color)
                    self.window.after(delay, lambda: color_transition(step + 1))
                else:
                    # 确保最终颜色正确
                    self.canvas.itemconfig(rect, fill=new_color)
            
            color_transition()

    # ===== 红黑树知识展示方法 =====
    
    def show_rb_insert_knowledge(self):
        """显示红黑树插入知识"""
        knowledge_text = (
            "红黑树插入知识:\n"
            "• 新插入的节点默认为红色\n"
            "• 如果父节点是黑色，插入完成\n"
            "• 如果父节点是红色，需要修复:\n"
            "  - Case 1: 叔叔节点是红色\n"
            "  - Case 2: 叔叔节点是黑色，当前节点是右孩子\n" 
            "  - Case 3: 叔叔节点是黑色，当前节点是左孩子"
        )
        self.show_knowledge_panel(knowledge_text)
    
    def show_rb_delete_knowledge(self):
        """显示红黑树删除知识"""
        knowledge_text = (
            "红黑树删除知识:\n"
            "• 删除红色节点通常不会破坏性质\n"
            "• 删除黑色节点需要修复平衡\n"
            "• 修复过程涉及兄弟节点的颜色判断\n"
            "• 可能需要重新着色和旋转操作"
        )
        self.show_knowledge_panel(knowledge_text)
    
    def show_rb_delete_fixup_knowledge(self):
        """显示红黑树删除修复知识"""
        knowledge_text = (
            "删除修复的四种情况:\n"
            "• Case 1: 兄弟节点是红色\n"
            "• Case 2: 兄弟节点是黑色，兄弟的两个子节点都是黑色\n"
            "• Case 3: 兄弟节点是黑色，兄弟的左孩子红色，右孩子黑色\n"
            "• Case 4: 兄弟节点是黑色，兄弟的右孩子红色"
        )
        self.show_knowledge_panel(knowledge_text)
    
    def show_rb_color_knowledge(self):
        """显示红黑树颜色知识"""
        knowledge_text = (
            "红黑树颜色性质:\n"
            "1. 每个节点是红色或黑色\n"
            "2. 根节点是黑色的\n"
            "3. 所有叶子节点(NIL)是黑色的\n"
            "4. 红色节点的两个子节点都是黑色的\n"
            "5. 从任一节点到其每个叶子的所有路径都包含相同数目的黑色节点"
        )
        self.show_knowledge_panel(knowledge_text)
    
    def show_rb_rotation_knowledge(self, direction):
        """显示红黑树旋转知识"""
        if direction == "左旋":
            knowledge_text = (
                "左旋操作:\n"
                "• 以某个节点为支点进行旋转\n"
                "• 右子节点成为新的父节点\n"
                "• 原父节点成为新父节点的左子节点\n"
                "• 新父节点的左子树成为原父节点的右子树"
            )
        else:
            knowledge_text = (
                "右旋操作:\n"
                "• 以某个节点为支点进行旋转\n"
                "• 左子节点成为新的父节点\n"
                "• 原父节点成为新父节点的右子节点\n"
                "• 新父节点的右子树成为原父节点的左子树"
            )
        self.show_knowledge_panel(knowledge_text)
    
    def show_knowledge_panel(self, text):
        """显示知识面板"""
        # 清除之前的知识面板
        for obj in self.temp_objects:
            if "knowledge" in str(obj):
                try:
                    self.canvas.delete(obj)
                except:
                    pass
        
        # 创建知识面板
        panel = self.canvas.create_rectangle(
            self.canvas_w - 350, 20, self.canvas_w - 20, 180,
            fill=self.colors["knowledge_panel"],
            outline="#2196F3", width=2
        )
        text_id = self.canvas.create_text(
            self.canvas_w - 340, 30, text=text,
            font=("微软雅黑", 9), anchor=NW, width=320,
            fill="#333333", justify=LEFT
        )
        
        # 标记为知识对象
        self.canvas.addtag_withtag("knowledge", panel)
        self.canvas.addtag_withtag("knowledge", text_id)
        
        self.temp_objects.extend([panel, text_id])


if __name__ == '__main__':
    w = Tk()
    w.title("红黑树可视化演示系统")
    w.geometry("1350x750")
    
    try:
        w.iconbitmap("rbt_icon.ico")
    except:
        pass
        
    RBTVisualizer(w)
    w.mainloop()