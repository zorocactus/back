import psycopg2
import sys

settings_db = {
    'dbname': 'medical_db',
    'user': 'postgres',
    'password': 'malik',
    'host': 'localhost',
    'port': '5432'
}

print(f"Diagnosing connection to {settings_db['dbname']} on port {settings_db['port']}...")
try:
    conn = psycopg2.connect(**settings_db)
    print("SUCCESS: Connected!")
    conn.close()
except Exception as e:
    print("Caught connection error. Attempting to decode message...")
    try:
        # Try to decode from bytes if available, or just re-encode/decode the string
        # Psycopg2 errors on Windows often come in the system's local encoding (e.g. cp1252)
        error_msg = str(e)
        print(f"Raw string representation: {repr(error_msg)}")
        
        # If the string contains the undecodable byte, we might need to catch the raw sub-exception
        # But usually, reaching this point means 'str(e)' itself failed or is mangled.
    except Exception as e2:
        print(f"Could not even stringify exception: {e2}")

    # More robust way: try connecting to 'postgres' first to see if server is alive
    print("\nChecking if PostgreSQL server is alive by connecting to 'postgres' system db...")
    try:
        conn = psycopg2.connect(dbname='postgres', user='postgres', password='malik', host='localhost', port='5432')
        print("SUCCESS: PostgreSQL is alive and password 'malik' is correct!")
        
        cur = conn.cursor()
        cur.execute("SELECT datname FROM pg_database;")
        dbs = [row[0] for row in cur.fetchall()]
        print(f"Available databases: {dbs}")
        
        if 'medical_db' in dbs:
            print("INFO: 'medical_db' EXISTS.")
        else:
            print("ERROR: 'medical_db' DOES NOT EXIST. You may need to create it.")
        conn.close()
    except Exception as e3:
        # Catch and decode manually
        print("Failed to connect to 'postgres' db.")
        # Sometimes you can get the raw bytes from the exception if you're lucky, 
        # but in Python 3 it's usually already tried to decode.
        print(f"Postgres system db error: {e3}")
