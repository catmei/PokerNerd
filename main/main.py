import cv2
import numpy as np
import pyautogui
import pygetwindow
from pokerstars_recognition import PokerStarsTableRecognizer
from utils import read_config_file, set_window_size, remove_cards, data_concatenate, resize_window
import time

config = read_config_file()
resize_window("Hold'em", 1600, 1200)
table_data = []
last_pot = None
new_pot = None

count = 0
while True:
    # start = time.time()
    window = pygetwindow.getWindowsWithTitle("No Limit Hold'em")[0]
    screenshot = pyautogui.screenshot(region=(window.left, window.top, window.width, window.height))

    screenshot = np.array(screenshot)
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
    recognizer = PokerStarsTableRecognizer(screenshot, config)
    is_my_turn = recognizer.is_main_player_turn()
    # cv2.imshow('Computer Vision', screenshot)

    # if is_my_turn:
    #     print("It's my turn")

    # # detect table cards
    # table_cards = recognizer.detect_table_cards()
    # print(table_cards)
    #
    # # detect my cards
    # my_cards = recognizer.detect_hero_cards()
    # print(my_cards)

    new_pot = recognizer.find_total_pot()
    if new_pot == last_pot:
        pass
    else:
        screenshot = pyautogui.screenshot(region=(window.left, window.top, window.width, window.height))
        screenshot.save(f'pot_example_{count}.png')

        print('-' * 50)
        print(new_pot)
        print('change')
        print(count)
        print('-' * 50)

        last_pot = new_pot
        count += 1

    # end = time.time()
    # print(f'fps: {1 / (end - start) }')
