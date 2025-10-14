from tkinter import messagebox

def _parse_items(args):
    items = []
    for a in args:
        for part in a.split(","):
            s = part.strip()
            if s != "":
                items.append(s)
    return items
def process(visualizer, text: str):
    text = (text or "").strip()
    parts = text.split()
    cmd = parts[0].lower()
    args = parts[1:]

    if cmd == "insert":
        value = " ".join(args)
        visualizer.programmatic_insert_last(value)
        return
        
    if cmd == "delete":
        key = args[0].lower()
        if key in ("first", "head", "1"):
            visualizer.delete_first_node()
            return
        if key in ("last", "tail"):
            if hasattr(visualizer, "delete_last_node"):
                visualizer.delete_last_node(0)
                return
            try:
                if hasattr(visualizer, "node_value_store") and len(visualizer.node_value_store) > 0:
                    visualizer.node_value_store.pop()
                if hasattr(visualizer, "model") and hasattr(visualizer.model, "delete_last"):
                    try:
                        visualizer.model.delete_last()
                    except Exception:
                        pass
                if hasattr(visualizer, "clear_visualization") and hasattr(visualizer, "programmatic_insert_last"):
                    tmp = list(visualizer.node_value_store)
                    visualizer.clear_visualization()
                    for v in tmp:
                        visualizer.programmatic_insert_last(v)
                return
            except Exception as e:
                messagebox.showerror("错误", f"删除失败：{e}")
                return
        try:
            pos = int(key)
        except Exception:
            messagebox.showerror("错误", "delete 参数需为 'first'/'last' 或 正整数位置，例如：delete 3")
            return

        n = len(visualizer.node_value_store) if hasattr(visualizer, "node_value_store") else (len(visualizer.model.node_value_store) if hasattr(visualizer, "model") and hasattr(visualizer.model, "node_value_store") else 0)
        if pos < 1 or pos > n:
            messagebox.showerror("错误", f"位置越界：当前链表长度 {n}")
            return

        try:
            if hasattr(visualizer, "node_value_store"):
                remaining = visualizer.node_value_store[:pos-1] + visualizer.node_value_store[pos:]
                visualizer.clear_visualization()
                for v in remaining:
                    visualizer.programmatic_insert_last(v)
                return
            else:
                if hasattr(visualizer, "model") and hasattr(visualizer.model, "to_list"):
                    lst = visualizer.model.to_list()
                    remaining = lst[:pos-1] + lst[pos:]
                    if hasattr(visualizer.model, "clear"):
                        visualizer.model.clear()
                    for v in remaining:
                        if hasattr(visualizer.model, "append"):
                            visualizer.model.append(v)
                    if hasattr(visualizer, "clear_visualization") and hasattr(visualizer, "programmatic_insert_last"):
                        visualizer.clear_visualization()
                        for v in remaining:
                            visualizer.programmatic_insert_last(v)
                    return
        except Exception as e:
            messagebox.showerror("错误", f"删除失败：{e}")
            return

    if cmd == "clear":
        visualizer.clear_visualization()
        return

    if cmd == "create":
        items = _parse_items(args)
        visualizer.clear_visualization()
        for v in items:
            visualizer.programmatic_insert_last(v)
        return
    messagebox.showinfo("未识别命令", "支持：insert x / delete x (first/last/pos) / clear / create 1 2 3（或 create 1,2,3）")
    return
