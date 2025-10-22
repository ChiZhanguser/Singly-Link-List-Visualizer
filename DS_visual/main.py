from tkinter import * 
from tkinter import ttk, messagebox
import traceback, sys
import random, math, time


def try_import(name, pkg):
    try:
        mod = __import__(pkg, fromlist=[name])
        return getattr(mod, name)
    except Exception:
        return None


LinkList = try_import("LinkList", "linked_list.linked_list_visual")
SequenceListVisualizer = try_import("SequenceListVisualizer", "sequence_list.sequence_list_visual")
StackVisualizer = try_import("StackVisualizer", "stack.stack_visual")
BinaryTreeVisualizer = try_import("BinaryTreeVisualizer", "binary_tree.linked_storage.linked_storage_visual")
BSTVisualizer = try_import("BSTVisualizer", "binary_tree.bst.bst_visual")
HuffmanVisualizer = try_import("HuffmanVisualizer", "binary_tree.huffman_tree.huffman_visual")
AVLVisualizer = try_import("AVLVisualizer", "avl.avl_visual")
RBTVisualizer = try_import("RBTVisualizer", "rbt.rbt_visual")
CircularQueueVisualizer = try_import("CircularQueueVisualizer", "circular_queue.circular_queue_visual")
TrieVisualizer = try_import("TrieVisualizer", "trie.trie_visual")
BPlusVisualizer = try_import("BPlusVisualizer", "bplustree.bplustree_visual")
HashtableVisualizer = try_import("HashtableVisualizer", "hashtable.hashtable_visual")

ChatWindow = try_import("ChatWindow", "llm.chat_window")


class EmbedHost(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.configure(bg="")
        self.pack(fill=BOTH, expand=True)

    def title(self, *_args, **_kwargs):
        return None
    def geometry(self, *_args, **_kwargs):
        return None
    def minsize(self, *_args, **_kwargs):
        return None
    def maxsize(self, *_args, **_kwargs):
        return None
    def resizable(self, *_args, **_kwargs):
        return None


class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("数据结构可视化工具")
        self.root.geometry("1500x820")
        self.root.minsize(1500, 820)

        self.bg_canvas = Canvas(self.root, highlightthickness=0, bd=0, bg="black")
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        try:
            self.root.tk.call('lower', self.bg_canvas._w)
        except Exception:
            pass
        self._static_stars = [(random.uniform(0,1), random.uniform(0,1), random.uniform(0.5,1.6)) for _ in range(160)]
        self._render_background()
        self.root.after(90, self._animate_stars)
        self._resize_job = None
        self.root.bind("<Configure>", self._on_configure)

        self.main_pane = PanedWindow(self.root, orient=HORIZONTAL)
        self.main_pane.pack(fill=BOTH, expand=True)

        self.sidebar = Frame(self.main_pane, width=220, bg="#1f2937")
        self.content = Frame(self.main_pane)
        self.main_pane.add(self.sidebar)
        self.main_pane.add(self.content)

        # ========== 美化顶部栏 ==========
        topbar = Frame(self.content, bg="#ffffff", height=70)
        topbar.pack(fill=X, side=TOP)
        topbar.pack_propagate(False)  # 保持固定高度
        
        # 应用现代样式
        self.style = ttk.Style(self.root)
        try:
            self.style.theme_use("vista")
        except Exception:
            pass
        self._apply_hidden_notebook_style()

        # ---- 左侧：Logo和标题 ----
        header_left = Frame(topbar, bg="#ffffff")
        header_left.pack(side=LEFT, padx=20, pady=15)
        
        # Logo容器（圆形背景）
        logo_frame = Frame(header_left, bg="#1FA2FF", width=40, height=40, relief=FLAT, bd=0)
        logo_frame.pack(side=LEFT, padx=(0, 12))
        logo_frame.pack_propagate(False)
        logo_label = Label(logo_frame, text="DS", bg="#1FA2FF", fg="white", 
                          font=("Segoe UI", 14, "bold"))
        logo_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # 主标题
        title_label = Label(header_left, text="数据结构可视化平台", 
                           bg="#ffffff", fg="#1a1a1a", font=("Segoe UI", 16, "bold"))
        title_label.pack(side=LEFT)
        
        # 副标题
        subtitle_label = Label(header_left, text="Data Structure Visualizer", 
                              bg="#ffffff", fg="#666666", font=("Segoe UI", 10))
        subtitle_label.pack(side=LEFT, padx=(8, 0), pady=(4, 0))

        # ---- 中间：当前结构指示器 ----
        header_center = Frame(topbar, bg="#ffffff")
        header_center.pack(side=LEFT, expand=True, fill=X, padx=40)
        
        # 当前结构标签 - 现代化设计
        current_frame = Frame(header_center, bg="#f8fafc", relief=SOLID, bd=1)
        current_frame.pack(side=TOP, pady=5)
        
        current_label = Label(current_frame, text="当前数据结构", bg="#f8fafc", 
                            fg="#666666", font=("Segoe UI", 9))
        current_label.pack(side=LEFT, padx=(12, 8), pady=4)
        
        self.structure_label = Label(current_frame, text="—", bg="#ffffff", fg="#1FA2FF", 
                                   font=("Segoe UI", 10, "bold"), relief=SOLID, bd=1, 
                                   padx=12, pady=4)
        self.structure_label.pack(side=LEFT, padx=(0, 12), pady=4)

        # ---- 右侧：功能区域 ----
        header_right = Frame(topbar, bg="#ffffff")
        header_right.pack(side=RIGHT, padx=20, pady=15)

        # 自然语言输入框 - 现代化设计
        from tkinter import StringVar
        self.nl_var = StringVar(value="")
        
        input_container = Frame(header_right, bg="#f1f5f9", relief=SOLID, bd=1)
        input_container.pack(side=LEFT, padx=(0, 12))
        
        # 输入图标
        input_icon = Label(input_container, text="🔍", bg="#f1f5f9", fg="#666666", 
                          font=("Segoe UI", 10))
        input_icon.pack(side=LEFT, padx=(12, 8))
        
        self.nl_entry = Entry(input_container, textvariable=self.nl_var, width=42, 
                             font=("Segoe UI", 10), fg="#374151", bg="#f1f5f9", 
                             relief=FLAT, bd=0, highlightthickness=0)
        self.nl_entry.insert(0, "请输入自然语言命令...")
        self.nl_entry.bind("<FocusIn>", lambda e: self.nl_entry.delete(0, END) if self.nl_entry.get() == "请输入自然语言命令..." else None)
        self.nl_entry.bind("<FocusOut>", lambda e: self.nl_entry.insert(0, "请输入自然语言命令...") if not self.nl_entry.get().strip() else None)
        self.nl_entry.bind("<Return>", self._on_nl_submit)
        self.nl_entry.pack(side=LEFT, padx=(0, 12), pady=8)
        self.nl_entry.bind("<Enter>", lambda e: self.status_label.config(text="输入自然语言命令并按回车提交"))
        self.nl_entry.bind("<Leave>", lambda e: self.status_label.config(text="© 张驰 的 数据结构可视化工具"))

        # AI 助手按钮 - 现代化设计
        ai_btn = Button(header_right, text="AI 助手", fg="#ffffff", bg="#1FA2FF",
                        activebackground="#52b6ff", activeforeground="#ffffff",
                        relief=FLAT, padx=24, pady=8, cursor="hand2",
                        font=("Segoe UI", 10, "bold"),
                        command=self._open_chat)
        ai_btn.pack(side=RIGHT)

        # 添加顶部装饰条
        decoration_frame = Frame(topbar, bg="#1FA2FF", height=3)
        decoration_frame.pack(fill=X, side=BOTTOM)

        # 隐藏 notebook 的样式（保持你原有逻辑）
        try:
            self.notebook = ttk.Notebook(self.content, style="Hidden.TNotebook")
            self.notebook.pack(fill=BOTH, expand=True, padx=10, pady=(0, 10))
            self.notebook.bind("<<NotebookTabChanged>>", self._ensure_tab_loaded)
        except Exception:
            # 兼容性：如果创建失败，仍然继续但提示
            self.notebook = ttk.Notebook(self.content)
            self.notebook.pack(fill=BOTH, expand=True, padx=10, pady=(0, 10))
            self.notebook.bind("<<NotebookTabChanged>>", self._ensure_tab_loaded)

        self.tabs = {}
        self.sidebar_btns = {}
        self._build_tabs()
        self._build_sidebar()
        try:
            self._update_sidebar_selection(next(iter(self.tabs.keys())))
        except Exception:
            pass

        status = Frame(self.root, bg="#111827")
        status.pack(fill=X, side=BOTTOM)
        # 保存状态栏的 label 方便更新
        self.status_label = Label(status, text="© 张驰 的 数据结构可视化工具", fg="#9ca3af", bg="#111827")
        self.status_label.pack(side=LEFT, padx=10)

        # 当前激活的数据结构 key（例如 "linked_list"）
        self.current_structure = None

    def _on_theme_change(self, _evt=None):
        try:
            self._apply_hidden_notebook_style()
            self.notebook.configure(style="Hidden.TNotebook")
        except Exception:
            pass

    def _open_chat(self):
        try:
            if ChatWindow is None:
                messagebox.showinfo("提示", "聊天模块不可用（llm 未安装或路径错误）")
                return
            # 设置主窗口实例到function_dispatcher
            from llm import function_dispatcher
            function_dispatcher.set_main_window_instance(self)
            chat_window = ChatWindow(self.root)
            self._center_chat_window(chat_window)
            self._ensure_tabs_hidden()
        except Exception as e:
            messagebox.showerror("错误", f"打开聊天窗口失败：{e}")
    
    def _center_chat_window(self, chat_window):
        try:
            chat_win = chat_window.win
            parent_x = self.root.winfo_x()
            parent_y = self.root.winfo_y()
            parent_width = self.root.winfo_width() or 1500
            parent_height = self.root.winfo_height() or 820
            window_width = 880
            window_height = 660
            
            x_pos = parent_x + (parent_width - window_width) // 2
            y_pos = parent_y + (parent_height - window_height) // 2
            
            chat_win.geometry(f"{window_width}x{window_height}+{x_pos}+{y_pos}")
        except Exception:
            pass
    
    def _ensure_tabs_hidden(self):
        try:
            self._apply_hidden_notebook_style()
            self.notebook.configure(style="Hidden.TNotebook")
        except Exception:
            pass

    def _render_background(self):
        try:
            w = max(200, self.root.winfo_width() or 1350)
            h = max(200, self.root.winfo_height() or 820)
            self.bg_canvas.delete("bg")
            steps = 56
            for i in range(steps):
                t = i / max(1, steps - 1)
                color = self._blend_hex("#000000", "#001f3f", t)
                y0 = int(i * (h / steps)); y1 = int((i + 1) * (h / steps))
                self.bg_canvas.create_rectangle(0, y0, w, y1, fill=color, outline=color, tags="bg")
            for (rx, ry, r) in self._static_stars:
                sx = int(rx * w); sy = int(ry * h)
                self.bg_canvas.create_oval(sx - r, sy - r, sx + r, sy + r, fill="#ffffff", outline="", tags="bg")
            try:
                self.root.tk.call('lower', self.bg_canvas._w)
            except Exception:
                pass
        except Exception:
            traceback.print_exc()

    def _on_configure(self, _evt=None):
        try:
            if self._resize_job is not None:
                self.root.after_cancel(self._resize_job)
            def repaint():
                try:
                    self.root.update_idletasks()
                except Exception:
                    pass
                self._render_background()
            self._resize_job = self.root.after(80, repaint)
        except Exception:
            pass

    def _animate_stars(self):
        try:
            w = max(200, self.root.winfo_width() or 1350)
            h = max(200, self.root.winfo_height() or 820)
            for _ in range(8):
                x = random.randint(8, max(9, w - 8))
                y = random.randint(8, max(9, h - 8))
                c = random.choice(["#e6f4ff", "#ffffff", "#cfe8ff"]) 
                self.bg_canvas.create_oval(x-1, y-1, x+1, y+1, fill=c, outline="", tags="twinkle")
            self.bg_canvas.after(260, lambda: self.bg_canvas.delete("twinkle"))
        except Exception:
            pass
        self.root.after(120, self._animate_stars)

    def _apply_hidden_notebook_style(self):
        try:
            self.style.layout("Hidden.TNotebook", [("Notebook.client", {"sticky": "nswe"})])
            self.style.layout("Hidden.TNotebook.Tab", [])
            try:
                self.style.layout("TNotebook.Tab", [])
            except Exception:
                pass
        except Exception:
            pass

    def _blend_hex(self, c1, c2, t):
        def h2rgb(h):
            h = h.lstrip('#')
            return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
        r1,g1,b1 = h2rgb(c1); r2,g2,b2 = h2rgb(c2)
        r = int(r1 + (r2 - r1) * t); g = int(g1 + (g2 - g1) * t); b = int(b1 + (b2 - b1) * t)
        return f"#{r:02x}{g:02x}{b:02x}"

    def _build_sidebar(self):
        Label(self.sidebar, text="数据结构", bg="#1f2937", fg="white", font=("Segoe UI", 12, "bold")).pack(fill=X, pady=(8, 6))

        def add_btn(title, tab_key):
            btn = Button(self.sidebar, text=title, anchor="w", relief=FLAT, fg="#e5e7eb", bg="#111827",
                         activebackground="#374151", activeforeground="white",
                         command=lambda: self._select_tab(tab_key))
            btn.pack(fill=X, padx=10, pady=4, ipady=6)
            self.sidebar_btns[tab_key] = btn

        for key, meta in self.tabs.items():
            add_btn(meta[3], key)

    def _select_tab(self, key):
        if key not in self.tabs: return
        frame = self.tabs[key][1]
        self.notebook.select(frame)
        self._update_sidebar_selection(key)

    def _build_tabs(self):
        def add_tab(key, title, ctor):
            frame = Frame(self.notebook)
            self.notebook.add(frame, text=title)
            self.tabs[key] = (ctor, frame, None, title)

        add_tab("linked_list", "单链表", LinkList)
        add_tab("sequence", "顺序表", SequenceListVisualizer)
        add_tab("stack", "栈", StackVisualizer)
        add_tab("binary_tree", "二叉树链式存储", BinaryTreeVisualizer)
        add_tab("bst", "二叉搜索树", BSTVisualizer)
        add_tab("huffman", "Huffman树", HuffmanVisualizer)
        add_tab("trie", "Trie", TrieVisualizer)
        add_tab("bplus", "B+树", BPlusVisualizer)
        add_tab("avl", "AVL", AVLVisualizer)
        add_tab("rbt", "红黑树", RBTVisualizer)
        add_tab("cqueue", "循环队列", CircularQueueVisualizer)
        add_tab("hashtable", "散列表", HashtableVisualizer)

    def _ensure_tab_loaded(self, _evt=None):
        try:
            current = self.notebook.select()
            selected_key = None
            for key, (_ctor, frame, _inst, _title) in self.tabs.items():
                if str(frame) == current:
                    selected_key = key
                    break
            if selected_key is not None:
                # 更新选择（并同步结构标签）
                self._update_sidebar_selection(selected_key)
            for key, (ctor, frame, inst, _title) in self.tabs.items():
                if str(frame) == current and inst is None:
                    if ctor is None:
                        Label(frame, text="模块未找到", fg="red").pack(padx=20, pady=20)
                        self.tabs[key] = (ctor, frame, False, _title)  # mark attempted
                        return
                    try:
                        frame.pack_propagate(False)
                        host = EmbedHost(frame)
                        instance = ctor(host)  # 存储实例而不是布尔值
                        print(f"DEBUG: Created instance of type: {type(instance).__name__}")  # 调试输出
                        self.tabs[key] = (ctor, frame, instance, _title)  # 存储实际实例
                    except Exception:
                        traceback.print_exc()
                        self.tabs[key] = (ctor, frame, False, _title)
                        Label(frame, text="加载失败，请查看控制台", fg="red").pack(padx=20, pady=20)
                    # Keep tabs hidden in case style was reset by theme/widget creation
                    try:
                        self._apply_hidden_notebook_style()
                        self.notebook.configure(style="Hidden.TNotebook")
                    except Exception:
                        pass
                    return
        except Exception:
            traceback.print_exc()

    def _update_sidebar_selection(self, active_key):
        try:
            for key, btn in self.sidebar_btns.items():
                if key == active_key:
                    btn.configure(bg="#2dd4bf", fg="#0b1321", relief=SUNKEN, activebackground="#14b8a6", activeforeground="#0b1321")
                else:
                    btn.configure(bg="#111827", fg="#e5e7eb", relief=FLAT, activebackground="#374151", activeforeground="#ffffff")
        except Exception:
            pass
        # 更新当前结构变量与界面标签
        try:
            self.current_structure = active_key
            # 获取友好的显示名称
            display_name = dict(self.tabs).get(active_key, [None, None, None, active_key])[3]
            display_text = f"当前: {display_name}" if active_key else "当前: —"
            if hasattr(self, "structure_label") and self.structure_label:
                self.structure_label.config(text=display_name if active_key else "—")
            # 更新状态栏简要提示
            if hasattr(self, "status_label") and self.status_label:
                self.status_label.config(text=f"当前数据结构：{display_name}    © 张驰 的 数据结构可视化工具")
        except Exception:
            pass

    # ---------- 新增：自然语言输入的提交钩子 -------------
    def _get_current_tab_key(self):
        """返回当前选中的 tab key（或 None）"""
        try:
            current = self.notebook.select()
            for key, (_ctor, frame, _inst, _title) in self.tabs.items():
                if str(frame) == current:
                    return key
        except Exception:
            pass
        return None

    def _on_nl_submit(self, event=None):
        """
        自然语言输入回车处理钩子 - 将自然语言转换为DSL并执行
        """
        try:
            # 获取输入文本
            text = self.nl_var.get().strip()
            if not text:
                return "break"

            # 获取当前数据结构类型
            current_tab_key = self._get_current_tab_key()
            if not current_tab_key:
                messagebox.showerror("错误", "请先选择一个数据结构类型")
                return "break"

            # 初始化LLM客户端并设置函数调用
            from llm.doubao_client import DoubaoClient
            client = DoubaoClient()

            # 准备系统提示和函数定义
            system_prompt = (
                "你是一个数据结构可视化助手。你需要将用户的自然语言指令转换为规范的DSL命令。\n"
                "请根据当前数据结构类型，按照以下格式转换：\n\n"
                "1. 通用操作:\n"
                "   - clear（清空）\n\n"
                "2. 链表/顺序表操作:\n"
                "   - 末尾插入：insert VALUE\n"
                "   - 指定位置插入：insert VALUE at POSITION 或 insert_at POSITION VALUE\n"
                "   - 删除操作：delete first/last/POSITION\n"
                "   - 批量创建：create VALUE1,VALUE2,VALUE3\n\n"
                "3. 栈操作:\n"
                "   - 压栈：push VALUE\n"
                "   - 弹栈：pop\n\n"
                "4. 二叉搜索树操作:\n"
                "   - 插入：insert VALUE\n"
                "   - 查找：search VALUE\n"
                "   - 删除：delete VALUE\n"
                "   - 批量创建：create VALUE1,VALUE2,VALUE3\n\n"
                "5. 循环队列操作:\n"
                "   - 入队：enqueue VALUE 或 enq VALUE\n"
                "   - 出队：dequeue 或 deq\n"
                "   - 清空：clear\n\n"
                "6. 哈夫曼树操作:\n"
                "   - 创建：create VALUE1,VALUE2,VALUE3\n"
                "   - 清空：clear\n\n"
                "示例转换：\n"
                "- '查找23' -> 'search 23'\n"
                "- '入队5' -> 'enqueue 5'\n"
                "- '压入6' -> 'push 6'\n"
                "- '删除队首元素' -> 'dequeue'\n"
                "仅返回转换后的命令，不要添加任何额外解释。"
            )

            # 发送请求给LLM（直接作为文本命令处理）
            response = client.send_message(
                text=text,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text}
                ],
                temperature=0.1  # 降低随机性，使输出更确定
            )

            print(f"LLM Response: {response}")  # 调试输出

            # 清理DSL命令（去除多余的空格和引号）
            dsl_command = response.strip().strip("'\"")
            if not dsl_command:
                messagebox.showerror("错误", "无法理解您的指令")
                print("Empty DSL command")
                return "break"

            print(f"Converted DSL command: {dsl_command}")  # 调试输出

            # 获取当前可视化实例
            current_frame = self.notebook.select()
            found_instance = False

            for key, (ctor, frame, instance, title) in self.tabs.items():
                if str(frame) == str(current_frame) and instance:
                    found_instance = True
                    print(f"Found visualizer instance: {key}")  # 调试输出
                    
                    # 直接使用DSL处理函数，不需要通过dsl_var
                    from DSL_utils import process_command
                    try:
                        print(f"DEBUG: Instance type in main: {type(instance).__name__}")
                        print(f"DEBUG: Has node_value_store: {hasattr(instance, 'node_value_store')}")
                        print(f"DEBUG: Instance methods: {[attr for attr in dir(instance) if not attr.startswith('_') and callable(getattr(instance, attr))]}")
                        process_command(instance, dsl_command)
                        print(f"DSL command executed: {dsl_command}")  # 调试输出
                        # 更新状态栏
                        self.status_label.config(text=f"已执行: {dsl_command}")
                        # 清空输入框
                        self.nl_var.set("")
                    except Exception as e:
                        print(f"Error processing DSL: {e}")  # 调试输出
                        raise

            if not found_instance:
                messagebox.showerror("错误", "未找到活动的数据结构实例")
                print("No active visualizer instance found")

        except Exception as e:
            messagebox.showerror("错误", f"处理失败: {str(e)}")
            print(f"Error in _on_nl_submit: {str(e)}")
            import traceback
            traceback.print_exc()

        return "break"

    # ----------------------------------------------------

if __name__ == "__main__":
    try:
        root = Tk()
        app = MainWindow(root)
        root.mainloop()
    except Exception:
        traceback.print_exc()
        try:
            messagebox.showerror("错误", "程序启动失败，请查看控制台输出")
        except Exception:
            pass
        sys.exit(1)