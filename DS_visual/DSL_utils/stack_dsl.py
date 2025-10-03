# DSL_utils/stack_dsl.py
# 栈的 DSL 实现（push/pop/clear/create）
from tkinter import messagebox

def process(visualizer, text):
    """
    支持命令：
      push x         -> 入栈（支持空格串）
      pop            -> 出栈
      clear          -> 清空
      create 1 2 3   -> 创建并填入（也支持 create 1,2,3）
    visualizer: 需要暴露以下方法/属性（存在则会被使用）
      - animating (bool)
      - animate_push_left(value)
      - pop()
      - clear_stack()
      - capacity (int)
      - model (具有 push/pop/clear/is_full/is_empty/data/top 的对象)
      - update_display()
      - _set_buttons_state(state)
      - _batch_step() / batch_queue / batch_index （用于 create 的动画入栈）
    该实现尽量非侵入，若 visualizer 提供 create_from_list，会优先使用它。
    """
    if getattr(visualizer, "animating", False):
        messagebox.showinfo("提示", "当前正在执行动画，请稍后再试")
        return

    text = text.strip()
    if not text:
        return

    parts = text.split()
    cmd = parts[0].lower()
    args = parts[1:]

    if cmd == "push":
        if not args:
            messagebox.showerror("错误", "push 需要一个参数，例如：push 5")
            return
        value = " ".join(args)
        # 如果 visualizer 有 is_full 判断则用它
        try:
            if hasattr(visualizer.model, "is_full") and visualizer.model.is_full():
                messagebox.showwarning("栈满", "栈已满，无法入栈")
                return
        except Exception:
            pass
        # 使用动画入栈方法（这是最直观的）
        if hasattr(visualizer, "animate_push_left"):
            visualizer.animate_push_left(value)
        else:
            # 回退：直接使用 model.push 并刷新
            try:
                visualizer.model.push(value)
                visualizer.update_display()
            except Exception as e:
                messagebox.showerror("错误", f"入栈失败：{e}")
        return

    if cmd == "pop":
        # 优先使用 visualizer.pop（会处理动画）
        if hasattr(visualizer, "pop"):
            visualizer.pop()
            return
        # 回退到 model.pop
        try:
            visualizer.model.pop()
            visualizer.update_display()
        except Exception:
            messagebox.showwarning("栈空/错误", "出栈失败或栈为空")
        return

    if cmd == "clear":
        if hasattr(visualizer, "clear_stack"):
            visualizer.clear_stack()
            return
        # 回退：直接清空 model
        try:
            if hasattr(visualizer.model, "clear"):
                visualizer.model.clear()
            else:
                # 尝试直接操作 data/top
                visualizer.model.data = []
                visualizer.model.top = -1
            visualizer.update_display()
        except Exception as e:
            messagebox.showerror("错误", f"清空失败：{e}")
        return

    if cmd == "create":
        # parse args: 支持 create 1 2 3 或 create 1,2,3
        if not args:
            messagebox.showerror("错误", "create 需要至少一个值，例如：create 1 2 3")
            return
        items = []
        for a in args:
            for part in a.split(","):
                s = part.strip()
                if s != "":
                    items.append(s)
        if not items:
            messagebox.showerror("错误", "未解析到有效值")
            return

        # 优先使用 visualizer.create_from_list（如果有的话）
        if hasattr(visualizer, "create_from_list"):
            try:
                visualizer.create_from_list(items)
            except Exception as e:
                messagebox.showerror("错误", f"调用 create_from_list 失败：{e}")
            return

        # 否则尝试兼容现有 StackVisualizer 的实现（会使用 batch 动画）
        cap = getattr(visualizer, "capacity", None)
        if cap is None:
            # 没有 capacity，不做扩容提示，直接写入
            pass
        else:
            if len(items) > cap:
                ans = messagebox.askyesno("容量不足",
                                          f"要创建的元素数量 {len(items)} 超过当前 capacity={cap}。\n选择【是】扩容并完整加载；选择【否】则只加载前 {cap} 个元素。")
                if ans:
                    try:
                        # 尝试扩容并重建 model （尝试导入 stack.stack_model）
                        from stack.stack_model import StackModel
                        visualizer.capacity = len(items)
                        visualizer.model = StackModel(visualizer.capacity)
                    except Exception:
                        # 如果导入失败，尝试简单扩容属性
                        visualizer.capacity = len(items)
                        # 若 model 有构造函数可用，尝试用 type 重建
                        try:
                            visualizer.model = type(visualizer.model)(visualizer.capacity)
                        except Exception:
                            pass
                else:
                    items = items[:cap]

        # 清空当前栈并使用 batch 动画逐个入栈（与原实现兼容）
        try:
            if hasattr(visualizer.model, "clear"):
                visualizer.model.clear()
            else:
                visualizer.model.data = []
                visualizer.model.top = -1
        except Exception:
            pass

        try:
            visualizer.update_display()
            # use existing batch mechanism if present
            visualizer.batch_queue = items
            visualizer.batch_index = 0
            if hasattr(visualizer, "_set_buttons_state"):
                visualizer._set_buttons_state("disabled")
            # kick off batch
            if hasattr(visualizer, "_batch_step"):
                visualizer._batch_step()
            else:
                # fallback: do immediate push (no animation)
                for v in items:
                    try:
                        visualizer.model.push(v)
                    except Exception:
                        break
                visualizer.update_display()
                if hasattr(visualizer, "_set_buttons_state"):
                    visualizer._set_buttons_state("normal")
        except Exception as e:
            messagebox.showerror("错误", f"创建失败：{e}")
        return

    # 未识别命令
    messagebox.showinfo("未识别命令", "支持命令：push x, pop, clear, create 1 2 3（或 create 1,2,3）")
    return
