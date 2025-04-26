#!/usr/bin/env python3
"""
Tile Swap Puzzle — Modern, Mobile-First UI
- Improved layout, padding, colors, and button design
- Animated tile swap feedback and clear pattern preview card
- Responsive for mobile and desktop
"""
import pygame
import random

# --- CONFIG ---
COLORS = [(230,230,230), (255,87,87), (66,135,245), (90,210,90)]  # bg, red, blue, green
TILE_COLORS = COLORS[1:]
BG_COLOR = (245, 245, 250)
PATTERN_CARD = (255,255,255)
PATTERN_SHADOW = (210,210,220)
TILE_SHADOW = (180,180,200)
FONT_COLOR = (40,40,60)
BUTTON_COLOR = (66,135,245)
BUTTON_TEXT = (255,255,255)
BUTTON_HOVER = (44, 105, 200)
SELECTED_BORDER = (255, 215, 0)
GRID_SIZE = 3
TILE_MARGIN = 12
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
        self.anim = 0  # Animation frame for swap
    def rect(self, offset_x, offset_y):
        x = offset_x + self.col * (self.size + TILE_MARGIN)
        y = offset_y + self.row * (self.size + TILE_MARGIN)
        return pygame.Rect(x, y, self.size, self.size)
    def draw(self, screen, offset_x, offset_y, highlight=False):
        rect = self.rect(offset_x, offset_y)
        # Shadow
        shadow_rect = rect.move(4, 6)
        pygame.draw.rect(screen, TILE_SHADOW, shadow_rect, border_radius=18)
        color = TILE_COLORS[self.value-1]
        pygame.draw.rect(screen, color, rect, border_radius=18)
        if highlight:
            pygame.draw.rect(screen, SELECTED_BORDER, rect, 6, border_radius=18)
        if self.anim > 0:
            pygame.draw.rect(screen, (255,255,255,100), rect, border_radius=18)
    def animate_swap(self):
        if self.anim > 0:
            self.anim -= 1

class Button:
    def __init__(self, rect, text):
        self.rect = rect
        self.text = text
        self.hover = False
    def draw(self, screen, font):
        color = BUTTON_HOVER if self.hover else BUTTON_COLOR
        pygame.draw.rect(screen, color, self.rect, border_radius=18)
        label = font.render(self.text, True, BUTTON_TEXT)
        label_rect = label.get_rect(center=self.rect.center)
        screen.blit(label, label_rect)
    def check_hover(self, pos):
        self.hover = self.rect.collidepoint(pos)
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

class SwapPuzzleGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((430, 700))
        pygame.display.set_caption("Tile Swap Puzzle")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, FONT_SIZE, bold=True)
        self.small_font = pygame.font.SysFont(None, 26)
        self.level = 0
        self.selected = None  # (row, col) of selected tile
        self.moves = 0
        self.solved = False
        self.animating = False
        self.reset()
        # Buttons
        self.restart_btn = Button(pygame.Rect(50, 620, 140, 48), "Restart")
        self.next_btn = Button(pygame.Rect(240, 620, 140, 48), "Next")
    def reset(self):
        self.solution = [row[:] for row in LEVELS[self.level]["solution"]]
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
        self.animating = False
    def tile_size(self):
        w, h = self.screen.get_size()
        size = min((w - (GRID_SIZE+1)*TILE_MARGIN)//GRID_SIZE, (h-360 - (GRID_SIZE+1)*TILE_MARGIN)//GRID_SIZE)
        return size
    def draw_pattern_card(self, offset_x, offset_y, tile_size):
        preview_tile = tile_size // 3
        card_w = preview_tile*GRID_SIZE + 24
        card_h = preview_tile*GRID_SIZE + 40
        card_x = offset_x + tile_size*GRID_SIZE//2 - card_w//2
        card_y = offset_y - card_h - 16
        # Shadow
        pygame.draw.rect(self.screen, PATTERN_SHADOW, (card_x+4, card_y+6, card_w, card_h), border_radius=18)
        # Card
        pygame.draw.rect(self.screen, PATTERN_CARD, (card_x, card_y, card_w, card_h), border_radius=18)
        # Label
        label = self.small_font.render("Pattern", True, FONT_COLOR)
        self.screen.blit(label, (card_x+12, card_y+10))
        # Tiles
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                color = TILE_COLORS[self.solution[r][c]-1]
                rect = pygame.Rect(
                    card_x+12 + c*(preview_tile+2),
                    card_y+34 + r*(preview_tile+2),
                    preview_tile, preview_tile)
                pygame.draw.rect(self.screen, color, rect, border_radius=8)
    def draw(self):
        self.screen.fill(BG_COLOR)
        tile_size = self.tile_size()
        offset_x = (self.screen.get_width() - (tile_size*GRID_SIZE + TILE_MARGIN*(GRID_SIZE-1)))//2
        offset_y = 220
        self.draw_pattern_card(offset_x, offset_y, tile_size)
        # Draw moves, level, instructions
        moves_surf = self.font.render(f"Moves: {self.moves}", True, FONT_COLOR)
        self.screen.blit(moves_surf, (30, 30))
        level_surf = self.font.render(f"Level: {self.level+1} of {len(LEVELS)}", True, FONT_COLOR)
        self.screen.blit(level_surf, (30, 80))
        instr = self.font.render("Tap two tiles to swap and match the pattern", True, (100,100,120))
        self.screen.blit(instr, (30, 140))
        # Draw grid
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                highlight = self.selected == (r, c)
                self.grid[r][c].size = tile_size
                self.grid[r][c].draw(self.screen, offset_x, offset_y, highlight=highlight)
        # Animate tiles
        for row in self.grid:
            for tile in row:
                tile.animate_swap()
        # Buttons
        self.restart_btn.draw(self.screen, self.font)
        if self.solved:
            msg = self.font.render("Solved!", True, (0,180,0))
            self.screen.blit(msg, (self.screen.get_width()//2-80, 520))
            self.next_btn.draw(self.screen, self.font)
        pygame.display.flip()
    def check_solution(self):
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if self.grid[r][c].value != self.solution[r][c]:
                    return False
        return True
    def handle_tap(self, pos):
        self.restart_btn.check_hover(pos)
        self.next_btn.check_hover(pos)
        if self.restart_btn.is_clicked(pos):
            self.reset()
            return
        if self.solved and self.next_btn.is_clicked(pos):
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
        offset_y = 220
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if self.grid[r][c].rect(offset_x, offset_y).collidepoint(pos):
                    if self.selected is None:
                        self.selected = (r, c)
                    else:
                        r0, c0 = self.selected
                        # Animate swap
                        self.grid[r0][c0].anim = 4
                        self.grid[r][c].anim = 4
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
