"""
Welcome to Breakout. A game with a paddle, a bouncing ball, and bricks to break out. Let the ball drop to the bottom
three times and it's game over.

About this program:
Constants are defined in all caps at the top of the program.
There are three globals: window, canvas, and run. These should be the only ones.
"""

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

    # Creating the window:
    global window
    window = tk.Tk()
    window.title("Breakout")
    window.geometry('505x605')
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
    x_velocity = random_excluding_zero()
    y_velocity = 10
    paddle = init_paddle()
    ball = init_ball()

    lives_left = 3
    life_board = init_life_board(lives_left)

    while run:
        refresh_window()
        if bricks_left(num_bricks) and still_have_lives(lives_left):
            update_paddle_position(paddle)

            update_ball_position(ball, x_velocity, y_velocity) #bugged. ball_coords list comes up empty

            x_velocity, y_velocity = bounce(ball, paddle, x_velocity, y_velocity, num_bricks)
            y_velocity, num_bricks = brick_collision_check(ball, paddle, y_velocity, num_bricks)

            if ball_touches_bottom_wall(ball):
                # Lose a life and reset ball to center when it falls off bottom of canvas.
                life_board, lives_left = update_life_board(lives_left, life_board)
                canvas.delete(ball)
                ball, x_velocity = init_ball()


            time.sleep(DELAY)

    window.destroy()

def bricks_left(num_bricks):
    if num_bricks > 0:
        return True

def still_have_lives(lives_left):
    if lives_left > 0:
        return True

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
    if x_velocity > 0:
        return True

def ball_moving_left(x_velocity):
    if x_velocity < 0:
        return True

def ball_moving_up(y_velocity):
    if y_velocity < 0:
        return True

def brick_collision_check(ball, paddle, y_velocity, num_bricks):
    # if ball touches brick
    ball_coords = canvas.coords(ball)
    overlapping = canvas.find_overlapping(*ball_coords)
    if len(overlapping) > 1 and paddle not in overlapping:
        y_velocity = -y_velocity
        canvas.delete(overlapping[0])
        num_bricks -= 1
    return y_velocity, num_bricks

def update_ball_position(ball, x_velocity, y_velocity):
    x1, y1, x2, y2 = canvas.coords(ball)
    canvas.coords(ball, x1 + x_velocity, y1 + y_velocity, x2 + x_velocity, y2 + y_velocity)

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
    canvas.moveto(paddle, abs_coord_x - PADDLE_WIDTH/2, PADDLE_Y)

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
    """
    if bottom of ball touches bottom wall of canvas, return True.
    """
    y2 = canvas.coords(ball)[3]
    if y2 >= CANVAS_HEIGHT:
        return True

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
            outline=''
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
    """
    Only used to shoot the ball at a new angle. Roll random ints between -10 and 10. The list excludes 0.
    """
    num_lst = init_num_lst()
    result = random.choice(num_lst)
    return result

def init_num_lst():
    """
    Only used for random_excluding_zero(). Creates a list of ints from -10 to 10 without zero in it.
    """
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

if __name__ == '__main__':
    main()