from machine import Pin, SPI
import max7219
import time
import random

from machine import Pin, SPI
import max7219
import time
import random

class Game:
    def __init__(self, player_interval=0.3, end_interval=0.6):
        # Maze + buttons
        self.maze, self.player, self.end = self.generate_maze(8, 8)
        self.button_pins = [28, 27, 26, 22, 19, 20]
        self.buttons = [Pin(pin, Pin.IN, Pin.PULL_UP) for pin in self.button_pins]
        self.buttons_values = [1 for pin in self.button_pins]

        # SPI + display setup
        self.spi = SPI(0, baudrate=10000000, polarity=1, phase=0, sck=Pin(2), mosi=Pin(3))
        self.ss = Pin(5, Pin.OUT)
        self.display = max7219.Matrix8x8(self.spi, self.ss, 1)
        self.brightness_value = 5
        self.display.brightness(self.brightness_value)
        self.display.fill(0)
        self.display.show()

        # Flicker timing (customizable)
        self.player_interval = player_interval  # seconds
        self.end_interval = end_interval        # seconds

        # Flicker state tracking
        self.last_player_toggle = time.ticks_ms()
        self.last_end_toggle = time.ticks_ms()
        self.player_on = False
        self.end_on = False
        
    def draw(self):
        for x in range(8):
            for y in range(8):
                if self.maze[x][y] == 1:
                    self.display.pixel(x, y, 1)
                elif self.maze[x][y] == 0:
                    self.display.pixel(x, y, 0)
                elif self.maze[x][y] == 2:
                    self.player[0], self.player[1] = x, y
                    self.display.pixel(x, y, 0)
                elif self.maze[x][y] == 3:
                    self.end = [x, y]
                else:
                    self.display.pixel(x, y, 0)
        self.display.show()
        
    def check_buttons(self):
        for index, button in enumerate(self.buttons):
            if button.value() == 1 and self.buttons_values[index] == 0:
                self.buttons_values[index] = 1
            elif button.value() == 0 and self.buttons_values[index] == 1:
                self.do_buttons(index)
                self.buttons_values[index] = 0
        return -1

    def generate_maze(width, height):
        """Generate a simple maze using iterative depth-first backtracker.

        Returns a 2D list where 1 indicates a visited/corridor cell and 0 is a wall.
        """
        maze = [[0] * width for _ in range(height)]
        start_cell = [random.randint(0, width - 1), random.randint(0, height - 1)]
        stack = [start_cell]
        maze[0][0] = 1
        final_cell = [0,0]
        stackmax = 0
        while stack:
            x, y = stack[-1]

            # collect unvisited neighbors
            neighbors = []
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if not (0 <= nx < width and 0 <= ny < height):
                    continue
                if maze[ny][nx] != 0:
                    continue
                adjacent_visited = 0
                for ddx, ddy in directions:
                    ax, ay = nx + ddx, ny + ddy
                    if 0 <= ax < width and 0 <= ay < height:
                        if maze[ay][ax] == 1 or (ax, ay) == start_cell:
                            adjacent_visited += 1
                if adjacent_visited <= 1:
                    neighbors.append((nx, ny))
            if neighbors:
                next_cell = random.choice(neighbors)
                print(next_cell)
                stack.append(next_cell)
                maze[next_cell[1]][next_cell[0]] = 1
            else:
                if len(stack) > stackmax:
                    stackmax = len(stack)
                    final_cell = stack.pop()
                else:
                    stack.pop()

        return maze, start_cell, final_cell

    def flicker(self):
        now = time.ticks_ms()

        # Player flicker
        if time.ticks_diff(now, self.last_player_toggle) > self.player_interval * 1000:
            self.player_on = not self.player_on
            self.display.pixel(self.player[0], self.player[1], self.player_on)
            self.last_player_toggle = now

        # End flicker
        if time.ticks_diff(now, self.last_end_toggle) > self.end_interval * 1000:
            self.end_on = not self.end_on
            self.display.pixel(self.end[0], self.end[1], self.end_on)
            self.last_end_toggle = now

        self.display.show()
        
    # This method will dedicate certain methods toward each of the buttons
    def do_buttons(self, button_num):
        if (button_num == 0): self.move_left()
        elif (button_num == 1): self.move_right()
        elif (button_num == 2): self.move_down()
        elif (button_num == 3): self.move_up()
        elif (button_num == 4): self.restart()
        elif (button_num == 5): self.change_brightness()
        
    def move_left(self):
        if (self.player[0]>0) and (self.maze[self.player[0]-1][self.player[1]] == 0):
            self.maze[self.player[0]-1][self.player[1]] = 2
            self.maze[self.player[0]][self.player[1]] = 0
            self.player[0] -= 1
        elif (self.maze[self.player[0]-1][self.player[1]] == 3):
            self.restart()
    def move_right(self):
        if (self.player[0]<7) and (self.maze[self.player[0]+1][self.player[1]] == 0):
            self.maze[self.player[0]+1][self.player[1]] = 2
            self.maze[self.player[0]][self.player[1]] = 0
            self.player[0] += 1
            self.draw()
        elif (self.maze[self.player[0]+1][self.player[1]] == 3):
            self.restart()
    def move_down(self):
        if (self.player[1]>0) and (self.maze[self.player[0]][self.player[1]-1] == 0):
            self.maze[self.player[0]][self.player[1]-1] = 2
            self.maze[self.player[0]][self.player[1]] = 0
            self.player[1] -= 1
            self.draw()
        elif (self.maze[self.player[0]][self.player[1]-1] == 3):
            self.restart()
    def move_up(self):
        if (self.player[1]<7) and (self.maze[self.player[0]][self.player[1]+1] == 0):
            self.maze[self.player[0]][self.player[1]+1] = 2
            self.maze[self.player[0]][self.player[1]] = 0
            self.player[1] += 1
            self.draw()
        elif (self.maze[self.player[0]][self.player[1]+1] == 3):
            self.restart()
    def restart(self):
        self.maze = self.generate_maze()
        self.draw()
    def change_brightness(self):
        print(self.brightness_value)
        if (self.brightness_value == 1):
            self.display.brightness(3)
            self.brightness_value = 3
        elif (self.brightness_value == 3):
            self.display.brightness(5)
            self.brightness_value = 5
        elif (self.brightness_value == 5):
            self.display.brightness(7)
            self.brightness_value = 7
        elif (self.brightness_value == 7):
            self.display.brightness(10)
            self.brightness_value = 10
        elif (self.brightness_value == 10):
            self.display.brightness(15)
            self.brightness_value = 15
        elif (self.brightness_value == 15):
            self.display.brightness(1)
            self.brightness_value = 1
        else: # default brightness
            self.display.brightness(5)
            self.brightness_value = 5
    
# Game(player_interval, end_interval)
game = Game(0.05, 0.3)
game.draw()
while(True):
    game.check_buttons()
    game.flicker()
    game.draw()

