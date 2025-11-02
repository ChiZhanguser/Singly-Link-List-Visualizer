import unittest
import sys
import os

def run_all_tests():
    """运行所有测试"""
    # 添加项目路径
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # 发现并运行所有测试
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(os.path.abspath(__file__))
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出测试结果摘要
    print("\n" + "="*60)
    print("测试结果摘要:")
    print(f"运行测试数: {result.testsRun}")
    print(f"失败测试数: {len(result.failures)}")
    print(f"错误测试数: {len(result.errors)}")
    print(f"跳过测试数: {len(result.skipped)}")
    print("="*60)
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
