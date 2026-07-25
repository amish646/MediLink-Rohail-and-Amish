import datetime

class DbSalesManager:
    @staticmethod
    def record_sale(cursor, conn, invoice_no, sale_date, sales_list):
        for sale in sales_list:
            item = sale["item"]
            sell_qty = sale["sell_qty"]
            sell_price = sale["sell_price"]
            new_qty = item["current_qty"] - sell_qty

            cursor.execute("""
                UPDATE LocalInventoryV2 
                SET quantity = ?, price = ?, retail_price = ? 
                WHERE brand_name = ?
            """, (new_qty, sell_price, sell_price, item["name"]))

            sub = sell_qty * sell_price
            disc = sub * (item.get("discount_rate", 0.0) / 100.0)
            taxable = sub - disc
            tax = taxable * (item.get("tax_rate", 0.0) / 100.0)
            net = taxable + tax
            cost_price = item.get("cost_price", 0.0)
            profit = sub - disc - (cost_price * sell_qty)

            cursor.execute("""
                INSERT INTO SalesHistory (
                    invoice_no, sale_date, medicine_name, generic_formula,
                    quantity, sell_price, cost_price, discount, tax, net_total, profit
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                invoice_no, sale_date, item["name"], item["formula"],
                sell_qty, sell_price, cost_price, disc, tax, net, profit
            ))
        conn.commit()

    @staticmethod
    def get_sales_analytics(cursor, period):
        query_date, params = DbSalesManager._build_period_filter(period)
        sql = f"""
            SELECT 
                COALESCE(SUM(net_total), 0.0), 
                COALESCE(SUM(profit), 0.0), 
                COUNT(DISTINCT invoice_no), 
                COALESCE(SUM(quantity), 0)
            FROM SalesHistory
            {query_date}
        """
        cursor.execute(sql, params)
        return cursor.fetchone()

    @staticmethod
    def get_recent_transactions(cursor, period):
        query_date, params = DbSalesManager._build_period_filter(period)
        sql = f"""
            SELECT 
                invoice_no, 
                MIN(sale_date), 
                GROUP_CONCAT(medicine_name || ' (' || quantity || ')', ', '), 
                SUM(quantity), 
                SUM(net_total), 
                SUM(profit) 
            FROM SalesHistory 
            {query_date} 
            GROUP BY invoice_no 
            ORDER BY MIN(sale_date) DESC
        """
        cursor.execute(sql, params)
        return cursor.fetchall()

    @staticmethod
    def get_top_selling_products(cursor, period, limit=10):
        query_date, params = DbSalesManager._build_period_filter(period)
        sql = f"""
            SELECT 
                medicine_name, 
                generic_formula, 
                SUM(quantity), 
                SUM(net_total), 
                SUM(profit) 
            FROM SalesHistory 
            {query_date} 
            GROUP BY medicine_name 
            ORDER BY SUM(quantity) DESC 
            LIMIT ?
        """
        params.append(limit)
        cursor.execute(sql, params)
        return cursor.fetchall()

    @staticmethod
    def _build_period_filter(period):
        query_date = ""
        params = []
        if period == "Today":
            query_date = "WHERE sale_date LIKE ?"
            params.append(f"{datetime.datetime.now().strftime('%Y-%m-%d')}%")
        elif period == "This Month":
            query_date = "WHERE sale_date LIKE ?"
            params.append(f"{datetime.datetime.now().strftime('%Y-%m')}%")
        return query_date, params
