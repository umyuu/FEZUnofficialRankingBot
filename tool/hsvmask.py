import argparse
# library
import cv2
import numpy as np

def nothing(x):
    pass

class Window():
    def __init__(self, title='window:stop esc key'):
        self.__title = title
        self.__canvas = None
        self.__hsv = None
        cv2.namedWindow(self.title, cv2.WINDOW_NORMAL)
        # createTrackbar params
        # trackbar_name,window_name,value,Maxvalue,on_changeCallBack
        cv2.createTrackbar('l_h', self.title, 0, 255, nothing)
        cv2.createTrackbar('l_s', self.title, 0, 255, nothing)
        cv2.createTrackbar('l_v', self.title, 0, 255, nothing)
        cv2.createTrackbar('u_h', self.title, 255, 255, nothing)
        cv2.createTrackbar('u_s', self.title, 255, 255, nothing)
        cv2.createTrackbar('u_v', self.title, 255, 255, nothing)
    @property
    def title(self):
        return self.__title
    @property
    def canvas(self):
        return self.__canvas
    @property
    def hsv(self):
        return self.__hsv
    @property
    def isClosed(self):
        return cv2.getWindowProperty(self.title, 0) < 0
    def createCanvas(self, src):
        assert src is not None
        self.__canvas = src.copy()
        self.__hsv = cv2.cvtColor(self.canvas, cv2.COLOR_BGR2HSV)
    def Draw(self):
        lower_b = np.array(self.__pickColor(['l_h', 'l_s', 'l_v']))
        upper_b = np.array(self.__pickColor(['u_h', 'u_s', 'u_v']))
        mask = cv2.inRange(self.hsv, lower_b, upper_b)
        result = cv2.bitwise_and(self.canvas, self.canvas, mask = mask)
        self.__updateCanvas(result)
    def __pickColor(self, colors):
        assert colors is not None
        h = cv2.getTrackbarPos(colors[0], self.title)
        s = cv2.getTrackbarPos(colors[1], self.title)
        v = cv2.getTrackbarPos(colors[2], self.title)
        return [h,s,v]
    def __updateCanvas(self, result):
        cv2.imshow(self.title, result)
        cv2.waitKey(1) # main Window PostQuitMessage.
    def __enter__(self):
        return self
    def __exit__(self, exception_type, exception_value	, traceback):
        cv2.destroyWindow(self.title)
        del self.__hsv
        del self.__canvas

def main():
    parser = argparse.ArgumentParser(prog='hsvmask',
                                     description='HSV ColorMask Simulator')
    parser.add_argument('--version', action='version', version='%(prog)s 0.0.1')
    parser.add_argument('--imagefile', '-image', default='../dat/Netzawar.png')
    parser.add_argument('--delay', '-d', default='100')
    args = parser.parse_args()
    
    print('args:{0}'.format(args))
    delay_time = int(args.delay)
    with Window() as win:
        win.createCanvas(cv2.imread(args.imagefile))
        while not win.isClosed:
            win.Draw()
            if ((cv2.waitKey(delay_time) & 0xFF) == 27):
                break
            
if __name__ == "__main__":
    main()