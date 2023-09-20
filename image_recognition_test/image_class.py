import cv2
import numpy as np
from main.utils import sort_bboxes, thresholding, card_separator, table_part_recognition, convert_contours_to_bboxes, find_by_template, find_closer_point


class ImageTest:
    def __init__(self, img, cfg):
        self.img = img
        self.cfg = cfg

    def is_main_player_turn(self):
        # image [y0: y1, x0: x1]
        res_img = self.img[self.cfg['hero_step_define']['y_0']:self.cfg['hero_step_define']['y_1'],
                           self.cfg['hero_step_define']['x_0']:self.cfg['hero_step_define']['x_1']]

        hsv_img = cv2.cvtColor(res_img, cv2.COLOR_BGR2HSV_FULL)
        self.show_image(hsv_img)
        mask = cv2.inRange(hsv_img, np.array([0, 5, 50]), np.array([179, 10, 255]))
        self.show_image(mask)
        count_of_white_pixels = cv2.countNonZero(mask)
        print(f'count_of_white_pixels: {count_of_white_pixels}')

        return True if count_of_white_pixels > self.cfg['hero_step_define']['min_white_pixels'] else False

    def detect_cards(self, separators, sort_bboxes_method, cards_coordinates, path_to_numbers, path_to_suits):
        """
        Parameters:
            separators(list of int): contains values where the card ends
            sort_bboxes_method(str): defines how we will sort the contours.
            It can be left-to-right, bottom-to-top, top-to-bottom
            cards_coordinates(str): path to cards coordinates
            path_to_numbers(str): path where located numbers (J, K etc.)
            path_to_suits(str) : path where located suits
        Returns:
            cards_name(list of str): name of the cards
        """
        cards_name = []
        img = self.img[self.cfg[cards_coordinates]['y_0']:self.cfg[cards_coordinates]['y_1'],
                       self.cfg[cards_coordinates]['x_0']:self.cfg[cards_coordinates]['x_1']]
        binary_img = thresholding(img, 200, 255)
        # self.show_image(binary_img)

        contours, _ = cv2.findContours(binary_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # Draw the contours on the image.
        img_with_contours = cv2.drawContours(img.copy(), contours, -1, (255, 0, 0), 2)
        self.show_image(img_with_contours)

        # bboxes width have to > 10 and height > 30
        bounding_boxes = convert_contours_to_bboxes(contours, 20, 4)
        bounding_boxes = sort_bboxes(bounding_boxes, method=sort_bboxes_method)
        self.show_image_with_boxes(img, bounding_boxes)
        cards_bboxes_dct = card_separator(bounding_boxes, separators)
        print(cards_bboxes_dct)
        for _, cards_bboxes in cards_bboxes_dct.items():
            if len(cards_bboxes) == 3:
                cards_bboxes = [cards_bboxes[0]]

            elif len(cards_bboxes) == 0:
                return []

            elif len(cards_bboxes) > 3:
                raise ValueError("The number of bounding boxes should not be more than 3!")

            card_name = ''
            for key, bbox in enumerate(cards_bboxes):
                color_of_img, directory = (cv2.IMREAD_COLOR, self.cfg['paths'][path_to_suits]) if key == 0 \
                    else (cv2.IMREAD_GRAYSCALE, self.cfg['paths'][path_to_numbers])
                res_img = img[bbox[1]:bbox[3], bbox[0]:bbox[2]]
                card_part = table_part_recognition(res_img, directory, color_of_img)
                print(card_part)
                print('--------------------------------')
                card_name = card_part + 'T' if len(cards_bboxes) == 1 else card_name + card_part
            cards_name.append(card_name[::-1])
        return cards_name

    def detect_hero_cards(self):
        """
        Returns:
            cards_name(list of str): name of the hero's cards
        """
        separators = [self.cfg['hero_cards']['separator_1'], self.cfg['hero_cards']['separator_2']]
        sort_bboxes_method = 'bottom-to-top'
        cards_coordinates = 'hero_cards'
        path_to_numbers = 'hero_cards_numbers'
        path_to_suits = 'hero_cards_suits'
        cards_name = self.detect_cards(separators, sort_bboxes_method, cards_coordinates,
                                       path_to_numbers, path_to_suits)
        return cards_name

    def detect_table_cards(self):
        """
        Returns:
            cards_name(list of str): name of the cards on the table
        """
        separators = [self.cfg['table_cards']['separator_1'], self.cfg['table_cards']['separator_2'],
                      self.cfg['table_cards']['separator_3'], self.cfg['table_cards']['separator_4'],
                      self.cfg['table_cards']['separator_5']]
        sort_bboxes_method = 'top-to-bottom'
        cards_coordinates = 'table_cards'
        path_to_numbers = 'table_cards_numbers'
        path_to_suits = 'table_cards_suits'
        cards_name = self.detect_cards(separators, sort_bboxes_method, cards_coordinates,
                                       path_to_numbers, path_to_suits)
        return cards_name

    def find_total_pot(self):
        """
        Returns:
            number(str): number with total pot
        """
        img = self.img[self.cfg['pot']['y_0']:self.cfg['pot']['y_1'],
              self.cfg['pot']['x_0']:self.cfg['pot']['x_1']]

        self.show_image(img, zoom_in=True)

        max_val, max_loc = find_by_template(img, self.cfg['paths']['pot_image'])
        print(f'highest correlation value: {max_val}')

        bet_img = img[max_loc[1] - 3:max_loc[1] + self.cfg['pot']['height'],
                      max_loc[0] + self.cfg['pot']['pot_template_width']:
                      max_loc[0] + self.cfg['pot']['pot_template_width'] + self.cfg['pot']['width']]
        binary_img = thresholding(bet_img, self.cfg['pot']['value_1'], self.cfg['pot']['value_2'])
        self.show_image(binary_img, zoom_in=True)

        # kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        # eroded = cv2.erode(binary_img, kernel, iterations=1)
        # self.show_image(eroded, zoom_in=True)

        contours, _ = cv2.findContours(binary_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        self.show_image_with_contours(bet_img, contours)

        bounding_boxes = convert_contours_to_bboxes(contours, self.cfg['pot']['min_height'], self.cfg['pot']['min_width'])
        print(f"boxes count: {len(bounding_boxes)}")
        self.show_image_with_boxes(bet_img, bounding_boxes)

        bounding_boxes = sort_bboxes(bounding_boxes, method='left-to-right')

        number = ''
        for bbox in bounding_boxes:
            number_img = bet_img[bbox[1]:bbox[3], bbox[0]:bbox[2]]
            symbol = table_part_recognition(number_img, self.cfg['paths']['pot_numbers'], cv2.IMREAD_GRAYSCALE)
            number += symbol
        return number

    def get_dealer_button_position(self):
        """
        determine who is closer to the dealer button
        Returns:
            player_info(dict): here is information about all players as it becomes available
        """
        player_info = {key: value for key in range(1, 7) for value in ['']}
        players_coordinates = self.cfg['player_center_coordinates']
        _, button_coordinates = find_by_template(self.img, self.cfg['paths']['dealer_button'])
        player_with_button = find_closer_point(players_coordinates, button_coordinates)
        player_info[player_with_button] = 'dealer_button'
        return player_info

    def get_missing_players(self, players_info, path_to_template_img, flag):
        """
        find players who are currently absent for various reasons
        Parameters:
            players_info(dict): key - player number, value - '' - if the player is in the game;
            '-' - if a player's seat is available; '-so-' - if the player is absent
            path_to_template_img(str): the path to the images where the benchmark images are located
            flag(str): It can be - and -so-
        Returns:
           players_info(dict): info about players
        """
        players_coordinates = self.cfg['players_coordinates']
        players_for_checking = [key for key, value in players_info.items() if value == '']
        for player, bbox in players_coordinates.items():
            if player != 1 and player in players_for_checking:
                player_img = self.img[bbox[1]:bbox[3], bbox[0]:bbox[2]]
                max_val, _ = find_by_template(player_img, self.cfg['paths'][path_to_template_img])

                print(f'player: {player}, max_val: {max_val}')
                if max_val > 0.8:
                    players_info[player] = flag
        return players_info

    def get_empty_seats(self, players_info):
        """
        find players whose places are currently vacant
        """
        path_to_template_img = 'empty_seat'
        flag = '-'
        players_info = self.get_missing_players(players_info, path_to_template_img, flag)
        return players_info

    def get_so_players(self, players_info):
        """
        find players who are not currently in the game
        """
        path_to_template_img = 'sitting_out'
        flag = '-so-'
        players_info = self.get_missing_players(players_info, path_to_template_img, flag)
        return players_info

    def assign_positions(self, players_info):
        """
        assign each player one of six positions if the player in the game
        Parameters:
            players_info(dict): info about players in {1:'', 2: 'dealer_button',3:'-so-' etc. } format
        Returns:
            players_info(dict): info about players in {1: 'BB', 2: 'SB', 3: '-so-' etc. } format
        """
        busy_seats = [k for k, v in players_info.items() if v != '-' and v != '-so-']
        exist_positions = ['BTN', 'SB', 'BB', 'UTG', 'MP', 'CO']
        del exist_positions[3:3 + (6 - len(busy_seats))]
        player_with_button = [k for k, v in players_info.items() if v == 'dealer_button'][0]
        for index, player_number in enumerate(
                busy_seats[busy_seats.index(player_with_button):] + busy_seats[:busy_seats.index(player_with_button)]):
            if len(busy_seats) == 2:
                position = 'SB' if index == 0 else 'BB'
                players_info[player_number] = position
            else:
                players_info[player_number] = exist_positions[index]
        return players_info

    def show_image_with_contours(self, img, contours):
        img_with_contours = cv2.drawContours(img.copy(), contours, -1, (255, 0, 0), 1)
        self.show_image(img_with_contours, zoom_in=True)

    def show_image_with_boxes(self, img, bounding_boxes):
        # Draw the bounding boxes on the image
        for bbox in bounding_boxes:
            x0, y0, x1, y1 = bbox
            cv2.rectangle(img, (x0, y0), (x1, y1), (0, 255, 0), 2)
        self.show_image(img, zoom_in=True)

    def show_image(self, img=None, zoom_in=False):
        if img is None:
            img = self.img

        if zoom_in:
            if len(img.shape) == 2:
                height, width = img.shape
            elif len(img.shape) == 3:
                height, width, channels = img.shape

            factor = 1600 / width
            width = 1600
            height = int(height * factor)
            img = cv2.resize(img.copy(), (width, height))

        cv2.imshow('Image', img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()



class ImageTools:
    def __init__(self, img):
        self.img = img

    def get_image_info(self):
        # Get image shape
        height, width, channels = self.img.shape

        # Determine if the image is grayscale or colored
        if channels == 1:
            color_mode = "Grayscale"
        elif channels == 3:
            color_mode = "Colored"
        else:
            color_mode = "Unknown"

        # Get image datatype
        data_type = self.img.dtype

        # Display the information
        print(f"Image Width: {width}")
        print(f"Image Height: {height}")
        print(f"Width/Height: {width / height}")
        print(f"Number of Channels: {channels}")
        print(f"Color Mode: {color_mode}")
        print(f"Data Type: {data_type}")

        # Optionally, to get the total number of pixels
        total_pixels = self.img.size
        print(f"Total Pixels: {total_pixels}")

    def show_hsv(self):
        hsv_img = cv2.cvtColor(self.img, cv2.COLOR_BGR2HSV_FULL)
        self.show_image(hsv_img)

    def get_image_range(self, save=False, resize=1):
        # Let the user manually select the ROI
        new_width = int(self.img.shape[1]*resize)
        new_height = int(self.img.shape[0]*resize)
        resized_img = cv2.resize(self.img.copy(), (new_width, new_height))

        r = cv2.selectROI(resized_img)

        # Print the selected region's coordinates and dimensions
        print(f"X Range: {r[0]} to {r[0] + r[2]}")
        print(f"Y Range: {r[1]} to {r[1] + r[3]}")

        cv2.destroyAllWindows()

        if save:
            filename = input("Enter the file name") + '.png'
            cv2.imwrite(filename, resized_img[r[1]: r[1] + r[3], r[0]: r[0] + r[2]])

    def show_roi(self, y0, y1, x0, x1):
        ROI = self.img[y0:y1, x0:x1]
        self.show_image(ROI)

    def show_image(self, img=None):
        if img is None:
            img = self.img
        cv2.imshow('Image', img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

