import os
from dotenv import load_dotenv
from game_record import GameRecorder


if __name__ == '__main__':
    load_dotenv()
    USERNAME = os.getenv('POKER_GAME_USERNAME')
    game_recorder = GameRecorder(conf_path='../config.yaml', username=USERNAME)

    # game_recorder.run(
    #     source='live',
    #     save_screenshot=True,
    #     save_2_db=True
    # )

    game_recorder.run(
        source='../test/images_for_integration_test/my_hand_history/1697982276',
        debug=False,
        save_2_db=False
    )
