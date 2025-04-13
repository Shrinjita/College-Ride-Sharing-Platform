from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_socketio import SocketIO, send, emit
from datetime import datetime
from collections import defaultdict

app = Flask(__name__, static_folder='static')
app.secret_key = 'da3f14683aa9d7649dad30081119e823e1b4271cfffe07d8405d5893a0d790ac'  # Change this to a secure key
socketio = SocketIO(app, cors_allowed_origins="*")

# In-memory databases
users = {}
rides = []
sos_alerts = []

# Add these global variables for chat functionality
active_chats = defaultdict(dict)  # {user1: {user2: [messages]}}
online_users = set()
user_status = {}  # {username: {"last_seen": timestamp, "status": "online/offline"}}

# Home Route
@app.route('/')
def home():
    return render_template('index.html')


# Register User
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data['username']
    password = data['password']
    register_no = data['registerNo']

    if username in users:
        return jsonify({"error": "Username already exists"}), 400

    users[username] = {"password": password, "registerNo": register_no}
    return jsonify({"message": "Registration successful"})


# Login User
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data['username']
    password = data['password']

    if username in users and users[username]['password'] == password:
        session['user'] = username
        if users[username]['registerNo'] == "RA2211047010017":
            return jsonify({"redirect": "/admin"})
        return jsonify({"redirect": "/"})
    return jsonify({"error": "Invalid credentials"}), 401


# Logout
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))


# Add Ride Request
@app.route('/add_ride', methods=['POST'])
def add_ride():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    ride = {
        "pickup": data['pickup'],
        "drop": data['drop'],
        "gender": data['gender'],
        "time": data['time'],
        "user": session['user'],
        "contact": users[session['user']]["registerNo"]  # Using registerNo as contact
    }
    rides.append(ride)
    return jsonify({"message": "Ride added successfully"})

# Get All Rides
@app.route('/get_rides')
def get_rides():
    return jsonify({"rides": rides})


# Send SOS Alert
@app.route('/send_sos', methods=['POST'])
def send_sos():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    sos_alerts.append({"user": session['user'], "contact": "7439947074"})
    return jsonify({"message": "SOS Alert Sent", "contact": "7439947074"})

# Admin Dashboard
@app.route('/admin')
def admin_dashboard():
    if 'user' not in session or users[session['user']]['registerNo'] != "RA2211047010017":
        return redirect(url_for('home'))

    return render_template('admin.html')


# Get Admin Data
@app.route('/admin_data')
def admin_data():
    if 'user' not in session or users[session['user']]['registerNo'] != "RA2211047010017":
        return jsonify({"error": "Unauthorized"}), 401

    return jsonify({"users": users, "rides": rides, "sos_alerts": sos_alerts})

# Get all users for chat
@app.route('/get_chat_users')
def get_chat_users():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    chat_users = []
    for username in users:
        if username != session['user']:
            status_info = user_status.get(username, {"status": "offline", "last_seen": None})
            chat_users.append({
                "username": username,
                "status": status_info["status"],
                "last_seen": status_info["last_seen"]
            })
    
    return jsonify({"users": chat_users})

# Chatroom WebSocket Functionality
@socketio.on('connect')
def handle_connect():
    print(f"Client connected: {request.sid}")
    if 'user' in session:
        username = session['user']
        online_users.add(username)
        user_status[username] = {
            "status": "online",
            "last_seen": datetime.now().isoformat()
        }
        emit('user_status_change', {
            'user': username,
            'status': 'online',
            'timestamp': datetime.now().isoformat()
        }, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    if 'user' in session:
        username = session['user']
        online_users.discard(username)
        user_status[username] = {
            "status": "offline",
            "last_seen": datetime.now().isoformat()
        }
        emit('user_status_change', {
            'user': username,
            'status': 'offline',
            'timestamp': datetime.now().isoformat()
        }, broadcast=True)
    print(f"Client disconnected: {request.sid}")

@socketio.on('private_message')
def handle_private_message(data):
    if 'user' not in session:
        return
    
    sender = session['user']
    recipient = data['to']
    message = {
        'from': sender,
        'to': recipient,
        'message': data['message'],
        'timestamp': datetime.now().isoformat(),
        'read': False
    }
    
    # Store message in both sender's and recipient's chat history
    active_chats[sender][recipient] = active_chats[sender].get(recipient, []) + [message]
    active_chats[recipient][sender] = active_chats[recipient].get(sender, []) + [message]
    
    # Emit to recipient if online
    emit('new_private_message', message, room=request.sid)  # To sender
    emit('new_private_message', message, broadcast=True)    # To recipient if connected

@socketio.on('get_chat_history')
def handle_get_chat_history(data):
    if 'user' not in session:
        return
    
    user = session['user']
    other_user = data['with']
    history = active_chats[user].get(other_user, [])
    
    # Mark messages as read
    for msg in history:
        if msg['from'] == other_user:
            msg['read'] = True
    
    emit('chat_history', {
        'with': other_user,
        'messages': history[-100:]  # Last 100 messages
    })

@socketio.on('mark_as_read')
def handle_mark_as_read(data):
    if 'user' not in session:
        return
    
    user = session['user']
    other_user = data['from']
    
    # Mark all messages from other_user as read
    for msg in active_chats[user].get(other_user, []):
        if msg['from'] == other_user:
            msg['read'] = True
    
    # Notify the sender that their message has been read
    if other_user in online_users:
        emit('messages_read', {
            'by': user,
            'timestamp': datetime.now().isoformat()
        }, broadcast=True)

@socketio.on('typing')
def handle_typing(data):
    if 'user' not in session:
        return
    
    emit('user_typing', {
        'user': session['user'],
        'to': data['to'],
        'isTyping': data['isTyping']
    }, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)