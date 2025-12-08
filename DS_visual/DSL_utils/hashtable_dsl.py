# -*- coding: utf-8 -*-
"""
散列表 DSL 处理器

支持的命令:
    create <val1> <val2> ...  - 批量创建并插入元素
    insert <value>            - 插入单个元素
    find <value>              - 查找元素
    search <value>            - 查找元素（同 find）
    delete <value>            - 删除元素
    clear                     - 清空散列表
    hash <expression>         - 设置散列函数（仅更新函数，不重建）
    hash! <expression>        - 设置散列函数并重建表
    preset <name>             - 使用预设散列函数
    resize <capacity>         - 调整容量
    switch                    - 切换冲突处理方法

散列函数表达式:
    - 支持变量: x (输入值), capacity (表容量)
    - 支持运算: +, -, *, /, //, %, **
    - 支持函数: int(), abs(), str(), len(), ord()
    - 示例: "x % 7", "(x * 2 + 1) % capacity", "int((x * 0.618) % 1 * capacity)"

预设散列函数:
    - mod: 取模法 (x % capacity)
    - multiply: 乘法散列 (黄金比例)
    - square_mid: 平方取中法
    - fold: 折叠法
    - custom: 自定义
"""

from tkinter import messagebox

def process(visualizer, text: str):
    """处理散列表 DSL 命令"""
    if not text or not text.strip():
        return
    
    text = text.strip()
    parts = text.split(maxsplit=1)
    cmd = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""
    
    try:
        if cmd == "create":
            _handle_create(visualizer, args)
        elif cmd == "insert" or cmd == "add":
            _handle_insert(visualizer, args)
        elif cmd in ("find", "search"):
            _handle_find(visualizer, args)
        elif cmd == "delete" or cmd == "remove":
            _handle_delete(visualizer, args)
        elif cmd == "clear":
            visualizer.clear_table()
        elif cmd == "hash":
            _handle_hash(visualizer, args, rebuild=False)
        elif cmd == "hash!":
            _handle_hash(visualizer, args, rebuild=True)
        elif cmd == "preset":
            _handle_preset(visualizer, args)
        elif cmd == "resize":
            _handle_resize(visualizer, args)
        elif cmd == "switch":
            visualizer.switch_method()
        else:
            # 尝试将整个文本作为create命令处理（纯数字列表）
            try:
                values = [int(x) for x in text.split()]
                if values:
                    _handle_create(visualizer, " ".join(str(v) for v in values))
                    return
            except ValueError:
                pass
            messagebox.showerror("错误", f"未知命令: {cmd}\n支持: create, insert, find, delete, clear, hash, preset, resize, switch")
    except Exception as e:
        messagebox.showerror("错误", f"命令执行失败: {str(e)}")


def _handle_create(visualizer, args: str):
    """处理批量创建命令"""
    if not args:
        messagebox.showerror("错误", "create 后请提供数值")
        return
    try:
        values = [int(x) for x in args.split()]
    except ValueError:
        messagebox.showerror("错误", "create 后请提供整数")
        return
    
    visualizer.batch_queue = values
    visualizer.batch_index = 0
    visualizer._set_buttons_state("disabled")
    visualizer._batch_step()


def _handle_insert(visualizer, args: str):
    """处理插入命令"""
    if not args:
        messagebox.showerror("错误", "insert 后请提供一个值")
        return
    try:
        value = int(args.strip())
        visualizer.insert_value(value)
    except ValueError:
        messagebox.showerror("错误", "请提供整数值")


def _handle_find(visualizer, args: str):
    """处理查找命令"""
    if not args:
        messagebox.showerror("错误", "find 后请提供一个值")
        return
    try:
        value = int(args.strip())
        visualizer.find_value(value)
    except ValueError:
        messagebox.showerror("错误", "请提供整数值")


def _handle_delete(visualizer, args: str):
    """处理删除命令"""
    if not args:
        messagebox.showerror("错误", "delete 后请提供一个值")
        return
    try:
        value = int(args.strip())
        visualizer.delete_value(value)
    except ValueError:
        messagebox.showerror("错误", "请提供整数值")


def _handle_hash(visualizer, args: str, rebuild: bool):
    """处理散列函数设置命令"""
    if not args:
        messagebox.showerror("错误", "请提供散列函数表达式\n例如: hash x%7 或 hash! (x*2+1)%capacity")
        return
    
    expr = args.strip()
    
    # 检查是否是预设名称
    try:
        from hashtable.hashtable_model import HASH_PRESETS
    except ModuleNotFoundError:
        from hashtable_model import HASH_PRESETS
    if expr.lower() in HASH_PRESETS:
        expr = HASH_PRESETS[expr.lower()][0]
    
    if visualizer.set_hash_expression(expr, rebuild=rebuild):
        mode = "（已重建表）" if rebuild else "（仅更新函数）"
        messagebox.showinfo("成功", f"散列函数已设置为: h(x) = {expr}\n{mode}")


def _handle_preset(visualizer, args: str):
    """处理预设散列函数命令"""
    try:
        from hashtable.hashtable_model import HASH_PRESETS
    except ModuleNotFoundError:
        from hashtable_model import HASH_PRESETS
    
    if not args:
        presets_list = "\n".join([f"  {k}: {v[1]}" for k, v in HASH_PRESETS.items()])
        messagebox.showinfo("预设散列函数", f"可用预设:\n{presets_list}\n\n用法: preset <名称>")
        return
    
    preset_name = args.strip().lower()
    if preset_name not in HASH_PRESETS:
        presets_list = ", ".join(HASH_PRESETS.keys())
        messagebox.showerror("错误", f"未知预设: {preset_name}\n可用预设: {presets_list}")
        return
    
    expr = HASH_PRESETS[preset_name][0]
    if visualizer.set_hash_expression(expr, rebuild=True):
        messagebox.showinfo("成功", f"已应用预设 '{preset_name}': h(x) = {expr}")


def _handle_resize(visualizer, args: str):
    """处理调整容量命令"""
    if not args:
        messagebox.showerror("错误", "resize 后请提供新容量")
        return
    try:
        new_cap = int(args.strip())
        if new_cap <= 0:
            messagebox.showerror("错误", "容量必须是正整数")
            return
        
        visualizer.capacity_var.set(str(new_cap))
        visualizer._on_confirm_resize()
    except ValueError:
        messagebox.showerror("错误", "请提供整数容量")

