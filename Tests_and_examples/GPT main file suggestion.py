from Classes import *

game_window = Window()
ball = Ball(game_window.canvas)
paddle = Paddle(game_window.canvas)


def main():
    initialize_bricks()
    update_lifeboard()
    game_window.root.bind('<Motion>', on_mouse_move)
    game_loop()
    game_window.root.mainloop()


def game_loop():
    if game_window.run:
        game_window.refresh_window()
        ball.move()
        check_collisions()
        update_lifeboard()
        game_window.root.after(16, game_loop)


def on_mouse_move(event):
    paddle.move_to(event.x)


def update_lifeboard():
    game_window.canvas.delete('lifeboard')
    game_window.canvas.create_text(
        game_window.CANVAS_WIDTH - 60,
        20,
        font=('Arial', 20),
        text=f'Lives: {GameState.lives_left}',
        fill='white',
        tags='lifeboard'
    )


def initialize_bricks():
    rows = 5
    cols = 10
    width = 40
    height = 20
    padding = 5
    offset_y = 50

    colors = ['red', 'orange', 'yellow', 'green', 'cyan']

    for row in range(rows):
        for col in range(cols):
            x = col * (width + padding)
            y = offset_y + row * (height + padding)
            game_window.canvas.create_rectangle(
                x, y, x + width, y + height,
                fill=colors[row % len(colors)],
                tags='brick'
            )


def check_collisions():
    # Get ball's current position
    ball_coords = game_window.canvas.coords(ball.id)
    overlaps = game_window.canvas.find_overlapping(*ball_coords)

    for item in overlaps:
        tags = game_window.canvas.gettags(item)
        if 'brick' in tags:
            game_window.canvas.delete(item)
            ball.dy *= -1  # Reverse Y direction
            break
        elif 'paddle' in tags:
            ball.dy = -abs(ball.dy)  # Bounce up


if __name__ == '__main__':
    main()
