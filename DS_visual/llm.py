import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from typing import List, Dict, Any

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 提示词：让LLM生成直接操作模型的Python代码
CODE_PROMPT = """
你需要将用户的自然语言描述转换为操作数据结构的Python代码片段。
可用数据结构类：
- BSTModel：二叉搜索树，支持 insert(value) 方法
- AVLModel：平衡二叉树，支持 insert(value) 方法
- StackModel：栈，支持 push(value) 方法
- SequenceListModel：顺序表，支持 append(value) 方法

可用可视化函数：
- visualize_bst(model)：显示BST可视化窗口
- visualize_avl(model)：显示AVL可视化窗口
- visualize_stack(model)：显示栈可视化窗口
- visualize_list(model)：显示顺序表可视化窗口

输出要求：
1. 只返回可执行的Python代码，不包含解释文字
2. 代码中需先创建模型实例，再操作数据，最后调用可视化函数
3. 自动生成合理的变量名（如未指定）
4. 数值保持原样，列表直接转换为Python列表

示例：
用户输入："创建一个包含[5,3,7,2,4]的二叉搜索树"
输出：
from binary_tree.bst.bst_model import BSTModel
from binary_tree.bst.bst_visual import visualize_bst

# 创建BST实例
bst = BSTModel()
# 插入数据
for val in [5,3,7,2,4]:
    bst.insert(val)
# 可视化
visualize_bst(bst)
"""

def natural_language_to_code(text: str) -> str:
    """将自然语言转换为可执行的Python代码"""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": CODE_PROMPT},
                {"role": "user", "content": text}
            ],
            temperature=0.2  # 降低随机性，确保代码稳定性
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"LLM转换失败: {str(e)}")
        return ""