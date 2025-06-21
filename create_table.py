import sqlite3

def create_tables():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Create users table with user_type and username as unique
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            user_type TEXT NOT NULL
        )
    ''')

    # Create owners table with reference to users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS owners (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,       -- Links to users table for login
            name TEXT NOT NULL,
            no_of_ships INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Create ships table with additional details and owner_id reference
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            owner_id INTEGER,               -- Foreign key linking to owners table
            age INTEGER,
            tonnage REAL,
            type TEXT,
            length REAL,
            cabins REAL,
            password TEXT,
            FOREIGN KEY (owner_id) REFERENCES owners (id)
        )
    ''')

    # Create crew_members table with status and other fields
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS crew_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,       -- Links to users table for login
            name TEXT NOT NULL,
            nationality TEXT,
            preferred_ship_type TEXT,
            rank TEXT,
            age INTEGER,
            status TEXT DEFAULT 'ON-SHORE',
            last_sign_off_date TEXT,
            ship_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (ship_id) REFERENCES ships (id)
        )
    ''')

    # Create preferred_ships table to link crew members with preferred ship types
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS preferred_ships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            crew_id INTEGER,
            ship_id INTEGER,
            FOREIGN KEY (crew_id) REFERENCES crew_members (id),
            FOREIGN KEY (ship_id) REFERENCES ships (id)
        )
    ''')

    # Create management_employees table with user_id and assigned crew/ship fields
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS management_employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,       -- Links to users table for login
            name TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Create management_assignments table to link employees with assigned crew and ships
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS management_assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER,
            crew_id INTEGER,
            ship_id INTEGER,
            FOREIGN KEY (employee_id) REFERENCES management_employees (id),
            FOREIGN KEY (crew_id) REFERENCES crew_members (id),
            FOREIGN KEY (ship_id) REFERENCES ships (id)
        )
    ''')

    # Create voyages table to track ship voyages
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS voyages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ship_id INTEGER,
            destination TEXT NOT NULL,
            eta TEXT NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (ship_id) REFERENCES ships (id)
        )
    ''')

    # Create crew_approvals table to manage approval requests for crew assignments
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS crew_approvals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            crew_id INTEGER,
            ship_id INTEGER,
            status TEXT,  -- Pending, Approved, Declined
            FOREIGN KEY (crew_id) REFERENCES crew_members (id),
            FOREIGN KEY (ship_id) REFERENCES ships (id)
        )
    ''')
    #messaging between crew and management employee
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id INTEGER,
        receiver_id INTEGER,
        message TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (sender_id) REFERENCES crew_members (id),
        FOREIGN KEY (receiver_id) REFERENCES management_employees (id)
    )
''')
    #notification table for ship
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ship_id INTEGER,
        message TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        is_read BOOLEAN DEFAULT FALSE,
        FOREIGN KEY (ship_id) REFERENCES ships (id)
    )
''')


    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_tables()
