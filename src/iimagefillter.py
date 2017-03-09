# -*- coding: utf-8 -*-
# pylint: disable=C0103

class ImageStream(object):
    def __init__(self, setup=None, task=None, teardown=None):
        self.filters = []
        if setup is None:
            setup = self.EmptyFilter
        if task is None:
            task = self.EmptyFilter
        if teardown is None:
            teardown = self.EmptyFilter
        self.filters.append(setup)
        self.filters.append(task)
        self.filters.append(teardown)
    def EmptyFilter(self, sender, args):
        """
            EmptyFilter
               stream => result
            usage ImageStream(task=ImageStream().EmptyFilter)
            @param {object}sender
                   {object},{None}args event args
            @return {object}
        """
        return sender
    def transform(self, data, args=None):
        """
            call
                preprocessor => task => finish
            @param {object}data stream
                   {object},{None}ev event args
            @return {object}
        """
        assert data is not None, 'data has Non'
        for caller in self.filters:
            data = caller(data, args)
            assert data is not None, '{0} has no return value'.format(str(caller))
        return data
