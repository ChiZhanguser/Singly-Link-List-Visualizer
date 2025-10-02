# improved_main_interface_fixed.py
from tkinter import *
from tkinter import ttk
from linked_list.linked_list_visual import LinkList
from sequence_list.sequence_list_visual import SequenceListVisualizer
from stack.stack_visual import StackVisualizer
from binary_tree.linked_storage.linked_storage_visual import BinaryTreeVisualizer
from binary_tree.bst.bst_visual import BSTVisualizer
from binary_tree.huffman_tree.huffman_visual import HuffmanVisualizer
from avl.avl_visual import AVLVisualizer
import math
from llm.chat_window import ChatWindow
from llm.function_dispatcher import register_visualizer

def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb):
    return '#{:02x}{:02x}{:02x}'.format(*rgb)

def blend_hex(c1, c2, t):
    r1, g1, b1 = hex_to_rgb(c1)
    r2, g2, b2 = hex_to_rgb(c2)
    return rgb_to_hex((int(r1 + (r2 - r1) * t),
                       int(g1 + (g2 - g1) * t),
                       int(b1 + (b2 - b1) * t)))

def lighten_hex(h, amount=0.12):
    r, g, b = hex_to_rgb(h)
    r = min(255, int(r + (255 - r) * amount))
    g = min(255, int(g + (255 - g) * amount))
    b = min(255, int(b + (255 - b) * amount))
    return rgb_to_hex((r, g, b))

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip = None
        widget.bind("<Enter>", self.show)
        widget.bind("<Leave>", self.hide)

    def show(self, _=None):
        if self.tip or not self.text:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 6
        self.tip = Toplevel(self.widget)
        self.tip.overrideredirect(True)
        self.tip.attributes("-topmost", True)
        label = Label(self.tip, text=self.text, font=("Arial", 10),
                      bg="#333333", fg="white", padx=6, pady=3, bd=0, relief='solid')
        label.pack()
        self.tip.geometry(f"+{x}+{y}")

    def hide(self, _=None):
        if self.tip:
            self.tip.destroy()
            self.tip = None

class MainInterface:
    def __init__(self, root):
        self.window = root
        self.window.title("数据结构可视化工具 — 张驰")
        self.window.geometry("980x720")
        self.window.minsize(860, 600)
        try:
            style = ttk.Style(self.window)
            style.theme_use('clam')
        except Exception:
            pass
        self.window.configure(bg="#EAF5FF")

        header_h = 160
        self.header = Canvas(self.window, height=header_h, bd=0, highlightthickness=0)
        self.header.pack(fill=X)
        # 绑定重绘，保证窗口大小变化时渐变正常
        self.header.bind("<Configure>", lambda e: self._draw_header_gradient(self.header, header_h, "#3a8dde", "#70b7ff"))

        # 顶部文字
        self.header.create_text(40, 42, anchor='w', text="数据结构可视化工具",
                                font=("Helvetica", 28, "bold"), fill="#062A4A", tags="title")
        self.header.create_text(40, 80, anchor='w',
                                text="交互、演示与教学 — 支持链表/顺序表/栈/多种树结构",
                                font=("Helvetica", 12), fill="#EAF6FF", tags="subtitle")

        # 先放 shadow（阴影）——非常关键：阴影应该在 card 下面
        shadow = Frame(self.window, bg="#d7e9ff")
        shadow.place(relx=0.5, y=header_h - 18, anchor='n', relwidth=0.86, height=424)

        # 再放主卡片（card），以保证卡片位于阴影之上
        card = Frame(self.window, bg="white")
        card.place(relx=0.5, y=header_h - 20, anchor='n', relwidth=0.86, height=420)
        card.grid_propagate(False)
        card.grid_rowconfigure(0, weight=0)
        card.grid_rowconfigure(1, weight=1)
        card.grid_columnconfigure(0, weight=1)

        top_frame = Frame(card, bg="white")
        top_frame.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 10))
        subtitle = Label(top_frame, text="选择可视化模块", font=("Helvetica", 16, "bold"), bg="white", fg="#0b3a66")
        subtitle.grid(row=0, column=0, sticky="w")
        desc = Label(top_frame, text="点击下面的按钮进入对应数据结构的交互演示。支持键盘/鼠标交互。",
                     font=("Helvetica", 10), bg="white", fg="#4d6b88")
        desc.grid(row=1, column=0, sticky="w", pady=(6, 0))

        btn_frame = Frame(card, bg="white")
        btn_frame.grid(row=1, column=0, sticky="nsew", padx=24, pady=10)
        for i in range(2):
            btn_frame.grid_columnconfigure(i, weight=1)

        btns = [
            ("单链表", "#FF8C42", "🔗", self.open_linked_list, "单链表（单向）可视化与操作"),
            ("顺序表", "#2ECC71", "📋", self.open_sequence_list, "基于数组的顺序表演示"),
            ("栈", "#8E44AD", "📚", self.open_stack, "后进先出（LIFO）结构演示"),
            ("二叉树链式存储", "#E74C3C", "🌳", self.open_binary_tree, "链式存储的普通二叉树"),
            ("二叉搜索树", "#3498DB", "🔎", self.open_bst, "BST：插入/删除/查找演示"),
            ("Huffman树", "#A0522D", "🔠", self.open_huffman, "基于频率的编码树（Huffman）"),
            ("AVL (平衡二叉树)", "#5DADE2", "⚖️", self.open_avl, "自平衡 AVL 树演示"),
        ]

        for idx, (label, color, emoji, cmd, tip) in enumerate(btns):
            col = idx % 2
            row = idx // 2
            btn = Button(btn_frame, text=f"{emoji}  {label}", font=("Helvetica", 13, "bold"),
                         bd=0, relief='flat', activebackground=lighten_hex(color, 0.10),
                         bg=color, fg="white", cursor="hand2",
                         command=cmd)
            btn.grid(row=row, column=col, sticky="nsew", padx=12, pady=12, ipadx=6, ipady=12)
            btn_frame.grid_rowconfigure(row, weight=1, minsize=80)
            self._attach_hover_effect(btn, color)
            ToolTip(btn, tip)

        bottom_bar = Frame(self.window, bg="#F4F8FF", height=36)
        bottom_bar.pack(fill=X, side=BOTTOM)
        copyright_label = Label(bottom_bar, text="© 张驰 的 数据结构可视化工具", bg="#F4F8FF", fg="#7a8897",
                                font=("Arial", 10))
        copyright_label.pack(side=LEFT, padx=12)
        status_label = Label(bottom_bar, text="版本 1.0  •  UI 改进版", bg="#F4F8FF", fg="#7a8897", font=("Arial", 10))
        status_label.pack(side=RIGHT, padx=12)

        self.window.bind("<Key-1>", lambda e: self.open_linked_list())
        self.window.bind("<Key-2>", lambda e: self.open_sequence_list())
        self.window.bind("<Key-3>", lambda e: self.open_stack())
        
        chat_btn = Button(self.header, text="🤖 聊天", font=("Helvetica", 10, "bold"),
                  bg="#1FA2FF", fg="white", bd=0, relief='flat', cursor="hand2",
                  command=lambda: ChatWindow(self.window))
        chat_btn.place(relx=0.95, y=28, anchor='ne', width=90, height=36)
        try:
            self._attach_hover_effect(chat_btn, "#1FA2FF")
            ToolTip(chat_btn, "与LLM聊天")
        except Exception:
            pass
  
    def _draw_header_gradient(self, canvas, h, c1, c2):
        # 清除旧图形
        canvas.delete("grad")
        width = canvas.winfo_width() or self.window.winfo_width() or 980
        steps = 60
        for i in range(steps):
            t = i / (steps - 1)
            color = blend_hex(c1, c2, t)
            y0 = int(i * (h / steps))
            y1 = int((i+1) * (h / steps))
            canvas.create_rectangle(0, y0, width, y1, outline=color, fill=color, tags="grad")
        # 波浪装饰
        points = []
        wave_h = 14
        for x in range(0, width+100, 20):
            y = h - (math.sin(x / 60.0) * wave_h + 8)
            points.append(x)
            points.append(y)
        canvas.create_polygon(*points, fill=blend_hex(c2, "#ffffff", 0.12), outline='', tags="grad")
        # 重新绘制标题文字在最上层
        canvas.tag_raise("title")
        canvas.tag_raise("subtitle")

    def _attach_hover_effect(self, widget, base_color):
        hover = lighten_hex(base_color, 0.18)
        def on_enter(e):
            try:
                e.widget.configure(bg=hover)
            except Exception:
                pass
        def on_leave(e):
            try:
                e.widget.configure(bg=base_color)
            except Exception:
                pass
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)

    # 以下函数保持不变，直接打开对应可视化窗口
    def open_linked_list(self):
        # self.window.destroy()
        linked_list_window = Toplevel(self.window)  
        linked_list_window.title("单链表可视化")
        linked_list_window.geometry("1350x730")
        linked_list_window.maxsize(1350, 730)
        linked_list_window.minsize(1350, 730)
        ll = LinkList(linked_list_window)
        register_visualizer("linked_list", ll)
        linked_list_window.mainloop()
    
    def open_sequence_list(self):
        # self.window.destroy()
        sequence_list_window = Toplevel(self.window)
        sequence_list_window.title("顺序表可视化")
        sequence_list_window.geometry("1350x730")
        sequence_list_window.maxsize(1350, 730)
        sequence_list_window.minsize(1350, 730)
        SequenceListVisualizer(sequence_list_window)
        sequence_list_window.mainloop()

    def open_stack(self):
        # self.window.destroy()
        stack_window = Toplevel(self.window)
        stack_window.title("栈可视化")
        stack_window.geometry("1350x730")
        stack_window.maxsize(1350, 730)
        stack_window.minsize(1350, 730)
        StackVisualizer(stack_window)
        stack_window.mainloop()

    def open_binary_tree(self):
        # self.window.destroy()
        binary_tree_window = Toplevel(self.window)
        binary_tree_window.title("二叉树可视化")
        binary_tree_window.geometry("1350x730")
        binary_tree_window.maxsize(1350, 730)
        binary_tree_window.minsize(1350, 730)
        BinaryTreeVisualizer(binary_tree_window)
        binary_tree_window.mainloop()

    def open_bst(self):
        # self.window.destroy()
        bst_window = Toplevel(self.window)
        bst_window.title("二叉搜索树可视化")
        bst_window.geometry("1350x730")
        bst_window.maxsize(1350, 730)
        bst_window.minsize(1350, 730)
        BSTVisualizer(bst_window)
        bst_window.mainloop()

    def open_huffman(self):
        # self.window.destroy()
        huffman_window = Toplevel(self.window)
        huffman_window.title("Huffman 可视化")
        huffman_window.geometry("1350x730")
        HuffmanVisualizer(huffman_window)
        huffman_window.mainloop()

    def open_avl(self):
        # self.window.destroy()
        avl_window = Toplevel(self.window)
        avl_window.title("AVL 可视化")
        avl_window.geometry("1350x730")
        AVLVisualizer(avl_window)
        avl_window.mainloop()

if __name__ == '__main__':
    root = Tk()
    app = MainInterface(root)
    root.mainloop()
