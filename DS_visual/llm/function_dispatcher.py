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

# 已注册的可视化器实例（用于独立窗口模式）
_registered_visualizers: Dict[str, Any] = {}

def set_main_window_instance(main_window):
    """设置主窗口实例，用于访问可视化组件"""
    global _main_window_instance
    _main_window_instance = main_window

def register_visualizer(structure_type: str, instance):
    """注册可视化器实例（用于独立窗口模式）"""
    global _registered_visualizers
    _registered_visualizers[structure_type] = instance
    print(f"Registered visualizer: {structure_type}")

def unregister_visualizer(structure_type: str):
    """注销可视化器实例"""
    global _registered_visualizers
    if structure_type in _registered_visualizers:
        del _registered_visualizers[structure_type]
        print(f"Unregistered visualizer: {structure_type}")

def _get_visualizer_instance(structure_type: str):
    """获取指定类型的可视化实例"""
    global _main_window_instance, _registered_visualizers
    
    # 首先从已注册的实例中查找
    if structure_type in _registered_visualizers:
        return _registered_visualizers[structure_type]
    
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

    elif name in ("stack_eval_postfix", "eval_postfix", "postfix_eval", "evaluate_postfix"):
        instance = _get_visualizer_instance("stack")
        if instance is None:
            return {"ok": False, "error": "stack visualizer not available"}
        
        expression = None
        if isinstance(args, dict):
            expression = args.get("expression") or args.get("expr") or args.get("postfix")
        if expression is None and isinstance(args, str):
            expression = args
        if expression is None:
            return {"ok": False, "error": "missing expression for stack_eval_postfix"}
        
        try:
            if hasattr(instance, 'start_postfix_eval'):
                instance.start_postfix_eval(expression)
                return {"ok": True, "message": f"started postfix evaluation for: {expression}"}
            else:
                return {"ok": False, "error": "stack instance missing start_postfix_eval method"}
        except Exception as e:
            return {"ok": False, "error": f"stack eval_postfix error: {e}"}

    elif name in ("stack_bracket_match", "bracket_match", "match_brackets", "check_brackets"):
        instance = _get_visualizer_instance("stack")
        if instance is None:
            return {"ok": False, "error": "stack visualizer not available"}
        
        expression = None
        if isinstance(args, dict):
            expression = args.get("expression") or args.get("expr") or args.get("brackets")
        if expression is None and isinstance(args, str):
            expression = args
        if expression is None:
            return {"ok": False, "error": "missing expression for stack_bracket_match"}
        
        try:
            if hasattr(instance, 'start_bracket_match'):
                instance.start_bracket_match(expression)
                return {"ok": True, "message": f"started bracket matching for: {expression}"}
            else:
                return {"ok": False, "error": "stack instance missing start_bracket_match method"}
        except Exception as e:
            return {"ok": False, "error": f"stack bracket_match error: {e}"}

    elif name in ("stack_dfs", "dfs", "dfs_visualize", "depth_first_search"):
        instance = _get_visualizer_instance("stack")
        if instance is None:
            return {"ok": False, "error": "stack visualizer not available"}
        
        # 获取参数
        vertex_count = 7
        branch_factor = 2
        start_vertex = "A"
        
        if isinstance(args, dict):
            if "vertex_count" in args:
                try:
                    vertex_count = int(args["vertex_count"])
                    vertex_count = max(5, min(10, vertex_count))
                except:
                    pass
            if "branch_factor" in args:
                try:
                    branch_factor = int(args["branch_factor"])
                    branch_factor = max(1, min(3, branch_factor))
                except:
                    pass
            if "start_vertex" in args:
                start_vertex = str(args["start_vertex"]).strip().upper()
        
        try:
            # 打开DFS可视化窗口
            if hasattr(instance, '_open_dfs_visualizer'):
                instance._open_dfs_visualizer()
                return {"ok": True, "message": f"opened DFS visualizer (vertices: {vertex_count}, branch: {branch_factor}, start: {start_vertex})"}
            else:
                return {"ok": False, "error": "stack instance missing _open_dfs_visualizer method"}
        except Exception as e:
            return {"ok": False, "error": f"stack dfs error: {e}"}

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

    elif name in ("sequence_reverse", "reverse_sequence", "reverse_list", "reverse"):
        instance = _get_visualizer_instance("sequence")
        if instance is None:
            return {"ok": False, "error": "sequence visualizer not available"}
        
        try:
            if hasattr(instance, 'start_reverse'):
                instance.start_reverse()
                return {"ok": True, "message": "sequence reversed with animation"}
            else:
                return {"ok": False, "error": "sequence instance missing start_reverse method"}
        except Exception as e:
            return {"ok": False, "error": f"sequence reverse error: {e}"}

    elif name in ("sequence_bubble_sort", "bubble_sort", "bubblesort", "sequence_sort"):
        instance = _get_visualizer_instance("sequence")
        if instance is None:
            return {"ok": False, "error": "sequence visualizer not available"}
        
        try:
            if hasattr(instance, 'start_bubble_sort'):
                instance.start_bubble_sort()
                return {"ok": True, "message": "bubble sort started with animation"}
            else:
                return {"ok": False, "error": "sequence instance missing start_bubble_sort method"}
        except Exception as e:
            return {"ok": False, "error": f"sequence bubble_sort error: {e}"}

    elif name in ("sequence_insertion_sort", "insertion_sort", "insertionsort"):
        instance = _get_visualizer_instance("sequence")
        if instance is None:
            return {"ok": False, "error": "sequence visualizer not available"}
        
        try:
            if hasattr(instance, 'start_insertion_sort'):
                instance.start_insertion_sort()
                return {"ok": True, "message": "insertion sort started with animation"}
            else:
                return {"ok": False, "error": "sequence instance missing start_insertion_sort method"}
        except Exception as e:
            return {"ok": False, "error": f"sequence insertion_sort error: {e}"}

    elif name in ("sequence_quick_sort", "quick_sort", "quicksort"):
        instance = _get_visualizer_instance("sequence")
        if instance is None:
            return {"ok": False, "error": "sequence visualizer not available"}
        
        try:
            if hasattr(instance, 'start_quick_sort'):
                instance.start_quick_sort()
                return {"ok": True, "message": "quick sort started with animation"}
            else:
                return {"ok": False, "error": "sequence instance missing start_quick_sort method"}
        except Exception as e:
            return {"ok": False, "error": f"sequence quick_sort error: {e}"}

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

    elif name in ("linked_list_delete_value", "linked_list_delete_by_value", "linked_list_remove_value"):
        instance = _get_visualizer_instance("linked_list")
        if instance is None:
            return {"ok": False, "error": "linked_list visualizer not available"}
        
        value = None
        if isinstance(args, dict):
            value = args.get("value") or args.get("val")
        if value is None and isinstance(args, (str, int, float)):
            value = args
        if value is None:
            return {"ok": False, "error": "missing value for linked_list_delete_value"}
        
        try:
            if hasattr(instance, 'delete_by_value'):
                result = instance.delete_by_value(value)
                if result:
                    return {"ok": True, "message": f"deleted first node with value '{value}'"}
                else:
                    return {"ok": True, "message": f"value '{value}' not found in linked list", "found": False}
            else:
                return {"ok": False, "error": "linked_list instance missing delete_by_value method"}
        except Exception as e:
            return {"ok": False, "error": f"linked_list delete_value error: {e}"}

    elif name in ("linked_list_insert_before", "linked_list_insert_before_value"):
        instance = _get_visualizer_instance("linked_list")
        if instance is None:
            return {"ok": False, "error": "linked_list visualizer not available"}
        
        target_value = None
        new_value = None
        if isinstance(args, dict):
            target_value = args.get("target_value") or args.get("target")
            new_value = args.get("new_value") or args.get("value") or args.get("new")
        if target_value is None or new_value is None:
            return {"ok": False, "error": "missing target_value or new_value for linked_list_insert_before"}
        
        try:
            if hasattr(instance, 'insert_before_value'):
                result = instance.insert_before_value(target_value, new_value)
                if result:
                    return {"ok": True, "message": f"inserted '{new_value}' before node with value '{target_value}'"}
                else:
                    return {"ok": True, "message": f"value '{target_value}' not found in linked list", "found": False}
            else:
                return {"ok": False, "error": "linked_list instance missing insert_before_value method"}
        except Exception as e:
            return {"ok": False, "error": f"linked_list insert_before error: {e}"}

    elif name in ("linked_list_insert_after", "linked_list_insert_after_value"):
        instance = _get_visualizer_instance("linked_list")
        if instance is None:
            return {"ok": False, "error": "linked_list visualizer not available"}
        
        target_value = None
        new_value = None
        if isinstance(args, dict):
            target_value = args.get("target_value") or args.get("target")
            new_value = args.get("new_value") or args.get("value") or args.get("new")
        if target_value is None or new_value is None:
            return {"ok": False, "error": "missing target_value or new_value for linked_list_insert_after"}
        
        try:
            if hasattr(instance, 'insert_after_value'):
                result = instance.insert_after_value(target_value, new_value)
                if result:
                    return {"ok": True, "message": f"inserted '{new_value}' after node with value '{target_value}'"}
                else:
                    return {"ok": True, "message": f"value '{target_value}' not found in linked list", "found": False}
            else:
                return {"ok": False, "error": "linked_list instance missing insert_after_value method"}
        except Exception as e:
            return {"ok": False, "error": f"linked_list insert_after error: {e}"}

    elif name in ("linked_list_insert_between", "linked_list_insert_between_values"):
        instance = _get_visualizer_instance("linked_list")
        if instance is None:
            return {"ok": False, "error": "linked_list visualizer not available"}
        
        value_a = None
        value_b = None
        new_value = None
        if isinstance(args, dict):
            value_a = args.get("value_a") or args.get("a")
            value_b = args.get("value_b") or args.get("b")
            new_value = args.get("new_value") or args.get("value") or args.get("new") or args.get("x")
        if value_a is None or value_b is None or new_value is None:
            return {"ok": False, "error": "missing value_a, value_b, or new_value for linked_list_insert_between"}
        
        try:
            if hasattr(instance, 'insert_between_values'):
                result = instance.insert_between_values(value_a, value_b, new_value)
                if result:
                    return {"ok": True, "message": f"inserted '{new_value}' between nodes '{value_a}' and '{value_b}'"}
                else:
                    return {"ok": True, "message": f"could not insert between '{value_a}' and '{value_b}'", "success": False}
            else:
                return {"ok": False, "error": "linked_list instance missing insert_between_values method"}
        except Exception as e:
            return {"ok": False, "error": f"linked_list insert_between error: {e}"}

    elif name in ("linked_list_search", "linked_list_find", "linkedlist_search"):
        instance = _get_visualizer_instance("linked_list")
        if instance is None:
            return {"ok": False, "error": "linked_list visualizer not available"}
        
        value = None
        if isinstance(args, dict):
            value = args.get("value") or args.get("val") or args.get("target")
        if value is None and isinstance(args, (str, int, float)):
            value = args
        if value is None:
            return {"ok": False, "error": "missing value for linked_list_search"}
        
        try:
            if hasattr(instance, 'enhanced_ops') and instance.enhanced_ops:
                instance.enhanced_ops.search_with_animation(value)
                return {"ok": True, "message": f"searching for value '{value}' with animation"}
            else:
                return {"ok": False, "error": "linked_list enhanced_ops not available"}
        except Exception as e:
            return {"ok": False, "error": f"linked_list search error: {e}"}

    elif name in ("linked_list_reverse", "linkedlist_reverse"):
        instance = _get_visualizer_instance("linked_list")
        if instance is None:
            return {"ok": False, "error": "linked_list visualizer not available"}
        
        try:
            if hasattr(instance, 'enhanced_ops') and instance.enhanced_ops:
                instance.enhanced_ops.reverse_with_animation()
                return {"ok": True, "message": "reversing linked list with animation"}
            else:
                return {"ok": False, "error": "linked_list enhanced_ops not available"}
        except Exception as e:
            return {"ok": False, "error": f"linked_list reverse error: {e}"}

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

    # ========== AVL 树相关操作 ==========
    
    elif name in ("avl_insert", "avl_add", "avl_insert_node"):
        instance = _get_visualizer_instance("avl")
        if instance is None:
            return {"ok": False, "error": "AVL visualizer not available"}
        
        vals = args.get("values") if isinstance(args, dict) and "values" in args else args
        # 处理不同类型的输入
        if isinstance(vals, (int, float)):
            vals = [vals]
        elif isinstance(vals, str):
            vals = [s.strip() for s in vals.split(",") if s.strip() != ""]
        
        try:
            # 设置输入并触发插入动画
            vals_str = ", ".join(map(str, vals))
            instance.input_var.set(vals_str)
            instance.start_insert_animated()
            return {"ok": True, "message": f"AVL inserting: {vals_str}"}
        except Exception as e:
            return {"ok": False, "error": f"AVL insert error: {e}"}

    elif name in ("avl_delete", "avl_remove", "avl_delete_node"):
        instance = _get_visualizer_instance("avl")
        if instance is None:
            return {"ok": False, "error": "AVL visualizer not available"}
        
        vals = args.get("values") if isinstance(args, dict) and "values" in args else args
        # 处理不同类型的输入
        if isinstance(vals, (int, float)):
            vals = [vals]
        elif isinstance(vals, str):
            vals = [s.strip() for s in vals.split(",") if s.strip() != ""]
        
        try:
            # 设置输入并触发删除动画
            vals_str = ", ".join(map(str, vals))
            instance.input_var.set(vals_str)
            instance.start_delete_animated()
            return {"ok": True, "message": f"AVL deleting: {vals_str}"}
        except Exception as e:
            return {"ok": False, "error": f"AVL delete error: {e}"}

    elif name in ("avl_search", "avl_find", "avl_lookup"):
        instance = _get_visualizer_instance("avl")
        if instance is None:
            return {"ok": False, "error": "AVL visualizer not available"}
        
        vals = args.get("values") if isinstance(args, dict) and "values" in args else args
        # 处理不同类型的输入
        if isinstance(vals, (int, float)):
            vals = [vals]
        elif isinstance(vals, str):
            vals = [s.strip() for s in vals.split(",") if s.strip() != ""]
        
        try:
            # 设置输入并触发查找动画
            vals_str = ", ".join(map(str, vals))
            instance.input_var.set(vals_str)
            instance.start_search_animated()
            return {"ok": True, "message": f"AVL searching: {vals_str}"}
        except Exception as e:
            return {"ok": False, "error": f"AVL search error: {e}"}

    elif name in ("avl_clear", "avl_reset", "clear_avl"):
        instance = _get_visualizer_instance("avl")
        if instance is None:
            return {"ok": False, "error": "AVL visualizer not available"}
        
        try:
            instance.clear_canvas()
            return {"ok": True, "message": "AVL tree cleared"}
        except Exception as e:
            return {"ok": False, "error": f"AVL clear error: {e}"}

    elif name in ("avl_batch_create", "avl_create", "create_avl"):
        instance = _get_visualizer_instance("avl")
        if instance is None:
            return {"ok": False, "error": "AVL visualizer not available"}
        
        vals = args.get("values") if isinstance(args, dict) and "values" in args else args
        if isinstance(vals, str):
            vals = [s.strip() for s in vals.split(",") if s.strip() != ""]
        
        try:
            # 先清空树
            instance.model.root = None
            # 设置输入并触发插入动画
            vals_str = ", ".join(map(str, vals))
            instance.input_var.set(vals_str)
            instance.start_insert_animated()
            return {"ok": True, "message": f"AVL batch creating: {vals_str}"}
        except Exception as e:
            return {"ok": False, "error": f"AVL batch_create error: {e}"}

    elif name in ("avl_get_state", "get_avl_state"):
        instance = _get_visualizer_instance("avl")
        if instance is None:
            return {"ok": False, "error": "AVL visualizer not available"}
        
        try:
            # 收集树的状态信息
            def collect_tree_info(node, depth=0):
                if node is None:
                    return None
                return {
                    "val": node.val,
                    "height": node.height,
                    "depth": depth,
                    "left": collect_tree_info(node.left, depth + 1),
                    "right": collect_tree_info(node.right, depth + 1)
                }
            
            root = instance.model.root
            tree_info = collect_tree_info(root)
            
            # 计算节点数量
            def count_nodes(node):
                if node is None:
                    return 0
                return 1 + count_nodes(node.left) + count_nodes(node.right)
            
            node_count = count_nodes(root)
            
            return {
                "ok": True, 
                "state": {
                    "node_count": node_count,
                    "tree": tree_info,
                    "is_empty": root is None
                }
            }
        except Exception as e:
            return {"ok": False, "error": f"AVL get_state error: {e}"}

    # ========== 红黑树 (RBT) 相关操作 ==========
    
    elif name in ("rbt_insert", "rbt_add", "rbt_insert_node"):
        instance = _get_visualizer_instance("rbt")
        if instance is None:
            return {"ok": False, "error": "RBT visualizer not available"}
        
        vals = args.get("values") if isinstance(args, dict) and "values" in args else args
        # 处理不同类型的输入
        if isinstance(vals, (int, float)):
            vals = [vals]
        elif isinstance(vals, str):
            vals = [s.strip() for s in vals.split(",") if s.strip() != ""]
        
        try:
            # 设置输入并触发插入动画
            vals_str = ", ".join(map(str, vals))
            instance.input_var.set(vals_str)
            instance.start_insert_animated()
            return {"ok": True, "message": f"RBT inserting: {vals_str}"}
        except Exception as e:
            return {"ok": False, "error": f"RBT insert error: {e}"}

    elif name in ("rbt_delete", "rbt_remove", "rbt_delete_node"):
        instance = _get_visualizer_instance("rbt")
        if instance is None:
            return {"ok": False, "error": "RBT visualizer not available"}
        
        val = args.get("value") if isinstance(args, dict) and "value" in args else args
        # 处理不同类型的输入
        if isinstance(val, (int, float)):
            val = str(val)
        elif isinstance(val, list) and len(val) > 0:
            val = str(val[0])
        
        try:
            # 设置输入并触发删除动画
            instance.input_var.set(str(val))
            instance.start_delete_animated()
            return {"ok": True, "message": f"RBT deleting: {val}"}
        except Exception as e:
            return {"ok": False, "error": f"RBT delete error: {e}"}

    elif name in ("rbt_search", "rbt_find", "rbt_lookup"):
        instance = _get_visualizer_instance("rbt")
        if instance is None:
            return {"ok": False, "error": "RBT visualizer not available"}
        
        vals = args.get("values") if isinstance(args, dict) and "values" in args else args
        # 处理不同类型的输入
        if isinstance(vals, (int, float)):
            vals = [vals]
        elif isinstance(vals, str):
            vals = [s.strip() for s in vals.split(",") if s.strip() != ""]
        
        try:
            # 设置输入并触发查找动画
            vals_str = ", ".join(map(str, vals))
            instance.input_var.set(vals_str)
            instance.start_search_animated()
            return {"ok": True, "message": f"RBT searching: {vals_str}"}
        except Exception as e:
            return {"ok": False, "error": f"RBT search error: {e}"}

    elif name in ("rbt_clear", "rbt_reset", "clear_rbt"):
        instance = _get_visualizer_instance("rbt")
        if instance is None:
            return {"ok": False, "error": "RBT visualizer not available"}
        
        try:
            instance.clear_canvas()
            return {"ok": True, "message": "RBT tree cleared"}
        except Exception as e:
            return {"ok": False, "error": f"RBT clear error: {e}"}

    elif name in ("rbt_batch_create", "rbt_create", "create_rbt"):
        instance = _get_visualizer_instance("rbt")
        if instance is None:
            return {"ok": False, "error": "RBT visualizer not available"}
        
        vals = args.get("values") if isinstance(args, dict) and "values" in args else args
        if isinstance(vals, str):
            vals = [s.strip() for s in vals.split(",") if s.strip() != ""]
        
        try:
            # 先清空树
            from rbt.rbt_model import RBModel
            instance.model = RBModel()
            # 设置输入并触发插入动画
            vals_str = ", ".join(map(str, vals))
            instance.input_var.set(vals_str)
            instance.start_insert_animated()
            return {"ok": True, "message": f"RBT batch creating: {vals_str}"}
        except Exception as e:
            return {"ok": False, "error": f"RBT batch_create error: {e}"}

    elif name in ("rbt_get_state", "get_rbt_state"):
        instance = _get_visualizer_instance("rbt")
        if instance is None:
            return {"ok": False, "error": "RBT visualizer not available"}
        
        try:
            # 收集树的状态信息
            def collect_tree_info(node, depth=0):
                if node is None:
                    return None
                return {
                    "val": node.val,
                    "color": node.color,
                    "depth": depth,
                    "left": collect_tree_info(node.left, depth + 1),
                    "right": collect_tree_info(node.right, depth + 1)
                }
            
            root = instance.model.root
            tree_info = collect_tree_info(root)
            
            # 计算节点数量
            def count_nodes(node):
                if node is None:
                    return 0
                return 1 + count_nodes(node.left) + count_nodes(node.right)
            
            node_count = count_nodes(root)
            
            return {
                "ok": True, 
                "state": {
                    "node_count": node_count,
                    "tree": tree_info,
                    "is_empty": root is None
                }
            }
        except Exception as e:
            return {"ok": False, "error": f"RBT get_state error: {e}"}

    # ========== Trie (字典树) 相关操作 ==========
    
    elif name in ("trie_insert", "trie_add", "trie_insert_word", "trie_insert_words"):
        instance = _get_visualizer_instance("trie")
        if instance is None:
            return {"ok": False, "error": "Trie visualizer not available"}
        
        vals = args.get("words") if isinstance(args, dict) and "words" in args else args
        if vals is None:
            vals = args.get("word") if isinstance(args, dict) and "word" in args else None
        if vals is None:
            vals = args.get("values") if isinstance(args, dict) and "values" in args else args
        
        # 处理不同类型的输入
        if isinstance(vals, str):
            vals = [s.strip() for s in vals.split(",") if s.strip() != ""]
        elif isinstance(vals, (list, tuple)):
            vals = [str(v).strip() for v in vals if str(v).strip() != ""]
        else:
            vals = [str(vals)]
        
        try:
            # 设置输入并触发插入动画
            vals_str = ", ".join(vals)
            instance.input_var.set(vals_str)
            instance.start_insert_animated()
            return {"ok": True, "message": f"Trie inserting: {vals_str}"}
        except Exception as e:
            return {"ok": False, "error": f"Trie insert error: {e}"}

    elif name in ("trie_search", "trie_find", "trie_lookup", "trie_search_word"):
        instance = _get_visualizer_instance("trie")
        if instance is None:
            return {"ok": False, "error": "Trie visualizer not available"}
        
        word = None
        if isinstance(args, dict):
            word = args.get("word") or args.get("value") or args.get("query")
        if word is None and isinstance(args, str):
            word = args.strip()
        if word is None and isinstance(args, (list, tuple)) and len(args) > 0:
            word = str(args[0]).strip()
        
        if not word:
            return {"ok": False, "error": "missing word for trie_search"}
        
        try:
            # 设置输入并触发查找动画
            instance.input_var.set(word)
            instance.start_search_animated()
            return {"ok": True, "message": f"Trie searching: {word}"}
        except Exception as e:
            return {"ok": False, "error": f"Trie search error: {e}"}

    elif name in ("trie_clear", "trie_reset", "clear_trie"):
        instance = _get_visualizer_instance("trie")
        if instance is None:
            return {"ok": False, "error": "Trie visualizer not available"}
        
        try:
            instance.clear_trie()
            return {"ok": True, "message": "Trie cleared"}
        except Exception as e:
            return {"ok": False, "error": f"Trie clear error: {e}"}

    elif name in ("trie_batch_create", "trie_create", "create_trie", "trie_build"):
        instance = _get_visualizer_instance("trie")
        if instance is None:
            return {"ok": False, "error": "Trie visualizer not available"}
        
        vals = args.get("words") if isinstance(args, dict) and "words" in args else args
        if vals is None:
            vals = args.get("values") if isinstance(args, dict) and "values" in args else args
        
        if isinstance(vals, str):
            vals = [s.strip() for s in vals.split(",") if s.strip() != ""]
        elif isinstance(vals, (list, tuple)):
            vals = [str(v).strip() for v in vals if str(v).strip() != ""]
        else:
            vals = [str(vals)]
        
        try:
            # 先清空Trie
            instance.clear_trie()
            # 设置输入并触发插入动画
            vals_str = ", ".join(vals)
            instance.input_var.set(vals_str)
            instance.start_insert_animated()
            return {"ok": True, "message": f"Trie batch creating: {vals_str}"}
        except Exception as e:
            return {"ok": False, "error": f"Trie batch_create error: {e}"}

    elif name in ("trie_get_state", "get_trie_state", "trie_get_words"):
        instance = _get_visualizer_instance("trie")
        if instance is None:
            return {"ok": False, "error": "Trie visualizer not available"}
        
        try:
            # 收集Trie中的所有单词
            def collect_words(node, prefix=""):
                words = []
                if node is None:
                    return words
                if node.is_end:
                    words.append(prefix)
                for ch, child in node.children.items():
                    words.extend(collect_words(child, prefix + ch))
                return words
            
            root = instance.model.root
            all_words = collect_words(root)
            
            # 计算节点数量
            def count_nodes(node):
                if node is None:
                    return 0
                count = 1
                for child in node.children.values():
                    count += count_nodes(child)
                return count
            
            node_count = count_nodes(root)
            
            return {
                "ok": True, 
                "state": {
                    "word_count": len(all_words),
                    "node_count": node_count,
                    "words": all_words,
                    "is_empty": len(all_words) == 0
                }
            }
        except Exception as e:
            return {"ok": False, "error": f"Trie get_state error: {e}"}

    # ========== B+ 树相关操作 ==========
    
    elif name in ("bplustree_insert", "bplus_insert", "bplus_add", "bplustree_add"):
        instance = _get_visualizer_instance("bplustree")
        if instance is None:
            return {"ok": False, "error": "B+ Tree visualizer not available"}
        
        vals = args.get("keys") if isinstance(args, dict) and "keys" in args else args
        if vals is None:
            vals = args.get("values") if isinstance(args, dict) and "values" in args else args
        
        # 处理不同类型的输入
        if isinstance(vals, (int, float)):
            vals = [vals]
        elif isinstance(vals, str):
            vals = [s.strip() for s in vals.split(",") if s.strip() != ""]
        elif isinstance(vals, (list, tuple)):
            vals = [str(v).strip() for v in vals if str(v).strip() != ""]
        else:
            vals = [str(vals)]
        
        try:
            # 设置输入并触发插入动画
            vals_str = ", ".join(str(v) for v in vals)
            instance.input_var.set(vals_str)
            instance.start_insert_animated()
            return {"ok": True, "message": f"B+ Tree inserting: {vals_str}"}
        except Exception as e:
            return {"ok": False, "error": f"B+ Tree insert error: {e}"}

    elif name in ("bplustree_search", "bplus_search", "bplus_find", "bplustree_find"):
        instance = _get_visualizer_instance("bplustree")
        if instance is None:
            return {"ok": False, "error": "B+ Tree visualizer not available"}
        
        key = None
        if isinstance(args, dict):
            key = args.get("key") or args.get("value") or args.get("query")
        if key is None and isinstance(args, (str, int, float)):
            key = args
        if key is None and isinstance(args, (list, tuple)) and len(args) > 0:
            key = args[0]
        
        if key is None:
            return {"ok": False, "error": "missing key for bplustree_search"}
        
        try:
            # 转换为整数（如果可能）
            try:
                key = int(key)
            except:
                pass
            
            # 简单的查找逻辑
            node = instance.tree.root
            found = False
            while node:
                if node.is_leaf:
                    if key in node.keys:
                        found = True
                    break
                i = 0
                while i < len(node.keys) and key >= node.keys[i]:
                    i += 1
                node = node.children[i] if i < len(node.children) else None
            
            if found:
                instance.update_status(f"✓ 找到键 {key}")
                return {"ok": True, "message": f"Key {key} found in B+ Tree", "found": True}
            else:
                instance.update_status(f"✗ 未找到键 {key}")
                return {"ok": True, "message": f"Key {key} not found in B+ Tree", "found": False}
        except Exception as e:
            return {"ok": False, "error": f"B+ Tree search error: {e}"}

    elif name in ("bplustree_clear", "bplus_clear", "clear_bplustree", "bplus_reset"):
        instance = _get_visualizer_instance("bplustree")
        if instance is None:
            return {"ok": False, "error": "B+ Tree visualizer not available"}
        
        try:
            instance.clear_tree()
            return {"ok": True, "message": "B+ Tree cleared"}
        except Exception as e:
            return {"ok": False, "error": f"B+ Tree clear error: {e}"}

    elif name in ("bplustree_batch_create", "bplus_create", "create_bplustree", "bplus_build"):
        instance = _get_visualizer_instance("bplustree")
        if instance is None:
            return {"ok": False, "error": "B+ Tree visualizer not available"}
        
        vals = args.get("keys") if isinstance(args, dict) and "keys" in args else args
        if vals is None:
            vals = args.get("values") if isinstance(args, dict) and "values" in args else args
        
        if isinstance(vals, str):
            vals = [s.strip() for s in vals.split(",") if s.strip() != ""]
        elif isinstance(vals, (list, tuple)):
            vals = [str(v).strip() for v in vals if str(v).strip() != ""]
        else:
            vals = [str(vals)]
        
        try:
            # 先清空树
            instance.clear_tree()
            # 设置输入并触发插入动画
            vals_str = ", ".join(str(v) for v in vals)
            instance.input_var.set(vals_str)
            instance.start_insert_animated()
            return {"ok": True, "message": f"B+ Tree batch creating: {vals_str}"}
        except Exception as e:
            return {"ok": False, "error": f"B+ Tree batch_create error: {e}"}

    elif name in ("bplustree_get_state", "get_bplustree_state", "bplus_get_state", "bplus_leaves"):
        instance = _get_visualizer_instance("bplustree")
        if instance is None:
            return {"ok": False, "error": "B+ Tree visualizer not available"}
        
        try:
            # 获取所有叶节点的键
            leaves = instance.tree.leaves()
            all_keys = []
            for leaf in leaves:
                all_keys.extend(leaf.keys)
            
            # 计算节点数量
            levels = instance.tree.nodes_by_level()
            node_count = sum(len(nodes) for nodes in levels.values())
            
            # 计算树高
            tree_height = max(levels.keys()) + 1 if levels else 0
            
            return {
                "ok": True, 
                "state": {
                    "key_count": len(all_keys),
                    "node_count": node_count,
                    "tree_height": tree_height,
                    "order": instance.tree.order,
                    "keys": all_keys,
                    "leaf_count": len(leaves),
                    "is_empty": len(all_keys) == 0
                }
            }
        except Exception as e:
            return {"ok": False, "error": f"B+ Tree get_state error: {e}"}

    # ========== 散列表相关操作 ==========
    
    elif name in ("hashtable_insert", "hash_insert", "hashtable_add", "hash_add"):
        instance = _get_visualizer_instance("hashtable")
        if instance is None:
            return {"ok": False, "error": "Hashtable visualizer not available"}
        
        val = None
        if isinstance(args, dict):
            val = args.get("value") or args.get("key")
        if val is None and isinstance(args, (str, int, float)):
            val = args
        
        if val is None:
            return {"ok": False, "error": "missing value for hashtable_insert"}
        
        try:
            val = int(val)
            instance.insert_value(val)
            return {"ok": True, "message": f"Inserted {val} into hashtable"}
        except Exception as e:
            return {"ok": False, "error": f"Hashtable insert error: {e}"}

    elif name in ("hashtable_find", "hash_find", "hashtable_search", "hash_search"):
        instance = _get_visualizer_instance("hashtable")
        if instance is None:
            return {"ok": False, "error": "Hashtable visualizer not available"}
        
        val = None
        if isinstance(args, dict):
            val = args.get("value") or args.get("key")
        if val is None and isinstance(args, (str, int, float)):
            val = args
        
        if val is None:
            return {"ok": False, "error": "missing value for hashtable_find"}
        
        try:
            val = int(val)
            instance.find_value(val)
            return {"ok": True, "message": f"Searching for {val} in hashtable"}
        except Exception as e:
            return {"ok": False, "error": f"Hashtable find error: {e}"}

    elif name in ("hashtable_delete", "hash_delete", "hashtable_remove", "hash_remove"):
        instance = _get_visualizer_instance("hashtable")
        if instance is None:
            return {"ok": False, "error": "Hashtable visualizer not available"}
        
        val = None
        if isinstance(args, dict):
            val = args.get("value") or args.get("key")
        if val is None and isinstance(args, (str, int, float)):
            val = args
        
        if val is None:
            return {"ok": False, "error": "missing value for hashtable_delete"}
        
        try:
            val = int(val)
            instance.delete_value(val)
            return {"ok": True, "message": f"Deleted {val} from hashtable"}
        except Exception as e:
            return {"ok": False, "error": f"Hashtable delete error: {e}"}

    elif name in ("hashtable_clear", "hash_clear", "clear_hashtable"):
        instance = _get_visualizer_instance("hashtable")
        if instance is None:
            return {"ok": False, "error": "Hashtable visualizer not available"}
        
        try:
            instance.clear_table()
            return {"ok": True, "message": "Hashtable cleared"}
        except Exception as e:
            return {"ok": False, "error": f"Hashtable clear error: {e}"}

    elif name in ("hashtable_batch_create", "hash_create", "create_hashtable", "hashtable_create"):
        instance = _get_visualizer_instance("hashtable")
        if instance is None:
            return {"ok": False, "error": "Hashtable visualizer not available"}
        
        vals = args.get("values") if isinstance(args, dict) and "values" in args else args
        if vals is None:
            vals = args.get("keys") if isinstance(args, dict) and "keys" in args else args
        
        if isinstance(vals, str):
            vals = [s.strip() for s in vals.split(",") if s.strip() != ""]
        elif isinstance(vals, (list, tuple)):
            vals = [str(v).strip() for v in vals if str(v).strip() != ""]
        else:
            vals = [str(vals)]
        
        try:
            # 转换为整数列表
            int_vals = [int(v) for v in vals]
            # 先清空
            instance.clear_table()
            # 设置批量队列
            instance.batch_queue = int_vals
            instance.batch_index = 0
            instance._set_buttons_state("disabled")
            instance._batch_step()
            return {"ok": True, "message": f"Creating hashtable with values: {int_vals}"}
        except Exception as e:
            return {"ok": False, "error": f"Hashtable batch_create error: {e}"}

    elif name in ("hashtable_get_state", "get_hashtable_state", "hash_get_state"):
        instance = _get_visualizer_instance("hashtable")
        if instance is None:
            return {"ok": False, "error": "Hashtable visualizer not available"}
        
        try:
            model = instance.model
            # 收集所有存储的值
            values = []
            for i, slot in enumerate(model.table):
                if slot is not None and slot != model.tombstone:
                    if isinstance(slot, list):
                        values.extend(slot)
                    else:
                        values.append(slot)
            
            return {
                "ok": True, 
                "state": {
                    "capacity": model.capacity,
                    "size": model.size,
                    "values": values,
                    "load_factor": model.size / model.capacity if model.capacity > 0 else 0,
                    "method": "open_addressing" if str(model.collision_method).find("OPEN") >= 0 else "chaining",
                    "is_empty": model.size == 0
                }
            }
        except Exception as e:
            return {"ok": False, "error": f"Hashtable get_state error: {e}"}

    elif name in ("hashtable_resize", "hash_resize", "resize_hashtable"):
        instance = _get_visualizer_instance("hashtable")
        if instance is None:
            return {"ok": False, "error": "Hashtable visualizer not available"}
        
        capacity = None
        if isinstance(args, dict):
            capacity = args.get("capacity") or args.get("size")
        if capacity is None and isinstance(args, (str, int)):
            capacity = args
        
        if capacity is None:
            return {"ok": False, "error": "missing capacity for hashtable_resize"}
        
        try:
            capacity = int(capacity)
            if capacity <= 0:
                return {"ok": False, "error": "capacity must be positive"}
            instance.capacity_var.set(str(capacity))
            instance._on_confirm_resize()
            return {"ok": True, "message": f"Hashtable resized to capacity {capacity}"}
        except Exception as e:
            return {"ok": False, "error": f"Hashtable resize error: {e}"}

    elif name in ("hashtable_switch", "hash_switch", "hashtable_switch_method", "switch_hashtable"):
        instance = _get_visualizer_instance("hashtable")
        if instance is None:
            return {"ok": False, "error": "Hashtable visualizer not available"}
        
        try:
            instance.switch_method()
            return {"ok": True, "message": "Hashtable collision method switched"}
        except Exception as e:
            return {"ok": False, "error": f"Hashtable switch error: {e}"}

    elif name in ("hashtable_set_hash", "hash_set_hash", "hashtable_hash", "set_hash_function"):
        instance = _get_visualizer_instance("hashtable")
        if instance is None:
            return {"ok": False, "error": "Hashtable visualizer not available"}
        
        expr = None
        rebuild = False
        if isinstance(args, dict):
            expr = args.get("expression") or args.get("expr") or args.get("hash")
            rebuild = args.get("rebuild", False)
        if expr is None and isinstance(args, str):
            expr = args.strip()
        
        if not expr:
            return {"ok": False, "error": "missing expression for hashtable_set_hash"}
        
        try:
            success = instance.set_hash_expression(expr, rebuild=rebuild)
            if success:
                return {"ok": True, "message": f"Hash function set to: h(x) = {expr}"}
            else:
                return {"ok": False, "error": "Failed to set hash expression"}
        except Exception as e:
            return {"ok": False, "error": f"Hashtable set_hash error: {e}"}

    return {"ok": False, "error": f"unknown function name: {name}"}
