import tkinter as tk

class SalesKpiRow(tk.Frame):
    def __init__(self, parent, controller, main_view):
        super().__init__(parent, bg=main_view.bg_color)
        self.controller = controller
        self.main_view = main_view
        self.setup_ui()

    def setup_ui(self):
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)
        
        def create_kpi_card(parent, col, title, text_color):
            card = tk.Frame(parent, bg=self.main_view.card_color, highlightthickness=1, highlightbackground="#e2e8f0", bd=0, padx=15, pady=12)
            card.grid(row=0, column=col, padx=4 if col in (1, 2) else (0, 4) if col == 0 else (4, 0), sticky="nsew")
            
            lbl = tk.Label(card, text=title, font=("Segoe UI", 9, "bold"), bg=self.main_view.card_color, fg=self.main_view.text_light)
            lbl.pack(anchor=tk.W)
            
            val_lbl = tk.Label(card, text="Rs 0.00", font=("Segoe UI", 15, "bold"), bg=self.main_view.card_color, fg=text_color)
            val_lbl.pack(anchor=tk.W, pady=(5, 0))
            return val_lbl
            
        self.lbl_revenue_val = create_kpi_card(self, 0, "Revenue (Net Sales)", self.main_view.accent_color)
        self.lbl_profit_val = create_kpi_card(self, 1, "Net Profit Margin", self.main_view.success_color)
        self.lbl_orders_val = create_kpi_card(self, 2, "Total Orders / Invoices", self.main_view.warn_color)
        self.lbl_items_val = create_kpi_card(self, 3, "Total Medicine Items Sold", "#7c3aed")

    def update_kpis(self, revenue, profit, orders, items_sold):
        self.lbl_revenue_val.config(text=f"Rs {revenue:,.2f}")
        self.lbl_profit_val.config(text=f"Rs {profit:,.2f}")
        self.lbl_orders_val.config(text=str(orders))
        self.lbl_items_val.config(text=str(items_sold))
