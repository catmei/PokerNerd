from hand_record import GameRecorder


if __name__ == '__main__':
    username = 'catvin666'
    game_recorder = GameRecorder(conf_path='config2.yaml', username=username)
    game_recorder.run(source='live', save_screenshot=True, save_2_db=True)
    # game_recorder.run(source='test_games_screenshots/my_hand_history/1696388635', debug=False, save_2_db=False)
