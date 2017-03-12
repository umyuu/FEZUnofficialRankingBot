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
            @return {SubElement}
        """
        element = SubElement(root, name)
        if d is None:
            return element
        for key, value in d.items():
            child = SubElement(element, key)
            child.text = value
        return element
    def getiter(self, name):
        """
            @param {string}name
            @yield {SubElement}
            
        """
        for country in self.root.iter(name):
            for row in country.findall('row'):
                yield row
    def findall(self, xpath):
        """
            xpath findall
            @param {string}xpath 
            @yield
        """
        for row in self.root.findall(xpath):
            yield row
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
    xml = XMLDocument('tweetbot')
    for i in ['decode', 'ocr']:
        child = xml.addChild(xml.body, i)
        for j in range(5):
            r = xml.addChild(child, 'row')
            r.text = 'This child contains text.' + i

    for row in xml.findall("./body/decode/row"):
        print(row.text)

    print(tostring(xml.root, 'utf-8'))
    print(XMLDocument.toPrettify(xml.root))
if __name__ == '__main__':
    main()
