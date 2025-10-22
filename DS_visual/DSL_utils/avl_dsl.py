"""
AVL树的DSL（领域特定语言）处理器
支持插入、搜索、删除等操作的自然语言命令
"""

import re
from typing import List, Optional, Tuple
from tkinter import messagebox

def process(visualizer, text: str) -> bool:
    """
    处理AVL树的DSL命令
    """
    if not text or not text.strip():
        return False
        
    text = text.strip().lower()
    print(f"DEBUG: AVL DSL processing: '{text}'")
    
    # 插入操作
    if text.startswith(('insert', '添加', '插入', 'add')):
        return _process_insert(visualizer, text)
    
    # 搜索操作
    elif text.startswith(('search', '查找', 'find', '查询')):
        return _process_search(visualizer, text)
    
    # 删除操作
    elif text.startswith(('delete', '删除', 'remove', 'del')):
        return _process_delete(visualizer, text)
    
    # 清空操作
    elif text in ('clear', '清空', 'reset', '重置'):
        visualizer.clear_canvas()
        return True
    
    # 保存操作
    elif text.startswith(('save', '保存', 'export')):
        visualizer.save_structure()
        return True
    
    # 加载操作
    elif text.startswith(('load', '加载', 'open', 'import')):
        visualizer.load_structure()
        return True
    
    # 批量插入
    elif text.startswith(('batch', '批量', 'multiple')):
        return _process_batch(visualizer, text)
    
    # 显示帮助
    elif text in ('help', '帮助', '?', '命令'):
        _show_help()
        return True
    
    else:
        # 尝试解析为数值插入
        if _is_numeric_insert(text):
            return _process_numeric_insert(visualizer, text)
        else:
            messagebox.showinfo("未识别的AVL命令", 
                f"无法识别的命令: {text}\n\n输入 'help' 查看可用命令")
            return False

def _process_insert(visualizer, text: str) -> bool:
    """
    处理插入命令
    格式: insert 5, insert 10, 添加 7, add 3
    """
    try:
        # 提取数字
        numbers = _extract_numbers(text)
        if not numbers:
            messagebox.showinfo("插入错误", "请在插入命令后指定要插入的数字")
            return False
        
        # 设置输入框并触发插入动画
        numbers_str = ",".join(map(str, numbers))
        visualizer.input_var.set(numbers_str)
        visualizer.start_insert_animated()
        return True
        
    except Exception as e:
        messagebox.showerror("插入错误", f"插入操作失败: {str(e)}")
        return False

def _process_search(visualizer, text: str) -> bool:
    """
    处理搜索命令
    格式: search 5, 查找 10, find 7
    """
    try:
        numbers = _extract_numbers(text)
        if not numbers:
            messagebox.showinfo("搜索错误", "请在搜索命令后指定要搜索的数字")
            return False
        
        # 由于AVLVisualizer目前没有专门的搜索动画，我们使用插入来演示搜索路径
        # 在实际实现中，应该添加专门的搜索方法
        target = numbers[0]
        messagebox.showinfo("搜索功能", 
            f"搜索功能正在开发中\n\n将搜索值: {target}\n\n"
            f"当前实现中，您可以使用插入操作来观察树的搜索路径")
        return True
        
    except Exception as e:
        messagebox.showerror("搜索错误", f"搜索操作失败: {str(e)}")
        return False

def _process_delete(visualizer, text: str) -> bool:
    """
    处理删除命令
    格式: delete 5, 删除 10, remove 7
    """
    try:
        numbers = _extract_numbers(text)
        if not numbers:
            messagebox.showinfo("删除错误", "请在删除命令后指定要删除的数字")
            return False
        
        # AVLVisualizer目前没有实现删除功能
        target = numbers[0]
        messagebox.showinfo("删除功能", 
            f"删除功能正在开发中\n\n将删除值: {target}\n\n"
            f"当前版本支持插入操作和自动平衡")
        return True
        
    except Exception as e:
        messagebox.showerror("删除错误", f"删除操作失败: {str(e)}")
        return False

def _process_batch(visualizer, text: str) -> bool:
    """
    处理批量插入命令
    格式: batch 1,2,3,4,5, 批量 10 20 30, multiple 5-10
    """
    try:
        numbers = _extract_numbers(text)
        if not numbers:
            messagebox.showinfo("批量插入错误", "请在批量命令后指定要插入的数字序列")
            return False
        
        # 设置输入框并触发插入动画
        numbers_str = ",".join(map(str, numbers))
        visualizer.input_var.set(numbers_str)
        visualizer.start_insert_animated()
        return True
        
    except Exception as e:
        messagebox.showerror("批量插入错误", f"批量插入失败: {str(e)}")
        return False

def _process_numeric_insert(visualizer, text: str) -> bool:
    """
    处理纯数字插入命令
    格式: 5, 10, 3.14, 1 2 3, 1,2,3
    """
    try:
        numbers = _extract_numbers(text)
        if not numbers:
            return False
        
        # 设置输入框并触发插入动画
        numbers_str = ",".join(map(str, numbers))
        visualizer.input_var.set(numbers_str)
        visualizer.start_insert_animated()
        return True
        
    except Exception as e:
        messagebox.showerror("插入错误", f"数字插入失败: {str(e)}")
        return False

def _extract_numbers(text: str) -> List:
    """
    从文本中提取所有数字
    """
    # 移除命令关键词
    cleaned_text = re.sub(r'^(insert|添加|插入|add|search|查找|find|查询|delete|删除|remove|del|batch|批量|multiple)\s*', '', text, flags=re.IGNORECASE)
    
    # 提取数字模式：整数、浮点数、科学计数法
    number_pattern = r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?'
    
    # 支持多种分隔符：空格、逗号、分号、中文逗号等
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
    检查文本是否为纯数字插入
    """
    # 检查是否以数字开头
    if re.match(r'^[-+]?\d', text):
        return True
    
    # 检查是否包含数字
    numbers = _extract_numbers(text)
    return len(numbers) > 0

def _show_help():
    """
    显示AVL DSL命令帮助
    """
    help_text = """
AVL树 DSL 命令帮助:

插入操作:
  insert 5          - 插入数字5
  添加 10           - 插入数字10  
  add 7            - 插入数字7
  5,10,15          - 批量插入数字5,10,15

搜索操作:
  search 8         - 搜索数字8
  查找 12          - 搜索数字12
  find 20          - 搜索数字20

删除操作:
  delete 5         - 删除数字5
  删除 10          - 删除数字10
  remove 7         - 删除数字7

批量操作:
  batch 1,2,3,4,5  - 批量插入数字1-5
  批量 10 20 30    - 批量插入数字10,20,30

其他命令:
  clear            - 清空AVL树
  save             - 保存AVL树结构
  load             - 加载AVL树结构
  help             - 显示此帮助信息

特性说明:
  • 自动平衡: AVL树在插入时会自动进行旋转操作保持平衡
  • 动画演示: 支持插入路径高亮和旋转动画
  • 可视化: 实时显示树的高度和平衡因子
  • 支持整数和浮点数

示例:
  insert 3,5,1,2,4  - 按顺序插入数字并观察自动平衡
  batch 10,20,30,40,50 - 批量插入并观察树的生长
    """
    
    messagebox.showinfo("AVL树 DSL 命令帮助", help_text)

# 备用处理函数，用于在__init__.py中调用
def _fallback_process_command(visualizer, text: str) -> bool:
    """备用命令处理函数，用于模块导入"""
    return process(visualizer, text)