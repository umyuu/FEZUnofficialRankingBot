# -*- coding: utf-8 -*-

# pylint: disable=C0103
class SimpleEvent(object):
    """
        SimpleEvent class
        note:handlers#iteratble
            add ordering
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
        self.__handlers = []
    def __call__(self, *args, **kargs):
        """
            @param args
                   kargs
        """
        for handler in self.__handlers:
            handler(*args, **kargs)
    def __add__(self, handler):
        """
            add handler
            @exception {TypeError}
        """
        if not hasattr(handler, '__call__'):
            raise TypeError("object is not callable:%s" % handler)
        assert handler not in self.__handlers, "handlers in %s" % handler
        self.__handlers.append(handler)
        return self
    def __sub__(self, handler):
        """
            remove handler
            @exception {ValueError} handler not in list
        """
        self.__handlers.remove(handler)
        return self
    @property
    def handlers(self):
        """
            handler protected property
        """
        return self.__handlers
    def clear(self):
        """
            handler#clear
        """
        self.__handlers = []
class EventArgs(object):
    @staticmethod
    def Empty(*args, **kargs):
        """
            EventArgs#Empty
        """
        pass

class Filters(SimpleEvent):
    """
        Filters
        -----------------------------------------------------
        << usage >>
        filters = Filters()
        filters += self.filter_1
        filters += self.filter_2
        filters(1)
        << result >>
        self.filter_2(self.filter_1(1))
        ------------------------------------------------------
    """
    def __call__(self, data, args=None):
        """
            @param {object}data stream
                   {object}args event args
            @return {object}
        """
        assert data is not None, 'data has Non'
        for handler in self.handlers:
            data = handler(data, args)
            assert data is not None, '{0} has no return value'.format(str(handler))
        return data
