"""
增强操作模块 - 提供链表的高级可视化操作
包含：搜索、遍历、反转、排序等操作的动画实现
"""
from tkinter import Label, messagebox, LAST
import time
import random


class EnhancedLinkedListOperations:
    """增强的链表操作类"""
    
    def __init__(self, visualizer):
        """
        初始化增强操作
        
        Args:
            visualizer: LinkList可视化器实例
        """
        self.vis = visualizer
        self.canvas = visualizer.canvas_make
        self.window = visualizer.window
        
        # 动画速度 (秒)
        self.animation_delay = 0.5
        
        # 搜索伪代码
        self.SEARCH_PSEUDOCODE = [
            ("// 链表搜索算法", "comment"),
            ("Node* current = head;", "code"),
            ("int index = 0;", "code"),
            ("while (current != NULL) {", "code"),
            ("    if (current->data == target) {", "code"),
            ("        return index; // 找到!", "code"),
            ("    }", "code"),
            ("    current = current->next;", "code"),
            ("    index++;", "code"),
            ("}", "code"),
            ("return -1; // 未找到", "code"),
        ]
        
        # 遍历伪代码
        self.TRAVERSE_PSEUDOCODE = [
            ("// 链表遍历算法", "comment"),
            ("Node* current = head;", "code"),
            ("while (current != NULL) {", "code"),
            ("    visit(current->data);", "code"),
            ("    current = current->next;", "code"),
            ("}", "code"),
            ("// 遍历完成", "comment"),
        ]
        
        # 反转伪代码
        self.REVERSE_PSEUDOCODE = [
            ("// 链表原地反转算法", "comment"),
            ("Node* prev = NULL;", "code"),
            ("Node* curr = head;", "code"),
            ("Node* next = NULL;", "code"),
            ("while (curr != NULL) {", "code"),
            ("    next = curr->next;", "code"),
            ("    curr->next = prev;", "code"),
            ("    prev = curr;", "code"),
            ("    curr = next;", "code"),
            ("}", "code"),
            ("head = prev;", "code"),
            ("// 反转完成", "comment"),
        ]
    
    def set_animation_speed(self, speed):
        """设置动画速度"""
        self.animation_delay = speed
    
    def search_with_animation(self, target_value):
        """
        带动画的搜索操作
        
        Args:
            target_value: 要搜索的值
        
        Returns:
            int: 找到的索引（1-based），未找到返回-1
        """
        # 检查链表是否为空
        if len(self.vis.node_value_store) == 0:
            messagebox.showinfo("提示", "链表为空，无法搜索")
            return -1
        
        # 设置伪代码面板
        try:
            self.vis.pseudocode_panel.set_pseudocode("search")
            self.vis.pseudocode_panel.highlight_line(0, "开始搜索操作")
        except:
            pass
        
        self.vis.toggle_action_buttons("disabled")
        self.vis.information.config(text=f"🔍 开始搜索值: {target_value}")
        
        # 创建搜索指针
        search_ptr = self._create_search_pointer()
        search_label = Label(
            self.canvas, text="🔎 search", 
            font=("Arial", 11, "bold"), 
            bg="#FF6B6B", fg="white"
        )
        search_label.place(x=35, y=150)
        
        found_index = -1
        target_str = str(target_value)
        
        # 高亮初始化
        try:
            self.vis.pseudocode_panel.highlight_line(1, "初始化current = head")
            self.window.update()
            time.sleep(self.animation_delay)
        except:
            pass
        
        # 遍历搜索
        for i, node_value in enumerate(self.vis.node_value_store):
            # 高亮while循环
            try:
                self.vis.pseudocode_panel.highlight_line(3, f"检查节点 {i+1}")
                self.window.update()
            except:
                pass
            
            # 移动搜索指针到当前节点
            if i < len(self.vis.linked_list_position):
                pos = self.vis.linked_list_position[i]
                target_x = pos[4] + 50
                target_y = pos[5] - 30
                
                # 动画移动搜索指针
                self._animate_pointer_move(search_ptr, search_label, target_x, target_y)
            
            # 高亮当前节点
            self._highlight_current_node(i, "#90EE90")  # 浅绿色
            
            self.vis.information.config(text=f"🔍 比较: {node_value} {'==' if str(node_value) == target_str else '≠'} {target_value}")
            self.window.update()
            
            # 显示比较动画
            self._show_comparison_popup(i, target_value, str(node_value) == target_str)
            
            # 高亮比较代码
            try:
                self.vis.pseudocode_panel.highlight_line(4, f"比较 {node_value} 和 {target_value}")
                self.window.update()
            except:
                pass
            
            time.sleep(self.animation_delay)
            
            if str(node_value) == target_str:
                # 找到了！
                found_index = i + 1  # 1-based
                
                # 高亮找到代码
                try:
                    self.vis.pseudocode_panel.highlight_line(5, f"找到! 位置: {found_index}")
                except:
                    pass
                
                # 特殊高亮找到的节点
                self._highlight_found_node(i)
                
                # 显示成功效果
                self._show_success_effect(i)
                
                self.vis.information.config(text=f"✅ 找到值 {target_value}，位置: {found_index}")
                break
            else:
                # 恢复节点颜色
                self._reset_node_highlight(i)
                
                # 高亮移动到下一个
                try:
                    self.vis.pseudocode_panel.highlight_line(7, "移动到下一个节点")
                except:
                    pass
        
        if found_index == -1:
            # 未找到
            try:
                self.vis.pseudocode_panel.highlight_line(10, "搜索完成，未找到")
            except:
                pass
            
            self.vis.information.config(text=f"❌ 未找到值 {target_value}")
            self._show_not_found_effect()
        
        # 清理搜索指针
        time.sleep(0.5)
        try:
            self.canvas.delete(search_ptr)
            search_label.destroy()
        except:
            pass
        
        self.vis.toggle_action_buttons("normal")
        return found_index
    
    def traverse_with_animation(self):
        """
        带动画的链表遍历操作 - 展示如何访问每个节点
        """
        if len(self.vis.node_value_store) == 0:
            messagebox.showinfo("提示", "链表为空，无法遍历")
            return
        
        # 设置伪代码面板
        try:
            self.vis.pseudocode_panel.set_pseudocode("traverse")
            self.vis.pseudocode_panel.highlight_line(0, "开始遍历操作")
        except:
            pass
        
        self.vis.toggle_action_buttons("disabled")
        self.vis.information.config(text="🚶 开始遍历链表...")
        
        # 创建遍历指针
        traverse_ptr = self._create_traverse_pointer()
        traverse_label = Label(
            self.canvas, text="👆 visitor", 
            font=("Arial", 11, "bold"), 
            bg="#4ECDC4", fg="white"
        )
        traverse_label.place(x=30, y=150)
        
        # 创建访问顺序显示框
        visited_values = []
        visited_label = Label(
            self.canvas, text="已访问: []",
            font=("Consolas", 11, "bold"),
            bg="#2D2D2D", fg="#00FF00"
        )
        visited_label.place(x=450, y=50)
        
        # 高亮初始化
        try:
            self.vis.pseudocode_panel.highlight_line(1, "初始化 current = head")
            self.window.update()
            time.sleep(self.animation_delay)
        except:
            pass
        
        # 遍历每个节点
        for i in range(len(self.vis.node_value_store)):
            # 高亮while循环
            try:
                self.vis.pseudocode_panel.highlight_line(2, f"节点 {i+1} 不为空")
            except:
                pass
            
            # 移动遍历指针
            if i < len(self.vis.linked_list_position):
                pos = self.vis.linked_list_position[i]
                target_x = pos[4] + 50
                target_y = pos[5] - 30
                self._animate_pointer_move(traverse_ptr, traverse_label, target_x, target_y)
            
            # 高亮当前节点
            self._highlight_current_node(i, "#FFD93D")  # 金黄色
            
            # 高亮visit代码
            try:
                self.vis.pseudocode_panel.highlight_line(3, f"访问节点 data = {self.vis.node_value_store[i]}")
            except:
                pass
            
            # 访问动画
            self._show_visit_animation(i)
            
            # 更新已访问列表
            visited_values.append(str(self.vis.node_value_store[i]))
            visited_label.config(text=f"已访问: [{', '.join(visited_values)}]")
            
            self.vis.information.config(text=f"🚶 访问节点 {i+1}: 值 = {self.vis.node_value_store[i]}")
            self.window.update()
            
            time.sleep(self.animation_delay)
            
            # 恢复节点颜色
            self._reset_node_highlight(i)
            
            # 高亮移动到下一个
            try:
                self.vis.pseudocode_panel.highlight_line(4, "current = current->next")
            except:
                pass
        
        # 遍历完成
        try:
            self.vis.pseudocode_panel.highlight_line(6, "遍历完成!")
        except:
            pass
        
        self.vis.information.config(text=f"✅ 遍历完成！共访问 {len(visited_values)} 个节点")
        
        # 清理
        time.sleep(1)
        try:
            self.canvas.delete(traverse_ptr)
            traverse_label.destroy()
            visited_label.destroy()
        except:
            pass
        
        self.vis.toggle_action_buttons("normal")
    
    def reverse_with_animation(self):
        """
        带动画的链表反转操作 - 展示原地反转的过程
        """
        n = len(self.vis.node_value_store)
        if n < 2:
            messagebox.showinfo("提示", "链表节点少于2个，无需反转")
            return
        
        # 设置伪代码面板
        try:
            self.vis.pseudocode_panel.set_pseudocode("reverse")
            self.vis.pseudocode_panel.highlight_line(0, "开始反转操作")
        except:
            pass
        
        self.vis.toggle_action_buttons("disabled")
        self.vis.information.config(text="🔄 开始反转链表...")
        
        # 创建三个指针标签
        prev_label = Label(
            self.canvas, text="prev=NULL",
            font=("Arial", 10, "bold"),
            bg="#FF6B6B", fg="white"
        )
        prev_label.place(x=10, y=220)
        
        curr_label = Label(
            self.canvas, text="curr",
            font=("Arial", 10, "bold"),
            bg="#4ECDC4", fg="white"
        )
        
        next_label = Label(
            self.canvas, text="next",
            font=("Arial", 10, "bold"),
            bg="#95E1D3", fg="black"
        )
        
        # 高亮初始化指针
        try:
            self.vis.pseudocode_panel.highlight_lines([1, 2, 3], "初始化 prev, curr, next 指针")
            self.window.update()
            time.sleep(self.animation_delay)
        except:
            pass
        
        # 获取原始节点顺序（值）
        original_values = list(self.vis.node_value_store)
        
        # 逐步反转（只反转逻辑值，保持可视化节点位置）
        for step in range(n):
            curr_idx = step
            
            # 放置curr标签
            if curr_idx < len(self.vis.linked_list_position):
                pos = self.vis.linked_list_position[curr_idx]
                curr_label.place(x=pos[4] + 30, y=pos[5] - 25)
            
            # 高亮while循环
            try:
                self.vis.pseudocode_panel.highlight_line(4, f"循环第 {step+1} 次")
            except:
                pass
            
            # 高亮当前节点
            self._highlight_current_node(curr_idx, "#FFD93D")
            
            self.vis.information.config(text=f"🔄 反转步骤 {step+1}/{n}: 处理节点 {original_values[curr_idx]}")
            self.window.update()
            time.sleep(self.animation_delay / 2)
            
            # 如果有下一个节点，显示next指针
            if curr_idx + 1 < n and curr_idx + 1 < len(self.vis.linked_list_position):
                next_pos = self.vis.linked_list_position[curr_idx + 1]
                next_label.place(x=next_pos[4] + 30, y=next_pos[5] - 25)
                
                try:
                    self.vis.pseudocode_panel.highlight_line(5, "保存 next = curr->next")
                except:
                    pass
            
            # 显示箭头反转动画
            self._show_arrow_reverse_animation(curr_idx)
            
            try:
                self.vis.pseudocode_panel.highlight_line(6, "反转指针 curr->next = prev")
            except:
                pass
            
            time.sleep(self.animation_delay / 2)
            
            # 更新prev标签位置
            if curr_idx < len(self.vis.linked_list_position):
                pos = self.vis.linked_list_position[curr_idx]
                prev_label.config(text="prev")
                prev_label.place(x=pos[4] + 30, y=pos[5] + 70)
            
            try:
                self.vis.pseudocode_panel.highlight_lines([7, 8], "移动 prev 和 curr")
            except:
                pass
            
            # 恢复节点颜色
            self._reset_node_highlight(curr_idx)
            
            time.sleep(self.animation_delay / 2)
        
        # 执行实际的值反转
        reversed_values = list(reversed(original_values))
        
        # 更新逻辑存储
        for i, val in enumerate(reversed_values):
            try:
                self.vis.node_value_store[i] = val
            except:
                pass
        
        # 更新显示的值
        for i in range(len(self.vis.linked_list_data_next_store)):
            try:
                self.vis.linked_list_data_next_store[i][0].config(text=str(reversed_values[i]))
            except:
                pass
        
        # 高亮完成
        try:
            self.vis.pseudocode_panel.highlight_line(11, "反转完成!")
        except:
            pass
        
        self.vis.information.config(text=f"✅ 链表反转完成! 新顺序: {reversed_values}")
        
        # 清理指针标签
        time.sleep(0.5)
        try:
            prev_label.destroy()
            curr_label.destroy()
            next_label.destroy()
        except:
            pass
        
        self.vis.toggle_action_buttons("normal")
    
    def get_length_with_animation(self):
        """
        带动画显示链表长度计算过程
        """
        if len(self.vis.node_value_store) == 0:
            self.vis.information.config(text="📏 链表长度: 0（空链表）")
            return 0
        
        self.vis.toggle_action_buttons("disabled")
        self.vis.information.config(text="📏 开始计算链表长度...")
        
        # 创建计数器显示
        count_label = Label(
            self.canvas, text="Count: 0",
            font=("Arial", 14, "bold"),
            bg="#2D2D2D", fg="#00FF00"
        )
        count_label.place(x=550, y=50)
        
        count = 0
        for i in range(len(self.vis.node_value_store)):
            count += 1
            
            # 高亮当前节点
            self._highlight_current_node(i, "#87CEEB")
            
            count_label.config(text=f"Count: {count}")
            self.vis.information.config(text=f"📏 计数: 节点 {count}")
            self.window.update()
            
            time.sleep(self.animation_delay / 2)
            
            # 恢复颜色
            self._reset_node_highlight(i)
        
        self.vis.information.config(text=f"📏 链表长度: {count}")
        
        # 清理
        time.sleep(1)
        try:
            count_label.destroy()
        except:
            pass
        
        self.vis.toggle_action_buttons("normal")
        return count
    
    # ========== 辅助方法 ==========
    
    def _create_search_pointer(self):
        """创建搜索指针（三角形）"""
        return self.canvas.create_polygon(
            50, 180, 35, 210, 65, 210,
            fill="#FF6B6B", outline="#333333", width=2
        )
    
    def _create_traverse_pointer(self):
        """创建遍历指针"""
        return self.canvas.create_polygon(
            50, 180, 35, 210, 65, 210,
            fill="#4ECDC4", outline="#333333", width=2
        )
    
    def _animate_pointer_move(self, ptr_id, label, target_x, target_y):
        """动画移动指针"""
        coords = self.canvas.coords(ptr_id)
        if len(coords) < 6:
            return
        
        # 计算当前中心
        curr_x = sum(coords[::2]) / 3
        curr_y = sum(coords[1::2]) / 3
        
        steps = 15
        dx = (target_x - curr_x) / steps
        dy = (target_y - curr_y) / steps
        
        for _ in range(steps):
            self.canvas.move(ptr_id, dx, dy)
            try:
                label.place_configure(
                    x=label.winfo_x() + dx,
                    y=label.winfo_y() + dy
                )
            except:
                pass
            self.window.update()
            time.sleep(0.02)
    
    def _highlight_current_node(self, idx, color):
        """高亮指定索引的节点"""
        if idx < len(self.vis.linked_list_canvas_small_widget):
            widgets = self.vis.linked_list_canvas_small_widget[idx]
            for widget in widgets:
                try:
                    # 只修改矩形的填充色
                    if self.canvas.type(widget) == "rectangle":
                        self.canvas.itemconfig(widget, fill=color, width=4)
                except:
                    pass
    
    def _reset_node_highlight(self, idx):
        """重置节点高亮"""
        if idx < len(self.vis.linked_list_canvas_small_widget):
            widgets = self.vis.linked_list_canvas_small_widget[idx]
            for i, widget in enumerate(widgets):
                try:
                    if self.canvas.type(widget) == "rectangle":
                        # data和next使用深蓝色，main_container保持透明
                        fill = "#1E3A5F" if i < 2 else ""
                        self.canvas.itemconfig(widget, fill=fill, width=3)
                except:
                    pass
    
    def _highlight_found_node(self, idx):
        """特殊高亮找到的节点"""
        if idx < len(self.vis.linked_list_canvas_small_widget):
            widgets = self.vis.linked_list_canvas_small_widget[idx]
            for _ in range(5):
                for widget in widgets:
                    try:
                        self.canvas.itemconfig(widget, fill="#00FF00", width=5)
                    except:
                        pass
                self.window.update()
                time.sleep(0.1)
                
                for widget in widgets:
                    try:
                        self.canvas.itemconfig(widget, fill="#FFD700", width=5)
                    except:
                        pass
                self.window.update()
                time.sleep(0.1)
    
    def _show_comparison_popup(self, idx, target, is_match):
        """显示比较弹窗"""
        if idx >= len(self.vis.linked_list_position):
            return
        
        pos = self.vis.linked_list_position[idx]
        x = pos[4] + 50
        y = pos[5] - 60
        
        bg_color = "#90EE90" if is_match else "#FFB6C1"
        symbol = "✓" if is_match else "✗"
        
        popup = Label(
            self.canvas,
            text=symbol,
            font=("Arial", 16, "bold"),
            bg=bg_color,
            fg="#333333",
            padx=5, pady=2
        )
        popup.place(x=x, y=y)
        self.window.update()
        
        time.sleep(0.3)
        popup.destroy()
    
    def _show_visit_animation(self, idx):
        """显示访问动画"""
        if idx >= len(self.vis.linked_list_position):
            return
        
        pos = self.vis.linked_list_position[idx]
        x = pos[4] + 50
        y = pos[5] + 35
        
        # 创建小的访问标记
        visit_marker = self.canvas.create_oval(
            x - 10, y - 10, x + 10, y + 10,
            fill="#4ECDC4", outline="#333333", width=2
        )
        
        self.window.update()
        time.sleep(0.2)
        
        self.canvas.delete(visit_marker)
    
    def _show_success_effect(self, idx):
        """显示成功效果"""
        if idx >= len(self.vis.linked_list_position):
            return
        
        pos = self.vis.linked_list_position[idx]
        x = pos[4] + 50
        y = pos[5] + 35
        
        # 创建星星效果
        for i in range(8):
            angle = i * 45
            import math
            dx = 30 * math.cos(math.radians(angle))
            dy = 30 * math.sin(math.radians(angle))
            
            star = self.canvas.create_oval(
                x + dx - 4, y + dy - 4,
                x + dx + 4, y + dy + 4,
                fill="#FFD700", outline=""
            )
            self.window.update()
            time.sleep(0.03)
            self.canvas.delete(star)
    
    def _show_not_found_effect(self):
        """显示未找到效果"""
        # 在画布中央显示红色X
        cx, cy = 600, 250
        
        line1 = self.canvas.create_line(
            cx - 30, cy - 30, cx + 30, cy + 30,
            fill="#FF0000", width=5
        )
        line2 = self.canvas.create_line(
            cx + 30, cy - 30, cx - 30, cy + 30,
            fill="#FF0000", width=5
        )
        
        self.window.update()
        time.sleep(0.5)
        
        self.canvas.delete(line1)
        self.canvas.delete(line2)
    
    def _show_arrow_reverse_animation(self, idx):
        """显示箭头反转动画"""
        if idx >= len(self.vis.linked_list_position):
            return
        
        pos = self.vis.linked_list_position[idx]
        x = pos[0] + 75
        y = pos[1] + 15
        
        # 创建反转箭头提示
        reverse_arrow = self.canvas.create_line(
            x + 30, y, x - 30, y,
            arrow=LAST, fill="#FF6B6B", width=3,
            arrowshape=(10, 12, 4)
        )
        
        self.window.update()
        time.sleep(0.3)
        
        self.canvas.delete(reverse_arrow)

