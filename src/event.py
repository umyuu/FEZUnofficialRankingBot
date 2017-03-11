# -*- coding: utf-8 -*-

# pylint: disable=C0103
class SimpleEvent(object):
    """
        SimpleEvent class
        -----------------------------------------------------
        << usage >>
        ev = SimpleEvent()
        ev += self.Callback_1
        ev += self.Callback_2
        ev('fire')
        << result >>
        Callback_1('fire')
        Callback_2('fire')
        ------------------------------------------------------
        @thread non-safe
    """
    def __init__(self):
        self.handlers = set()
    def __call__(self, *args, **kargs):
        for handler in self.handlers:
            handler(*args, **kargs)
    def __add__(self, handler):
        if not hasattr(handler, '__call__'):
           raise TypeError("object is not callable:%s" % handler)
        self.handlers.add(handler)
        return self
    def __sub__(self, handler):
        try:
            self.handlers.remove(handler)
        except:
            raise ValueError("is not handling this event:%s" % handler)
        return self
    def clear(self):
        self.handlers = set()

def aaaa(param):
    print(param)
    print('aaa')
def bbbb(param):
    print(param)
    print('bbb')
def main():
    ev = SimpleEvent()
    ev += aaaa
    ev += bbbb
    ev(123)
if __name__ == "__main__":
    main()
