"""
二叉树可视化工具的 DSL 命令处理器
支持构建、查找、插入、删除、遍历(静态和动画)、树属性查询等命令
"""

from tkinter import messagebox
import re

def process(visualizer, text: str):
    """
    处理二叉树可视化工具的 DSL 命令
    
    参数:
        visualizer: BinaryTreeVisualizer 实例
        text: 用户输入的命令文本
    """
    if not text or not text.strip():
        return
    
    raw = text.strip()
    
    # 将命令拆分:允许用空格或逗号分隔
    parts = [p for p in re.split(r'[\s,]+', raw) if p != ""]
    if not parts:
        return
    
    cmd = parts[0].lower()
    args = parts[1:]
    
    try:
        # ============================================
        # 树构建命令
        # ============================================
        if cmd in ("create", "animate"):
            if not args:
                messagebox.showinfo("用法", 
                    "示例: create 1 2 3 # 4 # 5\n"
                    "用空格或逗号分隔节点, # 表示空节点")
                return
            seq_text = " ".join(args)
            visualizer.input_var.set(seq_text)
            visualizer.start_animated_build()
            
        elif cmd == "build":
            if not args:
                messagebox.showinfo("用法", "示例: build 1 2 3 # 4 # 5")
                return
            seq_text = " ".join(args)
            visualizer.input_var.set(seq_text)
            visualizer.build_tree_from_input()
        
        # ============================================
        # 查找命令
        # ============================================
        elif cmd in ("search", "find"):
            if not hasattr(visualizer, "start_search_animation"):
                messagebox.showinfo("提示", "当前版本不支持查找动画")
                return
            if not args:
                visualizer.start_search_animation()
            else:
                visualizer.start_search_animation(args[0])
        
        # ============================================
        # 插入命令
        # ============================================
        elif cmd == "insert":
            if not hasattr(visualizer, "start_insert_animation"):
                messagebox.showinfo("提示", "当前版本不支持插入动画")
                return
            if not args:
                visualizer.start_insert_animation()
            else:
                value = args[0]
                parent_value = None
                direction = 'auto'
                
                # 解析插入参数
                # 格式1: insert <value>
                # 格式2: insert <value> <parent_value>
                # 格式3: insert <value> left <parent_value>
                # 格式4: insert <value> right <parent_value>
                if len(args) >= 3:
                    if args[1].lower() in ('left', 'l'):
                        direction = 'left'
                        parent_value = args[2]
                    elif args[1].lower() in ('right', 'r'):
                        direction = 'right'
                        parent_value = args[2]
                    elif args[2].lower() in ('left', 'l'):
                        parent_value = args[1]
                        direction = 'left'
                    elif args[2].lower() in ('right', 'r'):
                        parent_value = args[1]
                        direction = 'right'
                elif len(args) >= 2:
                    if args[1].lower() in ('left', 'l', 'right', 'r'):
                        direction = 'left' if args[1].lower() in ('left', 'l') else 'right'
                    else:
                        parent_value = args[1]
                
                visualizer.start_insert_animation(value, parent_value, direction)
        
        # ============================================
        # 删除命令
        # ============================================
        elif cmd == "delete":
            if not hasattr(visualizer, "start_delete_animation"):
                messagebox.showinfo("提示", "当前版本不支持删除动画")
                return
            if not args:
                visualizer.start_delete_animation()
            else:
                visualizer.start_delete_animation(args[0])
        
        # ============================================
        # 遍历命令 - 静态显示结果
        # ============================================
        elif cmd == "preorder":
            _show_traversal(visualizer, "preorder")
            
        elif cmd == "inorder":
            _show_traversal(visualizer, "inorder")
            
        elif cmd == "postorder":
            _show_traversal(visualizer, "postorder")
            
        elif cmd == "levelorder":
            _show_traversal(visualizer, "levelorder")
        
        # ============================================
        # 遍历动画命令
        # ============================================
        elif cmd in ("preorder-anim", "preorder-animate", "pre-anim"):
            if hasattr(visualizer, "start_preorder_animation"):
                visualizer.start_preorder_animation()
            else:
                messagebox.showinfo("提示", "当前版本不支持前序遍历动画")
                
        elif cmd in ("inorder-anim", "inorder-animate", "in-anim"):
            if hasattr(visualizer, "start_inorder_animation"):
                visualizer.start_inorder_animation()
            else:
                messagebox.showinfo("提示", "当前版本不支持中序遍历动画")
                
        elif cmd in ("postorder-anim", "postorder-animate", "post-anim"):
            if hasattr(visualizer, "start_postorder_animation"):
                visualizer.start_postorder_animation()
            else:
                messagebox.showinfo("提示", "当前版本不支持后序遍历动画")
        
        # ============================================
        # 树属性查询命令
        # ============================================
        elif cmd == "height":
            _show_tree_height(visualizer)
            
        elif cmd == "count":
            _show_node_count(visualizer)
            
        elif cmd == "depth":
            # depth 是 height 的别名
            _show_tree_height(visualizer)
        
        # ============================================
        # 显示控制命令
        # ============================================
        elif cmd in ("clear", "reset"):
            visualizer.clear_canvas()
            visualizer.update_status("DSL: 已清空画布", "#4299E1")
            
        # ============================================
        # 帮助和历史命令
        # ============================================
        elif cmd in ("help", "?"):
            _show_help()
            
        elif cmd == "history":
            if hasattr(visualizer, "show_command_history"):
                visualizer.show_command_history()
            else:
                messagebox.showinfo("提示", "历史记录功能不可用")
        
        # ============================================
        # 未知命令
        # ============================================
        else:
            messagebox.showinfo("未识别命令", 
                f"未知命令: {cmd}\n\n"
                "输入 'help' 查看可用命令列表")
    
    except Exception as e:
        messagebox.showerror("命令执行错误", 
            f"执行命令时发生错误:\n{str(e)}")
        if hasattr(visualizer, "update_status"):
            visualizer.update_status("DSL 错误", "#E53E3E")


# ============================================
# 辅助函数
# ============================================

def _show_traversal(visualizer, traversal_type: str):
    """显示遍历结果(静态)"""
    if not visualizer.root_node:
        messagebox.showinfo("遍历", "树为空,无法遍历")
        return
    
    result = []
    
    if traversal_type == "preorder":
        _preorder_traversal(visualizer.root_node, result)
        name = "前序"
    elif traversal_type == "inorder":
        _inorder_traversal(visualizer.root_node, result)
        name = "中序"
    elif traversal_type == "postorder":
        _postorder_traversal(visualizer.root_node, result)
        name = "后序"
    elif traversal_type == "levelorder":
        result = _levelorder_traversal(visualizer.root_node)
        name = "层序"
    else:
        return
    
    result_str = " → ".join(map(str, result))
    messagebox.showinfo(f"{name}遍历结果", 
        f"遍历序列:\n{result_str}\n\n"
        f"节点访问顺序: {len(result)} 个节点")
    
    if hasattr(visualizer, "update_status"):
        visualizer.update_status(f"{name}遍历完成", "#4299E1")


def _preorder_traversal(node, result):
    """前序遍历: 根 -> 左 -> 右"""
    if node:
        result.append(node.val)
        _preorder_traversal(node.left, result)
        _preorder_traversal(node.right, result)


def _inorder_traversal(node, result):
    """中序遍历: 左 -> 根 -> 右"""
    if node:
        _inorder_traversal(node.left, result)
        result.append(node.val)
        _inorder_traversal(node.right, result)


def _postorder_traversal(node, result):
    """后序遍历: 左 -> 右 -> 根"""
    if node:
        _postorder_traversal(node.left, result)
        _postorder_traversal(node.right, result)
        result.append(node.val)


def _levelorder_traversal(node):
    """层序遍历(广度优先)"""
    if not node:
        return []
    result = []
    queue = [node]
    while queue:
        current = queue.pop(0)
        result.append(current.val)
        if current.left:
            queue.append(current.left)
        if current.right:
            queue.append(current.right)
    return result


def _show_tree_height(visualizer):
    """显示树的高度"""
    height = _get_tree_height(visualizer.root_node)
    messagebox.showinfo("树高度", 
        f"树的高度为: {height}\n\n"
        f"说明: 树的高度是从根节点到最远叶节点的最长路径上的节点数")
    if hasattr(visualizer, "update_status"):
        visualizer.update_status(f"树高度: {height}", "#4299E1")


def _get_tree_height(node) -> int:
    """递归计算树高度"""
    if not node:
        return 0
    return 1 + max(_get_tree_height(node.left), 
                   _get_tree_height(node.right))


def _show_node_count(visualizer):
    """显示节点数量"""
    count = _count_nodes(visualizer.root_node)
    messagebox.showinfo("节点计数", 
        f"节点总数为: {count}\n\n"
        f"说明: 统计树中所有非空节点的数量")
    if hasattr(visualizer, "update_status"):
        visualizer.update_status(f"节点数: {count}", "#4299E1")


def _count_nodes(node) -> int:
    """递归计算节点数量"""
    if not node:
        return 0
    return 1 + _count_nodes(node.left) + _count_nodes(node.right)


def _show_help():
    """显示完整的帮助信息"""
    help_text = """
═══════════════════════════════════════
    二叉树 DSL 命令帮助文档
═══════════════════════════════════════

【树构建命令】
  build <序列>         一步构建完整的树
  create <序列>        逐步动画构建树
  animate <序列>       逐步动画构建树(同create)
  
  示例: build 1 2 3 # 4 # 5
       create 1 2 3 4 5 6 7

【节点操作命令】
  search <值>          查找节点 (动画演示)
  find <值>            查找节点 (同search)
  insert <值>          自动插入到第一个空位
  insert <值> left <父值>   插入为左子节点
  insert <值> right <父值>  插入为右子节点
  delete <值>          删除指定节点 (动画演示)

  示例: search 4
       insert 6 left 3
       insert 7 right 3
       delete 2

【遍历命令 - 显示结果】
  preorder            前序遍历 (根-左-右)
  inorder             中序遍历 (左-根-右)
  postorder           后序遍历 (左-右-根)
  levelorder          层序遍历 (逐层访问)

【遍历命令 - 动画演示】
  preorder-anim       前序遍历动画
  inorder-anim        中序遍历动画
  postorder-anim      后序遍历动画
  
  别名: pre-anim, in-anim, post-anim

【树属性查询】
  height              显示树的高度
  depth               显示树的深度(同height)
  count               统计节点总数

【显示控制】
  clear               清空画布
  reset               重置画布(同clear)

【其他命令】
  help / ?            显示此帮助信息
  history             查看命令历史记录

═══════════════════════════════════════
【使用说明】
  • 序列支持空格或逗号分隔
  • 使用 # 表示空节点
  • 按↑↓箭头键浏览历史命令
  • 所有操作都有动画演示效果
═══════════════════════════════════════
    """
    messagebox.showinfo("二叉树 DSL 命令帮助", help_text)