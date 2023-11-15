import tkinter.filedialog
from datetime import datetime, timedelta
import customtkinter as ctk
from tktooltip import *
import xlsxwriter


class App(ctk.CTk):
    def __init__(self, init_hours: int = 7, init_minutes: int = 0, init_seconds: int = 0,  **kwargs):
        super().__init__(**kwargs)
        self.init_seconds_left = init_hours*3600 + init_minutes*60 + init_seconds
        self.seconds_left: int = init_hours*3600 + init_minutes*60 + init_seconds
        self.start_time = None
        self.current_pause = None
        self.pauses: [Pause] = []
        self.threshold = None
        self.running = False
        self.over_time = 0

        self.export_path = ""

        self.resizable(width=False, height=False)
        self.overrideredirect(True)
        self.geometry("+0+0")

        self.min_font = ctk.CTkFont(family='Terminal', size=14)
        self.font = ctk.CTkFont(family='Terminal', size=16)
        self.max_font = ctk.CTkFont(family='Terminal', size=32)
        self.time_var = ctk.StringVar(master=self, value=time_to_str(self.seconds_left))

        self.time_frame = ctk.CTkFrame(master=self)
        self.time_label = ctk.CTkLabel(master=self.time_frame, textvariable=self.time_var, font=self.max_font)
        self.button = ctk.CTkButton(master=self.time_frame, text="Start", command=self._start, font=self.font)
        self.stop_button = ctk.CTkButton(master=self.time_frame, text="Fin", fg_color="#fd6868", hover_color="red", command=self._end, font=self.font)
        self.button_frame = ctk.CTkFrame(master=self)
        self.option_button = ctk.CTkButton(master=self.button_frame, text="Cfg.", width=5, font=self.font, command=lambda: Configure(self))
        self.save_button = ctk.CTkButton(master=self.button_frame, text="Save", width=5, font=self.font, command=self._export_pause, state="disabled")
        self.exit_button = ctk.CTkButton(master=self.button_frame, text="X", width=17, height=5, font=self.min_font, command=self.destroy, fg_color="#fd6868", hover_color="red")
        self.tooltip = ToolTip(widget=self.time_label, msg=self._est_end_date)

        self.time_frame.grid(row=0, column=0, padx=2, pady=2, sticky='ew')
        self.time_label.grid(row=0, column=0, columnspan=2, padx=2, pady=(12, 0), sticky='ew')
        self.button.grid(row=1, column=0, padx=2, pady=(12, 2), sticky='ew')
        self.stop_button.grid(row=1, column=1, pady=(12,2), padx=2, sticky='ew')
        self.button_frame.grid(row=0, column=1, padx=2, pady=2, sticky='ew')
        self.exit_button.grid(row=0, column=0, padx=2, pady=2, sticky='ew')
        self.option_button.grid(row=1, column=0, padx=2, pady=2, sticky='ew')
        self.save_button.grid(row=2, column=0, padx=2, pady=2, sticky='ew')

    def _start(self):
        if self.seconds_left and not self.over_time and not self.running and self.current_pause is None:
            if self.start_time is not None:
                self._adjust()
                self.after(1000, self._minus_one_sec)
                self.after(1000, self._start)
                self.running = True
                self.button.configure(command=self._pause, text="Pause")
            else:
                self.start_time = datetime.now()
                self.after(1000, self._minus_one_sec)
                self.after(1000, self._start)
                self.running = True
                self.button.configure(command=self._pause, text="Pause")
        elif self.seconds_left and not self.over_time and self.running:
            self.after(1000, self._minus_one_sec)
            self.after(1000, self._start)
        elif not self.seconds_left and not self.over_time and self.running:
            self.after(1000, self._minus_one_sec_overtime)
            self.after(1000, self._start)
            self.time_label.configure(text_color="green")
            self.threshold = datetime.now()
        elif not self.seconds_left and self.over_time and self.running:
            self.after(1000, self._minus_one_sec_overtime)
            self.after(1000, self._start)
        elif not self.seconds_left and self.over_time and not self.running and self.current_pause is None:
            self.after(1000, self._minus_one_sec_overtime)
            self.after(1000, self._start)
            self.running = True
            self.button.configure(command=self._pause, text="Pause")

    def _pause(self):
        self.running = False
        self.current_pause = Pause()
        self.button.configure(text="Reprendre", command=self._end_pause)

    def _end_pause(self):
        self.current_pause.stop()
        self.pauses.append(self.current_pause)
        self.current_pause = None
        self._start()

    def _minus_one_sec(self):
        if self.current_pause is None:
            self.seconds_left -= 1
            self.time_var.set(time_to_str(self.seconds_left))

    def _minus_one_sec_overtime(self):
        if self.current_pause is None:
            self.over_time += 1
            self.time_var.set("+ " + time_to_str(self.over_time))

    def _est_end_date(self):
        _now = datetime.now()
        _now_str = _now.strftime('%H:%M:%S')
        _est = (timedelta(seconds=self.seconds_left) + _now).strftime('%H:%M:%S')
        _est_45 = (timedelta(seconds=45*60 + self.seconds_left) + _now).strftime('%H:%M:%S')
        if self.seconds_left and int(_now_str.split(":")[0]) < 13:
            return "Fin estimée : " + _est_45
        elif self.seconds_left and int(_now_str.split(":")[0]) >= 13:
            return "Fin estimée : " + _est
        else:
            return "Vous pouvez débaucher"

    def _end(self):
        self._pause()
        self.button.configure(text="-", state="disabled")
        self.stop_button.configure(state="disabled")
        self.option_button.configure(state="disabled")
        self.save_button.configure(state="normal")

    def _adjust(self):
        seconds_spent = (datetime.now() - self.start_time).total_seconds()
        total_pause_seconds = sum(pause.duration.total_seconds() for pause in self.pauses)
        self.seconds_left = self.init_seconds_left - int(seconds_spent) + int(total_pause_seconds)

    def _export_pause(self):
        workbook = xlsxwriter.Workbook(f'{self.export_path}/Export_pauses_{datetime.now().strftime("%d%m%Y")}.xlsx')
        worksheet = workbook.add_worksheet()
        worksheet.write('A1', 'Test', 'bold')
        for i, pause in enumerate(self.pauses):
            worksheet.write(i + 1, 0, f"{'{:2d}'.format(pause.start_time.hour)}:{'{:2d}'.format(pause.start_time.minute)}")
            worksheet.write(i + 1, 1, f"{'{:2d}'.format(pause.end_time.hour)}:{'{:2d}'.format(pause.end_time.minute)}")
            worksheet.write(i + 1, 2, secs_to_mins(pause.duration))
        workbook.close()





class Pause:
    def __init__(self):
        self.start_time = datetime.now()
        self.end_time: datetime = None
        self.duration: timedelta = None

    def __repr__(self):
        return f"Pause de {self.start_time.strftime('%H:%M')} à {self.end_time.strftime('%H:%M')}\nDurée : {secs_to_mins(self.duration)}"

    def stop(self):
        self.end_time = datetime.now()
        self.duration = self.end_time - self.start_time


class Configure(ctk.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.export_path = "/"
        self.reste_a_bosser_hrs = 0
        self.reste_a_bosser_mins = 0

        self.resizable(False, False)
        self.title("Config")
        self.overrideredirect(True)
        self.geometry("+0+90")

        self.font = ctk.CTkFont(family='Terminal', size=16)
        self.max_font = ctk.CTkFont(family='Terminal', size=32)

        self.hours_var = ctk.StringVar(master=self, value="07")
        self.minutes_var = ctk.StringVar(master=self, value="00")

        self.title_label = ctk.CTkLabel(master=self, text="Config", font=self.max_font)
        self.time_label = ctk.CTkLabel(master=self, text="Temps de travail", font=self.font)
        self.hours_label = ctk.CTkLabel(master=self, text="H :", font=self.font)
        self.hours_entry = ctk.CTkEntry(master=self, textvariable=self.hours_var, width=40, height=35, font=self.font)
        self.minutes_label = ctk.CTkLabel(master=self, text="M :", font=self.font)
        self.minutes_entry = ctk.CTkEntry(master=self, textvariable=self.minutes_var, width=40, height=35, font=self.font)
        self.export_path_button = ctk.CTkButton(master=self, text="Dossier d'export", font=self.font, command=self._set_export_path)
        self.save_button = ctk.CTkButton(master=self, text="Enregistrer", font=self.font, command=self._save_config)
        self.cancel_button = ctk.CTkButton(master=self, text="Annuler", font=self.font, command=self.destroy, fg_color="#fd6868", hover_color="red")

        self.hours_entry.bind("<FocusOut>", self.on_focus_out_hours)
        self.minutes_entry.bind("<FocusOut>", self.on_focus_out_minutes)

        self.title_label.grid(row=0, column=0, columnspan=4, padx=5, pady=(15, 10), sticky='ew')
        self.time_label.grid(row=1, column=0, columnspan=4, padx=5, pady=(5, 2), sticky='w')
        self.hours_label.grid(row=2, column=0, padx=(5, 2), pady=(0, 5), sticky='ew')
        self.hours_entry.grid(row=2, column=1, padx=(0, 2), pady=(0, 5), sticky='w')
        self.minutes_label.grid(row=2, column=2, padx=(3, 2), pady=(0, 5), sticky='ew')
        self.minutes_entry.grid(row=2, column=3, padx=(0, 5), pady=(0, 5), sticky='w')
        self.export_path_button.grid(row=3, column=0, columnspan=4, padx=5, pady=(5, 5), sticky='ew')
        self.save_button.grid(row=4, column=0, columnspan=4, padx=5, pady=(0, 5), sticky='ew')
        self.cancel_button.grid(row=5, column=0, columnspan=4, padx=5, pady=(0, 10), sticky='ew')

    def on_focus_out_hours(self, event):
        var = self.hours_var
        try:
            if int(var.get()) > 23:
                var.set("23")
            elif int(var.get()) < 0:
                var.set("00")
            else:
                var.set("{:02d}".format(int(var.get())))
        except ValueError:
            var.set("00")

    def on_focus_out_minutes(self, event):
        var = self.minutes_var
        try:
            if int(var.get()) > 60:
                var.set("59")
            elif int(var.get()) < 0:
                var.set("00")
            else:
                var.set("{:02d}".format(int(var.get())))
        except ValueError:
            var.set("00")

    def _set_export_path(self):
        directory = tkinter.filedialog.askdirectory()
        if directory:
            self.export_path = directory
            self.export_path_button.configure(fg_color="green", text=directory.split('/')[-1])

    def _save_config(self):
        self.reste_a_bosser_hrs = int(self.hours_var.get())
        self.reste_a_bosser_mins = int(self.minutes_var.get())
        self.master.seconds_left = self.reste_a_bosser_hrs*3600 + self.reste_a_bosser_mins*60
        self.master.export_path = self.export_path
        self.master.time_var.set(value=time_to_str(self.master.seconds_left))
        self.destroy()


def time_to_str(seconds: int):
    hrs = seconds//3600
    mins = (seconds % 3600)//60
    seconds = (seconds % 3600) % 60
    return '{:02d}'.format(hrs) + ":" + '{:02d}'.format(mins) + ":" + '{:02d}'.format(seconds)


def secs_to_mins(delta: timedelta):
    secs = int(delta.total_seconds())
    minutes = secs // 60
    secs_left = secs % 60
    return f"{'{:02d}'.format(minutes)}:{'{:02d}'.format(secs_left)}"


if __name__ == '__main__':
    app = App()
    app.mainloop()
