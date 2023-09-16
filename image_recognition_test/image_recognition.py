import yaml
import pyautogui
import cv2
from image_class import ImageTest


if __name__ == "__main__":
    filename = '../config.yaml'
    with open(filename, 'r') as stream:
        config = yaml.safe_load(stream)

    # Initialize
    # image = cv2.imread('images_for_test/pot_example_0.png')
    # image_test = ImageTest(image, config)
    # image_test.show_image()

    # # is my turn
    # result = image_test.is_main_player_turn()
    # print(f'is my turn?: {result}')
    # image_test.show_image()
    #
    # # detect table cards
    # table_cards = image_test.detect_table_cards()
    # print(table_cards)
    #
    # # detect my cards
    # my_cards = image_test.detect_hero_cards()
    # print(my_cards)

    # # detect total pot cards
    # total_pot = image_test.find_total_pot()
    # print(total_pot)

    # test pot
    for i in range(14):
        image = cv2.imread(f'images_for_test/pot_example_{i}.png')
        image_test = ImageTest(image, config)
        image_test.show_image()

        total_pot = image_test.find_total_pot( )
        print(total_pot)