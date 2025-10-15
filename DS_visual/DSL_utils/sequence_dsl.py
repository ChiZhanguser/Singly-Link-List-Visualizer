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
    has_seq_insert_anim = hasattr(vis, "animate_insert") and hasattr(vis.model, "insert")
    has_seq_delete_anim = hasattr(vis, "animate_delete")

    # --------- insert / create ----------
    if cmd in ("insert", "insert_at", "insertat", "create"):
        # create 与 insert 的区别：create 是批量构建（清空后逐一 append）
        if cmd == "create":
            items = _split_items_from_args(args)
            if not items:
                return

            # BST visualizer: reuse its start_insert_animated flow (以逗号分隔传入)
            if has_bst_insert_anim:
                vis.input_var.set(",".join(items))
                vis.start_insert_animated()
                return

            # Sequence-list visualizer: 逐个 append 并 animate_build_element
            if has_seq_build_anim:
                try:
                    vis.disable_buttons()
                except Exception:
                    pass
                try:
                    vis.model.clear()
                    vis.update_display()
                    for i, v in enumerate(items):
                        vis.model.append(v)
                        # animate_build_element(i, v) - i 是新元素在序列中的索引
                        try:
                            vis.animate_build_element(i, v)
                        except Exception:
                            # 若没有动画实现，尝试直接刷新显示
                            vis.update_display()
                        try:
                            vis.window.update()
                        except Exception:
                            pass
                        # 小延时让动画更可见（可调整/移除）
                        time.sleep(0.06)
                except Exception as e:
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

            # fallback
            try:
                for v in items:
                    if hasattr(vis.model, "append"):
                        vis.model.append(v)
                if hasattr(vis, "update_display"):
                    vis.update_display()
            except Exception as e:
                messagebox.showerror("错误", f"插入失败: {e}")
            return

        # 下面处理 insert / insert_at / insertat：支持 "insert 42 at 2" 和 "insert_at 2 42"
        # 解析 items 与可选的 position
        pos = None  # 1-based if set
        items = []
        if cmd in ("insert_at", "insertat"):
            if len(args) < 2:
                messagebox.showerror("错误", "用法：insert_at POSITION VALUE（例如：insert_at 2 42）")
                return
            try:
                pos = int(args[0])
            except Exception:
                messagebox.showerror("错误", "位置需为正整数，例如：insert_at 2 42")
                return
            items = _split_items_from_args(args[1:])
        else:
            # cmd == "insert"
            low_args = [a.lower() for a in args]
            if "at" in low_args:
                at_idx = low_args.index("at")
                if at_idx == 0 or at_idx == len(args) - 1:
                    messagebox.showerror("错误", "用法：insert VALUE at POSITION（例如：insert 42 at 2）")
                    return
                # value 可能由多个 token 或包含逗号
                items = _split_items_from_args(args[:at_idx])
                try:
                    pos = int(" ".join(args[at_idx+1:]))
                except Exception:
                    messagebox.showerror("错误", "位置需为正整数，例如：insert 42 at 2")
                    return
            else:
                # 没指定位置 -> 仅值（可能多个） -> append 行为
                items = _split_items_from_args(args)
                pos = None

        if not items:
            return

        # BST-style visualizer: 原有行为（忽略位置，直接把字符串设置给输入并触发）
        if has_bst_insert_anim:
            vis.input_var.set(",".join(items))
            vis.start_insert_animated()
            return

        # Sequence visualizer: 支持在指定位置插入或追加
        if has_seq_insert_anim or has_seq_build_anim:
            # 若未指定位置 -> 追加（append）
            if pos is None:
                # 追加每个元素
                try:
                    vis.disable_buttons()
                except Exception:
                    pass
                try:
                    for v in items:
                        # append 到模型
                        if hasattr(vis.model, "append"):
                            vis.model.append(v)
                        # 如果有 build 动画接口优先使用
                        if hasattr(vis, "animate_build_element"):
                            idx = len(vis.data_store) - 1
                            try:
                                vis.animate_build_element(idx, v)
                            except Exception:
                                # 再试 animate_insert 作为回退（位置是末尾）
                                if hasattr(vis, "animate_insert"):
                                    try:
                                        vis.animate_insert(idx, v)
                                    except Exception:
                                        pass
                        else:
                            # 无动画，直接刷新
                            if hasattr(vis, "update_display"):
                                vis.update_display()
                        try: vis.window.update()
                        except: pass
                        time.sleep(0.06)
                except Exception as e:
                    try: vis.enable_buttons()
                    except: pass
                    messagebox.showerror("错误", f"插入失败: {e}")
                    return
                try: vis.enable_buttons()
                except: pass
                return

            # 指定位置插入（pos 为 1-based）
            try:
                # 边界检查（允许插入到末尾 len+1）
                n = len(vis.data_store)
                if pos < 1 or pos > n + 1:
                    messagebox.showerror("错误", f"位置越界：当前顺序表长度 {n}，合法位置 1..{n+1}")
                    return

                try:
                    vis.disable_buttons()
                except Exception:
                    pass

                base_idx = pos - 1  # 转为 0-based
                # 对于多个 items，按顺序插入：第一个放在 base_idx，其余依次放后面
                for i, v in enumerate(items):
                    insert_idx = base_idx + i
                    # 更新模型
                    if hasattr(vis.model, "insert"):
                        vis.model.insert(insert_idx, v)
                    else:
                        # fallback：如果只有 list-like data 字段
                        if hasattr(vis.model, "data"):
                            vis.model.data.insert(insert_idx, v)
                    # 播放插入动画（若有）
                    if hasattr(vis, "animate_insert"):
                        try:
                            vis.animate_insert(insert_idx, v)
                        except Exception:
                            # 若失败则刷新显示作为回退
                            if hasattr(vis, "update_display"):
                                vis.update_display()
                    else:
                        if hasattr(vis, "update_display"):
                            vis.update_display()

                    try:
                        vis.window.update()
                    except Exception:
                        pass
                    # 小延时让动画可见
                    time.sleep(0.06)

            except Exception as e:
                try: vis.enable_buttons()
                except: pass
                messagebox.showerror("错误", f"带位置插入失败: {e}")
                return
            finally:
                try: vis.enable_buttons()
                except: pass
            return

        # fallback: 没有 sequence 特定接口 -> 直接修改模型并刷新显示
        try:
            # 导出为普通 list，再进行插入重建
            cur = []
            if hasattr(vis.model, "data"):
                cur = list(vis.model.data)
            else:
                try:
                    cur = list(vis.data_store)
                except Exception:
                    pass
            if pos is None:
                # append
                cur.extend(items)
            else:
                if pos < 1 or pos > len(cur) + 1:
                    messagebox.showerror("错误", f"位置越界：当前顺序表长度 {len(cur)}")
                    return
                idx0 = pos - 1
                for offset, it in enumerate(items):
                    cur.insert(idx0 + offset, it)
            # 把 cur 重新写回模型（若支持 clear/append）
            if hasattr(vis.model, "clear") and hasattr(vis.model, "append"):
                vis.model.clear()
                for v in cur:
                    vis.model.append(v)
            else:
                if hasattr(vis.model, "data"):
                    vis.model.data = cur
                else:
                    try:
                        vis.data_store = cur
                    except Exception:
                        pass
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
            else:
                found = (val in vis.data_store)
            messagebox.showinfo("查找结果", f"{val} {'存在' if found else '不存在'}")
        except Exception as e:
            messagebox.showerror("错误", f"查找失败: {e}")
        return

    # --------- delete ----------
    if cmd == "delete":
        if not args:
            return

        # 如果是 BST visualizer（有专门动画删除接口），优先按值删除（保留原行为）
        if has_bst_insert_anim and hasattr(vis, "start_delete_animated"):
            # 将剩余 args 组合成原始值字符串
            val_str = " ".join(args).strip()
            vis.input_var.set(val_str)
            vis.start_delete_animated()
            return

        # 支持语法： "delete at N" / "delete position N" / "delete pos N"
        first = args[0].lower()
        is_positional = False
        pos = None
        if first in ("at", "position", "pos"):
            if len(args) >= 2:
                try:
                    pos = int(args[1])
                    is_positional = True
                except Exception:
                    is_positional = False
        else:
            # 也支持直接 "delete 3" 作为位置删除（1-based）。注意：这会把数字解释为位置，
            # 如果你还想按数值删除，可以用 "delete value 3" 之类的语法（未实现）。
            try:
                pos = int(first)
                is_positional = True
            except Exception:
                is_positional = False

        # 支持 'first' / 'head' / '1' / 'last' / 'tail' 与位置删除的互操作
        if not is_positional:
            # 仍然支持常见文本关键词删除
            keyword = args[0].lower()
            if keyword in ("first", "head", "1"):
                # 删除第一个元素（若有动画接口，调用 animate_delete(0)）
                if has_seq_delete_anim:
                    try:
                        vis.animate_delete(0)
                    except Exception as e:
                        # 回退：直接修改模型
                        try:
                            if hasattr(vis.model, "pop"):
                                vis.model.pop(0)
                            elif hasattr(vis.model, "data"):
                                vis.model.data.pop(0)
                            if hasattr(vis, "update_display"):
                                vis.update_display()
                        except Exception:
                            messagebox.showerror("错误", f"删除失败: {e}")
                else:
                    try:
                        if hasattr(vis.model, "pop"):
                            vis.model.pop(0)
                        elif hasattr(vis.model, "data"):
                            vis.model.data.pop(0)
                        if hasattr(vis, "update_display"):
                            vis.update_display()
                    except Exception as e:
                        messagebox.showerror("错误", f"删除失败: {e}")
                return
            if keyword in ("last", "tail", "-1"):
                # 删除最后一个
                last_idx = len(vis.data_store) - 1
                if last_idx < 0:
                    messagebox.showerror("错误", "顺序表为空")
                    return
                if has_seq_delete_anim:
                    try:
                        vis.animate_delete(last_idx)
                        return
                    except Exception:
                        pass
                try:
                    if hasattr(vis.model, "pop"):
                        vis.model.pop(last_idx)
                    elif hasattr(vis.model, "data"):
                        vis.model.data.pop(last_idx)
                    if hasattr(vis, "update_display"):
                        vis.update_display()
                except Exception as e:
                    messagebox.showerror("错误", f"删除失败: {e}")
                return

        # 如果识别为位置删除（1-based）
        if is_positional:
            # pos 是 1-based
            try:
                n = len(vis.data_store)
            except Exception:
                try:
                    n = len(vis.model.data)
                except Exception:
                    n = 0
            if pos < 1 or pos > n:
                messagebox.showerror("错误", f"位置越界：当前顺序表长度 {n}")
                return
            idx0 = pos - 1  # 转为 0-based
            # 优先使用 animate_delete（做动画）
            if has_seq_delete_anim:
                try:
                    vis.animate_delete(idx0)
                    return
                except Exception as e:
                    print("animate_delete failed, falling back to model mutation:", e)
            # 回退：直接修改模型并刷新显示
            try:
                if hasattr(vis.model, "pop"):
                    vis.model.pop(idx0)
                elif hasattr(vis.model, "data"):
                    vis.model.data.pop(idx0)
                else:
                    # 尝试修改 data_store 作为最后手段（若可写）
                    try:
                        tmp = list(vis.data_store)
                        tmp.pop(idx0)
                        if hasattr(vis.model, "data"):
                            vis.model.data = tmp
                    except Exception:
                        pass
                if hasattr(vis, "update_display"):
                    vis.update_display()
            except Exception as e:
                messagebox.showerror("错误", f"删除失败: {e}")
            return

        # 否则：按值删除（保持原行为）——在顺序表中查找第一个匹配的元素并删除
        # 兼容 animate_delete 或模型 delete
        val = " ".join(args).strip()
        if hasattr(vis, "data_store") and has_seq_delete_anim:
            try:
                idx = None
                for i, x in enumerate(vis.data_store):
                    if str(x) == val:
                        idx = i
                        break
                if idx is None:
                    messagebox.showinfo("删除", f"未找到 {val}")
                    return
                vis.animate_delete(idx)
            except Exception as e:
                messagebox.showerror("错误", f"删除失败: {e}")
            return
        # fallback: 直接从模型删除值
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
                try:
                    vis.model.clear()
                    if hasattr(vis, "update_display"):
                        vis.update_display()
                except Exception:
                    pass
        except Exception as e:
            messagebox.showerror("错误", f"清空失败: {e}")
        return

    # 未识别命令：不处理
    return
