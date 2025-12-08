# stack_api.py
"""
Programmatic API for controlling StackVisualizer from other modules (e.g. function_dispatcher).
All UI calls are scheduled via `visualizer.window.after(...)` so they run in Tk main thread.
We keep a weak reference to avoid preventing GC if window closes.
"""

import weakref
from typing import Any, Dict, List, Optional

_visualizer_ref: Optional[weakref.ref] = None

def register(visualizer) -> None:
    """Register the active StackVisualizer instance."""
    global _visualizer_ref
    try:
        _visualizer_ref = weakref.ref(visualizer)
    except Exception:
        # fallback to strong reference
        _visualizer_ref = lambda: visualizer

def unregister(visualizer) -> None:
    """Unregister the visualizer if it matches."""
    global _visualizer_ref
    if _visualizer_ref is None:
        return
    v = _visualizer_ref()
    if v is None:
        _visualizer_ref = None
    elif v is visualizer:
        _visualizer_ref = None

def _get_vis():
    if _visualizer_ref is None:
        return None
    return _visualizer_ref()

def _schedule_call(fn, *args, **kwargs):
    """
    Helper: schedule fn(*args, **kwargs) on the visualizer's Tk mainloop.
    Returns immediately a dict describing scheduling result.
    Note: the scheduled function itself is executed later and is responsible to update UI.
    """
    vis = _get_vis()
    if vis is None:
        return {"ok": False, "error": "Stack visualizer not registered (ui not running)."}
    try:
        vis.window.after(0, lambda: fn(*args, **kwargs))
        return {"ok": True, "message": "已调度到 UI 线程"}
    except Exception as e:
        return {"ok": False, "error": str(e)}

# ----------------- programmatic API functions -----------------

def push(value: Any) -> Dict[str, Any]:
    """Schedule a push of `value`. Returns immediately."""
    vis = _get_vis()
    if vis is None:
        return {"ok": False, "error": "Stack visualizer not registered."}
    return _schedule_call(lambda v=value: vis.animate_push_left(v))

def pop() -> Dict[str, Any]:
    """Schedule a pop (animate pop right)."""
    vis = _get_vis()
    if vis is None:
        return {"ok": False, "error": "Stack visualizer not registered."}
    return _schedule_call(lambda: vis.animate_pop_right())

def clear() -> Dict[str, Any]:
    """Schedule clearing the stack (animated)."""
    vis = _get_vis()
    if vis is None:
        return {"ok": False, "error": "Stack visualizer not registered."}
    return _schedule_call(lambda: vis.clear_stack())

def batch_create(values: List[Any]) -> Dict[str, Any]:
    """Schedule batch creation (values: list)."""
    vis = _get_vis()
    if vis is None:
        return {"ok": False, "error": "Stack visualizer not registered."}
    if not isinstance(values, (list, tuple)):
        return {"ok": False, "error": "values must be a list or tuple"}
    str_vals = [str(x) for x in values]
    def _start_batch():
        # set batch queue and start
        try:
            vis.batch_queue = str_vals
            vis.batch_index = 0
            vis._set_buttons_state("disabled")
            vis._batch_step()
        except Exception as e:
            # swallow errors in UI scheduling; they will show in UI logs if any
            pass
    return _schedule_call(lambda: _start_batch())

def get_state() -> Dict[str, Any]:
    """
    Return a snapshot of the current model state synchronously.
    NOTE: This will read vis.model.* attributes directly; make sure caller understands
    this is a best-effort snapshot (no locking).
    """
    vis = _get_vis()
    if vis is None:
        return {"ok": False, "error": "Stack visualizer not registered."}
    try:
        data = list(vis.model.data) if hasattr(vis.model, "data") else []
        top = getattr(vis.model, "top", len(data) - 1)
        capacity = getattr(vis, "capacity", None)
        return {"ok": True, "data": data, "top": top, "capacity": capacity}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def eval_postfix(expression: str) -> Dict[str, Any]:
    """
    Schedule postfix expression evaluation animation.
    Expression should be space-separated, e.g. "3 4 + 2 *" for (3+4)*2.
    Supported operators: + - * / % ^ **
    """
    vis = _get_vis()
    if vis is None:
        return {"ok": False, "error": "Stack visualizer not registered."}
    if not expression or not isinstance(expression, str):
        return {"ok": False, "error": "expression must be a non-empty string"}
    
    def _start_eval():
        try:
            if hasattr(vis, 'start_postfix_eval'):
                vis.start_postfix_eval(expression)
            else:
                from tkinter import messagebox
                messagebox.showerror("错误", "当前可视化器不支持后缀表达式求值")
        except Exception as e:
            pass
    
    return _schedule_call(lambda: _start_eval())


def bracket_match(expression: str) -> Dict[str, Any]:
    """
    Schedule bracket matching validation animation.
    Expression can contain any characters, brackets supported: ()[]{}
    Example: "{a+(b-c)*2}" or "[(a+b)*(c-d)]"
    """
    vis = _get_vis()
    if vis is None:
        return {"ok": False, "error": "Stack visualizer not registered."}
    if not expression or not isinstance(expression, str):
        return {"ok": False, "error": "expression must be a non-empty string"}
    
    def _start_match():
        try:
            if hasattr(vis, 'start_bracket_match'):
                vis.start_bracket_match(expression)
            else:
                from tkinter import messagebox
                messagebox.showerror("错误", "当前可视化器不支持括号匹配检验")
        except Exception as e:
            pass
    
    return _schedule_call(lambda: _start_match())


def open_dfs(vertex_count: int = 7, branch_factor: int = 2, start_vertex: str = "A") -> Dict[str, Any]:
    """
    Open DFS (Depth-First Search) visualization window.
    Uses stack to demonstrate graph traversal with DFS algorithm.
    
    Args:
        vertex_count: Number of vertices in the graph (5-10, default 7)
        branch_factor: Branch factor for each node (1-3, default 2)
        start_vertex: Starting vertex for DFS (default "A")
    """
    vis = _get_vis()
    if vis is None:
        return {"ok": False, "error": "Stack visualizer not registered."}
    
    # Validate parameters
    vertex_count = max(5, min(10, int(vertex_count)))
    branch_factor = max(1, min(3, int(branch_factor)))
    start_vertex = str(start_vertex).strip().upper()
    
    def _open_dfs():
        try:
            if hasattr(vis, '_open_dfs_visualizer'):
                vis._open_dfs_visualizer()
            else:
                from tkinter import messagebox
                messagebox.showerror("错误", "当前可视化器不支持DFS可视化")
        except Exception as e:
            pass
    
    return _schedule_call(lambda: _open_dfs())