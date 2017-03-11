# -*- coding: utf-8 -*-
import os
from datetime import datetime

from xml.etree.ElementTree import tostring, Element, Comment, SubElement
from xml.dom import minidom

def toPrettify(element):
    """
        @param {Element}element
        @return {xml}
    """
    rough_string = tostring(element, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")
def createHeader(root):
    header = SubElement(root, 'head')
    dc = SubElement(header, 'Created')
    dc.text = str(datetime.now())
    return header
def main():
    root = Element('ranking')
    root.set('version', '1.0')
    
    root.append(Comment('Generated for TweetBot'))
    createHeader(root)
    for i in range(5):
        child = SubElement(root, 'row')
        child.text = 'This child contains text.'

    print(toPrettify(root))
if __name__ == '__main__':
    main()
