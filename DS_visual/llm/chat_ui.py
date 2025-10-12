import tkinter as tk
from tkinter import Toplevel, Frame, Text, ttk, simpledialog, END
import time

USER_BG = "#E6F8EE"         
ASSIST_BG = "#FFFFFF"       
BG_COLOR = "#F3F6F9"        
BG_GRAD_2 = "#EEF9F4"       
INPUT_BG = "#FFFFFF"
ACCENT = "#0F9370"          
ACCENT_DARK = "#0d7b5e"
TEXT_COLOR = "#0F1724"
META_COLOR = "#6B7280"
SYSTEM_BG = "#EEF2F3"
FONT_FAMILY = "Helvetica"

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

        # window
        self.win = Toplevel(parent)
        self.win.title("LLM 聊天窗口")
        
        parent_x  = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width() or 1350
        window_width = 880
        x_pos = parent_x + parent_width + 10
        y_pos = parent_y
     
        self.win.geometry(f"{window_width}x660+{x_pos}+{y_pos}")
        self.win.configure(bg=BG_COLOR)
        self.win.minsize(560, 420)

        # style
        style = ttk.Style(self.win)
        style.theme_use('default')
        style.configure("Accent.TButton", background=ACCENT, foreground="white", font=(FONT_FAMILY, 10, "bold"), padding=6)
        style.map("Accent.TButton", background=[('active', ACCENT_DARK), ('disabled', '#94cdb7')])
        style.configure("Meta.TButton", foreground=TEXT_COLOR, font=(FONT_FAMILY, 9))
        style.configure("TScrollbar", gripcount=0, background="#E6EEF0", troughcolor="#F3F6F9", bordercolor="#F3F6F9")

        # topbar
        topbar = Frame(self.win, bg=BG_COLOR, padx=14, pady=10)
        topbar.pack(fill='x')
        title_frame = Frame(topbar, bg=BG_COLOR)
        title_frame.pack(side='left', anchor='w')
        title = tk.Label(title_frame, text="LLM 聊天窗口", font=(FONT_FAMILY, 15, "bold"), bg=BG_COLOR, fg=TEXT_COLOR)
        title.pack(side='left')
        subtitle = tk.Label(title_frame, text=" — 支持结构化函数调用与可视化触发", font=(FONT_FAMILY, 9), bg=BG_COLOR, fg=META_COLOR)
        subtitle.pack(side='left', padx=(8,0))

        btn_frame = Frame(topbar, bg=BG_COLOR)
        btn_frame.pack(side='right')
        clear_btn = ttk.Button(btn_frame, text="清空", style="Meta.TButton", command=self._handle_clear)
        clear_btn.pack(side='right', padx=(8,0))
        settings_btn = ttk.Button(btn_frame, text="设置", style="Meta.TButton", command=self._handle_settings)
        settings_btn.pack(side='right', padx=(8,0))

        sep = Frame(self.win, height=1, bg="#E6EEF3")
        sep.pack(fill='x')

        # content + canvas
        content = Frame(self.win, bg=BG_COLOR)
        content.pack(fill='both', expand=True, padx=14, pady=(8,10))

        self.canvas = tk.Canvas(content, bg=BG_COLOR, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(content, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side='right', fill='y')
        self.canvas.pack(side='left', fill='both', expand=True)

        self.messages_frame = Frame(self.canvas, bg=BG_COLOR)
        self.canvas.create_window((0,0), window=self.messages_frame, anchor='nw', tags="messages_frame")
        self.messages_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.draw_canvas_background())

        # mousewheel
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

        # input area
        input_frame = Frame(self.win, bg=BG_COLOR, padx=14, pady=12)
        input_frame.pack(fill='x')

        entry_container = Frame(input_frame, bg=INPUT_BG, bd=0, relief='flat', padx=8, pady=8)
        entry_container.pack(side='left', fill='x', expand=True, padx=(0,10))
        self.entry = Text(entry_container, height=4, wrap='word', font=(FONT_FAMILY, 12), bg=INPUT_BG, relief='flat', bd=0)
        self.entry.pack(fill='both', expand=True)
        self.entry.bind("<Return>", self.on_entry_return)
        self.entry.bind("<Shift-Return>", self.on_shift_enter)
        self.entry.bind("<Control-Return>", self.on_entry_return)

        right_controls = Frame(input_frame, bg=BG_COLOR)
        right_controls.pack(side='right')

        self.send_btn = tk.Button(right_controls, text="发送", bg=ACCENT, fg="white", activebackground=ACCENT_DARK,
                                  font=(FONT_FAMILY, 11, "bold"), width=10, command=self._handle_send, bd=0)
        self.send_btn.pack(side='top', pady=(2,8))
        self.quick_btn = ttk.Button(right_controls, text="示例", style="Meta.TButton", command=self.insert_example)
        self.quick_btn.pack(side='top')

        self._streaming = False
        self.draw_canvas_background()
        self.system_message("The best way to predict the future is to create it.")
    def _handle_send(self):
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

    # ---- 绘制相关 ----
    def _hex_to_rgb(self, h: str):
        h = h.lstrip('#')
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

    def _rgb_to_hex(self, rgb):
        return '#{:02x}{:02x}{:02x}'.format(*rgb)

    def _interpolate(self, c1, c2, t: float):
        return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

    def draw_canvas_background(self):
        try:
            w = max(self.canvas.winfo_width(), 2)
            h = max(self.canvas.winfo_height(), 2)
        except Exception:
            return
        self.canvas.delete("bg")
        c1 = self._hex_to_rgb(BG_COLOR)
        c2 = self._hex_to_rgb(BG_GRAD_2)
        steps = 24
        for i in range(steps):
            y0 = int(h * (i / steps))
            y1 = int(h * ((i + 1) / steps))
            t = (i + 0.5) / steps
            color = self._rgb_to_hex(self._interpolate(c1, c2, t))
            self.canvas.create_rectangle(0, y0, w, y1, fill=color, outline="", tags=("bg",))
        stripe_color = "#F1F6F4"
        spacing = 36
        for x in range(-h, w + h, spacing):
            self.canvas.create_line(x, 0, x + h, h, fill=stripe_color, width=1, tags=("bg",))
        watermark_text = "LLM 可视化"
        wm_color = "#F2F7F4"
        self.canvas.create_text(w - 12, h - 12, text=watermark_text, anchor='se', font=(FONT_FAMILY, 9, "italic"),
                                fill=wm_color, tags=("bg",))
        try:
            self.canvas.tag_raise("messages_frame")
        except Exception:
            pass

    def _on_mousewheel(self, event):
        if hasattr(event, 'num') and event.num == 4:
            self.canvas.yview_scroll(-3, "units")
        elif hasattr(event, 'num') and event.num == 5:
            self.canvas.yview_scroll(3, "units")
        else:
            delta = -1*(event.delta//120) if event.delta else 0
            self.canvas.yview_scroll(delta, "units")

    # ---- 消息与气泡 ----
    def add_message_bubble(self, who: str, text: str, align: str = "right"):
        container = Frame(self.messages_frame, bg=BG_COLOR)
        container.pack(fill='x', pady=8, padx=12)
        is_user = (who == "你")
        side = 'e' if is_user else 'w'
        bubble_frame = Frame(container, bg=BG_COLOR)
        bubble_frame.pack(anchor=side, padx=(80,12) if is_user else (12,80))
        avatar = tk.Canvas(bubble_frame, width=36, height=36, bg=BG_COLOR, highlightthickness=0)
        avatar.pack(side='right' if is_user else 'left', padx=(6,10) if is_user else (0,10))
        color = "#10A37F" if is_user else "#6B7280"
        avatar.create_oval(4,4,32,32, fill=color, outline="")
        meta = tk.Label(bubble_frame, text=f"{who}  {time.strftime('%H:%M:%S')}", bg=BG_COLOR, fg=META_COLOR, font=(FONT_FAMILY, 8))
        meta.pack(anchor='e' if is_user else 'w')
        bubble_bg = USER_BG if is_user else ASSIST_BG
        bubble = Frame(bubble_frame, bg=bubble_bg, bd=0, relief='flat', padx=10, pady=8)
        bubble.pack(anchor='e' if is_user else 'w')
        var = tk.StringVar(value=text)
        lbl = tk.Label(bubble, textvariable=var, justify='left', anchor='w',
                       font=(FONT_FAMILY, 12), bg=bubble_bg, fg=TEXT_COLOR, wraplength=560)
        lbl.pack()
        return var, lbl, bubble

    def system_message(self, text: str):
        panel = Frame(self.messages_frame, bg=SYSTEM_BG, bd=0, relief='flat', padx=12, pady=8)
        panel.pack(pady=(10,10), padx=120, fill='x')
        lbl = tk.Label(panel, text=text, bg=SYSTEM_BG, fg=META_COLOR, font=(FONT_FAMILY, 10), wraplength=520, justify='center')
        lbl.pack()

    def clear_messages(self):
        for child in self.messages_frame.winfo_children():
            child.destroy()
        self.system_message("对话已清空。")

    def insert_example(self):
        example = "将1压入栈"
        self.entry.insert("end", example)
        self.entry.see("end")

    def finish_stream(self):
        self._streaming = False
        self.send_btn.config(state='normal', bg=ACCENT)
        spacer = Frame(self.messages_frame, height=6, bg=BG_COLOR)
        spacer.pack()

    def append_chunk(self, var, chunk: str):
        current = var.get()
        var.set(current + chunk)
        self.canvas.yview_moveto(1.0)
