from tkinter import *
from tkinter import messagebox, filedialog
import time
from sequence_list.sequence_list_model import SequenceListModel
import os
import storage as storage
import json
from datetime import datetime
import sys
from sequence_list.sequence_ui import create_heading, create_buttons

# 导入 function_dispatcher 用于LLM集成
try:
    from llm import function_dispatcher
except ImportError:
    function_dispatcher = None

# ========== 多语言伪代码定义 ==========

# 语言选项
LANG_PSEUDOCODE = "伪代码"
LANG_C = "C语言"
LANG_JAVA = "Java"
LANG_PYTHON = "Python"
CODE_LANGUAGES = [LANG_PSEUDOCODE, LANG_C, LANG_JAVA, LANG_PYTHON]

# 插入 - 多语言模板
def get_insert_pseudocode(lang, pos, value, length):
    """获取插入操作的多语言伪代码"""
    if lang == "伪代码":
        return [
            {"text": f"// 顺序表插入: Insert({pos}, {value})", "indent": 0},
            {"text": f"if pos < 0 or pos > length then  // pos={pos}, length={length}", "indent": 0},
            {"text": "  return ERROR  // 位置非法", "indent": 0},
            {"text": "end if", "indent": 0},
            {"text": "if length ≥ capacity then", "indent": 0},
            {"text": "  扩容或返回错误", "indent": 0},
            {"text": "end if", "indent": 0},
            {"text": f"for i ← length-1 down to pos do  // 后移元素", "indent": 0},
            {"text": "  data[i+1] ← data[i]", "indent": 0},
            {"text": "end for", "indent": 0},
            {"text": f"data[{pos}] ← {value}  // 插入新元素", "indent": 0},
            {"text": f"length ← length + 1  // length变为{length+1}", "indent": 0},
            {"text": "return OK  // ✅ 插入成功", "indent": 0},
        ]
    elif lang == "C语言":
        return [
            {"text": f"// 顺序表插入: Insert({pos}, {value})", "indent": 0},
            {"text": f"if (pos < 0 || pos > length) {{ // pos={pos}, length={length}", "indent": 0},
            {"text": "  return ERROR; // 位置非法", "indent": 0},
            {"text": "}", "indent": 0},
            {"text": "if (length >= capacity) {", "indent": 0},
            {"text": "  // 扩容或返回错误", "indent": 0},
            {"text": "}", "indent": 0},
            {"text": f"for (int i = length-1; i >= pos; i--) {{ // 后移元素", "indent": 0},
            {"text": "  data[i+1] = data[i];", "indent": 0},
            {"text": "}", "indent": 0},
            {"text": f"data[{pos}] = {value}; // 插入新元素", "indent": 0},
            {"text": f"length++; // length变为{length+1}", "indent": 0},
            {"text": "return OK; // ✅ 插入成功", "indent": 0},
        ]
    elif lang == "Java":
        return [
            {"text": f"// 顺序表插入: insert({pos}, {value})", "indent": 0},
            {"text": f"if (pos < 0 || pos > length) {{ // pos={pos}, length={length}", "indent": 0},
            {"text": "  throw new IndexOutOfBoundsException(); // 位置非法", "indent": 0},
            {"text": "}", "indent": 0},
            {"text": "if (length >= capacity) {", "indent": 0},
            {"text": "  expand(); // 扩容", "indent": 0},
            {"text": "}", "indent": 0},
            {"text": f"for (int i = length-1; i >= pos; i--) {{ // 后移元素", "indent": 0},
            {"text": "  data[i+1] = data[i];", "indent": 0},
            {"text": "}", "indent": 0},
            {"text": f"data[{pos}] = {value}; // 插入新元素", "indent": 0},
            {"text": f"length++; // length变为{length+1}", "indent": 0},
            {"text": "return true; // ✅ 插入成功", "indent": 0},
        ]
    else:  # Python
        return [
            {"text": f"# 顺序表插入: insert({pos}, {value})", "indent": 0},
            {"text": f"if pos < 0 or pos > length:  # pos={pos}, length={length}", "indent": 0},
            {"text": "  raise IndexError('位置非法')", "indent": 0},
            {"text": "# endif", "indent": 0},
            {"text": "if length >= capacity:", "indent": 0},
            {"text": "  self.expand()  # 扩容", "indent": 0},
            {"text": "# endif", "indent": 0},
            {"text": f"for i in range(length-1, pos-1, -1):  # 后移元素", "indent": 0},
            {"text": "  data[i+1] = data[i]", "indent": 0},
            {"text": "# endfor", "indent": 0},
            {"text": f"data[{pos}] = {value}  # 插入新元素", "indent": 0},
            {"text": f"length += 1  # length变为{length+1}", "indent": 0},
            {"text": "return True  # ✅ 插入成功", "indent": 0},
        ]

# 删除 - 多语言模板
def get_delete_pseudocode(lang, pos, length):
    """获取删除操作的多语言伪代码"""
    if lang == "伪代码":
        return [
            {"text": f"// 顺序表删除: Delete({pos})", "indent": 0},
            {"text": f"if pos < 0 or pos ≥ length then  // pos={pos}, length={length}", "indent": 0},
            {"text": "  return ERROR  // 位置非法", "indent": 0},
            {"text": "end if", "indent": 0},
            {"text": "value ← data[pos]  // 保存被删元素", "indent": 0},
            {"text": f"for i ← pos to length-2 do  // 前移元素", "indent": 0},
            {"text": "  data[i] ← data[i+1]", "indent": 0},
            {"text": "end for", "indent": 0},
            {"text": f"length ← length - 1  // length变为{length-1}", "indent": 0},
            {"text": "return value  // ✅ 删除成功", "indent": 0},
        ]
    elif lang == "C语言":
        return [
            {"text": f"// 顺序表删除: Delete({pos})", "indent": 0},
            {"text": f"if (pos < 0 || pos >= length) {{ // pos={pos}, length={length}", "indent": 0},
            {"text": "  return ERROR; // 位置非法", "indent": 0},
            {"text": "}", "indent": 0},
            {"text": "int value = data[pos]; // 保存被删元素", "indent": 0},
            {"text": f"for (int i = pos; i < length-1; i++) {{ // 前移元素", "indent": 0},
            {"text": "  data[i] = data[i+1];", "indent": 0},
            {"text": "}", "indent": 0},
            {"text": f"length--; // length变为{length-1}", "indent": 0},
            {"text": "return value; // ✅ 删除成功", "indent": 0},
        ]
    elif lang == "Java":
        return [
            {"text": f"// 顺序表删除: delete({pos})", "indent": 0},
            {"text": f"if (pos < 0 || pos >= length) {{ // pos={pos}, length={length}", "indent": 0},
            {"text": "  throw new IndexOutOfBoundsException(); // 位置非法", "indent": 0},
            {"text": "}", "indent": 0},
            {"text": "int value = data[pos]; // 保存被删元素", "indent": 0},
            {"text": f"for (int i = pos; i < length-1; i++) {{ // 前移元素", "indent": 0},
            {"text": "  data[i] = data[i+1];", "indent": 0},
            {"text": "}", "indent": 0},
            {"text": f"length--; // length变为{length-1}", "indent": 0},
            {"text": "return value; // ✅ 删除成功", "indent": 0},
        ]
    else:  # Python
        return [
            {"text": f"# 顺序表删除: delete({pos})", "indent": 0},
            {"text": f"if pos < 0 or pos >= length:  # pos={pos}, length={length}", "indent": 0},
            {"text": "  raise IndexError('位置非法')", "indent": 0},
            {"text": "# endif", "indent": 0},
            {"text": "value = data[pos]  # 保存被删元素", "indent": 0},
            {"text": f"for i in range(pos, length-1):  # 前移元素", "indent": 0},
            {"text": "  data[i] = data[i+1]", "indent": 0},
            {"text": "# endfor", "indent": 0},
            {"text": f"length -= 1  # length变为{length-1}", "indent": 0},
            {"text": "return value  # ✅ 删除成功", "indent": 0},
        ]

# 查找 - 多语言模板
def get_search_pseudocode(lang, value, length):
    """获取查找操作的多语言伪代码"""
    if lang == "伪代码":
        return [
            {"text": f"// 顺序表查找: Search({value})", "indent": 0},
            {"text": f"for i ← 0 to length-1 do  // length={length}", "indent": 0},
            {"text": f"  if data[i] = {value} then", "indent": 0},
            {"text": "    return i  // 找到，返回位置", "indent": 0},
            {"text": "  end if", "indent": 0},
            {"text": "end for", "indent": 0},
            {"text": "return -1  // 未找到", "indent": 0},
        ]
    elif lang == "C语言":
        return [
            {"text": f"// 顺序表查找: Search({value})", "indent": 0},
            {"text": f"for (int i = 0; i < length; i++) {{ // length={length}", "indent": 0},
            {"text": f"  if (data[i] == {value}) {{", "indent": 0},
            {"text": "    return i; // 找到，返回位置", "indent": 0},
            {"text": "  }", "indent": 0},
            {"text": "}", "indent": 0},
            {"text": "return -1; // 未找到", "indent": 0},
        ]
    elif lang == "Java":
        return [
            {"text": f"// 顺序表查找: search({value})", "indent": 0},
            {"text": f"for (int i = 0; i < length; i++) {{ // length={length}", "indent": 0},
            {"text": f"  if (data[i] == {value}) {{", "indent": 0},
            {"text": "    return i; // 找到，返回位置", "indent": 0},
            {"text": "  }", "indent": 0},
            {"text": "}", "indent": 0},
            {"text": "return -1; // 未找到", "indent": 0},
        ]
    else:  # Python
        return [
            {"text": f"# 顺序表查找: search({value})", "indent": 0},
            {"text": f"for i in range(length):  # length={length}", "indent": 0},
            {"text": f"  if data[i] == {value}:", "indent": 0},
            {"text": "    return i  # 找到，返回位置", "indent": 0},
            {"text": "  # endif", "indent": 0},
            {"text": "# endfor", "indent": 0},
            {"text": "return -1  # 未找到", "indent": 0},
        ]

# 追加/构建 - 多语言模板
def get_append_pseudocode(lang, index, value):
    """获取追加操作的多语言伪代码"""
    if lang == "伪代码":
        return [
            f"// 在末尾添加元素 '{value}' (索引 {index})",
            "if length ≥ capacity then",
            "  扩容(capacity ← capacity × 2)",
            "end if",
            f"data[length] ← {value}  // 添加到末尾",
            "length ← length + 1  // 长度加1",
            "// 添加完成"
        ]
    elif lang == "C语言":
        return [
            f"// 在末尾添加元素 '{value}' (索引 {index})",
            "if (length >= capacity) {",
            "  expand(); // 扩容",
            "}",
            f"data[length] = {value}; // 添加到末尾",
            "length++; // 长度加1",
            "// 添加完成"
        ]
    elif lang == "Java":
        return [
            f"// 在末尾添加元素 '{value}' (索引 {index})",
            "if (length >= capacity) {",
            "  expand(); // 扩容",
            "}",
            f"data[length] = {value}; // 添加到末尾",
            "length++; // 长度加1",
            "// 添加完成"
        ]
    else:  # Python
        return [
            f"# 在末尾添加元素 '{value}' (索引 {index})",
            "if length >= capacity:",
            "  self.expand()  # 扩容",
            "# endif",
            f"data[length] = {value}  # 添加到末尾",
            "length += 1  # 长度加1",
            "# 添加完成"
        ]

# 清空 - 多语言模板
def get_clear_pseudocode_seq(lang, count):
    """获取清空操作的多语言伪代码"""
    if lang == "伪代码":
        return [
            f"// 清空操作: 移除所有 {count} 个元素",
            "for i ← length-1 downto 0 do",
            "  data[i] ← NULL  // 清除元素",
            "end for",
            "length ← 0  // 长度归零",
            "// 清空完成"
        ]
    elif lang == "C语言":
        return [
            f"// 清空操作: 移除所有 {count} 个元素",
            "for (int i = length-1; i >= 0; i--) {",
            "  data[i] = 0; // 清除元素",
            "}",
            "length = 0; // 长度归零",
            "// 清空完成"
        ]
    elif lang == "Java":
        return [
            f"// 清空操作: 移除所有 {count} 个元素",
            "for (int i = length-1; i >= 0; i--) {",
            "  data[i] = null; // 清除元素",
            "}",
            "length = 0; // 长度归零",
            "// 清空完成"
        ]
    else:  # Python
        return [
            f"# 清空操作: 移除所有 {count} 个元素",
            "for i in range(length-1, -1, -1):",
            "  data[i] = None  # 清除元素",
            "# endfor",
            "length = 0  # 长度归零",
            "# 清空完成"
        ]

class SequenceListVisualizer:
    def __init__(self, root):
        self.window = root
        self.window.config(bg="lightgreen")

        # 把容量放到模型里，模型默认初始容量是 11（可以在创建模型时修改）
        self.model = SequenceListModel(capacity=11)
        
        # 新增：动画速度控制
        self.animation_speed = 0.03  # 默认速度
        self.step_by_step = False    # 单步执行模式
        self.current_step = 0        # 当前步骤
        
        # 代码语言设置（支持运行时切换）
        self.current_code_language = LANG_PSEUDOCODE  # 默认伪代码
        self.current_operation_context = None  # 保存当前操作上下文，用于语言切换时重新渲染
        
        # 新增：操作历史记录
        self.operation_history = []
        
        # 创建主内容区域框架（包含画布和伪代码面板）
        main_content = Frame(self.window, bg="lightgreen")
        main_content.pack(fill=BOTH, expand=True, padx=10, pady=5)
        
        # 左侧：画布容器（可滚动）
        canvas_container = Frame(main_content, bg="lightgreen")
        canvas_container.pack(side=LEFT, fill=BOTH, expand=True)

        self.h_scroll = Scrollbar(canvas_container, orient=HORIZONTAL)
        self.h_scroll.pack(side=BOTTOM, fill=X)

        # 调整画布宽度，为右侧伪代码面板留出空间
        self.canvas = Canvas(canvas_container, bg="lightyellow", width=1000, height=380, relief=RAISED, bd=6,
                             xscrollcommand=self.h_scroll.set)
        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)
        self.h_scroll.config(command=self.canvas.xview)
        
        # 右侧：伪代码显示面板（固定位置，不随画布滚动）
        self.create_pseudo_code_panel(main_content)

        # 支持按住鼠标拖动平移画布
        self.canvas.bind("<ButtonPress-1>", lambda e: self.canvas.scan_mark(e.x, e.y))
        self.canvas.bind("<B1-Motion>", lambda e: self.canvas.scan_dragto(e.x, e.y, gain=1))

        # 鼠标滚轮水平滚动绑定：跨平台支持（Windows/Mac/Linux）
        # Shift+滚轮 和 普通滚轮都会映射为水平滚动（便于触控板用户）
        def _on_mousewheel(e):
            # Windows / Mac : e.delta 有正负，120 的倍数通常是单位
            delta = 0
            try:
                delta = int(-1 * (e.delta / 120))
            except Exception:
                # fallback
                delta = 0
            if delta != 0:
                self.canvas.xview_scroll(delta, "units")

        # Linux 常见的 Button-4/5（向上/向下滚轮）
        def _on_button4(e):
            self.canvas.xview_scroll(-1, "units")
        def _on_button5(e):
            self.canvas.xview_scroll(1, "units")

        # 绑定
        self.canvas.bind("<MouseWheel>", _on_mousewheel)            # Windows / Mac
        self.canvas.bind("<Shift-MouseWheel>", _on_mousewheel)      # Shift + 滚轮
        self.canvas.bind("<Button-4>", _on_button4)                 # Linux up
        self.canvas.bind("<Button-5>", _on_button5)                 # Linux down

        # 模型数据与 UI 存储
        self.dsl_var=StringVar()
        self.data_rectangles = []  # 数据矩形
        self.data_labels = []      # 数据标签
        self.index_labels = []     # 索引标签
        
        # 新增：步骤说明文本
        self.step_text_id = None
        self.pseudo_code_ids = []

        # 坐标和尺寸参数
        self.start_x = 100
        self.start_y = 200
        self.cell_width = 60
        self.cell_height = 40
        self.spacing = 5

        # 输入变量
        self.value_entry = StringVar()
        self.position_entry = StringVar()

        # 按钮列表
        self.buttons = []  # 初始化按钮列表
        
        # 伪代码相关变量
        self.pseudo_code_lines = []  # 当前显示的伪代码行
        self.current_highlight_line = -1  # 当前高亮的行号
        
        # 新增：控制面板
        self.create_control_panel()

        # 初始化界面
        create_heading(self)
        create_buttons(self)
        self.update_display()
        
        # LLM集成：初始化chat_window引用并注册到function_dispatcher
        self.chat_window = None
        if function_dispatcher:
            function_dispatcher.register_visualizer("sequence", self)
    
    def set_chat_window(self, chat_window):
        """设置LLM聊天窗口引用"""
        self.chat_window = chat_window
    
    def _execute_dsl(self, event=None):
        """执行DSL命令（供LLM调用）"""
        self.process_dsl(event)
    
    # ========== LLM集成方法 ==========
    def batch_create(self, values):
        """批量创建顺序表元素（供LLM调用）"""
        if getattr(self, 'animating', False):
            return
        # 转换values为列表
        if isinstance(values, str):
            values = [v.strip() for v in values.split(",") if v.strip()]
        
        self.disable_buttons()
        try:
            self.model.clear()
            self.update_display()
            for i, v in enumerate(values):
                self.model.append(v)
                try:
                    self.animate_build_element(i, v)
                except Exception:
                    self.update_display()
                self.window.update()
                time.sleep(0.06)
        finally:
            self.enable_buttons()
    
    def insert_last(self, value):
        """在尾部插入元素（供LLM调用）"""
        if getattr(self, 'animating', False):
            return
        pos = len(self.data_store)
        self.model.insert(pos, value)
        try:
            self.animate_insert(pos, value)
        except Exception:
            self.update_display()
    
    def insert_first(self, value):
        """在头部插入元素（供LLM调用）"""
        if getattr(self, 'animating', False):
            return
        self.model.insert(0, value)
        try:
            self.animate_insert(0, value)
        except Exception:
            self.update_display()
    
    def insert_at(self, index, value):
        """在指定位置插入元素（供LLM调用）"""
        if getattr(self, 'animating', False):
            return
        n = len(self.data_store)
        if index < 0 or index > n:
            raise ValueError(f"位置越界：合法范围 0..{n}")
        self.model.insert(index, value)
        try:
            self.animate_insert(index, value)
        except Exception:
            self.update_display()
    
    def delete_at(self, index):
        """删除指定位置的元素（供LLM调用）"""
        if getattr(self, 'animating', False):
            return
        n = len(self.data_store)
        if n == 0:
            raise ValueError("顺序表为空")
        if index < 0 or index >= n:
            raise ValueError(f"位置越界：合法范围 0..{n-1}")
        try:
            self.animate_delete(index)
        except Exception:
            self.model.delete(index)
            self.update_display()
    
    def clear(self):
        """清空顺序表（供LLM调用）"""
        self.clear_list()
    
    def get_state(self):
        """获取当前顺序表状态（供LLM调用）"""
        return {
            "data": list(self.data_store),
            "length": len(self.data_store),
            "capacity": self.model.capacity
        }
    
    def create_pseudo_code_panel(self, parent):
        """创建伪代码显示面板（固定在右侧）"""
        # 伪代码面板框架 - 调整尺寸以适应布局
        pseudo_frame = Frame(parent, bg="#2d3436", relief=RAISED, bd=2, width=320)
        pseudo_frame.pack(side=RIGHT, fill=Y, padx=(8, 0))
        pseudo_frame.pack_propagate(False)
        
        # 标题栏（包含标题和语言切换）
        title_frame = Frame(pseudo_frame, bg="#2d3436")
        title_frame.pack(fill=X, padx=10, pady=5)
        
        title_label = Label(title_frame, text="📋 代码执行", 
                           font=("微软雅黑", 11, "bold"), 
                           bg="#2d3436", fg="#00cec9")
        title_label.pack(side=LEFT)
        
        # 语言切换下拉框
        self.code_lang_var = StringVar(value=self.current_code_language)
        self.lang_menu = OptionMenu(
            title_frame, 
            self.code_lang_var, 
            *CODE_LANGUAGES,
            command=self._on_code_language_change
        )
        self.lang_menu.config(
            font=("微软雅黑", 8),
            bg="#45475A",
            fg="#CDD6F4",
            activebackground="#585B70",
            activeforeground="#CDD6F4",
            highlightthickness=0,
            relief="flat",
            width=5
        )
        self.lang_menu["menu"].config(
            bg="#45475A",
            fg="#CDD6F4",
            activebackground="#00cec9",
            activeforeground="#1E1E2E",
            font=("微软雅黑", 8)
        )
        self.lang_menu.pack(side=RIGHT)
        
        # 语言切换快捷按钮组
        lang_btn_frame = Frame(pseudo_frame, bg="#2d3436")
        lang_btn_frame.pack(fill=X, padx=10, pady=(0, 5))
        
        self.lang_buttons = {}
        for lang in CODE_LANGUAGES:
            short_name = {"伪代码": "伪代码", "C语言": "C", "Java": "Java", "Python": "Py"}.get(lang, lang)
            btn = Label(
                lang_btn_frame,
                text=short_name,
                font=("微软雅黑", 8),
                bg="#00cec9" if lang == self.current_code_language else "#45475A",
                fg="#1E1E2E" if lang == self.current_code_language else "#CDD6F4",
                padx=6,
                pady=2,
                cursor="hand2"
            )
            btn.pack(side=LEFT, padx=2)
            btn.bind("<Button-1>", lambda e, l=lang: self._switch_code_language(l))
            self.lang_buttons[lang] = btn
        
        # 分隔线
        separator = Frame(pseudo_frame, height=2, bg="#00cec9")
        separator.pack(fill=X, padx=10, pady=(0, 3))
        
        # 当前操作标签
        self.operation_label = Label(pseudo_frame, text="等待操作...", 
                                     font=("微软雅黑", 10), 
                                     bg="#2d3436", fg="#dfe6e9", 
                                     wraplength=290, justify=LEFT)
        self.operation_label.pack(fill=X, padx=10, pady=3)
        
        # 伪代码显示区域（使用Text组件支持高亮）
        code_container = Frame(pseudo_frame, bg="#1e272e")
        code_container.pack(fill=BOTH, expand=True, padx=8, pady=5)
        
        self.pseudo_text = Text(code_container, 
                               font=("Consolas", 10), 
                               bg="#1e272e", fg="#b2bec3",
                               relief=FLAT, 
                               wrap=WORD,
                               padx=8, pady=8,
                               cursor="arrow",
                               state=DISABLED,
                               height=10,
                               width=34)
        self.pseudo_text.pack(fill=BOTH, expand=True)
        
        # 配置高亮标签样式
        self.pseudo_text.tag_configure("highlight", 
                                       background="#00b894", 
                                       foreground="#ffffff",
                                       font=("Consolas", 10, "bold"))
        self.pseudo_text.tag_configure("executed", 
                                       foreground="#55efc4")
        self.pseudo_text.tag_configure("pending", 
                                       foreground="#636e72")
        self.pseudo_text.tag_configure("comment", 
                                       foreground="#74b9ff",
                                       font=("Consolas", 9, "italic"))
        self.pseudo_text.tag_configure("keyword", 
                                       foreground="#fd79a8",
                                       font=("Consolas", 10, "bold"))
        self.pseudo_text.tag_configure("variable", 
                                       foreground="#ffeaa7")
        
        # 进度指示器
        progress_frame = Frame(pseudo_frame, bg="#2d3436")
        progress_frame.pack(fill=X, padx=10, pady=(0, 5))
        
        self.progress_label = Label(progress_frame, text="步骤: 0/0", 
                                    font=("Arial", 9), 
                                    bg="#2d3436", fg="#b2bec3")
        self.progress_label.pack(side=LEFT)
        
        self.status_indicator = Label(progress_frame, text="⚫ 空闲", 
                                      font=("Arial", 9), 
                                      bg="#2d3436", fg="#b2bec3")
        self.status_indicator.pack(side=RIGHT)
        
        # === 控制区域（整合到伪代码面板底部）===
        control_separator = Frame(pseudo_frame, height=1, bg="#636e72")
        control_separator.pack(fill=X, padx=10, pady=5)
        
        # 速度控制
        speed_frame = Frame(pseudo_frame, bg="#2d3436")
        speed_frame.pack(fill=X, padx=10, pady=2)
        
        speed_label = Label(speed_frame, text="动画速度:", font=("Arial", 9), 
                           bg="#2d3436", fg="#dfe6e9")
        speed_label.pack(side=LEFT)
        
        self.speed_var = DoubleVar(value=self.animation_speed)
        speed_scale = Scale(speed_frame, from_=0.01, to=0.1, resolution=0.01, 
                           orient=HORIZONTAL, variable=self.speed_var,
                           command=self.update_speed, length=150,
                           bg="#2d3436", fg="#dfe6e9", highlightthickness=0,
                           troughcolor="#1e272e", activebackground="#00b894")
        speed_scale.pack(side=RIGHT, padx=5)
        
        # 单步执行模式
        self.step_var = BooleanVar()
        step_check = Checkbutton(pseudo_frame, text="单步执行模式", variable=self.step_var,
                                font=("Arial", 9), bg="#2d3436", fg="#dfe6e9",
                                selectcolor="#1e272e", activebackground="#2d3436",
                                activeforeground="#dfe6e9", command=self.toggle_step_mode)
        step_check.pack(anchor=W, padx=10, pady=2)
        
        # 按钮区域
        btn_frame = Frame(pseudo_frame, bg="#2d3436")
        btn_frame.pack(fill=X, padx=10, pady=5)
        
        self.next_step_btn = Button(btn_frame, text="下一步", font=("Arial", 9),
                                   command=self.next_step, state=DISABLED,
                                   bg="#636e72", fg="white", relief=FLAT)
        self.next_step_btn.pack(side=LEFT, padx=2)
        
        reset_btn = Button(btn_frame, text="重置", font=("Arial", 9),
                          command=self.reset_sequence,
                          bg="#e74c3c", fg="white", relief=FLAT)
        reset_btn.pack(side=RIGHT, padx=2)
    
    def _on_code_language_change(self, selected_lang):
        """语言切换回调（下拉框）"""
        self._switch_code_language(selected_lang)
    
    def _switch_code_language(self, new_lang):
        """切换代码语言"""
        if new_lang == self.current_code_language:
            return
        
        self.current_code_language = new_lang
        self.code_lang_var.set(new_lang)
        
        # 更新按钮样式
        for lang, btn in self.lang_buttons.items():
            if lang == new_lang:
                btn.config(bg="#00cec9", fg="#1E1E2E")
            else:
                btn.config(bg="#45475A", fg="#CDD6F4")
        
        # 重新渲染当前操作的伪代码
        self._rerender_current_pseudocode()
    
    def _rerender_current_pseudocode(self):
        """根据当前语言重新渲染伪代码"""
        if not self.current_operation_context:
            return
        
        ctx = self.current_operation_context
        op_type = ctx.get('type')
        
        if op_type == 'insert':
            pseudo_lines = get_insert_pseudocode(
                self.current_code_language, 
                ctx.get('position'), 
                ctx.get('value'),
                ctx.get('length')
            )
            self.set_pseudo_code(ctx.get('title', '插入操作'), pseudo_lines)
        elif op_type == 'delete':
            pseudo_lines = get_delete_pseudocode(
                self.current_code_language,
                ctx.get('position'),
                ctx.get('length')
            )
            self.set_pseudo_code(ctx.get('title', '删除操作'), pseudo_lines)
        elif op_type == 'append':
            pseudo_lines = get_append_pseudocode(
                self.current_code_language,
                ctx.get('index'),
                ctx.get('value')
            )
            self.set_pseudo_code(ctx.get('title', '添加操作'), pseudo_lines)
        elif op_type == 'clear':
            pseudo_lines = get_clear_pseudocode_seq(
                self.current_code_language,
                ctx.get('count')
            )
            self.set_pseudo_code(ctx.get('title', '清空操作'), pseudo_lines)
        
        # 恢复高亮状态
        if ctx.get('highlight_line', -1) >= 0:
            self.highlight_pseudo_line(ctx['highlight_line'], delay=False)
        
    def set_pseudo_code(self, title, lines):
        """设置要显示的伪代码
        
        Args:
            title: 操作标题（如"插入操作"）
            lines: 伪代码行列表，每行是一个字典：
                   {"text": "代码文本", "indent": 缩进级别(0,1,2...)}
                   或简单字符串
        """
        self.pseudo_code_lines = lines
        self.current_highlight_line = -1
        
        # 更新操作标题
        self.operation_label.config(text=title, fg="#74b9ff")
        
        # 更新状态指示器
        self.status_indicator.config(text="🟢 执行中", fg="#00b894")
        
        # 清空并重新填充伪代码
        self.pseudo_text.config(state=NORMAL)
        self.pseudo_text.delete(1.0, END)
        
        for i, line in enumerate(lines):
            if isinstance(line, dict):
                text = line.get("text", "")
                indent = line.get("indent", 0)
                line_text = "  " * indent + text
            else:
                line_text = str(line)
            
            # 添加行号
            line_num = f"{i+1:2}. "
            self.pseudo_text.insert(END, line_num, "pending")
            self.pseudo_text.insert(END, line_text + "\n", "pending")
        
        self.pseudo_text.config(state=DISABLED)
        self.progress_label.config(text=f"步骤: 0/{len(lines)}")
        self.window.update()
    
    def highlight_pseudo_line(self, line_index, delay=True):
        """高亮指定行的伪代码
        
        Args:
            line_index: 要高亮的行索引（0-based）
            delay: 是否在高亮后暂停一小段时间
        """
        if not self.pseudo_code_lines or line_index < 0:
            return
            
        if line_index >= len(self.pseudo_code_lines):
            return
        
        self.pseudo_text.config(state=NORMAL)
        
        # 移除之前的高亮，将已执行的行标记为executed
        for i in range(len(self.pseudo_code_lines)):
            start_pos = f"{i+1}.0"
            end_pos = f"{i+1}.end"
            self.pseudo_text.tag_remove("highlight", start_pos, end_pos)
            self.pseudo_text.tag_remove("pending", start_pos, end_pos)
            self.pseudo_text.tag_remove("executed", start_pos, end_pos)
            
            if i < line_index:
                # 已执行的行
                self.pseudo_text.tag_add("executed", start_pos, end_pos)
            elif i == line_index:
                # 当前执行的行
                self.pseudo_text.tag_add("highlight", start_pos, end_pos)
            else:
                # 待执行的行
                self.pseudo_text.tag_add("pending", start_pos, end_pos)
        
        self.pseudo_text.config(state=DISABLED)
        
        # 确保高亮行可见
        self.pseudo_text.see(f"{line_index+1}.0")
        
        # 更新进度
        self.current_highlight_line = line_index
        self.progress_label.config(text=f"步骤: {line_index+1}/{len(self.pseudo_code_lines)}")
        
        self.window.update()
        
        if delay:
            time.sleep(self.animation_speed * 5)  # 给用户时间阅读
    
    def clear_pseudo_code(self):
        """清除伪代码显示"""
        self.pseudo_code_lines = []
        self.current_highlight_line = -1
        
        self.operation_label.config(text="等待操作...", fg="#dfe6e9")
        self.status_indicator.config(text="⚫ 空闲", fg="#b2bec3")
        self.progress_label.config(text="步骤: 0/0")
        
        self.pseudo_text.config(state=NORMAL)
        self.pseudo_text.delete(1.0, END)
        self.pseudo_text.config(state=DISABLED)
        self.window.update()
    
    def complete_pseudo_code(self):
        """标记伪代码执行完成"""
        self.pseudo_text.config(state=NORMAL)
        
        # 将所有行标记为已执行
        for i in range(len(self.pseudo_code_lines)):
            start_pos = f"{i+1}.0"
            end_pos = f"{i+1}.end"
            self.pseudo_text.tag_remove("highlight", start_pos, end_pos)
            self.pseudo_text.tag_remove("pending", start_pos, end_pos)
            self.pseudo_text.tag_add("executed", start_pos, end_pos)
        
        self.pseudo_text.config(state=DISABLED)
        
        # 更新状态
        self.status_indicator.config(text="✅ 完成", fg="#55efc4")
        self.progress_label.config(text=f"步骤: {len(self.pseudo_code_lines)}/{len(self.pseudo_code_lines)}")
        self.window.update()
        
    def create_control_panel(self):
        """创建控制面板 - 已整合到伪代码面板中，此方法保留为空以兼容"""
        # 控制功能已整合到伪代码面板底部
        # 创建一个隐藏的history_text以兼容其他方法
        self.history_text = Text(self.window)
        self.history_text.place(x=-1000, y=-1000)  # 放在屏幕外
        self.history_text.config(state=DISABLED)

    def update_speed(self, value):
        """更新动画速度"""
        self.animation_speed = float(value)
        
    def toggle_step_mode(self):
        """切换单步执行模式"""
        self.step_by_step = self.step_var.get()
        if self.step_by_step:
            self.next_step_btn.config(state=NORMAL)
        else:
            self.next_step_btn.config(state=DISABLED)
            
    def next_step(self):
        """执行下一步（单步模式）"""
        self.current_step += 1
        
    def wait_for_step(self):
        """等待单步执行（如果启用单步模式）"""
        if self.step_by_step:
            self.current_step = 0
            # 等待用户点击"下一步"按钮
            self.window.wait_variable(self.step_var)
            
    def reset_sequence(self):
        """重置顺序表"""
        self.model.clear()
        self.operation_history = []
        self.update_history_display()
        self.update_display()
        messagebox.showinfo("重置", "顺序表已重置")

    def update_history_display(self):
        """更新操作历史显示"""
        self.history_text.config(state=NORMAL)
        self.history_text.delete(1.0, END)
        for op in self.operation_history[-10:]:  # 只显示最近10条记录
            self.history_text.insert(END, f"{op}\n")
        self.history_text.see(END)  # 滚动到底部
        self.history_text.config(state=DISABLED)

    def add_operation_history(self, operation):
        """添加操作历史记录"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.operation_history.append(f"[{timestamp}] {operation}")
        self.update_history_display()

    def show_step(self, text):
        """显示当前步骤说明"""
        # 清除之前的步骤说明
        if self.step_text_id:
            self.canvas.delete(self.step_text_id)
        
        # 显示新步骤说明 - 放在顶部中间位置，避免与其他文本重叠
        self.step_text_id = self.canvas.create_text(650, 30, text=text, 
                                                   font=("Arial", 14, "bold"), 
                                                   fill="blue", anchor="center")
        self.window.update()
        
        # 短暂暂停，让用户阅读步骤说明
        time.sleep(0.5)

    def show_pseudo_code(self, lines):
        """显示伪代码（兼容旧接口，现在使用新的面板系统）"""
        # 使用新的面板系统显示伪代码
        if lines:
            title = lines[0] if lines else "操作"
            self.set_pseudo_code(title, lines[1:] if len(lines) > 1 else lines)

    def highlight_element(self, index, color="orange"):
        """高亮指定元素"""
        if 0 <= index < len(self.data_rectangles):
            original_color = self.canvas.itemcget(self.data_rectangles[index], "fill")
            self.canvas.itemconfig(self.data_rectangles[index], fill=color)
            self.window.update()
            
            # 短暂闪烁效果
            for _ in range(2):
                self.canvas.itemconfig(self.data_rectangles[index], fill="yellow")
                self.window.update()
                time.sleep(0.1)
                self.canvas.itemconfig(self.data_rectangles[index], fill=color)
                self.window.update()
                time.sleep(0.1)
                
            return original_color
        return None

    def restore_element_color(self, index, color):
        """恢复元素颜色"""
        if 0 <= index < len(self.data_rectangles) and color:
            self.canvas.itemconfig(self.data_rectangles[index], fill=color)

    def _ensure_capacity_for(self, needed: int):
        """
        调用模型的 ensure_capacity_for，并把每次扩容通过 messagebox 通知用户（与旧行为一致）。
        返回 True/False 表示是否发生扩容。
        """
        try:
            expansions = self.model.ensure_capacity_for(needed)
        except Exception:
            expansions = []
        changed = False
        for old, new in expansions:
            changed = True
            try:
                messagebox.showinfo("容量扩展", f"容量已从 {old} 扩展到 {new}")
                self.add_operation_history(f"容量扩展: {old} -> {new}")
            except Exception:
                pass
        if changed:
            try:
                # 更新显示以反映新容量（确保画布 scrollregion 更新）
                self.update_display()
            except Exception:
                pass
        return changed

    def update_status(self, txt: str):
        """简单的状态更新（顺序表模块使用）"""
        try:
            if hasattr(self, 'status_label'):
                self.status_label.config(text=txt)
        except Exception:
            pass

    @property
    def data_store(self):
        """动态返回当前模型的数据列表，避免旧引用不同步问题。"""
        return getattr(self.model, "data", [])

    def _ensure_sequence_folder(self):
        if hasattr(storage, "ensure_save_subdir"):
            return storage.ensure_save_subdir("sequence")
        base_dir = os.path.dirname(os.path.abspath(storage.__file__))
        default_dir = os.path.join(base_dir, "save", "sequence")
        os.makedirs(default_dir, exist_ok=True)
        return default_dir

    def save_sequence(self):
        arr = list(self.data_store)
        meta = {"length": len(arr)}
        default_dir = self._ensure_sequence_folder()
        default_name = f"sequence_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = filedialog.asksaveasfilename(
            initialdir=default_dir,
            initialfile=default_name,
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="保存顺序表到文件"
        )
        if not filepath:
            return
        payload = {"type": "sequence", "data": arr, "metadata": meta}
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        messagebox.showinfo("成功", f"顺序表已保存到：\n{filepath}")
        self.add_operation_history("保存顺序表到文件")

    def load_sequence(self):
        default_dir = self._ensure_sequence_folder()
        filepath = filedialog.askopenfilename(
            initialdir=default_dir,
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="从文件加载顺序表"
        )
        if not filepath:
            return
        with open(filepath, "r", encoding="utf-8") as f:
            loaded = json.load(f)
        data_list = loaded.get("data",[])
        self.model.data = list(data_list)
        # 保证容量至少能呈现当前数据（若外部文件里的元素超出当前容量）
        self._ensure_capacity_for(len(self.model.data))
        self.update_display()
        messagebox.showinfo("成功", f"已加载 {len(data_list)} 个元素到顺序表")
        self.add_operation_history(f"从文件加载顺序表，包含 {len(data_list)} 个元素")

    def prepare_build_list(self):
        self.build_values_entry = StringVar()
        input_frame = Frame(self.window, bg="lightgreen")
        input_frame.place(x=400, y=600, width=600, height=80)
        value_label = Label(input_frame, text="输入多个值(用逗号分隔):", font=("Arial", 12), bg="lightgreen")
        value_label.grid(row=0, column=0, padx=5, pady=5)
        value_entry = Entry(input_frame, textvariable=self.build_values_entry, font=("Arial", 12), width=30)
        value_entry.grid(row=0, column=1, padx=5, pady=5)
        confirm_btn = Button(input_frame, text="确认构建", font=("Arial", 12),
                           command=self.perform_build_list)
        confirm_btn.grid(row=0, column=2, padx=5, pady=5)
        value_entry.focus()

    def perform_build_list(self):
        values_str = self.build_values_entry.get()
        if not values_str:
            messagebox.showerror("错误", "请输入要构建的值")
            return

        try:
            values = [v.strip() for v in values_str.split(',') if v.strip()]
            if not values:
                messagebox.showerror("错误", "请输入有效的值")
                return

            # 清空当前顺序表
            self.model.clear()
            self.update_display()

            # 逐个添加值并展示动画
            self.disable_buttons()

            for i, value in enumerate(values):
                # 在添加前确保容量（模型负责扩容）
                self._ensure_capacity_for(len(self.model.data) + 1)
                # 添加到模型（模型自己也会再检验一次）
                self.model.append(value)

                # 创建新元素的动画
                self.animate_build_element(i, value)

                # 短暂暂停，让用户能看到过程
                self.window.update()
                time.sleep(0.3)

            self.enable_buttons()
            self.add_operation_history(f"构建顺序表: {', '.join(values)}")

        except Exception as e:
            messagebox.showerror("错误", f"构建顺序表时出错: {str(e)}")
            self.enable_buttons()

    def animate_build_element(self, index, value):
        """动画展示构建顺序表元素的过程"""
        # 获取多语言伪代码
        pseudo_lines = get_append_pseudocode(self.current_code_language, index, value)
        
        # 保存操作上下文
        self.current_operation_context = {
            'type': 'append',
            'index': index,
            'value': value,
            'title': f"构建操作: 添加元素 '{value}'",
            'highlight_line': 0
        }
        
        self.set_pseudo_code(f"构建操作: 添加元素 '{value}'", pseudo_lines)
        
        # 步骤1: 检查容量
        self.highlight_pseudo_line(0)
        self.highlight_pseudo_line(1)
        self.highlight_pseudo_line(2)

        # 创建新元素（初始位置在右侧）
        new_x = self.start_x + (len(self.data_store) - 1) * (self.cell_width + self.spacing) + 200
        new_y = self.start_y

        new_rect = self.canvas.create_rectangle(new_x, new_y, new_x + self.cell_width,
                                              new_y + self.cell_height, fill="lightgreen", outline="black")
        new_label = self.canvas.create_text(new_x + self.cell_width/2, new_y + self.cell_height/2,
                                          text=value, font=("Arial", 14, "bold"))

        # 将新元素提升到最上层
        self.canvas.tag_raise(new_rect)
        self.canvas.tag_raise(new_label)

        # 步骤2: 添加到末尾
        self.highlight_pseudo_line(3, delay=False)

        # 移动新元素到正确位置
        target_x = self.start_x + index * (self.cell_width + self.spacing)

        # 移动新元素
        dx = (target_x - new_x) / 20
        for i in range(20):
            self.canvas.move(new_rect, dx, 0)
            self.canvas.move(new_label, dx, 0)
            # 移动过程中持续确保新元素在最上层
            self.canvas.tag_raise(new_rect)
            self.canvas.tag_raise(new_label)
            self.window.update()
            time.sleep(self.animation_speed)

        # 步骤3: 长度加1
        self.highlight_pseudo_line(4)

        # 更新显示
        self.update_display()
        
        # 步骤4: 完成
        self.highlight_pseudo_line(5)
        self.complete_pseudo_code()

    def disable_buttons(self):
        """禁用所有按钮"""
        for btn in self.buttons:
            btn.config(state=DISABLED)

    def enable_buttons(self):
        """启用所有按钮"""
        for btn in self.buttons:
            btn.config(state=NORMAL)

    def prepare_insert(self, position):
        self.value_entry.set("")

        input_frame = Frame(self.window, bg="lightgreen")
        input_frame.place(x=500, y=600, width=400, height=80)

        value_label = Label(input_frame, text="输入值:", font=("Arial", 12), bg="lightgreen")
        value_label.grid(row=0, column=0, padx=5, pady=5)

        value_entry = Entry(input_frame, textvariable=self.value_entry, font=("Arial", 12))
        value_entry.grid(row=0, column=1, padx=5, pady=5)

        confirm_btn = Button(input_frame, text="确认", font=("Arial", 12),
                           command=lambda: self.perform_insert(position))
        confirm_btn.grid(row=0, column=2, padx=5, pady=5)

        value_entry.focus()

    def prepare_insert_with_position(self):
        self.value_entry.set("")
        self.position_entry.set("")

        input_frame = Frame(self.window, bg="lightgreen")
        input_frame.place(x=400, y=600, width=600, height=80)

        value_label = Label(input_frame, text="输入值:", font=("Arial", 12), bg="lightgreen")
        value_label.grid(row=0, column=0, padx=5, pady=5)

        value_entry = Entry(input_frame, textvariable=self.value_entry, font=("Arial", 12), width=10)
        value_entry.grid(row=0, column=1, padx=5, pady=5)

        pos_label = Label(input_frame, text="位置(1-based):", font=("Arial", 12), bg="lightgreen")
        pos_label.grid(row=0, column=2, padx=5, pady=5)

        pos_entry = Entry(input_frame, textvariable=self.position_entry, font=("Arial", 12), width=10)
        pos_entry.grid(row=0, column=3, padx=5, pady=5)

        confirm_btn = Button(input_frame, text="确认", font=("Arial", 12),
                           command=self.perform_insert_with_position)
        confirm_btn.grid(row=0, column=4, padx=5, pady=5)

        value_entry.focus()

    def perform_insert(self, position):
        value = self.value_entry.get()
        if not value:
            messagebox.showerror("错误", "请输入一个值")
            return
        # 确保容量
        self._ensure_capacity_for(len(self.model.data) + 1)
        if position == 0:
            self.model.insert_first(value)
        elif position == len(self.data_store):
            self.model.insert_last(value)

        self.animate_insert(position, value)
        self.add_operation_history(f"插入元素 '{value}' 到位置 {position}")

    def perform_insert_with_position(self):
        value = self.value_entry.get()
        position_str = self.position_entry.get()
        if not value or not position_str:
            messagebox.showerror("错误", "请填写所有字段")
            return
        try:
            position = int(position_str)  # 用户输入是 1-based
        except ValueError:
            messagebox.showerror("错误", "位置必须是整数")
            return

        # 允许插入到末尾，所以最大为 len + 1
        if position < 1 or position > len(self.data_store) + 1:
            messagebox.showerror("错误", f"位置必须在1到{len(self.data_store) + 1}之间")
            return

        insert_idx = position - 1  # 转为 0-based
        try:
            # 扩容检查
            self._ensure_capacity_for(len(self.model.data) + 1)
            self.model.insert(insert_idx, value)
        except Exception as e:
            messagebox.showerror("错误", f"插入失败: {e}")
            return
        try:
            self.animate_insert(insert_idx, value)
            self.add_operation_history(f"插入元素 '{value}' 到位置 {position}")
        except Exception as e:
            messagebox.showerror("错误", f"插入动画失败: {e}")
            try:
                self.update_display()
            except Exception:
                pass

    def animate_insert(self, position, value):
        self.disable_buttons()

        # 获取多语言伪代码
        n = len(self.data_store) - 1  # 插入前的长度
        pseudo_lines = get_insert_pseudocode(self.current_code_language, position, value, n)
        
        # 保存操作上下文
        self.current_operation_context = {
            'type': 'insert',
            'position': position,
            'value': value,
            'length': n,
            'title': f"插入操作: 在位置 {position} 插入 '{value}'",
            'highlight_line': 0
        }
        
        self.set_pseudo_code(f"插入操作: 在位置 {position} 插入 '{value}'", pseudo_lines)
        
        # 步骤1: 检查容量
        self.highlight_pseudo_line(0)
        self.highlight_pseudo_line(1)
        self.highlight_pseudo_line(2)

        # 当前画布上已有的矩形数（插入前）
        old_count = len(self.data_rectangles)

        # 新元素起始在右侧（画布外/右侧）
        new_x = self.start_x + max(0, len(self.data_store) - 1) * (self.cell_width + self.spacing) + 200
        new_y = self.start_y
        new_rect = self.canvas.create_rectangle(new_x, new_y, new_x + self.cell_width,
                                                new_y + self.cell_height, fill="lightgreen", outline="black")
        new_label = self.canvas.create_text(new_x + self.cell_width / 2, new_y + self.cell_height / 2,
                                            text=value, font=("Arial", 14, "bold"))

        # 关键修改：在移动前将移动的元素提升到最上层
        for idx in range(old_count - 1, position - 1, -1):
            # 将当前要移动的元素提升到画布最上层
            self.canvas.tag_raise(self.data_rectangles[idx])
            self.canvas.tag_raise(self.data_labels[idx])
            self.canvas.tag_raise(self.index_labels[idx])

        # 步骤2: 从后向前逐个把已有元素向右移动一格
        self.highlight_pseudo_line(3)
        
        total_dx = self.cell_width + self.spacing
        steps = 12
        step_dx = total_dx / steps
        
        # 高亮显示需要移动的元素
        for idx in range(old_count - 1, position - 1, -1):
            # 每次移动元素时高亮对应的伪代码行
            self.highlight_pseudo_line(4, delay=False)
            
            original_color = self.highlight_element(idx, "orange")
            
            for _ in range(steps):
                try:
                    self.canvas.move(self.data_rectangles[idx], step_dx, 0)
                    self.canvas.move(self.data_labels[idx], step_dx, 0)
                    self.canvas.move(self.index_labels[idx], step_dx, 0)
                    # 关键：在每次移动后都确保元素在最上层
                    self.canvas.tag_raise(self.data_rectangles[idx])
                    self.canvas.tag_raise(self.data_labels[idx])
                    self.canvas.tag_raise(self.index_labels[idx])
                    self.window.update()
                    time.sleep(self.animation_speed)
                except Exception:
                    pass
                
            # 恢复元素颜色
            self.restore_element_color(idx, original_color)

        # 步骤3: 插入新元素
        self.highlight_pseudo_line(5)
        
        # 将新元素也提升到最上层
        self.canvas.tag_raise(new_rect)
        self.canvas.tag_raise(new_label)

        # 新元素从右侧滑入到指定位置
        target_x = self.start_x + position * (self.cell_width + self.spacing)
        dx = (target_x - new_x) / 20.0
        for _ in range(20):
            self.canvas.move(new_rect, dx, 0)
            self.canvas.move(new_label, dx, 0)
            # 移动过程中持续确保新元素在最上层
            self.canvas.tag_raise(new_rect)
            self.canvas.tag_raise(new_label)
            self.window.update()
            time.sleep(self.animation_speed)

        # 步骤4: 长度加1
        self.highlight_pseudo_line(6)
        
        # 最后刷新显示以保证数据结构与画布一致
        self.update_display()
        
        # 步骤5: 完成
        self.highlight_pseudo_line(7)
        self.complete_pseudo_code()
        
        # 清除画布上的步骤说明（如果有的话）
        if self.step_text_id:
            self.canvas.delete(self.step_text_id)
            self.step_text_id = None
        for code_id in self.pseudo_code_ids:
            self.canvas.delete(code_id)
        self.pseudo_code_ids = []
            
        self.enable_buttons()

    def delete_first(self):
        if len(self.data_store) == 0:
            messagebox.showerror("错误", "顺序表为空")
            return
        self.animate_delete(0)
        self.add_operation_history("删除第一个元素")

    def delete_last(self):
        if len(self.data_store) == 0:
            messagebox.showerror("错误", "顺序表为空")
            return
        self.animate_delete(len(self.data_store) - 1)
        self.add_operation_history("删除最后一个元素")

    def prepare_delete_with_position(self):
        self.position_entry.set("")
        input_frame = Frame(self.window, bg="lightgreen")
        input_frame.place(x=500, y=600, width=400, height=80)
        pos_label = Label(input_frame, text="位置(1-based):", font=("Arial", 12), bg="lightgreen")
        pos_label.grid(row=0, column=0, padx=5, pady=5)
        pos_entry = Entry(input_frame, textvariable=self.position_entry, font=("Arial", 12))
        pos_entry.grid(row=0, column=1, padx=5, pady=5)
        confirm_btn = Button(input_frame, text="确认", font=("Arial", 12),
                           command=self.perform_delete_with_position)
        confirm_btn.grid(row=0, column=2, padx=5, pady=5)
        pos_entry.focus()

    def perform_delete_with_position(self):
        position_str = self.position_entry.get()
        if not position_str:
            messagebox.showerror("错误", "请输入位置")
            return
        try:
            position = int(position_str)
            if position < 1 or position > len(self.data_store):
                messagebox.showerror("错误", f"位置必须在1到{len(self.data_store)}之间")
                return
            self.animate_delete(position - 1)
            self.add_operation_history(f"删除位置 {position} 的元素")
        except ValueError:
            messagebox.showerror("错误", "位置必须是整数")

    def animate_delete(self, position):
        # 禁用所有按钮
        self.disable_buttons()
        
        # 获取要删除的元素值
        deleted_value = self.data_store[position] if position < len(self.data_store) else "?"
        n = len(self.data_store)
        
        # 获取多语言伪代码
        pseudo_lines = get_delete_pseudocode(self.current_code_language, position, n)
        
        # 保存操作上下文
        self.current_operation_context = {
            'type': 'delete',
            'position': position,
            'length': n,
            'title': f"删除操作: 删除位置 {position} 的元素",
            'highlight_line': 0
        }
        
        self.set_pseudo_code(f"删除操作: 删除位置 {position} 的元素", pseudo_lines)
        
        # 步骤1: 检查位置有效性
        self.highlight_pseudo_line(0)
        self.highlight_pseudo_line(1)
        self.highlight_pseudo_line(2)
        
        # 步骤2: 保存被删除元素
        self.highlight_pseudo_line(3)
        
        # 高亮要删除的元素
        self.canvas.itemconfig(self.data_rectangles[position], fill="red")
        self.window.update()
        time.sleep(0.5)
        
        # 步骤3: 移动后面的元素向前
        self.highlight_pseudo_line(4)
        
        for i in range(position + 1, len(self.data_store)):
            # 每次移动元素时高亮对应的伪代码行
            self.highlight_pseudo_line(5, delay=False)
            
            # 高亮当前正在移动的元素
            original_color = self.highlight_element(i, "orange")
            
            dx = -(self.cell_width + self.spacing) / 10
            for j in range(10):
                self.canvas.move(self.data_rectangles[i], dx, 0)
                self.canvas.move(self.data_labels[i], dx, 0)
                self.canvas.move(self.index_labels[i], dx, 0)
                # 确保移动的元素在最上层
                self.canvas.tag_raise(self.data_rectangles[i])
                self.canvas.tag_raise(self.data_labels[i])
                self.canvas.tag_raise(self.index_labels[i])
                self.window.update()
                time.sleep(self.animation_speed)
                
            # 恢复元素颜色
            self.restore_element_color(i, original_color)
        
        # 步骤4: 长度减1
        self.highlight_pseudo_line(6)
            
        # 删除模型中的元素
        self.model.pop(position)
        
        # 更新显示
        self.update_display()
        
        # 步骤5: 返回被删除的元素
        self.highlight_pseudo_line(7)
        self.complete_pseudo_code()
        
        # 清除画布上的步骤说明（如果有的话）
        if self.step_text_id:
            self.canvas.delete(self.step_text_id)
            self.step_text_id = None
        for code_id in self.pseudo_code_ids:
            self.canvas.delete(code_id)
        self.pseudo_code_ids = []
            
        # 启用所有按钮
        self.enable_buttons()

    def clear_list(self):
        if len(self.data_store) == 0:
            messagebox.showinfo("信息", "顺序表已为空")
            return
        self.disable_buttons()
        
        n = len(self.data_store)
        
        # 获取多语言伪代码
        pseudo_lines = get_clear_pseudocode_seq(self.current_code_language, n)
        
        # 保存操作上下文
        self.current_operation_context = {
            'type': 'clear',
            'count': n,
            'title': f"清空操作: 移除所有 {n} 个元素",
            'highlight_line': 0
        }
        
        self.set_pseudo_code(f"清空操作: 移除所有 {n} 个元素", pseudo_lines)
        
        # 步骤1: 开始清空
        self.highlight_pseudo_line(0)
        self.highlight_pseudo_line(1)
        
        for i in range(len(self.data_store)):
            # 每次移除元素时高亮对应的伪代码行
            self.highlight_pseudo_line(2, delay=False)
            
            dx = 20
            for j in range(15):
                self.canvas.move(self.data_rectangles[i], dx, 0)
                self.canvas.move(self.data_labels[i], dx, 0)
                self.canvas.move(self.index_labels[i], dx, 0)
                # 确保移动的元素在最上层
                self.canvas.tag_raise(self.data_rectangles[i])
                self.canvas.tag_raise(self.data_labels[i])
                self.canvas.tag_raise(self.index_labels[i])
                self.window.update()
                time.sleep(self.animation_speed)
        
        # 步骤2: 重置长度
        self.highlight_pseudo_line(3)
        
        self.model.clear()
        self.update_display()
        
        # 步骤3: 完成
        self.highlight_pseudo_line(4)
        self.complete_pseudo_code()
        
        # 清除画布上的步骤说明（如果有的话）
        if self.step_text_id:
            self.canvas.delete(self.step_text_id)
            self.step_text_id = None
            
        self.enable_buttons()
        self.add_operation_history("清空顺序表")

    def process_dsl(self, event=None):
        txt = (self.dsl_var.get() or "").strip()
        from DSL_utils import process_command
        try:
            process_command(self, txt)
        finally:
            self.dsl_var.set("")

    def update_display(self):
        # 清除画布上的所有元素
        self.canvas.delete("all")
        self.data_rectangles.clear()
        self.data_labels.clear()
        self.index_labels.clear()
        # 预计算整个容量所需宽度，并设置画布滚动区域
        total_slots = max(self.model.capacity, len(self.data_store))
        total_width = self.start_x + total_slots * (self.cell_width + self.spacing) + self.start_x
        total_height = max(self.start_y + self.cell_height + 80, 450)
        try:
            self.canvas.config(scrollregion=(0, 0, total_width, total_height))
        except Exception:
            pass

        # 先绘制空槽（底层）
        for i in range(total_slots):
            x = self.start_x + i * (self.cell_width + self.spacing)
            y = self.start_y
            if i >= len(self.data_store):
                # 空槽——使用浅灰色边框
                rect = self.canvas.create_rectangle(x, y, x + self.cell_width, y + self.cell_height,
                                                   fill="#FAF9F6", outline="#D1D5DB", width=1)
                # 给空槽设置较低的层级
                self.canvas.tag_lower(rect)

        # 再绘制数据元素（上层）
        for i in range(len(self.data_store)):
            x = self.start_x + i * (self.cell_width + self.spacing)
            y = self.start_y
            # 已占用槽
            rect = self.canvas.create_rectangle(x, y, x + self.cell_width, y + self.cell_height,
                                               fill="lightblue", outline="black", width=2)
            label = self.canvas.create_text(x + self.cell_width/2, y + self.cell_height/2,
                                            text=str(self.data_store[i]), font=("Arial", 14, "bold"))
            self.data_rectangles.append(rect)
            self.data_labels.append(label)
            
            # 索引文本（0-based）
            index_label = self.canvas.create_text(x + self.cell_width/2, y + self.cell_height + 15,
                                                text=str(i), font=("Arial", 12))
            self.index_labels.append(index_label)

        # 绘制表结构说明（放在左上角，避免与步骤说明重叠）
        info_text = f"顺序表长度: {len(self.data_store)}  容量: {self.model.capacity}"
        self.canvas.create_text(100, 50, text=info_text, font=("Arial", 14), anchor="w")

    def back_to_main(self):
        # 返回主界面
        self.window.destroy()

    # ==================== 冒泡排序可视化（教学版） ====================
    
    def start_bubble_sort(self):
        """启动冒泡排序可视化 - 教学版"""
        if len(self.data_store) < 2:
            messagebox.showinfo("提示", "顺序表元素少于2个，无需排序")
            return
        
        # 检查是否所有元素都是数字
        try:
            numeric_data = [float(x) for x in self.data_store]
        except ValueError:
            messagebox.showerror("错误", "冒泡排序需要数值类型的元素")
            return
        
        self.disable_buttons()
        self.animate_bubble_sort_teaching()
        self.enable_buttons()
    
    def animate_bubble_sort_teaching(self):
        """冒泡排序教学演示 - 详细步骤说明版"""
        # 获取数值数据
        try:
            data = [float(x) for x in self.data_store]
        except ValueError:
            messagebox.showerror("错误", "数据必须为数值类型")
            return
        
        n = len(data)
        original_data = data.copy()
        
        # 设置教学伪代码
        pseudo_lines = [
            "【冒泡排序原理】",
            "重复地走访要排序的数列",
            "一次比较两个相邻元素",
            "如果顺序错误就交换位置",
            "直到没有需要交换的元素",
            "─────────────────",
            f"for i = 0 to {n-2}:  // 外层循环{n-1}轮",
            f"  for j = 0 to n-1-i:  // 内层遍历",
            "    比较 data[j] 和 data[j+1]",
            "    if data[j] > data[j+1]:",
            "      交换两个元素",
            "  // 本轮最大值已到末尾 ✓"
        ]
        self.set_pseudo_code("🎓 冒泡排序教学演示", pseudo_lines)
        
        # 清空画布
        self.canvas.delete("all")
        
        # ===== 布局参数 =====
        canvas_width = 1000
        canvas_height = 380
        
        # 条形图区域（左侧）
        bar_area_left = 50
        bar_area_right = 650
        bar_area_top = 100
        bar_area_bottom = 320
        
        # 教学说明区域（右侧）
        info_area_left = 670
        info_area_top = 60
        
        # 计算条形参数
        bar_area_width = bar_area_right - bar_area_left
        bar_width = max(30, min(55, (bar_area_width - 20) // n - 8))
        total_bars_width = n * bar_width + (n - 1) * 8
        bar_start_x = bar_area_left + (bar_area_width - total_bars_width) // 2
        
        # 数值范围
        max_val = max(data)
        min_val = min(data)
        value_range = max_val - min_val if max_val != min_val else 1
        bar_max_height = bar_area_bottom - bar_area_top - 50
        
        def get_bar_height(value):
            """计算条形高度"""
            if value_range == 0:
                return bar_max_height // 2
            normalized = (value - min_val) / value_range
            return max(30, int(normalized * bar_max_height * 0.85 + bar_max_height * 0.15))
        
        def get_bar_x(index):
            """获取条形的X坐标"""
            return bar_start_x + index * (bar_width + 8)
        
        def draw_full_scene(arr, round_num=0, compare_j=-1, action="", 
                           swap_highlight=False, sorted_set=None, show_arrow=False,
                           compare_result="", stats=None):
            """绘制完整场景"""
            self.canvas.delete("scene")
            sorted_set = sorted_set or set()
            stats = stats or {"compare": 0, "swap": 0}
            
            # ===== 标题 =====
            self.canvas.create_text(canvas_width // 2 - 100, 25,
                                   text="🎓 冒泡排序 · 教学演示",
                                   font=("微软雅黑", 18, "bold"), fill="#2c3e50",
                                   tags="scene")
            
            # ===== 颜色图例 =====
            legend_y = 55
            legend_items = [
                ("🔵 未排序", "#3498db"),
                ("🟡 正在比较", "#f39c12"),
                ("🔴 正在交换", "#e74c3c"),
                ("🟢 已排序", "#27ae60")
            ]
            legend_x = 60
            for text, color in legend_items:
                self.canvas.create_rectangle(legend_x, legend_y - 8, legend_x + 16, legend_y + 8,
                                            fill=color, outline="", tags="scene")
                self.canvas.create_text(legend_x + 22, legend_y, text=text,
                                       font=("微软雅黑", 9), fill="#2c3e50", 
                                       anchor="w", tags="scene")
                legend_x += 120
            
            # ===== 绘制条形图 =====
            for i, value in enumerate(arr):
                x = get_bar_x(i)
                bar_height = get_bar_height(value)
                y_bottom = bar_area_bottom
                y_top = y_bottom - bar_height
                
                # 确定颜色和状态
                if swap_highlight and i in [compare_j, compare_j + 1]:
                    color = "#e74c3c"  # 红色 - 交换中
                    outline = "#c0392b"
                    width = 3
                elif compare_j >= 0 and i in [compare_j, compare_j + 1]:
                    color = "#f39c12"  # 橙色 - 比较中
                    outline = "#d35400"
                    width = 3
                elif i in sorted_set:
                    color = "#27ae60"  # 绿色 - 已排序
                    outline = "#1e8449"
                    width = 2
                else:
                    color = "#3498db"  # 蓝色 - 未排序
                    outline = "#2980b9"
                    width = 2
                
                # 绘制条形（带阴影效果）
                shadow_offset = 3
                self.canvas.create_rectangle(x + shadow_offset, y_top + shadow_offset, 
                                            x + bar_width + shadow_offset, y_bottom + shadow_offset,
                                            fill="#bdc3c7", outline="", tags="scene")
                
                self.canvas.create_rectangle(x, y_top, x + bar_width, y_bottom,
                                            fill=color, outline=outline, width=width,
                                            tags="scene")
                
                # 条形内数值（大字）
                self.canvas.create_text(x + bar_width // 2, (y_top + y_bottom) // 2,
                                       text=f"{int(value)}",
                                       font=("Arial", 14, "bold"), fill="white",
                                       tags="scene")
                
                # 索引标签
                self.canvas.create_text(x + bar_width // 2, y_bottom + 18,
                                       text=f"[{i}]",
                                       font=("Arial", 10), fill="#7f8c8d",
                                       tags="scene")
            
            # ===== 比较箭头和符号 =====
            if show_arrow and compare_j >= 0 and compare_j < len(arr) - 1:
                x1 = get_bar_x(compare_j) + bar_width // 2
                x2 = get_bar_x(compare_j + 1) + bar_width // 2
                arrow_y = bar_area_top - 25
                
                # 绘制双向箭头框
                self.canvas.create_line(x1, arrow_y, x2, arrow_y,
                                       fill="#e74c3c", width=3, arrow="both",
                                       tags="scene")
                
                # 比较符号
                mid_x = (x1 + x2) // 2
                if compare_result:
                    # 绘制比较结果背景圆
                    self.canvas.create_oval(mid_x - 18, arrow_y - 35, mid_x + 18, arrow_y - 5,
                                           fill="#fff3cd" if ">" in compare_result else "#d4edda",
                                           outline="#ffc107" if ">" in compare_result else "#28a745",
                                           width=2, tags="scene")
                    self.canvas.create_text(mid_x, arrow_y - 20, text=compare_result,
                                           font=("Arial", 14, "bold"), 
                                           fill="#d35400" if ">" in compare_result else "#27ae60",
                                           tags="scene")
            
            # ===== 右侧教学信息面板 =====
            panel_x = info_area_left
            panel_y = info_area_top
            
            # 面板背景
            self.canvas.create_rectangle(panel_x, panel_y, canvas_width - 20, 360,
                                        fill="#f8f9fa", outline="#dee2e6", width=2,
                                        tags="scene")
            
            # 当前状态标题
            self.canvas.create_text(panel_x + 15, panel_y + 20, text="📌 当前状态",
                                   font=("微软雅黑", 12, "bold"), fill="#2c3e50",
                                   anchor="w", tags="scene")
            
            # 轮次信息
            self.canvas.create_text(panel_x + 15, panel_y + 50,
                                   text=f"第 {round_num + 1} 轮 / 共 {n - 1} 轮",
                                   font=("微软雅黑", 11), fill="#6c757d",
                                   anchor="w", tags="scene")
            
            # 分隔线
            self.canvas.create_line(panel_x + 10, panel_y + 70, canvas_width - 30, panel_y + 70,
                                   fill="#dee2e6", tags="scene")
            
            # 操作说明（大字醒目）
            self.canvas.create_text(panel_x + 15, panel_y + 95, text="💡 操作说明",
                                   font=("微软雅黑", 11, "bold"), fill="#2c3e50",
                                   anchor="w", tags="scene")
            
            # 当前操作（多行显示）
            action_lines = action.split("\n") if action else ["等待开始..."]
            action_y = panel_y + 120
            for line in action_lines[:4]:  # 最多显示4行
                self.canvas.create_text(panel_x + 15, action_y, text=line,
                                       font=("微软雅黑", 10), fill="#495057",
                                       anchor="w", width=280, tags="scene")
                action_y += 22
            
            # 分隔线
            self.canvas.create_line(panel_x + 10, panel_y + 195, canvas_width - 30, panel_y + 195,
                                   fill="#dee2e6", tags="scene")
            
            # 统计信息
            self.canvas.create_text(panel_x + 15, panel_y + 215, text="📊 统计数据",
                                   font=("微软雅黑", 11, "bold"), fill="#2c3e50",
                                   anchor="w", tags="scene")
            
            self.canvas.create_text(panel_x + 15, panel_y + 242,
                                   text=f"比较次数：{stats['compare']}",
                                   font=("微软雅黑", 10), fill="#17a2b8",
                                   anchor="w", tags="scene")
            
            self.canvas.create_text(panel_x + 150, panel_y + 242,
                                   text=f"交换次数：{stats['swap']}",
                                   font=("微软雅黑", 10), fill="#dc3545",
                                   anchor="w", tags="scene")
            
            # 原始数组 vs 当前数组
            self.canvas.create_text(panel_x + 15, panel_y + 272,
                                   text=f"原始：{[int(x) for x in original_data]}",
                                   font=("Consolas", 9), fill="#6c757d",
                                   anchor="w", tags="scene")
            self.canvas.create_text(panel_x + 15, panel_y + 292,
                                   text=f"当前：{[int(x) for x in arr]}",
                                   font=("Consolas", 9), fill="#28a745",
                                   anchor="w", tags="scene")
            
            self.window.update()
        
        def animate_swap(arr, j, sorted_set, stats):
            """执行交换动画 - 元素上升、移动、下降"""
            x1 = get_bar_x(j)
            x2 = get_bar_x(j + 1)
            
            # 阶段1: 两个元素同时上升
            for step in range(8):
                self.canvas.delete("swap_anim")
                offset_y = step * 8
                
                for idx, jj in enumerate([j, j + 1]):
                    x = get_bar_x(jj)
                    bar_height = get_bar_height(arr[jj])
                    y_bottom = bar_area_bottom - offset_y
                    y_top = y_bottom - bar_height
                    
                    self.canvas.create_rectangle(x, y_top, x + bar_width, y_bottom,
                                                fill="#e74c3c", outline="#c0392b", width=3,
                                                tags="swap_anim")
                    self.canvas.create_text(x + bar_width // 2, (y_top + y_bottom) // 2,
                                           text=f"{int(arr[jj])}",
                                           font=("Arial", 14, "bold"), fill="white",
                                           tags="swap_anim")
                
                self.window.update()
                time.sleep(0.03)
            
            # 阶段2: 水平交叉移动
            distance = bar_width + 8
            for step in range(12):
                self.canvas.delete("swap_anim")
                progress = step / 11
                offset_x1 = progress * distance
                offset_x2 = -progress * distance
                
                # 左边元素向右移
                x = x1 + offset_x1
                bar_height = get_bar_height(arr[j])
                y_bottom = bar_area_bottom - 64
                y_top = y_bottom - bar_height
                self.canvas.create_rectangle(x, y_top, x + bar_width, y_bottom,
                                            fill="#e74c3c", outline="#c0392b", width=3,
                                            tags="swap_anim")
                self.canvas.create_text(x + bar_width // 2, (y_top + y_bottom) // 2,
                                       text=f"{int(arr[j])}",
                                       font=("Arial", 14, "bold"), fill="white",
                                       tags="swap_anim")
                
                # 右边元素向左移
                x = x2 + offset_x2
                bar_height = get_bar_height(arr[j + 1])
                y_bottom = bar_area_bottom - 64
                y_top = y_bottom - bar_height
                self.canvas.create_rectangle(x, y_top, x + bar_width, y_bottom,
                                            fill="#e74c3c", outline="#c0392b", width=3,
                                            tags="swap_anim")
                self.canvas.create_text(x + bar_width // 2, (y_top + y_bottom) // 2,
                                       text=f"{int(arr[j + 1])}",
                                       font=("Arial", 14, "bold"), fill="white",
                                       tags="swap_anim")
                
                self.window.update()
                time.sleep(0.03)
            
            # 执行实际交换
            arr[j], arr[j + 1] = arr[j + 1], arr[j]
            
            # 阶段3: 下降回位
            for step in range(8):
                self.canvas.delete("swap_anim")
                offset_y = 64 - step * 8
                
                for jj in [j, j + 1]:
                    x = get_bar_x(jj)
                    bar_height = get_bar_height(arr[jj])
                    y_bottom = bar_area_bottom - offset_y
                    y_top = y_bottom - bar_height
                    
                    self.canvas.create_rectangle(x, y_top, x + bar_width, y_bottom,
                                                fill="#e74c3c", outline="#c0392b", width=3,
                                                tags="swap_anim")
                    self.canvas.create_text(x + bar_width // 2, (y_top + y_bottom) // 2,
                                           text=f"{int(arr[jj])}",
                                           font=("Arial", 14, "bold"), fill="white",
                                           tags="swap_anim")
                
                self.window.update()
                time.sleep(0.03)
            
            self.canvas.delete("swap_anim")
        
        # ===== 开始教学演示 =====
        stats = {"compare": 0, "swap": 0}
        sorted_set = set()
        
        # 第0步：介绍
        self.highlight_pseudo_line(0)
        draw_full_scene(data, round_num=0, action="🎬 冒泡排序开始！\n\n核心思想：\n相邻元素两两比较\n大的元素逐渐\"冒泡\"到末尾", stats=stats)
        time.sleep(1.5)
        
        self.highlight_pseudo_line(1)
        draw_full_scene(data, round_num=0, action="📖 算法原理：\n每一轮从头开始\n依次比较相邻两个元素\n如果前面的比后面的大\n就交换它们的位置", stats=stats)
        time.sleep(1.5)
        
        # 主循环
        for i in range(n - 1):
            # 本轮开始
            self.highlight_pseudo_line(6)
            draw_full_scene(data, round_num=i, sorted_set=sorted_set,
                           action=f"🔄 开始第 {i + 1} 轮\n\n本轮需要比较 {n - 1 - i} 对相邻元素\n找出未排序部分的最大值",
                           stats=stats)
            time.sleep(1.0)
            
            swapped_this_round = False
            
            for j in range(n - 1 - i):
                stats["compare"] += 1
                
                # 显示当前比较的两个元素
                self.highlight_pseudo_line(7)
                self.highlight_pseudo_line(8)
                draw_full_scene(data, round_num=i, compare_j=j, sorted_set=sorted_set,
                               show_arrow=True,
                               action=f"👀 比较第 {j+1} 对\n\ndata[{j}] = {int(data[j])}\ndata[{j+1}] = {int(data[j+1])}\n\n判断：{int(data[j])} 和 {int(data[j+1])} 谁大？",
                               stats=stats)
                time.sleep(0.8)
                
                # 显示比较结果
                if data[j] > data[j + 1]:
                    compare_result = ">"
                    self.highlight_pseudo_line(9)
                    self.highlight_pseudo_line(10)
                    draw_full_scene(data, round_num=i, compare_j=j, sorted_set=sorted_set,
                                   show_arrow=True, compare_result=compare_result,
                                   action=f"⚠️ 顺序错误！\n\n{int(data[j])} > {int(data[j+1])}\n左边比右边大\n需要交换位置！",
                                   stats=stats)
                    time.sleep(0.8)
                    
                    # 执行交换动画
                    draw_full_scene(data, round_num=i, compare_j=j, sorted_set=sorted_set,
                                   swap_highlight=True,
                                   action=f"🔀 执行交换\n\n{int(data[j])} ⟷ {int(data[j+1])}\n两个元素互换位置",
                                   stats=stats)
                    time.sleep(0.3)
                    
                    animate_swap(data, j, sorted_set, stats)
                    stats["swap"] += 1
                    swapped_this_round = True
                    
                    # 交换完成
                    draw_full_scene(data, round_num=i, compare_j=j, sorted_set=sorted_set,
                                   action=f"✅ 交换完成！\n\n现在 data[{j}] = {int(data[j])}\n     data[{j+1}] = {int(data[j+1])}\n顺序正确了",
                                   stats=stats)
                    time.sleep(0.6)
                else:
                    compare_result = "≤"
                    draw_full_scene(data, round_num=i, compare_j=j, sorted_set=sorted_set,
                                   show_arrow=True, compare_result=compare_result,
                                   action=f"✓ 顺序正确\n\n{int(data[j])} ≤ {int(data[j+1])}\n左边不大于右边\n无需交换，继续下一对",
                                   stats=stats)
                    time.sleep(0.6)
            
            # 本轮结束，最大值已到末尾
            sorted_set.add(n - 1 - i)
            self.highlight_pseudo_line(11)
            draw_full_scene(data, round_num=i, sorted_set=sorted_set,
                           action=f"🎉 第 {i + 1} 轮完成！\n\n最大值 {int(data[n - 1 - i])} \n已\"冒泡\"到位置 [{n - 1 - i}]\n\n该位置已排序完成 ✓",
                           stats=stats)
            time.sleep(1.0)
            
            # 优化：如果本轮没有交换，说明已排序完成
            if not swapped_this_round:
                draw_full_scene(data, round_num=i, sorted_set=sorted_set,
                               action=f"🚀 优化检测！\n\n本轮没有发生任何交换\n说明数组已经有序\n可以提前结束排序！",
                               stats=stats)
                time.sleep(1.2)
                break
        
        # 排序完成
        sorted_set = set(range(n))
        draw_full_scene(data, round_num=n-1, sorted_set=sorted_set,
                       action=f"🏆 排序完成！\n\n总共比较了 {stats['compare']} 次\n总共交换了 {stats['swap']} 次\n\n数组已完全有序！",
                       stats=stats)
        
        self.complete_pseudo_code()
        
        # 更新模型数据
        self.model.data = [str(int(x)) if x == int(x) else str(x) for x in data]
        
        # 添加操作历史
        self.add_operation_history(f"冒泡排序完成: 比较{stats['compare']}次, 交换{stats['swap']}次")
        
        # 最终总结 - 精美版
        time.sleep(1.5)
        self.canvas.delete("scene")
        self._draw_beautiful_summary(original_data, data, stats, n)
        
        # 等待用户查看总结
        time.sleep(5)
        self.update_display()
    
    def _draw_beautiful_summary(self, original_data, sorted_data, stats, n):
        """绘制精美的学习总结页面"""
        canvas_width = 1000
        canvas_height = 380
        
        # ===== 背景渐变效果 =====
        for i in range(canvas_height):
            # 从深蓝到浅蓝的渐变
            ratio = i / canvas_height
            r = int(15 + ratio * 30)
            g = int(23 + ratio * 50)
            b = int(42 + ratio * 60)
            color = f"#{r:02x}{g:02x}{b:02x}"
            self.canvas.create_line(0, i, canvas_width, i, fill=color, tags="scene")
        
        # ===== 顶部装饰条 =====
        self.canvas.create_rectangle(0, 0, canvas_width, 5, fill="#6366f1", outline="", tags="scene")
        
        # ===== 标题区域 =====
        # 标题背景光晕
        self.canvas.create_oval(canvas_width//2 - 200, -30, canvas_width//2 + 200, 70,
                               fill="#1e3a5f", outline="", tags="scene")
        
        # 主标题
        self.canvas.create_text(canvas_width // 2, 35, 
                               text="🎓 冒泡排序 · 学习总结",
                               font=("微软雅黑", 22, "bold"), fill="#ffffff", tags="scene")
        
        # 副标题装饰线
        self.canvas.create_line(canvas_width//2 - 150, 55, canvas_width//2 + 150, 55,
                               fill="#6366f1", width=2, tags="scene")
        
        # ===== 成就徽章 =====
        badge_x, badge_y = 880, 50
        # 徽章外圈
        self.canvas.create_oval(badge_x - 40, badge_y - 40, badge_x + 40, badge_y + 40,
                               fill="#fbbf24", outline="#f59e0b", width=3, tags="scene")
        # 徽章内圈
        self.canvas.create_oval(badge_x - 30, badge_y - 30, badge_x + 30, badge_y + 30,
                               fill="#fef3c7", outline="#fbbf24", width=2, tags="scene")
        # 徽章图标
        self.canvas.create_text(badge_x, badge_y - 5, text="✓",
                               font=("Arial", 24, "bold"), fill="#d97706", tags="scene")
        self.canvas.create_text(badge_x, badge_y + 22, text="完成",
                               font=("微软雅黑", 8, "bold"), fill="#92400e", tags="scene")
        
        # ===== 左侧：算法知识卡片 =====
        card1_x, card1_y = 40, 75
        card1_w, card1_h = 300, 290
        
        # 卡片阴影
        self.canvas.create_rectangle(card1_x + 4, card1_y + 4, 
                                    card1_x + card1_w + 4, card1_y + card1_h + 4,
                                    fill="#0f172a", outline="", tags="scene")
        # 卡片主体
        self.canvas.create_rectangle(card1_x, card1_y, card1_x + card1_w, card1_y + card1_h,
                                    fill="#1e293b", outline="#334155", width=2, tags="scene")
        
        # 卡片标题
        self.canvas.create_rectangle(card1_x, card1_y, card1_x + card1_w, card1_y + 35,
                                    fill="#6366f1", outline="", tags="scene")
        self.canvas.create_text(card1_x + card1_w//2, card1_y + 18, text="📚 算法知识点",
                               font=("微软雅黑", 12, "bold"), fill="#ffffff", tags="scene")
        
        # 知识点列表
        knowledge_items = [
            ("核心思想", "相邻元素两两比较\n大元素逐步「冒泡」到末尾", "#60a5fa"),
            ("时间复杂度", "最好 O(n) | 平均 O(n²) | 最坏 O(n²)", "#f472b6"),
            ("空间复杂度", "O(1) - 原地排序算法", "#34d399"),
            ("稳定性", "稳定排序 - 相等元素不改变顺序", "#fbbf24"),
        ]
        
        ky = card1_y + 55
        for title, content, color in knowledge_items:
            # 小圆点
            self.canvas.create_oval(card1_x + 15, ky + 3, card1_x + 23, ky + 11,
                                   fill=color, outline="", tags="scene")
            # 标题
            self.canvas.create_text(card1_x + 30, ky + 7, text=title,
                                   font=("微软雅黑", 10, "bold"), fill="#e2e8f0",
                                   anchor="w", tags="scene")
            # 内容
            self.canvas.create_text(card1_x + 30, ky + 32, text=content,
                                   font=("微软雅黑", 9), fill="#94a3b8",
                                   anchor="w", width=260, tags="scene")
            ky += 60
        
        # ===== 中间：统计数据卡片 =====
        card2_x, card2_y = 360, 75
        card2_w, card2_h = 280, 140
        
        # 卡片阴影和主体
        self.canvas.create_rectangle(card2_x + 4, card2_y + 4, 
                                    card2_x + card2_w + 4, card2_y + card2_h + 4,
                                    fill="#0f172a", outline="", tags="scene")
        self.canvas.create_rectangle(card2_x, card2_y, card2_x + card2_w, card2_y + card2_h,
                                    fill="#1e293b", outline="#334155", width=2, tags="scene")
        
        # 卡片标题
        self.canvas.create_rectangle(card2_x, card2_y, card2_x + card2_w, card2_y + 35,
                                    fill="#10b981", outline="", tags="scene")
        self.canvas.create_text(card2_x + card2_w//2, card2_y + 18, text="📊 本次排序统计",
                               font=("微软雅黑", 12, "bold"), fill="#ffffff", tags="scene")
        
        # 统计数据 - 比较次数
        stat_y = card2_y + 55
        self.canvas.create_text(card2_x + 20, stat_y, text="比较次数",
                               font=("微软雅黑", 10), fill="#94a3b8", anchor="w", tags="scene")
        # 进度条背景
        self.canvas.create_rectangle(card2_x + 90, stat_y - 8, card2_x + 220, stat_y + 8,
                                    fill="#334155", outline="", tags="scene")
        # 进度条填充
        max_compare = n * (n - 1) // 2  # 最大可能比较次数
        compare_ratio = min(1.0, stats['compare'] / max(1, max_compare))
        self.canvas.create_rectangle(card2_x + 90, stat_y - 8, 
                                    card2_x + 90 + int(130 * compare_ratio), stat_y + 8,
                                    fill="#3b82f6", outline="", tags="scene")
        # 数值
        self.canvas.create_text(card2_x + 240, stat_y, text=str(stats['compare']),
                               font=("Consolas", 12, "bold"), fill="#60a5fa", anchor="w", tags="scene")
        
        # 统计数据 - 交换次数
        stat_y = card2_y + 95
        self.canvas.create_text(card2_x + 20, stat_y, text="交换次数",
                               font=("微软雅黑", 10), fill="#94a3b8", anchor="w", tags="scene")
        # 进度条背景
        self.canvas.create_rectangle(card2_x + 90, stat_y - 8, card2_x + 220, stat_y + 8,
                                    fill="#334155", outline="", tags="scene")
        # 进度条填充
        swap_ratio = min(1.0, stats['swap'] / max(1, stats['compare']))
        self.canvas.create_rectangle(card2_x + 90, stat_y - 8, 
                                    card2_x + 90 + int(130 * swap_ratio), stat_y + 8,
                                    fill="#ef4444", outline="", tags="scene")
        # 数值
        self.canvas.create_text(card2_x + 240, stat_y, text=str(stats['swap']),
                               font=("Consolas", 12, "bold"), fill="#f87171", anchor="w", tags="scene")
        
        # ===== 中间下方：优化提示卡片 =====
        card3_x, card3_y = 360, 230
        card3_w, card3_h = 280, 135
        
        # 卡片阴影和主体
        self.canvas.create_rectangle(card3_x + 4, card3_y + 4, 
                                    card3_x + card3_w + 4, card3_y + card3_h + 4,
                                    fill="#0f172a", outline="", tags="scene")
        self.canvas.create_rectangle(card3_x, card3_y, card3_x + card3_w, card3_y + card3_h,
                                    fill="#1e293b", outline="#334155", width=2, tags="scene")
        
        # 卡片标题
        self.canvas.create_rectangle(card3_x, card3_y, card3_x + card3_w, card3_y + 35,
                                    fill="#f59e0b", outline="", tags="scene")
        self.canvas.create_text(card3_x + card3_w//2, card3_y + 18, text="💡 优化技巧",
                               font=("微软雅黑", 12, "bold"), fill="#ffffff", tags="scene")
        
        # 优化内容
        tips = [
            "• 设置标志位检测是否发生交换",
            "• 若某轮无交换，可提前结束",
            "• 记录最后交换位置优化边界",
        ]
        tip_y = card3_y + 55
        for tip in tips:
            self.canvas.create_text(card3_x + 15, tip_y, text=tip,
                                   font=("微软雅黑", 9), fill="#fcd34d",
                                   anchor="w", tags="scene")
            tip_y += 25
        
        # ===== 右侧：排序前后对比卡片 =====
        card4_x, card4_y = 660, 75
        card4_w, card4_h = 320, 290
        
        # 卡片阴影和主体
        self.canvas.create_rectangle(card4_x + 4, card4_y + 4, 
                                    card4_x + card4_w + 4, card4_y + card4_h + 4,
                                    fill="#0f172a", outline="", tags="scene")
        self.canvas.create_rectangle(card4_x, card4_y, card4_x + card4_w, card4_y + card4_h,
                                    fill="#1e293b", outline="#334155", width=2, tags="scene")
        
        # 卡片标题
        self.canvas.create_rectangle(card4_x, card4_y, card4_x + card4_w, card4_y + 35,
                                    fill="#8b5cf6", outline="", tags="scene")
        self.canvas.create_text(card4_x + card4_w//2, card4_y + 18, text="📈 排序前后对比",
                               font=("微软雅黑", 12, "bold"), fill="#ffffff", tags="scene")
        
        # 计算条形图参数
        bar_area_top = card4_y + 50
        bar_area_height = 100
        bar_width = min(25, (card4_w - 60) // len(original_data) - 4)
        
        max_val = max(max(original_data), max(sorted_data))
        min_val = min(min(original_data), min(sorted_data))
        val_range = max_val - min_val if max_val != min_val else 1
        
        def draw_mini_bars(data_list, start_y, label, label_color, bar_color):
            """绘制迷你条形图"""
            self.canvas.create_text(card4_x + 15, start_y + bar_area_height // 2, text=label,
                                   font=("微软雅黑", 9, "bold"), fill=label_color,
                                   anchor="w", tags="scene")
            
            bar_start_x = card4_x + 60
            for i, val in enumerate(data_list):
                height = max(10, int(((val - min_val) / val_range) * (bar_area_height - 20) + 10))
                x = bar_start_x + i * (bar_width + 4)
                y_bottom = start_y + bar_area_height - 5
                y_top = y_bottom - height
                
                # 条形
                self.canvas.create_rectangle(x, y_top, x + bar_width, y_bottom,
                                            fill=bar_color, outline="", tags="scene")
                # 数值
                self.canvas.create_text(x + bar_width // 2, y_top - 8, text=str(int(val)),
                                       font=("Consolas", 8, "bold"), fill="#e2e8f0", tags="scene")
        
        # 绘制排序前
        draw_mini_bars(original_data, bar_area_top, "排序前", "#f87171", "#ef4444")
        
        # 箭头分隔
        arrow_y = bar_area_top + bar_area_height + 15
        self.canvas.create_text(card4_x + card4_w // 2, arrow_y, text="▼  冒泡排序  ▼",
                               font=("微软雅黑", 10, "bold"), fill="#a78bfa", tags="scene")
        
        # 绘制排序后
        draw_mini_bars(sorted_data, arrow_y + 20, "排序后", "#34d399", "#10b981")
        
        # 数组文字对比
        text_y = arrow_y + 135
        self.canvas.create_text(card4_x + card4_w // 2, text_y,
                               text=f"前：{[int(x) for x in original_data]}",
                               font=("Consolas", 9), fill="#f87171", tags="scene")
        self.canvas.create_text(card4_x + card4_w // 2, text_y + 18,
                               text=f"后：{[int(x) for x in sorted_data]}",
                               font=("Consolas", 9), fill="#34d399", tags="scene")
        
        # ===== 底部装饰 =====
        self.canvas.create_text(canvas_width // 2, canvas_height - 12,
                               text="✨ 恭喜你完成了冒泡排序的学习！继续加油！ ✨",
                               font=("微软雅黑", 10), fill="#64748b", tags="scene")
        
        self.window.update()

    # ==================== 直接插入排序可视化（教学版） ====================
    
    def start_insertion_sort(self):
        """启动直接插入排序可视化 - 教学版"""
        if len(self.data_store) < 2:
            messagebox.showinfo("提示", "顺序表元素少于2个，无需排序")
            return
        
        # 检查是否所有元素都是数字
        try:
            numeric_data = [float(x) for x in self.data_store]
        except ValueError:
            messagebox.showerror("错误", "插入排序需要数值类型的元素")
            return
        
        self.disable_buttons()
        self.animate_insertion_sort_teaching()
        self.enable_buttons()
    
    def animate_insertion_sort_teaching(self):
        """直接插入排序教学演示 - 详细步骤说明版"""
        # 获取数值数据
        try:
            data = [float(x) for x in self.data_store]
        except ValueError:
            messagebox.showerror("错误", "数据必须为数值类型")
            return
        
        n = len(data)
        original_data = data.copy()
        
        # 设置教学伪代码
        pseudo_lines = [
            "【直接插入排序原理】",
            "将数组分为已排序和未排序两部分",
            "每次从未排序部分取出第一个元素",
            "在已排序部分找到合适位置插入",
            "直到所有元素都插入完成",
            "─────────────────",
            f"for i = 1 to {n-1}:  // 从第2个元素开始",
            "  key = data[i]  // 取出当前元素",
            "  j = i - 1  // 从已排序部分末尾开始",
            "  while j >= 0 and data[j] > key:",
            "    data[j+1] = data[j]  // 元素后移",
            "    j = j - 1",
            "  data[j+1] = key  // 插入到正确位置"
        ]
        self.set_pseudo_code("🎓 直接插入排序教学演示", pseudo_lines)
        
        # 清空画布
        self.canvas.delete("all")
        
        # ===== 布局参数（优化避免遮挡）=====
        canvas_width = 1000
        canvas_height = 380
        
        # 条形图区域（左侧）- 增加顶部空间
        bar_area_left = 50
        bar_area_right = 620
        bar_area_top = 155  # 增加顶部空间给key和标签
        bar_area_bottom = 340
        
        # 教学说明区域（右侧）
        info_area_left = 640
        info_area_top = 10
        
        # 计算条形参数
        bar_area_width = bar_area_right - bar_area_left
        bar_width = max(30, min(55, (bar_area_width - 20) // n - 8))
        total_bars_width = n * bar_width + (n - 1) * 8
        bar_start_x = bar_area_left + (bar_area_width - total_bars_width) // 2
        
        # 数值范围
        max_val = max(data)
        min_val = min(data)
        value_range = max_val - min_val if max_val != min_val else 1
        bar_max_height = bar_area_bottom - bar_area_top - 50
        
        def get_bar_height(value):
            """计算条形高度"""
            if value_range == 0:
                return bar_max_height // 2
            normalized = (value - min_val) / value_range
            return max(30, int(normalized * bar_max_height * 0.85 + bar_max_height * 0.15))
        
        def get_bar_x(index):
            """获取条形的X坐标"""
            return bar_start_x + index * (bar_width + 8)
        
        def draw_insertion_scene(arr, sorted_boundary, current_i=-1, key_value=None, 
                                 key_floating=False, shift_indices=None, insert_pos=-1,
                                 action="", stats=None, compare_j=-1):
            """绘制插入排序场景"""
            self.canvas.delete("scene")
            shift_indices = shift_indices or []
            stats = stats or {"compare": 0, "shift": 0}
            
            # ===== 标题（左上角）=====
            self.canvas.create_text(20, 18,
                                   text="🎓 直接插入排序 · 教学演示",
                                   font=("微软雅黑", 14, "bold"), fill="#2c3e50",
                                   anchor="w", tags="scene")
            
            # ===== 颜色图例（标题下方）=====
            legend_y = 42
            legend_items = [
                ("🟢 已排序", "#27ae60"),
                ("🔵 未排序", "#3498db"),
                ("🟡 key", "#f1c40f"),
                ("🔴 移动", "#e74c3c"),
            ]
            legend_x = 20
            for text, color in legend_items:
                self.canvas.create_rectangle(legend_x, legend_y - 6, legend_x + 12, legend_y + 6,
                                            fill=color, outline="", tags="scene")
                self.canvas.create_text(legend_x + 16, legend_y, text=text,
                                       font=("微软雅黑", 8), fill="#2c3e50", 
                                       anchor="w", tags="scene")
                legend_x += 80
            
            # ===== key 浮动显示区域（条形图上方居中）=====
            if key_floating and key_value is not None:
                float_x = (bar_area_left + bar_area_right) // 2
                float_y = 80
                
                # key 背景框
                self.canvas.create_rectangle(float_x - 70, float_y - 20,
                                            float_x + 70, float_y + 20,
                                            fill="#fff3cd", outline="#ffc107", width=2,
                                            tags="scene")
                
                # key 标签
                self.canvas.create_text(float_x - 30, float_y, text="🔑 key =",
                                       font=("微软雅黑", 11, "bold"), fill="#856404",
                                       tags="scene")
                self.canvas.create_text(float_x + 30, float_y, text=str(int(key_value)),
                                       font=("Arial", 18, "bold"), fill="#d63384",
                                       tags="scene")
            
            # ===== 分区标识（在条形图区域内顶部）=====
            region_label_y = bar_area_top - 12
            
            if sorted_boundary > 0:
                # 已排序区域背景
                sorted_end_x = get_bar_x(sorted_boundary - 1) + bar_width + 8
                self.canvas.create_rectangle(bar_start_x - 8, bar_area_top - 5,
                                            sorted_end_x, bar_area_bottom + 5,
                                            fill="#e8f5e9", outline="#27ae60", width=2,
                                            dash=(4, 2), tags="scene")
                self.canvas.create_text((bar_start_x + sorted_end_x) // 2, region_label_y,
                                       text="已排序", font=("微软雅黑", 8, "bold"),
                                       fill="#27ae60", tags="scene")
            
            if sorted_boundary < n:
                # 未排序区域背景
                unsorted_start_x = get_bar_x(sorted_boundary) - 8
                self.canvas.create_rectangle(unsorted_start_x, bar_area_top - 5,
                                            get_bar_x(n-1) + bar_width + 8, bar_area_bottom + 5,
                                            fill="#e3f2fd", outline="#3498db", width=2,
                                            dash=(4, 2), tags="scene")
                self.canvas.create_text((unsorted_start_x + get_bar_x(n-1) + bar_width) // 2, 
                                       region_label_y,
                                       text="未排序", font=("微软雅黑", 8, "bold"),
                                       fill="#3498db", tags="scene")
            
            # ===== 绘制条形图 =====
            for i, value in enumerate(arr):
                x = get_bar_x(i)
                bar_height = get_bar_height(value)
                y_bottom = bar_area_bottom
                y_top = y_bottom - bar_height
                
                # 确定颜色
                if i == insert_pos and key_value is not None:
                    color = "#9b59b6"  # 紫色 - 插入位置
                    outline = "#8e44ad"
                    width = 3
                elif i in shift_indices:
                    color = "#e74c3c"  # 红色 - 正在移动
                    outline = "#c0392b"
                    width = 3
                elif i == current_i and not key_floating:
                    color = "#f1c40f"  # 黄色 - 当前key
                    outline = "#f39c12"
                    width = 3
                elif i < sorted_boundary:
                    color = "#27ae60"  # 绿色 - 已排序
                    outline = "#1e8449"
                    width = 2
                else:
                    color = "#3498db"  # 蓝色 - 未排序
                    outline = "#2980b9"
                    width = 2
                
                # 绘制条形（带阴影效果）
                shadow_offset = 3
                self.canvas.create_rectangle(x + shadow_offset, y_top + shadow_offset, 
                                            x + bar_width + shadow_offset, y_bottom + shadow_offset,
                                            fill="#bdc3c7", outline="", tags="scene")
                
                self.canvas.create_rectangle(x, y_top, x + bar_width, y_bottom,
                                            fill=color, outline=outline, width=width,
                                            tags="scene")
                
                # 条形内数值
                self.canvas.create_text(x + bar_width // 2, (y_top + y_bottom) // 2,
                                       text=f"{int(value)}",
                                       font=("Arial", 14, "bold"), fill="white",
                                       tags="scene")
                
                # 索引标签
                self.canvas.create_text(x + bar_width // 2, y_bottom + 18,
                                       text=f"[{i}]",
                                       font=("Arial", 10), fill="#7f8c8d",
                                       tags="scene")
                
                # 比较指示箭头（在条形上方，但不超出区域）
                if compare_j >= 0 and i == compare_j:
                    arrow_y = max(y_top - 15, bar_area_top + 5)
                    self.canvas.create_text(x + bar_width // 2, arrow_y,
                                           text="▼比较",
                                           font=("微软雅黑", 8, "bold"), fill="#e74c3c",
                                           tags="scene")
            
            # ===== 右侧教学信息面板 =====
            panel_x = info_area_left
            panel_y = info_area_top
            panel_bottom = 370
            
            # 面板背景
            self.canvas.create_rectangle(panel_x, panel_y, canvas_width - 10, panel_bottom,
                                        fill="#f8f9fa", outline="#dee2e6", width=2,
                                        tags="scene")
            
            # 当前状态标题
            self.canvas.create_text(panel_x + 12, panel_y + 18, text="📌 当前状态",
                                   font=("微软雅黑", 11, "bold"), fill="#2c3e50",
                                   anchor="w", tags="scene")
            
            # 轮次信息
            round_text = f"正在处理第 {current_i + 1} 个元素" if current_i >= 0 else "准备开始"
            self.canvas.create_text(panel_x + 12, panel_y + 42,
                                   text=round_text,
                                   font=("微软雅黑", 10), fill="#6c757d",
                                   anchor="w", tags="scene")
            
            # 分隔线
            self.canvas.create_line(panel_x + 8, panel_y + 58, canvas_width - 18, panel_y + 58,
                                   fill="#dee2e6", tags="scene")
            
            # 操作说明
            self.canvas.create_text(panel_x + 12, panel_y + 76, text="💡 操作说明",
                                   font=("微软雅黑", 10, "bold"), fill="#2c3e50",
                                   anchor="w", tags="scene")
            
            # 当前操作
            action_lines = action.split("\n") if action else ["等待开始..."]
            action_y = panel_y + 96
            for line in action_lines[:6]:
                self.canvas.create_text(panel_x + 12, action_y, text=line,
                                       font=("微软雅黑", 9), fill="#495057",
                                       anchor="w", width=320, tags="scene")
                action_y += 20
            
            # 分隔线
            self.canvas.create_line(panel_x + 8, panel_y + 225, canvas_width - 18, panel_y + 225,
                                   fill="#dee2e6", tags="scene")
            
            # 统计信息
            self.canvas.create_text(panel_x + 12, panel_y + 245, text="📊 统计数据",
                                   font=("微软雅黑", 10, "bold"), fill="#2c3e50",
                                   anchor="w", tags="scene")
            
            self.canvas.create_text(panel_x + 12, panel_y + 268,
                                   text=f"比较次数：{stats['compare']}",
                                   font=("微软雅黑", 10), fill="#17a2b8",
                                   anchor="w", tags="scene")
            
            self.canvas.create_text(panel_x + 12, panel_y + 290,
                                   text=f"移动次数：{stats['shift']}",
                                   font=("微软雅黑", 10), fill="#dc3545",
                                   anchor="w", tags="scene")
            
            # 原始 vs 当前数组对比
            self.canvas.create_text(panel_x + 12, panel_y + 320,
                                   text=f"原始：{[int(x) for x in original_data]}",
                                   font=("Consolas", 8), fill="#6c757d",
                                   anchor="w", tags="scene")
            self.canvas.create_text(panel_x + 12, panel_y + 340,
                                   text=f"当前：{[int(x) for x in arr]}",
                                   font=("Consolas", 8), fill="#28a745",
                                   anchor="w", tags="scene")
            
            self.window.update()
        
        # ===== 开始教学演示 =====
        stats = {"compare": 0, "shift": 0}
        
        # 第0步：介绍
        self.highlight_pseudo_line(0)
        draw_insertion_scene(data, sorted_boundary=1, action="🎬 直接插入排序开始！\n\n核心思想：\n将数组分为已排序和未排序两部分\n逐个将未排序元素插入到已排序部分", stats=stats)
        time.sleep(1.5)
        
        self.highlight_pseudo_line(1)
        self.highlight_pseudo_line(2)
        draw_insertion_scene(data, sorted_boundary=1, action="📖 算法原理：\n第一个元素默认已排序\n从第二个元素开始\n每次取出一个元素（称为key）\n在已排序部分找到合适位置插入", stats=stats)
        time.sleep(1.5)
        
        # 主循环：从第二个元素开始
        for i in range(1, n):
            key = data[i]
            
            # 步骤1：取出当前元素作为key
            self.highlight_pseudo_line(6)
            self.highlight_pseudo_line(7)
            draw_insertion_scene(data, sorted_boundary=i, current_i=i,
                               action=f"🔄 开始处理第 {i+1} 个元素\n\n从位置 [{i}] 取出元素\nkey = {int(key)}\n这个元素需要插入到已排序部分",
                               stats=stats)
            time.sleep(0.8)
            
            # 提取key，显示浮动效果
            draw_insertion_scene(data, sorted_boundary=i, current_i=i, key_value=key,
                               key_floating=True,
                               action=f"🔑 提取 key = {int(key)}\n\n已将元素从位置 [{i}] 取出\n现在需要在已排序部分\n找到它应该插入的位置",
                               stats=stats)
            time.sleep(0.8)
            
            # 步骤2：从后向前扫描已排序部分
            self.highlight_pseudo_line(8)
            j = i - 1
            
            draw_insertion_scene(data, sorted_boundary=i, current_i=i, key_value=key,
                               key_floating=True, compare_j=j,
                               action=f"👀 开始比较\n\n从已排序部分的末尾开始\nj = {j}\n比较 data[{j}]={int(data[j])} 和 key={int(key)}",
                               stats=stats)
            time.sleep(0.6)
            
            # 步骤3：向前移动比key大的元素
            insert_position = i  # 记录最终插入位置
            
            while j >= 0 and data[j] > key:
                stats["compare"] += 1
                
                self.highlight_pseudo_line(9)
                draw_insertion_scene(data, sorted_boundary=i, current_i=i, key_value=key,
                                   key_floating=True, compare_j=j,
                                   action=f"⚠️ data[{j}] = {int(data[j])} > key = {int(key)}\n\n{int(data[j])} 比 {int(key)} 大\n需要将 {int(data[j])} 向后移动一位\n为 key 腾出位置",
                                   stats=stats)
                time.sleep(0.6)
                
                # 显示移动动画
                self.highlight_pseudo_line(10)
                draw_insertion_scene(data, sorted_boundary=i, current_i=i, key_value=key,
                                   key_floating=True, shift_indices=[j],
                                   action=f"🔀 移动元素\n\ndata[{j+1}] = data[{j}]\n将 {int(data[j])} 从位置 [{j}] 移到 [{j+1}]",
                                   stats=stats)
                time.sleep(0.5)
                
                # 执行移动
                data[j + 1] = data[j]
                stats["shift"] += 1
                
                draw_insertion_scene(data, sorted_boundary=i, current_i=i, key_value=key,
                                   key_floating=True,
                                   action=f"✓ 移动完成\n\n元素 {int(data[j+1])} 已移到位置 [{j+1}]\n继续向前检查...",
                                   stats=stats)
                time.sleep(0.4)
                
                self.highlight_pseudo_line(11)
                j -= 1
                insert_position = j + 1
                
                if j >= 0:
                    draw_insertion_scene(data, sorted_boundary=i, current_i=i, key_value=key,
                                       key_floating=True, compare_j=j,
                                       action=f"👀 继续比较\n\nj = {j}\n比较 data[{j}]={int(data[j])} 和 key={int(key)}",
                                       stats=stats)
                    time.sleep(0.4)
            
            # 如果还有比较但不需要移动
            if j >= 0:
                stats["compare"] += 1
                draw_insertion_scene(data, sorted_boundary=i, current_i=i, key_value=key,
                                   key_floating=True, compare_j=j,
                                   action=f"✓ data[{j}] = {int(data[j])} ≤ key = {int(key)}\n\n{int(data[j])} 不大于 {int(key)}\n找到插入位置了！\nkey 应该插入到位置 [{j+1}]",
                                   stats=stats)
                time.sleep(0.6)
                insert_position = j + 1
            else:
                draw_insertion_scene(data, sorted_boundary=i, current_i=i, key_value=key,
                                   key_floating=True,
                                   action=f"✓ 已到达数组开头\n\nj = -1，没有更小的元素了\nkey 应该插入到位置 [0]\n即数组最前面",
                                   stats=stats)
                time.sleep(0.6)
                insert_position = 0
            
            # 步骤4：插入key到正确位置
            self.highlight_pseudo_line(12)
            draw_insertion_scene(data, sorted_boundary=i, current_i=i, key_value=key,
                               key_floating=True, insert_pos=insert_position,
                               action=f"📍 插入 key\n\ndata[{insert_position}] = {int(key)}\n将 key 插入到位置 [{insert_position}]",
                               stats=stats)
            time.sleep(0.6)
            
            # 执行插入
            data[insert_position] = key
            
            # 本轮完成
            draw_insertion_scene(data, sorted_boundary=i+1,
                               action=f"🎉 第 {i} 轮完成！\n\n元素 {int(key)} 已插入到位置 [{insert_position}]\n已排序区域扩展到 {i+1} 个元素",
                               stats=stats)
            time.sleep(0.8)
        
        # 排序完成
        draw_insertion_scene(data, sorted_boundary=n,
                           action=f"🏆 排序完成！\n\n所有元素都已排好序\n总比较次数：{stats['compare']}\n总移动次数：{stats['shift']}",
                           stats=stats)
        
        self.complete_pseudo_code()
        
        # 更新模型数据
        self.model.data = [str(int(x)) if x == int(x) else str(x) for x in data]
        
        # 添加操作历史
        self.add_operation_history(f"插入排序完成: 比较{stats['compare']}次, 移动{stats['shift']}次")
        
        # 显示精美总结页面
        time.sleep(1.5)
        self.canvas.delete("scene")
        self._draw_insertion_sort_summary(original_data, data, stats, n)
        
        # 等待用户查看总结
        time.sleep(5)
        self.update_display()
    
    def _draw_insertion_sort_summary(self, original_data, sorted_data, stats, n):
        """绘制插入排序的精美学习总结页面"""
        canvas_width = 1000
        canvas_height = 380
        
        # ===== 背景渐变效果 =====
        for i in range(canvas_height):
            ratio = i / canvas_height
            r = int(20 + ratio * 25)
            g = int(30 + ratio * 40)
            b = int(48 + ratio * 50)
            color = f"#{r:02x}{g:02x}{b:02x}"
            self.canvas.create_line(0, i, canvas_width, i, fill=color, tags="scene")
        
        # ===== 顶部装饰条 =====
        self.canvas.create_rectangle(0, 0, canvas_width, 5, fill="#16a085", outline="", tags="scene")
        
        # ===== 标题区域 =====
        self.canvas.create_oval(canvas_width//2 - 200, -30, canvas_width//2 + 200, 70,
                               fill="#1a4a3a", outline="", tags="scene")
        
        self.canvas.create_text(canvas_width // 2, 35, 
                               text="🎓 直接插入排序 · 学习总结",
                               font=("微软雅黑", 22, "bold"), fill="#ffffff", tags="scene")
        
        self.canvas.create_line(canvas_width//2 - 150, 55, canvas_width//2 + 150, 55,
                               fill="#16a085", width=2, tags="scene")
        
        # ===== 成就徽章 =====
        badge_x, badge_y = 880, 50
        self.canvas.create_oval(badge_x - 40, badge_y - 40, badge_x + 40, badge_y + 40,
                               fill="#10b981", outline="#059669", width=3, tags="scene")
        self.canvas.create_oval(badge_x - 30, badge_y - 30, badge_x + 30, badge_y + 30,
                               fill="#d1fae5", outline="#10b981", width=2, tags="scene")
        self.canvas.create_text(badge_x, badge_y - 5, text="✓",
                               font=("Arial", 24, "bold"), fill="#047857", tags="scene")
        self.canvas.create_text(badge_x, badge_y + 22, text="完成",
                               font=("微软雅黑", 8, "bold"), fill="#065f46", tags="scene")
        
        # ===== 左侧：算法知识卡片 =====
        card1_x, card1_y = 40, 75
        card1_w, card1_h = 300, 290
        
        self.canvas.create_rectangle(card1_x + 4, card1_y + 4, 
                                    card1_x + card1_w + 4, card1_y + card1_h + 4,
                                    fill="#0f172a", outline="", tags="scene")
        self.canvas.create_rectangle(card1_x, card1_y, card1_x + card1_w, card1_y + card1_h,
                                    fill="#1e293b", outline="#334155", width=2, tags="scene")
        
        self.canvas.create_rectangle(card1_x, card1_y, card1_x + card1_w, card1_y + 35,
                                    fill="#16a085", outline="", tags="scene")
        self.canvas.create_text(card1_x + card1_w//2, card1_y + 18, text="📚 算法知识点",
                               font=("微软雅黑", 12, "bold"), fill="#ffffff", tags="scene")
        
        knowledge_items = [
            ("核心思想", "将数组分为已排序和未排序\n逐个将元素插入到正确位置", "#2dd4bf"),
            ("时间复杂度", "最好 O(n) | 平均 O(n²) | 最坏 O(n²)", "#f472b6"),
            ("空间复杂度", "O(1) - 原地排序算法", "#34d399"),
            ("稳定性", "稳定排序 - 相等元素不改变顺序", "#fbbf24"),
        ]
        
        ky = card1_y + 55
        for title, content, color in knowledge_items:
            self.canvas.create_oval(card1_x + 15, ky + 3, card1_x + 23, ky + 11,
                                   fill=color, outline="", tags="scene")
            self.canvas.create_text(card1_x + 30, ky + 7, text=title,
                                   font=("微软雅黑", 10, "bold"), fill="#e2e8f0",
                                   anchor="w", tags="scene")
            self.canvas.create_text(card1_x + 30, ky + 32, text=content,
                                   font=("微软雅黑", 9), fill="#94a3b8",
                                   anchor="w", width=260, tags="scene")
            ky += 60
        
        # ===== 中间：统计数据卡片 =====
        card2_x, card2_y = 360, 75
        card2_w, card2_h = 280, 140
        
        self.canvas.create_rectangle(card2_x + 4, card2_y + 4, 
                                    card2_x + card2_w + 4, card2_y + card2_h + 4,
                                    fill="#0f172a", outline="", tags="scene")
        self.canvas.create_rectangle(card2_x, card2_y, card2_x + card2_w, card2_y + card2_h,
                                    fill="#1e293b", outline="#334155", width=2, tags="scene")
        
        self.canvas.create_rectangle(card2_x, card2_y, card2_x + card2_w, card2_y + 35,
                                    fill="#0ea5e9", outline="", tags="scene")
        self.canvas.create_text(card2_x + card2_w//2, card2_y + 18, text="📊 本次排序统计",
                               font=("微软雅黑", 12, "bold"), fill="#ffffff", tags="scene")
        
        # 比较次数
        stat_y = card2_y + 55
        self.canvas.create_text(card2_x + 20, stat_y, text="比较次数",
                               font=("微软雅黑", 10), fill="#94a3b8", anchor="w", tags="scene")
        self.canvas.create_rectangle(card2_x + 90, stat_y - 8, card2_x + 220, stat_y + 8,
                                    fill="#334155", outline="", tags="scene")
        max_compare = n * (n - 1) // 2
        compare_ratio = min(1.0, stats['compare'] / max(1, max_compare))
        self.canvas.create_rectangle(card2_x + 90, stat_y - 8, 
                                    card2_x + 90 + int(130 * compare_ratio), stat_y + 8,
                                    fill="#0ea5e9", outline="", tags="scene")
        self.canvas.create_text(card2_x + 240, stat_y, text=str(stats['compare']),
                               font=("Consolas", 12, "bold"), fill="#38bdf8", anchor="w", tags="scene")
        
        # 移动次数
        stat_y = card2_y + 95
        self.canvas.create_text(card2_x + 20, stat_y, text="移动次数",
                               font=("微软雅黑", 10), fill="#94a3b8", anchor="w", tags="scene")
        self.canvas.create_rectangle(card2_x + 90, stat_y - 8, card2_x + 220, stat_y + 8,
                                    fill="#334155", outline="", tags="scene")
        shift_ratio = min(1.0, stats['shift'] / max(1, stats['compare']))
        self.canvas.create_rectangle(card2_x + 90, stat_y - 8, 
                                    card2_x + 90 + int(130 * shift_ratio), stat_y + 8,
                                    fill="#f43f5e", outline="", tags="scene")
        self.canvas.create_text(card2_x + 240, stat_y, text=str(stats['shift']),
                               font=("Consolas", 12, "bold"), fill="#fb7185", anchor="w", tags="scene")
        
        # ===== 中间下方：特点对比卡片 =====
        card3_x, card3_y = 360, 230
        card3_w, card3_h = 280, 135
        
        self.canvas.create_rectangle(card3_x + 4, card3_y + 4, 
                                    card3_x + card3_w + 4, card3_y + card3_h + 4,
                                    fill="#0f172a", outline="", tags="scene")
        self.canvas.create_rectangle(card3_x, card3_y, card3_x + card3_w, card3_y + card3_h,
                                    fill="#1e293b", outline="#334155", width=2, tags="scene")
        
        self.canvas.create_rectangle(card3_x, card3_y, card3_x + card3_w, card3_y + 35,
                                    fill="#8b5cf6", outline="", tags="scene")
        self.canvas.create_text(card3_x + card3_w//2, card3_y + 18, text="💡 算法特点",
                               font=("微软雅黑", 12, "bold"), fill="#ffffff", tags="scene")
        
        tips = [
            "• 对小规模数据效率较高",
            "• 对基本有序的数据效率很高",
            "• 实现简单，适合教学入门",
        ]
        tip_y = card3_y + 55
        for tip in tips:
            self.canvas.create_text(card3_x + 15, tip_y, text=tip,
                                   font=("微软雅黑", 9), fill="#c4b5fd",
                                   anchor="w", tags="scene")
            tip_y += 25
        
        # ===== 右侧：排序前后对比卡片 =====
        card4_x, card4_y = 660, 75
        card4_w, card4_h = 320, 290
        
        self.canvas.create_rectangle(card4_x + 4, card4_y + 4, 
                                    card4_x + card4_w + 4, card4_y + card4_h + 4,
                                    fill="#0f172a", outline="", tags="scene")
        self.canvas.create_rectangle(card4_x, card4_y, card4_x + card4_w, card4_y + card4_h,
                                    fill="#1e293b", outline="#334155", width=2, tags="scene")
        
        self.canvas.create_rectangle(card4_x, card4_y, card4_x + card4_w, card4_y + 35,
                                    fill="#ec4899", outline="", tags="scene")
        self.canvas.create_text(card4_x + card4_w//2, card4_y + 18, text="📈 排序前后对比",
                               font=("微软雅黑", 12, "bold"), fill="#ffffff", tags="scene")
        
        # 计算条形图参数
        bar_area_top = card4_y + 50
        bar_area_height = 100
        bar_width = min(25, (card4_w - 60) // len(original_data) - 4)
        
        max_val = max(max(original_data), max(sorted_data))
        min_val = min(min(original_data), min(sorted_data))
        val_range = max_val - min_val if max_val != min_val else 1
        
        def draw_mini_bars(data_list, start_y, label, label_color, bar_color):
            self.canvas.create_text(card4_x + 15, start_y + bar_area_height // 2, text=label,
                                   font=("微软雅黑", 9, "bold"), fill=label_color,
                                   anchor="w", tags="scene")
            
            bar_start_x = card4_x + 60
            for i, val in enumerate(data_list):
                height = max(10, int(((val - min_val) / val_range) * (bar_area_height - 20) + 10))
                x = bar_start_x + i * (bar_width + 4)
                y_bottom = start_y + bar_area_height - 5
                y_top = y_bottom - height
                
                self.canvas.create_rectangle(x, y_top, x + bar_width, y_bottom,
                                            fill=bar_color, outline="", tags="scene")
                self.canvas.create_text(x + bar_width // 2, y_top - 8, text=str(int(val)),
                                       font=("Consolas", 8, "bold"), fill="#e2e8f0", tags="scene")
        
        draw_mini_bars(original_data, bar_area_top, "排序前", "#fb7185", "#f43f5e")
        
        arrow_y = bar_area_top + bar_area_height + 15
        self.canvas.create_text(card4_x + card4_w // 2, arrow_y, text="▼  插入排序  ▼",
                               font=("微软雅黑", 10, "bold"), fill="#a78bfa", tags="scene")
        
        draw_mini_bars(sorted_data, arrow_y + 20, "排序后", "#34d399", "#10b981")
        
        text_y = arrow_y + 135
        self.canvas.create_text(card4_x + card4_w // 2, text_y,
                               text=f"前：{[int(x) for x in original_data]}",
                               font=("Consolas", 9), fill="#fb7185", tags="scene")
        self.canvas.create_text(card4_x + card4_w // 2, text_y + 18,
                               text=f"后：{[int(x) for x in sorted_data]}",
                               font=("Consolas", 9), fill="#34d399", tags="scene")
        
        # ===== 底部装饰 =====
        self.canvas.create_text(canvas_width // 2, canvas_height - 12,
                               text="✨ 恭喜你完成了直接插入排序的学习！继续加油！ ✨",
                               font=("微软雅黑", 10), fill="#64748b", tags="scene")
        
        self.window.update()

    # ==================== 快速排序可视化（教学版·增强版） ====================
    
    def start_quick_sort(self):
        """启动快速排序可视化 - 教学版"""
        if len(self.data_store) < 2:
            messagebox.showinfo("提示", "顺序表元素少于2个，无需排序")
            return
        
        # 检查是否所有元素都是数字
        try:
            numeric_data = [float(x) for x in self.data_store]
        except ValueError:
            messagebox.showerror("错误", "快速排序需要数值类型的元素")
            return
        
        self.disable_buttons()
        self.animate_quick_sort_teaching()
        self.enable_buttons()
    
    def animate_quick_sort_teaching(self):
        """快速排序教学演示 - 详细步骤说明版（增强版）"""
        # 获取数值数据
        try:
            data = [float(x) for x in self.data_store]
        except ValueError:
            messagebox.showerror("错误", "数据必须为数值类型")
            return
        
        n = len(data)
        original_data = data.copy()
        
        # 设置教学伪代码
        pseudo_lines = [
            "【快速排序原理】分治法",
            "1. 选择基准元素(pivot)",
            "2. 分区：小于pivot放左边，大于放右边",
            "3. 递归排序左右两部分",
            "─────────────────",
            "QuickSort(arr, low, high):",
            "  if low < high:",
            "    pivot_idx = Partition(arr, low, high)",
            "    QuickSort(arr, low, pivot_idx-1)",
            "    QuickSort(arr, pivot_idx+1, high)",
            "─────────────────",
            "Partition(arr, low, high):",
            "  pivot = arr[high]  // 选最后一个为基准",
            "  i = low - 1  // 分界线",
            "  for j = low to high-1:",
            "    if arr[j] <= pivot:",
            "      i++; swap(arr[i], arr[j])",
            "  swap(arr[i+1], arr[high])",
            "  return i + 1"
        ]
        self.set_pseudo_code("🎓 快速排序教学演示", pseudo_lines)
        
        # 清空画布
        self.canvas.delete("all")
        
        # ===== 布局参数 =====
        canvas_width = 1000
        canvas_height = 380
        
        # 条形图区域
        bar_area_left = 50
        bar_area_right = 620
        bar_area_top = 140
        bar_area_bottom = 335
        
        # 教学说明区域
        info_area_left = 640
        info_area_top = 10
        
        # 计算条形参数
        bar_area_width = bar_area_right - bar_area_left
        bar_width = max(28, min(50, (bar_area_width - 20) // n - 8))
        total_bars_width = n * bar_width + (n - 1) * 8
        bar_start_x = bar_area_left + (bar_area_width - total_bars_width) // 2
        
        # 数值范围
        max_val = max(data)
        min_val = min(data)
        value_range = max_val - min_val if max_val != min_val else 1
        bar_max_height = bar_area_bottom - bar_area_top - 45
        
        # 统计
        stats = {"compare": 0, "swap": 0, "partition_count": 0, "recursion_depth": 0}
        
        # 记录已完成排序的位置
        sorted_positions = set()
        
        # 记录小于等于pivot的区域 (用于可视化)
        less_equal_region = set()
        
        def get_bar_height(value):
            if value_range == 0:
                return bar_max_height // 2
            normalized = (value - min_val) / value_range
            return max(28, int(normalized * bar_max_height * 0.85 + bar_max_height * 0.15))
        
        def get_bar_x(index):
            return bar_start_x + index * (bar_width + 8)
        
        def draw_quick_scene(arr, low=-1, high=-1, pivot_idx=-1, i_ptr=-1, j_ptr=-1,
                            swap_pair=None, action="", depth=0, show_wall=False,
                            compare_result=None, less_region=None):
            """绘制快速排序场景（增强版）"""
            self.canvas.delete("scene")
            swap_pair = swap_pair or []
            less_region = less_region or set()
            
            # ===== 标题 =====
            self.canvas.create_text(20, 15,
                                   text="🎓 快速排序 · 教学演示",
                                   font=("微软雅黑", 14, "bold"), fill="#2c3e50",
                                   anchor="w", tags="scene")
            
            # ===== 颜色图例（更详细）=====
            legend_y = 38
            legend_items = [
                ("🟣 基准", "#9b59b6"),
                ("🟢 ≤基准", "#27ae60"),
                ("🔵 待处理", "#3498db"),
                ("🔴 交换", "#e74c3c"),
                ("✅ 已排序", "#16a085"),
            ]
            legend_x = 20
            for text, color in legend_items:
                self.canvas.create_rectangle(legend_x, legend_y - 5, legend_x + 12, legend_y + 5,
                                            fill=color, outline="", tags="scene")
                self.canvas.create_text(legend_x + 16, legend_y, text=text,
                                       font=("微软雅黑", 8), fill="#2c3e50", 
                                       anchor="w", tags="scene")
                legend_x += 85
            
            # ===== 当前分区范围显示 =====
            if low >= 0 and high >= low:
                range_text = f"📍 当前分区: [{low}, {high}]  |  递归深度: {depth}"
                self.canvas.create_text((bar_area_left + bar_area_right) // 2, 60,
                                       text=range_text,
                                       font=("微软雅黑", 10, "bold"), fill="#e91e63",
                                       tags="scene")
                
                # 绘制分区范围背景（虚线框）
                range_left = get_bar_x(low) - 6
                range_right = get_bar_x(high) + bar_width + 6
                self.canvas.create_rectangle(range_left, bar_area_top - 15,
                                            range_right, bar_area_bottom + 25,
                                            fill="#fce4ec", outline="#e91e63", width=2,
                                            dash=(5, 3), tags="scene")
            
            # ===== 基准值显示区域（更醒目）=====
            if pivot_idx >= 0 and pivot_idx < len(arr):
                pivot_val = arr[pivot_idx]
                # 基准值显示框
                self.canvas.create_rectangle(460, 78, 615, 112,
                                            fill="#e1bee7", outline="#9b59b6", width=2,
                                            tags="scene")
                self.canvas.create_text(538, 95, text=f"🎯 pivot = {int(pivot_val)}",
                                       font=("微软雅黑", 11, "bold"), fill="#7b1fa2",
                                       tags="scene")
            
            # ===== 分区说明区域 =====
            if show_wall and i_ptr >= low - 1:
                # 显示分界线说明
                wall_x = get_bar_x(i_ptr) + bar_width + 4 if i_ptr >= low else get_bar_x(low) - 4
                
                # 分界说明文字
                if i_ptr >= low:
                    self.canvas.create_text(bar_area_left + 10, bar_area_top - 8,
                                           text="≤pivot区域",
                                           font=("微软雅黑", 8), fill="#27ae60",
                                           anchor="w", tags="scene")
                    
                    # 绘制分界线
                    self.canvas.create_line(wall_x, bar_area_top - 5, wall_x, bar_area_bottom + 5,
                                           fill="#ff9800", width=3, dash=(6, 3), tags="scene")
                    self.canvas.create_text(wall_x, bar_area_bottom + 18,
                                           text="分界线", font=("微软雅黑", 8, "bold"),
                                           fill="#ff9800", tags="scene")
            
            # ===== 绘制条形图 =====
            for idx, value in enumerate(arr):
                x = get_bar_x(idx)
                bar_height = get_bar_height(value)
                y_bottom = bar_area_bottom
                y_top = y_bottom - bar_height
                
                # 确定颜色（优先级排序）
                if idx in swap_pair:
                    color = "#e74c3c"  # 红色 - 正在交换
                    outline = "#c0392b"
                    line_width = 3
                elif idx == pivot_idx:
                    color = "#9b59b6"  # 紫色 - 基准元素
                    outline = "#7b1fa2"
                    line_width = 3
                elif idx in sorted_positions:
                    color = "#16a085"  # 青绿色 - 已排序到最终位置
                    outline = "#0e6655"
                    line_width = 2
                elif idx in less_region:
                    color = "#27ae60"  # 绿色 - 小于等于pivot的区域
                    outline = "#1e8449"
                    line_width = 2
                elif low <= idx <= high:
                    color = "#3498db"  # 蓝色 - 当前分区内
                    outline = "#2980b9"
                    line_width = 2
                else:
                    color = "#bdc3c7"  # 灰色 - 不在当前分区
                    outline = "#95a5a6"
                    line_width = 1
                
                # 绘制条形阴影
                shadow_offset = 3
                self.canvas.create_rectangle(x + shadow_offset, y_top + shadow_offset, 
                                            x + bar_width + shadow_offset, y_bottom + shadow_offset,
                                            fill="#95a5a6", outline="", tags="scene")
                
                # 绘制条形主体
                self.canvas.create_rectangle(x, y_top, x + bar_width, y_bottom,
                                            fill=color, outline=outline, width=line_width,
                                            tags="scene")
                
                # 条形内数值（大字）
                self.canvas.create_text(x + bar_width // 2, (y_top + y_bottom) // 2,
                                       text=f"{int(value)}",
                                       font=("Arial", 13, "bold"), fill="white",
                                       tags="scene")
                
                # 索引标签
                self.canvas.create_text(x + bar_width // 2, y_bottom + 15,
                                       text=f"[{idx}]",
                                       font=("Arial", 9), fill="#7f8c8d",
                                       tags="scene")
                
                # 指针标记（更醒目的箭头样式）
                if idx == i_ptr and i_ptr >= low:
                    # i 指针 - 黄色三角箭头
                    arrow_y = y_top - 25
                    cx = x + bar_width // 2
                    self.canvas.create_polygon(cx - 8, arrow_y - 10, cx + 8, arrow_y - 10,
                                              cx, arrow_y, fill="#f39c12", outline="#d68910",
                                              tags="scene")
                    self.canvas.create_text(cx, arrow_y - 18,
                                           text="i", font=("Arial", 10, "bold"), fill="#d68910",
                                           tags="scene")
                
                if idx == j_ptr:
                    # j 指针 - 蓝色三角箭头
                    arrow_y = y_top - 25 if idx != i_ptr else y_top - 45
                    cx = x + bar_width // 2
                    self.canvas.create_polygon(cx - 8, arrow_y - 10, cx + 8, arrow_y - 10,
                                              cx, arrow_y, fill="#3498db", outline="#2980b9",
                                              tags="scene")
                    self.canvas.create_text(cx, arrow_y - 18,
                                           text="j", font=("Arial", 10, "bold"), fill="#2980b9",
                                           tags="scene")
            
            # ===== 比较结果显示 =====
            if compare_result and j_ptr >= 0:
                cx = get_bar_x(j_ptr) + bar_width // 2
                if compare_result == "<=":
                    self.canvas.create_oval(cx - 15, bar_area_bottom + 35, cx + 15, bar_area_bottom + 55,
                                           fill="#d4edda", outline="#27ae60", width=2, tags="scene")
                    self.canvas.create_text(cx, bar_area_bottom + 45, text="✓",
                                           font=("Arial", 12, "bold"), fill="#27ae60", tags="scene")
                else:
                    self.canvas.create_oval(cx - 15, bar_area_bottom + 35, cx + 15, bar_area_bottom + 55,
                                           fill="#f8d7da", outline="#e74c3c", width=2, tags="scene")
                    self.canvas.create_text(cx, bar_area_bottom + 45, text="✗",
                                           font=("Arial", 12, "bold"), fill="#e74c3c", tags="scene")
            
            # ===== 右侧教学信息面板 =====
            panel_x = info_area_left
            panel_y = info_area_top
            panel_bottom = 370
            
            # 面板背景（带渐变效果模拟）
            self.canvas.create_rectangle(panel_x, panel_y, canvas_width - 10, panel_bottom,
                                        fill="#f8f9fa", outline="#dee2e6", width=2,
                                        tags="scene")
            
            # 状态标题栏
            self.canvas.create_rectangle(panel_x, panel_y, canvas_width - 10, panel_y + 32,
                                        fill="#e91e63", outline="", tags="scene")
            self.canvas.create_text(panel_x + 15, panel_y + 16, text="📌 快速排序状态",
                                   font=("微软雅黑", 11, "bold"), fill="white",
                                   anchor="w", tags="scene")
            
            # 递归信息
            depth_text = f"🔄 递归深度: {depth}  |  分区次数: {stats['partition_count']}"
            self.canvas.create_text(panel_x + 12, panel_y + 52,
                                   text=depth_text,
                                   font=("微软雅黑", 9), fill="#6c757d",
                                   anchor="w", tags="scene")
            
            # 分隔线
            self.canvas.create_line(panel_x + 8, panel_y + 68, canvas_width - 18, panel_y + 68,
                                   fill="#dee2e6", tags="scene")
            
            # 操作说明
            self.canvas.create_text(panel_x + 12, panel_y + 85, text="💡 当前操作",
                                   font=("微软雅黑", 10, "bold"), fill="#2c3e50",
                                   anchor="w", tags="scene")
            
            action_lines = action.split("\n") if action else ["等待开始..."]
            action_y = panel_y + 105
            for line in action_lines[:8]:
                # 为关键词添加颜色
                fill_color = "#495057"
                if "✓" in line or "✅" in line:
                    fill_color = "#27ae60"
                elif "✗" in line or "✘" in line:
                    fill_color = "#e74c3c"
                elif "🔀" in line or "交换" in line:
                    fill_color = "#e74c3c"
                elif "pivot" in line.lower() or "基准" in line:
                    fill_color = "#9b59b6"
                    
                self.canvas.create_text(panel_x + 12, action_y, text=line,
                                       font=("微软雅黑", 9), fill=fill_color,
                                       anchor="w", width=330, tags="scene")
                action_y += 17
            
            # 分隔线
            self.canvas.create_line(panel_x + 8, panel_y + 245, canvas_width - 18, panel_y + 245,
                                   fill="#dee2e6", tags="scene")
            
            # 统计信息区域
            self.canvas.create_text(panel_x + 12, panel_y + 262, text="📊 实时统计",
                                   font=("微软雅黑", 10, "bold"), fill="#2c3e50",
                                   anchor="w", tags="scene")
            
            # 比较次数（带图标）
            self.canvas.create_text(panel_x + 12, panel_y + 285,
                                   text=f"🔍 比较次数：{stats['compare']}",
                                   font=("微软雅黑", 10), fill="#17a2b8",
                                   anchor="w", tags="scene")
            
            # 交换次数（带图标）
            self.canvas.create_text(panel_x + 180, panel_y + 285,
                                   text=f"🔀 交换次数：{stats['swap']}",
                                   font=("微软雅黑", 10), fill="#dc3545",
                                   anchor="w", tags="scene")
            
            # 数组状态对比
            self.canvas.create_line(panel_x + 8, panel_y + 305, canvas_width - 18, panel_y + 305,
                                   fill="#dee2e6", tags="scene")
            
            self.canvas.create_text(panel_x + 12, panel_y + 322,
                                   text=f"原始：{[int(x) for x in original_data]}",
                                   font=("Consolas", 8), fill="#6c757d",
                                   anchor="w", tags="scene")
            self.canvas.create_text(panel_x + 12, panel_y + 342,
                                   text=f"当前：{[int(x) for x in arr]}",
                                   font=("Consolas", 8), fill="#28a745",
                                   anchor="w", tags="scene")
            
            self.window.update()
        
        def animate_swap(arr, idx1, idx2, low, high, pivot_idx, depth):
            """执行交换动画 - 元素上升、交叉移动、下降"""
            x1 = get_bar_x(idx1)
            x2 = get_bar_x(idx2)
            val1, val2 = arr[idx1], arr[idx2]
            h1, h2 = get_bar_height(val1), get_bar_height(val2)
            
            # 阶段1: 两个元素同时上升
            for step in range(8):
                self.canvas.delete("swap_anim")
                offset_y = step * 6
                
                for pos, val, h in [(x1, val1, h1), (x2, val2, h2)]:
                    y_bottom = bar_area_bottom - offset_y
                    y_top = y_bottom - h
                    
                    self.canvas.create_rectangle(pos, y_top, pos + bar_width, y_bottom,
                                                fill="#e74c3c", outline="#c0392b", width=3,
                                                tags="swap_anim")
                    self.canvas.create_text(pos + bar_width // 2, (y_top + y_bottom) // 2,
                                           text=f"{int(val)}",
                                           font=("Arial", 13, "bold"), fill="white",
                                           tags="swap_anim")
                
                self.window.update()
                time.sleep(0.025)
            
            # 阶段2: 水平交叉移动
            distance = x2 - x1
            for step in range(15):
                self.canvas.delete("swap_anim")
                progress = step / 14
                
                # 左边元素向右移
                pos1 = x1 + progress * distance
                y_bottom = bar_area_bottom - 48
                y_top = y_bottom - h1
                self.canvas.create_rectangle(pos1, y_top, pos1 + bar_width, y_bottom,
                                            fill="#e74c3c", outline="#c0392b", width=3,
                                            tags="swap_anim")
                self.canvas.create_text(pos1 + bar_width // 2, (y_top + y_bottom) // 2,
                                       text=f"{int(val1)}",
                                       font=("Arial", 13, "bold"), fill="white",
                                       tags="swap_anim")
                
                # 右边元素向左移
                pos2 = x2 - progress * distance
                y_top = y_bottom - h2
                self.canvas.create_rectangle(pos2, y_top, pos2 + bar_width, y_bottom,
                                            fill="#e74c3c", outline="#c0392b", width=3,
                                            tags="swap_anim")
                self.canvas.create_text(pos2 + bar_width // 2, (y_top + y_bottom) // 2,
                                       text=f"{int(val2)}",
                                       font=("Arial", 13, "bold"), fill="white",
                                       tags="swap_anim")
                
                self.window.update()
                time.sleep(0.025)
            
            # 执行实际交换
            arr[idx1], arr[idx2] = arr[idx2], arr[idx1]
            
            # 阶段3: 下降回位
            for step in range(8):
                self.canvas.delete("swap_anim")
                offset_y = 48 - step * 6
                
                # 注意：位置已经交换
                for pos, val, h in [(x1, val2, h2), (x2, val1, h1)]:
                    y_bottom = bar_area_bottom - offset_y
                    y_top = y_bottom - h
                    
                    self.canvas.create_rectangle(pos, y_top, pos + bar_width, y_bottom,
                                                fill="#e74c3c", outline="#c0392b", width=3,
                                                tags="swap_anim")
                    self.canvas.create_text(pos + bar_width // 2, (y_top + y_bottom) // 2,
                                           text=f"{int(val)}",
                                           font=("Arial", 13, "bold"), fill="white",
                                           tags="swap_anim")
                
                self.window.update()
                time.sleep(0.025)
            
            self.canvas.delete("swap_anim")
        
        def partition_animated(arr, low, high, depth):
            """分区操作（带详细动画）"""
            stats["partition_count"] += 1
            pivot = arr[high]
            pivot_idx = high
            less_region = set()  # 记录小于等于pivot的元素位置
            
            # 步骤1：显示分区开始，选择基准
            self.highlight_pseudo_line(11)
            draw_quick_scene(arr, low, high, pivot_idx=pivot_idx, depth=depth,
                           action=f"📋 开始分区操作 Partition\n\n分区范围：[{low}, {high}]\n元素个数：{high - low + 1}")
            time.sleep(0.8)
            
            self.highlight_pseudo_line(12)
            draw_quick_scene(arr, low, high, pivot_idx=pivot_idx, depth=depth,
                           action=f"🎯 选择基准元素\n\npivot = arr[{high}] = {int(pivot)}\n\n💡 说明：\n选择数组最后一个元素作为基准\n接下来将数组分成两部分：\n  左边：≤ {int(pivot)}\n  右边：> {int(pivot)}")
            time.sleep(1.2)
            
            i = low - 1  # 小于pivot的区域的右边界
            
            self.highlight_pseudo_line(13)
            draw_quick_scene(arr, low, high, pivot_idx=pivot_idx, i_ptr=i, depth=depth, show_wall=True,
                           action=f"🔧 初始化分界指针 i\n\ni = {low} - 1 = {i}\n\n💡 说明：\ni 指向「≤pivot区域」的右边界\n初始时 i 在 low 的左边\n表示还没有找到任何 ≤pivot 的元素")
            time.sleep(1.0)
            
            # 遍历 [low, high-1]
            self.highlight_pseudo_line(14)
            for j in range(low, high):
                stats["compare"] += 1
                
                # 显示 j 扫描
                draw_quick_scene(arr, low, high, pivot_idx=pivot_idx, i_ptr=i, j_ptr=j, 
                               depth=depth, show_wall=True, less_region=less_region,
                               action=f"👀 j 扫描到位置 [{j}]\n\n正在检查：arr[{j}] = {int(arr[j])}\n基准值：pivot = {int(pivot)}\n\n❓ 问题：\n{int(arr[j])} ≤ {int(pivot)} 吗？")
                time.sleep(0.6)
                
                self.highlight_pseudo_line(15)
                if arr[j] <= pivot:
                    self.highlight_pseudo_line(16)
                    i += 1
                    
                    # 显示比较结果：满足条件
                    draw_quick_scene(arr, low, high, pivot_idx=pivot_idx, i_ptr=i, j_ptr=j, 
                                   depth=depth, show_wall=True, compare_result="<=", less_region=less_region,
                                   action=f"✅ 是的！{int(arr[j])} ≤ {int(pivot)}\n\n执行：i++ → i = {i}\n这个元素应该放到「≤pivot区域」")
                    time.sleep(0.5)
                    
                    if i != j:
                        # 需要交换
                        draw_quick_scene(arr, low, high, pivot_idx=pivot_idx, i_ptr=i, j_ptr=j,
                                       swap_pair=[i, j], depth=depth, less_region=less_region,
                                       action=f"🔀 需要交换！\n\n交换 arr[{i}] 和 arr[{j}]\n即：{int(arr[i])} ⟷ {int(arr[j])}\n\n💡 目的：\n把小元素 {int(arr[j])} 移到左边区域")
                        time.sleep(0.4)
                        
                        # 执行交换动画
                        animate_swap(arr, i, j, low, high, pivot_idx, depth)
                        stats["swap"] += 1
                        
                        # 更新 pivot_idx 如果基准被交换
                        if pivot_idx == i:
                            pivot_idx = j
                        elif pivot_idx == j:
                            pivot_idx = i
                        
                        less_region.add(i)
                        draw_quick_scene(arr, low, high, pivot_idx=pivot_idx, i_ptr=i, j_ptr=j, 
                                       depth=depth, show_wall=True, less_region=less_region,
                                       action=f"✓ 交换完成！\n\n现在 arr[{i}] = {int(arr[i])}\n「≤pivot区域」扩展了一位")
                        time.sleep(0.4)
                    else:
                        less_region.add(i)
                        draw_quick_scene(arr, low, high, pivot_idx=pivot_idx, i_ptr=i, j_ptr=j, 
                                       depth=depth, show_wall=True, less_region=less_region,
                                       action=f"✓ 元素已在正确位置\n\narr[{i}] = {int(arr[i])} 已经在左边\n无需交换，i 和 j 指向同一位置")
                        time.sleep(0.4)
                else:
                    # 不满足条件
                    draw_quick_scene(arr, low, high, pivot_idx=pivot_idx, i_ptr=i, j_ptr=j, 
                                   depth=depth, show_wall=True, compare_result=">", less_region=less_region,
                                   action=f"✗ 不是！{int(arr[j])} > {int(pivot)}\n\n这个元素比基准大\n暂时留在原位，j 继续前进\n最终它会在基准的右边")
                    time.sleep(0.5)
            
            # 将pivot放到正确位置
            self.highlight_pseudo_line(17)
            final_pivot_pos = i + 1
            
            draw_quick_scene(arr, low, high, pivot_idx=pivot_idx, i_ptr=i, 
                           depth=depth, show_wall=True, less_region=less_region,
                           action=f"📍 扫描完成！\n\n现在需要把基准放到正确位置\n最终位置 = i + 1 = {final_pivot_pos}\n\n💡 为什么？\n位置 {final_pivot_pos} 左边都 ≤ pivot\n位置 {final_pivot_pos} 右边都 > pivot")
            time.sleep(0.8)
            
            if final_pivot_pos != high:
                draw_quick_scene(arr, low, high, pivot_idx=pivot_idx, i_ptr=i, 
                               depth=depth, swap_pair=[final_pivot_pos, high], less_region=less_region,
                               action=f"🔀 放置基准到最终位置\n\n交换 arr[{final_pivot_pos}] 和 arr[{high}]\n即：{int(arr[final_pivot_pos])} ⟷ {int(pivot)}")
                time.sleep(0.5)
                
                # 交换动画
                animate_swap(arr, final_pivot_pos, high, low, high, pivot_idx, depth)
                stats["swap"] += 1
            
            # 标记基准位置已排序
            sorted_positions.add(final_pivot_pos)
            
            self.highlight_pseudo_line(18)
            draw_quick_scene(arr, low, high, pivot_idx=final_pivot_pos, depth=depth,
                           action=f"🎉 分区完成！\n\n基准 {int(pivot)} 已在最终位置 [{final_pivot_pos}]\n\n📊 分区结果：\n  左边 [{low}-{final_pivot_pos-1}]：都 ≤ {int(pivot)}\n  右边 [{final_pivot_pos+1}-{high}]：都 > {int(pivot)}\n\n✨ 基准元素位置确定！")
            time.sleep(1.0)
            
            return final_pivot_pos
        
        def quick_sort_animated(arr, low, high, depth=0):
            """快速排序递归（带详细动画）"""
            if depth > stats["recursion_depth"]:
                stats["recursion_depth"] = depth
            
            self.highlight_pseudo_line(6)
            if low < high:
                subarray = [int(arr[k]) for k in range(low, high+1)]
                draw_quick_scene(arr, low, high, depth=depth,
                               action=f"🔄 递归调用 QuickSort\n\nQuickSort(arr, {low}, {high})\n递归深度：{depth}\n\n📋 待排序子数组：\n{subarray}\n共 {high - low + 1} 个元素")
                time.sleep(0.8)
                
                # 分区
                self.highlight_pseudo_line(7)
                pivot_idx = partition_animated(arr, low, high, depth)
                
                # 递归排序左半部分
                if low < pivot_idx - 1:
                    self.highlight_pseudo_line(8)
                    left_sub = [int(arr[k]) for k in range(low, pivot_idx)]
                    draw_quick_scene(arr, low, pivot_idx - 1, depth=depth+1,
                                   action=f"⬅️ 递归排序左半部分\n\nQuickSort(arr, {low}, {pivot_idx - 1})\n\n💡 处理基准左边的元素：\n{left_sub}")
                    time.sleep(0.6)
                    quick_sort_animated(arr, low, pivot_idx - 1, depth + 1)
                elif low == pivot_idx - 1:
                    sorted_positions.add(low)
                    draw_quick_scene(arr, low, low, depth=depth+1,
                                   action=f"⬅️ 左边只有一个元素\n\narr[{low}] = {int(arr[low])}\n单个元素无需排序\n直接标记为已排序 ✓")
                    time.sleep(0.5)
                elif low == pivot_idx:
                    draw_quick_scene(arr, depth=depth,
                                   action=f"⬅️ 左边没有元素\n\n基准已经是最小的\n无需处理左半部分")
                    time.sleep(0.4)
                
                # 递归排序右半部分
                if pivot_idx + 1 < high:
                    self.highlight_pseudo_line(9)
                    right_sub = [int(arr[k]) for k in range(pivot_idx + 1, high + 1)]
                    draw_quick_scene(arr, pivot_idx + 1, high, depth=depth+1,
                                   action=f"➡️ 递归排序右半部分\n\nQuickSort(arr, {pivot_idx + 1}, {high})\n\n💡 处理基准右边的元素：\n{right_sub}")
                    time.sleep(0.6)
                    quick_sort_animated(arr, pivot_idx + 1, high, depth + 1)
                elif pivot_idx + 1 == high:
                    sorted_positions.add(high)
                    draw_quick_scene(arr, high, high, depth=depth+1,
                                   action=f"➡️ 右边只有一个元素\n\narr[{high}] = {int(arr[high])}\n单个元素无需排序\n直接标记为已排序 ✓")
                    time.sleep(0.5)
                elif pivot_idx == high:
                    draw_quick_scene(arr, depth=depth,
                                   action=f"➡️ 右边没有元素\n\n基准已经是最大的\n无需处理右半部分")
                    time.sleep(0.4)
                    
            elif low == high:
                sorted_positions.add(low)
                draw_quick_scene(arr, low, high, depth=depth,
                               action=f"✅ 子数组只有一个元素\n\narr[{low}] = {int(arr[low])}\n\n单个元素天然有序\n标记为已排序完成")
                time.sleep(0.5)
        
        # ===== 开始教学演示 =====
        self.highlight_pseudo_line(0)
        draw_quick_scene(data, action="🎬 快速排序教学开始！\n\n⚡ 快速排序是最重要的排序算法之一\n   平均时间复杂度 O(n log n)\n\n📚 核心思想：分治法\n   1. 选择一个基准元素 (pivot)\n   2. 分区：小的放左边，大的放右边\n   3. 递归处理左右两部分")
        time.sleep(2.0)
        
        self.highlight_pseudo_line(1)
        self.highlight_pseudo_line(2)
        self.highlight_pseudo_line(3)
        draw_quick_scene(data, action="📖 算法步骤详解：\n\n步骤1️⃣ 选择基准\n   通常选最后一个元素\n\n步骤2️⃣ 分区 (Partition)\n   把数组分成两部分\n\n步骤3️⃣ 递归\n   对左右两部分重复上述过程")
        time.sleep(1.5)
        
        self.highlight_pseudo_line(5)
        draw_quick_scene(data, 0, n-1, action=f"📋 初始数组\n\n{[int(x) for x in data]}\n共 {n} 个元素\n\n🚀 开始排序！\n调用 QuickSort(arr, 0, {n-1})")
        time.sleep(1.0)
        
        # 执行快速排序
        quick_sort_animated(data, 0, n - 1, 0)
        
        # 排序完成
        sorted_positions = set(range(n))
        draw_quick_scene(data, action=f"🏆 排序完成！\n\n✨ 快速排序成功！\n\n📊 统计结果：\n   比较次数：{stats['compare']}\n   交换次数：{stats['swap']}\n   分区次数：{stats['partition_count']}\n   最大递归深度：{stats['recursion_depth']}\n\n🎯 时间复杂度：O(n log n)")
        
        self.complete_pseudo_code()
        
        # 更新模型数据
        self.model.data = [str(int(x)) if x == int(x) else str(x) for x in data]
        
        # 添加操作历史
        self.add_operation_history(f"快速排序完成: 比较{stats['compare']}次, 交换{stats['swap']}次")
        
        # 显示精美总结页面
        time.sleep(2.0)
        self.canvas.delete("scene")
        self._draw_quick_sort_summary(original_data, data, stats, n)
        
        # 等待用户查看总结
        time.sleep(5)
        self.update_display()
    
    def _draw_quick_sort_summary(self, original_data, sorted_data, stats, n):
        """绘制快速排序的精美学习总结页面（增强版）"""
        canvas_width = 1000
        canvas_height = 380
        
        # ===== 背景渐变效果（深紫色主题）=====
        for i in range(canvas_height):
            ratio = i / canvas_height
            r = int(30 + ratio * 15)
            g = int(15 + ratio * 20)
            b = int(45 + ratio * 35)
            color = f"#{r:02x}{g:02x}{b:02x}"
            self.canvas.create_line(0, i, canvas_width, i, fill=color, tags="scene")
        
        # ===== 顶部装饰条（渐变效果）=====
        self.canvas.create_rectangle(0, 0, canvas_width, 6, fill="#e91e63", outline="", tags="scene")
        self.canvas.create_rectangle(0, 6, canvas_width, 8, fill="#f48fb1", outline="", tags="scene")
        
        # ===== 标题区域 =====
        # 光晕背景
        self.canvas.create_oval(canvas_width//2 - 220, -40, canvas_width//2 + 220, 75,
                               fill="#4a1942", outline="", tags="scene")
        
        self.canvas.create_text(canvas_width // 2, 32, 
                               text="🎓 快速排序 · 学习总结",
                               font=("微软雅黑", 20, "bold"), fill="#ffffff", tags="scene")
        
        # 装饰线
        self.canvas.create_line(canvas_width//2 - 160, 52, canvas_width//2 + 160, 52,
                               fill="#e91e63", width=2, tags="scene")
        
        # ===== 成就徽章（更精美）=====
        badge_x, badge_y = 900, 45
        # 外圈光晕
        self.canvas.create_oval(badge_x - 45, badge_y - 45, badge_x + 45, badge_y + 45,
                               fill="#5d1049", outline="", tags="scene")
        # 主圈
        self.canvas.create_oval(badge_x - 38, badge_y - 38, badge_x + 38, badge_y + 38,
                               fill="#e91e63", outline="#ad1457", width=3, tags="scene")
        # 内圈
        self.canvas.create_oval(badge_x - 28, badge_y - 28, badge_x + 28, badge_y + 28,
                               fill="#fce4ec", outline="#e91e63", width=2, tags="scene")
        self.canvas.create_text(badge_x, badge_y - 6, text="⚡",
                               font=("Arial", 18, "bold"), fill="#c2185b", tags="scene")
        self.canvas.create_text(badge_x, badge_y + 18, text="高效",
                               font=("微软雅黑", 8, "bold"), fill="#880e4f", tags="scene")
        
        # ===== 左侧：算法知识卡片 =====
        card1_x, card1_y = 30, 70
        card1_w, card1_h = 310, 295
        
        # 卡片阴影
        self.canvas.create_rectangle(card1_x + 4, card1_y + 4, 
                                    card1_x + card1_w + 4, card1_y + card1_h + 4,
                                    fill="#0f172a", outline="", tags="scene")
        # 卡片主体
        self.canvas.create_rectangle(card1_x, card1_y, card1_x + card1_w, card1_y + card1_h,
                                    fill="#1e293b", outline="#334155", width=2, tags="scene")
        
        # 卡片标题栏
        self.canvas.create_rectangle(card1_x, card1_y, card1_x + card1_w, card1_y + 35,
                                    fill="#e91e63", outline="", tags="scene")
        self.canvas.create_text(card1_x + card1_w//2, card1_y + 18, text="📚 快速排序知识要点",
                               font=("微软雅黑", 11, "bold"), fill="#ffffff", tags="scene")
        
        knowledge_items = [
            ("💡 核心思想", "分治法 (Divide & Conquer)\n选基准 → 分区 → 递归排序", "#f48fb1"),
            ("⏱️ 时间复杂度", "最好/平均：O(n log n)\n最坏：O(n²) 有序数组时", "#ce93d8"),
            ("💾 空间复杂度", "O(log n) - 递归调用栈\n原地排序，不需额外数组", "#90caf9"),
            ("⚖️ 稳定性", "不稳定排序\n相等元素可能改变相对顺序", "#ffcc80"),
        ]
        
        ky = card1_y + 52
        for title, content, color in knowledge_items:
            # 彩色标记条
            self.canvas.create_rectangle(card1_x + 10, ky, card1_x + 14, ky + 40,
                                        fill=color, outline="", tags="scene")
            # 标题
            self.canvas.create_text(card1_x + 22, ky + 8, text=title,
                                   font=("微软雅黑", 9, "bold"), fill="#e2e8f0",
                                   anchor="w", tags="scene")
            # 内容
            self.canvas.create_text(card1_x + 22, ky + 35, text=content,
                                   font=("微软雅黑", 8), fill="#94a3b8",
                                   anchor="w", width=275, tags="scene")
            ky += 58
        
        # ===== 中间上方：统计数据卡片 =====
        card2_x, card2_y = 360, 70
        card2_w, card2_h = 280, 150
        
        self.canvas.create_rectangle(card2_x + 4, card2_y + 4, 
                                    card2_x + card2_w + 4, card2_y + card2_h + 4,
                                    fill="#0f172a", outline="", tags="scene")
        self.canvas.create_rectangle(card2_x, card2_y, card2_x + card2_w, card2_y + card2_h,
                                    fill="#1e293b", outline="#334155", width=2, tags="scene")
        
        self.canvas.create_rectangle(card2_x, card2_y, card2_x + card2_w, card2_y + 32,
                                    fill="#7c4dff", outline="", tags="scene")
        self.canvas.create_text(card2_x + card2_w//2, card2_y + 16, text="📊 本次排序统计",
                               font=("微软雅黑", 10, "bold"), fill="#ffffff", tags="scene")
        
        # 统计数据网格
        stat_y = card2_y + 48
        stat_items = [
            ("🔍 比较次数", stats['compare'], "#64b5f6"),
            ("🔀 交换次数", stats['swap'], "#ef5350"),
            ("📦 分区次数", stats['partition_count'], "#81c784"),
            ("📈 递归深度", stats['recursion_depth'], "#ffb74d"),
        ]
        
        for idx, (label, value, color) in enumerate(stat_items):
            col = idx % 2
            row = idx // 2
            x = card2_x + 15 + col * 135
            y = stat_y + row * 40
            
            self.canvas.create_text(x, y, text=label,
                                   font=("微软雅黑", 9), fill="#94a3b8", anchor="w", tags="scene")
            self.canvas.create_text(x + 90, y, text=str(value),
                                   font=("Consolas", 12, "bold"), fill=color, anchor="w", tags="scene")
        
        # ===== 中间下方：算法特点与优化卡片 =====
        card3_x, card3_y = 360, 230
        card3_w, card3_h = 280, 132
        
        self.canvas.create_rectangle(card3_x + 4, card3_y + 4, 
                                    card3_x + card3_w + 4, card3_y + card3_h + 4,
                                    fill="#0f172a", outline="", tags="scene")
        self.canvas.create_rectangle(card3_x, card3_y, card3_x + card3_w, card3_y + card3_h,
                                    fill="#1e293b", outline="#334155", width=2, tags="scene")
        
        self.canvas.create_rectangle(card3_x, card3_y, card3_x + card3_w, card3_y + 32,
                                    fill="#ff7043", outline="", tags="scene")
        self.canvas.create_text(card3_x + card3_w//2, card3_y + 16, text="💡 算法优势与优化",
                               font=("微软雅黑", 10, "bold"), fill="#ffffff", tags="scene")
        
        tips = [
            "✨ 实际应用中最快的排序算法之一",
            "🎯 原地排序，空间效率高",
            "🔄 随机选基准可避免最坏情况",
            "📊 小数组可切换为插入排序",
        ]
        tip_y = card3_y + 48
        for tip in tips:
            self.canvas.create_text(card3_x + 12, tip_y, text=tip,
                                   font=("微软雅黑", 8), fill="#ffab91",
                                   anchor="w", tags="scene")
            tip_y += 22
        
        # ===== 右侧：排序前后对比卡片 =====
        card4_x, card4_y = 660, 70
        card4_w, card4_h = 325, 295
        
        self.canvas.create_rectangle(card4_x + 4, card4_y + 4, 
                                    card4_x + card4_w + 4, card4_y + card4_h + 4,
                                    fill="#0f172a", outline="", tags="scene")
        self.canvas.create_rectangle(card4_x, card4_y, card4_x + card4_w, card4_y + card4_h,
                                    fill="#1e293b", outline="#334155", width=2, tags="scene")
        
        self.canvas.create_rectangle(card4_x, card4_y, card4_x + card4_w, card4_y + 32,
                                    fill="#26c6da", outline="", tags="scene")
        self.canvas.create_text(card4_x + card4_w//2, card4_y + 16, text="📈 排序前后对比",
                               font=("微软雅黑", 10, "bold"), fill="#ffffff", tags="scene")
        
        # 条形图区域
        bar_area_top = card4_y + 48
        bar_area_height = 90
        bar_width = min(22, (card4_w - 70) // max(1, len(original_data)) - 4)
        
        max_val = max(max(original_data), max(sorted_data))
        min_val = min(min(original_data), min(sorted_data))
        val_range = max_val - min_val if max_val != min_val else 1
        
        def draw_mini_bars(data_list, start_y, label, label_color, bar_color, highlight_color):
            # 标签
            self.canvas.create_text(card4_x + 12, start_y + bar_area_height // 2, text=label,
                                   font=("微软雅黑", 8, "bold"), fill=label_color,
                                   anchor="w", tags="scene")
            bar_start_x = card4_x + 55
            for i, val in enumerate(data_list):
                height = max(12, int(((val - min_val) / val_range) * (bar_area_height - 25) + 12))
                x = bar_start_x + i * (bar_width + 4)
                y_bottom = start_y + bar_area_height - 8
                y_top = y_bottom - height
                
                # 条形阴影
                self.canvas.create_rectangle(x + 2, y_top + 2, x + bar_width + 2, y_bottom + 2,
                                            fill="#1a1a2e", outline="", tags="scene")
                # 条形主体
                self.canvas.create_rectangle(x, y_top, x + bar_width, y_bottom,
                                            fill=bar_color, outline=highlight_color, width=1, tags="scene")
                # 数值标签
                self.canvas.create_text(x + bar_width // 2, y_top - 8, text=str(int(val)),
                                       font=("Consolas", 7, "bold"), fill="#e2e8f0", tags="scene")
        
        # 绘制排序前
        draw_mini_bars(original_data, bar_area_top, "排序前", "#ef5350", "#e53935", "#c62828")
        
        # 箭头和标签
        arrow_y = bar_area_top + bar_area_height + 8
        self.canvas.create_text(card4_x + card4_w // 2, arrow_y, text="⬇️  快速排序  ⬇️",
                               font=("微软雅黑", 9, "bold"), fill="#e91e63", tags="scene")
        
        # 绘制排序后
        draw_mini_bars(sorted_data, arrow_y + 12, "排序后", "#66bb6a", "#43a047", "#2e7d32")
        
        # 数组文字对比
        text_y = arrow_y + bar_area_height + 25
        self.canvas.create_text(card4_x + card4_w // 2, text_y,
                               text=f"原始：{[int(x) for x in original_data]}",
                               font=("Consolas", 8), fill="#ef5350", tags="scene")
        self.canvas.create_text(card4_x + card4_w // 2, text_y + 16,
                               text=f"排序：{[int(x) for x in sorted_data]}",
                               font=("Consolas", 8), fill="#66bb6a", tags="scene")
        
        # ===== 底部装饰与鼓励语 =====
        # 底部渐变装饰条
        self.canvas.create_rectangle(0, canvas_height - 25, canvas_width, canvas_height,
                                    fill="#2d1f3d", outline="", tags="scene")
        self.canvas.create_line(0, canvas_height - 25, canvas_width, canvas_height - 25,
                               fill="#e91e63", width=1, tags="scene")
        
        self.canvas.create_text(canvas_width // 2, canvas_height - 12,
                               text="🎉 恭喜你掌握了快速排序！这是面试必考、工程必备的核心算法！ 🚀",
                               font=("微软雅黑", 10, "bold"), fill="#f48fb1", tags="scene")
        
        self.window.update()

    # ==================== 顺序表逆置可视化（教学版） ====================
    
    def start_reverse(self):
        """启动顺序表逆置可视化 - 教学版"""
        if len(self.data_store) < 2:
            messagebox.showinfo("提示", "顺序表元素少于2个，无需逆置")
            return
        
        self.disable_buttons()
        self.animate_reverse_teaching()
        self.enable_buttons()
    
    def animate_reverse_teaching(self):
        """顺序表逆置教学演示 - 详细步骤说明版"""
        data = list(self.data_store)  # 复制当前数据
        n = len(data)
        original_data = data.copy()
        
        # 设置教学伪代码
        pseudo_lines = [
            "【顺序表逆置原理】",
            "将顺序表中的元素前后颠倒",
            "第一个与最后一个交换",
            "第二个与倒数第二个交换...",
            "直到中间位置停止",
            "─────────────────",
            f"for i = 0 to {n//2 - 1}:  // 遍历前半部分",
            f"  j = n - 1 - i  // 计算对称位置",
            "  swap(data[i], data[j])  // 交换两端元素",
            "// 逆置完成"
        ]
        self.set_pseudo_code("🎓 顺序表逆置教学演示", pseudo_lines)
        
        # 清空画布
        self.canvas.delete("all")
        
        # ===== 布局参数 =====
        canvas_width = 1000
        canvas_height = 380
        
        # 条形图区域
        bar_area_left = 50
        bar_area_right = 620
        bar_area_top = 130
        bar_area_bottom = 320
        
        # 教学说明区域
        info_area_left = 640
        info_area_top = 10
        
        # 计算条形参数
        bar_area_width = bar_area_right - bar_area_left
        bar_width = max(35, min(60, (bar_area_width - 20) // n - 10))
        total_bars_width = n * bar_width + (n - 1) * 10
        bar_start_x = bar_area_left + (bar_area_width - total_bars_width) // 2
        
        # 统计
        stats = {"swap": 0}
        
        # 已完成交换的位置集合
        swapped_positions = set()
        
        def get_bar_x(index):
            """获取条形的X坐标"""
            return bar_start_x + index * (bar_width + 10)
        
        def get_bar_height(value):
            """计算条形高度（基于字符串长度或数值）"""
            try:
                # 尝试转换为数字
                num_val = float(value)
                # 如果都是数字，根据数值计算高度
                all_numeric = all(self._is_numeric(v) for v in data)
                if all_numeric:
                    values = [float(v) for v in data]
                    max_val = max(values)
                    min_val = min(values)
                    val_range = max_val - min_val if max_val != min_val else 1
                    normalized = (num_val - min_val) / val_range
                    return max(40, int(normalized * 120 + 40))
            except (ValueError, TypeError):
                pass
            # 非数字，使用固定高度
            return 80
        
        def draw_reverse_scene(arr, left_idx=-1, right_idx=-1, swap_highlight=False,
                              action="", current_step=0, total_steps=0):
            """绘制逆置场景"""
            self.canvas.delete("scene")
            
            # ===== 标题 =====
            self.canvas.create_text(20, 18,
                                   text="🔄 顺序表逆置 · 教学演示",
                                   font=("微软雅黑", 14, "bold"), fill="#2c3e50",
                                   anchor="w", tags="scene")
            
            # ===== 颜色图例 =====
            legend_y = 42
            legend_items = [
                ("🔵 未处理", "#3498db"),
                ("🟡 当前交换", "#f1c40f"),
                ("🔴 交换中", "#e74c3c"),
                ("🟢 已完成", "#27ae60"),
            ]
            legend_x = 20
            for text, color in legend_items:
                self.canvas.create_rectangle(legend_x, legend_y - 6, legend_x + 12, legend_y + 6,
                                            fill=color, outline="", tags="scene")
                self.canvas.create_text(legend_x + 16, legend_y, text=text,
                                       font=("微软雅黑", 8), fill="#2c3e50", 
                                       anchor="w", tags="scene")
                legend_x += 90
            
            # ===== 当前交换对显示 =====
            if left_idx >= 0 and right_idx >= 0:
                pair_text = f"📍 当前交换对: [{left_idx}] ⟷ [{right_idx}]"
                self.canvas.create_text((bar_area_left + bar_area_right) // 2, 70,
                                       text=pair_text,
                                       font=("微软雅黑", 11, "bold"), fill="#e91e63",
                                       tags="scene")
            
            # ===== 绘制连接弧线（交换对之间）=====
            if left_idx >= 0 and right_idx >= 0 and left_idx < right_idx:
                x1 = get_bar_x(left_idx) + bar_width // 2
                x2 = get_bar_x(right_idx) + bar_width // 2
                arc_y = bar_area_top - 25
                mid_x = (x1 + x2) // 2
                
                # 绘制弧线
                arc_color = "#e74c3c" if swap_highlight else "#f39c12"
                # 使用多段线模拟弧线
                points = []
                for t in range(21):
                    ratio = t / 20.0
                    x = x1 + (x2 - x1) * ratio
                    # 抛物线形状
                    y = arc_y - 30 * (1 - (2 * ratio - 1) ** 2)
                    points.extend([x, y])
                
                if len(points) >= 4:
                    self.canvas.create_line(points, fill=arc_color, width=3,
                                           smooth=True, tags="scene")
                
                # 交换符号
                self.canvas.create_text(mid_x, arc_y - 35, text="⟷",
                                       font=("Arial", 16, "bold"), fill=arc_color,
                                       tags="scene")
            
            # ===== 绘制元素条形图 =====
            for i, value in enumerate(arr):
                x = get_bar_x(i)
                bar_height = get_bar_height(value)
                y_bottom = bar_area_bottom
                y_top = y_bottom - bar_height
                
                # 确定颜色
                if swap_highlight and i in [left_idx, right_idx]:
                    color = "#e74c3c"  # 红色 - 正在交换
                    outline = "#c0392b"
                    line_width = 3
                elif i in [left_idx, right_idx]:
                    color = "#f1c40f"  # 黄色 - 当前选中
                    outline = "#f39c12"
                    line_width = 3
                elif i in swapped_positions:
                    color = "#27ae60"  # 绿色 - 已完成
                    outline = "#1e8449"
                    line_width = 2
                else:
                    color = "#3498db"  # 蓝色 - 未处理
                    outline = "#2980b9"
                    line_width = 2
                
                # 绘制阴影
                shadow_offset = 3
                self.canvas.create_rectangle(x + shadow_offset, y_top + shadow_offset, 
                                            x + bar_width + shadow_offset, y_bottom + shadow_offset,
                                            fill="#bdc3c7", outline="", tags="scene")
                
                # 绘制主体
                self.canvas.create_rectangle(x, y_top, x + bar_width, y_bottom,
                                            fill=color, outline=outline, width=line_width,
                                            tags="scene")
                
                # 元素值
                display_val = str(value)
                if len(display_val) > 5:
                    display_val = display_val[:4] + ".."
                self.canvas.create_text(x + bar_width // 2, (y_top + y_bottom) // 2,
                                       text=display_val,
                                       font=("Arial", 12, "bold"), fill="white",
                                       tags="scene")
                
                # 索引标签
                self.canvas.create_text(x + bar_width // 2, y_bottom + 15,
                                       text=f"[{i}]",
                                       font=("Arial", 10), fill="#7f8c8d",
                                       tags="scene")
                
                # 指针标记
                if i == left_idx:
                    self.canvas.create_text(x + bar_width // 2, y_top - 15,
                                           text="◀ i",
                                           font=("Arial", 10, "bold"), fill="#e74c3c",
                                           tags="scene")
                if i == right_idx:
                    self.canvas.create_text(x + bar_width // 2, y_top - 15,
                                           text="j ▶",
                                           font=("Arial", 10, "bold"), fill="#9b59b6",
                                           tags="scene")
            
            # ===== 右侧教学信息面板 =====
            panel_x = info_area_left
            panel_y = info_area_top
            panel_bottom = 370
            
            # 面板背景
            self.canvas.create_rectangle(panel_x, panel_y, canvas_width - 10, panel_bottom,
                                        fill="#f8f9fa", outline="#dee2e6", width=2,
                                        tags="scene")
            
            # 标题栏
            self.canvas.create_rectangle(panel_x, panel_y, canvas_width - 10, panel_y + 32,
                                        fill="#00bcd4", outline="", tags="scene")
            self.canvas.create_text(panel_x + 15, panel_y + 16, text="📌 逆置操作状态",
                                   font=("微软雅黑", 11, "bold"), fill="white",
                                   anchor="w", tags="scene")
            
            # 进度信息
            progress_text = f"🔄 进度: {current_step} / {total_steps} 次交换"
            self.canvas.create_text(panel_x + 12, panel_y + 52,
                                   text=progress_text,
                                   font=("微软雅黑", 10), fill="#6c757d",
                                   anchor="w", tags="scene")
            
            # 分隔线
            self.canvas.create_line(panel_x + 8, panel_y + 68, canvas_width - 18, panel_y + 68,
                                   fill="#dee2e6", tags="scene")
            
            # 操作说明
            self.canvas.create_text(panel_x + 12, panel_y + 85, text="💡 当前操作",
                                   font=("微软雅黑", 10, "bold"), fill="#2c3e50",
                                   anchor="w", tags="scene")
            
            action_lines = action.split("\n") if action else ["等待开始..."]
            action_y = panel_y + 105
            for line in action_lines[:8]:
                fill_color = "#495057"
                if "✓" in line or "✅" in line:
                    fill_color = "#27ae60"
                elif "🔀" in line or "交换" in line:
                    fill_color = "#e74c3c"
                    
                self.canvas.create_text(panel_x + 12, action_y, text=line,
                                       font=("微软雅黑", 9), fill=fill_color,
                                       anchor="w", width=330, tags="scene")
                action_y += 18
            
            # 分隔线
            self.canvas.create_line(panel_x + 8, panel_y + 240, canvas_width - 18, panel_y + 240,
                                   fill="#dee2e6", tags="scene")
            
            # 统计信息
            self.canvas.create_text(panel_x + 12, panel_y + 258, text="📊 统计数据",
                                   font=("微软雅黑", 10, "bold"), fill="#2c3e50",
                                   anchor="w", tags="scene")
            
            self.canvas.create_text(panel_x + 12, panel_y + 282,
                                   text=f"🔀 交换次数：{stats['swap']}",
                                   font=("微软雅黑", 10), fill="#dc3545",
                                   anchor="w", tags="scene")
            
            self.canvas.create_text(panel_x + 150, panel_y + 282,
                                   text=f"📏 数组长度：{n}",
                                   font=("微软雅黑", 10), fill="#17a2b8",
                                   anchor="w", tags="scene")
            
            # 分隔线
            self.canvas.create_line(panel_x + 8, panel_y + 305, canvas_width - 18, panel_y + 305,
                                   fill="#dee2e6", tags="scene")
            
            # 数组对比
            self.canvas.create_text(panel_x + 12, panel_y + 322,
                                   text=f"原始：{original_data}",
                                   font=("Consolas", 8), fill="#6c757d",
                                   anchor="w", tags="scene")
            self.canvas.create_text(panel_x + 12, panel_y + 342,
                                   text=f"当前：{list(arr)}",
                                   font=("Consolas", 8), fill="#28a745",
                                   anchor="w", tags="scene")
            
            self.window.update()
        
        def animate_swap(arr, idx1, idx2):
            """执行交换动画 - 元素上升、交叉移动、下降"""
            x1 = get_bar_x(idx1)
            x2 = get_bar_x(idx2)
            h1, h2 = get_bar_height(arr[idx1]), get_bar_height(arr[idx2])
            val1, val2 = arr[idx1], arr[idx2]
            
            # 阶段1: 两个元素同时上升
            for step in range(10):
                self.canvas.delete("swap_anim")
                offset_y = step * 8
                
                for pos, val, h in [(x1, val1, h1), (x2, val2, h2)]:
                    y_bottom = bar_area_bottom - offset_y
                    y_top = y_bottom - h
                    
                    self.canvas.create_rectangle(pos, y_top, pos + bar_width, y_bottom,
                                                fill="#e74c3c", outline="#c0392b", width=3,
                                                tags="swap_anim")
                    display_val = str(val)
                    if len(display_val) > 5:
                        display_val = display_val[:4] + ".."
                    self.canvas.create_text(pos + bar_width // 2, (y_top + y_bottom) // 2,
                                           text=display_val,
                                           font=("Arial", 12, "bold"), fill="white",
                                           tags="swap_anim")
                
                self.window.update()
                time.sleep(0.025)
            
            # 阶段2: 水平交叉移动
            distance = x2 - x1
            for step in range(18):
                self.canvas.delete("swap_anim")
                progress = step / 17
                
                # 左边元素向右移
                pos1 = x1 + progress * distance
                y_bottom = bar_area_bottom - 80
                y_top = y_bottom - h1
                self.canvas.create_rectangle(pos1, y_top, pos1 + bar_width, y_bottom,
                                            fill="#e74c3c", outline="#c0392b", width=3,
                                            tags="swap_anim")
                display_val = str(val1)
                if len(display_val) > 5:
                    display_val = display_val[:4] + ".."
                self.canvas.create_text(pos1 + bar_width // 2, (y_top + y_bottom) // 2,
                                       text=display_val,
                                       font=("Arial", 12, "bold"), fill="white",
                                       tags="swap_anim")
                
                # 右边元素向左移
                pos2 = x2 - progress * distance
                y_top = y_bottom - h2
                self.canvas.create_rectangle(pos2, y_top, pos2 + bar_width, y_bottom,
                                            fill="#e74c3c", outline="#c0392b", width=3,
                                            tags="swap_anim")
                display_val = str(val2)
                if len(display_val) > 5:
                    display_val = display_val[:4] + ".."
                self.canvas.create_text(pos2 + bar_width // 2, (y_top + y_bottom) // 2,
                                       text=display_val,
                                       font=("Arial", 12, "bold"), fill="white",
                                       tags="swap_anim")
                
                self.window.update()
                time.sleep(0.025)
            
            # 执行实际交换
            arr[idx1], arr[idx2] = arr[idx2], arr[idx1]
            
            # 阶段3: 下降回位
            for step in range(10):
                self.canvas.delete("swap_anim")
                offset_y = 80 - step * 8
                
                # 注意：位置已经交换
                for pos, val, h in [(x1, val2, h2), (x2, val1, h1)]:
                    y_bottom = bar_area_bottom - offset_y
                    y_top = y_bottom - h
                    
                    self.canvas.create_rectangle(pos, y_top, pos + bar_width, y_bottom,
                                                fill="#e74c3c", outline="#c0392b", width=3,
                                                tags="swap_anim")
                    display_val = str(val)
                    if len(display_val) > 5:
                        display_val = display_val[:4] + ".."
                    self.canvas.create_text(pos + bar_width // 2, (y_top + y_bottom) // 2,
                                           text=display_val,
                                           font=("Arial", 12, "bold"), fill="white",
                                           tags="swap_anim")
                
                self.window.update()
                time.sleep(0.025)
            
            self.canvas.delete("swap_anim")
        
        # ===== 开始教学演示 =====
        total_swaps = n // 2
        
        # 第0步：介绍
        self.highlight_pseudo_line(0)
        draw_reverse_scene(data, action="🎬 顺序表逆置开始！\n\n核心思想：\n将顺序表中的所有元素\n前后颠倒位置\n\n例如：[1,2,3,4,5]\n变为：[5,4,3,2,1]", current_step=0, total_steps=total_swaps)
        time.sleep(1.5)
        
        self.highlight_pseudo_line(1)
        self.highlight_pseudo_line(2)
        self.highlight_pseudo_line(3)
        draw_reverse_scene(data, action="📖 算法原理：\n\n使用双指针法：\n• i 从头开始向后移动\n• j 从尾开始向前移动\n• 每次交换 data[i] 和 data[j]\n• 直到 i >= j 时停止", current_step=0, total_steps=total_swaps)
        time.sleep(1.5)
        
        self.highlight_pseudo_line(4)
        draw_reverse_scene(data, action=f"📋 本次逆置：\n\n数组长度 n = {n}\n需要交换 {total_swaps} 对元素\n\n开始逆置操作...", current_step=0, total_steps=total_swaps)
        time.sleep(1.0)
        
        # 主循环
        self.highlight_pseudo_line(6)
        for i in range(n // 2):
            j = n - 1 - i
            
            # 显示当前要交换的元素
            self.highlight_pseudo_line(7)
            draw_reverse_scene(data, left_idx=i, right_idx=j, 
                             action=f"🔄 第 {i + 1} 次交换\n\ni = {i}, j = n - 1 - i = {j}\n\n准备交换：\ndata[{i}] = {data[i]}\ndata[{j}] = {data[j]}",
                             current_step=i, total_steps=total_swaps)
            time.sleep(0.8)
            
            # 显示交换前的比较
            draw_reverse_scene(data, left_idx=i, right_idx=j,
                             action=f"👀 观察交换对\n\n左边元素：data[{i}] = {data[i]}\n右边元素：data[{j}] = {data[j]}\n\n执行交换 ⟷",
                             current_step=i, total_steps=total_swaps)
            time.sleep(0.6)
            
            # 执行交换动画
            self.highlight_pseudo_line(8)
            draw_reverse_scene(data, left_idx=i, right_idx=j, swap_highlight=True,
                             action=f"🔀 执行交换\n\nswap(data[{i}], data[{j}])\n{data[i]} ⟷ {data[j]}",
                             current_step=i, total_steps=total_swaps)
            time.sleep(0.3)
            
            animate_swap(data, i, j)
            stats["swap"] += 1
            
            # 标记已完成
            swapped_positions.add(i)
            swapped_positions.add(j)
            
            # 交换完成
            draw_reverse_scene(data, left_idx=i, right_idx=j,
                             action=f"✅ 交换完成！\n\n现在：\ndata[{i}] = {data[i]}\ndata[{j}] = {data[j]}\n\n位置 [{i}] 和 [{j}] 已完成",
                             current_step=i + 1, total_steps=total_swaps)
            time.sleep(0.6)
        
        # 处理奇数长度数组的中间元素
        if n % 2 == 1:
            mid = n // 2
            swapped_positions.add(mid)
            draw_reverse_scene(data,
                             action=f"💡 中间元素\n\n数组长度为奇数\n中间元素 data[{mid}] = {data[mid]}\n位置不变，直接标记完成",
                             current_step=total_swaps, total_steps=total_swaps)
            time.sleep(0.8)
        
        # 逆置完成
        self.highlight_pseudo_line(9)
        draw_reverse_scene(data,
                         action=f"🎉 逆置完成！\n\n✨ 顺序表已成功逆置！\n\n📊 统计结果：\n总共交换了 {stats['swap']} 次\n\n⏱️ 时间复杂度：O(n/2) = O(n)\n💾 空间复杂度：O(1)",
                         current_step=total_swaps, total_steps=total_swaps)
        
        self.complete_pseudo_code()
        
        # 更新模型数据
        self.model.data = list(data)
        
        # 添加操作历史
        self.add_operation_history(f"顺序表逆置完成: 交换{stats['swap']}次")
        
        # 显示精美总结页面
        time.sleep(2.0)
        self.canvas.delete("scene")
        self._draw_reverse_summary(original_data, data, stats, n)
        
        # 等待用户查看总结
        time.sleep(4)
        self.update_display()
    
    def _is_numeric(self, value):
        """检查值是否为数字"""
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            return False
    
    def _draw_reverse_summary(self, original_data, reversed_data, stats, n):
        """绘制逆置操作的精美学习总结页面"""
        canvas_width = 1000
        canvas_height = 380
        
        # ===== 背景渐变效果（青色主题）=====
        for i in range(canvas_height):
            ratio = i / canvas_height
            r = int(0 + ratio * 20)
            g = int(50 + ratio * 40)
            b = int(60 + ratio * 50)
            color = f"#{r:02x}{g:02x}{b:02x}"
            self.canvas.create_line(0, i, canvas_width, i, fill=color, tags="scene")
        
        # ===== 顶部装饰条 =====
        self.canvas.create_rectangle(0, 0, canvas_width, 6, fill="#00bcd4", outline="", tags="scene")
        self.canvas.create_rectangle(0, 6, canvas_width, 8, fill="#4dd0e1", outline="", tags="scene")
        
        # ===== 标题区域 =====
        self.canvas.create_oval(canvas_width//2 - 200, -35, canvas_width//2 + 200, 70,
                               fill="#004d40", outline="", tags="scene")
        
        self.canvas.create_text(canvas_width // 2, 32, 
                               text="🔄 顺序表逆置 · 学习总结",
                               font=("微软雅黑", 20, "bold"), fill="#ffffff", tags="scene")
        
        self.canvas.create_line(canvas_width//2 - 150, 52, canvas_width//2 + 150, 52,
                               fill="#00bcd4", width=2, tags="scene")
        
        # ===== 成就徽章 =====
        badge_x, badge_y = 900, 45
        self.canvas.create_oval(badge_x - 42, badge_y - 42, badge_x + 42, badge_y + 42,
                               fill="#00695c", outline="", tags="scene")
        self.canvas.create_oval(badge_x - 35, badge_y - 35, badge_x + 35, badge_y + 35,
                               fill="#00bcd4", outline="#00838f", width=3, tags="scene")
        self.canvas.create_oval(badge_x - 25, badge_y - 25, badge_x + 25, badge_y + 25,
                               fill="#e0f7fa", outline="#00bcd4", width=2, tags="scene")
        self.canvas.create_text(badge_x, badge_y - 5, text="🔄",
                               font=("Arial", 16), fill="#006064", tags="scene")
        self.canvas.create_text(badge_x, badge_y + 18, text="完成",
                               font=("微软雅黑", 8, "bold"), fill="#004d40", tags="scene")
        
        # ===== 左侧：算法知识卡片 =====
        card1_x, card1_y = 30, 70
        card1_w, card1_h = 300, 290
        
        self.canvas.create_rectangle(card1_x + 4, card1_y + 4, 
                                    card1_x + card1_w + 4, card1_y + card1_h + 4,
                                    fill="#0f172a", outline="", tags="scene")
        self.canvas.create_rectangle(card1_x, card1_y, card1_x + card1_w, card1_y + card1_h,
                                    fill="#1e293b", outline="#334155", width=2, tags="scene")
        
        self.canvas.create_rectangle(card1_x, card1_y, card1_x + card1_w, card1_y + 35,
                                    fill="#00bcd4", outline="", tags="scene")
        self.canvas.create_text(card1_x + card1_w//2, card1_y + 18, text="📚 逆置算法知识点",
                               font=("微软雅黑", 11, "bold"), fill="#ffffff", tags="scene")
        
        knowledge_items = [
            ("💡 核心思想", "双指针法：首尾交换\n逐步向中间靠拢", "#4dd0e1"),
            ("⏱️ 时间复杂度", "O(n/2) = O(n)\n只需遍历一半元素", "#ce93d8"),
            ("💾 空间复杂度", "O(1) - 原地操作\n不需要额外空间", "#81c784"),
            ("🎯 应用场景", "字符串翻转、数组旋转\n链表逆置的辅助操作", "#ffcc80"),
        ]
        
        ky = card1_y + 52
        for title, content, color in knowledge_items:
            self.canvas.create_rectangle(card1_x + 10, ky, card1_x + 14, ky + 40,
                                        fill=color, outline="", tags="scene")
            self.canvas.create_text(card1_x + 22, ky + 8, text=title,
                                   font=("微软雅黑", 9, "bold"), fill="#e2e8f0",
                                   anchor="w", tags="scene")
            self.canvas.create_text(card1_x + 22, ky + 35, text=content,
                                   font=("微软雅黑", 8), fill="#94a3b8",
                                   anchor="w", width=265, tags="scene")
            ky += 58
        
        # ===== 中间上方：统计数据卡片 =====
        card2_x, card2_y = 350, 70
        card2_w, card2_h = 280, 120
        
        self.canvas.create_rectangle(card2_x + 4, card2_y + 4, 
                                    card2_x + card2_w + 4, card2_y + card2_h + 4,
                                    fill="#0f172a", outline="", tags="scene")
        self.canvas.create_rectangle(card2_x, card2_y, card2_x + card2_w, card2_y + card2_h,
                                    fill="#1e293b", outline="#334155", width=2, tags="scene")
        
        self.canvas.create_rectangle(card2_x, card2_y, card2_x + card2_w, card2_y + 32,
                                    fill="#26a69a", outline="", tags="scene")
        self.canvas.create_text(card2_x + card2_w//2, card2_y + 16, text="📊 本次操作统计",
                               font=("微软雅黑", 10, "bold"), fill="#ffffff", tags="scene")
        
        # 统计项
        self.canvas.create_text(card2_x + 20, card2_y + 55, text="🔀 交换次数",
                               font=("微软雅黑", 10), fill="#94a3b8", anchor="w", tags="scene")
        self.canvas.create_text(card2_x + 130, card2_y + 55, text=str(stats['swap']),
                               font=("Consolas", 14, "bold"), fill="#ef5350", anchor="w", tags="scene")
        
        self.canvas.create_text(card2_x + 160, card2_y + 55, text="📏 数组长度",
                               font=("微软雅黑", 10), fill="#94a3b8", anchor="w", tags="scene")
        self.canvas.create_text(card2_x + 260, card2_y + 55, text=str(n),
                               font=("Consolas", 14, "bold"), fill="#64b5f6", anchor="w", tags="scene")
        
        # 效率说明
        self.canvas.create_text(card2_x + card2_w // 2, card2_y + 90,
                               text=f"✨ 仅用 {stats['swap']} 次交换完成 {n} 个元素的逆置",
                               font=("微软雅黑", 9), fill="#4dd0e1", tags="scene")
        
        # ===== 中间下方：双指针图示卡片 =====
        card3_x, card3_y = 350, 205
        card3_w, card3_h = 280, 155
        
        self.canvas.create_rectangle(card3_x + 4, card3_y + 4, 
                                    card3_x + card3_w + 4, card3_y + card3_h + 4,
                                    fill="#0f172a", outline="", tags="scene")
        self.canvas.create_rectangle(card3_x, card3_y, card3_x + card3_w, card3_y + card3_h,
                                    fill="#1e293b", outline="#334155", width=2, tags="scene")
        
        self.canvas.create_rectangle(card3_x, card3_y, card3_x + card3_w, card3_y + 32,
                                    fill="#ff7043", outline="", tags="scene")
        self.canvas.create_text(card3_x + card3_w//2, card3_y + 16, text="💡 双指针法图示",
                               font=("微软雅黑", 10, "bold"), fill="#ffffff", tags="scene")
        
        # 图示
        demo_y = card3_y + 60
        self.canvas.create_text(card3_x + 20, demo_y, text="初始：",
                               font=("微软雅黑", 9), fill="#94a3b8", anchor="w", tags="scene")
        self.canvas.create_text(card3_x + 70, demo_y, text="[ ← i          j → ]",
                               font=("Consolas", 10, "bold"), fill="#4dd0e1", anchor="w", tags="scene")
        
        self.canvas.create_text(card3_x + 20, demo_y + 25, text="过程：",
                               font=("微软雅黑", 9), fill="#94a3b8", anchor="w", tags="scene")
        self.canvas.create_text(card3_x + 70, demo_y + 25, text="[    → i    j ←    ]",
                               font=("Consolas", 10, "bold"), fill="#ffcc80", anchor="w", tags="scene")
        
        self.canvas.create_text(card3_x + 20, demo_y + 50, text="结束：",
                               font=("微软雅黑", 9), fill="#94a3b8", anchor="w", tags="scene")
        self.canvas.create_text(card3_x + 70, demo_y + 50, text="[        i≥j        ]",
                               font=("Consolas", 10, "bold"), fill="#81c784", anchor="w", tags="scene")
        
        self.canvas.create_text(card3_x + card3_w // 2, demo_y + 80,
                               text="当 i ≥ j 时停止，逆置完成！",
                               font=("微软雅黑", 9, "bold"), fill="#26a69a", tags="scene")
        
        # ===== 右侧：逆置前后对比卡片 =====
        card4_x, card4_y = 650, 70
        card4_w, card4_h = 335, 290
        
        self.canvas.create_rectangle(card4_x + 4, card4_y + 4, 
                                    card4_x + card4_w + 4, card4_y + card4_h + 4,
                                    fill="#0f172a", outline="", tags="scene")
        self.canvas.create_rectangle(card4_x, card4_y, card4_x + card4_w, card4_y + card4_h,
                                    fill="#1e293b", outline="#334155", width=2, tags="scene")
        
        self.canvas.create_rectangle(card4_x, card4_y, card4_x + card4_w, card4_y + 32,
                                    fill="#ab47bc", outline="", tags="scene")
        self.canvas.create_text(card4_x + card4_w//2, card4_y + 16, text="📈 逆置前后对比",
                               font=("微软雅黑", 10, "bold"), fill="#ffffff", tags="scene")
        
        # 可视化对比
        viz_top = card4_y + 55
        box_size = min(30, (card4_w - 80) // max(1, n) - 4)
        
        def draw_array_viz(data_list, start_y, label, label_color, box_color, arrow_color=None):
            self.canvas.create_text(card4_x + 15, start_y + box_size // 2, text=label,
                                   font=("微软雅黑", 9, "bold"), fill=label_color,
                                   anchor="w", tags="scene")
            
            start_x = card4_x + 60
            for i, val in enumerate(data_list):
                x = start_x + i * (box_size + 4)
                
                # 方框
                self.canvas.create_rectangle(x, start_y, x + box_size, start_y + box_size,
                                            fill=box_color, outline="#ffffff", width=1, tags="scene")
                
                # 值
                display_val = str(val)
                if len(display_val) > 3:
                    display_val = display_val[:2] + ".."
                self.canvas.create_text(x + box_size // 2, start_y + box_size // 2,
                                       text=display_val,
                                       font=("Consolas", 8, "bold"), fill="white", tags="scene")
            
            # 绘制箭头（如果需要）
            if arrow_color:
                arrow_y = start_y + box_size + 12
                for i in range(n):
                    x = start_x + i * (box_size + 4) + box_size // 2
                    target_i = n - 1 - i
                    target_x = start_x + target_i * (box_size + 4) + box_size // 2
                    
                    if i < n // 2:
                        # 只画一半的箭头，避免重复
                        self.canvas.create_line(x, arrow_y, target_x, arrow_y + 35,
                                               fill=arrow_color, width=1, arrow="last",
                                               dash=(2, 2), tags="scene")
        
        # 逆置前
        draw_array_viz(original_data, viz_top, "前：", "#ef5350", "#e53935")
        
        # 箭头提示
        arrow_y = viz_top + box_size + 15
        self.canvas.create_text(card4_x + card4_w // 2, arrow_y + 20, text="⬇️  逆置操作  ⬇️",
                               font=("微软雅黑", 10, "bold"), fill="#00bcd4", tags="scene")
        
        # 逆置后
        draw_array_viz(reversed_data, arrow_y + 50, "后：", "#66bb6a", "#43a047")
        
        # 数组文字对比
        text_y = arrow_y + 50 + box_size + 25
        self.canvas.create_text(card4_x + card4_w // 2, text_y,
                               text=f"原始：{original_data}",
                               font=("Consolas", 9), fill="#ef5350", tags="scene")
        self.canvas.create_text(card4_x + card4_w // 2, text_y + 18,
                               text=f"逆置：{list(reversed_data)}",
                               font=("Consolas", 9), fill="#66bb6a", tags="scene")
        
        # ===== 底部装饰 =====
        self.canvas.create_rectangle(0, canvas_height - 25, canvas_width, canvas_height,
                                    fill="#003d33", outline="", tags="scene")
        self.canvas.create_line(0, canvas_height - 25, canvas_width, canvas_height - 25,
                               fill="#00bcd4", width=1, tags="scene")
        
        self.canvas.create_text(canvas_width // 2, canvas_height - 12,
                               text="🎉 恭喜你掌握了顺序表逆置算法！简单高效的双指针技巧！ 🚀",
                               font=("微软雅黑", 10, "bold"), fill="#4dd0e1", tags="scene")
        
        self.window.update()

if __name__ == '__main__':
    window = Tk()
    window.title("顺序表可视化")
    window.geometry("1350x800")
    window.maxsize(1350, 800)
    window.minsize(1350, 800)
    SequenceListVisualizer(window)
    window.mainloop()