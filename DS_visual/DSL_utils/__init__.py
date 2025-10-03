# DSL_utils/__init__.py
# 总入口：根据第一个命令词分发到不同的数据结构处理器
from . import stack_dsl

DISPATCH = {
    "stack": stack_dsl,
    "s": stack_dsl,   # 简写
}

def process_command(visualizer, text):
    """
    统一入口：把 text（如 "push 5"）交给合适的 handler 处理。
    visualizer: 你的 StackVisualizer 实例（或其它 ds 的可视化实例）。
    """
    if not text or not text.strip():
        return
    # 简单识别：优先用 stack handler（这是为向后兼容保留的行为）
    # 如果未来有 queue/linkedlist，可以根据前缀分发，例如 "queue:push 1"
    # 目前直接用 stack 处理（因为用户希望栈独立拆分）
    return stack_dsl.process(visualizer, text)
