# run_dsl.py
from dsl_interpreter import run_dsl_text
from avl.avl_model import AVLModel
from binary_tree.bst.bst_model import BSTModel
from binary_tree.huffman_tree.huffman_model import HuffmanModel
from stack.stack_model import StackModel
from sequence_list.sequence_list_model import SequenceListModel 
from tkinter import Tk
from avl.avl_visual import AVLVisualizer

env = {
    "classes": {
        "avl": AVLModel,
        "bst": BSTModel,
        "huffman": HuffmanModel,
        "stack": StackModel,
        "list": SequenceListModel
    },
    "visualizers": {},
    "save_func": None,
    "load_func": None,
    "models": {}
}

# 放在 env 构造之后
from tkinter import Tk, Toplevel
from avl.avl_visual import AVLVisualizer
from avl.avl_model import clone_tree  # 如果你要直接绘制 model 的快照

# 创建一个全局主根（隐藏），以便后续用 Toplevel 打开窗口
GUI_ROOT = Tk()
GUI_ROOT.withdraw()   # 隐藏主窗口（只作为事件循环根）

# 标记：是否创建过可视化窗口（决定脚本末尾是否进入 mainloop）
_launched_visuals = False

def make_avl_vis(model):
    global _launched_visuals
    _launched_visuals = True
    # 使用 Toplevel 作为窗口容器（不会阻塞当前线程）
    win = Toplevel(GUI_ROOT)
    win.title("AVL Visualizer (from DSL)")
    app = AVLVisualizer(win)
    # 尝试把模型装入 visualizer 并绘制快照（兼容旧版 visualizer）
    try:
        # 优先直接把 model 赋值，然后画快照（如果 visualizer 支持）
        if hasattr(app, "model"):
            app.model = model
            # 如果你的 visualizer 有 draw_tree_from_root / redraw 方法，调用之以立即显示
            if hasattr(app, "draw_tree_from_root") and hasattr(model, "root"):
                app.draw_tree_from_root(clone_tree(model.root))
            elif hasattr(app, "redraw"):
                app.redraw()
    except Exception as e:
        print("[WARN] 无法把模型注入 AVLVisualizer：", e)
    # 不在这里调用 win.mainloop() —— 会在脚本结尾统一调用 GUI_ROOT.mainloop()
    return app

env["visualizers"]["avl"] = make_avl_vis


if __name__ == "__main__":
    # 从文件加载 DSL 脚本（或把字符串直接写在这里）
    with open("demo.dsl", "r", encoding="utf-8") as f:
        text = f.read()
    run_dsl_text(text, env)
