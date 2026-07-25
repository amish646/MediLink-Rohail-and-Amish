import sqlite3
import hashlib

class DbConnectionManager:
    def __init__(self):
        self.db_name = None
        self.conn = None
        self.cursor = None

    def initialize_db(self, pharmacy_license):
        if pharmacy_license:
            db_hash = hashlib.sha256(pharmacy_license.strip().encode('utf-8')).hexdigest()[:16]
            self.db_name = f"pharmacy_{db_hash}.db"
        else:
            self.db_name = "pharmacy_default.db"

        self.close()

        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        
        self._create_tables()
        self._run_migrations()
        return self.db_name

    def get_connection(self):
        if not self.db_name:
            raise ValueError("Database has not been initialized.")
        return sqlite3.connect(self.db_name)

    def close(self):
        if self.conn:
            try:
                self.conn.close()
            except Exception as e:
                print(f"Error: {e}")
            finally:
                self.conn = None
                self.cursor = None

    def _create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS LocalInventoryV2 (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                brand_name TEXT UNIQUE,
                generic_formula TEXT,
                price REAL,
                expiry_date TEXT,
                quantity INTEGER
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS SalesHistory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_no TEXT,
                sale_date TEXT,
                medicine_name TEXT,
                generic_formula TEXT,
                quantity INTEGER,
                sell_price REAL,
                cost_price REAL,
                discount REAL,
                tax REAL,
                net_total REAL,
                profit REAL
            )
        """)
        self.conn.commit()

    def _run_migrations(self):
        fields = [
            ("manufacturer", "TEXT"),
            ("category", "TEXT"),
            ("form", "TEXT"),
            ("dosage", "TEXT"),
            ("barcode", "TEXT"),
            ("batch_number", "TEXT"),
            ("pack_size", "TEXT"),
            ("cost_price", "REAL"),
            ("retail_price", "REAL"),
            ("tax_rate", "REAL"),
            ("discount_allowed", "REAL")
        ]
        self.cursor.execute("PRAGMA table_info(LocalInventoryV2)")
        existing_cols = [row[1] for row in self.cursor.fetchall()]
        
        migrated = False
        for col_name, col_type in fields:
            if col_name not in existing_cols:
                try:
                    self.cursor.execute(f"ALTER TABLE LocalInventoryV2 ADD COLUMN {col_name} {col_type}")
                    migrated = True
                except Exception as e:
                    print(f"Error: {e}")
        
        if migrated:
            self.conn.commit()
