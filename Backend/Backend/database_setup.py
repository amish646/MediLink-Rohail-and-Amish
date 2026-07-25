import sqlite3

def setup_database():
    """Database table create karne ke liye"""
    conn = sqlite3.connect('pharmacy.db')
    cursor = conn.cursor()
    # brand_name ko UNIQUE rakha hai taake duplicates na hon
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            brand_name TEXT UNIQUE, 
            quantity INTEGER
        )
    """)
    conn.commit()
    conn.close()

def update_local_stock(name, qty):
    """Stock update ya insert karne ke liye"""
    conn = sqlite3.connect('pharmacy.db')
    cursor = conn.cursor()
    
    # INSERT OR REPLACE use karne se purana data delete nahi hoga
    # Balkay agar medicine pehle se hai to update hogi, warna nayi add hogi
    cursor.execute("""
        INSERT OR REPLACE INTO Inventory (brand_name, quantity) 
        VALUES (?, ?)
    """, (name, qty))
    
    conn.commit()
    conn.close()
    print(f"✅ Local Stock Updated: {name} = {qty}")

if __name__ == "__main__":
    # 1. Table setup karein
    setup_database()
    
    # 2. Multiple medicines add karein (Ab dono rahengi)
    update_local_stock("Arinac", 45)
    update_local_stock("Panadol", 450)
    update_local_stock("Neurobion", 110)
    update_local_stock("Acefyl", 30)

    print("\n🚀 Sab medicines local database mein save ho chuki hain!")