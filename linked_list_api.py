# linked_list_api.py
"""
Adapter for linked-list visualizer / model used by function_dispatcher.
Place this file in project root (or import path) so dispatcher can import it.

Design:
- bind_visualizer(vis) will be called by the visualizer (LinkList) to bind itself.
- Expose functions used by dispatcher:
    insert_last, insert_first, insert_at, pop/delete_at, clear, batch_create, get_state, info
- All UI actions are dispatched to Tk main thread via vis.window.after(0, callable).
"""

import importlib
import importlib.util
import os
import traceback
from typing import Any, List, Optional

_visualizer = None            # the LinkList instance (visualizer)
_model = None                 # optional model held by visualizer (if any)
_model_info = {"ok": False, "msg": "not initialized"}

# ---------------- binding ----------------
def bind_visualizer(vis):
    """
    Called by the visualizer to bind itself.
    Example in your LinkList.__init__(): linked_list_api.bind_visualizer(self)
    """
    global _visualizer, _model, _model_info
    try:
        _visualizer = vis
        # if visualizer exposes model attribute, keep reference
        if hasattr(vis, "model"):
            _model = getattr(vis, "model")
            _model_info = {"ok": True, "msg": "bound visualizer.model"}
        else:
            _model = None
            _model_info = {"ok": True, "msg": "bound visualizer (no model attribute)"}
        return {"ok": True, "message": "bound to visualizer"}
    except Exception as e:
        _visualizer = None
        _model = None
        _model_info = {"ok": False, "msg": f"bind failed: {e}"}
        return {"ok": False, "error": str(e)}

# helper to schedule call in Tk mainloop (safe UI invocation)
def _schedule_ui(func, *args, **kwargs):
    """
    Schedule func(*args, **kwargs) to run on the visualizer's Tk main loop.
    Returns True if scheduled, False otherwise.
    """
    if _visualizer is None:
        return False
    try:
        win = getattr(_visualizer, "window", None)
        if win is None:
            # maybe visualizer stores 'root' or different name
            win = getattr(_visualizer, "root", None)
        if win is None:
            return False
        # Use after(0, ...) to run as soon as possible on main thread
        win.after(0, lambda: func(*args, **kwargs))
        return True
    except Exception as e:
        print("linked_list_api._schedule_ui error:", e)
        return False

# ---------------- core operations ----------------
def insert_last(value: Any):
    """
    Insert value at tail. Prefer visualizer.programmatic_insert_last if present,
    otherwise try model methods or mutate model.node_value_store and schedule a refresh.
    """
    try:
        # If visualizer has a programmatic insertion (non-interactive) use it
        if _visualizer is not None and hasattr(_visualizer, "programmatic_insert_last"):
            scheduled = _schedule_ui(getattr(_visualizer, "programmatic_insert_last"), value)
            if scheduled:
                # also keep model list in sync if present
                try:
                    if _model is not None and hasattr(_model, "node_value_store"):
                        _model.node_value_store.append(str(value))
                except Exception:
                    pass
                return {"ok": True, "message": "inserted (scheduled programmatic_insert_last)", "result": None}
        # fallback: try model API-like methods
        if _model is not None:
            # try common names
            for name in ("insert_last", "append", "push", "add"):
                if hasattr(_model, name):
                    fn = getattr(_model, name)
                    try:
                        res = fn(value)
                        # schedule visual refresh if visualizer has clear_visualization or create_list_from_string
                        if _visualizer is not None and hasattr(_visualizer, "create_list_from_string"):
                            # rebuild visual from model state: set batch var and invoke create_list_from_string
                            vals = getattr(_model, "node_value_store", None) or getattr(_model, "data", None)
                            if isinstance(vals, (list, tuple)):
                                csv = ",".join(map(str, vals))
                                if hasattr(_visualizer, "batch_entry_var"):
                                    _schedule_ui(lambda: _visualizer.batch_entry_var.set(csv))
                                    _schedule_ui(getattr(_visualizer, "create_list_from_string"))
                        return {"ok": True, "message": "inserted (model method)", "result": res}
                    except Exception as e:
                        return {"ok": False, "error": f"model method {name} failed: {e}"}
        # last-resort: if visualizer exposes a node_value_store list, append and refresh via batch create
        if _visualizer is not None and hasattr(_visualizer, "node_value_store"):
            try:
                _visualizer.node_value_store.append(str(value))
                # rebuild visual by invoking create_list_from_string with constructed CSV
                if hasattr(_visualizer, "batch_entry_var") and hasattr(_visualizer, "create_list_from_string"):
                    csv = ",".join(_visualizer.node_value_store)
                    _schedule_ui(lambda: _visualizer.batch_entry_var.set(csv))
                    _schedule_ui(getattr(_visualizer, "create_list_from_string"))
                    return {"ok": True, "message": "inserted (mutated node_value_store and scheduled batch create)"}
            except Exception as e:
                return {"ok": False, "error": f"failed to append to visualizer store: {e}"}
        return {"ok": False, "error": "no method to insert_last found"}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def insert_first(value: Any):
    """
    Insert at head. If visualizer has only programmatic_insert_last, fallback by rebuilding:
    new_list = [value] + current_list -> clear_visualization -> batch_create.
    """
    try:
        # If visualizer exposes a direct method for insert_first, use it
        if _visualizer is not None and hasattr(_visualizer, "programmatic_insert_first"):
            scheduled = _schedule_ui(getattr(_visualizer, "programmatic_insert_first"), value)
            if scheduled:
                return {"ok": True, "message": "inserted at head (scheduled programmatic_insert_first)"}
        # else use model or rebuild approach
        # get current state
        cur = None
        if _model is not None:
            cur = getattr(_model, "node_value_store", None) or getattr(_model, "data", None)
        elif _visualizer is not None and hasattr(_visualizer, "node_value_store"):
            cur = list(getattr(_visualizer, "node_value_store"))
        if cur is None:
            # fallback to insert_last
            return insert_last(value)
        newlist = [str(value)] + list(cur)
        # schedule clear + batch create using visualizer's API if available
        if _visualizer is not None:
            if hasattr(_visualizer, "clear_visualization"):
                _schedule_ui(getattr(_visualizer, "clear_visualization"))
            if hasattr(_visualizer, "batch_entry_var") and hasattr(_visualizer, "create_list_from_string"):
                csv = ",".join(newlist)
                _schedule_ui(lambda: _visualizer.batch_entry_var.set(csv))
                _schedule_ui(getattr(_visualizer, "create_list_from_string"))
                # also try updating model if present
                if _model is not None and hasattr(_model, "node_value_store"):
                    try:
                        _model.node_value_store[:] = newlist
                    except Exception:
                        pass
                return {"ok": True, "message": "inserted at head (rebuilt via batch create)"}
        # otherwise try to mutate model directly
        if _model is not None and hasattr(_model, "node_value_store"):
            try:
                _model.node_value_store.insert(0, str(value))
                # attempt to refresh by scheduling visualizer.create_list_from_string if present
                if _visualizer is not None and hasattr(_visualizer, "create_list_from_string") and hasattr(_visualizer, "batch_entry_var"):
                    csv = ",".join(_model.node_value_store)
                    _schedule_ui(lambda: _visualizer.batch_entry_var.set(csv))
                    _schedule_ui(getattr(_visualizer, "create_list_from_string"))
                return {"ok": True, "message": "inserted at head (model updated)"}
            except Exception as e:
                return {"ok": False, "error": f"failed to insert into model store: {e}"}
        return {"ok": False, "error": "no method to insert_first found"}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def insert_at(index: int, value: Any):
    """
    Insert at given 0-based index. Strategy: rebuild list with insertion and invoke visualizer batch create.
    """
    try:
        # get current list
        cur = None
        if _model is not None:
            cur = getattr(_model, "node_value_store", None) or getattr(_model, "data", None)
        elif _visualizer is not None and hasattr(_visualizer, "node_value_store"):
            cur = list(getattr(_visualizer, "node_value_store"))
        if cur is None:
            return {"ok": False, "error": "no underlying list to insert into"}
        li = list(cur)
        if index < 0 or index > len(li):
            return {"ok": False, "error": "index out of range"}
        li.insert(int(index), str(value))
        # schedule rebuild
        if _visualizer is not None:
            if hasattr(_visualizer, "clear_visualization"):
                _schedule_ui(getattr(_visualizer, "clear_visualization"))
            if hasattr(_visualizer, "batch_entry_var") and hasattr(_visualizer, "create_list_from_string"):
                csv = ",".join(li)
                _schedule_ui(lambda: _visualizer.batch_entry_var.set(csv))
                _schedule_ui(getattr(_visualizer, "create_list_from_string"))
            if _model is not None and hasattr(_model, "node_value_store"):
                try:
                    _model.node_value_store[:] = li
                except Exception:
                    pass
            return {"ok": True, "message": "inserted at index (rebuild scheduled)", "state": li}
        # fallback: mutate model if possible
        if _model is not None and hasattr(_model, "node_value_store"):
            try:
                _model.node_value_store.insert(int(index), str(value))
                return {"ok": True, "message": "inserted into model store", "state": _model.node_value_store}
            except Exception as e:
                return {"ok": False, "error": str(e)}
        return {"ok": False, "error": "no method to insert_at found"}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def pop(index: Optional[int] = None):
    """
    Pop last if index is None, else delete at index.
    Uses visualizer.delete_last_node, delete_first_node, or delete_last_node(3) with delete_entry set.
    """
    try:
        if _visualizer is not None:
            # pop last
            if index is None:
                if hasattr(_visualizer, "delete_last_node"):
                    scheduled = _schedule_ui(getattr(_visualizer, "delete_last_node"), 0)
                    if scheduled:
                        # try to keep model in sync
                        try:
                            if _model is not None and hasattr(_model, "node_value_store") and len(_model.node_value_store) > 0:
                                popped = _model.node_value_store.pop()
                                return {"ok": True, "popped": popped}
                        except Exception:
                            pass
                        return {"ok": True, "message": "popped last (scheduled visualizer.delete_last_node)"}
            else:
                # delete at index
                idx = int(index)
                if idx == 0 and hasattr(_visualizer, "delete_first_node"):
                    scheduled = _schedule_ui(getattr(_visualizer, "delete_first_node"))
                    if scheduled:
                        try:
                            if _model is not None and hasattr(_model, "node_value_store"):
                                popped = _model.node_value_store.pop(0)
                                return {"ok": True, "popped": popped}
                        except Exception:
                            pass
                        return {"ok": True, "message": "deleted first (scheduled)"} 
                # use delete_last_node with locator=3 after setting delete_entry
                if hasattr(_visualizer, "delete_entry") and hasattr(_visualizer, "delete_last_node"):
                    # visualizer expects 1-based positions in delete_entry
                    try:
                        _schedule_ui(lambda idx1=idx: _visualizer.delete_entry.set(str(idx1 + 1)))
                        _schedule_ui(getattr(_visualizer, "delete_last_node"), 3)
                        try:
                            if _model is not None and hasattr(_model, "node_value_store"):
                                popped = _model.node_value_store.pop(idx)
                                return {"ok": True, "popped": popped}
                        except Exception:
                            pass
                        return {"ok": True, "message": "deleted at index (scheduled)"}
                    except Exception as e:
                        return {"ok": False, "error": str(e)}
        # fallback: mutate model
        if _model is not None and hasattr(_model, "node_value_store"):
            try:
                if index is None:
                    popped = _model.node_value_store.pop()
                else:
                    popped = _model.node_value_store.pop(int(index))
                # attempt to refresh UI by scheduling batch create
                if _visualizer is not None and hasattr(_visualizer, "batch_entry_var") and hasattr(_visualizer, "create_list_from_string"):
                    csv = ",".join(_model.node_value_store)
                    _schedule_ui(lambda: _visualizer.batch_entry_var.set(csv))
                    _schedule_ui(getattr(_visualizer, "create_list_from_string"))
                return {"ok": True, "popped": popped, "state": _model.node_value_store}
            except Exception as e:
                return {"ok": False, "error": str(e)}
        return {"ok": False, "error": "no method to pop/delete found"}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def clear():
    """
    Clear the linked list visualization and model.
    """
    try:
        # prefer visualizer clear function
        if _visualizer is not None and hasattr(_visualizer, "clear_visualization"):
            _schedule_ui(getattr(_visualizer, "clear_visualization"))
            # also clear underlying model store if present
            if _model is not None and hasattr(_model, "node_value_store"):
                try:
                    _model.node_value_store.clear()
                except Exception:
                    pass
            elif hasattr(_visualizer, "node_value_store"):
                try:
                    _visualizer.node_value_store.clear()
                except Exception:
                    pass
            return {"ok": True, "message": "cleared (scheduled visualizer.clear_visualization)", "state": getattr(_model or _visualizer, "node_value_store", None)}
        # fallback: mutate model
        if _model is not None and hasattr(_model, "node_value_store"):
            try:
                _model.node_value_store.clear()
                # schedule a UI refresh if possible
                if _visualizer is not None and hasattr(_visualizer, "batch_entry_var") and hasattr(_visualizer, "create_list_from_string"):
                    _schedule_ui(lambda: _visualizer.batch_entry_var.set(""))
                    _schedule_ui(getattr(_visualizer, "create_list_from_string"))
                return {"ok": True, "message": "cleared model", "state": _model.node_value_store}
            except Exception as e:
                return {"ok": False, "error": str(e)}
        return {"ok": False, "error": "no method to clear found"}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def batch_create(values):
    """
    Bulk-create the list from 'values' (list or comma-separated string).
    Prefer visualizer.create_list_from_string (which calls programmatic_insert_last internally).
    """
    try:
        vals = values
        if isinstance(vals, str):
            vals = [v.strip() for v in vals.split(",") if v.strip() != ""]
        if not isinstance(vals, (list, tuple)):
            vals = [vals]
        vals = list(map(str, vals))
        # If visualizer supports create_list_from_string and batch_entry_var, use it (best UX)
        if _visualizer is not None and hasattr(_visualizer, "batch_entry_var") and hasattr(_visualizer, "create_list_from_string"):
            csv = ",".join(vals)
            _schedule_ui(lambda: _visualizer.batch_entry_var.set(csv))
            _schedule_ui(getattr(_visualizer, "create_list_from_string"))
            # update model if present
            if _model is not None and hasattr(_model, "node_value_store"):
                try:
                    _model.node_value_store[:] = vals
                except Exception:
                    pass
            return {"ok": True, "message": "batch create scheduled via visualizer.create_list_from_string", "state": vals}
        # else, if visualizer offers programmatic_insert_last, call sequentially (scheduled)
        if _visualizer is not None and hasattr(_visualizer, "programmatic_insert_last"):
            # Clear existing visualization first if possible
            if hasattr(_visualizer, "clear_visualization"):
                _schedule_ui(getattr(_visualizer, "clear_visualization"))
            # schedule sequential calls with a small gap to avoid overlapping animations
            delay = 0
            for v in vals:
                _visualizer.window.after(delay, lambda vv=v: _visualizer.programmatic_insert_last(vv))
                delay += 200  # ms, rough spacing (programmatic_insert_last has its own sleeps)
            # update model store too
            if _model is not None and hasattr(_model, "node_value_store"):
                try:
                    _model.node_value_store[:] = vals
                except Exception:
                    pass
            return {"ok": True, "message": "batch create scheduled via programmatic_insert_last", "state": vals}
        # fallback: set model raw list then try to refresh visualizer via batch_entry_var/create_list_from_string if available
        if _model is not None and hasattr(_model, "node_value_store"):
            try:
                _model.node_value_store[:] = vals
                if _visualizer is not None and hasattr(_visualizer, "batch_entry_var") and hasattr(_visualizer, "create_list_from_string"):
                    _schedule_ui(lambda: _visualizer.batch_entry_var.set(",".join(vals)))
                    _schedule_ui(getattr(_visualizer, "create_list_from_string"))
                return {"ok": True, "message": "batch created (model updated)", "state": vals}
            except Exception as e:
                return {"ok": False, "error": str(e)}
        return {"ok": False, "error": "no method to perform batch_create"}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def get_state():
    """
    Return current linked-list state as Python list if possible.
    """
    try:
        if _model is not None:
            if hasattr(_model, "get_state"):
                try:
                    return {"ok": True, "state": _model.get_state()}
                except Exception:
                    pass
            if hasattr(_model, "node_value_store"):
                try:
                    return {"ok": True, "state": list(_model.node_value_store)}
                except Exception:
                    pass
            if hasattr(_model, "to_list"):
                try:
                    return {"ok": True, "state": _model.to_list()}
                except Exception:
                    pass
        if _visualizer is not None and hasattr(_visualizer, "node_value_store"):
            try:
                return {"ok": True, "state": list(_visualizer.node_value_store)}
            except Exception:
                pass
        return {"ok": False, "error": "no model/visualizer state available"}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def info():
    """
    Return info about adapter binding.
    """
    return {"ok": _visualizer is not None or _model is not None, "init": _model_info}
