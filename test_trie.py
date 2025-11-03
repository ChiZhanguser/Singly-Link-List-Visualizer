import unittest
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from DS_visual.trie.trie_model import TrieNode, TrieModel


class TestTrieNode(unittest.TestCase):
    """测试TrieNode基础功能"""
    
    def test_node_creation(self):
        """测试节点创建"""
        node = TrieNode('a')
        self.assertEqual(node.char, 'a')
        self.assertEqual(len(node.children), 0)
        self.assertFalse(node.is_end)
        self.assertIsNone(node.parent)
    
    def test_node_repr(self):
        """测试节点字符串表示"""
        node = TrieNode('b')
        node.is_end = True
        self.assertEqual(repr(node), "TrieNode('b', end=True)")
    
    def test_node_parent_link(self):
        """测试父子节点链接"""
        parent = TrieNode('a')
        child = TrieNode('b')
        child.parent = parent
        parent.children['b'] = child
        
        self.assertIn('b', parent.children)
        self.assertEqual(child.parent, parent)


class TestTrieBasics(unittest.TestCase):
    """测试Trie基本操作"""
    
    def setUp(self):
        """初始化测试"""
        self.trie = TrieModel()
    
    def test_empty_trie(self):
        """测试空Trie"""
        found, path = self.trie.search("hello")
        self.assertFalse(found)
        self.assertEqual(len(path), 0)
    
    def test_insert_single_word(self):
        """测试插入单个单词"""
        path = self.trie.insert("cat")
        self.assertEqual(len(path), 3)
        self.assertTrue(path[-1].is_end)
        
        found, search_path = self.trie.search("cat")
        self.assertTrue(found)
        self.assertEqual(len(search_path), 3)
    
    def test_insert_multiple_words(self):
        """测试插入多个单词"""
        words = ["cat", "car", "card", "dog", "dodge"]
        for word in words:
            self.trie.insert(word)
        
        for word in words:
            found, _ = self.trie.search(word)
            self.assertTrue(found, f"Word '{word}' should be found")
    
    def test_prefix_sharing(self):
        """测试前缀共享"""
        self.trie.insert("cat")
        self.trie.insert("car")
        
        # 'ca' 应该是共享前缀
        found, path = self.trie.search("ca")
        self.assertFalse(found)  # 不是完整单词
        self.assertEqual(len(path), 2)  # 但路径存在
        
        # 检查节点共享
        nodes_c = [node for node in self.trie.root.children.values() if node.char == 'c']
        self.assertEqual(len(nodes_c), 1)  # 只有一个 'c' 节点


class TestTrieSearch(unittest.TestCase):
    """测试Trie搜索功能"""
    
    def setUp(self):
        """初始化测试"""
        self.trie = TrieModel()
        words = ["apple", "app", "application", "apply"]
        for word in words:
            self.trie.insert(word)
    
    def test_search_existing_word(self):
        """测试搜索存在的单词"""
        found, path = self.trie.search("app")
        self.assertTrue(found)
        self.assertEqual(len(path), 3)
        self.assertTrue(path[-1].is_end)
    
    def test_search_non_existing_word(self):
        """测试搜索不存在的单词"""
        found, path = self.trie.search("banana")
        self.assertFalse(found)
        self.assertEqual(len(path), 0)
    
    def test_search_prefix_only(self):
        """测试搜索只是前缀的情况"""
        found, path = self.trie.search("appl")
        self.assertFalse(found)  # 不是完整单词
        self.assertEqual(len(path), 4)  # 路径存在
        self.assertFalse(path[-1].is_end)  # 但不是结束节点
    
    def test_search_longer_than_existing(self):
        """测试搜索比现有单词更长的情况"""
        found, path = self.trie.search("applications")
        self.assertFalse(found)
        # 路径只能到 "application" 的长度
        self.assertLess(len(path), len("applications"))


class TestTrieOperations(unittest.TestCase):
    """测试Trie复杂操作"""
    
    def setUp(self):
        """初始化测试"""
        self.trie = TrieModel()
    
    def test_clear_trie(self):
        """测试清空Trie"""
        words = ["hello", "world", "test"]
        for word in words:
            self.trie.insert(word)
        
        self.trie.clear()
        
        # 验证所有单词都不存在了
        for word in words:
            found, _ = self.trie.search(word)
            self.assertFalse(found)
        
        # 验证根节点已重置
        self.assertEqual(len(self.trie.root.children), 0)
    
    def test_collect_all_nodes(self):
        """测试收集所有节点"""
        words = ["cat", "car", "dog"]
        total_chars = sum(len(word) for word in words)
        
        for word in words:
            self.trie.insert(word)
        
        nodes = self.trie.collect_all_nodes()
        
        # 由于 "cat" 和 "car" 共享 "ca"，实际节点数会少于 total_chars
        # "cat"(3) + "car"(3) + "dog"(3) = 9，但 "ca" 共享，所以是 7
        expected_nodes = 7  # c-a-t, c-a-r, d-o-g
        self.assertEqual(len(nodes), expected_nodes)
    
    def test_nodes_by_level(self):
        """测试按层级组织节点"""
        words = ["cat", "car", "dog"]
        for word in words:
            self.trie.insert(word)
        
        levels = self.trie.nodes_by_level()
        
        # 第1层应该有 'c' 和 'd'
        self.assertEqual(len(levels[1]), 2)
        
        # 第2层应该有 'a' (从c来) 和 'o' (从d来)
        self.assertEqual(len(levels[2]), 2)
        
        # 第3层应该有 't', 'r', 'g'
        self.assertEqual(len(levels[3]), 3)
    
    def test_insert_duplicate_word(self):
        """测试插入重复单词"""
        self.trie.insert("test")
        path1 = self.trie.insert("test")
        
        # 第二次插入应该返回相同的路径
        self.assertEqual(len(path1), 4)
        self.assertTrue(path1[-1].is_end)
        
        # 验证没有创建额外节点
        nodes = self.trie.collect_all_nodes()
        self.assertEqual(len(nodes), 4)


class TestTrieEdgeCases(unittest.TestCase):
    """测试Trie边界情况"""
    
    def setUp(self):
        """初始化测试"""
        self.trie = TrieModel()
    
    def test_empty_string(self):
        """测试空字符串"""
        path = self.trie.insert("")
        self.assertEqual(len(path), 0)
        
        # 空串插入后，根节点被标记为is_end
        # 搜索空串应该返回True（因为根节点is_end=True）
        found, search_path = self.trie.search("")
        self.assertTrue(found)
        self.assertEqual(len(search_path), 0)
    
    def test_single_character(self):
        """测试单字符单词"""
        path = self.trie.insert("a")
        self.assertEqual(len(path), 1)
        self.assertTrue(path[0].is_end)
        
        found, _ = self.trie.search("a")
        self.assertTrue(found)
    
    def test_long_word(self):
        """测试长单词"""
        long_word = "a" * 100
        path = self.trie.insert(long_word)
        self.assertEqual(len(path), 100)
        
        found, search_path = self.trie.search(long_word)
        self.assertTrue(found)
        self.assertEqual(len(search_path), 100)
    
    def test_special_characters(self):
        """测试特殊字符"""
        words = ["hello-world", "test_case", "file.txt", "a@b"]
        for word in words:
            self.trie.insert(word)
        
        for word in words:
            found, _ = self.trie.search(word)
            self.assertTrue(found, f"Word '{word}' should be found")
    
    def test_numbers_in_words(self):
        """测试包含数字的单词"""
        words = ["abc123", "test1", "2pac", "100"]
        for word in words:
            self.trie.insert(word)
        
        for word in words:
            found, _ = self.trie.search(word)
            self.assertTrue(found)


class TestTrieParentLinks(unittest.TestCase):
    """测试Trie父节点链接"""
    
    def setUp(self):
        """初始化测试"""
        self.trie = TrieModel()
    
    def test_parent_links_consistency(self):
        """测试父节点链接一致性"""
        path = self.trie.insert("test")
        
        # 验证每个节点的parent指向正确
        for i in range(len(path)):
            if i == 0:
                self.assertEqual(path[i].parent, self.trie.root)
            else:
                self.assertEqual(path[i].parent, path[i-1])
    
    def test_shared_prefix_parent(self):
        """测试共享前缀的父节点"""
        self.trie.insert("cat")
        self.trie.insert("car")
        
        # 获取 'c' 和 'a' 节点
        c_node = self.trie.root.children['c']
        a_node = c_node.children['a']
        
        # 't' 和 'r' 应该有相同的父节点 'a'
        t_node = a_node.children['t']
        r_node = a_node.children['r']
        
        self.assertEqual(t_node.parent, a_node)
        self.assertEqual(r_node.parent, a_node)


class TestTrieStructure(unittest.TestCase):
    """测试Trie结构验证"""
    
    def setUp(self):
        """初始化测试"""
        self.trie = TrieModel()
    
    def test_word_count(self):
        """测试单词计数"""
        words = ["apple", "app", "application", "banana", "band"]
        for word in words:
            self.trie.insert(word)
        
        # 统计is_end为True的节点数
        all_nodes = self.trie.collect_all_nodes()
        word_count = sum(1 for node in all_nodes if node.is_end)
        
        self.assertEqual(word_count, len(words))
    
    def test_tree_height(self):
        """测试树的高度"""
        words = ["a", "ab", "abc", "abcd"]
        for word in words:
            self.trie.insert(word)
        
        levels = self.trie.nodes_by_level()
        max_depth = max(levels.keys()) if levels else 0
        
        # 最长单词 "abcd" 有4个字符
        self.assertEqual(max_depth, 4)
    
    def test_branching_factor(self):
        """测试分支因子"""
        # 插入共享前缀但末尾不同的单词
        words = ["cat", "car", "can", "cab"]
        for word in words:
            self.trie.insert(word)
        
        # 'ca' 节点应该有4个子节点
        c_node = self.trie.root.children['c']
        a_node = c_node.children['a']
        
        self.assertEqual(len(a_node.children), 4)


def run_tests():
    """运行所有测试"""
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加所有测试类
    suite.addTests(loader.loadTestsFromTestCase(TestTrieNode))
    suite.addTests(loader.loadTestsFromTestCase(TestTrieBasics))
    suite.addTests(loader.loadTestsFromTestCase(TestTrieSearch))
    suite.addTests(loader.loadTestsFromTestCase(TestTrieOperations))
    suite.addTests(loader.loadTestsFromTestCase(TestTrieEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestTrieParentLinks))
    suite.addTests(loader.loadTestsFromTestCase(TestTrieStructure))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 打印总结
    print("\n" + "="*70)
    print(f"测试完成! 总计: {result.testsRun} 个测试")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print("="*70)
    
    return result


if __name__ == '__main__':
    run_tests()



def test_search_prefix_only(self):
    """测试搜索只是前缀的情况"""
    # 先插入 ["apple", "app", "application", "apply"]
    found, path = self.trie.search("appl")
    self.assertFalse(found)  # 不是完整单词
    self.assertEqual(len(path), 4)  # 路径存在
    self.assertFalse(path[-1].is_end)  # 但不是结束节点