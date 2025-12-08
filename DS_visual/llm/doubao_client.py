import os
import json
import requests
from typing import Any, Generator, Optional, List, Dict, Union
import base64

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


    def send_message(self, text: str, messages: Optional[List[Dict[str, Any]]] = None, 
                     temperature: Optional[float] = None,
                     functions: Optional[List[Dict[str, Any]]] = None,
                     function_call: Optional[Union[str, Dict]] = None) -> Union[str, Dict]:
        """
        发送消息到LLM
        
        Args:
            text: 用户输入文本
            messages: 完整的消息列表
            temperature: 温度参数
            functions: 函数定义列表（用于function calling）
            function_call: 函数调用控制 ("auto", "none", 或指定函数名)
            
        Returns:
            如果启用了functions且LLM返回function_call，返回dict格式：
                {"type": "function_call", "name": "...", "arguments": {...}}
            否则返回字符串（LLM的文本回复）
        """
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
        
        # 添加function calling支持
        if functions:
            payload["functions"] = functions
            if function_call:
                payload["function_call"] = function_call
            else:
                payload["function_call"] = "auto"

        resp_json = self._post(payload, timeout_read=None)
        
        # 如果启用了functions，检查是否返回了function_call
        if functions:
            fc_result = self._extract_function_call(resp_json)
            if fc_result:
                return fc_result
        
        return self._extract_text(resp_json)
    
    def _extract_function_call(self, resp_json: Any) -> Optional[Dict]:
        """从响应中提取function_call信息"""
        try:
            if isinstance(resp_json, dict) and "choices" in resp_json:
                choices = resp_json["choices"]
                if choices and isinstance(choices, list):
                    first = choices[0]
                    if isinstance(first, dict):
                        message = first.get("message", {})
                        if isinstance(message, dict):
                            fc = message.get("function_call")
                            if fc and isinstance(fc, dict):
                                name = fc.get("name", "")
                                arguments = fc.get("arguments", "{}")
                                # 尝试解析arguments为dict
                                if isinstance(arguments, str):
                                    try:
                                        arguments = json.loads(arguments)
                                    except:
                                        pass
                                return {
                                    "type": "function_call",
                                    "name": name,
                                    "arguments": arguments
                                }
        except Exception as e:
            print(f"解析function_call出错: {e}")
        return None

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
    def send_multimodal_message(self, text: str, image_path: str = None, temperature: Optional[float] = None) -> str:
        """支持图片和文本的多模态消息发送"""
        messages = []
        
        # 构建消息内容
        content = []
        
        # 添加文本部分
        if text:
            content.append({
                "type": "text",
                "text": text
            })
        
        # 添加图片部分
        if image_path and os.path.exists(image_path):
            try:
                # 读取并编码图片
                with open(image_path, "rb") as image_file:
                    base64_image = base64.b64encode(image_file.read()).decode('utf-8')
                
                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                })
            except Exception as e:
                print(f"图片处理错误: {e}")
                # 如果图片处理失败，只发送文本
                if not text:
                    content.append({
                        "type": "text",
                        "text": "图片处理失败，请描述数据结构"
                    })
        
        if not content:
            raise ValueError("必须提供文本或图片内容")
            
        messages.append({
            "role": "user",
            "content": content
        })
        
        payload = {
            "model": self.model,
            "messages": messages
        }
        
        if temperature is not None:
            payload["temperature"] = float(temperature)

        resp_json = self._post(payload, timeout_read=None)
        return self._extract_text(resp_json)
