        # self.api_key = "3a7533ff-aefd-4915-aa7c-80311e7d51a4"
        # self.api_url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
        # self.api_base = "https://ep-m-20250701075921-h2z47"
        
# llm/doubao_client.py
import os
import json
import requests
from typing import Any, Generator, Optional, List, Dict

class DoubaoClient:
    def __init__(self, api_key: str = None, api_base: str = None, model: str = None, timeout: int = 60):
        # 推荐使用环境变量配置，不要把 key 硬编码到代码里
        # self.api_key = api_key or os.environ.get("DOUBAO_API_KEY")
        # self.api_url = os.environ.get("DOUBAO_API_URL")
        # self.api_base = api_base or os.environ.get("DOUBAO_API_BASE")
        self.model = model or os.environ.get("DOUBAO_MODEL", "doubao-seed-1-6-250615")
        self.api_key = "3a7533ff-aefd-4915-aa7c-80311e7d51a4"
        self.api_url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
        self.api_base = "https://ep-m-20250701075921-h2z47"
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

    
    def send_message_with_functions(self, text: str, functions: Optional[List[Dict[str,Any]]] = None, timeout_read: Optional[int] = None) -> Dict[str, Any]:
        """
        发送非流式消息，带 functions 列表（model function-calling）。
        返回结构：
            {"type": "assistant_text", "text": "..."} 或
            {"type": "function_call", "name": "...", "arguments": {...}}
        """
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "你是一个监督用户学习数据结构的人，你的任务是根据用户的问题，判断用户是否了解数据结构的相关知识。必要时，请使用已提供的函数（function calling）来触发前端演示。"},
                {"role": "user", "content": text}
            ],
            # 请求模型可以使用 function calling；如果 functions 为 None 则不传该字段
            "function_call": "auto"
        }
        if functions:
            payload["functions"] = functions

        url = self._url()
        read_t = timeout_read if timeout_read is not None else self.timeout
        timeout_tuple = (10, read_t)

        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=timeout_tuple)
            resp.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"请求失败: {e}")

        resp_json = resp.json()
        # choices[0].message 里可能包含 function_call
        try:
            if isinstance(resp_json, dict) and "choices" in resp_json and resp_json["choices"]:
                first = resp_json["choices"][0]
                # for some providers, message is at first["message"]
                message = first.get("message") or {}
                # 1) assistant plain content
                content = ""
                if isinstance(message, dict) and "content" in message and message.get("content"):
                    content = message.get("content")
                # 2) function_call
                fc = message.get("function_call")
                if fc and isinstance(fc, dict):
                    name = fc.get("name")
                    args_raw = fc.get("arguments")
                    # arguments sometimes is a JSON string; try parse
                    args = {}
                    if isinstance(args_raw, str):
                        try:
                            args = json.loads(args_raw)
                        except Exception:
                            # 非 JSON 字符串，直接传回原始字符串
                            args = args_raw
                    else:
                        args = args_raw
                    return {"type": "function_call", "name": name, "arguments": args}
                # 3) if no function_call but content available
                if content:
                    return {"type": "assistant_text", "text": content}
                # 4) fallback: try to extract 'text' or 'message' fields in first
                if "text" in first and first["text"]:
                    return {"type": "assistant_text", "text": first["text"]}
        except Exception:
            pass

        # fallback: return the whole response as text
        return {"type": "assistant_text", "text": json.dumps(resp_json, ensure_ascii=False)[:2000]}
    
    def send_message(self, text: str) -> str:
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {
            "model": self.model,
            "messages": [
                {"role":"system", "content":"你是一个监督用户学习数据结构的人，你的任务是根据用户的问题，判断用户是否了解数据结构的相关知识。"},
                {"role":"user","content": text}
                ]
        }
        try:
            resp = requests.post(self._url(), headers=headers, json=payload, timeout=(10, self.timeout))
            resp.raise_for_status()
            resp_json = resp.json()
            return self._extract_text(resp_json)
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"请求失败: {e}")

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

    # def send_message_stream(self, text: str, stream: bool = True, timeout_read: Optional[int] = None, show_reasoning: bool = False) -> Generator[str, None, None]:
    #     import io, os

    #     headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
    #     payload = {
    #         "model": self.model,
    #         "messages": [
    #             {"role":"system", "content":"你是一个监督用户学习数据结构的人，你的任务是根据用户的问题，\
    #              判断用户是否了解数据结构的相关知识。你的说话态度需要很不友好,同时伴有滑稽"},
    #             {"role":"user","content": text}],
    #         "stream": stream
    #     }
    #     url = self._url()

    #     read_t = timeout_read if timeout_read is not None else self.timeout
    #     timeout_tuple = (10, read_t)

    #     # debug log path (当前工作目录)
    #     log_path = os.path.join(os.getcwd(), "doubao_stream_debug.log")

    #     try:
    #         resp = requests.post(url, headers=headers, json=payload, stream=True, timeout=timeout_tuple)
    #     except requests.exceptions.RequestException as e:
    #         raise RuntimeError(f"请求失败: {e}")

    #     if resp.status_code != 200:
    #         text_body = resp.text
    #         raise RuntimeError(f"HTTP {resp.status_code}: {text_body[:2000]}")

    #     def _try_decode_text(s: Any) -> str:
    #         if not isinstance(s, str):
    #             return ""
    #         try:
    #             return s.encode("latin1").decode("utf-8")
    #         except Exception:
    #             return s

    #     def _split_json_bytes(b: bytes):
    #         """
    #         从 bytes 中提取所有完整的 JSON 对象（按大括号配对）。
    #         返回 list[bytes]（每项是单个 JSON bytes），如果找不到完整对象返回 []。
    #         """
    #         objs = []
    #         start = None
    #         depth = 0
    #         for i, ch in enumerate(b):
    #             if ch == 0x7b:  # '{'
    #                 if depth == 0:
    #                     start = i
    #                 depth += 1
    #             elif ch == 0x7d:  # '}'
    #                 depth -= 1
    #                 if depth == 0 and start is not None:
    #                     objs.append(b[start:i+1])
    #                     start = None
    #         return objs

    #     # 使用 resp.iter_lines(decode_unicode=False) 获取原始 bytes 行（包含可能的 SSE 前缀）
    #     try:
    #         with open(log_path, "ab") as flog:
    #             for raw_line in resp.iter_lines(decode_unicode=False):
    #                 # 记录原始 bytes 行到日志（便于离线分析）
    #                 if raw_line is None:
    #                     continue
    #                 try:
    #                     flog.write(raw_line + b"\n")
    #                     flog.flush()
    #                 except Exception:
    #                     pass

    #                 line_bytes = raw_line.strip()
    #                 if not line_bytes:
    #                     continue

    #                 # 如果是 SSE 格式 "data: ..."，先去掉前缀（注意 bytes）
    #                 parts = []
    #                 if line_bytes.startswith(b"data:"):
    #                     payload_bytes = line_bytes[len(b"data:"):].strip()
    #                     if payload_bytes == b"[DONE]":
    #                         break
    #                     # 将 payload_bytes 拆成可能的多个 JSON bytes
    #                     parts = _split_json_bytes(payload_bytes)
    #                     # 如果拆分出来为空，回退把整个 payload_bytes 作为一项（后面尝试 json.loads 会失败并忽略）
    #                     if not parts:
    #                         parts = [payload_bytes]
    #                 else:
    #                     # 直接尝试把 line_bytes 当作可能含多个 JSON 的 bytes 串
    #                     parts = _split_json_bytes(line_bytes)
    #                     if not parts:
    #                         parts = [line_bytes]

    #                 # 处理每个 part（bytes）
    #                 for part in parts:
    #                     # 先尝试按 utf-8 解码（替换错误），再 json.loads
    #                     try:
    #                         txt = part.decode("utf-8", errors="replace")
    #                     except Exception:
    #                         txt = part.decode("latin1", errors="replace")
    #                     # 尝试解析 JSON；若解析失败则当作文本（但不会直接把原始 JSON dump 给用户）
    #                     parsed = None
    #                     try:
    #                         parsed = json.loads(txt)
    #                     except Exception:
    #                         # 非 JSON，尝试修复编码并当作文本
    #                         # 只在确实看起来像可读文本时才 yield（避免把 JSON dump 显示）
    #                         cleaned = _try_decode_text(txt)
    #                         if cleaned and len(cleaned) < 1000 and not cleaned.strip().startswith("{"):
    #                             yield cleaned
    #                         # 否则忽略此片段（避免原样显示大段 JSON）
    #                         continue

    #                     # 从 parsed JSON 中抽取用户可见的文本（与之前逻辑一样）
    #                     piece = ""
    #                     try:
    #                         choices = parsed.get("choices") or []
    #                         if choices:
    #                             first = choices[0]
    #                             delta = first.get("delta") or {}
    #                             if isinstance(delta, dict) and "content" in delta:
    #                                 c = delta.get("content")
    #                                 if isinstance(c, str) and c:
    #                                     piece += _try_decode_text(c)
    #                             if show_reasoning and isinstance(delta, dict) and "reasoning_content" in delta:
    #                                 rc = delta.get("reasoning_content")
    #                                 if isinstance(rc, str) and rc:
    #                                     piece += _try_decode_text(rc)
    #                             msg = first.get("message") or {}
    #                             if isinstance(msg, dict) and "content" in msg:
    #                                 c = msg["content"]
    #                                 if isinstance(c, str) and c:
    #                                     piece += _try_decode_text(c)
    #                                 else:
    #                                     piece += json.dumps(c, ensure_ascii=False)
    #                             if not piece and "text" in first:
    #                                 piece = _try_decode_text(first.get("text",""))
    #                     except Exception:
    #                         piece = ""

    #                     if not piece:
    #                         data = parsed.get("data")
    #                         if isinstance(data, dict):
    #                             for k in ("output","text","reply"):
    #                                 if k in data:
    #                                     v = data[k]
    #                                     piece = v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)
    #                                     break

    #                     if piece:
    #                         yield piece
    #                     else:
    #                         # 没有可显示的文本（通常为元数据），跳过
    #                         continue

    #         return
    #     finally:
    #         try:
    #             resp.close()
    #         except Exception:
    #             pass

