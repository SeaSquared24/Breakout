from Classes import *

"""
This version of Breakout was designed to teach myself python Classes and how to create graphical programs outside
of the Code in Place IDE. I learned a lot about how tkinter canvas works in the real world and using .after instead of 
a time.sleep delay. Below are notes I made as I was making modifications. 

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

def main():
    game = Game()
    game.window.root.mainloop()

if __name__ == '__main__':
    main()
