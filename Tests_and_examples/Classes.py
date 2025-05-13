import tkinter as tk
from tkinter import Canvas
import time

class Window:
    CANVAS_WIDTH = 500
    CANVAS_HEIGHT = 600

    def __init__(self):
        self.run = True
        self.root = tk.Tk()
        self.root.title("Breakout")
        self.root.geometry(f"{self.CANVAS_WIDTH + 5}x{self.CANVAS_HEIGHT + 5}")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.handler)

        self.canvas = Canvas(self.root, width=self.CANVAS_WIDTH, height=self.CANVAS_HEIGHT, bg="white")
        self.canvas.pack()

    def handler(self):
        self.run = False
        self.root.destroy()

    def refresh_window(self):
        self.root.update_idletasks()
        self.root.update()
        time.sleep(GameState.delay)

class GameState(Window):
    delay = 0.01
    lives_left = 3
    num_bricks = 100

class Bricks(Window):
    rows, cols = 10, 10
    padding = 5
    width = (Window.CANVAS_WIDTH - padding * 9) / 10
    height = 10
    offset_y = 60

class Ball:
    def __init__(self, canvas):
        self.canvas = canvas
        self.radius = 10
        self.x = 250
        self.y = 250
        self.dx = 3
        self.dy = -3
        self.id = canvas.create_oval(
            self.x - self.radius, self.y - self.radius,
            self.x + self.radius, self.y + self.radius,
            fill='blue', tags='ball'
        )

    def move(self):
        self.x += self.dx
        self.y += self.dy
        self.canvas.move(self.id, self.dx, self.dy)

        # Bounce off walls
        if self.x - self.radius <= 0 or self.x + self.radius >= self.canvas.winfo_width():
            self.dx *= -1
        if self.y - self.radius <= Bricks.offset_y:
            self.dy *= -1
        if self.y + self.radius >= self.canvas.winfo_height():
            GameState.lives_left -= 1
            self.canvas.delete(self.id)


class Paddle:
    def __init__(self, canvas):
        self.canvas = canvas
        self.width = 80
        self.height = 10
        self.x = (canvas.winfo_width() / 2) - (self.width / 2)
        self.y = canvas.winfo_height() - 30
        self.id = canvas.create_rectangle(
            self.x, self.y,
            self.x + self.width, self.y + self.height,
            fill='black', tags='paddle'
        )

    def move_to(self, x):
        new_x = x - self.width / 2
        dx = new_x - self.x
        self.canvas.move(self.id, dx, 0)
        self.x = new_x
