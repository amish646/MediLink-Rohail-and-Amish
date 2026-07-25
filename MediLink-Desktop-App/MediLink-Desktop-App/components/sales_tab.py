import tkinter as tk
from tkinter import ttk
from components.sales_kpis import SalesKpiRow
from components.sales_log import SalesLogGrid
from components.sales_top_products import SalesTopProductsGrid

class SalesTab(tk.Frame):
    def __init__(self, parent, controller, main_view):
        super().__init__(parent, bg=main_view.bg_color)
        self.controller = controller
        self.main_view = main_view
        self.setup_ui()

    def setup_ui(self):
        main_sales_frame = tk.Frame(self, bg=self.main_view.bg_color)
        main_sales_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        ctrl_frame = tk.Frame(main_sales_frame, bg=self.main_view.bg_color)
        ctrl_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_lbl = tk.Label(ctrl_frame, text="📊 Sales & Revenue Analytics Dashboard", 
                             font=("Segoe UI", 14, "bold"), bg=self.main_view.bg_color, fg=self.main_view.primary_color)
        title_lbl.pack(side=tk.LEFT)
        
        filter_subframe = tk.Frame(ctrl_frame, bg=self.main_view.bg_color)
        filter_subframe.pack(side=tk.RIGHT)
        
        tk.Label(filter_subframe, text="Period Filter:", font=("Segoe UI", 9, "bold"), 
                 bg=self.main_view.bg_color, fg=self.main_view.text_color).pack(side=tk.LEFT, padx=5)
        
        self.sales_period_combo = ttk.Combobox(filter_subframe, values=["Today", "This Month", "All Time"], 
                                               state="readonly", width=12, font=("Segoe UI", 9))
        self.sales_period_combo.pack(side=tk.LEFT, padx=5)
        self.sales_period_combo.set("Today")
        self.sales_period_combo.bind("<<ComboboxSelected>>", lambda e: self.load_sales_analytics())
        
        refresh_btn = tk.Button(filter_subframe, text="🔄 Refresh Stats", font=("Segoe UI", 9, "bold"), 
                                bg=self.main_view.accent_color, fg="white", relief=tk.FLAT, bd=0, padx=12, pady=4,
                                command=self.load_sales_analytics)
        refresh_btn.pack(side=tk.LEFT, padx=5)
        refresh_btn.bind("<Enter>", lambda e: refresh_btn.config(bg="#1d4ed8"))
        refresh_btn.bind("<Leave>", lambda e: refresh_btn.config(bg=self.main_view.accent_color))
        
        self.kpi_row = SalesKpiRow(main_sales_frame, self.controller, self.main_view)
        self.kpi_row.pack(fill=tk.X, pady=(0, 15))
        
        tables_frame = tk.Frame(main_sales_frame, bg=self.main_view.bg_color)
        tables_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_grid = SalesLogGrid(tables_frame, self.controller, self.main_view)
        self.log_grid.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))

        self.top_grid = SalesTopProductsGrid(tables_frame, self.controller, self.main_view)
        self.top_grid.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(8, 0))

    def load_sales_analytics(self):
        self.log_grid.clear_grid()
        self.top_grid.clear_grid()
            
        period = self.sales_period_combo.get()
        
        try:
            rev, prof, orders, items = self.controller.db_manager.get_sales_analytics(period)
            self.kpi_row.update_kpis(rev, prof, orders, items)
            
            recent_sales = self.controller.db_manager.get_recent_transactions(period)
            for row in recent_sales:
                inv, dt, meds, qty, total, profit = row
                self.log_grid.insert_transaction((
                    inv, dt, meds, qty, f"Rs {total:,.2f}", f"Rs {profit:,.2f}"
                ))
                
            top_products = self.controller.db_manager.get_top_selling_products(period)
            for row in top_products:
                name, formula, qty, total, profit = row
                self.top_grid.insert_product((
                    name, formula, qty, f"Rs {total:,.2f}", f"Rs {profit:,.2f}"
                ))
                
        except Exception as e:
            print(f"Error updating sales analytics: {e}")
