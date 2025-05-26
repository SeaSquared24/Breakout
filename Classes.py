import tkinter as tk
from tkinter import Canvas
import random

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
        self.debug = False
        self.canvas = canvas
        self.play = False
        self.lives_left = 3
        self.num_bricks = 100
        self.cntdwn = self.num_bricks % 10
        self.speed_multi = 1.0

    def display_debug(self):
        if self.debug:
            print("")
            print("[GAMESTATE] Lives", self.lives_left)
            print("[GAMESTATE] Bricks", self.num_bricks)
            print("[GAMESTATE] Countdown", self.cntdwn)
            print("[GAMESTATE] Speed multi", self.speed_multi)
            print("")

    def display_menu(self):
        self.canvas.delete('all')
        self.canvas.create_text(
            Window.canvas_width / 2,
            Window.canvas_height / 2,
            anchor='center',
            justify='center',
            font=('Arial', 30),
            text=self.determine_menu(),
            tags='menu'
        )

    def determine_menu(self):
        dead = self.lives_left == 0
        winner = self.num_bricks == 0
        if dead:
            return "Oh no! You lost.\nPress Enter to Play Again."
        elif winner:
            return "Congrats!\nPress Enter to Play Again."
        else:
            return "Press Enter to Play."

    def update_lifeboard(self):
        if not self.canvas.find_withtag('lifeboard'):
            self.lifeboard_id = self.canvas.create_text(
                Window.canvas_width - 60,
                20,
                font=('Arial', 20),
                text=f'Lives: {self.lives_left}',
                tags='lifeboard'
            )
        else:
            self.canvas.itemconfig(self.lifeboard_id, text=f'Lives: {self.lives_left}')

    def init_countdown(self):
        if 0 < self.cntdwn < 4:
            if not self.canvas.find_withtag('countdown'):
                self.countdown_id = self.canvas.create_text(
                    0,
                    20,
                    font=('Arial', 20),
                    anchor='w',
                    text=f'Speedup in {self.cntdwn} bricks!',
                    tags='countdown'
                )
            else:
                self.canvas.itemconfig(self.countdown_id, text=f'Speedup in {self.cntdwn} bricks!')
        else:
            if self.canvas.find_withtag('countdown'):
                self.canvas.delete('countdown')

    def handle_brick_break(self):
        self.num_bricks -= 1
        self.cntdwn = self.num_bricks % 10
        self.init_countdown()

        if self.cntdwn == 0:
            self.update_spdmulti()

        if self.debug:
            print("[HANDLE BRICK BREAK] Countdown is", self.cntdwn)
            print("[HANDLE BRICK BREAK] Speed Multi is", self.speed_multi)

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
                brick_color = 'indigo'
            elif 2 <= row <= 3:
                brick_color = 'blue'
            elif 4 <= row <= 5:
                brick_color = 'teal'
            elif 6 <= row <= 7:
                brick_color = 'cyan'
            elif row >= 8:
                brick_color = 'lightblue'

            for col in range(self.cols):
                x = col * (self.width + self.padding)
                y = Window.offset_y + row * (self.height + self.padding)
                self.canvas.create_rectangle(
                    x, y, x + self.width, y + self.height,
                    fill=brick_color, outline='', tags='brick'
                )

class Ball:
    speed = 3
    def __init__(self, canvas, game_state=None):
        # Basic Info
        self.canvas = canvas
        self.game_state = game_state
        self.radius = 10
        # Starting point. Centered.
        self.x = Window.canvas_width / 2
        self.y = Window.canvas_height / 2 + Window.offset_y
        # Direction(+/- y), speed(Ball.speed) and angle(x).
        self.dx = self.random_dx() # randomly chosen angle
        self.dy = Ball.speed # start positive, always go down.
        # Velocity multiplied by speed_multi which cranks up every ten bricks.
        self.movex = self.dx * self.game_state.speed_multi
        self.movey = self.dy * self.game_state.speed_multi
        # Create ball.
        self.id = self.canvas.create_oval(
            self.x - self.radius, self.y - self.radius,
            self.x + self.radius, self.y + self.radius,
            fill='blue', tags='ball'
        )

    def update_movement(self):
        self.movex = self.dx * self.game_state.speed_multi
        self.movey = self.dy * self.game_state.speed_multi

    def move(self):
        self.update_movement() # Ensure correct velocity is passed to self.canvas.move
        self.canvas.move(self.id, self.movex, self.movey)
        self.velocity_debug()
        coords = self.canvas.coords(self.id)

        if coords[0] <= 0 or coords[2] >= self.canvas.winfo_width(): # sides
            self.dx *= -1
        elif coords[1] <= Window.offset_y: # top
            self.dy *= -1
        elif coords[3] >= self.canvas.winfo_height(): # bottom
            if self.game_state:
                self.game_state.lives_left -= 1
                if self.game_state.lives_left <= 0:
                    self.game_state.play = False
            self.reset()

    def velocity_debug(self):
        if self.game_state.debug:
            print(f"[BALL.MOVE] velocity is ({self.movex}, {self.movey})")

    def random_dx(self):
        choice = random.choice([i for i in range(-3, 4) if i != 0])
        if self.game_state.debug:
            print("[RANDOM DX]:", choice)
        return choice

    def reset(self):
        self.dx = self.random_dx()
        self.x = Window.canvas_width / 2
        self.y = Window.canvas_height / 2 + Window.offset_y
        self.canvas.coords(
            self.id,
            self.x - self.radius, self.y - self.radius,
            self.x + self.radius, self.y + self.radius
        )

    def collision_check(self):
        coords = self.canvas.coords(self.id)
        overlapping = self.canvas.find_overlapping(*coords)
        bounced = False

        paddle = self.canvas.find_withtag('paddle')
        p_coords = self.canvas.coords(paddle)

        for item in overlapping:
            tags = self.canvas.gettags(item)

            if 'paddle' in tags and self.dy > 0:
                self.dy = -self.dy
                # Side paddle bounce logic
                if coords[0] > p_coords[2] - 20 and self.dx < 0:
                    self.dx = -self.dx
                elif coords[2] < p_coords[0] + 20 and self.dx > 0:
                    self.dx = -self.dx

            elif 'brick' in tags:
                self.canvas.delete(item)
                if not bounced:
                    self.dy = -self.dy
                    bounced = True
                    self.game_state.handle_brick_break()

                if self.game_state.debug:
                    self.game_state.display_debug()
                    print("")
                    print(f"[COLLISION CHECK] Overlapping {overlapping} ")
                    print(f"[COLLISION CHECK] Direction ({self.dx, self.dy})")
                    print(f"[COLLISION CHECK] velocity is ({self.movex}, {self.movey})")
                    print("")

class Paddle:
    def __init__(self, canvas, game_state=None):
        self.canvas = canvas
        self.game_state = game_state
        self.width = 80
        self.height = 10
        self.speed = 3
        self.dx = 0

        self.x = (canvas.winfo_width() / 2) - (self.width / 2)
        self.y = canvas.winfo_height() - 30

        self.id = canvas.create_rectangle(
            self.x, self.y,
            self.x + self.width, self.y + self.height,
            fill='black', tags='paddle'
        )

        # Track currently pressed keys
        self.keys_held = set()

        # Bind key events
        self.canvas.bind_all("<KeyPress-Left>", self.key_down)
        self.canvas.bind_all("<KeyPress-Right>", self.key_down)
        self.canvas.bind_all("<KeyRelease-Left>", self.key_up)
        self.canvas.bind_all("<KeyRelease-Right>", self.key_up)

    def key_down(self, event):
        self.keys_held.add(event.keysym)
        self.update_direction()

    def key_up(self, event):
        self.keys_held.discard(event.keysym)
        self.update_direction()

    def update_direction(self):
        # Determine direction based on the last key still held
        if 'Right' in self.keys_held and 'Left' not in self.keys_held:
            self.dx = self.speed
        elif 'Left' in self.keys_held and 'Right' not in self.keys_held:
            self.dx = -self.speed
        else:
            self.dx = 0

    def draw(self):
        x1, y1, x2, y2 = self.canvas.coords(self.id)
        canvas_width = self.canvas.winfo_width()

        if x1 + self.dx < 0:
            self.canvas.move(self.id, -x1, 0)
        elif x2 + self.dx > canvas_width:
            self.canvas.move(self.id, canvas_width - x2, 0)
        else:
            self.canvas.move(self.id, self.dx, 0)


