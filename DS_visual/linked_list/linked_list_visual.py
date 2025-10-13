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
                        self.information.config(text="New node added to the last node")
                    elif take_notation == 2:
                        self.information.config(text="New node added after the targeting node")
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
                    self.information.config(text="New node added to the last node")
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
        self.node_value_store.append(self.value_entry.get())
        self.linked_list_data_next_store.append([self.value_set, self.arrow, self.next_set])
        print(self.linked_list_data_next_store); print(self.linked_list_canvas_small_widget)
        print(self.linked_list_position); print(self.linked_list_canvas_small_widget_label); print(self.node_value_store)

        try: self.element_take_label.place_forget(); self.value_entry.set(" "); self.element_take_entry.place_forget(); self.add_btn.place_forget()
        except: pass

        if take_notation == 1 and len(self.linked_list_data_next_store) > 1:
            temp_val = self.node_value_store[-1]
            for i in range(len(self.node_value_store)-2, -1, -1):
                self.node_value_store[i+1] = self.node_value_store[i]
            self.node_value_store[0] = temp_val
            for i in range(len(self.node_value_store)):
                self.linked_list_data_next_store[i][0].config(text=self.node_value_store[i])
        if take_notation == 2:
            temp_value = self.node_value_store[-1]
            pos = int(self.position_entry.get())
            for i in range(len(self.node_value_store)-2, pos-1, -1):
                self.node_value_store[i+1] = self.node_value_store[i]
            self.node_value_store[pos] = temp_value
            for i in range(pos, len(self.linked_list_data_next_store)):
                self.linked_list_data_next_store[i][0].config(text=self.node_value_store[i])
        self.reset_coords()
        self.toggle_action_buttons(NORMAL)
        
    def delete_last_node(self, locator):
        print(self.linked_list_data_next_store, self.linked_list_canvas_small_widget, self.linked_list_position, self.linked_list_canvas_small_widget_label, self.node_value_store)
        if len(self.linked_list_data_next_store) == 0:
            messagebox.showerror("Underflow", "Link list is empty"); return
        self.toggle_action_buttons(DISABLED)

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

            for _ in range(3): time.sleep(0.125); self.window.update()
            if locator == 0:
                self.information.config(text="Temp pointing node contains the address that present in the next part of last node and\nand Last node deleted")
            else:
                self.information.config(text="Targeting node deleted")

        if locator == 3:
            self.temp1_pointer = self.make_rect(self.temp_pointer_left+120, self.temp_pointer_up, self.temp_pointer_left + 150, self.temp_pointer_up + 30, fill="blue", outline="black", width=3)
            self.temp1_label.place(x=self.temp_label_x+120, y=self.temp_label_y)
            self.pointing_line_temp1 = self.canvas_make.create_line(self.pointing_line_temp_left+120, self.pointing_line_temp_up, self.pointing_line_temp_left+120, self.pointing_line_temp_up + 65, width=2)
            self.information.config(text="Temp is pointing the penultimate node of the targeting node and \ntemp1 is pointing the targeting node")
            for _ in range(3): time.sleep(2.5); self.window.update()
            for i in range(int(self.delete_entry.get()), len(self.node_value_store)):
                self.linked_list_data_next_store[i-1][0].config(text=self.node_value_store[i])
            for i in range(int(self.delete_entry.get()), len(self.node_value_store)):
                self.node_value_store[i-1] = self.node_value_store[i]
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
            if len(self.linked_list_data_next_store) > 0:
                temp3 = self.linked_list_position[-1]
                self.next_set = Label(self.canvas_make, text="NULL", font=("Arial", 15, "bold"), fg="green", bg="chocolate")
                self.next_set.place(x=temp3[2]+52, y=temp3[3])
                self.linked_list_data_next_store[-1].append(self.next_set)

            temp4 = self.linked_list_canvas_small_widget_label.pop()
            for widget_label in temp4:
                try: widget_label.place_forget()
                except: pass

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
