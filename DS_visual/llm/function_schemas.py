"""
Function schemas for LLM function-calling.
Provides STACK_FUNCTIONS, SEQUENCE_FUNCTIONS and a convenience getter get_function_schemas()
so other modules (e.g. chat_window) can import get_function_schemas().
"""
LINKED_LIST_FUNCTIONS = [
    {
        "name": "linked_list_insert_first",
        "description": "在单链表头部插入元素。参数 value 可以是字符串或数字。",
        "parameters": {
            "type": "object",
            "properties": {
                "value": {"type": ["string", "number"], "description": "插入的值"}
            },
            "required": ["value"]
        }
    },
    {
        "name": "linked_list_insert_last",
        "description": "在单链表尾部插入元素。参数 value 可以是字符串或数字。",
        "parameters": {
            "type": "object",
            "properties": {
                "value": {"type": ["string", "number"], "description": "插入的值"}
            },
            "required": ["value"]
        }
    },
    {
        "name": "linked_list_insert_at",
        "description": "在单链表指定位置插入元素。index 使用 0-based，参数 index 和 value。",
        "parameters": {
            "type": "object",
            "properties": {
                "index": {"type": "number", "description": "插入位置 (0-based)"},
                "value": {"type": ["string", "number"], "description": "插入的值"}
            },
            "required": ["index", "value"]
        }
    },
    {
        "name": "linked_list_delete_at",
        "description": "删除单链表指定位置的元素。参数 index (0-based)。",
        "parameters": {
            "type": "object",
            "properties": {
                "index": {"type": "number", "description": "删除位置 (0-based)"}
            },
            "required": ["index"]
        }
    },
    {
        "name": "linked_list_delete_value",
        "description": "按数值删除单链表中第一个匹配的节点。如果找到该值则删除，否则提示未找到。",
        "parameters": {
            "type": "object",
            "properties": {
                "value": {"type": ["string", "number"], "description": "要删除的值"}
            },
            "required": ["value"]
        }
    },
    {
        "name": "linked_list_insert_before",
        "description": "在单链表中第一个值为target_value的节点前面插入新值new_value。",
        "parameters": {
            "type": "object",
            "properties": {
                "target_value": {"type": ["string", "number"], "description": "目标节点的值，在此节点前面插入"},
                "new_value": {"type": ["string", "number"], "description": "要插入的新值"}
            },
            "required": ["target_value", "new_value"]
        }
    },
    {
        "name": "linked_list_insert_after",
        "description": "在单链表中第一个值为target_value的节点后面插入新值new_value。",
        "parameters": {
            "type": "object",
            "properties": {
                "target_value": {"type": ["string", "number"], "description": "目标节点的值，在此节点后面插入"},
                "new_value": {"type": ["string", "number"], "description": "要插入的新值"}
            },
            "required": ["target_value", "new_value"]
        }
    },
    {
        "name": "linked_list_insert_between",
        "description": "在单链表中第一个值为value_a的节点和第一个值为value_b的节点之间插入新值new_value。要求value_a在value_b前面。",
        "parameters": {
            "type": "object",
            "properties": {
                "value_a": {"type": ["string", "number"], "description": "前面节点的值"},
                "value_b": {"type": ["string", "number"], "description": "后面节点的值"},
                "new_value": {"type": ["string", "number"], "description": "要插入的新值"}
            },
            "required": ["value_a", "value_b", "new_value"]
        }
    },
    {
        "name": "linked_list_search",
        "description": "在单链表中查找指定值的节点，带有动画效果展示查找过程。",
        "parameters": {
            "type": "object",
            "properties": {
                "value": {"type": ["string", "number"], "description": "要查找的值"}
            },
            "required": ["value"]
        }
    },
    {
        "name": "linked_list_reverse",
        "description": "反转/逆置单链表，将链表中所有节点的顺序颠倒，带有动画效果。",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "linked_list_clear",
        "description": "清空单链表（删除所有节点）。无参数。",
        "parameters": {"type": "object", "properties": {}}
    },
    {
        "name": "linked_list_batch_create",
        "description": "批量创建单链表（按顺序插入）。参数 values 为数组或逗号分隔字符串。",
        "parameters": {
            "type": "object",
            "properties": {
                "values": {
                    "type": ["array", "string"],
                    "items": {"type": ["string", "number"]},
                    "description": "按顺序插入的元素列表，或逗号分隔字符串"
                }
            },
            "required": ["values"]
        }
    },
    {
        "name": "linked_list_get_state",
        "description": "获取当前单链表的内容（用于模型确认或展示）。",
        "parameters": {"type": "object", "properties": {}}
    }
]

STACK_FUNCTIONS = [
    {
        "name": "stack_push",
        "description": "将一个值入栈并触发可视化动画。参数 value 可以是字符串或数字。",
        "parameters": {
            "type": "object",
            "properties": {
                "value": {"type": ["string", "number"], "description": "要入栈的值"}
            },
            "required": ["value"]
        }
    },
    {
        "name": "stack_pop",
        "description": "出栈（从栈顶移除一个元素），触发可视化动画。无参数。",
        "parameters": {"type": "object", "properties": {}}
    },
    {
        "name": "stack_clear",
        "description": "清空栈（立即把栈变为空）。",
        "parameters": {"type": "object", "properties": {}}
    },
    {
        "name": "stack_batch_create",
        "description": "批量创建栈元素并演示插入动画。参数 values 是一个数组或逗号分隔的字符串。",
        "parameters": {
            "type": "object",
            "properties": {
                "values": {
                    "type": ["array", "string"],
                    "items": {"type": ["string", "number"]},
                    "description": "要按顺序入栈的元素列表，或逗号分隔字符串"
                }
            },
            "required": ["values"]
        }
    },
    {
        "name": "stack_get_state",
        "description": "获取当前栈的内容（用于模型确认或展示）。",
        "parameters": {"type": "object", "properties": {}}
    },
    {
        "name": "stack_eval_postfix",
        "description": "后缀表达式求值演示。使用栈来演示后缀（逆波兰）表达式的求值过程。表达式中的元素用空格分隔，支持 + - * / % ^ 运算符。例如 '3 4 + 2 *' 表示 (3+4)*2=14。",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string", 
                    "description": "后缀表达式，元素用空格分隔。例如: '3 4 +' 表示 3+4, '3 4 + 2 *' 表示 (3+4)*2, '5 1 2 + 4 * + 3 -' 表示 5+((1+2)*4)-3"
                }
            },
            "required": ["expression"]
        }
    },
    {
        "name": "stack_bracket_match",
        "description": "括号匹配检验演示。使用栈来演示括号匹配检验算法。支持三种括号: 圆括号()、方括号[]、花括号{}。会逐字符扫描表达式，遇到左括号入栈，遇到右括号与栈顶匹配并出栈，最后检查栈是否为空来判断是否匹配成功。",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string", 
                    "description": "包含括号的表达式。例如: '{a+(b-c)*2}' 表示一个括号匹配成功的表达式, '[(a+b)*(c-d)]' 同样是匹配的, 而 '{a+(b-c]*2}' 则是括号不匹配的"
                }
            },
            "required": ["expression"]
        }
    },
    {
        "name": "stack_dfs",
        "description": "DFS深度优先搜索演示。打开一个新窗口，使用栈来演示图的深度优先遍历算法。可以可视化观察DFS的'深度潜入、遇到死胡同回溯'的特性，以及栈在DFS中的作用。",
        "parameters": {
            "type": "object",
            "properties": {
                "vertex_count": {
                    "type": "number",
                    "description": "图的顶点数量，默认为7，范围5-10"
                },
                "branch_factor": {
                    "type": "number",
                    "description": "每个节点的分支因子（出边数），默认为2，范围1-3"
                },
                "start_vertex": {
                    "type": "string",
                    "description": "DFS起始顶点，默认为'A'"
                }
            },
            "required": []
        }
    }
]

SEQUENCE_FUNCTIONS = [
    {
        "name": "sequence_insert_first",
        "description": "在顺序表头部插入元素。参数 value 可为字符串或数字。",
        "parameters": {
            "type": "object",
            "properties": {
                "value": {"type": ["string", "number"], "description": "插入的值"}
            },
            "required": ["value"]
        }
    },
    {
        "name": "sequence_insert_last",
        "description": "在顺序表尾部插入元素。参数 value 可为字符串或数字。",
        "parameters": {
            "type": "object",
            "properties": {
                "value": {"type": ["string", "number"], "description": "插入的值"}
            },
            "required": ["value"]
        }
    },
    {
        "name": "sequence_insert_at",
        "description": "在指定位置插入元素。位置使用 0-based 索引（或在文档中说明为 1-based）。参数 index (number) 和 value。",
        "parameters": {
            "type": "object",
            "properties": {
                "index": {"type": "number", "description": "要插入的位置（0-based）"},
                "value": {"type": ["string", "number"], "description": "插入的值"}
            },
            "required": ["index", "value"]
        }
    },
    {
        "name": "sequence_delete_at",
        "description": "删除指定位置的元素（0-based 索引）。参数 index。",
        "parameters": {
            "type": "object",
            "properties": {
                "index": {"type": "number", "description": "要删除的位置（0-based）"}
            },
            "required": ["index"]
        }
    },
    {
        "name": "sequence_clear",
        "description": "清空顺序表（删除所有元素）。无参数。",
        "parameters": {"type": "object", "properties": {}}
    },
    {
        "name": "sequence_batch_create",
        "description": "批量创建顺序表元素并演示插入动画。parameters: values 是数组或逗号分隔字符串。",
        "parameters": {
            "type": "object",
            "properties": {
                "values": {
                    "type": ["array", "string"],
                    "items": {"type": ["string", "number"]},
                    "description": "要按顺序插入的元素列表，或逗号分隔字符串"
                }
            },
            "required": ["values"]
        }
    },
    {
        "name": "sequence_get_state",
        "description": "获取当前顺序表的内容（用于模型确认或展示）。",
        "parameters": {"type": "object", "properties": {}}
    },
    {
        "name": "sequence_reverse",
        "description": "逆置顺序表，将所有元素前后翻转。例如 [1,2,3,4,5] 变成 [5,4,3,2,1]。会触发可视化动画演示双指针逆置算法。无参数。",
        "parameters": {"type": "object", "properties": {}}
    },
    {
        "name": "sequence_bubble_sort",
        "description": "对顺序表执行冒泡排序，并展示排序过程的可视化动画。元素必须是数值类型。无参数。",
        "parameters": {"type": "object", "properties": {}}
    },
    {
        "name": "sequence_insertion_sort",
        "description": "对顺序表执行直接插入排序，并展示排序过程的可视化动画。元素必须是数值类型。无参数。",
        "parameters": {"type": "object", "properties": {}}
    },
    {
        "name": "sequence_quick_sort",
        "description": "对顺序表执行快速排序，并展示排序过程的可视化动画。元素必须是数值类型。无参数。",
        "parameters": {"type": "object", "properties": {}}
    }
]

# AVL树函数定义
AVL_FUNCTIONS = [
    {
        "name": "avl_insert",
        "description": "在AVL树中插入一个或多个数值，并展示插入动画（包括搜索路径高亮和旋转过程）。参数 values 可以是单个数字、逗号分隔的字符串或数组。",
        "parameters": {
            "type": "object",
            "properties": {
                "values": {
                    "type": ["array", "string", "number"],
                    "items": {"type": "number"},
                    "description": "要插入的数值，可以是单个数字、逗号分隔字符串（如'10,20,30'）或数组"
                }
            },
            "required": ["values"]
        }
    },
    {
        "name": "avl_delete",
        "description": "从AVL树中删除一个或多个数值，并展示删除动画（包括搜索路径高亮和旋转过程）。参数 values 可以是单个数字、逗号分隔的字符串或数组。",
        "parameters": {
            "type": "object",
            "properties": {
                "values": {
                    "type": ["array", "string", "number"],
                    "items": {"type": "number"},
                    "description": "要删除的数值，可以是单个数字、逗号分隔字符串或数组"
                }
            },
            "required": ["values"]
        }
    },
    {
        "name": "avl_search",
        "description": "在AVL树中查找一个或多个数值，并展示查找动画（显示搜索路径高亮，找到时节点变绿，未找到时显示提示）。参数 values 可以是单个数字、逗号分隔的字符串或数组。",
        "parameters": {
            "type": "object",
            "properties": {
                "values": {
                    "type": ["array", "string", "number"],
                    "items": {"type": "number"},
                    "description": "要查找的数值，可以是单个数字、逗号分隔字符串或数组"
                }
            },
            "required": ["values"]
        }
    },
    {
        "name": "avl_clear",
        "description": "清空AVL树（删除所有节点，重置为空树）。无参数。",
        "parameters": {"type": "object", "properties": {}}
    },
    {
        "name": "avl_batch_create",
        "description": "批量创建AVL树。会先清空现有树，然后依次插入所有数值并展示动画。参数 values 可以是逗号分隔的字符串或数组。",
        "parameters": {
            "type": "object",
            "properties": {
                "values": {
                    "type": ["array", "string"],
                    "items": {"type": "number"},
                    "description": "要按顺序插入的数值列表，或逗号分隔字符串"
                }
            },
            "required": ["values"]
        }
    },
    {
        "name": "avl_get_state",
        "description": "获取当前AVL树的结构信息（用于模型确认或展示）。返回树的节点信息。",
        "parameters": {"type": "object", "properties": {}}
    }
]

# 散列表函数定义
HASHTABLE_FUNCTIONS = [
    {
        "name": "hashtable_insert",
        "description": "在散列表中插入一个值，并展示插入过程动画（包括散列计算和冲突处理）。参数 value 是要插入的整数。",
        "parameters": {
            "type": "object",
            "properties": {
                "value": {
                    "type": ["string", "number"],
                    "description": "要插入的整数值"
                }
            },
            "required": ["value"]
        }
    },
    {
        "name": "hashtable_find",
        "description": "在散列表中查找一个值，并展示查找过程动画。参数 value 是要查找的整数。",
        "parameters": {
            "type": "object",
            "properties": {
                "value": {
                    "type": ["string", "number"],
                    "description": "要查找的整数值"
                }
            },
            "required": ["value"]
        }
    },
    {
        "name": "hashtable_delete",
        "description": "从散列表中删除一个值，并展示删除过程动画。参数 value 是要删除的整数。",
        "parameters": {
            "type": "object",
            "properties": {
                "value": {
                    "type": ["string", "number"],
                    "description": "要删除的整数值"
                }
            },
            "required": ["value"]
        }
    },
    {
        "name": "hashtable_clear",
        "description": "清空散列表（删除所有元素）。无参数。",
        "parameters": {"type": "object", "properties": {}}
    },
    {
        "name": "hashtable_batch_create",
        "description": "批量创建散列表。会先清空现有表，然后依次插入所有值并展示动画。参数 values 可以是逗号分隔的字符串或数组。",
        "parameters": {
            "type": "object",
            "properties": {
                "values": {
                    "type": ["array", "string"],
                    "items": {"type": "number"},
                    "description": "要按顺序插入的整数列表，或逗号/空格分隔的字符串，如 '23, 17, 35, 8'"
                }
            },
            "required": ["values"]
        }
    },
    {
        "name": "hashtable_get_state",
        "description": "获取当前散列表的状态信息（包括容量、大小、负载因子、存储的值等）。用于模型确认或展示。",
        "parameters": {"type": "object", "properties": {}}
    },
    {
        "name": "hashtable_resize",
        "description": "调整散列表的容量。参数 capacity 是新的容量值。",
        "parameters": {
            "type": "object",
            "properties": {
                "capacity": {
                    "type": ["string", "number"],
                    "description": "新的散列表容量（正整数）"
                }
            },
            "required": ["capacity"]
        }
    },
    {
        "name": "hashtable_switch",
        "description": "切换散列表的冲突处理方法。在开放寻址法和拉链法之间切换。无参数。",
        "parameters": {"type": "object", "properties": {}}
    },
    {
        "name": "hashtable_set_hash",
        "description": "设置散列表的散列函数。参数 expression 是散列函数表达式，如 'x % 7' 或 '(x * 2 + 1) % capacity'。可选参数 rebuild 指定是否重建表（默认 false）。",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "散列函数表达式，如 'x % 7'、'(x * 2 + 1) % capacity'。支持变量 x（输入值）和 capacity（表容量）"
                },
                "rebuild": {
                    "type": "boolean",
                    "description": "是否重建散列表（默认 false）"
                }
            },
            "required": ["expression"]
        }
    }
]

# B+ 树函数定义
BPLUSTREE_FUNCTIONS = [
    {
        "name": "bplustree_insert",
        "description": "在B+树中插入一个或多个键值，并展示插入和分裂动画。参数 keys 可以是单个数字、逗号分隔的字符串或数组。例如：'10, 20, 30' 或 [5, 15, 25]",
        "parameters": {
            "type": "object",
            "properties": {
                "keys": {
                    "type": ["array", "string", "number"],
                    "items": {"type": "number"},
                    "description": "要插入的键值，可以是单个数字、逗号分隔字符串（如'10,20,30'）或数组"
                }
            },
            "required": ["keys"]
        }
    },
    {
        "name": "bplustree_search",
        "description": "在B+树中查找一个键值。返回是否找到该键。参数 key 是要查找的键值。",
        "parameters": {
            "type": "object",
            "properties": {
                "key": {
                    "type": ["string", "number"],
                    "description": "要查找的键值"
                }
            },
            "required": ["key"]
        }
    },
    {
        "name": "bplustree_clear",
        "description": "清空B+树（删除所有键值，重置为空树）。无参数。",
        "parameters": {"type": "object", "properties": {}}
    },
    {
        "name": "bplustree_batch_create",
        "description": "批量创建B+树。会先清空现有树，然后依次插入所有键值并展示动画。参数 keys 可以是逗号分隔的字符串或数组。",
        "parameters": {
            "type": "object",
            "properties": {
                "keys": {
                    "type": ["array", "string"],
                    "items": {"type": "number"},
                    "description": "要按顺序插入的键值列表，或逗号分隔字符串"
                }
            },
            "required": ["keys"]
        }
    },
    {
        "name": "bplustree_get_state",
        "description": "获取当前B+树的状态信息（包括所有键值、节点数量、树高、叶节点数量等）。用于模型确认或展示。",
        "parameters": {"type": "object", "properties": {}}
    }
]

# Trie (字典树) 函数定义
TRIE_FUNCTIONS = [
    {
        "name": "trie_insert",
        "description": "在Trie树中插入一个或多个单词，并展示逐字符插入动画。参数 words 可以是单个单词、逗号分隔的字符串或数组。例如：'apple, app, application' 或 ['hello', 'world']",
        "parameters": {
            "type": "object",
            "properties": {
                "words": {
                    "type": ["array", "string"],
                    "items": {"type": "string"},
                    "description": "要插入的单词，可以是单个单词、逗号分隔字符串（如'apple,app,bat'）或数组"
                }
            },
            "required": ["words"]
        }
    },
    {
        "name": "trie_search",
        "description": "在Trie树中查找一个单词，并展示逐字符查找动画（显示搜索路径高亮，找到时节点变绿，未找到时显示红色提示）。参数 word 是要查找的单词。",
        "parameters": {
            "type": "object",
            "properties": {
                "word": {
                    "type": "string",
                    "description": "要查找的单词"
                }
            },
            "required": ["word"]
        }
    },
    {
        "name": "trie_clear",
        "description": "清空Trie树（删除所有单词，重置为空树）。无参数。",
        "parameters": {"type": "object", "properties": {}}
    },
    {
        "name": "trie_batch_create",
        "description": "批量创建Trie树。会先清空现有树，然后依次插入所有单词并展示动画。参数 words 可以是逗号分隔的字符串或数组。",
        "parameters": {
            "type": "object",
            "properties": {
                "words": {
                    "type": ["array", "string"],
                    "items": {"type": "string"},
                    "description": "要按顺序插入的单词列表，或逗号分隔字符串"
                }
            },
            "required": ["words"]
        }
    },
    {
        "name": "trie_get_state",
        "description": "获取当前Trie树的状态信息（包括已存储的所有单词列表、单词数量、节点数量）。用于模型确认或展示。",
        "parameters": {"type": "object", "properties": {}}
    }
]

# 红黑树函数定义
RBT_FUNCTIONS = [
    {
        "name": "rbt_insert",
        "description": "在红黑树中插入一个或多个数值，并展示插入动画（包括搜索路径高亮、颜色调整和旋转过程）。参数 values 可以是单个数字、逗号分隔的字符串或数组。",
        "parameters": {
            "type": "object",
            "properties": {
                "values": {
                    "type": ["array", "string", "number"],
                    "items": {"type": "number"},
                    "description": "要插入的数值，可以是单个数字、逗号分隔字符串（如'10,20,30'）或数组"
                }
            },
            "required": ["values"]
        }
    },
    {
        "name": "rbt_delete",
        "description": "从红黑树中删除一个数值，并展示删除动画（包括搜索路径高亮、删除过程和修复操作）。参数 value 是要删除的单个数字。",
        "parameters": {
            "type": "object",
            "properties": {
                "value": {
                    "type": ["string", "number"],
                    "description": "要删除的数值"
                }
            },
            "required": ["value"]
        }
    },
    {
        "name": "rbt_search",
        "description": "在红黑树中查找一个或多个数值，并展示查找动画（显示搜索路径高亮，找到时节点变绿，未找到时显示提示）。参数 values 可以是单个数字、逗号分隔的字符串或数组。",
        "parameters": {
            "type": "object",
            "properties": {
                "values": {
                    "type": ["array", "string", "number"],
                    "items": {"type": "number"},
                    "description": "要查找的数值，可以是单个数字、逗号分隔字符串或数组"
                }
            },
            "required": ["values"]
        }
    },
    {
        "name": "rbt_clear",
        "description": "清空红黑树（删除所有节点，重置为空树）。无参数。",
        "parameters": {"type": "object", "properties": {}}
    },
    {
        "name": "rbt_batch_create",
        "description": "批量创建红黑树。会先清空现有树，然后依次插入所有数值并展示动画。参数 values 可以是逗号分隔的字符串或数组。",
        "parameters": {
            "type": "object",
            "properties": {
                "values": {
                    "type": ["array", "string"],
                    "items": {"type": "number"},
                    "description": "要按顺序插入的数值列表，或逗号分隔字符串"
                }
            },
            "required": ["values"]
        }
    },
    {
        "name": "rbt_get_state",
        "description": "获取当前红黑树的结构信息（用于模型确认或展示）。返回树的节点信息，包括颜色。",
        "parameters": {"type": "object", "properties": {}}
    }
]

def get_function_schemas(kind: str = "stack"):
    """
    返回 function schema 列表。
    kind:
      - "stack": 仅栈
      - "sequence": 仅顺序表
      - "linked_list": 仅单链表
      - "avl": 仅AVL树
      - "rbt": 仅红黑树
      - "trie": 仅Trie字典树
      - "bplustree": 仅B+树
      - "hashtable": 仅散列表
      - "all": 全部
    """
    if kind == "stack":
        return STACK_FUNCTIONS
    if kind == "sequence":
        return SEQUENCE_FUNCTIONS
    if kind == "linked_list":
        return LINKED_LIST_FUNCTIONS
    if kind == "avl":
        return AVL_FUNCTIONS
    if kind == "rbt":
        return RBT_FUNCTIONS
    if kind == "trie":
        return TRIE_FUNCTIONS
    if kind == "bplustree":
        return BPLUSTREE_FUNCTIONS
    if kind == "hashtable":
        return HASHTABLE_FUNCTIONS
    if kind == "all":
        # 合并并返回
        return STACK_FUNCTIONS + SEQUENCE_FUNCTIONS + LINKED_LIST_FUNCTIONS + AVL_FUNCTIONS + RBT_FUNCTIONS + TRIE_FUNCTIONS + BPLUSTREE_FUNCTIONS + HASHTABLE_FUNCTIONS
    # 默认回退为 stack
    return STACK_FUNCTIONS
