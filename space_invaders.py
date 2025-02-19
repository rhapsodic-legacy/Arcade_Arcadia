import pygame
import random

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Set up the display
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)

# Player properties
player_width = 50
player_height = 40
player_speed = 5

# Bullet properties
bullet_width = 5
bullet_height = 15
bullet_speed = 7

# Enemy properties
enemy_width = 40
enemy_height = 30
base_enemy_speed = 0.5
enemy_horizontal_speed = 1
font = pygame.font.Font(None, 36)

# Game state
player_x = WIDTH // 2 - player_width // 2
player_y = HEIGHT - 60
bullets = []
enemies = []  # [x, y, type, frame, direction]
enemy_bullets = []
score = 0
level = 1
game_over = False

# Sound effects
def create_beep_sound(frequency, duration=100):
    sample_rate = 44100
    samples = int(sample_rate * duration / 1000)
    buffer = bytearray()
    for i in range(samples):
        value = int(127 * (1 + (i * frequency % sample_rate > sample_rate // 2) - 0.5))
        buffer.append(value)
    return pygame.mixer.Sound(buffer)

shoot_sound = create_beep_sound(800, 100)
hit_sound = create_beep_sound(200, 200)
enemy_shoot_sound = create_beep_sound(500, 150)
shoot_sound.set_volume(0.3)
hit_sound.set_volume(0.3)
enemy_shoot_sound.set_volume(0.3)

# Function to reset game state for a new level
def reset_level(new_level):
    global player_x, bullets, enemies, enemy_bullets, level
    player_x = WIDTH // 2 - player_width // 2
    bullets = []
    enemies = []
    enemy_bullets = []
    level = new_level
    enemy_count = 5 + level
    # Spawn enemies in a grid near the top
    rows = min(3, (enemy_count + 4) // 5)  # Up to 3 rows
    cols = (enemy_count + rows - 1) // rows  # Distribute across columns
    for i in range(enemy_count):
        row = i // cols
        col = i % cols
        x = col * (WIDTH // cols) + random.randint(0, WIDTH // cols - enemy_width)
        y = 50 + row * 50  # Keep y between 50 and 150
        enemy_type = random.randint(0, 1 + (level > 1))
        enemies.append([x, y, enemy_type, 0, 1])

# Initial level
reset_level(1)

# Alien designs
def draw_alien(x, y, alien_type, frame):
    if alien_type == 0:  # Classic Invader
        if frame == 0:
            pygame.draw.rect(screen, GREEN, (x + 10, y, 20, 10))
            pygame.draw.rect(screen, GREEN, (x + 5, y + 10, 30, 10))
            pygame.draw.rect(screen, GREEN, (x + 15, y - 10, 10, 10))
            pygame.draw.rect(screen, WHITE, (x + 10, y + 5, 5, 5))
            pygame.draw.rect(screen, WHITE, (x + 25, y + 5, 5, 5))
        else:
            pygame.draw.rect(screen, GREEN, (x + 5, y, 30, 10))
            pygame.draw.rect(screen, GREEN, (x + 10, y + 10, 20, 10))
            pygame.draw.rect(screen, GREEN, (x + 15, y - 5, 10, 5))
            pygame.draw.rect(screen, WHITE, (x + 15, y + 5, 5, 5))
            pygame.draw.rect(screen, WHITE, (x + 25, y + 5, 5, 5))
    elif alien_type == 1:  # Crab-like
        if frame == 0:
            pygame.draw.rect(screen, YELLOW, (x + 5, y + 5, 30, 10))
            pygame.draw.rect(screen, YELLOW, (x, y + 15, 40, 10))
            pygame.draw.rect(screen, WHITE, (x + 10, y + 10, 5, 5))
            pygame.draw.rect(screen, WHITE, (x + 25, y + 10, 5, 5))
        else:
            pygame.draw.rect(screen, YELLOW, (x + 10, y, 20, 10))
            pygame.draw.rect(screen, YELLOW, (x + 5, y + 10, 30, 10))
            pygame.draw.rect(screen, WHITE, (x + 15, y + 5, 5, 5))
            pygame.draw.rect(screen, WHITE, (x + 25, y + 5, 5, 5))
    elif alien_type == 2:  # Shooter
        if frame == 0:
            pygame.draw.rect(screen, PURPLE, (x + 10, y, 20, 15))
            pygame.draw.rect(screen, PURPLE, (x + 5, y + 15, 30, 10))
            pygame.draw.rect(screen, WHITE, (x + 15, y + 5, 5, 5))
            pygame.draw.rect(screen, WHITE, (x + 25, y + 5, 5, 5))
        else:
            pygame.draw.rect(screen, PURPLE, (x + 15, y, 10, 15))
            pygame.draw.rect(screen, PURPLE, (x + 10, y + 15, 20, 10))
            pygame.draw.rect(screen, WHITE, (x + 15, y + 10, 5, 5))
            pygame.draw.rect(screen, WHITE, (x + 25, y + 10, 5, 5))

# Game loop
clock = pygame.time.Clock()
running = True
frame_counter = 0

while running:
    if not game_over:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bullets.append([player_x + player_width // 2 - bullet_width // 2, player_y])
                    pygame.mixer.Sound.play(shoot_sound)

        # Player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_x > 0:
            player_x -= player_speed
        if keys[pygame.K_RIGHT] and player_x < WIDTH - player_width:
            player_x += player_speed

        # Update bullets
        for bullet in bullets[:]:
            bullet[1] -= bullet_speed
            if bullet[1] < 0:
                bullets.remove(bullet)

        # Update enemy bullets
        for e_bullet in enemy_bullets[:]:
            e_bullet[1] += bullet_speed
            if e_bullet[1] > HEIGHT:
                enemy_bullets.remove(e_bullet)
            if (e_bullet[0] < player_x + player_width and
                e_bullet[0] + bullet_width > player_x and
                e_bullet[1] < player_y + player_height and
                e_bullet[1] + bullet_height > player_y):
                game_over = True

        # Update enemies
        enemy_speed = base_enemy_speed + level * 0.1
        if not enemies:
            reset_level(level + 1)
        for enemy in enemies[:]:
            enemy[1] += enemy_speed
            enemy[0] += enemy_horizontal_speed * enemy[4]
            if enemy[0] <= 0 or enemy[0] >= WIDTH - enemy_width:
                enemy[4] *= -1
            if enemy[1] + enemy_height > player_y:
                game_over = True
            elif enemy[1] > HEIGHT:
                enemies.remove(enemy)
                enemies.append([random.randint(0, WIDTH - enemy_width), 0, random.randint(0, 1 + (level > 1)), 0, 1])
            if enemy[2] == 2 and random.random() < 0.01 * level:
                enemy_bullets.append([enemy[0] + enemy_width // 2 - bullet_width // 2, enemy[1] + enemy_height])
                pygame.mixer.Sound.play(enemy_shoot_sound)

        # Collision detection
        for bullet in bullets[:]:
            for enemy in enemies[:]:
                if (bullet[0] < enemy[0] + enemy_width and
                    bullet[0] + bullet_width > enemy[0] and
                    bullet[1] < enemy[1] + enemy_height and
                    bullet[1] + bullet_height > enemy[1]):
                    bullets.remove(bullet)
                    enemies.remove(enemy)
                    score += 10 + level * 5
                    pygame.mixer.Sound.play(hit_sound)
                    break

        # Animation
        frame_counter += 1
        if frame_counter % 20 == 0:
            for enemy in enemies:
                enemy[3] = 1 - enemy[3]

    else:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    reset_level(1)
                    game_over = False
                    score = 0
                if event.key == pygame.K_q:
                    running = False

    # Draw everything
    screen.fill(BLACK)
    if not game_over:
        pygame.draw.rect(screen, WHITE, (player_x, player_y, player_width, player_height))
        for bullet in bullets:
            pygame.draw.rect(screen, WHITE, (bullet[0], bullet[1], bullet_width, bullet_height))
        for e_bullet in enemy_bullets:
            pygame.draw.rect(screen, PURPLE, (e_bullet[0], e_bullet[1], bullet_width, bullet_height))
        for enemy in enemies:
            draw_alien(enemy[0], enemy[1], enemy[2], enemy[3])
    else:
        game_over_text = font.render(f"Game Over! Score: {score}", True, WHITE)
        restart_text = font.render("Press R to Restart, Q to Quit", True, WHITE)
        screen.blit(game_over_text, (WIDTH // 2 - 100, HEIGHT // 2 - 20))
        screen.blit(restart_text, (WIDTH // 2 - 140, HEIGHT // 2 + 20))

    # Draw score and level
    score_text = font.render(f"Score: {score}  Level: {level}", True, WHITE)
    screen.blit(score_text, (10, 10))

    # Update display
    pygame.display.flip()
    clock.tick(60)

# Quit Pygame
pygame.quit()
