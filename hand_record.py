import cv2
import numpy as np
import pandas as pd
import json
import pyautogui
import pygetwindow
from pokerstars_recognition import PokerStarsTableRecognizer
from utils import read_config_file
from database_controller import PokerDB
from strategy import calc_equity, remove_cards
from trigger_update_post import trigger_update_strategy
import time
from enum import Enum
import os
import uuid


def resize_window(title, width, height):
    window = pygetwindow.getWindowsWithTitle(title)[0]  # Get the first window with the specified title
    if window:
        window.resizeTo(width, height)


def position_windows():
    # adjust order
    window_tutor = pygetwindow.getWindowsWithTitle('PokerNerd --Tutor Mode--')[0]
    window_tutor.activate()

    window_game = pygetwindow.getWindowsWithTitle('Hold')[0]
    window_game.minimize()
    window_game.restore()

    if window_tutor:
        window_tutor.moveTo(-5, 0)

    if window_game:
        window_game.moveTo(510, 0)




def save_history(df_history, table_name='history'):
    poker_db_dao = PokerDB()
    poker_db_dao.build_connection()
    poker_db_dao.append_df(df=df_history, table_name=table_name)
    poker_db_dao.close_connection()


class ROUND(Enum):
    PRE_FLOP = 'Pre-Flop'
    FLOP = 'Flop'
    TURN = 'Turn'
    RIVER = 'River'


class GameRecorder:
    window_name = "Hold"

    def __init__(self, conf_path):
        self.save_2_db = None
        self.mode = None
        self.config = read_config_file(filename=conf_path)
        self.column_names = ['game_id', 'round', 'player', 'position', 'equity', 'action', 'number', 'pot_before',
                             'pot_after', 'stack_before', 'stack_after', 'my_cards', 'table_cards']
        # 'stack_size', 'my_cards', 'table_cards', 'equity']
        self.history = pd.DataFrame(columns=self.column_names)

        self.game_id = None
        self.players_position = None
        self.round = None
        self.my_cards = []
        self.start_strategy = 0

        self.last_pot = None
        self.last_players_bet = None
        self.last_players_turn = None
        self.last_table_cards = []
        self.action_record_queue = []
        self.bet_record_queue = []

    def reset_game(self):
        pass

    def recognize_image(self, recognizer):
        try:
            table_cards = recognizer.detect_table_cards()
            # print(table_cards)
            pot = recognizer.find_total_pot()

            # if len(self.last_table_cards) == 0:
            #     self.last_table_cards = table_cards

            # define round
            if table_cards != self.last_table_cards:
                if len(table_cards) == 0 and len(self.last_table_cards) >= 2:
                    # save and clean last game history
                    if self.game_id:
                        print(self.history)
                        self.history['my_cards'] = self.history['my_cards'].apply(json.dumps)
                        self.history['table_cards'] = self.history['table_cards'].apply(json.dumps)
                        if self.save_2_db:
                            save_history(df_history=self.history)
                        self.history = pd.DataFrame(columns=self.column_names)

                    print('=' * 50)
                    print('New Game Starts!')
                    # New Game Starts
                    self.game_id = None
                    self.players_position = None
                    self.round = None
                    self.last_pot = None
                    self.last_players_bet = None
                    self.last_players_turn = None

                    # start new game
                    self.game_id = int(time.time())
                    self.round = ROUND.PRE_FLOP

                    players_info = recognizer.get_dealer_button_position()
                    players_info = recognizer.get_empty_seats(players_info)
                    players_info = recognizer.get_so_players(players_info)
                    self.players_position = recognizer.assign_positions(players_info)

                    print(f'Game ID: {self.game_id}')
                    print(f'Players Position: {self.players_position}')
                    print('-' * 50)
                    print(f'Round: {self.round.value}')
                    print(f'table cards: {table_cards}')

                elif len(table_cards) == 3 and len(self.last_table_cards) == 0:
                    # clean pre-flop players turn (BB or SB would repeat)
                    self.last_players_turn = 0
                    self.round = ROUND.FLOP
                    print('-' * 50)
                    print(f'Round: {self.round.value}')
                    print(f'table cards: {table_cards}')

                elif len(table_cards) == 4 and len(self.last_table_cards) == 3:
                    self.round = ROUND.TURN
                    print('-' * 50)
                    print(f'Round: {self.round.value}')
                    print(f'table cards: {table_cards}')

                elif len(table_cards) == 5 and len(self.last_table_cards) == 4:
                    self.round = ROUND.RIVER
                    print('-' * 50)
                    print(f'Round: {self.round.value}')
                    print(f'table cards: {table_cards}')

                self.last_table_cards = table_cards

            else:
                pass

            # check recording from the pre-flop instead of middle
            if self.players_position:
                players_turn = recognizer.detect_players_turn_()

                # strategy
                if players_turn == 1:
                    # record my cards
                    if len(self.my_cards) == 0:
                        my_cards = recognizer.detect_hero_cards()
                        if len(my_cards) == 2:
                            print(f'My Cards: {my_cards}')
                            self.my_cards = my_cards

                    # trigger strategy
                    if len(self.my_cards) > 0 and self.start_strategy == 0:
                        self.start_strategy = 1
                        hero_cards = self.my_cards
                        table_cards = table_cards
                        deck = remove_cards(hero_cards, table_cards)
                        equity = calc_equity(deck, hero_cards, table_cards)
                        print(f'Equity: {equity}')
                        if pot is None:
                            print(self.round)
                            print(players_turn)
                        optimal_bet_amount = int(pot) * equity / (100 - equity)
                        print(f'Max Bet Amount: {optimal_bet_amount}')

                        data = {
                            'action': 'call',
                            'amount': optimal_bet_amount,
                            'analysis': 'strong hand',
                            'equity': equity
                        }

                        # if self.mode == 'live':
                        trigger_update_strategy(data)

                if self.start_strategy == 1 and players_turn != 1:
                    self.start_strategy = 0

                if players_turn != self.last_players_turn and players_turn != 0:
                    pot = int(pot) if pot else pot
                    self.action_record_queue.append({
                        'round': self.round.value,
                        'player': players_turn,
                        'pot_before': pot,
                    })
                    # print(f'turn: {players_turn}')
                    # print(f'action queue: {self.action_record_queue}')
                    self.last_players_turn = players_turn

                if len(self.action_record_queue) > 0:
                    action_job = self.action_record_queue[0]
                    player = action_job['player']
                    action = recognizer.detect_action(player=player)
                    if action:
                        action_job['action'] = action
                        self.bet_record_queue.append(action_job)
                        # print(f'player_{player} action: {action}')
                        # print(f'bet queue: {self.bet_record_queue}')
                        del self.action_record_queue[0]

                if len(self.bet_record_queue) > 0:
                    bet_job = self.bet_record_queue[0]
                    player = bet_job['player']
                    number = recognizer.find_player_bet(player=player)
                    number = int(number) if number else number

                    pot = int(pot) if pot else pot

                    bet_job['number'] = number
                    bet_job['pot_after'] = pot
                    record = bet_job
                    print(record)

                    record['game_id'] = self.game_id
                    record['my_cards'] = [self.my_cards]
                    record['table_cards'] = [table_cards]
                    record['position'] = 'test'
                    record['stack_before'] = 0
                    record['stack_after'] = 0
                    new_row = pd.DataFrame(record, index=[0])
                    self.history = pd.concat([self.history, new_row], ignore_index=True)

                    del self.bet_record_queue[0]

        except Exception as Error:
            raise
            # print(Error)

    def run(self, source, debug=False, save_screenshot=False, save_2_db=False):
        self.save_2_db = save_2_db
        self.mode = source
        count = 0
        if source == 'live':
            resize_window('Hold', 2000, 1500)
            position_windows()
            time.sleep(1)
            while True:
                window = pygetwindow.getWindowsWithTitle(self.window_name)[0]
                screenshot = pyautogui.screenshot(region=(window.left, window.top, window.width, window.height))
                if save_screenshot:
                    screenshot.save(f'test_games_screenshots/screenshot_{count}.png')
                count += 1
                screenshot = np.array(screenshot)
                screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
                recognizer = PokerStarsTableRecognizer(screenshot, self.config)
                self.recognize_image(recognizer)
        else:

            filenames = os.listdir(source)
            sorted_filenames = sorted(filenames, key=lambda x: int(x.split('_')[1].split('.png')[0]))

            for file in sorted_filenames:
                path = os.path.join(source, file)
                screenshot = cv2.imread(path)

                if debug:
                    cv2.imshow('Screenshot', screenshot)
                    key = cv2.waitKey(0)
                    if key == ord('q'):
                        break
                    cv2.destroyAllWindows()

                recognizer = PokerStarsTableRecognizer(screenshot, self.config)
                self.recognize_image(recognizer)
