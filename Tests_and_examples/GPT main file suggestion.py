# game.py (Refactored)

from GPT_Classes import *

"""
Basically what I've learned here is that the Game class needs to initialize in order to have a state to pass into other
class methods, in this case, when initializing the ball so that ball.<methods> can update the game state and have access
to the current correct information.

There's also a difference in the way I have to update things such as the speed of the ball. In my original layout, I used 
a variable in main() that my update_ball_position() then referred to when using canvas.move. When I do this in a class
oriented way, however, I need to update this information in both the GameState class, and then in the instance of ball
to reflect the change. Otherwise, the ball doesn't check again on its own.
"""
class Game:
    def __init__(self):
        self.window = Window()
        self.canvas = self.window.canvas
        self.state = GameState(self.canvas)
        self.ball = Ball(self.canvas, game_state=self.state)
        self.paddle = Paddle(self.canvas)
        self.bricks = Bricks(self.canvas)

        self.state.display_menu()
        self.canvas.bind_all("<Return>", self.start_game)

    def start_game(self, event=None):
        GameState.play = True
        GameState.lives_left = 3
        GameState.num_bricks = 100
        self.canvas.delete("all")  # Clear old elements

        self.ball = Ball(self.canvas, game_state=self.state)
        self.paddle = Paddle(self.canvas)
        self.bricks = Bricks(self.canvas)
        self.loop()

    def loop(self):
        if self.window.run:
            if GameState.play:
                self.ball.move()
                self.ball.collision_check()
                self.state.update_lifeboard()
                if self.state.lives_left <= 0 or self.state.num_bricks <= 0:
                    GameState.play = False
                    self.state.lives_left = 3
                    self.state.num_bricks = 100
                    self.state.display_menu()
                else:
                    self.window.root.after(16, self.loop)

def main():
    game = Game()
    game.window.root.mainloop()

if __name__ == '__main__':
    main()
