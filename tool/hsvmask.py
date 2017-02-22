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
        l_h = self.lower_h.get()
        l_s = self.lower_s.get()
        l_v = self.lower_v.get()
        u_h = self.upper_h.get()
        u_s = self.upper_s.get()
        u_v = self.upper_v.get()
        #print(l_h, l_s, l_v, u_h, u_s, u_v,sep=',')
        mask = cv2.inRange(self.hsv, np.array([l_h, l_s, l_v]), np.array([u_h, u_s, u_v]))
        result = cv2.bitwise_and(self.canvas, self.canvas, mask = mask)
        self.__changeImage(result)

def main():
    parser = argparse.ArgumentParser(prog='hsvmask',
                                     description='HSV ColorMask Simulator')
    parser.add_argument('--version', action='version', version='%(prog)s 0.0.3')
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