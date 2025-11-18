from tkinter import *
from tkinter import messagebox
import time
from linked_list.linked_list_model import LinkedListModel
import storage as storage
from llm import function_dispatcher
from linked_list.ui_utils import heading_with_label_subheading, make_start_with_other, make_btn, make_batch_create_ui, draw_gradient
from DSL_utils import process_command

class LinkList:
    def __init__(self, root):
        self.window = root
        self.chat_window = None
        self.window.config(bg="#F5F7FA")
        self.canvas_width, self.canvas_height = 1350, 500
        self.canvas_make = Canvas(self.window, bg="#0575E6",
                                  width=self.canvas_width, height=self.canvas_height,
                                  relief=RAISED, bd=8)
        self.canvas_make.pack()
        draw_gradient(self.canvas_make, self.canvas_width, self.canvas_height,
                           start_color="#021B79", end_color="#89CFF0", steps=200)

        # model & stores
        self.model = LinkedListModel()
        self.node_value_store = self.model.node_value_store
        self.linked_list_canvas_small_widget = []
        self.linked_list_canvas_small_widget_label = []
        self.linked_list_position = []
        self.linked_list_data_next_store = []

        self.value_entry = StringVar(value=" ")
        self.position_entry = StringVar(value=" ")
        self.delete_entry = StringVar(value=" ")
        self.batch_entry_var = StringVar(value=" ")
        self.dsl_var = StringVar(value="")

        self._init_coords()

        for name in ("head_name","information","insert_at_beg","insert_at_last","delete_at_first",
                     "delete_at_last","position_label","start_label","temp_label","temp1_label",
                     "data_label","next_label","element_take_label","element_take_entry","add_btn",
                     "value_set","next_set","start_initial_point_null","new_node_label",
                     "position_take_entry","find_btn","insert_after_node","delete_particular_node",
                     "save_btn","load_btn","back_to_main_btn"):
            setattr(self, name, None)
        heading_with_label_subheading(self)
        make_btn(self)
        make_start_with_other(self)
        make_batch_create_ui(self)

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

    def set_chat_window(self, chat_window):
        self.chat_window = chat_window  
    
    def _init_coords(self):
        self.start_left = 50; self.start_up = 380
        self.main_node_left = 25; self.main_node_up = 120
        self.data_left = 30; self.data_up = 150
        self.data_label_x = 30; self.data_label_y = 122
        self.temp_label_x = 40; self.temp_label_y = 150
        self.temp_pointer_left = 50; self.temp_pointer_up = 180
        self.pointing_line_temp_left = 65; self.pointing_line_temp_up = 195
        self.pointing_line_start = None
        self.pointing_line_temp = None
        self.pointing_line_temp1 = None
        self.temp_pointer = None
        self.temp1_pointer = None
        self.temp_label_x = 40
        self.node_helpers_reset()

    def node_helpers_reset(self):
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

    def process_dsl(self, event=None):
        txt = self.dsl_var.get().strip()
        try:
            process_command(self,txt)
        finally:
            try: self.dsl_var.set("")
            except: pass

    def save_structure(self):
        node_values = self.node_value_store
        success = storage.save_linked_list_to_file(node_values)
        if success:
            messagebox.showinfo("成功", "链表结构已保存")
        else:
            messagebox.showerror("错误", "保存失败")

    def clear_visualization(self):
        for entry in self.linked_list_data_next_store:
            try: entry[0].place_forget()
            except: pass
            try: self.canvas_make.delete(entry[1])
            except: pass
            try: entry[2].place_forget()
            except: pass
        self.linked_list_data_next_store.clear()

        for widgets in self.linked_list_canvas_small_widget:
            for wid in widgets:
                try: self.canvas_make.delete(wid)
                except: 
                    try: wid.place_forget()
                    except: pass
        self.linked_list_canvas_small_widget.clear()

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

    def reset_coords(self):
        self._init_coords()
        self.node_helpers_reset()

    def load_structure(self):
        loaded = storage.load_linked_list_from_file()
        self.clear_visualization()
        self.toggle_action_buttons(DISABLED)
        for val in loaded:
            self.programmatic_insert_last(val)
            self.window.update()
        self.toggle_action_buttons(NORMAL)
        self.information.config(text="加载完成")
        messagebox.showinfo("成功", "链表已从文件加载并重建可视化")

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
                messagebox.showerror("Not found","目标节点不存在")
                self.information.config(text="start 是一个指向第一个节点的指针，而 temp 指针在进行尾部插入和尾部删除操作时，用来遍历到目标位置。")
            else:
                self.insert_after_node.config(state=DISABLED)
                self.information.config(text="目标节点已找到")
                self.make_node_with_label(2)
        except Exception as e:
            messagebox.showerror("错误", f"位置检查出错: {e}")

    def make_node_with_label(self, take_notation):
        self.toggle_action_buttons(DISABLED)
        self.new_node_label = Label(self.canvas_make, text="New node", font=("Arial",13,"bold"), bg="chocolate", fg="green")
        self.new_node_label.place(x=30, y=90)
        self.data = self.make_rect(self.data_left,self.data_up,self.data_left+40,self.data_up+30, outline="green", fill="yellow", width=3)
        self.data_label = Label(self.canvas_make, text="data", font=("Arial",13,"bold"), bg="chocolate", fg="green")
        self.data_label.place(x=self.data_label_x, y=self.data_label_y)
        self.next = self.make_rect(self.data_left+50,self.data_up,self.data_left+90,self.data_up+30, outline="green", fill="yellow", width=3)
        self.next_label = Label(self.canvas_make, text="next", font=("Arial",13,"bold"), bg="chocolate", fg="green")
        self.next_label.place(x=self.data_label_x+50, y=self.data_label_y)
        self.main_container_node = self.make_rect(self.main_node_left, self.main_node_up, self.main_node_left+100, self.main_node_up+65, outline="brown", width=3)
        self.input_take(take_notation)

    def input_take(self, take_notation):
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

    def insert_node(self, take_notation):
        try:
            self.information.config(text=" ")
            self.new_node_label.place_forget()
            try: self.start_initial_point_null.place_forget()
            except: pass

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
                self.arrow = self.canvas_make.create_line(self.data_left+75, self.data_up+15, self.data_left+115, self.data_up+15, width=4)
                self.next_set.place(x=self.data_left+102, y=self.data_up + 2)

                time.sleep(0.04); self.window.update()
            if len(self.linked_list_data_next_store) > 1 and (take_notation == 0 or take_notation == 2):
                self.next_set.place_forget()
                self.temp_label.place(x=self.temp_label_x, y=self.temp_label_y)
                self.pointing_line_temp = self.canvas_make.create_line(self.pointing_line_temp_left, self.pointing_line_temp_up,
                                                                       self.pointing_line_temp_left, self.pointing_line_temp_up + 65, width=2)
                goto = (int(self.position_entry.get()) - 2) if take_notation == 2 else (len(self.linked_list_position) - 2)
                while self.temp_label_x < self.linked_list_position[goto][4] + 120:
                    if take_notation == 2:
                        if int(self.position_entry.get()) == 1: break
                        self.information.config(text="遍历直到找到目标节点")
                    else:
                        self.information.config(text="遍历直到找到最后一个节点")
                    self.temp_label.place_forget()
                    self.canvas_make.delete(self.pointing_line_temp, self.temp_pointer)
                    self.temp_label_x += 10; self.pointing_line_temp_left += 10; self.temp_pointer_left += 10
                    self.temp_pointer = self.make_rect(self.temp_pointer_left, self.temp_pointer_up, self.temp_pointer_left + 30, self.temp_pointer_up + 30, fill="blue", outline="black", width=3)
                    self.temp_label.place(x=self.temp_label_x, y=self.temp_label_y)
                    self.pointing_line_temp = self.canvas_make.create_line(self.pointing_line_temp_left, self.pointing_line_temp_up, self.pointing_line_temp_left, self.pointing_line_temp_up + 65, width=2)
                    time.sleep(0.05); self.window.update()

            if len(self.linked_list_data_next_store) > 0:
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
                        self.information.config(text="新节点已添加到链表的末尾")
                    elif take_notation == 2:
                        self.information.config(text="新节点已添加到目标节点之后")
                    time.sleep(0.04); self.window.update()
            self.linked_list_canvas_small_widget_label.append([self.data_label, self.next_label])
            self.linked_list_canvas_small_widget.append([self.data, self.next, self.main_container_node])
            loc = [self.data_left, self.data_up, self.data_left+50, self.data_up, self.main_node_left, self.main_node_up]
            self.linked_list_position.append(loc)
            try:
                self.temp_label.place_forget()
                self.canvas_make.delete(self.pointing_line_temp, self.temp_pointer)
            except: pass
            self.temp_label_x = 40; self.pointing_line_temp_left = 65; self.temp_pointer_left = 50
            if take_notation == 0 or take_notation == 1 or take_notation == 2:
                self.reset_with_store(take_notation)
        except Exception as e:
            print("insert_node error:", e)

    def programmatic_insert_last(self, value):
        print(f"DEBUG: Starting programmatic insert of value: {value}")
        print(f"DEBUG: self type: {type(self).__name__}")
        print(f"DEBUG: canvas_make exists: {hasattr(self, 'canvas_make')}")
        print(f"DEBUG: Current node_value_store: {getattr(self, 'node_value_store', [])}")
        
        try:
            print(f"DEBUG: Creating new node with value: {value}")
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
                    self.information.config(text="新节点已添加到最后一个节点")
                    time.sleep(0.04); self.window.update()
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

            self.reset_coords()
            if len(self.linked_list_data_next_store) == 1:
                try: self.start_initial_point_null.place_forget()
                except: pass

        except Exception as e:
            print("programmatic_insert_last error:", e)

    def reset_with_store(self, take_notation):
        # Add the new node's logical value and visual items (they were created at the end)
        self.node_value_store.append(self.value_entry.get())
        self.linked_list_data_next_store.append([self.value_set, self.arrow, self.next_set])
        print(self.linked_list_data_next_store); print(self.linked_list_canvas_small_widget)
        print(self.linked_list_position); print(self.linked_list_canvas_small_widget_label); print(self.node_value_store)

        try:
            self.element_take_label.place_forget(); self.value_entry.set(" "); self.element_take_entry.place_forget(); self.add_btn.place_forget()
        except: pass

        # For insert-at-begin (take_notation == 1) the original shifting behavior is OK
        if take_notation == 1 and len(self.linked_list_data_next_store) > 1:
            temp_val = self.node_value_store[-1]
            for i in range(len(self.node_value_store)-2, -1, -1):
                self.node_value_store[i+1] = self.node_value_store[i]
            self.node_value_store[0] = temp_val
            for i in range(len(self.node_value_store)):
                try: self.linked_list_data_next_store[i][0].config(text=self.node_value_store[i])
                except: pass

        # For insert-at-position (take_notation == 2) perform an in-place insertion of the visual node
        elif take_notation == 2:
            try:
                temp_value = self.node_value_store[-1]
                pos = int(self.position_entry.get())  # position is 1-based and insertion is after that position
                insert_idx = pos  # corresponds to placing new node at index == pos (0-based)

                # remove the last-created visual group (it was appended at the end)
                new_visual = self.linked_list_data_next_store.pop()  # [value_set, arrow, next_set]
                new_canvas_group = None
                try:
                    new_canvas_group = self.linked_list_canvas_small_widget.pop()
                except: pass
                try:
                    new_pos_loc = self.linked_list_position.pop()
                except: new_pos_loc = None

                # Insert logical value into model/list
                try:
                    self.node_value_store.insert(insert_idx, temp_value)
                except Exception:
                    # Fallback: if model doesn't support insert, emulate by shifting
                    for i in range(len(self.node_value_store)-2, insert_idx-1, -1):
                        self.node_value_store[i+1] = self.node_value_store[i]
                    self.node_value_store[insert_idx] = temp_value

                # Insert the visual group into the lists at the insertion index
                self.linked_list_data_next_store.insert(insert_idx, new_visual)
                if new_canvas_group is not None:
                    self.linked_list_canvas_small_widget.insert(insert_idx, new_canvas_group)
                if new_pos_loc is not None:
                    # new_pos_loc holds coordinates where the node was created (end). We'll insert it and then shift subsequent nodes.
                    self.linked_list_position.insert(insert_idx, new_pos_loc)

                # Shift all canvas items and stored positions for nodes AFTER the inserted node to make space
                dx = 120  # horizontal shift amount to make room for the new node
                for i in range(insert_idx+1, len(self.linked_list_position)):
                    try:
                        # shift stored position
                        self.linked_list_position[i][0] += dx
                        self.linked_list_position[i][2] += dx
                        self.linked_list_position[i][4] += dx

                        # move canvas rectangles / shapes
                        group = None
                        try:
                            group = self.linked_list_canvas_small_widget[i]
                        except: group = None
                        if group:
                            for cid in group:
                                try: self.canvas_make.move(cid, dx, 0)
                                except: pass

                        # move the arrow line and update its coords
                        try:
                            entry = self.linked_list_data_next_store[i]
                            vset = entry[0] if len(entry) > 0 else None
                            arrow_id = entry[1] if len(entry) > 1 else None
                            nset = entry[2] if len(entry) > 2 else None
                            # move arrow line if present
                            if arrow_id is not None:
                                try:
                                    self.canvas_make.move(arrow_id, dx, 0)
                                except:
                                    # fallback to coords update if move fails
                                    try:
                                        coords = self.canvas_make.coords(arrow_id)
                                        if coords and len(coords) >= 4:
                                            self.canvas_make.coords(arrow_id, coords[0]+dx, coords[1], coords[2]+dx, coords[3])
                                    except: pass
                            # move placed labels if present
                            if vset is not None:
                                try: vset.place_configure(x=(int(vset.place_info().get('x')) + dx))
                                except: pass
                            if nset is not None:
                                try: nset.place_configure(x=(int(nset.place_info().get('x')) + dx))
                                except: pass
                        except: pass
                    except Exception:
                        # ignore shifting errors per-node to avoid crashing the UI
                        pass

                # Now update arrows and label texts for affected nodes (previous and inserted and next)
                try:
                    # update text of all value labels to match model
                    for i in range(len(self.node_value_store)):
                        try:
                            self.linked_list_data_next_store[i][0].config(text=self.node_value_store[i])
                        except: pass

                    # recalc arrow coords for each node where possible
                    for i in range(len(self.linked_list_data_next_store)):
                        try:
                            data_x = self.linked_list_position[i][0]
                            data_y = self.linked_list_position[i][1]
                            arrow_id = self.linked_list_data_next_store[i][1]
                            try: self.canvas_make.coords(arrow_id, data_x+75, data_y+15, data_x+115, data_y+15)
                            except: pass
                            # place value and next labels at sensible computed positions
                            try: self.linked_list_data_next_store[i][0].place_configure(x=data_x+8, y=data_y+3)
                            except: pass
                            try: self.linked_list_data_next_store[i][2].place_configure(x=data_x+102, y=data_y+3)
                            except: pass
                        except: pass
                except: pass

            except Exception as e:
                print("insert-at-position error:", e)

        # default cleanup
        self.reset_coords()
        self.toggle_action_buttons(NORMAL)

    def _rebuild_visuals_from_store(self):
        """清除当前可视化并根据 `self.node_value_store` 重新构建所有节点的可视化（无动画）。"""
        # 保存原有位置（如果存在），以便重建时尽量复用坐标，避免整体跳位
        prev_positions = list(self.linked_list_position) if self.linked_list_position else []

        # 删除现有可视化元素（画布和标签）
        try:
            for entry in list(self.linked_list_data_next_store):
                try:
                    val_label = entry[0] if len(entry) > 0 else None
                    arrow_id = entry[1] if len(entry) > 1 else None
                    null_label = entry[2] if len(entry) > 2 else None
                    if val_label:
                        val_label.destroy()
                    if null_label:
                        null_label.destroy()
                    if arrow_id is not None:
                        try:
                            self.canvas_make.delete(arrow_id)
                        except Exception:
                            pass
                except Exception:
                    pass
        except Exception:
            pass

        try:
            for widgets in list(self.linked_list_canvas_small_widget):
                for wid in widgets:
                    try:
                        self.canvas_make.delete(wid)
                    except Exception:
                        try:
                            wid.destroy()
                        except Exception:
                            pass
        except Exception:
            pass

        try:
            for labels in list(self.linked_list_canvas_small_widget_label):
                for lab in labels:
                    try:
                        lab.destroy()
                    except Exception:
                        pass
        except Exception:
            pass


        # clear lists
        self.linked_list_data_next_store.clear()
        self.linked_list_canvas_small_widget.clear()
        self.linked_list_canvas_small_widget_label.clear()
        self.linked_list_position.clear()

        # Build fresh visuals from logical store
        n = len(self.node_value_store)
        # spacing and fallback coords
        spacing = 120
        base_node_left = self.main_node_left
        base_node_up = self.main_node_up

        for i, val in enumerate(self.node_value_store):
            # 优先使用之前保存的坐标，保证位置不发生明显跳动
            if i < len(prev_positions):
                prev = prev_positions[i]
                # prev format: [data_left, data_up, data_left+50, data_up, main_node_left, main_node_up]
                node_left = prev[4]
                data_left = prev[0]
                data_up = prev[1]
            else:
                # 若是新节点，放在最后一个已有节点右侧或基准位置
                if len(prev_positions) > 0:
                    last = prev_positions[-1]
                    node_left = last[4] + spacing * (i - len(prev_positions) + 1)
                    data_left = node_left + (self.data_left - self.main_node_left)
                    data_up = last[1]
                else:
                    node_left = base_node_left + i * spacing
                    data_left = node_left + (self.data_left - self.main_node_left)
                    data_up = base_node_up

            # rectangles and labels
            data_rect = self.make_rect(data_left, data_up, data_left + 40, data_up + 30, outline="green", fill="yellow", width=3)
            data_lbl = Label(self.canvas_make, text="data", font=("Arial",13,"bold"), bg="chocolate", fg="green")
            data_lbl.place(x=data_left, y=data_up - 28)
            next_rect = self.make_rect(data_left + 50, data_up, data_left + 90, data_up + 30, outline="green", fill="yellow", width=3)
            next_lbl = Label(self.canvas_make, text="next", font=("Arial",13,"bold"), bg="chocolate", fg="green")
            next_lbl.place(x=data_left + 50, y=data_up - 28)
            main_rect = self.make_rect(node_left, data_up - (self.data_up - self.main_node_up), node_left + 100, data_up - (self.data_up - self.main_node_up) + 65, outline="brown", width=3)

            # value label
            value_label = Label(self.canvas_make, text=str(val), font=("Arial",10,"bold"), fg="green", bg="yellow")
            value_label.place(x=data_left + 8, y=data_up + 3)

            # small arrow (short arrow inside node)
            arrow_id = self.canvas_make.create_line(data_left+75, data_up+15, data_left+115, data_up+15, width=4)

            # next_set label: show NULL only for last node
            next_text = "NULL" if i == n-1 else ""
            next_set = Label(self.canvas_make, text=next_text, font=("Arial",15,"bold"), fg="green", bg="chocolate")
            next_set.place(x=data_left + 102, y=data_up + 3)

            # store
            self.linked_list_canvas_small_widget.append([data_rect, next_rect, main_rect])
            self.linked_list_canvas_small_widget_label.append([data_lbl, next_lbl])
            self.linked_list_data_next_store.append([value_label, arrow_id, next_set])

            loc = [data_left, data_up, data_left+50, data_up, node_left, data_up - (self.data_up - self.main_node_up)]
            self.linked_list_position.append(loc)

        # update start pointer
        if len(self.linked_list_position) > 0:
            first_node_x = self.linked_list_position[0][4] + 50
            first_node_y = self.linked_list_position[0][5] + 32
            try:
                if self.pointing_line_start:
                    self.canvas_make.coords(self.pointing_line_start, 65, 327, first_node_x, first_node_y)
                else:
                    self.pointing_line_start = self.canvas_make.create_line(65, 327, first_node_x, first_node_y, width=3, fill='green')
            except Exception:
                # create if missing
                try:
                    self.pointing_line_start = self.canvas_make.create_line(65, 327, first_node_x, first_node_y, width=3, fill='green')
                except Exception:
                    pass
            try:
                self.start_initial_point_null.place_forget()
            except Exception:
                pass
        else:
            # no nodes -> point to NULL
            try:
                if self.pointing_line_start:
                    self.canvas_make.coords(self.pointing_line_start, 65, 327, 65, 395)
                else:
                    self.pointing_line_start = self.canvas_make.create_line(65, 327, 65, 395, width=3, fill='green')
            except Exception:
                pass
            try:
                self.start_initial_point_null.place(x=40, y=300)
            except Exception:
                pass

        self.window.update()

    def insert_at_no_animation(self, pos, value):
        """在位置 `pos` (1-based) 处插入值 `value`，不执行动画，只保证最终可视化结果正确。"""
        # validate position
        if pos < 1:
            pos = 1
        n = len(self.node_value_store)
        if pos > n + 1:
            pos = n + 1

        try:
            # insert logical value
            self.node_value_store.insert(pos-1, str(value))
        except Exception:
            # fallback: extend then set
            try:
                arr = list(self.node_value_store)
                arr.insert(pos-1, str(value))
                self.node_value_store = arr
            except Exception as e:
                messagebox.showerror("错误", f"插入失败：{e}")
                return

        # rebuild visuals from logical store
        try:
            self._rebuild_visuals_from_store()
            self.information.config(text=f"已在位置 {pos} 插入节点 {value}")
        except Exception as e:
            messagebox.showerror("错误", f"可视化重建失败：{e}")

    def animate_insert_between_nodes(self, prev_node_idx, next_node_idx, value):
        """在指定位置之间插入节点的动画"""
        self.toggle_action_buttons(DISABLED)
        
        try:
            # 获取前后节点的位置信息
            prev_pos = self.linked_list_position[prev_node_idx]
            next_pos = self.linked_list_position[next_node_idx]
            
            # 计算新节点的临时位置（在两个节点之间的上方）
            temp_x = (prev_pos[4] + next_pos[4]) / 2
            temp_y = prev_pos[5] - 100  # 上方位置
            
            # 创建新节点的可视化元素（在临时位置）
            self._create_temp_node_at_position(temp_x, temp_y, value)
            
            # 第一步：显示新节点的指针指向后一个节点
            self.information.config(text="第一步：新节点的指针指向后一个节点")
            self.window.update()
            time.sleep(1)
            
            # 绘制从新节点指向后一个节点的箭头（红色粗箭头）
            new_node_right = temp_x + 95  # 新节点右侧（next部分右侧）
            new_node_center_y = temp_y + 45  # 新节点垂直中心
            
            # 计算后一个节点的连接点位置
            next_node_connect_x = next_pos[4] + 25  # 后一个节点主容器左侧 + 25
            next_node_connect_y = next_pos[5] + 32  # 后一个节点主容器上侧 + 32
            
            # 绘制红色粗箭头 - 从新节点右侧指向后一个节点左侧
            temp_arrow = self.canvas_make.create_line(
                new_node_right, new_node_center_y,
                next_node_connect_x, next_node_connect_y,
                arrow=LAST, width=5, fill="red", arrowshape=(16, 20, 6)
            )
            
            # 添加箭头标签
            arrow_label1 = Label(self.canvas_make, text="新节点指向后一个节点", 
                                font=("Arial", 10, "bold"), bg="white", fg="red")
            arrow_label1.place(x=(new_node_right + next_node_connect_x)/2 - 60, 
                            y=(new_node_center_y + next_node_connect_y)/2 - 20)
            
            self.window.update()
            time.sleep(1.5)
            
            # 第二步：显示前一个节点的指针指向新节点
            self.information.config(text="第二步：前一个节点的指针指向新节点")
            self.window.update()
            time.sleep(1)
            
            # 修改前一个节点的箭头指向新节点
            prev_node_right = prev_pos[0] + 75  # 前一个节点右侧（data部分右侧）
            prev_node_center_y = prev_pos[1] + 15  # 前一个节点垂直中心
            new_node_left = temp_x + 25  # 新节点左侧（主容器左侧 + 25）
            new_node_center_y = temp_y + 32  # 新节点垂直中心
            
            # 创建从前一个节点指向新节点的箭头（蓝色粗箭头，曲线向下弯曲）
            control_x = (prev_node_right + new_node_left) / 2
            control_y = max(prev_node_center_y, new_node_center_y) + 50
            
            curve_points = []
            for t in range(0, 11):
                t_normalized = t / 10.0
                x = (1-t_normalized)**2 * prev_node_right + 2*(1-t_normalized)*t_normalized * control_x + t_normalized**2 * new_node_left
                y = (1-t_normalized)**2 * prev_node_center_y + 2*(1-t_normalized)*t_normalized * control_y + t_normalized**2 * new_node_center_y
                curve_points.extend([x, y])
            
            prev_to_new_arrow = self.canvas_make.create_line(
                curve_points, arrow=LAST, width=5, fill="blue", smooth=1, arrowshape=(16, 20, 6)
            )
            
            # 添加箭头标签
            arrow_label2 = Label(self.canvas_make, text="前一个节点指向新节点", 
                                font=("Arial", 10, "bold"), bg="white", fg="blue")
            arrow_label2.place(x=control_x - 60, y=control_y - 20)
            
            self.window.update()
            time.sleep(1.5)
            
            # 第三步：动画完成，准备显示最终结果
            self.information.config(text="插入动画完成，正在更新链表...")
            self.window.update()
            time.sleep(1)
            
            # 清理临时图形
            self.canvas_make.delete(temp_arrow)
            self.canvas_make.delete(prev_to_new_arrow)
            arrow_label1.destroy()
            arrow_label2.destroy()
            self._remove_temp_node()
            
        except Exception as e:
            print(f"animate_insert_between_nodes error: {e}")
        finally:
            self.toggle_action_buttons(NORMAL)

    def _create_temp_node_at_position(self, x, y, value):
        """在指定位置创建临时节点"""
        # 创建临时节点
        self.temp_main = self.make_rect(x, y, x+100, y+65, outline="red", width=3)
        self.temp_data = self.make_rect(x+5, y+30, x+45, y+60, outline="green", fill="yellow", width=3)
        self.temp_next = self.make_rect(x+55, y+30, x+95, y+60, outline="green", fill="yellow", width=3)
        
        # 显示值
        self.temp_value = Label(self.canvas_make, text=str(value), font=("Arial",10,"bold"), 
                               fg="green", bg="yellow")
        self.temp_value.place(x=x+13, y=y+33)
        
        # 标签
        self.temp_data_label = Label(self.canvas_make, text="data", font=("Arial",10,"bold"), 
                                    bg="chocolate", fg="green")
        self.temp_data_label.place(x=x+5, y=y+5)
        self.temp_next_label = Label(self.canvas_make, text="next", font=("Arial",10,"bold"), 
                                    bg="chocolate", fg="green")
        self.temp_next_label.place(x=x+55, y=y+5)
        
        # 在临时节点内部添加一个小箭头
        self.temp_inner_arrow = self.canvas_make.create_line(
            x+75, y+45, x+95, y+45, width=3, fill="black"
        )

    def _remove_temp_node(self):
        """移除临时节点"""
        try:
            self.canvas_make.delete(self.temp_main)
            self.canvas_make.delete(self.temp_data)
            self.canvas_make.delete(self.temp_next)
            self.canvas_make.delete(self.temp_inner_arrow)
            self.temp_value.destroy()
            self.temp_data_label.destroy()
            self.temp_next_label.destroy()
        except Exception as e:
            print(f"移除临时节点时出错: {e}")

    def delete_at_position(self, pos):
        """删除指定位置的节点，使用正确的链表删除逻辑"""
        if pos < 1 or pos > len(self.node_value_store):
            messagebox.showerror("错误", f"位置越界：当前链表长度 {len(self.node_value_store)}")
            return
        
        self.toggle_action_buttons(DISABLED)
        
        try:
            # 逻辑删除
            if hasattr(self.model, 'delete_at_position'):
                self.model.delete_at_position(pos)
            else:
                # 备用逻辑删除
                self.node_value_store.pop(pos-1)
            
            # 可视化删除
            idx = pos - 1  # 转换为0-based索引
            
            if pos == 1:  # 删除头节点
                self._delete_head_node(idx)
            elif pos == len(self.node_value_store) + 1:  # 删除尾节点
                self._delete_tail_node(idx)
            else:  # 删除中间节点
                self._delete_middle_node(idx)
                
        except Exception as e:
            messagebox.showerror("错误", f"删除失败：{e}")
        finally:
            self.toggle_action_buttons(NORMAL)

    def _delete_head_node(self, idx):
        """删除头节点"""
        # 先显示start指针移动到第二个节点的动画
        if len(self.linked_list_position) > 1:
            second_node_x = self.linked_list_position[1][4] + 50
            second_node_y = self.linked_list_position[1][5] + 32
            
            # 动画：start指针移动到第二个节点
            current_x = 65
            while current_x < second_node_x:
                self.canvas_make.coords(self.pointing_line_start, 65, 327, current_x, second_node_y)
                current_x += 10
                time.sleep(0.05)
                self.window.update()
        
        # 删除可视化元素
        self._remove_visual_elements(idx)
        
        # 左移所有后续节点
        if len(self.linked_list_position) > 0:
            self._shift_nodes_left(0)
        
        # 更新start指针
        if len(self.linked_list_position) > 0:
            first_node_x = self.linked_list_position[0][4] + 50
            first_node_y = self.linked_list_position[0][5] + 32
            self.canvas_make.coords(self.pointing_line_start, 65, 327, first_node_x, first_node_y)
        else:
            # 如果链表为空，start指向NULL
            self.canvas_make.coords(self.pointing_line_start, 65, 327, 65, 395)
            self.start_initial_point_null.place(x=40, y=300)
        
        self.information.config(text="头节点已被删除，后续节点已左移")

    def _delete_tail_node(self, idx):
        """删除尾节点"""
        if idx > 0:  # 确保不是第一个节点
            # 显示temp指针移动到倒数第二个节点的动画
            self.temp_label.place(x=self.temp_label_x, y=self.temp_label_y)
            self.pointing_line_temp = self.canvas_make.create_line(
                self.pointing_line_temp_left, self.pointing_line_temp_up,
                self.pointing_line_temp_left, self.pointing_line_temp_up + 65, width=2
            )
            
            # 移动到倒数第二个节点
            target_x = self.linked_list_position[idx-1][4] + 60
            while self.temp_label_x < target_x:
                self.temp_label.place_forget()
                self.canvas_make.delete(self.pointing_line_temp)
                self.temp_label_x += 10
                self.pointing_line_temp_left += 10
                self.temp_label.place(x=self.temp_label_x, y=self.temp_label_y)
                self.pointing_line_temp = self.canvas_make.create_line(
                    self.pointing_line_temp_left, self.pointing_line_temp_up,
                    self.pointing_line_temp_left, self.pointing_line_temp_up + 65, width=2
                )
                time.sleep(0.05)
                self.window.update()
            
            # 将倒数第二个节点的next指针设为NULL (安全获取条目)
            entry = self.linked_list_data_next_store[idx-1]
            prev_arrow_id = entry[1] if len(entry) > 1 else None
            data_x = self.linked_list_position[idx-1][0]
            data_y = self.linked_list_position[idx-1][1]
            if prev_arrow_id is not None:
                try:
                    self.canvas_make.coords(prev_arrow_id, data_x+75, data_y+15, data_x+90, data_y+15)
                except: pass
            
            # 更新NULL标签
            old_null = entry[2] if len(entry) > 2 else None
            if old_null:
                try: old_null.destroy()
                except: pass
            new_null = Label(self.canvas_make, text="NULL", font=("Arial", 15, "bold"), fg="green", bg="chocolate")
            try: new_null.place(x=data_x+77, y=data_y+3)
            except: pass
            # 写回到结构（确保索引存在）
            try:
                if len(entry) > 2:
                    self.linked_list_data_next_store[idx-1][2] = new_null
                else:
                    # extend entry to have next_set slot
                    while len(self.linked_list_data_next_store[idx-1]) < 3:
                        self.linked_list_data_next_store[idx-1].append(None)
                    self.linked_list_data_next_store[idx-1][2] = new_null
            except: pass
            
            # 移除temp指针
            self.temp_label.place_forget()
            self.canvas_make.delete(self.pointing_line_temp)
            self.temp_label_x = 40
            self.pointing_line_temp_left = 65
        
        # 删除可视化元素
        self._remove_visual_elements(idx)
        
        self.information.config(text="尾节点已被删除")

    def _delete_middle_node(self, idx):
        """删除中间节点 - 修复版本"""
        # 显示temp指针找到要删除节点的前一个节点
        self.temp_label.place(x=self.temp_label_x, y=self.temp_label_y)
        self.pointing_line_temp = self.canvas_make.create_line(
            self.pointing_line_temp_left, self.pointing_line_temp_up,
            self.pointing_line_temp_left, self.pointing_line_temp_up + 65, width=2
        )
        
        # 动画：移动temp指针到前一个节点
        prev_node_x = self.linked_list_position[idx-1][4] + 60
        while self.temp_label_x < prev_node_x:
            self.temp_label.place_forget()
            self.canvas_make.delete(self.pointing_line_temp)
            self.temp_label_x += 10
            self.pointing_line_temp_left += 10
            self.temp_label.place(x=self.temp_label_x, y=self.temp_label_y)
            self.pointing_line_temp = self.canvas_make.create_line(
                self.pointing_line_temp_left, self.pointing_line_temp_up,
                self.pointing_line_temp_left, self.pointing_line_temp_up + 65, width=2
            )
            time.sleep(0.05)
            self.window.update()
        
        self.information.config(text="temp指针已找到要删除节点的前一个节点")
        time.sleep(0.5)
        
        # 创建曲线连接前一个节点和下一个节点
        prev_node_center_x = self.linked_list_position[idx-1][4] + 50
        prev_node_center_y = self.linked_list_position[idx-1][5] + 32
        next_node_center_x = self.linked_list_position[idx+1][4] + 25
        next_node_center_y = self.linked_list_position[idx+1][5] + 32
        
        # 创建曲线 - 使用更简单的方法确保曲线可见
        # 计算控制点，使曲线向下弯曲
        control_x = (prev_node_center_x + next_node_center_x) / 2
        control_y = max(prev_node_center_y, next_node_center_y) + 80  # 向下弯曲
        
        # 生成曲线点
        curve_points = []
        for t in range(0, 11):
            t_normalized = t / 10.0
            # 二次贝塞尔曲线公式
            x = (1-t_normalized)**2 * prev_node_center_x + 2*(1-t_normalized)*t_normalized * control_x + t_normalized**2 * next_node_center_x
            y = (1-t_normalized)**2 * prev_node_center_y + 2*(1-t_normalized)*t_normalized * control_y + t_normalized**2 * next_node_center_y
            curve_points.extend([x, y])
        
        # 创建曲线，使用更醒目的颜色和更粗的线条
        curve_arrow = self.canvas_make.create_line(
            curve_points, arrow=LAST, width=5, fill="red", smooth=1
        )
        
        self.information.config(text="创建临时曲线连接前一个节点和下一个节点")
        self.window.update()  # 强制更新显示
        time.sleep(1.5)  # 延长显示时间
        
        # 删除可视化元素
        self._remove_visual_elements(idx)
        
        # 删除曲线
        self.canvas_make.delete(curve_arrow)
        
        # 左移后续节点
        self._shift_nodes_left(idx)
        
        # 修正：更新前一个节点的箭头指向下一个节点
        entry = self.linked_list_data_next_store[idx-1]
        prev_arrow_id = entry[1] if len(entry) > 1 else None
        prev_node_x = self.linked_list_position[idx-1][0]
        prev_node_y = self.linked_list_position[idx-1][1]
        
        # 修正：正确的下一个节点位置计算
        if idx < len(self.linked_list_position):
            # 下一个节点的data部分左侧 + 75 (箭头起点到终点的水平距离)
            next_node_x = self.linked_list_position[idx][0] + 75
            next_node_y = self.linked_list_position[idx][1] + 15  # 保持水平
        else:
            # 如果删除的是最后一个节点，指向NULL
            next_node_x = prev_node_x + 115
            next_node_y = prev_node_y + 15
        
        # 创建水平直线箭头
        if prev_arrow_id is not None:
            try:
                # 确保箭头是水平的
                self.canvas_make.coords(prev_arrow_id, 
                                       prev_node_x+75, prev_node_y+15,
                                       next_node_x, next_node_y)
            except Exception as e:
                print(f"更新箭头坐标失败: {e}")
        
        # 移除temp指针
        self.temp_label.place_forget()
        self.canvas_make.delete(self.pointing_line_temp)
        self.temp_label_x = 40
        self.pointing_line_temp_left = 65
        
        self.information.config(text="中间节点已被删除，后续节点已左移")

    def _shift_nodes_left(self, start_idx):
        """将start_idx开始的节点左移，保持间距 - 修复版本"""
        shift_distance = 120  # 节点间距
        
        for i in range(start_idx, len(self.linked_list_position)):
            # 计算新位置
            new_data_x = self.linked_list_position[i][0] - shift_distance
            new_data_y = self.linked_list_position[i][1]
            new_next_x = self.linked_list_position[i][2] - shift_distance
            new_main_x = self.linked_list_position[i][4] - shift_distance
            new_main_y = self.linked_list_position[i][5]
            
            # 更新位置信息
            self.linked_list_position[i] = [
                new_data_x, new_data_y, 
                new_next_x, new_data_y,  # next部分的y坐标与data相同
                new_main_x, new_main_y
            ]
            
            # 移动画布元素
            node_group = self.linked_list_canvas_small_widget[i]
            for element in node_group:
                self.canvas_make.move(element, -shift_distance, 0)
            
            # 移动标签 (安全解包，防止部分条目缺少元素)
            entry = self.linked_list_data_next_store[i]
            value_set = entry[0] if len(entry) > 0 else None
            arrow_id = entry[1] if len(entry) > 1 else None
            next_set = entry[2] if len(entry) > 2 else None
            if value_set is not None:
                value_set.place_configure(x=new_data_x + 8)
            
            # 修正：更新箭头坐标
            if i < len(self.linked_list_data_next_store) - 1:
                # 不是最后一个节点，箭头指向下一个节点
                # 修正：使用正确的坐标计算水平箭头
                next_node_x = self.linked_list_position[i+1][0] + 75  # 下一个节点的data左侧 + 75
                next_node_y = new_data_y + 15  # 保持水平
                
                if arrow_id is not None:
                    try:
                        self.canvas_make.coords(arrow_id, 
                                               new_data_x+75, new_data_y+15,
                                               next_node_x, next_node_y)
                    except Exception as e:
                        print(f"更新箭头坐标失败: {e}")
            else:
                # 最后一个节点，指向NULL - 水平短线
                if arrow_id is not None:
                    try:
                        self.canvas_make.coords(arrow_id, 
                                               new_data_x+75, new_data_y+15,
                                               new_data_x+115, new_data_y+15)
                    except Exception as e:
                        print(f"更新NULL箭头坐标失败: {e}")
                if next_set:
                    try: 
                        next_set.place_configure(x=new_data_x+102)
                    except: 
                        pass
            
            # 更新标签位置
            data_label, next_label = self.linked_list_canvas_small_widget_label[i]
            data_label.place_configure(x=new_data_x)
            next_label.place_configure(x=new_data_x+50)
            
            time.sleep(0.1)
            self.window.update()

    def _remove_visual_elements(self, idx):
        """移除指定索引的可视化元素 - 修复版本"""
        try:
            # 1. 移除数据存储中的元素
            if idx < len(self.linked_list_data_next_store):
                temp1 = self.linked_list_data_next_store.pop(idx)
                for element in temp1:
                    if element is not None:
                        if hasattr(element, 'place_forget'):
                            element.place_forget()
                        elif hasattr(element, 'destroy'):
                            element.destroy()
                        elif hasattr(element, 'delete'):
                            try:
                                self.canvas_make.delete(element)
                            except:
                                pass
            
            # 2. 移除画布元素（矩形等）
            if idx < len(self.linked_list_canvas_small_widget):
                temp2 = self.linked_list_canvas_small_widget.pop(idx)
                for element in temp2:
                    if element is not None:
                        try:
                            self.canvas_make.delete(element)
                        except:
                            pass
            
            # 3. 移除位置信息
            if idx < len(self.linked_list_position):
                self.linked_list_position.pop(idx)
            
            # 4. 移除标签
            if idx < len(self.linked_list_canvas_small_widget_label):
                temp4 = self.linked_list_canvas_small_widget_label.pop(idx)
                for widget_label in temp4:
                    if widget_label is not None:
                        try:
                            widget_label.place_forget()
                            widget_label.destroy()
                        except:
                            pass
            
            # 5. 强制刷新画布，确保所有删除操作生效
            self.canvas_make.update()
            
        except Exception as e:
            print(f"移除可视化元素时出错: {e}")
        
        # 如果链表为空，显示NULL
        if len(self.linked_list_data_next_store) == 0:
            try:
                self.start_initial_point_null.place(x=40, y=300)
            except:
                pass

    def delete_first_node(self):
        """删除第一个节点"""
        if len(self.node_value_store) == 0:
            messagebox.showerror("Underflow", "链表为空")
            return
        self.delete_at_position(1)

    def delete_last_node(self, locator=0):
        """删除最后一个节点"""
        if len(self.node_value_store) == 0:
            messagebox.showerror("Underflow", "链表为空")
            return
        self.delete_at_position(len(self.node_value_store))

    def delete_single_node_infrastructure(self):
        if len(self.node_value_store) == 0:
           self.information.config(text="链表为空  ::  没有节点可删除"); return
        self.information.config(text="第一个节点的位置: 1")
        self.toggle_action_buttons(DISABLED)
        self.position_label = Label(self.window, text="输入要删除的节点的位置", font=("Arial", 13, "bold"), bg="orange", fg="brown")
        self.position_label.place(x=1000, y=620)
        self.position_take_entry = Entry(self.window, font=("Arial", 13, "bold"), bg="white", state=NORMAL, fg="blue", relief=SUNKEN, bd=5, textvar=self.delete_entry)
        self.position_take_entry.place(x=1020, y=650); self.position_take_entry.focus()
        self.find_btn = Button(self.window, text="Find", font=("Arial", 10, "bold"), bg="blue", fg="red", relief=RAISED, bd=3, padx=3, pady=3, state=NORMAL, command=self.delete_single_node)
        self.find_btn.place(x=1230, y=650)

    def delete_single_node(self):
        self.position_label.place_forget(); self.position_take_entry.place_forget(); self.find_btn.place_forget()
        pos = int(self.delete_entry.get())
        self.delete_at_position(pos)

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

    # ========== DSL 直接插入方法 ==========
    
    def _direct_insert_first(self, value):
        """直接头部插入，无需用户交互"""
        self.toggle_action_buttons(DISABLED)
        try:
            self.insert_at_no_animation(1, value)
        except Exception as e:
            print("_direct_insert_first error:", e)
        finally:
            self.toggle_action_buttons(NORMAL)

    def _direct_insert_after(self, position, value):
        """直接在指定位置后插入，无需用户交互"""
        self.toggle_action_buttons(DISABLED)
        try:
            # position argument is expected as 0-based index of an existing node
            insert_pos = int(position) + 1
            self.insert_at_no_animation(insert_pos, value)
        except Exception as e:
            print("_direct_insert_after error:", e)
        finally:
            self.toggle_action_buttons(NORMAL)

    def _create_new_node_visual(self):
        """创建新节点的可视化元素"""
        # 清理可能存在的旧元素
        try:
            self.new_node_label.place_forget()
        except: pass
        try:
            self.data_label.place_forget()
        except: pass
        try:
            self.next_label.place_forget()
        except: pass
        try:
            self.canvas_make.delete(self.data, self.next, self.main_container_node, self.arrow)
        except: pass
        try:
            self.value_set.place_forget()
        except: pass
        try:
            self.next_set.place_forget()
        except: pass

        # 创建新节点
        self.new_node_label = Label(self.canvas_make, text="New node", font=("Arial",13,"bold"), bg="chocolate", fg="green")
        self.new_node_label.place(x=30, y=90)
        self.data = self.make_rect(self.data_left,self.data_up,self.data_left+40,self.data_up+30, outline="green", fill="yellow", width=3)
        self.data_label = Label(self.canvas_make, text="data", font=("Arial",13,"bold"), bg="chocolate", fg="green")
        self.data_label.place(x=self.data_label_x, y=self.data_label_y)
        self.next = self.make_rect(self.data_left+50,self.data_up,self.data_left+90,self.data_up+30, outline="green", fill="yellow", width=3)
        self.next_label = Label(self.canvas_make, text="next", font=("Arial",13,"bold"), bg="chocolate", fg="green")
        self.next_label.place(x=self.data_label_x+50, y=self.data_label_y)
        self.main_container_node = self.make_rect(self.main_node_left, self.main_node_up, self.main_node_left+100, self.main_node_up+65, outline="brown", width=3)
        
        # 设置节点值
        self.value_set = Label(self.canvas_make, text=self.value_entry.get(), font=("Arial", 10, "bold"), fg="green", bg="yellow")
        self.value_set.place(x=self.data_left + 8, y=self.data_up + 3)
        self.arrow = self.canvas_make.create_line(self.data_left+75, self.data_up+15, self.data_left+115, self.data_up+15, width=4)
        self.next_set = Label(self.canvas_make, text="NULL", font=("Arial", 15, "bold"), fg="green", bg="chocolate")
        self.next_set.place(x=self.data_left+102, y=self.data_up + 3)

    def _animate_node_to_position(self, take_notation):
        """将节点动画移动到指定位置"""
        try:
            self.information.config(text=" ")
            self.new_node_label.place_forget()
            try: 
                self.start_initial_point_null.place_forget()
            except: pass

            # 垂直动画 - 节点下落
            while self.main_node_up + 65 < 320:
                self.canvas_make.delete(self.main_container_node, self.data, self.next, self.arrow)
                self.next_label.place_forget()
                self.data_label.place_forget()
                self.value_set.place_forget()
                self.next_set.place_forget()

                self.main_node_up += 10
                self.data_up += 10
                self.data_label_y += 10
                
                self.main_container_node = self.make_rect(self.main_node_left, self.main_node_up, self.main_node_left+100, self.main_node_up+65, outline="brown", width=3)
                self.data = self.make_rect(self.data_left, self.data_up, self.data_left+40, self.data_up+30, outline="green", fill="yellow", width=3)
                self.next = self.make_rect(self.data_left+50, self.data_up, self.data_left+90, self.data_up+30, outline="green", fill="yellow", width=3)
                self.next_label.place(x=self.data_label_x+50, y=self.data_label_y)
                self.data_label.place(x=self.data_label_x, y=self.data_label_y)
                self.value_set.place(x=self.data_left + 8, y=self.data_up + 3)
                self.arrow = self.canvas_make.create_line(self.data_left+75, self.data_up+15, self.data_left+115, self.data_up+15, width=4)
                self.next_set.place(x=self.data_left+102, y=self.data_up + 2)

                time.sleep(0.04)
                self.window.update()

            # 水平移动和指针动画
            if len(self.linked_list_data_next_store) > 1 and (take_notation == 0 or take_notation == 2):
                self.next_set.place_forget()
                self.temp_label.place(x=self.temp_label_x, y=self.temp_label_y)
                self.pointing_line_temp = self.canvas_make.create_line(self.pointing_line_temp_left, self.pointing_line_temp_up,
                                                                       self.pointing_line_temp_left, self.pointing_line_temp_up + 65, width=2)
                
                if take_notation == 2:
                    goto = int(self.position_entry.get()) - 1  # 转换为0-based索引
                    target_x = self.linked_list_position[goto][4] + 120 if goto < len(self.linked_list_position) else self.linked_list_position[-1][4] + 120
                else:
                    goto = len(self.linked_list_position) - 1
                    target_x = self.linked_list_position[goto][4] + 120 if goto >= 0 else 170

                # 指针移动动画
                while self.temp_label_x < target_x:
                    if take_notation == 2:
                        self.information.config(text="遍历直到找到目标节点")
                    else:
                        self.information.config(text="遍历直到找到最后一个节点")
                        
                    self.temp_label.place_forget()
                    self.canvas_make.delete(self.pointing_line_temp, self.temp_pointer)
                    self.temp_label_x += 10
                    self.pointing_line_temp_left += 10
                    self.temp_pointer_left += 10
                    
                    self.temp_pointer = self.make_rect(self.temp_pointer_left, self.temp_pointer_up, self.temp_pointer_left + 30, self.temp_pointer_up + 30, fill="blue", outline="black", width=3)
                    self.temp_label.place(x=self.temp_label_x, y=self.temp_label_y)
                    self.pointing_line_temp = self.canvas_make.create_line(self.pointing_line_temp_left, self.pointing_line_temp_up, self.pointing_line_temp_left, self.pointing_line_temp_up + 65, width=2)
                    
                    time.sleep(0.05)
                    self.window.update()

            # 水平移动节点到最终位置
            if len(self.linked_list_data_next_store) > 0:
                try:
                    if len(self.linked_list_data_next_store[-1]) > 2:
                        self.linked_list_data_next_store[-1][2].place_forget()  # 移除旧的NULL标签
                except: pass
                
                if take_notation == 2:  # 在指定位置后插入
                    target_pos = int(self.position_entry.get())
                    if target_pos < len(self.linked_list_position):
                        target_x = self.linked_list_position[target_pos][4] + 120
                    else:
                        target_x = self.linked_list_position[-1][4] + 120
                else:  # 头部或尾部插入
                    target_x = self.linked_list_position[-1][4] + 120 if self.linked_list_position else 170

                while self.main_node_left < target_x:
                    self.canvas_make.delete(self.main_container_node, self.data, self.next, self.arrow)
                    self.next_label.place_forget()
                    self.data_label.place_forget()
                    self.value_set.place_forget()
                    self.next_set.place_forget()
                    
                    self.main_node_left += 10
                    self.data_left += 10
                    self.data_label_x += 10
                    
                    self.main_container_node = self.make_rect(self.main_node_left, self.main_node_up, self.main_node_left+100, self.main_node_up+65, outline="brown", width=3)
                    self.data = self.make_rect(self.data_left, self.data_up, self.data_left+40, self.data_up+30, outline="green", fill="yellow", width=3)
                    self.next = self.make_rect(self.data_left+50, self.data_up, self.data_left+90, self.data_up+30, outline="green", fill="yellow", width=3)
                    self.next_label.place(x=self.data_label_x+50, y=self.data_label_y)
                    self.data_label.place(x=self.data_label_x, y=self.data_label_y)
                    self.value_set.place(x=self.data_left + 8, y=self.data_up + 3)
                    self.arrow = self.canvas_make.create_line(self.data_left+75, self.data_up+15, self.data_left+115, self.data_up+15, width=4)
                    self.next_set.place(x=self.data_left+102, y=self.data_up + 2)
                    
                    if take_notation == 0:
                        self.information.config(text="新节点已添加到链表的末尾")
                    elif take_notation == 1:
                        self.information.config(text="新节点已添加到链表的头部")
                    elif take_notation == 2:
                        self.information.config(text="新节点已添加到目标节点之后")
                        
                    time.sleep(0.04)
                    self.window.update()

            # 保存节点信息
            self.linked_list_canvas_small_widget_label.append([self.data_label, self.next_label])
            self.linked_list_canvas_small_widget.append([self.data, self.next, self.main_container_node])
            loc = [self.data_left, self.data_up, self.data_left+50, self.data_up, self.main_node_left, self.main_node_up]
            self.linked_list_position.append(loc)
            
            # 清理临时指针
            try:
                self.temp_label.place_forget()
                self.canvas_make.delete(self.pointing_line_temp, self.temp_pointer)
            except: pass
            
            self.temp_label_x = 40
            self.pointing_line_temp_left = 65
            self.temp_pointer_left = 50
            
            # 更新数据结构
            self.reset_with_store(take_notation)
            
        except Exception as e:
            print("_animate_node_to_position error:", e)
            self.toggle_action_buttons(NORMAL)

if __name__ == '__main__':
    window = Tk()
    window.title("Singly Linked List Visualizer")
    window.geometry("1350x730")
    window.maxsize(1350,730)
    window.minsize(1350,730)
    LinkList(window)
    window.mainloop()