from Model.GlobalVariables import GlobalVariables
from View.mainWindow import MainWindow
from Control.AppTracking import AppTracking
from tkinter import ttk
import tkinter as tk
import threading
import ctypes
import sys


class SplashScreen(tk.Toplevel):
	def __init__(self, parent):
		super().__init__(parent)
		self.attributes("-topmost", True)
		self.overrideredirect(True)
		self.configure(bg="#202634")
		screen_width = self.winfo_screenwidth()
		screen_height = self.winfo_screenheight()

		width = screen_width // 3
		height = screen_height // 3

		x = (screen_width - width) // 2
		y = (screen_height - height) // 2
		self.geometry(f"{width}x{height}+{x}+{y}")

		self.grid_rowconfigure(0, weight=3)
		self.grid_rowconfigure(1, weight=1)
		self.grid_columnconfigure(0, weight=1)

		font_size = max(12, height // 10)
		ttk.Label(self, text="Loading...", font=("Segoe UI", font_size),
		  foreground="white", background="#202634",
		  anchor="center", justify="center").grid(row=0, column=0, sticky="nsew", pady=(height//10,0))

		self.progress = ttk.Progressbar(self, mode="indeterminate")
		self.progress.grid(row=1, column=0, sticky="ew", padx=width//10, pady=height//10)
		self.progress.start(10)

def init_work(view, splash):
	AppTracking(splash.winfo_screenwidth(), splash.winfo_screenheight())
	view.after(0, lambda: (splash.destroy(), view.deiconify()))

if sys.platform == "win32":
	myappid = u"EyeTrackerApp"
	ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)


if __name__ == "__main__":
	view = MainWindow()
	view.withdraw()
	splash = SplashScreen(view)
	threading.Thread(target=init_work, args=(view, splash), daemon=True).start()
	GlobalVariables().root = view
	view.mainloop()
