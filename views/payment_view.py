import customtkinter as ctk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry 
from utils import apply_treeview_style # <--- IMPORT MỚI

class PaymentView(ctk.CTkFrame):
    """
    Giao diện Quản lý Thanh toán (Payment Management).
    """
    
    def __init__(self, master, db):
        super().__init__(master, fg_color="transparent")
        self.db = db

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1) 
        self.grid_rowconfigure(4, weight=2) 

        # --- 1. Frame Tiêu đề và Nút ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="new", padx=10, pady=(0, 10))
        
        title = ctk.CTkLabel(header_frame, text="💳 Payment Management", font=ctk.CTkFont(size=20, weight="bold"))
        title.pack(side="left")
        
        add_button = ctk.CTkButton(header_frame, text="+ Add Payment", command=self.open_add_payment_popup)
        add_button.pack(side="right")
        
        refresh_button = ctk.CTkButton(header_frame, text="Refresh", command=self.load_payments)
        refresh_button.pack(side="right", padx=10)

        # --- 2. Bảng Tóm tắt Công nợ (Due Summary) ---
        due_label = ctk.CTkLabel(self, text="Current Month's Due Summary", font=ctk.CTkFont(size=16, weight="bold"))
        due_label.grid(row=1, column=0, sticky="w", padx=10, pady=(5, 5))

        due_frame, self.tree_due = self.create_treeview(
            columns=("Student", "Room", "Rent", "Paid", "Due", "Email"),
            headings=("Student Name", "Room", "Rent (₹)", "Paid (₹)", "Due (₹)", "Email")
        )
        due_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 10))
        
        self.tree_due.column("Rent", width=100, anchor="e")
        self.tree_due.column("Paid", width=100, anchor="e")
        self.tree_due.column("Due", width=100, anchor="e")
        self.tree_due.column("Email", width=200, anchor="w")
        
        # --- 3. Bảng Lịch sử Thanh toán (Payment History) ---
        history_label = ctk.CTkLabel(self, text="All Payments History", font=ctk.CTkFont(size=16, weight="bold"))
        history_label.grid(row=3, column=0, sticky="w", padx=10, pady=(10, 5))

        payments_frame, self.tree_payments = self.create_treeview(
            columns=("ID", "Student", "Amount", "Date", "Method"),
            headings=("Payment ID", "Student Name", "Amount (₹)", "Payment Date", "Method")
        )
        payments_frame.grid(row=4, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.tree_payments.column("ID", width=80, anchor="center")
        self.tree_payments.column("Amount", width=100, anchor="e")
        self.tree_payments.column("Method", width=100, anchor="center")

        self.load_payments()

    def create_treeview(self, columns, headings):
        """Hàm trợ giúp tạo Treeview với style."""
        
        # --- THAY THẾ KHỐI STYLE CŨ BẰNG HÀM NÀY ---
        apply_treeview_style()
        # ---------------------------------------------
        
        table_frame = ctk.CTkFrame(self, fg_color="transparent")
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical")
        tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            yscrollcommand=scrollbar.set
        )
        scrollbar.configure(command=tree.yview)

        for col, heading in zip(columns, headings):
            tree.heading(col, text=heading)
            tree.column(col, width=150, anchor="w") 

        scrollbar.pack(side="right", fill="y")
        tree.pack(side="left", fill="both", expand=True)
        
        return table_frame, tree 

    def load_payments(self):
        """Tải và tải lại tất cả dữ liệu cho cả hai bảng."""
        for item in self.tree_due.get_children():
            self.tree_due.delete(item)
            
        due_list = self.db.get_due_summary()
        for item in due_list:
            due_amount = item['due_amount']
            tags = ()
            if due_amount > 0:
                tags = ('due',)
                
            self.tree_due.insert("", "end", values=(
                item['name'],
                item['room_no'],
                f"{item['rent']:.2f}",
                f"{item['total_paid']:.2f}",
                f"{due_amount:.2f}",
                item['email']
            ), tags=tags)
        
        self.tree_due.tag_configure('due', foreground='red')

        for item in self.tree_payments.get_children():
            self.tree_payments.delete(item)
            
        payment_list = self.db.get_all_payments()
        for item in payment_list:
            self.tree_payments.insert("", "end", values=(
                f"PAY{item['payment_id']:04d}",
                item['name'],
                f"{item['amount']:.2f}",
                item['payment_date'],
                item['method']
            ))

    def open_add_payment_popup(self):
        """Mở pop-up để thêm thanh toán mới."""
        popup = AddPaymentPopup(self, self.db)
        self.wait_window(popup)
        self.load_payments() 

# (Class AddPaymentPopup giữ nguyên không đổi)
# ... (Bạn có thể giữ nguyên class này như trong file cũ)
class AddPaymentPopup(ctk.CTkToplevel):
    
    def __init__(self, master, db):
        super().__init__(master)
        self.db = db
        self.student_map = {} 

        self.title("Add New Payment")
        self.geometry("400x450")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        main_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(main_frame, text="Select Student:").grid(row=0, column=0, sticky="w", padx=10, pady=10)
        self.student_var = ctk.StringVar(value="Select Student")
        self.student_menu = ctk.CTkComboBox(main_frame, variable=self.student_var)
        self.student_menu.grid(row=0, column=1, sticky="ew", padx=10, pady=10)
        self.load_student_options()

        ctk.CTkLabel(main_frame, text="Amount (₹):").grid(row=1, column=0, sticky="w", padx=10, pady=10)
        self.amount_entry = ctk.CTkEntry(main_frame)
        self.amount_entry.grid(row=1, column=1, sticky="ew", padx=10, pady=10)

        ctk.CTkLabel(main_frame, text="Payment Date:").grid(row=2, column=0, sticky="w", padx=10, pady=10)
        self.date_entry = DateEntry(main_frame, date_pattern='yyyy-mm-dd')
        self.date_entry.grid(row=2, column=1, sticky="w", padx=10, pady=10) 

        ctk.CTkLabel(main_frame, text="Payment Method:").grid(row=3, column=0, sticky="w", padx=10, pady=10)
        self.method_var = ctk.StringVar(value="Cash")
        self.method_menu = ctk.CTkComboBox(main_frame, variable=self.method_var, values=["Cash", "UPI", "Card", "Other"])
        self.method_menu.grid(row=3, column=1, sticky="ew", padx=10, pady=10)
        
        self.message_label = ctk.CTkLabel(main_frame, text="", text_color="red")
        self.message_label.grid(row=4, column=0, columnspan=2, pady=(10, 0))

        save_button = ctk.CTkButton(main_frame, text="Save Payment", command=self.save_payment)
        save_button.grid(row=5, column=0, columnspan=2, pady=20)

    def load_student_options(self):
        students = self.db.get_student_list_for_payments()
        if not students:
            self.student_menu.configure(values=["No Students Found"])
            return
            
        student_names = []
        for student in students:
            display_name = f"{student['name']} ({student['student_id']})"
            student_names.append(display_name)
            self.student_map[display_name] = student['student_id']
            
        self.student_menu.configure(values=student_names)
        self.student_var.set(student_names[0]) 

    def save_payment(self):
        try:
            display_name = self.student_var.get()
            student_id = self.student_map.get(display_name)
            amount = float(self.amount_entry.get())
            payment_date = self.date_entry.get_date()
            method = self.method_var.get()

            if not student_id or display_name == "No Students Found":
                self.message_label.configure(text="Please select a valid student.")
                return
            if amount <= 0:
                 self.message_label.configure(text="Amount must be a positive number.")
                 return
                 
        except ValueError:
            self.message_label.configure(text="Amount must be a valid number (e.g., 4500.00).")
            return
            
        success, message = self.db.add_payment(student_id, amount, payment_date, method)
        
        if success:
            messagebox.showinfo("Success", message, parent=self)
            self.destroy()
        else:
            self.message_label.configure(text=message)