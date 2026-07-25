import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import os
import threading

class CheckoutDialog(tk.Toplevel):
    def __init__(self, parent, controller, cart, on_success_callback):
        super().__init__(parent)
        self.controller = controller
        self.cart = cart
        self.on_success = on_success_callback
        
        self.title("Checkout - MediLink Pharmacy")
        self.geometry("520x600")
        self.configure(bg="#f8fafc")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.row_widgets = []
        self.setup_ui()
        self.run_live_calc()

    def setup_ui(self):
        hdr = tk.Frame(self, bg=self.controller.main_window.primary_color, height=50)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)
        tk.Label(hdr, text="🛒 Multi-Medicine Checkout Portal", font=("Segoe UI", 11, "bold"), fg="white", 
                 bg=self.controller.main_window.primary_color).pack(pady=12)

        main_frame = tk.Frame(self, bg="#f8fafc", padx=20, pady=15)
        main_frame.pack(fill=tk.BOTH, expand=True)

        scroll_container = tk.Frame(main_frame, bg="#f8fafc")
        scroll_container.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        canvas = tk.Canvas(scroll_container, bg="#f8fafc", highlightthickness=0)
        v_scroll = ttk.Scrollbar(scroll_container, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#f8fafc")

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=v_scroll.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.bind('<Configure>', lambda event: canvas.itemconfig(canvas_window, width=event.width))

        for item in self.cart.values():
            item_card = tk.Frame(scrollable_frame, bg="#ffffff", bd=0, highlightthickness=1, highlightbackground="#e2e8f0", padx=10, pady=8)
            item_card.pack(fill=tk.X, pady=4, padx=5)

            info_sub = tk.Frame(item_card, bg="#ffffff")
            info_sub.pack(side=tk.LEFT, fill=tk.X, expand=True)

            tk.Label(info_sub, text=item["name"], font=("Segoe UI", 10, "bold"), bg="#ffffff", fg=self.controller.main_window.text_color, anchor=tk.W).pack(fill=tk.X)
            tk.Label(info_sub, text=f"Stock: {item['current_qty']} | Expiry: {item['expiry']}", font=("Segoe UI", 8), bg="#ffffff", fg=self.controller.main_window.text_light, anchor=tk.W).pack(fill=tk.X)

            inputs_sub = tk.Frame(item_card, bg="#ffffff")
            inputs_sub.pack(side=tk.RIGHT)

            tk.Label(inputs_sub, text="Qty:", font=("Segoe UI", 8, "bold"), bg="#ffffff", fg=self.controller.main_window.text_color).grid(row=0, column=0, padx=2, sticky=tk.E)
            qty_ent = tk.Entry(inputs_sub, font=("Segoe UI", 9), bg="#ffffff", fg=self.controller.main_window.text_color,
                               relief=tk.FLAT, bd=0, highlightthickness=1,
                               highlightbackground="#cbd5e1", highlightcolor=self.controller.main_window.accent_color,
                               insertbackground=self.controller.main_window.text_color, width=6)
            qty_ent.grid(row=0, column=1, padx=2, pady=2)
            qty_ent.insert(0, "1")

            tk.Label(inputs_sub, text="Price:", font=("Segoe UI", 8, "bold"), bg="#ffffff", fg=self.controller.main_window.text_color).grid(row=0, column=2, padx=2, sticky=tk.E)
            prc_ent = tk.Entry(inputs_sub, font=("Segoe UI", 9), bg="#ffffff", fg=self.controller.main_window.text_color,
                               relief=tk.FLAT, bd=0, highlightthickness=1,
                               highlightbackground="#cbd5e1", highlightcolor=self.controller.main_window.accent_color,
                               insertbackground=self.controller.main_window.text_color, width=8)
            prc_ent.grid(row=0, column=3, padx=2, pady=2)
            prc_ent.insert(0, f"{item['retail_price']:.2f}")

            del_btn = tk.Button(inputs_sub, text="🗑️", bg="#2563eb", fg="white", activebackground="#1d4ed8", font=("Segoe UI", 9), relief=tk.FLAT, bd=0, padx=6, pady=2, cursor="hand2")
            del_btn.grid(row=0, column=4, padx=(8, 2), pady=2)

            rw_dict = {"item": item, "qty_entry": qty_ent, "price_entry": prc_ent}
            self.row_widgets.append(rw_dict)
            del_btn.config(command=lambda name=item["name"], card=item_card: self.remove_item(name, card))

            qty_ent.bind("<KeyRelease>", self.run_live_calc)
            prc_ent.bind("<KeyRelease>", self.run_live_calc)

        self.summary_frame = tk.LabelFrame(main_frame, text=" Live Order Summary ", font=("Segoe UI", 9, "bold"), bg="#f1f5f9", fg=self.controller.main_window.primary_color, padx=15, pady=10, bd=1, relief=tk.SOLID)
        self.summary_frame.pack(fill=tk.X, pady=(0, 10))

        self.lbl_subtotal = self.create_summary_row(0, "Subtotal:")
        self.lbl_discount = self.create_summary_row(1, "Total Discount:")
        self.lbl_tax = self.create_summary_row(2, "Total Tax:")
        self.lbl_net = self.create_summary_row(3, "Net Total Payable:", is_bold=True)

        self.err_lbl = tk.Label(main_frame, text="", font=("Segoe UI", 9, "bold"), fg=self.controller.main_window.danger_color, bg="#f8fafc", wraplength=400)
        self.err_lbl.pack(fill=tk.X, pady=5)

        btn_box = tk.Frame(main_frame, bg="#f8fafc")
        btn_box.pack(fill=tk.X, side=tk.BOTTOM, pady=10)

        self.confirm_btn = tk.Button(btn_box, text="✔️ Confirm Sale", bg="#2563eb", fg="white", font=("Segoe UI", 10, "bold"), relief=tk.FLAT, bd=0, padx=15, pady=8, command=self.confirm_checkout)
        self.confirm_btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        self.confirm_btn.bind("<Enter>", lambda e: self.confirm_btn.config(bg="#059669") if self.confirm_btn['state'] == tk.NORMAL or self.confirm_btn['state'] == "normal" else None)
        self.confirm_btn.bind("<Leave>", lambda e: self.confirm_btn.config(bg="#10b981") if self.confirm_btn['state'] == tk.NORMAL or self.confirm_btn['state'] == "normal" else None)

        clear_btn = tk.Button(btn_box, text="🗑️ Clear Cart", bg="#2563eb", fg="white", font=("Segoe UI", 10, "bold"), relief=tk.FLAT, bd=0, padx=15, pady=8, command=self.clear_all_cart)
        clear_btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        cancel_btn = tk.Button(btn_box, text="❌ Cancel", bg="#2563eb", fg="white", font=("Segoe UI", 10, "bold"), relief=tk.FLAT, bd=0, padx=15, pady=8, command=self.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

    def create_summary_row(self, row_num, label_text, is_bold=False):
        color = self.controller.main_window.text_color if is_bold else self.controller.main_window.text_light
        font_spec = ("Segoe UI", 9, "bold") if is_bold else ("Segoe UI", 9)
        lbl = tk.Label(self.summary_frame, text=label_text, font=font_spec, bg="#f1f5f9", fg=color)
        lbl.grid(row=row_num, column=0, sticky=tk.W, pady=2)
        val = tk.Label(self.summary_frame, text="Rs 0.00", font=font_spec, bg="#f1f5f9", fg=self.controller.main_window.text_color)
        val.grid(row=row_num, column=1, sticky=tk.E, pady=2)
        self.summary_frame.grid_columnconfigure(1, weight=1)
        return val

    def remove_item(self, item_name, card_widget):
        if item_name in self.cart:
            del self.cart[item_name]
        card_widget.destroy()
        
        for rw in list(self.row_widgets):
            if rw["item"]["name"] == item_name:
                self.row_widgets.remove(rw)
                break
                
        self.run_live_calc()
        if not self.row_widgets:
            self.destroy()

    def clear_all_cart(self):
        self.cart.clear()
        self.on_success()
        self.destroy()

    def run_live_calc(self, event=None):
        total_subtotal = 0.0
        total_discount = 0.0
        total_tax = 0.0
        total_net = 0.0
        has_error = False
        error_msg = ""

        for rw in self.row_widgets:
            qty_text = rw["qty_entry"].get().strip()
            prc_text = rw["price_entry"].get().strip()
            item = rw["item"]

            if not qty_text or not prc_text:
                has_error = True
                continue

            try:
                sell_qty = int(qty_text)
                if sell_qty <= 0: raise ValueError
            except ValueError:
                has_error = True
                error_msg = f"⚠️ Qty for {item['name']} must be a positive integer."
                break

            if sell_qty > item["current_qty"]:
                has_error = True
                error_msg = f"⚠️ Qty for {item['name']} exceeds stock ({item['current_qty']})."
                break

            try:
                sell_price = float(prc_text)
                if sell_price <= 0: raise ValueError
            except ValueError:
                has_error = True
                error_msg = f"⚠️ Price for {item['name']} must be a positive number."
                break

            sub = sell_qty * sell_price
            disc = sub * (item["discount_rate"] / 100.0)
            taxable = sub - disc
            tax = taxable * (item["tax_rate"] / 100.0)
            net = taxable + tax

            total_subtotal += sub
            total_discount += disc
            total_tax += tax
            total_net += net

        if has_error:
            self.confirm_btn.config(state=tk.DISABLED, bg="#94a3b8")
            self.err_lbl.config(text=error_msg)
            self.lbl_subtotal.config(text="Rs 0.00")
            self.lbl_discount.config(text="Rs 0.00")
            self.lbl_tax.config(text="Rs 0.00")
            self.lbl_net.config(text="Rs 0.00")
        else:
            self.confirm_btn.config(state=tk.NORMAL, bg="#2563eb")
            self.err_lbl.config(text="")
            self.lbl_subtotal.config(text=f"Rs {total_subtotal:.2f}")
            self.lbl_discount.config(text=f"-Rs {total_discount:.2f}")
            self.lbl_tax.config(text=f"+Rs {total_tax:.2f}")
            self.lbl_net.config(text=f"Rs {total_net:.2f}")

    def confirm_checkout(self):
        sales_data = []
        for rw in self.row_widgets:
            qty_text = rw["qty_entry"].get().strip()
            prc_text = rw["price_entry"].get().strip()
            item = rw["item"]

            try:
                sell_qty = int(qty_text)
                sell_price = float(prc_text)
                if sell_qty <= 0 or sell_price <= 0 or sell_qty > item["current_qty"]:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Checkout Error", f"Invalid input for {item['name']}.", parent=self)
                return

            sales_data.append({"item": item, "sell_qty": sell_qty, "sell_price": sell_price})

        invoice_no = f"INV-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        sale_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            self.controller.db_manager.record_sale(invoice_no, sale_date, sales_data)
        except Exception as e:
            messagebox.showerror("Database Transaction Error", f"Checkout failed: {e}", parent=self)
            return

        if self.controller.pharmacy_license:
            def run_cloud_updates():
                for sale in sales_data:
                    item = sale["item"]
                    new_qty = item["current_qty"] - sale["sell_qty"]
                    self.controller.cloud_manager.update_single_item_stock(
                        self.controller.pharmacy_license, item["name"], new_qty, sale["sell_price"]
                    )
            threading.Thread(target=run_cloud_updates, daemon=True).start()

        total_subtotal = 0.0
        total_discount = 0.0
        total_tax = 0.0
        total_net = 0.0

        invoice_text = f"=========================================\n"
        invoice_text += f"        {self.controller.pharmacy_name.upper()}\n"
        if self.controller.lat and self.controller.lng:
            invoice_text += f"  Location: Lat {self.controller.lat}, Lng {self.controller.lng}\n"
        invoice_text += f"  License: {self.controller.pharmacy_license}\n"
        invoice_text += f"=========================================\n"
        invoice_text += f" Date: {sale_date}\n"
        invoice_text += f" Invoice No: {invoice_no}\n"
        invoice_text += f"-----------------------------------------\n"

        for sale in sales_data:
            item = sale["item"]
            qty = sale["sell_qty"]
            price = sale["sell_price"]
            sub = qty * price
            disc = sub * (item["discount_rate"] / 100.0)
            taxable = sub - disc
            tax = taxable * (item["tax_rate"] / 100.0)
            net = taxable + tax

            total_subtotal += sub
            total_discount += disc
            total_tax += tax
            total_net += net

            invoice_text += f" {item['name']}\n"
            if item['formula'] != "N/A":
                invoice_text += f"  Formula: {item['formula']}\n"
            if item['batch'] != "N/A":
                invoice_text += f"  Batch No: {item['batch']} | Expiry: {item['expiry']}\n"
            invoice_text += f"  {qty} x Rs {price:.2f} = Rs {sub:.2f}\n"
            if disc > 0:
                invoice_text += f"  Discount ({item['discount_rate']}%): -Rs {disc:.2f}\n"
            if tax > 0:
                invoice_text += f"  Tax ({item['tax_rate']}%):       +Rs {tax:.2f}\n"
            invoice_text += f"  Net Total: Rs {net:.2f}\n"
            invoice_text += f"-----------------------------------------\n"

        invoice_text += f" Gross Subtotal: Rs {total_subtotal:>10.2f}\n"
        if total_discount > 0:
            invoice_text += f" Total Discount: -Rs {total_discount:>9.2f}\n"
        if total_tax > 0:
            invoice_text += f" Total Tax:      +Rs {total_tax:>9.2f}\n"
        invoice_text += f"-----------------------------------------\n"
        invoice_text += f" NET TOTAL:      Rs {total_net:>10.2f}\n"
        invoice_text += f"=========================================\n"
        invoice_text += f"       Thank you for your visit!\n"
        invoice_text += f"=========================================\n"

        if len(sales_data) == 1:
            receipt_filename = f"Receipt_{sales_data[0]['item']['name']}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.txt"
        else:
            receipt_filename = f"Receipt_Multiple_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.txt"

        with open(receipt_filename, 'w') as f:
            f.write(invoice_text)

        self.cart.clear()
        self.on_success()
        self.destroy()

        self.show_receipt_popup(invoice_text, receipt_filename)

    def show_receipt_popup(self, invoice_text, receipt_filename):
        receipt_win = tk.Toplevel(self.master)
        receipt_win.title("Sale Invoice / Receipt")
        receipt_win.geometry("420x580")
        receipt_win.configure(bg="#f1f5f9")
        receipt_win.resizable(False, False)
        receipt_win.transient(self.master)
        receipt_win.grab_set()

        tk.Label(receipt_win, text="Invoice Generated Successfully", font=("Segoe UI", 11, "bold"), fg="#1e293b", bg="#f1f5f9", pady=10).pack()

        text_frame = tk.Frame(receipt_win, bg="#ffffff", bd=1, relief=tk.SOLID)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        text_widget = tk.Text(text_frame, font=("Courier New", 10), bg="#ffffff", fg="#0f172a", bd=0, padx=12, pady=12)
        text_widget.insert(tk.END, invoice_text)
        text_widget.config(state=tk.DISABLED)
        text_widget.pack(fill=tk.BOTH, expand=True)

        tk.Label(receipt_win, text=f"Invoice saved locally as:\n{receipt_filename}", font=("Segoe UI", 8), fg="#64748b", bg="#f1f5f9").pack(pady=5)

        btn_box = tk.Frame(receipt_win, bg="#f1f5f9")
        btn_box.pack(pady=10)

        def print_invoice():
            try:
                os.startfile(receipt_filename, "print")
            except Exception as e:
                messagebox.showerror("Printing Error", f"Failed to send to printer: {e}", parent=receipt_win)

        print_btn = tk.Button(btn_box, text="🖨️ Print Invoice", bg="#2563eb", fg="white", font=("Segoe UI", 9, "bold"), relief=tk.FLAT, bd=0, padx=20, pady=6, command=print_invoice)
        print_btn.pack(side=tk.LEFT, padx=10)
        
        close_btn = tk.Button(btn_box, text="❌ Dismiss", bg="#2563eb", fg="white", font=("Segoe UI", 9, "bold"), relief=tk.FLAT, bd=0, padx=20, pady=6, command=receipt_win.destroy)
        close_btn.pack(side=tk.LEFT, padx=10)
