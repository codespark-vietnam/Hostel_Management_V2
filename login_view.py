import customtkinter as ctk

class LoginView(ctk.CTk):
    """
    Tạo cửa sổ Login chính.
    """

    # CẬP NHẬT: Thêm 'db=None' vào __init__
    def __init__(self, db=None, on_register_click=None, on_login_success=None):
        super().__init__()

        # --- Lưu các đối tượng ---
        self.db = db # <--- LƯU ĐỐI TƯỢNG DATABASE
        self.on_register_click = on_register_click
        self.on_login_success = on_login_success

        # (Giữ nguyên toàn bộ code giao diện từ self.title đến self.register_button)
        # ...
        # ...
        # --- Cấu hình cửa sổ chính ---
        self.title("Hostel Management System - Login")
        self.geometry("450x500")
        self.resizable(False, False) 

        # --- Căn giữa cửa sổ ---
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width / 2) - (450 / 2)
        y = (screen_height / 2) - (500 / 2)
        self.geometry(f'450x500+{int(x)}+{int(y)}')

        # --- Tạo frame chính ---
        main_frame = ctk.CTkFrame(self, corner_radius=15)
        main_frame.pack(padx=30, pady=30, fill="both", expand=True)

        # --- Các Widgets bên trong Main Frame ---
        title_label = ctk.CTkLabel(main_frame, text="🏨 Welcome Back!", font=ctk.CTkFont(size=28, weight="bold"))
        title_label.pack(pady=(30, 15))

        subtitle_label = ctk.CTkLabel(main_frame, text="Sign in to manage your hostel", font=ctk.CTkFont(size=14), text_color="gray60")
        subtitle_label.pack(pady=(0, 30))

        self.username_entry = ctk.CTkEntry(main_frame, width=300, height=40, placeholder_text="Username")
        self.username_entry.pack(pady=12, padx=30)

        self.password_entry = ctk.CTkEntry(main_frame, width=300, height=40, placeholder_text="Password", show="*")
        self.password_entry.pack(pady=12, padx=30)
        
        self.message_label = ctk.CTkLabel(main_frame, text="", text_color="red", font=ctk.CTkFont(size=12))
        self.message_label.pack(pady=(5, 0)) 

        forgot_button = ctk.CTkButton(main_frame, text="Forgot Password?", fg_color="transparent", text_color=("gray10", "#DCE4EE"), hover_color=("#E5E5E5", "#2B2B2B"), command=self.forgot_password_event)
        forgot_button.place(x=230, y=280) 

        login_button = ctk.CTkButton(main_frame, text="Login", width=300, height=40, font=ctk.CTkFont(weight="bold"), command=self.login_event)
        login_button.pack(pady=(30, 20), padx=30) 

        register_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        register_frame.pack(pady=(10, 30))

        register_label = ctk.CTkLabel(register_frame, text="Don't have an account?")
        register_label.pack(side="left")

        register_button = ctk.CTkButton(register_frame, text="Register", fg_color="transparent", text_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"][1], hover_color=("#E5E5E5", "#2B2B2B"), command=self.show_register_event)
        register_button.pack(side="left", padx=5)
        # ...
        # ... (Kết thúc phần giao diện)


    # --- Các hàm xử lý sự kiện (Event Handlers) ---
    
    # CẬP NHẬT: Toàn bộ hàm login_event
    def login_event(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        # Xóa thông báo lỗi cũ
        self.message_label.configure(text="")
        
        if not username or not password:
            self.message_label.configure(text="Vui lòng nhập Username và Password")
            return
            
        # --- SỬ DỤNG DATABASE ---
        # (Đảm bảo self.db đã được truyền từ main.py)
        if not self.db:
            self.message_label.configure(text="Lỗi: Không tìm thấy kết nối CSDL.")
            return
            
        success, data_or_message = self.db.validate_login(username, password)
        
        if success:
            print("Login Successful!")
            # Gọi callback on_login_success (nếu nó tồn tại)
            if self.on_login_success:
                # Gửi dữ liệu user (data_or_message) về cho main.py
                self.on_login_success(data_or_message) 
        else:
            # data_or_message lúc này là thông báo lỗi
            self.message_label.configure(text=data_or_message)
            print(f"Login Failed: {data_or_message}")

    def show_register_event(self):
        # (Giữ nguyên hàm này)
        if self.on_register_click:
            self.on_register_click() # Báo cho main.py để mở cửa sổ register

    def forgot_password_event(self):
        # (Giữ nguyên hàm này)
        print("Forgot password button clicked...")