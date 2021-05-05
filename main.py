import os
import sys
import json
import random
import pygame

# Initialize pygame
pygame.init()

# Fonts
TITLE_FONT = pygame.font.Font('res/fonts/Emulogic-zrEw.ttf', 50)
MAIN_FONT = pygame.font.Font('res/fonts/Emulogic-zrEw.ttf', 20)

# Import Images
BLOCK_IMAGE = pygame.image.load(os.path.join('res', 'sprites', 'block_basic.png'))

# Screen
WIDTH, HEIGHT = 760, 660
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tetris")
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
COLORS = ["blue", "purple", "green", "red", "orange", "cyan", "yellow"]

# Game variables
game_over = False
debug_mode = False
saved_game_time = ""
current_scene = None
player_score = 0
next_call = 0
time = 0
time_delete = []
game_map = [
    "1","1","1","1","1","1","1","1","1","1","1","1",
    "1","0","0","0","0","0","0","0","0","0","0","1",
    "1","0","0","0","0","0","0","0","0","0","0","1",
    "1","0","0","0","0","0","0","0","0","0","0","1",
    "1","0","0","0","0","0","0","0","0","0","0","1",
    "1","0","0","0","0","0","0","0","0","0","0","1",
    "1","0","0","0","0","0","0","0","0","0","0","1",
    "1","0","0","0","0","0","0","0","0","0","0","1",
    "1","0","0","0","0","0","0","0","0","0","0","1",
    "1","0","0","0","0","0","0","0","0","0","0","1",
    "1","0","0","0","0","0","0","0","0","0","0","1",
    "1","0","0","0","0","0","0","0","0","0","0","1",
    "1","0","0","0","0","0","0","0","0","0","0","1",
    "1","0","0","0","0","0","0","0","0","0","0","1",
    "1","0","0","0","0","0","0","0","0","0","0","1",
    "1","0","0","0","0","0","0","0","0","0","0","1",
    "1","0","0","0","0","0","0","0","0","0","0","1",
    "1","0","0","0","0","0","0","0","0","0","0","1",
    "1","0","0","0","0","0","0","0","0","0","0","1",
    "1","0","0","0","0","0","0","0","0","0","0","1",
    "1","0","0","0","0","0","0","0","0","0","0","1",
    "1","1","1","1","1","1","1","1","1","1","1","1"
]

'''
---- Scenes ----
- Main Menu  = 0
- Game       = 1
'''

class Grid:
    def __init__(self, pos):
        self.rect = pygame.Rect(pos, (30, 30))
        self.occupied = False
    
    def draw(self):
        if game_over:
            pygame.draw.rect(SCREEN, RED, self.rect, 1)
        elif not self.occupied:
            pygame.draw.rect(SCREEN, WHITE, self.rect, 1)
        elif self.occupied:
            pygame.draw.rect(SCREEN, GREEN, self.rect, 1)

    def check_occupied(self, shapes_list):
        for shape in shapes_list:
            if not shape.infocus:
                for block in shape.blocks:
                    if block.rect.y == self.rect.y:
                        if block.rect.x == self.rect.x:
                            self.occupied = True
                            return
        self.occupied = False


class Shapes:
    def __init__(self, surface, blocks_list, shape, pos=[350,-120], color=None):
        with open('res/shapes.json', 'r') as jsn:
            self.data = json.load(jsn)
            self.shape = self.data['shapes'][shape][0]
        self.pos = {"x": pos[0], "y": pos[1]}
        self.blocks = []
        self.infocus = True
        self.surface = surface
        self.rotation = 0
        self.shape_type = shape
        if color is None:
            self.color = COLORS[random.randint(0,6)]
        else:
            self.color = color
        self.add_blocks(blocks_list)

    def remove_focus(self, shape_in_focus):
        self.infocus = False
        if shape_in_focus.count(self) > 0:
            shape_in_focus.remove(self)

    def move(self, direction, shapes_list):
        self.can_move = True
        for shape in shapes_list:
            for block in shape.blocks:
                if self.blocks.count(block) > 0:
                    continue
                else:
                    for m_block in self.blocks:
                        if m_block.rect.x + (30 * direction) == block.rect.x:
                            if m_block.rect.y == block.rect.y:
                                self.can_move = False
                                break
                        elif m_block.rect.x + (30 * direction) <= 200 or m_block.rect.x + (30 * direction) + 30 >= 560:
                            self.can_move = False
                            break
        if self.can_move:
            self.pos["x"] += 30 * direction
            for block in self.blocks:
                block.rect.x += 30 * direction

    def rotate(self, shapes_list, blocks_list):
        if self.infocus:
            self.can_rotate = True
            self.rotation += 1
            self.shape = self.data['shapes'][self.shape_type][self.rotation%len(self.data['shapes'][self.shape_type])]
            for shape in shapes_list:
                if shape is not self:
                    for block in shape.blocks:
                        for n in range(len(self.shape)):
                            if self.shape[n] == 1:
                                if block.rect.x == self.pos["x"]+(n%4*30):
                                    if block.rect.y == self.pos["y"]+(n//4*30):
                                        self.can_rotate = False
                                        self.rotation -= 1
                                        return
            for block in blocks_list:
                if block.wall:
                    for n in range(len(self.shape)):
                        if self.shape[n] == 1:
                            if block.rect.x == self.pos["x"]+(n%4*30):
                                if block.rect.y == self.pos["y"]+(n//4*30):
                                    self.can_rotate = False
                                    self.rotation -= 1
                                    return
            if self.can_rotate:
                self.blocks.clear()
                for n in range(len(self.shape)):
                    if self.shape[n] == 1:
                        self.temp_block = Block(self.surface , (self.pos["x"]+(n%4*30),self.pos["y"]+(n//4*30)), self.color, parent=self)
                        self.blocks.append(self.temp_block)

    
    def force_decent(self, shapes_list, shape_in_focus):
        self.can_move = True
        for shape in shapes_list:
            if not shape.infocus:
                for block in shape.blocks:
                    if not block.wall:
                        for m_block in self.blocks:
                            if m_block.rect.y + 30 == block.rect.y:
                                if m_block.rect.x == block.rect.x:
                                    self.can_move = False
                                    self.remove_focus(shape_in_focus)
                                    return
        for my_block in self.blocks:
            if my_block.rect.y + 30 == SCREEN.get_height() - 30: 
                self.can_move = False
                self.remove_focus(shape_in_focus)
                return
        if self.can_move:
            self.pos["y"] += 30
            for block in self.blocks:
                block.rect.y += 30
            
    def add_blocks(self, blocks_list):
        for n in range(len(self.shape)):
            if self.shape[n] == 1:
                self.temp_block = Block(self.surface , (self.pos["x"]+(n%4*30),self.pos["y"]+(n//4*30)), self.color, parent=self)
                self.blocks.append(self.temp_block)
    
    def draw_blocks(self):
        for block in self.blocks:
            block.draw()
    
    def decent_blocks(self, shapes_list, shape_in_focus):
        if self.infocus:
            self.can_move = True
            for shape in shapes_list:
                if not shape.infocus:
                    for block in shape.blocks:
                        if not block.wall:
                            for m_block in self.blocks:
                                if m_block.rect.y + 30 == block.rect.y:
                                    if m_block.rect.x == block.rect.x:
                                        self.can_move = False
                                        self.remove_focus(shape_in_focus)
                                        return
            for my_block in self.blocks:
                if my_block.rect.y + 30 == SCREEN.get_height() - 30: 
                    self.can_move = False
                    self.remove_focus(shape_in_focus)
                    return
            if self.can_move:
                self.pos["y"] += 30
                for block in self.blocks:
                    block.rect.y += 30


class Block:
    def __init__(self, surface, pos, color, wall=False, parent=None):
        self.rect = pygame.Rect(pos, (30, 30))
        self.wall = wall
        self.image = pygame.image.load('res/sprites/block_' + color + '.png')
        self.surface = surface
        self.parent = parent
    
    def draw(self):
        self.surface.blit(self.image, self.rect)
    
    def destroy(self):
        if self.parent.blocks.count(self) > 0:
            self.parent.blocks.remove(self)


def spawn_blocks(shapes_list, shape_in_focus, blocks_list):
    if len(shape_in_focus) < 2:
        shapes = ["I", "J", "L", "O", "S", "T", "Z"]
        temp = Shapes(SCREEN, blocks_list, random.choice(shapes))
        shapes_list.append(temp)
        shape_in_focus.append(temp)


def initialize_grids(grid_list):
    x = 0
    y = 0
    for i in range(264):
        if (x + 30) == 390:
            x = 0
            y += 30
        grid_list.append(Grid((200 + x, y)))
        x += 30


def initialize_borders(blocks_list):
    for n in range(len(game_map)):
        if game_map[n] == "1":
            temp_block = Block(SCREEN, (200 + (n%12*30), (n//12*30)), "basic", True)
            blocks_list.append(temp_block)


def draw_next_shape(shape_in_focus, blocks_list):
    if len(shape_in_focus) > 1:
        shape_color = shape_in_focus[1].color
        if shape_in_focus[1].shape_type == "I":
            next_shape = Shapes(SCREEN, blocks_list, shape_in_focus[1].shape_type, (90, 210), color=shape_color)
        elif shape_in_focus[1].shape_type == "Z" or shape_in_focus[1].shape_type == "S":
            next_shape = Shapes(SCREEN, blocks_list, shape_in_focus[1].shape_type, (60, 270), color=shape_color)
        elif shape_in_focus[1].shape_type == "O":
            next_shape = Shapes(SCREEN, blocks_list, shape_in_focus[1].shape_type, (70, 270), color=shape_color)
        elif shape_in_focus[1].shape_type == "T":
            next_shape = Shapes(SCREEN, blocks_list, shape_in_focus[1].shape_type, (60, 270), color=shape_color)
        else:
            next_shape = Shapes(SCREEN, blocks_list, shape_in_focus[1].shape_type, (70, 240), color=shape_color)
        next_shape.draw_blocks()


def move_shape(direction, shape_in_focus, shapes_list):
    if len(shape_in_focus) == 0:
        return
    shape_in_focus[0].move(direction, shapes_list)


def rotate_shape(shape_in_focus, blocks_list, shapes_list):
    if len(shape_in_focus) == 0:
        return
    shape_in_focus[0].rotate(shapes_list, blocks_list)


def force_decent_shape(shape_in_focus, shapes_list):
    if len(shape_in_focus) == 0:
        return
    shape_in_focus[0].force_decent(shapes_list, shape_in_focus)


def decent_timer(shape_in_focus, shapes_list, game_speed):
    global next_call
    if next_call == 0:
        next_call = pygame.time.get_ticks() + game_speed
    if pygame.time.get_ticks() > next_call:
        if len(shape_in_focus) > 0 and not game_over:
            shape_in_focus[0].decent_blocks(shapes_list, shape_in_focus)
        next_call = pygame.time.get_ticks() + game_speed


def set_game_speed(time):
    current_time = time//1000
    if current_time//60 <= 1:
        return [800, "01"]
    elif 1 < current_time//60 <= 3:
        return [600, "02"]
    elif 3 < current_time//60 <= 4:
        return [500, "03"]
    elif 4 < current_time//60 <= 6:
        return [450, "04"]
    elif 6 < current_time//60 <= 7:
        return [400, "05"]
    elif 7 < current_time//60 <= 8:
        return [350, "06"]
    elif 8 < current_time//60 <= 9:
        return [300, "07"]
    elif 9 < current_time//60 <= 11:
        return [250, "08"]
    elif 11 < current_time//60 <= 13:
        return [200, "09"]
    elif 13 < current_time//60 <= 15:
        return [150, "10"]
    elif current_time//60 > 15:
        return [100, "10+"]


def check_grids(grid_list, shapes_list, game_speed):
    global player_score
    for n in range(20):
        remove = True
        for grid in grid_list:
            if grid.rect.y == 30 + (n*30) and grid.rect.x == 230 and grid.occupied and remove:
                for related_grid in grid_list:
                    if 200 < related_grid.rect.x < 530: 
                        if grid.rect.y == related_grid.rect.y and related_grid.occupied == False:
                            remove = False
                if remove:
                    for x in range(3):
                        for shape in shapes_list:
                            for block in shape.blocks:
                                if block.rect.y == grid.rect.y:
                                    block.destroy()
                    for shape in shapes_list:
                        if not shape.infocus:
                            for block in shape.blocks:
                                if block.rect.y < grid.rect.y:
                                    block.rect.y += 30
                    player_score += (1000 - game_speed)
    for n in range(10):
        for grid in grid_list:
            if grid.rect.x == 230 + (n*30) and grid.rect.y == 30 and grid.occupied:
                global game_over, time
                return_game_time(time, True)
                save_score(player_score)
                game_over = True


def return_game_time(time, save=False):
    global saved_game_time
    if not game_over:
        game_time_min = time//1000//60
        game_time_sec = time//1000%60
        if game_time_min < 10:
            ret_min = "0"+str(game_time_min)
        else:
            ret_min = str(game_time_min)
        if game_time_sec < 10:
            ret_sec = "0"+str(game_time_sec)
        else:
            ret_sec = str(game_time_sec)
        if save:
            saved_game_time = ret_min + ":" + ret_sec
        return ret_min + ":" + ret_sec
    if game_over:
        return saved_game_time


def save_score(score):
    with open('res/scores.json', 'r') as jsn:
        data = json.load(jsn)
    data['highscore'].append(score)
    data['highscore'].sort()
    data['highscore'].pop(0)
    data['highscore'].reverse()
    with open('res/scores.json', 'w') as jsn:
        json.dump(data, jsn, indent=4)


def game(grid_list, blocks_list, shapes_list, shape_in_focus, time):
    # Always at the top
    SCREEN.fill(BLACK)

    if debug_mode:
        for grid in grid_list:
            grid.draw()

    for shape in shapes_list:
        shape.draw_blocks()
    
    for block in blocks_list:
        if block.wall:
            block.draw()

    # Draw next shape
    draw_next_shape(shape_in_focus, blocks_list)

    # Score Text
    if not game_over:
        SCREEN.blit(MAIN_FONT.render("TIME",True, GREEN), (570, 150))
    else:
        SCREEN.blit(MAIN_FONT.render("TIME",True, RED), (570, 150))
    SCREEN.blit(MAIN_FONT.render(return_game_time(time),True, WHITE), (570, 175))
    if not game_over:
        SCREEN.blit(MAIN_FONT.render("SCORE",True, GREEN), (570, 225))
    else:
        SCREEN.blit(MAIN_FONT.render("SCORE",True, RED), (570, 225))
    SCREEN.blit(MAIN_FONT.render(str(player_score),True, WHITE), (570, 250))
    if not game_over:
        SCREEN.blit(MAIN_FONT.render("LEVEL",True, GREEN), (570, 300))
    else:
        SCREEN.blit(MAIN_FONT.render("LEVEL",True, RED), (570, 300))
    SCREEN.blit(MAIN_FONT.render(set_game_speed(time)[1],True, WHITE), (580, 325))
    if not game_over:
        SCREEN.blit(MAIN_FONT.render("HIGHSCORE",True, GREEN), (570, 375))
    else:
        SCREEN.blit(MAIN_FONT.render("HIGHSCORE",True, RED), (570, 375))
    with open('res/scores.json', 'r') as jsn:
        h_data = json.load(jsn)
    for n in range(len(h_data['highscore'])):
        SCREEN.blit(MAIN_FONT.render(str(n+1)+"-"+str(h_data['highscore'][n]),True, WHITE), (570, 400+(n*25)))
    SCREEN.blit(MAIN_FONT.render("NEXT",True,WHITE), (60, 365))
    SCREEN.blit(MAIN_FONT.render("SHAPE",True,WHITE), (50, 385))

    if game_over:
        SCREEN.blit(TITLE_FONT.render("GAME OVER!", True, WHITE), (140, 300))
        SCREEN.blit(MAIN_FONT.render("'R' to Restart 'ESC' to Quit", True, RED), (95, 360))
    # Always at the bottom
    pygame.display.update()


def main(time_delete):

    global current_scene, game_over

    # Clock
    game_clock = pygame.time.Clock()

    # Grid
    grid_list = []
    initialize_grids(grid_list)

    # Blocks
    blocks_list = []
    initialize_borders(blocks_list)

    # Shapes
    shapes_list = []
    shape_in_focus = []

    # Game variables
    current_scene = 1
    game_over = False
    run = True

    while run:

        global time

        game_clock.tick(FPS)

        event_list = pygame.event.get()

        for event in event_list:
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_i:
                    global debug_mode
                    debug_mode = not debug_mode
                if event.key == pygame.K_r:
                    time_delete.append(time)
                    main(time_delete)
                    return
                if event.key == pygame.K_ESCAPE:
                    run = False
                    pygame.quit()
                    sys.exit()
        
        if current_scene == 0:
            pass
        elif current_scene == 1:

            # Clock
            if len(time_delete) > 0:
                time = pygame.time.get_ticks()
                for past_time in time_delete:
                    print(past_time)
                    time -= past_time
            else:
                time = pygame.time.get_ticks()

            if not game_over:
                # Player input
                keys_pressed = pygame.key.get_pressed()
                # Decent a shape in fast way
                if keys_pressed[pygame.K_SPACE]:
                    force_decent_shape(shape_in_focus, shapes_list)
                # Other Inputs
                for event in event_list:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                            move_shape(-1, shape_in_focus, shapes_list)
                        elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                            move_shape(+1, shape_in_focus, shapes_list)
                        elif event.key == pygame.K_s  or event.key == pygame.K_DOWN:
                            force_decent_shape(shape_in_focus, shapes_list)
                        elif event.key == pygame.K_w or event.key == pygame.K_UP:
                            rotate_shape(shape_in_focus, blocks_list, shapes_list)

                # Spawn new blocks
                spawn_blocks(shapes_list, shape_in_focus, blocks_list)

                # Set game speed
                game_speed = set_game_speed(time)[0]

                # Timer to decent blocks
                decent_timer(shape_in_focus, shapes_list, game_speed)

                # Check grids
                for grid in grid_list:
                    grid.check_occupied(shapes_list)
                check_grids(grid_list, shapes_list, game_speed)

            # Update the game display
            game(grid_list, blocks_list, shapes_list, shape_in_focus, time)


if __name__ == "__main__":
    main(time_delete)

