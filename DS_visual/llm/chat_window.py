# chat_window.py
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
            self.client = DoubaoClient()  # 从环境变量读取 key/url/model
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

        # 绑定回车发送（Enter 发送, Shift+Enter 换行, Ctrl+Enter 也发送）
        self.entry.bind("<Return>", self._on_entry_return)
        self.entry.bind("<Shift-Return>", self._on_shift_enter)
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
        # 显示用户消息
        self._append_message("你", user_text)

        # 在开始流时先插入“豆包”头（空回答），后续流式追加文本
        self.msg_area.config(state='normal')
        timestamp = time.strftime("%H:%M:%S")
        self.msg_area.insert('end', f"豆包 [{timestamp}]:\n")
        self.msg_area.config(state='disabled')

        self.send_btn.config(state='disabled')
        threading.Thread(target=self._worker_stream, args=(user_text,), daemon=True).start()

    def _worker_stream(self, user_text: str):
        """
        流式版本：逐片段更新 UI。若服务不支持流式，会回退到一次性结果。
        """
        try:
            # timeout_read=None 表示使用 client 的默认 read 超时（如果在环境变量设置为 "None" 则表示不限时）
            for chunk in self.client.send_message_stream(user_text, stream=True, timeout_read=None):
                # 回到主线程追加片段
                self.win.after(0, lambda c=chunk: self._append_stream(c))
            # 流结束后确保换行（把一个空行追加），并恢复按钮
            self.win.after(0, lambda: self._finish_stream())
        except Exception as e:
            # 出错时把错误信息展示出来并恢复按钮
            self.win.after(0, lambda: self._on_reply(f"调用失败：{e}"))
            self.win.after(0, lambda: self.send_btn.config(state='normal'))

    def _append_stream(self, text_fragment: str):
        # 追加片段（不添加 who/timestamp，因为已在发送前插入头）
        self.msg_area.config(state='normal')
        self.msg_area.insert('end', text_fragment)
        self.msg_area.see('end')
        self.msg_area.config(state='disabled')

    def _finish_stream(self):
        self.msg_area.config(state='normal')
        self.msg_area.insert('end', "\n\n")
        self.msg_area.see('end')
        self.msg_area.config(state='disabled')
        self.send_btn.config(state='normal')

    def _on_reply(self, reply_text: str):
        # 传统一次性回复显示（回退场景）
        self._append_message("豆包", reply_text)
        self.send_btn.config(state='normal')

    # 键盘事件处理
    def _on_entry_return(self, event):
        if str(self.send_btn['state']) == 'disabled':
            return "break"
        self._on_send()
        return "break"

    def _on_shift_enter(self, event):
        self.entry.insert("insert", "\n")
        self.entry.see("insert")
        return "break"
