import pygame
import random

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Set up the display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Breakout")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
PURPLE = (128, 0, 128)
BRICK_COLORS = [RED, ORANGE, YELLOW, GREEN, BLUE]

# Game objects
# Paddle
paddle_x, paddle_y = WIDTH // 2 - 50, HEIGHT - 40
paddle_width, paddle_height = 100, 20
base_paddle_speed = 5
paddle_speed = base_paddle_speed
base_paddle_width = 100

# Ball
ball_x, ball_y = WIDTH // 2, HEIGHT // 2
ball_radius = 10
ball_vx, ball_vy = 0, 0
base_ball_speed = 4

# Bricks
brick_width, brick_height = 80, 30
bricks = [[1 for _ in range(WIDTH // brick_width)] for _ in range(5)]

# Power-ups
powerup_size = 20
powerup_speed = 2
powerups = []  # [x, y, type, timer]
powerup_duration = 600  # ~10 seconds at 60 FPS

# Game state
lives = 3
font = pygame.font.Font(None, 36)
game_over = False
ball_moving = False
faster_paddle_timer = 0  # Separate timer for Faster Paddle
wider_paddle_timer = 0   # Separate timer for Wider Paddle

# Sound effects
def create_beep_sound(frequency, duration=100):
    sample_rate = 44100
    samples = int(sample_rate * duration / 1000)
    buffer = bytearray()
    for i in range(samples):
        value = int(127 * (1 + (i * frequency % sample_rate > sample_rate // 2) - 0.5))
        buffer.append(value)
    return pygame.mixer.Sound(buffer)

paddle_sound = create_beep_sound(800, 100)
brick_sound = create_beep_sound(200, 150)
life_sound = create_beep_sound(300, 200)
powerup_sound = create_beep_sound(1000, 150)
for sound in [paddle_sound, brick_sound, life_sound, powerup_sound]:
    sound.set_volume(0.3)

# Draw power-ups with distinct shapes
def draw_powerup(x, y, powerup_type):
    if powerup_type == 0:  # Extra Life - Green Circle
        pygame.draw.circle(screen, GREEN, (int(x + powerup_size // 2), int(y + powerup_size // 2)), powerup_size // 2)
    elif powerup_type == 1:  # Faster Paddle - Blue Square
        pygame.draw.rect(screen, BLUE, (x, y, powerup_size, powerup_size))
    elif powerup_type == 2:  # Wider Paddle - Purple Triangle
        points = [(x + powerup_size // 2, y), (x, y + powerup_size), (x + powerup_size, y + powerup_size)]
        pygame.draw.polygon(screen, PURPLE, points)

# Game loop
clock = pygame.time.Clock()
running = True

while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not game_over and not ball_moving:
                ball_vx, ball_vy = base_ball_speed, -base_ball_speed
                ball_moving = True
            if event.key == pygame.K_r and game_over:
                # Reset game
                paddle_x = WIDTH // 2 - 50
                paddle_width = base_paddle_width
                paddle_speed = base_paddle_speed
                ball_x, ball_y = WIDTH // 2, HEIGHT // 2
                ball_vx, ball_vy = 0, 0
                ball_moving = False
                bricks = [[1 for _ in range(WIDTH // brick_width)] for _ in range(5)]
                powerups = []
                faster_paddle_timer = 0
                wider_paddle_timer = 0
                lives = 3
                game_over = False

    # Paddle movement
    if not game_over:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and paddle_x > 0:
            paddle_x -= paddle_speed
        if keys[pygame.K_RIGHT] and paddle_x < WIDTH - paddle_width:
            paddle_x += paddle_speed

    # Ball movement and collision
    if ball_moving and not game_over:
        next_ball_x = ball_x + ball_vx
        next_ball_y = ball_y + ball_vy

        # Brick collision
        brick_hit = False
        for row in range(len(bricks)):
            for col in range(len(bricks[0])):
                if bricks[row][col]:
                    brick_left = col * brick_width
                    brick_right = brick_left + brick_width
                    brick_top = row * brick_height
                    brick_bottom = brick_top + brick_height
                    if (next_ball_x - ball_radius < brick_right and
                        next_ball_x + ball_radius > brick_left and
                        next_ball_y - ball_radius < brick_bottom and
                        next_ball_y + ball_radius > brick_top):
                        bricks[row][col] = 0
                        # Determine collision side
                        prev_x, prev_y = ball_x, ball_y
                        if prev_y + ball_radius <= brick_top and next_ball_y + ball_radius > brick_top:
                            ball_vy *= -1  # Hit top
                            next_ball_y = brick_top - ball_radius
                        elif prev_y - ball_radius >= brick_bottom and next_ball_y - ball_radius < brick_bottom:
                            ball_vy *= -1  # Hit bottom
                            next_ball_y = brick_bottom + ball_radius
                        elif prev_x + ball_radius <= brick_left:
                            ball_vx *= -1  # Hit left
                            next_ball_x = brick_left - ball_radius
                        elif prev_x - ball_radius >= brick_right:
                            ball_vx *= -1  # Hit right
                            next_ball_x = brick_right + ball_radius
                        pygame.mixer.Sound.play(brick_sound)
                        if random.random() < 0.3:  # 30% chance for power-up
                            powerup_type = random.randint(0, 2)
                            powerups.append([brick_left + brick_width // 2 - powerup_size // 2,
                                            brick_top, powerup_type, 0])
                        brick_hit = True
                        break
            if brick_hit:
                break

        # Wall and paddle collision
        if not brick_hit:  # Only check walls/paddle if no brick was hit
            if next_ball_x - ball_radius < 0:
                ball_vx *= -1
                next_ball_x = ball_radius
            elif next_ball_x + ball_radius > WIDTH:
                ball_vx *= -1
                next_ball_x = WIDTH - ball_radius
            if next_ball_y - ball_radius < 0:
                ball_vy *= -1
                next_ball_y = ball_radius
            elif (next_ball_y + ball_radius > paddle_y and
                  paddle_x < next_ball_x < paddle_x + paddle_width):
                ball_vy *= -1
                ball_vx += (next_ball_x - (paddle_x + paddle_width / 2)) * 0.1
                next_ball_y = paddle_y - ball_radius - 1
                pygame.mixer.Sound.play(paddle_sound)

        # Bottom boundary (lose life)
        if next_ball_y + ball_radius > HEIGHT:
            lives -= 1
            pygame.mixer.Sound.play(life_sound)
            ball_x, ball_y = WIDTH // 2, HEIGHT // 2
            ball_vx, ball_vy = 0, 0
            ball_moving = False
            if lives <= 0:
                game_over = True
        else:
            ball_x, ball_y = next_ball_x, next_ball_y

    # Power-up updates
    if not game_over:
        for powerup in powerups[:]:
            powerup[1] += powerup_speed
            if powerup[1] > HEIGHT:
                powerups.remove(powerup)
            elif (paddle_x < powerup[0] + powerup_size and
                  paddle_x + paddle_width > powerup[0] and
                  paddle_y < powerup[1] + powerup_size and
                  paddle_y + paddle_height > powerup[1]):
                if powerup[2] == 0:  # Extra Life
                    lives += 1
                elif powerup[2] == 1:  # Faster Paddle
                    paddle_speed = base_paddle_speed * 2
                    faster_paddle_timer = powerup_duration
                elif powerup[2] == 2:  # Wider Paddle
                    paddle_width = 150
                    wider_paddle_timer = powerup_duration
                powerups.remove(powerup)
                pygame.mixer.Sound.play(powerup_sound)

    # Power-up timers
    if faster_paddle_timer > 0:
        faster_paddle_timer -= 1
        if faster_paddle_timer <= 0:
            paddle_speed = base_paddle_speed
    if wider_paddle_timer > 0:
        wider_paddle_timer -= 1
        if wider_paddle_timer <= 0:
            paddle_width = base_paddle_width

    # Drawing
    screen.fill(BLACK)
    pygame.draw.rect(screen, WHITE, (paddle_x, paddle_y, paddle_width, paddle_height))
    pygame.draw.circle(screen, WHITE, (int(ball_x), int(ball_y)), ball_radius)
    for row in range(len(bricks)):
        for col in range(len(bricks[0])):
            if bricks[row][col]:
                pygame.draw.rect(screen, BRICK_COLORS[row % len(BRICK_COLORS)],
                                 (col * brick_width, row * brick_height, brick_width - 2, brick_height - 2))
    for powerup in powerups:
        draw_powerup(powerup[0], powerup[1], powerup[2])

    # UI
    lives_text = font.render(f"Lives: {max(0, lives)}", True, WHITE)
    screen.blit(lives_text, (10, 10))
    if faster_paddle_timer > 0:
        timer_text = font.render(f"Faster Paddle: {faster_paddle_timer // 60}s", True, WHITE)
        screen.blit(timer_text, (10, 40))
    if wider_paddle_timer > 0:
        offset = 70 if faster_paddle_timer > 0 else 40
        timer_text = font.render(f"Wider Paddle: {wider_paddle_timer // 60}s", True, WHITE)
        screen.blit(timer_text, (10, offset))

    if game_over:
        game_over_text = font.render("Game Over! Press R to Restart", True, WHITE)
        screen.blit(game_over_text, (WIDTH // 2 - 150, HEIGHT // 2))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
