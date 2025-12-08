"""
红黑树的DSL(领域特定语言)处理器
支持 create、clear 和 delete 命令
"""

import re
from typing import List
from tkinter import messagebox

def process(visualizer, text: str) -> bool:
    """
    处理红黑树的DSL命令
    支持 create、clear、delete 和 search 命令
    
    Args:
        visualizer: RBTVisualizer实例
        text: DSL命令文本
        
    Returns:
        bool: 命令是否执行成功
    """
    if not text or not text.strip():
        return False
        
    text = text.strip().lower()
    print(f"DEBUG: RBT DSL processing: '{text}'")
    
    # 清空操作
    if text in ('clear', '清空', 'reset', '重置', 'c'):
        return _process_clear(visualizer)
    
    # 批量创建操作
    elif text.startswith(('create', '创建', '批量创建')):
        return _process_create(visualizer, text)
    
    # 查找操作
    elif text.startswith(('search', 'find', '查找', '搜索', '查询', 's ')):
        return _process_search(visualizer, text)
    
    # 删除操作
    elif text.startswith(('delete', '删除', 'remove', 'del', 'd ')):
        return _process_delete(visualizer, text)
    
    # 显示帮助
    elif text in ('help', '帮助', '?'):
        _show_help()
        return True
    
    else:
        messagebox.showinfo("未识别的命令", 
            f"无法识别的命令: {text}\n\n"
            "支持的命令:\n"
            "  • create 1,2,3,4,5  (批量创建红黑树)\n"
            "  • search 3  (查找节点)\n"
            "  • delete 3  (删除节点)\n"
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
    
    Args:
        visualizer: RBTVisualizer实例
        text: 包含create命令的文本
        
    Returns:
        bool: 是否成功
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
        from rbt.rbt_model import RBModel
        visualizer.model = RBModel()
        
        # 设置输入框并触发插入动画
        numbers_str = ",".join(map(str, numbers))
        visualizer.input_var.set(numbers_str)
        
        print(f"DEBUG: RBT create command - inserting: {numbers_str}")
        
        # 调用插入动画方法
        visualizer.start_insert_animated()
        
        return True
        
    except Exception as e:
        messagebox.showerror("创建错误", f"创建操作失败: {str(e)}")
        print(f"ERROR: RBT create failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def _process_search(visualizer, text: str) -> bool:
    """
    处理查找命令
    
    支持格式:
      - search 5
      - search 5, 10, 15
      - find 10
      - 查找 20
      - s 15
    
    Args:
        visualizer: RBTVisualizer实例
        text: 包含search命令的文本
        
    Returns:
        bool: 是否成功
    """
    try:
        # 检查是否正在执行动画
        if getattr(visualizer, 'animating', False):
            messagebox.showinfo("提示", "请等待当前动画完成")
            return False
        
        # 检查树是否为空
        if visualizer.model.root is None:
            messagebox.showinfo("提示", "树为空,无法查找节点")
            return False
        
        # 提取要查找的数字
        numbers = _extract_numbers(text)
        
        if not numbers:
            messagebox.showinfo("查找错误", 
                "请指定要查找的节点值\n\n"
                "示例:\n"
                "  search 5\n"
                "  search 5, 10, 15\n"
                "  find 20\n"
                "  查找 30")
            return False
        
        # 设置输入框并调用查找方法
        numbers_str = ",".join(map(str, numbers))
        visualizer.input_var.set(numbers_str)
        
        print(f"DEBUG: RBT search command - searching: {numbers_str}")
        
        # 调用查找动画方法
        visualizer.start_search_animated()
        
        return True
        
    except Exception as e:
        messagebox.showerror("查找错误", f"查找操作失败: {str(e)}")
        print(f"ERROR: RBT search failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def _process_delete(visualizer, text: str) -> bool:
    """
    处理删除命令
    
    支持格式:
      - delete 5
      - delete 10
      - 删除 20
      - del 15
      - d 25
    
    Args:
        visualizer: RBTVisualizer实例
        text: 包含delete命令的文本
        
    Returns:
        bool: 是否成功
    """
    try:
        # 检查是否正在执行动画
        if getattr(visualizer, 'animating', False):
            messagebox.showinfo("提示", "请等待当前动画完成")
            return False
        
        # 检查树是否为空
        if visualizer.model.root is None:
            messagebox.showinfo("提示", "树为空,无法删除节点")
            return False
        
        # 提取要删除的数字
        numbers = _extract_numbers(text)
        
        if not numbers:
            messagebox.showinfo("删除错误", 
                "请指定要删除的节点值\n\n"
                "示例:\n"
                "  delete 5\n"
                "  delete 10\n"
                "  删除 20")
            return False
        
        if len(numbers) > 1:
            messagebox.showinfo("删除提示", 
                "一次只能删除一个节点\n"
                f"将删除第一个值: {numbers[0]}")
        
        value = numbers[0]
        
        # 设置输入框并调用删除方法
        visualizer.input_var.set(str(value))
        
        print(f"DEBUG: RBT delete command - deleting: {value}")
        
        # 调用删除动画方法
        visualizer.start_delete_animated()
        
        return True
        
    except Exception as e:
        messagebox.showerror("删除错误", f"删除操作失败: {str(e)}")
        print(f"ERROR: RBT delete failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def _process_clear(visualizer) -> bool:
    """
    处理清空命令
    
    Args:
        visualizer: RBTVisualizer实例
        
    Returns:
        bool: 是否成功
    """
    try:
        # 检查是否正在执行动画
        if getattr(visualizer, 'animating', False):
            messagebox.showinfo("提示", "请等待当前动画完成")
            return False
        
        # 调用清空方法
        visualizer.clear_canvas()
        print(f"DEBUG: RBT clear command executed")
        return True
        
    except Exception as e:
        messagebox.showerror("清空错误", f"清空操作失败: {str(e)}")
        print(f"ERROR: RBT clear failed: {e}")
        return False


def _extract_numbers(text: str) -> List[int]:
    """
    从文本中提取所有数字
    
    Args:
        text: 包含数字的文本
        
    Returns:
        List[int]: 提取的整数列表
    """
    # 移除命令关键词
    cleaned_text = re.sub(
        r'^(create|创建|批量创建|delete|删除|remove|del|d|search|find|查找|搜索|查询|s)\s*',
        '', 
        text, 
        flags=re.IGNORECASE
    )
    
    # 提取数字模式:支持正整数、负整数
    number_pattern = r'[-+]?\d+'
    number_strs = re.findall(number_pattern, cleaned_text)
    
    # 转换为整数
    result = []
    for num_str in number_strs:
        try:
            result.append(int(num_str))
        except ValueError:
            continue
    
    return result


def _show_help():
    """
    显示红黑树 DSL 命令帮助
    """
    help_text = """
🔴⚫ 红黑树 DSL 命令帮助

═══════════════════════════════════════

🌲 批量创建:
  create 1,2,3,4,5    创建包含1,2,3,4,5的红黑树
  create 10, 20, 30   创建包含10,20,30的红黑树
  create 5 15 25 35   创建包含5,15,25,35的红黑树
  创建 7,8,9          使用中文命令创建

🔍 查找节点:
  search 5            查找值为5的节点
  search 5, 10, 15    批量查找多个值
  find 10             查找值为10的节点
  查找 20             使用中文命令查找
  s 15                快捷查找命令

❌ 删除节点:
  delete 5            删除值为5的节点
  delete 10           删除值为10的节点
  删除 20             使用中文命令删除
  del 15              快捷删除命令
  d 25                超快捷删除

🗑️ 清空操作:
  clear               清空整棵红黑树
  reset               重置树
  c                   快捷清空

❓ 帮助:
  help                显示此帮助信息
  ?                   显示帮助

═══════════════════════════════════════

💡 使用示例:

1. 批量创建红黑树:
   create 1,2,3,4,5,0,6

2. 查找节点:
   search 3
   search 1, 5, 10

3. 删除节点:
   delete 3

4. 清空树:
   clear

5. 完整流程:
   create 10,20,30,40,50
   search 30
   delete 30
   search 30

═══════════════════════════════════════

✨ 红黑树特性:
  • 自平衡: 插入/删除时自动调整保持平衡
  • 颜色规则: 维护红黑树的5条性质
  • 动画演示: 
    - 搜索路径高亮显示
    - 新节点飞入动画
    - 颜色调整过程
    - 左旋/右旋操作
    - 删除节点淡出动画

🎨 颜色含义:
  • 🔴 红节点: 新插入的节点初始为红色
  • ⚫ 黑节点: 平衡后的节点或根节点
  • 🟢 路径高亮: 搜索路径 / 找到的节点
  • 🟠 操作高亮: 当前操作节点
  • 🔵 删除标记: 即将被删除的节点

📊 红黑树性质:
  1. 每个节点是红色或黑色
  2. 根节点是黑色
  3. 叶子节点(NIL)是黑色
  4. 红节点的子节点必须是黑色
  5. 从任一节点到叶子的所有路径包含相同数量的黑节点

🎬 观看动画:
  插入操作会显示:
  1. 搜索路径逐步高亮
  2. 新节点飞入动画
  3. 颜色调整(变色)
  4. 旋转操作(左旋/右旋)
  5. 最终平衡状态
  
  查找操作会显示:
  1. 搜索路径逐步高亮
  2. 找到时节点变绿高亮
  3. 未找到时显示提示
  
  删除操作会显示:
  1. 搜索要删除的节点
  2. 节点淡出消失动画
  3. 替换节点处理
  4. 删除后平衡调整
  5. 旋转和重新着色

📌 注意事项:
  • create 命令会先清空现有树
  • search 支持批量查找多个值
  • delete 一次只能删除一个节点
  • 删除/查找不存在的节点会给出提示
  • 支持逗号或空格分隔数字
  • 只支持整数值
  • 动画执行期间无法进行其他操作
    """
    
    messagebox.showinfo("红黑树 DSL 命令帮助", help_text)


# 备用处理函数,用于在__init__.py中调用
def _fallback_process_command(visualizer, text: str) -> bool:
    """
    备用命令处理函数,用于模块导入
    
    Args:
        visualizer: RBTVisualizer实例
        text: DSL命令文本
        
    Returns:
        bool: 命令是否执行成功
    """
    return process(visualizer, text)