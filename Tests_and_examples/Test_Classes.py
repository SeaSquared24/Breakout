from Classes import *

game_window = Window()
game_window.refresh_window()
ball = Ball(game_window.canvas)
paddle = Paddle(game_window.canvas)

def main():
    initialize_bricks()
    update_lifeboard()
    game_loop()  # Start the repeating loop
    game_window.root.mainloop()  # Start the Tkinter event loop

def game_loop(): # todo: add loop for game ends logic. work on menu screen.
    if game_window.run:
        game_window.refresh_window()
        ball.move()
        ball.collision_check()
        update_lifeboard()
        game_window.root.after(16, game_loop)  # Call this function again after ~16 ms (~60 FPS)

def update_lifeboard():
    game_window.canvas.delete('lifeboard')
    game_window.canvas.create_text( # Create lifeboard
        game_window.CANVAS_WIDTH - 60,
        20,
        font=('Arial', 20),
        text=f'Lives: {GameState.lives_left}',
        tags='lifeboard'
    )

def initialize_bricks():
    for row in range(Bricks.rows):
        if row <= 1:
            brick_color = 'red'
        elif 2 <= row <= 3:
            brick_color = 'orange'
        elif 4 <= row <= 5:
            brick_color = 'yellow'
        elif 6 <= row <= 7:
            brick_color = 'lime'
        elif row >= 8:
            brick_color = 'cyan'
        for col in range(Bricks.cols):
            x = col * (Bricks.width + Bricks.padding)
            y = Bricks.offset_y + row * (Bricks.height + Bricks.padding)
            game_window.canvas.create_rectangle(x, y, x + Bricks.width, y + Bricks.height, fill=brick_color, outline='', tags='brick')

if __name__ == '__main__':
    main()