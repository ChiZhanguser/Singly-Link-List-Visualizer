from tkinter import Button, Label, Entry, Frame, X, LEFT, RIGHT, TOP, BOTTOM

def create_controls(self):
    """创建控制按钮（兼容性函数）"""
    # 这个函数现在由BSTVisualizer类的create_control_panel方法替代
    pass

def draw_instructions(self):
    """绘制操作说明"""
    # 先清除画布上的节点，但保留背景
    for item in self.node_items:
        self.canvas.delete(item)
    self.node_items.clear()
    self.node_to_rect.clear()
    
    # 绘制说明文字
    self.canvas.create_text(
        self.canvas_width/2, 30, 
        text="🌳 二叉搜索树可视化演示 - 支持插入、查找、删除操作的动态展示", 
        font=("微软雅黑", 11, "bold"), 
        fill="#333333", 
        tags="instructions"
    )
    
    # 绘制特性说明
    self.canvas.create_text(
        10, 55, anchor="nw",
        text="• 中序遍历用于横向布局 • 红色高亮显示搜索路径 • 绿色表示操作成功", 
        font=("微软雅黑", 9),
        fill="#666666",
        tags="instructions"
    )
    
    if self.status_text_id:
        self.canvas.delete(self.status_text_id)
    
    self.status_text_id = self.canvas.create_text(
        self.canvas_width-10, 55, anchor="ne", text="", 
        font=("微软雅黑", 10, "bold"), 
        fill="#2E7D32", 
        tags="instructions"
    )