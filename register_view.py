import customtkinter as ctk

class RegisterView(ctk.CTk):
    """
    Tạo cửa sổ đăng ký.
    """
    
    # CẬP NHẬT: Thêm 'db=None' vào __init__
    def __init__(self, db=None, on_login_click=None):
        super().__init__()

        # --- Lưu các đối tượng ---
        self.db = db # <--- LƯU ĐỐI TƯỢNG DATABASE
        self.on_login_click = on_login_click

        # (Giữ nguyên toàn bộ code giao diện từ self.title đến self.login_button)
        # ...
        # ...
        # --- Cấu hình cửa sổ ---
        self.title("Hostel Management System - Register")
        self.geometry("450x600") 
        self.resizable(False, False)

        # --- Căn giữa cửa sổ ---
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width / 2) - (450 / 2)
        y = (screen_height / 2) - (600 / 2) 
        self.geometry(f'450x600+{int(x)}+{int(y)}')

        # --- Frame chính ---
        main_frame = ctk.CTkFrame(self, corner_radius=15)
        main_frame.pack(padx=30, pady=30, fill="both", expand=True)

        # --- Các Widgets ---
        title_label = ctk.CTkLabel(main_frame, text="📝 Create Account", font=ctk.CTkFont(size=28, weight="bold"))
        title_label.pack(pady=(30, 15))

        subtitle_label = ctk.CTkLabel(main_frame, text="Join our hostel management platform", font=ctk.CTkFont(size=14), text_color="gray60")
        subtitle_label.pack(pady=(0, 30))

        self.username_entry = ctk.CTkEntry(main_frame, width=300, height=40, placeholder_text="Username")
        self.username_entry.pack(pady=12, padx=30)

        self.email_entry = ctk.CTkEntry(main_frame, width=300, height=40, placeholder_text="Email")
        self.email_entry.pack(pady=12, padx=30)

        self.password_entry = ctk.CTkEntry(main_frame, width=300, height=40, placeholder_text="Password", show="*")
        self.password_entry.pack(pady=12, padx=30)

        self.confirm_password_entry = ctk.CTkEntry(main_frame, width=300, height=40, placeholder_text="Confirm Password", show="*")
        self.confirm_password_entry.pack(pady=12, padx=30)

        register_button = ctk.CTkButton(main_frame, text="Register", width=300, height=40, font=ctk.CTkFont(weight="bold"), command=self.register_event)
        register_button.pack(pady=20, padx=30)

        self.message_label = ctk.CTkLabel(main_frame, text="", text_color="red", font=ctk.CTkFont(size=12))
        self.message_label.pack(pady=(0, 10))

        login_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        login_frame.pack(pady=(0, 30))

        login_label = ctk.CTkLabel(login_frame, text="Already have an account?")
        login_label.pack(side="left")

        login_button = ctk.CTkButton(login_frame, text="Login", fg_color="transparent", text_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"][1], hover_color=("#E5E5E5", "#2B2B2B"), command=self.show_login_event) 
        login_button.pack(side="left", padx=5)
        # ...
        # ... (Kết thúc phần giao diện)


    # --- Các hàm xử lý sự kiện ---

    # CẬP NHẬT: Toàn bộ hàm register_event
    def register_event(self):
        username = self.username_entry.get()
        email = self.email_entry.get()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()

        self.message_label.configure(text="", text_color="red") # Đặt lại màu đỏ

        if not username or not email or not password or not confirm_password:
            self.message_label.configure(text="Vui lòng điền đầy đủ thông tin.")
            return

        if password != confirm_password:
            self.message_label.configure(text="Mật khẩu không khớp.")
            return

        # --- SỬ DỤNG DATABASE ---
        if not self.db:
            self.message_label.configure(text="Lỗi: Không tìm thấy kết nối CSDL.")
            return
            
        success, message = self.db.register_user(username, email, password)

        if success:
            self.message_label.configure(text=message, text_color="green")
            print("Registration Successful!")
            # Tự động chuyển về Login sau 2 giây
            self.after(2000, self.show_login_event) 
        else:
            self.message_label.configure(text=message) # Hiển thị lỗi từ CSDL
            print(f"Registration Failed: {message}")


    def show_login_event(self):
        # (Giữ nguyên hàm này)
        if self.on_login_click:
            self.on_login_click() # Báo cho main.py để mở cửa sổ login