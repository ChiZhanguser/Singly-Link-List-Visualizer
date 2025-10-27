# -*- coding: utf-8 -*-
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
        self.window.config(bg="#E8F4F9")
        self.canvas = Canvas(self.window, bg="#FFFFFF", width=1350, height=500,
                             relief=RIDGE, bd=3)
        self.canvas.pack(pady=10)

        self.capacity = capacity
        self.model = HashTableModel(self.capacity)

        # 可视元素引用
        self.cell_rects = []
        self.cell_texts = []
        self.index_texts = []

        # 布局参数
        self.start_x = 60
        self.start_y = 250   # 下移避免重叠
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

    # ------------------------------------------------------------------ #
    #                         UI 组件
    # ------------------------------------------------------------------ #
    def create_heading(self):
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

        btn_style = {
            'font': ("Microsoft YaHei UI", 11, "bold"),
            'width': 12,
            'height': 1,
            'relief': 'groove',
            'bd': 2,
            'cursor': 'hand2'
        }

        # 第一行按钮
        Button(button_frame, text="插入 Insert", bg="#3498DB", fg="white",
               activebackground="#2980B9", activeforeground="white",
               command=self.prepare_insert, **btn_style).grid(row=0, column=0, padx=8, pady=6)
        Button(button_frame, text="查找 Find", bg="#2ECC71", fg="white",
               activebackground="#27AE60", activeforeground="white",
               command=self.prepare_find, **btn_style).grid(row=0, column=1, padx=8, pady=6)
        Button(button_frame, text="删除 Delete", bg="#E74C3C", fg="white",
               activebackground="#C0392B", activeforeground="white",
               command=self.prepare_delete, **btn_style).grid(row=0, column=2, padx=8, pady=6)
        Button(button_frame, text="清空 Clear", bg="#95A5A6", fg="white",
               activebackground="#7F8C8D", activeforeground="white",
               command=self.clear_table, **btn_style).grid(row=0, column=3, padx=8, pady=6)
        Button(button_frame, text="返回主界面", bg="#9B59B6", fg="white",
               activebackground="#8E44AD", activeforeground="white",
               command=self.back_to_main, **btn_style).grid(row=0, column=4, padx=8, pady=6)
        Button(button_frame, text="调整容量", bg="#F39C12", fg="white",
               activebackground="#E67E22", activeforeground="white",
               command=self.prepare_resize, **btn_style).grid(row=0, column=5, padx=8, pady=6)

        # 命令输入区
        cmd_frame = Frame(button_frame, bg="white", relief="groove", bd=2)
        cmd_frame.grid(row=1, column=0, columnspan=6, sticky="ew", padx=8, pady=10)

        Label(cmd_frame, text="命令:", font=("Microsoft YaHei UI", 11), bg="white", fg="#2C3E50") \
            .pack(side=LEFT, padx=(15, 5), pady=8)

        dsl_entry = Entry(cmd_frame, textvariable=self.dsl_var, width=50,
                          font=("Microsoft YaHei UI", 11), relief="flat",
                          bg="white", highlightthickness=1, highlightcolor="#3498DB")
        dsl_entry.pack(side=LEFT, padx=5, pady=8, fill=X, expand=True)
        dsl_entry.bind("<Return>", lambda e: self.process_dsl())
        self.dsl_var.set("create 23 17 35 8 42 29 56 67")
        dsl_entry.select_range(0, END)

        cmd_hint = Label(cmd_frame,
                         text="试试运行示例，或输入: insert x | find x | delete x | clear",
                         font=("Microsoft YaHei UI", 9), bg="white", fg="#2980B9")
        cmd_hint.pack(side=LEFT, padx=(10, 5), pady=8)

        Button(cmd_frame, text="执行",
               font=("Microsoft YaHei UI", 11, "bold"), width=6, height=1,
               bg="#3498DB", fg="white", activebackground="#2980B9",
               activeforeground="white", relief="groove", bd=1,
               cursor="hand2", command=self.process_dsl) \
            .pack(side=LEFT, padx=(10, 15), pady=8)

        # 文件操作按钮
        file_frame = Frame(button_frame, bg="#E8F4F9")
        file_frame.grid(row=1, column=6, rowspan=2, padx=6, pady=4)

        Button(file_frame, text="保存数据",
               font=("Microsoft YaHei UI", 11, "bold"), width=10, height=1,
               bg="#3498DB", fg="white", activebackground="#2980B9",
               activeforeground="white", relief="groove", bd=1,
               cursor="hand2", command=self.save_structure).pack(pady=2)

        Button(file_frame, text="打开数据", font=("Microsoft YaHei UI", 11, "bold"),
               width=10, height=1, bg="#2ECC71", fg="white",
               activebackground="#27AE60", activeforeground="white",
               relief="groove", bd=1, cursor="hand2",
               command=self.load_structure).pack(pady=2)

        for child in button_frame.winfo_children():
            child.grid_configure(sticky="nsew")

    # ------------------------------------------------------------------ #
    #                         容量调整
    # ------------------------------------------------------------------ #
    def prepare_resize(self):
        if self.animating: return
        self._open_resize_input()

    def _open_resize_input(self):
        if self.resize_frame: self.resize_frame.destroy()
        self.resize_frame = Frame(self.window, bg="#E8F4F9")
        self.resize_frame.place(x=500, y=680, width=300, height=80)

        bg = Frame(self.resize_frame, bg="white", relief="groove", bd=2)
        bg.place(relx=0.02, rely=0.1, relwidth=0.96, relheight=0.8)

        Label(bg, text="新容量:", font=("Microsoft YaHei UI", 11), bg="white", fg="#2C3E50") \
            .pack(side=LEFT, padx=(15, 5), pady=4)
        Label(bg, text=f"(当前: {self.capacity})", font=("Microsoft YaHei UI", 9), bg="white", fg="#7F8C8D") \
            .pack(side=LEFT, padx=5, pady=4)

        entry = Entry(bg, textvariable=self.capacity_var, width=8,
                      font=("Microsoft YaHei UI", 11), relief="flat", bg="white",
                      highlightthickness=1, highlightcolor="#F39C12")
        entry.pack(side=LEFT, padx=5, pady=4)

        Button(bg, text="确认调整", font=("Microsoft YaHei UI", 10, "bold"), width=8, height=1,
               bg="#F39C12", fg="white", activebackground="#E67E22",
               activeforeground="white", relief="groove", bd=1,
               cursor="hand2", command=self._on_confirm_resize) \
            .pack(side=LEFT, padx=(10, 5), pady=4)

        Button(bg, text="取消", font=("Microsoft YaHei UI", 10, "bold"), width=6, height=1,
               bg="#95A5A6", fg="white", activebackground="#7F8C8D",
               activeforeground="white", relief="groove", bd=1,
               cursor="hand2", command=self._close_resize_input) \
            .pack(side=LEFT, padx=5, pady=4)

        self.window.after(50, lambda: entry.focus_set())
        entry.select_range(0, END)

    def _on_confirm_resize(self):
        try:
            new_cap = int(self.capacity_var.get())
            if new_cap <= 0:
                messagebox.showerror("错误", "容量必须是正整数")
                return
            if new_cap == self.capacity:
                messagebox.showinfo("提示", "新容量与当前容量相同")
                self._close_resize_input()
                return
            if new_cap < len(self.model):
                messagebox.showerror("错误",
                                     f"新容量({new_cap})不能小于当前元素数量({len(self.model)})")
                return
            self._resize_table(new_cap)
            self._close_resize_input()
        except ValueError:
            messagebox.showerror("错误", "请输入有效的整数容量")
        except Exception as e:
            messagebox.showerror("错误", f"调整容量失败: {str(e)}")

    def _resize_table(self, new_capacity: int):
        if self.animating: return
        self.animating = True
        self._set_buttons_state("disabled")

        valid_elements = [v for v in self.model.table if v is not None and v is not self.model.tombstone]
        old_cap = self.capacity
        self.model = HashTableModel(new_capacity)
        self.capacity = new_capacity
        self._show_resize_animation(old_cap, new_capacity, valid_elements)

    def _show_resize_animation(self, old_cap, new_cap, elements):
        self.canvas.delete("all")
        self.canvas.create_text(675, 250,
                                text=f"容量调整: {old_cap} → {new_cap}",
                                font=("Microsoft YaHei UI", 16, "bold"), fill="#2C3E50")
        old_start_x = 675 - (old_cap * (self.cell_width + self.spacing)) // 2
        for i in range(old_cap):
            x = old_start_x + i * (self.cell_width + self.spacing)
            self.canvas.create_rectangle(x, 300, x + self.cell_width, 300 + self.cell_height,
                                         fill="#FFEAA7", outline="#FDCB6E", width=2)
            self.canvas.create_text(x + self.cell_width / 2, 300 + self.cell_height / 2,
                                    text=str(i), font=("Arial", 10))
        self.window.after(1000, lambda: self._show_new_table_animation(new_cap, elements))

    def _show_new_table_animation(self, new_cap, elements):
        self.canvas.delete("all")
        total_w = (self.cell_width + self.spacing) * new_cap
        start_x = 675 - total_w // 2
        cell_rects = []
        for i in range(new_cap):
            x = start_x + i * (self.cell_width + self.spacing)
            r = self.canvas.create_rectangle(x, 300, x + self.cell_width, 300 + self.cell_height,
                                             fill="white", outline="#3498DB", width=2)
            cell_rects.append(r)
            self.canvas.create_text(x + self.cell_width / 2, 280,
                                    text=str(i), font=("Arial", 10, "bold"))
        self.canvas.create_text(675, 250,
                                text=f"新容量: {new_cap}",
                                font=("Microsoft YaHei UI", 16, "bold"), fill="#2C3E50")
        self._animate_elements_insertion(elements, start_x, cell_rects, new_cap)

    def _animate_elements_insertion(self, elements, start_x, cell_rects, new_cap):
        if not elements:
            self.window.after(500, self._finish_resize)
            return
        elem = elements[0]
        remain = elements[1:]
        new_idx = self.model._hash(elem)
        ex, ey = 675, 150
        rect = self.canvas.create_rectangle(ex - 30, ey - 20, ex + 30, ey + 20,
                                            fill="#ABEBC6", outline="#27AE60", width=2)
        txt = self.canvas.create_text(ex, ey, text=str(elem), font=("Arial", 12, "bold"))
        target_x = start_x + new_idx * (self.cell_width + self.spacing) + self.cell_width / 2
        target_y = 300 + self.cell_height / 2
        self._animate_element_move(rect, txt, ex, ey, target_x, target_y,
                                   remain, start_x, cell_rects, new_cap, elem, new_idx)

    def _animate_element_move(self, rect, txt, sx, sy, tx, ty,
                              remain, start_x, cell_rects, new_cap, elem, idx):
        steps = 20
        dx = (tx - sx) / steps
        dy = (ty - sy) / steps
        def step(i=0):
            if i < steps:
                self.canvas.move(rect, dx, dy)
                self.canvas.move(txt, dx, dy)
                self.window.after(30, lambda: step(i + 1))
            else:
                self.canvas.delete(rect)
                self.canvas.delete(txt)
                self.model.insert(elem)
                self.canvas.itemconfig(cell_rects[idx], fill="#ABEBC6")
                self.canvas.create_text(tx, ty, text=str(elem), font=("Arial", 12, "bold"))
                self.window.after(300, lambda: self._animate_elements_insertion(
                    remain, start_x, cell_rects, new_cap))
        step()

    def _finish_resize(self):
        self.animating = False
        self._set_buttons_state("normal")
        self.update_display()
        messagebox.showinfo("成功", f"容量已调整为 {self.capacity}")

    def _close_resize_input(self):
        if self.resize_frame:
            self.resize_frame.destroy()
            self.resize_frame = None

    # ------------------------------------------------------------------ #
    #                         DSL / 操作
    # ------------------------------------------------------------------ #
    def process_dsl(self):
        text = self.dsl_var.get().strip()
        try:
            if text.startswith("create"):
                items = text.split()[1:]
                if not items:
                    messagebox.showerror("错误", "create 后请提供数值")
                    return
                try:
                    values = [int(x) for x in items]
                except ValueError:
                    messagebox.showerror("错误", "create 后请提供整数")
                    return
                if len(values) > self.capacity:
                    if not messagebox.askyesno("容量不足",
                                               f"要插入 {len(values)} 个元素，容量={self.capacity}。是否只插入前 {self.capacity} 个？"):
                        return
                    values = values[:self.capacity]
                self.batch_queue = values
                self.batch_index = 0
                self._set_buttons_state("disabled")
                self._batch_step()
            elif text.startswith("insert"):
                parts = text.split()
                if len(parts) != 2:
                    messagebox.showerror("错误", "insert x")
                    return
                self.insert_value(int(parts[1]))
            elif text.startswith(("find", "search")):
                parts = text.split()
                if len(parts) != 2:
                    messagebox.showerror("错误", "find x")
                    return
                self.find_value(int(parts[1]))
            elif text.startswith("delete"):
                parts = text.split()
                if len(parts) != 2:
                    messagebox.showerror("错误", "delete x")
                    return
                self.delete_value(int(parts[1]))
            elif text == "clear":
                self.clear_table()
            else:
                messagebox.showerror("错误", "未知命令")
        finally:
            self.dsl_var.set("")

    # ------------------------------------------------------------------ #
    #                         文件 IO
    # ------------------------------------------------------------------ #
    def _ensure_folder(self):
        base = os.path.dirname(os.path.abspath(__file__))
        p = os.path.join(base, "save", "hashtable")
        os.makedirs(p, exist_ok=True)
        return p

    def save_structure(self):
        payload = {"type": "hashtable", "capacity": self.capacity, "data": self.model.table}
        default_dir = self._ensure_folder()
        default_name = f"hashtable_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = filedialog.asksaveasfilename(initialdir=default_dir,
                                                initialfile=default_name,
                                                defaultextension=".json",
                                                filetypes=[("JSON", "*.json")])
        if not filepath: return
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        messagebox.showinfo("保存成功", f"已保存到 {filepath}")

    def load_structure(self):
        default_dir = self._ensure_folder()
        filepath = filedialog.askopenfilename(initialdir=default_dir,
                                              filetypes=[("JSON", "*.json")])
        if not filepath: return
        with open(filepath, "r", encoding="utf-8") as f:
            loaded = json.load(f)
        data = loaded["data"]
        if len(data) != self.capacity:
            if messagebox.askyesno("容量不符",
                                   f"文件容量 {len(data)} 与当前 {self.capacity} 不符，是否以文件容量重建？"):
                self.capacity = len(data)
                self.model = HashTableModel(self.capacity)
            else:
                data = (data + [None] * self.capacity)[:self.capacity]
        conv = [self.model.tombstone if v == "__TOMBSTONE__" else v for v in data]
        self.model.table = conv
        self.update_display()
        messagebox.showinfo("加载成功", "已加载散列表")

    # ------------------------------------------------------------------ #
    #                         输入框
    # ------------------------------------------------------------------ #
    def prepare_insert(self, default_value: str = ""):
        if self.animating: return
        self._open_input("插入的值", default_value, "insert")

    def prepare_find(self, default_value: str = ""):
        if self.animating: return
        self._open_input("查找的值", default_value, "find")

    def prepare_delete(self, default_value: str = ""):
        if self.animating: return
        self._open_input("删除的值", default_value, "delete")

    def _open_input(self, label_text, default_value, action):
        if self.input_frame: self.input_frame.destroy()
        self.value_entry.set(default_value)

        self.input_frame = Frame(self.window, bg="#E8F4F9")
        self.input_frame.place(x=420, y=680, width=360, height=50)

        bg = Frame(self.input_frame, bg="white", relief="groove", bd=2)
        bg.place(relx=0.02, rely=0.1, relwidth=0.96, relheight=0.8)

        Label(bg, text=label_text + ":", font=("Microsoft YaHei UI", 11), bg="white", fg="#2C3E50") \
            .pack(side=LEFT, padx=(15, 5), pady=4)

        entry = Entry(bg, textvariable=self.value_entry, width=12,
                      font=("Microsoft YaHei UI", 11), relief="flat", bg="white",
                      highlightthickness=1, highlightcolor="#3498DB")
        entry.pack(side=LEFT, padx=5, pady=4)

        Button(bg, text="确认", font=("Microsoft YaHei UI", 11, "bold"), width=6, height=1,
               bg="#3498DB", fg="white", activebackground="#2980B9",
               activeforeground="white", relief="groove", bd=1,
               cursor="hand2", command=lambda: self._on_confirm(action)) \
            .pack(side=LEFT, padx=(10, 5), pady=4)

        self.window.after(50, lambda: self.input_frame.focus_force())

    def _on_confirm(self, action):
        val = self.value_entry.get().strip()
        if not val:
            messagebox.showerror("错误", "请输入一个值")
            return
        if self.input_frame:
            self.input_frame.destroy()
            self.input_frame = None
        {"insert": self.insert_value,
         "find": self.find_value,
         "delete": self.delete_value}[action](int(val) if val.isdigit() else val)

    # ------------------------------------------------------------------ #
    #                         动画核心
    # ------------------------------------------------------------------ #
    def animate_insert(self, value, target_idx, probe_path):
        if self.animating: return
        self.animating = True
        self._set_buttons_state("disabled")

        start_x = -(self.cell_width + 40)
        start_y = self.start_y
        rect = self.canvas.create_rectangle(start_x, start_y,
                                            start_x + self.cell_width,
                                            start_y + self.cell_height,
                                            fill="lightgreen", outline="black", width=2)
        txt = self.canvas.create_text(start_x + self.cell_width / 2,
                                      start_y + self.cell_height / 2,
                                      text=str(value), font=("Arial", 14, "bold"))

        total_steps = 30
        target_x = self.start_x + (self.cell_width + self.spacing) * target_idx
        dx = (target_x - start_x) / total_steps

        def probe_step(i=0):
            if i < len(probe_path):
                idx = probe_path[i]
                self.canvas.itemconfig(self.cell_rects[idx], outline="red", width=3)
                self.window.after(220, lambda: unprobe(i))
            else:
                move_step(0)

        def unprobe(i):
            idx = probe_path[i]
            self.canvas.itemconfig(self.cell_rects[idx], outline="black", width=2)
            self.window.after(60, lambda: probe_step(i + 1))

        def move_step(step=0):
            if step < total_steps:
                self.canvas.move(rect, dx, 0)
                self.canvas.move(txt, dx, 0)
                self.window.after(12, lambda: move_step(step + 1))
            else:
                self.canvas.delete(rect)
                self.canvas.delete(txt)
                try:
                    self.model.insert(value)
                except Exception:
                    pass
                self.update_display()
                self.animating = False
                self._set_buttons_state("normal")

        probe_step()

    def insert_value(self, value):
        if self.animating: return
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
            if val is self.model.tombstone and first_tomb == -1:
                first_tomb = i
            if val == value:
                self._probe_highlight(probe, found=True, found_idx=i,
                                      msg=f"值已存在于索引 {i}")
                return
            i = (i + 1) % self.capacity
            if i == start:
                target = first_tomb if first_tomb != -1 else None
                break
        if target is None:
            self._probe_highlight(probe, found=False,
                                  msg="散列表已满，无法插入")
            return
        self.animate_insert(value, target, probe)

    def _probe_highlight(self, probe_path, found=False, found_idx=None, msg=None):
        if self.animating: return
        self.animating = True
        self._set_buttons_state("disabled")

        def step(i=0):
            if i < len(probe_path):
                idx = probe_path[i]
                self.canvas.itemconfig(self.cell_rects[idx], outline="red", width=3)
                self.window.after(220, lambda: unstep(i))
            else:
                if found and found_idx is not None:
                    self.canvas.itemconfig(self.cell_rects[found_idx],
                                           outline="lime", width=4)
                    self.window.after(600, finish)
                else:
                    self.window.after(200, finish)

        def unstep(i):
            idx = probe_path[i]
            self.canvas.itemconfig(self.cell_rects[idx], outline="black", width=2)
            self.window.after(60, lambda: step(i + 1))

        def finish():
            if msg:
                messagebox.showinfo("提示", msg)
            self.animating = False
            self._set_buttons_state("normal")
            self.update_display()

        step()

    def find_value(self, value):
        if self.animating: return
        start = self.model._hash(value)
        i = start
        probe = []
        while True:
            probe.append(i)
            val = self.model.table[i]
            if val is None:
                self._probe_highlight(probe, found=False,
                                      msg=f"未找到 {value}")
                return
            if val is not self.model.tombstone and val == value:
                self._probe_highlight(probe, found=True, found_idx=i,
                                      msg=f"找到 {value}，索引 {i}")
                return
            i = (i + 1) % self.capacity
            if i == start:
                self._probe_highlight(probe, found=False,
                                      msg=f"未找到 {value}（全表）")
                return

    def delete_value(self, value):
        if self.animating: return
        start = self.model._hash(value)
        i = start
        probe = []
        while True:
            probe.append(i)
            val = self.model.table[i]
            if val is None:
                self._probe_highlight(probe, found=False,
                                      msg=f"未找到 {value}，无法删除")
                return
            if val is not self.model.tombstone and val == value:
                def after():
                    idx = self.model.delete(value)
                    if idx is not None:
                        messagebox.showinfo("删除", f"已在索引 {idx} 用墓碑删除 {value}")
                    self.update_display()
                self._probe_highlight_with_callback(probe, True, i, after)
                return
            i = (i + 1) % self.capacity
            if i == start:
                self._probe_highlight(probe, found=False,
                                      msg=f"未找到 {value}（全表）")
                return

    def _probe_highlight_with_callback(self, probe_path, found, found_idx, callback):
        if self.animating: return
        self.animating = True
        self._set_buttons_state("disabled")

        def step(i=0):
            if i < len(probe_path):
                idx = probe_path[i]
                self.canvas.itemconfig(self.cell_rects[idx], outline="red", width=3)
                self.window.after(220, lambda: un(i))
            else:
                if found:
                    self.canvas.itemconfig(self.cell_rects[found_idx],
                                           outline="orange", width=4)
                    self.window.after(360, finish)
                else:
                    self.window.after(200, finish)

        def un(i):
            idx = probe_path[i]
            self.canvas.itemconfig(self.cell_rects[idx], outline="black", width=2)
            self.window.after(60, lambda: step(i + 1))

        def finish():
            callback()
            self.animating = False
            self._set_buttons_state("normal")
            self.update_display()

        step()

    def clear_table(self):
        if self.animating: return
        if all(v is None for v in self.model.table):
            messagebox.showinfo("清空", "散列表已为空")
            return
        self.animating = True
        self._set_buttons_state("disabled")
        idxs = list(range(self.capacity - 1, -1, -1))

        def step(i=0):
            if i >= len(idxs):
                self.animating = False
                self._set_buttons_state("normal")
                self.update_display()
                return
            idx = idxs[i]
            self.canvas.itemconfig(self.cell_rects[idx], fill="#ffdddd")
            self.window.after(80, lambda: self.canvas.itemconfig(self.cell_rects[idx], fill="white"))
            self.model.table[idx] = None
            self.update_display()
            self.window.after(100, lambda: step(i + 1))

        step()

    # ------------------------------------------------------------------ #
    #                         批量 & 其它
    # ------------------------------------------------------------------ #
    def start_batch_build(self):
        if self.animating: return
        text = self.batch_entry_var.get().strip()
        if not text:
            messagebox.showinfo("提示", "请输入批量值，逗号分隔")
            return
        items = [s.strip() for s in text.replace("，", ",").split(",") if s.strip()]
        if len(items) > self.capacity:
            if not messagebox.askyesno("容量不足",
                                       f"要插入 {len(items)} 个，容量={self.capacity}。是否只插入前 {self.capacity} 个？"):
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

        def cont():
            if self.animating:
                self.window.after(120, cont)
            else:
                self._batch_step()

        self.insert_value(val)
        self.window.after(150, cont)

    # ------------------------------------------------------------------ #
    #                         显示更新（关键：2×2 布局）
    # ------------------------------------------------------------------ #
    def update_display(self):
        self.canvas.delete("all")
        self.cell_rects.clear()
        self.cell_texts.clear()
        self.index_texts.clear()

        total_width = (self.cell_width + self.spacing) * self.capacity

        # 背景渐变框
        for i in range(2):
            self.canvas.create_rectangle(
                self.start_x - 8 + i * 2, self.start_y - 8 + i * 2,
                self.start_x + total_width + 8 - i * 2,
                self.start_y + self.cell_height + 8 - i * 2,
                outline="#D0E3FF", fill=["#F5F9FF", "#EDF7FF"][i], width=1)

        # ---------- 信息面板：2×2 布局 ----------
        card_x, card_y = 20, 10
        card_w, card_h = 380, 150  # 高度略增
        self._draw_rounded_rect(card_x - 8, card_y - 8,
                                card_x + card_w + 8, card_y + card_h + 8,
                                radius=12, fill="#F7FFF7", outline="#DDD", tags="card_shadow")
        self._draw_rounded_rect(card_x, card_y,
                                card_x + card_w, card_y + card_h,
                                radius=12, fill="#FFFFFF", outline="#E0E0E0", tags="card_body")

        # 标题 + 图标
        self.canvas.create_text(card_x + 20, card_y + 22,
                                text="信息面板",
                                anchor="w", font=("Microsoft YaHei UI", 14, "bold"),
                                fill="#2C3E50")
        self.canvas.create_text(card_x + card_w - 20, card_y + 22,
                                text="i", anchor="e",
                                font=("Segoe UI Emoji", 16), fill="#3498DB")

        # 统计信息
        stats = f"容量: {self.capacity}   有效元素数: {len(self.model)}"
        self.canvas.create_text(card_x + 20, card_y + 50,
                                text=stats, anchor="w",
                                font=("Microsoft YaHei UI", 12), fill="#34495E")

        # 操作说明：2×2 网格
        ops = [
            ("插入", "insert x", "#3498DB"),
            ("查找", "find x", "#2ECC71"),
            ("删除", "delete x", "#E74C3C"),
            ("清空", "clear", "#95A5A6")
        ]
        base_y = card_y + 78
        row_height = 26
        col1_x = card_x + 35
        col2_x = card_x + 200

        for i in range(4):
            row = i // 2
            col = i % 2
            title, cmd, color = ops[i]
            y = base_y + row * row_height
            x_title = col1_x if col == 0 else col2_x
            x_cmd = x_title + 70

            self.canvas.create_text(x_title, y,
                                    text=title, anchor="w",
                                    font=("Microsoft YaHei UI", 11, "bold"),
                                    fill=color)
            self.canvas.create_text(x_cmd, y,
                                    text=cmd, anchor="w",
                                    font=("Microsoft YaHei UI", 10),
                                    fill="#7F8C8D")

        # ---------- 绘制哈希表格子 ----------
        for i in range(self.capacity):
            x = self.start_x + i * (self.cell_width + self.spacing)
            rect = self.canvas.create_rectangle(x, self.start_y,
                                                x + self.cell_width,
                                                self.start_y + self.cell_height,
                                                fill="white", outline="black", width=2)
            self.cell_rects.append(rect)

            idx_txt = self.canvas.create_text(x + self.cell_width / 2,
                                              self.start_y - 16,
                                              text=str(i),
                                              font=("Arial", 10, "bold"))
            self.index_texts.append(idx_txt)

            val = self.model.table[i]
            if val is None:
                txt = ""
            elif val is self.model.tombstone:
                txt = "墓碑"
                self.canvas.itemconfig(rect, fill="#eeeeee")
            else:
                txt = str(val)
            cell_txt = self.canvas.create_text(x + self.cell_width / 2,
                                               self.start_y + self.cell_height / 2,
                                               text=txt, font=("Arial", 12))
            self.cell_texts.append(cell_txt)

        # 右侧标题
        self.canvas.create_text(self.start_x + total_width + 40,
                                self.start_y + self.cell_height / 2,
                                text="散列表格", font=("Arial", 12, "bold"))

    # ---------- 辅助：绘制圆角矩形 ----------
    def _draw_rounded_rect(self, x0, y0, x1, y1, radius=10, **kwargs):
        points = [
            x0 + radius, y0,
            x1 - radius, y0,
            x1, y0,
            x1, y0 + radius,
            x1, y1 - radius,
            x1, y1,
            x1 - radius, y1,
            x0 + radius, y1,
            x0, y1,
            x0, y1 - radius,
            x0, y0 + radius,
            x0, y0
        ]
        return self.canvas.create_polygon(points, **kwargs, smooth=True)

    # ------------------------------------------------------------------ #
    def _set_buttons_state(self, state):
        for w in self.window.winfo_children():
            if isinstance(w, Frame):
                for c in w.winfo_children():
                    try:
                        c.config(state=state)
                    except Exception:
                        pass

    def back_to_main(self):
        if self.animating:
            messagebox.showinfo("提示", "动画进行中，无法返回")
            return
        self.window.destroy()


if __name__ == "__main__":
    root = Tk()
    root.title("散列表可视化")
    root.geometry("1350x770")
    root.minsize(1350, 770)
    HashtableVisualizer(root, capacity=13)
    root.mainloop()