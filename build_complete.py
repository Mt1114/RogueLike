import os
import sys
import subprocess
import shutil

def install_pyinstaller():
    """安装PyInstaller"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("PyInstaller安装成功")
        return True
    except subprocess.CalledProcessError:
        print("PyInstaller安装失败")
        return False

def check_assets():
    """检查assets文件夹是否存在"""
    if not os.path.exists("assets"):
        print("错误：assets文件夹不存在")
        return False
    
    # 检查关键资源文件
    required_files = [
        "assets/images/ui/logo_white.png",
        "assets/images/player/Ninja_frog_Idle_32x32.png",
        "assets/images/enemy/Slime_Idle_44x30.png"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("警告：以下文件不存在：")
        for file_path in missing_files:
            print(f"  - {file_path}")
        return False
    
    print("assets文件夹检查通过")
    return True

def build_exe():
    """打包游戏为exe"""
    
    # 检查PyInstaller是否已安装
    try:
        import PyInstaller
        print("PyInstaller已安装")
    except ImportError:
        print("PyInstaller未安装，正在安装...")
        if not install_pyinstaller():
            return False
    
    # 检查资源文件
    if not check_assets():
        print("资源文件检查失败，请确保assets文件夹完整")
        return False
    
    # 清理之前的构建文件
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("像素生存.spec"):
        os.remove("像素生存.spec")
    
    # 创建打包命令
    cmd = [
        "pyinstaller",
        "--onefile",  # 打包成单个exe文件
        "--windowed",  # 不显示控制台窗口
        "--name=像素生存",  # exe文件名
        "--add-data=assets;assets",  # 包含assets文件夹
        "--add-data=saves;saves",  # 包含saves文件夹
        "--hidden-import=pygame",
        "--hidden-import=pygame.mixer",
        "--hidden-import=numpy",
        "--hidden-import=pygame.sprite",
        "--hidden-import=pygame.image",
        "--hidden-import=pygame.transform",
        "--hidden-import=pygame.draw",
        "--hidden-import=pygame.font",
        "--hidden-import=pygame.time",
        "--hidden-import=pygame.event",
        "--hidden-import=pygame.display",
        "--hidden-import=pygame.key",
        "--hidden-import=pygame.mouse",
        "--hidden-import=pygame.rect",
        "--hidden-import=pygame.surface",
        "--hidden-import=pygame.color",
        "--hidden-import=pygame.math",
        "--hidden-import=pygame.vector2",
        "--collect-all=pygame",
        "--collect-all=numpy",
        "src/main.py"  # 主程序文件
    ]
    
    print("开始打包游戏...")
    print("打包命令:", " ".join(cmd))
    
    try:
        # 执行打包命令
        subprocess.check_call(cmd)
        print("打包成功！")
        
        # 检查生成的文件
        exe_path = "dist/像素生存.exe"
        if os.path.exists(exe_path):
            file_size = os.path.getsize(exe_path) / (1024*1024)
            print(f"exe文件已生成: {exe_path}")
            print(f"文件大小: {file_size:.2f} MB")
            
            # 创建发布文件夹
            release_dir = "release"
            if os.path.exists(release_dir):
                shutil.rmtree(release_dir)
            os.makedirs(release_dir)
            
            # 复制exe文件到发布文件夹
            shutil.copy2(exe_path, release_dir)
            print(f"exe文件已复制到: {release_dir}/像素生存.exe")
            
            return True
        else:
            print("未找到生成的exe文件")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"打包失败: {e}")
        return False

def create_readme():
    """创建发布说明文件"""
    readme_content = """# 像素生存游戏

## 游戏说明
这是一个像素风格的生存游戏，包含多种武器、敌人和地图。

## 运行要求
- Windows 7/8/10/11
- 不需要安装Python或其他依赖

## 操作说明
- WASD：移动角色
- 鼠标左键：攻击
- 鼠标右键：使用技能
- ESC：暂停/返回菜单
- 空格键：跳过开场动画

## 游戏特色
- 双角色系统
- 多种武器选择
- 随机地图生成
- 升级系统
- 存档功能

## 注意事项
- 首次运行可能需要较长时间
- 游戏会自动创建存档文件夹
- 支持全屏和窗口模式

## 技术支持
如有问题，请检查：
1. 是否以管理员身份运行
2. 杀毒软件是否拦截
3. 系统是否支持DirectX

祝您游戏愉快！
"""
    
    with open("release/README.txt", "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print("已创建README.txt文件")

def main():
    """主函数"""
    print("=== 完整游戏打包工具 ===")
    print("此工具将创建一个完整的可执行游戏文件")
    print("包含所有必要的资源和依赖")
    print()
    
    choice = input("是否开始打包？(Y/N): ").strip().upper()
    
    if choice == "Y":
        if build_exe():
            create_readme()
            print("\n=== 打包完成 ===")
            print("exe文件位置: release/像素生存.exe")
            print("说明文件位置: release/README.txt")
            print("\n现在可以将release文件夹中的文件分发给其他用户！")
            
            # 询问是否打开发布文件夹
            open_folder = input("\n是否打开release文件夹？(Y/N): ").strip().upper()
            if open_folder == "Y":
                os.startfile("release")
        else:
            print("打包失败，请检查错误信息")
    else:
        print("已取消打包")

if __name__ == "__main__":
    main() 