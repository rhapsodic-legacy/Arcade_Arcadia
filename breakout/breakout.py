import pygame
import random

# Initialize Pygame
# This line starts up Pygame, a library that helps us make games. Think of it as turning on the game engine!
pygame.init()
# This sets up the sound system so we can play beeps and boops later.
pygame.mixer.init()

# Set up the display
# We’re defining the size of our game window: 800 pixels wide and 600 pixels tall.
WIDTH, HEIGHT = 800, 600
# This creates the actual window where the game will happen.
screen = pygame.display.set_mode((WIDTH, HEIGHT))
# Sets the title at the top of the window to "Breakout" – cool, right?
pygame.display.set_caption("Breakout")

# Colors
# Colors in Pygame use RGB values (red, green, blue), where each ranges from 0 to 255.
# WHITE is full brightness of all colors, BLACK is none, and so on.
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
PURPLE = (128, 0, 128)
# A list of colors for our bricks – each row will cycle through these.
BRICK_COLORS = [RED, ORANGE, YELLOW, GREEN, BLUE]

# Game objects
# Paddle (the thing you move to bounce the ball)
# Starting position: centered horizontally (WIDTH // 2 - 50) and 40 pixels from the bottom.
paddle_x, paddle_y = WIDTH // 2 - 50, HEIGHT - 40
# Size of the paddle: 100 pixels wide and 20 pixels tall.
paddle_width, paddle_height = 100, 20
# How fast the paddle moves normally – 5 pixels per frame.
base_paddle_speed = 5
# Current speed, starts the same as the base but can change with power-ups.
paddle_speed = base_paddle_speed
# Normal width of the paddle, which might grow with a power-up.
base_paddle_width = 100

# Ball
# Starting position: smack in the middle of the screen.
ball_x, ball_y = WIDTH // 2, HEIGHT // 2
# The ball is a circle, and this is its radius (how big it is).
ball_radius = 10
# Speed in x and y directions – starts at 0, we’ll set it later when the game begins.
ball_vx, ball_vy = 0, 0
# Normal speed of the ball when it moves.
base_ball_speed = 4

# Bricks
# Each brick is 80 pixels wide and 30 pixels tall.
brick_width, brick_height = 80, 30
# Creates a grid of bricks: 5 rows, and each row has as many bricks as fit across the screen.
# '1' means the brick is there, '0' would mean it’s gone (we’ll change that later).
bricks = [[1 for _ in range(WIDTH // brick_width)] for _ in range(5)]

# Power-ups
# Power-ups are little bonuses that fall from bricks – they’re 20 pixels big.
powerup_size = 20
# How fast they fall down the screen – 2 pixels per frame.
powerup_speed = 2
# A list to keep track of all power-ups: each one has [x position, y position, type, timer].
powerups = []  # Starts empty!
# How long power-up effects last: 600 frames is about 10 seconds at 60 frames per second.
powerup_duration = 600

# Game state
# You start with 3 lives – lose them all, and it’s game over!
lives = 3
# Sets up a font for showing text like "Lives: 3" on the screen.
font = pygame.font.Font(None, 36)
# Tracks if the game is over (False means we’re still playing).
game_over = False
# Checks if the ball is moving yet – it won’t until you press Space.
ball_moving = False
# Timers for power-ups: these count down how long the effects last.
faster_paddle_timer = 0  # For faster paddle movement.
wider_paddle_timer = 0   # For a wider paddle.
# Whether we show the help menu (HUD) – starts as visible.
hud_visible = True

# Sound effects
# A little function to make beepy sounds for the game – like retro arcade vibes!
def create_beep_sound(frequency, duration=100):
    sample_rate = 44100  # How fast we sample the sound (standard for audio).
    samples = int(sample_rate * duration / 1000)  # How many sound samples to make.
    buffer = bytearray()  # A place to store the sound data.
    for i in range(samples):
        # This math makes a simple square wave sound – high or low based on frequency.
        value = int(127 * (1 + (i * frequency % sample_rate > sample_rate // 2) - 0.5))
        buffer.append(value)
    return pygame.mixer.Sound(buffer)  # Turns it into a sound Pygame can play.

# Making sounds for different actions in the game.
paddle_sound = create_beep_sound(800, 100)  # High beep for paddle hits.
brick_sound = create_beep_sound(200, 150)   # Lower beep for breaking bricks.
life_sound = create_beep_sound(300, 200)    # Sad beep for losing a life.
powerup_sound = create_beep_sound(1000, 150)  # Exciting beep for power-ups!
# Turn the volume down a bit so it’s not too loud – 30% of max.
for sound in [paddle_sound, brick_sound, life_sound, powerup_sound]:
    sound.set_volume(0.3)

# Draw power-ups with different shapes so you know what they do!
def draw_powerup(x, y, powerup_type):
    if powerup_type == 0:  # Extra Life – a green circle.
        pygame.draw.circle(screen, GREEN, (int(x + powerup_size // 2), int(y + powerup_size // 2)), powerup_size // 2)
    elif powerup_type == 1:  # Faster Paddle – a blue square.
        pygame.draw.rect(screen, BLUE, (x, y, powerup_size, powerup_size))
    elif powerup_type == 2:  # Wider Paddle – a purple triangle.
        points = [(x + powerup_size // 2, y), (x, y + powerup_size), (x + powerup_size, y + powerup_size)]
        pygame.draw.polygon(screen, PURPLE, points)

# Game loop
# This keeps the game running at 60 frames per second – like a heartbeat for the game!
clock = pygame.time.Clock()
# A flag to keep the game going – when it’s False, the game stops.
running = True

while running:
    # Event handling – checking what the player does!
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # Clicking the window’s X button?
            running = False  # Stop the game.
        if event.type == pygame.KEYDOWN:  # A key was pressed!
            if event.key == pygame.K_SPACE and not game_over and not ball_moving:
                # Press Space to start the ball moving if the game’s not over and it’s still.
                ball_vx, ball_vy = base_ball_speed, -base_ball_speed  # Moves right and up!
                ball_moving = True
            if event.key == pygame.K_r and game_over:
                # Press R to reset everything after a game over.
                paddle_x = WIDTH // 2 - 50  # Paddle back to center.
                paddle_width = base_paddle_width  # Normal size again.
                paddle_speed = base_paddle_speed  # Normal speed.
                ball_x, ball_y = WIDTH // 2, HEIGHT // 2  # Ball to center.
                ball_vx, ball_vy = 0, 0  # Ball stops moving.
                ball_moving = False
                bricks = [[1 for _ in range(WIDTH // brick_width)] for _ in range(5)]  # All bricks back!
                powerups = []  # No power-ups.
                faster_paddle_timer = 0  # Reset timers.
                wider_paddle_timer = 0
                lives = 3  # Back to 3 lives.
                game_over = False  # Game on again!
            if event.key == pygame.K_RETURN:
                # Press Enter to hide the help menu (HUD).
                hud_visible = False

    # Paddle movement
    if not game_over:  # Only move if the game’s still going!
        keys = pygame.key.get_pressed()  # Check which keys are being held down.
        if keys[pygame.K_LEFT] and paddle_x > 0:  # Left arrow pressed and not at edge?
            paddle_x -= paddle_speed  # Move left!
        if keys[pygame.K_RIGHT] and paddle_x < WIDTH - paddle_width:  # Right arrow and not at edge?
            paddle_x += paddle_speed  # Move right!

    # Ball movement and collision
    if ball_moving and not game_over:  # Ball only moves if it’s started and game’s on.
        next_ball_x = ball_x + ball_vx  # Where the ball will be next in x.
        next_ball_y = ball_y + ball_vy  # And in y.

        # Brick collision – let’s smash some bricks!
        brick_hit = False
        for row in range(len(bricks)):  # Check each row.
            for col in range(len(bricks[0])):  # Check each brick in the row.
                if bricks[row][col]:  # If the brick is still there (1, not 0)...
                    # Figure out the brick’s edges.
                    brick_left = col * brick_width
                    brick_right = brick_left + brick_width
                    brick_top = row * brick_height
                    brick_bottom = brick_top + brick_height
                    # Does the ball hit the brick?
                    if (next_ball_x - ball_radius < brick_right and
                        next_ball_x + ball_radius > brick_left and
                        next_ball_y - ball_radius < brick_bottom and
                        next_ball_y + ball_radius > brick_top):
                        bricks[row][col] = 0  # Brick goes bye-bye!
                        # Figure out which side we hit to bounce properly.
                        prev_x, prev_y = ball_x, ball_y  # Where the ball was before.
                        if prev_y + ball_radius <= brick_top and next_ball_y + ball_radius > brick_top:
                            ball_vy *= -1  # Hit the top – bounce down.
                            next_ball_y = brick_top - ball_radius
                        elif prev_y - ball_radius >= brick_bottom and next_ball_y - ball_radius < brick_bottom:
                            ball_vy *= -1  # Hit the bottom – bounce up.
                            next_ball_y = brick_bottom + ball_radius
                        elif prev_x + ball_radius <= brick_left:
                            ball_vx *= -1  # Hit the left – bounce right.
                            next_ball_x = brick_left - ball_radius
                        elif prev_x - ball_radius >= brick_right:
                            ball_vx *= -1  # Hit the right – bounce left.
                            next_ball_x = brick_right + ball_radius
                        pygame.mixer.Sound.play(brick_sound)  # Play that satisfying brick-breaking sound!
                        if random.random() < 0.3:  # 30% chance for a power-up to drop.
                            powerup_type = random.randint(0, 2)  # Pick one: 0, 1, or 2.
                            powerups.append([brick_left + brick_width // 2 - powerup_size // 2,
                                            brick_top, powerup_type, 0])  # Add it where the brick was.
                        brick_hit = True
                        break  # Stop checking this row.
            if brick_hit:
                break  # Stop checking all bricks.

        # Wall and paddle collision – keep that ball in play!
        if not brick_hit:  # Only check this if we didn’t hit a brick.
            if next_ball_x - ball_radius < 0:  # Hit left wall?
                ball_vx *= -1  # Bounce right.
                next_ball_x = ball_radius
            elif next_ball_x + ball_radius > WIDTH:  # Hit right wall?
                ball_vx *= -1  # Bounce left.
                next_ball_x = WIDTH - ball_radius
            if next_ball_y - ball_radius < 0:  # Hit top?
                ball_vy *= -1  # Bounce down.
                next_ball_y = ball_radius
            elif (next_ball_y + ball_radius > paddle_y and
                  paddle_x < next_ball_x < paddle_x + paddle_width):  # Hit the paddle?
                ball_vy *= -1  # Bounce up!
                # Add a little spin based on where it hits the paddle.
                ball_vx += (next_ball_x - (paddle_x + paddle_width / 2)) * 0.1
                next_ball_y = paddle_y - ball_radius - 1  # Keep it above the paddle.
                pygame.mixer.Sound.play(paddle_sound)  # Boop!

        # Bottom boundary – oops, missed it!
        if next_ball_y + ball_radius > HEIGHT:
            lives -= 1  # Lose a life.
            pygame.mixer.Sound.play(life_sound)  # Sad beep.
            ball_x, ball_y = WIDTH // 2, HEIGHT // 2  # Ball back to center.
            ball_vx, ball_vy = 0, 0  # Stop moving.
            ball_moving = False
            if lives <= 0:  # No lives left?
                game_over = True  # Game over, man!
        else:
            ball_x, ball_y = next_ball_x, next_ball_y  # Update ball position.

    # Power-up updates – catch those goodies!
    if not game_over:
        for powerup in powerups[:]:  # Copy the list so we can remove items safely.
            powerup[1] += powerup_speed  # Move it down.
            if powerup[1] > HEIGHT:  # Off the screen?
                powerups.remove(powerup)  # Bye-bye!
            elif (paddle_x < powerup[0] + powerup_size and
                  paddle_x + paddle_width > powerup[0] and
                  paddle_y < powerup[1] + powerup_size and
                  paddle_y + paddle_height > powerup[1]):  # Paddle catches it?
                if powerup[2] == 0:  # Extra Life.
                    lives += 1  # Woohoo, another chance!
                elif powerup[2] == 1:  # Faster Paddle.
                    paddle_speed = base_paddle_speed * 2  # Zoom zoom!
                    faster_paddle_timer = powerup_duration  # Lasts for a while.
                elif powerup[2] == 2:  # Wider Paddle.
                    paddle_width = 150  # Big paddle power!
                    wider_paddle_timer = powerup_duration  # Also lasts a bit.
                powerups.remove(powerup)  # Remove it after catching.
                pygame.mixer.Sound.play(powerup_sound)  # Happy beep!

    # Power-up timers – counting down the fun!
    if faster_paddle_timer > 0:
        faster_paddle_timer -= 1  # Tick down.
        if faster_paddle_timer <= 0:  # Time’s up?
            paddle_speed = base_paddle_speed  # Back to normal speed.
    if wider_paddle_timer > 0:
        wider_paddle_timer -= 1
        if wider_paddle_timer <= 0:  # Done?
            paddle_width = base_paddle_width  # Back to normal size.

    # Drawing – let’s make it look awesome!
    screen.fill(BLACK)  # Clear the screen with black.
    pygame.draw.rect(screen, WHITE, (paddle_x, paddle_y, paddle_width, paddle_height))  # Draw the paddle.
    pygame.draw.circle(screen, WHITE, (int(ball_x), int(ball_y)), ball_radius)  # Draw the ball.
    for row in range(len(bricks)):  # Draw all the bricks.
        for col in range(len(bricks[0])):
            if bricks[row][col]:  # If the brick’s still there...
                # Use the color from our list, cycling with %.
                pygame.draw.rect(screen, BRICK_COLORS[row % len(BRICK_COLORS)],
                                 (col * brick_width, row * brick_height, brick_width - 2, brick_height - 2))
    for powerup in powerups:  # Draw any falling power-ups.
        draw_powerup(powerup[0], powerup[1], powerup[2])

    # UI – show some info on the screen!
    lives_text = font.render(f"Lives: {max(0, lives)}", True, WHITE)  # Show lives (never negative).
    screen.blit(lives_text, (10, 10))  # Put it in the top-left corner.
    if faster_paddle_timer > 0:  # Got the faster paddle power-up?
        timer_text = font.render(f"Faster Paddle: {faster_paddle_timer // 60}s", True, WHITE)
        screen.blit(timer_text, (10, 40))  # Show how many seconds left.
    if wider_paddle_timer > 0:  # Wider paddle active?
        offset = 70 if faster_paddle_timer > 0 else 40  # Move it down if both are active.
        timer_text = font.render(f"Wider Paddle: {wider_paddle_timer // 60}s", True, WHITE)
        screen.blit(timer_text, (10, offset))

    # Heads-Up Display (HUD) – a little help menu!
    if hud_visible:  # Only show if we haven’t hidden it.
        hud_x = WIDTH - 280  # Bottom-right corner: 520 pixels from left.
        hud_y = HEIGHT - 160  # 440 pixels from top.
        # A hint to start the game.
        screen.blit(font.render("Press Space to start", True, WHITE), (hud_x - 50, hud_y - 100))
        # Tell them how to hide this.
        screen.blit(font.render("Press Enter to remove this list", True, WHITE), (hud_x - 100, hud_y - 60))
        # Title of the HUD.
        screen.blit(font.render("Powerups:", True, WHITE), (hud_x, hud_y))
        # List all power-ups with their shapes.
        powerup_descriptions = ["Extra Life", "Faster Paddle", "Wider Paddle"]
        for i in range(3):
            draw_powerup(hud_x, hud_y + (i + 1) * 40, i)  # Draw the shape.
            text_surface = font.render(powerup_descriptions[i], True, WHITE)
            screen.blit(text_surface, (hud_x + 30, hud_y + (i + 1) * 40))  # Name next to it.
        # Reminder to hide it.
        screen.blit(font.render("Press Enter to remove this HUD", True, WHITE), (hud_x, hud_y + 4 * 40))

    if game_over:  # Game over screen.
        game_over_text = font.render("Game Over! Press R to Restart", True, WHITE)
        screen.blit(game_over_text, (WIDTH // 2 - 150, HEIGHT // 2))  # Center it.

    pygame.display.flip()  # Update the screen with everything we drew!
    clock.tick(60)  # Keep the game running at 60 frames per second.

# When the loop ends (game closed), shut down Pygame nicely.
pygame.quit()