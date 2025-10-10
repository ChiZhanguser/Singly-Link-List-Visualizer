# DSL_utils/bst_dsl.py
from tkinter import messagebox

def _split_items_from_args(args):
    items = []
    for tok in args:
        if not tok:
            continue
        # tok: "1,2,3" 或 "1" 或 "1,2" 或 "10"
        parts = [p.strip() for p in tok.split(",") if p.strip() != ""]
        if parts:
            items.extend(parts)
    return items

def process(vis, text):
    if not vis or not text:
        return
    t = text.strip()
    if getattr(vis, "animating", False):
        messagebox.showinfo("提示", "当前正在执行动画，请稍后再试")
        return
    parts = t.split()
    cmd = parts[0].lower()
    args = parts[1:]
    if cmd == "insert":
        items = _split_items_from_args(args)
        vis.input_var.set(" ".join(items))
        vis.start_insert_animated()
        return
    if cmd == "search":
        val = args[0].strip()
        vis.input_var.set(val)
        vis.start_search_animated()
        return
    if cmd == "delete":
        val = args[0].strip()
        vis.input_var.set(val)
        vis.start_delete_animated()
        return
    if cmd == "clear":
        vis.clear_canvas()
        return
    if cmd == "create":
        items = _split_items_from_args(args)
        vis.model.root = None
        for v in items:
            vis.model.insert(v)
        vis.redraw()
        vis.update_status(f"已创建{len(items)}个节点")
        return
    return
