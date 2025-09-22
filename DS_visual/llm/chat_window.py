# chat_window.py
import threading
import time
import tkinter as tk
from tkinter import Toplevel, Frame, Text, Button, END, ttk, messagebox, simpledialog
from tkinter.scrolledtext import ScrolledText

from llm.doubao_client import DoubaoClient

from llm import function_dispatcher
from llm.function_schemas import get_function_schemas

import re

# Styling constants
USER_BG = "#DCF8C6"         # 左侧/用户气泡背景 (淡绿)
ASSIST_BG = "#FFFFFF"       # 右侧/助手气泡背景 (白)
BG_COLOR = "#F6F7F9"        # 窗口背景
INPUT_BG = "#FFFFFF"
ACCENT = "#10A37F"          # 按钮/高亮色
TEXT_COLOR = "#111827"
META_COLOR = "#6B7280"

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
        self.win.title("与豆包模型聊天")
        self.win.geometry("820x640")
        self.win.configure(bg=BG_COLOR)
        self.win.minsize(560, 400)

        # Top bar (title + actions)
        topbar = Frame(self.win, bg=BG_COLOR, padx=12, pady=8)
        topbar.pack(fill='x')
        title = tk.Label(topbar, text="豆包 聊天", font=("Helvetica", 14, "bold"), bg=BG_COLOR, fg=TEXT_COLOR)
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
        self._system_message("欢迎 — 可直接输入问题，与豆包模型聊天（Enter 发送，Shift+Enter 换行）。")

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
            os.environ["DOUBAO_TIMEOUT"] = "None"
            self.client.timeout = None
        else:
            try:
                iv = int(val)
                os.environ["DOUBAO_TIMEOUT"] = str(iv)
                self.client.timeout = iv
            except Exception:
                messagebox.showerror("设置错误", "请输入整数秒或 None。")

    def _insert_example(self):
        example = "给我讲解一下单链表这个数据结构：\n"
        self.entry.insert("end", example)

    # --- Message creation (bubbles) ---
    def _add_message_bubble(self, who: str, text: str, align: str = "right"):
        """
        who: "你" or "豆包"
        align: "left" (user) or "right" (assistant)
        returns: reference to label widget (useful for streaming to update text)
        """
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
    
    def _worker_handle_function_call(self, user_text: str, assistant_var: tk.StringVar):
        """
        1) 先请求模型（带 functions）；
        2) 如果模型直接返回 function_call -> dispatch 并显示结果；
        3) 如果模型返回普通文本 -> 先尝试本地解析（regex），能解析则 dispatch；
        否则再向模型发起一次“只返回 function_call”的请求，若得到 function_call 则 dispatch。
        """
        try:
            functions = get_function_schemas()
            resp = self.client.send_message_with_functions(user_text, functions=functions, timeout_read=None)

            # CASE A: 模型直接返回 function_call
            if resp.get("type") == "function_call":
                name = resp.get("name")
                args = resp.get("arguments") or {}
                self.win.after(0, lambda: assistant_var.set(f"[函数调用] {name} -> {args}"))
                result = function_dispatcher.dispatch(name, args)
                self.win.after(0, lambda: assistant_var.set(assistant_var.get() + f"\n\n执行结果: {result.get('message','')}"))
                return

            # CASE B: 模型返回普通文本（或 fallback）
            text = resp.get("text", "")
            if not text:
                text = "(空回复)"
            # 先把模型的文本显示出来
            self.win.after(0, lambda: assistant_var.set(text))

            # 1) 本地解析尝试直接提取动作并 dispatch
            parsed_result = self.__parse_and_dispatch_from_text(text)
            if parsed_result:
                # parsed_result 是 dispatcher 返回的 dict
                msg = parsed_result.get("message", "")
                self.win.after(0, lambda: assistant_var.set(assistant_var.get() + f"\n\n本地解析并执行结果: {msg}"))
                return

            # 2) 如果本地解析失败，向模型再次请求（明确要求只返回 function_call）
            followup_prompt = (
                "注意：如果你想触发前端可视化演示（例如向单链表插入/删除、批量创建、或栈的 push/pop），"
                "请**只**以 function_call 的形式返回（不要返回额外的自然语言说明）。"
                "可用函数包括：linked_list_insert_last, linked_list_insert_first, linked_list_delete_first, "
                "linked_list_delete_last, linked_list_create, stack_push, stack_pop。"
                "如果你判断需要演示，就返回相应的 function_call 并把必要参数放在 arguments 中。"
            )
            resp2 = self.client.send_message_with_functions(f"模型原文：{text}\n\n{followup_prompt}", functions=functions, timeout_read=None)
            if resp2.get("type") == "function_call":
                name = resp2.get("name")
                args = resp2.get("arguments") or {}
                self.win.after(0, lambda: assistant_var.set(assistant_var.get() + f"\n\n[函数调用] {name} -> {args}"))
                result = function_dispatcher.dispatch(name, args)
                self.win.after(0, lambda: assistant_var.set(assistant_var.get() + f"\n\n执行结果: {result.get('message','')}"))
                return

            # 最后兜底：没有 function_call 也没有本地解析到
            self.win.after(0, lambda: assistant_var.set(assistant_var.get() + "\n\n（未检测到可执行操作；未触发可视化）"))
        except Exception as e:
            self.win.after(0, lambda: assistant_var.set(f"调用失败：{e}"))
        finally:
            self.win.after(0, self._finish_stream)
    def _chinese_num_to_int(self, s: str):
        """简单中文数字到整数（支持 0-99 的常见写法：零 一 二 三 ... 十 二十三 等）"""
        s = s.strip()
        if not s:
            return None
        # 先尝试直接转 int
        try:
            return int(s)
        except Exception:
            pass
        # 简单映射
        digits = {"零":0,"一":1,"二":2,"两":2,"三":3,"四":4,"五":5,"六":6,"七":7,"八":8,"九":9}
        if all(ch in digits or ch=="十" for ch in s):
            if "十" in s:
                parts = s.split("十")
                if parts[0] == "":  # 十, 十三
                    tens = 1
                else:
                    tens = digits.get(parts[0], 0)
                ones = 0
                if len(parts) > 1 and parts[1] != "":
                    ones = digits.get(parts[1], 0)
                return tens*10 + ones
            else:
                # 纯个位中文
                return digits.get(s, None)
        return None

    def __parse_and_dispatch_from_text(self, text: str):
        """
        修复版解析器：优先识别创建（批量）操作，且优先提取方括号内的值。
        目标：避免把 '创建链表[1,2,3]' 中的 '创建链表' 当作第一个元素误传入 UI。
        """
        if not text or not isinstance(text, str):
            return None

        # candidates: 先用户输入，再模型回复
        candidates = []
        last_user = getattr(self, "_last_user_text", "") or ""
        if last_user:
            candidates.append(last_user)
        if text and text not in candidates:
            candidates.append(text)

        def extract_list_from_string(s: str):
            """
            尝试从字符串中提取元素列表，优先：
            1) 方括号 [ ... ] 内的内容
            2) 紧跟在创建/批量/生成关键词后的数字/词序列（由逗号或空白分隔）
            返回 values 列表或 None
            """
            if not s:
                return None
            # 1) 方括号优先
            m_br = re.search(r"\[([^\]]+)\]", s)
            if m_br:
                raw = m_br.group(1)
                vals = [p.strip() for p in re.split(r"[,\s，、]+", raw) if p.strip() != ""]
                if vals:
                    return vals
            # 2) 关键词后面的序列（只取包含数字/字母/中文字符的部分）
            m_after = re.search(r"(?:创建|批量|生成|初始化|建立|构建)[^\d\[\]]*([0-9A-Za-z\u4e00-\u9fff\-\_,，、\s]+)", s)
            if m_after:
                raw = m_after.group(1)
                vals = [p.strip() for p in re.split(r"[,\s，、]+", raw) if p.strip() != ""]
                # 过滤掉明显是说明性的词（例如包含“创建”“链表”“位置”等）
                filtered = [v for v in vals if not re.search(r"(创建|构建|链表|单链表|位置|插入|在|第|位|值为|值是)", v)]
                if filtered:
                    return filtered
                # 如果过滤后为空，但原 vals 看起来像数字序列（全部是数字），则返回原 vals
                if vals and all(re.match(r"^[+-]?\d+$", v) for v in vals):
                    return vals
            return None

        # main loop: 优先创建
        for s in candidates:
            s = (s or "").strip()
            if not s:
                continue

            # ===== 优先：创建 / 批量操作 =====
            if re.search(r"(创建|批量|初始化|生成|建立|构建)", s):
                vals = extract_list_from_string(s)
                if vals:
                    print("parse -> linked_list_create (extracted):", vals)
                    return function_dispatcher.dispatch("linked_list_create", {"values": [str(v) for v in vals]})
                else:
                    # 发现创建关键词但没取到 values -> 不盲目执行，提示需要明确
                    print("parse -> detect '创建' but no values found in:", s)
                    return {"ok": False, "message": "检测到创建意图，但未找到要创建的元素列表。请使用类似 `创建链表 [1,2,3]` 或 `批量创建 1,2,3`。"}

            # ===== 插入 / 删除 / 栈 等（保留原先行为，优先数字匹配） =====
            # 第 N 位插入
            m_pos_val = re.search(r"第\s*(\d+)\s*(?:个|位|位置).*?插入.*?(?:值为)?[:：]?\s*([+-]?\d+)", s)
            if m_pos_val:
                idx = int(m_pos_val.group(1))
                val = m_pos_val.group(2)
                print(f"parse -> linked_list_insert_at index={idx}, val={val}")
                return function_dispatcher.dispatch("linked_list_insert_at", {"index": idx, "value": str(val)})

            # 明确插入值（数字优先）
            m_insert_val = re.search(r"(?:在.*插入|插入|insert).*?(?:值为)?[:：]?\s*([+-]?\d+)", s, flags=re.IGNORECASE)
            if m_insert_val:
                val = m_insert_val.group(1)
                if re.search(r"(头部|首位|开头)", s):
                    return function_dispatcher.dispatch("linked_list_insert_first", {"value": str(val)})
                if re.search(r"(尾部|末尾|尾端|后面|最后)", s):
                    return function_dispatcher.dispatch("linked_list_insert_last", {"value": str(val)})
                if re.search(r"(链表|单链表|list)", s):
                    return function_dispatcher.dispatch("linked_list_insert_last", {"value": str(val)})

            # 删除首/尾
            if re.search(r"(删除|移除).{0,6}(首|头|第一个|第 1 个|第1个)", s):
                return function_dispatcher.dispatch("linked_list_delete_first", {})
            if re.search(r"(删除|移除).{0,6}(尾|最后|末尾|尾部)", s):
                return function_dispatcher.dispatch("linked_list_delete_last", {})

            # 栈 push/pop
            m_push = re.search(r"(?:push|入栈|压栈)[:：]?\s*([+-]?\d+)", s, flags=re.IGNORECASE)
            if m_push:
                val = m_push.group(1)
                return function_dispatcher.dispatch("stack_push", {"value": str(val)})
            if re.search(r"\b(pop|出栈|弹出)\b", s):
                return function_dispatcher.dispatch("stack_pop", {})

        # 本地规则都未命中 -> 回退给模型解析（你已有的更复杂模型解析逻辑）
        print("parse -> local rules not matched; invoking model parser (fallback).")
        return self._parse_with_model_and_dispatch(last_user, text)



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
