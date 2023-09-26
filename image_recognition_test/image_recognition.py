import yaml
import pyautogui
import os
import cv2
from image_class import ImageTest


if __name__ == "__main__":
    filename = '../config2.yaml'
    with open(filename, 'r') as stream:
        config = yaml.safe_load(stream)

    # Initialize
    image = cv2.imread(r'C:\Users\b0220\Documents\data_engineering\PokerNerd\main\images\game1\screenshot_261.png')
    image_test = ImageTest(image, config)
    image_test.show_image()

    # # is my turn
    # result = image_test.is_main_player_turn()
    # print(f'is my turn?: {result}')

    # # detect turn
    # players_turn = image_test.detect_players_turn()
    # print(players_turn)

    # count_white
    # player_turn = image_test.detect_players_turn_()
    # print(player_turn)

    # # detect table cards
    # table_cards = image_test.detect_table_cards()
    # print(table_cards)

    # detect action
    action = image_test.detect_action(player=3)
    print(action)

    # # detect my cards
    # my_cards = image_test.detect_hero_cards()
    # print(my_cards)

    # # find dealer
    # image = cv2.imread('bet_image/bet_all.png')
    # image_test = ImageTest(image, config)
    # image_test.show_image()
    # players_info = image_test.get_dealer_button_position()
    # print(players_info)
    #
    # # find empty seat
    # players_info = image_test.get_empty_seats(players_info)
    # print(players_info)
    #
    # # find sitting out players
    # players_info = image_test.get_so_players(players_info)
    # print(players_info)
    #
    # players_info = image_test.assign_positions(players_info)
    # print(players_info)
    #
    # players_info = image_test.find_players_bet_(players_info)
    # print(players_info)
    # exit()

    # # find bet by player
    # for i in range(1,7):
    #     player_bet = image_test.find_player_bet(player=i)
    #     print(player_bet)


    # # detect total pot cards
    # total_pot = image_test.find_total_pot()
    # print(total_pot)

    # # test pot
    # dir = 'images_for_test_2'
    #
    # for i in range(109):
    #     print(i)
    #
    #     image = cv2.imread(f'{dir}/pot_example_{i}.png')
    #     image_test = ImageTest(image, config)
    #     image_test.show_image()
    #
    #     total_pot = image_test.find_total_pot()
    #     print(total_pot)
    #     print('-'*50)
    #
    # exit()
    #
    # dir = 'to_be_trained_others'
    #
    # all_files_and_directories = os.listdir(dir)
    # print(all_files_and_directories)
    # for i in all_files_and_directories:
    #     print(i)
    #
    #     image = cv2.imread(f'{dir}/{i}')
    #     image_test = ImageTest(image, config)
    #     image_test.show_image()
    #
    #     total_pot = image_test.find_total_pot()
    #     print(total_pot)
    #     print('-'*50)