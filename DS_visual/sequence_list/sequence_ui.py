# sequence_list/sequence_ui.py
from tkinter import Label, Button, Frame, Entry

def create_heading(vis):
    """为 SequenceListVisualizer 创建标题/信息栏"""
    heading = Label(vis.window, text="顺序表(线性表)的可视化",
                    font=("Arial", 30, "bold"), bg="lightgreen", fg="darkblue")
    heading.place(x=400, y=20)

    info = Label(vis.window, text="顺序表在内存中连续存储，插入和删除操作需要移动元素",
                 font=("Arial", 16), bg="lightgreen", fg="black")
    info.place(x=400, y=80)


def create_buttons(vis):
    """把原来 create_buttons 的逻辑移到这里，vis 是 SequenceListVisualizer 实例"""
    # 操作按钮框架
    button_frame = Frame(vis.window, bg="lightgreen")
    button_frame.place(x=50, y=540, width=1250, height=150)

    # 构建顺序表按钮 - 新增
    build_list_btn = Button(button_frame, text="构建顺序表", font=("Arial", 12),
                            bg="teal", fg="white", command=vis.prepare_build_list)
    build_list_btn.grid(row=0, column=0, padx=10, pady=5)
    vis.buttons.append(build_list_btn)

    # 插入按钮
    insert_first_btn = Button(button_frame, text="头部插入", font=("Arial", 12),
                              bg="orange", command=lambda: vis.prepare_insert(0))
    insert_first_btn.grid(row=0, column=1, padx=10, pady=5)
    vis.buttons.append(insert_first_btn)

    insert_last_btn = Button(button_frame, text="尾部插入", font=("Arial", 12),
                             bg="orange", command=lambda: vis.prepare_insert(len(vis.data_store)))
    insert_last_btn.grid(row=0, column=2, padx=10, pady=5)
    vis.buttons.append(insert_last_btn)

    insert_pos_btn = Button(button_frame, text="指定位置插入", font=("Arial", 12),
                            bg="orange", command=vis.prepare_insert_with_position)
    insert_pos_btn.grid(row=0, column=3, padx=10, pady=5)
    vis.buttons.append(insert_pos_btn)

    # 删除按钮
    delete_first_btn = Button(button_frame, text="头部删除", font=("Arial", 12),
                              bg="red", fg="white", command=vis.delete_first)
    delete_first_btn.grid(row=1, column=0, padx=10, pady=5)
    vis.buttons.append(delete_first_btn)

    delete_last_btn = Button(button_frame, text="尾部删除", font=("Arial", 12),
                             bg="red", fg="white", command=vis.delete_last)
    delete_last_btn.grid(row=1, column=1, padx=10, pady=5)
    vis.buttons.append(delete_last_btn)

    delete_pos_btn = Button(button_frame, text="指定位置删除", font=("Arial", 12),
                            bg="red", fg="white", command=vis.prepare_delete_with_position)
    delete_pos_btn.grid(row=1, column=2, padx=10, pady=5)
    vis.buttons.append(delete_pos_btn)

    # 清空按钮
    clear_btn = Button(button_frame, text="清空顺序表", font=("Arial", 12),
                       bg="purple", fg="white", command=vis.clear_list)
    clear_btn.grid(row=1, column=3, padx=10, pady=5)
    vis.buttons.append(clear_btn)

    # 返回主界面按钮
    back_btn = Button(button_frame, text="返回主界面", font=("Arial", 12),
                      bg="blue", fg="white", command=vis.back_to_main)
    back_btn.grid(row=1, column=4, padx=10, pady=5)
    vis.buttons.append(back_btn)

    # 保存 / 打开 按钮
    save_btn = Button(button_frame, text="保存顺序表", font=("Arial", 12),
                      bg="#6C9EFF", fg="white", command=vis.save_sequence)
    save_btn.grid(row=0, column=5, padx=10, pady=5)
    vis.buttons.append(save_btn)

    load_btn = Button(button_frame, text="打开顺序表", font=("Arial", 12),
                      bg="#6C9EFF", fg="white", command=vis.load_sequence)
    load_btn.grid(row=0, column=6, padx=10, pady=5)
    vis.buttons.append(load_btn)

    # DSL 输入
    dsl_label = Label(button_frame, text="DSL 命令:", font=("Arial", 12), bg="lightgreen")
    dsl_label.grid(row=2, column=0, padx=(10, 2), pady=8, sticky="w")
    dsl_entry = Entry(button_frame, textvariable=vis.dsl_var, font=("Arial", 12), width=40)
    dsl_entry.grid(row=2, column=1, columnspan=3, padx=4, pady=8, sticky="w")
    dsl_entry.bind("<Return>", lambda e: vis.process_dsl())
    dsl_btn = Button(button_frame, text="执行 DSL", font=("Arial", 12), bg="#4CAF50", fg="white",
                     command=vis.process_dsl)
    dsl_btn.grid(row=2, column=4, padx=10, pady=8)
