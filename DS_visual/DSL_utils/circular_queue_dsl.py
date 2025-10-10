from tkinter import messagebox

def _fallback_process_command(visualizer, text):
    if visualizer.animating:
        messagebox.showinfo("提示", "当前正在执行动画，请稍后再试")
        return
    text = (text or "").strip()
    if not text:
        return
    parts = text.split(maxsplit=1)
    cmd = parts[0].lower()
    arg = parts[1].strip() if len(parts) > 1 else ""
    if cmd in ("enqueue", "enq", "push"):
        if arg == "":
            messagebox.showerror("错误", "enqueue 需要一个参数，例如：enqueue 5")
            return
        if visualizer.model.is_full():
            messagebox.showwarning("队列满", "队列已满，无法入队")
            return
        visualizer.animate_enqueue(arg)
        return
    if cmd in ("dequeue", "deq", "pop"):
        if visualizer.model.is_empty():
            messagebox.showwarning("队列空", "队列为空，无法出队")
            return
        visualizer.animate_dequeue()
        return
    if cmd == "clear":
        visualizer.clear_queue()
        return
    messagebox.showinfo("未识别命令", "仅支持命令：enqueue <value>、dequeue、clear。")