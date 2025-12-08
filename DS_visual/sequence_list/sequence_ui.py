# sequence_list/sequence_ui.py
from tkinter import Label, Button, Frame, Entry, X

def create_heading(vis):
    """标题栏 - 在主应用中已有顶部栏，此处不再创建"""
    # 当嵌入主应用时，主应用已有标题栏，无需重复创建
    pass

def create_buttons(vis):
    """把原来 create_buttons 的逻辑移到这里,vis 是 SequenceListVisualizer 实例"""
    # 操作按钮框架 - 使用pack布局，紧贴在主内容区域下方
    button_frame = Frame(vis.window, bg="#f8fbff", relief="raised", bd=1)
    button_frame.pack(fill=X, padx=10, pady=(0, 5))
    
    # 按钮样式配置 - 缩小按钮尺寸以适应布局
    button_style = {
        "font": ("Arial", 10, "bold"),
        "relief": "raised",
        "bd": 2,
        "padx": 8,
        "pady": 4,
        "width": 10
    }

    # 构建顺序表按钮
    build_list_btn = Button(button_frame, text="构建顺序表", 
                            bg="#27ae60", fg="white", activebackground="#2ecc71",
                            command=vis.prepare_build_list, **button_style)
    build_list_btn.grid(row=0, column=0, padx=5, pady=5)
    vis.buttons.append(build_list_btn)

    # 插入按钮
    insert_first_btn = Button(button_frame, text="头部插入",
                              bg="#e67e22", fg="white", activebackground="#f39c12",
                              command=lambda: vis.prepare_insert(0), **button_style)
    insert_first_btn.grid(row=0, column=1, padx=5, pady=5)
    vis.buttons.append(insert_first_btn)

    insert_last_btn = Button(button_frame, text="尾部插入",
                             bg="#e67e22", fg="white", activebackground="#f39c12",
                             command=lambda: vis.prepare_insert(len(vis.data_store)), **button_style)
    insert_last_btn.grid(row=0, column=2, padx=5, pady=5)
    vis.buttons.append(insert_last_btn)

    insert_pos_btn = Button(button_frame, text="位置插入",
                            bg="#e67e22", fg="white", activebackground="#f39c12",
                            command=vis.prepare_insert_with_position, **button_style)
    insert_pos_btn.grid(row=0, column=3, padx=5, pady=5)
    vis.buttons.append(insert_pos_btn)

    # 保存 / 打开 按钮
    save_btn = Button(button_frame, text="保存",
                      bg="#3498db", fg="white", activebackground="#2980b9",
                      command=vis.save_sequence, **button_style)
    save_btn.grid(row=0, column=4, padx=5, pady=5)
    vis.buttons.append(save_btn)

    load_btn = Button(button_frame, text="打开",
                      bg="#3498db", fg="white", activebackground="#2980b9",
                      command=vis.load_sequence, **button_style)
    load_btn.grid(row=0, column=5, padx=5, pady=5)
    vis.buttons.append(load_btn)

    # 删除按钮
    delete_first_btn = Button(button_frame, text="头部删除",
                              bg="#e74c3c", fg="white", activebackground="#c0392b",
                              command=vis.delete_first, **button_style)
    delete_first_btn.grid(row=1, column=0, padx=5, pady=5)
    vis.buttons.append(delete_first_btn)

    delete_last_btn = Button(button_frame, text="尾部删除",
                             bg="#e74c3c", fg="white", activebackground="#c0392b",
                             command=vis.delete_last, **button_style)
    delete_last_btn.grid(row=1, column=1, padx=5, pady=5)
    vis.buttons.append(delete_last_btn)

    delete_pos_btn = Button(button_frame, text="位置删除",
                            bg="#e74c3c", fg="white", activebackground="#c0392b",
                            command=vis.prepare_delete_with_position, **button_style)
    delete_pos_btn.grid(row=1, column=2, padx=5, pady=5)
    vis.buttons.append(delete_pos_btn)

    # 清空按钮
    clear_btn = Button(button_frame, text="清空",
                       bg="#9b59b6", fg="white", activebackground="#8e44ad",
                       command=vis.clear_list, **button_style)
    clear_btn.grid(row=1, column=3, padx=5, pady=5)
    vis.buttons.append(clear_btn)

    # 返回主界面按钮
    back_btn = Button(button_frame, text="返回主界面",
                      bg="#34495e", fg="white", activebackground="#2c3e50",
                      command=vis.back_to_main, **button_style)
    back_btn.grid(row=1, column=4, padx=5, pady=5)
    vis.buttons.append(back_btn)

    # 冒泡排序按钮
    bubble_sort_btn = Button(button_frame, text="冒泡排序",
                             bg="#8e44ad", fg="white", activebackground="#9b59b6",
                             command=vis.start_bubble_sort, **button_style)
    bubble_sort_btn.grid(row=1, column=5, padx=5, pady=5)
    vis.buttons.append(bubble_sort_btn)

    # 插入排序按钮
    insertion_sort_btn = Button(button_frame, text="插入排序",
                                bg="#16a085", fg="white", activebackground="#1abc9c",
                                command=vis.start_insertion_sort, **button_style)
    insertion_sort_btn.grid(row=2, column=0, padx=5, pady=5)
    vis.buttons.append(insertion_sort_btn)

    # 快速排序按钮
    quick_sort_btn = Button(button_frame, text="快速排序",
                            bg="#e91e63", fg="white", activebackground="#f06292",
                            command=vis.start_quick_sort, **button_style)
    quick_sort_btn.grid(row=2, column=1, padx=5, pady=5)
    vis.buttons.append(quick_sort_btn)

    # 逆置按钮
    reverse_btn = Button(button_frame, text="逆置",
                         bg="#00bcd4", fg="white", activebackground="#26c6da",
                         command=vis.start_reverse, **button_style)
    reverse_btn.grid(row=2, column=2, padx=5, pady=5)
    vis.buttons.append(reverse_btn)

    # DSL 输入区域
    dsl_frame = Frame(button_frame, bg="#f8fbff")
    dsl_frame.grid(row=2, column=3, columnspan=3, padx=5, pady=5, sticky="ew")
    
    dsl_label = Label(dsl_frame, text="DSL:", font=("Arial", 10, "bold"), 
                     bg="#f8fbff", fg="#2c3e50")
    dsl_label.pack(side="left", padx=(5, 3))
    
    dsl_entry = Entry(dsl_frame, textvariable=vis.dsl_var, font=("Arial", 10), 
                     width=35, relief="solid", bd=1, bg="#ffffff", fg="#2c3e50")
    dsl_entry.pack(side="left", padx=3, pady=3)
    
    dsl_btn = Button(dsl_frame, text="执行", font=("Arial", 10, "bold"),
                     bg="#2ecc71", fg="white", activebackground="#27ae60",
                     relief="raised", bd=2, padx=10, pady=2,
                     command=vis.process_dsl)
    dsl_btn.pack(side="left", padx=5, pady=3)
    
    dsl_entry.bind("<Return>", lambda e: vis.process_dsl())