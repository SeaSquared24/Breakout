"""
This is a test to figure out how to make an object follow the pointer.
It totally works.

Here's the function:

def update_ball_position(ball):
    x = window.winfo_pointerx()
    y = window.winfo_pointery()
    abs_coord_x = window.winfo_pointerx() - window.winfo_rootx()
    abs_coord_y = window.winfo_pointery() - window.winfo_rooty()
    canvas.coords(ball, abs_coord_x, abs_coord_y, abs_coord_x + BALL_DIAMETER, abs_coord_y + BALL_DIAMETER)
"""

import tkinter as tk
from tkinter import Canvas
import time

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

DELAY = 0.01

def main():
    global run
    run = True

    # Creating the window:
    global window
    window = tk.Tk()
    window.title("Breakout")
    window.geometry('500x600')
    window.resizable(False, False)
    window.protocol("WM_DELETE_WINDOW", handler)

    # Creating the canvas containing the game:
    global canvas
    canvas = Canvas(window, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg="white")
    canvas.pack()

    window.update()

    ball = init_ball()

    while run:
        refresh_window()

        update_ball_position(ball)

        time.sleep(DELAY)

    window.destroy()

def update_ball_position(ball):
    x = window.winfo_pointerx()
    y = window.winfo_pointery()
    abs_coord_x = window.winfo_pointerx() - window.winfo_rootx()
    abs_coord_y = window.winfo_pointery() - window.winfo_rooty()
    canvas.coords(ball, abs_coord_x, abs_coord_y, abs_coord_x + BALL_DIAMETER, abs_coord_y + BALL_DIAMETER)

def init_ball():
    ball = canvas.create_oval(CANVAS_WIDTH/2, CANVAS_HEIGHT/2, CANVAS_WIDTH/2 + BALL_DIAMETER, CANVAS_HEIGHT/2 + BALL_DIAMETER, fill="blue")
    return ball

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