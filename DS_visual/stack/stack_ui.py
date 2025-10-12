from tkinter import Button, Label, Entry, Frame, X, LEFT, RIGHT

def create_heading(self):
    heading = Label(self.window, text="栈(顺序栈)的可视化",
                    font=("Arial", 30, "bold"), bg="#E6F3FF", fg="darkblue")
    heading.place(x=450, y=20)

    info = Label(self.window, text="栈是一种后进先出(LIFO)的数据结构，只能在栈顶进行插入和删除操作",
                    font=("Arial", 16), bg="#E6F3FF", fg="black")
    info.place(x=300, y=80)

def create_buttons(self):
    button_frame = Frame(self.window, bg="#E6F3FF")
    button_frame.place(x=50, y=540, width=1250, height=160)

    self.push_btn = Button(button_frame, text="入栈(Push)", font=("Arial", 14),
                            width=15, height=2, bg="green", fg="white",
                            command=self.prepare_push)
    self.push_btn.grid(row=0, column=0, padx=20, pady=8)

    self.pop_btn = Button(button_frame, text="出栈(Pop)", font=("Arial", 14),
                            width=15, height=2, bg="red", fg="white",
                            command=self.pop)
    self.pop_btn.grid(row=0, column=1, padx=20, pady=8)

    self.clear_btn = Button(button_frame, text="清空栈", font=("Arial", 14),
                            width=15, height=2, bg="orange", fg="white",
                            command=self.clear_stack)
    self.clear_btn.grid(row=0, column=2, padx=20, pady=8)

    self.back_btn = Button(button_frame, text="返回主界面", font=("Arial", 14),
                            width=15, height=2, bg="blue", fg="white",
                            command=self.back_to_main)
    self.back_btn.grid(row=0, column=3, padx=20, pady=8)

    batch_label = Label(button_frame, text="批量构建 (逗号分隔):", font=("Arial", 12), bg="#E6F3FF")
    batch_label.grid(row=1, column=0, padx=(20, 4), pady=6, sticky="w")
    batch_entry = Entry(button_frame, textvariable=self.batch_entry_var, width=40, font=("Arial", 12))
    batch_entry.grid(row=1, column=1, columnspan=2, padx=4, pady=6, sticky="w")
    self.batch_build_btn = Button(button_frame, text="开始批量构建", font=("Arial", 12),
                                    command=self.start_batch_build)
    self.batch_build_btn.grid(row=1, column=3, padx=10, pady=6)

    # DSL 输入行（第三行）
    dsl_label = Label(button_frame, text="DSL 命令:", font=("Arial", 12), bg="#E6F3FF")
    dsl_label.grid(row=2, column=0, padx=(20, 4), pady=6, sticky="w")
    dsl_entry = Entry(button_frame, textvariable=self.dsl_var, width=60, font=("Arial", 12))
    dsl_entry.grid(row=2, column=1, columnspan=3, padx=4, pady=6, sticky="w")
    dsl_entry.bind("<Return>", self.process_dsl)   # 回车执行
    Button(button_frame, text="执行", font=("Arial", 12), command=self.process_dsl).grid(row=2, column=4, padx=10, pady=6)

    Button(button_frame, text="保存栈", font=("Arial", 14), width=15, height=2, bg="#6C9EFF", fg="white",
            command=self.save_structure).grid(row=0, column=4, padx=20, pady=8)
    Button(button_frame, text="打开栈", font=("Arial", 14), width=15, height=2, bg="#6C9EFF", fg="white",
            command=self.load_structure).grid(row=0, column=5, padx=20, pady=8)