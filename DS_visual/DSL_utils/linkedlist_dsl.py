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
        try:
            # 获取当前长度 n
            if hasattr(visualizer, "node_value_store"):
                try:
                    n = len(visualizer.node_value_store)
                except Exception:
                    # 兜底：尝试 to_list 或 model
                    if hasattr(visualizer.node_value_store, "to_list"):
                        n = len(visualizer.node_value_store.to_list())
                    else:
                        n = 0
            elif hasattr(visualizer, "model") and hasattr(visualizer.model, "to_list"):
                n = len(visualizer.model.to_list())
            else:
                n = 0

            if pos < 1 or pos > n + 1:
                messagebox.showerror("错误", f"位置越界：当前链表长度 {n}，合法位置范围 1..{n+1}")
                return

            # 构造新的列表（python list of values）
            if hasattr(visualizer, "node_value_store"):
                # 先尝试把 node_value_store 转为普通 list（兼容自定义容器）
                try:
                    new_list = list(visualizer.node_value_store)
                except Exception:
                    if hasattr(visualizer.node_value_store, "to_list"):
                        new_list = visualizer.node_value_store.to_list()
                    else:
                        # 兜底按索引读取
                        new_list = []
                        try:
                            for i in range(len(visualizer.node_value_store)):
                                new_list.append(visualizer.node_value_store[i])
                        except Exception:
                            pass
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
                    try:
                        if hasattr(visualizer.node_value_store, "clear"):
                            visualizer.node_value_store.clear()
                            if hasattr(visualizer.node_value_store, "append"):
                                for v in new_list:
                                    visualizer.node_value_store.append(v)
                        else:
                            # 兜底：尝试重新赋值（注意：可能不兼容）
                            visualizer.node_value_store = type(visualizer.node_value_store)(new_list)
                    except Exception:
                        pass
                messagebox.showinfo("提示", "已在底层数据结构插入元素，但未能重建可视化（缺少对应方法）")
            return

        except Exception as e:
            messagebox.showerror("错误", f"插入失败：{e}")
            return

    # ---------- DELETE ----------
    if cmd == "delete":
        key = args[0].lower() if args else ""
        # 支持 'first' / 'head' / '1'
        if key in ("first", "head", "1"):
            try:
                visualizer.delete_first_node()
            except Exception as e:
                messagebox.showerror("错误", f"删除失败：{e}")
            return

        # 支持 'last' / 'tail'
        if key in ("last", "tail"):
            if hasattr(visualizer, "delete_last_node"):
                try:
                    visualizer.delete_last_node(0)
                except Exception as e:
                    messagebox.showerror("错误", f"删除失败：{e}")
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
                    tmp = []
                    try:
                        tmp = list(visualizer.node_value_store)
                    except Exception:
                        if hasattr(visualizer.node_value_store, "to_list"):
                            tmp = visualizer.node_value_store.to_list()
                    visualizer.clear_visualization()
                    for v in tmp:
                        visualizer.programmatic_insert_last(v)
                return
            except Exception as e:
                messagebox.showerror("错误", f"删除失败：{e}")
                return

        # 尝试把 key 解析成整数位置
        try:
            pos = int(key)
        except Exception:
            messagebox.showerror("错误", "delete 参数需为 'first'/'last' 或 正整数位置，例如：delete 3")
            return

        # 获取当前长度 n（多种兼容）
        try:
            if hasattr(visualizer, "node_value_store"):
                try:
                    n = len(visualizer.node_value_store)
                except Exception:
                    if hasattr(visualizer.node_value_store, "to_list"):
                        n = len(visualizer.node_value_store.to_list())
                    else:
                        # 兜底按迭代读取
                        try:
                            n = len(list(visualizer.node_value_store))
                        except Exception:
                            n = 0
            elif hasattr(visualizer, "model") and hasattr(visualizer.model, "to_list"):
                n = len(visualizer.model.to_list())
            else:
                n = 0
        except Exception:
            n = 0

        if pos < 1 or pos > n:
            messagebox.showerror("错误", f"位置越界：当前链表长度 {n}")
            return

        # 优先使用 visualizer 提供的 delete_at_position（如果有）
        if hasattr(visualizer, "delete_at_position"):
            try:
                visualizer.delete_at_position(pos)
                return
            except Exception as e:
                # 如果 visualizer 的方法抛出异常，回退到通用实现
                print("visualizer.delete_at_position raised:", e)

        # 回退：导出为普通 list，删除指定索引，重建 model + 可视化
        try:
            # 导出为普通 list（兼容自定义容器）
            cur = []
            if hasattr(visualizer, "node_value_store"):
                try:
                    cur = list(visualizer.node_value_store)
                except Exception:
                    if hasattr(visualizer.node_value_store, "to_list"):
                        cur = visualizer.node_value_store.to_list()
                    else:
                        try:
                            for i in range(len(visualizer.node_value_store)):
                                cur.append(visualizer.node_value_store[i])
                        except Exception:
                            pass
            elif hasattr(visualizer, "model") and hasattr(visualizer.model, "to_list"):
                cur = visualizer.model.to_list()
            else:
                cur = []

            # 安全校验
            if pos < 1 or pos > len(cur):
                messagebox.showerror("错误", f"位置越界：当前链表长度 {len(cur)}")
                return

            remaining = cur[:pos-1] + cur[pos:]

            # 1) 更新底层 model（若存在）
            try:
                if hasattr(visualizer, "model"):
                    m = visualizer.model
                    if hasattr(m, "clear") and hasattr(m, "append"):
                        m.clear()
                        for v in remaining:
                            m.append(v)
            except Exception:
                pass

            # 2) 重建可视化
            if hasattr(visualizer, "clear_visualization") and hasattr(visualizer, "programmatic_insert_last"):
                try:
                    visualizer.clear_visualization()
                    for v in remaining:
                        visualizer.programmatic_insert_last(v)
                except Exception as e:
                    messagebox.showerror("错误", f"重建可视化失败：{e}")
                    return
            else:
                # 仅更新 node_value_store（如果支持）
                if hasattr(visualizer, "node_value_store"):
                    try:
                        if hasattr(visualizer.node_value_store, "clear") and hasattr(visualizer.node_value_store, "append"):
                            visualizer.node_value_store.clear()
                            for v in remaining:
                                visualizer.node_value_store.append(v)
                        else:
                            visualizer.node_value_store = type(visualizer.node_value_store)(remaining)
                    except Exception:
                        pass
                messagebox.showinfo("提示", "已在底层数据结构删除元素，但未能重建可视化（缺少对应方法）")
            return

        except Exception as e:
            messagebox.showerror("错误", f"删除失败：{e}")
            return

    # ---------- CLEAR ----------
    if cmd == "clear":
        try:
            visualizer.clear_visualization()
        except Exception as e:
            messagebox.showerror("错误", f"清空失败：{e}")
        return

    # ---------- CREATE ----------
    if cmd == "create":
        items = _parse_items(args)
        try:
            visualizer.clear_visualization()
            for v in items:
                visualizer.programmatic_insert_last(v)
        except Exception as e:
            messagebox.showerror("错误", f"创建失败：{e}")
        return

    messagebox.showinfo("未识别命令", "支持：insert x / insert VALUE at POS / insert_at POS VALUE / delete x (first/last/pos) / clear / create 1 2 3（或 create 1,2,3）")
    return
