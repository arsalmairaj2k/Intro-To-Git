import pygame
import random
import asyncio
import platform

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 300, 300
LINE_WIDTH = 5
BOARD_ROWS, BOARD_COLS = 3, 3
SQUARE_SIZE = WIDTH // BOARD_COLS
CIRCLE_RADIUS = SQUARE_SIZE // 3
CIRCLE_WIDTH = 15
CROSS_WIDTH = 25
SPACE = SQUARE_SIZE // 4

# Colors
BG_COLOR = (28, 170, 156)
LINE_COLOR = (23, 145, 135)
CIRCLE_COLOR = (239, 231, 200)
CROSS_COLOR = (66, 66, 66)

# Setup display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Tic Tac Toe')
screen.fill(BG_COLOR)

# Board
board = [['' for _ in range(BOARD_COLS)] for _ in range(BOARD_ROWS)]

# Fonts
font = pygame.font.SysFont('arial', 40)

def draw_lines():
    # Horizontal lines
    for i in range(1, BOARD_ROWS):
        pygame.draw.line(screen, LINE_COLOR, (0, i * SQUARE_SIZE), (WIDTH, i * SQUARE_SIZE), LINE_WIDTH)
    # Vertical lines
    for i in range(1, BOARD_COLS):
        pygame.draw.line(screen, LINE_COLOR, (i * SQUARE_SIZE, 0), (i * SQUARE_SIZE, HEIGHT), LINE_WIDTH)

def draw_figures():
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            if board[row][col] == 'X':
                pygame.draw.line(screen, CROSS_COLOR, 
                    (col * SQUARE_SIZE + SPACE, row * SQUARE_SIZE + SPACE),
                    (col * SQUARE_SIZE + SQUARE_SIZE - SPACE, row * SQUARE_SIZE + SQUARE_SIZE - SPACE), CROSS_WIDTH)
                pygame.draw.line(screen, CROSS_COLOR,
                    (col * SQUARE_SIZE + SQUARE_SIZE - SPACE, row * SQUARE_SIZE + SPACE),
                    (col * SQUARE_SIZE + SPACE, row * SQUARE_SIZE + SQUARE_SIZE - SPACE), CROSS_WIDTH)
            elif board[row][col] == 'O':
                pygame.draw.circle(screen, CIRCLE_COLOR,
                    (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2),
                    CIRCLE_RADIUS, CIRCLE_WIDTH)

def mark_square(row, col, player):
    board[row][col] = player

def available_square(row, col):
    return board[row][col] == ''

def is_board_full():
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            if board[row][col] == '':
                return False
    return True

def check_win_condition(player):
    # Vertical
    for col in range(BOARD_COLS):
        if board[0][col] == player and board[1][col] == player and board[2][col] == player:
            return True, ('vertical', col)
    # Horizontal
    for row in range(BOARD_ROWS):
        if board[row][0] == player and board[row][1] == player and board[row][2] == player:
            return True, ('horizontal', row)
    # Diagonal
    if board[0][0] == player and board[1][1] == player and board[2][2] == player:
        return True, ('diagonal', True)
    if board[2][0] == player and board[1][1] == player and board[0][2] == player:
        return True, ('diagonal', False)
    return False, None

def check_winner(player):
    won, win_type = check_win_condition(player)
    if won:
        if win_type[0] == 'vertical':
            draw_vertical_winning_line(win_type[1], player)
        elif win_type[0] == 'horizontal':
            draw_horizontal_winning_line(win_type[1], player)
        elif win_type[0] == 'diagonal':
            draw_diagonal_winning_line(player, win_type[1])
    return won

def draw_vertical_winning_line(col, player):
    posX = col * SQUARE_SIZE + SQUARE_SIZE // 2
    color = CIRCLE_COLOR if player == 'O' else CROSS_COLOR
    pygame.draw.line(screen, color, (posX, 15), (posX, HEIGHT - 15), 15)

def draw_horizontal_winning_line(row, player):
    posY = row * SQUARE_SIZE + SQUARE_SIZE // 2
    color = CIRCLE_COLOR if player == 'O' else CROSS_COLOR
    pygame.draw.line(screen, color, (15, posY), (WIDTH - 15, posY), 15)

def draw_diagonal_winning_line(player, main_diagonal):
    color = CIRCLE_COLOR if player == 'O' else CROSS_COLOR
    if main_diagonal:
        pygame.draw.line(screen, color, (15, 15), (WIDTH - 15, HEIGHT - 15), 15)
    else:
        pygame.draw.line(screen, color, (15, HEIGHT - 15), (WIDTH - 15, 15), 15)

def ai_move():
    # Check for winning move
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            if available_square(row, col):
                board[row][col] = 'O'
                won, _ = check_win_condition('O')
                if won:
                    board[row][col] = ''
                    return row, col
                board[row][col] = ''
    
    # Check for blocking player's winning move
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            if available_square(row, col):
                board[row][col] = 'X'
                won, _ = check_win_condition('X')
                if won:
                    board[row][col] = ''
                    return row, col
                board[row][col] = ''
    
    # Choose random move
    available = [(row, col) for row in range(BOARD_ROWS) for col in range(BOARD_COLS) if available_square(row, col)]
    return random.choice(available) if available else None

def display_message(message):
    # Draw semi-transparent overlay
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(128)  # 128 is semi-transparent
    overlay.fill((0, 0, 0))  # black overlay
    screen.blit(overlay, (0, 0))
    
    # Draw message
    text = font.render(message, True, (255, 255, 255))
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    
    # Add a background rectangle for the text
    padding = 20
    bg_rect = pygame.Rect(text_rect.left - padding, text_rect.top - padding,
                         text_rect.width + 2*padding, text_rect.height + 2*padding)
    pygame.draw.rect(screen, BG_COLOR, bg_rect)
    pygame.draw.rect(screen, LINE_COLOR, bg_rect, 2)
    
    screen.blit(text, text_rect)
    pygame.display.update()

async def main():
    global game_over
    game_over = False
    player = 'X'  # Human starts
    
    # Call setup to initialize the board
    setup()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            
            if event.type == pygame.MOUSEBUTTONDOWN and not game_over and player == 'X':
                mouseX, mouseY = event.pos
                clicked_row = mouseY // SQUARE_SIZE
                clicked_col = mouseX // SQUARE_SIZE
                
                if available_square(clicked_row, clicked_col):
                    mark_square(clicked_row, clicked_col, 'X')
                    draw_figures()
                    if check_winner('X'):
                        game_over = True
                        display_message("Player X Wins!")
                    elif is_board_full():
                        game_over = True
                        display_message("Tie Game!")
                    else:
                        player = 'O'
                    pygame.display.update()
        
        if not game_over and player == 'O':
            move = ai_move()
            if move:
                row, col = move
                mark_square(row, col, 'O')
                draw_figures()
                if check_winner('O'):
                    game_over = True
                    display_message("AI (O) Wins!")
                elif is_board_full():
                    game_over = True
                    display_message("Tie Game!")
                else:
                    player = 'X'
                pygame.display.update()
        
        await asyncio.sleep(1.0 / 60)  # 60 FPS

def setup():
    screen.fill(BG_COLOR)
    draw_lines()
    pygame.display.update()

def update_loop():
    if not game_over:
        draw_figures()
        pygame.display.update()

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())