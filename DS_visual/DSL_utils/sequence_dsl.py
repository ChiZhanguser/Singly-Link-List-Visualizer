# DSL_utils/sequence_dsl.py
from tkinter import messagebox

def _split_items(args):
    items = []
    for a in args:
        for p in a.split(","):
            s = p.strip()
            if s:
                items.append(s)
    return items

def process(vis, text):
    """
    支持命令：
      insert x        -> 尾部插入（append / insert_last）
      insert_at i x   -> 在第 i 个位置插入（1-based），也支持 insert_at 0 插入头部
      delete i        -> 删除第 i 个（1-based）；支持 delete first / delete last
      clear           -> 清空顺序表
      create 1 2 3    -> 清空并创建这些元素（支持逗号或空格分隔）
    """
    if not text or not vis:
        return
    parts = text.split()
    if not parts:
        return
    cmd = parts[0].lower()
    args = parts[1:]

    # insert x -> append / insert_last
    if cmd == "insert":
        if not args:
            messagebox.showerror("错误", "insert 需要一个参数，例如：insert 5")
            return
        val = " ".join(args)
        # 优先使用可视化提供的接口以保留动画
        if hasattr(vis, "perform_insert") and hasattr(vis, "animate_insert"):
            try:
                # 默认尾部插入
                pos = len(vis.data_store)
                vis.model.insert_last(val) if hasattr(vis.model, "insert_last") else getattr(vis.model, "append", vis.model.append)(val)
                vis.animate_insert(pos, val)
                return
            except Exception:
                pass
        # 回退：直接写 model 或 data_store 并刷新
        if hasattr(vis, "model") and hasattr(vis.model, "append"):
            try:
                vis.model.append(val)
                if hasattr(vis, "update_display"):
                    vis.update_display()
                return
            except Exception:
                pass
        if hasattr(vis, "data_store"):
            vis.data_store.append(str(val))
            if hasattr(vis, "update_display"):
                vis.update_display()
            return
        return

    # insert_at i x
    if cmd == "insert_at":
        if len(args) < 2:
            messagebox.showerror("错误", "insert_at 需要位置和数值，例如：insert_at 3 42")
            return
        try:
            pos = int(args[0])  # 1-based expected
            val = " ".join(args[1:])
        except Exception:
            messagebox.showerror("错误", "位置必须为整数")
            return
        # convert to 0-based index
        idx = max(0, pos-1)
        try:
            if hasattr(vis.model, "insert_after"):
                # some models use insert_after(index, value) where index is 0-based previous node
                vis.model.insert_after(idx-1 if idx>0 else 0, val)
            elif hasattr(vis.model, "insert"):
                vis.model.insert(idx, val)
            elif hasattr(vis, "insert_at"):
                vis.insert_at(idx, val)
            elif hasattr(vis, "data_store"):
                vis.data_store.insert(idx, str(val))
            if hasattr(vis, "update_display"):
                vis.update_display()
            return
        except Exception as e:
            messagebox.showerror("错误", f"插入失败：{e}")
            return

    # delete i  or delete first/last
    if cmd == "delete":
        if not args:
            messagebox.showerror("错误", "delete 需要参数，例如：delete 3 / delete first / delete last")
            return
        key = args[0].lower()
        if key in ("first", "head", "1"):
            if hasattr(vis, "delete_first"):
                try:
                    vis.delete_first(); return
                except Exception:
                    pass
            # fallback
            if hasattr(vis.model, "pop"):
                try:
                    vis.model.pop(0); vis.update_display(); return
                except Exception:
                    pass
            if hasattr(vis, "data_store") and vis.data_store:
                vis.data_store.pop(0); vis.update_display(); return
            return
        if key in ("last", "tail"):
            if hasattr(vis, "delete_last"):
                try:
                    vis.delete_last(); return
                except Exception:
                    pass
            if hasattr(vis.model, "pop"):
                try:
                    vis.model.pop(); vis.update_display(); return
                except Exception:
                    pass
            if hasattr(vis, "data_store") and vis.data_store:
                vis.data_store.pop(); vis.update_display(); return
            return
        # numeric pos
        try:
            pos = int(key)
        except Exception:
            messagebox.showerror("错误", "delete 参数需为 first/last 或 正整数位置，例如 delete 3")
            return
        idx = pos - 1
        if hasattr(vis.model, "pop"):
            try:
                vis.model.pop(idx)
                if hasattr(vis, "update_display"): vis.update_display()
                return
            except Exception:
                pass
        if hasattr(vis, "data_store"):
            if 0 <= idx < len(vis.data_store):
                vis.data_store.pop(idx)
                if hasattr(vis, "update_display"): vis.update_display()
                return
            else:
                messagebox.showerror("错误", "位置越界")
                return
        messagebox.showerror("错误", "无法执行删除：缺少支持的方法")
        return

    # clear
    if cmd == "clear":
        if hasattr(vis, "clear_list"):
            try:
                vis.clear_list(); return
            except Exception:
                pass
        if hasattr(vis.model, "clear"):
            try:
                vis.model.clear(); vis.update_display(); return
            except Exception:
                pass
        if hasattr(vis, "data_store"):
            vis.data_store.clear(); vis.update_display(); return
        return

    # create 1 2 3  or create 1,2,3
    if cmd == "create":
        if not args:
            messagebox.showerror("错误", "create 需要至少一个值，例如：create 1 2 3")
            return
        items = _split_items(args)
        if hasattr(vis, "prepare_build_list") and hasattr(vis, "perform_build_list"):
            # 如果有构建接口，优先走它（把 values 写入 build_values_entry 然后调用 perform）
            try:
                # 尝试直接快速创建：清空模型后逐个追加（不做动画），再刷新
                if hasattr(vis.model, "clear"):
                    vis.model.clear()
                if hasattr(vis.model, "append"):
                    for v in items:
                        vis.model.append(v)
                    if hasattr(vis, "update_display"):
                        vis.update_display()
                    return
            except Exception:
                pass
        # 回退：写 data_store 或 model
        if hasattr(vis, "data_store"):
            vis.data_store[:] = [str(x) for x in items]
            if hasattr(vis, "update_display"):
                vis.update_display()
            return
        if hasattr(vis.model, "clear") and hasattr(vis.model, "append"):
            try:
                vis.model.clear()
                for v in items:
                    vis.model.append(v)
                if hasattr(vis, "update_display"):
                    vis.update_display()
                return
            except Exception:
                pass
        return

    # 未识别命令 -> 静默返回
    return
