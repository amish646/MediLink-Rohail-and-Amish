import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import sqlite3
from pymongo import MongoClient
import datetime
import json
import os
import re
import threading
from PIL import Image, ImageTk
import winocr
import cv2

import pytesseract

# Auto-detect Tesseract installation path
_TESS_PATHS = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    r"C:\Users\pc\AppData\Local\Programs\Tesseract-OCR\tesseract.exe",
]
for _p in _TESS_PATHS:
    if os.path.exists(_p):
        pytesseract.pytesseract.tesseract_cmd = _p
        break

# --- Config ---
MONGO_URI = "mongodb+srv://amish:AmishPassword123@cluster0.ivayay0.mongodb.net/MediLinkDB?retryWrites=true&w=majority"
CONFIG_FILE = "pharmacy_config.json"

class PharmacyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MediLink - Pharmacy Desktop App (Pro)")
        self.root.geometry("1000x780")
        
        # Set window icon
        try:
            icon_path = os.path.join(os.path.dirname(__file__), "app_icon.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
            else:
                fallback_path = "app_icon.ico"
                if os.path.exists(fallback_path):
                    self.root.iconbitmap(fallback_path)
        except Exception as e:
            print(f"Error loading icon: {e}")
        
        self.pharmacy_name, self.pharmacy_license, self.lat, self.lng, self.gemini_key = self.load_config()
        self.invoice_photo = None
        self.cart = {}
        self.search_job = None
        
        # Expanded catalog of 28 common medicine brands for fuzzy matching
        self.known_brands = {
            "panadol": ("Panadol", "Paracetamol"),
            "augmentin": ("Augmentin", "Co-Amoxiclav"),
            "ponstan": ("Ponstan", "Mefenamic Acid"),
            "arinac": ("Arinac", "Ibuprofen/Pseudoephedrine"),
            "flagyl": ("Flagyl", "Metronidazole"),
            "brufen": ("Brufen", "Ibuprofen"),
            "calpol": ("Calpol", "Paracetamol"),
            "disprin": ("Disprin", "Aspirin"),
            "surbex": ("Surbex-Z", "Multivitamins"),
            "amoxil": ("Amoxil", "Amoxicillin"),
            "zyrtec": ("Zyrtec", "Cetirizine"),
            "loprin": ("Loprin", "Aspirin"),
            "nims": ("Nims", "Nimesulide"),
            "entamizole": ("Entamizole", "Diloxanide Furoate + Metronidazole"),
            "solvin": ("Solvin", "Paracetamol/Pseudoephedrine"),
            "risek": ("Risek", "Omeprazole"),
            "avil": ("Avil", "Pheniramine"),
            "sancos": ("Sancos", "Cough Syrup"),
            "fefol": ("Fefol", "Iron + Folic Acid"),
            "hydryllin": ("Hydryllin", "Aminophylline"),
            "ventolin": ("Ventolin", "Salbutamol"),
            "concor": ("Concor", "Bisoprolol"),
            "lipiget": ("Lipiget", "Atorvastatin"),
            "glucophage": ("Glucophage", "Metformin"),
            "novidat": ("Novidat", "Ciprofloxacin"),
            "klacid": ("Klacid", "Clarithromycin"),
            "gaviscon": ("Gaviscon", "Sodium Alginate"),
            "serc": ("Serc", "Betahistine")
        }
        
        # Setup and show Sign In screen first
        self.show_signin_screen()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    data = json.load(f)
                    return (data.get('name', 'MediLink Pharmacy'),
                            data.get('license', ''), 
                            data.get('lat', ''), 
                            data.get('lng', ''), 
                            data.get('gemini_key', ''))
            except:
                pass
        return "MediLink Pharmacy", "", "", "", ""

    def show_signin_screen(self):
        # Configure root for Sign In
        self.root.geometry("480x640")
        self.root.configure(bg="#f8fafc")
        self.root.resizable(False, False)
        self.root.title("MediLink - POS Portal Login")
        
        # Sign In main container
        self.signin_container = tk.Frame(self.root, bg="#f8fafc")
        self.signin_container.pack(fill=tk.BOTH, expand=True, padx=40, pady=30)
        
        # Logo/Brand header
        brand_lbl = tk.Label(self.signin_container, text="🏥 MediLink POS", font=("Segoe UI", 24, "bold"), fg="#2563eb", bg="#f8fafc")
        brand_lbl.pack(pady=(15, 5))
        
        sub_lbl = tk.Label(self.signin_container, text="Pharmacy Management System", font=("Segoe UI", 10, "bold"), fg="#64748b", bg="#f8fafc")
        sub_lbl.pack(pady=(0, 20))
        
        # A card-like frame for input fields
        card = tk.Frame(self.signin_container, bg="#ffffff", bd=0, highlightthickness=1, highlightbackground="#e2e8f0", padx=25, pady=25)
        card.pack(fill=tk.BOTH, expand=True)
        
        # Input fields helper
        def make_input_field(parent, label_text, var_name, is_password=False):
            lbl = tk.Label(parent, text=label_text, font=("Segoe UI", 9, "bold"), bg="#ffffff", fg="#0f172a")
            lbl.pack(anchor=tk.W, pady=(8, 2))
            
            ent = tk.Entry(parent, font=("Segoe UI", 10), bg="#f8fafc", fg="#0f172a",
                           insertbackground="#0f172a", relief=tk.FLAT, bd=0, highlightthickness=1,
                           highlightbackground="#cbd5e1", highlightcolor="#2563eb", width=30)
            if is_password:
                ent.config(show="*")
            ent.pack(fill=tk.X, ipady=4)
            setattr(self, var_name, ent)
            return ent

        # Create input fields
        self.name_config_entry = make_input_field(card, "🏥 Pharmacy Name", "name_config_entry")
        self.license_entry = make_input_field(card, "🔑 License Key", "license_entry", is_password=True)
        self.lat_entry = make_input_field(card, "📍 Latitude (e.g. 33.6844)", "lat_entry")
        self.lng_entry = make_input_field(card, "📍 Longitude (e.g. 73.0479)", "lng_entry")
        
        # Pre-fill entries from loaded config if they exist
        if self.pharmacy_name:
            self.name_config_entry.insert(0, self.pharmacy_name)
        if self.pharmacy_license:
            self.license_entry.insert(0, self.pharmacy_license)
        if self.lat:
            self.lat_entry.insert(0, self.lat)
        if self.lng:
            self.lng_entry.insert(0, self.lng)

        # Login action button
        login_btn = tk.Button(card, text="🚀 Access POS System", bg="#2563eb", fg="white", font=("Segoe UI", 11, "bold"), relief=tk.FLAT, bd=0, pady=10, cursor="hand2", command=self.handle_signin)
        login_btn.pack(fill=tk.X, pady=(25, 5))
        
        def on_enter(e):
            login_btn.config(bg="#1d4ed8")
        def on_leave(e):
            login_btn.config(bg="#2563eb")
        login_btn.bind("<Enter>", on_enter)
        login_btn.bind("<Leave>", on_leave)

        # Warning/Error message label
        self.signin_error_lbl = tk.Label(card, text="", font=("Segoe UI", 9, "bold"), fg="#ef4444", bg="#ffffff", wraplength=350)
        self.signin_error_lbl.pack(fill=tk.X, pady=(10, 0))

    def handle_signin(self):
        name = self.name_config_entry.get().strip()
        lic = self.license_entry.get().strip()
        lat = self.lat_entry.get().strip()
        lng = self.lng_entry.get().strip()
        
        # Preserve Gemini API Key from loaded config if not otherwise enetered
        gemini_key = getattr(self, "gemini_key", "") or ""
        
        if not name or not lic or not lat or not lng:
            self.signin_error_lbl.config(text="⚠️ Please fill in all four fields.")
            return

        try:
            float(lat)
            float(lng)
        except ValueError:
            self.signin_error_lbl.config(text="⚠️ Latitude and Longitude must be valid numbers.")
            return

        # Success - Save configuration
        self.pharmacy_name = name
        self.pharmacy_license = lic
        self.lat = lat
        self.lng = lng
        self.save_config(name, lic, lat, lng, gemini_key)
        
        # Initialize databases and load POS components
        try:
            self.setup_local_db()
            self.pull_inventory_from_cloud()
            self.load_db_brands()
            
            # Destroy sign in frame
            self.signin_container.destroy()
            
            # Reconfigure window settings for POS
            self.root.geometry("1000x780")
            self.root.resizable(True, True)
            self.root.title("MediLink - Pharmacy Desktop App (Pro)")
            
            # Create POS widgets and load inventory
            self.create_widgets()
            self.load_local_inventory()
            
        except Exception as e:
            self.signin_error_lbl.config(text=f"⚠️ Initialization Error: {e}")

    def save_config(self, name, license_no, lat, lng, gemini_key):
        with open(CONFIG_FILE, 'w') as f:
            json.dump({
                'name': name,
                'license': license_no, 
                'lat': lat, 
                'lng': lng, 
                'gemini_key': gemini_key
            }, f)
        self.pharmacy_name = name
        self.pharmacy_license = license_no
        self.lat = lat
        self.lng = lng
        self.gemini_key = gemini_key

    def setup_local_db(self):
        # Hash the license to act as a secure password/security code so database filename on disk is obscured
        import hashlib
        if self.pharmacy_license:
            db_hash = hashlib.sha256(self.pharmacy_license.strip().encode('utf-8')).hexdigest()[:16]
            db_name = f"pharmacy_{db_hash}.db"
        else:
            db_name = "pharmacy_default.db"

        # Close existing connection if already open to prevent leaks
        if hasattr(self, 'conn') and self.conn:
            try:
                self.conn.close()
            except Exception as e:
                print(f"Error closing old connection: {e}")

        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS LocalInventoryV2 (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                brand_name TEXT UNIQUE,
                generic_formula TEXT,
                price REAL,
                expiry_date TEXT,
                quantity INTEGER
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS SalesHistory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_no TEXT,
                sale_date TEXT,
                medicine_name TEXT,
                generic_formula TEXT,
                quantity INTEGER,
                sell_price REAL,
                cost_price REAL,
                discount REAL,
                tax REAL,
                net_total REAL,
                profit REAL
            )
        """)
        self.conn.commit()

        # Schema Migration: Add missing columns dynamically
        fields = [
            ("manufacturer", "TEXT"),
            ("category", "TEXT"),
            ("form", "TEXT"),
            ("dosage", "TEXT"),
            ("barcode", "TEXT"),
            ("batch_number", "TEXT"),
            ("pack_size", "TEXT"),
            ("cost_price", "REAL"),
            ("retail_price", "REAL"),
            ("tax_rate", "REAL"),
            ("discount_allowed", "REAL")
        ]
        self.cursor.execute("PRAGMA table_info(LocalInventoryV2)")
        existing_cols = [row[1] for row in self.cursor.fetchall()]
        for col_name, col_type in fields:
            if col_name not in existing_cols:
                try:
                    self.cursor.execute(f"ALTER TABLE LocalInventoryV2 ADD COLUMN {col_name} {col_type}")
                except Exception as e:
                    print(f"Migration error for {col_name}: {e}")
        self.conn.commit()

    def load_db_brands(self):
        try:
            self.cursor.execute("SELECT DISTINCT brand_name, generic_formula FROM LocalInventoryV2")
            rows = self.cursor.fetchall()
            for brand, formula in rows:
                if brand:
                    brand_low = brand.lower().strip()
                    self.known_brands[brand_low] = (brand.strip(), (formula or "Generic Formula").strip())
        except Exception as e:
            print(f"Error loading DB brands for fuzzy matching: {e}")

    def create_widgets(self):
        # Modern Color Palette
        self.primary_color = "#0f172a"  # Slate Navy (Header)
        self.secondary_color = "#1e293b"  # Medium Slate
        self.accent_color = "#2563eb"   # Corporate Blue
        self.success_color = "#10b981"  # Emerald Green
        self.warn_color = "#f59e0b"     # Amber
        self.danger_color = "#ef4444"    # Red
        self.bg_color = "#f8fafc"       # Soft Light Gray
        self.card_color = "#ffffff"     # White Card
        self.text_color = "#0f172a"     # Dark slate text
        self.text_light = "#64748b"     # Muted gray text

        # Style sheet configuration
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

        # Apply root background
        self.root.configure(bg=self.bg_color)

        # Helper function for hover effects
        def bind_hover(btn, normal_bg, hover_bg):
            btn.bind("<Enter>", lambda e: btn.config(bg=hover_bg))
            btn.bind("<Leave>", lambda e: btn.config(bg=normal_bg))

        # --- POS Header Bar (Top / Clean Title Bar) ---
        header_frame = tk.Frame(self.root, pady=12, bg=self.primary_color, bd=0)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        
        tk.Label(header_frame, text=f"🏥 {self.pharmacy_name} - POS System", font=("Segoe UI", 12, "bold"), bg=self.primary_color, fg="#ffffff").pack(side=tk.LEFT, padx=20)
        
        tk.Label(header_frame, text=f"Location: Lat {self.lat}, Lng {self.lng}", font=("Segoe UI", 9), bg=self.primary_color, fg="#94a3b8").pack(side=tk.RIGHT, padx=20)

        # --- Notebook (Tabs) ---
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.tab1 = tk.Frame(self.notebook, bg=self.bg_color)
        self.tab2 = tk.Frame(self.notebook, bg=self.bg_color)
        self.tab3 = tk.Frame(self.notebook, bg=self.bg_color)
        
        self.notebook.add(self.tab1, text="  📦 Local Inventory Manager  ")
        self.notebook.add(self.tab2, text="  📄 Invoice OCR Scanner  ")
        self.notebook.add(self.tab3, text="  📊 Sales & Revenue Analytics  ")

        # ==========================================
        # TAB 1: LOCAL INVENTORY MANAGER (Existing)
        # ==========================================
        # --- Input Frame ---
        # Main input container
        input_container = tk.Frame(self.tab1, bg=self.bg_color)
        input_container.pack(fill=tk.X, padx=15, pady=10)

        # Sub-card creation helper
        def create_card(parent, title):
            card = tk.Frame(parent, bg=self.card_color, highlightthickness=1, highlightbackground="#e2e8f0", bd=0, padx=15, pady=12)
            title_lbl = tk.Label(card, text=title, font=("Segoe UI", 10, "bold"), bg=self.card_color, fg=self.primary_color)
            title_lbl.pack(anchor=tk.W, pady=(0, 10))
            content = tk.Frame(card, bg=self.card_color)
            content.pack(fill=tk.BOTH, expand=True)
            return card, content

        # Grid layout for three cards
        input_container.columnconfigure(0, weight=1)
        input_container.columnconfigure(1, weight=1)
        input_container.columnconfigure(2, weight=1)

        card1, content1 = create_card(input_container, "📋 Core Identification")
        card1.grid(row=0, column=0, padx=(0, 8), sticky="nsew")

        card2, content2 = create_card(input_container, "🔬 Presentation & Specs")
        card2.grid(row=0, column=1, padx=4, sticky="nsew")

        card3, content3 = create_card(input_container, "💰 Financial & Stock")
        card3.grid(row=0, column=2, padx=(8, 0), sticky="nsew")

        # Sub-grid labels and entries
        def style_entry(parent, row, label_text, entry_var_name, default_val=""):
            tk.Label(parent, text=label_text, font=("Segoe UI", 9), bg=self.card_color, fg=self.text_color).grid(row=row, column=0, sticky=tk.W, pady=5, padx=(0, 10))
            entry = tk.Entry(parent, font=("Segoe UI", 10), bg="#ffffff", fg=self.text_color,
                             relief=tk.FLAT, bd=0, highlightthickness=1,
                             highlightbackground="#cbd5e1", highlightcolor=self.accent_color,
                             insertbackground=self.text_color, width=22)
            entry.grid(row=row, column=1, sticky=tk.EW, pady=5)
            parent.columnconfigure(1, weight=1)
            if default_val:
                entry.insert(0, default_val)
            setattr(self, entry_var_name, entry)

        # Card 1 Inputs
        style_entry(content1, 0, "Medicine Name:", "name_entry")
        style_entry(content1, 1, "Generic Name:", "formula_entry")
        style_entry(content1, 2, "Category:", "category_entry")
        style_entry(content1, 3, "Barcode:", "barcode_entry")
        style_entry(content1, 4, "Manufacturer:", "manufacturer_entry")

        # Card 2 Inputs
        style_entry(content2, 0, "Form (e.g. Tab/Syp):", "form_entry")
        style_entry(content2, 1, "Dosage (e.g. 500mg):", "dosage_entry")
        style_entry(content2, 2, "Pack Size:", "pack_size_entry")
        style_entry(content2, 3, "Expiry (MM/YY):", "expiry_entry")

        # Card 3 Inputs
        style_entry(content3, 0, "Quantity:", "qty_entry")
        style_entry(content3, 1, "Batch Number:", "batch_entry")
        style_entry(content3, 2, "Cost Price (Rs):", "cost_price_entry")
        style_entry(content3, 3, "Retail Price (Rs):", "retail_price_entry")
        style_entry(content3, 4, "Tax Rate (%):", "tax_rate_entry")
        style_entry(content3, 5, "Discount Allowed (%):", "discount_entry")

        # Buttons Frame
        btn_frame = tk.Frame(self.tab1, bg=self.bg_color)
        btn_frame.pack(fill=tk.X, padx=15, pady=5)

        self.add_btn = tk.Button(btn_frame, text="➕ Add/Update Stock", bg="#2563eb", fg="white", font=("Segoe UI", 9, "bold"), padx=10, pady=8, relief=tk.FLAT, bd=0, command=self.add_local_stock)
        self.add_btn.pack(side=tk.LEFT, padx=6, expand=True, fill=tk.X)
        bind_hover(self.add_btn, "#2563eb", "#1d4ed8")

        self.add_to_cart_btn = tk.Button(btn_frame, text="🛒 Add Selected to Cart", bg="#2563eb", fg="white", font=("Segoe UI", 9, "bold"), padx=10, pady=8, relief=tk.FLAT, bd=0, command=self.add_to_cart)
        self.add_to_cart_btn.pack(side=tk.LEFT, padx=6, expand=True, fill=tk.X)
        bind_hover(self.add_to_cart_btn, "#2563eb", "#1d4ed8")

        self.sell_btn = tk.Button(btn_frame, text="💳 Checkout Cart (0)", bg="#2563eb", fg="white", font=("Segoe UI", 9, "bold"), padx=10, pady=8, relief=tk.FLAT, bd=0, command=self.sell_medicine)
        self.sell_btn.pack(side=tk.LEFT, padx=6, expand=True, fill=tk.X)
        bind_hover(self.sell_btn, "#2563eb", "#1d4ed8")

        self.delete_btn = tk.Button(btn_frame, text="🗑️ Delete Selected", bg="#2563eb", fg="white", font=("Segoe UI", 9, "bold"), padx=10, pady=8, relief=tk.FLAT, bd=0, command=self.delete_selected_medicines)
        self.delete_btn.pack(side=tk.LEFT, padx=6, expand=True, fill=tk.X)
        bind_hover(self.delete_btn, "#2563eb", "#1d4ed8")

        self.sync_btn = tk.Button(btn_frame, text="☁️ Sync to Cloud", bg="#2563eb", fg="white", font=("Segoe UI", 9, "bold"), padx=10, pady=8, relief=tk.FLAT, bd=0, command=self.sync_to_cloud)
        self.sync_btn.pack(side=tk.LEFT, padx=6, expand=True, fill=tk.X)
        bind_hover(self.sync_btn, "#2563eb", "#1d4ed8")

        # --- Search Frame ---
        search_frame = tk.Frame(self.tab1, bg=self.bg_color, pady=5)
        search_frame.pack(fill=tk.X, padx=15, pady=5)

        tk.Label(search_frame, text="🔍 Search Inventory (Name/Formula):", font=("Segoe UI", 9, "bold"), bg=self.bg_color, fg=self.text_color).pack(side=tk.LEFT, padx=5)
        self.search_entry = tk.Entry(search_frame, font=("Segoe UI", 10), bg="#ffffff", fg=self.text_color,
                                     relief=tk.FLAT, bd=0, highlightthickness=1,
                                     highlightbackground="#cbd5e1", highlightcolor=self.accent_color,
                                     insertbackground=self.text_color, width=35)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind("<KeyRelease>", self.filter_inventory)

        self.clear_btn = tk.Button(search_frame, text="Clear Search", font=("Segoe UI", 8, "bold"), bg=self.text_light, fg="white", relief=tk.FLAT, bd=0, padx=8, command=self.clear_search)
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        bind_hover(self.clear_btn, self.text_light, "#475569")

        # Treeview Table Frame (Holds main inventory list and checkout cart)
        table_frame = tk.Frame(self.tab1, bg=self.bg_color)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        # Left Container: Main Inventory List
        inventory_frame = tk.Frame(table_frame, bg=self.bg_color)
        inventory_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        columns = (
            "Medicine Name", "Generic Name", "Manufacturer", "Category", "Form", "Dosage",
            "Barcode", "Batch Number", "Expiry Date", "Pack Size", "Cost Price", "Retail Price",
            "Tax Rate", "Discount Allowed", "Quantity"
        )
        self.tree = ttk.Treeview(inventory_frame, columns=columns, show="headings", height=12, selectmode="extended")
        self.tree.bind("<Delete>", lambda e: self.delete_selected_medicines())
        self.tree.bind("<BackSpace>", lambda e: self.delete_selected_medicines())
        self.tree.bind("<Double-1>", self.add_to_cart)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100 if col not in ("Medicine Name", "Generic Name", "Manufacturer") else 140)

        # Scrollbars for local inventory
        scrollbar = ttk.Scrollbar(inventory_frame, orient=tk.VERTICAL, command=self.tree.yview)
        hscrollbar = ttk.Scrollbar(inventory_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=scrollbar.set, xscrollcommand=hscrollbar.set)
        hscrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Right Side: Persistent Cart Panel
        cart_subframe = tk.LabelFrame(table_frame, text=" 🛒 Selected Cart (Double-click to remove) ", font=("Segoe UI", 9, "bold"), bg=self.card_color, fg=self.primary_color, bd=1, relief=tk.SOLID, padx=5, pady=5, width=280)
        cart_subframe.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False, padx=(12, 0))
        cart_subframe.pack_propagate(False)

        cart_columns = ("Medicine Name", "Stock", "Price")
        self.cart_tree = ttk.Treeview(cart_subframe, columns=cart_columns, show="headings", height=12, selectmode="browse")
        for col in cart_columns:
            self.cart_tree.heading(col, text=col)
            self.cart_tree.column(col, width=90 if col != "Medicine Name" else 110)

        cart_scrollbar = ttk.Scrollbar(cart_subframe, orient=tk.VERTICAL, command=self.cart_tree.yview)
        self.cart_tree.configure(yscrollcommand=cart_scrollbar.set)
        self.cart_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        cart_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.cart_tree.bind("<Double-1>", self.remove_from_cart)

        # ==========================================
        # TAB 2: INVOICE OCR SCANNER (New Feature)
        # ==========================================
        ocr_split_frame = tk.Frame(self.tab2, bg=self.bg_color)
        ocr_split_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left Panel (Image & Processing)
        left_panel = tk.Frame(ocr_split_frame, bg=self.bg_color, width=340)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=5, pady=5)
        left_panel.pack_propagate(False)

        self.scan_btn = tk.Button(left_panel, text="📷 Select & Scan Invoice Image", bg="#8b5cf6", fg="white", font=("Segoe UI", 10, "bold"), pady=8, relief=tk.FLAT, bd=0, command=self.select_and_scan_invoice)
        self.scan_btn.pack(fill=tk.X, pady=5)
        bind_hover(self.scan_btn, "#8b5cf6", "#7c3aed")

        img_frame = tk.LabelFrame(left_panel, text=" Invoice Preview ", font=("Segoe UI", 9, "bold"), bg=self.bg_color, fg=self.primary_color, bd=1, relief=tk.SOLID)
        img_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.image_label = tk.Label(img_frame, text="No invoice selected\n(Click button above to browse)", font=("Segoe UI", 9), fg=self.text_light, bg=self.card_color, bd=0)
        self.image_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.progress_label = tk.Label(left_panel, text="Status: Idle", font=("Segoe UI", 9, "bold"), fg=self.text_color, bg=self.bg_color)
        self.progress_label.pack(anchor=tk.W, pady=2)
        self.ocr_progress = ttk.Progressbar(left_panel, orient=tk.HORIZONTAL, mode='determinate')
        self.ocr_progress.pack(fill=tk.X, pady=5)

        tk.Label(left_panel, text="OCR Scanner Logs:", font=("Segoe UI", 8, "bold"), fg=self.text_light, bg=self.bg_color).pack(anchor=tk.W)
        self.log_text = tk.Text(left_panel, height=6, font=("Consolas", 8), bg=self.primary_color, fg="#94a3b8", bd=0, padx=5, pady=5)
        self.log_text.pack(fill=tk.X, pady=2)
        self.log_text.insert(tk.END, "OCR Engine initialized. Ready.\n")
        self.log_text.config(state=tk.DISABLED)

        # Right Panel (Extracted Data Review Table)
        right_panel = tk.LabelFrame(ocr_split_frame, text=" Reviewed Extracted Data ", font=("Segoe UI", 10, "bold"), bg=self.card_color, fg=self.primary_color, bd=1, relief=tk.SOLID, padx=10, pady=10)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        tip_label = tk.Label(right_panel,
            text="💡 Double-click = Edit  |  Ctrl/Shift+Click = Multi-Select  |  Del/Backspace = Delete Selected",
            font=("Segoe UI", 8, "italic"), fg=self.accent_color, bg="#eff6ff", pady=5)
        tip_label.pack(fill=tk.X, padx=0, pady=5)

        ocr_table_frame = tk.Frame(right_panel, bg=self.card_color)
        ocr_table_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        ocr_columns = (
            "Medicine Name", "Generic Name", "Manufacturer", "Category", "Form", "Dosage",
            "Barcode", "Batch Number", "Expiry Date", "Pack Size", "Cost Price", "Retail Price",
            "Tax Rate", "Discount Allowed", "Quantity"
        )
        self.ocr_tree = ttk.Treeview(ocr_table_frame, columns=ocr_columns, show="headings", height=12, selectmode="extended")
        
        ocr_scrollbar = ttk.Scrollbar(ocr_table_frame, orient=tk.VERTICAL, command=self.ocr_tree.yview)
        ocr_hscroll = ttk.Scrollbar(ocr_table_frame, orient=tk.HORIZONTAL, command=self.ocr_tree.xview)
        self.ocr_tree.configure(yscrollcommand=ocr_scrollbar.set, xscrollcommand=ocr_hscroll.set)
        
        for col in ocr_columns:
            self.ocr_tree.heading(col, text=col)
            self.ocr_tree.column(col, width=100 if col not in ("Medicine Name", "Generic Name") else 140)

        ocr_hscroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.ocr_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ocr_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.ocr_tree.bind("<Double-1>", self.edit_ocr_row)
        self.ocr_tree.bind("<Delete>",   lambda e: self.delete_selected_ocr_rows())
        self.ocr_tree.bind("<BackSpace>", lambda e: self.delete_selected_ocr_rows())

        ocr_btn_frame = tk.Frame(right_panel, bg=self.card_color, pady=5)
        ocr_btn_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=0)

        self.ocr_save_btn = tk.Button(ocr_btn_frame, text="💾 Save & Bulk Sync to Cloud", bg=self.success_color, fg="white", font=("Segoe UI", 9, "bold"), padx=15, pady=6, state=tk.DISABLED, relief=tk.FLAT, bd=0, command=self.save_bulk_ocr_data)
        self.ocr_save_btn.pack(side=tk.RIGHT, padx=5)
        bind_hover(self.ocr_save_btn, self.success_color, "#059669")

        self.ocr_delete_btn = tk.Button(ocr_btn_frame, text="❌ Delete Selected Row(s)", bg=self.danger_color, fg="white", font=("Segoe UI", 9, "bold"), padx=15, pady=6, relief=tk.FLAT, bd=0, command=self.delete_selected_ocr_rows)
        self.ocr_delete_btn.pack(side=tk.RIGHT, padx=5)
        bind_hover(self.ocr_delete_btn, self.danger_color, "#dc2626")

        self.ocr_clear_btn = tk.Button(ocr_btn_frame, text="🗑️ Clear All", bg=self.text_light, fg="white", font=("Segoe UI", 9, "bold"), padx=15, pady=6, relief=tk.FLAT, bd=0, command=self.clear_ocr_data)
        self.ocr_clear_btn.pack(side=tk.RIGHT, padx=5)
        bind_hover(self.ocr_clear_btn, self.text_light, "#475569")

        # Initialize Sales Widgets & Data
        self.create_sales_widgets()
        self.load_sales_analytics()

    def create_sales_widgets(self):
        # Modern Color Palette helpers and hover support
        def bind_hover(btn, normal_bg, hover_bg):
            btn.bind("<Enter>", lambda e: btn.config(bg=hover_bg))
            btn.bind("<Leave>", lambda e: btn.config(bg=normal_bg))

        # Main sales container frame
        main_sales_frame = tk.Frame(self.tab3, bg=self.bg_color)
        main_sales_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        # 1. Top Controls Bar
        ctrl_frame = tk.Frame(main_sales_frame, bg=self.bg_color)
        ctrl_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_lbl = tk.Label(ctrl_frame, text="📊 Sales & Revenue Analytics Dashboard", 
                             font=("Segoe UI", 14, "bold"), bg=self.bg_color, fg=self.primary_color)
        title_lbl.pack(side=tk.LEFT)
        
        # Period Filter controls
        filter_subframe = tk.Frame(ctrl_frame, bg=self.bg_color)
        filter_subframe.pack(side=tk.RIGHT)
        
        tk.Label(filter_subframe, text="Period Filter:", font=("Segoe UI", 9, "bold"), 
                 bg=self.bg_color, fg=self.text_color).pack(side=tk.LEFT, padx=5)
        
        # ttk Combobox for styling
        self.sales_period_combo = ttk.Combobox(filter_subframe, values=["Today", "This Month", "All Time"], 
                                               state="readonly", width=12, font=("Segoe UI", 9))
        self.sales_period_combo.pack(side=tk.LEFT, padx=5)
        self.sales_period_combo.set("Today")
        self.sales_period_combo.bind("<<ComboboxSelected>>", lambda e: self.load_sales_analytics())
        
        refresh_btn = tk.Button(filter_subframe, text="🔄 Refresh Stats", font=("Segoe UI", 9, "bold"), 
                                bg=self.accent_color, fg="white", relief=tk.FLAT, bd=0, padx=12, pady=4,
                                command=self.load_sales_analytics)
        refresh_btn.pack(side=tk.LEFT, padx=5)
        bind_hover(refresh_btn, self.accent_color, "#1d4ed8")
        
        # 2. Stats Cards (KPI Row)
        kpi_frame = tk.Frame(main_sales_frame, bg=self.bg_color)
        kpi_frame.pack(fill=tk.X, pady=(0, 15))
        
        # We configure 4 equal columns for cards
        kpi_frame.columnconfigure(0, weight=1)
        kpi_frame.columnconfigure(1, weight=1)
        kpi_frame.columnconfigure(2, weight=1)
        kpi_frame.columnconfigure(3, weight=1)
        
        def create_kpi_card(parent, col, title, color):
            card = tk.Frame(parent, bg=self.card_color, highlightthickness=1, highlightbackground="#e2e8f0", bd=0, padx=15, pady=12)
            card.grid(row=0, column=col, padx=4 if col in (1, 2) else (0, 4) if col == 0 else (4, 0), sticky="nsew")
            
            title_lbl = tk.Label(card, text=title, font=("Segoe UI", 9, "bold"), bg=self.card_color, fg=self.text_light)
            title_lbl.pack(anchor=tk.W)
            
            val_lbl = tk.Label(card, text="Rs 0.00", font=("Segoe UI", 15, "bold"), bg=self.card_color, fg=color)
            val_lbl.pack(anchor=tk.W, pady=(5, 0))
            
            return val_lbl
            
        self.lbl_revenue_val = create_kpi_card(kpi_frame, 0, "Revenue (Net Sales)", self.accent_color)
        self.lbl_profit_val = create_kpi_card(kpi_frame, 1, "Net Profit Margin", self.success_color)
        self.lbl_orders_val = create_kpi_card(kpi_frame, 2, "Total Orders / Invoices", self.warn_color)
        self.lbl_items_val = create_kpi_card(kpi_frame, 3, "Total Medicine Items Sold", "#7c3aed")
        
        # 3. Bottom Data Tables (Split View)
        tables_frame = tk.Frame(main_sales_frame, bg=self.bg_color)
        tables_frame.pack(fill=tk.BOTH, expand=True)
        
        # Split left and right panels
        left_table_card = tk.LabelFrame(tables_frame, text=" 📋 Recent Sales Log ", font=("Segoe UI", 10, "bold"),
                                        bg=self.card_color, fg=self.primary_color, bd=1, relief=tk.SOLID, padx=10, pady=10)
        left_table_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))
        
        # Recent Sales Treeview
        tx_cols = ("Invoice No", "Date/Time", "Items Sold", "Qty", "Total Paid", "Profit")
        self.sales_tree = ttk.Treeview(left_table_card, columns=tx_cols, show="headings", height=12, selectmode="browse")
        
        # Scrollbars for sales tree
        sales_scroll = ttk.Scrollbar(left_table_card, orient=tk.VERTICAL, command=self.sales_tree.yview)
        sales_hscroll = ttk.Scrollbar(left_table_card, orient=tk.HORIZONTAL, command=self.sales_tree.xview)
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
        
        # Right Panel (Top Selling Products)
        right_table_card = tk.LabelFrame(tables_frame, text=" 🏆 Top 10 Selling Products ", font=("Segoe UI", 10, "bold"),
                                         bg=self.card_color, fg=self.primary_color, bd=1, relief=tk.SOLID, padx=10, pady=10)
        right_table_card.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(8, 0))
        
        top_cols = ("Medicine Name", "Formula", "Qty Sold", "Revenue", "Profit")
        self.top_products_tree = ttk.Treeview(right_table_card, columns=top_cols, show="headings", height=12, selectmode="browse")
        
        # Scrollbars for top products tree
        top_scroll = ttk.Scrollbar(right_table_card, orient=tk.VERTICAL, command=self.top_products_tree.yview)
        top_hscroll = ttk.Scrollbar(right_table_card, orient=tk.HORIZONTAL, command=self.top_products_tree.xview)
        self.top_products_tree.configure(yscrollcommand=top_scroll.set, xscrollcommand=top_hscroll.set)
        
        for col in top_cols:
            self.top_products_tree.heading(col, text=col)
            self.top_products_tree.column(col, width=120 if col not in ("Medicine Name", "Formula") else 140)
            
        top_hscroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.top_products_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        top_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def load_sales_analytics(self):
        # 1. Clear existing rows
        for child in self.sales_tree.get_children():
            self.sales_tree.delete(child)
        for child in self.top_products_tree.get_children():
            self.top_products_tree.delete(child)
            
        # 2. Determine Period Filter
        period = self.sales_period_combo.get()
        query_date = ""
        params = []
        if period == "Today":
            query_date = "WHERE sale_date LIKE ?"
            params.append(f"{datetime.datetime.now().strftime('%Y-%m-%d')}%")
        elif period == "This Month":
            query_date = "WHERE sale_date LIKE ?"
            params.append(f"{datetime.datetime.now().strftime('%Y-%m')}%")
            
        # 3. Query Stats
        try:
            stats_sql = f"""
                SELECT 
                    COALESCE(SUM(net_total), 0.0), 
                    COALESCE(SUM(profit), 0.0), 
                    COUNT(DISTINCT invoice_no), 
                    COALESCE(SUM(quantity), 0)
                FROM SalesHistory
                {query_date}
            """
            self.cursor.execute(stats_sql, params)
            rev, prof, orders, items = self.cursor.fetchone()
            
            # Update labels
            self.lbl_revenue_val.config(text=f"Rs {rev:,.2f}")
            self.lbl_profit_val.config(text=f"Rs {prof:,.2f}")
            self.lbl_orders_val.config(text=str(orders))
            self.lbl_items_val.config(text=str(items))
            
            # 4. Query Recent Transactions grouped by invoice
            tx_sql = f"""
                SELECT 
                    invoice_no, 
                    MIN(sale_date), 
                    GROUP_CONCAT(medicine_name || ' (' || quantity || ')', ', '), 
                    SUM(quantity), 
                    SUM(net_total), 
                    SUM(profit) 
                FROM SalesHistory 
                {query_date} 
                GROUP BY invoice_no 
                ORDER BY MIN(sale_date) DESC
            """
            self.cursor.execute(tx_sql, params)
            for row in self.cursor.fetchall():
                inv, dt, meds, qty, total, profit = row
                self.sales_tree.insert("", tk.END, values=(
                    inv, dt, meds, qty, f"Rs {total:,.2f}", f"Rs {profit:,.2f}"
                ))
                
            # 5. Query Top Products
            top_sql = f"""
                SELECT 
                    medicine_name, 
                    generic_formula, 
                    SUM(quantity), 
                    SUM(net_total), 
                    SUM(profit) 
                FROM SalesHistory 
                {query_date} 
                GROUP BY medicine_name 
                ORDER BY SUM(quantity) DESC 
                LIMIT 10
            """
            self.cursor.execute(top_sql, params)
            for row in self.cursor.fetchall():
                name, formula, qty, total, profit = row
                self.top_products_tree.insert("", tk.END, values=(
                    name, formula, qty, f"Rs {total:,.2f}", f"Rs {profit:,.2f}"
                ))
                
        except Exception as e:
            print(f"Error loading sales analytics: {e}")

    def pull_inventory_from_cloud(self):
        if not self.pharmacy_license:
            return
        try:
            client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
            cloud_db = client['MediLinkDB']
            cloud_items = list(cloud_db.Inventory.find({"pharmacy_license": self.pharmacy_license}))
            
            if cloud_items:
                for item in cloud_items:
                    brand_name = item.get("brand_name", item.get("medicine_name"))
                    formula = item.get("generic_formula", "N/A")
                    price = item.get("price", item.get("retail_price", 0.0))
                    expiry = item.get("expiry_date", "12/27")
                    qty = item.get("quantity", 0)
                    manufacturer = item.get("manufacturer", "Unknown")
                    category = item.get("category", "General")
                    form = item.get("form", "Tablet")
                    dosage = item.get("dosage", "N/A")
                    barcode = item.get("barcode", "N/A")
                    batch = item.get("batch_number", "N/A")
                    pack_size = item.get("pack_size", "10s")
                    cost_price = item.get("cost_price", 0.0)
                    retail_price = item.get("retail_price", price)
                    tax_rate = item.get("tax_rate", 0.0)
                    discount = item.get("discount_allowed", 0.0)
                    
                    self.cursor.execute("""
                        INSERT OR REPLACE INTO LocalInventoryV2 (
                            brand_name, generic_formula, price, expiry_date, quantity,
                            manufacturer, category, form, dosage, barcode, batch_number,
                            pack_size, cost_price, retail_price, tax_rate, discount_allowed
                        ) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        brand_name, formula, retail_price, expiry, qty,
                        manufacturer, category, form, dosage, barcode, batch,
                        pack_size, cost_price, retail_price, tax_rate, discount
                    ))
                self.conn.commit()
        except Exception as e:
            print(f"Error pulling inventory from cloud: {e}")



    def load_local_inventory(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        self.cursor.execute("""
            SELECT brand_name, generic_formula, manufacturer, category, form, dosage, 
                   barcode, batch_number, expiry_date, pack_size, cost_price, 
                   retail_price, tax_rate, discount_allowed, quantity 
            FROM LocalInventoryV2 WHERE quantity > 0
        """)
        for row in self.cursor.fetchall():
            cost_price = f"Rs {row[10]:.2f}" if row[10] is not None else "N/A"
            retail_price = f"Rs {row[11]:.2f}" if row[11] is not None else "N/A"
            tax_rate = f"{row[12]}%" if row[12] is not None else "N/A"
            discount = f"{row[13]}%" if row[13] is not None else "N/A"
            
            self.tree.insert("", tk.END, values=(
                row[0], row[1], row[2], row[3], row[4], row[5],
                row[6], row[7], row[8], row[9], cost_price,
                retail_price, tax_rate, discount, row[14]
            ))

    def add_local_stock(self):
        name = self.name_entry.get().strip().title()
        if not name:
            messagebox.showwarning("Input Error", "Medicine Name is required.")
            return

        qty_str = self.qty_entry.get().strip()
        retail_price_str = self.retail_price_entry.get().strip()

        if not qty_str or not retail_price_str:
            messagebox.showwarning("Input Error", "Quantity and Retail Price are required.")
            return

        try:
            qty = int(qty_str)
            retail_price = float(retail_price_str)
        except ValueError:
            messagebox.showwarning("Input Error", "Quantity and Retail Price must be valid numbers.")
            return

        # Optional fields with defaults
        formula = self.formula_entry.get().strip().title() or "N/A"
        manufacturer = self.manufacturer_entry.get().strip().title() or "Unknown"
        category = self.category_entry.get().strip().title() or "General"
        form = self.form_entry.get().strip().title() or "Tablet"
        dosage = self.dosage_entry.get().strip() or "N/A"
        barcode = self.barcode_entry.get().strip() or "N/A"
        batch = self.batch_entry.get().strip() or "N/A"
        expiry = self.expiry_entry.get().strip() or "12/27"
        pack_size = self.pack_size_entry.get().strip() or "10s"

        cost_price_str = self.cost_price_entry.get().strip()
        cost_price = 0.0
        if cost_price_str:
            try:
                cost_price = float(cost_price_str)
            except ValueError:
                messagebox.showwarning("Input Error", "Cost Price must be a valid number.")
                return

        tax_rate_str = self.tax_rate_entry.get().strip()
        tax_rate = 0.0
        if tax_rate_str:
            try:
                tax_rate = float(tax_rate_str)
            except ValueError:
                messagebox.showwarning("Input Error", "Tax Rate must be a valid number.")
                return

        discount_str = self.discount_entry.get().strip()
        discount = 0.0
        if discount_str:
            try:
                discount = float(discount_str)
            except ValueError:
                messagebox.showwarning("Input Error", "Discount must be a valid number.")
                return

        try:
            # We set both 'price' and 'retail_price' to retail_price to keep backward compatibility
            self.cursor.execute("""
                INSERT OR REPLACE INTO LocalInventoryV2 (
                    brand_name, generic_formula, price, expiry_date, quantity,
                    manufacturer, category, form, dosage, barcode, batch_number,
                    pack_size, cost_price, retail_price, tax_rate, discount_allowed
                ) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                name, formula, retail_price, expiry, qty,
                manufacturer, category, form, dosage, barcode, batch,
                pack_size, cost_price, retail_price, tax_rate, discount
            ))
            self.conn.commit()
            
            # Clear all entry fields
            for entry in [
                self.name_entry, self.formula_entry, self.manufacturer_entry,
                self.category_entry, self.form_entry, self.dosage_entry,
                self.barcode_entry, self.batch_entry, self.expiry_entry,
                self.pack_size_entry, self.cost_price_entry, self.retail_price_entry,
                self.tax_rate_entry, self.discount_entry, self.qty_entry
            ]:
                entry.delete(0, tk.END)
            
            self.load_local_inventory()
            self.load_db_brands()
            messagebox.showinfo("Success", f"{name} updated in local stock.")
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def filter_inventory(self, event=None):
        if getattr(self, "search_job", None):
            self.root.after_cancel(self.search_job)
        self.search_job = self.root.after(200, self.perform_filter_query)

    def perform_filter_query(self):
        query = self.search_entry.get().strip().lower()
        for row in self.tree.get_children():
            self.tree.delete(row)
            
        if not query:
            self.load_local_inventory()
            return
            
        self.cursor.execute("""
            SELECT brand_name, generic_formula, manufacturer, category, form, dosage, 
                   barcode, batch_number, expiry_date, pack_size, cost_price, 
                   retail_price, tax_rate, discount_allowed, quantity 
            FROM LocalInventoryV2 
            WHERE (LOWER(brand_name) LIKE ? OR LOWER(generic_formula) LIKE ?) AND quantity > 0
        """, (f"%{query}%", f"%{query}%"))
        
        for row in self.cursor.fetchall():
            cost_price = f"Rs {row[10]:.2f}" if row[10] is not None else "N/A"
            retail_price = f"Rs {row[11]:.2f}" if row[11] is not None else "N/A"
            tax_rate = f"{row[12]}%" if row[12] is not None else "N/A"
            discount = f"{row[13]}%" if row[13] is not None else "N/A"
            
            self.tree.insert("", tk.END, values=(
                row[0], row[1], row[2], row[3], row[4], row[5],
                row[6], row[7], row[8], row[9], cost_price,
                retail_price, tax_rate, discount, row[14]
            ))

    def clear_search(self):
        self.search_entry.delete(0, tk.END)
        self.load_local_inventory()

    def sell_medicine(self):
        if not self.cart:
            messagebox.showwarning("Cart Empty", "Your checkout cart is empty. Please select medicines from the list and double-click or click 'Add Selected to Cart' first.")
            return

        items_to_sell = list(self.cart.values())

        # Custom Checkout Dialog Window
        checkout_win = tk.Toplevel(self.root)
        checkout_win.title("Checkout - MediLink Pharmacy")
        checkout_win.geometry("520x600")
        checkout_win.configure(bg="#f8fafc")
        checkout_win.resizable(False, False)
        checkout_win.transient(self.root)
        checkout_win.grab_set()

        # Header Bar
        hdr = tk.Frame(checkout_win, bg=self.primary_color, height=50)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)
        tk.Label(hdr, text="🛒 Multi-Medicine Checkout Portal", font=("Segoe UI", 11, "bold"), fg="white", bg=self.primary_color).pack(pady=12)

        # Main Container
        main_frame = tk.Frame(checkout_win, bg="#f8fafc", padx=20, pady=15)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Scrollable area for items
        scroll_container = tk.Frame(main_frame, bg="#f8fafc")
        scroll_container.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        canvas = tk.Canvas(scroll_container, bg="#f8fafc", highlightthickness=0)
        v_scroll = ttk.Scrollbar(scroll_container, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#f8fafc")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=v_scroll.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.bind('<Configure>', lambda event: canvas.itemconfig(canvas_window, width=event.width))

        row_widgets = []

        def remove_item_from_checkout(item_name, card_widget):
            # 1. Remove from self.cart
            if item_name in self.cart:
                del self.cart[item_name]
            # 2. Update the main application's cart display
            self.update_cart_display()
            # 3. Destroy the card widget
            card_widget.destroy()
            # 4. Remove from row_widgets list
            for rw in list(row_widgets):
                if rw["item"]["name"] == item_name:
                    row_widgets.remove(rw)
                    break
            # 5. Re-run live calculations
            run_live_calc()
            # 6. If no items left, close checkout window
            if not row_widgets:
                checkout_win.destroy()

        for item in items_to_sell:
            item_card = tk.Frame(scrollable_frame, bg="#ffffff", bd=0, highlightthickness=1, highlightbackground="#e2e8f0", padx=10, pady=8)
            item_card.pack(fill=tk.X, pady=4, padx=5)

            # Left side: Name & Stock info
            info_sub = tk.Frame(item_card, bg="#ffffff")
            info_sub.pack(side=tk.LEFT, fill=tk.X, expand=True)

            tk.Label(info_sub, text=item["name"], font=("Segoe UI", 10, "bold"), bg="#ffffff", fg=self.text_color, anchor=tk.W).pack(fill=tk.X)
            tk.Label(info_sub, text=f"Stock: {item['current_qty']} | Expiry: {item['expiry']}", font=("Segoe UI", 8), bg="#ffffff", fg=self.text_light, anchor=tk.W).pack(fill=tk.X)

            # Right side: Inputs
            inputs_sub = tk.Frame(item_card, bg="#ffffff")
            inputs_sub.pack(side=tk.RIGHT)

            # Qty entry
            tk.Label(inputs_sub, text="Qty:", font=("Segoe UI", 8, "bold"), bg="#ffffff", fg=self.text_color).grid(row=0, column=0, padx=2, sticky=tk.E)
            qty_ent = tk.Entry(inputs_sub, font=("Segoe UI", 9), bg="#ffffff", fg=self.text_color,
                               relief=tk.FLAT, bd=0, highlightthickness=1,
                               highlightbackground="#cbd5e1", highlightcolor=self.accent_color,
                               insertbackground=self.text_color, width=6)
            qty_ent.grid(row=0, column=1, padx=2, pady=2)
            qty_ent.insert(0, "1")

            # Price entry
            tk.Label(inputs_sub, text="Price:", font=("Segoe UI", 8, "bold"), bg="#ffffff", fg=self.text_color).grid(row=0, column=2, padx=2, sticky=tk.E)
            prc_ent = tk.Entry(inputs_sub, font=("Segoe UI", 9), bg="#ffffff", fg=self.text_color,
                               relief=tk.FLAT, bd=0, highlightthickness=1,
                               highlightbackground="#cbd5e1", highlightcolor=self.accent_color,
                               insertbackground=self.text_color, width=8)
            prc_ent.grid(row=0, column=3, padx=2, pady=2)
            prc_ent.insert(0, f"{item['retail_price']:.2f}")

            # Delete button
            del_btn = tk.Button(inputs_sub, text="🗑️", bg="#2563eb", fg="white",
                                activebackground="#1d4ed8", font=("Segoe UI", 9),
                                relief=tk.FLAT, bd=0, padx=6, pady=2, cursor="hand2")
            del_btn.grid(row=0, column=4, padx=(8, 2), pady=2)

            rw_dict = {
                "item": item,
                "qty_entry": qty_ent,
                "price_entry": prc_ent
            }
            row_widgets.append(rw_dict)
            del_btn.config(command=lambda name=item["name"], card=item_card: remove_item_from_checkout(name, card))

        # Summary Frame (Live calculations)
        summary_frame = tk.LabelFrame(main_frame, text=" Live Order Summary ", font=("Segoe UI", 9, "bold"), bg="#f1f5f9", fg=self.primary_color, padx=15, pady=10, bd=1, relief=tk.SOLID)
        summary_frame.pack(fill=tk.X, pady=(0, 10))

        def create_summary_row(parent, row_num, label_text, is_bold=False):
            color = self.text_color if is_bold else self.text_light
            font_spec = ("Segoe UI", 9, "bold") if is_bold else ("Segoe UI", 9)
            lbl = tk.Label(parent, text=label_text, font=font_spec, bg="#f1f5f9", fg=color)
            lbl.grid(row=row_num, column=0, sticky=tk.W, pady=2)
            val = tk.Label(parent, text="Rs 0.00", font=font_spec, bg="#f1f5f9", fg=self.text_color)
            val.grid(row=row_num, column=1, sticky=tk.E, pady=2)
            parent.grid_columnconfigure(1, weight=1)
            return val

        lbl_subtotal = create_summary_row(summary_frame, 0, "Subtotal:")
        lbl_discount = create_summary_row(summary_frame, 1, "Total Discount:")
        lbl_tax = create_summary_row(summary_frame, 2, "Total Tax:")
        lbl_net = create_summary_row(summary_frame, 3, "Net Total Payable:", is_bold=True)

        # Warning/Error Label
        err_lbl = tk.Label(main_frame, text="", font=("Segoe UI", 9, "bold"), fg=self.danger_color, bg="#f8fafc", wraplength=400)
        err_lbl.pack(fill=tk.X, pady=5)

        # Action Buttons
        btn_box = tk.Frame(main_frame, bg="#f8fafc")
        btn_box.pack(fill=tk.X, side=tk.BOTTOM, pady=10)

        confirm_btn = tk.Button(btn_box, text="✔️ Confirm Sale", bg="#2563eb", fg="white", font=("Segoe UI", 10, "bold"), relief=tk.FLAT, bd=0, padx=15, pady=8)
        confirm_btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        confirm_btn.bind("<Enter>", lambda e: confirm_btn.config(bg="#1d4ed8") if confirm_btn["state"] == tk.NORMAL or confirm_btn["state"] == "normal" else None)
        confirm_btn.bind("<Leave>", lambda e: confirm_btn.config(bg="#2563eb") if confirm_btn["state"] == tk.NORMAL or confirm_btn["state"] == "normal" else None)

        def checkout_clear_cart():
            self.clear_cart()
            checkout_win.destroy()

        clear_btn = tk.Button(btn_box, text="🗑️ Clear Cart", bg="#2563eb", fg="white", font=("Segoe UI", 10, "bold"), relief=tk.FLAT, bd=0, padx=15, pady=8, command=checkout_clear_cart)
        clear_btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        clear_btn.bind("<Enter>", lambda e: clear_btn.config(bg="#1d4ed8"))
        clear_btn.bind("<Leave>", lambda e: clear_btn.config(bg="#2563eb"))

        cancel_btn = tk.Button(btn_box, text="❌ Cancel", bg="#2563eb", fg="white", font=("Segoe UI", 10, "bold"), relief=tk.FLAT, bd=0, padx=15, pady=8, command=checkout_win.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        cancel_btn.bind("<Enter>", lambda e: cancel_btn.config(bg="#1d4ed8"))
        cancel_btn.bind("<Leave>", lambda e: cancel_btn.config(bg="#2563eb"))

        def run_live_calc(event=None):
            total_subtotal = 0.0
            total_discount = 0.0
            total_tax = 0.0
            total_net = 0.0

            has_error = False
            error_msg = ""

            for rw in row_widgets:
                qty_text = rw["qty_entry"].get().strip()
                prc_text = rw["price_entry"].get().strip()
                item = rw["item"]

                if not qty_text or not prc_text:
                    has_error = True
                    continue

                # Validate Quantity
                try:
                    sell_qty = int(qty_text)
                    if sell_qty <= 0:
                        raise ValueError
                except ValueError:
                    has_error = True
                    error_msg = f"⚠️ Qty for {item['name']} must be a positive integer."
                    break

                if sell_qty > item["current_qty"]:
                    has_error = True
                    error_msg = f"⚠️ Qty for {item['name']} exceeds stock ({item['current_qty']})."
                    break

                # Validate Price
                try:
                    sell_price = float(prc_text)
                    if sell_price <= 0:
                        raise ValueError
                except ValueError:
                    has_error = True
                    error_msg = f"⚠️ Price for {item['name']} must be a positive number."
                    break

                # Calculations
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
                confirm_btn.config(state=tk.DISABLED, bg="#94a3b8")
                if error_msg:
                    err_lbl.config(text=error_msg)
                else:
                    err_lbl.config(text="")

                lbl_subtotal.config(text="Rs 0.00")
                lbl_discount.config(text="Rs 0.00")
                lbl_tax.config(text="Rs 0.00")
                lbl_net.config(text="Rs 0.00")
            else:
                confirm_btn.config(state=tk.NORMAL, bg="#2563eb")
                err_lbl.config(text="")

                lbl_subtotal.config(text=f"Rs {total_subtotal:.2f}")
                lbl_discount.config(text=f"-Rs {total_discount:.2f}")
                lbl_tax.config(text=f"+Rs {total_tax:.2f}")
                lbl_net.config(text=f"Rs {total_net:.2f}")

        for rw in row_widgets:
            rw["qty_entry"].bind("<KeyRelease>", run_live_calc)
            rw["price_entry"].bind("<KeyRelease>", run_live_calc)

        # Trigger initial calculation
        run_live_calc()

        # Expose calculations function for testing
        checkout_win.run_live_calc = run_live_calc

        def confirm_checkout():
            # Gather and re-validate all row data
            sales_data = []
            for rw in row_widgets:
                qty_text = rw["qty_entry"].get().strip()
                prc_text = rw["price_entry"].get().strip()
                item = rw["item"]

                try:
                    sell_qty = int(qty_text)
                    sell_price = float(prc_text)
                    if sell_qty <= 0 or sell_price <= 0 or sell_qty > item["current_qty"]:
                        raise ValueError
                except ValueError:
                    messagebox.showerror("Checkout Error", f"Invalid input for {item['name']}.", parent=checkout_win)
                    return

                sales_data.append({
                    "item": item,
                    "sell_qty": sell_qty,
                    "sell_price": sell_price
                })

            # Perform SQLite updates
            invoice_no = f"INV-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
            sale_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for sale in sales_data:
                item = sale["item"]
                sell_qty = sale["sell_qty"]
                sell_price = sale["sell_price"]
                new_qty = item["current_qty"] - sell_qty

                # Update SQLite database - decrement qty, update price
                self.cursor.execute("""
                    UPDATE LocalInventoryV2 
                    SET quantity = ?, price = ?, retail_price = ? 
                    WHERE brand_name = ?
                """, (new_qty, sell_price, sell_price, item["name"]))

                # Calculate discount, tax, net_total and profit for SalesHistory
                sub = sell_qty * sell_price
                disc = sub * (item.get("discount_rate", 0.0) / 100.0)
                taxable = sub - disc
                tax = taxable * (item.get("tax_rate", 0.0) / 100.0)
                net = taxable + tax
                cost_price = item.get("cost_price", 0.0)
                profit = sub - disc - (cost_price * sell_qty)

                self.cursor.execute("""
                    INSERT INTO SalesHistory (
                        invoice_no, sale_date, medicine_name, generic_formula,
                        quantity, sell_price, cost_price, discount, tax, net_total, profit
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    invoice_no, sale_date, item["name"], item["formula"],
                    sell_qty, sell_price, cost_price, disc, tax, net, profit
                ))
            self.conn.commit()

            # Instantly update Cloud MongoDB database if online and license is configured (using background thread to keep UI fast)
            if self.pharmacy_license:
                def run_cloud_update():
                    try:
                        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
                        cloud_db = client['MediLinkDB']
                        for sale in sales_data:
                            item = sale["item"]
                            sell_qty = sale["sell_qty"]
                            sell_price = sale["sell_price"]
                            new_qty = item["current_qty"] - sell_qty
                            
                            cloud_db.Inventory.update_one(
                                {
                                    "medicine_name": item["name"],
                                    "pharmacy_license": self.pharmacy_license
                                },
                                {
                                    "$set": {
                                        "quantity": new_qty,
                                        "price": sell_price,
                                        "retail_price": sell_price,
                                        "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                    }
                                }
                            )
                    except Exception as e:
                        print(f"Cloud update error during checkout: {e}")
                threading.Thread(target=run_cloud_update, daemon=True).start()

            # Calc totals for receipt
            total_subtotal = 0.0
            total_discount = 0.0
            total_tax = 0.0
            total_net = 0.0

            pharmacy_name = getattr(self, "pharmacy_name", "MediLink Pharmacy") or "MediLink Pharmacy"

            invoice_text = f"=========================================\n"
            invoice_text += f"        {pharmacy_name.upper()}\n"
            if self.lat and self.lng:
                invoice_text += f"  Location: Lat {self.lat}, Lng {self.lng}\n"
            invoice_text += f"  License: {self.pharmacy_license}\n"
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

            self.load_local_inventory()
            self.clear_cart()
            self.load_sales_analytics()
            checkout_win.destroy()

            # Show receipt in a modern scrollable window
            receipt_win = tk.Toplevel(self.root)
            receipt_win.title("Sale Invoice / Receipt")
            receipt_win.geometry("420x580")
            receipt_win.configure(bg="#f1f5f9")
            receipt_win.resizable(False, False)
            receipt_win.transient(self.root)
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
                    import os
                    os.startfile(receipt_filename, "print")
                except Exception as e:
                    messagebox.showerror("Printing Error", f"Failed to send to printer: {e}", parent=receipt_win)

            print_btn = tk.Button(btn_box, text="🖨️ Print Invoice", bg="#2563eb", fg="white", font=("Segoe UI", 9, "bold"), relief=tk.FLAT, bd=0, padx=20, pady=6, command=print_invoice)
            print_btn.pack(side=tk.LEFT, padx=10)
            print_btn.bind("<Enter>", lambda e: print_btn.config(bg="#1d4ed8"))
            print_btn.bind("<Leave>", lambda e: print_btn.config(bg="#2563eb"))

            close_btn = tk.Button(btn_box, text="❌ Dismiss", bg="#2563eb", fg="white", font=("Segoe UI", 9, "bold"), relief=tk.FLAT, bd=0, padx=20, pady=6, command=receipt_win.destroy)
            close_btn.pack(side=tk.LEFT, padx=10)
            close_btn.bind("<Enter>", lambda e: close_btn.config(bg="#1d4ed8"))
            close_btn.bind("<Leave>", lambda e: close_btn.config(bg="#2563eb"))

        confirm_btn.config(command=confirm_checkout)
        confirm_btn.bind("<Enter>", lambda e: confirm_btn.config(bg="#059669") if confirm_btn['state'] == tk.NORMAL else None)
        confirm_btn.bind("<Leave>", lambda e: confirm_btn.config(bg=self.success_color) if confirm_btn['state'] == tk.NORMAL else None)

        # Expose checkout confirmation command for testing
        checkout_win.confirm_checkout = confirm_checkout

    def add_to_cart(self, event=None):
        selected_items = self.tree.selection()
        if not selected_items and event is None:
            messagebox.showwarning("Select Medicine", "Please select one or more medicines from the list to add to cart.")
            return

        added_count = 0
        for sel in selected_items:
            item_values = self.tree.item(sel, "values")
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

            # Add to cart
            self.cart[name] = {
                "name": name,
                "formula": formula,
                "manufacturer": manufacturer,
                "category": category,
                "form": form,
                "dosage": dosage,
                "barcode": barcode,
                "batch": batch,
                "expiry": expiry,
                "pack_size": pack_size,
                "retail_price": retail_price,
                "tax_rate": tax_rate,
                "discount_rate": discount_rate,
                "current_qty": current_qty,
                "cost_price": cost_price
            }
            added_count += 1
            
        self.update_cart_display()

    def remove_from_cart(self, event=None):
        selected_items = self.cart_tree.selection()
        if not selected_items:
            return
            
        for sel in selected_items:
            item_values = self.cart_tree.item(sel, "values")
            if not item_values:
                continue
            name = item_values[0]
            if name in self.cart:
                del self.cart[name]
                
        self.update_cart_display()

    def clear_cart(self):
        self.cart.clear()
        self.update_cart_display()

    def update_cart_display(self):
        # Clear existing display
        for row in self.cart_tree.get_children():
            self.cart_tree.delete(row)
            
        # Re-populate cart table
        for name, item in self.cart.items():
            self.cart_tree.insert("", tk.END, values=(
                item["name"],
                item["current_qty"],
                f"Rs {item['retail_price']:.2f}"
            ))
            
        # Update Checkout button text
        self.sell_btn.config(text=f"💳 Checkout Cart ({len(self.cart)})")

    def delete_selected_medicines(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Nothing Selected", "Please select one or more medicines to delete.")
            return

        count = len(selected_items)
        confirm_msg = f"Are you sure you want to delete the selected {count} medicine(s)?\nThis will remove them from inventory."
        if not messagebox.askyesno("Confirm Deletion", confirm_msg):
            return

        for item in selected_items:
            item_values = self.tree.item(item, "values")
            name = item_values[0]
            
            # Delete from SQLite
            self.cursor.execute("DELETE FROM LocalInventoryV2 WHERE brand_name = ?", (name,))
            
            # Instantly delete from Cloud MongoDB database if online (using background thread)
            def run_cloud_delete(m_name=name, p_lic=self.pharmacy_license):
                try:
                    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
                    cloud_db = client['MediLinkDB']
                    cloud_db.Inventory.delete_one({
                        "medicine_name": m_name, 
                        "pharmacy_license": p_lic
                    })
                except Exception as e:
                    print(f"Cloud deletion error for {m_name}: {e}")
            threading.Thread(target=run_cloud_delete, daemon=True).start()

        self.conn.commit()
        self.load_local_inventory()
        messagebox.showinfo("Success", f"Successfully deleted {count} medicine(s) from inventory.")

    def sync_to_cloud(self):
        if not self.pharmacy_license or not self.lat or not self.lng:
            messagebox.showwarning("Config Error", "Please save your Pharmacy License, Latitude, and Longitude first.")
            return

        try:
            self.cursor.execute("""
                SELECT brand_name, generic_formula, price, expiry_date, quantity,
                       manufacturer, category, form, dosage, barcode, batch_number,
                       pack_size, cost_price, retail_price, tax_rate, discount_allowed
                FROM LocalInventoryV2
            """)
            local_items = self.cursor.fetchall()

            self.sync_btn.config(text="Syncing...", state=tk.DISABLED)
            self.root.update()

            client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
            cloud_db = client['MediLinkDB']

            # Reconcile deletions on cloud
            local_names = {item[0] for item in local_items}
            cloud_db.Inventory.delete_many({
                "pharmacy_license": self.pharmacy_license,
                "medicine_name": {"$nin": list(local_names)}
            })

            cloud_db.Pharmacies.update_one(
                {"license_no": self.pharmacy_license},
                {"$set": {
                    "name": self.pharmacy_name,
                    "license_no": self.pharmacy_license,
                    "location": {
                        "type": "Point",
                        "coordinates": [float(self.lng), float(self.lat)]
                    }
                }},
                upsert=True
            )

            synced_count = 0
            for item in local_items:
                (name, formula, price, expiry, qty, manufacturer, category, form,
                 dosage, barcode, batch, pack_size, cost_price, retail_price,
                 tax_rate, discount) = item

                cloud_db.GlobalMedicines.update_one(
                    {"brand_name": name},
                    {"$set": {"brand_name": name, "generic_formula": formula}},
                    upsert=True
                )

                cloud_db.Inventory.update_one(
                    {"medicine_name": name, "pharmacy_license": self.pharmacy_license},
                    {"$set": {
                        "brand_name": name,
                        "medicine_name": name,
                        "generic_formula": formula,
                        "price": price,
                        "expiry_date": expiry,
                        "pharmacy_license": self.pharmacy_license,
                        "quantity": qty,
                        "manufacturer": manufacturer,
                        "category": category,
                        "form": form,
                        "dosage": dosage,
                        "barcode": barcode,
                        "batch_number": batch,
                        "pack_size": pack_size,
                        "cost_price": cost_price,
                        "retail_price": retail_price,
                        "tax_rate": tax_rate,
                        "discount_allowed": discount,
                        "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }},
                    upsert=True
                )
                synced_count += 1
            
            messagebox.showinfo("Sync Success", f"Synced {synced_count} items and updated pharmacy location!")
        except Exception as e:
            messagebox.showerror("Sync Error", f"Failed to sync: {e}")
        finally:
            self.sync_btn.config(text="☁️ Sync to Cloud", state=tk.NORMAL)

    # ==========================================
    # FUZZY MATCH & HIGH-ACCURACY OCR METHODS
    # ==========================================
    def levenshtein_distance(self, s1, s2):
        if len(s1) < len(s2):
            return self.levenshtein_distance(s2, s1)
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
            
        return previous_row[-1]

    def fuzzy_match_brand(self, word):
        word_low = word.lower().strip()
        if not word_low or len(word_low) < 3:
            return None
            
        best_match = None
        min_dist = 999
        
        for brand in self.known_brands.keys():
            dist = self.levenshtein_distance(word_low, brand)
            threshold = 2 if len(brand) > 5 else 1
            if dist <= threshold and dist < min_dist:
                min_dist = dist
                best_match = brand
                
        if best_match:
            if min_dist > 0:
                self.append_log(f"Fuzzy Auto-Corrected: '{word}' -> '{self.known_brands[best_match][0]}' (edit distance: {min_dist})")
            return self.known_brands[best_match]
        return None

    def is_inventory_line(self, line_text):
        line_low = line_text.lower().strip()
        if not line_low:
            return False
            
        # Expanded ignore list to exclude headers, metadata, footers, and invoice details
        ignore_keywords = [
            "total", "subtotal", "tax", "invoice", "receipt", "bill", "cashier",
            "customer", "address", "phone", "mobile", "cash", "change", "net amount", "balance",
            "b.no", "bno", "s.no", "sno", "page", "tel", "fax", "email", "website",
            "lic", "mfg", "client", "buyer", "seller", "patient", "slip", "payment",
            "sign", "signature", "received", "delivered", "terms", "conditions", "warranty", "thank", "visit"
        ]
        
        for kw in ignore_keywords:
            if kw in line_low:
                return False
                
        # Must contain at least one alphabetical word of length 3 or more (candidate brand name)
        words = re.findall(r'\b[a-zA-Z]{3,}\b', line_low)
        if not words:
            return False
            
        # Must contain at least one numeric digit (representing price or quantity)
        if not re.search(r'\d', line_low):
            return False
            
        return True

    def clean_ocr_number(self, num_str):
        num_str = num_str.upper()
        corrections = {
            'O': '0', 'I': '1', 'L': '1', 'S': '5', 'Z': '2'
        }
        cleaned = ""
        for char in num_str:
            if char in corrections:
                cleaned += corrections[char]
            elif char.isdigit() or char == '.':
                cleaned += char
        return cleaned

    def parse_fields_from_text(self, text, base_brand=None, base_formula=None, base_price=None, base_qty=None, base_expiry=None):
        original_text = text.strip()
        text = original_text
        
        # OCR Digit Correction (Replace O/o with 0 in numeric regions)
        text = re.sub(r'(?<=\d)[oO]', '0', text)
        text = re.sub(r'[oO](?=\d)', '0', text)
        text = re.sub(r'\.[oO]{2}', '.00', text)
        text = re.sub(r'\.[oO]', '.0', text)
        text = re.sub(r'[\u0000-\u001f\u007f-\u009f]S', 'Rs', text)
        
        # 1. Parse Expiry Date and strip from text to avoid numeric collision
        expiry = base_expiry or ""
        expiry_match = re.search(r'\b(0[1-9]|1[0-2])[-/.](2[3-9]|3[0-9])\b', text)
        if expiry_match:
            if not expiry:
                expiry = expiry_match.group(0)
            text = text.replace(expiry_match.group(0), " ")
        if not expiry or expiry == "N/A":
            expiry = "12/27"
            
        # 2. Dosage and strip from text to avoid numeric collision
        dosage_match = re.search(r'\b\d+(?:\s*(?:mg|g|ml|mcg|iu|mg/ml|ug))\b', text, re.IGNORECASE)
        dosage = "N/A"
        if dosage_match:
            dosage = dosage_match.group(0)
            text = text.replace(dosage_match.group(0), " ")
        
        # 3. Form and strip from text to avoid numeric collision
        form_match = re.search(r'\b(tab|tabs|cap|caps|syp|syrup|inj|injection|susp|suspension|crm|cream|drp|drops|tablet|capsule)\b', text, re.IGNORECASE)
        form = "Tablet"
        if form_match:
            form = form_match.group(0).title()
            text = text.replace(form_match.group(0), " ")
        if form in ("Tabs", "Tab"):
            form = "Tablet"
        elif form in ("Caps", "Cap"):
            form = "Capsule"
        elif form in ("Syp", "Syrup"):
            form = "Syrup"
        elif form in ("Inj", "Injection"):
            form = "Injection"
            
        # 4. Manufacturer
        mfg_list = ["GSK", "Abbott", "Hilton", "Pfizer", "Getz", "Sami", "Searle", "Ferozsons", "Sanofi", "Novartis", "Bayer", "Wyeth", "Roche", "Martin Dow", "Bosch", "Barrett Hodgson", "Pharmatec", "Zafa"]
        manufacturer = "Unknown"
        for m in mfg_list:
            if re.search(r'\b' + re.escape(m) + r'\b', text, re.IGNORECASE):
                manufacturer = m
                text = re.sub(r'\b' + re.escape(m) + r'\b', ' ', text, flags=re.IGNORECASE)
                break
                
        # 5. Category
        category = "General"
        cat_map = {
            "Analgesic": ["panadol", "paracetamol", "calpol", "disprin", "brufen", "ibuprofen", "aspirin", "ponstan", "mefenamic"],
            "Antibiotic": ["amoxil", "amoxicillin", "augmentin", "cipro", "ciprofloxacin", "novidat", "klacid", "clarithromycin", "flagyl", "metronidazole"],
            "Vitamins": ["surbex", "fefol", "vit", "vitamin", "multivitamin"],
            "Antihistamine": ["zyrtec", "cetirizine", "avil", "pheniramine"],
            "Gastrointestinal": ["risek", "omeprazole", "gaviscon", "glucophage", "metformin"]
        }
        lower_line = original_text.lower()
        for cat, keywords in cat_map.items():
            for kw in keywords:
                if kw in lower_line:
                    category = cat
                    break
                    
        # 6. Barcode and strip from text to avoid numeric collision
        barcode_match = re.search(r'\b\d{12,13}\b', text)
        barcode = "N/A"
        if barcode_match:
            barcode = barcode_match.group(0)
            text = text.replace(barcode_match.group(0), " ")
        
        # 7. Batch Number and strip from text to avoid numeric collision
        batch_match = re.search(r'\b(?:B\.?No|Batch|Lot)[:\s\-#]*([A-Z0-9\-]{3,12})\b', text, re.IGNORECASE)
        batch = "N/A"
        if batch_match:
            batch = batch_match.group(1)
            text = text.replace(batch_match.group(0), " ")
        else:
            fb_match = re.search(r'\b(?:B|L|LOT)\s*[-/]?\s*([0-9A-Z]{3,10})\b', text, re.IGNORECASE)
            if fb_match:
                batch = fb_match.group(1) if len(fb_match.groups()) > 0 else fb_match.group(0)
                text = text.replace(fb_match.group(0), " ")
                
        # 8. Pack Size and strip from text to avoid numeric collision
        pack_match = re.search(r'\b(\d+\s*\'?s|pack\s*of\s*\d+)\b', text, re.IGNORECASE)
        pack_size = "10s"
        if pack_match:
            pack_size = pack_match.group(0)
            text = text.replace(pack_match.group(0), " ")
        
        # 9. Price & Qty Numbers extraction
        cleaned_text = re.sub(r'\b(Rs|RS|PKR|pk|Price|\$)\.?\s*', '', text, flags=re.IGNORECASE)
        
        words = cleaned_text.split()
        raw_nums = []
        for w in words:
            if any(c.isdigit() for c in w):
                cleaned_num = self.clean_ocr_number(w).strip('.')
                if cleaned_num:
                    try:
                        if '.' in cleaned_num:
                            raw_nums.append(float(cleaned_num))
                        else:
                            raw_nums.append(int(cleaned_num))
                    except ValueError:
                        pass
                        
        price = base_price or 0.0
        quantity = base_qty or 0
        
        # Smart mathematical verification: Look for Qty * Price = Total
        matches = []
        if len(raw_nums) >= 3:
            for i in range(len(raw_nums)):
                for j in range(len(raw_nums)):
                    if i == j: continue
                    for k in range(len(raw_nums)):
                        if k == i or k == j: continue
                        q, p, s = raw_nums[i], raw_nums[j], raw_nums[k]
                        if isinstance(q, int) and 1 <= q <= 200 and p > 0:
                            if abs(q * p - s) < 2.0:
                                matches.append((q, p, s))
        if matches:
            matches.sort(key=lambda x: x[2], reverse=True)
            quantity, price, _ = matches[0]
            
        # Fallback if no math validation succeeded
        if price == 0.0 or quantity == 0:
            floats = [n for n in raw_nums if isinstance(n, float) or (isinstance(n, int) and n > 200)]
            ints   = [n for n in raw_nums if isinstance(n, int) and n <= 200]
            
            if price == 0.0:
                if floats:
                    price = float(max(floats))
                elif len(raw_nums) == 1 and raw_nums[0] > 200:
                    price = float(raw_nums[0])
                else:
                    price = 100.0
                    
            if quantity == 0:
                if ints:
                    quantity = int(ints[-1])
                elif len(raw_nums) == 1 and raw_nums[0] <= 200:
                    quantity = int(raw_nums[0])
                else:
                    quantity = 50
                    
        # 10. Cost Price
        cost_price = round(price * 0.85, 2)
        
        # 11. Tax Rate
        tax_match = re.search(r'\b(\d+(?:\.\d+)?)\s*%\s*(?:tax|gst|vat)\b', original_text, re.IGNORECASE)
        tax_rate = 0.0
        if tax_match:
            tax_rate = float(tax_match.group(1))
        else:
            any_pct = re.findall(r'\b(\d+(?:\.\d+)?)\s*%\b', original_text)
            if len(any_pct) >= 1:
                tax_rate = float(any_pct[0])
                
        # 12. Discount Allowed
        disc_match = re.search(r'\b(\d+(?:\.\d+)?)\s*%\s*(?:disc|discount|off)\b', original_text, re.IGNORECASE)
        discount = 0.0
        if disc_match:
            discount = float(disc_match.group(1))
            
        # 13. Brand and formula identification
        brand_name = base_brand or ""
        generic_formula = base_formula or ""
        
        if not brand_name:
            text_only = cleaned_text
            for w in words:
                if any(c.isdigit() for c in w):
                    text_only = text_only.replace(w, " ", 1)
            words_only = [w.strip() for w in re.split(r'[^a-zA-Z/]', text_only) if len(w.strip()) > 1]
            matched = False
            for word in words_only:
                match_res = self.fuzzy_match_brand(word)
                if match_res:
                    brand_name, generic_formula = match_res
                    matched = True
                    break
            if not matched:
                if len(words_only) >= 2:
                    brand_name = words_only[0].title()
                    generic_formula = " ".join(words_only[1:]).title()
                elif len(words_only) == 1:
                    brand_name = words_only[0].title()
                    generic_formula = "Generic Formula"
                else:
                    brand_name = "Scanned Medicine"
                    generic_formula = "Generic Formula"
                    
        return {
            "brand_name": brand_name,
            "generic_formula": generic_formula,
            "manufacturer": manufacturer,
            "category": category,
            "form": form,
            "dosage": dosage,
            "barcode": barcode,
            "batch_number": batch,
            "expiry_date": expiry,
            "pack_size": pack_size,
            "cost_price": cost_price,
            "retail_price": price,
            "tax_rate": tax_rate,
            "discount_allowed": discount,
            "quantity": quantity
        }

    def parse_ocr_line(self, line_text):
        return self.parse_fields_from_text(line_text)

    def run_tesseract_ocr(self, image_path):
        """
        Use Tesseract OCR (via pytesseract.image_to_data) and vertical Y-clustering
        to extract structured medicine data from a pharmacy invoice image.
        Returns list of medicine field dicts.
        """
        tess_cmd = pytesseract.pytesseract.tesseract_cmd
        if not os.path.exists(tess_cmd):
            raise FileNotFoundError(
                f"Tesseract not found at: {tess_cmd}\n"
                "Please install from: https://github.com/UB-Mannheim/tesseract/wiki"
            )

        # Open and preprocess image using cv2
        img_cv = cv2.imread(image_path)
        if img_cv is not None:
            img_h, img_w = img_cv.shape[:2]
            target_h = 1500
            scale = target_h / img_h
            target_w = int(img_w * scale)
            resized = cv2.resize(img_cv, (target_w, target_h), interpolation=cv2.INTER_LANCZOS4)
            gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
            # Denoise using bilateral filter/NLMeans for crisp text edges
            denoised = cv2.fastNlMeansDenoising(gray, h=10, templateWindowSize=7, searchWindowSize=21)
            img = Image.fromarray(denoised)
            img_w, img_h = img.size
        else:
            img = Image.open(image_path).convert("RGB")
            img_w, img_h = img.size
            # Upscale small images for better OCR accuracy
            if img_w < 1200:
                scale = 1200 / img_w
                img = img.resize((int(img_w * scale), int(img_h * scale)), Image.LANCZOS)
                img_w, img_h = img.size

        self.append_log(f"Tesseract scanning {img_w}x{img_h} image using PSM 3 & Y-clustering...")

        data = pytesseract.image_to_data(
            img,
            config="--psm 3",
            output_type=pytesseract.Output.DICT
        )

        n = len(data['text'])
        words = []
        for i in range(n):
            conf = int(data['conf'][i])
            text = str(data['text'][i]).strip()
            if conf < 30 or not text:
                continue
            words.append({
                'text':     text,
                'left':     data['left'][i],
                'top':      data['top'][i],
                'width':    data['width'][i],
                'height':   data['height'][i],
                'xcenter':  data['left'][i] + data['width'][i] / 2,
                'ycenter':  data['top'][i]  + data['height'][i] / 2,
            })

        if not words:
            self.append_log("Tesseract returned no words.")
            return []

        # 1. Y-Clustering vertical line group alignment
        words_sorted = sorted(words, key=lambda w: w['top'])
        clustered_rows = []

        for w in words_sorted:
            y_center = w['ycenter']
            h = w['height']
            tolerance = max(12, h * 0.6)

            placed = False
            for row in clustered_rows:
                avg_y = sum(word['ycenter'] for word in row) / len(row)
                if abs(y_center - avg_y) <= tolerance:
                    row.append(w)
                    placed = True
                    break

            if not placed:
                clustered_rows.append([w])

        # Sort words left-to-right, and sort rows top-to-bottom
        sorted_rows = []
        for row in clustered_rows:
            row_sorted = sorted(row, key=lambda w: w['left'])
            sorted_rows.append(row_sorted)

        sorted_rows = sorted(sorted_rows, key=lambda r: sum(w['ycenter'] for w in r) / len(r))
        self.append_log(f"Aligned words into {len(sorted_rows)} line rows.")

        skip_kw = {
            'total','subtotal','invoice','receipt','bill','cashier','customer',
            'address','phone','mobile','cash','change','balance','page','tel',
            'fax','email','website','signature','received','delivered','thank',
            'visit','tax','due','discount','disc','net','gross','vat','gst',
            'batch','b.no','serial','s.no','mfg','lic','buyer','seller',
            'patient','slip','payment','terms','conditions','warranty',
        }

        items = []
        for row in sorted_rows:
            full_text = ' '.join(w['text'] for w in row)
            full_text_low = full_text.lower().strip()

            if not full_text:
                continue

            if any(k in full_text_low for k in skip_kw):
                continue

            # Check if visual line has a medicine candidate (needs letters) and price (needs digits)
            if not re.search(r'[A-Za-z]{3,}', full_text) or not re.search(r'\d', full_text):
                continue

            parsed = self.parse_fields_from_text(full_text)

            # Override brand name if row contains a known catalog brand name
            fuzzy_brand = parsed["brand_name"]
            for w in row:
                match = self.fuzzy_match_brand(w['text'])
                if match:
                    fuzzy_brand, parsed["generic_formula"] = match
                    break

            parsed["brand_name"] = fuzzy_brand

            if parsed["brand_name"] == "Scanned Medicine" and parsed["retail_price"] == 100.0:
                continue

            items.append(parsed)
            self.append_log(
                f"  ✔ {parsed['brand_name']} | Rs {parsed['retail_price']} | Qty {parsed['quantity']} | Exp {parsed['expiry_date']}")

        return items


    def select_and_scan_invoice(self):
        file_path = filedialog.askopenfilename(
            title="Select Invoice Image",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.webp *.bmp"), ("All Files", "*.*")]
        )
        if not file_path:
            return

        try:
            img = Image.open(file_path)
            img.thumbnail((260, 200))
            self.invoice_photo = ImageTk.PhotoImage(img)
            self.image_label.config(image=self.invoice_photo, text="")
            
            for row in self.ocr_tree.get_children():
                self.ocr_tree.delete(row)
                
            self.scan_btn.config(state=tk.DISABLED)
            self.ocr_save_btn.config(state=tk.DISABLED)
            self.ocr_progress['value'] = 0
            
            self.append_log(f"Loading invoice: {os.path.basename(file_path)}...")
            self.run_simulated_ocr_stages(file_path)
            
        except Exception as e:
            messagebox.showerror("Image Error", f"Failed to load image: {e}")
            self.scan_btn.config(state=tk.NORMAL)
            self.ocr_save_btn.config(state=tk.NORMAL)

    def _ui(self, fn):
        """Helper: safely schedule a callable on the main Tkinter thread."""
        self.root.after(0, fn)

    def run_simulated_ocr_stages(self, file_path):
        """Kick off the AI OCR pipeline on a background thread so the UI stays live."""
        def worker():
            try:
                self.populate_extracted_data(file_path)
            except Exception as e:
                self._ui(lambda: messagebox.showerror("OCR Error", str(e)))
            finally:
                self._ui(lambda: self.scan_btn.config(state=tk.NORMAL))
                self._ui(lambda: self.ocr_save_btn.config(state=tk.NORMAL))

        t = threading.Thread(target=worker, daemon=True)
        t.start()

    def populate_extracted_data(self, file_path):
        """
        Full AI+OCR pipeline — runs on a background thread.
        If Gemini API Key is provided:
          - Use Gemini Multimodal AI OCR (highly accurate)
        Otherwise (fallback):
          - Stage 1: EasyOCR (Tesseract)
          - Stage 2: WinOCR + smart parsing
          - Stage 3: Fuzzy brand scan
        """
        def update_progress(msg, val):
            self._ui(lambda m=msg, v=val: [
                self.progress_label.config(text=f"Status: {m}"),
                self.ocr_progress.config(value=v),
                self.append_log(m)
            ])

        try:
            items = []
            use_gemini = bool(getattr(self, "gemini_key", "").strip()) or bool(os.environ.get("GEMINI_API_KEY", "").strip()) or bool(os.environ.get("GOOGLE_API_KEY", "").strip())
            
            if use_gemini:
                update_progress("🧠 Running Gemini Multimodal AI OCR...", 20)
                try:
                    self.append_log("Starting Gemini API multimodal scan...")
                    items = self.run_gemini_ai_ocr(file_path)
                    self.append_log(f"✅ Gemini AI extracted {len(items)} item(s).")
                    update_progress(f"✅ Gemini found {len(items)} items!", 80)
                except Exception as e_gem:
                    self.append_log(f"⚠️ Gemini API failed: {e_gem}")
                    self.append_log("Falling back to local Tesseract OCR engine...")
                    use_gemini = False

            if not use_gemini:
                # Open and preprocess image using cv2
                img_cv = cv2.imread(file_path)
                if img_cv is not None:
                    h, w = img_cv.shape[:2]
                    target_h = 1500
                    scale = target_h / h
                    target_w = int(w * scale)
                    resized = cv2.resize(img_cv, (target_w, target_h), interpolation=cv2.INTER_LANCZOS4)
                    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
                    denoised = cv2.fastNlMeansDenoising(gray, h=10, templateWindowSize=7, searchWindowSize=21)
                    img_pil = Image.fromarray(denoised)
                else:
                    img_pil = Image.open(file_path)
                    img_pil.thumbnail((2000, 2000))

                # -------- STAGE 1: Windows OCR with Y-Clustering --------
                update_progress("🔍 Step 1/3 — Running Windows OCR (WinOCR) engine...", 10)
                try:
                    self.append_log("🔍 Starting Windows OCR scan...")
                    res = winocr.recognize_pil_sync(img_pil, lang="en-US")
                    raw_text = res.get('text', '').strip()
                    lines = res.get('lines', [])
                    self.append_log(f"WinOCR extracted {len(raw_text)} characters.")
                    
                    win_words = []
                    for line in lines:
                        for w_obj in line.get('words', []):
                            rect = w_obj.get('bounding_rect', {})
                            w_text = w_obj.get('text', '').strip()
                            if w_text:
                                win_words.append({
                                    'text': w_text,
                                    'left': rect.get('x', 0),
                                    'top': rect.get('y', 0),
                                    'width': rect.get('width', 0),
                                    'height': rect.get('height', 0),
                                    'xcenter': rect.get('x', 0) + rect.get('width', 0) / 2,
                                    'ycenter': rect.get('y', 0) + rect.get('height', 0) / 2
                                })
                    
                    if win_words:
                        words_sorted = sorted(win_words, key=lambda w: w['top'])
                        clustered_rows = []
                        for w in words_sorted:
                            y_center = w['ycenter']
                            h_val = w['height']
                            tolerance = max(12, h_val * 0.6)
                            placed = False
                            for row in clustered_rows:
                                avg_y = sum(word['ycenter'] for word in row) / len(row)
                                if abs(y_center - avg_y) <= tolerance:
                                    row.append(w)
                                    placed = True
                                    break
                            if not placed:
                                clustered_rows.append([w])
                                
                        sorted_rows = []
                        for row in clustered_rows:
                            row_sorted = sorted(row, key=lambda w: w['left'])
                            sorted_rows.append(row_sorted)
                        sorted_rows = sorted(sorted_rows, key=lambda r: sum(w['ycenter'] for w in r) / len(r))
                        
                        self.append_log(f"Aligned WinOCR words into {len(sorted_rows)} line rows.")
                        
                        skip_kw = {
                            'total','subtotal','invoice','receipt','bill','cashier','customer',
                            'address','phone','mobile','cash','change','balance','page','tel',
                            'fax','email','website','signature','received','delivered','thank',
                            'visit','tax','due','discount','disc','net','gross','vat','gst',
                            'batch','b.no','serial','s.no','mfg','lic','buyer','seller',
                            'patient','slip','payment','terms','conditions','warranty',
                        }
                        
                        for row in sorted_rows:
                            full_text = ' '.join(word['text'] for word in row)
                            full_text_low = full_text.lower().strip()
                            if not full_text or any(k in full_text_low for k in skip_kw):
                                continue
                            if not re.search(r'[A-Za-z]{3,}', full_text) or not re.search(r'\d', full_text):
                                continue
                                
                            parsed = self.parse_ocr_line(full_text)
                            fuzzy_brand = parsed["brand_name"]
                            for word in row:
                                match = self.fuzzy_match_brand(word['text'])
                                if match:
                                    fuzzy_brand, parsed["generic_formula"] = match
                                    break
                            parsed["brand_name"] = fuzzy_brand
                            if parsed["brand_name"] == "Scanned Medicine" and parsed["retail_price"] == 100.0:
                                continue
                                
                            items.append(parsed)
                            self.append_log(
                                f"  ✔ {parsed['brand_name']} | Rs {parsed['retail_price']} | Qty {parsed['quantity']} | Exp {parsed['expiry_date']}")
                    
                    if items:
                        update_progress(f"✅ Windows OCR found {len(items)} items!", 80)
                except Exception as e_win:
                    self.append_log(f"⚠️ Windows OCR scan failed: {e_win}")

                # -------- STAGE 2: Tesseract OCR Fallback --------
                if not items:
                    update_progress("🔍 Step 2/3 — Running Tesseract OCR engine...", 40)
                    try:
                        self.append_log("🔍 Starting Tesseract OCR scan...")
                        items = self.run_tesseract_ocr(file_path)
                        self.append_log(f"✅ Tesseract extracted {len(items)} item(s).")
                        update_progress(f"✅ Tesseract found {len(items)} items!", 80)
                    except Exception as e_tess:
                        self.append_log(f"⚠️ Tesseract failed: {e_tess}")

                # -------- STAGE 3: Fuzzy Word Scan Fallback --------
                if not items:
                    update_progress("🔍 Step 3/3 — Running fallback fuzzy word scan...", 60)
                    try:
                        raw_text = ""
                        try:
                            res = winocr.recognize_pil_sync(img_pil, lang="en-US")
                            raw_text = res.get('text', '').strip()
                        except:
                            pass
                        if not raw_text:
                            try:
                                raw_text = pytesseract.image_to_string(img_pil).strip()
                            except:
                                pass
                        
                        if raw_text:
                            words = re.findall(r'\b[a-zA-Z]+\b', raw_text)
                            seen = set()
                            for w in words:
                                wl = w.lower()
                                if wl in self.known_brands and wl not in seen:
                                    bn, gf = self.known_brands[wl]
                                    items.append({
                                        "brand_name": bn,
                                        "generic_formula": gf,
                                        "manufacturer": "Unknown",
                                        "category": "General",
                                        "form": "Tablet",
                                        "dosage": "N/A",
                                        "barcode": "N/A",
                                        "batch_number": "N/A",
                                        "expiry_date": "12/27",
                                        "pack_size": "10s",
                                        "cost_price": 85.0,
                                        "retail_price": 100.0,
                                        "tax_rate": 0.0,
                                        "discount_allowed": 0.0,
                                        "quantity": 10
                                    })
                                    seen.add(wl)
                            if items:
                                update_progress(f"✅ Fuzzy scan extracted {len(items)} items!", 80)
                    except Exception as e_fuzzy:
                        self.append_log(f"⚠️ Fuzzy scan fallback failed: {e_fuzzy}")

            # -------- Populate table on main thread --------
            update_progress("Populating results table...", 90)

            def fill_table():
                for row in self.ocr_tree.get_children():
                    self.ocr_tree.delete(row)

                populated = 0
                for item in items:
                    b_name = str(item.get("brand_name") or "").strip()
                    g_form = str(item.get("generic_formula") or "N/A").strip()
                    if not b_name or b_name.lower() in ("n/a", "none"):
                        continue
                    try:
                        price = float(
                            str(item.get("retail_price", 0))
                            .replace(",","").replace("Rs","").replace("PKR","").strip())
                    except (ValueError, TypeError):
                        price = 0.0
                    expiry = str(item.get("expiry_date") or "N/A").strip()
                    try:
                        qty = max(1, int(float(str(item.get("quantity", 1)).strip())))
                    except (ValueError, TypeError):
                        qty = 1

                    cost_val = f"Rs {item.get('cost_price', price * 0.85):.2f}"
                    retail_val = f"Rs {price:.2f}"
                    tax_val = f"{item.get('tax_rate', 0.0)}%"
                    disc_val = f"{item.get('discount_allowed', 0.0)}%"

                    self.ocr_tree.insert("", tk.END, values=(
                        b_name, g_form, item.get("manufacturer", "Unknown"), item.get("category", "General"),
                        item.get("form", "Tablet"), item.get("dosage", "N/A"), item.get("barcode", "N/A"),
                        item.get("batch_number", "N/A"), expiry, item.get("pack_size", "10s"),
                        cost_val, retail_val, tax_val, disc_val, qty
                    ))
                    populated += 1

                self.progress_label.config(text="Status: ✅ AI Scan Complete!")
                self.ocr_progress.config(value=100)

                if populated:
                    self.append_log(f"🎉 {populated} medicines extracted. Review and upload!")
                    messagebox.showinfo(
                        "AI OCR Complete 🎉",
                        f"✅ Extracted {populated} medicine(s)!\n\n"
                        "💡 Double-click any row to edit before uploading."
                    )
                else:
                    self.append_log("⚠️ No medicines extracted.")
                    messagebox.showwarning(
                        "No Data Found",
                        "Could not extract any medicine rows.\n\n"
                        "Tips:\n"
                        "• Use a clear, well-lit photo of the invoice\n"
                        "• Make sure text is not blurry\n"
                        "• You can add medicines manually in the Inventory tab."
                    )

            self._ui(fill_table)

        except Exception as e:
            self.append_log(f"❌ Error: {e}")
            self._ui(lambda: messagebox.showerror("Processing Error", f"Failed:\n{e}"))

    def run_gemini_ai_ocr(self, image_path):
        import base64
        import urllib.request
        import urllib.error
        import json
        
        # Read and encode image
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            
        # Determine mime type
        ext = os.path.splitext(image_path)[1].lower()
        mime_type = "image/jpeg"
        if ext == ".png":
            mime_type = "image/png"
        elif ext == ".webp":
            mime_type = "image/webp"
            
        prompt = (
            "Analyze this invoice image and extract all medicine line items. "
            "Return a valid JSON array of objects. Each object must contain these exact keys: "
            "brand_name, generic_formula, manufacturer, category, form, dosage, barcode, "
            "batch_number, expiry_date, pack_size, cost_price, retail_price, tax_rate, "
            "discount_allowed, quantity. "
            "Rules:\n"
            "- Extract clean strings. Brand name must not contain dosage or form.\n"
            "- Retail price and cost price must be numbers (floats). If cost_price is missing, default to 85% of retail_price.\n"
            "- Expiry date must be in MM/YY format.\n"
            "- Tax rate and discount allowed must be percentage float values (e.g. 10.0 or 0.0).\n"
            "- If any field is not visible, use a reasonable guess or default (e.g. category: 'General', manufacturer: 'Unknown', barcode: 'N/A', batch_number: 'N/A', pack_size: '10s').\n"
            "Return ONLY the raw JSON array of objects, with no markdown code blocks or wrapper text."
        )
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt},
                        {
                            "inlineData": {
                                "mimeType": mime_type,
                                "data": encoded_string
                            }
                        }
                    ]
                }
            ],
            "generationConfig": {
                "responseMimeType": "application/json"
            }
        }
        
        api_key = self.gemini_key.strip() or os.environ.get("GEMINI_API_KEY", "").strip() or os.environ.get("GOOGLE_API_KEY", "").strip()
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        data_bytes = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            url,
            data=data_bytes,
            headers={'Content-Type': 'application/json'}
        )
        
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                res_body = response.read().decode('utf-8')
                res_json = json.loads(res_body)
                
                text_content = res_json["candidates"][0]["content"]["parts"][0]["text"].strip()
                # Clean up markdown if Gemini returned it despite instructions
                if text_content.startswith("```"):
                    lines = text_content.split("\n")
                    if lines[0].startswith("```"):
                        lines = lines[1:]
                    if lines and lines[-1].strip() == "```":
                        lines = lines[:-1]
                    text_content = "\n".join(lines).strip()
                    
                items = json.loads(text_content)
                if not isinstance(items, list):
                    if isinstance(items, dict) and "items" in items:
                        items = items["items"]
                    else:
                        raise ValueError("Gemini response is not a list of items")
                        
                # Perform post-processing normalization
                normalized_items = []
                for item in items:
                    b_name = str(item.get("brand_name") or "").strip().title()
                    if not b_name:
                        continue
                    
                    try:
                        price = float(str(item.get("retail_price", 100.0)).replace(",","").replace("Rs","").strip())
                    except:
                        price = 100.0
                        
                    try:
                        cost = float(str(item.get("cost_price", price * 0.85)).replace(",","").replace("Rs","").strip())
                    except:
                        cost = round(price * 0.85, 2)
                        
                    try:
                        tax = float(str(item.get("tax_rate", 0.0)).replace("%","").strip())
                    except:
                        tax = 0.0
                        
                    try:
                        disc = float(str(item.get("discount_allowed", 0.0)).replace("%","").strip())
                    except:
                        disc = 0.0
                        
                    try:
                        qty = max(1, int(float(str(item.get("quantity", 10)).strip())))
                    except:
                        qty = 10
                        
                    normalized_items.append({
                        "brand_name": b_name,
                        "generic_formula": str(item.get("generic_formula") or "N/A").strip().title(),
                        "manufacturer": str(item.get("manufacturer") or "Unknown").strip().title(),
                        "category": str(item.get("category") or "General").strip().title(),
                        "form": str(item.get("form") or "Tablet").strip().title(),
                        "dosage": str(item.get("dosage") or "N/A").strip(),
                        "barcode": str(item.get("barcode") or "N/A").strip(),
                        "batch_number": str(item.get("batch_number") or "N/A").strip(),
                        "expiry_date": str(item.get("expiry_date") or "12/27").strip(),
                        "pack_size": str(item.get("pack_size") or "10s").strip(),
                        "cost_price": cost,
                        "retail_price": price,
                        "tax_rate": tax,
                        "discount_allowed": disc,
                        "quantity": qty
                    })
                return normalized_items
                
        except urllib.error.HTTPError as he:
            err_msg = he.read().decode('utf-8')
            raise RuntimeError(f"Gemini API HTTP Error: {he.code} - {err_msg}")
        except Exception as e:
            raise RuntimeError(f"Gemini parsing error: {e}")

    def edit_ocr_row(self, event):
        selected_item = self.ocr_tree.selection()
        if not selected_item:
            return
            
        item_values = self.ocr_tree.item(selected_item[0], "values")
        
        edit_win = tk.Toplevel(self.root)
        edit_win.title("Review & Edit Medicine Details")
        edit_win.geometry("520x650")
        edit_win.resizable(False, False)
        edit_win.configure(bg="#fcfcfc")
        
        edit_win.transient(self.root)
        edit_win.grab_set()
        
        tk.Label(edit_win, text="✏️ Edit Scanned Record", font=("Segoe UI", 12, "bold"), bg="#fcfcfc", fg="#0d47a1").pack(pady=10)
        
        form_frame = tk.Frame(edit_win, bg="#fcfcfc", padx=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Grid config
        form_frame.columnconfigure(1, weight=1)
        form_frame.columnconfigure(3, weight=1)
        
        def add_form_field(label_text, row, col_start, val):
            lbl = tk.Label(form_frame, text=label_text, font=("Segoe UI", 9, "bold"), bg="#fcfcfc")
            lbl.grid(row=row, column=col_start, sticky=tk.W, pady=6, padx=(5, 2))
            ent = tk.Entry(form_frame, font=("Segoe UI", 10), width=18, highlightthickness=1, highlightbackground="#cbd5e1", highlightcolor="#0d47a1", bd=0, relief=tk.FLAT)
            ent.grid(row=row, column=col_start+1, pady=6, padx=(2, 5), sticky=tk.EW)
            ent.insert(0, val)
            return ent
            
        # Row 0:
        name_ent = add_form_field("Medicine Name:", 0, 0, item_values[0])
        formula_ent = add_form_field("Generic Name:", 0, 2, item_values[1])
        
        # Row 1:
        mfg_ent = add_form_field("Manufacturer:", 1, 0, item_values[2])
        cat_ent = add_form_field("Category:", 1, 2, item_values[3])
        
        # Row 2:
        form_ent = add_form_field("Form (e.g. Tab):", 2, 0, item_values[4])
        dosage_ent = add_form_field("Dosage (500mg):", 2, 2, item_values[5])
        
        # Row 3:
        barcode_ent = add_form_field("Barcode:", 3, 0, item_values[6])
        batch_ent = add_form_field("Batch Number:", 3, 2, item_values[7])
        
        # Row 4:
        expiry_ent = add_form_field("Expiry (MM/YY):", 4, 0, item_values[8])
        pack_ent = add_form_field("Pack Size:", 4, 2, item_values[9])
        
        # Row 5:
        cost_ent = add_form_field("Cost Price:", 5, 0, item_values[10].replace("Rs ", ""))
        retail_ent = add_form_field("Retail Price:", 5, 2, item_values[11].replace("Rs ", ""))
        
        # Row 6:
        tax_ent = add_form_field("Tax Rate (%):", 6, 0, item_values[12].replace("%", ""))
        disc_ent = add_form_field("Discount (%):", 6, 2, item_values[13].replace("%", ""))
        
        # Row 7:
        qty_ent = add_form_field("Quantity:", 7, 0, item_values[14])
        
        def save_changes():
            name = name_ent.get().strip()
            formula = formula_ent.get().strip()
            mfg = mfg_ent.get().strip()
            cat = cat_ent.get().strip()
            form_val = form_ent.get().strip()
            dosage = dosage_ent.get().strip()
            barcode = barcode_ent.get().strip()
            batch = batch_ent.get().strip()
            expiry = expiry_ent.get().strip()
            pack = pack_ent.get().strip()
            cost_str = cost_ent.get().strip()
            retail_str = retail_ent.get().strip()
            tax_str = tax_ent.get().strip()
            disc_str = disc_ent.get().strip()
            qty_str = qty_ent.get().strip()
            
            if not name:
                messagebox.showwarning("Input Error", "Medicine name cannot be empty.", parent=edit_win)
                return
                
            try:
                cost = float(cost_str) if cost_str else 0.0
                retail = float(retail_str) if retail_str else 0.0
                tax = float(tax_str) if tax_str else 0.0
                disc = float(disc_str) if disc_str else 0.0
                qty = int(qty_str) if qty_str else 1
            except ValueError:
                messagebox.showwarning("Input Error", "Price, Tax, Discount, and Qty must be numbers.", parent=edit_win)
                return
                
            cost_val = f"Rs {cost:.2f}"
            retail_val = f"Rs {retail:.2f}"
            tax_val = f"{tax}%"
            disc_val = f"{disc}%"
            
            self.ocr_tree.item(selected_item[0], values=(
                name, formula, mfg, cat, form_val, dosage, barcode, batch, expiry, pack,
                cost_val, retail_val, tax_val, disc_val, qty
            ))
            self.append_log(f"Updated item: {name}")
            edit_win.destroy()
            
        tk.Button(edit_win, text="✔️ Save Changes", bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), pady=6, command=save_changes).pack(pady=15)

    def save_bulk_ocr_data(self):
        items = []
        for child in self.ocr_tree.get_children():
            values = self.ocr_tree.item(child, "values")
            items.append({
                "brand_name": values[0],
                "generic_formula": values[1],
                "manufacturer": values[2],
                "category": values[3],
                "form": values[4],
                "dosage": values[5],
                "barcode": values[6],
                "batch_number": values[7],
                "expiry_date": values[8],
                "pack_size": values[9],
                "cost_price": float(values[10].replace("Rs ", "")),
                "retail_price": float(values[11].replace("Rs ", "")),
                "tax_rate": float(values[12].replace("%", "")),
                "discount_allowed": float(values[13].replace("%", "")),
                "quantity": int(values[14])
            })
            
        if not items:
            messagebox.showwarning("No Data", "No items to save. Please scan an invoice first.")
            return
            
        if not self.pharmacy_license or not self.lat or not self.lng:
            messagebox.showwarning("Config Error", "Please save your Pharmacy License, Latitude, and Longitude first.")
            return

        try:
            self.append_log("Saving bulk data to local SQLite database...")
            for item in items:
                self.cursor.execute("""
                    INSERT OR REPLACE INTO LocalInventoryV2 (
                        brand_name, generic_formula, price, expiry_date, quantity,
                        manufacturer, category, form, dosage, barcode, batch_number,
                        pack_size, cost_price, retail_price, tax_rate, discount_allowed
                    ) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    item["brand_name"], item["generic_formula"], item["retail_price"], item["expiry_date"], item["quantity"],
                    item["manufacturer"], item["category"], item["form"], item["dosage"], item["barcode"], item["batch_number"],
                    item["pack_size"], item["cost_price"], item["retail_price"], item["tax_rate"], item["discount_allowed"]
                ))
            self.conn.commit()
            
            self.append_log("Local SQLite database updated successfully.")
            
            self.progress_label.config(text="Status: Syncing bulk data to cloud...")
            self.ocr_progress['value'] = 40
            self.root.update()
            
            self.append_log("Connecting to MongoDB cloud cluster...")
            client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
            cloud_db = client['MediLinkDB']
            
            cloud_db.Pharmacies.update_one(
                {"license_no": self.pharmacy_license},
                {"$set": {
                    "name": self.pharmacy_name,
                    "license_no": self.pharmacy_license,
                    "location": {
                        "type": "Point",
                        "coordinates": [float(self.lng), float(self.lat)]
                    }
                }},
                upsert=True
            )
            
            self.ocr_progress['value'] = 70
            self.root.update()
            self.append_log("Uploading items to Global Catalog and Branch Inventory...")
            
            for item in items:
                cloud_db.GlobalMedicines.update_one(
                    {"brand_name": item["brand_name"]},
                    {"$set": {"brand_name": item["brand_name"], "generic_formula": item["generic_formula"]}},
                    upsert=True
                )
                
                cloud_db.Inventory.update_one(
                    {"medicine_name": item["brand_name"], "pharmacy_license": self.pharmacy_license},
                    {"$set": {
                        "brand_name": item["brand_name"],
                        "medicine_name": item["brand_name"],
                        "generic_formula": item["generic_formula"],
                        "price": item["retail_price"],
                        "expiry_date": item["expiry_date"],
                        "pharmacy_license": self.pharmacy_license,
                        "quantity": item["quantity"],
                        "manufacturer": item["manufacturer"],
                        "category": item["category"],
                        "form": item["form"],
                        "dosage": item["dosage"],
                        "barcode": item["barcode"],
                        "batch_number": item["batch_number"],
                        "pack_size": item["pack_size"],
                        "cost_price": item["cost_price"],
                        "retail_price": item["retail_price"],
                        "tax_rate": item["tax_rate"],
                        "discount_allowed": item["discount_allowed"],
                        "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }},
                    upsert=True
                )
                
            self.ocr_progress['value'] = 100
            self.progress_label.config(text="Status: Bulk Upload Successful")
            self.append_log(f"Bulk sync complete. Synced {len(items)} items.")
            
            self.load_local_inventory()
            self.load_db_brands()
            self.clear_ocr_data()
            
            messagebox.showinfo("Bulk Sync Success", f"Successfully saved {len(items)} medicines to SQLite & uploaded in bulk to cloud!")
            
        except Exception as e:
            self.progress_label.config(text="Status: Sync failed")
            self.ocr_progress['value'] = 0
            self.append_log(f"Error during bulk sync: {e}")
            messagebox.showerror("Bulk Sync Error", f"Failed to upload data in bulk: {e}")

    def append_log(self, text):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {text}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def clear_ocr_data(self):
        for row in self.ocr_tree.get_children():
            self.ocr_tree.delete(row)
        self.invoice_photo = None
        self.image_label.config(image="", text="No invoice selected\n(Click button above to browse)")
        self.progress_label.config(text="Status: Idle")
        self.ocr_progress['value'] = 0
        self.ocr_save_btn.config(state=tk.DISABLED)
        self.append_log("Cleared scan workbench.")

    def delete_selected_ocr_rows(self):
        selected = self.ocr_tree.selection()
        if not selected:
            messagebox.showwarning("Nothing Selected",
                "کوئی row select نہیں ہے!\n\n"
                "Ctrl+Click یا Shift+Click سے rows select کریں پھر Delete دبائیں۔")
            return

        count = len(selected)
        for item in selected:
            self.ocr_tree.delete(item)

        self.append_log(f"🗑️ {count} row(s) deleted by user.")

        # Disable save button if table is now empty
        if not self.ocr_tree.get_children():
            self.ocr_save_btn.config(state=tk.DISABLED)
            self.append_log("Table is now empty.")

if __name__ == "__main__":
    root = tk.Tk()
    app = PharmacyApp(root)
    root.mainloop()
