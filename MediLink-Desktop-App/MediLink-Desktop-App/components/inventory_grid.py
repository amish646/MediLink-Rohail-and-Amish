import tkinter as tk
from tkinter import ttk

class InventoryGrid(tk.Frame):
    def __init__(self, parent, controller, main_view, on_delete_callback, on_add_to_cart_callback, on_search_callback):
        super().__init__(parent, bg=main_view.bg_color)
        self.controller = controller
        self.main_view = main_view
        self.on_delete = on_delete_callback
        self.on_add_to_cart = on_add_to_cart_callback
        self.on_search = on_search_callback
        self.setup_ui()

    def setup_ui(self):
        search_frame = tk.Frame(self, bg=self.main_view.bg_color, pady=5)
        search_frame.pack(fill=tk.X, pady=(0, 5))

        tk.Label(search_frame, text="🔍 Search Inventory (Name/Formula):", font=("Segoe UI", 9, "bold"), bg=self.main_view.bg_color, fg=self.main_view.text_color).pack(side=tk.LEFT, padx=5)
        self.search_entry = tk.Entry(search_frame, font=("Segoe UI", 10), bg="#ffffff", fg=self.main_view.text_color,
                                     relief=tk.FLAT, bd=0, highlightthickness=1,
                                     highlightbackground="#cbd5e1", highlightcolor=self.main_view.accent_color,
                                     insertbackground=self.main_view.text_color, width=35)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind("<KeyRelease>", self.on_search)

        clear_btn = tk.Button(search_frame, text="Clear Search", font=("Segoe UI", 8, "bold"), bg=self.main_view.text_light, fg="white", relief=tk.FLAT, bd=0, padx=8, command=self.clear_search)
        clear_btn.pack(side=tk.LEFT, padx=5)
        clear_btn.bind("<Enter>", lambda e: clear_btn.config(bg="#475569"))
        clear_btn.bind("<Leave>", lambda e: clear_btn.config(bg=self.main_view.text_light))

        columns = (
            "Medicine Name", "Generic Name", "Manufacturer", "Category", "Form", "Dosage",
            "Barcode", "Batch Number", "Expiry Date", "Pack Size", "Cost Price", "Retail Price",
            "Tax Rate", "Discount Allowed", "Quantity"
        )
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=12, selectmode="extended")
        self.tree.bind("<Delete>", lambda e: self.on_delete())
        self.tree.bind("<BackSpace>", lambda e: self.on_delete())
        self.tree.bind("<Double-1>", self.on_add_to_cart)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100 if col not in ("Medicine Name", "Generic Name", "Manufacturer") else 140)

        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        hscrollbar = ttk.Scrollbar(self, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=scrollbar.set, xscrollcommand=hscrollbar.set)
        
        hscrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def get_search_query(self):
        return self.search_entry.get().strip().lower()

    def clear_search(self):
        self.search_entry.delete(0, tk.END)
        self.on_search()

    def get_selected_rows(self):
        return self.tree.selection()

    def get_row_values(self, item_id):
        return self.tree.item(item_id, "values")

    def clear_grid(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

    def insert_row(self, values):
        self.tree.insert("", tk.END, values=values)
