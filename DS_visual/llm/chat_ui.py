import tkinter as tk
from tkinter import Toplevel, Frame, Text, ttk, simpledialog, END, Canvas
import time

# 现代化高级配色方案
USER_BG = "#667EEA"         # 渐变紫蓝色用户气泡
USER_BG_LIGHT = "#764BA2"   # 用户气泡渐变色
ASSIST_BG = "#FFFFFF"       # 白色助手气泡
BG_COLOR = "#F7F8FC"        # 浅灰蓝背景
BG_GRAD_START = "#E8EAF6"   # 渐变起始色
BG_GRAD_END = "#F3E5F5"     # 渐变结束色
INPUT_BG = "#FFFFFF"
ACCENT = "#667EEA"          # 主题紫蓝色
ACCENT_DARK = "#5568D3"
ACCENT_HOVER = "#7C8FEF"
TEXT_COLOR = "#2D3748"
META_COLOR = "#A0AEC0"
SYSTEM_BG = "#EDF2F7"
BORDER_COLOR = "#E2E8F0"
SHADOW_COLOR = "#CBD5E0"
FONT_FAMILY = "Segoe UI"

class ChatUI:
    def __init__(self, parent,
                 on_send, on_clear, on_settings,
                 on_entry_return, on_shift_enter):
        self.parent = parent
        self.on_send = on_send
        self.on_clear = on_clear
        self.on_settings = on_settings
        self.on_entry_return = on_entry_return
        self.on_shift_enter = on_shift_enter

        # 初始化状态变量
        self._streaming = False
        self._entry_placeholder = True
        self._send_btn_hovered = False
        self._send_btn_disabled = False

        # window
        self.win = Toplevel(parent)
        self.win.title("LLM 智能对话")
        
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width() or 1350
        window_width = 980
        x_pos = parent_x + parent_width + 10
        y_pos = parent_y
     
        self.win.geometry(f"{window_width}x760+{x_pos}+{y_pos}")
        self.win.configure(bg=BG_COLOR)
        self.win.minsize(700, 550)

        # style
        style = ttk.Style(self.win)
        style.theme_use('clam')
        
        style.configure("TScrollbar", 
                       gripcount=0, 
                       background="#CBD5E0", 
                       troughcolor=BG_COLOR, 
                       bordercolor=BG_COLOR,
                       arrowcolor="white",
                       width=8)
        style.map("TScrollbar",
                 background=[('active', '#A0AEC0')])

        # 顶部栏 - 毛玻璃效果
        topbar_container = Frame(self.win, bg=BG_COLOR)
        topbar_container.pack(fill='x')
        
        topbar = Frame(topbar_container, bg="#FFFFFF", padx=24, pady=20)
        topbar.pack(fill='x', padx=12, pady=(12, 0))
        
        # 添加底部阴影线
        shadow_line = Canvas(topbar_container, height=3, bg=BG_COLOR, highlightthickness=0)
        shadow_line.pack(fill='x', padx=12)
        shadow_line.create_rectangle(0, 0, 2000, 1, fill="#E2E8F0", outline="")
        shadow_line.create_rectangle(0, 1, 2000, 2, fill="#EDF2F7", outline="")
        shadow_line.create_rectangle(0, 2, 2000, 3, fill="#F7FAFC", outline="")
        
        title_frame = Frame(topbar, bg="#FFFFFF")
        title_frame.pack(side='left', anchor='w')
        
        # 精美的渐变图标
        icon_canvas = Canvas(title_frame, width=42, height=42, bg="#FFFFFF", highlightthickness=0)
        icon_canvas.pack(side='left', padx=(0, 14))
        
        # 创建渐变圆形图标
        for i in range(5):
            offset = i * 0.8
            size = 42 - i * 2
            color_gradient = self._interpolate_color("#667EEA", "#764BA2", i/5)
            icon_canvas.create_oval(
                4 + offset, 4 + offset, 
                4 + size, 4 + size, 
                fill=color_gradient, outline="", width=0
            )
        icon_canvas.create_text(23, 23, text="✨", font=(FONT_FAMILY, 18))
        
        title_content = Frame(title_frame, bg="#FFFFFF")
        title_content.pack(side='left')
        
        title = tk.Label(title_content, text="LLM 智能助手", 
                        font=(FONT_FAMILY, 18, "bold"), 
                        bg="#FFFFFF", fg=TEXT_COLOR)
        title.pack(anchor='w')
        
        subtitle = tk.Label(title_content, text="AI驱动 · 实时响应 · 智能交互", 
                           font=(FONT_FAMILY, 9), 
                           bg="#FFFFFF", fg=META_COLOR)
        subtitle.pack(anchor='w')

        btn_frame = Frame(topbar, bg="#FFFFFF")
        btn_frame.pack(side='right')
        
        # 现代化圆角按钮
        self._create_modern_button(
            btn_frame, "⚙️ 设置", 
            self._handle_settings
        ).pack(side='right', padx=(10, 0))
        
        self._create_modern_button(
            btn_frame, "🗑️ 清空", 
            self._handle_clear
        ).pack(side='right', padx=(10, 0))

        # 内容区域
        content = Frame(self.win, bg=BG_COLOR)
        content.pack(fill='both', expand=True, padx=12, pady=(0, 12))

        # 消息容器 - 带圆角和阴影
        messages_container = Frame(content, bg="#FFFFFF", bd=0)
        messages_container.pack(fill='both', expand=True)
        
        self.canvas = tk.Canvas(messages_container, bg="#FAFBFC", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(messages_container, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side='right', fill='y', padx=(0, 2), pady=2)
        self.canvas.pack(side='left', fill='both', expand=True, padx=2, pady=2)

        self.messages_frame = Frame(self.canvas, bg="#FAFBFC")
        self.canvas.create_window((0, 0), window=self.messages_frame, anchor='nw', tags="messages_frame")
        self.messages_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # mousewheel
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

        # 输入区域 - 现代化设计
        input_wrapper = Frame(self.win, bg=BG_COLOR)
        input_wrapper.pack(fill='x', padx=12, pady=(0, 12))
        
        input_card = Frame(input_wrapper, bg="#FFFFFF", bd=0)
        input_card.pack(fill='x', padx=0, pady=0)
        
        input_inner = Frame(input_card, bg="#FFFFFF", padx=20, pady=18)
        input_inner.pack(fill='x')
        
        # 输入框容器 - 带阴影边框
        entry_wrapper = Frame(input_inner, bg="#E2E8F0", bd=0)
        entry_wrapper.pack(side='left', fill='x', expand=True, padx=(0, 16))
        
        entry_inner = Frame(entry_wrapper, bg=INPUT_BG, bd=0)
        entry_inner.pack(fill='both', expand=True, padx=2, pady=2)
        
        # 文本输入框
        self.entry = Text(entry_inner, height=3, wrap='word', 
                         font=(FONT_FAMILY, 11), 
                         bg=INPUT_BG, relief='flat', bd=0,
                         padx=16, pady=12,
                         insertbackground=ACCENT)
        self.entry.pack(fill='both', expand=True)
        self.entry.bind("<Return>", self.on_entry_return)
        self.entry.bind("<Shift-Return>", self.on_shift_enter)
        self.entry.bind("<Control-Return>", self.on_entry_return)
        
        # 占位符
        self.entry.insert("1.0", "输入消息... (Shift+Enter 换行)")
        self.entry.config(fg=META_COLOR)
        self.entry.bind("<FocusIn>", self._on_entry_focus_in)
        self.entry.bind("<FocusOut>", self._on_entry_focus_out)

        right_controls = Frame(input_inner, bg="#FFFFFF")
        right_controls.pack(side='right')

        # 渐变发送按钮
        self.send_btn_canvas = Canvas(right_controls, width=130, height=48, 
                                      bg="#FFFFFF", highlightthickness=0, cursor="hand2")
        self.send_btn_canvas.pack(side='top', pady=(0, 10))
        self._draw_gradient_button(self.send_btn_canvas, "发送 ✈️", "normal")
        self.send_btn_canvas.bind("<Button-1>", lambda e: self._handle_send())
        self.send_btn_canvas.bind("<Enter>", lambda e: self._on_send_hover(True))
        self.send_btn_canvas.bind("<Leave>", lambda e: self._on_send_hover(False))
        
        # 为兼容性创建 send_btn 属性
        self.send_btn = self.send_btn_canvas
        
        self.quick_btn = self._create_secondary_button(
            right_controls, "💡 示例", self.insert_example
        )
        self.quick_btn.pack(side='top')

        self.system_message("👋 你好!我是 LLM 助手,很高兴为你服务!")

    def _interpolate_color(self, color1, color2, ratio):
        """颜色插值"""
        c1 = tuple(int(color1[i:i+2], 16) for i in (1, 3, 5))
        c2 = tuple(int(color2[i:i+2], 16) for i in (1, 3, 5))
        c3 = tuple(int(c1[i] + (c2[i] - c1[i]) * ratio) for i in range(3))
        return f"#{c3[0]:02x}{c3[1]:02x}{c3[2]:02x}"

    def _create_modern_button(self, parent, text, command):
        """创建现代化按钮"""
        btn = tk.Button(parent, text=text, 
                       font=(FONT_FAMILY, 9),
                       bg="#F7FAFC", fg=TEXT_COLOR,
                       relief="flat", bd=0,
                       padx=18, pady=10,
                       cursor="hand2",
                       activebackground="#EDF2F7",
                       command=command)
        btn.bind("<Enter>", lambda e: btn.config(bg="#EDF2F7"))
        btn.bind("<Leave>", lambda e: btn.config(bg="#F7FAFC"))
        return btn

    def _create_secondary_button(self, parent, text, command):
        """创建次要按钮"""
        btn = tk.Button(parent, text=text, 
                       font=(FONT_FAMILY, 9),
                       bg="#F7FAFC", fg=TEXT_COLOR,
                       relief="flat", bd=0,
                       padx=18, pady=10,
                       cursor="hand2",
                       activebackground="#EDF2F7",
                       command=command)
        btn.bind("<Enter>", lambda e: btn.config(bg="#EDF2F7"))
        btn.bind("<Leave>", lambda e: btn.config(bg="#F7FAFC"))
        return btn

    def _draw_gradient_button(self, canvas, text, state="normal"):
        """绘制渐变按钮"""
        canvas.delete("all")
        width = 130
        height = 48
        
        if state == "disabled" or self._send_btn_disabled:
            # 禁用状态
            for i in range(height):
                ratio = i / height
                color = self._interpolate_color("#CBD5E0", "#A0AEC0", ratio)
                canvas.create_line(0, i, width, i, fill=color, width=1)
            canvas.config(cursor="arrow")
        elif self._send_btn_hovered and state == "normal":
            # 悬停状态
            for i in range(height):
                ratio = i / height
                color = self._interpolate_color("#7C8FEF", "#8B5CF6", ratio)
                canvas.create_line(0, i, width, i, fill=color, width=1)
            canvas.config(cursor="hand2")
        else:
            # 正常状态
            for i in range(height):
                ratio = i / height
                color = self._interpolate_color("#667EEA", "#764BA2", ratio)
                canvas.create_line(0, i, width, i, fill=color, width=1)
            canvas.config(cursor="hand2")
        
        # 添加阴影效果
        canvas.create_rectangle(2, height-2, width-2, height, fill="#D0D0D0", outline="")
        
        # 文字
        text_color = "#E0E0E0" if (state == "disabled" or self._send_btn_disabled) else "white"
        canvas.create_text(width//2, height//2, text=text, 
                          fill=text_color, font=(FONT_FAMILY, 11, "bold"))

    def _on_send_hover(self, entering):
        """发送按钮悬停效果"""
        if not self._send_btn_disabled:
            self._send_btn_hovered = entering
            self._draw_gradient_button(self.send_btn_canvas, "发送 ✈️", "normal")

    def _on_entry_focus_in(self, event):
        if self._entry_placeholder:
            self.entry.delete("1.0", END)
            self.entry.config(fg=TEXT_COLOR)
            self._entry_placeholder = False

    def _on_entry_focus_out(self, event):
        if not self.entry.get("1.0", END).strip():
            self.entry.insert("1.0", "输入消息... (Shift+Enter 换行)")
            self.entry.config(fg=META_COLOR)
            self._entry_placeholder = True

    def _handle_send(self):
        if self._streaming or self._send_btn_disabled:
            return
        if callable(self.on_send):
            self.on_send()

    def _handle_clear(self):
        if callable(self.on_clear):
            self.on_clear()

    def _handle_settings(self):
        if callable(self.on_settings):
            self.on_settings()

    def on_entry_return(self, event):
        if callable(self.on_entry_return):
            return self.on_entry_return(event)

    def on_shift_enter(self, event):
        if callable(self.on_shift_enter):
            return self.on_shift_enter(event)

    def _on_mousewheel(self, event):
        if hasattr(event, 'num') and event.num == 4:
            self.canvas.yview_scroll(-3, "units")
        elif hasattr(event, 'num') and event.num == 5:
            self.canvas.yview_scroll(3, "units")
        else:
            delta = -1 * (event.delta // 120) if event.delta else 0
            self.canvas.yview_scroll(delta, "units")

    def add_message_bubble(self, who: str, text: str, align: str = "right"):
        container = Frame(self.messages_frame, bg="#FAFBFC")
        container.pack(fill='x', pady=12, padx=24)
        
        is_user = (who == "你")
        side = 'e' if is_user else 'w'
        
        bubble_frame = Frame(container, bg="#FAFBFC")
        bubble_frame.pack(anchor=side, padx=(120, 24) if is_user else (24, 120))
        
        # 精美头像
        avatar_container = Frame(bubble_frame, bg="#FAFBFC")
        avatar_container.pack(side='right' if is_user else 'left', 
                             padx=(12, 0) if is_user else (0, 12))
        
        avatar = tk.Canvas(avatar_container, width=44, height=44, 
                          bg="#FAFBFC", highlightthickness=0)
        avatar.pack()
        
        # 渐变头像
        if is_user:
            for i in range(3):
                offset = i * 1
                size = 44 - i * 2
                color = self._interpolate_color("#667EEA", "#764BA2", i/3)
                avatar.create_oval(2 + offset, 2 + offset, 2 + size, 2 + size, 
                                  fill=color, outline="")
            avatar.create_text(23, 23, text="👤", font=(FONT_FAMILY, 18))
        else:
            for i in range(3):
                offset = i * 1
                size = 44 - i * 2
                color = self._interpolate_color("#48BB78", "#38A169", i/3)
                avatar.create_oval(2 + offset, 2 + offset, 2 + size, 2 + size, 
                                  fill=color, outline="")
            avatar.create_text(23, 23, text="🤖", font=(FONT_FAMILY, 18))
        
        content_frame = Frame(bubble_frame, bg="#FAFBFC")
        content_frame.pack(side='right' if is_user else 'left')
        
        # 元信息
        meta = tk.Label(content_frame, text=f"{who}  {time.strftime('%H:%M')}", 
                       bg="#FAFBFC", fg=META_COLOR, font=(FONT_FAMILY, 9))
        meta.pack(anchor='e' if is_user else 'w', pady=(0, 6))
        
        # 气泡容器 - 多层阴影效果
        shadow_outer = Frame(content_frame, bg="#E8E8E8", bd=0)
        shadow_outer.pack(anchor='e' if is_user else 'w')
        
        shadow_mid = Frame(shadow_outer, bg="#F0F0F0", bd=0)
        shadow_mid.pack(padx=(0 if is_user else 1, 1 if is_user else 0), 
                       pady=(0, 1))
        
        if is_user:
            # 用户消息 - 渐变气泡
            bubble_canvas = Canvas(shadow_mid, width=600, height=100, 
                                  bg="#FAFBFC", highlightthickness=0)
            bubble_canvas.pack()
            
            # 计算实际高度
            temp_label = tk.Label(bubble_canvas, text=text, font=(FONT_FAMILY, 11), 
                                 wraplength=560)
            temp_label.update_idletasks()
            actual_height = temp_label.winfo_reqheight() + 28
            bubble_canvas.configure(height=actual_height)
            temp_label.destroy()
            
            # 绘制渐变背景
            for i in range(actual_height):
                ratio = i / actual_height
                color = self._interpolate_color("#667EEA", "#764BA2", ratio * 0.3)
                bubble_canvas.create_line(0, i, 600, i, fill=color, width=1)
            
            # 文字
            var = tk.StringVar(value=text)
            lbl = tk.Label(bubble_canvas, textvariable=var, justify='left', anchor='w',
                          font=(FONT_FAMILY, 11), bg=USER_BG, fg="white", 
                          wraplength=560)
            bubble_canvas.create_window(18, 14, window=lbl, anchor='nw')
            
            bubble = bubble_canvas
        else:
            # 助手消息 - 白色卡片
            bubble = Frame(shadow_mid, bg=ASSIST_BG, bd=0, relief='flat', 
                          padx=18, pady=14)
            bubble.pack()
            
            var = tk.StringVar(value=text)
            lbl = tk.Label(bubble, textvariable=var, justify='left', anchor='w',
                          font=(FONT_FAMILY, 11), bg=ASSIST_BG, fg=TEXT_COLOR, 
                          wraplength=560)
            lbl.pack()
        
        return var, lbl, bubble

    def system_message(self, text: str):
        container = Frame(self.messages_frame, bg="#FAFBFC")
        container.pack(pady=18, padx=180, fill='x')
        
        panel = Frame(container, bg="#EDF2F7", bd=0, relief='flat', padx=24, pady=16)
        panel.pack(fill='x')
        
        # 顶部装饰条
        accent_bar = Canvas(panel, height=4, bg="#EDF2F7", highlightthickness=0)
        accent_bar.pack(fill='x', pady=(0, 12))
        for i in range(4):
            color = self._interpolate_color("#667EEA", "#764BA2", i/4)
            accent_bar.create_rectangle(0, i, 1000, i+1, fill=color, outline="")
        
        lbl = tk.Label(panel, text=text, bg="#EDF2F7", fg="#4A5568", 
                      font=(FONT_FAMILY, 10), wraplength=500, justify='center')
        lbl.pack()

    def clear_messages(self):
        for child in self.messages_frame.winfo_children():
            child.destroy()
        self.system_message("✨ 对话已清空,让我们重新开始吧!")

    def insert_example(self):
        if self._entry_placeholder:
            self.entry.delete("1.0", END)
            self.entry.config(fg=TEXT_COLOR)
            self._entry_placeholder = False
        example = "将1压入栈"
        self.entry.insert("end", example)
        self.entry.see("end")

    def finish_stream(self):
        self._streaming = False
        self._send_btn_disabled = False
        self._draw_gradient_button(self.send_btn_canvas, "发送 ✈️", "normal")
        spacer = Frame(self.messages_frame, height=12, bg="#FAFBFC")
        spacer.pack()

    def append_chunk(self, var, chunk: str):
        current = var.get()
        var.set(current + chunk)
        self.canvas.yview_moveto(1.0)