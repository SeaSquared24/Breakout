class GameState:
    def __init__(self):
        # Paddle state
        self.paddle_x = 300
        self.paddle_width = 100

        # Ball state
        self.ball_x = 350
        self.ball_y = 250
        self.ball_dx = 4
        self.ball_dy = -4
        self.ball_radius = 10

        # Bricks: list of (x, y, width, height)
        self.bricks = self.initialize_bricks()

        # Game state
        self.score = 0
        self.lives = 3
        self.is_game_over = False
        self.is_paused = False

    def initialize_bricks(self):
        bricks = []
        rows, cols = 5, 10
        brick_width = 60
        brick_height = 20
        padding = 10
        offset_x = 35
        offset_y = 60

        for row in range(rows):
            for col in range(cols):
                x = offset_x + col * (brick_width + padding)
                y = offset_y + row * (brick_height + padding)
                bricks.append((x, y, brick_width, brick_height))
        return bricks

game_state = GameState()

# Move paddle
game_state.paddle_x += 5

# Update ball
game_state.ball_x += game_state.ball_dx
game_state.ball_y += game_state.ball_dy
