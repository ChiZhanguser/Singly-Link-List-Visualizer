# llm/function_dispatcher.py
from typing import Any, Dict, Optional
import json
import traceback

# registry for visualizer instances
_reg = {
    "linked_list": None,
    "stack": None,
    # extend as needed
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

def _call_on_ui_thread_if_possible(inst, fn, *args, **kwargs):
    """
    If the visualizer instance has a 'window' (Tk or Toplevel) with .after,
    schedule the fn to run on that UI thread; otherwise call directly.
    """
    try:
        vis_window = getattr(inst, "window", None)
        if vis_window is not None and hasattr(vis_window, "after"):
            vis_window.after(0, lambda: fn(*args, **kwargs))
        else:
            fn(*args, **kwargs)
    except Exception as e:
        # last resort: try calling directly and swallow errors
        try:
            fn(*args, **kwargs)
        except Exception as ex:
            print("function_dispatcher: UI call failed:", ex)

def dispatch(function_name: str, raw_args: Optional[Any] = None) -> Dict[str, Any]:
    """
    Dispatch a logical function name to the registered visualizer instance.
    Returns a dict: {"ok": bool, "message": str}
    """
    args = _safe_parse_args(raw_args)
    try:
        if function_name.startswith("linked_list_"):
            inst = _reg.get("linked_list")
            if not inst:
                return {"ok": False, "message": "没有注册单链表可视化实例。请先打开单链表窗口。"}
            # insert last
            if function_name == "linked_list_insert_last":
                _call_on_ui_thread_if_possible(inst, getattr(inst, "programmatic_insert_last"), args.get("value"))
                return {"ok": True, "message": f"已调度：在链表尾部插入 {args.get('value')}"}
            # insert first
            if function_name == "linked_list_insert_first":
                _call_on_ui_thread_if_possible(inst, getattr(inst, "programmatic_insert_first"), args.get("value"))
                return {"ok": True, "message": f"已调度：在链表头部插入 {args.get('value')}"}
            # insert at index (1-based). Try programmatic_insert_at, fallback to first/last
            if function_name == "linked_list_insert_at":
                idx = args.get("index")
                val = args.get("value")
                if hasattr(inst, "programmatic_insert_at"):
                    _call_on_ui_thread_if_possible(inst, getattr(inst, "programmatic_insert_at"), int(idx), val)
                    return {"ok": True, "message": f"已调度：在链表第 {idx} 位插入 {val}"}
                else:
                    # fallback: index 1 -> insert_first; else insert_last (best-effort)
                    if idx and int(idx) == 1 and hasattr(inst, "programmatic_insert_first"):
                        _call_on_ui_thread_if_possible(inst, getattr(inst, "programmatic_insert_first"), val)
                        return {"ok": True, "message": f"已调度（回退）: 在链表头部插入 {val}"}
                    else:
                        _call_on_ui_thread_if_possible(inst, getattr(inst, "programmatic_insert_last"), val)
                        return {"ok": True, "message": f"已调度（回退）: 在链表尾部插入 {val}（因为未实现 insert_at）"}
            # delete first
            if function_name == "linked_list_delete_first":
                if hasattr(inst, "delete_first_node"):
                    _call_on_ui_thread_if_possible(inst, getattr(inst, "delete_first_node"))
                else:
                    _call_on_ui_thread_if_possible(inst, getattr(inst, "programmatic_delete_first") if hasattr(inst, "programmatic_delete_first") else getattr(inst, "delete_first", lambda: None))
                return {"ok": True, "message": "已调度：删除单链表第一个节点。"}
            # delete last
            if function_name == "linked_list_delete_last":
                if hasattr(inst, "delete_last_node"):
                    _call_on_ui_thread_if_possible(inst, getattr(inst, "delete_last_node"), 0)
                else:
                    _call_on_ui_thread_if_possible(inst, getattr(inst, "programmatic_delete_last") if hasattr(inst, "programmatic_delete_last") else getattr(inst, "delete_last", lambda: None))
                return {"ok": True, "message": "已调度：删除单链表最后一个节点。"}
            # create
            if function_name == "linked_list_create":
                vals = args.get("values") or []
                for v in vals:
                    _call_on_ui_thread_if_possible(inst, getattr(inst, "programmatic_insert_last"), v)
                return {"ok": True, "message": f"已调度：批量创建单链表，元素数: {len(vals)}"}
        # stack handling
        if function_name.startswith("stack_"):
            inst = _reg.get("stack")
            if not inst:
                return {"ok": False, "message": "没有注册栈可视化实例。请先打开栈窗口。"}
            if function_name == "stack_push":
                _call_on_ui_thread_if_possible(inst, getattr(inst, "programmatic_push"), args.get("value"))
                return {"ok": True, "message": f"已调度：向栈 push {args.get('value')}"}
            if function_name == "stack_pop":
                _call_on_ui_thread_if_possible(inst, getattr(inst, "programmatic_pop"))
                return {"ok": True, "message": "已调度：从栈 pop 一个元素。"}
        return {"ok": False, "message": f"未知函数: {function_name}"}
    except Exception as e:
        tb = traceback.format_exc()
        return {"ok": False, "message": f"执行函数 {function_name} 时发生异常: {e}\n{tb}"}
