import customtkinter as ctk
import sqlite3
import os
import ctypes
import tkinter.messagebox as messagebox

# --- Database Configuration & Functions ---
DB_FOLDER = r"C:\ProgramData\ContactBook"
DB_PATH = os.path.join(DB_FOLDER, "sys_cache.db")

class ContactDB:
    def __init__(self):
        self._setup_system_folder()
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        self._create_table()

    def _setup_system_folder(self):
        if not os.path.exists(DB_FOLDER):
            os.makedirs(DB_FOLDER)
            # Hide the folder on Windows (0x02 = FILE_ATTRIBUTE_HIDDEN)
            try:
                ctypes.windll.kernel32.SetFileAttributesW(DB_FOLDER, 0x02)
            except Exception:
                pass

    def _create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT UNIQUE NOT NULL,
                email TEXT,
                address TEXT
            )
        ''')
        self.conn.commit()

    def add_contact(self, name, phone, email, address):
        try:
            self.cursor.execute('''
                INSERT INTO contacts (name, phone, email, address)
                VALUES (?, ?, ?, ?)
            ''', (name, phone, email, address))
            self.conn.commit()
            return True, "Contact added successfully."
        except sqlite3.IntegrityError:
            return False, "Duplicate detected: A contact with this phone number already exists."

    def get_all(self):
        self.cursor.execute("SELECT * FROM contacts ORDER BY name")
        return self.cursor.fetchall()

    def search(self, query):
        search_term = f"%{query}%"
        self.cursor.execute('''
            SELECT * FROM contacts 
            WHERE name LIKE ? OR phone LIKE ? OR email LIKE ?
            ORDER BY name
        ''', (search_term, search_term, search_term))
        return self.cursor.fetchall()

    def update_contact(self, cid, name, phone, email, address):
        try:
            self.cursor.execute('''
                UPDATE contacts 
                SET name=?, phone=?, email=?, address=? 
                WHERE id=?
            ''', (name, phone, email, address, cid))
            self.conn.commit()
            return True, "Contact updated."
        except sqlite3.IntegrityError:
            return False, "Duplicate detected: Phone number already in use."

    def delete_contact(self, cid):
        self.cursor.execute("DELETE FROM contacts WHERE id=?", (cid,))
        self.conn.commit()


# --- Main Application UI ---
class ContactApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Contact Book")
        self.geometry("900x600")
        self.minsize(800, 500)
        
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.db = ContactDB()

        # Grid configuration: 2 columns
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_main_area()
        self.load_contacts()

    def _build_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        logo_label = ctk.CTkLabel(self.sidebar_frame, text="Contact Book", font=ctk.CTkFont(size=20, weight="bold"))
        logo_label.grid(row=0, column=0, padx=20, pady=(20, 30))

        btn_add = ctk.CTkButton(self.sidebar_frame, text="Add Contact", command=lambda: self.show_contact_modal())
        btn_add.grid(row=1, column=0, padx=20, pady=10)

        btn_view = ctk.CTkButton(self.sidebar_frame, text="View All", command=lambda: [self.search_var.set(""), self.load_contacts()])
        btn_view.grid(row=2, column=0, padx=20, pady=10)

        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"],
                                                             command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=5, column=0, padx=20, pady=20, sticky="s")
        self.appearance_mode_optionemenu.set("System")

    def _build_main_area(self):
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)

        # Top Search Bar
        search_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        search_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        search_frame.grid_columnconfigure(0, weight=1)

        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", self.perform_search)
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Search by name, phone, or email...", 
                                         textvariable=self.search_var, height=40)
        self.search_entry.grid(row=0, column=0, sticky="ew")

        # Scrollable Contacts Area
        self.scroll_frame = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
        self.scroll_frame.grid(row=1, column=0, sticky="nsew")
        self.scroll_frame.grid_columnconfigure(0, weight=1)

    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

    def perform_search(self, *args):
        query = self.search_var.get()
        if query:
            results = self.db.search(query)
            self.load_contacts(results)
        else:
            self.load_contacts()

    def _get_initials(self, name):
        parts = name.strip().split()
        if not parts: return "??"
        if len(parts) == 1: return parts[0][:2].upper()
        return (parts[0][0] + parts[-1][0]).upper()

    def load_contacts(self, data=None):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        if data is None:
            data = self.db.get_all()

        for contact in data:
            cid, name, phone, email, address = contact
            self._create_contact_card(cid, name, phone, email, address)

    def _create_contact_card(self, cid, name, phone, email, address):
        card = ctk.CTkFrame(self.scroll_frame, corner_radius=8)
        card.grid(sticky="ew", pady=5, padx=5)
        card.grid_columnconfigure(1, weight=1)

        # Avatar
        initials = self._get_initials(name)
        avatar = ctk.CTkLabel(card, text=initials, width=50, height=50, corner_radius=25, 
                              fg_color=("gray70", "gray30"), font=ctk.CTkFont(size=16, weight="bold"))
        avatar.grid(row=0, column=0, rowspan=2, padx=(15, 15), pady=15)

        # Info
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.grid(row=0, column=1, rowspan=2, sticky="w", pady=10)
        
        name_lbl = ctk.CTkLabel(info_frame, text=name, font=ctk.CTkFont(size=16, weight="bold"))
        name_lbl.grid(row=0, column=0, sticky="w")
        
        details_lbl = ctk.CTkLabel(info_frame, text=f"📞 {phone}   |   ✉️ {email or 'N/A'}", text_color="gray")
        details_lbl.grid(row=1, column=0, sticky="w")

        # Buttons Frame
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.grid(row=0, column=2, rowspan=2, sticky="e", padx=15)

        btn_call = ctk.CTkButton(btn_frame, text="Call", width=60, command=lambda n=name: self._mock_action("Calling", n))
        btn_call.grid(row=0, column=0, padx=5)

        btn_email = ctk.CTkButton(btn_frame, text="Email", width=60, command=lambda n=name: self._mock_action("Opening email for", n))
        btn_email.grid(row=0, column=1, padx=5)

        btn_edit = ctk.CTkButton(btn_frame, text="Edit", width=60, fg_color="#E59500", hover_color="#B37400",
                                 command=lambda: self.show_contact_modal(cid, name, phone, email, address))
        btn_edit.grid(row=0, column=2, padx=5)

        btn_delete = ctk.CTkButton(btn_frame, text="Delete", width=60, fg_color="#D62828", hover_color="#9E1B1B",
                                   command=lambda: self._delete_contact(cid, name))
        btn_delete.grid(row=0, column=3, padx=5)

    def _mock_action(self, action, name):
        messagebox.showinfo(action, f"{action} {name}...")

    def _delete_contact(self, cid, name):
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {name}?"):
            self.db.delete_contact(cid)
            self.perform_search() # Refresh current view

    def show_contact_modal(self, cid=None, name="", phone="", email="", address=""):
        modal = ctk.CTkToplevel(self)
        modal.title("Update Contact" if cid else "Add Contact")
        modal.geometry("400x450")
        modal.resizable(False, False)
        modal.grab_set() # Make it modal
        
        modal.grid_columnconfigure(0, weight=1)

        # Fields
        # c_name = ctk.CTkEntry(modal, placeholder_text="Full Name")
        # c_name.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        # c_name.insert(0, name)

        # c_phone = ctk.CTkEntry(modal, placeholder_text="Phone Number")
        # c_phone.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        # c_phone.insert(0, phone)

        # c_email = ctk.CTkEntry(modal, placeholder_text="Email Address")
        # c_email.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        # c_email.insert(0, email)

        # c_address = ctk.CTkEntry(modal, placeholder_text="Physical Address")
        # c_address.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        # c_address.insert(0, address)

        # Fields
        ctk.CTkLabel(modal, text="Name").grid(row=0, column=0, padx=20, pady=(15, 0), sticky="w")
        c_name = ctk.CTkEntry(modal, placeholder_text="Full Name")
        c_name.grid(row=1, column=0, padx=20, pady=(5, 10), sticky="ew")
        c_name.insert(0, name)

        ctk.CTkLabel(modal, text="Phone Number").grid(row=2, column=0, padx=20, pady=(10, 0), sticky="w")
        c_phone = ctk.CTkEntry(modal, placeholder_text="Phone Number")
        c_phone.grid(row=3, column=0, padx=20, pady=(5, 10), sticky="ew")
        c_phone.insert(0, phone)

        ctk.CTkLabel(modal, text="Email").grid(row=4, column=0, padx=20, pady=(10, 0), sticky="w")
        c_email = ctk.CTkEntry(modal, placeholder_text="Email Address")
        c_email.grid(row=5, column=0, padx=20, pady=(5, 10), sticky="ew")
        c_email.insert(0, email)

        ctk.CTkLabel(modal, text="Address").grid(row=6, column=0, padx=20, pady=(10, 0), sticky="w")
        c_address = ctk.CTkEntry(modal, placeholder_text="Physical Address")
        c_address.grid(row=7, column=0, padx=20, pady=(5, 10), sticky="ew")
        c_address.insert(0, address)

        def save():
            n, p, e, a = c_name.get().strip(), c_phone.get().strip(), c_email.get().strip(), c_address.get().strip()
            if not n or not p:
                messagebox.showerror("Error", "Name and Phone are required fields.")
                return

            if cid:
                success, msg = self.db.update_contact(cid, n, p, e, a)
            else:
                success, msg = self.db.add_contact(n, p, e, a)

            if success:
                modal.destroy()
                self.perform_search() # Refresh current view
            else:
                messagebox.showwarning("Warning", msg)

        btn_save = ctk.CTkButton(modal, text="Save Contact", command=save)
        # btn_save.grid(row=4, column=0, padx=20, pady=(20, 10), sticky="ew")
        btn_save.grid(row=8, column=0, padx=20, pady=(20, 10), sticky="ew")

        # Center modal on main window
        modal.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - (modal.winfo_width() // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (modal.winfo_height() // 2)
        modal.geometry(f"+{x}+{y}")


if __name__ == "__main__":
    app = ContactApp()
    app.mainloop()