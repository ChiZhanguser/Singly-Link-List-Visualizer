import threading
import json
import re
import tkinter as tk
from tkinter import messagebox, END
from llm.doubao_client import DoubaoClient
from llm import function_dispatcher
from llm.function_schemas import get_function_schemas
from llm.chat_ui import ChatUI  
import os
class ChatWindow:
    def __init__(self, parent):
        self.client = DoubaoClient()
        self.ui = ChatUI(parent,
                         on_send=self._on_send,
                         on_clear=self._clear_messages,
                         on_settings=self._open_settings,
                         on_entry_return=self._on_entry_return,
                         on_shift_enter=self._on_shift_enter)
        self.win = self.ui.win
        self.canvas = self.ui.canvas
        self.messages_frame = self.ui.messages_frame
        self.entry = self.ui.entry
        self.send_btn = self.ui.send_btn
        self._streaming = False
    def _on_send(self):
        if self._streaming:
            return
        user_text = self.entry.get("1.0", END).strip()
        self._last_user_text = user_text
        self.entry.delete("1.0", END)
        self.ui.add_message_bubble("你", user_text, align="left")
        assistant_var, assistant_lbl, _ = self.ui.add_message_bubble("豆包", "", align="right")
        self.win.after(60, lambda: self.canvas.yview_moveto(1.0))
        self.send_btn.config(state='disabled', bg="#84BFAA")
        self._streaming = True
        threading.Thread(target=self._worker_handle_function_call, args=(user_text, assistant_var), daemon=True).start()

    def _open_settings(self):
        cur = getattr(self.client, "timeout", None)
        val = tk.simpledialog.askstring("设置", f"当前 read 超时: {cur}\n输入秒数或 None（不限制）:", parent=self.win)
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

    def _clear_messages(self):
        self.ui.clear_messages()

    def _on_entry_return(self, event):
        if event.state & 0x0001:  # Shift pressed
            return
        if str(self.send_btn['state']) == 'disabled':
            return "break"
        self._on_send()
        return "break"

    def _on_shift_enter(self, event):
        self.entry.insert("insert", "\n")
        self.entry.see("insert")
        return "break"

    def _extract_message_object(self, resp):
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

    def _worker_handle_function_call(self, user_text: str, assistant_var):
        try:
            functions = get_function_schemas("all")
            system_msg = ("系统指令：你**必须**只输出一个单独的 JSON 对象，不能包含任何多余的自然语言。"
                          "格式：{\"name\":\"FUNCTION_NAME\",\"arguments\":{...}}。")
            examples = "示例: 用户: 将1压入栈 -> {\"name\":\"stack_push\",\"arguments\":{\"value\":1}}"
            messages = [
                {"role":"system", "content": system_msg},
                {"role":"user", "content": examples + "\n用户输入:\n" + user_text}
            ]
            resp = self.client.send_message_with_functions(
                messages=messages,
                functions=functions,
                temperature=0.0,
                timeout_read=None
            )
            msg = self._extract_message_object(resp)
            if msg is None:
                if isinstance(resp, dict) and 'text' in resp:
                    msg = {'type': 'assistant_text', 'text': resp.get('text', '')}
                else:
                    self.win.after(0, lambda: assistant_var.set("（模型回复无法解析；未触发可视化）"))
                    return
            if msg.get('type') == 'function_call':
                name = msg.get('name')
                args = msg.get('arguments') or {}
                self.win.after(0, lambda: assistant_var.set(f"[函数调用] {name} -> {args}"))
                result = function_dispatcher.dispatch(name, args)
                res_msg = result.get('message') if isinstance(result, dict) else str(result)
                self.win.after(0, lambda: assistant_var.set(assistant_var.get() + f"\n\n执行结果: {res_msg}"))
                return
            if msg.get('type') == 'assistant_text':
                text = msg.get('text', '') or ''
                self.win.after(0, lambda: assistant_var.set(text))
                m = re.search(r"<\|FunctionCallBegin\|\>(.*?)<\|FunctionCallEnd\|>", text, re.S)
                if m:
                    payload = m.group(1).strip()
                    parsed_obj = None
                    parsed_obj = json.loads(payload)
                    if isinstance(parsed_obj, dict) and 'name' in parsed_obj:
                        name = parsed_obj.get('name')
                        params = parsed_obj.get('parameters') or parsed_obj.get('arguments') or {}
                        self.win.after(0, lambda: assistant_var.set(assistant_var.get() + f"\n\n[函数调用] {name} -> {params}"))
                        result = function_dispatcher.dispatch(name, params)
                        res_msg = result.get('message') if isinstance(result, dict) else str(result)
                        self.win.after(0, lambda: assistant_var.set(assistant_var.get() + f"\n\n执行结果: {res_msg}"))
                        return

                json_m = re.search(r"(\{.*\"name\".*\})", text, re.S)
                if json_m:
                    payload = json_m.group(1)
                    obj = json.loads(payload)
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

            self.win.after(0, lambda: assistant_var.set("（未识别模型输出类型；未触发可视化）"))
            return
        except Exception as e:
            print("worker error:", e)
            self.win.after(0, lambda: assistant_var.set(assistant_var.get() + f"\n\n注: 调用失败"))
        finally:
            self.win.after(0, self._finish_stream)
    def _finish_stream(self):
        self._streaming = False
        self.ui.finish_stream()
