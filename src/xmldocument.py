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

    def addChild(self, root, tag):
        """
            Syntax Sugar　newSubElement
            @param {Element},{SubElement}root Element
                   {string}tag     first character non-numeric
            @return {SubElement}created child element
            @exception Exception
        """
        if not isinstance(tag, str):
            raise Exception('Tag is not str type')
        if tag[0].isdigit():
            # note)check throw self#toPretty
            # xml.parsers.expat.ExpatError: not well-formed (invalid token)
            raise Exception('The first character of the tag must be non-numeric')
        
        element = SubElement(root, tag)
        return element

    def addDict(self, root, d):
        for tag, value in d.items():
            child = self.addChild(root, tag)
            child.text = value
        return root

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

    def __str__(self):
        return self.toPretty()

def main():
    xml = XMLDocument('tweetbot')
    for i in ['ranking', 'ocr']:
        child = xml.addChild(xml.body, i)
        for j in range(5):
            xml.addChild(child, 'row').text = 'child contains text.' + i

    for row in xml.findall("./body/ranking/row"):
        print(row.text)

    print('')
    print(tostring(xml.root, 'utf-8'))
    print('')
    print(xml.toPretty())
    print(xml)
if __name__ == '__main__':
    main()
