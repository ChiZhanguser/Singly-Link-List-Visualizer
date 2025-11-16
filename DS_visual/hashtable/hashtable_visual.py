# -*- coding: utf-8 -*-
from tkinter import *
from tkinter import messagebox, filedialog, ttk
import json
import os
from datetime import datetime
from hashtable.hashtable_model import HashTableModel, TOMBSTONE, CollisionMethod

class HashtableVisualizer:
    def __init__(self, root, capacity: int = 11, method: CollisionMethod = CollisionMethod.OPEN_ADDRESSING):
        self.window = root
        self.window.config(bg="#E8F4F9")
        self.canvas = Canvas(self.window, bg="#FFFFFF", width=1350, height=500,
                             relief=RIDGE, bd=3)
        self.canvas.pack(pady=10)

        self.capacity = capacity
        self.method = method
        self.model = HashTableModel(self.capacity, self.method)

        # 可视元素引用
        self.cell_rects = []
        self.cell_texts = []
        self.index_texts = []
        self.chain_elements = []  # 拉链法专用

        # 布局参数
        self.start_x = 60
        self.start_y = 250
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

        # 动画临时数据
        self._anim_highlights = []
        self._anim_temp = None

        self.create_heading()
        self.create_buttons()
        self.update_display()

    # ------------------------------------------------------------------ #
    #                         UI 组件
    # ------------------------------------------------------------------ #
    def create_heading(self):
        title_frame = Frame(self.window, bg="#E8F4F9")
        title_frame.pack(fill=X, padx=20, pady=(15, 5))

        method_name = "开放寻址法" if self.method == CollisionMethod.OPEN_ADDRESSING else "拉链法"
        heading = Label(title_frame, text=f"散列表（{method_name}）可视化",
                        font=("Microsoft YaHei UI", 28, "bold"),
                        bg="#E8F4F9", fg="#2C3E50")
        heading.pack()

        if self.method == CollisionMethod.OPEN_ADDRESSING:
            info_text = "散列方式：h(x)=x%capacity；冲突处理：线性探测（向后逐位查找），删除使用墓碑（tombstone）"
        else:
            info_text = "散列方式：h(x)=x%capacity；冲突处理：拉链法（链表存储冲突元素）"
        
        info = Label(title_frame, text=info_text,
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
        Button(button_frame, text="切换模式", bg="#9B59B6", fg="white",
               activebackground="#8E44AD", activeforeground="white",
               command=self.switch_method, **btn_style).grid(row=0, column=4, padx=8, pady=6)
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

    # ------------------------------------------------------------------ #
    #                         模式切换
    # ------------------------------------------------------------------ #
    def switch_method(self):
        if self.animating:
            messagebox.showinfo("提示", "动画进行中，无法切换")
            return
        
        # 保存当前数据
        if self.method == CollisionMethod.OPEN_ADDRESSING:
            old_data = [v for v in self.model.table if v is not None and v is not self.model.tombstone]
            new_method = CollisionMethod.CHAINING
        else:
            old_data = [item for chain in self.model.table for item in chain]
            new_method = CollisionMethod.OPEN_ADDRESSING
        
        # 切换模式
        self.method = new_method
        self.model = HashTableModel(self.capacity, self.method)
        
        # 重新插入数据
        for item in old_data:
            self.model.insert(item)
        
        # 更新界面
        self.create_heading()
        self.update_display()
        
        method_name = "拉链法" if new_method == CollisionMethod.CHAINING else "开放寻址法"
        messagebox.showinfo("切换成功", f"已切换到{method_name}")

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
            if self.method == CollisionMethod.OPEN_ADDRESSING and new_cap < len(self.model):
                messagebox.showerror("错误",
                                     f"新容量({new_cap})不能小于当前元素数量({len(self.model)})")
                return
            self.model.resize(new_cap)
            self.capacity = new_cap
            self.update_display()
            self._close_resize_input()
            messagebox.showinfo("成功", f"容量已调整为 {self.capacity}")
        except ValueError:
            messagebox.showerror("错误", "请输入有效的整数容量")
        except Exception as e:
            messagebox.showerror("错误", f"调整容量失败: {str(e)}")

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
    def save_structure(self):
        payload = {
            "type": "hashtable",
            "capacity": self.capacity,
            "method": self.method.value,
            "data": self.model.table
        }
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON", "*.json")]
        )
        if not filepath: return
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        messagebox.showinfo("保存成功", f"已保存到 {filepath}")

    def load_structure(self):
        filepath = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if not filepath: return
        with open(filepath, "r", encoding="utf-8") as f:
            loaded = json.load(f)
        
        method_str = loaded.get("method", "open_addressing")
        new_method = CollisionMethod.CHAINING if method_str == "chaining" else CollisionMethod.OPEN_ADDRESSING
        
        if new_method != self.method:
            self.method = new_method
            self.create_heading()
        
        self.capacity = loaded["capacity"]
        self.model = HashTableModel(self.capacity, self.method)
        self.model.table = loaded["data"]
        
        # 重新计算size
        if self.method == CollisionMethod.OPEN_ADDRESSING:
            self.model.size = sum(1 for v in self.model.table if v is not None and v is not TOMBSTONE)
        else:
            self.model.size = sum(len(chain) for chain in self.model.table)
        
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
    #                         操作实现
    # ------------------------------------------------------------------ #
    def insert_value(self, value):
        """对开放寻址法增加动画演示：探测路径高亮 + 值移动动画"""
        if self.animating: return

        if self.method != CollisionMethod.OPEN_ADDRESSING:
            # 对于拉链法直接插入并更新显示
            target_idx, probe_path, is_full, chain_pos = self.model.insert(value)
            if target_idx is None and self.method == CollisionMethod.OPEN_ADDRESSING:
                messagebox.showinfo("提示", "值已存在")
            self.update_display()
            # 如果批量处理中，继续下一步
            if self.batch_queue and self.batch_index < len(self.batch_queue):
                self.window.after(150, self._batch_step)
            return

        # Snapshot table before insertion so we can animate on previous state
        # 对于拉链法，table 项是 list，需要深拷贝链表
        def snapshot_table(tbl):
            if self.method == CollisionMethod.OPEN_ADDRESSING:
                return list(tbl)
            else:
                return [list(chain) if isinstance(chain, list) else chain for chain in tbl]

        before = snapshot_table(self.model.table)

        # 执行插入以得到 probe_path 和结果，同时保留插入后的表
        target_idx, probe_path, is_full, chain_pos = self.model.insert(value)
        after = snapshot_table(self.model.table)

        # 立即回滚到插入前状态，等待动画结束后再设置为插入后状态
        self.model.table = before
        # 重新计算 size
        if self.method == CollisionMethod.OPEN_ADDRESSING:
            self.model.size = sum(1 for v in self.model.table if v is not None and v is not TOMBSTONE)
        else:
            self.model.size = sum(len(chain) for chain in self.model.table)

        # 如果表满或值已存在，直接提示并刷新
        if is_full:
            self.update_display()
            messagebox.showerror("错误", "散列表已满，无法插入")
            # 继续批量（如果有）
            if self.batch_queue and self.batch_index < len(self.batch_queue):
                self.window.after(150, self._batch_step)
            return
        if target_idx is None:
            self.update_display()
            messagebox.showinfo("提示", "值已存在")
            if self.batch_queue and self.batch_index < len(self.batch_queue):
                self.window.after(150, self._batch_step)
            return

        # 开始动画流程
        self.animating = True
        self._set_buttons_state("disabled")
        self._anim_highlights = []

        # 绘制初始（回滚后）视图
        self.update_display()

        # 逐步高亮探测路径
        step_delay = 450  # 每步显示时长（ms）
        highlights = []

        def make_highlight(idx, color="#FFD54F"):
            x = self.start_x + idx * (self.cell_width + self.spacing)
            h = self.canvas.create_rectangle(x, self.start_y,
                                             x + self.cell_width, self.start_y + self.cell_height,
                                             outline="#E67E22", width=4)
            return h

        # schedule highlight steps
        current = {'i': 0}

        def highlight_step():
            i = current['i']
            if i > 0:
                # 将上一步恢复为原样（轻微淡化）
                try:
                    self.canvas.delete(highlights[i - 1])
                except Exception:
                    pass
            if i >= len(probe_path):
                # 探测结束 -> 执行动画：把值移动到 target_idx
                self._animate_move_into_cell(value, target_idx, after)
                return
            idx = probe_path[i]
            h = make_highlight(idx)
            highlights.append(h)
            current['i'] += 1
            # 在单元顶部显示当前探测索引提示
            # 先删除之前的提示
            if self._anim_temp:
                try:
                    self.canvas.delete(self._anim_temp)
                except Exception:
                    pass
                self._anim_temp = None
            top_x = self.start_x + (self.cell_width + self.spacing) * idx + self.cell_width / 2
            self._anim_temp = self.canvas.create_text(top_x, self.start_y - 40, text=f"探测 -> {idx}",
                                                      font=("Arial", 12, "bold"))

            self.window.after(step_delay, highlight_step)

        # 启动高亮步骤
        self.window.after(150, highlight_step)

    def _animate_move_into_cell(self, value, target_idx, final_table):
        """把值从上方移动到目标单元格，并在末尾把模型替换为插入后的 final_table"""
        # 创建一个临时文本在画布顶部（居中在表格上方）
        start_x = self.start_x + (self.cell_width + self.spacing) * 0 + self.cell_width / 2
        start_y = self.start_y - 80
        tx = self.canvas.create_text(start_x, start_y, text=str(value), font=("Arial", 12, "bold"))
        self._anim_temp = tx

        # 目标坐标
        tgt_x = self.start_x + target_idx * (self.cell_width + self.spacing) + self.cell_width / 2
        tgt_y = self.start_y + self.cell_height / 2

        steps = 12
        dx = (tgt_x - start_x) / steps
        dy = (tgt_y - start_y) / steps
        step = {'i': 0}

        def move_step():
            if step['i'] >= steps:
                # 到达目标位置：删除临时文本，应用 final_table，刷新显示，清理高亮
                try:
                    self.canvas.delete(tx)
                except Exception:
                    pass
                self._anim_temp = None
                # 应用插入后的表
                self.model.table = list(final_table)
                # 重新计算 size
                if self.method == CollisionMethod.OPEN_ADDRESSING:
                    self.model.size = sum(1 for v in self.model.table if v is not None and v is not TOMBSTONE)
                else:
                    self.model.size = sum(len(chain) for chain in self.model.table)
                # 刷新显示并结束动画
                self.update_display()
                # 清除所有高亮
                for h in list(self._anim_highlights):
                    try:
                        self.canvas.delete(h)
                    except Exception:
                        pass
                self._anim_highlights = []
                self.animating = False
                self._set_buttons_state("normal")
                # 继续批量
                if self.batch_queue and self.batch_index < len(self.batch_queue):
                    self.window.after(200, self._batch_step)
                return
            # 移动一步
            try:
                self.canvas.move(tx, dx, dy)
            except Exception:
                pass
            step['i'] += 1
            self.window.after(40, move_step)

        move_step()

    def find_value(self, value):
        if self.animating: return
        
        found, probe_path, chain_pos = self.model.find(value)
        
        if found:
            if self.method == CollisionMethod.CHAINING:
                messagebox.showinfo("查找", f"找到 {value}，索引 {probe_path[0]}，链表位置 {chain_pos}")
            else:
                messagebox.showinfo("查找", f"找到 {value}，索引 {probe_path[-1]}")
        else:
            messagebox.showinfo("查找", f"未找到 {value}")

    def delete_value(self, value):
        if self.animating: return
        
        del_idx, probe_path, chain_pos = self.model.delete(value)
        
        if del_idx is not None:
            self.update_display()
            if self.method == CollisionMethod.CHAINING:
                messagebox.showinfo("删除", f"已从索引 {del_idx} 的链表删除 {value}")
            else:
                messagebox.showinfo("删除", f"已在索引 {del_idx} 用墓碑删除 {value}")
        else:
            messagebox.showinfo("删除", f"未找到 {value}，无法删除")

    def clear_table(self):
        if self.animating: return
        self.model.clear()
        self.update_display()
        messagebox.showinfo("清空", "散列表已清空")

    # ------------------------------------------------------------------ #
    #                         批量处理
    # ------------------------------------------------------------------ #
    def _batch_step(self):
        if self.batch_index >= len(self.batch_queue):
            self.batch_queue = []
            self.batch_index = 0
            self._set_buttons_state("normal")
            return
        
        val = self.batch_queue[self.batch_index]
        self.batch_index += 1
        # 插入会在动画结束后自动触发下一步
        self.insert_value(val)

    # ------------------------------------------------------------------ #
    #                         显示更新
    # ------------------------------------------------------------------ #
    def update_display(self):
        self.canvas.delete("all")
        self.cell_rects.clear()
        self.cell_texts.clear()
        self.index_texts.clear()
        self.chain_elements.clear()

        total_width = (self.cell_width + self.spacing) * self.capacity

        # 背景渐变框
        for i in range(2):
            self.canvas.create_rectangle(
                self.start_x - 8 + i * 2, self.start_y - 8 + i * 2,
                self.start_x + total_width + 8 - i * 2,
                self.start_y + self.cell_height + 8 - i * 2,
                outline="#D0E3FF", fill=["#F5F9FF", "#EDF7FF"][i], width=1)

        # 信息面板
        self._draw_info_panel()

        # 绘制哈希表
        if self.method == CollisionMethod.OPEN_ADDRESSING:
            self._draw_open_addressing()
        else:
            self._draw_chaining()

    def _draw_info_panel(self):
        card_x, card_y = 20, 10
        card_w, card_h = 380, 150
        
        self._draw_rounded_rect(card_x - 8, card_y - 8,
                                card_x + card_w + 8, card_y + card_h + 8,
                                radius=12, fill="#F7FFF7", outline="#DDD", tags="card_shadow")
        self._draw_rounded_rect(card_x, card_y,
                                card_x + card_w, card_y + card_h,
                                radius=12, fill="#FFFFFF", outline="#E0E0E0", tags="card_body")

        # 标题
        method_name = "开放寻址法" if self.method == CollisionMethod.OPEN_ADDRESSING else "拉链法"
        self.canvas.create_text(card_x + 20, card_y + 22,
                                text=f"信息面板 ({method_name})",
                                anchor="w", font=("Microsoft YaHei UI", 14, "bold"),
                                fill="#2C3E50")

        # 统计信息
        stats = f"容量: {self.capacity}   有效元素数: {len(self.model)}"
        self.canvas.create_text(card_x + 20, card_y + 50,
                                text=stats, anchor="w",
                                font=("Microsoft YaHei UI", 12), fill="#34495E")

        if self.method == CollisionMethod.CHAINING:
            max_chain = self.model.get_max_chain_length()
            avg_chain = len(self.model) / self.capacity if self.capacity > 0 else 0
            chain_stats = f"最大链长: {max_chain}   平均链长: {avg_chain:.2f}"
            self.canvas.create_text(card_x + 20, card_y + 75,
                                    text=chain_stats, anchor="w",
                                    font=("Microsoft YaHei UI", 11), fill="#7F8C8D")

        # 操作说明
        ops = [
            ("插入", "insert x", "#3498DB"),
            ("查找", "find x", "#2ECC71"),
            ("删除", "delete x", "#E74C3C"),
            ("清空", "clear", "#95A5A6")
        ]
        base_y = card_y + 100
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

    def _draw_open_addressing(self):
        """绘制开放寻址法表格"""
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

    def _draw_chaining(self):
        """绘制拉链法表格"""
        for i in range(self.capacity):
            x = self.start_x + i * (self.cell_width + self.spacing)
            
            # 主格子
            rect = self.canvas.create_rectangle(x, self.start_y,
                                                x + self.cell_width,
                                                self.start_y + self.cell_height,
                                                fill="white", outline="black", width=2)
            self.cell_rects.append(rect)

            # 索引
            idx_txt = self.canvas.create_text(x + self.cell_width / 2,
                                              self.start_y - 16,
                                              text=str(i),
                                              font=("Arial", 10, "bold"))
            self.index_texts.append(idx_txt)

            # 链表元素
            chain = self.model.table[i]
            if not chain:
                cell_txt = self.canvas.create_text(x + self.cell_width / 2,
                                                   self.start_y + self.cell_height / 2,
                                                   text="NULL", font=("Arial", 10),
                                                   fill="#999999")
                self.cell_texts.append(cell_txt)
            else:
                # 显示链长
                chain_len_txt = self.canvas.create_text(x + self.cell_width / 2,
                                                        self.start_y + 15,
                                                        text=f"链长:{len(chain)}",
                                                        font=("Arial", 8),
                                                        fill="#666666")
                
                # 绘制链表节点
                node_y = self.start_y + self.cell_height + 10
                for j, item in enumerate(chain):
                    node_x = x + self.cell_width / 2
                    node_rect = self.canvas.create_rectangle(
                        node_x - 25, node_y + j * 35,
                        node_x + 25, node_y + j * 35 + 30,
                        fill="#E8F8F5", outline="#27AE60", width=2
                    )
                    node_txt = self.canvas.create_text(
                        node_x, node_y + j * 35 + 15,
                        text=str(item), font=("Arial", 11, "bold")
                    )
                    self.chain_elements.append((node_rect, node_txt))
                    
                    # 绘制箭头
                    if j < len(chain) - 1:
                        self.canvas.create_line(
                            node_x, node_y + j * 35 + 30,
                            node_x, node_y + (j + 1) * 35,
                            arrow=LAST, fill="#27AE60", width=2
                        )
                    else:
                        # 最后一个节点指向NULL
                        self.canvas.create_text(
                            node_x, node_y + j * 35 + 40,
                            text="↓ NULL", font=("Arial", 8),
                            fill="#999999"
                        )

    def _draw_rounded_rect(self, x0, y0, x1, y1, radius=10, **kwargs):
        """绘制圆角矩形"""
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

    def _set_buttons_state(self, state):
        """设置按钮状态"""
        for w in self.window.winfo_children():
            if isinstance(w, Frame):
                for c in w.winfo_children():
                    try:
                        c.config(state=state)
                    except Exception:
                        pass

    def back_to_main(self):
        """返回主界面"""
        if self.animating:
            messagebox.showinfo("提示", "动画进行中，无法返回")
            return
        self.window.destroy()


if __name__ == "__main__":
    root = Tk()
    root.title("散列表可视化")
    root.geometry("1350x770")
    root.minsize(1350, 770)
    
    # 可以选择启动模式
    # HashtableVisualizer(root, capacity=11, method=CollisionMethod.OPEN_ADDRESSING)
    HashtableVisualizer(root, capacity=11, method=CollisionMethod.OPEN_ADDRESSING)
    
    root.mainloop()
