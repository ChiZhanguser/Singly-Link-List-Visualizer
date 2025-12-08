"""
伪代码显示面板 - 用于在链表操作时实时展示算法执行过程
支持多语言切换：伪代码/C语言/Java/Python
"""
from tkinter import Frame, Label, Canvas, BOTH, LEFT, RIGHT, TOP, BOTTOM, Y, NW, StringVar, OptionMenu
import tkinter as tk
import time


class PseudocodePanel:
    """伪代码显示面板，支持行高亮、动画效果和多语言切换"""
    
    # 语言选项
    LANG_PSEUDOCODE = "伪代码"
    LANG_C = "C语言"
    LANG_JAVA = "Java"
    LANG_PYTHON = "Python"
    
    LANGUAGES = [LANG_PSEUDOCODE, LANG_C, LANG_JAVA, LANG_PYTHON]
    
    # ========== 多语言代码定义 ==========
    
    # 头部插入 - 多语言
    MULTILANG_INSERT_HEAD = {
        "伪代码": [
            ("// 头部插入算法", "comment"),
            ("newNode ← 创建新节点", "code"),
            ("newNode.data ← value", "code"),
            ("newNode.next ← head", "code"),
            ("head ← newNode", "code"),
            ("// 插入完成", "comment"),
        ],
        "C语言": [
            ("// 头部插入算法", "comment"),
            ("Node* newNode = (Node*)malloc(sizeof(Node));", "code"),
            ("newNode->data = value;", "code"),
            ("newNode->next = head;", "code"),
            ("head = newNode;", "code"),
            ("// 插入完成", "comment"),
        ],
        "Java": [
            ("// 头部插入算法", "comment"),
            ("Node newNode = new Node();", "code"),
            ("newNode.data = value;", "code"),
            ("newNode.next = head;", "code"),
            ("head = newNode;", "code"),
            ("// 插入完成", "comment"),
        ],
        "Python": [
            ("# 头部插入算法", "comment"),
            ("new_node = Node()", "code"),
            ("new_node.data = value", "code"),
            ("new_node.next = head", "code"),
            ("head = new_node", "code"),
            ("# 插入完成", "comment"),
        ]
    }
    
    # 尾部插入 - 多语言
    MULTILANG_INSERT_TAIL = {
        "伪代码": [
            ("// 尾部插入算法", "comment"),
            ("newNode ← 创建新节点", "code"),
            ("newNode.data ← value", "code"),
            ("newNode.next ← NULL", "code"),
            ("if head = NULL then", "code"),
            ("    head ← newNode", "code"),
            ("else", "code"),
            ("    temp ← head", "code"),
            ("    while temp.next ≠ NULL do", "code"),
            ("        temp ← temp.next", "code"),
            ("    end while", "code"),
            ("    temp.next ← newNode", "code"),
            ("end if", "code"),
            ("// 插入完成", "comment"),
        ],
        "C语言": [
            ("// 尾部插入算法", "comment"),
            ("Node* newNode = (Node*)malloc(sizeof(Node));", "code"),
            ("newNode->data = value;", "code"),
            ("newNode->next = NULL;", "code"),
            ("if (head == NULL) {", "code"),
            ("    head = newNode;", "code"),
            ("} else {", "code"),
            ("    Node* temp = head;", "code"),
            ("    while (temp->next != NULL) {", "code"),
            ("        temp = temp->next;", "code"),
            ("    }", "code"),
            ("    temp->next = newNode;", "code"),
            ("}", "code"),
            ("// 插入完成", "comment"),
        ],
        "Java": [
            ("// 尾部插入算法", "comment"),
            ("Node newNode = new Node();", "code"),
            ("newNode.data = value;", "code"),
            ("newNode.next = null;", "code"),
            ("if (head == null) {", "code"),
            ("    head = newNode;", "code"),
            ("} else {", "code"),
            ("    Node temp = head;", "code"),
            ("    while (temp.next != null) {", "code"),
            ("        temp = temp.next;", "code"),
            ("    }", "code"),
            ("    temp.next = newNode;", "code"),
            ("}", "code"),
            ("// 插入完成", "comment"),
        ],
        "Python": [
            ("# 尾部插入算法", "comment"),
            ("new_node = Node()", "code"),
            ("new_node.data = value", "code"),
            ("new_node.next = None", "code"),
            ("if head is None:", "code"),
            ("    head = new_node", "code"),
            ("else:", "code"),
            ("    temp = head", "code"),
            ("    while temp.next is not None:", "code"),
            ("        temp = temp.next", "code"),
            ("    # 找到尾节点", "comment"),
            ("    temp.next = new_node", "code"),
            ("# endif", "comment"),
            ("# 插入完成", "comment"),
        ]
    }
    
    # 指定位置插入 - 多语言
    MULTILANG_INSERT_AT_POSITION = {
        "伪代码": [
            ("// 在位置 pos 处插入", "comment"),
            ("newNode ← 创建新节点", "code"),
            ("newNode.data ← value", "code"),
            ("if pos = 1 then", "code"),
            ("    newNode.next ← head", "code"),
            ("    head ← newNode", "code"),
            ("else", "code"),
            ("    temp ← head", "code"),
            ("    for i ← 1 to pos-1 do", "code"),
            ("        temp ← temp.next", "code"),
            ("    end for", "code"),
            ("    newNode.next ← temp.next", "code"),
            ("    temp.next ← newNode", "code"),
            ("end if", "code"),
            ("// 插入完成", "comment"),
        ],
        "C语言": [
            ("// 在位置 pos 处插入", "comment"),
            ("Node* newNode = (Node*)malloc(sizeof(Node));", "code"),
            ("newNode->data = value;", "code"),
            ("if (pos == 1) {", "code"),
            ("    newNode->next = head;", "code"),
            ("    head = newNode;", "code"),
            ("} else {", "code"),
            ("    Node* temp = head;", "code"),
            ("    for (int i = 1; i < pos-1; i++) {", "code"),
            ("        temp = temp->next;", "code"),
            ("    }", "code"),
            ("    newNode->next = temp->next;", "code"),
            ("    temp->next = newNode;", "code"),
            ("}", "code"),
            ("// 插入完成", "comment"),
        ],
        "Java": [
            ("// 在位置 pos 处插入", "comment"),
            ("Node newNode = new Node();", "code"),
            ("newNode.data = value;", "code"),
            ("if (pos == 1) {", "code"),
            ("    newNode.next = head;", "code"),
            ("    head = newNode;", "code"),
            ("} else {", "code"),
            ("    Node temp = head;", "code"),
            ("    for (int i = 1; i < pos-1; i++) {", "code"),
            ("        temp = temp.next;", "code"),
            ("    }", "code"),
            ("    newNode.next = temp.next;", "code"),
            ("    temp.next = newNode;", "code"),
            ("}", "code"),
            ("// 插入完成", "comment"),
        ],
        "Python": [
            ("# 在位置 pos 处插入", "comment"),
            ("new_node = Node()", "code"),
            ("new_node.data = value", "code"),
            ("if pos == 1:", "code"),
            ("    new_node.next = head", "code"),
            ("    head = new_node", "code"),
            ("else:", "code"),
            ("    temp = head", "code"),
            ("    for i in range(1, pos-1):", "code"),
            ("        temp = temp.next", "code"),
            ("    # 找到前驱节点", "comment"),
            ("    new_node.next = temp.next", "code"),
            ("    temp.next = new_node", "code"),
            ("# endif", "comment"),
            ("# 插入完成", "comment"),
        ]
    }
    
    # 删除头节点 - 多语言
    MULTILANG_DELETE_HEAD = {
        "伪代码": [
            ("// 删除头节点算法", "comment"),
            ("if head = NULL then", "code"),
            ("    return  // 链表为空", "comment"),
            ("end if", "code"),
            ("temp ← head", "code"),
            ("head ← head.next", "code"),
            ("释放 temp", "code"),
            ("// 删除完成", "comment"),
        ],
        "C语言": [
            ("// 删除头节点算法", "comment"),
            ("if (head == NULL) {", "code"),
            ("    return; // 链表为空", "comment"),
            ("}", "code"),
            ("Node* temp = head;", "code"),
            ("head = head->next;", "code"),
            ("free(temp);", "code"),
            ("// 删除完成", "comment"),
        ],
        "Java": [
            ("// 删除头节点算法", "comment"),
            ("if (head == null) {", "code"),
            ("    return; // 链表为空", "comment"),
            ("}", "code"),
            ("Node temp = head;", "code"),
            ("head = head.next;", "code"),
            ("temp = null; // GC回收", "code"),
            ("// 删除完成", "comment"),
        ],
        "Python": [
            ("# 删除头节点算法", "comment"),
            ("if head is None:", "code"),
            ("    return  # 链表为空", "comment"),
            ("# endif", "comment"),
            ("temp = head", "code"),
            ("head = head.next", "code"),
            ("del temp  # 释放内存", "code"),
            ("# 删除完成", "comment"),
        ]
    }
    
    # 删除尾节点 - 多语言
    MULTILANG_DELETE_TAIL = {
        "伪代码": [
            ("// 删除尾节点算法", "comment"),
            ("if head = NULL then return", "code"),
            ("if head.next = NULL then", "code"),
            ("    释放 head", "code"),
            ("    head ← NULL", "code"),
            ("else", "code"),
            ("    temp ← head", "code"),
            ("    while temp.next.next ≠ NULL do", "code"),
            ("        temp ← temp.next", "code"),
            ("    end while", "code"),
            ("    释放 temp.next", "code"),
            ("    temp.next ← NULL", "code"),
            ("end if", "code"),
            ("// 删除完成", "comment"),
        ],
        "C语言": [
            ("// 删除尾节点算法", "comment"),
            ("if (head == NULL) return;", "code"),
            ("if (head->next == NULL) {", "code"),
            ("    free(head);", "code"),
            ("    head = NULL;", "code"),
            ("} else {", "code"),
            ("    Node* temp = head;", "code"),
            ("    while (temp->next->next != NULL) {", "code"),
            ("        temp = temp->next;", "code"),
            ("    }", "code"),
            ("    free(temp->next);", "code"),
            ("    temp->next = NULL;", "code"),
            ("}", "code"),
            ("// 删除完成", "comment"),
        ],
        "Java": [
            ("// 删除尾节点算法", "comment"),
            ("if (head == null) return;", "code"),
            ("if (head.next == null) {", "code"),
            ("    head = null;", "code"),
            ("    return;", "code"),
            ("} else {", "code"),
            ("    Node temp = head;", "code"),
            ("    while (temp.next.next != null) {", "code"),
            ("        temp = temp.next;", "code"),
            ("    }", "code"),
            ("    temp.next = null;", "code"),
            ("}", "code"),
            ("// 尾节点已删除", "comment"),
            ("// 删除完成", "comment"),
        ],
        "Python": [
            ("# 删除尾节点算法", "comment"),
            ("if head is None: return", "code"),
            ("if head.next is None:", "code"),
            ("    del head", "code"),
            ("    head = None", "code"),
            ("else:", "code"),
            ("    temp = head", "code"),
            ("    while temp.next.next is not None:", "code"),
            ("        temp = temp.next", "code"),
            ("    # 找到倒数第二个节点", "comment"),
            ("    del temp.next", "code"),
            ("    temp.next = None", "code"),
            ("# endif", "comment"),
            ("# 删除完成", "comment"),
        ]
    }
    
    # 删除指定位置 - 多语言
    MULTILANG_DELETE_AT_POSITION = {
        "伪代码": [
            ("// 删除位置 pos 的节点", "comment"),
            ("if head = NULL then return", "code"),
            ("if pos = 1 then", "code"),
            ("    temp ← head", "code"),
            ("    head ← head.next", "code"),
            ("    释放 temp", "code"),
            ("else", "code"),
            ("    temp ← head", "code"),
            ("    for i ← 1 to pos-1 do", "code"),
            ("        temp ← temp.next", "code"),
            ("    end for", "code"),
            ("    toDelete ← temp.next", "code"),
            ("    temp.next ← toDelete.next", "code"),
            ("    释放 toDelete", "code"),
            ("end if", "code"),
            ("// 删除完成", "comment"),
        ],
        "C语言": [
            ("// 删除位置 pos 的节点", "comment"),
            ("if (head == NULL) return;", "code"),
            ("if (pos == 1) {", "code"),
            ("    Node* temp = head;", "code"),
            ("    head = head->next;", "code"),
            ("    free(temp);", "code"),
            ("} else {", "code"),
            ("    Node* temp = head;", "code"),
            ("    for (int i = 1; i < pos-1; i++) {", "code"),
            ("        temp = temp->next;", "code"),
            ("    }", "code"),
            ("    Node* toDelete = temp->next;", "code"),
            ("    temp->next = toDelete->next;", "code"),
            ("    free(toDelete);", "code"),
            ("}", "code"),
            ("// 删除完成", "comment"),
        ],
        "Java": [
            ("// 删除位置 pos 的节点", "comment"),
            ("if (head == null) return;", "code"),
            ("if (pos == 1) {", "code"),
            ("    Node temp = head;", "code"),
            ("    head = head.next;", "code"),
            ("    temp = null;", "code"),
            ("} else {", "code"),
            ("    Node temp = head;", "code"),
            ("    for (int i = 1; i < pos-1; i++) {", "code"),
            ("        temp = temp.next;", "code"),
            ("    }", "code"),
            ("    Node toDelete = temp.next;", "code"),
            ("    temp.next = toDelete.next;", "code"),
            ("    toDelete = null;", "code"),
            ("}", "code"),
            ("// 删除完成", "comment"),
        ],
        "Python": [
            ("# 删除位置 pos 的节点", "comment"),
            ("if head is None: return", "code"),
            ("if pos == 1:", "code"),
            ("    temp = head", "code"),
            ("    head = head.next", "code"),
            ("    del temp", "code"),
            ("else:", "code"),
            ("    temp = head", "code"),
            ("    for i in range(1, pos-1):", "code"),
            ("        temp = temp.next", "code"),
            ("    # 找到前驱节点", "comment"),
            ("    to_delete = temp.next", "code"),
            ("    temp.next = to_delete.next", "code"),
            ("    del to_delete", "code"),
            ("# endif", "comment"),
            ("# 删除完成", "comment"),
        ]
    }
    
    # 搜索 - 多语言
    MULTILANG_SEARCH = {
        "伪代码": [
            ("// 链表搜索算法", "comment"),
            ("current ← head", "code"),
            ("index ← 0", "code"),
            ("while current ≠ NULL do", "code"),
            ("    if current.data = target then", "code"),
            ("        return index  // 找到!", "comment"),
            ("    end if", "code"),
            ("    current ← current.next", "code"),
            ("    index ← index + 1", "code"),
            ("end while", "code"),
            ("return -1  // 未找到", "comment"),
        ],
        "C语言": [
            ("// 链表搜索算法", "comment"),
            ("Node* current = head;", "code"),
            ("int index = 0;", "code"),
            ("while (current != NULL) {", "code"),
            ("    if (current->data == target) {", "code"),
            ("        return index; // 找到!", "comment"),
            ("    }", "code"),
            ("    current = current->next;", "code"),
            ("    index++;", "code"),
            ("}", "code"),
            ("return -1; // 未找到", "comment"),
        ],
        "Java": [
            ("// 链表搜索算法", "comment"),
            ("Node current = head;", "code"),
            ("int index = 0;", "code"),
            ("while (current != null) {", "code"),
            ("    if (current.data == target) {", "code"),
            ("        return index; // 找到!", "comment"),
            ("    }", "code"),
            ("    current = current.next;", "code"),
            ("    index++;", "code"),
            ("}", "code"),
            ("return -1; // 未找到", "comment"),
        ],
        "Python": [
            ("# 链表搜索算法", "comment"),
            ("current = head", "code"),
            ("index = 0", "code"),
            ("while current is not None:", "code"),
            ("    if current.data == target:", "code"),
            ("        return index  # 找到!", "comment"),
            ("    # endif", "comment"),
            ("    current = current.next", "code"),
            ("    index += 1", "code"),
            ("# endwhile", "comment"),
            ("return -1  # 未找到", "comment"),
        ]
    }
    
    # 遍历 - 多语言
    MULTILANG_TRAVERSE = {
        "伪代码": [
            ("// 链表遍历算法", "comment"),
            ("current ← head", "code"),
            ("while current ≠ NULL do", "code"),
            ("    visit(current.data)", "code"),
            ("    current ← current.next", "code"),
            ("end while", "code"),
            ("// 遍历完成", "comment"),
        ],
        "C语言": [
            ("// 链表遍历算法", "comment"),
            ("Node* current = head;", "code"),
            ("while (current != NULL) {", "code"),
            ("    visit(current->data);", "code"),
            ("    current = current->next;", "code"),
            ("}", "code"),
            ("// 遍历完成", "comment"),
        ],
        "Java": [
            ("// 链表遍历算法", "comment"),
            ("Node current = head;", "code"),
            ("while (current != null) {", "code"),
            ("    visit(current.data);", "code"),
            ("    current = current.next;", "code"),
            ("}", "code"),
            ("// 遍历完成", "comment"),
        ],
        "Python": [
            ("# 链表遍历算法", "comment"),
            ("current = head", "code"),
            ("while current is not None:", "code"),
            ("    visit(current.data)", "code"),
            ("    current = current.next", "code"),
            ("# endwhile", "comment"),
            ("# 遍历完成", "comment"),
        ]
    }
    
    # 反转 - 多语言
    MULTILANG_REVERSE = {
        "伪代码": [
            ("// 链表原地反转算法", "comment"),
            ("prev ← NULL", "code"),
            ("curr ← head", "code"),
            ("next ← NULL", "code"),
            ("while curr ≠ NULL do", "code"),
            ("    next ← curr.next", "code"),
            ("    curr.next ← prev", "code"),
            ("    prev ← curr", "code"),
            ("    curr ← next", "code"),
            ("end while", "code"),
            ("head ← prev", "code"),
            ("// 反转完成", "comment"),
        ],
        "C语言": [
            ("// 链表原地反转算法", "comment"),
            ("Node* prev = NULL;", "code"),
            ("Node* curr = head;", "code"),
            ("Node* next = NULL;", "code"),
            ("while (curr != NULL) {", "code"),
            ("    next = curr->next;", "code"),
            ("    curr->next = prev;", "code"),
            ("    prev = curr;", "code"),
            ("    curr = next;", "code"),
            ("}", "code"),
            ("head = prev;", "code"),
            ("// 反转完成", "comment"),
        ],
        "Java": [
            ("// 链表原地反转算法", "comment"),
            ("Node prev = null;", "code"),
            ("Node curr = head;", "code"),
            ("Node next = null;", "code"),
            ("while (curr != null) {", "code"),
            ("    next = curr.next;", "code"),
            ("    curr.next = prev;", "code"),
            ("    prev = curr;", "code"),
            ("    curr = next;", "code"),
            ("}", "code"),
            ("head = prev;", "code"),
            ("// 反转完成", "comment"),
        ],
        "Python": [
            ("# 链表原地反转算法", "comment"),
            ("prev = None", "code"),
            ("curr = head", "code"),
            ("next_node = None", "code"),
            ("while curr is not None:", "code"),
            ("    next_node = curr.next", "code"),
            ("    curr.next = prev", "code"),
            ("    prev = curr", "code"),
            ("    curr = next_node", "code"),
            ("# endwhile", "comment"),
            ("head = prev", "code"),
            ("# 反转完成", "comment"),
        ]
    }
    
    # 保持向后兼容的旧属性（默认使用C语言）
    @property
    def PSEUDOCODE_INSERT_HEAD(self):
        return self.MULTILANG_INSERT_HEAD.get(self.current_language, self.MULTILANG_INSERT_HEAD["C语言"])
    
    @property
    def PSEUDOCODE_INSERT_TAIL(self):
        return self.MULTILANG_INSERT_TAIL.get(self.current_language, self.MULTILANG_INSERT_TAIL["C语言"])
    
    @property
    def PSEUDOCODE_INSERT_AT_POSITION(self):
        return self.MULTILANG_INSERT_AT_POSITION.get(self.current_language, self.MULTILANG_INSERT_AT_POSITION["C语言"])
    
    @property
    def PSEUDOCODE_DELETE_HEAD(self):
        return self.MULTILANG_DELETE_HEAD.get(self.current_language, self.MULTILANG_DELETE_HEAD["C语言"])
    
    @property
    def PSEUDOCODE_DELETE_TAIL(self):
        return self.MULTILANG_DELETE_TAIL.get(self.current_language, self.MULTILANG_DELETE_TAIL["C语言"])
    
    @property
    def PSEUDOCODE_DELETE_AT_POSITION(self):
        return self.MULTILANG_DELETE_AT_POSITION.get(self.current_language, self.MULTILANG_DELETE_AT_POSITION["C语言"])
    
    @property
    def PSEUDOCODE_SEARCH(self):
        return self.MULTILANG_SEARCH.get(self.current_language, self.MULTILANG_SEARCH["C语言"])
    
    @property
    def PSEUDOCODE_TRAVERSE(self):
        return self.MULTILANG_TRAVERSE.get(self.current_language, self.MULTILANG_TRAVERSE["C语言"])
    
    @property
    def PSEUDOCODE_REVERSE(self):
        return self.MULTILANG_REVERSE.get(self.current_language, self.MULTILANG_REVERSE["C语言"])
    
    def __init__(self, parent, x=1100, y=85, width=280, height=420):
        """
        初始化伪代码面板
        
        Args:
            parent: 父窗口
            x, y: 面板位置
            width, height: 面板尺寸
        """
        self.parent = parent
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
        # 当前语言设置
        self.current_language = self.LANG_C  # 默认C语言
        
        # 当前操作类型（用于语言切换时重新渲染）
        self.current_operation_type = None
        
        self.current_pseudocode = []
        self.line_labels = []
        self.highlighted_line = -1
        self.highlighted_lines = []  # 支持多行高亮
        
        self._create_panel()
    
    def _create_panel(self):
        """创建面板UI"""
        # 主框架
        self.frame = Frame(self.parent, bg="#1E1E2E", bd=2, relief="raised")
        self.frame.place(x=self.x, y=self.y, width=self.width, height=self.height)
        
        # 标题栏（包含标题和语言切换）
        title_frame = Frame(self.frame, bg="#1E1E2E")
        title_frame.pack(fill="x", padx=5, pady=5)
        
        # 标题
        self.title_label = Label(
            title_frame, 
            text="📝 代码执行", 
            font=("Consolas", 11, "bold"),
            bg="#1E1E2E", 
            fg="#89B4FA",
            anchor="w"
        )
        self.title_label.pack(side=LEFT, padx=5)
        
        # 语言切换下拉框
        self.lang_var = StringVar(value=self.current_language)
        self.lang_menu = OptionMenu(
            title_frame, 
            self.lang_var, 
            *self.LANGUAGES,
            command=self._on_language_change
        )
        self.lang_menu.config(
            font=("微软雅黑", 9),
            bg="#313244",
            fg="#CDD6F4",
            activebackground="#45475A",
            activeforeground="#CDD6F4",
            highlightthickness=0,
            relief="flat",
            width=6
        )
        self.lang_menu["menu"].config(
            bg="#313244",
            fg="#CDD6F4",
            activebackground="#45475A",
            activeforeground="#CDD6F4",
            font=("微软雅黑", 9)
        )
        self.lang_menu.pack(side=RIGHT, padx=5)
        
        # 语言切换快捷按钮组
        btn_frame = Frame(self.frame, bg="#1E1E2E")
        btn_frame.pack(fill="x", padx=5, pady=(0, 5))
        
        self.lang_buttons = {}
        for lang in self.LANGUAGES:
            btn = Label(
                btn_frame,
                text=self._get_lang_short_name(lang),
                font=("Consolas", 8),
                bg="#89B4FA" if lang == self.current_language else "#313244",
                fg="#1E1E2E" if lang == self.current_language else "#CDD6F4",
                padx=6,
                pady=2,
                cursor="hand2"
            )
            btn.pack(side=LEFT, padx=2)
            btn.bind("<Button-1>", lambda e, l=lang: self._switch_language(l))
            self.lang_buttons[lang] = btn
        
        # 分隔线
        separator = Frame(self.frame, height=2, bg="#45475A")
        separator.pack(fill="x", padx=5)
        
        # 代码显示区域（带滚动）
        code_container = Frame(self.frame, bg="#1E1E2E")
        code_container.pack(fill=BOTH, expand=True, padx=5, pady=5)
        
        # 创建Canvas用于滚动
        self.code_canvas = Canvas(code_container, bg="#1E1E2E", highlightthickness=0)
        self.code_canvas.pack(side=LEFT, fill=BOTH, expand=True)
        
        # 滚动条
        self.scrollbar = tk.Scrollbar(code_container, orient="vertical", command=self.code_canvas.yview)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.code_canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # 代码显示框架
        self.code_frame = Frame(self.code_canvas, bg="#1E1E2E")
        self.canvas_window = self.code_canvas.create_window((0, 0), window=self.code_frame, anchor="nw")
        
        self.code_frame.bind("<Configure>", self._on_frame_configure)
        self.code_canvas.bind("<Configure>", self._on_canvas_configure)
        
        # 鼠标滚轮绑定
        self.code_canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
        # 状态标签
        self.status_label = Label(
            self.frame,
            text="等待操作...",
            font=("微软雅黑", 9),
            bg="#313244",
            fg="#A6ADC8",
            anchor="w",
            padx=5,
            pady=3
        )
        self.status_label.pack(fill="x", side=BOTTOM)
    
    def _get_lang_short_name(self, lang):
        """获取语言的简短名称"""
        mapping = {
            self.LANG_PSEUDOCODE: "伪代码",
            self.LANG_C: "C",
            self.LANG_JAVA: "Java",
            self.LANG_PYTHON: "Py"
        }
        return mapping.get(lang, lang)
    
    def _on_frame_configure(self, event):
        """更新滚动区域"""
        self.code_canvas.configure(scrollregion=self.code_canvas.bbox("all"))
    
    def _on_canvas_configure(self, event):
        """调整框架宽度"""
        self.code_canvas.itemconfig(self.canvas_window, width=event.width)
    
    def _on_mousewheel(self, event):
        """鼠标滚轮事件"""
        self.code_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def _on_language_change(self, selected_lang):
        """语言切换回调（下拉框）"""
        self._switch_language(selected_lang)
    
    def _switch_language(self, new_lang):
        """
        切换语言并重新渲染代码
        
        Args:
            new_lang: 新的语言名称
        """
        if new_lang == self.current_language:
            return
        
        self.current_language = new_lang
        self.lang_var.set(new_lang)
        
        # 更新按钮样式
        for lang, btn in self.lang_buttons.items():
            if lang == new_lang:
                btn.config(bg="#89B4FA", fg="#1E1E2E")
            else:
                btn.config(bg="#313244", fg="#CDD6F4")
        
        # 保存当前高亮状态
        saved_highlight = self.highlighted_line
        saved_highlights = self.highlighted_lines.copy()
        
        # 如果有当前操作类型，重新获取该语言的代码
        if self.current_operation_type:
            self.set_pseudocode(self.current_operation_type)
            
            # 恢复高亮
            if saved_highlights:
                self.highlight_lines(saved_highlights)
            elif saved_highlight >= 0:
                self.highlight_line(saved_highlight)
    
    def set_pseudocode(self, pseudocode_type):
        """
        设置要显示的伪代码类型
        
        Args:
            pseudocode_type: 伪代码类型字符串
        """
        self.current_operation_type = pseudocode_type
        
        # 多语言代码映射
        multilang_map = {
            "insert_head": self.MULTILANG_INSERT_HEAD,
            "insert_tail": self.MULTILANG_INSERT_TAIL,
            "insert_at_position": self.MULTILANG_INSERT_AT_POSITION,
            "delete_head": self.MULTILANG_DELETE_HEAD,
            "delete_tail": self.MULTILANG_DELETE_TAIL,
            "delete_at_position": self.MULTILANG_DELETE_AT_POSITION,
            "search": self.MULTILANG_SEARCH,
            "traverse": self.MULTILANG_TRAVERSE,
            "reverse": self.MULTILANG_REVERSE,
        }
        
        # 获取当前语言的代码
        multilang_code = multilang_map.get(pseudocode_type, {})
        self.current_pseudocode = multilang_code.get(self.current_language, [])
        
        self._render_pseudocode()
        self.highlighted_line = -1
        self.highlighted_lines = []
    
    def set_custom_pseudocode(self, pseudocode_list):
        """
        设置自定义伪代码
        
        Args:
            pseudocode_list: 伪代码列表，每项为 (代码文本, 类型) 元组
        """
        self.current_operation_type = None
        self.current_pseudocode = pseudocode_list
        self._render_pseudocode()
        self.highlighted_line = -1
        self.highlighted_lines = []
    
    def _render_pseudocode(self):
        """渲染伪代码到面板"""
        # 清除现有标签
        for label in self.line_labels:
            try:
                label.destroy()
            except:
                pass
        self.line_labels = []
        
        # 创建新标签
        for i, item in enumerate(self.current_pseudocode):
            if isinstance(item, tuple):
                text, code_type = item
            else:
                text = str(item)
                code_type = "code"
            
            # 设置颜色
            if code_type == "comment":
                fg_color = "#6C7086"  # 灰色注释
            else:
                fg_color = "#CDD6F4"  # 浅色代码
            
            label = Label(
                self.code_frame,
                text=f" {i+1:2d} │ {text}",
                font=("Consolas", 9),
                bg="#1E1E2E",
                fg=fg_color,
                anchor="w",
                padx=2,
                pady=1
            )
            label.pack(fill="x", anchor="w")
            self.line_labels.append(label)
    
    def highlight_line(self, line_number, status_text=None):
        """
        高亮指定行
        
        Args:
            line_number: 要高亮的行号（从0开始）
            status_text: 可选的状态文本
        """
        # 取消之前的高亮
        if 0 <= self.highlighted_line < len(self.line_labels):
            old_label = self.line_labels[self.highlighted_line]
            code_type = self.current_pseudocode[self.highlighted_line][1] if self.highlighted_line < len(self.current_pseudocode) else "code"
            fg_color = "#6C7086" if code_type == "comment" else "#CDD6F4"
            try:
                old_label.config(bg="#1E1E2E", fg=fg_color, font=("Consolas", 9))
            except:
                pass
        
        # 设置新的高亮
        if 0 <= line_number < len(self.line_labels):
            new_label = self.line_labels[line_number]
            try:
                new_label.config(bg="#F9E2AF", fg="#1E1E2E", font=("Consolas", 9, "bold"))
            except:
                pass
            self.highlighted_line = line_number
        
        # 更新状态
        if status_text:
            self.set_status(status_text)
        
        # 强制更新显示
        try:
            self.frame.update()
        except:
            pass
    
    def highlight_lines(self, line_numbers, status_text=None):
        """
        高亮多行
        
        Args:
            line_numbers: 要高亮的行号列表
            status_text: 可选的状态文本
        """
        # 先重置所有行
        self.reset_highlight()
        
        self.highlighted_lines = []
        
        # 高亮指定的多行
        for line_num in line_numbers:
            if 0 <= line_num < len(self.line_labels):
                label = self.line_labels[line_num]
                try:
                    label.config(bg="#F9E2AF", fg="#1E1E2E", font=("Consolas", 9, "bold"))
                except:
                    pass
                self.highlighted_lines.append(line_num)
        
        if line_numbers:
            self.highlighted_line = line_numbers[0]
        
        if status_text:
            self.set_status(status_text)
        
        try:
            self.frame.update()
        except:
            pass
    
    def reset_highlight(self):
        """重置所有高亮"""
        for i, label in enumerate(self.line_labels):
            if i < len(self.current_pseudocode):
                item = self.current_pseudocode[i]
                code_type = item[1] if isinstance(item, tuple) else "code"
            else:
                code_type = "code"
            fg_color = "#6C7086" if code_type == "comment" else "#CDD6F4"
            try:
                label.config(bg="#1E1E2E", fg=fg_color, font=("Consolas", 9))
            except:
                pass
        self.highlighted_line = -1
        self.highlighted_lines = []
    
    def get_current_language(self):
        """获取当前选择的语言"""
        return self.current_language
    
    def set_language(self, lang):
        """
        设置当前语言（外部调用）
        
        Args:
            lang: 语言名称（伪代码/C语言/Java/Python）
        """
        if lang in self.LANGUAGES:
            self._switch_language(lang)
    
    def set_status(self, text):
        """设置状态文本"""
        try:
            self.status_label.config(text=text)
        except:
            pass
    
    def show(self):
        """显示面板"""
        try:
            self.frame.place(x=self.x, y=self.y, width=self.width, height=self.height)
        except:
            pass
    
    def hide(self):
        """隐藏面板"""
        try:
            self.frame.place_forget()
        except:
            pass
    
    def clear(self):
        """清除伪代码显示"""
        self.current_pseudocode = []
        for label in self.line_labels:
            try:
                label.destroy()
            except:
                pass
        self.line_labels = []
        self.highlighted_line = -1
        self.set_status("等待操作...")
    
    def animate_execution(self, line_sequence, delay=0.5, window=None):
        """
        动画执行伪代码序列
        
        Args:
            line_sequence: 行号序列列表
            delay: 每行之间的延迟（秒）
            window: 窗口对象（用于更新）
        """
        for line_num in line_sequence:
            self.highlight_line(line_num)
            if window:
                try:
                    window.update()
                except:
                    pass
            time.sleep(delay)


class PseudocodeHelper:
    """伪代码辅助类，提供便捷的伪代码操作方法"""
    
    @staticmethod
    def get_insert_head_steps():
        """获取头部插入的步骤映射"""
        return {
            "create_node": (1, "创建新节点"),
            "set_data": (2, "设置节点数据"),
            "set_next": (3, "新节点next指向原头节点"),
            "update_head": (4, "更新头指针"),
            "complete": (5, "插入完成"),
        }
    
    @staticmethod
    def get_insert_tail_steps():
        """获取尾部插入的步骤映射"""
        return {
            "create_node": (1, "创建新节点"),
            "set_data": (2, "设置节点数据"),
            "set_next_null": (3, "新节点next设为NULL"),
            "check_empty": (4, "检查链表是否为空"),
            "empty_set_head": (5, "空链表：设置头节点"),
            "else_branch": (6, "非空链表"),
            "init_temp": (7, "初始化temp指针"),
            "while_loop": (8, "循环条件"),
            "traverse": (9, "遍历到下一节点"),
            "end_while": (10, "循环结束"),
            "link_node": (11, "连接新节点"),
            "end_if": (12, "条件结束"),
            "complete": (13, "插入完成"),
        }
    
    @staticmethod
    def get_insert_at_position_steps():
        """获取指定位置插入的步骤映射"""
        return {
            "create_node": (1, "创建新节点"),
            "set_data": (2, "设置节点数据"),
            "check_pos": (3, "检查是否头部插入"),
            "head_set_next": (4, "新节点next指向原头节点"),
            "head_update": (5, "更新头指针"),
            "else_branch": (6, "非头部插入"),
            "init_temp": (7, "初始化temp指针"),
            "for_loop": (8, "循环遍历到目标位置"),
            "traverse": (9, "temp移动到下一节点"),
            "end_loop": (10, "循环结束"),
            "link_new_next": (11, "新节点next指向后继节点"),
            "link_prev": (12, "前驱节点next指向新节点"),
            "end_if": (13, "条件结束"),
            "complete": (14, "插入完成"),
        }
    
    @staticmethod
    def get_delete_at_position_steps():
        """获取删除指定位置节点的步骤映射"""
        return {
            "check_empty": (1, "检查链表是否为空"),
            "check_pos": (2, "检查是否删除头节点"),
            "save_head": (3, "保存头节点引用"),
            "move_head": (4, "头指针后移"),
            "delete_temp": (5, "删除原头节点"),
            "else_branch": (6, "非头节点删除"),
            "init_temp": (7, "初始化temp指针"),
            "for_loop": (8, "循环遍历到前驱节点"),
            "traverse": (9, "temp移动到下一节点"),
            "end_loop": (10, "循环结束"),
            "save_delete": (11, "保存要删除的节点"),
            "relink": (12, "重新链接：跳过被删节点"),
            "delete_node": (13, "删除节点"),
            "end_if": (14, "条件结束"),
            "complete": (15, "删除完成"),
        }

