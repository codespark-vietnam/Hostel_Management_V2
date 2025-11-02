import customtkinter as ctk

class DashboardView(ctk.CTkFrame):
    """
    A non-mainstream, asymmetrical Dashboard View.
    It features a main "Key Metrics" list and secondary "Mini-Cards".
    """
    
    def __init__(self, master, db):
        super().__init__(master, fg_color="transparent")
        
        self.db = db
        self.stats = {} # To hold the stat values

        # --- Configure Main Grid (1 row, 2 columns) ---
        # Col 0 (Key Metrics) gets 1 part of the width
        # Col 1 (Secondary Stats) gets 2 parts of the width
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(1, weight=1) # Row for content
        self.grid_rowconfigure(0, weight=0) # Row for header

        # --- Header and Refresh Button ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        # Span across both columns (0 and 1)
        header_frame.grid(row=0, column=0, columnspan=2, sticky="new", padx=10, pady=(0, 10))
        
        title = ctk.CTkLabel(header_frame, text="📊 Dashboard Overview", font=ctk.CTkFont(size=20, weight="bold"))
        title.pack(side="left")
        
        refresh_button = ctk.CTkButton(header_frame, text="Refresh", command=self.load_stats)
        refresh_button.pack(side="right")

        # --- 1. Key Metrics Frame (Left Column) ---
        key_metrics_frame = ctk.CTkFrame(self, corner_radius=10)
        key_metrics_frame.grid(row=1, column=0, sticky="nsew", padx=(10, 5), pady=10)
        
        key_metrics_frame.grid_columnconfigure(1, weight=1) # Title label expands
        key_metrics_frame.grid_columnconfigure(2, weight=1) # Value label expands

        # Add a title for this section
        key_title = ctk.CTkLabel(key_metrics_frame, text="Key Metrics", font=ctk.CTkFont(size=16, weight="bold"))
        key_title.grid(row=0, column=0, columnspan=3, padx=20, pady=(15, 10), sticky="w")

        # Create 4 key metric rows
        self.lbl_students_val = self._create_key_metric_row(key_metrics_frame, "🧑‍🎓", "Total Students", 1)
        self.lbl_monthly_rev_val = self._create_key_metric_row(key_metrics_frame, "💳", "This Month's Revenue", 2)
        self.lbl_present_val = self._create_key_metric_row(key_metrics_frame, "👍", "Present Today", 3)
        self.lbl_total_rooms_val = self._create_key_metric_row(key_metrics_frame, "🚪", "Total Rooms", 4)


        # --- 2. Secondary Stats Frame (Right Column) ---
        secondary_frame = ctk.CTkFrame(self, fg_color="transparent")
        secondary_frame.grid(row=1, column=1, sticky="nsew", padx=(5, 10), pady=0)
        secondary_frame.grid_rowconfigure((0, 1), weight=1) # Two rows of mini-cards
        secondary_frame.grid_columnconfigure(0, weight=1)

        # -- 2a. Top Row (Room Status)
        room_stats_frame = ctk.CTkFrame(secondary_frame, corner_radius=10)
        room_stats_frame.grid(row=0, column=0, sticky="nsew", pady=(10, 5))
        room_stats_frame.grid_columnconfigure((0, 1, 2), weight=1) # 3 mini-cards
        
        room_title = ctk.CTkLabel(room_stats_frame, text="Room Status", font=ctk.CTkFont(size=16, weight="bold"))
        room_title.grid(row=0, column=0, columnspan=3, padx=20, pady=(15, 5), sticky="w")

        self.lbl_occupied_val = self._create_mini_card(room_stats_frame, "Occupied", 1, 0, "orange")
        self.lbl_available_val = self._create_mini_card(room_stats_frame, "Available", 1, 1, "green")
        self.lbl_full_rooms_val = self._create_mini_card(room_stats_frame, "Full", 1, 2, "red")

        # -- 2b. Bottom Row (Other Stats)
        other_stats_frame = ctk.CTkFrame(secondary_frame, corner_radius=10)
        other_stats_frame.grid(row=1, column=0, sticky="nsew", pady=(5, 10))
        other_stats_frame.grid_columnconfigure((0, 1, 2), weight=1) # 3 mini-cards

        other_title = ctk.CTkLabel(other_stats_frame, text="Other Statistics", font=ctk.CTkFont(size=16, weight="bold"))
        other_title.grid(row=0, column=0, columnspan=3, padx=20, pady=(15, 5), sticky="w")

        self.lbl_staff_val = self._create_mini_card(other_stats_frame, "Total Staff", 1, 0)
        self.lbl_absent_val = self._create_mini_card(other_stats_frame, "Absent Today", 1, 1, "red")
        self.lbl_revenue_val = self._create_mini_card(other_stats_frame, "Total Revenue", 1, 2)


        # Load data for the first time
        self.load_stats()

    def _create_key_metric_row(self, parent, emoji, title, row):
        """Helper to create a row in the Key Metrics frame."""
        icon = ctk.CTkLabel(parent, text=emoji, font=ctk.CTkFont(size=24))
        icon.grid(row=row, column=0, padx=(20, 10), pady=15)
        
        title_label = ctk.CTkLabel(parent, text=title, font=ctk.CTkFont(size=14))
        title_label.grid(row=row, column=1, padx=10, pady=15, sticky="w")
        
        value_label = ctk.CTkLabel(parent, text="...", font=ctk.CTkFont(size=24, weight="bold"))
        value_label.grid(row=row, column=2, padx=(10, 20), pady=15, sticky="e")
        
        return value_label # Return the label to update its text

    def _create_mini_card(self, parent, title, row, col, color_name=None):
        """Helper to create a small card in the Secondary Stats frame."""
        colors = {
            "green": "#22c55e",
            "red": "#ef4444",
            "orange": "#f97316"
        }
        text_color = colors.get(color_name, "gray")

        # Frame for the mini-card
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=row, column=col, padx=10, pady=(5, 20), sticky="nsw")

        title_label = ctk.CTkLabel(frame, text=title, font=ctk.CTkFont(size=13), text_color="gray")
        title_label.pack(anchor="w")
        
        value_label = ctk.CTkLabel(frame, text="...", font=ctk.CTkFont(size=28, weight="bold"), text_color=text_color)
        value_label.pack(anchor="w", pady=(5, 0))
        
        return value_label # Return the label to update its text

    def load_stats(self):
        """
        Fetch data from the database and update all 10 card labels.
        """
        print("Loading dashboard statistics...")
        self.stats = self.db.get_dashboard_stats()
        
        if not self.stats:
            print("Failed to load statistics.")
            return

        # Update Key Metrics (Left)
        self.lbl_students_val.configure(text=str(self.stats.get('total_students', 0)))
        self.lbl_monthly_rev_val.configure(text=f"₹{self.stats.get('monthly_revenue', 0.00):,.2f}")
        self.lbl_present_val.configure(text=str(self.stats.get('present_today', 0)))
        self.lbl_total_rooms_val.configure(text=str(self.stats.get('total_rooms', 0)))

        # Update Secondary Stats (Right)
        # Room Stats
        self.lbl_occupied_val.configure(text=str(self.stats.get('occupied_rooms', 0)))
        self.lbl_available_val.configure(text=str(self.stats.get('available_rooms', 0)))
        self.lbl_full_rooms_val.configure(text=str(self.stats.get('full_rooms', 0)))
        
        # Other Stats
        self.lbl_staff_val.configure(text=str(self.stats.get('total_staff', 0)))
        self.lbl_absent_val.configure(text=str(self.stats.get('absent_today', 0)))
        self.lbl_revenue_val.configure(text=f"₹{self.stats.get('total_revenue', 0.00):,.0f}") # Shortened
        
        print("Dashboard statistics loaded successfully.")