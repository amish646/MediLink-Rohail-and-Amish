import tkinter as tk
from tkinter import ttk

class SalesLogGrid(tk.LabelFrame):
    def __init__(self, parent, controller, main_view):
        super().__init__(parent, text=" 📋 Recent Sales Log ", font=("Segoe UI", 10, "bold"),
                         bg=main_view.card_color, fg=main_view.primary_color, bd=1, relief=tk.SOLID, padx=10, pady=10)
        self.controller = controller
        self.main_view = main_view
        self.setup_ui()

    def setup_ui(self):
        tx_cols = ("Invoice No", "Date/Time", "Items Sold", "Qty", "Total Paid", "Profit")
        self.sales_tree = ttk.Treeview(self, columns=tx_cols, show="headings", height=12, selectmode="browse")
        
        sales_scroll = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.sales_tree.yview)
        sales_hscroll = ttk.Scrollbar(self, orient=tk.HORIZONTAL, command=self.sales_tree.xview)
        self.sales_tree.configure(yscrollcommand=sales_scroll.set, xscrollcommand=sales_hscroll.set)
        
        for col in tx_cols:
            self.sales_tree.heading(col, text=col)
            width = 100
            if col == "Date/Time":
                width = 130
            elif col == "Items Sold":
                width = 200
            self.sales_tree.column(col, width=width)
            
        sales_hscroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.sales_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sales_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def clear_grid(self):
        for child in self.sales_tree.get_children():
            self.sales_tree.delete(child)

    def insert_transaction(self, values):
        self.sales_tree.insert("", tk.END, values=values)
