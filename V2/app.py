from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
import os
import datetime
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
        pickup VARCHAR(50) NOT NULL,
        "drop" VARCHAR(50) NOT NULL,
        time VARCHAR(20) NOT NULL,
        gender VARCHAR(10) NOT NULL,
        contact VARCHAR(50) NOT NULL,
        status VARCHAR(20),
        FOREIGN KEY (user_id) REFERENCES user (id)
        )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sos_alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        resolved BOOLEAN DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES user (id)
        )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ride_issues (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ride_id INTEGER NOT NULL,
        issue_type TEXT NOT NULL,
        description TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        resolved BOOLEAN DEFAULT 0,
        FOREIGN KEY (ride_id) REFERENCES ride (id)
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
        'active_users': cursor.execute("SELECT COUNT(DISTINCT user_id) FROM ride WHERE status = 'Scheduled' OR (status = 'Completed' AND date(created_at) = date('now'))").fetchone()[0],
        'ride_issues': cursor.execute("SELECT COUNT(*) FROM ride_issues WHERE resolved = 0").fetchone()[0],
        'sos_alerts': cursor.execute("SELECT COUNT(*) FROM sos_alerts WHERE resolved = 0").fetchone()[0],
    }
    
    # Get SOS alerts data
    cursor.execute("""
        SELECT sos_alerts.id, user.roll_number, sos_alerts.timestamp, sos_alerts.resolved, ride.contact
        FROM sos_alerts 
        JOIN user ON sos_alerts.user_id = user.id
        LEFT JOIN ride ON ride.user_id = user.id
        ORDER BY sos_alerts.timestamp DESC
    """)
    sos_alerts_data = cursor.fetchall()
    sos_alerts_list = [
        {
            'id': row[0],
            'roll_number': row[1],
            'timestamp': row[2],
            'resolved': bool(row[3]),
            'contact': row[4] or "N/A"
        }
        for row in sos_alerts_data
    ]
    
    # Get ride issues data
    cursor.execute("""
        SELECT ride_issues.id, user.roll_number, ride_issues.issue_type, 
               ride_issues.description, ride_issues.timestamp, ride_issues.resolved, ride.contact
        FROM ride_issues 
        JOIN ride ON ride_issues.ride_id = ride.id
        JOIN user ON ride.user_id = user.id
        ORDER BY ride_issues.timestamp DESC
    """)
    ride_issues_data = cursor.fetchall()
    ride_issues_list = [
        {
            'id': row[0],
            'roll_number': row[1],
            'issue_type': row[2],
            'description': row[3],
            'timestamp': row[4],
            'resolved': bool(row[5]),
            'contact': row[6] or "N/A"
        }
        for row in ride_issues_data
    ]
    
    # Get rides data including gender and contact
    cursor.execute("""
        SELECT user.roll_number, ride.pickup, ride."drop", ride.time, ride.status, ride.gender, ride.contact
        FROM ride JOIN user ON ride.user_id = user.id
        ORDER BY ride.created_at DESC
    """)
    rides = cursor.fetchall()
    conn.close()
    
    return render_template("admin.html", rides=rides, sos_alerts_list=sos_alerts_list, 
                           ride_issues_list=ride_issues_list, **stats)

@app.route('/user')
def user_dashboard():
    roll = session.get('roll')
    if not roll:
        return redirect(url_for('signin'))

    conn = sqlite3.connect('ride_pool.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT user.roll_number, ride.pickup, ride."drop", ride.time, ride.status, ride.gender, ride.contact
        FROM ride JOIN user ON ride.user_id = user.id
        WHERE user.roll_number = ?
        ORDER BY 
            CASE ride.status 
                WHEN 'Scheduled' THEN 1 
                WHEN 'Completed' THEN 2 
                ELSE 3 
            END,
            ride.created_at DESC
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
    gender = request.form.get('gender')
    contact = request.form.get('contact')  # Add this line to get contact info

    # Validate required fields
    if not all([pickup, drop, time, status, gender, contact]):  # Add contact to validation
        return "All fields are required", 400
        
    # Prevent same pickup and drop location
    if pickup == drop:
        return "Pickup and drop locations cannot be the same", 400

    user_id = get_or_create_user(roll_number)

    conn = sqlite3.connect('ride_pool.db')
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO ride (user_id, pickup, "drop", time, status, gender, contact)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, pickup, drop, time, status, gender, contact))  # Add contact parameter
        conn.commit()
    except sqlite3.Error as e:
        conn.close()
        return f"Database error: {e}", 500
    conn.close()

    return redirect(url_for('admin_dashboard' if is_admin else 'user_dashboard'))

@app.route('/send_sos', methods=['POST'])
def send_sos():
    if 'roll' not in session:
        return jsonify({'error': 'Not logged in'}), 401
        
    roll = session.get('roll')
    
    conn = sqlite3.connect('ride_pool.db')
    cursor = conn.cursor()
    
    # Get user ID
    cursor.execute("SELECT id FROM user WHERE roll_number = ?", (roll,))
    result = cursor.fetchone()
    
    if not result:
        conn.close()
        return jsonify({'error': 'User not found'}), 404
    
    user_id = result[0]
    
    # Add SOS alert
    try:
        cursor.execute("INSERT INTO sos_alerts (user_id) VALUES (?)", (user_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'SOS alert sent successfully'})
    except sqlite3.Error as e:
        conn.close()
        return jsonify({'error': f'Database error: {e}'}), 500

@app.route('/report_issue', methods=['POST'])
def report_issue():
    if 'roll' not in session:
        return jsonify({'error': 'Not logged in'}), 401
        
    ride_id = request.json.get('ride_id')
    issue_type = request.json.get('issue_type')
    description = request.json.get('description')
    
    if not all([ride_id, issue_type]):
        return jsonify({'error': 'Missing required fields'}), 400
        
    conn = sqlite3.connect('ride_pool.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO ride_issues (ride_id, issue_type, description)
            VALUES (?, ?, ?)
        """, (ride_id, issue_type, description))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Issue reported successfully'})
    except sqlite3.Error as e:
        conn.close()
        return jsonify({'error': f'Database error: {e}'}), 500

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
        'active_users': cursor.execute("SELECT COUNT(DISTINCT user_id) FROM ride WHERE status = 'Scheduled'").fetchone()[0],
        'new_users_today': cursor.execute("SELECT COUNT(*) FROM user WHERE date(created_at) = date('now')").fetchone()[0],
        'ride_issues': cursor.execute("SELECT COUNT(*) FROM ride_issues WHERE resolved = 0").fetchone()[0],
        'sos_alerts': cursor.execute("SELECT COUNT(*) FROM sos_alerts WHERE resolved = 0").fetchone()[0]
    }
    conn.close()
    return jsonify(stats)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('signin'))

@app.route('/resolve_sos', methods=['POST'])
def resolve_sos():
    if session.get('roll') != ADMIN_ROLL:
        return jsonify({'error': 'Unauthorized'}), 401
    
    alert_id = request.json.get('id')
    if not alert_id:
        return jsonify({'error': 'Missing alert ID'}), 400
    
    conn = sqlite3.connect('ride_pool.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("UPDATE sos_alerts SET resolved = 1 WHERE id = ?", (alert_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except sqlite3.Error as e:
        conn.close()
        return jsonify({'error': f'Database error: {e}'}), 500

@app.route('/resolve_issue', methods=['POST'])
def resolve_issue():
    if session.get('roll') != ADMIN_ROLL:
        return jsonify({'error': 'Unauthorized'}), 401
    
    issue_id = request.json.get('id')
    if not issue_id:
        return jsonify({'error': 'Missing issue ID'}), 400
    
    conn = sqlite3.connect('ride_pool.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("UPDATE ride_issues SET resolved = 1 WHERE id = ?", (issue_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except sqlite3.Error as e:
        conn.close()
        return jsonify({'error': f'Database error: {e}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)