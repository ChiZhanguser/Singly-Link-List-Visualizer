from tkinter import *
from tkinter import messagebox, filedialog
import json
import os
from datetime import datetime
from typing import Any, List, Optional

from circular_queue.circular_queue_model import CircularQueueModel
import storage
from DSL_utils import circular_queue_dsl

process_command = circular_queue_dsl._fallback_process_command

class CircularQueueVisualizer:
    def __init__(self, root):
        self.window = root
        self.window.config(bg="#F5F7FA")
        self.window.title("循环队列可视化")
        
        # 使用现代化字体
        self.title_font = ("Microsoft YaHei", 24, "bold")
        self.subtitle_font = ("Microsoft YaHei", 11)
        self.button_font = ("Microsoft YaHei", 11)
        self.input_font = ("Microsoft YaHei", 11)
        self.canvas_font = ("Microsoft YaHei", 12)
        
        # 创建主框架
        self.main_frame = Frame(self.window, bg="#F5F7FA")
        self.main_frame.pack(fill=BOTH, expand=True, padx=20, pady=15)
        
        # 标题区域
        self.create_heading()
        
        # 画布区域
        self.canvas_frame = Frame(self.main_frame, bg="#F5F7FA")
        self.canvas_frame.pack(fill=X, pady=(0, 20))
        
        self.canvas = Canvas(self.canvas_frame, bg="white", width=1350, height=520, 
                           relief="flat", bd=0, highlightthickness=1, highlightbackground="#E1E8ED")
        self.canvas.pack()
        
        self.capacity = 8
        self.model = CircularQueueModel(self.capacity)

        self.box_ids: List[int] = []
        self.text_ids: List[int] = []

        # 布局参数
        self.center_x = 120
        self.center_y = 220
        self.cell_w = 110
        self.cell_h = 60
        self.gap = 14

        # 控件 & 状态
        self.value_var = StringVar()
        self.batch_var = StringVar()
        self.batch_var.set("1,2,3,4,5,6,7,8")
        self.dsl_var = StringVar()
        self.input_frame = None

        self.enqueue_btn = None
        self.dequeue_btn = None
        self.clear_btn = None
        self.batch_btn = None
        self.back_btn = None

        self.batch_queue: List[str] = []
        self.batch_index = 0
        self.animating = False

        self.create_control_panel()
        self.update_display()

    def create_heading(self):
        heading_frame = Frame(self.main_frame, bg="#F5F7FA")
        heading_frame.pack(fill=X, pady=(0, 20))
        
        title_label = Label(heading_frame, text="循环队列可视化系统", 
                          font=self.title_font, bg="#F5F7FA", fg="#2C3E50")
        title_label.pack()
        
        subtitle_label = Label(heading_frame, 
                             text="环形缓冲数据结构：展示 head/tail 指针移动、入队/出队与满/空状态",
                             font=self.subtitle_font, bg="#F5F7FA", fg="#7F8C8D")
        subtitle_label.pack(pady=(5, 0))

    def create_control_panel(self):
        # 主控制面板
        control_frame = Frame(self.main_frame, bg="#FFFFFF", relief="flat", bd=1, 
                            highlightbackground="#E1E8ED", highlightthickness=1)
        control_frame.pack(fill=X, pady=(0, 10))
        
        # 第一行：主要操作按钮
        btn_row1 = Frame(control_frame, bg="#FFFFFF")
        btn_row1.pack(fill=X, padx=20, pady=15)
        
        # 修复：确保按钮命令正确绑定
        self.enqueue_btn = self.create_modern_button(btn_row1, "入队 (Enqueue)", "#3498DB", 
                                                   self.prepare_enqueue)
        self.enqueue_btn.pack(side=LEFT, padx=8, pady=5)
        
        self.dequeue_btn = self.create_modern_button(btn_row1, "出队 (Dequeue)", "#E74C3C", 
                                                   self.animate_dequeue)
        self.dequeue_btn.pack(side=LEFT, padx=8, pady=5)
        
        self.clear_btn = self.create_modern_button(btn_row1, "清空队列", "#F39C12", 
                                                 self.clear_queue)
        self.clear_btn.pack(side=LEFT, padx=8, pady=5)
        
        self.back_btn = self.create_modern_button(btn_row1, "返回主界面", "#95A5A6", 
                                                self.back_to_main)
        self.back_btn.pack(side=LEFT, padx=8, pady=5)
        
        # 文件操作按钮放在第一行右侧
        save_btn = self.create_modern_button(btn_row1, "保存结构", "#1ABC9C", 
                                           self.save_structure, small=True)
        save_btn.pack(side=RIGHT, padx=8, pady=5)
        
        load_btn = self.create_modern_button(btn_row1, "加载结构", "#1ABC9C", 
                                           self.load_structure, small=True)
        load_btn.pack(side=RIGHT, padx=8, pady=5)
        
        # 第二行：批量操作
        btn_row2 = Frame(control_frame, bg="#FFFFFF")
        btn_row2.pack(fill=X, padx=20, pady=15)
        
        batch_label = Label(btn_row2, text="批量构建 (逗号分隔):", 
                          font=self.button_font, bg="#FFFFFF", fg="#2C3E50")
        batch_label.pack(side=LEFT, padx=(0, 10), pady=5)
        
        batch_entry = Entry(btn_row2, textvariable=self.batch_var, width=40, 
                          font=self.input_font, relief="solid", bd=1)
        batch_entry.pack(side=LEFT, padx=10, pady=5)
        
        self.batch_btn = self.create_modern_button(btn_row2, "开始批量构建", "#27AE60", 
                                                 self.start_batch, small=True)
        self.batch_btn.pack(side=LEFT, padx=8, pady=5)
        
        # 第三行：DSL命令
        btn_row3 = Frame(control_frame, bg="#FFFFFF")
        btn_row3.pack(fill=X, padx=20, pady=(0, 15))
        
        dsl_label = Label(btn_row3, text="DSL 命令:", 
                        font=self.button_font, bg="#FFFFFF", fg="#2C3E50")
        dsl_label.pack(side=LEFT, padx=(0, 10), pady=5)
        
        dsl_entry = Entry(btn_row3, textvariable=self.dsl_var, width=50, 
                        font=self.input_font, relief="solid", bd=1)
        dsl_entry.pack(side=LEFT, padx=10, pady=5)
        dsl_entry.bind("<Return>", self.process_dsl)
        
        execute_btn = self.create_modern_button(btn_row3, "执行", "#9B59B6", 
                                              self.process_dsl, small=True)
        execute_btn.pack(side=LEFT, padx=8, pady=5)

    def create_modern_button(self, parent, text, color, command, small=False):
        btn_font = self.button_font if not small else ("Microsoft YaHei", 10)
        btn_width = 16 if not small else 12
        
        # 修复：确保命令正确传递
        btn = Button(parent, text=text, font=btn_font,
                    width=btn_width, height=1 if small else 2, 
                    bg=color, fg="white", 
                    activebackground=self.darken_color(color),
                    activeforeground="white",
                    relief="flat", bd=0,
                    command=command)  # 直接传递命令，不使用lambda
        
        # 添加悬停效果
        def on_enter(e):
            btn['bg'] = self.darken_color(color)
        def on_leave(e):
            btn['bg'] = color
            
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
        return btn

    def darken_color(self, color):
        # 简单的颜色变暗函数
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)
        
        r = max(0, r - 30)
        g = max(0, g - 30)
        b = max(0, b - 30)
        
        return f"#{r:02x}{g:02x}{b:02x}"

    def process_dsl(self, event=None):
        text = self.dsl_var.get().strip()
        if not text:
            return
        process_command(self, text)
        self.dsl_var.set("")

    def _ensure_folder(self):
        return storage.ensure_save_subdir("circular_queue")

    def save_structure(self):
        data = list(self.model.buffer)
        meta = {"capacity": self.capacity, "head": self.model.head, "tail": self.model.tail, "size": self.model.size}
        default_dir = self._ensure_folder()
        default_name = f"cqueue_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = filedialog.asksaveasfilename(initialdir=default_dir, initialfile=default_name, defaultextension=".json", filetypes=[("JSON files","*.json")])
        if filepath:
            payload = {"type":"circular_queue","buffer":data,"meta":meta}
            with open(filepath,"w",encoding="utf-8") as f:
                json.dump(payload,f,ensure_ascii=False,indent=2)
            messagebox.showinfo("成功", f"已保存到：\n{filepath}")

    def load_structure(self):
        default_dir = self._ensure_folder()
        filepath = filedialog.askopenfilename(initialdir=default_dir, filetypes=[("JSON files","*.json")])
        if filepath:
            with open(filepath,"r",encoding="utf-8") as f:
                loaded = json.load(f)
            buf = loaded.get("buffer", [])
            meta = loaded.get("meta", {})
            self.model.buffer = list(buf)[:self.capacity]
            self.model.capacity = self.capacity
            self.model.head = int(meta.get("head", 0))
            self.model.tail = int(meta.get("tail", 0))
            self.model.size = int(meta.get("size", sum(1 for x in buf if x is not None)))
            self.update_display()
            messagebox.showinfo("成功", "已加载循环队列")

    def prepare_enqueue(self):
        """准备入队操作 - 显示输入框"""
        if self.animating:
            messagebox.showwarning("提示", "动画进行中，请稍候")
            return
            
        if self.model.is_full():
            messagebox.showwarning("队列满", "队列已满，无法入队")
            return
            
        # 如果已有输入框，先销毁
        if self.input_frame:
            self.input_frame.destroy()
            self.input_frame = None
        
        self.value_var.set("")
        # 创建输入框
        self.input_frame = Frame(self.main_frame, bg="#F5F7FA", relief="flat", bd=1,
                               highlightbackground="#E1E8ED", highlightthickness=1)
        self.input_frame.pack(fill=X, pady=10)
        
        input_content = Frame(self.input_frame, bg="#F5F7FA")
        input_content.pack(padx=20, pady=15)
        
        Label(input_content, text="输入要入队的值:", 
              font=self.button_font, bg="#F5F7FA", fg="#2C3E50").pack(side=LEFT, padx=(0, 10))
        
        entry = Entry(input_content, textvariable=self.value_var, 
                     font=self.input_font, width=20, relief="solid", bd=1)
        entry.pack(side=LEFT, padx=10)
        entry.focus_set()  # 自动聚焦
        
        # 确认按钮
        confirm_btn = Button(input_content, text="确认入队", font=self.button_font,
                           width=12, height=1, 
                           bg="#3498DB", fg="white", 
                           activebackground=self.darken_color("#3498DB"),
                           activeforeground="white",
                           relief="flat", bd=0,
                           command=self._on_confirm_enqueue)
        confirm_btn.pack(side=LEFT, padx=5)
        
        # 取消按钮
        cancel_btn = Button(input_content, text="取消", font=self.button_font,
                          width=8, height=1,
                          bg="#95A5A6", fg="white",
                          activebackground=self.darken_color("#95A5A6"),
                          activeforeground="white",
                          relief="flat", bd=0,
                          command=self._cancel_input)
        cancel_btn.pack(side=LEFT, padx=5)
        
        # 添加悬停效果
        for btn in [confirm_btn, cancel_btn]:
            color = btn.cget("bg")
            def make_on_enter(button, btn_color):
                def on_enter(e):
                    button['bg'] = self.darken_color(btn_color)
                return on_enter
            def make_on_leave(button, btn_color):
                def on_leave(e):
                    button['bg'] = btn_color
                return on_leave
            
            btn.bind("<Enter>", make_on_enter(btn, color))
            btn.bind("<Leave>", make_on_leave(btn, color))
        
        # 绑定回车键到确认
        entry.bind("<Return>", lambda e: self._on_confirm_enqueue())

    def _cancel_input(self):
        """取消输入"""
        if self.input_frame:
            self.input_frame.destroy()
            self.input_frame = None

    def _on_confirm_enqueue(self):
        """确认入队操作"""
        value = self.value_var.get().strip()
        if not value:
            messagebox.showerror("错误", "请输入要入队的值")
            return
            
        # 销毁输入框
        if self.input_frame:
            self.input_frame.destroy()
            self.input_frame = None
            
        # 执行入队动画
        self.animate_enqueue(value)

    def animate_enqueue(self, value: Any, on_finish=None):
        """执行入队动画"""
        if self.animating:
            return
            
        if self.model.is_full():
            messagebox.showwarning("队列满", "队列已满，无法入队")
            return
            
        self.animating = True
        self._set_buttons_state("disabled")

        # 创建移动的元素
        sx, sy = -120, self.center_y
        rect = self.canvas.create_rectangle(sx, sy, sx + self.cell_w, sy + self.cell_h, 
                                          fill="#D5F5E3", outline="#27AE60", width=2)
        txt = self.canvas.create_text(sx + self.cell_w/2, sy + self.cell_h/2, 
                                    text=str(value), font=("Microsoft YaHei", 14, "bold"), fill="#145A32")

        tail_idx = self.model.tail
        tx = self.center_x + tail_idx * (self.cell_w + self.gap)
        steps = 30
        dx = (tx - sx) / steps
        delay = 12

        def step(i=0):
            if i < steps:
                self.canvas.move(rect, dx, 0)
                self.canvas.move(txt, dx, 0)
                self.window.after(delay, lambda: step(i+1))
            else:
                self.canvas.delete(rect)
                self.canvas.delete(txt)
                ok = self.model.enqueue(value)
                if not ok:
                    messagebox.showwarning("队列满", "入队失败：队列已满")
                self.update_display()
                self.animating = False
                self._set_buttons_state("normal")
                if on_finish:
                    on_finish()
        step()

    def animate_dequeue(self, on_finish=None):
        if self.animating or self.model.is_empty():
            if self.model.is_empty():
                messagebox.showwarning("队列空", "队列为空")
            return
        self.animating = True
        self._set_buttons_state("disabled")

        head = self.model.head
        x = self.center_x + head * (self.cell_w + self.gap)
        y = self.center_y
        highlight = self.canvas.create_rectangle(x, y, x + self.cell_w, y + self.cell_h, 
                                               fill="#FADBD8", outline="#E74C3C", width=2)
        val = self.model.buffer[head]
        txt = self.canvas.create_text(x + self.cell_w/2, y + self.cell_h/2, 
                                    text=str(val) if val is not None else "", 
                                    font=("Microsoft YaHei", 14, "bold"), fill="#922B21")

        steps = 30
        dx = (1400 - x) / steps
        delay = 12

        def step(i=0):
            if i < steps:
                self.canvas.move(highlight, dx, 0)
                self.canvas.move(txt, dx, 0)
                self.window.after(delay, lambda: step(i+1))
            else:
                self.canvas.delete(highlight)
                self.canvas.delete(txt)
                self.model.dequeue()
                self.update_display()
                self.animating = False
                self._set_buttons_state("normal")
                if on_finish:
                    on_finish()
        step()

    def clear_queue(self):
        if self.animating or self.model.is_empty():
            if self.model.is_empty():
                messagebox.showinfo("信息", "队列已空")
            return
        self._set_buttons_state("disabled")
        self.model.clear()
        self.update_display()
        self._set_buttons_state("normal")

    def start_batch(self):
        if self.animating:
            return
        text = self.batch_var.get().strip()
        if not text:
            messagebox.showinfo("提示", "请输入要构建的值，例如：1,2,3")
            return
        items = [s.strip() for s in text.split(",") if s.strip() != ""]
        available = self.capacity - self.model.size
        if len(items) > available:
            if not messagebox.askyesno("容量不足", f"当前可用位置 {available}，要入队 {len(items)} 个。是否只入队前 {available} 个？"):
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
        v = self.batch_queue[self.batch_index]
        self.batch_index += 1
        self.animate_enqueue(v, on_finish=self._batch_step)

    def update_display(self):
        self.canvas.delete("all")
        self.box_ids.clear()
        self.text_ids.clear()

        # 信息面板
        info_x, info_y, info_w = 24, 18, 360
        self.canvas.create_rectangle(info_x-8, info_y-8, info_x+info_w+8, info_y+140, 
                                   fill="#F8F9F9", outline="#D5DBDB", width=2)
        
        sz = self.model.size
        status = "满" if self.model.is_full() else ("空" if self.model.is_empty() else "非空")
        status_color = "#E74C3C" if self.model.is_full() else ("#7F8C8D" if self.model.is_empty() else "#27AE60")
        
        self.canvas.create_text(info_x+6, info_y+6, 
                              text=f"队列状态: {status}， 大小: {sz}/{self.capacity}",
                              font=self.canvas_font, anchor="nw", width=info_w, 
                              justify=LEFT, fill=status_color)
        
        instruct = "操作指南：\n• enqueue <value> / dequeue / clear\n• 箭头显示 head/tail 指针位置\n• 批量构建支持逗号分隔输入"
        self.canvas.create_text(info_x+6, info_y+44, text=instruct, 
                              font=("Microsoft YaHei", 10), anchor="nw", 
                              width=info_w, justify=LEFT, fill="#566573")

        # 绘制队列单元格
        for i in range(self.capacity):
            x = self.center_x + i * (self.cell_w + self.gap)
            y = self.center_y
            
            # 单元格样式
            fill_color = "#EBF5FB" if self.model.buffer[i] is not None else "#FDFEFE"
            outline_color = "#3498DB" if self.model.buffer[i] is not None else "#BDC3C7"
            
            rect = self.canvas.create_rectangle(x, y, x + self.cell_w, y + self.cell_h, 
                                              fill=fill_color, outline=outline_color, width=2)
            self.box_ids.append(rect)
            
            val = self.model.buffer[i]
            txt = self.canvas.create_text(x + self.cell_w/2, y + self.cell_h/2, 
                                        text=(str(val) if val is not None else "空"), 
                                        font=("Microsoft YaHei", 12, "bold"),
                                        fill="#2C3E50")
            self.text_ids.append(txt)
            
            # 索引标签
            self.canvas.create_text(x + self.cell_w/2, y + self.cell_h + 14, 
                                  text=f"位置 {i}", font=("Microsoft YaHei", 9), fill="#7F8C8D")

        # head/tail 指针
        head, tail = self.model.head, self.model.tail
        hx = self.center_x + head * (self.cell_w + self.gap) + self.cell_w/2
        hy = self.center_y - 28
        self.canvas.create_line(hx, hy, hx, self.center_y, arrow=LAST, width=3, fill="#E67E22")
        self.canvas.create_text(hx, hy - 16, text=f"head ({head})", 
                              font=("Microsoft YaHei", 10, "bold"), fill="#E67E22")

        tx = self.center_x + tail * (self.cell_w + self.gap) + self.cell_w/2
        ty = self.center_y + self.cell_h + 28
        self.canvas.create_line(tx, self.center_y + self.cell_h, tx, ty, arrow=LAST, width=3, fill="#2E86C1")
        self.canvas.create_text(tx, ty + 16, text=f"tail ({tail})", 
                              font=("Microsoft YaHei", 10, "bold"), fill="#2E86C1")

    def _set_buttons_state(self, state):
        buttons = [self.enqueue_btn, self.dequeue_btn, self.clear_btn, self.back_btn, self.batch_btn]
        for btn in buttons:
            if btn:
                btn.config(state=state)
        
        if self.input_frame:
            for child in self.input_frame.winfo_children():
                if hasattr(child, 'config') and 'state' in child.config():
                    child.config(state=state)

    def back_to_main(self):
        if self.animating:
            messagebox.showinfo("提示", "动画尚在进行，无法返回")
            return
        self.window.destroy()

if __name__ == '__main__':
    root = Tk()
    root.title("循环队列可视化系统")
    root.geometry("1350x800")
    root.configure(bg="#F5F7FA")
    CircularQueueVisualizer(root)
    root.mainloop()