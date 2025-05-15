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
    speed_multi = 1.0

    def update_spdmulti(self):
        self.speed_multi += 0.2

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
        self.dy = 3
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
        if self.x - self.radius <= 0 or self.x + self.radius >= self.canvas.winfo_width(): # sides
            self.dx *= -1
        elif self.y - self.radius <= Bricks.offset_y: # top wall
            self.dy *= -1
        elif self.y + self.radius >= self.canvas.winfo_height(): # bottom wall, lose a life and reset position.
            GameState.lives_left -= 1
            self.reset()

    def reset(self):
        # Set to initial position (you can adjust these values as needed)
        self.x = self.canvas.winfo_width() // 2
        self.y = self.canvas.winfo_height() // 2
        self.dx = 3
        self.dy = 3

        # Move ball to new position
        self.canvas.coords(
            self.id,
            self.x - self.radius,
            self.y - self.radius,
            self.x + self.radius,
            self.y + self.radius
        )

    def collision_check(self):
        ball_coords = self.canvas.coords(self.id)
        if not ball_coords: # check that ball exists
            return
        overlapping = self.canvas.find_overlapping(*ball_coords)
        bounced = False

        for item in overlapping:
            if "paddle" in self.canvas.gettags(item) and self.dy > 0: # if ball touches paddle
                self.dy *= -1
            elif "brick" in self.canvas.gettags(item):
                self.canvas.delete(item)
                GameState.num_bricks -= 1
                if bounced == False:  # only bounce once if hitting two at the same time.
                    bounced = True
                    self.dy *= -1 # bounce
                if GameState.num_bricks % 10 == 0:  # num_bricks has already gone down so it shouldn't trigger on 100 bricks.
                    GameState.update_spdmulti()

class Paddle:
    def __init__(self, canvas):
        self.canvas = canvas
        self.width = 80
        self.height = 10
        self.speed = 10  # Pixels per key press
        self.x = (canvas.winfo_width() / 2) - (self.width / 2)
        self.y = canvas.winfo_height() - 30
        self.id = canvas.create_rectangle(
            self.x, self.y,
            self.x + self.width, self.y + self.height,
            fill='black', tags='paddle'
        )

        # Bind key events
        self.canvas.bind_all("<Left>", self.move_left)
        self.canvas.bind_all("<Right>", self.move_right)

    def move_left(self, event):
        if self.canvas.coords(self.id)[0] > 0:
            self.canvas.move(self.id, -self.speed, 0)

    def move_right(self, event):
        if self.canvas.coords(self.id)[2] < self.canvas.winfo_width():
            self.canvas.move(self.id, self.speed, 0)