from tkinter import Button, Label, Entry, Frame, X, LEFT, RIGHT, SOLID, FLAT, RIDGE

def create_heading(self):
    # 创建标题容器
    header_frame = Frame(self.window, bg="#F8FAFC")
    header_frame.place(x=0, y=0, width=1350, height=140)
    
    # 主标题区域（带有现代感的设计）
    title_container = Frame(header_frame, bg="#FFFFFF", relief=SOLID, bd=1)
    title_container.place(relx=0.5, y=20, anchor="n", width=800, height=100)
    
    # Logo和标题组合
    title_frame = Frame(title_container, bg="#FFFFFF")
    title_frame.pack(pady=12)
    
    # Logo圆形背景
    logo_frame = Frame(title_frame, bg="#4F46E5", width=46, height=46)
    logo_frame.pack(side=LEFT, padx=(0,15))
    logo_frame.pack_propagate(False)
    
    # Logo文字
    Label(logo_frame, text="S", font=("Helvetica", 24, "bold"), 
          bg="#4F46E5", fg="white").place(relx=0.5, rely=0.5, anchor="center")
    
    # 标题和描述垂直排列
    text_frame = Frame(title_frame, bg="#FFFFFF")
    text_frame.pack(side=LEFT)
    
    heading = Label(text_frame, text="栈的可视化", 
                   font=("Microsoft YaHei UI", 24, "bold"), 
                   bg="#FFFFFF", fg="#1E293B")
    heading.pack(anchor="w")
    
    info = Label(text_frame, 
                text="Stack Visualization · LIFO (Last In First Out)", 
                font=("Segoe UI", 12),
                bg="#FFFFFF", fg="#6B7280")
    info.pack(anchor="w", pady=(4,0))
    
    # 右侧附加信息
    status_frame = Frame(title_container, bg="#F8FAFC", relief=SOLID, bd=1)
    status_frame.place(relx=0.92, rely=0.5, anchor="e")
    
    Label(status_frame, text="后进先出", font=("Microsoft YaHei UI", 12, "bold"),
          bg="#F8FAFC", fg="#3B82F6", padx=12, pady=6).pack()

def create_buttons(self):
    # 主控制面板
    control_panel = Frame(self.window, bg="#FFFFFF", relief=RIDGE, bd=1)
    control_panel.place(x=50, y=540, width=1250, height=180)
    
    # 操作按钮区域
    button_frame = Frame(control_panel, bg="#FFFFFF")
    button_frame.pack(pady=15)
    
    # 统一的按钮样式
    btn_style = {
        "font": ("Microsoft YaHei UI", 12, "bold"),
        "width": 16,
        "height": 2,
        "bd": 0,
        "relief": FLAT,
        "cursor": "hand2"  # 鼠标悬停时显示手型
    }
    
    # 创建按钮容器来实现阴影效果
    def create_button(parent, text, color, active_color, command):
        frame = Frame(parent, bg="#E5E7EB")
        frame.pack(side=LEFT, padx=12)
        btn = Button(frame, text=text, bg=color, fg="white",
                    activebackground=active_color,
                    activeforeground="white",
                    command=command, **btn_style)
        btn.pack(padx=1, pady=1)  # 1像素偏移创造阴影效果
        return btn

    # 创建主要操作按钮
    self.push_btn = create_button(button_frame, "入栈 Push", "#3B82F6", "#2563EB", self.prepare_push)
    self.pop_btn = create_button(button_frame, "出栈 Pop", "#10B981", "#059669", self.pop)
    self.clear_btn = create_button(button_frame, "清空栈", "#EF4444", "#DC2626", self.clear_stack)
    self.back_btn = create_button(button_frame, "返回主界面", "#6B7280", "#4B5563", self.back_to_main)

    # 创建输入区域容器
    input_area = Frame(control_panel, bg="#FFFFFF")
    input_area.pack(fill=X, padx=20, pady=(5, 15))
    
    # 批量构建区域
    batch_frame = Frame(input_area, bg="#F8FAFC", relief=SOLID, bd=1)
    batch_frame.pack(fill=X, pady=(0, 8))
    
    batch_label = Label(batch_frame, text="批量构建", 
                       font=("Microsoft YaHei UI", 11, "bold"),
                       bg="#F8FAFC", fg="#374151")
    batch_label.pack(side=LEFT, padx=(15, 8), pady=10)
    
    hint_label = Label(batch_frame, text="(使用逗号分隔多个值)", 
                      font=("Microsoft YaHei UI", 9),
                      bg="#F8FAFC", fg="#6B7280")
    hint_label.pack(side=LEFT, pady=10)
    
    batch_entry = Entry(batch_frame, textvariable=self.batch_entry_var,
                       width=50, font=("Segoe UI", 11),
                       relief=FLAT, bg="#FFFFFF",
                       highlightthickness=1,
                       highlightbackground="#E5E7EB",
                       highlightcolor="#3B82F6")
    batch_entry.pack(side=LEFT, padx=15, pady=10)
    
    self.batch_build_btn = Button(batch_frame, text="开始构建",
                                 font=("Microsoft YaHei UI", 10, "bold"),
                                 bg="#3B82F6", fg="white",
                                 activebackground="#2563EB",
                                 activeforeground="white",
                                 relief=FLAT, bd=0,
                                 padx=15, pady=5,
                                 cursor="hand2",
                                 command=self.start_batch_build)
    self.batch_build_btn.pack(side=LEFT, padx=(0, 15), pady=10)
    
    # DSL 命令区域
    dsl_frame = Frame(input_area, bg="#F8FAFC", relief=SOLID, bd=1)
    dsl_frame.pack(fill=X)
    
    dsl_label = Label(dsl_frame, text="DSL 命令", 
                     font=("Microsoft YaHei UI", 11, "bold"),
                     bg="#F8FAFC", fg="#374151")
    dsl_label.pack(side=LEFT, padx=(15, 8), pady=10)
    
    hint_label = Label(dsl_frame, text="(按回车执行)", 
                      font=("Microsoft YaHei UI", 9),
                      bg="#F8FAFC", fg="#6B7280")
    hint_label.pack(side=LEFT, pady=10)
    
    dsl_entry = Entry(dsl_frame, textvariable=self.dsl_var,
                     width=65, font=("Segoe UI", 11),
                     relief=FLAT, bg="#FFFFFF",
                     highlightthickness=1,
                     highlightbackground="#E5E7EB",
                     highlightcolor="#3B82F6")
    dsl_entry.pack(side=LEFT, padx=15, pady=10)
    dsl_entry.bind("<Return>", self.process_dsl)
    
    execute_btn = Button(dsl_frame, text="执行命令",
                        font=("Microsoft YaHei UI", 10, "bold"),
                        bg="#10B981", fg="white",
                        activebackground="#059669",
                        activeforeground="white",
                        relief=FLAT, bd=0,
                        padx=15, pady=5,
                        cursor="hand2",
                        command=self.process_dsl)
    execute_btn.pack(side=LEFT, padx=(0, 15), pady=10)

    # 添加保存和打开按钮
    file_frame = Frame(button_frame, bg="#FFFFFF")
    file_frame.pack(side=LEFT, padx=12)
    
    # 创建一个容器来放置两个文件操作按钮
    save_btn = Button(file_frame, text="💾 保存栈",
                     font=("Microsoft YaHei UI", 11),
                     bg="#F1F5F9", fg="#334155",
                     activebackground="#E2E8F0",
                     activeforeground="#1E293B",
                     relief=FLAT, bd=0,
                     padx=15, pady=8,
                     cursor="hand2",
                     command=self.save_structure)
    save_btn.pack(side=LEFT, padx=2)
    
    load_btn = Button(file_frame, text="📂 打开栈",
                     font=("Microsoft YaHei UI", 11),
                     bg="#F1F5F9", fg="#334155",
                     activebackground="#E2E8F0",
                     activeforeground="#1E293B",
                     relief=FLAT, bd=0,
                     padx=15, pady=8,
                     cursor="hand2",
                     command=self.load_structure)
    load_btn.pack(side=LEFT, padx=2)