from hand_record import GameRecorder


if __name__ == '__main__':
    game_recorder = GameRecorder(conf_path='config2.yaml')
    # game_recorder.run(source='live', save_screenshot=True, save_2_db=True)
    game_recorder.run(source='test_games_screenshots/my_hand_history/multi_1696159106', debug=False, save_2_db=False)
