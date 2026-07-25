import tkinter as tk
from tkinter import messagebox, filedialog
import os
import re
import cv2
import winocr
import pytesseract
import threading
from PIL import Image, ImageTk
from components.ocr_sidebar import OcrSidebar
from components.ocr_table import OcrTable
from components.ocr_edit_dialog import OcrEditDialog

class OcrTab(tk.Frame):
    def __init__(self, parent, controller, main_view):
        super().__init__(parent, bg=main_view.bg_color)
        self.controller = controller
        self.main_view = main_view
        self.invoice_photo = None
        self.setup_ui()

    def setup_ui(self):
        ocr_split_frame = tk.Frame(self, bg=self.main_view.bg_color)
        ocr_split_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.sidebar = OcrSidebar(ocr_split_frame, self.controller, self.main_view, 
                                  self.select_and_scan_invoice, self.save_gemini_key_from_ui)
        self.sidebar.pack(side=tk.LEFT, fill=tk.BOTH, padx=5, pady=5)

        self.table = OcrTable(ocr_split_frame, self.controller, self.main_view, 
                              self.edit_ocr_row, self.delete_selected_ocr_rows, 
                              self.save_bulk_ocr_data, self.clear_ocr_data)
        self.table.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

    def save_gemini_key_from_ui(self):
        key = self.sidebar.get_gemini_key()
        self.controller.gemini_key = key
        try:
            from core import settings
            settings.save_config(self.controller.pharmacy_name, self.controller.pharmacy_license, 
                               self.controller.lat, self.controller.lng, key)
            self.append_log(f"🔑 Gemini Key updated. AI OCR: {'Enabled' if key else 'Disabled (Local OCR fallback)'}")
            messagebox.showinfo("Gemini Key", "Gemini API key saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save Gemini Key: {e}")

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
            self.sidebar.set_preview_image(self.invoice_photo)
            
            self.table.clear_grid()
            self.sidebar.set_button_state(tk.DISABLED)
            self.table.set_save_button_state(tk.DISABLED)
            self.sidebar.update_progress("Idle", 0)
            
            self.append_log(f"Loading invoice: {os.path.basename(file_path)}...")
            self.run_simulated_ocr_stages(file_path)
            
        except Exception as e:
            messagebox.showerror("Image Error", f"Failed to load image: {e}")
            self.sidebar.set_button_state(tk.NORMAL)
            self.table.set_save_button_state(tk.NORMAL)

    def _ui(self, fn):
        self.controller._ui(fn)

    def run_simulated_ocr_stages(self, file_path):
        def worker():
            try:
                self.populate_extracted_data(file_path)
            except Exception as e:
                self._ui(lambda: messagebox.showerror("OCR Error", str(e)))
            finally:
                self._ui(lambda: self.sidebar.set_button_state(tk.NORMAL))
                self._ui(lambda: self.table.set_save_button_state(tk.NORMAL))

        threading.Thread(target=worker, daemon=True).start()

    def populate_extracted_data(self, file_path):
        def update_progress(msg, val):
            self._ui(lambda: [
                self.sidebar.update_progress(msg, val),
                self.append_log(msg)
            ])

        try:
            items = []
            use_gemini = bool(self.controller.gemini_key.strip()) or bool(os.environ.get("GEMINI_API_KEY", "").strip()) or bool(os.environ.get("GOOGLE_API_KEY", "").strip())
            
            if use_gemini:
                update_progress("🧠 Running Gemini Multimodal AI OCR...", 20)
                try:
                    self.append_log("Starting Gemini API multimodal scan...")
                    items = self.controller.ocr_engine.run_gemini_ai_ocr(file_path, self.controller.gemini_key)
                    self.append_log(f"✅ Gemini AI extracted {len(items)} item(s).")
                    update_progress(f"✅ Gemini found {len(items)} items!", 80)
                except Exception as e_gem:
                    self.append_log(f"⚠️ Gemini API failed: {e_gem}")
                    self.append_log("Falling back to local Tesseract OCR engine...")
                    use_gemini = False

            if not use_gemini:
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
                                
                            parsed = self.controller.ocr_engine.parse_fields_from_text(full_text, self.controller.known_brands, self.append_log)
                            fuzzy_brand = parsed["brand_name"]
                            for word in row:
                                match = self.controller.ocr_engine.fuzzy_match_brand(word['text'], self.controller.known_brands, self.append_log)
                                if match:
                                    fuzzy_brand, parsed["generic_formula"] = match
                                    break
                            parsed["brand_name"] = fuzzy_brand
                            if parsed["brand_name"] == "Scanned Medicine" and parsed["retail_price"] == 100.0:
                                continue
                                
                            items.append(parsed)
                            self.append_log(f"  ✔ {parsed['brand_name']} | Rs {parsed['retail_price']} | Qty {parsed['quantity']} | Exp {parsed['expiry_date']}")
                    
                    if items:
                        update_progress(f"✅ Windows OCR found {len(items)} items!", 80)
                except Exception as e_win:
                    self.append_log(f"⚠️ Windows OCR scan failed: {e_win}")

                if not items:
                    update_progress("🔍 Step 2/3 — Running Tesseract OCR engine...", 40)
                    try:
                        self.append_log("🔍 Starting Tesseract OCR scan...")
                        items = self.controller.ocr_engine.run_tesseract_ocr(file_path, self.controller.known_brands, self.append_log)
                        update_progress(f"✅ Tesseract found {len(items)} items!", 80)
                    except Exception as e_tess:
                        self.append_log(f"⚠️ Tesseract failed: {e_tess}")

                if not items:
                    update_progress("🔍 Step 3/3 — Running fallback fuzzy word scan...", 60)
                    try:
                        raw_text = ""
                        try:
                            res = winocr.recognize_pil_sync(img_pil, lang="en-US")
                            raw_text = res.get('text', '').strip()
                        except Exception:
                            pass
                        if not raw_text:
                            try:
                                raw_text = pytesseract.image_to_string(img_pil).strip()
                            except Exception:
                                pass
                        
                        if raw_text:
                            words = re.findall(r'\b[a-zA-Z]+\b', raw_text)
                            seen = set()
                            for w in words:
                                wl = w.lower()
                                if wl in self.controller.known_brands and wl not in seen:
                                    bn, gf = self.controller.known_brands[wl]
                                    items.append({
                                        "brand_name": bn, "generic_formula": gf, "manufacturer": "Unknown",
                                        "category": "General", "form": "Tablet", "dosage": "N/A",
                                        "barcode": "N/A", "batch_number": "N/A", "expiry_date": "12/27",
                                        "pack_size": "10s", "cost_price": 85.0, "retail_price": 100.0,
                                        "tax_rate": 0.0, "discount_allowed": 0.0, "quantity": 10
                                    })
                                    seen.add(wl)
                            if items:
                                update_progress(f"✅ Fuzzy scan extracted {len(items)} items!", 80)
                    except Exception as e_fuzzy:
                        self.append_log(f"⚠️ Fuzzy scan fallback failed: {e_fuzzy}")

            update_progress("Populating results table...", 90)

            def fill_table():
                self.table.clear_grid()
                populated = 0
                for item in items:
                    b_name = str(item.get("brand_name") or "").strip()
                    g_form = str(item.get("generic_formula") or "N/A").strip()
                    if not b_name or b_name.lower() in ("n/a", "none"):
                        continue
                    try:
                        price = float(str(item.get("retail_price", 0)).replace(",","").replace("Rs","").replace("PKR","").strip())
                    except Exception:
                        price = 0.0
                    expiry = str(item.get("expiry_date") or "N/A").strip()
                    try:
                        qty = max(1, int(float(str(item.get("quantity", 1)).strip())))
                    except Exception:
                        qty = 1
                    
                    cost_val = f"Rs {item.get('cost_price', price * 0.85):.2f}"
                    retail_val = f"Rs {price:.2f}"
                    tax_val = f"{item.get('tax_rate', 0.0)}%"
                    disc_val = f"{item.get('discount_allowed', 0.0)}%"

                    self.table.insert_row((
                        b_name, g_form, item.get("manufacturer", "Unknown"), item.get("category", "General"),
                        item.get("form", "Tablet"), item.get("dosage", "N/A"), item.get("barcode", "N/A"),
                        item.get("batch_number", "N/A"), expiry, item.get("pack_size", "10s"),
                        cost_val, retail_val, tax_val, disc_val, qty
                    ))
                    populated += 1

                self.sidebar.update_progress("AI Scan Complete!", 100)

                if populated:
                    self.append_log(f"🎉 {populated} medicines extracted. Review and upload!")
                    self.table.set_save_button_state(tk.NORMAL)
                    messagebox.showinfo("AI OCR Complete 🎉", f"✅ Extracted {populated} medicine(s)!\n\n💡 Double-click any row to edit before uploading.")
                else:
                    self.append_log("⚠️ No medicines extracted.")
                    messagebox.showwarning("No Data Found", "Could not extract any medicine rows.\n\nTips:\n• Use clear lighting\n• Hold camera steady\n• Add manually in Inventory tab.")

            self._ui(fill_table)

        except Exception as e:
            self.append_log(f"❌ Error: {e}")
            self._ui(lambda: messagebox.showerror("Processing Error", f"Failed:\n{e}"))

    def edit_ocr_row(self, event):
        selected_item = self.table.get_selected_rows()
        if not selected_item:
            return
            
        item_values = self.table.get_row_values(selected_item[0])
        
        def on_save_changes(values):
            self.table.set_row_values(selected_item[0], values)
            self.append_log(f"Updated item: {values[0]}")

        OcrEditDialog(self.master, item_values, on_save_changes)

    def save_bulk_ocr_data(self):
        items = []
        for child in self.table.get_all_rows():
            values = self.table.get_row_values(child)
            items.append({
                "brand_name": values[0], "generic_formula": values[1], "manufacturer": values[2],
                "category": values[3], "form": values[4], "dosage": values[5], "barcode": values[6],
                "batch_number": values[7], "expiry_date": values[8], "pack_size": values[9],
                "cost_price": float(values[10].replace("Rs ", "")),
                "retail_price": float(values[11].replace("Rs ", "")),
                "tax_rate": float(values[12].replace("%", "")),
                "discount_allowed": float(values[13].replace("%", "")),
                "quantity": int(values[14])
            })
            
        if not items:
            messagebox.showwarning("No Data", "No items to save. Please scan an invoice first.")
            return
            
        if not self.controller.pharmacy_license or not self.controller.lat or not self.controller.lng:
            messagebox.showwarning("Config Error", "Please save your Pharmacy License, Latitude, and Longitude first.")
            return

        try:
            self.append_log("Saving bulk data to local SQLite database...")
            for item in items:
                self.controller.db_manager.add_or_update_stock(item)
            
            self.append_log("Local SQLite database updated successfully.")
            self.sidebar.update_progress("Syncing bulk data to cloud...", 40)
            self.update()
            
            self.append_log("Connecting to MongoDB cloud cluster...")
            
            def do_bulk_sync():
                try:
                    self.controller.cloud_manager.sync_local_to_cloud(
                        self.controller.db_name, self.controller.pharmacy_name, 
                        self.controller.pharmacy_license, self.controller.lat, self.controller.lng
                    )
                    
                    self._ui(lambda: [
                        self.sidebar.update_progress("Bulk Upload Successful", 100),
                        self.append_log(f"Bulk sync complete. Synced {len(items)} items."),
                        self.main_view.inventory_tab.load_local_inventory(),
                        self.controller.db_manager.load_db_brands(self.controller.known_brands),
                        self.clear_ocr_data(),
                        messagebox.showinfo("Bulk Sync Success", f"Successfully saved {len(items)} medicines and uploaded in bulk to cloud!")
                    ])
                except Exception as e_sync:
                    self._ui(lambda err=e_sync: [
                        self.sidebar.update_progress("Sync failed", 0),
                        self.append_log(f"Error during bulk sync: {err}"),
                        messagebox.showerror("Bulk Sync Error", f"Failed to upload data in bulk: {err}")
                    ])

            threading.Thread(target=do_bulk_sync, daemon=True).start()
            
        except Exception as e:
            self.append_log(f"Database error during bulk save: {e}")
            messagebox.showerror("Bulk Save Error", f"Failed to write locally: {e}")

    def append_log(self, text):
        self.sidebar.append_log(text)

    def clear_ocr_data(self):
        self.table.clear_grid()
        self.invoice_photo = None
        self.sidebar.clear_preview()
        self.sidebar.update_progress("Idle", 0)
        self.table.set_save_button_state(tk.DISABLED)
        self.append_log("Cleared scan workbench.")

    def delete_selected_ocr_rows(self):
        selected = self.table.get_selected_rows()
        if not selected:
            messagebox.showwarning("Nothing Selected",
                "کوئی row select نہیں ہے!\n\n"
                "Ctrl+Click یا Shift+Click سے rows select کریں پھر Delete دبائیں۔")
            return

        count = len(selected)
        for item in selected:
            self.table.delete_row(item)

        self.append_log(f"🗑️ {count} row(s) deleted by user.")

        if not self.table.get_all_rows():
            self.table.set_save_button_state(tk.DISABLED)
            self.append_log("Table is now empty.")
