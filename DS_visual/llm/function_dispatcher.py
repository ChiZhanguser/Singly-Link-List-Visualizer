# llm/function_dispatcher.py
"""
Robust dispatcher that ensures stack_api and sequence_api are importable.
- tries plain import
- tries relative import
- if still not found, tries to locate *_api.py in parent folders and load it via importlib

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

# ----------------- backend modules (lazy-loaded) -----------------
stack_api = None
sequence_api = None

def _try_import_stack_api():
    global stack_api
    if stack_api is not None:
        return stack_api
    # 1) package import
    try:
        import stack.stack_api as _m
        stack_api = _m
        return stack_api
    except Exception:
        pass
    # 2) relative import
    try:
        from .. import stack_api as _m  # type: ignore
        stack_api = _m
        return stack_api
    except Exception:
        pass
    # 3) search upward for stack_api.py
    try:
        this_file = os.path.abspath(__file__)
        cur = os.path.dirname(this_file)
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
            import sys
            sys.modules["stack_api"] = module
            stack_api = module
            return stack_api
    except Exception:
        pass
    return None

def _try_import_sequence_api():
    global sequence_api
    if sequence_api is not None:
        return sequence_api
    # 1) package import
    try:
        import sequence.sequence_api as _m
        sequence_api = _m
        return sequence_api
    except Exception:
        pass
    # 2) relative import
    try:
        from .. import sequence_api as _m  # type: ignore
        sequence_api = _m
        return sequence_api
    except Exception:
        pass
    # 3) search upward for sequence_api.py
    try:
        this_file = os.path.abspath(__file__)
        cur = os.path.dirname(this_file)
        max_up = 6
        up = 0
        found = None
        while cur and up < max_up:
            candidate = os.path.join(cur, "sequence_api.py")
            if os.path.isfile(candidate):
                found = candidate
                break
            parent = os.path.dirname(cur)
            if parent == cur:
                break
            cur = parent
            up += 1
        if found:
            spec = importlib.util.spec_from_file_location("sequence_api", found)
            module = importlib.util.module_from_spec(spec)
            loader = spec.loader
            if loader is None:
                raise ImportError("spec.loader is None for sequence_api")
            loader.exec_module(module)  # type: ignore
            import sys
            sys.modules["sequence_api"] = module
            sequence_api = module
            return sequence_api
    except Exception:
        pass
    return None

# attempt to initialize at import time (optional)
_try_import_stack_api()
_try_import_sequence_api()

# registry: kind -> weakref to visualizer instance
_registry: Dict[str, weakref.ref] = {}

def _safe_parse_args(arguments: Any) -> Any:
    if arguments is None:
        return {}
    if isinstance(arguments, str):
        try:
            return json.loads(arguments)
        except Exception:
            # keep raw string for downstream handling
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
    # stack aliases
    "push_to_stack": "stack_push",
    "push_stack": "stack_push",
    "push": "stack_push",
    "push_to_stack_v1": "stack_push",
    "pushstack": "stack_push",
    "pushstack_v1": "stack_push",
    "democlearstack": "stack_clear",
    "clearstack": "stack_clear",
    "clear": "stack_clear",

    # sequence / list aliases -> normalize
    "list_insert": "sequence_insert_last",
    "list_append": "sequence_insert_last",
    "list_push": "sequence_insert_last",
    "list_add": "sequence_insert_last",
    "insert_into_list": "sequence_insert_last",
    "seq_list_insert": "sequence_insert_last",
    "sequence_insert": "sequence_insert_last",
    "list_insert_at": "sequence_insert_at",
    "list_insert_pos": "sequence_insert_at",
    "list_insert_position": "sequence_insert_at",
    "list_delete": "sequence_delete_at",
    "list_remove": "sequence_delete_at",
    "seq_list_delete": "sequence_delete_at",
    "list_clear": "sequence_clear",
    "sequenceclear": "sequence_clear",
    "build_list": "sequence_batch_create",
    "sequence_batch_create": "sequence_batch_create",
    "get_list_state": "sequence_get_state",

    # additional common variants for batch/create/clear
    "create_sequence_list": "sequence_batch_create",
    "create_list": "sequence_batch_create",
    "create_seq_list": "sequence_batch_create",
    "build_sequence": "sequence_batch_create",
    "create_sequence": "sequence_batch_create",
    "elements_to_list": "sequence_batch_create",
    "clear_sequence_list": "sequence_clear",
    "clear_list_sequence": "sequence_clear",
}

# ---------------- helpers ----------------
def _normalize_name(raw):
    """
    Normalize model returned function name:
    - convert camelCase -> snake_case
    - remove illegal chars -> underscores, lowercased
    - collapse repeated underscores
    - remove common prefixes demo/do/action_
    - apply alias map and simple keyword-based fallbacks
    """
    if not isinstance(raw, str):
        return raw
    s = raw.strip()
    # camelCase -> snake_case
    s = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s)
    # non-alnum -> underscore
    s = re.sub(r'[^0-9a-zA-Z_]', '_', s).lower()
    s = re.sub(r'_+', '_', s).strip('_')
    # remove prefixes
    s = re.sub(r'^(demo|do|action)_', '', s)

    # alias lookup
    if s in _ALIAS_MAP:
        return _ALIAS_MAP[s]

    # keyword-based fallbacks to improve robustness
    if 'sequence' in s or 'list' in s or 'seq' in s:
        if 'clear' in s:
            return 'sequence_clear'
        if any(k in s for k in ('batch', 'create', 'build', 'elements', 'create_list', 'create_sequence')):
            return 'sequence_batch_create'
        if any(k in s for k in ('insert', 'append', 'push', 'add')) and any(k in s for k in ('at', 'pos', 'position', 'index')):
            return 'sequence_insert_at'
        if any(k in s for k in ('insert', 'append', 'push', 'add')) :
            return 'sequence_insert_last'
        if any(k in s for k in ('delete', 'remove', 'pop')):
            return 'sequence_delete_at'
        if any(k in s for k in ('get', 'state', 'to_list', 'get_state')):
            return 'sequence_get_state'

    # stack-specific simple fallbacks
    if 'stack' in s:
        if any(k in s for k in ('push', 'push_to_stack', 'pushstack')):
            return 'stack_push'
        if any(k in s for k in ('pop', 'stack_pop')):
            return 'stack_pop'
        if 'clear' in s:
            return 'stack_clear'
        if any(k in s for k in ('batch', 'create')):
            return 'stack_batch_create'
        if any(k in s for k in ('get', 'state')):
            return 'stack_get_state'

    return s

# ---------------- dispatch ----------------
def dispatch(name: str, arguments: Any) -> Dict[str, Any]:
    """
    Dispatch model function call. Returns a dict describing the outcome or API return.
    """
    global stack_api, sequence_api
    # ensure api modules available (lazy)
    if stack_api is None:
        _try_import_stack_api()
    if sequence_api is None:
        _try_import_sequence_api()

    args = _safe_parse_args(arguments)
    if isinstance(name, str):
        name = _normalize_name(name)

    # debug print
    try:
        print(f"dispatch -> name={name!r}, arguments={args!r}")
    except Exception:
        pass

    # ---------------- stack handlers ----------------
    try:
        if name in ("stack_push", "push"):
            if stack_api is None:
                return {"ok": False, "error": "stack_api not available"}
            value = args.get("value") if isinstance(args, dict) and "value" in args else args
            res = stack_api.push(value)
            print(f"dispatch -> stack_push result={res!r}")
            return res

        if name in ("stack_pop", "pop"):
            if stack_api is None:
                return {"ok": False, "error": "stack_api not available"}
            res = stack_api.pop()
            print(f"dispatch -> stack_pop result={res!r}")
            return res

        if name in ("stack_clear", "clear"):
            if stack_api is None:
                return {"ok": False, "error": "stack_api not available"}
            res = stack_api.clear()
            print(f"dispatch -> stack_clear result={res!r}")
            return res

        if name in ("stack_batch_create", "batch_create"):
            if stack_api is None:
                return {"ok": False, "error": "stack_api not available"}
            vals = args.get("values") if isinstance(args, dict) and "values" in args else args
            if isinstance(vals, str):
                vals = [s.strip() for s in vals.split(",") if s.strip() != ""]
            res = stack_api.batch_create(vals)
            print(f"dispatch -> stack_batch_create result={res!r}")
            return res

        if name in ("stack_get_state", "get_state"):
            if stack_api is None:
                return {"ok": False, "error": "stack_api not available"}
            res = stack_api.get_state()
            print(f"dispatch -> stack_get_state result={res!r}")
            return res
    except Exception as e:
        return {"ok": False, "error": f"stack dispatch error: {e}"}

    # ---------------- sequence handlers ----------------
    try:
        # ensure sequence_api loaded
        if sequence_api is None:
            _try_import_sequence_api()

        if name in ("sequence_insert_last", "sequence_insert", "insert_last", "insert"):
            if sequence_api is None:
                return {"ok": False, "error": "sequence_api not available"}
            value = args.get("value") if isinstance(args, dict) and "value" in args else args
            # try common methods
            if hasattr(sequence_api, "insert_last"):
                res = sequence_api.insert_last(value)
                print(f"dispatch -> sequence.insert_last result={res!r}")
                return res
            if hasattr(sequence_api, "append"):
                res = sequence_api.append(value)
                print(f"dispatch -> sequence.append result={res!r}")
                return res
            if hasattr(sequence_api, "push"):
                res = sequence_api.push(value)
                print(f"dispatch -> sequence.push result={res!r}")
                return res
            # fallback: if model object exposes `data` list, try to append
            if hasattr(sequence_api, "data") and isinstance(getattr(sequence_api, "data"), list):
                getattr(sequence_api, "data").append(value)
                return {"ok": True, "message": "appended raw to sequence_api.data", "state": getattr(sequence_api, "data")}
            return {"ok": False, "error": "sequence_api missing insert/append method"}

        if name in ("sequence_insert_at", "sequence_insert_pos", "insert_at"):
            if sequence_api is None:
                return {"ok": False, "error": "sequence_api not available"}
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
            # prefer 0-based API; caller may send 1-based — try to be tolerant
            # If sequence_api has insert_at(index, value) or insert_after etc.
            if hasattr(sequence_api, "insert_at"):
                res = sequence_api.insert_at(idx_int, val)
                print(f"dispatch -> sequence.insert_at result={res!r}")
                return res
            if hasattr(sequence_api, "insert_after"):
                res = sequence_api.insert_after(idx_int, val)
                print(f"dispatch -> sequence.insert_after result={res!r}")
                return res
            # if underlying model exposes .data, attempt insertion
            if hasattr(sequence_api, "data") and isinstance(getattr(sequence_api, "data"), list):
                data = getattr(sequence_api, "data")
                if 0 <= idx_int <= len(data):
                    data.insert(idx_int, val)
                    return {"ok": True, "message": f"inserted at {idx_int} in raw data", "state": data}
                else:
                    return {"ok": False, "error": "index out of range for raw data insert"}
            return {"ok": False, "error": "sequence_api missing insert_at method"}

        if name in ("sequence_delete_at", "sequence_delete", "delete_at", "remove_at"):
            if sequence_api is None:
                return {"ok": False, "error": "sequence_api not available"}
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
            if hasattr(sequence_api, "pop"):
                res = sequence_api.pop(idx_int)
                print(f"dispatch -> sequence.pop result={res!r}")
                return res
            if hasattr(sequence_api, "delete_at"):
                res = sequence_api.delete_at(idx_int)
                print(f"dispatch -> sequence.delete_at result={res!r}")
                return res
            # fallback mutate raw data
            if hasattr(sequence_api, "data") and isinstance(getattr(sequence_api, "data"), list):
                data = getattr(sequence_api, "data")
                if 0 <= idx_int < len(data):
                    val = data.pop(idx_int)
                    return {"ok": True, "popped": val, "state": data}
                return {"ok": False, "error": "index out of range for raw data pop"}
            return {"ok": False, "error": "sequence_api missing delete/pop method"}

        if name in ("sequence_clear", "clear_sequence", "clear_list", "clear_sequence_list"):
            if sequence_api is None:
                return {"ok": False, "error": "sequence_api not available"}
            if hasattr(sequence_api, "clear"):
                res = sequence_api.clear()
                print(f"dispatch -> sequence.clear result={res!r}")
                return res
            if hasattr(sequence_api, "data") and isinstance(getattr(sequence_api, "data"), list):
                getattr(sequence_api, "data").clear()
                return {"ok": True, "message": "cleared raw data", "state": getattr(sequence_api, "data")}
            return {"ok": False, "error": "sequence_api missing clear method"}

        if name in ("sequence_batch_create", "batch_create_sequence", "batch_create",
                    "create_sequence_list", "create_list", "create_seq_list", "build_list",
                    "create_sequence", "build_sequence"):
            if sequence_api is None:
                return {"ok": False, "error": "sequence_api not available"}
            # 从多种可能的 key 中提取列表：values / elements / data / items
            vals = None
            if isinstance(args, dict):
                vals = args.get("values") or args.get("elements") or args.get("data") or args.get("items") or args.get("elements_list")
            # 如果 args 本身就是 list/tuple
            if vals is None and isinstance(args, (list, tuple)):
                vals = list(args)
            # 如果还是 None，直接使用 args（可能是字符串或其他）
            if vals is None:
                vals = args

            # 如果是字符串，按逗号切分
            if isinstance(vals, str):
                vals = [s.strip() for s in vals.split(",") if s.strip() != ""]

            # 调用 backend
            if hasattr(sequence_api, "batch_create"):
                res = sequence_api.batch_create(vals)
                print(f"dispatch -> sequence.batch_create result={res!r}")
                return res
            if hasattr(sequence_api, "create_from_list"):
                res = sequence_api.create_from_list(vals)
                print(f"dispatch -> sequence.create_from_list result={res!r}")
                return res
            # fallback: 尝试设置 raw data
            if hasattr(sequence_api, "data"):
                try:
                    setattr(sequence_api, "data", list(vals) if isinstance(vals, (list, tuple)) else [vals])
                    return {"ok": True, "message": "set raw data from batch_create", "state": getattr(sequence_api, "data")}
                except Exception as e:
                    return {"ok": False, "error": f"failed to set raw data: {e}"}
            return {"ok": False, "error": "sequence_api missing batch_create method"}

        if name in ("sequence_get_state", "get_sequence_state", "get_list_state"):
            if sequence_api is None:
                return {"ok": False, "error": "sequence_api not available"}
            if hasattr(sequence_api, "get_state"):
                res = sequence_api.get_state()
                print(f"dispatch -> sequence.get_state result={res!r}")
                return res
            if hasattr(sequence_api, "to_list"):
                res = sequence_api.to_list()
                print(f"dispatch -> sequence.to_list result={res!r}")
                return {"ok": True, "state": res}
            if hasattr(sequence_api, "data"):
                return {"ok": True, "state": getattr(sequence_api, "data")}
            return {"ok": False, "error": "sequence_api missing get_state/to_list/data"}
    except Exception as e:
        return {"ok": False, "error": f"sequence dispatch error: {e}"}

    # ---------------- fallback: method prefix visualizer ----------------
    if isinstance(name, str) and "_" in name:
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

    # unknown function
    return {"ok": False, "error": f"unknown function name: {name}"}
