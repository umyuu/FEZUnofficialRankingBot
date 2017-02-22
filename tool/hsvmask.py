import argparse
import tkinter as tk
# library
import cv2
import numpy as np
from PIL import Image, ImageTk

class ImageData(object):
    def __init__(self, src):
        assert src is not None
        self.__canvas = src.copy()
        self.__hsv = cv2.cvtColor(self.canvas, cv2.COLOR_BGR2HSV)
    @property
    def canvas(self):
        return self.__canvas
    @property
    def hsv(self):
        return self.__hsv
    def change(self):
        return self.__hsv
class HSVcolor(object):
    __slots__ = ['h','s','v']
    def __init__(self, h=0, s=0, v=0):
        self.h = h
        self.s = s
        self.v = v
    def __str__(self):
        res = ','.join([str(self.h), str(self.s), str(self.v)])
        return res
    def toarray_np(self):
        return np.array([self.h, self.s, self.v])
class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.data = None
        self.createWidgets()
    def createWidgets(self):
        controls = dict()
        # lower
        controls['lower_h'] = {'label':'Hue','from_':0,'to':255,'length':300,'orient':tk.HORIZONTAL, 'command':self.updateScaleValue}
        controls['lower_s'] = {'label':'Saturation','from_':0,'to':255,'length':300,'orient':tk.HORIZONTAL, 'command':self.updateScaleValue}
        controls['lower_v'] = {'label':'Value','from_':0,'to':255,'length':300,'orient':tk.HORIZONTAL, 'command':self.updateScaleValue}
        # upper
        controls['upper_h'] = {'label':'Hue','from_':0,'to':255,'length':300,'orient':tk.HORIZONTAL, 'command':self.updateScaleValue}
        controls['upper_s'] = {'label':'Saturation','from_':0,'to':255,'length':300,'orient':tk.HORIZONTAL, 'command':self.updateScaleValue}
        controls['upper_v'] = {'label':'Value','from_':0,'to':255,'length':300,'orient':tk.HORIZONTAL, 'command':self.updateScaleValue}
        
        #print(controls)
        self.lowerframe = tk.LabelFrame(self, text='lower')
        self.lowerframe.grid(row=0, column=0)
        self.lower_h = tk.Scale(self.lowerframe, controls['lower_h'])
        self.lower_h.pack()
        self.lower_s = tk.Scale(self.lowerframe, controls['lower_s'])
        self.lower_s.pack()
        self.lower_v = tk.Scale(self.lowerframe, controls['lower_v'])
        self.lower_v.pack()
        
        self.upperframe = tk.LabelFrame(self, text='upper')
        self.upperframe.grid(row=0, column=1)
                
        self.upper_h = tk.Scale(self.upperframe, controls['upper_h'])
        self.upper_h.set(255)
        self.upper_h.pack()
        self.upper_s = tk.Scale(self.upperframe, controls['upper_s'])
        self.upper_s.set(255)
        self.upper_s.pack()
        self.upper_v = tk.Scale(self.upperframe, controls['upper_v'])
        self.upper_v.set(255)
        self.upper_v.pack()

        self.lblimage = tk.Label(self)
        self.lblimage.grid(row=1, column=0, columnspan=2)
    def __createHSV(self, root, h, s, v):
        """
            @params names controlnames
        """
        return tk.Scale(root,h), tk.Scale(root,s), tk.Scale(root,v)
    @property
    def canvas(self):
        return self.data.canvas
    @property
    def hsv(self):
        return self.data.hsv
    def loadImage(self, src):
        self.data = ImageData(src)
        self.__changeImage(src)
    def __changeImage(self, src):
        imgtk = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(src, cv2.COLOR_BGR2RGB)))
        self.lblimage.imgtk = imgtk
        self.lblimage.configure(image= imgtk) 
    def updateScaleValue(self, event):
        lower = HSVcolor(self.lower_h.get(), self.lower_s.get(), self.lower_v.get())
        upper = HSVcolor(self.upper_h.get(), self.upper_s.get(), self.upper_v.get())
        #print(lower, upper, sep=' | ')
        mask = cv2.inRange(self.hsv, lower.toarray_np(), upper.toarray_np())
        result = cv2.bitwise_and(self.canvas, self.canvas, mask = mask)
        self.__changeImage(result)

def main():
    parser = argparse.ArgumentParser(prog='hsvmask',
                                     description='HSV ColorMask Simulator')
    parser.add_argument('--version', action='version', version='%(prog)s 0.0.4')
    parser.add_argument('--image', '-in', default='../dat/Netzawar.png')
    args = parser.parse_args()
    print('args:{0}'.format(args))
    
    app = Application()
    app.master.title('HSV ColorMask Simulator')
    app.loadImage(cv2.imread(args.image))
    app.pack()
    app.mainloop()
            
if __name__ == "__main__":
    main()