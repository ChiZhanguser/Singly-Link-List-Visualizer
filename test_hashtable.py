# test_hashtable_model.py
import unittest
from DS_visual.hashtable.hashtable_model import HashTableModel

class TestHashTableModel(unittest.TestCase):
    """哈希表测试"""
    
    def setUp(self):
        self.hashtable = HashTableModel(capacity=11)
    
    def test_insert_and_find(self):
        """测试插入和查找功能"""
        # 插入元素
        index, path, is_full = self.hashtable.insert(10)
        self.assertIsNotNone(index)
        self.assertFalse(is_full)
        
        # 查找元素
        found, probe_path = self.hashtable.find(10)
        self.assertTrue(found)
    
    def test_find_nonexistent(self):
        """测试查找不存在的元素"""
        found, probe_path = self.hashtable.find(10)
        self.assertFalse(found)
    
    def test_insert_multiple_elements(self):
        """测试插入多个元素"""
        values = [10, 20, 30, 40, 50]
        for value in values:
            index, path, is_full = self.hashtable.insert(value)
            self.assertIsNotNone(index)
            self.assertFalse(is_full)
        
        # 验证所有元素都能找到
        for value in values:
            found, _ = self.hashtable.find(value)
            self.assertTrue(found)
    
    def test_insert_duplicate(self):
        """测试插入重复元素"""
        # 第一次插入
        index1, path1, is_full1 = self.hashtable.insert(10)
        self.assertIsNotNone(index1)
        
        # 第二次插入相同元素
        index2, path2, is_full2 = self.hashtable.insert(10)
        
        # 应该返回相同的索引，且表大小不变
        self.assertEqual(index1, index2)
        self.assertEqual(self.hashtable.size, 1)
    
    def test_invalid_capacity(self):
        """测试无效容量"""
        with self.assertRaises(ValueError):
            HashTableModel(capacity=0)
        
        with self.assertRaises(ValueError):
            HashTableModel(capacity=-5)
    
    def test_hash_different_types(self):
        """测试哈希不同类型的值"""
        # 插入不同类型的值
        self.hashtable.insert(10)
        self.hashtable.insert("test")
        self.hashtable.insert(3.14)
        
        # 验证都能找到
        self.assertTrue(self.hashtable.find(10)[0])
        self.assertTrue(self.hashtable.find("test")[0])
        self.assertTrue(self.hashtable.find(3.14)[0])