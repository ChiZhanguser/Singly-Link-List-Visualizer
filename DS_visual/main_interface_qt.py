import sys
import threading
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QGridLayout, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt

def run_linked_list():
    from linked_list.linked_list_visual import LinkList
    import tkinter as tk
    root = tk.Tk()
    root.title("单链表可视化")
    root.geometry("1350x730")
    LinkList(root)
    root.mainloop()

def run_sequence_list():
    from sequence_list.sequence_list_visual import SequenceListVisualizer
    import tkinter as tk
    root = tk.Tk()
    root.title("顺序表可视化")
    root.geometry("1350x730")
    SequenceListVisualizer(root)
    root.mainloop()

def run_stack():
    from stack.stack_visual import StackVisualizer
    import tkinter as tk
    root = tk.Tk()
    root.title("栈可视化")
    root.geometry("1350x730")
    StackVisualizer(root)
    root.mainloop()

def run_binary_tree():
    from binary_tree.linked_storage.linked_storage_visual import BinaryTreeVisualizer
    import tkinter as tk
    root = tk.Tk()
    root.title("二叉树可视化")
    root.geometry("1350x730")
    BinaryTreeVisualizer(root)
    root.mainloop()

def run_bst():
    from binary_tree.bst.bst_visual import BSTVisualizer
    import tkinter as tk
    root = tk.Tk()
    root.title("二叉搜索树可视化")
    root.geometry("1350x730")
    BSTVisualizer(root)
    root.mainloop()

def run_huffman():
    from binary_tree.huffman_tree.huffman_visual import HuffmanVisualizer
    import tkinter as tk
    root = tk.Tk()
    root.title("Huffman 可视化")
    root.geometry("1350x730")
    HuffmanVisualizer(root)
    root.mainloop()

def run_avl():
    from avl.avl_visual import AVLVisualizer
    import tkinter as tk
    root = tk.Tk()
    root.title("AVL 可视化")
    root.geometry("1350x730")
    AVLVisualizer(root)
    root.mainloop()

def run_rbt():
    from rbt.rbt_visual import RBTVisualizer
    import tkinter as tk
    root = tk.Tk()
    root.title("红黑树可视化")
    root.geometry("1350x730")
    RBTVisualizer(root)
    root.mainloop()

def run_trie():
    from trie.trie_visual import TrieVisualizer
    import tkinter as tk
    root = tk.Tk()
    root.title("Trie（前缀树）可视化")
    root.geometry("1350x730")
    TrieVisualizer(root)
    root.mainloop()

def run_bplustree():
    from bplustree.bplustree_visual import BPlusVisualizer
    import tkinter as tk
    root = tk.Tk()
    root.title("B+树 可视化")
    root.geometry("1350x730")
    BPlusVisualizer(root)
    root.mainloop()

def run_circular_queue():
    from circular_queue.circular_queue_visual import CircularQueueVisualizer
    import tkinter as tk
    root = tk.Tk()
    root.title("循环队列 可视化")
    root.geometry("1350x730")
    CircularQueueVisualizer(root)
    root.mainloop()

def run_hashtable():
    from hashtable.hashtable_visual import HashtableVisualizer
    import tkinter as tk
    root = tk.Tk()
    root.title("哈希表 可视化")
    root.geometry("1350x730")
    HashtableVisualizer(root)
    root.mainloop()

class MainInterfaceQt(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("数据结构可视化工具 — 张驰 (PyQt5)")
        self.setGeometry(100, 100, 1100, 700)
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        title = QLabel("数据结构可视化工具", self)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size:38px;font-weight:bold;color:#062A4A;")
        layout.addWidget(title)
        subtitle = QLabel("交互、演示与教学 — 顶级视觉体验", self)
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("font-size:18px;color:#4d6b88;")
        layout.addWidget(subtitle)
        grid = QGridLayout()
        layout.addLayout(grid)
        btns = [
            ("🔗 单链表", run_linked_list),
            ("📋 顺序表", run_sequence_list),
            ("📚 栈", run_stack),
            ("🌳 二叉树链式存储", run_binary_tree),
            ("🔎 二叉搜索树", run_bst),
            ("🔠 Huffman树", run_huffman),
            ("⚖️ AVL", run_avl),
            ("🔴 红黑树", run_rbt),
            ("🔤 Trie", run_trie),
            ("🗃️ B+树", run_bplustree),
            ("🔁 循环队列", run_circular_queue),
            ("🔑 散列表", run_hashtable)
        ]
        for i, (label, func) in enumerate(btns):
            btn = QPushButton(label, self)
            btn.setFixedHeight(70)
            btn.setStyleSheet("""
                QPushButton {
                    font-size:22px;
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #3a8dde, stop:1 #70b7ff);
                    color: white;
                    border-radius: 18px;
                    border: none;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #70b7ff, stop:1 #3a8dde);
                }
            """)
            btn.clicked.connect(lambda _, f=func: threading.Thread(target=f, daemon=True).start())
            grid.addWidget(btn, i // 3, i % 3)
        copyright = QLabel("© 张驰 的 数据结构可视化工具", self)
        copyright.setAlignment(Qt.AlignRight)
        copyright.setStyleSheet("font-size:14px;color:#7a8897;")
        layout.addWidget(copyright)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainInterfaceQt()
    win.show()
    sys.exit(app.exec_())
