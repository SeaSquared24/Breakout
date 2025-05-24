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

And I FINALLY fixed the randomly speeding up issue. Turns out it was a performance issue caused by my being unaware of 
canvas' .itemconfig method. The program no longer drops frames due to canvas having to redraw both the life and countdown
timers every frame.
"""
class Game:
    def __init__(self):
        self.window = Window()
        self.canvas = self.window.canvas
        self.state = GameState(self.canvas) # GameState class initialized and assigned to state
        self.loop_running = False
        self._loop_id = None  # Track the scheduled callback ID

        self.ball = None
        self.paddle = None
        self.bricks = None

        self.state.display_menu()
        self.canvas.bind_all("<Return>", self.start_game)

    def start_game(self, event=None):
        if not self.state.play:
            self.state.play = True
            self.state.lives_left = 3 # reset counters
            self.state.num_bricks = 100
            self.canvas.delete("all")  # Clear old elements

            self.ball = Ball(self.canvas, game_state=self.state)
            self.paddle = Paddle(self.canvas)
            self.bricks = Bricks(self.canvas)

            self.loop_running = False
            self._loop_id = None  # Reset the callback ID
            self.loop()

    def loop(self):
        if self.window.run and self.state.play and not self.loop_running:
            self.loop_running = True
            self._loop_step()

    def _loop_step(self):
        if not self.state.play:
            self.loop_running = False
            return

        if self.state.debug:
            print("[LOOP] Ball velocity:", self.ball.movex, self.ball.movey)
            print("[LOOP] Ball object id:", self.ball.id)

        self.ball.collision_check()
        self.state.update_lifeboard()
        self.state.init_countdown()
        self.ball.move()

        if self.state.lives_left <= 0 or self.state.num_bricks <= 0:
            self.state.play = False
            self.state.lives_left = 3
            self.state.num_bricks = 100
            self.state.display_menu()
        else:
            if self._loop_id:
                self.window.root.after_cancel(self._loop_id)  # Cancel any existing callback
            self._loop_id = self.window.root.after(16, self._loop_step)  # Schedule the next callback

def main():
    game = Game()
    game.window.root.mainloop()

if __name__ == '__main__':
    main()
