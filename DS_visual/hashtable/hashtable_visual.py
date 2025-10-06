from tkinter import *
from tkinter import messagebox, filedialog
import json
import os
from datetime import datetime
from typing import Any, List, Tuple

from hashtable.hashtable_model import HashTable, _TOMBSTONE

class HashtableVisualizer:
    def __init__(self, root):
        self.window = root
        self.window.title("哈希表（线性探测）可视化")
        self.window.config(bg="#FFFDF0")
        self.canvas = Canvas(self.window, bg="white", width=1200, height=520, bd=6, relief=RAISED)
        self.canvas.pack()

        # model & params
        self.capacity = 11
        self.model = HashTable(self.capacity)
        self.cell_w = 120
        self.cell_h = 60
        self.start_x = 40
        self.start_y = 120
        self.gap = 12

        # state
        self.key_var = StringVar()
        self.value_var = StringVar()
        self.batch_var = StringVar()
        self.dsl_var = StringVar()

        # UI
        self.create_heading()
        self.create_controls()
        self.update_display()

    def create_heading(self):
        Label(self.window, text="线性探测哈希表（带墓碑）",
              font=("Arial", 24, "bold"), bg="#FFFDF0", fg="#5D4037").place(x=24, y=12)
        Label(self.window, text="映射: hash(key) % capacity；删除用 tombstone（墓碑）标记",
              font=("Arial", 11), bg="#FFFDF0").place(x=24, y=52)

    def create_controls(self):
        frame = Frame(self.window, bg="#FFFDF0")
        frame.place(x=24, y=76, width=1150, height=40)

        Label(frame, text="Key:", bg="#FFFDF0").pack(side=LEFT, padx=(4,2))
        Entry(frame, textvariable=self.key_var, width=20).pack(side=LEFT, padx=(0,8))
        Label(frame, text="Value:", bg="#FFFDF0").pack(side=LEFT, padx=(4,2))
        Entry(frame, textvariable=self.value_var, width=20).pack(side=LEFT, padx=(0,8))
        Button(frame, text="Put", bg="#4CAF50", fg="white", command=self.on_put).pack(side=LEFT, padx=6)
        Button(frame, text="Get", bg="#2196F3", fg="white", command=self.on_get).pack(side=LEFT, padx=6)
        Button(frame, text="Remove", bg="#F44336", fg="white", command=self.on_remove).pack(side=LEFT, padx=6)
        Button(frame, text="Clear", bg="#FFB300", fg="white", command=self.on_clear).pack(side=LEFT, padx=6)
        Button(frame, text="Save", bg="#6C9EFF", fg="white", command=self.save_table).pack(side=LEFT, padx=6)
        Button(frame, text="Load", bg="#6C9EFF", fg="white", command=self.load_table).pack(side=LEFT, padx=6)

        bottom = Frame(self.window, bg="#FFFDF0")
        bottom.place(x=24, y=420, width=1150, height=120)
        Label(bottom, text="批量创建 (k1:v1,k2:v2 ...):", bg="#FFFDF0").grid(row=0, column=0, sticky="w", padx=6, pady=6)
        Entry(bottom, textvariable=self.batch_var, width=80).grid(row=0, column=1, padx=6, pady=6)
        Button(bottom, text="批量创建", command=self.batch_create).grid(row=0, column=2, padx=6)

        Label(bottom, text="DSL:", bg="#FFFDF0").grid(row=1, column=0, sticky="w", padx=6, pady=6)
        Entry(bottom, textvariable=self.dsl_var, width=80).grid(row=1, column=1, padx=6, pady=6)
        Button(bottom, text="执行", command=self.process_dsl).grid(row=1, column=2, padx=6)

    def on_put(self):
        k = self.key_var.get().strip()
        v = self.value_var.get()
        if k == "":
            messagebox.showerror("错误", "Key 不能为空")
            return
        self.model.put(k, v)
        self.update_display()

    def on_get(self):
        k = self.key_var.get().strip()
        if k == "":
            messagebox.showerror("错误", "Key 不能为空")
            return
        v = self.model.get(k)
        if v is None:
            messagebox.showinfo("Get", f"{k} not found")
        else:
            messagebox.showinfo("Get", f"{k} -> {v}")

    def on_remove(self):
        k = self.key_var.get().strip()
        if k == "":
            messagebox.showerror("错误", "Key 不能为空")
            return
        ok = self.model.remove(k)
        messagebox.showinfo("Remove", "removed" if ok else "not found")
        self.update_display()

    def on_clear(self):
        self.model.clear()
        self.update_display()

    def batch_create(self):
        txt = self.batch_var.get().strip()
        if not txt:
            return
        parts = [p.strip() for p in txt.split(",") if p.strip()]
        for p in parts:
            if ":" in p:
                k, v = p.split(":", 1)
                self.model.put(k.strip(), v)
        self.update_display()

    # ---------- DSL ----------
    def process_dsl(self):
        t = self.dsl_var.get().strip()
        if not t:
            return
        parts = t.split(maxsplit=2)
        cmd = parts[0].lower()
        if cmd == "put" and len(parts) >= 3:
            k = parts[1]; v = parts[2]
            self.model.put(k, v); self.update_display()
        elif cmd == "get" and len(parts) >= 2:
            k = parts[1]; v = self.model.get(k)
            messagebox.showinfo("Get", f"{k} -> {v}" if v is not None else f"{k} not found")
        elif cmd in ("remove", "rm") and len(parts) >= 2:
            k = parts[1]; ok = self.model.remove(k)
            messagebox.showinfo("Remove", "removed" if ok else "not found"); self.update_display()
        elif cmd == "clear":
            self.model.clear(); self.update_display()
        else:
            messagebox.showinfo("DSL 未识别", "支持：put k v, get k, remove k, clear")
        self.dsl_var.set("")
    

    # ---------- save/load ----------
    def _ensure_folder(self):
        base = os.path.dirname(os.path.abspath(__file__))
        d = os.path.join(base, "save")
        os.makedirs(d, exist_ok=True)
        return d

    def save_table(self):
        items = list(self.model.items())
        default = f"hashtable_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        path = filedialog.asksaveasfilename(initialdir=self._ensure_folder(), initialfile=default, defaultextension=".json")
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"items": items, "meta": {"capacity": self.model.capacity}}, f, ensure_ascii=False, indent=2)
        messagebox.showinfo("保存", "保存成功")

    def load_table(self):
        path = filedialog.askopenfilename(initialdir=self._ensure_folder(), filetypes=[("JSON files", "*.json")])
        if not path:
            return
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        items = data.get("items", [])
        cap = data.get("meta", {}).get("capacity", self.capacity)
        self.capacity = max(3, int(cap))
        self.model = HashTable(self.capacity)
        for k, v in items:
            self.model.put(k, v)
        self.update_display()
        messagebox.showinfo("加载", "加载完成")

    # ---------- display ----------
    def update_display(self):
        self.canvas.delete("all")
        x = self.start_x
        y = self.start_y

        # status/info box
        status = f"size={self.model.size}  capacity={self.model.capacity}  tombstones={self.model.tombstones}"
        self.canvas.create_text(24, 24, anchor="nw", text=status, font=("Arial", 12, "bold"))

        for i in range(self.model.capacity):
            rect = self.canvas.create_rectangle(x, y, x + self.cell_w, y + self.cell_h, fill="#FAFAFA", outline="#333")
            k = self.model.keys[i]
            v = self.model.values[i]

            # display string
            if k is None:
                display = ""
            elif k is _TOMBSTONE:
                display = "<TOMBSTONE>"
            else:
                display = f"{k}:{v}"

            # index & content
            self.canvas.create_text(x + 8, y + 8, anchor="nw", text=f"idx {i}", font=("Arial", 10), fill="#666")
            self.canvas.create_text(x + self.cell_w/2, y + self.cell_h/2, text=display, font=("Arial", 12))

            x += self.cell_w + self.gap

# ---------- run demo ----------
if __name__ == "__main__":
    root = Tk()
    root.geometry("1280x620")
    HashtableVisualizer(root)
    root.mainloop()
