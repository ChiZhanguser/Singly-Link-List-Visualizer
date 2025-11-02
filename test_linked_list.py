#!/usr/bin/env python3
"""
单链表测试程序
测试 LinkedListModel 的核心功能
"""

import unittest
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from DS_visual.linked_list.linked_list_model import LinkedListModel, _Node, _NodeList


class TestNode(unittest.TestCase):
    """测试 _Node 类"""
    
    def test_node_creation(self):
        """测试节点创建"""
        node = _Node(10)
        self.assertEqual(node.value, 10)
        self.assertIsNone(node.next)
    
    def test_node_with_different_types(self):
        """测试不同类型的节点值"""
        int_node = _Node(42)
        str_node = _Node("hello")
        float_node = _Node(3.14)
        list_node = _Node([1, 2, 3])
        
        self.assertEqual(int_node.value, 42)
        self.assertEqual(str_node.value, "hello")
        self.assertEqual(float_node.value, 3.14)
        self.assertEqual(list_node.value, [1, 2, 3])
    
    def test_node_linking(self):
        """测试节点连接"""
        node1 = _Node(1)
        node2 = _Node(2)
        node3 = _Node(3)
        
        node1.next = node2
        node2.next = node3
        
        self.assertEqual(node1.next, node2)
        self.assertEqual(node2.next, node3)
        self.assertIsNone(node3.next)

class TestNodeList(unittest.TestCase):
    """测试 _NodeList 类"""
    
    def setUp(self):
        """每个测试前的初始化"""
        self.node_list = _NodeList()
    
    def test_initial_state(self):
        """测试初始状态"""
        self.assertIsNone(self.node_list.head)
        self.assertEqual(len(self.node_list), 0)
        self.assertEqual(self.node_list.to_list(), [])
    
    def test_init_with_iterable(self):
        """测试使用可迭代对象初始化"""
        node_list = _NodeList([1, 2, 3, 4])
        self.assertEqual(len(node_list), 4)
        self.assertEqual(node_list.to_list(), [1, 2, 3, 4])
    
    def test_append_single_element(self):
        """测试添加单个元素"""
        self.node_list.append(10)
        self.assertEqual(len(self.node_list), 1)
        self.assertEqual(self.node_list.to_list(), [10])
        self.assertIsNotNone(self.node_list.head)
        self.assertEqual(self.node_list.head.value, 10)
    
    def test_append_multiple_elements(self):
        """测试添加多个元素"""
        values = [1, 2, 3, 4, 5]
        for val in values:
            self.node_list.append(val)
        
        self.assertEqual(len(self.node_list), 5)
        self.assertEqual(self.node_list.to_list(), values)
    
    def test_clear(self):
        """测试清空链表"""
        self.node_list.append(1)
        self.node_list.append(2)
        self.node_list.append(3)
        
        self.node_list.clear()
        
        self.assertIsNone(self.node_list.head)
        self.assertEqual(len(self.node_list), 0)
        self.assertEqual(self.node_list.to_list(), [])
    
    def test_iter(self):
        """测试迭代器"""
        values = [1, 2, 3, 4, 5]
        for val in values:
            self.node_list.append(val)
        
        result = list(self.node_list)
        self.assertEqual(result, values)
    
    def test_repr(self):
        """测试字符串表示"""
        self.node_list.append(1)
        self.node_list.append(2)
        self.node_list.append(3)
        
        self.assertEqual(repr(self.node_list), "[1, 2, 3]")
    
    def test_getitem_positive_index(self):
        """测试正向索引访问"""
        values = [10, 20, 30, 40, 50]
        for val in values:
            self.node_list.append(val)
        
        self.assertEqual(self.node_list[0], 10)
        self.assertEqual(self.node_list[2], 30)
        self.assertEqual(self.node_list[4], 50)
    
    def test_getitem_negative_index(self):
        """测试负向索引访问"""
        values = [10, 20, 30, 40, 50]
        for val in values:
            self.node_list.append(val)
        
        self.assertEqual(self.node_list[-1], 50)
        self.assertEqual(self.node_list[-3], 30)
        self.assertEqual(self.node_list[-5], 10)
    
    def test_getitem_out_of_range(self):
        """测试索引越界"""
        self.node_list.append(1)
        self.node_list.append(2)
        
        with self.assertRaises(IndexError):
            _ = self.node_list[5]
        
        with self.assertRaises(IndexError):
            _ = self.node_list[-10]
    
    def test_setitem(self):
        """测试修改元素值"""
        self.node_list.append(1)
        self.node_list.append(2)
        self.node_list.append(3)
        
        self.node_list[1] = 20
        self.assertEqual(self.node_list.to_list(), [1, 20, 3])
        
        self.node_list[-1] = 30
        self.assertEqual(self.node_list.to_list(), [1, 20, 30])
    
    def test_pop_last(self):
        """测试删除最后一个元素"""
        values = [1, 2, 3, 4, 5]
        for val in values:
            self.node_list.append(val)
        
        popped = self.node_list.pop()
        self.assertEqual(popped, 5)
        self.assertEqual(self.node_list.to_list(), [1, 2, 3, 4])
        self.assertEqual(len(self.node_list), 4)
    
    def test_pop_first(self):
        """测试删除第一个元素"""
        values = [1, 2, 3, 4, 5]
        for val in values:
            self.node_list.append(val)
        
        popped = self.node_list.pop(0)
        self.assertEqual(popped, 1)
        self.assertEqual(self.node_list.to_list(), [2, 3, 4, 5])
        self.assertEqual(len(self.node_list), 4)
    
    def test_pop_middle(self):
        """测试删除中间元素"""
        values = [1, 2, 3, 4, 5]
        for val in values:
            self.node_list.append(val)
        
        popped = self.node_list.pop(2)
        self.assertEqual(popped, 3)
        self.assertEqual(self.node_list.to_list(), [1, 2, 4, 5])
    
    def test_pop_negative_index(self):
        """测试使用负索引删除"""
        values = [1, 2, 3, 4, 5]
        for val in values:
            self.node_list.append(val)
        
        popped = self.node_list.pop(-2)
        self.assertEqual(popped, 4)
        self.assertEqual(self.node_list.to_list(), [1, 2, 3, 5])
    
    def test_pop_empty_list(self):
        """测试从空链表删除"""
        with self.assertRaises(IndexError):
            self.node_list.pop()
    
    def test_pop_out_of_range(self):
        """测试删除越界索引"""
        self.node_list.append(1)
        self.node_list.append(2)
        
        with self.assertRaises(IndexError):
            self.node_list.pop(5)
    
    def test_insert_at_beginning(self):
        """测试在开头插入"""
        self.node_list.append(2)
        self.node_list.append(3)
        
        self.node_list.insert(0, 1)
        self.assertEqual(self.node_list.to_list(), [1, 2, 3])
    
    def test_insert_at_end(self):
        """测试在末尾插入"""
        self.node_list.append(1)
        self.node_list.append(2)
        
        self.node_list.insert(10, 3)  # 超出范围应该追加到末尾
        self.assertEqual(self.node_list.to_list(), [1, 2, 3])
    
    def test_insert_in_middle(self):
        """测试在中间插入"""
        self.node_list.append(1)
        self.node_list.append(3)
        
        self.node_list.insert(1, 2)
        self.assertEqual(self.node_list.to_list(), [1, 2, 3])
    
    def test_insert_negative_index(self):
        """测试负索引插入"""
        self.node_list.append(2)
        self.node_list.append(3)
        
        self.node_list.insert(-1, 1)  # 负索引应该插入到开头
        self.assertEqual(self.node_list.to_list(), [1, 2, 3])


class TestLinkedListModel(unittest.TestCase):
    """测试 LinkedListModel 类"""
    
    def setUp(self):
        """每个测试前的初始化"""
        self.model = LinkedListModel()
    
    def test_initial_state(self):
        """测试初始状态"""
        self.assertEqual(len(self.model), 0)
        self.assertEqual(self.model.to_list(), [])
    
    def test_append(self):
        """测试追加元素"""
        self.model.append(1)
        self.model.append(2)
        self.model.append(3)
        
        self.assertEqual(len(self.model), 3)
        self.assertEqual(self.model.to_list(), [1, 2, 3])
    
    def test_insert_first(self):
        """测试在开头插入"""
        self.model.append(2)
        self.model.append(3)
        
        self.model.insert_first(1)
        
        self.assertEqual(self.model.to_list(), [1, 2, 3])
    
    def test_insert_last(self):
        """测试在末尾插入"""
        self.model.append(1)
        self.model.append(2)
        
        self.model.insert_last(3)
        
        self.assertEqual(self.model.to_list(), [1, 2, 3])
    
    def test_insert_after(self):
        """测试在指定位置后插入"""
        self.model.append(1)
        self.model.append(2)
        self.model.append(4)
        
        # 在位置1后插入（1-based，所以在索引1处插入）
        self.model.insert_after(1, 3)
        
        self.assertEqual(self.model.to_list(), [1, 3, 2, 4])
    
    def test_insert_after_out_of_range(self):
        """测试insert_after越界"""
        self.model.append(1)
        self.model.append(2)
        
        with self.assertRaises(IndexError):
            self.model.insert_after(0, 99)  # position < 1
        
        with self.assertRaises(IndexError):
            self.model.insert_after(10, 99)  # position > length
    
    def test_delete_first(self):
        """测试删除第一个元素"""
        self.model.append(1)
        self.model.append(2)
        self.model.append(3)
        
        self.model.delete_first()
        
        self.assertEqual(self.model.to_list(), [2, 3])
        self.assertEqual(len(self.model), 2)
    
    def test_delete_first_empty(self):
        """测试从空链表删除第一个"""
        with self.assertRaises(IndexError):
            self.model.delete_first()
    
    def test_delete_last(self):
        """测试删除最后一个元素"""
        self.model.append(1)
        self.model.append(2)
        self.model.append(3)
        
        self.model.delete_last()
        
        self.assertEqual(self.model.to_list(), [1, 2])
        self.assertEqual(len(self.model), 2)
    
    def test_delete_last_empty(self):
        """测试从空链表删除最后一个"""
        with self.assertRaises(IndexError):
            self.model.delete_last()
    
    def test_clear(self):
        """测试清空链表"""
        self.model.append(1)
        self.model.append(2)
        self.model.append(3)
        
        self.model.clear()
        
        self.assertEqual(len(self.model), 0)
        self.assertEqual(self.model.to_list(), [])
    
    def test_pop(self):
        """测试pop操作"""
        self.model.append(1)
        self.model.append(2)
        self.model.append(3)
        
        val = self.model.pop()
        self.assertEqual(val, 3)
        self.assertEqual(self.model.to_list(), [1, 2])
        
        val = self.model.pop(0)
        self.assertEqual(val, 1)
        self.assertEqual(self.model.to_list(), [2])
    
    def test_insert(self):
        """测试insert操作"""
        self.model.append(1)
        self.model.append(3)
        
        self.model.insert(1, 2)
        self.assertEqual(self.model.to_list(), [1, 2, 3])
    
    def test_repr(self):
        """测试字符串表示"""
        self.model.append(1)
        self.model.append(2)
        self.model.append(3)
        
        self.assertEqual(repr(self.model), "[1, 2, 3]")


class TestLinkedListOperations(unittest.TestCase):
    """测试链表的复杂操作"""
    
    def setUp(self):
        """每个测试前的初始化"""
        self.model = LinkedListModel()
    
    def test_multiple_insertions_and_deletions(self):
        """测试多次插入和删除"""
        # 插入元素
        for i in range(1, 6):
            self.model.append(i)
        self.assertEqual(self.model.to_list(), [1, 2, 3, 4, 5])
        
        # 删除第一个
        self.model.delete_first()
        self.assertEqual(self.model.to_list(), [2, 3, 4, 5])
        
        # 删除最后一个
        self.model.delete_last()
        self.assertEqual(self.model.to_list(), [2, 3, 4])
        
        # 在开头插入
        self.model.insert_first(1)
        self.assertEqual(self.model.to_list(), [1, 2, 3, 4])
        
        # 在末尾插入
        self.model.insert_last(5)
        self.assertEqual(self.model.to_list(), [1, 2, 3, 4, 5])
    
    def test_single_element_operations(self):
        """测试单元素链表的操作"""
        self.model.append(42)
        
        self.assertEqual(len(self.model), 1)
        self.assertEqual(self.model.to_list(), [42])
        
        # 删除唯一元素
        self.model.delete_first()
        self.assertEqual(len(self.model), 0)
        
        # 再次添加
        self.model.append(99)
        self.model.delete_last()
        self.assertEqual(len(self.model), 0)
    
    def test_large_list(self):
        """测试大型链表"""
        # 插入1000个元素
        for i in range(1000):
            self.model.append(i)
        
        self.assertEqual(len(self.model), 1000)
        self.assertEqual(self.model.to_list()[0], 0)
        self.assertEqual(self.model.to_list()[-1], 999)
        
        # 删除一些元素
        for _ in range(10):
            self.model.delete_first()
        
        self.assertEqual(len(self.model), 990)
        self.assertEqual(self.model.to_list()[0], 10)
    
    def test_alternating_operations(self):
        """测试交替操作"""
        self.model.append(1)
        self.model.insert_first(0)
        self.model.append(2)
        self.model.delete_last()
        self.model.append(2)
        self.model.delete_first()
        
        self.assertEqual(self.model.to_list(), [1, 2])
    
    def test_string_values(self):
        """测试字符串值"""
        words = ["hello", "world", "python", "test"]
        for word in words:
            self.model.append(word)
        
        self.assertEqual(self.model.to_list(), words)
        
        self.model.delete_first()
        self.assertEqual(self.model.to_list(), words[1:])
    
    def test_mixed_type_values(self):
        """测试混合类型值"""
        self.model.append(1)
        self.model.append("two")
        self.model.append(3.0)
        self.model.append([4, 5])
        self.model.append({"key": 6})
        
        result = self.model.to_list()
        self.assertEqual(len(result), 5)
        self.assertEqual(result[0], 1)
        self.assertEqual(result[1], "two")
        self.assertEqual(result[2], 3.0)
        self.assertEqual(result[3], [4, 5])
        self.assertEqual(result[4], {"key": 6})


class TestEdgeCases(unittest.TestCase):
    """测试边界情况"""
    
    def setUp(self):
        """每个测试前的初始化"""
        self.model = LinkedListModel()
    
    def test_operations_on_empty_list(self):
        """测试空链表操作"""
        self.assertEqual(len(self.model), 0)
        self.assertEqual(self.model.to_list(), [])
        
        # 清空空链表
        self.model.clear()
        self.assertEqual(len(self.model), 0)
    
    def test_repeated_clears(self):
        """测试重复清空"""
        self.model.append(1)
        self.model.clear()
        self.model.append(2)
        self.model.clear()
        self.model.append(3)
        
        self.assertEqual(self.model.to_list(), [3])
    
    def test_insert_after_boundary_positions(self):
        """测试insert_after的边界位置"""
        self.model.append(1)
        self.model.append(2)
        self.model.append(3)
        
        # 在第一个位置后插入
        self.model.insert_after(1, 1.5)
        self.assertEqual(self.model.to_list(), [1, 1.5, 2, 3])
        
        # 在最后一个位置后插入
        self.model.insert_after(4, 4)
        self.assertEqual(self.model.to_list(), [1, 1.5, 2, 3, 4])
    
    def test_delete_until_empty(self):
        """测试删除直到空链表"""
        values = [1, 2, 3, 4, 5]
        for val in values:
            self.model.append(val)
        
        while len(self.model) > 0:
            self.model.delete_last()
        
        self.assertEqual(len(self.model), 0)
        self.assertEqual(self.model.to_list(), [])
    
    def test_rebuild_after_clear(self):
        """测试清空后重建"""
        # 第一次构建
        for i in range(5):
            self.model.append(i)
        self.assertEqual(len(self.model), 5)
        
        # 清空
        self.model.clear()
        self.assertEqual(len(self.model), 0)
        
        # 重建
        for i in range(10, 15):
            self.model.append(i)
        self.assertEqual(len(self.model), 5)
        self.assertEqual(self.model.to_list(), [10, 11, 12, 13, 14])


class TestPerformance(unittest.TestCase):
    """性能测试（简单验证）"""
    
    def test_append_performance(self):
        """测试append性能"""
        model = LinkedListModel()
        import time
        
        start = time.time()
        for i in range(10000):
            model.append(i)
        duration = time.time() - start
        
        self.assertEqual(len(model), 10000)
        print(f"\nAppend 10000 elements: {duration:.4f} seconds")
    
    def test_delete_first_performance(self):
        """测试delete_first性能"""
        model = LinkedListModel()
        for i in range(1000):
            model.append(i)
        
        import time
        start = time.time()
        for _ in range(500):
            model.delete_first()
        duration = time.time() - start
        
        self.assertEqual(len(model), 500)
        print(f"Delete first 500 elements: {duration:.4f} seconds")


def run_linked_list_tests():
    """运行所有链表测试"""
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加所有测试类
    suite.addTests(loader.loadTestsFromTestCase(TestNode))
    suite.addTests(loader.loadTestsFromTestCase(TestNodeList))
    suite.addTests(loader.loadTestsFromTestCase(TestLinkedListModel))
    suite.addTests(loader.loadTestsFromTestCase(TestLinkedListOperations))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestPerformance))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出摘要
    print("\n" + "="*60)
    print("单链表测试结果摘要:")
    print(f"运行测试数: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print("="*60)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_linked_list_tests()
    sys.exit(0 if success else 1)