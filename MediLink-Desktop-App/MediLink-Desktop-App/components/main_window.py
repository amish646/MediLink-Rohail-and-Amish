import tkinter as tk
from tkinter import ttk
from components.inventory_tab import InventoryTab
from components.ocr_tab import OcrTab
from components.sales_tab import SalesTab

class MainWindow(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f8fafc")
        self.controller = controller
        
        self.primary_color = "#0f172a"
        self.secondary_color = "#1e293b"
        self.accent_color = "#2563eb"
        self.success_color = "#10b981"
        self.warn_color = "#f59e0b"
        self.danger_color = "#ef4444"
        self.bg_color = "#f8fafc"
        self.card_color = "#ffffff"
        self.text_color = "#0f172a"
        self.text_light = "#64748b"

        self.setup_styles()
        self.setup_ui()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('default')
        style.configure("TNotebook", background=self.bg_color, borderwidth=0)
        style.configure("TNotebook.Tab", font=("Segoe UI", 9, "bold"), padding=[16, 8], background="#e2e8f0", foreground="#475569")
        style.map("TNotebook.Tab",
            background=[("selected", self.card_color)],
            foreground=[("selected", self.primary_color)]
        )

        style.configure("Treeview",
            font=("Segoe UI", 9),
            background=self.card_color,
            foreground=self.text_color,
            rowheight=25,
            fieldbackground=self.card_color,
            borderwidth=0
        )
        style.configure("Treeview.Heading",
            font=("Segoe UI", 9, "bold"),
            background="#e2e8f0",
            foreground=self.text_color,
            relief=tk.FLAT
        )
        style.map("Treeview",
            background=[("selected", self.accent_color)],
            foreground=[("selected", "#ffffff")]
        )

    def setup_ui(self):
        header_frame = tk.Frame(self, pady=12, bg=self.primary_color, bd=0)
        header_frame.pack(fill=tk.X)
        
        self.title_lbl = tk.Label(header_frame, text=f"🏥 {self.controller.pharmacy_name} - POS System", 
                                  font=("Segoe UI", 12, "bold"), bg=self.primary_color, fg="#ffffff")
        self.title_lbl.pack(side=tk.LEFT, padx=20)
        
        self.loc_lbl = tk.Label(header_frame, text=f"Location: Lat {self.controller.lat}, Lng {self.controller.lng}", 
                               font=("Segoe UI", 9), bg=self.primary_color, fg="#94a3b8")
        self.loc_lbl.pack(side=tk.RIGHT, padx=20)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.inventory_tab = InventoryTab(self.notebook, self.controller, self)
        self.ocr_tab = OcrTab(self.notebook, self.controller, self)
        self.sales_tab = SalesTab(self.notebook, self.controller, self)

        self.notebook.add(self.inventory_tab, text="  📦 Local Inventory Manager  ")
        self.notebook.add(self.ocr_tab, text="  📄 Invoice OCR Scanner  ")
        self.notebook.add(self.sales_tab, text="  📊 Sales & Revenue Analytics  ")
        
    def refresh_header(self):
        self.title_lbl.config(text=f"🏥 {self.controller.pharmacy_name} - POS System")
        self.loc_lbl.config(text=f"Location: Lat {self.controller.lat}, Lng {self.controller.lng}")
