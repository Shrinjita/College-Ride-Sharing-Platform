from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_socketio import SocketIO, send

app = Flask(__name__)
app.secret_key = 'da3f14683aa9d7649dad30081119e823e1b4271cfffe07d8405d5893a0d790ac'  # Change this to a secure key
socketio = SocketIO(app, cors_allowed_origins="*")

# In-memory database (Replace with actual DB in production)
users = {}
rides = []
sos_alerts = []
chat_messages = []  # Store chat messages

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

# Chatroom WebSocket Functionality
@socketio.on("message")
def handle_message(data):
    print(f"Received message: {data}")
    socketio.emit('message', data, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)
