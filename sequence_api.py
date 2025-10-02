# sequence_api.py
import importlib
import importlib.util
import os
import traceback
import time

# singleton model instance (will be set by _init_model or by external binding)
_model = None
_model_info = {"ok": False, "msg": "not initialized"}

# optional visualizer instance (if a GUI visualizer wants to bind itself)
_visualizer = None

def bind_visualizer(vis):
    """外部（visualizer）调用以绑定 visualizer 实例（同时把 model 共享给 sequence_api）"""
    global _visualizer, _model, _model_info
    _visualizer = vis
    try:
        if hasattr(vis, "model"):
            _model = vis.model
            _model_info = {"ok": True, "msg": "bound to visualizer.model"}
        else:
            _model_info = {"ok": True, "msg": "bound to visualizer instance (no .model found)"}
    except Exception as e:
        _model_info = {"ok": False, "msg": f"bind_visualizer error: {e}"}

def _maybe_refresh_visualizer():
    """如果 visualizer 绑定了并且提供 update_display，调用它以刷新画面"""
    try:
        if _visualizer is not None:
            fn = getattr(_visualizer, "update_display", None)
            if callable(fn):
                # small delay to let model change settle (可按需删掉)
                try:
                    fn()
                except Exception:
                    # 有时 UI 线程限制，visualizer.update_display 需要在主线程调用
                    # 我们尽量在 visualizer 里做线程安全处理，若不行，visualizer 可以自行轮询 model
                    pass
    except Exception:
        pass

def _init_model():
    global _model, _model_info
    if _model is not None:
        return

    tried = []
    candidates = [
        "sequence_list.sequence_list_model",
        "sequence.sequence_list_model",
        "sequence_list_model",
        "sequence_list.model",
        "sequence.model",
    ]
    for modname in candidates:
        try:
            mod = importlib.import_module(modname)
            for cls_name in ("SequenceListModel", "SequenceModel", "SequenceList"):
                if hasattr(mod, cls_name):
                    cls = getattr(mod, cls_name)
                    _model = cls()
                    _model_info = {"ok": True, "msg": f"instantiated {cls_name} from {modname}"}
                    return
            for inst_name in ("model", "sequence", "sequence_model"):
                if hasattr(mod, inst_name):
                    _model = getattr(mod, inst_name)
                    _model_info = {"ok": True, "msg": f"got instance '{inst_name}' from {modname}"}
                    return
            tried.append(f"{modname} (no known class/instance)")
        except Exception as e:
            tried.append(f"{modname} -> {e}")
            continue

    # search upward for file fallback (保持原逻辑)
    this_dir = os.path.dirname(os.path.abspath(__file__))
    cur = this_dir
    max_up = 5
    up = 0
    found = None
    while up < max_up:
        candidate = os.path.join(cur, "sequence_list", "sequence_list_model.py")
        if os.path.isfile(candidate):
            found = candidate
            break
        candidate2 = os.path.join(cur, "sequence_list_model.py")
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
            spec = importlib.util.spec_from_file_location("sequence_list_model_local", found)
            m = importlib.util.module_from_spec(spec)
            loader = spec.loader
            if loader is None:
                raise ImportError("loader None")
            loader.exec_module(m)
            for cls_name in ("SequenceListModel", "SequenceModel", "SequenceList"):
                if hasattr(m, cls_name):
                    cls = getattr(m, cls_name)
                    _model = cls()
                    _model_info = {"ok": True, "msg": f"instantiated {cls_name} from file {found}"}
                    return
            for inst_name in ("model", "sequence", "sequence_model"):
                if hasattr(m, inst_name):
                    _model = getattr(m, inst_name)
                    _model_info = {"ok": True, "msg": f"got instance {inst_name} from file {found}"}
                    return
        except Exception as e:
            tried.append(f"file {found} import error: {e}\n{traceback.format_exc()}")

    _model_info = {"ok": False, "msg": "could not locate SequenceListModel; tried: " + "; ".join(tried)}

# best-effort init
try:
    _init_model()
except Exception:
    pass

def _call_model_method(methods, *args, **kwargs):
    if _model is None:
        return False, "sequence model not available"
    for name in methods:
        if hasattr(_model, name):
            try:
                fn = getattr(_model, name)
                res = fn(*args, **kwargs)
                return True, res
            except Exception as e:
                return False, f"method {name} raised: {e}"
    return False, f"no method found among: {methods}"

# ---------- exported API ----------
def insert_last(value):
    ok, res = _call_model_method(["insert_last", "append", "insert_last_value", "add", "push"], value)
    if not ok:
        return {"ok": False, "error": res}
    # 刷新 visualizer（如果有绑定）
    _maybe_refresh_visualizer()
    try:
        state = getattr(_model, "data", None)
        return {"ok": True, "message": "inserted", "result": res, "state": state}
    except Exception:
        return {"ok": True, "message": "inserted", "result": res}

def insert_at(index, value):
    ok, res = _call_model_method(["insert_at", "insert", "insert_after", "insert_after_index"], index, value)
    if not ok:
        ok2, res2 = _call_model_method(["insert_after"], index - 1, value)
        if ok2:
            _maybe_refresh_visualizer()
            return {"ok": True, "message": "inserted (via insert_after)", "result": res2, "state": getattr(_model, "data", None)}
        return {"ok": False, "error": res}
    _maybe_refresh_visualizer()
    return {"ok": True, "message": "inserted", "result": res, "state": getattr(_model, "data", None)}

def pop(index=None):
    if index is None:
        ok, res = _call_model_method(["pop", "remove_last", "delete_last"], )
        if not ok:
            ok2, res2 = _call_model_method(["pop"], -1)
            if ok2:
                _maybe_refresh_visualizer()
                return {"ok": True, "popped": res2, "state": getattr(_model, "data", None)}
            return {"ok": False, "error": res}
        _maybe_refresh_visualizer()
        return {"ok": True, "popped": res, "state": getattr(_model, "data", None)}
    else:
        ok, res = _call_model_method(["pop", "delete_at", "remove_at"], int(index))
        if not ok:
            return {"ok": False, "error": res}
        _maybe_refresh_visualizer()
        return {"ok": True, "popped": res, "state": getattr(_model, "data", None)}

def clear():
    ok, res = _call_model_method(["clear", "reset", "remove_all"])
    if not ok:
        # 尝试直接清空 data
        if _model is not None and hasattr(_model, "data"):
            try:
                getattr(_model, "data").clear()
                _maybe_refresh_visualizer()
                return {"ok": True, "message": "cleared raw data", "state": getattr(_model, "data", None)}
            except Exception as e:
                return {"ok": False, "error": str(e)}
        return {"ok": False, "error": res}
    _maybe_refresh_visualizer()
    return {"ok": True, "message": "cleared", "state": getattr(_model, "data", None)}

def batch_create(values):
    if not isinstance(values, (list, tuple)):
        if isinstance(values, str):
            values = [v.strip() for v in values.split(",") if v.strip()]
        else:
            values = [values]
    ok, res = _call_model_method(["batch_create", "create_from_list", "from_list", "load_list"], values)
    if ok:
        _maybe_refresh_visualizer()
        return {"ok": True, "message": "batch created", "state": getattr(_model, "data", None)}
    if _model is not None and hasattr(_model, "data"):
        try:
            setattr(_model, "data", list(values))
            if hasattr(_model, "length"):
                try:
                    setattr(_model, "length", len(values))
                except Exception:
                    pass
            _maybe_refresh_visualizer()
            return {"ok": True, "message": "set raw .data", "state": getattr(_model, "data", None)}
        except Exception as e:
            return {"ok": False, "error": f"failed to set raw data: {e}"}
    return {"ok": False, "error": "no batch_create and cannot set raw data"}

def get_state():
    if _model is None:
        return {"ok": False, "error": "sequence model not available"}
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
