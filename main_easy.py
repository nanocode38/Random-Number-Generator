import random
import tkinter as tk
from tkinter import messagebox

class Main(object):
    def __init__(self):
        self.root = tk.Tk()
        self.root.resizable(False, False)
        self.root.geometry("390x430")
        self.root.title("随机学号生成器简易版")
        self.root.wm_iconbitmap("data/icon.ico")
        menu = tk.Menu(self.root)
        submenu = tk.Menu(menu, tearoff=False)
        submenu.add_command(label="帮助", command=self.help)
        submenu.add_command(label='关于', command=self.about)
        menu.add_cascade(label="关于", menu=submenu)
        self.root.config(menu=menu)

        tk.Label(self.root, text="抽查范围: ", font=('KaiTi', 13)).place(x=2, y=3)
        self.start = tk.Entry(self.root, width=12)
        self.start.place(x=95, y=5)
        tk.Label(self.root, text=" ~ ", font=('KaiTi', 13)).place(x=100 + self.start.winfo_reqwidth(), y=10)
        self.end = tk.Entry(self.root, width=12)
        self.end.place(x=150 + self.start.winfo_reqwidth(), y=5)
        self.label = tk.Label(self.root, text="", bg='white', fg='red', width=3, height=1, font=("Times", 150, "bold"))
        self.label.place(x=(390 - self.label.winfo_reqwidth()) // 2, y=(290 - self.label.winfo_reqheight()) // 2 + 20)
        self.button = tk.Button(self.root, text="  生成随机学号  ", font=("Times", 30, "bold"), command=self.make_random)
        self.button.place(x=(390 - self.button.winfo_reqwidth()) // 2, y=300)
        self.de_widget = tk.BooleanVar()
        self.de_weight_button = tk.Checkbutton(self.root, text="去重模式", variable=self.de_widget, onvalue=True, offvalue=False)
        self.de_weight_button.place(x=300, y=5)
        self.number_list = {-10086}

    def make_random(self):
        start, end = self.start.get(), self.end.get()
        rand = -10086
        if self.de_widget:
            if sorted(list(range(int(start), int(end) + 1)) + [-10086,]) == sorted(list(self.number_list)):
                messagebox.showwarning('随机学号生成器', "学号已抽完")
                self.number_list = {-10086}
                self.root.update()
                return
            while rand in self.number_list:
                rand = random.randint(int(start) if start else 0, int(end) if end else 40)
        else:
            rand = random.randint(int(start) if start else 0, int(end) if end else 40)
        self.label.config(text=str(rand))
        self.number_list.add(rand)



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
                 text="随机学号生成器，\n 输入选择范围，点击按钮生产随机学号").pack()
        toplevel.mainloop()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    Main().run()
