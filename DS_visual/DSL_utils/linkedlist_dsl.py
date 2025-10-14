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
    if not text:
        return
    parts = text.split()
    cmd = parts[0].lower()
    args = parts[1:]

    # ---------- INSERT (支持末尾插入与指定位置插入) ----------
    if cmd in ("insert", "insert_at", "insertat"):
        # insert_at POS VALUE 形式
        if cmd in ("insert_at", "insertat"):
            if len(args) < 2:
                messagebox.showerror("错误", "用法：insert_at POSITION VALUE（例如：insert_at 2 42）")
                return
            try:
                pos = int(args[0])
            except Exception:
                messagebox.showerror("错误", "位置需为正整数，例如：insert_at 2 42")
                return
            value = " ".join(args[1:])
        else:
            # cmd == "insert"：检查是否使用 "at" 关键字（insert VALUE at POS）
            low_args = [a.lower() for a in args]
            if "at" in low_args:
                at_idx = low_args.index("at")
                if at_idx == 0 or at_idx == len(args) - 1:
                    messagebox.showerror("错误", "用法：insert VALUE at POSITION（例如：insert 42 at 2）")
                    return
                value = " ".join(args[:at_idx])
                try:
                    pos = int(" ".join(args[at_idx+1:]))
                except Exception:
                    messagebox.showerror("错误", "位置需为正整数，例如：insert 42 at 2")
                    return
            else:
                # 没有指定位置 -> 末尾插入（保持原有行为）
                value = " ".join(args)
                try:
                    visualizer.programmatic_insert_last(value)
                except Exception as e:
                    messagebox.showerror("错误", f"插入失败：{e}")
                return

        # 到达这里表示我们有 pos（1-based）和 value，需要在指定位置插入
        # 检查合法性并重建可视化与模型
        try:
            # 获取当前长度 n
            if hasattr(visualizer, "node_value_store"):
                n = len(visualizer.node_value_store)
            elif hasattr(visualizer, "model") and hasattr(visualizer.model, "to_list"):
                n = len(visualizer.model.to_list())
            else:
                n = 0

            if pos < 1 or pos > n + 1:
                messagebox.showerror("错误", f"位置越界：当前链表长度 {n}，合法位置范围 1..{n+1}")
                return

            # 构造新的列表（python list of values）
            if hasattr(visualizer, "node_value_store"):
                new_list = list(visualizer.node_value_store)
            elif hasattr(visualizer, "model") and hasattr(visualizer.model, "to_list"):
                new_list = visualizer.model.to_list()
            else:
                new_list = []

            new_list.insert(pos - 1, str(value))

            # 1) 更新底层 model（如果存在并支持 clear/append 或 insert）
            try:
                if hasattr(visualizer, "model"):
                    m = visualizer.model
                    if hasattr(m, "insert"):
                        # model.insert 期待 0-based idx
                        try:
                            m.insert(pos - 1, value)
                        except Exception:
                            # 如果 insert 失败，退回到 clear+append 重建
                            if hasattr(m, "clear"):
                                m.clear()
                                if hasattr(m, "append"):
                                    for v in new_list:
                                        m.append(v)
                    elif hasattr(m, "clear") and hasattr(m, "append"):
                        m.clear()
                        for v in new_list:
                            m.append(v)
            except Exception:
                # 不影响可视化，继续重建可视化
                pass

            # 2) 重建可视化：先清空，再用 programmatic_insert_last 逐一插入
            if hasattr(visualizer, "clear_visualization") and hasattr(visualizer, "programmatic_insert_last"):
                try:
                    visualizer.clear_visualization()
                    for v in new_list:
                        visualizer.programmatic_insert_last(v)
                except Exception as e:
                    messagebox.showerror("错误", f"重建可视化失败：{e}")
                    return
            else:
                # 如果没有可视化函数，则只尝试更新 node_value_store（如果存在）
                if hasattr(visualizer, "node_value_store"):
                    visualizer.node_value_store.clear()
                    for v in new_list:
                        visualizer.node_value_store.append(v)
                messagebox.showinfo("提示", "已在底层数据结构插入元素，但未能重建可视化（缺少对应方法）")
            return

        except Exception as e:
            messagebox.showerror("错误", f"插入失败：{e}")
            return

    # ---------- DELETE ----------
    if cmd == "delete":
        key = args[0].lower() if args else ""
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

    # ---------- CLEAR ----------
    if cmd == "clear":
        visualizer.clear_visualization()
        return

    # ---------- CREATE ----------
    if cmd == "create":
        items = _parse_items(args)
        visualizer.clear_visualization()
        for v in items:
            visualizer.programmatic_insert_last(v)
        return

    messagebox.showinfo("未识别命令", "支持：insert x / insert VALUE at POS / insert_at POS VALUE / delete x (first/last/pos) / clear / create 1 2 3（或 create 1,2,3）")
    return
