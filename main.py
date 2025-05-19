"""
Welcome to Breakout. A game with a paddle, a bouncing ball, and bricks to break out. Let the ball drop to the bottom
three times and it's game over.

About this program:
Constants are defined in all caps at the top of the program.
There are three globals: window, canvas, and run. These should be the only ones.
"""
# TODO: add opening screen with a button to start game, return to opening screen after game ends.
# TODO: put objects and the game state in class form

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
BRICK_WIDTH = (CANVAS_WIDTH - 10 - BRICK_GAP * 9) / 10 # Canvas width minus 10 seems to keep the bricks perfectly within the border.
BRICK_HEIGHT = 10
UPPER_BOUND = 50

DELAY = 0.01

# Instantiating global variables before referring to them in main.
run = True

# Creating the window:
window = tk.Tk()
window.title("Breakout")
window.geometry(f"{CANVAS_WIDTH + 5}x{CANVAS_HEIGHT + 5}")
window.resizable(False, False)

# Creating the canvas containing the game:
canvas = Canvas(window, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg="white")
canvas.pack()
border = canvas.create_rectangle(1, UPPER_BOUND - 7, CANVAS_WIDTH, CANVAS_HEIGHT, fill='', outline='black', tags='border')
window.update()

def main():
    # Protocol goes here to make sure the handler is recognized.
    window.protocol("WM_DELETE_WINDOW", handler)

    # Game setup.
    lay_bricks()
    num_bricks = 100
    speed_multi = 1.0
    y_velocity = 3
    paddle = init_paddle()
    ball, x_velocity = init_ball()

    lives_left = 3
    life_board = init_life_board(lives_left)

    game_over = num_bricks == 0 or lives_left == 0

    while run:
        refresh_window()

        # Animation Loop. Uses an if because the window still needs to refresh.
        if not game_over:
            update_paddle_position(paddle)
            update_ball_position(
                ball,
                x_velocity, y_velocity, speed_multi
            )

            x_velocity, y_velocity = bounce(
                ball, paddle,
                x_velocity, y_velocity
            )

            y_velocity, num_bricks, speed_multi = brick_collision_check(
                ball, paddle, life_board,
                y_velocity, num_bricks, speed_multi
            )

            if ball_touches_bottom_wall(ball):
                # Lose a life and reset ball to center when it falls off bottom of canvas.
                life_board, lives_left = update_life_board(
                    lives_left, life_board
                )

                ball, x_velocity = reset_ball(ball)
                time.sleep(0.1)

            time.sleep(DELAY)

        else:
            end_game(ball, num_bricks)

    window.destroy()

def init_life_board(lives_left):
    life_board = canvas.create_text(
        CANVAS_WIDTH - 50,
        20,
        text = f"Lives: {lives_left}",
        font = ('Arial', 20),
        fill = 'black'
    )
    return life_board

def update_life_board(lives_left, life_board):
    lives_left -= 1
    canvas.delete(life_board)
    life_board = init_life_board(lives_left)
    return life_board, lives_left

def bounce(ball, paddle, x_velocity, y_velocity):
    ball_coords = canvas.coords(ball) # where is ball
    overlapping_w_ball = canvas.find_overlapping(*ball_coords) # what is ball touching
    # ball movement definitions
    ball_moving_right = x_velocity > 0
    ball_moving_left = x_velocity < 0
    ball_moving_up = y_velocity < 0
    ball_moving_down = y_velocity > 0
    ball_touching_right = ball_coords[2] >= CANVAS_WIDTH
    ball_touching_left = ball_coords[0] <= 0
    ball_touching_top = ball_coords[1] <= UPPER_BOUND
    # paddle related definitions
    paddle_coords = canvas.coords(paddle) # where is paddle
    paddle_hit = len(overlapping_w_ball) > 1 and paddle in overlapping_w_ball # is ball touching paddle
    paddle_right_hit = ball_coords[0] > paddle_coords[2] - PADDLE_WIDTH/4 # bounce logic changes based on side of paddle
    paddle_left_hit = ball_coords[2] < paddle_coords[0] + PADDLE_WIDTH/4

    if len(ball_coords) != 4:
        return x_velocity, y_velocity  # Skip bounce logic if coords are invalid
    else:
        # if ball touches right wall
        if ball_touching_right and ball_moving_right:
            x_velocity = -x_velocity

        # if ball touches left wall
        elif ball_touching_left and ball_moving_left:
            x_velocity = -x_velocity

        # if ball touches top wall
        elif ball_touching_top and ball_moving_up:
            y_velocity = -y_velocity

        # if ball touches paddle
        elif paddle_hit and ball_moving_down: # always bounce up but can bounce backwards horizontally
            y_velocity = -y_velocity
            if paddle_right_hit and ball_moving_left: # ball touches right quarter of paddle
                x_velocity = -x_velocity
            if paddle_left_hit and ball_moving_right: # ball touches left quarter of paddle
                x_velocity = -x_velocity

        return x_velocity, y_velocity

def brick_collision_check(ball, paddle, life_board, y_velocity, num_bricks, speed_multi):
    ball_coords = canvas.coords(ball)
    overlapping = canvas.find_overlapping(*ball_coords)
    bounced = False

    for item in overlapping:
        if item in (paddle, life_board):
            continue # if the overlapping item is the paddle or lifeboard, skip
        elif "brick" in canvas.gettags(item):
            canvas.delete(item)
            num_bricks -= 1
            if bounced == False: # only bounce once if hitting two at the same time.
                bounced = True
                y_velocity = -y_velocity  # bounce
            if num_bricks % 10 == 0: # num_bricks has already gone down so it shouldn't trigger on 100 bricks.
                speed_multi = update_spdmulti(speed_multi)

    return y_velocity, num_bricks, speed_multi

def update_spdmulti(speed_multi):
    speed_multi += 0.2
    return speed_multi

def update_ball_position(ball, x_velocity, y_velocity, speed_multi):
    coords = canvas.coords(ball)
    if not coords:
        return  # Ball has been deleted or not initialized
    canvas.move(ball, x_velocity, y_velocity * speed_multi)

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
        fill="blue",
        tags="ball"
    )
    return ball, x_velocity

def update_paddle_position(paddle):
    """
    subtract the root window from the pointer position on screen, otherwise window size will be from the top left
    corner of the screen, even though window might be elsewhere on screen.
    """
    abs_coord_x = window.winfo_pointerx() - window.winfo_rootx()

    """
    locked_x is the max of either the left side of the canvas, or the minimum of either the right edge of the canvas
    or the center of the paddle wherever the mouse is. This locks the paddle inside the canvas so it doesn't follow
    the mouse off screen.
    """
    locked_x = max(0, min(CANVAS_WIDTH - PADDLE_WIDTH, abs_coord_x - PADDLE_WIDTH/2))
    canvas.moveto(paddle, locked_x, PADDLE_Y)

def init_paddle():
    paddle = canvas.create_rectangle(
        CANVAS_WIDTH/2 - PADDLE_WIDTH/2,
        PADDLE_Y,
        CANVAS_WIDTH/2 + PADDLE_WIDTH/2,
        PADDLE_Y + PADDLE_HEIGHT,
        fill="black",
        tags="paddle"
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
        brick_left_x = 5 + canvas.coords(border)[0]
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
        brick_top_y = (UPPER_BOUND + 5) + i * (BRICK_HEIGHT + BRICK_GAP) # first instance of brick_top_y variable
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
    for i in range(-3, 4):
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
    # End game with either a congrats or loss text.
    if num_bricks == 0:
        canvas.delete(ball)
        canvas.create_text(
            CANVAS_WIDTH / 2,
            CANVAS_HEIGHT / 2,
            anchor = 'center',
            text = 'You Won!',
            font = ('Arial', 40),
            fill = 'red'
        )
    elif num_bricks > 0:
        canvas.delete(ball)
        canvas.create_text(
            CANVAS_WIDTH / 2,
            CANVAS_HEIGHT / 2,
            anchor = 'center',
            text = 'Oh No! You Lost.',
            font = ('Arial', 40),
            fill = 'black'
        )

if __name__ == '__main__':
    main()