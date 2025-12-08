"""
高级动画效果模块 - 为链表可视化提供丰富的动画效果
包含：脉冲效果、发光效果、粒子效果、路径动画等
"""
from tkinter import Canvas, Label, LAST
import time
import math
import random


class AnimationEffects:
    """动画效果管理器"""
    
    # 动画速度设置
    SPEED_SLOW = 0.08
    SPEED_NORMAL = 0.04
    SPEED_FAST = 0.02
    
    def __init__(self, canvas: Canvas, window):
        self.canvas = canvas
        self.window = window
        self.animation_speed = self.SPEED_NORMAL
        self.particle_ids = []  # 存储粒子ID用于清理
        
    def set_speed(self, speed_level):
        """设置动画速度"""
        speed_map = {
            "slow": self.SPEED_SLOW,
            "normal": self.SPEED_NORMAL,
            "fast": self.SPEED_FAST
        }
        self.animation_speed = speed_map.get(speed_level, self.SPEED_NORMAL)
    
    def pulse_node(self, node_rect_id, color1="#FFFF00", color2="#FF6B6B", cycles=3):
        """
        节点脉冲效果 - 让节点在两种颜色之间闪烁
        
        Args:
            node_rect_id: 节点矩形的canvas ID
            color1, color2: 脉冲的两种颜色
            cycles: 脉冲次数
        """
        original_fill = self.canvas.itemcget(node_rect_id, "fill")
        original_outline = self.canvas.itemcget(node_rect_id, "outline")
        
        for _ in range(cycles):
            # 变为高亮色
            self.canvas.itemconfig(node_rect_id, fill=color2, outline="#FF0000", width=5)
            self.window.update()
            time.sleep(self.animation_speed * 2)
            
            # 变回原色
            self.canvas.itemconfig(node_rect_id, fill=color1, outline=original_outline, width=3)
            self.window.update()
            time.sleep(self.animation_speed * 2)
        
        # 恢复原始状态
        self.canvas.itemconfig(node_rect_id, fill=original_fill, outline=original_outline, width=3)
        self.window.update()
    
    def glow_effect(self, x, y, radius=30, color="#00FF00", duration=0.5):
        """
        发光效果 - 在指定位置创建扩散发光圆环
        
        Args:
            x, y: 发光中心位置
            radius: 最大发光半径
            color: 发光颜色
            duration: 持续时间
        """
        glow_ids = []
        steps = 15
        
        for i in range(steps):
            r = radius * (i + 1) / steps
            alpha = 1 - (i / steps)
            # 创建渐变透明效果的圆环
            glow_id = self.canvas.create_oval(
                x - r, y - r, x + r, y + r,
                outline=color, width=max(1, int(3 * alpha)),
                dash=(3, 2) if i > steps // 2 else ()
            )
            glow_ids.append(glow_id)
            self.window.update()
            time.sleep(duration / steps / 2)
        
        # 淡出效果
        time.sleep(duration / 3)
        
        # 清理发光效果
        for glow_id in glow_ids:
            try:
                self.canvas.delete(glow_id)
            except:
                pass
        self.window.update()
    
    def create_particles(self, x, y, count=12, color="#FFD700", spread=50):
        """
        创建粒子爆炸效果
        
        Args:
            x, y: 粒子中心位置
            count: 粒子数量
            color: 粒子颜色
            spread: 扩散范围
        """
        particles = []
        
        for i in range(count):
            angle = (2 * math.pi * i) / count
            dx = math.cos(angle)
            dy = math.sin(angle)
            
            # 创建粒子（小圆点）
            pid = self.canvas.create_oval(
                x - 3, y - 3, x + 3, y + 3,
                fill=color, outline=color
            )
            particles.append((pid, dx, dy))
        
        # 动画扩散
        for step in range(15):
            for pid, dx, dy in particles:
                self.canvas.move(pid, dx * spread / 15, dy * spread / 15)
            self.window.update()
            time.sleep(self.animation_speed / 2)
        
        # 淡出并删除粒子
        time.sleep(0.1)
        for pid, _, _ in particles:
            try:
                self.canvas.delete(pid)
            except:
                pass
        self.window.update()
    
    def draw_animated_arrow(self, x1, y1, x2, y2, color="#FF4500", width=4, steps=20):
        """
        绘制带动画的箭头 - 从起点逐渐延伸到终点
        
        Args:
            x1, y1: 起点
            x2, y2: 终点
            color: 箭头颜色
            width: 箭头宽度
            steps: 动画步数
        
        Returns:
            arrow_id: 创建的箭头ID
        """
        arrow_id = None
        
        for i in range(1, steps + 1):
            t = i / steps
            # 缓动函数
            t = t * (2 - t)  # ease-out
            
            curr_x = x1 + (x2 - x1) * t
            curr_y = y1 + (y2 - y1) * t
            
            if arrow_id:
                self.canvas.delete(arrow_id)
            
            arrow_id = self.canvas.create_line(
                x1, y1, curr_x, curr_y,
                arrow=LAST, width=width, fill=color,
                arrowshape=(12, 15, 5)
            )
            self.window.update()
            time.sleep(self.animation_speed / 2)
        
        return arrow_id
    
    def draw_curved_arrow(self, x1, y1, x2, y2, curve_height=50, color="#FF6B6B", width=3, animated=True):
        """
        绘制曲线箭头（用于显示指针跳转）
        
        Args:
            x1, y1: 起点
            x2, y2: 终点
            curve_height: 曲线弯曲高度
            color: 颜色
            width: 线宽
            animated: 是否动画绘制
        
        Returns:
            arrow_id: 创建的箭头ID
        """
        # 计算控制点
        mid_x = (x1 + x2) / 2
        mid_y = min(y1, y2) - curve_height
        
        # 生成贝塞尔曲线点
        points = []
        num_points = 30
        
        for i in range(num_points + 1):
            t = i / num_points
            # 二次贝塞尔曲线公式
            x = (1-t)**2 * x1 + 2*(1-t)*t * mid_x + t**2 * x2
            y = (1-t)**2 * y1 + 2*(1-t)*t * mid_y + t**2 * y2
            points.extend([x, y])
        
        if animated:
            arrow_id = None
            for i in range(4, len(points), 4):
                if arrow_id:
                    self.canvas.delete(arrow_id)
                arrow_id = self.canvas.create_line(
                    points[:i], 
                    arrow=LAST if i >= len(points) - 4 else None,
                    width=width, fill=color, smooth=True,
                    arrowshape=(10, 12, 4)
                )
                self.window.update()
                time.sleep(self.animation_speed / 3)
        else:
            arrow_id = self.canvas.create_line(
                points, arrow=LAST, width=width, fill=color, smooth=True,
                arrowshape=(10, 12, 4)
            )
        
        return arrow_id
    
    def highlight_node_sequence(self, node_rect_ids, highlight_color="#90EE90", delay=0.3):
        """
        依次高亮一系列节点（用于遍历可视化）
        
        Args:
            node_rect_ids: 节点矩形ID列表
            highlight_color: 高亮颜色
            delay: 每个节点的高亮延迟
        """
        original_colors = []
        
        # 保存原始颜色
        for rect_id in node_rect_ids:
            try:
                original_colors.append(self.canvas.itemcget(rect_id, "fill"))
            except:
                original_colors.append("#1E3A5F")
        
        # 依次高亮
        for i, rect_id in enumerate(node_rect_ids):
            # 重置前一个节点
            if i > 0:
                try:
                    self.canvas.itemconfig(node_rect_ids[i-1], fill=original_colors[i-1])
                except:
                    pass
            
            # 高亮当前节点
            try:
                self.canvas.itemconfig(rect_id, fill=highlight_color, width=5)
            except:
                pass
            
            self.window.update()
            time.sleep(delay)
        
        # 恢复最后一个节点
        if node_rect_ids and original_colors:
            try:
                self.canvas.itemconfig(node_rect_ids[-1], fill=original_colors[-1], width=3)
            except:
                pass
            self.window.update()
    
    def create_memory_address_label(self, x, y, address=None):
        """
        创建内存地址标签
        
        Args:
            x, y: 标签位置
            address: 地址值（如果为None则随机生成）
        
        Returns:
            label: 创建的标签对象
        """
        if address is None:
            address = hex(random.randint(0x1000, 0xFFFF))
        
        label = Label(
            self.canvas, 
            text=f"@{address}",
            font=("Consolas", 8),
            bg="#2D2D2D",
            fg="#00FF00",
            padx=2, pady=1
        )
        label.place(x=x, y=y)
        return label
    
    def animate_pointer_jump(self, start_x, start_y, end_x, end_y, 
                            pointer_rect_id=None, color="#00BFFF"):
        """
        动画显示指针跳转（从一个节点跳到另一个节点）
        
        Args:
            start_x, start_y: 起始位置
            end_x, end_y: 目标位置
            pointer_rect_id: 指针矩形ID（可选）
            color: 轨迹颜色
        """
        # 绘制跳转轨迹
        trail_ids = []
        steps = 20
        
        for i in range(steps):
            t = i / steps
            # 使用抛物线轨迹
            curr_x = start_x + (end_x - start_x) * t
            # 添加抛物线效果
            arc = -4 * 50 * t * (t - 1)  # 抛物线高度50
            curr_y = start_y + (end_y - start_y) * t - arc
            
            # 创建轨迹点
            trail_id = self.canvas.create_oval(
                curr_x - 3, curr_y - 3, curr_x + 3, curr_y + 3,
                fill=color, outline=""
            )
            trail_ids.append(trail_id)
            
            # 移动指针矩形（如果提供）
            if pointer_rect_id:
                self.canvas.coords(
                    pointer_rect_id,
                    curr_x - 15, curr_y - 15,
                    curr_x + 15, curr_y + 15
                )
            
            self.window.update()
            time.sleep(self.animation_speed)
        
        # 清理轨迹
        time.sleep(0.1)
        for tid in trail_ids:
            try:
                self.canvas.delete(tid)
            except:
                pass
        self.window.update()
    
    def create_comparison_animation(self, x, y, search_value, node_value, match=False):
        """
        创建比较动画（用于搜索操作）
        
        Args:
            x, y: 动画位置
            search_value: 搜索值
            node_value: 节点值
            match: 是否匹配
        """
        # 创建比较显示框
        bg_color = "#90EE90" if match else "#FFB6C1"
        text = f"{search_value} {'==' if match else '≠'} {node_value}"
        
        # 创建背景框
        frame_id = self.canvas.create_rectangle(
            x - 40, y - 15, x + 40, y + 15,
            fill=bg_color, outline="#333333", width=2
        )
        
        # 创建文本
        text_id = self.canvas.create_text(
            x, y, text=text,
            font=("Arial", 10, "bold"),
            fill="#333333"
        )
        
        self.window.update()
        
        # 动画效果
        if match:
            # 匹配成功 - 放大效果
            for scale in [1.0, 1.1, 1.2, 1.1, 1.0]:
                # 简化的缩放效果
                self.canvas.itemconfig(text_id, font=("Arial", int(10 * scale), "bold"))
                self.window.update()
                time.sleep(0.05)
        
        time.sleep(0.5)
        
        # 清理
        self.canvas.delete(frame_id)
        self.canvas.delete(text_id)
        self.window.update()
        
        return match
    
    def create_success_effect(self, x, y, message=None):
        """
        创建成功效果（星星爆炸粒子效果）
        """
        # 粒子效果
        self.create_particles(x, y, count=8, color="#FFD700", spread=40)
    
    def create_failure_effect(self, x, y, message="未找到"):
        """
        创建失败效果（红色X + 文字）
        """
        # 绘制X
        line1 = self.canvas.create_line(
            x - 20, y - 20, x + 20, y + 20,
            fill="#FF0000", width=4
        )
        line2 = self.canvas.create_line(
            x + 20, y - 20, x - 20, y + 20,
            fill="#FF0000", width=4
        )
        
        # 失败文字
        text_id = self.canvas.create_text(
            x, y + 30, text=message,
            font=("Arial", 12, "bold"),
            fill="#FF0000"
        )
        
        self.window.update()
        time.sleep(0.8)
        
        self.canvas.delete(line1)
        self.canvas.delete(line2)
        self.canvas.delete(text_id)
        self.window.update()


class NodeAnimator:
    """节点动画器 - 专门用于节点的各种动画效果"""
    
    def __init__(self, canvas, window, effects: AnimationEffects):
        self.canvas = canvas
        self.window = window
        self.effects = effects
    
    def shake_node(self, elements, intensity=5, duration=0.3):
        """
        抖动节点效果（用于错误或警告）
        
        Args:
            elements: 要抖动的元素列表
            intensity: 抖动强度
            duration: 持续时间
        """
        steps = int(duration / 0.02)
        
        for i in range(steps):
            offset = intensity * math.sin(i * 0.5) * (1 - i / steps)
            
            for elem in elements:
                try:
                    self.canvas.move(elem, offset, 0)
                except:
                    pass
            
            self.window.update()
            time.sleep(0.02)
            
            # 移回
            for elem in elements:
                try:
                    self.canvas.move(elem, -offset, 0)
                except:
                    pass
    
    def fade_out_node(self, rect_id, label_widgets, steps=15):
        """
        淡出节点效果
        
        Args:
            rect_id: 节点矩形ID
            label_widgets: 相关标签控件列表
            steps: 动画步数
        """
        # 逐渐缩小并淡化
        coords = self.canvas.coords(rect_id)
        if len(coords) < 4:
            return
        
        cx = (coords[0] + coords[2]) / 2
        cy = (coords[1] + coords[3]) / 2
        w = coords[2] - coords[0]
        h = coords[3] - coords[1]
        
        for i in range(steps):
            scale = 1 - (i / steps)
            nw = w * scale
            nh = h * scale
            
            self.canvas.coords(
                rect_id,
                cx - nw/2, cy - nh/2,
                cx + nw/2, cy + nh/2
            )
            self.window.update()
            time.sleep(0.02)
        
        # 隐藏标签
        for label in label_widgets:
            try:
                label.place_forget()
            except:
                pass
    
    def bounce_in_node(self, x, y, create_func, final_y=None):
        """
        弹跳进入效果
        
        Args:
            x, y: 起始位置
            create_func: 创建节点的函数
            final_y: 最终Y位置
        """
        if final_y is None:
            final_y = y
        
        start_y = y - 100  # 从上方开始
        bounce_heights = [40, 20, 10, 5]  # 递减的弹跳高度
        
        current_y = start_y
        
        # 下落
        while current_y < final_y:
            current_y += 8
            # 更新位置（需要外部实现）
            self.window.update()
            time.sleep(0.02)
        
        # 弹跳
        for bounce in bounce_heights:
            # 上弹
            for _ in range(int(bounce / 2)):
                current_y -= 2
                self.window.update()
                time.sleep(0.01)
            # 下落
            for _ in range(int(bounce / 2)):
                current_y += 2
                self.window.update()
                time.sleep(0.01)

