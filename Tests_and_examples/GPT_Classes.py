import tkinter as tk
from tkinter import Canvas

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

class GameState:
    def __init__(self, canvas):
        self.canvas = canvas
        self.play = False
        self.lives_left = 3
        self.num_bricks = 100
        self.speed_multi = 1.0

    def display_menu(self):
        self.canvas.delete('all')
        self.canvas.create_text(
            Window.canvas_width / 2,
            Window.canvas_height / 2,
            anchor='center',
            font=('Arial', 30),
            text="Press Enter to Play",
            tags='menu'
        )

    def update_lifeboard(self):
        self.canvas.delete('lifeboard')
        self.canvas.create_text(
            Window.canvas_width - 60,
            20,
            font=('Arial', 20),
            text=f'Lives: {self.lives_left}',
            tags='lifeboard'
        )

    def update_spdmulti(self):
        self.speed_multi += 0.2

class Bricks:
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
                self.canvas.create_rectangle(
                    x, y, x + self.width, y + self.height,
                    fill=brick_color, outline='', tags='brick'
                )

class Ball:
    speed = 5
    def __init__(self, canvas, game_state=None):
        self.canvas = canvas
        self.game_state = game_state
        self.radius = 10
        self.x = 250
        self.y = 250
        self.dx = Ball.speed * self.game_state.speed_multi
        self.dy = Ball.speed * self.game_state.speed_multi
        self.id = self.canvas.create_oval(
            self.x - self.radius, self.y - self.radius,
            self.x + self.radius, self.y + self.radius,
            fill='blue', tags='ball'
        )

    def move(self):
        self.x += self.dx
        self.y += self.dy
        self.canvas.move(self.id, self.dx, self.dy)

        if self.x - self.radius <= 0 or self.x + self.radius >= self.canvas.winfo_width():
            self.dx *= -1
        elif self.y - self.radius <= Window.offset_y:
            self.dy *= -1
        elif self.y + self.radius >= self.canvas.winfo_height():
            if self.game_state:
                self.game_state.lives_left -= 1
                if self.game_state.lives_left <= 0:
                    self.game_state.play = False
            self.reset()

    def reset(self):
        self.x = self.canvas.winfo_width() // 2
        self.y = self.canvas.winfo_height() // 2
        self.dx = Ball.speed * self.game_state.speed_multi
        self.dy = Ball.speed * self.game_state.speed_multi
        self.canvas.coords(
            self.id,
            self.x - self.radius, self.y - self.radius,
            self.x + self.radius, self.y + self.radius
        )

    def update_speed(self):
        self.dx = Ball.speed * (1 if self.dx == 0 else (self.dx / abs(self.dx))) * self.game_state.speed_multi
        self.dy = Ball.speed * (1 if self.dy == 0 else (self.dy / abs(self.dy))) * self.game_state.speed_multi

    def collision_check(self):
        if not self.canvas.coords(self.id):
            return
        # coords and overlapping will be checked every time this function runs. bounced will always start as False.
        self.coords = self.canvas.coords(self.id)
        self.overlapping = self.canvas.find_overlapping(*self.coords)
        self.bounced = False

        for item in self.overlapping:
            self.item_tags = self.canvas.gettags(item)

            if "paddle" in self.item_tags and self.dy > 0:
                self.dy *= -1
                # TODO: paddle physics
            elif "brick" in self.item_tags:
                self.canvas.delete(item)
                if self.game_state:
                    self.game_state.num_bricks -= 1
                    if not self.bounced:
                        self.dy *= -1
                        self.bounced = True
                    if self.game_state.num_bricks % 10 == 0:
                        self.game_state.update_spdmulti()
                        self.update_speed()

class Paddle:
    def __init__(self, canvas):
        self.canvas = canvas
        self.width = 80
        self.height = 10
        self.speed = 15
        self.x = (canvas.winfo_width() / 2) - (self.width / 2)
        self.y = canvas.winfo_height() - 30
        self.id = canvas.create_rectangle(
            self.x, self.y,
            self.x + self.width, self.y + self.height,
            fill='black', tags='paddle'
        )
        self.canvas.bind_all("<Left>", self.move_left)
        self.canvas.bind_all("<Right>", self.move_right)

    def move_left(self, event):
        if self.canvas.coords(self.id)[0] > 0:
            self.canvas.move(self.id, -self.speed, 0)

    def move_right(self, event):
        if self.canvas.coords(self.id)[2] < self.canvas.winfo_width():
            self.canvas.move(self.id, self.speed, 0)
