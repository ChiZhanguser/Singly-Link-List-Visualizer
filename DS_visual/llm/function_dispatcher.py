import json
import weakref
import os
import importlib
import importlib.util
import re
from typing import Any, Dict, Optional
from llm.function_aliases import _ALIAS_MAP  
import sys

# 全局变量存储主程序的可视化实例
_main_window_instance = None

def set_main_window_instance(main_window):
    """设置主窗口实例，用于访问可视化组件"""
    global _main_window_instance
    _main_window_instance = main_window

def _get_visualizer_instance(structure_type: str):
    """获取指定类型的可视化实例"""
    global _main_window_instance
    if _main_window_instance is None:
        return None
    
    try:
        # 从主窗口的tabs中获取对应的实例
        tabs = getattr(_main_window_instance, 'tabs', {})
        for key, (ctor, frame, instance, title) in tabs.items():
            if key == structure_type and instance is not None:
                return instance
    except Exception as e:
        print(f"Error getting visualizer instance for {structure_type}: {e}")
    
    return None

def _safe_parse_args(arguments: Any) -> Any:
    if arguments is None:
        return {}
    if isinstance(arguments, str):
        try:
            return json.loads(arguments)
        except Exception:
            return {"__raw": arguments}
    return arguments

def _normalize_name(raw):
    if not isinstance(raw, str):
        return raw
    s = raw.strip()
    s = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s)
    s = re.sub(r'[^0-9a-zA-Z_]', '_', s).lower()
    s = re.sub(r'_+', '_', s).strip('_')
    s = re.sub(r'^(demo|do|action)_', '', s)
    return _ALIAS_MAP.get(s, s)

def dispatch(name: str, arguments: Any) -> Dict[str, Any]:
    """分发函数调用到对应的可视化组件"""
    args = _safe_parse_args(arguments)
    if isinstance(name, str):
        name = _normalize_name(name)

    try:
        print(f"dispatch -> name={name!r}, arguments={args!r}")
    except Exception:
        pass

    # 处理栈相关操作
    if name in ("stack_push", "push"):
        instance = _get_visualizer_instance("stack")
        if instance is None:
            return {"ok": False, "error": "stack visualizer not available"}
        
        value = args.get("value") if isinstance(args, dict) and "value" in args else args
        try:
            # 调用栈的push方法
            if hasattr(instance, 'push'):
                instance.push(value)
                return {"ok": True, "message": f"pushed {value} to stack"}
            else:
                return {"ok": False, "error": "stack instance missing push method"}
        except Exception as e:
            return {"ok": False, "error": f"stack push error: {e}"}

    elif name in ("stack_pop", "pop"):
        instance = _get_visualizer_instance("stack")
        if instance is None:
            return {"ok": False, "error": "stack visualizer not available"}
        
        try:
            if hasattr(instance, 'pop'):
                result = instance.pop()
                return {"ok": True, "message": f"popped {result} from stack", "result": result}
            else:
                return {"ok": False, "error": "stack instance missing pop method"}
        except Exception as e:
            return {"ok": False, "error": f"stack pop error: {e}"}

    elif name in ("stack_clear", "clear"):
        instance = _get_visualizer_instance("stack")
        if instance is None:
            return {"ok": False, "error": "stack visualizer not available"}
        
        try:
            if hasattr(instance, 'clear'):
                instance.clear()
                return {"ok": True, "message": "stack cleared"}
            else:
                return {"ok": False, "error": "stack instance missing clear method"}
        except Exception as e:
            return {"ok": False, "error": f"stack clear error: {e}"}

    elif name in ("stack_batch_create", "batch_create"):
        instance = _get_visualizer_instance("stack")
        if instance is None:
            return {"ok": False, "error": "stack visualizer not available"}
        
        vals = args.get("values") if isinstance(args, dict) and "values" in args else args
        if isinstance(vals, str):
            vals = [s.strip() for s in vals.split(",") if s.strip() != ""]
        
        try:
            if hasattr(instance, 'batch_create'):
                instance.batch_create(vals)
                return {"ok": True, "message": f"created stack with values: {vals}"}
            else:
                return {"ok": False, "error": "stack instance missing batch_create method"}
        except Exception as e:
            return {"ok": False, "error": f"stack batch_create error: {e}"}

    elif name in ("stack_get_state", "get_state"):
        instance = _get_visualizer_instance("stack")
        if instance is None:
            return {"ok": False, "error": "stack visualizer not available"}
        
        try:
            if hasattr(instance, 'get_state'):
                state = instance.get_state()
                return {"ok": True, "state": state}
            else:
                return {"ok": False, "error": "stack instance missing get_state method"}
        except Exception as e:
            return {"ok": False, "error": f"stack get_state error: {e}"}

    # 处理顺序表相关操作
    elif name in ("sequence_insert_last", "sequence_insert", "insert_last", "insert"):
        instance = _get_visualizer_instance("sequence")
        if instance is None:
            return {"ok": False, "error": "sequence visualizer not available"}
        
        value = args.get("value") if isinstance(args, dict) and "value" in args else args
        try:
            if hasattr(instance, 'insert_last'):
                instance.insert_last(value)
                return {"ok": True, "message": f"inserted {value} at end of sequence"}
            elif hasattr(instance, 'append'):
                instance.append(value)
                return {"ok": True, "message": f"appended {value} to sequence"}
            else:
                return {"ok": False, "error": "sequence instance missing insert/append method"}
        except Exception as e:
            return {"ok": False, "error": f"sequence insert error: {e}"}

    elif name in ("sequence_insert_at", "sequence_insert_pos", "insert_at"):
        instance = _get_visualizer_instance("sequence")
        if instance is None:
            return {"ok": False, "error": "sequence visualizer not available"}
        
        idx = None
        val = None
        if isinstance(args, dict):
            val = args.get("value") or args.get("val")
            idx = args.get("index") or args.get("position") or args.get("pos")
        if idx is None and isinstance(args, (list, tuple)) and len(args) >= 2:
            idx = args[0]; val = args[1]
        if idx is None:
            return {"ok": False, "error": "missing index for sequence_insert_at"}
        
        try:
            idx_int = int(idx)
        except Exception:
            return {"ok": False, "error": f"invalid index: {idx}"}
        
        try:
            if hasattr(instance, 'insert_at'):
                instance.insert_at(idx_int, val)
                return {"ok": True, "message": f"inserted {val} at position {idx_int}"}
            else:
                return {"ok": False, "error": "sequence instance missing insert_at method"}
        except Exception as e:
            return {"ok": False, "error": f"sequence insert_at error: {e}"}

    elif name in ("sequence_delete_at", "sequence_delete", "delete_at", "remove_at"):
        instance = _get_visualizer_instance("sequence")
        if instance is None:
            return {"ok": False, "error": "sequence visualizer not available"}
        
        idx = None
        if isinstance(args, dict):
            idx = args.get("index") or args.get("position") or args.get("pos")
        if idx is None and isinstance(args, (int, str)):
            idx = args
        if idx is None:
            return {"ok": False, "error": "missing index for sequence_delete_at"}
        
        try:
            idx_int = int(idx)
        except Exception:
            return {"ok": False, "error": f"invalid index: {idx}"}
        
        try:
            if hasattr(instance, 'delete_at'):
                result = instance.delete_at(idx_int)
                return {"ok": True, "message": f"deleted element at position {idx_int}", "result": result}
            elif hasattr(instance, 'pop'):
                result = instance.pop(idx_int)
                return {"ok": True, "message": f"popped element at position {idx_int}", "result": result}
            else:
                return {"ok": False, "error": "sequence instance missing delete method"}
        except Exception as e:
            return {"ok": False, "error": f"sequence delete error: {e}"}

    elif name in ("sequence_clear", "clear_sequence", "clear_list", "clear_sequence_list"):
        instance = _get_visualizer_instance("sequence")
        if instance is None:
            return {"ok": False, "error": "sequence visualizer not available"}
        
        try:
            if hasattr(instance, 'clear'):
                instance.clear()
                return {"ok": True, "message": "sequence cleared"}
            else:
                return {"ok": False, "error": "sequence instance missing clear method"}
        except Exception as e:
            return {"ok": False, "error": f"sequence clear error: {e}"}

    elif name in ("sequence_batch_create", "batch_create_sequence", "batch_create",
                "create_sequence_list", "create_list", "create_seq_list", "build_list",
                "create_sequence", "build_sequence"):
        instance = _get_visualizer_instance("sequence")
        if instance is None:
            return {"ok": False, "error": "sequence visualizer not available"}
        
        vals = None
        if isinstance(args, dict):
            vals = args.get("values") or args.get("elements") or args.get("data") or args.get("items")
        if vals is None and isinstance(args, (list, tuple)):
            vals = list(args)
        if vals is None:
            vals = args
        if isinstance(vals, str):
            vals = [s.strip() for s in vals.split(",") if s.strip() != ""]
        
        try:
            if hasattr(instance, 'batch_create'):
                instance.batch_create(vals)
                return {"ok": True, "message": f"created sequence with values: {vals}"}
            else:
                return {"ok": False, "error": "sequence instance missing batch_create method"}
        except Exception as e:
            return {"ok": False, "error": f"sequence batch_create error: {e}"}

    elif name in ("sequence_get_state", "get_sequence_state", "get_list_state"):
        instance = _get_visualizer_instance("sequence")
        if instance is None:
            return {"ok": False, "error": "sequence visualizer not available"}
        
        try:
            if hasattr(instance, 'get_state'):
                state = instance.get_state()
                return {"ok": True, "state": state}
            else:
                return {"ok": False, "error": "sequence instance missing get_state method"}
        except Exception as e:
            return {"ok": False, "error": f"sequence get_state error: {e}"}

    # 处理单链表相关操作
    elif name in ("linked_list_insert_last", "linked_list_insert", "linked_list_insert_tail", 
                  "linked_list_add", "linked_list_push", "linked_list_append", 
                  "linked_list_insert_end", "linked_list_insert_tail"):
        instance = _get_visualizer_instance("linked_list")
        if instance is None:
            return {"ok": False, "error": "linked_list visualizer not available"}
        
        val = args.get("value") if isinstance(args, dict) and "value" in args else args
        try:
            if hasattr(instance, 'insert_last'):
                instance.insert_last(val)
                return {"ok": True, "message": f"inserted {val} at end of linked list"}
            elif hasattr(instance, 'append'):
                instance.append(val)
                return {"ok": True, "message": f"appended {val} to linked list"}
            else:
                return {"ok": False, "error": "linked_list instance missing insert method"}
        except Exception as e:
            return {"ok": False, "error": f"linked_list insert error: {e}"}

    elif name in ("linked_list_insert_first", "linked_list_insert_head"):
        instance = _get_visualizer_instance("linked_list")
        if instance is None:
            return {"ok": False, "error": "linked_list visualizer not available"}
        
        val = args.get("value") if isinstance(args, dict) and "value" in args else args
        try:
            if hasattr(instance, 'insert_first'):
                instance.insert_first(val)
                return {"ok": True, "message": f"inserted {val} at head of linked list"}
            else:
                return {"ok": False, "error": "linked_list instance missing insert_first method"}
        except Exception as e:
            return {"ok": False, "error": f"linked_list insert_first error: {e}"}

    elif name in ("linked_list_insert_at", "linked_list_insert_pos", "linked_list_insert_position", "linked_list_insert_index"):
        instance = _get_visualizer_instance("linked_list")
        if instance is None:
            return {"ok": False, "error": "linked_list visualizer not available"}
        
        idx = None
        val = None
        if isinstance(args, dict):
            idx = args.get("index") or args.get("position") or args.get("pos")
            val = args.get("value") or args.get("val")
        if idx is None and isinstance(args, (list, tuple)) and len(args) >= 2:
            idx = args[0]; val = args[1]
        if idx is None:
            return {"ok": False, "error": "missing index for linked_list_insert_at"}
        
        try:
            idx_int = int(idx)
        except Exception:
            return {"ok": False, "error": f"invalid index: {idx}"}
        
        try:
            if hasattr(instance, 'insert_at'):
                instance.insert_at(idx_int, val)
                return {"ok": True, "message": f"inserted {val} at position {idx_int}"}
            else:
                return {"ok": False, "error": "linked_list instance missing insert_at method"}
        except Exception as e:
            return {"ok": False, "error": f"linked_list insert_at error: {e}"}

    elif name in ("linked_list_delete_at", "linked_list_delete", "linked_list_remove_at"):
        instance = _get_visualizer_instance("linked_list")
        if instance is None:
            return {"ok": False, "error": "linked_list visualizer not available"}
        
        idx = None
        if isinstance(args, dict):
            idx = args.get("index") or args.get("position") or args.get("pos")
        if idx is None and isinstance(args, (int, str)):
            idx = args
        if idx is None:
            return {"ok": False, "error": "missing index for linked_list_delete_at"}
        
        try:
            idx_int = int(idx)
        except Exception:
            return {"ok": False, "error": f"invalid index: {idx}"}
        
        try:
            if hasattr(instance, 'delete_at'):
                result = instance.delete_at(idx_int)
                return {"ok": True, "message": f"deleted element at position {idx_int}", "result": result}
            elif hasattr(instance, 'pop'):
                result = instance.pop(idx_int)
                return {"ok": True, "message": f"popped element at position {idx_int}", "result": result}
            else:
                return {"ok": False, "error": "linked_list instance missing delete method"}
        except Exception as e:
            return {"ok": False, "error": f"linked_list delete error: {e}"}

    elif name in ("linked_list_clear", "linked_list_clear_all", "linked_list_reset", "linked_list_empty"):
        instance = _get_visualizer_instance("linked_list")
        if instance is None:
            return {"ok": False, "error": "linked_list visualizer not available"}
        
        try:
            if hasattr(instance, 'clear'):
                instance.clear()
                return {"ok": True, "message": "linked list cleared"}
            else:
                return {"ok": False, "error": "linked_list instance missing clear method"}
        except Exception as e:
            return {"ok": False, "error": f"linked_list clear error: {e}"}

    elif name in ("linked_list_batch_create", "linked_list_create", "linked_list_build", "linked_list_create_from"):
        instance = _get_visualizer_instance("linked_list")
        if instance is None:
            return {"ok": False, "error": "linked_list visualizer not available"}
        
        vals = args.get("values") if isinstance(args, dict) and "values" in args else args
        if isinstance(vals, str):
            vals = [s.strip() for s in vals.split(",") if s.strip() != ""]
        
        try:
            if hasattr(instance, 'batch_create'):
                instance.batch_create(vals)
                return {"ok": True, "message": f"created linked list with values: {vals}"}
            else:
                return {"ok": False, "error": "linked_list instance missing batch_create method"}
        except Exception as e:
            return {"ok": False, "error": f"linked_list batch_create error: {e}"}

    elif name in ("linked_list_get_state", "get_linked_list_state"):
        instance = _get_visualizer_instance("linked_list")
        if instance is None:
            return {"ok": False, "error": "linked_list visualizer not available"}
        
        try:
            if hasattr(instance, 'get_state'):
                state = instance.get_state()
                return {"ok": True, "state": state}
            else:
                return {"ok": False, "error": "linked_list instance missing get_state method"}
        except Exception as e:
            return {"ok": False, "error": f"linked_list get_state error: {e}"}

    return {"ok": False, "error": f"unknown function name: {name}"}
