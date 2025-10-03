# DSL_utils/linkedlist_dsl.py
"""
单链表 DSL：insert / delete / clear / create
设计原则：
- 尽量复用 visualizer 已有的“programmatic_insert_last”以保留可视化动画
- 当需要直接重建时，使用 clear_visualization() + programmatic_insert_last(...) 重建
- 操作对 visualizer.node_value_store 和 visualizer.model 均做兼容修改（若存在 model）
"""
from tkinter import messagebox

def _parse_items(args):
    """把 args 列表解析为元素字符串列表，支持空格或逗号分隔"""
    items = []
    for a in args:
        for part in a.split(","):
            s = part.strip()
            if s != "":
                items.append(s)
    return items

def process(visualizer, text: str):
    text = (text or "").strip()
    if not text:
        return
    parts = text.split()
    cmd = parts[0].lower()
    args = parts[1:]

    # --- insert x  -> insert last ---
    if cmd == "insert":
        if not args:
            messagebox.showerror("错误", "insert 需要一个参数，例如：insert 5")
            return
        value = " ".join(args)
        # 优先使用 programmatic 插入（含可视化动画）
        if hasattr(visualizer, "programmatic_insert_last"):
            try:
                visualizer.programmatic_insert_last(value)
                return
            except Exception as e:
                print("programmatic_insert_last error:", e)
        # 否则直接操作 model / node_value_store 并重建可视化（若提供）
        try:
            if hasattr(visualizer, "model") and hasattr(visualizer.model, "append"):
                visualizer.model.append(value)
            if hasattr(visualizer, "node_value_store"):
                visualizer.node_value_store.append(str(value))
            # 如果可视化没有 programmatic 插入，尝试调用 clear+批量重建（若实现）
            if hasattr(visualizer, "clear_visualization") and hasattr(visualizer, "programmatic_insert_last"):
                tmp = list(visualizer.node_value_store)
                visualizer.clear_visualization()
                for v in tmp:
                    visualizer.programmatic_insert_last(v)
            else:
                # 最后回退：刷新 UI（如果有）
                try:
                    visualizer.information.config(text="已插入（无动画）")
                except Exception:
                    pass
            return
        except Exception as e:
            messagebox.showerror("错误", f"插入失败：{e}")
            return

    # --- delete x  -> 删除第 x 个节点（1-based） ---
    if cmd == "delete":
        if not args:
            messagebox.showerror("错误", "delete 需要一个参数，例如：delete 3，或 delete first / delete last")
            return
        key = args[0].lower()
        # 支持 delete first / delete last
        if key in ("first", "head", "1"):
            # 若有可调用的 delete_first_node，则用它（包含动画）
            if hasattr(visualizer, "delete_first_node"):
                try:
                    visualizer.delete_first_node()
                    return
                except Exception as e:
                    print("delete_first_node error:", e)
            # 回退：修改数据并重建
            try:
                if hasattr(visualizer, "node_value_store") and len(visualizer.node_value_store) > 0:
                    visualizer.node_value_store.pop(0)
                if hasattr(visualizer, "model") and hasattr(visualizer.model, "delete_first"):
                    try:
                        visualizer.model.delete_first()
                    except Exception:
                        pass
                # rebuild
                if hasattr(visualizer, "clear_visualization") and hasattr(visualizer, "programmatic_insert_last"):
                    tmp = list(visualizer.node_value_store)
                    visualizer.clear_visualization()
                    for v in tmp:
                        visualizer.programmatic_insert_last(v)
                return
            except Exception as e:
                messagebox.showerror("错误", f"删除失败：{e}")
                return

        if key in ("last", "tail"):
            # 若有可调用的 delete_last_node(locator) 用 locator=0
            if hasattr(visualizer, "delete_last_node"):
                try:
                    visualizer.delete_last_node(0)
                    return
                except Exception as e:
                    print("delete_last_node error:", e)
            # 回退：数据修改并重建
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

        # 否则尝试把参数解释为位置索引
        try:
            pos = int(key)
        except Exception:
            messagebox.showerror("错误", "delete 参数需为 'first'/'last' 或 正整数位置，例如：delete 3")
            return

        # 检查范围
        n = len(visualizer.node_value_store) if hasattr(visualizer, "node_value_store") else (len(visualizer.model.node_value_store) if hasattr(visualizer, "model") and hasattr(visualizer.model, "node_value_store") else 0)
        if pos < 1 or pos > n:
            messagebox.showerror("错误", f"位置越界：当前链表长度 {n}")
            return

        # 执行删除（数据层面），然后用 programmatic_insert_last 逐个重建可视化（以保留动画）
        try:
            # 剔除指定项（1-based -> index pos-1）
            if hasattr(visualizer, "node_value_store"):
                # 拷贝剩余元素
                remaining = visualizer.node_value_store[:pos-1] + visualizer.node_value_store[pos:]
                # 清空并重建
                visualizer.clear_visualization()
                for v in remaining:
                    visualizer.programmatic_insert_last(v)
                return
            else:
                # 如果没有 node_value_store，尝试在 model 操作然后重建（若 model 支持 to_list）
                if hasattr(visualizer, "model") and hasattr(visualizer.model, "to_list"):
                    lst = visualizer.model.to_list()
                    remaining = lst[:pos-1] + lst[pos:]
                    # 尝试把 model 清空并重新填充
                    if hasattr(visualizer.model, "clear"):
                        visualizer.model.clear()
                    for v in remaining:
                        if hasattr(visualizer.model, "append"):
                            visualizer.model.append(v)
                    # 尝试可视化重建
                    if hasattr(visualizer, "clear_visualization") and hasattr(visualizer, "programmatic_insert_last"):
                        visualizer.clear_visualization()
                        for v in remaining:
                            visualizer.programmatic_insert_last(v)
                    return
        except Exception as e:
            messagebox.showerror("错误", f"删除失败：{e}")
            return

    # --- clear ---
    if cmd == "clear":
        # 优先使用 visualizer.clear_visualization（含 UI 清理）
        if hasattr(visualizer, "clear_visualization"):
            try:
                visualizer.clear_visualization()
                return
            except Exception as e:
                print("clear_visualization error:", e)
        # 回退：清理模型数据并尝试刷新 UI
        try:
            if hasattr(visualizer, "node_value_store"):
                visualizer.node_value_store.clear()
            if hasattr(visualizer, "model") and hasattr(visualizer.model, "clear"):
                visualizer.model.clear()
            try:
                visualizer.information.config(text="已清空")
            except Exception:
                pass
            return
        except Exception as e:
            messagebox.showerror("错误", f"clear 失败：{e}")
            return

    # --- create 1 2 3  或 create 1,2,3 ---
    if cmd == "create":
        if not args:
            messagebox.showerror("错误", "create 需要至少一个值，例如：create 1 2 3 或 create 1,2,3")
            return
        items = _parse_items(args)
        if not items:
            messagebox.showerror("错误", "未解析到有效元素")
            return

        # 清空现有并逐个 programmatic 插入（保留动画）
        try:
            if hasattr(visualizer, "clear_visualization"):
                visualizer.clear_visualization()
            if hasattr(visualizer, "programmatic_insert_last"):
                for v in items:
                    visualizer.programmatic_insert_last(v)
                return
            else:
                # 回退：操作 model / node_value_store 并尝试刷新说明文本
                if hasattr(visualizer, "node_value_store"):
                    visualizer.node_value_store.clear()
                    for v in items:
                        visualizer.node_value_store.append(str(v))
                if hasattr(visualizer, "model") and hasattr(visualizer.model, "clear"):
                    try:
                        visualizer.model.clear()
                        if hasattr(visualizer.model, "append"):
                            for v in items:
                                visualizer.model.append(v)
                    except Exception:
                        pass
                try:
                    visualizer.information.config(text="已创建（无动画）")
                except Exception:
                    pass
                return
        except Exception as e:
            messagebox.showerror("错误", f"创建失败：{e}")
            return

    # 未识别命令
    messagebox.showinfo("未识别命令", "支持：insert x / delete x (first/last/pos) / clear / create 1 2 3（或 create 1,2,3）")
    return
