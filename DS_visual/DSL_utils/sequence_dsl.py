from tkinter import messagebox
import time

def _split_items_from_args(args):
    """
    把命令参数解析成元素列表，支持空格或逗号分隔混合：
    e.g. "1 2 3" / "1,2,3" / "1, 2,3" 等都能解析成 ["1","2","3"]
    """
    items = []
    for tok in args:
        if not tok:
            continue
        parts = [p.strip() for p in tok.split(",") if p.strip() != ""]
        if parts:
            items.extend(parts)
    return items

def process(vis, text):
    """
    通用 DSL 处理器（对顺序表 & BST 都友好）。
    vis: 某个 Visualizer 实例（例如 SequenceListVisualizer 或 BSTVisualizer）
    text: 用户在 DSL 输入框写的命令
    """
    if not vis or not text:
        return
    t = text.strip()
    if getattr(vis, "animating", False):
        messagebox.showinfo("提示", "当前正在执行动画，请稍后再试")
        return

    parts = t.split()
    if not parts:
        return
    cmd = parts[0].lower()
    args = parts[1:]

    # --- helpers to detect capabilities ---
    has_bst_insert_anim = hasattr(vis, "start_insert_animated")
    has_seq_build_anim = hasattr(vis, "animate_build_element") and hasattr(vis, "disable_buttons")

    # --------- insert / create ----------
    if cmd in ("insert", "create"):
        items = _split_items_from_args(args)
        if not items:
            return

        # BST-style visualizer: reuse its start_insert_animated flow
        if has_bst_insert_anim:
            # 用逗号分隔的输入兼容 BST 的解析逻辑
            vis.input_var.set(",".join(items))
            vis.start_insert_animated()
            return

        # Sequence-list visualizer: use append + animate_build_element
        if has_seq_build_anim:
            try:
                vis.disable_buttons()
            except Exception:
                pass
            try:
                # 逐个 append 并调用动画（perform_build_list 的逻辑）
                for i, v in enumerate(items):
                    # append 到模型
                    vis.model.append(v)
                    # 调用可视化的单个插入动画（该方法本身会做移动与刷新）
                    vis.animate_build_element(i, v)
                    # 保证 UI 刷新（animate_build_element 内通常会有 update/sleep，但我们再保证一下）
                    try:
                        vis.window.update()
                    except Exception:
                        pass
                    # 给一点小间隔（可选、调速用）
                    # time.sleep(0.06)
                # 完成后恢复按钮
            except Exception as e:
                # 遇到错误也要确保恢复按钮
                try:
                    vis.enable_buttons()
                except Exception:
                    pass
                messagebox.showerror("错误", f"执行 create/insert 时出错: {e}")
                return
            try:
                vis.enable_buttons()
            except Exception:
                pass
            return

        # fallback: 没有动画接口，直接插入模型并刷新显示
        try:
            for v in items:
                if hasattr(vis.model, "append"):
                    vis.model.append(v)
            if hasattr(vis, "update_display"):
                vis.update_display()
        except Exception as e:
            messagebox.showerror("错误", f"插入失败: {e}")
        return

    # --------- search ----------
    if cmd == "search":
        if not args:
            return
        val = args[0].strip()
        # BST visualizer: use its animated search if exists
        if has_bst_insert_anim and hasattr(vis, "start_search_animated"):
            vis.input_var.set(val)
            vis.start_search_animated()
            return
        # Sequence: no animated search defined — fallback to simple highlight if available
        if hasattr(vis, "start_search_animated"):
            vis.input_var.set(val)
            vis.start_search_animated()
            return
        # fallback: try model search and show message
        try:
            found = False
            if hasattr(vis.model, "data"):
                found = (val in vis.model.data)
            messagebox.showinfo("查找结果", f"{val} {'存在' if found else '不存在'}")
        except Exception as e:
            messagebox.showerror("错误", f"查找失败: {e}")
        return

    # --------- delete ----------
    if cmd == "delete":
        if not args:
            return
        val = args[0].strip()
        # BST visualizer
        if has_bst_insert_anim and hasattr(vis, "start_delete_animated"):
            vis.input_var.set(val)
            vis.start_delete_animated()
            return
        # Sequence visualizer: try to find index then call animate_delete
        if hasattr(vis, "data_store") and hasattr(vis, "animate_delete"):
            try:
                # 在数据模型中查找第一个匹配项的索引（字符串匹配）
                idx = None
                for i, x in enumerate(vis.data_store):
                    if str(x) == val:
                        idx = i
                        break
                if idx is None:
                    messagebox.showinfo("删除", f"未找到 {val}")
                    return
                # animate_delete 使用 0-based index
                vis.animate_delete(idx)
            except Exception as e:
                messagebox.showerror("错误", f"删除失败: {e}")
            return
        # fallback: try model delete/pop then refresh
        try:
            if hasattr(vis.model, "data") and val in vis.model.data:
                vis.model.data.remove(val)
            if hasattr(vis, "update_display"):
                vis.update_display()
        except Exception as e:
            messagebox.showerror("错误", f"删除失败: {e}")
        return

    # --------- clear ----------
    if cmd == "clear":
        try:
            if hasattr(vis, "clear_list"):
                vis.clear_list()
            elif hasattr(vis, "clear_canvas"):
                vis.clear_canvas()
            else:
                vis.model.clear()
                if hasattr(vis, "update_display"):
                    vis.update_display()
        except Exception as e:
            messagebox.showerror("错误", f"清空失败: {e}")
        return

    # 未识别命令：不处理
    return
