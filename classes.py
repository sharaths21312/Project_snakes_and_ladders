from __future__ import annotations
import math, typing, pygame
from turtle import screensize
from pygame import Rect, draw


class box:
    """An individual box"""

    def __init__(self, x: int, y: int, num: int, size: int, screen_scale: float | int = 1) -> None:
        self.x = x * screen_scale
        self.y = y * screen_scale
        self.pos = pygame.Vector2(self.x, self.y)
        self.num = num
        self.size = size * screen_scale
        self.rect = Rect([self.x, self.y, self.size, self.size])

    def draw_text(self,
                  canvas: pygame.Surface,
                  font: pygame.font,
                  col: tuple):
        text = font.render(str(self.num), True, col)
        canvas.blit(text,
                    [self.pos.x + self.size/3, self.pos.y + self.size/3])
        # Text starts from 1/3rd the box's size
        # to result in an approximately central position

    def draw(self, canvas: pygame.Surface, color: typing.Sequence):
        draw.rect(canvas, color, self.rect, width=2)


class boxGrid:
    """Stores the grid of boxes"""

    def __init__(self, col: typing.Sequence, screen_scale = 1) -> None:
        self.boxes: list[box] = []
        for i in range(10):
            for j in range(10):
                self.boxes.append(box(
                    10 + ((i % 2) * 540) - (60 * j) +
                    (120 * (1-(i % 2)) * j), 550 - 60 * i,
                    j + 10 * i + 1, 60, screen_scale))
        self.color = col

    def draw_text(self,
                  canvas: pygame.Surface,
                  font: pygame.font) -> None:
        for i in self.boxes:
            i.draw_text(canvas, font, (0, 0, 0))

    def draw(self, canvas: pygame.Surface) -> None:
        for i in self.boxes:
            i.draw(canvas, self.color)


class players:
    """Stores the combination of player objects and the scoreboard"""

    def __init__(self, players_data: dict, screen_scale: int | float = 1) -> None:
        self.players_list: list[player] = []
        for i in players_data['players']:
            self.players_list.append(player(i['name'], i['color'], screen_scale))

        self.turn: int = -1  # 1 will be added on the first call to move()
        self.num_players: int = len(self.players_list)
        self.game_over: bool = False

        self.col: list[int, int, int] = players_data['colors'][
            'players_display_boxes_color']
        self.text_col: list[int, int, int] = players_data['colors']['text']

        self.boxes_pos: list[int, int] = mtp(players_data[
            'players_display_boxes_pos'], screen_scale)
        self.boxes_size: list[int, int] = mtp(players_data[
            'players_display_boxes_size'], screen_scale)

    def move(self, move_by: int) -> None:
        """Processes the current turn of movement"""

        iterations = 0
        self.turn += 1
        self.turn %= self.num_players

        while self.players_list[self.turn].has_won and not self.game_over:
            if iterations == self.num_players:
                self.game_over = True
                return

            self.turn += 1
            self.turn %= self.num_players
            iterations += 1

        self.players_list[self.turn].move(move_by)

    def draw_text(self,
                  canvas: pygame.Surface,
                  font: pygame.font):
        """Draws the text that displays the current score and move"""
        for i, j in enumerate(self.players_list):
            if j.has_won:
                text = font.render(f"{j.name}: won",
                                   True, self.text_col)
            else:
                text = font.render(f"{j.name}: {j.move_to}",
                                   True, self.text_col)
            xpos = self.boxes_pos[0] + self.boxes_size[0] * (i % 2)
            ypos = self.boxes_pos[1] + self.boxes_size[1] * (i > 1)
            canvas.blit(text, [xpos + self.boxes_size[0] /
                        5, ypos + self.boxes_size[1]/5])

    def draw_boxes(self, canvas: pygame.Surface):
        for i in range(self.num_players):
            xpos = self.boxes_pos[0] + self.boxes_size[0] * (i % 2)
            ypos = self.boxes_pos[1] + self.boxes_size[1] * (i > 1)

            draw.rect(canvas, self.col, (xpos, ypos,
                      self.boxes_size[0], self.boxes_size[1]),
                      width=(3 and not self.players_list[i].has_won))
            # Width = 0 -> filled

    def draw_players(self, canvas: pygame.Surface, box_list: list[box]):
        for i in self.players_list:
            i.animate(box_list)
            i.draw(canvas)


class player:
    """Stores an individual player object"""

    def __init__(self, name: str, color: typing.Sequence, screen_scale) -> None:

        # Stores starting position, is for debugging/testing
        start = 1

        self.size = 20 * screen_scale
        self.name: str = name
        self.color: tuple = tuple(color)

        # The current display coordinates of the circle
        self.coordinates: pygame.Vector2 = pygame.Vector2(*mtp((10, 550), screen_scale))
        self.has_won: bool = False

        # The final position of the player after all moves
        self.move_to: int = start
        # The subsection of the path being animated
        self.animate_int: list[int, int] = [start, start]
        self.speed: float = 0.25

        # The current position in terms of the box number 
        self.pos: float = start
        # List of moves in sequence
        self.moves: list[str] = []
        # The endpoint of the animation currently occuring
        self.moving: int = start
        # Used to pause animation between different moves
        self.pauseframes: int = 0

    def draw(self, canvas: pygame.Surface) -> None:
        """Draw the player"""
        draw.circle(canvas, self.color,
                    self.coordinates.elementwise() + 1.5 * self.size, self.size)

    def move(self, move_by: int = 0) -> None:
        """Controls the movement in normal die rolls"""

        self.move_to += move_by
        if self.move_to == 100 or self.move_to - move_by == 100:
            self.has_won = True
        if self.move_to > 100:
            self.move_to -= move_by
            return
        self.moves.append(f'm {self.move_to}')

    def SN_move(self, to: int) -> None:
        """Controls movement when on a snake/ladder"""
        self.moves.append(f's {to}')
        self.move_to = to
        if self.move_to == 100:
            self.has_won = True

    def animate(self, boxes: list[box]) -> None:
        """Proceed with the animation for 1 frame"""

        if self.animate_int[0] == self.animate_int[1] == self.moving:
            # If current move is finished
            if not self.process():
                return
        if self.pauseframes:
            self.pauseframes -= 1
            return

        if self.animate_int[1] == self.animate_int[0] != self.moving:
            self.animate_int[1] += sign(self.moving - self.animate_int[1])

        self.pos += sign(self.animate_int[1] -
                         self.animate_int[0]) * self.speed  # Actual movement

        if (math.fabs(self.pos - self.animate_int[1]) <= self.speed + 0.01
            and self.pos >= self.animate_int[1]):
            # If current step is finished
            self.animate_int[0] = self.animate_int[1]
            self.pos = self.animate_int[1]

            # Coordinates based on current position
        self.coordinates = transform_coordinates(
            self.pos, self.animate_int, boxes[self.animate_int[0] - 1].pos,
            boxes[self.animate_int[1] - 1].pos)

        
        # Working of the animate() function:
        # self.pos defines the current position of the box, and is moved in the animate_int variable
        # For normal movement, the animate_int is the interval of 2 continuous boxes
        # For movement on a snake/ladder, the animate_int is the start and end of the current move
        # The pos variable represents the coordinate in between the two animate_int values
        # self.moving represents the current move that the animation is proceeding in .
        # the self.process function sets the variables up for the next move
        # In a move, the animate_int interval changes several times
        # eg: in moving from 1 to 4, animate_int first takes the value [1, 2],
        # then [2, 3], then [3, 4], then [4, 4] when finished

    def process(self) -> bool:
        """Sets up moves from the moves list to be animated"""
        try:
            x: list[str] = self.moves.pop(0).split()
            y: int = int(x[1])
        except IndexError:
            return None

        if x[0] == 'm':
            self.moving = y
            self.speed = 0.25
            self.pauseframes = 2
        elif x[0] == 's':
            self.speed = abs(y - self.pos)/20 + 0.5
            self.moving = y
            self.animate_int[1] = y
            self.pauseframes = 6
        return True


class snakesLadders:
    """Stores data for snakes, ladders and checking player positions"""

    def __init__(self, data: dict, boxes: list[box], screen_scale: float | int = 1) -> None:
        self.snakes: list[arrow] = []
        self.ladders: list[arrow] = []

        self.snakes_color = data['colors']['snakes']
        self.ladders_color = data['colors']['ladders']
        box_size = 30 * screen_scale

        for i in data['snakes']:
            end = boxes[i[1] - 1]
            start = boxes[i[0] - 1]
            self.snakes.append(arrow((end.x + box_size, end.y + box_size,
                                     start.x + box_size, start.y + box_size),
                                     i[0], i[1]))
        for i in data['ladders']:
            end = boxes[i[1] - 1]
            start = boxes[i[0] - 1]
            self.ladders.append(arrow((end.x + box_size, end.y + box_size,
                                     start.x + box_size, start.y + box_size),
                                     i[0], i[1]))
        # The - 1 is necessary due to the boxes list starting from 0,
        # but the positions read from the file start from 1

    def draw(self, canvas) -> None:
        """Draw the arrows"""

        for i in self.snakes:
            draw.line(canvas, self.snakes_color,
                      i.start, i.vector + i.start, 4)
            draw.polygon(canvas, self.snakes_color, [
                         i.side1 + i.start, i.side2 + i.start, i.start])
        
        for i in self.ladders:
            draw.line(canvas, self.ladders_color,
                      i.start, i.vector + i.start, 4)
            draw.polygon(canvas, self.ladders_color, [
                         i.side1 + i.start, i.side2 + i.start, i.start])

    def check(self, to_check: players) -> None:
        """Check if a player is on a snake or ladder and act accordingly"""
        for i in to_check.players_list:
            if i.has_won: return
            for j in self.snakes + self.ladders:
                if j.start_value == i.move_to:
                    i.SN_move(j.end_value)


class arrow:
    """A class that computes and stores coordinates for drawing an arrow"""

    def __init__(self, t,
                 start_value, end_value) -> None:
        # t : start_x, start_y, end_x, end_y 
        self.vector = pygame.Vector2(t[2] - t[0], t[3] - t[1])
        self.start = pygame.Vector2(t[0], t[1])

        self.side1 = pygame.Vector2()
        self.side2 = pygame.Vector2()

        # Rotate the vectors to form the arrow head 
        # vector.as_polar()[1] is the angle of the vector
        self.side1.from_polar((20, self.vector.as_polar()[1] - 30))
        self.side2.from_polar((20, self.vector.as_polar()[1] + 30))

        self.start_value = start_value
        self.end_value = end_value


def transform_coordinates(value: float,
                          minmax: tuple[float, float],
                          coords1: pygame.Vector2,
                          coords2: pygame.Vector2) -> pygame.Vector2:
    """ Get a position between 2 coordinates """
    try:
        fac = (value - minmax[0])/(minmax[1] - minmax[0])
    except ZeroDivisionError:
        fac = 0
    return coords1 * (1 - fac) + coords2 * fac


def sign(num: float) -> int:  
    """ Sign of number """
    if num == 0:
        return 0
    return int(num // math.fabs(num))

def mtp(t, n: int | float = 1):
    tmp = []
    for i in t:
        tmp.append(i*n)
    return tmp