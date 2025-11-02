# test_trie_model.py
import unittest
from DS_visual.trie.trie_model import TrieModel, TrieNode

class TestTrieModel(unittest.TestCase):
    """Trie数据结构模型测试"""
    
    def setUp(self):
        self.trie = TrieModel()
    
    def test_insert_single_word(self):
        """测试插入单个单词"""
        path = self.trie.insert("hello")
        self.assertEqual(len(path), 5)
        self.assertTrue(path[-1].is_end)
    
    def test_insert_multiple_words(self):
        """测试插入多个单词"""
        self.trie.insert("hello")
        self.trie.insert("world")
        self.trie.insert("hell")
        
        # 验证搜索功能
        found, _ = self.trie.search("hello")
        self.assertTrue(found)
        
        found, _ = self.trie.search("hell")
        self.assertTrue(found)
        
        found, _ = self.trie.search("world")
        self.assertTrue(found)
    
    def test_search_nonexistent_word(self):
        """测试搜索不存在的单词"""
        self.trie.insert("hello")
        found, _ = self.trie.search("world")
        self.assertFalse(found)
    
    def test_search_partial_word(self):
        """测试搜索部分匹配的单词"""
        self.trie.insert("hello")
        found, path = self.trie.search("hell")
        self.assertFalse(found)  # "hell" 不是完整单词
        self.assertEqual(len(path), 4)  # 但路径应该正确
    
    def test_empty_trie_search(self):
        """测试空Trie的搜索"""
        found, path = self.trie.search("anything")
        self.assertFalse(found)
        self.assertEqual(len(path), 0)
    
    def test_clear_trie(self):
        """测试清空Trie"""
        self.trie.insert("hello")
        self.trie.insert("world")
        
        self.trie.clear()
        
        found, _ = self.trie.search("hello")
        self.assertFalse(found)
        found, _ = self.trie.search("world")
        self.assertFalse(found)
    
    def test_collect_all_nodes(self):
        """测试收集所有节点"""
        self.trie.insert("hello")
        self.trie.insert("world")
        
        nodes = self.trie.collect_all_nodes()
        # hello(5) + world(5) 共10个节点
        self.assertEqual(len(nodes), 10)
    
    def test_nodes_by_level(self):
        """测试按层级获取节点"""
        self.trie.insert("hello")
        self.trie.insert("world")
        
        levels = self.trie.nodes_by_level()
        self.assertIn(1, levels)
        self.assertIn(2, levels)
        self.assertIn(3, levels)
        self.assertIn(4, levels)
        self.assertIn(5, levels)
    
    def test_insert_empty_string(self):
        """测试插入空字符串"""
        path = self.trie.insert("")
        self.assertEqual(len(path), 0)
    
    def test_insert_special_characters(self):
        """测试插入特殊字符"""
        self.trie.insert("hello@world")
        found, _ = self.trie.search("hello@world")
        self.assertTrue(found)