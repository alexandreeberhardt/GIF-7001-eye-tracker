from Model.NotificationCenter import NotificationCenter
from Model.NotificationList import AppNotification
from Model.GlobalVariables import GlobalVariables
from Model.SingletonDecorator import singleton
from View.ViewOption import ViewOption
from View.ViewCalibration import ViewCalibration
from tkinter import font as tkfont
from tkinter import ttk
import tkinter as tk
import os


@singleton
class MainWindow(tk.Tk):
	def __init__(self):
		super().__init__()
		self.title("Eye Tracker")
		self.base_width = 220
		self.base_height = 150
		self.geometry(f"{self.base_width}x{self.base_height}")
		self.after(10, self.location_on_the_screen)
		self.base_font = tkfont.Font(family="Segoe UI", size=10)
		self._last_font_size = 10
		self._resizing = False
		self.minsize(self.base_width, self.base_height)
		self.scale = 1

		self.style = ttk.Style()
		self.style.theme_use("clam")
		self.style.configure(".", font=self.base_font)
		bg_main = "#f8caa9"
		fg_text = "#000000"
		bg_entry = "#dcbdbb"
		bg_button = "#dcbdbb"

		self.configure(bg=bg_main)
		self.style.configure("TFrame", background=bg_main)
		self.style.configure("TLabel",background=bg_main,foreground=fg_text)
		self.style.configure("TCombobox",fieldbackground=bg_entry,foreground=fg_text,background=bg_entry)
		self.style.configure("TEntry",fieldbackground="#000000",foreground=fg_text,background=bg_entry)
		self.style.configure("TButton",background=bg_button,foreground=fg_text)
		self.style.configure("Vertical.TScrollbar",background=bg_main,troughcolor=bg_main)
		self.style.configure("TCheckbutton",background=bg_main,foreground=fg_text)
		self.style.configure("TProgressbar", troughcolor=bg_entry, background="#4CAF50")
		self.style.configure("TNotebook.Tab",background=bg_main,foreground=fg_text)
		self.style.configure("TSpinbox",fieldbackground="#000000",foreground=fg_text,background=bg_main)
		self.style.configure("TNotebook",background=bg_main,foreground=fg_text)

		self.style.configure("TCombobox", font=self.base_font)
		self.option_add("*TCombobox*Listbox.font", self.base_font)

		self.style.map("TNotebook.Tab", background=[("selected", bg_main)], foreground=[("selected", fg_text)])
		self.style.map("TCheckbutton",foreground=[('disabled', fg_text)],background=[('disabled', bg_main)])
		self.style.map("TEntry",foreground=[('disabled', fg_text)],fieldbackground=[('disabled', bg_entry)],background=[('disabled', bg_entry)])
		self.style.map("TButton",foreground=[('disabled', bg_main)],background=[('disabled', bg_main)])
		self.style.map("TCombobox",foreground=[('disabled', fg_text)],fieldbackground=[('disabled', bg_entry)],background=[('disabled', bg_entry)])

		self.setup_window_tabs()
		self.iconbitmap(f"{os.path.abspath('')}{os.sep}View{os.sep}logo{os.sep}logo.ico")
		self.attributes("-topmost", True)

		GlobalVariables().root = self
		self.calibrationView = ViewCalibration(self.base_font)
		self.protocol("WM_DELETE_WINDOW", self.closeEvent)
		self.bind("<Configure>", self.on_resize)

	def on_resize(self, event):
		if event.widget is not self:
			return

		scale_w = event.width / self.base_width
		scale_h = event.height / self.base_height
		scale = min(scale_w, scale_h)

		if scale != self.scale:
			self.scale = scale
			new_size = int(10 * scale)
			self.base_font.configure(size=max(8, new_size))

	def setup_window_tabs(self):
		"""
		Tab setup
		"""
		notebook = ttk.Notebook(self)
		notebook.pack(expand=True, fill="both")

		self.viewOption = ViewOption(notebook, self)
		notebook.add(self.viewOption, text="Options")

	def closeEvent(self):
		"""
		event: close event
		Close all window and disconnect motor

		"""
		NotificationCenter().post_notification(AppNotification.CLOSE_ALL_WINDOW, self,"")
		self.destroy()

	def location_on_the_screen(self):
		self.update_idletasks()

		screen_width = self.winfo_screenwidth()
		screen_height = self.winfo_screenheight()
		window_width = self.winfo_width()
		window_height = self.winfo_height()

		x = screen_width - 10 - window_width
		y = int(screen_height / 2 - window_height / 2)

		self.geometry(f"+{x}+{y}")
