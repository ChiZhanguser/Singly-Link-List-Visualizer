"""
AVL树的DSL（领域特定语言）处理器 - 支持 create 命令
支持 create 和 insert 命令
"""

import re
from typing import List
from tkinter import messagebox

def process(visualizer, text: str) -> bool:
    """
    处理AVL树的DSL命令
    支持 create, insert 和 clear 命令
    """
    if not text or not text.strip():
        return False
        
    text = text.strip().lower()
    print(f"DEBUG: AVL DSL processing: '{text}'")
    
    # 清空操作
    if text in ('clear', '清空', 'reset', '重置', 'c'):
        visualizer.clear_canvas()
        return True
    
    # 显示帮助
    elif text in ('help', '帮助', '?'):
        _show_help()
        return True
    
    # **新增：批量创建操作 (create 命令)**
    elif text.startswith(('create', '创建', '批量创建')):
        return _process_create(visualizer, text)
    
    # 插入操作 - 支持多种格式
    elif (text.startswith(('insert', '添加', '插入', 'add', 'i ')) or 
          _is_numeric_insert(text)):
        return _process_insert(visualizer, text)
    
    else:
        messagebox.showinfo("未识别的命令", 
            f"无法识别的命令: {text}\n\n"
            "支持的命令:\n"
            "  • create 1,2,3  (批量创建AVL树)\n"
            "  • insert 1 2 3  (插入数字)\n"
            "  • clear  (清空树)\n"
            "  • help  (显示帮助)")
        return False

def _process_create(visualizer, text: str) -> bool:
    """
    处理批量创建命令
    支持格式:
      - create 1,2,3,4,5
      - create 1, 2, 3, 4, 5
      - create 10 20 30 40 50
      - 创建 5,15,25,35
    """
    try:
        # 提取数字
        numbers = _extract_numbers(text)
        
        if not numbers:
            messagebox.showinfo("创建错误", 
                "请指定要创建的数字序列\n\n"
                "示例:\n"
                "  create 1,2,3,4,5\n"
                "  create 10, 20, 30\n"
                "  create 5 15 25 35")
            return False
        
        # 先清空现有树
        visualizer.model.root = None
        
        # 设置输入框并触发插入动画
        # 使用逗号+空格格式，这是 start_insert_animated 期望的格式
        numbers_str = ", ".join(map(str, numbers))
        visualizer.input_var.set(numbers_str)
        
        print(f"DEBUG: AVL create command - inserting: {numbers_str}")
        
        # 调用插入动画方法
        visualizer.start_insert_animated()
        
        return True
        
    except Exception as e:
        messagebox.showerror("创建错误", f"创建操作失败: {str(e)}")
        print(f"ERROR: AVL create failed: {e}")
        return False

def _process_insert(visualizer, text: str) -> bool:
    """
    处理插入命令
    支持格式:
      - insert 1 2 3
      - insert 1, 2, 3
      - add 5 10 15
      - i 1 2 3
      - 1 2 3 (直接输入数字)
    """
    try:
        # 提取数字
        numbers = _extract_numbers(text)
        
        if not numbers:
            messagebox.showinfo("插入错误", 
                "请指定要插入的数字\n\n"
                "示例:\n"
                "  insert 1 2 3\n"
                "  insert 5, 10, 15\n"
                "  1 2 3")
            return False
        
        # 设置输入框并触发插入动画
        numbers_str = ", ".join(map(str, numbers))
        visualizer.input_var.set(numbers_str)
        visualizer.start_insert_animated()
        
        return True
        
    except Exception as e:
        messagebox.showerror("插入错误", f"插入操作失败: {str(e)}")
        return False

def _extract_numbers(text: str) -> List:
    """
    从文本中提取所有数字
    支持整数和浮点数
    """
    # 移除命令关键词
    cleaned_text = re.sub(
        r'^(create|创建|批量创建|insert|添加|插入|add|i)\s*',
        '', 
        text, 
        flags=re.IGNORECASE
    )
    
    # 提取数字模式：整数、浮点数、负数
    number_pattern = r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?'
    numbers = re.findall(number_pattern, cleaned_text)
    
    # 转换为适当的类型（整数或浮点数）
    result = []
    for num_str in numbers:
        try:
            if '.' in num_str or 'e' in num_str.lower():
                result.append(float(num_str))
            else:
                result.append(int(num_str))
        except ValueError:
            continue
    
    return result

def _is_numeric_insert(text: str) -> bool:
    """
    检查文本是否为纯数字插入（不带命令关键词）
    例如: "1 2 3" 或 "5, 10, 15"
    """
    # 检查是否以数字开头
    if re.match(r'^[-+]?\d', text):
        numbers = _extract_numbers(text)
        return len(numbers) > 0
    
    return False

def _show_help():
    """
    显示AVL DSL命令帮助
    """
    help_text = """
🌳 AVL树 DSL 命令帮助

═══════════════════════════════════════

🌲 批量创建:
  create 1,2,3      创建包含1,2,3的AVL树
  create 5, 10, 15  创建包含5,10,15的AVL树
  create 7 8 9      创建包含7,8,9的AVL树

📥 插入操作:
  insert 1 2 3      插入数字1, 2, 3
  insert 5, 10, 15  插入数字5, 10, 15
  add 7 8 9         插入数字7, 8, 9
  i 20 30 40        快捷插入20, 30, 40
  1 2 3             直接输入数字插入

🗑️ 清空操作:
  clear             清空整棵AVL树
  reset             重置树
  c                 快捷清空

❓ 帮助:
  help              显示此帮助信息
  ?                 显示帮助

═══════════════════════════════════════

💡 使用示例:

1. 批量创建AVL树:
   create 5,2,6,1,4,7,3

2. 在现有树上插入:
   insert 50 60 70

3. 清空树后重新创建:
   clear
   create 10,20,30,40,50

4. 直接输入数字:
   1 2 3 4 5

═══════════════════════════════════════

✨ AVL树特性:
  • 自动平衡: 插入时自动旋转保持平衡
  • 动画演示: 显示插入路径和旋转过程
  • 平衡因子: 实时显示节点的平衡状态
  • 支持整数和浮点数

🎬 观看动画:
  插入操作会显示:
  1. 搜索路径高亮
  2. 新节点飞入动画
  3. 旋转调整过程

📌 注意事项:
  • create 命令会先清空现有树
  • insert 命令会在现有树上添加节点
  • 支持逗号或空格分隔数字
    """
    
    messagebox.showinfo("AVL树 DSL 命令帮助", help_text)

# 备用处理函数，用于在__init__.py中调用
def _fallback_process_command(visualizer, text: str) -> bool:
    """备用命令处理函数，用于模块导入"""
    return process(visualizer, text)