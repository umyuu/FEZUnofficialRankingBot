# -*- coding: utf-8 -*-
import argparse
import os
import tkinter as tk
from tkinter.filedialog import askopenfilename
# library
import cv2
import numpy as np
from PIL import Image, ImageTk
from datetime import datetime

class ImageData(object):
    def __init__(self, src):
        assert src is not None
        self.__canvas = src.copy()
        self.__hsv = cv2.cvtColor(self.canvas.copy(), cv2.COLOR_BGR2HSV)
        self.event = None
    @property
    def canvas(self):
        return self.__canvas
    @property
    def hsv(self):
        return self.__hsv
    def bitwise_and(self, lower, upper):
        mask = cv2.inRange(self.hsv, lower.to_np(), upper.to_np())
        return cv2.bitwise_and(self.canvas, self.canvas.copy(), mask = mask)
    def bitwise_or(self, lower, upper):
        mask = cv2.inRange(self.hsv, lower.to_np(), upper.to_np())
        return cv2.bitwise_or(self.canvas, self.canvas, mask = mask)
    def bitwise_xor(self, lower, upper):
        mask = cv2.inRange(self.hsv, lower.to_np(), upper.to_np())
        return cv2.bitwise_xor(self.canvas, self.canvas.copy(), mask = mask)
    def bitwise_not(self, lower, upper):
        mask = cv2.inRange(self.hsv, lower.to_np(), upper.to_np())
        return cv2.bitwise_not(self.canvas, self.canvas.copy(), mask = mask)
    def bitOperation(self, operation, lower, upper):
        if operation == 1:
            result = self.bitwise_and(lower, upper)
        elif operation == 2:
            result = self.bitwise_or(lower, upper)
        elif operation == 3:
            result = self.bitwise_xor(lower, upper)
        elif operation == 4:
            result = self.bitwise_not(lower, upper)
        else:
            assert False
        # callback
        self.event.onChanged_Image(result)
    def setEventListener(self, event):
        self.event = event
        return self
class HSVcolor(object):
    __slots__ = ['h','s','v']
    def __init__(self, h=0, s=0, v=0):
        if h < 0:
            h = h + 360
        self.h = h
        self.s = s
        self.v = v
    def __str__(self):
        return ','.join([str(self.h), str(self.s), str(self.v)])
    def to_np(self):
        return np.array([self.h, self.s, self.v])
    @staticmethod
    def valueOf(h, s, v):
        return HSVcolor(h, s, v)
class ApplicationCore(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.isdestroyed = False
        self.focus_set()
        self.bind_all('<Control-Shift-KeyPress-Q>', self.onApplicationExit)
    def onApplicationExit(self, event=None):
        # spyder IDE Run Script app hangup
        # github doc\images\IDE_spyder_setting.jpg
        if not self.isdestroyed:
            self.isdestroyed = True
            self.master.destroy()
    def run(self):
        """
             start messageloop
        """
        self.pack()
        self.mainloop()
    def title(self, title):
        self.master.title(title)
    def __enter__(self):
        return self
    def __exit__(self, exception_type, exception_value, traceback):
        self.onApplicationExit()
class Application(ApplicationCore):
    def __init__(self, master=None):
        super().__init__(master)
        self.data = None
        self.createMenu()
        self.createWidgets()
    def createWidgets(self):
        controls = dict()
        # lower
        controls['lower_h'] = {'label':'Hue','from_':0,'to':180,'length':400,'orient':tk.HORIZONTAL, 'command':self.__onChanged_ScaleValue}
        controls['lower_s'] = {'label':'Saturation','from_':0,'to':255,'length':400,'orient':tk.HORIZONTAL, 'command':self.__onChanged_ScaleValue}
        controls['lower_v'] = {'label':'Value','from_':0,'to':255,'length':400,'orient':tk.HORIZONTAL, 'command':self.__onChanged_ScaleValue}
        # upper
        controls['upper_h'] = {'label':'Hue','from_':0,'to':180,'length':400,'orient':tk.HORIZONTAL, 'command':self.__onChanged_ScaleValue}
        controls['upper_s'] = {'label':'Saturation','from_':0,'to':255,'length':400,'orient':tk.HORIZONTAL, 'command':self.__onChanged_ScaleValue}
        controls['upper_v'] = {'label':'Value','from_':0,'to':255,'length':400,'orient':tk.HORIZONTAL, 'command':self.__onChanged_ScaleValue}
        
        #print(controls)
        self.frame_top = tk.LabelFrame(self)
        self.frame_top.grid(row=0, column=0, columnspan=2)
        self.frame_lower = tk.LabelFrame(self.frame_top, text='lower')
        self.frame_lower.grid(row=0, column=0)
        self.lower_h = tk.Scale(self.frame_lower, controls['lower_h'])
        self.lower_h.pack()
        self.lower_s = tk.Scale(self.frame_lower, controls['lower_s'])
        self.lower_s.pack()
        self.lower_v = tk.Scale(self.frame_lower, controls['lower_v'])
        self.lower_v.pack()
        
        self.frame_op = tk.LabelFrame(self.frame_top, text='op')
        self.frame_op.grid(row=0, column=1)
        self.rbnOperation = tk.IntVar()
        self.rbnOperation.set(1)
        self.bitwise_and = tk.Radiobutton(self.frame_op, text="and", variable=self.rbnOperation, value=1, command=self.__onChanged_rbnOperation)
        self.bitwise_and.pack( anchor = tk.W )
        self.bitwise_or = tk.Radiobutton(self.frame_op, text="or", variable=self.rbnOperation, value=2, command=self.__onChanged_rbnOperation)
        self.bitwise_or.pack( anchor = tk.W )
        self.bitwise_xor = tk.Radiobutton(self.frame_op, text="xor", variable=self.rbnOperation, value=3, command=self.__onChanged_rbnOperation)
        self.bitwise_xor.pack( anchor = tk.W )
        self.bitwise_not = tk.Radiobutton(self.frame_op, text="not", variable=self.rbnOperation, value=4, command=self.__onChanged_rbnOperation)
        self.bitwise_not.pack( anchor = tk.W )
        
        self.frame_upper = tk.LabelFrame(self.frame_top, text='upper')
        self.frame_upper.grid(row=0, column=2)
        self.upper_h = tk.Scale(self.frame_upper, controls['upper_h'])
        self.upper_h.pack()
        self.upper_s = tk.Scale(self.frame_upper, controls['upper_s'])
        self.upper_s.pack()
        self.upper_v = tk.Scale(self.frame_upper, controls['upper_v'])
        self.upper_v.pack()
        
        self.hsvParamsReset()

        self.frame_output_image = tk.LabelFrame(self, text='output')
        self.frame_output_image.grid(row=1, column=0)
        self.lbl_output = tk.Label(self.frame_output_image)
        self.lbl_output.pack()
    def createMenu(self):
        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)
        filemenu = tk.Menu(menubar)
        filemenu.add_command(label="Open(O)...", under=5, command=self.openFile)
        filemenu.add_separator()
        filemenu.add_command(label="Exit(X)        Ctrl+Shift-Q", under=5, command=self.onApplicationExit)
        menubar.add_cascade(label="File(F)", menu=filemenu, underline=5)
        visualmenu = tk.Menu(menubar)
        menubar.add_cascade(label="Visual(V)", menu=visualmenu, underline=7)
        visualmenu.add_command(label="Input Image(I)...", under=12, command=self.createWindow_InputImage)
        visualmenu.add_command(label="Python Code(C)", under=12, command=self.createPythonCode)
        visualmenu.add_separator()
        visualmenu.add_command(label="Reset params(R)", under=0, command=self.hsvParamsReset)
    def createPythonCode(self):
        pass
    def createWindow_InputImage(self):
        toplevel = tk.LabelFrame(tk.Toplevel(), text='input')
        self.inputimageWindow = toplevel
        toplevel.pack()
        toplevel.lbl_input = tk.Label(toplevel)
        self.setLabelImage(toplevel.lbl_input, self.data.canvas)
        toplevel.lbl_input.pack()
    def hsvParamsReset(self):
        self.lower_h.set(0)
        self.lower_s.set(0)
        self.lower_v.set(0)
        self.upper_h.set(180)
        self.upper_s.set(255)
        self.upper_v.set(255)
    def openFile(self):
        name = askopenfilename(initialdir=os.getcwd())
        if len(name) == 0:
            return
        image = cv2.imread(name)
        self.loadImage(image)
    def __onChanged_rbnOperation(self):
        self.__stateChanged()
    def __onChanged_ScaleValue(self, event):
        self.__stateChanged()
    def __createHSV(self, root, h, s, v):
        """
            @params names controlnames
        """
        return tk.Scale(root,h), tk.Scale(root,s), tk.Scale(root,v)
    def loadImage(self, src):
        self.data = ImageData(src)
        self.data.setEventListener(self)
        self.__stateChanged()
    def onChanged_Image(self, src):
        self.setLabelImage(self.lbl_output, src)
        #print('END:{0}'.format(datetime.now()))
    def __stateChanged(self):
        #print('STA:{0}'.format(datetime.now()))
        lower = HSVcolor.valueOf(self.lower_h.get(), self.lower_s.get(), self.lower_v.get())
        upper = HSVcolor.valueOf(self.upper_h.get(), self.upper_s.get(), self.upper_v.get())
        v = self.rbnOperation.get()
        self.data.bitOperation(v, lower, upper)
    def setLabelImage(self, label, src):
        assert label is not None
        imgtk = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(src, cv2.COLOR_BGR2RGB)))
        label.imgtk = imgtk
        label.configure(image= imgtk)
def main():
    APP_VERSION =  (0, 0, 4)
    parser = argparse.ArgumentParser(prog='hsvmask',
                                     description='HSV ColorMask Simulator')
    parser.add_argument('--version', action='version', version='%(prog)s {0}'.format(APP_VERSION))
    parser.add_argument('--image', '-in', default='../resource/Netzawar.png')
    args = parser.parse_args()
    print('args:{0}'.format(args))
    with Application() as app:
        app.title('HSV ColorMask Simulator version:{0}'.format(APP_VERSION))
        app.loadImage(cv2.imread(args.image))
        app.run()

if __name__ == "__main__":
    main()