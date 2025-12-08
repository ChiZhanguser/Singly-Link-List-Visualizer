"""
单链表可视化 - 现代化UI工具模块
采用深色霓虹主题，圆角按钮，动态渐变效果
"""
from tkinter import Label, Button, Frame, Scale, HORIZONTAL, StringVar, Entry, Toplevel

# ============== 颜色主题定义 ==============
THEME = {
    # 主色调
    "bg_dark": "#0D1117",          # GitHub暗色背景
    "bg_card": "#161B22",          # 卡片背景
    "bg_input": "#21262D",         # 输入框背景
    
    # 霓虹强调色
    "neon_cyan": "#00FFE5",        # 青色霓虹
    "neon_pink": "#FF2E97",        # 粉色霓虹
    "neon_purple": "#A855F7",      # 紫色霓虹
    "neon_blue": "#3B82F6",        # 蓝色霓虹
    "neon_green": "#10B981",       # 绿色霓虹
    "neon_orange": "#F97316",      # 橙色霓虹
    "neon_yellow": "#FBBF24",      # 黄色霓虹
    "neon_red": "#EF4444",         # 红色霓虹
    
    # 文字颜色
    "text_primary": "#E6EDF3",     # 主文字
    "text_secondary": "#8B949E",   # 次要文字
    "text_accent": "#58A6FF",      # 强调文字
    
    # 边框颜色
    "border": "#30363D",
    "border_active": "#58A6FF",
}


def draw_gradient(canvas, width, height, start_color="#0D1117", end_color="#1A1F36", steps=100):
    """绘制优雅的垂直渐变背景"""
    def hex_to_rgb(h): 
        h = h.lstrip('#')
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
    
    def rgb_to_hex(r, g, b): 
        return f'#{r:02x}{g:02x}{b:02x}'
    
    (r1, g1, b1), (r2, g2, b2) = hex_to_rgb(start_color), hex_to_rgb(end_color)
    
    for i in range(steps):
        t = i / max(steps - 1, 1)
        # 使用缓动函数使渐变更自然
        t = t * t * (3 - 2 * t)  # smoothstep
        r = int(r1 + (r2 - r1) * t)
        g = int(g1 + (g2 - g1) * t)
        b = int(b1 + (b2 - b1) * t)
        color = rgb_to_hex(r, g, b)
        y0 = int(i * (height / steps))
        y1 = int((i + 1) * (height / steps))
        canvas.create_rectangle(0, y0, width, y1, outline="", fill=color)
    
    # 添加装饰性网格线（可选）
    grid_color = "#1C2333"
    for x in range(0, width, 50):
        canvas.create_line(x, 0, x, height, fill=grid_color, width=1, dash=(2, 8))
    for y in range(0, height, 50):
        canvas.create_line(0, y, width, y, fill=grid_color, width=1, dash=(2, 8))


def create_modern_button(parent, text, command, bg_color, fg_color="#FFFFFF", 
                         width=None, font_size=11, emoji=None, hover_color=None):
    """创建现代化霓虹风格按钮"""
    display_text = f"{emoji} {text}" if emoji else text
    
    btn = Button(
        parent,
        text=display_text,
        command=command,
        bg=bg_color,
        fg=fg_color,
        font=("Segoe UI", font_size, "bold"),
        relief="flat",
        bd=0,
        padx=12,
        pady=6,
        cursor="hand2",
        activebackground=hover_color or _lighten_color(bg_color),
        activeforeground=fg_color,
    )
    
    if width:
        btn.config(width=width)
    
    # 添加悬停效果
    original_bg = bg_color
    hover_bg = hover_color or _lighten_color(bg_color)
    
    def on_enter(e):
        btn.config(bg=hover_bg)
    
    def on_leave(e):
        btn.config(bg=original_bg)
    
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    
    return btn


def _lighten_color(hex_color, factor=0.2):
    """使颜色变亮"""
    hex_color = hex_color.lstrip('#')
    r, g, b = [int(hex_color[i:i+2], 16) for i in (0, 2, 4)]
    r = min(255, int(r + (255 - r) * factor))
    g = min(255, int(g + (255 - g) * factor))
    b = min(255, int(b + (255 - b) * factor))
    return f'#{r:02x}{g:02x}{b:02x}'


def _darken_color(hex_color, factor=0.2):
    """使颜色变暗"""
    hex_color = hex_color.lstrip('#')
    r, g, b = [int(hex_color[i:i+2], 16) for i in (0, 2, 4)]
    r = max(0, int(r * (1 - factor)))
    g = max(0, int(g * (1 - factor)))
    b = max(0, int(b * (1 - factor)))
    return f'#{r:02x}{g:02x}{b:02x}'


def heading_with_label_subheading(vis):
    """创建现代化标题和信息栏"""
    
    # 主标题 - 放在画布上方居中位置
    title_frame = Frame(vis.canvas_make, bg=THEME["bg_dark"], bd=0)
    title_frame.place(x=20, y=8)
    
    # 装饰性左边框
    left_accent = Frame(title_frame, bg=THEME["neon_cyan"], width=4, height=35)
    left_accent.pack(side="left", padx=(0, 10))
    
    vis.head_name = Label(
        title_frame,
        text="⛓️ 单链表可视化",
        font=("Microsoft YaHei UI", 20, "bold"),
        bg=THEME["bg_dark"],
        fg=THEME["neon_cyan"]
    )
    vis.head_name.pack(side="left")
    
    # 副标题装饰
    subtitle = Label(
        title_frame,
        text="LINKED LIST",
        font=("Consolas", 9),
        bg=THEME["bg_dark"],
        fg=THEME["text_secondary"]
    )
    subtitle.pack(side="left", padx=(12, 0))
    
    # 信息提示栏 - 使用卡片式设计，放在第三行
    info_frame = Frame(vis.window, bg=THEME["bg_card"], bd=0)
    info_frame.place(x=10, y=610, width=1190, height=38)
    
    # 左侧图标
    info_icon = Label(
        info_frame,
        text="💡",
        font=("Segoe UI Emoji", 12),
        bg=THEME["bg_card"],
        fg=THEME["neon_yellow"]
    )
    info_icon.pack(side="left", padx=(10, 5), pady=6)
    
    vis.information = Label(
        info_frame,
        text="start 指向首节点 | temp 指针用于遍历至目标位置 | 支持DSL命令操作",
        font=("Microsoft YaHei UI", 10),
        bg=THEME["bg_card"],
        fg=THEME["text_primary"],
        anchor="w"
    )
    vis.information.pack(side="left", fill="x", expand=True, pady=6)


def make_start_with_other(vis):
    """创建现代化的start指针和相关标签"""
    
    # start指针 - 使用圆角矩形效果
    vis.start_pointer = vis.canvas_make.create_rectangle(
        vis.start_left, vis.start_up,
        vis.start_left + 35, vis.start_up + 35,
        fill=THEME["neon_blue"],
        outline=THEME["neon_cyan"],
        width=2
    )
    
    # 添加发光效果边框
    vis.canvas_make.create_rectangle(
        vis.start_left - 2, vis.start_up - 2,
        vis.start_left + 37, vis.start_up + 37,
        outline=_lighten_color(THEME["neon_blue"], 0.3),
        width=1
    )
    
    vis.start_label = Label(
        vis.canvas_make,
        text="START",
        font=("Consolas", 12, "bold"),
        bg=THEME["bg_dark"],
        fg=THEME["neon_green"]
    )
    vis.start_label.place(x=35, y=418)
    
    # 指向线
    vis.pointing_line_start = vis.canvas_make.create_line(
        67, 330, 67, 395,
        width=2,
        fill=THEME["neon_green"],
        arrow="first"
    )
    
    # NULL标签 - 现代化样式
    vis.start_initial_point_null = Label(
        vis.canvas_make,
        text="NULL",
        font=("Consolas", 14, "bold"),
        bg=THEME["bg_card"],
        fg=THEME["neon_red"],
        padx=8,
        pady=2
    )
    vis.start_initial_point_null.place(x=35, y=300)
    
    # temp和temp1标签
    vis.temp_label = Label(
        vis.canvas_make,
        text="temp",
        font=("Consolas", 12, "bold"),
        bg=THEME["bg_dark"],
        fg=THEME["neon_orange"]
    )
    
    vis.temp1_label = Label(
        vis.canvas_make,
        text="temp1",
        font=("Consolas", 12, "bold"),
        bg=THEME["bg_dark"],
        fg=THEME["neon_pink"]
    )


def make_btn(vis):
    """创建现代化操作按钮组"""
    
    # 操作按钮组容器 - 第一行
    btn_frame = Frame(vis.window, bg=THEME["bg_card"], bd=0)
    btn_frame.place(x=10, y=510, width=1080, height=50)
    
    # 按钮配置 - [文字, 命令, 背景色, 图标, 属性名]
    buttons_config = [
        ("头部插入", lambda: vis.make_node_with_label(1), THEME["neon_green"], "➕", "insert_at_beg"),
        ("尾部插入", lambda: vis.make_node_with_label(0), THEME["neon_blue"], "➕", "insert_at_last"),
        ("头部删除", vis.delete_first_node, THEME["neon_red"], "🗑️", "delete_at_first"),
        ("尾部删除", lambda: vis.delete_last_node(0), THEME["neon_orange"], "🗑️", "delete_at_last"),
        ("位置插入", vis.set_of_input_method, THEME["neon_purple"], "📍", "insert_after_node"),
        ("指定删除", vis.delete_single_node_infrastructure, THEME["neon_pink"], "❌", "delete_particular_node"),
        ("保存", vis.save_structure, "#2D7D46", "💾", "save_btn"),
        ("加载", vis.load_structure, "#2563EB", "📂", "load_btn"),
    ]
    
    x_offset = 10
    for text, cmd, bg, emoji, attr_name in buttons_config:
        btn = create_modern_button(
            btn_frame, text, cmd, bg, 
            font_size=10, emoji=emoji
        )
        btn.place(x=x_offset, y=8)
        setattr(vis, attr_name, btn)
        x_offset += btn.winfo_reqwidth() + 12
    
    # 返回主界面按钮（右下角独立放置）
    vis.back_to_main_btn = create_modern_button(
        vis.window,
        "返回主界面",
        vis.back_to_main,
        THEME["neon_pink"],
        font_size=11,
        emoji="🏠"
    )
    vis.back_to_main_btn.place(x=1220, y=565)


def make_batch_create_ui(vis):
    """创建现代化批量创建和DSL输入区域"""
    
    # 批量创建区域 - 第二行左侧
    batch_frame = Frame(vis.window, bg=THEME["bg_card"], bd=0)
    batch_frame.place(x=10, y=565, width=430, height=40)
    
    Label(
        batch_frame,
        text="📦 批量创建",
        font=("Microsoft YaHei UI", 10, "bold"),
        bg=THEME["bg_card"],
        fg=THEME["neon_cyan"]
    ).place(x=10, y=9)
    
    # 输入框 - 现代化样式
    batch_entry = Entry(
        batch_frame,
        font=("Consolas", 11),
        bg=THEME["bg_input"],
        fg=THEME["text_primary"],
        insertbackground=THEME["neon_cyan"],
        relief="flat",
        bd=0,
        textvariable=vis.batch_entry_var,
        width=18
    )
    batch_entry.place(x=105, y=8, height=25)
    
    # 创建按钮
    create_btn = create_modern_button(
        batch_frame,
        "创建",
        vis.create_list_from_string,
        THEME["neon_green"],
        font_size=9
    )
    create_btn.place(x=320, y=5)
    
    # DSL命令区域 - 第二行右侧
    dsl_frame = Frame(vis.window, bg=THEME["bg_card"], bd=0)
    dsl_frame.place(x=450, y=565, width=400, height=40)
    
    Label(
        dsl_frame,
        text="⚡ DSL命令",
        font=("Microsoft YaHei UI", 10, "bold"),
        bg=THEME["bg_card"],
        fg=THEME["neon_purple"]
    ).place(x=10, y=9)
    
    dsl_entry = Entry(
        dsl_frame,
        font=("Consolas", 11),
        bg=THEME["bg_input"],
        fg=THEME["text_primary"],
        insertbackground=THEME["neon_purple"],
        relief="flat",
        bd=0,
        textvariable=vis.dsl_var,
        width=22
    )
    dsl_entry.place(x=100, y=8, height=25)
    dsl_entry.bind("<Return>", lambda e: vis.process_dsl())
    
    # 执行按钮
    exec_btn = create_modern_button(
        dsl_frame,
        "执行",
        vis.process_dsl,
        THEME["neon_purple"],
        font_size=9
    )
    exec_btn.place(x=335, y=5)
    
    # 帮助按钮
    def show_dsl_help():
        from tkinter import messagebox
        help_text = """
╔══════════════════════════════════╗
║        📖 DSL 命令帮助           ║
╠══════════════════════════════════╣
║                                  ║
║  📥 插入操作:                    ║
║    insert VALUE [at POS]         ║
║    append VALUE  (尾部插入)      ║
║    prepend VALUE (头部插入)      ║
║                                  ║
║  📤 删除操作:                    ║
║    delete first/last/POS         ║
║                                  ║
║  ✨ 增强操作:                    ║
║    search VALUE  搜索            ║
║    traverse      遍历            ║
║    reverse       反转            ║
║    length        计算长度        ║
║    memory        显示内存地址    ║
║                                  ║
║  🔧 其他:                        ║
║    clear         清空链表        ║
║    create V1,V2,V3  批量创建     ║
║                                  ║
╚══════════════════════════════════╝
        """
        messagebox.showinfo("DSL 命令帮助", help_text)
    
    help_btn = create_modern_button(
        dsl_frame,
        "?",
        show_dsl_help,
        THEME["text_secondary"],
        font_size=10,
        width=2
    )
    help_btn.place(x=385, y=5)


def make_enhanced_controls(vis):
    """创建现代化增强功能控制面板"""
    
    # ========== 状态面板（画布右上角）==========
    status_frame = Frame(vis.canvas_make, bg=THEME["bg_card"], bd=0)
    status_frame.place(x=880, y=10, width=200, height=75)
    
    # 状态面板装饰边框
    vis.canvas_make.create_rectangle(
        878, 8, 1082, 87,
        outline=THEME["neon_cyan"],
        width=1,
        dash=(4, 4)
    )
    
    # 标题
    Label(
        status_frame,
        text="📊 链表状态",
        font=("Microsoft YaHei UI", 11, "bold"),
        bg=THEME["bg_card"],
        fg=THEME["neon_cyan"]
    ).pack(pady=(5, 2))
    
    # 节点计数器
    vis.node_counter_label = Label(
        status_frame,
        text="节点数量: 0",
        font=("Consolas", 14, "bold"),
        bg=THEME["bg_card"],
        fg=THEME["neon_green"]
    )
    vis.node_counter_label.pack(pady=2)
    
    # 速度控制
    speed_frame = Frame(status_frame, bg=THEME["bg_card"])
    speed_frame.pack(fill="x", pady=2)
    
    Label(
        speed_frame,
        text="⚡ 速度",
        font=("Microsoft YaHei UI", 9),
        bg=THEME["bg_card"],
        fg=THEME["neon_yellow"]
    ).pack(side="left", padx=(10, 5))
    
    vis.speed_var = Scale(
        speed_frame,
        from_=0.1, to=1.0,
        resolution=0.1,
        orient=HORIZONTAL,
        length=100,
        bg=THEME["bg_input"],
        fg=THEME["text_primary"],
        troughcolor=THEME["bg_dark"],
        highlightthickness=0,
        sliderrelief="flat",
        command=lambda v: _update_animation_speed(vis, float(v))
    )
    vis.speed_var.set(0.5)
    vis.speed_var.pack(side="left", padx=5)
    
    # ========== 增强功能按钮组 ==========
    enhanced_frame = Frame(vis.window, bg=THEME["bg_card"], bd=0)
    enhanced_frame.place(x=860, y=565, width=350, height=40)
    
    Label(
        enhanced_frame,
        text="✨",
        font=("Segoe UI Emoji", 12),
        bg=THEME["bg_card"],
        fg=THEME["neon_yellow"]
    ).place(x=8, y=8)
    
    # 增强按钮配置
    enhanced_btns = [
        ("搜索", lambda: _open_search_dialog(vis), THEME["neon_blue"], "search_btn"),
        ("遍历", lambda: _do_traverse(vis), THEME["neon_green"], "traverse_btn"),
        ("反转", lambda: _do_reverse(vis), THEME["neon_orange"], "reverse_btn"),
        ("长度", lambda: _do_get_length(vis), THEME["neon_purple"], "length_btn"),
        ("内存", lambda: _toggle_memory_addresses(vis), THEME["neon_pink"], "memory_btn"),
        ("清空", vis.clear_visualization, THEME["text_secondary"], "clear_btn"),
    ]
    
    x_offset = 35
    for text, cmd, bg, attr_name in enhanced_btns:
        btn = create_modern_button(
            enhanced_frame, text, cmd, bg,
            font_size=9
        )
        btn.place(x=x_offset, y=5)
        setattr(vis, attr_name, btn)
        x_offset += 60
    
    # 初始化内存地址显示状态
    vis.memory_addresses_visible = False
    vis.memory_labels = []


def _update_animation_speed(vis, speed):
    """更新动画速度"""
    try:
        if hasattr(vis, 'enhanced_ops') and vis.enhanced_ops:
            vis.enhanced_ops.set_animation_speed(speed)
    except:
        pass


def _open_search_dialog(vis):
    """打开现代化搜索对话框"""
    dialog = Toplevel(vis.window)
    dialog.title("🔍 搜索节点")
    dialog.geometry("350x180")
    dialog.resizable(False, False)
    dialog.configure(bg=THEME["bg_dark"])
    
    # 居中显示
    dialog.transient(vis.window)
    dialog.grab_set()
    
    # 标题
    Label(
        dialog,
        text="🔍 搜索节点",
        font=("Microsoft YaHei UI", 16, "bold"),
        bg=THEME["bg_dark"],
        fg=THEME["neon_cyan"]
    ).pack(pady=(20, 15))
    
    Label(
        dialog,
        text="输入要搜索的值:",
        font=("Microsoft YaHei UI", 11),
        bg=THEME["bg_dark"],
        fg=THEME["text_secondary"]
    ).pack(pady=5)
    
    search_var = StringVar()
    entry = Entry(
        dialog,
        font=("Consolas", 14),
        bg=THEME["bg_input"],
        fg=THEME["text_primary"],
        insertbackground=THEME["neon_cyan"],
        relief="flat",
        bd=0,
        textvariable=search_var,
        width=20,
        justify="center"
    )
    entry.pack(pady=10, ipady=8)
    entry.focus_set()
    
    def do_search():
        value = search_var.get().strip()
        if value:
            dialog.destroy()
            try:
                if hasattr(vis, 'enhanced_ops') and vis.enhanced_ops:
                    vis.enhanced_ops.search_with_animation(value)
            except Exception as e:
                from tkinter import messagebox
                messagebox.showerror("错误", f"搜索失败: {e}")
    
    search_btn = create_modern_button(
        dialog,
        "开始搜索",
        do_search,
        THEME["neon_blue"],
        font_size=12,
        emoji="🔍"
    )
    search_btn.pack(pady=15)
    
    entry.bind("<Return>", lambda e: do_search())


def _do_traverse(vis):
    """执行遍历操作"""
    try:
        if hasattr(vis, 'enhanced_ops') and vis.enhanced_ops:
            vis.enhanced_ops.traverse_with_animation()
    except Exception as e:
        from tkinter import messagebox
        messagebox.showerror("错误", f"遍历失败: {e}")


def _do_reverse(vis):
    """执行反转操作"""
    try:
        if hasattr(vis, 'enhanced_ops') and vis.enhanced_ops:
            vis.enhanced_ops.reverse_with_animation()
    except Exception as e:
        from tkinter import messagebox
        messagebox.showerror("错误", f"反转失败: {e}")


def _do_get_length(vis):
    """计算链表长度"""
    try:
        if hasattr(vis, 'enhanced_ops') and vis.enhanced_ops:
            vis.enhanced_ops.get_length_with_animation()
    except Exception as e:
        from tkinter import messagebox
        messagebox.showerror("错误", f"计算长度失败: {e}")


def _toggle_memory_addresses(vis):
    """切换内存地址显示"""
    import random
    
    if vis.memory_addresses_visible:
        # 隐藏内存地址
        for label in vis.memory_labels:
            try:
                label.destroy()
            except:
                pass
        vis.memory_labels = []
        vis.memory_addresses_visible = False
        vis.memory_btn.config(text="内存")
        vis.information.config(text="已隐藏内存地址显示")
    else:
        # 显示内存地址
        vis.memory_labels = []
        base_addr = random.randint(0x1000, 0x8000)
        
        for i, pos in enumerate(vis.linked_list_position):
            addr = hex(base_addr + i * 16)
            label = Label(
                vis.canvas_make,
                text=f"@{addr}",
                font=("Consolas", 9, "bold"),
                bg=THEME["bg_card"],
                fg=THEME["neon_green"],
                padx=3,
                pady=1
            )
            label.place(x=pos[4] + 20, y=pos[5] + 75)
            vis.memory_labels.append(label)
        
        vis.memory_addresses_visible = True
        vis.memory_btn.config(text="隐藏")
        vis.information.config(text=f"📍 显示内存地址 | 模拟基址: {hex(base_addr)}")


def update_node_counter(vis):
    """更新节点计数器显示"""
    try:
        count = len(vis.node_value_store)
        if hasattr(vis, 'node_counter_label') and vis.node_counter_label:
            vis.node_counter_label.config(text=f"节点数量: {count}")
    except:
        pass
