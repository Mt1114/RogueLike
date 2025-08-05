import pygame
import math
import random
from .resource_manager import resource_manager

class IntroAnimation:
    """开场动画类"""
    
    def __init__(self, screen):
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        
        # 动画状态
        self.is_playing = True
        self.animation_timer = 0
        self.total_duration = 10.0  # 总动画时长10秒
        
        # 加载logo
        original_logo = resource_manager.load_image('logo_white', 'images/ui/logo_white.png')
        
        # 计算logo大小（保持宽高比，最大宽度为屏幕宽度的40%）
        max_width = int(self.screen_width * 0.4)
        logo_width, logo_height = original_logo.get_size()
        scale_factor = min(max_width / logo_width, max_width / logo_width)
        new_width = int(logo_width * scale_factor)
        new_height = int(logo_height * scale_factor)
        self.logo = pygame.transform.scale(original_logo, (new_width, new_height))
        
        # 动画阶段参数
        self.pixelate_duration = 2.0    # 像素化时间
        self.assemble_duration = 5.0    # 拼装时间（延长到5秒）
        self.hold_duration = 2.0        # 保持时间
        self.fade_out_duration = 1.0    # 淡出时间
        
        # 粒子效果
        self.particles = []
        self._init_particles()
        
        # 像素块效果
        self.pixel_blocks = []
        self._init_pixel_blocks()
        
        # 状态标志
        self.pixelate_complete = False
        self.assemble_complete = False
        self.hold_complete = False
    
    def _get_random_border_position(self):
        """获取屏幕边框的随机位置"""
        # 随机选择边框的一边（0:上, 1:右, 2:下, 3:左）
        side = random.randint(0, 3)
        
        if side == 0:  # 上边框
            x = random.randint(0, self.screen_width)
            y = random.randint(-50, 0)
        elif side == 1:  # 右边框
            x = random.randint(self.screen_width, self.screen_width + 50)
            y = random.randint(0, self.screen_height)
        elif side == 2:  # 下边框
            x = random.randint(0, self.screen_width)
            y = random.randint(self.screen_height, self.screen_height + 50)
        else:  # 左边框
            x = random.randint(-50, 0)
            y = random.randint(0, self.screen_height)
        
        return x, y
        
    def _init_particles(self):
        """初始化粒子效果"""
        self.particles = []
        for i in range(200):  # 增加粒子数量
            angle = (i / 200) * 2 * math.pi
            speed = 1 + (i % 4) * 0.5  # 不同的速度
            
            particle = {
                'x': self.screen_width // 2,
                'y': self.screen_height // 2,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'life': 1.0 + (i % 2) * 0.5,
                'max_life': 1.0 + (i % 2) * 0.5,
                'size': 1 + (i % 3),
                'color': (255, 255, 255),
                'type': i % 3
            }
            self.particles.append(particle)
    
    def _init_pixel_blocks(self):
        """初始化像素块"""
        self.pixel_blocks = []
        block_size = 4  # 4x4像素块
        
        # 获取logo尺寸
        logo_width, logo_height = self.logo.get_size()
        
        # 计算logo在屏幕中心的位置
        self.logo_x = (self.screen_width - logo_width) // 2
        self.logo_y = (self.screen_height - logo_height) // 2
        
        # 创建像素块
        for y in range(0, logo_height, block_size):
            for x in range(0, logo_width, block_size):
                # 获取像素块区域
                rect = pygame.Rect(x, y, block_size, block_size)
                
                # 获取像素块的平均颜色
                color_sum = [0, 0, 0]
                pixel_count = 0
                
                for py in range(y, min(y + block_size, logo_height)):
                    for px in range(x, min(x + block_size, logo_width)):
                        try:
                            color = self.logo.get_at((px, py))
                            color_sum[0] += color[0]
                            color_sum[1] += color[1]
                            color_sum[2] += color[2]
                            pixel_count += 1
                        except IndexError:
                            pass
                
                if pixel_count > 0:
                    avg_color = (
                        int(color_sum[0] / pixel_count),
                        int(color_sum[1] / pixel_count),
                        int(color_sum[2] / pixel_count)
                    )
                else:
                    avg_color = (0, 0, 0)
                
                # 创建像素块，从屏幕边框随机位置开始
                start_x, start_y = self._get_random_border_position()
                block = {
                    'orig_x': x + self.logo_x,  # 原始位置
                    'orig_y': y + self.logo_y,
                    'x': start_x,  # 从边框随机位置开始
                    'y': start_y,
                    'target_x': x + self.logo_x,  # 目标位置
                    'target_y': y + self.logo_y,
                    'width': min(block_size, logo_width - x),
                    'height': min(block_size, logo_height - y),
                    'color': avg_color,
                    'speed': random.uniform(0.5, 2.0)  # 移动速度
                }
                self.pixel_blocks.append(block)
    
    def update(self, dt):
        """更新动画"""
        if not self.is_playing:
            return
            
        self.animation_timer += dt
        
        # 更新粒子
        for particle in self.particles:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= dt * 0.3
            
            # 粒子扩散效果
            distance = math.sqrt((particle['x'] - self.screen_width // 2) ** 2 + 
                               (particle['y'] - self.screen_height // 2) ** 2)
            
            # 根据粒子类型设置不同的行为
            if particle['type'] == 0:
                if distance < 300:
                    particle['vx'] *= 1.01
                    particle['vy'] *= 1.01
            elif particle['type'] == 1:
                angle = math.atan2(particle['y'] - self.screen_height // 2, 
                                 particle['x'] - self.screen_width // 2)
                particle['vx'] += math.cos(angle + 0.1) * 0.1
                particle['vy'] += math.sin(angle + 0.1) * 0.1
            else:
                particle['vx'] += (random.random() - 0.5) * 0.1
                particle['vy'] += (random.random() - 0.5) * 0.1
            
            # 限制粒子速度
            speed = math.sqrt(particle['vx']**2 + particle['vy']**2)
            if speed > 5:
                particle['vx'] = particle['vx'] / speed * 5
                particle['vy'] = particle['vy'] / speed * 5
        
        # 阶段1: 像素化 (0-2秒)
        if self.animation_timer < self.pixelate_duration:
            # 像素块向外扩散
            progress = self.animation_timer / self.pixelate_duration
            for block in self.pixel_blocks:
                # 从原始位置向随机位置移动
                block['x'] = block['orig_x'] + (block['x'] - block['orig_x']) * progress
                block['y'] = block['orig_y'] + (block['y'] - block['orig_y']) * progress
                
        # 阶段2: 拼装 (2-7秒) - 延长到5秒
        elif self.animation_timer < self.pixelate_duration + self.assemble_duration:
            if not self.pixelate_complete:
                self.pixelate_complete = True
                
            # 像素块向原始位置移动
            progress = (self.animation_timer - self.pixelate_duration) / self.assemble_duration
            
            # 使用缓动函数使移动更自然，添加一些随机性
            ease_progress = 1 - (1 - progress) ** 2  # 使用平方缓动
            
            for i, block in enumerate(self.pixel_blocks):
                # 为每个像素块添加不同的延迟
                block_delay = (i % 10) * 0.1  # 每10个块一组，每组延迟0.1秒
                adjusted_progress = max(0, (progress - block_delay) / (1 - block_delay)) if progress > block_delay else 0
                
                # 从当前位置向原始位置移动
                dx = block['target_x'] - block['x']
                dy = block['target_y'] - block['y']
                
                distance = math.sqrt(dx*dx + dy*dy)
                if distance > 1:
                    # 根据距离和进度调整移动速度
                    move_speed = min(block['speed'] * 15 * dt * adjusted_progress, distance * ease_progress)
                    
                    # 添加一些随机摆动
                    if adjusted_progress < 0.8:  # 在接近目标前添加摆动
                        swing = math.sin(self.animation_timer * 3 + i) * 2
                        block['x'] += swing * dt
                        block['y'] += swing * dt
                    
                    # 移动像素块
                    if distance > 0:
                        block['x'] += dx / distance * move_speed
                        block['y'] += dy / distance * move_speed
        
        # 阶段3: 保持显示 (7-9秒)
        elif self.animation_timer < self.pixelate_duration + self.assemble_duration + self.hold_duration:
            if not self.assemble_complete:
                self.assemble_complete = True
                # 确保所有像素块都在正确位置
                for block in self.pixel_blocks:
                    block['x'] = block['target_x']
                    block['y'] = block['target_y']
        
        # 阶段4: 淡出 (9-10秒)
        else:
            if not self.hold_complete:
                self.hold_complete = True
        
        # 检查动画是否结束
        if self.animation_timer >= self.total_duration:
            self.is_playing = False
    
    def render(self):
        """渲染动画"""
        # 纯黑色背景
        self.screen.fill((0, 0, 0))
        
        # 渲染粒子效果
        for particle in self.particles:
            if particle['life'] > 0:
                alpha = int(255 * (particle['life'] / particle['max_life']))
                
                if particle['type'] == 0:
                    color = (255, 255, 255, alpha)
                elif particle['type'] == 1:
                    color = (100, 150, 255, alpha)
                else:
                    color = (255, 200, 100, alpha)
                
                particle_surface = pygame.Surface((particle['size'] * 2, particle['size'] * 2), pygame.SRCALPHA)
                
                if particle['type'] == 0:
                    pygame.draw.circle(particle_surface, color, (particle['size'], particle['size']), particle['size'])
                elif particle['type'] == 1:
                    pygame.draw.rect(particle_surface, color, (0, 0, particle['size'] * 2, particle['size'] * 2))
                else:
                    points = [
                        (particle['size'], 0),
                        (particle['size'] * 2, particle['size']),
                        (particle['size'], particle['size'] * 2),
                        (0, particle['size'])
                    ]
                    pygame.draw.polygon(particle_surface, color, points)
                
                self.screen.blit(particle_surface, (particle['x'] - particle['size'], particle['y'] - particle['size']))
        
        # 计算整体透明度
        if self.animation_timer < self.pixelate_duration + self.assemble_duration + self.hold_duration:
            alpha = 255
        else:
            # 淡出阶段
            fade_out_progress = (self.animation_timer - self.pixelate_duration - self.assemble_duration - self.hold_duration) / self.fade_out_duration
            alpha = max(0, int(255 * (1 - fade_out_progress)))
        
        # 渲染像素块
        for block in self.pixel_blocks:
            # 创建像素块表面
            block_surface = pygame.Surface((block['width'], block['height']), pygame.SRCALPHA)
            block_surface.fill((*block['color'], alpha))
            
            # 添加发光效果
            if self.assemble_complete and not self.hold_complete:
                glow_alpha = int(100 * (0.5 + 0.5 * math.sin(self.animation_timer * 5)))
                pygame.draw.rect(block_surface, (255, 255, 255, glow_alpha), 
                                (0, 0, block['width'], block['height']), 1)
            
            self.screen.blit(block_surface, (block['x'], block['y']))
        
        # 在拼装完成后添加额外效果
        if self.assemble_complete and not self.hold_complete:
            # 添加logo周围的发光效果
            glow_radius = int(20 * (0.5 + 0.5 * math.sin(self.animation_timer * 3)))
            glow_surface = pygame.Surface((self.logo.get_width() + glow_radius * 2, 
                                          self.logo.get_height() + glow_radius * 2), 
                                         pygame.SRCALPHA)
            
            # 创建发光效果
            for i in range(glow_radius, 0, -1):
                alpha = int(50 * (i / glow_radius))
                pygame.draw.rect(glow_surface, (255, 255, 255, alpha), 
                                (glow_radius - i, glow_radius - i, 
                                 self.logo.get_width() + i * 2, 
                                 self.logo.get_height() + i * 2), 
                                i)
            
            self.screen.blit(glow_surface, (self.logo_x - glow_radius, self.logo_y - glow_radius))
    
    def is_finished(self):
        """检查动画是否结束"""
        return not self.is_playing 