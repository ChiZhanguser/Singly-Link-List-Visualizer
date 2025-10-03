# stack_visual.py
# 完整版：栈可视化（含 DSL 插件点与回退兼容）
from tkinter import *
from tkinter import messagebox, filedialog
import json
import os
from datetime import datetime

# ---- 对 StackModel 做兼容性导入 ----
StackModel = None
try:
    from stack.stack_model import StackModel  # 项目内可能的包结构
except Exception:
    try:
        from stack_model import StackModel  # 如果直接放在工程根目录
    except Exception:
        StackModel = None

# ---- storage 兼容导入（用于保存/加载默认目录） ----
try:
    import storage
except Exception:
    # 提供一个最小兼容接口
    class _FakeStorage:
        @staticmethod
        def ensure_save_subdir(name: str):
            base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "save")
            p = os.path.join(base, name)
            os.makedirs(p, exist_ok=True)
            return p
    storage = _FakeStorage()

# ---- stack_api 可选兼容（供外部 programmatic 注册） ----
try:
    import stack.stack_api as stack_api
except Exception:
    stack_api = None

# ---- DSL_utils 插件点导入（优先使用外部包） ----
process_command = None
try:
    # 期望 DSL_utils/__init__.py 提供 process_command(visualizer, text)
    from DSL_utils import process_command as _pc
    process_command = _pc
except Exception:
    process_command = None

# 如果没有外部 DSL_utils，则使用内置回退的解析器（功能等同于之前版本）
def _fallback_process_command(visualizer, text):
    """
    回退实现：支持 push x | pop | clear | create 1 2 3 或 create 1,2,3
    优先调用 visualizer 已有的动画方法（animate_push_left, pop, clear_stack, _batch_step）
    """
    if getattr(visualizer, "animating", False):
        messagebox.showinfo("提示", "当前正在执行动画，请稍后再试")
        return

    text = (text or "").strip()
    if not text:
        return

    parts = text.split()
    cmd = parts[0].lower()
    args = parts[1:]

    if cmd == "push":
        if not args:
            messagebox.showerror("错误", "push 需要一个参数，例如：push 5")
            return
        value = " ".join(args)
        # 检查栈满
        try:
            if hasattr(visualizer.model, "is_full") and visualizer.model.is_full():
                messagebox.showwarning("栈满", "栈已满，无法入栈")
                return
        except Exception:
            pass

        if hasattr(visualizer, "animate_push_left"):
            visualizer.animate_push_left(value)
        else:
            try:
                visualizer.model.push(value)
                visualizer.update_display()
            except Exception as e:
                messagebox.showerror("错误", f"入栈失败：{e}")
        return

    if cmd == "pop":
        if hasattr(visualizer, "pop"):
            visualizer.pop()
            return
        try:
            visualizer.model.pop()
            visualizer.update_display()
        except Exception:
            messagebox.showwarning("栈空/错误", "出栈失败或栈为空")
        return

    if cmd == "clear":
        if hasattr(visualizer, "clear_stack"):
            visualizer.clear_stack()
            return
        try:
            if hasattr(visualizer.model, "clear"):
                visualizer.model.clear()
            else:
                visualizer.model.data = []
                visualizer.model.top = -1
            visualizer.update_display()
        except Exception as e:
            messagebox.showerror("错误", f"清空失败：{e}")
        return

    if cmd == "create":
        if not args:
            messagebox.showerror("错误", "create 需要至少一个值，例如：create 1 2 3")
            return
        items = []
        for a in args:
            for part in a.split(","):
                s = part.strip()
                if s != "":
                    items.append(s)
        if not items:
            messagebox.showerror("错误", "未解析到有效值")
            return

        # 优先使用 visualizer.create_from_list
        if hasattr(visualizer, "create_from_list"):
            try:
                visualizer.create_from_list(items)
            except Exception as e:
                messagebox.showerror("错误", f"调用 create_from_list 失败：{e}")
            return

        cap = getattr(visualizer, "capacity", None)
        if cap is not None and len(items) > cap:
            ans = messagebox.askyesno("容量不足",
                                      f"要创建的元素数量 {len(items)} 超过当前 capacity={cap}。\n选择【是】扩容并完整加载；选择【否】则只加载前 {cap} 个元素。")
            if ans:
                # 尝试扩容并重建 model
                try:
                    if StackModel is not None:
                        visualizer.capacity = len(items)
                        visualizer.model = StackModel(visualizer.capacity)
                    else:
                        visualizer.capacity = len(items)
                        try:
                            visualizer.model = type(visualizer.model)(visualizer.capacity)
                        except Exception:
                            pass
                except Exception:
                    visualizer.capacity = len(items)
            else:
                items = items[:cap]

        # 清空并批量入栈（使用 batch 动画，如果存在）
        try:
            if hasattr(visualizer.model, "clear"):
                visualizer.model.clear()
            else:
                visualizer.model.data = []
                visualizer.model.top = -1
        except Exception:
            pass

        try:
            visualizer.update_display()
            visualizer.batch_queue = items
            visualizer.batch_index = 0
            if hasattr(visualizer, "_set_buttons_state"):
                visualizer._set_buttons_state("disabled")
            if hasattr(visualizer, "_batch_step"):
                visualizer._batch_step()
            else:
                for v in items:
                    try:
                        visualizer.model.push(v)
                    except Exception:
                        break
                visualizer.update_display()
                if hasattr(visualizer, "_set_buttons_state"):
                    visualizer._set_buttons_state("normal")
        except Exception as e:
            messagebox.showerror("错误", f"创建失败：{e}")
        return

    messagebox.showinfo("未识别命令", "支持命令：push x, pop, clear, create 1 2 3（或 create 1,2,3）")
    return

if process_command is None:
    process_command = _fallback_process_command

# ---------------- StackVisualizer 类 ----------------
class StackVisualizer:
    def __init__(self, root):
        self.window = root
        self.window.config(bg="#E6F3FF")
        self.canvas = Canvas(self.window, bg="white", width=1350, height=500, relief=RAISED, bd=8)
        self.canvas.pack()

        # 默认 capacity 与模型（若未能导入 StackModel，会在运行时尝试基础替代）
        self.capacity = 10
        if StackModel is not None:
            try:
                self.model = StackModel(self.capacity)
            except Exception:
                # 如果 StackModel 构造异常，尝试一个最小模型
                self.model = self._make_minimal_model()
        else:
            self.model = self._make_minimal_model()

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
        self.value_entry = StringVar()
        self.batch_entry_var = StringVar()
        self.dsl_var = StringVar()
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

        # 尝试注册到 stack_api（如果有）
        try:
            if stack_api is not None and hasattr(stack_api, "register"):
                stack_api.register(self)
        except Exception:
            pass

    # 最小模型（fallback）实现，兼容 push/pop/clear/top/is_full/is_empty/len/data
    def _make_minimal_model(self):
        class MinimalStack:
            def __init__(self, capacity=10):
                self.data = []
                self.top = -1
                self.capacity = capacity
            def push(self, v):
                if len(self.data) >= self.capacity:
                    return False
                self.data.append(v)
                self.top = len(self.data) - 1
                return True
            def pop(self):
                if not self.data:
                    raise IndexError("pop from empty")
                v = self.data.pop()
                self.top = len(self.data) - 1
                return v
            def is_full(self):
                return len(self.data) >= self.capacity
            def is_empty(self):
                return len(self.data) == 0
            def clear(self):
                self.data = []
                self.top = -1
            def __len__(self):
                return len(self.data)
        return MinimalStack(self.capacity)

    def create_heading(self):
        heading = Label(self.window, text="栈(顺序栈)的可视化",
                       font=("Arial", 30, "bold"), bg="#E6F3FF", fg="darkblue")
        heading.place(x=450, y=20)

        info = Label(self.window, text="栈是一种后进先出(LIFO)的数据结构，只能在栈顶进行插入和删除操作",
                     font=("Arial", 16), bg="#E6F3FF", fg="black")
        info.place(x=300, y=80)

    def create_buttons(self):
        button_frame = Frame(self.window, bg="#E6F3FF")
        button_frame.place(x=50, y=540, width=1250, height=160)

        self.push_btn = Button(button_frame, text="入栈(Push)", font=("Arial", 14),
                               width=15, height=2, bg="green", fg="white",
                               command=self.prepare_push)
        self.push_btn.grid(row=0, column=0, padx=20, pady=8)

        self.pop_btn = Button(button_frame, text="出栈(Pop)", font=("Arial", 14),
                              width=15, height=2, bg="red", fg="white",
                              command=self.pop)
        self.pop_btn.grid(row=0, column=1, padx=20, pady=8)

        self.clear_btn = Button(button_frame, text="清空栈", font=("Arial", 14),
                                width=15, height=2, bg="orange", fg="white",
                                command=self.clear_stack)
        self.clear_btn.grid(row=0, column=2, padx=20, pady=8)

        self.back_btn = Button(button_frame, text="返回主界面", font=("Arial", 14),
                               width=15, height=2, bg="blue", fg="white",
                               command=self.back_to_main)
        self.back_btn.grid(row=0, column=3, padx=20, pady=8)

        batch_label = Label(button_frame, text="批量构建 (逗号分隔):", font=("Arial", 12), bg="#E6F3FF")
        batch_label.grid(row=1, column=0, padx=(20, 4), pady=6, sticky="w")
        batch_entry = Entry(button_frame, textvariable=self.batch_entry_var, width=40, font=("Arial", 12))
        batch_entry.grid(row=1, column=1, columnspan=2, padx=4, pady=6, sticky="w")
        self.batch_build_btn = Button(button_frame, text="开始批量构建", font=("Arial", 12),
                                      command=self.start_batch_build)
        self.batch_build_btn.grid(row=1, column=3, padx=10, pady=6)

        # DSL 输入行（第三行）
        dsl_label = Label(button_frame, text="DSL 命令:", font=("Arial", 12), bg="#E6F3FF")
        dsl_label.grid(row=2, column=0, padx=(20, 4), pady=6, sticky="w")
        dsl_entry = Entry(button_frame, textvariable=self.dsl_var, width=60, font=("Arial", 12))
        dsl_entry.grid(row=2, column=1, columnspan=3, padx=4, pady=6, sticky="w")
        dsl_entry.bind("<Return>", self.process_dsl)   # 回车执行
        Button(button_frame, text="执行", font=("Arial", 12), command=self.process_dsl).grid(row=2, column=4, padx=10, pady=6)

        Button(button_frame, text="保存栈", font=("Arial", 14), width=15, height=2, bg="#6C9EFF", fg="white",
               command=self.save_structure).grid(row=0, column=4, padx=20, pady=8)
        Button(button_frame, text="打开栈", font=("Arial", 14), width=15, height=2, bg="#6C9EFF", fg="white",
               command=self.load_structure).grid(row=0, column=5, padx=20, pady=8)

    # ----------------- DSL 调用桥接 -----------------
    def process_dsl(self, event=None):
        text = self.dsl_var.get().strip()
        if not text:
            return
        try:
            process_command(self, text)
        finally:
            # 清空输入框（保留 UX）
            self.dsl_var.set("")
    # ----------------- end DSL -----------------

    def _ensure_stack_folder(self):
        try:
            default_dir = storage.ensure_save_subdir("stack") if hasattr(storage, "ensure_save_subdir") else os.path.join(os.path.dirname(os.path.abspath(__file__)), "save", "stack")
            os.makedirs(default_dir, exist_ok=True)
            return default_dir
        except Exception:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            default_dir = os.path.join(base_dir, "save", "stack")
            os.makedirs(default_dir, exist_ok=True)
            return default_dir

    def save_structure(self):
        try:
            data = list(self.model.data) if hasattr(self.model, "data") else []
            meta = {"capacity": self.capacity, "top": getattr(self.model, "top", len(data) - 1)}

            if len(data) == 0:
                if not messagebox.askyesno("确认", "当前栈为空，是否仍然保存一个空栈文件？"):
                    return

            default_dir = self._ensure_stack_folder()
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
        try:
            default_dir = self._ensure_stack_folder()

            filepath = filedialog.askopenfilename(
                initialdir=default_dir,
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="从文件加载栈"
            )
            if not filepath:
                return

            with open(filepath, "r", encoding="utf-8") as f:
                loaded = json.load(f)

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

            if len(data_list) > self.capacity:
                ans = messagebox.askyesno(
                    "容量不足",
                    f"要加载的文件包含 {len(data_list)} 个元素，当前 capacity = {self.capacity}。\n"
                    "选择【是】以扩容并完整加载；选择【否】则只加载前 capacity 个元素。"
                )
                if ans:
                    try:
                        if StackModel is not None:
                            self.capacity = len(data_list)
                            self.model = StackModel(self.capacity)
                        else:
                            self.capacity = len(data_list)
                            try:
                                self.model = type(self.model)(self.capacity)
                            except Exception:
                                pass
                    except Exception:
                        self.capacity = len(data_list)
                else:
                    data_list = data_list[:self.capacity]

            try:
                # 尝试直接设定 model 的 data
                self.model.data = list(data_list)
                self.model.top = len(self.model.data) - 1
            except Exception:
                # 回退：重新 push 元素
                self.model = StackModel(self.capacity) if StackModel is not None else self._make_minimal_model()
                for v in data_list:
                    try:
                        self.model.push(v)
                    except Exception:
                        break

            self.update_display()
            messagebox.showinfo("成功", f"已加载 {len(self.model.data)} 个元素到栈")

        except Exception as e:
            print("load_structure error:", e)
            messagebox.showerror("错误", f"加载失败：{e}")

    def prepare_push(self):
        if self.animating:
            return
        try:
            is_full = self.model.is_full()
        except Exception:
            is_full = len(self.model.data) >= self.capacity
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

        self.input_frame = Frame(self.window, bg="#E6F3FF")
        self.input_frame.place(x=500, y=620, width=400, height=80)

        value_label = Label(self.input_frame, text="输入要入栈的值:", font=("Arial", 12), bg="#E6F3FF")
        value_label.grid(row=0, column=0, padx=5, pady=5)

        value_entry = Entry(self.input_frame, textvariable=self.value_entry, font=("Arial", 12))
        value_entry.grid(row=0, column=1, padx=5, pady=5)

        self.confirm_btn = Button(self.input_frame, text="确认", font=("Arial", 12),
                                  command=self._on_confirm_push)
        self.confirm_btn.grid(row=0, column=2, padx=5, pady=5)

        value_entry.focus()

    def _on_confirm_push(self):
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
                try:
                    self.canvas.delete(rect_id)
                    self.canvas.delete(text_id)
                except Exception:
                    pass
                try:
                    pushed = self.model.push(value)
                    if not pushed:
                        messagebox.showwarning("栈满", "入栈失败：栈已满")
                except Exception:
                    # 若 model.push 抛出异常，尝试直接修改 data
                    try:
                        self.model.data.append(value)
                        self.model.top = len(self.model.data) - 1
                    except Exception:
                        pass

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
        try:
            empty = self.model.is_empty()
        except Exception:
            empty = len(self.model.data) == 0
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
        if top_idx < 0:
            self.animating = False
            self._set_buttons_state("normal")
            return

        try:
            rect_id = self.stack_rectangles[top_idx]
            text_id = self.stack_labels[top_idx]
        except Exception:
            try:
                _ = self.model.pop()
            except Exception:
                pass
            self.update_display()
            self.animating = False
            self._set_buttons_state("normal")
            return

        self.canvas.itemconfig(rect_id, fill="salmon")

        total_steps = 30
        dx = (1350 + self.cell_width) / total_steps
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
                try:
                    _ = self.model.pop()
                except Exception:
                    pass
                self.update_display()
                self.animating = False
                self._set_buttons_state("normal")

        step()

    def clear_stack(self):
        if self.animating:
            return
        try:
            empty = self.model.is_empty()
        except Exception:
            empty = len(self.model.data) == 0
        if empty:
            messagebox.showinfo("信息", "栈已为空")
            return
        self._set_buttons_state("disabled")
        self._clear_step()

    def _clear_step(self):
        if getattr(self.model, "is_empty", lambda: len(self.model.data) == 0)():
            self._set_buttons_state("normal")
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
        self.canvas.create_rectangle(
            self.start_x - 10,
            self.start_y - 10,
            self.start_x + frame_width - 10,
            self.start_y + frame_height - 10,
            outline="gray",
            width=2,
            fill="lightgray"
        )

        self.canvas.create_text(
            self.start_x - 30,
            self.start_y + self.cell_height/2,
            text="栈底",
            font=("Arial", 12, "bold")
        )

        self.canvas.create_text(
            self.start_x + (self.cell_width + self.spacing) * self.capacity + 30,
            self.start_y + self.cell_height/2,
            text="栈顶",
            font=("Arial", 12, "bold")
        )

        for i in range(len(self.model.data)):
            x = self.start_x + i * (self.cell_width + self.spacing)

            rect = self.canvas.create_rectangle(
                x, self.start_y,
                x + self.cell_width, self.start_y + self.cell_height,
                fill="lightblue",
                outline="black",
                width=2
            )
            self.stack_rectangles.append(rect)

            label = self.canvas.create_text(
                x + self.cell_width/2,
                self.start_y + self.cell_height/2,
                text=str(self.model.data[i]),
                font=("Arial", 14, "bold")
            )
            self.stack_labels.append(label)

        if not getattr(self.model, "is_empty", lambda: len(self.model.data) == 0)():
            top_x = self.start_x + getattr(self.model, "top", len(self.model.data) - 1) * (self.cell_width + self.spacing)
            self.canvas.create_line(
                top_x + self.cell_width/2,
                self.start_y - 30,
                top_x + self.cell_width/2,
                self.start_y - 5,
                arrow=LAST,
                width=2
            )
            self.canvas.create_text(
                top_x + self.cell_width/2,
                self.start_y - 50,
                text=f"top → {getattr(self.model, 'top', len(self.model.data) - 1)}",
                font=("Arial", 12, "bold"),
                fill="red"
            )
        else:
            self.canvas.create_text(
                self.start_x + self.cell_width/2,
                self.start_y - 50,
                text="top → -1 (空栈)",
                font=("Arial", 12, "bold"),
                fill="red"
            )

        # ================== 修复：信息/说明区（背景+自动换行） ==================
        # 我把说明和状态放到画布左上角的一个固定宽度区域，使用 anchor='nw' 和 width 自动换行
        info_x = 20
        info_y = 20
        info_width = 360  # 控制说明区域宽度，超过则自动换行
        # 背景框（可选）让说明更清晰，不与栈图重叠
        self.canvas.create_rectangle(info_x-8, info_y-8, info_x + info_width + 8, info_y + 180, fill="#F7F9FF", outline="#DDD")

        info_text = f"栈状态: {'满' if getattr(self.model, 'is_full', lambda: False)() else '空' if getattr(self.model, 'is_empty', lambda: len(self.model.data) == 0)() else '非空'}， 大小: {len(self.model)}/{self.capacity}"
        # 使用 anchor='nw'（左上角锚点）和 width 使文本自动换行，justify=LEFT 左对齐
        self.canvas.create_text(info_x, info_y + 6, text=info_text, font=("Arial", 12), anchor="nw", width=info_width, justify=LEFT)

        instruction_text = (
            "操作说明：\n"
            "1. 入栈(Push): 在栈顶添加元素（左侧飞入）\n"
            "2. 出栈(Pop): 移除栈顶元素（右侧飞出）\n"
            "3. 清空栈: 移除所有元素\n"
            "4. 批量构建: 输入 1,2,3 并点击开始批量构建\n"
            "5. DSL: 在下方 DSL 命令框输入：push x / pop / clear / create 1 2 3（或 create 1,2,3）并回车"
        )
        self.canvas.create_text(info_x + 6, info_y + 36, text=instruction_text, font=("Arial", 11), anchor="nw", width=info_width, justify=LEFT)
        # ================== 结束修复 ==================


    def _set_buttons_state(self, state):
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
        try:
            if stack_api is not None and hasattr(stack_api, "unregister"):
                stack_api.unregister(self)
        except Exception:
            pass
        try:
            self.window.destroy()
        except Exception:
            pass

if __name__ == '__main__':
    window = Tk()
    window.title("栈可视化")
    window.geometry("1350x770")
    window.maxsize(1350, 770)
    window.minsize(1350, 770)
    StackVisualizer(window)
    window.mainloop()
