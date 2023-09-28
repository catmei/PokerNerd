from flask import Flask, request, render_template, jsonify
from flask_socketio import SocketIO
from database_controller import PokerDB


app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")


@app.route('/')
def homepage():
    return render_template('homepage.html')


@app.route('/tutor.html')
def tutor():
    return render_template('tutor.html')


@app.route('/history.html')
def history():
    return render_template('history.html')


@app.route('/game_ids')
def get_game_ids():
    poker_db_dao = PokerDB()
    poker_db_dao.build_connection()
    game_ids = poker_db_dao.fetch_game_id()
    poker_db_dao.close_connection()
    return jsonify(game_ids)


@app.route('/history_data')
def get_history_data():
    game_id = request.args.get('game_id')
    poker_db_dao = PokerDB()
    poker_db_dao.build_connection()
    df_history = poker_db_dao.fetch_history_by_game_id(game_id)
    poker_db_dao.close_connection()
    table_html = df_history.to_html()
    return table_html


@app.route('/trigger_update', methods=['post'])
def update_strategy():
    print('updating strategy')
    strategy = request.json
    print(f'strategy: {strategy}')
    socketio.emit('update_strategy', strategy)
    return 'OK'


# @socketio.on('update')
# def show_strategy(message):
#     print('updating strategy')
#     print(f'message: {message}')
#     socketio.emit('update_strategy', message)


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