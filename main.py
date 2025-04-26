#!/usr/bin/env python3
"""
Browser-compatible version of TestGame (no GTK/Sugar dependencies).
"""
import pygame

RADIUS = 100

class TestGame:
    def __init__(self):
        self.clock = pygame.time.Clock()
        self.x = -RADIUS
        self.y = RADIUS
        self.vx = RADIUS // 10
        self.vy = 0
        self.paused = False
        self.direction = 1

    def set_paused(self, paused):
        self.paused = paused

    def run(self):
        self.running = True
        screen = pygame.display.get_surface()
        width = screen.get_width()
        height = screen.get_height()
        dirty = []
        dirty.append(pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(0, 0, width, height)))
        pygame.display.update(dirty)
        while self.running:
            dirty = []
            # No GTK event pump for web build
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.VIDEORESIZE:
                    pygame.display.set_mode(event.size, pygame.RESIZABLE)
                    width = screen.get_width()
                    height = screen.get_height()
                    dirty.append(pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(0, 0, width, height)))
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.direction = -1
                    elif event.key == pygame.K_RIGHT:
                        self.direction = 1
            if not self.paused:
                dirty.append(pygame.draw.circle(screen, (255, 255, 255), (self.x, self.y), RADIUS))
                self.x += self.vx * self.direction
                if self.direction == 1 and self.x > width - RADIUS:
                    self.x = width - RADIUS
                    self.direction = -1
                elif self.direction == -1 and self.x < RADIUS:
                    self.x = RADIUS
                    self.direction = 1
                self.y += self.vy
                if self.y > height - RADIUS:
                    self.y = height - RADIUS
                    self.vy = -self.vy
                self.vy += 5
                dirty.append(pygame.draw.circle(screen, (192, 0, 0), (self.x, self.y), RADIUS))
            pygame.display.update(dirty)
            self.clock.tick(30)

def main():
    pygame.init()
    pygame.display.set_mode((640, 480), pygame.RESIZABLE)
    game = TestGame()
    game.run()

if __name__ == '__main__':
    main()
