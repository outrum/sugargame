#!/usr/bin/env python3
"""
Playable Pong-like game: Ball, paddle, scoring, game over, restart.
"""
import pygame

# Game constants
WIDTH, HEIGHT = 640, 480
BALL_RADIUS = 20
PADDLE_WIDTH, PADDLE_HEIGHT = 120, 16
PADDLE_SPEED = 10
BALL_SPEED_X, BALL_SPEED_Y = 6, -6
FONT_SIZE = 32

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Paddle Ball Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, FONT_SIZE)
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
        pygame.display.flip()

    def update(self):
        if self.game_over:
            return
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
        keys = pygame.key.get_pressed()
        if not self.game_over:
            if keys[pygame.K_LEFT]:
                self.paddle_x -= PADDLE_SPEED
            if keys[pygame.K_RIGHT]:
                self.paddle_x += PADDLE_SPEED
            self.paddle_x = max(0, min(WIDTH - PADDLE_WIDTH, self.paddle_x))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN and self.game_over:
                if event.key == pygame.K_r:
                    self.reset()
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
