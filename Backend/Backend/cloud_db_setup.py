from pymongo import MongoClient

uri = "mongodb+srv://amish:AmishPassword123@cluster0.ivayay0.mongodb.net/MediLinkDB?retryWrites=true&w=majority"
client = MongoClient(uri)
db = client['MediLinkDB']

def setup_cloud_db():
    print("🚀 MediLink Cloud Setup Started...")

    # 1. Pharmacies (Registration)
    db.Pharmacies.delete_many({})
    db.Pharmacies.insert_many([
        {"name": "MediLink F-10 Branch", "license_no": "PHA-ISB-001", "location": {"type": "Point", "coordinates": [73.01, 33.69]}},
        {"name": "MediLink G-11 Branch", "license_no": "PHA-ISB-002", "location": {"type": "Point", "coordinates": [72.99, 33.67]}}
    ])
    print("✅ Branches Registered.")

    # 2. Global Catalog (Medicines ki Info)
    # Is se user ko formula pata chalta hai (BioBERT AI ke liye zaruri hai)
    db.GlobalMedicines.delete_many({})
    db.GlobalMedicines.insert_many([
        {"brand_name": "Panadol", "generic_formula": "Paracetamol"},
        {"brand_name": "Arinac", "generic_formula": "Ibuprofen"},
        {"brand_name": "Neurobion", "generic_formula": "Vitamin B Complex"}
    ])
    print("✅ Global Catalog Updated.")

    # 3. Distributed Inventory (Linking Stock to Branches)
    db.Inventory.delete_many({})
    db.Inventory.insert_many([
        # Panadol sirf PHA-ISB-001 (F-10) mein hai
        {"medicine_name": "Panadol", "pharmacy_license": "PHA-ISB-001", "quantity": 150},
        
        # Arinac PHA-ISB-001 (F-10) aur PHA-ISB-002 (G-11) dono mein hai
        {"medicine_name": "Arinac", "pharmacy_license": "PHA-ISB-001", "quantity": 45},
        {"medicine_name": "Arinac", "pharmacy_license": "PHA-ISB-002", "quantity": 80}
    ])
    print("✅ Distributed Inventory Linked Successfully!")

if __name__ == "__main__":
    setup_cloud_db()