import os
from dotenv import load_dotenv
from app_tutor_crawler.game_record import GameRecorder


def test_full_game_recognition():
    load_dotenv()
    USERNAME = os.getenv('POKER_GAME_USERNAME')
    game_recorder = GameRecorder(conf_path='../config.yaml', username=USERNAME)
    df_history = game_recorder.run(
        source='images_for_integration_test/test_game',
        debug=False,
        save_2_db=False
    )

    df_history.drop(['game_id', 'equity'], axis=1, inplace=True)

    dict_test = df_history.to_dict()
    dict_answer = {'round': {0: 'Pre-Flop', 1: 'Pre-Flop', 2: 'Pre-Flop', 3: 'Flop', 4: 'Flop', 5: 'Flop', 6: 'Flop',
                             7: 'Flop', 8: 'Flop', 9: 'Flop', 10: 'Turn', 11: 'Turn', 12: 'Turn', 13: 'Turn', 14: 'Turn',
                             15: 'River', 16: 'River'},
                   'player': {0: 1, 1: 2, 2: 4, 3: 2, 4: 4, 5: 6, 6: 1, 7: 2, 8: 4, 9: 6, 10: 4, 11: 6, 12: 1, 13: 4, 14: 6,
                              15: 4, 16: 1},
                   'position': {0: 'BTN', 1: 'SB', 2: 'BB', 3: 'SB', 4: 'BB', 5: 'CO', 6: 'BTN', 7: 'SB', 8: 'BB', 9: 'CO',
                                10: 'BB', 11: 'CO', 12: 'BTN', 13: 'BB', 14: 'CO', 15: 'BB', 16: 'BTN'},
                   'action': {0: 'call', 1: 'call', 2: 'check', 3: 'call', 4: 'check', 5: 'check', 6: 'bet', 7: 'fold',
                              8: 'call', 9: 'call', 10: 'check', 11: 'check', 12: 'bet', 13: 'call', 14: 'fold', 15: 'bet',
                              16: 'call'},
                   'number': {0: 100, 1: 100, 2: None, 3: None, 4: None, 5: None, 6: 378, 7: None, 8: 378, 9: None,
                              10: None, 11: None, 12: 1500, 13: 1500, 14: None, 15: 7922, 16: 7922},
                   'pot_before': {0: 250, 1: 350, 2: 400, 3: 378, 4: 378, 5: 378, 6: 378, 7: 756, 8: 756, 9: 1134, 10: 1450,
                                  11: 1450, 12: 1450, 13: 2950, 14: 4450, 15: 4285, 16: 12207},
                   'pot_after': {0: 350, 1: 400, 2: 378, 3: 378, 4: 378, 5: 378, 6: 756, 7: 756, 8: 1134, 9: 1450, 10: 1450,
                                 11: 1450, 12: 2950, 13: 4450, 14: 4285, 15: 12207, 16: 20129},
                   'stack_before': {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0,
                                    14: 0, 15: 0, 16: 0},
                   'stack_after': {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0,
                                   14: 0, 15: 0, 16: 0},
                   'my_cards': {0: ['Kc', 'Qd'], 1: ['Kc', 'Qd'], 2: ['Kc', 'Qd'], 3: ['Kc', 'Qd'], 4: ['Kc', 'Qd'],
                                5: ['Kc', 'Qd'], 6: ['Kc', 'Qd'], 7: ['Kc', 'Qd'], 8: ['Kc', 'Qd'], 9: ['Kc', 'Qd'],
                                10: ['Kc', 'Qd'], 11: ['Kc', 'Qd'], 12: ['Kc', 'Qd'], 13: ['Kc', 'Qd'], 14: ['Kc', 'Qd'],
                                15: ['Kc', 'Qd'], 16: ['Kc', 'Qd']},
                   'table_cards': {0: [], 1: [], 2: ['6d', 'Ks', '7c'], 3: ['6d', 'Ks', '7c'], 4: ['6d', 'Ks', '7c'],
                                   5: ['6d', 'Ks', '7c'], 6: ['6d', 'Ks', '7c'], 7: ['6d', 'Ks', '7c'],
                                   8: ['6d', 'Ks', '7c'], 9: ['6d', 'Ks', '7c', '3s'], 10: ['6d', 'Ks', '7c', '3s'],
                                   11: ['6d', 'Ks', '7c', '3s'], 12: ['6d', 'Ks', '7c', '3s'], 13: ['6d', 'Ks', '7c', '3s'],
                                   14: ['6d', 'Ks', '7c', '3s', 'Ah'], 15: ['6d', 'Ks', '7c', '3s', 'Ah'],
                                   16: ['6d', 'Ks', '7c', '3s', 'Ah']}}

    assert dict_test == dict_answer

