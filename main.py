#!/usr/bin/env python3
"""
Mobile-first IQ Puzzle Game: Multi-level, feedback, animation, progress tracker. Sound optional.
"""
import pygame
import time

# --- CONFIG ---
COLORS = [(220,220,220), (255,0,0), (0,128,255), (0,200,0)]  # gray, red, blue, green
GRID_SIZE = 3
TILE_MARGIN = 8
FONT_SIZE = 36
ANIMATION_FRAMES = 6

LEVELS = [
    {"solution": [
        [1,2,3],
        [2,3,1],
        [3,1,2]
    ], "moves": 7},
    {"solution": [
        [2,1,2],
        [1,3,1],
        [2,1,2]
    ], "moves": 6},
    {"solution": [
        [3,3,1],
        [2,1,2],
        [1,2,3]
    ], "moves": 8},
]

# --- SOUND ---
def load_sound(path):
    try:
        return pygame.mixer.Sound(path)
    except Exception:
        return None

class Tile:
    def __init__(self, row, col, size):
        self.row, self.col = row, col
        self.size = size
        self.value = 0  # Start as gray
        self.animating = False
        self.anim_frame = 0
        self.last_state = 0
    def rect(self, offset_x, offset_y):
        x = offset_x + self.col * (self.size + TILE_MARGIN)
        y = offset_y + self.row * (self.size + TILE_MARGIN)
        return pygame.Rect(x, y, self.size, self.size)
    def draw(self, screen, offset_x, offset_y, highlight=None):
        base_color = COLORS[self.value]
        color = base_color
        # Animate color flash
        if self.animating and self.anim_frame < ANIMATION_FRAMES:
            color = tuple(min(255, x+50) for x in base_color)
        # Highlight
        if highlight == 'correct':
            color = (120, 255, 120)
        elif highlight == 'incorrect':
            color = (255, 120, 120)
        pygame.draw.rect(screen, color, self.rect(offset_x, offset_y), border_radius=12)
    def animate(self):
        if self.animating:
            self.anim_frame += 1
            if self.anim_frame >= ANIMATION_FRAMES:
                self.animating = False
                self.anim_frame = 0

class PuzzleGame:
    def __init__(self):
        pygame.init()
        # DO NOT call pygame.mixer.init() to avoid errors on cloud/virtual environments
        self.screen = pygame.display.set_mode((400, 600))
        pygame.display.set_caption("IQ Puzzle Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, FONT_SIZE)
        self.level = 0
        self.showing_solution = False
        # Sounds (optional)
        try:
            self.tap_sound = load_sound("tap.wav")
            self.win_sound = load_sound("win.wav")
            self.fail_sound = load_sound("fail.wav")
        except Exception:
            self.tap_sound = self.win_sound = self.fail_sound = None
        self.last_tap = (-1, -1)
        self.last_feedback = None
        self.reset()
    def reset(self):
        level_data = LEVELS[self.level]
        self.moves = level_data["moves"]
        self.solution = level_data["solution"]
        self.grid = [[Tile(r, c, self.tile_size()) for c in range(GRID_SIZE)] for r in range(GRID_SIZE)]
        self.solved = False
        self.failed = False
        self.showing_solution = False
        self.last_tap = (-1, -1)
        self.last_feedback = None
    def tile_size(self):
        w, h = self.screen.get_size()
        size = min((w - (GRID_SIZE+1)*TILE_MARGIN)//GRID_SIZE, (h-200 - (GRID_SIZE+1)*TILE_MARGIN)//GRID_SIZE)
        return size
    def draw(self):
        self.screen.fill((250,250,250))
        tile_size = self.tile_size()
        offset_x = (self.screen.get_width() - (tile_size*GRID_SIZE + TILE_MARGIN*(GRID_SIZE-1)))//2
        offset_y = 120
        # Draw tiles with feedback
        for r, row in enumerate(self.grid):
            for c, tile in enumerate(row):
                tile.size = tile_size
                highlight = None
                if self.last_tap == (r,c) and self.last_feedback:
                    highlight = self.last_feedback
                tile.draw(self.screen, offset_x, offset_y, highlight=highlight)
        # Animate
        for row in self.grid:
            for tile in row:
                tile.animate()
        # Draw moves left, level, progress
        moves_surf = self.font.render(f"Moves: {self.moves}", True, (0,0,0))
        self.screen.blit(moves_surf, (20, 20))
        level_surf = self.font.render(f"Level: {self.level+1} of {len(LEVELS)}", True, (0,0,0))
        self.screen.blit(level_surf, (20, 60))
        # Draw instructions
        instr = self.font.render("Tap tiles to match pattern", True, (80,80,80))
        self.screen.blit(instr, (20, 100))
        # Draw result and buttons
        if self.solved:
            msg = self.font.render("Solved! ", True, (0,180,0))
            self.screen.blit(msg, (100, 500))
            next_btn = self.font.render("Next", True, (0,0,200))
            self.screen.blit(next_btn, (250, 20))
        elif self.failed:
            msg = self.font.render("Out of moves!", True, (200,0,0))
            self.screen.blit(msg, (100, 500))
            restart_btn = self.font.render("Restart", True, (0,0,200))
            self.screen.blit(restart_btn, (250, 20))
            sol_btn = self.font.render("Show Solution", True, (150,80,0))
            self.screen.blit(sol_btn, (120, 550))
        else:
            restart_btn = self.font.render("Restart", True, (0,0,200))
            self.screen.blit(restart_btn, (250, 20))
            sol_btn = self.font.render("Show Solution", True, (150,80,0))
            self.screen.blit(sol_btn, (120, 550))
        # Draw solution overlay if needed
        if self.showing_solution:
            surf = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
            surf.fill((255,255,255,220))
            for r in range(GRID_SIZE):
                for c in range(GRID_SIZE):
                    color = COLORS[self.solution[r][c]]
                    rect = pygame.Rect(
                        offset_x + c*(tile_size+TILE_MARGIN),
                        offset_y + r*(tile_size+TILE_MARGIN),
                        tile_size, tile_size)
                    pygame.draw.rect(surf, color, rect, border_radius=12)
            self.screen.blit(surf, (0,0))
            label = self.font.render("Solution", True, (150,80,0))
            self.screen.blit(label, (140, 40))
        pygame.display.flip()
    def check_solution(self):
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if self.grid[r][c].value != self.solution[r][c]:
                    return False
        return True
    def handle_tap(self, pos):
        if self.solved:
            btn_rect = pygame.Rect(250, 20, 120, 40)
            if btn_rect.collidepoint(pos):
                if self.level < len(LEVELS)-1:
                    self.level += 1
                    self.reset()
                else:
                    self.level = 0
                    self.reset()
            return
        if self.failed:
            btn_rect = pygame.Rect(250, 20, 120, 40)
            if btn_rect.collidepoint(pos):
                self.reset()
                return
            sol_btn_rect = pygame.Rect(120, 550, 200, 40)
            if sol_btn_rect.collidepoint(pos):
                self.showing_solution = not self.showing_solution
                if self.fail_sound: self.fail_sound.play()
                return
        if self.showing_solution:
            self.showing_solution = False
            return
        # Normal play
        tile_size = self.tile_size()
        offset_x = (self.screen.get_width() - (tile_size*GRID_SIZE + TILE_MARGIN*(GRID_SIZE-1)))//2
        offset_y = 120
        for r, row in enumerate(self.grid):
            for c, tile in enumerate(row):
                if tile.rect(offset_x, offset_y).collidepoint(pos):
                    tile.value = (tile.value + 1) % len(COLORS)
                    tile.animating = True
                    tile.anim_frame = 0
                    self.last_tap = (r, c)
                    if tile.value == self.solution[r][c]:
                        self.last_feedback = 'correct'
                    else:
                        self.last_feedback = 'incorrect'
                    if self.tap_sound: self.tap_sound.play()
                    if not self.solved and not self.failed:
                        self.moves -= 1
                        if self.check_solution():
                            self.solved = True
                            if self.win_sound: self.win_sound.play()
                        elif self.moves == 0:
                            self.failed = True
                            if self.fail_sound: self.fail_sound.play()
                    return
        btn_rect = pygame.Rect(250, 20, 120, 40)
        if btn_rect.collidepoint(pos):
            self.reset()
        sol_btn_rect = pygame.Rect(120, 550, 200, 40)
        if sol_btn_rect.collidepoint(pos):
            self.showing_solution = not self.showing_solution
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_tap(event.pos)
            self.draw()
            self.clock.tick(60)

if __name__ == '__main__':
    PuzzleGame().run()
