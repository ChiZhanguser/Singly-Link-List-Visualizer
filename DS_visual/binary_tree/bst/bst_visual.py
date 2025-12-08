from tkinter import *
from tkinter import messagebox
from tkinter import Toplevel, filedialog
from typing import Dict, Tuple, List, Optional
from binary_tree.bst.bst_model import BSTModel, TreeNode
import storage as storage
import json
from datetime import datetime
import os
import time
import math
from DSL_utils import process_command
from binary_tree.bst.bst_ui import draw_instructions, create_controls

class BSTVisualizer:
    def __init__(self, root):
        self.window = root
        self.window.title("🌳 二叉搜索树可视化系统")
        self.window.config(bg="#F0F2F5")
        
        # 颜色配置
        self.colors = {
            "bg_primary": "#F0F2F5",
            "bg_secondary": "#FFFFFF",
            "canvas_bg": "#FAFAFA",
            "node_default": "#E3F2FD",
            "node_highlight": "#FFEB3B",
            "node_success": "#C8E6C9",
            "node_warning": "#FFCDD2",
            "node_info": "#B3E5FC",
            "node_comparing": "#FFD54F",  # 正在比较的节点
            "node_visited": "#90CAF9",    # 已访问的节点
            "node_target": "#EF5350",     # 目标节点
            "node_successor": "#81C784",  # 后继节点
            "pointer_color": "#E91E63",   # 指针颜色
            "arrow_color": "#FF5722",     # 比较箭头颜色
            "connection_new": "#4CAF50",  # 新连接线颜色
            "text_primary": "#212121",
            "text_secondary": "#666666",
            "btn_primary": "#2196F3",
            "btn_success": "#4CAF50",
            "btn_warning": "#FF9800",
            "btn_danger": "#F44336",
            "btn_info": "#9C27B0",
            "status_success": "#2E7D32",
            "status_error": "#C62828",
            "guide_bg": "#FFFDE7"
        }
        
        # 伪代码相关变量（需要在创建面板前初始化）
        self.pseudo_code_lines = []
        self.current_highlight_line = -1
        self.animation_speed = 0.03
        
        # 动画辅助元素ID列表（用于清理）
        self.animation_elements: List[int] = []
        self.comparison_box_id: Optional[int] = None
        self.pointer_id: Optional[int] = None
        self.arrow_ids: List[int] = []
        
        # 初始化核心属性
        self.canvas_width = 950
        self.canvas_height = 480
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
        self.level_gap = 80  # 减小垂直间距
        self.margin_x = 40

        # 动画和引导模式状态
        self.animating = False
        self.guide_mode = BooleanVar(value=True)  # 提前初始化

        # 输入变量
        self.input_var = StringVar()
        self.dsl_var = StringVar()
        
        # 创建主框架
        self.main_frame = Frame(self.window, bg=self.colors["bg_primary"])
        self.main_frame.pack(fill=BOTH, expand=True, padx=12, pady=12)
        
        # 按正确顺序创建UI组件 - 控制面板在顶部
        self.create_header()
        self.create_control_panel()  # 先创建控制面板
        self.create_canvas_area()    # 再创建画布区域
        
        # 绘制初始界面
        self.redraw()
        
    def create_header(self):
        """创建标题区域"""
        header_frame = Frame(self.main_frame, bg=self.colors["bg_secondary"], 
                           relief=RAISED, bd=1)
        header_frame.pack(fill=X, pady=(0, 8))
        
        title_label = Label(header_frame, text="🌳 二叉搜索树可视化系统", 
                          font=("微软雅黑", 16, "bold"), 
                          bg=self.colors["bg_secondary"],
                          fg=self.colors["text_primary"],
                          pady=10)
        title_label.pack()
        
        subtitle_label = Label(header_frame, 
                             text="动态演示BST的插入、查找、删除操作，支持分步引导和动画展示",
                             font=("微软雅黑", 10), 
                             bg=self.colors["bg_secondary"],
                             fg=self.colors["text_secondary"])
        subtitle_label.pack(pady=(0, 8))

    def create_control_panel(self):
        """创建控制面板 - 放在顶部"""
        control_frame = Frame(self.main_frame, bg=self.colors["bg_secondary"],
                            relief=SOLID, bd=1)
        control_frame.pack(fill=X, pady=(0, 8))
        
        # 输入区域
        input_frame = Frame(control_frame, bg=self.colors["bg_secondary"])
        input_frame.pack(fill=X, padx=15, pady=8)
        
        Label(input_frame, text="节点值:", 
              font=("微软雅黑", 10), 
              bg=self.colors["bg_secondary"]).grid(row=0, column=0, sticky=W, pady=4)
        
        self.entry = Entry(input_frame, textvariable=self.input_var, 
                          width=25, font=("微软雅黑", 10),
                          relief=SOLID, bd=1)
        self.entry.grid(row=0, column=1, padx=8, pady=4, sticky=W)
        self.entry.insert(0, "15,6,23,4,7,71,5")
        
        # DSL输入区域
        Label(input_frame, text="DSL命令:", 
              font=("微软雅黑", 10), 
              bg=self.colors["bg_secondary"]).grid(row=0, column=2, sticky=W, pady=4, padx=(20,0))
        
        self.dsl_entry = Entry(input_frame, textvariable=self.dsl_var,
                              width=15, font=("微软雅黑", 10),
                              relief=SOLID, bd=1)
        self.dsl_entry.grid(row=0, column=3, padx=8, pady=4, sticky=W)
        self.dsl_entry.bind("<Return>", self.process_dsl)
        
        # 按钮区域 - 两行按钮
        btn_frame = Frame(control_frame, bg=self.colors["bg_secondary"])
        btn_frame.pack(fill=X, padx=15, pady=8)
        
        # 第一行按钮 - 主要操作
        btn_row1 = Frame(btn_frame, bg=self.colors["bg_secondary"])
        btn_row1.pack(fill=X, pady=4)
        
        self.create_button(btn_row1, "✨ 插入节点", 
                         self.insert_direct, self.colors["btn_success"]).pack(side=LEFT, padx=2)
        self.create_button(btn_row1, "🎬 动画插入", 
                         self.start_insert_animated, "#009688").pack(side=LEFT, padx=2)
        self.create_button(btn_row1, "🔍 查找节点", 
                         self.start_search_animated, self.colors["btn_primary"]).pack(side=LEFT, padx=2)
        self.create_button(btn_row1, "🗑️ 删除节点", 
                         self.start_delete_animated, self.colors["btn_danger"]).pack(side=LEFT, padx=2)
        
        # 第二行按钮 - 辅助操作
        btn_row2 = Frame(btn_frame, bg=self.colors["bg_secondary"])
        btn_row2.pack(fill=X, pady=4)
        
        self.create_button(btn_row2, "💾 保存结构", 
                         self.save_tree, "#9C27B0").pack(side=LEFT, padx=2)
        self.create_button(btn_row2, "📂 加载结构", 
                         self.load_tree, "#9C27B0").pack(side=LEFT, padx=2)
        self.create_button(btn_row2, "🧹 清空树", 
                         self.clear_canvas, self.colors["btn_warning"]).pack(side=LEFT, padx=2)
        self.create_button(btn_row2, "🚪 返回主界面", 
                         self.back_to_main, "#795548").pack(side=LEFT, padx=2)
        self.create_button(btn_row2, "⚡ 执行DSL", 
                         self.process_dsl, "#607D8B").pack(side=LEFT, padx=2)
        
        # 配置网格权重
        input_frame.columnconfigure(1, weight=1)

    def create_canvas_area(self):
        """创建画布区域 - 放在控制面板下方"""
        # 主内容区域（画布 + 伪代码面板）
        content_frame = Frame(self.main_frame, bg=self.colors["bg_secondary"])
        content_frame.pack(fill=BOTH, expand=True, pady=(0, 8))
        
        # 左侧画布容器
        canvas_container = Frame(content_frame, bg=self.colors["bg_secondary"],
                               relief=SOLID, bd=1)
        canvas_container.pack(side=LEFT, fill=BOTH, expand=True)
        
        # 画布控制栏
        canvas_toolbar = Frame(canvas_container, bg=self.colors["bg_secondary"], height=28)
        canvas_toolbar.pack(fill=X, padx=10, pady=6)
        canvas_toolbar.pack_propagate(False)
        
        self.status_label = Label(canvas_toolbar, text="🟢 就绪", 
                                font=("微软雅黑", 10), 
                                bg=self.colors["bg_secondary"],
                                fg=self.colors["status_success"],
                                anchor=W)
        self.status_label.pack(side=LEFT, fill=X, expand=True)
        
        # 引导模式复选框
        self.guide_check = Checkbutton(canvas_toolbar, text="启用分步引导模式", 
                                      variable=self.guide_mode,
                                      bg=self.colors["bg_secondary"],
                                      font=("微软雅黑", 9),
                                      command=self._on_guide_mode_changed)
        self.guide_check.pack(side=RIGHT, padx=10)
        
        # 创建画布框架（带滚动条）
        canvas_frame = Frame(canvas_container)
        canvas_frame.pack(padx=10, pady=(0, 8), fill=BOTH, expand=True)
        
        # 添加垂直滚动条
        vscrollbar = Scrollbar(canvas_frame, orient=VERTICAL)
        vscrollbar.pack(side=RIGHT, fill=Y)
        
        # 添加水平滚动条
        hscrollbar = Scrollbar(canvas_frame, orient=HORIZONTAL)
        hscrollbar.pack(side=BOTTOM, fill=X)
        
        # 画布（支持滚动）
        self.canvas = Canvas(canvas_frame, bg=self.colors["canvas_bg"],
                           width=self.canvas_width, height=self.canvas_height,
                           relief=FLAT, highlightthickness=1,
                           highlightbackground="#E0E0E0",
                           yscrollcommand=vscrollbar.set,
                           xscrollcommand=hscrollbar.set)
        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)
        
        # 配置滚动条
        vscrollbar.config(command=self.canvas.yview)
        hscrollbar.config(command=self.canvas.xview)
        
        # 绑定鼠标滚轮事件
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Shift-MouseWheel>", self._on_shift_mousewheel)
        
        # 引导信息标签
        self.guide_label = Label(canvas_container, text="", font=("微软雅黑", 10, "bold"), 
                                fg="#D35400", bg=self.colors["guide_bg"], relief=SOLID, bd=1,
                                wraplength=900, justify=CENTER, height=2)
        self.guide_label.pack(fill=X, padx=10, pady=(0, 8))
        
        # 右侧伪代码面板
        self.create_pseudo_code_panel(content_frame)
    
    def create_pseudo_code_panel(self, parent):
        """创建伪代码显示面板（固定在右侧）"""
        pseudo_frame = Frame(parent, bg="#2d3436", relief=RAISED, bd=2, width=300)
        pseudo_frame.pack(side=RIGHT, fill=Y, padx=(8, 0))
        pseudo_frame.pack_propagate(False)
        
        # 标题
        title_label = Label(pseudo_frame, text="📋 伪代码执行过程", 
                           font=("微软雅黑", 12, "bold"), 
                           bg="#2d3436", fg="#00cec9", pady=5)
        title_label.pack(fill=X)
        
        # 分隔线
        separator = Frame(pseudo_frame, height=2, bg="#00cec9")
        separator.pack(fill=X, padx=10, pady=(0, 3))
        
        # 当前操作标签
        self.operation_label = Label(pseudo_frame, text="等待操作...", 
                                     font=("微软雅黑", 10), 
                                     bg="#2d3436", fg="#dfe6e9", 
                                     wraplength=280, justify=LEFT)
        self.operation_label.pack(fill=X, padx=10, pady=3)
        
        # 伪代码显示区域
        code_container = Frame(pseudo_frame, bg="#1e272e")
        code_container.pack(fill=BOTH, expand=True, padx=8, pady=5)
        
        self.pseudo_text = Text(code_container, 
                               font=("Consolas", 10), 
                               bg="#1e272e", fg="#b2bec3",
                               relief=FLAT, 
                               wrap=WORD,
                               padx=8, pady=8,
                               cursor="arrow",
                               state=DISABLED,
                               height=16,
                               width=32)
        self.pseudo_text.pack(fill=BOTH, expand=True)
        
        # 配置高亮标签样式
        self.pseudo_text.tag_configure("highlight", 
                                       background="#00b894", 
                                       foreground="#ffffff",
                                       font=("Consolas", 10, "bold"))
        self.pseudo_text.tag_configure("executed", 
                                       foreground="#55efc4")
        self.pseudo_text.tag_configure("pending", 
                                       foreground="#636e72")
        
        # 进度指示器
        progress_frame = Frame(pseudo_frame, bg="#2d3436")
        progress_frame.pack(fill=X, padx=10, pady=(0, 5))
        
        self.progress_label = Label(progress_frame, text="步骤: 0/0", 
                                    font=("Arial", 9), 
                                    bg="#2d3436", fg="#b2bec3")
        self.progress_label.pack(side=LEFT)
        
        self.status_indicator = Label(progress_frame, text="⚫ 空闲", 
                                      font=("Arial", 9), 
                                      bg="#2d3436", fg="#b2bec3")
        self.status_indicator.pack(side=RIGHT)
        
        # 速度控制
        control_separator = Frame(pseudo_frame, height=1, bg="#636e72")
        control_separator.pack(fill=X, padx=10, pady=5)
        
        speed_frame = Frame(pseudo_frame, bg="#2d3436")
        speed_frame.pack(fill=X, padx=10, pady=2)
        
        speed_label = Label(speed_frame, text="动画速度:", font=("Arial", 9), 
                           bg="#2d3436", fg="#dfe6e9")
        speed_label.pack(side=LEFT)
        
        self.speed_var = DoubleVar(value=self.animation_speed)
        speed_scale = Scale(speed_frame, from_=0.01, to=0.1, resolution=0.01, 
                           orient=HORIZONTAL, variable=self.speed_var,
                           command=self._update_speed, length=140,
                           bg="#2d3436", fg="#dfe6e9", highlightthickness=0,
                           troughcolor="#1e272e", activebackground="#00b894")
        speed_scale.pack(side=RIGHT, padx=5)
    
    def _update_speed(self, value):
        """更新动画速度"""
        self.animation_speed = float(value)
    
    # ==================== 增强动画辅助方法 ====================
    
    def clear_animation_elements(self):
        """清除所有动画辅助元素"""
        for elem_id in self.animation_elements:
            try:
                self.canvas.delete(elem_id)
            except Exception:
                pass
        self.animation_elements.clear()
        
        for arrow_id in self.arrow_ids:
            try:
                self.canvas.delete(arrow_id)
            except Exception:
                pass
        self.arrow_ids.clear()
        
        if self.comparison_box_id:
            try:
                self.canvas.delete(self.comparison_box_id)
            except Exception:
                pass
            self.comparison_box_id = None
            
        if self.pointer_id:
            try:
                self.canvas.delete(self.pointer_id)
            except Exception:
                pass
            self.pointer_id = None
    
    def draw_comparison_box(self, val1, val2, result: str, x: float = None, y: float = None):
        """绘制比较结果框 - 固定在画布左上角，简洁显示
        
        Args:
            val1: 要插入/查找的值
            val2: 当前节点的值
            result: 比较结果 '<', '>', '='
            x, y: 忽略，使用固定位置
        """
        self.clear_comparison_box()
        
        # 固定位置在画布左上角，避免遮挡节点
        box_x = 90
        box_y = 90
        box_width = 160
        box_height = 50
        
        # 根据比较结果设置颜色
        if result == "<":
            bg_color = "#E3F2FD"
            border_color = "#1976D2"
            text_color = "#1565C0"
            desc = "⬅ 去左子树"
        elif result == ">":
            bg_color = "#E8F5E9"
            border_color = "#388E3C"
            text_color = "#2E7D32"
            desc = "➡ 去右子树"
        else:
            bg_color = "#FFEBEE"
            border_color = "#D32F2F"
            text_color = "#C62828"
            desc = "✓ 找到!"
        
        # 背景框
        bg = self.canvas.create_rectangle(
            box_x - box_width/2, box_y - box_height/2,
            box_x + box_width/2, box_y + box_height/2,
            fill=bg_color, outline=border_color, width=2,
            tags="comparison_box"
        )
        self.animation_elements.append(bg)
        
        # 比较表达式
        compare_text = f"{val1} {result} {val2}"
        text_id = self.canvas.create_text(
            box_x, box_y - 8,
            text=compare_text,
            font=("Consolas", 13, "bold"),
            fill=text_color,
            tags="comparison_box"
        )
        self.animation_elements.append(text_id)
        
        # 结果说明
        desc_id = self.canvas.create_text(
            box_x, box_y + 12,
            text=desc,
            font=("微软雅黑", 9),
            fill=text_color,
            tags="comparison_box"
        )
        self.animation_elements.append(desc_id)
        
        self.comparison_box_id = bg
        self.window.update()
    
    def clear_comparison_box(self):
        """清除比较框"""
        self.canvas.delete("comparison_box")
        self.comparison_box_id = None
    
    def draw_pointer(self, x: float, y: float, direction: str = "down"):
        """绘制简化的当前节点指示器 - 只在节点上方显示小箭头
        
        Args:
            x, y: 节点顶部位置
            direction: 忽略，始终在上方
        """
        self.clear_pointer()
        
        # 简化：只绘制一个小三角形箭头指向节点
        arrow_y = y - 8
        pointer = self.canvas.create_polygon(
            x, arrow_y,           # 箭头尖端
            x - 6, arrow_y - 12,  # 左上角
            x + 6, arrow_y - 12,  # 右上角
            fill=self.colors["pointer_color"],
            outline="",
            tags="pointer"
        )
        self.pointer_id = pointer
        self.animation_elements.append(pointer)
        self.window.update()
    
    def clear_pointer(self):
        """清除指针"""
        self.canvas.delete("pointer")
        self.pointer_id = None
    
    def animate_pointer_move(self, from_x: float, from_y: float, to_x: float, to_y: float, 
                            callback=None, steps: int = 20):
        """动画移动指针从一个位置到另一个位置"""
        dx = (to_x - from_x) / steps
        dy = (to_y - from_y) / steps
        
        def step(i=0, cur_x=from_x, cur_y=from_y):
            if i >= steps:
                self.draw_pointer(to_x, to_y)
                if callback:
                    self.window.after(100, callback)
                return
            
            self.draw_pointer(cur_x, cur_y)
            self.window.after(30, lambda: step(i + 1, cur_x + dx, cur_y + dy))
        
        step()
    
    def draw_direction_arrow(self, from_x: float, from_y: float, to_x: float, to_y: float, 
                            color: str = None, label: str = ""):
        """绘制简化的方向箭头"""
        if color is None:
            color = self.colors["arrow_color"]
        
        # 绘制简单的虚线箭头，不添加标签避免杂乱
        arrow = self.canvas.create_line(
            from_x, from_y, to_x, to_y,
            fill=color, width=2, arrow=LAST,
            arrowshape=(10, 12, 4),
            dash=(4, 2),
            tags="direction_arrow"
        )
        self.arrow_ids.append(arrow)
        self.animation_elements.append(arrow)
        self.window.update()
    
    def clear_direction_arrows(self):
        """清除方向箭头"""
        self.canvas.delete("direction_arrow")
        self.arrow_ids.clear()
    
    def pulse_node(self, node: TreeNode, color: str, times: int = 3, callback=None):
        """让节点产生脉冲闪烁效果"""
        if node not in self.node_to_rect:
            if callback:
                callback()
            return
        
        rid = self.node_to_rect[node]
        original_color = self.colors["node_default"]
        
        def do_pulse(count=0, is_on=True):
            if count >= times * 2:
                try:
                    self.canvas.itemconfig(rid, fill=color)
                except Exception:
                    pass
                if callback:
                    self.window.after(100, callback)
                return
            
            try:
                if is_on:
                    self.canvas.itemconfig(rid, fill=color)
                else:
                    self.canvas.itemconfig(rid, fill=original_color)
            except Exception:
                pass
            
            self.window.update()
            self.window.after(150, lambda: do_pulse(count + 1, not is_on))
        
        do_pulse()
    
    def draw_node_glow(self, cx: float, cy: float, color: str = "#FFD54F"):
        """绘制节点外围简单边框效果（已简化，不再使用多层光晕）"""
        # 简化为单层虚线边框
        glow = self.canvas.create_rectangle(
            cx - self.node_w/2 - 4, cy - self.node_h/2 - 4,
            cx + self.node_w/2 + 4, cy + self.node_h/2 + 4,
            fill="", outline=color, width=2,
            dash=(3, 2),
            tags="node_glow"
        )
        self.animation_elements.append(glow)
        self.window.update()
    
    def clear_node_glow(self):
        """清除节点光晕"""
        self.canvas.delete("node_glow")
    
    def animate_connection_draw(self, from_x: float, from_y: float, to_x: float, to_y: float,
                               callback=None, steps: int = 15):
        """动画绘制连接线"""
        top = from_y + self.node_h/2
        bot = to_y - self.node_h/2
        mid_y = (top + bot) / 2
        
        def step(i=0):
            if i >= steps:
                if callback:
                    self.window.after(100, callback)
                return
            
            progress = (i + 1) / steps
            
            # 分段绘制
            if progress <= 0.33:
                # 第一段：垂直向下
                seg_progress = progress / 0.33
                cur_y = top + (mid_y - top) * seg_progress
                self.canvas.delete("temp_connection")
                line = self.canvas.create_line(
                    from_x, top, from_x, cur_y,
                    fill=self.colors["connection_new"], width=3,
                    tags="temp_connection"
                )
            elif progress <= 0.66:
                # 第二段：斜向下
                seg_progress = (progress - 0.33) / 0.33
                cur_x = from_x + (to_x - from_x) * seg_progress
                cur_y = mid_y + (bot - mid_y) * seg_progress * 0.5
                self.canvas.delete("temp_connection")
                line = self.canvas.create_line(
                    from_x, top, from_x, mid_y, cur_x, cur_y,
                    fill=self.colors["connection_new"], width=3,
                    smooth=True,
                    tags="temp_connection"
                )
            else:
                # 第三段：到达目标
                seg_progress = (progress - 0.66) / 0.34
                cur_y = mid_y + (bot - mid_y) * (0.5 + 0.5 * seg_progress)
                self.canvas.delete("temp_connection")
                line = self.canvas.create_line(
                    from_x, top, from_x, mid_y, to_x, cur_y,
                    fill=self.colors["connection_new"], width=3,
                    smooth=True, arrow=LAST,
                    tags="temp_connection"
                )
            
            self.animation_elements.append(line)
            self.window.update()
            self.window.after(40, lambda: step(i + 1))
        
        step()
    
    def draw_value_badge(self, val, x: float = None, y: float = None, label: str = "目标值"):
        """绘制值标签 - 固定在画布右上角，显示当前操作的目标值"""
        # 固定位置在右上角
        badge_x = self.canvas_width - 70
        badge_y = 90
        badge_width = 100
        badge_height = 40
        
        # 背景
        bg = self.canvas.create_rectangle(
            badge_x - badge_width/2, badge_y - badge_height/2,
            badge_x + badge_width/2, badge_y + badge_height/2,
            fill="#FFF8E1", outline="#FFA000", width=2,
            tags="value_badge"
        )
        self.animation_elements.append(bg)
        
        # 值和标签合并显示
        text_id = self.canvas.create_text(
            badge_x, badge_y,
            text=f"{label}: {val}",
            font=("微软雅黑", 10, "bold"),
            fill="#E65100",
            tags="value_badge"
        )
        self.animation_elements.append(text_id)
        
        self.window.update()
    
    def clear_value_badge(self):
        """清除值标签"""
        self.canvas.delete("value_badge")
    
    def animate_value_badge_move(self, val, from_x: float, from_y: float, 
                                 to_x: float, to_y: float, callback=None, steps: int = 25):
        """动画移动值标签"""
        dx = (to_x - from_x) / steps
        dy = (to_y - from_y) / steps
        
        def step(i=0, cur_x=from_x, cur_y=from_y):
            if i >= steps:
                self.clear_value_badge()
                if callback:
                    self.window.after(50, callback)
                return
            
            self.clear_value_badge()
            self.draw_value_badge(val, cur_x, cur_y, "新值")
            self.window.after(25, lambda: step(i + 1, cur_x + dx, cur_y + dy))
        
        step()
    
    def show_bst_property_hint(self, node_val, compare_val, result: str):
        """显示BST性质提示 - 已简化，通过guide_label显示"""
        # 不再单独绘制，使用update_guide来显示信息
        pass
    
    def clear_bst_hint(self):
        """清除BST提示"""
        self.canvas.delete("bst_hint")
    
    def draw_subtree_highlight(self, node: TreeNode, pos_map: Dict, is_left: bool):
        """高亮子树区域 - 已简化，不再绘制"""
        # 移除此功能，减少视觉杂乱
        pass
    
    def clear_subtree_highlight(self):
        """清除子树高亮"""
        self.canvas.delete("subtree_highlight")
    
    # ==================== 结束增强动画辅助方法 ====================
    
    def set_pseudo_code(self, title, lines):
        """设置要显示的伪代码"""
        self.pseudo_code_lines = lines
        self.current_highlight_line = -1
        
        self.operation_label.config(text=title, fg="#74b9ff")
        self.status_indicator.config(text="🟢 执行中", fg="#00b894")
        
        self.pseudo_text.config(state=NORMAL)
        self.pseudo_text.delete(1.0, END)
        
        for i, line in enumerate(lines):
            line_text = str(line) if not isinstance(line, dict) else line.get("text", "")
            line_num = f"{i+1:2}. "
            self.pseudo_text.insert(END, line_num, "pending")
            self.pseudo_text.insert(END, line_text + "\n", "pending")
        
        self.pseudo_text.config(state=DISABLED)
        self.progress_label.config(text=f"步骤: 0/{len(lines)}")
        self.window.update()
    
    def highlight_pseudo_line(self, line_index, delay=True):
        """高亮指定行的伪代码"""
        if not self.pseudo_code_lines or line_index < 0 or line_index >= len(self.pseudo_code_lines):
            return
        
        self.pseudo_text.config(state=NORMAL)
        
        for i in range(len(self.pseudo_code_lines)):
            start_pos = f"{i+1}.0"
            end_pos = f"{i+1}.end"
            self.pseudo_text.tag_remove("highlight", start_pos, end_pos)
            self.pseudo_text.tag_remove("pending", start_pos, end_pos)
            self.pseudo_text.tag_remove("executed", start_pos, end_pos)
            
            if i < line_index:
                self.pseudo_text.tag_add("executed", start_pos, end_pos)
            elif i == line_index:
                self.pseudo_text.tag_add("highlight", start_pos, end_pos)
            else:
                self.pseudo_text.tag_add("pending", start_pos, end_pos)
        
        self.pseudo_text.config(state=DISABLED)
        self.pseudo_text.see(f"{line_index+1}.0")
        
        self.current_highlight_line = line_index
        self.progress_label.config(text=f"步骤: {line_index+1}/{len(self.pseudo_code_lines)}")
        self.window.update()
        
        if delay:
            time.sleep(self.animation_speed * 3)
    
    def complete_pseudo_code(self):
        """标记伪代码执行完成"""
        self.pseudo_text.config(state=NORMAL)
        
        for i in range(len(self.pseudo_code_lines)):
            start_pos = f"{i+1}.0"
            end_pos = f"{i+1}.end"
            self.pseudo_text.tag_remove("highlight", start_pos, end_pos)
            self.pseudo_text.tag_remove("pending", start_pos, end_pos)
            self.pseudo_text.tag_add("executed", start_pos, end_pos)
        
        self.pseudo_text.config(state=DISABLED)
        self.status_indicator.config(text="✅ 完成", fg="#55efc4")
        self.progress_label.config(text=f"步骤: {len(self.pseudo_code_lines)}/{len(self.pseudo_code_lines)}")
        self.window.update()
    
    def clear_pseudo_code(self):
        """清除伪代码显示"""
        self.pseudo_code_lines = []
        self.current_highlight_line = -1
        
        self.operation_label.config(text="等待操作...", fg="#dfe6e9")
        self.status_indicator.config(text="⚫ 空闲", fg="#b2bec3")
        self.progress_label.config(text="步骤: 0/0")
        
        self.pseudo_text.config(state=NORMAL)
        self.pseudo_text.delete(1.0, END)
        self.pseudo_text.config(state=DISABLED)
        self.window.update()

    def create_button(self, parent, text, command, color):
        """创建样式化按钮"""
        return Button(parent, text=text, command=command,
                     bg=color, fg="white", font=("微软雅黑", 9),
                     relief=FLAT, bd=0, padx=12, pady=6,
                     cursor="hand2", activebackground=self._darken_color(color))

    def _darken_color(self, color):
        """加深颜色用于按钮激活状态"""
        if color.startswith("#"):
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            r = max(0, r - 30)
            g = max(0, g - 30)
            b = max(0, b - 30)
            return f"#{r:02x}{g:02x}{b:02x}"
        return color

    def _on_guide_mode_changed(self):
        """引导模式改变时的回调"""
        if not self.guide_mode.get():
            self.guide_label.config(bg=self.colors["bg_secondary"])
        else:
            self.guide_label.config(bg=self.colors["guide_bg"])
        
    def update_guide(self, text: str):
        """更新引导文本"""
        if not self.guide_mode.get():
            return
            
        self.guide_label.config(text=text)
        
        # 同时在画布底部也显示
        if hasattr(self, 'guide_text_id') and self.guide_text_id:
            self.canvas.delete(self.guide_text_id)
        self.guide_text_id = self.canvas.create_text(
            self.canvas_width/2, self.canvas_height - 20, 
            text=text, font=("微软雅黑", 10, "bold"), 
            fill="#D35400", width=self.canvas_width-40
        )
    
    def clear_guide(self):
        """清除引导文本"""
        self.guide_label.config(text="")
        if hasattr(self, 'guide_text_id') and self.guide_text_id:
            self.canvas.delete(self.guide_text_id)
            self.guide_text_id = None
        
    def _on_mousewheel(self, event):
        """处理垂直滚动"""
        if event.state & 0x0004:  # Shift键被按下时，进行水平滚动
            self.canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")
        else:  # 否则进行垂直滚动
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    def _on_shift_mousewheel(self, event):
        """处理水平滚动（备用方法）"""
        self.canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")

    def process_dsl(self, event=None):
        text = (self.dsl_var.get() or "").strip()
        if not text:
            return
        if getattr(self, "animating", False):
            messagebox.showinfo("提示", "请等待当前动画完成")
            return
        process_command(self, text)
        self.dsl_var.set("")
    
    def update_status(self, text: str, color: Optional[str] = None):
        """更新状态文本。可以指定颜色（默认为成功色）。
        同步更新顶部状态标签和画布上的状态文本。
        """
        use_color = color if color is not None else self.colors.get("status_success", "#2E7D32")
        # 更新顶部状态标签
        try:
            self.status_label.config(text=text, fg=use_color)
        except Exception:
            pass

        # 同时在画布上也显示状态
        if not self.status_text_id:
            self.status_text_id = self.canvas.create_text(
                self.canvas_width - 10, 10, anchor="ne",
                text=text, font=("微软雅黑", 10, "bold"),
                fill=use_color
            )
        else:
            try:
                self.canvas.itemconfig(self.status_text_id, text=text, fill=use_color)
            except Exception:
                pass

    # 其他方法保持不变...
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
        if not filepath:  # 用户取消保存
            return
            
        tree_dict = storage.tree_to_dict(self.model.root)
        
        metadata = {
            "saved_at": datetime.now().isoformat(),
            "node_count": len(tree_dict.get("nodes", [])) if isinstance(tree_dict, dict) else 0
        }
        payload = {"type": "tree", "tree": tree_dict, "metadata": metadata}
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)
            messagebox.showinfo("成功", f"✅ 二叉搜索树已保存到：\n{filepath}")
            self.update_status("💾 保存成功")
        except Exception as e:
            messagebox.showerror("错误", f"保存失败：{str(e)}")

    def load_tree(self):
        if self.animating:
            messagebox.showinfo("提示", "⏳ 请等待当前动画完成")
            return
            
        default_dir = self._ensure_tree_folder()
        filepath = filedialog.askopenfilename(
            initialdir=default_dir,
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="从文件加载二叉树"
        )
        if not filepath:  # 用户取消加载
            return
            
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                obj = json.load(f)
            tree_dict = obj.get("tree", {})
            if hasattr(storage, "tree_dict_to_nodes"):
                new_root = storage.tree_dict_to_nodes(tree_dict, TreeNode)
                self.model.root = new_root
                self.redraw()
                messagebox.showinfo("成功", "✅ 二叉树已成功加载并恢复")
                self.update_status("📂 加载成功")
        except Exception as e:
            messagebox.showerror("错误", f"加载失败：{str(e)}")

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
            y = 80 + depths[node] * self.level_gap
            pos[node] = (x, y)
        return pos

    def redraw(self):
        self.canvas.delete("all")
        self.node_items.clear()
        self.node_to_rect.clear()
        
        # 清除动画元素ID列表（但不删除画布上的元素，因为已被delete all清除）
        self.animation_elements.clear()
        self.arrow_ids.clear()
        self.comparison_box_id = None
        self.pointer_id = None
        
        self.draw_instructions()
        if self.model.root is None:
            # 显示更详细的空树说明
            self.canvas.create_text(
                self.canvas_width/2, self.canvas_height/2 - 20, 
                text="🌳 空树 - 请插入节点开始可视化", 
                font=("微软雅黑", 14), fill="#9E9E9E"
            )
            self.canvas.create_text(
                self.canvas_width/2, self.canvas_height/2 + 20, 
                text="💡 提示: 在上方输入框输入数值（如: 10,5,15），然后点击\"动画插入\"观看详细过程", 
                font=("微软雅黑", 10), fill="#BDBDBD"
            )
            return
        
        pos = self.compute_positions()
        
        # 先绘制边
        for node, (cx, cy) in pos.items():
            if node.left and node.left in pos:
                lx, ly = pos[node.left]
                self._draw_connection(cx, cy, lx, ly, is_left=True)
            if node.right and node.right in pos:
                rx, ry = pos[node.right]
                self._draw_connection(cx, cy, rx, ry, is_left=False)
        
        # 绘制节点
        for node, (cx, cy) in pos.items():
            self._draw_node(node, cx, cy)

    def _draw_connection(self, cx, cy, tx, ty, is_left: bool = True):
        """绘制节点连接线"""
        top = cy + self.node_h/2
        bot = ty - self.node_h/2
        mid_y = (top + bot) / 2
        
        # 根据左右子树使用不同颜色
        color = "#5C6BC0" if is_left else "#66BB6A"  # 蓝色=左, 绿色=右
        
        # 绘制带箭头的连接线
        line = self.canvas.create_line(cx, top, cx, mid_y, tx, bot, 
                                     width=2, fill=color, arrow=LAST,
                                     smooth=True)
        self.node_items.append(line)
        
        # 添加左/右标签（可选，在边的中点）
        mid_x = (cx + tx) / 2
        label_y = mid_y - 5
        direction_text = "L" if is_left else "R"
        label = self.canvas.create_text(
            mid_x, label_y,
            text=direction_text,
            font=("Arial", 8, "bold"),
            fill=color
        )
        self.node_items.append(label)

    def _draw_node(self, node: TreeNode, cx: float, cy: float):
        """绘制树节点 - 增强版，显示更多信息"""
        left = cx - self.node_w/2
        top = cy - self.node_h/2
        right = cx + self.node_w/2
        bottom = cy + self.node_h/2
        
        # 确定节点类型颜色
        outline_color = "#1976D2"
        if node == self.model.root:
            outline_color = "#9C27B0"  # 根节点用紫色边框
        elif node.left is None and node.right is None:
            outline_color = "#4CAF50"  # 叶子节点用绿色边框
        
        # 绘制节点主体
        rect = self.canvas.create_rectangle(
            left, top, right, bottom, 
            fill=self.colors["node_default"], 
            outline=outline_color, width=2
        )
        self.node_to_rect[node] = rect
        self.node_items.append(rect)
        
        # 节点内部区域分隔 - 左指针区 | 值区 | 右指针区
        x1 = left + self.left_cell_w
        x2 = x1 + self.center_cell_w
        v1 = self.canvas.create_line(x1, top, x1, bottom, width=1, fill="#BBDEFB")
        v2 = self.canvas.create_line(x2, top, x2, bottom, width=1, fill="#BBDEFB")
        self.node_items += [v1, v2]
        
        # 左指针区域标记
        left_marker = "◀" if node.left else "∅"
        left_color = "#5C6BC0" if node.left else "#BDBDBD"
        self.canvas.create_text(
            left + self.left_cell_w/2, (top+bottom)/2,
            text=left_marker,
            font=("Arial", 8),
            fill=left_color
        )
        
        # 节点值
        val_text = self.canvas.create_text(
            (x1+x2)/2, (top+bottom)/2, 
            text=str(node.val), 
            font=("微软雅黑", 11, "bold"),
            fill=self.colors["text_primary"]
        )
        self.node_items.append(val_text)
        
        # 右指针区域标记
        right_marker = "▶" if node.right else "∅"
        right_color = "#66BB6A" if node.right else "#BDBDBD"
        self.canvas.create_text(
            x2 + self.right_cell_w/2, (top+bottom)/2,
            text=right_marker,
            font=("Arial", 8),
            fill=right_color
        )
        
        # 如果是根节点，添加标签
        if node == self.model.root:
            root_label = self.canvas.create_text(
                cx, top - 12,
                text="👑 ROOT",
                font=("Arial", 8, "bold"),
                fill="#9C27B0"
            )
            self.node_items.append(root_label)

    def draw_instructions(self):
        """绘制操作说明 - 增强版，包含图例"""
        # 绘制说明文字
        self.canvas.create_text(
            self.canvas_width/2, 25, 
            text="🌳 二叉搜索树可视化演示 - 支持插入、查找、删除操作的动态展示", 
            font=("微软雅黑", 11, "bold"), 
            fill="#333333", 
            tags="instructions"
        )
        
        # 绘制BST性质说明
        self.canvas.create_text(
            10, 48, anchor="nw",
            text="📚 BST性质: 左子树所有值 < 根节点值 < 右子树所有值", 
            font=("微软雅黑", 9, "bold"),
            fill="#1565C0",
            tags="instructions"
        )
        
        # 绘制图例
        legend_y = 48
        legend_x = self.canvas_width - 280
        
        # 边颜色图例
        self.canvas.create_text(
            legend_x, legend_y, anchor="nw",
            text="图例: ",
            font=("微软雅黑", 8),
            fill="#666666",
            tags="instructions"
        )
        
        # L 边
        self.canvas.create_line(legend_x + 35, legend_y + 6, legend_x + 50, legend_y + 6,
                               fill="#5C6BC0", width=2, tags="instructions")
        self.canvas.create_text(legend_x + 55, legend_y, anchor="nw",
                               text="L=左", font=("Arial", 8), fill="#5C6BC0", tags="instructions")
        
        # R 边
        self.canvas.create_line(legend_x + 85, legend_y + 6, legend_x + 100, legend_y + 6,
                               fill="#66BB6A", width=2, tags="instructions")
        self.canvas.create_text(legend_x + 105, legend_y, anchor="nw",
                               text="R=右", font=("Arial", 8), fill="#66BB6A", tags="instructions")
        
        # 根节点标记
        self.canvas.create_rectangle(legend_x + 140, legend_y + 2, legend_x + 150, legend_y + 12,
                                    outline="#9C27B0", width=2, tags="instructions")
        self.canvas.create_text(legend_x + 155, legend_y, anchor="nw",
                               text="根", font=("Arial", 8), fill="#9C27B0", tags="instructions")
        
        # 叶子节点标记
        self.canvas.create_rectangle(legend_x + 175, legend_y + 2, legend_x + 185, legend_y + 12,
                                    outline="#4CAF50", width=2, tags="instructions")
        self.canvas.create_text(legend_x + 190, legend_y, anchor="nw",
                               text="叶", font=("Arial", 8), fill="#4CAF50", tags="instructions")
        
        if self.status_text_id:
            self.canvas.delete(self.status_text_id)
        
        self.status_text_id = self.canvas.create_text(
            self.canvas_width-10, 25, anchor="ne", text="", 
            font=("微软雅黑", 10, "bold"), 
            fill="#2E7D32", 
            tags="instructions"
        )

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
        """直接插入节点"""
        if self.animating:
            messagebox.showinfo("提示", "⏳ 当前正在执行动画，请稍候...")
            return
            
        text = self.input_var.get().strip()
        if not text:
            messagebox.showinfo("提示", "📝 请输入要插入的值（多个值用逗号分隔）")
            return
            
        try:
            items = [self.parse_value(s) for s in text.split(",") if s.strip() != ""]
            for v in items:
                self.model.insert(v)
            self.redraw()
            self.update_status(f"✅ 已插入 {len(items)} 个节点")
            self.update_guide(f"✨ 成功插入 {len(items)} 个节点: {', '.join(map(str, items))}")
        except Exception as e:
            messagebox.showerror("错误", f"插入失败：{str(e)}")

    def start_insert_animated(self):
        """开始动画插入"""
        if self.animating:
            messagebox.showinfo("提示", "⏳ 当前正在执行动画，请稍候...")
            return
            
        text = self.input_var.get().strip()
        if not text:
            messagebox.showinfo("提示", "📝 请输入要插入的值（多个值用逗号分隔）")
            return  
            
        try:
            items = [self.parse_value(s) for s in text.split(",") if s.strip() != ""]
            if not items:
                return
            self.animating = True
            self.clear_guide()
            
            # 设置伪代码
            pseudo_lines = [
                "// BST插入操作",
                "Insert(root, val):",
                "    if (root == null):",
                "        return new Node(val)",
                "    if (val < root.val):",
                "        root.left = Insert(root.left, val)",
                "    else:",
                "        root.right = Insert(root.right, val)",
                "    return root"
            ]
            self.set_pseudo_code(f"BST插入: {items[0]}", pseudo_lines)
            self.highlight_pseudo_line(0)
            self.highlight_pseudo_line(1)
            
            self.update_guide(f"🚀 开始插入操作：将依次插入 {len(items)} 个值")
            self.window.after(1000, lambda: self._insert_seq(items, 0))
        except Exception as e:
            messagebox.showerror("错误", f"插入失败：{str(e)}")

    def _insert_seq(self, items: List[str], idx: int):
        if idx >= len(items):
            self.animating = False
            self.complete_pseudo_code()
            self.update_status("✅ 插入完成")
            self.update_guide("🎉 所有插入操作已完成！")
            self.window.after(2000, self.clear_guide)
            return
        
        # 更新伪代码标题
        val = items[idx]
        pseudo_lines = [
            f"// BST插入: {val}",
            "Insert(root, val):",
            "    if (root == null):",
            f"        return new Node({val})",
            f"    if ({val} < root.val):",
            "        root.left = Insert(root.left, val)",
            "    else:",
            "        root.right = Insert(root.right, val)",
            "    return root"
        ]
        self.set_pseudo_code(f"BST插入: {val}", pseudo_lines)
        self.highlight_pseudo_line(0)
        self.highlight_pseudo_line(1)
            
        remaining = len(items) - idx - 1
        self.update_guide(f"📥 准备插入第 {idx+1}/{len(items)} 个值: {val} ({remaining} 个待插入)")
        self.window.after(800, lambda: self._animate_search_path_for_insert(val, items, idx))

    def _animate_search_path_for_insert(self, val: str, items: List[str], idx: int):
        path_nodes = []
        explanations = []
        pseudo_highlights = []  # 记录每步对应的伪代码行
        compare_results = []  # 记录比较结果符号
        directions = []  # 记录移动方向
        
        cur = self.model.root
        if cur is None:
            # 高亮 root == null 分支
            self.highlight_pseudo_line(2, delay=False)
            self.highlight_pseudo_line(3)
            self.update_guide(f"🌱 树为空，将 {val} 作为根节点插入")
            
            # 显示新值徽章从顶部下降
            self.draw_value_badge(val, self.canvas_width/2, 80, "🌱 首个节点")
            self.window.after(1000, lambda: self._finalize_insert_first_node(val, items, idx))
            return

        # 构建路径和解释
        step_count = 0
        while cur:
            path_nodes.append(cur)
            step_count += 1
            cmp = self.model.compare_values(val, cur.val)
            
            if cmp == 0:
                explanation = f"🔍 步骤{step_count}: 比较 {val} 与 {cur.val} → 相等(=)，向右子树移动（BST允许重复值）"
                pseudo_highlights.append(7)  # else 分支
                compare_results.append("=")
                directions.append("right")
                cur = cur.right
            elif cmp < 0:
                explanation = f"🔍 步骤{step_count}: 比较 {val} 与 {cur.val} → 较小(<)，进入左子树"
                pseudo_highlights.append(4)  # if val < root.val
                compare_results.append("<")
                directions.append("left")
                cur = cur.left
            else:
                explanation = f"🔍 步骤{step_count}: 比较 {val} 与 {cur.val} → 较大(>)，进入右子树"
                pseudo_highlights.append(7)  # else 分支
                compare_results.append(">")
                directions.append("right")
                cur = cur.right
                
            explanations.append(explanation)

        self._play_highlight_sequence_with_explanations_enhanced(
            path_nodes, explanations, pseudo_highlights, 
            compare_results, directions, val, items, idx
        )
    
    def _finalize_insert_first_node(self, val, items, idx):
        """处理插入第一个节点（空树情况）"""
        self.clear_value_badge()
        new_node = self.model.insert(val)
        self.redraw()
        
        # 高亮新节点并显示成功动画
        if new_node in self.node_to_rect:
            rid = self.node_to_rect[new_node]
            self.pulse_node(new_node, self.colors["node_success"], times=2, callback=lambda: self._after_first_insert(val, items, idx, rid))
        else:
            self.window.after(500, lambda: self._insert_seq(items, idx + 1))
    
    def _after_first_insert(self, val, items, idx, rid):
        """第一个节点插入后的处理"""
        self.update_guide(f"✅ 成功创建根节点 {val}！这是BST的第一个节点")
        self.canvas.itemconfig(rid, fill=self.colors["node_success"])
        
        def continue_next():
            try:
                self.canvas.itemconfig(rid, fill=self.colors["node_default"])
            except Exception:
                pass
            self.window.after(500, lambda: self._insert_seq(items, idx + 1))
        
        self.window.after(1500, continue_next)

    def _play_highlight_sequence_with_explanations(self, nodes: List[TreeNode], explanations: List[str], pseudo_highlights: List[int], val: str, items: List[str], idx: int):
        """保留旧方法用于兼容性"""
        if not nodes:
            self.highlight_pseudo_line(2, delay=False)
            self.highlight_pseudo_line(3)
            self.update_guide(f"📍 找到插入位置，准备插入新节点 {val}")
            self.window.after(800, lambda: self._finalize_insert_and_continue(val, items, idx))
            return
            
        i = 0
        def step():
            nonlocal i
            if i >= len(nodes):
                self.highlight_pseudo_line(8)  # return root
                self.update_guide(f"📍 搜索完成，准备在适当位置插入 {val}")
                self.window.after(800, lambda: self._finalize_insert_and_continue(val, items, idx))
                return
                
            node = nodes[i]
            explanation = explanations[i] if i < len(explanations) else f"访问节点 {node.val}"
            
            # 高亮对应的伪代码行
            if i < len(pseudo_highlights):
                self.highlight_pseudo_line(pseudo_highlights[i], delay=False)
            
            self.redraw()
            if node in self.node_to_rect:
                rid = self.node_to_rect[node]
                self.canvas.itemconfig(rid, fill=self.colors["node_highlight"])
                
            self.update_status(f"插入 {val}: 步骤 {i+1}/{len(nodes)}")
            self.update_guide(explanation)
            
            i += 1
            self.window.after(1000, step)
            
        step()
    
    def _play_highlight_sequence_with_explanations_enhanced(self, nodes: List[TreeNode], 
            explanations: List[str], pseudo_highlights: List[int], 
            compare_results: List[str], directions: List[str],
            val: str, items: List[str], idx: int):
        """增强版的高亮序列播放 - 流畅无跳变的动画"""
        
        if not nodes:
            self.clear_animation_elements()
            self.highlight_pseudo_line(2, delay=False)
            self.highlight_pseudo_line(3)
            self.update_guide(f"📍 找到插入位置，准备插入新节点 {val}")
            self.window.after(800, lambda: self._finalize_insert_and_continue(val, items, idx))
            return
        
        pos_map = self.compute_positions()
        
        # 先绘制一次树（之后不再重绘，只更新颜色）
        self.redraw()
        
        # 显示目标值（固定位置）
        self.draw_value_badge(val, label="插入")
        
        prev_node = None  # 记录上一个高亮的节点
        
        i = 0
        def step():
            nonlocal i, prev_node
            
            # 清除上一步的动画元素
            self.clear_comparison_box()
            self.clear_direction_arrows()
            self.clear_pointer()
            
            # 将上一个节点恢复为已访问状态（平滑过渡）
            if prev_node and prev_node in self.node_to_rect:
                self._smooth_color_transition(prev_node, self.colors["node_visited"])
            
            if i >= len(nodes):
                self.clear_animation_elements()
                self.highlight_pseudo_line(8)  # return root
                
                direction = directions[-1] if directions else "left"
                self.update_guide(f"📍 找到位置！将在 {nodes[-1].val} 的{'左' if direction == 'left' else '右'}子节点插入 {val}")
                self.window.after(1000, lambda: self._finalize_insert_and_continue(val, items, idx))
                return
            
            node = nodes[i]
            explanation = explanations[i] if i < len(explanations) else f"访问节点 {node.val}"
            compare_result = compare_results[i] if i < len(compare_results) else "?"
            direction = directions[i] if i < len(directions) else "left"
            
            # 高亮对应的伪代码行
            if i < len(pseudo_highlights):
                self.highlight_pseudo_line(pseudo_highlights[i], delay=False)
            
            # 平滑高亮当前节点
            if node in self.node_to_rect:
                self._smooth_color_transition(node, self.colors["node_comparing"])
                
                if node in pos_map:
                    cx, cy = pos_map[node]
                    # 简单的指针指示
                    self.draw_pointer(cx, cy - self.node_h/2)
                    # 比较框（固定位置）
                    self.draw_comparison_box(val, node.val, compare_result)
                    
                    # 如果不是最后一个节点，延迟显示方向箭头
                    if i < len(nodes) - 1:
                        next_node = nodes[i + 1]
                        if next_node in pos_map:
                            nx, ny = pos_map[next_node]
                            arrow_color = "#1565C0" if direction == "left" else "#2E7D32"
                            # 延迟显示箭头，让用户先看到比较结果
                            self.window.after(600, lambda c=cx, cy2=cy, n=nx, ny2=ny, col=arrow_color: 
                                self.draw_direction_arrow(c, cy2 + self.node_h/2, n, ny2 - self.node_h/2, col))
            
            self.update_status(f"插入 {val}: 步骤 {i+1}/{len(nodes)}")
            self.update_guide(explanation)
            
            prev_node = node
            i += 1
            self.window.after(1300, step)
        
        step()
    
    def _smooth_color_transition(self, node: TreeNode, target_color: str, steps: int = 5):
        """平滑过渡节点颜色"""
        if node not in self.node_to_rect:
            return
        
        rid = self.node_to_rect[node]
        
        # 直接设置颜色（简化版，避免复杂的颜色过渡）
        # 如果需要更平滑可以添加渐变，但这里保持简单
        try:
            self.canvas.itemconfig(rid, fill=target_color)
            self.window.update_idletasks()
        except Exception:
            pass

    def _finalize_insert_and_continue(self, val, items, idx):
        """最终插入节点 - 流畅动画版"""
        # 清除动画元素
        self.clear_animation_elements()
        self.clear_value_badge()
        self.canvas.delete("insert_hint")
        
        # 获取插入前的父节点信息
        parent_node = None
        is_left_child = True
        
        if self.model.root is not None:
            cur = self.model.root
            while cur:
                cmp = self.model.compare_values(val, cur.val)
                if cmp < 0:
                    if cur.left is None:
                        parent_node = cur
                        is_left_child = True
                        break
                    cur = cur.left
                else:
                    if cur.right is None:
                        parent_node = cur
                        is_left_child = False
                        break
                    cur = cur.right
        
        # 获取父节点当前位置
        parent_pos = None
        if parent_node:
            old_pos_map = self.compute_positions()
            if parent_node in old_pos_map:
                parent_pos = old_pos_map[parent_node]
        
        # 执行插入
        new_node = self.model.insert(val)
        new_pos_map = self.compute_positions()
        
        if new_node not in new_pos_map:
            self.redraw()
            self.update_guide(f"✅ 已插入 {val}")
            self.window.after(800, lambda: self._insert_seq(items, idx+1))
            return
        
        tx, ty = new_pos_map[new_node]
        
        # 确定起始位置
        if parent_pos:
            px, py = parent_pos
            # 从父节点下方开始
            sx = px - 40 if is_left_child else px + 40
            sy = py + self.node_h/2 + 10
        else:
            # 根节点从顶部中央开始
            sx, sy = self.canvas_width/2, 60
        
        self.update_guide(f"🎯 插入新节点 {val}...")
        
        # 创建简洁的移动节点
        temp_rect = self.canvas.create_rectangle(
            sx - self.node_w/2, sy - self.node_h/2,
            sx + self.node_w/2, sy + self.node_h/2,
            fill=self.colors["node_success"], 
            outline="#4CAF50", width=2,
            tags="temp_node"
        )
        
        temp_text = self.canvas.create_text(
            sx, sy, 
            text=str(val), 
            font=("微软雅黑", 11, "bold"),
            tags="temp_node"
        )
        
        # 使用缓动函数实现平滑移动
        total_steps = 30
        
        def ease_out_quad(t):
            """缓出二次方缓动函数"""
            return 1 - (1 - t) * (1 - t)
        
        def move_step(step=0):
            if step >= total_steps:
                # 动画完成，删除临时元素并重绘
                self.canvas.delete("temp_node")
                self.redraw()
                
                # 高亮新节点
                if new_node in self.node_to_rect:
                    rid = self.node_to_rect[new_node]
                    self.canvas.itemconfig(rid, fill=self.colors["node_success"])
                    self.update_guide(f"✅ 成功插入 {val}！")
                    self.update_status(f"✅ 插入完成: {val}")
                    
                    # 延迟恢复颜色并继续下一个
                    def finish():
                        try:
                            self.canvas.itemconfig(rid, fill=self.colors["node_default"])
                        except Exception:
                            pass
                        self.window.after(400, lambda: self._insert_seq(items, idx+1))
                    
                    self.window.after(1000, finish)
                else:
                    self.window.after(400, lambda: self._insert_seq(items, idx+1))
                return
            
            # 计算当前位置（使用缓动）
            progress = ease_out_quad(step / total_steps)
            cur_x = sx + (tx - sx) * progress
            cur_y = sy + (ty - sy) * progress
            
            # 更新位置
            self.canvas.coords(temp_rect, 
                cur_x - self.node_w/2, cur_y - self.node_h/2,
                cur_x + self.node_w/2, cur_y + self.node_h/2)
            self.canvas.coords(temp_text, cur_x, cur_y)
            
            self.window.after(18, lambda: move_step(step + 1))
        
        move_step()

    def start_search_animated(self):
        """开始动画查找"""
        if self.animating:
            messagebox.showinfo("提示", "⏳ 当前正在执行动画，请稍候...")
            return
            
        raw = self.input_var.get().strip()
        if not raw:
            messagebox.showinfo("提示", "🔍 请输入要查找的值")
            return
            
        try:
            val = self.parse_value(raw)
            self.animating = True
            self.clear_guide()
            
            # 设置伪代码
            pseudo_lines = [
                f"// BST查找: {val}",
                "Search(root, val):",
                "    if (root == null):",
                "        return null  // 未找到",
                f"    if ({val} == root.val):",
                "        return root  // 找到目标",
                f"    if ({val} < root.val):",
                "        return Search(root.left, val)",
                "    else:",
                "        return Search(root.right, val)"
            ]
            self.set_pseudo_code(f"BST查找: {val}", pseudo_lines)
            self.highlight_pseudo_line(0)
            self.highlight_pseudo_line(1)
            
            self.update_guide(f"🔎 开始查找值 {val}：从根节点开始比较")
            
            path_nodes = []
            explanations = []
            pseudo_highlights = []  # 记录每步对应的伪代码行
            compare_results = []  # 比较结果符号
            cur = self.model.root
            
            if cur is None:
                self.highlight_pseudo_line(2)
                self.highlight_pseudo_line(3)
                self.update_guide("❌ 树为空，无法查找")
                self.update_status("❌ 查找失败：树为空", color=self.colors.get("status_error"))
                self.animating = False
                self.complete_pseudo_code()
                # 弹窗提示并返回
                self.window.after(100, lambda: messagebox.showinfo("查找结果", "树为空，无法执行查找。"))
                return
            
            step_count = 0
            while cur:
                step_count += 1
                path_nodes.append(cur)
                cmp = self.model.compare_values(val, cur.val)
                
                if cmp == 0:
                    explanations.append(f"🎉 步骤{step_count}: 比较 {val} = {cur.val}，找到目标值！查找成功")
                    pseudo_highlights.append(4)  # val == root.val
                    compare_results.append("=")
                    break
                elif cmp < 0:
                    explanations.append(f"🔍 步骤{step_count}: 比较 {val} < {cur.val}，向左子树继续查找")
                    pseudo_highlights.append(6)  # val < root.val
                    compare_results.append("<")
                    cur = cur.left
                else:
                    explanations.append(f"🔍 步骤{step_count}: 比较 {val} > {cur.val}，向右子树继续查找")
                    pseudo_highlights.append(8)  # else 分支
                    compare_results.append(">")
                    cur = cur.right
                    
            found = (path_nodes and self.model.compare_values(val, path_nodes[-1].val) == 0)
            
            if not found and path_nodes:
                explanations.append(f"❌ 步骤{step_count}: 到达空位置，BST中不存在值 {val}")
            
            # 使用增强版的搜索动画
            self._play_search_animation_enhanced(val, path_nodes, explanations, 
                                                  pseudo_highlights, compare_results, found)
            
        except Exception as e:
            messagebox.showerror("错误", f"查找失败：{str(e)}")
            self.animating = False
    
    def _play_search_animation_enhanced(self, val, path_nodes: List[TreeNode], 
                                         explanations: List[str], pseudo_highlights: List[int],
                                         compare_results: List[str], found: bool):
        """增强版搜索动画 - 流畅无跳变"""
        pos_map = self.compute_positions()
        
        # 先绘制一次树（之后只更新颜色，不重绘）
        self.redraw()
        
        # 显示搜索目标值
        self.draw_value_badge(val, label="查找")
        
        prev_node = None  # 记录上一个高亮的节点
        
        i = 0
        def step():
            nonlocal i, prev_node
            
            # 清除上一步的动画元素
            self.clear_comparison_box()
            self.clear_direction_arrows()
            self.clear_pointer()
            
            # 将上一个节点平滑过渡到已访问状态
            if prev_node and prev_node in self.node_to_rect:
                self._smooth_color_transition(prev_node, self.colors["node_visited"])
            
            if i >= len(path_nodes):
                self.clear_animation_elements()
                self.animating = False
                
                if found:
                    self.highlight_pseudo_line(5, delay=False)  # return root (找到)
                    self.complete_pseudo_code()
                    node = path_nodes[-1]
                    
                    if node in self.node_to_rect:
                        rid = self.node_to_rect[node]
                        self.canvas.itemconfig(rid, fill=self.colors["node_success"])
                        self.update_guide(f"🎉 查找成功！找到值 {val}")
                        self.update_status(f"✅ 查找成功: {val}")
                        
                        def reset_color():
                            try:
                                self.canvas.itemconfig(rid, fill=self.colors["node_default"])
                            except Exception:
                                pass
                        self.window.after(2000, reset_color)
                else:
                    self.highlight_pseudo_line(3, delay=False)  # return null (未找到)
                    self.complete_pseudo_code()
                    self.update_guide(f"❌ 查找失败：BST中不存在值 {val}")
                    self.update_status(f"❌ 查找失败", color=self.colors.get("status_error"))
                    
                    # 高亮最后访问的节点
                    if path_nodes:
                        last = path_nodes[-1]
                        if last in self.node_to_rect:
                            self.canvas.itemconfig(self.node_to_rect[last], fill=self.colors["node_warning"])
                    
                    self.window.after(500, lambda: messagebox.showinfo("查找结果", f"未找到值 {val}"))
                return
            
            node = path_nodes[i]
            explanation = explanations[i] if i < len(explanations) else f"访问节点 {node.val}"
            compare_result = compare_results[i] if i < len(compare_results) else "?"
            
            # 高亮对应的伪代码行
            if i < len(pseudo_highlights):
                self.highlight_pseudo_line(pseudo_highlights[i], delay=False)
            
            # 高亮当前节点（不重绘整棵树）
            if node in self.node_to_rect:
                self._smooth_color_transition(node, self.colors["node_comparing"])
                
                if node in pos_map:
                    cx, cy = pos_map[node]
                    # 简单指针
                    self.draw_pointer(cx, cy - self.node_h/2)
                    # 比较框（固定位置）
                    self.draw_comparison_box(val, node.val, compare_result)
                    
                    # 如果不是最后一个且未找到，延迟显示方向箭头
                    if i < len(path_nodes) - 1 and compare_result != "=":
                        next_node = path_nodes[i + 1]
                        if next_node in pos_map:
                            nx, ny = pos_map[next_node]
                            arrow_color = "#1565C0" if compare_result == "<" else "#2E7D32"
                            self.window.after(500, lambda c=cx, cy2=cy, n=nx, ny2=ny, col=arrow_color:
                                self.draw_direction_arrow(c, cy2 + self.node_h/2, n, ny2 - self.node_h/2, col))
            
            self.update_status(f"查找 {val}: 步骤 {i+1}/{len(path_nodes)}")
            self.update_guide(explanation)
            
            prev_node = node
            i += 1
            self.window.after(1300, step)
        
        self.window.after(300, step)

    def start_delete_animated(self):
        """开始动画删除"""
        if self.animating:
            messagebox.showinfo("提示", "⏳ 当前正在执行动画，请稍候...")
            return
            
        raw = self.input_var.get().strip()
        if not raw:
            messagebox.showinfo("提示", "🗑️ 请输入要删除的值")
            return
            
        try:
            val = self.parse_value(raw)
            self.animating = True
            self.clear_guide()
            
            # 设置伪代码
            pseudo_lines = [
                f"// BST删除: {val}",
                "Delete(root, val):",
                "    node = Search(root, val)",
                "    if (node == null):",
                "        return  // 未找到",
                "    // 情况1: 叶子节点",
                "    if (node无子节点):",
                "        直接删除node",
                "    // 情况2: 只有一个子节点",
                "    else if (node只有一个子节点):",
                "        用子节点替换node",
                "    // 情况3: 有两个子节点",
                "    else:",
                "        successor = 右子树最小值",
                "        交换node和successor的值",
                "        删除successor"
            ]
            self.set_pseudo_code(f"BST删除: {val}", pseudo_lines)
            self.highlight_pseudo_line(0)
            self.highlight_pseudo_line(1)
            self.highlight_pseudo_line(2)
            
            self.update_guide(f"🗑️ 开始删除操作：首先需要在BST中定位值 {val}")

            path_nodes = []
            explanations = []
            pseudo_highlights = []
            compare_results = []  # 比较结果
            cur = self.model.root
            
            if cur is None:
                self.highlight_pseudo_line(3)
                self.highlight_pseudo_line(4)
                self.complete_pseudo_code()
                self.update_guide("❌ 树为空，无法删除")
                self.animating = False
                messagebox.showinfo("删除结果", "树为空，无法执行删除操作。")
                return
            
            step_count = 0
            while cur:
                step_count += 1
                path_nodes.append(cur)
                cmp = self.model.compare_values(val, cur.val)
                
                if cmp == 0:
                    explanations.append(f"🎯 步骤{step_count}: 比较 {val} = {cur.val}，找到目标节点！")
                    pseudo_highlights.append(2)  # Search 找到
                    compare_results.append("=")
                    break
                elif cmp < 0:
                    explanations.append(f"🔍 步骤{step_count}: 比较 {val} < {cur.val}，向左子树继续查找")
                    pseudo_highlights.append(2)  # Search 过程
                    compare_results.append("<")
                    cur = cur.left
                else:
                    explanations.append(f"🔍 步骤{step_count}: 比较 {val} > {cur.val}，向右子树继续查找")
                    pseudo_highlights.append(2)  # Search 过程
                    compare_results.append(">")
                    cur = cur.right

            found = (path_nodes and self.model.compare_values(val, path_nodes[-1].val) == 0)
            
            if not found and path_nodes:
                explanations.append(f"❌ 步骤{step_count}: 到达空位置，BST中不存在值 {val}")
            
            # 使用增强版删除定位动画
            self._play_delete_search_animation_enhanced(val, path_nodes, explanations, 
                                                         pseudo_highlights, compare_results, found)
                
        except Exception as e:
            messagebox.showerror("错误", f"删除失败：{str(e)}")
            self.animating = False
    
    def _play_delete_search_animation_enhanced(self, val, path_nodes: List[TreeNode],
                                                explanations: List[str], pseudo_highlights: List[int],
                                                compare_results: List[str], found: bool):
        """增强版删除搜索动画 - 流畅无跳变"""
        pos_map = self.compute_positions()
        
        # 先绘制一次树（之后只更新颜色）
        self.redraw()
        
        # 显示删除目标值
        self.draw_value_badge(val, label="删除")
        
        prev_node = None
        
        i = 0
        def step():
            nonlocal i, prev_node
            
            # 清除上一步的动画元素
            self.clear_comparison_box()
            self.clear_direction_arrows()
            self.clear_pointer()
            
            # 将上一个节点平滑过渡到已访问状态
            if prev_node and prev_node in self.node_to_rect:
                self._smooth_color_transition(prev_node, self.colors["node_visited"])
            
            if i >= len(path_nodes):
                self.clear_animation_elements()
                
                if not found:
                    self.highlight_pseudo_line(3, delay=False)
                    self.highlight_pseudo_line(4, delay=False)
                    self.complete_pseudo_code()
                    self.animating = False
                    self.update_guide(f"❌ 删除失败：BST中不存在值 {val}")
                    self.update_status(f"❌ 删除失败", color=self.colors.get("status_error"))
                    
                    if path_nodes:
                        last = path_nodes[-1]
                        if last in self.node_to_rect:
                            self.canvas.itemconfig(self.node_to_rect[last], fill=self.colors["node_warning"])
                    
                    self.window.after(300, lambda: messagebox.showinfo("删除结果", f"未找到值 {val}"))
                    return
                
                # 找到节点，开始删除过程
                self._animate_deletion_process(val, path_nodes[-1])
                return
            
            node = path_nodes[i]
            explanation = explanations[i] if i < len(explanations) else f"访问节点 {node.val}"
            compare_result = compare_results[i] if i < len(compare_results) else "?"
            
            # 高亮对应的伪代码行
            if i < len(pseudo_highlights):
                self.highlight_pseudo_line(pseudo_highlights[i], delay=False)
            
            # 高亮当前节点（不重绘整棵树）
            if node in self.node_to_rect:
                # 如果是目标节点，使用警告色；否则使用比较色
                target_color = self.colors["node_target"] if compare_result == "=" else self.colors["node_comparing"]
                self._smooth_color_transition(node, target_color)
                
                if node in pos_map:
                    cx, cy = pos_map[node]
                    # 简单指针
                    self.draw_pointer(cx, cy - self.node_h/2)
                    # 比较框（固定位置）
                    self.draw_comparison_box(val, node.val, compare_result)
                    
                    # 如果不是目标节点，延迟显示方向箭头
                    if compare_result != "=" and i < len(path_nodes) - 1:
                        next_node = path_nodes[i + 1]
                        if next_node in pos_map:
                            nx, ny = pos_map[next_node]
                            arrow_color = "#1565C0" if compare_result == "<" else "#2E7D32"
                            self.window.after(500, lambda c=cx, cy2=cy, n=nx, ny2=ny, col=arrow_color:
                                self.draw_direction_arrow(c, cy2 + self.node_h/2, n, ny2 - self.node_h/2, col))
            
            self.update_status(f"定位删除目标 {val}: 步骤 {i+1}/{len(path_nodes)}")
            self.update_guide(explanation)
            
            prev_node = node
            i += 1
            self.window.after(1300, step)
        
        self.window.after(300, step)

    def _animate_deletion_process(self, val, target_node):
        self.redraw()
        pos_map = self.compute_positions()
        
        if target_node in self.node_to_rect:
            self.canvas.itemconfig(self.node_to_rect[target_node], fill=self.colors["node_warning"])
            
            # 添加目标节点标识
            if target_node in pos_map:
                cx, cy = pos_map[target_node]
                self.draw_pointer(cx, cy - self.node_h/2)
                
                # 显示删除目标标签
                target_label = self.canvas.create_text(
                    cx, cy - self.node_h/2 - 50,
                    text="🎯 删除目标",
                    font=("微软雅黑", 10, "bold"),
                    fill="#C62828",
                    tags="delete_target"
                )
                self.animation_elements.append(target_label)
            
            self.update_guide(f"🎯 已定位到要删除的节点 {val}，正在分析节点类型...")
        
        def analyze_node_type():
            # 清除指针
            self.clear_pointer()
            
            # 显示节点分析信息
            has_left = target_node.left is not None
            has_right = target_node.right is not None
            
            # 创建分析框
            if target_node in pos_map:
                cx, cy = pos_map[target_node]
                
                analysis_text = f"📊 节点分析:\n"
                analysis_text += f"   左子节点: {'有 (' + str(target_node.left.val) + ')' if has_left else '无'}\n"
                analysis_text += f"   右子节点: {'有 (' + str(target_node.right.val) + ')' if has_right else '无'}"
                
                # 背景框
                box_x = cx + 120
                box_y = cy
                analysis_bg = self.canvas.create_rectangle(
                    box_x - 80, box_y - 35,
                    box_x + 80, box_y + 35,
                    fill="#E3F2FD", outline="#1976D2", width=2,
                    tags="analysis_box"
                )
                analysis_label = self.canvas.create_text(
                    box_x, box_y,
                    text=analysis_text,
                    font=("微软雅黑", 9),
                    fill="#0D47A1",
                    tags="analysis_box",
                    justify=LEFT
                )
                self.animation_elements.extend([analysis_bg, analysis_label])
            
            self.window.after(1500, lambda: self._execute_deletion_case(val, target_node, has_left, has_right, pos_map))
        
        self.window.after(1000, analyze_node_type)
    
    def _execute_deletion_case(self, val, target_node, has_left: bool, has_right: bool, pos_map: Dict):
        """根据节点类型执行相应的删除操作"""
        
        # 清除分析框
        self.canvas.delete("analysis_box")
        self.canvas.delete("delete_target")
        
        # 情况1：叶子节点
        if not has_left and not has_right:
            self._animate_delete_leaf(val, target_node, pos_map)
        
        # 情况2：只有一个子节点
        elif not has_left or not has_right:
            child = target_node.left if has_left else target_node.right
            child_type = "左" if has_left else "右"
            self._animate_delete_one_child(val, target_node, child, child_type, pos_map)
        
        # 情况3：有两个子节点
        else:
            self._animate_delete_two_children(val, target_node, pos_map)
    
    def _animate_delete_leaf(self, val, target_node, pos_map):
        """动画演示删除叶子节点"""
        self.highlight_pseudo_line(5, delay=False)  # 情况1注释
        self.highlight_pseudo_line(6, delay=False)  # if无子节点
        self.highlight_pseudo_line(7, delay=False)  # 直接删除
        
        self.update_guide(f"🍃 情况1: 节点 {val} 是叶子节点（无子节点）")
        
        if target_node in pos_map:
            cx, cy = pos_map[target_node]
            
            # 显示删除类型标签
            case_label = self.canvas.create_text(
                cx, cy + self.node_h/2 + 20,
                text="📋 情况1: 直接删除",
                font=("微软雅黑", 10, "bold"),
                fill="#4CAF50",
                tags="case_label"
            )
            self.animation_elements.append(case_label)
        
        def show_delete_animation():
            self.update_guide(f"🗑️ 直接删除叶子节点 {val}，无需调整树结构")
            
            if target_node in self.node_to_rect:
                rid = self.node_to_rect[target_node]
                
                # 淡出动画
                def fade_out(alpha=1.0):
                    if alpha <= 0:
                        self._complete_deletion(val)
                        return
                    
                    # 模拟淡出（通过改变颜色深度）
                    r = int(255 * alpha + 250 * (1 - alpha))
                    g = int(205 * alpha + 250 * (1 - alpha))
                    b = int(210 * alpha + 250 * (1 - alpha))
                    color = f"#{r:02x}{g:02x}{b:02x}"
                    
                    try:
                        self.canvas.itemconfig(rid, fill=color)
                    except Exception:
                        pass
                    
                    self.window.after(50, lambda: fade_out(alpha - 0.1))
                
                fade_out()
            else:
                self._complete_deletion(val)
        
        self.window.after(1500, show_delete_animation)
    
    def _animate_delete_one_child(self, val, target_node, child, child_type, pos_map):
        """动画演示删除只有一个子节点的节点"""
        self.highlight_pseudo_line(8, delay=False)  # 情况2注释
        self.highlight_pseudo_line(9, delay=False)  # if只有一个子节点
        self.highlight_pseudo_line(10, delay=False)  # 用子节点替换
        
        self.update_guide(f"📋 情况2: 节点 {val} 只有一个{child_type}子节点 {child.val}")
        
        # 高亮子节点
        if child in self.node_to_rect:
            self.canvas.itemconfig(self.node_to_rect[child], fill="#FFD93D")
        
        if target_node in pos_map:
            cx, cy = pos_map[target_node]
            
            # 显示删除类型标签
            case_label = self.canvas.create_text(
                cx, cy + self.node_h/2 + 20,
                text=f"📋 情况2: 子节点替换",
                font=("微软雅黑", 10, "bold"),
                fill="#FF9800",
                tags="case_label"
            )
            self.animation_elements.append(case_label)
        
        def show_replacement():
            self.update_guide(f"🔄 将{child_type}子节点 {child.val} 提升到 {val} 的位置")
            
            if child in pos_map and target_node in pos_map:
                child_x, child_y = pos_map[child]
                target_x, target_y = pos_map[target_node]
                
                # 绘制提升箭头
                self.draw_direction_arrow(
                    child_x, child_y - self.node_h/2,
                    target_x, target_y + self.node_h/2,
                    "#FF9800", "⬆️ 提升"
                )
            
            self.window.after(1500, lambda: self._complete_one_child_deletion(val, child, child_type))
        
        self.window.after(1500, show_replacement)
    
    def _complete_one_child_deletion(self, val, child, child_type):
        """完成单子节点删除"""
        self.clear_direction_arrows()
        self.canvas.delete("case_label")
        
        self.model.delete(val)
        self.redraw()
        
        # 高亮提升后的子节点
        if child in self.node_to_rect:
            self.canvas.itemconfig(self.node_to_rect[child], fill=self.colors["node_success"])
        
        self.complete_pseudo_code()
        self.update_guide(f"✅ 删除完成！{child_type}子节点 {child.val} 已提升到原 {val} 的位置")
        self.update_status(f"✅ 删除成功: {val}")
        
        self.window.after(1500, self._finish_deletion)
    
    def _animate_delete_two_children(self, val, target_node, pos_map):
        """动画演示删除有两个子节点的节点"""
        self.highlight_pseudo_line(11, delay=False)  # 情况3注释
        self.highlight_pseudo_line(12, delay=False)  # else
        
        self.update_guide(f"🔄 情况3: 节点 {val} 有两个子节点，这是最复杂的情况")
        
        if target_node in pos_map:
            cx, cy = pos_map[target_node]
            
            # 显示删除类型标签
            case_label = self.canvas.create_text(
                cx, cy + self.node_h/2 + 20,
                text="📋 情况3: 后继替换",
                font=("微软雅黑", 10, "bold"),
                fill="#9C27B0",
                tags="case_label"
            )
            self.animation_elements.append(case_label)
            
            # 高亮左右子节点
            if target_node.left in self.node_to_rect:
                self.canvas.itemconfig(self.node_to_rect[target_node.left], fill="#B3E5FC")
            if target_node.right in self.node_to_rect:
                self.canvas.itemconfig(self.node_to_rect[target_node.right], fill="#B3E5FC")
        
        def find_successor():
            self.update_guide(f"🔍 需要找到后继节点：右子树中的最小值（用于替换被删节点）")
            self.highlight_pseudo_line(13, delay=False)
            
            succ = self.model.find_min(target_node.right)
            
            # 动画显示寻找后继的过程
            self._animate_find_successor(target_node, succ, val, pos_map)
        
        self.window.after(1500, find_successor)
    
    def _animate_find_successor(self, target_node, succ, val, pos_map):
        """动画显示寻找后继节点的过程"""
        # 收集从右子节点到后继节点的路径
        path_to_succ = []
        cur = target_node.right
        while cur:
            path_to_succ.append(cur)
            if cur == succ:
                break
            cur = cur.left
        
        def highlight_path(idx=0):
            if idx >= len(path_to_succ):
                # 路径遍历完成，后继节点已找到
                self._show_successor_found(target_node, succ, val, pos_map)
                return
            
            node = path_to_succ[idx]
            if node in self.node_to_rect:
                if node == succ:
                    self.canvas.itemconfig(self.node_to_rect[node], fill=self.colors["node_successor"])
                    self.update_guide(f"✅ 找到后继节点: {succ.val}（右子树的最小值）")
                else:
                    self.canvas.itemconfig(self.node_to_rect[node], fill="#FFCC80")
                    self.update_guide(f"🔍 遍历右子树寻找最小值: 当前节点 {node.val}")
            
            # 绘制指针
            if node in pos_map:
                cx, cy = pos_map[node]
                self.draw_pointer(cx, cy - self.node_h/2)
            
            self.window.after(800, lambda: highlight_path(idx + 1))
        
        highlight_path()
    
    def _show_successor_found(self, target_node, succ, val, pos_map):
        """显示找到后继节点后的操作"""
        self.clear_pointer()
        
        # 高亮后继节点
        if succ in self.node_to_rect:
            self.canvas.itemconfig(self.node_to_rect[succ], fill=self.colors["node_successor"])
        
        # 绘制箭头连接目标节点和后继节点
        if target_node in pos_map and succ in pos_map:
            tx, ty = pos_map[target_node]
            sx, sy = pos_map[succ]
            
            # 显示值交换箭头
            swap_arrow = self.canvas.create_line(
                tx, ty, sx, sy,
                fill="#9C27B0", width=3,
                arrow=BOTH, arrowshape=(12, 15, 5),
                dash=(5, 3),
                tags="swap_arrow"
            )
            self.animation_elements.append(swap_arrow)
            
            # 交换标签
            mid_x, mid_y = (tx + sx) / 2, (ty + sy) / 2
            swap_label = self.canvas.create_text(
                mid_x, mid_y - 15,
                text="🔄 值交换",
                font=("微软雅黑", 10, "bold"),
                fill="#9C27B0",
                tags="swap_arrow"
            )
            self.animation_elements.append(swap_label)
        
        self.update_guide(f"📌 准备将后继节点 {succ.val} 的值复制到目标节点位置，然后删除后继节点")
        
        self.window.after(2000, lambda: self._perform_swap_and_delete(target_node, succ, val, pos_map))
    
    def _perform_swap_and_delete(self, target_node, succ, val, pos_map):
        """执行值交换和删除"""
        self.highlight_pseudo_line(14, delay=False)  # 交换值
        self.canvas.delete("swap_arrow")
        
        # 保存原始值用于显示
        old_target_val = target_node.val
        succ_val = succ.val
        
        # 执行值交换
        target_node.val = succ.val
        succ.val = old_target_val
        
        # 重绘显示交换后的状态
        self.redraw()
        
        # 重新高亮节点
        if target_node in self.node_to_rect:
            self.canvas.itemconfig(self.node_to_rect[target_node], fill="#4ECDC4")
        if succ in self.node_to_rect:
            self.canvas.itemconfig(self.node_to_rect[succ], fill=self.colors["node_warning"])
        
        self.update_guide(f"🔄 值已交换！目标位置现在是 {succ_val}，后继位置是 {old_target_val}")
        
        def delete_successor():
            self.highlight_pseudo_line(15, delay=False)  # 删除successor
            self.update_guide(f"🗑️ 删除后继节点（现在包含原值 {old_target_val}）")
            
            # 后继节点现在是叶子节点或只有右子节点，可以简单删除
            if succ in self.node_to_rect:
                rid = self.node_to_rect[succ]
                
                # 淡出动画
                def fade_out(alpha=1.0):
                    if alpha <= 0:
                        self.model.delete_node(succ)
                        self.redraw()
                        self._complete_two_children_deletion(succ_val, old_target_val)
                        return
                    
                    r = int(255 * alpha + 250 * (1 - alpha))
                    g = int(205 * alpha + 250 * (1 - alpha))
                    b = int(210 * alpha + 250 * (1 - alpha))
                    color = f"#{r:02x}{g:02x}{b:02x}"
                    
                    try:
                        self.canvas.itemconfig(rid, fill=color)
                    except Exception:
                        pass
                    
                    self.window.after(50, lambda: fade_out(alpha - 0.1))
                
                fade_out()
            else:
                self.model.delete_node(succ)
                self.redraw()
                self._complete_two_children_deletion(succ_val, old_target_val)
        
        self.window.after(1500, delete_successor)
    
    def _complete_two_children_deletion(self, new_val, old_val):
        """完成双子节点删除"""
        self.canvas.delete("case_label")
        self.clear_animation_elements()
        
        self.complete_pseudo_code()
        self.update_guide(f"✅ 删除完成！原节点 {old_val} 已被后继值 {new_val} 替换，BST性质保持不变")
        self.update_status(f"✅ 删除成功: {old_val}")
        
        self.window.after(1500, self._finish_deletion)
    
    def _complete_deletion(self, val):
        """完成叶子节点删除"""
        self.canvas.delete("case_label")
        self.clear_animation_elements()
        
        self.model.delete(val)
        self.redraw()
        self.complete_pseudo_code()
        self.update_guide(f"✅ 叶子节点 {val} 已成功删除！")
        self.update_status(f"✅ 删除成功: {val}")
        
        self.window.after(1500, self._finish_deletion)
    
    def _finish_deletion(self):
        """删除操作结束"""
        self.animating = False
        self.clear_animation_elements()

    def clear_canvas(self):
        """清空画布"""
        if self.animating:
            messagebox.showinfo("提示", "⏳ 当前正在执行动画，请稍候...")
            return
        
        # 清除所有动画元素
        self.clear_animation_elements()
        self.clear_pseudo_code()
        
        self.model = BSTModel()
        self.redraw()
        self.update_status("🧹 已清空BST")
        self.clear_guide()

    def back_to_main(self):
        """返回主界面"""
        if self.animating:
            messagebox.showinfo("提示", "⏳ 正在执行动画，请等待完成")
            return
            
        if messagebox.askyesno("确认返回", "确定要返回主界面吗？"):
            self.window.destroy()
        
if __name__ == '__main__':
    w = Tk()
    w.title("🌳 二叉搜索树可视化系统")
    w.geometry("1350x800")
        
    BSTVisualizer(w)
    w.mainloop()