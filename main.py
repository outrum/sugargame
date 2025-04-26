#!/usr/bin/env python3
"""
Mobile-first Tile Swap Puzzle: Classic, intuitive, and accessible for all ages.
- Tap two tiles to swap them and match the target pattern.
- Target pattern always visible as a preview.
- Unlimited moves (for accessibility).
"""
import pygame
import random

# --- CONFIG ---
COLORS = [(220,220,220), (255,0,0), (0,128,255), (0,200,0)]  # gray, red, blue, green
GRID_SIZE = 3
TILE_MARGIN = 8
FONT_SIZE = 36

LEVELS = [
    {"solution": [
        [1,2,3],
        [2,3,1],
        [3,1,2]
    ]},
    {"solution": [
        [2,1,2],
        [1,3,1],
        [2,1,2]
    ]},
    {"solution": [
        [3,3,1],
        [2,1,2],
        [1,2,3]
    ]},
]

class Tile:
    def __init__(self, row, col, value, size):
        self.row, self.col = row, col
        self.value = value
        self.size = size
    def rect(self, offset_x, offset_y):
        x = offset_x + self.col * (self.size + TILE_MARGIN)
        y = offset_y + self.row * (self.size + TILE_MARGIN)
        return pygame.Rect(x, y, self.size, self.size)
    def draw(self, screen, offset_x, offset_y, highlight=False):
        color = COLORS[self.value]
        pygame.draw.rect(screen, color, self.rect(offset_x, offset_y), border_radius=12)
        if highlight:
            pygame.draw.rect(screen, (255, 215, 0), self.rect(offset_x, offset_y), 4, border_radius=12)

class SwapPuzzleGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((400, 600))
        pygame.display.set_caption("Tile Swap Puzzle")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, FONT_SIZE)
        self.level = 0
        self.selected = None  # (row, col) of selected tile
        self.moves = 0
        self.solved = False
        self.reset()
    def reset(self):
        self.solution = [row[:] for row in LEVELS[self.level]["solution"]]
        # Flatten and shuffle to create a solvable puzzle
        flat = sum(self.solution, [])
        while True:
            random.shuffle(flat)
            grid = [flat[i*GRID_SIZE:(i+1)*GRID_SIZE] for i in range(GRID_SIZE)]
            if grid != self.solution:
                break
        self.grid = [[Tile(r, c, grid[r][c], self.tile_size()) for c in range(GRID_SIZE)] for r in range(GRID_SIZE)]
        self.selected = None
        self.moves = 0
        self.solved = False
    def tile_size(self):
        w, h = self.screen.get_size()
        size = min((w - (GRID_SIZE+1)*TILE_MARGIN)//GRID_SIZE, (h-200 - (GRID_SIZE+1)*TILE_MARGIN)//GRID_SIZE)
        return size
    def draw_pattern_preview(self, offset_x, offset_y, tile_size):
        preview_tile = tile_size // 3
        preview_offset_x = offset_x + tile_size*GRID_SIZE//2 - (preview_tile*GRID_SIZE)//2
        preview_offset_y = offset_y - preview_tile*GRID_SIZE - 20
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                color = COLORS[self.solution[r][c]]
                rect = pygame.Rect(
                    preview_offset_x + c*(preview_tile+2),
                    preview_offset_y + r*(preview_tile+2),
                    preview_tile, preview_tile)
                pygame.draw.rect(self.screen, color, rect, border_radius=6)
        label = self.font.render("Pattern", True, (80,80,80))
        self.screen.blit(label, (preview_offset_x, preview_offset_y-30))
    def draw(self):
        self.screen.fill((250,250,250))
        tile_size = self.tile_size()
        offset_x = (self.screen.get_width() - (tile_size*GRID_SIZE + TILE_MARGIN*(GRID_SIZE-1)))//2
        offset_y = 160
        self.draw_pattern_preview(offset_x, offset_y, tile_size)
        # Draw tiles
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                highlight = self.selected == (r, c)
                self.grid[r][c].size = tile_size
                self.grid[r][c].draw(self.screen, offset_x, offset_y, highlight=highlight)
        # Draw moves, level, instructions
        moves_surf = self.font.render(f"Moves: {self.moves}", True, (0,0,0))
        self.screen.blit(moves_surf, (20, 20))
        level_surf = self.font.render(f"Level: {self.level+1} of {len(LEVELS)}", True, (0,0,0))
        self.screen.blit(level_surf, (20, 60))
        instr = self.font.render("Tap two tiles to swap and match the pattern", True, (80,80,80))
        self.screen.blit(instr, (20, 100))
        restart_btn = self.font.render("Restart", True, (0,0,200))
        self.screen.blit(restart_btn, (250, 20))
        if self.solved:
            msg = self.font.render("Solved!", True, (0,180,0))
            self.screen.blit(msg, (120, 500))
            next_btn = self.font.render("Next", True, (0,0,200))
            self.screen.blit(next_btn, (250, 60))
        pygame.display.flip()
    def check_solution(self):
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if self.grid[r][c].value != self.solution[r][c]:
                    return False
        return True
    def handle_tap(self, pos):
        btn_rect = pygame.Rect(250, 20, 120, 40)
        next_btn_rect = pygame.Rect(250, 60, 120, 40)
        if btn_rect.collidepoint(pos):
            self.reset()
            return
        if next_btn_rect.collidepoint(pos) and self.solved:
            if self.level < len(LEVELS)-1:
                self.level += 1
                self.reset()
            else:
                self.level = 0
                self.reset()
            return
        if self.solved:
            return
        tile_size = self.tile_size()
        offset_x = (self.screen.get_width() - (tile_size*GRID_SIZE + TILE_MARGIN*(GRID_SIZE-1)))//2
        offset_y = 160
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if self.grid[r][c].rect(offset_x, offset_y).collidepoint(pos):
                    if self.selected is None:
                        self.selected = (r, c)
                    else:
                        r0, c0 = self.selected
                        # Swap values
                        self.grid[r0][c0].value, self.grid[r][c].value = self.grid[r][c].value, self.grid[r0][c0].value
                        self.selected = None
                        self.moves += 1
                        if self.check_solution():
                            self.solved = True
                    return
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
    SwapPuzzleGame().run()
