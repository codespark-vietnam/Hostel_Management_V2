import customtkinter as ctk
from tkinter import filedialog, messagebox
from tkcalendar import DateEntry
import pandas as pd
from datetime import date

class ReportView(ctk.CTkFrame):
    """
    Giao diện Báo cáo & Phân tích (Reports & Analytics).
    """
    
    def __init__(self, master, db):
        super().__init__(master, fg_color="transparent")
        self.db = db

        # --- Cấu hình Grid ---
        # 2 cột, 3 hàng cho các nút
        self.grid_columnconfigure((0, 1), weight=1, uniform="group1")
        self.grid_rowconfigure((1, 2, 3), weight=1, uniform="group1")

        # --- 1. Frame Tiêu đề ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, columnspan=2, sticky="new", padx=10, pady=(0, 20))
        
        title = ctk.CTkLabel(header_frame, text="📈 Reports & Analytics", font=ctk.CTkFont(size=20, weight="bold"))
        title.pack(side="left")
        
        info = ctk.CTkLabel(self, text="Click a button to generate and save an Excel (.xlsx) report.")
        info.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=(40, 10))

        # --- 2. Các Nút Báo cáo ---
        
        # Hàng 1
        self._create_report_button("🧑‍🎓 Student Report", self.export_student_report, 1, 0)
        self._create_report_button("🚪 Room Report", self.export_room_report, 1, 1)
        
        # Hàng 2
        self._create_report_button("💳 Payment Report", self.export_payment_report, 2, 0)
        self._create_report_button("💰 Due Summary Report", self.export_due_summary_report, 2, 1)
        
        # Hàng 3
        self._create_report_button("✅ Attendance Report", self.open_date_range_popup, 3, 0)
        self._create_report_button("🏨 Room Occupancy Report", self.export_room_occupancy_report, 3, 1)

    def _create_report_button(self, text, command, row, col):
        """Hàm trợ giúp tạo nút bấm."""
        button = ctk.CTkButton(self, text=text, command=command, height=60, font=ctk.CTkFont(size=14, weight="bold"))
        button.grid(row=row, column=col, sticky="nsew", padx=15, pady=15)
        return button

    def _save_to_excel(self, df, filename_prefix):
        """Hàm trợ giúp chung để lưu DataFrame ra Excel."""
        try:
            filename = filedialog.asksaveasfilename(
                initialfile=f"{filename_prefix}_{date.today().isoformat()}.xlsx",
                defaultextension=".xlsx",
                filetypes=[("Excel Files", "*.xlsx"), ("All Files", "*.*")]
            )
            
            if not filename:
                # Người dùng hủy
                return
                
            # Ghi ra file Excel
            df.to_excel(filename, index=False, engine='openpyxl')
            messagebox.showinfo("Success", f"Report saved successfully to:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save report: {e}")

    # --- Các hàm xuất báo cáo ---

    def export_student_report(self):
        data = self.db.get_all_students()
        if not data:
            messagebox.showinfo("No Data", "No student data to export.")
            return
        
        df = pd.DataFrame(data)
        self._save_to_excel(df, "Student_Report")

    def export_room_report(self):
        data = self.db.get_all_rooms()
        if not data:
            messagebox.showinfo("No Data", "No room data to export.")
            return
        
        df = pd.DataFrame(data)
        self._save_to_excel(df, "Room_List_Report")
        
    def export_payment_report(self):
        data = self.db.get_all_payments()
        if not data:
            messagebox.showinfo("No Data", "No payment data to export.")
            return
        
        df = pd.DataFrame(data)
        self._save_to_excel(df, "Payment_History_Report")

    def export_due_summary_report(self):
        data = self.db.get_due_summary()
        if not data:
            messagebox.showinfo("No Data", "No due summary data to export.")
            return
        
        df = pd.DataFrame(data)
        self._save_to_excel(df, "Due_Summary_Report")

    def export_room_occupancy_report(self):
        data = self.db.get_all_rooms()
        if not data:
            messagebox.showinfo("No Data", "No room data to export.")
            return
        
        # Chỉ chọn các cột liên quan
        df = pd.DataFrame(data)
        df_filtered = df[["room_no", "room_type", "capacity", "occupied", "status"]]
        self._save_to_excel(df_filtered, "Room_Occupancy_Report")

    def open_date_range_popup(self):
        """Mở pop-up để chọn khoảng ngày cho Báo cáo Điểm danh."""
        popup = DateRangePopup(self)
        self.wait_window(popup) # Chờ cho đến khi popup đóng
        
        if popup.dates_selected:
            start, end = popup.dates_selected
            self._run_attendance_report(start, end)
            
    def _run_attendance_report(self, start_date, end_date):
        data = self.db.get_attendance_report(start_date, end_date)
        if not data:
            messagebox.showinfo("No Data", f"No attendance data found between {start_date} and {end_date}.")
            return
            
        df = pd.DataFrame(data)
        self._save_to_excel(df, f"Attendance_Report_{start_date}_to_{end_date}")


# --- Class Pop-up (Toplevel) cho Khoảng ngày ---

class DateRangePopup(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.dates_selected = None

        self.title("Select Date Range")
        self.geometry("350x200")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        main_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(main_frame, text="Start Date:").grid(row=0, column=0, sticky="w", padx=10, pady=10)
        self.start_date_entry = DateEntry(main_frame, date_pattern='yyyy-mm-dd')
        self.start_date_entry.grid(row=0, column=1, sticky="ew", padx=10, pady=10)
        
        ctk.CTkLabel(main_frame, text="End Date:").grid(row=1, column=0, sticky="w", padx=10, pady=10)
        self.end_date_entry = DateEntry(main_frame, date_pattern='yyyy-mm-dd')
        self.end_date_entry.grid(row=1, column=1, sticky="ew", padx=10, pady=10)

        generate_button = ctk.CTkButton(main_frame, text="Generate Report", command=self.submit_dates)
        generate_button.grid(row=2, column=0, columnspan=2, pady=20)

    def submit_dates(self):
        start = self.start_date_entry.get_date()
        end = self.end_date_entry.get_date()
        
        if start > end:
            messagebox.showerror("Invalid Range", "Start Date must be before End Date.", parent=self)
            return
            
        self.dates_selected = (start.isoformat(), end.isoformat())
        self.destroy()