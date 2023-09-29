from hand_record import GameRecorder
import time


if __name__ == '__main__':
    # time.sleep(5)
    game_recorder = GameRecorder(conf_path='config2.yaml')
    game_recorder.run(source='live', save_screenshot=False, save_2_db=True)
    # game_recorder.run(source='test_games_screenshots/my_hand_history/game1', debug=False, save_2_db=True)
