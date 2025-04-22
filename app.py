from flask import Flask, render_template, request
from flask_socketio import SocketIO
from datetime import datetime
import random

app = Flask(__name__)
socketio = SocketIO(app)

# Store users: { session_id: { username: ..., color: ... } }
users = {}

# Generate a random HEX color
def random_color():
    return f"#{''.join(random.choices('0123456789ABCDEF', k=6))}"

def broadcast_active_users():
    usernames = [data["username"] for data in users.values()]
    socketio.emit("active users", usernames)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('user joined')
def handle_user_joined(username):
    color = random_color()
    timestamp = datetime.now().strftime("%I:%M %p")
    users[request.sid] = {'username': username, 'color': color}
    print(f"{username} joined at {timestamp} with color {color}")
    socketio.emit('user joined', {
        'username': username,
        'color': color,
        'time': timestamp
    })

    broadcast_active_users()



@socketio.on('chat message')
def handle_chat(data):
    timestamp = datetime.now().strftime("%I:%M %p")
    user_data = users.get(request.sid, {"username": "Unknown", "color": "#000"})

    message_with_time = f"[{timestamp}] {data['text']}"
    
    socketio.emit('chat message', {
        'user': user_data["username"],
        'text': message_with_time,
        'color': user_data["color"]
    })

    with open("chat_log.txt", "a") as file:
        file.write(f"{user_data['username']}: {message_with_time}\n")

@socketio.on('disconnect')
def handle_disconnect():
    user_data = users.pop(request.sid, None)
    if user_data:
        timestamp = datetime.now().strftime("%I:%M %p")
        print(f"{user_data['username']} disconnected at {timestamp}")
        socketio.emit('user left', {
            'username': user_data['username'],
            'time': timestamp
        })

        broadcast_active_users()


if __name__ == '__main__':
    socketio.run(app, debug=True)



