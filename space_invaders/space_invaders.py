# We’re bringing in two cool tools: Pygame for making the game and random for some fun surprises!
import pygame
import random

# Let’s wake up Pygame and its sound system so we can start playing and hearing beeps!
pygame.init()
pygame.mixer.init()

# Setting up our game window—think of it as our space battlefield!
WIDTH = 800  # How wide our window is (in pixels)
HEIGHT = 600  # How tall our window is
screen = pygame.display.set_mode((WIDTH, HEIGHT))  # Creates the window
pygame.display.set_caption("Space Invaders")  # Gives our game a fun title!

# Defining some colors using RGB values (red, green, blue)—like painting with numbers!
WHITE = (255, 255, 255)  # Bright white
BLACK = (0, 0, 0)  # Deep black
GREEN = (0, 255, 0)  # Neon green
YELLOW = (255, 255, 0)  # Sunny yellow
PURPLE = (128, 0, 128)  # Mysterious purple

# Player stuff—our spaceship!
player_width = 50  # How wide our ship is
player_height = 40  # How tall it is
player_speed = 5  # How fast it zooms left or right

# Bullet stuff—pew pew!
bullet_width = 5  # How wide our bullets are
bullet_height = 15  # How tall they are
bullet_speed = 7  # How fast they zip up the screen

# Enemy stuff—the invaders we’re blasting!
enemy_width = 40  # How wide each enemy is
enemy_height = 30  # How tall they are
base_enemy_speed = 0.5  # How fast they creep down
enemy_horizontal_speed = 1  # How fast they wiggle side-to-side
font = pygame.font.Font(None, 36)  # A font for showing text, like our score

# Starting game info—where things are and what’s happening!
player_x = WIDTH // 2 - player_width // 2  # Puts our ship in the middle (x position)
player_y = HEIGHT - 60  # Puts it near the bottom (y position)
bullets = []  # A list to keep track of all our bullets
enemies = []  # A list for enemies: [x position, y position, type, animation frame, direction]
enemy_bullets = []  # A list for enemy bullets coming at us!
score = 0  # Our points—let’s rack ‘em up!
level = 1  # Starting at level 1
game_over = False  # Game’s not over yet—we’re just starting!

# Fun sound effects—let’s make some beeps!
def create_beep_sound(frequency, duration=100):
    sample_rate = 44100  # How smooth our sound is
    samples = int(sample_rate * duration / 1000)  # How many sound bits we need
    buffer = bytearray()  # A place to store our sound
    for i in range(samples):
        # This math makes a simple beep—high or low based on frequency!
        value = int(127 * (1 + (i * frequency % sample_rate > sample_rate // 2) - 0.5))
        buffer.append(value)
    return pygame.mixer.Sound(buffer)  # Turns our beep into a sound we can play

# Creating our sound effects—pew, boom, zap!
shoot_sound = create_beep_sound(800, 100)  # High beep for shooting
hit_sound = create_beep_sound(200, 200)  # Low beep for hitting an enemy
enemy_shoot_sound = create_beep_sound(500, 150)  # Medium beep for enemy shots
shoot_sound.set_volume(0.3)  # Keep it quiet so it’s not too loud
hit_sound.set_volume(0.3)
enemy_shoot_sound.set_volume(0.3)

# A function to reset the game for a new level—like a fresh start!
def reset_level(new_level):
    global player_x, bullets, enemies, enemy_bullets, level  # These can change everywhere
    player_x = WIDTH // 2 - player_width // 2  # Ship back to the middle
    bullets = []  # Clear out old bullets
    enemies = []  # Clear out old enemies
    enemy_bullets = []  # Clear enemy bullets
    level = new_level  # Set the new level
    enemy_count = 5 + level  # More enemies as levels go up!
    # Let’s spawn enemies in a neat grid at the top
    rows = min(3, (enemy_count + 4) // 5)  # Up to 3 rows
    cols = (enemy_count + rows - 1) // rows  # Spread them across columns
    for i in range(enemy_count):
        row = i // cols  # Which row this enemy goes in
        col = i % cols  # Which column
        x = col * (WIDTH // cols) + random.randint(0, WIDTH // cols - enemy_width)  # Random x spot
        y = 50 + row * 50  # y spot based on row
        enemy_type = random.randint(0, 1 + (level > 1))  # Pick an enemy type (more variety later!)
        enemies.append([x, y, enemy_type, 0, 1])  # Add enemy to the list

# Start the game at level 1
reset_level(1)

# Drawing our aliens—time to get creative!
def draw_alien(x, y, alien_type, frame):
    if alien_type == 0:  # Classic invader—old-school vibes!
        if frame == 0:  # First animation pose
            pygame.draw.rect(screen, GREEN, (x + 10, y, 20, 10))  # Body parts as green rectangles
            pygame.draw.rect(screen, GREEN, (x + 5, y + 10, 30, 10))
            pygame.draw.rect(screen, GREEN, (x + 15, y - 10, 10, 10))
            pygame.draw.rect(screen, WHITE, (x + 10, y + 5, 5, 5))  # White eyes
            pygame.draw.rect(screen, WHITE, (x + 25, y + 5, 5, 5))
        else:  # Second pose—makes it look like it’s moving!
            pygame.draw.rect(screen, GREEN, (x + 5, y, 30, 10))
            pygame.draw.rect(screen, GREEN, (x + 10, y + 10, 20, 10))
            pygame.draw.rect(screen, GREEN, (x + 15, y - 5, 10, 5))
            pygame.draw.rect(screen, WHITE, (x + 15, y + 5, 5, 5))
            pygame.draw.rect(screen, WHITE, (x + 25, y + 5, 5, 5))
    elif alien_type == 1:  # Crab-like alien—so sneaky!
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
    elif alien_type == 2:  # Shooter alien—watch out, it fights back!
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

# The big game loop—where all the action happens!
clock = pygame.time.Clock()  # Keeps our game running at a steady speed
running = True  # Keeps the game going until we say stop
frame_counter = 0  # Helps us animate things

while running:
    if not game_over:  # If we’re still playing...
        # Check what the player does—like pressing keys!
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Clicking the X closes the game
                running = False
            if event.type == pygame.KEYDOWN:  # A key was pressed!
                if event.key == pygame.K_SPACE:  # Spacebar shoots a bullet!
                    bullets.append([player_x + player_width // 2 - bullet_width // 2, player_y])
                    pygame.mixer.Sound.play(shoot_sound)  # Pew!

        # Move the player’s ship with arrow keys
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_x > 0:  # Left arrow, but don’t go off-screen!
            player_x -= player_speed
        if keys[pygame.K_RIGHT] and player_x < WIDTH - player_width:  # Right arrow, stay in bounds!
            player_x += player_speed

        # Update bullets—make them fly up!
        for bullet in bullets[:]:  # Copy the list so we can remove stuff safely
            bullet[1] -= bullet_speed  # Move bullet up (y gets smaller)
            if bullet[1] < 0:  # If it’s off the top, bye-bye!
                bullets.remove(bullet)

        # Update enemy bullets—coming down at us!
        for e_bullet in enemy_bullets[:]:
            e_bullet[1] += bullet_speed  # Move down
            if e_bullet[1] > HEIGHT:  # Off the bottom? Remove it!
                enemy_bullets.remove(e_bullet)
            # Check if it hits the player—oh no!
            if (e_bullet[0] < player_x + player_width and
                e_bullet[0] + bullet_width > player_x and
                e_bullet[1] < player_y + player_height and
                e_bullet[1] + bullet_height > player_y):
                game_over = True  # Game over if hit!

        # Move enemies—they’re sneaky!
        enemy_speed = base_enemy_speed + level * 0.1  # Faster each level
        if not enemies:  # No enemies left? Next level!
            reset_level(level + 1)
        for enemy in enemies[:]:
            enemy[1] += enemy_speed  # Move down
            enemy[0] += enemy_horizontal_speed * enemy[4]  # Move side-to-side
            if enemy[0] <= 0 or enemy[0] >= WIDTH - enemy_width:  # Hit a wall? Turn around!
                enemy[4] *= -1  # Flip direction
            if enemy[1] + enemy_height > player_y:  # Reach the player? Game over!
                game_over = True
            elif enemy[1] > HEIGHT:  # Off the bottom? Respawn at top!
                enemies.remove(enemy)
                enemies.append([random.randint(0, WIDTH - enemy_width), 0, random.randint(0, 1 + (level > 1)), 0, 1])
            # Some enemies shoot back—type 2 is tricky!
            if enemy[2] == 2 and random.random() < 0.01 * level:
                enemy_bullets.append([enemy[0] + enemy_width // 2 - bullet_width // 2, enemy[1] + enemy_height])
                pygame.mixer.Sound.play(enemy_shoot_sound)

        # Check for hits—did we blast an alien?
        for bullet in bullets[:]:
            for enemy in enemies[:]:
                if (bullet[0] < enemy[0] + enemy_width and  # Bullet overlaps enemy?
                    bullet[0] + bullet_width > enemy[0] and
                    bullet[1] < enemy[1] + enemy_height and
                    bullet[1] + bullet_height > enemy[1]):
                    bullets.remove(bullet)  # Bullet disappears
                    enemies.remove(enemy)  # Enemy goes boom!
                    score += 10 + level * 5  # Points yay!
                    pygame.mixer.Sound.play(hit_sound)  # Boom sound!
                    break  # Move to next bullet

        # Animate enemies—make them wiggle!
        frame_counter += 1
        if frame_counter % 20 == 0:  # Every 20 ticks, switch poses
            for enemy in enemies:
                enemy[3] = 1 - enemy[3]  # Flip between 0 and 1

    else:  # If game over...
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Close the window
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:  # R restarts the game!
                    reset_level(1)
                    game_over = False
                    score = 0
                if event.key == pygame.K_q:  # Q quits
                    running = False

    # Draw everything on the screen—like painting a picture!
    screen.fill(BLACK)  # Clear it with black
    if not game_over:
        pygame.draw.rect(screen, WHITE, (player_x, player_y, player_width, player_height))  # Draw our ship
        for bullet in bullets:
            pygame.draw.rect(screen, WHITE, (bullet[0], bullet[1], bullet_width, bullet_height))  # Draw bullets
        for e_bullet in enemy_bullets:
            pygame.draw.rect(screen, PURPLE, (e_bullet[0], e_bullet[1], bullet_width, bullet_height))  # Enemy bullets
        for enemy in enemies:
            draw_alien(enemy[0], enemy[1], enemy[2], enemy[3])  # Draw all aliens
    else:
        # Show game over text—time to brag about your score!
        game_over_text = font.render(f"Game Over! Score: {score}", True, WHITE)
        restart_text = font.render("Press R to Restart, Q to Quit", True, WHITE)
        screen.blit(game_over_text, (WIDTH // 2 - 100, HEIGHT // 2 - 20))  # Center it
        screen.blit(restart_text, (WIDTH // 2 - 140, HEIGHT // 2 + 20))

    # Show score and level in the top corner
    score_text = font.render(f"Score: {score}  Level: {level}", True, WHITE)
    screen.blit(score_text, (10, 10))

    # Update the screen so we see everything!
    pygame.display.flip()
    clock.tick(60)  # Keep the game at 60 frames per second—smooth!

# When we’re done, close Pygame nicely
pygame.quit()