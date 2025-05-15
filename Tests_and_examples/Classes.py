import tkinter as tk
from tkinter import Canvas
import time

class Window:
    canvas_width = 500
    canvas_height = 600
    offset_y = 60

    def __init__(self):
        self.run = True
        self.root = tk.Tk()
        self.root.title("Breakout")
        self.root.geometry(f"{self.canvas_width + 5}x{self.canvas_height + 5}")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.handler)

        self.canvas = Canvas(self.root, width=self.canvas_width, height=self.canvas_height, bg="white")
        self.canvas.pack()

    def handler(self):
        self.run = False
        self.root.destroy()

    def refresh_window(self):
        self.root.update_idletasks()
        self.root.update()
        time.sleep(GameState.delay)

class GameState():
    delay = 0.01
    lives_left = 3
    num_bricks = 100
    speed_multi = 1.0

    def __init__(self, canvas):
        self.canvas = canvas

    def update_lifeboard(self):
        self.canvas.delete('lifeboard')
        self.canvas.create_text(  # Create lifeboard
            Window.canvas_width - 60,
            20,
            font=('Arial', 20),
            text=f'Lives: {GameState.lives_left}',
            tags='lifeboard'
        )

    def update_spdmulti(self):
        self.speed_multi += 0.2

class Bricks():
    def __init__(self, canvas):
        self.canvas = canvas
        self.rows, self.cols = 10, 10
        self.padding = 5
        self.width = (Window.canvas_width - self.padding * 9) / 10
        self.height = 10

        for row in range(self.rows):
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
            for col in range(self.cols):
                x = col * (self.width + self.padding)
                y = Window.offset_y + row * (self.height + self.padding)
                self.canvas.create_rectangle(x, y, x + self.width, y + self.height, fill=brick_color,
                                                    outline='', tags='brick')

class Ball:
    # todo: randomize ball direction.
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
        elif self.y - self.radius <= Window.offset_y: # top wall
            self.dy *= -1
        elif self.y + self.radius >= self.canvas.winfo_height(): # bottom wall, lose a life and reset position
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
                # todo: add paddle physics
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