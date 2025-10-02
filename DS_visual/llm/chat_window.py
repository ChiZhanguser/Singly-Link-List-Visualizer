# chat_window.py
import threading
import time
import tkinter as tk
from tkinter import Toplevel, Frame, Text, Button, END, ttk, messagebox, simpledialog
from tkinter.scrolledtext import ScrolledText

from llm.doubao_client import DoubaoClient

from llm import function_dispatcher
from llm.function_schemas import get_function_schemas
import json
import re

# Styling constants
USER_BG = "#DCF8C6"         # 左侧/用户气泡背景 (淡绿)
ASSIST_BG = "#FFFFFF"       # 右侧/助手气泡背景 (白)
BG_COLOR = "#F6F7F9"        # 窗口背景
INPUT_BG = "#FFFFFF"
ACCENT = "#10A37F"          # 按钮/高亮色
TEXT_COLOR = "#111827"
META_COLOR = "#6B7280"

STRICT_JSON_PROMPT = (
    "注意：**严格返回一个 JSON 对象，且不能包含任何额外自然语言**。"
    "返回格式必须为单个 JSON object，例如：\n"
    '{"name":"stack_push","arguments":{"value":1}}\n'
    "或：\n"
    '{"name":"stack_pop","arguments":{}}\n'
    "不要使用任何标记、函数调用样式（例如 stack_push(1)）或额外说明文字。\n"
)


class ChatWindow:
    def __init__(self, parent):
        self.parent = parent
        try:
            self.client = DoubaoClient()
        except Exception as e:
            messagebox.showerror("配置错误", str(e))
            return

        # Create window
        self.win = Toplevel(parent)
        self.win.title("LLM 聊天窗口 ")
        self.win.geometry("820x640")
        self.win.configure(bg=BG_COLOR)
        self.win.minsize(560, 400)

        # Top bar (title + actions)
        topbar = Frame(self.win, bg=BG_COLOR, padx=12, pady=8)
        topbar.pack(fill='x')
        title = tk.Label(topbar, text="LLM 聊天窗口", font=("Helvetica", 14, "bold"), bg=BG_COLOR, fg=TEXT_COLOR)
        title.pack(side='left')

        btn_frame = Frame(topbar, bg=BG_COLOR)
        btn_frame.pack(side='right')
        clear_btn = ttk.Button(btn_frame, text="清空", command=self._clear_messages)
        clear_btn.pack(side='right', padx=(6,0))
        settings_btn = ttk.Button(btn_frame, text="设置", command=self._open_settings)
        settings_btn.pack(side='right', padx=(6,0))

        # Main content area: left padding + message canvas
        content = Frame(self.win, bg=BG_COLOR)
        content.pack(fill='both', expand=True, padx=12, pady=(4,8))

        # Scrollable messages area using Canvas
        self.canvas = tk.Canvas(content, bg=BG_COLOR, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(content, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side='right', fill='y')
        self.canvas.pack(side='left', fill='both', expand=True)

        # Frame inside canvas to hold message widgets
        self.messages_frame = Frame(self.canvas, bg=BG_COLOR)
        self.canvas.create_window((0,0), window=self.messages_frame, anchor='nw', tags="messages_frame")

        # Bind to resize scrollregion
        self.messages_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # Input area
        input_frame = Frame(self.win, bg=BG_COLOR, padx=12, pady=10)
        input_frame.pack(fill='x')

        self.entry = Text(input_frame, height=4, wrap='word', font=("Helvetica", 12), bg=INPUT_BG, relief='flat')
        self.entry.pack(side='left', fill='x', expand=True, padx=(0,8))
        self.entry.bind("<Return>", self._on_entry_return)
        self.entry.bind("<Shift-Return>", self._on_shift_enter)
        self.entry.bind("<Control-Return>", self._on_entry_return)

        right_controls = Frame(input_frame, bg=BG_COLOR)
        right_controls.pack(side='right')

        self.send_btn = tk.Button(right_controls, text="发送", bg=ACCENT, fg="white", activebackground="#0e8a63",
                                  font=("Helvetica", 11, "bold"), width=10, command=self._on_send)
        self.send_btn.pack(side='top', pady=(0,6))
        # Optional quick buttons
        self.quick_btn = ttk.Button(right_controls, text="示例", command=self._insert_example)
        self.quick_btn.pack(side='top')

        # Keep track of whether currently streaming
        self._streaming = False

        # Add a polite welcome system message
        self._system_message("欢迎 — 可直接输入问题（Enter 发送，Shift+Enter 换行）。")

    # --- Utilities / UI behaviors ---
    def _on_mousewheel(self, event):
        # Mac & Windows compatible scroll
        delta = -1*(event.delta//120) if event.delta else 0
        self.canvas.yview_scroll(delta, "units")

    def _system_message(self, text: str):
        # Small grey system message in center
        lbl = tk.Label(self.messages_frame, text=text, bg=BG_COLOR, fg=META_COLOR, font=("Helvetica", 10), wraplength=520, justify='center')
        lbl.pack(pady=(8,8))

    def _clear_messages(self):
        for child in self.messages_frame.winfo_children():
            child.destroy()
        # re-add small welcome
        self._system_message("对话已清空。")

    def _open_settings(self):
        # Very small settings dialog for DOUBAO_TIMEOUT
        cur = self.client.timeout
        val = simpledialog.askstring("设置", f"当前 read 超时: {cur}\n输入秒数或 None（不限制）:", parent=self.win)
        if val is None:
            return
        val = val.strip()
        if val.lower() == "none":
            import os
            os.environ["DOUBAO_TIMEOUT"] = "None"
            self.client.timeout = None
        else:
            try:
                iv = int(val)
                import os
                os.environ["DOUBAO_TIMEOUT"] = str(iv)
                self.client.timeout = iv
            except Exception:
                messagebox.showerror("设置错误", "请输入整数秒或 None。")

    def _insert_example(self):
        example = "将1压入栈"
        self.entry.insert("end", example)

    # --- Message creation (bubbles) ---
    def _add_message_bubble(self, who: str, text: str, align: str = "right"):
        container = Frame(self.messages_frame, bg=BG_COLOR)
        container.pack(fill='x', pady=6, padx=8)

        is_user = (who == "你")
        side = 'e' if is_user else 'w'
        # bubble frame
        bubble_frame = Frame(container, bg=BG_COLOR)
        bubble_frame.pack(anchor=side, padx=(60,8) if is_user else (8,60))

        # timestamp + who (small)
        meta = tk.Label(bubble_frame, text=f"{who}  {time.strftime('%H:%M:%S')}", bg=BG_COLOR, fg=META_COLOR, font=("Helvetica", 8))
        meta.pack(anchor='e' if is_user else 'w')

        # bubble (Label inside a Frame to allow padding)
        bubble_bg = USER_BG if is_user else ASSIST_BG
        fg = TEXT_COLOR if not is_user else TEXT_COLOR
        bubble = Frame(bubble_frame, bg=bubble_bg, bd=0, relief='flat')
        bubble.pack(anchor='e' if is_user else 'w')

        # text variable for streaming update
        var = tk.StringVar(value=text)
        lbl = tk.Label(bubble, textvariable=var, justify='left', anchor='w',
                       font=("Helvetica", 12), bg=bubble_bg, fg=fg, wraplength=520)
        lbl.pack(padx=10, pady=8)

        return var, lbl, bubble

    # --- Sending & streaming ---
    def _on_send(self):
        if self._streaming:
            return  # prevent re-send while streaming
        user_text = self.entry.get("1.0", END).strip()
        if not user_text:
            return
        self._last_user_text = user_text
        # clear input
        self.entry.delete("1.0", END)
        # add user bubble
        self._add_message_bubble("你", user_text, align="left")

        # prepare assistant bubble with empty content (stream target)
        assistant_var, assistant_lbl, _ = self._add_message_bubble("豆包", "", align="right")
        # scroll to bottom
        self.win.after(50, lambda: self.canvas.yview_moveto(1.0))

        # disable send button
        self.send_btn.config(state='disabled', bg="#84BFAA")
        self._streaming = True

        # start worker thread for streaming
        threading.Thread(target=self._worker_handle_function_call, args=(user_text, assistant_var), daemon=True).start()

    def _extract_message_object(self, resp):
        # handle list
        if isinstance(resp, list):
            # prefer the last dict with 'type'
            for item in reversed(resp):
                if isinstance(item, dict) and 'type' in item:
                    return item
            # try to find openai-like choices in list
            for item in reversed(resp):
                if isinstance(item, dict) and 'choices' in item:
                    resp = item
                    break

        # handle dicts (many possible layouts)
        if isinstance(resp, dict):
            # already a typed message
            if 'type' in resp:
                return resp

            # openai style: { "choices":[ { "message": {...} } ] }
            if 'choices' in resp and isinstance(resp['choices'], list) and len(resp['choices']) > 0:
                choice = resp['choices'][-1]
                if isinstance(choice, dict) and 'message' in choice and isinstance(choice['message'], dict):
                    m = choice['message']
                    if 'function_call' in m and isinstance(m['function_call'], dict):
                        fc = m['function_call']
                        return {'type': 'function_call', 'name': fc.get('name'), 'arguments': fc.get('arguments')}
                    return {'type': 'assistant_text', 'text': m.get('content') or m.get('text') or ''}
                if isinstance(choice, dict) and 'function_call' in choice:
                    fc = choice['function_call']
                    return {'type': 'function_call', 'name': fc.get('name'), 'arguments': fc.get('arguments')}
                if isinstance(choice, dict) and ('text' in choice or 'message' in choice):
                    return {'type': 'assistant_text', 'text': choice.get('text') or choice.get('message')}

            # some clients return {'messages': [...]}
            if 'messages' in resp and isinstance(resp['messages'], list):
                for item in reversed(resp['messages']):
                    if isinstance(item, dict) and 'type' in item:
                        return item

            # fallback: if there's a 'text' field treat as assistant_text
            if 'text' in resp:
                return {'type': 'assistant_text', 'text': resp.get('text')}

        return None
    
    def _worker_handle_function_call(self, user_text: str, assistant_var: tk.StringVar):
        try:
            functions = get_function_schemas("all")
            # resp = self.client.send_message_with_functions(user_text, functions=functions, timeout_read=None)

            system_msg = (
                "系统指令：你**必须**只输出一个单独的 JSON 对象，不能包含任何多余的自然语言。"
                "格式：{\"name\":\"FUNCTION_NAME\",\"arguments\":{...}}。"
            )
            examples = "示例: 用户: 将1压入栈 -> {\"name\":\"stack_push\",\"arguments\":{\"value\":1}}"

            messages = [
                {"role":"system", "content": system_msg + "\n" + STRICT_JSON_PROMPT},
                {"role":"user", "content": examples + "\n用户输入:\n" + user_text}
            ]

            resp = self.client.send_message_with_functions(
                messages=messages,
                functions=functions,
                temperature=0.0,
                timeout_read=None
            )
            
            # debug print for dev (if you want more visibility)
            print("debug -> raw resp from client:", repr(resp)[:2000])

            msg = self._extract_message_object(resp)
            if msg is None:
                # defensive: if resp is dict with 'text' present
                if isinstance(resp, dict) and 'text' in resp:
                    msg = {'type': 'assistant_text', 'text': resp.get('text', '')}
                else:
                    print("parse -> cannot extract message object from initial resp:", resp)
                    self.win.after(0, lambda: assistant_var.set("（模型回复无法解析；未触发可视化）"))
                    return

            # if model already returned function_call
            if msg.get('type') == 'function_call':
                print("model already returned function_call")
                name = msg.get('name')
                args = msg.get('arguments') or {}
                self.win.after(0, lambda: assistant_var.set(f"[函数调用] {name} -> {args}"))
                result = function_dispatcher.dispatch(name, args)
                # safely display result.message if present
                res_msg = result.get('message') if isinstance(result, dict) else str(result)
                self.win.after(0, lambda: assistant_var.set(assistant_var.get() + f"\n\n执行结果: {res_msg}"))
                return

            # if assistant_text: try to extract embedded function call markers or JSON
            if msg.get('type') == 'assistant_text':
                print("assistant_text")
                text = msg.get('text', '') or ''
                self.win.after(0, lambda: assistant_var.set(text))

                # try to extract <|FunctionCallBegin|> ... <|FunctionCallEnd|>
                m = re.search(r"<\|FunctionCallBegin\|>(.*?)<\|FunctionCallEnd\|>", text, re.S)
                if m:
                    payload = m.group(1).strip()
                    parsed_obj = None
                    # first try JSON
                    try:
                        parsed_obj = json.loads(payload)
                    except Exception:
                        # try single quotes -> double quotes
                        try:
                            parsed_obj = json.loads(payload.replace("'", '"'))
                        except Exception:
                            parsed_obj = None

                    if isinstance(parsed_obj, dict) and 'name' in parsed_obj:
                        name = parsed_obj.get('name')
                        params = parsed_obj.get('parameters') or parsed_obj.get('arguments') or {}
                        self.win.after(0, lambda: assistant_var.set(assistant_var.get() + f"\n\n[函数调用] {name} -> {params}"))
                        result = function_dispatcher.dispatch(name, params)
                        res_msg = result.get('message') if isinstance(result, dict) else str(result)
                        self.win.after(0, lambda: assistant_var.set(assistant_var.get() + f"\n\n执行结果: {res_msg}"))
                        return
                    else:
                        # could not parse payload
                        print("parse -> found markers but payload not parseable:", payload)

                # try to find a JSON object like {"name": "...", "arguments": {...}} inside text
                json_m = re.search(r"(\{.*\"name\".*\})", text, re.S)
                if json_m:
                    payload = json_m.group(1)
                    try:
                        obj = json.loads(payload)
                    except Exception:
                        try:
                            obj = json.loads(payload.replace("'", '"'))
                        except Exception:
                            obj = None
                    if isinstance(obj, dict) and 'name' in obj:
                        name = obj.get('name')
                        params = obj.get('parameters') or obj.get('arguments') or {}
                        self.win.after(0, lambda: assistant_var.set(assistant_var.get() + f"\n\n[函数调用] {name} -> {params}"))
                        result = function_dispatcher.dispatch(name, params)
                        res_msg = result.get('message') if isinstance(result, dict) else str(result)
                        self.win.after(0, lambda: assistant_var.set(assistant_var.get() + f"\n\n执行结果: {res_msg}"))
                        return
                # 没有 function_call, 输出自然语言
                self.win.after(0, lambda: assistant_var.set(assistant_var.get() + "\n\n（未检测到可执行操作；未触发可视化）"))
                return

            # unknown type
            print("parse -> unexpected message type:", msg)
            self.win.after(0, lambda: assistant_var.set("（未识别模型输出类型；未触发可视化）"))
            return

        except Exception as e:
            print("worker error:", e)
            self.win.after(0, lambda: assistant_var.set(assistant_var.get() + f"\n\n注: 没有进行函数调"))
        finally:
            self.win.after(0, self._finish_stream)

    def _on_entry_return(self, event):
        # Enter sends unless Shift held
        if event.state & 0x0001:  # Shift pressed (platform dependent); we also bind Shift separately
            return
        if str(self.send_btn['state']) == 'disabled':
            return "break"
        self._on_send()
        return "break"

    def _on_shift_enter(self, event):
        self.entry.insert("insert", "\n")
        self.entry.see("insert")
        return "break"

    def _worker_stream(self, user_text: str, assistant_var: tk.StringVar):
        try:
            # stream: True; timeout_read=None => use client.timeout (can be None)
            for chunk in self.client.send_message_stream(user_text, stream=True, timeout_read=None, show_reasoning=False):
                # update UI in main thread
                self.win.after(0, lambda c=chunk: self._append_chunk(assistant_var, c))
            # finished: add final newline and re-enable
            self.win.after(0, self._finish_stream)
        except Exception as e:
            # show error in assistant bubble
            self.win.after(0, lambda: assistant_var.set(f"调用失败：{e}"))
            self.win.after(0, self._finish_stream)

    def _append_chunk(self, var: tk.StringVar, chunk: str):
        current = var.get()
        # Append chunk (no extra spacing, chunks usually are continuous)
        var.set(current + chunk)
        # auto-scroll to bottom
        self.canvas.yview_moveto(1.0)

    def _finish_stream(self):
        self._streaming = False
        self.send_btn.config(state='normal', bg=ACCENT)
        # ensure spacing after message
        spacer = Frame(self.messages_frame, height=6, bg=BG_COLOR)
        spacer.pack()

    def _on_reply(self, reply_text: str):
        # fallback for non-stream replies
        self._add_message_bubble("豆包", reply_text, align="right")
        self.send_btn.config(state='normal')

# If you want to test this window standalone:
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # hide main root
    ChatWindow(root)
    root.mainloop()
