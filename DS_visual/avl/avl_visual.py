from tkinter import *
from tkinter import messagebox
from typing import Dict, Tuple, List, Optional
from avl.avl_model import AVLModel, AVLNode, clone_tree
import storage as storage
from tkinter import filedialog
from datetime import datetime
# 确保 TclError 被导入，以便在动画中捕获异常
from tkinter import TclError 

# ========== 多语言伪代码定义 ==========

# 语言选项
LANG_PSEUDOCODE = "伪代码"
LANG_C = "C语言"
LANG_JAVA = "Java"
LANG_PYTHON = "Python"
CODE_LANGUAGES = [LANG_PSEUDOCODE, LANG_C, LANG_JAVA, LANG_PYTHON]

# AVL插入 - 多语言
MULTILANG_INSERT = {
    "伪代码": [
        "INSERT(tree, val):",
        "  if tree.root = null then",
        "    tree.root ← new Node(val)",
        "    return",
        "  end if",
        "  node ← tree.root",
        "  while true do",
        "    if val < node.val then",
        "      if node.left = null then",
        "        node.left ← new Node(val)",
        "        break",
        "      end if",
        "      node ← node.left",
        "    else",
        "      if node.right = null then",
        "        node.right ← new Node(val)",
        "        break",
        "      end if",
        "      node ← node.right",
        "    end if",
        "  end while",
        "  // 回溯更新高度并检查平衡",
        "  REBALANCE(new_node.parent)",
    ],
    "C语言": [
        "void insert(AVLTree* tree, int val) {",
        "  if (tree->root == NULL) {",
        "    tree->root = create_node(val);",
        "    return;",
        "  }",
        "  Node* node = tree->root;",
        "  while (1) {",
        "    if (val < node->val) {",
        "      if (node->left == NULL) {",
        "        node->left = create_node(val);",
        "        break;",
        "      }",
        "      node = node->left;",
        "    } else {",
        "      if (node->right == NULL) {",
        "        node->right = create_node(val);",
        "        break;",
        "      }",
        "      node = node->right;",
        "    }",
        "  }",
        "  // 回溯更新高度并检查平衡",
        "  rebalance(new_node->parent);",
        "}",
    ],
    "Java": [
        "void insert(AVLTree tree, int val) {",
        "  if (tree.root == null) {",
        "    tree.root = new Node(val);",
        "    return;",
        "  }",
        "  Node node = tree.root;",
        "  while (true) {",
        "    if (val < node.val) {",
        "      if (node.left == null) {",
        "        node.left = new Node(val);",
        "        break;",
        "      }",
        "      node = node.left;",
        "    } else {",
        "      if (node.right == null) {",
        "        node.right = new Node(val);",
        "        break;",
        "      }",
        "      node = node.right;",
        "    }",
        "  }",
        "  // 回溯更新高度并检查平衡",
        "  rebalance(newNode.parent);",
        "}",
    ],
    "Python": [
        "def insert(tree, val):",
        "  if tree.root is None:",
        "    tree.root = Node(val)",
        "    return",
        "  # endif",
        "  node = tree.root",
        "  while True:",
        "    if val < node.val:",
        "      if node.left is None:",
        "        node.left = Node(val)",
        "        break",
        "      # endif",
        "      node = node.left",
        "    else:",
        "      if node.right is None:",
        "        node.right = Node(val)",
        "        break",
        "      # endif",
        "      node = node.right",
        "    # endif",
        "  # endwhile",
        "  # 回溯更新高度并检查平衡",
        "  rebalance(new_node.parent)",
    ]
}

# AVL删除 - 多语言
MULTILANG_DELETE = {
    "伪代码": [
        "DELETE(tree, val):",
        "  node ← SEARCH(tree.root, val)",
        "  if node = null then",
        "    return  // 未找到",
        "  end if",
        "  if node有两个子节点 then",
        "    successor ← MIN(node.right)",
        "    node.val ← successor.val",
        "    node ← successor",
        "  end if",
        "  // 现在node最多有一个子节点",
        "  child ← node.left or node.right",
        "  REPLACE(node, child)",
        "  // 回溯更新高度并检查平衡",
        "  REBALANCE(parent)",
    ],
    "C语言": [
        "void delete(AVLTree* tree, int val) {",
        "  Node* node = search(tree->root, val);",
        "  if (node == NULL) {",
        "    return; // 未找到",
        "  }",
        "  if (node->left && node->right) { // 两个子节点",
        "    Node* successor = minimum(node->right);",
        "    node->val = successor->val;",
        "    node = successor;",
        "  }",
        "  // 现在node最多有一个子节点",
        "  Node* child = node->left ? node->left : node->right;",
        "  replace(tree, node, child);",
        "  // 回溯更新高度并检查平衡",
        "  rebalance(parent);",
        "}",
    ],
    "Java": [
        "void delete(AVLTree tree, int val) {",
        "  Node node = search(tree.root, val);",
        "  if (node == null) {",
        "    return; // 未找到",
        "  }",
        "  if (node.left != null && node.right != null) {",
        "    Node successor = minimum(node.right);",
        "    node.val = successor.val;",
        "    node = successor;",
        "  }",
        "  // 现在node最多有一个子节点",
        "  Node child = (node.left != null) ? node.left : node.right;",
        "  replace(tree, node, child);",
        "  // 回溯更新高度并检查平衡",
        "  rebalance(parent);",
        "}",
    ],
    "Python": [
        "def delete(tree, val):",
        "  node = search(tree.root, val)",
        "  if node is None:",
        "    return  # 未找到",
        "  # endif",
        "  if node.left and node.right:  # 两个子节点",
        "    successor = minimum(node.right)",
        "    node.val = successor.val",
        "    node = successor",
        "  # endif",
        "  # 现在node最多有一个子节点",
        "  child = node.left if node.left else node.right",
        "  replace(tree, node, child)",
        "  # 回溯更新高度并检查平衡",
        "  rebalance(parent)",
    ]
}

# AVL再平衡 - 多语言
MULTILANG_REBALANCE = {
    "伪代码": [
        "REBALANCE(node):",
        "  while node ≠ null do",
        "    UPDATE_HEIGHT(node)",
        "    bf ← BALANCE_FACTOR(node)",
        "    if bf > 1 then  // 左重",
        "      if BF(node.left) ≥ 0 then",
        "        LL旋转: RIGHT_ROTATE(node)",
        "      else",
        "        LR旋转: LEFT_ROTATE(left)",
        "               RIGHT_ROTATE(node)",
        "      end if",
        "    end if",
        "    if bf < -1 then  // 右重",
        "      if BF(node.right) ≤ 0 then",
        "        RR旋转: LEFT_ROTATE(node)",
        "      else",
        "        RL旋转: RIGHT_ROTATE(right)",
        "               LEFT_ROTATE(node)",
        "      end if",
        "    end if",
        "    node ← node.parent",
        "  end while",
    ],
    "C语言": [
        "void rebalance(Node* node) {",
        "  while (node != NULL) {",
        "    update_height(node);",
        "    int bf = balance_factor(node);",
        "    if (bf > 1) { // 左重",
        "      if (balance_factor(node->left) >= 0) {",
        "        // LL旋转",
        "        node = right_rotate(node);",
        "      } else {",
        "        // LR旋转",
        "        node->left = left_rotate(node->left);",
        "        node = right_rotate(node);",
        "      }",
        "    }",
        "    if (bf < -1) { // 右重",
        "      if (balance_factor(node->right) <= 0) {",
        "        // RR旋转",
        "        node = left_rotate(node);",
        "      } else {",
        "        // RL旋转",
        "        node->right = right_rotate(node->right);",
        "        node = left_rotate(node);",
        "      }",
        "    }",
        "    node = node->parent;",
        "  }",
        "}",
    ],
    "Java": [
        "void rebalance(Node node) {",
        "  while (node != null) {",
        "    updateHeight(node);",
        "    int bf = balanceFactor(node);",
        "    if (bf > 1) { // 左重",
        "      if (balanceFactor(node.left) >= 0) {",
        "        // LL旋转",
        "        node = rightRotate(node);",
        "      } else {",
        "        // LR旋转",
        "        node.left = leftRotate(node.left);",
        "        node = rightRotate(node);",
        "      }",
        "    }",
        "    if (bf < -1) { // 右重",
        "      if (balanceFactor(node.right) <= 0) {",
        "        // RR旋转",
        "        node = leftRotate(node);",
        "      } else {",
        "        // RL旋转",
        "        node.right = rightRotate(node.right);",
        "        node = leftRotate(node);",
        "      }",
        "    }",
        "    node = node.parent;",
        "  }",
        "}",
    ],
    "Python": [
        "def rebalance(node):",
        "  while node is not None:",
        "    update_height(node)",
        "    bf = balance_factor(node)",
        "    if bf > 1:  # 左重",
        "      if balance_factor(node.left) >= 0:",
        "        # LL旋转",
        "        node = right_rotate(node)",
        "      else:",
        "        # LR旋转",
        "        node.left = left_rotate(node.left)",
        "        node = right_rotate(node)",
        "      # endif",
        "    # endif",
        "    if bf < -1:  # 右重",
        "      if balance_factor(node.right) <= 0:",
        "        # RR旋转",
        "        node = left_rotate(node)",
        "      else:",
        "        # RL旋转",
        "        node.right = right_rotate(node.right)",
        "        node = left_rotate(node)",
        "      # endif",
        "    # endif",
        "    node = node.parent",
        "  # endwhile",
    ]
}

# LL旋转 - 多语言
MULTILANG_LL = {
    "伪代码": [
        "LL旋转 - RIGHT_ROTATE(z):",
        "  y ← z.left",
        "  T3 ← y.right",
        "  y.right ← z",
        "  z.left ← T3",
        "  更新z和y的高度",
        "  return y  // 新的子树根",
    ],
    "C语言": [
        "// LL旋转 - 右旋",
        "Node* right_rotate(Node* z) {",
        "  Node* y = z->left;",
        "  Node* T3 = y->right;",
        "  y->right = z;",
        "  z->left = T3;",
        "  update_height(z);",
        "  update_height(y);",
        "  return y; // 新的子树根",
        "}",
    ],
    "Java": [
        "// LL旋转 - 右旋",
        "Node rightRotate(Node z) {",
        "  Node y = z.left;",
        "  Node T3 = y.right;",
        "  y.right = z;",
        "  z.left = T3;",
        "  updateHeight(z);",
        "  updateHeight(y);",
        "  return y; // 新的子树根",
        "}",
    ],
    "Python": [
        "# LL旋转 - 右旋",
        "def right_rotate(z):",
        "  y = z.left",
        "  T3 = y.right",
        "  y.right = z",
        "  z.left = T3",
        "  update_height(z)",
        "  update_height(y)",
        "  return y  # 新的子树根",
    ]
}

# RR旋转 - 多语言
MULTILANG_RR = {
    "伪代码": [
        "RR旋转 - LEFT_ROTATE(z):",
        "  y ← z.right",
        "  T2 ← y.left",
        "  y.left ← z",
        "  z.right ← T2",
        "  更新z和y的高度",
        "  return y  // 新的子树根",
    ],
    "C语言": [
        "// RR旋转 - 左旋",
        "Node* left_rotate(Node* z) {",
        "  Node* y = z->right;",
        "  Node* T2 = y->left;",
        "  y->left = z;",
        "  z->right = T2;",
        "  update_height(z);",
        "  update_height(y);",
        "  return y; // 新的子树根",
        "}",
    ],
    "Java": [
        "// RR旋转 - 左旋",
        "Node leftRotate(Node z) {",
        "  Node y = z.right;",
        "  Node T2 = y.left;",
        "  y.left = z;",
        "  z.right = T2;",
        "  updateHeight(z);",
        "  updateHeight(y);",
        "  return y; // 新的子树根",
        "}",
    ],
    "Python": [
        "# RR旋转 - 左旋",
        "def left_rotate(z):",
        "  y = z.right",
        "  T2 = y.left",
        "  y.left = z",
        "  z.right = T2",
        "  update_height(z)",
        "  update_height(y)",
        "  return y  # 新的子树根",
    ]
}

# LR旋转 - 多语言
MULTILANG_LR = {
    "伪代码": [
        "LR旋转 (先左旋后右旋):",
        "  y ← z.left",
        "  x ← y.right",
        "  // 第一步: 对y左旋",
        "  LEFT_ROTATE(y)",
        "  // 第二步: 对z右旋",
        "  RIGHT_ROTATE(z)",
        "  return x  // 新的子树根",
    ],
    "C语言": [
        "// LR旋转 (先左旋后右旋)",
        "Node* lr_rotate(Node* z) {",
        "  Node* y = z->left;",
        "  Node* x = y->right;",
        "  // 第一步: 对y左旋",
        "  z->left = left_rotate(y);",
        "  // 第二步: 对z右旋",
        "  return right_rotate(z);",
        "}",
    ],
    "Java": [
        "// LR旋转 (先左旋后右旋)",
        "Node lrRotate(Node z) {",
        "  Node y = z.left;",
        "  Node x = y.right;",
        "  // 第一步: 对y左旋",
        "  z.left = leftRotate(y);",
        "  // 第二步: 对z右旋",
        "  return rightRotate(z);",
        "}",
    ],
    "Python": [
        "# LR旋转 (先左旋后右旋)",
        "def lr_rotate(z):",
        "  y = z.left",
        "  x = y.right",
        "  # 第一步: 对y左旋",
        "  z.left = left_rotate(y)",
        "  # 第二步: 对z右旋",
        "  return right_rotate(z)",
    ]
}

# RL旋转 - 多语言
MULTILANG_RL = {
    "伪代码": [
        "RL旋转 (先右旋后左旋):",
        "  y ← z.right",
        "  x ← y.left",
        "  // 第一步: 对y右旋",
        "  RIGHT_ROTATE(y)",
        "  // 第二步: 对z左旋",
        "  LEFT_ROTATE(z)",
        "  return x  // 新的子树根",
    ],
    "C语言": [
        "// RL旋转 (先右旋后左旋)",
        "Node* rl_rotate(Node* z) {",
        "  Node* y = z->right;",
        "  Node* x = y->left;",
        "  // 第一步: 对y右旋",
        "  z->right = right_rotate(y);",
        "  // 第二步: 对z左旋",
        "  return left_rotate(z);",
        "}",
    ],
    "Java": [
        "// RL旋转 (先右旋后左旋)",
        "Node rlRotate(Node z) {",
        "  Node y = z.right;",
        "  Node x = y.left;",
        "  // 第一步: 对y右旋",
        "  z.right = rightRotate(y);",
        "  // 第二步: 对z左旋",
        "  return leftRotate(z);",
        "}",
    ],
    "Python": [
        "# RL旋转 (先右旋后左旋)",
        "def rl_rotate(z):",
        "  y = z.right",
        "  x = y.left",
        "  # 第一步: 对y右旋",
        "  z.right = right_rotate(y)",
        "  # 第二步: 对z左旋",
        "  return left_rotate(z)",
    ]
}

# 搜索 - 多语言
MULTILANG_SEARCH = {
    "伪代码": [
        "SEARCH(node, val):",
        "  while node ≠ null do",
        "    if val = node.val then",
        "      return node  // 找到",
        "    end if",
        "    if val < node.val then",
        "      node ← node.left",
        "    else",
        "      node ← node.right",
        "    end if",
        "  end while",
        "  return null  // 未找到",
    ],
    "C语言": [
        "Node* search(Node* node, int val) {",
        "  while (node != NULL) {",
        "    if (val == node->val) {",
        "      return node; // 找到",
        "    }",
        "    if (val < node->val) {",
        "      node = node->left;",
        "    } else {",
        "      node = node->right;",
        "    }",
        "  }",
        "  return NULL; // 未找到",
        "}",
    ],
    "Java": [
        "Node search(Node node, int val) {",
        "  while (node != null) {",
        "    if (val == node.val) {",
        "      return node; // 找到",
        "    }",
        "    if (val < node.val) {",
        "      node = node.left;",
        "    } else {",
        "      node = node.right;",
        "    }",
        "  }",
        "  return null; // 未找到",
        "}",
    ],
    "Python": [
        "def search(node, val):",
        "  while node is not None:",
        "    if val == node.val:",
        "      return node  # 找到",
        "    # endif",
        "    if val < node.val:",
        "      node = node.left",
        "    else:",
        "      node = node.right",
        "    # endif",
        "  # endwhile",
        "  return None  # 未找到",
    ]
}

# 保持向后兼容的旧变量（默认使用伪代码）
PSEUDOCODE_INSERT = MULTILANG_INSERT["伪代码"]
PSEUDOCODE_DELETE = MULTILANG_DELETE["伪代码"]
PSEUDOCODE_REBALANCE = MULTILANG_REBALANCE["伪代码"]
PSEUDOCODE_LL = MULTILANG_LL["伪代码"]
PSEUDOCODE_RR = MULTILANG_RR["伪代码"]
PSEUDOCODE_LR = MULTILANG_LR["伪代码"]
PSEUDOCODE_RL = MULTILANG_RL["伪代码"]
PSEUDOCODE_SEARCH = MULTILANG_SEARCH["伪代码"]

class AVLVisualizer:
    # ... __init__ ...
    # (init, 颜色, 字体等保持不变)
    def __init__(self, root):
        self.window = root
        self.is_embedded = hasattr(root, 'title') and callable(root.title)
        
        # 代码语言设置（支持运行时切换）
        self.current_code_language = LANG_PSEUDOCODE  # 默认伪代码
        self.current_operation_type = None  # 当前操作类型
        self.current_highlight_line = -1  # 当前高亮行
        
        if self.is_embedded:
            self.window.title("🌳 AVL 树可视化系统")
            self.window.config(bg="#1E1E2E")
            self.window.geometry("1550x820")  # 增大窗口以容纳伪代码面板
        else:
            self.window.config(bg="#1E1E2E")
        
        self.title_font = ("Segoe UI", 16, "bold")
        self.label_font = ("Segoe UI", 11)
        self.button_font = ("Segoe UI", 10, "bold")
        self.status_font = ("Segoe UI", 10, "italic")
        self.code_font = ("Consolas", 10)  # 伪代码字体
        
        self.colors = {
            "bg_primary": "#1E1E2E",
            "bg_secondary": "#2D2D44",
            "bg_canvas": "#FFFFFF",
            "accent_green": "#4CAF50",
            "accent_blue": "#2196F3",
            "accent_orange": "#FF9800",
            "accent_purple": "#9C27B0",
            "accent_red": "#F44336",
            "text_light": "#FFFFFF",
            "text_dark": "#2D2D44",
            "node_normal": "#E3F2FD",
            "node_highlight": "#FFF9C4",
            "node_new": "#C8E6C9",
            "edge_color": "#616161",
            # 伪代码相关颜色
            "code_bg": "#1E1E2E",
            "code_fg": "#D4D4D4",
            "code_highlight_bg": "#264F78",
            "code_highlight_fg": "#FFFFFF",
            "code_keyword": "#569CD6",
            "code_comment": "#6A9955",
        }
        
        # 创建主容器框架
        if self.is_embedded:
            self.main_container = Frame(self.window, bg=self.colors["bg_primary"])
            self.main_container.pack(fill=BOTH, expand=True, padx=15, pady=10)
            self.canvas_w = 950
            self.canvas_h = 500
        else:
            self.main_container = Frame(self.window, bg=self.colors["bg_primary"])
            self.main_container.grid(row=0, column=0, columnspan=4, sticky="nsew", padx=10, pady=5)
            self.canvas_w = 850
            self.canvas_h = 450
        
        # 创建左侧画布区域
        self.canvas_frame = Frame(self.main_container, bg=self.colors["bg_primary"])
        self.canvas_frame.pack(side=LEFT, fill=BOTH, expand=True)
        
        self.canvas = Canvas(
            self.canvas_frame, 
            bg=self.colors["bg_canvas"], 
            width=self.canvas_w, 
            height=self.canvas_h,
            bd=4, 
            relief=GROOVE,
            highlightthickness=2,
            highlightbackground=self.colors["accent_blue"]
        )
        self.canvas.pack(fill=BOTH, expand=True)
        
        # 创建右侧伪代码面板
        self._create_pseudocode_panel()

        self.model = AVLModel()
        self.node_vis: Dict[str, Dict] = {}
        self.animating = False
        self.batch: List[str] = []
        self.current_pseudocode: List[str] = []  # 当前显示的伪代码

        self.node_w = 120
        self.node_h = 44
        self.level_gap = 100
        self.margin_x = 40

        self.input_var = StringVar()
        self.create_controls()
        self.draw_instructions()
    
    def _create_pseudocode_panel(self):
        """创建伪代码显示面板"""
        # 伪代码面板容器
        self.code_panel = Frame(
            self.main_container, 
            bg=self.colors["bg_secondary"],
            width=340
        )
        self.code_panel.pack(side=RIGHT, fill=Y, padx=(10, 0))
        self.code_panel.pack_propagate(False)
        
        # 标题栏（包含标题和语言切换）
        title_frame = Frame(self.code_panel, bg=self.colors["bg_secondary"])
        title_frame.pack(fill=X, padx=10, pady=(10, 5))
        
        # 伪代码标题
        code_title = Label(
            title_frame,
            text="📝 算法代码",
            bg=self.colors["bg_secondary"],
            fg=self.colors["text_light"],
            font=("Segoe UI", 12, "bold")
        )
        code_title.pack(side=LEFT)
        
        # 语言切换下拉框
        self.code_lang_var = StringVar(value=self.current_code_language)
        self.lang_menu = OptionMenu(
            title_frame, 
            self.code_lang_var, 
            *CODE_LANGUAGES,
            command=self._on_code_language_change
        )
        self.lang_menu.config(
            font=("微软雅黑", 9),
            bg="#3D3D5C",
            fg="#FFFFFF",
            activebackground="#4D4D6C",
            activeforeground="#FFFFFF",
            highlightthickness=0,
            relief="flat",
            width=6
        )
        self.lang_menu["menu"].config(
            bg="#3D3D5C",
            fg="#FFFFFF",
            activebackground="#2196F3",
            activeforeground="#FFFFFF",
            font=("微软雅黑", 9)
        )
        self.lang_menu.pack(side=RIGHT)
        
        # 语言切换快捷按钮组
        btn_frame = Frame(self.code_panel, bg=self.colors["bg_secondary"])
        btn_frame.pack(fill=X, padx=10, pady=(0, 5))
        
        self.lang_buttons = {}
        for lang in CODE_LANGUAGES:
            short_name = {"伪代码": "伪代码", "C语言": "C", "Java": "Java", "Python": "Py"}.get(lang, lang)
            btn = Label(
                btn_frame,
                text=short_name,
                font=("微软雅黑", 8),
                bg="#2196F3" if lang == self.current_code_language else "#3D3D5C",
                fg="#FFFFFF",
                padx=8,
                pady=2,
                cursor="hand2"
            )
            btn.pack(side=LEFT, padx=2)
            btn.bind("<Button-1>", lambda e, l=lang: self._switch_code_language(l))
            self.lang_buttons[lang] = btn
        
        # 伪代码文本框架（带滚动条）
        code_text_frame = Frame(self.code_panel, bg=self.colors["code_bg"])
        code_text_frame.pack(fill=BOTH, expand=True, padx=10, pady=(0, 10))
        
        # 滚动条
        scrollbar = Scrollbar(code_text_frame)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # 伪代码文本框
        self.code_text = Text(
            code_text_frame,
            bg=self.colors["code_bg"],
            fg=self.colors["code_fg"],
            font=self.code_font,
            width=35,
            height=26,
            wrap=NONE,
            state=DISABLED,
            relief=FLAT,
            padx=8,
            pady=8,
            cursor="arrow",
            selectbackground=self.colors["code_highlight_bg"]
        )
        self.code_text.pack(side=LEFT, fill=BOTH, expand=True)
        
        # 配置滚动条
        scrollbar.config(command=self.code_text.yview)
        self.code_text.config(yscrollcommand=scrollbar.set)
        
        # 配置文本标签用于高亮
        self.code_text.tag_config(
            "highlight",
            background=self.colors["code_highlight_bg"],
            foreground=self.colors["code_highlight_fg"]
        )
        self.code_text.tag_config(
            "keyword",
            foreground=self.colors["code_keyword"]
        )
        self.code_text.tag_config(
            "comment",
            foreground=self.colors["code_comment"]
        )
        self.code_text.tag_config(
            "normal",
            foreground=self.colors["code_fg"]
        )
        
        # 显示初始提示
        self._show_initial_code_hint()
    
    def _on_code_language_change(self, selected_lang):
        """语言切换回调（下拉框）"""
        self._switch_code_language(selected_lang)
    
    def _switch_code_language(self, new_lang):
        """
        切换代码语言并重新渲染
        
        Args:
            new_lang: 新的语言名称
        """
        if new_lang == self.current_code_language:
            return
        
        self.current_code_language = new_lang
        self.code_lang_var.set(new_lang)
        
        # 更新按钮样式
        for lang, btn in self.lang_buttons.items():
            if lang == new_lang:
                btn.config(bg="#2196F3")
            else:
                btn.config(bg="#3D3D5C")
        
        # 保存当前高亮行
        saved_highlight = self.current_highlight_line
        
        # 如果有当前操作类型，重新显示该语言的代码
        if self.current_operation_type:
            self._show_pseudocode_for_operation(self.current_operation_type, saved_highlight)
    
    def _show_initial_code_hint(self):
        """显示初始提示信息"""
        hint_text = [
            "💡 伪代码显示区域",
            "",
            "执行插入或删除操作时，",
            "这里会显示对应的算法伪代码，",
            "并实时高亮当前执行的步骤。",
            "",
            "📌 支持的操作：",
            "  • 插入节点 (Insert)",
            "  • 删除节点 (Delete)",
            "  • LL/RR/LR/RL 旋转",
            "",
            "🎯 使用方法：",
            "  1. 在输入框输入数字",
            "  2. 点击 Insert 或 Delete",
            "  3. 观察动画和伪代码高亮",
        ]
        self._set_pseudocode(hint_text)
    
    def _set_pseudocode(self, lines: List[str], highlight_line: int = -1):
        """
        设置伪代码内容并可选地高亮某一行
        
        Args:
            lines: 伪代码行列表
            highlight_line: 要高亮的行号 (0-based)，-1 表示不高亮
        """
        self.current_pseudocode = lines
        self.code_text.config(state=NORMAL)
        self.code_text.delete("1.0", END)
        
        for i, line in enumerate(lines):
            # 插入行
            self.code_text.insert(END, line + "\n")
            
            # 确定行的标签
            line_start = f"{i+1}.0"
            line_end = f"{i+1}.end"
            
            if i == highlight_line:
                # 高亮当前行
                self.code_text.tag_add("highlight", line_start, line_end)
            else:
                # 应用语法高亮
                self._apply_syntax_highlight(i + 1, line)
        
        self.code_text.config(state=DISABLED)
        
        # 如果有高亮行，滚动到该行
        if highlight_line >= 0:
            self.code_text.see(f"{highlight_line + 1}.0")
    
    def _apply_syntax_highlight(self, line_num: int, line: str):
        """应用简单的语法高亮"""
        line_start = f"{line_num}.0"
        
        # 检测注释
        if "//" in line:
            comment_idx = line.index("//")
            comment_start = f"{line_num}.{comment_idx}"
            self.code_text.tag_add("comment", comment_start, f"{line_num}.end")
        
        # 检测关键字
        keywords = ["if", "else", "while", "return", "null", "new", "break", "or", "and"]
        for kw in keywords:
            start = 0
            while True:
                idx = line.find(kw, start)
                if idx == -1:
                    break
                # 确保是完整单词
                before_ok = idx == 0 or not line[idx-1].isalnum()
                after_ok = idx + len(kw) >= len(line) or not line[idx + len(kw)].isalnum()
                if before_ok and after_ok:
                    kw_start = f"{line_num}.{idx}"
                    kw_end = f"{line_num}.{idx + len(kw)}"
                    self.code_text.tag_add("keyword", kw_start, kw_end)
                start = idx + 1
    
    def _highlight_line(self, line_num: int):
        """
        高亮指定行（不重新设置整个伪代码）
        
        Args:
            line_num: 要高亮的行号 (0-based)，-1 表示清除所有高亮
        """
        self.code_text.config(state=NORMAL)
        
        # 清除所有高亮
        self.code_text.tag_remove("highlight", "1.0", END)
        
        if line_num >= 0 and line_num < len(self.current_pseudocode):
            line_start = f"{line_num + 1}.0"
            line_end = f"{line_num + 1}.end"
            self.code_text.tag_add("highlight", line_start, line_end)
            self.code_text.see(line_start)
        
        self.code_text.config(state=DISABLED)
    
    def _show_pseudocode_for_operation(self, operation: str, highlight_line: int = -1):
        """
        显示指定操作的伪代码（支持多语言）
        
        Args:
            operation: 操作类型 ('insert', 'delete', 'search', 'rebalance', 'LL', 'RR', 'LR', 'RL')
            highlight_line: 要高亮的行号 (0-based)
        """
        # 保存当前状态，用于语言切换时恢复
        self.current_operation_type = operation
        self.current_highlight_line = highlight_line
        
        # 多语言代码映射
        multilang_map = {
            'insert': MULTILANG_INSERT,
            'delete': MULTILANG_DELETE,
            'search': MULTILANG_SEARCH,
            'rebalance': MULTILANG_REBALANCE,
            'LL': MULTILANG_LL,
            'RR': MULTILANG_RR,
            'LR': MULTILANG_LR,
            'RL': MULTILANG_RL,
        }
        
        if operation in multilang_map:
            # 获取当前语言的代码
            code_dict = multilang_map[operation]
            code = code_dict.get(self.current_code_language, code_dict.get("伪代码", []))
            
            self._set_pseudocode(code, highlight_line)

    # ... create_controls ...
    # (此函数保持不变)
    def create_controls(self):
        if self.is_embedded:
            self._create_standalone_controls()
        else:
            self._create_embedded_controls()

    def _create_standalone_controls(self):
        """独立运行时的控件布局 (添加删除按钮)"""
        # ... (main_frame, title_label, top_controls_container, dsl_frame ... 均保持不变)
        main_frame = Frame(self.window, bg=self.colors["bg_primary"])
        main_frame.pack(pady=(0, 8), fill=X, padx=15)
        
        title_label = Label(
            main_frame, 
            text="🎯 AVL 树操作面板", 
            bg=self.colors["bg_primary"], 
            fg=self.colors["text_light"],
            font=self.title_font
        )
        title_label.pack(pady=(0, 15))

        top_controls_container = Frame(main_frame, bg=self.colors["bg_primary"])
        top_controls_container.pack(fill=X, pady=(0, 12)) 
        
        dsl_frame = LabelFrame(
            top_controls_container,
            text="⚡ DSL 命令",
            bg=self.colors["bg_secondary"],
            fg=self.colors["text_light"],
            font=self.label_font,
            padx=12,
            pady=12
        )
        dsl_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 6)) 

        dsl_row1 = Frame(dsl_frame, bg=self.colors["bg_secondary"])
        dsl_row1.pack(fill=X, pady=(0, 8))

        Label(
            dsl_row1, 
            text="DSL命令:", 
            bg=self.colors["bg_secondary"], 
            fg=self.colors["text_light"],
            font=self.label_font
        ).pack(side=LEFT, padx=6)
        
        self.dsl_var = StringVar()
        dsl_entry = Entry(
            dsl_row1, 
            textvariable=self.dsl_var, 
            width=35,
            font=self.label_font,
            bd=2,
            relief=GROOVE
        )
        dsl_entry.pack(side=LEFT, padx=6, fill=X, expand=True)
        dsl_entry.bind('<Return>', self.execute_dsl_command)
        
        dsl_row2 = Frame(dsl_frame, bg=self.colors["bg_secondary"])
        dsl_row2.pack(fill=X, pady=(8, 0))
        
        self.create_button(
            dsl_row2, 
            "🚀 执行DSL", 
            self.colors["accent_purple"],
            self.execute_dsl_command
        ).pack(side=LEFT, padx=6, pady=4)
        
        self.create_button(
            dsl_row2, 
            "❓ DSL帮助", 
            "#673AB7",
            self.show_dsl_help
        ).pack(side=LEFT, padx=6, pady=4)

        # 2. 插入/删除操作框架 (原插入框架)
        insert_frame = LabelFrame(
            top_controls_container,
            text="📥 插入 / 删除 节点", # <--- 修改标题
            bg=self.colors["bg_secondary"],
            fg=self.colors["text_light"],
            font=self.label_font,
            padx=12,
            pady=12
        )
        insert_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=(6, 0)) 

        input_row1 = Frame(insert_frame, bg=self.colors["bg_secondary"])
        input_row1.pack(fill=X, pady=(0, 8))

        Label(
            input_row1, 
            text="输入数字（逗号分隔）:", 
            bg=self.colors["bg_secondary"], 
            fg=self.colors["text_light"],
            font=self.label_font
        ).pack(side=LEFT, padx=6)
        
        entry = Entry(
            input_row1, 
            textvariable=self.input_var, 
            width=25,
            font=self.label_font,
            bd=2,
            relief=GROOVE
        )
        entry.pack(side=LEFT, padx=6, fill=X, expand=True)
        entry.insert(0, "30, 20, 10, 25, 28, 27, 50, 40, 45")
        
        input_row2 = Frame(insert_frame, bg=self.colors["bg_secondary"])
        input_row2.pack(fill=X, pady=(8, 0))
        
        self.create_button(
            input_row2, 
            "✨ Insert (动画)", 
            self.colors["accent_green"],
            self.start_insert_animated
        ).pack(side=LEFT, padx=4, pady=4)
        
        # --- 新增删除按钮 ---
        self.create_button(
            input_row2, 
            "❌ Delete (动画)", 
            self.colors["accent_red"],
            self.start_delete_animated
        ).pack(side=LEFT, padx=4, pady=4)
        
        # --- 新增查找按钮 ---
        self.create_button(
            input_row2, 
            "🔍 Search (动画)", 
            self.colors["accent_blue"],
            self.start_search_animated
        ).pack(side=LEFT, padx=4, pady=4)
        
        self.create_button(
            input_row2, 
            "🗑️ 清空", 
            self.colors["accent_orange"],
            self.clear_canvas
        ).pack(side=LEFT, padx=4, pady=4)

        # ... (file_frame, status_frame ... 均保持不变)
        file_frame = LabelFrame(
            main_frame,
            text="💾 文件操作",
            bg=self.colors["bg_secondary"],
            fg=self.colors["text_light"],
            font=self.label_font,
            padx=12,
            pady=12
        )
        file_frame.pack(fill=X, pady=(0, 12))

        file_buttons = Frame(file_frame, bg=self.colors["bg_secondary"])
        file_buttons.pack(fill=X)
        
        self.create_button(
            file_buttons, 
            "💾 保存", 
            self.colors["accent_blue"],
            self.save_structure
        ).pack(side=LEFT, padx=6, pady=6)
        
        self.create_button(
            file_buttons, 
            "📂 打开", 
            self.colors["accent_blue"],
            self.load_structure
        ).pack(side=LEFT, padx=6, pady=6)
        
        self.create_button(
            file_buttons, 
            "🏠 返回主界面", 
            "#6A5ACD",
            self.back_to_main
        ).pack(side=LEFT, padx=6, pady=6)

        self.status_frame = Frame(self.window, bg=self.colors["bg_secondary"], height=30)
        self.status_frame.pack(fill=X, side=BOTTOM, pady=(5, 0))
        self.status_frame.pack_propagate(False)
        
        self.status_label = Label(
            self.status_frame,
            text="就绪",
            bg=self.colors["bg_secondary"],
            fg=self.colors["text_light"],
            font=self.status_font
        )
        self.status_label.pack(side=LEFT, padx=12, pady=6)


    def _create_embedded_controls(self):
        """嵌入到主程序时的紧凑控件布局 (添加删除按钮)"""
        control_frame = Frame(self.window, bg=self.colors["bg_primary"])
        # (保持4列不变)
        control_frame.grid(row=1, column=0, columnspan=4, sticky="ew", padx=10, pady=5)
        
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_columnconfigure(1, weight=1)
        self.window.grid_columnconfigure(2, weight=1)
        self.window.grid_columnconfigure(3, weight=1)
        
        # 第一行：插入操作
        insert_label = Label(
            control_frame, 
            text="插入/删除:", # <--- 修改
            bg=self.colors["bg_primary"], 
            fg=self.colors["text_light"],
            font=self.label_font
        )
        insert_label.grid(row=0, column=0, padx=(0, 5), pady=2, sticky="w")
        
        entry = Entry(
            control_frame, 
            textvariable=self.input_var, 
            width=20, 
            font=self.label_font,
            bd=2,
            relief=GROOVE
        )
        # (让输入框跨越2列，为按钮腾出空间)
        entry.grid(row=0, column=1, columnspan=2, padx=5, pady=2, sticky="ew") 
        entry.insert(0, "30, 20, 40, 10, 25, 35, 50")
        
        self.create_button(
            control_frame, 
            "✨ Insert", 
            self.colors["accent_green"],
            self.start_insert_animated
        ).grid(row=0, column=3, padx=5, pady=2) # <--- 移动到第4列
        
        # 第二行：操作按钮
        self.create_button(
            control_frame, 
            "❌ Delete", # <--- 新增
            self.colors["accent_red"],
            self.start_delete_animated
        ).grid(row=1, column=0, padx=5, pady=2)
        
        # 新增查找按钮
        self.create_button(
            control_frame, 
            "🔍 Search",
            self.colors["accent_blue"],
            self.start_search_animated
        ).grid(row=1, column=1, padx=5, pady=2)
        
        self.create_button(
            control_frame, 
            "🗑️ 清空", 
            self.colors["accent_orange"],
            self.clear_canvas
        ).grid(row=1, column=2, padx=5, pady=2)
        
        self.create_button(
            control_frame, 
            "💾 保存", 
            "#607D8B",
            self.save_structure
        ).grid(row=1, column=3, padx=5, pady=2)
        
        # 第三行：DSL命令
        dsl_label = Label(
            control_frame, 
            text="DSL:", 
            bg=self.colors["bg_primary"], 
            fg=self.colors["text_light"],
            font=self.label_font
        )
        dsl_label.grid(row=2, column=1, padx=(0, 5), pady=2, sticky="w")
        
        self.dsl_var = StringVar()
        dsl_entry = Entry(
            control_frame, 
            textvariable=self.dsl_var, 
            width=25, 
            font=self.label_font,
            bd=2,
            relief=GROOVE
        )
        dsl_entry.grid(row=2, column=2, padx=5, pady=2, sticky="ew")
        
        self.create_button(
            control_frame, 
            "🚀 执行", 
            self.colors["accent_purple"],
            self.execute_dsl_command
        ).grid(row=2, column=3, padx=5, pady=2)
        
        # 第四行：帮助和状态
        self.create_button(
            control_frame, 
            "❓ 帮助", 
            "#673AB7",
            self.show_dsl_help
        ).grid(row=3, column=0, padx=5, pady=2)
        
        # 状态标签
        self.status_label = Label(
            control_frame,
            text="就绪",
            bg=self.colors["bg_primary"],
            fg=self.colors["text_light"],
            font=self.status_font
        )
        self.status_label.grid(row=3, column=1, columnspan=3, padx=5, pady=2, sticky="w")

    # ... create_button, execute_dsl_command, show_dsl_help, draw_instructions, update_status, _draw_connection, compute_positions_for_root, draw_tree_from_root ...
    # (这些函数保持不变)

    # (保持不变)
    def create_button(self, parent, text, color, command):
        if self.is_embedded:
            return Button(
                parent,
                text=text,
                bg=color,
                fg=self.colors["text_light"],
                font=("Segoe UI", 9, "bold"),
                command=command,
                bd=0,
                relief=RAISED,
                padx=12,
                pady=4,
                cursor="hand2"
            )
        else:
            return Button(
                parent,
                text=text,
                bg=color,
                fg=self.colors["text_light"],
                font=self.button_font,
                command=command,
                bd=0,
                relief=RAISED,
                padx=15,
                pady=8,
                cursor="hand2"
            )
    # (保持不变)
    def execute_dsl_command(self, event=None):
        dsl_text = self.dsl_var.get().strip()
        if not dsl_text:
            return
        try:
            from DSL_utils import process_command 
            success = process_command(self, dsl_text) 
            if success:
                self.dsl_var.set("")
                self.update_status("✅ DSL命令执行成功")
        except Exception as e:
            messagebox.showerror("❌ DSL错误", f"执行DSL命令时出错: {str(e)}")
    # (保持不变)
    def show_dsl_help(self):
        try:
            from DSL_utils import avl_dsl
            avl_dsl._show_help()
        except ImportError:
             messagebox.showerror("❌ 导入错误", "无法加载 AVL DSL 帮助。\n请确保 'DSL_utils' 包已正确安装。")
    # (保持不变)
    def draw_instructions(self):
        self.canvas.delete("all")
        self.node_vis.clear()
        
        title_text = "🌳 AVL 树可视化系统 - 插入/删除演示：展示搜索路径并精确动画显示旋转" # <--- 更新标题
        self.canvas.create_text(
            self.canvas_w/2, 20, 
            text=title_text, 
            font=("Segoe UI", 12, "bold"), 
            fill=self.colors["text_dark"]
        )
        
        self.status_id = self.canvas.create_text(
            self.canvas_w - 15, 20, 
            anchor="ne", 
            text="", 
            font=self.status_font, 
            fill=self.colors["accent_green"]
        )
    # (保持不变)
    def update_status(self, txt: str):
        if hasattr(self, 'status_label'):
            self.status_label.config(text=txt)
        
        if self.status_id:
            try:
                self.canvas.itemconfig(self.status_id, text=txt)
            except TclError:
                self.status_id = None # 重置
        
        if not self.status_id:
             try:
                self.status_id = self.canvas.create_text(
                    self.canvas_w - 15, 20, 
                    anchor="ne", 
                    text=txt, 
                    font=self.status_font, 
                    fill=self.colors["accent_green"]
                )
             except TclError:
                 pass
    # (保持不变)
    def _draw_connection(self, cx, cy, tx, ty):
        top = cy + self.node_h/2
        bot = ty - self.node_h/2
        midy = (top + bot) / 2
        l1 = self.canvas.create_line(cx, top, cx, midy, width=2.5, fill=self.colors["edge_color"])
        l2 = self.canvas.create_line(cx, midy, tx, bot, arrow=LAST, width=2.5, fill=self.colors["edge_color"])
        return (l1, l2)
    # (保持不变)
    def compute_positions_for_root(self, root: Optional[AVLNode]) -> Dict[str, Tuple[float, float]]:
        res: Dict[str, Tuple[float,float]] = {}
        if not root:
            return res
        inorder_nodes: List[AVLNode] = []
        depths: Dict[AVLNode, int] = {}
        def inorder(n: Optional[AVLNode], d: int):
            if not n:
                return
            inorder(n.left, d+1)
            inorder_nodes.append(n)
            depths[n] = d
            inorder(n.right, d+1)
        inorder(root, 0)
        n = len(inorder_nodes)
        if n == 0:
            return res
        width = max(200, self.canvas_w - 2*self.margin_x)
        counts: Dict[str,int] = {}
        for i, node in enumerate(inorder_nodes):
            base = str(node.val)
            cnt = counts.get(base, 0)
            counts[base] = cnt + 1
            key = f"{base}#{cnt}" if cnt > 0 else base
            if n == 1:
                x = self.canvas_w/2
            else:
                x = self.margin_x + i * (width / (n-1))
            y = 60 + depths[node] * self.level_gap
            res[key] = (x, y)
        return res
    # (保持不变)
    def draw_tree_from_root(self, root: Optional[AVLNode]):
        self.canvas.delete("all")
        self.draw_instructions()
        if root is None:
            self.canvas.create_text(
                self.canvas_w/2, self.canvas_h/2, 
                text="🌲 空树", 
                font=("Segoe UI", 20), 
                fill="#888888"
            )
            return
        pos = self.compute_positions_for_root(root)
        inorder_nodes: List[AVLNode] = []
        def inorder_collect(n: Optional[AVLNode]):
            if not n:
                return
            inorder_collect(n.left)
            inorder_nodes.append(n)
            inorder_collect(n.right)
        inorder_collect(root)
        node_to_key: Dict[AVLNode, str] = {}
        counts: Dict[str,int] = {}
        for node in inorder_nodes:
            base = str(node.val)
            cnt = counts.get(base, 0)
            counts[base] = cnt + 1
            key = f"{base}#{cnt}" if cnt > 0 else base
            node_to_key[node] = key
        self.node_vis.clear()
        for node, key in node_to_key.items():
            cx, cy = pos[key]
            left, top, right, bottom = cx - self.node_w/2, cy - self.node_h/2, cx + self.node_w/2, cy + self.node_h/2
            rect = self.canvas.create_rectangle(
                left, top, right, bottom, 
                fill=self.colors["node_normal"], 
                outline=self.colors["accent_blue"], 
                width=2,
                stipple="gray50"
            )
            x1, x2 = left + 28, left + 92
            self.canvas.create_line(x1, top, x1, bottom, width=1, fill="#BBDEFB")
            self.canvas.create_line(x2, top, x2, bottom, width=1, fill="#BBDEFB")
            txt = self.canvas.create_text(
                (x1+x2)/2, cy, 
                text=str(node.val), 
                font=("Segoe UI", 12, "bold"),
                fill=self.colors["text_dark"]
            )
            self.node_vis[key] = {
                'rect': rect, 
                'text': txt, 
                'cx': cx, 
                'cy': cy, 
                'val': str(node.val),
                'edges': {}
            }
        def setup_edges(n: Optional[AVLNode]):
            if not n:
                return
            parent_key = node_to_key[n]
            parent_cx, parent_cy = pos[parent_key]
            if n.left:
                child_key = node_to_key[n.left]
                child_cx, child_cy = pos[child_key]
                line_ids = self._draw_connection(parent_cx, parent_cy, child_cx, child_cy)
                self.node_vis[parent_key]['edges'][child_key] = line_ids
                setup_edges(n.left)
            if n.right:
                child_key = node_to_key[n.right]
                child_cx, child_cy = pos[child_key]
                line_ids = self._draw_connection(parent_cx, parent_cy, child_cx, child_cy)
                self.node_vis[parent_key]['edges'][child_key] = line_ids
                setup_edges(n.right)
        setup_edges(root)

    # ---------- 插入动画流程 (增加伪代码高亮) ----------
    def start_insert_animated(self):
        if self.animating:
            self.update_status("⚠️ 正在执行动画，请稍候...")
            return
        s = self.input_var.get().strip()
        if not s:
            messagebox.showinfo("💡 提示", "请输入数字，例如：1,2,3")
            return
        batch = [p.strip() for p in s.split(",") if p.strip()!=""]
        if not batch:
            return
        self.batch = batch
        self.animating = True
        self.update_status("🎬 开始插入动画...")
        # 显示插入伪代码
        self._show_pseudocode_for_operation('insert', 0)
        self._insert_seq(0)

    def _insert_seq(self, idx: int):
        if idx >= len(self.batch):
            self.animating = False
            self.update_status("✅ 所有插入完成")
            self._show_initial_code_hint()  # 恢复初始提示
            return
        val = self.batch[idx]
        inserted_node, path_nodes, rotations, snapshots = self.model.insert_with_steps(val)
        snap_pre = snapshots[0]
        snap_after_insert = snapshots[1] if len(snapshots) > 1 else None
        pos_pre = self.compute_positions_for_root(snap_pre)
        val_to_keys_pre: Dict[str, List[str]] = {}
        for k in pos_pre.keys():
            base = k.split('#')[0]
            val_to_keys_pre.setdefault(base, []).append(k)

        # 检查是否是空树插入
        is_empty_tree = snap_pre is None

        def highlight_path(i=0):
            if i >= len(path_nodes):
                # 路径搜索完成，准备插入
                self.update_status(f"📥 插入 {val}: 开始落位")
                if is_empty_tree:
                    # 空树插入：高亮第2-3行
                    self._show_pseudocode_for_operation('insert', 2)
                else:
                    # 非空树：高亮插入新节点的行
                    self._show_pseudocode_for_operation('insert', 7)  # node.left = new Node(val)
                self.animate_flyin_new(val, snap_after_insert, lambda: self._after_insert_rotations(rotations, snapshots, idx))
                return
            
            node = path_nodes[i]
            v = str(node.val)
            keylist = val_to_keys_pre.get(v, [])
            if keylist:
                key = keylist.pop(0)
                self.draw_tree_from_root(snap_pre)
                try:
                    self.canvas.itemconfig(self.node_vis[key]['rect'], fill=self.colors["node_highlight"])
                except Exception:
                    pass
            else:
                self.draw_tree_from_root(snap_pre)
            
            # 高亮伪代码中的搜索步骤
            if i == len(path_nodes) - 1:
                # 最后一个节点（新节点将被插入的位置）
                self._show_pseudocode_for_operation('insert', 7)  # 插入位置
            else:
                # 搜索过程中
                self._show_pseudocode_for_operation('insert', 5)  # while循环
            
            self.update_status(f"🔍 搜索路径: 访问 {v} (步骤 {i+1}/{len(path_nodes)})")
            self.window.after(420, lambda: highlight_path(i+1))

        highlight_path(0)
    
    # (保持不变)
    def animate_flyin_new(self, val_str: str, snap_after_insert: Optional[AVLNode], on_complete):
        if not snap_after_insert:
            on_complete(); return
        pos_after = self.compute_positions_for_root(snap_after_insert)
        candidate_keys = [k for k in pos_after.keys() if k.split('#')[0] == str(val_str)]
        if not candidate_keys:
            on_complete(); return
        target_key = candidate_keys[-1]
        tx, ty = pos_after[target_key]
        sx, sy = self.canvas_w/2, 20
        left, top, right, bottom = sx - self.node_w/2, sy - self.node_h/2, sx + self.node_w/2, sy + self.node_h/2
        temp_rect = self.canvas.create_rectangle(
            left, top, right, bottom, 
            fill=self.colors["node_new"], 
            outline=self.colors["accent_green"], 
            width=2
        )
        temp_text = self.canvas.create_text(sx, sy, text=str(val_str), font=("Segoe UI", 12, "bold"))
        steps = 30
        dx = (tx - sx)/steps
        dy = (ty - sy)/steps
        delay = 12
        def step(i=0):
            if i < steps:
                try:
                    self.canvas.move(temp_rect, dx, dy)
                    self.canvas.move(temp_text, dx, dy)
                except Exception:
                    pass
                self.window.after(delay, lambda: step(i+1))
            else:
                try:
                    self.canvas.delete(temp_rect)
                    self.canvas.delete(temp_text)
                except Exception:
                    pass
                self.draw_tree_from_root(snap_after_insert)
                try:
                    self.canvas.itemconfig(self.node_vis[target_key]['rect'], fill=self.colors["node_new"])
                except Exception:
                    pass
                self.window.after(300, on_complete)
        step()

    # (增加伪代码高亮)
    def _after_insert_rotations(self, rotations, snapshots, insertion_idx):
        if not rotations:
            # 无需旋转，高亮rebalance结束
            self._show_pseudocode_for_operation('rebalance', 16)  # node = node.parent (结束)
            self.draw_tree_from_root(clone_tree(self.model.root))
            self.window.after(300, lambda: self._insert_seq(insertion_idx+1))
            return
        
        # 显示平衡检查伪代码
        self._show_pseudocode_for_operation('rebalance', 0)
        
        def done_all():
            self.draw_tree_from_root(clone_tree(self.model.root))
            self.window.after(300, lambda: self._insert_seq(insertion_idx+1))
        self._animate_rotations_sequence(rotations, snapshots, insertion_idx, done_all, is_insert=True)

    # ---------- 删除动画流程 (增加伪代码高亮) ----------
    
    def start_delete_animated(self):
        """启动删除动画"""
        if self.animating:
            self.update_status("⚠️ 正在执行动画，请稍候...")
            return
            
        s = self.input_var.get().strip()
        if not s:
            messagebox.showinfo("💡 提示", "请输入要删除的数字，例如：1,2,3")
            return
            
        batch = [p.strip() for p in s.split(",") if p.strip()!=""]
        if not batch:
            return
            
        self.batch = batch
        self.animating = True
        self.update_status("🎬 开始删除动画...")
        # 显示删除伪代码
        self._show_pseudocode_for_operation('delete', 0)
        self._delete_seq(0)

    def _delete_seq(self, idx: int):
        """按顺序执行删除动画"""
        if idx >= len(self.batch):
            self.animating = False
            self.update_status("✅ 所有删除完成")
            self._show_initial_code_hint()  # 恢复初始提示
            return

        val = self.batch[idx]
        # 调用 model 的 delete_with_steps
        deleted_node, path_nodes, rotations, snapshots = self.model.delete_with_steps(val)

        snap_pre = snapshots[0]
        # snap_after_delete 是删除后、旋转前的快照
        snap_after_delete = snapshots[1] if len(snapshots) > 1 else None

        pos_pre = self.compute_positions_for_root(snap_pre)
        val_to_keys_pre: Dict[str, List[str]] = {}
        for k in pos_pre.keys():
            base = k.split('#')[0]
            val_to_keys_pre.setdefault(base, []).append(k)

        def highlight_path_for_delete(i=0):
            if i >= len(path_nodes):
                # 路径高亮完成
                if deleted_node is None:
                    # --- 未找到节点 ---
                    self.update_status(f"❌ 未找到 {val}")
                    self._show_pseudocode_for_operation('delete', 3)  # return // 未找到
                    self.draw_tree_from_root(snap_pre)
                    self.window.after(600, lambda: self._delete_seq(idx + 1))
                else:
                    # --- 找到节点，执行删除 ---
                    self.update_status(f"❌ 找到 {val}: 正在移除...")
                    self._show_pseudocode_for_operation('delete', 10)  # REPLACE(node, child)
                    self.animate_show_deletion(
                        val, 
                        snap_after_delete, 
                        lambda: self._after_delete_rotations(rotations, snapshots, idx)
                    )
                return
            
            # 高亮逻辑
            node = path_nodes[i]
            v = str(node.val)
            keylist = val_to_keys_pre.get(v, [])
            if keylist:
                key = keylist.pop(0)
                self.draw_tree_from_root(snap_pre)
                try:
                    self.canvas.itemconfig(self.node_vis[key]['rect'], fill=self.colors["node_highlight"])
                except Exception:
                    pass
            else:
                self.draw_tree_from_root(snap_pre)
            
            # 高亮伪代码中的搜索步骤
            self._show_pseudocode_for_operation('delete', 1)  # node = SEARCH(...)
            
            self.update_status(f"🔍 搜索 {val}: 访问 {v} (步骤 {i+1}/{len(path_nodes)})")
            self.window.after(420, lambda: highlight_path_for_delete(i+1))

        highlight_path_for_delete(0)

    def animate_show_deletion(self, val_str: str, snap_after_delete: Optional[AVLNode], on_complete):
        """
        "删除" 动画：显示删除后、旋转前的状态
        """
        # 直接绘制删除/交换后的快照
        self.draw_tree_from_root(snap_after_delete)
        
        self.update_status(f"✅ {val_str} 已移除 (或值已交换). 准备旋转...")
        
        # 暂停一段时间让用户看到结果
        self.window.after(800, on_complete)

    def _after_delete_rotations(self, rotations, snapshots, deletion_idx):
        """处理删除后的旋转序列"""
        if not rotations:
            # 没有旋转
            self._show_pseudocode_for_operation('rebalance', 16)  # 结束
            self.draw_tree_from_root(clone_tree(self.model.root))
            self.window.after(300, lambda: self._delete_seq(deletion_idx+1))
            return

        # 显示平衡检查伪代码
        self._show_pseudocode_for_operation('rebalance', 0)

        def done_all():
            # 所有旋转完成
            self.draw_tree_from_root(clone_tree(self.model.root))
            self.window.after(300, lambda: self._delete_seq(deletion_idx+1))
            
        # 使用通用的旋转动画序列
        self._animate_rotations_sequence(rotations, snapshots, deletion_idx, done_all, is_insert=False)


    # ---------- 查找动画流程 ----------
    
    def start_search_animated(self):
        """启动查找动画"""
        if self.animating:
            self.update_status("⚠️ 正在执行动画，请稍候...")
            return
            
        s = self.input_var.get().strip()
        if not s:
            messagebox.showinfo("💡 提示", "请输入要查找的数字，例如：1,2,3")
            return
            
        batch = [p.strip() for p in s.split(",") if p.strip()!=""]
        if not batch:
            return
            
        self.batch = batch
        self.animating = True
        self.update_status("🎬 开始查找动画...")
        # 显示查找伪代码
        self._show_pseudocode_for_operation('search', 0)
        self._search_seq(0)

    def _search_seq(self, idx: int):
        """按顺序执行查找动画"""
        if idx >= len(self.batch):
            self.animating = False
            self.update_status("✅ 所有查找完成")
            self._show_initial_code_hint()  # 恢复初始提示
            return

        val = self.batch[idx]
        # 调用 model 的 search_with_steps
        found_node, path_nodes, found = self.model.search_with_steps(val)
        
        # 获取当前树的快照用于可视化
        snap = clone_tree(self.model.root)
        pos = self.compute_positions_for_root(snap)
        
        val_to_keys: Dict[str, List[str]] = {}
        for k in pos.keys():
            base = k.split('#')[0]
            val_to_keys.setdefault(base, []).append(k)

        def highlight_path_for_search(i=0):
            if i >= len(path_nodes):
                # 路径高亮完成
                if found:
                    # --- 找到节点 ---
                    self.update_status(f"✅ 找到 {val}")
                    self._show_pseudocode_for_operation('search', 3)  # return node // 找到
                    # 高亮找到的节点为绿色
                    self.draw_tree_from_root(snap)
                    v = str(found_node.val)
                    keylist = val_to_keys.get(v, [])
                    if keylist:
                        key = keylist[0]  # 使用第一个匹配的key
                        try:
                            self.canvas.itemconfig(self.node_vis[key]['rect'], 
                                                 fill=self.colors["node_new"],
                                                 outline=self.colors["accent_green"],
                                                 width=3)
                        except Exception:
                            pass
                else:
                    # --- 未找到节点 ---
                    self.update_status(f"❌ 未找到 {val}")
                    self._show_pseudocode_for_operation('search', 10)  # return null // 未找到
                    self.draw_tree_from_root(snap)
                
                # 延迟后进行下一个查找
                self.window.after(1000, lambda: self._search_seq(idx + 1))
                return
            
            # 高亮当前访问的节点
            node = path_nodes[i]
            v = str(node.val)
            keylist = val_to_keys.get(v, [])
            
            self.draw_tree_from_root(snap)
            
            if keylist:
                key = keylist.pop(0)
                try:
                    self.canvas.itemconfig(self.node_vis[key]['rect'], 
                                         fill=self.colors["node_highlight"],
                                         outline=self.colors["accent_orange"],
                                         width=3)
                except Exception:
                    pass
            
            # 高亮伪代码中的搜索步骤
            if i == len(path_nodes) - 1 and found:
                # 最后一个节点且找到了
                self._show_pseudocode_for_operation('search', 2)  # if val == node.val
            else:
                # 搜索过程中
                self._show_pseudocode_for_operation('search', 1)  # while循环
            
            self.update_status(f"🔍 查找 {val}: 访问 {v} (步骤 {i+1}/{len(path_nodes)})")
            self.window.after(500, lambda: highlight_path_for_search(i+1))

        highlight_path_for_search(0)

    # ---------- 通用动画 (保持不变) ----------
    
    # (保持不变)
    def _redraw_all_edges_during_animation(self):
        for parent_key, parent_vis in self.node_vis.items():
            try:
                parent_coords = self.canvas.coords(parent_vis['rect'])
                if not parent_coords or len(parent_coords) < 4: continue
                parent_cx = (parent_coords[0] + parent_coords[2]) / 2
                parent_cy = (parent_coords[1] + parent_coords[3]) / 2
                for child_key, line_ids in parent_vis.get('edges', {}).items():
                    child_vis = self.node_vis.get(child_key)
                    if not child_vis: continue
                    child_coords = self.canvas.coords(child_vis['rect'])
                    if not child_coords or len(child_coords) < 4: continue
                    child_cx = (child_coords[0] + child_coords[2]) / 2
                    child_cy = (child_coords[1] + child_coords[3]) / 2
                    l1_id, l2_id = line_ids
                    top = parent_cy + self.node_h / 2
                    bot = child_cy - self.node_h / 2
                    midy = (top + bot) / 2
                    self.canvas.coords(l1_id, parent_cx, top, parent_cx, midy)
                    self.canvas.coords(l2_id, parent_cx, midy, child_cx, bot)
            except TclError:
                continue

    # (增加伪代码高亮)
    def _animate_single_rotation(self, before_root: Optional[AVLNode], after_root: Optional[AVLNode], rotation_info: Dict, on_done):
        pos_before = self.compute_positions_for_root(before_root)
        pos_after = self.compute_positions_for_root(after_root)
        self.draw_tree_from_root(before_root)
        keys_common = set(pos_before.keys()) & set(pos_after.keys())
        moves = []
        for k in keys_common:
            item = self.node_vis.get(k)
            if not item:
                continue
            sx, sy = pos_before[k]
            tx, ty = pos_after[k]
            moves.append((k, item['rect'], item['text'], sx, sy, tx, ty))
        rtype = rotation_info.get('type', '')
        label_text = f"🔄 旋转: {rtype}"
        
        # 显示对应旋转类型的伪代码
        self._show_pseudocode_for_operation(rtype, 0)
        
        z = rotation_info.get('z'); y = rotation_info.get('y')
        zkey = None; ykey = None
        if z:
            zkey = next((k for k in pos_before.keys() if k.split('#')[0]==str(z.val)), None)
        if y:
            ykey = next((k for k in pos_before.keys() if k.split('#')[0]==str(y.val)), None)
        arc_id = None; label_id = None
        if zkey and ykey:
            zx, zy = pos_before[zkey]; yx, yy = pos_before[ykey]
            midx = (zx + yx)/2
            topy = min(zy, yy) - 30
            try:
                arc_id = self.canvas.create_arc(
                    midx-30, topy-20, midx+30, topy+20, 
                    start=0, extent=180, style=ARC, width=3, 
                    outline=self.colors["accent_red"]
                )
                label_id = self.canvas.create_text(
                    midx, topy-28, 
                    text=label_text, 
                    font=("Segoe UI", 11, "bold"), 
                    fill=self.colors["accent_red"]
                )
            except Exception:
                arc_id = None; label_id = None
        frames = 30
        delay = 20
        
        # 计算伪代码高亮步骤
        total_code_lines = len(self.current_pseudocode)
        
        def rect_center_coords(rect_id):
            try:
                coords = self.canvas.coords(rect_id)
                if not coords or len(coords) < 4:
                    return (0,0)
                x1,y1,x2,y2 = coords
                return ((x1+x2)/2, (y1+y2)/2)
            except TclError:
                return (0,0)
        
        def frame_step(f=0):
            if f >= frames:
                self.draw_tree_from_root(after_root)
                # 高亮最后一行（return）
                self._highlight_line(total_code_lines - 1)
                if arc_id:
                    try: self.canvas.delete(arc_id)
                    except: pass
                if label_id:
                    try: self.canvas.delete(label_id)
                    except: pass
                self.window.after(300, on_done)
                return
            
            t = (f+1)/frames
            
            # 根据动画进度高亮不同的伪代码行
            if total_code_lines > 2:
                # 跳过第一行（函数名）和最后一行（return）
                progress_line = 1 + int(t * (total_code_lines - 2))
                progress_line = min(progress_line, total_code_lines - 2)
                self._highlight_line(progress_line)
            
            for (k, rect_id, text_id, sx, sy, tx, ty) in moves:
                cur_cx = sx + (tx - sx) * t
                cur_cy = sy + (ty - sy) * t
                try:
                    ccx, ccy = rect_center_coords(rect_id)
                    if (ccx, ccy) == (0,0): continue
                    dx = cur_cx - ccx
                    dy = cur_cy - ccy
                    self.canvas.move(rect_id, dx, dy)
                    self.canvas.move(text_id, dx, dy)
                except Exception:
                    pass
            self._redraw_all_edges_during_animation()
            self.window.after(delay, lambda: frame_step(f+1))
        frame_step(0)

    # (增加伪代码高亮)
    def _animate_rotations_sequence(self, rotations: List[Dict], snapshots: List[Optional[AVLNode]], operation_index: int, on_all_done, is_insert: bool = True):
        """通用旋转动画序列，适用于插入和删除"""
        if not rotations:
            on_all_done(); return
        
        def step(i=0):
            if i >= len(rotations):
                # 所有旋转完成，显示rebalance的最后一步
                self._show_pseudocode_for_operation('rebalance', 16)
                on_all_done()
                return
            # 快照索引从 1 开始 (snap[0] = 插入前, snap[1] = 插入后/删除后)
            # snap[1] 是第一次旋转的 "before"
            # snap[2] 是第一次旋转的 "after"
            before_root = snapshots[1 + i] 
            after_root = snapshots[2 + i]
            rot_info = rotations[i]
            
            # 先显示rebalance伪代码，高亮对应的旋转类型行
            rtype = rot_info.get('type', '')
            if rtype == 'LL':
                self._show_pseudocode_for_operation('rebalance', 6)  # LL旋转行
            elif rtype == 'LR':
                self._show_pseudocode_for_operation('rebalance', 8)  # LR旋转行
            elif rtype == 'RR':
                self._show_pseudocode_for_operation('rebalance', 12)  # RR旋转行
            elif rtype == 'RL':
                self._show_pseudocode_for_operation('rebalance', 14)  # RL旋转行
            
            self.update_status(f"🔄 执行旋转 {i+1}/{len(rotations)}: {rtype}")
            
            # 延迟后开始实际的旋转动画（让用户先看到rebalance中的高亮）
            self.window.after(500, lambda: self._animate_single_rotation(before_root, after_root, rot_info, lambda: step(i+1)))
        
        step(0)

    # ---------- 清空 和 文件操作 (保持不变) ----------
    
    def clear_canvas(self):
        if self.animating:
            self.update_status("⚠️ 正在执行动画，无法清空")
            return
        self.model = AVLModel()
        self.node_vis.clear()
        self.canvas.delete("all")
        self.draw_instructions()
        self._show_initial_code_hint()  # 重置伪代码面板
        self.update_status("🗑️ 已清空")

    # (保持不变)
    def back_to_main(self):
        if self.is_embedded:
            self.window.pack_forget()
        else:
            self.window.destroy()

    # (保持不变)
    def _ensure_avl_folder(self) -> str:
        return storage.ensure_save_subdir("avl")

    # (保持不变)
    def save_structure(self):
        root = self.model.root
        default_dir = self._ensure_avl_folder()
        default_name = f"avl_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = filedialog.asksaveasfilename(
            initialdir=default_dir,
            initialfile=default_name,
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="保存 AVL 到文件"
        )
        if not filepath: return
        ok = storage.save_tree_to_file(root, filepath)
        if ok:
            messagebox.showinfo("✅ 成功", f"AVL 已保存到：\n{filepath}")
            self.update_status("💾 保存成功")

    # (保持不变)
    def load_structure(self):
        default_dir = self._ensure_avl_folder()
        filepath = filedialog.askopenfilename(
            initialdir=default_dir,
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="从文件加载 AVL"
        )
        if not filepath: return
        tree_dict = storage.load_tree_from_file(filepath)
        from avl.avl_model import AVLNode as AVLNodeClass
        newroot = storage.tree_dict_to_nodes(tree_dict, AVLNodeClass)
        self.model.root = newroot
        self.draw_tree_from_root(clone_tree(self.model.root))
        messagebox.showinfo("✅ 成功", f"AVL 已从文件加载并恢复结构：\n{filepath}")
        self.update_status("📂 已从文件加载结构")

# (保持不变)
if __name__ == '__main__':
    w = Tk()
    app = AVLVisualizer(w)
    w.mainloop()