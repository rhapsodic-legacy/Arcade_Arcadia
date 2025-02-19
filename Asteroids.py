import pygame
import math
import random

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Set up the display
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Asteroids")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Ship properties
ship_x = WIDTH // 2
ship_y = HEIGHT // 2
ship_angle = 0
ship_speed = 0
ship_max_speed = 5
ship_acceleration = 0.1
ship_rotation_speed = 5

# Bullet properties
bullet_speed = 7
bullets = []  # [x, y, angle]
shoot_cooldown = 0
base_shoot_cooldown = 10

# Asteroid properties
asteroids = []  # [x, y, size, vx, vy, points]
for _ in range(4):
    asteroids.append([random.randint(0, WIDTH), random.randint(0, HEIGHT), 40,
                      random.uniform(-1, 1), random.uniform(-1, 1), []])

# Power-up properties
powerup_size = 20
powerup_speed = 2
powerups = []  # [x, y, type, timer]
powerup_duration = 600  # 10 seconds for Double Fire
powerup_timer = 0
double_fire_active = False

# Game state
score = 0
lives = 3
font = pygame.font.Font(None, 36)
min_asteroids = 4
spawn_timer = 0
spawn_interval = 180  # 3 seconds
hyperspace_cooldown = 0
hyperspace_max_cooldown = 300  # 5 seconds

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
powerup_sound = create_beep_sound(1000, 150)
hyperspace_sound = create_beep_sound(400, 300)
death_sound = create_beep_sound(300, 200)
for sound in [shoot_sound, hit_sound, powerup_sound, hyperspace_sound, death_sound]:
    sound.set_volume(0.3)

# Function to generate Atari-style asteroid points
def generate_asteroid_points(x, y, size):
    points = []
    num_points = 8 + random.randint(0, 4)
    for i in range(num_points):
        angle = i * 360 / num_points + random.randint(-15, 15)
        radius = size * (0.7 + random.uniform(0, 0.3))
        px = x + radius * math.cos(math.radians(angle))
        py = y + radius * math.sin(math.radians(angle))
        points.append((px, py))
    return points

# Function to spawn asteroid
def spawn_asteroid():
    edge = random.randint(0, 3)
    if edge == 0:
        x, y = random.randint(0, WIDTH), 0
        vx, vy = random.uniform(-1, 1), random.uniform(0.5, 1.5)
    elif edge == 1:
        x, y = WIDTH, random.randint(0, HEIGHT)
        vx, vy = random.uniform(-1.5, -0.5), random.uniform(-1, 1)
    elif edge == 2:
        x, y = random.randint(0, WIDTH), HEIGHT
        vx, vy = random.uniform(-1, 1), random.uniform(-1.5, -0.5)
    else:
        x, y = 0, random.randint(0, HEIGHT)
        vx, vy = random.uniform(0.5, 1.5), random.uniform(-1, 1)
    size = 40
    points = generate_asteroid_points(x, y, size)
    asteroids.append([x, y, size, vx, vy, points])

# Draw power-ups with different shapes
def draw_powerup(x, y, powerup_type):
    if powerup_type == 0:  # Double Fire - Circle
        pygame.draw.circle(screen, BLUE, (int(x + powerup_size // 2), int(y + powerup_size // 2)), powerup_size // 2)
    elif powerup_type == 1:  # Bonus Score - Triangle
        points = [
            (x + powerup_size // 2, y),
            (x, y + powerup_size),
            (x + powerup_size, y + powerup_size)
        ]
        pygame.draw.polygon(screen, RED, points)
    elif powerup_type == 2:  # Extra Life - Square
        pygame.draw.rect(screen, GREEN, (x, y, powerup_size, powerup_size))

# Initialize asteroid shapes
for asteroid in asteroids:
    asteroid[5] = generate_asteroid_points(asteroid[0], asteroid[1], asteroid[2])

# Game loop
clock = pygame.time.Clock()
running = True

while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and shoot_cooldown <= 0:
                bullets.append([ship_x, ship_y, ship_angle])
                if double_fire_active:
                    bullets.append([ship_x, ship_y, ship_angle + 10])
                shoot_cooldown = base_shoot_cooldown
                pygame.mixer.Sound.play(shoot_sound)
            if event.key == pygame.K_h and hyperspace_cooldown <= 0 and lives > 0:
                ship_x = random.randint(0, WIDTH)
                ship_y = random.randint(0, HEIGHT)
                ship_speed = 0
                hyperspace_cooldown = hyperspace_max_cooldown
                pygame.mixer.Sound.play(hyperspace_sound)

    # Ship controls
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        ship_angle += ship_rotation_speed
    if keys[pygame.K_RIGHT]:
        ship_angle -= ship_rotation_speed
    if keys[pygame.K_UP]:
        ship_speed = min(ship_speed + ship_acceleration, ship_max_speed)
    if keys[pygame.K_DOWN]:
        ship_speed = max(ship_speed - ship_acceleration, 0)

    # Update ship position
    ship_vx = ship_speed * math.cos(math.radians(ship_angle))
    ship_vy = -ship_speed * math.sin(math.radians(ship_angle))
    ship_x += ship_vx
    ship_y += ship_vy
    ship_x %= WIDTH
    ship_y %= HEIGHT

    # Update bullets
    for bullet in bullets[:]:
        bullet[0] += bullet_speed * math.cos(math.radians(bullet[2]))
        bullet[1] -= bullet_speed * math.sin(math.radians(bullet[2]))
        if not (0 <= bullet[0] <= WIDTH and 0 <= bullet[1] <= HEIGHT):
            bullets.remove(bullet)

    # Update asteroids
    for asteroid in asteroids:
        asteroid[0] += asteroid[3]
        asteroid[1] += asteroid[4]
        asteroid[0] %= WIDTH
        asteroid[1] %= HEIGHT
        asteroid[5] = generate_asteroid_points(asteroid[0], asteroid[1], asteroid[2])

    # Update power-ups
    for powerup in powerups[:]:
        powerup[1] += powerup_speed
        if powerup[1] > HEIGHT:
            powerups.remove(powerup)
        elif (powerup[0] < ship_x + 20 and powerup[0] + powerup_size > ship_x - 20 and
              powerup[1] < ship_y + 20 and powerup[1] + powerup_size > ship_y - 20):
            if powerup[2] == 0:  # Double Fire
                powerup_timer = powerup_duration
                double_fire_active = True
            elif powerup[2] == 1:  # Bonus Score
                score += 500
            elif powerup[2] == 2:  # Extra Life
                lives += 1
            powerups.remove(powerup)
            pygame.mixer.Sound.play(powerup_sound)

    # Spawn new asteroids
    spawn_timer += 1
    if spawn_timer >= spawn_interval and len(asteroids) < min_asteroids:
        spawn_asteroid()
        spawn_timer = 0

    # Collision detection: ship vs asteroid
    for asteroid in asteroids:
        if math.hypot(ship_x - asteroid[0], ship_y - asteroid[1]) < asteroid[2] + 15 and lives > 0:
            lives -= 1
            ship_x = WIDTH // 2
            ship_y = HEIGHT // 2
            ship_speed = 0
            ship_angle = 0
            pygame.mixer.Sound.play(death_sound)
            break

    # Collision detection: bullet vs asteroid
    for bullet in bullets[:]:
        for asteroid in asteroids[:]:
            if math.hypot(bullet[0] - asteroid[0], bullet[1] - asteroid[1]) < asteroid[2]:
                bullets.remove(bullet)
                points = 20 if asteroid[2] > 30 else 50 if asteroid[2] > 15 else 100
                score += points
                if random.random() < 0.2:
                    powerup_type = random.randint(0, 2)
                    powerups.append([asteroid[0], asteroid[1], powerup_type, 0])
                if asteroid[2] > 20:
                    new_size = asteroid[2] // 2
                    asteroids.append([asteroid[0], asteroid[1], new_size,
                                      random.uniform(-1, 1), random.uniform(-1, 1),
                                      generate_asteroid_points(asteroid[0], asteroid[1], new_size)])
                    asteroids.append([asteroid[0], asteroid[1], new_size,
                                      random.uniform(-1, 1), random.uniform(-1, 1),
                                      generate_asteroid_points(asteroid[0], asteroid[1], new_size)])
                asteroids.remove(asteroid)
                pygame.mixer.Sound.play(hit_sound)
                break

    # Update timers
    if shoot_cooldown > 0:
        shoot_cooldown -= 1
    if hyperspace_cooldown > 0:
        hyperspace_cooldown -= 1
    if powerup_timer > 0:
        powerup_timer -= 1
        if powerup_timer <= 0:
            double_fire_active = False
            powerup_timer = 0

    # Draw everything
    screen.fill(BLACK)
    if lives > 0:
        points = [
            (ship_x + 20 * math.cos(math.radians(ship_angle)),
             ship_y - 20 * math.sin(math.radians(ship_angle))),
            (ship_x + 10 * math.cos(math.radians(ship_angle + 135)),
             ship_y - 10 * math.sin(math.radians(ship_angle + 135))),
            (ship_x + 10 * math.cos(math.radians(ship_angle - 135)),
             ship_y - 10 * math.sin(math.radians(ship_angle - 135)))
        ]
        pygame.draw.polygon(screen, WHITE, points)
        for bullet in bullets:
            pygame.draw.circle(screen, WHITE, (int(bullet[0]), int(bullet[1])), 2)
        for asteroid in asteroids:
            pygame.draw.polygon(screen, WHITE, asteroid[5], 1)
        for powerup in powerups:
            draw_powerup(powerup[0], powerup[1], powerup[2])
    else:
        game_over_text = font.render(f"Game Over! Score: {score}", True, WHITE)
        restart_text = font.render("Press R to Restart", True, WHITE)
        screen.blit(game_over_text, (WIDTH // 2 - 100, HEIGHT // 2 - 20))
        screen.blit(restart_text, (WIDTH // 2 - 80, HEIGHT // 2 + 20))

    # Draw score, lives, and power-up timer
    score_text = font.render(f"Score: {score}  Lives: {lives}", True, WHITE)
    screen.blit(score_text, (10, 10))
    if powerup_timer > 0 and double_fire_active:  # Only Double Fire has a duration
        powerup_text = font.render(f"Power: Double {powerup_timer // 60}s", True, WHITE)
        screen.blit(powerup_text, (10, 40))

    # Update display
    pygame.display.flip()
    clock.tick(60)

    # Check for restart
    if lives <= 0 and keys[pygame.K_r]:
        ship_x = WIDTH // 2
        ship_y = HEIGHT // 2
        ship_angle = 0
        ship_speed = 0
        bullets = []
        asteroids = []
        powerups = []
        score = 0
        lives = 3
        powerup_timer = 0
        hyperspace_cooldown = 0
        double_fire_active = False
        for _ in range(4):
            asteroids.append([random.randint(0, WIDTH), random.randint(0, HEIGHT), 40,
                              random.uniform(-1, 1), random.uniform(-1, 1),
                              generate_asteroid_points(0, 0, 40)])

# Quit Pygame
pygame.quit()
