# Import Pygame for graphics and sound, and random for picking Tetriminos
import pygame  # This is a library that helps us make games with graphics, sound, and input handling.
import random  # This lets us pick random numbers, which we’ll use to choose the next Tetris piece.
import numpy as np  # A math library we’ll use to create sound effects with waves.

# Start Pygame
pygame.init()  # This wakes up Pygame so it’s ready to handle graphics, sound, and more.

# Set up the game window: 475x600 pixels
WIDTH, HEIGHT = 475, 600  # These are the width and height of our game window in pixels.
screen = pygame.display.set_mode((WIDTH, HEIGHT))  # Creates the window we’ll draw everything on.
pygame.display.set_caption("Tetris")  # Sets the window title to "Tetris" – neat, right?

# Define colors in RGB format (Red, Green, Blue values from 0 to 255)
BLACK = (0, 0, 0)    # Pure black for the background – all zeros mean no color.
WHITE = (255, 255, 255)  # Bright white for text – all 255s mean full color.
GRAY = (128, 128, 128)   # A medium gray for block borders – halfway between black and white.

# Define the game board: 10x20 grid, 30x30 pixel cells
BOARD_WIDTH, BOARD_HEIGHT = 10, 20  # The board is 10 cells wide and 20 cells tall.
CELL_SIZE = 30  # Each cell (or square) on the board is 30 pixels by 30 pixels.

# Define Tetriminos (shapes, colors, and rotations)
# Tetriminos are the falling pieces in Tetris. Each has a color and 4 possible shapes (for rotations).
tetriminos = [
    # 'I' piece: a long straight line
    {'color': (0, 255, 255), 'shapes': [[(0,0), (1,0), (2,0), (3,0)], [(0,0), (0,1), (0,2), (0,3)], [(0,0), (1,0), (2,0), (3,0)], [(0,0), (0,1), (0,2), (0,3)]]},  # Cyan
    # 'O' piece: a square (no rotation needed, so it’s the same 4 times)
    {'color': (255, 255, 0), 'shapes': [[(0,0), (1,0), (0,1), (1,1)] for _ in range(4)]},  # Yellow
    # 'T' piece: a T-shape
    {'color': (128, 0, 128), 'shapes': [[(1,0), (0,1), (1,1), (2,1)], [(0,1), (1,0), (1,1), (1,2)], [(0,1), (1,1), (2,1), (1,2)], [(1,0), (1,1), (1,2), (2,1)]]},  # Purple
    # 'S' piece: a zigzag
    {'color': (0, 255, 0), 'shapes': [[(1,0), (2,0), (0,1), (1,1)], [(0,0), (0,1), (1,1), (1,2)], [(1,0), (2,0), (0,1), (1,1)], [(0,0), (0,1), (1,1), (1,2)]]},  # Green
    # 'Z' piece: an opposite zigzag
    {'color': (255, 0, 0), 'shapes': [[(0,0), (1,0), (1,1), (2,1)], [(1,0), (0,1), (1,1), (0,2)], [(0,0), (1,0), (1,1), (2,1)], [(1,0), (0,1), (1,1), (0,2)]]},  # Red
    # 'J' piece: an L-shape flipped
    {'color': (0, 0, 255), 'shapes': [[(0,0), (0,1), (1,1), (2,1)], [(1,0), (0,0), (0,1), (0,2)], [(0,1), (1,1), (2,1), (2,2)], [(1,2), (0,0), (0,1), (0,2)]]},  # Blue
    # 'L' piece: an L-shape
    {'color': (255, 165, 0), 'shapes': [[(2,0), (0,1), (1,1), (2,1)], [(0,0), (0,1), (0,2), (1,2)], [(0,1), (1,1), (2,1), (0,2)], [(1,0), (0,0), (0,1), (0,2)]]}  # Orange
]
# Each shape is a list of (x, y) coordinates showing where the blocks are relative to a starting point.

# Create an empty game board
# This makes a 20-row, 10-column grid where each spot starts as None (empty).
board = [[None for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]

# Set up clock and font
clock = pygame.time.Clock()  # Helps control the game speed – like a metronome!
font = pygame.font.SysFont("Arial", 24)  # Sets up a font (Arial, size 24) for text like the score.

# Initialize Pygame's sound system
pygame.mixer.init(frequency=44100, size=-16, channels=1)  # Sets up sound: 44100 Hz (standard audio rate), 16-bit, mono (1 channel).

# Load and play background music
pygame.mixer.music.load('/your/file/path/here/tetris/Tetris_remix.wav')  # Loads a music file (Change the file path to what's relevant to your computer!).
pygame.mixer.music.set_volume(0.5)  # Sets volume to half strength (0.0 to 1.0 scale).
pygame.mixer.music.play(-1)  # Plays the music in a loop forever (-1 means infinite).

# Function to generate a simple sine wave sound
def generate_sound(frequency, duration):
    # This creates a sound effect by making a sine wave (a smooth beep or tone).
    sample_rate = 44100  # How many sound samples per second – 44100 is CD quality.
    n_samples = int(sample_rate * duration)  # Total samples based on how long the sound lasts.
    t = np.linspace(0, duration, n_samples, False)  # Splits time into tiny steps for the wave.
    audio = 32767 * np.sin(2 * np.pi * frequency * t)  # Makes a sine wave at the given frequency (pitch).
    sound_array = audio.astype(np.int16)  # Turns the wave into a format Pygame understands (16-bit numbers).
    stereo_array = np.column_stack((sound_array, sound_array))  # Makes it stereo by duplicating for left and right speakers.
    return pygame.sndarray.make_sound(stereo_array)  # Turns it into a playable sound.

# Create sound effects with different frequencies and durations
move_sound = generate_sound(440, 0.1)      # A short beep (A4 note) when moving left or right.
rotate_sound = generate_sound(523, 0.1)    # A higher beep (C5) for rotating a piece.
land_sound = generate_sound(261, 0.2)      # A deeper thud (C4) when a piece lands.
line_sound = generate_sound(659, 0.3)      # A longer chime (E5) when you clear a line.
gameover_sound = generate_sound(196, 0.5)  # A low tone (G3) for game over – sounds dramatic!

# Game variables
score = 0  # Keeps track of your points.
level = 0  # Starts at level 0; increases with more lines cleared.
total_lines = 0  # Counts how many lines you’ve cleared.
fall_speed = 0.5  # How fast pieces fall (in seconds per drop) – starts slow.
fall_time = 0  # Tracks time since the last drop.
game_over = False  # False means the game is still going; True means it’s done.
next_type = random.randint(0, 6)  # Picks a random number (0-6) for the next Tetrimino type.

# Spawn a new Tetrimino
def spawn_new_tetrimino():
    global current_type, current_rotation, current_x, current_y, next_type, game_over  # These are variables we’ll change everywhere.
    current_type = next_type  # The current piece becomes the one that was next.
    next_type = random.randint(0, 6)  # Pick a new random piece for next time.
    current_rotation = 0  # Start with the first rotation (0 out of 4).
    current_x = 3  # Start near the middle of the board (column 3 out of 10).
    shape = tetriminos[current_type]['shapes'][current_rotation]  # Get the shape of this piece.
    max_dy = max(dy for dx, dy in shape)  # Find the tallest part of the shape (highest y value).
    current_y = -max_dy  # Start above the board so it drops in smoothly.
    for dx, dy in shape:  # Check each block in the shape.
        board_x = current_x + dx  # Where it lands horizontally.
        board_y = current_y + dy  # Where it lands vertically.
        if board_y >= 0 and board[board_y][board_x] is not None:  # If it’s on the board and hits something...
            game_over = True  # Game ends because the board is too full!
            gameover_sound.play()  # Play that sad game-over sound.
            break  # Stop checking – it’s over.

# Check if a move or rotation is possible
def can_move(x, y, rotation):
    shape = tetriminos[current_type]['shapes'][rotation]  # Get the shape for this rotation.
    for dx, dy in shape:  # Look at each block in the shape.
        board_x = x + dx  # New x position.
        board_y = y + dy  # New y position.
        if board_x < 0 or board_x >= BOARD_WIDTH or board_y >= BOARD_HEIGHT:  # Off the sides or bottom?
            return False  # Can’t move there.
        if board_y >= 0 and board[board_y][board_x] is not None:  # Hits another block?
            return False  # Can’t move there either.
    return True  # All clear – move is okay!

# Land a Tetrimino on the board
def land_tetrimino():
    global score, total_lines, level, fall_speed  # Update these game stats.
    shape = tetriminos[current_type]['shapes'][current_rotation]  # Get the current shape.
    for dx, dy in shape:  # For each block in the shape...
        board_x = current_x + dx  # Where it lands horizontally.
        board_y = current_y + dy  # Where it lands vertically.
        if board_y >= 0:  # If it’s on the board (not above it)...
            board[board_y][board_x] = tetriminos[current_type]['color']  # Paint it with the piece’s color.
    land_sound.play()  # Play a thud sound – it’s landed!
    lines_cleared = 0  # Count how many lines we clear.
    for row in range(BOARD_HEIGHT - 1, -1, -1):  # Check each row from bottom to top.
        if all(cell is not None for cell in board[row]):  # If every cell in the row is filled...
            del board[row]  # Remove that row.
            board.insert(0, [None for _ in range(BOARD_WIDTH)])  # Add an empty row at the top.
            lines_cleared += 1  # Add to our line count.
    if lines_cleared > 0:  # If we cleared any lines...
        line_sound.play()  # Play a happy chime!
        score += [0, 40, 100, 300, 1200][lines_cleared] * (level + 1)  # Add points based on lines cleared and level.
        total_lines += lines_cleared  # Update total lines.
        new_level = total_lines // 10  # Every 10 lines, level up!
        if new_level > level:  # If we hit a new level...
            level = new_level  # Update the level.
            fall_speed = max(0.1, 0.5 - level * 0.05)  # Pieces fall faster (but not below 0.1 seconds).
    spawn_new_tetrimino()  # Bring in the next piece.

# Function to create a pronounced gradient effect for blocks
def draw_gradient_block(surface, x, y, size, base_color):
    # This makes blocks look fancy with a light-to-dark gradient.
    light_color = tuple(min(c + 70, 255) for c in base_color)  # Brighten the color (but not past 255).
    dark_color = tuple(max(c - 70, 0) for c in base_color)     # Darken the color (but not below 0).
    for i in range(size):  # Draw the block line by line.
        r = int(light_color[0] + (dark_color[0] - light_color[0]) * i / size)  # Blend red.
        g = int(light_color[1] + (dark_color[1] - light_color[1]) * i / size)  # Blend green.
        b = int(light_color[2] + (dark_color[2] - light_color[2]) * i / size)  # Blend blue.
        pygame.draw.line(surface, (r, g, b), (x, y + i), (x + size - 1, y + i))  # Draw a horizontal line.
    pygame.draw.rect(surface, GRAY, (x, y, size, size), 1)  # Add a gray border around the block.

# Draw the game board with gradient blocks
def draw_board():
    for row in range(BOARD_HEIGHT):  # Go through every row.
        for col in range(BOARD_WIDTH):  # And every column.
            if board[row][col] is not None:  # If there’s a block there...
                draw_gradient_block(screen, col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, board[row][col])  # Draw it!

# Draw the current Tetrimino with gradient blocks
def draw_tetrimino(x, y, type, rotation):
    shape = tetriminos[type]['shapes'][rotation]  # Get the shape of the falling piece.
    color = tetriminos[type]['color']  # Get its color.
    for dx, dy in shape:  # For each block in the shape...
        board_x = x + dx  # Where it is horizontally.
        board_y = y + dy  # Where it is vertically.
        if board_y >= 0:  # If it’s on the visible board (not above it)...
            draw_gradient_block(screen, board_x * CELL_SIZE, board_y * CELL_SIZE, CELL_SIZE, color)  # Draw it!

# Draw the next Tetrimino with gradient blocks
def draw_next_tetrimino():
    shape = tetriminos[next_type]['shapes'][0]  # Get the shape of the next piece (first rotation).
    color = tetriminos[next_type]['color']  # Get its color.
    for dx, dy in shape:  # For each block...
        draw_x = 330 + dx * 15  # Position it on the right side of the screen (smaller scale: 15 pixels).
        draw_y = 50 + dy * 15  # Position it near the top.
        draw_gradient_block(screen, draw_x, draw_y, 15, color)  # Draw a smaller version.

# Draw score and level
def draw_score():
    score_text = font.render(f"Score: {score}", True, WHITE)  # Make text showing the score.
    screen.blit(score_text, (330, 200))  # Put it on the right side of the screen.

def draw_level():
    level_text = font.render(f"Level: {level}", True, WHITE)  # Make text showing the level.
    screen.blit(level_text, (330, 250))  # Put it below the score.

# Draw controls on the HUD (heads-up display)
def draw_controls():
    controls = [
        "Controls:", "Left: ←", "Right: →", "Down: ↓", "Rotate: ↑", "Drop: Space"
    ]  # List of instructions.
    y_offset = 300  # Start position below the level text.
    for line in controls:  # For each line...
        text = font.render(line, True, WHITE)  # Make it into white text.
        screen.blit(text, (330, y_offset))  # Draw it on the right side.
        y_offset += 30  # Move down for the next line.

# Draw game over text
def draw_game_over():
    game_over_text = font.render("Game Over", True, WHITE)  # Make "Game Over" text.
    screen.blit(game_over_text, (150, 300))  # Put it near the center of the screen.

# Start the game
spawn_new_tetrimino()  # Drop the first piece into play.

# Main game loop
running = True  # Keeps the game going until we say stop.
while running:  # This loop runs over and over until the game ends.
    for event in pygame.event.get():  # Check for things like key presses or closing the window.
        if event.type == pygame.QUIT:  # If you click the window’s close button...
            running = False  # Stop the game.
        elif event.type == pygame.KEYDOWN and not game_over:  # If a key is pressed and the game isn’t over...
            if event.key == pygame.K_LEFT:  # Left arrow?
                if can_move(current_x - 1, current_y, current_rotation):  # Can we move left?
                    current_x -= 1  # Move the piece left.
                    move_sound.play()  # Beep!
            elif event.key == pygame.K_RIGHT:  # Right arrow?
                if can_move(current_x + 1, current_y, current_rotation):  # Can we move right?
                    current_x += 1  # Move the piece right.
                    move_sound.play()  # Beep!
            elif event.key == pygame.K_DOWN:  # Down arrow?
                if can_move(current_x, current_y + 1, current_rotation):  # Can we move down?
                    current_y += 1  # Move the piece down faster.
            elif event.key == pygame.K_UP:  # Up arrow?
                new_rotation = (current_rotation + 1) % 4  # Try the next rotation (0 to 3, then back to 0).
                if can_move(current_x, current_y, new_rotation):  # Can we rotate?
                    current_rotation = new_rotation  # Update the rotation.
                    rotate_sound.play()  # Higher beep!
            elif event.key == pygame.K_SPACE:  # Spacebar?
                while can_move(current_x, current_y + 1, current_rotation):  # Keep moving down until we can’t.
                    current_y += 1
                land_tetrimino()  # Land it immediately.

    if not game_over:  # If the game is still going...
        fall_time += clock.get_rawtime()  # Add up time since the last frame (in milliseconds).
        if fall_time / 1000 > fall_speed:  # If enough time has passed (converted to seconds)...
            if can_move(current_x, current_y + 1, current_rotation):  # Can the piece fall?
                current_y += 1  # Move it down.
            else:
                land_tetrimino()  # If not, land it.
            fall_time = 0  # Reset the fall timer.

    screen.fill(BLACK)  # Clear the screen with black before drawing.
    if not game_over:  # If the game is still on...
        draw_board()  # Draw the landed pieces.
        draw_tetrimino(current_x, current_y, current_type, current_rotation)  # Draw the falling piece.
        draw_next_tetrimino()  # Show the next piece on the side.
        draw_score()  # Show the score.
        draw_level()  # Show the level.
        draw_controls()  # Show the control instructions.
    else:
        draw_game_over()  # If it’s over, show "Game Over".

    pygame.display.flip()  # Update the screen with everything we drew.
    clock.tick(60)  # Aim for 60 frames per second – keeps the game smooth.

pygame.quit()  # Clean up and close Pygame when the game ends.