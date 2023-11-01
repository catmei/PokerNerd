import os
from dotenv import load_dotenv
from game_record import GameRecorder


if __name__ == '__main__':
    load_dotenv()
    USERNAME = os.getenv('POKER_GAME_USERNAME')
    game_recorder = GameRecorder(conf_path='../config.yaml', username=USERNAME)

    # run by the live game
    game_recorder.run(
        source='live',
        save_screenshot=False,
        save_2_db=True
    )

    # run by the history screenshots
    # game_recorder.run(
    #     source='../test/images_for_integration_test/test_game',
    #     debug=False,
    #     save_2_db=False
    # )
