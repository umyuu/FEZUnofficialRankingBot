# -*- coding: utf-8 -*-
import argparse
import tkinter as tk
# library
import cv2
from PIL import Image, ImageTk

class ImageData(object):
    def __init__(self, src):
        assert src is not None
        self.__canvas = src.copy()
        self.__grayscale = cv2.cvtColor(self.canvas, cv2.COLOR_BGR2GRAY)
    @property
    def canvas(self):
        return self.__canvas
    @property
    def grayscale(self):
        return self.__grayscale

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.data = None
        self.createWidgets()
    def createWidgets(self):
        controls = dict()
        self.topframe = tk.LabelFrame(self, text='params')
        self.topframe.grid(row=0, column=0)

        controls['ADAPTIVE'] = {'label':'0:MEAN_C / 1:GAUSSIAN_C', 'from_':0, 'to':1, 'length':300, 'orient':tk.HORIZONTAL, 'command':self.__onChanged_ScaleValue}
        self.scale_adaptive = tk.Scale(self.topframe, controls['ADAPTIVE'])
        self.scale_adaptive.pack()
        
        controls['THRESHOLDTYPE'] = {'label':'0:BINARY / 1:INV', 'from_':0, 'to':1, 'length':300, 'orient':tk.HORIZONTAL, 'command':self.__onChanged_ScaleValue}
        self.scale_thresholdType = tk.Scale(self.topframe, controls['THRESHOLDTYPE'])
        self.scale_thresholdType.pack()
        # initial stepvalue 3.
        controls['BLOCKSIZE'] = {'label':'blocksize', 'from_':3, 'to':255, 'length':300, 'orient':tk.HORIZONTAL, 'command':self.__onChanged_ScaleValue}
        self.scale_blocksize = tk.Scale(self.topframe, controls['BLOCKSIZE'])
        self.scale_blocksize.set(11)
        self.scale_blocksize.pack()
        
        controls['C'] = {'label':'c', 'from_':0, 'to':255, 'length':300, 'orient':tk.HORIZONTAL, 'command':self.__onChanged_ScaleValue}
        self.scale_c = tk.Scale(self.topframe, controls['C'])
        self.scale_c.set(2)
        self.scale_c.pack()
        
        self.lblimage = tk.Label(self)
        self.lblimage.grid(row=1, column=0)
        self.__adaptiveMethod = {0:cv2.ADAPTIVE_THRESH_MEAN_C, 1:cv2.ADAPTIVE_THRESH_GAUSSIAN_C}
        self.__thresholdType = {0:cv2.THRESH_BINARY, 1:cv2.THRESH_BINARY_INV}
    def draw(self):
        adaptiveMethod = self.__adaptiveMethod[self.scale_adaptive.get()]
        thresholdType = self.__thresholdType[self.scale_thresholdType.get()]
        size = self.scale_blocksize.get()
        c = self.scale_c.get()
        # adaptiveThreshold params check
        # blocksize range:Odd numbers{3,5,7,9,…} intial:3
        #   in:0,0  out:NG blocksize of even.
        #   in:2,0  out:NG blocksize of even.
        #   in:3,10　out:NG size * size - c < 0
        #   in:5,25 out:OK
        if size % 2 == 0:
            return
        if (size * size - c) < 0:
            return
        try:
            result = cv2.adaptiveThreshold(self.data.grayscale, 255, adaptiveMethod, thresholdType, size, c)
            self.__changeImage(result)
        except (Exception) as ex:
            print(ex)
            pass
    def loadImage(self, src):
        self.data = ImageData(src)
        self.__changeImage(src)
    def __changeImage(self, src):
        #imgtk = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(src, cv2.COLOR_BGR2RGB)))
        imgtk = ImageTk.PhotoImage(Image.fromarray(src))
        self.lblimage.imgtk = imgtk
        self.lblimage.configure(image=imgtk)
    def __onChanged_ScaleValue(self, event):
        self.draw()
def main():
    parser = argparse.ArgumentParser(prog='adaptiveThreshold',
                                     description='AdaptiveThreshold Simulator')
    parser.add_argument('--version', action='version', version='%(prog)s 0.0.3')
    parser.add_argument('--image', '-in', default='../dat/Netzawar.png')
    parser.add_argument('--delay', '-d', default='100')
    args = parser.parse_args()
    
    print('args:{0}'.format(args))
    
    app = Application()
    app.master.title('AdaptiveThreshold Simulator')
    app.loadImage(cv2.imread(args.image))
    app.pack()
    app.mainloop()
    
if __name__ == "__main__":
    main()