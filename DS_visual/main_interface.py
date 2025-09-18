from tkinter import *
from tkinter import ttk
from linked_list.linked_list_visual import LinkList
from sequence_list.sequence_list_visual import SequenceListVisualizer
from stack.stack_visual import StackVisualizer
from binary_tree.linked_storage.linked_storage_visual import BinaryTreeVisualizer
from binary_tree.bst.bst_visual import BSTVisualizer
from binary_tree.huffman_tree.huffman_visual import HuffmanVisualizer
from avl.avl_visual import AVLVisualizer

class MainInterface:
    def __init__(self, root):
        self.window = root
        self.window.title("数据结构可视化工具")
        self.window.geometry("600x500")
        self.window.maxsize(1200, 1000)
        self.window.minsize(800, 700)
        self.window.config(bg="lightblue")
        
        # 标题
        title_label = Label(self.window, text="数据结构可视化工具", 
                          font=("Arial", 24, "bold"), bg="lightblue", fg="darkblue")
        title_label.pack(pady=40)
        
        # 说明文字
        desc_label = Label(self.window, text="请选择要可视化的数据结构类型：", 
                         font=("Arial", 16), bg="lightblue", fg="black")
        desc_label.pack(pady=20)
        
        # 按钮框架
        button_frame = Frame(self.window, bg="lightblue")
        button_frame.pack(pady=30)
        
        # 单链表按钮
        linked_list_btn = Button(button_frame, text="单链表", font=("Arial", 14), 
                               width=15, height=2, bg="orange", fg="white",
                               command=self.open_linked_list)
        linked_list_btn.grid(row=0, column=0, padx=20, pady=10)
        
        # 顺序表按钮
        sequence_list_btn = Button(button_frame, text="顺序表", font=("Arial", 14), 
                                 width=15, height=2, bg="green", fg="white",
                                 command=self.open_sequence_list)
        sequence_list_btn.grid(row=0, column=1, padx=20, pady=10)
        
        # 栈按钮
        stack_btn = Button(button_frame, text="栈", font=("Arial", 14), 
                         width=15, height=2, bg="purple", fg="white",
                         command=self.open_stack)
        stack_btn.grid(row=1, column=0, padx=20, pady=10)
        
        # 二叉树链式按钮
        binary_tree_btn = Button(button_frame, text="二叉树链式存储", font=("Arial", 14), 
                        width=15, height=2, bg="red", fg="white",
                        command=self.open_binary_tree)
        binary_tree_btn.grid(row=1, column=1, padx=20, pady=10)
        
        # BST
        bst_btn = Button(button_frame, text="二叉搜索树", font=("Arial", 14), 
                        width=15, height=2, bg="blue", fg="white",
                        command=self.open_bst)
        bst_btn.grid(row=2, column=0, padx=20, pady=10)
        
        # huffman
        huffman_btn = Button(button_frame, text="Huffman树", font=("Arial",14), width=15, height=2, bg="brown", fg="white",
                     command=self.open_huffman)
        huffman_btn.grid(row=2, column=1, padx=20, pady=10)
        
        # AVL
        avl_btn = Button(button_frame, text="AVL (平衡二叉树)", font=("Arial",14), width=15, height=2, bg="#8E44AD", fg="white", command=self.open_avl)
        avl_btn.grid(row=3, column=0, padx=20, pady=10)

        
        # 版权信息
        copyright_label = Label(self.window, text="© 张驰的数据结构可视化工具", 
                              font=("Arial", 10), bg="lightblue", fg="gray")
        copyright_label.pack(side=BOTTOM, pady=10)
           
    def open_linked_list(self):
        # 关闭主界面
        self.window.destroy()
        # 打开单链表界面
        linked_list_window = Tk()
        linked_list_window.title("单链表可视化")
        linked_list_window.geometry("1350x730")
        linked_list_window.maxsize(1350, 730)
        linked_list_window.minsize(1350, 730)
        LinkList(linked_list_window)
        linked_list_window.mainloop()
    
    def open_sequence_list(self):
        # 关闭主界面
        self.window.destroy()
        # 打开顺序表界面
        sequence_list_window = Tk()
        sequence_list_window.title("顺序表可视化")
        sequence_list_window.geometry("1350x730")
        sequence_list_window.maxsize(1350, 730)
        sequence_list_window.minsize(1350, 730)
        SequenceListVisualizer(sequence_list_window)
        sequence_list_window.mainloop()
    
    def open_stack(self):
        # 关闭主界面
        self.window.destroy()
        # 打开栈界面
        stack_window = Tk()
        stack_window.title("栈可视化")
        stack_window.geometry("1350x730")
        stack_window.maxsize(1350, 730)
        stack_window.minsize(1350, 730)
        StackVisualizer(stack_window)
        stack_window.mainloop()
        
    def open_binary_tree(self):
        self.window.destroy()
        binary_tree_window = Tk()
        binary_tree_window.title("二叉树可视化")
        binary_tree_window.geometry("1350x730")
        binary_tree_window.maxsize(1350, 730)
        binary_tree_window.minsize(1350, 730)
        BinaryTreeVisualizer(binary_tree_window)
        binary_tree_window.mainloop()
        
    def open_bst(self):
        self.window.destroy()
        bst_window = Tk()
        bst_window.title("二叉搜索树可视化")
        bst_window.geometry("1350x730")
        bst_window.maxsize(1350, 730)
        bst_window.minsize(1350, 730)
        BSTVisualizer(bst_window)
        bst_window.mainloop()
    def open_huffman(self):
        self.window.destroy()
        win = Tk()
        win.title("Huffman 可视化")
        win.geometry("1350x730")
        HuffmanVisualizer(win)
        win.mainloop()
    def open_avl(self):
        self.window.destroy()
        avl_window = Tk()
        avl_window.title("AVL 可视化")
        avl_window.geometry("1350x730")
        AVLVisualizer(avl_window)
        avl_window.mainloop()

if __name__ == '__main__':
    window = Tk()
    app = MainInterface(window)
    window.mainloop()
