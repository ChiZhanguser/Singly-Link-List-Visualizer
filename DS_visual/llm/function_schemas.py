# llm/function_schemas.py
"""
Function schemas for LLM function-calling.
Provides STACK_FUNCTIONS, SEQUENCE_FUNCTIONS and a convenience getter get_function_schemas()
so other modules (e.g. chat_window) can import get_function_schemas().
"""

STACK_FUNCTIONS = [
    {
        "name": "stack_push",
        "description": "将一个值入栈并触发可视化动画。参数 value 可以是字符串或数字。",
        "parameters": {
            "type": "object",
            "properties": {
                "value": {"type": ["string", "number"], "description": "要入栈的值"}
            },
            "required": ["value"]
        }
    },
    {
        "name": "stack_pop",
        "description": "出栈（从栈顶移除一个元素），触发可视化动画。无参数。",
        "parameters": {"type": "object", "properties": {}}
    },
    {
        "name": "stack_clear",
        "description": "清空栈（立即把栈变为空）。",
        "parameters": {"type": "object", "properties": {}}
    },
    {
        "name": "stack_batch_create",
        "description": "批量创建栈元素并演示插入动画。参数 values 是一个数组或逗号分隔的字符串。",
        "parameters": {
            "type": "object",
            "properties": {
                "values": {
                    "type": ["array", "string"],
                    "items": {"type": ["string", "number"]},
                    "description": "要按顺序入栈的元素列表，或逗号分隔字符串"
                }
            },
            "required": ["values"]
        }
    },
    {
        "name": "stack_get_state",
        "description": "获取当前栈的内容（用于模型确认或展示）。",
        "parameters": {"type": "object", "properties": {}}
    }
]

SEQUENCE_FUNCTIONS = [
    {
        "name": "sequence_insert_first",
        "description": "在顺序表头部插入元素。参数 value 可为字符串或数字。",
        "parameters": {
            "type": "object",
            "properties": {
                "value": {"type": ["string", "number"], "description": "插入的值"}
            },
            "required": ["value"]
        }
    },
    {
        "name": "sequence_insert_last",
        "description": "在顺序表尾部插入元素。参数 value 可为字符串或数字。",
        "parameters": {
            "type": "object",
            "properties": {
                "value": {"type": ["string", "number"], "description": "插入的值"}
            },
            "required": ["value"]
        }
    },
    {
        "name": "sequence_insert_at",
        "description": "在指定位置插入元素。位置使用 0-based 索引（或在文档中说明为 1-based）。参数 index (number) 和 value。",
        "parameters": {
            "type": "object",
            "properties": {
                "index": {"type": "number", "description": "要插入的位置（0-based）"},
                "value": {"type": ["string", "number"], "description": "插入的值"}
            },
            "required": ["index", "value"]
        }
    },
    {
        "name": "sequence_delete_at",
        "description": "删除指定位置的元素（0-based 索引）。参数 index。",
        "parameters": {
            "type": "object",
            "properties": {
                "index": {"type": "number", "description": "要删除的位置（0-based）"}
            },
            "required": ["index"]
        }
    },
    {
        "name": "sequence_clear",
        "description": "清空顺序表（删除所有元素）。无参数。",
        "parameters": {"type": "object", "properties": {}}
    },
    {
        "name": "sequence_batch_create",
        "description": "批量创建顺序表元素并演示插入动画。parameters: values 是数组或逗号分隔字符串。",
        "parameters": {
            "type": "object",
            "properties": {
                "values": {
                    "type": ["array", "string"],
                    "items": {"type": ["string", "number"]},
                    "description": "要按顺序插入的元素列表，或逗号分隔字符串"
                }
            },
            "required": ["values"]
        }
    },
    {
        "name": "sequence_get_state",
        "description": "获取当前顺序表的内容（用于模型确认或展示）。",
        "parameters": {"type": "object", "properties": {}}
    }
]

def get_function_schemas(kind: str = "stack"):
    """
    返回 function schema 列表。
    kind:
      - "stack": 仅栈
      - "sequence": 仅顺序表
      - "all": stack + sequence
    """
    if kind == "stack":
        return STACK_FUNCTIONS
    if kind == "sequence":
        return SEQUENCE_FUNCTIONS
    if kind == "all":
        # 合并并返回
        return STACK_FUNCTIONS + SEQUENCE_FUNCTIONS
    # 默认回退为 stack（向后兼容）
    return STACK_FUNCTIONS
