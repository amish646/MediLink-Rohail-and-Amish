from pymongo import MongoClient
import sqlite3

# Cloud DB
uri = "mongodb+srv://amish:AmishPassword123@cluster0.ivayay0.mongodb.net/MediLinkDB?retryWrites=true&w=majority"
client = MongoClient(uri)
db = client['MediLinkDB']

print("Deleting all Inventory records from Cloud...")
db.Inventory.delete_many({})

print("Deleting all Prescriptions from Cloud...")
db.Prescriptions.delete_many({})

print("Resetting Pharmacies in Cloud...")
db.Pharmacies.delete_many({})
db.Pharmacies.insert_many([
    {"name": "MediLink F-10 Branch", "license_no": "PHA-ISB-001", "location": {"type": "Point", "coordinates": [73.01, 33.69]}},
    {"name": "MediLink G-11 Branch", "license_no": "PHA-ISB-002", "location": {"type": "Point", "coordinates": [72.99, 33.67]}}
])

# Local DB
print("Deleting all Local Inventory records from SQLite...")
try:
    conn = sqlite3.connect('e:/Main/FYP-1/Final/Backend/pharmacy.db')
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS LocalInventoryV2")
    conn.commit()
    conn.close()
except Exception as e:
    print("Local DB error:", e)

print("All data successfully cleared! You can now start fresh.")
