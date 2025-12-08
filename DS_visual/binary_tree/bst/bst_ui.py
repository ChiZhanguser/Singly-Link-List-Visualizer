from tkinter import Button, Label, Entry, Frame, X, LEFT, RIGHT, TOP, BOTTOM

def create_controls(self):
    """创建控制按钮（兼容性函数）"""
    # 这个函数现在由BSTVisualizer类的create_control_panel方法替代
    pass

def draw_instructions(self):
    """绘制操作说明 - 增强版，包含图例
    注意：此函数已被BSTVisualizer类中的同名方法替代
    保留此处仅为兼容性目的
    """
    # 先清除画布上的节点，但保留背景
    for item in self.node_items:
        self.canvas.delete(item)
    self.node_items.clear()
    self.node_to_rect.clear()
    
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