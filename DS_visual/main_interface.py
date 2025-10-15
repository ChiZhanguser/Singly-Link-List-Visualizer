# main_interface.py
# 半透明卡片 + 星辰背景 主界面（修正版：文字用 Canvas 绘制，保证中文可见）
from tkinter import *
from tkinter import ttk, messagebox
from PIL import Image, ImageDraw, ImageFilter, ImageTk, ImageFont
import math, random, time, os, sys, traceback

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
ChatWindow = try_import("ChatWindow", "llm.chat_window")
register_visualizer = try_import("register_visualizer", "llm.function_dispatcher")
RBTVisualizer = try_import("RBTVisualizer", "rbt.rbt_visual")
CircularQueueVisualizer = try_import("CircularQueueVisualizer", "circular_queue.circular_queue_visual")
TrieVisualizer = try_import("TrieVisualizer", "trie.trie_visual")
BPlusVisualizer = try_import("BPlusVisualizer", "bplustree.bplustree_visual")
HashtableVisualizer = try_import("HashtableVisualizer", "hashtable.hashtable_visual")

# ---------- color helpers ----------
def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
def rgb_to_hex(rgb):
    return '#{:02x}{:02x}{:02x}'.format(*rgb)
def blend_hex(c1, c2, t):
    r1, g1, b1 = hex_to_rgb(c1); r2, g2, b2 = hex_to_rgb(c2)
    return rgb_to_hex((int(r1 + (r2 - r1) * t),
                       int(g1 + (g2 - g1) * t),
                       int(b1 + (b2 - b1) * t)))
def lighten_hex(h, amount=0.12):
    r, g, b = hex_to_rgb(h)
    r = min(255, int(r + (255 - r) * amount))
    g = min(255, int(g + (255 - g) * amount))
    b = min(255, int(b + (255 - b) * amount))
    return rgb_to_hex((r, g, b))

# ---------- tooltip ----------
class CanvasToolTip:
    def __init__(self, canvas):
        self.canvas = canvas; self.tip = None
    def show(self, text, x, y):
        self.hide()
        if not text: return
        self.tip = Toplevel(self.canvas); self.tip.overrideredirect(True); self.tip.attributes("-topmost", True)
        label = Label(self.tip, text=text, font=("Arial", 10), bg="#333333", fg="white", padx=6, pady=3, bd=0)
        label.pack()
        self.tip.geometry(f"+{x}+{y}")
    def hide(self):
        if self.tip:
            try: self.tip.destroy()
            except: pass
            self.tip = None

# ---------- PIL helpers ----------
def rounded_rect_image(w, h, radius, color_rgba, shadow=False, shadow_offset=(6,6), shadow_blur=10):
    w = max(1, int(w)); h = max(1, int(h)); radius = max(0, int(radius))
    if shadow:
        sw = w + abs(shadow_offset[0]) + shadow_blur*2
        sh = h + abs(shadow_offset[1]) + shadow_blur*2
        base = Image.new("RGBA", (sw, sh), (0,0,0,0))
        shadow_layer = Image.new("RGBA", (sw, sh), (0,0,0,0))
        draw_s = ImageDraw.Draw(shadow_layer)
        sx = shadow_blur; sy = shadow_blur
        draw_s.rounded_rectangle([sx + shadow_offset[0], sy + shadow_offset[1],
                                  sx + shadow_offset[0] + w, sy + shadow_offset[1] + h],
                                 radius, fill=(0,0,0,160))
        shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(shadow_blur))
        base = Image.alpha_composite(base, shadow_layer)
        draw = ImageDraw.Draw(base)
        draw.rounded_rectangle([sx, sy, sx + w, sy + h], radius, fill=color_rgba)
        return base
    else:
        im = Image.new("RGBA", (w, h), (0,0,0,0))
        draw = ImageDraw.Draw(im)
        draw.rounded_rectangle([0,0,w,h], radius, fill=color_rgba)
        return im

def make_button_image(size, label, icon_color_hex, fill_hex, font_path=None, font_size=18, radius=14):
    w, h = size
    w = max(1, int(w)); h = max(1, int(h))
    fill_rgb = hex_to_rgb(fill_hex)
    im = Image.new("RGBA", (w, h), (0,0,0,0))
    draw = ImageDraw.Draw(im)
    draw.rounded_rectangle([0,0,w,h], radius, fill=(fill_rgb[0], fill_rgb[1], fill_rgb[2], 255))
    # draw white circle icon on left (we won't draw text here)
    icon_r = min(12, h//4)
    icon_x = 18
    icon_y = h//2
    draw.ellipse([icon_x-icon_r, icon_y-icon_r, icon_x+icon_r, icon_y+icon_r], fill=(255,255,255,255))
    return im

# ---------- Main UI ----------
class MainInterface:
    def __init__(self, root):
        self.window = root
        self.window.title("数据结构可视化工具 — 张驰")
        self.window.geometry("1380x980")
        self.window.minsize(1000,700)
        try:
            style = ttk.Style(self.window); style.theme_use('clam')
        except: pass

        self._anim_phase = 0.0
        self._particle_positions = [(random.uniform(0,1380), random.uniform(0,980), random.uniform(1,3), random.uniform(0.12,0.6)) for _ in range(180)]
        self._static_stars = [(random.uniform(0,1380), random.uniform(0,980), random.uniform(0.5,1.5)) for _ in range(260)]
        self.offset_x = 0.0; self.offset_y = 0.0

        self.window.configure(bg="#000000")
        self.bg_canvas = Canvas(self.window, bd=0, highlightthickness=0, bg=self.window['bg'])
        self.bg_canvas.pack(fill=BOTH, expand=True)
        self.bg_canvas.bind("<Button-1>", self._on_drag_start)
        self.bg_canvas.bind("<B1-Motion>", self._on_drag)
        self.bg_canvas.bind("<ButtonRelease-1>", self._on_drag_end)

        self._canvas_w = 1380; self._canvas_h = 980
        self._photo_refs = {}
        self._ctooltip = CanvasToolTip(self.bg_canvas)
        self._resize_after_id = None

        # title
        self.bg_canvas.create_text(48, 52, anchor='w', text="数据结构可视化工具", font=("Helvetica",36,"bold"), fill="#ffffff", tags="title")
        self.bg_canvas.create_text(48, 120, anchor='w', text="探索数据结构的宇宙", font=("Helvetica",14), fill="#EAF6FF", tags="subtitle")

        self.header_h = 200
        self.panel_relwidth = 0.92
        self.panel_h = 540
        self.panel_radius = 18
        self.panel_color = (8,24,39,200)
        self.panel_shadow_offset = (10,10)
        self.panel_shadow_blur = 18

        # button metadata
        self.btns = [
            ("单链表", "#FF8C42", "🔗", self.open_linked_list, "单链表（单向）可视化与操作"),
            ("顺序表", "#2ECC71", "📋", self.open_sequence_list, "基于数组的顺序表演"),
            ("栈", "#8E44AD", "📚", self.open_stack, "后进先出（LIFO）结构演示"),
            ("二叉树链式存储", "#E74C3C", "🌳", self.open_binary_tree, "链式存储的普通二叉树"),
            ("二叉搜索树", "#3498DB", "🔎", self.open_bst, "BST：插入/删除/查找演示"),
            ("Huffman树", "#A0522D", "🔠", self.open_huffman, "基于频率的编码树（Huffman）"),
            ("Trie（前缀树）", "#FF6F61", "🔤", self.open_trie, "Trie（前缀树）可视化 — 自动补全 / 前缀查询"),
            ("B+树", "#16A085", "🗃️", self.open_bplustree, "B+树（B+ Tree）可视化 — 索引 / 磁盘页 演示"),
            ("AVL (平衡二叉树)", "#5DADE2", "⚖️", self.open_avl, "自平衡 AVL 树演示"),
            ("红黑树", "#D84315", "🔴", self.open_rbt, "红黑树（Red-Black Tree）可视化"),
            ("循环队列", "#F1C40F", "🔁", self.open_circular_queue, "循环队列（Ring Buffer）可视化 — 入队/出队/环绕示意"),
            ("散列表", "#2C3E50", "🔑", self.open_hashtable, "散列表（Hash Table）可视化 — 键值对存储")
        ]

        self.window.after(80, self._on_ready)
        self._animate_bg()

        # bottom bar
        bottom_bar = Frame(self.window, bg="#1b1b3a", height=44)
        bottom_bar.pack(fill=X, side=BOTTOM)
        Label(bottom_bar, text="© 张驰 的 数据结构可视化工具", bg="#1b1b3a", fg="#aaaaaa", font=("Arial",10)).pack(side=LEFT,padx=12)
        Label(bottom_bar, text="23070215", bg="#1b1b3a", fg="#aaaaaa", font=("Arial",10)).pack(side=RIGHT,padx=12)

        # shortcuts
        self.window.bind("<Key-1>", lambda e: self.open_linked_list())
        self.window.bind("<Key-2>", lambda e: self.open_sequence_list())
        self.window.bind("<Key-3>", lambda e: self.open_stack())
        self.window.bind("<Key-4>", lambda e: self.open_trie())
        self.window.bind("<Key-5>", lambda e: self.open_bplustree())

    def _on_ready(self):
        try: self.window.update_idletasks()
        except: pass
        self._canvas_w = max(200, self.bg_canvas.winfo_width() or 1380)
        self._canvas_h = max(200, self.bg_canvas.winfo_height() or 980)
        self._draw_bg_gradient("#000000", "#001f3f")
        self._create_panel_and_buttons()
        self.bg_canvas.bind("<Configure>", self._on_configure)

    def _on_configure(self, event):
        if self._resize_after_id:
            try: self.window.after_cancel(self._resize_after_id)
            except: pass
        self._resize_after_id = self.window.after(120, lambda: self._handle_resize(event.width, event.height))

    def _handle_resize(self, w, h):
        self._resize_after_id = None
        self._canvas_w = max(200, int(w)); self._canvas_h = max(200, int(h))
        self._draw_bg_gradient("#000000", "#001f3f")
        self._create_panel_and_buttons()

    def _draw_bg_gradient(self, c1, c2):
        try:
            self.bg_canvas.delete("grad")
            width = getattr(self, "_canvas_w", 1380) or 1380
            h = getattr(self, "_canvas_h", 980) or 980
            steps = 72
            for i in range(steps):
                t = i / (steps - 1)
                color = blend_hex(c1, c2, t)
                y0 = int(i * (h / steps)); y1 = int((i+1) * (h / steps))
                self.bg_canvas.create_rectangle(0, y0, width, y1, outline=color, fill=color, tags="grad")
            for i, (sx, sy, sr) in enumerate(self._static_stars):
                twinkle = (math.sin(time.time() * 2 + i * 0.1) + 1) / 2 * 0.5 + 0.5
                star_color = blend_hex("#ffffff", c2, 1 - twinkle)
                draw_x = (sx + self.offset_x) % width
                if draw_x < 0: draw_x += width
                draw_y = (sy + self.offset_y) % h
                if draw_y < 0: draw_y += h
                self.bg_canvas.create_oval(draw_x - sr, draw_y - sr, draw_x + sr, draw_y + sr, fill=star_color, outline="", tags="grad")
            for i, (px, py, rad, alpha) in enumerate(self._particle_positions):
                glow_rad = rad * 2
                glow_color = blend_hex("#ffffff", c2, 0.9)
                draw_x = (px + self.offset_x) % width
                if draw_x < 0: draw_x += width
                draw_y = (py + self.offset_y) % h
                if draw_y < 0: draw_y += h
                self.bg_canvas.create_oval(draw_x - glow_rad, draw_y - glow_rad, draw_x + glow_rad, draw_y + glow_rad, fill=glow_color, outline="", stipple="gray25", tags="grad")
                particle_color = blend_hex("#ffffff", c2, 0.7 * alpha)
                self.bg_canvas.create_oval(draw_x - rad, draw_y - rad, draw_x + rad, draw_y + rad, fill=particle_color, outline="", tags="grad")
            try: self.bg_canvas.tag_lower("grad")
            except: pass
            self.bg_canvas.tag_raise("title"); self.bg_canvas.tag_raise("subtitle")
        except Exception:
            traceback.print_exc()

    def _animate_bg(self):
        self._anim_phase = (getattr(self, "_anim_phase", 0.0) + 0.006) % 1.0
        new_positions = []
        width = getattr(self, "_canvas_w", 1380) or 1380
        h = getattr(self, "_canvas_h", 980) or 980
        for (x, y, r, a) in self._particle_positions:
            nx = x + math.sin(time.time() * 0.18 + x) * 0.4
            nx = nx % width
            if nx < 0: nx += width
            ny = y + math.sin(time.time() * 0.85 + x) * 4 * a
            ny = ny % h
            if ny < 0: ny += h
            new_positions.append((nx, ny, r, a))
        self._particle_positions = new_positions
        try: self._draw_bg_gradient("#000000", "#001f3f")
        except: traceback.print_exc()
        self.window.after(40, self._animate_bg)

    def _create_panel_and_buttons(self):
        try:
            self.bg_canvas.delete("panel_img"); self.bg_canvas.delete("btn_item"); self.bg_canvas.delete("btn_text")
            cw = getattr(self, "_canvas_w", 1380) or 1380
            ch = getattr(self, "_canvas_h", 980) or 980
            panel_w = max(600, int(self.panel_relwidth * cw)); panel_h = int(self.panel_h)
            panel_x = cw//2; panel_y = self.header_h - 16

            panel_img = rounded_rect_image(panel_w, panel_h, self.panel_radius,
                                           (self.panel_color[0], self.panel_color[1], self.panel_color[2], self.panel_color[3]),
                                           shadow=True, shadow_offset=self.panel_shadow_offset, shadow_blur=self.panel_shadow_blur)
            ptk = ImageTk.PhotoImage(panel_img); self._photo_refs['panel'] = ptk
            self.bg_canvas.create_image(panel_x, panel_y, image=ptk, anchor='n', tags="panel_img")
            try: self.bg_canvas.tag_raise("panel_img"); self.bg_canvas.tag_raise("title"); self.bg_canvas.tag_raise("subtitle")
            except: pass

            cols = 3
            total_buttons = len(self.btns)
            rows = (total_buttons + cols - 1) // cols
            v_gap = 18
            min_btn_w = 360
            btn_gap_side = 80
            btn_area_w = max(1, panel_w - btn_gap_side)
            raw_btn_w = int(btn_area_w / cols) if cols>0 else 160
            btn_w = max(min_btn_w, raw_btn_w)
            max_btn_w = max(120, int((panel_w - (cols+1)*8)/cols))
            if btn_w > max_btn_w: btn_w = max_btn_w
            btn_h = 92
            spacing_x = max(8, (panel_w - cols * btn_w) / (cols + 1))
            total_h = rows * btn_h + (rows - 1) * v_gap
            start_y = panel_y + max(40, (panel_h - total_h)//2)
            start_x = panel_x - panel_w//2 + spacing_x + btn_w//2

            # clear caches
            self._photo_refs['buttons'] = []; self._photo_refs['hover_imgs'] = []

            for idx, (label, color, emoji, cmd, tip) in enumerate(self.btns):
                col = idx % cols; row = idx // cols
                x = int(start_x + col * (btn_w + spacing_x))
                y = int(start_y + row * (btn_h + v_gap))

                pil_btn = make_button_image((btn_w, btn_h), label, color, color, font_size=18, radius=12)
                btn_img = ImageTk.PhotoImage(pil_btn)
                self._photo_refs['buttons'].append(btn_img)
                img_item = self.bg_canvas.create_image(x, y, image=btn_img, tags=("btn_item", f"btn_{idx}"))

                # compute text position (left bound + icon offset)
                left_x = x - btn_w//2
                icon_r = min(12, btn_h//4)
                text_x = left_x + 18 + icon_r + 14
                # create canvas text (use Tk font so Chinese displays reliably)
                text_item = self.bg_canvas.create_text(text_x, y, text=label, anchor='w', font=("Helvetica", 16), fill="white", tags=("btn_text", f"text_{idx}"))

                # bind both image and text to same handlers
                def make_cb(f): return lambda e: f()
                self.bg_canvas.tag_bind(img_item, "<Button-1>", make_cb(cmd))
                self.bg_canvas.tag_bind(text_item, "<Button-1>", make_cb(cmd))

                hover_img = ImageTk.PhotoImage(make_button_image((btn_w, btn_h), label, color, lighten_hex(color, 0.12), font_size=18, radius=12))
                self._photo_refs['hover_imgs'].append(hover_img)

                def on_enter(evt, it_img=img_item, hi=hover_img, tip_text=tip):
                    try:
                        self.bg_canvas.itemconfigure(it_img, image=hi)
                        abs_x = self.window.winfo_rootx() + evt.x; abs_y = self.window.winfo_rooty() + evt.y + 20
                        self._ctooltip.show(tip_text, abs_x, abs_y)
                    except: pass
                def on_leave(evt, it_img=img_item, bi=btn_img):
                    try:
                        self.bg_canvas.itemconfigure(it_img, image=bi); self._ctooltip.hide()
                    except: pass

                # bind both
                self.bg_canvas.tag_bind(img_item, "<Enter>", on_enter)
                self.bg_canvas.tag_bind(img_item, "<Leave>", on_leave)
                self.bg_canvas.tag_bind(text_item, "<Enter>", on_enter)
                self.bg_canvas.tag_bind(text_item, "<Leave>", on_leave)

            try: self.bg_canvas.tag_raise("btn_item")
            except: pass

            # floating chat button
            chat_w, chat_h = 120, 48
            chat_x = int(cw * 0.96); chat_y = 28
            chat_img = make_button_image((chat_w, chat_h), "聊天", "#1FA2FF", "#1FA2FF", font_size=16, radius=10)
            chat_ptk = ImageTk.PhotoImage(chat_img); self._photo_refs['chat'] = chat_ptk
            chat_item = self.bg_canvas.create_image(chat_x, chat_y, image=chat_ptk, anchor='ne', tags=("btn_item","chat_btn"))
            self.bg_canvas.tag_bind(chat_item, "<Button-1>", lambda e: self._open_chat())
            chat_hover = ImageTk.PhotoImage(make_button_image((chat_w, chat_h), "聊天", "#1FA2FF", lighten_hex("#1FA2FF", 0.12), font_size=16, radius=10))
            self._photo_refs['chat_hover'] = chat_hover
            self.bg_canvas.tag_bind(chat_item, "<Enter>", lambda e: self.bg_canvas.itemconfigure(chat_item, image=chat_hover))
            self.bg_canvas.tag_bind(chat_item, "<Leave>", lambda e: self.bg_canvas.itemconfigure(chat_item, image=chat_ptk))

        except Exception:
            traceback.print_exc()
            messagebox.showerror("错误", f"绘制界面时出错：\n{traceback.format_exc()}")

    def _open_chat(self):
        try:
            if ChatWindow: ChatWindow(self.window)
            else: messagebox.showinfo("提示", "聊天模块不可用（llm 未安装或路径错误）")
        except Exception as e:
            messagebox.showerror("错误", f"打开聊天窗口失败：{e}")

    # drag helpers
    def _on_drag_start(self, event):
        self.drag_start_x = event.x; self.drag_start_y = event.y
    def _on_drag(self, event):
        if getattr(self, "drag_start_x", None) is None: return
        dx = event.x - self.drag_start_x; dy = event.y - self.drag_start_y
        self.offset_x += dx; self.offset_y += dy
        self.drag_start_x = event.x; self.drag_start_y = event.y
    def _on_drag_end(self, event):
        self.drag_start_x = None; self.drag_start_y = None

    def _safe_open(self, cls_name, import_info, title):
        try:
            if import_info is None: raise ImportError(f"{cls_name} 未找到")
            win = Toplevel(self.window); win.title(title); win.geometry("1350x730")
            if callable(import_info): import_info(win)
        except Exception as e:
            messagebox.showerror("错误", f"无法打开 {title}：{e}")

    def open_linked_list(self): self._safe_open("LinkList", LinkList, "单链表可视化")
    def open_sequence_list(self): self._safe_open("SequenceListVisualizer", SequenceListVisualizer, "顺序表可视化")
    def open_stack(self): self._safe_open("StackVisualizer", StackVisualizer, "栈可视化")
    def open_binary_tree(self): self._safe_open("BinaryTreeVisualizer", BinaryTreeVisualizer, "二叉树可视化")
    def open_bst(self): self._safe_open("BSTVisualizer", BSTVisualizer, "二叉搜索树可视化")
    def open_huffman(self): self._safe_open("HuffmanVisualizer", HuffmanVisualizer, "Huffman 可视化")
    def open_avl(self): self._safe_open("AVLVisualizer", AVLVisualizer, "AVL 可视化")
    def open_rbt(self): self._safe_open("RBTVisualizer", RBTVisualizer, "红黑树可视化")
    def open_trie(self): self._safe_open("TrieVisualizer", TrieVisualizer, "Trie（前缀树）可视化")
    def open_bplustree(self): self._safe_open("BPlusVisualizer", BPlusVisualizer, "B+树 可视化")
    def open_circular_queue(self): self._safe_open("CircularQueueVisualizer", CircularQueueVisualizer, "循环队列 可视化")
    def open_hashtable(self): self._safe_open("HashtableVisualizer", HashtableVisualizer, "哈希表 可视化")

if __name__ == '__main__':
    try:
        root = Tk(); app = MainInterface(root); root.mainloop()
    except Exception:
        traceback.print_exc()
        try: messagebox.showerror("错误", "程序启动失败，请查看控制台输出")
        except: pass
        sys.exit(1)
