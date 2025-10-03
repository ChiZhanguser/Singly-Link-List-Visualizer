# linked_list_api.py
import importlib
import importlib.util
import os
import traceback
import weakref
from typing import Any, Dict, Tuple

# singleton model + visualizer ref
_model = None
_visualizer_ref = None
_model_info = {"ok": False, "msg": "not initialized"}

def _init_model():
    global _model, _model_info
    if _model is not None:
        return

    tried = []
    candidates = [
        "linked_list.linked_list_model",
        "linked_list_model",
        "linked_list.model",
        "linked.list_model",
    ]
    for modname in candidates:
        try:
            mod = importlib.import_module(modname)
            # try known class names
            for cls_name in ("LinkedListModel", "LinkedList", "SinglyLinkedList"):
                if hasattr(mod, cls_name):
                    cls = getattr(mod, cls_name)
                    _model = cls()
                    _model_info = {"ok": True, "msg": f"instantiated {cls_name} from {modname}"}
                    return
            # try known instance names
            for inst_name in ("model", "linked_list", "linkedlist"):
                if hasattr(mod, inst_name):
                    _model = getattr(mod, inst_name)
                    _model_info = {"ok": True, "msg": f"got instance '{inst_name}' from {modname}"}
                    return
            tried.append(f"{modname} (no known class/instance)")
        except Exception as e:
            tried.append(f"{modname} -> {e}")

    # search upward for a file called linked_list_model.py
    this_dir = os.path.dirname(os.path.abspath(__file__))
    cur = this_dir
    max_up = 6
    up = 0
    found = None
    while up < max_up:
        candidate = os.path.join(cur, "linked_list", "linked_list_model.py")
        if os.path.isfile(candidate):
            found = candidate
            break
        candidate2 = os.path.join(cur, "linked_list_model.py")
        if os.path.isfile(candidate2):
            found = candidate2
            break
        parent = os.path.dirname(cur)
        if parent == cur:
            break
        cur = parent
        up += 1

    if found:
        try:
            spec = importlib.util.spec_from_file_location("linked_list_model_local", found)
            m = importlib.util.module_from_spec(spec)
            loader = spec.loader
            if loader is None:
                raise ImportError("loader None")
            loader.exec_module(m)
            for cls_name in ("LinkedListModel", "LinkedList", "SinglyLinkedList"):
                if hasattr(m, cls_name):
                    cls = getattr(m, cls_name)
                    _model = cls()
                    _model_info = {"ok": True, "msg": f"instantiated {cls_name} from file {found}"}
                    return
            for inst_name in ("model", "linked_list", "linkedlist"):
                if hasattr(m, inst_name):
                    _model = getattr(m, inst_name)
                    _model_info = {"ok": True, "msg": f"got instance {inst_name} from file {found}"}
                    return
        except Exception as e:
            tried.append(f"file {found} import error: {e}\n{traceback.format_exc()}")

    _model_info = {"ok": False, "msg": "could not locate LinkedListModel; tried: " + "; ".join(tried)}

# best-effort init
try:
    _init_model()
except Exception:
    pass

# ----- helper to call model methods -----
def _call_model_method(methods, *args, **kwargs) -> Tuple[bool, Any]:
    if _model is None:
        # try to init lazily
        _init_model()
        if _model is None:
            return False, "linked list model not available"
    for name in methods:
        if hasattr(_model, name):
            try:
                fn = getattr(_model, name)
                res = fn(*args, **kwargs)
                # after mutating model, ask visualizer to refresh if present
                _refresh_visualizer()
                return True, res
            except Exception as e:
                return False, f"method {name} raised: {e}"
    return False, f"no method found among: {methods}"

# ----- visualizer binding -----
def bind_visualizer(vis):
    """
    visualizer 应在初始化时调用本函数，将 visualizer 传入（visualizer 应有 .model 和 .window/.root 属性）。
    """
    global _visualizer_ref, _model, _model_info
    try:
        _visualizer_ref = weakref.ref(vis)
        if hasattr(vis, "model") and vis.model is not None:
            _model = vis.model
            _model_info = {"ok": True, "msg": "bound to visualizer.model"}
        return {"ok": True, "message": "linked_list_api bound to visualizer"}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def _get_visualizer():
    if _visualizer_ref is None:
        return None
    return _visualizer_ref()

def _refresh_visualizer():
    vis = _get_visualizer()
    if vis is None:
        return
    try:
        # schedule UI update in tkinter mainloop
        if hasattr(vis, "window") and hasattr(vis.window, "after"):
            vis.window.after(0, lambda: getattr(vis, "update_display", lambda: None)())
        elif hasattr(vis, "root") and hasattr(vis.root, "after"):
            vis.root.after(0, lambda: getattr(vis, "update_display", lambda: None)())
        else:
            # try direct call (best-effort)
            try:
                vis.update_display()
            except Exception:
                pass
    except Exception:
        pass

# ----- exported API functions -----
def insert_last(value):
    ok, res = _call_model_method(["insert_last", "append", "push", "add", "insert_tail"], value)
    if not ok:
        return {"ok": False, "error": res}
    return {"ok": True, "message": "inserted", "result": res, "state": getattr(_model, "to_list", lambda: getattr(_model, "data", None))() if hasattr(_model, "to_list") else getattr(_model, "data", None)}

def insert_first(value):
    ok, res = _call_model_method(["insert_first", "insert_head", "prepend"], value)
    if not ok:
        # fallback: insert_at(0)
        ok2, res2 = _call_model_method(["insert_at", "insert"], 0, value)
        if ok2:
            return {"ok": True, "message": "inserted at head (via insert_at)", "result": res2, "state": getattr(_model, "data", None)}
        return {"ok": False, "error": res}
    return {"ok": True, "message": "inserted_first", "result": res, "state": getattr(_model, "data", None)}

def insert_at(index, value):
    ok, res = _call_model_method(["insert_at", "insert_after", "insert"], index, value)
    if not ok:
        # try insert_after with index-1 (if model expects node/index variations)
        try:
            ok2, res2 = _call_model_method(["insert_after"], index-1, value)
            if ok2:
                return {"ok": True, "message": "inserted (via insert_after)", "result": res2, "state": getattr(_model, "data", None)}
        except Exception:
            pass
        return {"ok": False, "error": res}
    return {"ok": True, "message": "inserted", "result": res, "state": getattr(_model, "data", None)}

def pop(index=None):
    if index is None:
        ok, res = _call_model_method(["pop", "remove_last", "delete_last"], )
        if not ok:
            # try pop(-1)
            ok2, res2 = _call_model_method(["pop"], -1)
            if ok2:
                return {"ok": True, "popped": res2, "state": getattr(_model, "data", None)}
            return {"ok": False, "error": res}
        return {"ok": True, "popped": res, "state": getattr(_model, "data", None)}
    else:
        ok, res = _call_model_method(["pop", "delete_at", "remove_at"], int(index))
        if not ok:
            return {"ok": False, "error": res}
        return {"ok": True, "popped": res, "state": getattr(_model, "data", None)}

def clear():
    ok, res = _call_model_method(["clear", "reset", "remove_all"], )
    if not ok:
        return {"ok": False, "error": res}
    return {"ok": True, "message": "cleared", "state": getattr(_model, "data", None)}

def batch_create(values):
    if not isinstance(values, (list, tuple)):
        if isinstance(values, str):
            values = [v.strip() for v in values.split(",") if v.strip()]
        else:
            values = [values]
    ok, res = _call_model_method(["batch_create", "create_from_list", "from_list", "load_list"], values)
    if ok:
        return {"ok": True, "message": "batch created", "state": getattr(_model, "data", None)}
    # fallback try to set data
    if _model is not None and hasattr(_model, "data"):
        try:
            setattr(_model, "data", list(values))
            _refresh_visualizer()
            return {"ok": True, "message": "set raw .data", "state": getattr(_model, "data", None)}
        except Exception as e:
            return {"ok": False, "error": f"failed to set raw data: {e}"}
    return {"ok": False, "error": "no batch_create and cannot set raw data"}

def get_state():
    if _model is None:
        return {"ok": False, "error": "linked list model not available"}
    if hasattr(_model, "get_state"):
        try:
            return {"ok": True, "state": _model.get_state()}
        except Exception:
            pass
    if hasattr(_model, "to_list"):
        try:
            return {"ok": True, "state": _model.to_list()}
        except Exception:
            pass
    if hasattr(_model, "data"):
        try:
            return {"ok": True, "state": list(getattr(_model, "data"))}
        except Exception:
            pass
    return {"ok": True, "state": repr(_model)}

def info():
    return {"ok": _model is not None, "init": _model_info}
