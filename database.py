import mysql.connector
from mysql.connector import Error
import hashlib
from datetime import date 

class DatabaseConnector:
    """
    Quản lý tất cả các kết nối và truy vấn CSDL MySQL.
    """
    
    def __init__(self, host='localhost', user='root', password='', database='hostel_v2'):
        self.host = host
        self.user = user
        self.password = password # <--- (Hãy chắc chắn bạn đã đặt mật khẩu ở đây)
        self.database = database
        self.conn = None
        self.cursor = None

        try:
            self.conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            if self.conn.is_connected():
                print("Kết nối MySQL thành công!")
                self.cursor = self.conn.cursor(dictionary=True)
                self.create_tables() 
                
        except Error as e:
            print(f"Lỗi khi kết nối MySQL: {e}")
            self.conn = None 

    def _hash_password(self, password):
        sha256 = hashlib.sha256()
        sha256.update(password.encode('utf-8'))
        return sha256.hexdigest()

    def create_tables(self):
        if not self.conn:
            return
        try:
            # 1. Bảng Users
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    role ENUM('admin', 'staff') DEFAULT 'staff',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 2. Bảng Rooms
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS rooms (
                    room_no VARCHAR(10) PRIMARY KEY,
                    room_type VARCHAR(50) NOT NULL,
                    capacity INT NOT NULL,
                    occupied INT DEFAULT 0,
                    rent DECIMAL(10, 2) NOT NULL,
                    status ENUM('Available', 'Full', 'Maintenance') DEFAULT 'Available'
                )
            """)

            # 3. Bảng Students
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS students (
                    student_id VARCHAR(20) PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    gender VARCHAR(10),
                    age INT,
                    email VARCHAR(100) UNIQUE,
                    contact VARCHAR(20),
                    admission_date DATE,
                    room_no VARCHAR(10),
                    FOREIGN KEY (room_no) REFERENCES rooms(room_no) ON DELETE SET NULL
                )
            """)

            # 4. Bảng Payments
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS payments (
                    payment_id INT AUTO_INCREMENT PRIMARY KEY,
                    student_id VARCHAR(20),
                    amount DECIMAL(10, 2) NOT NULL,
                    payment_date DATE NOT NULL,
                    method ENUM('Cash', 'UPI', 'Card', 'Other') DEFAULT 'Cash',
                    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE SET NULL
                )
            """)
            
            # 5. Bảng Attendance
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS attendance (
                    attendance_id INT AUTO_INCREMENT PRIMARY KEY,
                    student_id VARCHAR(20),
                    attendance_date DATE NOT NULL,
                    status ENUM('Present', 'Absent') NOT NULL,
                    UNIQUE KEY (student_id, attendance_date),
                    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
                )
            """)
            
            self.conn.commit()
            print("Tất cả các bảng đã được kiểm tra/tạo thành công.")
        except Error as e:
            print(f"Lỗi khi tạo bảng: {e}")

    # --- Các hàm User (Login/Register) ---

    def register_user(self, username, email, password):
        if not self.conn:
            return False, "Kết nối CSDL thất bại."
        try:
            check_query = "SELECT * FROM users WHERE username = %s OR email = %s"
            self.cursor.execute(check_query, (username, email))
            if self.cursor.fetchone():
                return False, "Tên đăng nhập hoặc Email đã tồn tại."
        except Error as e:
            return False, f"Lỗi CSDL khi kiểm tra: {e}"
        try:
            hashed_password = self._hash_password(password)
            insert_query = "INSERT INTO users (username, email, password, role) VALUES (%s, %s, %s, %s)"
            values = (username, email, hashed_password, 'staff')
            self.cursor.execute(insert_query, values)
            self.conn.commit()
            return True, "Đăng ký thành công!"
        except Error as e:
            self.conn.rollback()
            return False, f"Lỗi CSDL khi đăng ký: {e}"

    def validate_login(self, username, password):
        if not self.conn:
            return False, "Kết nối CSDL thất bại."
        try:
            hashed_password = self._hash_password(password)
            query = "SELECT * FROM users WHERE username = %s AND password = %s"
            self.cursor.execute(query, (username, hashed_password))
            user = self.cursor.fetchone()
            if user:
                return True, user
            else:
                return False, "Sai tên đăng nhập hoặc mật khẩu."
        except Error as e:
            return False, f"Lỗi CSDL khi đăng nhập: {e}"

    # --- Hàm Dashboard ---

    def get_dashboard_stats(self):
        if not self.conn:
            return None
        stats = {
            'total_students': 0, 'total_staff': 0, 'total_rooms': 0,
            'occupied_rooms': 0, 'available_rooms': 0, 'full_rooms': 0,
            'total_revenue': 0.00, 'monthly_revenue': 0.00,
            'present_today': 0, 'absent_today': 0
        }
        try:
            self.cursor.execute("SELECT COUNT(*) as count FROM students")
            stats['total_students'] = self.cursor.fetchone()['count']
            self.cursor.execute("SELECT COUNT(*) as count FROM users WHERE role = 'staff'")
            stats['total_staff'] = self.cursor.fetchone()['count']
            self.cursor.execute("SELECT COUNT(*) as count FROM rooms")
            stats['total_rooms'] = self.cursor.fetchone()['count']
            self.cursor.execute("SELECT COUNT(*) as count FROM rooms WHERE occupied > 0")
            stats['occupied_rooms'] = self.cursor.fetchone()['count']
            self.cursor.execute("SELECT COUNT(*) as count FROM rooms WHERE status = 'Available'")
            stats['available_rooms'] = self.cursor.fetchone()['count']
            self.cursor.execute("SELECT COUNT(*) as count FROM rooms WHERE status = 'Full'")
            stats['full_rooms'] = self.cursor.fetchone()['count']
            self.cursor.execute("SELECT SUM(amount) as total FROM payments")
            total_rev = self.cursor.fetchone()['total']
            stats['total_revenue'] = total_rev if total_rev else 0.00
            self.cursor.execute(
                "SELECT SUM(amount) as total FROM payments WHERE YEAR(payment_date) = YEAR(CURDATE()) AND MONTH(payment_date) = MONTH(CURDATE())"
            )
            monthly_rev = self.cursor.fetchone()['total']
            stats['monthly_revenue'] = monthly_rev if monthly_rev else 0.00
            today = date.today().isoformat()
            self.cursor.execute("SELECT COUNT(*) as count FROM attendance WHERE attendance_date = %s AND status = 'Present'", (today,))
            stats['present_today'] = self.cursor.fetchone()['count']
            self.cursor.execute("SELECT COUNT(*) as count FROM attendance WHERE attendance_date = %s AND status = 'Absent'", (today,))
            stats['absent_today'] = self.cursor.fetchone()['count']
            return stats
        except Error as e:
            print(f"Lỗi khi lấy số liệu Dashboard: {e}")
            return stats 

    # --- Các hàm Staff Management ---

    def get_all_users(self):
        if not self.conn: return []
        try:
            query = "SELECT id, username, email, role, created_at FROM users"
            self.cursor.execute(query)
            return self.cursor.fetchall() 
        except Error as e:
            print(f"Lỗi khi lấy danh sách nhân viên: {e}")
            return []

    def delete_user(self, user_id):
        if not self.conn: return False, "Kết nối CSDL thất bại."
        try:
            check_query = "SELECT role FROM users WHERE id = %s"
            self.cursor.execute(check_query, (user_id,))
            user = self.cursor.fetchone()
            if user and user['role'] == 'admin':
                return False, "Không thể xóa tài khoản Admin."
            delete_query = "DELETE FROM users WHERE id = %s"
            self.cursor.execute(delete_query, (user_id,))
            self.conn.commit()
            if self.cursor.rowcount > 0:
                return True, "Nhân viên đã được xóa."
            else:
                return False, "Không tìm thấy nhân viên."
        except Error as e:
            self.conn.rollback()
            return False, f"Lỗi CSDL khi xóa: {e}"

    def reset_user_password(self, user_id, new_password):
        if not self.conn: return False, "Kết nối CSDL thất bại."
        try:
            hashed_password = self._hash_password(new_password)
            query = "UPDATE users SET password = %s WHERE id = %s"
            self.cursor.execute(query, (hashed_password, user_id))
            self.conn.commit()
            return True, "Mật khẩu đã được cập nhật."
        except Error as e:
            self.conn.rollback()
            return False, f"Lỗi CSDL khi cập nhật: {e}"

    # --- Các hàm Room Management ---

    def get_room_types(self):
        if not self.conn: return []
        try:
            query = "SELECT DISTINCT room_type FROM rooms ORDER BY room_type"
            self.cursor.execute(query)
            return [row['room_type'] for row in self.cursor.fetchall()]
        except Error as e:
            print(f"Lỗi khi lấy loại phòng: {e}")
            return []

    def get_all_rooms(self, filter_type=None):
        if not self.conn: return []
        try:
            if filter_type and filter_type != "All":
                query = "SELECT * FROM rooms WHERE room_type = %s ORDER BY room_no"
                self.cursor.execute(query, (filter_type,))
            else:
                query = "SELECT * FROM rooms ORDER BY room_no"
                self.cursor.execute(query)
            return self.cursor.fetchall()
        except Error as e:
            print(f"Lỗi khi lấy danh sách phòng: {e}")
            return []

    def get_room_by_no(self, room_no):
        if not self.conn: return None
        try:
            query = "SELECT * FROM rooms WHERE room_no = %s"
            self.cursor.execute(query, (room_no,))
            return self.cursor.fetchone() 
        except Error as e:
            print(f"Lỗi khi lấy phòng: {e}")
            return None

    def add_room(self, room_no, room_type, capacity, rent, status):
        if not self.conn: return False, "Kết nối CSDL thất bại."
        try:
            if self.get_room_by_no(room_no):
                return False, f"Số phòng '{room_no}' đã tồn tại."
            query = "INSERT INTO rooms (room_no, room_type, capacity, rent, status, occupied) VALUES (%s, %s, %s, %s, %s, 0)"
            self.cursor.execute(query, (room_no, room_type, capacity, rent, status))
            self.conn.commit()
            return True, "Phòng đã được thêm thành công."
        except Error as e:
            self.conn.rollback()
            return False, f"Lỗi CSDL khi thêm phòng: {e}"

    def update_room(self, room_no, room_type, capacity, rent, status):
        if not self.conn: return False, "Kết nối CSDL thất bại."
        try:
            query = "UPDATE rooms SET room_type = %s, capacity = %s, rent = %s, status = %s WHERE room_no = %s"
            self.cursor.execute(query, (room_type, capacity, rent, status, room_no))
            self.conn.commit()
            return True, "Thông tin phòng đã được cập nhật."
        except Error as e:
            self.conn.rollback()
            return False, f"Lỗi CSDL khi cập nhật: {e}"

    def delete_room(self, room_no):
        if not self.conn: return False, "Kết nối CSDL thất bại."
        try:
            room = self.get_room_by_no(room_no)
            if room and room['occupied'] > 0:
                return False, "Không thể xóa phòng đang có sinh viên."
            query = "DELETE FROM rooms WHERE room_no = %s"
            self.cursor.execute(query, (room_no,))
            self.conn.commit()
            if self.cursor.rowcount > 0:
                return True, "Phòng đã được xóa."
            else:
                return False, "Không tìm thấy phòng."
        except Error as e:
            self.conn.rollback()
            return False, f"Lỗi CSDL khi xóa: {e}"

    # --- Các hàm Student Management ---

    def get_available_rooms(self):
        if not self.conn: return []
        try:
            query = "SELECT room_no FROM rooms WHERE status = 'Available' ORDER BY room_no"
            self.cursor.execute(query)
            return [row['room_no'] for row in self.cursor.fetchall()]
        except Error as e:
            print(f"Lỗi khi lấy phòng còn trống: {e}")
            return []

    def _update_room_occupancy(self, room_no, change):
        if not room_no: return
        try:
            query_update = "UPDATE rooms SET occupied = occupied + (%s) WHERE room_no = %s"
            self.cursor.execute(query_update, (change, room_no))
            room = self.get_room_by_no(room_no)
            if not room: return
            new_status = room['status']
            if room['occupied'] >= room['capacity']:
                new_status = 'Full'
            elif room['occupied'] < room['capacity']:
                if room['status'] != 'Maintenance':
                    new_status = 'Available'
            query_status = "UPDATE rooms SET status = %s WHERE room_no = %s"
            self.cursor.execute(query_status, (new_status, room_no))
            self.conn.commit()
        except Error as e:
            print(f"Lỗi khi cập nhật số lượng phòng: {e}")
            self.conn.rollback()

    def get_all_students(self, search_term=None):
        if not self.conn: return []
        try:
            if search_term:
                query = "SELECT * FROM students WHERE name LIKE %s OR student_id LIKE %s ORDER BY student_id"
                like_term = f"%{search_term}%"
                self.cursor.execute(query, (like_term, like_term))
            else:
                query = "SELECT * FROM students ORDER BY student_id"
                self.cursor.execute(query)
            return self.cursor.fetchall()
        except Error as e:
            print(f"Lỗi khi lấy danh sách sinh viên: {e}")
            return []

    def get_student_by_id(self, student_id):
        if not self.conn: return None
        try:
            query = "SELECT * FROM students WHERE student_id = %s"
            self.cursor.execute(query, (student_id,))
            return self.cursor.fetchone()
        except Error as e:
            print(f"Lỗi khi lấy sinh viên: {e}")
            return None

    def add_student(self, data):
        if not self.conn: return False, "Kết nối CSDL thất bại."
        try:
            if self.get_student_by_id(data['student_id']):
                return False, f"ID sinh viên '{data['student_id']}' đã tồn tại."
            query = "INSERT INTO students (student_id, name, gender, age, email, contact, admission_date, room_no) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            self.cursor.execute(query, (data['student_id'], data['name'], data['gender'], data['age'], data['email'], data['contact'], data['admission_date'], data['room_no']))
            self._update_room_occupancy(data['room_no'], change=1)
            return True, "Thêm sinh viên thành công."
        except Error as e:
            self.conn.rollback()
            return False, f"Lỗi CSDL khi thêm sinh viên: {e}"

    def update_student(self, old_student_id, data, old_room_no):
        if not self.conn: return False, "Kết nối CSDL thất bại."
        try:
            if old_student_id != data['student_id']:
                if self.get_student_by_id(data['student_id']):
                    return False, f"ID sinh viên mới '{data['student_id']}' đã tồn tại."
            query = "UPDATE students SET student_id = %s, name = %s, gender = %s, age = %s, email = %s, contact = %s, admission_date = %s, room_no = %s WHERE student_id = %s"
            self.cursor.execute(query, (data['student_id'], data['name'], data['gender'], data['age'], data['email'], data['contact'], data['admission_date'], data['room_no'], old_student_id))
            new_room_no = data['room_no']
            if old_room_no != new_room_no:
                self._update_room_occupancy(old_room_no, change=-1)
                self._update_room_occupancy(new_room_no, change=1)
            return True, "Cập nhật sinh viên thành công."
        except Error as e:
            self.conn.rollback()
            return False, f"Lỗi CSDL khi cập nhật sinh viên: {e}"

    def delete_student(self, student_id):
        if not self.conn: return False, "Kết nối CSDL thất bại."
        try:
            student = self.get_student_by_id(student_id)
            if not student:
                return False, "Không tìm thấy sinh viên."
            room_no = student['room_no']
            query = "DELETE FROM students WHERE student_id = %s"
            self.cursor.execute(query, (student_id,))
            self._update_room_occupancy(room_no, change=-1)
            return True, "Xóa sinh viên thành công."
        except Error as e:
            self.conn.rollback()
            if e.errno == 1451: 
                return False, "Không thể xóa: Sinh viên này đã có thanh toán (payment) trong hệ thống."
            return False, f"Lỗi CSDL khi xóa sinh viên: {e}"

    # --- Các hàm Payment Management ---

    def get_student_list_for_payments(self):
        if not self.conn: return []
        try:
            query = "SELECT student_id, name FROM students ORDER BY name"
            self.cursor.execute(query)
            return self.cursor.fetchall() 
        except Error as e:
            print(f"Lỗi khi lấy danh sách sinh viên: {e}")
            return []

    def add_payment(self, student_id, amount, payment_date, method):
        if not self.conn: return False, "Kết nối CSDL thất bại."
        try:
            query = "INSERT INTO payments (student_id, amount, payment_date, method) VALUES (%s, %s, %s, %s)"
            self.cursor.execute(query, (student_id, amount, payment_date, method))
            self.conn.commit()
            return True, "Thêm thanh toán thành công."
        except Error as e:
            self.conn.rollback()
            return False, f"Lỗi CSDL khi thêm thanh toán: {e}"

    def get_all_payments(self):
        if not self.conn: return []
        try:
            query = "SELECT p.payment_id, s.name, p.amount, p.payment_date, p.method FROM payments p JOIN students s ON p.student_id = s.student_id ORDER BY p.payment_date DESC, p.payment_id DESC"
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Error as e:
            print(f"Lỗi khi lấy lịch sử thanh toán: {e}")
            return []
            
    def get_due_summary(self):
        if not self.conn: return []
        try:
            query = "SELECT s.student_id, s.name, s.email, r.room_no, r.rent, COALESCE(SUM(p.amount), 0) AS total_paid, (r.rent - COALESCE(SUM(p.amount), 0)) AS due_amount FROM students s JOIN rooms r ON s.room_no = r.room_no LEFT JOIN payments p ON s.student_id = p.student_id AND YEAR(p.payment_date) = YEAR(CURDATE()) AND MONTH(p.payment_date) = MONTH(CURDATE()) GROUP BY s.student_id, s.name, s.email, r.room_no, r.rent ORDER BY due_amount DESC, s.name"
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Error as e:
            print(f"Lỗi khi lấy tóm tắt công nợ: {e}")
            return []

    # --- Các hàm Attendance Management ---

    def get_attendance_for_date(self, attendance_date):
        if not self.conn: return []
        try:
            query = "SELECT s.student_id, s.name, s.room_no, a.status FROM students s LEFT JOIN attendance a ON s.student_id = a.student_id AND a.attendance_date = %s ORDER BY s.room_no, s.name"
            self.cursor.execute(query, (attendance_date,))
            return self.cursor.fetchall()
        except Error as e:
            print(f"Lỗi khi lấy dữ liệu điểm danh: {e}")
            return []

    def mark_attendance(self, student_id, attendance_date, status):
        if not self.conn: return False, "Kết nối CSDL thất bại."
        try:
            query = "INSERT INTO attendance (student_id, attendance_date, status) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE status = %s"
            self.cursor.execute(query, (student_id, attendance_date, status, status))
            self.conn.commit()
            return True, "Đã cập nhật điểm danh."
        except Error as e:
            self.conn.rollback()
            return False, f"Lỗi CSDL khi điểm danh: {e}"

    def mark_all_present(self, attendance_date):
        if not self.conn: return False, "Kết nối CSDL thất bại."
        try:
            self.cursor.execute("SELECT student_id FROM students")
            students = self.cursor.fetchall()
            if not students:
                return True, "Không có sinh viên nào để điểm danh."
            query = "REPLACE INTO attendance (student_id, attendance_date, status) VALUES (%s, %s, %s)"
            data_to_insert = [(student['student_id'], attendance_date, 'Present') for student in students]
            self.cursor.executemany(query, data_to_insert)
            self.conn.commit()
            return True, f"Đã điểm danh 'Present' cho {len(students)} sinh viên."
        except Error as e:
            self.conn.rollback()
            return False, f"Lỗi CSDL khi điểm danh hàng loạt: {e}"

    # --- Các hàm Report ---

    def get_attendance_report(self, start_date, end_date):
        if not self.conn: return []
        try:
            query = "SELECT s.student_id, s.name, s.room_no, a.attendance_date, a.status FROM attendance a JOIN students s ON s.student_id = a.student_id WHERE a.attendance_date BETWEEN %s AND %s ORDER BY a.attendance_date, s.name"
            self.cursor.execute(query, (start_date, end_date))
            return self.cursor.fetchall()
        except Error as e:
            print(f"Lỗi khi lấy báo cáo điểm danh: {e}")
            return []

    # --- HÀM ĐÓNG (NGUYÊN NHÂN GÂY LỖI 2) ---
    
    def close(self):
        """Đóng kết nối CSDL."""
        if self.conn and self.conn.is_connected():
            self.cursor.close()
            self.conn.close()
            print("Kết nối MySQL đã đóng.")