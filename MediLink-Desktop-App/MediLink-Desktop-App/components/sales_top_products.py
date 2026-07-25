import tkinter as tk
from tkinter import ttk

class SalesTopProductsGrid(tk.LabelFrame):
    def __init__(self, parent, controller, main_view):
        super().__init__(parent, text=" 🏆 Top 10 Selling Products ", font=("Segoe UI", 10, "bold"),
                         bg=main_view.card_color, fg=main_view.primary_color, bd=1, relief=tk.SOLID, padx=10, pady=10)
        self.controller = controller
        self.main_view = main_view
        self.setup_ui()

    def setup_ui(self):
        top_cols = ("Medicine Name", "Formula", "Qty Sold", "Revenue", "Profit")
        self.top_products_tree = ttk.Treeview(self, columns=top_cols, show="headings", height=12, selectmode="browse")
        
        top_scroll = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.top_products_tree.yview)
        top_hscroll = ttk.Scrollbar(self, orient=tk.HORIZONTAL, command=self.top_products_tree.xview)
        self.top_products_tree.configure(yscrollcommand=top_scroll.set, xscrollcommand=top_hscroll.set)
        
        for col in top_cols:
            self.top_products_tree.heading(col, text=col)
            self.top_products_tree.column(col, width=120 if col not in ("Medicine Name", "Formula") else 140)
            
        top_hscroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.top_products_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        top_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def clear_grid(self):
        for child in self.top_products_tree.get_children():
            self.top_products_tree.delete(child)

    def insert_product(self, values):
        self.top_products_tree.insert("", tk.END, values=values)
