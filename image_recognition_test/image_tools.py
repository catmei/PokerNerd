import yaml
import time
import pyautogui
import pygetwindow
import cv2
from image_class import ImageTools


def get_screenshot(name, interval=0.5):
    for i in range(10):
        window = pygetwindow.getWindowsWithTitle("No Limit Hold'em")[0]
        screenshot = pyautogui.screenshot(region=(window.left, window.top, window.width, window.height))
        screenshot.save(f'{name}_{i}.png')
        time.sleep(interval)


def resize_window(title, width, height):
    window = pygetwindow.getWindowsWithTitle(title)[0]  # Get the first window with the specified title
    if window:
        window.resizeTo(width, height)


if __name__ == "__main__":
    # filename = '../config.yaml'
    # with open(filename, 'r') as stream:
    #     config = yaml.safe_load(stream)

    # # get my turn and not my turn screenshot
    resize_window("Hold'em", 2000, 1200)
    get_screenshot("pot_example", interval=1)
    exit()

    # Initialize
    image = cv2.imread('images_for_test/screenshot_hero_cards.png')
    image_tool = ImageTools(image)
    image_tool.show_image()

    # image_tool.get_image_info()
    # print('-' * 100)

    # # get hsv image
    # hsv = image_tool.show_hsv()

    # get x0~x1 and y0~y1
    # image_tool.get_image_range()

    # save ROI
    # image_tool.get_image_range(save=True)

    # # show ROI
    # table_cards = config['table_cards']
    # # all cards
    # image_tool.show_roi(table_cards['y_0'], table_cards['y_1'], table_cards['x_0'], table_cards['x_1'])
    # # each cards
    # for i in range(1, 6):
    #     if i == 1:
    #         image_tool.show_roi(table_cards['y_0'], table_cards['y_1'], table_cards['x_0'], table_cards['x_0']+table_cards[f'separator_{i}'])
    #     else:
    #         image_tool.show_roi(table_cards['y_0'], table_cards['y_1'], table_cards['x_0'] + table_cards[f'separator_{i-1}'], table_cards['x_0']+table_cards[f'separator_{i}'])

