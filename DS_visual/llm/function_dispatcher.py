import json
import weakref
import os
import importlib
import importlib.util
import re
from typing import Any, Dict, Optional
from llm.function_aliases import _ALIAS_MAP  


stack_api = None
sequence_api = None
linked_list_api = None

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

def _try_import_linked_list_api():
    global linked_list_api
    if linked_list_api is not None:
        return linked_list_api
    # 1) package import
    try:
        import linked_list.linked_list_api as _m
        linked_list_api = _m
        return linked_list_api
    except Exception:
        pass
    # 2) relative import
    try:
        from .. import linked_list_api as _m  # type: ignore
        linked_list_api = _m
        return linked_list_api
    except Exception:
        pass
    # 3) search upward for linked_list_api.py
    try:
        this_file = os.path.abspath(__file__)
        cur = os.path.dirname(this_file)
        max_up = 6
        up = 0
        found = None
        while cur and up < max_up:
            candidate = os.path.join(cur, "linked_list_api.py")
            if os.path.isfile(candidate):
                found = candidate
                break
            parent = os.path.dirname(cur)
            if parent == cur:
                break
            cur = parent
            up += 1
        if found:
            spec = importlib.util.spec_from_file_location("linked_list_api", found)
            module = importlib.util.module_from_spec(spec)
            loader = spec.loader
            if loader is None:
                raise ImportError("spec.loader is None for linked_list_api")
            loader.exec_module(module)  # type: ignore
            import sys
            sys.modules["linked_list_api"] = module
            linked_list_api = module
            return linked_list_api
    except Exception:
        pass
    return None

# attempt to initialize at import time (optional)
_try_import_stack_api()
_try_import_sequence_api()
_try_import_linked_list_api()

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

# ---------------- helpers ----------------
def _normalize_name(raw):
    """
    Normalize model returned function name:
    - convert camelCase -> snake_case
    - remove illegal chars -> underscores, lowercased
    - collapse repeated underscores
    - remove common prefixes demo/do/action_
    - apply alias map
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
    # alias
    return _ALIAS_MAP.get(s, s)

# ---------------- dispatch ----------------
def dispatch(name: str, arguments: Any) -> Dict[str, Any]:
    """
    Dispatch model function call. Returns a dict describing the outcome or API return.
    """
    global stack_api, sequence_api, linked_list_api
    # ensure api modules available (lazy)
    if stack_api is None:
        _try_import_stack_api()
    if sequence_api is None:
        _try_import_sequence_api()
    if linked_list_api is None:
        _try_import_linked_list_api()

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
            if hasattr(sequence_api, "insert_at"):
                res = sequence_api.insert_at(idx_int, val)
                print(f"dispatch -> sequence.insert_at result={res!r}")
                return res
            if hasattr(sequence_api, "insert_after"):
                res = sequence_api.insert_after(idx_int, val)
                print(f"dispatch -> sequence.insert_after result={res!r}")
                return res
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
            vals = None
            if isinstance(args, dict):
                vals = args.get("values") or args.get("elements") or args.get("data") or args.get("items")
            if vals is None and isinstance(args, (list, tuple)):
                vals = list(args)
            if vals is None:
                vals = args
            if isinstance(vals, str):
                vals = [s.strip() for s in vals.split(",") if s.strip() != ""]
            if hasattr(sequence_api, "batch_create"):
                res = sequence_api.batch_create(vals)
                print(f"dispatch -> sequence.batch_create result={res!r}")
                return res
            if hasattr(sequence_api, "create_from_list"):
                res = sequence_api.create_from_list(vals)
                print(f"dispatch -> sequence.create_from_list result={res!r}")
                return res
            if hasattr(sequence_api, "data"):
                try:
                    setattr(sequence_api, "data", list(vals))
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

    # ---------------- linked-list handlers ----------------
    try:
        if linked_list_api is None:
            _try_import_linked_list_api()

        # insert last / append
        if name in ("linked_list_insert_last", "linked_list_insert", "linked_list_insert_tail", "linked_list_add", "linked_list_push", "linked_list_append", "linked_list_insert_end", "linked_list_insert_tail"):
            if linked_list_api is None:
                # if the dedicated API not available, try calling registered visualizer programmatically
                vis = _get_visualizer("linked_list")
                if vis:
                    val = args.get("value") if isinstance(args, dict) and "value" in args else args
                    # try a few known method names on visualizer
                    for m in ("programmatic_insert_last", "create_list_from_string", "insert_last", "insert"):
                        if hasattr(vis, m):
                            try:
                                if m == "create_list_from_string" and isinstance(val, (list, tuple)):
                                    # join into comma string
                                    vis.batch_entry_var.set(",".join(map(str, val)))
                                    vis.create_list_from_string()
                                    return {"ok": True, "message": "created via visualizer.create_list_from_string"}
                                else:
                                    getattr(vis, m)(val)
                                    return {"ok": True, "message": f"invoked visualizer.{m}", "state": getattr(vis, "node_value_store", None)}
                            except Exception as e:
                                print("visualizer method call failed:", m, e)
                                continue
                return {"ok": False, "error": "linked_list_api and visualizer methods not available"}
            val = args.get("value") if isinstance(args, dict) and "value" in args else args
            res = None
            # prefer explicit API name
            if hasattr(linked_list_api, "insert_last"):
                res = linked_list_api.insert_last(val)
                print(f"dispatch -> linked_list_api.insert_last result={res!r}")
                return res
            # try common names
            for m in ("insert_last", "append", "push", "programmatic_insert_last"):
                if hasattr(linked_list_api, m):
                    res = getattr(linked_list_api, m)(val)
                    print(f"dispatch -> linked_list_api.{m} result={res!r}")
                    return res
            # fallback: if API exposes data list
            if hasattr(linked_list_api, "data") and isinstance(getattr(linked_list_api, "data"), list):
                getattr(linked_list_api, "data").append(val)
                return {"ok": True, "message": "appended raw to linked_list_api.data", "state": getattr(linked_list_api, "data")}
            return {"ok": False, "error": "linked_list_api missing insert/append method"}

        # insert at index (0-based)
        if name in ("linked_list_insert_at", "linked_list_insert_pos", "linked_list_insert_position", "linked_list_insert_index"):
            if linked_list_api is None:
                return {"ok": False, "error": "linked_list_api not available"}
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
            # try API
            if hasattr(linked_list_api, "insert_at"):
                res = linked_list_api.insert_at(idx_int, val)
                print(f"dispatch -> linked_list_api.insert_at result={res!r}")
                return res
            if hasattr(linked_list_api, "insert_after"):
                res = linked_list_api.insert_after(idx_int, val)
                print(f"dispatch -> linked_list_api.insert_after result={res!r}")
                return res
            # fallback mutate .data
            if hasattr(linked_list_api, "data") and isinstance(getattr(linked_list_api, "data"), list):
                data = getattr(linked_list_api, "data")
                if 0 <= idx_int <= len(data):
                    data.insert(idx_int, val)
                    return {"ok": True, "message": f"inserted at {idx_int} in raw data", "state": data}
                else:
                    return {"ok": False, "error": "index out of range for raw data insert"}
            return {"ok": False, "error": "linked_list_api missing insert_at method"}

        # delete at index
        if name in ("linked_list_delete_at", "linked_list_delete", "linked_list_remove_at"):
            if linked_list_api is None:
                return {"ok": False, "error": "linked_list_api not available"}
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
            if hasattr(linked_list_api, "pop"):
                res = linked_list_api.pop(idx_int)
                print(f"dispatch -> linked_list_api.pop result={res!r}")
                return res
            if hasattr(linked_list_api, "delete_at"):
                res = linked_list_api.delete_at(idx_int)
                print(f"dispatch -> linked_list_api.delete_at result={res!r}")
                return res
            if hasattr(linked_list_api, "data") and isinstance(getattr(linked_list_api, "data"), list):
                data = getattr(linked_list_api, "data")
                if 0 <= idx_int < len(data):
                    val = data.pop(idx_int)
                    return {"ok": True, "popped": val, "state": data}
                return {"ok": False, "error": "index out of range for raw data pop"}
            return {"ok": False, "error": "linked_list_api missing delete/pop method"}

        # clear linked list
        if name in ("linked_list_clear", "linked_list_clear_all", "linked_list_reset", "linked_list_empty"):
            if linked_list_api is None:
                # try visualizer-level clear
                vis = _get_visualizer("linked_list")
                if vis:
                    # try common visualizer clearing methods
                    for m in ("clear_visualization", "clear", "reset", "clear_all"):
                        if hasattr(vis, m):
                            try:
                                getattr(vis, m)()
                                return {"ok": True, "message": f"visualizer.{m} invoked"}
                            except Exception as e:
                                print("visualizer clear method failed:", m, e)
                                continue
                return {"ok": False, "error": "linked_list_api not available"}
            if hasattr(linked_list_api, "clear"):
                res = linked_list_api.clear()
                print(f"dispatch -> linked_list_api.clear result={res!r}")
                return res
            if hasattr(linked_list_api, "data") and isinstance(getattr(linked_list_api, "data"), list):
                getattr(linked_list_api, "data").clear()
                return {"ok": True, "message": "cleared raw data", "state": getattr(linked_list_api, "data")}
            return {"ok": False, "error": "linked_list_api missing clear method"}

        # batch create
        if name in ("linked_list_batch_create", "linked_list_create", "linked_list_build", "linked_list_create_from"):
            if linked_list_api is None:
                # try visualizer-level create_list_from_string
                vis = _get_visualizer("linked_list")
                if vis:
                    vals = args.get("values") if isinstance(args, dict) and "values" in args else args
                    if isinstance(vals, (list, tuple)):
                        vis.batch_entry_var.set(",".join(map(str, vals)))
                        vis.create_list_from_string()
                        return {"ok": True, "message": "created via visualizer.create_list_from_string"}
                    if isinstance(vals, str):
                        vis.batch_entry_var.set(vals)
                        vis.create_list_from_string()
                        return {"ok": True, "message": "created via visualizer.create_list_from_string"}
                return {"ok": False, "error": "linked_list_api not available"}
            vals = args.get("values") if isinstance(args, dict) and "values" in args else args
            if isinstance(vals, str):
                vals = [s.strip() for s in vals.split(",") if s.strip() != ""]
            if hasattr(linked_list_api, "batch_create"):
                res = linked_list_api.batch_create(vals)
                print(f"dispatch -> linked_list_api.batch_create result={res!r}")
                return res
            if hasattr(linked_list_api, "create_from_list"):
                res = linked_list_api.create_from_list(vals)
                print(f"dispatch -> linked_list_api.create_from_list result={res!r}")
                return res
            if hasattr(linked_list_api, "data"):
                try:
                    setattr(linked_list_api, "data", list(vals))
                    return {"ok": True, "message": "set raw data from batch_create", "state": getattr(linked_list_api, "data")}
                except Exception as e:
                    return {"ok": False, "error": f"failed to set raw data: {e}"}
            return {"ok": False, "error": "linked_list_api missing batch_create method"}

        # get state
        if name in ("linked_list_get_state", "get_linked_list_state"):
            if linked_list_api is None:
                # try visualizer read
                vis = _get_visualizer("linked_list")
                if vis:
                    state = getattr(vis, "node_value_store", None)
                    return {"ok": True, "state": state}
                return {"ok": False, "error": "linked_list_api not available"}
            if hasattr(linked_list_api, "get_state"):
                res = linked_list_api.get_state()
                print(f"dispatch -> linked_list_api.get_state result={res!r}")
                return res
            if hasattr(linked_list_api, "to_list"):
                res = linked_list_api.to_list()
                return {"ok": True, "state": res}
            if hasattr(linked_list_api, "data"):
                return {"ok": True, "state": getattr(linked_list_api, "data")}
            return {"ok": False, "error": "linked_list_api missing get_state/to_list/data"}
    except Exception as e:
        return {"ok": False, "error": f"linked_list dispatch error: {e}"}

    # ---------------- fallback: method prefix visualizer ----------------
    if isinstance(name, str) and "_" in name:
        prefix, suffix = name.split("_", 1)
        vis = _get_visualizer(prefix)
        if vis:
            # try to call suffix method on visualizer if exists
            # e.g., 'linked_list_insert' -> call vis.insert(...) or vis.programmatic_insert_last(...)
            try:
                # try direct method
                if hasattr(vis, suffix):
                    fn = getattr(vis, suffix)
                    try:
                        if isinstance(args, dict):
                            res = fn(**args)
                        else:
                            res = fn(args)
                        return {"ok": True, "message": f"invoked visualizer.{suffix}", "result": res}
                    except Exception as e:
                        return {"ok": False, "error": f"visualizer.{suffix} raised: {e}"}
                # try common mappings for suffix
                # e.g., suffix 'insert' -> programmatic_insert_last
                fallback_map = {
                    "insert": "programmatic_insert_last",
                    "insert_last": "programmatic_insert_last",
                    "insert_tail": "programmatic_insert_last",
                    "insert_first": "insert_node",
                    "create": "create_list_from_string",
                    "clear": "clear_visualization",
                    "delete": "delete_last_node"
                }
                mapped = fallback_map.get(suffix)
                if mapped and hasattr(vis, mapped):
                    fn = getattr(vis, mapped)
                    try:
                        if isinstance(args, dict):
                            res = fn(**args)
                        else:
                            res = fn(args)
                        return {"ok": True, "message": f"invoked visualizer.{mapped}", "result": res}
                    except Exception as e:
                        return {"ok": False, "error": f"visualizer.{mapped} raised: {e}"}
                return {
                    "ok": True,
                    "info": "visualizer_found",
                    "kind": prefix,
                    "method": suffix,
                    "note": f"Visualizer for '{prefix}' is registered but no auto-call mapping for '{name}'."
                }
            except Exception as e:
                return {"ok": False, "error": f"visualizer dispatch error: {e}"}
        else:
            return {"ok": False, "error": f"no visualizer registered for kind '{prefix}'"}

    # unknown function
    return {"ok": False, "error": f"unknown function name: {name}"}
