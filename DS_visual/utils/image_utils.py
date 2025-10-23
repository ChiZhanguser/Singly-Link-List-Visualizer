# image_utils.py
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os

class ImageProcessor:
    def __init__(self, parent_window):
        self.parent = parent_window
        self.current_image_path = None
        self.preview_label = None
        
    def select_image(self):
        """选择图片文件"""
        file_types = [
            ('图片文件', '*.jpg *.jpeg *.png *.gif *.bmp *.tiff'),
            ('所有文件', '*.*')
        ]
        
        filename = filedialog.askopenfilename(
            title="选择数据结构图片",
            filetypes=file_types
        )
        
        if filename:
            self.current_image_path = filename
            return self._preview_image(filename)
        return False
    
    def _preview_image(self, image_path):
        """预览图片"""
        try:
            # 打开并调整图片大小以适应预览
            image = Image.open(image_path)
            
            # 调整大小以适应预览（最大 300x300）
            max_size = (300, 300)
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # 转换为 PhotoImage
            photo = ImageTk.PhotoImage(image)
            
            # 创建或更新预览标签
            if not self.preview_label:
                self.preview_label = tk.Label(self.parent, image=photo, bg="white", relief="solid", bd=1)
                self.preview_label.image = photo  # 保持引用
                self.preview_label.pack(pady=10)
            else:
                self.preview_label.config(image=photo)
                self.preview_label.image = photo
            
            return True
            
        except Exception as e:
            messagebox.showerror("错误", f"图片加载失败: {str(e)}")
            return False
    
    def get_image_path(self):
        """获取当前选择的图片路径"""
        return self.current_image_path
    
    def clear_preview(self):
        """清除预览"""
        if self.preview_label:
            self.preview_label.pack_forget()
            self.preview_label = None
        self.current_image_path = None