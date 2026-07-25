import tkinter as tk

class LoginFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f8fafc")
        self.controller = controller
        self.setup_ui()

    def setup_ui(self):
        brand_lbl = tk.Label(self, text="🏥 MediLink POS", font=("Segoe UI", 24, "bold"), fg="#2563eb", bg="#f8fafc")
        brand_lbl.pack(pady=(15, 5))
        
        sub_lbl = tk.Label(self, text="Pharmacy Management System", font=("Segoe UI", 10, "bold"), fg="#64748b", bg="#f8fafc")
        sub_lbl.pack(pady=(0, 20))
        
        card = tk.Frame(self, bg="#ffffff", bd=0, highlightthickness=1, highlightbackground="#e2e8f0", padx=25, pady=25)
        card.pack(fill=tk.BOTH, expand=True)
        
        def make_input_field(parent, label_text, is_password=False):
            lbl = tk.Label(parent, text=label_text, font=("Segoe UI", 9, "bold"), bg="#ffffff", fg="#0f172a")
            lbl.pack(anchor=tk.W, pady=(8, 2))
            
            ent = tk.Entry(parent, font=("Segoe UI", 10), bg="#f8fafc", fg="#0f172a",
                           insertbackground="#0f172a", relief=tk.FLAT, bd=0, highlightthickness=1,
                           highlightbackground="#cbd5e1", highlightcolor="#2563eb", width=30)
            if is_password:
                ent.config(show="*")
            ent.pack(fill=tk.X, ipady=4)
            return ent

        self.name_entry = make_input_field(card, "🏥 Pharmacy Name")
        self.license_entry = make_input_field(card, "🔑 License Key", is_password=True)
        self.lat_entry = make_input_field(card, "📍 Latitude (e.g. 33.6844)")
        self.lng_entry = make_input_field(card, "📍 Longitude (e.g. 73.0479)")
        
        if self.controller.pharmacy_name:
            self.name_entry.insert(0, self.controller.pharmacy_name)
        if self.controller.lat:
            self.lat_entry.insert(0, self.controller.lat)
        if self.controller.lng:
            self.lng_entry.insert(0, self.controller.lng)

        login_btn = tk.Button(card, text="🚀 Access POS System", bg="#2563eb", fg="white", 
                              font=("Segoe UI", 11, "bold"), relief=tk.FLAT, bd=0, pady=10, 
                              cursor="hand2", command=self.submit_login)
        login_btn.pack(fill=tk.X, pady=(25, 5))
        
        login_btn.bind("<Enter>", lambda e: login_btn.config(bg="#1d4ed8"))
        login_btn.bind("<Leave>", lambda e: login_btn.config(bg="#2563eb"))

        self.error_lbl = tk.Label(card, text="", font=("Segoe UI", 9, "bold"), fg="#ef4444", bg="#ffffff", wraplength=350)
        self.error_lbl.pack(fill=tk.X, pady=(10, 0))

    def submit_login(self):
        name = self.name_entry.get().strip()
        license_key = self.license_entry.get().strip()
        lat = self.lat_entry.get().strip()
        lng = self.lng_entry.get().strip()
        
        self.controller.handle_signin(name, license_key, lat, lng, self.error_lbl)
