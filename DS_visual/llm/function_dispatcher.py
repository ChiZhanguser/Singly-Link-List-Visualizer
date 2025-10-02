# llm/function_dispatcher.py
"""
Robust dispatcher that ensures stack_api is importable.
- tries plain import
- tries relative import
- if still not found, tries to locate stack_api.py in parent folders and load it via importlib
Provides:
    register_visualizer(kind_or_visualizer, visualizer=None)
    unregister_visualizer(kind_or_visualizer, visualizer=None)
    dispatch(name, arguments)
"""

import json
import weakref
import os
import importlib
import importlib.util
import re
from typing import Any, Dict, Optional

# Try to import stack_api robustly
stack_api = None

_ALIAS_MAP = {
    "push_to_stack": "stack_push",
    "push_stack": "stack_push",
    "push": "stack_push",
    "push_to_stack_v1": "stack_push",
    "pushstack": "stack_push",
    "pushstack_v1": "stack_push",
    "democlearstack": "stack_clear",
    "clearstack": "stack_clear",
    "clear": "stack_clear",
}

def _normalize_name(raw):
    """
    把模型可能返回的各种变体归一为 dispatcher 使用的内部 name。
    - camelCase -> snake_case
    - 去掉非法字符
    - 去掉 demo_、do_ 等前缀
    - 用 _ALIAS_MAP 进一步映射常见别名
    """
    if not isinstance(raw, str):
        return raw
    s = raw.strip()
    # camelCase -> snake_case
    s = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s)
    # 非法字符换成下划线
    s = re.sub(r'[^0-9a-zA-Z_]', '_', s).lower()
    s = re.sub(r'_+', '_', s).strip('_')
    # remove common prefixes
    s = re.sub(r'^(demo|do|action)_', '', s)
    # alias table
    return _ALIAS_MAP.get(s, s)

def _try_import_stack_api():
    global stack_api
    if stack_api is not None:
        return stack_api
    # 1) direct import
    try:
        import stack.stack_api as _m
        stack_api = _m
        return stack_api
    except Exception:
        pass
    # 2) relative import (if llm is a package inside project)
    try:
        # this will work if package layout is project_root/llm/function_dispatcher.py
        # and project_root (containing stack_api.py) is a package root
        from .. import stack_api as _m  # type: ignore
        stack_api = _m
        return stack_api
    except Exception:
        pass
    # 3) search upward for stack_api.py and load it dynamically
    try:
        this_file = os.path.abspath(__file__)
        cur = os.path.dirname(this_file)
        # search up to root (limit depth to avoid infinite loop)
        max_up = 6
        up = 0
        found = None
        while cur and up < max_up:
            candidate = os.path.join(cur, "stack_api.py")
            if os.path.isfile(candidate):
                found = candidate
                break
            parent = os.path.dirname(cur)
            if parent == cur:
                break
            cur = parent
            up += 1
        if found:
            spec = importlib.util.spec_from_file_location("stack_api", found)
            module = importlib.util.module_from_spec(spec)
            loader = spec.loader
            if loader is None:
                raise ImportError("spec.loader is None for stack_api")
            loader.exec_module(module)  # type: ignore
            # register into sys.modules under name 'stack_api'
            import sys
            sys.modules["stack_api"] = module
            stack_api = module
            return stack_api
    except Exception:
        pass
    # last resort: None
    return None

# initialize at import time
_try_import_stack_api()

# registry: kind -> weakref to visualizer instance
_registry: Dict[str, weakref.ref] = {}

def _safe_parse_args(arguments: Any) -> Any:
    if arguments is None:
        return {}
    if isinstance(arguments, str):
        try:
            return json.loads(arguments)
        except Exception:
            return {"__raw": arguments}
    return arguments

# ---------------- register / unregister ----------------
def register_visualizer(kind_or_visualizer, visualizer: Optional[object] = None) -> Dict[str, Any]:
    try:
        if visualizer is None:
            vis = kind_or_visualizer
            kind = "default"
        else:
            kind = str(kind_or_visualizer)
            vis = visualizer
        _registry[kind] = weakref.ref(vis)
        return {"ok": True, "message": f"registered visualizer for kind='{kind}'"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def unregister_visualizer(kind_or_visualizer, visualizer: Optional[object] = None) -> Dict[str, Any]:
    try:
        if visualizer is None:
            if isinstance(kind_or_visualizer, str):
                kind = kind_or_visualizer
                if kind in _registry:
                    _registry.pop(kind, None)
                    return {"ok": True, "message": f"unregistered kind='{kind}'"}
                return {"ok": False, "error": f"kind '{kind}' not found"}
            else:
                vis = kind_or_visualizer
                removed = []
                for k, wr in list(_registry.items()):
                    inst = wr()
                    if inst is None or inst is vis:
                        _registry.pop(k, None)
                        removed.append(k)
                if removed:
                    return {"ok": True, "message": f"unregistered keys: {removed}"}
                return {"ok": False, "error": "no matching visualizer found"}
        else:
            kind = str(kind_or_visualizer)
            if kind in _registry:
                _registry.pop(kind, None)
                return {"ok": True, "message": f"unregistered kind='{kind}'"}
            return {"ok": False, "error": f"kind '{kind}' not found"}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def _get_visualizer(kind: str):
    wr = _registry.get(kind)
    if wr is None:
        return None
    return wr()

# ---------------- alias map ----------------
_ALIAS_MAP = {
    "push_to_stack": "stack_push",
    "push_stack": "stack_push",
    "push": "stack_push",
    "push_to_stack_v1": "stack_push",
    # add more aliases as needed
}

# ---------------- dispatch ----------------
def dispatch(name: str, arguments: Any) -> Dict[str, Any]:
    """
    Dispatch model function call.
    """
    global stack_api
    # refresh stack_api if needed
    if stack_api is None:
        _try_import_stack_api()
    args = _safe_parse_args(arguments)
    if isinstance(name, str):
        name = _normalize_name(name)

    # Try stack-specific handlers first
    try:
        if name in ("stack_push", "push"):
            if stack_api is None:
                return {"ok": False, "error": "stack_api not available"}
            value = args.get("value") if isinstance(args, dict) and "value" in args else args
            return stack_api.push(value)

        if name in ("stack_pop", "pop"):
            if stack_api is None:
                return {"ok": False, "error": "stack_api not available"}
            return stack_api.pop()

        if name in ("stack_clear", "clear"):
            if stack_api is None:
                return {"ok": False, "error": "stack_api not available"}
            return stack_api.clear()

        if name in ("stack_batch_create", "batch_create"):
            if stack_api is None:
                return {"ok": False, "error": "stack_api not available"}
            vals = args.get("values") if isinstance(args, dict) and "values" in args else args
            if isinstance(vals, str):
                vals = [s.strip() for s in vals.split(",") if s.strip() != ""]
            return stack_api.batch_create(vals)

        if name in ("stack_get_state", "get_state"):
            if stack_api is None:
                return {"ok": False, "error": "stack_api not available"}
            return stack_api.get_state()
    except Exception as e:
        return {"ok": False, "error": f"stack dispatch error: {e}"}

    # Non-stack: try prefix lookup like linked_list_push -> kind 'linked_list'
    if "_" in name:
        prefix, suffix = name.split("_", 1)
        vis = _get_visualizer(prefix)
        if vis:
            return {
                "ok": True,
                "info": "visualizer_found",
                "kind": prefix,
                "method": suffix,
                "note": f"Visualizer for '{prefix}' is registered. Implement mapping for '{name}' in dispatcher if you want automatic dispatch."
            }
        else:
            return {"ok": False, "error": f"no visualizer registered for kind '{prefix}'"}

    return {"ok": False, "error": f"unknown function name: {name}"}
