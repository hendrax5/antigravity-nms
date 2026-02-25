import os
import psycopg2

def run_migration():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL is not set.")
        return
        
    try:
        conn = psycopg2.connect(db_url)
        conn.autocommit = True
        cur = conn.cursor()
        
        # Check if connection_method column exists
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='devices' and column_name='connection_method';
        """)
        if not cur.fetchone():
            print("Adding connection_method column...")
            cur.execute("ALTER TABLE devices ADD COLUMN connection_method VARCHAR DEFAULT 'ssh' NOT NULL;")
            
        # Check if port column exists
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='devices' and column_name='port';
        """)
        if not cur.fetchone():
            print("Adding port column...")
            cur.execute("ALTER TABLE devices ADD COLUMN port INTEGER DEFAULT 22 NOT NULL;")
            
        # Check if snmp_community column exists
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='devices' and column_name='snmp_community';
        """)
        if not cur.fetchone():
            print("Adding snmp_community column...")
            cur.execute("ALTER TABLE devices ADD COLUMN snmp_community VARCHAR;")

        # Make credential_id nullable
        print("Altering credential_id to DROP NOT NULL...")
        cur.execute("ALTER TABLE devices ALTER COLUMN credential_id DROP NOT NULL;")
        
        print("Migration completed successfully.")
        
    except Exception as e:
        print(f"Migration failed: {e}")
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    run_migration()
