from tkinter import *
from tkinter import messagebox

# 深色主题颜色常量
THEME_COLORS = {
    "bg_dark": "#0D1117",
    "bg_card": "#161B22",
    "bg_input": "#21262D",
    "neon_cyan": "#00FFE5",
    "neon_pink": "#FF2E97",
    "neon_purple": "#A855F7",
    "neon_blue": "#3B82F6",
    "neon_green": "#10B981",
    "neon_orange": "#F97316",
    "neon_yellow": "#FBBF24",
    "neon_red": "#EF4444",
    "text_primary": "#E6EDF3",
    "text_secondary": "#8B949E",
}
import time
from linked_list.linked_list_model import LinkedListModel
import storage as storage
from llm import function_dispatcher
from linked_list.ui_utils import (
    heading_with_label_subheading, make_start_with_other, make_btn, 
    make_batch_create_ui, draw_gradient, make_enhanced_controls, update_node_counter
)
from linked_list.pseudocode_panel import PseudocodePanel
from linked_list.enhanced_operations import EnhancedLinkedListOperations
from linked_list.animation_effects import AnimationEffects, NodeAnimator
from DSL_utils import process_command

class LinkList:
    def __init__(self, root):
        self.window = root
        self.chat_window = None
        # 使用深色主题背景
        self.window.config(bg="#0D1117")
        self.canvas_width, self.canvas_height = 1350, 500
        self.canvas_make = Canvas(self.window, bg="#0D1117",
                                  width=self.canvas_width, height=self.canvas_height,
                                  relief=FLAT, bd=0, highlightthickness=0)
        self.canvas_make.pack()
        # 使用新的深色渐变背景
        draw_gradient(self.canvas_make, self.canvas_width, self.canvas_height,
                           start_color="#0D1117", end_color="#1A1F36", steps=200)

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
        
        # 初始化伪代码面板（放在画布右侧）
        self.pseudocode_panel = PseudocodePanel(self.window, x=1100, y=95, width=250, height=350)
        
        # 初始化增强功能
        make_enhanced_controls(self)
        
        # 初始化动画效果和增强操作
        self.animation_effects = AnimationEffects(self.canvas_make, self.window)
        self.node_animator = NodeAnimator(self.canvas_make, self.window, self.animation_effects)
        self.enhanced_ops = EnhancedLinkedListOperations(self)

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
        # 注意：不重置 pointing_line_start，保持对画布项目的引用
        if not hasattr(self, 'pointing_line_start'):
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
    
    # ============== 增强指针动画系统 ==============
    
    def create_visual_pointer(self, name, x, y, color=None, direction="down"):
        """
        创建一个可视化指针，包含标签和箭头
        返回: (pointer_line_id, pointer_label, glow_id)
        """
        if color is None:
            color = THEME_COLORS["neon_orange"]
        
        # 创建发光效果背景
        glow_id = self.canvas_make.create_oval(
            x - 8, y - 8, x + 8, y + 8,
            fill="", outline=color, width=2, dash=(3, 3)
        )
        
        # 创建指针线（带箭头）
        if direction == "down":
            pointer_line = self.canvas_make.create_line(
                x, y, x, y + 50,
                width=3, fill=color, arrow="last", arrowshape=(10, 12, 5)
            )
            label_y = y - 25
        else:
            pointer_line = self.canvas_make.create_line(
                x, y, x + 50, y,
                width=3, fill=color, arrow="last", arrowshape=(10, 12, 5)
            )
            label_y = y - 20
        
        # 创建指针标签
        pointer_label = Label(
            self.canvas_make,
            text=name,
            font=("Consolas", 11, "bold"),
            bg=color,
            fg="#000000",
            padx=5, pady=2
        )
        pointer_label.place(x=x - 20, y=label_y)
        
        return pointer_line, pointer_label, glow_id
    
    def move_pointer_to_node(self, pointer_line, pointer_label, glow_id, target_x, target_y, 
                             steps=15, color=None):
        """平滑移动指针到目标位置"""
        if color is None:
            color = THEME_COLORS["neon_orange"]
        
        # 获取当前位置
        try:
            coords = self.canvas_make.coords(pointer_line)
            current_x = coords[0]
            current_y = coords[1]
        except:
            return
        
        dx = (target_x - current_x) / steps
        dy = (target_y - current_y) / steps
        
        for i in range(steps):
            new_x = current_x + dx * (i + 1)
            new_y = current_y + dy * (i + 1)
            
            # 更新指针线
            try:
                self.canvas_make.coords(pointer_line, new_x, new_y, new_x, new_y + 50)
                self.canvas_make.coords(glow_id, new_x - 8, new_y - 8, new_x + 8, new_y + 8)
                pointer_label.place(x=new_x - 20, y=new_y - 25)
            except:
                pass
            
            time.sleep(0.03)
            self.window.update()
    
    def destroy_pointer(self, pointer_line, pointer_label, glow_id):
        """销毁指针"""
        try:
            self.canvas_make.delete(pointer_line)
            self.canvas_make.delete(glow_id)
            pointer_label.destroy()
        except:
            pass
    
    def highlight_node(self, idx, color=None, duration=0.3):
        """高亮显示节点"""
        if color is None:
            color = THEME_COLORS["neon_yellow"]
        
        if idx >= len(self.linked_list_canvas_small_widget):
            return
        
        node_widgets = self.linked_list_canvas_small_widget[idx]
        original_outlines = []
        
        # 保存原始颜色并设置高亮
        for widget in node_widgets:
            try:
                original_outlines.append(self.canvas_make.itemcget(widget, "outline"))
                self.canvas_make.itemconfig(widget, outline=color, width=4)
            except:
                original_outlines.append(None)
        
        self.window.update()
        time.sleep(duration)
        
        # 恢复原始颜色
        for i, widget in enumerate(node_widgets):
            try:
                if original_outlines[i]:
                    self.canvas_make.itemconfig(widget, outline=original_outlines[i], width=3)
            except:
                pass
        
        self.window.update()
    
    def flash_node(self, idx, times=3, color=None):
        """闪烁节点"""
        if color is None:
            color = THEME_COLORS["neon_pink"]
        
        for _ in range(times):
            self.highlight_node(idx, color, 0.15)
            time.sleep(0.1)
    
    def show_operation_step(self, text, highlight_color=None):
        """显示当前操作步骤"""
        if highlight_color is None:
            highlight_color = THEME_COLORS["neon_cyan"]
        
        self.information.config(text=f"▶ {text}", fg=highlight_color)
        self.window.update()
    
    def animate_arrow_redirect(self, from_node_idx, to_x, to_y, color=None):
        """动画显示箭头重定向"""
        if color is None:
            color = THEME_COLORS["neon_green"]
        
        if from_node_idx >= len(self.linked_list_data_next_store):
            return
        
        entry = self.linked_list_data_next_store[from_node_idx]
        arrow_id = entry[1] if len(entry) > 1 else None
        
        if arrow_id is None:
            return
        
        try:
            coords = self.canvas_make.coords(arrow_id)
            start_x, start_y = coords[0], coords[1]
            end_x, end_y = coords[2], coords[3]
            
            # 计算动画步骤
            steps = 20
            dx = (to_x - end_x) / steps
            dy = (to_y - end_y) / steps
            
            # 动画移动箭头终点
            for i in range(steps):
                new_end_x = end_x + dx * (i + 1)
                new_end_y = end_y + dy * (i + 1)
                self.canvas_make.coords(arrow_id, start_x, start_y, new_end_x, new_end_y)
                self.canvas_make.itemconfig(arrow_id, fill=color, width=4)
                time.sleep(0.02)
                self.window.update()
            
            # 恢复正常样式
            self.canvas_make.itemconfig(arrow_id, width=3)
        except Exception as e:
            print(f"箭头重定向动画失败: {e}")
    
    def create_step_indicator(self, step_num, total_steps, description):
        """创建步骤指示器"""
        # 移除旧的指示器
        if hasattr(self, '_step_indicator'):
            try:
                self._step_indicator.destroy()
            except:
                pass
        
        self._step_indicator = Label(
            self.canvas_make,
            text=f"步骤 {step_num}/{total_steps}: {description}",
            font=("Microsoft YaHei UI", 12, "bold"),
            bg=THEME_COLORS["bg_card"],
            fg=THEME_COLORS["neon_cyan"],
            padx=10, pady=5
        )
        self._step_indicator.place(x=20, y=450)
        self.window.update()
    
    def remove_step_indicator(self):
        """移除步骤指示器"""
        if hasattr(self, '_step_indicator'):
            try:
                self._step_indicator.destroy()
            except:
                pass

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
                         "insert_after_node","delete_particular_node","save_btn","load_btn",
                         "search_btn","traverse_btn","reverse_btn","length_btn","memory_btn","clear_btn"):
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

        # 更新start指针指向NULL
        try:
            if self.pointing_line_start:
                self.canvas_make.coords(self.pointing_line_start, 65, 327, 65, 395)
        except: pass
        
        self.reset_coords()
        self.information.config(text="已清空当前可视化")
        
        # 更新节点计数器
        update_node_counter(self)
        
        # 隐藏内存地址（如果显示）
        if hasattr(self, 'memory_addresses_visible') and self.memory_addresses_visible:
            for label in getattr(self, 'memory_labels', []):
                try:
                    label.destroy()
                except:
                    pass
            self.memory_labels = []
            self.memory_addresses_visible = False
            if hasattr(self, 'memory_btn'):
                self.memory_btn.config(text="💾 内存")
        
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
        self.position_label = Label(self.window, text="📍 输入目标节点位置后，将在其后插入新节点",
                                    font=("Microsoft YaHei UI",11,"bold"), bg=THEME_COLORS["bg_card"], fg=THEME_COLORS["neon_orange"])
        self.position_label.place(x=750, y=620)
        self.position_take_entry = Entry(self.window, font=("Consolas", 13, "bold"), bg="#21262D", state=NORMAL,
                                         fg=THEME_COLORS["text_primary"], relief=FLAT, bd=0, insertbackground=THEME_COLORS["neon_cyan"],
                                         textvar=self.position_entry)
        self.position_take_entry.place(x=810, y=650, height=30); self.position_take_entry.focus()
        self.find_btn = Button(self.window, text="🔍 查找", font=("Microsoft YaHei UI", 10, "bold"), 
                               bg=THEME_COLORS["neon_cyan"], fg="#0D1117",
                               relief=FLAT, bd=0, padx=10, pady=5, state=NORMAL, cursor="hand2",
                               command=self.checking_of_existence)
        self.find_btn.place(x=1020, y=648)

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
        
        # 根据插入类型设置伪代码面板
        try:
            if take_notation == 1:  # 头部插入
                self.pseudocode_panel.set_pseudocode("insert_head")
                self.pseudocode_panel.highlight_line(0, "开始头部插入操作")
            elif take_notation == 0:  # 尾部插入
                self.pseudocode_panel.set_pseudocode("insert_tail")
                self.pseudocode_panel.highlight_line(0, "开始尾部插入操作")
            else:  # 指定位置插入
                self.pseudocode_panel.set_pseudocode("insert_at_position")
                self.pseudocode_panel.highlight_line(0, "开始指定位置插入")
        except:
            pass
        
        self.new_node_label = Label(self.canvas_make, text="✨ New Node", font=("Consolas",12,"bold"), bg=THEME_COLORS["bg_card"], fg=THEME_COLORS["neon_cyan"])
        self.new_node_label.place(x=25, y=90)
        self.data = self.make_rect(self.data_left,self.data_up,self.data_left+40,self.data_up+30, outline=THEME_COLORS["neon_cyan"], fill="#1E3A5F", width=2)
        self.data_label = Label(self.canvas_make, text="data", font=("Consolas",11,"bold"), bg=THEME_COLORS["bg_dark"], fg=THEME_COLORS["neon_green"])
        self.data_label.place(x=self.data_label_x, y=self.data_label_y)
        self.next = self.make_rect(self.data_left+50,self.data_up,self.data_left+90,self.data_up+30, outline=THEME_COLORS["neon_cyan"], fill="#1E3A5F", width=2)
        self.next_label = Label(self.canvas_make, text="next", font=("Consolas",11,"bold"), bg=THEME_COLORS["bg_dark"], fg=THEME_COLORS["neon_pink"])
        self.next_label.place(x=self.data_label_x+50, y=self.data_label_y)
        self.main_container_node = self.make_rect(self.main_node_left, self.main_node_up, self.main_node_left+100, self.main_node_up+65, outline=THEME_COLORS["neon_cyan"], width=2)
        self.input_take(take_notation)

    def input_take(self, take_notation):
        self.element_take_label = Label(self.window, text="✏️ 输入节点值", bg=THEME_COLORS["bg_card"], fg=THEME_COLORS["neon_orange"], font=("Microsoft YaHei UI", 11, "bold"))
        self.element_take_label.place(x=10, y=620)
        self.element_take_entry = Entry(self.window, font=("Consolas", 13, "bold"), bg="#21262D", state=NORMAL,
                                        fg=THEME_COLORS["text_primary"], relief=FLAT, bd=0, insertbackground=THEME_COLORS["neon_cyan"],
                                        textvar=self.value_entry)
        self.element_take_entry.place(x=10, y=650, height=30); self.element_take_entry.focus()
        self.add_btn = Button(self.window, text="➕ 添加", font=("Microsoft YaHei UI", 10, "bold"), 
                              bg=THEME_COLORS["neon_green"], fg="#0D1117",
                              relief=FLAT, bd=0, padx=10, pady=5, cursor="hand2",
                              command=lambda: self.make_main_container_with_node_value_set_and_next_arrow_creation(take_notation))
        self.add_btn.place(x=220, y=648)

        if take_notation == 2:
            self.element_take_label.config(text="✏️ 输入新节点值"); self.element_take_label.place(x=810, y=620)
            self.element_take_entry.place(x=810, y=650, height=30); self.add_btn.place(x=1020, y=648)
        elif take_notation == 3:
            self.element_take_label.config(text="✏️ 输入节点位置"); self.element_take_label.place(x=1100, y=620)
            self.element_take_entry.place(x=1100, y=650, height=30); self.add_btn.place(x=1300, y=648)

    def make_main_container_with_node_value_set_and_next_arrow_creation(self, take_notation):
        self.add_btn.config(state=DISABLED)
        self.value_set = Label(self.canvas_make, text=self.value_entry.get(), font=("Consolas", 11, "bold"), fg=THEME_COLORS["neon_yellow"], bg="#1E3A5F")
        self.value_set.place(x=self.data_left + 8, y=self.data_up + 3)
        self.arrow = self.canvas_make.create_line(self.data_left+75, self.data_up+15, self.data_left+115, self.data_up+15, width=3, fill=THEME_COLORS["neon_green"])
        self.next_set = Label(self.canvas_make, text="NULL", font=("Consolas", 12, "bold"), fg=THEME_COLORS["neon_pink"], bg=THEME_COLORS["bg_card"])
        self.next_set.place(x=self.data_left+102, y=self.data_up + 3)
        self.insert_node(take_notation)

    def insert_node(self, take_notation):
        try:
            # 高亮创建节点步骤
            try:
                self.pseudocode_panel.highlight_line(1, "创建新节点 newNode")
            except:
                pass
            
            self.information.config(text="创建新节点，准备插入...")
            self.new_node_label.place_forget()
            try: self.start_initial_point_null.place_forget()
            except: pass

            # 平滑下落动画 - 使用缓动效果
            start_y = self.main_node_up
            target_y = 255  # 目标高度使 main_node_up + 65 = 320
            total_distance = target_y - start_y
            animation_steps = 25
            
            # 使用缓入缓出的缓动函数
            def ease_out_quad(t):
                return t * (2 - t)  # 缓出效果
            
            for step in range(animation_steps + 1):
                t = step / animation_steps
                eased_t = ease_out_quad(t)
                current_y = start_y + total_distance * eased_t
                
                # 计算当前帧的位置
                self.canvas_make.delete(self.main_container_node, self.data, self.next, self.arrow)
                self.next_label.place_forget(); self.data_label.place_forget()
                self.value_set.place_forget(); self.next_set.place_forget()

                self.main_node_up = current_y
                self.data_up = current_y + 30  # data相对于main_node的偏移
                self.data_label_y = current_y + 2
                
                self.main_container_node = self.make_rect(self.main_node_left, self.main_node_up, self.main_node_left+100, self.main_node_up+65, outline=THEME_COLORS["neon_cyan"], width=3)
                self.data = self.make_rect(self.data_left, self.data_up, self.data_left+40, self.data_up+30, outline=THEME_COLORS["neon_cyan"], fill="#1E3A5F", width=3)
                self.next = self.make_rect(self.data_left+50, self.data_up, self.data_left+90, self.data_up+30, outline=THEME_COLORS["neon_cyan"], fill="#1E3A5F", width=3)
                self.next_label.place(x=self.data_label_x+50, y=self.data_label_y); self.data_label.place(x=self.data_label_x, y=self.data_label_y)
                self.value_set.place(x=self.data_left + 8, y=self.data_up + 3)
                self.arrow = self.canvas_make.create_line(self.data_left+75, self.data_up+15, self.data_left+115, self.data_up+15, width=4)
                self.next_set.place(x=self.data_left+102, y=self.data_up + 2)

                time.sleep(0.025); self.window.update()
            
            self.information.config(text="新节点已下落到位")
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
                    self.temp_pointer = self.make_rect(self.temp_pointer_left, self.temp_pointer_up, self.temp_pointer_left + 30, self.temp_pointer_up + 30, fill=THEME_COLORS["neon_cyan"], outline="black", width=3)
                    self.temp_label.place(x=self.temp_label_x, y=self.temp_label_y)
                    self.pointing_line_temp = self.canvas_make.create_line(self.pointing_line_temp_left, self.pointing_line_temp_up, self.pointing_line_temp_left, self.pointing_line_temp_up + 65, width=2)
                    time.sleep(0.05); self.window.update()

            if len(self.linked_list_data_next_store) > 0:
                try:
                    self.linked_list_data_next_store[-1].pop().place_forget()
                except: pass
                
                # 平滑水平移动动画 - 使用缓动效果
                start_x = self.main_node_left
                target_x = self.linked_list_position[-1][4] + 120
                total_distance = target_x - start_x
                animation_steps = 25
                
                # 使用缓入缓出的缓动函数
                def ease_in_out_quad(t):
                    return 2*t*t if t < 0.5 else -1+(4-2*t)*t
                
                self.information.config(text="新节点平滑移动到目标位置...")
                
                for step in range(animation_steps + 1):
                    t = step / animation_steps
                    eased_t = ease_in_out_quad(t)
                    current_x = start_x + total_distance * eased_t
                    
                    self.canvas_make.delete(self.main_container_node, self.data, self.next, self.arrow)
                    self.next_label.place_forget(); self.data_label.place_forget()
                    self.value_set.place_forget(); self.next_set.place_forget()
                    
                    self.main_node_left = current_x
                    self.data_left = current_x + 5  # data相对于main_node的偏移
                    self.data_label_x = current_x + 5
                    
                    self.main_container_node = self.make_rect(self.main_node_left, self.main_node_up, self.main_node_left+100, self.main_node_up+65, outline=THEME_COLORS["neon_cyan"], width=3)
                    self.data = self.make_rect(self.data_left, self.data_up, self.data_left+40, self.data_up+30, outline=THEME_COLORS["neon_cyan"], fill="#1E3A5F", width=3)
                    self.next = self.make_rect(self.data_left+50, self.data_up, self.data_left+90, self.data_up+30, outline=THEME_COLORS["neon_cyan"], fill="#1E3A5F", width=3)
                    self.next_label.place(x=self.data_label_x+50, y=self.data_label_y); self.data_label.place(x=self.data_label_x, y=self.data_label_y)
                    self.value_set.place(x=self.data_left + 8, y=self.data_up + 3)
                    self.arrow = self.canvas_make.create_line(self.data_left+75, self.data_up+15, self.data_left+115, self.data_up+15, width=4)
                    self.next_set.place(x=self.data_left+102, y=self.data_up + 2)
                    
                    if take_notation == 0:
                        self.information.config(text="新节点正在移动到链表末尾...")
                    elif take_notation == 2:
                        self.information.config(text="新节点正在移动到目标位置...")
                    
                    time.sleep(0.025); self.window.update()
                
                if take_notation == 0:
                    self.information.config(text="新节点已添加到链表的末尾")
                elif take_notation == 2:
                    self.information.config(text="新节点已添加到目标节点之后")
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
        
        # 设置伪代码面板显示尾部插入算法
        try:
            self.pseudocode_panel.set_pseudocode("insert_tail")
            self.pseudocode_panel.highlight_line(0, "开始尾部插入操作")
        except:
            pass
        
        try:
            # 高亮创建新节点
            try:
                self.pseudocode_panel.highlight_line(1, "创建新节点 newNode")
            except:
                pass
            
            print(f"DEBUG: Creating new node with value: {value}")
            self.new_node_label = Label(self.canvas_make, text="✨ New Node", font=("Consolas", 12, "bold"), bg=THEME_COLORS["bg_card"], fg=THEME_COLORS["neon_cyan"])
            self.new_node_label.place(x=25, y=90)
            self.data = self.make_rect(self.data_left, self.data_up, self.data_left+40, self.data_up+30, outline=THEME_COLORS["neon_cyan"], fill="#1E3A5F", width=2)
            self.data_label = Label(self.canvas_make, text="data", font=("Consolas", 11, "bold"), bg=THEME_COLORS["bg_dark"], fg=THEME_COLORS["neon_green"])
            self.data_label.place(x=self.data_label_x, y=self.data_label_y)
            self.next = self.make_rect(self.data_left+50, self.data_up, self.data_left+90, self.data_up+30, outline=THEME_COLORS["neon_cyan"], fill="#1E3A5F", width=2)
            self.next_label = Label(self.canvas_make, text="next", font=("Consolas", 11, "bold"), bg=THEME_COLORS["bg_dark"], fg=THEME_COLORS["neon_pink"])
            self.next_label.place(x=self.data_label_x+50, y=self.data_label_y)
            self.main_container_node = self.make_rect(self.main_node_left, self.main_node_up, self.main_node_left + 100, self.main_node_up + 65, outline=THEME_COLORS["neon_cyan"], width=2)
            self.value_set = Label(self.canvas_make, text=str(value), font=("Consolas", 11, "bold"), fg=THEME_COLORS["neon_yellow"], bg="#1E3A5F")
            self.value_set.place(x=self.data_left + 8, y=self.data_up + 3)
            self.arrow = self.canvas_make.create_line(self.data_left+75, self.data_up + 15, self.data_left+115, self.data_up + 15, width=3, fill=THEME_COLORS["neon_green"])
            self.next_set = Label(self.canvas_make, text="NULL", font=("Consolas", 12, "bold"), fg=THEME_COLORS["neon_pink"], bg=THEME_COLORS["bg_card"])
            self.next_set.place(x=self.data_left+102, y=self.data_up + 3)
            
            # 高亮设置数据和next指针
            try:
                self.pseudocode_panel.highlight_line(2, f"设置 newNode->data = {value}")
                self.window.update()
                time.sleep(0.2)
                self.pseudocode_panel.highlight_line(3, "设置 newNode->next = NULL")
            except:
                pass

            # 垂直动画
            self.start_initial_point_null.place_forget()
            
            # 检查链表是否为空
            is_empty = len(self.linked_list_data_next_store) == 0
            try:
                self.pseudocode_panel.highlight_line(4, "检查 head == NULL")
            except:
                pass
            
            while self.main_node_up + 65 < 320:
                self.canvas_make.delete(self.main_container_node, self.data, self.next, self.arrow)
                self.next_label.place_forget(); self.data_label.place_forget()
                self.value_set.place_forget(); self.next_set.place_forget()
                self.main_node_up += 10; self.data_up += 10; self.data_label_y += 10
                self.main_container_node = self.make_rect(self.main_node_left, self.main_node_up, self.main_node_left+100, self.main_node_up+65, outline=THEME_COLORS["neon_cyan"], width=3)
                self.data = self.make_rect(self.data_left, self.data_up, self.data_left+40, self.data_up+30, outline=THEME_COLORS["neon_cyan"], fill="#1E3A5F", width=3)
                self.next = self.make_rect(self.data_left+50, self.data_up, self.data_left+90, self.data_up+30, outline=THEME_COLORS["neon_cyan"], fill="#1E3A5F", width=3)
                self.next_label.place(x=self.data_label_x+50, y=self.data_label_y); self.data_label.place(x=self.data_label_x, y=self.data_label_y)
                self.value_set.place(x=self.data_left + 8, y=self.data_up + 3)
                self.arrow = self.canvas_make.create_line(self.data_left+75, self.data_up + 15, self.data_left+115, self.data_up + 15, width=4)
                self.next_set.place(x=self.data_left+102, y=self.data_up + 2)
                time.sleep(0.04); self.window.update()

            if len(self.linked_list_data_next_store) > 1:
                # 非空链表，需要遍历
                try:
                    self.pseudocode_panel.highlight_line(7, "初始化 temp = head")
                except:
                    pass
                    
                self.next_set.place_forget()
                self.temp_label.place(x=self.temp_label_x, y=self.temp_label_y)
                self.pointing_line_temp = self.canvas_make.create_line(self.pointing_line_temp_left, self.pointing_line_temp_up, self.pointing_line_temp_left, self.pointing_line_temp_up + 65, width=2)
                goto = len(self.linked_list_position) - 2
                
                # 高亮循环遍历
                try:
                    self.pseudocode_panel.highlight_line(8, "while (temp->next != NULL)")
                except:
                    pass
                    
                while self.temp_label_x < self.linked_list_position[goto][4] + 120:
                    # 高亮遍历步骤
                    try:
                        self.pseudocode_panel.highlight_line(9, "temp = temp->next")
                    except:
                        pass
                        
                    self.temp_label.place_forget()
                    self.canvas_make.delete(self.pointing_line_temp, self.temp_pointer)
                    self.temp_label_x += 10; self.pointing_line_temp_left += 10; self.temp_pointer_left += 10
                    self.temp_pointer = self.make_rect(self.temp_pointer_left, self.temp_pointer_up, self.temp_pointer_left + 30, self.temp_pointer_up + 30, fill=THEME_COLORS["neon_cyan"], outline="black", width=3)
                    self.temp_label.place(x=self.temp_label_x, y=self.temp_label_y)
                    self.pointing_line_temp = self.canvas_make.create_line(self.pointing_line_temp_left, self.pointing_line_temp_up, self.pointing_line_temp_left, self.pointing_line_temp_up + 65, width=2)
                    time.sleep(0.05); self.window.update()

            if len(self.linked_list_data_next_store) > 0:
                # 高亮连接新节点
                try:
                    self.pseudocode_panel.highlight_line(11, "temp->next = newNode")
                except:
                    pass
                    
                try: self.linked_list_data_next_store[-1].pop().place_forget()
                except: pass
                while self.main_node_left < self.linked_list_position[-1][4] + 120:
                    self.canvas_make.delete(self.main_container_node, self.data, self.next, self.arrow)
                    self.next_label.place_forget(); self.data_label.place_forget()
                    self.value_set.place_forget(); self.next_set.place_forget()
                    self.main_node_left += 10; self.data_left += 10; self.data_label_x += 10
                    self.main_container_node = self.make_rect(self.main_node_left, self.main_node_up, self.main_node_left+100, self.main_node_up+65, outline=THEME_COLORS["neon_cyan"], width=3)
                    self.data = self.make_rect(self.data_left, self.data_up, self.data_left+40, self.data_up+30, outline=THEME_COLORS["neon_cyan"], fill="#1E3A5F", width=3)
                    self.next = self.make_rect(self.data_left+50, self.data_up, self.data_left+90, self.data_up+30, outline=THEME_COLORS["neon_cyan"], fill="#1E3A5F", width=3)
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
            
            # 更新start指针指向第一个节点
            if len(self.linked_list_position) > 0:
                try:
                    first_node_x = self.linked_list_position[0][4] + 50
                    first_node_y = self.linked_list_position[0][5] + 32
                    if self.pointing_line_start:
                        self.canvas_make.coords(self.pointing_line_start, 65, 327, first_node_x, first_node_y)
                    else:
                        self.pointing_line_start = self.canvas_make.create_line(65, 327, first_node_x, first_node_y, width=2, fill=THEME_COLORS["neon_green"])
                except:
                    pass
            
            # 高亮完成状态
            try:
                self.pseudocode_panel.highlight_line(13, "尾部插入完成！")
            except:
                pass
            
            # 添加成功效果
            try:
                if hasattr(self, 'animation_effects') and self.animation_effects:
                    # 在新插入的节点位置显示成功效果
                    if len(self.linked_list_position) > 0:
                        last_pos = self.linked_list_position[-1]
                        effect_x = last_pos[4] + 50
                        effect_y = last_pos[5] + 32
                        self.animation_effects.create_success_effect(effect_x, effect_y)
                
                # 高亮新插入的节点
                self.highlight_node(len(self.linked_list_position) - 1, THEME_COLORS["neon_green"], 0.5)
            except:
                pass
            
            self.information.config(text=f"节点 {value} 已插入到链表尾部")
            
            # 更新节点计数器
            update_node_counter(self)

        except Exception as e:
            print("programmatic_insert_last error:", e)

    def reset_with_store(self, take_notation):
        # Add the new node's logical value and visual items (they were created at the end)
        self.node_value_store.append(self.value_entry.get())
        self.linked_list_data_next_store.append([self.value_set, self.arrow, self.next_set])
        print(self.linked_list_data_next_store); print(self.linked_list_canvas_small_widget)
        print(self.linked_list_position); print(self.linked_list_canvas_small_widget_label); print(self.node_value_store)
        
        # 更新节点计数器
        update_node_counter(self)

        try:
            self.element_take_label.place_forget(); self.value_entry.set(" "); self.element_take_entry.place_forget(); self.add_btn.place_forget()
        except: pass

        # For insert-at-begin (take_notation == 1) 使用新的平滑动画
        if take_notation == 1 and len(self.linked_list_data_next_store) > 1:
            self._smooth_insert_at_beginning_animation()
            # 重置坐标并返回，动画方法中已处理所有逻辑
            self.reset_coords()
            self.toggle_action_buttons(NORMAL)
            return

        # For insert-at-position (take_notation == 2) 使用平滑动画
        elif take_notation == 2:
            self._smooth_insert_at_position_animation()
            # 重置坐标并返回，动画方法中已处理所有逻辑
            self.reset_coords()
            self.toggle_action_buttons(NORMAL)
            return

        # For insert-at-last (take_notation == 0) 使用平滑动画（当有多个节点时）
        if take_notation == 0 and len(self.linked_list_data_next_store) > 1:
            self._smooth_insert_at_last_animation()
            # 重置坐标并返回
            self.reset_coords()
            self.toggle_action_buttons(NORMAL)
            return

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
            data_rect = self.make_rect(data_left, data_up, data_left + 40, data_up + 30, outline=THEME_COLORS["neon_cyan"], fill="#1E3A5F", width=3)
            data_lbl = Label(self.canvas_make, text="data", font=("Arial",13,"bold"), bg=THEME_COLORS["bg_card"], fg=THEME_COLORS["neon_green"])
            data_lbl.place(x=data_left, y=data_up - 28)
            next_rect = self.make_rect(data_left + 50, data_up, data_left + 90, data_up + 30, outline=THEME_COLORS["neon_cyan"], fill="#1E3A5F", width=3)
            next_lbl = Label(self.canvas_make, text="next", font=("Arial",13,"bold"), bg=THEME_COLORS["bg_card"], fg=THEME_COLORS["neon_green"])
            next_lbl.place(x=data_left + 50, y=data_up - 28)
            main_rect = self.make_rect(node_left, data_up - (self.data_up - self.main_node_up), node_left + 100, data_up - (self.data_up - self.main_node_up) + 65, outline=THEME_COLORS["neon_cyan"], width=3)

            # value label
            value_label = Label(self.canvas_make, text=str(val), font=("Arial",10,"bold"), fg=THEME_COLORS["neon_yellow"], bg="#1E3A5F")
            value_label.place(x=data_left + 8, y=data_up + 3)

            # small arrow (short arrow inside node)
            arrow_id = self.canvas_make.create_line(data_left+75, data_up+15, data_left+115, data_up+15, width=4)

            # next_set label: show NULL only for last node
            next_text = "NULL" if i == n-1 else ""
            next_set = Label(self.canvas_make, text=next_text, font=("Arial",15,"bold"), fg=THEME_COLORS["neon_pink"], bg=THEME_COLORS["bg_card"])
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

    def animate_insert_with_node_movement(self, position, value):
        """在指定位置插入节点，并展示节点移动动画 - 减慢版本"""
        if position < 1 or position > len(self.node_value_store) + 1:
            messagebox.showerror("错误", f"插入位置无效：{position}")
            return
        
        self.toggle_action_buttons(DISABLED)
        
        try:
            # 第一步：创建新节点
            self.information.config(text="创建新节点")
            self._create_temp_node_at_position(600, 100, value)  # 在顶部创建新节点
            
            # 第二步：新节点移动到插入位置
            self.information.config(text="新节点移动到插入位置")
            
            # 计算目标位置
            if position <= len(self.linked_list_position):
                # 在中间插入
                target_x = self.linked_list_position[position-1][4]
            else:
                # 在末尾插入
                target_x = self.linked_list_position[-1][4] + 120 if self.linked_list_position else 170
            
            # 新节点下落动画 - 减慢
            current_y = 100
            target_y = 320
            while current_y < target_y:
                try:
                    self.canvas_make.move(self.temp_main, 0, 5)
                    self.canvas_make.move(self.temp_data, 0, 5)
                    self.canvas_make.move(self.temp_next, 0, 5)
                    self.canvas_make.move(self.temp_inner_arrow, 0, 5)
                    if hasattr(self, 'temp_value') and self.temp_value:
                        self.temp_value.place_configure(y=self.temp_value.winfo_y() + 5)
                    if hasattr(self, 'temp_data_label') and self.temp_data_label:
                        self.temp_data_label.place_configure(y=self.temp_data_label.winfo_y() + 5)
                    if hasattr(self, 'temp_next_label') and self.temp_next_label:
                        self.temp_next_label.place_configure(y=self.temp_next_label.winfo_y() + 5)
                    if hasattr(self, 'temp_node_label') and self.temp_node_label:
                        self.temp_node_label.place_configure(y=self.temp_node_label.winfo_y() + 5)
                except Exception as e:
                    print(f"移动节点时出错: {e}")
                
                current_y += 5
                time.sleep(0.05)  # 增加延迟
                self.window.update()
            
            # 新节点水平移动动画 - 减慢
            current_x = 600
            while current_x > target_x:
                try:
                    self.canvas_make.move(self.temp_main, -5, 0)
                    self.canvas_make.move(self.temp_data, -5, 0)
                    self.canvas_make.move(self.temp_next, -5, 0)
                    self.canvas_make.move(self.temp_inner_arrow, -5, 0)
                    if hasattr(self, 'temp_value') and self.temp_value:
                        self.temp_value.place_configure(x=self.temp_value.winfo_x() - 5)
                    if hasattr(self, 'temp_data_label') and self.temp_data_label:
                        self.temp_data_label.place_configure(x=self.temp_data_label.winfo_x() - 5)
                    if hasattr(self, 'temp_next_label') and self.temp_next_label:
                        self.temp_next_label.place_configure(x=self.temp_next_label.winfo_x() - 5)
                    if hasattr(self, 'temp_node_label') and self.temp_node_label:
                        self.temp_node_label.place_configure(x=self.temp_node_label.winfo_x() - 5)
                except Exception as e:
                    print(f"移动节点时出错: {e}")
                
                current_x -= 5
                time.sleep(0.05)  # 增加延迟
                self.window.update()
            
            # 第三步：后续节点向右移动动画 - 大幅减慢
            if position <= len(self.linked_list_position):
                self.information.config(text="后续节点向右移动，为新节点腾出空间")
                time.sleep(0.5)  # 增加暂停，让用户看清楚
                
                # 计算需要移动的节点数量和距离
                nodes_to_move = len(self.linked_list_position) - position + 1
                total_move_distance = 120  # 每个节点移动的距离
                
                # 分步骤移动所有后续节点 - 大幅减慢
                step_size = 5  # 减小步长
                total_steps = total_move_distance // step_size
                
                for step in range(total_steps):
                    self.information.config(text=f"移动节点中... ({step+1}/{total_steps})")
                    
                    for i in range(position-1, len(self.linked_list_position)):
                        # 移动画布元素
                        node_group = self.linked_list_canvas_small_widget[i]
                        for element in node_group:
                            self.canvas_make.move(element, step_size, 0)
                        
                        # 移动数据标签
                        entry = self.linked_list_data_next_store[i]
                        value_set = entry[0] if len(entry) > 0 else None
                        arrow_id = entry[1] if len(entry) > 1 else None
                        next_set = entry[2] if len(entry) > 2 else None
                        
                        if value_set:
                            value_set.place_configure(x=value_set.winfo_x() + step_size)
                        if next_set:
                            next_set.place_configure(x=next_set.winfo_x() + step_size)
                        
                        # 移动标签
                        labels = self.linked_list_canvas_small_widget_label[i]
                        for label in labels:
                            label.place_configure(x=label.winfo_x() + step_size)
                    
                    # 每移动一步都更新箭头，让箭头跟随节点移动
                    for i in range(len(self.linked_list_data_next_store)):
                        if i < len(self.linked_list_data_next_store) - 1:
                            arrow_id = self.linked_list_data_next_store[i][1]
                            if arrow_id:
                                try:
                                    # 计算当前步骤的临时位置
                                    temp_data_x = self.linked_list_position[i][0] + (step + 1) * step_size
                                    temp_data_y = self.linked_list_position[i][1]
                                    temp_next_data_x = self.linked_list_position[i+1][0] + (step + 1) * step_size
                                    self.canvas_make.coords(arrow_id, 
                                                           temp_data_x+75, temp_data_y+15,
                                                           temp_next_data_x+25, temp_data_y+15)
                                except Exception as e:
                                    print(f"更新箭头失败: {e}")
                    
                    time.sleep(0.1)  # 大幅增加延迟，让动画更慢
                    self.window.update()
                
                # 更新位置信息
                for i in range(position-1, len(self.linked_list_position)):
                    self.linked_list_position[i][0] += total_move_distance
                    self.linked_list_position[i][2] += total_move_distance
                    self.linked_list_position[i][4] += total_move_distance
                
                # 最终更新所有箭头
                for i in range(len(self.linked_list_data_next_store)):
                    if i < len(self.linked_list_data_next_store) - 1:
                        arrow_id = self.linked_list_data_next_store[i][1]
                        if arrow_id:
                            try:
                                data_x = self.linked_list_position[i][0]
                                data_y = self.linked_list_position[i][1]
                                next_data_x = self.linked_list_position[i+1][0]
                                self.canvas_make.coords(arrow_id, 
                                                       data_x+75, data_y+15,
                                                       next_data_x+25, data_y+15)
                            except Exception as e:
                                print(f"更新箭头失败: {e}")
                
                self.information.config(text="节点移动完成")
                time.sleep(0.5)  # 暂停一下，让用户看清楚移动完成
            
            # 第四步：将新节点整合到链表中
            self.information.config(text="将新节点整合到链表中")
            time.sleep(0.5)  # 增加暂停
            
            # 在逻辑存储中插入新值
            self.node_value_store.insert(position-1, str(value))
            
            # 创建永久节点
            data_x = target_x
            data_y = 320
            node_left = data_x - (self.data_left - self.main_node_left)
            
            # 创建节点元素
            data_rect = self.make_rect(data_x, data_y, data_x+40, data_y+30, 
                                      outline=THEME_COLORS["neon_cyan"], fill="#1E3A5F", width=3)
            data_lbl = Label(self.canvas_make, text="data", font=("Arial",13,"bold"), 
                            bg=THEME_COLORS["bg_card"], fg=THEME_COLORS["neon_green"])
            data_lbl.place(x=data_x, y=data_y-28)
            
            next_rect = self.make_rect(data_x+50, data_y, data_x+90, data_y+30, 
                                      outline=THEME_COLORS["neon_cyan"], fill="#1E3A5F", width=3)
            next_lbl = Label(self.canvas_make, text="next", font=("Arial",13,"bold"), 
                            bg=THEME_COLORS["bg_card"], fg=THEME_COLORS["neon_green"])
            next_lbl.place(x=data_x+50, y=data_y-28)
            
            main_rect = self.make_rect(node_left, data_y-30, node_left+100, data_y+35, 
                                      outline=THEME_COLORS["neon_cyan"], width=3)
            
            value_label = Label(self.canvas_make, text=str(value), font=("Arial",10,"bold"), 
                              fg=THEME_COLORS["neon_yellow"], bg="#1E3A5F")
            value_label.place(x=data_x+8, y=data_y+3)
            
            arrow_id = self.canvas_make.create_line(data_x+75, data_y+15, data_x+115, data_y+15, width=4)
            
            # 如果不是最后一个节点，不显示NULL
            next_text = "NULL" if position == len(self.node_value_store) else ""
            next_set = Label(self.canvas_make, text=next_text, font=("Arial",15,"bold"), 
                            fg=THEME_COLORS["neon_pink"], bg=THEME_COLORS["bg_card"])
            next_set.place(x=data_x+102, y=data_y+3)
            
            # 更新存储
            self.linked_list_canvas_small_widget.insert(position-1, [data_rect, next_rect, main_rect])
            self.linked_list_canvas_small_widget_label.insert(position-1, [data_lbl, next_lbl])
            self.linked_list_data_next_store.insert(position-1, [value_label, arrow_id, next_set])
            self.linked_list_position.insert(position-1, [data_x, data_y, data_x+50, data_y, node_left, data_y-30])
            
            # 移除临时节点
            self._remove_temp_node()
            
            # 更新前一个节点的箭头
            if position > 1:
                prev_idx = position - 2
                prev_arrow_id = self.linked_list_data_next_store[prev_idx][1]
                prev_data_x = self.linked_list_position[prev_idx][0]
                prev_data_y = self.linked_list_position[prev_idx][1]
                current_data_x = self.linked_list_position[position-1][0]
                
                if prev_arrow_id:
                    self.canvas_make.coords(prev_arrow_id, 
                                           prev_data_x+75, prev_data_y+15,
                                           current_data_x+25, prev_data_y+15)
            
            # 更新新节点的箭头（如果不是最后一个节点）
            if position < len(self.node_value_store):
                next_data_x = self.linked_list_position[position][0]
                self.canvas_make.coords(arrow_id, 
                                       data_x+75, data_y+15,
                                       next_data_x+25, data_y+15)
            
            self.information.config(text=f"在位置 {position} 插入节点 {value}")
            
        except Exception as e:
            print(f"animate_insert_with_node_movement error: {e}")
            messagebox.showerror("错误", f"插入动画失败：{e}")
        finally:
            self.toggle_action_buttons(NORMAL)

    def enhanced_insert_at_position(self, position, value):
        """增强的插入方法，包含完整的动画效果"""
        if position < 1 or position > len(self.node_value_store) + 1:
            messagebox.showerror("错误", f"插入位置无效：{position}")
            return
        
        # 使用新的动画插入方法
        self.animate_insert_with_node_movement(position, value)

    def animate_insert_between_nodes(self, prev_node_idx, next_node_idx, value):
        """在指定位置之间插入节点的动画 - 修复文字覆盖问题"""
        self.toggle_action_buttons(DISABLED)
        
        try:
            # 获取前后节点的位置信息
            prev_pos = self.linked_list_position[prev_node_idx]
            next_pos = self.linked_list_position[next_node_idx]
            
            # 计算新节点的临时位置（在两个节点之间的上方）
            temp_x = (prev_pos[4] + next_pos[4]) / 2
            temp_y = prev_pos[5] - 100  # 更上方位置，为标签留出空间
            
            # 创建新节点的可视化元素（在临时位置）
            self._create_temp_node_at_position(temp_x, temp_y, value)
            
            # ========== 第一步：新节点指向后一个节点 ==========
            self.information.config(text="第一步：新节点的指针指向后一个节点")
            self.window.update()
            time.sleep(0.8)
            
            # 计算坐标
            new_node_right = temp_x + 95  # 新节点右侧
            new_node_center_y = temp_y + 45
            
            next_node_left = next_pos[4] + 25  # 后一个节点左侧
            next_node_center_y = next_pos[5] + 32
            
            # 创建红色直线箭头 - 新节点指向后一个节点
            temp_arrow = self.canvas_make.create_line(
                new_node_right, new_node_center_y,
                next_node_left, next_node_center_y,
                arrow=LAST, width=4, fill="red", arrowshape=(12, 15, 5)
            )
            
            # 将标签放在箭头上方，避免覆盖
            mid_x = (new_node_right + next_node_left) / 2
            mid_y = (new_node_center_y + next_node_center_y) / 2
            
            arrow_label1 = Label(self.canvas_make, text="新节点→后节点", 
                                font=("Arial", 9, "bold"), bg=THEME_COLORS["bg_card"], fg=THEME_COLORS["neon_pink"],
                                relief="solid", bd=1)
            # 放在箭头上方30像素处
            arrow_label1.place(x=mid_x - 40, y=mid_y - 40)
            
            # 高亮闪烁效果
            for _ in range(3):
                self.canvas_make.itemconfig(temp_arrow, width=6, fill="darkred")
                self.window.update()
                time.sleep(0.2)
                self.canvas_make.itemconfig(temp_arrow, width=4, fill="red")
                self.window.update()
                time.sleep(0.2)
            
            self.window.update()
            time.sleep(0.8)
            
            # ========== 第二步：前一个节点指向新节点 ==========
            self.information.config(text="第二步：前一个节点的指针指向新节点")
            self.window.update()
            time.sleep(0.8)
            
            # 计算坐标
            prev_node_right = prev_pos[4] + 95  # 前一个节点右侧
            prev_node_center_y = prev_pos[5] + 32
            
            new_node_left = temp_x + 25  # 新节点左侧
            new_node_center_y = temp_y + 32
            
            # 创建蓝色直线箭头 - 前一个节点指向新节点
            prev_to_new_arrow = self.canvas_make.create_line(
                prev_node_right, prev_node_center_y,
                new_node_left, new_node_center_y,
                arrow=LAST, width=4, fill=THEME_COLORS["neon_cyan"], arrowshape=(12, 15, 5)
            )
            
            # 计算第二个箭头的中间点
            mid_x2 = (prev_node_right + new_node_left) / 2
            mid_y2 = (prev_node_center_y + new_node_center_y) / 2
            
            # 将第二个标签放在箭头下方，避免覆盖
            arrow_label2 = Label(self.canvas_make, text="前节点→新节点", 
                                font=("Arial", 9, "bold"), bg=THEME_COLORS["bg_card"], fg=THEME_COLORS["neon_cyan"],
                                relief="solid", bd=1)
            # 放在箭头下方30像素处
            arrow_label2.place(x=mid_x2 - 40, y=mid_y2 + 20)
            
            # 高亮闪烁效果
            for _ in range(3):
                self.canvas_make.itemconfig(prev_to_new_arrow, width=6, fill="darkblue")
                self.window.update()
                time.sleep(0.2)
                self.canvas_make.itemconfig(prev_to_new_arrow, width=4, fill=THEME_COLORS["neon_cyan"])
                self.window.update()
                time.sleep(0.2)
            
            self.window.update()
            time.sleep(1.0)
            
            # ========== 第三步：完成插入，显示最终结果 ==========
            self.information.config(text="插入完成！正在更新链表可视化...")
            self.window.update()
            time.sleep(0.5)
            
            # 清理临时图形
            self.canvas_make.delete(temp_arrow)
            self.canvas_make.delete(prev_to_new_arrow)
            arrow_label1.destroy()
            arrow_label2.destroy()
            self._remove_temp_node()
            
            # 显示成功信息
            self.information.config(text=f"在位置 {prev_node_idx + 2} 插入节点 {value}")
            
        except Exception as e:
            print(f"animate_insert_between_nodes error: {e}")
            self.information.config(text="插入动画出现错误")
        finally:
            self.toggle_action_buttons(NORMAL)

    def _create_temp_node_at_position(self, x, y, value):
        """在指定位置创建临时节点 - 修复版本"""
        # 初始化临时节点变量
        self.temp_main = None
        self.temp_data = None
        self.temp_next = None
        self.temp_value = None
        self.temp_data_label = None
        self.temp_next_label = None
        self.temp_node_label = None
        self.temp_inner_arrow = None
        
        # 创建临时节点（使用不同的颜色突出显示）
        self.temp_main = self.make_rect(x, y, x+100, y+65, outline="red", width=3, fill="lightyellow")
        self.temp_data = self.make_rect(x+5, y+30, x+45, y+60, outline=THEME_COLORS["neon_cyan"], fill="lightgreen", width=3)
        self.temp_next = self.make_rect(x+55, y+30, x+95, y+60, outline=THEME_COLORS["neon_cyan"], fill="lightgreen", width=3)
        
        # 显示值（突出显示）
        self.temp_value = Label(self.canvas_make, text=str(value), font=("Arial",10,"bold"), 
                            fg="darkred", bg="lightgreen", relief="solid", bd=1)
        self.temp_value.place(x=x+13, y=y+33)
        
        # 标签
        self.temp_data_label = Label(self.canvas_make, text="data", font=("Arial",10,"bold"), 
                                    bg="#1E3A5F", fg=THEME_COLORS["neon_green"])
        self.temp_data_label.place(x=x+5, y=y+5)
        self.temp_next_label = Label(self.canvas_make, text="next", font=("Arial",10,"bold"), 
                                    bg="#1E3A5F", fg=THEME_COLORS["neon_green"])
        self.temp_next_label.place(x=x+55, y=y+5)
        
        # 在临时节点内部添加一个小箭头
        self.temp_inner_arrow = self.canvas_make.create_line(
            x+75, y+45, x+95, y+45, width=3, fill="black", arrow=LAST
        )
        
        # 添加新节点标签 - 放在节点上方更远的位置
        self.temp_node_label = Label(self.canvas_make, text="✨ 新节点", font=("Consolas",11,"bold"), 
                                    bg=THEME_COLORS["neon_orange"], fg="white", relief="flat", bd=0)
        self.temp_node_label.place(x=x+25, y=y-35)  # 从y-25改为y-35，提供更多空间

    def _remove_temp_node(self):
        """移除临时节点"""
        # 删除画布元素
        for attr in ['temp_main', 'temp_data', 'temp_next', 'temp_inner_arrow']:
            try:
                if hasattr(self, attr) and getattr(self, attr):
                    self.canvas_make.delete(getattr(self, attr))
                    setattr(self, attr, None)
            except:
                pass
        
        # 销毁标签
        for attr in ['temp_value', 'temp_data_label', 'temp_next_label', 'temp_node_label']:
            try:
                if hasattr(self, attr) and getattr(self, attr):
                    getattr(self, attr).destroy()
                    setattr(self, attr, None)
            except:
                pass

    def _smooth_insert_at_beginning_animation(self):
        """头部插入的平滑动画：演示指针变化，然后新节点下落同时后续节点右移"""
        try:
            # 获取新节点的值（刚刚添加到末尾的）
            new_value = self.node_value_store[-1]
            
            # 获取新节点当前的可视化元素（在末尾位置创建的）
            new_visual = self.linked_list_data_next_store[-1]  # [value_set, arrow, next_set]
            new_canvas_group = self.linked_list_canvas_small_widget[-1]  # [data, next, main_container]
            new_labels = self.linked_list_canvas_small_widget_label[-1]  # [data_label, next_label]
            new_pos = self.linked_list_position[-1]  # [data_left, data_up, ...]
            
            # 当前新节点位置
            current_new_x = new_pos[4]  # main_node_left
            current_new_y = new_pos[5]  # main_node_up
            
            # 目标位置是头部位置
            target_x = 25  # self.main_node_left 的初始值
            target_y = current_new_y  # 保持在同一水平线
            
            # 原第一个节点的位置
            first_node_pos = self.linked_list_position[0]
            first_node_x = first_node_pos[4]
            first_node_y = first_node_pos[5]
            
            total_steps = 4
            
            # ========== 步骤1：新节点的next指针指向原头节点 ==========
            self.create_step_indicator(1, total_steps, "设置 newNode->next = head")
            self.show_operation_step("① newNode->next = head  (新节点指向原头节点)")
            
            try:
                self.pseudocode_panel.highlight_line(3, "执行 newNode->next = head")
            except:
                pass
            
            # 高亮新节点
            self.highlight_node(len(self.linked_list_canvas_small_widget) - 1, THEME_COLORS["neon_cyan"], 0.3)
            
            # 创建带动画的箭头 - 从新节点指向原头节点
            new_node_right_x = current_new_x + 95
            new_node_center_y = current_new_y + 32
            first_node_left_x = first_node_x + 25
            first_node_center_y = first_node_y + 32
            
            # 动画绘制箭头
            pointer_arrow = self.canvas_make.create_line(
                new_node_right_x, new_node_center_y,
                new_node_right_x, new_node_center_y,  # 初始长度为0
                arrow="last", width=4, fill=THEME_COLORS["neon_pink"], arrowshape=(12, 15, 5)
            )
            
            # 箭头生长动画
            steps = 20
            for i in range(steps + 1):
                t = i / steps
                current_end_x = new_node_right_x + (first_node_left_x - new_node_right_x) * t
                current_end_y = new_node_center_y + (first_node_center_y - new_node_center_y) * t
                self.canvas_make.coords(pointer_arrow, new_node_right_x, new_node_center_y, current_end_x, current_end_y)
                time.sleep(0.02)
                self.window.update()
            
            # 添加说明标签
            mid_x = (new_node_right_x + first_node_left_x) / 2
            mid_y = min(new_node_center_y, first_node_center_y) - 35
            pointer_label = Label(self.canvas_make, text="🔗 new->next = head", 
                                 font=("Consolas", 10, "bold"), bg=THEME_COLORS["neon_pink"], fg="white",
                                 padx=5, pady=2)
            pointer_label.place(x=mid_x - 60, y=mid_y)
            
            # 高亮原头节点
            self.highlight_node(0, THEME_COLORS["neon_pink"], 0.5)
            time.sleep(0.3)
            
            # ========== 步骤2：head指针指向新节点 ==========
            self.create_step_indicator(2, total_steps, "设置 head = newNode")
            self.show_operation_step("② head = newNode  (头指针指向新节点)")
            
            try:
                self.pseudocode_panel.highlight_line(4, "执行 head = newNode")
            except:
                pass
            
            # 创建新的start指针动画箭头
            start_arrow = self.canvas_make.create_line(
                65, 327, 65, 327,  # 初始长度为0
                arrow="last", width=4, fill=THEME_COLORS["neon_green"], arrowshape=(12, 15, 5), dash=(5, 3)
            )
            
            # start指针动画 - 从当前位置移动到新节点
            target_end_x = current_new_x + 50
            target_end_y = current_new_y + 32
            
            for i in range(steps + 1):
                t = i / steps
                t = t * t * (3 - 2 * t)  # smoothstep
                current_end_x = 65 + (target_end_x - 65) * t
                current_end_y = 327 + (target_end_y - 327) * t
                self.canvas_make.coords(start_arrow, 65, 327, current_end_x, current_end_y)
                time.sleep(0.02)
                self.window.update()
            
            start_label = Label(self.canvas_make, text="📍 head = new", 
                               font=("Consolas", 10, "bold"), bg=THEME_COLORS["neon_green"], fg="white",
                               padx=5, pady=2)
            start_label.place(x=50, y=280)
            
            time.sleep(0.5)
            
            # 清理临时箭头和标签
            self.canvas_make.delete(pointer_arrow)
            self.canvas_make.delete(start_arrow)
            pointer_label.destroy()
            start_label.destroy()
            
            # ========== 步骤3：节点位置调整动画 ==========
            self.create_step_indicator(3, total_steps, "调整节点位置")
            self.show_operation_step("③ 新节点移动到头部位置，原节点右移")
            
            # 计算需要移动的距离
            # 新节点需要向左移动的总距离
            total_x_move = current_new_x - target_x
            # 后续节点需要向右移动的距离（一个节点宽度）
            shift_distance = 120
            
            # 动画步数和每步移动距离
            animation_steps = 30
            new_node_step_x = total_x_move / animation_steps
            other_nodes_step_x = shift_distance / animation_steps
            
            # 同时移动新节点和其他节点
            for step in range(animation_steps):
                # 移动新节点（向左）
                for cid in new_canvas_group:
                    try:
                        self.canvas_make.move(cid, -new_node_step_x, 0)
                    except:
                        pass
                
                # 移动新节点的箭头
                if len(new_visual) > 1 and new_visual[1]:
                    try:
                        self.canvas_make.move(new_visual[1], -new_node_step_x, 0)
                    except:
                        pass
                
                # 移动新节点的标签
                try:
                    new_visual[0].place_configure(x=new_visual[0].winfo_x() - new_node_step_x)  # value_set
                except:
                    pass
                try:
                    new_visual[2].place_configure(x=new_visual[2].winfo_x() - new_node_step_x)  # next_set
                except:
                    pass
                for lbl in new_labels:
                    try:
                        lbl.place_configure(x=lbl.winfo_x() - new_node_step_x)
                    except:
                        pass
                
                # 移动所有其他节点（向右）- 除了最后一个（新节点）
                for i in range(len(self.linked_list_canvas_small_widget) - 1):
                    # 移动画布元素
                    for cid in self.linked_list_canvas_small_widget[i]:
                        try:
                            self.canvas_make.move(cid, other_nodes_step_x, 0)
                        except:
                            pass
                    
                    # 移动箭头
                    entry = self.linked_list_data_next_store[i]
                    if len(entry) > 1 and entry[1]:
                        try:
                            self.canvas_make.move(entry[1], other_nodes_step_x, 0)
                        except:
                            pass
                    
                    # 移动标签
                    if len(entry) > 0 and entry[0]:
                        try:
                            entry[0].place_configure(x=entry[0].winfo_x() + other_nodes_step_x)
                        except:
                            pass
                    if len(entry) > 2 and entry[2]:
                        try:
                            entry[2].place_configure(x=entry[2].winfo_x() + other_nodes_step_x)
                        except:
                            pass
                    
                    # 移动 data/next 标签
                    labels = self.linked_list_canvas_small_widget_label[i]
                    for lbl in labels:
                        try:
                            lbl.place_configure(x=lbl.winfo_x() + other_nodes_step_x)
                        except:
                            pass
                
                time.sleep(0.025)
                self.window.update()
            
            # ========== 步骤4：完成插入 ==========
            self.create_step_indicator(4, total_steps, "头部插入完成")
            
            try:
                self.pseudocode_panel.highlight_line(5, "头部插入完成！")
            except:
                pass
            
            # 更新位置信息
            # 新节点的最终位置
            new_pos[0] = target_x + 5  # data_left
            new_pos[2] = target_x + 55  # next_x
            new_pos[4] = target_x  # main_node_left
            
            # 更新其他节点的位置信息
            for i in range(len(self.linked_list_position) - 1):
                self.linked_list_position[i][0] += shift_distance
                self.linked_list_position[i][2] += shift_distance
                self.linked_list_position[i][4] += shift_distance
            
            # 重要：根据 linked_list_position 重新同步所有被移动节点的标签位置
            for i in range(len(self.linked_list_position) - 1):  # 排除新节点（在末尾）
                try:
                    curr_data_x = self.linked_list_position[i][0]
                    curr_data_y = self.linked_list_position[i][1]
                    
                    entry = self.linked_list_data_next_store[i]
                    if len(entry) > 0 and entry[0]:
                        entry[0].place(x=curr_data_x + 8, y=curr_data_y + 3)
                    if len(entry) > 2 and entry[2]:
                        entry[2].place(x=curr_data_x + 102, y=curr_data_y + 3)
                    
                    labels = self.linked_list_canvas_small_widget_label[i]
                    if len(labels) > 0:
                        labels[0].place(x=curr_data_x, y=curr_data_y - 28)
                    if len(labels) > 1:
                        labels[1].place(x=curr_data_x + 50, y=curr_data_y - 28)
                except:
                    pass
            
            # 重新排列数据结构，将新节点放到开头
            # 从末尾取出新节点的元素
            new_visual_item = self.linked_list_data_next_store.pop()
            new_canvas_item = self.linked_list_canvas_small_widget.pop()
            new_label_item = self.linked_list_canvas_small_widget_label.pop()
            new_pos_item = self.linked_list_position.pop()
            
            # 插入到开头
            self.linked_list_data_next_store.insert(0, new_visual_item)
            self.linked_list_canvas_small_widget.insert(0, new_canvas_item)
            self.linked_list_canvas_small_widget_label.insert(0, new_label_item)
            self.linked_list_position.insert(0, new_pos_item)
            
            # 更新逻辑值存储
            temp_val = self.node_value_store[-1]
            for i in range(len(self.node_value_store) - 2, -1, -1):
                self.node_value_store[i + 1] = self.node_value_store[i]
            self.node_value_store[0] = temp_val
            
            # 更新所有节点的显示值
            for i in range(len(self.node_value_store)):
                try:
                    self.linked_list_data_next_store[i][0].config(text=self.node_value_store[i])
                except:
                    pass
            
            # 更新箭头连接
            for i in range(len(self.linked_list_data_next_store)):
                try:
                    data_x = self.linked_list_position[i][0]
                    data_y = self.linked_list_position[i][1]
                    arrow_id = self.linked_list_data_next_store[i][1]
                    
                    if i < len(self.linked_list_data_next_store) - 1:
                        # 不是最后一个节点，箭头指向下一个节点
                        next_data_x = self.linked_list_position[i + 1][0]
                        self.canvas_make.coords(arrow_id, 
                                               data_x + 75, data_y + 15,
                                               next_data_x + 25, data_y + 15)
                    else:
                        # 最后一个节点，短箭头
                        self.canvas_make.coords(arrow_id,
                                               data_x + 75, data_y + 15,
                                               data_x + 115, data_y + 15)
                except Exception as e:
                    print(f"更新箭头出错: {e}")
            
            # 更新 NULL 标签显示
            for i in range(len(self.linked_list_data_next_store)):
                try:
                    if i == len(self.linked_list_data_next_store) - 1:
                        # 最后一个节点显示 NULL
                        self.linked_list_data_next_store[i][2].config(text="NULL")
                        data_x = self.linked_list_position[i][0]
                        data_y = self.linked_list_position[i][1]
                        self.linked_list_data_next_store[i][2].place(x=data_x + 102, y=data_y + 3)
                    else:
                        # 非最后节点隐藏 NULL
                        self.linked_list_data_next_store[i][2].place_forget()
                except:
                    pass
            
            # 更新 start 指针指向新的头节点
            try:
                first_node_x = self.linked_list_position[0][4] + 50
                first_node_y = self.linked_list_position[0][5] + 32
                self.canvas_make.coords(self.pointing_line_start, 65, 327, first_node_x, first_node_y)
            except:
                pass
            
            self.window.update()
            time.sleep(0.3)
            
            # 移除步骤指示器
            self.remove_step_indicator()
            self.show_operation_step(f"✓ 新节点 {new_value} 已插入到链表头部", THEME_COLORS["neon_green"])
            
        except Exception as e:
            self.remove_step_indicator()
            print(f"_smooth_insert_at_beginning_animation error: {e}")
            import traceback
            traceback.print_exc()

    def _smooth_insert_at_position_animation(self):
        """在指定位置后插入的平滑动画：演示指针变化，然后新节点下落同时后续节点右移"""
        try:
            # 高亮设置数据
            try:
                self.pseudocode_panel.highlight_line(2, "设置 newNode->data")
            except:
                pass
            
            # 获取插入位置
            pos = int(self.position_entry.get())  # 1-based position
            insert_idx = pos  # 在pos位置后插入，即新节点放在index=pos的位置
            
            # 获取新节点的值（刚刚添加到末尾的）
            new_value = self.node_value_store[-1]
            
            # 获取新节点当前的可视化元素（在末尾位置创建的）
            new_visual = self.linked_list_data_next_store[-1]
            new_canvas_group = self.linked_list_canvas_small_widget[-1]
            new_labels = self.linked_list_canvas_small_widget_label[-1]
            new_pos = self.linked_list_position[-1]
            
            # 当前新节点位置
            current_new_x = new_pos[4]
            current_new_y = new_pos[5]
            
            # 计算目标位置（在前一个节点之后）
            if pos <= len(self.linked_list_position) - 1:
                prev_node_pos = self.linked_list_position[pos - 1]
                target_x = prev_node_pos[4] + 120  # 前一个节点右侧
            else:
                target_x = current_new_x  # 在末尾，保持当前位置
            
            target_y = current_new_y
            
            # 前一个节点的位置
            prev_node_pos = self.linked_list_position[pos - 1]
            prev_node_x = prev_node_pos[4]
            prev_node_y = prev_node_pos[5]
            
            # 后一个节点的位置（如果存在）
            has_next_node = pos < len(self.linked_list_position) - 1
            if has_next_node:
                next_node_pos = self.linked_list_position[pos]
                next_node_x = next_node_pos[4]
                next_node_y = next_node_pos[5]
            
            # ========== 第一步：显示指针动画 - 新节点指向后一个节点 ==========
            # 高亮遍历到目标位置
            try:
                self.pseudocode_panel.highlight_lines([7, 8, 9, 10], f"遍历到位置 {pos}")
            except:
                pass
            
            if has_next_node:
                # 高亮 newNode->next = temp->next
                try:
                    self.pseudocode_panel.highlight_line(11, "执行 newNode->next = temp->next")
                except:
                    pass
                
                self.information.config(text="第一步：新节点的next指针指向后一个节点")
                self.window.update()
                time.sleep(0.5)
                
                # 创建红色箭头：新节点 -> 后一个节点
                new_node_right_x = current_new_x + 95
                new_node_center_y = current_new_y + 32
                next_node_left_x = next_node_x + 25
                next_node_center_y = next_node_y + 32
                
                pointer_arrow1 = self.canvas_make.create_line(
                    new_node_right_x, new_node_center_y,
                    next_node_left_x, next_node_center_y,
                    arrow=LAST, width=4, fill="red", arrowshape=(12, 15, 5)
                )
                
                mid_x = (new_node_right_x + next_node_left_x) / 2
                mid_y = min(new_node_center_y, next_node_center_y) - 35
                pointer_label1 = Label(self.canvas_make, text="new->next = 后节点", 
                                      font=("Arial", 10, "bold"), bg=THEME_COLORS["bg_card"], fg=THEME_COLORS["neon_pink"],
                                      relief="solid", bd=1)
                pointer_label1.place(x=mid_x - 60, y=mid_y)
                
                # 闪烁效果
                for _ in range(3):
                    self.canvas_make.itemconfig(pointer_arrow1, width=6, fill="darkred")
                    self.window.update()
                    time.sleep(0.15)
                    self.canvas_make.itemconfig(pointer_arrow1, width=4, fill="red")
                    self.window.update()
                    time.sleep(0.15)
                
                time.sleep(0.5)
            
            # ========== 第二步：显示前一个节点指向新节点 ==========
            # 高亮 temp->next = newNode
            try:
                self.pseudocode_panel.highlight_line(12, "执行 temp->next = newNode")
            except:
                pass
            
            self.information.config(text="第二步：前一个节点的next指针指向新节点")
            self.window.update()
            time.sleep(0.5)
            
            # 创建蓝色箭头：前一个节点 -> 新节点
            prev_node_right_x = prev_node_x + 95
            prev_node_center_y = prev_node_y + 32
            new_node_left_x = current_new_x + 25
            new_node_center_y = current_new_y + 32
            
            pointer_arrow2 = self.canvas_make.create_line(
                prev_node_right_x, prev_node_center_y,
                new_node_left_x, new_node_center_y,
                arrow=LAST, width=4, fill=THEME_COLORS["neon_cyan"], arrowshape=(12, 15, 5)
            )
            
            mid_x2 = (prev_node_right_x + new_node_left_x) / 2
            mid_y2 = min(prev_node_center_y, new_node_center_y) + 40
            pointer_label2 = Label(self.canvas_make, text="前节点->next = new", 
                                  font=("Arial", 10, "bold"), bg=THEME_COLORS["bg_card"], fg=THEME_COLORS["neon_cyan"],
                                  relief="solid", bd=1)
            pointer_label2.place(x=mid_x2 - 60, y=mid_y2)
            
            # 闪烁效果
            for _ in range(3):
                self.canvas_make.itemconfig(pointer_arrow2, width=6, fill="darkblue")
                self.window.update()
                time.sleep(0.15)
                self.canvas_make.itemconfig(pointer_arrow2, width=4, fill=THEME_COLORS["neon_cyan"])
                self.window.update()
                time.sleep(0.15)
            
            time.sleep(0.5)
            
            # 清理临时箭头和标签
            if has_next_node:
                self.canvas_make.delete(pointer_arrow1)
                pointer_label1.destroy()
            self.canvas_make.delete(pointer_arrow2)
            pointer_label2.destroy()
            
            # ========== 第三步：平滑动画 - 新节点移动到目标位置，同时后续节点右移 ==========
            self.information.config(text="第三步：新节点移动到目标位置，后续节点平滑右移")
            self.window.update()
            time.sleep(0.3)
            
            # 计算新节点需要移动的距离
            x_distance = current_new_x - target_x
            
            # 后续节点需要向右移动的距离
            shift_distance = 120
            
            # 动画步数
            animation_steps = 30
            new_node_step_x = x_distance / animation_steps
            other_nodes_step_x = shift_distance / animation_steps
            
            # 需要右移的节点索引（从insert_idx开始到倒数第二个，因为最后一个是新节点）
            nodes_to_shift = list(range(insert_idx, len(self.linked_list_position) - 1))
            
            # 同时移动新节点和后续节点
            for step in range(animation_steps):
                # 移动新节点（向左到目标位置）
                for cid in new_canvas_group:
                    try:
                        self.canvas_make.move(cid, -new_node_step_x, 0)
                    except:
                        pass
                
                # 移动新节点的箭头
                if len(new_visual) > 1 and new_visual[1]:
                    try:
                        self.canvas_make.move(new_visual[1], -new_node_step_x, 0)
                    except:
                        pass
                
                # 移动新节点的标签
                try:
                    new_visual[0].place_configure(x=new_visual[0].winfo_x() - new_node_step_x)
                except:
                    pass
                try:
                    new_visual[2].place_configure(x=new_visual[2].winfo_x() - new_node_step_x)
                except:
                    pass
                for lbl in new_labels:
                    try:
                        lbl.place_configure(x=lbl.winfo_x() - new_node_step_x)
                    except:
                        pass
                
                # 移动需要右移的节点
                for i in nodes_to_shift:
                    # 移动画布元素
                    for cid in self.linked_list_canvas_small_widget[i]:
                        try:
                            self.canvas_make.move(cid, other_nodes_step_x, 0)
                        except:
                            pass
                    
                    # 移动箭头
                    entry = self.linked_list_data_next_store[i]
                    if len(entry) > 1 and entry[1]:
                        try:
                            self.canvas_make.move(entry[1], other_nodes_step_x, 0)
                        except:
                            pass
                    
                    # 移动标签
                    if len(entry) > 0 and entry[0]:
                        try:
                            entry[0].place_configure(x=entry[0].winfo_x() + other_nodes_step_x)
                        except:
                            pass
                    if len(entry) > 2 and entry[2]:
                        try:
                            entry[2].place_configure(x=entry[2].winfo_x() + other_nodes_step_x)
                        except:
                            pass
                    
                    # 移动 data/next 标签
                    labels = self.linked_list_canvas_small_widget_label[i]
                    for lbl in labels:
                        try:
                            lbl.place_configure(x=lbl.winfo_x() + other_nodes_step_x)
                        except:
                            pass
                
                time.sleep(0.025)
                self.window.update()
            
            # ========== 第四步：更新数据结构 ==========
            # 高亮完成
            try:
                self.pseudocode_panel.highlight_line(14, "插入完成！")
            except:
                pass
            
            self.information.config(text="插入完成，更新链表结构...")
            
            # 更新新节点的位置信息
            new_pos[0] = target_x + 5
            new_pos[2] = target_x + 55
            new_pos[4] = target_x
            
            # 更新需要右移的节点的位置信息
            for i in nodes_to_shift:
                self.linked_list_position[i][0] += shift_distance
                self.linked_list_position[i][2] += shift_distance
                self.linked_list_position[i][4] += shift_distance
            
            # 重要：根据 linked_list_position 重新同步被移动节点的标签位置
            for i in nodes_to_shift:
                try:
                    curr_data_x = self.linked_list_position[i][0]
                    curr_data_y = self.linked_list_position[i][1]
                    
                    entry = self.linked_list_data_next_store[i]
                    if len(entry) > 0 and entry[0]:
                        entry[0].place(x=curr_data_x + 8, y=curr_data_y + 3)
                    if len(entry) > 2 and entry[2]:
                        entry[2].place(x=curr_data_x + 102, y=curr_data_y + 3)
                    
                    labels = self.linked_list_canvas_small_widget_label[i]
                    if len(labels) > 0:
                        labels[0].place(x=curr_data_x, y=curr_data_y - 28)
                    if len(labels) > 1:
                        labels[1].place(x=curr_data_x + 50, y=curr_data_y - 28)
                except:
                    pass
            
            # 从末尾取出新节点的元素
            new_visual_item = self.linked_list_data_next_store.pop()
            new_canvas_item = self.linked_list_canvas_small_widget.pop()
            new_label_item = self.linked_list_canvas_small_widget_label.pop()
            new_pos_item = self.linked_list_position.pop()
            
            # 插入到正确的位置
            self.linked_list_data_next_store.insert(insert_idx, new_visual_item)
            self.linked_list_canvas_small_widget.insert(insert_idx, new_canvas_item)
            self.linked_list_canvas_small_widget_label.insert(insert_idx, new_label_item)
            self.linked_list_position.insert(insert_idx, new_pos_item)
            
            # 更新逻辑值存储
            temp_value = self.node_value_store[-1]
            try:
                # 删除末尾的值
                self.node_value_store.pop()
                # 在正确位置插入
                self.node_value_store.insert(insert_idx, temp_value)
            except:
                # 备用方案
                for i in range(len(self.node_value_store) - 2, insert_idx - 1, -1):
                    self.node_value_store[i + 1] = self.node_value_store[i]
                self.node_value_store[insert_idx] = temp_value
            
            # 更新所有节点的显示值
            for i in range(len(self.node_value_store)):
                try:
                    self.linked_list_data_next_store[i][0].config(text=self.node_value_store[i])
                except:
                    pass
            
            # 更新箭头连接
            for i in range(len(self.linked_list_data_next_store)):
                try:
                    data_x = self.linked_list_position[i][0]
                    data_y = self.linked_list_position[i][1]
                    arrow_id = self.linked_list_data_next_store[i][1]
                    
                    if i < len(self.linked_list_data_next_store) - 1:
                        next_data_x = self.linked_list_position[i + 1][0]
                        self.canvas_make.coords(arrow_id, 
                                               data_x + 75, data_y + 15,
                                               next_data_x + 25, data_y + 15)
                    else:
                        self.canvas_make.coords(arrow_id,
                                               data_x + 75, data_y + 15,
                                               data_x + 115, data_y + 15)
                except Exception as e:
                    print(f"更新箭头出错: {e}")
            
            # 更新 NULL 标签显示
            for i in range(len(self.linked_list_data_next_store)):
                try:
                    if i == len(self.linked_list_data_next_store) - 1:
                        self.linked_list_data_next_store[i][2].config(text="NULL")
                        data_x = self.linked_list_position[i][0]
                        data_y = self.linked_list_position[i][1]
                        self.linked_list_data_next_store[i][2].place(x=data_x + 102, y=data_y + 3)
                    else:
                        self.linked_list_data_next_store[i][2].place_forget()
                except:
                    pass
            
            self.window.update()
            time.sleep(0.5)
            self.information.config(text=f"新节点 {new_value} 已插入到位置 {pos} 之后")
            
        except Exception as e:
            print(f"_smooth_insert_at_position_animation error: {e}")
            import traceback
            traceback.print_exc()

    def dsl_insert_at_head_with_smooth_animation(self, value):
        """DSL调用的头部插入完整平滑动画：演示指针变化，新节点下落，后续节点平滑右移"""
        self.toggle_action_buttons(DISABLED)
        
        # 清理可能残留的临时节点和标签
        self._remove_temp_node()
        try:
            if hasattr(self, 'new_node_label') and self.new_node_label:
                self.new_node_label.place_forget()
        except:
            pass
        
        # 设置伪代码面板显示头部插入算法
        self.pseudocode_panel.set_pseudocode("insert_head")
        self.pseudocode_panel.highlight_line(0, "开始头部插入操作")
        
        try:
            n = len(self.node_value_store)
            
            if n == 0:
                # 空链表，直接插入
                self.programmatic_insert_last(value)
                self.pseudocode_panel.highlight_line(5, "插入完成")
                # 添加成功效果
                if hasattr(self, 'animation_effects') and self.animation_effects:
                    self.animation_effects.create_success_effect(100, 430)
                return
            
            # 获取原头节点的位置
            first_pos = self.linked_list_position[0]
            first_node_x = first_pos[4]
            first_node_y = first_pos[5]
            
            # 新节点目标位置是原来的头部位置
            target_x = 25
            target_y = first_node_y
            
            # ========== 第一步：在上方创建临时新节点（带动画效果）==========
            self.pseudocode_panel.highlight_line(1, "创建新节点 newNode")
            self.information.config(text="✨ 创建新节点...")
            temp_start_x = 400  # 在画布中间上方
            temp_start_y = 100
            
            # 添加发光效果
            if hasattr(self, 'animation_effects') and self.animation_effects:
                self.animation_effects.glow_effect(temp_start_x + 50, temp_start_y + 32, radius=60, color="#00FF00", duration=0.3)
            
            self._create_temp_node_at_position(temp_start_x, temp_start_y, value)
            
            # 节点创建缩放动画
            self._animate_node_scale_in(temp_start_x, temp_start_y, value)
            self.window.update()
            time.sleep(0.3)
            
            # 高亮设置数据
            self.pseudocode_panel.highlight_line(2, f"设置 newNode->data = {value}")
            
            # ========== 第二步：显示指针动画 - 新节点指向原头节点 ==========
            self.pseudocode_panel.highlight_line(3, "执行 newNode->next = head")
            self.information.config(text="第一步：新节点的next指针指向原头节点")
            self.window.update()
            time.sleep(0.5)
            
            # 创建红色箭头：新节点 -> 原头节点
            new_node_right_x = temp_start_x + 95
            new_node_center_y = temp_start_y + 45
            first_node_left_x = first_node_x + 25
            first_node_center_y = first_node_y + 32
            
            pointer_arrow1 = self.canvas_make.create_line(
                new_node_right_x, new_node_center_y,
                first_node_left_x, first_node_center_y,
                arrow=LAST, width=4, fill="red", arrowshape=(12, 15, 5)
            )
            
            mid_x = (new_node_right_x + first_node_left_x) / 2
            mid_y = min(new_node_center_y, first_node_center_y) - 35
            pointer_label1 = Label(self.canvas_make, text="new->next = head", 
                                  font=("Arial", 10, "bold"), bg=THEME_COLORS["bg_card"], fg=THEME_COLORS["neon_pink"],
                                  relief="solid", bd=1)
            pointer_label1.place(x=mid_x - 50, y=mid_y)
            
            # 闪烁效果
            for _ in range(3):
                self.canvas_make.itemconfig(pointer_arrow1, width=6, fill="darkred")
                self.window.update()
                time.sleep(0.15)
                self.canvas_make.itemconfig(pointer_arrow1, width=4, fill="red")
                self.window.update()
                time.sleep(0.15)
            
            time.sleep(0.3)
            
            # ========== 第三步：显示start指针将指向新节点 ==========
            self.pseudocode_panel.highlight_line(4, "执行 head = newNode")
            self.information.config(text="第二步：start指针将指向新节点")
            self.window.update()
            time.sleep(0.5)
            
            # 创建蓝色箭头：start -> 新节点
            pointer_arrow2 = self.canvas_make.create_line(
                65, 327,
                temp_start_x + 50, temp_start_y + 32,
                arrow=LAST, width=4, fill=THEME_COLORS["neon_cyan"], arrowshape=(12, 15, 5), dash=(5, 3)
            )
            
            pointer_label2 = Label(self.canvas_make, text="start = new", 
                                  font=("Arial", 10, "bold"), bg=THEME_COLORS["bg_card"], fg=THEME_COLORS["neon_cyan"],
                                  relief="solid", bd=1)
            pointer_label2.place(x=65, y=280)
            
            # 闪烁效果
            for _ in range(3):
                self.canvas_make.itemconfig(pointer_arrow2, width=6, fill="darkblue")
                self.window.update()
                time.sleep(0.15)
                self.canvas_make.itemconfig(pointer_arrow2, width=4, fill=THEME_COLORS["neon_cyan"])
                self.window.update()
                time.sleep(0.15)
            
            time.sleep(0.3)
            
            # 清理临时指针箭头和标签
            self.canvas_make.delete(pointer_arrow1)
            self.canvas_make.delete(pointer_arrow2)
            pointer_label1.destroy()
            pointer_label2.destroy()
            
            # ========== 第四步：平滑动画 - 新节点下落到头部位置，同时后续节点右移 ==========
            self.information.config(text="第三步：新节点移动到头部，后续节点平滑右移")
            self.window.update()
            time.sleep(0.3)
            
            # 计算移动距离
            total_x_move = temp_start_x - target_x
            total_y_move = target_y - temp_start_y
            shift_distance = 120
            
            # 动画步数
            animation_steps = 35
            
            # 使用缓动函数
            def ease_in_out_quad(t):
                return 2*t*t if t < 0.5 else -1+(4-2*t)*t
            
            # 执行平滑动画
            for step in range(animation_steps + 1):
                t = step / animation_steps
                eased_t = ease_in_out_quad(t)
                
                current_x_offset = total_x_move * eased_t
                current_y_offset = total_y_move * eased_t
                
                # 移动临时新节点
                try:
                    new_x = temp_start_x - current_x_offset
                    new_y = temp_start_y + current_y_offset
                    
                    self.canvas_make.delete(self.temp_main)
                    self.canvas_make.delete(self.temp_data)
                    self.canvas_make.delete(self.temp_next)
                    self.canvas_make.delete(self.temp_inner_arrow)
                    
                    self.temp_main = self.make_rect(new_x, new_y, new_x+100, new_y+65, outline="red", width=3, fill="lightyellow")
                    self.temp_data = self.make_rect(new_x+5, new_y+30, new_x+45, new_y+60, outline=THEME_COLORS["neon_cyan"], fill="lightgreen", width=3)
                    self.temp_next = self.make_rect(new_x+55, new_y+30, new_x+95, new_y+60, outline=THEME_COLORS["neon_cyan"], fill="lightgreen", width=3)
                    self.temp_inner_arrow = self.canvas_make.create_line(
                        new_x+75, new_y+45, new_x+95, new_y+45, width=3, fill="black", arrow=LAST
                    )
                    
                    if hasattr(self, 'temp_value') and self.temp_value:
                        self.temp_value.place(x=new_x+13, y=new_y+33)
                    if hasattr(self, 'temp_data_label') and self.temp_data_label:
                        self.temp_data_label.place(x=new_x+5, y=new_y+5)
                    if hasattr(self, 'temp_next_label') and self.temp_next_label:
                        self.temp_next_label.place(x=new_x+55, y=new_y+5)
                    if hasattr(self, 'temp_node_label') and self.temp_node_label:
                        self.temp_node_label.place(x=new_x+30, y=new_y-35)
                except:
                    pass
                
                # 移动所有现有节点向右
                if step > 0:
                    step_shift = shift_distance / animation_steps
                    for i in range(len(self.linked_list_position)):
                        try:
                            for cid in self.linked_list_canvas_small_widget[i]:
                                self.canvas_make.move(cid, step_shift, 0)
                            
                            entry = self.linked_list_data_next_store[i]
                            if len(entry) > 1 and entry[1]:
                                self.canvas_make.move(entry[1], step_shift, 0)
                            if len(entry) > 0 and entry[0]:
                                entry[0].place_configure(x=entry[0].winfo_x() + step_shift)
                            if len(entry) > 2 and entry[2]:
                                entry[2].place_configure(x=entry[2].winfo_x() + step_shift)
                            
                            labels = self.linked_list_canvas_small_widget_label[i]
                            for lbl in labels:
                                lbl.place_configure(x=lbl.winfo_x() + step_shift)
                        except:
                            pass
                
                time.sleep(0.02)
                self.window.update()
            
            # ========== 第五步：更新数据结构 ==========
            self.information.config(text="头部插入完成！")
            
            # 更新所有现有节点的位置信息
            for i in range(len(self.linked_list_position)):
                self.linked_list_position[i][0] += shift_distance
                self.linked_list_position[i][2] += shift_distance
                self.linked_list_position[i][4] += shift_distance
            
            # 重要：根据 linked_list_position 重新同步所有被移动节点的标签位置
            # 这可以修复动画过程中 winfo_x() 累积误差导致的标签位置偏移
            for i in range(len(self.linked_list_position)):
                try:
                    curr_data_x = self.linked_list_position[i][0]
                    curr_data_y = self.linked_list_position[i][1]
                    
                    # 同步值标签位置
                    entry = self.linked_list_data_next_store[i]
                    if len(entry) > 0 and entry[0]:
                        entry[0].place(x=curr_data_x + 8, y=curr_data_y + 3)
                    if len(entry) > 2 and entry[2]:
                        entry[2].place(x=curr_data_x + 102, y=curr_data_y + 3)
                    
                    # 同步 data/next 标签位置
                    labels = self.linked_list_canvas_small_widget_label[i]
                    if len(labels) > 0:
                        labels[0].place(x=curr_data_x, y=curr_data_y - 28)  # data 标签
                    if len(labels) > 1:
                        labels[1].place(x=curr_data_x + 50, y=curr_data_y - 28)  # next 标签
                except Exception as sync_err:
                    print(f"同步标签位置出错: {sync_err}")
            
            # 清理临时节点
            self._remove_temp_node()
            
            # 创建永久节点
            data_x = target_x + 5
            data_y = target_y + 30
            node_left = target_x
            node_up = target_y
            
            data_rect = self.make_rect(data_x, data_y, data_x+40, data_y+30, 
                                      outline=THEME_COLORS["neon_cyan"], fill="#1E3A5F", width=3)
            data_lbl = Label(self.canvas_make, text="data", font=("Arial",13,"bold"), 
                            bg=THEME_COLORS["bg_card"], fg=THEME_COLORS["neon_green"])
            data_lbl.place(x=data_x, y=data_y-28)
            
            next_rect = self.make_rect(data_x+50, data_y, data_x+90, data_y+30, 
                                      outline=THEME_COLORS["neon_cyan"], fill="#1E3A5F", width=3)
            next_lbl = Label(self.canvas_make, text="next", font=("Arial",13,"bold"), 
                            bg=THEME_COLORS["bg_card"], fg=THEME_COLORS["neon_green"])
            next_lbl.place(x=data_x+50, y=data_y-28)
            
            main_rect = self.make_rect(node_left, node_up, node_left+100, node_up+65, 
                                      outline=THEME_COLORS["neon_cyan"], width=3)
            
            value_label = Label(self.canvas_make, text=str(value), font=("Arial",10,"bold"), 
                              fg=THEME_COLORS["neon_yellow"], bg="#1E3A5F")
            value_label.place(x=data_x+8, y=data_y+3)
            
            arrow_id = self.canvas_make.create_line(data_x+75, data_y+15, data_x+115, data_y+15, width=4)
            
            next_set = Label(self.canvas_make, text="", font=("Arial",15,"bold"), 
                            fg=THEME_COLORS["neon_pink"], bg=THEME_COLORS["bg_card"])
            next_set.place(x=data_x+102, y=data_y+3)
            
            # 插入到数据结构的开头
            self.linked_list_canvas_small_widget.insert(0, [data_rect, next_rect, main_rect])
            self.linked_list_canvas_small_widget_label.insert(0, [data_lbl, next_lbl])
            self.linked_list_data_next_store.insert(0, [value_label, arrow_id, next_set])
            self.linked_list_position.insert(0, [data_x, data_y, data_x+50, data_y, node_left, node_up])
            
            # 插入逻辑值
            self.node_value_store.insert(0, str(value))
            
            # 更新所有节点的显示值
            for i in range(len(self.node_value_store)):
                try:
                    self.linked_list_data_next_store[i][0].config(text=self.node_value_store[i])
                except:
                    pass
            
            # 更新箭头连接
            for i in range(len(self.linked_list_data_next_store)):
                try:
                    curr_data_x = self.linked_list_position[i][0]
                    curr_data_y = self.linked_list_position[i][1]
                    curr_arrow_id = self.linked_list_data_next_store[i][1]
                    
                    if i < len(self.linked_list_data_next_store) - 1:
                        next_data_x = self.linked_list_position[i + 1][0]
                        self.canvas_make.coords(curr_arrow_id, 
                                               curr_data_x + 75, curr_data_y + 15,
                                               next_data_x + 25, curr_data_y + 15)
                    else:
                        self.canvas_make.coords(curr_arrow_id,
                                               curr_data_x + 75, curr_data_y + 15,
                                               curr_data_x + 115, curr_data_y + 15)
                except:
                    pass
            
            # 更新 NULL 标签显示
            for i in range(len(self.linked_list_data_next_store)):
                try:
                    if i == len(self.linked_list_data_next_store) - 1:
                        self.linked_list_data_next_store[i][2].config(text="NULL")
                        curr_data_x = self.linked_list_position[i][0]
                        curr_data_y = self.linked_list_position[i][1]
                        self.linked_list_data_next_store[i][2].place(x=curr_data_x + 102, y=curr_data_y + 3)
                    else:
                        self.linked_list_data_next_store[i][2].place_forget()
                except:
                    pass
            
            # 更新start指针
            try:
                first_node_x = self.linked_list_position[0][4] + 50
                first_node_y = self.linked_list_position[0][5] + 32
                self.canvas_make.coords(self.pointing_line_start, 65, 327, first_node_x, first_node_y)
            except:
                pass
            
            self.window.update()
            time.sleep(0.3)
            
            # 高亮完成状态
            self.pseudocode_panel.highlight_line(5, "头部插入完成！")
            self.information.config(text=f"新节点 {value} 已插入到链表头部")
            
            # 添加成功粒子效果
            if hasattr(self, 'animation_effects') and self.animation_effects:
                self.animation_effects.create_success_effect(target_x + 50, target_y + 32)
            
            # 高亮新插入的节点
            self.highlight_node(0, THEME_COLORS["neon_green"], 0.5)
            
        except Exception as e:
            print(f"dsl_insert_at_head_with_smooth_animation error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.toggle_action_buttons(NORMAL)

    def _animate_node_scale_in(self, x, y, value):
        """节点创建时的缩放动画效果"""
        try:
            # 先清理之前的临时节点（包括标签）
            self._remove_temp_node()
            
            # 从小到大的缩放动画
            scales = [0.3, 0.5, 0.7, 0.85, 0.95, 1.0]
            for scale in scales:
                # 删除旧的临时节点画布元素
                try:
                    if hasattr(self, 'temp_main') and self.temp_main:
                        self.canvas_make.delete(self.temp_main)
                    if hasattr(self, 'temp_data') and self.temp_data:
                        self.canvas_make.delete(self.temp_data)
                    if hasattr(self, 'temp_next') and self.temp_next:
                        self.canvas_make.delete(self.temp_next)
                    if hasattr(self, 'temp_inner_arrow') and self.temp_inner_arrow:
                        self.canvas_make.delete(self.temp_inner_arrow)
                except:
                    pass
                
                # 计算缩放后的尺寸
                w = int(100 * scale)
                h = int(65 * scale)
                offset_x = (100 - w) // 2
                offset_y = (65 - h) // 2
                
                new_x = x + offset_x
                new_y = y + offset_y
                
                # 重新创建临时节点
                self.temp_main = self.make_rect(new_x, new_y, new_x + w, new_y + h, 
                                               outline="red", width=3, fill="lightyellow")
                
                if scale >= 0.7:
                    inner_w = int(40 * scale)
                    inner_h = int(30 * scale)
                    self.temp_data = self.make_rect(new_x + 5, new_y + h - inner_h - 5, 
                                                   new_x + 5 + inner_w, new_y + h - 5,
                                                   outline=THEME_COLORS["neon_cyan"], fill="lightgreen", width=3)
                    self.temp_next = self.make_rect(new_x + w - inner_w - 5, new_y + h - inner_h - 5,
                                                   new_x + w - 5, new_y + h - 5,
                                                   outline=THEME_COLORS["neon_cyan"], fill="lightgreen", width=3)
                
                self.window.update()
                time.sleep(0.03)
            
            # 清理缩放动画创建的元素
            try:
                if hasattr(self, 'temp_main') and self.temp_main:
                    self.canvas_make.delete(self.temp_main)
                if hasattr(self, 'temp_data') and self.temp_data:
                    self.canvas_make.delete(self.temp_data)
                if hasattr(self, 'temp_next') and self.temp_next:
                    self.canvas_make.delete(self.temp_next)
                if hasattr(self, 'temp_inner_arrow') and self.temp_inner_arrow:
                    self.canvas_make.delete(self.temp_inner_arrow)
            except:
                pass
            
            # 最终重新创建完整的临时节点
            self._create_temp_node_at_position(x, y, value)
        except Exception as e:
            print(f"Scale animation error: {e}")

    def _animate_traverse_to_position(self, target_idx):
        """动画展示指针从头部遍历到目标位置"""
        if target_idx <= 0 or len(self.linked_list_position) == 0:
            return None, None, None
        
        # 创建遍历指针
        first_x = self.linked_list_position[0][4] + 50
        first_y = self.linked_list_position[0][5] - 30
        traverse_ptr, traverse_label, traverse_glow = self.create_visual_pointer(
            "p", first_x, first_y, THEME_COLORS["neon_orange"]
        )
        
        # 高亮第一个节点
        self.highlight_node(0, THEME_COLORS["neon_orange"], 0.2)
        
        # 遍历到目标位置
        for i in range(min(target_idx, len(self.linked_list_position) - 1)):
            self.information.config(text=f"🔍 遍历中... 当前位置: {i + 1}")
            
            # 高亮当前节点
            self.highlight_node(i, THEME_COLORS["neon_yellow"], 0.15)
            
            # 移动指针到下一个节点
            if i + 1 < len(self.linked_list_position):
                next_x = self.linked_list_position[i + 1][4] + 50
                next_y = self.linked_list_position[i + 1][5] - 30
                self.move_pointer_to_node(traverse_ptr, traverse_label, traverse_glow, next_x, next_y, steps=10)
                
                # 高亮下一个节点
                self.highlight_node(i + 1, THEME_COLORS["neon_orange"], 0.15)
        
        self.information.config(text=f"✓ 已定位到位置 {target_idx}")
        time.sleep(0.2)
        
        return traverse_ptr, traverse_label, traverse_glow

    def _animate_arrow_grow(self, x1, y1, x2, y2, color="red", steps=12):
        """箭头生长动画 - 从起点逐渐延伸到终点"""
        arrow_id = None
        for i in range(1, steps + 1):
            t = i / steps
            # 使用缓动函数使动画更自然
            eased_t = t * t * (3 - 2 * t)  # smoothstep
            
            current_x = x1 + (x2 - x1) * eased_t
            current_y = y1 + (y2 - y1) * eased_t
            
            if arrow_id:
                self.canvas_make.delete(arrow_id)
            
            arrow_id = self.canvas_make.create_line(
                x1, y1, current_x, current_y,
                arrow=LAST, width=4, fill=color, arrowshape=(12, 15, 5)
            )
            self.window.update()
            time.sleep(0.02)
        
        return arrow_id

    def _pulse_arrow(self, arrow_id, times=3):
        """箭头脉冲闪烁效果"""
        original_color = "red"
        for _ in range(times):
            self.canvas_make.itemconfig(arrow_id, width=6, fill="#FF4444")
            self.window.update()
            time.sleep(0.1)
            self.canvas_make.itemconfig(arrow_id, width=4, fill=original_color)
            self.window.update()
            time.sleep(0.1)

    def dsl_insert_at_position_with_smooth_animation(self, pos, value):
        """DSL调用的完整平滑动画插入方法：演示指针变化，新节点下落，后续节点平滑右移"""
        self.toggle_action_buttons(DISABLED)
        
        # 清理可能残留的临时节点和标签
        self._remove_temp_node()
        try:
            if hasattr(self, 'new_node_label') and self.new_node_label:
                self.new_node_label.place_forget()
        except:
            pass
        
        # 设置伪代码面板显示指定位置插入算法
        self.pseudocode_panel.set_pseudocode("insert_at_position")
        self.pseudocode_panel.highlight_line(0, f"开始在位置 {pos} 插入")
        
        traverse_ptr = traverse_label = traverse_glow = None
        
        try:
            # 获取当前链表长度
            n = len(self.node_value_store)
            
            if pos < 1 or pos > n + 1:
                from tkinter import messagebox
                messagebox.showerror("错误", f"位置越界：{pos}")
                return
            
            # 获取前一个节点和后一个节点的位置
            prev_node_idx = pos - 2  # 0-based index
            next_node_idx = pos - 1  # 0-based index
            
            prev_pos = self.linked_list_position[prev_node_idx]
            prev_node_x = prev_pos[4]
            prev_node_y = prev_pos[5]
            
            has_next_node = next_node_idx < len(self.linked_list_position)
            if has_next_node:
                next_pos = self.linked_list_position[next_node_idx]
                next_node_x = next_pos[4]
                next_node_y = next_pos[5]
            
            # 计算新节点的目标位置
            target_x = prev_node_x + 120
            target_y = prev_node_y
            
            # ========== 第一步：遍历动画找到插入位置 ==========
            self.pseudocode_panel.highlight_lines([7, 8, 9, 10], f"遍历到位置 {pos-1}")
            self.information.config(text=f"🔍 开始遍历，查找位置 {pos-1}...")
            self.window.update()
            time.sleep(0.3)
            
            # 执行遍历动画
            traverse_ptr, traverse_label, traverse_glow = self._animate_traverse_to_position(prev_node_idx + 1)
            
            # 高亮前一个节点
            self.highlight_node(prev_node_idx, THEME_COLORS["neon_cyan"], 0.3)
            time.sleep(0.2)
            
            # ========== 第二步：在上方创建临时新节点（带动画效果）==========
            self.pseudocode_panel.highlight_line(1, "创建新节点 newNode")
            self.information.config(text="✨ 创建新节点...")
            temp_start_x = 600  # 在画布中间上方
            temp_start_y = 100
            
            # 添加发光效果
            if hasattr(self, 'animation_effects') and self.animation_effects:
                self.animation_effects.glow_effect(temp_start_x + 50, temp_start_y + 32, radius=60, color="#00FF00", duration=0.3)
            
            self._create_temp_node_at_position(temp_start_x, temp_start_y, value)
            
            # 节点创建缩放动画
            self._animate_node_scale_in(temp_start_x, temp_start_y, value)
            self.window.update()
            time.sleep(0.2)
            
            # 高亮设置数据
            self.pseudocode_panel.highlight_line(2, f"设置 newNode->data = {value}")
            time.sleep(0.2)
            
            if has_next_node:
                self.pseudocode_panel.highlight_line(11, "执行 newNode->next = temp->next")
                self.information.config(text="🔗 新节点的next指针指向后一个节点")
                self.window.update()
                time.sleep(0.3)
                
                # 创建红色箭头：新节点 -> 后一个节点（带生长动画）
                new_node_right_x = temp_start_x + 95
                new_node_center_y = temp_start_y + 45
                next_node_left_x = next_node_x + 25
                next_node_center_y = next_node_y + 32
                
                # 箭头生长动画
                pointer_arrow1 = self._animate_arrow_grow(
                    new_node_right_x, new_node_center_y,
                    next_node_left_x, next_node_center_y,
                    color="red"
                )
                
                mid_x = (new_node_right_x + next_node_left_x) / 2
                mid_y = min(new_node_center_y, next_node_center_y) - 35
                pointer_label1 = Label(self.canvas_make, text="new->next = 后节点", 
                                      font=("Arial", 10, "bold"), bg=THEME_COLORS["bg_card"], fg=THEME_COLORS["neon_pink"],
                                      relief="solid", bd=1)
                pointer_label1.place(x=mid_x - 60, y=mid_y)
                
                # 脉冲闪烁效果
                self._pulse_arrow(pointer_arrow1, 3)
                time.sleep(0.2)
            
            # ========== 第三步：显示前一个节点指向新节点 ==========
            self.pseudocode_panel.highlight_line(12, "执行 temp->next = newNode")
            self.information.config(text="🔗 前一个节点的next指针指向新节点")
            self.window.update()
            time.sleep(0.3)
            
            # 创建蓝色箭头：前一个节点 -> 新节点（带生长动画）
            prev_node_right_x = prev_node_x + 95
            prev_node_center_y = prev_node_y + 32
            new_node_left_x = temp_start_x + 25
            new_node_center_y = temp_start_y + 32
            
            # 箭头生长动画
            pointer_arrow2 = self._animate_arrow_grow(
                prev_node_right_x, prev_node_center_y,
                new_node_left_x, new_node_center_y,
                color=THEME_COLORS["neon_cyan"]
            )
            
            mid_x2 = (prev_node_right_x + new_node_left_x) / 2
            mid_y2 = min(prev_node_center_y, new_node_center_y) + 40
            pointer_label2 = Label(self.canvas_make, text="前节点->next = new", 
                                  font=("Arial", 10, "bold"), bg=THEME_COLORS["bg_card"], fg=THEME_COLORS["neon_cyan"],
                                  relief="solid", bd=1)
            pointer_label2.place(x=mid_x2 - 60, y=mid_y2)
            
            # 脉冲效果
            for _ in range(3):
                self.canvas_make.itemconfig(pointer_arrow2, width=6)
                self.window.update()
                time.sleep(0.1)
                self.canvas_make.itemconfig(pointer_arrow2, width=4)
                self.window.update()
                time.sleep(0.1)
            
            time.sleep(0.2)
            
            # 清理临时指针箭头和标签
            if has_next_node:
                self.canvas_make.delete(pointer_arrow1)
                pointer_label1.destroy()
            self.canvas_make.delete(pointer_arrow2)
            pointer_label2.destroy()
            
            # 销毁遍历指针
            if traverse_ptr:
                self.destroy_pointer(traverse_ptr, traverse_label, traverse_glow)
            
            # ========== 第四步：平滑动画 - 新节点下落并移动到目标位置，同时后续节点右移 ==========
            self.information.config(text="📍 新节点移动到目标位置，后续节点平滑右移")
            self.window.update()
            time.sleep(0.2)
            
            # 计算移动距离
            total_x_move = temp_start_x - target_x  # 新节点水平移动距离
            total_y_move = target_y - temp_start_y  # 新节点垂直移动距离（下落）
            shift_distance = 120  # 后续节点右移距离
            
            # 动画步数
            animation_steps = 35
            new_node_step_x = total_x_move / animation_steps
            new_node_step_y = total_y_move / animation_steps
            other_nodes_step_x = shift_distance / animation_steps
            
            # 需要右移的节点索引
            nodes_to_shift = list(range(next_node_idx, len(self.linked_list_position)))
            
            # 使用缓动函数
            def ease_in_out_quad(t):
                return 2*t*t if t < 0.5 else -1+(4-2*t)*t
            
            # 执行平滑动画
            for step in range(animation_steps + 1):
                t = step / animation_steps
                eased_t = ease_in_out_quad(t)
                
                # 计算当前帧的移动量
                current_x_offset = total_x_move * eased_t
                current_y_offset = total_y_move * eased_t
                current_shift = shift_distance * eased_t
                
                # 移动临时新节点
                try:
                    # 计算新位置
                    new_x = temp_start_x - current_x_offset
                    new_y = temp_start_y + current_y_offset
                    
                    # 删除旧的临时节点
                    self.canvas_make.delete(self.temp_main)
                    self.canvas_make.delete(self.temp_data)
                    self.canvas_make.delete(self.temp_next)
                    self.canvas_make.delete(self.temp_inner_arrow)
                    
                    # 重新创建临时节点在新位置
                    self.temp_main = self.make_rect(new_x, new_y, new_x+100, new_y+65, outline="red", width=3, fill="lightyellow")
                    self.temp_data = self.make_rect(new_x+5, new_y+30, new_x+45, new_y+60, outline=THEME_COLORS["neon_cyan"], fill="lightgreen", width=3)
                    self.temp_next = self.make_rect(new_x+55, new_y+30, new_x+95, new_y+60, outline=THEME_COLORS["neon_cyan"], fill="lightgreen", width=3)
                    self.temp_inner_arrow = self.canvas_make.create_line(
                        new_x+75, new_y+45, new_x+95, new_y+45, width=3, fill="black", arrow=LAST
                    )
                    
                    # 移动标签
                    if hasattr(self, 'temp_value') and self.temp_value:
                        self.temp_value.place(x=new_x+13, y=new_y+33)
                    if hasattr(self, 'temp_data_label') and self.temp_data_label:
                        self.temp_data_label.place(x=new_x+5, y=new_y+5)
                    if hasattr(self, 'temp_next_label') and self.temp_next_label:
                        self.temp_next_label.place(x=new_x+55, y=new_y+5)
                    if hasattr(self, 'temp_node_label') and self.temp_node_label:
                        self.temp_node_label.place(x=new_x+30, y=new_y-35)
                except:
                    pass
                
                # 移动需要右移的现有节点
                if step > 0:  # 从第二帧开始移动现有节点
                    step_shift = other_nodes_step_x
                    for i in nodes_to_shift:
                        try:
                            # 移动画布元素
                            for cid in self.linked_list_canvas_small_widget[i]:
                                self.canvas_make.move(cid, step_shift, 0)
                            
                            # 移动箭头
                            entry = self.linked_list_data_next_store[i]
                            if len(entry) > 1 and entry[1]:
                                self.canvas_make.move(entry[1], step_shift, 0)
                            
                            # 移动标签
                            if len(entry) > 0 and entry[0]:
                                entry[0].place_configure(x=entry[0].winfo_x() + step_shift)
                            if len(entry) > 2 and entry[2]:
                                entry[2].place_configure(x=entry[2].winfo_x() + step_shift)
                            
                            # 移动 data/next 标签
                            labels = self.linked_list_canvas_small_widget_label[i]
                            for lbl in labels:
                                lbl.place_configure(x=lbl.winfo_x() + step_shift)
                        except:
                            pass
                
                time.sleep(0.02)
                self.window.update()
            
            # ========== 第五步：更新数据结构 ==========
            self.information.config(text="插入完成，更新链表结构...")
            
            # 更新被移动节点的位置信息
            for i in nodes_to_shift:
                self.linked_list_position[i][0] += shift_distance
                self.linked_list_position[i][2] += shift_distance
                self.linked_list_position[i][4] += shift_distance
            
            # 重要：根据 linked_list_position 重新同步所有被移动节点的标签位置
            # 这可以修复动画过程中 winfo_x() 累积误差导致的标签位置偏移
            for i in nodes_to_shift:
                try:
                    curr_data_x = self.linked_list_position[i][0]
                    curr_data_y = self.linked_list_position[i][1]
                    
                    # 同步值标签位置
                    entry = self.linked_list_data_next_store[i]
                    if len(entry) > 0 and entry[0]:
                        entry[0].place(x=curr_data_x + 8, y=curr_data_y + 3)
                    if len(entry) > 2 and entry[2]:
                        entry[2].place(x=curr_data_x + 102, y=curr_data_y + 3)
                    
                    # 同步 data/next 标签位置
                    labels = self.linked_list_canvas_small_widget_label[i]
                    if len(labels) > 0:
                        labels[0].place(x=curr_data_x, y=curr_data_y - 28)  # data 标签
                    if len(labels) > 1:
                        labels[1].place(x=curr_data_x + 50, y=curr_data_y - 28)  # next 标签
                except Exception as sync_err:
                    print(f"同步标签位置出错: {sync_err}")
            
            # 清理临时节点
            self._remove_temp_node()
            
            # 创建永久节点
            data_x = target_x + 5
            data_y = target_y + 30
            node_left = target_x
            node_up = target_y
            
            # 创建节点元素
            data_rect = self.make_rect(data_x, data_y, data_x+40, data_y+30, 
                                      outline=THEME_COLORS["neon_cyan"], fill="#1E3A5F", width=3)
            data_lbl = Label(self.canvas_make, text="data", font=("Arial",13,"bold"), 
                            bg=THEME_COLORS["bg_card"], fg=THEME_COLORS["neon_green"])
            data_lbl.place(x=data_x, y=data_y-28)
            
            next_rect = self.make_rect(data_x+50, data_y, data_x+90, data_y+30, 
                                      outline=THEME_COLORS["neon_cyan"], fill="#1E3A5F", width=3)
            next_lbl = Label(self.canvas_make, text="next", font=("Arial",13,"bold"), 
                            bg=THEME_COLORS["bg_card"], fg=THEME_COLORS["neon_green"])
            next_lbl.place(x=data_x+50, y=data_y-28)
            
            main_rect = self.make_rect(node_left, node_up, node_left+100, node_up+65, 
                                      outline=THEME_COLORS["neon_cyan"], width=3)
            
            value_label = Label(self.canvas_make, text=str(value), font=("Arial",10,"bold"), 
                              fg=THEME_COLORS["neon_yellow"], bg="#1E3A5F")
            value_label.place(x=data_x+8, y=data_y+3)
            
            arrow_id = self.canvas_make.create_line(data_x+75, data_y+15, data_x+115, data_y+15, width=4)
            
            # 如果不是最后一个节点，不显示NULL
            is_last = (pos == len(self.node_value_store) + 1)
            next_text = "NULL" if is_last else ""
            next_set = Label(self.canvas_make, text=next_text, font=("Arial",15,"bold"), 
                            fg=THEME_COLORS["neon_pink"], bg=THEME_COLORS["bg_card"])
            next_set.place(x=data_x+102, y=data_y+3)
            
            # 插入到数据结构的正确位置
            insert_idx = pos - 1  # 0-based
            self.linked_list_canvas_small_widget.insert(insert_idx, [data_rect, next_rect, main_rect])
            self.linked_list_canvas_small_widget_label.insert(insert_idx, [data_lbl, next_lbl])
            self.linked_list_data_next_store.insert(insert_idx, [value_label, arrow_id, next_set])
            self.linked_list_position.insert(insert_idx, [data_x, data_y, data_x+50, data_y, node_left, node_up])
            
            # 插入逻辑值
            self.node_value_store.insert(insert_idx, str(value))
            
            # 更新所有节点的显示值
            for i in range(len(self.node_value_store)):
                try:
                    self.linked_list_data_next_store[i][0].config(text=self.node_value_store[i])
                except:
                    pass
            
            # 更新箭头连接
            for i in range(len(self.linked_list_data_next_store)):
                try:
                    curr_data_x = self.linked_list_position[i][0]
                    curr_data_y = self.linked_list_position[i][1]
                    curr_arrow_id = self.linked_list_data_next_store[i][1]
                    
                    if i < len(self.linked_list_data_next_store) - 1:
                        next_data_x = self.linked_list_position[i + 1][0]
                        self.canvas_make.coords(curr_arrow_id, 
                                               curr_data_x + 75, curr_data_y + 15,
                                               next_data_x + 25, curr_data_y + 15)
                    else:
                        self.canvas_make.coords(curr_arrow_id,
                                               curr_data_x + 75, curr_data_y + 15,
                                               curr_data_x + 115, curr_data_y + 15)
                except:
                    pass
            
            # 更新 NULL 标签显示
            for i in range(len(self.linked_list_data_next_store)):
                try:
                    if i == len(self.linked_list_data_next_store) - 1:
                        self.linked_list_data_next_store[i][2].config(text="NULL")
                        curr_data_x = self.linked_list_position[i][0]
                        curr_data_y = self.linked_list_position[i][1]
                        self.linked_list_data_next_store[i][2].place(x=curr_data_x + 102, y=curr_data_y + 3)
                    else:
                        self.linked_list_data_next_store[i][2].place_forget()
                except:
                    pass
            
            self.window.update()
            time.sleep(0.2)
            
            # 高亮完成状态
            self.pseudocode_panel.highlight_line(14, "插入完成！")
            self.information.config(text=f"新节点 {value} 已插入到位置 {pos}")
            
            # 添加成功粒子效果
            if hasattr(self, 'animation_effects') and self.animation_effects:
                insert_idx = pos - 1
                if insert_idx < len(self.linked_list_position):
                    effect_x = self.linked_list_position[insert_idx][4] + 50
                    effect_y = self.linked_list_position[insert_idx][5] + 32
                    self.animation_effects.create_success_effect(effect_x, effect_y)
            
            # 高亮新插入的节点
            insert_idx = pos - 1
            self.highlight_node(insert_idx, THEME_COLORS["neon_green"], 0.5)
            
        except Exception as e:
            print(f"dsl_insert_at_position_with_smooth_animation error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # 确保清理遍历指针
            if traverse_ptr:
                try:
                    self.destroy_pointer(traverse_ptr, traverse_label, traverse_glow)
                except:
                    pass
            self.toggle_action_buttons(NORMAL)

    def _smooth_insert_at_last_animation(self):
        """尾部插入的平滑动画：演示最后一个节点的指针变化，新节点从上方平滑下落"""
        try:
            # 高亮遍历到尾部
            try:
                self.pseudocode_panel.highlight_lines([7, 8, 9, 10], "遍历到链表末尾")
            except:
                pass
            
            # 获取新节点的值（刚刚添加到末尾的）
            new_value = self.node_value_store[-1]
            
            # 新节点是刚添加的，位置在末尾
            new_visual = self.linked_list_data_next_store[-1]
            new_canvas_group = self.linked_list_canvas_small_widget[-1]
            new_labels = self.linked_list_canvas_small_widget_label[-1]
            new_pos = self.linked_list_position[-1]
            
            # 当前新节点位置
            current_new_x = new_pos[4]
            current_new_y = new_pos[5]
            
            # 获取原最后一个节点的位置（现在是倒数第二个）
            # 注意：在调用此方法时，新节点已经被添加到列表末尾
            if len(self.linked_list_position) >= 2:
                prev_last_pos = self.linked_list_position[-2]
                prev_last_x = prev_last_pos[4]
                prev_last_y = prev_last_pos[5]
            else:
                # 只有一个节点（新节点），不需要指针动画
                return
            
            # ========== 第一步：高亮显示原最后节点的NULL将被修改 ==========
            # 高亮 temp->next = newNode
            try:
                self.pseudocode_panel.highlight_line(11, "执行 temp->next = newNode")
            except:
                pass
            
            self.information.config(text="第一步：原最后一个节点的next指针将指向新节点")
            self.window.update()
            time.sleep(0.5)
            
            # 获取原最后节点的NULL标签和箭头
            prev_last_entry = self.linked_list_data_next_store[-2]
            prev_last_null = prev_last_entry[2] if len(prev_last_entry) > 2 else None
            
            # 高亮原NULL标签
            if prev_last_null:
                original_bg = THEME_COLORS["bg_card"]
                for _ in range(3):
                    try:
                        prev_last_null.config(bg=THEME_COLORS["neon_pink"], fg="white")
                        self.window.update()
                        time.sleep(0.15)
                        prev_last_null.config(bg=THEME_COLORS["neon_yellow"], fg="#0D1117")
                        self.window.update()
                        time.sleep(0.15)
                    except:
                        pass
            
            # ========== 第二步：显示指针变化动画 ==========
            self.information.config(text="第二步：原最后节点->next = 新节点")
            self.window.update()
            time.sleep(0.3)
            
            # 创建红色箭头：原最后节点 -> 新节点
            prev_last_right_x = prev_last_x + 95
            prev_last_center_y = prev_last_y + 32
            new_node_left_x = current_new_x + 25
            new_node_center_y = current_new_y + 32
            
            pointer_arrow = self.canvas_make.create_line(
                prev_last_right_x, prev_last_center_y,
                new_node_left_x, new_node_center_y,
                arrow=LAST, width=4, fill=THEME_COLORS["neon_green"], arrowshape=(12, 15, 5)
            )
            
            mid_x = (prev_last_right_x + new_node_left_x) / 2
            mid_y = min(prev_last_center_y, new_node_center_y) - 35
            pointer_label = Label(self.canvas_make, text="last->next = new", 
                                 font=("Arial", 10, "bold"), bg="lightgreen", fg="darkgreen",
                                 relief="solid", bd=1)
            pointer_label.place(x=mid_x - 50, y=mid_y)
            
            # 闪烁效果
            for _ in range(3):
                self.canvas_make.itemconfig(pointer_arrow, width=6, fill="darkgreen")
                self.window.update()
                time.sleep(0.15)
                self.canvas_make.itemconfig(pointer_arrow, width=4, fill=THEME_COLORS["neon_green"])
                self.window.update()
                time.sleep(0.15)
            
            time.sleep(0.5)
            
            # 清理临时箭头和标签
            self.canvas_make.delete(pointer_arrow)
            pointer_label.destroy()
            
            # 隐藏原最后节点的NULL标签
            if prev_last_null:
                try:
                    prev_last_null.place_forget()
                except:
                    pass
            
            # ========== 第三步：更新箭头连接 ==========
            self.information.config(text="尾部插入完成！")
            self.window.update()
            
            # 更新倒数第二个节点（原最后节点）的箭头指向新节点
            prev_last_arrow = prev_last_entry[1] if len(prev_last_entry) > 1 else None
            if prev_last_arrow:
                try:
                    prev_data_x = prev_last_pos[0]
                    prev_data_y = prev_last_pos[1]
                    new_data_x = new_pos[0]
                    self.canvas_make.coords(prev_last_arrow,
                                           prev_data_x + 75, prev_data_y + 15,
                                           new_data_x + 25, prev_data_y + 15)
                    
                    # 短暂高亮新箭头
                    self.canvas_make.itemconfig(prev_last_arrow, width=5, fill=THEME_COLORS["neon_green"])
                    self.window.update()
                    time.sleep(0.3)
                    self.canvas_make.itemconfig(prev_last_arrow, width=4, fill="black")
                except:
                    pass
            
            time.sleep(0.3)
            
            # 高亮完成
            try:
                self.pseudocode_panel.highlight_line(13, "尾部插入完成！")
            except:
                pass
            
            self.information.config(text=f"新节点 {new_value} 已添加到链表末尾")
            
        except Exception as e:
            print(f"_smooth_insert_at_last_animation error: {e}")
            import traceback
            traceback.print_exc()

    def delete_at_position(self, pos):
        """删除指定位置的节点，使用正确的链表删除逻辑"""
        if pos < 1 or pos > len(self.node_value_store):
            messagebox.showerror("错误", f"位置越界：当前链表长度 {len(self.node_value_store)}")
            return
        
        self.toggle_action_buttons(DISABLED)
        
        # 设置伪代码面板显示删除算法
        try:
            self.pseudocode_panel.set_pseudocode("delete_at_position")
            self.pseudocode_panel.highlight_line(0, f"开始删除位置 {pos} 的节点")
        except:
            pass
        
        try:
            # 高亮检查空链表
            try:
                self.pseudocode_panel.highlight_line(1, "检查 head == NULL")
            except:
                pass
            
            # 逻辑删除
            if hasattr(self.model, 'delete_at_position'):
                self.model.delete_at_position(pos)
            else:
                # 备用逻辑删除
                self.node_value_store.pop(pos-1)
            
            # 可视化删除
            idx = pos - 1  # 转换为0-based索引
            
            if pos == 1:  # 删除头节点
                try:
                    self.pseudocode_panel.highlight_line(2, "pos == 1: 删除头节点")
                except:
                    pass
                self._delete_head_node(idx)
            elif pos == len(self.node_value_store) + 1:  # 删除尾节点
                self._delete_tail_node(idx)
            else:  # 删除中间节点
                try:
                    self.pseudocode_panel.highlight_line(6, "删除中间节点")
                except:
                    pass
                self._delete_middle_node_enhanced(idx)
                
            # 更新节点计数器
            update_node_counter(self)
                
        except Exception as e:
            messagebox.showerror("错误", f"删除失败：{e}")
        finally:
            self.toggle_action_buttons(NORMAL)

    def delete_by_value(self, value):
        """按值删除第一个匹配的节点"""
        # 先查找值的位置
        if hasattr(self.model, 'find_value_index'):
            idx = self.model.find_value_index(value)
        else:
            # 备用查找逻辑
            idx = -1
            for i, v in enumerate(self.node_value_store):
                if str(v) == str(value):
                    idx = i
                    break
        
        if idx < 0:
            messagebox.showinfo("提示", f"链表中未找到值 '{value}'")
            return False
        
        # 转换为1-based位置，调用已有的删除方法
        pos = idx + 1
        self.delete_at_position(pos)
        return True

    def insert_before_value(self, target_value, new_value):
        """在第一个值为target_value的节点前面插入new_value"""
        # 先查找目标值的位置
        if hasattr(self.model, 'find_value_index'):
            idx = self.model.find_value_index(target_value)
        else:
            idx = -1
            for i, v in enumerate(self.node_value_store):
                if str(v) == str(target_value):
                    idx = i
                    break
        
        if idx < 0:
            messagebox.showinfo("提示", f"链表中未找到值 '{target_value}'")
            return False
        
        # 转换为1-based位置，调用已有的插入方法
        pos = idx + 1  # 1-based位置，在该位置插入相当于在原节点前面插入
        
        if pos == 1:
            # 头部插入
            if hasattr(self, 'dsl_insert_at_head_with_smooth_animation'):
                self.dsl_insert_at_head_with_smooth_animation(new_value)
            else:
                self._direct_insert_first(new_value)
        else:
            # 中间位置插入
            if hasattr(self, 'dsl_insert_at_position_with_smooth_animation'):
                self.dsl_insert_at_position_with_smooth_animation(pos, new_value)
            else:
                self.insert_at_no_animation(pos, new_value)
        return True

    def insert_after_value(self, target_value, new_value):
        """在第一个值为target_value的节点后面插入new_value"""
        # 先查找目标值的位置
        if hasattr(self.model, 'find_value_index'):
            idx = self.model.find_value_index(target_value)
        else:
            idx = -1
            for i, v in enumerate(self.node_value_store):
                if str(v) == str(target_value):
                    idx = i
                    break
        
        if idx < 0:
            messagebox.showinfo("提示", f"链表中未找到值 '{target_value}'")
            return False
        
        # 转换为1-based位置，在目标节点后面插入
        pos = idx + 2  # 在idx后面插入，即在idx+1位置插入（1-based）
        
        n = len(self.node_value_store)
        if pos > n + 1:
            pos = n + 1
        
        if pos == n + 1:
            # 尾部插入
            self.programmatic_insert_last(new_value)
        else:
            # 中间位置插入
            if hasattr(self, 'dsl_insert_at_position_with_smooth_animation'):
                self.dsl_insert_at_position_with_smooth_animation(pos, new_value)
            else:
                self.insert_at_no_animation(pos, new_value)
        return True

    def insert_between_values(self, value_a, value_b, new_value):
        """在第一个值为value_a和第一个值为value_b的节点之间插入new_value"""
        # 查找两个目标值的位置
        if hasattr(self.model, 'find_value_index'):
            idx_a = self.model.find_value_index(value_a)
            idx_b = self.model.find_value_index(value_b)
        else:
            idx_a = idx_b = -1
            for i, v in enumerate(self.node_value_store):
                if idx_a < 0 and str(v) == str(value_a):
                    idx_a = i
                if idx_b < 0 and str(v) == str(value_b):
                    idx_b = i
                if idx_a >= 0 and idx_b >= 0:
                    break
        
        if idx_a < 0:
            messagebox.showinfo("提示", f"链表中未找到值 '{value_a}'")
            return False
        if idx_b < 0:
            messagebox.showinfo("提示", f"链表中未找到值 '{value_b}'")
            return False
        if idx_a >= idx_b:
            messagebox.showinfo("提示", f"值 '{value_a}' 不在值 '{value_b}' 前面，无法在两者之间插入")
            return False
        
        # 在a后面插入（即在b前面插入），转换为1-based位置
        pos = idx_a + 2  # 在idx_a后面插入
        
        if hasattr(self, 'dsl_insert_at_position_with_smooth_animation'):
            self.dsl_insert_at_position_with_smooth_animation(pos, new_value)
        else:
            self.insert_at_no_animation(pos, new_value)
        return True

    def _delete_head_node(self, idx):
        """删除头节点 - 增强动画版本"""
        
        # ========== 步骤1: 显示temp指针保存头节点 ==========
        self.create_step_indicator(1, 4, "创建temp指针保存头节点")
        self.show_operation_step("temp = head  (保存要删除的节点)")
        
        try:
            self.pseudocode_panel.highlight_line(3, "temp = head")
        except:
            pass
        
        # 创建temp指针指向头节点
        if len(self.linked_list_position) > 0:
            head_x = self.linked_list_position[0][4] + 50
            head_y = self.linked_list_position[0][5] - 30
            temp_ptr, temp_label, temp_glow = self.create_visual_pointer(
                "temp", head_x, head_y, THEME_COLORS["neon_orange"]
            )
            self.highlight_node(0, THEME_COLORS["neon_orange"], 0.5)
            time.sleep(0.5)
        
        # 确保 pointing_line_start 存在
        if not self.pointing_line_start:
            try:
                first_node_x = self.linked_list_position[0][4] + 50
                first_node_y = self.linked_list_position[0][5] + 32
                self.pointing_line_start = self.canvas_make.create_line(
                    65, 327, first_node_x, first_node_y, 
                    width=3, fill=THEME_COLORS["neon_green"], arrow="last"
                )
            except:
                self.pointing_line_start = self.canvas_make.create_line(
                    65, 327, 65, 395, width=3, fill=THEME_COLORS["neon_green"], arrow="last"
                )
        
        # ========== 步骤2: head指针移动到下一个节点 ==========
        if len(self.linked_list_position) > 1:
            self.create_step_indicator(2, 4, "head指针移动到下一个节点")
            self.show_operation_step("head = head->next  (头指针后移)")
            
            try:
                self.pseudocode_panel.highlight_line(4, "head = head->next")
            except:
                pass
            
            second_node_x = self.linked_list_position[1][4] + 50
            second_node_y = self.linked_list_position[1][5] + 32
            
            # 高亮第二个节点
            self.highlight_node(1, THEME_COLORS["neon_green"], 0.3)
            
            # 平滑动画：start指针移动到第二个节点
            try:
                coords = self.canvas_make.coords(self.pointing_line_start)
                start_end_x = coords[2] if len(coords) > 2 else 65
                start_end_y = coords[3] if len(coords) > 3 else 395
            except:
                start_end_x, start_end_y = 65, 395
            
            steps = 20
            for i in range(steps + 1):
                t = i / steps
                # 使用缓动函数
                t = t * t * (3 - 2 * t)
                current_x = start_end_x + (second_node_x - start_end_x) * t
                current_y = start_end_y + (second_node_y - start_end_y) * t
                try:
                    self.canvas_make.coords(self.pointing_line_start, 65, 327, current_x, current_y)
                    # 动画过程中改变颜色
                    self.canvas_make.itemconfig(self.pointing_line_start, fill=THEME_COLORS["neon_cyan"], width=4)
                except:
                    pass
                time.sleep(0.03)
                self.window.update()
            
            # 恢复正常颜色
            try:
                self.canvas_make.itemconfig(self.pointing_line_start, fill=THEME_COLORS["neon_green"], width=3)
            except:
                pass
            
            time.sleep(0.3)
        
        # ========== 步骤3: 删除temp指向的节点 ==========
        self.create_step_indicator(3, 4, "释放temp指向的节点内存")
        self.show_operation_step("delete temp  (删除节点)")
        
        try:
            self.pseudocode_panel.highlight_line(5, "delete temp")
        except:
            pass
        
        # 闪烁要删除的节点
        if len(self.linked_list_canvas_small_widget) > 0:
            self.flash_node(0, 3, THEME_COLORS["neon_red"])
        
        # 销毁temp指针
        if 'temp_ptr' in dir():
            self.destroy_pointer(temp_ptr, temp_label, temp_glow)
        
        # 删除可视化元素
        self._remove_visual_elements(idx)
        time.sleep(0.3)
        
        # ========== 步骤4: 整理节点位置 ==========
        if len(self.linked_list_position) > 0:
            self.create_step_indicator(4, 4, "整理剩余节点位置")
            self.show_operation_step("节点左移，保持连续...")
            self._shift_nodes_left(0)
        
        # 更新start指针最终位置
        if len(self.linked_list_position) > 0:
            first_node_x = self.linked_list_position[0][4] + 50
            first_node_y = self.linked_list_position[0][5] + 32
            try:
                if self.pointing_line_start:
                    self.canvas_make.coords(self.pointing_line_start, 65, 327, first_node_x, first_node_y)
                else:
                    self.pointing_line_start = self.canvas_make.create_line(
                        65, 327, first_node_x, first_node_y, 
                        width=3, fill=THEME_COLORS["neon_green"], arrow="last"
                    )
            except:
                pass
        else:
            # 如果链表为空，start指向NULL
            try:
                if self.pointing_line_start:
                    self.canvas_make.coords(self.pointing_line_start, 65, 327, 65, 395)
                else:
                    self.pointing_line_start = self.canvas_make.create_line(
                        65, 327, 65, 395, width=3, fill=THEME_COLORS["neon_green"], arrow="last"
                    )
            except:
                pass
            self.start_initial_point_null.place(x=40, y=300)
        
        # 完成
        self.remove_step_indicator()
        try:
            self.pseudocode_panel.highlight_line(15, "删除完成！")
        except:
            pass
        
        self.show_operation_step("✓ 头节点已删除", THEME_COLORS["neon_green"])

    def _delete_tail_node(self, idx):
        """删除尾节点 - 增强动画版本"""
        
        temp_ptr = temp_label = temp_glow = None
        
        if idx > 0:  # 确保不是第一个节点
            total_steps = 4
            
            # ========== 步骤1: 创建temp指针从头开始遍历 ==========
            self.create_step_indicator(1, total_steps, "遍历找到倒数第二个节点")
            self.show_operation_step("temp = head; while(temp->next->next != NULL)")
            
            # 创建temp指针
            first_x = self.linked_list_position[0][4] + 50
            first_y = self.linked_list_position[0][5] - 30
            temp_ptr, temp_label, temp_glow = self.create_visual_pointer(
                "temp", first_x, first_y, THEME_COLORS["neon_orange"]
            )
            
            # 遍历到倒数第二个节点
            for i in range(idx - 1):
                self.highlight_node(i, THEME_COLORS["neon_orange"], 0.2)
                if i < idx - 2:
                    next_x = self.linked_list_position[i + 1][4] + 50
                    next_y = self.linked_list_position[i + 1][5] - 30
                    self.move_pointer_to_node(temp_ptr, temp_label, temp_glow, next_x, next_y)
            
            # 最终定位到倒数第二个节点
            target_x = self.linked_list_position[idx - 1][4] + 50
            target_y = self.linked_list_position[idx - 1][5] - 30
            self.move_pointer_to_node(temp_ptr, temp_label, temp_glow, target_x, target_y)
            self.highlight_node(idx - 1, THEME_COLORS["neon_cyan"], 0.5)
            
            time.sleep(0.3)
            
            # ========== 步骤2: 保存要删除的节点 ==========
            self.create_step_indicator(2, total_steps, "找到要删除的尾节点")
            self.show_operation_step("toDelete = temp->next  (标记要删除的节点)")
            
            # 高亮要删除的尾节点
            self.flash_node(idx, 2, THEME_COLORS["neon_red"])
            time.sleep(0.3)
            
            # ========== 步骤3: 修改前驱节点的next指针 ==========
            self.create_step_indicator(3, total_steps, "修改前驱节点的next指针为NULL")
            self.show_operation_step("temp->next = NULL  (断开与尾节点的连接)")
            
            # 动画：箭头缩短变为指向NULL
            entry = self.linked_list_data_next_store[idx - 1]
            prev_arrow_id = entry[1] if len(entry) > 1 else None
            data_x = self.linked_list_position[idx - 1][0]
            data_y = self.linked_list_position[idx - 1][1]
            
            if prev_arrow_id is not None:
                try:
                    # 动画缩短箭头
                    coords = self.canvas_make.coords(prev_arrow_id)
                    start_x, start_y = coords[0], coords[1]
                    end_x = coords[2]
                    target_end_x = data_x + 115
                    
                    steps = 15
                    for i in range(steps + 1):
                        t = i / steps
                        current_end_x = end_x + (target_end_x - end_x) * t
                        self.canvas_make.coords(prev_arrow_id, start_x, start_y, current_end_x, start_y)
                        self.canvas_make.itemconfig(prev_arrow_id, fill=THEME_COLORS["neon_pink"], width=4)
                        time.sleep(0.02)
                        self.window.update()
                    
                    self.canvas_make.itemconfig(prev_arrow_id, fill="black", width=3)
                except:
                    pass
            
            # 更新NULL标签
            old_null = entry[2] if len(entry) > 2 else None
            if old_null:
                try:
                    old_null.destroy()
                except:
                    pass
            
            new_null = Label(
                self.canvas_make, text="NULL",
                font=("Consolas", 12, "bold"),
                fg=THEME_COLORS["neon_pink"],
                bg=THEME_COLORS["bg_card"]
            )
            new_null.place(x=data_x + 102, y=data_y + 3)
            
            # 写回到结构
            try:
                if len(entry) > 2:
                    self.linked_list_data_next_store[idx - 1][2] = new_null
                else:
                    while len(self.linked_list_data_next_store[idx - 1]) < 3:
                        self.linked_list_data_next_store[idx - 1].append(None)
                    self.linked_list_data_next_store[idx - 1][2] = new_null
            except:
                pass
            
            time.sleep(0.3)
            
            # ========== 步骤4: 删除尾节点 ==========
            self.create_step_indicator(4, total_steps, "释放尾节点内存")
            self.show_operation_step("delete toDelete  (删除尾节点)")
            
            # 闪烁并删除
            self.flash_node(idx, 3, THEME_COLORS["neon_red"])
            
            # 销毁temp指针
            self.destroy_pointer(temp_ptr, temp_label, temp_glow)
            
            # 重置temp指针位置
            self.temp_label_x = 40
            self.pointing_line_temp_left = 65
        
        # 删除可视化元素
        self._remove_visual_elements(idx)
        
        # 完成
        self.remove_step_indicator()
        self.show_operation_step("✓ 尾节点已删除", THEME_COLORS["neon_green"])

    def _delete_middle_node_enhanced(self, idx):
        """删除中间节点 - 增强版动画，突出展示指针变化过程"""
        
        total_steps = 4
        
        # ========== 步骤1：遍历找到要删除节点的前一个节点 ==========
        self.create_step_indicator(1, total_steps, "遍历找到要删除节点的前驱")
        self.show_operation_step("① temp = head; 遍历到位置 " + str(idx))
        
        try:
            self.pseudocode_panel.highlight_line(7, "temp = head")
        except:
            pass
        
        # 创建temp指针
        first_x = self.linked_list_position[0][4] + 50
        first_y = self.linked_list_position[0][5] - 30
        temp_ptr, temp_lbl, temp_glow = self.create_visual_pointer(
            "temp", first_x, first_y, THEME_COLORS["neon_orange"]
        )
        
        # 高亮遍历循环
        try:
            self.pseudocode_panel.highlight_line(8, f"遍历到位置 {idx}")
        except:
            pass
        
        # 遍历到前一个节点
        for i in range(idx - 1):
            self.highlight_node(i, THEME_COLORS["neon_orange"], 0.2)
            if i < idx - 2:
                next_x = self.linked_list_position[i + 1][4] + 50
                next_y = self.linked_list_position[i + 1][5] - 30
                self.move_pointer_to_node(temp_ptr, temp_lbl, temp_glow, next_x, next_y)
        
        # 最终定位到前一个节点
        prev_node_x = self.linked_list_position[idx - 1][4] + 50
        prev_node_y = self.linked_list_position[idx - 1][5] - 30
        self.move_pointer_to_node(temp_ptr, temp_lbl, temp_glow, prev_node_x, prev_node_y)
        
        # 高亮前一个节点
        self.highlight_node(idx - 1, THEME_COLORS["neon_cyan"], 0.5)
        self.show_operation_step("temp指针已定位到要删除节点的前驱")
        time.sleep(0.3)
        
        # ========== 步骤2：标记要删除的节点 ==========
        self.create_step_indicator(2, total_steps, "标记要删除的节点")
        self.show_operation_step("② toDelete = temp->next  (标记要删除的节点)")
        
        try:
            self.pseudocode_panel.highlight_line(11, "toDelete = temp->next")
        except:
            pass
        
        # 获取要删除节点的位置
        delete_node_x = self.linked_list_position[idx][4]
        delete_node_y = self.linked_list_position[idx][5]
        
        # 创建红色高亮框
        highlight_box = self.canvas_make.create_rectangle(
            delete_node_x-5, delete_node_y-5, 
            delete_node_x+105, delete_node_y+70,
            outline="red", width=4, dash=(5, 2)
        )
        
        # 使用画布文本来避免覆盖问题
        delete_text = self.canvas_make.create_text(
            delete_node_x + 50, delete_node_y - 40,
            text="要删除的节点", 
            font=("Arial", 12, "bold"), 
            fill="white",
            anchor="center"
        )
        
        # 创建文本背景
        text_bbox = self.canvas_make.bbox(delete_text)
        text_bg = self.canvas_make.create_rectangle(
            text_bbox[0]-5, text_bbox[1]-2,
            text_bbox[2]+5, text_bbox[3]+2,
            fill="red", outline="red"
        )
        # 将背景放在文本后面
        self.canvas_make.tag_lower(text_bg, delete_text)
        
        # 闪烁效果
        for _ in range(3):
            self.canvas_make.itemconfig(highlight_box, outline="darkred", width=6)
            self.canvas_make.itemconfig(text_bg, fill="darkred")
            self.window.update()
            time.sleep(0.2)
            self.canvas_make.itemconfig(highlight_box, outline="red", width=4)
            self.canvas_make.itemconfig(text_bg, fill="red")
            self.window.update()
            time.sleep(0.2)
        
        self.window.update()
        time.sleep(0.8)
        
        # ========== 步骤3：修改前驱节点的next指针，绕过被删除节点 ==========
        self.create_step_indicator(3, total_steps, "修改指针，绕过被删节点")
        self.show_operation_step("③ temp->next = toDelete->next  (指针绕过被删节点)")
        
        try:
            self.pseudocode_panel.highlight_line(12, "temp->next = toDelete->next")
        except:
            pass
        
        # 获取前一个节点和后一个节点的位置
        prev_node_center_x = self.linked_list_position[idx-1][4] + 95  # 前一个节点右侧
        prev_node_center_y = self.linked_list_position[idx-1][5] + 32
        
        next_node_center_x = self.linked_list_position[idx+1][4] + 25  # 后一个节点左侧  
        next_node_center_y = self.linked_list_position[idx+1][5] + 32
        
        # 创建醒目的红色曲线箭头（绕过被删除节点）
        # 计算控制点，使曲线明显绕过被删除节点
        control_x1 = (prev_node_center_x + delete_node_x) / 2
        control_y1 = prev_node_center_y - 60  # 向上弯曲
        control_x2 = (delete_node_x + next_node_center_x) / 2  
        control_y2 = next_node_center_y - 60  # 向上弯曲
        
        # 使用三次贝塞尔曲线创建更平滑的路径
        curve_points = []
        for t in range(0, 21):  # 更多点使曲线更平滑
            t_normalized = t / 20.0
            # 三次贝塞尔曲线公式
            x = (1-t_normalized)**3 * prev_node_center_x + \
                3*(1-t_normalized)**2*t_normalized * control_x1 + \
                3*(1-t_normalized)*t_normalized**2 * control_x2 + \
                t_normalized**3 * next_node_center_x
            y = (1-t_normalized)**3 * prev_node_center_y + \
                3*(1-t_normalized)**2*t_normalized * control_y1 + \
                3*(1-t_normalized)*t_normalized**2 * control_y2 + \
                t_normalized**3 * next_node_center_y
            curve_points.extend([x, y])
        
        # 创建粗的红色箭头
        redirect_arrow = self.canvas_make.create_line(
            curve_points, arrow=LAST, width=6, fill="red", 
            arrowshape=(16, 20, 8), smooth=1
        )
        
        # 使用画布文本创建说明标签，避免覆盖问题
        label_x = (prev_node_center_x + next_node_center_x) / 2
        label_y = min(prev_node_center_y, next_node_center_y) - 100
        
        # 创建文本
        redirect_text = self.canvas_make.create_text(
            label_x, label_y,
            text="前节点→后节点", 
            font=("Arial", 11, "bold"), 
            fill="red",
            anchor="center"
        )
        
        # 创建文本背景
        text_bbox2 = self.canvas_make.bbox(redirect_text)
        text_bg2 = self.canvas_make.create_rectangle(
            text_bbox2[0]-5, text_bbox2[1]-2,
            text_bbox2[2]+5, text_bbox2[3]+2,
            fill="#1E3A5F", outline="red", width=2
        )
        # 将背景放在文本后面
        self.canvas_make.tag_lower(text_bg2, redirect_text)
        
        # 闪烁强调
        for _ in range(4):
            self.canvas_make.itemconfig(redirect_arrow, width=8, fill=THEME_COLORS["neon_pink"])
            self.canvas_make.itemconfig(redirect_text, fill=THEME_COLORS["neon_pink"])
            self.canvas_make.itemconfig(text_bg2, fill=THEME_COLORS["neon_orange"], outline=THEME_COLORS["neon_pink"])
            self.window.update()
            time.sleep(0.2)
            self.canvas_make.itemconfig(redirect_arrow, width=6, fill=THEME_COLORS["neon_red"])
            self.canvas_make.itemconfig(redirect_text, fill=THEME_COLORS["neon_red"])
            self.canvas_make.itemconfig(text_bg2, fill="#1E3A5F", outline=THEME_COLORS["neon_red"])
            self.window.update()
            time.sleep(0.2)
        
        self.window.update()
        time.sleep(1.0)
        
        # ========== 步骤4：执行删除并更新可视化 ==========
        self.create_step_indicator(4, total_steps, "释放节点内存，整理链表")
        self.show_operation_step("④ delete toDelete  (删除节点，释放内存)")
        
        try:
            self.pseudocode_panel.highlight_line(13, "delete toDelete")
        except:
            pass
        
        # 销毁temp指针
        self.destroy_pointer(temp_ptr, temp_lbl, temp_glow)
        
        # 先清理临时图形
        self.canvas_make.delete(highlight_box)
        self.canvas_make.delete(text_bg)
        self.canvas_make.delete(delete_text)
        self.canvas_make.delete(redirect_arrow)
        self.canvas_make.delete(text_bg2)
        self.canvas_make.delete(redirect_text)
        
        # 移除temp指针
        self.temp_label.place_forget()
        self.canvas_make.delete(self.pointing_line_temp)
        self.temp_label_x = 40
        self.pointing_line_temp_left = 65
        
        # 实际删除可视化元素
        self._remove_visual_elements(idx)
        
        # 左移后续节点
        self._shift_nodes_left(idx)
        
        # 更新前一个节点的箭头指向
        self._update_previous_node_arrow(idx-1, idx)
        
        # 完成
        self.remove_step_indicator()
        
        try:
            self.pseudocode_panel.highlight_line(15, "删除完成！")
        except:
            pass
        
        time.sleep(0.3)
        self.show_operation_step(f"✓ 位置 {idx+1} 的节点已删除", THEME_COLORS["neon_green"])

    def _update_previous_node_arrow(self, prev_idx, deleted_idx):
        """更新前一个节点的箭头指向"""
        if prev_idx < 0 or prev_idx >= len(self.linked_list_data_next_store):
            return
            
        entry = self.linked_list_data_next_store[prev_idx]
        prev_arrow_id = entry[1] if len(entry) > 1 else None
        
        if prev_arrow_id is None:
            return
            
        prev_node_x = self.linked_list_position[prev_idx][0]
        prev_node_y = self.linked_list_position[prev_idx][1]
        
        # 计算新的目标位置
        if deleted_idx < len(self.linked_list_position):
            # 指向被删除节点的下一个节点
            next_node_x = self.linked_list_position[deleted_idx][0] + 75
            next_node_y = self.linked_list_position[deleted_idx][1] + 15
        else:
            # 如果删除的是最后一个节点，指向NULL
            next_node_x = prev_node_x + 115
            next_node_y = prev_node_y + 15
        
        # 更新箭头为直线
        try:
            self.canvas_make.coords(prev_arrow_id, 
                                   prev_node_x+75, prev_node_y+15,
                                   next_node_x, next_node_y)
            
            # 短暂高亮新箭头
            original_color = self.canvas_make.itemcget(prev_arrow_id, "fill")
            self.canvas_make.itemconfig(prev_arrow_id, width=5, fill=THEME_COLORS["neon_green"])
            self.window.update()
            time.sleep(0.3)
            self.canvas_make.itemconfig(prev_arrow_id, width=3, fill=original_color)
            
        except Exception as e:
            print(f"更新箭头失败: {e}")

    def _shift_nodes_left(self, start_idx):
        """将start_idx开始的节点左移，保持间距 - 修复版本"""
        shift_distance = 120  # 节点间距
        
        # 第一步：先更新所有位置信息和移动画布元素
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
                new_next_x, new_data_y,
                new_main_x, new_main_y
            ]
            
            # 移动画布元素（矩形等）
            node_group = self.linked_list_canvas_small_widget[i]
            for element in node_group:
                try:
                    self.canvas_make.move(element, -shift_distance, 0)
                except:
                    pass
            
            # 移动值标签
            entry = self.linked_list_data_next_store[i]
            value_set = entry[0] if len(entry) > 0 else None
            if value_set is not None:
                try:
                    value_set.place_configure(x=new_data_x + 8)
                except:
                    pass
            
            # 移动 data/next 标签
            try:
                data_label, next_label = self.linked_list_canvas_small_widget_label[i]
                data_label.place_configure(x=new_data_x)
                next_label.place_configure(x=new_data_x+50)
            except:
                pass
        
        # 第二步：所有节点移动完成后，统一更新箭头坐标
        for i in range(start_idx, len(self.linked_list_position)):
            entry = self.linked_list_data_next_store[i]
            arrow_id = entry[1] if len(entry) > 1 else None
            next_set = entry[2] if len(entry) > 2 else None
            
            new_data_x = self.linked_list_position[i][0]
            new_data_y = self.linked_list_position[i][1]
            
            if i < len(self.linked_list_data_next_store) - 1:
                # 不是最后一个节点，箭头指向下一个节点
                next_node_x = self.linked_list_position[i+1][0]
                if arrow_id is not None:
                    try:
                        self.canvas_make.coords(arrow_id, 
                                               new_data_x+75, new_data_y+15,
                                               next_node_x+25, new_data_y+15)
                    except Exception as e:
                        print(f"更新箭头坐标失败: {e}")
            else:
                # 最后一个节点，指向NULL
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
            
            time.sleep(0.05)
            self.window.update()

    def _remove_visual_elements(self, idx):
        """移除指定索引的可视化元素 - 修复版本"""
        try:
            # 1. 移除数据存储中的元素
            if idx < len(self.linked_list_data_next_store):
                temp1 = self.linked_list_data_next_store.pop(idx)
                for element in temp1:
                    if element is not None:
                        removed = False
                        # widget-like objects (Label widgets)
                        try:
                            element.place_forget()
                            try: element.destroy()
                            except: pass
                            removed = True
                        except Exception:
                            pass

                        # tkinter widget objects that only implement destroy
                        if not removed:
                            try:
                                element.destroy()
                                removed = True
                            except Exception:
                                pass

                        # finally, if it's a canvas item id (int) or anything else, try canvas delete
                        if not removed:
                            try:
                                self.canvas_make.delete(element)
                                removed = True
                            except Exception:
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
        self.position_label = Label(self.window, text="🗑️ 输入要删除的节点位置", font=("Microsoft YaHei UI", 11, "bold"), bg=THEME_COLORS["bg_card"], fg=THEME_COLORS["neon_orange"])
        self.position_label.place(x=1000, y=620)
        self.position_take_entry = Entry(self.window, font=("Consolas", 13, "bold"), bg="#21262D", state=NORMAL, 
                                         fg=THEME_COLORS["text_primary"], relief=FLAT, bd=0, insertbackground=THEME_COLORS["neon_cyan"],
                                         textvar=self.delete_entry)
        self.position_take_entry.place(x=1020, y=650, height=30); self.position_take_entry.focus()
        self.find_btn = Button(self.window, text="🔍 查找", font=("Microsoft YaHei UI", 10, "bold"), 
                               bg=THEME_COLORS["neon_red"], fg="white", relief=FLAT, bd=0, padx=10, pady=5, 
                               state=NORMAL, cursor="hand2", command=self.delete_single_node)
        self.find_btn.place(x=1230, y=648)

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
            self.enhanced_insert_at_position(1, value)
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
            self.enhanced_insert_at_position(insert_pos, value)
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
        self.new_node_label = Label(self.canvas_make, text="✨ New Node", font=("Consolas",12,"bold"), bg=THEME_COLORS["bg_card"], fg=THEME_COLORS["neon_cyan"])
        self.new_node_label.place(x=25, y=90)
        self.data = self.make_rect(self.data_left,self.data_up,self.data_left+40,self.data_up+30, outline=THEME_COLORS["neon_cyan"], fill="#1E3A5F", width=2)
        self.data_label = Label(self.canvas_make, text="data", font=("Consolas",11,"bold"), bg=THEME_COLORS["bg_dark"], fg=THEME_COLORS["neon_green"])
        self.data_label.place(x=self.data_label_x, y=self.data_label_y)
        self.next = self.make_rect(self.data_left+50,self.data_up,self.data_left+90,self.data_up+30, outline=THEME_COLORS["neon_cyan"], fill="#1E3A5F", width=2)
        self.next_label = Label(self.canvas_make, text="next", font=("Consolas",11,"bold"), bg=THEME_COLORS["bg_dark"], fg=THEME_COLORS["neon_pink"])
        self.next_label.place(x=self.data_label_x+50, y=self.data_label_y)
        self.main_container_node = self.make_rect(self.main_node_left, self.main_node_up, self.main_node_left+100, self.main_node_up+65, outline=THEME_COLORS["neon_cyan"], width=2)
        
        # 设置节点值
        self.value_set = Label(self.canvas_make, text=self.value_entry.get(), font=("Consolas", 11, "bold"), fg=THEME_COLORS["neon_yellow"], bg="#1E3A5F")
        self.value_set.place(x=self.data_left + 8, y=self.data_up + 3)
        self.arrow = self.canvas_make.create_line(self.data_left+75, self.data_up+15, self.data_left+115, self.data_up+15, width=3, fill=THEME_COLORS["neon_green"])
        self.next_set = Label(self.canvas_make, text="NULL", font=("Consolas", 12, "bold"), fg=THEME_COLORS["neon_pink"], bg=THEME_COLORS["bg_card"])
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
                
                self.main_container_node = self.make_rect(self.main_node_left, self.main_node_up, self.main_node_left+100, self.main_node_up+65, outline=THEME_COLORS["neon_cyan"], width=3)
                self.data = self.make_rect(self.data_left, self.data_up, self.data_left+40, self.data_up+30, outline=THEME_COLORS["neon_cyan"], fill="#1E3A5F", width=3)
                self.next = self.make_rect(self.data_left+50, self.data_up, self.data_left+90, self.data_up+30, outline=THEME_COLORS["neon_cyan"], fill="#1E3A5F", width=3)
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
                    
                    self.temp_pointer = self.make_rect(self.temp_pointer_left, self.temp_pointer_up, self.temp_pointer_left + 30, self.temp_pointer_up + 30, fill=THEME_COLORS["neon_cyan"], outline="black", width=3)
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
                    
                    self.main_container_node = self.make_rect(self.main_node_left, self.main_node_up, self.main_node_left+100, self.main_node_up+65, outline=THEME_COLORS["neon_cyan"], width=3)
                    self.data = self.make_rect(self.data_left, self.data_up, self.data_left+40, self.data_up+30, outline=THEME_COLORS["neon_cyan"], fill="#1E3A5F", width=3)
                    self.next = self.make_rect(self.data_left+50, self.data_up, self.data_left+90, self.data_up+30, outline=THEME_COLORS["neon_cyan"], fill="#1E3A5F", width=3)
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
    window.geometry("1350x700")
    window.maxsize(1500,800)
    window.minsize(1350,700)
    LinkList(window)
    window.mainloop()
    

