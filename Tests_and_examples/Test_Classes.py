from Classes import *

game_window = Window()
game_state = GameState(game_window.canvas)
game_window.refresh_window()
ball = Ball(game_window.canvas)
paddle = Paddle(game_window.canvas)
bricks = Bricks(game_window.canvas)
game_state.update_lifeboard()

def main():
    game_loop()  # Start the repeating loop
    game_window.root.mainloop()  # Start the Tkinter event loop

def game_loop(): # todo: add loop for game ends logic. work on menu screen.
    if game_window.run:
        if GameState.num_bricks > 0 and GameState.lives_left > 0:
            game_window.refresh_window()
            ball.move()
            ball.collision_check()
            game_state.update_lifeboard()
            game_window.root.after(16, game_loop)  # Call this function again after ~16 ms (~60 FPS)


if __name__ == '__main__':
    main()