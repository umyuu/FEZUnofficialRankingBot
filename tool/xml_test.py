# -*- coding: utf-8 -*-
import os
from datetime import datetime

from xml.etree.ElementTree import tostring, Element, Comment, SubElement
from xml.dom import minidom

class XMLDocument(object):
    def __init__(self):
        self.xml = None
    def Root(self, rootname='ranking'):
        root = Element(rootname)
        root.set('version', '1.0')
        root.append(Comment('Generated for TweetBot'))
        return root
    def Header(self, root):
        header = SubElement(root, 'head')
        dc = SubElement(header, 'Created')
        dc.text = str(datetime.now())
        return header
    def Body(self, root):
        body = SubElement(root, 'body')
        return body
    @staticmethod
    def toPrettify(element):
        """
            @param {Element}element
                   @return {xml}
        """
        rough_string = tostring(element, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")
def main():
    xml = XMLDocument()
    root = xml.Root()
    xml.Header(root)
    body = xml.Body(root)
    for i in range(5):
        child = SubElement(body, 'row')
        child.text = 'This child contains text.'

    print(XMLDocument.toPrettify(root))
if __name__ == '__main__':
    main()
