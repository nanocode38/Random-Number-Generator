import random
import csv
import os
import sys
import time
import pathlib as pb
import tkinter as tk
from contextlib import suppress
from tkinter import ttk
from tkinter import messagebox
import json
from typing import Union

import pyautogui as pyg
import sv_ttk

from tools import init_method, restart
from constant import *


# Preprocessing: Loading data
if not (pb.Path('AppData').is_dir() and pb.Path('Classes').is_dir()):
    os.chdir('..')

with open('AppData/data.json', encoding='utf-8') as f:
    data = json.load(f)



class Main:
    def __init__(self, is_edge_hiding_mode, is_deduplication_mode, mode, language):
        # Declare all attributes in __init__
        type Color = str
        type Mode = Union['Dark', 'Light']

        self.language: dict[str, str] | None = None
        self.root: tk.Tk | None = None
        self.language_name: tk.StringVar | None = None
        self.mode: Mode | None = None
        self.bg: Color | None = None
        self.fg: Color | None = None
        self.style: ttk.Style | None = None
        self.menu: tk.Menu | None = None
        self.about_submenu: tk.Menu | None = None
        self.mode_submenu: tk.Menu | None = None
        self.language_submenu: tk.Menu | None = None
        self.class_var: tk.StringVar | None = None
        self.classes: list | None = None
        self.combobox: ttk.Combobox | None = None
        self.num_label: tk.Label | None = None
        self.name_label: tk.Label | None = None
        self.button: ttk.Button | None = None
        self.de_widget: tk.BooleanVar | None = None
        self.number_list: dict | None = None
        self.activate_timer: float | None = None
        self.cross_the_boundary_timer: float | None = None
        self.activate_floating_window: tk.Wm | None = None
        self.edge_hiding_mode: tk.BooleanVar | None = None
        self.edge_hiding_mode_button: ttk.Checkbutton | None = None
        # ========================================================================================== #

        # load language
        self.load_language_data(language)

        # Create Main Window
        self.root = tk.Tk()

        self.init_language_name(language)

        # Set mode
        self.mode, self.bg, self.fg = ('white',) * 3
        self.change_mode(mode)

        self.config_window(self.root)
        self.set_style()
        self.init_menu()
        self.init_config_area()
        self.init_num_and_name_label(is_deduplication_mode, is_edge_hiding_mode)
        self.create_button()

    @init_method
    def create_button(self):
        self.button = ttk.Button(self.root, text=self.language['Button Text'], style='Big.TButton',
                                 command=self.make_random)
        self.button.place(x=(min(ROOT_WINDOW_HEIGHT, ROOT_WINDOW_WIDTH) - self.button.winfo_reqwidth()) // 2, y=300)

    @init_method
    def load_language_data(self, language):
        with open('AppData/language/{}.json'.format(language), encoding='utf-8') as fp:
            self.language = json.load(fp)

    @init_method
    def init_language_name(self, language):
        self.language_name = tk.StringVar()
        self.language_name.set(language)

    @init_method
    def config_window(self, window):
        window.resizable(False, False)
        window.geometry("%dx%d" % (ROOT_WINDOW_WIDTH, ROOT_WINDOW_HEIGHT))
        window.title(self.language['Title'])
        window.wm_iconbitmap("AppData/icon.ico")
        window.protocol("WM_DELETE_WINDOW", self.save_data_and_exit)

    @init_method
    def set_style(self):
        self.style = ttk.Style()
        self.style.configure('TLabel', font=('Microsoft YaHei', 10))
        self.style.configure('Header.TLabel', font=('Microsoft YaHei', 12, 'bold'))
        self.style.configure('Big.TLabel', font=('Times', 60, 'bold'), foreground='red', anchor='center')
        self.style.configure('TButton', font=('Microsoft YaHei', 12), padding=6, background='red')
        self.style.configure('Big.TButton', font=('Times', 30, 'bold'), padding=10, background="lightblue",
                        relief="ridge", width=15, focuscolor="lightblue", lightcolor="lightblue",
                        darkcolor="lightblue", bordercolor="lightblue")
        self.style.configure('TCheckbutton', font=('Microsoft YaHei', 10))
        self.style.map('TCheckbutton', foreground=[('active', 'grey')])

    @init_method
    def init_menu(self):
        self.menu = tk.Menu(self.root, bg=self.bg)

        self.about_submenu = tk.Menu(self.menu, tearoff=False, bg=self.bg)
        self.about_submenu.add_command(label=self.language['Help'], command=self.help)
        self.about_submenu.add_command(label=self.language['About'], command=self.about)
        self.menu.add_cascade(label=self.language['About'], menu=self.about_submenu)

        self.mode_submenu = tk.Menu(self.menu, tearoff=False, bg=self.bg)
        self.mode_submenu.add_command(label=self.language['Light'], command=lambda: self.change_mode('Light'))
        self.mode_submenu.add_command(label=self.language['Dark'], command=lambda: self.change_mode('Dark'))
        self.menu.add_cascade(label=self.language['Mode'], menu=self.mode_submenu)

        self.language_submenu = tk.Menu(self.menu, tearoff=False, bg=self.bg)
        for language_file in os.listdir('AppData/language'):
            if language_file.endswith('.json'):
                language = language_file.split('.')[0]
                self.language_submenu.add_radiobutton(label=language, variable=self.language_name,
                command=self.change_language, value=language, indicatoron=True)
        self.menu.add_cascade(label=self.language['Language'], menu=self.language_submenu)

        count = self.language_submenu.index(tk.END) + 1
        for i in range(count):
            self.language_submenu.entryconfig(i, selectcolor=self.fg)

        self.root.config(menu=self.menu)

    @init_method
    def init_config_area(self):
        ttk.Label(self.root, text=self.language['Class'] + ": ", style='Header.TLabel').place(x=2, y=3)
        self.class_var = tk.StringVar()
        self.classes = []
        for file in os.listdir('Classes/'):
            if file.endswith('.csv'):
                self.classes.append(file)
                self._classes_name = [file.split('.')[0] for file in self.classes]
        self.combobox = ttk.Combobox(self.root, textvariable=self.class_var, values=self._classes_name,
                                     state="readonly", width=10)
        self.combobox.place(x=60, y=5)

    @init_method
    def init_num_and_name_label(self, is_deduplication_mode, is_edge_hiding_mode):
        label_bg = '#bbb' if self.mode == 'Light' else '#444'

        self.num_label = tk.Label(self.root, text="", bg=label_bg, fg='red', width=3, height=2,
                                  font=("Times", 60, "bold"))
        self.num_label.place(x=5, y=(290 - self.num_label.winfo_reqheight()) // 2 + 20)
        self.name_label = tk.Label(self.root, text="", bg=label_bg, fg='red', width=8, height=4, font=("Times", 30,
                                                                                                    "bold"))
        self.name_label.place(x=230, y=(290 - self.num_label.winfo_reqheight()) // 2 + 20)

        self.init_deweight_checkbox(is_deduplication_mode)
        self.init_hide_mode(is_edge_hiding_mode)

    @init_method
    def init_deweight_checkbox(self, is_deduplication_mode):
        self.de_widget = tk.BooleanVar()
        self.de_widget.set(is_deduplication_mode)
        self.de_weight_button = ttk.Checkbutton(self.root, text=self.language['Deduplication'], variable=self.de_widget,
                                                onvalue=True, offvalue=False, style='TCheckbutton')
        self.de_weight_button.place(x=330, y=5)
        self.number_list = {-10_086}

    @init_method
    def init_hide_mode(self, is_edge_hiding_mode):
        self.cross_the_boundary_timer = .0
        self.activate_timer = .0

        self.config_floating_window()

        self._img = tk.PhotoImage(file="AppData/icon.png").subsample(18, 18)
        tk.Label(self.activate_floating_window, image=self._img).pack()

        self.init_hide_checkbox(is_edge_hiding_mode)
        self.bind_floating_window()

    @init_method
    def bind_floating_window(self):
        self.activate_floating_window.bind("<Enter>", self.start_activate_timer)
        self.activate_floating_window.bind("<Leave>", self.stop_activate_timer)
        self.activate_floating_window.bind("<Button-1>", lambda _: self.check_activate(True))

    @init_method
    def config_floating_window(self):
        self.activate_floating_window = tk.Toplevel(self.root, bg=self.bg)
        self.activate_floating_window.wm_attributes('-topmost', True)
        self.activate_floating_window.wm_attributes('-alpha', 0.4)
        self.activate_floating_window.config(bg=self.bg)
        self.activate_floating_window.wm_attributes('-transparentcolor', self.bg)
        self.activate_floating_window.withdraw()
        self.activate_floating_window.overrideredirect(True)
        self.activate_floating_window.geometry("50x50")

    @init_method
    def init_hide_checkbox(self, is_edge_hiding_mode):
        self.edge_hiding_mode = tk.BooleanVar()
        self.edge_hiding_mode.set(is_edge_hiding_mode)
        self.edge_hiding_mode.trace("w", self.switchover_mode)
        self.edge_hiding_mode_button = ttk.Checkbutton(self.root, text=self.language['Hide'],
                                                       variable=self.edge_hiding_mode,
                                                       onvalue=True, offvalue=False, style='TCheckbutton')
        self.edge_hiding_mode_button.place(x=190, y=5)

    def change_language(self):
        try:
            language = self.language_name.get()
            with open('AppData/language/' + language + '.json', encoding='utf-8') as fp:
                self.language = json.load(fp)
        except Exception as e:
            messagebox.showerror(self.language['Title'], self.language['Language Error'].format(type=type(e).__name__,
                                                                                                e=e, id=hex(id(e))))
            raise e
        else:
            if messagebox.askyesno(self.language['Title'], self.language['Restart Info']):
                self.save_data_and_exit(silent=True)
                restart()

    def change_mode(self, mode: str):
        self.mode = mode
        sv_ttk.set_theme(self.mode)
        ttk.Label(self.root, text=self.language['Class'] + ": ", style='Header.TLabel').place(x=2, y=3)
        self.bg = 'white' if self.mode == 'Light' else 'black'
        self.fg = 'black' if self.mode == 'Light' else 'white'
        with suppress(AttributeError):
            self.menu.config(bg=self.bg)
            self.mode_submenu.config(bg=self.bg)
            self.about_submenu.config(bg=self.bg)
            self.set_style()
            count = self.language_submenu.index(tk.END) + 1  # 菜单项数量
            for i in range(count):
                self.language_submenu.entryconfig(i, selectcolor=self.fg)
        self.root.update()

    def make_random(self):
        file = self.class_var.get()
        if not file:
            file = 'example.csv'
        if not file.endswith('.csv'):
            file += '.csv'
        with open('Classes/' + file, newline='', encoding='utf-8') as csv_file:
            row = list(csv.reader(csv_file))[0]
        rand = -10086
        if self.de_widget.get():
            if sorted(list(range(0, len(row))) + [-10086, ]) == sorted(list(self.number_list)):
                messagebox.showwarning(self.language['Title'], self.language['Message'])
                self.number_list = {-10086}
                self.root.update()
                return
            while rand in self.number_list:
                rand = random.randint(0, len(row) - 1)
        else:
            rand = random.randint(0, len(row) - 1)
        self.number_list.add(rand)
        self.num_label.config(text=str(rand + 1))
        self.name_label.config(text=row[rand])

    def about(self):
        toplevel = tk.Toplevel(self.root)
        toplevel.wm_iconbitmap("AppData/icon.ico")
        toplevel.wm_attributes("-topmost", True)
        toplevel.title(self.language['Title'])
        ttk.Label(toplevel, text=self.language['About Text']).pack()
        toplevel.mainloop()

    def help(self):
        toplevel = tk.Toplevel(self.root)
        toplevel.wm_attributes('-topmost', True)
        toplevel.wm_iconbitmap("AppData/icon.ico")
        toplevel.title("随机学号生成器")
        ttk.Label(toplevel, text=self.language['Help Text']).pack()
        toplevel.mainloop()

    def run(self):
        while True:
            self.root.update()
            self.check_cross_the_boundary()
            self.check_activate()
            self.check_mouse_in_window()

    def show_animate(self, pos_x, pos_y, *, mode='show', left=False):
        self.root.withdraw()
        self.activate_floating_window.withdraw()
        animate_window = tk.Toplevel(self.root)
        animate_window.wm_attributes('-topmost', True)
        animate_window.wm_attributes('-alpha', .5 if mode == 'show' else 1.)

        img = tk.PhotoImage(file=f"AppData/{self.mode}.png")
        label = tk.Label(animate_window, image=img)
        label.place(x=0, y=0)

        animate_window.withdraw()
        animate_window.overrideredirect(True)
        animate_window.geometry('50x50' if mode == 'show' else '{size}x{size}'.format(size=min(ROOT_WINDOW_HEIGHT,
                                                                                               ROOT_WINDOW_WIDTH)))

        animate_window.deiconify()

        alpha = .5 if mode == 'show' else 1.
        pos_x_copy, pos_y_copy = pos_x, pos_y
        for _ in range(74):
            alpha += .006 if mode == 'show' else -.006
            animate_window.wm_attributes('-alpha', alpha)
            animate_window.update()
            if not left:
                animate_window.geometry(f"{animate_window.winfo_width() + (5 if mode == 'show' else -5)}x"
                                        f"{animate_window.winfo_height() + (5 if mode == 'show' else -5)}+"
                                        f"{pos_x}+{pos_y}")
            else:
                pos_x_copy -= 5 if mode == 'show' else -5
                pos_y_copy  -= 5 if mode == 'show' else -5
                animate_window.geometry(f"{animate_window.winfo_width() + (5 if mode == 'show' else -5)}x"
                                        f"{animate_window.winfo_height() + (5 if mode == 'show' else -5)}+"
                                        f"{pos_x_copy}+{pos_y_copy}")
            time.sleep(.002)

        animate_window.withdraw()

    def check_cross_the_boundary(self, *_):
        if not self.edge_hiding_mode.get() or self.check_mouse_in_window():
            return False
        if self.activate_floating_window.winfo_viewable():
            return True
        root_width = self.root.winfo_width()
        screen_size = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        if not (self.root.winfo_x() < EDGE_POS_FAULT_TOLERANCE or self.root.winfo_x() > screen_size[
            0] - root_width - EDGE_POS_FAULT_TOLERANCE):
            self.cross_the_boundary_timer = 0
        if (self.root.winfo_x() < EDGE_HIDDEN_DELAY_TIME or self.root.winfo_x() > screen_size[
            0] - root_width - EDGE_POS_FAULT_TOLERANCE) and self.cross_the_boundary_timer == 0:
            # Hidden Left
            self.cross_the_boundary_timer = time.time()
        elif self.root.winfo_x() < EDGE_POS_FAULT_TOLERANCE and time.time() - self.cross_the_boundary_timer >= EDGE_HIDDEN_DELAY_TIME:
            self.activate_floating_window.geometry(
                f"+{EDGE_POS_FAULT_TOLERANCE}+{self.root.winfo_y()}"
            )
            if self.root.winfo_viewable():
                self.show_animate(EDGE_POS_FAULT_TOLERANCE, self.root.winfo_y(), mode='hidden')
            self.activate_floating_window.deiconify()
        elif self.root.winfo_x() > screen_size[
            0] - root_width - EDGE_POS_FAULT_TOLERANCE and time.time() - self.cross_the_boundary_timer >= EDGE_HIDDEN_DELAY_TIME:
            self.activate_floating_window.geometry(
                "+%d+%d" % (self.root.winfo_screenwidth() - EDGE_POS_FAULT_TOLERANCE -
                            self.activate_floating_window.winfo_width(),
                            self.root.winfo_y() + self.root.winfo_height()))

            if self.root.winfo_viewable():
                self.show_animate(self.root.winfo_x(), self.root.winfo_y(), mode='hidden', left=True)
            self.activate_floating_window.deiconify()
        return True

    def check_activate(self, free: bool = False):
        if not self.edge_hiding_mode.get():
            return
        if free or (time.time() - self.activate_timer >= EDGE_HIDDEN_DELAY_TIME and self.activate_timer != .0):
            left = self.activate_floating_window.winfo_x() >= 100
            if left:
                self.show_animate(self.activate_floating_window.winfo_x(), self.activate_floating_window.winfo_y(), left=True)
            else:
                self.show_animate(self.root.winfo_x(), self.root.winfo_y(), left=False)

            self.root.deiconify()
            self.activate_timer = .0
            self.cross_the_boundary_timer = .0

    def switchover_mode(self, *_):
        self.root.wm_attributes('-topmost', self.edge_hiding_mode.get())
        if not self.edge_hiding_mode.get():
            self.cross_the_boundary_timer = .0

    def start_activate_timer(self, *_):
        self.activate_timer = time.time()

    def stop_activate_timer(self, *_):
        self.activate_timer = .0

    def check_mouse_in_window(self) -> bool:
        window_x1 = self.root.winfo_rootx()
        window_y1 = self.root.winfo_rooty()
        window_x2 = window_x1 + self.root.winfo_width()
        window_y2 = window_y1 + self.root.winfo_height()
        window_y1 -= 80

        mouse_x, mouse_y = pyg.position()

        if (window_x1 <= mouse_x <= window_x2 and
                window_y1 <= mouse_y <= window_y2):
            self.cross_the_boundary_timer = .0
            return True
        return False

    def save_data_and_exit(self, silent=False):
        global data
        data['Deduplication mode'] = self.de_widget.get()
        data['Edge hiding mode'] = self.edge_hiding_mode.get()
        data['Language'] = self.language['Name']
        with open('AppData/data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f)
        self.root.destroy()
        if not silent:
            sys.exit(0)


if __name__ == "__main__":
    Main(is_deduplication_mode=data['Deduplication mode'], is_edge_hiding_mode=data['Edge hiding mode'],
         mode=data["Mode"], language=data["Language"]).run()