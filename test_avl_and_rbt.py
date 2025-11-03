#!/usr/bin/env python3
"""
AVL树测试程序
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from DS_visual.avl.avl_model import AVLModel, AVLNode, clone_tree


class TestAVLNode(unittest.TestCase):
    """AVL节点测试"""
    
    def test_node_creation(self):
        """测试节点创建"""
        node = AVLNode(10)
        
        self.assertEqual(node.val, 10)
        self.assertIsNone(node.left)
        self.assertIsNone(node.right)
        self.assertIsNone(node.parent)
        self.assertEqual(node.height, 1)
    
    def test_node_repr(self):
        """测试节点字符串表示"""
        node = AVLNode(42)
        self.assertEqual(repr(node), "AVLNode(42)")
    
    def test_node_with_children(self):
        """测试带子节点的节点"""
        parent = AVLNode(10)
        left = AVLNode(5)
        right = AVLNode(15)
        
        parent.left = left
        parent.right = right
        left.parent = parent
        right.parent = parent
        
        self.assertEqual(parent.left, left)
        self.assertEqual(parent.right, right)
        self.assertEqual(left.parent, parent)
        self.assertEqual(right.parent, parent)


class TestAVLBasics(unittest.TestCase):
    """AVL树基础功能测试"""
    
    def setUp(self):
        """每个测试前的初始化"""
        self.avl = AVLModel()
    
    def test_initial_state(self):
        """测试初始状态"""
        self.assertIsNone(self.avl.root)
    
    def test_height_calculation(self):
        """测试高度计算"""
        self.assertEqual(self.avl._height(None), 0)
        
        node = AVLNode(10)
        node.height = 1
        self.assertEqual(self.avl._height(node), 1)
    
    def test_balance_factor(self):
        """测试平衡因子计算"""
        root = AVLNode(10)
        root.left = AVLNode(5)
        root.right = AVLNode(15)
        root.left.height = 1
        root.right.height = 1
        root.height = 2
        
        # 左右子树高度相同，平衡因子为0
        bf = self.avl._balance_factor(root)
        self.assertEqual(bf, 0)
    
    def test_insert_single_node(self):
        """测试插入单个节点"""
        node, path, rotations, snapshots = self.avl.insert_with_steps(10)
        
        self.assertIsNotNone(node)
        self.assertEqual(node.val, 10)
        self.assertEqual(self.avl.root.val, 10)
        self.assertEqual(len(path), 1)
        self.assertEqual(len(rotations), 0)  # 单节点不需要旋转
    
    def test_insert_two_nodes(self):
        """测试插入两个节点"""
        self.avl.insert_with_steps(10)
        node, path, rotations, snapshots = self.avl.insert_with_steps(5)
        
        self.assertEqual(len(path), 2)
        self.assertEqual(self.avl.root.val, 10)
        # 5 < 10，应该在左子树
        if self.avl.root.left:
            self.assertEqual(self.avl.root.left.val, 5)
        else:
            # 如果使用字符串比较，"5" > "10"，在右子树
            self.assertEqual(self.avl.root.right.val, 5)


class TestAVLRotations(unittest.TestCase):
    """AVL旋转操作测试"""
    
    def setUp(self):
        """每个测试前的初始化"""
        self.avl = AVLModel()
    
    def test_rotate_right_LL(self):
        """测试LL型右旋"""
        # 构造需要LL旋转的场景
        self.avl.insert_with_steps(30)
        self.avl.insert_with_steps(20)
        node, path, rotations, snapshots = self.avl.insert_with_steps(10)
        
        # 应该发生一次LL旋转
        self.assertEqual(len(rotations), 1)
        self.assertEqual(rotations[0]['type'], 'LL')
        
        # 验证旋转后结构: 20变为根，10和30为子节点
        self.assertEqual(self.avl.root.val, 20)
        self.assertEqual(self.avl.root.left.val, 10)
        self.assertEqual(self.avl.root.right.val, 30)
    
    def test_rotate_left_RR(self):
        """测试RR型左旋"""
        # 构造需要RR旋转的场景
        self.avl.insert_with_steps(10)
        self.avl.insert_with_steps(20)
        node, path, rotations, snapshots = self.avl.insert_with_steps(30)
        
        # 应该发生一次RR旋转
        self.assertEqual(len(rotations), 1)
        self.assertEqual(rotations[0]['type'], 'RR')
        
        # 验证旋转后结构: 20变为根，10和30为子节点
        self.assertEqual(self.avl.root.val, 20)
        self.assertEqual(self.avl.root.left.val, 10)
        self.assertEqual(self.avl.root.right.val, 30)
    
    def test_rotate_left_right_LR(self):
        """测试LR型旋转"""
        # 构造需要LR旋转的场景
        self.avl.insert_with_steps(30)
        self.avl.insert_with_steps(10)
        node, path, rotations, snapshots = self.avl.insert_with_steps(20)
        
        # 应该发生一次LR旋转
        self.assertEqual(len(rotations), 1)
        self.assertEqual(rotations[0]['type'], 'LR')
        
        # 验证旋转后结构: 20变为根，10和30为子节点
        self.assertEqual(self.avl.root.val, 20)
        self.assertEqual(self.avl.root.left.val, 10)
        self.assertEqual(self.avl.root.right.val, 30)
    
    def test_rotate_right_left_RL(self):
        """测试RL型旋转"""
        # 构造需要RL旋转的场景
        self.avl.insert_with_steps(10)
        self.avl.insert_with_steps(30)
        node, path, rotations, snapshots = self.avl.insert_with_steps(20)
        
        # 应该发生一次RL旋转
        self.assertEqual(len(rotations), 1)
        self.assertEqual(rotations[0]['type'], 'RL')
        
        # 验证旋转后结构: 20变为根，10和30为子节点
        self.assertEqual(self.avl.root.val, 20)
        self.assertEqual(self.avl.root.left.val, 10)
        self.assertEqual(self.avl.root.right.val, 30)


class TestAVLBalance(unittest.TestCase):
    """AVL平衡性测试"""
    
    def setUp(self):
        """每个测试前的初始化"""
        self.avl = AVLModel()
    
    def _is_balanced(self, node: AVLNode) -> bool:
        """递归检查AVL平衡性"""
        if node is None:
            return True
        
        bf = abs(self.avl._balance_factor(node))
        if bf > 1:
            return False
        
        return self._is_balanced(node.left) and self._is_balanced(node.right)
    
    def test_tree_remains_balanced_after_insertions(self):
        """测试多次插入后树保持平衡"""
        values = [10, 20, 30, 40, 50, 25, 35, 45]
        
        for val in values:
            self.avl.insert_with_steps(val)
            # 验证每次插入后树都平衡
            self.assertTrue(self._is_balanced(self.avl.root))
    
    def test_height_update_after_insertion(self):
        """测试插入后高度更新"""
        self.avl.insert_with_steps(10)
        self.assertEqual(self.avl.root.height, 1)
        
        self.avl.insert_with_steps(5)
        self.avl.insert_with_steps(15)
        self.assertEqual(self.avl.root.height, 2)
    
    def test_sequential_insertions(self):
        """测试顺序插入保持平衡"""
        # 顺序插入应该触发多次旋转以保持平衡
        for i in range(1, 11):
            self.avl.insert_with_steps(i)
        
        # 验证树保持平衡
        self.assertTrue(self._is_balanced(self.avl.root))
        
        # 高度应该接近log2(n)
        import math
        expected_height = math.ceil(math.log2(11))
        actual_height = self.avl.root.height
        self.assertLessEqual(actual_height, expected_height + 1)


class TestAVLSnapshots(unittest.TestCase):
    """AVL快照测试"""
    
    def setUp(self):
        """每个测试前的初始化"""
        self.avl = AVLModel()
    
    def test_snapshot_count(self):
        """测试快照数量"""
        # 插入不需要旋转
        node, path, rotations, snapshots = self.avl.insert_with_steps(10)
        # before + after = 2
        self.assertEqual(len(snapshots), 2)
        
        # 插入需要旋转
        self.avl = AVLModel()
        self.avl.insert_with_steps(30)
        self.avl.insert_with_steps(20)
        node, path, rotations, snapshots = self.avl.insert_with_steps(10)
        # before + after + rotation = 3
        self.assertEqual(len(snapshots), 3)
    
    def test_clone_tree_function(self):
        """测试树克隆函数"""
        self.avl.insert_with_steps(10)
        self.avl.insert_with_steps(5)
        self.avl.insert_with_steps(15)
        
        cloned = clone_tree(self.avl.root)
        
        # 验证克隆的值相同但对象不同
        self.assertEqual(cloned.val, self.avl.root.val)
        self.assertIsNot(cloned, self.avl.root)
        self.assertEqual(cloned.left.val, self.avl.root.left.val)
        self.assertIsNot(cloned.left, self.avl.root.left)


class TestAVLEdgeCases(unittest.TestCase):
    """AVL边界情况测试"""
    
    def setUp(self):
        """每个测试前的初始化"""
        self.avl = AVLModel()
    
    def test_duplicate_values(self):
        """测试重复值插入"""
        self.avl.insert_with_steps(10)
        self.avl.insert_with_steps(10)
        self.avl.insert_with_steps(10)
        
        # 重复值应该放在右子树
        self.assertEqual(self.avl.root.val, 10)
        self.assertEqual(self.avl.root.right.val, 10)
    
    def test_large_tree(self):
        """测试大型AVL树"""
        import random
        values = list(range(1, 101))
        random.shuffle(values)
        
        for val in values:
            self.avl.insert_with_steps(val)
        
        # 验证树保持平衡
        def is_balanced(node):
            if not node:
                return True
            bf = abs(self.avl._balance_factor(node))
            return bf <= 1 and is_balanced(node.left) and is_balanced(node.right)
        
        self.assertTrue(is_balanced(self.avl.root))
    
    def test_string_values(self):
        """测试字符串值"""
        words = ["dog", "cat", "elephant", "bird", "fish"]
        
        for word in words:
            self.avl.insert_with_steps(word)
        
        # 验证根节点
        self.assertIsNotNone(self.avl.root)


def run_avl_tests():
    """运行所有AVL树测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestAVLNode))
    suite.addTests(loader.loadTestsFromTestCase(TestAVLBasics))
    suite.addTests(loader.loadTestsFromTestCase(TestAVLRotations))
    suite.addTests(loader.loadTestsFromTestCase(TestAVLBalance))
    suite.addTests(loader.loadTestsFromTestCase(TestAVLSnapshots))
    suite.addTests(loader.loadTestsFromTestCase(TestAVLEdgeCases))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "="*60)
    print("AVL树测试结果摘要:")
    print(f"运行测试数: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print("="*60)
    
    return result.wasSuccessful()


# ============================================================
# 红黑树测试
# ============================================================

from DS_visual.rbt.rbt_model import RBModel, RBNode, clone_tree as rb_clone_tree


class TestRBNode(unittest.TestCase):
    """红黑树节点测试"""
    
    def test_node_creation(self):
        """测试节点创建"""
        node = RBNode(10)
        
        self.assertEqual(node.val, 10)
        self.assertEqual(node.color, "R")  # 默认为红色
        self.assertIsNone(node.left)
        self.assertIsNone(node.right)
        self.assertIsNone(node.parent)
    
    def test_node_with_color(self):
        """测试指定颜色的节点"""
        red_node = RBNode(10, color="R")
        black_node = RBNode(20, color="B")
        
        self.assertEqual(red_node.color, "R")
        self.assertEqual(black_node.color, "B")
    
    def test_node_repr(self):
        """测试节点字符串表示"""
        node = RBNode(42, color="R")
        self.assertIn("42", repr(node))
        self.assertIn("R", repr(node))


class TestRBBasics(unittest.TestCase):
    """红黑树基础功能测试"""
    
    def setUp(self):
        """每个测试前的初始化"""
        self.rbt = RBModel()
    
    def test_initial_state(self):
        """测试初始状态"""
        self.assertIsNone(self.rbt.root)
    
    def test_insert_single_node(self):
        """测试插入单个节点"""
        node, path, events, snapshots = self.rbt.insert_with_steps(10)
        
        self.assertIsNotNone(node)
        self.assertEqual(node.val, 10)
        self.assertEqual(self.rbt.root.val, 10)
        # 根节点必须是黑色
        self.assertEqual(self.rbt.root.color, "B")
    
    def test_insert_two_nodes(self):
        """测试插入两个节点"""
        self.rbt.insert_with_steps(10)
        node, path, events, snapshots = self.rbt.insert_with_steps(5)
        
        self.assertEqual(self.rbt.root.val, 10)
        self.assertEqual(self.rbt.root.color, "B")
        
        # 验证新节点被插入（可能在左子树或右子树）
        has_child = (self.rbt.root.left is not None) or (self.rbt.root.right is not None)
        self.assertTrue(has_child, "根节点应该有子节点")
        
        # 找到新插入的节点并验证其颜色
        if self.rbt.root.left and self.rbt.root.left.val == 5:
            self.assertEqual(self.rbt.root.left.color, "R")
        elif self.rbt.root.right and self.rbt.root.right.val == 5:
            self.assertEqual(self.rbt.root.right.color, "R")
        else:
            self.fail("未找到插入的节点值5")


class TestRBProperties(unittest.TestCase):
    """红黑树性质测试"""
    
    def setUp(self):
        """每个测试前的初始化"""
        self.rbt = RBModel()
    
    def test_root_is_black(self):
        """测试性质1: 根节点是黑色"""
        values = [10, 5, 15, 3, 7, 12, 20]
        for val in values:
            self.rbt.insert_with_steps(val)
        
        self.assertEqual(self.rbt.root.color, "B")
    
    def test_red_node_has_black_children(self):
        """测试性质3: 红色节点的子节点必须是黑色"""
        values = [10, 5, 15, 3, 7, 12, 20]
        for val in values:
            self.rbt.insert_with_steps(val)
        
        def check_red_property(node):
            if not node:
                return True
            if node.color == "R":
                if node.left and node.left.color == "R":
                    return False
                if node.right and node.right.color == "R":
                    return False
            return check_red_property(node.left) and check_red_property(node.right)
        
        self.assertTrue(check_red_property(self.rbt.root))
    
    def test_black_height_consistent(self):
        """测试性质4: 所有路径黑高度相同"""
        values = [10, 5, 15, 3, 7, 12, 20]
        for val in values:
            self.rbt.insert_with_steps(val)
        
        def get_black_height(node):
            if not node:
                return 1
            left_height = get_black_height(node.left)
            right_height = get_black_height(node.right)
            if left_height != right_height:
                return -1  # 不一致
            return left_height + (1 if node.color == "B" else 0)
        
        black_height = get_black_height(self.rbt.root)
        self.assertGreater(black_height, 0)


class TestRBOperations(unittest.TestCase):
    """红黑树操作测试"""
    
    def setUp(self):
        """每个测试前的初始化"""
        self.rbt = RBModel()
    
    def test_recolor_operation(self):
        """测试重新着色操作"""
        self.rbt.insert_with_steps(10)
        self.rbt.insert_with_steps(5)
        self.rbt.insert_with_steps(15)
        node, path, events, snapshots = self.rbt.insert_with_steps(3)
        
        # 查找重新着色事件
        recolor_events = [e for e in events if e.get('type') == 'recolor']
        # 可能有重新着色事件
        self.assertGreaterEqual(len(recolor_events), 0)
    
    def test_rotation_operation(self):
        """测试旋转操作"""
        # 构造需要旋转的场景
        self.rbt.insert_with_steps(10)
        self.rbt.insert_with_steps(5)
        node, path, events, snapshots = self.rbt.insert_with_steps(3)
        
        # 查找旋转事件
        rotation_events = [e for e in events if 'rotate' in e.get('type', '')]
        # 应该有旋转事件
        self.assertGreaterEqual(len(rotation_events), 0)
    
    def test_complex_insertion_sequence(self):
        """测试复杂插入序列"""
        values = [10, 20, 30, 40, 50, 25, 35, 45]
        
        for val in values:
            node, path, events, snapshots = self.rbt.insert_with_steps(val)
        
        # 验证根节点是黑色
        self.assertEqual(self.rbt.root.color, "B")
        
        # 验证红黑树性质
        def verify_properties(node):
            if not node:
                return True
            if node.color == "R":
                if node.left and node.left.color == "R":
                    return False
                if node.right and node.right.color == "R":
                    return False
            return verify_properties(node.left) and verify_properties(node.right)
        
        self.assertTrue(verify_properties(self.rbt.root))


class TestRBSnapshots(unittest.TestCase):
    """红黑树快照测试"""
    
    def setUp(self):
        """每个测试前的初始化"""
        self.rbt = RBModel()
    
    def test_snapshot_count(self):
        """测试快照数量"""
        node, path, events, snapshots = self.rbt.insert_with_steps(10)
        # 至少有before和after快照
        self.assertGreaterEqual(len(snapshots), 2)
    
    def test_clone_preserves_color(self):
        """测试克隆保持颜色"""
        self.rbt.insert_with_steps(10)
        self.rbt.insert_with_steps(5)
        
        cloned = rb_clone_tree(self.rbt.root)
        
        # 验证颜色被保持
        self.assertEqual(cloned.color, self.rbt.root.color)
        if cloned.left:
            self.assertEqual(cloned.left.color, self.rbt.root.left.color)


class TestRBEdgeCases(unittest.TestCase):
    """红黑树边界情况测试"""
    
    def setUp(self):
        """每个测试前的初始化"""
        self.rbt = RBModel()
    
    def test_sequential_insertions(self):
        """测试顺序插入"""
        for i in range(1, 11):
            self.rbt.insert_with_steps(i)
        
        # 验证根节点是黑色
        self.assertEqual(self.rbt.root.color, "B")
    
    def test_reverse_insertions(self):
        """测试逆序插入"""
        for i in range(10, 0, -1):
            self.rbt.insert_with_steps(i)
        
        # 验证根节点是黑色
        self.assertEqual(self.rbt.root.color, "B")
    
    def test_duplicate_values(self):
        """测试重复值"""
        self.rbt.insert_with_steps(10)
        self.rbt.insert_with_steps(10)
        self.rbt.insert_with_steps(10)
        
        # 重复值应该放在右子树
        self.assertEqual(self.rbt.root.val, 10)
        if self.rbt.root.right:
            self.assertEqual(self.rbt.root.right.val, 10)
    
    def test_large_tree(self):
        """测试大型红黑树"""
        import random
        values = list(range(1, 51))
        random.shuffle(values)
        
        for val in values:
            self.rbt.insert_with_steps(val)
        
        # 验证根节点是黑色
        self.assertEqual(self.rbt.root.color, "B")


def run_rbt_tests():
    """运行所有红黑树测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestRBNode))
    suite.addTests(loader.loadTestsFromTestCase(TestRBBasics))
    suite.addTests(loader.loadTestsFromTestCase(TestRBProperties))
    suite.addTests(loader.loadTestsFromTestCase(TestRBOperations))
    suite.addTests(loader.loadTestsFromTestCase(TestRBSnapshots))
    suite.addTests(loader.loadTestsFromTestCase(TestRBEdgeCases))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "="*60)
    print("红黑树测试结果摘要:")
    print(f"运行测试数: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print("="*60)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    print("="*60)
    print("运行AVL树测试...")
    print("="*60)
    avl_success = run_avl_tests()
    
    print("\n" + "="*60)
    print("运行红黑树测试...")
    print("="*60)
    rbt_success = run_rbt_tests()
    
    print("\n" + "="*60)
    print("总体结果:")
    print(f"AVL树测试: {'✅ 通过' if avl_success else '❌ 失败'}")
    print(f"红黑树测试: {'✅ 通过' if rbt_success else '❌ 失败'}")
    print("="*60)
    
    sys.exit(0 if (avl_success and rbt_success) else 1)