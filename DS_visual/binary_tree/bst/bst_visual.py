from tkinter import *
from tkinter import messagebox
from tkinter import Toplevel, filedialog
from typing import Dict, Tuple, List, Optional
from binary_tree.bst.bst_model import BSTModel, TreeNode
import storage as storage
import json
from datetime import datetime
import os
from DSL_utils import process_command
from binary_tree.bst.bst_ui import draw_instructions, create_controls

class BSTVisualizer:
    def __init__(self, root):
        self.window = root
        self.window.title("二叉搜索树（BST）可视化")
        self.window.config(bg="#F7F9FB")
        self.canvas_width = 1250
        self.canvas_height = 560
        
        # 创建顶部框架用于状态和引导信息
        self.top_frame = Frame(self.window, bg="#F7F9FB")
        self.top_frame.pack(fill=X, padx=10, pady=5)
        
        # 状态标签
        self.status_label = Label(self.top_frame, text="就绪", font=("Arial", 10, "bold"), 
                                 fg="darkgreen", bg="#F7F9FB")
        self.status_label.pack(side=TOP, anchor=NE)
        
        # 引导信息标签 - 更加醒目
        self.guide_label = Label(self.top_frame, text="", font=("Arial", 11, "bold"), 
                                fg="#D35400", bg="#FFF9C4", relief=SOLID, bd=1,
                                wraplength=1200, justify=CENTER, height=2)
        self.guide_label.pack(side=TOP, fill=X, pady=(5, 0))
        
        self.canvas = Canvas(self.window, bg="white", width=self.canvas_width, height=self.canvas_height, relief=RAISED, bd=8)
        self.canvas.pack(pady=(10,0))
        self.dsl_var = StringVar()
        self.model = BSTModel()
        self.node_to_rect: Dict[TreeNode, int] = {}
        self.node_items: List[int] = []
        self.status_text_id: Optional[int] = None

        # 布局参数
        self.node_w = 120
        self.node_h = 44
        self.left_cell_w = 28
        self.center_cell_w = 64
        self.right_cell_w = self.node_w - self.left_cell_w - self.center_cell_w
        self.level_gap = 100
        self.margin_x = 40

        # 是否正在执行动画
        self.animating = False
        # 是否启用分步引导模式
        self.guide_mode = BooleanVar(value=True)  # 默认启用引导模式

        # 输入框
        self.input_var = StringVar()
        create_controls(self)
        draw_instructions(self)
        
        # 添加引导模式复选框
        self._add_guide_mode_checkbox()
        
    def _add_guide_mode_checkbox(self):
        """添加引导模式复选框"""
        guide_frame = Frame(self.window, bg="#F7F9FB")
        guide_frame.pack(pady=5)
        Checkbutton(guide_frame, text="启用分步引导模式", variable=self.guide_mode, 
                   bg="#F7F9FB", font=("Arial", 10), command=self._on_guide_mode_changed).pack(side=LEFT, padx=5)
        
    def _on_guide_mode_changed(self):
        """引导模式改变时的回调"""
        if not self.guide_mode.get():
            self.guide_label.config(text="", bg="#F7F9FB")
        else:
            self.guide_label.config(bg="#FFF9C4")
        
    def update_guide(self, text: str):
        """更新引导文本"""
        if not self.guide_mode.get():
            return
            
        # 使用Label显示引导文本，更加醒目
        self.guide_label.config(text=text)
        
        # 同时在画布底部也显示（可选）
        if hasattr(self, 'guide_text_id') and self.guide_text_id:
            self.canvas.delete(self.guide_text_id)
        self.guide_text_id = self.canvas.create_text(
            self.canvas_width/2, self.canvas_height - 20, 
            text=text, font=("Arial", 11, "bold"), 
            fill="#D35400", width=self.canvas_width-40
        )
    
    def clear_guide(self):
        """清除引导文本"""
        self.guide_label.config(text="")
        if hasattr(self, 'guide_text_id') and self.guide_text_id:
            self.canvas.delete(self.guide_text_id)
            self.guide_text_id = None
        
    def process_dsl(self, event=None):
        text = (self.dsl_var.get() or "").strip()
        if not text:
            return
        if getattr(self, "animating", False):
            messagebox.showinfo("提示", "当前正在动画，请稍后执行 DSL 命令")
            return
        process_command(self,text)
        self.dsl_var.set("")
    
    def update_status(self, text: str):
        """更新状态文本"""
        self.status_label.config(text=text)
        # 同时在画布上也显示状态
        if not self.status_text_id:
            self.status_text_id = self.canvas.create_text(self.canvas_width-10, 10, anchor="ne", text=text, font=("Arial",12,"bold"), fill="darkgreen")
        else:
            self.canvas.itemconfig(self.status_text_id, text=text)
    
    def _ensure_tree_folder(self) -> str:
        if hasattr(storage, "ensure_save_subdir"):
            return storage.ensure_save_subdir("bst")
        base_dir = os.path.dirname(os.path.abspath(storage.__file__))
        default_dir = os.path.join(base_dir, "save", "bst")
        os.makedirs(default_dir, exist_ok=True)
        return default_dir

    def save_tree(self):
        default_dir = self._ensure_tree_folder()
        default_name = f"bst_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = filedialog.asksaveasfilename(
            initialdir=default_dir,
            initialfile=default_name,
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="保存树到文件"
        )
        tree_dict = storage.tree_to_dict(self.model.root)
        
        metadata = {
            "saved_at": datetime.now().isoformat(),
            "node_count": len(tree_dict.get("nodes", [])) if isinstance(tree_dict, dict) else 0
        }
        payload = {"type": "tree", "tree": tree_dict, "metadata": metadata}
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        messagebox.showinfo("成功", f"二叉搜索树已保存到：\n{filepath}")
        self.update_status("保存成功")

    def load_tree(self):
        default_dir = self._ensure_tree_folder()
        filepath = filedialog.askopenfilename(
            initialdir=default_dir,
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="从文件加载二叉树"
        )
        with open(filepath, "r", encoding="utf-8") as f:
            obj = json.load(f)
        tree_dict = obj.get("tree", {})
        if hasattr(storage, "tree_dict_to_nodes"):
            new_root = storage.tree_dict_to_nodes(tree_dict, TreeNode)
            self.model.root = new_root
            self.redraw()
            messagebox.showinfo("成功", "二叉树已成功加载并恢复")
            self.update_status("加载成功")
            return

    def compute_positions(self) -> Dict[TreeNode, Tuple[float,float]]:
        pos: Dict[TreeNode, Tuple[float,float]] = {}
        nodes_inorder: List[TreeNode] = []
        depths: Dict[TreeNode, int] = {}

        def inorder(n: Optional[TreeNode], d: int):
            if n is None:
                return
            inorder(n.left, d+1)
            nodes_inorder.append(n)
            depths[n] = d
            inorder(n.right, d+1)

        inorder(self.model.root, 0)
        n = len(nodes_inorder)
        if n == 0:
            return pos
        width = self.canvas_width - 2*self.margin_x
        for i, node in enumerate(nodes_inorder):
            if n == 1:
                x = self.canvas_width / 2
            else:
                x = self.margin_x + i * (width / (n-1))
            y = 60 + depths[node] * self.level_gap
            pos[node] = (x, y)
        return pos

    def redraw(self):
        self.canvas.delete("all")
        self.node_items.clear()
        self.node_to_rect.clear()
        draw_instructions(self)
        if self.model.root is None:
            self.canvas.create_text(self.canvas_width/2, self.canvas_height/2, text="空树", font=("Arial",18), fill="gray")
            return
        pos = self.compute_positions()
        # draw edges first for nicer visuals
        for node, (cx, cy) in pos.items():
            if node.left and node.left in pos:
                lx, ly = pos[node.left]
                self._draw_connection(cx, cy, lx, ly)
            if node.right and node.right in pos:
                rx, ry = pos[node.right]
                self._draw_connection(cx, cy, rx, ry)
        # draw nodes
        for node, (cx, cy) in pos.items():
            self._draw_node(node, cx, cy)

    def _draw_connection(self, cx, cy, tx, ty):
        # draw two-stage line
        top = cy + self.node_h/2
        bot = ty - self.node_h/2
        mid_y = (top + bot) / 2
        l1 = self.canvas.create_line(cx, top, cx, mid_y, width=2)
        l2 = self.canvas.create_line(cx, mid_y, tx, bot, arrow=LAST, width=2)
        self.node_items += [l1, l2]

    def _draw_node(self, node: TreeNode, cx: float, cy: float):
        left = cx - self.node_w/2
        top = cy - self.node_h/2
        right = cx + self.node_w/2
        bottom = cy + self.node_h/2
        rect = self.canvas.create_rectangle(left, top, right, bottom, fill="#F0F8FF", outline="black", width=2)
        self.node_to_rect[node] = rect
        self.node_items.append(rect)
        # vertical splits
        x1 = left + self.left_cell_w
        x2 = x1 + self.center_cell_w
        v1 = self.canvas.create_line(x1, top, x1, bottom, width=1)
        v2 = self.canvas.create_line(x2, top, x2, bottom, width=1)
        self.node_items += [v1, v2]
        self.canvas.create_text((x1+x2)/2, (top+bottom)/2, text=str(node.val), font=("Arial",12,"bold"))
        
    def parse_value(self, s: str):
        s = s.strip()
        try:
            return int(s)
        except Exception:
            try:
                return float(s)
            except Exception:
                return s

    def insert_direct(self):
        text = self.input_var.get().strip()
        if not text:
            messagebox.showinfo("提示", "请输入值或逗号分隔的值")
            return
        items = [self.parse_value(s) for s in text.split(",") if s.strip() != ""]
        for v in items:
            self.model.insert(v)
        self.redraw()
        self.update_status(f"已插入 {len(items)} 个节点")

    def start_insert_animated(self):
        if self.animating:
            return
        text = self.input_var.get().strip()
        if not text:
            messagebox.showinfo("提示", "请输入值或逗号分隔的值")
            return  
        items = [self.parse_value(s) for s in text.split(",") if s.strip() != ""]
        if not items:
            return
        self.animating = True
        self.clear_guide()
        self.update_guide(f"🚀 开始插入操作：将依次插入 {len(items)} 个值")
        self.window.after(1000, lambda: self._insert_seq(items, 0))

    def _insert_seq(self, items: List[str], idx: int):
        if idx >= len(items):
            self.animating = False
            self.update_status("插入完成")
            self.update_guide("✅ 所有插入操作已完成！")
            self.window.after(2000, self.clear_guide)
            return
            
        val = items[idx]
        remaining = len(items) - idx - 1
        self.update_guide(f"📥 准备插入第 {idx+1}/{len(items)} 个值: {val} ({remaining} 个待插入)")
        self.window.after(800, lambda: self._animate_search_path_for_insert(val, items, idx))

    def _animate_search_path_for_insert(self, val: str, items: List[str], idx: int):
        path_nodes = []
        explanations = []
        
        cur = self.model.root
        if cur is None:
            self.update_guide(f"🌱 树为空，将 {val} 作为根节点插入")
            self.redraw()
            self.window.after(800, lambda: self._finalize_insert_and_continue(val, items, idx))
            return

        # 构建路径和解释
        step_count = 0
        while cur:
            path_nodes.append(cur)
            step_count += 1
            cmp = self.model.compare_values(val, cur.val)
            
            if cmp == 0:
                explanation = f"🔍 步骤{step_count}: {val} = {cur.val}，向右子树移动（BST允许重复值）"
                cur = cur.right
            elif cmp < 0:
                explanation = f"🔍 步骤{step_count}: {val} < {cur.val}，向左子树移动（较小值在左）"
                cur = cur.left
            else:
                explanation = f"🔍 步骤{step_count}: {val} > {cur.val}，向右子树移动（较大值在右）"
                cur = cur.right
                
            explanations.append(explanation)

        self._play_highlight_sequence_with_explanations(path_nodes, explanations, val, items, idx)

    def _play_highlight_sequence_with_explanations(self, nodes: List[TreeNode], explanations: List[str], val: str, items: List[str], idx: int):
        if not nodes:
            self.update_guide(f"📍 找到插入位置，准备插入新节点 {val}")
            self.window.after(800, lambda: self._finalize_insert_and_continue(val, items, idx))
            return
            
        i = 0
        def step():
            nonlocal i
            if i >= len(nodes):
                self.update_guide(f"📍 搜索完成，准备在适当位置插入 {val}")
                self.window.after(800, lambda: self._finalize_insert_and_continue(val, items, idx))
                return
                
            node = nodes[i]
            explanation = explanations[i] if i < len(explanations) else f"访问节点 {node.val}"
            
            self.redraw()
            if node in self.node_to_rect:
                rid = self.node_to_rect[node]
                self.canvas.itemconfig(rid, fill="yellow")
                
            self.update_status(f"插入 {val}: 步骤 {i+1}/{len(nodes)}")
            self.update_guide(explanation)
            
            i += 1
            self.window.after(1000, step)  # 增加延迟以便阅读说明
            
        step()

    def _finalize_insert_and_continue(self, val, items, idx):
        # 执行实际插入
        new_node = self.model.insert(val)
        pos_map = self.compute_positions()
        
        if new_node not in pos_map:
            self.redraw()
            self.update_guide(f"✅ 已插入 {val}，继续下一个值")
            self.window.after(800, lambda: self._insert_seq(items, idx+1))
            return
            
        # 显示新节点移动动画
        tx, ty = pos_map[new_node]
        sx, sy = self.canvas_width/2, 20
        
        self.update_guide(f"🎯 正在将新节点 {val} 放置到正确位置...")
        
        # 创建移动的新节点
        left = sx - self.node_w/2
        top = sy - self.node_h/2
        right = sx + self.node_w/2
        bottom = sy + self.node_h/2
        
        temp_rect = self.canvas.create_rectangle(left, top, right, bottom, fill="#C6F6D5", outline="black", width=2)
        x1 = left + self.left_cell_w
        x2 = x1 + self.center_cell_w
        temp_text = self.canvas.create_text((x1+x2)/2, (top+bottom)/2, text=str(val), font=("Arial",12,"bold"))

        steps = 30
        dx = (tx - sx)/steps
        dy = (ty - sy)/steps
        delay = 15

        def step(i=0):
            if i < steps:
                self.canvas.move(temp_rect, dx, dy)
                self.canvas.move(temp_text, dx, dy)
                self.window.after(delay, lambda: step(i+1))
            else:
                try:
                    self.canvas.delete(temp_rect)
                    self.canvas.delete(temp_text)
                except Exception:
                    pass
                    
                # 重绘完整树
                self.redraw()
                
                # 高亮显示新节点
                if new_node in self.node_to_rect:
                    rid = self.node_to_rect[new_node]
                    self.canvas.itemconfig(rid, fill="lightgreen")
                    self.update_guide(f"✅ 成功插入 {val}！新节点已放置在正确位置")
                    
                    def unhigh():
                        try:
                            self.canvas.itemconfig(rid, fill="#F0F8FF")
                        except Exception:
                            pass
                        # 继续插入下一个值
                        self.window.after(500, lambda: self._insert_seq(items, idx+1))
                    self.window.after(1000, unhigh)
                else:
                    self.window.after(500, lambda: self._insert_seq(items, idx+1))

        step()

    def start_search_animated(self):
        if self.animating:
            return
        raw = self.input_var.get().strip()
        if not raw:
            messagebox.showinfo("提示", "请输入要查找的值")
            return
        val = self.parse_value(raw)
        self.animating = True
        self.clear_guide()
        
        self.update_guide(f"🔎 开始查找值 {val}：从根节点开始比较")
        
        path_nodes = []
        explanations = []
        cur = self.model.root
        
        if cur is None:
            self.update_guide("❌ 树为空，无法查找")
            self.animating = False
            return
        
        step_count = 0
        while cur:
            step_count += 1
            path_nodes.append(cur)
            cmp = self.model.compare_values(val, cur.val)
            
            if cmp == 0:
                explanations.append(f"🎉 步骤{step_count}: 找到目标值 {val}！查找成功")
                break
            elif cmp < 0:
                explanations.append(f"🔍 步骤{step_count}: {val} < {cur.val}，向左子树继续查找")
                cur = cur.left
            else:
                explanations.append(f"🔍 步骤{step_count}: {val} > {cur.val}，向右子树继续查找")
                cur = cur.right
                
        found = (path_nodes and self.model.compare_values(val, path_nodes[-1].val) == 0)
        
        if not found and path_nodes:
            explanations.append(f"❌ 步骤{step_count}: 到达叶子节点，未找到值 {val}，查找失败")
            
        i = 0
        def step():
            nonlocal i
            if i >= len(path_nodes):
                self.animating = False
                if found:
                    node = path_nodes[-1]
                    self.redraw()
                    if node in self.node_to_rect:
                        rid = self.node_to_rect[node]
                        self.canvas.itemconfig(rid, fill="#4CAF50")
                        self.update_guide(f"🎉 查找成功！在BST中找到值 {val}")
                    self.window.after(1500, lambda: self.canvas.itemconfig(rid, fill="#F0F8FF") if 'rid' in locals() else None)
                else:
                    self.update_guide(f"❌ 查找失败：BST中不存在值 {val}")
                return
                
            node = path_nodes[i]
            explanation = explanations[i] if i < len(explanations) else f"访问节点 {node.val}"
            
            self.redraw()
            if node in self.node_to_rect:
                rid = self.node_to_rect[node]
                self.canvas.itemconfig(rid, fill="yellow")
                
            self.update_status(f"查找: 步骤 {i+1}/{len(path_nodes)}")
            self.update_guide(explanation)
            
            i += 1
            self.window.after(1000, step)
            
        step()

    def start_delete_animated(self):
        if self.animating:
            return
        raw = self.input_var.get().strip()
        if not raw:
            messagebox.showinfo("提示", "请输入要删除的值")
            return
        val = self.parse_value(raw)
        self.animating = True
        self.clear_guide()
        
        self.update_guide(f"🗑️ 开始删除值 {val}：首先定位目标节点")

        path_nodes = []
        explanations = []
        cur = self.model.root
        
        if cur is None:
            self.update_guide("❌ 树为空，无法删除")
            self.animating = False
            return
        
        step_count = 0
        while cur:
            step_count += 1
            path_nodes.append(cur)
            cmp = self.model.compare_values(val, cur.val)
            
            if cmp == 0:
                explanations.append(f"🎯 步骤{step_count}: 找到要删除的节点 {val}，开始删除操作")
                break
            elif cmp < 0:
                explanations.append(f"🔍 步骤{step_count}: {val} < {cur.val}，向左子树继续查找")
                cur = cur.left
            else:
                explanations.append(f"🔍 步骤{step_count}: {val} > {cur.val}，向右子树继续查找")
                cur = cur.right

        found = (path_nodes and self.model.compare_values(val, path_nodes[-1].val) == 0)
        
        if not found and path_nodes:
            explanations.append(f"❌ 步骤{step_count}: 未找到要删除的值 {val}，删除操作终止")
            
        i = 0
        def step():
            nonlocal i
            if i >= len(path_nodes):
                if not found:
                    self.animating = False
                    self.update_guide(f"❌ 删除失败：BST中不存在值 {val}")
                    return
                self._animate_deletion_process(val, path_nodes[-1])
                return
                
            node = path_nodes[i]
            explanation = explanations[i] if i < len(explanations) else f"访问节点 {node.val}"
            
            self.redraw()
            if node in self.node_to_rect:
                self.canvas.itemconfig(self.node_to_rect[node], fill="yellow")
                
            self.update_status(f"删除：步骤 {i+1}/{len(path_nodes)}")
            self.update_guide(explanation)
            
            i += 1
            self.window.after(1000, step)
            
        step()

    def _animate_deletion_process(self, val, target_node):
        self.redraw()
        if target_node in self.node_to_rect:
            self.canvas.itemconfig(self.node_to_rect[target_node], fill="#FF6B6B")
            self.update_guide(f"🎯 已定位到要删除的节点 {val}，分析节点类型...")
        
        def after_highlight():
            # 情况1：叶子节点
            if target_node.left is None and target_node.right is None:
                self.update_guide(f"🍃 节点 {val} 是叶子节点（无子节点），直接删除")
                def do_delete():
                    self.model.delete(val)
                    self.redraw()
                    self.update_guide(f"✅ 叶子节点 {val} 已成功删除")
                    self.animating = False
                self.window.after(1200, do_delete)
                
            # 情况2：只有一个子节点
            elif target_node.left is None or target_node.right is None:
                child = target_node.left if target_node.left else target_node.right
                child_type = "左" if target_node.left else "右"
                self.update_guide(f"📋 节点 {val} 有一个{child_type}子节点 {child.val}，用子节点替换当前节点")
                
                self.redraw()
                if child in self.node_to_rect:
                    self.canvas.itemconfig(self.node_to_rect[child], fill="#FFD93D")
                    
                def do_transplant():
                    self.model.delete(val)
                    self.redraw()
                    self.update_guide(f"✅ 已删除 {val}，其{child_type}子节点 {child.val} 提升到该位置")
                    self.animating = False
                self.window.after(1200, do_transplant)
                
            # 情况3：有两个子节点
            else:
                self.update_guide(f"🔄 节点 {val} 有两个子节点，寻找右子树中的最小值作为后继节点")
                succ = self.model.find_min(target_node.right)
                
                self.redraw()
                if succ in self.node_to_rect:
                    self.canvas.itemconfig(self.node_to_rect[succ], fill="#6BCF77")
                    self.update_guide(f"📌 找到后继节点 {succ.val}，用后继节点的值替换目标节点的值")
                    
                def swap_and_delete():
                    # 交换值
                    old_val = target_node.val
                    target_node.val = succ.val
                    succ.val = old_val
                    
                    self.redraw()
                    if target_node in self.node_to_rect:
                        self.canvas.itemconfig(self.node_to_rect[target_node], fill="#4ECDC4")
                        
                    self.update_guide(f"🔄 值已交换：节点现在包含 {target_node.val}，原值移到后继节点位置")
                    
                    def final_del():
                        self.update_guide(f"🗑️ 删除原后继节点（现在包含值 {old_val}）")
                        self.model.delete_node(succ)  
                        self.redraw()
                        self.update_guide(f"✅ 删除完成！BST结构已保持有序性")
                        self.animating = False
                    self.window.after(1200, final_del)
                    
                self.window.after(1200, swap_and_delete)
                
        self.window.after(800, after_highlight)

    def clear_canvas(self):
        if self.animating:
            return
        self.model = BSTModel()
        self.redraw()
        self.update_status("已清空")
        self.clear_guide()

    def back_to_main(self):
        if self.animating:
            messagebox.showinfo("提示", "正在动画，不能返回")
            return
        self.window.destroy()
        
if __name__ == '__main__':
    w = Tk()
    w.title("BST 可视化 - 分步引导模式")
    w.geometry("1350x780")  # 增加高度以容纳新的引导标签
    BSTVisualizer(w)
    w.mainloop()