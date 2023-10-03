from flask import Flask, request, render_template, jsonify
from flask_socketio import SocketIO
from database_controller import PokerDB
import random
import pandas as pd


app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")


@app.route('/')
def homepage():
    return render_template('homepage.html')


@app.route('/tutor.html')
def tutor_page():
    return render_template('tutor.html')


@app.route('/review.html')
def history_page():
    return render_template('review.html')


@app.route('/detail.html')
def detail_page():
    game_id = request.args.get('game_id')
    poker_db_dao = PokerDB()
    poker_db_dao.build_connection()
    detail = poker_db_dao.fetch_history_by_game_id(game_id)
    detail = detail[['round', 'player', 'position', 'action', 'number', 'pot_before', 'pot_after',
                     'stack_before', 'stack_after']]
    print(detail)
    print(detail.columns)
    table_html = detail.to_html()
    return render_template('detail.html', table_html=table_html)


@app.route('/game_ids')
def get_game_ids():
    poker_db_dao = PokerDB()
    poker_db_dao.build_connection()
    game_ids = poker_db_dao.fetch_game_id()
    poker_db_dao.close_connection()
    return jsonify(game_ids)


@app.route('/hand_history_overview')
def get_hand_history_overview():
    start = int(request.args.get('start'))
    end = int(request.args.get('end'))

    poker_db_dao = PokerDB()
    poker_db_dao.build_connection()
    df_history_overview = poker_db_dao.fetch_history_overview_by_timestamp(start, end)
    df_history_overview['pnl'] = df_history_overview['pnl'].apply(lambda x: x + random.randint(-5000, 5000))

    df_history_overview['game_id'] = df_history_overview['game_id'].astype(int)
    df_history_overview['datetime'] = pd.to_datetime(df_history_overview['game_id'], unit='s')
    df_history_overview['datetime'] = df_history_overview['datetime'].dt.tz_localize('UTC')
    df_history_overview['datetime'] = df_history_overview['datetime'].dt.tz_convert('Asia/Taipei')
    df_history_overview['details'] = df_history_overview['game_id']
    df_history_overview['details'] = df_history_overview['game_id'].apply(
        lambda x: f'<a href="detail.html?game_id={x}" target="_blank">Details</a>'
    )
    df_history_overview = df_history_overview[['datetime', 'position', 'hole_cards', 'community_cards', 'pnl', 'details']]
    print(df_history_overview)

    poker_db_dao.close_connection()
    table_html = df_history_overview.to_html(escape=False, index=False)
    return table_html


@app.route('/performance_history')
def get_performance_history():
    start = int(request.args.get('start'))
    end = int(request.args.get('end'))

    poker_db_dao = PokerDB()
    poker_db_dao.build_connection()
    df_history_overview = poker_db_dao.fetch_history_overview_by_timestamp(start, end)
    random.seed(1)
    df_history_overview['pnl'] = df_history_overview['pnl'].apply(lambda x: x + random.randint(-5000, 5000))
    df_history_overview['all_in_ev'] = df_history_overview['pnl'].apply(lambda x: x - random.randint(0, 500))
    print(df_history_overview)

    performance_json = {
        'pnl': df_history_overview['pnl'].tolist(),
        'all_in_ev': df_history_overview['all_in_ev'].tolist()
    }
    poker_db_dao.close_connection()
    return jsonify(performance_json)


@app.route('/hole_cards_performance')
def get_hole_cards_performance():
    def cards_category(cards):
        num1 = cards[0][0]
        num2 = cards[1][0]
        suit1 = cards[0][1]
        suit2 = cards[1][1]
        if num1 == num2:
            cat = num1 + num2
            return cat
        else:
            if num1 > num2:
                cat = num1 + num2
            else:
                cat = num2 + num1

            if suit1 == suit2:
                cat += 's'
            else:
                cat += 'o'
            return cat
    start = int(request.args.get('start'))
    end = int(request.args.get('end'))

    poker_db_dao = PokerDB()
    poker_db_dao.build_connection()
    df_history_overview = poker_db_dao.fetch_history_overview_by_timestamp(start, end)
    random.seed(1)
    df_history_overview['pnl'] = df_history_overview['pnl'].apply(lambda x: x + random.randint(-5000, 5000))
    df_history_overview['hole_cards_cat'] = df_history_overview['hole_cards'].apply(lambda x: cards_category(x))
    grouped_pnl = df_history_overview.groupby('hole_cards_cat')['pnl'].sum().reset_index()
    pnl_dict = grouped_pnl.set_index('hole_cards_cat')['pnl'].to_dict()

    return jsonify(pnl_dict)


@app.route('/position_performance')
def get_position_performance():
    start = int(request.args.get('start'))
    end = int(request.args.get('end'))
    poker_db_dao = PokerDB()
    poker_db_dao.build_connection()
    df_history_overview = poker_db_dao.fetch_history_overview_by_timestamp(start, end)
    random.seed(1)
    df_history_overview['pnl'] = df_history_overview['pnl'].apply(lambda x: x + random.randint(-5000, 5000))
    grouped_pnl = df_history_overview.groupby('position')['pnl'].sum().reset_index()
    grouped_pnl = grouped_pnl.sort_values(by='pnl', ascending=False).to_dict('list')
    # pnl_dict = grouped_pnl.set_index('position')['pnl'].to_dict()
    print(grouped_pnl)
    return jsonify(grouped_pnl)


@app.route('/trigger_update', methods=['post'])
def update_strategy():
    print('updating user interface')
    data = request.json
    print(f'data: {data}')
    socketio.emit('update_ui', data)
    return 'Updated!'


@socketio.on('connect')
def handle_connect():
    print('Client connected')


@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')


@socketio.on_error_default
def default_error_handler(e):
    print(f"Error: {str(e)}")


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=9000, debug=True, allow_unsafe_werkzeug=True)