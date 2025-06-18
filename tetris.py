import pygame
import random
import json
import os
from typing import List, Tuple, Optional

# Initialize Pygame
pygame.init()

# Constants
GRID_WIDTH = 10
GRID_HEIGHT = 20
CELL_SIZE = 30
GRID_X_OFFSET = 50
GRID_Y_OFFSET = 50
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 700
PREVIEW_X = 550
PREVIEW_Y = 100

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)

# Tetris piece shapes
PIECES = {
    'I': [['.....',
           '..#..',
           '..#..',
           '..#..',
           '..#..'],
          ['.....',
           '.....',
           '####.',
           '.....',
           '.....']],
    
    'O': [['.....',
           '.....',
           '.##..',
           '.##..',
           '.....']],
    
    'T': [['.....',
           '.....',
           '.#...',
           '###..',
           '.....'],
          ['.....',
           '.....',
           '.#...',
           '.##..',
           '.#...'],
          ['.....',
           '.....',
           '.....',
           '###..',
           '.#...'],
          ['.....',
           '.....',
           '.#...',
           '##...',
           '.#...']],
    
    'S': [['.....',
           '.....',
           '.##..',
           '##...',
           '.....'],
          ['.....',
           '.#...',
           '.##..',
           '..#..',
           '.....']],
    
    'Z': [['.....',
           '.....',
           '##...',
           '.##..',
           '.....'],
          ['.....',
           '..#..',
           '.##..',
           '.#...',
           '.....']],
    
    'J': [['.....',
           '.#...',
           '.#...',
           '##...',
           '.....'],
          ['.....',
           '.....',
           '#....',
           '###..',
           '.....'],
          ['.....',
           '.##..',
           '.#...',
           '.#...',
           '.....'],
          ['.....',
           '.....',
           '###..',
           '..#..',
           '.....']],
    
    'L': [['.....',
           '..#..',
           '..#..',
           '.##..',
           '.....'],
          ['.....',
           '.....',
           '###..',
           '#....',
           '.....'],
          ['.....',
           '##...',
           '.#...',
           '.#...',
           '.....'],
          ['.....',
           '.....',
           '..#..',
           '###..',
           '.....']]
}

PIECE_COLORS = {
    'I': CYAN,
    'O': YELLOW,
    'T': PURPLE,
    'S': GREEN,
    'Z': RED,
    'J': BLUE,
    'L': ORANGE
}

class Tetris:
    def __init__(self):
        self.grid = [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = None
        self.current_piece_pos = [0, 0]
        self.current_piece_rotation = 0
        self.next_piece = None
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.fall_time = 0
        self.fall_speed = 500  # milliseconds
        self.game_over = False
        self.paused = False
        
        # Load high scores
        self.high_scores = self.load_high_scores()
        
        # Generate first pieces
        self.spawn_piece()
        self.generate_next_piece()
    
    def load_high_scores(self) -> List[int]:
        """Load high scores from file"""
        try:
            if os.path.exists('tetris_scores.json'):
                with open('tetris_scores.json', 'r') as f:
                    scores = json.load(f)
                    return sorted(scores, reverse=True)[:10]  # Keep top 10
            return []
        except:
            return []
    
    def save_high_scores(self):
        """Save high scores to file"""
        try:
            # Add current score if it's worthy
            scores = self.high_scores[:]
            scores.append(self.score)
            scores = sorted(scores, reverse=True)[:10]  # Keep top 10
            
            with open('tetris_scores.json', 'w') as f:
                json.dump(scores, f)
            
            self.high_scores = scores
        except:
            pass
    
    def get_random_piece(self) -> str:
        """Get a random piece type"""
        return random.choice(list(PIECES.keys()))
    
    def spawn_piece(self):
        """Spawn a new piece at the top"""
        if self.next_piece:
            piece_type = self.next_piece
        else:
            piece_type = self.get_random_piece()
        
        self.current_piece = piece_type
        self.current_piece_pos = [0, GRID_WIDTH // 2 - 2]
        self.current_piece_rotation = 0
        
        # Check if game over
        if self.check_collision():
            self.game_over = True
    
    def generate_next_piece(self):
        """Generate the next piece"""
        self.next_piece = self.get_random_piece()
    
    def get_piece_shape(self, piece_type: str, rotation: int) -> List[str]:
        """Get the shape of a piece at a specific rotation"""
        return PIECES[piece_type][rotation % len(PIECES[piece_type])]
    
    def check_collision(self, dx: int = 0, dy: int = 0, rotation: Optional[int] = None) -> bool:
        """Check if the current piece collides with the grid or boundaries"""
        if not self.current_piece:
            return False
        
        test_rotation = rotation if rotation is not None else self.current_piece_rotation
        shape = self.get_piece_shape(self.current_piece, test_rotation)
        
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell == '#':
                    new_x = self.current_piece_pos[1] + x + dx
                    new_y = self.current_piece_pos[0] + y + dy
                    
                    # Check boundaries
                    if new_x < 0 or new_x >= GRID_WIDTH or new_y >= GRID_HEIGHT:
                        return True
                    
                    # Check collision with placed pieces
                    if new_y >= 0 and self.grid[new_y][new_x] != BLACK:
                        return True
        
        return False
    
    def place_piece(self):
        """Place the current piece on the grid"""
        if not self.current_piece:
            return
        
        shape = self.get_piece_shape(self.current_piece, self.current_piece_rotation)
        color = PIECE_COLORS[self.current_piece]
        
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell == '#':
                    grid_x = self.current_piece_pos[1] + x
                    grid_y = self.current_piece_pos[0] + y
                    if grid_y >= 0:
                        self.grid[grid_y][grid_x] = color
        
        # Clear completed lines
        self.clear_lines()
        
        # Spawn next piece
        self.spawn_piece()
        self.generate_next_piece()
    
    def clear_lines(self):
        """Clear completed lines and update score"""
        lines_to_clear = []
        
        for y in range(GRID_HEIGHT):
            if all(cell != BLACK for cell in self.grid[y]):
                lines_to_clear.append(y)
        
        # Remove cleared lines
        for y in lines_to_clear:
            del self.grid[y]
            self.grid.insert(0, [BLACK for _ in range(GRID_WIDTH)])
        
        # Update score and level
        if lines_to_clear:
            self.lines_cleared += len(lines_to_clear)
            
            # Scoring system
            line_scores = {1: 100, 2: 300, 3: 500, 4: 800}
            self.score += line_scores.get(len(lines_to_clear), 0) * self.level
            
            # Level up every 10 lines
            new_level = self.lines_cleared // 10 + 1
            if new_level > self.level:
                self.level = new_level
                self.fall_speed = max(50, 500 - (self.level - 1) * 50)
    
    def move_piece(self, dx: int, dy: int):
        """Move the current piece"""
        if self.game_over or self.paused:
            return
        
        if not self.check_collision(dx, dy):
            self.current_piece_pos[1] += dx
            self.current_piece_pos[0] += dy
        elif dy > 0:  # Piece hit bottom
            self.place_piece()
    
    def rotate_piece(self):
        """Rotate the current piece"""
        if self.game_over or self.paused or not self.current_piece:
            return
        
        new_rotation = (self.current_piece_rotation + 1) % len(PIECES[self.current_piece])
        
        if not self.check_collision(rotation=new_rotation):
            self.current_piece_rotation = new_rotation
    
    def drop_piece(self):
        """Drop the piece all the way down"""
        if self.game_over or self.paused:
            return
        
        while not self.check_collision(0, 1):
            self.current_piece_pos[0] += 1
        
        self.place_piece()
    
    def update(self, dt: int):
        """Update game state"""
        if self.game_over or self.paused:
            return
        
        self.fall_time += dt
        
        if self.fall_time >= self.fall_speed:
            self.move_piece(0, 1)
            self.fall_time = 0
    
    def reset_game(self):
        """Reset the game to initial state"""
        self.grid = [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = None
        self.current_piece_pos = [0, 0]
        self.current_piece_rotation = 0
        self.next_piece = None
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.fall_time = 0
        self.fall_speed = 500
        self.game_over = False
        self.paused = False
        
        self.spawn_piece()
        self.generate_next_piece()

class TetrisRenderer:
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font
        self.large_font = pygame.font.Font(None, 48)
    
    def draw_grid(self, tetris: Tetris):
        """Draw the game grid"""
        # Draw grid lines
        for x in range(GRID_WIDTH + 1):
            pygame.draw.line(self.screen, GRAY, 
                           (GRID_X_OFFSET + x * CELL_SIZE, GRID_Y_OFFSET),
                           (GRID_X_OFFSET + x * CELL_SIZE, GRID_Y_OFFSET + GRID_HEIGHT * CELL_SIZE))
        
        for y in range(GRID_HEIGHT + 1):
            pygame.draw.line(self.screen, GRAY,
                           (GRID_X_OFFSET, GRID_Y_OFFSET + y * CELL_SIZE),
                           (GRID_X_OFFSET + GRID_WIDTH * CELL_SIZE, GRID_Y_OFFSET + y * CELL_SIZE))
        
        # Draw placed pieces
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if tetris.grid[y][x] != BLACK:
                    rect = pygame.Rect(GRID_X_OFFSET + x * CELL_SIZE + 1,
                                     GRID_Y_OFFSET + y * CELL_SIZE + 1,
                                     CELL_SIZE - 2, CELL_SIZE - 2)
                    pygame.draw.rect(self.screen, tetris.grid[y][x], rect)
    
    def draw_current_piece(self, tetris: Tetris):
        """Draw the current falling piece"""
        if not tetris.current_piece:
            return
        
        shape = tetris.get_piece_shape(tetris.current_piece, tetris.current_piece_rotation)
        color = PIECE_COLORS[tetris.current_piece]
        
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell == '#':
                    screen_x = GRID_X_OFFSET + (tetris.current_piece_pos[1] + x) * CELL_SIZE + 1
                    screen_y = GRID_Y_OFFSET + (tetris.current_piece_pos[0] + y) * CELL_SIZE + 1
                    
                    if screen_y >= GRID_Y_OFFSET:  # Only draw if visible
                        rect = pygame.Rect(screen_x, screen_y, CELL_SIZE - 2, CELL_SIZE - 2)
                        pygame.draw.rect(self.screen, color, rect)
    
    def draw_next_piece(self, tetris: Tetris):
        """Draw the next piece preview"""
        if not tetris.next_piece:
            return
        
        # Draw preview box
        preview_rect = pygame.Rect(PREVIEW_X, PREVIEW_Y, 150, 100)
        pygame.draw.rect(self.screen, DARK_GRAY, preview_rect)
        pygame.draw.rect(self.screen, WHITE, preview_rect, 2)
        
        # Draw "NEXT" label
        next_text = self.font.render("NEXT", True, WHITE)
        self.screen.blit(next_text, (PREVIEW_X + 10, PREVIEW_Y - 25))
        
        # Draw preview piece
        shape = tetris.get_piece_shape(tetris.next_piece, 0)
        color = PIECE_COLORS[tetris.next_piece]
        
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell == '#':
                    screen_x = PREVIEW_X + 20 + x * 20
                    screen_y = PREVIEW_Y + 20 + y * 20
                    rect = pygame.Rect(screen_x, screen_y, 18, 18)
                    pygame.draw.rect(self.screen, color, rect)
    
    def draw_ui(self, tetris: Tetris):
        """Draw the game UI"""
        # Score
        score_text = self.font.render(f"Score: {tetris.score}", True, WHITE)
        self.screen.blit(score_text, (PREVIEW_X, PREVIEW_Y + 120))
        
        # Level
        level_text = self.font.render(f"Level: {tetris.level}", True, WHITE)
        self.screen.blit(level_text, (PREVIEW_X, PREVIEW_Y + 150))
        
        # Lines
        lines_text = self.font.render(f"Lines: {tetris.lines_cleared}", True, WHITE)
        self.screen.blit(lines_text, (PREVIEW_X, PREVIEW_Y + 180))
        
        # High Score
        if tetris.high_scores:
            high_score_text = self.font.render(f"High: {tetris.high_scores[0]}", True, WHITE)
            self.screen.blit(high_score_text, (PREVIEW_X, PREVIEW_Y + 210))
        
        # Controls
        controls = [
            "Controls:",
            "← → Move",
            "↓ Soft Drop",
            "↑ Rotate",
            "Space Hard Drop",
            "P Pause",
            "R Restart"
        ]
        
        for i, control in enumerate(controls):
            color = WHITE if i == 0 else GRAY
            control_text = self.font.render(control, True, color)
            self.screen.blit(control_text, (PREVIEW_X, PREVIEW_Y + 280 + i * 25))
    
    def draw_game_over(self, tetris: Tetris):
        """Draw game over screen"""
        # Semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Game Over text
        game_over_text = self.large_font.render("GAME OVER", True, WHITE)
        game_over_rect = game_over_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50))
        self.screen.blit(game_over_text, game_over_rect)
        
        # Final score
        score_text = self.font.render(f"Final Score: {tetris.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        self.screen.blit(score_text, score_rect)
        
        # High scores
        if tetris.high_scores:
            high_scores_text = self.font.render("High Scores:", True, WHITE)
            high_scores_rect = high_scores_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 40))
            self.screen.blit(high_scores_text, high_scores_rect)
            
            for i, score in enumerate(tetris.high_scores[:5]):  # Show top 5
                score_text = self.font.render(f"{i + 1}. {score}", True, WHITE)
                score_rect = score_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 70 + i * 25))
                self.screen.blit(score_text, score_rect)
        
        # Restart instruction
        restart_text = self.font.render("Press R to restart or ESC to quit", True, WHITE)
        restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50))
        self.screen.blit(restart_text, restart_rect)
    
    def draw_pause(self):
        """Draw pause screen"""
        pause_text = self.large_font.render("PAUSED", True, WHITE)
        pause_rect = pause_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        self.screen.blit(pause_text, pause_rect)
        
        resume_text = self.font.render("Press P to resume", True, WHITE)
        resume_rect = resume_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 40))
        self.screen.blit(resume_text, resume_rect)

def main():
    """Main game loop"""
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Tetris Clone")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 24)
    
    tetris = Tetris()
    renderer = TetrisRenderer(screen, font)
    
    running = True
    
    while running:
        dt = clock.tick(60)  # 60 FPS
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                
                elif event.key == pygame.K_r:
                    if tetris.game_over:
                        tetris.save_high_scores()
                    tetris.reset_game()
                
                elif event.key == pygame.K_p:
                    if not tetris.game_over:
                        tetris.paused = not tetris.paused
                
                elif not tetris.game_over and not tetris.paused:
                    if event.key == pygame.K_LEFT:
                        tetris.move_piece(-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        tetris.move_piece(1, 0)
                    elif event.key == pygame.K_DOWN:
                        tetris.move_piece(0, 1)
                    elif event.key == pygame.K_UP:
                        tetris.rotate_piece()
                    elif event.key == pygame.K_SPACE:
                        tetris.drop_piece()
        
        # Update game
        tetris.update(dt)
        
        # Draw everything
        screen.fill(BLACK)
        
        renderer.draw_grid(tetris)
        renderer.draw_current_piece(tetris)
        renderer.draw_next_piece(tetris)
        renderer.draw_ui(tetris)
        
        if tetris.game_over:
            renderer.draw_game_over(tetris)
        elif tetris.paused:
            renderer.draw_pause()
        
        pygame.display.flip()
    
    # Save high scores on exit
    if tetris.score > 0:
        tetris.save_high_scores()
    
    pygame.quit()

if __name__ == "__main__":
    main()

