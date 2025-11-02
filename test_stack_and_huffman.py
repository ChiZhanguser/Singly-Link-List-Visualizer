#!/usr/bin/env python3
"""
栈 (Stack) 测试程序
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from DS_visual.stack.stack_model import StackModel


class TestStackBasics(unittest.TestCase):
    """栈基本功能测试"""
    
    def setUp(self):
        """每个测试前的初始化"""
        self.stack = StackModel(capacity=5)
    
    def test_initial_state(self):
        """测试初始状态"""
        self.assertTrue(self.stack.is_empty())
        self.assertFalse(self.stack.is_full())
        self.assertEqual(self.stack.top, -1)
        self.assertEqual(len(self.stack), 0)
    
    def test_custom_capacity(self):
        """测试自定义容量"""
        stack = StackModel(capacity=10)
        self.assertEqual(stack.capacity, 10)
        
        stack = StackModel(capacity=1)
        self.assertEqual(stack.capacity, 1)
    
    def test_push_single_element(self):
        """测试压入单个元素"""
        success = self.stack.push(10)
        
        self.assertTrue(success)
        self.assertFalse(self.stack.is_empty())
        self.assertEqual(self.stack.top, 0)
        self.assertEqual(len(self.stack), 1)
    
    def test_push_multiple_elements(self):
        """测试压入多个元素"""
        values = [1, 2, 3, 4, 5]
        
        for val in values:
            success = self.stack.push(val)
            self.assertTrue(success)
        
        self.assertEqual(len(self.stack), 5)
        self.assertEqual(self.stack.top, 4)
        self.assertTrue(self.stack.is_full())
    
    def test_push_to_full_stack(self):
        """测试向满栈压入元素"""
        # 填满栈
        for i in range(5):
            self.stack.push(i)
        
        # 尝试压入第6个元素
        success = self.stack.push(99)
        
        self.assertFalse(success)
        self.assertTrue(self.stack.is_full())
        self.assertEqual(len(self.stack), 5)
    
    def test_pop_single_element(self):
        """测试弹出单个元素"""
        self.stack.push(42)
        value = self.stack.pop()
        
        self.assertEqual(value, 42)
        self.assertTrue(self.stack.is_empty())
        self.assertEqual(self.stack.top, -1)
    
    def test_pop_multiple_elements(self):
        """测试弹出多个元素（LIFO顺序）"""
        values = [1, 2, 3, 4, 5]
        for val in values:
            self.stack.push(val)
        
        popped = []
        while not self.stack.is_empty():
            popped.append(self.stack.pop())
        
        # 应该是逆序弹出
        self.assertEqual(popped, [5, 4, 3, 2, 1])
    
    def test_pop_from_empty_stack(self):
        """测试从空栈弹出"""
        value = self.stack.pop()
        
        self.assertIsNone(value)
        self.assertTrue(self.stack.is_empty())
    
    def test_peek(self):
        """测试查看栈顶元素"""
        self.stack.push(10)
        self.stack.push(20)
        self.stack.push(30)
        
        top = self.stack.peek()
        
        self.assertEqual(top, 30)
        self.assertEqual(len(self.stack), 3)  # peek不改变栈
    
    def test_peek_empty_stack(self):
        """测试查看空栈栈顶"""
        top = self.stack.peek()
        self.assertIsNone(top)
    
    def test_clear(self):
        """测试清空栈"""
        for i in range(5):
            self.stack.push(i)
        
        self.stack.clear()
        
        self.assertTrue(self.stack.is_empty())
        self.assertEqual(self.stack.top, -1)
        self.assertEqual(len(self.stack), 0)
    
    def test_len(self):
        """测试长度函数"""
        self.assertEqual(len(self.stack), 0)
        
        self.stack.push(1)
        self.assertEqual(len(self.stack), 1)
        
        self.stack.push(2)
        self.stack.push(3)
        self.assertEqual(len(self.stack), 3)
        
        self.stack.pop()
        self.assertEqual(len(self.stack), 2)


class TestStackOperations(unittest.TestCase):
    """栈操作序列测试"""
    
    def setUp(self):
        """每个测试前的初始化"""
        self.stack = StackModel(capacity=10)
    
    def test_push_pop_sequence(self):
        """测试压入弹出序列"""
        # 压入3个
        self.stack.push(1)
        self.stack.push(2)
        self.stack.push(3)
        
        # 弹出2个
        self.assertEqual(self.stack.pop(), 3)
        self.assertEqual(self.stack.pop(), 2)
        
        # 再压入2个
        self.stack.push(4)
        self.stack.push(5)
        
        # 验证顺序
        self.assertEqual(self.stack.pop(), 5)
        self.assertEqual(self.stack.pop(), 4)
        self.assertEqual(self.stack.pop(), 1)
    
    def test_alternating_push_pop(self):
        """测试交替压入弹出"""
        for i in range(10):
            self.stack.push(i)
            if i % 2 == 1:
                self.stack.pop()
        
        # 应该剩下5个元素: 0, 2, 4, 6, 8
        self.assertEqual(len(self.stack), 5)
    
    def test_fill_empty_fill(self):
        """测试填满-清空-再填满"""
        # 第一次填满
        for i in range(10):
            self.stack.push(i)
        self.assertTrue(self.stack.is_full())
        
        # 清空
        self.stack.clear()
        self.assertTrue(self.stack.is_empty())
        
        # 再次填满
        for i in range(10, 20):
            self.stack.push(i)
        self.assertTrue(self.stack.is_full())
        self.assertEqual(self.stack.peek(), 19)
    
    def test_mixed_type_values(self):
        """测试混合类型值"""
        self.stack.push(1)
        self.stack.push("hello")
        self.stack.push(3.14)
        self.stack.push([1, 2, 3])
        self.stack.push({"key": "value"})
        
        self.assertEqual(self.stack.pop(), {"key": "value"})
        self.assertEqual(self.stack.pop(), [1, 2, 3])
        self.assertEqual(self.stack.pop(), 3.14)
        self.assertEqual(self.stack.pop(), "hello")
        self.assertEqual(self.stack.pop(), 1)


class TestStackEdgeCases(unittest.TestCase):
    """栈边界情况测试"""
    
    def setUp(self):
        """每个测试前的初始化"""
        self.stack = StackModel(capacity=5)
    
    def test_single_capacity_stack(self):
        """测试容量为1的栈"""
        stack = StackModel(capacity=1)
        
        self.assertTrue(stack.push(42))
        self.assertTrue(stack.is_full())
        
        self.assertFalse(stack.push(99))
        
        self.assertEqual(stack.pop(), 42)
        self.assertTrue(stack.is_empty())
    
    def test_large_capacity_stack(self):
        """测试大容量栈"""
        stack = StackModel(capacity=1000)
        
        for i in range(1000):
            success = stack.push(i)
            self.assertTrue(success)
        
        self.assertTrue(stack.is_full())
        self.assertEqual(len(stack), 1000)
    
    def test_repeated_clears(self):
        """测试重复清空"""
        self.stack.push(1)
        self.stack.clear()
        self.assertTrue(self.stack.is_empty())
        
        self.stack.clear()  # 再次清空
        self.assertTrue(self.stack.is_empty())
        
        # 清空后仍可正常使用
        self.stack.push(2)
        self.assertEqual(self.stack.pop(), 2)
    
    def test_empty_operations(self):
        """测试空栈上的各种操作"""
        self.assertIsNone(self.stack.pop())
        self.assertIsNone(self.stack.peek())
        self.assertTrue(self.stack.is_empty())
        self.assertEqual(len(self.stack), 0)
    
    def test_full_stack_operations(self):
        """测试满栈上的操作"""
        # 填满栈
        for i in range(5):
            self.stack.push(i)
        
        # 验证满栈状态
        self.assertTrue(self.stack.is_full())
        self.assertFalse(self.stack.push(99))
        
        # peek应该仍然工作
        self.assertEqual(self.stack.peek(), 4)
        
        # pop后应该可以再push
        self.stack.pop()
        self.assertFalse(self.stack.is_full())
        self.assertTrue(self.stack.push(99))


class TestStackProperties(unittest.TestCase):
    """栈性质测试"""
    
    def test_lifo_property(self):
        """测试后进先出性质"""
        stack = StackModel(capacity=10)
        values = [1, 2, 3, 4, 5]
        
        for val in values:
            stack.push(val)
        
        result = []
        while not stack.is_empty():
            result.append(stack.pop())
        
        # 应该是逆序
        self.assertEqual(result, [5, 4, 3, 2, 1])
    
    def test_top_pointer_consistency(self):
        """测试栈顶指针一致性"""
        stack = StackModel(capacity=10)
        
        # 初始top为-1
        self.assertEqual(stack.top, -1)
        
        # 每次push，top递增
        for i in range(5):
            stack.push(i)
            self.assertEqual(stack.top, i)
        
        # 每次pop，top递减
        for i in range(4, -1, -1):
            self.assertEqual(stack.top, i)
            stack.pop()
        
        # 最后应该回到-1
        self.assertEqual(stack.top, -1)
    
    def test_repr(self):
        """测试字符串表示"""
        stack = StackModel(capacity=5)
        stack.push(1)
        stack.push(2)
        stack.push(3)
        
        repr_str = repr(stack)
        self.assertIn("Stack", repr_str)
        self.assertIn("top=2", repr_str)
        self.assertIn("[1, 2, 3]", repr_str)


def run_stack_tests():
    """运行所有栈测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestStackBasics))
    suite.addTests(loader.loadTestsFromTestCase(TestStackOperations))
    suite.addTests(loader.loadTestsFromTestCase(TestStackEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestStackProperties))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "="*60)
    print("栈测试结果摘要:")
    print(f"运行测试数: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print("="*60)
    
    return result.wasSuccessful()


# ============================================================
# Huffman树测试
# ============================================================

from DS_visual.binary_tree.huffman_tree.huffman_model import HuffmanModel, HuffmanNode


class TestHuffmanNode(unittest.TestCase):
    """Huffman节点测试"""
    
    def test_node_creation(self):
        """测试节点创建"""
        node = HuffmanNode(weight=5.0)
        
        self.assertEqual(node.weight, 5.0)
        self.assertIsNone(node.left)
        self.assertIsNone(node.right)
        self.assertEqual(node.label, "")
    
    def test_node_with_children(self):
        """测试带子节点的节点"""
        left = HuffmanNode(weight=2.0, label="A")
        right = HuffmanNode(weight=3.0, label="B")
        parent = HuffmanNode(weight=5.0, left=left, right=right, label="5.0")
        
        self.assertEqual(parent.weight, 5.0)
        self.assertEqual(parent.left, left)
        self.assertEqual(parent.right, right)
        self.assertEqual(parent.label, "5.0")
    
    def test_node_repr(self):
        """测试节点字符串表示"""
        node = HuffmanNode(weight=10.5)
        self.assertIn("10.5", repr(node))


class TestHuffmanModel(unittest.TestCase):
    """Huffman树模型测试"""
    
    def setUp(self):
        """每个测试前的初始化"""
        self.model = HuffmanModel()
    
    def test_initial_state(self):
        """测试初始状态"""
        self.assertIsNone(self.model.root)
        self.assertEqual(len(self.model.steps), 0)
    
    def test_build_empty_weights(self):
        """测试空权值列表"""
        root, steps, before, after = self.model.build_with_steps([])
        
        self.assertIsNone(root)
        self.assertEqual(len(steps), 0)
        self.assertEqual(len(before), 0)
        self.assertEqual(len(after), 0)
    
    def test_build_single_weight(self):
        """测试单个权值"""
        weights = [5.0]
        root, steps, before, after = self.model.build_with_steps(weights)
        
        self.assertIsNotNone(root)
        self.assertEqual(root.weight, 5.0)
        self.assertEqual(len(steps), 0)  # 单节点无需合并
    
    def test_build_two_weights(self):
        """测试两个权值"""
        weights = [3.0, 5.0]
        root, steps, before, after = self.model.build_with_steps(weights)
        
        self.assertIsNotNone(root)
        self.assertEqual(root.weight, 8.0)
        self.assertEqual(len(steps), 1)
        
        # 验证步骤
        left, right, parent = steps[0]
        self.assertEqual(left.weight, 3.0)
        self.assertEqual(right.weight, 5.0)
        self.assertEqual(parent.weight, 8.0)
    
    def test_build_multiple_weights(self):
        """测试多个权值"""
        weights = [5, 9, 12, 13, 16, 45]
        root, steps, before, after = self.model.build_with_steps(weights)
        
        # 根节点权值应该是所有权值之和
        self.assertEqual(root.weight, sum(weights))
        
        # 步骤数应该是n-1
        self.assertEqual(len(steps), len(weights) - 1)
        
        # 快照数量应该等于步骤数
        self.assertEqual(len(before), len(steps))
        self.assertEqual(len(after), len(steps))
    
    def test_build_process_correctness(self):
        """测试构建过程正确性"""
        weights = [1, 2, 3, 4]
        root, steps, before, after = self.model.build_with_steps(weights)
        
        # 验证每一步都是合并最小的两个节点
        for i, (left, right, parent) in enumerate(steps):
            self.assertEqual(parent.weight, left.weight + right.weight)
            self.assertEqual(parent.left, left)
            self.assertEqual(parent.right, right)
            
            # 验证before快照是排序的
            self.assertEqual(before[i], sorted(before[i]))
            
            # 验证after快照是排序的
            self.assertEqual(after[i], sorted(after[i]))


class TestHuffmanBuilding(unittest.TestCase):
    """Huffman树构建测试"""
    
    def test_small_tree(self):
        """测试小型Huffman树"""
        model = HuffmanModel()
        weights = [1, 2, 3]
        
        root, steps, before, after = model.build_with_steps(weights)
        
        self.assertIsNotNone(root)
        self.assertEqual(len(steps), 2)
        
        # 第一步：合并1和2
        self.assertEqual(steps[0][0].weight, 1)
        self.assertEqual(steps[0][1].weight, 2)
        self.assertEqual(steps[0][2].weight, 3)
        
        # 第二步：合并3和3（前面的结果）
        self.assertEqual(steps[1][2].weight, 6)
    
    def test_classic_example(self):
        """测试经典教材示例"""
        model = HuffmanModel()
        weights = [5, 9, 12, 13, 16, 45]
        
        root, steps, before, after = model.build_with_steps(weights)
        
        # 验证根节点
        self.assertEqual(root.weight, 100)
        
        # 验证步骤数
        self.assertEqual(len(steps), 5)
        
        # 第一步应该合并最小的两个：5和9
        first_left = min(steps[0][0].weight, steps[0][1].weight)
        first_right = max(steps[0][0].weight, steps[0][1].weight)
        self.assertEqual(first_left, 5)
        self.assertEqual(first_right, 9)
    
    def test_equal_weights(self):
        """测试相同权值"""
        model = HuffmanModel()
        weights = [1, 1, 1, 1]
        
        root, steps, before, after = model.build_with_steps(weights)
        
        self.assertEqual(root.weight, 4)
        self.assertEqual(len(steps), 3)
    
    def test_increasing_weights(self):
        """测试递增权值"""
        model = HuffmanModel()
        weights = [1, 2, 3, 4, 5]
        
        root, steps, before, after = model.build_with_steps(weights)
        
        self.assertEqual(root.weight, sum(weights))
        self.assertEqual(len(steps), len(weights) - 1)


class TestHuffmanSnapshots(unittest.TestCase):
    """Huffman快照测试"""
    
    def test_snapshot_consistency(self):
        """测试快照一致性"""
        model = HuffmanModel()
        weights = [3, 5, 7, 9]
        
        root, steps, before, after = model.build_with_steps(weights)
        
        # before和after数量应该相等
        self.assertEqual(len(before), len(after))
        
        # 每个before应该比对应的after多一个元素（合并前 vs 合并后）
        for i in range(len(before)):
            self.assertEqual(len(before[i]), len(after[i]) + 1)
    
    def test_snapshot_order(self):
        """测试快照排序"""
        model = HuffmanModel()
        weights = [10, 5, 15, 20, 8]
        
        root, steps, before, after = model.build_with_steps(weights)
        
        # 所有before快照应该是排序的
        for snapshot in before:
            self.assertEqual(snapshot, sorted(snapshot))
        
        # 所有after快照应该是排序的
        for snapshot in after:
            self.assertEqual(snapshot, sorted(snapshot))
    
    def test_snapshot_weight_sum(self):
        """测试快照权值总和"""
        model = HuffmanModel()
        weights = [1, 2, 3, 4, 5]
        total = sum(weights)
        
        root, steps, before, after = model.build_with_steps(weights)
        
        # 每个快照的权值总和应该保持不变
        for snapshot in before:
            self.assertAlmostEqual(sum(snapshot), total)
        
        for snapshot in after:
            self.assertAlmostEqual(sum(snapshot), total)


class TestHuffmanEdgeCases(unittest.TestCase):
    """Huffman边界情况测试"""
    
    def test_very_small_weights(self):
        """测试非常小的权值"""
        model = HuffmanModel()
        weights = [0.1, 0.2, 0.3]
        
        root, steps, before, after = model.build_with_steps(weights)
        
        self.assertIsNotNone(root)
        self.assertAlmostEqual(root.weight, 0.6)
    
    def test_large_weights(self):
        """测试大权值"""
        model = HuffmanModel()
        weights = [1000, 2000, 3000, 4000]
        
        root, steps, before, after = model.build_with_steps(weights)
        
        self.assertEqual(root.weight, 10000)
    
    def test_many_nodes(self):
        """测试大量节点"""
        model = HuffmanModel()
        weights = list(range(1, 21))  # 20个节点
        
        root, steps, before, after = model.build_with_steps(weights)
        
        self.assertEqual(root.weight, sum(weights))
        self.assertEqual(len(steps), 19)
    
    def test_float_weights(self):
        """测试浮点权值"""
        model = HuffmanModel()
        weights = [1.5, 2.7, 3.2, 4.8]
        
        root, steps, before, after = model.build_with_steps(weights)
        
        self.assertAlmostEqual(root.weight, sum(weights), places=6)


def run_huffman_tests():
    """运行所有Huffman树测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestHuffmanNode))
    suite.addTests(loader.loadTestsFromTestCase(TestHuffmanModel))
    suite.addTests(loader.loadTestsFromTestCase(TestHuffmanBuilding))
    suite.addTests(loader.loadTestsFromTestCase(TestHuffmanSnapshots))
    suite.addTests(loader.loadTestsFromTestCase(TestHuffmanEdgeCases))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "="*60)
    print("Huffman树测试结果摘要:")
    print(f"运行测试数: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print("="*60)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    print("="*60)
    print("运行栈测试...")
    print("="*60)
    stack_success = run_stack_tests()
    
    print("\n" + "="*60)
    print("运行Huffman树测试...")
    print("="*60)
    huffman_success = run_huffman_tests()
    
    print("\n" + "="*60)
    print("总体结果:")
    print(f"栈测试: {'✅ 通过' if stack_success else '❌ 失败'}")
    print(f"Huffman树测试: {'✅ 通过' if huffman_success else '❌ 失败'}")
    print("="*60)
    
    sys.exit(0 if (stack_success and huffman_success) else 1)

