#!/usr/bin/env python3
"""
Tile Swap Puzzle — Integrated UI & Fixed Mechanics
- Compact pattern preview in top bar, right-aligned
- No overlap, clear instructions, centered grid
- Reliable tap-to-swap mechanics
"""
import pygame
import random

# --- CONFIG ---
BG_GRADIENT_TOP = (36, 37, 130)
BG_GRADIENT_BOTTOM = (93, 193, 255)
TITLE_COLOR = (255, 255, 255)
PATTERN_BORDER = (220, 220, 240)
TILE_COLORS = [(255, 99, 132), (54, 162, 235), (75, 192, 120)]  # red, blue, green
SELECTED_BORDER = (255, 215, 0)
INSTR_COLOR = (255,255,255)
BUTTON_COLOR = (54, 162, 235)
BUTTON_TEXT = (255, 255, 255)
BUTTON_SHADOW = (36, 37, 130)
BUTTON_HOVER = (40, 130, 210)
GRID_SIZE = 3
TILE_MARGIN = 14
FONT_SIZE = 32
TITLE_FONT_SIZE = 44

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
        self.anim_offset = (0, 0)
    def rect(self, offset_x, offset_y):
        x = offset_x + self.col * (self.size + TILE_MARGIN) + self.anim_offset[0]
        y = offset_y + self.row * (self.size + TILE_MARGIN) + self.anim_offset[1]
        return pygame.Rect(x, y, self.size, self.size)
    def draw(self, screen, offset_x, offset_y, highlight=False):
        rect = self.rect(offset_x, offset_y)
        shadow_rect = rect.move(4, 8)
        pygame.draw.rect(screen, (0,0,0,60), shadow_rect, border_radius=22)
        color = TILE_COLORS[self.value-1]
        pygame.draw.rect(screen, color, rect, border_radius=22)
        glass = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.ellipse(glass, (255,255,255,60), (0,0,self.size,self.size//2))
        screen.blit(glass, rect.topleft)
        if highlight:
            pygame.draw.rect(screen, SELECTED_BORDER, rect, 6, border_radius=22)
    def animate_swap(self, target_pos=None):
        if self.anim > 0 and target_pos:
            dx = (target_pos[0] - self.col) * (self.size + TILE_MARGIN) / self.anim
            dy = (target_pos[1] - self.row) * (self.size + TILE_MARGIN) / self.anim
            self.anim_offset = (int(dx), int(dy))
            self.anim -= 1
        else:
            self.anim_offset = (0, 0)

class Button:
    def __init__(self, rect, text):
        self.rect = rect
        self.text = text
        self.hover = False
    def draw(self, screen, font):
        shadow_rect = self.rect.move(2, 5)
        pygame.draw.rect(screen, BUTTON_SHADOW, shadow_rect, border_radius=20)
        color = BUTTON_HOVER if self.hover else BUTTON_COLOR
        pygame.draw.rect(screen, color, self.rect, border_radius=20)
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
        self.screen = pygame.display.set_mode((440, 800))
        pygame.display.set_caption("Tile Swap Puzzle")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Nunito", FONT_SIZE, bold=True)
        self.title_font = pygame.font.SysFont("Nunito", TITLE_FONT_SIZE, bold=True)
        self.instr_font = pygame.font.SysFont("Nunito", 26)
        self.level = 0
        self.selected = None
        self.moves = 0
        self.solved = False
        self.animating = False
        self.last_swap = None
        self.reset()
        self.restart_btn = Button(pygame.Rect(40, 700, 160, 54), "Restart")
        self.next_btn = Button(pygame.Rect(240, 700, 160, 54), "Next")
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
        self.last_swap = None
    def tile_size(self):
        w, h = self.screen.get_size()
        size = min((w-80 - (GRID_SIZE-1)*TILE_MARGIN)//GRID_SIZE, (h-500 - (GRID_SIZE-1)*TILE_MARGIN)//GRID_SIZE)
        return size
    def draw_gradient_bg(self):
        w, h = self.screen.get_size()
        for y in range(h):
            ratio = y/h
            r = int(BG_GRADIENT_TOP[0]*(1-ratio) + BG_GRADIENT_BOTTOM[0]*ratio)
            g = int(BG_GRADIENT_TOP[1]*(1-ratio) + BG_GRADIENT_BOTTOM[1]*ratio)
            b = int(BG_GRADIENT_TOP[2]*(1-ratio) + BG_GRADIENT_BOTTOM[2]*ratio)
            pygame.draw.line(self.screen, (r,g,b), (0,y), (w,y))
    def draw_title(self):
        label = self.title_font.render("Tile Swap Puzzle", True, TITLE_COLOR)
        self.screen.blit(label, (self.screen.get_width()//2 - label.get_width()//2, 28))
    def draw_top_bar(self, tile_size):
        moves = self.font.render(f"Moves: {self.moves}", True, TITLE_COLOR)
        level = self.font.render(f"Level: {self.level+1} of {len(LEVELS)}", True, TITLE_COLOR)
        self.screen.blit(moves, (32, 80))
        self.screen.blit(level, (self.screen.get_width()//2 - level.get_width()//2, 80))
        # Compact pattern preview (right-aligned)
        preview_tile = tile_size // 4
        preview_w = preview_tile * GRID_SIZE + 6
        preview_h = preview_tile * GRID_SIZE + 6
        preview_x = self.screen.get_width() - preview_w - 24
        preview_y = 76
        pygame.draw.rect(self.screen, PATTERN_BORDER, (preview_x-3, preview_y-3, preview_w+6, preview_h+6), border_radius=10)
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                color = TILE_COLORS[self.solution[r][c]-1]
                rect = pygame.Rect(
                    preview_x + c*preview_tile,
                    preview_y + r*preview_tile,
                    preview_tile-2, preview_tile-2)
                pygame.draw.rect(self.screen, color, rect, border_radius=6)
    def draw_instructions(self):
        instr = self.instr_font.render("Tap two tiles to swap and match the pattern", True, INSTR_COLOR)
        self.screen.blit(instr, (self.screen.get_width()//2 - instr.get_width()//2, 140))
    def draw_grid(self, tile_size):
        offset_x = self.screen.get_width()//2 - (tile_size*GRID_SIZE + TILE_MARGIN*(GRID_SIZE-1))//2
        offset_y = 210
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                highlight = self.selected == (r, c)
                self.grid[r][c].size = tile_size
                if self.last_swap and (r, c) in self.last_swap:
                    target = self.last_swap[(r, c)]
                    self.grid[r][c].animate_swap(target)
                else:
                    self.grid[r][c].animate_swap()
                self.grid[r][c].draw(self.screen, offset_x, offset_y, highlight=highlight)
    def draw_buttons(self):
        self.restart_btn.draw(self.screen, self.font)
        if self.solved:
            self.next_btn.draw(self.screen, self.font)
    def draw_solved(self):
        if self.solved:
            msg = self.font.render("Solved!", True, (255,255,255))
            self.screen.blit(msg, (self.screen.get_width()//2 - msg.get_width()//2, 630))
    def draw(self):
        self.draw_gradient_bg()
        tile_size = self.tile_size()
        self.draw_title()
        self.draw_top_bar(tile_size)
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
        offset_y = 210
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if self.grid[r][c].rect(offset_x, offset_y).collidepoint(pos):
                    if self.selected is None:
                        self.selected = (r, c)
                    elif self.selected != (r, c):
                        r0, c0 = self.selected
                        # Animate slide
                        self.grid[r0][c0].anim = self.grid[r][c].anim = 6
                        self.last_swap = {(r0, c0): (r, c), (r, c): (r0, c0)}
                        self.grid[r0][c0].value, self.grid[r][c].value = self.grid[r][c].value, self.grid[r0][c0].value
                        self.selected = None
                        self.moves += 1
                        if self.check_solution():
                            self.solved = True
                        pygame.time.set_timer(pygame.USEREVENT, 90)
                    else:
                        # Deselect if the same tile is tapped twice
                        self.selected = None
                    return
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_tap(event.pos)
                elif event.type == pygame.USEREVENT:
                    self.last_swap = None
                    pygame.time.set_timer(pygame.USEREVENT, 0)
            self.draw()
            self.clock.tick(60)

if __name__ == '__main__':
    SwapPuzzleGame().run()
