# llm/function_schemas.py
# 函数 schema 列表，供 DoubaoClient.send_message_with_functions 传给模型
from typing import List, Dict, Any

def get_function_schemas() -> List[Dict[str, Any]]:
    """
    返回可被大模型调用的函数定义（JSON Schema 风格）。
    根据需要在这里增加/修改函数。
    """
    return [
        {
            "name": "linked_list_insert_last",
            "description": "向当前打开的单链表可视化界面在尾部插入一个节点（演示动画）",
            "parameters": {
                "type": "object",
                "properties": {
                    "value": {"type": "string", "description": "要插入的节点值（字符串形式）"}
                },
                "required": ["value"]
            }
        },
        {
            "name": "linked_list_insert_first",
            "description": "向当前打开的单链表可视化界面在头部插入一个节点（演示动画）",
            "parameters": {
                "type": "object",
                "properties": {
                    "value": {"type": "string"}
                },
                "required": ["value"]
            }
        },
        {
            "name": "linked_list_delete_first",
            "description": "删除单链表的第一个节点（演示动画）",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        },
        {
            "name": "linked_list_delete_last",
            "description": "删除单链表的最后一个节点（演示动画）",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        },
        {
            "name": "linked_list_create",
            "description": "批量创建单链表（按顺序插入多个值并演示）。",
            "parameters": {
                "type": "object",
                "properties": {
                    "values": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "顺序插入的值数组"
                    }
                },
                "required": ["values"]
            }
        },
        {
            "name": "stack_push",
            "description": "向当前打开的栈可视化界面 push 一个元素（演示动画）",
            "parameters": {
                "type": "object",
                "properties": {
                    "value": {"type": "string"}
                },
                "required": ["value"]
            }
        },
        {
            "name": "stack_pop",
            "description": "向当前打开的栈可视化界面 pop（演示动画）",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    ]
