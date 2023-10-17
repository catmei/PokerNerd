from flask import Flask, request, render_template, jsonify, redirect, url_for
from flask_socketio import SocketIO
from database_controller import PokerDB
import random
import numpy as np
import pandas as pd
import jwt
import hashlib
import time
import math
import os
from dotenv import load_dotenv

load_dotenv()
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")


@app.route('/')
def homepage():
    return render_template('homepage.html')


@app.route('/tutor.html')
def tutor_page():
    return render_template('tutor.html')


@app.route('/tutor_demo.html')
def tutor_demo_page():
    return render_template('tutor_demo.html')


def verify_jwt_token():
    auth_header = request.headers.get('Authorization')

    if auth_header:
        token = auth_header.split(" ")[1]  # Extract token from Bearer
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
            print("Verified token")
            return {
                'valid': True,
                'payload': payload
            }, 200

        except jwt.ExpiredSignatureError:
            print("Expired token")
            return {
                'valid': False,
                'error': 'Token has expired'
            }, 401

        except jwt.InvalidTokenError:
            print("Invalid token")
            return {
                'valid': False,
                'error': 'Invalid token'
            }, 401
    else:
        # Authorization header is missing, return an error response
        return {
            'valid': False,
            'error': 'Authorization header is missing'
        }, 400


@app.route('/verify_token', methods=['POST'])
def verify_jwt_token_web():
    return verify_jwt_token()


@app.route('/review.html')
def history_page():
    token = request.cookies.get('jwt')

    if not token:
        return redirect(url_for('homepage'))
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return redirect(url_for('homepage'))
    except jwt.InvalidTokenError:
        return redirect(url_for('homepage'))

    return render_template('review.html', username=payload['username'])


@app.route('/detail.html')
def detail_page():
    game_id = request.args.get('game_id')
    token = request.cookies.get('jwt')

    if not token:
        return redirect(url_for('homepage'))
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return redirect(url_for('homepage'))
    except jwt.InvalidTokenError:
        return redirect(url_for('homepage'))

    return render_template('detail.html', game_id=game_id)


@app.route('/hand_history_details')
def get_hand_history_details():
    game_id = request.args.get('game_id')

    msg, status = verify_jwt_token()

    if msg['valid']:
        username = msg['payload']['username']
    else:
        return jsonify(msg), status

    poker_db_dao = PokerDB()
    poker_db_dao.build_connection()
    detail = poker_db_dao.fetch_history_by_game_id(username, game_id)
    overview = poker_db_dao.fetch_history_overview_by_id(username, game_id)
    poker_db_dao.close_connection()

    my_cards = cards_to_emoji(overview['hole_cards'].tolist()[-1])
    table_cards = cards_to_emoji(overview['community_cards'].tolist()[-1])

    detail = detail[['round', 'player', 'position', 'action', 'number', 'pot_before', 'pot_after', 'equity']]

    def cal_number(x):
        if not np.isnan(x.pot_before) and not np.isnan(x.pot_after):
            number = int(x.pot_after) - int(x.pot_before)
            if number <= 0:
                return '--'
            else:
                return number
        elif not np.isnan(x.pot_after) and np.isnan(x.pot_before):
            return x.pot_after
        else:
            return '--'

    detail['number_2'] = detail.apply(lambda x: cal_number(x), axis=1)

    detail['number'] = detail['number'].apply(lambda x: str(int(x)) if not np.isnan(x) else x)
    detail['pot_before'] = detail['pot_before'].apply(lambda x: str(int(x)) if not np.isnan(x) else x)
    detail['pot_after'] = detail['pot_after'].apply(lambda x: str(int(x)) if not np.isnan(x) else x)

    detail['equity'] = detail['equity'].apply(lambda x: np.nan if x is None else x)
    detail['equity'] = detail['equity'].apply(lambda x: str(int(x)) if not np.isnan(x) else x)

    note = ''  # Initialize note here
    index = 0

    def strategy(x):
        nonlocal note
        nonlocal index
        pot = int(x.pot_before) if isinstance(x.pot_before, str) else x.pot_before
        equity = int(x.equity) if isinstance(x.equity, str) else x.equity
        bet_amount = int(x.number_2) if x.number_2 != '--' else x.number_2

        # print(pot)
        # print(type(pot))
        # print(equity)
        # print(type(equity))
        # print(bet_amount)
        # print(type(bet_amount))
        # print('-'*50)

        index += 1

        note = ''  # Reset note for each row
        diagnosis = True  # Default value

        if not isinstance(equity, int) or not (isinstance(bet_amount, int)):
            return diagnosis, note
        else:
            if equity < 50:
                if 0 < equity < 20:
                    return diagnosis, note
                else:
                    optimal_bet_amount = pot * 1 / 6  # pot * equity / (100 - 2 * equity)
            else:
                if 50 <= equity < 65:
                    optimal_bet_amount = 1 / 3 * pot
                else:
                    optimal_bet_amount = pot

            if optimal_bet_amount:
                optimal_bet_amount = int(optimal_bet_amount)
                if optimal_bet_amount < 100:
                    optimal_bet_amount = 100

            if bet_amount > optimal_bet_amount:
                note = f'Bet Number should not exceed {int(optimal_bet_amount)}'
                diagnosis = False

            return diagnosis, note

    # Apply the strategy function and create a new DataFrame with the results
    diagnoses_and_notes = pd.DataFrame(detail.apply(lambda x: strategy(x), axis=1).tolist(), columns=['is_diagnose', 'diagnosis'])
    detail = pd.concat([detail, diagnoses_and_notes], axis=1)

    # detail['diagnose'] = detail.apply(lambda x: strategy(x), axis=1)
    mistake = (detail['is_diagnose'] == False).any()

    detail = detail.rename(columns={
        'round': 'Round',
        'player': 'Player',
        'position': 'Position',
        'action': 'Action',
        'number_2': 'Bet Number',
        'pot_before': 'Pot Before',
        'pot_after': 'Pot After',
        'equity': 'equity(%)'
    })

    detail = detail[['Round', 'Player', 'Position', 'Action', 'Bet Number', 'Pot Before', 'Pot After', 'equity(%)',
                     'diagnosis', 'is_diagnose']]
    detail.fillna('--', inplace=True)
    # print(detail)
    # print(my_cards)
    # print(table_cards)

    detail.index = detail.index + 1
    table_html = detail.to_html()

    response = {
        "table_html": table_html,
        "my_cards": my_cards,
        "table_cards": table_cards,
        "is_diagnose": bool(mistake),
        "note": note
    }

    return jsonify(response)


def generate_jwt_token(username, password):
    access_expired = 3600

    # Define the payload for the JWT token
    payload = {
        "username": username,
        "password": password,
        "exp": int(time.time()) + access_expired
    }

    # Generate the JWT token
    jwt_token = jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")

    return jwt_token


@app.route('/sign_up', methods=['POST'])
def sign_up():
    data = request.get_json()  # Get JSON data
    username = data['username']
    password = data['password']
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    poker_db_dao = PokerDB()
    poker_db_dao.build_connection()
    resp = poker_db_dao.save_user_info(username=username, password=hashed_password)
    poker_db_dao.close_connection()

    jwt_token = generate_jwt_token(username=username, password=hashed_password)

    if resp:
        return jsonify({
            'msg': 'OK',
            'jwt_token': jwt_token
        })
    else:
        return jsonify({
            'msg': 'Error'
        })


@app.route('/sign_in', methods=['POST'])
def sign_in():
    data = request.get_json()  # Get JSON data
    username = data['username']
    password = data['password']
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    poker_db_dao = PokerDB()
    poker_db_dao.build_connection()
    resp = poker_db_dao.verify_login(username, hashed_password)
    poker_db_dao.close_connection()

    jwt_token = generate_jwt_token(username=username, password=hashed_password)

    if resp:
        return jsonify({
            'msg': 'OK',
            'jwt_token': jwt_token
        })
    else:
        return jsonify({
            'msg': 'Error'
        })


@app.route('/game_ids')
def get_game_ids():
    poker_db_dao = PokerDB()
    poker_db_dao.build_connection()
    game_ids = poker_db_dao.fetch_game_id()
    poker_db_dao.close_connection()
    return jsonify(game_ids)


def cards_to_emoji(cards):
    if len(cards) == 0:
        return '--'
    suits_to_emoji = {'s': '♠', 'h': '♥', 'd': '♦', 'c': '♣'}
    cards_string = ''
    for card in cards:
        cards_string += card[:-1] + suits_to_emoji[card[-1]] + ' '
    return cards_string


@app.route('/hand_history_overview')
def get_hand_history_overview():
    start = int(request.args.get('start'))
    end = int(request.args.get('end'))

    msg, status = verify_jwt_token()

    if msg['valid']:
        user = msg['payload']['username']
    else:
        return jsonify(msg), status

    poker_db_dao = PokerDB()
    poker_db_dao.build_connection()
    df_history_overview = poker_db_dao.fetch_history_overview_by_timestamp(user, start, end)
    poker_db_dao.close_connection()

    df_history_overview['game_id'] = df_history_overview['game_id'].astype(int)
    df_history_overview['datetime'] = pd.to_datetime(df_history_overview['game_id'], unit='s')
    df_history_overview['datetime'] = df_history_overview['datetime'].dt.tz_localize('UTC')
    df_history_overview['datetime'] = df_history_overview['datetime'].dt.tz_convert('Asia/Taipei')
    df_history_overview['datetime'] = df_history_overview['datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')
    df_history_overview['community_cards'] = df_history_overview['community_cards'].apply(cards_to_emoji)
    df_history_overview['hole_cards'] = df_history_overview['hole_cards'].apply(cards_to_emoji)
    df_history_overview['details'] = df_history_overview['game_id'].apply(
        lambda x: f'<a href="detail.html?game_id={int(x)}" target="_blank">Details</a>'
    )

    df_history_overview = df_history_overview[
        ['datetime', 'position', 'hole_cards', 'community_cards', 'pnl', 'details']]
    df_history_overview = df_history_overview.rename(columns={
        'datetime': 'Datetime',
        'position': 'Position',
        'hole_cards': 'Hole Cards',
        'community_cards': 'Community Cards',
        'pnl': 'WinLoss',
        'details': 'Details'
    })

    table_html = df_history_overview.to_html(escape=False, index=False)
    return table_html


@app.route('/performance_history')
def get_performance_history():
    start = int(request.args.get('start'))
    end = int(request.args.get('end'))

    msg, status = verify_jwt_token()

    if msg['valid']:
        user = msg['payload']['username']
    else:
        return jsonify(msg), status

    poker_db_dao = PokerDB()
    poker_db_dao.build_connection()
    df_history_overview = poker_db_dao.fetch_history_overview_by_timestamp(user, start, end)
    poker_db_dao.close_connection()

    random.seed(1)
    df_history_overview['all_in_ev'] = df_history_overview['pnl'].apply(lambda x: x - random.randint(0, 1000))
    df_history_overview['pnl'] = df_history_overview['pnl'].cumsum()
    df_history_overview['all_in_ev'] = df_history_overview['all_in_ev'].cumsum()

    performance_json = {
        'pnl': df_history_overview['pnl'].tolist(),
        'all_in_ev': df_history_overview['all_in_ev'].tolist()
    }
    return jsonify(performance_json)


@app.route('/hole_cards_performance')
def get_hole_cards_performance():
    def cards_category(cards):
        if not cards:
            return None
        else:
            table = {
                '2': 2,
                '3': 3,
                '4': 4,
                '5': 5,
                '6': 6,
                '7': 7,
                '8': 8,
                '9': 9,
                'T': 10,
                'J': 11,
                'Q': 12,
                'K': 13,
                'A': 14,
            }
            num1 = cards[0][0]
            num1_ = table[num1]
            num2 = cards[1][0]
            num2_ = table[num2]
            suit1 = cards[0][1]
            suit2 = cards[1][1]
            if num1_ == num2_:
                cat = num1 + num2
                return cat
            else:
                if num1_ > num2_:
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

    msg, status = verify_jwt_token()

    if msg['valid']:
        user = msg['payload']['username']
    else:
        return jsonify(msg), status

    poker_db_dao = PokerDB()
    poker_db_dao.build_connection()
    df_history_overview = poker_db_dao.fetch_history_overview_by_timestamp(user, start, end)
    poker_db_dao.close_connection()

    df_history_overview['hole_cards_cat'] = df_history_overview['hole_cards'].apply(lambda x: cards_category(x))
    df_history_overview = df_history_overview[df_history_overview['hole_cards_cat'].notnull()]

    grouped_pnl = df_history_overview.groupby('hole_cards_cat')['pnl'].sum().reset_index()
    pnl_dict = grouped_pnl.set_index('hole_cards_cat')['pnl'].to_dict()

    return jsonify(pnl_dict)


@app.route('/position_performance')
def get_position_performance():
    start = int(request.args.get('start'))
    end = int(request.args.get('end'))

    msg, status = verify_jwt_token()

    if msg['valid']:
        user = msg['payload']['username']
    else:
        return jsonify(msg), status

    poker_db_dao = PokerDB()
    poker_db_dao.build_connection()
    df_history_overview = poker_db_dao.fetch_history_overview_by_timestamp(user, start, end)
    poker_db_dao.close_connection()

    df_history_overview = df_history_overview[df_history_overview['position'].notnull()]

    grouped_pnl = df_history_overview.groupby('position')['pnl'].sum().reset_index()
    grouped_pnl = grouped_pnl.sort_values(by='pnl', ascending=False).to_dict('list')
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
