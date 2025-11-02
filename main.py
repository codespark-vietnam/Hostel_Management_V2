import customtkinter as ctk
from login_view import LoginView
from register_view import RegisterView
from database import DatabaseConnector
from main_app_view import MainAppView # Import file chính

class AppController:
    """
    Class chính điều khiển luồng của ứng dụng.
    Quản lý việc chuyển đổi giữa các cửa sổ.
    """
    
    def __init__(self):
        # --- THAY ĐỔI GIAO DIỆN TẠI ĐÂY ---
        ctk.set_appearance_mode("Light")  # <--- ĐÃ THAY ĐỔI TỪ "Dark"
        ctk.set_default_color_theme("green")  # <--- (Tùy chọn) Đổi sang theme "green"
        
        # --- KẾT NỐI DATABASE ---
        self.db = DatabaseConnector() 
        if not self.db.conn:
            print("KHÔNG THỂ KẾT NỐI CSDL. Thoát ứng dụng.")
            return 
        
        self.app = None 
        self.current_user = None 
        self.show_login() 

    def show_login(self):
        if self.app:
            self.app.destroy()
        
        self.current_user = None 
            
        self.app = LoginView(
            db=self.db, 
            on_register_click=self.show_register,  
            on_login_success=self.show_main_app   
        )
        self.app.mainloop()

    def show_register(self):
        if self.app:
            self.app.destroy()
            
        self.app = RegisterView(
            db=self.db, 
            on_login_click=self.show_login 
        )
        self.app.mainloop()

    def show_main_app(self, user_data): 
        if self.app:
            self.app.destroy()
        
        self.current_user = user_data 
        print(f"Login Successful! User: {self.current_user['username']}, Role: {self.current_user['role']}")
        
        # Tạo MainAppView
        self.app = MainAppView(
            db=self.db, 
            user=self.current_user,
            on_logout=self.show_login 
        ) 
        self.app.mainloop()

if __name__ == "__main__":
    controller = AppController()
    # Khi ứng dụng đóng
    if controller.db:
        controller.db.close()
    print("Ứng dụng đã đóng.")