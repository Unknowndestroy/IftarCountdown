import tkinter as tk
import time
import datetime
import json
import urllib.request
from math import sin, pi
from tkinter import simpledialog, messagebox

class IftarCountdown(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # Configure the window as an overlay
        self.title("Iftar Countdown")
        self.geometry("800x600")
        self.configure(bg="white")
        self.attributes("-alpha", 0.1)  # 10% opacity
        
        # Make it frameless and stay on top
        self.overrideredirect(True)  # Remove window decorations
        self.attributes("-topmost", True)  # Stay on top
        
        # Set up variables
        self.blink_state = False
        self.color_toggle = 0
        self.iftar_time = None
        self.is_fullscreen = False
        
        # For window movement
        self.bind("<Button-1>", self.start_move)
        self.bind("<ButtonRelease-1>", self.stop_move)
        self.bind("<B1-Motion>", self.do_move)
        
        # Location selection dialog before showing overlay
        self.withdraw()  # Hide main window initially
        self.location_selection()
        
    def start_move(self, event):
        self.x = event.x
        self.y = event.y
    
    def stop_move(self, event):
        self.x = None
        self.y = None
    
    def do_move(self, event):
        if self.is_fullscreen:
            return  # Don't allow movement in fullscreen mode
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry(f"+{x}+{y}")
        
    def location_selection(self):
        # Create a small dialog window for location selection
        self.dialog = tk.Toplevel(self)
        self.dialog.title("Location Selection")
        self.dialog.geometry("400x300")
        self.dialog.resizable(False, False)
        
        # Center the dialog
        screen_width = self.dialog.winfo_screenwidth()
        screen_height = self.dialog.winfo_screenheight()
        x = (screen_width - 400) // 2
        y = (screen_height - 300) // 2
        self.dialog.geometry(f"400x300+{x}+{y}")
        
        # Create frame for content
        frame = tk.Frame(self.dialog, padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Add labels and entry fields
        tk.Label(frame, text="Please select your location:", font=("Arial", 14, "bold")).pack(pady=(0, 20))
        
        # Auto-detect option
        auto_detect_frame = tk.Frame(frame)
        auto_detect_frame.pack(fill=tk.X, pady=10)
        
        tk.Button(
            auto_detect_frame, 
            text="Auto-detect my location", 
            font=("Arial", 12),
            command=self.auto_detect_location
        ).pack(fill=tk.X)
        
        # Separator
        tk.Frame(frame, height=2, bg="gray").pack(fill=tk.X, pady=15)
        
        # Manual entry option
        manual_frame = tk.Frame(frame)
        manual_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(manual_frame, text="Or enter city name manually:", font=("Arial", 12)).pack(anchor=tk.W)
        
        entry_frame = tk.Frame(manual_frame)
        entry_frame.pack(fill=tk.X, pady=5)
        
        self.city_entry = tk.Entry(entry_frame, font=("Arial", 12))
        self.city_entry.insert(0, "Istanbul")  # Default
        self.city_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        tk.Button(
            entry_frame,
            text="Confirm",
            font=("Arial", 12),
            command=self.manual_location
        ).pack(side=tk.RIGHT)
        
        # Status label
        self.status_label = tk.Label(frame, text="", font=("Arial", 10), fg="gray")
        self.status_label.pack(pady=10)
        
        # Make sure dialog closes properly
        self.dialog.protocol("WM_DELETE_WINDOW", self.on_dialog_close)
        
        # Setup main window while dialog is active
        self.setup_main_window()
        
    def setup_main_window(self):
        # Calculate screen dimensions
        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()
        
        # Position the overlay at the top of the screen but not fullscreen
        self.geometry(f"400x200+{self.screen_width // 2 - 200}+50")
        
        # Create a small frame for countdown at the top center (initially small)
        self.countdown_frame = tk.Frame(self, bg="white", width=150, height=100, bd=2, relief="solid")
        self.countdown_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Prevent the frame from resizing to fit its children
        self.countdown_frame.pack_propagate(False)
        
        # Create loading label
        self.loading_label = tk.Label(
            self.countdown_frame,
            text="Loading...",
            font=("Arial", 12),
            bg="white",
            fg="black"
        )
        self.loading_label.pack(expand=True)
        
        # Create countdown label (hidden initially)
        self.countdown_label = tk.Label(
            self.countdown_frame,
            text="",
            font=("Arial", 24, "bold"),
            bg="white",
            fg="black"
        )
        
        # Create the "Afiyet Olsun" label (hidden initially)
        self.final_label = tk.Label(
            self,
            text="Afiyet Olsun!",
            font=("Arial", 100, "bold"),
            bg="white",
            fg="black"
        )
        
        # Create big countdown label for final countdown (hidden initially)
        self.big_countdown = tk.Label(
            self,
            text="",
            font=("Arial", 200, "bold"),
            bg="white",
            fg="black"
        )
        
        # Add escape key binding to exit
        self.bind("<Escape>", lambda e: self.destroy())
        
        # Add a small close button in the corner
        close_btn = tk.Button(self, text="×", command=self.destroy, font=("Arial", 12), bd=0, bg="white")
        close_btn.place(x=380, y=10)
    
    def on_dialog_close(self):
        # If user closes the dialog without selecting, exit the application
        self.destroy()
    
    def auto_detect_location(self):
        self.status_label.config(text="Detecting location...")
        try:
            # Try to get the user's location based on IP
            location_url = "https://ipapi.co/json/"
            location_response = urllib.request.urlopen(location_url)
            location_data = json.loads(location_response.read().decode())
            
            # Extract city and country
            city = location_data.get('city', 'Istanbul')  # Default to Istanbul if not found
            country = location_data.get('country_name', 'Turkey')
            latitude = location_data.get('latitude')
            longitude = location_data.get('longitude')
            
            self.status_label.config(text=f"Detected: {city}, {country}")
            
            # Use the detected location to get prayer times
            self.city = city
            self.country = country
            self.latitude = latitude
            self.longitude = longitude
            
            # Close dialog and show main window
            self.dialog.destroy()
            self.deiconify()
            
            # Get iftar time
            self.after(100, self.get_iftar_time)
            
        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)}")
            messagebox.showerror("Error", f"Could not detect location: {str(e)}\nPlease enter manually.")
    
    def manual_location(self):
        city = self.city_entry.get().strip()
        if not city:
            messagebox.showerror("Error", "Please enter a city name")
            return
        
        self.status_label.config(text=f"Looking up: {city}")
        
        try:
            # Use geocoding to get coordinates for the city
            geocode_url = f"https://nominatim.openstreetmap.org/search?q={city}&format=json&limit=1"
            headers = {'User-Agent': 'IftarCountdownApp/1.0'}
            req = urllib.request.Request(geocode_url, headers=headers)
            geocode_response = urllib.request.urlopen(req)
            geocode_data = json.loads(geocode_response.read().decode())
            
            if not geocode_data:
                raise Exception(f"City '{city}' not found")
            
            # Extract location information
            self.city = city
            self.country = "Turkey"  # Default to Turkey but could be extracted if needed
            self.latitude = float(geocode_data[0]['lat'])
            self.longitude = float(geocode_data[0]['lon'])
            
            # Close dialog and show main window
            self.dialog.destroy()
            self.deiconify()
            
            # Get iftar time
            self.after(100, self.get_iftar_time)
            
        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)}")
            messagebox.showerror("Error", f"Could not find city: {str(e)}")
    
    def get_iftar_time(self):
        try:
            # Use AladhanAPI to get prayer times (no API key needed)
            date = datetime.date.today()
            prayer_url = f"http://api.aladhan.com/v1/timings/{date.day}-{date.month}-{date.year}?latitude={self.latitude}&longitude={self.longitude}&method=2"
            
            prayer_response = urllib.request.urlopen(prayer_url)
            prayer_data = json.loads(prayer_response.read().decode())
            
            # Get Maghrib (Iftar) time
            iftar_time_str = prayer_data['data']['timings']['Maghrib']
            
            # Parse the time (format: HH:MM)
            hour, minute = map(int, iftar_time_str.split(':'))
            
            # Create datetime object for today's iftar
            iftar_time = datetime.datetime.combine(
                datetime.date.today(),
                datetime.time(hour=hour, minute=minute)
            )
            
            # If iftar time has already passed today, use tomorrow's iftar
            now = datetime.datetime.now()
            if now > iftar_time:
                tomorrow = datetime.date.today() + datetime.timedelta(days=1)
                prayer_url = f"http://api.aladhan.com/v1/timings/{tomorrow.day}-{tomorrow.month}-{tomorrow.year}?latitude={self.latitude}&longitude={self.longitude}&method=2"
                
                prayer_response = urllib.request.urlopen(prayer_url)
                prayer_data = json.loads(prayer_response.read().decode())
                
                iftar_time_str = prayer_data['data']['timings']['Maghrib']
                hour, minute = map(int, iftar_time_str.split(':'))
                
                iftar_time = datetime.datetime.combine(
                    tomorrow,
                    datetime.time(hour=hour, minute=minute)
                )
            
            # Update loading label with information
            self.loading_label.config(
                text=f"Iftar: {hour:02d}:{minute:02d}\n{self.city}"
            )
            
            # Store iftar time
            self.iftar_time = iftar_time
            
            # Start countdown after a brief delay
            self.after(2000, self.start_countdown)
            
        except Exception as e:
            # If there's an error fetching data, use a default time (5 minutes from now for testing)
            self.loading_label.config(
                text=f"Error: Using test time\n(5 min from now)"
            )
            
            # Use a default time for testing (5 minutes from now)
            self.iftar_time = datetime.datetime.now() + datetime.timedelta(minutes=5)
            
            # Start countdown after a brief delay
            self.after(3000, self.start_countdown)
    
    def start_countdown(self):
        # Hide loading label and show countdown
        self.loading_label.pack_forget()
        self.countdown_label.pack(expand=True)
        
        # Start the countdown
        self.update_countdown()
    
    def update_countdown(self):
        now = datetime.datetime.now()
        time_diff = self.iftar_time - now
        
        # If countdown finished
        if time_diff.total_seconds() <= 0:
            self.countdown_finished()
            return
        
        # Calculate hours, minutes, seconds
        hours, remainder = divmod(time_diff.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        # Format the countdown text
        countdown_text = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
        # Set different styles based on time remaining
        remaining_seconds = time_diff.total_seconds()
        
        if remaining_seconds < 5 * 60:  # Less than 5 minutes
            # Only set fullscreen when we're in the final 5 minutes
            if not self.is_fullscreen:
                self.make_fullscreen()
            self.style_less_than_5_minutes(remaining_seconds, countdown_text)
        elif remaining_seconds < 10 * 60:  # Less than 10 minutes
            self.style_less_than_10_minutes(countdown_text)
        elif remaining_seconds < 30 * 60:  # Less than 30 minutes
            self.style_less_than_30_minutes(countdown_text)
        elif remaining_seconds < 60 * 60:  # Less than 1 hour
            self.countdown_label.config(fg="red", text=countdown_text)
        elif remaining_seconds < 5 * 60 * 60:  # Less than 5 hours
            self.countdown_label.config(fg="orange", text=countdown_text)
        else:
            self.countdown_label.config(fg="black", text=countdown_text)
        
        # Schedule the next update (every 100ms for smooth animations)
        self.after(100, self.update_countdown)
    
    def make_fullscreen(self):
        self.is_fullscreen = True
        self.geometry(f"{self.screen_width}x{self.screen_height}+0+0")
        # Ensure it covers the entire screen
        self.overrideredirect(True)
        self.lift()
        self.attributes("-topmost", True)
    
    def style_less_than_30_minutes(self, countdown_text):
        # Swap colors every 4 seconds
        current_second = int(time.time())
        if current_second % 4 < 2:
            self.countdown_label.config(fg="red", text=countdown_text)
        else:
            self.countdown_label.config(fg="orange", text=countdown_text)
    
    def style_less_than_10_minutes(self, countdown_text):
        # Swap colors every 2 seconds and blink
        current_second = int(time.time() * 10)
        
        if current_second % 20 < 10:
            self.countdown_label.config(fg="red", text=countdown_text)
        else:
            self.countdown_label.config(fg="gray", text=countdown_text)
            
        # Blink effect
        if current_second % 10 < 5:
            self.countdown_label.config(text=countdown_text)
        else:
            self.countdown_label.config(text="")
    
    def style_less_than_5_minutes(self, remaining_seconds, countdown_text):
        # Expand the countdown frame when there are less than 5 minutes remaining
        self.countdown_frame.place_forget()  # Remove from current position
        
        # Calculate new size based on remaining time (gradually increases)
        # From 150x100 at 5 minutes to 500x300 at 0 seconds
        remaining_percent = remaining_seconds / (5 * 60)
        width = int(500 - (500 - 150) * remaining_percent)
        height = int(300 - (300 - 100) * remaining_percent)
        
        # Update the frame size and position
        self.countdown_frame.config(width=width, height=height)
        
        # Move to center of screen as time decreases
        rely_position = 0.1 + (0.5 - 0.1) * (1 - remaining_percent)
        self.countdown_frame.place(relx=0.5, rely=rely_position, anchor="center")
        
        # Update font size as frame grows
        font_size = int(24 + (80 - 24) * (1 - remaining_percent))
        
        # For different time ranges within the last 5 minutes
        if remaining_seconds < 10:  # Less than 10 seconds
            self.style_less_than_10_seconds(int(remaining_seconds), countdown_text)
        elif remaining_seconds < 15:  # Less than 15 seconds
            self.style_less_than_15_seconds(countdown_text)
        elif remaining_seconds < 30:  # Less than 30 seconds
            self.style_less_than_30_seconds(countdown_text)
        elif remaining_seconds < 60:  # Less than 1 minute
            self.style_less_than_1_minute(countdown_text)
        else:  # Less than 5 minutes but more than 1 minute
            current_second = int(time.time())
            if current_second % 2 < 1:
                self.countdown_label.config(fg="red", text=countdown_text, font=("Arial", font_size, "bold"))
            else:
                self.countdown_label.config(fg="black", text=countdown_text, font=("Arial", font_size, "bold"))
    
    def style_less_than_1_minute(self, countdown_text):
        # Swap colors every 2 seconds: Black - Purple - Red
        current_second = int(time.time())
        color_cycle = current_second % 6
        
        if color_cycle < 2:
            color = "black"
        elif color_cycle < 4:
            color = "purple"
        else:
            color = "red"
        
        # Animated properties
        self.countdown_label.config(fg=color, text=countdown_text, font=("Arial", 60, "bold"))
        self.attributes("-alpha", 0.3)  # Increase background opacity
    
    def style_less_than_30_seconds(self, countdown_text):
        # Swap colors Red-Black every 0.3 seconds
        current_time = time.time()
        color_toggle = int(current_time / 0.3) % 2
        
        if color_toggle == 0:
            text_color = "red"
        else:
            text_color = "black"
        
        bg_toggle = int(current_time) % 2
        if bg_toggle == 0:
            bg_color = "black"
            self.countdown_frame.config(bg=bg_color)
            self.countdown_label.config(bg=bg_color)
        else:
            bg_color = "white"
            self.countdown_frame.config(bg=bg_color)
            self.countdown_label.config(bg=bg_color)
        
        # Animated properties
        self.countdown_label.config(fg=text_color, text=countdown_text, font=("Arial", 70, "bold"))
        self.attributes("-alpha", 0.5)  # Increase background opacity
    
    def style_less_than_15_seconds(self, countdown_text):
        # Swap colors Red-Black every 0.2 seconds and blink
        current_time = time.time()
        color_toggle = int(current_time / 0.2) % 2
        
        if color_toggle == 0:
            text_color = "red"
        else:
            text_color = "black"
        
        # Blink effect
        blink_toggle = int(current_time * 5) % 2
        
        # Configure countdown label
        self.countdown_label.config(
            fg=text_color,
            text=countdown_text if blink_toggle else "",
            font=("Arial", 75, "bold")
        )
        
        self.attributes("-alpha", 0.7)  # Increase background opacity
    
    def style_less_than_10_seconds(self, seconds_remaining, countdown_text):
        # Hide the countdown frame
        self.countdown_frame.place_forget()
        
        # Show the big countdown in the middle
        self.big_countdown.place(relx=0.5, rely=0.5, anchor="center")
        
        # Set full opacity
        self.attributes("-alpha", 1.0)  # Full opacity
        
        # Alternate between black bg/white text and white bg/black text
        current_time = time.time()
        toggle = int(current_time) % 2
        
        if seconds_remaining <= 5:  # Less than 5 seconds
            if toggle == 0:
                bg_color = "red"
                text_color = "black"
            else:
                bg_color = "black"
                text_color = "red"
        else:  # Between 6-10 seconds
            if toggle == 0:
                bg_color = "black"
                text_color = "white"
            else:
                bg_color = "white"
                text_color = "black"
        
        # Update the big countdown
        self.configure(bg=bg_color)
        self.big_countdown.config(
            text=str(seconds_remaining),
            fg=text_color,
            bg=bg_color,
            font=("Arial", 200, "bold")
        )
    
    def countdown_finished(self):
        # Hide countdown elements
        self.countdown_frame.place_forget()
        self.big_countdown.place_forget()
        
        # Show "Afiyet Olsun!" message
        self.configure(bg="white")
        self.attributes("-alpha", 1.0)
        self.final_label.config(bg="white", fg="black")
        self.final_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Schedule automatic closure after 3 seconds
        self.after(3000, self.destroy())

if __name__ == "__main__":
    app = IftarCountdown()
    app.mainloop()
