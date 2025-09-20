# llm/doubao_client.py
import os
import json
import requests
from typing import Any, Generator, Optional

class DoubaoClient:
    def __init__(self, api_key: str = None, api_base: str = None, model: str = None, timeout: int = 60):
        # self.api_key = api_key or os.environ.get("DOUBAO_API_KEY")
        self.api_key = "3a7533ff-aefd-4915-aa7c-80311e7d51a4"
        # self.api_url = os.environ.get("DOUBAO_API_URL")
        self.api_url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
        # self.api_base = api_base or os.environ.get("DOUBAO_API_BASE")
        self.api_base = "https://ep-m-20250701075921-h2z47"
        self.model = model or os.environ.get("DOUBAO_MODEL", "doubao-seed-1-6-250615")
        # read 超时：如果环境变量为 "None"（不区分大小写），表示不限制 read 超时（用于流式）
        tv = os.environ.get("DOUBAO_TIMEOUT", "")
        if tv.lower() == "none":
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

    def send_message(self, text: str) -> str:
        """一次性请求（原行为）"""
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {"model": self.model, "messages": [{"role":"user","content": text}]}
        resp = requests.post(self._url(), headers=headers, json=payload, timeout=(10, self.timeout))
        resp.raise_for_status()
        resp_json = resp.json()
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

    # ---------- 流式接口 ----------
    def send_message_stream(self, text: str, stream: bool = True, timeout_read: Optional[int] = None) -> Generator[str, None, None]:
        """
        流式请求生成器：每次 yield 一个文本片段（字符串）。
        若服务端不支持流式，上游会返回一次性响应并触发 HTTP 200；此时函数会尝试解析并 yield 完整回复（回退）。
        参数:
            text: 用户输入文本
            stream: 是否告诉服务端返回流（默认 True）
            timeout_read: read 超时（秒），传 None 表示使用 self.timeout（None 表示不限制）
        """
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {"model": self.model, "messages": [{"role":"user","content": text}], "stream": stream}
        url = self._url()

        # 连接超时固定短些（10s），read 超时可配置
        read_t = timeout_read if timeout_read is not None else self.timeout
        timeout_tuple = (10, read_t)

        try:
            resp = requests.post(url, headers=headers, json=payload, stream=True, timeout=timeout_tuple)
        except Exception as e:
            raise RuntimeError(f"请求失败: {e}")

        if resp.status_code != 200:
            # 非流式或错误：读取 body 并抛错（或回退）
            text_body = resp.text
            raise RuntimeError(f"HTTP {resp.status_code}: {text_body[:2000]}")

        def _try_decode(possible):
            """
            修复常见的 latin1 -> utf-8 的 mojibake（把被错误解码的字符串恢复成 utf-8）。
            如果不是字符串或解码失败，返回原始字符串。
            """
            if not isinstance(possible, str):
                return ""
            try:
                return possible.encode("latin1").decode("utf-8")
            except Exception:
                return possible

        try:
            # 逐行读取 chunk（SSE 或 chunked JSON）
            for raw_line in resp.iter_lines(decode_unicode=True):
                if raw_line is None:
                    continue
                line = raw_line.strip()
                if not line:
                    continue
                # 可能的形式： "data: {...}" 或 纯 JSON 行
                if line.startswith("data:"):
                    payload_text = line[len("data:"):].strip()
                    if payload_text == "[DONE]":
                        break
                    try:
                        j = json.loads(payload_text)
                    except Exception:
                        # 不是 JSON，直接返回原始文本（并尝试修复编码）
                        yield _try_decode(payload_text)
                        continue
                else:
                    try:
                        j = json.loads(line)
                    except Exception:
                        yield _try_decode(line)
                        continue

                # ----- 尝试从 j 中提取增量文本 -----
                text_piece = ""

                try:
                    choices = j.get("choices") or []
                    if choices:
                        first = choices[0]
                        delta = first.get("delta") or {}
                        # 优先取 delta.content
                        if isinstance(delta, dict) and "content" in delta:
                            text_piece += _try_decode(delta.get("content") if isinstance(delta.get("content"), str) else str(delta.get("content")))
                        # 兼容 reasoning_content（部分实现会返回）
                        if isinstance(delta, dict) and "reasoning_content" in delta:
                            text_piece += _try_decode(delta.get("reasoning_content"))
                        # message 里也可能有 content / reasoning_content
                        msg = first.get("message") or {}
                        if isinstance(msg, dict):
                            if "content" in msg:
                                c = msg["content"]
                                if isinstance(c, str):
                                    text_piece += _try_decode(c)
                                else:
                                    text_piece += json.dumps(c, ensure_ascii=False)
                            if "reasoning_content" in msg:
                                text_piece += _try_decode(msg["reasoning_content"])
                        # 旧接口可能用 text
                        if not text_piece and "text" in first:
                            text_piece = _try_decode(first.get("text",""))
                except Exception:
                    text_piece = ""

                # 另一些实现把文本放在 data 下
                if not text_piece:
                    data = j.get("data")
                    if isinstance(data, dict):
                        for k in ("output","text","reply"):
                            if k in data:
                                v = data[k]
                                text_piece = v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)
                                break

                if text_piece:
                    yield text_piece
                else:
                    # 没找到文本字段，跳过
                    continue

            return
        finally:
            try:
                resp.close()
            except Exception:
                pass
