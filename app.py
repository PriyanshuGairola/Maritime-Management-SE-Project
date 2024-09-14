from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3

# Initialize the Flask application
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Used to handle sessions securely

# Create a helper function to connect to the SQLite database
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Route for the home page
@app.route('/')
def index():
    return render_template('index.html')

# Route for the login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the user exists in the database
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?',
                            (username, password)).fetchone()
        conn.close()

        if user:
            # Store user details in session
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['user_type'] = user['user_type']

            # Redirect to user-specific dashboard
            if user['user_type'] == 'crew_member':
                return redirect(url_for('crew_member_dashboard'))
            elif user['user_type'] == 'ship_owner':
                return redirect(url_for('ship_owner_dashboard'))
            elif user['user_type'] == 'management_employee':
                return redirect(url_for('management_employee_dashboard'))
            elif user['user_type'] == 'ship':
                return redirect(url_for('ship_dashboard'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')

    return render_template('login.html')

# Route for the signup page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_type = request.form['user_type']

        # Insert the user data into the database
        conn = get_db_connection()
        conn.execute('INSERT INTO users (username, password, user_type) VALUES (?, ?, ?)',
                     (username, password, user_type))
        conn.commit()
        conn.close()

        flash('Signup successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')
#CREW_MEMBER
@app.route('/crew_member_dashboard')
def crew_member_dashboard():
    crew_id = session.get('user_id')
    print(f"Logged in crew member ID: {crew_id}")

    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch the crew member's status
    cursor.execute('SELECT status FROM crew_members WHERE id = ?', (crew_id,))
    crew_member = cursor.fetchone()
    print(f"Crew member status: {crew_member}")

    if crew_member:
        crew_status = crew_member['status']
    else:
        crew_status = 'unknown'

    # Fetch preferred ships
    cursor.execute('''
        SELECT ps.ship_id, s.name, s.type
        FROM preferred_ships ps
        JOIN ships s ON ps.ship_id = s.id
        WHERE ps.crew_id = ?
    ''', (crew_id,))
    preferred_ships = cursor.fetchall()
    print(f"Preferred ships: {preferred_ships}")

    # Fetch ship details
    cursor.execute('''
        SELECT s.id, s.name, s.type
        FROM ships s
        WHERE s.id IN (SELECT ps.ship_id FROM preferred_ships ps WHERE ps.crew_id = ?)
    ''', (crew_id,))
    ship_details = cursor.fetchone()
    print(f"Ship details: {ship_details}")

    if ship_details:
        cursor.execute('''
            SELECT cm.name, cm.status
            FROM crew_members cm
            JOIN crew_readiness cr ON cm.id = cr.crew_id
            WHERE cr.ship_id = ?
        ''', (ship_details['id'],))
        ship_crew_members = cursor.fetchall()
        print(f"Ship crew members: {ship_crew_members}")
        ship_details['crew_members'] = ship_crew_members
    else:
        ship_details = None

    conn.close()

    return render_template(
        'crew_member_dashboard.html',
        status=crew_status,
        preferred_ships=preferred_ships,
        ship_details=ship_details
    )

@app.route('/submit_readiness', methods=['POST'])
def submit_readiness():
    readiness_date = request.form['readiness_date']
    crew_id = session.get('user_id')  # Use the logged-in crew member's ID from the session

    conn = get_db_connection()
    cursor = conn.cursor()

    # Insert or update the readiness date in the database
    cursor.execute('INSERT OR REPLACE INTO crew_readiness (crew_id, readiness_date, status) VALUES (?, ?, ?)',
                   (crew_id, readiness_date, 'Pending'))  # Added default status
    conn.commit()
    conn.close()

    return redirect(url_for('crew_member_dashboard'))
@app.route('/add_ship', methods=['POST'])
def add_ship():
    name = request.form['name']
    type = request.form['type']
    flag = request.form['flag']
    imo_number = request.form['imo_number']
    gross_tonnage = request.form['gross_tonnage']
    net_tonnage = request.form['net_tonnage']
    quality = request.form['quality']
    age = request.form['age']

    conn = get_db_connection()
    conn.execute('''
        INSERT INTO ships (name, type, flag, imo_number, gross_tonnage, net_tonnage, quality, age)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (name, type, flag, imo_number, gross_tonnage, net_tonnage, quality, age))
    conn.commit()
    conn.close()

    return redirect(url_for('ship_owner_dashboard'))
#SHIP_OWNER
@app.route('/ship_owner_dashboard')
def ship_owner_dashboard():
    conn = get_db_connection()

    # Fetch ship details
    ships = conn.execute('SELECT * FROM ships').fetchall()

    # Fetch crew members and their associated ships
    crew = conn.execute('''
        SELECT crew_members.name, crew_members.rank, ships.name AS ship_name
        FROM crew_members
        JOIN ships ON crew_members.ship_id = ships.id
    ''').fetchall()

    conn.close()

    return render_template(
        'ship_owner_dashboard.html',
        ships=ships,
        crew=crew
    )


#Management Employee

@app.route('/manage_fleet')
def manage_fleet():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM ships')
    ships = cursor.fetchall()
    conn.close()
    
    return render_template('management_employee_dashboard.html', ships=ships)
@app.route('/assign_voyage', methods=['POST'])
def assign_voyage():
    ship_id = request.form['ship_id']
    destination = request.form['destination']
    eta = request.form['eta']
    status = request.form['status']

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO voyages (ship_id, destination, eta, status)
        VALUES (?, ?, ?, ?)
    ''', (ship_id, destination, eta, status))
    conn.commit()
    conn.close()

    return redirect(url_for('management_employee_dashboard'))
@app.route('/search_crew', methods=['POST'])
def search_crew():
    name = request.form.get('name', '')
    rank = request.form.get('rank', '')
    ship_type = request.form.get('ship_type', '')

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    query = '''
        SELECT * FROM crew_members
        WHERE name LIKE ? AND rank LIKE ? AND ship_type LIKE ?
    '''
    cursor.execute(query, (f'%{name}%', f'%{rank}%', f'%{ship_type}%'))
    crew_members = cursor.fetchall()
    conn.close()

    return render_template('management_employee_dashboard.html', crew_members=crew_members)
@app.route('/handle_readiness_requests', methods=['POST'])
def handle_readiness_requests():
    request_id = request.form['request_id']
    action = request.form['action']

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    if action == 'approve':
        cursor.execute('UPDATE crew_readiness SET status = "Approved" WHERE id = ?', (request_id,))
    elif action == 'decline':
        cursor.execute('UPDATE crew_readiness SET status = "Declined" WHERE id = ?', (request_id,))
    
    conn.commit()
    conn.close()

    return redirect(url_for('management_employee_dashboard'))
@app.route('/chat')
def chat():
    # Implement chat functionality or integrate a chat service
    return render_template('management_employee_dashboard.html')

@app.route('/management_employee_dashboard')
def management_employee_dashboard():
    return render_template('management_employee_dashboard.html')





#SHIP 
@app.route('/update_sailing_status', methods=['POST'])
def update_sailing_status():
    area = request.form['area']
    destination = request.form['destination']
    speed = request.form['speed']
    ship_id = 1  # Placeholder; use the logged-in ship's ID

    conn = get_db_connection()
    cursor = conn.cursor()

    # Update the ship's sailing status in the database
    cursor.execute('''
        UPDATE ships
        SET area = ?, destination = ?, speed = ?, status = 'sailing'
        WHERE id = ?
    ''', (area, destination, speed, ship_id))
    conn.commit()
    conn.close()

    flash('Sailing status updated successfully!', 'success')
    return redirect(url_for('ship_dashboard'))
@app.route('/update_anchored_status', methods=['POST'])
def update_anchored_status():
    loading = request.form['loading']
    discharging = request.form['discharging']
    inspections = request.form['inspections']
    ship_id = 1  # Placeholder; use the logged-in ship's ID

    conn = get_db_connection()
    cursor = conn.cursor()

    # Update the ship's anchored status in the database
    cursor.execute('''
        UPDATE ships
        SET loading = ?, discharging = ?, inspections = ?, status = 'anchored'
        WHERE id = ?
    ''', (loading, discharging, inspections, ship_id))
    conn.commit()
    conn.close()

    flash('Anchored status updated successfully!', 'success')
    return redirect(url_for('ship_dashboard'))
@app.route('/ship_dashboard')
def ship_dashboard():
    ship_id = 1  # Placeholder; use the logged-in ship's ID

    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch upcoming voyages/ports assigned by management employees
    cursor.execute('''
        SELECT destination, eta FROM voyages
        WHERE ship_id = ? AND status = 'upcoming'
    ''', (ship_id,))
    voyages = cursor.fetchall()
    conn.close()

    return render_template('ship_dashboard.html', voyages=voyages)


if __name__ == '__main__':
    app.run(debug=True)
