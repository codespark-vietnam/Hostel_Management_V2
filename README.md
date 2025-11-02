# Hostel Management System V2.0 (CustomTkinter + MySQL)

A modern Hostel Management System (V2.0) built in Python, featuring a theme-aware (Light/Dark) GUI with CustomTkinter and a MySQL database backend. This full-featured application provides a complete solution for student, room, staff, payment, and attendance management, including an Excel reporting system.

## 📸 Screenshots

<img width="959" height="502" alt="Dashboard" src="https://github.com/user-attachments/assets/919f0f33-ef04-45ee-801f-299536a8a65d" />
<img width="959" height="504" alt="Staff Management" src="https://github.com/user-attachments/assets/f2542f70-89fe-47d2-b830-3e12a045b03a" />
<img width="959" height="504" alt="Room Management" src="https://github.com/user-attachments/assets/4d18a990-5736-41ed-8959-63bd8a803d03" />
<img width="959" height="502" alt="Student Management" src="https://github.com/user-attachments/assets/21ec28b8-fbc3-47dd-bfda-63ac27ab5400" />
<img width="959" height="502" alt="Payment Management" src="https://github.com/user-attachments/assets/dcca219d-503f-490a-881c-1bfee16dbaa3" />
<img width="959" height="502" alt="Attendance Tracking" src="https://github.com/user-attachments/assets/523aa37c-168b-48e8-9843-f38f82f43180" />
<img width="340" height="401" alt="Add/Edit Room Popup" src="https://github.com/user-attachments/assets/93f4ca03-394e-4f13-b312-7fec0e32afb2" />
<img width="345" height="479" alt="Add/Edit Student Popup" src="https://github.com/user-attachments/assets/f4fcbb28-c36c-4feb-a101-944691bbf0a9" />
<img width="959" height="502" alt="Reports" src="https://github.com/user-attachments/assets/dce966bd-599c-4b62-a6d2-5b428fa34b40" />

## ✨ Features

This application features 7 full management modules and a secure authentication system:

* **🔐 Authentication:** Secure Login and Registration system for staff accounts with password hashing (`hashlib`).
* **📊 Dashboard:** An asymmetrical, modern dashboard with 10 key metrics, including student counts, room status, monthly revenue, and daily attendance.
* **👥 Staff Management:** Full CRUD (Create, Read, Update, Delete) operations for staff accounts (Add, Delete, Reset Password).
* **🚪 Room Management:** Full CRUD for rooms (Add, Edit, Delete). Features dynamic status updates (`Available`, `Full`) based on occupancy.
* **🧑‍🎓 Student Management:** Full CRUD for students (Add, Edit, Delete) with a live search bar. Automatically updates room occupancy counts when students are added, moved, or deleted.
* **💳 Payment Management:** A complete payment tracking system. Features a "Current Month's Due Summary" table (auto-calculates rent vs. paid) and a "Full Payment History" table.
* **✅ Attendance Tracking:** A daily attendance module. Allows marking "Present" or "Absent" for all students on a selected date. Features "Mark All Present" and double-click-to-toggle-status.
* **📈 Reporting:** Export data from all major modules (Students, Rooms, Payments, etc.) directly to **Excel (.xlsx)** files for analysis or record-keeping.

## 🛠️ Tech Stack

* **Language:** Python 3.12+
* **GUI:** CustomTkinter (for the modern, themeable UI)
* **Database:** MySQL (connected via `mysql-connector-python`)
* **Excel Reporting:** Pandas & OpenPyXL
* **Data Grids:** `ttk.Treeview` (from built-in Tkinter, styled by `utils.py`)
* **Calendar Widgets:** `tkcalendar`

---

## 🚀 How to Run (Setup Guide)

Follow these steps to get the project running on your local machine.

### Step 1: Environment Setup

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/codespark-vietnam/Hostel_Management_V2.git](https://github.com/codespark-vietnam/Hostel_Management_V2.git)
    cd Hostel_Management_V2
    ```

2.  **Start MySQL Server (XAMPP):**
    * Open your **XAMPP Control Panel**.
    * Click **Start** for both **Apache** and **MySQL**.
    * Click the **Admin** button for MySQL to open `phpMyAdmin`.

3.  **Create the Database:**
    * In `phpMyAdmin`, go to the **SQL** tab.
    * Execute the following command to create the database:

    ```sql
    CREATE DATABASE IF NOT EXISTS hostel_v2;
    ```

    *(Note: You only need to create the database. The Python script (`database.py`) will automatically create all 5 tables (`users`, `rooms`, `students`, `payments`, `attendance`) the first time it runs).*

### Step 2: Create the Configuration File (Critical)

You **must** do this step so the Python code can find your database.

1.  In the project's root folder, create a new file named `config.ini`.
2.  Copy and paste the following content into it:

    **`config.ini`**
    ```ini
    [database]
    host = 127.0.0.1
    user = root
    password = 
    database = hostel_v2
    ```

    *(**Note:** If your XAMPP/MySQL `root` user has a password, add it after `password = `).*

### Step 3: Create `.gitignore` (Protect Credentials)

To ensure you never accidentally commit your `config.ini` file to GitHub:

1.  Create a new file in the root folder named `.gitignore`.
2.  Paste the following content into it:

    **`.gitignore`**
    ```gitignore
    # Configuration files
    config.ini
    
    # Python cache
    __pycache__/
    *.pyc
    
    # Virtual environment
    venv/
    *.env
    ```

### Step 4: Install Dependencies

1.  **Create a Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    ```

2.  **Activate the Environment:**
    * On Windows: `.\venv\Scripts\activate`
    * On macOS/Linux: `source venv/bin/activate`

3.  **Create `requirements.txt`:**
    Create a new file named `requirements.txt` and paste the following:

    **`requirements.txt`**
    ```text
    customtkinter
    mysql-connector-python
    pandas
    openpyxl
    tkcalendar
    ```

4.  **Install the libraries:**
    ```bash
    pip install -r requirements.txt
    ```

### Step 5: Run the Application!

After completing all the steps above, just run the `main.py` file:

```bash
python main.py
