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
        self.window.config(bg="#F0FFF5")
        self.window.title("循环队列可视化")
        self.canvas = Canvas(self.window, bg="white", width=1350, height=520, relief=RAISED, bd=8)
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

        self.create_heading()
        self.create_buttons()
        self.update_display()

    def create_heading(self):
        Label(self.window, text="循环队列（Circular Queue）可视化",
              font=("Arial", 28, "bold"), bg="#F0FFF5", fg="#0a5f3a").place(x=420, y=12)
        Label(self.window, text="环形缓冲：展示 head/tail 指针移动、入队/出队与满/空状态",
              font=("Arial", 13), bg="#F0FFF5", fg="black").place(x=400, y=64)

    def create_buttons(self):
        btn_frame = Frame(self.window, bg="#F0FFF5")
        btn_frame.place(x=40, y=420, width=1270, height=170)

        self.enqueue_btn = Button(btn_frame, text="入队 (Enqueue)", font=("Arial", 13),
                                  width=16, height=2, bg="#27AE60", fg="white", command=self.prepare_enqueue)
        self.enqueue_btn.grid(row=0, column=0, padx=12, pady=8)

        self.dequeue_btn = Button(btn_frame, text="出队 (Dequeue)", font=("Arial", 13),
                                  width=16, height=2, bg="#E74C3C", fg="white", command=self.animate_dequeue)
        self.dequeue_btn.grid(row=0, column=1, padx=12, pady=8)

        self.clear_btn = Button(btn_frame, text="清空队列", font=("Arial", 13),
                                width=16, height=2, bg="#F39C12", fg="white", command=self.clear_queue)
        self.clear_btn.grid(row=0, column=2, padx=12, pady=8)

        self.back_btn = Button(btn_frame, text="返回主界面", font=("Arial", 13),
                               width=16, height=2, bg="#3498DB", fg="white", command=self.back_to_main)
        self.back_btn.grid(row=0, column=3, padx=12, pady=8)

        Label(btn_frame, text="批量构建 (逗号分隔):", font=("Arial", 11), bg="#F0FFF5").grid(row=1, column=0, padx=(16, 4), pady=8, sticky="w")
        Entry(btn_frame, textvariable=self.batch_var, width=40, font=("Arial", 12)).grid(row=1, column=1, columnspan=2, padx=4, pady=8, sticky="w")
        self.batch_btn = Button(btn_frame, text="开始批量构建", font=("Arial", 11), command=self.start_batch)
        self.batch_btn.grid(row=1, column=3, padx=8, pady=8)

        Label(btn_frame, text="DSL 命令:", font=("Arial", 11), bg="#F0FFF5").grid(row=2, column=0, padx=(16,4), pady=6, sticky="w")
        dsl_entry = Entry(btn_frame, textvariable=self.dsl_var, width=60, font=("Arial", 11))
        dsl_entry.grid(row=2, column=1, columnspan=2, padx=4, pady=6, sticky="w")
        dsl_entry.bind("<Return>", self.process_dsl)
        Button(btn_frame, text="执行", font=("Arial", 11), command=self.process_dsl).grid(row=2, column=3, padx=8, pady=6)

        Button(btn_frame, text="保存", font=("Arial", 11), width=12, bg="#6C9EFF", fg="white", command=self.save_structure).grid(row=0, column=4, padx=8)
        Button(btn_frame, text="打开", font=("Arial", 11), width=12, bg="#6C9EFF", fg="white", command=self.load_structure).grid(row=1, column=4, padx=8)

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
        payload = {"type":"circular_queue","buffer":data,"meta":meta}
        with open(filepath,"w",encoding="utf-8") as f:
            json.dump(payload,f,ensure_ascii=False,indent=2)
        messagebox.showinfo("成功", f"已保存到：\n{filepath}")

    def load_structure(self):
        default_dir = self._ensure_folder()
        filepath = filedialog.askopenfilename(initialdir=default_dir, filetypes=[("JSON files","*.json")])
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
        if self.animating or self.model.is_full():
            if self.model.is_full():
                messagebox.showwarning("队列满", "队列已满")
            return
        if self.input_frame:
            self.input_frame.destroy()
            self.input_frame = None
        self.value_var.set("")
        self.input_frame = Frame(self.window, bg="#F0FFF5")
        self.input_frame.place(x=420, y=420, width=420, height=80)
        Label(self.input_frame, text="输入要入队的值:", font=("Arial", 12), bg="#F0FFF5").grid(row=0, column=0, padx=6, pady=6)
        Entry(self.input_frame, textvariable=self.value_var, font=("Arial", 12)).grid(row=0, column=1, padx=6, pady=6)
        Button(self.input_frame, text="确认", font=("Arial", 12), command=self._on_confirm_enqueue).grid(row=0, column=2, padx=6, pady=6)

    def _on_confirm_enqueue(self):
        value = self.value_var.get()
        if value == "":
            messagebox.showerror("错误", "请输入值")
            return
        if self.input_frame:
            self.input_frame.destroy()
            self.input_frame = None
        self.animate_enqueue(value)

    def animate_enqueue(self, value: Any, on_finish=None):
        if self.animating:
            return
        self.animating = True
        self._set_buttons_state("disabled")

        sx, sy = -120, self.center_y
        rect = self.canvas.create_rectangle(sx, sy, sx + self.cell_w, sy + self.cell_h, fill="#C8F7C5", outline="black", width=2)
        txt = self.canvas.create_text(sx + self.cell_w/2, sy + self.cell_h/2, text=str(value), font=("Arial", 14, "bold"))

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
                self.canvas.delete(rect); self.canvas.delete(txt)
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
        highlight = self.canvas.create_rectangle(x, y, x + self.cell_w, y + self.cell_h, fill="#FFD2D2", outline="black", width=2)
        val = self.model.buffer[head]
        txt = self.canvas.create_text(x + self.cell_w/2, y + self.cell_h/2, text=str(val) if val is not None else "", font=("Arial", 14, "bold"))

        steps = 30
        dx = (1400 - x) / steps
        delay = 12

        def step(i=0):
            if i < steps:
                self.canvas.move(highlight, dx, 0)
                self.canvas.move(txt, dx, 0)
                self.window.after(delay, lambda: step(i+1))
            else:
                self.canvas.delete(highlight); self.canvas.delete(txt)
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

        info_x, info_y, info_w = 24, 18, 360
        self.canvas.create_rectangle(info_x-8, info_y-8, info_x+info_w+8, info_y+140, fill="#F7FFF6", outline="#DDD")
        sz = self.model.size
        status = "满" if self.model.is_full() else ("空" if self.model.is_empty() else "非空")
        info_text = f"队列状态: {status}， 大小: {sz}/{self.capacity}"
        self.canvas.create_text(info_x+6, info_y+6, text=info_text, font=("Arial", 12), anchor="nw", width=info_w, justify=LEFT)
        instruct = "操作：enqueue <value> / dequeue / clear\n箭头显示 head/tail 指针位置\n批量构建支持逗号分隔（界面按钮）"
        self.canvas.create_text(info_x+6, info_y+44, text=instruct, font=("Arial", 11), anchor="nw", width=info_w, justify=LEFT)

        # boxes
        for i in range(self.capacity):
            x = self.center_x + i * (self.cell_w + self.gap)
            y = self.center_y
            rect = self.canvas.create_rectangle(x, y, x + self.cell_w, y + self.cell_h, fill="#FAFAFA", outline="#444", width=2)
            self.box_ids.append(rect)
            val = self.model.buffer[i]
            txt = self.canvas.create_text(x + self.cell_w/2, y + self.cell_h/2, text=(str(val) if val is not None else ""), font=("Arial", 14))
            self.text_ids.append(txt)
            self.canvas.create_text(x + self.cell_w/2, y + self.cell_h + 14, text=f"idx {i}", font=("Arial", 10))

        # head/tail
        head, tail = self.model.head, self.model.tail
        hx = self.center_x + head * (self.cell_w + self.gap) + self.cell_w/2
        hy = self.center_y - 28
        self.canvas.create_line(hx, hy, hx, self.center_y, arrow=LAST, width=2, fill="#E67E22")
        self.canvas.create_text(hx, hy - 16, text=f"head ({head})", font=("Arial", 10), fill="#E67E22")

        tx = self.center_x + tail * (self.cell_w + self.gap) + self.cell_w/2
        ty = self.center_y + self.cell_h + 28
        self.canvas.create_line(tx, self.center_y + self.cell_h, tx, ty, arrow=LAST, width=2, fill="#2E86C1")
        self.canvas.create_text(tx, ty + 16, text=f"tail ({tail})", font=("Arial", 10), fill="#2E86C1")

    def _set_buttons_state(self, state):
        if self.enqueue_btn: self.enqueue_btn.config(state=state)
        if self.dequeue_btn: self.dequeue_btn.config(state=state)
        if self.clear_btn: self.clear_btn.config(state=state)
        if self.back_btn: self.back_btn.config(state=state)
        if self.batch_btn: self.batch_btn.config(state=state)
        if self.input_frame:
            for child in self.input_frame.winfo_children():
                child.config(state=state)

    def back_to_main(self):
        if self.animating:
            messagebox.showinfo("提示", "动画尚在进行，无法返回")
            return
        self.window.destroy()

if __name__ == '__main__':
    root = Tk()
    root.title("循环队列 可视化")
    root.geometry("1350x770")
    CircularQueueVisualizer(root)
    root.mainloop()
