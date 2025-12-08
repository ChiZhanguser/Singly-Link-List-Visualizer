# BST 删除操作伪代码

## 主删除函数：DELETE(val)

```
FUNCTION DELETE(val):
    // 第一步：查找要删除的节点
    node, path ← SEARCH_WITH_PATH(val)
    
    IF node is NULL THEN
        RETURN (False, path)  // 未找到节点
    END IF
    
    // 第二步：执行删除操作
    success ← DELETE_NODE(node)
    RETURN (success, path)
END FUNCTION
```

## 核心删除函数：DELETE_NODE(node)

```
FUNCTION DELETE_NODE(node):
    // 边界检查
    IF node is NULL THEN
        RETURN False
    END IF
    
    // 情况1：叶子节点（无子节点）
    IF node.left is NULL AND node.right is NULL THEN
        IF node.parent is NULL THEN
            root ← NULL  // 删除的是根节点
        ELSE
            IF node is node.parent.left THEN
                node.parent.left ← NULL
            ELSE
                node.parent.right ← NULL
            END IF
        END IF
    
    // 情况2：只有右子节点
    ELSE IF node.left is NULL THEN
        TRANSPLANT(node, node.right)
    
    // 情况3：只有左子节点
    ELSE IF node.right is NULL THEN
        TRANSPLANT(node, node.left)
    
    // 情况4：有两个子节点
    ELSE
        // 找到右子树中的最小节点（后继节点）
        successor ← FIND_MIN(node.right)
        
        // 如果后继节点不是被删除节点的直接右子节点
        IF successor ≠ node.right THEN
            // 先用后继节点的右子节点替换后继节点
            TRANSPLANT(successor, successor.right)
            // 将后继节点的右指针指向被删除节点的右子树
            successor.right ← node.right
            IF successor.right ≠ NULL THEN
                successor.right.parent ← successor
            END IF
        END IF
        
        // 用后继节点替换被删除节点
        TRANSPLANT(node, successor)
        // 将后继节点的左指针指向被删除节点的左子树
        successor.left ← node.left
        IF successor.left ≠ NULL THEN
            successor.left.parent ← successor
        END IF
    END IF
    
    RETURN True
END FUNCTION
```

## 辅助函数：TRANSPLANT(u, v)

```
FUNCTION TRANSPLANT(u, v):
    // 用节点v替换节点u在树中的位置
    
    // 如果u是根节点
    IF u.parent is NULL THEN
        root ← v
    ELSE
        // 更新u的父节点指向v
        IF u is u.parent.left THEN
            u.parent.left ← v
        ELSE
            u.parent.right ← v
        END IF
    END IF
    
    // 更新v的父节点指针
    IF v ≠ NULL THEN
        v.parent ← u.parent
    END IF
END FUNCTION
```

## 辅助函数：FIND_MIN(node)

```
FUNCTION FIND_MIN(node):
    cur ← node
    
    // 一直向左走，找到最小节点
    WHILE cur.left ≠ NULL DO
        cur ← cur.left
    END WHILE
    
    RETURN cur
END FUNCTION
```

## 辅助函数：SEARCH_WITH_PATH(val)

```
FUNCTION SEARCH_WITH_PATH(val):
    path ← []  // 记录搜索路径
    cur ← root
    
    WHILE cur ≠ NULL DO
        path.APPEND(cur)
        
        cmp ← COMPARE_VALUES(val, cur.val)
        
        IF cmp = 0 THEN
            RETURN (cur, path)  // 找到节点
        ELSE IF cmp < 0 THEN
            cur ← cur.left
        ELSE
            cur ← cur.right
        END IF
    END WHILE
    
    RETURN (NULL, path)  // 未找到
END FUNCTION
```

## 删除流程总结

```
删除节点流程：
1. 查找目标节点
   └─ 如果不存在，返回失败

2. 根据子节点情况处理：
   ├─ 情况1：叶子节点
   │  └─ 直接删除，更新父节点指针
   │
   ├─ 情况2：只有一个子节点
   │  └─ 用子节点替换当前节点（TRANSPLANT）
   │
   └─ 情况3：有两个子节点
      ├─ 找到右子树的最小节点（后继节点）
      ├─ 如果后继节点不是直接右子节点：
      │  ├─ 用后继节点的右子节点替换后继节点
      │  └─ 将后继节点的右指针指向原右子树
      ├─ 用后继节点替换被删除节点
      └─ 将后继节点的左指针指向原左子树
```

## 时间复杂度

- **查找节点**：O(h)，其中 h 是树的高度
- **删除操作**：O(h)
- **总体复杂度**：O(h)
  - 最坏情况：O(n)，当树退化为链表时
  - 平均情况：O(log n)，当树平衡时

