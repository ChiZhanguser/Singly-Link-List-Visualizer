import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from datetime import datetime
from stack.stack_model import StackModel
import storage
import stack.stack_api as stack_api
from DSL_utils import process_command

class StackVisualizer:
    def __init__(self, root):
        self.window = root
        
        # --- 美化: 1. 定义样式和字体 ---
        self.style = ttk.Style(self.window)
        try:
            if os.name == 'nt':
                self.style.theme_use('clam')
            else:
                self.style.theme_use('clam')
        except tk.TclError:
            pass 

        # 定义字体
        self.font_large_bold = ("Segoe UI", 28, "bold")
        self.font_medium = ("Segoe UI", 16)
        self.font_normal_bold = ("Segoe UI", 13, "bold")
        self.font_normal = ("Segoe UI", 12)
        self.font_small = ("Segoe UI", 11)

        # 定义颜色
        self.bg_color = "#F0F0F0"       
        self.header_color = "#003366" 
        self.canvas_bg = "#FFFFFF"
        self.accent_color = "#6C9EFF"
        self.stack_fill = "#B0E0E6"    
        self.stack_outline = "#333333" 
        
        # 配置 ttk 样式
        self.style.configure('.', font=self.font_normal, background=self.bg_color)
        self.style.configure('TLabel', background=self.bg_color)
        self.style.configure('TFrame', background=self.bg_color)

        # --- 美化: 2. 定义彩色按钮样式 (使用 configure) ---
        self.style.configure("success.TButton", font=self.font_normal_bold, background="#28a745", foreground="white")
        self.style.configure("danger.TButton", font=self.font_normal_bold, background="#dc3545", foreground="white")
        self.style.configure("warning.TButton", font=self.font_normal_bold, background="#ffc107", foreground="black") 
        self.style.configure("primary.TButton", font=self.font_normal_bold, background="#007bff", foreground="white")
        self.style.configure("info.TButton", font=self.font_normal_bold, background=self.accent_color, foreground="white")

        # --- [!!! 关键修复 !!!] ---
        # 解决某些主题下 background 和 foreground 不生效的问题
        # 必须同时 "map" (映射) foreground 才能保证文字在 !disabled 状态下可见
        self.style.map("success.TButton",
                       background=[('active', '#218838'), ('!disabled', '#28a745')],
                       foreground=[('active', 'white'), ('!disabled', 'white')]) # <-- 增加 foreground 映射
        self.style.map("danger.TButton",
                       background=[('active', '#c82333'), ('!disabled', '#dc3545')],
                       foreground=[('active', 'white'), ('!disabled', 'white')]) # <-- 增加 foreground 映射
        self.style.map("warning.TButton",
                       background=[('active', '#e0a800'), ('!disabled', '#ffc107')],
                       foreground=[('active', 'black'), ('!disabled', 'black')]) # <-- 确保 active 和 !disabled 都有
        self.style.map("primary.TButton",
                       background=[('active', '#0069d9'), ('!disabled', '#007bff')],
                       foreground=[('active', 'white'), ('!disabled', 'white')]) # <-- 增加 foreground 映射
        self.style.map("info.TButton",
                       background=[('active', '#5A8DFF'), ('!disabled', self.accent_color)],
                       foreground=[('active', 'white'), ('!disabled', 'white')]) # <-- 增加 foreground 映射
        
        # --- 美化: 3. 更新窗口和画布样式 ---
        self.window.config(bg=self.bg_color)
        
        self.canvas = tk.Canvas(self.window, bg=self.canvas_bg, width=1350, height=500, 
                                relief=tk.FLAT, bd=1, highlightbackground="#BDBDBD")
        self.canvas.pack(pady=(0, 10)) 

        # 默认 capacity 与模型
        self.capacity = 10
        self.model = StackModel(self.capacity)
        
        # 画布元素引用
        self.stack_rectangles = []
        self.stack_labels = []
        
        # 布局参数
        self.start_x = 200
        self.start_y = 300
        self.cell_width = 80
        self.cell_height = 60
        self.spacing = 10
        
        # 控件状态与变量
        self.value_entry = tk.StringVar()
        self.batch_entry_var = tk.StringVar()
        self.dsl_var = tk.StringVar()
        self.input_frame = None
        self.push_btn = None
        self.pop_btn = None
        self.clear_btn = None
        self.back_btn = None
        self.confirm_btn = None
        self.batch_build_btn = None

        self.batch_queue = []
        self.batch_index = 0

        self.animating = False

        # 初始化界面
        self.create_heading()
        self.create_buttons()
        self.update_display()

        # 注册到 stack_api
        stack_api.register(self)

    def create_heading(self):
        # --- 美化: 4. 使用 ttk.Label 并动态居中 ---
        heading = ttk.Label(self.window, text="栈 (顺序栈) 的可视化",
                            font=self.font_large_bold, foreground=self.header_color)
        heading.place(relx=0.5, y=20, anchor="n")

        info = ttk.Label(self.window, text="栈是一种后进先出 (LIFO) 的数据结构，只能在栈顶进行插入和删除操作",
                        font=self.font_medium, foreground="black")
        info.place(relx=0.5, y=80, anchor="n")

    def create_buttons(self):
        # --- 美化: 5. 使用 ttk.Frame 和 ttk.Button ---
        button_frame = ttk.Frame(self.window)
        button_frame.place(x=50, y=530, width=1250, height=180) 

        btn_padding = (10, 8) 
        
        self.push_btn = ttk.Button(button_frame, text="入栈 (Push)",
                                   style="success.TButton", padding=btn_padding,
                                   command=self.prepare_push)
        self.push_btn.grid(row=0, column=0, padx=20, pady=8)

        self.pop_btn = ttk.Button(button_frame, text="出栈 (Pop)",
                                  style="danger.TButton", padding=btn_padding,
                                  command=self.pop)
        self.pop_btn.grid(row=0, column=1, padx=20, pady=8)

        self.clear_btn = ttk.Button(button_frame, text="清空栈",
                                    style="warning.TButton", padding=btn_padding,
                                    command=self.clear_stack)
        self.clear_btn.grid(row=0, column=2, padx=20, pady=8)

        self.back_btn = ttk.Button(button_frame, text="返回主界面",
                                   style="primary.TButton", padding=btn_padding,
                                   command=self.back_to_main)
        self.back_btn.grid(row=0, column=3, padx=20, pady=8)
        
        # 保存/打开 按钮
        ttk.Button(button_frame, text="保存栈", style="info.TButton", padding=btn_padding,
                   command=self.save_structure).grid(row=0, column=4, padx=20, pady=8)
        ttk.Button(button_frame, text="打开栈", style="info.TButton", padding=btn_padding,
                   command=self.load_structure).grid(row=0, column=5, padx=20, pady=8)

        # --- 美化: 6. 使用 ttk.Label 和 ttk.Entry ---
        batch_label = ttk.Label(button_frame, text="批量构建 (逗号分隔):", font=self.font_normal)
        batch_label.grid(row=1, column=0, padx=(20, 4), pady=10, sticky="e")
        
        batch_entry = ttk.Entry(button_frame, textvariable=self.batch_entry_var, width=40, font=self.font_normal)
        batch_entry.grid(row=1, column=1, columnspan=2, padx=4, pady=10, sticky="w")
        
        self.batch_build_btn = ttk.Button(button_frame, text="开始批量构建",
                                          command=self.start_batch_build)
        self.batch_build_btn.grid(row=1, column=3, padx=10, pady=10)

        # DSL 输入行
        dsl_label = ttk.Label(button_frame, text="DSL 命令:", font=self.font_normal)
        dsl_label.grid(row=2, column=0, padx=(20, 4), pady=10, sticky="e")
        
        dsl_entry = ttk.Entry(button_frame, textvariable=self.dsl_var, width=60, font=self.font_normal)
        dsl_entry.grid(row=2, column=1, columnspan=3, padx=4, pady=10, sticky="w")
        dsl_entry.bind("<Return>", self.process_dsl)
        
        ttk.Button(button_frame, text="执行", command=self.process_dsl).grid(row=2, column=4, padx=10, pady=10)

    def process_dsl(self, event=None):
        text = self.dsl_var.get().strip()
        try:
            process_command(self, text)
        finally:
            self.dsl_var.set("")

    def _ensure_stack_folder(self):
        default_dir = storage.ensure_save_subdir("stack") if hasattr(storage, "ensure_save_subdir") else os.path.join(os.path.dirname(os.path.abspath(__file__)), "save", "stack")
        os.makedirs(default_dir, exist_ok=True)
        return default_dir

    def save_structure(self):
        data = list(self.model.data) if hasattr(self.model, "data") else []
        meta = {"capacity": self.capacity, "top": getattr(self.model, "top", len(data) - 1)}
        default_dir = self._ensure_stack_folder()
        default_name = f"stack_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = filedialog.asksaveasfilename(
            initialdir=default_dir,
            initialfile=default_name,
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="保存栈到文件"
        )
        if not filepath: return 
        payload = {"type": "stack", "data": data, "metadata": meta}
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)
            messagebox.showinfo("成功", f"栈已保存到：\n{filepath}")
        except Exception as e:
            messagebox.showerror("保存失败", f"发生错误：{e}")


    def load_structure(self):
        default_dir = self._ensure_stack_folder()
        filepath = filedialog.askopenfilename(
            initialdir=default_dir,
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="从文件加载栈"
        )
        if not filepath: return 
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                loaded = json.load(f)
            
            if loaded.get("type") != "stack":
                messagebox.showwarning("文件错误", "文件类型不匹配，请选择正确的栈 (stack) JSON 文件。")
                return

            data_list = loaded.get("data", [])
            self.model = StackModel(self.capacity) 
            for item in data_list:
                self.model.push(item) 

            self.update_display()
            messagebox.showinfo("成功", f"已加载 {len(self.model.data)} 个元素到栈")
        except Exception as e:
            messagebox.showerror("加载失败", f"无法读取或解析文件：{e}")


    def prepare_push(self):
        if self.animating:
            return
        is_full = self.model.is_full()
        if is_full:
            messagebox.showwarning("栈满", "栈已满，无法执行入栈操作")
            return
        if self.input_frame:
            try:
                self.input_frame.destroy()
            except Exception:
                pass
            self.input_frame = None

        self.value_entry.set("")

        # --- 美化: 7. 使用 ttk.Frame 并居中 ---
        self.input_frame = ttk.Frame(self.window, padding=10)
        self.input_frame.place(relx=0.5, y=650, anchor='n')

        value_label = ttk.Label(self.input_frame, text="输入要入栈的值:", font=self.font_normal)
        value_label.grid(row=0, column=0, padx=5, pady=5)

        value_entry = ttk.Entry(self.input_frame, textvariable=self.value_entry, font=self.font_normal)
        value_entry.grid(row=0, column=1, padx=5, pady=5)

        self.confirm_btn = ttk.Button(self.input_frame, text="确认",
                                      style="success.TButton",
                                      command=self.on_confirm_push) # 修正：原代码有个笔误 _on_confirm_push
        self.confirm_btn.grid(row=0, column=2, padx=5, pady=5)

        value_entry.focus()

    def on_confirm_push(self): # 修正：原代码有个笔误 _on_confirm_push
        value = self.value_entry.get()
        if not value:
            messagebox.showerror("错误", "请输入一个值")
            return
        if self.input_frame:
            try:
                self.input_frame.destroy()
            except Exception:
                pass
            self.input_frame = None
            self.confirm_btn = None
        self.animate_push_left(value)

    def animate_push_left(self, value, on_finish=None):
        if self.animating:
            return
        self.animating = True
        self._set_buttons_state("disabled")

        start_x = - (self.cell_width + 20)
        start_y = self.start_y
        target_idx = len(self.model.data)
        target_x = self.start_x + target_idx * (self.cell_width + self.spacing)

        rect_id = self.canvas.create_rectangle(
            start_x, start_y, start_x + self.cell_width, start_y + self.cell_height,
            fill="lightgreen", outline=self.stack_outline, width=2
        )
        text_id = self.canvas.create_text(
            start_x + self.cell_width/2, start_y + self.cell_height/2,
            text=str(value), font=self.font_normal_bold
        )

        total_steps = 30
        dx = (target_x - start_x) / total_steps
        step_delay = 12 

        def step(step_i=0):
            if step_i < total_steps:
                self.canvas.move(rect_id, dx, 0)
                self.canvas.move(text_id, dx, 0)
                self.window.after(step_delay, lambda: step(step_i + 1))
            else:
                try:
                    self.canvas.delete(rect_id)
                    self.canvas.delete(text_id)
                except Exception:
                    pass
                pushed = self.model.push(value)
                if not pushed:
                    messagebox.showwarning("栈满", "入栈失败：栈已满")

                self.update_display()
                self.animating = False
                if on_finish:
                    on_finish()
                else:
                    self._set_buttons_state("normal")
        step()

    def pop(self):
        if self.animating:
            return
        empty = self.model.is_empty()
        if empty:
            messagebox.showwarning("栈空", "栈已空，无法执行出栈操作")
            return
        self.animate_pop_right()

    def animate_pop_right(self):
        if self.animating:
            return
        self.animating = True
        self._set_buttons_state("disabled")

        top_idx = getattr(self.model, "top", len(self.model.data) - 1)
        if top_idx < 0 or top_idx >= len(self.stack_rectangles): 
            self.animating = False
            self._set_buttons_state("normal")
            self.update_display() 
            return

        rect_id = self.stack_rectangles[top_idx]
        text_id = self.stack_labels[top_idx]
        self.canvas.itemconfig(rect_id, fill="salmon")
        
        total_steps = 30
        target_x = 1350 + self.cell_width 
        current_x = self.canvas.coords(rect_id)[0]
        dx = (target_x - current_x) / total_steps
        step_delay = 12

        def step(step_i=0):
            if step_i < total_steps:
                self.canvas.move(rect_id, dx, 0)
                self.canvas.move(text_id, dx, 0)
                self.window.after(step_delay, lambda: step(step_i + 1))
            else:
                _ = self.model.pop()
                self.update_display() 
                self.animating = False
                self._set_buttons_state("normal")
        step()

    def clear_stack(self):
        if self.animating:
            return
        empty = self.model.is_empty()
        if empty:
            messagebox.showinfo("信息", "栈已为空")
            return
        self._set_buttons_state("disabled")
        self._clear_step()

    def _clear_step(self):
        if getattr(self.model, "is_empty", lambda: len(self.model.data) == 0)():
            self._set_buttons_state("normal")
            return
        
        if self.animating:
             self.window.after(50, self._clear_step) 
             return

        self.animate_pop_right() 

        def poll():
            if self.animating:
                self.window.after(80, poll) 
            else:
                self.window.after(120, self._clear_step) 
        poll()

    def start_batch_build(self):
        if self.animating:
            return
        text = self.batch_entry_var.get().strip()
        if not text:
            messagebox.showinfo("提示", "请输入要构建的值，例如：1,2,3")
            return
        items = [s.strip() for s in text.split(",") if s.strip() != ""]
        if not items:
            messagebox.showinfo("提示", "未解析到有效值")
            return
        available = self.capacity - len(self.model.data)
        if len(items) > available:
            if not messagebox.askyesno("容量不足", f"当前可用位置 {available}，要入栈 {len(items)} 个。是否只入栈前 {available} 个？"):
                return
            items = items[:available]
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
        value = self.batch_queue[self.batch_index]
        self.batch_index += 1
        self.animate_push_left(value, on_finish=self._batch_step)


    def update_display(self):
        self.canvas.delete("all")
        self.stack_rectangles.clear()
        self.stack_labels.clear()
        
        frame_width = (self.cell_width + self.spacing) * self.capacity + 20
        frame_height = self.cell_height + 20
        
        # --- 美化: 8. 更新画布元素样式 (字体和颜色) ---
        
        self.canvas.create_rectangle(
            self.start_x - 10,
            self.start_y - 10,
            self.start_x + frame_width - 10,
            self.start_y + frame_height - 10,
            outline="#BBBBBB", 
            width=2,
            fill="#EEEEEE"  
        )
        
        self.canvas.create_text(
            self.start_x - 30,
            self.start_y + self.cell_height/2,
            text="栈底",
            font=self.font_normal_bold
        )
        self.canvas.create_text(
            self.start_x + (self.cell_width + self.spacing) * self.capacity + 30,
            self.start_y + self.cell_height/2,
            text="栈顶",
            font=self.font_normal_bold
        )
        
        for i in range(len(self.model.data)):
            x = self.start_x + i * (self.cell_width + self.spacing)

            rect = self.canvas.create_rectangle(
                x, self.start_y,
                x + self.cell_width, self.start_y + self.cell_height,
                fill=self.stack_fill,
                outline=self.stack_outline,
                width=2
            )
            self.stack_rectangles.append(rect)
            
            label = self.canvas.create_text(
                x + self.cell_width/2,
                self.start_y + self.cell_height/2,
                text=str(self.model.data[i]),
                font=self.font_normal_bold
            )
            self.stack_labels.append(label)

        if not getattr(self.model, "is_empty", lambda: len(self.model.data) == 0)():
            top_idx = getattr(self.model, "top", len(self.model.data) - 1)
            top_x = self.start_x + top_idx * (self.cell_width + self.spacing)
            
            self.canvas.create_line(
                top_x + self.cell_width/2,
                self.start_y - 30,
                top_x + self.cell_width/2,
                self.start_y - 5,
                arrow=tk.LAST,
                width=2,
                fill="red" 
            )
            self.canvas.create_text(
                top_x + self.cell_width/2,
                self.start_y - 50,
                text=f"top → {top_idx}",
                font=self.font_normal_bold,
                fill="red"
            )
        else:
            self.canvas.create_text(
                self.start_x + self.cell_width/2, 
                self.start_y - 50,
                text="top → -1 (空栈)",
                font=self.font_normal_bold,
                fill="red"
            )

        info_x = 20
        info_y = 20
        info_width = 360 
        
        self.canvas.create_rectangle(info_x-8, info_y-8, info_x + info_width + 8, info_y + 180, 
                                     fill="#F7F9FF", outline="#DDD", width=1)

        info_text = f"栈状态: {'满' if getattr(self.model, 'is_full', lambda: False)() else '空' if getattr(self.model, 'is_empty', lambda: len(self.model.data) == 0)() else '非空'}， 大小: {len(self.model)}/{self.capacity}"
        
        self.canvas.create_text(info_x, info_y + 6, text=info_text, 
                                font=self.font_normal, anchor="nw", width=info_width, justify=tk.LEFT)
        instruction_text = (
            "操作说明：\n"
            "1. 入栈(Push): 在栈顶添加元素（左侧飞入）\n"
            "2. 出栈(Pop): 移除栈顶元素（右侧飞出）\n"
            "3. 清空栈: 移除所有元素\n"
            "4. 批量构建: 输入 1,2,3 并点击开始批量构建\n"
            "5. DSL: 在下方 DSL 命令框输入：push x / pop / clear / create 1 2 3（或 create 1,2,3）并回车"
        )
        self.canvas.create_text(info_x + 6, info_y + 36, text=instruction_text, 
                                font=self.font_small, anchor="nw", width=info_width, justify=tk.LEFT)

    def _set_buttons_state(self, state):
        all_buttons = [
            self.push_btn, self.pop_btn, self.clear_btn, self.back_btn,
            self.batch_build_btn, self.confirm_btn
        ]
        
        all_entries = [] # 存储所有 Entry

        try:
            button_frame = self.push_btn.master
            for child in button_frame.winfo_children():
                if isinstance(child, ttk.Button):
                    if child not in all_buttons:
                        all_buttons.append(child)
                elif isinstance(child, ttk.Entry):
                     all_entries.append(child) # 收集 Entry

        except Exception:
            pass
        
        for btn in all_buttons:
            if btn:
                try:
                    btn.config(state=state)
                except Exception:
                    pass
        
        # 统一处理 Entry
        for entry in all_entries:
             if entry:
                try:
                    entry.config(state="normal" if state == "normal" else "disabled")
                except Exception:
                    pass

        if self.input_frame:
            try:
                for child in self.input_frame.winfo_children():
                    if isinstance(child, (ttk.Button, ttk.Entry)):
                        child.config(state="normal" if state == "normal" else "disabled")
            except Exception:
                pass


    def back_to_main(self):
        if self.animating:
            messagebox.showinfo("提示", "正在动画构建，无法返回")
            return
        stack_api.unregister(self)
        self.window.destroy()

if __name__ == '__main__':
    window = tk.Tk()
    window.title("栈 (Stack) 可视化")
    window.geometry("1350x770")
    window.maxsize(1350, 770)
    window.minsize(1350, 770)
    
    window.configure(bg="#F0F0F0") 

    app = StackVisualizer(window)
    window.mainloop()