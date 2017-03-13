# -*- coding: utf-8 -*-
import numpy as np
import cv2
# pylint: disable=C0103
def imread(filename, flags=1):
    """
        @param {string}filename
               {int}flags 1=cv2.IMREAD_COLOR
        @return {Mat}image
                    FileNotFound image == None
    """
    image = None
    try:
        with open(filename, 'rb') as file:
            buffer = np.asarray(bytearray(file.read()), dtype=np.uint8)
            image = cv2.imdecode(buffer, flags)
    except FileNotFoundError as ex:
        # cv2.imread 互換
        pass
    return image

def main():
    filename = './日本語ファイル.png'
    img = imread(filename)
    #img = cv2.imread(filename)
    cv2.namedWindow('main', cv2.WINDOW_AUTOSIZE)
    cv2.imshow('main', img)
    cv2.waitKey(0)
if __name__ == '__main__':
    main()
