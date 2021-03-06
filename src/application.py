# -*- coding: utf-8 -*-
import argparse
import os
from datetime import datetime
import tkinter as tk
from tkinter.filedialog import askopenfilename
import threading
# library
import cv2
import numpy as np
from PIL import Image, ImageTk
#
from serializer import Serializer
from widgets.core import ApplicationCore
from hsvcolor import HSVcolor
# pylint: disable=C0103

class ImageData(object):
    def __init__(self, src):
        assert src is not None
        self.__canvas = src.copy()
        self.__hsv = cv2.cvtColor(self.canvas.copy(), cv2.COLOR_BGR2HSV)
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

class Application(ApplicationCore):
    def __init__(self, master=None):
        super().__init__(master)
        self.data = None
        self.frame_inputimage = None
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

        self.frame_input_image = tk.LabelFrame(self, text='input')
        self.frame_input_image.grid(row=1, column=0)
        self.lbl_input = tk.Label(self.frame_input_image)
        self.lbl_input.pack()
        
        self.frame_output_image = tk.LabelFrame(self, text='output')
        self.frame_output_image.grid(row=1, column=1)
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
        visualmenu.add_command(label="Input Image(I)...", under=13, command=self.createInputImageWindow)
        visualmenu.add_separator()
        visualmenu.add_command(label="Reset params(R)", under=0, command=self.hsvParamsReset)
    def createInputImageWindow(self):
        if self.frame_inputimage is None:
           self.frame_inputimage = tk.Toplevel()
           self.frame_inputimage.lbl_input = tk.Label(self.frame_inputimage)
           self.frame_inputimage.lbl_input.pack()
        
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
        imgtk = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(src, cv2.COLOR_BGR2RGB)))
        self.lbl_input.imgtk = imgtk
        self.lbl_input.configure(image= imgtk)
        self.__changeImage(src)
    def __changeImage(self, src):
        imgtk = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(src, cv2.COLOR_BGR2RGB)))
        self.lbl_output.imgtk = imgtk
        self.lbl_output.configure(image= imgtk)
        #print('END:{0}'.format(datetime.now()))
    def __stateChanged(self):
        #print('STA:{0}'.format(datetime.now()))
        lower = HSVcolor(self.lower_h.get(), self.lower_s.get(), self.lower_v.get())
        upper = HSVcolor(self.upper_h.get(), self.upper_s.get(), self.upper_v.get())
        result = None
        v = self.rbnOperation.get()
        if v == 1:
            result = self.data.bitwise_and(lower, upper)
        elif v == 2:
            result = self.data.bitwise_or(lower, upper)
        elif v == 3:
            result = self.data.bitwise_xor(lower, upper)
        elif v == 4:
            result = self.data.bitwise_not(lower, upper)
        else:
            assert False
        self.__changeImage(result)

def main():
    APP_VERSION =  (0, 0, 4)
    parser = argparse.ArgumentParser(prog='tweetbot',
                                     description='tweetbot　gui')
    parser.add_argument('--version', action='version', version='%(prog)s {0}'.format(APP_VERSION))
    parser.add_argument('--image', '-in', default='../resource/Netzawar.png')
    args = parser.parse_args()
    print('args:{0}'.format(args))
    with Application() as app:
        app.title('tweetbot　gui version:{0}'.format(APP_VERSION))
        app.loadImage(cv2.imread(args.image))
        app.run()

if __name__ == "__main__":
    main()
