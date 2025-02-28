# These are libraries we need to make our game work. Think of them as toolboxes!
import pygame  # This helps us build games with graphics and sound
import random  # This lets us add some fun randomness (like picking colors or directions)
import numpy as np  # This is a math helper for making cool sounds

# Time to set up Pygame so it’s ready to go!
pygame.init()  # Starts up Pygame’s engine
pygame.mixer.init(frequency=44100, size=-16, channels=1)  # Sets up sound system (44100 is how fast it samples sound, -16 is for quality, 1 means one sound at a time)

# These are like the "rules" of our game world, stored in all caps so we know they won’t change
SCREEN_WIDTH = 800  # How wide our game window is (in pixels)
SCREEN_HEIGHT = 600  # How tall our game window is
PADDLE_WIDTH = 20  # Width of the paddles
PADDLE_HEIGHT = 100  # Height of the paddles
BALL_SIZE = 20  # How big our ball is (it’s a square, so this is both width and height)
BRICK_WIDTH = 40  # Width of the bricks in the middle
BRICK_HEIGHT = 40  # Height of the bricks
NUM_COLS = 5  # How many columns of bricks we’ll have
NUM_ROWS = 14  # How many rows of bricks

# Colors we’ll use (RGB style: red, green, blue)
BLACK = (0, 0, 0)  # For the background
WHITE = (255, 255, 255)  # For paddles, ball, and text

# Set up our game window (like opening a canvas to draw on)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))  # Creates the window
pygame.display.set_caption("Pong + Breakout")  # Gives it a fun title
clock = pygame.time.Clock()  # This keeps our game running at a steady speed

# **Sound Generation** - Let’s make some beeps without any music files!
def create_sound(frequency, duration):
    sample_rate = 44100  # How many “sound snapshots” we take per second
    t = np.linspace(0, duration, int(sample_rate * duration), False)  # Makes a list of time steps
    wave = np.sin(frequency * t * 2 * np.pi)  # Creates a sine wave (a smooth sound curve)
    mono_array = (wave * 32767).astype(np.int16)  # Turns the wave into loudness numbers computers understand
    stereo_array = np.column_stack((mono_array, mono_array))  # Doubles it for left and right speakers
    sound = pygame.sndarray.make_sound(stereo_array)  # Turns our numbers into a playable sound
    return sound  # Gives the sound back to use later

# Making our game sounds
ball_hit_sound = create_sound(800, 0.1)  # A quick, high beep when the ball hits a paddle
brick_hit_sound = create_sound(600, 0.1)  # A slightly lower beep for hitting bricks
score_sound = create_sound(400, 0.5)  # A longer, lower sound when someone scores

# **Paddle Class** - This is like a blueprint for our paddles
class Paddle:
    def __init__(self, x, y):  # Sets up a new paddle
        self.x = x  # Where it starts horizontally
        self.y = y  # Where it starts vertically
        self.width = PADDLE_WIDTH  # How wide it is
        self.height = PADDLE_HEIGHT  # How tall it is
    
    def move(self, dy):  # Moves the paddle up or down
        self.y += dy  # Changes its y position (dy is how much to move)
        self.y = max(0, min(self.y, SCREEN_HEIGHT - self.height))  # Keeps it on the screen
    
    def draw(self, screen):  # Draws the paddle
        pygame.draw.rect(screen, WHITE, (self.x, self.y, self.width, self.height))  # Makes a white rectangle

# **Ball Class** - Our bouncy little friend
class Ball:
    def __init__(self, x, y):  # Sets up a new ball
        self.x = x  # Starting x position
        self.y = y  # Starting y position
        self.vx = 5  # How fast it moves left/right
        self.vy = 3  # How fast it moves up/down
        self.size = BALL_SIZE  # Its size
    
    def update(self):  # Moves the ball each frame
        self.x += self.vx  # Updates x position
        self.y += self.vy  # Updates y position
    
    def reset(self):  # Puts the ball back in the middle
        self.x = SCREEN_WIDTH // 2  # Center horizontally
        self.y = SCREEN_HEIGHT // 2  # Center vertically
        self.vx = random.choice([-5, 5])  # Picks a random left or right speed
        self.vy = random.uniform(-3, 3)  # Picks a random up/down speed
    
    def draw(self, screen):  # Draws the ball
        pygame.draw.rect(screen, WHITE, (self.x, self.y, self.size, self.size))  # Makes a white square

# **Brick Class with Gradient** - Fancy bricks that look cool
class Brick:
    def __init__(self, x, y):  # Sets up a new brick
        self.x = x  # Where it sits horizontally
        self.y = y  # Where it sits vertically
        self.width = BRICK_WIDTH  # How wide
        self.height = BRICK_HEIGHT  # How tall
        self.color1 = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))  # Top color
        self.color2 = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))  # Bottom color
        self.surface = self.create_gradient_surface()  # Makes its pretty look
    
    def create_gradient_surface(self):  # Creates a smooth color fade
        surface = pygame.Surface((self.width, self.height))  # A blank canvas for the brick
        for row in range(self.height):  # Loops through each row
            ratio = row / (self.height - 1)  # How far down we are (0 at top, 1 at bottom)
            r = int(self.color1[0] * (1 - ratio) + self.color2[0] * ratio)  # Mixes red
            g = int(self.color1[1] * (1 - ratio) + self.color2[1] * ratio)  # Mixes green
            b = int(self.color1[2] * (1 - ratio) + self.color2[2] * ratio)  # Mixes blue
            pygame.draw.line(surface, (r, g, b), (0, row), (self.width, row))  # Draws a colored line
        return surface  # Gives back the finished look
    
    def draw(self, screen):  # Draws the brick
        screen.blit(self.surface, (self.x, self.y))  # Puts the gradient on the screen
        pygame.draw.rect(screen, WHITE, (self.x, self.y, self.width, self.height), 1)  # Adds a white border

# **Initialize Game Objects** - Setting up our players!
left_paddle = Paddle(20, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2)  # Player’s paddle on the left
right_paddle = Paddle(SCREEN_WIDTH - PADDLE_WIDTH - 20, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2)  # AI’s paddle on the right
ball = Ball(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)  # Ball starts in the middle

# Brick grid - Making a wall of bricks
brick_grid = [[None for _ in range(NUM_ROWS)] for _ in range(NUM_COLS)]  # A 5x14 grid to hold bricks
BRICK_AREA_LEFT = (SCREEN_WIDTH - NUM_COLS * BRICK_WIDTH) // 2  # Where the bricks start on the left
BRICK_AREA_TOP = 20  # How far from the top they start

for c in range(NUM_COLS):  # Loop through columns
    for r in range(NUM_ROWS):  # Loop through rows
        if random.random() < 0.2:  # 20% chance to add a brick
            x = BRICK_AREA_LEFT + c * BRICK_WIDTH  # Calculate x position
            y = BRICK_AREA_TOP + r * BRICK_HEIGHT  # Calculate y position
            brick_grid[c][r] = Brick(x, y)  # Place a brick there

# Scores - Keeping track of who’s winning
score1 = 0  # Player’s score (left)
score2 = 0  # AI’s score (right)

# **Add More Bricks Function** - Adds bricks when someone scores
def add_more_bricks():
    empty_positions = [(c, r) for c in range(NUM_COLS) for r in range(NUM_ROWS) if not brick_grid[c][r]]  # Finds empty spots
    if empty_positions:  # If there are empty spots
        num_to_add = min(5, len(empty_positions))  # Adds up to 5 bricks
        positions = random.sample(empty_positions, num_to_add)  # Picks random spots
        for c, r in positions:  # Loops through chosen spots
            x = BRICK_AREA_LEFT + c * BRICK_WIDTH  # Sets x
            y = BRICK_AREA_TOP + r * BRICK_HEIGHT  # Sets y
            brick_grid[c][r] = Brick(x, y)  # Adds a brick

# **AI Movement Function** - Makes the right paddle smart
def ai_move(paddle, ball):
    paddle_center = paddle.y + paddle.height / 2  # Finds the middle of the paddle
    if ball.vx > 0:  # If ball is moving toward the AI
        target_y = ball.y + ball.size / 2 + random.uniform(-10, 10)  # Aims for the ball with a little wobble
    else:  # If ball is moving away
        target_y = SCREEN_HEIGHT / 2  # Goes back to the middle
    dy = target_y - paddle_center  # How far to move
    move_speed = 4  # AI’s max speed
    dy = max(min(dy, move_speed), -move_speed)  # Keeps movement smooth
    paddle.move(dy)  # Moves the paddle

# **Game Loop** - Where the magic happens!
running = True  # Keeps our game going
while running:
    for event in pygame.event.get():  # Checks for things like closing the window
        if event.type == pygame.QUIT:  # If you click the X
            running = False  # Stops the game
    
    # Player controls (left paddle)
    keys = pygame.key.get_pressed()  # Checks which keys you’re pressing
    if keys[pygame.K_w]:  # W key moves up
        left_paddle.move(-5)
    if keys[pygame.K_s]:  # S key moves down
        left_paddle.move(5)
    
    # AI controls (right paddle)
    ai_move(right_paddle, ball)  # Let the AI do its thing
    
    # Update ball position
    ball.update()  # Moves the ball
    
    # Ball hits top or bottom walls
    if ball.y <= 0 or ball.y + ball.size >= SCREEN_HEIGHT:  # If it hits the top or bottom
        ball.vy = -ball.vy  # Bounces it back
    
    # Ball hits paddles
    if (ball.x < left_paddle.x + left_paddle.width and  # If ball hits left paddle
        left_paddle.y < ball.y + ball.size and
        ball.y < left_paddle.y + left_paddle.height):
        ball.vx = -ball.vx  # Bounces horizontally
        hit_pos = (ball.y + ball.size / 2 - left_paddle.y) / left_paddle.height  # Where it hit
        ball.vy = (hit_pos - 0.5) * 10  # Changes vertical speed based on hit spot
        ball_hit_sound.play()  # Beep!
    
    elif (ball.x + ball.size > right_paddle.x and  # If ball hits right paddle
          right_paddle.y < ball.y + ball.size and
          ball.y < right_paddle.y + right_paddle.height):
        ball.vx = -ball.vx  # Bounces horizontally
        hit_pos = (ball.y + ball.size / 2 - right_paddle.y) / right_paddle.height  # Where it hit
        ball.vy = (hit_pos - 0.5) * 10  # Changes vertical speed
        ball_hit_sound.play()  # Beep!
    
    # Ball hits bricks
    for c in range(NUM_COLS):  # Checks every column
        for r in range(NUM_ROWS):  # Checks every row
            brick = brick_grid[c][r]  # Gets the brick (if there is one)
            if brick and (brick.x < ball.x + ball.size and  # If ball hits a brick
                          brick.x + brick.width > ball.x and
                          brick.y < ball.y + ball.size and
                          brick.y + brick.height > ball.y):
                overlap_x = min(ball.x + ball.size - brick.x, brick.x + brick.width - ball.x)  # How much overlap horizontally
                overlap_y = min(ball.y + ball.size - brick.y, brick.y + brick.height - ball.y)  # How much overlap vertically
                if overlap_x < overlap_y:  # If it hit the side
                    ball.vx = -ball.vx  # Bounce horizontally
                else:  # If it hit top or bottom
                    ball.vy = -ball.vy  # Bounce vertically
                brick_grid[c][r] = None  # Brick goes poof!
                brick_hit_sound.play()  # Crunch sound!
    
    # Scoring
    if ball.x < 0:  # Ball goes past left side
        score2 += 1  # AI scores
        ball.reset()  # Reset the ball
        add_more_bricks()  # Add more bricks
        score_sound.play()  # Victory beep!
    elif ball.x > SCREEN_WIDTH:  # Ball goes past right side
        score1 += 1  # Player scores
        ball.reset()  # Reset the ball
        add_more_bricks()  # Add more bricks
        score_sound.play()  # Victory beep!
    
    # **Draw Everything** - Time to paint the screen!
    screen.fill(BLACK)  # Clears it to black
    left_paddle.draw(screen)  # Draws player paddle
    right_paddle.draw(screen)  # Draws AI paddle
    ball.draw(screen)  # Draws the ball
    for c in range(NUM_COLS):  # Loops through columns
        for r in range(NUM_ROWS):  # Loops through rows
            if brick_grid[c][r]:  # If there’s a brick
                brick_grid[c][r].draw(screen)  # Draws it
    
    # Display scores
    font = pygame.font.Font(None, 36)  # Makes a font for text
    text1 = font.render(f"Player: {score1}", True, WHITE)  # Player’s score
    text2 = font.render(f"AI: {score2}", True, WHITE)  # AI’s score
    screen.blit(text1, (100, 10))  # Puts player score on screen
    screen.blit(text2, (SCREEN_WIDTH - 200, 10))  # Puts AI score on screen
    
    pygame.display.flip()  # Shows everything we drew
    clock.tick(60)  # Keeps the game at 60 frames per second (smooth!)

# Quit Pygame - Clean up when we’re done
pygame.quit()  # Shuts down Pygame nicely