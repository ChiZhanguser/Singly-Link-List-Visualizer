from tkinter import * 
from tkinter import ttk, messagebox
import traceback, sys
import random, math, time
from utils.image_utils import ImageProcessor
import tempfile
import shutil
import re

# ============== 现代化配色方案 ==============
THEME = {
    # 主色调
    "primary": "#6366f1",        # 靛蓝紫 - 主色
    "primary_light": "#818cf8",  # 浅紫
    "primary_dark": "#4f46e5",   # 深紫
    
    # 背景色
    "bg_dark": "#0f172a",        # 深蓝黑 - 主背景
    "bg_sidebar": "#1e293b",     # 侧边栏背景
    "bg_card": "#1e293b",        # 卡片背景
    "bg_hover": "#334155",       # 悬停背景
    "bg_active": "#475569",      # 激活背景
    
    # 顶栏
    "topbar_bg": "#ffffff",      # 顶栏背景
    "topbar_border": "#e2e8f0",  # 顶栏边框
    
    # 文本色
    "text_primary": "#f8fafc",   # 主文本 (白)
    "text_secondary": "#94a3b8", # 次要文本 (灰)
    "text_muted": "#64748b",     # 更淡的文本
    "text_dark": "#1e293b",      # 深色文本
    
    # 强调色
    "accent_green": "#10b981",   # 绿色
    "accent_blue": "#3b82f6",    # 蓝色
    "accent_orange": "#f59e0b",  # 橙色
    "accent_red": "#ef4444",     # 红色
    "accent_pink": "#ec4899",    # 粉色
    "accent_cyan": "#06b6d4",    # 青色
    
    # 状态栏
    "status_bg": "#020617",      # 状态栏背景
    "status_text": "#64748b",    # 状态栏文本
}

# 数据结构图标映射
DS_ICONS = {
    "linked_list": "🔗",
    "sequence": "📋",
    "stack": "📚",
    "binary_tree": "🌲",
    "bst": "🔍",
    "huffman": "📊",
    "trie": "🔤",
    "bplus": "📁",
    "avl": "⚖️",
    "rbt": "🔴",
    "cqueue": "🔄",
    "hashtable": "🗂️",
}

# 数据结构分类
DS_CATEGORIES = {
    "线性结构": ["linked_list", "sequence", "stack", "cqueue"],
    "树形结构": ["binary_tree", "bst", "avl", "rbt", "huffman", "trie", "bplus"],
    "散列结构": ["hashtable"],
}

def try_import(name, pkg):
    try:
        mod = __import__(pkg, fromlist=[name])
        return getattr(mod, name)
    except Exception:
        return None


LinkList = try_import("LinkList", "linked_list.linked_list_visual")
SequenceListVisualizer = try_import("SequenceListVisualizer", "sequence_list.sequence_list_visual")
StackVisualizer = try_import("StackVisualizer", "stack.stack_visual")
BinaryTreeVisualizer = try_import("BinaryTreeVisualizer", "binary_tree.linked_storage.linked_storage_visual")
BSTVisualizer = try_import("BSTVisualizer", "binary_tree.bst.bst_visual")
HuffmanVisualizer = try_import("HuffmanVisualizer", "binary_tree.huffman_tree.huffman_visual")
AVLVisualizer = try_import("AVLVisualizer", "avl.avl_visual")
RBTVisualizer = try_import("RBTVisualizer", "rbt.rbt_visual")
CircularQueueVisualizer = try_import("CircularQueueVisualizer", "circular_queue.circular_queue_visual")
TrieVisualizer = try_import("TrieVisualizer", "trie.trie_visual")
BPlusVisualizer = try_import("BPlusVisualizer", "bplustree.bplustree_visual")
HashtableVisualizer = try_import("HashtableVisualizer", "hashtable.hashtable_visual")
ChatWindow = try_import("ChatWindow", "llm.chat_window")


class EmbedHost(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.configure(bg="")
        self.pack(fill=BOTH, expand=True)

    def title(self, *_args, **_kwargs):
        return None
    def geometry(self, *_args, **_kwargs):
        return None
    def minsize(self, *_args, **_kwargs):
        return None
    def maxsize(self, *_args, **_kwargs):
        return None
    def resizable(self, *_args, **_kwargs):
        return None


# ============== 沉浸式高端落地页 ==============
class LandingPage:
    """沉浸式深色落地页 - 图片背景高端设计"""
    
    # 背景图片路径 - 请将图片放在这个位置
    BG_IMAGE_PATH = "assets/landing_bg.jpg"
    
    def __init__(self, root, on_start_callback):
        self.root = root
        self.on_start_callback = on_start_callback
        self.root.title("DS Visual")
        self.root.geometry("1500x850")
        self.root.minsize(1200, 700)
        self.root.configure(bg="#0a0a0a")
        
        # 动画状态
        self._animation_ids = []
        self._bg_image = None
        self._bg_photo = None
        
        # 构建界面
        self._build_ui()
        
        # 绑定窗口大小变化事件
        self.root.bind("<Configure>", self._on_resize)
    
    def _load_background_image(self):
        """加载背景图片"""
        try:
            from PIL import Image, ImageTk, ImageEnhance, ImageFilter
            import os
            
            # 获取图片路径
            script_dir = os.path.dirname(os.path.abspath(__file__))
            img_path = os.path.join(script_dir, self.BG_IMAGE_PATH)
            
            # 检查文件是否存在
            if not os.path.exists(img_path):
                print(f"[提示] 背景图片未找到: {img_path}")
                print(f"[提示] 请将图片放在: {img_path}")
                return False
            
            # 加载原始图片
            self._original_image = Image.open(img_path)
            
            # 获取窗口尺寸
            w = self.root.winfo_width() or 1500
            h = self.root.winfo_height() or 850
            
            # 调整图片大小（保持比例，覆盖整个窗口）
            img_ratio = self._original_image.width / self._original_image.height
            win_ratio = w / h
            
            if img_ratio > win_ratio:
                # 图片更宽，以高度为准
                new_h = h
                new_w = int(h * img_ratio)
            else:
                # 图片更高，以宽度为准
                new_w = w
                new_h = int(w / img_ratio)
            
            # 缩放图片
            resized = self._original_image.resize((new_w, new_h), Image.Resampling.LANCZOS)
            
            # 裁剪到窗口大小（居中裁剪）
            left = (new_w - w) // 2
            top = (new_h - h) // 2
            cropped = resized.crop((left, top, left + w, top + h))
            
            # 可选：添加暗化效果使文字更清晰
            enhancer = ImageEnhance.Brightness(cropped)
            darkened = enhancer.enhance(0.7)  # 0.7 = 70% 亮度
            
            # 转换为 Tkinter 可用的格式
            self._bg_photo = ImageTk.PhotoImage(darkened)
            
            return True
            
        except ImportError:
            print("[错误] 需要安装 Pillow 库: pip install Pillow")
            return False
        except Exception as e:
            print(f"[错误] 加载背景图片失败: {e}")
            return False
    
    def _build_ui(self):
        """构建沉浸式UI"""
        # 主容器
        self.main_container = Frame(self.root, bg="#0a0a0a")
        self.main_container.pack(fill=BOTH, expand=True)
        
        # 全屏背景Canvas
        self.bg_canvas = Canvas(self.main_container, highlightthickness=0, bg="#0a0a0a")
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        
        # 尝试加载背景图片
        self.root.update_idletasks()
        if self._load_background_image():
            # 显示背景图片
            self._bg_image_id = self.bg_canvas.create_image(0, 0, anchor="nw", 
                                                            image=self._bg_photo)
        else:
            # 如果图片加载失败，使用纯色背景 + 提示
            self._draw_fallback_bg()
        
        # 添加半透明暗色遮罩使文字更清晰（仅覆盖背景，不覆盖文字）
        self._add_dark_overlay()
        
        # 延迟创建文字内容（确保Canvas已完全渲染）
        self.root.after(100, self._create_canvas_content)
    
    def _draw_fallback_bg(self):
        """当图片不存在时绘制备用背景"""
        w = 1600
        h = 900
        
        # 深色渐变背景
        steps = 50
        for i in range(steps):
            t = i / steps
            r = int(10 + t * 8)
            g = int(10 + t * 6)
            b = int(12 + t * 8)
            color = f"#{r:02x}{g:02x}{b:02x}"
            y0 = int(i * h / steps)
            y1 = int((i + 1) * h / steps)
            self.bg_canvas.create_rectangle(0, y0, w, y1, fill=color, outline="", tags="bg")
        
        # 中央光晕
        cx, cy = w // 2, h // 2 - 50
        for radius in range(350, 50, -15):
            alpha = (350 - radius) / 300
            r = int(30 + alpha * 40)
            g = int(25 + alpha * 35)
            b = int(20 + alpha * 30)
            color = f"#{r:02x}{g:02x}{b:02x}"
            self.bg_canvas.create_oval(cx - radius, cy - radius,
                                      cx + radius, cy + radius,
                                      fill=color, outline="", tags="glow")
        
        # 提示文字
        self.bg_canvas.create_text(w // 2, h - 50,
                                   text="提示：请将背景图片放在 assets/landing_bg.jpg",
                                   fill="#666666", font=("微软雅黑", 10))
    
    def _add_dark_overlay(self):
        """添加半透明暗色遮罩 - 使文字更清晰"""
        w = 1600
        h = 900
        
        # 使用 stipple 创建半透明效果的全屏遮罩（更轻的遮罩）
        self.bg_canvas.create_rectangle(
            0, 0, w, h,
            fill="#000000",
            stipple="gray25",  # 25% 透明度，更轻
            outline="",
            tags="dark_overlay"
        )
    
    def _create_canvas_content(self):
        """创建Canvas上的所有内容元素"""
        # 确保窗口尺寸已更新
        self.root.update_idletasks()
        
        # 构建中央内容
        self._build_center_content()
        
        # 构建底部导航（Canvas版本）
        self._build_bottom_nav_canvas()
        
        # 启动入场动画（稍微延迟确保Canvas已渲染）
        self.root.after(300, self._start_entrance_animation)
    
    def _on_resize(self, event):
        """窗口大小变化时重新加载背景图片"""
        # 使用延迟避免频繁重绘
        if hasattr(self, '_resize_job'):
            self.root.after_cancel(self._resize_job)
        
        self._resize_job = self.root.after(200, self._update_background)
    
    def _update_background(self):
        """更新背景图片尺寸"""
        if hasattr(self, '_original_image'):
            try:
                from PIL import Image, ImageTk, ImageEnhance
                
                w = self.root.winfo_width()
                h = self.root.winfo_height()
                
                if w < 100 or h < 100:
                    return
                
                # 重新计算尺寸
                img_ratio = self._original_image.width / self._original_image.height
                win_ratio = w / h
                
                if img_ratio > win_ratio:
                    new_h = h
                    new_w = int(h * img_ratio)
                else:
                    new_w = w
                    new_h = int(w / img_ratio)
                
                resized = self._original_image.resize((new_w, new_h), Image.Resampling.LANCZOS)
                
                left = (new_w - w) // 2
                top = (new_h - h) // 2
                cropped = resized.crop((left, top, left + w, top + h))
                
                enhancer = ImageEnhance.Brightness(cropped)
                darkened = enhancer.enhance(0.7)
                
                self._bg_photo = ImageTk.PhotoImage(darkened)
                self.bg_canvas.itemconfig(self._bg_image_id, image=self._bg_photo)
                
            except Exception as e:
                print(f"更新背景失败: {e}")
    
    def _build_center_content(self):
        """构建中央主内容 - 直接在Canvas上绘制，无黑框"""
        # 使用固定的窗口尺寸（确保元素在正确位置）
        w = 1500
        h = 850
        
        # 中心位置（略微偏上，给底部导航留空间）
        cx, cy = w // 2, h // 2 - 80
        
        print(f"[内容] 创建Canvas元素，中心位置: ({cx}, {cy})")
        
        # 存储Canvas元素ID
        self._canvas_elements = {}
        
        # ===== 在 bg_canvas 上直接绘制文字 =====
        
        # 左侧大字母 D - 初始透明（不绘制，动画时再绘制）
        self._canvas_elements['letter_d'] = self.bg_canvas.create_text(
            cx - 200, cy - 30,
            text="D",
            font=("Segoe UI Light", 160),
            fill="",  # 初始不可见
            anchor="center",
            tags="anim_text"
        )
        
        # 右侧大字母 S
        self._canvas_elements['letter_s'] = self.bg_canvas.create_text(
            cx + 200, cy - 30,
            text="S",
            font=("Segoe UI Light", 160),
            fill="",
            anchor="center",
            tags="anim_text"
        )
        
        # 中间分隔线 - 初始宽度为0
        self._canvas_elements['line'] = self.bg_canvas.create_line(
            cx, cy - 30, cx, cy - 30,  # 初始长度为0
            fill="#ffffff",
            width=3,
            tags="anim_line"
        )
        
        # 上方小字 - DATA STRUCTURE
        self._canvas_elements['text_top'] = self.bg_canvas.create_text(
            cx, cy - 70,
            text="",
            font=("Segoe UI", 13),
            fill="#a0a0a0",
            anchor="center",
            tags="anim_text"
        )
        
        # 下方小字 - VISUALIZER  
        self._canvas_elements['text_bottom'] = self.bg_canvas.create_text(
            cx, cy + 15,
            text="",
            font=("Segoe UI", 13),
            fill="#a0a0a0",
            anchor="center",
            tags="anim_text"
        )
        
        # 主标语
        self._canvas_elements['tagline'] = self.bg_canvas.create_text(
            cx, cy + 120,
            text="",
            font=("微软雅黑", 20),
            fill="#ffffff",
            anchor="center",
            tags="anim_text"
        )
        
        # 副标语
        self._canvas_elements['subtitle'] = self.bg_canvas.create_text(
            cx, cy + 165,
            text="",
            font=("微软雅黑", 12),
            fill="#888888",
            anchor="center",
            tags="anim_text"
        )
        
        # ===== 按钮 - 使用Canvas绘制 =====
        btn_y = cy + 250
        btn_width = 180
        btn_height = 50
        
        # 按钮边框（初始不可见）
        self._canvas_elements['btn_border'] = self.bg_canvas.create_rectangle(
            cx - btn_width//2, btn_y - btn_height//2,
            cx + btn_width//2, btn_y + btn_height//2,
            outline="",
            width=2,
            tags="anim_btn"
        )
        
        # 按钮文字
        self._canvas_elements['btn_text'] = self.bg_canvas.create_text(
            cx, btn_y,
            text="",
            font=("微软雅黑", 13),
            fill="",
            anchor="center",
            tags="anim_btn"
        )
        
        # 按钮悬停区域（透明矩形用于检测鼠标）
        self._btn_area = (cx - btn_width//2, btn_y - btn_height//2,
                         cx + btn_width//2, btn_y + btn_height//2)
        
        # 绑定按钮事件
        self.bg_canvas.tag_bind("anim_btn", "<Enter>", self._on_btn_enter)
        self.bg_canvas.tag_bind("anim_btn", "<Leave>", self._on_btn_leave)
        self.bg_canvas.tag_bind("anim_btn", "<Button-1>", lambda e: self._on_start_click())
        
        # 绑定整个Canvas的点击（备用）
        def on_canvas_click(event):
            x, y = event.x, event.y
            if (self._btn_area[0] <= x <= self._btn_area[2] and 
                self._btn_area[1] <= y <= self._btn_area[3]):
                self._on_start_click()
        
        self.bg_canvas.bind("<Button-1>", on_canvas_click)
    
    def _on_btn_enter(self, event):
        """按钮悬停进入"""
        if self.bg_canvas.itemcget(self._canvas_elements['btn_text'], 'text'):
            self.bg_canvas.itemconfig(self._canvas_elements['btn_border'], 
                                     fill="#ffffff", outline="#ffffff")
            self.bg_canvas.itemconfig(self._canvas_elements['btn_text'], fill="#0a0a0a")
            self.bg_canvas.config(cursor="hand2")
    
    def _on_btn_leave(self, event):
        """按钮悬停离开"""
        if self.bg_canvas.itemcget(self._canvas_elements['btn_text'], 'text'):
            self.bg_canvas.itemconfig(self._canvas_elements['btn_border'], 
                                     fill="", outline="#ffffff")
            self.bg_canvas.itemconfig(self._canvas_elements['btn_text'], fill="#ffffff")
            self.bg_canvas.config(cursor="")
        
        # 启动入场动画序列
        self.root.after(500, self._start_entrance_animation)
    
    def _start_entrance_animation(self):
        """启动入场动画序列 - Canvas版本"""
        if getattr(self, '_destroyed', False):
            return
        
        # 动画时间线 - 逐步显示元素
        aid1 = self.root.after(0, lambda: self._animate_canvas_fade('letter_d', "#ffffff", 600))
        aid2 = self.root.after(300, lambda: self._animate_canvas_fade('letter_s', "#ffffff", 600))
        aid3 = self.root.after(700, self._animate_line_expand)
        aid4 = self.root.after(1100, lambda: self._animate_canvas_typewriter('text_top', "DATA  STRUCTURE", 35))
        aid5 = self.root.after(1700, lambda: self._animate_canvas_typewriter('text_bottom', "VISUALIZER", 45))
        aid6 = self.root.after(2200, lambda: self._animate_canvas_text('tagline', "让抽象的数据结构，变得触手可及"))
        aid7 = self.root.after(2700, lambda: self._animate_canvas_text('subtitle', "交互式可视化  ·  实时演示  ·  AI 智能辅助"))
        aid8 = self.root.after(3200, self._animate_button_appear)
        aid9 = self.root.after(3700, self._animate_bottom_nav)
        
        self._animation_ids.extend([aid1, aid2, aid3, aid4, aid5, aid6, aid7, aid8, aid9])
    
    def _animate_canvas_fade(self, element_key, target_color, duration):
        """Canvas元素淡入动画"""
        if getattr(self, '_destroyed', False):
            return
        if element_key not in self._canvas_elements:
            return
        
        element_id = self._canvas_elements[element_key]
        steps = 25
        step_time = duration // steps
        
        def fade_step(step):
            if getattr(self, '_destroyed', False) or step > steps:
                return
            
            t = step / steps
            t = 1 - (1 - t) ** 3  # ease out cubic
            
            brightness = int(t * 255)
            color = f"#{brightness:02x}{brightness:02x}{brightness:02x}"
            
            try:
                self.bg_canvas.itemconfig(element_id, fill=color)
            except:
                return  # Canvas已销毁，停止动画
            
            aid = self.root.after(step_time, lambda: fade_step(step + 1))
            self._animation_ids.append(aid)
        
        fade_step(1)
    
    def _animate_line_expand(self):
        """分隔线从中心向两边展开"""
        if getattr(self, '_destroyed', False):
            return
        if 'line' not in self._canvas_elements:
            return
        
        cx = 750  # 固定中心位置
        cy = 265  # 固定Y位置
        
        target_half_width = 180
        duration = 600
        steps = 35
        step_time = duration // steps
        
        def expand_step(step):
            if getattr(self, '_destroyed', False) or step > steps:
                return
            
            t = step / steps
            t = 1 - (1 - t) ** 3
            
            half_width = int(t * target_half_width)
            
            try:
                self.bg_canvas.coords(
                    self._canvas_elements['line'],
                    cx - half_width, cy,
                    cx + half_width, cy
                )
            except:
                return
            
            aid = self.root.after(step_time, lambda: expand_step(step + 1))
            self._animation_ids.append(aid)
        
        expand_step(0)
    
    def _animate_canvas_typewriter(self, element_key, text, char_delay):
        """Canvas文字打字机效果"""
        if getattr(self, '_destroyed', False):
            return
        if element_key not in self._canvas_elements:
            return
        
        element_id = self._canvas_elements[element_key]
        
        def type_char(index):
            if getattr(self, '_destroyed', False) or index > len(text):
                return
            
            try:
                self.bg_canvas.itemconfig(element_id, text=text[:index])
            except:
                return
            
            aid = self.root.after(char_delay, lambda: type_char(index + 1))
            self._animation_ids.append(aid)
        
        type_char(0)
    
    def _animate_canvas_text(self, element_key, text):
        """Canvas文字淡入显示"""
        if getattr(self, '_destroyed', False):
            return
        if element_key not in self._canvas_elements:
            return
        
        element_id = self._canvas_elements[element_key]
        
        # 先设置文字
        try:
            self.bg_canvas.itemconfig(element_id, text=text, fill="#000000")
        except:
            return
        
        # 渐变到目标颜色
        target_brightness = 255 if element_key == 'tagline' else 136
        steps = 20
        step_time = 25
        
        def fade_step(step):
            if getattr(self, '_destroyed', False) or step > steps:
                return
            
            t = step / steps
            brightness = int(t * target_brightness)
            color = f"#{brightness:02x}{brightness:02x}{brightness:02x}"
            
            try:
                self.bg_canvas.itemconfig(element_id, fill=color)
            except:
                return
            
            aid = self.root.after(step_time, lambda: fade_step(step + 1))
            self._animation_ids.append(aid)
        
        fade_step(0)
    
    def _animate_button_appear(self):
        """按钮出现动画 - Canvas版本"""
        if getattr(self, '_destroyed', False):
            return
        try:
            self.bg_canvas.itemconfig(self._canvas_elements['btn_border'], outline="#ffffff")
            self.bg_canvas.itemconfig(self._canvas_elements['btn_text'], text="进 入 平 台", fill="#ffffff")
        except:
            pass
    
    def _animate_bottom_nav(self):
        """底部导航淡入 - Canvas版本"""
        if getattr(self, '_destroyed', False):
            return
        
        # 逐个显示底部导航文字
        if hasattr(self, '_nav_text_ids'):
            def show_nav(index):
                if getattr(self, '_destroyed', False) or index >= len(self._nav_text_ids):
                    return
                try:
                    self.bg_canvas.itemconfig(self._nav_text_ids[index], fill="#909090")
                except:
                    return
                aid = self.root.after(80, lambda: show_nav(index + 1))
                self._animation_ids.append(aid)
            
            show_nav(0)
        
        # 显示版权信息
        def show_copyright():
            if getattr(self, '_destroyed', False):
                return
            if hasattr(self, '_copyright_id'):
                try:
                    self.bg_canvas.itemconfig(self._copyright_id, fill="#606060")
                except:
                    pass
        
        aid = self.root.after(800, show_copyright)
        self._animation_ids.append(aid)
    
    def _build_bottom_nav_canvas(self):
        """在Canvas上构建底部导航"""
        w = self.root.winfo_width() or 1500
        h = self.root.winfo_height() or 850
        
        # 底部导航Y位置
        nav_y = h - 60
        
        # 数据结构列表
        structures = ["链表", "栈", "队列", "二叉树", "BST", "AVL", "红黑树", "哈希表"]
        
        # 计算总宽度和起始位置
        total_width = len(structures) * 70 + (len(structures) - 1) * 20
        start_x = (w - total_width) // 2
        
        self._nav_text_ids = []
        
        for i, name in enumerate(structures):
            x = start_x + i * 90 + 35
            
            # 创建导航文字（初始不可见）
            text_id = self.bg_canvas.create_text(
                x, nav_y,
                text=name,
                font=("微软雅黑", 11),
                fill="",  # 初始不可见
                anchor="center",
                tags="nav_item"
            )
            self._nav_text_ids.append(text_id)
            
            # 分隔符
            if i < len(structures) - 1:
                sep_id = self.bg_canvas.create_text(
                    x + 45, nav_y,
                    text="·",
                    font=("Arial", 12),
                    fill="",
                    anchor="center",
                    tags="nav_sep"
                )
                self._nav_text_ids.append(sep_id)
        
        # 版权信息
        self._copyright_id = self.bg_canvas.create_text(
            w // 2, h - 25,
            text="© 2024 DS Visual · 数据结构可视化学习平台",
            font=("Segoe UI", 9),
            fill="",  # 初始不可见
            anchor="center",
            tags="copyright"
        )
        
        # 绑定导航悬停效果
        def on_nav_enter(event):
            item = self.bg_canvas.find_closest(event.x, event.y)
            if item:
                current_fill = self.bg_canvas.itemcget(item[0], 'fill')
                if current_fill and current_fill != "":
                    self.bg_canvas.itemconfig(item[0], fill="#ffffff")
                    self.bg_canvas.config(cursor="hand2")
        
        def on_nav_leave(event):
            for tid in self._nav_text_ids:
                current_fill = self.bg_canvas.itemcget(tid, 'fill')
                if current_fill == "#ffffff":
                    self.bg_canvas.itemconfig(tid, fill="#909090")
            self.bg_canvas.config(cursor="")
        
        self.bg_canvas.tag_bind("nav_item", "<Enter>", on_nav_enter)
        self.bg_canvas.tag_bind("nav_item", "<Leave>", on_nav_leave)
        self.bg_canvas.tag_bind("nav_item", "<Button-1>", lambda e: self._on_start_click())
    
    def _build_bottom_nav(self):
        """占位 - 由Canvas版本替代"""
        pass
    
    def _build_bottom_nav_animated(self):
        """构建底部导航 - 带淡入动画"""
        trans_bg = "#0a0a0a"
        
        nav_frame = Frame(self.main_container, bg=trans_bg)
        nav_frame.place(relx=0.5, rely=0.92, anchor="center")
        
        structures = ["链表", "栈", "队列", "二叉树", "BST", "AVL", "红黑树", "哈希表"]
        self._nav_labels = []
        
        for i, name in enumerate(structures):
            btn = Label(nav_frame, text=name, bg=trans_bg, fg=trans_bg,  # 初始不可见
                       font=("微软雅黑", 10), cursor="hand2", padx=12)
            btn.pack(side=LEFT)
            self._nav_labels.append(btn)
            
            if i < len(structures) - 1:
                sep = Label(nav_frame, text="·", bg=trans_bg, fg=trans_bg,
                           font=("Arial", 10))
                sep.pack(side=LEFT, padx=3)
                self._nav_labels.append(sep)
            
            # 悬停效果
            def make_hover(widget):
                def on_enter(e):
                    current_fg = widget.cget('fg')
                    if current_fg != trans_bg and current_fg != "#0a0a0a":
                        widget.config(fg="#ffffff")
                def on_leave(e):
                    current_fg = widget.cget('fg')
                    if current_fg != trans_bg and current_fg != "#0a0a0a":
                        widget.config(fg="#808080")
                return on_enter, on_leave
            
            enter_fn, leave_fn = make_hover(btn)
            btn.bind("<Enter>", enter_fn)
            btn.bind("<Leave>", leave_fn)
            btn.bind("<Button-1>", lambda e: self._on_start_click())
        
        # 逐个淡入导航项
        def fade_in_nav(index):
            if index >= len(self._nav_labels):
                return
            
            label = self._nav_labels[index]
            label.config(fg="#808080" if label.cget('text') != "·" else "#505050")
            
            aid = self.root.after(60, lambda: fade_in_nav(index + 1))
            self._animation_ids.append(aid)
        
        fade_in_nav(0)
        
        # 版权信息
        copyright_frame = Frame(self.main_container, bg=trans_bg)
        copyright_frame.place(relx=0.5, rely=0.97, anchor="center")
        
        copyright_label = Label(copyright_frame, text="",
                               bg=trans_bg, fg=trans_bg, font=("Segoe UI", 9))
        copyright_label.pack()
        
        # 延迟显示版权
        def show_copyright():
            copyright_label.config(text="© 2024 DS Visual · 数据结构可视化学习平台", fg="#505050")
        
        aid = self.root.after(500, show_copyright)
        self._animation_ids.append(aid)
    
    def _build_bottom_nav(self):
        """占位 - 实际由动画函数构建"""
        pass
    
    def _on_start_click(self):
        """点击开始学习"""
        # 标记为已销毁，防止动画继续更新
        self._destroyed = True
        
        # 清理所有动画回调
        for aid in self._animation_ids:
            try:
                self.root.after_cancel(aid)
            except:
                pass
        self._animation_ids.clear()
        
        # 解绑所有事件
        try:
            self.bg_canvas.unbind_all("<Button-1>")
        except:
            pass
        
        # 销毁落地页内容
        try:
            self.main_container.destroy()
        except:
            pass
        
        # 调用回调启动主界面
        self.on_start_callback()
    
    def destroy(self):
        """销毁落地页"""
        for aid in self._animation_ids:
            try:
                self.root.after_cancel(aid)
            except:
                pass
        try:
            self.main_container.destroy()
        except:
            pass


class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("数据结构可视化工具")
        self.root.geometry("1500x820")
        self.root.minsize(1500, 820)
        self.root.configure(bg=THEME["bg_dark"])

        # 背景画布
        self.bg_canvas = Canvas(self.root, highlightthickness=0, bd=0, bg=THEME["bg_dark"])
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        try:
            self.root.tk.call('lower', self.bg_canvas._w)
        except Exception:
            pass
        self._static_stars = [(random.uniform(0,1), random.uniform(0,1), random.uniform(0.5,1.6)) for _ in range(120)]
        self._render_background()
        self.root.after(90, self._animate_stars)
        self._resize_job = None
        self.root.bind("<Configure>", self._on_configure)

        # 主面板
        self.main_pane = PanedWindow(self.root, orient=HORIZONTAL, bg=THEME["bg_dark"], 
                                      sashwidth=2, sashrelief=FLAT)
        self.main_pane.pack(fill=BOTH, expand=True)

        # 侧边栏 - 更现代的设计
        self.sidebar = Frame(self.main_pane, width=240, bg=THEME["bg_sidebar"])
        self.content = Frame(self.main_pane, bg=THEME["bg_dark"])
        self.main_pane.add(self.sidebar)
        self.main_pane.add(self.content)

        # ========== 现代化顶部栏 ==========
        topbar = Frame(self.content, bg=THEME["topbar_bg"], height=72)
        topbar.pack(fill=X, side=TOP)
        topbar.pack_propagate(False)
        
        # 应用现代样式
        self.style = ttk.Style(self.root)
        try:
            self.style.theme_use("clam")
        except Exception:
            pass
        self._apply_hidden_notebook_style()

        # ---- 左侧：Logo和标题 ----
        header_left = Frame(topbar, bg=THEME["topbar_bg"])
        header_left.pack(side=LEFT, padx=24, pady=16)
        
        # Logo容器（渐变效果模拟）
        logo_frame = Frame(header_left, bg=THEME["primary"], width=42, height=42)
        logo_frame.pack(side=LEFT, padx=(0, 14))
        logo_frame.pack_propagate(False)
        logo_label = Label(logo_frame, text="DS", bg=THEME["primary"], fg="white", 
                          font=("Segoe UI", 15, "bold"))
        logo_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # 标题区域
        title_container = Frame(header_left, bg=THEME["topbar_bg"])
        title_container.pack(side=LEFT)
        
        title_label = Label(title_container, text="数据结构可视化", 
                           bg=THEME["topbar_bg"], fg=THEME["text_dark"], 
                           font=("微软雅黑", 16, "bold"))
        title_label.pack(anchor=W)
        
        subtitle_label = Label(title_container, text="Data Structure Visualizer", 
                              bg=THEME["topbar_bg"], fg=THEME["text_muted"], 
                              font=("Segoe UI", 9))
        subtitle_label.pack(anchor=W)

        # ---- 中间：当前结构指示器 ----
        header_center = Frame(topbar, bg=THEME["topbar_bg"])
        header_center.pack(side=LEFT, expand=True, fill=X, padx=30)
        
        # 当前结构标签 - 胶囊样式
        current_frame = Frame(header_center, bg="#f1f5f9")
        current_frame.pack(side=TOP, pady=8)
        
        self.structure_icon_label = Label(current_frame, text="📊", bg="#f1f5f9", 
                                         font=("Segoe UI", 12))
        self.structure_icon_label.pack(side=LEFT, padx=(12, 6), pady=6)
        
        self.structure_label = Label(current_frame, text="选择数据结构", bg="#f1f5f9", 
                                    fg=THEME["primary"], font=("微软雅黑", 10, "bold"),
                                    padx=8, pady=6)
        self.structure_label.pack(side=LEFT, padx=(0, 12))

        # ---- 右侧：功能区域 ----
        header_right = Frame(topbar, bg=THEME["topbar_bg"])
        header_right.pack(side=RIGHT, padx=24, pady=16)

        # 自然语言输入框
        from tkinter import StringVar
        self.nl_var = StringVar(value="")
        
        input_container = Frame(header_right, bg="#f1f5f9")
        input_container.pack(side=LEFT, padx=(0, 16))
        
        input_icon = Label(input_container, text="✨", bg="#f1f5f9", 
                          font=("Segoe UI", 11))
        input_icon.pack(side=LEFT, padx=(14, 8))
        
        self.nl_entry = Entry(input_container, textvariable=self.nl_var, width=36, 
                             font=("Segoe UI", 10), fg=THEME["text_muted"], bg="#f1f5f9", 
                             relief=FLAT, bd=0, highlightthickness=0,
                             insertbackground=THEME["primary"])
        self.nl_entry.insert(0, "输入自然语言命令...")
        self.nl_entry.bind("<FocusIn>", self._on_entry_focus_in)
        self.nl_entry.bind("<FocusOut>", self._on_entry_focus_out)
        self.nl_entry.bind("<Return>", self._on_nl_submit)
        self.nl_entry.pack(side=LEFT, padx=(0, 14), pady=10)

        # 图片上传按钮
        image_btn = Button(header_right, text="📷 识图", fg="white", bg=THEME["accent_green"],
                          activebackground="#059669", activeforeground="white",
                          relief=FLAT, padx=16, pady=8, cursor="hand2",
                          font=("微软雅黑", 9, "bold"),
                          command=self._open_image_upload)
        image_btn.pack(side=LEFT, padx=(0, 10))
        self._bind_button_hover(image_btn, THEME["accent_green"], "#059669")

        # AI 助手按钮
        ai_btn = Button(header_right, text="🤖 AI助手", fg="white", bg=THEME["primary"],
                        activebackground=THEME["primary_dark"], activeforeground="white",
                        relief=FLAT, padx=16, pady=8, cursor="hand2",
                        font=("微软雅黑", 9, "bold"),
                        command=self._open_chat)
        ai_btn.pack(side=LEFT)
        self._bind_button_hover(ai_btn, THEME["primary"], THEME["primary_dark"])

        # 顶部渐变装饰条
        gradient_bar = Canvas(topbar, height=3, bg=THEME["topbar_bg"], highlightthickness=0)
        gradient_bar.pack(fill=X, side=BOTTOM)
        self._draw_gradient_bar(gradient_bar)

        # Notebook
        try:
            self.notebook = ttk.Notebook(self.content, style="Hidden.TNotebook")
            self.notebook.pack(fill=BOTH, expand=True, padx=8, pady=(0, 8))
            self.notebook.bind("<<NotebookTabChanged>>", self._ensure_tab_loaded)
        except Exception:
            self.notebook = ttk.Notebook(self.content)
            self.notebook.pack(fill=BOTH, expand=True, padx=8, pady=(0, 8))
            self.notebook.bind("<<NotebookTabChanged>>", self._ensure_tab_loaded)

        self.tabs = {}
        self.sidebar_btns = {}
        self.category_frames = {}  # 分类折叠框架
        self._build_tabs()
        self._build_sidebar()
        try:
            self._update_sidebar_selection(next(iter(self.tabs.keys())))
        except Exception:
            pass

        # 现代化状态栏
        status = Frame(self.root, bg=THEME["status_bg"], height=28)
        status.pack(fill=X, side=BOTTOM)
        status.pack_propagate(False)
        
        # 左侧状态信息
        status_left = Frame(status, bg=THEME["status_bg"])
        status_left.pack(side=LEFT, padx=12)
        
        self.status_icon = Label(status_left, text="●", fg=THEME["accent_green"], 
                                bg=THEME["status_bg"], font=("Segoe UI", 8))
        self.status_icon.pack(side=LEFT, padx=(0, 6))
        
        self.status_label = Label(status_left, text="就绪", fg=THEME["status_text"], 
                                 bg=THEME["status_bg"], font=("Segoe UI", 9))
        self.status_label.pack(side=LEFT)
        
        # 右侧版权信息
        copyright_label = Label(status, text="© 张驰 · 数据结构可视化工具 v2.0", 
                               fg=THEME["text_muted"], bg=THEME["status_bg"], 
                               font=("Segoe UI", 8))
        copyright_label.pack(side=RIGHT, padx=12)

        self.current_structure = None
    
    def _on_entry_focus_in(self, e):
        """输入框获得焦点"""
        if self.nl_entry.get() == "输入自然语言命令...":
            self.nl_entry.delete(0, END)
            self.nl_entry.config(fg=THEME["text_dark"])
    
    def _on_entry_focus_out(self, e):
        """输入框失去焦点"""
        if not self.nl_entry.get().strip():
            self.nl_entry.insert(0, "输入自然语言命令...")
            self.nl_entry.config(fg=THEME["text_muted"])
    
    def _bind_button_hover(self, btn, normal_bg, hover_bg):
        """绑定按钮悬停效果"""
        btn.bind("<Enter>", lambda e: btn.config(bg=hover_bg))
        btn.bind("<Leave>", lambda e: btn.config(bg=normal_bg))
    
    def _draw_gradient_bar(self, canvas):
        """绘制渐变装饰条"""
        canvas.update_idletasks()
        width = canvas.winfo_width() or 1200
        colors = [THEME["primary"], THEME["accent_cyan"], THEME["accent_green"]]
        
        for i in range(width):
            t = i / width
            if t < 0.5:
                t2 = t * 2
                r = int(int(colors[0][1:3], 16) * (1-t2) + int(colors[1][1:3], 16) * t2)
                g = int(int(colors[0][3:5], 16) * (1-t2) + int(colors[1][3:5], 16) * t2)
                b = int(int(colors[0][5:7], 16) * (1-t2) + int(colors[1][5:7], 16) * t2)
            else:
                t2 = (t - 0.5) * 2
                r = int(int(colors[1][1:3], 16) * (1-t2) + int(colors[2][1:3], 16) * t2)
                g = int(int(colors[1][3:5], 16) * (1-t2) + int(colors[2][3:5], 16) * t2)
                b = int(int(colors[1][5:7], 16) * (1-t2) + int(colors[2][5:7], 16) * t2)
            color = f"#{r:02x}{g:02x}{b:02x}"
            canvas.create_line(i, 0, i, 3, fill=color)

    def _open_image_upload(self):
        """打开图片上传窗口"""
        try:
            # 创建图片上传窗口
            self.image_window = Toplevel(self.root)
            self.image_window.title("📷 图片识别 - 数据结构可视化")
            self.image_window.geometry("580x680")
            self.image_window.configure(bg="#f8fafc")
            self.image_window.resizable(False, False)
            
            # 设置窗口图标和样式
            try:
                self.image_window.attributes('-topmost', True)
                self.image_window.after(100, lambda: self.image_window.attributes('-topmost', False))
            except:
                pass
            
            # 居中显示
            self._center_window(self.image_window, 580, 680)
            
            # 初始化图片处理器
            self.image_processor = ImageProcessor(self.image_window)
            
            # 创建界面
            self._create_image_upload_ui()
            
        except Exception as e:
            messagebox.showerror("错误", f"打开图片上传窗口失败：{e}")
    
    def _center_window(self, window, width, height):
        """居中显示窗口"""
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        window.geometry(f"{width}x{height}+{x}+{y}")
        
    def _create_image_upload_ui(self):
        """创建图片上传界面 - 现代化设计"""
        bg_color = "#f8fafc"
        self.image_window.configure(bg=bg_color)
        
        # 标题区域
        title_frame = Frame(self.image_window, bg=bg_color)
        title_frame.pack(fill=X, padx=30, pady=(30, 20))
        
        # 图标和标题
        header_row = Frame(title_frame, bg=bg_color)
        header_row.pack()
        
        Label(header_row, text="🖼️", font=("Segoe UI", 28), bg=bg_color).pack(side=LEFT, padx=(0, 12))
        
        title_text = Frame(header_row, bg=bg_color)
        title_text.pack(side=LEFT)
        Label(title_text, text="图片识别", font=("微软雅黑", 20, "bold"), 
              bg=bg_color, fg=THEME["text_dark"]).pack(anchor=W)
        Label(title_text, text="AI 自动识别数据结构并生成可视化", 
              font=("Segoe UI", 10), bg=bg_color, fg=THEME["text_muted"]).pack(anchor=W)
        
        # 提示卡片
        tip_card = Frame(self.image_window, bg="#e0f2fe")
        tip_card.pack(fill=X, padx=30, pady=(0, 20))
        
        tip_content = Frame(tip_card, bg="#e0f2fe")
        tip_content.pack(fill=X, padx=16, pady=12)
        
        Label(tip_content, text="💡", font=("Segoe UI", 14), bg="#e0f2fe").pack(side=LEFT, padx=(0, 10))
        Label(tip_content, text="请上传清晰显示数据结构的图片（链表、树、栈等），AI将自动识别并生成创建命令", 
              font=("微软雅黑", 9), bg="#e0f2fe", fg="#0369a1", wraplength=450).pack(side=LEFT)
        
        # 上传区域 - 虚线框设计
        upload_outer = Frame(self.image_window, bg=bg_color)
        upload_outer.pack(fill=X, padx=30, pady=(0, 20))
        
        upload_frame = Frame(upload_outer, bg="#f1f5f9", highlightbackground="#cbd5e1",
                            highlightthickness=2)
        upload_frame.pack(fill=X, ipady=30)
        
        Label(upload_frame, text="📁", font=("Segoe UI", 32), bg="#f1f5f9").pack(pady=(20, 10))
        
        upload_btn = Button(upload_frame, text="选择图片文件", 
                          font=("微软雅黑", 11, "bold"), bg=THEME["primary"], fg="white",
                          relief=FLAT, padx=24, pady=10, cursor="hand2",
                          activebackground=THEME["primary_dark"],
                          command=self._handle_image_selection)
        upload_btn.pack(pady=10)
        self._bind_button_hover(upload_btn, THEME["primary"], THEME["primary_dark"])
        
        Label(upload_frame, text="支持 JPG, PNG, GIF, BMP 格式 · 最大 10MB", 
              font=("Segoe UI", 9), bg="#f1f5f9", fg=THEME["text_muted"]).pack(pady=(0, 20))
        
        # 预览区域
        self.preview_frame = Frame(self.image_window, bg=bg_color)
        self.preview_frame.pack(fill=BOTH, expand=True, padx=30, pady=(0, 10))
        
        # 描述输入区域
        desc_frame = Frame(self.image_window, bg=bg_color)
        desc_frame.pack(fill=X, padx=30, pady=(0, 15))
        
        desc_header = Frame(desc_frame, bg=bg_color)
        desc_header.pack(fill=X)
        Label(desc_header, text="📝 补充描述", font=("微软雅黑", 10, "bold"), 
              bg=bg_color, fg=THEME["text_dark"]).pack(side=LEFT)
        Label(desc_header, text="(可选)", font=("Segoe UI", 9), 
              bg=bg_color, fg=THEME["text_muted"]).pack(side=LEFT, padx=(6, 0))
        
        self.desc_text = Text(desc_frame, height=2, font=("Segoe UI", 10), 
                            relief=FLAT, bd=0, bg="#f1f5f9", fg=THEME["text_dark"],
                            padx=12, pady=10, wrap=WORD,
                            insertbackground=THEME["primary"])
        self.desc_text.pack(fill=X, pady=(8, 0))
        self.desc_text.insert("1.0", "描述图片内容可提高识别准确度...")
        self.desc_text.bind("<FocusIn>", lambda e: self.desc_text.delete("1.0", END) 
                           if self.desc_text.get("1.0", END).strip() == "描述图片内容可提高识别准确度..." else None)
        
        # 按钮区域
        btn_frame = Frame(self.image_window, bg=bg_color)
        btn_frame.pack(fill=X, padx=30, pady=(10, 30))
        
        # 取消按钮
        cancel_btn = Button(btn_frame, text="取消", 
                          font=("微软雅黑", 10), bg="#e2e8f0", fg=THEME["text_dark"],
                          relief=FLAT, padx=24, pady=10, cursor="hand2",
                          command=lambda: self.image_window.destroy())
        cancel_btn.pack(side=LEFT)
        self._bind_button_hover(cancel_btn, "#e2e8f0", "#cbd5e1")
        
        # 清除按钮
        clear_btn = Button(btn_frame, text="清除", 
                         font=("微软雅黑", 10), bg="#f1f5f9", fg=THEME["text_muted"],
                         relief=FLAT, padx=20, pady=10, cursor="hand2",
                         command=self._clear_image)
        clear_btn.pack(side=LEFT, padx=(10, 0))
        self._bind_button_hover(clear_btn, "#f1f5f9", "#e2e8f0")
        
        # 识别按钮
        analyze_btn = Button(btn_frame, text="🚀 开始识别", 
                           font=("微软雅黑", 11, "bold"), bg=THEME["accent_green"], fg="white",
                           relief=FLAT, padx=28, pady=10, cursor="hand2",
                           activebackground="#059669",
                           command=self._analyze_image)
        analyze_btn.pack(side=RIGHT)
        self._bind_button_hover(analyze_btn, THEME["accent_green"], "#059669")
    
    def _handle_image_selection(self):
        """处理图片选择"""
        if self.image_processor.select_image():
            # 图片选择成功
            pass
    
    def _clear_image(self):
        """清除已选择的图片"""
        self.image_processor.clear_preview()
        self.desc_text.delete("1.0", END)
        self.desc_text.insert("1.0", "例如：这是一个包含1,2,3的链表")
    
# 在 main.py 中修改以下方法

    def _clean_dsl_response(self, response):
        """清理DSL响应，提取纯命令"""
        if not response:
            return ""
        
        cleaned = response.strip()
        
        # 移除可能的markdown代码块
        if "```" in cleaned:
            code_blocks = re.findall(r'```(?:\w+)?\s*(.*?)\s*```', cleaned, re.DOTALL)
            if code_blocks:
                cleaned = code_blocks[0].strip()
        
        # 检查是否是Python对象表示（如LinkedList、Node等）
        if any(keyword in cleaned for keyword in ['LinkedList', 'Node', 'data=', 'next=', 'head=']):
            numbers = re.findall(r'\b\d+\b', cleaned)
            if numbers:
                return f"create {','.join(numbers)}"
        
        # 移除常见的非命令文本前缀
        unwanted_prefixes = [
            "dsl命令:", "命令:", "生成的dsl命令:", "根据图片分析",
            "这个图示", "图片显示", "数据结构", "链表", "栈", "队列", "树",
            "LinkedList", "Node", "insert", ";"
        ]
        
        for prefix in unwanted_prefixes:
            if cleaned.lower().startswith(prefix.lower()):
                cleaned = cleaned[len(prefix):].strip()
        
        # **新增：处理多条 insert 命令的情况（BST图片识别场景）**
        # 如果响应包含多个 insert 语句（用分号分隔），转换为 create 命令
        if 'insert' in cleaned.lower() and ';' in cleaned:
            # 提取所有数字
            numbers = re.findall(r'\b\d+\b', cleaned)
            if numbers:
                return f"create {','.join(numbers)}"
        
        # 只保留看起来像DSL命令的行
        lines = cleaned.split('\n')
        for line in lines:
            line = line.strip()
            if line and not any(word in line.lower() for word in ['分析', '解释', '说明', '示例', '图片', '结构', 'python', '代码']):
                # 检查是否包含DSL命令关键字
                dsl_keywords = ['create', 'insert', 'delete', 'push', 'pop', 'enqueue', 'dequeue', 'clear', 'search']
                if any(keyword in line.lower() for keyword in dsl_keywords):
                    # **额外检查：如果是单个insert但应该用create**
                    if line.lower().startswith('insert') and ',' not in line:
                        # 这可能是图片识别场景，尝试提取所有数字
                        all_numbers = re.findall(r'\b\d+\b', cleaned)
                        if len(all_numbers) > 1:
                            return f"create {','.join(all_numbers)}"
                    return line
        
        # 如果没有找到明确命令，尝试手动解析结构
        parsed_command = self._parse_tree_from_response(cleaned)
        if parsed_command:
            return parsed_command
        
        # 返回原始响应的第一行
        return lines[0].strip() if lines else ""

    def _parse_tree_from_response(self, response):
        """从响应中手动解析树结构（新增方法）"""
        try:
            # 尝试匹配常见的树表示格式
            patterns = [
                r'BST\(.*?(\d+).*?(\d+).*?(\d+)',  # BST包含数字
                r'Tree.*?(\d+).*?(\d+).*?(\d+)',   # Tree描述
                r'根节点.*?(\d+)',                  # 中文根节点描述
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, response)
                if matches:
                    if isinstance(matches[0], tuple):
                        numbers = list(matches[0])
                    else:
                        numbers = matches
                    if len(numbers) >= 2:
                        return f"create {','.join(map(str, numbers))}"
            
            # 提取所有数字作为最后的备选方案
            numbers = re.findall(r'\b\d+\b', response)
            if len(numbers) >= 2:
                return f"create {','.join(numbers)}"
            
            return None
        except Exception as e:
            print(f"解析树响应失败: {e}")
            return None


    # 同时修改 _analyze_image 方法中的系统提示词
    def _analyze_image(self):
        """分析图片并生成DSL命令"""
        image_path = self.image_processor.get_image_path()
        description = self.desc_text.get("1.0", END).strip()
        
        if not image_path:
            messagebox.showwarning("警告", "请先选择图片文件")
            return
        
        try:
            self.image_window.config(cursor="watch")
            
            from llm.doubao_client import DoubaoClient
            client = DoubaoClient()
            
            # **优化后的系统提示词 - 强调使用 create 命令**
            system_prompt = (
                "你是一个数据结构可视化助手。你的唯一任务是分析用户上传的图片，识别其中的数据结构，并生成相应的DSL命令。\n\n"
                "重要规则：\n"
                "1. 只返回DSL命令，不要有任何解释、描述、分析或其他文本\n"
                "2. 不要使用markdown格式\n"
                "3. 不要添加任何前缀或后缀\n"
                "4. 不要返回Python代码或对象表示\n"
                "5. 如果无法识别，返回 'error'\n"
                "6. **对于树结构（BST、二叉树等），必须使用单个 create 命令，不要使用多个 insert 命令**\n\n"
                "DSL命令格式（只使用以下格式）：\n"
                "- 清空：clear\n"
                "- 批量创建（推荐用于树和链表）：create 1,2,3,4,5\n"
                "- 链表插入：insert 5 或 insert 5 at 2\n"
                "- 链表删除：delete first 或 delete last 或 delete 2\n"
                "- 栈操作：push 5 或 pop\n"
                "- 队列操作：enqueue 5 或 dequeue\n"
                "- 树操作：insert 5（用于单个节点）\n"
                "- 搜索：search 5\n\n"
                "示例：\n"
                "- 如果图片显示BST包含节点 5,2,6,1,4,7,3，则返回 'create 5,2,6,1,4,7,3'\n"
                "- 如果图片显示链表 1->2->3，则返回 'create 1,2,3'\n"
                "- 如果图片显示栈顶有5，下面有3,1，则返回 'create 1,3,5'\n\n"
                "**关键：对于树结构，始终使用 create 命令列出所有节点值（用逗号分隔），不要使用分号分隔的多条 insert 命令。**\n\n"
                "现在请严格按照上述规则，只返回DSL命令："
            )
            
            # 用户描述文本
            user_prompt = "分析这张图片中的数据结构，只返回单个DSL命令（如 'create 1,2,3'），不要任何解释、代码或对象表示。"
            if description and description != "例如：这是一个包含1,2,3的链表":
                user_prompt = f"{description} 只返回单个DSL命令，不要任何解释、代码或对象表示。"
            
            # 发送多模态请求
            response = client.send_multimodal_message(
                text=user_prompt,
                image_path=image_path,
                temperature=0.0
            )
            
            print(f"图片识别原始响应: {response}")
            
            # 清理DSL命令
            dsl_command = self._clean_dsl_response(response)
            if not dsl_command or dsl_command.lower() == 'error':
                messagebox.showerror("错误", "无法识别图片中的数据结构")
                self.image_window.config(cursor="")
                return
            
            print(f"清理后的DSL命令: {dsl_command}")
            
            # 执行DSL命令
            self._execute_dsl_command_from_image(dsl_command)
            
            self.image_window.config(cursor="")
            self.image_window.destroy()
            messagebox.showinfo("成功", f"已识别并执行命令: {dsl_command}")
            
        except Exception as e:
            messagebox.showerror("错误", f"图片识别失败: {str(e)}")
            print(f"图片识别错误: {str(e)}")
            import traceback
            traceback.print_exc()
            try:
                self.image_window.config(cursor="")
            except:
                pass
    
    def _parse_linked_list_from_response(self, response):
        """从响应中手动解析链表结构"""
        try:
            # 尝试匹配常见的链表表示格式
            patterns = [
                r'LinkedList\(.*?(\d+).*?(\d+).*?(\d+)',  # LinkedList包含数字
                r'(\d+)\s*->\s*(\d+)\s*->\s*(\d+)',      # 1->2->3格式
                r'节点\s*(\d+).*?节点\s*(\d+).*?节点\s*(\d+)',  # 中文节点描述
                r'数据\s*(\d+).*?数据\s*(\d+).*?数据\s*(\d+)'   # 数据字段
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, response)
                if matches and len(matches[0]) >= 3:
                    numbers = matches[0][:3]  # 取前三个数字
                    return f"create {','.join(numbers)}"
            
            # 如果没有匹配到特定格式，尝试提取所有数字
            numbers = re.findall(r'\b\d+\b', response)
            if len(numbers) >= 2:  # 至少有两个数字才认为是有效的链表
                return f"create {','.join(numbers)}"
            
            return None
        except Exception as e:
            print(f"解析链表响应失败: {e}")
            return None
    
    def _validate_dsl_command(self, command):
        """验证DSL命令格式"""
        if not command:
            return False
        
        command_lower = command.lower()
        
        # 检查是否包含有效的DSL关键字
        dsl_keywords = ['create', 'insert', 'delete', 'push', 'pop', 'enqueue', 'dequeue', 'clear', 'search']
        
        return any(keyword in command_lower for keyword in dsl_keywords)
    
    def _execute_dsl_command_from_image(self, dsl_command):
        """执行从图片识别得到的DSL命令"""
        try:
            # 验证命令格式
            if not self._validate_dsl_command(dsl_command):
                messagebox.showerror("错误", f"无效的DSL命令格式: {dsl_command}")
                return
                
            print(f"从图片识别的DSL命令: {dsl_command}")
            
            # 获取当前可视化实例
            current_frame = self.notebook.select()
            found_instance = False

            for key, (ctor, frame, instance, title) in self.tabs.items():
                if str(frame) == str(current_frame) and instance:
                    found_instance = True
                    print(f"找到可视化实例: {key}")
                    
                    # 使用DSL处理函数
                    from DSL_utils import process_command
                    try:
                        process_command(instance, dsl_command)
                        print(f"DSL命令执行成功: {dsl_command}")
                        # 更新状态栏
                        self.status_label.config(text=f"图片识别执行: {dsl_command}")
                    except Exception as e:
                        print(f"DSL处理错误: {e}")
                        # 尝试使用程序化方法
                        self._try_programmatic_creation(instance, dsl_command)

            if not found_instance:
                messagebox.showerror("错误", "未找到活动的数据结构实例")

        except Exception as e:
            messagebox.showerror("错误", f"执行失败: {str(e)}")
            print(f"执行错误: {str(e)}")
    
    def _try_programmatic_creation(self, instance, dsl_command):
        """尝试使用程序化方法创建数据结构"""
        try:
            command_lower = dsl_command.lower()
            
            if command_lower.startswith('create'):
                # 提取数值
                numbers = re.findall(r'\d+', dsl_command)
                if numbers:
                    # 检查实例是否有 programmatic_insert_last 方法
                    if hasattr(instance, 'programmatic_insert_last'):
                        # 清空现有数据
                        if hasattr(instance, 'clear_visualization'):
                            instance.clear_visualization()
                        
                        # 批量插入
                        for num in numbers:
                            instance.programmatic_insert_last(num)
                        print(f"程序化创建成功: {numbers}")
                    elif hasattr(instance, 'create_list_from_string'):
                        # 使用批量创建方法
                        values_str = ','.join(numbers)
                        instance.batch_entry_var.set(values_str)
                        instance.create_list_from_string()
                        print(f"批量创建成功: {values_str}")
        except Exception as e:
            print(f"程序化创建失败: {e}")

    def _on_theme_change(self, _evt=None):
        try:
            self._apply_hidden_notebook_style()
            self.notebook.configure(style="Hidden.TNotebook")
        except Exception:
            pass

    def _open_chat(self):
        try:
            if ChatWindow is None:
                messagebox.showinfo("提示", "聊天模块不可用（llm 未安装或路径错误）")
                return
            # 设置主窗口实例到function_dispatcher
            from llm import function_dispatcher
            function_dispatcher.set_main_window_instance(self)
            chat_window = ChatWindow(self.root)
            self._center_chat_window(chat_window)
            self._ensure_tabs_hidden()
        except Exception as e:
            messagebox.showerror("错误", f"打开聊天窗口失败：{e}")
    
    def _center_chat_window(self, chat_window):
        try:
            chat_win = chat_window.win
            parent_x = self.root.winfo_x()
            parent_y = self.root.winfo_y()
            parent_width = self.root.winfo_width() or 1500
            parent_height = self.root.winfo_height() or 820
            window_width = 880
            window_height = 660
            
            x_pos = parent_x + (parent_width - window_width) // 2
            y_pos = parent_y + (parent_height - window_height) // 2
            
            chat_win.geometry(f"{window_width}x{window_height}+{x_pos}+{y_pos}")
        except Exception:
            pass
    
    def _ensure_tabs_hidden(self):
        try:
            self._apply_hidden_notebook_style()
            self.notebook.configure(style="Hidden.TNotebook")
        except Exception:
            pass

    def _render_background(self):
        """渲染现代渐变背景"""
        try:
            w = max(200, self.root.winfo_width() or 1350)
            h = max(200, self.root.winfo_height() or 820)
            self.bg_canvas.delete("bg")
            
            # 渐变背景：从深蓝到更深的蓝黑
            steps = 40
            for i in range(steps):
                t = i / max(1, steps - 1)
                color = self._blend_hex(THEME["bg_dark"], "#020617", t)
                y0 = int(i * (h / steps))
                y1 = int((i + 1) * (h / steps))
                self.bg_canvas.create_rectangle(0, y0, w, y1, fill=color, outline=color, tags="bg")
            
            # 星星效果（更柔和）
            for (rx, ry, r) in self._static_stars:
                sx = int(rx * w)
                sy = int(ry * h)
                # 随机星星颜色（白色/淡蓝/淡紫）
                colors = ["#ffffff", "#e0e7ff", "#c7d2fe", "#a5b4fc"]
                star_color = random.choice(colors)
                opacity_r = r * 0.8
                self.bg_canvas.create_oval(sx - opacity_r, sy - opacity_r, 
                                          sx + opacity_r, sy + opacity_r, 
                                          fill=star_color, outline="", tags="bg")
            
            try:
                self.root.tk.call('lower', self.bg_canvas._w)
            except Exception:
                pass
        except Exception:
            traceback.print_exc()

    def _on_configure(self, _evt=None):
        try:
            if self._resize_job is not None:
                try:
                    self.root.after_cancel(self._resize_job)
                except Exception:
                    pass
            def repaint():
                try:
                    if not self.root.winfo_exists():
                        return
                    self.root.update_idletasks()
                    self._render_background()
                except Exception:
                    pass
            self._resize_job = self.root.after(80, repaint)
        except Exception:
            pass

    def _animate_stars(self):
        """星星闪烁动画（更柔和）"""
        try:
            # 检查窗口是否仍然有效
            if not self.root.winfo_exists():
                return
            if not self.bg_canvas.winfo_exists():
                return
                
            w = max(200, self.root.winfo_width() or 1350)
            h = max(200, self.root.winfo_height() or 820)
            
            # 减少闪烁频率，更柔和
            for _ in range(4):
                x = random.randint(8, max(9, w - 8))
                y = random.randint(8, max(9, h - 8))
                colors = ["#c7d2fe", "#a5b4fc", "#818cf8", "#e0e7ff"]
                c = random.choice(colors)
                size = random.uniform(0.5, 1.5)
                self.bg_canvas.create_oval(x-size, y-size, x+size, y+size, 
                                          fill=c, outline="", tags="twinkle")
            
            # 使用安全的删除回调
            def safe_delete_twinkle():
                try:
                    if self.bg_canvas.winfo_exists():
                        self.bg_canvas.delete("twinkle")
                except Exception:
                    pass
            
            self.bg_canvas.after(350, safe_delete_twinkle)
            
            # 重新调度动画（在 try 块内部，确保只有成功时才继续）
            self.root.after(180, self._animate_stars)
        except Exception:
            # 发生异常时仍然尝试继续动画（如果窗口有效）
            try:
                if self.root.winfo_exists():
                    self.root.after(500, self._animate_stars)
            except Exception:
                pass

    def _apply_hidden_notebook_style(self):
        """应用隐藏标签页的notebook样式"""
        try:
            # 隐藏notebook标签
            self.style.layout("Hidden.TNotebook", [("Notebook.client", {"sticky": "nswe"})])
            self.style.layout("Hidden.TNotebook.Tab", [])
            
            # 配置notebook背景
            self.style.configure("Hidden.TNotebook", background=THEME["bg_dark"], borderwidth=0)
            self.style.configure("TFrame", background=THEME["bg_dark"])
            
            try:
                self.style.layout("TNotebook.Tab", [])
            except Exception:
                pass
        except Exception:
            pass

    def _blend_hex(self, c1, c2, t):
        def h2rgb(h):
            h = h.lstrip('#')
            return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
        r1,g1,b1 = h2rgb(c1); r2,g2,b2 = h2rgb(c2)
        r = int(r1 + (r2 - r1) * t); g = int(g1 + (g2 - g1) * t); b = int(b1 + (b2 - b1) * t)
        return f"#{r:02x}{g:02x}{b:02x}"

    def _build_sidebar(self):
        """构建现代化侧边栏"""
        # 侧边栏头部
        header = Frame(self.sidebar, bg=THEME["bg_sidebar"])
        header.pack(fill=X, padx=16, pady=(20, 16))
        
        # Logo和标题
        Label(header, text="📚", bg=THEME["bg_sidebar"], font=("Segoe UI", 22)).pack(side=LEFT)
        
        title_frame = Frame(header, bg=THEME["bg_sidebar"])
        title_frame.pack(side=LEFT, padx=(12, 0))
        Label(title_frame, text="数据结构", bg=THEME["bg_sidebar"], fg="#ffffff",
              font=("微软雅黑", 14, "bold")).pack(anchor=W)
        Label(title_frame, text="选择要学习的结构", bg=THEME["bg_sidebar"], fg="#94a3b8",
              font=("微软雅黑", 9)).pack(anchor=W)
        
        # 分隔线
        sep = Frame(self.sidebar, bg="#475569", height=1)
        sep.pack(fill=X, padx=16, pady=(0, 16))
        
        # 滚动容器
        nav_container = Frame(self.sidebar, bg=THEME["bg_sidebar"])
        nav_container.pack(fill=BOTH, expand=True, padx=8)
        
        # 按分类添加按钮
        for category, keys in DS_CATEGORIES.items():
            # 分类标题 - 更明显
            cat_frame = Frame(nav_container, bg=THEME["bg_sidebar"])
            cat_frame.pack(fill=X, pady=(12, 6))
            
            cat_label = Label(cat_frame, text=f"── {category} ──", bg=THEME["bg_sidebar"], 
                            fg="#64748b", font=("微软雅黑", 9, "bold"))
            cat_label.pack(side=LEFT, padx=8)
            
            # 分类下的按钮
            for tab_key in keys:
                if tab_key in self.tabs:
                    title = self.tabs[tab_key][3]
                    icon = DS_ICONS.get(tab_key, "📌")
                    self._add_sidebar_btn(nav_container, icon, title, tab_key)
        
        # 底部信息
        footer = Frame(self.sidebar, bg=THEME["bg_sidebar"])
        footer.pack(fill=X, side=BOTTOM, padx=16, pady=16)
        
        # 快捷键提示
        tip_frame = Frame(footer, bg="#334155")
        tip_frame.pack(fill=X, pady=(0, 8))
        Label(tip_frame, text="💡 提示", bg="#334155", fg="#fbbf24",
              font=("微软雅黑", 9, "bold")).pack(anchor=W, padx=12, pady=(8, 2))
        Label(tip_frame, text="使用顶部输入框发送\n自然语言命令操作", bg="#334155", 
              fg="#cbd5e1", font=("微软雅黑", 9), justify=LEFT).pack(anchor=W, padx=12, pady=(0, 8))
    
    def _add_sidebar_btn(self, parent, icon, title, tab_key):
        """添加侧边栏按钮（带图标和悬停效果）"""
        btn_frame = Frame(parent, bg=THEME["bg_sidebar"], cursor="hand2")
        btn_frame.pack(fill=X, pady=2, padx=4)
        
        # 图标
        icon_label = Label(btn_frame, text=icon, bg=THEME["bg_sidebar"], 
                          font=("Segoe UI", 13), width=2)
        icon_label.pack(side=LEFT, padx=(10, 8), pady=10)
        
        # 文本 - 使用更亮的颜色
        text_label = Label(btn_frame, text=title, bg=THEME["bg_sidebar"], 
                          fg="#e2e8f0", font=("微软雅黑", 11),
                          anchor="w")
        text_label.pack(side=LEFT, fill=X, expand=True, pady=10)
        
        # 存储引用
        self.sidebar_btns[tab_key] = {
            'frame': btn_frame,
            'icon': icon_label,
            'text': text_label,
            'title': title,
            'icon_char': icon
        }
        
        # 绑定点击事件
        for widget in [btn_frame, icon_label, text_label]:
            widget.bind("<Button-1>", lambda e, k=tab_key: self._select_tab(k))
            widget.bind("<Enter>", lambda e, k=tab_key: self._on_sidebar_hover(k, True))
            widget.bind("<Leave>", lambda e, k=tab_key: self._on_sidebar_hover(k, False))
    
    def _on_sidebar_hover(self, tab_key, entering):
        """侧边栏按钮悬停效果"""
        if tab_key not in self.sidebar_btns:
            return
        btn_data = self.sidebar_btns[tab_key]
        if self.current_structure == tab_key:
            return  # 已选中的不改变
        
        bg_color = "#334155" if entering else THEME["bg_sidebar"]
        fg_color = "#ffffff" if entering else "#e2e8f0"
        
        btn_data['frame'].config(bg=bg_color)
        btn_data['icon'].config(bg=bg_color)
        btn_data['text'].config(bg=bg_color, fg=fg_color)

    def _select_tab(self, key):
        if key not in self.tabs: return
        frame = self.tabs[key][1]
        self.notebook.select(frame)
        self._update_sidebar_selection(key)

    def _build_tabs(self):
        def add_tab(key, title, ctor):
            frame = Frame(self.notebook)
            self.notebook.add(frame, text=title)
            self.tabs[key] = (ctor, frame, None, title)

        add_tab("linked_list", "单链表", LinkList)
        add_tab("sequence", "顺序表", SequenceListVisualizer)
        add_tab("stack", "栈", StackVisualizer)
        add_tab("binary_tree", "二叉树链式存储", BinaryTreeVisualizer)
        add_tab("bst", "二叉搜索树", BSTVisualizer)
        add_tab("huffman", "Huffman树", HuffmanVisualizer)
        add_tab("trie", "Trie", TrieVisualizer)
        add_tab("bplus", "B+树", BPlusVisualizer)
        add_tab("avl", "AVL", AVLVisualizer)
        add_tab("rbt", "红黑树", RBTVisualizer)
        add_tab("cqueue", "循环队列", CircularQueueVisualizer)
        add_tab("hashtable", "散列表", HashtableVisualizer)

    def _ensure_tab_loaded(self, _evt=None):
        try:
            current = self.notebook.select()
            selected_key = None
            for key, (_ctor, frame, _inst, _title) in self.tabs.items():
                if str(frame) == current:
                    selected_key = key
                    break
            if selected_key is not None:
                # 更新选择（并同步结构标签）
                self._update_sidebar_selection(selected_key)
            for key, (ctor, frame, inst, _title) in self.tabs.items():
                if str(frame) == current and inst is None:
                    if ctor is None:
                        Label(frame, text="模块未找到", fg="red").pack(padx=20, pady=20)
                        self.tabs[key] = (ctor, frame, False, _title)  # mark attempted
                        return
                    try:
                        frame.pack_propagate(False)
                        host = EmbedHost(frame)
                        instance = ctor(host)  # 存储实例而不是布尔值
                        print(f"DEBUG: Created instance of type: {type(instance).__name__}")  # 调试输出
                        self.tabs[key] = (ctor, frame, instance, _title)  # 存储实际实例
                    except Exception:
                        traceback.print_exc()
                        self.tabs[key] = (ctor, frame, False, _title)
                        Label(frame, text="加载失败，请查看控制台", fg="red").pack(padx=20, pady=20)
                    # Keep tabs hidden in case style was reset by theme/widget creation
                    try:
                        self._apply_hidden_notebook_style()
                        self.notebook.configure(style="Hidden.TNotebook")
                    except Exception:
                        pass
                    return
        except Exception:
            traceback.print_exc()

    def _update_sidebar_selection(self, active_key):
        """更新侧边栏选中状态"""
        try:
            for key, btn_data in self.sidebar_btns.items():
                if isinstance(btn_data, dict):  # 新式按钮结构
                    if key == active_key:
                        # 选中状态 - 高亮显示（使用主色调）
                        btn_data['frame'].config(bg=THEME["primary"])
                        btn_data['icon'].config(bg=THEME["primary"])
                        btn_data['text'].config(bg=THEME["primary"], fg="#ffffff", 
                                               font=("微软雅黑", 11, "bold"))
                    else:
                        # 未选中状态 - 亮色文字
                        btn_data['frame'].config(bg=THEME["bg_sidebar"])
                        btn_data['icon'].config(bg=THEME["bg_sidebar"])
                        btn_data['text'].config(bg=THEME["bg_sidebar"], fg="#e2e8f0",
                                               font=("微软雅黑", 11))
                else:  # 兼容旧式按钮
                    if key == active_key:
                        btn_data.configure(bg=THEME["primary"], fg="white")
                    else:
                        btn_data.configure(bg=THEME["bg_sidebar"], fg="#e2e8f0")
        except Exception:
            pass
        
        # 更新当前结构变量与界面标签
        try:
            self.current_structure = active_key
            display_name = dict(self.tabs).get(active_key, [None, None, None, active_key])[3]
            icon = DS_ICONS.get(active_key, "📊")
            
            # 更新顶栏结构指示器
            if hasattr(self, "structure_icon_label"):
                self.structure_icon_label.config(text=icon)
            if hasattr(self, "structure_label"):
                self.structure_label.config(text=display_name if active_key else "选择数据结构")
            
            # 更新状态栏
            if hasattr(self, "status_label"):
                self.status_label.config(text=f"当前: {display_name}")
        except Exception:
            pass

    # ---------- 新增：自然语言输入的提交钩子 -------------
    def _get_current_tab_key(self):
        """返回当前选中的 tab key（或 None）"""
        try:
            current = self.notebook.select()
            for key, (_ctor, frame, _inst, _title) in self.tabs.items():
                if str(frame) == current:
                    return key
        except Exception:
            pass
        return None

    def _on_nl_submit(self, event=None):
        """
        自然语言输入回车处理钩子 - 将自然语言转换为DSL并执行
        支持栈的特殊操作（后缀表达式求值、括号匹配、DFS）的function calling
        """
        try:
            # 获取输入文本
            text = self.nl_var.get().strip()
            if not text:
                return "break"

            # 获取当前数据结构类型
            current_tab_key = self._get_current_tab_key()
            if not current_tab_key:
                messagebox.showerror("错误", "请先选择一个数据结构类型")
                return "break"

            # 初始化LLM客户端
            from llm.doubao_client import DoubaoClient
            from llm.function_schemas import get_function_schemas
            from llm import function_dispatcher
            client = DoubaoClient()

            # 对于栈数据结构，检测是否是特殊操作（后缀表达式、括号匹配、DFS）
            if current_tab_key == "stack":
                # 检测是否是特殊栈操作
                special_keywords = [
                    "后缀", "逆波兰", "postfix", "rpn", "求值", "计算表达式",
                    "括号", "匹配", "检验", "bracket", "parenthesis",
                    "dfs", "深度优先", "遍历图"
                ]
                
                text_lower = text.lower()
                is_special_operation = any(kw in text_lower for kw in special_keywords)
                
                if is_special_operation:
                    # 使用 function calling 处理特殊操作
                    functions = get_function_schemas("stack")
                    
                    fc_system_prompt = """你是一个数据结构可视化助手。你可以调用函数来演示栈的应用：

1. **后缀表达式求值** (stack_eval_postfix): 当用户想要演示后缀表达式（逆波兰表达式）的求值过程时调用
   - 用户说"演示后缀表达式 3 4 + 2 *"，调用 stack_eval_postfix(expression="3 4 + 2 *")
   - 用户说"计算 5 1 2 + 4 * + 3 -"，调用 stack_eval_postfix(expression="5 1 2 + 4 * + 3 -")
   
2. **括号匹配检验** (stack_bracket_match): 当用户想要检验括号是否匹配时调用
   - 用户说"检验{a+(b-c)*2}的括号"，调用 stack_bracket_match(expression="{a+(b-c)*2}")
   - 用户说"括号匹配 [(a+b)]"，调用 stack_bracket_match(expression="[(a+b)]")

3. **DFS深度优先搜索** (stack_dfs): 当用户想要演示DFS遍历时调用
   - 用户说"演示DFS"或"深度优先遍历"，调用 stack_dfs()

请根据用户请求调用对应的函数。"""

                    response = client.send_message(
                        text=text,
                        messages=[
                            {"role": "system", "content": fc_system_prompt},
                            {"role": "user", "content": text}
                        ],
                        temperature=0.0,
                        functions=functions,
                        function_call="auto"
                    )
                    
                    print(f"LLM Response (function calling): {response}")
                    
                    # 检查是否是function_call响应
                    if isinstance(response, dict) and response.get("type") == "function_call":
                        func_name = response.get("name", "")
                        func_args = response.get("arguments", {})
                        
                        print(f"调用函数: {func_name}, 参数: {func_args}")
                        
                        # 执行函数调用
                        result = function_dispatcher.dispatch(func_name, func_args)
                        
                        if result.get("ok"):
                            self.status_label.config(text=f"✅ 执行: {result.get('message', func_name)}")
                        else:
                            messagebox.showerror("执行失败", result.get("error", "未知错误"))
                        
                        self.nl_var.set("")
                        return "break"
                    else:
                        # 如果LLM没有调用函数，继续使用DSL方式
                        print("LLM未调用函数，使用DSL方式处理")

            # 准备系统提示（普通DSL转换）
            system_prompt = (
                "你是一个数据结构可视化助手。你需要将用户的自然语言指令转换为规范的DSL命令。\n"
                "请根据当前数据结构类型，按照以下格式转换：\n\n"
                "1. 通用操作:\n"
                "   - clear（清空）\n\n"
                "2. 链表/顺序表操作:\n"
                "   - 末尾插入：insert VALUE\n"
                "   - 指定位置插入：insert VALUE at POSITION 或 insert_at POSITION VALUE\n"
                "   - 在某值前插入：insert_before TARGET NEW（在第一个值为TARGET的节点前插入NEW）\n"
                "   - 在某值后插入：insert_after TARGET NEW（在第一个值为TARGET的节点后插入NEW）\n"
                "   - 在两值之间插入：insert_between A B X（在第一个A和第一个B之间插入X）\n"
                "   - 删除操作：delete first/last/POSITION\n"
                "   - 按值删除：delete_value VALUE（删除第一个值为VALUE的节点）\n"
                "   - 查找操作：search VALUE（查找第一个值为VALUE的节点，带动画）\n"
                "   - 反转链表：reverse（将链表所有节点顺序颠倒，带动画）\n"
                "   - 批量创建：create VALUE1,VALUE2,VALUE3\n"
                "   - 冒泡排序：bubblesort 或 bubble_sort\n"
                "   - 插入排序：insertionsort 或 insertion_sort\n"
                "   - 快速排序：quicksort 或 quick_sort\n"
                "   - 逆置：reverse（将顺序表/链表元素前后颠倒）\n\n"
                "3. 栈操作:\n"
                "   - 压栈：push VALUE\n"
                "   - 弹栈：pop\n"
                "   - 后缀表达式求值：eval EXPRESSION（如 eval 3 4 + 2 *）\n"
                "   - 括号匹配检验：match EXPRESSION（如 match {a+(b-c)*2}）\n\n"
                "4. 二叉搜索树操作:\n"
                "   - 插入：insert VALUE\n"
                "   - 查找：search VALUE\n"
                "   - 删除：delete VALUE\n"
                "   - 批量创建：create VALUE1,VALUE2,VALUE3\n\n"
                "5. 二叉树(链式存储)操作:\n"
                "   - 查找节点：search VALUE\n"
                "   - 自动插入：insert VALUE (插入到第一个空位)\n"
                "   - 指定位置插入：insert VALUE left PARENT_VALUE (插入为左子节点)\n"
                "   - 指定位置插入：insert VALUE right PARENT_VALUE (插入为右子节点)\n"
                "   - 删除节点：delete VALUE\n"
                "   - 批量创建：create VALUE1,VALUE2,VALUE3\n"
                "   - 遍历动画：preorder-anim / inorder-anim / postorder-anim\n"
                "   - 遍历结果：preorder / inorder / postorder / levelorder\n"
                "   - 树高度：height\n"
                "   - 节点数：count\n\n"
                "6. 循环队列操作:\n"
                "   - 入队：enqueue VALUE 或 enq VALUE\n"
                "   - 出队：dequeue 或 deq\n"
                "   - 清空：clear\n\n"
                "7. 哈夫曼树操作:\n"
                "   - 创建：create VALUE1,VALUE2,VALUE3\n"
                "   - 清空：clear\n\n"
                "8. 散列表操作:\n"
                "   - 批量创建：create VALUE1 VALUE2 VALUE3\n"
                "   - 插入：insert VALUE\n"
                "   - 查找：find VALUE 或 search VALUE\n"
                "   - 删除：delete VALUE\n"
                "   - 清空：clear\n"
                "   - 切换模式：switch（在开放寻址法和拉链法之间切换）\n"
                "   - 设置散列函数：hash EXPRESSION（如 hash x%7）\n"
                "   - 设置散列函数并重建：hash! EXPRESSION\n"
                "   - 使用预设散列函数：preset NAME（如 preset mod/multiply/square_mid）\n"
                "   - 调整容量：resize CAPACITY\n\n"
                "9. Trie字典树操作:\n"
                "   - 插入单词：insert WORD1,WORD2,WORD3\n"
                "   - 查找单词：search WORD\n"
                "   - 清空：clear\n\n"
                "10. B+树操作:\n"
                "   - 插入键值：insert VALUE1,VALUE2,VALUE3\n"
                "   - 查找：search VALUE\n"
                "   - 清空：clear\n\n"
                "示例转换：\n"
                "- '查找23' -> 'search 23'\n"
                "- '入队5' -> 'enqueue 5'\n"
                "- '压入6' -> 'push 6'\n"
                "- '删除队首元素' -> 'dequeue'\n"
                "- '在节点3的左边插入5' -> 'insert 5 left 3'\n"
                "- '删除节点2' -> 'delete 2'\n"
                "- '前序遍历动画' -> 'preorder-anim'\n"
                "- '排序' -> 'bubblesort'\n"
                "- '冒泡排序' -> 'bubblesort'\n"
                "- '插入排序' -> 'insertionsort'\n"
                "- '直接插入排序' -> 'insertionsort'\n"
                "- '快速排序' -> 'quicksort'\n"
                "- '快排' -> 'quicksort'\n"
                "- '逆置' -> 'reverse'\n"
                "- '翻转' -> 'reverse'\n"
                "- '反转' -> 'reverse'\n"
                "- '散列表切换模式' -> 'switch'\n"
                "- '设置散列函数为x模7' -> 'hash x%7'\n"
                "- '调整散列表容量为17' -> 'resize 17'\n"
                "- '插入单词apple' -> 'insert apple'\n"
                "- '演示后缀表达式 3 4 + 2 *' -> 'eval 3 4 + 2 *'\n"
                "- '检验括号 {a+b}' -> 'match {a+b}'\n"
                "- '删除值为5的节点' -> 'delete_value 5'\n"
                "- '按值删除42' -> 'delete_value 42'\n"
                "- '在5前面插入3' -> 'insert_before 5 3'\n"
                "- '在节点7后面插入10' -> 'insert_after 7 10'\n"
                "- '在3和7之间插入5' -> 'insert_between 3 7 5'\n"
                "- '查找值为5的节点' -> 'search 5'\n"
                "- '搜索42' -> 'search 42'\n"
                "- '反转链表' -> 'reverse'\n"
                "- '逆置单链表' -> 'reverse'\n"
                "仅返回转换后的命令，不要添加任何额外解释。"
            )

            # 发送请求给LLM（DSL命令转换）
            response = client.send_message(
                text=text,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text}
                ],
                temperature=0.1
            )

            print(f"LLM Response: {response}")

            # 清理DSL命令（去除多余的空格和引号）
            dsl_command = response.strip().strip("'\"") if isinstance(response, str) else ""
            if not dsl_command:
                messagebox.showerror("错误", "无法理解您的指令")
                print("Empty DSL command")
                return "break"

            print(f"Converted DSL command: {dsl_command}")

            # 获取当前可视化实例
            current_frame = self.notebook.select()
            found_instance = False

            for key, (ctor, frame, instance, title) in self.tabs.items():
                if str(frame) == str(current_frame) and instance:
                    found_instance = True
                    print(f"Found visualizer instance: {key}")
                    
                    # 直接使用DSL处理函数
                    from DSL_utils import process_command
                    try:
                        print(f"DEBUG: Instance type in main: {type(instance).__name__}")
                        process_command(instance, dsl_command)
                        print(f"DSL command executed: {dsl_command}")
                        self.status_label.config(text=f"已执行: {dsl_command}")
                        self.nl_var.set("")
                    except Exception as e:
                        print(f"Error processing DSL: {e}")
                        raise

            if not found_instance:
                messagebox.showerror("错误", "未找到活动的数据结构实例")
                print("No active visualizer instance found")

        except Exception as e:
            messagebox.showerror("错误", f"处理失败: {str(e)}")
            print(f"Error in _on_nl_submit: {str(e)}")
            import traceback
            traceback.print_exc()

        return "break"

    # ----------------------------------------------------

class Application:
    """应用程序入口类 - 管理落地页和主界面的切换"""
    
    def __init__(self):
        self.root = Tk()
        self.landing_page = None
        self.main_window = None
        
        # 显示落地页
        self._show_landing_page()
    
    def _show_landing_page(self):
        """显示落地页"""
        self.landing_page = LandingPage(self.root, self._on_start_learning)
    
    def _on_start_learning(self):
        """用户点击开始学习后的回调"""
        # 清理落地页引用
        self.landing_page = None
        
        # 创建主界面
        self.main_window = MainWindow(self.root)
    
    def run(self):
        """运行应用程序"""
        self.root.mainloop()


if __name__ == "__main__":
    try:
        app = Application()
        app.run()
    except Exception:
        traceback.print_exc()
        try:
            messagebox.showerror("错误", "程序启动失败，请查看控制台输出")
        except Exception:
            pass
        sys.exit(1)