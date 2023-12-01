import threading
import time
from datetime import datetime
import CTkTable
import customtkinter as ctk
import agt_api


class LoginWindow(ctk.CTk):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.badge_var = ctk.StringVar(master=self, value='001234ABCD')
        self.time_var = ctk.StringVar(master=self, value='07:00')
        self.warn_frame = ctk.CTkFrame(master=self, fg_color="#FF6666")

        title_font = ctk.CTkFont(family="Terminal", size=32, weight='bold')
        bold_font = ctk.CTkFont(family="Terminal", size=16, weight='bold')
        font = ctk.CTkFont(family="Terminal", size=16)

        warn_label = ctk.CTkLabel(master=self.warn_frame, font=font, text="Badge inconnu", text_color="#FFFFFF", bg_color='transparent', justify='center')

        badge_entry = ctk.CTkEntry(master=self, font=font, textvariable=self.badge_var, justify='center')
        time_entry = ctk.CTkEntry(master=self, font=font, textvariable=self.time_var, justify='center', width=80)

        title_label = ctk.CTkLabel(master=self, text='Login', font=title_font)
        badge_label = ctk.CTkLabel(master=self, text='BADGE', font=bold_font)
        time_label = ctk.CTkLabel(master=self, text='TEMPS', font=bold_font)
        start_button = ctk.CTkButton(master=self, text='Connexion', font=bold_font, border_spacing=10, command=self._on_connexion)

        warn_label.grid(row=0, column=0, pady=5, padx=20, sticky='ew')

        title_label.grid(row=0, column=0, padx=50, pady=20, sticky='ew')
        badge_label.grid(row=1, column=0, padx=50, pady=(0, 2), sticky='ew')
        badge_entry.grid(row=2, column=0, padx=50, pady=(0, 8), sticky='ew')
        time_label.grid(row=3, column=0, padx=50, pady=(0, 2), sticky='ew')
        time_entry.grid(row=4, column=0, padx=50, pady=(0, 8), sticky='ew')
        start_button.grid(row=6, column=0, padx=50, pady=(7, 15), sticky='ew')

        time_entry.bind('<FocusOut>', self._on_leave_time)
        badge_entry.bind('<FocusOut>', self._on_leave_badge)

    def _on_leave_time(self, event):
        content = self.time_var.get()
        if len(content) > 5:
            content = content[:5]
        try:
            _time = content.split(':')
            hr = _time[0]
            mn = _time[1]
            hr_int = int(hr)
            mn_int = int(mn)
        except IndexError or ValueError:
            hr_int = 7
            mn_int = 0
        finally:
            self.time_var.set(value=f"{hr_int:02}:{mn_int:02}")

    def _on_leave_badge(self, event):
        badge_number = self.badge_var.get()
        ecart = 10 - len(badge_number)
        if ecart > 0:
            self.badge_var.set("0" * ecart + badge_number)
        elif ecart < 0:
            self.badge_var.set(badge_number[-10:])

    def _on_connexion(self):
        badge_number = self.badge_var.get()
        try:
            time_lst = self.time_var.get().split(':')
            seconds = int(time_lst[0])*3600 + int(time_lst[1])*60
        except IndexError or ValueError:
            self.warn_frame.grid(row=5, column=0, padx=20, pady=5, sticky='ew')
            return 0
        is_allowed = agt_api.check_badge_number(badge_number)
        if is_allowed:
            self.destroy()
            time_app = App(badge_number=badge_number, seconds_left=seconds)
            time_app.mainloop()
        else:
            self.warn_frame.grid(row=5, column=0, padx=20, pady=5, sticky='ew')


class DetailFrame(CTkTable.CTkTable):
    def __init__(self, master: any, **kwargs):
        h_font = ctk.CTkFont(family="Terminal", size=16, weight="bold")
        self.font = ctk.CTkFont(family="Terminal", size=16)
        super().__init__(master, column=2, row=1, values=[["Heure", "Action"]], font=h_font, **kwargs)
        self.edit_column(0, width=50)
        self.index = 1

    def add_action(self, action_str, in_out):
        time_str = datetime.now().strftime("%H:%M")
        if in_out:
            color = "#298a0b"
        else:
            color = "#910c0c"
        self.add_row([time_str, action_str], text_color=color)
        self.edit_column(0, width=50)
        self.index += 1


class CountDown(ctk.CTkFrame):
    def __init__(self, master: any, seconds_left, precision="seconds", **kwargs):
        super().__init__(master, **kwargs)
        self.seconds_left = seconds_left
        self.precision = precision
        self.start_time = datetime.now()
        self.is_running = False

        self.time_var = ctk.StringVar(master=self, value=self.estimate_time_string())

        font = ctk.CTkFont(family="Terminal", size=32)

        time_label = ctk.CTkLabel(master=self, textvariable=self.time_var, font=font, justify='center')
        time_label.grid(row=0, column=0, padx=50, pady=10, sticky='ew')

    def start(self):
        if not self.is_running:
            self.is_running = True
            self.start_time = datetime.now()

    def stop(self):
        if self.is_running:
            self.is_running = False
            end_time = datetime.now()
            self.seconds_left = self.seconds_left - (end_time - self.start_time).total_seconds()

    def estimate_time(self):
        if self.is_running:
            est_now = datetime.now()
            est_seconds_left = self.seconds_left - (est_now - self.start_time).total_seconds()
            return est_seconds_left
        else:
            return self.seconds_left

    def estimate_time_string(self):
        seconds_left = self.estimate_time()
        hours_left = int(seconds_left // 3600)
        minutes_left = int((seconds_left - hours_left*3600) // 60)
        seconds = int(seconds_left - hours_left*3600 - minutes_left*60)

        if self.precision == "seconds":
            return f"{hours_left:02}:{minutes_left:02}:{seconds:02}"
        elif self.precision == "minutes":
            return f"{hours_left:02}:{minutes_left:02}"


class App(ctk.CTk):
    def __init__(self, badge_number, seconds_left, **kwargs):
        super().__init__(**kwargs)
        self.badge_number = badge_number
        self.countdown = CountDown(master=self, seconds_left=seconds_left)
        self.drop_down = False

        self.resizable(False, False)
        self.overrideredirect(True)
        self.geometry("+0+0")

        threading.Thread(target=self.cron, daemon=True).start()

        font = ctk.CTkFont(family="Terminal", size=16)
        self.badge_button = ctk.CTkButton(master=self, text='Badger', width=90, font=font, command=self._badger, fg_color="#4287f5")
        self.pause_button = ctk.CTkButton(master=self, text='Pause', width=90, font=font, command=self._pause, fg_color="#4287f5")
        exit_button = ctk.CTkButton(master=self, text='X', width=15, font=font, fg_color='#FE6666', hover_color='red', command=self.destroy)
        self.precision_tick = ctk.CTkButton(master=self, text='S', width=15, height=27, font=font,
                                            command=self._precision)
        self.detail_button = ctk.CTkButton(master=self, text='+', width=15, height=28, font=font, command=self._detail)
        self.detail_frame = DetailFrame(master=self)

        self.countdown.grid(row=0, column=0, columnspan=2, rowspan=2, padx=(5, 1), pady=(5, 1), sticky='ew')
        self.badge_button.grid(row=2, column=0, padx=(5, 1), pady=(1, 1), sticky='ew')
        self.pause_button.grid(row=2, column=1, padx=(1, 1), pady=(1, 1), sticky='ew')
        exit_button.grid(row=0, column=2, padx=(2, 5), pady=(5, 1), sticky='new')
        self.precision_tick.grid(row=1, column=2, rowspan=1, padx=(2, 5), pady=(1, 1), sticky='nsew')
        self.detail_button.grid(row=2, column=2, rowspan=1, padx=(2, 5), pady=(1, 1), sticky='nsew')

    def cron(self):
        while True:
            time_left = self.countdown.estimate_time_string()
            if time_left != self.countdown.time_var:
                self.countdown.time_var.set(time_left)
            time.sleep(1)

    def _pause(self):
        if self.countdown.is_running:
            print('Pause start')
            self.countdown.stop()
            self.detail_frame.add_action("Pause", False)
            self.pause_button.configure(fg_color="#299133", hover_color="#1d6624")
        else:
            print('Pause stop')
            self.countdown.start()
            self.detail_frame.add_action("Pause", True)
            self.pause_button.configure(fg_color="#4287f5", hover_color="#224680")
        agt_api.agt_action(action="PAUSE", badge_number=self.badge_number)

    def _badger(self):
        if self.countdown.is_running:
            print('Badging out')
            self.countdown.stop()
            self.detail_frame.add_action("Badge", False)
            self.badge_button.configure(fg_color="#4287f5", hover_color="#224680")
        else:
            print('Badging in')
            self.countdown.start()
            self.detail_frame.add_action("Badge", True)
            self.badge_button.configure(fg_color="#299133", hover_color="#1d6624")
        agt_api.agt_action(action="BADGER", badge_number=self.badge_number)

    def _detail(self):
        if not self.drop_down:
            self.detail_frame.grid(row=3, column=0, columnspan=3, padx=5, pady=5, sticky='ew')
            self.detail_button.configure(text="-")
        else:
            self.detail_frame.grid_remove()
            self.detail_button.configure(text="+")
        self.drop_down = not self.drop_down

    def _precision(self):
        precision = self.countdown.precision
        if precision == "seconds":
            self.countdown.precision = "minutes"
            self.precision_tick.configure(text='M')
        elif precision == "minutes":
            self.countdown.precision = "seconds"
            self.precision_tick.configure(text='S')


if __name__ == "__main__":
    login = LoginWindow()
    login.mainloop()
