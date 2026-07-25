import tkinter as tk
import os
import threading
import datetime

from core import settings
from core.database import DatabaseManager
from core.cloud_sync import CloudSyncManager
from core.ocr_manager import OcrEngine
from components.login_screen import LoginFrame
from components.main_window import MainWindow

class PharmacyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MediLink - Pharmacy Desktop App (Pro)")
        self.root.geometry("1000x780")
        
        self._load_app_icon()
        
        self.cart = {}
        self.known_brands = {}
        
        self.pharmacy_name, self.pharmacy_license, self.lat, self.lng, self.gemini_key = settings.load_config()
        
        self.db_manager = DatabaseManager()
        self.cloud_manager = CloudSyncManager(settings.MONGO_URI)
        self.ocr_engine = OcrEngine()
        
        self._initialize_brand_catalog()
        
        self.show_signin_screen()

    def _load_app_icon(self):
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

    def _initialize_brand_catalog(self):
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

    def show_signin_screen(self):
        self.root.geometry("480x640")
        self.root.configure(bg="#f8fafc")
        self.root.resizable(False, False)
        self.root.title("MediLink - POS Portal Login")
        
        self.login_frame = LoginFrame(self.root, self)
        self.login_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=30)

    def handle_signin(self, name, license_key, lat, lng, error_lbl):
        if not name or not license_key or not lat or not lng:
            error_lbl.config(text="⚠️ Please fill in all four fields.")
            return

        try:
            float(lat)
            float(lng)
        except ValueError:
            error_lbl.config(text="⚠️ Latitude and Longitude must be valid numbers.")
            return

        self.pharmacy_name = name
        self.pharmacy_license = license_key
        self.lat = lat
        self.lng = lng
        settings.save_config(name, license_key, lat, lng, self.gemini_key)
        
        try:
            self.db_name = self.db_manager.initialize_db(license_key)
            self.cloud_manager.pull_cloud_to_local(self.db_manager, license_key)
            self.db_manager.load_db_brands(self.known_brands)
            
            self.login_frame.destroy()
            self.root.geometry("1000x780")
            self.root.resizable(True, True)
            self.root.title("MediLink - Pharmacy Desktop App (Pro)")
            
            self.main_window = MainWindow(self.root, self)
            self.main_window.pack(fill=tk.BOTH, expand=True)
            
            self.main_window.inventory_tab.load_local_inventory()
            
            self.root.after(5000, self.auto_sync_check)
            
        except Exception as e:
            error_lbl.config(text=f"⚠️ Initialization Error: {e}")

    def run_auto_sync(self):
        if not self.pharmacy_license or not self.lat or not self.lng:
            return

        try:
            synced_count = self.cloud_manager.sync_local_to_cloud(
                self.db_name, self.pharmacy_name, self.pharmacy_license, self.lat, self.lng
            )
            settings.save_last_sync_time()
            self._ui(lambda: self.main_window.ocr_tab.append_log(f"Auto-sync successful: Synced {synced_count} items to cloud."))
        except Exception as e:
            self._ui(lambda: self.main_window.ocr_tab.append_log(f"Auto-sync failed: {e}"))

    def auto_sync_check(self):
        last_sync = settings.get_last_sync_time()
        should_sync = False
        if not last_sync:
            should_sync = True
        else:
            try:
                last_dt = datetime.datetime.strptime(last_sync, "%Y-%m-%d %H:%M:%S")
                elapsed = datetime.datetime.now() - last_dt
                if elapsed.total_seconds() >= 12 * 3600:
                    should_sync = True
            except Exception:
                should_sync = True

        if should_sync:
            threading.Thread(target=self.run_auto_sync, daemon=True).start()

        self.root.after(600000, self.auto_sync_check)

    def _ui(self, fn):
        self.root.after(0, fn)

if __name__ == "__main__":
    root = tk.Tk()
    app = PharmacyApp(root)
    root.mainloop()
