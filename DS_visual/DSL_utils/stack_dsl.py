from tkinter import messagebox
def process(visualizer, text):
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
        value = " ".join(args)
        if visualizer.model.is_full():
            messagebox.showwarning("栈满", "栈已满，无法入栈")
            return
        visualizer.animate_push_left(value)
        return
    if cmd == "pop":
        visualizer.pop()
        return
    if cmd == "clear":
        visualizer.clear_stack()
        return
    if cmd == "create":
        items = []
        for a in args:
            for part in a.split(","):
                s = part.strip()
                if s != "":
                    items.append(s)
        cap = getattr(visualizer, "capacity", None)
        if cap is None:
            pass
        else:
            if len(items) > cap:
                ans = messagebox.askyesno("容量不足",
                                          f"要创建的元素数量 {len(items)} 超过当前 capacity={cap}。\n选择【是】扩容并完整加载；选择【否】则只加载前 {cap} 个元素。")
                if ans:
                    from stack.stack_model import StackModel
                    visualizer.capacity = len(items)
                    visualizer.model = StackModel(visualizer.capacity)
                else:
                    items = items[:cap]
        visualizer.model.clear()
        visualizer.update_display()
        visualizer.batch_queue = items
        visualizer.batch_index = 0
        visualizer._set_buttons_state("disabled")
        visualizer._batch_step()
        return
    messagebox.showinfo("未识别命令", "支持命令：push x, pop, clear, create 1 2 3（或 create 1,2,3）")
    return
