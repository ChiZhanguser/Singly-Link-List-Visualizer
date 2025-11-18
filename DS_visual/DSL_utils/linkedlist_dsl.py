from tkinter import messagebox
import time

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
                # 没有指定位置 -> 末尾插入
                value = " ".join(args)
                try:
                    # 直接调用可视化器的尾部插入方法
                    visualizer.programmatic_insert_last(value)
                except Exception as e:
                    messagebox.showerror("错误", f"插入失败：{e}")
                return
        
        # 指定位置插入 - 先播放动画，再执行插入
        try:
            # 获取当前链表长度
            if hasattr(visualizer, "node_value_store"):
                try:
                    n = len(visualizer.node_value_store)
                except Exception:
                    if hasattr(visualizer.node_value_store, "to_list"):
                        n = len(visualizer.node_value_store.to_list())
                    else:
                        n = 0
            elif hasattr(visualizer, "model") and hasattr(visualizer.model, "to_list"):
                n = len(visualizer.model.to_list())
            else:
                n = 0

            # 验证位置范围
            if pos < 1 or pos > n + 1:
                messagebox.showerror("错误", f"位置越界：当前链表长度 {n}，合法位置范围 1..{n+1}")
                return

            # 根据位置选择不同的插入方法
            if pos == 1:
                # 头部插入 - 直接调用内部方法
                visualizer._direct_insert_first(value)
            elif pos == n + 1:
                # 尾部插入
                visualizer.programmatic_insert_last(value)
            else:
                # 中间位置插入 - 先播放动画，再执行插入
                prev_node_idx = pos - 2  # 前一个节点的索引（0-based）
                next_node_idx = pos - 1  # 后一个节点的索引（0-based）
                
                # 播放插入动画
                try:
                    visualizer.animate_insert_between_nodes(prev_node_idx, next_node_idx, value)
                except Exception as anim_e:
                    print(f"动画播放失败: {anim_e}")
                    # 如果动画播放失败，直接执行插入
                    visualizer.insert_at_no_animation(pos, value)
                else:
                    # 动画播放成功后，执行实际的插入操作
                    visualizer.insert_at_no_animation(pos, value)
                    
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
            try:
                visualizer.delete_last_node()
            except Exception as e:
                messagebox.showerror("错误", f"删除失败：{e}")
            return

        # 尝试把 key 解析成整数位置
        try:
            pos = int(key)
        except Exception:
            messagebox.showerror("错误", "delete 参数需为 'first'/'last' 或 正整数位置，例如：delete 3")
            return

        # 使用可视化器的删除方法
        if hasattr(visualizer, "delete_at_position"):
            try:
                visualizer.delete_at_position(pos)
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

    # ---------- APPEND (尾部插入) ----------
    if cmd == "append":
        value = " ".join(args)
        try:
            visualizer.programmatic_insert_last(value)
        except Exception as e:
            messagebox.showerror("错误", f"尾部插入失败：{e}")
        return

    # ---------- PREPEND (头部插入) ----------
    if cmd == "prepend":
        value = " ".join(args)
        try:
            if hasattr(visualizer, "_direct_insert_first"):
                visualizer._direct_insert_first(value)
        except Exception as e:
            messagebox.showerror("错误", f"头部插入失败：{e}")
        return

    messagebox.showinfo("未识别命令", 
        "支持命令：\n"
        "- insert VALUE [at POSITION] / insert_at POSITION VALUE\n" 
        "- append VALUE (尾部插入)\n"
        "- prepend VALUE (头部插入)\n"
        "- delete first/last/POSITION\n"
        "- clear\n"
        "- create VALUE1,VALUE2,...")
    return