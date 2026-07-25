import tkinter as tk
from tkinter import ttk

class GeminiKeyDialog(tk.Toplevel):
    def __init__(self, parent, current_key, main_view, on_save_callback):
        super().__init__(parent)
        self.current_key = current_key
        self.on_save = on_save_callback
        self.main_view = main_view
        
        self.title("Configure Gemini API Key")
        self.geometry("420x220")
        self.resizable(False, False)
        self.configure(bg=main_view.bg_color)
        self.transient(parent)
        self.grab_set()
        
        self.setup_ui()
        
    def setup_ui(self):
        # Header Label
        tk.Label(self, text="🧠 Configure Gemini API Key", font=("Segoe UI", 12, "bold"), 
                 bg=self.main_view.bg_color, fg="#2563eb").pack(pady=(15, 10))
        
        # Helper text
        tk.Label(self, text="Please enter your Gemini API Key. This enables advanced AI-powered OCR.", 
                 font=("Segoe UI", 9), bg=self.main_view.bg_color, fg=self.main_view.text_color, wraplength=380).pack(pady=(0, 10))
        
        frame = tk.Frame(self, bg=self.main_view.bg_color, padx=20)
        frame.pack(fill=tk.X)
        
        self.entry = tk.Entry(frame, font=("Segoe UI", 10), bg="#ffffff", fg=self.main_view.text_color,
                              insertbackground=self.main_view.text_color, relief=tk.FLAT, bd=0, highlightthickness=1,
                              highlightbackground="#cbd5e1", highlightcolor=self.main_view.accent_color)
        self.entry.pack(fill=tk.X, ipady=5, pady=5)
        if self.current_key:
            self.entry.insert(0, self.current_key)
            
        btn_frame = tk.Frame(self, bg=self.main_view.bg_color)
        btn_frame.pack(fill=tk.X, pady=(15, 10))
        
        save_btn = tk.Button(btn_frame, text="💾 Save Key", bg=self.main_view.accent_color, fg="white", 
                             font=("Segoe UI", 9, "bold"), relief=tk.FLAT, bd=0, padx=15, pady=6, command=self.save_key)
        save_btn.pack(side=tk.RIGHT, padx=(5, 20))
        save_btn.bind("<Enter>", lambda e: save_btn.config(bg="#1d4ed8"))
        save_btn.bind("<Leave>", lambda e: save_btn.config(bg=self.main_view.accent_color))
        
        cancel_btn = tk.Button(btn_frame, text="Cancel", bg="#64748b", fg="white", 
                               font=("Segoe UI", 9, "bold"), relief=tk.FLAT, bd=0, padx=15, pady=6, command=self.destroy)
        cancel_btn.pack(side=tk.RIGHT, padx=5)
        cancel_btn.bind("<Enter>", lambda e: cancel_btn.config(bg="#475569"))
        cancel_btn.bind("<Leave>", lambda e: cancel_btn.config(bg="#64748b"))

    def save_key(self):
        key = self.entry.get().strip()
        self.on_save(key)
        self.destroy()

class OcrSidebar(tk.Frame):
    def __init__(self, parent, controller, main_view, on_scan_callback, on_save_key_callback):
        super().__init__(parent, bg=main_view.bg_color, width=340)
        self.controller = controller
        self.main_view = main_view
        self.on_scan = on_scan_callback
        self.on_save_key = on_save_key_callback
        self.gemini_key = getattr(self.controller, "gemini_key", "")
        self.pack_propagate(False)
        self.setup_ui()

    def setup_ui(self):
        self.scan_btn = tk.Button(self, text="📷 Select & Scan Invoice Image", bg="#8b5cf6", fg="white", 
                                  font=("Segoe UI", 10, "bold"), pady=8, relief=tk.FLAT, bd=0, command=self.on_scan)
        self.scan_btn.pack(fill=tk.X, pady=5)
        self.scan_btn.bind("<Enter>", lambda e: self.scan_btn.config(bg="#7c3aed"))
        self.scan_btn.bind("<Leave>", lambda e: self.scan_btn.config(bg="#8b5cf6"))

        gemini_btn = tk.Button(self, text="🔑 Configure Gemini API Key", bg="#2563eb", fg="white", 
                               font=("Segoe UI", 9, "bold"), relief=tk.FLAT, bd=0, pady=6, 
                               cursor="hand2", command=self.open_gemini_key_dialog)
        gemini_btn.pack(fill=tk.X, pady=5)
        gemini_btn.bind("<Enter>", lambda e: gemini_btn.config(bg="#1d4ed8"))
        gemini_btn.bind("<Leave>", lambda e: gemini_btn.config(bg="#2563eb"))

        img_frame = tk.LabelFrame(self, text=" Invoice Preview ", font=("Segoe UI", 9, "bold"), bg=self.main_view.bg_color, fg=self.main_view.primary_color, bd=1, relief=tk.SOLID)
        img_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.image_label = tk.Label(img_frame, text="No invoice selected\n(Click button above to browse)", font=("Segoe UI", 9), fg=self.main_view.text_light, bg=self.main_view.card_color, bd=0)
        self.image_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.progress_label = tk.Label(self, text="Status: Idle", font=("Segoe UI", 9, "bold"), fg=self.main_view.text_color, bg=self.main_view.bg_color)
        self.progress_label.pack(anchor=tk.W, pady=2)

        self.ocr_progress = ttk.Progressbar(self, orient=tk.HORIZONTAL, mode='determinate')
        self.ocr_progress.pack(fill=tk.X, pady=5)

        tk.Label(self, text="OCR Scanner Logs:", font=("Segoe UI", 8, "bold"), fg=self.main_view.text_light, bg=self.main_view.bg_color).pack(anchor=tk.W)
        self.log_text = tk.Text(self, height=6, font=("Consolas", 8), bg=self.main_view.primary_color, fg="#94a3b8", bd=0, padx=5, pady=5)
        self.log_text.pack(fill=tk.X, pady=2)
        self.log_text.insert(tk.END, "OCR Engine initialized. Ready.\n")
        self.log_text.config(state=tk.DISABLED)

    def set_button_state(self, state):
        self.scan_btn.config(state=state)

    def get_gemini_key(self):
        return self.gemini_key

    def open_gemini_key_dialog(self):
        dialog = GeminiKeyDialog(self.winfo_toplevel(), self.gemini_key, self.main_view, self.update_and_save_gemini_key)

    def update_and_save_gemini_key(self, new_key):
        self.gemini_key = new_key
        self.on_save_key()

    def set_preview_image(self, photo):
        self.image_label.config(image=photo, text="")

    def clear_preview(self):
        self.image_label.config(image="", text="No invoice selected\n(Click button above to browse)")

    def update_progress(self, text, value):
        self.progress_label.config(text=f"Status: {text}")
        self.ocr_progress.config(value=value)

    def append_log(self, text):
        import datetime
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {text}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def clear_logs(self):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.insert(tk.END, "OCR Engine initialized. Ready.\n")
        self.log_text.config(state=tk.DISABLED)
