import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from DS_visual.binary_tree.bst.bst_model import BSTModel, TreeNode


class TestTreeNode(unittest.TestCase):
    """测试 TreeNode 类"""
    
    def test_node_creation(self):
        """测试节点创建"""
        node = TreeNode(10)
        self.assertEqual(node.val, 10)
        self.assertIsNone(node.left)
        self.assertIsNone(node.right)
        self.assertIsNone(node.parent)
    
    def test_node_repr(self):
        """测试节点字符串表示"""
        node = TreeNode(5)
        self.assertEqual(repr(node), "TreeNode(5)")
    
    def test_node_with_different_types(self):
        """测试不同类型的节点值"""
        int_node = TreeNode(42)
        str_node = TreeNode("hello")
        float_node = TreeNode(3.14)
        
        self.assertEqual(int_node.val, 42)
        self.assertEqual(str_node.val, "hello")
        self.assertEqual(float_node.val, 3.14)


class TestBSTModel(unittest.TestCase):
    """测试 BSTModel 类"""
    
    def setUp(self):
        """每个测试前的初始化"""
        self.bst = BSTModel()
    
    def test_initial_state(self):
        """测试初始状态"""
        self.assertIsNone(self.bst.root)
    
    def test_compare_values_integers(self):
        """测试整数比较"""
        self.assertEqual(self.bst.compare_values(5, 10), -1)
        self.assertEqual(self.bst.compare_values(10, 5), 1)
        self.assertEqual(self.bst.compare_values(5, 5), 0)
    
    def test_compare_values_strings(self):
        """测试字符串比较"""
        self.assertEqual(self.bst.compare_values("apple", "banana"), -1)
        self.assertEqual(self.bst.compare_values("banana", "apple"), 1)
        self.assertEqual(self.bst.compare_values("apple", "apple"), 0)
    
    def test_compare_values_mixed_types(self):
        """测试混合类型比较"""
        # 混合类型应该降级到字符串比较
        result = self.bst.compare_values(5, "hello")
        self.assertIn(result, [-1, 0, 1])
    
    def test_insert_single_node(self):
        """测试插入单个节点"""
        node = self.bst.insert(10)
        self.assertIsNotNone(node)
        self.assertEqual(node.val, 10)
        self.assertEqual(self.bst.root.val, 10)
    
    def test_insert_multiple_nodes(self):
        """测试插入多个节点"""
        values = [15, 6, 23, 4, 7, 71, 5]
        for val in values:
            self.bst.insert(val)
        
        # 验证根节点
        self.assertEqual(self.bst.root.val, 15)
        
        # 验证左子树
        self.assertEqual(self.bst.root.left.val, 6)
        self.assertEqual(self.bst.root.left.left.val, 4)
        self.assertEqual(self.bst.root.left.right.val, 7)
        
        # 验证右子树
        self.assertEqual(self.bst.root.right.val, 23)
        self.assertEqual(self.bst.root.right.right.val, 71)
    
    def test_insert_duplicate_values(self):
        """测试插入重复值（应该放在右子树）"""
        self.bst.insert(10)
        self.bst.insert(10)
        self.bst.insert(10)
        
        # 重复值应该在右子树
        self.assertEqual(self.bst.root.val, 10)
        self.assertEqual(self.bst.root.right.val, 10)
        self.assertEqual(self.bst.root.right.right.val, 10)
    
    def test_parent_pointers(self):
        """测试父节点指针"""
        self.bst.insert(10)
        left = self.bst.insert(5)
        right = self.bst.insert(15)
        
        self.assertIsNone(self.bst.root.parent)
        self.assertEqual(left.parent, self.bst.root)
        self.assertEqual(right.parent, self.bst.root)
    
    def test_search_existing_value(self):
        """测试查找存在的值"""
        values = [15, 6, 23, 4, 7, 71]
        for val in values:
            self.bst.insert(val)
        
        node, path = self.bst.search_with_path(7)
        self.assertIsNotNone(node)
        self.assertEqual(node.val, 7)
        self.assertGreater(len(path), 0)
        self.assertEqual(path[-1].val, 7)
    
    def test_search_non_existing_value(self):
        """测试查找不存在的值"""
        values = [15, 6, 23, 4, 7, 71]
        for val in values:
            self.bst.insert(val)
        
        node, path = self.bst.search_with_path(100)
        self.assertIsNone(node)
        self.assertGreater(len(path), 0)
    
    def test_search_empty_tree(self):
        """测试在空树中查找"""
        node, path = self.bst.search_with_path(10)
        self.assertIsNone(node)
        self.assertEqual(len(path), 0)
    
    def test_find_min(self):
        """测试查找最小值"""
        values = [15, 6, 23, 4, 7, 71, 5]
        for val in values:
            self.bst.insert(val)
        
        min_node = self.bst.find_min(self.bst.root)
        self.assertEqual(min_node.val, 4)
    
    def test_find_min_single_node(self):
        """测试单节点树的最小值"""
        self.bst.insert(10)
        min_node = self.bst.find_min(self.bst.root)
        self.assertEqual(min_node.val, 10)
    
    def test_delete_leaf_node(self):
        """测试删除叶子节点"""
        values = [15, 6, 23, 4, 7]
        for val in values:
            self.bst.insert(val)
        
        success, path = self.bst.delete(4)
        self.assertTrue(success)
        
        # 验证节点已删除
        node, _ = self.bst.search_with_path(4)
        self.assertIsNone(node)
        
        # 验证父节点的左子节点为空
        self.assertIsNone(self.bst.root.left.left)
    
    def test_delete_node_with_one_child(self):
        """测试删除只有一个子节点的节点"""
        values = [15, 6, 23, 4]
        for val in values:
            self.bst.insert(val)
        
        success, path = self.bst.delete(6)
        self.assertTrue(success)
        
        # 验证节点已删除
        node, _ = self.bst.search_with_path(6)
        self.assertIsNone(node)
        
        # 验证子节点提升
        self.assertEqual(self.bst.root.left.val, 4)
    
    def test_delete_node_with_two_children(self):
        """测试删除有两个子节点的节点"""
        values = [15, 6, 23, 4, 7, 20, 30]
        for val in values:
            self.bst.insert(val)
        
        success, path = self.bst.delete(23)
        self.assertTrue(success)
        
        # 验证节点已删除
        node, _ = self.bst.search_with_path(23)
        self.assertIsNone(node)
        
        # 验证后继节点替换
        self.assertEqual(self.bst.root.right.val, 30)
        self.assertEqual(self.bst.root.right.left.val, 20)
    
    def test_delete_root_node(self):
        """测试删除根节点"""
        self.bst.insert(10)
        success, path = self.bst.delete(10)
        self.assertTrue(success)
        self.assertIsNone(self.bst.root)
    
    def test_delete_root_with_children(self):
        """测试删除有子节点的根节点"""
        values = [15, 6, 23, 4, 7, 20, 30]
        for val in values:
            self.bst.insert(val)
        
        success, path = self.bst.delete(15)
        self.assertTrue(success)
        
        # 根应该被后继节点替换
        self.assertIsNotNone(self.bst.root)
        self.assertNotEqual(self.bst.root.val, 15)
    
    def test_delete_non_existing_value(self):
        """测试删除不存在的值"""
        values = [15, 6, 23]
        for val in values:
            self.bst.insert(val)
        
        success, path = self.bst.delete(100)
        self.assertFalse(success)
    
    def test_delete_from_empty_tree(self):
        """测试从空树删除"""
        success, path = self.bst.delete(10)
        self.assertFalse(success)
    
    def test_complex_operations(self):
        """测试复杂操作序列"""
        # 插入
        values = [50, 30, 70, 20, 40, 60, 80, 10, 25, 35, 65]
        for val in values:
            self.bst.insert(val)
        
        # 查找
        node, _ = self.bst.search_with_path(35)
        self.assertIsNotNone(node)
        self.assertEqual(node.val, 35)
        
        # 删除叶子节点
        self.bst.delete(10)
        node, _ = self.bst.search_with_path(10)
        self.assertIsNone(node)
        
        # 删除有一个子节点的节点
        self.bst.delete(20)
        node, _ = self.bst.search_with_path(20)
        self.assertIsNone(node)
        
        # 删除有两个子节点的节点
        self.bst.delete(30)
        node, _ = self.bst.search_with_path(30)
        self.assertIsNone(node)
        
        # 验证剩余节点
        remaining = [50, 70, 40, 60, 80, 25, 35, 65]
        for val in remaining:
            node, _ = self.bst.search_with_path(val)
            self.assertIsNotNone(node, f"Value {val} should exist")


class TestBSTProperties(unittest.TestCase):
    """测试BST的属性"""
    
    def setUp(self):
        """每个测试前的初始化"""
        self.bst = BSTModel()
    
    def _inorder_traversal(self, node, result):
        """中序遍历辅助函数"""
        if node:
            self._inorder_traversal(node.left, result)
            result.append(node.val)
            self._inorder_traversal(node.right, result)
    
    def test_bst_property_after_insertions(self):
        """测试插入后的BST性质（中序遍历应该有序）"""
        values = [15, 6, 23, 4, 7, 71, 5, 18, 25]
        for val in values:
            self.bst.insert(val)
        
        result = []
        self._inorder_traversal(self.bst.root, result)
        
        # 中序遍历应该是升序（允许重复）
        for i in range(len(result) - 1):
            self.assertLessEqual(result[i], result[i + 1])
    
    def test_bst_property_after_deletions(self):
        """测试删除后的BST性质"""
        values = [50, 30, 70, 20, 40, 60, 80]
        for val in values:
            self.bst.insert(val)
        
        # 删除几个节点
        self.bst.delete(30)
        self.bst.delete(70)
        
        result = []
        self._inorder_traversal(self.bst.root, result)
        
        # 中序遍历仍应该有序
        for i in range(len(result) - 1):
            self.assertLessEqual(result[i], result[i + 1])
    
    def test_tree_height(self):
        """测试树的高度"""
        def height(node):
            if not node:
                return 0
            return 1 + max(height(node.left), height(node.right))
        
        # 平衡插入
        values = [15, 6, 23, 4, 7, 18, 25]
        for val in values:
            self.bst.insert(val)
        
        h = height(self.bst.root)
        self.assertGreater(h, 0)
        self.assertLessEqual(h, len(values))
    
    def test_node_count(self):
        """测试节点数量"""
        def count_nodes(node):
            if not node:
                return 0
            return 1 + count_nodes(node.left) + count_nodes(node.right)
        
        values = [15, 6, 23, 4, 7, 71, 5]
        for val in values:
            self.bst.insert(val)
        
        count = count_nodes(self.bst.root)
        self.assertEqual(count, len(values))
        
        # 删除一个节点
        self.bst.delete(4)
        count = count_nodes(self.bst.root)
        self.assertEqual(count, len(values) - 1)


class TestEdgeCases(unittest.TestCase):
    """测试边界情况"""
    
    def setUp(self):
        """每个测试前的初始化"""
        self.bst = BSTModel()
    
    def test_large_tree(self):
        """测试大型树"""
        import random
        values = list(range(1, 101))
        random.shuffle(values)
        
        for val in values:
            self.bst.insert(val)
        
        # 验证所有值都能找到
        for val in values:
            node, _ = self.bst.search_with_path(val)
            self.assertIsNotNone(node)
    
    def test_sequential_insertions(self):
        """测试顺序插入（会产生不平衡树）"""
        values = list(range(1, 11))
        for val in values:
            self.bst.insert(val)
        
        # 树应该是右斜的
        current = self.bst.root
        count = 0
        while current:
            count += 1
            current = current.right
        
        self.assertEqual(count, len(values))
    
    def test_reverse_sequential_insertions(self):
        """测试逆序插入（会产生左斜树）"""
        values = list(range(10, 0, -1))
        for val in values:
            self.bst.insert(val)
        
        # 树应该是左斜的
        current = self.bst.root
        count = 0
        while current:
            count += 1
            current = current.left
        
        self.assertEqual(count, len(values))
    
    def test_string_values(self):
        """测试字符串值"""
        values = ["dog", "cat", "elephant", "bird", "fish"]
        for val in values:
            self.bst.insert(val)
        
        # 查找
        node, _ = self.bst.search_with_path("cat")
        self.assertIsNotNone(node)
        self.assertEqual(node.val, "cat")
        
        # 删除
        success, _ = self.bst.delete("elephant")
        self.assertTrue(success)
        
        node, _ = self.bst.search_with_path("elephant")
        self.assertIsNone(node)


def run_bst_tests():
    """运行所有BST测试"""
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加所有测试类
    suite.addTests(loader.loadTestsFromTestCase(TestTreeNode))
    suite.addTests(loader.loadTestsFromTestCase(TestBSTModel))
    suite.addTests(loader.loadTestsFromTestCase(TestBSTProperties))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出摘要
    print("\n" + "="*60)
    print("BST 测试结果摘要:")
    print(f"运行测试数: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print("="*60)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_bst_tests()
    sys.exit(0 if success else 1)