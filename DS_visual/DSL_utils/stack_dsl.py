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
    
    # 后缀表达式求值命令
    if cmd in ("eval", "postfix", "evaluate", "calc"):
        expression = " ".join(args)
        if not expression:
            messagebox.showinfo("提示", 
                "请输入后缀表达式\n"
                "格式: eval <表达式>\n"
                "例如: eval 3 4 + 2 *\n"
                "      eval 5 1 2 + 4 * + 3 -\n"
                "运算符: + - * / % ^ (空格分隔)")
            return
        # 调用后缀表达式求值方法
        if hasattr(visualizer, 'start_postfix_eval'):
            visualizer.start_postfix_eval(expression)
        else:
            messagebox.showerror("错误", "当前可视化器不支持后缀表达式求值")
        return
    
    # 括号匹配检验命令
    if cmd in ("match", "bracket", "brackets", "check"):
        expression = " ".join(args) if args else ""
        if not expression:
            messagebox.showinfo("提示", 
                "请输入包含括号的表达式\n"
                "格式: match <表达式>\n"
                "例如: match {a+(b-c)*2}\n"
                "      match [(a+b)*(c-d)]\n"
                "      match ((a+b)*[c-d])\n"
                "支持的括号: ( ) [ ] { }")
            return
        # 调用括号匹配检验方法
        if hasattr(visualizer, 'start_bracket_match'):
            visualizer.start_bracket_match(expression)
        else:
            messagebox.showerror("错误", "当前可视化器不支持括号匹配检验")
        return
    
    # 自动扩容控制
    if cmd in ("autoexpand", "auto_expand", "expand"):
        if args:
            arg = args[0].lower()
            if arg in ("on", "true", "1", "yes", "开启", "开"):
                visualizer.model.auto_expand = True
                visualizer.auto_expand_var.set(True)
                visualizer.update_display()
                messagebox.showinfo("设置成功", "自动扩容已开启")
            elif arg in ("off", "false", "0", "no", "关闭", "关"):
                visualizer.model.auto_expand = False
                visualizer.auto_expand_var.set(False)
                visualizer.update_display()
                messagebox.showinfo("设置成功", "自动扩容已关闭")
            else:
                messagebox.showinfo("用法", "autoexpand on/off - 开启/关闭自动扩容")
        else:
            status = "开启" if visualizer.model.auto_expand else "关闭"
            messagebox.showinfo("自动扩容状态", f"当前自动扩容: {status}")
        return
    
    # 设置容量
    if cmd in ("capacity", "cap", "size"):
        if args:
            try:
                new_cap = int(args[0])
                if new_cap < len(visualizer.model.data):
                    messagebox.showerror("错误", f"新容量 {new_cap} 不能小于当前元素数 {len(visualizer.model.data)}")
                else:
                    visualizer.capacity = new_cap
                    visualizer.model.set_capacity(new_cap)
                    visualizer.update_display()
                    messagebox.showinfo("设置成功", f"栈容量已设置为 {new_cap}")
            except ValueError:
                messagebox.showerror("错误", "容量必须是整数")
        else:
            messagebox.showinfo("当前容量", f"栈容量: {visualizer.capacity}, 已使用: {len(visualizer.model.data)}")
        return
    
    # 显示帮助
    if cmd in ("help", "?"):
        messagebox.showinfo("DSL 命令帮助", 
            "支持的命令：\n\n"
            "push <value>      - 入栈\n"
            "pop               - 出栈\n"
            "clear             - 清空栈\n"
            "create 1 2 3      - 批量构建栈\n"
            "create 1,2,3      - 批量构建栈(逗号分隔)\n\n"
            "eval <表达式>     - 后缀表达式求值演示\n"
            "  例: eval 3 4 + 2 *\n"
            "  例: eval 5 1 2 + 4 * + 3 -\n"
            "  运算符: + - * / % ^\n\n"
            "match <表达式>    - 括号匹配检验演示\n"
            "  例: match {a+(b-c)*2}\n"
            "  例: match [(a+b)*(c-d)]\n"
            "  支持括号: ( ) [ ] { }\n\n"
            "autoexpand on/off - 开启/关闭自动扩容\n"
            "capacity <n>      - 设置栈容量\n"
            "help              - 显示此帮助")
        return
    
    messagebox.showinfo("未识别命令", 
        "支持命令：\n"
        "push x, pop, clear, create 1 2 3\n"
        "eval <后缀表达式> (例: eval 3 4 + 2 *)\n"
        "match <表达式> (例: match {a+[b*c]})\n"
        "autoexpand on/off, capacity <n>\n"
        "输入 help 查看详细帮助")
    return
