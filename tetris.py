import pygame
import random

# 初始化 Pygame
pygame.init()

# 设置游戏窗口和网格
BLOCK_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
WINDOW_WIDTH = BLOCK_SIZE * (GRID_WIDTH + 8)
WINDOW_HEIGHT = BLOCK_SIZE * GRID_HEIGHT
GAME_AREA_X = BLOCK_SIZE * 2  # 游戏区域的x坐标

# 创建游戏窗口
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('俄罗斯方块')

# 定义颜色
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# 定义方块形状
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[1, 1, 1], [0, 1, 0]],  # T
    [[1, 1, 1], [1, 0, 0]],  # L
    [[1, 1, 1], [0, 0, 1]],  # J
    [[1, 1, 0], [0, 1, 1]],  # S
    [[0, 1, 1], [1, 1, 0]]   # Z
]

SHAPE_COLORS = [CYAN, YELLOW, PURPLE, BLUE, ORANGE, GREEN, RED]

# 创建游戏区域
grid = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

class Tetromino:
    def __init__(self):
        self.shape_idx = random.randrange(len(SHAPES))
        self.shape = SHAPES[self.shape_idx]
        self.color = SHAPE_COLORS[self.shape_idx]
        self.x = GRID_WIDTH // 2 - len(self.shape[0]) // 2
        self.y = 0
        self.rotation = 0

    def draw(self, surface, offset_x=0):
        for y, row in enumerate(self.shape):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(
                        surface,
                        self.color,
                        ((self.x + x) * BLOCK_SIZE + offset_x,
                         (self.y + y) * BLOCK_SIZE,
                         BLOCK_SIZE - 1,
                         BLOCK_SIZE - 1)
                    )

    def rotate(self):
        # 保存当前状态
        old_shape = self.shape
        # 获取矩阵尺寸
        rows = len(self.shape)
        cols = len(self.shape[0])
        # 创建新的旋转后的形状
        rotated = [[self.shape[rows-1-j][i] for j in range(rows)] for i in range(cols)]
        self.shape = rotated
        # 如果发生碰撞则恢复
        if self.check_collision():
            self.shape = old_shape

    def check_collision(self, dx=0, dy=0):
        for y, row in enumerate(self.shape):
            for x, cell in enumerate(row):
                if cell:
                    new_x = self.x + x + dx
                    new_y = self.y + y + dy
                    if (new_x < 0 or new_x >= GRID_WIDTH or
                        new_y >= GRID_HEIGHT or
                        (new_y >= 0 and grid[new_y][new_x] is not None)):
                        return True
        return False

def lock_piece(piece):
    for y, row in enumerate(piece.shape):
        for x, cell in enumerate(row):
            if cell:
                grid[piece.y + y][piece.x + x] = piece.color

def clear_lines():
    lines_cleared = 0
    y = GRID_HEIGHT - 1
    while y >= 0:
        if all(cell is not None for cell in grid[y]):
            lines_cleared += 1
            # 移动所有行下来
            for y2 in range(y, 0, -1):
                grid[y2] = grid[y2-1][:]
            # 创建新的空行
            grid[0] = [None] * GRID_WIDTH
        else:
            y -= 1
    return lines_cleared

def draw_grid():
    # 绘制游戏区域边框
    pygame.draw.rect(screen, WHITE, 
                    (GAME_AREA_X - 1, 0, 
                     GRID_WIDTH * BLOCK_SIZE + 2, 
                     GRID_HEIGHT * BLOCK_SIZE + 1), 1)
    
    # 绘制网格和已放置的方块
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if grid[y][x] is not None:
                pygame.draw.rect(
                    screen,
                    grid[y][x],
                    (x * BLOCK_SIZE + GAME_AREA_X,
                     y * BLOCK_SIZE,
                     BLOCK_SIZE - 1,
                     BLOCK_SIZE - 1)
                )

def draw_next_piece(next_piece):
    # 绘制"下一个"区域
    next_area_x = GAME_AREA_X + (GRID_WIDTH + 1) * BLOCK_SIZE
    next_area_y = BLOCK_SIZE * 2
    
    # 绘制标题
    font = pygame.font.Font(None, 36)
    text = font.render("下一个:", True, WHITE)
    screen.blit(text, (next_area_x, BLOCK_SIZE))
    
    # 绘制下一个方块
    for y, row in enumerate(next_piece.shape):
        for x, cell in enumerate(row):
            if cell:
                pygame.draw.rect(
                    screen,
                    next_piece.color,
                    (next_area_x + x * BLOCK_SIZE,
                     next_area_y + y * BLOCK_SIZE,
                     BLOCK_SIZE - 1,
                     BLOCK_SIZE - 1)
                )

def draw_score(score):
    font = pygame.font.Font(None, 36)
    text = font.render(f"分数: {score}", True, WHITE)
    screen.blit(text, (GAME_AREA_X + (GRID_WIDTH + 1) * BLOCK_SIZE, BLOCK_SIZE * 6))

def main():
    clock = pygame.time.Clock()
    current_piece = Tetromino()
    next_piece = Tetromino()
    fall_time = 0
    fall_speed = 1000  # 初始下落速度（毫秒）
    score = 0
    
    running = True
    while running:
        current_time = pygame.time.get_ticks()
        
        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    if not current_piece.check_collision(dx=-1):
                        current_piece.x -= 1
                elif event.key == pygame.K_RIGHT:
                    if not current_piece.check_collision(dx=1):
                        current_piece.x += 1
                elif event.key == pygame.K_DOWN:
                    if not current_piece.check_collision(dy=1):
                        current_piece.y += 1
                elif event.key == pygame.K_UP:
                    current_piece.rotate()
                elif event.key == pygame.K_SPACE:
                    # 硬降落
                    while not current_piece.check_collision(dy=1):
                        current_piece.y += 1
                    lock_piece(current_piece)
                    lines = clear_lines()
                    score += lines * 100
                    current_piece = next_piece
                    next_piece = Tetromino()
                    fall_time = current_time
        
        # 自动下落
        if current_time - fall_time > fall_speed:
            if not current_piece.check_collision(dy=1):
                current_piece.y += 1
            else:
                lock_piece(current_piece)
                lines = clear_lines()
                score += lines * 100
                current_piece = next_piece
                next_piece = Tetromino()
                # 检查游戏是否结束
                if current_piece.check_collision():
                    running = False
            fall_time = current_time
        
        # 绘制
        screen.fill(BLACK)
        draw_grid()
        current_piece.draw(screen, GAME_AREA_X)
        draw_next_piece(next_piece)
        draw_score(score)
        pygame.display.flip()
        
        clock.tick(60)
    
    # 游戏结束画面
    font = pygame.font.Font(None, 48)
    game_over_text = font.render("游戏结束!", True, WHITE)
    score_text = font.render(f"最终分数: {score}", True, WHITE)
    screen.blit(game_over_text, 
                (WINDOW_WIDTH//2 - game_over_text.get_width()//2, 
                 WINDOW_HEIGHT//2 - 50))
    screen.blit(score_text, 
                (WINDOW_WIDTH//2 - score_text.get_width()//2, 
                 WINDOW_HEIGHT//2 + 10))
    pygame.display.flip()
    
    # 等待几秒后退出
    pygame.time.wait(3000)
    pygame.quit()

if __name__ == "__main__":
    main()