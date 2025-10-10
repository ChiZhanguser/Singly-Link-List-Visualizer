from . import linkedlist_dsl
from . import stack_dsl
from . import sequence_dsl
from . import bst_dsl

def process_command(visualizer, text):
    if not visualizer or not text or not text.strip():
        return
    try:
        if hasattr(visualizer, "node_value_store") or "linked" in type(visualizer).__name__.lower() or "link" in type(visualizer).__name__.lower():
            return linkedlist_dsl.process(visualizer, text)
    except Exception:
        pass
    try:
        if "stack" in type(visualizer).__name__.lower():
            return stack_dsl.process(visualizer, text)
    except Exception:
        pass
    try:
        if "sequence" in type(visualizer).__name__.lower():
            return sequence_dsl.process(visualizer, text)
    except Exception:
        pass
    try:
        if "bst" in type(visualizer).__name__.lower():
            return bst_dsl.process(visualizer, text)
    except Exception:
        pass
    
    from tkinter import messagebox
    messagebox.showinfo("未识别可视化类型", "当前 DSL 只支持单链表（linked list）的命令。")
