from tkinter import *
from tkinter import messagebox
import time
from linked_list.linked_list_model import LinkedListModel
import storage as storage
from llm import function_dispatcher

class LinkList:
    def __init__(self, root):
        self.window = root
        self.window.config(bg="#F5F7FA")
        self.canvas_width, self.canvas_height = 1350, 500
        self.canvas_make = Canvas(self.window, bg="#0575E6",
                                  width=self.canvas_width, height=self.canvas_height,
                                  relief=RAISED, bd=8)
        self.canvas_make.pack()
        self.draw_gradient(self.canvas_make, self.canvas_width, self.canvas_height,
                           start_color="#021B79", end_color="#89CFF0", steps=200)

        # model & stores
        self.model = LinkedListModel()
        self.node_value_store = self.model.node_value_store
        self.linked_list_canvas_small_widget = []
        self.linked_list_canvas_small_widget_label = []
        self.linked_list_position = []
        self.linked_list_data_next_store = []

        # inputs
        self.value_entry = StringVar(value=" ")
        self.position_entry = StringVar(value=" ")
        self.delete_entry = StringVar(value=" ")
        self.batch_entry_var = StringVar(value=" ")
        self.dsl_var = StringVar(value="")

        # coordinates / small state initialized via helper
        self._init_coords()

        # many widget attributes set to None generically (previous代码大量显式声明)
        for name in ("head_name","information","insert_at_beg","insert_at_last","delete_at_first",
                     "delete_at_last","position_label","start_label","temp_label","temp1_label",
                     "data_label","next_label","element_take_label","element_take_entry","add_btn",
                     "value_set","next_set","start_initial_point_null","new_node_label",
                     "position_take_entry","find_btn","insert_after_node","delete_particular_node",
                     "save_btn","load_btn","back_to_main_btn"):
            setattr(self, name, None)

        # build UI
        self.heading_with_label_subheading()
        self.make_btn()
        self.make_start_with_other()
        self.make_batch_create_ui()

        # register visualizer if possible
        try:
            function_dispatcher.register_visualizer("linked_list", self)
            print("linked list visualizer registered.")
        except Exception as e:
            print("linked list registered failed:", e)

        try:
            import linked_list_api
            linked_list_api.bind_visualizer(self)
            print("linked_list_api successfully bound to visualizer (model shared).")
        except Exception as e:
            print("linked_list_api bind failed:", e)

    def _init_coords(self):
        # initial coordinates (kept names from original for compatibility)
        self.start_left = 50; self.start_up = 380
        self.main_node_left = 25; self.main_node_up = 120
        self.data_left = 30; self.data_up = 150
        self.data_label_x = 30; self.data_label_y = 122
        self.temp_label_x = 40; self.temp_label_y = 150
        self.temp_pointer_left = 50; self.temp_pointer_up = 180
        self.pointing_line_temp_left = 65; self.pointing_line_temp_up = 195
        # dynamic handles
        self.pointing_line_start = None
        self.pointing_line_temp = None
        self.pointing_line_temp1 = None
        self.temp_pointer = None
        self.temp1_pointer = None
        self.temp_label_x = 40
        self.node_helpers_reset()

    def node_helpers_reset(self):
        # placeholders used during animations & creation
        self.data = None; self.next = None; self.main_container_node = None
        self.arrow = None; self.value_set = None; self.next_set = None

    def make_label(self, parent, **kw):
        lbl = Label(parent, **kw)
        return lbl

    def make_button(self, parent, **kw):
        btn = Button(parent, **kw)
        return btn

    def make_rect(self, x1, y1, x2, y2, **kw):
        return self.canvas_make.create_rectangle(x1, y1, x2, y2, **kw)

    def toggle_action_buttons(self, state):
        for btn_attr in ("insert_at_last","insert_at_beg","delete_at_last","delete_at_first",
                         "insert_after_node","delete_particular_node","save_btn","load_btn"):
            b = getattr(self, btn_attr, None)
            if b:
                try: b.config(state=state)
                except: pass

    # -------- gradient & heading --------
    def draw_gradient(self, canvas, width, height, start_color="#000000", end_color="#FFFFFF", steps=100):
        def hex_to_rgb(h): h = h.lstrip('#'); return tuple(int(h[i:i+2],16) for i in (0,2,4))
        def rgb_to_hex(r,g,b): return f'#{r:02x}{g:02x}{b:02x}'
        (r1,g1,b1),(r2,g2,b2) = hex_to_rgb(start_color), hex_to_rgb(end_color)
        for i in range(steps):
            t = i / max(steps - 1,1)
            r = int(r1 + (r2 - r1) * t); g = int(g1 + (g2 - g1) * t); b = int(b1 + (b2 - b1) * t)
            color = rgb_to_hex(r,g,b)
            y0 = int(i * (height / steps)); y1 = int((i + 1) * (height / steps))
            canvas.create_rectangle(0, y0, width, y1, outline="", fill=color)

    def heading_with_label_subheading(self):
        self.head_name = self.make_label(self.window, text="单链表的可视化",
                                         font=("Arial",35,"bold","italic"),
                                         bg="chocolate", fg="yellow")
        self.head_name.place(x=350,y=20)
        self.information = self.make_label(self.window,
            text="start是指向第一个节点的指针\ntemp指针在insert_last和delete_last的时候用于遍历找到目标位置",
            font=("Arial",20,"bold","italic"), bg="chocolate", fg="#00FF00")
        self.information.place(x=150,y=380)

    def make_start_with_other(self):
        self.start_pointer = self.make_rect(self.start_left,self.start_up,self.start_left+30,self.start_up+30,
                                           fill="blue", outline="black", width=3)
        self.start_label = self.make_label(self.canvas_make, text="start", font=("Arial",15,"bold"),
                                           bg="chocolate", fg="green")
        self.start_label.place(x=40,y=410)
        self.pointing_line_start = self.canvas_make.create_line(65,327,65,395,width=2,fill="green")
        self.start_initial_point_null = self.make_label(self.canvas_make, text="NULL",
                                                        font=("Arial",15,"bold"), bg="chocolate", fg="blue")
        self.start_initial_point_null.place(x=40, y=300)
        self.temp_label = self.make_label(self.canvas_make, text="temp", font=("Arial",15,"bold"), bg="chocolate", fg="green")
        self.temp1_label = self.make_label(self.canvas_make, text="temp1", font=("Arial",15,"bold"), bg="chocolate", fg="green")

    def make_btn(self):
        btns = [
            ("Insert first", lambda: self.make_node_with_label(1), 20,540),
            ("Insert last",  lambda: self.make_node_with_label(0), 220,540),
            ("Delete first", self.delete_first_node, 420,540),
            ("Delete last",  lambda: self.delete_last_node(0), 620,540),
            ("Insert after node", self.set_of_input_method, 830,540),
            ("Delete particular node", self.delete_single_node_infrastructure, 1090,540),
            ("返回主界面", self.back_to_main, 1090,600),
            ("保存链表", self.save_structure, 900,600),
            ("打开链表", self.load_structure, 900,650),
        ]
        for text, cmd, x, y in btns:
            btn = self.make_button(self.window, text=text, bg=("black" if text.startswith(("Insert","Delete")) else "blue"),
                                   fg="red" if text.startswith(("Insert","Delete")) else "white",
                                   font=("Arial", 15 if len(text)>6 else 12, "bold"),
                                   relief=RAISED, bd=10 if len(text)>6 else 6, command=cmd)
            btn.place(x=x, y=y)
            # attach to attr by cleaned name for later toggling
            attr = text.lower().split()[0] if " " in text else text.lower()
            # ensure names same as original where needed
            if text == "Insert first": self.insert_at_beg = btn
            if text == "Insert last": self.insert_at_last = btn
            if text == "Delete first": self.delete_at_first = btn
            if text == "Delete last": self.delete_at_last = btn
            if text == "Insert after node": self.insert_after_node = btn
            if text == "Delete particular node": self.delete_particular_node = btn
            if text == "返回主界面": self.back_to_main_btn = btn
            if text == "保存链表": self.save_btn = btn
            if text == "打开链表": self.load_btn = btn

    def make_batch_create_ui(self):
        Label(self.window, text="批量创建（以逗号分隔）", font=("Arial", 12, "bold"), bg="lightgray").place(x=20, y=610)
        Entry(self.window, font=("Arial", 12), bg="white", textvar=self.batch_entry_var, width=40).place(x=200, y=610)
        Button(self.window, text="Create List", font=("Arial", 10, "bold"), bg="green", fg="white",
               relief=RAISED, bd=3, command=self.create_list_from_string).place(x=620, y=607)

        Label(self.window, text="DSL 命令:", font=("Arial", 12, "bold"), bg="lightgray").place(x=20, y=650)
        dsl_entry = Entry(self.window, font=("Arial", 12), bg="white", textvar=self.dsl_var, width=40)
        dsl_entry.place(x=200, y=650); dsl_entry.bind("<Return>", lambda e: self.process_dsl())
        Button(self.window, text="执行 DSL", font=("Arial", 10, "bold"), bg="green", fg="white",
               command=self.process_dsl).place(x=620, y=647)

    # -------- DSL & storage --------
    def process_dsl(self, event=None):
        txt = self.dsl_var.get().strip()
        if not txt: return
        try:
            try:
                from DSL_utils import process_command
            except Exception:
                process_command = None

            if process_command is not None:
                process_command(self, txt)
            else:
                # fallback minimal commands
                if txt.startswith("create "):
                    parts = [p.strip() for p in txt[len("create "):].replace(",", " ").split() if p.strip()]
                    if parts:
                        self.clear_visualization()
                        for v in parts: self.programmatic_insert_last(v)
                elif txt == "clear":
                    self.clear_visualization()
                elif txt.startswith("insert "):
                    v = txt[len("insert "):].strip()
                    if v: self.programmatic_insert_last(v)
                elif txt.startswith("delete "):
                    messagebox.showinfo("提示", "已收到 delete 请求，请安装 DSL_utils 获取更完整行为")
                else:
                    messagebox.showinfo("未识别命令", "支持 insert/delete/clear/create 等 (推荐安装 DSL_utils)")
        finally:
            try: self.dsl_var.set("")
            except: pass

    def save_structure(self):
        node_values = self.node_value_store
        if not node_values:
            messagebox.showinfo("提示", "链表为空，无需保存")
            return
        success = storage.save_linked_list_to_file(node_values)
        if success:
            messagebox.showinfo("成功", "链表结构已保存")
        else:
            messagebox.showerror("错误", "保存失败")

    # -------- clear / load --------
    def clear_visualization(self):
        try:
            # clear data_next_store
            for entry in self.linked_list_data_next_store:
                try: entry[0].place_forget()
                except: pass
                try: self.canvas_make.delete(entry[1])
                except: pass
                try: entry[2].place_forget()
                except: pass
            self.linked_list_data_next_store.clear()

            # clear widget rectangles
            for widgets in self.linked_list_canvas_small_widget:
                for wid in widgets:
                    try: self.canvas_make.delete(wid)
                    except: 
                        try: wid.place_forget()
                        except: pass
            self.linked_list_canvas_small_widget.clear()

            # clear small labels
            for labels in self.linked_list_canvas_small_widget_label:
                for lab in labels:
                    try: lab.place_forget()
                    except: pass
            self.linked_list_canvas_small_widget_label.clear()

            self.linked_list_position.clear()
            self.node_value_store.clear()
            try: self.model.node_value_store.clear()
            except: pass

            try: self.start_initial_point_null.place(x=40, y=300)
            except: pass

            self.reset_coords()
            self.information.config(text="已清空当前可视化")
            self.window.update()
        except Exception as e:
            print("clear_visualization error:", e)

    def reset_coords(self):
        # reset many coordinates to initial defaults
        self._init_coords()
        self.node_helpers_reset()

    def load_structure(self):
        loaded = storage.load_linked_list_from_file()
        if loaded is None: return
        if not isinstance(loaded, list) or len(loaded) == 0:
            messagebox.showerror("错误", "未从文件中读取到有效链表数据"); return
        self.clear_visualization()
        self.toggle_action_buttons(DISABLED)
        try:
            for val in loaded:
                self.programmatic_insert_last(val)
                self.window.update()
        except Exception as e:
            print("load_structure error during insert:", e)
            messagebox.showerror("错误", f"加载时出错：{e}")
        self.toggle_action_buttons(NORMAL)
        self.information.config(text="加载完成")
        messagebox.showinfo("成功", "链表已从文件加载并重建可视化")

    # -------- node creation & input --------
    def set_of_input_method(self):
        self.information.config(text="First node position: 1")
        self.position_label = Label(self.window, text="Enter the node position after you want to insert new node",
                                    font=("Arial",13,"bold"), bg="orange", fg="brown")
        self.position_label.place(x=750, y=620)
        self.position_take_entry = Entry(self.window, font=("Arial", 13, "bold"), bg="white", state=NORMAL,
                                         fg="blue", relief=SUNKEN, bd=5, textvar=self.position_entry)
        self.position_take_entry.place(x=810, y=650); self.position_take_entry.focus()
        self.find_btn = Button(self.window, text="Find", font=("Arial", 10, "bold"), bg="blue", fg="red",
                               relief=RAISED, bd=3, padx=3, pady=3, state=NORMAL,
                               command=self.checking_of_existence)
        self.find_btn.place(x=1020, y=650)

    def checking_of_existence(self):
        try:
            self.position_label.place_forget(); self.position_take_entry.place_forget(); self.find_btn.place_forget()
            pos = int(self.position_entry.get())
            if pos < 1 or pos > len(self.node_value_store):
                messagebox.showerror("Not found","The target node is not found")
                self.information.config(text="start is a pointer that pointing the first node and temp pointer is used at the time of \ninsert last and delete last to reach to the targeting location")
            else:
                self.insert_after_node.config(state=DISABLED)
                self.information.config(text="Targeting node found")
                self.make_node_with_label(2)
        except Exception as e:
            messagebox.showerror("Error", f"位置检查出错: {e}")

    def make_node_with_label(self, take_notation):
        self.toggle_action_buttons(DISABLED)
        self.new_node_label = Label(self.canvas_make, text="New node", font=("Arial",13,"bold"), bg="chocolate", fg="green")
        self.new_node_label.place(x=30, y=90)
        # rectangles for data/next and outer node
        self.data = self.make_rect(self.data_left,self.data_up,self.data_left+40,self.data_up+30, outline="green", fill="yellow", width=3)
        self.data_label = Label(self.canvas_make, text="data", font=("Arial",13,"bold"), bg="chocolate", fg="green")
        self.data_label.place(x=self.data_label_x, y=self.data_label_y)
        self.next = self.make_rect(self.data_left+50,self.data_up,self.data_left+90,self.data_up+30, outline="green", fill="yellow", width=3)
        self.next_label = Label(self.canvas_make, text="next", font=("Arial",13,"bold"), bg="chocolate", fg="green")
        self.next_label.place(x=self.data_label_x+50, y=self.data_label_y)
        self.main_container_node = self.make_rect(self.main_node_left, self.main_node_up, self.main_node_left+100, self.main_node_up+65, outline="brown", width=3)
        self.input_take(take_notation)

    def input_take(self, take_notation):
        # create shared entry & add button
        self.element_take_label = Label(self.window, text="Enter the element value", bg="orange", fg="brown", font=("Arial", 12, "bold"))
        self.element_take_label.place(x=10, y=620)
        self.element_take_entry = Entry(self.window, font=("Arial", 13, "bold"), bg="white", state=NORMAL,
                                        fg="blue", relief=SUNKEN, bd=5, textvar=self.value_entry)
        self.element_take_entry.place(x=10, y=650); self.element_take_entry.focus()
        self.add_btn = Button(self.window, text="Add", font=("Arial", 10, "bold"), bg="blue", fg="red",
                              relief=RAISED, bd=3, padx=3, pady=3, command=lambda: self.make_main_container_with_node_value_set_and_next_arrow_creation(take_notation))
        self.add_btn.place(x=220, y=650)

        if take_notation == 2:
            self.element_take_label.config(text="Enter the new node value"); self.element_take_label.place(x=810, y=620)
            self.element_take_entry.place(x=810, y=650); self.add_btn.place(x=1020, y=650)
        elif take_notation == 3:
            self.element_take_label.config(text="Enter the node position"); self.element_take_label.place(x=1100, y=620)
            self.element_take_entry.place(x=1100, y=650); self.add_btn.place(x=1300, y=650)

    def make_main_container_with_node_value_set_and_next_arrow_creation(self, take_notation):
        self.add_btn.config(state=DISABLED)
        self.value_set = Label(self.canvas_make, text=self.value_entry.get(), font=("Arial", 10, "bold"), fg="green", bg="yellow")
        self.value_set.place(x=self.data_left + 8, y=self.data_up + 3)
        self.arrow = self.canvas_make.create_line(self.data_left+75, self.data_up+15, self.data_left+115, self.data_up+15, width=4)
        self.next_set = Label(self.canvas_make, text="NULL", font=("Arial", 15, "bold"), fg="green", bg="chocolate")
        self.next_set.place(x=self.data_left+102, y=self.data_up + 3)
        self.insert_node(take_notation)

    # -------- core insertion flow (保留原逻辑，但重用函数) --------
    def insert_node(self, take_notation):
        try:
            self.information.config(text=" ")
            self.new_node_label.place_forget()
            try: self.start_initial_point_null.place_forget()
            except: pass

            # vertical drop animation (shared of original)
            while self.main_node_up + 65 < 320:
                # delete/recreate to simulate movement
                self.canvas_make.delete(self.main_container_node, self.data, self.next, self.arrow)
                self.next_label.place_forget(); self.data_label.place_forget()
                self.value_set.place_forget(); self.next_set.place_forget()

                self.main_node_up += 10; self.data_up += 10; self.data_label_y += 10
                self.main_container_node = self.make_rect(self.main_node_left, self.main_node_up, self.main_node_left+100, self.main_node_up+65, outline="brown", width=3)
                self.data = self.make_rect(self.data_left, self.data_up, self.data_left+40, self.data_up+30, outline="green", fill="yellow", width=3)
                self.next = self.make_rect(self.data_left+50, self.data_up, self.data_left+90, self.data_up+30, outline="green", fill="yellow", width=3)
                self.next_label.place(x=self.data_label_x+50, y=self.data_label_y); self.data_label.place(x=self.data_label_x, y=self.data_label_y)
                self.value_set.place(x=self.data_left + 8, y=self.data_up + 3)
                self.arrow = self.canvas_make.create_line(self.data_left+75, self.data_up+15, self.data_left+115, self.data_up+15, width=4)
                self.next_set.place(x=self.data_left+102, y=self.data_up + 2)

                time.sleep(0.04); self.window.update()

            # traversal temp pointer if needed (insert_last or insert_after)
            if len(self.linked_list_data_next_store) > 1 and (take_notation == 0 or take_notation == 2):
                self.next_set.place_forget()
                self.temp_label.place(x=self.temp_label_x, y=self.temp_label_y)
                self.pointing_line_temp = self.canvas_make.create_line(self.pointing_line_temp_left, self.pointing_line_temp_up,
                                                                       self.pointing_line_temp_left, self.pointing_line_temp_up + 65, width=2)
                goto = (int(self.position_entry.get()) - 2) if take_notation == 2 else (len(self.linked_list_position) - 2)
                while self.temp_label_x < self.linked_list_position[goto][4] + 120:
                    if take_notation == 2:
                        if int(self.position_entry.get()) == 1: break
                        self.information.config(text="Traversing until found the targeting node")
                    else:
                        self.information.config(text="Traversing until found the last node")
                    self.temp_label.place_forget()
                    self.canvas_make.delete(self.pointing_line_temp, self.temp_pointer)
                    self.temp_label_x += 10; self.pointing_line_temp_left += 10; self.temp_pointer_left += 10
                    self.temp_pointer = self.make_rect(self.temp_pointer_left, self.temp_pointer_up, self.temp_pointer_left + 30, self.temp_pointer_up + 30, fill="blue", outline="black", width=3)
                    self.temp_label.place(x=self.temp_label_x, y=self.temp_label_y)
                    self.pointing_line_temp = self.canvas_make.create_line(self.pointing_line_temp_left, self.pointing_line_temp_up, self.pointing_line_temp_left, self.pointing_line_temp_up + 65, width=2)
                    time.sleep(0.05); self.window.update()

            # horizontal approach to append position
            if len(self.linked_list_data_next_store) > 0:
                # remove last NULL of previous tail
                try:
                    self.linked_list_data_next_store[-1].pop().place_forget()
                except: pass
                while self.main_node_left < self.linked_list_position[-1][4] + 120:
                    self.canvas_make.delete(self.main_container_node, self.data, self.next, self.arrow)
                    self.next_label.place_forget(); self.data_label.place_forget()
                    self.value_set.place_forget(); self.next_set.place_forget()
                    self.main_node_left += 10; self.data_left += 10; self.data_label_x += 10
                    self.main_container_node = self.make_rect(self.main_node_left, self.main_node_up, self.main_node_left+100, self.main_node_up+65, outline="brown", width=3)
                    self.data = self.make_rect(self.data_left, self.data_up, self.data_left+40, self.data_up+30, outline="green", fill="yellow", width=3)
                    self.next = self.make_rect(self.data_left+50, self.data_up, self.data_left+90, self.data_up+30, outline="green", fill="yellow", width=3)
                    self.next_label.place(x=self.data_label_x+50, y=self.data_label_y); self.data_label.place(x=self.data_label_x, y=self.data_label_y)
                    self.value_set.place(x=self.data_left + 8, y=self.data_up + 3)
                    self.arrow = self.canvas_make.create_line(self.data_left+75, self.data_up+15, self.data_left+115, self.data_up+15, width=4)
                    self.next_set.place(x=self.data_left+102, y=self.data_up + 2)
                    if take_notation == 0:
                        self.information.config(text="New node added to the last node")
                    elif take_notation == 2:
                        self.information.config(text="New node added after the targeting node")
                    time.sleep(0.04); self.window.update()

            # store widgets & positions (same structure as旧版)
            self.linked_list_canvas_small_widget_label.append([self.data_label, self.next_label])
            self.linked_list_canvas_small_widget.append([self.data, self.next, self.main_container_node])
            loc = [self.data_left, self.data_up, self.data_left+50, self.data_up, self.main_node_left, self.main_node_up]
            self.linked_list_position.append(loc)

            # cleanup temp pointer
            try:
                self.temp_label.place_forget()
                self.canvas_make.delete(self.pointing_line_temp, self.temp_pointer)
            except: pass
            self.temp_label_x = 40; self.pointing_line_temp_left = 65; self.temp_pointer_left = 50

            # record to model store & reset UI bits
            if take_notation == 0 or take_notation == 1 or take_notation == 2:
                # reuse reset_with_store semantics
                self.reset_with_store(take_notation)
        except Exception as e:
            print("insert_node error:", e)

    # -------- programmatic insert (批量时复用) --------
    def programmatic_insert_last(self, value):
        # 复用 make_main_container... + insert_node 的流程，但直接使用给定 value
        try:
            self.new_node_label = Label(self.canvas_make, text="New node", font=("Arial", 13, "bold"), bg="chocolate", fg="green")
            self.new_node_label.place(x=30, y=90)
            self.data = self.make_rect(self.data_left, self.data_up, self.data_left+40, self.data_up+30, outline="green", fill="yellow", width=3)
            self.data_label = Label(self.canvas_make, text="data", font=("Arial", 13, "bold"), bg="chocolate", fg="green")
            self.data_label.place(x=self.data_label_x, y=self.data_label_y)
            self.next = self.make_rect(self.data_left+50, self.data_up, self.data_left+90, self.data_up+30, outline="green", fill="yellow", width=3)
            self.next_label = Label(self.canvas_make, text="next", font=("Arial", 13, "bold"), bg="chocolate", fg="green")
            self.next_label.place(x=self.data_label_x+50, y=self.data_label_y)
            self.main_container_node = self.make_rect(self.main_node_left, self.main_node_up, self.main_node_left + 100, self.main_node_up + 65, outline="brown", width=3)
            self.value_set = Label(self.canvas_make, text=str(value), font=("Arial", 10, "bold"), fg="green", bg="yellow")
            self.value_set.place(x=self.data_left + 8, y=self.data_up + 3)
            self.arrow = self.canvas_make.create_line(self.data_left+75, self.data_up + 15, self.data_left+115, self.data_up + 15, width=4)
            self.next_set = Label(self.canvas_make, text="NULL", font=("Arial", 15, "bold"), fg="green", bg="chocolate")
            self.next_set.place(x=self.data_left+102, y=self.data_up + 3)

            # 垂直动画
            self.start_initial_point_null.place_forget()
            while self.main_node_up + 65 < 320:
                self.canvas_make.delete(self.main_container_node, self.data, self.next, self.arrow)
                self.next_label.place_forget(); self.data_label.place_forget()
                self.value_set.place_forget(); self.next_set.place_forget()
                self.main_node_up += 10; self.data_up += 10; self.data_label_y += 10
                self.main_container_node = self.make_rect(self.main_node_left, self.main_node_up, self.main_node_left+100, self.main_node_up+65, outline="brown", width=3)
                self.data = self.make_rect(self.data_left, self.data_up, self.data_left+40, self.data_up+30, outline="green", fill="yellow", width=3)
                self.next = self.make_rect(self.data_left+50, self.data_up, self.data_left+90, self.data_up+30, outline="green", fill="yellow", width=3)
                self.next_label.place(x=self.data_label_x+50, y=self.data_label_y); self.data_label.place(x=self.data_label_x, y=self.data_label_y)
                self.value_set.place(x=self.data_left + 8, y=self.data_up + 3)
                self.arrow = self.canvas_make.create_line(self.data_left+75, self.data_up + 15, self.data_left+115, self.data_up + 15, width=4)
                self.next_set.place(x=self.data_left+102, y=self.data_up + 2)
                time.sleep(0.04); self.window.update()

            # temp traverse if needed
            if len(self.linked_list_data_next_store) > 1:
                self.next_set.place_forget()
                self.temp_label.place(x=self.temp_label_x, y=self.temp_label_y)
                self.pointing_line_temp = self.canvas_make.create_line(self.pointing_line_temp_left, self.pointing_line_temp_up, self.pointing_line_temp_left, self.pointing_line_temp_up + 65, width=2)
                goto = len(self.linked_list_position) - 2
                while self.temp_label_x < self.linked_list_position[goto][4] + 120:
                    self.temp_label.place_forget()
                    self.canvas_make.delete(self.pointing_line_temp, self.temp_pointer)
                    self.temp_label_x += 10; self.pointing_line_temp_left += 10; self.temp_pointer_left += 10
                    self.temp_pointer = self.make_rect(self.temp_pointer_left, self.temp_pointer_up, self.temp_pointer_left + 30, self.temp_pointer_up + 30, fill="blue", outline="black", width=3)
                    self.temp_label.place(x=self.temp_label_x, y=self.temp_label_y)
                    self.pointing_line_temp = self.canvas_make.create_line(self.pointing_line_temp_left, self.pointing_line_temp_up, self.pointing_line_temp_left, self.pointing_line_temp_up + 65, width=2)
                    time.sleep(0.05); self.window.update()

            # horizontal approach & store (same as insert_node)
            if len(self.linked_list_data_next_store) > 0:
                try: self.linked_list_data_next_store[-1].pop().place_forget()
                except: pass
                while self.main_node_left < self.linked_list_position[-1][4] + 120:
                    self.canvas_make.delete(self.main_container_node, self.data, self.next, self.arrow)
                    self.next_label.place_forget(); self.data_label.place_forget()
                    self.value_set.place_forget(); self.next_set.place_forget()
                    self.main_node_left += 10; self.data_left += 10; self.data_label_x += 10
                    self.main_container_node = self.make_rect(self.main_node_left, self.main_node_up, self.main_node_left+100, self.main_node_up+65, outline="brown", width=3)
                    self.data = self.make_rect(self.data_left, self.data_up, self.data_left+40, self.data_up+30, outline="green", fill="yellow", width=3)
                    self.next = self.make_rect(self.data_left+50, self.data_up, self.data_left+90, self.data_up+30, outline="green", fill="yellow", width=3)
                    self.next_label.place(x=self.data_label_x+50, y=self.data_label_y); self.data_label.place(x=self.data_label_x, y=self.data_label_y)
                    self.value_set.place(x=self.data_left + 8, y=self.data_up + 3)
                    self.arrow = self.canvas_make.create_line(self.data_left+75, self.data_up+15, self.data_left+115, self.data_up+15, width=4)
                    self.next_set.place(x=self.data_left+102, y=self.data_up + 2)
                    self.information.config(text="New node added to the last node")
                    time.sleep(0.04); self.window.update()

            # store to internal lists
            self.linked_list_canvas_small_widget_label.append([self.data_label, self.next_label])
            self.linked_list_canvas_small_widget.append([self.data, self.next, self.main_container_node])
            loc = [self.data_left, self.data_up, self.data_left+50, self.data_up, self.main_node_left, self.main_node_up]
            self.linked_list_position.append(loc)

            try:
                self.temp_label.place_forget()
                self.canvas_make.delete(self.pointing_line_temp, self.temp_pointer)
            except: pass
            self.temp_label_x = 40; self.pointing_line_temp_left = 65; self.temp_pointer_left = 50

            self.node_value_store.append(str(value))
            self.linked_list_data_next_store.append([self.value_set, self.arrow, self.next_set])

            # reset positions for next insert
            self.reset_coords()
            if len(self.linked_list_data_next_store) == 1:
                try: self.start_initial_point_null.place_forget()
                except: pass

        except Exception as e:
            print("programmatic_insert_last error:", e)

    # -------- store reset & value shifting --------
    def reset_with_store(self, take_notation):
        # 保存输入值
        self.node_value_store.append(self.value_entry.get())
        self.linked_list_data_next_store.append([self.value_set, self.arrow, self.next_set])
        # debug prints (保留)
        print(self.linked_list_data_next_store); print(self.linked_list_canvas_small_widget)
        print(self.linked_list_position); print(self.linked_list_canvas_small_widget_label); print(self.node_value_store)

        # cleanup input widgets
        try: self.element_take_label.place_forget(); self.value_entry.set(" "); self.element_take_entry.place_forget(); self.add_btn.place_forget()
        except: pass

        # insert first value shifting（行为与原版一致）
        if take_notation == 1 and len(self.linked_list_data_next_store) > 1:
            temp_val = self.node_value_store[-1]
            for i in range(len(self.node_value_store)-2, -1, -1):
                self.node_value_store[i+1] = self.node_value_store[i]
            self.node_value_store[0] = temp_val
            for i in range(len(self.node_value_store)):
                self.linked_list_data_next_store[i][0].config(text=self.node_value_store[i])

        # insert after node shifting
        if take_notation == 2:
            temp_value = self.node_value_store[-1]
            pos = int(self.position_entry.get())
            for i in range(len(self.node_value_store)-2, pos-1, -1):
                self.node_value_store[i+1] = self.node_value_store[i]
            self.node_value_store[pos] = temp_value
            for i in range(pos, len(self.linked_list_data_next_store)):
                self.linked_list_data_next_store[i][0].config(text=self.node_value_store[i])

        # reset coords and buttons
        self.reset_coords()
        self.toggle_action_buttons(NORMAL)

    # -------- deletions (保留所有外部调用签名) --------
    def delete_last_node(self, locator):
        print(self.linked_list_data_next_store, self.linked_list_canvas_small_widget, self.linked_list_position, self.linked_list_canvas_small_widget_label, self.node_value_store)
        if len(self.linked_list_data_next_store) == 0:
            messagebox.showerror("Underflow", "Link list is empty"); return
        self.toggle_action_buttons(DISABLED)

        # temp traversal for penultimate
        if (locator == 0 or locator==3) and len(self.linked_list_data_next_store)>1:
            self.temp_pointer = self.make_rect(self.temp_pointer_left, self.temp_pointer_up, self.temp_pointer_left + 30, self.temp_pointer_up + 30, fill="blue", outline="black", width=3)
            self.temp_label.place(x=self.temp_label_x, y=self.temp_label_y)
            self.pointing_line_temp = self.canvas_make.create_line(self.pointing_line_temp_left, self.pointing_line_temp_up, self.pointing_line_temp_left, self.pointing_line_temp_up + 65, width=2)
            if len(self.linked_list_data_next_store) > 2:
                goto = (int(self.delete_entry.get())-3) if locator == 3 else (len(self.linked_list_position) - 3)
                while self.temp_label_x < self.linked_list_position[goto][4] + 120:
                    if locator == 3:
                        if int(self.delete_entry.get()) == 2: break
                        self.information.config(text="Traversing until found the penultimate node of the targeting node")
                    else:
                        self.information.config(text="Traversing until found the penultimate node of the last node")
                    self.temp_label.place_forget()
                    self.canvas_make.delete(self.pointing_line_temp, self.temp_pointer)
                    self.temp_label_x += 10; self.pointing_line_temp_left += 10; self.temp_pointer_left += 10
                    self.temp_pointer = self.make_rect(self.temp_pointer_left, self.temp_pointer_up, self.temp_pointer_left + 30, self.temp_pointer_up + 30, fill="blue", outline="black", width=3)
                    self.temp_label.place(x=self.temp_label_x, y=self.temp_label_y)
                    self.pointing_line_temp = self.canvas_make.create_line(self.pointing_line_temp_left, self.pointing_line_temp_up, self.pointing_line_temp_left, self.pointing_line_temp_up + 65, width=2)
                    time.sleep(0.04); self.window.update()

            # pause
            for _ in range(3): time.sleep(0.125); self.window.update()
            if locator == 0:
                self.information.config(text="Temp pointing node contains the address that present in the next part of last node and\nand Last node deleted")
            else:
                self.information.config(text="Targeting node deleted")

        if locator == 3:
            # temp1 creation and value shift for delete particular node
            self.temp1_pointer = self.make_rect(self.temp_pointer_left+120, self.temp_pointer_up, self.temp_pointer_left + 150, self.temp_pointer_up + 30, fill="blue", outline="black", width=3)
            self.temp1_label.place(x=self.temp_label_x+120, y=self.temp_label_y)
            self.pointing_line_temp1 = self.canvas_make.create_line(self.pointing_line_temp_left+120, self.pointing_line_temp_up, self.pointing_line_temp_left+120, self.pointing_line_temp_up + 65, width=2)
            self.information.config(text="Temp is pointing the penultimate node of the targeting node and \ntemp1 is pointing the targeting node")
            for _ in range(3): time.sleep(2.5); self.window.update()
            for i in range(int(self.delete_entry.get()), len(self.node_value_store)):
                self.linked_list_data_next_store[i-1][0].config(text=self.node_value_store[i])
            for i in range(int(self.delete_entry.get()), len(self.node_value_store)):
                self.node_value_store[i-1] = self.node_value_store[i]

        # pop physical widgets (always remove last node)
        if len(self.linked_list_data_next_store) > 0:
            temp1 = self.linked_list_data_next_store.pop()
            try: temp1[0].place_forget()
            except: pass
            try: self.canvas_make.delete(temp1[1])
            except: pass
            try: temp1[2].place_forget()
            except: pass

            temp2 = self.linked_list_canvas_small_widget.pop()
            for i in temp2: 
                try: self.canvas_make.delete(i)
                except: pass
            self.linked_list_position.pop()

            # set NULL on new last node
            if len(self.linked_list_data_next_store) > 0:
                temp3 = self.linked_list_position[-1]
                self.next_set = Label(self.canvas_make, text="NULL", font=("Arial", 15, "bold"), fg="green", bg="chocolate")
                self.next_set.place(x=temp3[2]+52, y=temp3[3])
                self.linked_list_data_next_store[-1].append(self.next_set)

            temp4 = self.linked_list_canvas_small_widget_label.pop()
            for widget_label in temp4:
                try: widget_label.place_forget()
                except: pass

            # pop value store
            try: self.node_value_store.pop()
            except: pass

            if len(self.linked_list_data_next_store) == 0:
               self.start_initial_point_null.place(x=40, y=300)

            if locator == 3:
                try:
                    self.temp1_label.place_forget()
                    self.canvas_make.delete(self.pointing_line_temp1, self.temp1_pointer)
                except: pass
                self.information.config(text="The next part of the temp is now containing the address that is present in the \nnext part of temp1 and temp1 pointing node is deleted")

            for _ in range(3): time.sleep(1); self.window.update()

            try:
                self.temp_label.place_forget()
                self.canvas_make.delete(self.pointing_line_temp,self.temp_pointer)
            except: pass
            self.temp_label_x = 40; self.pointing_line_temp_left = 65; self.temp_pointer_left = 50

            if len(self.node_value_store) == 0:
               self.information.config(text="List is empty and start pointing NULL")
            elif locator == 0:
                self.information.config(text="Last node deleted")
            elif locator == 3:
                self.information.config(text="Targeting node deleted")

            self.toggle_action_buttons(NORMAL)

    def delete_first_node(self):
        if len(self.linked_list_data_next_store) == 0:
            messagebox.showerror("Underflow","Link list is empty")
            return
        if len(self.node_value_store) == 1:
            self.delete_last_node(1)
            self.information.config(text="Now start pointer is containing NULL and first node deleted")
            return
        # shift left then delete last
        for i in range(1,len(self.node_value_store)): self.node_value_store[i-1] = self.node_value_store[i]
        self.delete_last_node(1)
        for i in range(len(self.linked_list_data_next_store)):
            self.linked_list_data_next_store[i][0].config(text=self.node_value_store[i])
        self.information.config(text="Now start pointer is containing the address that present in the next part of the first node\nand first node deleted")

    def delete_single_node_infrastructure(self):
        if len(self.node_value_store) == 0:
           self.information.config(text="Link list is empty  ::  Nothing to delete"); return
        self.information.config(text="First node position: 1")
        self.toggle_action_buttons(DISABLED)
        self.position_label = Label(self.window, text="Enter the node position you want to delete", font=("Arial", 13, "bold"), bg="orange", fg="brown")
        self.position_label.place(x=1000, y=620)
        self.position_take_entry = Entry(self.window, font=("Arial", 13, "bold"), bg="white", state=NORMAL, fg="blue", relief=SUNKEN, bd=5, textvar=self.delete_entry)
        self.position_take_entry.place(x=1020, y=650); self.position_take_entry.focus()
        self.find_btn = Button(self.window, text="Find", font=("Arial", 10, "bold"), bg="blue", fg="red", relief=RAISED, bd=3, padx=3, pady=3, state=NORMAL, command=self.delete_single_node)
        self.find_btn.place(x=1230, y=650)

    def delete_single_node(self):
        self.position_label.place_forget(); self.position_take_entry.place_forget(); self.find_btn.place_forget()
        pos = int(self.delete_entry.get())
        if pos > len(self.node_value_store) or pos < 1:
           messagebox.showerror("Error","Positional node not found")
        elif pos == 1:
           self.delete_first_node()
        else:
           self.delete_last_node(3)
        self.toggle_action_buttons(NORMAL)

    def create_list_from_string(self):
        txt = self.batch_entry_var.get()
        if not txt or not txt.strip():
            messagebox.showerror("Error", "请输入以逗号分隔的值，例如：1,2,3"); return
        parts = [p.strip() for p in txt.split(',') if p.strip() != ""]
        if not parts:
            messagebox.showerror("Error", "未解析到有效元素"); return
        self.toggle_action_buttons(DISABLED)
        for val in parts: self.programmatic_insert_last(val)
        self.toggle_action_buttons(NORMAL)
        self.information.config(text="批量创建完成")

    def back_to_main(self):
        self.window.destroy()

if __name__ == '__main__':
    window = Tk()
    window.title("Singly Linked List Visualizer")
    window.geometry("1350x730")
    window.maxsize(1350,730)
    window.minsize(1350,730)
    LinkList(window)
    window.mainloop()
