# doubao_client.py
import os
import requests
from typing import Any, Dict

class DoubaoClient:
    """
    简单封装：读取环境变量 DOUBAO_API_KEY / DOUBAO_API_BASE / DOUBAO_MODEL，
    提供 send_message(text) -> str 的接口。
    """
    def __init__(self, api_key: str = None, api_base: str = None, model: str = None, timeout: int = 30):
        self.api_key = api_key or os.environ.get("DOUBAO_API_KEY")
        self.api_base = api_base or os.environ.get("DOUBAO_API_BASE")
        self.model = model or os.environ.get("DOUBAO_MODEL", "doubao-seed-1-6-250615")
        self.timeout = timeout
        if not self.api_key:
            # 运行时抛出，调用方可以捕获并显示提示
            raise RuntimeError("环境变量 DOUBAO_API_KEY 未设置")

    def _url(self) -> str:
        # 优先使用完整调用地址
        env_url = os.environ.get("DOUBAO_API_URL")
        if env_url:
            return env_url
        if self.api_base:
            return self.api_base.rstrip("/") + "/api/v3/chat/completions"
        raise RuntimeError("未配置 DOUBAO_API_URL 或 DOUBAO_API_BASE")


    def send_message(self, text: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": text}]
        }
        resp = requests.post(self._url(), headers=headers, json=payload, timeout=self.timeout)
        resp.raise_for_status()
        resp_json = resp.json()
        return self._extract_text(resp_json)

    def _extract_text(self, resp_json: Any) -> str:
        # 尽量兼容多种返回结构
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
                        for k in ("output", "text", "reply"):
                            if k in data:
                                return data[k]
                        if "choices" in data and data["choices"]:
                            c0 = data["choices"][0]
                            if isinstance(c0, dict) and "text" in c0:
                                return c0["text"]
                for k in ("reply", "output", "answer", "text"):
                    if k in resp_json:
                        return resp_json[k]
            return str(resp_json)[:2000]
        except Exception:
            return str(resp_json)[:2000]
