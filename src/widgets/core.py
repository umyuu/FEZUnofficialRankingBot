# -*- coding: utf-8 -*-
import tkinter as tk

# pylint: disable=C0103
class Core(tk.Frame):
    """
        widget core
    """
    def __init__(self, master=None):
        super().__init__(master)
        self.focus_set()
        self.bind_all('<Control-Shift-KeyPress-Q>', self.onApplicationExit)
    def onApplicationExit(self, event=None):
        """
            application exit event
            @param {object}event event args
            note:
            spyder IDE Run Script app hangup
            github doc\\images\\IDE_spyder_setting.jpg
        """
        self.quit()
    def run(self):
        """
             start messageloop
        """
        self.pack()
        self.mainloop()
    def title(self, title):
        """
            @param {string}title Window Title
        """
        self.master.title(title)
    def __enter__(self):
        return self
    def __exit__(self, exception_type, exception_value, traceback):
        self.onApplicationExit()
