# sequence_list/sequence_ui.py
from tkinter import Label, Button, Frame, Entry, X

def create_heading(vis):
    """为 SequenceListVisualizer 创建标题/信息栏"""
    # 创建标题背景
    heading_frame = Frame(vis.window, bg="#4a6baf", height=120)
    heading_frame.pack(fill=X, pady=(0, 10))
    heading_frame.pack_propagate(False)
    
    heading = Label(heading_frame, text="顺序表(线性表)可视化系统",
                    font=("微软雅黑", 24, "bold"), bg="#4a6baf", fg="white")
    heading.pack(pady=(20, 5))
    
    info = Label(heading_frame, text="顺序表在内存中连续存储,插入和删除操作需要移动元素",
                 font=("微软雅黑", 12), bg="#4a6baf", fg="#e8f4fd")
    info.pack(pady=(0, 20))

def create_buttons(vis):
    """把原来 create_buttons 的逻辑移到这里,vis 是 SequenceListVisualizer 实例"""
    # 操作按钮框架
    button_frame = Frame(vis.window, bg="#f8fbff", relief="raised", bd=1)
    button_frame.place(x=50, y=490, width=1250, height=180)
    
    # 按钮样式配置
    button_style = {
        "font": ("Arial", 11, "bold"),
        "relief": "raised",
        "bd": 2,
        "padx": 12,
        "pady": 6,
        "width": 12
    }

    # 构建顺序表按钮 - 新增
    build_list_btn = Button(button_frame, text="构建顺序表", 
                            bg="#27ae60", fg="white", activebackground="#2ecc71",
                            command=vis.prepare_build_list, **button_style)
    build_list_btn.grid(row=0, column=0, padx=8, pady=8)
    vis.buttons.append(build_list_btn)

    # 插入按钮
    insert_first_btn = Button(button_frame, text="头部插入",
                              bg="#e67e22", fg="white", activebackground="#f39c12",
                              command=lambda: vis.prepare_insert(0), **button_style)
    insert_first_btn.grid(row=0, column=1, padx=8, pady=8)
    vis.buttons.append(insert_first_btn)

    insert_last_btn = Button(button_frame, text="尾部插入",
                             bg="#e67e22", fg="white", activebackground="#f39c12",
                             command=lambda: vis.prepare_insert(len(vis.data_store)), **button_style)
    insert_last_btn.grid(row=0, column=2, padx=8, pady=8)
    vis.buttons.append(insert_last_btn)

    insert_pos_btn = Button(button_frame, text="指定位置插入",
                            bg="#e67e22", fg="white", activebackground="#f39c12",
                            command=vis.prepare_insert_with_position, **button_style)
    insert_pos_btn.grid(row=0, column=3, padx=8, pady=8)
    vis.buttons.append(insert_pos_btn)

    # 删除按钮
    delete_first_btn = Button(button_frame, text="头部删除",
                              bg="#e74c3c", fg="white", activebackground="#c0392b",
                              command=vis.delete_first, **button_style)
    delete_first_btn.grid(row=1, column=0, padx=8, pady=8)
    vis.buttons.append(delete_first_btn)

    delete_last_btn = Button(button_frame, text="尾部删除",
                             bg="#e74c3c", fg="white", activebackground="#c0392b",
                             command=vis.delete_last, **button_style)
    delete_last_btn.grid(row=1, column=1, padx=8, pady=8)
    vis.buttons.append(delete_last_btn)

    delete_pos_btn = Button(button_frame, text="指定位置删除",
                            bg="#e74c3c", fg="white", activebackground="#c0392b",
                            command=vis.prepare_delete_with_position, **button_style)
    delete_pos_btn.grid(row=1, column=2, padx=8, pady=8)
    vis.buttons.append(delete_pos_btn)

    # 清空按钮
    clear_btn = Button(button_frame, text="清空顺序表",
                       bg="#9b59b6", fg="white", activebackground="#8e44ad",
                       command=vis.clear_list, **button_style)
    clear_btn.grid(row=1, column=3, padx=8, pady=8)
    vis.buttons.append(clear_btn)

    # 返回主界面按钮
    back_btn = Button(button_frame, text="返回主界面",
                      bg="#34495e", fg="white", activebackground="#2c3e50",
                      command=vis.back_to_main, **button_style)
    back_btn.grid(row=1, column=4, padx=8, pady=8)
    vis.buttons.append(back_btn)

    # 保存 / 打开 按钮
    save_btn = Button(button_frame, text="保存顺序表",
                      bg="#3498db", fg="white", activebackground="#2980b9",
                      command=vis.save_sequence, **button_style)
    save_btn.grid(row=0, column=5, padx=8, pady=8)
    vis.buttons.append(save_btn)

    load_btn = Button(button_frame, text="打开顺序表",
                      bg="#3498db", fg="white", activebackground="#2980b9",
                      command=vis.load_sequence, **button_style)
    load_btn.grid(row=0, column=6, padx=8, pady=8)
    vis.buttons.append(load_btn)

    # DSL 输入区域
    dsl_frame = Frame(button_frame, bg="#f8fbff")
    dsl_frame.grid(row=2, column=0, columnspan=7, padx=10, pady=8, sticky="ew")
    
    dsl_label = Label(dsl_frame, text="DSL 命令:", font=("Arial", 12, "bold"), 
                     bg="#f8fbff", fg="#2c3e50")
    dsl_label.pack(side="left", padx=(10, 5))
    
    dsl_entry = Entry(dsl_frame, textvariable=vis.dsl_var, font=("Arial", 12), 
                     width=40, relief="solid", bd=1, bg="#ffffff", fg="#2c3e50")
    dsl_entry.pack(side="left", padx=5, pady=5)
    
    dsl_btn = Button(dsl_frame, text="执行 DSL", font=("Arial", 11, "bold"),
                     bg="#2ecc71", fg="white", activebackground="#27ae60",
                     relief="raised", bd=2, padx=15, pady=4,
                     command=vis.process_dsl)
    dsl_btn.pack(side="left", padx=10, pady=5)
    
    dsl_entry.bind("<Return>", lambda e: vis.process_dsl())