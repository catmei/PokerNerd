import cv2
import numpy as np
import pyautogui
import pygetwindow
from pokerstars_recognition import PokerStarsTableRecognizer
from utils import read_config_file, set_window_size, remove_cards, data_concatenate, resize_window
import time

config = read_config_file(filename="../config2.yaml")
resize_window("Hold'em", 2000, 1500)
table_data = []
player_position = None
print_my_turn = 1
last_pot = None
last_table_cards = None
last_my_cards = None

count = 0
while True:
    # start = time.time()
    window = pygetwindow.getWindowsWithTitle("No Limit Hold'em")[0]
    screenshot = pyautogui.screenshot(region=(window.left, window.top, window.width, window.height))

    screenshot = np.array(screenshot)
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
    recognizer = PokerStarsTableRecognizer(screenshot, config)

    try:
        # if not player_position:
        # player_position = recognizer.get_dealer_button_position()
        # print(player_position)

        is_my_turn = recognizer.is_main_player_turn()
        # cv2.imshow('Computer Vision', screenshot)

        if is_my_turn:
            if print_my_turn == 1:
                print("It's my turn")
                print_my_turn = 0
        else:
            print_my_turn = 1

        # detect table cards
        new_table_cards = recognizer.detect_table_cards()
        if new_table_cards != last_table_cards:

            players_info = recognizer.get_dealer_button_position()
            players_info = recognizer.get_empty_seats(players_info)
            players_info = recognizer.get_so_players(players_info)
            players_info = recognizer.assign_positions(players_info)
            print(players_info)

            print(f'table_cards: {new_table_cards}')
            last_table_cards = new_table_cards

        # detect my cards
        new_my_cards = recognizer.detect_hero_cards()
        if new_my_cards != last_my_cards:
            print(f'my_cards: {new_my_cards}')
            last_my_cards = new_my_cards

        new_pot, boxes_number = recognizer.find_total_pot()
        if new_pot == last_pot:
            pass
        else:
            screenshot = pyautogui.screenshot(region=(window.left, window.top, window.width, window.height))
            # screenshot.save(f'pot_example_{count}.png')

            # print('-' * 50)
            # print(f"png_{count}")
            print(f"pot: {new_pot}")
            # print(f"boxes number: {boxes_number}")
            # print('-' * 50)

            last_pot = new_pot
            count += 1
    except Exception as Error:
        print(Error)

    # end = time.time()
    # print(f'fps: {1 / (end - start) }')
