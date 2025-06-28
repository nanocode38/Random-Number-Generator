import random
import csv
import os
import sys
import time
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import _tkinter
import json

import pyautogui as pyg


EDGE_HIDDEN_DELAY_TIME = 1
EDGE_POS_FAULT_TOLERANCE = 5

with open('data/data.json','r', encoding='utf-8') as f:
    data = json.load(f)

class Main(object):
    def __init__(self, is_edge_hiding_mode, is_deduplication_mode):
        self.root = tk.Tk()
        self.root.resizable(False, False)
        self.root.geometry("420x430")
        self.root.title("随机学号生成器")
        self.root.wm_iconbitmap("data/icon.ico")
        self.root.protocol("WM_DELETE_WINDOW", self.save_data_and_exit)
        menu = tk.Menu(self.root)
        submenu = tk.Menu(menu, tearoff=False)
        submenu.add_command(label="帮助", command=self.help)
        submenu.add_command(label='关于', command=self.about)
        menu.add_cascade(label="关于", menu=submenu)
        self.root.config(menu=menu)

        tk.Label(self.root, text="班级: ", font=('KaiTi', 13)).place(x=2, y=3)
        self.class_var = tk.StringVar()
        self.classes = list()
        for file in os.listdir('./data/'):
            if file.endswith('.csv'):
                self.classes.append(file)
        self.combobox = ttk.Combobox(self.root, textvariable=self.class_var, values=self.classes, state="readonly", width=10)
        self.combobox.place(x=60, y=5)
        self.label = tk.Label(self.root, text="", bg='white', fg='red', width=3, height=2, font=("Times", 60, "bold"))
        self.label.place(x=5, y=(290 - self.label.winfo_reqheight()) // 2 + 20)
        self.label1 = tk.Label(self.root, text="", bg='white', fg='red', width=6, height=4, font=("Times", 30, "bold"))
        self.label1.place(x=230, y=(290 - self.label.winfo_reqheight()) // 2 + 20)
        self.button = tk.Button(self.root, text="     生成随机学号\t", font=("Times", 30, "bold"), command=self.make_random)
        self.button.place(x=(390 - self.button.winfo_reqwidth()) // 2, y=300)
        self.de_widget = tk.BooleanVar()
        self.de_widget.set(is_deduplication_mode)
        self.de_weight_button = tk.Checkbutton(self.root, text="去重模式", variable=self.de_widget, onvalue=True, offvalue=False)
        self.de_weight_button.place(x=300, y=5)
        self.number_list = {-10_086}


        # 贴边隐藏功能
        self.cross_the_boundary_timer = .0
        self.activate_timer = .0
        self.activate_floating_window = tk.Toplevel(self.root, bg="white")
        self.activate_floating_window.wm_attributes('-topmost', True)
        self.activate_floating_window.wm_attributes('-alpha', 0.4)
        self.activate_floating_window.config(bg="white")
        self.activate_floating_window.wm_attributes('-transparentcolor', 'white')
        self.activate_floating_window.withdraw()
        self.activate_floating_window.overrideredirect(True)
        self.activate_floating_window.geometry("50x50")
        self._img = tk.PhotoImage(file="data/icon.png").subsample(18, 18)
        tk.Label(self.activate_floating_window, image=self._img).pack()

        self.edge_hiding_mode = tk.BooleanVar()
        self.edge_hiding_mode.set(is_edge_hiding_mode)
        self.edge_hiding_mode.trace("w", self.switchover_mode)
        self.edge_hiding_mode_button = tk.Checkbutton(self.root, text="贴边隐藏模式", variable=self.edge_hiding_mode,
                                                      onvalue=True, offvalue=False)
        self.edge_hiding_mode_button.place(x=180, y=5)

        self.activate_floating_window.bind("<Enter>", self.start_activate_timer)
        self.activate_floating_window.bind("<Leave>", self.stop_activate_timer)
        self.activate_floating_window.bind("<Button-1>",  lambda _: self.check_activate(True))

    def make_random(self):
        file = self.class_var.get()
        if not file:
            file = 'example.csv'
        with open('data/' + file, newline='', encoding='utf-8') as csv_file:
            row = list(csv.reader(csv_file))[0]
        rand = -10086
        if self.de_widget:
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
        self.label.config(text=str(rand+1))
        self.label1.config(text=row[rand])


    def about(self):
        toplevel = tk.Toplevel(self.root)
        toplevel.wm_iconbitmap("data/icon.ico")
        toplevel.wm_attributes("-topmost", True)
        toplevel.title("随机学号生成器")
        tk.Label(toplevel, text="随机学号生成器，\n 由nanocode38使用Python tkinter制作， \n更多详见https://github.com/nanocode38/Random-Number-Generator.git").pack()
        toplevel.mainloop()

    def help(self):
        toplevel = tk.Toplevel(self.root)
        toplevel.wm_attributes('-topmost', True)
        toplevel.wm_iconbitmap("data/icon.ico")
        toplevel.title("随机学号生成器")
        tk.Label(toplevel,
                 text="随机学号生成器，\n 选择班级配置文件，点击按钮生产随机学号").pack()
        toplevel.mainloop()

    def run(self):
        while True:
            self.root.update()
            self.check_cross_the_boundary()
            self.check_activate()
            self.check_mouse_in_window()

    def check_cross_the_boundary(self, *_):
        if not self.edge_hiding_mode.get():
            return False
        root_width = self.root.winfo_width()
        screen_size = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        if not (self.root.winfo_x() < EDGE_POS_FAULT_TOLERANCE or self.root.winfo_x() > screen_size[0] - root_width - EDGE_POS_FAULT_TOLERANCE):
            self.cross_the_boundary_timer = 0
        if (self.root.winfo_x() < EDGE_HIDDEN_DELAY_TIME or self.root.winfo_x() > screen_size[0] - root_width - EDGE_POS_FAULT_TOLERANCE) and self.cross_the_boundary_timer == 0:
            # Hidden Left
            self.cross_the_boundary_timer = time.time()
        elif self.root.winfo_x() < EDGE_POS_FAULT_TOLERANCE and time.time() - self.cross_the_boundary_timer >= EDGE_HIDDEN_DELAY_TIME:
            self.activate_floating_window.geometry(f"+{EDGE_POS_FAULT_TOLERANCE}+{self.root.winfo_y() + self.root.winfo_width()//2 - 
                                                         self.activate_floating_window.winfo_height()//2}")
            self.root.withdraw()
            self.activate_floating_window.deiconify()
        elif self.root.winfo_x() > screen_size[0] - root_width - EDGE_POS_FAULT_TOLERANCE and time.time() - self.cross_the_boundary_timer >= EDGE_HIDDEN_DELAY_TIME:
            self.activate_floating_window.geometry("+%d+%d" % (self.root.winfo_screenwidth() - EDGE_POS_FAULT_TOLERANCE -
                                                               self.activate_floating_window.winfo_width(),
                                                               self.root.winfo_y() + self.root.winfo_width()//2 -
                                                               self.activate_floating_window.winfo_height()//2))
            self.root.withdraw()
            self.activate_floating_window.deiconify()
        return None

    def check_activate(self, free: bool=False):
        if not self.edge_hiding_mode.get():
            return
        if free or (time.time() - self.activate_timer >= EDGE_HIDDEN_DELAY_TIME and self.activate_timer != .0):
            self.root.deiconify()
            self.activate_floating_window.withdraw()
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

    def check_mouse_in_window(self):
        # 窗体边界范围
        window_x1 = self.root.winfo_rootx()
        window_y1 = self.root.winfo_rooty()
        window_x2 = window_x1 + self.root.winfo_width()
        window_y2 = window_y1 + self.root.winfo_height()

        # 鼠标坐标（屏幕绝对坐标）
        mouse_x, mouse_y = pyg.position()

        if (window_x1 <= mouse_x <= window_x2 and
                window_y1 <= mouse_y <= window_y2):
            self.cross_the_boundary_timer = .0

    def save_data_and_exit(self):
        global data
        data['Deduplication mode'] = self.de_widget.get()
        data['Edge hiding mode'] = self.edge_hiding_mode.get()
        with open('data/data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f)
        self.root.destroy()
        sys.exit(0)

if __name__ == "__main__":
    try:
        Main(is_deduplication_mode=data['Deduplication mode'], is_edge_hiding_mode=data['Edge hiding mode']).run()
    except _tkinter.TclError:
        pass
    except KeyboardInterrupt:
        pass