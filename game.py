import pygame
import random
import copy
from collections import deque

pygame.init()

FPS = 20
DISPLAY_WIDTH  = 300
DISPLAY_HEIGHT = 300
DISPLAY_DIMENSIONS = (DISPLAY_WIDTH, DISPLAY_HEIGHT)

# color swatch
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# get the screen context
screen = pygame.display.set_mode(DISPLAY_DIMENSIONS)
# get the game clock to control update rate
clock = pygame.time.Clock()
grid = []

# compare two-element tuples
def cmp_tpl(t1, t2):
    return (t1[0] == t2[0] and t1[1] == t2[1])

class Game:
    GRID_BOX_SIZE = 10
    GRID_DIMENSIONS = {
        "x": 0,
        "y": 0,
        "w": DISPLAY_WIDTH / GRID_BOX_SIZE,
        "h": DISPLAY_HEIGHT / GRID_BOX_SIZE
    }

    def __init__(self):
        global grid
        # init grid
        rows = []
        for x in xrange(self.GRID_DIMENSIONS["h"]):
            cols = []
            for y in xrange(self.GRID_DIMENSIONS["w"]):
                cols.append(0)
            rows.append(cols)
        grid = rows

        self.snake = Snake(length = 5)
        self.spawn_food()
        self.stopped = False

    def spawn_food(self):
        """ Spawns a new food object in a random location on the grid"""
        def new_food_pos(self):
            return (random.randint(0, self.GRID_DIMENSIONS["w"] - 1),
                random.randint(0, self.GRID_DIMENSIONS["h"] - 1))

        pos = new_food_pos(self)
        x, y = pos
        # recompute position until we spawn on an unoccupied box
        while(grid[x][y]):
            pos = new_food_pos(self)
            x, y = pos

        self.food = Food(pos)

    def is_over(self):
        """ Determines the game over state
            If the snake's head crosses the edge of the grid or its tail,
            it's game over"""

        x, y = self.snake.get_next_pos()

        if x < 0 or x > self.GRID_DIMENSIONS["w"] - 1:
            return True

        if y < 0 or y > self.GRID_DIMENSIONS["h"] - 1:
            return True

        # check if head is occupying the same box as any of its tail
        if len(filter(lambda pos: cmp_tpl(self.snake.get_head(), pos),
            self.snake.get_tail())) >= 1:
            return True

    def is_stopped(self):
        return self.stopped

    def reset(self):
        """Resets the game state by reinitializing the game object"""
        self.__init__()

    def update(self, input_events):
        """The update loop of the game.
            Update the game based on user inputs, game events etc."""
        for event in input_events:
            if event.type == pygame.QUIT:
                self.stopped = True

        self.snake.update(input_events)

        # check if the snake is occupying the same box as the food
        if cmp_tpl(self.snake.get_head(), self.food.get_pos()):
            self.snake.eat(self.food)
            self.spawn_food()

    def render(self, ctx):
        """The render loop of the game.
            Any grid box with a value of 1 is rendered as white, the rest as
            black."""
        global grid
        # reset the screen as black each iteration
        # ie. clearing the board
        ctx.fill(BLACK)
        # set background as black
        self.draw_box(ctx, BLACK, 0, 0, DISPLAY_WIDTH, DISPLAY_HEIGHT)

        for y in xrange(self.GRID_DIMENSIONS["h"]):
            for x in xrange(self.GRID_DIMENSIONS["w"]):
                box_x = self.GRID_DIMENSIONS["x"] + (self.GRID_BOX_SIZE * x)
                box_y = self.GRID_DIMENSIONS["y"] + (self.GRID_BOX_SIZE * y)

                # occupied boxes are drawn as white
                if grid[x][y] == 1:
                    self.draw_box(ctx, WHITE, box_x, box_y, self.GRID_BOX_SIZE,
                        self.GRID_BOX_SIZE)
                else:
                    # unoccupied boxes are drawn as black
                    self.draw_box(ctx, BLACK, box_x, box_y, self.GRID_BOX_SIZE,
                        self.GRID_BOX_SIZE)

        pygame.display.flip()

    def draw_box(self, ctx, color, x, y, w, h):
        pygame.draw.rect(ctx, color, pygame.Rect(x, y, w, h))

class Snake():
    DIR_LEFT  = (-1, 0)
    DIR_RIGHT = (1, 0)
    DIR_DOWN  = (0, 1)
    DIR_UP    = (0, -1)

    def __init__(self, length = 5):
        self.max_length = length
        self.dir = self.DIR_DOWN
        # TODO: random spawn pos
        init_x = 3
        init_y = 4

        # init head and tail, the snake starts with a lenght of 1
        self.tail = deque([])
        self.head = (init_x, init_y)
        # "move" the snake until its at the desired length
        for x in range(0, length):
            self.move()

    def update(self, input_events):
        """The update loop for the snake.
            Process key inputs by the player (the arrow keys). The player can
            only change the direction of the snake"""
        for event in input_events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    if not cmp_tpl(self.get_dir(), self.DIR_RIGHT):
                        self.dir = self.DIR_LEFT
                elif event.key == pygame.K_RIGHT:
                    if not cmp_tpl(self.get_dir(), self.DIR_LEFT):
                        self.dir = self.DIR_RIGHT
                elif event.key == pygame.K_DOWN:
                    if not cmp_tpl(self.get_dir(), self.DIR_UP):
                        self.dir = self.DIR_DOWN
                elif event.key == pygame.K_UP:
                    if not cmp_tpl(self.get_dir(), self.DIR_DOWN):
                        self.dir = self.DIR_UP

        self.move()

    def move(self):
        global grid
        nextpos = self.get_next_pos() # get next postion of the head

        # add the head to the tail and set the new position as the head
        self.tail.append(self.get_head())
        self.head = nextpos
        # update the grid box as occupied
        x, y = self.get_head()
        grid[x][y] = 1

        # the snake can only maintain a lenght of max_length
        if len(self) > self.max_length:
            # drop the last element of the tail
            x, y = self.tail.popleft()
            # set the last element now as unoccupied
            grid[x][y] = 0

    def get_next_pos(self):
        """Gets the next the position of the head"""
        x, y = self.get_head()
        dx, dy = self.get_dir()
        nextpos = (x + dx, y + dy) # add the direction delta to current pos

        return nextpos

    def eat(self, food):
        self.max_length += food.get_value()

    def get_head(self):
        return self.head

    def get_tail(self):
        return self.tail

    def get_dir(self):
        return self.dir

    def set_dir(self, newdir):
        self.dir = newdir

    def get_body(self):
        body = copy.deepcopy(self.tail)
        body.append(self.head)
        return body

    def __len__(self):
        return len(self.get_body())

    def __repr__(self):
        return str(self.get_body())

    def __str__(self):
        return str(self.get_body())

class Food():
    def __init__(self, pos, value = 1):
        global grid
        x, y = pos
        self.pos = pos
        self.value = value
        # set the food's box as occupied
        grid[x][y] = 1

    def get_pos(self):
        return self.pos

    def get_value(self):
        return self.value

game = Game()

# main game loop
while True:
    if game.is_stopped():
        break

    if game.is_over():
        game.reset()

    # player inputs are retrieved by the event.get function in pygame
    game.update(pygame.event.get())

    # pass in the screen context to the game render loop
    game.render(screen)
    # this pauses the loop execution for a certain length of time
    # allowing us to control the game loop rate
    clock.tick(FPS)
