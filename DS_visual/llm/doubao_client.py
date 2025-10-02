# llm/doubao_client.py
import os
import json
import requests
from typing import Any, Generator, Optional, List, Dict, Union

class DoubaoClient:
    def __init__(self, api_key: str = None, api_base: str = None, model: str = None, timeout: int = 60):
        # 优先使用传入参数，其次使用环境变量（不要把真实 key 提交到仓库）
        self.model = model or os.environ.get("DOUBAO_MODEL", "doubao-seed-1-6-250615")
        self.api_key = api_key or os.environ.get("DOUBAO_API_KEY") or "3a7533ff-aefd-4915-aa7c-80311e7d51a4"
        self.api_url = os.environ.get("DOUBAO_API_URL") or "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
        self.api_base = api_base or os.environ.get("DOUBAO_API_BASE") or "https://ep-m-20250701075921-h2z47"

        tv = os.environ.get("DOUBAO_TIMEOUT", "")
        if isinstance(tv, str) and tv.lower() == "none":
            self.timeout = None
        else:
            try:
                self.timeout = int(tv) if tv else timeout
            except Exception:
                self.timeout = timeout

        if not self.api_key:
            raise RuntimeError("环境变量 DOUBAO_API_KEY 未设置")

    def _url(self) -> str:
        # 优先使用 explicit api_url，如果没有再拼 api_base
        if self.api_url:
            return self.api_url
        if self.api_base:
            return self.api_base.rstrip("/") + "/api/v3/chat/completions"
        raise RuntimeError("未配置 DOUBAO_API_URL 或 DOUBAO_API_BASE")

    def _post(self, payload: dict, timeout_read: Optional[int]) -> dict:
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        url = self._url()
        read_t = timeout_read if timeout_read is not None else self.timeout
        timeout_tuple = (10, read_t)
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=timeout_tuple)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"请求失败: {e}")

    def send_message_with_functions(
        self,
        text: Optional[str] = None,
        messages: Optional[List[Dict[str, Any]]] = None,
        functions: Optional[List[Dict[str, Any]]] = None,
        temperature: Optional[float] = 0.0,
        timeout_read: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        发送非流式消息，支持 function-calling。

        参数：
          - text: 兼容旧 API，如果 messages 未提供，会把 text 放到 user 内容里。
          - messages: 完整 messages 列表（role: system/user/...），优先使用。
          - functions: 可选函数 schema 列表，会被包含到请求体中。
          - temperature: 控制随机性，建议在调用时传 0。
          - timeout_read: 可选读超时覆盖实例 timeout。

        返回：
            {"type": "function_call", "name": ..., "arguments": ...}
            或 {"type": "assistant_text", "text": "..."}
        """
        # 构造 messages：优先使用调用方传入的 messages，否则用默认 system + user(text)
        if messages and isinstance(messages, list):
            msgs = messages
        else:
            system_content = (
                "你是一个监督用户学习数据结构的人，你的任务是根据用户的问题，判断用户是否了解数据结构的相关知识。"
                "必要时，请使用已提供的函数（function calling）来触发前端演示。"
            )
            user_content = text or ""
            msgs = [
                {"role": "system", "content": system_content},
                {"role": "user", "content": user_content}
            ]

        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": msgs,
            # 如果需要 function calling，请设置 function_call 与 functions
            # "function_call": "auto" 表示模型可以自由选择
            "function_call": "auto",
            # temperature 可为 None 保持默认；但这里如果传了数值就设置
        }
        if functions:
            payload["functions"] = functions
        if temperature is not None:
            # API 字段名通常是 temperature
            payload["temperature"] = float(temperature)

        resp_json = self._post(payload, timeout_read)

        # --- 解析返回 --- 
        # 兼容多种 provider：优先查 choices[0].message
        try:
            if isinstance(resp_json, dict) and "choices" in resp_json and resp_json["choices"]:
                first = resp_json["choices"][0]
                message = first.get("message") or {}

                # 1) function_call （首选）
                fc = message.get("function_call")
                if fc and isinstance(fc, dict):
                    name = fc.get("name")
                    args_raw = fc.get("arguments")
                    # arguments 有时是 JSON 字符串
                    if isinstance(args_raw, str):
                        try:
                            args = json.loads(args_raw)
                        except Exception:
                            args = args_raw
                    else:
                        args = args_raw
                    return {"type": "function_call", "name": name, "arguments": args}

                # 2) content 字段（assistant 普通回复，可能是 JSON 文本）
                content = ""
                if isinstance(message, dict) and "content" in message and message.get("content"):
                    content = message.get("content")

                if content:
                    # 如果 content 是 JSON 文本（例如模型直接输出 {"name":...}），尽力解析成 dict 并返回为 assistant_text（调用方可再解析）
                    stripped = content.strip()
                    # 如果整个 content 看起来像单个 JSON object，就直接把文本返回（调用方会再 parse）
                    return {"type": "assistant_text", "text": content}

                # 3) some providers put text at first['text']
                if "text" in first and first["text"]:
                    return {"type": "assistant_text", "text": first["text"]}

        except Exception:
            # 忽略解析异常，走下面的兜底
            pass

        # 兜底：返回原始 JSON（截断以避免超长）
        return {"type": "assistant_text", "text": json.dumps(resp_json, ensure_ascii=False)[:2000]}

    def send_message(self, text: str, messages: Optional[List[Dict[str, Any]]] = None, temperature: Optional[float] = None) -> str:
        """
        简单非函数调用版本的发送（向后兼容）。如果传 messages 则优先使用。
        """
        if messages and isinstance(messages, list):
            msgs = messages
        else:
            msgs = [
                {"role":"system", "content":"你是一个监督用户学习数据结构的人，你的任务是根据用户的问题，判断用户是否了解数据结构的相关知识。"},
                {"role":"user","content": text}
            ]
        payload = {
            "model": self.model,
            "messages": msgs
        }
        if temperature is not None:
            payload["temperature"] = float(temperature)

        resp_json = self._post(payload, timeout_read=None)
        return self._extract_text(resp_json)

    def _extract_text(self, resp_json: Any) -> str:
        try:
            if isinstance(resp_json, dict):
                if "choices" in resp_json and resp_json["choices"]:
                    first = resp_json["choices"][0]
                    if isinstance(first, dict):
                        m = first.get("message")
                        if isinstance(m, dict) and "content" in m:
                            return m["content"]
                        if "text" in first:
                            return first["text"]
                if "data" in resp_json:
                    data = resp_json["data"]
                    if isinstance(data, str):
                        return data
                    if isinstance(data, dict):
                        for k in ("output","text","reply"):
                            if k in data:
                                return data[k]
                        if "choices" in data and data["choices"]:
                            c0 = data["choices"][0]
                            if isinstance(c0, dict) and "text" in c0:
                                return c0["text"]
                for k in ("reply","output","answer","text"):
                    if k in resp_json:
                        return resp_json[k]
            return str(resp_json)[:2000]
        except Exception:
            return str(resp_json)[:2000]
