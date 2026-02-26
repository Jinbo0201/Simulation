import pygame
import sys
import random

# 初始化Pygame
pygame.init()

# 窗口设置
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pygame 动态可视化示例")

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# ===== 动态元素1：移动的小球 =====
ball_pos = [WIDTH // 2, HEIGHT // 2]  # 小球位置（用列表方便修改）
ball_radius = 30
ball_speed = [5, 3]  # 小球x/y方向速度（正数向右/下，负数向左/上）
ball_color = (255, 0, 0)  # 初始红色

# ===== 动态元素2：颜色渐变的背景色 =====
bg_hue = 0  # 色相值（0-360），用于渐变背景

# 帧率控制器
clock = pygame.time.Clock()
running = True

while running:
    # 控制帧率（每秒60帧，保证运动速度稳定）
    clock.tick(60)

    # 1. 事件处理（关闭窗口）
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 2. 更新动态元素状态（核心：每一帧都修改位置/颜色）
    # --- 小球移动逻辑 ---
    ball_pos[0] += ball_speed[0]  # x轴移动
    ball_pos[1] += ball_speed[1]  # y轴移动

    # 小球碰到窗口边界反弹
    if ball_pos[0] - ball_radius < 0 or ball_pos[0] + ball_radius > WIDTH:
        ball_speed[0] *= -1  # x轴速度反转（反弹）
        # 反弹时随机改变小球颜色
        ball_color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
    if ball_pos[1] - ball_radius < 0 or ball_pos[1] + ball_radius > HEIGHT:
        ball_speed[1] *= -1  # y轴速度反转（反弹）
        ball_color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))

    # --- 背景色渐变逻辑 ---
    bg_hue = (bg_hue + 1) % 360  # 色相值递增，超过360重置为0
    # 将色相转换为RGB颜色（实现彩虹渐变背景）
    bg_color = pygame.Color(0)
    bg_color.hsva = (bg_hue, 50, 90, 100)  # 色相、饱和度、明度、透明度

    # 3. 绘制所有元素（每一帧重新画）
    screen.fill(bg_color)  # 填充渐变背景

    # --- 绘制移动的小球 ---
    pygame.draw.circle(screen, ball_color, (int(ball_pos[0]), int(ball_pos[1])), ball_radius)

    # --- 绘制跟随鼠标的矩形 ---
    mouse_pos = pygame.mouse.get_pos()  # 获取当前鼠标位置
    rect_x = mouse_pos[0] - 50  # 矩形中心对齐鼠标x轴
    rect_y = mouse_pos[1] - 30  # 矩形中心对齐鼠标y轴
    pygame.draw.rect(screen, BLACK, (rect_x, rect_y, 100, 60), 3)  # 空心矩形

    # 4. 更新显示（必须调用，否则看不到变化）
    pygame.display.flip()

# 退出程序
pygame.quit()
sys.exit()