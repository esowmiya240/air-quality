import tkinter as tk
from tkinter import messagebox
from plyer import notification
import time
import threading

class NotificationDemo:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Notification Demo")
        self.root.geometry("400x300")
        
        # Notification enabled by default
        self.notifications_enabled = True
        
        self.setup_ui()
        
    def setup_ui(self):
        # Title
        tk.Label(self.root, text="🔔 Notification Demo", 
                font=('Arial', 16)).pack(pady=20)
        
        # Enable/Disable checkbox
        self.notify_var = tk.BooleanVar(value=True)
        tk.Checkbutton(self.root, text="Enable Notifications",
                      variable=self.notify_var,
                      command=self.toggle_notifications).pack()
        
        # Test button
        tk.Button(self.root, text="Show Test Notification",
                 command=self.show_notification,
                 bg='#667eea', fg='white', padx=20).pack(pady=20)
        
        # Minimize instructions
        tk.Label(self.root, 
                text="👇 Minimize this window and click button\nNotification will still appear!",
                font=('Arial', 10), fg='green').pack(pady=20)
        
        # Background task demo
        tk.Button(self.root, text="Start Background Monitor",
                 command=self.start_monitor,
                 bg='#28a745', fg='white').pack(pady=10)
    
    def toggle_notifications(self):
        self.notifications_enabled = self.notify_var.get()
        status = "ENABLED" if self.notifications_enabled else "DISABLED"
        print(f"Notifications {status}")
    
    def show_notification(self):
        """Show a test notification"""
        if not self.notifications_enabled:
            messagebox.showinfo("Info", "Notifications are disabled")
            return
        
        try:
            notification.notify(
                title="✅ Test Notification",
                message="This works even when window is minimized!",
                app_name="AQI Demo",
                timeout=3
            )
            print("Notification sent!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed: {e}")
    
    def background_monitor(self):
        """Simulate background monitoring"""
        for i in range(5):
            if not self.notifications_enabled:
                break
            
            time.sleep(3)  # Wait 3 seconds
            
            # Simulate AQI check
            fake_aqi = 150 + (i * 20)
            
            # Show notification
            notification.notify(
                title="🚨 Background Alert!",
                message=f"AQI: {fake_aqi} - Check air quality!",
                app_name="AQI Monitor",
                timeout=3
            )
            print(f"Alert {i+1}: AQI = {fake_aqi}")
    
    def start_monitor(self):
        """Start monitoring in background thread"""
        thread = threading.Thread(target=self.background_monitor)
        thread.daemon = True  # Thread stops when main program closes
        thread.start()
        messagebox.showinfo("Started", "Monitoring in background!\nMinimize window to test.")
    
    def run(self):
        self.root.mainloop()

# Run the demo
if __name__ == "__main__":
    app = NotificationDemo()
    app.run()