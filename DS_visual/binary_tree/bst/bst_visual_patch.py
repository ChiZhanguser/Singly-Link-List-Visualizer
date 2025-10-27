from tkinter import *
from tkinter import messagebox
from tkinter import Toplevel, filedialog
from typing import Dict, Tuple, List, Optional
import os
from datetime import datetime
from binary_tree.bst.bst_model import BSTModel, TreeNode
from DSL_utils import process_command

class BSTVisualizer:
    def __init__(self, root):
        # ... 其他初始化代码保持不变 ...

        # 更新核心属性
        self.canvas_width = 1250
        self.canvas_height = 560
        self.model = BSTModel()
        self.node_to_rect: Dict[TreeNode, int] = {}
        self.node_items: List[int] = []
        self.status_text_id: Optional[int] = None

        # 优化布局参数
        self.node_w = 120
        self.node_h = 44
        self.left_cell_w = 28
        self.center_cell_w = 64
        self.right_cell_w = self.node_w - self.left_cell_w - self.center_cell_w
        self.level_gap = 80  # 减小垂直间距
        self.margin_x = 40
        
        # 创建主框架
        self.main_frame = Frame(self.window, bg="#F0F2F5")
        self.main_frame.pack(fill=BOTH, expand=True, padx=12, pady=12)
        
        # 创建界面组件
        self.create_header()
        self.create_control_panel()
        self.create_canvas_area()
        
        # 初始绘制
        self.redraw()

    def create_canvas_area(self):
        """创建画布区域 - 放在控制面板下方"""
        canvas_container = Frame(self.main_frame, bg="#FFFFFF", relief=SOLID, bd=1)
        canvas_container.pack(fill=BOTH, expand=True, pady=(0, 8))
        
        # 画布控制栏
        canvas_toolbar = Frame(canvas_container, bg="#FFFFFF", height=28)
        canvas_toolbar.pack(fill=X, padx=10, pady=6)
        canvas_toolbar.pack_propagate(False)
        
        self.status_label = Label(canvas_toolbar, text="🟢 就绪", 
                                font=("微软雅黑", 10), 
                                bg="#FFFFFF",
                                fg="#2E7D32",
                                anchor=W)
        self.status_label.pack(side=LEFT, fill=X, expand=True)
        
        # 创建画布框架（带滚动条）
        canvas_frame = Frame(canvas_container)
        canvas_frame.pack(padx=10, pady=(0, 8), fill=BOTH, expand=True)
        
        # 添加垂直滚动条
        vscrollbar = Scrollbar(canvas_frame, orient=VERTICAL)
        vscrollbar.pack(side=RIGHT, fill=Y)
        
        # 添加水平滚动条
        hscrollbar = Scrollbar(canvas_frame, orient=HORIZONTAL)
        hscrollbar.pack(side=BOTTOM, fill=X)
        
        # 创建画布（支持滚动）
        self.canvas = Canvas(canvas_frame, bg="#FAFAFA",
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
        # 绑定鼠标拖动事件
        self.canvas.bind("<ButtonPress-1>", self._start_pan)
        self.canvas.bind("<B1-Motion>", self._pan_canvas)
        
        # 引导信息标签
        self.guide_label = Label(canvas_container, text="", 
                               font=("微软雅黑", 10, "bold"),
                               fg="#D35400", bg="#FFFDE7",
                               relief=SOLID, bd=1,
                               wraplength=1200, justify=CENTER,
                               height=2)
        self.guide_label.pack(fill=X, padx=10, pady=(0, 8))

    def _on_mousewheel(self, event):
        """处理垂直滚动"""
        if event.state & 0x0004:  # Shift键被按下时，进行水平滚动
            self.canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")
        else:  # 否则进行垂直滚动
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    def _on_shift_mousewheel(self, event):
        """处理水平滚动（备用方法）"""
        self.canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")

    def _start_pan(self, event):
        """开始平移"""
        self.canvas.scan_mark(event.x, event.y)

    def _pan_canvas(self, event):
        """平移画布"""
        self.canvas.scan_dragto(event.x, event.y, gain=1)

    def redraw(self):
        """重绘画布内容"""
        # 清除现有内容
        self.canvas.delete("all")
        self.node_items.clear()
        self.node_to_rect.clear()

        if not self.model.root:
            self.draw_instructions()
            return
            
        # 计算布局位置
        positions = self.compute_positions()
        
        # 计算树的实际尺寸并设置滚动区域
        if positions:
            max_y = max(y for x, y in positions.values()) + 100
            max_x = max(x for x, y in positions.values()) + 100
            self.canvas.configure(scrollregion=(0, 0, max(max_x, self.canvas_width), 
                                             max(max_y, self.canvas_height)))
        
        # 先绘制连接线
        for node in self.model.preorder():
            if node in positions:
                cx, cy = positions[node]
                if node.left and node.left in positions:
                    tx, ty = positions[node.left]
                    self._draw_connection(cx, cy, tx, ty)
                if node.right and node.right in positions:
                    tx, ty = positions[node.right]
                    self._draw_connection(cx, cy, tx, ty)
        
        # 再绘制节点
        for node in self.model.preorder():
            if node in positions:
                cx, cy = positions[node]
                self._draw_node(node, cx, cy)