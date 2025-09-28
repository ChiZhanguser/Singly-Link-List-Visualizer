# stack_visual.py
from tkinter import *
from tkinter import messagebox
from stack.stack_model import StackModel
import json
import os
from datetime import datetime
import storage as storage
from tkinter import filedialog


class StackVisualizer:
    def __init__(self, root):
        self.window = root
        self.window.config(bg="#E6F3FF")
        self.canvas = Canvas(self.window, bg="white", width=1350, height=500, relief=RAISED, bd=8)
        self.canvas.pack()
        
        # 栈模型和容量
        self.capacity = 10
        self.model = StackModel(self.capacity)
        
        # 存储画布上的元素 id
        self.stack_rectangles = []  # 栈单元格（canvas id 列表）
        self.stack_labels = []      # 栈值标签（canvas id 列表）
        
        # 坐标和尺寸参数 - 横向布局
        self.start_x = 200  # 起始X坐标（栈第0个元素位置）
        self.start_y = 300  # 起始Y坐标
        self.cell_width = 80  # 单元格宽度
        self.cell_height = 60  # 单元格高度
        self.spacing = 10  # 单元格间距
        
        # 输入变量
        self.value_entry = StringVar()
        self.batch_entry_var = StringVar()
        self.input_frame = None  # 存放临时输入框（prepare_push 创建）
        
        # 按钮引用（用于禁用/启用）
        self.push_btn = None
        self.pop_btn = None
        self.clear_btn = None
        self.back_btn = None
        self.confirm_btn = None
        self.batch_build_btn = None
        
        # 批量队列
        self.batch_queue = []
        self.batch_index = 0
        
        # 动画标志
        self.animating = False
        
        # 初始化界面
        self.create_heading()
        self.create_buttons()
        self.update_display()
    
    def create_heading(self):
        heading = Label(self.window, text="栈(顺序栈)的可视化", 
                       font=("Arial", 30, "bold"), bg="#E6F3FF", fg="darkblue")
        heading.place(x=450, y=20)
        
        info = Label(self.window, text="栈是一种后进先出(LIFO)的数据结构，只能在栈顶进行插入和删除操作", 
                    font=("Arial", 16), bg="#E6F3FF", fg="black")
        info.place(x=300, y=80)
    
    def create_buttons(self):
        # 操作按钮框架
        button_frame = Frame(self.window, bg="#E6F3FF")
        button_frame.place(x=50, y=540, width=1250, height=120)
        
        # 入栈按钮
        self.push_btn = Button(button_frame, text="入栈(Push)", font=("Arial", 14), 
                            width=15, height=2, bg="green", fg="white",
                            command=self.prepare_push)
        self.push_btn.grid(row=0, column=0, padx=20, pady=8)
        
        # 出栈按钮
        self.pop_btn = Button(button_frame, text="出栈(Pop)", font=("Arial", 14), 
                           width=15, height=2, bg="red", fg="white",
                           command=self.pop)
        self.pop_btn.grid(row=0, column=1, padx=20, pady=8)
        
        # 清空栈按钮
        self.clear_btn = Button(button_frame, text="清空栈", font=("Arial", 14), 
                             width=15, height=2, bg="orange", fg="white",
                             command=self.clear_stack)
        self.clear_btn.grid(row=0, column=2, padx=20, pady=8)
        
        # 返回主界面按钮
        self.back_btn = Button(button_frame, text="返回主界面", font=("Arial", 14), 
                            width=15, height=2, bg="blue", fg="white",
                            command=self.back_to_main)
        self.back_btn.grid(row=0, column=3, padx=20, pady=8)
        
        # 批量构建输入（第二行）
        batch_label = Label(button_frame, text="批量构建 (逗号分隔):", font=("Arial", 12), bg="#E6F3FF")
        batch_label.grid(row=1, column=0, padx=(20,4), pady=6, sticky="w")
        batch_entry = Entry(button_frame, textvariable=self.batch_entry_var, width=40, font=("Arial", 12))
        batch_entry.grid(row=1, column=1, columnspan=2, padx=4, pady=6, sticky="w")
        self.batch_build_btn = Button(button_frame, text="开始批量构建", font=("Arial", 12),
                                      command=self.start_batch_build)
        self.batch_build_btn.grid(row=1, column=3, padx=10, pady=6)
        
        Button(button_frame, text="保存栈", font=("Arial", 14), width=15, height=2, bg="#6C9EFF", fg="white",
               command=self.save_structure).grid(row=0, column=4, padx=20, pady=8)
        Button(button_frame, text="打开栈", font=("Arial", 14), width=15, height=2, bg="#6C9EFF", fg="white",
               command=self.load_structure).grid(row=0, column=5, padx=20, pady=8)
    
        # ---------- 保存/打开 helpers for StackVisualizer ----------
    def _ensure_stack_folder(self):
        try:
            base_dir = os.path.dirname(os.path.abspath(storage.__file__))
            default_dir = os.path.join(base_dir, "save", "stack")
            os.makedirs(default_dir, exist_ok=True)
            return default_dir
        except Exception:
            # 兜底：当前脚本目录下的 save/stack
            base_dir = os.path.dirname(os.path.abspath(__file__))
            default_dir = os.path.join(base_dir, "..", "save", "stack")
            default_dir = os.path.normpath(default_dir)
            os.makedirs(default_dir, exist_ok=True)
            return default_dir
    def save_structure(self):
        """
        直接在 StackVisualizer 里弹出保存文件对话框，初始目录固定为 save/stack（storage.ensure_save_subdir）。
        这样可以保证默认目录不是 save/linked_list。
        """
        try:
            data = list(self.model.data) if hasattr(self.model, "data") else []
            meta = {"capacity": self.capacity, "top": getattr(self.model, "top", len(data) - 1)}

            if len(data) == 0:
                if not messagebox.askyesno("确认", "当前栈为空，是否仍然保存一个空栈文件？"):
                    return

            default_dir = storage.ensure_save_subdir("stack") if hasattr(storage, "ensure_save_subdir") else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "save", "stack")
            os.makedirs(default_dir, exist_ok=True)
            default_name = f"stack_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            filepath = filedialog.asksaveasfilename(
                initialdir=default_dir,
                initialfile=default_name,
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="保存栈到文件"
            )
            if not filepath:
                return

            payload = {"type": "stack", "data": data, "metadata": meta}
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)

            messagebox.showinfo("成功", f"栈已保存到：\n{filepath}")
        except Exception as e:
            print("save_structure error:", e)
            messagebox.showerror("错误", f"保存失败：{e}")


    def load_structure(self):
        """
        直接在 StackVisualizer 里弹出打开对话框，初始目录固定为 save/stack（storage.ensure_save_subdir）。
        读取后快速恢复（无动画）。
        """
        try:
            default_dir = storage.ensure_save_subdir("stack") if hasattr(storage, "ensure_save_subdir") else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "save", "stack")
            os.makedirs(default_dir, exist_ok=True)

            filepath = filedialog.askopenfilename(
                initialdir=default_dir,
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="从文件加载栈"
            )
            if not filepath:
                return

            with open(filepath, "r", encoding="utf-8") as f:
                loaded = json.load(f)

            # 支持两种格式：{type:stack, data:[...]} 或直接 list
            if isinstance(loaded, dict) and "data" in loaded:
                data_list = loaded.get("data", [])
            elif isinstance(loaded, list):
                data_list = loaded
            else:
                messagebox.showerror("错误", "文件格式不被识别（需为 list 或包含 data 字段的 dict）")
                return

            if not isinstance(data_list, list):
                messagebox.showerror("错误", "读取的数据不是列表")
                return

            # 容量检查：扩容或截断
            if len(data_list) > self.capacity:
                ans = messagebox.askyesno(
                    "容量不足",
                    f"要加载的文件包含 {len(data_list)} 个元素，当前 capacity = {self.capacity}。\n"
                    "选择【是】以扩容并完整加载；选择【否】则只加载前 capacity 个元素。"
                )
                if ans:
                    self.capacity = len(data_list)
                    self.model = StackModel(self.capacity)
                else:
                    data_list = data_list[:self.capacity]

            # 直接赋值或兜底 push
            try:
                self.model.data = list(data_list)
                self.model.top = len(self.model.data) - 1
            except Exception:
                self.model = StackModel(self.capacity)
                for v in data_list:
                    if not self.model.push(v):
                        break

            self.update_display()
            messagebox.showinfo("成功", f"已加载 {len(self.model.data)} 个元素到栈")

        except Exception as e:
            print("load_structure error:", e)
            messagebox.showerror("错误", f"加载失败：{e}")


    
    def prepare_push(self):
        if self.animating:
            return
        if self.model.is_full():
            messagebox.showwarning("栈满", "栈已满，无法执行入栈操作")
            return
            
        # 如果之前的输入框还在，先销毁
        if self.input_frame:
            try:
                self.input_frame.destroy()
            except Exception:
                pass
            self.input_frame = None
        
        self.value_entry.set("")
        
        self.input_frame = Frame(self.window, bg="#E6F3FF")
        # 保持你之前的大致位置（y值）
        self.input_frame.place(x=500, y=620, width=400, height=80)
        
        value_label = Label(self.input_frame, text="输入要入栈的值:", font=("Arial", 12), bg="#E6F3FF")
        value_label.grid(row=0, column=0, padx=5, pady=5)
        
        value_entry = Entry(self.input_frame, textvariable=self.value_entry, font=("Arial", 12))
        value_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # 确认按钮引用保存，以便禁用
        self.confirm_btn = Button(self.input_frame, text="确认", font=("Arial", 12), 
                           command=self._on_confirm_push)
        self.confirm_btn.grid(row=0, column=2, padx=5, pady=5)
        
        value_entry.focus()
    
    def _on_confirm_push(self):
        # 触发动画入栈（从左侧飞入）
        value = self.value_entry.get()
        if not value:
            messagebox.showerror("错误", "请输入一个值")
            return
        # 销毁临时输入区域
        if self.input_frame:
            try:
                self.input_frame.destroy()
            except Exception:
                pass
            self.input_frame = None
            self.confirm_btn = None
        # 开始动画（动画结束后会把值 push 到 model 并刷新显示）
        # 不传回调，单次入栈会在完成后恢复按钮状态
        self.animate_push_left(value)
    
    def animate_push_left(self, value, on_finish=None):
        """
        从左侧飞入并在到达后将值写入 model。
        支持可选回调 on_finish（用于批量时链式调用）。
        """
        if self.animating:
            return
        self.animating = True
        self._set_buttons_state(DISABLED)
        
        # 起始位置在左侧画布外
        start_x = - (self.cell_width + 20)
        start_y = self.start_y
        # 目标位置是当前将要插入的位置（index = len(model.data)）
        target_idx = len(self.model.data)  # 在 push 之前的新索引
        target_x = self.start_x + target_idx * (self.cell_width + self.spacing)
        
        rect_id = self.canvas.create_rectangle(
            start_x, start_y, start_x + self.cell_width, start_y + self.cell_height,
            fill="lightgreen", outline="black", width=2
        )
        text_id = self.canvas.create_text(
            start_x + self.cell_width/2, start_y + self.cell_height/2,
            text=str(value), font=("Arial", 14, "bold")
        )
        
        total_steps = 30
        dx = (target_x - start_x) / total_steps
        step_delay = 12  # ms per step
        
        def step(step_i=0):
            if step_i < total_steps:
                self.canvas.move(rect_id, dx, 0)
                self.canvas.move(text_id, dx, 0)
                self.window.after(step_delay, lambda: step(step_i + 1))
            else:
                # 动画到达，删除临时图元，真正 push 到 model 并刷新
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
                # 如果有回调（批量），调用回调；否则恢复按钮状态
                if on_finish:
                    on_finish()
                else:
                    self._set_buttons_state(NORMAL)
        
        step()
    
    def pop(self):
        if self.animating:
            return
        if self.model.is_empty():
            messagebox.showwarning("栈空", "栈已空，无法执行出栈操作")
            return
        # 动画出栈（向右飞出）
        self.animate_pop_right()
    
    def animate_pop_right(self):
        if self.animating:
            return
        self.animating = True
        self._set_buttons_state(DISABLED)
        
        top_idx = self.model.top
        if top_idx < 0:
            self.animating = False
            self._set_buttons_state(NORMAL)
            return
        
        # 获取当前绘制的 top 元素 canvas id（update_display 保证列表同步）
        try:
            rect_id = self.stack_rectangles[top_idx]
            text_id = self.stack_labels[top_idx]
        except Exception:
            # 若找不到则直接 pop 并重画
            popped = self.model.pop()
            self.update_display()
            self.animating = False
            self._set_buttons_state(NORMAL)
            return
        
        # 高亮（变色）
        self.canvas.itemconfig(rect_id, fill="salmon")
        
        total_steps = 30
        dx =  (1350 + self.cell_width) / total_steps  # 向右移出画布
        step_delay = 12  # ms
        
        def step(step_i=0):
            if step_i < total_steps:
                try:
                    self.canvas.move(rect_id, dx, 0)
                    self.canvas.move(text_id, dx, 0)
                except Exception:
                    pass
                self.window.after(step_delay, lambda: step(step_i + 1))
            else:
                # 动画完成，执行模型 pop 并重画
                try:
                    popped = self.model.pop()
                except Exception:
                    popped = None
                # 这里不再弹出 messagebox.showinfo，按你的要求直接刷新显示
                self.update_display()
                self.animating = False
                self._set_buttons_state(NORMAL)
        
        step()
    
    def clear_stack(self):
        if self.animating:
            return
        if self.model.is_empty():
            messagebox.showinfo("信息", "栈已为空")
            return
        # 连续出栈（递归 after）
        self._set_buttons_state(DISABLED)
        self._clear_step()
    
    def _clear_step(self):
        if self.model.is_empty():
            self._set_buttons_state(NORMAL)
            return
        # 触发一次出栈动画，动画完成后回调继续
        # 使用 animate_pop_right 并轮询其完成，然后继续
        self.animate_pop_right()
        def poll():
            if self.animating:
                self.window.after(80, poll)
            else:
                # 短延迟后继续清空
                self.window.after(120, self._clear_step)
        poll()
    
    def start_batch_build(self):
        """
        解析批量输入 (例如: 1,2,3)，按顺序从左依次飞入并入栈。
        """
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
        # 准备批量队列并开始
        self.batch_queue = items
        self.batch_index = 0
        # 禁用按钮直到批量完成
        self._set_buttons_state(DISABLED)
        self._batch_step()
    
    def _batch_step(self):
        if self.batch_index >= len(self.batch_queue):
            # 完成
            self.batch_queue = []
            self.batch_index = 0
            self._set_buttons_state(NORMAL)
            return
        value = self.batch_queue[self.batch_index]
        self.batch_index += 1
        # 调用 animate_push_left 并在结束时继续下一项
        self.animate_push_left(value, on_finish=self._batch_step)
    
    def update_display(self):
        # 清除画布上的所有元素
        self.canvas.delete("all")
        self.stack_rectangles.clear()
        self.stack_labels.clear()
        
        # 绘制栈框架
        frame_width = (self.cell_width + self.spacing) * self.capacity + 20
        frame_height = self.cell_height + 20
        self.canvas.create_rectangle(
            self.start_x - 10, 
            self.start_y - 10,
            self.start_x + frame_width - 10,
            self.start_y + frame_height - 10,
            outline="gray", 
            width=2,
            fill="lightgray"
        )
        
        # 绘制栈底指示
        self.canvas.create_text(
            self.start_x - 30, 
            self.start_y + self.cell_height/2,
            text="栈底", 
            font=("Arial", 12, "bold")
        )
        
        # 绘制栈顶指示（位置说明）
        self.canvas.create_text(
            self.start_x + (self.cell_width + self.spacing) * self.capacity + 30, 
            self.start_y + self.cell_height/2,
            text="栈顶", 
            font=("Arial", 12, "bold")
        )
        
        # 绘制栈元素（从0开始水平排列）
        for i in range(len(self.model.data)):
            x = self.start_x + i * (self.cell_width + self.spacing)
            
            # 绘制栈单元格
            rect = self.canvas.create_rectangle(
                x, self.start_y, 
                x + self.cell_width, self.start_y + self.cell_height, 
                fill="lightblue", 
                outline="black", 
                width=2
            )
            self.stack_rectangles.append(rect)
            
            # 绘制栈值
            label = self.canvas.create_text(
                x + self.cell_width/2, 
                self.start_y + self.cell_height/2, 
                text=str(self.model.data[i]), 
                font=("Arial", 14, "bold")
            )
            self.stack_labels.append(label)
        
        # 绘制栈顶指针
        if not self.model.is_empty():
            top_x = self.start_x + self.model.top * (self.cell_width + self.spacing)
            # 绘制指针箭头
            self.canvas.create_line(
                top_x + self.cell_width/2,
                self.start_y - 30,
                top_x + self.cell_width/2,
                self.start_y - 5,
                arrow=LAST,
                width=2
            )
            # 绘制指针标签
            self.canvas.create_text(
                top_x + self.cell_width/2,
                self.start_y - 50,
                text=f"top → {self.model.top}",
                font=("Arial", 12, "bold"),
                fill="red"
            )
        else:
            # 空栈时的指针显示
            self.canvas.create_text(
                self.start_x + self.cell_width/2,
                self.start_y - 50,
                text="top → -1 (空栈)",
                font=("Arial", 12, "bold"),
                fill="red"
            )
        
        # 绘制栈信息
        info_text = f"栈状态: {'满' if self.model.is_full() else '空' if self.model.is_empty() else '非空'}, 大小: {len(self.model)}/{self.capacity}"
        self.canvas.create_text(100, 100, text=info_text, font=("Arial", 14), anchor="w")
        
        # 绘制操作说明
        instruction_text = "操作说明:\n1. 入栈(Push): 在栈顶添加元素（左侧飞入）\n2. 出栈(Pop): 移除栈顶元素（右侧飞出）\n3. 清空栈: 移除所有元素\n4. 批量构建: 输入 1,2,3 并点击开始批量构建"
        self.canvas.create_text(100, 150, text=instruction_text, font=("Arial", 12), anchor="w")
    
    def _set_buttons_state(self, state):
        # state: NORMAL / DISABLED
        try:
            if self.push_btn:
                self.push_btn.config(state=state)
            if self.pop_btn:
                self.pop_btn.config(state=state)
            if self.clear_btn:
                self.clear_btn.config(state=state)
            if self.back_btn:
                self.back_btn.config(state=state)
            if self.confirm_btn:
                self.confirm_btn.config(state=state)
            if self.batch_build_btn:
                self.batch_build_btn.config(state=state)
            # 如果有临时输入框，禁用输入框
            if self.input_frame:
                for child in self.input_frame.winfo_children():
                    try:
                        child.config(state=state)
                    except Exception:
                        pass
        except Exception:
            pass
    
    def back_to_main(self):
        if self.animating:
            messagebox.showinfo("提示", "正在动画构建，无法返回")
            return
        self.window.destroy()

if __name__ == '__main__':
    window = Tk()
    window.title("栈可视化")
    window.geometry("1350x730")
    window.maxsize(1350, 730)
    window.minsize(1350, 730)
    StackVisualizer(window)
    window.mainloop()
