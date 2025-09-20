# chat_window.py
import threading
import time
from tkinter import Toplevel, Frame, Text, Button, Label, END
from tkinter.scrolledtext import ScrolledText
from tkinter import messagebox

from llm.doubao_client import DoubaoClient

class ChatWindow:
    def __init__(self, parent):
        self.parent = parent
        try:
            self.client = DoubaoClient()  # 可能抛出错误（没设置 KEY）
        except Exception as e:
            messagebox.showerror("配置错误", str(e))
            return

        self.win = Toplevel(parent)
        self.win.title("与豆包模型聊天")
        self.win.geometry("640x480")

        # 消息展示区
        self.msg_area = ScrolledText(self.win, state='disabled', wrap='word', font=("Arial", 11))
        self.msg_area.pack(fill='both', expand=True, padx=8, pady=(8,4))

        # 底部输入区
        bottom = Frame(self.win)
        bottom.pack(fill='x', padx=8, pady=8)
        self.entry = Text(bottom, height=3, font=("Arial", 11))
        self.entry.pack(side='left', fill='x', expand=True, padx=(0,8))
        self.send_btn = Button(bottom, text="发送", width=10, command=self._on_send)
        self.send_btn.pack(side='right')

    def _append_message(self, who: str, text: str):
        self.msg_area.config(state='normal')
        timestamp = time.strftime("%H:%M:%S")
        self.msg_area.insert('end', f"{who} [{timestamp}]:\n")
        self.msg_area.insert('end', f"{text}\n\n")
        self.msg_area.see('end')
        self.msg_area.config(state='disabled')

    def _on_send(self):
        user_text = self.entry.get("1.0", END).strip()
        if not user_text:
            return
        self.entry.delete("1.0", END)
        self._append_message("你", user_text)
        self.send_btn.config(state='disabled')
        threading.Thread(target=self._worker, args=(user_text,), daemon=True).start()

    def _worker(self, user_text: str):
        try:
            reply = self.client.send_message(user_text)
        except Exception as e:
            reply = f"调用失败：{e}"
        # 回到主线程更新 UI
        self.win.after(0, lambda: self._on_reply(reply))

    def _on_reply(self, reply_text: str):
        self._append_message("豆包", reply_text)
        self.send_btn.config(state='normal')
