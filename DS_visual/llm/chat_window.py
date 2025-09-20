# chat_window.py（带回车发送与 Shift+Enter 换行支持）
import threading
import time
from tkinter import Toplevel, Frame, Text, Button, END
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

        # ---- 关键：绑定按键事件 ----
        # Enter -> 发送（并阻止插入换行）
        self.entry.bind("<Return>", self._on_entry_return)
        # Shift+Enter -> 在文本中插入换行（保留换行功能）
        self.entry.bind("<Shift-Return>", self._on_shift_enter)
        # Ctrl+Enter -> 也发送（适合中文输入法场景）
        self.entry.bind("<Control-Return>", self._on_entry_return)

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

    # ---- 键盘事件处理函数 ----
    def _on_entry_return(self, event):
        """
        处理 Enter / Ctrl+Enter：触发发送。
        返回 "break" 阻止 Text 默认插入换行。
        """
        # 如果按钮被禁用（正在发送），忽略输入
        if str(self.send_btn['state']) == 'disabled':
            return "break"
        # 触发发送
        self._on_send()
        # 阻止事件继续传播（防止插入换行）
        return "break"

    def _on_shift_enter(self, event):
        """
        处理 Shift+Enter：在光标位置插入换行符并将焦点放回输入框。
        返回 "break" 防止默认行为（有些平台会重复插入）。
        """
        self.entry.insert("insert", "\n")
        # 将光标移动到插入点（可选）
        self.entry.see("insert")
        return "break"
