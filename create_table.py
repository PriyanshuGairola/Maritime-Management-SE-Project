import sqlite3

def create_tables():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            user_type TEXT NOT NULL
        )
    ''')

    # Create ships table
 # Create ships table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ships (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        type TEXT NOT NULL,
        flag TEXT,
        imo_number TEXT,
        gross_tonnage INTEGER,
        net_tonnage INTEGER,
        quality TEXT,
        age INTEGER,
        status TEXT  -- For managing fleet status
    )
''')

# Create crew_members table with rank column and ship_id added
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS crew_members (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        status TEXT NOT NULL,
        rank TEXT,  -- Add the rank column here
        ship_id INTEGER,
        FOREIGN KEY (ship_id) REFERENCES ships (id)
    )
''')

# Create crew_readiness table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS crew_readiness (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            crew_id INTEGER,
            readiness_date TEXT,
            status TEXT,
            FOREIGN KEY (crew_id) REFERENCES crew_members (id)
        )
    ''')

    # Create preferred_ships table (example for on-shore preferred ships)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS preferred_ships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            crew_id INTEGER,
            ship_id INTEGER,
            FOREIGN KEY (crew_id) REFERENCES crew_members (id),
            FOREIGN KEY (ship_id) REFERENCES ships (id)
        )
    ''')

    # Create voyages table
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



    # Create crew_approvals table
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


    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_tables()
