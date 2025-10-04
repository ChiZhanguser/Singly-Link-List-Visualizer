from tkinter import *
from tkinter import messagebox, filedialog
import time
from sequence_list.sequence_list_model import SequenceListModel
import os
import storage as storage
import json
from datetime import datetime


class SequenceListVisualizer:
    def __init__(self, root):
        self.window = root
        self.window.config(bg="lightgreen")
        self.canvas = Canvas(self.window, bg="lightyellow", width=1350, height=500, relief=RAISED, bd=8)
        self.canvas.pack()
        
        self.model = SequenceListModel()
        # 注意：data_store 改为 property（见类下面），这样始终反映 self.model.data 的最新状态
        
        # sequence_list_visual.py 中 __init__ 的末尾附近，紧跟 self.model 实例化之后
        try:
            # 优先直接 import project 根的 sequence_api
            import sequence_api as sequence_api
            # 把 visualizer 的 model 绑定给 adapter，使两个模块共享同一实例
            sequence_api.bind_visualizer(self)
            print("sequence_api successfully bound to SequenceListVisualizer (model shared).")
        except Exception as e:
            # 若 import 失败，尝试把 sequence_api 路径加入 sys.path 或打印警告
            try:
                import sys
                # 可选地把项目根加入 sys.path（按需取消注释并调整路径）
                # sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
                import sequence_api as sequence_api
                sequence_api.bind_visualizer(self)
                print("sequence_api successfully bound after sys.path tweak.")
            except Exception as e2:
                print("WARNING: could not bind sequence_api to visualizer:", e, e2)
        self.dsl_var=StringVar()
        
        
        # 存储画布上的元素
        self.data_rectangles = []  # 数据矩形
        self.data_labels = []      # 数据标签
        self.index_labels = []     # 索引标签
        
        # 坐标和尺寸参数
        self.start_x = 100
        self.start_y = 200
        self.cell_width = 60
        self.cell_height = 40
        self.spacing = 5
        
        # 输入变量
        self.value_entry = StringVar()
        self.position_entry = StringVar()
        
        # 按钮列表
        self.buttons = []  # 初始化按钮列表
        
        # 初始化界面
        self.create_heading()
        self.create_buttons()
        self.update_display()
    
    @property
    def data_store(self):
        """动态返回当前模型的数据列表，避免旧引用不同步问题。"""
        return getattr(self.model, "data", [])
    
    def create_heading(self):
        heading = Label(self.window, text="顺序表(线性表)的可视化", 
                       font=("Arial", 30, "bold"), bg="lightgreen", fg="darkblue")
        heading.place(x=400, y=20)
        
        info = Label(self.window, text="顺序表在内存中连续存储，插入和删除操作需要移动元素", 
                    font=("Arial", 16), bg="lightgreen", fg="black")
        info.place(x=400, y=80)
    
    def create_buttons(self):
        # 操作按钮框架
        button_frame = Frame(self.window, bg="lightgreen")
        button_frame.place(x=50, y=540, width=1250, height=150)  # 增加高度以容纳更多按钮
        
        # 构建顺序表按钮 - 新增
        build_list_btn = Button(button_frame, text="构建顺序表", font=("Arial", 12), 
                              bg="teal", fg="white", command=self.prepare_build_list)
        build_list_btn.grid(row=0, column=0, padx=10, pady=5)
        self.buttons.append(build_list_btn)
        
        # 插入按钮
        insert_first_btn = Button(button_frame, text="头部插入", font=("Arial", 12), 
                                bg="orange", command=lambda: self.prepare_insert(0))
        insert_first_btn.grid(row=0, column=1, padx=10, pady=5)
        self.buttons.append(insert_first_btn)
        
        insert_last_btn = Button(button_frame, text="尾部插入", font=("Arial", 12), 
                               bg="orange", command=lambda: self.prepare_insert(len(self.data_store)))
        insert_last_btn.grid(row=0, column=2, padx=10, pady=5)
        self.buttons.append(insert_last_btn)
        
        insert_pos_btn = Button(button_frame, text="指定位置插入", font=("Arial", 12), 
                              bg="orange", command=self.prepare_insert_with_position)
        insert_pos_btn.grid(row=0, column=3, padx=10, pady=5)
        self.buttons.append(insert_pos_btn)
        
        # 删除按钮
        delete_first_btn = Button(button_frame, text="头部删除", font=("Arial", 12), 
                                bg="red", fg="white", command=self.delete_first)
        delete_first_btn.grid(row=1, column=0, padx=10, pady=5)
        self.buttons.append(delete_first_btn)
        
        delete_last_btn = Button(button_frame, text="尾部删除", font=("Arial", 12), 
                               bg="red", fg="white", command=self.delete_last)
        delete_last_btn.grid(row=1, column=1, padx=10, pady=5)
        self.buttons.append(delete_last_btn)
        
        delete_pos_btn = Button(button_frame, text="指定位置删除", font=("Arial", 12), 
                              bg="red", fg="white", command=self.prepare_delete_with_position)
        delete_pos_btn.grid(row=1, column=2, padx=10, pady=5)
        self.buttons.append(delete_pos_btn)
        
        # 清空按钮
        clear_btn = Button(button_frame, text="清空顺序表", font=("Arial", 12), 
                         bg="purple", fg="white", command=self.clear_list)
        clear_btn.grid(row=1, column=3, padx=10, pady=5)
        self.buttons.append(clear_btn)
        
        # 返回主界面按钮
        back_btn = Button(button_frame, text="返回主界面", font=("Arial", 12), 
                        bg="blue", fg="white", command=self.back_to_main)
        back_btn.grid(row=1, column=4, padx=10, pady=5)
        self.buttons.append(back_btn)
        
        # 保存 / 打开 按钮
        save_btn = Button(button_frame, text="保存顺序表", font=("Arial", 12),
                          bg="#6C9EFF", fg="white", command=self.save_sequence)
        save_btn.grid(row=0, column=5, padx=10, pady=5)
        self.buttons.append(save_btn)
        
        load_btn = Button(button_frame, text="打开顺序表", font=("Arial", 12),
                          bg="#6C9EFF", fg="white", command=self.load_sequence)
        load_btn.grid(row=0, column=6, padx=10, pady=5)
        self.buttons.append(load_btn)
        dsl_label = Label(button_frame, text="DSL 命令:", font=("Arial", 12), bg="lightgreen")
        dsl_label.grid(row=2, column=0, padx=(10,2), pady=8, sticky="w")
        dsl_entry = Entry(button_frame, textvariable=self.dsl_var, font=("Arial", 12), width=40)
        dsl_entry.grid(row=2, column=1, columnspan=3, padx=4, pady=8, sticky="w")
        dsl_entry.bind("<Return>", lambda e: self.process_dsl())
        dsl_btn = Button(button_frame, text="执行 DSL", font=("Arial", 12), bg="#4CAF50", fg="white", command=self.process_dsl)
        dsl_btn.grid(row=2, column=4, padx=10, pady=8)

    
    # ---------- storage helpers ----------
    def _ensure_sequence_folder(self):
        """
        确保 save/sequence 文件夹存在，优先使用 storage.ensure_save_subdir。
        返回该目录的绝对路径。
        """
        try:
            if hasattr(storage, "ensure_save_subdir"):
                return storage.ensure_save_subdir("sequence")
            base_dir = os.path.dirname(os.path.abspath(storage.__file__))
            default_dir = os.path.join(base_dir, "save", "sequence")
            os.makedirs(default_dir, exist_ok=True)
            return default_dir
        except Exception:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            default_dir = os.path.join(base_dir, "..", "save", "sequence")
            default_dir = os.path.normpath(default_dir)
            os.makedirs(default_dir, exist_ok=True)
            return default_dir

    def save_sequence(self):
        """
        保存当前顺序表（self.model.data）到 JSON 文件。
        初始目录为 save/sequence，默认文件名 sequence_YYYYmmdd_HHMMSS.json
        """
        try:
            arr = list(self.data_store)
            meta = {"length": len(arr)}
            
            if len(arr) == 0:
                if not messagebox.askyesno("确认", "当前顺序表为空，是否仍然保存一个空文件？"):
                    return
            
            default_dir = self._ensure_sequence_folder()
            default_name = f"sequence_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            filepath = filedialog.asksaveasfilename(
                initialdir=default_dir,
                initialfile=default_name,
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="保存顺序表到文件"
            )
            if not filepath:
                return
            
            payload = {"type": "sequence", "data": arr, "metadata": meta}
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)
            
            messagebox.showinfo("成功", f"顺序表已保存到：\n{filepath}")
        except Exception as e:
            print("save_sequence error:", e)
            messagebox.showerror("错误", f"保存失败：{e}")
    
    def load_sequence(self):
        """
        从文件加载顺序表数据并快速恢复（无动画）。
        支持格式：
          1) {"type":"sequence","data":[...], ...}
          2) {"data":[...], ...}
          3) 直接 [...](list)
        """
        try:
            default_dir = self._ensure_sequence_folder()
            filepath = filedialog.askopenfilename(
                initialdir=default_dir,
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="从文件加载顺序表"
            )
            if not filepath:
                return
            
            with open(filepath, "r", encoding="utf-8") as f:
                loaded = json.load(f)
            
            # 兼容不同格式
            if isinstance(loaded, dict) and "data" in loaded:
                data_list = loaded.get("data", [])
            elif isinstance(loaded, list):
                data_list = loaded
            else:
                messagebox.showerror("错误", "文件格式不被识别（需为 list 或包含 data 字段的 dict）")
                return
            
            if not isinstance(data_list, list):
                messagebox.showerror("错误", "读取的数据不是列表")
                return
            
            # 直接赋值或兜底逐项插入（保持模型兼容）
            try:
                # 如果模型有直接 data 属性，尝试直接替换
                if hasattr(self.model, "data"):
                    self.model.data = list(data_list)
                    # 如果模型有 length/size/top 等，尝试同步
                    if hasattr(self.model, "length"):
                        try:
                            self.model.length = len(self.model.data)
                        except Exception:
                            pass
                else:
                    # 否则尽量通过提供的接口插入（append/insert）
                    if hasattr(self.model, "clear"):
                        try:
                            self.model.clear()
                        except Exception:
                            pass
                    for v in data_list:
                        if hasattr(self.model, "append"):
                            self.model.append(v)
                        elif hasattr(self.model, "insert_last"):
                            try:
                                self.model.insert_last(v)
                            except Exception:
                                # 回退为 append
                                self.model.append(v)
                        else:
                            # 兜底：尝试创建 data 属性
                            if not hasattr(self.model, "data"):
                                self.model.data = []
                            self.model.data.append(v)
            except Exception as e:
                print("load_sequence assign error:", e)
                messagebox.showwarning("警告", "加载时遇到模型兼容性问题，可能未完全恢复。")
            
            self.update_display()
            messagebox.showinfo("成功", f"已加载 {len(data_list)} 个元素到顺序表")
        except Exception as e:
            print("load_sequence error:", e)
            messagebox.showerror("错误", f"加载失败：{e}")
    
    # ---------- 其余方法（未动） ----------
    def prepare_build_list(self):
        """准备构建顺序表的输入界面"""
        self.build_values_entry = StringVar()
        
        input_frame = Frame(self.window, bg="lightgreen")
        input_frame.place(x=400, y=650, width=600, height=80)  # 调整位置
        
        value_label = Label(input_frame, text="输入多个值(用逗号分隔):", font=("Arial", 12), bg="lightgreen")
        value_label.grid(row=0, column=0, padx=5, pady=5)
        
        value_entry = Entry(input_frame, textvariable=self.build_values_entry, font=("Arial", 12), width=30)
        value_entry.grid(row=0, column=1, padx=5, pady=5)
        
        confirm_btn = Button(input_frame, text="确认构建", font=("Arial", 12), 
                           command=self.perform_build_list)
        confirm_btn.grid(row=0, column=2, padx=5, pady=5)
        
        value_entry.focus()
    
    def perform_build_list(self):
        """执行构建顺序表的操作"""
        values_str = self.build_values_entry.get()
        if not values_str:
            messagebox.showerror("错误", "请输入要构建的值")
            return
        
        try:
            # 解析输入的值
            values = [v.strip() for v in values_str.split(',') if v.strip()]
            if not values:
                messagebox.showerror("错误", "请输入有效的值")
                return
            
            # 清空当前顺序表
            self.model.clear()
            self.update_display()
            
            # 逐个添加值并展示动画
            self.disable_buttons()
            
            for i, value in enumerate(values):
                # 添加到模型
                self.model.append(value)
                
                # 创建新元素的动画
                self.animate_build_element(i, value)
                
                # 短暂暂停，让用户能看到过程
                self.window.update()
                time.sleep(0.3)
            
            self.enable_buttons()
            
        except Exception as e:
            messagebox.showerror("错误", f"构建顺序表时出错: {str(e)}")
            self.enable_buttons()
    
    def animate_build_element(self, index, value):
        """动画展示构建顺序表元素的过程"""
        # 创建新元素（初始位置在右侧）
        new_x = self.start_x + (len(self.data_store) - 1) * (self.cell_width + self.spacing) + 200
        new_y = self.start_y
        
        new_rect = self.canvas.create_rectangle(new_x, new_y, new_x + self.cell_width, 
                                              new_y + self.cell_height, fill="lightgreen", outline="black")
        new_label = self.canvas.create_text(new_x + self.cell_width/2, new_y + self.cell_height/2, 
                                          text=value, font=("Arial", 14, "bold"))
        
        # 移动新元素到正确位置
        target_x = self.start_x + index * (self.cell_width + self.spacing)
        
        # 移动新元素
        dx = (target_x - new_x) / 20
        for i in range(20):
            self.canvas.move(new_rect, dx, 0)
            self.canvas.move(new_label, dx, 0)
            self.window.update()
            time.sleep(0.03)
        
        # 更新显示
        self.update_display()
    
    def disable_buttons(self):
        """禁用所有按钮"""
        for btn in self.buttons:
            btn.config(state=DISABLED)
    
    def enable_buttons(self):
        """启用所有按钮"""
        for btn in self.buttons:
            btn.config(state=NORMAL)
    
    def prepare_insert(self, position):
        self.value_entry.set("")
        
        input_frame = Frame(self.window, bg="lightgreen")
        input_frame.place(x=500, y=650, width=400, height=80)  # 调整位置
        
        value_label = Label(input_frame, text="输入值:", font=("Arial", 12), bg="lightgreen")
        value_label.grid(row=0, column=0, padx=5, pady=5)
        
        value_entry = Entry(input_frame, textvariable=self.value_entry, font=("Arial", 12))
        value_entry.grid(row=0, column=1, padx=5, pady=5)
        
        confirm_btn = Button(input_frame, text="确认", font=("Arial", 12), 
                           command=lambda: self.perform_insert(position))
        confirm_btn.grid(row=0, column=2, padx=5, pady=5)
        
        value_entry.focus()
    
    def prepare_insert_with_position(self):
        self.value_entry.set("")
        self.position_entry.set("")
        
        input_frame = Frame(self.window, bg="lightgreen")
        input_frame.place(x=400, y=650, width=600, height=80)  # 调整位置
        
        value_label = Label(input_frame, text="输入值:", font=("Arial", 12), bg="lightgreen")
        value_label.grid(row=0, column=0, padx=5, pady=5)
        
        value_entry = Entry(input_frame, textvariable=self.value_entry, font=("Arial", 12), width=10)
        value_entry.grid(row=0, column=1, padx=5, pady=5)
        
        pos_label = Label(input_frame, text="位置(1-based):", font=("Arial", 12), bg="lightgreen")
        pos_label.grid(row=0, column=2, padx=5, pady=5)
        
        pos_entry = Entry(input_frame, textvariable=self.position_entry, font=("Arial", 12), width=10)
        pos_entry.grid(row=0, column=3, padx=5, pady=5)
        
        confirm_btn = Button(input_frame, text="确认", font=("Arial", 12), 
                           command=self.perform_insert_with_position)
        confirm_btn.grid(row=0, column=4, padx=5, pady=5)
        
        value_entry.focus()
    
    def perform_insert(self, position):
        value = self.value_entry.get()
        if not value:
            messagebox.showerror("错误", "请输入一个值")
            return
        
        try:
            if position == 0:
                self.model.insert_first(value)
            elif position == len(self.data_store):
                self.model.insert_last(value)
            
            self.animate_insert(position, value)
        except Exception as e:
            messagebox.showerror("错误", str(e))
    
    def perform_insert_with_position(self):
        value = self.value_entry.get()
        position_str = self.position_entry.get()
        
        if not value or not position_str:
            messagebox.showerror("错误", "请填写所有字段")
            return
        
        try:
            position = int(position_str)
            if position < 1 or position > len(self.data_store) + 1:
                messagebox.showerror("错误", f"位置必须在1到{len(self.data_store) + 1}之间")
                return
            
            self.model.insert_after(position - 1, value)
            self.animate_insert(position, value)
        except ValueError:
            messagebox.showerror("错误", "位置必须是整数")
        except Exception as e:
            messagebox.showerror("错误", str(e))
    
    def animate_insert(self, position, value):
        # 禁用所有按钮
        self.disable_buttons()
        
        # 创建新元素（初始位置在右侧）
        new_x = self.start_x + (len(self.data_store) - 1) * (self.cell_width + self.spacing) + 200
        new_y = self.start_y
        
        new_rect = self.canvas.create_rectangle(new_x, new_y, new_x + self.cell_width, 
                                              new_y + self.cell_height, fill="lightblue", outline="black")
        new_label = self.canvas.create_text(new_x + self.cell_width/2, new_y + self.cell_height/2, 
                                          text=value, font=("Arial", 14, "bold"))
        
        # 移动新元素到正确位置
        target_x = self.start_x + position * (self.cell_width + self.spacing)
        
        # 移动新元素
        dx = (target_x - new_x) / 20
        for i in range(20):
            self.canvas.move(new_rect, dx, 0)
            self.canvas.move(new_label, dx, 0)
            self.window.update()
            time.sleep(0.05)
        
        # 移动后面的元素
        for i in range(position, len(self.data_store) - 1):
            dx = (self.cell_width + self.spacing) / 10
            for j in range(10):
                self.canvas.move(self.data_rectangles[i], dx, 0)
                self.canvas.move(self.data_labels[i], dx, 0)
                self.canvas.move(self.index_labels[i], dx, 0)
                self.window.update()
                time.sleep(0.02)
        
        # 更新显示
        self.update_display()
        
        # 启用所有按钮
        self.enable_buttons()
    
    def delete_first(self):
        if len(self.data_store) == 0:
            messagebox.showerror("错误", "顺序表为空")
            return
        
        self.animate_delete(0)
    
    def delete_last(self):
        if len(self.data_store) == 0:
            messagebox.showerror("错误", "顺序表为空")
            return
        
        self.animate_delete(len(self.data_store) - 1)
    
    def prepare_delete_with_position(self):
        self.position_entry.set("")
        
        input_frame = Frame(self.window, bg="lightgreen")
        input_frame.place(x=500, y=650, width=400, height=80)  # 调整位置
        
        pos_label = Label(input_frame, text="位置(1-based):", font=("Arial", 12), bg="lightgreen")
        pos_label.grid(row=0, column=0, padx=5, pady=5)
        
        pos_entry = Entry(input_frame, textvariable=self.position_entry, font=("Arial", 12))
        pos_entry.grid(row=0, column=1, padx=5, pady=5)
        
        confirm_btn = Button(input_frame, text="确认", font=("Arial", 12), 
                           command=self.perform_delete_with_position)
        confirm_btn.grid(row=0, column=2, padx=5, pady=5)
        
        pos_entry.focus()
    
    def perform_delete_with_position(self):
        position_str = self.position_entry.get()
        
        if not position_str:
            messagebox.showerror("错误", "请输入位置")
            return
        
        try:
            position = int(position_str)
            if position < 1 or position > len(self.data_store):
                messagebox.showerror("错误", f"位置必须在1到{len(self.data_store)}之间")
                return
            
            self.animate_delete(position - 1)
        except ValueError:
            messagebox.showerror("错误", "位置必须是整数")
    
    def animate_delete(self, position):
        # 禁用所有按钮
        self.disable_buttons()
        
        # 高亮要删除的元素
        self.canvas.itemconfig(self.data_rectangles[position], fill="red")
        self.window.update()
        time.sleep(0.5)
        
        # 移动后面的元素向前
        for i in range(position + 1, len(self.data_store)):
            dx = -(self.cell_width + self.spacing) / 10
            for j in range(10):
                self.canvas.move(self.data_rectangles[i], dx, 0)
                self.canvas.move(self.data_labels[i], dx, 0)
                self.canvas.move(self.index_labels[i], dx, 0)
                self.window.update()
                time.sleep(0.02)
        
        # 删除元素
        self.model.pop(position)
        
        # 更新显示
        self.update_display()
        
        # 启用所有按钮
        self.enable_buttons()
    
    def clear_list(self):
        if len(self.data_store) == 0:
            messagebox.showinfo("信息", "顺序表已为空")
            return
        
        # 禁用所有按钮
        self.disable_buttons()
        
        # 动画：所有元素向右移动消失
        for i in range(len(self.data_store)):
            dx = 20
            for j in range(15):
                self.canvas.move(self.data_rectangles[i], dx, 0)
                self.canvas.move(self.data_labels[i], dx, 0)
                self.canvas.move(self.index_labels[i], dx, 0)
                self.window.update()
                time.sleep(0.02)
        
        # 清空模型
        self.model.clear()
        
        # 更新显示
        self.update_display()
        
        # 启用所有按钮
        self.enable_buttons()
    def process_dsl(self, event=None):
        txt = (self.dsl_var.get() or "").strip()
        if not txt:
            return
        try:
            from DSL_utils import process_command
        except Exception:
            process_command = None
        try:
            if process_command:
                process_command(self, txt)
            else:
                # 最小回退：支持 create/clear/insert/delete 简单行为
                cmd = txt.split()
                if not cmd:
                    return
                c = cmd[0].lower()
                args = cmd[1:]
                if c == "create":
                    # 快速创建（无动画）
                    items = []
                    for a in args:
                        for p in a.split(","):
                            s = p.strip()
                            if s:
                                items.append(s)
                    if hasattr(self.model, "clear"):
                        self.model.clear()
                    if hasattr(self.model, "append"):
                        for v in items:
                            self.model.append(v)
                    self.update_display()
                elif c == "clear":
                    if hasattr(self, "clear_list"):
                        self.clear_list()
                    else:
                        if hasattr(self.model, "clear"):
                            self.model.clear()
                        self.update_display()
                elif c == "insert":
                    if not args:
                        return
                    v = " ".join(args)
                    if hasattr(self.model, "append"):
                        self.model.append(v)
                    self.update_display()
                elif c == "delete":
                    if not args:
                        return
                    key = args[0].lower()
                    if key in ("first", "1"):
                        if hasattr(self.model, "pop"):
                            try:
                                self.model.pop(0)
                            except Exception:
                                pass
                        elif hasattr(self, "delete_first"):
                            self.delete_first()
                        self.update_display()
                    elif key in ("last",):
                        if hasattr(self.model, "pop"):
                            try:
                                self.model.pop()
                            except Exception:
                                pass
                        elif hasattr(self, "delete_last"):
                            self.delete_last()
                        self.update_display()
                    else:
                        try:
                            pos = int(key)
                            if hasattr(self.model, "pop"):
                                try:
                                    self.model.pop(pos-1)
                                except Exception:
                                    pass
                            self.update_display()
                        except Exception:
                            pass
        finally:
            try:
                self.dsl_var.set("")
            except Exception:
                pass

    
    def update_display(self):
        # 清除画布上的所有元素
        self.canvas.delete("all")
        self.data_rectangles.clear()
        self.data_labels.clear()
        self.index_labels.clear()
        
        # 绘制顺序表
        for i in range(len(self.data_store)):
            x = self.start_x + i * (self.cell_width + self.spacing)
            y = self.start_y
                
            # 绘制数据单元格
            rect = self.canvas.create_rectangle(x, y, x + self.cell_width, y + self.cell_height, 
                                              fill="lightblue", outline="black", width=2)
            self.data_rectangles.append(rect)
            
            # 绘制数据值
            label = self.canvas.create_text(x + self.cell_width/2, y + self.cell_height/2, 
                                          text=str(self.data_store[i]), font=("Arial", 14, "bold"))
            self.data_labels.append(label)
            
            # 绘制索引
            index_label = self.canvas.create_text(x + self.cell_width/2, y + self.cell_height + 15, 
                                                text=str(i), font=("Arial", 12))
            self.index_labels.append(index_label)
        
        # 绘制表结构说明
        info_text = f"顺序表长度: {len(self.data_store)}"
        self.canvas.create_text(100, 100, text=info_text, font=("Arial", 14), anchor="w")
    
    def back_to_main(self):
        # 返回主界面
        self.window.destroy()


if __name__ == '__main__':
    window = Tk()
    window.title("顺序表可视化")
    window.geometry("1350x730")
    window.maxsize(1350, 730)
    window.minsize(1350, 730)
    SequenceListVisualizer(window)
    window.mainloop()
