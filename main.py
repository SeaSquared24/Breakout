"""
Welcome to Breakout. A game with a paddle, a bouncing ball, and bricks to break out. Let the ball drop to the bottom
three times and it's game over.

About this program:
Constants are defined in all caps at the top of the program.
There are three globals: window, canvas, and run. These should be the only ones.
"""
# TODO: add opening screen with a button to start game, return to opening screen after game ends.

import tkinter as tk
from tkinter import Canvas
import time
import random

CANVAS_WIDTH = 500
CANVAS_HEIGHT = 600

PADDLE_Y = CANVAS_HEIGHT - 30
PADDLE_WIDTH = 80
PADDLE_HEIGHT = 15

BALL_DIAMETER = 20
BALL_RADIUS = BALL_DIAMETER/2

BRICK_GAP = 5
BRICK_WIDTH = (CANVAS_WIDTH - BRICK_GAP * 9) / 10
BRICK_HEIGHT = 10

DELAY = 0.05

def main():
    # Window handling. See def handler()
    global run
    run = True

    game_over = False

    # Creating the window:
    global window
    window = tk.Tk()
    window.title("Breakout")
    window.geometry(f"{CANVAS_WIDTH + 5}x{CANVAS_HEIGHT + 5}")
    window.resizable(False, False)
    window.protocol("WM_DELETE_WINDOW", handler)

    # Creating the canvas containing the game:
    global canvas
    canvas = Canvas(window, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg="white")
    canvas.pack()
    window.update()

    # Game setup.
    # lay_bricks() lays 100 bricks so right now, it doesn't have assigned obj names.
    # bricks are removed using index number of the output of canvas.find_overlapping when the ball touches them.
    lay_bricks()
    num_bricks = 100
    y_velocity = 10
    paddle = init_paddle()
    ball, x_velocity = init_ball()

    lives_left = 3
    life_board = init_life_board(lives_left)

    while run:
        refresh_window()
        # Animation Loop. Uses an if because the window still needs to refresh.
        if not game_over:
            update_paddle_position(paddle)
            update_ball_position(ball, x_velocity, y_velocity)

            x_velocity, y_velocity = bounce(ball, paddle, x_velocity, y_velocity, num_bricks)
            y_velocity, num_bricks = brick_collision_check(ball, paddle, life_board, y_velocity, num_bricks)

            if ball_touches_bottom_wall(ball):
                # Lose a life and reset ball to center when it falls off bottom of canvas.
                life_board, lives_left = update_life_board(lives_left, life_board)
                ball, x_velocity = reset_ball(ball)
                time.sleep(0.1)

            game_over = check_game_state(num_bricks, lives_left, game_over)
            time.sleep(DELAY)

        else:
            end_game(ball, num_bricks)

    window.destroy()

def check_game_state(num_bricks, lives_left, game_over):
    if not (bricks_left(num_bricks) and still_have_lives(lives_left)):
        return True
    return False

def bricks_left(num_bricks):
    return num_bricks > 0

def still_have_lives(lives_left):
    return lives_left > 0

def init_life_board(lives_left):
    life_board = canvas.create_text(
        CANVAS_WIDTH - 50,
        CANVAS_HEIGHT - 50,
        text = str(lives_left),
        font = ('Arial', 30),
        fill = 'black'
    )
    return life_board

def update_life_board(lives_left, life_board):
    lives_left -= 1
    canvas.delete(life_board)
    life_board = init_life_board(lives_left)
    return life_board, lives_left

def bounce(ball, paddle, x_velocity, y_velocity, num_bricks):
    ball_coords = canvas.coords(ball)

    if len(ball_coords) != 4:
        return x_velocity, y_velocity  # Skip bounce logic if coords are invalid

    # if ball touches right wall
    if ball_coords[2] >= CANVAS_WIDTH and ball_moving_right(x_velocity):
        x_velocity = -x_velocity

    # if ball touches left wall
    if ball_coords[0] <= 0 and ball_moving_left(x_velocity):
        x_velocity = -x_velocity

    # if ball touches top wall
    if ball_coords[1] <= 0 and ball_moving_up(y_velocity):
        y_velocity = -y_velocity

    # if ball touches paddle
    overlapping = canvas.find_overlapping(*ball_coords)
    if len(overlapping) > 1 and paddle in overlapping and y_velocity > 0:
        y_velocity = -y_velocity

    return x_velocity, y_velocity

def ball_moving_right(x_velocity):
    return x_velocity > 0

def ball_moving_left(x_velocity):
    return x_velocity < 0

def ball_moving_up(y_velocity):
    return y_velocity < 0

def brick_collision_check(ball, paddle, life_board, y_velocity, num_bricks):
    ball_coords = canvas.coords(ball)
    overlapping = canvas.find_overlapping(*ball_coords)

    brick_hit = False  # Track if we hit any bricks

    for item in overlapping:
        if item in (paddle, life_board):
            continue # if the overlapping item is the paddle or lifeboard, skip
        if "brick" in canvas.gettags(item):
            canvas.delete(item)
            num_bricks -= 1
            brick_hit = True  # Mark that we should invert y_velocity

    if brick_hit:
        y_velocity = -y_velocity # bounce

    return y_velocity, num_bricks

def update_ball_position(ball, x_velocity, y_velocity):
    coords = canvas.coords(ball)
    if not coords:
        return  # Ball has been deleted or not initialized
    canvas.moveto(ball, coords[0] + x_velocity, coords[1] + y_velocity)

def reset_ball(ball):
    canvas.delete(ball)
    return init_ball()

def init_ball():
    x_velocity = random_excluding_zero()
    ball = canvas.create_oval(
        CANVAS_WIDTH/2,
        CANVAS_HEIGHT/2,
        CANVAS_WIDTH/2 + BALL_DIAMETER,
        CANVAS_HEIGHT/2 + BALL_DIAMETER,
        fill="blue"
    )
    return ball, x_velocity

def update_paddle_position(paddle):
    abs_coord_x = window.winfo_pointerx() - window.winfo_rootx()
    new_x = max(0, min(CANVAS_WIDTH - PADDLE_WIDTH, abs_coord_x - PADDLE_WIDTH/2))
    canvas.moveto(paddle, new_x, PADDLE_Y)

def init_paddle():
    paddle = canvas.create_rectangle(
        CANVAS_WIDTH/2 - PADDLE_WIDTH/2,
        PADDLE_Y,
        CANVAS_WIDTH/2 + PADDLE_WIDTH/2,
        PADDLE_Y + PADDLE_HEIGHT,
        fill="black"
    )
    return paddle

def ball_touches_bottom_wall(ball):
    coords = canvas.coords(ball)
    if len(coords) != 4:
        return False
    y2 = coords[3]
    return y2 >= CANVAS_HEIGHT

def lay_brick_row(brick_top_y, color):
    """
    Prints a single row of bricks left to right. Accepts variables for a new
    row and color each time it runs.
    """
    for i in range(10):
        brick_left_x = 0
        brick_right_x = brick_left_x + BRICK_WIDTH
        brick_bottom_y = brick_top_y + BRICK_HEIGHT
        # Just going across one row here (only manipulating x values). New rows handled in lay_bricks.
        canvas.create_rectangle(
            brick_left_x + (BRICK_WIDTH + BRICK_GAP) * i, # refers to i because bricks are laid along x-axis i number of times.
            brick_top_y,
            brick_right_x + (BRICK_WIDTH + BRICK_GAP) * i,# this one has to match the operations on left_x because if it doesn't the bricks end up upside down.
            brick_bottom_y,
            fill=color,
            outline='',
            tags="brick"
        )

def lay_bricks():
    """
    Lays ten rows by passing the color and new y variable to the lay_brick_row
    function: two rows red, two orange, etc.
    """
    for i in range(10):
        brick_top_y = i * (BRICK_HEIGHT + BRICK_GAP) # first instance of brick_top_y variable
        if i <= 1:
            lay_brick_row(brick_top_y, 'red')
        elif 2 <= i <= 3:
            lay_brick_row(brick_top_y, 'orange')
        elif 4 <= i <= 5:
            lay_brick_row(brick_top_y, 'yellow')
        elif 6 <= i <= 7:
            lay_brick_row(brick_top_y, 'lime')
        elif i >= 8:
            lay_brick_row(brick_top_y, 'cyan')

def random_excluding_zero():
    # Only used to shoot the ball at a new angle. Roll random ints between -8 and 8. The list excludes 0.
    num_lst = init_num_lst()
    result = random.choice(num_lst)
    return result

def init_num_lst():
    # Only used for random_excluding_zero(). Creates a list of ints from -8 to 8 without zero in it.
    num_lst = []
    for i in range(-8, 9):
        if i != 0:
            num_lst.append(i)
    return num_lst

def refresh_window():
    # Redraw the window.
    window.update()
    window.update_idletasks()

def handler():
    # Allows graceful exit when window is closed.
    global run
    run = False

def end_game(ball, num_bricks):
    # End game with either a congrats or wompwomp.
    if num_bricks == 0:
        canvas.delete(ball)
        congrats = canvas.create_text(
            CANVAS_WIDTH / 2,
            CANVAS_HEIGHT / 2,
            anchor = 'center',
            text = 'You Won!',
            font = ('Arial', 40),
            fill = 'red'
        )
    elif num_bricks > 0:
        canvas.delete(ball)
        wompwomp = canvas.create_text(
            CANVAS_WIDTH / 2,
            CANVAS_HEIGHT / 2,
            anchor = 'center',
            text = 'Oh No! You Lost.',
            font = ('Arial', 40),
            fill = 'black'
        )

if __name__ == '__main__':
    main()