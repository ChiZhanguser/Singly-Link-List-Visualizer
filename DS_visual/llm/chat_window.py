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
        self.send_btn_canvas = self.ui.send_btn_canvas
        self._streaming = False
    
    def _on_send(self):
        if self._streaming:
            return
        user_text = self.entry.get("1.0", END).strip()
        if not user_text or user_text == "输入消息... (Shift+Enter 换行)":
            return
        
        self._last_user_text = user_text
        self.entry.delete("1.0", END)
        
        # 重置占位符状态
        self.ui._entry_placeholder = True
        self.entry.insert("1.0", "输入消息... (Shift+Enter 换行)")
        self.entry.config(fg="#A0AEC0")
        
        self.ui.add_message_bubble("你", user_text, align="left")
        assistant_var, assistant_lbl, _ = self.ui.add_message_bubble("豆包", "", align="right")
        self.win.after(60, lambda: self.canvas.yview_moveto(1.0))
        
        # 禁用发送按钮
        self.ui._send_btn_disabled = True
        self.ui._draw_gradient_button(self.send_btn_canvas, "发送 ✈️", "disabled")
        
        self._streaming = True
        threading.Thread(target=self._worker_handle_function_call, args=(user_text, assistant_var), daemon=True).start()

    def _open_settings(self):
        cur = getattr(self.client, "timeout", None)
        val = tk.simpledialog.askstring("设置", f"当前 read 超时: {cur}\n输入秒数或 None(不限制):", parent=self.win)
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
        if self._streaming or self.ui._send_btn_disabled:
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
            # 获取当前数据结构类型对应的函数schemas
            # 默认获取栈相关的函数（可以根据上下文动态调整）
            functions = get_function_schemas("stack")
            
            system_prompt = """你是一个帮助用户学习数据结构的AI助手。你可以通过调用函数来演示各种栈的应用：

1. **后缀表达式求值** (stack_eval_postfix): 当用户想要演示后缀表达式（逆波兰表达式）的求值过程时调用
   - 例如用户说"演示后缀表达式 3 4 + 2 *"，应调用 stack_eval_postfix(expression="3 4 + 2 *")
   
2. **括号匹配检验** (stack_bracket_match): 当用户想要检验括号是否匹配时调用
   - 例如用户说"检验{a+(b-c)*2}的括号"，应调用 stack_bracket_match(expression="{a+(b-c)*2}")

3. **DFS深度优先搜索** (stack_dfs): 当用户想要演示DFS遍历时调用
   - 例如用户说"演示DFS"，应调用 stack_dfs()

4. **栈的基本操作**: stack_push, stack_pop, stack_clear, stack_batch_create, stack_get_state

请根据用户的请求，判断是否需要调用函数。如果需要，直接调用对应函数；如果只是普通问答，直接回复即可。"""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text}
            ]
            
            response = self.client.send_message(
                text=user_text,
                messages=messages,
                temperature=0.0,
                functions=functions,
                function_call="auto"
            )
            
            # 检查是否是function_call响应
            if isinstance(response, dict) and response.get("type") == "function_call":
                func_name = response.get("name", "")
                func_args = response.get("arguments", {})
                
                print(f"LLM调用函数: {func_name}, 参数: {func_args}")
                
                # 执行函数调用
                result = function_dispatcher.dispatch(func_name, func_args)
                
                # 根据结果构建回复
                if result.get("ok"):
                    response_text = f"✅ 正在执行: {result.get('message', func_name)}"
                else:
                    response_text = f"❌ 执行失败: {result.get('error', '未知错误')}"
                
                self.win.after(0, lambda t=response_text: assistant_var.set(t))
            else:
                # 普通文本回复
                self.win.after(0, lambda t=response: assistant_var.set(t))
                
        except Exception as e:
            print("worker error:", e)
            import traceback
            traceback.print_exc()
            self.win.after(0, lambda: assistant_var.set(assistant_var.get() + f"\n\n注: 调用失败: {str(e)}"))
        finally:
            self.win.after(0, self._finish_stream) 
            
    def _finish_stream(self):
        self._streaming = False
        self.ui.finish_stream()