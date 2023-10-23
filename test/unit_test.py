import cv2
import yaml
from app_tutor_crawler.recognition.pokerstars_recognition import PokerStarsTableRecognizer


with open('../config.yaml', 'r') as stream:
    CONFIG = yaml.safe_load(stream)


def test_detect_players_turn():
    image = cv2.imread(r'images_for_unit_test\player_turn\1.png')
    recognizer = PokerStarsTableRecognizer(img=image, cfg=CONFIG)
    assert recognizer.detect_players_turn() == 1


def test_detect_action():
    image = cv2.imread(r'images_for_unit_test\player_action\5_call.png')
    recognizer = PokerStarsTableRecognizer(img=image, cfg=CONFIG)
    assert recognizer.detect_action(player=5) == 'call'


def test_detect_table_cards():
    image = cv2.imread(r'images_for_unit_test\table_cards\Th_3c_As_7s_Jc.png')
    recognizer = PokerStarsTableRecognizer(img=image, cfg=CONFIG)
    assert recognizer.detect_table_cards() == ['Th', '3c', 'As', '7s', 'Jc']


def test_detect_hero_cards():
    image = cv2.imread(r'images_for_unit_test\hero_cards\7h_2c.png')
    recognizer = PokerStarsTableRecognizer(img=image, cfg=CONFIG)
    assert recognizer.detect_hero_cards() == ['7h', '2c']


def test_find_total_pot():
    image = cv2.imread(r'images_for_unit_test\total_pot\14834.png')
    recognizer = PokerStarsTableRecognizer(img=image, cfg=CONFIG)
    assert recognizer.find_total_pot() == '14834'


def test_detect_stack_number():
    image = cv2.imread(r'images_for_unit_test\stack_number\4741.png')
    recognizer = PokerStarsTableRecognizer(img=image, cfg=CONFIG)
    assert recognizer.detect_stack_number() == '4741'


def test_find_player_bet():
    image = cv2.imread(r'images_for_unit_test\player_bet\3_2413.png')
    recognizer = PokerStarsTableRecognizer(img=image, cfg=CONFIG)
    assert recognizer.find_player_bet(3) == '2413'

