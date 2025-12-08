# bplustree_dsl.py
"""
DSL for BPlusVisualizer.

支持命令：
  insert <key1, key2 ...>   -> 批量插入键值（调用 visualizer.start_insert_animated）
  search <key>              -> 查找键值（暂未实现动画，显示提示）
  clear                     -> 清空 B+ 树（visualizer.clear_tree）
  help                      -> 弹窗显示帮助

如果没有命令（直接输入若干数字），会将整串内容当作 insert 处理。

输入框会在命令执行后自动清空，以便下次输入。
"""
import re
from tkinter import messagebox

def _split_tokens(text: str):
    """把输入按逗号或空白拆分为 token 列表，去除空串"""
    if not text:
        return []
    tokens = [t.strip() for t in re.split(r'[\s,]+', text) if t.strip() != ""]
    return tokens

def process_command(visualizer, raw_text: str):
    """
    解析并执行 B+ 树 DSL 命令。
    visualizer: BPlusVisualizer 实例
    raw_text: 用户输入的字符串
    
    执行后会自动清空输入框。
    """
    if not visualizer:
        return
    txt = (raw_text or "").strip()
    if not txt:
        return

    parts = txt.split(None, 1)
    cmd = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""

    # 如果 visualizer 正在动画中，提示并返回
    if getattr(visualizer, "animating", False):
        messagebox.showinfo("提示", "当前正在执行动画，请稍后再试")
        return

    # ---------- insert ----------
    if cmd in ("insert", "add", "ins", "push"):
        tokens = _split_tokens(args) if args else _split_tokens(visualizer.input_var.get() or "")
        if not tokens:
            messagebox.showinfo("用法", "示例: insert 10, 20, 30  （支持逗号或空格分隔多个键值）")
            return
        # 将解析后的键值写回输入框
        visualizer.input_var.set(", ".join(tokens))
        try:
            visualizer.start_insert_animated()
        except Exception as e:
            messagebox.showerror("错误", f"启动插入动画失败: {e}")
        finally:
            visualizer.input_var.set("")
        return

    # ---------- search ----------
    if cmd in ("search", "find", "s", "query"):
        token = args.strip() if args else ""
        if not token:
            toks = _split_tokens(visualizer.input_var.get() or "")
            if toks:
                token = toks[0]
        if not token:
            messagebox.showinfo("用法", "示例: search 10")
            return
        # B+ 树目前没有实现查找动画，显示提示
        try:
            key = int(token)
        except:
            key = token
        
        # 简单的查找逻辑
        node = visualizer.tree.root
        found = False
        while node:
            if node.is_leaf:
                if key in node.keys:
                    found = True
                break
            # 找到对应的子节点
            i = 0
            while i < len(node.keys) and key >= node.keys[i]:
                i += 1
            node = node.children[i] if i < len(node.children) else None
        
        if found:
            visualizer.update_status(f"✓ 找到键 {key}")
            visualizer.update_explanation(f"键 {key} 存在于 B+ 树中")
            messagebox.showinfo("查找结果", f"✓ 找到键 {key}")
        else:
            visualizer.update_status(f"✗ 未找到键 {key}")
            visualizer.update_explanation(f"键 {key} 不存在于 B+ 树中")
            messagebox.showinfo("查找结果", f"✗ 未找到键 {key}")
        
        visualizer.input_var.set("")
        return

    # ---------- clear ----------
    if cmd in ("clear", "reset"):
        try:
            visualizer.clear_tree()
        except Exception as e:
            messagebox.showerror("错误", f"清空 B+ 树失败: {e}")
        finally:
            visualizer.input_var.set("")
        return

    # ---------- help ----------
    if cmd in ("help", "h", "?"):
        msg = (
            "B+ 树 DSL 帮助：\n"
            "  insert <key1, key2 ...>  - 批量插入键值（支持逗号或空白分隔），例如：insert 10, 20, 30\n"
            "  search <key>             - 查找键值，例如：search 10\n"
            "  clear                    - 清空 B+ 树\n"
            "  help                     - 显示本帮助\n\n"
            "提示：直接输入数字列表会当作 insert 处理。"
        )
        messagebox.showinfo("DSL 帮助", msg)
        visualizer.input_var.set("")
        return

    # ---------- 默认情况：当作 insert 处理 ----------
    tokens = _split_tokens(txt)
    if tokens:
        # 检查是否都是数字
        visualizer.input_var.set(", ".join(tokens))
        try:
            visualizer.start_insert_animated()
        except Exception as e:
            messagebox.showerror("错误", f"启动插入动画失败: {e}")
        finally:
            visualizer.input_var.set("")
        return

    # 兜底提示
    messagebox.showinfo("未识别命令", "支持命令：insert / search / clear / help，或直接输入数字列表（将视作 insert）。")
    visualizer.input_var.set("")


# 兼容性：DSL_utils 可能期望模块导出名为 `process`
def process(visualizer, text):
    """兼容名为 process 的导出（代理到 process_command）。"""
    return process_command(visualizer, text)

