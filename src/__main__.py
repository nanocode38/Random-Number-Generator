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

import pyautogui as pyg
import sv_ttk

EDGE_HIDDEN_DELAY_TIME = 1
EDGE_POS_FAULT_TOLERANCE = 5

if not (pb.Path('AppData').is_dir() and pb.Path('Classes').is_dir()):
    os.chdir('..')

with open('AppData/data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)


class Main:
    def __init__(self, is_edge_hiding_mode, is_deduplication_mode, mode):
        self.root = tk.Tk()
        self.mode, self.bg, self.fg = ('white',) * 3
        self.change_mode(mode)
        self.root.resizable(False, False)
        self.root.geometry("420x430")
        self.root.title("随机学号生成器")
        self.root.wm_iconbitmap("AppData/icon.ico")
        self.root.protocol("WM_DELETE_WINDOW", self.save_data_and_exit)

        style = ttk.Style()
        style.configure('TLabel', font=('Microsoft YaHei', 10))
        style.configure('Header.TLabel', font=('Microsoft YaHei', 12, 'bold'))
        style.configure('Big.TLabel', font=('Times', 60, 'bold'), foreground='red', anchor='center')
        style.configure('TButton', font=('Microsoft YaHei', 12), padding=6)
        style.configure('Big.TButton', font=('Times', 30, 'bold'), padding=10)
        style.configure('TCheckbutton', font=('Microsoft YaHei', 10))
        style.map('TCheckbutton', foreground=[('active', 'grey')])


        self.menu = tk.Menu(self.root, bg=self.bg)

        self.about_submenu = tk.Menu(self.menu, tearoff=False, bg=self.bg)
        self.about_submenu.add_command(label="帮助", command=self.help)
        self.about_submenu.add_command(label='关于', command=self.about)
        self.menu.add_cascade(label="关于", menu=self.about_submenu)

        self.mode_submenu = tk.Menu(self.menu, tearoff=False, bg=self.bg)
        self.mode_submenu.add_command(label="明亮模式", command=lambda: self.change_mode('Light'))
        self.mode_submenu.add_command(label="暗黑模式", command=lambda: self.change_mode('Dark'))
        self.menu.add_cascade(label="主题", menu=self.mode_submenu)

        self.root.config(menu=self.menu)


        ttk.Label(self.root, text="班级: ", style='Header.TLabel').place(x=2, y=3)
        self.class_var = tk.StringVar()
        self.classes = list()
        for file in os.listdir('Classes/'):
            if file.endswith('.csv'):
                self.classes.append(file)
                self._classes_name = [file.split('.')[0] for file in self.classes]
        self.combobox = ttk.Combobox(self.root, textvariable=self.class_var, values=self._classes_name,
                                     state="readonly", width=10)
        self.combobox.place(x=60, y=5)

        label_bg = '#bbb' if self.mode == 'Light' else '#444'

        self.num_label = tk.Label(self.root, text="", bg=label_bg, fg='red', width=3, height=2,
                                  font=("Times", 60, "bold"))
        self.num_label.place(x=5, y=(290 - self.num_label.winfo_reqheight()) // 2 + 20)
        self.name_label = tk.Label(self.root, text="", bg=label_bg, fg='red', width=6, height=4, font=("Times", 30,
                                                                                                    "bold"))
        self.name_label.place(x=230, y=(290 - self.num_label.winfo_reqheight()) // 2 + 20)

        self.button = ttk.Button(self.root, text="生成随机学号", style='Big.TButton', command=self.make_random)
        self.button.place(x=(420 - self.button.winfo_reqwidth()) // 2, y=300)

        self.de_widget = tk.BooleanVar()
        self.de_widget.set(is_deduplication_mode)
        self.de_weight_button = ttk.Checkbutton(self.root, text="去重模式", variable=self.de_widget,
                                                onvalue=True, offvalue=False, style='TCheckbutton')
        self.de_weight_button.place(x=320, y=5)
        self.number_list = {-10_086}

        # 贴边隐藏功能
        self.cross_the_boundary_timer = .0
        self.activate_timer = .0
        self.activate_floating_window = tk.Toplevel(self.root, bg=self.bg)
        self.activate_floating_window.wm_attributes('-topmost', True)
        self.activate_floating_window.wm_attributes('-alpha', 0.4)
        self.activate_floating_window.config(bg=self.bg)
        self.activate_floating_window.wm_attributes('-transparentcolor', self.bg)
        self.activate_floating_window.withdraw()
        self.activate_floating_window.overrideredirect(True)
        self.activate_floating_window.geometry("50x50")
        self._img = tk.PhotoImage(file="AppData/icon.png").subsample(18, 18)
        tk.Label(self.activate_floating_window, image=self._img).pack()

        self.edge_hiding_mode = tk.BooleanVar()
        self.edge_hiding_mode.set(is_edge_hiding_mode)
        self.edge_hiding_mode.trace("w", self.switchover_mode)
        self.edge_hiding_mode_button = ttk.Checkbutton(self.root, text="贴边隐藏模式", variable=self.edge_hiding_mode,
                                                       onvalue=True, offvalue=False, style='TCheckbutton')
        self.edge_hiding_mode_button.place(x=180, y=5)

        self.activate_floating_window.bind("<Enter>", self.start_activate_timer)
        self.activate_floating_window.bind("<Leave>", self.stop_activate_timer)
        self.activate_floating_window.bind("<Button-1>", lambda _: self.check_activate(True))

    def change_mode(self, mode: str):
        self.mode = mode
        sv_ttk.set_theme(self.mode)
        self.bg = 'white' if self.mode == 'Light' else 'black'
        self.fg = 'black' if self.mode == 'Light' else 'white'
        with suppress(AttributeError):
            self.menu.config(bg=self.bg)
            self.mode_submenu.config(bg=self.bg)
            self.about_submenu.config(bg=self.bg)
            ttk.Style().configure('Big.TButton', font=('Times', 30, 'bold'), padding=10)
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
                messagebox.showwarning('随机学号生成器', "学号已抽完")
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
        toplevel.title("随机学号生成器")
        ttk.Label(toplevel,
                  text="随机学号生成器，\n 由nanocode38使用Python tkinter制作， \n更多详见https://github.com/nanocode38/Random-Number-Generator.git").pack()
        toplevel.mainloop()

    def help(self):
        toplevel = tk.Toplevel(self.root)
        toplevel.wm_attributes('-topmost', True)
        toplevel.wm_iconbitmap("AppData/icon.ico")
        toplevel.title("随机学号生成器")
        ttk.Label(toplevel,
                  text="随机学号生成器，\n 选择班级配置文件，点击按钮生产随机学号").pack()
        toplevel.mainloop()

    def run(self):
        while True:
            self.root.update()
            self.check_cross_the_boundary()
            self.check_activate()
            self.check_mouse_in_window()

    def hidden_animate(self, pos_x, pos_y):
        self.root.withdraw()
        animate_window = tk.Toplevel(self.root)
        animate_window.wm_attributes('-topmost', True)
        animate_window.wm_attributes('-alpha', 1.0)
        animate_window.config(bg=self.bg)

        img = tk.PhotoImage(file=f"AppData/{self.mode}.png")
        label = tk.Label(animate_window, image=img)
        label.place(x=0, y=0)

        animate_window.withdraw()
        animate_window.overrideredirect(True)
        animate_window.geometry('420x420')

        animate_window.deiconify()

        alpha = 1.

        for _ in range(74):
            alpha -= .006
            animate_window.wm_attributes('-alpha', alpha)
            animate_window.update()
            animate_window.geometry(f"{animate_window.winfo_width() - 5}x{animate_window.winfo_height() - 5}+"
                                    f"{pos_x}+{pos_y}")
            time.sleep(.003)

        animate_window.withdraw()

    def show_animate(self, pos_x, pos_y):
        self.activate_floating_window.withdraw()
        animate_window = tk.Toplevel(self.root)
        animate_window.wm_attributes('-topmost', True)
        animate_window.wm_attributes('-alpha', 0.5)

        img = tk.PhotoImage(file=f"AppData/{self.mode}.png")
        label = tk.Label(animate_window, image=img)
        label.place(x=0, y=0)

        animate_window.withdraw()
        animate_window.overrideredirect(True)
        animate_window.geometry('50x50')

        animate_window.deiconify()

        alpha = .5

        for _ in range(74):
            alpha += .006
            animate_window.wm_attributes('-alpha', alpha)
            animate_window.update()
            animate_window.geometry(f"{animate_window.winfo_width() + 5}x{animate_window.winfo_height() + 5}+"
                                    f"{pos_x}+{pos_y}")
            time.sleep(.003)

        animate_window.withdraw()

    def check_cross_the_boundary(self, *_):
        if not self.edge_hiding_mode.get() or self.check_mouse_in_window():
            return False
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
                self.hidden_animate(EDGE_POS_FAULT_TOLERANCE, self.root.winfo_y())
            self.activate_floating_window.deiconify()
        elif self.root.winfo_x() > screen_size[
            0] - root_width - EDGE_POS_FAULT_TOLERANCE and time.time() - self.cross_the_boundary_timer >= EDGE_HIDDEN_DELAY_TIME:
            self.activate_floating_window.geometry(
                "+%d+%d" % (self.root.winfo_screenwidth() - EDGE_POS_FAULT_TOLERANCE -
                            self.activate_floating_window.winfo_width(),
                            self.root.winfo_y()))

            if self.root.winfo_viewable():
                self.hidden_animate(self.root.winfo_screenwidth() - EDGE_POS_FAULT_TOLERANCE -
                            self.activate_floating_window.winfo_width(), self.root.winfo_y())
            self.activate_floating_window.deiconify()
        return True

    def check_activate(self, free: bool = False):
        if not self.edge_hiding_mode.get():
            return
        if free or (time.time() - self.activate_timer >= EDGE_HIDDEN_DELAY_TIME and self.activate_timer != .0):
            self.show_animate(self.root.winfo_x(), self.root.winfo_y())
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
        # 窗体边界范围
        window_x1 = self.root.winfo_rootx()
        window_y1 = self.root.winfo_rooty()
        window_x2 = window_x1 + self.root.winfo_width()
        window_y2 = window_y1 + self.root.winfo_height()
        window_y1 -= 80

        # 鼠标坐标（屏幕绝对坐标）
        mouse_x, mouse_y = pyg.position()

        if (window_x1 <= mouse_x <= window_x2 and
                window_y1 <= mouse_y <= window_y2):
            self.cross_the_boundary_timer = .0
            return True
        return False

    def save_data_and_exit(self):
        global data
        data['Deduplication mode'] = self.de_widget.get()
        data['Edge hiding mode'] = self.edge_hiding_mode.get()
        with open('AppData/data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f)
        self.root.destroy()
        sys.exit(0)


if __name__ == "__main__":
    Main(is_deduplication_mode=data['Deduplication mode'], is_edge_hiding_mode=data['Edge hiding mode'],
         mode=data["Mode"]).run()