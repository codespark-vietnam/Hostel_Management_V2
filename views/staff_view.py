import customtkinter as ctk
from tkinter import ttk, messagebox
from utils import apply_treeview_style # <--- IMPORT MỚI

class StaffView(ctk.CTkFrame):
    """
    Giao diện Quản lý Nhân viên (Staff Management).
    """
    
    def __init__(self, master, db):
        super().__init__(master, fg_color="transparent")
        self.db = db
        self.selected_user_id = None 

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1) 

        # --- 1. Frame Tiêu đề và Nút ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="new", padx=10, pady=(0, 10))
        
        title = ctk.CTkLabel(header_frame, text="👥 Staff Management", font=ctk.CTkFont(size=20, weight="bold"))
        title.pack(side="left")
        
        add_button = ctk.CTkButton(header_frame, text="+ Add Staff", command=self.open_add_staff_popup)
        add_button.pack(side="right")

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
            columns=("UserID", "Username", "Email", "Role", "CreatedDate"),
            show="headings",
            yscrollcommand=scrollbar.set
        )
        
        scrollbar.configure(command=self.tree.yview)
        
        self.tree.heading("UserID", text="User ID")
        self.tree.heading("Username", text="Username")
        self.tree.heading("Email", text="Email")
        self.tree.heading("Role", text="Role")
        self.tree.heading("CreatedDate", text="Created Date")
        
        self.tree.column("UserID", width=100, anchor="w")
        self.tree.column("Username", width=150, anchor="w")
        self.tree.column("Email", width=250, anchor="w")
        self.tree.column("Role", width=100, anchor="w")
        self.tree.column("CreatedDate", width=150, anchor="w")

        scrollbar.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)

        self.tree.bind('<<TreeviewSelect>>', self.on_row_select)

        # --- 3. Frame Nút bấm dưới ---
        bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        bottom_frame.grid(row=2, column=0, sticky="sew", padx=10, pady=10)
        
        self.reset_pass_button = ctk.CTkButton(bottom_frame, text="Reset Password", command=self.open_reset_password_popup, state="disabled")
        self.reset_pass_button.pack(side="left")
        
        self.delete_button = ctk.CTkButton(bottom_frame, text="Delete", fg_color="#D2042D", hover_color="#FF0800", command=self.delete_selected_staff, state="disabled")
        self.delete_button.pack(side="left", padx=10)

        self.load_staff()

    def load_staff(self):
        """Tải hoặc tải lại danh sách nhân viên từ CSDL."""
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        staff_list = self.db.get_all_users()
        
        for staff in staff_list:
            id_prefix = "ADM" if staff['role'] == 'admin' else "STF"
            display_id = f"{id_prefix}{staff['id']:03d}"
            
            self.tree.insert("", "end", iid=staff['id'], values=(
                display_id,
                staff['username'],
                staff['email'],
                staff['role'].capitalize(),
                staff['created_at'].strftime("%Y-%m-%d %H:%M")
            ))
        
        self.on_row_select(None)

    def on_row_select(self, event):
        """Được gọi khi một hàng trong bảng được chọn."""
        selected_item = self.tree.focus()
        if selected_item:
            self.selected_user_id = selected_item
            self.reset_pass_button.configure(state="normal")
            self.delete_button.configure(state="normal")
        else:
            self.selected_user_id = None
            self.reset_pass_button.configure(state="disabled")
            self.delete_button.configure(state="disabled")

    def open_add_staff_popup(self):
        """Mở cửa sổ Toplevel để thêm nhân viên mới."""
        popup = AddStaffPopup(self, self.db)
        self.wait_window(popup)
        self.load_staff()

    def open_reset_password_popup(self):
        """Mở cửa sổ Toplevel để đặt lại mật khẩu."""
        if not self.selected_user_id:
            return
            
        popup = ResetPasswordPopup(self, self.db, self.selected_user_id)
        self.wait_window(popup)

    def delete_selected_staff(self):
        """Xóa nhân viên đang được chọn."""
        if not self.selected_user_id:
            return
            
        selected_item = self.tree.item(self.selected_user_id)
        username = selected_item['values'][1]

        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete staff member '{username}'?"):
            return
            
        success, message = self.db.delete_user(self.selected_user_id)
        
        if success:
            messagebox.showinfo("Success", message)
            self.load_staff() # Tải lại bảng
        else:
            messagebox.showerror("Error", message)

# (Class AddStaffPopup và ResetPasswordPopup giữ nguyên không đổi)
# ... (Bạn có thể giữ nguyên 2 class này như trong file cũ)
class AddStaffPopup(ctk.CTkToplevel):
    """Cửa sổ Pop-up để thêm nhân viên mới."""
    
    def __init__(self, master, db):
        super().__init__(master)
        self.db = db
        self.master_view = master
        
        self.title("Add New Staff")
        self.geometry("350x400")
        self.resizable(False, False)
        
        self.transient(master)
        self.grab_set() 

        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        title = ctk.CTkLabel(main_frame, text="New Staff Account", font=ctk.CTkFont(size=16, weight="bold"))
        title.pack(pady=(0, 20))
        
        self.username_entry = ctk.CTkEntry(main_frame, width=250, placeholder_text="Username")
        self.username_entry.pack(pady=10)
        
        self.email_entry = ctk.CTkEntry(main_frame, width=250, placeholder_text="Email")
        self.email_entry.pack(pady=10)
        
        self.password_entry = ctk.CTkEntry(main_frame, width=250, placeholder_text="Password", show="*")
        self.password_entry.pack(pady=10)
        
        self.confirm_entry = ctk.CTkEntry(main_frame, width=250, placeholder_text="Confirm Password", show="*")
        self.confirm_entry.pack(pady=10)

        self.message_label = ctk.CTkLabel(main_frame, text="", text_color="red")
        self.message_label.pack(pady=(5, 0))
        
        add_button = ctk.CTkButton(main_frame, text="Add Staff", command=self.add_staff)
        add_button.pack(pady=20)
        
    def add_staff(self):
        username = self.username_entry.get()
        email = self.email_entry.get()
        password = self.password_entry.get()
        confirm = self.confirm_entry.get()
        
        self.message_label.configure(text="")
        
        if not username or not email or not password or not confirm:
            self.message_label.configure(text="Please fill in all fields.")
            return
            
        if password != confirm:
            self.message_label.configure(text="Passwords do not match.")
            return
            
        success, message = self.db.register_user(username, email, password)
        
        if success:
            messagebox.showinfo("Success", "Staff added successfully!", parent=self)
            self.destroy() 
        else:
            self.message_label.configure(text=message)


class ResetPasswordPopup(ctk.CTkToplevel):
    """Cửa sổ Pop-up để đặt lại mật khẩu."""
    
    def __init__(self, master, db, user_id):
        super().__init__(master)
        self.db = db
        self.user_id = user_id
        
        self.title("Reset Password")
        self.geometry("350x250")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        title = ctk.CTkLabel(main_frame, text="Set New Password", font=ctk.CTkFont(size=16, weight="bold"))
        title.pack(pady=(0, 20))

        self.password_entry = ctk.CTkEntry(main_frame, width=250, placeholder_text="New Password", show="*")
        self.password_entry.pack(pady=10)
        
        self.confirm_entry = ctk.CTkEntry(main_frame, width=250, placeholder_text="Confirm New Password", show="*")
        self.confirm_entry.pack(pady=10)
        
        self.message_label = ctk.CTkLabel(main_frame, text="", text_color="red")
        self.message_label.pack(pady=(5, 0))
        
        reset_button = ctk.CTkButton(main_frame, text="Reset Password", command=self.reset_password)
        reset_button.pack(pady=20)

    def reset_password(self):
        password = self.password_entry.get()
        confirm = self.confirm_entry.get()

        self.message_label.configure(text="")

        if not password or not confirm:
            self.message_label.configure(text="Please fill in all fields.")
            return

        if password != confirm:
            self.message_label.configure(text="Passwords do not match.")
            return
            
        success, message = self.db.reset_user_password(self.user_id, password)
        
        if success:
            messagebox.showinfo("Success", message, parent=self)
            self.destroy()
        else:
            self.message_label.configure(text=message)