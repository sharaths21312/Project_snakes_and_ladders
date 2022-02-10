"""Snakes and ladders project"""
import json
from random import randint
import pygame

import classes
from classes import mtp

pygame.init()
pygame.font.init()
Font_used: pygame.font = pygame.font.SysFont("arial", 20)
clock = pygame.time.Clock()
wait_frames, rate_limit = 0, 0

# Open json file
players_file = open(__file__[0:-7] + 'players.json')

# Workaround to allow comments
players_str = ""
for i in players_file.readlines():
    if i.find('//') > -1:
        players_str += i[:i.find('//')]
    else:
        players_str += i
players_file.close()
players_text = json.loads(players_str)

screen_scale = players_text['screen_scale']
Font_used: pygame.font = pygame.font.SysFont("arial", int(20 * screen_scale))
display = pygame.display.set_mode([int(800 * screen_scale), int(800 * screen_scale)],
                                    flags=pygame.SCALED)


def init():
    """Initialise all variables"""
    global roll, players_list, players_text, button_move, button_reset, \
        bg_col, snakes_ladders, grid_object, move_text, button_move_col, \
        button_text_col, button_reset_col, display, screen_scale, rate_limit


    bg_col = players_text['colors']['background']
    button_move_col = players_text['colors']['move_button']
    button_reset_col = players_text['colors']['reset_button']
    button_text_col = players_text['colors']['text']
    roll = 0

    rate_limit = players_text["ratelimit"]
    players_list = classes.players(players_text, screen_scale)
    button_move = pygame.Rect(mtp(players_text['box_move'], screen_scale), mtp((100, 100), screen_scale))
    button_reset = pygame.Rect(mtp(players_text['box_reset'], screen_scale), mtp((60, 40), screen_scale))
    grid_object = classes.boxGrid(players_text['colors']['grid'], screen_scale)
    snakes_ladders = classes.snakesLadders(players_text, grid_object.boxes, screen_scale)
    move_text = players_text['move_text_pos']


init()


while True:
    """Game loop"""
    clock.tick(30)  # Update clock

    for e in pygame.event.get():
        if e.type == pygame.MOUSEMOTION:
            break

        if e.type == pygame.QUIT:
            exit()

        if (pygame.mouse.get_pressed()[0] 
                and button_move.collidepoint(pygame.mouse.get_pos())
                or e.type == pygame.KEYDOWN):
            if wait_frames: break
            
            wait_frames += rate_limit
            roll = randint(1, 6)
            players_list.move(roll)
            snakes_ladders.check(players_list)
        elif (pygame.mouse.get_pressed()[0] 
                and button_reset.collidepoint(pygame.mouse.get_pos())):
            init()

    # Update wait frames
    if wait_frames > 0: wait_frames -= 1

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
                 (button_move.x + 15 * screen_scale, button_move.y + 25 * screen_scale))
    display.blit(Font_used.render("to Move", True, button_text_col),
                 (button_move.x + 20 * screen_scale, button_move.y + 50 * screen_scale))
    # Reset button
    display.blit(Font_used.render("Reset", True, button_text_col),
                 (button_reset.x + 9 * screen_scale, button_reset.y + 7 * screen_scale))

    # Movement text
    if players_list.turn != -1 and not players_list.game_over:
        text_displayed = f"{players_list.players_list[players_list.turn].name} moves by {roll}"
        display.blit(Font_used.render(text_displayed, True, button_text_col),
                     (move_text[0] * screen_scale, move_text[1] * screen_scale))
    elif players_list.game_over:
        display.blit(Font_used.render("Game over", True, button_text_col),
                     (move_text[0] * screen_scale, move_text[1] * screen_scale))

    # Remaining text
    players_list.draw_text(display, Font_used)
    grid_object.draw_text(display, Font_used)

    # Update display
    pygame.display.update()
