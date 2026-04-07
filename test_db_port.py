import psycopg2
import sys

settings_db = {
    'dbname': 'medical_db',
    'user': 'postgres',
    'password': 'malik',
    'host': 'localhost',
    'port': '5432'
}

print(f"Testing connection on port {settings_db['port']}...")
try:
    conn = psycopg2.connect(**settings_db)
    print("SUCCESS: Connected to medical_db on port 5432!")
    conn.close()
except Exception as e:
    print(f"FAILED to connect to medical_db on port 5432: {e}")
    
    # Try default 'postgres' db
    print("\nTesting connection to 'postgres' db on port 5432...")
    try:
        conn = psycopg2.connect(dbname='postgres', user='postgres', password='malik', host='localhost', port='5432')
        print("SUCCESS: Connected to 'postgres' db on port 5432!")
        
        # Check if medical_db exists
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM pg_database WHERE datname='medical_db';")
        exists = cur.fetchone()
        if exists:
            print("INFO: 'medical_db' EXISTS on this server.")
        else:
            print("WARNING: 'medical_db' does NOT exist on this server.")
        conn.close()
    except Exception as e2:
        print(f"FAILED to connect to 'postgres' db on port 5432: {e2}")
