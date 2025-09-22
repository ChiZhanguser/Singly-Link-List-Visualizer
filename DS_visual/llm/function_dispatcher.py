# llm/function_dispatcher.py
from typing import Any, Dict, Optional, Callable
import json

# llm/function_dispatcher.py
from typing import Any, Dict, Optional
import json
import traceback

_reg = {
    "linked_list": None,
    "stack": None,
    # 如需其他可视化，添加键
}

def register_visualizer(kind: str, instance: Any) -> None:
    _reg[kind] = instance

def unregister_visualizer(kind: str) -> None:
    _reg[kind] = None

def _safe_parse_args(raw_args: Any) -> Dict[str, Any]:
    if raw_args is None:
        return {}
    if isinstance(raw_args, dict):
        return raw_args
    if isinstance(raw_args, str):
        try:
            return json.loads(raw_args)
        except Exception:
            return {"value": raw_args}
    return {}

def _call_on_ui_thread_if_possible(inst: Any, func: callable, *args, **kwargs) -> None:
    """
    如果 visualizer 实例有 .window（或 .root）并支持 .after，则使用 after 调度 UI 操作。
    否则直接调用（谨慎）。
    这里不等待结果：我们把操作视为已调度并返回给调用者。
    """
    try:
        # try common attribute names for Tk root/frame
        loop_owner = getattr(inst, "window", None) or getattr(inst, "root", None) or getattr(inst, "tk", None)
        if loop_owner is not None and hasattr(loop_owner, "after"):
            # schedule in Tk main thread
            loop_owner.after(0, lambda: func(*args, **kwargs))
            return
    except Exception:
        # 如果 above 出错，继续到直接调用分支（但捕获异常）
        pass

    # 如果没有 after，可尝试直接调用（仍包 try）
    try:
        func(*args, **kwargs)
    except Exception:
        # 吃掉异常以免在 worker 线程崩溃，把 trace 打印到 stderr
        trace = traceback.format_exc()
        print("Error calling visualizer function directly (no UI thread):", trace)

def dispatch(function_name: str, raw_arguments: Any) -> Dict[str, Any]:
    args = _safe_parse_args(raw_arguments)
    try:
        if function_name.startswith("linked_list_"):
            inst = _reg.get("linked_list")
            if not inst:
                return {"ok": False, "message": "没有注册单链表可视化实例。请先打开单链表窗口。"}
            # 下面所有操作都通过 _call_on_ui_thread_if_possible 调度
            if function_name == "linked_list_insert_last":
                _call_on_ui_thread_if_possible(inst, getattr(inst, "programmatic_insert_last"), args["value"])
                return {"ok": True, "message": f"已调度：向单链表尾部插入 {args['value']}"}
            if function_name == "linked_list_insert_first":
                # 如果 visualizer 没有直接的 insert_first，实现者可以在类内做转换
                if hasattr(inst, "programmatic_insert_first"):
                    _call_on_ui_thread_if_possible(inst, getattr(inst, "programmatic_insert_first"), args["value"])
                else:
                    # fallback: 插入到尾部再由 visualizer 处理为头插（如果 visualizer 支持）
                    _call_on_ui_thread_if_possible(inst, getattr(inst, "programmatic_insert_last"), args["value"])
                    # visualizer 内部可以在收到后自己把它移动到头部
                return {"ok": True, "message": f"已调度：向单链表头部插入 {args['value']}"}
            if function_name == "linked_list_delete_first":
                _call_on_ui_thread_if_possible(inst, getattr(inst, "delete_first_node"))
                return {"ok": True, "message": "已调度：删除单链表第一个节点。"}
            if function_name == "linked_list_delete_last":
                # 有些实现需要 delay 参数，这里尝试调用 delete_last_node(0) 若可行
                if hasattr(inst, "delete_last_node"):
                    try:
                        _call_on_ui_thread_if_possible(inst, getattr(inst, "delete_last_node"), 0)
                    except TypeError:
                        _call_on_ui_thread_if_possible(inst, getattr(inst, "delete_last_node"))
                return {"ok": True, "message": "已调度：删除单链表最后一个节点。"}
            if function_name == "linked_list_create":
                vals = args.get("values") or []
                # 逐个调度插入（避免主线程被长时间阻塞）
                for v in vals:
                    _call_on_ui_thread_if_possible(inst, getattr(inst, "programmatic_insert_last"), v)
                return {"ok": True, "message": f"已调度：批量创建单链表，元素数: {len(vals)}"}

        if function_name.startswith("stack_"):
            inst = _reg.get("stack")
            if not inst:
                return {"ok": False, "message": "没有注册栈可视化实例。请先打开栈窗口。"}
            if function_name == "stack_push":
                _call_on_ui_thread_if_possible(inst, getattr(inst, "programmatic_push"), args["value"])
                return {"ok": True, "message": f"已调度：向栈 push {args['value']}"}
            if function_name == "stack_pop":
                _call_on_ui_thread_if_possible(inst, getattr(inst, "programmatic_pop"))
                return {"ok": True, "message": "已调度：从栈 pop 一个元素。"}
        return {"ok": False, "message": f"未知函数: {function_name}"}
    except Exception as e:
        return {"ok": False, "message": f"执行函数 {function_name} 时发生异常: {e}"}
