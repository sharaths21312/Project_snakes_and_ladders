"""Snakes and ladders project"""
import json
from random import randint
import pygame
from pygame.mouse import get_pressed as mouse_pressed, get_pos as mouse_pos

import classes

pygame.font.init()
Font_used: pygame.font = pygame.font.SysFont("arial", 20)
clock = pygame.time.Clock()

# Remove "game.py" (7 characters) from the current file path to get the folder
players_file = open(__file__[0:-7] + 'players.json')
players_text = json.load(players_file)
players_file.close()


pygame.init()
display = pygame.display.set_mode([800, 800], flags=pygame.SCALED | pygame.RESIZABLE)


def init():
    """Initialise all variables"""
    global roll, players_list, players_text, button_move, button_reset, \
        bg_col, snakes_ladders, grid_object, move_text, button_move_col, \
        button_text_col, button_reset_col

    players_file = open(__file__[0:-7] + 'players.json')
    players_text = json.load(players_file)
    players_file.close()

    bg_col = players_text["colors"]["background"]
    button_move_col = players_text["colors"]["move_button"]
    button_reset_col = players_text["colors"]["reset_button"]
    button_text_col = players_text["colors"]["text"]
    roll = 0

    players_list = classes.players(players_text)
    button_move = pygame.Rect(players_text["buttons"]["box_move"], (100, 100))
    button_reset = pygame.Rect(players_text["buttons"]["box_reset"], (60, 40))
    grid_object = classes.boxGrid(players_text["colors"]["grid"])
    snakes_ladders = classes.snakesLadders(players_text, grid_object.boxes)
    move_text = players_text["others"]["move_text_pos"]


init()


while True:
    """Game loop"""
    clock.tick(30)  # Update clock

    for e in pygame.event.get():
        if e.type == pygame.MOUSEMOTION:
            break

        if e.type == pygame.QUIT:
            exit()

        if (mouse_pressed()[0] and button_move.collidepoint(mouse_pos())
                or e.type == pygame.KEYDOWN):
            roll = randint(1, 6)
            players_list.move(roll)
            snakes_ladders.check(players_list)
            print(roll)
        elif mouse_pressed()[0] and button_reset.collidepoint(mouse_pos()):
            init()

    # Redraw screen

    display.lock()
    display.fill(bg_col)
    grid_object.draw(display)
    pygame.draw.rect(display, button_move_col, button_move)
    pygame.draw.rect(display, button_reset_col, button_reset)
    players_list.draw_boxes(display)
    snakes_ladders.draw(display)
    players_list.draw_players(display, grid_object.boxes)
    display.unlock()

    # Move button
    display.blit(Font_used.render("Click here", True, button_text_col),
                 (button_move.x + 15, button_move.y + 25))
    display.blit(Font_used.render("to Move", True, button_text_col),
                 (button_move.x + 20, button_move.y + 50))
    # Reset button
    display.blit(Font_used.render("Reset", True, button_text_col),
                 (button_reset.x + 9, button_reset.y + 7))

    # Movement text
    if players_list.turn != -1 and not players_list.game_over:
        display.blit(Font_used.render(f"{players_list.players_list[players_list.turn].name} moves by {roll}", True, button_text_col),
                     (move_text[0], move_text[1]))
    elif players_list.game_over:
        display.blit(Font_used.render("Game over", True, button_text_col),
                     (move_text[0], move_text[1]))

    # Remaining text
    players_list.draw_text(display, Font_used)
    grid_object.draw_text(display, Font_used)

    # Update display
    pygame.display.update()
