import pygame
import sys
import os

def test_melee_attack_sound():
    """测试近战攻击音效"""
    print("开始测试近战攻击音效...")
    
    # 初始化pygame
    pygame.init()
    
    # 初始化音频系统
    try:
        pygame.mixer.init()
        print("✅ 音频系统初始化成功")
    except pygame.error as e:
        print(f"❌ 音频系统初始化失败: {e}")
        return False
    
    # 检查音效文件路径
    sound_file_path = "assets/sounds/melee_attack.wav"
    print(f"检查音效文件: {sound_file_path}")
    
    if os.path.exists(sound_file_path):
        print("✅ 音效文件存在")
    else:
        print("❌ 音效文件不存在")
        return False
    
    # 尝试加载音效
    try:
        sound = pygame.mixer.Sound(sound_file_path)
        print("✅ 音效加载成功")
    except pygame.error as e:
        print(f"❌ 音效加载失败: {e}")
        return False
    
    # 设置音量
    sound.set_volume(0.7)
    print("✅ 音量设置成功")
    
    # 播放音效
    try:
        print("🎵 播放近战攻击音效...")
        sound.play()
        
        # 等待音效播放完成
        import time
        time.sleep(3)  # 等待3秒
        
        print("✅ 音效播放完成")
        
    except pygame.error as e:
        print(f"❌ 音效播放失败: {e}")
        return False
    
    pygame.quit()
    return True

if __name__ == "__main__":
    test_melee_attack_sound() 