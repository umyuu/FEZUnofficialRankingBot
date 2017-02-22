import argparse
# library
import cv2

class Window():
    def __init__(self, title='AdaptiveThreshold Simulator:stop esc key'):
        self.__title = title
        self.__canvas = None
        self.__grayscale = None
        self.titles = [self.title, 'src image ' + self.title]
        for t in self.titles:
            cv2.namedWindow(t, cv2.WINDOW_NORMAL)
        self.__lastMessage = None
        self.__adaptiveMethod = {0:cv2.ADAPTIVE_THRESH_MEAN_C, 1:cv2.ADAPTIVE_THRESH_GAUSSIAN_C}
        self.__thresholdType = {0:cv2.THRESH_BINARY, 1:cv2.THRESH_BINARY_INV}
    def nothing(self, x):
        pass
    @property
    def title(self):
        return self.__title
    @property
    def canvas(self):
        return self.__canvas
    @property
    def grayscale(self):
        return self.__grayscale
    @property
    def isClosed(self):
        for t in self.titles:
            if cv2.getWindowProperty(t, 0) < 0:
                return True
        return False
    def createCanvas(self, src):
        assert src is not None
        self.__canvas = src.copy()
        self.__grayscale = cv2.cvtColor(self.canvas, cv2.COLOR_BGR2GRAY)
        # createTrackbar params
        # trackbar_name, window_name, value, Maxvalue, on_changeCallBack
        self.switch_one = '''MEAN
GAUSS'''
        cv2.createTrackbar(self.switch_one, self.title, 1, 1, self.nothing)
        self.switch_two = '''BINARY
INV'''
        cv2.createTrackbar(self.switch_two, self.title, 0, 1, self.nothing)
        self.blocksize = ' blocksize'
        cv2.createTrackbar(self.blocksize, self.title, 11, 255, self.nothing)
        self.c = 'c'
        cv2.createTrackbar(self.c, self.title, 2, 255, self.nothing) 
    def drawDisplayImage(self):
        display_image = cv2.vconcat([self.canvas, cv2.cvtColor(self.grayscale, cv2.COLOR_GRAY2BGR)])
        cv2.imshow('src image ' + self.title, display_image)
    def draw(self):
        adaptiveMethod = self.__adaptiveMethod[cv2.getTrackbarPos(self.switch_one, self.title)]
        thresholdType = self.__thresholdType[cv2.getTrackbarPos(self.switch_two, self.title)]
        size = cv2.getTrackbarPos(self.blocksize, self.title)
        c = cv2.getTrackbarPos(self.c, self.title)
        message = 'params adaptiveMethod:{0}, thresholdType:{1}, blocksize:{2}, c:{3}'.format(
                adaptiveMethod, thresholdType, size, c)
        if message != self.__lastMessage:
           self.__lastMessage = message
           print(message)
        # adaptiveThreshold params check
        # blocksize range:Odd numbers{3,5,7,9,…} intial:3
        #   in:0,0  out:NG blocksize of even.
        #   in:1,0  out:NG initial stepvalue 3.
        #   in:2,0  out:NG blocksize of even.
        #   in:3,10　out:NG size * size - c < 0
        #   in:5,25 out:OK
        if size % 2 == 0 or size == 1:
            return
        if (size * size - c) < 0:
            return
        try:
            result = cv2.adaptiveThreshold(self.grayscale, 255, adaptiveMethod, thresholdType, size, c)
            self.__updateCanvas(result)
        except:
            pass
    def __updateCanvas(self, result):
        cv2.imshow(self.title, result)
        cv2.waitKey(1) # main Window PostQuitMessage.
    def __enter__(self):
        return self
    def __exit__(self, exception_type, exception_value	, traceback):
        for t in self.titles:
            cv2.destroyWindow(t)
        del self.__grayscale
        del self.__canvas

def main():
    parser = argparse.ArgumentParser(prog='adaptiveThreshold',
                                     description='AdaptiveThreshold Simulator')
    parser.add_argument('--version', action='version', version='%(prog)s 0.0.3')
    parser.add_argument('--image', '-in', default='../dat/Netzawar.png')
    parser.add_argument('--delay', '-d', default='100')
    args = parser.parse_args()
    
    print('args:{0}'.format(args))
    delay_time = int(args.delay)
    with Window() as win:
        win.createCanvas(cv2.imread(args.image))
        win.drawDisplayImage()
        while not win.isClosed:
            win.draw()
            if ((cv2.waitKey(delay_time) & 0xFF) == 27):
                break
            
if __name__ == "__main__":
    main()