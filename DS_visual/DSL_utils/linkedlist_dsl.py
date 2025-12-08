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
                # 头部插入 - 使用带平滑动画的方法
                try:
                    if hasattr(visualizer, 'dsl_insert_at_head_with_smooth_animation'):
                        visualizer.dsl_insert_at_head_with_smooth_animation(value)
                    else:
                        visualizer._direct_insert_first(value)
                except Exception as e:
                    print(f"头部插入动画失败: {e}")
                    visualizer._direct_insert_first(value)
            elif pos == n + 1:
                # 尾部插入
                visualizer.programmatic_insert_last(value)
            else:
                # 中间位置插入 - 使用带完整平滑动画的方法
                try:
                    if hasattr(visualizer, 'dsl_insert_at_position_with_smooth_animation'):
                        visualizer.dsl_insert_at_position_with_smooth_animation(pos, value)
                    else:
                        # 回退到旧方法
                        prev_node_idx = pos - 2
                        next_node_idx = pos - 1
                        visualizer.animate_insert_between_nodes(prev_node_idx, next_node_idx, value)
                        visualizer.insert_at_no_animation(pos, value)
                except Exception as anim_e:
                    print(f"动画播放失败: {anim_e}")
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

    # ---------- DELETE_VALUE (按值删除) ----------
    if cmd in ("delete_value", "deletevalue", "remove_value", "removevalue"):
        if not args:
            messagebox.showerror("错误", "用法：delete_value VALUE（例如：delete_value 42）")
            return
        value = " ".join(args)
        try:
            if hasattr(visualizer, "delete_by_value"):
                visualizer.delete_by_value(value)
            else:
                messagebox.showerror("错误", "当前可视化器不支持按值删除")
        except Exception as e:
            messagebox.showerror("错误", f"按值删除失败：{e}")
        return

    # ---------- INSERT_BEFORE (在某值前插入) ----------
    if cmd in ("insert_before", "insertbefore"):
        if len(args) < 2:
            messagebox.showerror("错误", "用法：insert_before TARGET_VALUE NEW_VALUE（例如：insert_before 5 3）\n在值为5的节点前面插入3")
            return
        target_value = args[0]
        new_value = " ".join(args[1:])
        try:
            if hasattr(visualizer, "insert_before_value"):
                visualizer.insert_before_value(target_value, new_value)
            else:
                messagebox.showerror("错误", "当前可视化器不支持按值前插入")
        except Exception as e:
            messagebox.showerror("错误", f"按值前插入失败：{e}")
        return

    # ---------- INSERT_AFTER (在某值后插入) ----------
    if cmd in ("insert_after", "insertafter"):
        if len(args) < 2:
            messagebox.showerror("错误", "用法：insert_after TARGET_VALUE NEW_VALUE（例如：insert_after 5 3）\n在值为5的节点后面插入3")
            return
        target_value = args[0]
        new_value = " ".join(args[1:])
        try:
            if hasattr(visualizer, "insert_after_value"):
                visualizer.insert_after_value(target_value, new_value)
            else:
                messagebox.showerror("错误", "当前可视化器不支持按值后插入")
        except Exception as e:
            messagebox.showerror("错误", f"按值后插入失败：{e}")
        return

    # ---------- INSERT_BETWEEN (在两个值之间插入) ----------
    if cmd in ("insert_between", "insertbetween"):
        if len(args) < 3:
            messagebox.showerror("错误", "用法：insert_between A B X（例如：insert_between 3 7 5）\n在值为3和7的节点之间插入5")
            return
        value_a = args[0]
        value_b = args[1]
        new_value = " ".join(args[2:])
        try:
            if hasattr(visualizer, "insert_between_values"):
                visualizer.insert_between_values(value_a, value_b, new_value)
            else:
                messagebox.showerror("错误", "当前可视化器不支持在两值之间插入")
        except Exception as e:
            messagebox.showerror("错误", f"在两值之间插入失败：{e}")
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

    # ---------- SEARCH ----------
    if cmd == "search":
        if not args:
            messagebox.showerror("错误", "用法：search VALUE（例如：search 42）")
            return
        value = " ".join(args)
        try:
            if hasattr(visualizer, 'enhanced_ops') and visualizer.enhanced_ops:
                visualizer.enhanced_ops.search_with_animation(value)
            else:
                messagebox.showerror("错误", "增强操作模块未初始化")
        except Exception as e:
            messagebox.showerror("错误", f"搜索失败：{e}")
        return

    # ---------- TRAVERSE ----------
    if cmd == "traverse":
        try:
            if hasattr(visualizer, 'enhanced_ops') and visualizer.enhanced_ops:
                visualizer.enhanced_ops.traverse_with_animation()
            else:
                messagebox.showerror("错误", "增强操作模块未初始化")
        except Exception as e:
            messagebox.showerror("错误", f"遍历失败：{e}")
        return

    # ---------- REVERSE ----------
    if cmd == "reverse":
        try:
            if hasattr(visualizer, 'enhanced_ops') and visualizer.enhanced_ops:
                visualizer.enhanced_ops.reverse_with_animation()
            else:
                messagebox.showerror("错误", "增强操作模块未初始化")
        except Exception as e:
            messagebox.showerror("错误", f"反转失败：{e}")
        return

    # ---------- LENGTH ----------
    if cmd == "length":
        try:
            if hasattr(visualizer, 'enhanced_ops') and visualizer.enhanced_ops:
                visualizer.enhanced_ops.get_length_with_animation()
            else:
                # 回退到直接显示
                n = len(visualizer.node_value_store) if hasattr(visualizer, 'node_value_store') else 0
                visualizer.information.config(text=f"链表长度: {n}")
        except Exception as e:
            messagebox.showerror("错误", f"计算长度失败：{e}")
        return

    # ---------- MEMORY ----------
    if cmd == "memory":
        try:
            from linked_list.ui_utils import _toggle_memory_addresses
            _toggle_memory_addresses(visualizer)
        except Exception as e:
            messagebox.showerror("错误", f"显示内存地址失败：{e}")
        return

    messagebox.showinfo("未识别命令", 
        "支持命令：\n"
        "📥 插入操作:\n"
        "  - insert VALUE [at POSITION]\n"
        "  - append VALUE (尾部插入)\n"
        "  - prepend VALUE (头部插入)\n"
        "  - insert_before TARGET NEW (在某值前插入)\n"
        "  - insert_after TARGET NEW (在某值后插入)\n"
        "  - insert_between A B X (在A和B之间插入X)\n"
        "📤 删除操作:\n"
        "  - delete first/last/POSITION\n"
        "  - delete_value VALUE (按值删除)\n"
        "✨ 增强操作:\n"
        "  - search VALUE (搜索)\n"
        "  - traverse (遍历)\n"
        "  - reverse (反转)\n"
        "  - length (计算长度)\n"
        "  - memory (显示内存地址)\n"
        "🔧 其他:\n"
        "  - clear\n"
        "  - create VALUE1,VALUE2,...")
    return