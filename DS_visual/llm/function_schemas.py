# llm/function_schemas.py
"""
Function schemas for LLM function-calling.
Provides STACK_FUNCTIONS and a convenience getter get_function_schemas()
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
        "description": "清空栈（立即把栈变为空）。示例：用户: 清空栈 -> 返回 function_call: {\"name\":\"stack_clear\",\"arguments\":{}}",
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

# 如果未来需要扩展到更多数据结构，可以把它们加入到这个模块，然后在 get_function_schemas 中选择性返回。
# 例如： LINKED_LIST_FUNCTIONS = [...] ， QUEUE_FUNCTIONS = [...] 等。

def get_function_schemas(kind: str = "stack"):
    """
    返回 function schema 列表，默认返回栈的 schema。
    参数 kind 可以是 "stack" / "all" / 未来扩展的其他结构名。
    """
    if kind == "stack":
        return STACK_FUNCTIONS
    elif kind == "all":
        # 目前只有 stack；后续把其他结构合并到这里
        return STACK_FUNCTIONS
    # 未知 kind 时默认返回 stack（保持向后兼容）
    return STACK_FUNCTIONS
