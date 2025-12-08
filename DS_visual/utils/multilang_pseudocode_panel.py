"""
多语言伪代码显示面板 - 支持在 伪代码/C语言/Java/Python 之间实时切换
"""
from tkinter import Frame, Label, Canvas, BOTH, LEFT, RIGHT, TOP, BOTTOM, Y, NW, StringVar, OptionMenu, END
import tkinter as tk


class MultiLangPseudocodePanel:
    """
    多语言伪代码显示面板，支持：
    - 伪代码 (Pseudocode)
    - C语言 (C)
    - Java
    - Python
    
    支持运行时切换语言，同时保持当前高亮状态
    """
    
    # 语言选项
    LANG_PSEUDOCODE = "伪代码"
    LANG_C = "C语言"
    LANG_JAVA = "Java"
    LANG_PYTHON = "Python"
    
    LANGUAGES = [LANG_PSEUDOCODE, LANG_C, LANG_JAVA, LANG_PYTHON]
    
    # 语言对应的内部键
    LANG_KEYS = {
        "伪代码": "pseudo",
        "C语言": "c",
        "Java": "java",
        "Python": "python"
    }
    
    def __init__(self, parent, x=1100, y=85, width=280, height=420):
        """
        初始化多语言伪代码面板
        
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
        
        # 当前选择的语言
        self.current_language = self.LANG_PSEUDOCODE
        
        # 当前操作类型
        self.current_operation = None
        
        # 多语言代码存储：{operation_type: {lang_key: [(code_text, type), ...]}}
        self.multilang_code = {}
        
        # 当前显示的代码
        self.current_code = []
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
        
        # 语言切换按钮组（可选的快捷按钮）
        btn_frame = Frame(self.frame, bg="#1E1E2E")
        btn_frame.pack(fill="x", padx=5, pady=(0, 5))
        
        self.lang_buttons = {}
        for lang in self.LANGUAGES:
            btn = Label(
                btn_frame,
                text=self._get_lang_short_name(lang),
                font=("Consolas", 8),
                bg="#313244" if lang != self.current_language else "#89B4FA",
                fg="#CDD6F4" if lang != self.current_language else "#1E1E2E",
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
        
        # 代码显示区域的容器（带滚动）
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
        self.code_canvas.create_window((0, 0), window=self.code_frame, anchor="nw")
        
        self.code_frame.bind("<Configure>", lambda e: self.code_canvas.configure(scrollregion=self.code_canvas.bbox("all")))
        
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
    
    def _on_mousewheel(self, event):
        """鼠标滚轮事件"""
        self.code_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def _on_language_change(self, selected_lang):
        """语言切换回调（下拉框）"""
        self._switch_language(selected_lang)
    
    def _switch_language(self, new_lang):
        """
        切换语言
        
        Args:
            new_lang: 新的语言名称
        """
        if new_lang == self.current_language:
            return
        
        old_lang = self.current_language
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
        
        # 重新渲染当前操作的代码
        if self.current_operation and self.current_operation in self.multilang_code:
            lang_key = self.LANG_KEYS.get(new_lang, "pseudo")
            if lang_key in self.multilang_code[self.current_operation]:
                self.current_code = self.multilang_code[self.current_operation][lang_key]
                self._render_code()
                
                # 恢复高亮
                if saved_highlights:
                    self.highlight_lines(saved_highlights)
                elif saved_highlight >= 0:
                    self.highlight_line(saved_highlight)
    
    def register_multilang_code(self, operation_type, code_dict):
        """
        注册某个操作的多语言代码
        
        Args:
            operation_type: 操作类型标识（如 "insert_head"）
            code_dict: 多语言代码字典，格式为：
                {
                    "pseudo": [(code_text, type), ...],
                    "c": [(code_text, type), ...],
                    "java": [(code_text, type), ...],
                    "python": [(code_text, type), ...]
                }
                type 可以是 "code" 或 "comment"
        """
        self.multilang_code[operation_type] = code_dict
    
    def set_operation(self, operation_type):
        """
        设置当前操作并显示对应代码
        
        Args:
            operation_type: 操作类型标识
        """
        self.current_operation = operation_type
        
        if operation_type not in self.multilang_code:
            self.current_code = []
            self._render_code()
            return
        
        lang_key = self.LANG_KEYS.get(self.current_language, "pseudo")
        if lang_key in self.multilang_code[operation_type]:
            self.current_code = self.multilang_code[operation_type][lang_key]
        else:
            # 如果当前语言没有，尝试使用伪代码
            self.current_code = self.multilang_code[operation_type].get("pseudo", [])
        
        self._render_code()
        self.highlighted_line = -1
        self.highlighted_lines = []
    
    def set_custom_code(self, code_list):
        """
        设置自定义代码（不使用注册的多语言代码）
        
        Args:
            code_list: 代码列表，每项为 (代码文本, 类型) 元组
        """
        self.current_operation = None
        self.current_code = code_list
        self._render_code()
        self.highlighted_line = -1
        self.highlighted_lines = []
    
    def _render_code(self):
        """渲染代码到面板"""
        # 清除现有标签
        for label in self.line_labels:
            try:
                label.destroy()
            except:
                pass
        self.line_labels = []
        
        if not self.current_code:
            return
        
        # 创建新标签
        for i, item in enumerate(self.current_code):
            if isinstance(item, tuple):
                text, code_type = item
            else:
                text = str(item)
                code_type = "code"
            
            # 设置颜色
            if code_type == "comment":
                fg_color = "#6C7086"  # 灰色注释
            elif code_type == "keyword":
                fg_color = "#F38BA8"  # 关键字颜色
            elif code_type == "function":
                fg_color = "#89B4FA"  # 函数颜色
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
        self._clear_all_highlights()
        
        # 设置新的高亮
        if 0 <= line_number < len(self.line_labels):
            new_label = self.line_labels[line_number]
            try:
                new_label.config(bg="#F9E2AF", fg="#1E1E2E", font=("Consolas", 9, "bold"))
            except:
                pass
            self.highlighted_line = line_number
            self.highlighted_lines = [line_number]
            
            # 滚动到可见区域
            self._scroll_to_line(line_number)
        
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
        # 先清除所有高亮
        self._clear_all_highlights()
        
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
            self._scroll_to_line(line_numbers[0])
        
        if status_text:
            self.set_status(status_text)
        
        try:
            self.frame.update()
        except:
            pass
    
    def _clear_all_highlights(self):
        """清除所有高亮"""
        for i, label in enumerate(self.line_labels):
            if i < len(self.current_code):
                item = self.current_code[i]
                if isinstance(item, tuple):
                    code_type = item[1]
                else:
                    code_type = "code"
                
                if code_type == "comment":
                    fg_color = "#6C7086"
                elif code_type == "keyword":
                    fg_color = "#F38BA8"
                elif code_type == "function":
                    fg_color = "#89B4FA"
                else:
                    fg_color = "#CDD6F4"
                
                try:
                    label.config(bg="#1E1E2E", fg=fg_color, font=("Consolas", 9))
                except:
                    pass
    
    def _scroll_to_line(self, line_number):
        """滚动到指定行"""
        if len(self.line_labels) == 0:
            return
        try:
            # 计算滚动位置
            fraction = line_number / len(self.line_labels)
            self.code_canvas.yview_moveto(max(0, fraction - 0.3))
        except:
            pass
    
    def reset_highlight(self):
        """重置所有高亮"""
        self._clear_all_highlights()
        self.highlighted_line = -1
        self.highlighted_lines = []
    
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
        """清除代码显示"""
        self.current_code = []
        self.current_operation = None
        for label in self.line_labels:
            try:
                label.destroy()
            except:
                pass
        self.line_labels = []
        self.highlighted_line = -1
        self.highlighted_lines = []
        self.set_status("等待操作...")
    
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


# ==================== 预定义的多语言代码模板 ====================

class LinkedListCode:
    """链表操作的多语言代码定义"""
    
    # 头部插入
    INSERT_HEAD = {
        "pseudo": [
            ("// 头部插入算法", "comment"),
            ("newNode ← 创建新节点", "code"),
            ("newNode.data ← value", "code"),
            ("newNode.next ← head", "code"),
            ("head ← newNode", "code"),
            ("// 插入完成", "comment"),
        ],
        "c": [
            ("// 头部插入算法", "comment"),
            ("Node* newNode = (Node*)malloc(sizeof(Node));", "code"),
            ("newNode->data = value;", "code"),
            ("newNode->next = head;", "code"),
            ("head = newNode;", "code"),
            ("// 插入完成", "comment"),
        ],
        "java": [
            ("// 头部插入算法", "comment"),
            ("Node newNode = new Node();", "code"),
            ("newNode.data = value;", "code"),
            ("newNode.next = head;", "code"),
            ("head = newNode;", "code"),
            ("// 插入完成", "comment"),
        ],
        "python": [
            ("# 头部插入算法", "comment"),
            ("new_node = Node()", "code"),
            ("new_node.data = value", "code"),
            ("new_node.next = head", "code"),
            ("head = new_node", "code"),
            ("# 插入完成", "comment"),
        ]
    }
    
    # 尾部插入
    INSERT_TAIL = {
        "pseudo": [
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
        "c": [
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
        "java": [
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
        "python": [
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
    
    # 指定位置插入
    INSERT_AT_POSITION = {
        "pseudo": [
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
        "c": [
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
        "java": [
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
        "python": [
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
    
    # 删除头节点
    DELETE_HEAD = {
        "pseudo": [
            ("// 删除头节点算法", "comment"),
            ("if head = NULL then", "code"),
            ("    return  // 链表为空", "comment"),
            ("end if", "code"),
            ("temp ← head", "code"),
            ("head ← head.next", "code"),
            ("释放 temp", "code"),
            ("// 删除完成", "comment"),
        ],
        "c": [
            ("// 删除头节点算法", "comment"),
            ("if (head == NULL) {", "code"),
            ("    return; // 链表为空", "comment"),
            ("}", "code"),
            ("Node* temp = head;", "code"),
            ("head = head->next;", "code"),
            ("free(temp);", "code"),
            ("// 删除完成", "comment"),
        ],
        "java": [
            ("// 删除头节点算法", "comment"),
            ("if (head == null) {", "code"),
            ("    return; // 链表为空", "comment"),
            ("}", "code"),
            ("Node temp = head;", "code"),
            ("head = head.next;", "code"),
            ("temp = null; // GC回收", "code"),
            ("// 删除完成", "comment"),
        ],
        "python": [
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
    
    # 删除尾节点
    DELETE_TAIL = {
        "pseudo": [
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
        "c": [
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
        "java": [
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
            ("// 空行", "comment"),
            ("// 删除完成", "comment"),
        ],
        "python": [
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
    
    # 删除指定位置
    DELETE_AT_POSITION = {
        "pseudo": [
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
        "c": [
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
        "java": [
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
        "python": [
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
    
    # 搜索
    SEARCH = {
        "pseudo": [
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
        "c": [
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
        "java": [
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
        "python": [
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
    
    # 遍历
    TRAVERSE = {
        "pseudo": [
            ("// 链表遍历算法", "comment"),
            ("current ← head", "code"),
            ("while current ≠ NULL do", "code"),
            ("    visit(current.data)", "code"),
            ("    current ← current.next", "code"),
            ("end while", "code"),
            ("// 遍历完成", "comment"),
        ],
        "c": [
            ("// 链表遍历算法", "comment"),
            ("Node* current = head;", "code"),
            ("while (current != NULL) {", "code"),
            ("    visit(current->data);", "code"),
            ("    current = current->next;", "code"),
            ("}", "code"),
            ("// 遍历完成", "comment"),
        ],
        "java": [
            ("// 链表遍历算法", "comment"),
            ("Node current = head;", "code"),
            ("while (current != null) {", "code"),
            ("    visit(current.data);", "code"),
            ("    current = current.next;", "code"),
            ("}", "code"),
            ("// 遍历完成", "comment"),
        ],
        "python": [
            ("# 链表遍历算法", "comment"),
            ("current = head", "code"),
            ("while current is not None:", "code"),
            ("    visit(current.data)", "code"),
            ("    current = current.next", "code"),
            ("# endwhile", "comment"),
            ("# 遍历完成", "comment"),
        ]
    }
    
    # 反转
    REVERSE = {
        "pseudo": [
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
        "c": [
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
        "java": [
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
        "python": [
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


class RBTreeCode:
    """红黑树操作的多语言代码定义"""
    
    # 插入
    INSERT = {
        "pseudo": [
            ("RB-INSERT(T, val):", "function"),
            ("  z ← new Node(val)", "code"),
            ("  z.color ← RED", "code"),
            ("  // 找到插入位置", "comment"),
            ("  y ← null", "code"),
            ("  x ← T.root", "code"),
            ("  while x ≠ null do", "code"),
            ("    y ← x", "code"),
            ("    if z.val < x.val then", "code"),
            ("      x ← x.left", "code"),
            ("    else", "code"),
            ("      x ← x.right", "code"),
            ("    end if", "code"),
            ("  end while", "code"),
            ("  z.parent ← y", "code"),
            ("  if y = null then", "code"),
            ("    T.root ← z  // 树为空", "comment"),
            ("  else if z.val < y.val then", "code"),
            ("    y.left ← z", "code"),
            ("  else", "code"),
            ("    y.right ← z", "code"),
            ("  end if", "code"),
            ("  // 修复红黑性质", "comment"),
            ("  RB-INSERT-FIXUP(T, z)", "code"),
        ],
        "c": [
            ("void rb_insert(RBTree* T, int val) {", "function"),
            ("  Node* z = create_node(val);", "code"),
            ("  z->color = RED;", "code"),
            ("  // 找到插入位置", "comment"),
            ("  Node* y = NULL;", "code"),
            ("  Node* x = T->root;", "code"),
            ("  while (x != NULL) {", "code"),
            ("    y = x;", "code"),
            ("    if (z->val < x->val) {", "code"),
            ("      x = x->left;", "code"),
            ("    } else {", "code"),
            ("      x = x->right;", "code"),
            ("    }", "code"),
            ("  }", "code"),
            ("  z->parent = y;", "code"),
            ("  if (y == NULL) {", "code"),
            ("    T->root = z; // 树为空", "comment"),
            ("  } else if (z->val < y->val) {", "code"),
            ("    y->left = z;", "code"),
            ("  } else {", "code"),
            ("    y->right = z;", "code"),
            ("  }", "code"),
            ("  // 修复红黑性质", "comment"),
            ("  rb_insert_fixup(T, z);", "code"),
        ],
        "java": [
            ("void rbInsert(RBTree T, int val) {", "function"),
            ("  Node z = new Node(val);", "code"),
            ("  z.color = RED;", "code"),
            ("  // 找到插入位置", "comment"),
            ("  Node y = null;", "code"),
            ("  Node x = T.root;", "code"),
            ("  while (x != null) {", "code"),
            ("    y = x;", "code"),
            ("    if (z.val < x.val) {", "code"),
            ("      x = x.left;", "code"),
            ("    } else {", "code"),
            ("      x = x.right;", "code"),
            ("    }", "code"),
            ("  }", "code"),
            ("  z.parent = y;", "code"),
            ("  if (y == null) {", "code"),
            ("    T.root = z; // 树为空", "comment"),
            ("  } else if (z.val < y.val) {", "code"),
            ("    y.left = z;", "code"),
            ("  } else {", "code"),
            ("    y.right = z;", "code"),
            ("  }", "code"),
            ("  // 修复红黑性质", "comment"),
            ("  rbInsertFixup(T, z);", "code"),
        ],
        "python": [
            ("def rb_insert(T, val):", "function"),
            ("  z = Node(val)", "code"),
            ("  z.color = RED", "code"),
            ("  # 找到插入位置", "comment"),
            ("  y = None", "code"),
            ("  x = T.root", "code"),
            ("  while x is not None:", "code"),
            ("    y = x", "code"),
            ("    if z.val < x.val:", "code"),
            ("      x = x.left", "code"),
            ("    else:", "code"),
            ("      x = x.right", "code"),
            ("    # endif", "comment"),
            ("  # endwhile", "comment"),
            ("  z.parent = y", "code"),
            ("  if y is None:", "code"),
            ("    T.root = z  # 树为空", "comment"),
            ("  elif z.val < y.val:", "code"),
            ("    y.left = z", "code"),
            ("  else:", "code"),
            ("    y.right = z", "code"),
            ("  # endif", "comment"),
            ("  # 修复红黑性质", "comment"),
            ("  rb_insert_fixup(T, z)", "code"),
        ]
    }
    
    # 左旋
    LEFT_ROTATE = {
        "pseudo": [
            ("LEFT-ROTATE(T, x):", "function"),
            ("  y ← x.right", "code"),
            ("  x.right ← y.left  // 将y的左子树给x", "comment"),
            ("  if y.left ≠ null then", "code"),
            ("    y.left.parent ← x", "code"),
            ("  end if", "code"),
            ("  y.parent ← x.parent", "code"),
            ("  if x.parent = null then", "code"),
            ("    T.root ← y", "code"),
            ("  else if x = x.parent.left then", "code"),
            ("    x.parent.left ← y", "code"),
            ("  else", "code"),
            ("    x.parent.right ← y", "code"),
            ("  end if", "code"),
            ("  y.left ← x", "code"),
            ("  x.parent ← y", "code"),
        ],
        "c": [
            ("void left_rotate(RBTree* T, Node* x) {", "function"),
            ("  Node* y = x->right;", "code"),
            ("  x->right = y->left; // 将y的左子树给x", "comment"),
            ("  if (y->left != NULL) {", "code"),
            ("    y->left->parent = x;", "code"),
            ("  }", "code"),
            ("  y->parent = x->parent;", "code"),
            ("  if (x->parent == NULL) {", "code"),
            ("    T->root = y;", "code"),
            ("  } else if (x == x->parent->left) {", "code"),
            ("    x->parent->left = y;", "code"),
            ("  } else {", "code"),
            ("    x->parent->right = y;", "code"),
            ("  }", "code"),
            ("  y->left = x;", "code"),
            ("  x->parent = y;", "code"),
        ],
        "java": [
            ("void leftRotate(RBTree T, Node x) {", "function"),
            ("  Node y = x.right;", "code"),
            ("  x.right = y.left; // 将y的左子树给x", "comment"),
            ("  if (y.left != null) {", "code"),
            ("    y.left.parent = x;", "code"),
            ("  }", "code"),
            ("  y.parent = x.parent;", "code"),
            ("  if (x.parent == null) {", "code"),
            ("    T.root = y;", "code"),
            ("  } else if (x == x.parent.left) {", "code"),
            ("    x.parent.left = y;", "code"),
            ("  } else {", "code"),
            ("    x.parent.right = y;", "code"),
            ("  }", "code"),
            ("  y.left = x;", "code"),
            ("  x.parent = y;", "code"),
        ],
        "python": [
            ("def left_rotate(T, x):", "function"),
            ("  y = x.right", "code"),
            ("  x.right = y.left  # 将y的左子树给x", "comment"),
            ("  if y.left is not None:", "code"),
            ("    y.left.parent = x", "code"),
            ("  # endif", "comment"),
            ("  y.parent = x.parent", "code"),
            ("  if x.parent is None:", "code"),
            ("    T.root = y", "code"),
            ("  elif x == x.parent.left:", "code"),
            ("    x.parent.left = y", "code"),
            ("  else:", "code"),
            ("    x.parent.right = y", "code"),
            ("  # endif", "comment"),
            ("  y.left = x", "code"),
            ("  x.parent = y", "code"),
        ]
    }
    
    # 右旋
    RIGHT_ROTATE = {
        "pseudo": [
            ("RIGHT-ROTATE(T, x):", "function"),
            ("  y ← x.left", "code"),
            ("  x.left ← y.right  // 将y的右子树给x", "comment"),
            ("  if y.right ≠ null then", "code"),
            ("    y.right.parent ← x", "code"),
            ("  end if", "code"),
            ("  y.parent ← x.parent", "code"),
            ("  if x.parent = null then", "code"),
            ("    T.root ← y", "code"),
            ("  else if x = x.parent.right then", "code"),
            ("    x.parent.right ← y", "code"),
            ("  else", "code"),
            ("    x.parent.left ← y", "code"),
            ("  end if", "code"),
            ("  y.right ← x", "code"),
            ("  x.parent ← y", "code"),
        ],
        "c": [
            ("void right_rotate(RBTree* T, Node* x) {", "function"),
            ("  Node* y = x->left;", "code"),
            ("  x->left = y->right; // 将y的右子树给x", "comment"),
            ("  if (y->right != NULL) {", "code"),
            ("    y->right->parent = x;", "code"),
            ("  }", "code"),
            ("  y->parent = x->parent;", "code"),
            ("  if (x->parent == NULL) {", "code"),
            ("    T->root = y;", "code"),
            ("  } else if (x == x->parent->right) {", "code"),
            ("    x->parent->right = y;", "code"),
            ("  } else {", "code"),
            ("    x->parent->left = y;", "code"),
            ("  }", "code"),
            ("  y->right = x;", "code"),
            ("  x->parent = y;", "code"),
        ],
        "java": [
            ("void rightRotate(RBTree T, Node x) {", "function"),
            ("  Node y = x.left;", "code"),
            ("  x.left = y.right; // 将y的右子树给x", "comment"),
            ("  if (y.right != null) {", "code"),
            ("    y.right.parent = x;", "code"),
            ("  }", "code"),
            ("  y.parent = x.parent;", "code"),
            ("  if (x.parent == null) {", "code"),
            ("    T.root = y;", "code"),
            ("  } else if (x == x.parent.right) {", "code"),
            ("    x.parent.right = y;", "code"),
            ("  } else {", "code"),
            ("    x.parent.left = y;", "code"),
            ("  }", "code"),
            ("  y.right = x;", "code"),
            ("  x.parent = y;", "code"),
        ],
        "python": [
            ("def right_rotate(T, x):", "function"),
            ("  y = x.left", "code"),
            ("  x.left = y.right  # 将y的右子树给x", "comment"),
            ("  if y.right is not None:", "code"),
            ("    y.right.parent = x", "code"),
            ("  # endif", "comment"),
            ("  y.parent = x.parent", "code"),
            ("  if x.parent is None:", "code"),
            ("    T.root = y", "code"),
            ("  elif x == x.parent.right:", "code"),
            ("    x.parent.right = y", "code"),
            ("  else:", "code"),
            ("    x.parent.left = y", "code"),
            ("  # endif", "comment"),
            ("  y.right = x", "code"),
            ("  x.parent = y", "code"),
        ]
    }


class AVLTreeCode:
    """AVL树操作的多语言代码定义"""
    
    # 插入
    INSERT = {
        "pseudo": [
            ("INSERT(tree, val):", "function"),
            ("  if tree.root = null then", "code"),
            ("    tree.root ← new Node(val)", "code"),
            ("    return", "code"),
            ("  end if", "code"),
            ("  node ← tree.root", "code"),
            ("  while true do", "code"),
            ("    if val < node.val then", "code"),
            ("      if node.left = null then", "code"),
            ("        node.left ← new Node(val)", "code"),
            ("        break", "code"),
            ("      end if", "code"),
            ("      node ← node.left", "code"),
            ("    else", "code"),
            ("      if node.right = null then", "code"),
            ("        node.right ← new Node(val)", "code"),
            ("        break", "code"),
            ("      end if", "code"),
            ("      node ← node.right", "code"),
            ("    end if", "code"),
            ("  end while", "code"),
            ("  REBALANCE(new_node.parent)", "code"),
        ],
        "c": [
            ("void insert(AVLTree* tree, int val) {", "function"),
            ("  if (tree->root == NULL) {", "code"),
            ("    tree->root = create_node(val);", "code"),
            ("    return;", "code"),
            ("  }", "code"),
            ("  Node* node = tree->root;", "code"),
            ("  while (1) {", "code"),
            ("    if (val < node->val) {", "code"),
            ("      if (node->left == NULL) {", "code"),
            ("        node->left = create_node(val);", "code"),
            ("        break;", "code"),
            ("      }", "code"),
            ("      node = node->left;", "code"),
            ("    } else {", "code"),
            ("      if (node->right == NULL) {", "code"),
            ("        node->right = create_node(val);", "code"),
            ("        break;", "code"),
            ("      }", "code"),
            ("      node = node->right;", "code"),
            ("    }", "code"),
            ("  }", "code"),
            ("  rebalance(new_node->parent);", "code"),
        ],
        "java": [
            ("void insert(AVLTree tree, int val) {", "function"),
            ("  if (tree.root == null) {", "code"),
            ("    tree.root = new Node(val);", "code"),
            ("    return;", "code"),
            ("  }", "code"),
            ("  Node node = tree.root;", "code"),
            ("  while (true) {", "code"),
            ("    if (val < node.val) {", "code"),
            ("      if (node.left == null) {", "code"),
            ("        node.left = new Node(val);", "code"),
            ("        break;", "code"),
            ("      }", "code"),
            ("      node = node.left;", "code"),
            ("    } else {", "code"),
            ("      if (node.right == null) {", "code"),
            ("        node.right = new Node(val);", "code"),
            ("        break;", "code"),
            ("      }", "code"),
            ("      node = node.right;", "code"),
            ("    }", "code"),
            ("  }", "code"),
            ("  rebalance(newNode.parent);", "code"),
        ],
        "python": [
            ("def insert(tree, val):", "function"),
            ("  if tree.root is None:", "code"),
            ("    tree.root = Node(val)", "code"),
            ("    return", "code"),
            ("  # endif", "comment"),
            ("  node = tree.root", "code"),
            ("  while True:", "code"),
            ("    if val < node.val:", "code"),
            ("      if node.left is None:", "code"),
            ("        node.left = Node(val)", "code"),
            ("        break", "code"),
            ("      # endif", "comment"),
            ("      node = node.left", "code"),
            ("    else:", "code"),
            ("      if node.right is None:", "code"),
            ("        node.right = Node(val)", "code"),
            ("        break", "code"),
            ("      # endif", "comment"),
            ("      node = node.right", "code"),
            ("    # endif", "comment"),
            ("  # endwhile", "comment"),
            ("  rebalance(new_node.parent)", "code"),
        ]
    }
    
    # LL旋转
    LL_ROTATE = {
        "pseudo": [
            ("LL旋转 - RIGHT_ROTATE(z):", "function"),
            ("  y ← z.left", "code"),
            ("  T3 ← y.right", "code"),
            ("  y.right ← z", "code"),
            ("  z.left ← T3", "code"),
            ("  UPDATE_HEIGHT(z)", "code"),
            ("  UPDATE_HEIGHT(y)", "code"),
            ("  return y  // 新的子树根", "comment"),
        ],
        "c": [
            ("// LL旋转 - 右旋", "comment"),
            ("Node* right_rotate(Node* z) {", "function"),
            ("  Node* y = z->left;", "code"),
            ("  Node* T3 = y->right;", "code"),
            ("  y->right = z;", "code"),
            ("  z->left = T3;", "code"),
            ("  update_height(z);", "code"),
            ("  update_height(y);", "code"),
            ("  return y; // 新的子树根", "comment"),
        ],
        "java": [
            ("// LL旋转 - 右旋", "comment"),
            ("Node rightRotate(Node z) {", "function"),
            ("  Node y = z.left;", "code"),
            ("  Node T3 = y.right;", "code"),
            ("  y.right = z;", "code"),
            ("  z.left = T3;", "code"),
            ("  updateHeight(z);", "code"),
            ("  updateHeight(y);", "code"),
            ("  return y; // 新的子树根", "comment"),
        ],
        "python": [
            ("# LL旋转 - 右旋", "comment"),
            ("def right_rotate(z):", "function"),
            ("  y = z.left", "code"),
            ("  T3 = y.right", "code"),
            ("  y.right = z", "code"),
            ("  z.left = T3", "code"),
            ("  update_height(z)", "code"),
            ("  update_height(y)", "code"),
            ("  return y  # 新的子树根", "comment"),
        ]
    }
    
    # RR旋转
    RR_ROTATE = {
        "pseudo": [
            ("RR旋转 - LEFT_ROTATE(z):", "function"),
            ("  y ← z.right", "code"),
            ("  T2 ← y.left", "code"),
            ("  y.left ← z", "code"),
            ("  z.right ← T2", "code"),
            ("  UPDATE_HEIGHT(z)", "code"),
            ("  UPDATE_HEIGHT(y)", "code"),
            ("  return y  // 新的子树根", "comment"),
        ],
        "c": [
            ("// RR旋转 - 左旋", "comment"),
            ("Node* left_rotate(Node* z) {", "function"),
            ("  Node* y = z->right;", "code"),
            ("  Node* T2 = y->left;", "code"),
            ("  y->left = z;", "code"),
            ("  z->right = T2;", "code"),
            ("  update_height(z);", "code"),
            ("  update_height(y);", "code"),
            ("  return y; // 新的子树根", "comment"),
        ],
        "java": [
            ("// RR旋转 - 左旋", "comment"),
            ("Node leftRotate(Node z) {", "function"),
            ("  Node y = z.right;", "code"),
            ("  Node T2 = y.left;", "code"),
            ("  y.left = z;", "code"),
            ("  z.right = T2;", "code"),
            ("  updateHeight(z);", "code"),
            ("  updateHeight(y);", "code"),
            ("  return y; // 新的子树根", "comment"),
        ],
        "python": [
            ("# RR旋转 - 左旋", "comment"),
            ("def left_rotate(z):", "function"),
            ("  y = z.right", "code"),
            ("  T2 = y.left", "code"),
            ("  y.left = z", "code"),
            ("  z.right = T2", "code"),
            ("  update_height(z)", "code"),
            ("  update_height(y)", "code"),
            ("  return y  # 新的子树根", "comment"),
        ]
    }


def get_all_code_templates():
    """获取所有预定义的代码模板"""
    return {
        # 链表操作
        "insert_head": LinkedListCode.INSERT_HEAD,
        "insert_tail": LinkedListCode.INSERT_TAIL,
        "insert_at_position": LinkedListCode.INSERT_AT_POSITION,
        "delete_head": LinkedListCode.DELETE_HEAD,
        "delete_tail": LinkedListCode.DELETE_TAIL,
        "delete_at_position": LinkedListCode.DELETE_AT_POSITION,
        "search": LinkedListCode.SEARCH,
        "traverse": LinkedListCode.TRAVERSE,
        "reverse": LinkedListCode.REVERSE,
        # 红黑树操作
        "rb_insert": RBTreeCode.INSERT,
        "rb_left_rotate": RBTreeCode.LEFT_ROTATE,
        "rb_right_rotate": RBTreeCode.RIGHT_ROTATE,
        # AVL树操作
        "avl_insert": AVLTreeCode.INSERT,
        "avl_ll": AVLTreeCode.LL_ROTATE,
        "avl_rr": AVLTreeCode.RR_ROTATE,
    }

