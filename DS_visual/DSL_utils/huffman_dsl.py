# Huffman_dsl.py
from tkinter import messagebox

def process(visualizer, text: str):
    """
    通过简单 DSL 控制 Huffman 可视化器。
    支持命令：
      - create <n1> <n2> ...    （空格或逗号分隔）
      - clear
      - help
    visualizer: 你的 HuffmanVisualizer 实例（或其它兼容接口）
    """
    if not visualizer or not text or not text.strip():
        return

    # 允许用逗号或空格分隔，忽略大小写
    parts = text.strip().lower().replace(',', ' ').split()
    if not parts:
        return
    cmd = parts[0]
    args = parts[1:]

    if cmd in ('create', 'build', 'start'):
        if not args:
            messagebox.showerror('错误', '请在 create 后提供权值，例如：create 1 2 3 或 create 1,2,3')
            return

        vals = []
        for a in args:
            try:
                v = float(a)
            except Exception:
                messagebox.showerror('错误', f'非法权值：{a}')
                return
            # 可根据需要禁止非正权值（这里允许 0，但禁止负数）
            if v < 0:
                messagebox.showerror('错误', f'权值不能为负数：{a}')
                return
            vals.append(v)

        # 优先使用动画构建接口
        if hasattr(visualizer, 'input_var') and hasattr(visualizer, 'start_animated_build'):
            try:
                visualizer.input_var.set(','.join([str(x) for x in vals]))
                visualizer.start_animated_build()
            except Exception as e:
                messagebox.showerror('错误', f'启动动画失败：{e}')
            return

        # 回退：如果有 draw_initial_leaves 方法则直接绘制初始叶子
        if hasattr(visualizer, 'draw_initial_leaves'):
            try:
                visualizer.draw_initial_leaves(vals)
            except Exception as e:
                messagebox.showerror('错误', f'绘制初始叶子失败：{e}')
            return

        messagebox.showinfo('提示', '当前可视化不支持 create 操作')
        return

    elif cmd in ('clear', 'reset'):
        if hasattr(visualizer, 'clear_canvas'):
            try:
                visualizer.clear_canvas()
            except Exception as e:
                messagebox.showerror('错误', f'清空失败：{e}')
        elif hasattr(visualizer, 'clear_table'):
            try:
                visualizer.clear_table()
            except Exception as e:
                messagebox.showerror('错误', f'清空失败：{e}')
        else:
            messagebox.showinfo('提示', '当前可视化没有 clear 方法')
        return

    elif cmd in ('help', '?'):
        help_txt = (
            "Huffman DSL 支持的命令：\n\n"
            "  create 1 2 3       - 使用空格分隔的权值创建并开始逐步动画\n"
            "  create 1,2,3       - 使用逗号分隔也可以\n"
            "  clear              - 清空画布 / 重置可视化器\n"
            "  help               - 显示此帮助\n\n"
            "示例：\n  create 5,3,8,2\n"
        )
        messagebox.showinfo('Huffman DSL 帮助', help_txt)
        return

    else:
        messagebox.showerror('错误', '不支持的 Huffman 命令。支持：create, clear, help')
        return
