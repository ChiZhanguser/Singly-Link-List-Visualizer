# chat_window.py (带非单调背景的美化版)
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

# ================= Styling constants (可集中修改) =================
USER_BG = "#E6F8EE"         # 用户气泡（淡绿）
ASSIST_BG = "#FFFFFF"       # 助手气泡（白）
BG_COLOR = "#F3F6F9"        # 窗口背景（浅灰蓝）
BG_GRAD_2 = "#EEF9F4"       # 渐变第二色（浅绿偏白）
INPUT_BG = "#FFFFFF"
ACCENT = "#0F9370"          # 主色（按钮 / 亮色）
ACCENT_DARK = "#0d7b5e"
TEXT_COLOR = "#0F1724"
META_COLOR = "#6B7280"
SYSTEM_BG = "#EEF2F3"
BUBBLE_RADIUS = 8
FONT_FAMILY = "Helvetica"

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
        self.win.title("LLM 聊天窗口")
        self.win.geometry("880x660")
        self.win.configure(bg=BG_COLOR)
        self.win.minsize(560, 420)

        # Global ttk style
        style = ttk.Style(self.win)
        style.theme_use('default')
        style.configure("Accent.TButton", background=ACCENT, foreground="white", font=(FONT_FAMILY, 10, "bold"), padding=6)
        style.map("Accent.TButton",
                  background=[('active', ACCENT_DARK), ('disabled', '#94cdb7')])
        style.configure("Meta.TButton", foreground=TEXT_COLOR, font=(FONT_FAMILY, 9))
        style.configure("TScrollbar", gripcount=0, background="#E6EEF0", troughcolor="#F3F6F9", bordercolor="#F3F6F9")

        # Top bar (title + actions) with subtle shadow bar
        topbar = Frame(self.win, bg=BG_COLOR, padx=14, pady=10)
        topbar.pack(fill='x')
        title_frame = Frame(topbar, bg=BG_COLOR)
        title_frame.pack(side='left', anchor='w')
        title = tk.Label(title_frame, text="LLM 聊天窗口", font=(FONT_FAMILY, 15, "bold"), bg=BG_COLOR, fg=TEXT_COLOR)
        title.pack(side='left')
        subtitle = tk.Label(title_frame, text=" — 支持结构化函数调用与可视化触发", font=(FONT_FAMILY, 9), bg=BG_COLOR, fg=META_COLOR)
        subtitle.pack(side='left', padx=(8,0))

        btn_frame = Frame(topbar, bg=BG_COLOR)
        btn_frame.pack(side='right')
        clear_btn = ttk.Button(btn_frame, text="清空", style="Meta.TButton", command=self._clear_messages)
        clear_btn.pack(side='right', padx=(8,0))
        settings_btn = ttk.Button(btn_frame, text="设置", style="Meta.TButton", command=self._open_settings)
        settings_btn.pack(side='right', padx=(8,0))

        # separator line
        sep = Frame(self.win, height=1, bg="#E6EEF3")
        sep.pack(fill='x')

        # Main content area: left padding + message canvas
        content = Frame(self.win, bg=BG_COLOR)
        content.pack(fill='both', expand=True, padx=14, pady=(8,10))

        # Scrollable messages area using Canvas
        self.canvas = tk.Canvas(content, bg=BG_COLOR, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(content, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side='right', fill='y')
        self.canvas.pack(side='left', fill='both', expand=True)

        # Frame inside canvas to hold message widgets
        self.messages_frame = Frame(self.canvas, bg=BG_COLOR)
        # keep a stable tag for raising later
        self.canvas.create_window((0,0), window=self.messages_frame, anchor='nw', tags="messages_frame")

        # Bind to resize scrollregion & redraw background
        self.messages_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self._draw_canvas_background())
        # mousewheel support (Windows + Mac compatibility)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)  # Linux
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

        # Input area (rounded-like visual via Frame + padding)
        input_frame = Frame(self.win, bg=BG_COLOR, padx=14, pady=12)
        input_frame.pack(fill='x')

        entry_container = Frame(input_frame, bg=INPUT_BG, bd=0, relief='flat', padx=8, pady=8)
        entry_container.pack(side='left', fill='x', expand=True, padx=(0,10))
        self.entry = Text(entry_container, height=4, wrap='word', font=(FONT_FAMILY, 12), bg=INPUT_BG, relief='flat', bd=0)
        self.entry.pack(fill='both', expand=True)
        self.entry.bind("<Return>", self._on_entry_return)
        self.entry.bind("<Shift-Return>", self._on_shift_enter)
        self.entry.bind("<Control-Return>", self._on_entry_return)

        right_controls = Frame(input_frame, bg=BG_COLOR)
        right_controls.pack(side='right')

        self.send_btn = tk.Button(right_controls, text="发送", bg=ACCENT, fg="white", activebackground=ACCENT_DARK,
                                  font=(FONT_FAMILY, 11, "bold"), width=10, command=self._on_send, bd=0)
        self.send_btn.pack(side='top', pady=(2,8))
        # Optional quick buttons
        self.quick_btn = ttk.Button(right_controls, text="示例", style="Meta.TButton", command=self._insert_example)
        self.quick_btn.pack(side='top')

        # keep track
        self._streaming = False

        # draw initial bg once (canvas might not be configured size yet; Configure binding will redraw)
        self._draw_canvas_background()

        # Add a polite welcome system message (centered and distinct)
        self._system_message("欢迎 — 直接输入问题（Enter 发送，Shift+Enter 换行）。界面已优化，功能保持不变。")

    # ================== 背景绘制相关（非单调背景） ==================
    def _hex_to_rgb(self, h: str):
        h = h.lstrip('#')
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

    def _rgb_to_hex(self, rgb):
        return '#{:02x}{:02x}{:02x}'.format(*rgb)

    def _interpolate(self, c1, c2, t: float):
        return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

    def _draw_canvas_background(self):
        """
        在 self.canvas 上绘制柔和的竖向渐变，并加上非常浅的斜纹装饰（不会影响文本可读性）。
        使用 tag 'bg' 以便重绘时清理旧图形；最后把 messages_frame 提到最上层。
        """
        try:
            w = max(self.canvas.winfo_width(), 2)
            h = max(self.canvas.winfo_height(), 2)
        except Exception:
            return

        # remove previous bg items
        self.canvas.delete("bg")

        # gradient from BG_COLOR -> BG_GRAD_2
        c1 = self._hex_to_rgb(BG_COLOR)
        c2 = self._hex_to_rgb(BG_GRAD_2)

        steps = 24  # 渐变条段数（越大越平滑，代价为绘制更多矩形）
        for i in range(steps):
            y0 = int(h * (i / steps))
            y1 = int(h * ((i + 1) / steps))
            t = (i + 0.5) / steps
            color = self._rgb_to_hex(self._interpolate(c1, c2, t))
            self.canvas.create_rectangle(0, y0, w, y1, fill=color, outline="", tags=("bg",))

        # subtle diagonal stripes — 非常浅的线，不抢眼
        stripe_color = "#F1F6F4"  # 近乎透明的浅色
        spacing = 36
        # draw a few diagonal lines across canvas
        # we limit number so performance is fine
        for x in range(-h, w + h, spacing):
            self.canvas.create_line(x, 0, x + h, h, fill=stripe_color, width=1, tags=("bg",))

        # soft watermark text in bottom-right
        watermark_text = "LLM 可视化"
        # choose an extremely light color so it never影响可读性
        wm_color = "#F2F7F4"
        self.canvas.create_text(w - 12, h - 12, text=watermark_text, anchor='se', font=(FONT_FAMILY, 9, "italic"),
                                fill=wm_color, tags=("bg",))

        # ensure the messages_frame window is above the bg
        try:
            self.canvas.tag_raise("messages_frame")
        except Exception:
            pass

    # --- Utilities / UI behaviors ---
    def _on_mousewheel(self, event):
        # cross-platform scrolling
        if hasattr(event, 'num') and event.num == 4:   # Linux scroll up
            self.canvas.yview_scroll(-3, "units")
        elif hasattr(event, 'num') and event.num == 5: # Linux scroll down
            self.canvas.yview_scroll(3, "units")
        else:
            # Windows / Mac: event.delta is multiples of 120
            delta = -1*(event.delta//120) if event.delta else 0
            self.canvas.yview_scroll(delta, "units")

    def _system_message(self, text: str):
        # System message with subtle panel
        panel = Frame(self.messages_frame, bg=SYSTEM_BG, bd=0, relief='flat', padx=12, pady=8)
        panel.pack(pady=(10,10), padx=120, fill='x')
        lbl = tk.Label(panel, text=text, bg=SYSTEM_BG, fg=META_COLOR, font=(FONT_FAMILY, 10), wraplength=520, justify='center')
        lbl.pack()

    def _clear_messages(self):
        for child in self.messages_frame.winfo_children():
            child.destroy()
        # re-add small welcome
        self._system_message("对话已清空。")

    def _open_settings(self):
        cur = getattr(self.client, "timeout", None)
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
        self.entry.see("end")

    # --- Message creation (bubbles) ---
    def _add_message_bubble(self, who: str, text: str, align: str = "right"):
        container = Frame(self.messages_frame, bg=BG_COLOR)
        container.pack(fill='x', pady=8, padx=12)

        is_user = (who == "你")
        side = 'e' if is_user else 'w'

        # bubble frame with avatar + bubble
        bubble_frame = Frame(container, bg=BG_COLOR)
        bubble_frame.pack(anchor=side, padx=(80,12) if is_user else (12,80))

        # small avatar circle
        avatar = tk.Canvas(bubble_frame, width=36, height=36, bg=BG_COLOR, highlightthickness=0)
        avatar.pack(side='right' if is_user else 'left', padx=(6,10) if is_user else (0,10))
        color = "#10A37F" if is_user else "#6B7280"
        avatar.create_oval(4,4,32,32, fill=color, outline="")

        # meta label (who + time)
        meta = tk.Label(bubble_frame, text=f"{who}  {time.strftime('%H:%M:%S')}", bg=BG_COLOR, fg=META_COLOR, font=(FONT_FAMILY, 8))
        meta.pack(anchor='e' if is_user else 'w')

        # bubble background frame (use pad to imitate rounded bubble)
        bubble_bg = USER_BG if is_user else ASSIST_BG
        bubble = Frame(bubble_frame, bg=bubble_bg, bd=0, relief='flat', padx=10, pady=8)
        bubble.pack(anchor='e' if is_user else 'w')

        # text variable for streaming update
        var = tk.StringVar(value=text)
        lbl = tk.Label(bubble, textvariable=var, justify='left', anchor='w',
                       font=(FONT_FAMILY, 12), bg=bubble_bg, fg=TEXT_COLOR, wraplength=560)
        lbl.pack()

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
        # scroll to bottom slightly after UI update
        self.win.after(60, lambda: self.canvas.yview_moveto(1.0))

        # disable send button visually
        self.send_btn.config(state='disabled', bg="#84BFAA")
        self._streaming = True

        # start worker thread for streaming
        threading.Thread(target=self._worker_handle_function_call, args=(user_text, assistant_var), daemon=True).start()

    def _extract_message_object(self, resp):
        # same robust extraction as original
        if isinstance(resp, list):
            for item in reversed(resp):
                if isinstance(item, dict) and 'type' in item:
                    return item
            for item in reversed(resp):
                if isinstance(item, dict) and 'choices' in item:
                    resp = item
                    break

        if isinstance(resp, dict):
            if 'type' in resp:
                return resp
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

            if 'messages' in resp and isinstance(resp['messages'], list):
                for item in reversed(resp['messages']):
                    if isinstance(item, dict) and 'type' in item:
                        return item

            if 'text' in resp:
                return {'type': 'assistant_text', 'text': resp.get('text')}

        return None

    def _worker_handle_function_call(self, user_text: str, assistant_var: tk.StringVar):
        try:
            functions = get_function_schemas("all")

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

            print("debug -> raw resp from client:", repr(resp)[:2000])

            msg = self._extract_message_object(resp)
            if msg is None:
                if isinstance(resp, dict) and 'text' in resp:
                    msg = {'type': 'assistant_text', 'text': resp.get('text', '')}
                else:
                    print("parse -> cannot extract message object from initial resp:", resp)
                    self.win.after(0, lambda: assistant_var.set("（模型回复无法解析；未触发可视化）"))
                    return

            if msg.get('type') == 'function_call':
                print("model already returned function_call")
                name = msg.get('name')
                args = msg.get('arguments') or {}
                self.win.after(0, lambda: assistant_var.set(f"[函数调用] {name} -> {args}"))
                result = function_dispatcher.dispatch(name, args)
                res_msg = result.get('message') if isinstance(result, dict) else str(result)
                self.win.after(0, lambda: assistant_var.set(assistant_var.get() + f"\n\n执行结果: {res_msg}"))
                return

            if msg.get('type') == 'assistant_text':
                print("assistant_text")
                text = msg.get('text', '') or ''
                self.win.after(0, lambda: assistant_var.set(text))

                # try to extract markers / JSON - same as original
                m = re.search(r"<\|FunctionCallBegin\|>(.*?)<\|FunctionCallEnd\|>", text, re.S)
                if m:
                    payload = m.group(1).strip()
                    parsed_obj = None
                    try:
                        parsed_obj = json.loads(payload)
                    except Exception:
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
                        print("parse -> found markers but payload not parseable:", payload)

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

                self.win.after(0, lambda: assistant_var.set(assistant_var.get() + "\n\n（未检测到可执行操作；未触发可视化）"))
                return

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
        if event.state & 0x0001:  # Shift pressed (platform dependent)
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
            for chunk in self.client.send_message_stream(user_text, stream=True, timeout_read=None, show_reasoning=False):
                self.win.after(0, lambda c=chunk: self._append_chunk(assistant_var, c))
            self.win.after(0, self._finish_stream)
        except Exception as e:
            self.win.after(0, lambda: assistant_var.set(f"调用失败：{e}"))
            self.win.after(0, self._finish_stream)

    def _append_chunk(self, var: tk.StringVar, chunk: str):
        current = var.get()
        var.set(current + chunk)
        self.canvas.yview_moveto(1.0)

    def _finish_stream(self):
        self._streaming = False
        self.send_btn.config(state='normal', bg=ACCENT)
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
