from tkinter import *
from tkinter import messagebox, filedialog
import time
from sequence_list.sequence_list_model import SequenceListModel
import os
import storage as storage
import json
from datetime import datetime
import sys
import sequence_api as sequence_api
from sequence_list.sequence_ui import create_heading, create_buttons

class SequenceListVisualizer:
    def __init__(self, root):
        self.window = root
        self.window.config(bg="lightgreen")
        self.canvas = Canvas(self.window, bg="lightyellow", width=1350, height=500, relief=RAISED, bd=8)
        self.canvas.pack()
        self.model = SequenceListModel()
        sequence_api.bind_visualizer(self)
        print("sequence_api successfully bound to SequenceListVisualizer (model shared).")
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
        create_heading(self)        
        create_buttons(self)
        self.update_display()
    
    @property
    def data_store(self):
        """动态返回当前模型的数据列表，避免旧引用不同步问题。"""
        return getattr(self.model, "data", [])

    def _ensure_sequence_folder(self):
        if hasattr(storage, "ensure_save_subdir"):
            return storage.ensure_save_subdir("sequence")
        base_dir = os.path.dirname(os.path.abspath(storage.__file__))
        default_dir = os.path.join(base_dir, "save", "sequence")
        os.makedirs(default_dir, exist_ok=True)
        return default_dir

    def save_sequence(self):
        arr = list(self.data_store)
        meta = {"length": len(arr)}
        default_dir = self._ensure_sequence_folder()
        default_name = f"sequence_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = filedialog.asksaveasfilename(
            initialdir=default_dir,
            initialfile=default_name,
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="保存顺序表到文件"
        )
        payload = {"type": "sequence", "data": arr, "metadata": meta}
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        messagebox.showinfo("成功", f"顺序表已保存到：\n{filepath}")
    
    def load_sequence(self):
        default_dir = self._ensure_sequence_folder()
        filepath = filedialog.askopenfilename(
            initialdir=default_dir,
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="从文件加载顺序表"
        )
        with open(filepath, "r", encoding="utf-8") as f:
            loaded = json.load(f)
        data_list = loaded.get("data",[])
        self.model.data = list(data_list)
        self.update_display()
        messagebox.showinfo("成功", f"已加载 {len(data_list)} 个元素到顺序表")
    
    def prepare_build_list(self):
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
        if position == 0:
            self.model.insert_first(value)
        elif position == len(self.data_store):
            self.model.insert_last(value)
        
        self.animate_insert(position, value)
        
    def perform_insert_with_position(self):
        value = self.value_entry.get()
        position_str = self.position_entry.get()
        if not value or not position_str:
            messagebox.showerror("错误", "请填写所有字段")
            return
        try:
            position = int(position_str)  # 用户输入是 1-based
        except ValueError:
            messagebox.showerror("错误", "位置必须是整数")
            return

        # 允许插入到末尾，所以最大为 len + 1
        if position < 1 or position > len(self.data_store) + 1:
            messagebox.showerror("错误", f"位置必须在1到{len(self.data_store) + 1}之间")
            return

        insert_idx = position - 1  # 转为 0-based
        try:
            # 使用 model.insert (0-based) 将数据插入模型
            self.model.insert(insert_idx, value)
        except Exception as e:
            messagebox.showerror("错误", f"插入失败: {e}")
            return

        # 以 0-based index 播放动画
        try:
            self.animate_insert(insert_idx, value)
        except Exception as e:
            messagebox.showerror("错误", f"插入动画失败: {e}")
            try:
                self.update_display()
            except Exception:
                pass
        
    def animate_insert(self, position, value):
        # position: 0-based 插入索引
        self.disable_buttons()
        # 新元素起始在右侧（画布外/右侧）
        new_x = self.start_x + max(0, len(self.data_store)-1) * (self.cell_width + self.spacing) + 200
        new_y = self.start_y
        new_rect = self.canvas.create_rectangle(new_x, new_y, new_x + self.cell_width,
                                                new_y + self.cell_height, fill="lightblue", outline="black")
        new_label = self.canvas.create_text(new_x + self.cell_width/2, new_y + self.cell_height/2,
                                            text=value, font=("Arial", 14, "bold"))

        target_x = self.start_x + position * (self.cell_width + self.spacing)
        dx = (target_x - new_x) / 20.0
        for _ in range(20):
            self.canvas.move(new_rect, dx, 0)
            self.canvas.move(new_label, dx, 0)
            self.window.update()
            time.sleep(0.03)

        old_count = len(self.data_rectangles)
        # move items at indices >= position up to old_count-1 (these correspond to elements before insertion)
        for idx in range(position, old_count):
            step_dx = (self.cell_width + self.spacing) / 10.0
            for _ in range(10):
                try:
                    self.canvas.move(self.data_rectangles[idx], step_dx, 0)
                    self.canvas.move(self.data_labels[idx], step_dx, 0)
                    self.canvas.move(self.index_labels[idx], step_dx, 0)
                    self.window.update()
                    time.sleep(0.01)
                except Exception:
                    pass

        # 最后刷新显示以保证一致
        self.update_display()
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
        self.disable_buttons()
        for i in range(len(self.data_store)):
            dx = 20
            for j in range(15):
                self.canvas.move(self.data_rectangles[i], dx, 0)
                self.canvas.move(self.data_labels[i], dx, 0)
                self.canvas.move(self.index_labels[i], dx, 0)
                self.window.update()
                time.sleep(0.02)
        self.model.clear()
        self.update_display()
        self.enable_buttons()
    def process_dsl(self, event=None):
        txt = (self.dsl_var.get() or "").strip()
        from DSL_utils import process_command
        try:
            process_command(self, txt)
        finally:
            self.dsl_var.set("")

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
