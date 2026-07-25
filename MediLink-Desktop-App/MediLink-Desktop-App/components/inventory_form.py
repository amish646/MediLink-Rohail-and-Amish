import tkinter as tk

class InventoryForm(tk.Frame):
    def __init__(self, parent, controller, main_view):
        super().__init__(parent, bg=main_view.bg_color)
        self.controller = controller
        self.main_view = main_view
        self.setup_ui()

    def setup_ui(self):
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

        def create_card(parent, title):
            card = tk.Frame(parent, bg=self.main_view.card_color, highlightthickness=1, highlightbackground="#e2e8f0", bd=0, padx=15, pady=12)
            title_lbl = tk.Label(card, text=title, font=("Segoe UI", 10, "bold"), bg=self.main_view.card_color, fg=self.main_view.primary_color)
            title_lbl.pack(anchor=tk.W, pady=(0, 10))
            content = tk.Frame(card, bg=self.main_view.card_color)
            content.pack(fill=tk.BOTH, expand=True)
            return card, content

        card1, content1 = create_card(self, "📋 Core Identification")
        card1.grid(row=0, column=0, padx=(0, 8), sticky="nsew")

        card2, content2 = create_card(self, "🔬 Presentation & Specs")
        card2.grid(row=0, column=1, padx=4, sticky="nsew")

        card3, content3 = create_card(self, "💰 Financial & Stock")
        card3.grid(row=0, column=2, padx=(8, 0), sticky="nsew")

        def build_entry(parent, row, label_text):
            tk.Label(parent, text=label_text, font=("Segoe UI", 9), bg=self.main_view.card_color, fg=self.main_view.text_color).grid(row=row, column=0, sticky=tk.W, pady=5, padx=(0, 10))
            entry = tk.Entry(parent, font=("Segoe UI", 10), bg="#ffffff", fg=self.main_view.text_color,
                             relief=tk.FLAT, bd=0, highlightthickness=1,
                             highlightbackground="#cbd5e1", highlightcolor=self.main_view.accent_color,
                             insertbackground=self.main_view.text_color, width=22)
            entry.grid(row=row, column=1, sticky=tk.EW, pady=5)
            parent.columnconfigure(1, weight=1)
            return entry

        self.name_entry = build_entry(content1, 0, "Medicine Name:")
        self.formula_entry = build_entry(content1, 1, "Generic Name:")
        self.category_entry = build_entry(content1, 2, "Category:")
        self.barcode_entry = build_entry(content1, 3, "Barcode:")
        self.manufacturer_entry = build_entry(content1, 4, "Manufacturer:")

        self.form_entry = build_entry(content2, 0, "Form (e.g. Tab/Syp):")
        self.dosage_entry = build_entry(content2, 1, "Dosage (e.g. 500mg):")
        self.pack_size_entry = build_entry(content2, 2, "Pack Size:")
        self.expiry_entry = build_entry(content2, 3, "Expiry (MM/YY):")

        self.qty_entry = build_entry(content3, 0, "Quantity:")
        self.batch_entry = build_entry(content3, 1, "Batch Number:")
        self.cost_price_entry = build_entry(content3, 2, "Cost Price (Rs):")
        self.retail_price_entry = build_entry(content3, 3, "Retail Price (Rs):")
        self.tax_rate_entry = build_entry(content3, 4, "Tax Rate (%):")
        self.discount_entry = build_entry(content3, 5, "Discount Allowed (%):")

    def get_form_values(self):
        return {
            "brand_name": self.name_entry.get().strip().title(),
            "generic_formula": self.formula_entry.get().strip().title() or "N/A",
            "manufacturer": self.manufacturer_entry.get().strip().title() or "Unknown",
            "category": self.category_entry.get().strip().title() or "General",
            "form": self.form_entry.get().strip().title() or "Tablet",
            "dosage": self.dosage_entry.get().strip() or "N/A",
            "barcode": self.barcode_entry.get().strip() or "N/A",
            "batch_number": self.batch_entry.get().strip() or "N/A",
            "expiry_date": self.expiry_entry.get().strip() or "12/27",
            "pack_size": self.pack_size_entry.get().strip() or "10s",
            "quantity_str": self.qty_entry.get().strip(),
            "retail_price_str": self.retail_price_entry.get().strip(),
            "cost_price_str": self.cost_price_entry.get().strip(),
            "tax_rate_str": self.tax_rate_entry.get().strip(),
            "discount_str": self.discount_entry.get().strip(),
        }

    def clear_form(self):
        for entry in [
            self.name_entry, self.formula_entry, self.manufacturer_entry,
            self.category_entry, self.form_entry, self.dosage_entry,
            self.barcode_entry, self.batch_entry, self.expiry_entry,
            self.pack_size_entry, self.cost_price_entry, self.retail_price_entry,
            self.tax_rate_entry, self.discount_entry, self.qty_entry
        ]:
            entry.delete(0, tk.END)
