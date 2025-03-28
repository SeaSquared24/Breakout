from graphics import Canvas
import time
import random
import math

"""
Breakout:
    This game of Breakout is built using tkinter canvas and written before the author learns classes.
    Essentially, the trick to making this work was to use a dictionary to store the coordinates of the ball
    and update that dictionary after each move. This prevents entire PILES of arguments needing to be passed
    to and returned from all the functions. Now, we just return the ball and allow the animation loop to handle
    updating our notes of where it is.

TODO:
    - add physics to cause ball to change x_velocity when hit from different sides by the paddle

    - solve paddle bug

    - rewrite function for lay_bricks in a way that labels each one on creation. So, brick_0 through brick_99 will be variables.
"""

CANVAS_WIDTH = 500
CANVAS_HEIGHT = 600

PADDLE_Y = CANVAS_HEIGHT - 30
PADDLE_WIDTH = 80
PADDLE_HEIGHT = 15

BALL_DIAMETER = 20
BALL_RADIUS = 10

BRICK_GAP = 5
BRICK_WIDTH = (CANVAS_WIDTH - BRICK_GAP * 9) / 10
BRICK_HEIGHT = 10

DELAY = 0.01

ball_params = {"bx1": None, "by1": None, "bx2": None, "by2": None}
paddle_params = {"px1": None, "py1": None, "px2": None, "py2": None}
ball_coords = ball_params.values()  # only used in canvas.find_overlapping(*ball_coords) b/c we need to unpack the dictionaries values to pass into canvas
paddle_coords = paddle_params.values()


def main():
    # Backend setup.
    num_lst = init_num_lst()
    num_bricks = 100
    lives = 3

    # Setup board
    canvas = Canvas(CANVAS_WIDTH, CANVAS_HEIGHT)
    lay_bricks(canvas)
    paddle = place_paddle(canvas)
    ball = place_ball(canvas)
    ball_params = update_ball_params(canvas, ball)  # get params for ball now that it exists
    paddle_params = update_paddle_params(canvas, paddle)  # get params for paddle now that it exists
    lives_left = life_tracker(canvas, lives)

    x_velocity = random_excluding_zero(num_lst)
    y_velocity = 10

    while num_bricks > 0 and lives > 0:  # animation loop

        ### Check ###
        # check for collisions with safe walls
        x_velocity, y_velocity = walls_check(
            x_velocity,
            y_velocity
        )

        ### Check ###
        # check for collisions with other canvas objects, minus the paddle and walls once per loop
        x_velocity, y_velocity, num_bricks = collision_check(
            canvas,
            paddle,
            x_velocity,
            y_velocity,
            num_bricks,
        )

        ### Check ###
        # Ball touches bottom wall. Lose a life, return to center.
        ball, lives, lives_left = bottom_wall_check(
            canvas,
            ball,
            lives,
            lives_left
        )

        ### Animation ###
        # Mouse tracking for paddle
        mouse_x = canvas.get_mouse_x()
        canvas.moveto(paddle, mouse_x - PADDLE_WIDTH / 2, PADDLE_Y)
        paddle_params = update_paddle_params(canvas, paddle)

        ### Paddle collision check ###
        # This goes here because we are checking the paddle coords for collisions rather than the ball coords.
        x_velocity, y_velocity = paddle_collision_check(canvas, paddle, ball, x_velocity, y_velocity)

        ### Animation ###
        # Ball continues moving in straight line
        ball_params = update_ball_params(canvas, ball)
        ball_params["bx1"] = ball_params["bx1"] + x_velocity
        ball_params["by1"] = ball_params["by1"] + y_velocity
        canvas.moveto(ball, ball_params["bx1"], ball_params["by1"])
        ball_params = update_ball_params(canvas, ball)

        time.sleep(DELAY)

    end_game(canvas, ball, num_bricks)


def bottom_wall_check(canvas, ball, lives, lives_left):
    """
    If the ball touches (bottom_y greater than or equal to) the bottom wall, update lives and print new lives_left,
    generate new ball angle, and return the ball to center of screen.
    """
    if ball_touches_bottom_wall():
        lives, lives_left = update_lives(canvas, lives, lives_left)
        canvas.delete(ball)
        ball = place_ball(canvas)

    return ball, lives, lives_left


def walls_check(x_velocity, y_velocity):
    """
    If ball touches a wall that isn't the bottom one, bounce it by flipping the x or y velocity depending on which wall it hits.
    """
    if ball_params["bx1"] <= 0 or ball_params["bx2"] >= CANVAS_WIDTH:  # check left and right walls
        x_velocity = -x_velocity
    elif ball_params["by1"] <= 0:  # check top wall
        y_velocity = -y_velocity

    return x_velocity, y_velocity


def collision_check(canvas, paddle, x_velocity, y_velocity, num_bricks):
    """
    Creates a list of overlapping objects then if there is more than one object in list (there will always be one, the ball),
    check if the other object is the paddle, if not, delete it.
    """
    overlapping = canvas.find_overlapping(*ball_coords)
    if len(overlapping) > 1:
        if paddle not in overlapping:
            y_velocity = -y_velocity
            canvas.delete(overlapping[0])
            num_bricks -= 1

    return x_velocity, y_velocity, num_bricks


def paddle_collision_check(canvas, paddle, ball, x_velocity, y_velocity):
    """
    Check for collisions with the ball from the paddle's p.o.v. We want to see if checking for paddle bounces after animating
    the paddle but before animating the ball will solve the stuck_inside_paddle bug

    *This partially worked. The ball still gets stuck when you flick it juuust right really really fast.
    """
    overlapping = canvas.find_overlapping(*paddle_coords)
    if len(overlapping) > 1:
        if ball in overlapping:
            y_velocity = -y_velocity

    return x_velocity, y_velocity

def ball_touches_bottom_wall():
    """
    if bottom of ball touches bottom wall of canvas, return True.
    """
    if ball_params["by2"] >= CANVAS_HEIGHT:
        return True


def update_ball_params(canvas, ball):
    """
    Get coords of ball and update values of keys in ball_params dict.
    """
    x1, y1 = get_coords(canvas, ball)
    x2, y2 = (x1 + BALL_DIAMETER), (y1 + BALL_DIAMETER)

    ball_params["bx1"] = x1
    ball_params["by1"] = y1
    ball_params["bx2"] = x2
    ball_params["by2"] = y2

    return ball_params


def update_paddle_params(canvas, paddle):
    """
    Get coords of paddle and update paddle dict with new values.
    """
    x1, y1 = get_coords(canvas, paddle)
    x2, y2 = (x1 + PADDLE_WIDTH), (y1 + PADDLE_HEIGHT)

    paddle_params["px1"] = x1
    paddle_params["py1"] = y1
    paddle_params["px2"] = x2
    paddle_params["py2"] = y2

    return paddle_params


def get_coords(canvas, obj):
    x, y = canvas.get_left_x(obj), canvas.get_top_y(obj)
    return x, y


def random_excluding_zero(num_lst):
    """
    Only used to shoot the ball at a new angle. Roll random ints between -10 and 10. The list excludes 0.
    """
    result = random.choice(num_lst)
    return result


def init_num_lst():
    """
    Only used for radnom_excluding_zero(num_lst). Creates a list of ints from -10 to 10 without zero in it.
    """
    num_lst = []
    for i in range(-10, 11):
        if i != 0:
            num_lst.append(i)
    return num_lst


def life_tracker(canvas, lives):
    """
    Creates a new lives left text with updated number.
    """
    lives_left = canvas.create_text(  # The actual obj on screen is lives_left
        CANVAS_WIDTH - 50,
        CANVAS_HEIGHT - 50,
        text=str(lives),
        font='Arial',
        font_size=30,
        color='black'
    )
    return lives_left


def update_lives(canvas, lives, lives_left):
    """
    Process results of losing a life. Replace canvas obj with updated one.
    """
    lives -= 1
    canvas.delete(lives_left)
    lives_left = life_tracker(canvas, lives)  # shape_102

    return lives, lives_left


def place_ball(canvas):
    """
    Create canvas obj for the ball at center.
    """
    x1, y1 = CANVAS_WIDTH / 2 - BALL_DIAMETER / 2, CANVAS_HEIGHT / 2 - BALL_DIAMETER / 2
    x2, y2 = x1 + BALL_DIAMETER, y1 + BALL_DIAMETER

    ball = canvas.create_oval(
        x1, y1, x2, y2
    )
    return ball


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
    for i in range(10):
        brick_left_x = 0
        brick_right_x = brick_left_x + BRICK_WIDTH
        brick_bottom_y = brick_top_y + BRICK_HEIGHT
        # Just going across one row here (only manipulating x values). New rows handled in lay_bricks.
        canvas.create_rectangle(
            brick_left_x + (BRICK_WIDTH + BRICK_GAP) * i,
            # refers to i because bricks are laid along x axis i number of times.
            brick_top_y,
            brick_right_x + (BRICK_WIDTH + BRICK_GAP) * i,
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
        brick_top_y = i * (BRICK_HEIGHT + BRICK_GAP)  # first instance of brick_top_y variable
        if i <= 1:
            lay_brick_row(canvas, brick_top_y, 'red')
        elif 2 <= i <= 3:
            lay_brick_row(canvas, brick_top_y, 'orange')
        elif 4 <= i <= 5:
            lay_brick_row(canvas, brick_top_y, 'yellow')
        elif 6 <= i <= 7:
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