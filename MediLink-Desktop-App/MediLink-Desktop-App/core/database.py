from core.db_connection import DbConnectionManager
from core.db_inventory import DbInventoryManager
from core.db_sales import DbSalesManager

class DatabaseManager:
    def __init__(self):
        self._connection_manager = DbConnectionManager()

    @property
    def db_name(self):
        return self._connection_manager.db_name

    @property
    def conn(self):
        return self._connection_manager.conn

    @property
    def cursor(self):
        return self._connection_manager.cursor

    def initialize_db(self, pharmacy_license):
        return self._connection_manager.initialize_db(pharmacy_license)

    def get_connection(self):
        return self._connection_manager.get_connection()

    def close(self):
        self._connection_manager.close()

    def load_db_brands(self, known_brands_dict):
        DbInventoryManager.load_db_brands(self.cursor, known_brands_dict)

    def get_all_inventory(self):
        return DbInventoryManager.get_all_inventory(self.cursor)

    def add_or_update_stock(self, data):
        DbInventoryManager.add_or_update_stock(self.cursor, self.conn, data)

    def search_inventory(self, query):
        return DbInventoryManager.search_inventory(self.cursor, query)

    def delete_medicine(self, brand_name):
        DbInventoryManager.delete_medicine(self.cursor, self.conn, brand_name)

    def record_sale(self, invoice_no, sale_date, sales_list):
        DbSalesManager.record_sale(self.cursor, self.conn, invoice_no, sale_date, sales_list)

    def get_sales_analytics(self, period):
        return DbSalesManager.get_sales_analytics(self.cursor, period)

    def get_recent_transactions(self, period):
        return DbSalesManager.get_recent_transactions(self.cursor, period)

    def get_top_selling_products(self, period, limit=10):
        return DbSalesManager.get_top_selling_products(self.cursor, period, limit)
