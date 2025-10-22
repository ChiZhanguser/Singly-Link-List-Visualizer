# trie_dsl.py
"""
DSL for TrieVisualizer.

支持命令：
  insert <word1, word2 ...>   -> 逐词逐字符动画插入（调用 visualizer.start_insert_animated）
  search <word>               -> 逐字符动画查找（调用 visualizer.start_search_animated）
  clear                       -> 清空 Trie（visualizer.clear_trie）
  help                        -> 弹窗显示帮助

如果没有命令（直接输入若干单词），会将整串内容当作 insert 处理。

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
    解析并执行 Trie DSL 命令。
    visualizer: TrieVisualizer 实例
    raw_text: 用户输入的字符串（可以来自 visualizer.input_var.get()）
    
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
    if cmd in ("insert", "add", "ins"):
        # 支持 insert word1 word2 或 insert word1,word2
        tokens = _split_tokens(args) if args else _split_tokens(visualizer.input_var.get() or "")
        if not tokens:
            messagebox.showinfo("用法", "示例: insert apple, app, bat  （支持逗号或空格分隔多个单词）")
            return
        # 将解析后的单词写回输入框（方便 visualizer 的 parse_input_words 使用）
        visualizer.input_var.set(", ".join(tokens))
        try:
            # 调用可视化的逐词插入动画（visualizer.start_insert_animated 会逐词处理）
            visualizer.start_insert_animated()
        except Exception as e:
            messagebox.showerror("错误", f"启动插入动画失败: {e}")
        finally:
            # 清空输入框
            visualizer.input_var.set("")
        return

    # ---------- search ----------
    if cmd in ("search", "find", "s"):
        token = args.strip() if args else ""
        if not token:
            # 如果没有在命令后给出单词，则尝试从输入框拿第一个词
            toks = _split_tokens(visualizer.input_var.get() or "")
            if toks:
                token = toks[0]
        if not token:
            messagebox.showinfo("用法", "示例: search apple")
            return
        # 写回 input_var，便于 visualizer.start_search_animated 使用
        visualizer.input_var.set(token)
        try:
            visualizer.start_search_animated()
        except Exception as e:
            messagebox.showerror("错误", f"启动查找动画失败: {e}")
        finally:
            # 清空输入框
            visualizer.input_var.set("")
        return

    # ---------- clear ----------
    if cmd in ("clear", "reset"):
        try:
            visualizer.clear_trie()
        except Exception as e:
            messagebox.showerror("错误", f"清空 Trie 失败: {e}")
        finally:
            # 清空输入框
            visualizer.input_var.set("")
        return

    # ---------- help ----------
    if cmd in ("help", "h", "?"):
        msg = (
            "Trie DSL 帮助：\n"
            "  insert <word1, word2 ...>  - 逐词逐字符插入（支持逗号或空白分隔多个单词），例如：insert apple, app, bat\n"
            "  search <word>              - 逐字符动画查找单词，例如：search apple\n"
            "  clear                      - 清空 Trie\n"
            "  help                       - 显示本帮助\n\n"
            "提示：输入框会在命令执行后自动清空，以便下次输入。"
        )
        messagebox.showinfo("DSL 帮助", msg)
        # 清空输入框
        visualizer.input_var.set("")
        return

    # ---------- 默认情况：当作 insert 处理 ----------
    tokens = _split_tokens(txt)
    if tokens:
        visualizer.input_var.set(", ".join(tokens))
        try:
            visualizer.start_insert_animated()
        except Exception as e:
            messagebox.showerror("错误", f"启动插入动画失败: {e}")
        finally:
            # 清空输入框
            visualizer.input_var.set("")
        return

    # 兜底提示
    messagebox.showinfo("未识别命令", "支持命令：insert / search / clear / help，或直接输入单词列表（将视作 insert）。")
    # 清空输入框
    visualizer.input_var.set("")

# 兼容性：DSL_utils 可能期望模块导出名为 `process`
def process(visualizer, text):
    """兼容名为 process 的导出（代理到 process_command）。"""
    return process_command(visualizer, text)