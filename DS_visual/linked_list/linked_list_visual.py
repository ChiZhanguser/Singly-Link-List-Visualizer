from tkinter import *
from tkinter import messagebox
import time
from linked_list.linked_list_model import LinkedListModel

class LinkList: # One and only class of that project
    def __init__(self,root):
        self.window = root
        # 保留窗口背景为浅色（可改），画布背景使用渐变绘制
        self.window.config(bg="#F5F7FA")

        # Canvas 尺寸（与原代码一致）
        self.canvas_width = 1350
        self.canvas_height = 500

        # 创建 Canvas（背景色设为与渐变最后一条相近，防止闪烁）
        self.canvas_make = Canvas(self.window, bg="#0575E6", width=self.canvas_width, height=self.canvas_height, relief=RAISED, bd=8)
        self.canvas_make.pack()

        # 绘制纵向渐变（从深蓝 -> 浅蓝）
        # 调整 start_color / end_color 可更换渐变色
        self.draw_gradient(self.canvas_make, self.canvas_width, self.canvas_height, start_color="#021B79", end_color="#89CFF0", steps=200)

        self.linked_list_canvas_small_widget = []
        self.linked_list_canvas_small_widget_label = []
        self.linked_list_position = []
        self.linked_list_data_next_store = []

        self.model = LinkedListModel()
        self.node_value_store = self.model.node_value_store
        self.value_entry = StringVar()
        self.position_entry = StringVar()
        self.delete_entry = StringVar()
        # 新增批量输入的 StringVar
        self.batch_entry_var = StringVar()

        self.value_entry.set(" ")
        self.position_entry.set(" ")
        self.delete_entry.set(" ")
        self.batch_entry_var.set(" ")

        self.head_name = None
        self.information = None
        self.insert_at_beg = None
        self.insert_at_last = None
        self.delete_at_first = None
        self.delete_at_last = None
        self.position_label = None
        self.start_label = None
        self.temp_label = None
        self.temp1_label = None
        self.data_label = None
        self.next_label = None
        self.element_take_label = None
        self.element_take_entry = None
        self.add_btn = None
        self.value_set = None
        self.next_set = None
        self.start_initial_point_null = None
        self.new_node_label = None
        self.position_take_entry = None
        self.find_btn = None
        self.insert_after_node = None
        self.delete_particular_node = None

        self.start_pointer = 0
        self.pointing_line_start = 0
        self.pointing_line_temp = 0
        self.pointing_line_temp1 = 0
        self.temp_pointer = 0
        self.temp1_pointer = 0
        self.data = 0
        self.next = 0
        self.main_container_node = 0
        self.arrow = 0

        self.pointing_line_temp_left = 65
        self.pointing_line_temp_up = 195

        self.temp_label_x = 40
        self.temp_label_y = 150

        self.temp_pointer_left = 50
        self.temp_pointer_up = 180

        self.value_set_x = 40
        self.value_set_y = 160

        self.start_left = 50
        self.start_up = 380

        #data widget coordinate initialization
        self.data_left = 30
        self.data_up = 150

        # main node widget coordinate initialization
        self.main_node_left=25
        self.main_node_up = 120

        #node value containing label coordinate initialization
        self.data_label_x = 30
        self.data_label_y = 122

        # Initially required Function call
        self.heading_with_label_subheading()
        self.make_btn()
        self.make_start_with_other()
        # 新增：批量创建 UI
        self.make_batch_create_ui()


    def draw_gradient(self, canvas, width, height, start_color="#000000", end_color="#FFFFFF", steps=100):
        """
        在给定 canvas 上绘制纵向渐变。
        - start_color / end_color: hex 字符串，例如 "#021B79"
        - steps: 梯度分段数（越大越平滑，但绘制越慢）
        """
        def hex_to_rgb(h):
            h = h.lstrip('#')
            return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
        def rgb_to_hex(r, g, b):
            return f'#{r:02x}{g:02x}{b:02x}'

        (r1, g1, b1) = hex_to_rgb(start_color)
        (r2, g2, b2) = hex_to_rgb(end_color)

        # 用若干条矩形条带模拟渐变（纵向）
        for i in range(steps):
            t = i / max(steps - 1, 1)
            r = int(r1 + (r2 - r1) * t)
            g = int(g1 + (g2 - g1) * t)
            b = int(b1 + (b2 - b1) * t)
            color = rgb_to_hex(r, g, b)
            y0 = int(i * (height / steps))
            y1 = int((i + 1) * (height / steps))
            # outline 为空以避免细线
            canvas.create_rectangle(0, y0, width, y1, outline="", fill=color)

    # Heading and status/information initialization process
    def heading_with_label_subheading(self):
        self.head_name = Label(self.window,text="单链表的可视化",font=("Arial",35,"bold","italic"),
                               bg="chocolate",fg="yellow")
        self.head_name.place(x=350,y=20)

        self.information =  Label(self.window,text="start是指向第一个节点的指针\ntemp指针在insert_last和delete_last的时候用于遍历找到目标位置",font=("Arial",20,"bold","italic"),
                               bg="chocolate",fg="#00FF00")
        self.information.place(x=150,y=380)

    # start and other pointer initialization
    def make_start_with_other(self):
        #making of start pointer block
        self.start_pointer = self.canvas_make.create_rectangle(self.start_left,self.start_up,self.start_left+30,self.start_up+30,fill="blue",outline="black",width=3)

        #making of start label
        self.start_label = Label(self.canvas_make,text="start",font=("Arial",15,"bold"),bg="chocolate",
                                 fg="green")
        self.start_label.place(x=40,y=410)

        #making of start pointing line
        self.pointing_line_start = self.canvas_make.create_line(65,327,65,395,width=2,fill="green")

        #Making of NULL which is primarily pointing by start
        self.start_initial_point_null = Label(self.canvas_make, text="NULL", font=("Arial", 15, "bold"), bg="chocolate",
                                 fg="blue")
        self.start_initial_point_null.place(x=40, y=300)

        #Making of temp label without set coordinate(coordinate set in other function)
        self.temp_label = Label(self.canvas_make,text="temp",font=("Arial",15,"bold"),bg="chocolate",
                                 fg="green")

        self.temp1_label = Label(self.canvas_make, text="temp1", font=("Arial", 15, "bold"), bg="chocolate",
                                fg="green")

    def back_to_main(self):
    # 返回主界面
        self.window.destroy()
        from main_interface import MainInterface
        main_window = Tk()
        app = MainInterface(main_window)
        main_window.mainloop()

    # Make some buttons to give instruction to program
    def make_btn(self):
        self.insert_at_beg = Button(self.window,text="Insert first",bg="black",fg="red",
                                    font=("Arial",15,"bold"),relief=RAISED,bd=10,command=lambda: self.make_node_with_label(1))
        self.insert_at_beg.place(x=20,y=540)

        self.insert_at_last = Button(self.window, text="Insert last", bg="black", fg="red",
                                    font=("Arial", 15, "bold"), relief=RAISED, bd=10
                                     ,command=lambda: self.make_node_with_label(0))
        self.insert_at_last.place(x=220, y=540)


        self.delete_at_first = Button(self.window, text="Delete first", bg="black", fg="red",
                                     font=("Arial", 15, "bold"), relief=RAISED, bd=10,
                                      command=self.delete_first_node)
        self.delete_at_first.place(x=420, y=540)

        self.delete_at_last = Button(self.window, text="Delete last", bg="black", fg="red",
                                      font=("Arial", 15, "bold"), relief=RAISED, bd=10,
                                     command=lambda: self.delete_last_node(0))
        self.delete_at_last.place(x=620, y=540)

        self.insert_after_node = Button(self.window, text="Insert after node", bg="black", fg="red",
                                     font=("Arial", 15, "bold"), relief=RAISED, bd=10,state=NORMAL,
                                     command=self.set_of_input_method)
        self.insert_after_node.place(x=830, y=540)

        self.delete_particular_node = Button(self.window, text="Delete particular node", bg="black", fg="red",
                                        font=("Arial", 15, "bold"), relief=RAISED, bd=10, state=NORMAL,
                                        command=self.delete_single_node_infrastructure)
        self.delete_particular_node.place(x=1090, y=540)

        self.back_to_main_btn = Button(self.window, text="返回主界面", bg="blue", fg="white",
                              font=("Arial", 15, "bold"), relief=RAISED, bd=10,
                              command=self.back_to_main)
        self.back_to_main_btn.place(x=1090, y=600)

    # 新增：批量创建的 UI（输入 CSV 并创建）
    def make_batch_create_ui(self):
        label = Label(self.window, text="批量创建（以逗号分隔）", font=("Arial", 12, "bold"), bg="lightgray")
        label.place(x=20, y=610)
        entry = Entry(self.window, font=("Arial", 12), bg="white", textvar=self.batch_entry_var, width=40)
        entry.place(x=200, y=610)
        create_btn = Button(self.window, text="Create List", font=("Arial", 10, "bold"),
                            bg="green", fg="white", relief=RAISED, bd=3,
                            command=self.create_list_from_string)
        create_btn.place(x=620, y=607)

    #Making of structure to take input about position
    def set_of_input_method(self):
        self.information.config(text="First node position: 1")

        self.position_label = Label(self.window,text="Enter the node position after you want to insert new node",font=("Arial",13,"bold"),bg="orange",
                                 fg="brown")
        self.position_label.place(x=750, y=620)

        self.position_take_entry = Entry(self.window, font=("Arial", 13, "bold"), bg="white", state=NORMAL,
                                         fg="blue", relief=SUNKEN, bd=5, textvar=self.position_entry)
        self.position_take_entry.place(x=810, y=650)

        self.position_take_entry.focus()

        self.find_btn = Button(self.window, text="Find", font=("Arial", 10, "bold"),
                               bg="blue", fg="red", relief=RAISED, bd=3, padx=3, pady=3,
                               state=NORMAL,command=self.checking_of_existence)
        self.find_btn.place(x=1020, y=650)

    # Positional node existence checking
    def checking_of_existence(self):
        self.position_label.place_forget()
        self.position_take_entry.place_forget()
        self.find_btn.place_forget()
        if int(self.position_entry.get())<1  or  int(self.position_entry.get()) > len(self.node_value_store):
            messagebox.showerror("Not found","The target node is not found")
            self.information.config(text="start is a pointer that pointing the first node and temp pointer is used at the time of \ninsert last and delete last to reach to the targeting location")
        else:
            self.insert_after_node.config(state=DISABLED)
            self.information.config(text="Targeting node found")
            self.make_node_with_label(2)

    # Node making process
    def make_node_with_label(self,take_notation):
        # Button deactivation
        self.insert_at_last.config(state=DISABLED)
        self.insert_at_beg.config(state=DISABLED)
        self.delete_at_last.config(state=DISABLED)
        self.delete_at_first.config(state=DISABLED)
        self.insert_after_node.config(state=DISABLED)
        self.delete_particular_node.config(state=DISABLED)

        #New_node label make
        self.new_node_label = Label(self.canvas_make,text="New node",font=("Arial",13,"bold"),bg="chocolate",
                                 fg="green")
        self.new_node_label.place(x=30, y=90)

        #Data widget making
        self.data = self.canvas_make.create_rectangle(self.data_left,self.data_up,self.data_left+40,self.data_up+30,outline="green",fill="yellow",width=3)

        # Data widget corresponding label making
        self.data_label = Label(self.canvas_make,text="data",font=("Arial",13,"bold"),bg="chocolate",
                                 fg="green")
        self.data_label.place(x=self.data_label_x, y=self.data_label_y)

        # Next widget making
        self.next = self.canvas_make.create_rectangle(self.data_left+50,self.data_up,self.data_left+50+40,self.data_up+30,outline="green",fill="yellow",width=3)

        # Next widget corresponding label making
        self.next_label = Label(self.canvas_make, text="next", font=("Arial", 13, "bold"), bg="chocolate",
                                fg="green")
        self.next_label.place(x=self.data_label_x+50, y=self.data_label_y)

        #Making of real node widget(outline border)
        self.main_container_node = self.canvas_make.create_rectangle(self.main_node_left, self.main_node_up,
                                                                     self.main_node_left + 100, self.main_node_up + 65,
                                                                     outline="brown", width=3)
        self.input_take(take_notation)

    # input taking process
    def input_take(self,take_notation):

        self.element_take_label = Label(self.window, text="Enter the element value",
                                        bg="orange", fg="brown", font=("Arial", 12, "bold"))
        self.element_take_label.place(x=10, y=620)

        self.element_take_entry = Entry(self.window, font=("Arial", 13, "bold"), bg="white", state=NORMAL,
                                        fg="blue", relief=SUNKEN, bd=5, textvar=self.value_entry)
        self.element_take_entry.place(x=10, y=650)

        # Default entry value set in __init__()

        self.element_take_entry.focus() #To focus in the entry box on activation

        self.add_btn = Button(self.window, text="Add", font=("Arial", 10, "bold"),
                              bg="blue", fg="red", relief=RAISED, bd=3, padx=3, pady=3,
                              command=lambda: self.make_main_container_with_node_value_set_and_next_arrow_creation(take_notation))
        self.add_btn.place(x=220, y=650)

        if take_notation==2: # For insert_after_node process
            self.element_take_label.config(text="Enter the new node value")
            self.element_take_label.place(x=810, y=620)
            self.element_take_entry.place(x=810, y=650)
            self.add_btn.place(x=1020, y=650)

        elif take_notation==3: # For delete_particular_node process
            self.element_take_label.config(text="Enter the node position")
            self.element_take_label.place(x=1100, y=620)
            self.element_take_entry.place(x=1100, y=650)
            self.add_btn.place(x=1300, y=650)

    # Working same as function name
    def make_main_container_with_node_value_set_and_next_arrow_creation(self,take_notation):
        #Deactivate the add btn
        self.add_btn.config(state=DISABLED)

        #Node value set
        self.value_set = Label(self.canvas_make, text=self.value_entry.get(),
                               font=("Arial", 10, "bold"), fg="green", bg="yellow")
        self.value_set.place(x=self.data_left + 8, y=self.data_up + 3)

        # Node next arrow set
        self.arrow = self.canvas_make.create_line(self.data_left+50 + 25, self.data_up + 15, self.data_left+50 + 65, self.data_up + 15, width=4)

        # Node next set
        self.next_set = Label(self.canvas_make, text="NULL", font=("Arial", 15, "bold"),
                              fg="green", bg="chocolate")
        self.next_set.place(x=self.data_left+50 + 52, y=self.data_up + 3)

        self.insert_node(take_notation)

        # take notation=0 means go to insert_at_last perform.
        # take notation=1 means go to insert_at_first perform.
        # take notation=2 means go to insert_after_node perform.
        # take notation=3 means go to delete_particular_node perform

    #Make insert first and insert last within that function
    def insert_node(self,take_notation):
        try:
            self.information.config(text=" ")
            self.new_node_label.place_forget()  # 'new node' label release
            self.start_initial_point_null.place_forget() # start pointing NULL release
            while True: # For vertical motion in three cases: insert_first, insert_last and insert_after_node
                   if take_notation == 1: #For insert first process
                      self.information.config(text="First node insertion process")
                   if self.main_node_up+65 <320: #For all function that allowed in that function
                       self.canvas_make.delete(self.main_container_node,self.data,self.next,self.arrow)
                       self.next_label.place_forget(); self.data_label.place_forget()
                       self.value_set.place_forget()
                       self.next_set.place_forget()
                       self.main_node_up +=10
                       self.data_up +=10
                       self.data_label_y +=10
                       self.main_container_node = self.canvas_make.create_rectangle(self.main_node_left, self.main_node_up, self.main_node_left+100,self.main_node_up+65, outline="brown",width=3)
                       self.data = self.canvas_make.create_rectangle(self.data_left, self.data_up, self.data_left+40, self.data_up+30, outline="green", fill="yellow", width=3)
                       self.next = self.canvas_make.create_rectangle(self.data_left+50, self.data_up, self.data_left+50+ 40, self.data_up+30, outline="green", fill="yellow", width=3)
                       self.next_label.place(x=self.data_label_x+50, y=self.data_label_y)
                       self.data_label.place(x=self.data_label_x, y=self.data_label_y)
                       self.value_set.place(x=self.data_left + 8, y=self.data_up + 3)
                       self.arrow = self.canvas_make.create_line(self.data_left+50 + 25, self.data_up + 15, self.data_left+50 + 65, self.data_up + 15, width=4)
                       self.next_set.place(x=self.data_left+50 + 52, y=self.data_up + 2)

                   else:
                       break

                   #time to sleep or slow motion
                   time.sleep(0.04)
                   self.window.update()

            if take_notation == 1:  #For insert first
                if len(self.node_value_store) >0:
                   self.information.config(text="Next part of New node contain the address of start pointing node and \nnow start pointing new node")
                else:
                    self.information.config(text="start pointing New node and next part of new node contains NULL")

            # Moving temp for insert last process
            if len(self.linked_list_data_next_store) > 1 and (take_notation==0 or take_notation==2):
                self.next_set.place_forget() #node next label place_forget()
                self.temp_label.place(x=self.temp_label_x, y=self.temp_label_y) #temp pointer start from first node

                #Making of start pointer pointing line
                self.pointing_line_temp = self.canvas_make.create_line(self.pointing_line_temp_left,
                                                                       self.pointing_line_temp_up,
                                                                       self.pointing_line_temp_left,
                                                                       self.pointing_line_temp_up + 65, width=2)

                #temp pointer movement process
                if take_notation==2:
                    goto = int(self.position_entry.get()) - 2
                else:
                    goto = len(self.linked_list_position) - 2

                # temp pointer movement until find the location
                while self.temp_label_x < self.linked_list_position[goto][4] + 100 + 20:
                    if take_notation == 2:# For insert_after_node()
                        if int(self.position_entry.get()) == 1: # For join after first node
                           break # In that case temp movement not required
                        self.information.config(text="Traversing until found the targeting node")#otherwise print that information

                    else:# For other function except insert_after_node()
                        self.information.config(text="Traversing until found the last node")

                    #pre location forget
                    self.temp_label.place_forget()
                    self.canvas_make.delete(self.pointing_line_temp,self.temp_pointer)

                    #temp pointer all coordinate change
                    self.temp_label_x += 10
                    self.pointing_line_temp_left += 10
                    self.temp_pointer_left +=10

                    self.temp_pointer = self.canvas_make.create_rectangle(self.temp_pointer_left, self.temp_pointer_up,
                                                                          self.temp_pointer_left + 30,
                                                                          self.temp_pointer_up + 30, fill="blue",
                                                                          outline="black", width=3)
                    self.temp_label.place(x=self.temp_label_x, y=self.temp_label_y)
                    self.pointing_line_temp = self.canvas_make.create_line(self.pointing_line_temp_left,
                                                                           self.pointing_line_temp_up,
                                                                           self.pointing_line_temp_left,
                                                                           self.pointing_line_temp_up + 65, width=2)
                    #used for slow the movement
                    time.sleep(0.05)
                    self.window.update()

            # For horizontal motion of the node
            if len(self.linked_list_data_next_store) >0:
                # Remove the NULL label from the last node
                self.linked_list_data_next_store[len(self.linked_list_data_next_store) - 1].pop().place_forget()
                # For horizontal motion of the node in both cases:insert_first and insert_last
                while self.main_node_left < self.linked_list_position[len(self.linked_list_position)-1][4]+100+20:
                        #previous coordinate and position delete of temp pointer
                        self.canvas_make.delete(self.main_container_node, self.data, self.next,self.arrow)
                        self.next_label.place_forget(); self.data_label.place_forget()
                        self.value_set.place_forget()
                        self.next_set.place_forget()
                        self.main_node_left +=10
                        self.data_left +=10
                        self.data_label_x +=10
                        self.main_container_node = self.canvas_make.create_rectangle(self.main_node_left, self.main_node_up, self.main_node_left+100,self.main_node_up+65, outline="brown",width=3)
                        self.data = self.canvas_make.create_rectangle(self.data_left, self.data_up, self.data_left+40, self.data_up+30, outline="green", fill="yellow", width=3)
                        self.next = self.canvas_make.create_rectangle(self.data_left+50, self.data_up, self.data_left+50+ 40, self.data_up+30, outline="green", fill="yellow", width=3)
                        self.next_label.place(x=self.data_label_x+50, y=self.data_label_y)
                        self.data_label.place(x=self.data_label_x, y=self.data_label_y)
                        self.value_set.place(x=self.data_left + 8, y=self.data_up + 3)
                        self.arrow = self.canvas_make.create_line(self.data_left+50 + 25, self.data_up + 15, self.data_left+50 + 65, self.data_up + 15, width=4)
                        self.next_set.place(x=self.data_left+50 + 52, y=self.data_up + 2)

                        if take_notation == 0: # Makes for insert last only.
                            self.information.config(text="New node added to the last node")
                            time.sleep(0.02)
                            self.window.update()

                        if take_notation == 2: # No slow motion except insert last
                            self.information.config(text="New node added after the targeting node")

                   #time to sleep or slow motion
                        time.sleep(0.04)
                        self.window.update()

            #storing widget label
            temp_label = []
            temp_label.append(self.data_label)
            temp_label.append(self.next_label)
            self.linked_list_canvas_small_widget_label.append(temp_label)

            # storing widget
            temp_block_number = []; temp_block_number.append(self.data); temp_block_number.append(self.next); temp_block_number.append(self.main_container_node)
            self.linked_list_canvas_small_widget.append(temp_block_number)

            # storing widget coordinate
            temp_block_location = []
            temp_block_location.append(self.data_left); temp_block_location.append(self.data_up)
            temp_block_location.append(self.data_left+50); temp_block_location.append(self.data_up)
            temp_block_location.append(self.main_node_left); temp_block_location.append(self.main_node_up)
            self.linked_list_position.append(temp_block_location)

            # Forget temp pointer
            self.temp_label.place_forget()
            self.canvas_make.delete(self.pointing_line_temp,self.temp_pointer)
            self.temp_label_x = 40
            self.pointing_line_temp_left = 65
            self.temp_pointer_left = 50

            self.reset_with_store(take_notation)

        except:
            pass

    # 新增：核心——从 CSV 字符串创建链表（对外触发）
    def create_list_from_string(self):
        txt = self.batch_entry_var.get()
        if not txt or not txt.strip():
            messagebox.showerror("Error", "请输入以逗号分隔的值，例如：1,2,3")
            return

        # 解析字符串（按逗号分割，去掉多余空格，忽略空项）
        parts = [p.strip() for p in txt.split(',') if p.strip() != ""]
        if not parts:
            messagebox.showerror("Error", "未解析到有效元素")
            return

        # 禁用按钮，防止并发操作
        self.insert_at_last.config(state=DISABLED)
        self.insert_at_beg.config(state=DISABLED)
        self.delete_at_last.config(state=DISABLED)
        self.delete_at_first.config(state=DISABLED)
        self.insert_after_node.config(state=DISABLED)
        self.delete_particular_node.config(state=DISABLED)

        # 顺序插入每个元素（模拟 insert_last 动画）
        for val in parts:
            # 为了复用已有节点动画逻辑，我们直接用 programmatic 插入
            self.programmatic_insert_last(val)

        # 恢复按钮
        self.insert_at_last.config(state=NORMAL)
        self.insert_at_beg.config(state=NORMAL)
        self.delete_at_last.config(state=NORMAL)
        self.delete_at_first.config(state=NORMAL)
        self.insert_after_node.config(state=NORMAL)
        self.delete_particular_node.config(state=NORMAL)
        self.information.config(text="批量创建完成")

    # 新增：程序化地执行 "insert last" 的可视化（不依赖手动 Entry）
    # 逻辑参考：make_main_container_with_node_value_set_and_next_arrow_creation + insert_node（仅 insert_last 路径）
    def programmatic_insert_last(self, value):
        try:
            # 在顶部创建节点的可视化元素（与 make_node_with_label 相同的起始布局）
            # 临时用到同一套位置属性（与手动插入一致）
            self.new_node_label = Label(self.canvas_make, text="New node", font=("Arial", 13, "bold"), bg="chocolate", fg="green")
            self.new_node_label.place(x=30, y=90)

            # 使用当前的 data_left/data_up 等位置绘制矩形（与手动流程一致）
            self.data = self.canvas_make.create_rectangle(self.data_left, self.data_up, self.data_left+40, self.data_up+30, outline="green", fill="yellow", width=3)
            self.data_label = Label(self.canvas_make, text="data", font=("Arial", 13, "bold"), bg="chocolate", fg="green")
            self.data_label.place(x=self.data_label_x, y=self.data_label_y)

            self.next = self.canvas_make.create_rectangle(self.data_left+50, self.data_up, self.data_left+50+40, self.data_up+30, outline="green", fill="yellow", width=3)
            self.next_label = Label(self.canvas_make, text="next", font=("Arial", 13, "bold"), bg="chocolate", fg="green")
            self.next_label.place(x=self.data_label_x+50, y=self.data_label_y)

            self.main_container_node = self.canvas_make.create_rectangle(self.main_node_left, self.main_node_up, self.main_node_left + 100, self.main_node_up + 65, outline="brown", width=3)

            # value label（直接使用传入的 value）
            self.value_set = Label(self.canvas_make, text=str(value), font=("Arial", 10, "bold"), fg="green", bg="yellow")
            self.value_set.place(x=self.data_left + 8, y=self.data_up + 3)

            # arrow & next_set
            self.arrow = self.canvas_make.create_line(self.data_left+50 + 25, self.data_up + 15, self.data_left+50 + 65, self.data_up + 15, width=4)
            self.next_set = Label(self.canvas_make, text="NULL", font=("Arial", 15, "bold"), fg="green", bg="chocolate")
            self.next_set.place(x=self.data_left+50 + 52, y=self.data_up + 3)

            # --- 垂直下落动画（与 insert_node 中的一段类似） ---
            self.start_initial_point_null.place_forget()  # 去掉 start 指向 NULL 的显示（若存在）
            while self.main_node_up + 65 < 320:
                # 删除并重建以模拟移动（沿用原逻辑）
                self.canvas_make.delete(self.main_container_node, self.data, self.next, self.arrow)
                self.next_label.place_forget(); self.data_label.place_forget()
                self.value_set.place_forget()
                self.next_set.place_forget()

                self.main_node_up += 10
                self.data_up += 10
                self.data_label_y += 10

                self.main_container_node = self.canvas_make.create_rectangle(self.main_node_left, self.main_node_up, self.main_node_left+100, self.main_node_up+65, outline="brown", width=3)
                self.data = self.canvas_make.create_rectangle(self.data_left, self.data_up, self.data_left+40, self.data_up+30, outline="green", fill="yellow", width=3)
                self.next = self.canvas_make.create_rectangle(self.data_left+50, self.data_up, self.data_left+50+ 40, self.data_up+30, outline="green", fill="yellow", width=3)
                self.next_label.place(x=self.data_label_x+50, y=self.data_label_y)
                self.data_label.place(x=self.data_label_x, y=self.data_label_y)
                self.value_set.place(x=self.data_left + 8, y=self.data_up + 3)
                self.arrow = self.canvas_make.create_line(self.data_left+50 + 25, self.data_up + 15, self.data_left+50 + 65, self.data_up + 15, width=4)
                self.next_set.place(x=self.data_left+50 + 52, y=self.data_up + 2)

                time.sleep(0.04)
                self.window.update()

            # --- 如果已有节点，则让 temp 指针遍历至最后一个节点 ---
            if len(self.linked_list_data_next_store) > 1:
                self.next_set.place_forget()  # 新节点的 NULL 临时隐藏（和原逻辑一致）
                self.temp_label.place(x=self.temp_label_x, y=self.temp_label_y)
                self.pointing_line_temp = self.canvas_make.create_line(self.pointing_line_temp_left, self.pointing_line_temp_up, self.pointing_line_temp_left, self.pointing_line_temp_up + 65, width=2)

                goto = len(self.linked_list_position) - 2  # 与插入到尾部一致
                # 移动 temp 指针直到对准 penultimate（用于之后水平移动）
                while self.temp_label_x < self.linked_list_position[goto][4] + 100 + 20:
                    self.temp_label.place_forget()
                    self.canvas_make.delete(self.pointing_line_temp, self.temp_pointer)

                    self.temp_label_x += 10
                    self.pointing_line_temp_left += 10
                    self.temp_pointer_left += 10

                    self.temp_pointer = self.canvas_make.create_rectangle(self.temp_pointer_left, self.temp_pointer_up,
                                                                          self.temp_pointer_left + 30, self.temp_pointer_up + 30, fill="blue",
                                                                          outline="black", width=3)
                    self.temp_label.place(x=self.temp_label_x, y=self.temp_label_y)
                    self.pointing_line_temp = self.canvas_make.create_line(self.pointing_line_temp_left, self.pointing_line_temp_up, self.pointing_line_temp_left, self.pointing_line_temp_up + 65, width=2)

                    time.sleep(0.05)
                    self.window.update()

            # --- 水平移动至目标位置（接入链表末尾） ---
            if len(self.linked_list_data_next_store) > 0:
                # 删除上一个节点的 "NULL" label（按原逻辑）
                self.linked_list_data_next_store[len(self.linked_list_data_next_store) - 1].pop().place_forget()

                while self.main_node_left < self.linked_list_position[len(self.linked_list_position)-1][4] + 100 + 20:
                    self.canvas_make.delete(self.main_container_node, self.data, self.next, self.arrow)
                    self.next_label.place_forget(); self.data_label.place_forget()
                    self.value_set.place_forget()
                    self.next_set.place_forget()

                    self.main_node_left += 10
                    self.data_left += 10
                    self.data_label_x += 10

                    self.main_container_node = self.canvas_make.create_rectangle(self.main_node_left, self.main_node_up, self.main_node_left+100, self.main_node_up+65, outline="brown", width=3)
                    self.data = self.canvas_make.create_rectangle(self.data_left, self.data_up, self.data_left+40, self.data_up+30, outline="green", fill="yellow", width=3)
                    self.next = self.canvas_make.create_rectangle(self.data_left+50, self.data_up, self.data_left+50+ 40, self.data_up+30, outline="green", fill="yellow", width=3)
                    self.next_label.place(x=self.data_label_x+50, y=self.data_label_y)
                    self.data_label.place(x=self.data_label_x, y=self.data_label_y)
                    self.value_set.place(x=self.data_left + 8, y=self.data_up + 3)
                    self.arrow = self.canvas_make.create_line(self.data_left+50 + 25, self.data_up + 15, self.data_left+50 + 65, self.data_up + 15, width=4)
                    self.next_set.place(x=self.data_left+50 + 52, y=self.data_up + 2)

                    self.information.config(text="New node added to the last node")
                    time.sleep(0.04)
                    self.window.update()

            # --- 存储 widget 与位置（与 reset_with_store 中的存储结构一致） ---
            temp_label = []
            temp_label.append(self.data_label)
            temp_label.append(self.next_label)
            self.linked_list_canvas_small_widget_label.append(temp_label)

            temp_block_number = []; temp_block_number.append(self.data); temp_block_number.append(self.next); temp_block_number.append(self.main_container_node)
            self.linked_list_canvas_small_widget.append(temp_block_number)

            temp_block_location = []
            temp_block_location.append(self.data_left); temp_block_location.append(self.data_up)
            temp_block_location.append(self.data_left+50); temp_block_location.append(self.data_up)
            temp_block_location.append(self.main_node_left); temp_block_location.append(self.main_node_up)
            self.linked_list_position.append(temp_block_location)

            # 清理 temp 指针显示
            self.temp_label.place_forget()
            self.canvas_make.delete(self.pointing_line_temp, self.temp_pointer)
            self.temp_label_x = 40
            self.pointing_line_temp_left = 65
            self.temp_pointer_left = 50

            # 把数据保存到 model / node_value_store，并模拟原 reset_with_store 的其余工作
            self.node_value_store.append(str(value))
            temp = []
            temp.append(self.value_set)
            temp.append(self.arrow)
            temp.append(self.next_set)
            self.linked_list_data_next_store.append(temp)

            # data and next label reset
            self.value_set = None
            self.next_set = None

            #Initialize of location of data next label and main block/node（重置为初始值，保证下一个插入从顶部开始）
            self.value_set_x = 40
            self.value_set_y = 160

            self.start_left = 50
            self.start_up = 380

            self.data_left = 30
            self.data_up = 150

            self.main_node_left = 25
            self.main_node_up = 120

            self.data_label_x = 30
            self.data_label_y = 122

            # 为了和手动插入的行为一致，如果是第一个节点需要在 start 处去掉 NULL 显示
            if len(self.linked_list_data_next_store) == 1:
                self.start_initial_point_null.place_forget()

        except Exception as e:
            print("programmatic_insert_last error:", e)
            pass

    def reset_with_store(self,take_notation): # Reset coordinate and store value,arrow and next label
        #Node value store only in that list
        # 这里与原程序一致：将输入的值 append 到 node_value_store（现在保存在 model 中）
        self.node_value_store.append(self.value_entry.get())

        temp = []
        temp.append(self.value_set)
        temp.append(self.arrow)
        temp.append(self.next_set)

        # Main list append
        self.linked_list_data_next_store.append(temp)

        # printing all list value ::Create this at the time of creation of the program to checking
        print(self.linked_list_data_next_store)
        print(self.linked_list_canvas_small_widget)
        print(self.linked_list_position)
        print(self.linked_list_canvas_small_widget_label)
        print(self.node_value_store)

        # data and next label reset
        self.value_set = None
        self.next_set = None

        #location forget of all under  input_take()
        self.element_take_label.place_forget()
        self.value_entry.set(" ")
        self.element_take_entry.place_forget()
        self.add_btn.place_forget()


        # process of value shifting in case of insert_first from left to right and new node insert at last
        if take_notation == 1 and len(self.linked_list_data_next_store) >1:
            temp_val = self.node_value_store[len(self.node_value_store)-1]
            for i in range(len(self.node_value_store)-2,-1,-1):
                self.node_value_store[i+1] = self.node_value_store[i]

            self.node_value_store[0] = temp_val

            #new value label set  :::::  after shifting through list
            for i in range(len(self.node_value_store)):
                self.linked_list_data_next_store[i][0].config(text=self.node_value_store[i])

        #Initialize of location of data next label and main block/node
        self.value_set_x = 40
        self.value_set_y = 160

        self.start_left = 50
        self.start_up = 380

        self.data_left = 30
        self.data_up = 150

        self.main_node_left = 25
        self.main_node_up = 120

        self.data_label_x = 30
        self.data_label_y = 122

        #Button state mode change
        self.insert_at_last.config(state=NORMAL)
        self.insert_at_beg.config(state=NORMAL)
        self.delete_at_last.config(state=NORMAL)
        self.delete_at_first.config(state=NORMAL)
        self.insert_after_node.config(state=NORMAL)
        self.delete_particular_node.config(state=NORMAL)

        #For insert after node function
        if take_notation == 2:
            # value shifting and store process
            temp_value = self.node_value_store[len(self.node_value_store)-1]
            for i in range(len(self.node_value_store)-2,int(self.position_entry.get())-1,-1):
                self.node_value_store[i+1] = self.node_value_store[i]
            self.node_value_store[int(self.position_entry.get())] = temp_value
            print(self.node_value_store)
            for i in range(int(self.position_entry.get()),len(self.linked_list_data_next_store)):
                self.linked_list_data_next_store[i][0].config(text=self.node_value_store[i])

    # For delete last node directly, for delete first and delete particular node indirectly
    def delete_last_node(self,locator):
        # printing all list value :: Create this at the time of creation of the program to checking
        print(self.linked_list_data_next_store)
        print(self.linked_list_canvas_small_widget)
        print(self.linked_list_position)
        print(self.linked_list_canvas_small_widget_label)
        print(self.node_value_store)


        if len(self.linked_list_data_next_store) == 0: # Checking if the list is empty
            messagebox.showerror("Underflow", "Link list is empty")
            return

        # Button state mode change
        self.insert_at_last.config(state=DISABLED)
        self.insert_at_beg.config(state=DISABLED)
        self.delete_at_last.config(state=DISABLED)
        self.delete_at_first.config(state=DISABLED)
        self.insert_after_node.config(state=DISABLED)
        self.delete_particular_node.config(state=DISABLED)

        #temp movement until found the second last node or targeting node
        if (locator == 0 or locator==3) and len(self.linked_list_data_next_store)>1:
            self.temp_pointer = self.canvas_make.create_rectangle(self.temp_pointer_left, self.temp_pointer_up,
                                                                  self.temp_pointer_left + 30,
                                                                  self.temp_pointer_up + 30, fill="blue",
                                                                  outline="black", width=3)
            self.temp_label.place(x=self.temp_label_x, y=self.temp_label_y)

            self.pointing_line_temp = self.canvas_make.create_line(self.pointing_line_temp_left,
                                                                   self.pointing_line_temp_up,
                                                                   self.pointing_line_temp_left,
                                                                   self.pointing_line_temp_up + 65, width=2)
            if len(self.linked_list_data_next_store) > 2:
                if locator == 3: # For delete particular node process
                    goto = int(self.delete_entry.get())-3
                else:
                    goto = len(self.linked_list_position) - 3
                while self.temp_label_x<self.linked_list_position[goto][4]+100+20:
                    if locator == 3:  # For delete particular node process
                        if int(self.delete_entry.get()) == 2:
                           break
                        else:
                            self.information.config(text="Traversing until found the penultimate node of the targeting node")
                    else:
                        self.information.config(text="Traversing until found the penultimate node of the last node")

                    # Forget temp pointer
                    self.temp_label.place_forget()
                    self.canvas_make.delete(self.pointing_line_temp,self.temp_pointer)

                    self.temp_label_x +=10
                    self.pointing_line_temp_left +=10
                    self.temp_pointer_left += 10

                    self.temp_pointer = self.canvas_make.create_rectangle(self.temp_pointer_left, self.temp_pointer_up,
                                                                          self.temp_pointer_left + 30,
                                                                          self.temp_pointer_up + 30, fill="blue",
                                                                          outline="black", width=3)
                    self.temp_label.place(x=self.temp_label_x, y=self.temp_label_y)
                    self.pointing_line_temp = self.canvas_make.create_line(self.pointing_line_temp_left, self.pointing_line_temp_up,
                                                                           self.pointing_line_temp_left,
                                                                           self.pointing_line_temp_up + 65, width=2)
                    time.sleep(0.04)
                    self.window.update()

            #stop some time to ensure that temp pointer reach the second last node or before the targeting node
            i=1
            while i<7:
                i+=2
                time.sleep(0.125)
                self.window.update()

            if locator == 0: #For last node deletion process
               self.information.config(text="Temp pointing node contains the address that present in the next part of last node and\nand Last node deleted")
            else:
                self.information.config(text="Targeting node deleted")

        if locator == 3: # For delete particular node process
           #temp1 pointer creation
           self.temp1_pointer = self.canvas_make.create_rectangle(self.temp_pointer_left+120, self.temp_pointer_up,
                                                                  self.temp_pointer_left + 120+30,
                                                                  self.temp_pointer_up + 30, fill="blue",
                                                                  outline="black", width=3)
           self.temp1_label.place(x=self.temp_label_x+120, y=self.temp_label_y)
           self.pointing_line_temp1 = self.canvas_make.create_line(self.pointing_line_temp_left+120,
                                                                   self.pointing_line_temp_up,
                                                                   self.pointing_line_temp_left+120,
                                                                   self.pointing_line_temp_up + 65, width=2)

           #status update
           self.information.config(text="Temp is pointing the penultimate node of the targeting node and \ntemp1 is pointing the targeting node")

           #Time to wait process
           i = 1
           while i < 7:
               i += 2
               time.sleep(2.5)
               self.window.update()

           #Value shifting and store in proper position for delete particular node process
           for i in range(int(self.delete_entry.get()), len(self.node_value_store)):
               self.linked_list_data_next_store[i-1][0].config(text=self.node_value_store[i])

           for i in range(int(self.delete_entry.get()),len(self.node_value_store)):
               self.node_value_store[i-1] = self.node_value_store[i]

        #Last node, first node, particular node deletion process
        if len(self.linked_list_data_next_store) > 0:
            # delete reference of last node from all list
            temp1 = self.linked_list_data_next_store.pop()
            temp1[0].place_forget()
            self.canvas_make.delete(temp1[1])
            temp1[2].place_forget()

            temp2 = self.linked_list_canvas_small_widget.pop()
            for i in range(len(temp2)):
                self.canvas_make.delete(temp2[i])

            self.linked_list_position.pop()

            if len(self.linked_list_data_next_store) > 0:
               temp3 = self.linked_list_position[len(self.linked_list_position)-1]
               self.next_set = Label(self.canvas_make, text="NULL", font=("Arial", 15, "bold"),
                                  fg="green", bg="chocolate")
               self.next_set.place(x=temp3[2]+52, y=temp3[3])

               self.linked_list_data_next_store[len(self.linked_list_data_next_store)-1].append(self.next_set)

            temp4 = self.linked_list_canvas_small_widget_label.pop()
            for widget_label in temp4:
                widget_label.place_forget()

            #Value delete from list storing only node value
            self.node_value_store.pop()
            print(self.node_value_store)

            # create start pointing NULL
            if len(self.linked_list_data_next_store) == 0:
               self.start_initial_point_null.place(x=40, y=300)

            #For delete last and delete particular node only
            if locator == 0 or locator == 3:
                if locator == 3:  # For temp 1 pointer delete process
                   self.temp1_label.place_forget()
                   self.canvas_make.delete(self.pointing_line_temp1, self.temp1_pointer)
                   self.information.config(text="The next part of the temp is now containing the address that is present in the \nnext part of temp1 and temp1 pointing node is deleted")

                # Time sleep to slow the process
                i = 1
                while i < 7:
                   i += 2
                   time.sleep(3)
                   self.window.update()

                #For temp pointer delete process
                self.temp_label.place_forget()
                self.canvas_make.delete(self.pointing_line_temp,self.temp_pointer)
                self.temp_label_x = 40
                self.pointing_line_temp_left = 65
                self.temp_pointer_left = 50

            # List empty checking with having last status to show
            if len(self.node_value_store) == 0:
               self.information.config(text="List is empty and start pointing NULL")
            elif locator == 0:
                self.information.config(text="Last node deleted")
            elif locator == 3:
                self.information.config(text="Targeting node deleted")

            #Button activation by changing state mode
            self.insert_at_last.config(state=NORMAL)
            self.insert_at_beg.config(state=NORMAL)
            self.delete_at_last.config(state=NORMAL)
            self.delete_at_first.config(state=NORMAL)
            self.insert_after_node.config(state=NORMAL)
            self.delete_particular_node.config(state=NORMAL)

    #For delete first
    def delete_first_node(self):
        if len(self.linked_list_data_next_store) == 0: # empty checking
            messagebox.showerror("Underflow","Link list is empty")


        elif len(self.node_value_store) == 1: # For one node in the list delete process same as delete last
            self.delete_last_node(1) #delete last function call
            self.information.config(text="Now start pointer is containing NULL and first node deleted")

        else:
            #For value shifting right to left
            for i in range(1,len(self.node_value_store)):
                self.node_value_store[i-1] = self.node_value_store[i]

            self.delete_last_node(1) #For delete the last node

            #After shifting new node value set
            for i in range(len(self.linked_list_data_next_store)):
                self.linked_list_data_next_store[i][0].config(text=self.node_value_store[i])

            self.information.config(text="Now start pointer is containing the address that present in the next part of the first node\nand first node deleted")

    #For delete particular node infrastructure
    def delete_single_node_infrastructure(self):
        if len(self.node_value_store) == 0: #Checking if link list is empty
           self.information.config(text="Link list is empty  ::  Nothing to delete")
           return
        else:
           self.information.config(text="First node position: 1")

        # Button deactivation
        self.insert_at_last.config(state=DISABLED)
        self.insert_at_beg.config(state=DISABLED)
        self.delete_at_last.config(state=DISABLED)
        self.delete_at_first.config(state=DISABLED)
        self.insert_after_node.config(state=DISABLED)
        self.delete_particular_node.config(state=DISABLED)

        #input taking process set
        self.position_label = Label(self.window, text="Enter the node position you want to delete",
                                    font=("Arial", 13, "bold"), bg="orange",
                                    fg="brown")
        self.position_label.place(x=1000, y=620)

        self.position_take_entry = Entry(self.window, font=("Arial", 13, "bold"), bg="white", state=NORMAL,
                                         fg="blue", relief=SUNKEN, bd=5, textvar=self.delete_entry)
        self.position_take_entry.place(x=1020, y=650)

        self.position_take_entry.focus()

        self.find_btn = Button(self.window, text="Find", font=("Arial", 10, "bold"),
                               bg="blue", fg="red", relief=RAISED, bd=3, padx=3, pady=3,
                               state=NORMAL, command=self.delete_single_node)
        self.find_btn.place(x=1230, y=650)

    # For delete particular node process start
    def delete_single_node(self):
        self.position_label.place_forget()
        self.position_take_entry.place_forget()
        self.find_btn.place_forget()

        # Node position checking
        if int(self.delete_entry.get())>len(self.node_value_store) or int(self.delete_entry.get())<1:
           messagebox.showerror("Error","Positional node not found")
        elif int(self.delete_entry.get()) == 1: #For only one node present in the list
           self.delete_first_node()
        else:
            self.delete_last_node(3)

        # Button activation
        self.insert_at_last.config(state=NORMAL)
        self.insert_at_beg.config(state=NORMAL)
        self.delete_at_last.config(state=NORMAL)
        self.delete_at_first.config(state=NORMAL)
        self.insert_after_node.config(state=NORMAL)
        self.delete_particular_node.config(state=NORMAL)

if __name__ == '__main__':
    window = Tk()
    window.title("Singly Linked List Visualizer")
    window.geometry("1350x730")
    window.maxsize(1350,730)
    window.minsize(1350,730)
    # window.iconbitmap('Singly linked list visualizer\\list_icon.ico')
    LinkList(window)
    window.mainloop()
