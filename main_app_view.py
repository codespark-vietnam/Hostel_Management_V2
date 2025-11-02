import customtkinter as ctk
# Import tất cả 7 view của chúng ta từ thư mục 'views'
from views.dashboard_view import DashboardView 
from views.staff_view import StaffView
from views.room_view import RoomView 
from views.student_view import StudentView
from views.payment_view import PaymentView
from views.attendance_view import AttendanceView
from views.report_view import ReportView 

class MainAppView(ctk.CTk):
    """
    Tạo cửa sổ ứng dụng chính sau khi đăng nhập thành công.
    Cửa sổ này chứa sidebar điều hướng và các frame nội dung.
    """

    def __init__(self, db, user, on_logout=None):
        super().__init__()

        self.db = db
        self.current_user = user
        self.on_logout = on_logout # Callback function để hiển thị lại cửa sổ login

        # --- Cấu hình cửa sổ ---
        self.title("Hostel Management System V2.0")
        self.geometry("1100x720") # Kích thước cửa sổ
        self.minsize(900, 600) # Kích thước tối thiểu

        # --- Cấu hình Layout (Sidebar + Main Content) ---
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- 1. Tạo Sidebar Frame ---
        self.sidebar_frame = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(8, weight=1) 

        # Tiêu đề Sidebar
        self.sidebar_title = ctk.CTkLabel(self.sidebar_frame, 
                                          text="🏨 Hostel System", 
                                          font=ctk.CTkFont(size=20, weight="bold"))
        self.sidebar_title.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Các nút điều hướng
        self.nav_buttons = {}
        nav_items = [
            ("Dashboard", "📊"),
            ("Staff", "👥"),
            ("Rooms", "🚪"),
            ("Students", "🧑‍🎓"),
            ("Payments", "💳"),
            ("Attendance", "✅"),
            ("Reports", "📈")
        ]

        for i, (name, emoji) in enumerate(nav_items, start=1):
            button = ctk.CTkButton(self.sidebar_frame, 
                                   text=f" {emoji}  {name}",
                                   height=40,
                                   corner_radius=10,
                                   anchor="w", 
                                   font=ctk.CTkFont(size=14),
                                   command=lambda n=name: self.show_frame(n))
            button.grid(row=i, column=0, padx=20, pady=5, sticky="ew")
            self.nav_buttons[name] = button

        # --- Thông tin User & Logout (ở cuối sidebar) ---
        user_role = self.current_user.get('role', 'N/A')
        self.user_label = ctk.CTkLabel(self.sidebar_frame, 
                                       text=f"👤 {self.current_user['username']} ({user_role.capitalize()})",
                                       font=ctk.CTkFont(size=14))
        self.user_label.grid(row=9, column=0, padx=20, pady=(10, 5), sticky="w")

        self.logout_button = ctk.CTkButton(self.sidebar_frame, 
                                           text="Logout", 
                                           fg_color="transparent",
                                           text_color=("gray10", "#DCE4EE"),
                                           hover_color=("#E5E5E5", "#2B2B2B"),
                                           command=self.logout_event)
        self.logout_button.grid(row=10, column=0, padx=20, pady=(0, 20), sticky="w")

        # --- 2. Tạo Frame Nội dung chính ---
        self.main_content_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="transparent")
        self.main_content_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_content_frame.grid_rowconfigure(0, weight=1)
        self.main_content_frame.grid_columnconfigure(0, weight=1)

        # --- 3. Tạo và lưu trữ tất cả các Frame View ---
        self.frames = {}
        
        for (name, emoji) in nav_items:
            
            if name == "Dashboard":
                frame = DashboardView(self.main_content_frame, self.db)
                frame.grid(row=0, column=0, sticky="nsew")
            
            elif name == "Staff":
                frame = StaffView(self.main_content_frame, self.db)
                frame.grid(row=0, column=0, sticky="nsew")

            elif name == "Rooms":
                frame = RoomView(self.main_content_frame, self.db)
                frame.grid(row=0, column=0, sticky="nsew")
                
            elif name == "Students":
                frame = StudentView(self.main_content_frame, self.db)
                frame.grid(row=0, column=0, sticky="nsew")

            elif name == "Payments":
                frame = PaymentView(self.main_content_frame, self.db)
                frame.grid(row=0, column=0, sticky="nsew")
            
            elif name == "Attendance":
                frame = AttendanceView(self.main_content_frame, self.db)
                frame.grid(row=0, column=0, sticky="nsew")

            elif name == "Reports":
                frame = ReportView(self.main_content_frame, self.db)
                frame.grid(row=0, column=0, sticky="nsew")

            else: 
                frame = ctk.CTkFrame(self.main_content_frame, corner_radius=10, fg_color="transparent")
                frame.grid(row=0, column=0, sticky="nsew")
                frame.grid_rowconfigure(0, weight=1)
                frame.grid_columnconfigure(0, weight=1)
                label = ctk.CTkLabel(frame, text=f"{emoji} {name} View\n(Coming Soon)", 
                                     font=ctk.CTkFont(size=24, weight="bold"))
                label.grid(row=0, column=0, sticky="nsew")
                
            self.frames[name] = frame 


        # --- 4. Hiển thị frame mặc định (Dashboard) ---
        self.show_frame("Dashboard")

    def show_frame(self, frame_name):
        """
        Đưa frame được chọn lên trên cùng.
        (Đã xóa bỏ việc tải lại dữ liệu để tránh lag/crash)
        """
        frame = self.frames[frame_name]
        frame.tkraise() # Đưa frame được chọn lên trên cùng
        
        # Cập nhật trạng thái nút
        for name, button in self.nav_buttons.items():
            if name == frame_name:
                button.configure(fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"])
            else:
                button.configure(fg_color="transparent")
        
    def logout_event(self):
        """
        Gọi callback on_logout (nếu có) để chuyển cửa sổ.
        (ĐÃ SỬA LỖI - XÓA self.destroy())
        """
        print("Logout event called")
        if self.on_logout:
            # self.destroy() # <--- ĐÃ XÓA DÒNG NÀY (NGUYÊN NHÂN GÂY LỖI 1)
            self.on_logout() # Chỉ gọi callback, để main.py xử lý