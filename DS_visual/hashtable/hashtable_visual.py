from tkinter import *
from tkinter import messagebox, filedialog
import json
import os
from datetime import datetime
from hashtable.hashtable_model import HashTableModel, TOMBSTONE
from DSL_utils import process_command as _pc
process_command = _pc

class HashtableVisualizer:
    def __init__(self, root, capacity: int = 11):
        self.window = root
        self.window.config(bg="#E8F4F9")  # 使用更柔和的背景色
        self.canvas = Canvas(self.window, bg="#FFFFFF", width=1350, height=500,
                           relief=RIDGE, bd=3)  # 使用更精致的边框样式
        self.canvas.pack(pady=10)  # 添加上下间距

        self.capacity = capacity
        self.model = HashTableModel(self.capacity)

        # 可视元素引用
        self.cell_rects = []
        self.cell_texts = []
        self.index_texts = []
        self.capacity = self.model.capacity

        # 布局参数
        self.start_x = 60
        self.start_y = 200
        self.cell_width = 90
        self.cell_height = 60
        self.spacing = 12

        # 控件与状态
        self.value_entry = StringVar()
        self.dsl_var = StringVar()
        self.batch_entry_var = StringVar()
        self.input_frame = None
        self.animating = False
        self.batch_queue = []
        self.batch_index = 0
        
        self.capacity_var = StringVar(value=str(self.capacity))
        self.resize_frame = None

        self.create_heading()
        self.create_buttons()
        self.update_display()

    def create_heading(self):
        # 创建标题容器
        title_frame = Frame(self.window, bg="#E8F4F9")
        title_frame.pack(fill=X, padx=20, pady=(15, 5))
        
        heading = Label(title_frame, text="散列表（线性探测法）可视化",
                       font=("Microsoft YaHei UI", 28, "bold"), 
                       bg="#E8F4F9", fg="#2C3E50")
        heading.pack()
        
        info = Label(title_frame, 
                    text="散列方式：h(x)=x%capacity；冲突处理：线性探测（向后逐位查找），删除使用墓碑（tombstone）",
                    font=("Microsoft YaHei UI", 12),
                    bg="#E8F4F9", fg="#34495E")
        info.pack(pady=(5, 0))

    def create_buttons(self):
        button_frame = Frame(self.window, bg="#E8F4F9")
        button_frame.place(x=20, y=540, width=1310, height=150)

        # 定义按钮样式
        btn_style = {
            'font': ("Microsoft YaHei UI", 11, "bold"),
            'width': 12,
            'height': 1,
            'relief': 'groove',
            'bd': 2,
            'cursor': 'hand2'  # 添加手型光标
        }

        # 第一行：操作按钮
        Button(button_frame, text="插入 Insert", bg="#3498DB", fg="white",
               activebackground="#2980B9", activeforeground="white",
               command=self.prepare_insert, **btn_style).grid(row=0, column=0, padx=8, pady=6)
        Button(button_frame, text="查找 Find", bg="#2ECC71", fg="white",
               activebackground="#27AE60", activeforeground="white",
               command=lambda: self.prepare_find(), **btn_style).grid(row=0, column=1, padx=8, pady=6)
        Button(button_frame, text="删除 Delete", bg="#E74C3C", fg="white",
               activebackground="#C0392B", activeforeground="white",
               command=lambda: self.prepare_delete(), **btn_style).grid(row=0, column=2, padx=8, pady=6)
        Button(button_frame, text="清空 Clear", bg="#95A5A6", fg="white",
               activebackground="#7F8C8D", activeforeground="white",
               command=self.clear_table, **btn_style).grid(row=0, column=3, padx=8, pady=6)
        Button(button_frame, text="返回主界面", bg="#9B59B6", fg="white",
               activebackground="#8E44AD", activeforeground="white",
               command=self.back_to_main, **btn_style).grid(row=0, column=4, padx=8, pady=6)
            # 新增：调整容量按钮
        Button(button_frame, text="调整容量", bg="#F39C12", fg="white",
            activebackground="#E67E22", activeforeground="white",
            command=self.prepare_resize, **btn_style).grid(row=0, column=4, padx=8, pady=6)

        # 创建一个优雅的命令输入区
        cmd_frame = Frame(button_frame, bg="white", relief="groove", bd=2)
        cmd_frame.grid(row=1, column=0, columnspan=4, sticky="ew", padx=8, pady=10)
        
        # 命令输入框
        Label(cmd_frame, text="命令:", font=("Microsoft YaHei UI", 11), bg="white", fg="#2C3E50").pack(side=LEFT, padx=(15,5), pady=8)
        dsl_entry = Entry(cmd_frame, textvariable=self.dsl_var, width=50,
                         font=("Microsoft YaHei UI", 11), relief="flat",
                         bg="white", highlightthickness=1,
                         highlightcolor="#3498DB")
        dsl_entry.pack(side=LEFT, padx=5, pady=8, fill=X, expand=True)
        dsl_entry.bind("<Return>", lambda e: self.process_dsl())
        
        # 设置初始示例命令
        self.dsl_var.set("create 23 17 35 8 42 29 56 67")
        dsl_entry.select_range(0, END)  # 默认全选，方便用户直接输入新命令
        
        # 添加带图标的提示标签
        cmd_hint = Label(cmd_frame, text="↑ 试试运行这个示例，或输入: insert x | find x | delete x | clear",
                        font=("Microsoft YaHei UI", 9), bg="white", fg="#2980B9")
        cmd_hint.pack(side=LEFT, padx=(10,5), pady=8)
        
        Button(cmd_frame, text="执行",
               font=("Microsoft YaHei UI", 11, "bold"),
               width=6, height=1,
               bg="#3498DB", fg="white",
               activebackground="#2980B9",
               activeforeground="white",
               relief="groove", bd=1,
               cursor="hand2",
               command=self.process_dsl).pack(side=LEFT, padx=(10,15), pady=8)

        # 创建文件操作按钮框架
        file_frame = Frame(button_frame, bg="#E8F4F9")
        file_frame.grid(row=1, column=4, rowspan=2, padx=6, pady=4)
        
        # 保存和打开按钮采用更现代的样式
        Button(file_frame, text="保存数据",
               font=("Microsoft YaHei UI", 11, "bold"),
               width=10, height=1,
               bg="#3498DB", fg="white",
               activebackground="#2980B9",
               activeforeground="white",
               relief="groove", bd=1,
               cursor="hand2",
               command=self.save_structure).pack(pady=2)
               
        Button(file_frame, text="打开数据",
               font=("Microsoft YaHei UI", 11, "bold"),
               width=10, height=1,
               bg="#2ECC71", fg="white",
               activebackground="#27AE60",
               activeforeground="white",
               relief="groove", bd=1,
               cursor="hand2",
               command=self.load_structure).pack(pady=2)

        # 统一设置 sticky 和 pady，确保对齐
        for child in button_frame.winfo_children():
            child.grid_configure(sticky="nsew")
        
            # 添加容量调整相关方法：
    def prepare_resize(self):
        """准备调整容量"""
        if self.animating: 
            return
        self._open_resize_input()

    def _open_resize_input(self):
        """打开容量调整输入框"""
        if self.resize_frame:
            self.resize_frame.destroy()
        
        # 创建容量调整输入框
        self.resize_frame = Frame(self.window, bg="#E8F4F9")
        self.resize_frame.place(x=500, y=680, width=300, height=80)
        
        # 添加样式背景
        resize_bg = Frame(self.resize_frame, bg="white", relief="groove", bd=2)
        resize_bg.place(relx=0.02, rely=0.1, relwidth=0.96, relheight=0.8)
        
        Label(resize_bg, text="新容量:", 
            font=("Microsoft YaHei UI", 11),
            bg="white", fg="#2C3E50").pack(side=LEFT, padx=(15,5), pady=4)
        
        # 显示当前容量作为提示
        current_info = Label(resize_bg, text=f"(当前: {self.capacity})", 
                            font=("Microsoft YaHei UI", 9),
                            bg="white", fg="#7F8C8D")
        current_info.pack(side=LEFT, padx=5, pady=4)
        
        capacity_entry = Entry(resize_bg, textvariable=self.capacity_var,
                            width=8, font=("Microsoft YaHei UI", 11),
                            relief="flat", bg="white",
                            highlightthickness=1,
                            highlightcolor="#F39C12")
        capacity_entry.pack(side=LEFT, padx=5, pady=4)
        
        Button(resize_bg, text="确认调整",
            font=("Microsoft YaHei UI", 10, "bold"),
            width=8, height=1,
            bg="#F39C12", fg="white",
            activebackground="#E67E22",
            activeforeground="white",
            relief="groove", bd=1,
            cursor="hand2",
            command=self._on_confirm_resize).pack(side=LEFT, padx=(10,5), pady=4)
        
        Button(resize_bg, text="取消",
            font=("Microsoft YaHei UI", 10, "bold"),
            width=6, height=1,
            bg="#95A5A6", fg="white",
            activebackground="#7F8C8D",
            activeforeground="white",
            relief="groove", bd=1,
            cursor="hand2",
            command=lambda: self._close_resize_input()).pack(side=LEFT, padx=5, pady=4)
        
        self.window.after(50, lambda: capacity_entry.focus_set())
        capacity_entry.select_range(0, END)

    def _on_confirm_resize(self):
        """确认调整容量"""
        try:
            new_capacity = int(self.capacity_var.get())
            if new_capacity <= 0:
                messagebox.showerror("错误", "容量必须是正整数")
                return
            
            if new_capacity == self.capacity:
                messagebox.showinfo("提示", "新容量与当前容量相同")
                self._close_resize_input()
                return
            
            # 检查新容量是否足够容纳当前元素
            if new_capacity < len(self.model):
                messagebox.showerror("错误", f"新容量({new_capacity})不能小于当前元素数量({len(self.model)})")
                return
            
            # 执行容量调整
            self._resize_table(new_capacity)
            self._close_resize_input()
            
        except ValueError:
            messagebox.showerror("错误", "请输入有效的整数容量")
        except Exception as e:
            messagebox.showerror("错误", f"调整容量失败: {str(e)}")

    def _resize_table(self, new_capacity: int):
        """执行表容量调整"""
        if self.animating:
            return
            
        self.animating = True
        self._set_buttons_state("disabled")
        
        try:
            # 保存当前有效元素
            valid_elements = []
            for item in self.model.table:
                if item is not None and item is not self.model.tombstone:
                    valid_elements.append(item)
            
            # 创建新模型
            old_capacity = self.capacity
            self.model = HashTableModel(new_capacity)
            self.capacity = new_capacity
            
            # 显示调整动画
            self._show_resize_animation(old_capacity, new_capacity, valid_elements)
            
        except Exception as e:
            self.animating = False
            self._set_buttons_state("normal")
            raise e

    def _show_resize_animation(self, old_capacity: int, new_capacity: int, elements: list):
        """显示容量调整动画"""
        # 第一步：显示旧表淡出
        self.canvas.delete("all")
        self.canvas.create_text(675, 250, text=f"容量调整: {old_capacity} → {new_capacity}", 
                            font=("Microsoft YaHei UI", 16, "bold"), fill="#2C3E50")
        
        # 绘制旧表（缩小并淡出）
        old_start_x = 675 - (old_capacity * (self.cell_width + self.spacing)) // 2
        for i in range(old_capacity):
            x = old_start_x + i * (self.cell_width + self.spacing)
            rect = self.canvas.create_rectangle(x, 300, x + self.cell_width, 300 + self.cell_height, 
                                            fill="#FFEAA7", outline="#FDCB6E", width=2)
            self.canvas.create_text(x + self.cell_width/2, 300 + self.cell_height/2, 
                                text=str(i), font=("Arial", 10))
        
        self.window.after(1000, lambda: self._show_new_table_animation(new_capacity, elements))

    def _show_new_table_animation(self, new_capacity: int, elements: list):
        """显示新表构建动画"""
        self.canvas.delete("all")
        
        # 绘制新表框架
        total_width = (self.cell_width + self.spacing) * new_capacity
        start_x = 675 - total_width // 2
        
        # 绘制空表
        cell_rects = []
        for i in range(new_capacity):
            x = start_x + i * (self.cell_width + self.spacing)
            rect = self.canvas.create_rectangle(x, 300, x + self.cell_width, 300 + self.cell_height, 
                                            fill="white", outline="#3498DB", width=2)
            cell_rects.append(rect)
            self.canvas.create_text(x + self.cell_width/2, 280, 
                                text=str(i), font=("Arial", 10, "bold"))
        
        self.canvas.create_text(675, 250, text=f"新容量: {new_capacity}", 
                            font=("Microsoft YaHei UI", 16, "bold"), fill="#2C3E50")
        
        # 逐步插入元素
        self._animate_elements_insertion(elements, start_x, cell_rects, new_capacity)

    def _animate_elements_insertion(self, elements: list, start_x: int, cell_rects: list, new_capacity: int):
        """动画显示元素重新插入过程"""
        if not elements:
            # 所有元素插入完成
            self.window.after(500, self._finish_resize)
            return
        
        element = elements[0]
        remaining_elements = elements[1:]
        
        # 计算新哈希位置
        new_index = self.model._hash(element)
        
        # 创建移动元素
        elem_x = 675
        elem_y = 150
        rect = self.canvas.create_rectangle(elem_x-30, elem_y-20, elem_x+30, elem_y+20, 
                                        fill="#ABEBC6", outline="#27AE60", width=2)
        text = self.canvas.create_text(elem_x, elem_y, text=str(element), 
                                    font=("Arial", 12, "bold"))
        
        # 目标位置
        target_x = start_x + new_index * (self.cell_width + self.spacing) + self.cell_width/2
        target_y = 300 + self.cell_height/2
        
        # 移动动画
        self._animate_element_move(rect, text, elem_x, elem_y, target_x, target_y, 
                                remaining_elements, start_x, cell_rects, new_capacity, element, new_index)

    def _animate_element_move(self, rect, text, start_x, start_y, target_x, target_y, 
                            remaining_elements, start_x_table, cell_rects, new_capacity, element, target_index):
        """动画显示单个元素移动"""
        steps = 20
        dx = (target_x - start_x) / steps
        dy = (target_y - start_y) / steps
        
        def move_step(step=0):
            if step < steps:
                self.canvas.move(rect, dx, dy)
                self.canvas.move(text, dx, dy)
                self.window.after(30, lambda: move_step(step + 1))
            else:
                # 移动完成，实际插入元素
                self.model.insert(element)
                self.canvas.delete(rect)
                self.canvas.delete(text)
                
                # 高亮显示插入的位置
                self.canvas.itemconfig(cell_rects[target_index], fill="#ABEBC6")
                self.canvas.create_text(target_x, target_y, text=str(element), 
                                    font=("Arial", 12, "bold"))
                
                # 继续插入下一个元素
                self.window.after(300, lambda: self._animate_elements_insertion(
                    remaining_elements, start_x_table, cell_rects, new_capacity))

        move_step()

    def _finish_resize(self):
        """完成容量调整"""
        self.animating = False
        self._set_buttons_state("normal")
        self.update_display()
        messagebox.showinfo("成功", f"容量已调整为 {self.capacity}")

    def _close_resize_input(self):
        """关闭容量调整输入框"""
        if self.resize_frame:
            self.resize_frame.destroy()
            self.resize_frame = None

    def process_dsl(self):
        text = self.dsl_var.get().strip()
        try:
            # 处理 create 命令的特殊情况
            if text.startswith("create"):
                # 解析 create 后的数字序列
                items = text.split()[1:]
                if not items:
                    messagebox.showerror("错误", "请在create后提供要插入的值，例如：create 1 2 3")
                    return
                # 转换为整数序列
                try:
                    values = [int(x) for x in items]
                except ValueError:
                    messagebox.showerror("错误", "create命令后请提供有效的整数值")
                    return
                # 设置批量队列并开始处理
                if len(values) > self.capacity:
                    if not messagebox.askyesno("容量不足", 
                        f"要插入 {len(values)} 个元素，capacity={self.capacity}。是否只插入前 {self.capacity} 个？"):
                        return
                    values = values[:self.capacity]
                self.batch_queue = values
                self.batch_index = 0
                self._set_buttons_state("disabled")
                self._batch_step()
            # 处理 insert 命令
            elif text.startswith("insert"):
                parts = text.split()
                if len(parts) != 2:
                    messagebox.showerror("错误", "插入命令格式：insert 值")
                    return
                try:
                    value = int(parts[1])
                    self.insert_value(value)
                except ValueError:
                    messagebox.showerror("错误", "请输入有效的整数值")
                    return
            # 处理 find/search 命令
            elif text.startswith("find") or text.startswith("search"):
                parts = text.split()
                if len(parts) != 2:
                    messagebox.showerror("错误", "查找命令格式：find 值 或 search 值")
                    return
                try:
                    value = int(parts[1])
                    self.find_value(value)
                except ValueError:
                    messagebox.showerror("错误", "请输入有效的整数值")
                    return
            # 处理 delete 命令
            elif text.startswith("delete"):
                parts = text.split()
                if len(parts) != 2:
                    messagebox.showerror("错误", "删除命令格式：delete 值")
                    return
                try:
                    value = int(parts[1])
                    self.delete_value(value)
                except ValueError:
                    messagebox.showerror("错误", "请输入有效的整数值")
                    return
            # 处理 clear 命令
            elif text.strip() == "clear":
                self.clear_table()
            else:
                messagebox.showerror("错误", "未知命令。支持的命令：create、insert、find/search、delete、clear")
        finally:
            self.dsl_var.set("")

    def _ensure_folder(self):
        base = os.path.dirname(os.path.abspath(__file__))
        p = os.path.join(base, "save", "hashtable")
        os.makedirs(p, exist_ok=True)
        return p

    def save_structure(self):
        payload = {"type": "hashtable", "capacity": self.capacity, "data": self.model.table}
        default_dir = self._ensure_folder()
        default_name = f"hashtable_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = filedialog.asksaveasfilename(initialdir=default_dir, initialfile=default_name, defaultextension=".json", filetypes=[("JSON","*.json")])
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        messagebox.showinfo("保存成功", f"已保存到 {filepath}")

    def load_structure(self):
        default_dir = self._ensure_folder()
        filepath = filedialog.askopenfilename(initialdir=default_dir, filetypes=[("JSON","*.json")])
        with open(filepath, "r", encoding="utf-8") as f:
            loaded = json.load(f)
        data = loaded["data"]
        # 校验并加载
        if len(data) != self.capacity:
            if messagebox.askyesno("容量不符", f"文件容量 {len(data)} 与当前 capacity {self.capacity} 不符，是否以文件容量为准并重建？"):
                self.capacity = len(data)
                self.model = HashTableModel(self.capacity)
            else:
                # 尽量 fit 到当前容量：截断或补 None
                data = (data + [None] * self.capacity)[:self.capacity]
        conv = []
        for v in data:
            if v == "__TOMBSTONE__":
                conv.append(self.model.tombstone)
            else:
                conv.append(v)
        self.model.table = conv
        self.update_display()
        messagebox.showinfo("加载成功", "已加载散列表")

    def prepare_insert(self, default_value: str = ""):
        if self.animating: return
        self._open_input("插入的值", default_value, action="insert")

    def prepare_find(self, default_value: str = ""):
        if self.animating: return
        self._open_input("查找的值", default_value, action="find")

    def prepare_delete(self, default_value: str = ""):
        if self.animating: return
        self._open_input("删除的值", default_value, action="delete")

    def _open_input(self, label_text, default_value, action):
        if self.input_frame:
            self.input_frame.destroy()  # 销毁旧的 input_frame
        self.value_entry.set(default_value)
        
        # 创建一个更现代的输入框
        self.input_frame = Frame(self.window, bg="#E8F4F9")
        self.input_frame.place(x=420, y=680, width=360, height=50)
        
        # 添加圆角效果的背景
        input_bg = Frame(self.input_frame, bg="white", relief="groove", bd=2)
        input_bg.place(relx=0.02, rely=0.1, relwidth=0.96, relheight=0.8)
        
        Label(input_bg, text=label_text + ":", 
              font=("Microsoft YaHei UI", 11),
              bg="white", fg="#2C3E50").pack(side=LEFT, padx=(15,5), pady=4)
              
        entry = Entry(input_bg, textvariable=self.value_entry,
                     width=12, font=("Microsoft YaHei UI", 11),
                     relief="flat", bg="white",
                     highlightthickness=1,
                     highlightcolor="#3498DB")
        entry.pack(side=LEFT, padx=5, pady=4)
        
        Button(input_bg, text="确认",
               font=("Microsoft YaHei UI", 11, "bold"),
               width=6, height=1,
               bg="#3498DB", fg="white",
               activebackground="#2980B9",
               activeforeground="white",
               relief="groove", bd=1,
               cursor="hand2",
               command=lambda: self._on_confirm(action)).pack(side=LEFT, padx=(10,5), pady=4)
        self.window.after(50, lambda: self.input_frame.focus_force())

    def _on_confirm(self, action):
        val = self.value_entry.get()
        if val == "":
            messagebox.showerror("错误", "请输入一个值")
            return
        if self.input_frame:
            self.input_frame.destroy()  # 销毁输入框
            self.input_frame = None
        if action == "insert":
            self.insert_value(val)
        elif action == "find":
            self.find_value(val)
        elif action == "delete":
            self.delete_value(val)

    def _on_confirm_value(self):
        # 默认按 insert 处理
        v = self.value_entry.get()
        if v.strip() == "":
            messagebox.showerror("错误", "请输入一个值")
            return
        self.insert_value(v)

    # ---------- 动画操作 ----------
    def animate_insert(self, value, target_idx, probe_path):
        """
        value: 要插入的值（字符串）
        target_idx: 最终插入位置索引（若 None 表示失败）
        probe_path: 探测的索引序列（用于高亮显示探测过程）
        """
        if self.animating:
            return
        self.animating = True
        self._set_buttons_state("disabled")
        # 起点：画布左侧外面飞入
        start_x = - (self.cell_width + 40)
        start_y = self.start_y
        rect = self.canvas.create_rectangle(start_x, start_y, start_x + self.cell_width, start_y + self.cell_height, fill="lightgreen", outline="black", width=2)
        text_id = self.canvas.create_text(start_x + self.cell_width/2, start_y + self.cell_height/2, text=str(value), font=("Arial", 14, "bold"))

        total_steps = 30
        target_x = self.start_x + (self.cell_width + self.spacing) * (target_idx if target_idx is not None else (len(probe_path)-1))
        dx = (target_x - start_x) / total_steps
        step_delay = 12
        # 在移动之前先做探测高亮动画
        def probe_and_move_then_place():
            # probe_path 高亮（逐个闪烁）
            def probe_step(i=0):
                if i < len(probe_path):
                    idx = probe_path[i]
                    rect_id = self.cell_rects[idx]
                    # 高亮当前探测格
                    self.canvas.itemconfig(rect_id, outline="red", width=3)
                    self.window.after(220, lambda: unhighlight_and_next(i))
                else:
                    # 探测完成后开始移动
                    move_step(0)

            def unhighlight_and_next(i):
                idx = probe_path[i]
                rect_id = self.cell_rects[idx]
                self.canvas.itemconfig(rect_id, outline="black", width=2)
                self.window.after(60, lambda: probe_step(i+1))

            probe_step()

        def move_step(step_i=0):
            nonlocal rect, text_id
            if step_i < total_steps:
                self.canvas.move(rect, dx, 0)
                self.canvas.move(text_id, dx, 0)
                self.window.after(step_delay, lambda: move_step(step_i + 1))
            else:
                # 删除临时移动形状，插入模型并刷新显示
                try:
                    inserted = self.model.insert(value)
                except Exception:
                    inserted = None
                self.canvas.delete(rect)
                self.canvas.delete(text_id)
                self.update_display()
                self.animating = False
                self._set_buttons_state("normal")

        probe_and_move_then_place()

    def insert_value(self, value):
        """由接口触发的插入（带动画）。"""
        if self.animating:
            return
        # 先模拟探测路径并返回最终位置（不修改 model）
        start = self.model._hash(value)
        i = start
        probe = []
        first_tomb = -1
        while True:
            probe.append(i)
            val = self.model.table[i]
            if val is None:
                target = first_tomb if first_tomb != -1 else i
                break
            if val is self.model.tombstone:
                if first_tomb == -1:
                    first_tomb = i
            if val == value:
                # 已存在：标记 probe path 并高亮提示（不插入）
                self._probe_highlight(probe, found=True, found_idx=i, msg=f"值已存在于索引 {i}")
                return
            i = (i + 1) % self.capacity
            if i == start:
                target = first_tomb if first_tomb != -1 else None
                break
        if target is None:
            # 表满
            self._probe_highlight(probe, found=False, found_idx=None, msg="散列表已满，无法插入")
            return
        # 执行动画：探测高亮 + 飞入放置
        self.animate_insert(value, target, probe)

    def _probe_highlight(self, probe_path, found=False, found_idx=None, msg=None):
        """通用的 probe 高亮：逐个闪烁，当 found=True 时高亮找到位置并提示 msg"""
        if self.animating:
            return
        self.animating = True
        self._set_buttons_state("disabled")

        def step(i=0):
            if i < len(probe_path):
                idx = probe_path[i]
                rid = self.cell_rects[idx]
                self.canvas.itemconfig(rid, outline="red", width=3)
                self.window.after(220, lambda: unhighlight(i))
            else:
                # 探测结束
                if found and found_idx is not None:
                    # 强调找到的位置
                    rid = self.cell_rects[found_idx]
                    self.canvas.itemconfig(rid, outline="lime", width=4)
                    self.window.after(600, finish)
                else:
                    self.window.after(200, finish)

        def unhighlight(i):
            idx = probe_path[i]
            rid = self.cell_rects[idx]
            self.canvas.itemconfig(rid, outline="black", width=2)
            self.window.after(60, lambda: step(i+1))

        def finish():
            if msg:
                messagebox.showinfo("提示", msg)
            self.animating = False
            self._set_buttons_state("normal")
            self.update_display()

        step()

    def find_value(self, value):
        """查找并高亮探测路径；找到的话突出显示格子并提示索引。"""
        if self.animating:
            return
        start = self.model._hash(value)
        i = start
        probe = []
        while True:
            probe.append(i)
            val = self.model.table[i]
            if val is None:
                # 遇到空位 => 不存在
                self._probe_highlight(probe, found=False, found_idx=None, msg=f"未找到 {value}")
                return
            if val is not self.model.tombstone and val == value:
                self._probe_highlight(probe, found=True, found_idx=i, msg=f"找到 {value}，索引 {i}")
                return
            i = (i + 1) % self.capacity
            if i == start:
                self._probe_highlight(probe, found=False, found_idx=None, msg=f"未找到 {value}（全表探测）")
                return

    def delete_value(self, value):
        """查找并用墓碑标记删除（带探测动画）。"""
        if self.animating:
            return
        start = self.model._hash(value)
        i = start
        probe = []
        while True:
            probe.append(i)
            val = self.model.table[i]
            if val is None:
                self._probe_highlight(probe, found=False, found_idx=None, msg=f"未找到 {value}，无法删除")
                return
            if val is not self.model.tombstone and val == value:
                # 做探测高亮，然后执行删除模型并刷新显示，同时在该格写上墓碑标记
                def after_probe():
                    try:
                        idx = self.model.delete(value)
                    except Exception:
                        idx = None
                    if idx is not None:
                        messagebox.showinfo("删除", f"已在索引 {idx} 用墓碑删除 {value}")
                    self.update_display()
                # 使用 _probe_highlight 并在 finish 后执行删除效果
                self._probe_highlight_with_callback(probe, found=True, found_idx=i, callback=after_probe)
                return
            i = (i + 1) % self.capacity
            if i == start:
                self._probe_highlight(probe, found=False, found_idx=None, msg=f"未找到 {value}（全表探测）")
                return

    def _probe_highlight_with_callback(self, probe_path, found, found_idx, callback):
        """与 _probe_highlight 类似，但 finish 后执行 callback"""
        if self.animating:
            return
        self.animating = True
        self._set_buttons_state("disabled")
        def step(i=0):
            if i < len(probe_path):
                idx = probe_path[i]
                rid = self.cell_rects[idx]
                self.canvas.itemconfig(rid, outline="red", width=3)
                self.window.after(220, lambda: unhighlight(i))
            else:
                if found and found_idx is not None:
                    rid = self.cell_rects[found_idx]
                    self.canvas.itemconfig(rid, outline="orange", width=4)
                    self.window.after(360, finish)
                else:
                    self.window.after(200, finish)
        def unhighlight(i):
            idx = probe_path[i]
            rid = self.cell_rects[idx]
            self.canvas.itemconfig(rid, outline="black", width=2)
            self.window.after(60, lambda: step(i+1))
        def finish():
            try:
                callback()
            except Exception:
                pass
            self.animating = False
            self._set_buttons_state("normal")
            self.update_display()
        step()

    def clear_table(self):
        if self.animating:
            return
        # 如果已经空了，提示
        if all(v is None for v in self.model.table):
            messagebox.showinfo("清空", "散列表已为空")
            return
        # 逐格清空动画（从右到左）
        self.animating = True
        self._set_buttons_state("disabled")
        idxs = [i for i in range(self.capacity-1, -1, -1)]
        def clear_step(i=0):
            if i >= len(idxs):
                self.animating = False
                self._set_buttons_state("normal")
                return
            idx = idxs[i]
            rid = self.cell_rects[idx]
            # 做一个闪烁然后清空
            self.canvas.itemconfig(rid, fill="#ffdddd")
            self.window.after(80, lambda: self.canvas.itemconfig(rid, fill="white"))
            # 模型清除对应位置（设置为 None）
            try:
                self.model.table[idx] = None
            except Exception:
                pass
            self.update_display()
            self.window.after(100, lambda: clear_step(i+1))
        clear_step()

    # ---------- 批量构建 ----------
    def start_batch_build(self):
        if self.animating:
            return
        text = self.batch_entry_var.get().strip()
        if not text:
            messagebox.showinfo("提示", "请输入要批量构建的值，例如：1,2,3")
            return
        items = [s.strip() for s in text.replace("，", ",").split(",") if s.strip() != ""]
        if not items:
            messagebox.showinfo("提示", "未解析到有效值")
            return
        # 若 items 长度超 capacity，提示截断或扩容：这里简单截断
        if len(items) > self.capacity:
            if not messagebox.askyesno("容量不足", f"要插入 {len(items)} 个元素，capacity={self.capacity}。是否只插入前 {self.capacity} 个？"):
                return
            items = items[:self.capacity]
        self.batch_queue = items
        self.batch_index = 0
        self._set_buttons_state("disabled")
        self._batch_step()

    def _batch_step(self):
        if self.batch_index >= len(self.batch_queue):
            self.batch_queue = []
            self.batch_index = 0
            self._set_buttons_state("normal")
            return
        val = self.batch_queue[self.batch_index]
        self.batch_index += 1
        # 直接调用 insert_value（含动画），在其完成后继续下一项
        def continue_batch():
            if self.animating:
                # poll until not animating
                self.window.after(120, continue_batch)
            else:
                self._batch_step()
        # initiate animation and poll for finish
        self.insert_value(val)
        self.window.after(150, continue_batch)

    # ---------- 显示更新 ----------
    def update_display(self):
        self.canvas.delete("all")
        self.cell_rects.clear()
        self.cell_texts.clear()
        self.index_texts.clear()

        total_width = (self.cell_width + self.spacing) * self.capacity
        # 背景框 - 使用渐变色效果
        gradient_colors = ["#F5F9FF", "#EDF7FF"]
        for i in range(2):
            self.canvas.create_rectangle(
                self.start_x - 8 + i*2, self.start_y - 8 + i*2,
                self.start_x + total_width + 8 - i*2, self.start_y + self.cell_height + 8 - i*2,
                outline="#D0E3FF", fill=gradient_colors[i], width=1)

        # 说明区域
        info_x = 20
        info_y = 20
        info_w = 380
        self.canvas.create_rectangle(info_x-8, info_y-8, info_x + info_w + 8, info_y + 170, fill="#F7FFF7", outline="#DDD")
        info_text = f"容量: {self.capacity}  有效元素数: {len(self.model)}"
        self.canvas.create_text(info_x+6, info_y+6, text=info_text, anchor="nw", font=("Arial", 12))
        inst = ("说明：\n"
                "1) 插入: insert x（或按钮）\n"
                "2) 查找: find x\n"
                "3) 删除: delete x（使用墓碑标记）\n"
                "4) 清空: clear")
        self.canvas.create_text(info_x+6, info_y+36, text=inst, anchor="nw", width=info_w, font=("Arial", 11))

        # 绘制格子
        for i in range(self.capacity):
            x = self.start_x + i * (self.cell_width + self.spacing)
            rect = self.canvas.create_rectangle(x, self.start_y, x + self.cell_width, self.start_y + self.cell_height, fill="white", outline="black", width=2)
            self.cell_rects.append(rect)
            # index 上方
            idx_text = self.canvas.create_text(x + self.cell_width/2, self.start_y - 16, text=str(i), font=("Arial", 10, "bold"))
            self.index_texts.append(idx_text)
            # cell 内容：根据模型
            val = self.model.table[i]
            if val is None:
                txt = ""
            elif val is self.model.tombstone:
                txt = "墓碑"
                # tombstone 特殊填色
                self.canvas.itemconfig(rect, fill="#eeeeee")
            else:
                txt = str(val)
            text_id = self.canvas.create_text(x + self.cell_width/2, self.start_y + self.cell_height/2, text=txt, font=("Arial", 12))
            self.cell_texts.append(text_id)
        # 右侧注释
        self.canvas.create_text(self.start_x + total_width + 40, self.start_y + self.cell_height/2, text="散列表格", font=("Arial", 12, "bold"))

    def _set_buttons_state(self, state):
        # enable/disable window-level buttons by scanning all children
        for w in self.window.winfo_children():
            try:
                if isinstance(w, Frame):
                    for c in w.winfo_children():
                        try:
                            c.config(state=state)
                        except Exception:
                            pass
            except Exception:
                pass

    def back_to_main(self):
        if self.animating:
            messagebox.showinfo("提示", "正在动画执行，无法返回")
            return
        try:
            self.window.destroy()
        except Exception:
            pass

if __name__ == "__main__":
    root = Tk()
    root.title("散列表可视化")
    root.geometry("1350x770")
    root.minsize(1350, 770)
    HashtableVisualizer(root, capacity=13)
    root.mainloop()