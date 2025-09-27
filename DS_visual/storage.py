# DS_visual/storage.py
# 通用保存/加载工具（JSON），支持二叉树(保存节点图) 与 线性结构（数组）

import json
from typing import Optional, Dict, Any, List
from tkinter import filedialog
import os
from datetime import datetime


def ensure_save_subdir(subdir: str) -> str:
    """
    确保 storage.py 同目录下的 save/<subdir> 文件夹存在，返回该目录的绝对路径。
    例如: ensure_save_subdir('stack') -> .../save/stack
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    target = os.path.join(base_dir, "save", subdir)
    os.makedirs(target, exist_ok=True)
    return target
# ---------- helpers for tree -> dict and dict -> tree ----------
def tree_to_dict(root) -> Dict[str, Any]:
    """
    将链式二叉树转换为字典：
    { "nodes": [ { "id": "n0", "val": value, "left": "n1" or None, "right": "n2" or None, "height": maybe }, ... ],
      "root": "n0" }
    root: 任意对象，要求存在 .val, .left, .right, 可选 .height 属性。
    """
    if root is None:
        return {"nodes": [], "root": None}
    id_map = {}
    nodes = []
    counter = 0

    def assign(node):
        nonlocal counter
        if node is None:
            return None
        if id(node) in id_map:
            return id_map[id(node)]
        nid = f"n{counter}"
        id_map[id(node)] = nid
        counter += 1
        left_id = assign(getattr(node, "left", None))
        right_id = assign(getattr(node, "right", None))
        node_dict = {
            "id": nid,
            "val": getattr(node, "val", None),
            "left": left_id,
            "right": right_id
        }
        # include height if present
        if hasattr(node, "height"):
            node_dict["height"] = getattr(node, "height")
        nodes.append(node_dict)
        return nid

    root_id = assign(root)
    return {"nodes": nodes, "root": root_id}

def dict_to_avlroot(d: Dict[str, Any]):
    """
    将 tree_dict 转回 AVLNode 风格的节点图（使用已有 AVLNode 类构造）
    这里不会 import AVLNode，调用方应再次转换为合适的类或将此函数粘到对应 visual 模块里。
    为方便，你可以把下面的逻辑复制到使用的模块并替换 NodeClass。
    """
    # This generic version will return a plain dict describing nodes; caller should reconstruct
    return d

# ---------- tree-specific (AVL/BST/BinaryTree) serializer helpers ----------
def save_tree_to_file(root, filepath: Optional[str] = None):
    """
    保存任意链式二叉树（node 有 .val/.left/.right/.height 可选）到 filepath（JSON）。
    如果 filepath 为 None，会弹出文件对话框让用户选择。
    """
    if filepath is None:
        filepath = filedialog.asksaveasfilename(defaultextension=".json",
                                                filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if not filepath:
            return False
    d = tree_to_dict(root)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump({"type": "tree", "tree": d}, f, indent=2, ensure_ascii=False)
    return True

def load_tree_from_file(filepath: Optional[str] = None) -> Dict[str, Any]:
    """
    从文件加载 tree dict（与 tree_to_dict 生成的格式一致）。
    返回 dict（包含 "nodes" 和 "root"），但**不会**自动转换成模型类对象（因为模型类在不同模块中）。
    调用方需要把该 dict 转换成对应模型的节点实例（我在下面给出一个示例转换函数）。
    """
    if filepath is None:
        filepath = filedialog.askopenfilename(filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if not filepath:
            return {}
    with open(filepath, "r", encoding="utf-8") as f:
        obj = json.load(f)
    if not obj:
        return {}
    # support both generic and typed saves
    if obj.get("type") == "tree":
        return obj.get("tree", {})
    # fallback: if old files stored structure differently
    return obj

# ---------- linear structures (stack, list) ----------
def save_list_to_file(arr, filepath: Optional[str] = None):
    if filepath is None:
        filepath = filedialog.asksaveasfilename(defaultextension=".json",
                                                filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if not filepath:
            return False
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump({"type": "list", "data": arr}, f, indent=2, ensure_ascii=False)
    return True

def load_list_from_file(filepath: Optional[str] = None):
    if filepath is None:
        filepath = filedialog.askopenfilename(filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if not filepath:
            return None
    with open(filepath, "r", encoding="utf-8") as f:
        obj = json.load(f)
    if not obj:
        return None
    return obj.get("data")

# ---------- convenience: reconstruct tree into model-specific Node class ----------
def tree_dict_to_nodes(tree_dict, NodeClass):
    """
    把 tree_dict 转换为以 NodeClass 构造的节点图并返回 root。
    NodeClass 需要可以按 NodeClass(val) 创建实例，并支持 .left/.right/.parent/.height 设置。
    """
    if not tree_dict or not tree_dict.get("nodes"):
        return None
    nodes = tree_dict["nodes"]
    # create map id->nodeobj
    id_to_obj = {}
    for item in nodes:
        nid = item["id"]
        val = item.get("val")
        node = NodeClass(val)
        # set height if NodeClass 有 height 属性
        if "height" in item and hasattr(node, "height"):
            try:
                node.height = item.get("height")
            except Exception:
                pass
        id_to_obj[nid] = node
    # second pass: wire children and parents
    for item in nodes:
        nid = item["id"]
        node = id_to_obj[nid]
        left_id = item.get("left")
        right_id = item.get("right")
        if left_id:
            node.left = id_to_obj[left_id]
            id_to_obj[left_id].parent = node if hasattr(id_to_obj[left_id], "parent") else None
        if right_id:
            node.right = id_to_obj[right_id]
            id_to_obj[right_id].parent = node if hasattr(id_to_obj[right_id], "parent") else None
    root_id = tree_dict.get("root")
    return id_to_obj.get(root_id)

def _ensure_default_folder():
    """确保默认保存/打开目录存在，返回绝对路径"""
    base_dir = os.path.dirname(os.path.abspath(__file__))  # storage.py 所在目录
    default_dir = os.path.join(base_dir, "save", "linked_list")
    os.makedirs(default_dir, exist_ok=True)
    return default_dir

def save_linked_list_to_file(node_values: List, filepath: Optional[str] = None) -> bool:
    """
    保存单链表数据到文件。
    node_values: 链表节点的值列表（按顺序）
    如果 filepath 为 None，会弹出保存对话框，初始目录为 save/linked_list，默认文件名 linked_list_YYYYmmdd_HHMMSS.json
    """
    default_dir = _ensure_default_folder()

    if filepath is None:
        default_name = f"linked_list_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = filedialog.asksaveasfilename(
            initialdir=default_dir,
            initialfile=default_name,
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="保存链表到文件"
        )
        if not filepath:
            return False

    linked_list_data = {
        "type": "linked_list",
        "data": node_values,
        "metadata": {
            "length": len(node_values),
            "structure": "singly_linked_list"
        }
    }

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(linked_list_data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"保存链表时出错: {e}")
        return False

def load_linked_list_from_file(filepath: Optional[str] = None) -> Optional[List]:
    """
    从文件加载链表数据（返回节点值列表），如果失败返回 None。
    如果 filepath 为 None，会弹出打开对话框，初始目录为 save/linked_list。
    """
    default_dir = _ensure_default_folder()

    if filepath is None:
        filepath = filedialog.askopenfilename(
            initialdir=default_dir,
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="从文件加载链表"
        )
        if not filepath:
            return None

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            obj = json.load(f)

        if not obj:
            return None

        if obj.get("type") == "linked_list":
            return obj.get("data", [])
        else:
            # 兼容旧格式：如果文件就是一个 list
            return obj if isinstance(obj, list) else None

    except Exception as e:
        print(f"加载链表时出错: {e}")
        return None

# --------- example usage comments ----------
# 在 AVL/ BST visualizer 中，你可以：
#  1) 保存: storage.save_tree_to_file(self.model.root)
#  2) 打开: tree_dict = storage.load_tree_from_file(); newroot = storage.tree_dict_to_nodes(tree_dict, AVLNodeClass); self.model.root = newroot; redraw()
#
# 在 Stack/Sequence/LinkedList visualizer 中使用 save_list_to_file/load_list_from_file。
