import sqlite3
from pymongo import MongoClient

# MongoDB Connection
MONGO_URI = "mongodb+srv://amish:AmishPassword123@cluster0.ivayay0.mongodb.net/MediLinkDB?retryWrites=true&w=majority"
client = MongoClient(MONGO_URI)
cloud_db = client['MediLinkDB']

def sync_local_to_cloud(pharmacy_license):
    try:
        # 1. Local SQLite se data uthana
        conn = sqlite3.connect('pharmacy.db')
        conn.row_factory = sqlite3.Row  # Dict-like access ke liye
        cursor = conn.cursor()
        
        # 'brand_name' lazmi check karein ke aapke SQLite table mein yahi column name hai
        cursor.execute("SELECT brand_name, quantity FROM Inventory")
        local_items = cursor.fetchall()
        conn.close()

        if not local_items:
            print(f"⚠️ No local inventory found to sync for {pharmacy_license}.")
            return

        print(f"🔄 Syncing {len(local_items)} items for Pharmacy: {pharmacy_license}...")

        # 2. Har item ko Cloud (MongoDB) mein update karna
        for item in local_items:
            # Data cleaning: Spaces khatam karna aur Title Case (e.g., panadol -> Panadol)
            name = item['brand_name'].strip().title() 
            qty = item['quantity']

            # MongoDB Update Logic
            # Hum 'medicine_name' aur 'pharmacy_license' dono ko check kar rahe hain
            cloud_db.Inventory.update_one(
                {
                    "medicine_name": name, 
                    "pharmacy_license": pharmacy_license
                },
                {
                    "$set": {
                        "medicine_name": name,
                        "pharmacy_license": pharmacy_license,
                        "quantity": qty,
                        "last_updated": "2026-04-23" # Tracking ke liye date (optional)
                    }
                },
                upsert=True # Agar medicine cloud par nahi hai to insert kar dega
            )
            print(f"   [Synced] {name}: {qty} units")
        
        print("✅ Sync Complete! Cloud data is now consistent.")

    except Exception as e:
        print(f"❌ Sync Error: {e}")

if __name__ == "__main__":
    # Pharmacy Device 1: F-10 Branch
    sync_local_to_cloud("PHA-ISB-001")
    
    # Note: Jab aap doosri machine/device simulate karein, 
    # to wahan license "PHA-ISB-002" use karein.