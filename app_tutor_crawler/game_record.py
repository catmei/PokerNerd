import os
import cv2
import time
import yaml
import json
import requests
import pyautogui
import pygetwindow
import numpy as np
import pandas as pd

from enum import Enum
from threading import Thread

from database.database_utils import PokerDB
from app_tutor_crawler.strategy.strategy import calc_equity, remove_cards, simple_strategy
from app_tutor_crawler.recognition.pokerstars_recognition import PokerStarsTableRecognizer


def adjust_windows(config):
    w_t = config['window']['tutor']
    window_tutor = pygetwindow.getWindowsWithTitle(w_t['title'])[0]
    window_tutor.moveTo(w_t['move_left'], w_t['move_top'])
    window_tutor.activate()

    w_g = config['window']['game']
    window_game = pygetwindow.getWindowsWithTitle(w_g['title'])[0]
    window_game.resizeTo(w_g['resize_width'], w_g['resize_height'])
    window_game.moveTo(w_g['move_left'], w_g['move_top'])
    window_game.minimize()
    window_game.restore()


def save_info_to_db(poker_db_dao, username, game_id, df_history_detail, df_history_overview):
    print('saving data to database')

    poker_db_dao.save_user_game_mapping(username=username, game_id=game_id)
    poker_db_dao.append_df(df=df_history_detail, table_name='history_detail')
    poker_db_dao.append_df(df=df_history_overview, table_name='history_overview')

    print('data saved to database')


def get_history_overview(df_history_detail, pnl, position, my_cards, table_cards):
    new_row = pd.DataFrame({
        'game_id': df_history_detail['game_id'].tolist()[-1],
        'position': position,
        'hole_cards': [my_cards],
        'community_cards': [table_cards],
        'pnl': pnl
    })

    new_row['hole_cards'] = new_row['hole_cards'].apply(json.dumps)
    new_row['community_cards'] = new_row['community_cards'].apply(json.dumps)

    return new_row


def trigger_update_strategy(data):
    url = "http://127.0.0.1:9001/trigger_update"

    payload = json.dumps(data)
    headers = {
        'Content-Type': 'application/json'
    }

    requests.request("POST", url, headers=headers, data=payload)


class ROUND(Enum):
    PRE_FLOP = 'Pre-Flop'
    FLOP = 'Flop'
    TURN = 'Turn'
    RIVER = 'River'


class GameRecorder:
    window_name = "Hold"

    def __init__(self, conf_path, username):
        with open(conf_path, 'r') as stream:
            self.config = yaml.safe_load(stream)
        self.db_dao = PokerDB()
        self.username = username
        self.count = 0
        self.save_screenshot = None
        self.save_2_db = None
        self.mode = None
        self.column_names = ['game_id', 'round', 'player', 'position', 'action', 'number', 'pot_before',
                             'pot_after', 'stack_before', 'stack_after', 'my_cards', 'table_cards', 'equity']
        self.history = pd.DataFrame(columns=self.column_names)

        self.new_game_start = 0
        self.game_id = None
        self.players_position = None
        self.round = None
        self.my_cards = []
        self.start_strategy = 0
        self.stack_number_start = None
        self.stack_number_end = None
        self.strategy = None

        self.last_screen_shot = None
        self.last_players_turn = None
        self.last_table_cards = []
        self.action_record_queue = []
        self.bet_record_queue = []

    def reset_game(self):
        self.history = pd.DataFrame(columns=self.column_names)
        self.count = 0
        self.new_game_start = 1
        self.game_id = None
        self.players_position = None
        self.round = None
        self.my_cards = []
        self.last_table_cards = []
        self.last_players_turn = None
        self.stack_number_start = None
        self.stack_number_end = None

    def recognize_image(self, screenshot):
        recognizer = PokerStarsTableRecognizer(screenshot, self.config)

        try:
            table_cards = recognizer.detect_table_cards()
            pot = recognizer.find_total_pot()

            # define round
            if (not pot or (len(table_cards) == 0 and len(self.last_table_cards) > 0)) and (self.new_game_start == 0):
                data = {
                    'method': 'clean'
                }
                if self.mode == 'live':
                    trigger_update_strategy(data)

                # save last game history
                if self.game_id:
                    if self.stack_number_end is None:
                        recognizer_last = PokerStarsTableRecognizer(self.last_screen_shot, self.config)
                        self.stack_number_end = recognizer_last.detect_stack_number()
                        print(f'Stack Number End: {self.stack_number_end}')

                    pnl = int(self.stack_number_end) - int(self.stack_number_start)
                    print(f'WinLoss: {pnl}')

                    if self.save_2_db:
                        self.history['my_cards'] = self.history['my_cards'].apply(json.dumps)
                        self.history['table_cards'] = self.history['table_cards'].apply(json.dumps)

                        df_history_detail = self.history
                        df_history_overview = get_history_overview(df_history_detail, pnl, self.players_position[1],
                                                                   self.my_cards, self.last_table_cards)

                        t = Thread(target=save_info_to_db,
                                   args=(
                                       self.db_dao, self.username, self.game_id, df_history_detail,
                                       df_history_overview
                                   ))
                        t.start()

                    if self.mode != 'live':
                        return self.history

                # clean last game history
                self.reset_game()

                # new game starts
                print('=' * 50)
                print('New Game Starts!')

                # start new game
                self.game_id = int(time.time())
                if self.save_screenshot:
                    os.mkdir(f'../test/images_for_integration_test/my_hand_history/{self.game_id}')
                self.round = ROUND.PRE_FLOP

                # record stack before
                self.stack_number_start = recognizer.detect_stack_number()
                print(f'Game ID: {self.game_id}')
                print(f'Stack Number Start: {self.stack_number_start}')

                print('-' * 50)
                print(f'Round: {self.round.value}')
                print(f'Table Cards: {table_cards}')

            elif pot and table_cards != self.last_table_cards:
                if len(table_cards) == 0:
                    pass
                else:
                    if len(table_cards) == 3 and len(self.last_table_cards) == 0:
                        # clean pre-flop players turn (BB or SB would repeat)
                        self.last_players_turn = 0
                        self.round = ROUND.FLOP
                        print('-' * 50)
                        print(f'Round: {self.round.value}')
                        print(f'Table Cards: {table_cards}')
                        print(f'My Cards: {self.my_cards}')

                    elif len(table_cards) == 4 and len(self.last_table_cards) == 3:
                        self.round = ROUND.TURN
                        print('-' * 50)
                        print(f'Round: {self.round.value}')
                        print(f'Table Cards: {table_cards}')
                        print(f'My Cards: {self.my_cards}')

                    elif len(table_cards) == 5 and len(self.last_table_cards) == 4:
                        self.round = ROUND.RIVER
                        print('-' * 50)
                        print(f'Round: {self.round.value}')
                        print(f'table cards: {table_cards}')
                        print(f'My Cards: {self.my_cards}')

                    data = {
                        'method': 'table-cards',
                        'table-cards': table_cards
                    }
                    if self.mode == 'live':
                        trigger_update_strategy(data)
                self.last_table_cards = table_cards

            # check recording from the pre-flop instead of middle
            if self.game_id:
                players_turn = recognizer.detect_players_turn()

                # strategy
                if players_turn == 1:
                    # record my cards
                    if len(self.my_cards) == 0:
                        my_cards = recognizer.detect_hero_cards()
                        if len(my_cards) == 2:
                            print(f'My Cards: {my_cards}')
                            self.my_cards = my_cards
                            data = {
                                'method': 'my-cards',
                                'my-cards': my_cards
                            }
                            if self.mode == 'live':
                                trigger_update_strategy(data)

                    # trigger strategy
                    if len(self.my_cards) > 0 and self.start_strategy == 0 and pot is not None:
                        self.stack_number_end = recognizer.detect_stack_number()
                        self.start_strategy = 1
                        hero_cards = self.my_cards
                        deck = remove_cards(hero_cards, table_cards)
                        equity = 100 * (calc_equity(deck, hero_cards, table_cards) / 100) ** 1.5

                        action, optimal_bet_amount, analysis = simple_strategy(pot, equity)

                        data = {
                            'method': 'strategy',
                            'action': action,
                            'amount': optimal_bet_amount,
                            'analysis': analysis,
                            'equity': f'{int(equity)} %'
                        }

                        self.strategy = data
                        self.strategy['equity'] = round(equity, 2)
                        print(f'strategy: {data}')

                        if self.mode == 'live':
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

                    data = {
                        'method': 'pot',
                        'pot': pot
                    }
                    if self.mode == 'live':
                        trigger_update_strategy(data)

                if len(self.action_record_queue) > 0:
                    action_job = self.action_record_queue[0]
                    player = action_job['player']

                    # check if player leave
                    is_empty = recognizer.check_is_player_empty(player)
                    if is_empty:
                        # print(f'player {player} leaves!')
                        action_job['action'] = 'leave'
                        self.bet_record_queue.append(action_job)
                        del self.action_record_queue[0]
                    else:
                        action = recognizer.detect_action(player=player)
                        if action:
                            if player == 1:
                                if action == 'fold':
                                    print(f'Stack Number End: {self.stack_number_end}')
                                else:
                                    self.stack_number_end = None

                            action_job['action'] = action
                            self.bet_record_queue.append(action_job)
                            # print(f'player_{player} action: {action}')
                            # print(f'bet queue: {self.bet_record_queue}')
                            del self.action_record_queue[0]

                            if self.new_game_start == 1:
                                players_info = recognizer.get_dealer_button_position()
                                players_info = recognizer.get_empty_seats(players_info)
                                players_info = recognizer.get_so_players(players_info)
                                self.players_position = recognizer.assign_positions(players_info)
                                print(f'Players Position: {self.players_position}')

                            self.new_game_start = 0

                if len(self.bet_record_queue) > 0:
                    bet_job = self.bet_record_queue[0]
                    player = bet_job['player']
                    number = recognizer.find_player_bet(player=player)
                    number = int(number) if number else number

                    pot = int(pot) if pot else pot

                    bet_job['number'] = number
                    bet_job['pot_after'] = pot
                    record = bet_job

                    record['game_id'] = self.game_id
                    record['my_cards'] = [self.my_cards]
                    record['table_cards'] = [table_cards]
                    record['position'] = self.players_position[record['player']]
                    record['stack_before'] = 0
                    record['stack_after'] = 0
                    record['equity'] = np.nan

                    if self.strategy is not None and player == 1:
                        record['equity'] = self.strategy['equity']
                        self.strategy = None

                    print(record)
                    new_row = pd.DataFrame(record, index=[0])
                    self.history = pd.concat([self.history, new_row], ignore_index=True)

                    del self.bet_record_queue[0]
            self.last_screen_shot = screenshot
        except Exception as Error:
            print(Error)
            raise

    def run(self, source, debug=False, save_screenshot=False, save_2_db=False):
        self.save_2_db = save_2_db
        self.save_screenshot = save_screenshot
        self.mode = source
        if source == 'live':
            adjust_windows(self.config)
            time.sleep(1)
            while True:
                window = pygetwindow.getWindowsWithTitle(self.window_name)[0]
                screenshot_ = pyautogui.screenshot(region=(window.left, window.top, window.width, window.height))
                screenshot = np.array(screenshot_)
                screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
                self.recognize_image(screenshot)
                if self.save_screenshot and self.game_id:
                    screenshot_.save(f'../test/images_for_integration_test/my_hand_history/{self.game_id}/{self.count}.png')
                    self.count += 1

        else:
            filenames = os.listdir(source)
            sorted_filenames = sorted(filenames, key=lambda x: int(x.split('.png')[0]))

            for file in sorted_filenames:
                path = os.path.join(source, file)
                screenshot = cv2.imread(path)

                if debug:
                    cv2.imshow('Screenshot', screenshot)
                    key = cv2.waitKey(0)
                    if key == ord('q'):
                        break
                    cv2.destroyAllWindows()

                df_history = self.recognize_image(screenshot)
                if df_history is not None:
                    return df_history

