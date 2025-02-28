# We're bringing in some cool tools (libraries) to help us make the game
import pygame  # This is the main game-making library - it handles graphics, sound, and input
import math    # Math stuff like angles and distances (don't worry, it's not too scary!)
import random  # For adding some fun randomness, like where asteroids pop up

# Let's wake up Pygame and its sound system - it's like turning on our game console
pygame.init()
pygame.mixer.init()

# Setting up our game window - think of it as our TV screen
WIDTH = 800    # How wide our screen is (800 pixels)
HEIGHT = 600   # How tall our screen is (600 pixels)
screen = pygame.display.set_mode((WIDTH, HEIGHT))  # Creates the window
pygame.display.set_caption("Asteroids")  # Gives our window a cool title

# Colors we'll use - these are like our paint cans (numbers are for Red, Green, Blue)
WHITE = (255, 255, 255)  # Pure white
BLACK = (0, 0, 0)        # Pure black
BLUE = (0, 0, 255)      # Bright blue
RED = (255, 0, 0)       # Bright red
GREEN = (0, 255, 0)     # Bright green

# Setting up our spaceship - our little hero!
ship_x = WIDTH // 2      # Starts in the middle horizontally (// means divide and round down)
ship_y = HEIGHT // 2     # Starts in the middle vertically
ship_angle = 0           # Which way it's pointing (0 degrees is right)
ship_speed = 0           # How fast it's going (starts still)
ship_max_speed = 5       # Top speed limit
ship_acceleration = 0.1  # How quickly it speeds up
ship_rotation_speed = 5  # How fast it turns

# Bullets our ship will shoot
bullet_speed = 7         # How fast bullets fly
bullets = []             # A list to keep track of bullets - [x, y, angle] for each
shoot_cooldown = 0       # A timer to stop us shooting too fast
base_shoot_cooldown = 10 # How long we wait between shots

# Asteroids - the bad guys!
asteroids = []  # A list of asteroids - each has [x, y, size, vx, vy, points]
# Let's make 4 asteroids to start with
for _ in range(4):
    asteroids.append([
        random.randint(0, WIDTH),  # Random x position
        random.randint(0, HEIGHT), # Random y position
        40,                        # Size (40 pixels big)
        random.uniform(-1, 1),     # Speed in x direction (vx)
        random.uniform(-1, 1),     # Speed in y direction (vy)
        []                         # Points for drawing (we'll fill this later)
    ])

# Power-ups - little bonuses to help us!
powerup_size = 20         # How big they are
powerup_speed = 2         # How fast they fall
powerups = []             # List of power-ups - [x, y, type, timer]
powerup_duration = 600    # How long Double Fire lasts (600 frames = 10 seconds)
powerup_timer = 0         # Counts down the power-up time
double_fire_active = False # Is Double Fire on? Starts as no

# Game stuff - keeping score and lives
score = 0                 # Points we've earned
lives = 3                 # How many chances we get
font = pygame.font.Font(None, 36)      # Big text for score and messages
font_small = pygame.font.Font(None, 24) # Smaller text for our power-up guide
min_asteroids = 4         # Always have at least 4 asteroids
spawn_timer = 0           # Counts up to spawn new asteroids
spawn_interval = 180      # New asteroid every 3 seconds (180 frames)
hyperspace_cooldown = 0   # Timer for our teleport trick
hyperspace_max_cooldown = 300  # 5 seconds wait between teleports

# Fun sound effects - retro beeps!
def create_beep_sound(frequency, duration=100):
    # This makes a simple beep sound - like old arcade games!
    sample_rate = 44100  # How fast we sample sound (standard for audio)
    samples = int(sample_rate * duration / 1000)  # How many sound bits we need
    buffer = bytearray()  # A place to store our sound
    for i in range(samples):
        # Math magic to make a square wave (beep!)
        value = int(127 * (1 + (i * frequency % sample_rate > sample_rate // 2) - 0.5))
        buffer.append(value)
    return pygame.mixer.Sound(buffer)  # Turn it into a playable sound

# Making our sound effects
shoot_sound = create_beep_sound(800, 100)  # High beep for shooting
hit_sound = create_beep_sound(200, 200)    # Lower beep for hitting stuff
powerup_sound = create_beep_sound(1000, 150) # High happy beep for power-ups
hyperspace_sound = create_beep_sound(400, 300) # Weird beep for teleporting
death_sound = create_beep_sound(300, 200)  # Sad beep for losing a life
# Turn down the volume a bit so it's not too loud
for sound in [shoot_sound, hit_sound, powerup_sound, hyperspace_sound, death_sound]:
    sound.set_volume(0.3)

# Making jagged asteroid shapes - like the old Atari game
def generate_asteroid_points(x, y, size):
    points = []  # List of dots to connect
    num_points = 8 + random.randint(0, 4)  # 8 to 12 corners
    for i in range(num_points):
        angle = i * 360 / num_points + random.randint(-15, 15)  # Spread them around
        radius = size * (0.7 + random.uniform(0, 0.3))  # Vary the distance a bit
        px = x + radius * math.cos(math.radians(angle))  # X spot using math
        py = y + radius * math.sin(math.radians(angle))  # Y spot using math
        points.append((px, py))  # Add this dot to our shape
    return points

# Adding new asteroids when we need them
def spawn_asteroid():
    edge = random.randint(0, 3)  # Pick a side (0=top, 1=right, 2=bottom, 3=left)
    if edge == 0:
        x, y = random.randint(0, WIDTH), 0  # Start at top
        vx, vy = random.uniform(-1, 1), random.uniform(0.5, 1.5)  # Drift down
    elif edge == 1:
        x, y = WIDTH, random.randint(0, HEIGHT)  # Start at right
        vx, vy = random.uniform(-1.5, -0.5), random.uniform(-1, 1)  # Drift left
    elif edge == 2:
        x, y = random.randint(0, WIDTH), HEIGHT  # Start at bottom
        vx, vy = random.uniform(-1, 1), random.uniform(-1.5, -0.5)  # Drift up
    else:
        x, y = 0, random.randint(0, HEIGHT)  # Start at left
        vx, vy = random.uniform(0.5, 1.5), random.uniform(-1, 1)  # Drift right
    size = 40  # Big asteroid
    points = generate_asteroid_points(x, y, size)  # Make its shape
    asteroids.append([x, y, size, vx, vy, points])  # Add it to our list

# Drawing our power-ups with fun shapes
def draw_powerup(x, y, powerup_type):
    if powerup_type == 0:  # Double Fire - Blue Circle
        pygame.draw.circle(screen, BLUE, (int(x + powerup_size // 2), int(y + powerup_size // 2)), powerup_size // 2)
    elif powerup_type == 1:  # Bonus Score - Red Triangle
        points = [
            (x + powerup_size // 2, y),  # Top
            (x, y + powerup_size),       # Bottom left
            (x + powerup_size, y + powerup_size)  # Bottom right
        ]
        pygame.draw.polygon(screen, RED, points)  # Connect the dots
    elif powerup_type == 2:  # Extra Life - Green Square
        pygame.draw.rect(screen, GREEN, (x, y, powerup_size, powerup_size))  # Simple box

# Give our starting asteroids their shapes
for asteroid in asteroids:
    asteroid[5] = generate_asteroid_points(asteroid[0], asteroid[1], asteroid[2])

# Our game clock - keeps everything running smoothly at 60 frames per second
clock = pygame.time.Clock()
running = True  # Keeps our game going until we say stop

# The big game loop - this is where all the action happens!
while running:
    # Check what the player is doing
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # Did they click the X button?
            running = False  # Time to stop
        if event.type == pygame.KEYDOWN:  # Did they press a key?
            if event.key == pygame.K_SPACE and shoot_cooldown <= 0:  # Space to shoot!
                bullets.append([ship_x, ship_y, ship_angle])  # Add a bullet
                if double_fire_active:  # Extra bullet if we have the power-up
                    bullets.append([ship_x, ship_y, ship_angle + 10])
                shoot_cooldown = base_shoot_cooldown  # Wait before next shot
                pygame.mixer.Sound.play(shoot_sound)  # Pew pew!
            if event.key == pygame.K_h and hyperspace_cooldown <= 0 and lives > 0:  # H to teleport!
                ship_x = random.randint(0, WIDTH)  # Random spot
                ship_y = random.randint(0, HEIGHT)
                ship_speed = 0  # Stop moving
                hyperspace_cooldown = hyperspace_max_cooldown  # Wait before next teleport
                pygame.mixer.Sound.play(hyperspace_sound)  # Whoosh!

    # What keys are being held down?
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:   # Left arrow turns left
        ship_angle += ship_rotation_speed
    if keys[pygame.K_RIGHT]:  # Right arrow turns right
        ship_angle -= ship_rotation_speed
    if keys[pygame.K_UP]:     # Up arrow speeds up
        ship_speed = min(ship_speed + ship_acceleration, ship_max_speed)
    if keys[pygame.K_DOWN]:   # Down arrow slows down
        ship_speed = max(ship_speed - ship_acceleration, 0)

    # Move the ship based on its speed and angle
    ship_vx = ship_speed * math.cos(math.radians(ship_angle))  # X speed
    ship_vy = -ship_speed * math.sin(math.radians(ship_angle)) # Y speed (up is negative)
    ship_x += ship_vx  # Update position
    ship_y += ship_vy
    ship_x %= WIDTH    # Wrap around screen edges
    ship_y %= HEIGHT

    # Move all our bullets
    for bullet in bullets[:]:  # Copy list so we can remove stuff safely
        bullet[0] += bullet_speed * math.cos(math.radians(bullet[2]))  # Move x
        bullet[1] -= bullet_speed * math.sin(math.radians(bullet[2]))  # Move y
        if not (0 <= bullet[0] <= WIDTH and 0 <= bullet[1] <= HEIGHT):  # Off screen?
            bullets.remove(bullet)  # Bye bye bullet!

    # Move all our asteroids
    for asteroid in asteroids:
        asteroid[0] += asteroid[3]  # Move x by velocity (vx)
        asteroid[1] += asteroid[4]  # Move y by velocity (vy)
        asteroid[0] %= WIDTH        # Wrap around
        asteroid[1] %= HEIGHT
        asteroid[5] = generate_asteroid_points(asteroid[0], asteroid[1], asteroid[2])  # Update shape

    # Move power-ups and check if we grab them
    for powerup in powerups[:]:
        powerup[1] += powerup_speed  # Fall down
        if powerup[1] > HEIGHT:  # Off screen?
            powerups.remove(powerup)
        elif (powerup[0] < ship_x + 20 and powerup[0] + powerup_size > ship_x - 20 and
              powerup[1] < ship_y + 20 and powerup[1] + powerup_size > ship_y - 20):  # Touching ship?
            if powerup[2] == 0:  # Double Fire
                powerup_timer = powerup_duration
                double_fire_active = True
            elif powerup[2] == 1:  # Bonus Score
                score += 500
            elif powerup[2] == 2:  # Extra Life
                lives += 1
            powerups.remove(powerup)  # Got it!
            pygame.mixer.Sound.play(powerup_sound)  # Yay!

    # Add new asteroids if we need them
    spawn_timer += 1
    if spawn_timer >= spawn_interval and len(asteroids) < min_asteroids:
        spawn_asteroid()  # New asteroid time!
        spawn_timer = 0   # Reset timer

    # Check if ship hits an asteroid
    for asteroid in asteroids:
        if math.hypot(ship_x - asteroid[0], ship_y - asteroid[1]) < asteroid[2] + 15 and lives > 0:
            # Math.hypot is like measuring distance with a ruler!
            lives -= 1  # Ouch!
            ship_x = WIDTH // 2  # Back to center
            ship_y = HEIGHT // 2
            ship_speed = 0       # Stop
            ship_angle = 0       # Reset direction
            pygame.mixer.Sound.play(death_sound)  # Oh no!
            break  # Stop checking - we’re already hit

    # Check if bullets hit asteroids
    for bullet in bullets[:]:
        for asteroid in asteroids[:]:
            if math.hypot(bullet[0] - asteroid[0], bullet[1] - asteroid[1]) < asteroid[2]:
                bullets.remove(bullet)  # Bullet’s gone
                # Points depend on asteroid size
                points = 20 if asteroid[2] > 30 else 50 if asteroid[2] > 15 else 100
                score += points
                if random.random() < 0.2:  # 20% chance for power-up
                    powerup_type = random.randint(0, 2)
                    powerups.append([asteroid[0], asteroid[1], powerup_type, 0])
                if asteroid[2] > 20:  # Big ones split
                    new_size = asteroid[2] // 2
                    asteroids.append([asteroid[0], asteroid[1], new_size,
                                      random.uniform(-1, 1), random.uniform(-1, 1),
                                      generate_asteroid_points(asteroid[0], asteroid[1], new_size)])
                    asteroids.append([asteroid[0], asteroid[1], new_size,
                                      random.uniform(-1, 1), random.uniform(-1, 1),
                                      generate_asteroid_points(asteroid[0], asteroid[1], new_size)])
                asteroids.remove(asteroid)  # Bye asteroid!
                pygame.mixer.Sound.play(hit_sound)  # Boom!
                break  # Move to next bullet

    # Update our timers
    if shoot_cooldown > 0:
        shoot_cooldown -= 1  # Count down to shoot again
    if hyperspace_cooldown > 0:
        hyperspace_cooldown -= 1  # Count down to teleport again
    if powerup_timer > 0:
        powerup_timer -= 1
        if powerup_timer <= 0:  # Power-up over?
            double_fire_active = False
            powerup_timer = 0

    # Draw everything on the screen
    screen.fill(BLACK)  # Clear it with black
    if lives > 0:  # Still alive?
        # Draw the ship - it’s a triangle!
        points = [
            (ship_x + 20 * math.cos(math.radians(ship_angle)),  # Nose
             ship_y - 20 * math.sin(math.radians(ship_angle))),
            (ship_x + 10 * math.cos(math.radians(ship_angle + 135)),  # Left wing
             ship_y - 10 * math.sin(math.radians(ship_angle + 135))),
            (ship_x + 10 * math.cos(math.radians(ship_angle - 135)),  # Right wing
             ship_y - 10 * math.sin(math.radians(ship_angle - 135)))
        ]
        pygame.draw.polygon(screen, WHITE, points)  # Connect the dots
        for bullet in bullets:  # Draw little bullet dots
            pygame.draw.circle(screen, WHITE, (int(bullet[0]), int(bullet[1])), 2)
        for asteroid in asteroids:  # Draw jagged asteroids
            pygame.draw.polygon(screen, WHITE, asteroid[5], 1)  # 1 means outline only
        for powerup in powerups:  # Draw falling power-ups
            draw_powerup(powerup[0], powerup[1], powerup[2])
    else:  # Game over!
        game_over_text = font.render(f"Game Over! Score: {score}", True, WHITE)
        restart_text = font.render("Press R to Restart", True, WHITE)
        screen.blit(game_over_text, (WIDTH // 2 - 100, HEIGHT // 2 - 20))  # Show message
        screen.blit(restart_text, (WIDTH // 2 - 80, HEIGHT // 2 + 20))

    # Show score and lives in top left
    score_text = font.render(f"Score: {score}  Lives: {lives}", True, WHITE)
    screen.blit(score_text, (10, 10))
    if powerup_timer > 0 and double_fire_active:  # Show power-up time
        powerup_text = font.render(f"Power: Double {powerup_timer // 60}s", True, WHITE)
        screen.blit(powerup_text, (10, 40))

    # Draw our power-up guide in the top right - like a little cheat sheet!
    hud_x = WIDTH - 150  # 150 pixels from the right
    hud_y = 10           # Near the top
    # Double Fire (Blue Circle)
    pygame.draw.circle(screen, BLUE, (hud_x + 10, hud_y + 10), 5)  # Small blue dot
    hud_text1 = font_small.render("= Double Fire", True, WHITE)  # What it does
    screen.blit(hud_text1, (hud_x + 20, hud_y + 2))  # Put text next to it
    # Bonus Score (Red Triangle)
    pygame.draw.polygon(screen, RED, [
        (hud_x + 10, hud_y + 25),  # Top
        (hud_x + 5, hud_y + 35),   # Bottom left
        (hud_x + 15, hud_y + 35)   # Bottom right
    ])
    hud_text2 = font_small.render("= 500 Points", True, WHITE)
    screen.blit(hud_text2, (hud_x + 20, hud_y + 25))
    # Extra Life (Green Square)
    pygame.draw.rect(screen, GREEN, (hud_x + 5, hud_y + 45, 10, 10))  # Little box
    hud_text3 = font_small.render("= Extra Life", True, WHITE)
    screen.blit(hud_text3, (hud_x + 20, hud_y + 45))

    # Show everything we drew!
    pygame.display.flip()
    clock.tick(60)  # Keep it running at 60 frames per second - nice and smooth

    # Restart if we’re dead and press R
    if lives <= 0 and keys[pygame.K_r]:
        # Reset everything to start over
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
        for _ in range(4):  # Make 4 new asteroids
            asteroids.append([random.randint(0, WIDTH), random.randint(0, HEIGHT), 40,
                              random.uniform(-1, 1), random.uniform(-1, 1),
                              generate_asteroid_points(0, 0, 40)])

# When we’re done, turn off Pygame nicely
pygame.quit()