from datetime import datetime
import customtkinter as ctk
import agt_api
from utils import time_to_str
from CTkTable import *


class TimeFrame(ctk.CTkFrame):
    def __init__(self, master: any, seconds: int, **kwargs):
        super().__init__(master, **kwargs)
        self.font = ctk.CTkFont(family="Terminal", size=32)
        self.time_var = ctk.StringVar(master=self, value=time_to_str(seconds=seconds))

        time_label = ctk.CTkLabel(master=self, textvariable=self.time_var, font=self.font)
        time_label.grid(column=0, row=0, padx=(50, 0), pady=10)

    def set(self, value: int):
        self.time_var.set(time_to_str(seconds=value))

    def get(self):
        self.time_var.get()


class BottomButtonFrame(ctk.CTkFrame):
    def __init__(self, master: any, **kwargs):
        super().__init__(master, fg_color='transparent', **kwargs)
        self.font = ctk.CTkFont(family="Terminal", size=16)

        badge_button = ctk.CTkButton(master=self, text="Badger", font=self.font, fg_color="#6e8a84", hover_color="#3a464c", command=self.badge)
        pause_button = ctk.CTkButton(master=self, text="Pause", font=self.font, fg_color="#3474b2", hover_color="#2c5484", command=self.pause)

        badge_button.grid(row=0, column=0, padx=(0, 1), sticky='ew')
        pause_button.grid(row=0, column=1, padx=(1, 0), sticky='ew')

    def add_mvt(self):
        pass

    def badge(self):
        time = datetime.now().strftime("%H:%M")
        if self.master.in_out:
            self.master.detail_frame.add_mvt(type_mouvement="Badger", mouvement="Sortie", time=time, color="darkred")
        else:
            self.master.detail_frame.add_mvt(type_mouvement="Badger", mouvement="Entree", time=time, color="green")
        self.master.in_out = not self.master.in_out
        agt_api.agt_action(action="BADGER", badge=self.master.detail_frame.badge_entry.get())

    def pause(self):
        time = datetime.now().strftime("%H:%M")
        if self.master.in_out:
            self.master.detail_frame.add_mvt(type_mouvement="Pause", mouvement="Sortie", time=time, color="red")
        else:
            self.master.detail_frame.add_mvt(type_mouvement="Pause", mouvement="Entree", time=time, color="green")
        self.master.in_out = not self.master.in_out
        agt_api.agt_action(action="PAUSE", badge=self.master.detail_frame.badge_entry.get())


class RightButtonFrame(ctk.CTkFrame):
    def __init__(self, master: any, **kwargs):
        super().__init__(master, fg_color='transparent', **kwargs)
        self.font = ctk.CTkFont(family="Terminal", size=16)

        exit_button = ctk.CTkButton(master=self, text="X", font=self.font, width=65, height=27, fg_color="#fd6868", hover_color="red", command=self.master.destroy)
        conf_button = ctk.CTkButton(master=self, text="Cfg.", font=self.font, width=65, height=27, fg_color="#7ea99e", hover_color="#6e8a84", command=self.cfg)
        self.plus_button = ctk.CTkButton(master=self, text="+", font=self.font, width=65, height=27, fg_color="#7ea99e", hover_color="#6e8a84", command=self.plus)

        exit_button.grid(row=0, column=0, pady=(0, 2), sticky='ew')
        conf_button.grid(row=1, column=0, pady=(0, 2), sticky='ew')
        self.plus_button.grid(row=2, column=0, pady=(0, 0), sticky='ew')

    def cfg(self):
        print("Config")

    def plus(self):
        if not self.master.drop_down:
            self.plus_button.configure(text="-")
            self.master.drop_down = True
            self.master.detail_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky='ew')
        else:
            self.plus_button.configure(text="+")
            self.master.drop_down = False
            self.master.detail_frame.grid_forget()


class DetailFrame(ctk.CTkFrame):
    def __init__(self, master: any, **kwargs):
        super().__init__(master, width=359, **kwargs)
        self.headers_font = ctk.CTkFont(family="Terminal", size=16, weight="bold")
        self.font = ctk.CTkFont(family="Terminal", size=16)
        headers = ["Type Mvt", "E/S", "Heure"]

        self.last_index = 0

        self.badge_entry = ctk.CTkEntry(master=self, placeholder_text="#badge", font=self.font)
        self.table = CTkTable(master=self, column=3, row=1, values=[headers], font=self.headers_font)
        self.table.edit_column(0, width=138)
        self.table.edit_column(1, width=103)
        self.table.edit_column(2, width=100)

        self.badge_entry.grid(row=0, column=0, padx=50, pady=(0,5), sticky='ew')
        self.table.grid(row=1, column=0, sticky='ew')

    def add_mvt(self, type_mouvement: str, mouvement: str, time: str, color: str):
        self.table.add_row(values=[type_mouvement, mouvement, time], index=self.last_index+1, text_color=color)
        self.table.edit_column(0, width=138)
        self.table.edit_column(1, width=103)
        self.table.edit_column(2, width=100)
        self.last_index += 1


class App(ctk.CTk):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.resizable(False, False)
        self.drop_down = False
        self.in_out = False

        self.time_frame = TimeFrame(master=self, seconds=45610)
        self.right_frame = RightButtonFrame(master=self)
        self.bottom_frame = BottomButtonFrame(master=self)
        self.detail_frame = DetailFrame(master=self)

        self.time_frame.grid(row=0, column=0, padx=(5, 2), pady=(5, 2), sticky='ew')
        self.bottom_frame.grid(row=1, column=0, padx=(5, 2), pady=(0, 5), sticky='ew')
        self.right_frame.grid(row=0, column=1, rowspan=2, padx=(0, 5), pady=(5, 5), sticky='ew')


if __name__ == '__main__':
    app = App()
    app.mainloop()
