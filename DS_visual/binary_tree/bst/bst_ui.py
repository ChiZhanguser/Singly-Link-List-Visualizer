from tkinter import Button, Label, Entry, Frame, X, LEFT, RIGHT, TOP, BOTTOM

def create_controls(self):  # 创建控制按钮
    # 主控制框架 - 放在窗口顶部，使用更小的高度
    main_control_frame = Frame(self.window, bg="#F7F9FB", height=80)  # 减少高度
    main_control_frame.pack(side=TOP, fill=X, pady=1, padx=6)
    main_control_frame.pack_propagate(False)  # 防止框架收缩
    
    # 单行布局：所有控件放在一行
    control_row = Frame(main_control_frame, bg="#F7F9FB")
    control_row.pack(fill=X, pady=2)
    
    # 输入标签和框
    Label(control_row, text="值:", 
          font=("Arial", 10), bg="#F7F9FB").pack(side=LEFT, padx=(0,2))
    
    entry = Entry(control_row, textvariable=self.input_var, width=15, font=("Arial", 10))
    entry.pack(side=LEFT, padx=(0,8))
    entry.insert(0, "15,6,23,4,7,71,5")
    
    # 主要操作按钮 - 减小宽度
    Button(control_row, text="插入", command=self.insert_direct, 
           bg="green", fg="white", width=6).pack(side=LEFT, padx=1)
    Button(control_row, text="动画插入", command=self.start_insert_animated, 
           bg="#2E8B57", fg="white", width=8).pack(side=LEFT, padx=1)
    Button(control_row, text="搜索", command=self.start_search_animated, 
           bg="#FFA500", width=6).pack(side=LEFT, padx=1)
    Button(control_row, text="删除", command=self.start_delete_animated, 
           bg="red", fg="white", width=6).pack(side=LEFT, padx=1)
    
    # 清空和返回按钮
    Button(control_row, text="清空", command=self.clear_canvas, 
           bg="orange", width=5).pack(side=LEFT, padx=1)
    Button(control_row, text="返回", command=self.back_to_main, 
           bg="blue", fg="white", width=5).pack(side=LEFT, padx=1)
    
    # 文件操作按钮
    Button(control_row, text="保存", command=self.save_tree, 
           bg="#6C9EFF", fg="white", width=5).pack(side=LEFT, padx=1)
    Button(control_row, text="打开", command=self.load_tree, 
           bg="#6C9EFF", fg="white", width=5).pack(side=LEFT, padx=1)
    
    # DSL命令 - 放在同一行
    Label(control_row, text="DSL:", font=("Arial", 10), 
          bg="#F7F9FB").pack(side=LEFT, padx=(10,2))
    
    self.dsl_entry = Entry(control_row, width=12, font=("Arial", 10), 
                          textvariable=self.dsl_var)
    self.dsl_entry.pack(side=LEFT, padx=(0,2))
    self.dsl_entry.bind("<Return>", lambda e: self.process_dsl())
    
    Button(control_row, text="执行", command=self.process_dsl, 
           width=4).pack(side=LEFT, padx=1)

def draw_instructions(self):  # 绘制操作说明
    # 先清除画布上的节点，但保留背景
    for item in self.node_items:
        self.canvas.delete(item)
    self.node_items.clear()
    self.node_to_rect.clear()
    
    # 绘制说明文字 - 位置稍微下移，避免被控制面板遮挡
    self.canvas.create_text(10, 30, anchor="nw", 
                           text="BST：插入/查找/删除动态演示。中序位置用于横向布局。", 
                           font=("Arial", 10), tags="instructions")
    
    if self.status_text_id:
        self.canvas.delete(self.status_text_id)
    
    self.status_text_id = self.canvas.create_text(
        self.canvas_width-10, 30, anchor="ne", text="", 
        font=("Arial", 11, "bold"), fill="darkgreen", tags="instructions"
    )