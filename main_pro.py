import random
import csv
import os
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

class Main(object):
    def __init__(self):
        self.root = tk.Tk()
        self.root.resizable(False, False)
        self.root.geometry("390x430")
        self.root.title("随机学号生成器高级版")
        self.root.wm_iconbitmap("data/icon.ico")
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
        self.combobox = ttk.Combobox(self.root, textvariable=self.class_var, values=self.classes, state="readonly")
        self.combobox.place(x=95, y=5)
        self.label = tk.Label(self.root, text="", bg='white', fg='red', width=3, height=2, font=("Times", 60, "bold"))
        self.label.place(x=5, y=(290 - self.label.winfo_reqheight()) // 2 + 20)
        self.label1 = tk.Label(self.root, text="", bg='white', fg='red', width=6, height=4, font=("Times", 30, "bold"))
        self.label1.place(x=230, y=(290 - self.label.winfo_reqheight()) // 2 + 20)
        self.button = tk.Button(self.root, text="  生成随机学号  ", font=("Times", 30, "bold"), command=self.make_random)
        self.button.place(x=(390 - self.button.winfo_reqwidth()) // 2, y=300)
        self.de_widget = tk.BooleanVar()
        self.de_weight_button = tk.Checkbutton(self.root, text="去重模式", variable=self.de_widget, onvalue=True, offvalue=False)
        self.de_weight_button.place(x=300, y=5)
        self.number_list = {-10086}

    def make_random(self):
        file = self.class_var.get()
        if not file:
            file = '706.csv'
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
        toplevel.title("随机学号生成器")
        tk.Label(toplevel, text="随机学号生成器，\n 由nanocode38使用Python tkinter制作， \n更多详见https://github.com/nanocode38").pack()
        toplevel.mainloop()

    def help(self):
        toplevel = tk.Toplevel(self.root)
        toplevel.wm_iconbitmap("data/icon.ico")
        toplevel.title("随机学号生成器")
        tk.Label(toplevel,
                 text="随机学号生成器，\n 选择班级配置文件，点击按钮生产随机学号").pack()
        toplevel.mainloop()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    Main().run()
