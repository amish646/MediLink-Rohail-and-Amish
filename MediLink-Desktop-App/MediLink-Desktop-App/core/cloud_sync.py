from pymongo import MongoClient
import datetime
import sqlite3

class CloudSyncManager:
    def __init__(self, mongo_uri):
        self.mongo_uri = mongo_uri

    def sync_local_to_cloud(self, db_name, pharmacy_name, pharmacy_license, lat, lng):
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT brand_name, generic_formula, price, expiry_date, quantity,
                   manufacturer, category, form, dosage, barcode, batch_number,
                   pack_size, cost_price, retail_price, tax_rate, discount_allowed
            FROM LocalInventoryV2
        """)
        local_items = cursor.fetchall()
        conn.close()

        client = MongoClient(self.mongo_uri, serverSelectionTimeoutMS=5000)
        cloud_db = client['MediLinkDB']

        local_names = {item[0] for item in local_items}
        cloud_db.Inventory.delete_many({
            "pharmacy_license": pharmacy_license,
            "medicine_name": {"$nin": list(local_names)}
        })

        cloud_db.Pharmacies.update_one(
            {"license_no": pharmacy_license},
            {"$set": {
                "name": pharmacy_name,
                "license_no": pharmacy_license,
                "location": {
                    "type": "Point",
                    "coordinates": [float(lng), float(lat)]
                }
            }},
            upsert=True
        )

        synced_count = 0
        for item in local_items:
            (name, formula, price, expiry, qty, manufacturer, category, form,
             dosage, barcode, batch, pack_size, cost_price, retail_price,
             tax_rate, discount) = item

            cloud_db.GlobalMedicines.update_one(
                {"brand_name": name},
                {"$set": {"brand_name": name, "generic_formula": formula}},
                upsert=True
            )

            cloud_db.Inventory.update_one(
                {"medicine_name": name, "pharmacy_license": pharmacy_license},
                {"$set": {
                    "brand_name": name,
                    "medicine_name": name,
                    "generic_formula": formula,
                    "price": price,
                    "expiry_date": expiry,
                    "pharmacy_license": pharmacy_license,
                    "quantity": qty,
                    "manufacturer": manufacturer,
                    "category": category,
                    "form": form,
                    "dosage": dosage,
                    "barcode": barcode,
                    "batch_number": batch,
                    "pack_size": pack_size,
                    "cost_price": cost_price,
                    "retail_price": retail_price,
                    "tax_rate": tax_rate,
                    "discount_allowed": discount,
                    "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }},
                upsert=True
            )
            synced_count += 1
            
        return synced_count

    def pull_cloud_to_local(self, db_manager, pharmacy_license):
        if not pharmacy_license:
            return 0
            
        client = MongoClient(self.mongo_uri, serverSelectionTimeoutMS=3000)
        cloud_db = client['MediLinkDB']
        cloud_items = list(cloud_db.Inventory.find({"pharmacy_license": pharmacy_license}))
        
        pulled_count = 0
        if cloud_items:
            conn = db_manager.get_connection()
            cursor = conn.cursor()
            
            for item in cloud_items:
                brand_name = item.get("brand_name", item.get("medicine_name"))
                formula = item.get("generic_formula", "N/A")
                price = item.get("price", item.get("retail_price", 0.0))
                expiry = item.get("expiry_date", "12/27")
                qty = item.get("quantity", 0)
                manufacturer = item.get("manufacturer", "Unknown")
                category = item.get("category", "General")
                form = item.get("form", "Tablet")
                dosage = item.get("dosage", "N/A")
                barcode = item.get("barcode", "N/A")
                batch = item.get("batch_number", "N/A")
                pack_size = item.get("pack_size", "10s")
                cost_price = item.get("cost_price", 0.0)
                retail_price = item.get("retail_price", price)
                tax_rate = item.get("tax_rate", 0.0)
                discount = item.get("discount_allowed", 0.0)
                
                cursor.execute("""
                    INSERT OR REPLACE INTO LocalInventoryV2 (
                        brand_name, generic_formula, price, expiry_date, quantity,
                        manufacturer, category, form, dosage, barcode, batch_number,
                        pack_size, cost_price, retail_price, tax_rate, discount_allowed
                    ) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    brand_name, formula, retail_price, expiry, qty,
                    manufacturer, category, form, dosage, barcode, batch,
                    pack_size, cost_price, retail_price, tax_rate, discount
                ))
                pulled_count += 1
                
            conn.commit()
            conn.close()
            
        return pulled_count

    def update_single_item_stock(self, pharmacy_license, medicine_name, new_qty, sell_price):
        try:
            client = MongoClient(self.mongo_uri, serverSelectionTimeoutMS=2000)
            cloud_db = client['MediLinkDB']
            cloud_db.Inventory.update_one(
                {
                    "medicine_name": medicine_name,
                    "pharmacy_license": pharmacy_license
                },
                {
                    "$set": {
                        "quantity": new_qty,
                        "price": sell_price,
                        "retail_price": sell_price,
                        "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                }
            )
        except Exception as e:
            print(f"Failed to update single item '{medicine_name}' in MongoDB: {e}")

    def delete_single_item(self, pharmacy_license, medicine_name):
        try:
            client = MongoClient(self.mongo_uri, serverSelectionTimeoutMS=2000)
            cloud_db = client['MediLinkDB']
            cloud_db.Inventory.delete_one({
                "medicine_name": medicine_name, 
                "pharmacy_license": pharmacy_license
            })
        except Exception as e:
            print(f"Failed to delete single item '{medicine_name}' from MongoDB: {e}")
