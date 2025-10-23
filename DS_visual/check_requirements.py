# requirements_check.py
import sys
import subprocess
import pkg_resources

def check_and_install_packages():
    """检查并安装必要的包"""
    required_packages = [
        'Pillow>=8.0.0'  # 用于图片处理
    ]
    
    installed_packages = {pkg.key for pkg in pkg_resources.working_set}
    
    for package in required_packages:
        package_name = package.split('>=')[0].lower()
        if package_name not in installed_packages:
            try:
                print(f"正在安装 {package}...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"成功安装 {package}")
            except subprocess.CalledProcessError:
                print(f"安装 {package} 失败，请手动安装: pip install {package}")
                return False
    return True

if __name__ == "__main__":
    check_and_install_packages()