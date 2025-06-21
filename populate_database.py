import sqlite3
import csv

# Database connection
def connect_db():
    return sqlite3.connect('database.db')

# Insert data into the users table and return the new user_id
def insert_user(conn, username, password, user_type):
    cursor = conn.cursor()
    
    # Check if the username already exists
    cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
    if cursor.fetchone() is not None:
        print(f"User '{username}' already exists. Skipping insertion.")
        return None  # Return None to indicate no insertion was made

    # Insert new user if username doesn't exist
    cursor.execute('INSERT INTO users (username, password, user_type) VALUES (?, ?, ?)', (username, password, user_type))
    conn.commit()
    return cursor.lastrowid
# Populate owners table
def populate_owners(conn):
    with open('owners.csv', 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            username = row['Name']
            password = row['Password']
            no_of_ships = int(row['No. of Ships'])
            
            # Insert user entry and retrieve user_id
            user_id = insert_user(conn, username, password, 'owner')
            
            # Insert owner entry with the user_id
            conn.execute('INSERT INTO owners (user_id, name, no_of_ships) VALUES (?, ?, ?)', (user_id, username, no_of_ships))
    conn.commit()

# Populate ships table
def populate_ships(conn):
    with open('ships.csv', 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            ship_name = row['Ship_name']
            owner_name = row['Owner']
            age = int(row['Age'])
            tonnage = float(row['Tonnage'])
            ship_type = row['Type']
            length = float(row['length'])
            cabins = float(row['cabins'])
            password = row['Password']
            
            # Find the owner_id from the owners table
            cursor = conn.execute('SELECT id FROM owners WHERE name = ?', (owner_name,))
            result = cursor.fetchone()
            owner_id = result[0] if result else None

            if owner_id is None:
                print(f"Warning: Owner '{owner_name}' not found in owners table. Skipping ship '{ship_name}'.")
                continue  # Skip this ship if the owner is not found
            
            # Insert user entry for ship
            user_id = insert_user(conn, ship_name, password, 'ship')
            
            # Insert ship entry with owner_id
            conn.execute('''
                INSERT INTO ships (name, owner_id, age, tonnage, type, length, cabins, password)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (ship_name, owner_id, age, tonnage, ship_type, length, cabins, password))
    conn.commit()

# Populate crew_members table
def populate_crew(conn):
    with open('crew.csv', 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            name = row['Name']
            nationality = row['Nationality']
            preferred_ship_type = row['Preferred Ship Type']
            rank = row['Rank']
            age = int(row['Age'])
            password = row['Password']
            
            # Insert user entry for crew member
            user_id = insert_user(conn, name, password, 'crew')
            
            # Insert crew member entry
            conn.execute('''
                INSERT INTO crew_members (user_id, name, nationality, preferred_ship_type, rank, age)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, name, nationality, preferred_ship_type, rank, age))
    conn.commit()

# Populate management_employees table
def populate_management_employees(conn):
    with open('management_employees.csv', 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            name = row['Name']
            password = row['Password']
            
            # Insert user entry for management employee
            user_id = insert_user(conn, name, password, 'management_employee')
            
            # Insert management employee entry
            conn.execute('INSERT INTO management_employees (user_id, name) VALUES (?, ?)', (user_id, name))
    conn.commit()

# Run population functions
if __name__ == '__main__':
    conn = connect_db()
    try:
        populate_owners(conn)
        populate_ships(conn)
        populate_crew(conn)
        populate_management_employees(conn)
        print("Database populated successfully from CSV files.")
    finally:
        conn.close()
