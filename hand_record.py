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


def adjust_windows():
    window_tutor = pygetwindow.getWindowsWithTitle('PokerNerd --Tutor Mode--')[0]
    window_tutor.moveTo(-10, 0)
    window_tutor.activate()

    window_game = pygetwindow.getWindowsWithTitle('No Limit')[0]
    window_game.resizeTo(2000, 1500)
    window_game.moveTo(510, 0)
    window_game.minimize()
    window_game.restore()


def save_dataframe_2_db(df, table_name):
    poker_db_dao = PokerDB()
    poker_db_dao.build_connection()
    poker_db_dao.append_df(df=df, table_name=table_name)
    poker_db_dao.close_connection()


def save_mapping_2_db(username, game_id):
    poker_db_dao = PokerDB()
    poker_db_dao.build_connection()
    poker_db_dao.save_user_game_mapping(username, game_id)
    poker_db_dao.close_connection()


def get_history_overview(df_history_detail, pnl, position):
    new_row = pd.DataFrame({
        'game_id': df_history_detail['game_id'].tolist()[-1],
        'position': position,
        'hole_cards': [df_history_detail['my_cards'].tolist()[-1]],
        'community_cards': [df_history_detail['table_cards'].tolist()[-1]],
        'pnl': pnl
    })
    # new_row['hole_cards'] = new_row['hole_cards'].apply(json.dumps)
    # new_row['community_cards'] = new_row['community_cards'].apply(json.dumps)

    return new_row


class ROUND(Enum):
    PRE_FLOP = 'Pre-Flop'
    FLOP = 'Flop'
    TURN = 'Turn'
    RIVER = 'River'


class GameRecorder:
    window_name = "Hold"

    def __init__(self, conf_path, username):
        self.username = username
        self.count = 0
        self.save_screenshot = None
        self.save_2_db = None
        self.mode = None
        self.config = read_config_file(filename=conf_path)
        self.column_names = ['game_id', 'round', 'player', 'position', 'action', 'number', 'pot_before',
                             'pot_after', 'stack_before', 'stack_after', 'my_cards', 'table_cards', 'equity']
        # 'stack_size', 'equity']
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
        pass

    def recognize_image(self, screenshot):
        recognizer = PokerStarsTableRecognizer(screenshot, self.config)
        if self.last_screen_shot is not None:
            recognizer_last = PokerStarsTableRecognizer(self.last_screen_shot, self.config)
        try:
            table_cards = recognizer.detect_table_cards()
            pot = recognizer.find_total_pot()

            # define round
            if not pot and self.new_game_start == 0:
                data = {
                    'method': 'clean'
                }
                trigger_update_strategy(data)

                # save last game history
                if self.game_id:
                    if self.stack_number_end is None:
                        self.stack_number_end = recognizer_last.detect_stack_number(mode=1)

                    pnl = int(self.stack_number_end) - int(self.stack_number_start)
                    print(f'Stack Number End: {self.stack_number_end}')
                    print(f'WinLoss: {pnl}')

                    # pd.set_option('display.max_rows', None)
                    # pd.set_option('display.max_columns', None)
                    # print(self.history)
                    if self.save_2_db:
                        self.history['my_cards'] = self.history['my_cards'].apply(json.dumps)
                        self.history['table_cards'] = self.history['table_cards'].apply(json.dumps)

                        save_mapping_2_db(username=self.username, game_id=self.game_id)

                        df_history_detail = self.history
                        print('saving history details')
                        print(df_history_detail)
                        save_dataframe_2_db(df=df_history_detail, table_name='history_detail')

                        df_history_overview = get_history_overview(df_history_detail, pnl, self.players_position[1])
                        print('saving history overview')
                        print(df_history_overview)
                        save_dataframe_2_db(df=df_history_overview, table_name='history_overview')

                # clean last game history
                self.history = pd.DataFrame(columns=self.column_names)
                self.count = 0
                self.new_game_start = 1
                self.game_id = None
                self.players_position = None
                self.round = None
                self.my_cards = []
                self.last_players_turn = None
                self.stack_number_start = None
                self.stack_number_end = None

                # new game starts
                print('=' * 50)
                print('New Game Starts!')

                # start new game
                self.game_id = int(time.time())
                if self.save_screenshot:
                    os.mkdir(f'test_games_screenshots/my_hand_history/{self.game_id}')
                self.round = ROUND.PRE_FLOP

                # record stack before
                self.stack_number_start = recognizer.detect_stack_number(mode=1)
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
                    trigger_update_strategy(data)

                self.last_table_cards = table_cards

            # check recording from the pre-flop instead of middle
            if self.game_id:
                players_turn = recognizer.detect_players_turn_()

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
                            trigger_update_strategy(data)

                    # trigger strategy
                    if len(self.my_cards) > 0 and self.start_strategy == 0:
                        self.start_strategy = 1
                        hero_cards = self.my_cards
                        table_cards = table_cards
                        deck = remove_cards(hero_cards, table_cards)
                        equity = 100 * (calc_equity(deck, hero_cards, table_cards)/100) ** 1.5
                        # print(f'Equity: {equity}')
                        if pot is None:
                            optimal_bet_amount = -666
                        else:
                            pot = int(pot)
                            if equity < 50:
                                if 0 < equity < 20:
                                    action = 'fold'
                                    optimal_bet_amount = None
                                    analysis = 'extremely weak hand'
                                else:
                                    action = 'bet'
                                    optimal_bet_amount = pot * 1/6  # pot * equity / (100 - 2 * equity)
                                    analysis = 'weak hand'
                            else:
                                action = 'bet'
                                if 50 <= equity < 65:
                                    optimal_bet_amount = 1/3 * pot
                                    analysis = 'strong hand'
                                else:
                                    optimal_bet_amount = pot
                                    analysis = 'extremely strong hand'

                        if optimal_bet_amount:
                            optimal_bet_amount = int(optimal_bet_amount)
                            if optimal_bet_amount < 100:
                                optimal_bet_amount = 100

                        # print(f'Action: {action}')
                        # print(f'Max Bet Amount: {optimal_bet_amount}')

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

                    data = {
                        'method': 'pot',
                        'pot': pot
                    }
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
                            if player == 1 and action == 'fold':
                                self.stack_number_end = recognizer_last.detect_stack_number(mode=1)
                                # self.stack_number_end = recognizer.detect_stack_number(mode=2)
                                print(f'Stack Number End: {self.stack_number_end}')

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
                    print(record)

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
                    new_row = pd.DataFrame(record, index=[0])
                    self.history = pd.concat([self.history, new_row], ignore_index=True)

                    del self.bet_record_queue[0]
            self.last_screen_shot = screenshot
        except Exception as Error:
            raise
            # print(Error)

    def run(self, source, debug=False, save_screenshot=False, save_2_db=False):
        self.save_2_db = save_2_db
        self.save_screenshot = save_screenshot
        self.mode = source
        if source == 'live':
            adjust_windows()
            time.sleep(1)
            while True:
                window = pygetwindow.getWindowsWithTitle(self.window_name)[0]
                screenshot_ = pyautogui.screenshot(region=(window.left, window.top, window.width, window.height))
                screenshot = np.array(screenshot_)
                screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
                self.recognize_image(screenshot)
                if self.save_screenshot and self.game_id:
                    screenshot_.save(f'test_games_screenshots/my_hand_history/{self.game_id}/{self.count}.png')
                    self.count += 1

        else:

            filenames = os.listdir(source)
            sorted_filenames = sorted(filenames, key=lambda x: int(x.split('.png')[0]))
            # print(sorted_filenames)

            for file in sorted_filenames:
                path = os.path.join(source, file)
                screenshot = cv2.imread(path)

                if debug:
                    cv2.imshow('Screenshot', screenshot)
                    key = cv2.waitKey(0)
                    if key == ord('q'):
                        break
                    cv2.destroyAllWindows()

                self.recognize_image(screenshot)
