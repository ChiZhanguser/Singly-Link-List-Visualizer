import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import time
from datetime import datetime
from stack.stack_model import StackModel
from stack.dfs_visual import open_dfs_visualizer
import storage
import stack.stack_api as stack_api
from DSL_utils import process_command

# ========== 多语言伪代码定义 ==========

# 语言选项
LANG_PSEUDOCODE = "伪代码"
LANG_C = "C语言"
LANG_JAVA = "Java"
LANG_PYTHON = "Python"
CODE_LANGUAGES = [LANG_PSEUDOCODE, LANG_C, LANG_JAVA, LANG_PYTHON]

# 入栈 - 多语言模板 (参数化)
def get_push_pseudocode(lang, value, top, capacity, will_expand=False, new_cap=None):
    """获取入栈操作的多语言伪代码"""
    if lang == "伪代码":
        if will_expand:
            return [
                f"// 入栈操作: Push({value})",
                f"if top ≥ capacity - 1 then  // top={top}, capacity={capacity}",
                f"  if auto_expand then  // ✓ 自动扩容开启",
                f"    capacity ← capacity × 2  // 新容量={new_cap}",
                f"  end if",
                f"end if",
                f"top ← top + 1  // top变为{top+1}",
                f"stack[top] ← {value}",
                f"return OK  // ✅ 入栈成功"
            ]
        else:
            return [
                f"// 入栈操作: Push({value})",
                f"if top ≥ capacity - 1 then  // top={top}, capacity={capacity}",
                f"  return OVERFLOW  // 栈满",
                f"end if",
                f"top ← top + 1  // top变为{top+1}",
                f"stack[top] ← {value}",
                f"return OK  // ✅ 入栈成功"
            ]
    elif lang == "C语言":
        if will_expand:
            return [
                f"// 入栈操作: Push({value})",
                f"if (top >= capacity - 1) {{ // top={top}, capacity={capacity}",
                f"  if (auto_expand) {{ // ✓ 自动扩容",
                f"    capacity = capacity * 2; // 新容量={new_cap}",
                f"    realloc(stack, capacity * sizeof(int));",
                f"  }}",
                f"}}",
                f"top++; // top变为{top+1}",
                f"stack[top] = {value};",
                f"return OK; // ✅ 入栈成功"
            ]
        else:
            return [
                f"// 入栈操作: Push({value})",
                f"if (top >= capacity - 1) {{ // top={top}, capacity={capacity}",
                f"  return OVERFLOW; // 栈满",
                f"}}",
                f"top++; // top变为{top+1}",
                f"stack[top] = {value};",
                f"return OK; // ✅ 入栈成功"
            ]
    elif lang == "Java":
        if will_expand:
            return [
                f"// 入栈操作: push({value})",
                f"if (top >= capacity - 1) {{ // top={top}, capacity={capacity}",
                f"  if (autoExpand) {{ // ✓ 自动扩容",
                f"    capacity = capacity * 2; // 新容量={new_cap}",
                f"    stack = Arrays.copyOf(stack, capacity);",
                f"  }}",
                f"}}",
                f"top++; // top变为{top+1}",
                f"stack[top] = {value};",
                f"return true; // ✅ 入栈成功"
            ]
        else:
            return [
                f"// 入栈操作: push({value})",
                f"if (top >= capacity - 1) {{ // top={top}, capacity={capacity}",
                f"  throw new StackOverflowError(); // 栈满",
                f"}}",
                f"top++; // top变为{top+1}",
                f"stack[top] = {value};",
                f"return true; // ✅ 入栈成功"
            ]
    else:  # Python
        if will_expand:
            return [
                f"# 入栈操作: push({value})",
                f"if top >= capacity - 1:  # top={top}, capacity={capacity}",
                f"  if auto_expand:  # ✓ 自动扩容",
                f"    capacity = capacity * 2  # 新容量={new_cap}",
                f"    stack.extend([None] * (capacity - len(stack)))",
                f"  # endif",
                f"# endif",
                f"top += 1  # top变为{top+1}",
                f"stack[top] = {value}",
                f"return True  # ✅ 入栈成功"
            ]
        else:
            return [
                f"# 入栈操作: push({value})",
                f"if top >= capacity - 1:  # top={top}, capacity={capacity}",
                f"  raise StackOverflowError()  # 栈满",
                f"# endif",
                f"top += 1  # top变为{top+1}",
                f"stack[top] = {value}",
                f"return True  # ✅ 入栈成功"
            ]

# 出栈 - 多语言模板
def get_pop_pseudocode(lang, top, capacity):
    """获取出栈操作的多语言伪代码"""
    if lang == "伪代码":
        return [
            "// 出栈操作: Pop()",
            f"if top < 0 then  // top={top}",
            "  return UNDERFLOW  // 栈空",
            "end if",
            f"value ← stack[top]  // 取出栈顶元素",
            f"top ← top - 1  // top变为{top-1}",
            "return value  // ✅ 出栈成功"
        ]
    elif lang == "C语言":
        return [
            "// 出栈操作: Pop()",
            f"if (top < 0) {{ // top={top}",
            "  return UNDERFLOW; // 栈空",
            "}",
            f"int value = stack[top]; // 取出栈顶元素",
            f"top--; // top变为{top-1}",
            "return value; // ✅ 出栈成功"
        ]
    elif lang == "Java":
        return [
            "// 出栈操作: pop()",
            f"if (top < 0) {{ // top={top}",
            "  throw new EmptyStackException(); // 栈空",
            "}",
            f"int value = stack[top]; // 取出栈顶元素",
            f"top--; // top变为{top-1}",
            "return value; // ✅ 出栈成功"
        ]
    else:  # Python
        return [
            "# 出栈操作: pop()",
            f"if top < 0:  # top={top}",
            "  raise IndexError('栈空')  # 栈空",
            "# endif",
            f"value = stack[top]  # 取出栈顶元素",
            f"top -= 1  # top变为{top-1}",
            "return value  # ✅ 出栈成功"
        ]

# 清空栈 - 多语言模板
def get_clear_pseudocode(lang, count):
    """获取清空栈操作的多语言伪代码"""
    if lang == "伪代码":
        return [
            f"// 清空栈操作 (共 {count} 个元素)",
            "while top ≥ 0 do",
            "  Pop()  // 逐个出栈",
            "end while",
            "// 栈已清空, top = -1"
        ]
    elif lang == "C语言":
        return [
            f"// 清空栈操作 (共 {count} 个元素)",
            "while (top >= 0) {",
            "  pop(); // 逐个出栈",
            "}",
            "// 栈已清空, top = -1"
        ]
    elif lang == "Java":
        return [
            f"// 清空栈操作 (共 {count} 个元素)",
            "while (top >= 0) {",
            "  pop(); // 逐个出栈",
            "}",
            "// 栈已清空, top = -1"
        ]
    else:  # Python
        return [
            f"# 清空栈操作 (共 {count} 个元素)",
            "while top >= 0:",
            "  pop()  # 逐个出栈",
            "# endwhile",
            "# 栈已清空, top = -1"
        ]

class StackVisualizer:
    def __init__(self, root):
        self.window = root
        
        # 代码语言设置（支持运行时切换）
        self.current_code_language = LANG_PSEUDOCODE  # 默认伪代码
        self.current_operation_context = None  # 保存当前操作上下文，用于语言切换时重新渲染
        
        # --- 美化: 1. 定义样式和字体 ---
        self.style = ttk.Style(self.window)
        try:
            if os.name == 'nt':
                self.style.theme_use('clam')
            else:
                self.style.theme_use('clam')
        except tk.TclError:
            pass 

        # 定义字体
        self.font_large_bold = ("Segoe UI", 28, "bold")
        self.font_medium = ("Segoe UI", 16)
        self.font_normal_bold = ("Segoe UI", 13, "bold")
        self.font_normal = ("Segoe UI", 12)
        self.font_small = ("Segoe UI", 11)

        # 定义颜色
        self.bg_color = "#F0F0F0"       
        self.header_color = "#003366" 
        self.canvas_bg = "#FFFFFF"
        self.accent_color = "#6C9EFF"
        self.stack_fill = "#B0E0E6"    
        self.stack_outline = "#333333" 
        
        # 配置 ttk 样式
        self.style.configure('.', font=self.font_normal, background=self.bg_color)
        self.style.configure('TLabel', background=self.bg_color)
        self.style.configure('TFrame', background=self.bg_color)

        # --- 美化: 2. 定义彩色按钮样式 (使用 configure) ---
        self.style.configure("success.TButton", font=self.font_normal_bold, background="#28a745", foreground="white")
        self.style.configure("danger.TButton", font=self.font_normal_bold, background="#dc3545", foreground="white")
        self.style.configure("warning.TButton", font=self.font_normal_bold, background="#ffc107", foreground="black") 
        self.style.configure("primary.TButton", font=self.font_normal_bold, background="#007bff", foreground="white")
        self.style.configure("info.TButton", font=self.font_normal_bold, background=self.accent_color, foreground="white")

        # --- [!!! 关键修复 !!!] ---
        # 解决某些主题下 background 和 foreground 不生效的问题
        # 必须同时 "map" (映射) foreground 才能保证文字在 !disabled 状态下可见
        self.style.map("success.TButton",
                       background=[('active', '#218838'), ('!disabled', '#28a745')],
                       foreground=[('active', 'white'), ('!disabled', 'white')])
        self.style.map("danger.TButton",
                       background=[('active', '#c82333'), ('!disabled', '#dc3545')],
                       foreground=[('active', 'white'), ('!disabled', 'white')])
        self.style.map("warning.TButton",
                       background=[('active', '#e0a800'), ('!disabled', '#ffc107')],
                       foreground=[('active', 'black'), ('!disabled', 'black')])
        self.style.map("primary.TButton",
                       background=[('active', '#0069d9'), ('!disabled', '#007bff')],
                       foreground=[('active', 'white'), ('!disabled', 'white')])
        self.style.map("info.TButton",
                       background=[('active', '#5A8DFF'), ('!disabled', self.accent_color)],
                       foreground=[('active', 'white'), ('!disabled', 'white')])
        
        # --- 美化: 3. 更新窗口和画布样式 ---
        self.window.config(bg=self.bg_color)
        
        # 创建主内容区域（画布 + 伪代码面板）
        main_content = tk.Frame(self.window, bg=self.bg_color)
        main_content.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 左侧画布容器
        canvas_container = tk.Frame(main_content, bg=self.bg_color)
        canvas_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 伪代码相关变量（需要在创建面板前初始化）
        self.pseudo_code_lines = []
        self.current_highlight_line = -1
        self.animation_speed = 0.03
        
        self.canvas = tk.Canvas(canvas_container, bg=self.canvas_bg, width=1000, height=420, 
                                relief=tk.FLAT, bd=1, highlightbackground="#BDBDBD")
        self.canvas.pack(pady=(0, 5))
        
        # 右侧伪代码面板
        self.create_pseudo_code_panel(main_content) 

        # 默认 capacity 与模型
        self.capacity = 10
        self.model = StackModel(self.capacity)
        
        # 画布元素引用
        self.stack_rectangles = []
        self.stack_labels = []
        
        # 布局参数
        self.start_x = 150
        self.start_y = 350  # 下移避免与信息面板重叠
        self.cell_width = 70
        self.cell_height = 50
        self.spacing = 8
        
        # 控件状态与变量
        self.value_entry = tk.StringVar()
        self.batch_entry_var = tk.StringVar()
        self.dsl_var = tk.StringVar()
        self.input_frame = None
        self.push_btn = None
        self.pop_btn = None
        self.clear_btn = None
        self.back_btn = None
        self.confirm_btn = None
        self.batch_build_btn = None

        self.batch_queue = []
        self.batch_index = 0

        self.animating = False
        
        # 后缀表达式求值相关
        self.postfix_var = tk.StringVar()
        self.postfix_queue = []  # 存储待处理的token
        self.postfix_index = 0
        self.postfix_result = None
        self.eval_btn = None
        self.postfix_expression = ""  # 原始表达式
        self.postfix_tokens_display = []  # 用于显示的token列表
        
        # 括号匹配检验相关
        self.bracket_var = tk.StringVar()
        self.bracket_queue = []  # 存储待处理的字符
        self.bracket_index = 0
        self.bracket_expression = ""  # 原始表达式
        self.bracket_match_btn = None
        self.bracket_pairs = {'(': ')', '[': ']', '{': '}'}  # 括号配对
        self.left_brackets = set('([{')
        self.right_brackets = set(')]}')
        
        # 动态扩容相关
        self.auto_expand_var = tk.BooleanVar(value=True)

        # 初始化界面
        self.create_heading()
        self.create_buttons()
        self.update_display()

        # 注册到 stack_api
        stack_api.register(self)
    
    def create_pseudo_code_panel(self, parent):
        """创建伪代码显示面板（固定在右侧）"""
        pseudo_frame = tk.Frame(parent, bg="#2d3436", relief=tk.RAISED, bd=2, width=320)
        pseudo_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(8, 0))
        pseudo_frame.pack_propagate(False)
        
        # 标题栏（包含标题和语言切换）
        title_frame = tk.Frame(pseudo_frame, bg="#2d3436")
        title_frame.pack(fill=tk.X, padx=10, pady=5)
        
        title_label = tk.Label(title_frame, text="📋 代码执行", 
                              font=("微软雅黑", 11, "bold"), 
                              bg="#2d3436", fg="#00cec9")
        title_label.pack(side=tk.LEFT)
        
        # 语言切换下拉框
        self.code_lang_var = tk.StringVar(value=self.current_code_language)
        self.lang_menu = tk.OptionMenu(
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
        self.lang_menu.pack(side=tk.RIGHT)
        
        # 语言切换快捷按钮组
        btn_frame = tk.Frame(pseudo_frame, bg="#2d3436")
        btn_frame.pack(fill=tk.X, padx=10, pady=(0, 5))
        
        self.lang_buttons = {}
        for lang in CODE_LANGUAGES:
            short_name = {"伪代码": "伪代码", "C语言": "C", "Java": "Java", "Python": "Py"}.get(lang, lang)
            btn = tk.Label(
                btn_frame,
                text=short_name,
                font=("微软雅黑", 8),
                bg="#00cec9" if lang == self.current_code_language else "#45475A",
                fg="#1E1E2E" if lang == self.current_code_language else "#CDD6F4",
                padx=6,
                pady=2,
                cursor="hand2"
            )
            btn.pack(side=tk.LEFT, padx=2)
            btn.bind("<Button-1>", lambda e, l=lang: self._switch_code_language(l))
            self.lang_buttons[lang] = btn
        
        # 分隔线
        separator = tk.Frame(pseudo_frame, height=2, bg="#00cec9")
        separator.pack(fill=tk.X, padx=10, pady=(0, 3))
        
        # 当前操作标签
        self.operation_label = tk.Label(pseudo_frame, text="等待操作...", 
                                        font=("微软雅黑", 10), 
                                        bg="#2d3436", fg="#dfe6e9", 
                                        wraplength=280, justify=tk.LEFT)
        self.operation_label.pack(fill=tk.X, padx=10, pady=3)
        
        # 伪代码显示区域
        code_container = tk.Frame(pseudo_frame, bg="#1e272e")
        code_container.pack(fill=tk.BOTH, expand=True, padx=8, pady=5)
        
        self.pseudo_text = tk.Text(code_container, 
                                   font=("Consolas", 10), 
                                   bg="#1e272e", fg="#b2bec3",
                                   relief=tk.FLAT, 
                                   wrap=tk.WORD,
                                   padx=8, pady=8,
                                   cursor="arrow",
                                   state=tk.DISABLED,
                                   height=12,
                                   width=34)
        self.pseudo_text.pack(fill=tk.BOTH, expand=True)
        
        # 配置高亮标签样式
        self.pseudo_text.tag_configure("highlight", 
                                       background="#00b894", 
                                       foreground="#ffffff",
                                       font=("Consolas", 10, "bold"))
        self.pseudo_text.tag_configure("executed", 
                                       foreground="#55efc4")
        self.pseudo_text.tag_configure("pending", 
                                       foreground="#636e72")
        
        # 进度指示器
        progress_frame = tk.Frame(pseudo_frame, bg="#2d3436")
        progress_frame.pack(fill=tk.X, padx=10, pady=(0, 5))
        
        self.progress_label = tk.Label(progress_frame, text="步骤: 0/0", 
                                       font=("Arial", 9), 
                                       bg="#2d3436", fg="#b2bec3")
        self.progress_label.pack(side=tk.LEFT)
        
        self.status_indicator = tk.Label(progress_frame, text="⚫ 空闲", 
                                         font=("Arial", 9), 
                                         bg="#2d3436", fg="#b2bec3")
        self.status_indicator.pack(side=tk.RIGHT)
        
        # 速度控制
        control_separator = tk.Frame(pseudo_frame, height=1, bg="#636e72")
        control_separator.pack(fill=tk.X, padx=10, pady=5)
        
        speed_frame = tk.Frame(pseudo_frame, bg="#2d3436")
        speed_frame.pack(fill=tk.X, padx=10, pady=2)
        
        speed_label = tk.Label(speed_frame, text="动画速度:", font=("Arial", 9), 
                              bg="#2d3436", fg="#dfe6e9")
        speed_label.pack(side=tk.LEFT)
        
        self.speed_var = tk.DoubleVar(value=self.animation_speed)
        speed_scale = tk.Scale(speed_frame, from_=0.01, to=0.1, resolution=0.01, 
                              orient=tk.HORIZONTAL, variable=self.speed_var,
                              command=self._update_speed, length=140,
                              bg="#2d3436", fg="#dfe6e9", highlightthickness=0,
                              troughcolor="#1e272e", activebackground="#00b894")
        speed_scale.pack(side=tk.RIGHT, padx=5)
    
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
        
        if op_type == 'push':
            pseudo_lines = get_push_pseudocode(
                self.current_code_language, 
                ctx.get('value'), 
                ctx.get('top'), 
                ctx.get('capacity'),
                ctx.get('will_expand', False),
                ctx.get('new_cap')
            )
            self.set_pseudo_code(ctx.get('title', '入栈操作'), pseudo_lines)
        elif op_type == 'pop':
            pseudo_lines = get_pop_pseudocode(
                self.current_code_language,
                ctx.get('top'),
                ctx.get('capacity')
            )
            self.set_pseudo_code(ctx.get('title', '出栈操作'), pseudo_lines)
        elif op_type == 'clear':
            pseudo_lines = get_clear_pseudocode(
                self.current_code_language,
                ctx.get('count')
            )
            self.set_pseudo_code(ctx.get('title', '清空栈'), pseudo_lines)
        
        # 恢复高亮状态
        if ctx.get('highlight_line', -1) >= 0:
            self.highlight_pseudo_line(ctx['highlight_line'], delay=False)
    
    def _update_speed(self, value):
        """更新动画速度"""
        self.animation_speed = float(value)
    
    def set_pseudo_code(self, title, lines):
        """设置要显示的伪代码"""
        self.pseudo_code_lines = lines
        self.current_highlight_line = -1
        
        self.operation_label.config(text=title, fg="#74b9ff")
        self.status_indicator.config(text="🟢 执行中", fg="#00b894")
        
        self.pseudo_text.config(state=tk.NORMAL)
        self.pseudo_text.delete(1.0, tk.END)
        
        for i, line in enumerate(lines):
            line_text = str(line) if not isinstance(line, dict) else line.get("text", "")
            line_num = f"{i+1:2}. "
            self.pseudo_text.insert(tk.END, line_num, "pending")
            self.pseudo_text.insert(tk.END, line_text + "\n", "pending")
        
        self.pseudo_text.config(state=tk.DISABLED)
        self.progress_label.config(text=f"步骤: 0/{len(lines)}")
        self.window.update()
    
    def highlight_pseudo_line(self, line_index, delay=True):
        """高亮指定行的伪代码"""
        if not self.pseudo_code_lines or line_index < 0 or line_index >= len(self.pseudo_code_lines):
            return
        
        self.pseudo_text.config(state=tk.NORMAL)
        
        for i in range(len(self.pseudo_code_lines)):
            start_pos = f"{i+1}.0"
            end_pos = f"{i+1}.end"
            self.pseudo_text.tag_remove("highlight", start_pos, end_pos)
            self.pseudo_text.tag_remove("pending", start_pos, end_pos)
            self.pseudo_text.tag_remove("executed", start_pos, end_pos)
            
            if i < line_index:
                self.pseudo_text.tag_add("executed", start_pos, end_pos)
            elif i == line_index:
                self.pseudo_text.tag_add("highlight", start_pos, end_pos)
            else:
                self.pseudo_text.tag_add("pending", start_pos, end_pos)
        
        self.pseudo_text.config(state=tk.DISABLED)
        self.pseudo_text.see(f"{line_index+1}.0")
        
        self.current_highlight_line = line_index
        self.progress_label.config(text=f"步骤: {line_index+1}/{len(self.pseudo_code_lines)}")
        self.window.update()
        
        if delay:
            time.sleep(self.animation_speed * 3)
    
    def complete_pseudo_code(self):
        """标记伪代码执行完成"""
        self.pseudo_text.config(state=tk.NORMAL)
        
        for i in range(len(self.pseudo_code_lines)):
            start_pos = f"{i+1}.0"
            end_pos = f"{i+1}.end"
            self.pseudo_text.tag_remove("highlight", start_pos, end_pos)
            self.pseudo_text.tag_remove("pending", start_pos, end_pos)
            self.pseudo_text.tag_add("executed", start_pos, end_pos)
        
        self.pseudo_text.config(state=tk.DISABLED)
        self.status_indicator.config(text="✅ 完成", fg="#55efc4")
        self.progress_label.config(text=f"步骤: {len(self.pseudo_code_lines)}/{len(self.pseudo_code_lines)}")
        self.window.update()
    
    def clear_pseudo_code(self):
        """清除伪代码显示"""
        self.pseudo_code_lines = []
        self.current_highlight_line = -1
        
        self.operation_label.config(text="等待操作...", fg="#dfe6e9")
        self.status_indicator.config(text="⚫ 空闲", fg="#b2bec3")
        self.progress_label.config(text="步骤: 0/0")
        
        self.pseudo_text.config(state=tk.NORMAL)
        self.pseudo_text.delete(1.0, tk.END)
        self.pseudo_text.config(state=tk.DISABLED)
        self.window.update()

    def create_heading(self):
        # 当嵌入主应用时，主应用已有标题栏，无需重复创建
        pass

    def create_buttons(self):
        """
        创建底部按钮区域
        
        调整说明：
        - 原来的按钮直接贴在主窗口上，在深色主题下会显得一整条很“厚重 / 很深”
        - 这里增加一层浅色卡片容器，让按钮区域整体更轻、更干净
        """
        # 外层控制面板（跟随整体背景）
        control_panel = tk.Frame(self.window, bg=self.bg_color)
        control_panel.pack(fill=tk.X, padx=10, pady=(0, 8))

        # 浅色卡片容器，让按钮区域从背景中"浮起来"
        button_card = tk.Frame(
            control_panel,
            bg="#FFFFFF",
            highlightbackground="#E5E7EB",   # 更浅的边框色
            highlightthickness=1,
            bd=0
        )
        button_card.pack(fill=tk.X, expand=False)

        # 使用 tk.Frame 确保背景色一致为白色
        button_frame = tk.Frame(button_card, bg="#FFFFFF")
        button_frame.pack(fill=tk.X, padx=12, pady=10)

        btn_padding = (10, 8) 
        
        self.push_btn = ttk.Button(button_frame, text="入栈 (Push)",
                                   style="success.TButton", padding=btn_padding,
                                   command=self.prepare_push)
        self.push_btn.grid(row=0, column=0, padx=20, pady=8)

        self.pop_btn = ttk.Button(button_frame, text="出栈 (Pop)",
                                  style="danger.TButton", padding=btn_padding,
                                  command=self.pop)
        self.pop_btn.grid(row=0, column=1, padx=20, pady=8)

        self.clear_btn = ttk.Button(button_frame, text="清空栈",
                                    style="warning.TButton", padding=btn_padding,
                                    command=self.clear_stack)
        self.clear_btn.grid(row=0, column=2, padx=20, pady=8)

        self.back_btn = ttk.Button(button_frame, text="返回主界面",
                                   style="primary.TButton", padding=btn_padding,
                                   command=self.back_to_main)
        self.back_btn.grid(row=0, column=3, padx=20, pady=8)
        
        # 保存/打开 按钮
        ttk.Button(button_frame, text="保存栈", style="info.TButton", padding=btn_padding,
                   command=self.save_structure).grid(row=0, column=4, padx=20, pady=8)
        ttk.Button(button_frame, text="打开栈", style="info.TButton", padding=btn_padding,
                   command=self.load_structure).grid(row=0, column=5, padx=20, pady=8)

        # --- 美化: 6. 使用 tk.Label 确保白色背景 ---
        batch_label = tk.Label(button_frame, text="批量构建 (逗号分隔):", font=self.font_normal, bg="#FFFFFF", fg="#374151")
        batch_label.grid(row=1, column=0, padx=(20, 4), pady=10, sticky="e")
        
        batch_entry = ttk.Entry(button_frame, textvariable=self.batch_entry_var, width=40, font=self.font_normal)
        batch_entry.grid(row=1, column=1, columnspan=2, padx=4, pady=10, sticky="w")
        
        self.batch_build_btn = ttk.Button(button_frame, text="开始批量构建",
                                          command=self.start_batch_build)
        self.batch_build_btn.grid(row=1, column=3, padx=10, pady=10)
        
        # 自动扩容选项 - 使用自定义样式确保白色背景
        self.style.configure("White.TCheckbutton", background="#FFFFFF")
        self.auto_expand_check = ttk.Checkbutton(
            button_frame, text="🔄 自动扩容", 
            variable=self.auto_expand_var,
            command=self._toggle_auto_expand,
            style="White.TCheckbutton"
        )
        self.auto_expand_check.grid(row=1, column=4, padx=10, pady=10, sticky="w")
        
        # 容量显示
        self.capacity_label = tk.Label(button_frame, text=f"容量: {self.capacity}", font=self.font_small, bg="#FFFFFF", fg="#374151")
        self.capacity_label.grid(row=1, column=5, padx=10, pady=10, sticky="w")

        # 后缀表达式求值输入行
        postfix_label = tk.Label(button_frame, text="后缀表达式:", font=self.font_normal, bg="#FFFFFF", fg="#374151")
        postfix_label.grid(row=2, column=0, padx=(20, 4), pady=10, sticky="e")
        
        postfix_entry = ttk.Entry(button_frame, textvariable=self.postfix_var, width=40, font=self.font_normal)
        postfix_entry.grid(row=2, column=1, columnspan=2, padx=4, pady=10, sticky="w")
        postfix_entry.bind("<Return>", lambda e: self.start_postfix_eval())
        
        self.eval_btn = ttk.Button(button_frame, text="求值演示",
                                   style="info.TButton", padding=btn_padding,
                                   command=self.start_postfix_eval)
        self.eval_btn.grid(row=2, column=3, padx=10, pady=10)
        
        # 后缀表达式示例提示
        hint_label = tk.Label(button_frame, text="例: 3 4 + 2 * 或 5 1 2 + 4 * + 3 -", 
                              font=self.font_small, bg="#FFFFFF", fg="#666666")
        hint_label.grid(row=2, column=4, columnspan=2, padx=4, pady=10, sticky="w")

        # 括号匹配检验输入行
        bracket_label = tk.Label(button_frame, text="括号匹配:", font=self.font_normal, bg="#FFFFFF", fg="#374151")
        bracket_label.grid(row=3, column=0, padx=(20, 4), pady=10, sticky="e")
        
        bracket_entry = ttk.Entry(button_frame, textvariable=self.bracket_var, width=40, font=self.font_normal)
        bracket_entry.grid(row=3, column=1, columnspan=2, padx=4, pady=10, sticky="w")
        bracket_entry.bind("<Return>", lambda e: self.start_bracket_match())
        
        self.bracket_match_btn = ttk.Button(button_frame, text="检验匹配",
                                            style="info.TButton", padding=btn_padding,
                                            command=self.start_bracket_match)
        self.bracket_match_btn.grid(row=3, column=3, padx=10, pady=10)
        
        # 括号匹配示例提示
        bracket_hint = tk.Label(button_frame, text="例: {a+(b-c)*2} 或 [(a+b)*(c-d)]", 
                                font=self.font_small, bg="#FFFFFF", fg="#666666")
        bracket_hint.grid(row=3, column=4, columnspan=2, padx=4, pady=10, sticky="w")

        # DFS可视化按钮
        dfs_label = tk.Label(button_frame, text="图遍历演示:", font=self.font_normal, bg="#FFFFFF", fg="#374151")
        dfs_label.grid(row=4, column=0, padx=(20, 4), pady=10, sticky="e")
        
        self.dfs_btn = ttk.Button(button_frame, text="🌲 DFS深度优先遍历",
                                  style="primary.TButton", padding=btn_padding,
                                  command=self._open_dfs_visualizer)
        self.dfs_btn.grid(row=4, column=1, padx=10, pady=10, sticky="w")
        
        dfs_hint = tk.Label(button_frame, text="使用栈实现DFS算法可视化 - 展示深度优先遍历的工作原理", 
                            font=self.font_small, bg="#FFFFFF", fg="#666666")
        dfs_hint.grid(row=4, column=2, columnspan=3, padx=4, pady=10, sticky="w")

        # DSL 输入行
        dsl_label = tk.Label(button_frame, text="DSL 命令:", font=self.font_normal, bg="#FFFFFF", fg="#374151")
        dsl_label.grid(row=5, column=0, padx=(20, 4), pady=10, sticky="e")
        
        dsl_entry = ttk.Entry(button_frame, textvariable=self.dsl_var, width=60, font=self.font_normal)
        dsl_entry.grid(row=5, column=1, columnspan=3, padx=4, pady=10, sticky="w")
        dsl_entry.bind("<Return>", self.process_dsl)
        
        ttk.Button(button_frame, text="执行", command=self.process_dsl).grid(row=5, column=4, padx=10, pady=10)

    def process_dsl(self, event=None):
        text = self.dsl_var.get().strip()
        try:
            process_command(self, text)
        finally:
            self.dsl_var.set("")
    
    def _open_dfs_visualizer(self):
        """打开DFS深度优先遍历可视化窗口"""
        if self.animating:
            messagebox.showinfo("提示", "当前正在执行动画，请稍后再试")
            return
        open_dfs_visualizer(self.window, self.model, self.current_code_language)
    
    def _toggle_auto_expand(self):
        """切换自动扩容设置"""
        self.model.auto_expand = self.auto_expand_var.get()
        status = "开启" if self.model.auto_expand else "关闭"
        # 更新显示
        self.update_display()
    
    def animate_expansion(self, old_capacity, new_capacity, callback=None):
        """
        动画展示栈的扩容过程
        
        Args:
            old_capacity: 旧容量
            new_capacity: 新容量
            callback: 扩容完成后的回调函数
        """
        # 在画布上显示扩容提示
        canvas_width = self.canvas.winfo_width() or 1000
        canvas_height = self.canvas.winfo_height() or 420
        
        # 创建扩容动画背景遮罩
        overlay = self.canvas.create_rectangle(
            0, 0, canvas_width, canvas_height,
            fill="#000000", stipple="gray50", tags="expansion_anim"
        )
        
        # 扩容提示框
        box_width = 400
        box_height = 150
        box_x = (canvas_width - box_width) // 2
        box_y = (canvas_height - box_height) // 2
        
        box = self.canvas.create_rectangle(
            box_x, box_y, box_x + box_width, box_y + box_height,
            fill="#FFF3E0", outline="#FF9800", width=3, tags="expansion_anim"
        )
        
        # 扩容标题
        title = self.canvas.create_text(
            box_x + box_width/2, box_y + 30,
            text="🔄 栈容量扩展中...", 
            font=("微软雅黑", 16, "bold"), fill="#E65100",
            tags="expansion_anim"
        )
        
        # 容量变化显示
        capacity_text = self.canvas.create_text(
            box_x + box_width/2, box_y + 70,
            text=f"{old_capacity} → {new_capacity}",
            font=("Consolas", 24, "bold"), fill="#FF5722",
            tags="expansion_anim"
        )
        
        # 进度条背景
        progress_bg = self.canvas.create_rectangle(
            box_x + 50, box_y + 105, box_x + box_width - 50, box_y + 125,
            fill="#FFCCBC", outline="#FF8A65", tags="expansion_anim"
        )
        
        # 进度条
        progress_width = 0
        max_progress_width = box_width - 100
        progress_bar = self.canvas.create_rectangle(
            box_x + 50, box_y + 105, box_x + 50, box_y + 125,
            fill="#FF5722", outline="", tags="expansion_anim"
        )
        
        self.window.update()
        
        # 动画更新进度条
        total_steps = 20
        step_delay = 30
        
        def animate_step(step_i=0):
            nonlocal progress_width
            if step_i <= total_steps:
                progress_width = (step_i / total_steps) * max_progress_width
                self.canvas.coords(
                    progress_bar,
                    box_x + 50, box_y + 105,
                    box_x + 50 + progress_width, box_y + 125
                )
                self.window.update()
                self.window.after(step_delay, lambda: animate_step(step_i + 1))
            else:
                # 扩容完成，显示成功
                self.canvas.itemconfig(title, text="✅ 扩容完成!")
                self.window.update()
                
                # 短暂延迟后清除动画元素
                def cleanup():
                    self.canvas.delete("expansion_anim")
                    # 更新实际容量
                    self.capacity = new_capacity
                    self.model.set_capacity(new_capacity)
                    self.update_display()
                    self.window.update()
                    if callback:
                        callback()
                
                self.window.after(400, cleanup)
        
        animate_step()

    def _ensure_stack_folder(self):
        default_dir = storage.ensure_save_subdir("stack") if hasattr(storage, "ensure_save_subdir") else os.path.join(os.path.dirname(os.path.abspath(__file__)), "save", "stack")
        os.makedirs(default_dir, exist_ok=True)
        return default_dir

    def save_structure(self):
        data = list(self.model.data) if hasattr(self.model, "data") else []
        meta = {"capacity": self.capacity, "top": getattr(self.model, "top", len(data) - 1)}
        default_dir = self._ensure_stack_folder()
        default_name = f"stack_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = filedialog.asksaveasfilename(
            initialdir=default_dir,
            initialfile=default_name,
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="保存栈到文件"
        )
        if not filepath: return 
        payload = {"type": "stack", "data": data, "metadata": meta}
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)
            messagebox.showinfo("成功", f"栈已保存到：\n{filepath}")
        except Exception as e:
            messagebox.showerror("保存失败", f"发生错误：{e}")


    def load_structure(self):
        default_dir = self._ensure_stack_folder()
        filepath = filedialog.askopenfilename(
            initialdir=default_dir,
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="从文件加载栈"
        )
        if not filepath: return 
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                loaded = json.load(f)
            
            if loaded.get("type") != "stack":
                messagebox.showwarning("文件错误", "文件类型不匹配，请选择正确的栈 (stack) JSON 文件。")
                return

            data_list = loaded.get("data", [])
            self.model = StackModel(self.capacity) 
            for item in data_list:
                self.model.push(item) 

            self.update_display()
            messagebox.showinfo("成功", f"已加载 {len(self.model.data)} 个元素到栈")
        except Exception as e:
            messagebox.showerror("加载失败", f"无法读取或解析文件：{e}")


    def prepare_push(self):
        if self.animating:
            return
        is_full = self.model.is_full()
        # 只有在栈满且自动扩容关闭时才阻止操作
        if is_full and not self.model.auto_expand:
            messagebox.showwarning("栈满", "栈已满，无法执行入栈操作\n💡 提示：可以开启「自动扩容」功能")
            return
        if self.input_frame:
            try:
                self.input_frame.destroy()
            except Exception:
                pass
            self.input_frame = None

        self.value_entry.set("")

        # --- 美化: 7. 使用 ttk.Frame ---
        self.input_frame = ttk.Frame(self.window, padding=10)
        self.input_frame.pack(pady=5)

        value_label = ttk.Label(self.input_frame, text="输入要入栈的值:", font=self.font_normal)
        value_label.grid(row=0, column=0, padx=5, pady=5)

        value_entry = ttk.Entry(self.input_frame, textvariable=self.value_entry, font=self.font_normal)
        value_entry.grid(row=0, column=1, padx=5, pady=5)

        self.confirm_btn = ttk.Button(self.input_frame, text="确认",
                                      style="success.TButton",
                                      command=self.on_confirm_push) # 修正：原代码有个笔误 _on_confirm_push
        self.confirm_btn.grid(row=0, column=2, padx=5, pady=5)

        value_entry.focus()

    def on_confirm_push(self): # 修正：原代码有个笔误 _on_confirm_push
        value = self.value_entry.get()
        if not value:
            messagebox.showerror("错误", "请输入一个值")
            return
        if self.input_frame:
            try:
                self.input_frame.destroy()
            except Exception:
                pass
            self.input_frame = None
            self.confirm_btn = None
        self.animate_push_left(value)

    def animate_push_left(self, value, on_finish=None, show_pseudo=True):
        if self.animating:
            return
        self.animating = True
        self._set_buttons_state("disabled")
        
        # 检查是否需要扩容
        will_expand = self.model.is_full() and self.model.auto_expand
        old_capacity = self.capacity
        new_cap = int(self.capacity * self.model.expand_factor) if will_expand else self.capacity
        
        # 获取多语言伪代码
        top = self.model.top
        pseudo_lines = get_push_pseudocode(
            self.current_code_language, value, top, self.capacity, will_expand, new_cap
        )
        
        # 保存操作上下文，用于语言切换时重新渲染
        self.current_operation_context = {
            'type': 'push',
            'value': value,
            'top': top,
            'capacity': self.capacity,
            'will_expand': will_expand,
            'new_cap': new_cap,
            'title': f"入栈操作: Push({value})",
            'highlight_line': 1
        }
        
        if show_pseudo:
            self.set_pseudo_code(f"入栈操作: Push({value})", pseudo_lines)
            self.highlight_pseudo_line(0)
            self.highlight_pseudo_line(1)
        
        # 如果需要扩容，先显示扩容动画
        if will_expand:
            if show_pseudo:
                self.highlight_pseudo_line(2)
                self.highlight_pseudo_line(3)
            
            # 使用新的扩容动画
            def after_expansion():
                if show_pseudo:
                    self.highlight_pseudo_line(4)
                self._do_push_animation(value, on_finish, show_pseudo, will_expand)
            
            self.animate_expansion(old_capacity, new_cap, callback=after_expansion)
        else:
            if show_pseudo:
                self.highlight_pseudo_line(2)
            self._do_push_animation(value, on_finish, show_pseudo, will_expand)
    
    def _do_push_animation(self, value, on_finish, show_pseudo, will_expand):
        """执行实际的入栈动画"""
        start_x = - (self.cell_width + 20)
        start_y = self.start_y
        target_idx = len(self.model.data)
        target_x = self.start_x + target_idx * (self.cell_width + self.spacing)

        # 创建入栈元素 - 使用渐变色效果
        rect_id = self.canvas.create_rectangle(
            start_x, start_y, start_x + self.cell_width, start_y + self.cell_height,
            fill="#90EE90", outline="#228B22", width=3
        )
        text_id = self.canvas.create_text(
            start_x + self.cell_width/2, start_y + self.cell_height/2,
            text=str(value), font=self.font_normal_bold, fill="#006400"
        )
        
        # 添加入栈指示箭头
        arrow_id = self.canvas.create_text(
            start_x + self.cell_width/2, start_y - 25,
            text="⬇️ 入栈", font=("微软雅黑", 10, "bold"), fill="#228B22"
        )
        
        # 步骤: top++
        if show_pseudo:
            line_idx = 5 if will_expand else 3
            self.highlight_pseudo_line(line_idx, delay=False)

        total_steps = 35  # 增加步数使动画更流畅
        dx = (target_x - start_x) / total_steps
        step_delay = 15  # 稍微减慢

        def step(step_i=0):
            if step_i < total_steps:
                self.canvas.move(rect_id, dx, 0)
                self.canvas.move(text_id, dx, 0)
                self.canvas.move(arrow_id, dx, 0)
                
                # 动态改变颜色增加视觉效果
                progress = step_i / total_steps
                if progress > 0.7:
                    self.canvas.itemconfig(rect_id, fill="#7CFC00")  # 快到位时变亮
                
                self.window.after(step_delay, lambda: step(step_i + 1))
            else:
                # 步骤: 存入新元素
                if show_pseudo:
                    line_idx = 6 if will_expand else 4
                    self.highlight_pseudo_line(line_idx, delay=False)
                
                # 闪烁效果表示成功入栈
                def flash(count=0):
                    if count < 4:
                        color = "#FFFF00" if count % 2 == 0 else "#90EE90"
                        self.canvas.itemconfig(rect_id, fill=color)
                        self.window.after(100, lambda: flash(count + 1))
                    else:
                        # 清除动画元素
                        try:
                            self.canvas.delete(rect_id)
                            self.canvas.delete(text_id)
                            self.canvas.delete(arrow_id)
                        except Exception:
                            pass
                        
                        result = self.model.push(value)
                        success = result[0] if isinstance(result, tuple) else result
                        
                        if not success:
                            messagebox.showwarning("栈满", "入栈失败：栈已满（自动扩容已关闭）")

                        self.update_display()
                        
                        # 高亮新入栈的元素
                        if self.stack_rectangles:
                            new_idx = len(self.stack_rectangles) - 1
                            if new_idx >= 0:
                                self.canvas.itemconfig(self.stack_rectangles[new_idx], fill="#98FB98")
                        
                        # 步骤: 完成
                        if show_pseudo:
                            line_idx = 7 if will_expand else 5
                            self.highlight_pseudo_line(line_idx)
                            self.complete_pseudo_code()
                        
                        self.animating = False
                        if on_finish:
                            on_finish()
                        else:
                            self._set_buttons_state("normal")
                
                flash()
        step()

    def pop(self):
        if self.animating:
            return
        empty = self.model.is_empty()
        if empty:
            messagebox.showwarning("栈空", "栈已空，无法执行出栈操作")
            return
        self.animate_pop_right()

    def animate_pop_right(self):
        if self.animating:
            return
        self.animating = True
        self._set_buttons_state("disabled")

        top_idx = getattr(self.model, "top", len(self.model.data) - 1)
        if top_idx < 0 or top_idx >= len(self.stack_rectangles): 
            self.animating = False
            self._set_buttons_state("normal")
            self.update_display() 
            return
        
        # 获取栈顶元素值
        top_value = self.model.data[top_idx] if top_idx < len(self.model.data) else "?"
        
        # 获取多语言伪代码
        pseudo_lines = get_pop_pseudocode(self.current_code_language, top_idx, self.capacity)
        
        # 保存操作上下文
        self.current_operation_context = {
            'type': 'pop',
            'top': top_idx,
            'capacity': self.capacity,
            'title': f"出栈操作: Pop() → {top_value}",
            'highlight_line': 0
        }
        
        self.set_pseudo_code(f"出栈操作: Pop() → {top_value}", pseudo_lines)
        
        # 步骤1-2: 检查栈是否空
        self.highlight_pseudo_line(0)
        self.highlight_pseudo_line(1)
        self.highlight_pseudo_line(2)
        
        # 步骤3: 取出元素
        self.highlight_pseudo_line(3)

        rect_id = self.stack_rectangles[top_idx]
        text_id = self.stack_labels[top_idx]
        
        # 先高亮要出栈的元素 - 闪烁提示
        def highlight_element(count=0):
            if count < 4:
                color = "#FFD700" if count % 2 == 0 else "#FF6347"  # 金色和番茄色交替
                self.canvas.itemconfig(rect_id, fill=color)
                self.window.after(150, lambda: highlight_element(count + 1))
            else:
                self.canvas.itemconfig(rect_id, fill="#FF6347")  # 番茄红色
                
                # 添加出栈指示箭头
                coords = self.canvas.coords(rect_id)
                arrow_x = coords[0] + self.cell_width / 2
                arrow_y = coords[1] - 25
                arrow_id = self.canvas.create_text(
                    arrow_x, arrow_y,
                    text="⬆️ 出栈", font=("微软雅黑", 10, "bold"), fill="#DC143C"
                )
                
                # 开始移动动画
                self.window.after(300, lambda: start_move_animation(arrow_id))
        
        def start_move_animation(arrow_id):
            total_steps = 30
            canvas_width = self.canvas.winfo_width() or 1000
            target_x = canvas_width + self.cell_width
            current_x = self.canvas.coords(rect_id)[0]
            dx = (target_x - current_x) / total_steps
            dy = -2  # 同时稍微向上移动
            step_delay = 12

            def step(step_i=0):
                if step_i < total_steps:
                    self.canvas.move(rect_id, dx, dy if step_i < 10 else 0)
                    self.canvas.move(text_id, dx, dy if step_i < 10 else 0)
                    self.canvas.move(arrow_id, dx, dy if step_i < 10 else 0)
                    
                    # 渐变颜色效果
                    progress = step_i / total_steps
                    if progress > 0.5:
                        # 逐渐变淡
                        alpha = int(255 * (1 - (progress - 0.5) * 2))
                        # 由于tkinter不支持透明度，用颜色变化模拟
                        self.canvas.itemconfig(rect_id, fill="#FFA07A")  # 浅橙色
                    
                    self.window.after(step_delay, lambda: step(step_i + 1))
                else:
                    # 步骤4: top--
                    self.highlight_pseudo_line(4, delay=False)
                    
                    # 清除箭头
                    try:
                        self.canvas.delete(arrow_id)
                    except:
                        pass
                    
                    popped_value = self.model.pop()
                    self.update_display()
                    
                    # 显示返回值提示
                    self._show_return_value(popped_value)
                    
                    # 步骤5: 返回值
                    self.highlight_pseudo_line(5)
                    self.complete_pseudo_code()
                    
                    self.animating = False
                    self._set_buttons_state("normal")
            step()
        
        highlight_element()
    
    def _show_return_value(self, value):
        """在画布上短暂显示返回值"""
        canvas_width = self.canvas.winfo_width() or 1000
        
        # 创建返回值提示框
        box_x = canvas_width - 180
        box_y = 20
        
        box = self.canvas.create_rectangle(
            box_x, box_y, box_x + 160, box_y + 60,
            fill="#E8F5E9", outline="#4CAF50", width=2,
            tags="return_value"
        )
        
        label = self.canvas.create_text(
            box_x + 80, box_y + 18,
            text="返回值:", font=("微软雅黑", 10),
            fill="#388E3C", tags="return_value"
        )
        
        value_text = self.canvas.create_text(
            box_x + 80, box_y + 42,
            text=str(value), font=("Consolas", 16, "bold"),
            fill="#1B5E20", tags="return_value"
        )
        
        # 2秒后自动消失
        def remove_hint():
            self.canvas.delete("return_value")
        
        self.window.after(2000, remove_hint)

    def clear_stack(self):
        if self.animating:
            return
        empty = self.model.is_empty()
        if empty:
            messagebox.showinfo("信息", "栈已为空")
            return
        
        n = len(self.model.data)
        
        # 获取多语言伪代码
        pseudo_lines = get_clear_pseudocode(self.current_code_language, n)
        
        # 保存操作上下文
        self.current_operation_context = {
            'type': 'clear',
            'count': n,
            'title': f"清空栈: 移除 {n} 个元素",
            'highlight_line': 0
        }
        
        self.set_pseudo_code(f"清空栈: 移除 {n} 个元素", pseudo_lines)
        self.highlight_pseudo_line(0)
        self.highlight_pseudo_line(1)
        
        self._set_buttons_state("disabled")
        self._clear_step()

    def _clear_step(self):
        if getattr(self.model, "is_empty", lambda: len(self.model.data) == 0)():
            # 清空完成
            self.highlight_pseudo_line(3)
            self.complete_pseudo_code()
            self._set_buttons_state("normal")
            return
        
        if self.animating:
             self.window.after(50, self._clear_step) 
             return
        
        # 高亮Pop行
        self.highlight_pseudo_line(2, delay=False)
        self.animate_pop_right() 

        def poll():
            if self.animating:
                self.window.after(80, poll) 
            else:
                self.window.after(120, self._clear_step) 
        poll()

    def start_batch_build(self):
        if self.animating:
            return
        text = self.batch_entry_var.get().strip()
        if not text:
            messagebox.showinfo("提示", "请输入要构建的值，例如：1,2,3")
            return
        items = [s.strip() for s in text.split(",") if s.strip() != ""]
        if not items:
            messagebox.showinfo("提示", "未解析到有效值")
            return
        
        available = self.capacity - len(self.model.data)
        # 如果自动扩容开启，则不需要限制数量
        if not self.model.auto_expand and len(items) > available:
            if not messagebox.askyesno("容量不足", 
                f"当前可用位置 {available}，要入栈 {len(items)} 个。\n"
                f"是否只入栈前 {available} 个？\n\n"
                f"💡 提示：开启「自动扩容」可自动增加容量"):
                return
            items = items[:available]
        
        self.batch_queue = items
        self.batch_index = 0
        self._set_buttons_state("disabled")
        self._batch_step()

    def _batch_step(self):
        if self.batch_index >= len(self.batch_queue):
            self.batch_queue = []
            self.batch_index = 0
            self._set_buttons_state("normal")
            return
        value = self.batch_queue[self.batch_index]
        self.batch_index += 1
        self.animate_push_left(value, on_finish=self._batch_step)

    # ==================== 后缀表达式求值功能 ====================
    
    def _is_operator(self, token):
        """判断是否为运算符"""
        return token in ('+', '-', '*', '/', '%', '^', '**')
    
    def _is_number(self, token):
        """判断是否为数字"""
        try:
            float(token)
            return True
        except ValueError:
            return False
    
    def _parse_postfix(self, expression):
        """解析后缀表达式，返回token列表"""
        # 支持空格分隔的表达式
        tokens = expression.strip().split()
        parsed = []
        for token in tokens:
            token = token.strip()
            if not token:
                continue
            if self._is_operator(token):
                parsed.append(('op', token))
            elif self._is_number(token):
                parsed.append(('num', float(token) if '.' in token else int(token)))
            else:
                # 尝试作为变量名或字符处理
                parsed.append(('var', token))
        return parsed
    
    def _apply_operator(self, op, a, b):
        """应用运算符"""
        if op == '+':
            return a + b
        elif op == '-':
            return a - b
        elif op == '*':
            return a * b
        elif op == '/':
            if b == 0:
                raise ValueError("除数不能为零")
            return a / b
        elif op == '%':
            return a % b
        elif op in ('^', '**'):
            return a ** b
        else:
            raise ValueError(f"未知运算符: {op}")
    
    def start_postfix_eval(self, expression=None):
        """开始后缀表达式求值演示"""
        if self.animating:
            messagebox.showinfo("提示", "当前正在执行动画，请稍后再试")
            return
        
        if expression is None:
            expression = self.postfix_var.get().strip()
        
        if not expression:
            messagebox.showinfo("提示", "请输入后缀表达式\n例如: 3 4 + 2 *")
            return
        
        # 解析表达式
        try:
            tokens = self._parse_postfix(expression)
        except Exception as e:
            messagebox.showerror("解析错误", f"表达式格式错误: {e}")
            return
        
        if not tokens:
            messagebox.showinfo("提示", "表达式为空")
            return
        
        # 验证表达式
        if not self._validate_postfix(tokens):
            messagebox.showerror("表达式错误", "后缀表达式不合法，请检查操作数和运算符的数量")
            return
        
        # 清空当前栈
        self.model.clear()
        self.update_display()
        
        # 设置求值队列
        self.postfix_queue = tokens
        self.postfix_index = 0
        self.postfix_result = None
        self.postfix_expression = expression
        self.postfix_tokens_display = [str(t[1]) for t in tokens]  # 用于显示的token列表
        self.postfix_calc_history = []  # 计算历史
        
        # 显示整体伪代码和表达式
        self._show_postfix_algorithm(expression)
        self._update_expression_display(-1)  # 初始显示，无高亮
        
        # 开始动画
        self._set_buttons_state("disabled")
        self.window.after(800, self._postfix_step)
    
    def _validate_postfix(self, tokens):
        """验证后缀表达式是否合法"""
        stack_count = 0
        for token_type, _ in tokens:
            if token_type in ('num', 'var'):
                stack_count += 1
            elif token_type == 'op':
                if stack_count < 2:
                    return False
                stack_count -= 1  # 弹出2个，压入1个，净减少1个
        return stack_count == 1
    
    def _show_postfix_algorithm(self, expression):
        """显示后缀表达式求值算法"""
        pseudo_lines = [
            f"// 后缀表达式: {expression}",
            f"// 等价中缀式: {self._postfix_to_infix_hint(expression)}",
            "━━━━━━━━━━━━━━━━━━━━━━━━",
            "算法 EvaluatePostfix(expr):",
            "  Stack S = new Stack()",
            "  for each token in expr:",
            "    if (token 是数字):",
            "      S.push(token)",
            "    else:  // token 是运算符",
            "      b ← S.pop()  // 右操作数",
            "      a ← S.pop()  // 左操作数",
            "      result ← a ⊕ b",
            "      S.push(result)",
            "  return S.pop()"
        ]
        self.set_pseudo_code(f"📊 后缀表达式求值演示", pseudo_lines)
        self.highlight_pseudo_line(0)
        self.highlight_pseudo_line(1)
    
    def _postfix_to_infix_hint(self, expression):
        """尝试将后缀表达式转换为中缀提示（简化版）"""
        try:
            tokens = expression.strip().split()
            stack = []
            for token in tokens:
                if self._is_operator(token):
                    if len(stack) >= 2:
                        b = stack.pop()
                        a = stack.pop()
                        stack.append(f"({a}{token}{b})")
                    else:
                        return "无法转换"
                else:
                    stack.append(token)
            return stack[0] if stack else "空表达式"
        except:
            return "复杂表达式"
    
    def _update_expression_display(self, current_idx, calc_info=None):
        """在画布上更新表达式显示，高亮当前处理的token"""
        # 清除之前的表达式显示
        self.canvas.delete("expr_display")
        
        if not self.postfix_tokens_display:
            return
        
        # 表达式显示区域（放在右上角，不与左侧信息面板重叠）
        expr_start_x = 240
        expr_y = 20
        
        # 计算token显示宽度
        token_width = 38
        token_spacing = 5
        total_width = len(self.postfix_tokens_display) * (token_width + token_spacing) + 80
        
        # 绘制背景框
        self.canvas.create_rectangle(
            expr_start_x, expr_y, 
            expr_start_x + total_width, expr_y + 90,
            fill="#F5F5FF", outline="#6A5ACD", width=2,
            tags="expr_display"
        )
        
        # 标题
        self.canvas.create_text(
            expr_start_x + 10, expr_y + 12,
            text="📝 后缀表达式:", font=("微软雅黑", 10, "bold"),
            anchor="w", fill="#333", tags="expr_display"
        )
        
        # 绘制每个token
        token_x = expr_start_x + 15
        token_y = expr_y + 35
        for i, token in enumerate(self.postfix_tokens_display):
            # 确定颜色
            if i < current_idx:
                bg_color = "#90EE90"
                text_color = "#006400"
                status = "✓"
            elif i == current_idx:
                bg_color = "#FFD700"
                text_color = "#8B4513"
                status = "▶"
            else:
                bg_color = "#E6E6FA"
                text_color = "#666"
                status = ""
            
            # 绘制token背景
            self.canvas.create_rectangle(
                token_x, token_y, token_x + token_width, token_y + 30,
                fill=bg_color, outline="#888", width=1,
                tags="expr_display"
            )
            
            # 绘制token文本
            self.canvas.create_text(
                token_x + token_width/2, token_y + 15,
                text=str(token), font=("Consolas", 11, "bold"),
                fill=text_color, tags="expr_display"
            )
            
            # 绘制状态指示
            if status:
                self.canvas.create_text(
                    token_x + token_width/2, token_y + 42,
                    text=status, font=("Arial", 8),
                    fill=text_color, tags="expr_display"
                )
            
            token_x += token_width + token_spacing
        
        # 显示计算信息
        if calc_info:
            self.canvas.create_text(
                expr_start_x + 10, expr_y + 78,
                text=f"💡 {calc_info}", font=("微软雅黑", 9),
                anchor="w", fill="#8B4513", tags="expr_display"
            )
        
        self.window.update()
    
    def _postfix_step(self):
        """执行后缀表达式求值的一步"""
        if self.postfix_index >= len(self.postfix_queue):
            # 求值完成
            self._postfix_complete()
            return
        
        current_idx = self.postfix_index
        token_type, token_value = self.postfix_queue[self.postfix_index]
        self.postfix_index += 1
        
        # 更新表达式显示，高亮当前token
        if token_type in ('num', 'var'):
            self._update_expression_display(current_idx, f"读取操作数: {token_value}")
        else:
            self._update_expression_display(current_idx, f"读取运算符: {token_value}")
        
        self.window.after(400, lambda: self._postfix_process_token(token_type, token_value, current_idx))
    
    def _postfix_process_token(self, token_type, token_value, current_idx):
        """处理单个token"""
        if token_type in ('num', 'var'):
            # 操作数：入栈
            self._postfix_push_operand(token_value, current_idx)
        elif token_type == 'op':
            # 运算符：弹出两个操作数，计算，结果入栈
            self._postfix_apply_operator(token_value, current_idx)
    
    def _postfix_push_operand(self, value, current_idx):
        """后缀求值：操作数入栈"""
        # 计算当前步骤信息
        step_num = current_idx + 1
        total_steps = len(self.postfix_queue)
        stack_before = list(self.model.data)
        stack_after = stack_before + [value]
        
        # 设置详细伪代码
        detail_lines = [
            f"━━━ 步骤 {step_num}/{total_steps}: 遇到操作数 ━━━",
            f"",
            f"当前token: {value} (数字)",
            f"操作: Push({value})",
            f"",
            f"栈变化:",
            f"  之前: {self._format_stack(stack_before)}",
            f"  之后: {self._format_stack(stack_after)}",
            f"",
            f"执行: S.push({value})"
        ]
        self.set_pseudo_code(f"🔢 入栈操作数: {value}", detail_lines)
        self.highlight_pseudo_line(2)
        self.highlight_pseudo_line(3)
        
        # 更新表达式显示
        self._update_expression_display(current_idx, f"将 {value} 入栈")
        
        # 动画入栈
        self.animate_push_left(value, on_finish=lambda: self._postfix_after_push(current_idx), show_pseudo=False)
    
    def _format_stack(self, stack_data):
        """格式化栈显示"""
        if not stack_data:
            return "[空栈]"
        return "[" + " | ".join(str(x) for x in stack_data) + "] ← 栈顶"
    
    def _postfix_after_push(self, current_idx):
        """入栈动画完成后的回调"""
        self.highlight_pseudo_line(7)
        self.highlight_pseudo_line(9)
        self.complete_pseudo_code()
        # 更新表达式显示为已处理状态
        self._update_expression_display(current_idx + 1, f"✓ 入栈完成，栈: {self._format_stack(list(self.model.data))}")
        self.window.after(500, self._postfix_step)
    
    def _postfix_apply_operator(self, op, current_idx):
        """后缀求值：应用运算符"""
        if len(self.model.data) < 2:
            messagebox.showerror("错误", "栈中元素不足，无法执行运算")
            self._postfix_abort()
            return
        
        # 获取操作数（不弹出，先显示）
        b = self.model.data[-1]  # 右操作数（栈顶）
        a = self.model.data[-2]  # 左操作数
        
        try:
            # 确保是数字
            a_num = float(a) if isinstance(a, str) else a
            b_num = float(b) if isinstance(b, str) else b
            result = self._apply_operator(op, a_num, b_num)
            # 如果结果是整数，转为整数显示
            if isinstance(result, float) and result == int(result):
                result = int(result)
        except Exception as e:
            messagebox.showerror("计算错误", f"运算失败: {e}")
            self._postfix_abort()
            return
        
        # 计算步骤信息
        step_num = current_idx + 1
        total_steps = len(self.postfix_queue)
        stack_before = list(self.model.data)
        
        # 记录计算历史
        calc_str = f"{a} {op} {b} = {result}"
        self.postfix_calc_history.append(calc_str)
        
        # 显示详细伪代码
        detail_lines = [
            f"━━━ 步骤 {step_num}/{total_steps}: 遇到运算符 ━━━",
            f"",
            f"当前token: '{op}' (运算符)",
            f"",
            f"执行计算:",
            f"  ① b = Pop() → {b}  (右操作数,栈顶)",
            f"  ② a = Pop() → {a}  (左操作数)",
            f"  ③ 计算: {a} {op} {b} = {result}",
            f"  ④ Push({result})",
            f"",
            f"栈变化:",
            f"  之前: {self._format_stack(stack_before)}",
            f"  之后: {self._format_stack(stack_before[:-2] + [result])}"
        ]
        self.set_pseudo_code(f"⚙️ 执行运算: {a} {op} {b}", detail_lines)
        self.highlight_pseudo_line(2)
        self.highlight_pseudo_line(4)
        
        # 更新表达式显示
        self._update_expression_display(current_idx, f"计算: {a} {op} {b} = {result}")
        
        # 保存计算结果供后续使用
        self._pending_result = result
        self._pending_op = op
        self._pending_a = a
        self._pending_b = b
        self._pending_current_idx = current_idx
        
        # 开始弹出动画序列
        self.window.after(600, self._postfix_pop_first)
    
    def _get_op_name(self, op):
        """获取运算符名称"""
        names = {'+': '加法', '-': '减法', '*': '乘法', '/': '除法', '%': '取模', '^': '幂运算', '**': '幂运算'}
        return names.get(op, '运算')
    
    def _postfix_pop_first(self):
        """弹出第一个操作数（栈顶，右操作数）"""
        self.highlight_pseudo_line(5)
        self._update_expression_display(
            self._pending_current_idx, 
            f"① 弹出右操作数 b = {self._pending_b}"
        )
        
        # 执行弹出动画
        self._postfix_pop_animated(callback=self._postfix_pop_second)
    
    def _postfix_pop_second(self):
        """弹出第二个操作数（左操作数）"""
        self.highlight_pseudo_line(6)
        self._update_expression_display(
            self._pending_current_idx, 
            f"② 弹出左操作数 a = {self._pending_a}"
        )
        
        # 执行弹出动画
        self._postfix_pop_animated(callback=self._postfix_push_result)
    
    def _postfix_pop_animated(self, callback):
        """执行一次弹出动画"""
        if self.model.is_empty():
            callback()
            return
        
        self.animating = True
        top_idx = self.model.top
        
        if top_idx < 0 or top_idx >= len(self.stack_rectangles):
            self.model.pop()
            self.update_display()
            self.animating = False
            callback()
            return
        
        rect_id = self.stack_rectangles[top_idx]
        text_id = self.stack_labels[top_idx]
        self.canvas.itemconfig(rect_id, fill="#FFB6C1")  # 浅粉色表示即将弹出
        
        total_steps = 18
        canvas_width = self.canvas.winfo_width() or 1000
        target_x = canvas_width + self.cell_width
        current_x = self.canvas.coords(rect_id)[0]
        dx = (target_x - current_x) / total_steps
        step_delay = 8
        
        def step(step_i=0):
            if step_i < total_steps:
                self.canvas.move(rect_id, dx, 0)
                self.canvas.move(text_id, dx, 0)
                self.window.after(step_delay, lambda: step(step_i + 1))
            else:
                self.model.pop()
                self.update_display()
                self.animating = False
                self.window.after(150, callback)
        step()
    
    def _postfix_push_result(self):
        """压入计算结果"""
        result = self._pending_result
        a = self._pending_a
        b = self._pending_b
        op = self._pending_op
        
        self.highlight_pseudo_line(7)
        self._update_expression_display(
            self._pending_current_idx, 
            f"③ 计算: {a} {op} {b} = {result}"
        )
        self.window.after(500, lambda: self._do_push_result(result))
    
    def _do_push_result(self, result):
        """实际执行结果入栈"""
        self.highlight_pseudo_line(8)
        self._update_expression_display(
            self._pending_current_idx, 
            f"④ 将结果 {result} 入栈"
        )
        
        # 动画入栈结果
        self.animate_push_left(result, on_finish=lambda: self._postfix_after_operation(), show_pseudo=False)
    
    def _postfix_after_operation(self):
        """运算完成后的回调"""
        current_idx = self._pending_current_idx
        result = self._pending_result
        
        self.complete_pseudo_code()
        # 更新表达式显示，标记当前token已处理
        self._update_expression_display(
            current_idx + 1, 
            f"✓ 运算完成，结果 {result} 已入栈"
        )
        self.window.after(600, self._postfix_step)
    
    def _postfix_complete(self):
        """后缀表达式求值完成"""
        # 清除表达式显示
        self.canvas.delete("expr_display")
        
        if len(self.model.data) == 1:
            result = self.model.data[0]
            self.postfix_result = result
            
            # 构建计算历史字符串
            history_str = " → ".join(self.postfix_calc_history) if hasattr(self, 'postfix_calc_history') and self.postfix_calc_history else ""
            
            # 显示完成信息
            complete_lines = [
                f"━━━━━ 🎉 求值完成! ━━━━━",
                f"",
                f"原始表达式: {self.postfix_expression}",
                f"等价中缀式: {self._postfix_to_infix_hint(self.postfix_expression)}",
                f"",
                f"计算过程:",
            ]
            # 添加计算历史
            if hasattr(self, 'postfix_calc_history'):
                for i, calc in enumerate(self.postfix_calc_history, 1):
                    complete_lines.append(f"  {i}. {calc}")
            complete_lines.extend([
                f"",
                f"最终结果: {result}",
                f"",
                f"return {result}  ✓"
            ])
            
            self.set_pseudo_code(f"🎯 求值完成: {result}", complete_lines)
            for i in range(len(complete_lines)):
                self.highlight_pseudo_line(i, delay=False)
            self.complete_pseudo_code()
            
            # 高亮最终结果
            if self.stack_rectangles:
                self.canvas.itemconfig(self.stack_rectangles[0], fill="#90EE90")  # 浅绿色
            
            # 在画布上显示最终结果
            self._show_final_result(result)
            
            messagebox.showinfo("求值完成", 
                f"后缀表达式: {self.postfix_expression}\n"
                f"等价中缀式: {self._postfix_to_infix_hint(self.postfix_expression)}\n\n"
                f"计算结果: {result}")
        else:
            messagebox.showwarning("警告", f"求值结束但栈中剩余 {len(self.model.data)} 个元素，表达式可能不正确")
        
        self._set_buttons_state("normal")
        self.postfix_var.set("")
    
    def _show_final_result(self, result):
        """在画布上显示最终结果"""
        # 在画布右上角显示结果框
        result_x = 240
        result_y = 20
        
        self.canvas.create_rectangle(
            result_x, result_y, result_x + 280, result_y + 90,
            fill="#E8F5E9", outline="#4CAF50", width=3,
            tags="final_result"
        )
        self.canvas.create_text(
            result_x + 140, result_y + 25,
            text="🎯 计算结果", font=("微软雅黑", 12, "bold"),
            fill="#2E7D32", tags="final_result"
        )
        self.canvas.create_text(
            result_x + 140, result_y + 60,
            text=str(result), font=("Consolas", 24, "bold"),
            fill="#1B5E20", tags="final_result"
        )
    
    def _postfix_abort(self):
        """中止后缀表达式求值"""
        self.postfix_queue = []
        self.postfix_index = 0
        self.canvas.delete("expr_display")
        self.canvas.delete("final_result")
        self._set_buttons_state("normal")
        self.clear_pseudo_code()

    # ==================== 后缀表达式求值功能结束 ====================

    # ==================== 括号匹配检验功能 ====================
    
    def start_bracket_match(self, expression=None):
        """开始括号匹配检验演示"""
        if self.animating:
            messagebox.showinfo("提示", "当前正在执行动画，请稍后再试")
            return
        
        if expression is None:
            expression = self.bracket_var.get().strip()
        
        if not expression:
            messagebox.showinfo("提示", "请输入包含括号的表达式\n例如: {a+(b-c)*2} 或 [(a+b)*(c-d)]")
            return
        
        # 检查是否包含括号
        has_brackets = any(c in self.left_brackets or c in self.right_brackets for c in expression)
        if not has_brackets:
            messagebox.showinfo("提示", "表达式中没有发现括号\n支持的括号: ( ) [ ] { }")
            return
        
        # 清空当前栈
        self.model.clear()
        self.update_display()
        
        # 设置检验队列
        self.bracket_queue = list(expression)
        self.bracket_index = 0
        self.bracket_expression = expression
        self.bracket_error_info = None  # 错误信息
        
        # 显示算法伪代码
        self._show_bracket_algorithm(expression)
        self._update_bracket_display(-1)
        
        # 开始动画
        self._set_buttons_state("disabled")
        self.window.after(800, self._bracket_step)
    
    def _show_bracket_algorithm(self, expression):
        """显示括号匹配检验算法"""
        pseudo_lines = [
            f"// 表达式: {expression}",
            "━━━━━━━━━━━━━━━━━━━━━━━━",
            "算法 BracketMatch(expr):",
            "  Stack S = new Stack()",
            "  for each char c in expr:",
            "    if (c 是左括号 '(' '[' '{'):",
            "      S.push(c)",
            "    else if (c 是右括号 ')' ']' '}'):",
            "      if (S.isEmpty()):",
            "        return 不匹配(缺少左括号)",
            "      left ← S.pop()",
            "      if (left 与 c 不配对):",
            "        return 不匹配(类型错误)",
            "  if (!S.isEmpty()):",
            "    return 不匹配(缺少右括号)",
            "  return 匹配成功 ✓"
        ]
        self.set_pseudo_code("🔍 括号匹配检验", pseudo_lines)
        self.highlight_pseudo_line(0)
    
    def _update_bracket_display(self, current_idx, info=None, error_idx=-1):
        """在画布上更新表达式显示，高亮当前处理的字符"""
        self.canvas.delete("bracket_display")
        
        if not self.bracket_expression:
            return
        
        # 表达式显示区域
        expr_start_x = 240
        expr_y = 20
        
        # 计算字符显示宽度
        char_width = 28
        char_spacing = 3
        max_chars_per_row = 20
        total_chars = len(self.bracket_expression)
        
        # 计算需要的行数
        rows = (total_chars + max_chars_per_row - 1) // max_chars_per_row
        total_height = 60 + rows * 45
        total_width = min(total_chars, max_chars_per_row) * (char_width + char_spacing) + 40
        
        # 绘制背景框
        self.canvas.create_rectangle(
            expr_start_x, expr_y,
            expr_start_x + max(total_width, 300), expr_y + total_height,
            fill="#FFF8E7", outline="#D4A574", width=2,
            tags="bracket_display"
        )
        
        # 标题
        self.canvas.create_text(
            expr_start_x + 10, expr_y + 12,
            text="🔍 括号匹配检验:", font=("微软雅黑", 10, "bold"),
            anchor="w", fill="#333", tags="bracket_display"
        )
        
        # 绘制每个字符
        for i, char in enumerate(self.bracket_expression):
            row = i // max_chars_per_row
            col = i % max_chars_per_row
            char_x = expr_start_x + 15 + col * (char_width + char_spacing)
            char_y = expr_y + 35 + row * 38
            
            # 确定颜色
            is_bracket = char in self.left_brackets or char in self.right_brackets
            
            if i == error_idx:
                # 错误位置
                bg_color = "#FF6B6B"
                text_color = "#FFFFFF"
                outline_color = "#CC0000"
            elif i < current_idx:
                if is_bracket:
                    bg_color = "#90EE90"  # 已处理的括号-绿色
                    text_color = "#006400"
                else:
                    bg_color = "#E8E8E8"  # 已处理的非括号-灰色
                    text_color = "#666"
                outline_color = "#888"
            elif i == current_idx:
                bg_color = "#FFD700"  # 当前处理-金色
                text_color = "#8B4513"
                outline_color = "#B8860B"
            else:
                if is_bracket:
                    bg_color = "#E6F3FF"  # 待处理的括号-浅蓝
                    text_color = "#0066CC"
                else:
                    bg_color = "#F5F5F5"  # 待处理的非括号
                    text_color = "#888"
                outline_color = "#CCC"
            
            # 绘制字符背景
            self.canvas.create_rectangle(
                char_x, char_y, char_x + char_width, char_y + 28,
                fill=bg_color, outline=outline_color, width=1,
                tags="bracket_display"
            )
            
            # 绘制字符
            display_char = char if char != ' ' else '␣'
            self.canvas.create_text(
                char_x + char_width/2, char_y + 14,
                text=display_char, font=("Consolas", 11, "bold"),
                fill=text_color, tags="bracket_display"
            )
        
        # 显示提示信息
        if info:
            info_y = expr_y + total_height - 18
            self.canvas.create_text(
                expr_start_x + 10, info_y,
                text=f"💡 {info}", font=("微软雅黑", 9),
                anchor="w", fill="#8B4513", tags="bracket_display"
            )
        
        self.window.update()
    
    def _bracket_step(self):
        """执行括号匹配的每一步"""
        if self.bracket_index >= len(self.bracket_queue):
            # 检验完成，检查栈是否为空
            self._bracket_final_check()
            return
        
        current_idx = self.bracket_index
        current_char = self.bracket_queue[current_idx]
        self.bracket_index += 1
        
        # 判断字符类型
        if current_char in self.left_brackets:
            # 左括号：入栈
            self._update_bracket_display(current_idx, f"遇到左括号 '{current_char}'，准备入栈")
            self.highlight_pseudo_line(5)
            self.window.after(400, lambda: self._bracket_push_left(current_char, current_idx))
        elif current_char in self.right_brackets:
            # 右括号：检查匹配
            self._update_bracket_display(current_idx, f"遇到右括号 '{current_char}'，检查匹配")
            self.highlight_pseudo_line(7)
            self.window.after(400, lambda: self._bracket_check_match(current_char, current_idx))
        else:
            # 非括号字符：跳过
            self._update_bracket_display(current_idx, f"跳过字符 '{current_char}'")
            self.window.after(200, self._bracket_step)
    
    def _bracket_push_left(self, bracket, current_idx):
        """左括号入栈"""
        stack_before = list(self.model.data)
        stack_after = stack_before + [bracket]
        
        detail_lines = [
            f"━━━ 位置 {current_idx}: 左括号入栈 ━━━",
            f"",
            f"当前字符: '{bracket}' (左括号)",
            f"操作: Push('{bracket}')",
            f"",
            f"栈变化:",
            f"  之前: {self._format_bracket_stack(stack_before)}",
            f"  之后: {self._format_bracket_stack(stack_after)}",
        ]
        self.set_pseudo_code(f"⬇️ 左括号入栈: '{bracket}'", detail_lines)
        self.highlight_pseudo_line(3)
        self.highlight_pseudo_line(6)
        
        # 动画入栈
        self.animate_push_left(bracket, on_finish=lambda: self._bracket_after_push(current_idx), show_pseudo=False)
    
    def _format_bracket_stack(self, stack_data):
        """格式化括号栈显示"""
        if not stack_data:
            return "[空栈]"
        return "[" + " ".join(f"'{x}'" for x in stack_data) + "] ← 栈顶"
    
    def _bracket_after_push(self, current_idx):
        """入栈完成后继续"""
        self._update_bracket_display(current_idx + 1, f"✓ 入栈完成")
        self.complete_pseudo_code()
        self.window.after(300, self._bracket_step)
    
    def _bracket_check_match(self, right_bracket, current_idx):
        """检查右括号是否匹配"""
        # 检查栈是否为空
        if self.model.is_empty():
            # 栈空，缺少左括号
            self.highlight_pseudo_line(8)
            self.highlight_pseudo_line(9)
            self.bracket_error_info = f"位置 {current_idx}: 遇到右括号 '{right_bracket}' 但栈为空，缺少对应的左括号"
            self._bracket_fail(current_idx, "栈空", f"遇到 '{right_bracket}' 但没有对应的左括号")
            return
        
        # 获取栈顶元素
        top_bracket = self.model.data[-1]
        
        # 检查是否匹配
        expected_right = self.bracket_pairs.get(top_bracket)
        
        if expected_right == right_bracket:
            # 匹配成功
            self._bracket_match_success(top_bracket, right_bracket, current_idx)
        else:
            # 匹配失败
            self.highlight_pseudo_line(10)
            self.highlight_pseudo_line(11)
            self.highlight_pseudo_line(12)
            self.bracket_error_info = f"位置 {current_idx}: '{top_bracket}' 与 '{right_bracket}' 不匹配"
            self._bracket_fail(current_idx, "类型不匹配", f"栈顶 '{top_bracket}' 与 '{right_bracket}' 不配对")
    
    def _bracket_match_success(self, left, right, current_idx):
        """括号匹配成功，弹出栈顶"""
        stack_before = list(self.model.data)
        stack_after = stack_before[:-1]
        
        detail_lines = [
            f"━━━ 位置 {current_idx}: 匹配成功 ━━━",
            f"",
            f"当前字符: '{right}' (右括号)",
            f"栈顶元素: '{left}' (左括号)",
            f"",
            f"'{left}' 与 '{right}' 配对成功! ✓",
            f"",
            f"操作: Pop() → '{left}'",
            f"",
            f"栈变化:",
            f"  之前: {self._format_bracket_stack(stack_before)}",
            f"  之后: {self._format_bracket_stack(stack_after)}",
        ]
        self.set_pseudo_code(f"✅ 匹配成功: '{left}' ↔ '{right}'", detail_lines)
        self.highlight_pseudo_line(5)
        self.highlight_pseudo_line(7)
        
        self._update_bracket_display(current_idx, f"✓ '{left}' 与 '{right}' 匹配成功，弹出栈顶")
        
        # 动画出栈
        self._bracket_pop_animated(lambda: self._bracket_after_match(current_idx))
    
    def _bracket_pop_animated(self, callback):
        """执行括号出栈动画"""
        if self.model.is_empty():
            callback()
            return
        
        self.animating = True
        top_idx = self.model.top
        
        if top_idx < 0 or top_idx >= len(self.stack_rectangles):
            self.model.pop()
            self.update_display()
            self.animating = False
            callback()
            return
        
        rect_id = self.stack_rectangles[top_idx]
        text_id = self.stack_labels[top_idx]
        self.canvas.itemconfig(rect_id, fill="#90EE90")  # 绿色表示匹配成功
        
        total_steps = 18
        canvas_width = self.canvas.winfo_width() or 1000
        target_x = canvas_width + self.cell_width
        current_x = self.canvas.coords(rect_id)[0]
        dx = (target_x - current_x) / total_steps
        step_delay = 8
        
        def step(step_i=0):
            if step_i < total_steps:
                self.canvas.move(rect_id, dx, 0)
                self.canvas.move(text_id, dx, 0)
                self.window.after(step_delay, lambda: step(step_i + 1))
            else:
                self.model.pop()
                self.update_display()
                self.animating = False
                self.window.after(150, callback)
        step()
    
    def _bracket_after_match(self, current_idx):
        """匹配成功后继续"""
        self.complete_pseudo_code()
        self._update_bracket_display(current_idx + 1, "继续检验...")
        self.window.after(300, self._bracket_step)
    
    def _bracket_final_check(self):
        """最终检查：栈是否为空"""
        self.highlight_pseudo_line(13)
        
        if self.model.is_empty():
            # 栈空，匹配成功
            self.highlight_pseudo_line(15)
            self._bracket_success()
        else:
            # 栈不空，有未匹配的左括号
            self.highlight_pseudo_line(14)
            remaining = "".join(str(x) for x in self.model.data)
            self.bracket_error_info = f"表达式结束但栈中还有未匹配的左括号: {remaining}"
            self._bracket_fail(-1, "缺少右括号", f"栈中剩余: {self._format_bracket_stack(list(self.model.data))}")
    
    def _bracket_success(self):
        """括号匹配成功"""
        self.canvas.delete("bracket_display")
        
        # 统计括号数量
        left_count = sum(1 for c in self.bracket_expression if c in self.left_brackets)
        right_count = sum(1 for c in self.bracket_expression if c in self.right_brackets)
        
        complete_lines = [
            f"━━━━━ 🎉 检验完成! ━━━━━",
            f"",
            f"表达式: {self.bracket_expression}",
            f"",
            f"结果: ✅ 括号匹配成功!",
            f"",
            f"统计:",
            f"  左括号数量: {left_count}",
            f"  右括号数量: {right_count}",
            f"  全部正确配对 ✓",
        ]
        
        self.set_pseudo_code("🎯 检验结果: 匹配成功!", complete_lines)
        for i in range(len(complete_lines)):
            self.highlight_pseudo_line(i, delay=False)
        self.complete_pseudo_code()
        
        # 显示成功结果
        self._show_bracket_result(True)
        
        messagebox.showinfo("检验完成", 
            f"表达式: {self.bracket_expression}\n\n"
            f"✅ 括号匹配成功!\n\n"
            f"左括号: {left_count} 个\n"
            f"右括号: {right_count} 个")
        
        self._set_buttons_state("normal")
        self.bracket_var.set("")
    
    def _bracket_fail(self, error_idx, error_type, error_detail):
        """括号匹配失败"""
        self._update_bracket_display(self.bracket_index, error_detail, error_idx)
        
        fail_lines = [
            f"━━━━━ ❌ 检验失败! ━━━━━",
            f"",
            f"表达式: {self.bracket_expression}",
            f"",
            f"错误类型: {error_type}",
            f"错误详情: {error_detail}",
            f"",
            f"栈状态: {self._format_bracket_stack(list(self.model.data))}",
        ]
        
        self.set_pseudo_code("❌ 检验结果: 匹配失败!", fail_lines)
        for i in range(len(fail_lines)):
            self.highlight_pseudo_line(i, delay=False)
        self.complete_pseudo_code()
        
        # 显示失败结果
        self._show_bracket_result(False, error_type, error_detail)
        
        messagebox.showerror("检验失败", 
            f"表达式: {self.bracket_expression}\n\n"
            f"❌ 括号匹配失败!\n\n"
            f"错误类型: {error_type}\n"
            f"详情: {error_detail}")
        
        self._set_buttons_state("normal")
        self.bracket_var.set("")
    
    def _show_bracket_result(self, success, error_type=None, error_detail=None):
        """在画布上显示检验结果"""
        self.canvas.delete("bracket_display")
        
        result_x = 240
        result_y = 20
        
        if success:
            bg_color = "#E8F5E9"
            outline_color = "#4CAF50"
            title = "✅ 括号匹配成功"
            title_color = "#2E7D32"
            detail = "所有括号正确配对"
            detail_color = "#1B5E20"
        else:
            bg_color = "#FFEBEE"
            outline_color = "#F44336"
            title = f"❌ {error_type}"
            title_color = "#C62828"
            detail = error_detail or "括号不匹配"
            detail_color = "#B71C1C"
        
        self.canvas.create_rectangle(
            result_x, result_y, result_x + 350, result_y + 90,
            fill=bg_color, outline=outline_color, width=3,
            tags="bracket_result"
        )
        self.canvas.create_text(
            result_x + 175, result_y + 25,
            text=title, font=("微软雅黑", 12, "bold"),
            fill=title_color, tags="bracket_result"
        )
        self.canvas.create_text(
            result_x + 175, result_y + 55,
            text=detail, font=("微软雅黑", 10),
            fill=detail_color, tags="bracket_result", width=320
        )
    
    def _bracket_abort(self):
        """中止括号匹配检验"""
        self.bracket_queue = []
        self.bracket_index = 0
        self.canvas.delete("bracket_display")
        self.canvas.delete("bracket_result")
        self._set_buttons_state("normal")
        self.clear_pseudo_code()

    # ==================== 括号匹配检验功能结束 ====================

    def update_display(self):
        self.canvas.delete("all")
        self.stack_rectangles.clear()
        self.stack_labels.clear()
        
        # 更新容量标签
        if hasattr(self, 'capacity_label'):
            expand_status = "🔄" if self.model.auto_expand else "🔒"
            self.capacity_label.config(text=f"{expand_status} 容量: {self.capacity}")
        
        # ============ 左侧信息面板 ============
        info_x = 15
        info_y = 15
        info_width = 200
        info_height = 180
        
        self.canvas.create_rectangle(
            info_x, info_y, info_x + info_width, info_y + info_height,
            fill="#F0F8FF", outline="#B0C4DE", width=1, tags="info_panel"
        )
        
        # 栈状态信息
        status = '满' if self.model.is_full() else '空' if self.model.is_empty() else '非空'
        expand_text = "🔄" if self.model.auto_expand else "🔒"
        
        self.canvas.create_text(
            info_x + 10, info_y + 12,
            text=f"📊 栈状态: {status}",
            font=self.font_normal_bold, anchor="nw", fill="#333"
        )
        self.canvas.create_text(
            info_x + 10, info_y + 35,
            text=f"大小: {len(self.model)}/{self.capacity}",
            font=self.font_small, anchor="nw", fill="#555"
        )
        self.canvas.create_text(
            info_x + 10, info_y + 55,
            text=f"自动扩容: {expand_text}",
            font=self.font_small, anchor="nw", fill="#555"
        )
        
        # 简化操作说明
        instruction_text = (
            "━━━━━━━━━━━━━━━\n"
            "📌 操作说明:\n"
            "• Push/Pop: 入栈/出栈\n"
            "• 后缀求值: 3 4 + 2 *\n"
            "• 括号匹配: {a+[b*c]}"
        )
        self.canvas.create_text(
            info_x + 10, info_y + 80,
            text=instruction_text,
            font=("Consolas", 9), anchor="nw", fill="#666", width=info_width - 20
        )
        
        # ============ 栈可视化区域 ============
        stack_area_x = info_x + info_width + 30  # 栈区域起始x
        stack_area_y = 250  # 栈区域y位置
        
        frame_width = (self.cell_width + self.spacing) * self.capacity + 20
        frame_height = self.cell_height + 20
        
        # 栈容器背景
        self.canvas.create_rectangle(
            stack_area_x - 10,
            stack_area_y - 10,
            stack_area_x + frame_width,
            stack_area_y + frame_height,
            outline="#BBBBBB", 
            width=2,
            fill="#EEEEEE"
        )
        
        # 栈底/栈顶标签
        self.canvas.create_text(
            stack_area_x - 35,
            stack_area_y + self.cell_height/2,
            text="栈底",
            font=self.font_normal_bold, fill="#666"
        )
        self.canvas.create_text(
            stack_area_x + frame_width + 25,
            stack_area_y + self.cell_height/2,
            text="栈顶",
            font=self.font_normal_bold, fill="#666"
        )
        
        # 绘制栈元素
        for i in range(len(self.model.data)):
            x = stack_area_x + i * (self.cell_width + self.spacing)

            rect = self.canvas.create_rectangle(
                x, stack_area_y,
                x + self.cell_width, stack_area_y + self.cell_height,
                fill=self.stack_fill,
                outline=self.stack_outline,
                width=2
            )
            self.stack_rectangles.append(rect)
            
            label = self.canvas.create_text(
                x + self.cell_width/2,
                stack_area_y + self.cell_height/2,
                text=str(self.model.data[i]),
                font=self.font_normal_bold
            )
            self.stack_labels.append(label)

        # top指针
        if not self.model.is_empty():
            top_idx = self.model.top
            top_x = stack_area_x + top_idx * (self.cell_width + self.spacing)
            
            self.canvas.create_line(
                top_x + self.cell_width/2,
                stack_area_y - 25,
                top_x + self.cell_width/2,
                stack_area_y - 5,
                arrow=tk.LAST,
                width=2,
                fill="#E53935"
            )
            self.canvas.create_text(
                top_x + self.cell_width/2,
                stack_area_y - 40,
                text=f"top={top_idx}",
                font=("Consolas", 11, "bold"),
                fill="#E53935"
            )
        else:
            self.canvas.create_text(
                stack_area_x + self.cell_width/2, 
                stack_area_y - 35,
                text="top=-1 (空栈)",
                font=("Consolas", 11, "bold"),
                fill="#E53935"
            )
        
        # 更新内部坐标供动画使用
        self.start_x = stack_area_x
        self.start_y = stack_area_y

    def _set_buttons_state(self, state):
        all_buttons = [
            self.push_btn, self.pop_btn, self.clear_btn, self.back_btn,
            self.batch_build_btn, self.confirm_btn, self.eval_btn, self.bracket_match_btn,
            getattr(self, 'dfs_btn', None)  # DFS按钮
        ]
        
        all_entries = [] # 存储所有 Entry

        try:
            button_frame = self.push_btn.master
            for child in button_frame.winfo_children():
                if isinstance(child, ttk.Button):
                    if child not in all_buttons:
                        all_buttons.append(child)
                elif isinstance(child, ttk.Entry):
                     all_entries.append(child) # 收集 Entry

        except Exception:
            pass
        
        for btn in all_buttons:
            if btn:
                try:
                    btn.config(state=state)
                except Exception:
                    pass
        
        # 统一处理 Entry
        for entry in all_entries:
             if entry:
                try:
                    entry.config(state="normal" if state == "normal" else "disabled")
                except Exception:
                    pass

        if self.input_frame:
            try:
                for child in self.input_frame.winfo_children():
                    if isinstance(child, (ttk.Button, ttk.Entry)):
                        child.config(state="normal" if state == "normal" else "disabled")
            except Exception:
                pass


    def back_to_main(self):
        if self.animating:
            messagebox.showinfo("提示", "正在动画构建，无法返回")
            return
        stack_api.unregister(self)
        self.window.destroy()

if __name__ == '__main__':
    window = tk.Tk()
    window.title("栈 (Stack) 可视化")
    window.geometry("1350x770")
    window.maxsize(1350, 770)
    window.minsize(1350, 770)
    
    window.configure(bg="#F0F0F0") 

    app = StackVisualizer(window)
    window.mainloop()