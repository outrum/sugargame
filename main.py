#!/usr/bin/env python3
"""
Tile Swap Puzzle — Modern, Clean, and Mobile-First UI
- Clear layout: top bar, pattern card, instructions, grid, buttons
- No overlapping, perfect alignment and spacing
- Soft color palette, subtle shadows, and clean typography
- Responsive and visually balanced for all screens
"""
import pygame
import random

# --- CONFIG ---
SOFT_BG = (245, 247, 252)
TOP_BAR_BG = (255, 255, 255)
PATTERN_CARD = (255, 255, 255)
PATTERN_SHADOW = (220, 225, 235)
TILE_SHADOW = (210, 215, 230)
TILE_COLORS = [(178, 222, 255), (255, 185, 185), (178, 255, 201)]  # soft blue, soft red, soft green
SELECTED_BORDER = (255, 205, 60)
FONT_COLOR = (40, 40, 60)
INSTR_COLOR = (100, 110, 140)
BUTTON_COLOR = (80, 120, 255)
BUTTON_TEXT = (255, 255, 255)
BUTTON_SHADOW = (180, 190, 230)
BUTTON_HOVER = (60, 100, 210)
GRID_SIZE = 3
TILE_MARGIN = 10
FONT_SIZE = 32

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
        self.anim = 0
    def rect(self, offset_x, offset_y):
        x = offset_x + self.col * (self.size + TILE_MARGIN)
        y = offset_y + self.row * (self.size + TILE_MARGIN)
        return pygame.Rect(x, y, self.size, self.size)
    def draw(self, screen, offset_x, offset_y, highlight=False):
        rect = self.rect(offset_x, offset_y)
        shadow_rect = rect.move(3, 5)
        pygame.draw.rect(screen, TILE_SHADOW, shadow_rect, border_radius=16)
        color = TILE_COLORS[self.value-1]
        pygame.draw.rect(screen, color, rect, border_radius=16)
        if highlight:
            pygame.draw.rect(screen, SELECTED_BORDER, rect, 5, border_radius=16)
        if self.anim > 0:
            pygame.draw.rect(screen, (255,255,255,100), rect, border_radius=16)
    def animate_swap(self):
        if self.anim > 0:
            self.anim -= 1

class Button:
    def __init__(self, rect, text):
        self.rect = rect
        self.text = text
        self.hover = False
    def draw(self, screen, font):
        shadow_rect = self.rect.move(2, 4)
        pygame.draw.rect(screen, BUTTON_SHADOW, shadow_rect, border_radius=16)
        color = BUTTON_HOVER if self.hover else BUTTON_COLOR
        pygame.draw.rect(screen, color, self.rect, border_radius=16)
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
        self.screen = pygame.display.set_mode((420, 720))
        pygame.display.set_caption("Tile Swap Puzzle")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, FONT_SIZE, bold=True)
        self.instr_font = pygame.font.SysFont(None, 26)
        self.level = 0
        self.selected = None
        self.moves = 0
        self.solved = False
        self.reset()
        # Buttons at bottom
        self.restart_btn = Button(pygame.Rect(40, 640, 150, 48), "Restart")
        self.next_btn = Button(pygame.Rect(230, 640, 150, 48), "Next")
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
    def tile_size(self):
        w, h = self.screen.get_size()
        size = min((w-80 - (GRID_SIZE-1)*TILE_MARGIN)//GRID_SIZE, (h-420 - (GRID_SIZE-1)*TILE_MARGIN)//GRID_SIZE)
        return size
    def draw_top_bar(self):
        pygame.draw.rect(self.screen, TOP_BAR_BG, (0, 0, self.screen.get_width(), 60))
        moves = self.font.render(f"Moves: {self.moves}", True, FONT_COLOR)
        level = self.font.render(f"Level: {self.level+1} of {len(LEVELS)}", True, FONT_COLOR)
        self.screen.blit(moves, (24, 14))
        self.screen.blit(level, (220, 14))
    def draw_pattern_card(self, tile_size):
        card_w = tile_size*GRID_SIZE//2 + 32
        card_h = tile_size*GRID_SIZE//2 + 38
        card_x = self.screen.get_width()//2 - card_w//2
        card_y = 80
        pygame.draw.rect(self.screen, PATTERN_SHADOW, (card_x+3, card_y+5, card_w, card_h), border_radius=16)
        pygame.draw.rect(self.screen, PATTERN_CARD, (card_x, card_y, card_w, card_h), border_radius=16)
        label = self.instr_font.render("Pattern", True, FONT_COLOR)
        self.screen.blit(label, (card_x+14, card_y+10))
        preview_tile = tile_size//3
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                color = TILE_COLORS[self.solution[r][c]-1]
                rect = pygame.Rect(
                    card_x+14 + c*(preview_tile+2),
                    card_y+34 + r*(preview_tile+2),
                    preview_tile, preview_tile)
                pygame.draw.rect(self.screen, color, rect, border_radius=7)
    def draw_instructions(self):
        instr = self.instr_font.render("Tap two tiles to swap and match the pattern", True, INSTR_COLOR)
        self.screen.blit(instr, (self.screen.get_width()//2 - instr.get_width()//2, 180))
    def draw_grid(self, tile_size):
        offset_x = self.screen.get_width()//2 - (tile_size*GRID_SIZE + TILE_MARGIN*(GRID_SIZE-1))//2
        offset_y = 220
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                highlight = self.selected == (r, c)
                self.grid[r][c].size = tile_size
                self.grid[r][c].draw(self.screen, offset_x, offset_y, highlight=highlight)
        for row in self.grid:
            for tile in row:
                tile.animate_swap()
    def draw_buttons(self):
        self.restart_btn.draw(self.screen, self.font)
        if self.solved:
            self.next_btn.draw(self.screen, self.font)
    def draw_solved(self):
        if self.solved:
            msg = self.font.render("Solved!", True, (70,180,80))
            self.screen.blit(msg, (self.screen.get_width()//2 - msg.get_width()//2, 570))
    def draw(self):
        self.screen.fill(SOFT_BG)
        tile_size = self.tile_size()
        self.draw_top_bar()
        self.draw_pattern_card(tile_size)
        self.draw_instructions()
        self.draw_grid(tile_size)
        self.draw_solved()
        self.draw_buttons()
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
        offset_x = self.screen.get_width()//2 - (tile_size*GRID_SIZE + TILE_MARGIN*(GRID_SIZE-1))//2
        offset_y = 220
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if self.grid[r][c].rect(offset_x, offset_y).collidepoint(pos):
                    if self.selected is None:
                        self.selected = (r, c)
                    else:
                        r0, c0 = self.selected
                        self.grid[r0][c0].anim = 4
                        self.grid[r][c].anim = 4
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
