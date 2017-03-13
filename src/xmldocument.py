# -*- coding: utf-8 -*-
from datetime import datetime

from xml.etree.ElementTree import tostring, Element, Comment, SubElement
from xml.dom import minidom

class XMLDocument(object):
    """
        XMLDocument class
    """
    def __init__(self, name):
        """
            XML Document
            root / header / body
        """
        # root
        root = Element(name)
        root.set('version', '1.0')
        root.append(Comment('Generated for TweetBot'))
        self.root = root
        # header
        self.header = SubElement(self.root, 'head')
        dc = SubElement(self.header, 'Created')
        dc.text = str(datetime.now())
        # body
        self.body = SubElement(self.root, 'body')
    def addChild(self, root, name, d=None):
        """
            @param {Element},{SubElement}root Element
                   {string}name
                   {dict}d
            @return {SubElement}created child element
        """
        element = SubElement(root, name)
        if d is None:
            return element
        for key, value in d.items():
            child = SubElement(element, key)
            child.text = value
        return element
    def findall(self, xpath):
        """
            xpath findall
            @param {string}xpath 
            @yield
        """
        for row in self.root.findall(xpath):
            yield row
    def toPretty(self):
        """
            @param {Element}element
            @return {xml}copy pretty xml
        """
        rough_string = tostring(self.root, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")
def main():
    xml = XMLDocument('tweetbot')
    for i in ['ranking', 'ocr']:
        child = xml.addChild(xml.body, i)
        for j in range(5):
            xml.addChild(child, 'row').text = 'child contains text.' + i

    for row in xml.findall("./body/ranking/row"):
        print(row.text)

    print(tostring(xml.root, 'utf-8'))
    print(xml.toPretty())
if __name__ == '__main__':
    main()
