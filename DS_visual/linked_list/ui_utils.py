from tkinter import Label, Button

def draw_gradient(canvas, width, height, start_color="#000000", end_color="#FFFFFF", steps=100):
    """在指定 canvas 上绘制渐变（与原 draw_gradient 等价，但独立成函数）"""
    def hex_to_rgb(h): h = h.lstrip('#'); return tuple(int(h[i:i+2],16) for i in (0,2,4))
    def rgb_to_hex(r,g,b): return f'#{r:02x}{g:02x}{b:02x}'
    (r1,g1,b1),(r2,g2,b2) = hex_to_rgb(start_color), hex_to_rgb(end_color)
    for i in range(steps):
        t = i / max(steps - 1,1)
        r = int(r1 + (r2 - r1) * t); g = int(g1 + (g2 - g1) * t); b = int(b1 + (b2 - b1) * t)
        color = rgb_to_hex(r,g,b)
        y0 = int(i * (height / steps)); y1 = int((i + 1) * (height / steps))
        canvas.create_rectangle(0, y0, width, y1, outline="", fill=color)

def heading_with_label_subheading(vis):
    """把原来的 heading_with_label_subheading 转为函数，vis 是 LinkList 实例"""
    vis.head_name = vis.make_label(vis.window, text="单链表的可视化",
                                   font=("Arial",35,"bold","italic"),
                                   bg="chocolate", fg="yellow")
    vis.head_name.place(x=350,y=20)
    vis.information = vis.make_label(vis.window,
        text="start是指向第一个节点的指针\ntemp指针在insert_last和delete_last的时候用于遍历找到目标位置",
        font=("Arial",20,"bold","italic"), bg="chocolate", fg="#00FF00")
    vis.information.place(x=150,y=380)

def make_start_with_other(vis):
    """原 make_start_with_other"""
    vis.start_pointer = vis.make_rect(vis.start_left,vis.start_up,vis.start_left+30,vis.start_up+30,
                                      fill="blue", outline="black", width=3)
    vis.start_label = vis.make_label(vis.canvas_make, text="start", font=("Arial",15,"bold"),
                                     bg="chocolate", fg="green")
    vis.start_label.place(x=40,y=410)
    vis.pointing_line_start = vis.canvas_make.create_line(65,327,65,395,width=2,fill="green")
    vis.start_initial_point_null = vis.make_label(vis.canvas_make, text="NULL",
                                                   font=("Arial",15,"bold"), bg="chocolate", fg="blue")
    vis.start_initial_point_null.place(x=40, y=300)
    vis.temp_label = vis.make_label(vis.canvas_make, text="temp", font=("Arial",15,"bold"), bg="chocolate", fg="green")
    vis.temp1_label = vis.make_label(vis.canvas_make, text="temp1", font=("Arial",15,"bold"), bg="chocolate", fg="green")

def make_btn(vis):
    """原 make_btn，注意它会给 vis 设置若干属性（例如 insert_at_beg 等）"""
    btns = [
        ("Insert first", lambda: vis.make_node_with_label(1), 20,540),
        ("Insert last",  lambda: vis.make_node_with_label(0), 220,540),
        ("Delete first", vis.delete_first_node, 420,540),
        ("Delete last",  lambda: vis.delete_last_node(0), 620,540),
        ("Insert after node", vis.set_of_input_method, 830,540),
        ("Delete particular node", vis.delete_single_node_infrastructure, 1090,540),
        ("返回主界面", vis.back_to_main, 1090,600),
        ("保存链表", vis.save_structure, 900,600),
        ("打开链表", vis.load_structure, 900,650),
    ]
    for text, cmd, x, y in btns:
        btn = vis.make_button(vis.window, text=text,
                              bg=("black" if text.startswith(("Insert","Delete")) else "blue"),
                              fg="red" if text.startswith(("Insert","Delete")) else "white",
                              font=("Arial", 15 if len(text)>6 else 12, "bold"),
                              relief="raised", bd=10 if len(text)>6 else 6, command=cmd)
        btn.place(x=x, y=y)
        # attach to attr by cleaned name for later toggling
        if text == "Insert first": vis.insert_at_beg = btn
        if text == "Insert last": vis.insert_at_last = btn
        if text == "Delete first": vis.delete_at_first = btn
        if text == "Delete last": vis.delete_at_last = btn
        if text == "Insert after node": vis.insert_after_node = btn
        if text == "Delete particular node": vis.delete_particular_node = btn
        if text == "返回主界面": vis.back_to_main_btn = btn
        if text == "保存链表": vis.save_btn = btn
        if text == "打开链表": vis.load_btn = btn

def make_batch_create_ui(vis):
    """原 make_batch_create_ui"""
    Label(vis.window, text="批量创建（以逗号分隔）", font=("Arial", 12, "bold"), bg="lightgray").place(x=20, y=610)
    from tkinter import Entry  # 本地导入避免循环 import 问题
    Entry(vis.window, font=("Arial", 12), bg="white", textvar=vis.batch_entry_var, width=40).place(x=200, y=610)
    Button(vis.window, text="Create List", font=("Arial", 10, "bold"), bg="green", fg="white",
           relief="raised", bd=3, command=vis.create_list_from_string).place(x=620, y=607)

    Label(vis.window, text="DSL 命令:", font=("Arial", 12, "bold"), bg="lightgray").place(x=20, y=650)
    dsl_entry = Entry(vis.window, font=("Arial", 12), bg="white", textvar=vis.dsl_var, width=40)
    dsl_entry.place(x=200, y=650); dsl_entry.bind("<Return>", lambda e: vis.process_dsl())
    Button(vis.window, text="执行 DSL", font=("Arial", 10, "bold"), bg="green", fg="white",
           command=vis.process_dsl).place(x=620, y=647)