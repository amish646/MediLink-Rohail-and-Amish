import tkinter as tk
from tkinter import ttk

class InventoryCart(tk.LabelFrame):
    def __init__(self, parent, controller, main_view, on_remove_callback):
        super().__init__(parent, text=" 🛒 Selected Cart (Double-click to remove) ", 
                         font=("Segoe UI", 9, "bold"), bg=main_view.card_color, 
                         fg=main_view.primary_color, bd=1, relief=tk.SOLID, padx=5, pady=5, width=280)
        self.controller = controller
        self.main_view = main_view
        self.on_remove = on_remove_callback
        self.pack_propagate(False)
        self.setup_ui()

    def setup_ui(self):
        cart_columns = ("Medicine Name", "Stock", "Price")
        self.cart_tree = ttk.Treeview(self, columns=cart_columns, show="headings", height=12, selectmode="browse")
        for col in cart_columns:
            self.cart_tree.heading(col, text=col)
            self.cart_tree.column(col, width=90 if col != "Medicine Name" else 110)

        cart_scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.cart_tree.yview)
        self.cart_tree.configure(yscrollcommand=cart_scrollbar.set)
        self.cart_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        cart_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.cart_tree.bind("<Double-1>", self.on_remove)

    def get_selected_rows(self):
        return self.cart_tree.selection()

    def get_row_values(self, item_id):
        return self.cart_tree.item(item_id, "values")

    def clear_grid(self):
        for row in self.cart_tree.get_children():
            self.cart_tree.delete(row)

    def insert_row(self, values):
        self.cart_tree.insert("", tk.END, values=values)
