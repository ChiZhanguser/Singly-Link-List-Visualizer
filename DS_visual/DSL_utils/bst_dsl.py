# DSL_utils/bst_dsl.py
from tkinter import messagebox

def _split_items_from_args(args):
    """
    优先按空格分隔（args 已经是按空格切分的片段），
    每个片段内部若包含逗号也会再拆一次以兼容逗号写法。
    返回按顺序的字符串列表。
    """
    items = []
    for tok in args:
        if not tok:
            continue
        # tok 可能像 "1,2,3" 或 "1" 或 "1,2" 或 "10"
        parts = [p.strip() for p in tok.split(",") if p.strip() != ""]
        if parts:
            items.extend(parts)
    return items

def process(vis, text):
    """
    BST DSL:
      insert x y z    -> 插入 x, y, z（优先用动画入口 start_insert_animated / insert_direct）
      search x        -> 查找 x（优先动画）
      delete x        -> 删除 x（优先动画）
      clear           -> 清空（优先 clear_canvas）
      create x y z    -> 清空并按顺序创建 x,y,z（以空格分隔；也兼容逗号）
    """
    if not vis or not text:
        return
    t = text.strip()
    if not t:
        return

    # 阻止在动画进行时重复操作
    if getattr(vis, "animating", False):
        messagebox.showinfo("提示", "当前正在执行动画，请稍后再试")
        return

    parts = t.split()
    cmd = parts[0].lower()
    args = parts[1:]

    # ---------- insert ----------
    if cmd == "insert":
        items = _split_items_from_args(args)
        if not items:
            messagebox.showerror("错误", "insert 需要至少一个值，例如：insert 5 或 insert 5 6 7")
            return
        # 尝试使用动画入口（如果存在且可用）
        try:
            if hasattr(vis, "start_insert_animated") and hasattr(vis, "input_var"):
                vis.input_var.set(" ".join(items))  # set space-separated for consistency
                vis.start_insert_animated()
                return
        except Exception:
            pass
        # 尝试使用直接插入入口
        try:
            if hasattr(vis, "insert_direct") and hasattr(vis, "input_var"):
                vis.input_var.set(" ".join(items))
                vis.insert_direct()
                return
        except Exception:
            pass
        # 回退：直接写 model 并 redraw
        try:
            for v in items:
                if hasattr(vis, "model") and hasattr(vis.model, "insert"):
                    vis.model.insert(v)
                elif hasattr(vis, "model") and hasattr(vis.model, "append"):
                    vis.model.append(v)
            if hasattr(vis, "redraw"):
                vis.redraw()
            if hasattr(vis, "update_status"):
                vis.update_status(f"已插入 {len(items)} 个节点")
        except Exception as e:
            messagebox.showerror("错误", f"插入失败：{e}")
        return

    # ---------- search ----------
    if cmd == "search":
        if not args:
            messagebox.showerror("错误", "search 需要一个参数，例如：search 7")
            return
        val = args[0].strip()
        try:
            if hasattr(vis, "start_search_animated") and hasattr(vis, "input_var"):
                vis.input_var.set(val)
                vis.start_search_animated()
                return
        except Exception:
            pass
        # 回退：直接在 model 中查找并标注
        try:
            node = None
            if hasattr(vis.model, "search_with_path"):
                node, _ = vis.model.search_with_path(val)
            elif hasattr(vis.model, "search"):
                node = vis.model.search(val)
            if node is not None:
                if hasattr(vis, "redraw"):
                    vis.redraw()
                    try:
                        if node in getattr(vis, "node_to_rect", {}):
                            rid = vis.node_to_rect[node]
                            vis.canvas.itemconfig(rid, fill="red")
                            vis.window.after(600, lambda: vis.canvas.itemconfig(rid, fill="#F0F8FF"))
                    except Exception:
                        pass
                if hasattr(vis, "update_status"):
                    vis.update_status(f"查找：找到 {val}")
            else:
                if hasattr(vis, "update_status"):
                    vis.update_status(f"查找：未找到 {val}")
                else:
                    messagebox.showinfo("结果", f"未找到 {val}")
        except Exception as e:
            messagebox.showerror("错误", f"查找失败：{e}")
        return

    # ---------- delete ----------
    if cmd == "delete":
        if not args:
            messagebox.showerror("错误", "delete 需要一个参数，例如：delete 7")
            return
        val = args[0].strip()
        try:
            if hasattr(vis, "start_delete_animated") and hasattr(vis, "input_var"):
                vis.input_var.set(val)
                vis.start_delete_animated()
                return
        except Exception:
            pass
        # 回退：直接调用 model.delete 并 redraw
        try:
            if hasattr(vis.model, "delete"):
                vis.model.delete(val)
            elif hasattr(vis.model, "remove"):
                vis.model.remove(val)
            elif hasattr(vis.model, "delete_by_value"):
                vis.model.delete_by_value(val)
            if hasattr(vis, "redraw"):
                vis.redraw()
            if hasattr(vis, "update_status"):
                vis.update_status(f"已删除 {val}（若存在）")
        except Exception as e:
            messagebox.showerror("错误", f"删除失败：{e}")
        return

    # ---------- clear ----------
    if cmd == "clear":
        try:
            if hasattr(vis, "clear_canvas"):
                vis.clear_canvas()
            else:
                # 最小回退：重建空 model 或置 root 为 None
                try:
                    from binary_tree.bst.bst_model import BSTModel
                    vis.model = BSTModel()
                except Exception:
                    try:
                        vis.model.root = None
                    except Exception:
                        pass
                if hasattr(vis, "redraw"):
                    vis.redraw()
                if hasattr(vis, "update_status"):
                    vis.update_status("已清空")
        except Exception as e:
            messagebox.showerror("错误", f"清空失败：{e}")
        return

    # ---------- create ----------
    if cmd == "create":
        items = _split_items_from_args(args)
        if not items:
            messagebox.showerror("错误", "create 需要至少一个值，例如：create 5 6 7")
            return
        try:
            # 清空模型并逐项插入（不做动画，快速恢复）
            if hasattr(vis.model, "clear"):
                vis.model.clear()
            else:
                try:
                    vis.model.root = None
                except Exception:
                    pass
            for v in items:
                if hasattr(vis.model, "insert"):
                    vis.model.insert(v)
                elif hasattr(vis.model, "append"):
                    vis.model.append(v)
            if hasattr(vis, "redraw"):
                vis.redraw()
            if hasattr(vis, "update_status"):
                vis.update_status(f"已创建 {len(items)} 个节点")
        except Exception as e:
            messagebox.showerror("错误", f"创建失败：{e}")
        return

    # 未识别命令 -> 静默返回
    return
