# Huffman_dsl.py
from tkinter import messagebox

def process(visualizer, text: str):
    """
    通过简单 DSL 控制 Huffman 可视化器。
    支持命令：
      - create <n1> <n2> ...    （空格或逗号分隔）创建并构建Huffman树
      - clear / reset           清空重置
      - pause                   暂停动画
      - resume / continue       继续动画
      - step                    单步执行
      - auto                    自动模式
      - speed <0.25-3.0>        设置动画速度
      - help / ?                显示帮助
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

    elif cmd == 'pause':
        # 暂停动画
        if hasattr(visualizer, 'toggle_pause'):
            if not getattr(visualizer, 'paused', False):
                visualizer.toggle_pause()
        elif hasattr(visualizer, 'paused'):
            visualizer.paused = True
        else:
            messagebox.showinfo('提示', '当前可视化不支持 pause 操作')
        return

    elif cmd in ('resume', 'continue', 'play'):
        # 继续动画
        if hasattr(visualizer, 'set_auto_mode'):
            visualizer.set_auto_mode()
        elif hasattr(visualizer, 'toggle_pause'):
            if getattr(visualizer, 'paused', True):
                visualizer.toggle_pause()
        elif hasattr(visualizer, 'paused'):
            visualizer.paused = False
        else:
            messagebox.showinfo('提示', '当前可视化不支持 resume 操作')
        return

    elif cmd == 'step':
        # 单步执行
        if hasattr(visualizer, 'do_next_step'):
            visualizer.do_next_step()
        else:
            messagebox.showinfo('提示', '当前可视化不支持 step 操作')
        return

    elif cmd == 'auto':
        # 自动模式
        if hasattr(visualizer, 'set_auto_mode'):
            visualizer.set_auto_mode()
        else:
            messagebox.showinfo('提示', '当前可视化不支持 auto 操作')
        return

    elif cmd == 'speed':
        # 设置动画速度
        if not args:
            messagebox.showerror('错误', '请指定速度值 (0.25-3.0)，例如：speed 1.5')
            return
        try:
            speed_val = float(args[0])
            if speed_val < 0.25 or speed_val > 3.0:
                messagebox.showerror('错误', '速度值必须在 0.25 到 3.0 之间')
                return
            
            if hasattr(visualizer, 'speed_var'):
                visualizer.speed_var.set(speed_val)
            if hasattr(visualizer, 'animation_speed'):
                visualizer.animation_speed = speed_val
            if hasattr(visualizer, 'speed_label'):
                visualizer.speed_label.config(text=f"{speed_val:.2f}x")
            if hasattr(visualizer, 'speed_scale'):
                visualizer.speed_scale.set(speed_val)
        except ValueError:
            messagebox.showerror('错误', f'非法速度值：{args[0]}')
        return

    elif cmd == 'demo':
        # 演示模式：使用预设数据
        demo_data = "5, 9, 12, 13, 16, 45"
        if hasattr(visualizer, 'input_var') and hasattr(visualizer, 'start_animated_build'):
            visualizer.input_var.set(demo_data)
            visualizer.start_animated_build()
        return

    elif cmd == 'heap':
        # 堆相关命令
        if not args:
            # 显示当前堆状态
            if hasattr(visualizer, 'heap_state') and visualizer.heap_state:
                messagebox.showinfo('堆状态', 
                    f"当前堆: {visualizer.heap_state}\n"
                    f"堆顶 (最小值): {visualizer.heap_state[0] if visualizer.heap_state else 'N/A'}")
            else:
                messagebox.showinfo('堆状态', '堆为空')
            return
        
        sub_cmd = args[0]
        if sub_cmd == 'show':
            if hasattr(visualizer, 'show_heap'):
                visualizer.show_heap = True
                if hasattr(visualizer, '_draw_heap') and hasattr(visualizer, 'heap_state'):
                    visualizer._draw_heap(visualizer.heap_state)
        elif sub_cmd == 'hide':
            if hasattr(visualizer, 'show_heap'):
                visualizer.show_heap = False
            if hasattr(visualizer, '_clear_heap_display'):
                visualizer._clear_heap_display()
        elif sub_cmd == 'clear':
            if hasattr(visualizer, '_clear_heap_display'):
                visualizer._clear_heap_display()
        return

    elif cmd in ('help', '?'):
        help_txt = (
            "🎓 Huffman DSL 教学命令：\n\n"
            "📝 构建命令：\n"
            "  create 1 2 3       - 使用权值创建Huffman树\n"
            "  create 1,2,3       - 逗号分隔也可以\n"
            "  demo               - 使用预设数据演示\n\n"
            "🎮 动画控制：\n"
            "  pause              - 暂停动画\n"
            "  resume / continue  - 继续动画\n"
            "  step               - 单步执行 (需先暂停)\n"
            "  auto               - 切换到自动模式\n"
            "  speed 1.5          - 设置动画速度 (0.25-3.0)\n\n"
            "📊 堆可视化：\n"
            "  heap               - 显示当前堆状态\n"
            "  heap show          - 显示堆可视化\n"
            "  heap hide          - 隐藏堆可视化\n"
            "  heap clear         - 清空堆显示\n\n"
            "🔧 其他命令：\n"
            "  clear / reset      - 清空画布重置\n"
            "  help / ?           - 显示此帮助\n\n"
            "💡 示例：\n"
            "  create 5,3,8,2     - 创建4个节点的树\n"
            "  speed 0.5          - 放慢动画速度\n"
            "  pause              - 暂停查看细节\n"
            "  step               - 逐步查看过程\n"
        )
        messagebox.showinfo('Huffman DSL 帮助', help_txt)
        return

    else:
        messagebox.showerror('错误', f'不支持的命令: {cmd}\n\n输入 help 查看所有支持的命令')
        return
