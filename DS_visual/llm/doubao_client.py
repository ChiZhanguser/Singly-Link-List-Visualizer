import os
import json
import requests
from typing import Any, Generator, Optional, List, Dict, Union

class DoubaoClient:
    def __init__(self, api_key: str = None, api_base: str = None, model: str = None, timeout: int = 60):
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
            "function_call": "auto",
        }
        if functions:
            payload["functions"] = functions
        if temperature is not None:
            payload["temperature"] = float(temperature)

        resp_json = self._post(payload, timeout_read)

        try:
            if isinstance(resp_json, dict) and "choices" in resp_json and resp_json["choices"]:
                first = resp_json["choices"][0]
                message = first.get("message") or {}
                fc = message.get("function_call")
                if fc and isinstance(fc, dict):
                    name = fc.get("name")
                    args_raw = fc.get("arguments")
                    if isinstance(args_raw, str):
                        try:
                            args = json.loads(args_raw)
                        except Exception:
                            args = args_raw
                    else:
                        args = args_raw
                    return {"type": "function_call", "name": name, "arguments": args}

                content = ""
                if isinstance(message, dict) and "content" in message and message.get("content"):
                    content = message.get("content")

                if content:
                    stripped = content.strip()
                    return {"type": "assistant_text", "text": content}

                if "text" in first and first["text"]:
                    return {"type": "assistant_text", "text": first["text"]}

        except Exception:
            pass
        return {"type": "assistant_text", "text": json.dumps(resp_json, ensure_ascii=False)[:2000]}

    def send_message(self, text: str, messages: Optional[List[Dict[str, Any]]] = None, temperature: Optional[float] = None) -> str:
        if messages and isinstance(messages, list):
            msgs = messages
        else:
            msgs = [
                {"role":"system", "content":"你是一个帮助用户学习数据结构的人，你的任务是根据用户的问题，判断用户是否了解数据结构的相关知识。"},
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
