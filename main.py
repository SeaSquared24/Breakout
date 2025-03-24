from graphics import Canvas
import time
import random
import math

"""
TODO:
    - update all canvas usages to work in real life. current syntax is for Code in Place.
    - solve paddle bug. ball should not get stuck inside paddle when entering from side.

    - use list to pass params to ball related functions, i.e.

    def some_func(a_char, a_float, a_something):
    print a_char

    params = ['a', 3.4, None]
    some_func(*params)

    >> a
"""

CANVAS_WIDTH = 500
CANVAS_HEIGHT = 600

PADDLE_Y = CANVAS_HEIGHT - 30
PADDLE_WIDTH = 80
PADDLE_HEIGHT = 15

BALL_DIAMETER = 20

BRICK_GAP = 5
BRICK_WIDTH = (CANVAS_WIDTH - BRICK_GAP * 9) / 10
BRICK_HEIGHT = 10

DELAY = 0.05


def main():
    canvas = Canvas(CANVAS_WIDTH, CANVAS_HEIGHT)
    lay_bricks(canvas)
    num_bricks = 100
    lives = 3
    paddle = place_paddle(canvas)  # shape_100
    ball = place_ball(canvas)  # shape_101
    lives_left = life_tracker(canvas, lives)  # shape_102

    ball_left_x = canvas.get_left_x(ball)
    ball_top_y = canvas.get_top_y(ball)
    x_velocity = random_excluding_zero()
    y_velocity = 10

    while num_bricks > 0 and lives > 0:  # animation loop

        # check for collisions with safe walls
        x_velocity, y_velocity = walls_check(
            ball_left_x,
            ball_top_y,
            x_velocity,
            y_velocity
        )

        # check for collisions with other canvas objects once per loop
        y_velocity, num_bricks = collision_check(
            canvas,
            ball_left_x, ball_top_y,
            x_velocity, y_velocity,
            num_bricks
        )

        # Ball touches bottom wall. Lose a life, return to center.
        ball_left_x, ball_top_y, x_velocity, lives, lives_left = bottom_wall_check(
            canvas,
            ball,
            ball_left_x,
            ball_top_y,
            x_velocity,
            lives,
            lives_left
        )

        # Ball continues moving in straight line
        ball_left_x += x_velocity
        ball_top_y += y_velocity
        canvas.moveto(ball, ball_left_x, ball_top_y)

        # Mouse tracking for paddle
        mouse_x = canvas.get_mouse_x()
        canvas.moveto(paddle, mouse_x, PADDLE_Y)
        time.sleep(DELAY)

    end_game(canvas, ball, num_bricks)


def bottom_wall_check(canvas, ball, ball_left_x, ball_top_y, x_velocity, lives, lives_left):
    if (ball_top_y + BALL_DIAMETER) >= CANVAS_HEIGHT:
        lives, lives_left = update_lives(canvas, lives, lives_left)
        x_velocity = random_excluding_zero()  # reset x_velocity as if the game started from scratch
        ball_left_x = CANVAS_WIDTH / 2 - BALL_DIAMETER  # return ball to center
        ball_top_y = CANVAS_HEIGHT / 2 - BALL_DIAMETER
        canvas.moveto(ball, ball_left_x, ball_top_y)
        # Not returning y_velocity b/c it will always be down in this case and
        # we don't need to change that on reset.
    return ball_left_x, ball_top_y, x_velocity, lives, lives_left


def walls_check(ball_left_x, ball_top_y, x_velocity, y_velocity):
    if ball_left_x < 0 or (ball_left_x + BALL_DIAMETER) > CANVAS_WIDTH:  # check left and right walls
        x_velocity = -x_velocity
    elif ball_top_y < 0:  # check top wall
        y_velocity = -y_velocity
    return x_velocity, y_velocity


def random_excluding_zero():
    rand_int = random.randint(-10, 10)
    while rand_int == 0:
        rand_int = random.randint(-10, 10)
    return rand_int


def life_tracker(canvas, lives):
    lives_left = canvas.create_text(
        CANVAS_WIDTH - 50,
        CANVAS_HEIGHT - 50,
        text=str(lives),
        font='Arial',
        font_size=30,
        color='black'
    )
    return lives_left


def update_lives(canvas, lives, lives_left):
    lives -= 1
    canvas.delete(lives_left)
    lives_left = life_tracker(canvas, lives)  # shape_102
    return lives, lives_left


def place_ball(canvas):
    ball_left_x = CANVAS_WIDTH / 2 - BALL_DIAMETER / 2
    ball_top_y = CANVAS_HEIGHT / 2 - BALL_DIAMETER / 2
    ball_right_x = ball_left_x + BALL_DIAMETER
    ball_bottom_y = ball_top_y + BALL_DIAMETER

    ball = canvas.create_oval(
        ball_left_x,
        ball_top_y,
        ball_right_x,
        ball_bottom_y
    )
    return ball


def collision_check(canvas, x, y, x_velocity, y_velocity, num_bricks):
    overlapping = canvas.find_overlapping(x, y, x + BALL_DIAMETER, y + BALL_DIAMETER)
    if len(overlapping) > 1:
        if overlapping[0] != 'shape_100':
            y_velocity = -y_velocity
            canvas.delete(overlapping[0])
            num_bricks -= 1
        elif overlapping[0] == 'shape_100':
            y_velocity = -y_velocity
    return y_velocity, num_bricks


def place_paddle(canvas):
    """
    Create a centered paddle using the constant for height.
    """
    paddle_left_x = CANVAS_WIDTH / 2 - PADDLE_WIDTH / 2
    paddle_right_x = paddle_left_x + PADDLE_WIDTH
    paddle_bottom_y = PADDLE_Y + PADDLE_HEIGHT

    paddle = canvas.create_rectangle(
        paddle_left_x,
        PADDLE_Y,
        paddle_right_x,
        paddle_bottom_y
    )
    return paddle  # we return the object so we can manipulate its coords for mouse tracking in main


def lay_brick_row(canvas, brick_top_y, color):
    """
    Prints a single row of bricks left to right. Accepts variables for a new
    row and color each time it runs.
    """
    for r in range(10):
        brick_left_x = 0
        brick_right_x = brick_left_x + BRICK_WIDTH
        brick_bottom_y = brick_top_y + BRICK_HEIGHT
        # Just going across one row here (only manipulating x values). New rows handled in lay_bricks.
        canvas.create_rectangle(
            brick_left_x + (BRICK_WIDTH + BRICK_GAP) * r,
            # refers to r because bricks are laid along x axis r number of times.
            brick_top_y,
            brick_right_x + (BRICK_WIDTH + BRICK_GAP) * r,
            # this one has to match the operations on left_x because if it doesn't the bricks end up upside down.
            brick_bottom_y,
            color
        )


def lay_bricks(canvas):
    """
    Lays ten rows by passing the color and new y variable to the lay_brick_row
    function: two rows red, two orange, etc.
    """
    for i in range(10):
        brick_top_y = i * (BRICK_HEIGHT + BRICK_GAP)
        if i <= 1:
            lay_brick_row(canvas, brick_top_y, 'red')
        elif i == 2 or i == 3:
            lay_brick_row(canvas, brick_top_y, 'orange')
        elif i == 4 or i == 5:
            lay_brick_row(canvas, brick_top_y, 'yellow')
        elif i == 6 or i == 7:
            lay_brick_row(canvas, brick_top_y, 'lime')
        elif i >= 8:
            lay_brick_row(canvas, brick_top_y, 'cyan')


def end_game(canvas, ball, num_bricks):
    """
    End game with either a congrats or wompwomp. In the case of wompwomp, delete the ball to clean up.
    """
    if num_bricks == 0:
        canvas.delete(ball)
        congrats = canvas.create_text(
            CANVAS_WIDTH / 2 - 110,
            CANVAS_HEIGHT / 2 - 50,
            text='You Won!',
            font='Arial',
            font_size=50,
            color='red'
        )
    elif num_bricks > 0:
        canvas.delete(ball)
        wompwomp = canvas.create_text(
            CANVAS_WIDTH / 2 - 200,
            CANVAS_HEIGHT / 2 - 50,
            text='Oh No! You Lost.',
            font='Arial',
            font_size=50,
            color='black'
        )


if __name__ == '__main__':
    main()