
import sqlite3

def check_user():
    try:
        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        
        # Check by UID (ID) and Username
        print("Checking for User ID 118 or username 'mbygrave'...")
        cursor.execute("SELECT id, username, email, is_active FROM auth_user WHERE id = 118 OR username = 'mbygrave'")
        rows = cursor.fetchall()
        
        if rows:
            for row in rows:
                print(f"UID: #{row[0]} | Username: {row[1]} | Email: {row[2]} | Active: {row[3]}")
        else:
            print("No matching user found in the LOCAL database.")
            
        conn.close()
    except Exception as e:
        print(f"Error checking database: {e}")

if __name__ == "__main__":
    check_user()
