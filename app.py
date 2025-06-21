from flask import Flask, render_template, request, redirect, flash, session
import sqlite3
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with your actual secret key

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row  # To access columns by name
    return conn

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        user = cursor.fetchone()
        
        if user:
            user_type = user['user_type']
            session['username'] = username
            session['user_type'] = user_type
            
            if user_type == 'owner':
                return redirect('/owner_dashboard')
            elif user_type == 'crew':
                return redirect('/crew_dashboard')
            elif user_type == 'management_employee':
                return redirect('/management_employee_dashboard')
            elif user_type == 'ship':
                return redirect('/ship_dashboard')
        else:
            flash('Invalid username or password. Please try again.')
        conn.close()
    return render_template('login.html')

@app.route('/owner_dashboard')
def owner_dashboard():
    username = session.get('username')
    if not username:
        return redirect('/login')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Fetch owner_id from users and owners tables
    cursor.execute('''
        SELECT owners.id FROM owners
        JOIN users ON owners.user_id = users.id
        WHERE users.username = ?
    ''', (username,))
    owner = cursor.fetchone()
    
    if not owner:
        flash('Owner not found.')
        conn.close()
        return redirect('/login')
    
    owner_id = owner['id']
    
    # Fetch ships owned by the owner
    cursor.execute('''
        SELECT id, name, age, tonnage, type, length, cabins FROM ships
        WHERE owner_id = ?
    ''', (owner_id,))
    ships = cursor.fetchall()
    
    # For each ship, fetch the latest voyage
    ship_voyages = []
    for ship in ships:
        cursor.execute('''
            SELECT destination, eta, status FROM voyages
            WHERE ship_id = ?
            ORDER BY eta DESC
            LIMIT 1
        ''', (ship['id'],))
        voyage = cursor.fetchone()
        ship_voyages.append({
            'name': ship['name'],
            'age': ship['age'],
            'tonnage': ship['tonnage'],
            'type': ship['type'],
            'length': ship['length'],
            'cabins': ship['cabins'],
            'voyage_destination': voyage['destination'] if voyage else 'No Voyage',
            'voyage_eta': voyage['eta'] if voyage else 'N/A',
            'voyage_status': voyage['status'] if voyage else 'N/A'
        })
    
    conn.close()
    
    return render_template('owner_dashboard.html', ships=ship_voyages)
@app.route('/add_ship', methods=['POST'])
#Add Ship Function
def add_ship():
    username = session.get('username')
    if not username:
        return redirect('/login')
    
    # Fetch owner_id from users and owners tables
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT owners.id FROM owners
        JOIN users ON owners.user_id = users.id
        WHERE users.username = ?
    ''', (username,))
    owner = cursor.fetchone()
    
    if not owner:
        flash('Owner not found.')
        conn.close()
        return redirect('/login')
    
    owner_id = owner['id']
    
    # Get form data
    name = request.form['name']
    age = request.form['age']
    tonnage = request.form['tonnage']
    ship_type = request.form['type']
    length = request.form['length']
    cabins = request.form['cabins']
    password = request.form['password']
    
    try:
        # Insert ship as a user for login
        user_id = insert_user(conn, name, password, 'ship')
        
        if not user_id:
            flash(f"Ship '{name}' already exists. Please choose a different name.")
            conn.close()
            return redirect('/owner_dashboard')
        
        # Insert ship into ships table
        cursor.execute('''
            INSERT INTO ships (name, owner_id, age, tonnage, type, length, cabins, password)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, owner_id, int(age), float(tonnage), ship_type, float(length), float(cabins), password))
        
        conn.commit()
        flash(f"Ship '{name}' added successfully.")
    except Exception as e:
        flash(f"Error adding ship: {e}")
    finally:
        conn.close()
    
    return redirect('/owner_dashboard')

# Placeholder routes for other dashboards
@app.route('/crew_dashboard')
def crew_dashboard():
    username = session.get('username')
    if not username:
        return redirect('/login')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT crew_members.rank, crew_members.status, ships.name as ship_name 
        FROM crew_members
        JOIN users ON crew_members.user_id = users.id
        LEFT JOIN ships ON crew_members.ship_id = ships.id
        WHERE users.username = ?
    ''', (username,))
    crew = cursor.fetchone()
    conn.close()
    
    return render_template('crew_dashboard.html', crew=crew)


#management employee
@app.route('/management_employee_dashboard', methods=['GET', 'POST'])
def management_employee_dashboard():
    username = session.get('username')
    if not username:
        return redirect('/login')
    
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch management employee id
    cursor.execute('''
        SELECT management_employees.id FROM management_employees
        JOIN users ON management_employees.user_id = users.id
        WHERE users.username = ?
    ''', (username,))
    employee = cursor.fetchone()
    
    if not employee:
        flash('Management Employee not found.')
        conn.close()
        return redirect('/login')
    
    employee_id = employee['id']
    
    # Fetch assigned crew members and ships
    cursor.execute('''
        SELECT crew_members.id, crew_members.name, crew_members.rank, ships.name as ship_name
        FROM management_assignments
        JOIN crew_members ON management_assignments.crew_id = crew_members.id
        JOIN ships ON management_assignments.ship_id = ships.id
        WHERE management_assignments.employee_id = ?
    ''', (employee_id,))
    assignments = cursor.fetchall()

    # Handle form submissions for updating status, assigning crew, etc.
    if request.method == 'POST':
        # Update Crew Status (ON-SHORE/ABOARD)
        if 'update_status' in request.form:
            crew_id = request.form['crew_id']
            status = request.form['status']
            cursor.execute('''
                UPDATE crew_members
                SET status = ?
                WHERE id = ?
            ''', (status, crew_id))
            conn.commit()
            flash('Crew status updated.')

        # Assign crew to ship
        if 'assign_crew' in request.form:
            crew_id = request.form['crew_id']
            ship_id = request.form['ship_id']
            cursor.execute('''
                INSERT INTO management_assignments (employee_id, crew_id, ship_id)
                VALUES (?, ?, ?)
            ''', (employee_id, crew_id, ship_id))
            conn.commit()
            flash('Crew assigned to ship.')

    conn.close()

    return render_template('management_employee_dashboard.html', crew=assignments)

##management employee functions
@app.route('/assign_crew_to_ship', methods=['POST'])
def assign_crew_to_ship():
    username = session.get('username')
    if not username:
        return redirect('/login')

    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch management employee ID
    cursor.execute('''
        SELECT management_employees.id FROM management_employees
        JOIN users ON management_employees.user_id = users.id
        WHERE users.username = ?
    ''', (username,))
    employee = cursor.fetchone()

    if not employee:
        flash('Management employee not found.')
        conn.close()
        return redirect('/login')

    employee_id = employee['id']
    
    # Fetch crew and ship IDs from the form
    crew_id = request.form['crew_id']
    ship_id = request.form['ship_id']

    # Assign the crew member to the ship
    cursor.execute('''
        INSERT INTO crew_assignments (crew_id, ship_id)
        VALUES (?, ?)
    ''', (crew_id, ship_id))

    conn.commit()
    conn.close()

    flash('Crew member assigned to the ship.')
    return redirect('/management_dashboard')
@app.route('/update_crew_status', methods=['POST'])
def update_crew_status():
    username = session.get('username')
    if not username:
        return redirect('/login')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Fetch management employee ID
    cursor.execute('''
        SELECT management_employees.id FROM management_employees
        JOIN users ON management_employees.user_id = users.id
        WHERE users.username = ?
    ''', (username,))
    employee = cursor.fetchone()

    if not employee:
        flash('Management employee not found.')
        conn.close()
        return redirect('/login')
    
    crew_id = request.form['crew_id']
    status = request.form['status']
    
    # Update the crew member's status (ON-SHORE/ABOARD)
    cursor.execute('''
        UPDATE crew_members
        SET status = ?
        WHERE id = ?
    ''', (status, crew_id))

    conn.commit()
    conn.close()

    flash(f'Crew member status updated to {status}.')
    return redirect('/management_dashboard')
@app.route('/view_crew_contracts')
def view_crew_contracts():
    username = session.get('username')
    if not username:
        return redirect('/login')

    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch management employee ID
    cursor.execute('''
        SELECT management_employees.id FROM management_employees
        JOIN users ON management_employees.user_id = users.id
        WHERE users.username = ?
    ''', (username,))
    employee = cursor.fetchone()

    if not employee:
        flash('Management employee not found.')
        conn.close()
        return redirect('/login')

    # Fetch crew members assigned to the management employee
    cursor.execute('''
        SELECT crew_members.id, crew_members.name, crew_members.contract_expiration 
        FROM crew_members
        JOIN management_assignments ON crew_members.id = management_assignments.crew_id
        WHERE management_assignments.employee_id = ?
    ''', (employee['id'],))
    crew_members = cursor.fetchall()

    conn.close()

    return render_template('view_crew_contracts.html', crew_members=crew_members)
@app.route('/find_relievers', methods=['POST'])
def find_relievers():
    username = session.get('username')
    if not username:
        return redirect('/login')

    rank = request.form['rank']
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch management employee ID
    cursor.execute('''
        SELECT management_employees.id FROM management_employees
        JOIN users ON management_employees.user_id = users.id
        WHERE users.username = ?
    ''', (username,))
    employee = cursor.fetchone()

    if not employee:
        flash('Management employee not found.')
        conn.close()
        return redirect('/login')

    # Fetch crew members of the same rank
    cursor.execute('''
        SELECT crew_members.id, crew_members.name, crew_members.rank, crew_members.status
        FROM crew_members
        WHERE crew_members.rank = ? AND crew_members.status = 'ON-SHORE'
    ''', (rank,))
    relievers = cursor.fetchall()

    conn.close()

    return render_template('find_relievers.html', relievers=relievers)


#readiness
@app.route('/apply_readiness', methods=['POST'])
def apply_readiness():
    username = session.get('username')
    if not username:
        return redirect('/login')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Fetch crew member's id based on username
    cursor.execute('''
        SELECT crew_members.id FROM crew_members
        JOIN users ON crew_members.user_id = users.id
        WHERE users.username = ?
    ''', (username,))
    crew_member = cursor.fetchone()
    
    if not crew_member:
        flash('Crew member not found.')
        conn.close()
        return redirect('/login')
    
    crew_id = crew_member['id']
    readiness_date = request.form['readiness_date']  # This will be taken from the form input
    
    # Insert or update readiness status for the crew member
    try:
        cursor.execute('''
            INSERT INTO crew_readiness (crew_id, readiness_date, status)
            VALUES (?, ?, ?)
            ON CONFLICT(crew_id) DO UPDATE SET
            readiness_date = excluded.readiness_date,
            status = 'Ready'
        ''', (crew_id, readiness_date))
        
        conn.commit()
        flash("Readiness status updated successfully.")
    except Exception as e:
        flash(f"Error updating readiness: {e}")
    finally:
        conn.close()
    
    return redirect('/crew_dashboard')
#messaging between crew and management employee
from datetime import datetime

@app.route('/send_message', methods=['POST'])
def send_message():
    username = session.get('username')
    if not username:
        return redirect('/login')

    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch crew and manager IDs
    cursor.execute('''
        SELECT crew_members.id AS crew_id, management_employees.id AS manager_id
        FROM crew_members
        JOIN users ON crew_members.user_id = users.id
        JOIN management_assignments ON management_assignments.crew_id = crew_members.id
        JOIN management_employees ON management_assignments.employee_id = management_employees.id
        WHERE users.username = ?
    ''', (username,))
    ids = cursor.fetchone()

    if not ids:
        flash("No management employee assigned.")
        conn.close()
        return redirect('/crew_dashboard')

    crew_id, manager_id = ids['crew_id'], ids['manager_id']
    message = request.form['message']
    timestamp = datetime.now()  # Current timestamp

    # Insert message into messages table with timestamp
    cursor.execute('''
        INSERT INTO messages (sender_id, receiver_id, message, timestamp)
        VALUES (?, ?, ?, ?)
    ''', (crew_id, manager_id, message, timestamp))

    conn.commit()
    conn.close()

    flash("Message sent successfully.")
    return redirect('/crew_dashboard')
@app.route('/get_messages')
def get_messages():
    username = session.get('username')
    if not username:
        return redirect('/login')

    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch crew_id and manager_id based on username
    cursor.execute('''
        SELECT crew_members.id AS crew_id, management_employees.id AS manager_id
        FROM crew_members
        JOIN users ON crew_members.user_id = users.id
        JOIN management_assignments ON management_assignments.crew_id = crew_members.id
        JOIN management_employees ON management_assignments.employee_id = management_employees.id
        WHERE users.username = ?
    ''', (username,))
    ids = cursor.fetchone()

    if not ids:
        flash("No management employee assigned.")
        conn.close()
        return redirect('/crew_dashboard')

    crew_id, manager_id = ids['crew_id'], ids['manager_id']

    # Fetch messages between crew member and management employee
    cursor.execute('''
        SELECT sender_id, receiver_id, message, timestamp FROM messages
        WHERE (sender_id = ? AND receiver_id = ?)
           OR (sender_id = ? AND receiver_id = ?)
        ORDER BY timestamp ASC
    ''', (crew_id, manager_id, manager_id, crew_id))
    messages = cursor.fetchall()

    print("Fetched messages:", [dict(msg) for msg in messages])  # Debug print

    conn.close()
    return render_template('crew_dashboard.html', messages=messages)


@app.route('/ship_dashboard')
def ship_dashboard():
    username = session.get('username')
    if not username:
        return redirect('/login')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Fetch ship_id from users and ships tables based on username
    cursor.execute('''
        SELECT ships.id, ships.name FROM ships
        JOIN users ON ships.name = users.username
        WHERE users.username = ?
    ''', (username,))
    ship = cursor.fetchone()
    
    if not ship:
        flash('Ship not found.')
        conn.close()
        return redirect('/login')
    
    ship_id = ship['id']
    
    # Fetch current voyage details for the ship
    cursor.execute('''
        SELECT destination, eta, status FROM voyages
        WHERE ship_id = ?
        ORDER BY eta DESC
        LIMIT 1
    ''', (ship_id,))
    voyage = cursor.fetchone()

    # Fetch current crew assigned to the ship
    cursor.execute('''
        SELECT crew_members.name, crew_members.rank, crew_members.status 
        FROM crew_members
        WHERE crew_members.ship_id = ?
    ''', (ship_id,))
    crew_members = cursor.fetchall()

    # Fetch notifications for the ship
    cursor.execute('''
        SELECT message, timestamp FROM notifications
        WHERE ship_id = ?
        ORDER BY timestamp DESC
    ''', (ship_id,))
    notifications = cursor.fetchall()

    # Prepare ship details to display
    ship_details = {
        'name': ship['name'],
        'voyage_destination': voyage['destination'] if voyage else 'No Voyage',
        'voyage_eta': voyage['eta'] if voyage else 'N/A',
        'voyage_status': voyage['status'] if voyage else 'N/A',
        'crew_members': crew_members,  # Add crew members to ship details
        'notifications': notifications  # Add notifications to ship details
    }
    
    conn.close()
    
    # Pass ship details to the template
    return render_template('ship_dashboard.html', ship=ship_details)

#update voyage
@app.route('/update_voyage', methods=['GET', 'POST'])
def update_voyage():
    username = session.get('username')
    if not username:
        return redirect('/login')
    
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch ship_id based on the username
    cursor.execute('''
        SELECT ships.id, ships.name FROM ships
        JOIN users ON ships.name = users.username
        WHERE users.username = ?
    ''', (username,))
    ship = cursor.fetchone()

    if not ship:
        flash('Ship not found.')
        conn.close()
        return redirect('/login')

    ship_id = ship['id']

    if request.method == 'POST':
        # Get form data
        destination = request.form['destination']
        eta = request.form['eta']
        status = request.form['status']
        
        # Check if there's already a voyage, if so, update it
        cursor.execute('''
            SELECT * FROM voyages WHERE ship_id = ?
        ''', (ship_id,))
        existing_voyage = cursor.fetchone()

        if existing_voyage:
            cursor.execute('''
                UPDATE voyages
                SET destination = ?, eta = ?, status = ?
                WHERE ship_id = ?
            ''', (destination, eta, status, ship_id))
        else:
            # If no existing voyage, insert a new one
            cursor.execute('''
                INSERT INTO voyages (ship_id, destination, eta, status)
                VALUES (?, ?, ?, ?)
            ''', (ship_id, destination, eta, status))

        # Insert a notification for the ship
        notification_message = f"New voyage assigned: {destination} - ETA: {eta}"
        cursor.execute('''
            INSERT INTO notifications (ship_id, message)
            VALUES (?, ?)
        ''', (ship_id, notification_message))

        conn.commit()
        flash("Voyage details updated successfully and notification sent.")
        conn.close()
        return redirect('/ship_dashboard')

    # If GET request, render the voyage update form
    return render_template('update_voyage.html', ship_name=ship['name'])

if __name__ == '__main__':
    app.run(debug=True)
