class DbInventoryManager:
    @staticmethod
    def load_db_brands(cursor, known_brands_dict):
        try:
            cursor.execute("SELECT DISTINCT brand_name, generic_formula FROM LocalInventoryV2")
            rows = cursor.fetchall()
            for brand, formula in rows:
                if brand:
                    brand_low = brand.lower().strip()
                    known_brands_dict[brand_low] = (brand.strip(), (formula or "Generic Formula").strip())
        except Exception as e:
            print(f"Error: {e}")

    @staticmethod
    def get_all_inventory(cursor):
        cursor.execute("""
            SELECT brand_name, generic_formula, manufacturer, category, form, dosage, 
                   barcode, batch_number, expiry_date, pack_size, cost_price, 
                   retail_price, tax_rate, discount_allowed, quantity 
            FROM LocalInventoryV2 WHERE quantity > 0
        """)
        return cursor.fetchall()

    @staticmethod
    def add_or_update_stock(cursor, conn, data):
        cursor.execute("""
            INSERT OR REPLACE INTO LocalInventoryV2 (
                brand_name, generic_formula, price, expiry_date, quantity,
                manufacturer, category, form, dosage, barcode, batch_number,
                pack_size, cost_price, retail_price, tax_rate, discount_allowed
            ) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["brand_name"], data["generic_formula"], data["retail_price"], data["expiry_date"], data["quantity"],
            data["manufacturer"], data["category"], data["form"], data["dosage"], data["barcode"], data["batch_number"],
            data["pack_size"], data["cost_price"], data["retail_price"], data["tax_rate"], data["discount_allowed"]
        ))
        conn.commit()

    @staticmethod
    def search_inventory(cursor, query):
        cursor.execute("""
            SELECT brand_name, generic_formula, manufacturer, category, form, dosage, 
                   barcode, batch_number, expiry_date, pack_size, cost_price, 
                   retail_price, tax_rate, discount_allowed, quantity 
            FROM LocalInventoryV2 
            WHERE (LOWER(brand_name) LIKE ? OR LOWER(generic_formula) LIKE ?) AND quantity > 0
        """, (f"%{query}%", f"%{query}%"))
        return cursor.fetchall()

    @staticmethod
    def delete_medicine(cursor, conn, brand_name):
        cursor.execute("DELETE FROM LocalInventoryV2 WHERE brand_name = ?", (brand_name,))
        conn.commit()
