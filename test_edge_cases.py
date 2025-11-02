# test_edge_cases.py
import unittest
from DS_visual.trie.trie_model import TrieModel
from DS_visual.linked_list.linked_list_model import _NodeList
from DS_visual.stack.stack_model import StackModel
from DS_visual.binary_tree.bst.bst_model import BSTModel
from DS_visual.hashtable.hashtable_model import HashTableModel

class TestEdgeCases(unittest.TestCase):
    """边界数据测试"""
    
    def test_trie_large_input(self):
        """测试Trie处理大量数据"""
        trie = TrieModel()
        
        # 插入1000个单词
        for i in range(1000):
            trie.insert(f"word{i}")
        
        # 验证所有单词都能找到
        for i in range(100):  # 抽样测试100个
            found, _ = trie.search(f"word{i}")
            self.assertTrue(found)
    
    def test_linked_list_large_data(self):
        """测试链表处理大量数据"""
        linked_list = _NodeList()
        
        # 添加10000个元素
        for i in range(10000):
            linked_list.append(i)
        
        # 验证大小
        self.assertEqual(len(linked_list), 10000)
        
        # 验证首尾元素
        self.assertEqual(linked_list[0], 0)
        self.assertEqual(linked_list[9999], 9999)
    
    def test_stack_overflow_protection(self):
        """测试栈溢出保护"""
        stack = StackModel(capacity=1000)
        
        # 大量入栈操作
        for i in range(1000):
            self.assertTrue(stack.push(i))
        
        # 验证栈已满
        self.assertTrue(stack.is_full())
        self.assertFalse(stack.push(1000))
    
    def test_trie_unicode_characters(self):
        """测试Trie处理Unicode字符"""
        trie = TrieModel()
        
        # 插入包含Unicode字符的单词
        test_words = ["hello", "世界", "こんにちは", "안녕하세요", "🎉"]
        
        for word in test_words:
            trie.insert(word)
        
        for word in test_words:
            found, _ = trie.search(word)
            self.assertTrue(found)
    
    def test_empty_operations(self):
        """测试空数据结构操作"""
        # 空Trie
        trie = TrieModel()
        found, _ = trie.search("anything")
        self.assertFalse(found)
        
        # 空链表
        linked_list = _NodeList()
        with self.assertRaises(IndexError):
            _ = linked_list[0]
        
        # 空栈
        stack = StackModel()
        self.assertIsNone(stack.pop())
        
        # 空BST
        bst = BSTModel()
        node, path = bst.search_with_path(10)
        self.assertIsNone(node)
        
        # 空哈希表
        hashtable = HashTableModel()
        found, _ = hashtable.find(10)
        self.assertFalse(found)
    
    def test_bst_extreme_balanced(self):
        """测试BST处理完全平衡的情况"""
        bst = BSTModel()
        # 按照能形成完全平衡树的顺序插入
        values = [50, 30, 70, 20, 40, 60, 80]
        for val in values:
            bst.insert(val)
        
        # 验证搜索
        for val in values:
            node, path = bst.search_with_path(val)
            self.assertIsNotNone(node)
            self.assertEqual(node.val, val)
    
    def test_bst_extreme_unbalanced(self):
        """测试BST处理完全不平衡的情况（链表化）"""
        bst = BSTModel()
        # 按升序插入，形成链表
        for i in range(100):
            bst.insert(i)
        
        # 验证搜索
        for i in range(10):
            node, path = bst.search_with_path(i)
            self.assertIsNotNone(node)
            self.assertEqual(node.val, i)
    
    def test_hashtable_high_collision(self):
        """测试哈希表处理高冲突情况"""
        # 使用小容量来强制冲突
        hashtable = HashTableModel(capacity=5)
        
        # 插入多个可能导致冲突的值
        values = [1, 6, 11, 16, 21]  # 这些值模5都是1
        for val in values:
            index, path, is_full = hashtable.insert(val)
            self.assertIsNotNone(index)
        
        # 验证所有值都能找到
        for val in values:
            found, _ = hashtable.find(val)
            self.assertTrue(found)