import tkinter as tk
from tkinter import messagebox, ttk # Import ttk for themed widgets
from pynput.mouse import Controller, Button
from pynput.keyboard import Controller as KeyboardController, Key 
import threading
import time
import sys

# --- Constants and Configuration ---
WINDOW_TITLE = "🐦 WOODY Autoclicker"
WHITE_BG_COLOR = "#ffffff"  # White Background
BUTTON_BG_COLOR = "#dc3545"  # Red (All main buttons background)
ACCENT_COLOR = "#007bff"    # Blue (For status messages)
FONT_STYLE = ("Arial", 10, "bold")
DELAY_BEFORE_START = 3
CLICK_INTERVAL_SECONDS = 0.03 
MESSAGE_TO_TYPE = "Hola soy un bot 🤖 de Neuros 😎 que sirve a su dios ⚡"

class WoodyAutoclicker:
    def __init__(self, master):
        self.master = master
        master.title(WINDOW_TITLE)
        master.geometry("400x570") 
        master.resizable(False, False)
        master.config(bg=WHITE_BG_COLOR) 

        # Initialization variables
        self.mouse = Controller()
        self.keyboard = KeyboardController() 
        self.target_x = None
        self.target_y = None
        self.is_running = False
        self.stop_requested = False 
        self.clicks_performed = 0
        self.current_click_limit = 0
        
        # --- TTK Style Configuration (The fix for disabled background) ---
        self.style = ttk.Style()
        
        # 1. Define the base style for all buttons ('Red.TButton')
        self.style.configure(
            'Red.TButton',
            background=BUTTON_BG_COLOR,
            foreground='white',
            font=FONT_STYLE,
            relief='flat',
            borderwidth=0,
            # We set the background and foreground for the normal state here
            # These are usually overridden by map, but necessary for the base style
        )
        
        # 2. Map specific state colors (Crucial for DISABLED and ACTIVE states)
        self.style.map(
            'Red.TButton',
            # Set the foreground (text color) to always be white
            foreground=[('disabled', 'white'), ('active', 'white'), ('!disabled', 'white')],
            # Set the background color for different states
            background=[('disabled', BUTTON_BG_COLOR), ('active', '#b02a37'), ('!disabled', BUTTON_BG_COLOR)],
        )

        # 3. Define the style for labels (ttk.Label doesn't support 'bg', so we use standard tk.Label)
        LABEL_STYLES = {
            "fg": "black", 
            "bg": WHITE_BG_COLOR,
        }

        # --- Main Title ---
        # Labels remain tk.Label for easy background color control
        self.title_label = tk.Label(
            master,
            text="🐦 WOODY",
            font=("Arial", 24, "bold"),
            **LABEL_STYLES
        )
        self.title_label.pack(pady=(20, 0))

        self.subtitle_label = tk.Label(
            master,
            text="Autoclicker",
            font=("Arial", 14),
            **LABEL_STYLES
        )
        self.subtitle_label.pack(pady=(0, 15))


        # 1. Status/Coordinates Indicator
        self.status_label = tk.Label(
            master,
            text="State: Waiting for coordinates...",
            font=("Arial", 11),
            **LABEL_STYLES
        )
        self.status_label.pack(pady=5)
        
        # 1b. Progress Label 
        self.progress_label = tk.Label(
            master,
            text=f"Interval: {CLICK_INTERVAL_SECONDS}s per click",
            font=("Arial", 10),
            **LABEL_STYLES
        )
        self.progress_label.pack(pady=5)


        # 2. Area Selection Button (Now ttk.Button)
        self.select_button = ttk.Button(
            master,
            text="📌 Select Area (3s)",
            command=self.start_selection_thread,
            style='Red.TButton' # Apply the custom style
        )
        self.select_button.pack(pady=8, padx=20, fill=tk.X)
        
        # 3a. Start 1000 Clicks Button (Now ttk.Button)
        self.start_1000_button = ttk.Button(
            master,
            text="🚀 Start 1000 Clicks",
            command=lambda: self.start_clicks_thread(1000),
            state=tk.DISABLED,
            style='Red.TButton'
        )
        self.start_1000_button.pack(pady=(10, 5), padx=20, fill=tk.X)

        # 3b. Start 5000 Clicks Button (Now ttk.Button)
        self.start_5000_button = ttk.Button(
            master,
            text="⚡️ Start 5000 Clicks",
            command=lambda: self.start_clicks_thread(5000),
            state=tk.DISABLED,
            style='Red.TButton'
        )
        self.start_5000_button.pack(pady=5, padx=20, fill=tk.X)
        
        # 3c. Typing Message Button (Now ttk.Button)
        self.typing_button = ttk.Button(
            master,
            text="✍️ Type Message",
            command=self.start_typing_thread,
            state=tk.DISABLED,
            style='Red.TButton'
        )
        self.typing_button.pack(pady=5, padx=20, fill=tk.X)


        # 4. Stop Button (Now ttk.Button)
        self.stop_button = ttk.Button(
            master,
            text="🛑 Stop Clicks",
            command=self.stop_clicks,
            state=tk.DISABLED,
            style='Red.TButton'
        )
        self.stop_button.pack(pady=8, padx=20, fill=tk.X)
        
        # 5. Exit Button (Now ttk.Button)
        self.exit_button = ttk.Button(
            master,
            text="Exit",
            command=master.quit,
            style='Red.TButton'
        )
        self.exit_button.pack(pady=15, padx=20, fill=tk.X)
        
        # --- Developer Label ---
        self.dev_label = tk.Label(
            master,
            text="Developed by Neurocode",
            font=("Arial", 9, "italic"),
            fg="black", 
            bg=WHITE_BG_COLOR
        )
        self.dev_label.pack(pady=(10, 10))


    # --- Threading and Coordinate Capture Logic ---

    def start_selection_thread(self):
        """Starts a thread for the countdown and coordinate capture."""
        if self.is_running:
            return

        self.status_label.config(text="State: ⏳ 3 seconds to position mouse...", fg=ACCENT_COLOR)
        self._disable_all_buttons()
        self.is_running = True

        threading.Thread(target=self.capture_coordinates_after_delay, daemon=True).start()

    def capture_coordinates_after_delay(self):
        """Waits 3 seconds and then captures mouse coordinates."""
        
        # Simple countdown display
        for i in range(DELAY_BEFORE_START, 0, -1):
            # Use master.after to update the UI from the thread
            self.master.after(1000 * (DELAY_BEFORE_START - i), 
                              lambda i=i: self.status_label.config(text=f"State: ⏳ Capture in {i} seconds...", fg=ACCENT_COLOR))
            time.sleep(1) 

        time.sleep(1) 
        
        try:
            x, y = self.mouse.position
            self.target_x = x
            self.target_y = y
            self.master.after(0, self.update_status_after_selection)
        except Exception as e:
            self.master.after(0, lambda: self._handle_mac_permissions_error(e))

    def update_status_after_selection(self):
        """Updates the interface after selection is complete."""
        self.is_running = False
        self._enable_all_buttons()
        
        if self.target_x is not None:
            self.status_label.config(
                text=f"✅ Coordinates captured: ({self.target_x}, {self.target_y})",
                fg=BUTTON_BG_COLOR 
            )
            # Enable all action buttons (clicks and typing)
            self.start_1000_button.config(state=tk.NORMAL)
            self.start_5000_button.config(state=tk.NORMAL)
            self.typing_button.config(state=tk.NORMAL)
            self.progress_label.config(text=f"Ready to start clicks or typing.")
        else:
            self.status_label.config(text="❌ Error capturing coordinates.", fg=BUTTON_BG_COLOR)
            self.progress_label.config(text=f"Interval: {CLICK_INTERVAL_SECONDS}s per click")
        
    # --- Auto Clicks Logic ---

    def start_clicks_thread(self, click_limit):
        """Starts a thread for the click burst and enables the Stop button."""
        if self.is_running or self.target_x is None:
            return
        
        # Set the click limit for this execution
        self.current_click_limit = click_limit
        
        # Reset control variables
        self.stop_requested = False
        self.clicks_performed = 0

        self.status_label.config(text=f"State: ⚙️ Performing {click_limit} clicks...", fg=ACCENT_COLOR)
        self._disable_all_buttons(allow_stop=True) # Only allow Stop button to be active
        self.is_running = True
        
        threading.Thread(target=self.perform_clicks, daemon=True).start()

    def stop_clicks(self):
        """Sets the flag to safely stop the clicks process."""
        if self.is_running:
            self.stop_requested = True
            self.status_label.config(text="State: 🔴 Stop requested...", fg=BUTTON_BG_COLOR)
            self.stop_button.config(state=tk.DISABLED)

    def perform_clicks(self):
        """Moves the mouse and performs clicks with a pause, checking the stop flag."""
        
        try:
            # Move the mouse once before starting
            self.mouse.position = (self.target_x, self.target_y)

            for i in range(1, self.current_click_limit + 1):
                if self.stop_requested:
                    break # Exit the loop if stop is requested

                self.clicks_performed = i
                
                # Update the progress label on the main thread
                self.master.after(0, 
                                  lambda i=i: self.progress_label.config(text=f"Click {i} of {self.current_click_limit} | Remaining {self.current_click_limit - i}"))
                
                self.mouse.click(Button.left)
                
                # PAUSE OF 0.03 SECONDS
                time.sleep(CLICK_INTERVAL_SECONDS) 

            self.master.after(0, self.finish_clicks)
        except Exception as e:
            self.master.after(0, lambda: self._handle_mac_permissions_error(e))

    # --- Auto Typing Logic ---

    def start_typing_thread(self):
        """Starts a thread for typing automation."""
        if self.is_running or self.target_x is None:
            return
        
        self.status_label.config(text="State: ✍️ Typing message...", fg=ACCENT_COLOR)
        self.progress_label.config(text=f"Message: '{MESSAGE_TO_TYPE[:30]}...'")
        self._disable_all_buttons() 
        self.is_running = True
        
        threading.Thread(target=self.perform_typing, daemon=True).start()

    def perform_typing(self):
        """Moves the mouse, clicks, types the message, and then presses Enter."""
        try:
            # 1. Move the mouse and click to activate the text field
            self.mouse.position = (self.target_x, self.target_y)
            time.sleep(0.1) 
            self.mouse.click(Button.left)
            time.sleep(0.1) 

            # 2. Type the message
            self.keyboard.type(MESSAGE_TO_TYPE)
            time.sleep(0.1) 
            
            # 3. PRESS THE ENTER KEY
            self.keyboard.press(Key.enter)
            self.keyboard.release(Key.enter)
            time.sleep(0.5) 

            self.master.after(0, self.finish_typing)
        except Exception as e:
            self.master.after(0, lambda: self._handle_mac_permissions_error(e))

    def finish_typing(self):
        """Shows the typing completion popup and restores the state."""
        self.is_running = False
        self._enable_all_buttons()
        
        msg = (f"The message has been typed and sent (by pressing Enter) at coordinates "
               f"({self.target_x}, {self.target_y}):\n\n{MESSAGE_TO_TYPE}")
        self.status_label.config(text="✅ Typing task finished.", fg=BUTTON_BG_COLOR)
        self.progress_label.config(text=f"Ready to start clicks or typing.")

        messagebox.showinfo("Woody - Typing Finished", msg)


    # --- Finalization and Utility ---

    def finish_clicks(self):
        """Shows the clicks completion popup and restores the state."""
        
        self.is_running = False
        self._enable_all_buttons()
        
        if self.clicks_performed == self.current_click_limit:
            # Task completed
            msg = (f"The burst of {self.current_click_limit} left clicks has been COMPLETELY "
                   f"finished at coordinates ({self.target_x}, {self.target_y}).")
            self.status_label.config(text=f"✅ Task finished ({self.clicks_performed} clicks).", fg=BUTTON_BG_COLOR)
        else:
            # Task stopped
            msg = (f"The click burst ({self.current_click_limit}) was STOPPED by the user after "
                   f"performing {self.clicks_performed} clicks.")
            self.status_label.config(text=f"⚠️ Task stopped ({self.clicks_performed} clicks).", fg=ACCENT_COLOR)
        
        self.progress_label.config(text=f"Total: {self.clicks_performed} clicks performed. Last limit: {self.current_click_limit}")

        # Show completion message with updated count
        messagebox.showinfo("Woody - Finished", msg)
        
    # --- Utility Methods ---

    def _disable_all_buttons(self, allow_stop=False):
        """Disables all action buttons."""
        self.select_button.config(state=tk.DISABLED)
        self.start_1000_button.config(state=tk.DISABLED)
        self.start_5000_button.config(state=tk.DISABLED)
        self.typing_button.config(state=tk.DISABLED)
        self.exit_button.config(state=tk.DISABLED)
        # Enable stop button only if the process is ongoing
        self.stop_button.config(state=tk.NORMAL if allow_stop else tk.DISABLED)

    def _enable_all_buttons(self):
        """Enables all primary buttons."""
        self.select_button.config(state=tk.NORMAL)
        self.exit_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED) # Always disabled outside of the click process
        # Action buttons are only enabled if coordinates have been captured
        if self.target_x is not None:
            self.start_1000_button.config(state=tk.NORMAL)
            self.start_5000_button.config(state=tk.NORMAL)
            self.typing_button.config(state=tk.NORMAL)

    def _handle_mac_permissions_error(self, error):
        """Handles specific pynput errors on macOS."""
        self.is_running = False
        self._enable_all_buttons()
        self.status_label.config(text="❌ macOS Permissions ERROR.", fg=BUTTON_BG_COLOR)
        self.progress_label.config(text=f"Interval: {CLICK_INTERVAL_SECONDS}s per click")

        if "You must grant permission for the application to control your input devices" in str(error) or sys.platform == "darwin":
            messagebox.showerror(
                "❌ ERROR: macOS Permissions",
                "ATTENTION! The macOS operating system is blocking mouse/keyboard control.\n\n"
                "YOU NEED to do the following:\n"
                "1. Go to System Preferences > Security & Privacy > Privacy.\n"
                "2. Select 'Accessibility'.\n"
                "3. Add the Python application (or the terminal running the script) to the list of allowed applications.\n"
                "4. Restart the Woody application."
            )
        else:
            messagebox.showerror("Error", f"An unexpected error occurred while using the mouse/keyboard: {e}")


# --- Main Execution ---
if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = WoodyAutoclicker(root)
        root.mainloop()
    except ImportError:
        messagebox.showerror(
            "Dependency Error",
            "The 'pynput' library is required for this application.\n"
            "Install it with: pip install pynput"
        )
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred while starting the application: {e}")
