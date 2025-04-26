#!/usr/bin/env python3
"""
Playable Paddle-Ball Game: Ball, paddle, scoring, game over, restart.
- Paddle can be controlled by mouse, keyboard, and on-screen buttons (for Replit).
"""
import pygame

# Game constants
WIDTH, HEIGHT = 640, 480
BALL_RADIUS = 20
PADDLE_WIDTH, PADDLE_HEIGHT = 120, 16
PADDLE_SPEED = 10
BALL_SPEED_X, BALL_SPEED_Y = 6, -6
FONT_SIZE = 32
BUTTON_WIDTH, BUTTON_HEIGHT = 60, 40
BUTTON_Y = HEIGHT - BUTTON_HEIGHT - 60

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Paddle Ball Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, FONT_SIZE)
        self.left_button = pygame.Rect(30, BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT)
        self.right_button = pygame.Rect(WIDTH-30-BUTTON_WIDTH, BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT)
        self.left_held = False
        self.right_held = False
        self.reset()

    def reset(self):
        self.ball_x = WIDTH // 2
        self.ball_y = HEIGHT // 2
        self.ball_vx = BALL_SPEED_X
        self.ball_vy = BALL_SPEED_Y
        self.paddle_x = WIDTH // 2 - PADDLE_WIDTH // 2
        self.score = 0
        self.game_over = False

    def draw(self):
        self.screen.fill((255, 255, 255))
        # Draw ball
        pygame.draw.circle(self.screen, (192, 0, 0), (int(self.ball_x), int(self.ball_y)), BALL_RADIUS)
        # Draw paddle
        pygame.draw.rect(self.screen, (0, 0, 192), (self.paddle_x, HEIGHT - PADDLE_HEIGHT - 10, PADDLE_WIDTH, PADDLE_HEIGHT))
        # Draw score
        score_surf = self.font.render(f"Score: {self.score}", True, (0, 0, 0))
        self.screen.blit(score_surf, (10, 10))
        # Draw game over
        if self.game_over:
            over_surf = self.font.render("GAME OVER! Press R to restart", True, (255, 0, 0))
            rect = over_surf.get_rect(center=(WIDTH//2, HEIGHT//2))
            self.screen.blit(over_surf, rect)
        # Draw on-screen buttons
        pygame.draw.rect(self.screen, (200, 200, 200), self.left_button)
        pygame.draw.rect(self.screen, (200, 200, 200), self.right_button)
        left_surf = self.font.render("<", True, (0, 0, 0))
        right_surf = self.font.render(">", True, (0, 0, 0))
        self.screen.blit(left_surf, self.left_button.move(18, 2))
        self.screen.blit(right_surf, self.right_button.move(18, 2))
        pygame.display.flip()

    def update(self):
        if self.game_over:
            return
        # Move paddle by keyboard or on-screen button
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or self.left_held:
            self.paddle_x -= PADDLE_SPEED
        if keys[pygame.K_RIGHT] or self.right_held:
            self.paddle_x += PADDLE_SPEED
        # Move paddle by mouse
        mouse_x, _ = pygame.mouse.get_pos()
        if pygame.mouse.get_focused():
            self.paddle_x = mouse_x - PADDLE_WIDTH // 2
        self.paddle_x = max(0, min(WIDTH - PADDLE_WIDTH, self.paddle_x))
        # Move ball
        self.ball_x += self.ball_vx
        self.ball_y += self.ball_vy
        # Wall collision
        if self.ball_x < BALL_RADIUS or self.ball_x > WIDTH - BALL_RADIUS:
            self.ball_vx *= -1
        if self.ball_y < BALL_RADIUS:
            self.ball_vy *= -1
        # Paddle collision
        paddle_rect = pygame.Rect(self.paddle_x, HEIGHT - PADDLE_HEIGHT - 10, PADDLE_WIDTH, PADDLE_HEIGHT)
        ball_rect = pygame.Rect(self.ball_x - BALL_RADIUS, self.ball_y - BALL_RADIUS, BALL_RADIUS*2, BALL_RADIUS*2)
        if ball_rect.colliderect(paddle_rect) and self.ball_vy > 0:
            self.ball_vy *= -1
            self.score += 1
        # Missed paddle
        if self.ball_y > HEIGHT:
            self.game_over = True

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN and self.game_over:
                if event.key == pygame.K_r:
                    self.reset()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.left_button.collidepoint(event.pos):
                    self.left_held = True
                if self.right_button.collidepoint(event.pos):
                    self.right_held = True
            if event.type == pygame.MOUSEBUTTONUP:
                if self.left_held:
                    self.left_held = False
                if self.right_held:
                    self.right_held = False
        return True

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)

if __name__ == '__main__':
    Game().run()
