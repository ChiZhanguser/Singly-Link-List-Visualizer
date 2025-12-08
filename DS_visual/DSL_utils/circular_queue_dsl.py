from tkinter import messagebox
import random

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
    if cmd in ("random", "rand", "rnd"):
        # 随机插入指定数量的元素
        try:
            count = int(arg) if arg else 5  # 默认5个
            if count < 1:
                raise ValueError("数量必须大于0")
            if count > 100:
                count = 100
                messagebox.showinfo("提示", "已限制为最多100个")
        except ValueError:
            messagebox.showerror("错误", "random 需要一个正整数参数，例如：random 5")
            return
        
        available = visualizer.capacity - visualizer.model.size
        if available == 0:
            messagebox.showwarning("队列满", "队列已满，无法入队")
            return
        
        if count > available:
            count = available
            messagebox.showinfo("提示", f"可用空间不足，将入队 {count} 个元素")
        
        # 生成随机数并设置批量入队
        random_values = [str(random.randint(1, 100)) for _ in range(count)]
        visualizer.batch_queue = random_values
        visualizer.batch_index = 0
        visualizer._set_buttons_state("disabled")
        visualizer._set_code_status(f"随机入队 {len(random_values)} 个元素...")
        visualizer._batch_step()
        return
    
    # BFS 相关命令
    if cmd == "bfs":
        # 打开BFS演示窗口
        visualizer.open_bfs_demo()
        return
    
    if cmd == "help":
        help_text = """支持的DSL命令：
        
📥 队列操作:
  enqueue <value> - 入队
  dequeue - 出队
  clear - 清空队列
  random <n> - 随机入队n个元素

🔍 图算法演示:
  bfs - 打开BFS广度优先遍历演示

📋 示例:
  enqueue 10
  dequeue
  random 5
  bfs"""
        messagebox.showinfo("DSL 命令帮助", help_text)
        return
    
    messagebox.showinfo("未识别命令", "支持命令：enqueue <value>、dequeue、clear、random <n>、bfs、help")