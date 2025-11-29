import pygame
import random
import math
import sys
from enum import Enum

# 初始化pygame
pygame.init()

# 屏幕设置
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("安全驾驶诊断")

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 120, 255)
YELLOW = (255, 255, 0)
GRAY = (100, 100, 100)
DARK_GRAY = (50, 50, 50)
ROAD_COLOR = (40, 40, 40)

# 游戏状态
class GameState(Enum):
    START = 0
    PLAYING = 1
    RESULTS = 2

# 玩家车辆类
class PlayerCar:
    def __init__(self):
        self.width = 40
        self.height = 70
        self.x = SCREEN_WIDTH // 2 - self.width // 2
        self.y = SCREEN_HEIGHT - 100
        self.speed = 0
        self.max_speed = 8
        self.acceleration = 0.1
        self.deceleration = 0.2
        self.steering = 3
        self.color = BLUE
        self.score = 100  # 初始安全驾驶分数
        self.infractions = []  # 违规记录
        self.anger_level = 0  # 路怒症指数
        
    def draw(self, screen):
        # 绘制车辆主体
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        
        # 绘制车窗
        pygame.draw.rect(screen, DARK_GRAY, (self.x + 5, self.y + 5, self.width - 10, 15))
        
        # 绘制车轮
        pygame.draw.rect(screen, BLACK, (self.x - 3, self.y + 10, 6, 15))
        pygame.draw.rect(screen, BLACK, (self.x + self.width - 3, self.y + 10, 6, 15))
        pygame.draw.rect(screen, BLACK, (self.x - 3, self.y + self.height - 25, 6, 15))
        pygame.draw.rect(screen, BLACK, (self.x + self.width - 3, self.y + self.height - 25, 6, 15))
        
    def move(self, keys):
        # 加速和减速
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.speed = min(self.speed + self.acceleration, self.max_speed)
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.speed = max(self.speed - self.deceleration, 0)
        else:
            self.speed = max(self.speed - self.deceleration/2, 0)
            
        # 转向
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= self.steering * (self.speed / self.max_speed)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += self.steering * (self.speed / self.max_speed)
            
        # 限制车辆不超出屏幕
        self.x = max(150, min(self.x, SCREEN_WIDTH - 150 - self.width))
        
    def update_score(self, infraction_type, severity=1):
        self.score = max(0, self.score - severity)
        self.infractions.append(infraction_type)
        
        # 增加路怒症指数
        if infraction_type == "超速" or infraction_type == "危险超车":
            self.anger_level += 1

# 其他车辆类
class TrafficCar:
    def __init__(self, lane, speed):
        self.width = 40
        self.height = 70
        self.lane = lane
        self.x = 150 + lane * 100 + random.randint(-10, 10)
        self.y = -self.height
        self.speed = speed
        self.color = random.choice([RED, GREEN, YELLOW, (200, 100, 50)])
        
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        
        # 绘制车窗
        pygame.draw.rect(screen, DARK_GRAY, (self.x + 5, self.y + 5, self.width - 10, 15))
        
        # 绘制车轮
        pygame.draw.rect(screen, BLACK, (self.x - 3, self.y + 10, 6, 15))
        pygame.draw.rect(screen, BLACK, (self.x + self.width - 3, self.y + 10, 6, 15))
        pygame.draw.rect(screen, BLACK, (self.x - 3, self.y + self.height - 25, 6, 15))
        pygame.draw.rect(screen, BLACK, (self.x + self.width - 3, self.y + self.height - 25, 6, 15))
        
    def move(self):
        self.y += self.speed
        
    def is_off_screen(self):
        return self.y > SCREEN_HEIGHT

# 游戏类
class DrivingGame:
    def __init__(self):
        self.state = GameState.START
        self.player = PlayerCar()
        self.traffic = []
        self.road_offset = 0
        self.timer = 0
        self.game_duration = 60000  # 60秒游戏时间
        self.spawn_timer = 0
        self.spawn_delay = 1500  # 生成新车辆的延迟
        
    def draw_road(self):
        # 绘制道路
        pygame.draw.rect(screen, ROAD_COLOR, (150, 0, SCREEN_WIDTH - 300, SCREEN_HEIGHT))
        
        # 绘制道路标记
        for i in range(20):
            mark_y = (i * 100 + self.road_offset) % (SCREEN_HEIGHT + 200) - 100
            pygame.draw.rect(screen, YELLOW, (SCREEN_WIDTH // 2 - 5, mark_y, 10, 50))
            
        # 绘制车道线
        for i in range(1, 4):
            lane_x = 150 + i * 100
            for j in range(30):
                dash_y = (j * 40 + self.road_offset) % (SCREEN_HEIGHT + 40) - 20
                pygame.draw.rect(screen, WHITE, (lane_x, dash_y, 4, 20))
    
    def draw_hud(self):
        # 绘制速度表
        speed_text = f"速度: {int(self.player.speed * 20)} km/h"
        speed_surface = pygame.font.SysFont(None, 30).render(speed_text, True, WHITE)
        screen.blit(speed_surface, (50, 50))
        
        # 绘制分数
        score_text = f"安全分数: {self.player.score}"
        score_surface = pygame.font.SysFont(None, 30).render(score_text, True, WHITE)
        screen.blit(score_surface, (50, 90))
        
        # 绘制路怒症指数
        anger_text = f"路怒指数: {self.player.anger_level}/10"
        anger_surface = pygame.font.SysFont(None, 30).render(anger_text, True, WHITE)
        screen.blit(anger_surface, (50, 130))
        
        # 绘制时间
        time_left = max(0, (self.game_duration - self.timer) // 1000)
        time_text = f"剩余时间: {time_left}秒"
        time_surface = pygame.font.SysFont(None, 30).render(time_text, True, WHITE)
        screen.blit(time_surface, (SCREEN_WIDTH - 200, 50))
        
        # 绘制警告信息
        if self.player.speed > self.player.max_speed * 0.8:
            warning_text = "警告: 超速行驶!"
            warning_surface = pygame.font.SysFont(None, 36).render(warning_text, True, RED)
            screen.blit(warning_surface, (SCREEN_WIDTH // 2 - 100, 50))
    
    def draw_start_screen(self):
        screen.fill(BLACK)
        title_font = pygame.font.SysFont(None, 72)
        title = title_font.render("安全驾驶诊断", True, GREEN)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 150))
        
        instruction_font = pygame.font.SysFont(None, 36)
        instructions = [
            "使用方向键或WASD键控制车辆",
            "避免碰撞，遵守交通规则",
            "你的驾驶行为将被评估",
            "按空格键开始游戏"
        ]
        
        for i, line in enumerate(instructions):
            text = instruction_font.render(line, True, WHITE)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 300 + i * 50))
    
    def draw_results_screen(self):
        screen.fill(BLACK)
        title_font = pygame.font.SysFont(None, 72)
        title = title_font.render("诊断结果", True, GREEN)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))
        
        result_font = pygame.font.SysFont(None, 36)
        
        # 显示分数
        score_text = f"安全驾驶分数: {self.player.score}/100"
        score_color = GREEN if self.player.score >= 80 else YELLOW if self.player.score >= 60 else RED
        score_surface = result_font.render(score_text, True, score_color)
        screen.blit(score_surface, (SCREEN_WIDTH // 2 - score_surface.get_width() // 2, 200))
        
        # 显示路怒症指数
        anger_text = f"路怒症指数: {self.player.anger_level}/10"
        anger_color = GREEN if self.player.anger_level <= 3 else YELLOW if self.player.anger_level <= 6 else RED
        anger_surface = result_font.render(anger_text, True, anger_color)
        screen.blit(anger_surface, (SCREEN_WIDTH // 2 - anger_surface.get_width() // 2, 250))
        
        # 显示诊断结果
        if self.player.score >= 80 and self.player.anger_level <= 3:
            diagnosis = "优秀的安全驾驶员!"
            advice = "继续保持良好的驾驶习惯。"
        elif self.player.score >= 60:
            diagnosis = "基本安全的驾驶员"
            advice = "注意改进一些驾驶行为。"
        else:
            diagnosis = "需要改善驾驶行为"
            advice = "您可能有路怒症倾向，请寻求专业帮助。"
            
        diagnosis_surface = result_font.render(diagnosis, True, WHITE)
        screen.blit(diagnosis_surface, (SCREEN_WIDTH // 2 - diagnosis_surface.get_width() // 2, 320))
        
        advice_surface = result_font.render(advice, True, YELLOW)
        screen.blit(advice_surface, (SCREEN_WIDTH // 2 - advice_surface.get_width() // 2, 370))
        
        # 显示违规记录
        if self.player.infractions:
            infractions_text = "违规记录: " + ", ".join(set(self.player.infractions))
            infractions_surface = result_font.render(infractions_text, True, RED)
            screen.blit(infractions_surface, (SCREEN_WIDTH // 2 - infractions_surface.get_width() // 2, 450))
        
        restart_text = result_font.render("按R键重新开始游戏", True, WHITE)
        screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 550))
    
    def check_collisions(self):
        player_rect = pygame.Rect(self.player.x, self.player.y, self.player.width, self.player.height)
        
        for car in self.traffic:
            car_rect = pygame.Rect(car.x, car.y, car.width, car.height)
            if player_rect.colliderect(car_rect):
                self.player.update_score("碰撞", 20)
                self.traffic.remove(car)
                return True
        return False
    
    def check_speeding(self):
        if self.player.speed > self.player.max_speed * 0.8:
            self.player.update_score("超速", 1)
    
    def check_lane_discipline(self):
        # 检查是否频繁变道
        lane = (self.player.x - 150) // 100
        if hasattr(self, 'last_lane'):
            if lane != self.last_lane:
                self.player.update_score("频繁变道", 0.5)
        self.last_lane = lane
    
    def update(self, dt):
        if self.state == GameState.PLAYING:
            self.timer += dt
            self.road_offset += self.player.speed * 2
            
            # 生成新车辆
            self.spawn_timer += dt
            if self.spawn_timer >= self.spawn_delay:
                self.spawn_timer = 0
                lane = random.randint(0, 3)
                speed = random.uniform(3, 6)
                self.traffic.append(TrafficCar(lane, speed))
            
            # 更新车辆位置
            for car in self.traffic[:]:
                car.move()
                if car.is_off_screen():
                    self.traffic.remove(car)
            
            # 检查各种违规行为
            self.check_collisions()
            self.check_speeding()
            self.check_lane_discipline()
            
            # 检查游戏是否结束
            if self.timer >= self.game_duration or self.player.score <= 0:
                self.state = GameState.RESULTS
    
    def draw(self):
        screen.fill(BLACK)
        
        if self.state == GameState.START:
            self.draw_start_screen()
        elif self.state == GameState.PLAYING:
            self.draw_road()
            for car in self.traffic:
                car.draw(screen)
            self.player.draw(screen)
            self.draw_hud()
        elif self.state == GameState.RESULTS:
            self.draw_results_screen()
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and self.state == GameState.START:
                    self.state = GameState.PLAYING
                elif event.key == pygame.K_r and self.state == GameState.RESULTS:
                    self.__init__()  # 重置游戏
        
        if self.state == GameState.PLAYING:
            keys = pygame.key.get_pressed()
            self.player.move(keys)
            
        return True

# 主游戏循环
def main():
    clock = pygame.time.Clock()
    game = DrivingGame()
    
    running = True
    while running:
        dt = clock.tick(60)  # 限制帧率为60FPS
        
        running = game.handle_events()
        game.update(dt)
        game.draw()
        
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
