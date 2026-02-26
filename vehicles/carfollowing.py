import pygame
import numpy as np

# 初始化Pygame
pygame.init()

# -------------------------- 配置参数 --------------------------
# 窗口设置
WIDTH, HEIGHT = 800, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("IDM 跟驰模型动态演示")

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)    # 前车颜色
BLUE = (0, 0, 255)   # 后车颜色
GRAY = (200, 200, 200)  # 道路颜色

# 车辆尺寸
CAR_WIDTH = 40
CAR_HEIGHT = 20

# 道路位置（垂直居中）
ROAD_Y = HEIGHT // 2 - CAR_HEIGHT // 2

# 仿真参数
FPS = 30  # 帧率
dt = 0.2  # 时间步长（和原模型一致）
clock = pygame.time.Clock()

# -------------------------- 车辆类（复用IDM逻辑） --------------------------
class Vehicle:
    def __init__(self, position=0, speed=0):
        # IDM核心参数（和原代码一致）
        self.position = position  # 车辆x轴位置（像素）
        self.speed = speed        # 当前速度（像素/秒，原m/s映射为像素/秒）
        self.desired_speed = 150  # 期望速度（像素/秒，对应原15m/s）
        self.max_acc = 20         # 最大加速度（像素/秒²，对应原2m/s²）
        self.comf_decel = 20      # 舒适减速度（像素/秒²）
        self.min_gap = 20         # 最小安全间距（像素，对应原2m）
        self.time_headway = 1.5   # 期望车头时距（s）

    # IDM加速度计算（核心逻辑不变，仅单位适配像素）
    def calculate_acceleration(self, front_vehicle=None):
        if front_vehicle is None:
            delta = 1 - (self.speed / self.desired_speed) ** 2
            acc = self.max_acc * delta
        else:
            # 计算实际车头间距（减去车辆宽度）
            gap = front_vehicle.position - self.position - CAR_WIDTH
            # 期望安全间距
            desired_gap = self.min_gap + self.speed * self.time_headway + \
                          (self.speed * (self.speed - front_vehicle.speed)) / (2 * np.sqrt(self.max_acc * self.comf_decel))
            desired_gap = max(desired_gap, self.min_gap)
            
            delta = 1 - (self.speed / self.desired_speed) ** 2 - (desired_gap / gap) ** 2
            acc = self.max_acc * delta
        
        # 限制加速度范围
        acc = max(min(acc, self.max_acc), -100.0)  # 最大制动加速度-100
        return acc

    # 更新车辆状态
    def update(self, front_vehicle=None):
        acc = self.calculate_acceleration(front_vehicle)
        self.speed += acc * dt
        self.speed = max(self.speed, 0)  # 速度不能为负
        self.position += self.speed * dt
        
        # 边界处理：车辆超出窗口右侧后重置到左侧（循环道路）
        if self.position > WIDTH + CAR_WIDTH:
            self.position = -CAR_WIDTH

# -------------------------- 绘制工具函数 --------------------------
def draw_road():
    """绘制道路背景"""
    pygame.draw.rect(screen, GRAY, (0, ROAD_Y - 10, WIDTH, CAR_HEIGHT + 20))  # 道路主体
    pygame.draw.line(screen, WHITE, (0, ROAD_Y + CAR_HEIGHT // 2), (WIDTH, ROAD_Y + CAR_HEIGHT // 2), 2)  # 道路中心线

def draw_car(x, y, color):
    """绘制车辆（矩形+简化细节）"""
    pygame.draw.rect(screen, color, (x, y, CAR_WIDTH, CAR_HEIGHT))
    # 绘制车窗（白色小矩形）
    pygame.draw.rect(screen, WHITE, (x + 5, y + 5, CAR_WIDTH - 10, CAR_HEIGHT - 10))

def draw_info(lead_car, follow_car):
    """绘制文字信息（速度、间距）"""
    font = pygame.font.SysFont(None, 24)
    # 前车信息
    lead_text = font.render(f"speed: {lead_car.speed:.1f} px/s", True, BLACK)
    screen.blit(lead_text, (10, 10))
    # 后车信息
    follow_text = font.render(f"speed: {follow_car.speed:.1f} px/s", True, BLACK)
    screen.blit(follow_text, (10, 40))
    # 间距信息
    gap = lead_car.position - follow_car.position - CAR_WIDTH
    gap_text = font.render(f"gap: {gap:.1f} px", True, BLACK)
    screen.blit(gap_text, (10, 70))

# -------------------------- 主仿真循环 --------------------------
def main():
    # 初始化两车：前车初始位置200px，速度100px/s；后车初始位置50px，速度80px/s
    lead_car = Vehicle(position=200, speed=100)
    follow_car = Vehicle(position=50, speed=80)
    
    running = True
    while running:
        # 控制帧率
        clock.tick(FPS)
        
        # 事件处理（关闭窗口）
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # 清屏（白色背景）
        screen.fill(WHITE)
        
        # 绘制道路
        draw_road()
        
        # 更新车辆状态
        lead_car.update()  # 前车无前车，匀速（实际会按IDM维持期望速度）
        follow_car.update(lead_car)  # 后车跟随前车
        
        # 绘制车辆
        draw_car(lead_car.position, ROAD_Y, RED)
        draw_car(follow_car.position, ROAD_Y, BLUE)
        
        # 绘制信息面板
        draw_info(lead_car, follow_car)
        
        # 更新显示
        pygame.display.flip()
    
    # 退出Pygame
    pygame.quit()

if __name__ == "__main__":
    main()