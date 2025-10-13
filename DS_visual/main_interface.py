from tkinter import *
from tkinter import ttk, messagebox
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
from rbt.rbt_visual import RBTVisualizer
from circular_queue.circular_queue_visual import CircularQueueVisualizer
from trie.trie_visual import TrieVisualizer
from bplustree.bplustree_visual import BPlusVisualizer
from hashtable.hashtable_visual import HashtableVisualizer
import random
import time

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
        # 放大窗口以容纳更多按钮与更大卡片区
        self.window.geometry("1280x880")
        self.window.minsize(1000, 700)
        style = ttk.Style(self.window)
        style.theme_use('clam')
        self.window.configure(bg="#EAF5FF")
        header_h = 200
        self.header = Canvas(self.window, height=header_h, bd=0, highlightthickness=0, bg=self.window['bg'])
        self.header.pack(fill=X)
        self._anim_phase = 0.0
        self._particle_positions = [(random.uniform(40, 1180), random.uniform(18, header_h-18),
                                     random.uniform(6, 26), random.uniform(0.12, 0.6)) for _ in range(12)]
        self._draw_header_gradient(self.header, header_h, "#3a8dde", "#70b7ff")
        self._animate_header()
        self.header.create_text(48, 52, anchor='w', text="数据结构可视化工具",
                                font=("Helvetica", 36, "bold"), fill="#062A4A", tags="title")
        self.header.create_text(48, 120, anchor='w',
                                text="交互、演示与教学 — 支持链表/顺序表/栈/多种树结构",
                                font=("Helvetica", 14), fill="#EAF6FF", tags="subtitle")
        shadow = Frame(self.window, bg="#d7e9ff", bd=8)
        shadow.place(relx=0.5, y=header_h - 12, anchor='n', relwidth=0.92, height=560)
        card = Frame(self.window, bg="white", relief="flat", bd=0, highlightthickness=0)
        card.place(relx=0.5, y=header_h - 16, anchor='n', relwidth=0.92, height=540)
        card.grid_propagate(False)
        card.grid_rowconfigure(0, weight=0)
        card.grid_rowconfigure(1, weight=1)
        card.grid_columnconfigure(0, weight=1)
        top_frame = Frame(card, bg="white", bd=0)
        top_frame.grid(row=0, column=0, sticky="ew", padx=28, pady=(24, 12))
        subtitle = Label(top_frame, text="选择可视化模块", font=("Helvetica", 22, "bold"), bg="white", fg="#0b3a66")
        subtitle.grid(row=0, column=0, sticky="w")
        desc = Label(top_frame, text="点击下面的按钮进入对应数据结构的交互演示。支持键盘/鼠标/DSL/自然语言交互。",
                     font=("Helvetica", 12), bg="white", fg="#4d6b88")
        desc.grid(row=1, column=0, sticky="w", pady=(6, 0))
        btn_frame = Frame(card, bg="white")
        btn_frame.grid(row=1, column=0, sticky="nsew", padx=28, pady=14)
        cols = 3
        for i in range(cols):
            btn_frame.grid_columnconfigure(i, weight=1)
        btns = [
            ("单链表", "#FF8C42", "🔗", self.open_linked_list, "单链表（单向）可视化与操作"),
            ("顺序表", "#2ECC71", "📋", self.open_sequence_list, "基于数组的顺序表演"),
            ("栈", "#8E44AD", "📚", self.open_stack, "后进先出（LIFO）结构演示"),
            ("二叉树链式存储", "#E74C3C", "🌳", self.open_binary_tree, "链式存储的普通二叉树"),
            ("二叉搜索树", "#3498DB", "🔎", self.open_bst, "BST：插入/删除/查找演示"),
            ("Huffman树", "#A0522D", "🔠", self.open_huffman, "基于频率的编码树（Huffman）"),
            ("Trie（前缀树）", "#FF6F61", "🔤", self.open_trie, "Trie（前缀树）可视化 — 自动补全 / 前缀查询"),
            ("B+树", "#16A085", "🗃️", self.open_bplustree, "B+树（B+ Tree）可视化 — 索引 / 磁盘页 演示"),
            ("AVL (平衡二叉树)", "#5DADE2", "⚖️", self.open_avl, "自平衡 AVL 树演示"),
            ("红黑树", "#D84315", "🔴", self.open_rbt, "红黑树（Red-Black Tree）可视化"),
            ("循环队列", "#F1C40F", "🔁", self.open_circular_queue, "循环队列（Ring Buffer）可视化 — 入队/出队/环绕示意"),
            ("散列表", "#2C3E50", "🔑", self.open_hashtable, "散列表（Hash Table）可视化 — 键值对存储")
        ]
        for idx, (label, color, emoji, cmd, tip) in enumerate(btns):
            col = idx % cols
            row = idx // cols
            btn = Button(btn_frame, text=f"{emoji}  {label}", font=("Helvetica", 15, "bold"),
                         bd=0, relief='flat', activebackground=lighten_hex(color, 0.10),
                         bg=color, fg="white", cursor="hand2", width=22, height=2, command=cmd)
            btn.grid(row=row, column=col, sticky="nsew", padx=10, pady=10, ipadx=6, ipady=12)
            btn_frame.grid_rowconfigure(row, weight=1, minsize=84)
            self._attach_hover_effect(btn, color)
            ToolTip(btn, tip)
        bottom_bar = Frame(self.window, bg="#F4F8FF", height=44)
        bottom_bar.pack(fill=X, side=BOTTOM)
        copyright_label = Label(bottom_bar, text="© 张驰 的 数据结构可视化工具", bg="#F4F8FF", fg="#7a8897",
                                font=("Arial", 10))
        copyright_label.pack(side=LEFT, padx=12)
        status_label = Label(bottom_bar, text="23070215", bg="#F4F8FF", fg="#7a8897", font=("Arial", 10))
        status_label.pack(side=RIGHT, padx=12)
        self.window.bind("<Key-1>", lambda e: self.open_linked_list())
        self.window.bind("<Key-2>", lambda e: self.open_sequence_list())
        self.window.bind("<Key-3>", lambda e: self.open_stack())
        self.window.bind("<Key-4>", lambda e: self.open_trie())
        self.window.bind("<Key-5>", lambda e: self.open_bplustree())
        chat_btn = Button(self.header, text="🤖 聊天", font=("Helvetica", 14, "bold"),
                          bg="#1FA2FF", fg="white", bd=0, relief='flat', cursor="hand2",
                          command=lambda: ChatWindow(self.window))
        chat_btn.place(relx=0.96, y=28, anchor='ne', width=110, height=44)
        try:
            self._attach_hover_effect(chat_btn, "#1FA2FF")
            ToolTip(chat_btn, "通过LLM交互")
        except Exception:
            pass

    def _draw_header_gradient(self, canvas, h, c1, c2):
        canvas.delete("grad")
        width = canvas.winfo_width() or self.window.winfo_width() or 1280
        steps = 72
        for i in range(steps):
            t = i / (steps - 1)
            color = blend_hex(c1, c2, t)
            y0 = int(i * (h / steps))
            y1 = int((i+1) * (h / steps))
            canvas.create_rectangle(0, y0, width, y1, outline=color, fill=color, tags="grad")
        points = []
        wave_h = 18
        for x in range(0, width+160, 20):
            y = h - (math.sin(x / 60.0) * wave_h + 8)
            points.append(x)
            points.append(y)
        canvas.create_polygon(*points, fill=blend_hex(c2, "#ffffff", 0.12), outline='', tags="grad")
        for i, (px, py, rad, alpha) in enumerate(self._particle_positions):
            canvas.create_oval(px-rad, py-rad, px+rad, py+rad, fill=blend_hex("#ffffff", c2, 0.7), outline="", tags="grad")
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

    def _animate_header(self):
        self._anim_phase = (self._anim_phase + 0.006) % 1.0
        new_positions = []
        for (x, y, r, a) in self._particle_positions:
            nx = x + math.sin(time.time() * 0.18 + x) * 0.4
            if nx < 20: nx = 1240
            if nx > 1240: nx = 20
            ny = y + math.sin(time.time() * 0.85 + x) * 4 * a
            new_positions.append((nx, ny, r, a))
        self._particle_positions = new_positions
        try:
            self._draw_header_gradient(self.header, 200, "#3a8dde", "#70b7ff")
        except Exception:
            pass
        self.window.after(40, self._animate_header)

    def open_linked_list(self):
        linked_list_window = Toplevel(self.window)
        linked_list_window.title("单链表可视化")
        linked_list_window.geometry("1350x730")
        linked_list_window.maxsize(1350, 730)
        linked_list_window.minsize(1350, 730)
        ll = LinkList(linked_list_window)
        register_visualizer("linked_list", ll)
        chat_window = ChatWindow(self.window)
        chat_window.win.transient(linked_list_window)  # 设置为主窗口的子窗口
        chat_window.win.geometry("200x300")  # 缩小尺寸
        ll.set_chat_window(chat_window)
        linked_list_window.mainloop()

    def open_sequence_list(self):
        sequence_list_window = Toplevel(self.window)
        sequence_list_window.title("顺序表可视化")
        sequence_list_window.geometry("1350x730")
        sequence_list_window.maxsize(1350, 730)
        sequence_list_window.minsize(1350, 730)
        SequenceListVisualizer(sequence_list_window)
        chat_window = ChatWindow(self.window)
        chat_window.win.transient(sequence_list_window)  # 设置为主窗口的子窗口
        chat_window.win.geometry("200x300")  # 缩小尺寸
        sequence_list_window.mainloop()

    def open_stack(self):
        stack_window = Toplevel(self.window)
        stack_window.title("栈可视化")
        stack_window.geometry("1350x730")
        stack_window.maxsize(1350, 730)
        stack_window.minsize(1350, 730)
        StackVisualizer(stack_window)
        chat_window = ChatWindow(self.window)
        chat_window.win.transient(stack_window)  # 设置为主窗口的子窗口
        chat_window.win.geometry("200x300")  # 缩小尺寸
        stack_window.mainloop()

    def open_binary_tree(self):
        binary_tree_window = Toplevel(self.window)
        binary_tree_window.title("二叉树可视化")
        binary_tree_window.geometry("1350x730")
        binary_tree_window.maxsize(1350, 730)
        binary_tree_window.minsize(1350, 730)
        BinaryTreeVisualizer(binary_tree_window)
        binary_tree_window.mainloop()

    def open_bst(self):
        bst_window = Toplevel(self.window)
        bst_window.title("二叉搜索树可视化")
        bst_window.geometry("1350x730")
        bst_window.maxsize(1350, 730)
        bst_window.minsize(1350, 730)
        BSTVisualizer(bst_window)
        bst_window.mainloop()

    def open_huffman(self):
        huffman_window = Toplevel(self.window)
        huffman_window.title("Huffman 可视化")
        huffman_window.geometry("1350x730")
        HuffmanVisualizer(huffman_window)
        huffman_window.mainloop()

    def open_avl(self):
        avl_window = Toplevel(self.window)
        avl_window.title("AVL 可视化")
        avl_window.geometry("1350x730")
        AVLVisualizer(avl_window)
        avl_window.mainloop()

    def open_rbt(self):
        rbt_window = Toplevel(self.window)
        rbt_window.title("红黑树可视化")
        rbt_window.geometry("1350x730")
        rbt_window.maxsize(1350, 730)
        rbt_window.minsize(1350, 730)
        rb = RBTVisualizer(rbt_window)
        try:
            register_visualizer("rbt", rb)
        except Exception:
            pass
        rbt_window.mainloop()

    def open_trie(self):
        trie_window = Toplevel(self.window)
        trie_window.title("Trie（前缀树）可视化")
        trie_window.geometry("1350x730")
        trie_window.maxsize(1350, 730)
        trie_window.minsize(1350, 730)
        try:
            t = TrieVisualizer(trie_window)
            try:
                register_visualizer("trie", t)
            except Exception:
                pass
        except Exception as e:
            messagebox.showerror("错误", f"无法打开 Trie 可视化：{e}")
        trie_window.mainloop()

    def open_bplustree(self):
        bpt_window = Toplevel(self.window)
        bpt_window.title("B+树 可视化")
        bpt_window.geometry("1350x730")
        bpt_window.maxsize(1350, 730)
        bpt_window.minsize(1350, 730)
        try:
            bp = BPlusVisualizer(bpt_window)
            try:
                register_visualizer("bplustree", bp)
            except Exception:
                pass
        except Exception as e:
            messagebox.showerror("错误", f"无法打开 B+树 可视化：{e}")
        bpt_window.mainloop()
    
    def open_circular_queue(self):
        cq_window = Toplevel(self.window)
        cq_window.title("循环队列 可视化")
        cq_window.geometry("1350x730")
        cq_window.maxsize(1350, 730)
        cq_window.minsize(1350, 730)
        try:
            cq = CircularQueueVisualizer(cq_window)
            try:
                register_visualizer("circular_queue", cq)
            except Exception:
                pass
        except Exception as e:
            messagebox.showerror("错误", f"无法打开 循环队列 可视化：{e}")
        cq_window.mainloop()
        
    def open_hashtable(self):
        ht_window = Toplevel(self.window)
        ht_window.title("哈希表 可视化")
        ht_window.geometry("1350x730")
        ht_window.maxsize(1350, 730)
        ht_window.minsize(1350, 730)
        try:
            ht = HashtableVisualizer(ht_window)
            try:
                register_visualizer("hashtable", ht)
            except Exception:
                pass
        except Exception as e:
            messagebox.showerror("错误", f"无法打开 哈希表 可视化：{e}")
        ht_window.mainloop()


if __name__ == '__main__':
    root = Tk()
    app = MainInterface(root)
    root.mainloop()
