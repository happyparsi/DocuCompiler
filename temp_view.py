import sqlite3
import pandas as pd

def view_db():
    conn = sqlite3.connect('docucompiler.db')
    
    # Get all tables
    tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
    
    with open('db_sample.txt', 'w', encoding='utf-8') as f:
        for t in tables:
            table_name = t[0]
            f.write(f"\n{'='*50}\n")
            f.write(f"TABLE: {table_name}\n")
            f.write(f"{'='*50}\n")
            
            # Get schema
            schema = conn.execute(f"PRAGMA table_info({table_name});").fetchall()
            f.write("Schema:\n")
            for col in schema:
                f.write(f"  - {col[1]} ({col[2]})\n")
                
            # Get sample rows
            f.write("\nSample Rows (Limit 5):\n")
            try:
                df = pd.read_sql_query(f"SELECT * FROM {table_name} LIMIT 5", conn)
                f.write(df.to_string())
            except Exception as e:
                f.write(f"Error reading table: {e}")
            f.write("\n")
            
    conn.close()
    print("Database sample exported to db_sample.txt")

if __name__ == '__main__':
    view_db()
