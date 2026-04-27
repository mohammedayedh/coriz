import sqlite3

def create_database():
    # Create or connect to the database
    conn = sqlite3.connect('login_system.db')
    cursor = conn.cursor()
    
    # Create Roles_table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Roles_table (
        Role_id INTEGER PRIMARY KEY AUTOINCREMENT,
        Role_name TEXT NOT NULL,
        Permissions TEXT,
        Active BOOLEAN DEFAULT 1
    )
    ''')
    
    # Create Users_table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users_table (
        User_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        Email TEXT UNIQUE NOT NULL,
        Password TEXT NOT NULL,
        Role_id INTEGER,
        Active BOOLEAN DEFAULT 1,
        Time_create DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (Role_id) REFERENCES Roles_table(Role_id)
    )
    ''')
    
    # Create Login_Attempts_table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Login_Attempts_table (
        Attempt_id INTEGER PRIMARY KEY AUTOINCREMENT,
        Time_login DATETIME DEFAULT CURRENT_TIMESTAMP,
        username_attempt TEXT NOT NULL,
        User_id INTEGER,
        FOREIGN KEY (User_id) REFERENCES Users_table(User_id)
    )
    ''')
    
    # Insert default roles
    default_roles = [
        ('Admin', 'all_permissions'),
        ('User', 'basic_permissions'),
        ('Guest', 'limited_permissions')
    ]
    
    cursor.executemany('''
    INSERT OR IGNORE INTO Roles_table (Role_name, Permissions) 
    VALUES (?, ?)
    ''', default_roles)
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    print("Database and tables created successfully!")
    
####################################### function to test database ###############################################################

# def test_database():
#     """Test function to verify the database structure"""
#     conn = sqlite3.connect('login_system.db')
#     cursor = conn.cursor()
    
#     # Check tables
#     cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
#     tables = cursor.fetchall()
#     print("Tables in database:")
#     for table in tables:
#         print(f"- {table[0]}")
    
#     # Check Roles_table structure
#     cursor.execute("PRAGMA table_info(Roles_table)")
#     roles_columns = cursor.fetchall()
#     print("\nRoles_table columns:")
#     for col in roles_columns:
#         print(f"- {col[1]} ({col[2]})")
    
#     # Check Users_table structure
#     cursor.execute("PRAGMA table_info(Users_table)")
#     users_columns = cursor.fetchall()
#     print("\nUsers_table columns:")
#     for col in users_columns:
#         print(f"- {col[1]} ({col[2]})")
    
#     # Check Login_Attempts_table structure
#     cursor.execute("PRAGMA table_info(Login_Attempts_table)")
#     login_columns = cursor.fetchall()
#     print("\nLogin_Attempts_table columns:")
#     for col in login_columns:
#         print(f"- {col[1]} ({col[2]})")
    
#     conn.close()

if __name__ == "__main__":
    create_database()
    # test_database()