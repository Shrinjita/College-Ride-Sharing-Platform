from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')

ADMIN_ROLL = "RA2211047010017"

def init_db():
    conn = sqlite3.connect('ride_pool.db')
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            roll_number TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ride (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        pickup TEXT NOT NULL,
        "drop" TEXT NOT NULL,
        time TEXT NOT NULL,
        status TEXT NOT NULL,
        gender TEXT,  -- Add gender field
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES user (id)
        )
    """)
    conn.commit()
    conn.close()

def get_or_create_user(roll_number):
    conn = sqlite3.connect('ride_pool.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM user WHERE roll_number = ?", (roll_number,))
    result = cursor.fetchone()
    if result:
        user_id = result[0]
    else:
        cursor.execute("INSERT INTO user (roll_number) VALUES (?)", (roll_number,))
        user_id = cursor.lastrowid
        conn.commit()
    conn.close()
    return user_id

init_db()

@app.route('/')
def signin():
    return render_template('signin.html')

@app.route('/login', methods=['POST'])
def login():
    roll = request.form.get('username')
    password = request.form.get('password')

    if not roll or not password:
        return "Username and password are required", 403
        
    # Validate roll number format
    if not roll.startswith("RA2211047010") or not roll[13:].isdigit() or not (1 <= int(roll[-3:]) <= 100):
        return "Invalid Roll Number", 403

    if roll == ADMIN_ROLL and password == "ADMIN":
        session['roll'] = roll
        return redirect(url_for('admin_dashboard'))

    if password == roll[-3:] + "srm":
        session['roll'] = roll
        return redirect(url_for('user_dashboard'))

    return "Invalid Credentials", 403

@app.route('/admin')
def admin_dashboard():
    if session.get('roll') != ADMIN_ROLL:
        return redirect(url_for('signin'))

    conn = sqlite3.connect('ride_pool.db')
    cursor = conn.cursor()
    
    # Get stats for dashboard
    stats = {
        'total_rides': cursor.execute("SELECT COUNT(*) FROM ride").fetchone()[0],
        'active_rides': cursor.execute("SELECT COUNT(*) FROM ride WHERE status = 'Scheduled'").fetchone()[0],
        'total_users': cursor.execute("SELECT COUNT(*) FROM user").fetchone()[0],
    }
    
    # Get rides data including gender
    cursor.execute("""
        SELECT user.roll_number, ride.pickup, ride."drop", ride.time, ride.status, ride.gender
        FROM ride JOIN user ON ride.user_id = user.id
    """)
    rides = cursor.fetchall()
    conn.close()
    
    return render_template("admin.html", rides=rides, **stats)

@app.route('/user')
def user_dashboard():
    roll = session.get('roll')
    if not roll:
        return redirect(url_for('signin'))

    conn = sqlite3.connect('ride_pool.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT user.roll_number, ride.pickup, ride."drop", ride.time, ride.status, ride.gender
        FROM ride JOIN user ON ride.user_id = user.id
        WHERE user.roll_number = ?
    """, (roll,))
    rides = cursor.fetchall()
    conn.close()
    return render_template('index.html', roll=roll, rides=rides)

@app.route('/add_ride', methods=['POST'])
def add_ride():
    if 'roll' not in session:
        return redirect(url_for('signin'))

    # Determine whose ride is being added
    is_admin = session['roll'] == ADMIN_ROLL
    roll_number = request.form.get('roll_number') if is_admin else session['roll']

    pickup = request.form.get('pickup')
    drop = request.form.get('drop')
    time = request.form.get('time')
    status = request.form.get('status')
    gender = request.form.get('gender')  # Get gender field

    # Validate required fields
    if not all([pickup, drop, time, status]):
        return "All fields are required", 400

    user_id = get_or_create_user(roll_number)

    conn = sqlite3.connect('ride_pool.db')
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO ride (user_id, pickup, "drop", time, status, gender)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, pickup, drop, time, status, gender))
        conn.commit()
    except sqlite3.Error as e:
        conn.close()
        return f"Database error: {e}", 500
    conn.close()

    return redirect(url_for('admin_dashboard' if is_admin else 'user_dashboard'))

@app.route('/admin_stats')
def admin_stats():
    if session.get('roll') != ADMIN_ROLL:
        return redirect(url_for('signin'))

    conn = sqlite3.connect('ride_pool.db')
    cursor = conn.cursor()
    stats = {
        'total_rides': cursor.execute("SELECT COUNT(*) FROM ride").fetchone()[0],
        'active_rides': cursor.execute("SELECT COUNT(*) FROM ride WHERE status = 'Scheduled'").fetchone()[0],
        'completed_rides': cursor.execute("SELECT COUNT(*) FROM ride WHERE status = 'Completed'").fetchone()[0],
        'total_users': cursor.execute("SELECT COUNT(*) FROM user").fetchone()[0],
        'active_users': cursor.execute("SELECT COUNT(DISTINCT user_id) FROM ride WHERE status = 'Scheduled' OR (status = 'Completed' AND date(created_at) = date('now'))").fetchone()[0],
        'new_users_today': cursor.execute("SELECT COUNT(*) FROM user WHERE date(created_at) = date('now')").fetchone()[0],
        'ride_issues': 0,
        'sos_alerts': 0
    }
    conn.close()
    return stats

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('signin'))

if __name__ == '__main__':
    app.run(debug=True)