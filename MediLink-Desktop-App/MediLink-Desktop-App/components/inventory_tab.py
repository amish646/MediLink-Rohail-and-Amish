import tkinter as tk
from tkinter import ttk, messagebox
import threading
from components.inventory_form import InventoryForm
from components.inventory_grid import InventoryGrid
from components.inventory_cart import InventoryCart
from components.checkout_dialog import CheckoutDialog

class InventoryTab(tk.Frame):
    def __init__(self, parent, controller, main_view):
        super().__init__(parent, bg=main_view.bg_color)
        self.controller = controller
        self.main_view = main_view
        self.search_job = None
        self.setup_ui()

    def setup_ui(self):
        self.form_panel = InventoryForm(self, self.controller, self.main_view)
        self.form_panel.pack(fill=tk.X, padx=15, pady=10)

        btn_frame = tk.Frame(self, bg=self.main_view.bg_color)
        btn_frame.pack(fill=tk.X, padx=15, pady=5)

        def style_btn(text, cmd, normal_bg, hover_bg):
            btn = tk.Button(btn_frame, text=text, bg=normal_bg, fg="white", font=("Segoe UI", 9, "bold"), padx=10, pady=8, relief=tk.FLAT, bd=0, command=cmd)
            btn.pack(side=tk.LEFT, padx=6, expand=True, fill=tk.X)
            btn.bind("<Enter>", lambda e: btn.config(bg=hover_bg))
            btn.bind("<Leave>", lambda e: btn.config(bg=normal_bg))
            return btn

        self.add_btn = style_btn("➕ Add/Update Stock", self.add_local_stock, "#2563eb", "#1d4ed8")
        self.add_to_cart_btn = style_btn("🛒 Add Selected to Cart", self.add_to_cart, "#2563eb", "#1d4ed8")
        self.sell_btn = style_btn("💳 Checkout Cart (0)", self.sell_medicine, "#2563eb", "#1d4ed8")
        self.delete_btn = style_btn("🗑️ Delete Selected", self.delete_selected_medicines, "#2563eb", "#1d4ed8")
        self.sync_btn = style_btn("☁️ Sync to Cloud", self.sync_to_cloud, "#2563eb", "#1d4ed8")

        table_frame = tk.Frame(self, bg=self.main_view.bg_color)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        self.grid_panel = InventoryGrid(table_frame, self.controller, self.main_view, 
                                        self.delete_selected_medicines, self.add_to_cart, self.filter_inventory)
        self.grid_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.cart_panel = InventoryCart(table_frame, self.controller, self.main_view, self.remove_from_cart)
        self.cart_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False, padx=(12, 0))

    def load_local_inventory(self):
        self.grid_panel.clear_grid()
        try:
            rows = self.controller.db_manager.get_all_inventory()
            for r in rows:
                cost_price = f"Rs {r[10]:.2f}" if r[10] is not None else "N/A"
                retail_price = f"Rs {r[11]:.2f}" if r[11] is not None else "N/A"
                tax_rate = f"{r[12]}%" if r[12] is not None else "N/A"
                discount = f"{r[13]}%" if r[13] is not None else "N/A"
                
                self.grid_panel.insert_row((
                    r[0], r[1], r[2], r[3], r[4], r[5],
                    r[6], r[7], r[8], r[9], cost_price,
                    retail_price, tax_rate, discount, r[14]
                ))
        except Exception as e:
            print(f"Error loading inventory tree: {e}")

    def add_local_stock(self):
        vals = self.form_panel.get_form_values()
        
        name = vals["brand_name"]
        if not name:
            messagebox.showwarning("Input Error", "Medicine Name is required.")
            return

        qty_str = vals["quantity_str"]
        retail_price_str = vals["retail_price_str"]

        if not qty_str or not retail_price_str:
            messagebox.showwarning("Input Error", "Quantity and Retail Price are required.")
            return

        try:
            qty = int(qty_str)
            retail_price = float(retail_price_str)
        except ValueError:
            messagebox.showwarning("Input Error", "Quantity and Retail Price must be valid numbers.")
            return

        cost_price = 0.0
        if vals["cost_price_str"]:
            try:
                cost_price = float(vals["cost_price_str"])
            except ValueError:
                messagebox.showwarning("Input Error", "Cost Price must be a valid number.")
                return

        tax_rate = 0.0
        if vals["tax_rate_str"]:
            try:
                tax_rate = float(vals["tax_rate_str"])
            except ValueError:
                messagebox.showwarning("Input Error", "Tax Rate must be a valid number.")
                return

        discount = 0.0
        if vals["discount_str"]:
            try:
                discount = float(vals["discount_str"])
            except ValueError:
                messagebox.showwarning("Input Error", "Discount must be a valid number.")
                return

        data = {
            "brand_name": name, "generic_formula": vals["generic_formula"], "expiry_date": vals["expiry_date"], "quantity": qty,
            "manufacturer": vals["manufacturer"], "category": vals["category"], "form": vals["form"], "dosage": vals["dosage"],
            "barcode": vals["barcode"], "batch_number": vals["batch_number"], "pack_size": vals["pack_size"], "cost_price": cost_price,
            "retail_price": retail_price, "tax_rate": tax_rate, "discount_allowed": discount
        }

        try:
            self.controller.db_manager.add_or_update_stock(data)
            self.form_panel.clear_form()
            self.load_local_inventory()
            self.controller.db_manager.load_db_brands(self.controller.known_brands)
            messagebox.showinfo("Success", f"{name} updated in local stock.")
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def filter_inventory(self, event=None):
        if self.search_job:
            self.after_cancel(self.search_job)
        self.search_job = self.after(200, self.perform_filter_query)

    def perform_filter_query(self):
        query = self.grid_panel.get_search_query()
        self.grid_panel.clear_grid()
            
        if not query:
            self.load_local_inventory()
            return
            
        try:
            rows = self.controller.db_manager.search_inventory(query)
            for r in rows:
                cost_price = f"Rs {r[10]:.2f}" if r[10] is not None else "N/A"
                retail_price = f"Rs {r[11]:.2f}" if r[11] is not None else "N/A"
                tax_rate = f"{r[12]}%" if r[12] is not None else "N/A"
                discount = f"{r[13]}%" if r[13] is not None else "N/A"
                
                self.grid_panel.insert_row((
                    r[0], r[1], r[2], r[3], r[4], r[5],
                    r[6], r[7], r[8], r[9], cost_price,
                    retail_price, tax_rate, discount, r[14]
                ))
        except Exception as e:
            print(f"Error querying search filters: {e}")

    def clear_search(self):
        self.grid_panel.clear_search()

    def delete_selected_medicines(self):
        selected_items = self.grid_panel.get_selected_rows()
        if not selected_items:
            messagebox.showwarning("Nothing Selected", "Please select one or more medicines to delete.")
            return

        count = len(selected_items)
        confirm_msg = f"Are you sure you want to delete the selected {count} medicine(s)?\nThis will remove them from inventory."
        if not messagebox.askyesno("Confirm Deletion", confirm_msg):
            return

        for item in selected_items:
            item_values = self.grid_panel.get_row_values(item)
            name = item_values[0]
            
            self.controller.db_manager.delete_medicine(name)
            
            if self.controller.pharmacy_license:
                threading.Thread(
                    target=lambda m_name=name: self.controller.cloud_manager.delete_single_item(self.controller.pharmacy_license, m_name),
                    daemon=True
                ).start()

        self.load_local_inventory()
        messagebox.showinfo("Success", f"Successfully deleted {count} medicine(s) from inventory.")

    def sync_to_cloud(self):
        if not self.controller.pharmacy_license or not self.controller.lat or not self.controller.lng:
            messagebox.showwarning("Config Error", "Please save your Pharmacy License, Latitude, and Longitude first.")
            return

        try:
            self.sync_btn.config(text="Syncing...", state=tk.DISABLED)
            self.update()
            
            synced_count = self.controller.cloud_manager.sync_local_to_cloud(
                self.controller.db_name, self.controller.pharmacy_name, 
                self.controller.pharmacy_license, self.controller.lat, self.controller.lng
            )
            
            from core import settings
            settings.save_last_sync_time()
            messagebox.showinfo("Sync Success", f"Synced {synced_count} items and updated pharmacy location!")
        except Exception as e:
            messagebox.showerror("Sync Error", f"Failed to sync: {e}")
        finally:
            self.sync_btn.config(text="☁️ Sync to Cloud", state=tk.NORMAL)

    def add_to_cart(self, event=None):
        selected_items = self.grid_panel.get_selected_rows()
        if not selected_items and event is None:
            messagebox.showwarning("Select Medicine", "Please select one or more medicines from the list to add to cart.")
            return

        for sel in selected_items:
            item_values = self.grid_panel.get_row_values(sel)
            if not item_values:
                continue
            name = item_values[0]
            formula = item_values[1]
            manufacturer = item_values[2]
            category = item_values[3]
            form = item_values[4]
            dosage = item_values[5]
            barcode = item_values[6]
            batch = item_values[7]
            expiry = item_values[8]
            pack_size = item_values[9]
            
            cost_price_str = item_values[10].replace("Rs ", "")
            retail_price_str = item_values[11].replace("Rs ", "")
            tax_rate_str = item_values[12].replace("%", "")
            discount_rate_str = item_values[13].replace("%", "")
            current_qty = int(item_values[14])
            
            try:
                cost_price = float(cost_price_str) if cost_price_str != "N/A" else 0.0
            except ValueError:
                cost_price = 0.0
            try:
                retail_price = float(retail_price_str) if retail_price_str != "N/A" else 0.0
            except ValueError:
                retail_price = 0.0
            try:
                tax_rate = float(tax_rate_str) if tax_rate_str != "N/A" else 0.0
            except ValueError:
                tax_rate = 0.0
            try:
                discount_rate = float(discount_rate_str) if discount_rate_str != "N/A" else 0.0
            except ValueError:
                discount_rate = 0.0

            self.controller.cart[name] = {
                "name": name, "formula": formula, "manufacturer": manufacturer, "category": category,
                "form": form, "dosage": dosage, "barcode": barcode, "batch": batch, "expiry": expiry,
                "pack_size": pack_size, "retail_price": retail_price, "tax_rate": tax_rate,
                "discount_rate": discount_rate, "current_qty": current_qty, "cost_price": cost_price
            }
            
        self.update_cart_display()

    def remove_from_cart(self, event=None):
        selected_items = self.cart_panel.get_selected_rows()
        if not selected_items:
            return
            
        for sel in selected_items:
            item_values = self.cart_panel.get_row_values(sel)
            if not item_values:
                continue
            name = item_values[0]
            if name in self.controller.cart:
                del self.controller.cart[name]
                
        self.update_cart_display()

    def clear_cart(self):
        self.controller.cart.clear()
        self.update_cart_display()

    def update_cart_display(self):
        self.cart_panel.clear_grid()
            
        for name, item in self.controller.cart.items():
            self.cart_panel.insert_row((
                item["name"],
                item["current_qty"],
                f"Rs {item['retail_price']:.2f}"
            ))
            
        self.sell_btn.config(text=f"💳 Checkout Cart ({len(self.controller.cart)})")

    def sell_medicine(self):
        if not self.controller.cart:
            messagebox.showwarning("Cart Empty", "Your checkout cart is empty. Please select medicines from the list first.")
            return

        def on_checkout_success():
            self.load_local_inventory()
            self.update_cart_display()
            self.main_view.sales_tab.load_sales_analytics()

        CheckoutDialog(self.master, self.controller, self.controller.cart, on_checkout_success)
