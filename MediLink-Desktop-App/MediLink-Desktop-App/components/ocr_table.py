import tkinter as tk
from tkinter import ttk

class OcrTable(tk.LabelFrame):
    def __init__(self, parent, controller, main_view, on_edit_callback, on_delete_callback, on_save_callback, on_clear_callback):
        super().__init__(parent, text=" Reviewed Extracted Data ", font=("Segoe UI", 10, "bold"), 
                         bg=main_view.card_color, fg=main_view.primary_color, bd=1, relief=tk.SOLID, padx=10, pady=10)
        self.controller = controller
        self.main_view = main_view
        self.on_edit = on_edit_callback
        self.on_delete = on_delete_callback
        self.on_save = on_save_callback
        self.on_clear = on_clear_callback
        self.setup_ui()

    def setup_ui(self):
        tip_label = tk.Label(self,
            text="💡 Double-click = Edit  |  Ctrl/Shift+Click = Multi-Select  |  Del/Backspace = Delete Selected",
            font=("Segoe UI", 8, "italic"), fg=self.main_view.accent_color, bg="#eff6ff", pady=5)
        tip_label.pack(fill=tk.X, padx=0, pady=5)

        ocr_table_frame = tk.Frame(self, bg=self.main_view.card_color)
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

        self.ocr_tree.bind("<Double-1>", self.on_edit)
        self.ocr_tree.bind("<Delete>",   lambda e: self.on_delete())
        self.ocr_tree.bind("<BackSpace>", lambda e: self.on_delete())

        ocr_btn_frame = tk.Frame(self, bg=self.main_view.card_color, pady=5)
        ocr_btn_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=0)

        def style_action_btn(text, cmd, normal_bg, hover_bg, disabled=False):
            btn = tk.Button(ocr_btn_frame, text=text, bg=normal_bg, fg="white", font=("Segoe UI", 9, "bold"), padx=15, pady=6, relief=tk.FLAT, bd=0, command=cmd)
            btn.pack(side=tk.RIGHT, padx=5)
            btn.bind("<Enter>", lambda e: btn.config(bg=hover_bg) if btn["state"] == tk.NORMAL or btn["state"] == "normal" else None)
            btn.bind("<Leave>", lambda e: btn.config(bg=normal_bg) if btn["state"] == tk.NORMAL or btn["state"] == "normal" else None)
            if disabled:
                btn.config(state=tk.DISABLED)
            return btn

        self.ocr_save_btn = style_action_btn("💾 Save & Bulk Sync to Cloud", self.on_save, self.main_view.success_color, "#059669", disabled=True)
        self.ocr_delete_btn = style_action_btn("❌ Delete Selected Row(s)", self.on_delete, self.main_view.danger_color, "#dc2626")
        self.ocr_clear_btn = style_action_btn("🗑️ Clear All", self.on_clear, self.main_view.text_light, "#475569")

    def set_save_button_state(self, state):
        self.ocr_save_btn.config(state=state)

    def clear_grid(self):
        for row in self.ocr_tree.get_children():
            self.ocr_tree.delete(row)

    def insert_row(self, values):
        self.ocr_tree.insert("", tk.END, values=values)

    def get_selected_rows(self):
        return self.ocr_tree.selection()

    def get_row_values(self, item_id):
        return self.ocr_tree.item(item_id, "values")

    def set_row_values(self, item_id, values):
        self.ocr_tree.item(item_id, values=values)

    def get_all_rows(self):
        return self.ocr_tree.get_children()

    def delete_row(self, item_id):
        self.ocr_tree.delete(item_id)
