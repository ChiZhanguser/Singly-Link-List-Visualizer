from tkinter import *
from tkinter import ttk
from tkinter import messagebox, filedialog
from typing import Dict, Tuple, List, Optional
from rbt.rbt_model import RBModel, RBNode, clone_tree
import storage as storage
from DSL_utils import process_command 
import time

# ========== 多语言伪代码定义 ==========

# 语言选项
LANG_PSEUDOCODE = "伪代码"
LANG_C = "C语言"
LANG_JAVA = "Java"
LANG_PYTHON = "Python"
CODE_LANGUAGES = [LANG_PSEUDOCODE, LANG_C, LANG_JAVA, LANG_PYTHON]

# 红黑树插入 - 多语言
MULTILANG_RB_INSERT = {
    "伪代码": [
    "RB-INSERT(T, val):",
        "  z ← new Node(val)",
        "  z.color ← RED",
    "  // 找到插入位置",
        "  y ← null",
        "  x ← T.root",
        "  while x ≠ null do",
        "    y ← x",
        "    if z.val < x.val then",
        "      x ← x.left",
        "    else",
        "      x ← x.right",
        "    end if",
        "  end while",
        "  z.parent ← y",
        "  if y = null then",
        "    T.root ← z  // 树为空",
        "  else if z.val < y.val then",
        "    y.left ← z",
        "  else",
        "    y.right ← z",
        "  end if",
        "  // 修复红黑性质",
        "  RB-INSERT-FIXUP(T, z)",
    ],
    "C语言": [
        "void rb_insert(RBTree* T, int val) {",
        "  Node* z = create_node(val);",
        "  z->color = RED;",
        "  // 找到插入位置",
        "  Node* y = NULL;",
        "  Node* x = T->root;",
        "  while (x != NULL) {",
        "    y = x;",
        "    if (z->val < x->val) {",
        "      x = x->left;",
        "    } else {",
        "      x = x->right;",
        "    }",
        "  }",
        "  z->parent = y;",
        "  if (y == NULL) {",
        "    T->root = z; // 树为空",
        "  } else if (z->val < y->val) {",
        "    y->left = z;",
        "  } else {",
        "    y->right = z;",
        "  }",
        "  // 修复红黑性质",
        "  rb_insert_fixup(T, z);",
        "}",
    ],
    "Java": [
        "void rbInsert(RBTree T, int val) {",
        "  Node z = new Node(val);",
        "  z.color = RED;",
        "  // 找到插入位置",
        "  Node y = null;",
        "  Node x = T.root;",
        "  while (x != null) {",
        "    y = x;",
        "    if (z.val < x.val) {",
        "      x = x.left;",
        "    } else {",
        "      x = x.right;",
        "    }",
        "  }",
        "  z.parent = y;",
        "  if (y == null) {",
        "    T.root = z; // 树为空",
        "  } else if (z.val < y.val) {",
        "    y.left = z;",
        "  } else {",
        "    y.right = z;",
        "  }",
        "  // 修复红黑性质",
        "  rbInsertFixup(T, z);",
        "}",
    ],
    "Python": [
        "def rb_insert(T, val):",
        "  z = Node(val)",
        "  z.color = RED",
        "  # 找到插入位置",
        "  y = None",
    "  x = T.root",
        "  while x is not None:",
    "    y = x",
    "    if z.val < x.val:",
    "      x = x.left",
    "    else:",
    "      x = x.right",
        "  # endwhile",
    "  z.parent = y",
        "  if y is None:",
        "    T.root = z  # 树为空",
        "  elif z.val < y.val:",
    "    y.left = z",
    "  else:",
    "    y.right = z",
        "  # endif",
        "  # 修复红黑性质",
        "  rb_insert_fixup(T, z)",
    ]
}

# 左旋 - 多语言
MULTILANG_LEFT_ROTATE = {
    "伪代码": [
    "LEFT-ROTATE(T, x):",
        "  y ← x.right",
        "  x.right ← y.left  // 将y的左子树给x",
        "  if y.left ≠ null then",
        "    y.left.parent ← x",
        "  end if",
        "  y.parent ← x.parent",
        "  if x.parent = null then",
        "    T.root ← y",
        "  else if x = x.parent.left then",
        "    x.parent.left ← y",
        "  else",
        "    x.parent.right ← y",
        "  end if",
        "  y.left ← x",
        "  x.parent ← y",
    ],
    "C语言": [
        "void left_rotate(RBTree* T, Node* x) {",
        "  Node* y = x->right;",
        "  x->right = y->left; // 将y的左子树给x",
        "  if (y->left != NULL) {",
        "    y->left->parent = x;",
        "  }",
        "  y->parent = x->parent;",
        "  if (x->parent == NULL) {",
        "    T->root = y;",
        "  } else if (x == x->parent->left) {",
        "    x->parent->left = y;",
        "  } else {",
        "    x->parent->right = y;",
        "  }",
        "  y->left = x;",
        "  x->parent = y;",
        "}",
    ],
    "Java": [
        "void leftRotate(RBTree T, Node x) {",
        "  Node y = x.right;",
        "  x.right = y.left; // 将y的左子树给x",
        "  if (y.left != null) {",
        "    y.left.parent = x;",
        "  }",
        "  y.parent = x.parent;",
        "  if (x.parent == null) {",
        "    T.root = y;",
        "  } else if (x == x.parent.left) {",
        "    x.parent.left = y;",
        "  } else {",
        "    x.parent.right = y;",
        "  }",
        "  y.left = x;",
        "  x.parent = y;",
        "}",
    ],
    "Python": [
        "def left_rotate(T, x):",
    "  y = x.right",
        "  x.right = y.left  # 将y的左子树给x",
        "  if y.left is not None:",
    "    y.left.parent = x",
        "  # endif",
    "  y.parent = x.parent",
        "  if x.parent is None:",
    "    T.root = y",
        "  elif x == x.parent.left:",
    "    x.parent.left = y",
    "  else:",
    "    x.parent.right = y",
        "  # endif",
    "  y.left = x",
    "  x.parent = y",
]
}

# 右旋 - 多语言
MULTILANG_RIGHT_ROTATE = {
    "伪代码": [
    "RIGHT-ROTATE(T, x):",
        "  y ← x.left",
        "  x.left ← y.right  // 将y的右子树给x",
        "  if y.right ≠ null then",
        "    y.right.parent ← x",
        "  end if",
        "  y.parent ← x.parent",
        "  if x.parent = null then",
        "    T.root ← y",
        "  else if x = x.parent.right then",
        "    x.parent.right ← y",
        "  else",
        "    x.parent.left ← y",
        "  end if",
        "  y.right ← x",
        "  x.parent ← y",
    ],
    "C语言": [
        "void right_rotate(RBTree* T, Node* x) {",
        "  Node* y = x->left;",
        "  x->left = y->right; // 将y的右子树给x",
        "  if (y->right != NULL) {",
        "    y->right->parent = x;",
        "  }",
        "  y->parent = x->parent;",
        "  if (x->parent == NULL) {",
        "    T->root = y;",
        "  } else if (x == x->parent->right) {",
        "    x->parent->right = y;",
        "  } else {",
        "    x->parent->left = y;",
        "  }",
        "  y->right = x;",
        "  x->parent = y;",
        "}",
    ],
    "Java": [
        "void rightRotate(RBTree T, Node x) {",
        "  Node y = x.left;",
        "  x.left = y.right; // 将y的右子树给x",
        "  if (y.right != null) {",
        "    y.right.parent = x;",
        "  }",
        "  y.parent = x.parent;",
        "  if (x.parent == null) {",
        "    T.root = y;",
        "  } else if (x == x.parent.right) {",
        "    x.parent.right = y;",
        "  } else {",
        "    x.parent.left = y;",
        "  }",
        "  y.right = x;",
        "  x.parent = y;",
        "}",
    ],
    "Python": [
        "def right_rotate(T, x):",
    "  y = x.left",
        "  x.left = y.right  # 将y的右子树给x",
        "  if y.right is not None:",
    "    y.right.parent = x",
        "  # endif",
    "  y.parent = x.parent",
        "  if x.parent is None:",
    "    T.root = y",
        "  elif x == x.parent.right:",
    "    x.parent.right = y",
    "  else:",
    "    x.parent.left = y",
        "  # endif",
    "  y.right = x",
    "  x.parent = y",
]
}

# 插入修复 - 多语言
MULTILANG_RB_INSERT_FIXUP = {
    "伪代码": [
        "RB-INSERT-FIXUP(T, z):",
        "  while z.parent.color = RED do",
        "    if z.parent = z.parent.parent.left then",
        "      y ← z.parent.parent.right  // 叔叔",
        "      if y.color = RED then  // Case 1",
        "        z.parent.color ← BLACK",
        "        y.color ← BLACK",
        "        z.parent.parent.color ← RED",
        "        z ← z.parent.parent",
        "      else",
        "        if z = z.parent.right then  // Case 2",
        "          z ← z.parent",
        "          LEFT-ROTATE(T, z)",
        "        end if",
        "        // Case 3",
        "        z.parent.color ← BLACK",
        "        z.parent.parent.color ← RED",
        "        RIGHT-ROTATE(T, z.parent.parent)",
        "      end if",
        "    else  // 对称情况",
        "      y ← z.parent.parent.left  // 叔叔",
        "      // ... (对称操作)",
        "    end if",
        "  end while",
        "  T.root.color ← BLACK",
    ],
    "C语言": [
        "void rb_insert_fixup(RBTree* T, Node* z) {",
        "  while (z->parent->color == RED) {",
        "    if (z->parent == z->parent->parent->left) {",
        "      Node* y = z->parent->parent->right; // 叔叔",
        "      if (y->color == RED) { // Case 1",
        "        z->parent->color = BLACK;",
        "        y->color = BLACK;",
        "        z->parent->parent->color = RED;",
        "        z = z->parent->parent;",
        "      } else {",
        "        if (z == z->parent->right) { // Case 2",
        "          z = z->parent;",
        "          left_rotate(T, z);",
        "        }",
        "        // Case 3",
        "        z->parent->color = BLACK;",
        "        z->parent->parent->color = RED;",
        "        right_rotate(T, z->parent->parent);",
        "      }",
        "    } else { // 对称情况",
        "      Node* y = z->parent->parent->left; // 叔叔",
        "      // ... (对称操作)",
        "    }",
        "  }",
        "  T->root->color = BLACK;",
        "}",
    ],
    "Java": [
        "void rbInsertFixup(RBTree T, Node z) {",
        "  while (z.parent.color == RED) {",
        "    if (z.parent == z.parent.parent.left) {",
        "      Node y = z.parent.parent.right; // 叔叔",
        "      if (y.color == RED) { // Case 1",
        "        z.parent.color = BLACK;",
        "        y.color = BLACK;",
        "        z.parent.parent.color = RED;",
        "        z = z.parent.parent;",
        "      } else {",
        "        if (z == z.parent.right) { // Case 2",
        "          z = z.parent;",
        "          leftRotate(T, z);",
        "        }",
        "        // Case 3",
        "        z.parent.color = BLACK;",
        "        z.parent.parent.color = RED;",
        "        rightRotate(T, z.parent.parent);",
        "      }",
        "    } else { // 对称情况",
        "      Node y = z.parent.parent.left; // 叔叔",
        "      // ... (对称操作)",
        "    }",
        "  }",
        "  T.root.color = BLACK;",
        "}",
    ],
    "Python": [
        "def rb_insert_fixup(T, z):",
        "  while z.parent.color == RED:",
        "    if z.parent == z.parent.parent.left:",
        "      y = z.parent.parent.right  # 叔叔",
        "      if y.color == RED:  # Case 1",
        "        z.parent.color = BLACK",
        "        y.color = BLACK",
        "        z.parent.parent.color = RED",
        "        z = z.parent.parent",
        "      else:",
        "        if z == z.parent.right:  # Case 2",
        "          z = z.parent",
        "          left_rotate(T, z)",
        "        # endif",
        "        # Case 3",
        "        z.parent.color = BLACK",
        "        z.parent.parent.color = RED",
        "        right_rotate(T, z.parent.parent)",
        "      # endif",
        "    else:  # 对称情况",
        "      y = z.parent.parent.left  # 叔叔",
        "      # ... (对称操作)",
        "    # endif",
        "  # endwhile",
        "  T.root.color = BLACK",
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

# 重着色 - 多语言
MULTILANG_RECOLOR = {
    "伪代码": [
        "RECOLOR 重着色操作:",
        "  // Case 1: 叔叔是红色",
        "  // 将父节点和叔叔节点染黑",
        "  parent.color ← BLACK",
        "  uncle.color ← BLACK",
        "  // 将祖父节点染红",
        "  grandparent.color ← RED",
        "  // 继续向上检查祖父节点",
        "  z ← grandparent",
    ],
    "C语言": [
        "// RECOLOR 重着色操作",
        "// Case 1: 叔叔是红色",
        "// 将父节点和叔叔节点染黑",
        "parent->color = BLACK;",
        "uncle->color = BLACK;",
        "// 将祖父节点染红",
        "grandparent->color = RED;",
        "// 继续向上检查祖父节点",
        "z = grandparent;",
    ],
    "Java": [
        "// RECOLOR 重着色操作",
        "// Case 1: 叔叔是红色",
        "// 将父节点和叔叔节点染黑",
        "parent.color = BLACK;",
        "uncle.color = BLACK;",
        "// 将祖父节点染红",
        "grandparent.color = RED;",
        "// 继续向上检查祖父节点",
        "z = grandparent;",
    ],
    "Python": [
        "# RECOLOR 重着色操作",
        "# Case 1: 叔叔是红色",
        "# 将父节点和叔叔节点染黑",
        "parent.color = BLACK",
        "uncle.color = BLACK",
        "# 将祖父节点染红",
        "grandparent.color = RED",
        "# 继续向上检查祖父节点",
        "z = grandparent",
    ]
}

# 删除 - 多语言
MULTILANG_RB_DELETE = {
    "伪代码": [
        "RB-DELETE(T, val):",
        "  z ← SEARCH(T.root, val)",
        "  if z = null then",
        "    return  // 未找到",
        "  end if",
        "  y ← z  // 实际删除的节点",
        "  y-original-color ← y.color",
        "  if z.left = null then",
        "    x ← z.right",
        "    TRANSPLANT(T, z, z.right)",
        "  else if z.right = null then",
        "    x ← z.left",
        "    TRANSPLANT(T, z, z.left)",
        "  else  // 有两个子节点",
        "    y ← MINIMUM(z.right)",
        "    y-original-color ← y.color",
        "    x ← y.right",
        "    // 替换和重新链接",
        "  end if",
        "  if y-original-color = BLACK then",
        "    RB-DELETE-FIXUP(T, x)",
        "  end if",
    ],
    "C语言": [
        "void rb_delete(RBTree* T, int val) {",
        "  Node* z = search(T->root, val);",
        "  if (z == NULL) {",
        "    return; // 未找到",
        "  }",
        "  Node* y = z; // 实际删除的节点",
        "  int y_original_color = y->color;",
        "  if (z->left == NULL) {",
        "    Node* x = z->right;",
        "    transplant(T, z, z->right);",
        "  } else if (z->right == NULL) {",
        "    Node* x = z->left;",
        "    transplant(T, z, z->left);",
        "  } else { // 有两个子节点",
        "    y = minimum(z->right);",
        "    y_original_color = y->color;",
        "    Node* x = y->right;",
        "    // 替换和重新链接",
        "  }",
        "  if (y_original_color == BLACK) {",
        "    rb_delete_fixup(T, x);",
        "  }",
        "}",
    ],
    "Java": [
        "void rbDelete(RBTree T, int val) {",
        "  Node z = search(T.root, val);",
        "  if (z == null) {",
        "    return; // 未找到",
        "  }",
        "  Node y = z; // 实际删除的节点",
        "  int yOriginalColor = y.color;",
        "  if (z.left == null) {",
        "    Node x = z.right;",
        "    transplant(T, z, z.right);",
        "  } else if (z.right == null) {",
        "    Node x = z.left;",
        "    transplant(T, z, z.left);",
        "  } else { // 有两个子节点",
        "    y = minimum(z.right);",
        "    yOriginalColor = y.color;",
        "    Node x = y.right;",
        "    // 替换和重新链接",
        "  }",
        "  if (yOriginalColor == BLACK) {",
        "    rbDeleteFixup(T, x);",
        "  }",
        "}",
    ],
    "Python": [
        "def rb_delete(T, val):",
        "  z = search(T.root, val)",
        "  if z is None:",
        "    return  # 未找到",
        "  # endif",
        "  y = z  # 实际删除的节点",
        "  y_original_color = y.color",
        "  if z.left is None:",
        "    x = z.right",
        "    transplant(T, z, z.right)",
        "  elif z.right is None:",
        "    x = z.left",
        "    transplant(T, z, z.left)",
        "  else:  # 有两个子节点",
        "    y = minimum(z.right)",
        "    y_original_color = y.color",
        "    x = y.right",
        "    # 替换和重新链接",
        "  # endif",
        "  if y_original_color == BLACK:",
        "    rb_delete_fixup(T, x)",
        "  # endif",
    ]
}

# 删除修复 - 多语言
MULTILANG_RB_DELETE_FIXUP = {
    "伪代码": [
        "RB-DELETE-FIXUP(T, x):",
        "  while x ≠ T.root and x.color = BLACK do",
        "    if x = x.parent.left then",
        "      w ← x.parent.right  // 兄弟",
        "      if w.color = RED then  // Case 1",
        "        w.color ← BLACK",
        "        x.parent.color ← RED",
        "        LEFT-ROTATE(T, x.parent)",
        "        w ← x.parent.right",
        "      end if",
        "      if w.left.color=BLACK and w.right.color=BLACK then",
        "        w.color ← RED  // Case 2",
        "        x ← x.parent",
        "      else",
        "        // Case 3 & 4",
        "      end if",
        "    else  // 对称情况",
        "      // ... (对称操作)",
        "    end if",
        "  end while",
        "  x.color ← BLACK",
    ],
    "C语言": [
        "void rb_delete_fixup(RBTree* T, Node* x) {",
        "  while (x != T->root && x->color == BLACK) {",
        "    if (x == x->parent->left) {",
        "      Node* w = x->parent->right; // 兄弟",
        "      if (w->color == RED) { // Case 1",
        "        w->color = BLACK;",
        "        x->parent->color = RED;",
        "        left_rotate(T, x->parent);",
        "        w = x->parent->right;",
        "      }",
        "      if (w->left->color==BLACK && w->right->color==BLACK) {",
        "        w->color = RED; // Case 2",
        "        x = x->parent;",
        "      } else {",
        "        // Case 3 & 4",
        "      }",
        "    } else { // 对称情况",
        "      // ... (对称操作)",
        "    }",
        "  }",
        "  x->color = BLACK;",
        "}",
    ],
    "Java": [
        "void rbDeleteFixup(RBTree T, Node x) {",
        "  while (x != T.root && x.color == BLACK) {",
        "    if (x == x.parent.left) {",
        "      Node w = x.parent.right; // 兄弟",
        "      if (w.color == RED) { // Case 1",
        "        w.color = BLACK;",
        "        x.parent.color = RED;",
        "        leftRotate(T, x.parent);",
        "        w = x.parent.right;",
        "      }",
        "      if (w.left.color==BLACK && w.right.color==BLACK) {",
        "        w.color = RED; // Case 2",
        "        x = x.parent;",
        "      } else {",
        "        // Case 3 & 4",
        "      }",
        "    } else { // 对称情况",
        "      // ... (对称操作)",
        "    }",
        "  }",
        "  x.color = BLACK;",
        "}",
    ],
    "Python": [
        "def rb_delete_fixup(T, x):",
        "  while x != T.root and x.color == BLACK:",
        "    if x == x.parent.left:",
        "      w = x.parent.right  # 兄弟",
        "      if w.color == RED:  # Case 1",
        "        w.color = BLACK",
        "        x.parent.color = RED",
        "        left_rotate(T, x.parent)",
        "        w = x.parent.right",
        "      # endif",
        "      if w.left.color==BLACK and w.right.color==BLACK:",
        "        w.color = RED  # Case 2",
        "        x = x.parent",
        "      else:",
        "        # Case 3 & 4",
        "      # endif",
        "    else:  # 对称情况",
        "      # ... (对称操作)",
        "    # endif",
        "  # endwhile",
        "  x.color = BLACK",
    ]
}

# 保持向后兼容的旧变量（默认使用伪代码）
PSEUDOCODE_RB_INSERT = MULTILANG_RB_INSERT["伪代码"]
PSEUDOCODE_RB_INSERT_FIXUP = MULTILANG_RB_INSERT_FIXUP["伪代码"]
PSEUDOCODE_RB_DELETE = MULTILANG_RB_DELETE["伪代码"]
PSEUDOCODE_RB_DELETE_FIXUP = MULTILANG_RB_DELETE_FIXUP["伪代码"]
PSEUDOCODE_LEFT_ROTATE = MULTILANG_LEFT_ROTATE["伪代码"]
PSEUDOCODE_RIGHT_ROTATE = MULTILANG_RIGHT_ROTATE["伪代码"]
PSEUDOCODE_RECOLOR = MULTILANG_RECOLOR["伪代码"]
PSEUDOCODE_SEARCH = MULTILANG_SEARCH["伪代码"]

class RBTVisualizer:
    def __init__(self, root):
        self.window = root
        self.window.title("红黑树可视化演示")
        self.window.config(bg="#F0F2F5")
        
        # 设置窗口图标和样式
        self.window.geometry("1550x850")
        self.window.minsize(1400, 800)
        
        # 代码语言设置（支持运行时切换）
        self.current_code_language = LANG_PSEUDOCODE  # 默认伪代码
        self.current_operation_type = None  # 当前操作类型
        self.current_highlight_line = -1  # 当前高亮行
        self.current_step_desc = ""  # 当前步骤描述
        
        # 颜色配置
        self.colors = {
            "bg_primary": "#F0F2F5",
            "bg_secondary": "#FFFFFF",
            "red_node": "#FF5252",
            "black_node": "#37474F",
            "highlight": "#FF9800",
            "path_highlight": "#4CAF50",
            "delete_mark": "#2196F3",
            "text_light": "#FFFFFF",
            "text_dark": "#212121",
            "btn_primary": "#2196F3",
            "btn_success": "#4CAF50",
            "btn_warning": "#FF9800",
            "btn_danger": "#F44336",
            "canvas_bg": "#FAFAFA",
            "search_halo": "#FFC107",
            "rotation_guide": "#9C27B0",
            "case1_color": "#E91E63",
            "case2_color": "#9C27B0",
            "case3_color": "#3F51B5",
            "info_panel": "#FFF9C4",
            "knowledge_panel": "#E3F2FD",
            "nil_node": "#90A4AE",
            "parent_link": "#B39DDB",
            # 伪代码相关颜色
            "code_bg": "#1E1E2E",
            "code_fg": "#D4D4D4",
            "code_highlight_bg": "#264F78",
            "code_highlight_fg": "#FFFFFF",
            "code_keyword": "#569CD6",
            "code_comment": "#6A9955",
            "code_string": "#CE9178",
            # 新增教育面板颜色
            "edu_panel_bg": "#E8F5E9",
            "edu_panel_border": "#4CAF50",
            "case_panel_bg": "#FFF3E0",
            "case_panel_border": "#FF9800",
        }
        
        # 字体配置
        self.code_font = ("Consolas", 10)
        
        # 动画控制变量
        self.animation_speed = 500  # 默认速度（毫秒）
        self.paused = False
        self.current_step = 0
        self.total_steps = 0
        
        # 伪代码当前内容
        self.current_pseudocode = []
        
        # 可视化选项
        self.show_nil_nodes = False
        self.show_parent_links = False
        self.show_black_height = False
        
        # 创建主框架
        self.main_frame = Frame(self.window, bg=self.colors["bg_primary"])
        self.main_frame.pack(fill=BOTH, expand=True, padx=12, pady=12)
        
        # 创建标题
        self.create_header()
        
        # 创建内容区域（包含画布和伪代码面板）
        self.content_frame = Frame(self.main_frame, bg=self.colors["bg_primary"])
        self.content_frame.pack(fill=BOTH, expand=True, pady=(0, 8))
        
        # 创建画布区域
        self.create_canvas_area()
        
        # 创建伪代码面板
        self._create_pseudocode_panel()
        
        # 创建教育信息面板（在画布下方）
        self._create_education_panel()
        
        # 创建控制面板
        self.create_control_panel()
        
        # 初始化模型和状态
        self.model = RBModel()
        self.node_vis: Dict[str, Dict] = {}
        self.animating = False
        self.node_w = 100
        self.node_h = 40
        self.level_gap = 85
        self.margin_x = 40
        
        # 临时动画对象存储
        self.temp_objects = []
        
        # 知识展示状态
        self.showing_welcome = True
        
        # 绘制初始说明
        self.draw_instructions()

    def create_header(self):
        """创建标题区域"""
        header_frame = Frame(self.main_frame, bg=self.colors["bg_secondary"], 
                           relief=RAISED, bd=1)
        header_frame.pack(fill=X, pady=(0, 12))
        
        title_label = Label(header_frame, text="红黑树可视化演示系统", 
                          font=("微软雅黑", 16, "bold"), 
                          bg=self.colors["bg_secondary"],
                          fg=self.colors["text_dark"],
                          pady=12)
        title_label.pack()
        
        subtitle_label = Label(header_frame, 
                             text="演示红黑树的插入/删除过程:搜索路径、节点操作、颜色调整与旋转修复",
                             font=("微软雅黑", 10), 
                             bg=self.colors["bg_secondary"],
                             fg="#666666")
        subtitle_label.pack(pady=(0, 10))

    def create_canvas_area(self):
        """创建画布区域"""
        canvas_container = Frame(self.content_frame, bg=self.colors["bg_secondary"],
                               relief=SOLID, bd=1)
        canvas_container.pack(side=LEFT, fill=BOTH, expand=True)
        
        # 画布控制栏
        canvas_toolbar = Frame(canvas_container, bg=self.colors["bg_secondary"], height=36)
        canvas_toolbar.pack(fill=X, padx=10, pady=6)
        canvas_toolbar.pack_propagate(False)
        
        self.status_label = Label(canvas_toolbar, text="就绪", 
                                font=("微软雅黑", 10), 
                                bg=self.colors["bg_secondary"],
                                fg=self.colors["btn_primary"],
                                anchor=W)
        self.status_label.pack(side=LEFT, fill=X, expand=True)
        
        # 可视化选项
        vis_options_frame = Frame(canvas_toolbar, bg=self.colors["bg_secondary"])
        vis_options_frame.pack(side=RIGHT, padx=(0, 15))
        
        # NIL节点显示选项
        self.nil_var = IntVar(value=0)
        nil_check = Checkbutton(vis_options_frame, text="显示NIL", variable=self.nil_var,
                               bg=self.colors["bg_secondary"], font=("微软雅黑", 9),
                               command=self._toggle_nil_nodes)
        nil_check.pack(side=LEFT, padx=3)
        
        # 父指针显示选项
        self.parent_var = IntVar(value=0)
        parent_check = Checkbutton(vis_options_frame, text="父指针", variable=self.parent_var,
                                  bg=self.colors["bg_secondary"], font=("微软雅黑", 9),
                                  command=self._toggle_parent_links)
        parent_check.pack(side=LEFT, padx=3)
        
        # 黑高度显示选项
        self.bh_var = IntVar(value=0)
        bh_check = Checkbutton(vis_options_frame, text="黑高度", variable=self.bh_var,
                              bg=self.colors["bg_secondary"], font=("微软雅黑", 9),
                              command=self._toggle_black_height)
        bh_check.pack(side=LEFT, padx=3)
        
        # 动画速度控制
        speed_frame = Frame(canvas_toolbar, bg=self.colors["bg_secondary"])
        speed_frame.pack(side=RIGHT, padx=10)
        
        Label(speed_frame, text="速度:", font=("微软雅黑", 9), 
              bg=self.colors["bg_secondary"]).pack(side=LEFT, padx=(0, 5))
        
        self.speed_scale = Scale(speed_frame, from_=100, to=2000, orient=HORIZONTAL,
                                length=100, showvalue=False, command=self.update_speed,
                                bg=self.colors["bg_secondary"], highlightthickness=0)
        self.speed_scale.set(500)
        self.speed_scale.pack(side=LEFT)
        
        # 画布 - 高度缩减以腾出教育面板空间
        self.canvas_w = 1100
        self.canvas_h = 420
        self.canvas = Canvas(canvas_container, bg=self.colors["canvas_bg"], 
                           width=self.canvas_w, height=self.canvas_h,
                           relief=FLAT, highlightthickness=1,
                           highlightbackground="#E0E0E0")
        self.canvas.pack(padx=10, pady=(0, 8), fill=BOTH, expand=True)

    def _create_pseudocode_panel(self):
        """创建伪代码显示面板"""
        # 伪代码面板容器
        self.code_panel = Frame(
            self.content_frame,
            bg=self.colors["bg_secondary"],
            width=340,
            relief=SOLID,
            bd=1
        )
        self.code_panel.pack(side=RIGHT, fill=Y, padx=(12, 0))
        self.code_panel.pack_propagate(False)
        
        # 标题栏（包含标题和语言切换）
        title_frame = Frame(self.code_panel, bg=self.colors["bg_secondary"])
        title_frame.pack(fill=X, padx=10, pady=(10, 5))
        
        # 伪代码标题
        code_title = Label(
            title_frame,
            text="📝 算法代码",
            bg=self.colors["bg_secondary"],
            fg=self.colors["text_dark"],
            font=("微软雅黑", 12, "bold")
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
            bg="#E8E8E8",
            fg="#333333",
            activebackground="#D0D0D0",
            activeforeground="#333333",
            highlightthickness=0,
            relief="flat",
            width=6
        )
        self.lang_menu["menu"].config(
            bg="#F0F0F0",
            fg="#333333",
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
                bg="#2196F3" if lang == self.current_code_language else "#E0E0E0",
                fg="#FFFFFF" if lang == self.current_code_language else "#333333",
                padx=8,
                pady=2,
                cursor="hand2"
            )
            btn.pack(side=LEFT, padx=2)
            btn.bind("<Button-1>", lambda e, l=lang: self._switch_code_language(l))
            self.lang_buttons[lang] = btn
        
        # 当前执行位置提示
        self.code_step_label = Label(
            self.code_panel,
            text="",
            bg=self.colors["bg_secondary"],
            fg=self.colors["btn_primary"],
            font=("微软雅黑", 9),
            wraplength=300,
            justify=LEFT
        )
        self.code_step_label.pack(pady=(0, 5), padx=10, anchor="w")
        
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
            width=38,
            height=30,
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
                btn.config(bg="#2196F3", fg="#FFFFFF")
            else:
                btn.config(bg="#E0E0E0", fg="#333333")
        
        # 保存当前高亮行
        saved_highlight = self.current_highlight_line
        
        # 如果有当前操作类型，重新显示该语言的代码
        if self.current_operation_type:
            self._show_pseudocode_for_operation(
                self.current_operation_type, 
                saved_highlight,
                self.current_step_desc
            )
    
    def _create_education_panel(self):
        """创建教育信息面板（位于画布下方，不遮挡树）"""
        # 教育面板容器
        self.edu_container = Frame(self.main_frame, bg=self.colors["bg_primary"])
        self.edu_container.pack(fill=X, pady=(0, 8))
        
        # 左侧：操作说明面板
        self.operation_panel = Frame(self.edu_container, bg=self.colors["edu_panel_bg"],
                                    relief=SOLID, bd=1, width=400, height=90)
        self.operation_panel.pack(side=LEFT, fill=Y, padx=(0, 8))
        self.operation_panel.pack_propagate(False)
        
        # 操作说明标题
        op_title = Label(self.operation_panel, text="📌 当前操作说明",
                        bg=self.colors["edu_panel_bg"], fg=self.colors["text_dark"],
                        font=("微软雅黑", 10, "bold"))
        op_title.pack(anchor=W, padx=10, pady=(8, 4))
        
        # 操作说明内容
        self.operation_text = Label(self.operation_panel, 
                                   text="准备就绪，请输入节点值开始操作",
                                   bg=self.colors["edu_panel_bg"], fg="#555555",
                                   font=("微软雅黑", 9), wraplength=380, justify=LEFT)
        self.operation_text.pack(anchor=W, padx=10, pady=2)
        
        # 中间：Case说明面板（用于Fixup过程中的Case解释）
        self.case_panel = Frame(self.edu_container, bg=self.colors["case_panel_bg"],
                               relief=SOLID, bd=1, width=450, height=90)
        self.case_panel.pack(side=LEFT, fill=Y, padx=(0, 8))
        self.case_panel.pack_propagate(False)
        
        # Case说明标题
        case_title = Label(self.case_panel, text="🔍 修复Case详解",
                          bg=self.colors["case_panel_bg"], fg=self.colors["text_dark"],
                          font=("微软雅黑", 10, "bold"))
        case_title.pack(anchor=W, padx=10, pady=(8, 4))
        
        # Case说明内容
        self.case_text = Label(self.case_panel, 
                              text="执行修复操作时，这里会显示当前Case的详细解释",
                              bg=self.colors["case_panel_bg"], fg="#555555",
                              font=("微软雅黑", 9), wraplength=430, justify=LEFT)
        self.case_text.pack(anchor=W, padx=10, pady=2)
        
        # 右侧：红黑树性质提示面板
        self.property_panel = Frame(self.edu_container, bg=self.colors["knowledge_panel"],
                                   relief=SOLID, bd=1, height=90)
        self.property_panel.pack(side=LEFT, fill=BOTH, expand=True)
        self.property_panel.pack_propagate(False)
        
        # 性质说明标题
        prop_title = Label(self.property_panel, text="📖 红黑树关键性质",
                          bg=self.colors["knowledge_panel"], fg=self.colors["text_dark"],
                          font=("微软雅黑", 10, "bold"))
        prop_title.pack(anchor=W, padx=10, pady=(8, 4))
        
        # 性质说明内容（简洁版）
        self.property_text = Label(self.property_panel, 
                                  text="① 节点为红或黑  ② 根节点为黑  ③ NIL叶子为黑\n"
                                       "④ 红节点的子节点必为黑  ⑤ 任一路径黑节点数相同",
                                  bg=self.colors["knowledge_panel"], fg="#333333",
                                  font=("微软雅黑", 9), justify=LEFT)
        self.property_text.pack(anchor=W, padx=10, pady=2)
    
    def _toggle_nil_nodes(self):
        """切换NIL节点显示"""
        self.show_nil_nodes = bool(self.nil_var.get())
        if self.model.root:
            self.draw_tree_from_root(clone_tree(self.model.root))
    
    def _toggle_parent_links(self):
        """切换父指针显示"""
        self.show_parent_links = bool(self.parent_var.get())
        if self.model.root:
            self.draw_tree_from_root(clone_tree(self.model.root))
    
    def _toggle_black_height(self):
        """切换黑高度显示"""
        self.show_black_height = bool(self.bh_var.get())
        if self.model.root:
            self.draw_tree_from_root(clone_tree(self.model.root))
    
    def update_operation_info(self, text: str):
        """更新操作说明面板"""
        self.operation_text.config(text=text)
    
    def update_case_info(self, case_name: str, description: str):
        """更新Case说明面板"""
        full_text = f"【{case_name}】\n{description}"
        self.case_text.config(text=full_text)
    
    def clear_case_info(self):
        """清除Case说明"""
        self.case_text.config(text="执行修复操作时，这里会显示当前Case的详细解释")
    
    def update_property_highlight(self, violated_property: int = 0):
        """高亮显示被违反的性质"""
        base_text = "① 节点为红或黑  ② 根节点为黑  ③ NIL叶子为黑\n④ 红节点的子节点必为黑  ⑤ 任一路径黑节点数相同"
        if violated_property > 0:
            # 简单提示哪条性质可能被违反
            self.property_text.config(text=base_text + f"\n⚠️ 性质 {violated_property} 可能被违反，需要修复！",
                                     fg="#D32F2F")
        else:
            self.property_text.config(text=base_text, fg="#333333")

    def _show_initial_code_hint(self):
        """显示初始提示信息"""
        hint_text = [
            "💡 伪代码显示区域",
            "",
            "执行插入或删除操作时，",
            "这里会显示对应的算法伪代码，",
            "并实时高亮当前执行的步骤。",
            "",
            "📌 红黑树关键操作：",
            "  • 插入节点 (RB-INSERT)",
            "  • 删除节点 (RB-DELETE)",
            "  • 查找节点 (SEARCH)",
            "  • 左旋/右旋 (ROTATE)",
            "  • 重着色 (RECOLOR)",
            "  • 插入修复 (INSERT-FIXUP)",
            "  • 删除修复 (DELETE-FIXUP)",
            "",
            "🎯 使用方法：",
            "  1. 在输入框输入数字",
            "  2. 点击插入或删除按钮",
            "  3. 观察动画和伪代码高亮",
            "",
            "📖 红黑树性质：",
            "  1. 节点是红色或黑色",
            "  2. 根节点是黑色",
            "  3. 叶子节点(NIL)是黑色",
            "  4. 红节点的子节点必须是黑色",
            "  5. 任一节点到叶子的路径上",
            "     黑色节点数量相同",
        ]
        self._set_pseudocode(hint_text)
        self.code_step_label.config(text="")

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
        keywords = ["if", "else", "while", "return", "null", "new", "and", "or", "RED", "BLACK"]
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

    def _show_pseudocode_for_operation(self, operation: str, highlight_line: int = -1, step_desc: str = ""):
        """
        显示指定操作的伪代码（支持多语言）
        
        Args:
            operation: 操作类型
            highlight_line: 要高亮的行号 (0-based)
            step_desc: 步骤描述
        """
        # 保存当前状态，用于语言切换时恢复
        self.current_operation_type = operation
        self.current_highlight_line = highlight_line
        self.current_step_desc = step_desc
        
        # 多语言代码映射
        multilang_map = {
            'insert': MULTILANG_RB_INSERT,
            'insert_fixup': MULTILANG_RB_INSERT_FIXUP,
            'delete': MULTILANG_RB_DELETE,
            'delete_fixup': MULTILANG_RB_DELETE_FIXUP,
            'rotate_left': MULTILANG_LEFT_ROTATE,
            'rotate_right': MULTILANG_RIGHT_ROTATE,
            'recolor': MULTILANG_RECOLOR,
            'search': MULTILANG_SEARCH,
        }
        
        if operation in multilang_map:
            # 获取当前语言的代码
            code_dict = multilang_map[operation]
            code = code_dict.get(self.current_code_language, code_dict.get("伪代码", []))
            
            self._set_pseudocode(code, highlight_line)
            if step_desc:
                self.code_step_label.config(text=f"▶ {step_desc}")
            else:
                self.code_step_label.config(text="")

    def create_control_panel(self):
        """创建控制面板"""
        control_frame = Frame(self.main_frame, bg=self.colors["bg_secondary"],
                            relief=SOLID, bd=1)
        control_frame.pack(fill=X)

        # 输入区域
        input_frame = Frame(control_frame, bg=self.colors["bg_secondary"])
        input_frame.pack(fill=X, padx=15, pady=12)

        # 输入节点值
        Label(input_frame, text="输入节点值:",
            font=("微软雅黑", 10),
            bg=self.colors["bg_secondary"]).grid(row=0, column=0, sticky=W, padx=(0,6), pady=5)

        self.input_var = StringVar()
        self.input_entry = Entry(input_frame, textvariable=self.input_var,
                                font=("微软雅黑", 10), relief=SOLID, bd=1)
        self.input_entry.grid(row=0, column=1, padx=(0,12), pady=5, sticky=EW)
        self.input_entry.insert(0, "1,2,3,4,5,0,6")
        self.input_entry.bind("<Return>", lambda e: self.start_insert_animated())

        # DSL输入
        Label(input_frame, text="DSL命令:",
            font=("微软雅黑", 10),
            bg=self.colors["bg_secondary"]).grid(row=0, column=2, sticky=W, padx=(6,6), pady=5)

        self.dsl_var = StringVar()
        self.dsl_entry = Entry(input_frame, textvariable=self.dsl_var,
                            font=("微软雅黑", 10), relief=SOLID, bd=1)
        self.dsl_entry.grid(row=0, column=3, padx=(0,6), pady=5, sticky=EW)
        self.dsl_entry.insert(0, "create 1 2 3 4 5 0 6")
        self.dsl_entry.bind("<Return>", lambda e: self.execute_dsl())

        # DSL执行按钮
        self.execute_dsl_btn = Button(input_frame, text="执行DSL", command=self.execute_dsl,
                                    bg=self.colors["btn_primary"], fg="white",
                                    font=("微软雅黑", 9), relief=FLAT, bd=0, padx=10, pady=4,
                                    cursor="hand2")
        self.execute_dsl_btn.grid(row=0, column=4, padx=(6,0), pady=5, sticky=W)

        input_frame.columnconfigure(1, weight=1)
        input_frame.columnconfigure(3, weight=1)
        self.entry = self.input_entry

        # 按钮区域
        btn_frame = Frame(control_frame, bg=self.colors["bg_secondary"])
        btn_frame.pack(fill=X, padx=15, pady=10)

        # 第一行按钮
        btn_row1 = Frame(btn_frame, bg=self.colors["bg_secondary"])
        btn_row1.pack(fill=X, pady=5)

        self.create_button(btn_row1, "插入节点 (动画演示)",
                        self.start_insert_animated, self.colors["btn_success"]).pack(side=LEFT, padx=4)
        self.create_button(btn_row1, "插入节点 (直接)",
                        self.insert_direct, self.colors["btn_primary"]).pack(side=LEFT, padx=4)
        self.create_button(btn_row1, "单节点插入 (动画)",
                        self.insert_single_node_animated, "#00ACC1").pack(side=LEFT, padx=4)
        self.create_button(btn_row1, "删除节点 (动画)",
                        self.start_delete_animated, self.colors["btn_danger"]).pack(side=LEFT, padx=4)
        self.create_button(btn_row1, "查找节点 (动画)",
                        self.start_search_animated, "#00BCD4").pack(side=LEFT, padx=4)
        self.create_button(btn_row1, "清空树",
                        self.clear_canvas, self.colors["btn_warning"]).pack(side=LEFT, padx=4)

        # 第二行按钮
        btn_row2 = Frame(btn_frame, bg=self.colors["bg_secondary"])
        btn_row2.pack(fill=X, pady=5)

        self.create_button(btn_row2, "保存结构",
                        self.save_structure, "#9C27B0").pack(side=LEFT, padx=4)
        self.create_button(btn_row2, "加载结构",
                        self.load_structure, "#9C27B0").pack(side=LEFT, padx=4)
        self.create_button(btn_row2, "返回主界面",
                        self.back_to_main, self.colors["btn_danger"]).pack(side=LEFT, padx=4)
        
        # 第三行按钮 - 动画控制
        btn_row3 = Frame(btn_frame, bg=self.colors["bg_secondary"])
        btn_row3.pack(fill=X, pady=5)
        
        self.create_button(btn_row3, "暂停动画",
                        self.pause_animation, "#FF5722").pack(side=LEFT, padx=4)
        self.create_button(btn_row3, "继续动画",
                        self.resume_animation, "#4CAF50").pack(side=LEFT, padx=4)
        self.create_button(btn_row3, "下一步",
                        self.next_step, "#2196F3").pack(side=LEFT, padx=4)

    def create_button(self, parent, text, command, color):
        """创建样式化按钮"""
        return Button(parent, text=text, command=command,
                     bg=color, fg="white", font=("微软雅黑", 9),
                     relief=FLAT, bd=0, padx=12, pady=6,
                     cursor="hand2")

    def draw_instructions(self):
        """绘制初始说明"""
        self.canvas.delete("all")
        self.node_vis.clear()    
        # 绘制图例（放在画布底部）
        legend_y = self.canvas_h - 20
        self.draw_legend(legend_y)
        
        # 只在未开始动画时显示欢迎信息
        if self.showing_welcome:
            # 绘制欢迎信息（居中显示，不会被遮挡）
            welcome_text = "欢迎使用红黑树可视化演示系统\n\n" \
                          "功能说明:\n" \
                          "• 插入节点: 展示搜索路径和平衡过程\n" \
                          "• 删除节点: 展示删除过程和修复操作\n" \
                          "• 查找节点: 展示搜索路径动画\n" \
                          "• 动画控制: 可暂停、继续和调整速度\n" \
                          "• 可视化选项: 显示NIL节点/父指针/黑高度\n" \
                          "• 支持DSL命令批量操作\n\n" \
                          "请在下方输入节点值开始演示"
            
            self.canvas.create_text(self.canvas_w/2, self.canvas_h/2 - 40, 
                                  text=welcome_text, font=("微软雅黑", 11), 
                                  fill="#666666", justify=CENTER)

    def draw_legend(self, y_pos):
        """绘制图例（更紧凑的布局）"""
        legend_items = [
            ("红节点", self.colors["red_node"]),
            ("黑节点", self.colors["black_node"]),
            ("搜索路径", self.colors["path_highlight"]),
            ("当前操作", self.colors["highlight"]),
            ("旋转", self.colors["rotation_guide"]),
        ]
        
        if self.show_nil_nodes:
            legend_items.append(("NIL", self.colors["nil_node"]))
        if self.show_parent_links:
            legend_items.append(("父指针", self.colors["parent_link"]))
        
        # 计算居中起始位置
        total_width = len(legend_items) * 80
        x_pos = (self.canvas_w - total_width) / 2
        
        for text, color in legend_items:
            self.canvas.create_rectangle(x_pos, y_pos-6, x_pos+14, y_pos+6,
                                       fill=color, outline="#CCCCCC")
            self.canvas.create_text(x_pos+20, y_pos, text=text, 
                                  font=("微软雅黑", 8), anchor=W, fill="#666666")
            x_pos += 80

    def update_status(self, text: str):
        """更新状态栏"""
        self.status_label.config(text=text)
    
    def update_speed(self, value):
        """更新动画速度"""
        self.animation_speed = int(value)
    
    def pause_animation(self):
        """暂停动画"""
        self.paused = True
        self.update_status("动画已暂停")
    
    def resume_animation(self):
        """继续动画"""
        self.paused = False
        self.update_status("动画继续")
    
    def next_step(self):
        """执行下一步"""
        # 这里需要与具体的动画步骤配合使用
        pass
    
    def wait_if_paused(self):
        """如果暂停则等待"""
        while self.paused:
            self.window.update()
            time.sleep(0.1)
    
    def execute_dsl(self):
        """执行DSL命令"""
        cmd = self.dsl_var.get().strip()
        if not cmd:
            messagebox.showinfo("提示", "请输入DSL命令,例如:\n  create 1,2,3\n  delete 5\n  clear")
            return

        if process_command is None:
            messagebox.showerror("模块缺失", "未找到 DSL_utils 模块,无法执行 DSL 命令。")
            self.update_status("DSL 执行失败:缺少 DSL_utils")
            return

        try:
            result = process_command(self, cmd)
            if result is False:
                self.update_status(f"DSL 命令执行失败: {cmd}")
            else:
                self.update_status(f"DSL 命令已执行: {cmd}")
        except Exception as e:
            import traceback
            traceback.print_exc()
            messagebox.showerror("DSL 执行异常", f"执行 DSL 时发生异常:\n{e}")
            self.update_status("DSL 执行异常")

    def start_delete_animated(self):
        """开始删除节点动画"""
        if self.animating:
            messagebox.showinfo("提示", "当前正在执行动画,请稍候...")
            return
        
        if self.model.root is None:
            messagebox.showinfo("提示", "树为空,无法删除节点")
            return
        
        val_str = self.input_var.get().strip()
        if not val_str:
            messagebox.showinfo("提示", "请输入要删除的节点值")
            return
        
        # 只取第一个值
        values = [v.strip() for v in val_str.split(",") if v.strip()]
        if not values:
            messagebox.showinfo("提示", "请输入有效的节点值")
            return
        
        val = values[0]
        
        try:
            int(val)
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")
            return
        
        # 开始动画，移除欢迎文字
        self.showing_welcome = False
        self.animating = True
        self.update_status(f"开始删除节点: {val}")
        
        # 使用底部面板显示操作说明
        self.update_operation_info(f"🗑️ 开始删除节点 {val}：首先搜索定位该节点")
        self.update_case_info("删除流程", "① 搜索目标节点\n② 找到后继节点（如需要）\n③ 删除节点\n④ 如删除黑节点，需要修复")
        self.update_property_highlight(5)  # 删除可能违反性质5
        
        # 显示删除伪代码
        self._show_pseudocode_for_operation('delete', 0, f"开始删除节点 {val}")
        
        # 调用删除方法
        deleted_node, path_nodes, events, snapshots = self.model.delete_with_steps(val)
        
        if deleted_node is None:
            self.animating = False
            # 高亮未找到的代码行
            self._show_pseudocode_for_operation('delete', 3, f"节点 {val} 未找到")
            messagebox.showinfo("提示", f"节点 {val} 不存在")
            self.update_status(f"删除失败: 节点 {val} 不存在")
            return
        
        snap_pre = snapshots[0]
        snap_after_delete = snapshots[1] if len(snapshots) > 1 else None
        
        # 显示搜索伪代码
        self._show_pseudocode_for_operation('search', 1, f"搜索节点 {val}")
        
        # 高亮搜索路径
        def highlight_path(i=0):
            if i >= len(path_nodes):
                self.update_status(f"找到节点 {val}, 准备删除")
                self.show_operation_explanation("delete", f"已定位到节点 {val}, 开始删除操作")
                # 高亮删除操作代码
                self._show_pseudocode_for_operation('delete', 4, f"找到节点，开始删除")
                self.animate_delete_node(val, deleted_node, snap_after_delete,
                                       lambda: self._after_delete_events(events, snapshots, val))
                return
            
            self.wait_if_paused()
            
            node = path_nodes[i]
            self.draw_tree_from_root(snap_pre)
            
            # 高亮当前访问的节点
            origid_to_key, _ = self._build_key_maps_from_root(snap_pre)
            node_id = getattr(node, 'id', None)
            key = origid_to_key.get(node_id)
            
            if key and key in self.node_vis:
                try:
                    # 如果是目标节点,用删除标记颜色
                    if str(node.val) == str(val):
                        self.canvas.itemconfig(self.node_vis[key]['rect'],
                                             outline=self.colors["delete_mark"],
                                             width=4)
                        # 添加闪烁效果
                        self.flash_node(key, self.colors["delete_mark"])
                        # 高亮找到节点的代码
                        self._highlight_line(3)  # return node // 找到
                        self.code_step_label.config(text=f"▶ 找到节点 {val}")
                    else:
                        self.canvas.itemconfig(self.node_vis[key]['rect'],
                                             outline=self.colors["path_highlight"],
                                             width=3)
                        # 添加搜索光晕
                        self.create_search_halo(key)
                        # 高亮搜索过程中的代码行
                        if self._compare_values(val, node.val):
                            self._highlight_line(5)  # node = node.left
                            self.code_step_label.config(text=f"▶ {val} < {node.val}，向左搜索")
                        else:
                            self._highlight_line(7)  # node = node.right
                            self.code_step_label.config(text=f"▶ {val} >= {node.val}，向右搜索")
                except Exception:
                    pass
            
            self.update_status(f"搜索路径: 访问节点 {node.val} (步骤 {i+1})")
            self.window.after(max(100, self.animation_speed), lambda: highlight_path(i+1))
        
        highlight_path(0)

    def animate_delete_node(self, val_str: str, deleted_node, snap_after_delete, on_complete):
        """删除节点的淡出动画"""
        if not snap_after_delete:
            # 如果删除后树为空
            self.canvas.delete("all")
            self.draw_instructions()
            self.update_status(f"已删除节点 {val_str}, 树已为空")
            self.window.after(400, on_complete)
            return
        
        # 找到被删除节点的可视化键
        snap_before = clone_tree(self.model.root) if self.model.root else None
        if not snap_before:
            on_complete()
            return
        
        origid_to_key, _ = self._build_key_maps_from_root(snap_before)
        deleted_id = getattr(deleted_node, 'id', None)
        deleted_key = origid_to_key.get(deleted_id)
        
        if not deleted_key or deleted_key not in self.node_vis:
            # 无法找到节点,直接完成
            self.draw_tree_from_root(snap_after_delete)
            on_complete()
            return
        
        # 显示删除动画说明
        self.show_operation_explanation("delete", f"正在删除节点 {val_str}")
        
        # 淡出动画
        node_item = self.node_vis[deleted_key]
        rect_id = node_item['rect']
        text_id = node_item['text']
        color_label = node_item['color_label']
        
        steps = 20
        delay = max(10, self.animation_speed // 30)
        
        def fade_step(i=0):
            if i >= steps:
                # 删除完成,重绘树
                self.draw_tree_from_root(snap_after_delete)
                self.update_status(f"节点 {val_str} 已删除")
                self.window.after(max(100, self.animation_speed), on_complete)
                return
            
            self.wait_if_paused()
            
            # 计算透明度 (通过颜色变淡模拟)
            alpha = 1 - (i / steps)
            
            try:
                # 获取当前颜色并调整亮度
                if hasattr(deleted_node, 'color') and deleted_node.color == "R":
                    base_color = self.colors["red_node"]
                else:
                    base_color = self.colors["black_node"]
                
                # 简单的淡出效果:逐渐变成背景色
                bg_color = self.colors["canvas_bg"]
                
                # 逐渐缩小
                scale = alpha
                cx = node_item['cx']
                cy = node_item['cy']
                new_w = self.node_w * scale
                new_h = self.node_h * scale
                
                left = cx - new_w/2
                right = cx + new_w/2
                top = cy - new_h/2
                bottom = cy + new_h/2
                
                self.canvas.coords(rect_id, left, top, right, bottom)
                
                # 逐渐变透明
                if i > steps/2:
                    self.canvas.itemconfig(text_id, state=HIDDEN)
                    self.canvas.itemconfig(color_label, state=HIDDEN)
                
            except Exception:
                pass
            
            self.window.after(delay, lambda: fade_step(i+1))
        
        fade_step(0)

    def _after_delete_events(self, events, snapshots, val):
        """删除后的修复事件处理"""
        if not events or len(snapshots) <= 2:
            # 没有修复事件,直接完成
            self.draw_tree_from_root(clone_tree(self.model.root))
            self.animating = False
            self.update_status(f"完成删除: {val}")
            self.update_operation_info(f"✅ 节点 {val} 删除完成（无需修复）")
            self.clear_case_info()
            self.update_property_highlight(0)
            self._show_initial_code_hint()  # 恢复初始提示
            return
        
        # 显示删除修复伪代码
        self._show_pseudocode_for_operation('delete_fixup', 0, "删除黑色节点，需要修复")
        self.update_operation_info(f"⚠️ 删除了黑色节点 {val}，需要修复红黑树性质")
        
        def done_all():
            self.draw_tree_from_root(clone_tree(self.model.root))
            self.animating = False
            self.update_status(f"完成删除并修复平衡: {val}")
            self.update_operation_info(f"✅ 节点 {val} 删除完成，树已重新平衡")
            self.clear_case_info()
            self.update_property_highlight(0)
            # 高亮最后的着色
            self._show_pseudocode_for_operation('delete_fixup', 27, "修复完成，节点染黑")
        
        # 从索引2开始(0是删除前,1是删除后删除修复前)
        self._animate_delete_events_sequence(events, snapshots, 2, done_all)

    def _animate_delete_events_sequence(self, events, snapshots, start_idx, on_done):
        """删除修复事件序列动画"""
        if not events:
            self.clear_case_info()
            on_done()
            return
        
        def step(event_idx=0, snap_idx=start_idx):
            if event_idx >= len(events):
                self.clear_case_info()
                on_done()
                return
            
            self.wait_if_paused()
            
            # 确保有足够的快照
            if snap_idx >= len(snapshots) or snap_idx + 1 >= len(snapshots):
                self.clear_case_info()
                on_done()
                return
            
            before_root = snapshots[snap_idx]
            after_root = snapshots[snap_idx + 1]
            ev = events[event_idx]
            
            # 根据事件类型显示对应的删除修复说明
            op_type = ev.get('type', 'unknown')
            
            if op_type == 'recolor':
                new_color = ev.get('new_color', '')
                if new_color == 'R':
                    self._show_pseudocode_for_operation('delete_fixup', 10, "Case 2: 兄弟两个子节点都是黑色")
                    self.update_case_info("删除Case 2", 
                        "兄弟是黑色，且兄弟的两个子节点都是黑色:\n将兄弟染红，将x指向父节点继续向上修复")
                else:
                    self._show_pseudocode_for_operation('delete_fixup', 5, "Case 1: 兄弟是红色")
                    self.update_case_info("删除Case 1", 
                        "兄弟是红色:\n① 将兄弟染黑\n② 将父节点染红\n③ 对父节点左旋\n④ 更新兄弟指针")
            elif op_type == 'rotate_left':
                self._show_pseudocode_for_operation('delete_fixup', 7, "Case 1/4: 执行左旋")
                self.update_case_info("删除Case 4 左旋", 
                    "兄弟是黑色，兄弟的右孩子是红色:\n执行左旋并调整颜色，修复完成")
            elif op_type == 'rotate_right':
                self._show_pseudocode_for_operation('delete_fixup', 16, "Case 3: 执行右旋")
                self.update_case_info("删除Case 3 右旋", 
                    "兄弟是黑色，兄弟的左孩子红、右孩子黑:\n① 将兄弟左孩子染黑\n② 将兄弟染红\n③ 对兄弟右旋\n④ 转化为Case 4")
            
            self.update_status(f"删除修复 {event_idx+1}/{len(events)}: {op_type}")
            self._animate_single_event(before_root, after_root, ev,
                                     lambda: step(event_idx+1, snap_idx+1))
        
        step(0, start_idx)

    # ---------- 查找动画流程 ----------
    
    def start_search_animated(self):
        """启动查找动画"""
        if self.animating:
            self.update_status("⚠️ 正在执行动画，请稍候...")
            return
        
        if self.model.root is None:
            messagebox.showinfo("💡 提示", "树为空，无法查找节点")
            return
            
        s = self.input_var.get().strip()
        if not s:
            messagebox.showinfo("💡 提示", "请输入要查找的数字，例如：1,2,3")
            return
            
        batch = [p.strip() for p in s.split(",") if p.strip()!=""]
        if not batch:
            return
            
        self.batch = batch
        self.showing_welcome = False
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
            self.clear_case_info()
            self.update_property_highlight(0)
            return

        val = self.batch[idx]
        # 调用 model 的 search_with_steps
        found_node, path_nodes, found = self.model.search_with_steps(val)
        
        # 获取当前树的快照用于可视化
        snap = clone_tree(self.model.root)
        pos = self.compute_positions_for_root(snap)
        
        # 建立 val -> key 映射
        val_to_keys: Dict[str, List[str]] = {}
        for k in pos.keys():
            base = k.split('#')[0]
            val_to_keys.setdefault(base, []).append(k)
        
        # 获取 orig_id -> key 映射
        origid_to_key, _ = self._build_key_maps_from_root(snap)

        def highlight_path_for_search(i=0):
            if i >= len(path_nodes):
                # 路径高亮完成
                if found:
                    # --- 找到节点 ---
                    self.update_status(f"✅ 找到 {val}")
                    self._show_pseudocode_for_operation('search', 3)  # return node // 找到
                    self.update_operation_info(f"✅ 查找成功：节点 {val} 存在于树中")
                    self.update_case_info("查找成功", f"已找到值为 {val} 的节点\n查找路径长度: {len(path_nodes)}")
                    # 高亮找到的节点为绿色
                    self.draw_tree_from_root(snap)
                    v = str(found_node.val)
                    keylist = val_to_keys.get(v, [])
                    if keylist:
                        key = keylist[0]  # 使用第一个匹配的key
                        try:
                            self.canvas.itemconfig(self.node_vis[key]['rect'], 
                                                 fill=self.colors["path_highlight"],
                                                 outline=self.colors["path_highlight"],
                                                 width=4)
                            # 添加找到效果
                            self.flash_node(key, self.colors["path_highlight"])
                        except Exception:
                            pass
                else:
                    # --- 未找到节点 ---
                    self.update_status(f"❌ 未找到 {val}")
                    self._show_pseudocode_for_operation('search', 10)  # return null // 未找到
                    self.update_operation_info(f"❌ 查找失败：节点 {val} 不存在于树中")
                    self.update_case_info("查找失败", f"未找到值为 {val} 的节点\n遍历路径长度: {len(path_nodes)}")
                    self.draw_tree_from_root(snap)
                
                # 延迟后进行下一个查找
                self.window.after(1000, lambda: self._search_seq(idx + 1))
                return
            
            self.wait_if_paused()
            
            # 高亮当前访问的节点
            node = path_nodes[i]
            node_id = getattr(node, 'id', None)
            
            self.draw_tree_from_root(snap)
            
            # 尝试通过 orig_id 找到 key
            key = origid_to_key.get(node_id)
            if not key:
                # 回退：通过值找 key
                v = str(node.val)
                keylist = val_to_keys.get(v, [])
                if keylist:
                    key = keylist[0]
            
            if key and key in self.node_vis:
                try:
                    self.canvas.itemconfig(self.node_vis[key]['rect'], 
                                         fill=self.colors["highlight"],
                                         outline=self.colors["search_halo"],
                                         width=4)
                    # 添加搜索光晕效果
                    self.create_search_halo(key)
                except Exception:
                    pass
            
            # 高亮伪代码中的搜索步骤
            if i == len(path_nodes) - 1 and found:
                # 最后一个节点且找到了
                self._show_pseudocode_for_operation('search', 2)  # if val == node.val
            else:
                # 搜索过程中
                self._show_pseudocode_for_operation('search', 1)  # while循环
            
            self.update_status(f"🔍 查找 {val}: 访问 {node.val} (步骤 {i+1}/{len(path_nodes)})")
            self.update_operation_info(f"🔍 查找 {val}：当前访问节点 {node.val}")
            self.window.after(max(300, self.animation_speed), lambda: highlight_path_for_search(i+1))

        highlight_path_for_search(0)

    def insert_single_node_animated(self):
        """单节点插入(带动画)"""
        if self.animating:
            messagebox.showinfo("提示", "当前正在执行动画,请稍候...")
            return
        
        val_str = self.input_var.get().strip()
        if not val_str:
            messagebox.showinfo("提示", "请输入要插入的单个节点值")
            return
        
        values = [v.strip() for v in val_str.split(",") if v.strip()]
        if len(values) != 1:
            messagebox.showwarning("提示", "单节点插入模式只能输入一个节点值\n如需插入多个节点,请使用批量插入功能")
            return
        
        val = values[0]
        
        try:
            int(val)
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")
            return
        
        # 开始动画，移除欢迎文字
        self.showing_welcome = False
        self.animating = True
        
        # 使用底部面板显示操作说明
        self.update_operation_info(f"🎯 单节点插入：正在搜索节点 {val} 的插入位置")
        self.update_case_info("插入流程", "① 按BST规则从根开始搜索\n② 找到空位置插入红色新节点\n③ 检查并修复红黑树性质")
        self.update_property_highlight(4)
        
        # 显示插入伪代码
        self._show_pseudocode_for_operation('insert', 0, f"开始插入节点 {val}")
        
        inserted_node, path_nodes, events, snapshots = self.model.insert_with_steps(val)
        
        snap_pre = snapshots[0]
        snap_after_insert = snapshots[1] if len(snapshots) > 1 else None
        
        pos_pre = self.compute_positions_for_root(snap_pre)
        origid_to_key_pre, _ = self._build_key_maps_from_root(snap_pre)
        
        def highlight_path(i=0):
            if i >= len(path_nodes):
                self.update_status(f"插入 {val}: 定位插入位置")
                self.show_operation_explanation("insert", f"已找到插入位置, 准备插入节点 {val}")
                # 高亮插入位置代码
                if snap_pre is None:
                    self._show_pseudocode_for_operation('insert', 14, f"树为空，{val}成为根节点")
                else:
                    self._show_pseudocode_for_operation('insert', 16, f"将{val}插入到正确位置")
                self.animate_flyin_new(val, snap_after_insert, 
                                     lambda: self._after_insert_events_single(events, snapshots, val))
                return
            
            self.wait_if_paused()
            
            node = path_nodes[i]
            node_id = getattr(node, 'id', None)
            key = origid_to_key_pre.get(node_id)
            self.draw_tree_from_root(snap_pre)
            
            if key:
                try:
                    self.canvas.itemconfig(self.node_vis[key]['rect'], 
                                         outline=self.colors["path_highlight"], 
                                         width=3)
                    # 添加搜索光晕
                    self.create_search_halo(key)
                except Exception:
                    pass
            
            # 高亮搜索过程中的代码行
            if self._compare_values(val, node.val):
                self._highlight_line(8)  # if z.val < x.val
                self.code_step_label.config(text=f"▶ {val} < {node.val}，向左子树搜索")
            else:
                self._highlight_line(10)  # else: x = x.right
                self.code_step_label.config(text=f"▶ {val} >= {node.val}，向右子树搜索")
            
            self.update_status(f"搜索路径: 访问节点 {node.val} (步骤 {i+1})")
            self.window.after(max(100, self.animation_speed), lambda: highlight_path(i+1))
        
        highlight_path(0)

    def _after_insert_events_single(self, events, snapshots, val):
        """单节点插入后的事件处理"""
        if not events:
            self.draw_tree_from_root(clone_tree(self.model.root))
            self.animating = False
            self.update_status(f"完成单节点插入: {val}")
            self.update_operation_info(f"✅ 节点 {val} 插入完成（无需修复）")
            self.clear_case_info()
            self.update_property_highlight(0)
            self._show_initial_code_hint()  # 恢复初始提示
            return
        
        # 显示插入修复伪代码
        self._show_pseudocode_for_operation('insert_fixup', 0, "开始修复红黑树性质")
        self.update_operation_info(f"⚠️ 插入红色节点 {val} 后需要修复性质4")
        
        def done_all():
            self.draw_tree_from_root(clone_tree(self.model.root))
            self.animating = False
            self.update_status(f"完成单节点插入: {val}")
            self.update_operation_info(f"✅ 节点 {val} 插入完成，树已重新平衡")
            self.clear_case_info()
            self.update_property_highlight(0)
            # 高亮根节点变黑
            self._show_pseudocode_for_operation('insert_fixup', 31, "确保根节点为黑色")
        
        self._animate_events_sequence(events, snapshots, 0, done_all)

    def _draw_connection(self, cx, cy, tx, ty):
        """绘制节点连接线"""
        top = cy + self.node_h/2
        bot = ty - self.node_h/2
        midy = (top + bot) / 2
        
        line = self.canvas.create_line(cx, top, cx, midy, tx, bot, 
                                     width=2, fill="#78909C", arrow=LAST,
                                     smooth=True)
        return line

    def compute_positions_for_root(self, root: Optional[RBNode]) -> Dict[str, Tuple[float, float]]:
        """计算节点位置"""
        res: Dict[str, Tuple[float,float]] = {}
        if not root:
            return res

        inorder_nodes: List[RBNode] = []
        depths: Dict[RBNode, int] = {}
        
        def inorder(n: Optional[RBNode], d: int):
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
            y = 80 + depths[node] * self.level_gap
            res[key] = (x, y)
            
        return res

    def _build_key_maps_from_root(self, root: Optional[RBNode]) -> Tuple[Dict[int,str], Dict[str, RBNode]]:
        """构建键映射"""
        orig_id_to_key: Dict[int,str] = {}
        key_to_node: Dict[str, RBNode] = {}
        if not root:
            return orig_id_to_key, key_to_node

        inorder_nodes: List[RBNode] = []
        def inorder_collect(n: Optional[RBNode]):
            if not n:
                return
            inorder_collect(n.left)
            inorder_nodes.append(n)
            inorder_collect(n.right)
        inorder_collect(root)

        counts: Dict[str,int] = {}
        for node in inorder_nodes:
            base = str(node.val)
            cnt = counts.get(base, 0)
            counts[base] = cnt + 1
            key = f"{base}#{cnt}" if cnt > 0 else base
            key_to_node[key] = node
            if getattr(node, 'orig_id', None) is not None:
                orig_id_to_key[node.orig_id] = key
        return orig_id_to_key, key_to_node

    def draw_tree_from_root(self, root: Optional[RBNode]):
        """绘制树"""
        self.canvas.delete("all")
        # 不再绘制欢迎文字
        self.showing_welcome = False
        
        # 绘制图例（放在底部）
        legend_y = self.canvas_h - 20
        self.draw_legend(legend_y)
        
        if root is None:
            self.canvas.create_text(self.canvas_w/2, self.canvas_h/2 - 30, 
                                  text="空树", font=("微软雅黑", 14), fill="#9E9E9E")
            return

        pos = self.compute_positions_for_root(root)

        inorder_nodes: List[RBNode] = []
        def inorder_collect(n: Optional[RBNode]):
            if not n:
                return
            inorder_collect(n.left)
            inorder_nodes.append(n)
            inorder_collect(n.right)
        inorder_collect(root)

        node_to_key: Dict[RBNode, str] = {}
        counts: Dict[str,int] = {}
        for node in inorder_nodes:
            base = str(node.val)
            cnt = counts.get(base, 0)
            counts[base] = cnt + 1
            key = f"{base}#{cnt}" if cnt > 0 else base
            node_to_key[node] = key

        # 先绘制边
        def draw_edges(n: Optional[RBNode]):
            if not n:
                return
            k = node_to_key[n]
            cx, cy = pos[k]
            if n.left:
                lk = node_to_key[n.left]
                lx, ly = pos[lk]
                self._draw_connection(cx, cy, lx, ly)
            elif self.show_nil_nodes:
                # 绘制NIL节点（左）
                nil_x = cx - 40
                nil_y = cy + self.level_gap * 0.6
                self._draw_nil_connection(cx, cy, nil_x, nil_y)
                self._draw_nil_node(nil_x, nil_y)
                
            if n.right:
                rk = node_to_key[n.right]
                rx, ry = pos[rk]
                self._draw_connection(cx, cy, rx, ry)
            elif self.show_nil_nodes:
                # 绘制NIL节点（右）
                nil_x = cx + 40
                nil_y = cy + self.level_gap * 0.6
                self._draw_nil_connection(cx, cy, nil_x, nil_y)
                self._draw_nil_node(nil_x, nil_y)
                
            draw_edges(n.left); draw_edges(n.right)
        draw_edges(root)
        
        # 绘制父指针（如果启用）
        if self.show_parent_links:
            self._draw_parent_links(root, node_to_key, pos)

        # 绘制节点
        self.node_vis.clear()
        for node, key in node_to_key.items():
            cx, cy = pos[key]
            # 计算黑高度（如果启用）
            black_height = self._calc_black_height(node) if self.show_black_height else None
            self.draw_tree_node(cx, cy, node, key, black_height)
    
    def _draw_nil_node(self, x: float, y: float):
        """绘制NIL节点"""
        size = 16
        self.canvas.create_rectangle(x - size, y - size/2, x + size, y + size/2,
                                    fill=self.colors["nil_node"], outline="#78909C",
                                    width=1)
        self.canvas.create_text(x, y, text="NIL", font=("Arial", 7, "bold"),
                               fill="white")
    
    def _draw_nil_connection(self, cx: float, cy: float, tx: float, ty: float):
        """绘制到NIL节点的连接线"""
        top = cy + self.node_h/2
        self.canvas.create_line(cx, top, tx, ty - 8, 
                               width=1, fill="#B0BEC5", dash=(3, 3))
    
    def _draw_parent_links(self, root: RBNode, node_to_key: Dict, pos: Dict):
        """绘制父指针（虚线向上指向父节点）"""
        def draw_parent_link(n: Optional[RBNode]):
            if not n or not n.parent:
                return
            k = node_to_key.get(n)
            pk = node_to_key.get(n.parent)
            if k and pk and k in pos and pk in pos:
                cx, cy = pos[k]
                px, py = pos[pk]
                # 绘制弧形父指针
                offset = 15  # 偏移量，避免与子指针重叠
                if cx < px:
                    # 节点在父节点左边
                    self.canvas.create_line(cx + offset, cy - self.node_h/2 - 3, 
                                          px - offset, py + self.node_h/2 + 3,
                                          fill=self.colors["parent_link"], width=1, 
                                          dash=(2, 2), arrow=LAST, arrowshape=(6, 8, 4))
                else:
                    # 节点在父节点右边
                    self.canvas.create_line(cx - offset, cy - self.node_h/2 - 3, 
                                          px + offset, py + self.node_h/2 + 3,
                                          fill=self.colors["parent_link"], width=1, 
                                          dash=(2, 2), arrow=LAST, arrowshape=(6, 8, 4))
            draw_parent_link(n.left)
            draw_parent_link(n.right)
        draw_parent_link(root)
    
    def _calc_black_height(self, node: Optional[RBNode]) -> int:
        """计算节点的黑高度"""
        if node is None:
            return 1  # NIL节点计为1
        # 向下走到叶子，计算黑节点数量
        left_bh = self._calc_black_height(node.left)
        # 如果当前节点是黑色，加1
        return left_bh + (1 if node.color == "B" else 0)

    def draw_tree_node(self, cx: float, cy: float, node: RBNode, key: str, black_height: int = None):
        """绘制单个树节点"""
        left = cx - self.node_w/2
        top = cy - self.node_h/2
        right = cx + self.node_w/2
        bottom = cy + self.node_h/2
        
        is_red = node.color == "R"
        fill_color = self.colors["red_node"] if is_red else self.colors["black_node"]
        text_color = self.colors["text_light"] if not is_red else self.colors["text_dark"]
        
        # 使用圆角矩形效果（通过多边形模拟）
        radius = 6
        rect = self.canvas.create_rectangle(left, top, right, bottom,
                                          fill=fill_color, outline="#E0E0E0",
                                          width=2)
        
        # 节点内部区域分隔（简化设计）
        x1 = left + 24
        x2 = right - 24
        # Tkinter不支持RGBA颜色，使用纯色代替
        line_color = "#FFAAAA" if is_red else "#546E7A"
        self.canvas.create_line(x1, top+4, x1, bottom-4, width=1, fill=line_color)
        self.canvas.create_line(x2, top+4, x2, bottom-4, width=1, fill=line_color)
        
        # 节点值（居中显示）
        txt = self.canvas.create_text(cx, cy, text=str(node.val),
                                    font=("微软雅黑", 11, "bold"), fill=text_color)
        
        # 颜色标识（左侧小区域）
        color_label = self.canvas.create_text(left+12, cy, text=node.color,
                                            font=("微软雅黑", 8, "bold"),
                                            fill="#FFD54F" if is_red else "#B0BEC5")
        
        # 黑高度显示（右侧小区域）
        bh_label = None
        if black_height is not None:
            bh_label = self.canvas.create_text(right-12, cy, text=f"h{black_height}",
                                              font=("Arial", 7),
                                              fill="#FFD54F" if is_red else "#B0BEC5")
        
        self.node_vis[key] = {
            'rect': rect, 
            'text': txt, 
            'cx': cx, 
            'cy': cy, 
            'val': str(node.val),
            'color_label': color_label,
            'bh_label': bh_label
        }

    def start_insert_animated(self):
        """开始动画插入"""
        if self.animating:
            messagebox.showinfo("提示", "当前正在执行动画,请稍候...")
            return
            
        if not self.validate_input():
            return
            
        # 开始动画，移除欢迎文字
        self.showing_welcome = False
        self.animating = True
        self.batch = [p.strip() for p in self.input_var.get().split(",") if p.strip()]
        
        # 使用底部面板显示操作说明
        self.update_operation_info(f"🚀 开始批量插入 {len(self.batch)} 个节点: {', '.join(self.batch)}")
        self.update_case_info("插入流程", "① 按BST规则找到插入位置\n② 插入红色新节点\n③ 检查并修复红黑树性质")
        self.update_property_highlight(4)  # 插入可能违反性质4
        
        # 显示插入伪代码
        self._show_pseudocode_for_operation('insert', 0, "开始插入操作")
        
        self._insert_seq(0)

    def insert_direct(self):
        """直接插入(无动画)"""
        if not self.validate_input():
            return
            
        values = [p.strip() for p in self.input_var.get().split(",") if p.strip()]
        for val in values:
            self.model.insert(val)
            
        self.draw_tree_from_root(clone_tree(self.model.root))
        self.update_status(f"已直接插入节点: {', '.join(values)}")

    def validate_input(self):
        """验证输入"""
        s = self.input_var.get().strip()
        if not s:
            messagebox.showinfo("提示", "请输入数字,用逗号分隔\n例如:10, 5, 20, 15, 30")
            return False
            
        try:
            values = [p.strip() for p in s.split(",") if p.strip()]
            for val in values:
                int(val)
        except ValueError:
            messagebox.showerror("错误", "输入包含非数字内容,请确保只输入数字")
            return False
            
        return True
    
    def _compare_values(self, val1, val2):
        """比较两个值的大小(按整数比较)"""
        try:
            return int(val1) < int(val2)
        except (ValueError, TypeError):
            return str(val1) < str(val2)

    def _insert_seq(self, idx: int):
        """插入序列"""
        if idx >= len(self.batch):
            self.animating = False
            self.update_status("所有插入操作已完成")
            self.update_operation_info(f"✅ 完成！已成功插入 {len(self.batch)} 个节点")
            self.clear_case_info()
            self.update_property_highlight(0)
            self._show_initial_code_hint()  # 恢复初始提示
            return

        val = self.batch[idx]
        inserted_node, path_nodes, events, snapshots = self.model.insert_with_steps(val)

        snap_pre = snapshots[0]
        snap_after_insert = snapshots[1] if len(snapshots) > 1 else None

        pos_pre = self.compute_positions_for_root(snap_pre)
        origid_to_key_pre, _ = self._build_key_maps_from_root(snap_pre)
        
        # 显示插入伪代码
        self._show_pseudocode_for_operation('insert', 4, f"开始插入节点 {val}")

        def highlight_path(i=0):
            if i >= len(path_nodes):
                self.update_status(f"插入 {val}: 定位插入位置")
                self.show_operation_explanation("insert", f"准备插入节点 {val}")
                # 高亮插入位置代码
                if snap_pre is None:
                    self._show_pseudocode_for_operation('insert', 14, f"树为空，{val}成为根节点")
                else:
                    self._show_pseudocode_for_operation('insert', 16, f"将{val}插入到正确位置")
                self.animate_flyin_new(val, snap_after_insert, 
                                     lambda: self._after_insert_events(events, snapshots, idx))
                return
                
            self.wait_if_paused()
            
            node = path_nodes[i]
            node_id = getattr(node, 'id', None)
            key = origid_to_key_pre.get(node_id)
            self.draw_tree_from_root(snap_pre)
            
            if key:
                try:
                    self.canvas.itemconfig(self.node_vis[key]['rect'], 
                                         outline=self.colors["path_highlight"], 
                                         width=3)
                    # 添加搜索光晕
                    self.create_search_halo(key)
                except Exception:
                    pass
            
            # 高亮搜索过程中的代码行
            if self._compare_values(val, node.val):
                self._highlight_line(8)  # if z.val < x.val
                self.code_step_label.config(text=f"▶ {val} < {node.val}，向左子树搜索")
            else:
                self._highlight_line(10)  # else: x = x.right
                self.code_step_label.config(text=f"▶ {val} >= {node.val}，向右子树搜索")
                    
            self.update_status(f"搜索路径: 访问节点 {node.val} (步骤 {i+1})")
            self.window.after(max(100, self.animation_speed), lambda: highlight_path(i+1))

        highlight_path(0)

    def animate_flyin_new(self, val_str: str, snap_after_insert: Optional[RBNode], on_complete):
        """动画:新节点飞入"""
        if not snap_after_insert:
            on_complete()
            return
            
        pos_after = self.compute_positions_for_root(snap_after_insert)
        origid_to_key_after, _ = self._build_key_maps_from_root(snap_after_insert)
        
        # 找到新插入的节点
        candidate_keys = [k for id_, k in origid_to_key_after.items() 
                         if k and k.split('#')[0] == str(val_str)]
        if not candidate_keys:
            candidate_keys = [k for k in pos_after.keys() 
                            if k.split('#')[0] == str(val_str)]
        if not candidate_keys:
            on_complete()
            return
            
        target_key = candidate_keys[-1]
        tx, ty = pos_after[target_key]

        # 起始位置
        sx, sy = self.canvas_w/2, 20
        
        # 创建临时节点
        left = sx - self.node_w/2
        top = sy - self.node_h/2
        right = sx + self.node_w/2
        bottom = sy + self.node_h/2
        
        temp_rect = self.canvas.create_rectangle(left, top, right, bottom,
                                               fill="#FFE0B2", outline="#FF9800",
                                               width=2)
        temp_text = self.canvas.create_text(sx, sy, text=str(val_str),
                                          font=("微软雅黑", 11, "bold"))
        
        # 添加到临时对象列表
        self.temp_objects.extend([temp_rect, temp_text])

        # 动画参数
        steps = 30
        dx = (tx - sx)/steps
        dy = (ty - sy)/steps
        delay = max(10, self.animation_speed // 30)
        
        def step(i=0):
            if i < steps:
                self.wait_if_paused()
                
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
                    # 从临时对象列表中移除
                    self.temp_objects = [obj for obj in self.temp_objects 
                                       if obj not in [temp_rect, temp_text]]
                except Exception:
                    pass
                    
                self.draw_tree_from_root(snap_after_insert)
                try:
                    self.canvas.itemconfig(self.node_vis[target_key]['rect'], 
                                         outline=self.colors["highlight"], 
                                         width=3)
                    # 添加插入完成闪烁
                    self.flash_node(target_key, self.colors["highlight"])
                except Exception:
                    pass
                    
                self.window.after(max(100, self.animation_speed), on_complete)
        step()

    def _animate_single_event(self, before_root: Optional[RBNode], after_root: Optional[RBNode], event: Dict, on_done):
        """动画:单步操作"""
        pos_before = self.compute_positions_for_root(before_root)
        pos_after = self.compute_positions_for_root(after_root)

        self.draw_tree_from_root(before_root)
        origid_to_key_before, key_to_node_before = self._build_key_maps_from_root(before_root)
        origid_to_key_after, key_to_node_after = self._build_key_maps_from_root(after_root)

        # 收集需要移动的节点
        keys_common = set(pos_before.keys()) & set(pos_after.keys())
        moves = []
        for k in keys_common:
            item = self.node_vis.get(k)
            if not item:
                continue
            sx, sy = pos_before[k]
            tx, ty = pos_after[k]
            moves.append((k, item['rect'], item['text'], sx, sy, tx, ty))

        # 使用底部面板显示操作说明（不遮挡画布）
        op_type = event.get('type', '')
        
        if op_type == 'recolor':
            self.update_operation_info("🎨 重着色操作：调整节点颜色以修复红黑树性质")
            self.update_case_info("重着色 (Recolor)", 
                                 "叔叔节点是红色时，将父节点和叔叔染黑，祖父染红，然后向上继续检查")
            # 显示重着色伪代码
            self._show_pseudocode_for_operation('recolor', 3, "执行重着色操作")
            # 显示颜色变化动画
            self.animate_color_change(event, before_root, after_root)
        elif op_type == 'rotate_left':
            self.update_operation_info("🔄 左旋操作：将节点向左下方旋转以调整树结构")
            self.update_case_info("左旋 (Left Rotate)", 
                                 "右子节点成为新父节点，原节点成为左子节点，原右子节点的左子树成为原节点的右子树")
            # 显示左旋伪代码
            self._show_pseudocode_for_operation('rotate_left', 1, "执行LEFT-ROTATE")
            # 显示旋转指示
            self.show_rotation_guide(event, before_root)
        elif op_type == 'rotate_right':
            self.update_operation_info("🔄 右旋操作：将节点向右下方旋转以调整树结构")
            self.update_case_info("右旋 (Right Rotate)", 
                                 "左子节点成为新父节点，原节点成为右子节点，原左子节点的右子树成为原节点的左子树")
            # 显示右旋伪代码
            self._show_pseudocode_for_operation('rotate_right', 1, "执行RIGHT-ROTATE")
            # 显示旋转指示
            self.show_rotation_guide(event, before_root)
        elif op_type == 'root_recolor':
            self.update_operation_info("⬛ 根节点重着色：确保根节点为黑色（性质2）")
            self.update_case_info("根节点着色", "红黑树性质2要求根节点必须是黑色的")
            # 显示根节点重着色
            self._show_pseudocode_for_operation('insert_fixup', 31, "确保根节点为黑色")
        else:
            self.update_operation_info("⚙️ 执行平衡操作")
            self.clear_case_info()

        # 在画布上显示简短的操作指示（不遮挡树，放在顶部中央）
        label_text = {"recolor": "重着色", "rotate_left": "← 左旋", "rotate_right": "右旋 →", 
                     "root_recolor": "根染黑"}.get(op_type, "平衡")
        label_color = {"recolor": "#D32F2F", "rotate_left": "#1976D2", "rotate_right": "#1976D2",
                      "root_recolor": "#388E3C"}.get(op_type, "#388E3C")
        
        label_id = self.canvas.create_text(self.canvas_w/2, 15, text=f"▶ {label_text}",
                                         font=("微软雅黑", 10, "bold"),
                                         fill=label_color)
        self.temp_objects.append(label_id)

        # 执行动画
        frames = 24
        delay = max(10, self.animation_speed // 20)

        def frame_step(f=0):
            if f >= frames:
                self.draw_tree_from_root(after_root)
                # 清理临时对象
                for obj in self.temp_objects:
                    try: 
                        self.canvas.delete(obj)
                    except: 
                        pass
                self.temp_objects.clear()
                self.window.after(max(100, self.animation_speed), on_done)
                return
                
            self.wait_if_paused()
            
            t = (f+1)/frames
            for (k, rect_id, text_id, sx, sy, tx, ty) in moves:
                cur_cx = sx + (tx - sx) * t
                cur_cy = sy + (ty - sy) * t
                
                try:
                    coords = self.canvas.coords(rect_id)
                    if not coords or len(coords) < 4:
                        continue
                    x1, y1, x2, y2 = coords
                    current_cx = (x1 + x2) / 2
                    current_cy = (y1 + y2) / 2
                    
                    dx = cur_cx - current_cx
                    dy = cur_cy - current_cy
                    self.canvas.move(rect_id, dx, dy)
                    self.canvas.move(text_id, dx, dy)
                except Exception:
                    pass
                    
            self.window.after(delay, lambda: frame_step(f+1))
            
        frame_step(0)

    def _animate_events_sequence(self, events: List[Dict], snapshots: List[Optional[RBNode]], insertion_index: int, on_all_done):
        """动画:事件序列"""
        if not events:
            self.clear_case_info()
            on_all_done()
            return

        def step(i=0):
            if i >= len(events):
                self.clear_case_info()
                on_all_done()
                return
                
            self.wait_if_paused()
            
            before_root = snapshots[1 + i]
            after_root = snapshots[2 + i]
            ev = events[i]
            
            # 根据事件类型显示对应的插入修复伪代码行和详细说明
            op_type = ev.get('type', 'unknown')
            if op_type == 'recolor':
                # Case 1: 叔叔是红色，需要重着色
                self._show_pseudocode_for_operation('insert_fixup', 4, f"Case 1: 叔叔是红色，执行重着色")
                self.update_case_info("Case 1: 叔叔是红色", 
                    "① 将父节点染黑\n② 将叔叔节点染黑\n③ 将祖父节点染红\n④ 将当前节点移至祖父，继续向上检查")
            elif op_type == 'rotate_left':
                # Case 2 或 Case 3 的左旋
                self._show_pseudocode_for_operation('insert_fixup', 12, "Case 2/3: 执行左旋")
                self.update_case_info("Case 2/3: 左旋", 
                    "Case 2: 当前节点是右孩子，先左旋转化为Case 3\nCase 3对称: 执行左旋完成修复")
            elif op_type == 'rotate_right':
                # Case 3 的右旋
                self._show_pseudocode_for_operation('insert_fixup', 16, "Case 3: 执行右旋")
                self.update_case_info("Case 3: 右旋", 
                    "当前节点是左孩子，叔叔是黑色:\n① 将父节点染黑\n② 将祖父节点染红\n③ 对祖父节点右旋")
            elif op_type == 'root_recolor':
                self._show_pseudocode_for_operation('insert_fixup', 31, "确保根节点为黑色")
                self.update_case_info("根节点着色", "红黑树性质2: 根节点必须是黑色")
            
            self.update_status(f"修复步骤 {i+1}/{len(events)}: {op_type}")
            self._animate_single_event(before_root, after_root, ev, 
                                     lambda: step(i+1))
        step(0)

    def _after_insert_events(self, events, snapshots, insertion_idx):
        """插入后的事件处理"""
        if not events:
            self.draw_tree_from_root(clone_tree(self.model.root))
            self._show_pseudocode_for_operation('insert', 20, "插入完成，调用修复函数")
            self.window.after(max(100, self.animation_speed), lambda: self._insert_seq(insertion_idx+1))
            return

        # 显示插入修复伪代码
        self._show_pseudocode_for_operation('insert_fixup', 0, "开始修复红黑树性质")

        def done_all():
            self.draw_tree_from_root(clone_tree(self.model.root))
            self.update_status(f"完成插入: {self.batch[insertion_idx]}")
            # 高亮根节点变黑
            self._show_pseudocode_for_operation('insert_fixup', 31, "确保根节点为黑色")
            self.window.after(max(100, self.animation_speed), lambda: self._insert_seq(insertion_idx+1))
            
        self._animate_events_sequence(events, snapshots, insertion_idx, done_all)

    def clear_canvas(self):
        """清空画布"""
        if self.animating:
            messagebox.showinfo("提示", "请等待当前动画完成")
            return
            
        self.model = RBModel()
        self.node_vis.clear()
        self.canvas.delete("all")
        self.showing_welcome = True  # 重置欢迎文字显示状态
        self.draw_instructions()
        self._show_initial_code_hint()  # 重置伪代码面板
        # 重置教育面板
        self.update_operation_info("准备就绪，请输入节点值开始操作")
        self.clear_case_info()
        self.update_property_highlight(0)
        self.update_status("已清空红黑树")

    def back_to_main(self):
        """返回主界面"""
        if messagebox.askyesno("确认", "确定要返回主界面吗?"):
            self.window.destroy()

    def save_structure(self):
        """保存结构"""
        root = self.model.root
        ok = storage.save_tree_to_file(root)
        if ok:
            self.update_status("树结构保存成功")
            messagebox.showinfo("成功", "红黑树结构已保存到文件")

    def load_structure(self):
        """加载结构"""
        if self.animating:
            messagebox.showinfo("提示", "请等待当前动画完成")
            return
            
        tree_dict = storage.load_tree_from_file()
        if not tree_dict:
            messagebox.showinfo("提示", "没有找到保存的树结构文件")
            return
            
        from rbt.rbt_model import RBNode as RBNodeClass
        newroot = storage.tree_dict_to_nodes(tree_dict, RBNodeClass)
        self.model.root = newroot
        self.showing_welcome = False  # 加载结构后不显示欢迎文字
        self.draw_tree_from_root(clone_tree(self.model.root))
        self.update_status("已从文件加载红黑树结构")

    # ===== 新增的动画效果方法 =====
    
    def create_search_halo(self, node_key):
        """创建搜索光晕效果"""
        if node_key not in self.node_vis:
            return
            
        node = self.node_vis[node_key]
        cx, cy = node['cx'], node['cy']
        
        # 创建光晕圆圈
        halo = self.canvas.create_oval(cx-25, cy-25, cx+25, cy+25,
                                     outline=self.colors["search_halo"],
                                     width=2, dash=(5, 2))
        self.temp_objects.append(halo)
        
        # 光晕动画
        def animate_halo(step=0):
            if step < 3:  # 闪烁3次
                if step % 2 == 0:
                    self.canvas.itemconfig(halo, state=HIDDEN)
                else:
                    self.canvas.itemconfig(halo, state=NORMAL)
                self.window.after(200, lambda: animate_halo(step+1))
            else:
                try:
                    self.canvas.delete(halo)
                    self.temp_objects.remove(halo)
                except:
                    pass
                    
        animate_halo()

    def flash_node(self, node_key, color):
        """节点闪烁效果"""
        if node_key not in self.node_vis:
            return
            
        node = self.node_vis[node_key]
        rect = node['rect']
        original_width = 2
        
        def flash(step=0):
            if step < 6:  # 闪烁3次
                if step % 2 == 0:
                    self.canvas.itemconfig(rect, outline=color, width=4)
                else:
                    self.canvas.itemconfig(rect, outline="#E0E0E0", width=original_width)
                self.window.after(150, lambda: flash(step+1))
            else:
                self.canvas.itemconfig(rect, outline="#E0E0E0", width=original_width)
                
        flash()

    def show_operation_explanation(self, operation_type, text):
        """显示操作说明（使用底部面板，不遮挡画布）"""
        # 使用底部教育面板显示操作说明
        self.update_operation_info(text)
        
        # 根据操作类型更新性质高亮
        if operation_type == "insert" and "红色" in text:
            self.update_property_highlight(4)  # 性质4可能被违反
        elif operation_type == "delete":
            self.update_property_highlight(5)  # 性质5可能被违反
        elif operation_type == "fixup":
            pass  # 修复过程中保持当前高亮
        else:
            self.update_property_highlight(0)  # 清除高亮

    def get_operation_explanation(self, operation_type):
        """获取操作说明文本"""
        explanations = {
            'recolor': '颜色调整: 重新着色节点以保持红黑树性质',
            'rotate_left': '左旋操作: 调整树结构保持平衡',
            'rotate_right': '右旋操作: 调整树结构保持平衡',
            'root_recolor': '根节点重着色: 确保根节点为黑色'
        }
        return explanations.get(operation_type, '执行平衡操作')

    def show_rotation_guide(self, event, before_root):
        """显示旋转指示"""
        pivot_id = event.get('x_id')
        if not pivot_id:
            return
            
        origid_to_key, _ = self._build_key_maps_from_root(before_root)
        pivot_key = origid_to_key.get(pivot_id)
        
        if pivot_key and pivot_key in self.node_vis:
            node = self.node_vis[pivot_key]
            cx, cy = node['cx'], node['cy']
            
            # 根据旋转类型显示方向指示
            if event.get('type') == 'rotate_left':
                # 左旋指示 - 逆时针箭头
                arrow = self.canvas.create_line(cx, cy-30, cx-20, cy-10, cx-10, cy-10,
                                              arrow=LAST, fill=self.colors["rotation_guide"],
                                              width=3)
                text = self.canvas.create_text(cx-30, cy-15, text="左旋", 
                                             font=("微软雅黑", 9, "bold"),
                                             fill=self.colors["rotation_guide"])
            else:
                # 右旋指示 - 顺时针箭头  
                arrow = self.canvas.create_line(cx, cy-30, cx+20, cy-10, cx+10, cy-10,
                                              arrow=LAST, fill=self.colors["rotation_guide"],
                                              width=3)
                text = self.canvas.create_text(cx+30, cy-15, text="右旋", 
                                             font=("微软雅黑", 9, "bold"),
                                             fill=self.colors["rotation_guide"])
            
            self.temp_objects.extend([arrow, text])

    def animate_color_change(self, event, before_root, after_root):
        """颜色变化动画"""
        node_id = event.get('node_id')
        if not node_id:
            return
            
        origid_to_key, _ = self._build_key_maps_from_root(before_root)
        node_key = origid_to_key.get(node_id)
        
        if node_key and node_key in self.node_vis:
            node = self.node_vis[node_key]
            rect = node['rect']
            
            # 获取新旧颜色
            old_color = self.canvas.itemcget(rect, "fill")
            new_color = self.colors["red_node"] if event.get('new_color') == 'R' else self.colors["black_node"]
            
            # 颜色过渡动画
            steps = 10
            delay = max(10, self.animation_speed // 30)
            
            def color_transition(step=0):
                if step <= steps:
                    # 计算过渡颜色
                    ratio = step / steps
                    if old_color == self.colors["red_node"] and new_color == self.colors["black_node"]:
                        # 红变黑
                        r = int(255 * (1 - ratio))
                        g = int(82 * (1 - ratio))
                        b = int(82 * (1 - ratio))
                    else:
                        # 黑变红
                        r = int(55 + 200 * ratio)
                        g = int(71 + 184 * ratio)
                        b = int(79 + 173 * ratio)
                    
                    transition_color = f"#{r:02x}{g:02x}{b:02x}"
                    self.canvas.itemconfig(rect, fill=transition_color)
                    self.window.after(delay, lambda: color_transition(step + 1))
                else:
                    # 确保最终颜色正确
                    self.canvas.itemconfig(rect, fill=new_color)
            
            color_transition()

    # ===== 红黑树知识展示方法 =====
    
    def show_rb_insert_knowledge(self):
        """显示红黑树插入知识"""
        knowledge_text = (
            "红黑树插入知识:\n"
            "• 新插入的节点默认为红色\n"
            "• 如果父节点是黑色，插入完成\n"
            "• 如果父节点是红色，需要修复:\n"
            "  - Case 1: 叔叔节点是红色\n"
            "  - Case 2: 叔叔节点是黑色，当前节点是右孩子\n" 
            "  - Case 3: 叔叔节点是黑色，当前节点是左孩子"
        )
        self.show_knowledge_panel(knowledge_text)
    
    def show_rb_delete_knowledge(self):
        """显示红黑树删除知识"""
        knowledge_text = (
            "红黑树删除知识:\n"
            "• 删除红色节点通常不会破坏性质\n"
            "• 删除黑色节点需要修复平衡\n"
            "• 修复过程涉及兄弟节点的颜色判断\n"
            "• 可能需要重新着色和旋转操作"
        )
        self.show_knowledge_panel(knowledge_text)
    
    def show_rb_delete_fixup_knowledge(self):
        """显示红黑树删除修复知识"""
        knowledge_text = (
            "删除修复的四种情况:\n"
            "• Case 1: 兄弟节点是红色\n"
            "• Case 2: 兄弟节点是黑色，兄弟的两个子节点都是黑色\n"
            "• Case 3: 兄弟节点是黑色，兄弟的左孩子红色，右孩子黑色\n"
            "• Case 4: 兄弟节点是黑色，兄弟的右孩子红色"
        )
        self.show_knowledge_panel(knowledge_text)
    
    def show_rb_color_knowledge(self):
        """显示红黑树颜色知识"""
        knowledge_text = (
            "红黑树颜色性质:\n"
            "1. 每个节点是红色或黑色\n"
            "2. 根节点是黑色的\n"
            "3. 所有叶子节点(NIL)是黑色的\n"
            "4. 红色节点的两个子节点都是黑色的\n"
            "5. 从任一节点到其每个叶子的所有路径都包含相同数目的黑色节点"
        )
        self.show_knowledge_panel(knowledge_text)
    
    def show_rb_rotation_knowledge(self, direction):
        """显示红黑树旋转知识"""
        if direction == "左旋":
            knowledge_text = (
                "左旋操作:\n"
                "• 以某个节点为支点进行旋转\n"
                "• 右子节点成为新的父节点\n"
                "• 原父节点成为新父节点的左子节点\n"
                "• 新父节点的左子树成为原父节点的右子树"
            )
        else:
            knowledge_text = (
                "右旋操作:\n"
                "• 以某个节点为支点进行旋转\n"
                "• 左子节点成为新的父节点\n"
                "• 原父节点成为新父节点的右子节点\n"
                "• 新父节点的右子树成为原父节点的左子树"
            )
        self.show_knowledge_panel(knowledge_text)
    
    def show_knowledge_panel(self, text):
        """显示知识面板（使用底部教育面板，不遮挡画布）"""
        # 使用底部的Case说明面板显示知识
        lines = text.strip().split('\n')
        if lines:
            title = lines[0].rstrip(':')
            content = '\n'.join(lines[1:]) if len(lines) > 1 else ""
            self.update_case_info(title, content.strip())


if __name__ == '__main__':
    w = Tk()
    w.title("红黑树可视化演示系统")
    w.geometry("1350x750")
    
    try:
        w.iconbitmap("rbt_icon.ico")
    except:
        pass
        
    RBTVisualizer(w)
    w.mainloop()