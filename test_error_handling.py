# test_error_handling.py
import unittest
from DS_visual.trie.trie_model import TrieModel
from DS_visual.linked_list.linked_list_model import _NodeList
from DS_visual.stack.stack_model import StackModel
from DS_visual.binary_tree.bst.bst_model import BSTModel
from DS_visual.hashtable.hashtable_model import HashTableModel

class TestErrorHandling(unittest.TestCase):
    """错误处理测试"""
    
    def test_linked_list_invalid_index(self):
        """测试链表无效索引处理"""
        linked_list = _NodeList([10, 20, 30])
        
        # 负索引越界
        with self.assertRaises(IndexError):
            _ = linked_list[-4]
        
        # 正索引越界
        with self.assertRaises(IndexError):
            _ = linked_list[3]
        
        # 弹出无效索引
        with self.assertRaises(IndexError):
            linked_list.pop(3)
        
        # 空链表弹出
        empty_list = _NodeList()
        with self.assertRaises(IndexError):
            empty_list.pop()
    
    def test_hashtable_invalid_capacity(self):
        """测试哈希表无效容量处理"""
        with self.assertRaises(ValueError):
            HashTableModel(capacity=0)
        
        with self.assertRaises(ValueError):
            HashTableModel(capacity=-10)
    
    def test_stack_full_behavior(self):
        """测试栈满时的行为"""
        stack = StackModel(capacity=3)
        
        # 填满栈
        stack.push(1)
        stack.push(2)
        stack.push(3)
        
        # 尝试继续推入
        result = stack.push(4)
        self.assertFalse(result)
        # 验证栈大小不变
        self.assertEqual(len(stack), 3)
    
    def test_bst_delete_nonexistent(self):
        """测试BST删除不存在节点"""
        bst = BSTModel()
        bst.insert(10)
        
        # 删除None
        result = bst.delete_node(None)
        self.assertFalse(result)
    
    def test_bst_compare_uncomparable(self):
        """测试BST比较不可比较类型"""
        bst = BSTModel()
        
        # 尝试比较不可直接比较的类型，但应该回退到字符串比较
        result = bst.compare_values({}, [])
        # 只要不抛出异常，并且返回一个有效结果（-1, 0, 1），测试就通过
        self.assertIn(result, [-1, 0, 1])
    
    def test_model_robustness(self):
        """测试模型对异常输入的健壮性"""
        # 测试各种数据结构对None值的处理
        trie = TrieModel()
        with self.assertRaises(TypeError):
            trie.insert(None)
        
        stack = StackModel()
        # 大多数Python数据结构允许None值，但我们应该确保它们能正确处理
        self.assertTrue(stack.push(None))
        self.assertIsNone(stack.pop())
        
        # 测试哈希表对None的处理
        hashtable = HashTableModel()
        index, path, is_full = hashtable.insert(None)
        self.assertIsNotNone(index)
        found, _ = hashtable.find(None)
        self.assertTrue(found)