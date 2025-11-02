# test_performance.py
import unittest
import time
from DS_visual.trie.trie_model import TrieModel
from DS_visual.linked_list.linked_list_model import _NodeList
from DS_visual.stack.stack_model import StackModel
from DS_visual.binary_tree.bst.bst_model import BSTModel
from DS_visual.hashtable.hashtable_model import HashTableModel

class TestPerformance(unittest.TestCase):
    """性能测试"""
    
    def test_trie_insertion_performance(self):
        """测试Trie插入性能"""
        trie = TrieModel()
        
        start_time = time.time()
        
        # 插入10000个单词
        for i in range(10000):
            trie.insert(f"testword{i}")
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # 性能要求：10000次插入应在5秒内完成
        self.assertLess(execution_time, 5.0)
    
    def test_trie_search_performance(self):
        """测试Trie搜索性能"""
        trie = TrieModel()
        
        # 准备测试数据
        for i in range(10000):
            trie.insert(f"testword{i}")
        
        start_time = time.time()
        
        # 搜索1000次
        for i in range(1000):
            trie.search(f"testword{i}")
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # 性能要求：1000次搜索应在1秒内完成
        self.assertLess(execution_time, 1.0)
    
    def test_linked_list_traversal_performance(self):
        """测试链表遍历性能"""
        linked_list = _NodeList()
        
        # 准备大型链表
        for i in range(10000):
            linked_list.append(i)
        
        start_time = time.time()
        
        # 遍历整个链表
        current = linked_list.head
        while current:
            current = current.next
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # 性能要求：遍历10000个节点应在0.1秒内完成
        self.assertLess(execution_time, 0.1)
    
    def test_stack_operations_performance(self):
        """测试栈操作性能"""
        stack = StackModel(capacity=100000)
        
        # 测试push性能
        start_time = time.time()
        for i in range(100000):
            stack.push(i)
        end_time = time.time()
        push_time = end_time - start_time
        self.assertLess(push_time, 1.0)  # 10万次push应在1秒内完成
        
        # 测试pop性能
        start_time = time.time()
        for _ in range(100000):
            stack.pop()
        end_time = time.time()
        pop_time = end_time - start_time
        self.assertLess(pop_time, 1.0)  # 10万次pop应在1秒内完成
    
    def test_bst_balanced_performance(self):
        """测试平衡BST的性能"""
        bst = BSTModel()
        
        # 构建一个相对平衡的BST
        balanced_values = [500, 250, 750, 125, 375, 625, 875]  # 这样的插入顺序会形成更平衡的树
        for val in balanced_values:
            bst.insert(val)
        
        # 测试搜索性能
        start_time = time.time()
        for _ in range(10000):
            for val in balanced_values:
                bst.search_with_path(val)
        end_time = time.time()
        search_time = end_time - start_time
        
        # 性能要求：多次搜索应高效完成
        self.assertLess(search_time, 0.5)