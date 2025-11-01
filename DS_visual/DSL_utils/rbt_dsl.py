"""
红黑树的DSL（领域特定语言）处理器
支持 create 和 clear 命令
"""

import re
from typing import List
from tkinter import messagebox

def process(visualizer, text: str) -> bool:
    """
    处理红黑树的DSL命令
    支持 create 和 clear 命令
    
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
    
    # 显示帮助
    elif text in ('help', '帮助', '?'):
        _show_help()
        return True
    
    else:
        messagebox.showinfo("未识别的命令", 
            f"无法识别的命令: {text}\n\n"
            "支持的命令:\n"
            "  • create 1,2,3,4,5  (批量创建红黑树)\n"
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
        # 使用逗号分隔格式，这是 start_insert_animated 期望的格式
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
        r'^(create|创建|批量创建)\s*',
        '', 
        text, 
        flags=re.IGNORECASE
    )
    
    # 提取数字模式：支持正整数、负整数
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

2. 清空树:
   clear

3. 清空后重新创建:
   clear
   create 10,20,30,40,50

═══════════════════════════════════════

✨ 红黑树特性:
  • 自平衡: 插入时自动调整保持平衡
  • 颜色规则: 维护红黑树的5条性质
  • 动画演示: 
    - 搜索路径高亮显示
    - 新节点飞入动画
    - 颜色调整过程
    - 左旋/右旋操作

🎨 颜色含义:
  • 🔴 红节点: 新插入的节点初始为红色
  • ⚫ 黑节点: 平衡后的节点或根节点
  • 🟢 路径高亮: 搜索路径
  • 🟠 操作高亮: 当前操作节点

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

📌 注意事项:
  • create 命令会先清空现有树
  • 支持逗号或空格分隔数字
  • 只支持整数值
  • 动画执行期间无法进行其他操作
    """
    
    messagebox.showinfo("红黑树 DSL 命令帮助", help_text)


# 备用处理函数，用于在__init__.py中调用
def _fallback_process_command(visualizer, text: str) -> bool:
    """
    备用命令处理函数，用于模块导入
    
    Args:
        visualizer: RBTVisualizer实例
        text: DSL命令文本
        
    Returns:
        bool: 命令是否执行成功
    """
    return process(visualizer, text)