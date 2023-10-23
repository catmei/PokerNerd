from flask import Flask, request, render_template
from flask_socketio import SocketIO


app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")


@app.route('/')
def tutor_page():
    return render_template('tutor.html')


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
    socketio.run(app, host='0.0.0.0', port=9001, debug=True, allow_unsafe_werkzeug=True)
