import customtkinter as ctk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import date
from utils import apply_treeview_style # <--- IMPORT MỚI

class AttendanceView(ctk.CTkFrame):
    """
    Giao diện Quản lý Điểm danh (Attendance Tracking).
    """
    
    def __init__(self, master, db):
        super().__init__(master, fg_color="transparent")
        self.db = db
        self.current_date = date.today().isoformat() 

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1) 

        # --- 1. Frame Tiêu đề và Nút ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="new", padx=10, pady=(0, 10))
        
        title = ctk.CTkLabel(header_frame, text="✅ Attendance Tracking", font=ctk.CTkFont(size=20, weight="bold"))
        title.pack(side="left")
        
        mark_all_button = ctk.CTkButton(header_frame, text="Mark All Present", command=self.mark_all_present)
        mark_all_button.pack(side="right")

        refresh_button = ctk.CTkButton(header_frame, text="Refresh", command=self.load_attendance)
        refresh_button.pack(side="right", padx=10)
        
        self.date_entry = DateEntry(header_frame, date_pattern='yyyy-mm-dd', width=12)
        self.date_entry.pack(side="right", padx=10)
        self.date_entry.bind("<<DateEntrySelected>>", self.on_date_change) 
        
        ctk.CTkLabel(header_frame, text="Select Date:").pack(side="right")

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
            columns=("ID", "Name", "Room", "Status"),
            show="headings",
            yscrollcommand=scrollbar.set
        )
        scrollbar.configure(command=self.tree.yview)
        
        self.tree.heading("ID", text="Student ID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Room", text="Room No")
        self.tree.heading("Status", text="Status")
        
        self.tree.column("ID", width=100, anchor="w")
        self.tree.column("Name", width=200, anchor="w")
        self.tree.column("Room", width=100, anchor="center")
        self.tree.column("Status", width=100, anchor="center")

        scrollbar.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)

        # Cấu hình màu sắc
        self.tree.tag_configure('Present', foreground='#22c55e') # Màu xanh lá
        self.tree.tag_configure('Absent', foreground='#ef4444') # Màu đỏ
        self.tree.tag_configure('NotMarked', foreground='gray')
        
        self.tree.bind('<Double-1>', self.toggle_attendance)

        self.load_attendance()

    def on_date_change(self, event):
        self.current_date = self.date_entry.get_date().isoformat()
        self.load_attendance()

    def load_attendance(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        self.current_date = self.date_entry.get_date().isoformat()
        attendance_list = self.db.get_attendance_for_date(self.current_date)
        
        for student in attendance_list:
            status = student['status']
            if status == 'Present':
                tags = ('Present',)
            elif status == 'Absent':
                tags = ('Absent',)
            else:
                status = "Not Marked" 
                tags = ('NotMarked',)
                
            self.tree.insert("", "end", iid=student['student_id'], values=(
                student['student_id'],
                student['name'],
                student['room_no'],
                status
            ), tags=tags)

    def toggle_attendance(self, event):
        selected_item_id = self.tree.focus() 
        if not selected_item_id:
            return
            
        student_id = selected_item_id
        current_values = self.tree.item(selected_item_id, 'values')
        current_status = current_values[3] 
        
        new_status = 'Present'
        if current_status == 'Present':
            new_status = 'Absent'
        
        success, message = self.db.mark_attendance(student_id, self.current_date, new_status)
        
        if success:
            new_tags = (new_status,)
            self.tree.item(selected_item_id, values=(
                current_values[0],
                current_values[1],
                current_values[2],
                new_status
            ), tags=new_tags)
        else:
            messagebox.showerror("Error", message)

    def mark_all_present(self):
        self.current_date = self.date_entry.get_date().isoformat()
        
        if not messagebox.askyesno("Confirm", f"This will mark ALL students as 'Present' for {self.current_date}.\nThis will overwrite any 'Absent' marks.\n\nContinue?"):
            return
            
        success, message = self.db.mark_all_present(self.current_date)
        
        if success:
            messagebox.showinfo("Success", message)
            self.load_attendance() 
        else:
            messagebox.showerror("Error", message)