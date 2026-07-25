import tkinter as tk
from tkinter import messagebox

class OcrEditDialog(tk.Toplevel):
    def __init__(self, parent, item_values, on_save_callback):
        super().__init__(parent)
        self.item_values = item_values
        self.on_save = on_save_callback
        
        self.title("Review & Edit Medicine Details")
        self.geometry("520x650")
        self.resizable(False, False)
        self.configure(bg="#fcfcfc")
        self.transient(parent)
        self.grab_set()

        self.setup_ui()

    def setup_ui(self):
        tk.Label(self, text="✏️ Edit Scanned Record", font=("Segoe UI", 12, "bold"), bg="#fcfcfc", fg="#0d47a1").pack(pady=10)
        
        form_frame = tk.Frame(self, bg="#fcfcfc", padx=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        form_frame.columnconfigure(1, weight=1)
        form_frame.columnconfigure(3, weight=1)
        
        def add_form_field(label_text, row, col_start, val):
            lbl = tk.Label(form_frame, text=label_text, font=("Segoe UI", 9, "bold"), bg="#fcfcfc")
            lbl.grid(row=row, column=col_start, sticky=tk.W, pady=6, padx=(5, 2))
            ent = tk.Entry(form_frame, font=("Segoe UI", 10), width=18, highlightthickness=1, 
                           highlightbackground="#cbd5e1", highlightcolor="#0d47a1", bd=0, relief=tk.FLAT)
            ent.grid(row=row, column=col_start+1, pady=6, padx=(2, 5), sticky=tk.EW)
            ent.insert(0, val)
            return ent
            
        self.name_ent = add_form_field("Medicine Name:", 0, 0, self.item_values[0])
        self.formula_ent = add_form_field("Generic Name:", 0, 2, self.item_values[1])
        self.mfg_ent = add_form_field("Manufacturer:", 1, 0, self.item_values[2])
        self.cat_ent = add_form_field("Category:", 1, 2, self.item_values[3])
        self.form_ent = add_form_field("Form (e.g. Tab):", 2, 0, self.item_values[4])
        self.dosage_ent = add_form_field("Dosage (500mg):", 2, 2, self.item_values[5])
        self.barcode_ent = add_form_field("Barcode:", 3, 0, self.item_values[6])
        self.batch_ent = add_form_field("Batch Number:", 3, 2, self.item_values[7])
        self.expiry_ent = add_form_field("Expiry (MM/YY):", 4, 0, self.item_values[8])
        self.pack_ent = add_form_field("Pack Size:", 4, 2, self.item_values[9])
        self.cost_ent = add_form_field("Cost Price:", 5, 0, self.item_values[10].replace("Rs ", ""))
        self.retail_ent = add_form_field("Retail Price:", 5, 2, self.item_values[11].replace("Rs ", ""))
        self.tax_ent = add_form_field("Tax Rate (%):", 6, 0, self.item_values[12].replace("%", ""))
        self.disc_ent = add_form_field("Discount (%):", 6, 2, self.item_values[13].replace("%", ""))
        self.qty_ent = add_form_field("Quantity:", 7, 0, self.item_values[14])
        
        tk.Button(self, text="✔️ Save Changes", bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), 
                  pady=6, command=self.submit_save).pack(pady=15)

    def submit_save(self):
        name = self.name_ent.get().strip()
        formula = self.formula_ent.get().strip()
        mfg = self.mfg_ent.get().strip()
        cat = self.cat_ent.get().strip()
        form_val = self.form_ent.get().strip()
        dosage = self.dosage_ent.get().strip()
        barcode = self.barcode_ent.get().strip()
        batch = self.batch_ent.get().strip()
        expiry = self.expiry_ent.get().strip()
        pack = self.pack_ent.get().strip()
        cost_str = self.cost_ent.get().strip()
        retail_str = self.retail_ent.get().strip()
        tax_str = self.tax_ent.get().strip()
        disc_str = self.disc_ent.get().strip()
        qty_str = self.qty_ent.get().strip()
        
        if not name:
            messagebox.showwarning("Input Error", "Medicine name cannot be empty.", parent=self)
            return
            
        try:
            cost = float(cost_str) if cost_str else 0.0
            retail = float(retail_str) if retail_str else 0.0
            tax = float(tax_str) if tax_str else 0.0
            disc = float(disc_str) if disc_str else 0.0
            qty = int(qty_str) if qty_str else 1
        except ValueError:
            messagebox.showwarning("Input Error", "Numerical fields must be valid numbers.", parent=self)
            return
            
        cost_val = f"Rs {cost:.2f}"
        retail_val = f"Rs {retail:.2f}"
        tax_val = f"{tax}%"
        disc_val = f"{disc}%"
        
        values = (
            name, formula, mfg, cat, form_val, dosage, barcode, batch, expiry, pack,
            cost_val, retail_val, tax_val, disc_val, qty
        )
        self.on_save(values)
        self.destroy()
