import customtkinter as ctk
from tkinter import ttk

def apply_treeview_style():
    """
    Tạo style cho ttk.Treeview để phù hợp với theme Sáng/Tối của CustomTkinter.
    """
    style = ttk.Style()
    style.theme_use("default")
    
    current_mode = ctk.get_appearance_mode()
    
    # Lấy màu theme (ví dụ: "blue", "green")
    # Chúng ta sẽ lấy màu của nút bấm
    theme_color = ctk.ThemeManager.theme["CTkButton"]["fg_color"]
    if isinstance(theme_color, (list, tuple)):
        theme_color = theme_color[1] # Lấy màu cho dark mode (hoặc light)

    if current_mode == "Dark":
        # --- Cấu hình Giao diện Tối ---
        style.configure("Treeview",
                        background="#2A2D2E",
                        foreground="#DCE4EE",
                        rowheight=25,
                        fieldbackground="#2A2D2E",
                        bordercolor="#2A2D2E",
                        borderwidth=0)
        style.map('Treeview', 
                  background=[('selected', '#2A2D2E')], 
                  foreground=[('selected', theme_color)])
        
        style.configure("Treeview.Heading",
                        background="#2A2D2E",
                        foreground="#DCE4EE",
                        font=('Calibri', 12, 'bold'),
                        bordercolor="#2A2D2E",
                        borderwidth=0)
    else:
        # --- Cấu hình Giao diện Sáng ---
        style.configure("Treeview",
                        background="#F5F5F5",       # Nền sáng
                        foreground="#1A1A1A",       # Chữ đen
                        rowheight=25,
                        fieldbackground="#F5F5F5",
                        bordercolor="#F5F5F5",
                        borderwidth=0)
        style.map('Treeview', 
                  background=[('selected', theme_color)], # Màu theme
                  foreground=[('selected', 'white')])    # Chữ trắng
        
        style.configure("Treeview.Heading",
                        background="#E0E0E0",       # Nền xám nhạt
                        foreground="#1A1A1A",       # Chữ đen
                        font=('Calibri', 12, 'bold'),
                        bordercolor="#E0E0E0",
                        borderwidth=0)