import customtkinter as ctk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry 
from utils import apply_treeview_style # <--- IMPORT MỚI

class StudentView(ctk.CTkFrame):
    """
    Giao diện Quản lý Sinh viên (Student Management).
    """
    
    def __init__(self, master, db):
        super().__init__(master, fg_color="transparent")
        self.db = db
        self.selected_student_id = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1) 

        # --- 1. Frame Tiêu đề và Nút ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="new", padx=10, pady=(0, 10))
        
        title = ctk.CTkLabel(header_frame, text="🧑‍🎓 Student Management", font=ctk.CTkFont(size=20, weight="bold"))
        title.pack(side="left")
        
        add_button = ctk.CTkButton(header_frame, text="+ Add Student", command=self.open_add_student_popup)
        add_button.pack(side="right")
        
        self.search_entry = ctk.CTkEntry(header_frame, placeholder_text="Search by Name or ID...")
        self.search_entry.pack(side="right", padx=10, fill="x", expand=True)
        self.search_entry.bind("<KeyRelease>", self.on_search) 

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
            columns=("ID", "Name", "Age", "Gender", "Room", "Admission", "Contact", "Email"),
            show="headings",
            yscrollcommand=scrollbar.set
        )
        scrollbar.configure(command=self.tree.yview)
        
        self.tree.heading("ID", text="Student ID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Age", text="Age")
        self.tree.heading("Gender", text="Gender")
        self.tree.heading("Room", text="Room No")
        self.tree.heading("Admission", text="Admission Date")
        self.tree.heading("Contact", text="Contact")
        self.tree.heading("Email", text="Email")
        
        self.tree.column("ID", width=100, anchor="w")
        self.tree.column("Name", width=150, anchor="w")
        self.tree.column("Age", width=50, anchor="center")
        self.tree.column("Gender", width=80, anchor="w")
        self.tree.column("Room", width=80, anchor="center")
        self.tree.column("Admission", width=100, anchor="w")
        self.tree.column("Contact", width=100, anchor="w")
        self.tree.column("Email", width=180, anchor="w")

        scrollbar.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)

        self.tree.bind('<<TreeviewSelect>>', self.on_row_select)

        # --- 3. Frame Nút bấm dưới ---
        bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        bottom_frame.grid(row=2, column=0, sticky="sew", padx=10, pady=10)
        
        self.edit_button = ctk.CTkButton(bottom_frame, text="Edit / View Details", command=self.open_edit_student_popup, state="disabled")
        self.edit_button.pack(side="left")
        
        self.delete_button = ctk.CTkButton(bottom_frame, text="Delete", fg_color="#D2042D", hover_color="#FF0800", command=self.delete_selected_student, state="disabled")
        self.delete_button.pack(side="left", padx=10)

        self.load_students()

    def on_search(self, event):
        search_term = self.search_entry.get()
        self.load_students(search_term)

    def load_students(self, search_term=None):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        student_list = self.db.get_all_students(search_term)
        
        for student in student_list:
            self.tree.insert("", "end", iid=student['student_id'], values=(
                student['student_id'],
                student['name'],
                student['age'],
                student['gender'],
                student['room_no'],
                student['admission_date'],
                student['contact'],
                student['email']
            ))
        
        self.on_row_select(None) 

    def on_row_select(self, event):
        selected_item = self.tree.focus()
        if selected_item:
            self.selected_student_id = selected_item
            self.edit_button.configure(state="normal")
            self.delete_button.configure(state="normal")
        else:
            self.selected_student_id = None
            self.edit_button.configure(state="disabled")
            self.delete_button.configure(state="disabled")

    def open_add_student_popup(self):
        popup = StudentPopup(self, self.db, title="Add New Student")
        self.wait_window(popup)
        self.load_students() 

    def open_edit_student_popup(self):
        if not self.selected_student_id:
            return
        
        student_data = self.db.get_student_by_id(self.selected_student_id)
        if not student_data:
            messagebox.showerror("Error", "Student not found.")
            return
            
        popup = StudentPopup(self, self.db, title="Edit Student", student_data=student_data)
        self.wait_window(popup)
        self.load_students() 

    def delete_selected_student(self):
        if not self.selected_student_id:
            return

        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete student '{self.selected_student_id}'?\nThis will also remove them from their room."):
            return
            
        success, message = self.db.delete_student(self.selected_student_id)
        
        if success:
            messagebox.showinfo("Success", message)
            self.load_students()
        else:
            messagebox.showerror("Error", message)

# (Class StudentPopup giữ nguyên không đổi)
# ... (Bạn có thể giữ nguyên class này như trong file cũ)
class StudentPopup(ctk.CTkToplevel):
    
    def __init__(self, master, db, title, student_data=None):
        super().__init__(master)
        self.db = db
        self.is_edit_mode = (student_data is not None)
        self.student_data = student_data
        self.old_room_no = student_data['room_no'] if self.is_edit_mode else None

        self.title(title)
        self.geometry("500x600") 
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(main_frame, text="Student ID:").pack(anchor="w", padx=10)
        self.id_entry = ctk.CTkEntry(main_frame, width=420)
        self.id_entry.pack(fill="x", padx=10, pady=(0, 10))

        ctk.CTkLabel(main_frame, text="Full Name:").pack(anchor="w", padx=10)
        self.name_entry = ctk.CTkEntry(main_frame)
        self.name_entry.pack(fill="x", padx=10, pady=(0, 10))
        
        age_gender_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        age_gender_frame.pack(fill="x", padx=10, pady=(0, 10))
        age_gender_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        ctk.CTkLabel(age_gender_frame, text="Age:").grid(row=0, column=0, sticky="w")
        self.age_entry = ctk.CTkEntry(age_gender_frame)
        self.age_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        
        ctk.CTkLabel(age_gender_frame, text="Gender:").grid(row=0, column=2, sticky="w", padx=10)
        self.gender_var = ctk.StringVar(value="Male")
        self.gender_menu = ctk.CTkComboBox(age_gender_frame, variable=self.gender_var, values=["Male", "Female", "Other"])
        self.gender_menu.grid(row=0, column=3, sticky="ew")

        ctk.CTkLabel(main_frame, text="Email:").pack(anchor="w", padx=10)
        self.email_entry = ctk.CTkEntry(main_frame)
        self.email_entry.pack(fill="x", padx=10, pady=(0, 10))

        ctk.CTkLabel(main_frame, text="Contact No:").pack(anchor="w", padx=10)
        self.contact_entry = ctk.CTkEntry(main_frame)
        self.contact_entry.pack(fill="x", padx=10, pady=(0, 10))

        date_room_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        date_room_frame.pack(fill="x", padx=10, pady=(0, 10))
        date_room_frame.grid_columnconfigure((1, 3), weight=1)

        ctk.CTkLabel(date_room_frame, text="Admission Date:").grid(row=0, column=0, sticky="w")
        self.admission_date_entry = DateEntry(date_room_frame, date_pattern='yyyy-mm-dd')
        self.admission_date_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10))

        ctk.CTkLabel(date_room_frame, text="Assign Room:").grid(row=0, column=2, sticky="w", padx=10)
        self.room_var = ctk.StringVar(value="Select Room")
        self.room_menu = ctk.CTkComboBox(date_room_frame, variable=self.room_var)
        self.room_menu.grid(row=0, column=3, sticky="ew")
        
        self.load_room_options()

        self.message_label = ctk.CTkLabel(main_frame, text="", text_color="red")
        self.message_label.pack(pady=(10, 0))

        save_button = ctk.CTkButton(main_frame, text="Save Student", command=self.save_student)
        save_button.pack(pady=20)

        if self.is_edit_mode:
            self.fill_form()

    def load_room_options(self):
        available_rooms = self.db.get_available_rooms()
        if self.is_edit_mode and self.old_room_no and self.old_room_no not in available_rooms:
            available_rooms.insert(0, self.old_room_no)
            
        if not available_rooms:
            available_rooms = ["No Available Rooms"]
            
        self.room_menu.configure(values=available_rooms)
        
        if self.is_edit_mode and self.old_room_no:
            self.room_var.set(self.old_room_no)
        elif available_rooms[0] != "No Available Rooms":
             self.room_var.set(available_rooms[0])
        else:
            self.room_var.set(available_rooms[0])

    def fill_form(self):
        self.id_entry.insert(0, self.student_data['student_id'])
        self.name_entry.insert(0, self.student_data['name'])
        self.age_entry.insert(0, str(self.student_data['age']))
        self.gender_var.set(self.student_data['gender'])
        self.email_entry.insert(0, self.student_data['email'])
        self.contact_entry.insert(0, self.student_data['contact'])
        self.admission_date_entry.set_date(self.student_data['admission_date'])

    def save_student(self):
        try:
            data = {
                'student_id': self.id_entry.get().strip(),
                'name': self.name_entry.get().strip(),
                'age': int(self.age_entry.get()),
                'gender': self.gender_var.get(),
                'email': self.email_entry.get().strip(),
                'contact': self.contact_entry.get().strip(),
                'admission_date': self.admission_date_entry.get_date(),
                'room_no': self.room_var.get()
            }

            if not data['student_id'] or not data['name']:
                self.message_label.configure(text="Student ID and Name are required.")
                return
            if data['room_no'] == "No Available Rooms" or data['room_no'] == "Select Room":
                self.message_label.configure(text="Please select a valid room.")
                return
            if data['age'] <= 0:
                 self.message_label.configure(text="Age must be a positive number.")
                 return

        except ValueError:
            self.message_label.configure(text="Age must be a valid number (e.g., 20).")
            return
        
        if self.is_edit_mode:
            success, message = self.db.update_student(self.student_data['student_id'], data, self.old_room_no)
        else:
            success, message = self.db.add_student(data)
            
        if success:
            messagebox.showinfo("Success", message, parent=self)
            self.destroy()
        else:
            self.message_label.configure(text=message)