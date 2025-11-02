import customtkinter as ctk
from tkinter import ttk, messagebox
from utils import apply_treeview_style # <--- IMPORT MỚI

class RoomView(ctk.CTkFrame):
    """
    Giao diện Quản lý Phòng (Room Management).
    """
    
    def __init__(self, master, db):
        super().__init__(master, fg_color="transparent")
        self.db = db
        self.selected_room_no = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1) 

        # --- 1. Frame Tiêu đề và Nút ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="new", padx=10, pady=(0, 10))
        
        title = ctk.CTkLabel(header_frame, text="🚪 Room Management", font=ctk.CTkFont(size=20, weight="bold"))
        title.pack(side="left")
        
        add_button = ctk.CTkButton(header_frame, text="+ Add Room", command=self.open_add_room_popup)
        add_button.pack(side="right")
        
        refresh_button = ctk.CTkButton(header_frame, text="Refresh", command=self.load_rooms)
        refresh_button.pack(side="right", padx=10)
        
        self.filter_var = ctk.StringVar(value="All")
        self.filter_menu = ctk.CTkComboBox(header_frame, variable=self.filter_var, command=self.load_rooms)
        self.filter_menu.pack(side="right", padx=10)
        
        filter_label = ctk.CTkLabel(header_frame, text="Filter by Type:")
        filter_label.pack(side="right")

        # --- 2. Bảng (Treeview) ---
        
        # --- THAY THẾ KHỐI STYLE CŨ BẰNG HÀM NÀY ---
        apply_treeview_style()
        # ---------------------------------------------
        
        table_frame = ctk.CTkFrame(self, fg_color="transparent")
        table_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical")
        
        self.tree = ttk.Treeview(
            table_frame,
            columns=("RoomNo", "Type", "Capacity", "Occupied", "Rent", "Status"),
            show="headings",
            yscrollcommand=scrollbar.set
        )
        scrollbar.configure(command=self.tree.yview)
        
        self.tree.heading("RoomNo", text="Room No")
        self.tree.heading("Type", text="Type")
        self.tree.heading("Capacity", text="Capacity")
        self.tree.heading("Occupied", text="Occupied")
        self.tree.heading("Rent", text="Rent (₹)")
        self.tree.heading("Status", text="Status")
        
        self.tree.column("RoomNo", width=100, anchor="w")
        self.tree.column("Type", width=150, anchor="w")
        self.tree.column("Capacity", width=80, anchor="center")
        self.tree.column("Occupied", width=80, anchor="center")
        self.tree.column("Rent", width=100, anchor="e")
        self.tree.column("Status", width=120, anchor="w")

        scrollbar.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)

        self.tree.bind('<<TreeviewSelect>>', self.on_row_select)

        # --- 3. Frame Nút bấm dưới ---
        bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        bottom_frame.grid(row=2, column=0, sticky="sew", padx=10, pady=10)
        
        self.edit_button = ctk.CTkButton(bottom_frame, text="Edit", command=self.open_edit_room_popup, state="disabled")
        self.edit_button.pack(side="left")
        
        self.delete_button = ctk.CTkButton(bottom_frame, text="Delete", fg_color="#D2042D", hover_color="#FF0800", command=self.delete_selected_room, state="disabled")
        self.delete_button.pack(side="left", padx=10)

        self.load_rooms()
        self.update_filter_options()

    def update_filter_options(self):
        types = self.db.get_room_types()
        self.filter_menu.configure(values=["All"] + types)

    def load_rooms(self, filter_choice=None):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        filter_type = self.filter_var.get()
        room_list = self.db.get_all_rooms(filter_type)
        
        for room in room_list:
            self.tree.insert("", "end", iid=room['room_no'], values=(
                room['room_no'],
                room['room_type'],
                room['capacity'],
                room['occupied'],
                f"{room['rent']:.2f}", 
                room['status']
            ))
        
        self.on_row_select(None) 
        if filter_choice is None:
             self.update_filter_options()

    def on_row_select(self, event):
        selected_item = self.tree.focus()
        if selected_item:
            self.selected_room_no = selected_item
            self.edit_button.configure(state="normal")
            self.delete_button.configure(state="normal")
        else:
            self.selected_room_no = None
            self.edit_button.configure(state="disabled")
            self.delete_button.configure(state="disabled")

    def open_add_room_popup(self):
        popup = RoomPopup(self, self.db, title="Add New Room")
        self.wait_window(popup)
        self.load_rooms() 

    def open_edit_room_popup(self):
        if not self.selected_room_no:
            return
        
        room_data = self.db.get_room_by_no(self.selected_room_no)
        if not room_data:
            messagebox.showerror("Error", "Room not found.")
            return
            
        popup = RoomPopup(self, self.db, title="Edit Room", room_data=room_data)
        self.wait_window(popup)
        self.load_rooms() 

    def delete_selected_room(self):
        if not self.selected_room_no:
            return

        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete room '{self.selected_room_no}'?"):
            return
            
        success, message = self.db.delete_room(self.selected_room_no)
        
        if success:
            messagebox.showinfo("Success", message)
            self.load_rooms()
        else:
            messagebox.showerror("Error", message)

# (Class RoomPopup giữ nguyên không đổi)
# ... (Bạn có thể giữ nguyên class này như trong file cũ)
class RoomPopup(ctk.CTkToplevel):
    """Cửa sổ Pop-up để Thêm hoặc Sửa thông tin phòng."""
    
    def __init__(self, master, db, title, room_data=None):
        super().__init__(master)
        self.db = db
        self.is_edit_mode = (room_data is not None)
        self.room_data = room_data

        self.title(title)
        self.geometry("400x450")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        main_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(main_frame, text="Room No:").grid(row=0, column=0, sticky="w", padx=10, pady=10)
        self.room_no_entry = ctk.CTkEntry(main_frame)
        self.room_no_entry.grid(row=0, column=1, sticky="ew", padx=10, pady=10)

        ctk.CTkLabel(main_frame, text="Room Type:").grid(row=1, column=0, sticky="w", padx=10, pady=10)
        self.room_type_entry = ctk.CTkEntry(main_frame)
        self.room_type_entry.grid(row=1, column=1, sticky="ew", padx=10, pady=10)

        ctk.CTkLabel(main_frame, text="Capacity:").grid(row=2, column=0, sticky="w", padx=10, pady=10)
        self.capacity_entry = ctk.CTkEntry(main_frame)
        self.capacity_entry.grid(row=2, column=1, sticky="ew", padx=10, pady=10)

        ctk.CTkLabel(main_frame, text="Rent (₹):").grid(row=3, column=0, sticky="w", padx=10, pady=10)
        self.rent_entry = ctk.CTkEntry(main_frame)
        self.rent_entry.grid(row=3, column=1, sticky="ew", padx=10, pady=10)

        ctk.CTkLabel(main_frame, text="Status:").grid(row=4, column=0, sticky="w", padx=10, pady=10)
        self.status_var = ctk.StringVar(value="Available")
        self.status_menu = ctk.CTkComboBox(main_frame, variable=self.status_var, values=["Available", "Full", "Maintenance"])
        self.status_menu.grid(row=4, column=1, sticky="ew", padx=10, pady=10)

        self.message_label = ctk.CTkLabel(main_frame, text="", text_color="red")
        self.message_label.grid(row=5, column=0, columnspan=2, pady=(5, 0))

        save_button = ctk.CTkButton(main_frame, text="Save Room", command=self.save_room)
        save_button.grid(row=6, column=0, columnspan=2, pady=20)

        if self.is_edit_mode:
            self.fill_form()

    def fill_form(self):
        self.room_no_entry.insert(0, self.room_data['room_no'])
        self.room_no_entry.configure(state="disabled") 
        
        self.room_type_entry.insert(0, self.room_data['room_type'])
        self.capacity_entry.insert(0, str(self.room_data['capacity']))
        self.rent_entry.insert(0, f"{self.room_data['rent']:.2f}")
        self.status_var.set(self.room_data['status'])

    def save_room(self):
        try:
            room_no = self.room_no_entry.get().strip()
            room_type = self.room_type_entry.get().strip()
            capacity = int(self.capacity_entry.get())
            rent = float(self.rent_entry.get())
            status = self.status_var.get()

            if not room_no or not room_type:
                self.message_label.configure(text="Room No and Type are required.")
                return
            if capacity <= 0 or rent <= 0:
                 self.message_label.configure(text="Capacity and Rent must be positive numbers.")
                 return

        except ValueError:
            self.message_label.configure(text="Capacity must be an integer (e.g., 2) and Rent must be a number (e.g., 4500.00).")
            return
        
        if self.is_edit_mode and self.room_data['occupied'] > 0 and status == "Available":
             self.message_label.configure(text="Cannot set status to 'Available' for an occupied room.")
             return
        
        if self.is_edit_mode:
            success, message = self.db.update_room(room_no, room_type, capacity, rent, status)
        else:
            success, message = self.db.add_room(room_no, room_type, capacity, rent, status)
            
        if success:
            messagebox.showinfo("Success", message, parent=self)
            self.destroy()
        else:
            self.message_label.configure(text=message)